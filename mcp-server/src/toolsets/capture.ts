import { z } from "zod";

const VARIANT_WIRES = ["original", "annotated"] as const;
const REQUEST_STATUS_WIRES = ["pending", "completed", "cancelled", "expired"] as const;
const CAPTURE_MIN_EDGE_PX = 8;
const TEXT_MAX_CHARS = 500;
// PIXELATE_BLOCK (Session 39): optional here; the API applies the default.
const PIXELATE_BLOCK_MIN = 2;
const PIXELATE_BLOCK_MAX = 100;

// Its base64 plus the JSON-RPC envelope must fit the SDK's 10 MiB stdio buffer; a longer line closes the connection.
export const IMAGE_MAX_BYTES = 7_800_000;
/**
 * Capture ids are server-minted opaque tokens (uuid4). Anything else is refused at the boundary,
 * so agent text can never reach the USER_CONFIRM prompt or the request path (review F1).
 */
export const CAPTURE_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/;
const captureId = z.string().regex(CAPTURE_ID_PATTERN, "id must be an opaque capture id");
export const GET_QUERY_KEYS = [
  "variant",
  "status",
  "x",
  "y",
  "width",
  "height",
  "unit",
  "max_edge",
] as const;
// REGION_VIEW (MEU-128, D-409): the bounds of max_edge, as the API checks them.
export const REGION_MAX_EDGE_MIN = 64;
export const REGION_MAX_EDGE_MAX = 2576;

function desc(action: string, method: string, path: string): string {
  return [
    `Workflow: call avkit_capture ${action} to ${method} ${path} then poll list/get.`,
    `Prerequisite: local screen grab or inbox files; Capture never uploads YouTube.`,
    `Returns: JSON from ${method} ${path} with path pointers, or image content for image.`,
    `Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.`,
  ].join(" ");
}

// Design 6.7 (D-415): the capture action's import mode.
const IMPORT_TEXT =
  "mode=import copies a local image (png, jpg, jpeg, webp; absolute path) into the capture inbox as a new shot so image, crop and annotate work on it. The source file is never changed.";

// Design 6.7 (D-412): the image action's region view and its frame item.
const REGION_VIEW_TEXT =
  'Optional x/y/width/height returns just that region from the full-resolution image, scaled to fit max_edge (default 1568; pass 2576 for high-resolution vision). Writes no file. Coordinates are original pixels, or unit: "fraction" (0–1) when you read them off a scaled view. The first content item gives the frame: source px = region.x + x / scale.';

// CROP_MCP (MEU-130, D-492, D-494): the crop action writes a new shot.
const CROP_TEXT =
  "Writes the region as a NEW shot (PNG) and returns its id and paths; the source is never changed. Same coordinates as image: original pixels, or unit: \"fraction\" (0–1). A box past the edge is clamped and `applied` reports what was cut. Saved marks are carried over and clipped to the region; `marks` counts kept, clipped and dropped. Optional name sets the file name (letters, digits, space, dot, underscore, hyphen). Like ImageMagick `-crop WxH+X+Y +repage`, without the virtual canvas.";

// FRAMES_MCP (MEU-134, D-583): frames has its own four markers, not desc()'s shared lines.
// D-577 A: at most 20 frames. D-576 A: a raw stream with no duration takes only at.
const FRAMES_MAX = 20;
const timeValue = z.union([z.number().nonnegative(), z.string().min(1).max(32)]);
const FRAMES_TEXT = [
  // D-605 (MEU-135): sheet finds the moment between probe and frames.
  "Workflow: call avkit_convert probe for the duration, then avkit_capture sheet to find the moment, then frames to POST /captures/frames for exact stills, then image to view a frame.",
  "Prerequisite: a local absolute video path and FFmpeg; the video is read in place, never changed or uploaded.",
  "Returns: JSON with the video's duration and size and each new shot's id, path, time_ms and timecode; no image bytes.",
  "Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.",
  'Give at (1-20 times: seconds, or "HH:MM:SS.mmm") or count (1-20 evenly spaced frames, with optional start and end).',
  "Each frame is the first one at or after its time; a time after the last video frame but before the end returns the last frame.",
  "Frames are new shots, so image, crop and annotate work on them.",
  "A raw stream with no duration takes only at, and is slow; remuxing it with avkit_convert add (fast copy) gives it a duration.",
].join(" ");

