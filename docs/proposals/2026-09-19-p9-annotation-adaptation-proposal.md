# Phase 9 annotation adaptation recommendation

Date: 2026-09-19. Advisory proposal for the owner; no implementation or review verdict. Local citations describe the working tree inspected for this recommendation.

## 1. Executive recommendation

Keep F2, the native Windows picker, inbox, filmstrip, four existing tools, renderer history, strict annotation boundaries, immutable originals, and Pillow baking.
Repair the human path before enlarging it: image-coordinate mapping, preview/bake agreement, truthful Save feedback, baked-image inspection, and reloading editable annotations.
Adapt interaction rules from ShareX and Flameshot; use snap and Blip as examples of human marks becoming useful agent input.
Keep React + SVG and Pillow. These primitives do not justify another drawing engine or package.
Propose only two additions: an outline `circle` first, then a numbered `marker` if the owner wants stable visual references.
Both are currently named deferrals; this proposal requests a future, explicit spec change rather than treating them as already authorized scope.
Ship each addition through the GUI and existing bake path before advertising it to MCP.
Use the same full-list annotation DTO for GUI saves, agent suggestions, agent commits, and sidecars.
Suggestions can be ordinary JSON loaded into the GUI as an unsaved draft; no new REST action or Electron MCP server is needed.
Keep freehand, blur, curved arrows, spotlight, frames, in-picker ink, and macOS/Linux picking deferred. Capture remains a catalog, never a queue.

The governing local intent is `docs/BUILD_PLAN.md:129`; the existing four-tool and deferral contracts are `docs/build-plan/09-screenshot-capture.md:133` and `docs/build-plan/09-screenshot-capture.md:551`.

## 2. Adaptation map

Target abbreviations below name files actually inspected:

| Target | Local file and relevant entry point |
|---|---|
| Viewport | `ui/src/renderer/src/features/capture/CaptureViewport.tsx:37` — SVG marks; pointer mapping at line 195 |
| Page | `ui/src/renderer/src/features/capture/CapturePage.tsx:28` — selection, history, gestures, Save |
| Renderer DTO | `ui/src/renderer/src/features/capture/capture-annotate.ts:8` |
| Commands / image loader | `ui/src/renderer/src/features/capture/capture-commands.ts:69`; `ui/src/renderer/src/features/capture/capture-image.ts:15` |
| Domain / port | `packages/core/src/avkit_core/domain/capture.py:123`; `packages/core/src/avkit_core/ports/capture.py:18` |
| Service | `packages/core/src/avkit_core/services/capture.py:294` — save; clamp at line 474 |
| Bake | `packages/infrastructure/src/avkit_infra/capture/adapter.py:114` |
| REST / API DTO | `packages/api/src/avkit_api/routes/captures.py:206`; `packages/api/src/avkit_api/schemas/captures.py:53` |
| MCP | `mcp-server/src/toolsets/capture.ts:11` |

“Small adapt” means a bounded change to these existing surfaces, not a claim that persistence and concurrency require no design. External references establish the behavior; av-kit-specific choices below are recommendations, not claims that upstream implemented av-kit's exact contract.

