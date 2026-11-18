"""ONNX FP16 phase guard: the guarded Kokoro graph, built in memory at load (MEU-144).

Kokoro's FP16 graph divides at `/decoder/decoder/generator/Div` and feeds the quotient to an
`Atan`. A 0/0 there gives NaN, and the audio is not finite (`TTS-ONNX-FP16-NONFINITE-AUDIO`).
Session 73's `PHASE_GUARD` inserts `Where(IsNaN(q), 0, q)` between the two, so a NaN quotient
becomes +0 and a finite one is unchanged (D-797).

`splice` applies that edit to the model's protobuf bytes with a small wire-format reader (no
`onnx` package), building the result in one join over `memoryview` slices of the source
(`ONE_JOIN`). `guarded_model` applies it only to the FP16 file Session 73 hashed, and only
returns the result when it has Session 73's guarded hash (`GUARD_GATE`, `GUARD_REFUSE`,
`GUARD_APPLIED`); anything else loads as shipped. Nothing is written to disk (`NO_FILE_WRITE`,
D-1136 A).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import structlog

log = structlog.get_logger(module="tts")

__all__ = ["KOKORO_FP16", "GuardSpec", "SpliceError", "guarded_model", "splice"]

G = "/decoder/decoder/generator/"
DIV = G + "Div"
GUARD_ISNAN = G + "PhaseGuard_IsNaN"
GUARD_WHERE = G + "PhaseGuard_Where"
GUARD_ZERO = G + "PhaseGuard_zero"
GUARD_MASK = G + "PhaseGuard_IsNaN_output_0"
GUARD_OUT = G + "PhaseGuard_Where_output_0"
FLOAT16 = 10
FP16_VARIANT = "kokoro-onnx-fp16"

#: (field number, wire type, field start, payload start, field end)
Field = tuple[int, int, int, int, int]


class SpliceError(Exception):
    """The model is not the shape the guard knows; nothing is guessed."""


@dataclass(frozen=True)
class GuardSpec:
    """The one source file the guard applies to, and the result it must give."""

    source_sha256: str
    source_bytes: int
    guarded_sha256: str


#: Session 73's pins: the downloaded `model_fp16.onnx` and its guarded graph (D-797).
KOKORO_FP16 = GuardSpec(
    "ba4527a874b42b21e35f468c10d326fdff3c7fc8cac1f85e9eb6c0dfc35c334a",
    163234740,
    "9037c82b84dca069464f707f31a4fcb6e5d57107b0534fd4a7ae0c044396fd33",
)


def _read_varint(buf: bytes, pos: int) -> tuple[int, int]:
    result = 0
    shift = 0
    while True:
        if pos >= len(buf):
            raise SpliceError("truncated varint")
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not b & 0x80:
            return result, pos
        shift += 7
        if shift > 63:
            raise SpliceError("varint too long")


def _varint(value: int) -> bytes:
    out = bytearray()
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def _fields(buf: bytes, start: int = 0, end: int | None = None) -> list[Field]:
    end = len(buf) if end is None else end
    out: list[Field] = []
    pos = start
    while pos < end:
        fstart = pos
        tag, pos = _read_varint(buf, pos)
        no, wt = tag >> 3, tag & 7
        if wt == 0:
            _, pos = _read_varint(buf, pos)
            pstart = fstart
        elif wt == 1:
            pstart = pos
            pos += 8
        elif wt == 2:
            length, pos = _read_varint(buf, pos)
            pstart = pos
            pos += length
        elif wt == 5:
            pstart = pos
            pos += 4
        else:
            raise SpliceError(f"unsupported wire type {wt}")
        if pos > end:
            raise SpliceError("field runs past its message")
        out.append((no, wt, fstart, pstart, pos))
    return out


def _ld(no: int, payload: bytes) -> bytes:
    return _varint((no << 3) | 2) + _varint(len(payload)) + payload


def _text(buf: bytes, start: int, end: int) -> str:
    try:
        return buf[start:end].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SpliceError("a name is not UTF-8") from exc


def _strings(buf: bytes, start: int, end: int, no: int) -> list[str]:
    return [
        _text(buf, p, e) for (n, wt, _f, p, e) in _fields(buf, start, end) if n == no and wt == 2
    ]


def _node(inputs: list[str], outputs: list[str], name: str, op: str) -> bytes:
    body = b"".join(_ld(1, s.encode()) for s in inputs)
    body += b"".join(_ld(2, s.encode()) for s in outputs)
    body += _ld(3, name.encode()) + _ld(4, op.encode())
    return _ld(1, body)


def splice(src: bytes) -> bytes:
    """`PHASE_GUARD` on an ONNX model's bytes; raises `SpliceError` on any other shape."""
    top = _fields(src)
    graphs = [f for f in top if f[0] == 7 and f[1] == 2]
    if len(graphs) != 1:
        raise SpliceError(f"expected one graph, found {len(graphs)}")
    _, _, g_fstart, g_start, g_end = graphs[0]
    gf = _fields(src, g_start, g_end)
    nodes = [f for f in gf if f[0] == 1 and f[1] == 2]
    flat = [(_strings(src, f[3], f[4], 3) or [""])[0] for f in nodes]
    if GUARD_ISNAN in flat or GUARD_WHERE in flat:
        raise SpliceError("already guarded")
    hits = [i for i, n in enumerate(flat) if n == DIV]
    if len(hits) != 1:
        raise SpliceError(f"expected one {DIV}, found {len(hits)}")
    div = nodes[hits[0]]
    ops = _strings(src, div[3], div[4], 4)
    outs = _strings(src, div[3], div[4], 2)
    if ops != ["Div"] or len(outs) != 1:
        raise SpliceError("Div is not one Div with one output")
    quotient = outs[0]
    graph_outputs = [_strings(src, f[3], f[4], 1) for f in gf if f[0] == 12 and f[1] == 2]
    if any(quotient in o for o in graph_outputs):
        raise SpliceError("quotient is a graph output")
    consumers = [f for f in nodes if quotient in _strings(src, f[3], f[4], 1)]
    if len(consumers) != 1 or _strings(src, consumers[0][3], consumers[0][4], 4) != ["Atan"]:
        raise SpliceError("quotient must feed exactly one Atan")
    atan_field = consumers[0]
    # The Atan node: each input equal to the quotient becomes GUARD_OUT, other bytes kept.
    a_body = bytearray()
    for n, wt, f, p, e in _fields(src, atan_field[3], atan_field[4]):
        if n == 1 and wt == 2 and _text(src, p, e) == quotient:
            a_body += _ld(1, GUARD_OUT.encode())
        else:
            a_body += src[f:e]
    new_atan = _ld(1, bytes(a_body))
    isnan = _node([quotient], [GUARD_MASK], GUARD_ISNAN, "IsNaN")
    where = _node([GUARD_MASK, GUARD_ZERO, quotient], [GUARD_OUT], GUARD_WHERE, "Where")
    zero = _ld(
        5,
        _varint((2 << 3) | 0)
        + _varint(FLOAT16)
        + _ld(8, GUARD_ZERO.encode())
        + _ld(9, b"\x00\x00"),
    )
    inits = [i for i, f in enumerate(gf) if f[0] == 5 and f[1] == 2]
    if not inits:
        raise SpliceError("no initializer")
    last_init = inits[-1]
    view = memoryview(src)
    try:
        parts: list[bytes | memoryview] = []
        for i, fld in enumerate(gf):
            _n, _wt, f, _p, e = fld
            parts.append(new_atan if fld == atan_field else view[f:e])
            if fld == div:
                parts += [isnan, where]
            if i == last_init:
                parts.append(zero)
        glen = sum(len(x) for x in parts)
        head = _varint((7 << 3) | 2) + _varint(glen)
        result = b"".join([view[:g_fstart], head, *parts, view[g_end:]])
        del parts
    finally:
        view.release()
    return result


