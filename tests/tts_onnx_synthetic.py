"""A tiny FP16 `Div -> Atan -> Mul` ONNX model, written as raw protobuf bytes (MEU-144).

Session 74 plan, §The guard. `build()` is the plan-time probe's builder (`synthetic-probe.py`):
`y = atan(a / b) * 1.0`, all FP16, with the `Div` named `/decoder/decoder/generator/Div` as in
Kokoro's FP16 graph, so 0/0 gives NaN through the `Atan` and `phase_guard.splice` can guard it.
Its keyword arguments build the shapes the splice must refuse:

- `div_names`: the names of the `Div` nodes (default one `G + "Div"`; an empty list gives one
  `Div` under another name);
- `div_op`: the first `Div` node's op type (default `"Div"`);
- `atan`: `False` feeds the quotient straight to the `Mul`;
- `quotient_output`: `True` also lists the quotient as a graph output;
- `initializer`: `False` drops the graph's only initializer;
- `graphs`: how many graph fields the model holds (default 1);
- `name_bytes`: raw bytes for the first `Div` node's name (invalid UTF-8, say).

No `onnx` package is used. `SPEC` (the synthetic `GuardSpec`) is built on first access, so
importing this helper never imports `avkit_infra.tts.phase_guard`.
"""

from __future__ import annotations

from typing import Any

G = "/decoder/decoder/generator/"
FLOAT16 = 10

#: `build()`'s bytes: 375, SHA-256 below (`s74-plan-synthetic.json`).
SOURCE_BYTES = 375
SOURCE_SHA256 = "57ba7da424695a40e2a43ad0f7b271685a6cd729439d930c0e9ff52c4f41348b"
#: `splice(build())`: 839 bytes.
GUARDED_BYTES = 839
GUARDED_SHA256 = "fbbd7205e07079c6aa2670e6a0a8333844b1c9b44486549ace3e9b33f66526b7"


def varint(value: int) -> bytes:
    out = bytearray()
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def ld(no: int, payload: bytes) -> bytes:
    """A length-delimited field."""
    return varint((no << 3) | 2) + varint(len(payload)) + payload


def vi(no: int, value: int) -> bytes:
    """A varint field."""
    return varint(no << 3) + varint(value)


def node(inputs: list[str], outputs: list[str], name: str | bytes, op: str) -> bytes:
    raw = name if isinstance(name, bytes) else name.encode()
    body = b"".join(ld(1, s.encode()) for s in inputs)
    body += b"".join(ld(2, s.encode()) for s in outputs)
    body += ld(3, raw) + ld(4, op.encode())
    return ld(1, body)


def value_info(name: str) -> bytes:
    shape = ld(1, vi(1, 1))  # one Dimension, dim_value 1
    tensor = vi(1, FLOAT16) + ld(2, shape)
    return ld(1, name.encode()) + ld(2, ld(1, tensor))


def build(
    *,
    div_names: list[str] | None = None,
    div_op: str = "Div",
    atan: bool = True,
    quotient_output: bool = False,
    initializer: bool = True,
    graphs: int = 1,
    name_bytes: bytes | None = None,
) -> bytes:
    """The synthetic model; with no arguments, exactly `SOURCE_SHA256`."""
    names: list[str | bytes] = list([G + "Div"] if div_names is None else div_names)
    if not names:
        names = ["Div"]
    if name_bytes is not None:
        names[0] = name_bytes
    quotient = G + "Div_output_0"
    atan_out = G + "Atan_output_0"
    graph = node(["a", "b"], [quotient], names[0], div_op)
    for i, extra in enumerate(names[1:], start=1):
        graph += node(["a", "b"], [f"{quotient}_{i}"], extra, "Div")
    if atan:
        graph += node([quotient], [atan_out], G + "Atan", "Atan")
        graph += node([atan_out, "one"], ["y"], "Mul", "Mul")
    else:
        graph += node([quotient, "one"], ["y"], "Mul", "Mul")
    graph += ld(2, b"s74-synthetic")
    if initializer:
        one = vi(1, 1) + vi(2, FLOAT16) + ld(8, b"one") + ld(9, b"\x00\x3c")  # FP16 1.0
        graph += ld(5, one)
    graph += ld(11, value_info("a")) + ld(11, value_info("b"))
    graph += ld(12, value_info("y"))
    if quotient_output:
        graph += ld(12, value_info(quotient))
    opset = ld(1, b"") + vi(2, 13)
    return vi(1, 8) + ld(2, b"s74-probe") + ld(7, graph) * graphs + ld(8, opset)


def spec() -> Any:
    """The synthetic `GuardSpec`; imports `phase_guard` only when called."""
    from avkit_infra.tts.phase_guard import GuardSpec

    return GuardSpec(SOURCE_SHA256, SOURCE_BYTES, GUARDED_SHA256)


def __getattr__(name: str) -> Any:
    if name == "SPEC":
        return spec()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