| Behavior | Proven source (repo + file or README section) | av-kit target file(s) | Delta (keep / small adapt / defer) | New dependency? |
|---|---|---|---|---|
| Hotkey → capture → inbox | [ShareX source map](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Forms/RegionCaptureForm.cs); [snap, The Flow](https://github.com/adjective-rob/snap#the-flow) | `native/region-picker/Program.cs:127`; `ui/src/main/capture-picker.ts:535` | **Keep** av-kit's light picker/page split; do not import their annotation overlay | No |
| Image and marks share zoom/pan | [ShareX RegionCaptureForm, ZoomTransform/OnPaint](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Forms/RegionCaptureForm.cs) | Viewport, Page | **Small adapt:** one image-space SVG transform and its inverse for input | No |
| Object history, selection and tool configuration | [ShareX ShapeManager, CurrentShape/CurrentTool and keyboard handling](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Shapes/ShapeManager.cs) | Page, Viewport | **Keep** snapshot history; **small adapt** selection/edit/delete, tool-specific controls and scoped shortcuts | No |
| Text has an explicit editing lifecycle | [Flameshot texttool.cpp, widget/editingFinished](https://github.com/flameshot-org/flameshot/blob/master/src/tools/text/texttool.cpp); [snap, Annotation Tools](https://github.com/adjective-rob/snap#annotation-tools) | Page, Viewport | **Keep** Enter/Esc; **small adapt** draft isolation, overflow feedback and background preview | No |
| PNG plus structured annotation data | [snap, What Gets Saved](https://github.com/adjective-rob/snap#what-gets-saved) | Service, REST/API DTO, Page, image loader | **Keep** sibling files; **small adapt** load saved vectors and inspect the bake | No |
| Human marks become agent input | [Blip, What it does / Usage](https://github.com/nebenzu/Blip#what-it-does) | Page, MCP | **Keep** annotated image retrieval; teach the reverse human → agent loop | No |
| Circle and numbered badge | [image-annotator-mcp, Annotation types](https://github.com/vapvarun/image-annotator-mcp#annotation-types); [agent-browser, Annotated Screenshots](https://github.com/vercel-labs/agent-browser#annotated-screenshots) | Domain, Renderer DTO, API DTO, Service, Bake, Viewport/Page; MCP last | **Small adapt:** `circle`, then `marker`; no speech-bubble engine | No |
| Explicit pixel positions and bounds handling | [mcp-screenshot-server, precise_annotate / _auto_adjust_position](https://github.com/aamar-shahzad/mcp-screenshot-server/blob/main/src/mcp_screenshot_server/server.py) | Service, Viewport, MCP descriptions | **Keep** pixel DTO and clamp; **small adapt** extent handling and valid examples; omit named-position grammar | No |
| Rect and highlight remain different tools | [Flameshot README, Keyboard shortcuts](https://github.com/flameshot-org/flameshot#keyboard-shortcuts); [Blip, Drawing tools](https://github.com/nebenzu/Blip#drawing-tools) | Viewport, Bake | **Keep** unfilled box versus translucent fill | No |
| Legible labels on busy/dark images | [image-annotator-mcp, Annotation types / Changelog](https://github.com/vapvarun/image-annotator-mcp#annotation-types) | Viewport, Page, Bake | **Small adapt:** expose existing `bg_color`, matching preview, contrast presets | No |
| Suggest without saving | [snap, structured JSON](https://github.com/adjective-rob/snap#what-gets-saved); [Blip, human annotation loop](https://github.com/nebenzu/Blip#usage) | Renderer DTO, Page, Viewport | **Small adapt:** av-kit-specific synthesis: validate pasted proposal JSON into current draft and history | No |
| Concurrent GUI/agent saves | [HTTP If-Match lost-update rule](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1); [Python os.replace](https://docs.python.org/3/library/os.html#os.replace) | Service, REST, Commands; MCP after GUI | **Small adapt, separate slice:** conditional replacement, per-shot serialization and staged files; no named annotator's concurrency guarantee was verified | No |
| Windows overlay and embedded MCP comparison | [Shotik, Flameshot-style overlay / Built-in MCP server](https://github.com/gorka2354/shotik#features) | Keep `native/region-picker/`; keep existing MCP | **Defer/reject** that architecture; borrow only the short capture-to-inspection flow | No |

The layout mockup is composition guidance, not evidence that annotation correctness is solved: it retains four buttons at `docs/proposals/2026-09-03-capture-page-layout-mockup.html:246` and calls the draw surface unchanged at line 350. Fixing the transform must supersede that “unchanged” assumption without reopening the wider page-layout phase.

## 3. GUI-first implementation order

1. **Make the four-tool human path trustworthy.** First write failing tests for scaled/letterboxed placement, pointer release outside the image, and saved PNG location. Use one SVG image-space transform, capture pointer gestures, show an in-progress mark, preserve one undo step per completed gesture, and cancel without adding history. Repair the visual mismatches in §4. After Save, fetch `variant=annotated` and provide an explicit baked-result view; return to original-plus-vectors for editing. Never draw the vectors over an already baked image. Add circle only after these checks pass, as the one primitive in the smallest next MEU.

2. **Complete editing, recovery and honest Save state.** Keep Enter to commit text and Esc to cancel. Stop text-editor pointer events from starting a new mark; ignore composing IME Enter; keep keyboard shortcuts out of focused text fields. Keep the dirty-switch confirmation but include a nonempty text draft in “dirty.” Show only relevant controls: color/stroke for arrow, box and circle; color/opacity for highlight; color/font size/background for text. Add Ctrl+Z, Ctrl+Y/Ctrl+Shift+Z and Ctrl+S through the same handlers as buttons. Preserve F2. Add an accessible mark list with edit/delete and simple move controls before attempting a complex resize-handle system.

3. **Reopen saved vectors and protect replacements.** Extend the existing shot-detail GET response to include the validated saved annotation list and an annotation revision; do not add a write endpoint. Load that list as both draft and saved baseline when selecting a shot. A malformed/unsupported sidecar is an error, never an empty list that Save can silently erase. Implement the concurrent-save contract in §7 before enabling enhanced agent writes. Test human save → switch away → reopen → edit/delete one mark → save, including marks originating outside the page.

4. **Add numbered markers, only if selected by the owner.** Deliver the GUI tool, SVG preview, domain/API validation, sidecar round trip and Pillow bake together. Auto-number new marks; retain explicit numbers through undo, reload and deletion. Prove a human can place, change and remove a marker. Existing four tools and circle remain usable throughout.

5. **Let a human inspect a proposal without committing it.** Add “Load proposal” for pasted `{ "annotations": [...] }`, parsed by the existing renderer schema. On the selected shot, show its name and dimensions, apply dirty-replacement confirmation, then replace the draft as one undoable operation. It must make no POST. This is an explicit human-mediated transport from agent conversation to GUI; it is not automatic agent-to-renderer delivery.

6. **Only then improve MCP.** Publish matching schema changes, exact examples, dimension guidance and conditional-save metadata. Test read → suggest → human edit, and read → authorized commit → read annotated → human reopen/edit. Keep the existing `capture_interactive` request/poll route.

Current evidence matters: history exists at `ui/src/renderer/src/features/capture/CapturePage.tsx:126` and line 408; dirty state omits `textDraft` at line 53; selecting a shot clears vectors at line 132. Save currently marks the list saved at line 268 even though invalid renderer input can silently return from `ui/src/renderer/src/features/capture/capture-commands.ts:73`. Replace that silent return with visible failure, and snapshot shot ID plus submitted list so an asynchronous response cannot mark another shot or later edits clean. The image loader currently requests only the default original (`ui/src/renderer/src/features/capture/capture-image.ts:15`).

Each slice needs tests first and a real Electron Playwright human-path check before being called working. Extend the existing capture tests rather than introducing a separate harness. No tests or GUI were run for this advisory document.

## 4. Coordinate + bake contract

**One coordinate space:** original image pixels, origin at its top-left, integer DTO coordinates; width, stroke and font sizes use that same space. Desktop coordinates stop at capture. Device scale is already represented in the saved image dimensions; do not multiply renderer pointer coordinates by `devicePixelRatio` again.

**Confirmed defect:** `ui/src/renderer/src/features/capture/CaptureViewport.tsx:197` and line 201 subtract only the container origin. The image is independently fitted with `object-contain` at line 209, while the SVG has no `viewBox` at line 212. `CaptureViewportProps` at line 12 does not receive original dimensions. This fails whenever displayed image size differs from the original, and letterboxing adds another offset. It is a current fit-to-viewport defect, not merely a future zoom concern.

For an original `W × H` inside a container `Cw × Ch`, the fit model is:

```text
s  = min(Cw / W, Ch / H)
ox = (Cw - W*s) / 2
oy = (Ch - H*s) / 2
x  = round((clientX - containerLeft - ox) / s)
y  = round((clientY - containerTop  - oy) / s)
```

For example, a 1600×900 shot inside 800×600 has scale 0.5 and a 75-pixel top letterbox. Container point (400,300) maps to image point (800,450), not (400,300).

Prefer a single SVG `viewBox="0 0 W H"` containing the image and marks, with `preserveAspectRatio="xMidYMid meet"`. Transform pointer positions through the inverse screen matrix; use the forward matrix for the HTML text editor. Ignore pointer-down in letterbox margins; clamp a captured drag at image boundaries; cancel on pointer cancellation. Guard unloaded images, zero-sized surfaces and unavailable/invertible matrices. This adapts ShareX's common drawing transform using the browser's existing [SVG matrix API](https://developer.mozilla.org/en-US/docs/Web/API/SVGGraphicsElement/getScreenCTM).

Fit is the required mode. Optional 100%/zoom controls must change only this presentation transform, not stored coordinates or stroke widths. Resizing the window must not rewrite annotations. Keep scroll zoom optional under `docs/build-plan/09-screenshot-capture.md:146`.

The canonical FIC should pin geometry and colors with shared cross-language fixture values; TypeScript and Python implement the same rules. It should not promise identical browser/Pillow antialiasing.

| Element | Current mismatch or existing behavior | Recommended agreement |
|---|---|---|
| Arrow | SVG uses fixed 10×4 head geometry (`CaptureViewport.tsx:37`); Pillow uses `max(10, 4*stroke_width)` and angle 0.4 (`packages/infrastructure/src/avkit_infra/capture/adapter.py:250`) | Keep the existing Pillow formula and reproduce its vertices in SVG. Pin shaft cap and endpoint behavior in fixtures. A zero-length gesture creates no GUI mark; legacy/API zero-length arrows have explicitly matched no-head rendering. |
| Box | SVG strokes are centered; Pillow uses its rectangle outline (`packages/infrastructure/src/avkit_infra/capture/adapter.py:263`) | Preserve unfilled boxes and define edge inclusion. Match the bake's inward outline with an inset SVG outline; handle widths thicker than a small box. Test odd/even strokes and image-edge clipping. |
| Highlight | Pillow already alpha-composites and uses `x+width-1`, `y+height-1` (`packages/infrastructure/src/avkit_infra/capture/adapter.py:226`) | Keep that raster extent and paint order. Quantize preview opacity to the same 8-bit alpha. Do not substitute a filled opaque box or a CSS blend mode. Zero-area fills are no-ops. |
| Text | SVG uses an implicit baseline and no background (`CaptureViewport.tsx:95`); Pillow uses its font fallback and draws `bg_color` (`packages/infrastructure/src/avkit_infra/capture/adapter.py:274`) | Specify the existing Pillow anchor explicitly, then align SVG using matching font metrics. Keep Segoe UI → Arial → default fallback, detect/report fallback mismatch, and draw the existing optional background in preview. Measure ink bounds, including bearings and explicit newlines; do not equate `y` with a browser baseline. |
| Circle / marker | Proposed, not shipped | Derive one bounding box from center/radius or diameter, match inward outline/fill, and use the same text-metric rules to center marker numbers. Clip to the original image rectangle. |

Pillow already provides ellipse outlines/fills, polygons and measured text bounds. No dependency is missing. Its [ImageDraw documentation](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html) also makes clear why font anchors and bounding boxes must be specified. Bake output is the authoritative shareable result; visual tests should allow a documented raster-edge tolerance while testing geometry and interior colors exactly.

## 5. DTO growth

The current union is `packages/core/src/avkit_core/domain/capture.py:209`; corresponding renderer and API unions are `ui/src/renderer/src/features/capture/capture-annotate.ts:54` and `packages/api/src/avkit_api/schemas/captures.py:99`. Preserve `arrow/rect/highlight/text` field names, including `from`/`to` on the wire and `from_xy`/`to_xy` inside Python. Do not import upstream camelCase or its broader color vocabulary.

Proposed additions, with every field required unless stated otherwise:

| Type | Exact wire fields | Semantics and validation |
|---|---|---|
| `circle` | `type: "circle"`, `x: int`, `y: int`, `radius: positive int`, `color: existing Color`, `stroke_width: positive int` | `x,y` are the center, not a top-left corner. Outline only. GUI center-to-edge drag; all lengths in original pixels. Python `CircleAnnotation` carries the fields other than the discriminator, following existing dataclass style. |
| `marker` | `type: "marker"`, `x: int`, `y: int`, `number: int (1..999)`, `size: positive int`, `color: existing Color` | `x,y` are the badge center; `size` is diameter. Filled circular badge; derive black/white number color from fill contrast and fit the number using text metrics. Python `MarkerAnnotation` follows the same convention. No leader, text payload, style enum or automatic layout. |

These names adapt the `circle` and `marker` vocabulary in [image-annotator-mcp](https://github.com/vapvarun/image-annotator-mcp#annotation-types), while retaining av-kit's `stroke_width` convention. They are deliberately smaller contracts. A nearby existing arrow and text label can explain a marker without creating a compound callout language.

**Circle is the first candidate:** it can ring a target without covering it, has clear human value, and requires SVG circle plus Pillow ellipse. **Marker is second:** it gives human and agent a durable number to discuss, borrowing the reference-label idea from [agent-browser](https://github.com/vercel-labs/agent-browser#annotated-screenshots). Unlike agent-browser, av-kit has no DOM element references: a number identifies a mark on a particular shot/revision, not a clickable UI object.

The 1..999 number limit, center semantics and explicit marker diameter are proposed av-kit product choices, not pre-existing spec facts. Keep numbers unique within a list; choose `max(existing numbers)+1` for a new GUI marker, preserve gaps, and show a validation message at the limit. Never renumber existing marks silently.

Lift only circle and numbered markers from `docs/build-plan/09-screenshot-capture.md:558` in a future plan. Freehand adds sampling/simplification and hit-testing; blur adds pixel-effect/redaction semantics; curved arrows add control points and tangent rules. None is needed for the requested two loops.

Keep one logical DTO across all clients. Today the validators already differ: renderer stroke is positive at `capture-annotate.ts:12`, whereas MCP accepts any integer at `mcp-server/src/toolsets/capture.ts:41`; the renderer color regex accepts arbitrary alphabetic names at line 6, whereas the domain allows only seven names at `packages/core/src/avkit_core/domain/capture.py:28`. Align constraints with shared valid/invalid fixture payloads. Pydantic `extra="forbid"` rejects unknown fields but does not by itself enable strict numeric typing (`packages/api/src/avkit_api/schemas/common.py:11`); use annotation-specific strict integer validation for new and reconciled fields rather than changing unrelated APIs.

Keep reading version-1 sidecars. Document a version bump when writing newly supported types, and reject unsupported versions/types visibly before permitting edits. Tolerating unknown sidecar metadata must not mean dropping unknown marks. The current parser is permissive (`packages/core/src/avkit_core/services/capture.py:52`); the new read path must validate known annotation fields and preserve the original file on failure. Request bodies remain strict; the sidecar's `version` wrapper is not an extra field to POST.

## 6. MCP agent loop

The current tool is one compound `avkit_capture`, with `action` in its input. `avkit_capture.image` and `.annotate` are description keys, not grounds for inventing separately named tools. Existing image/annotate schemas are at `mcp-server/src/toolsets/capture.ts:110` and line 132. Descriptions at line 11 currently contain no concrete annotation example.

Teach this sequence:

1. Select a shot with `list/get`, or use `capture`; for `capture_interactive`, poll `list_requests` until completion and take its `shot_id`. Keep `CaptureRequest`, not reverse RPC.
2. Read shot width/height and the original image. An agent needs image content, not merely a filesystem path. Preserve the 15 MiB limit (`packages/api/src/avkit_api/routes/captures.py:42`). On 413, do not invent coordinates or silently resize the original.
3. Inspect and reason. If the user asked for suggestions, return the full proposed `{ "annotations": [...] }` body in conversation, with shot ID, dimensions and rationale outside that body. Do not call annotate. The human can load it into the GUI draft, edit it, undo it or discard it.
4. If the user requested drawing/saving, submit the complete list through the existing annotate action, preserving existing marks unless replacement was intended. After the detail-response enhancement, read saved annotations and revision first. An empty list deliberately clears both derived files.
5. Read `image` with `variant="annotated"` to verify placement. Report uncertainty if target identification remains ambiguous; a valid coordinate is not proof that it names the right control.

Example calls below fit the **currently shipped four-type schema**. Substitute a real shot ID returned by av-kit; the example assumes a 1600×900 original.

```json
{
  "action": "image",
  "id": "7f47b859-311b-4d65-826e-a55ea9d25e24",
  "variant": "original"
}
```

The GUI POST body, and the exact suggestion body to load without saving:

```json
{
  "annotations": [
    {
      "type": "arrow",
      "from": [700, 220],
      "to": [900, 320],
      "color": "#FF0000",
      "stroke_width": 3
    },
    {
      "type": "text",
      "x": 700,
      "y": 170,
      "text": "Check this control",
      "color": "white",
      "font_size": 20,
      "bg_color": "black"
    }
  ]
}
```

The corresponding current MCP commit:

```json
{
  "action": "annotate",
  "id": "7f47b859-311b-4d65-826e-a55ea9d25e24",
  "annotations": [
    {
      "type": "arrow",
      "from": [700, 220],
      "to": [900, 320],
      "color": "#FF0000",
      "stroke_width": 3
    },
    {
      "type": "text",
      "x": 700,
      "y": 170,
      "text": "Check this control",
      "color": "white",
      "font_size": 20,
      "bg_color": "black"
    }
  ]
}
```

```json
{
  "action": "image",
  "id": "7f47b859-311b-4d65-826e-a55ea9d25e24",
  "variant": "annotated"
}
```

Descriptions should explicitly forbid extra keys such as `label`, `reason`, `strokeWidth`, `position`, `preview` and `version` in these bodies. Circle/marker examples belong in tool descriptions only after the GUI and backend support them. Conditional-save metadata from §7 is a future transport extension, not a key that works in today's example.

**No new suggestion action now.** A renderer draft already contains an annotation list; validated paste provides a concrete way to populate it without POST. Automatic remote proposal delivery would need additional persistence/notification semantics and is not necessary to satisfy the human-mediated loop. Saved agent marks become editable through the same detail GET and mark list as human marks; no author-specific shape type or second overlay schema is needed.

## 7. Edge cases already solved elsewhere — import the rule, not the code

| Edge case | Rule and smallest local adaptation |
|---|---|
| DPI / physical pixels | **Keep.** The picker contract already handles PerMonitorV2, negative monitor origins, freeze-before-show, `CAPTUREBLT` and opaque alpha (`docs/build-plan/09-screenshot-capture.md:210`; `native/region-picker/ScreenCaptureSource.cs:91` and line 136). ShareX's capture/editor split is inspiration, not a reason to rework this. Renderer fit correction must not alter capture pixels. |
| Black/empty capture | **Keep** rejection before publication (`ui/src/main/capture-picker.ts:469`) and adapter guard (`packages/infrastructure/src/avkit_infra/capture/adapter.py:193`). Do not confuse a dark but valid screenshot with a need for generative enhancement. |
| Bounds clamp | The external server has position-adjustment rules, but also permits partially off-image positions. Adapt the bounded-geometry intent, not its 10-pixel offsets. av-kit's service already clamps points, but rect/highlight widths remain unchanged (`packages/core/src/avkit_core/services/capture.py:493`). Specify intersection with image extents, rather than moving an off-image rectangle and accidentally enlarging its visible area. Preserve `[0,W] × [0,H]` geometric edges from the spec; raster indices stop at `W-1,H-1`. Clip circle ink without turning it into an ellipse. Keep an entire numbered badge visible where it fits; reject an impossible badge size. [Source: position helpers](https://github.com/aamar-shahzad/mcp-screenshot-server/blob/main/src/mcp_screenshot_server/server.py). |
| Text overflow | Flameshot tracks an editable text area; Pillow supplies ink bounds. Keep the 500-character limit, measure actual glyphs/background, show overflow before save, and clip at image edges consistently. Preserve explicit newlines; do not silently reflow or truncate text. Reposition/resize is a human edit. [Source: TextTool](https://github.com/flameshot-org/flameshot/blob/master/src/tools/text/texttool.cpp). |
| Zero-length arrow / zero-area fill | The local arrow already avoids dividing by zero after drawing the shaft (`packages/infrastructure/src/avkit_infra/capture/adapter.py:247`). **Keep** that defensive rule, suppress accidental GUI clicks, and pin legacy rendering. Guard zero-width/height highlights before Pillow receives reversed rectangle endpoints. Do not turn a degenerate list into `[]`, which has destructive clear semantics. |
| Highlight versus rect | **Keep** fill-only alpha versus outline-only box. Apply annotations in list order in both renderers. Existing alpha compositing is at `packages/infrastructure/src/avkit_infra/capture/adapter.py:226`; Blip's separate highlight tool supports the semantic distinction. |
| Annotated PNG scan collision | **Keep** the explicit case-insensitive suffix exclusion at `packages/core/src/avkit_core/services/capture.py:142`. snap's paired artifacts support the product idea, but this exact collision guard is already av-kit's solution. Ensure future temporary bake names cannot be scanned as originals. |
| Extra-key 422 | **Keep** API `extra="forbid"` and renderer/MCP `.strict()`. Unknown keys reaching REST return 422; MCP may reject them before any HTTP request. Reconcile value constraints without weakening this behavior. These rules are already local, not borrowed from a permissive external annotator. |
| Concurrent annotate | Current save writes the fixed bake and then sidecar directly, with no explicit per-shot lock or stale-write check in the method (`packages/core/src/avkit_core/services/capture.py:300`). Add per-shot serialization shared by annotate, clear, delete and corresponding reads; a renderer-disabled Save button alone cannot protect against MCP. Use a persisted annotation revision exposed by existing GET and a conditional POST, following HTTP `If-Match`. Compare the revision inside the write critical section; stale submissions fail with 412 and retain the GUI draft. [Source: RFC 9110 §13.1.1](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.1). |
| Consistent file publication | Stage PNG and JSON outside the flat scan's recognized originals, then publish under the same shot lock and update metadata/revision only on success. Keep the previous successful pair recoverable on failure. `os.replace` replaces one file, not a PNG/JSON/database transaction; interruption/recovery and multi-process writer ownership require explicit tests before promising atomicity. This is a bounded persistence follow-up, not a new queue. [Source: Python filesystem API](https://docs.python.org/3/library/os.html#os.replace). |
| Fit / zoom / resize | Adapt ShareX's shared transform, keep original-pixel DTOs. Test different aspect ratios, letterbox clicks, window resize, 100% view and Windows display scaling. Transform the text editor as well as SVG marks. [Source: RegionCaptureForm](https://github.com/ShareX/ShareX/blob/develop/ShareX.ScreenCaptureLib/Forms/RegionCaptureForm.cs). |
| Color contrast | Expose existing opaque text background; offer black/white/yellow presets and a visible color sample. For markers derive contrasting digits from badge fill. Keep the screenshot unchanged outside actual marks: do not bake a global dim layer borrowed from another product. [Source: image-annotator-mcp label legibility](https://github.com/vapvarun/image-annotator-mcp#annotation-types). |
| Agent coordinate hallucination | Read dimensions and image first, translate any model-view downscaling explicitly, preserve crop origin, and inspect the bake. Never treat an edge-clamped arrow as confirmation of the intended target. Prefer a suggestion when uncertain. Agent-browser's numbered references inspire discussion, but its DOM mapping does not exist in desktop PNGs. [Source: agent-browser](https://github.com/vercel-labs/agent-browser#annotated-screenshots). |
| Original / clear / Delete | **Keep** baking from original (`packages/infrastructure/src/avkit_infra/capture/adapter.py:122`), empty-list removal of derived files (`packages/core/src/avkit_core/services/capture.py:311`), and confirmed destructive Delete of all three files (`packages/core/src/avkit_core/services/capture.py:357`). Delete-selected-mark must be a separate editor action from Delete-capture. |

Conditional saves require a coordinated contract update: GET supplies the saved list and revision; GUI sends the revision as `If-Match`; the existing MCP action later gains equivalent request metadata that its HTTP adapter maps to that header. Annotation objects remain identical. Once protected writes ship, all shipped writers must supply a baseline; an unconditional legacy route would otherwise bypass lost-update protection. A list refresh while the GUI is dirty should show “saved version changed” and offer reload/retain-draft, never replace the draft silently. This proposal does not claim that an in-process lock protects multiple API processes or filesystem edits by other applications.

## 8. What not to do

- Do not add Konva, Fabric.js, Paper.js, svg.js, Sharp, Cairo or OpenCV for these primitives; no npm/pip packages or git submodules from the inspiration projects. Their behavior is reading material, not a dependency plan.
- Do not send screenshots to Nano Banana, GPT Image or Flux Kontext to draw markup. Overlay JSON plus deterministic bake preserves the original; generative redrawing cannot guarantee that unrelated screenshot content remains faithful.
- Do not paste or translate ShareX/Flameshot source. Write against av-kit's FIC under Golden Rule 5.
- Do not restore Chromium transparent capture windows or put ShapeManager/ink tools into `avkit-region-picker.exe`. There is one editor, on the Capture page.
- Do not introduce a second MCP server, named-position strings, percentages, arbitrary SVG paths, upstream `strokeWidth`, or an agent-only annotation language.
- Do not expand the canvas, add screenshot frames, or mutate original dimensions to avoid clipping. Do not flatten marks and then pretend the human can still edit them individually.
- Do not pull capture into processor queues, reopen Phase 1–8 or Phase 10/11, or turn this recommendation into a page-layout redesign.
- Keep macOS/Linux picker and hotkey support a named deferral.

## 9. Spec delta sketch

If the owner opens a real plan, make only these Phase 9 changes:

- Clarify original-pixel coordinates, fitted-image offsets, pointer capture, image-edge conventions and common preview/bake geometry in the viewport/DTO sections.
- Add regression acceptance criteria for arrowheads, outline placement, text font/anchor/background, alpha overlap and degenerate shapes.
- Specify baked-result inspection, truthful Save failure, pending-save snapshots, dirty text drafts and focused-editor keyboard behavior.
- Add saved-vector reload and individual mark editing/deletion; extend the existing detail GET response with annotations and revision, preserving strict write bodies.
- Specify conditional full-list replacement, serialization, derived-file publication/recovery and stale-draft handling before enhanced agent commits.
- Move only `circle`, then optionally `marker`, out of the named-deferral row; add their exact fields, validation, sidecar version compatibility and GUI-first exit criteria.
- Add human-mediated “Load proposal” using the same annotation body, with no POST until Save; no new suggestion REST action.
- Expand MCP descriptions with current valid examples, original dimensions, full-list replacement/clear semantics, later revision metadata and annotated-image verification.
- Retain native-picker safeguards, image-byte exception and cap, request polling, immutable originals, suffix exclusion and three-file destructive Delete unchanged.

These are recommendations for future decisions. This run does not edit `docs/build-plan/09-screenshot-capture.md`, production code, tests or `task.md`.

## 10. Confidence + dissent

**High confidence** in the fit-coordinate defect and static gaps described here: the relevant implementation was read, including domain, port, service, bake, REST/API models, renderer, MCP and layout mockup. **Moderate confidence** in adaptation sizing: no application, GUI, Pillow fixture suite, MCP request or concurrent-save experiment was run. This is source inspection, not a runtime verification receipt. External READMEs establish advertised behavior, not proof that every edge case is robust.

All eight named projects were consulted through their GitHub pages or source. Several raw-file requests failed; GitHub pages supplied the READMEs and ShareX RegionCaptureForm. Flameshot's text tool and the external MCP server's coordinate helpers were readable; a useful counter-tool source view and individual ShareX arrow/text class fetches were not obtained. Numbered-marker recommendations therefore rely on documented behavior and the readable MCP server example, not a claimed audit of Flameshot's counter internals. Star-count, “highest-followed” and “newest” rankings were not verified and are not selection criteria here.

Conflicts are explicit: Flameshot documents Ctrl+Return for text commit, whereas av-kit specifies Enter/Esc; keep av-kit. External MCP examples accept named positions, broader colors and different field names; keep av-kit's pixel DTO. The external server's bounds helpers intentionally allow some off-image content; do not copy that behavior wholesale. Circle and numbered markers remain deferred in the current local spec despite their usefulness. Shotik's current README advertises OCR, translation and recording beyond screenshot markup; those features do not widen this task.

The strongest case for in-overlay annotation is its immediacy: freeze, point, explain and save in one uninterrupted visual context. ShareX and Shotik demonstrate that product flow, and snap makes the same flow useful to an agent. av-kit should still refuse it: capture reliability has already been established through a narrowly scoped native helper, while durable saved-shot editing and MCP interoperability belong to the existing page/DTO/bake path. Adding native ink would create a second editor with duplicate tools, history, text metrics and serialization. Preserve immediacy instead by selecting the newly captured shot and making its page toolbar ready to use.

**Smallest next MEU:** define a source-backed FIC and failing tests for original-pixel pointer mapping under fit/letterboxing, consistent SVG/Pillow geometry, and one new outline circle; then repair the four-tool path and deliver circle through the existing strict DTO, GUI history, sidecar and bake. Acceptance is a real Windows Electron sequence: F2 → select shot → draw arrow and circle at fitted coordinates → Undo/Redo → Save overlay → inspect the baked PNG, with the original hash unchanged. Keep named deferrals intact except the explicitly selected circle, add no package, and expose no MCP-only schema; enhanced MCP behavior follows the working human path.