// SHEET_MCP (MEU-135): sheet has its own four markers. D-601 A: grid at most 5.
const SHEET_TEXT = [
  "Workflow: call avkit_convert probe for the duration, then avkit_capture sheet to POST /captures/sheet for a grid over a span, then frames for exact stills, then image to view the sheet.",
  "Prerequisite: a local absolute video path and FFmpeg; the video is read in place, never changed or uploaded.",
  "Returns: JSON with the video's duration and size, the new shot's id, path and size, spacing_ms and each cell's number, time_ms and timecode; no image bytes.",
  "Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.",
  "One labelled grid image of a span (default the whole video): grid 2-5 (default 3, so 9 cells), max_edge 64-2576 (default 1568).",
  "Cells sit at the midpoints of equal parts of the span; each is the first frame at or after its time, and a time after the last video frame but before the end shows the last frame.",
  "Cite times from cells, never from the image.",
  "To zoom, call again with a narrower start and end; no state is kept between calls.",
  "Events between cells can be missed.",
  "Needs a video with a duration.",
].join(" ");

const ANNOTATE_EXAMPLE =
  'Example annotations: [{"type": "arrow", "from": [10, 10], "to": [80, 40], "color": "red", "stroke_width": 3}, {"type": "text", "x": 12, "y": 48, "text": "Note", "color": "white", "font_size": 16}].';

export const captureDescriptions: Record<string, string> = {
  "avkit_capture.list": desc("list", "GET", "/captures"),
  "avkit_capture.get": desc("get", "GET", "/captures/{id}"),
  "avkit_capture.image": `${desc("image", "GET", "/captures/{id}/image")} variant=original|annotated. ${REGION_VIEW_TEXT} ${ANNOTATE_EXAMPLE}`,
  "avkit_capture.capture": `${desc("capture", "POST", "/captures")} ${IMPORT_TEXT}`,
  "avkit_capture.capture_interactive": desc("capture_interactive", "POST", "/captures/requests"),
  "avkit_capture.list_requests": desc("list_requests", "GET", "/captures/requests"),
  "avkit_capture.annotate": `${desc("annotate", "POST", "/captures/{id}/annotate")} ${ANNOTATE_EXAMPLE}`,
  "avkit_capture.remove": desc("remove", "DELETE", "/captures/{id}"),
  "avkit_capture.flatten": `${desc("flatten", "POST", "/captures/{id}/flatten")} Bakes the saved marks into the image file (backup first when capture.flatten_backup is on; a JPEG/WebP shot gets a new PNG copy instead); the user must also accept in the IDE.`,
  "avkit_capture.revert": `${desc("revert", "POST", "/captures/{id}/revert")} Overwrites the image file from its newest backup; the user must also accept in the IDE.`,
  "avkit_capture.crop": `${desc("crop", "POST", "/captures/{id}/crop")} ${CROP_TEXT}`,
  "avkit_capture.frames": FRAMES_TEXT,
  "avkit_capture.sheet": SHEET_TEXT,
};

function withDesc<T extends z.ZodTypeAny>(action: string, schema: T): T {
  return schema.describe(captureDescriptions[`avkit_capture.${action}`]) as T;
}

const arrowAnn = z
  .object({
    type: z.literal("arrow"),
    from: z.tuple([z.number().int(), z.number().int()]),
    to: z.tuple([z.number().int(), z.number().int()]),
    color: z.string().min(1),
    stroke_width: z.number().int(),
  })
  .strict();

const rectAnn = z
  .object({
    type: z.literal("rect"),
    x: z.number().int(),
    y: z.number().int(),
    width: z.number().int(),
    height: z.number().int(),
    color: z.string().min(1),
    stroke_width: z.number().int(),
  })
  .strict();

const highlightAnn = z
  .object({
    type: z.literal("highlight"),
    x: z.number().int(),
    y: z.number().int(),
    width: z.number().int(),
    height: z.number().int(),
    color: z.string().min(1),
    opacity: z.number().min(0).max(1),
  })
  .strict();

const textAnn = z
  .object({
    type: z.literal("text"),
    x: z.number().int(),
    y: z.number().int(),
    text: z.string().min(1).max(TEXT_MAX_CHARS),
    color: z.string().min(1),
    font_size: z.number().int(),
    bg_color: z.string().nullable().optional(),
  })
  .strict();

const pixelateAnn = z
  .object({
    type: z.literal("pixelate"),
    x: z.number().int(),
    y: z.number().int(),
    width: z.number().int(),
    height: z.number().int(),
    block_size: z.number().int().min(PIXELATE_BLOCK_MIN).max(PIXELATE_BLOCK_MAX).optional(),
  })
  .strict();