def guarded_model(path: Path, variant_id: str, spec: GuardSpec | None = None) -> str | bytes:
    """The model to hand to `InferenceSession`: the guarded bytes, or `str(path)`.

    With no `spec`, only `kokoro-onnx-fp16` is guarded, against `KOKORO_FP16` read at call
    time. A file of another size or hash loads as shipped, with no log. A splice that fails or
    gives another hash loads as shipped with one warning. Never raises; never writes a file.
    """
    if spec is None:
        if variant_id != FP16_VARIANT:
            return str(path)
        spec = KOKORO_FP16
    try:
        if path.stat().st_size != spec.source_bytes:
            return str(path)
        src = path.read_bytes()
    except (OSError, MemoryError):
        return str(path)
    if hashlib.sha256(src).hexdigest() != spec.source_sha256:
        return str(path)
    try:
        result = splice(src)
    except Exception as exc:
        # Only the class: no path, no file name, no message (D-323).
        log.warning(
            "tts.phase_guard", variant_id=variant_id, outcome="refused", reason=type(exc).__name__
        )
        return str(path)
    del src
    if hashlib.sha256(result).hexdigest() != spec.guarded_sha256:
        log.warning(
            "tts.phase_guard", variant_id=variant_id, outcome="refused", reason="result_hash"
        )
        return str(path)
    log.info("tts.phase_guard", variant_id=variant_id, outcome="applied")
    return result
