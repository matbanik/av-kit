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
export const GET_QUERY_KEYS = ["variant", "status"] as const;

function desc(action: string, method: string, path: string): string {
  return [
    `Workflow: call avkit_capture ${action} to ${method} ${path} then poll list/get.`,
    `Prerequisite: local screen grab or inbox files; Capture never uploads YouTube.`,
    `Returns: JSON from ${method} ${path} with path pointers, or image content for image.`,
    `Errors: TOOL_ERROR with envelope code and message; extra keys rejected before fetch.`,
  ].join(" ");
}

const ANNOTATE_EXAMPLE =
  'Example annotations: [{"type": "arrow", "from": [10, 10], "to": [80, 40], "color": "red", "stroke_width": 3}, {"type": "text", "x": 12, "y": 48, "text": "Note", "color": "white", "font_size": 16}].';

export const captureDescriptions: Record<string, string> = {
  "avkit_capture.list": desc("list", "GET", "/captures"),
  "avkit_capture.get": desc("get", "GET", "/captures/{id}"),
  "avkit_capture.image": `${desc("image", "GET", "/captures/{id}/image")} variant=original|annotated. ${ANNOTATE_EXAMPLE}`,
  "avkit_capture.capture": desc("capture", "POST", "/captures"),
  "avkit_capture.capture_interactive": desc("capture_interactive", "POST", "/captures/requests"),
  "avkit_capture.list_requests": desc("list_requests", "GET", "/captures/requests"),
  "avkit_capture.annotate": `${desc("annotate", "POST", "/captures/{id}/annotate")} ${ANNOTATE_EXAMPLE}`,
  "avkit_capture.remove": desc("remove", "DELETE", "/captures/{id}"),
  "avkit_capture.flatten": `${desc("flatten", "POST", "/captures/{id}/flatten")} Bakes the saved marks into the image file (backup first when capture.flatten_backup is on; a JPEG/WebP shot gets a new PNG copy instead); the user must also accept in the IDE.`,
  "avkit_capture.revert": `${desc("revert", "POST", "/captures/{id}/revert")} Overwrites the image file from its newest backup; the user must also accept in the IDE.`,
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
      })
      .strict(),
  ),
  captureFullscreen,
  captureRegion,
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
]);