const eraserAnn = z
  .object({
    type: z.literal("eraser"),
    x: z.number().int(),
    y: z.number().int(),
    width: z.number().int(),
    height: z.number().int(),
  })
  .strict();

const annotation = z.discriminatedUnion("type", [
  arrowAnn,
  rectAnn,
  highlightAnn,
  textAnn,
  pixelateAnn,
  eraserAnn,
]);

const captureFullscreen = withDesc(
  "capture",
  z
    .object({
      action: z.literal("capture"),
      mode: z.literal("fullscreen"),
    })
    .strict(),
);

const captureRegion = withDesc(
  "capture",
  z
    .object({
      action: z.literal("capture"),
      mode: z.literal("region"),
      x: z.number().int().nonnegative(),
      y: z.number().int().nonnegative(),
      width: z.number().int().min(CAPTURE_MIN_EDGE_PX),
      height: z.number().int().min(CAPTURE_MIN_EDGE_PX),
    })
    .strict(),
);

// IMPORT_MODE (MEU-129, D-415): copy a local image into the inbox; the source is only read.
const captureImport = withDesc(
  "capture",
  z
    .object({
      action: z.literal("capture"),
      mode: z.literal("import"),
      path: z.string().min(1),
    })
    .strict(),
);

export const captureSchema = z.union([
  withDesc("list", z.object({ action: z.literal("list") }).strict()),
  withDesc("get", z.object({ action: z.literal("get"), id: captureId }).strict()),
  withDesc(
    "image",
    z
      .object({
        action: z.literal("image"),
        id: captureId,
        variant: z.enum(VARIANT_WIRES).optional(),
        // A first filter only; the API's messages stay the contract (D-412).
        x: z.number().nonnegative().optional(),
        y: z.number().nonnegative().optional(),
        width: z.number().positive().optional(),
        height: z.number().positive().optional(),
        unit: z.enum(["px", "fraction"]).optional(),
        max_edge: z.number().int().min(REGION_MAX_EDGE_MIN).max(REGION_MAX_EDGE_MAX).optional(),
      })
      .strict(),
  ),
  captureFullscreen,
  captureRegion,
  captureImport,
  withDesc("capture_interactive", z.object({ action: z.literal("capture_interactive") }).strict()),
  withDesc(
    "list_requests",
    z
      .object({
        action: z.literal("list_requests"),
        status: z.enum(REQUEST_STATUS_WIRES).optional(),
      })
      .strict(),
  ),
  withDesc(
    "annotate",
    z
      .object({
        action: z.literal("annotate"),
        id: captureId,
        annotations: z.array(annotation),
      })
      .strict(),
  ),
  withDesc(
    "remove",
    z.object({ action: z.literal("remove"), id: captureId, confirm: z.literal(true) }).strict(),
  ),
  withDesc(
    "flatten",
    z.object({ action: z.literal("flatten"), id: captureId, confirm: z.literal(true) }).strict(),
  ),
  withDesc(
    "revert",
    z.object({ action: z.literal("revert"), id: captureId, confirm: z.literal(true) }).strict(),
  ),
  withDesc(
    "crop",
    z
      .object({
        action: z.literal("crop"),
        id: captureId,
        // A first filter only; the API's REGION_RESOLVE and CROP_NAME messages stay the contract.
        x: z.number().nonnegative(),
        y: z.number().nonnegative(),
        width: z.number().positive(),
        height: z.number().positive(),
        unit: z.enum(["px", "fraction"]).optional(),
        name: z.string().min(1).max(80).optional(),
      })
      .strict(),
  ),
  withDesc(
    "frames",
    z
      .object({
        action: z.literal("frames"),
        path: z.string().min(1).max(4096),
        at: z.array(timeValue).min(1).max(FRAMES_MAX).optional(),
        count: z.number().int().min(1).max(FRAMES_MAX).optional(),
        start: timeValue.optional(),
        end: timeValue.optional(),
      })
      .strict()
      .refine(
        (v) =>
          (v.at === undefined) !== (v.count === undefined)
          && (v.at === undefined || (v.start === undefined && v.end === undefined)),
        { message: "frames takes either at or count; start and end go with count" },
      ),
  ),
  withDesc(
    "sheet",
    z
      .object({
        action: z.literal("sheet"),
        path: z.string().min(1).max(4096),
        start: timeValue.optional(),
        end: timeValue.optional(),
        grid: z.number().int().min(2).max(5).optional(),
        max_edge: z.number().int().min(64).max(2576).optional(),
      })
      .strict(),
  ),
]);
