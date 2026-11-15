import type { HelpSection } from '../../components/help/HelpCard'

export const CAPTURE_HELP_SECTIONS: HelpSection[] = [
  {
    id: 'what-capture-does',
    title: 'What Capture does',
    body: 'Capture grabs a screen region with F2 or Capture region, stores PNGs in your inbox, and lets you annotate them. Capture never uploads.',
  },
  {
    id: 'f2-sharex',
    title: 'F2 vs ShareX conflict',
    body: 'If F2 is already registered by ShareX or another tool, av-kit shows a banner. Quit ShareX or pick another accelerator.',
  },
  {
    id: 'inbox-folder',
    title: 'inbox folder',
    body: 'New shots land in capture.inbox_dir as local-timestamp PNG files. Browse picks a folder; Save writes the settings PUT.',
  },
  {
    id: 'original-annotated',
    title: 'original vs .annotated.png',
    body: 'The filmstrip lists originals. Sidecar .annotated.png files are baked copies and are skipped by the inbox watcher. Flatten into image bakes the saved marks into the original file after copying it to the backup folder (Settings → Capture); a JPEG or WebP shot gets a new PNG copy instead, and the original stays unchanged. Restore backup restores the newest backup. Save annotations can write PNG, JPEG or WebP (Settings → Capture).',
  },
  {
    id: 'four-tools',
    title: 'Annotation tools',
    body: 'Seven annotation tools: Arrow, Box, Highlight, Text and Step draw on the selected shot; Redact and Smart eraser change the pixels under them, and drawn marks stay on top. Redact covers its box in Solid black by default; its Pixelate mode turns the box into blocks instead, and picking the other mode with a redaction selected swaps it. The Head control turns an arrow into a line or gives it a head at both ends, and the Shape control turns a box into an ellipse; with a mark selected, either one changes that mark. Step places the next number at each click. The Smart eraser fills its box with the most common colour along its border. A swatch applies when you pick it, and a typed hex colour applies on Enter. With a mark selected, a style control changes only that mark; with none selected, it sets the current tool\'s own colour and size, which Capture remembers. Save POSTs the full annotation list. Undo and redo stay on the open image. Marks use original image pixels and survive Save then reload. Select a mark to move it or drag an arrow end until Save. Arrow keys nudge the selected mark (Shift+arrow by 10 px), or the arrow end you grabbed or tabbed to. Ctrl+D duplicates the selected mark 10 px down and right and selects the copy. Ctrl+Z undoes and Ctrl+Y or Ctrl+Shift+Z redoes while the image has focus; a text field keeps its own undo. Drag a square handle on a selected box, ellipse, highlight, redact, pixelate or eraser mark to resize it. Double-click a text mark, or press Enter with it selected, to edit its text; drag a corner of its plate to scale it. Drag the Stroke, Size or Block size label, or use the mouse wheel or Up/Down over its field, to change the size; each gesture is one undo step. The lock is on by default: the tool stays armed after each mark and the new mark stays selected, so a style change restyles it and a press on it moves or resizes it; pick the tool again to set its own style. Turn the lock off to return to Select after each mark; Capture remembers the choice. Press V, A, R, H, T, X, E or C for Select, Arrow, Box, Highlight, Text, Redact, Smart eraser or Crop; letters type normally in a text field. Hold Shift to draw a square, keep a box\'s shape from a corner or snap an arrow to 45 degrees; hold Alt to draw a box from its centre. Shift and Alt work the same on an ellipse, and Shift snaps a line to 45 degrees. Zoom with the mouse wheel, the + / − / Fit buttons or Ctrl+= / Ctrl+- / Ctrl+0; hold Space or the middle button and drag to pan. Zoom never changes saved marks. Copy image, or Ctrl+C while the image has focus, copies the shot with its current marks, saved or not; a text field keeps its own copy. Right-click a thumbnail (or press Shift+F10) to copy its path or image, or delete it; Shift-click selects a range to delete together.',
  },
  {
    id: 'mcp-png',
    title: 'MCP can see the PNG',
    body: 'Registered shots appear in GET /captures so MCP tools can list and read the same inbox files.',
  },
  {
    id: 'close-to-tray',
    title: 'close-to-tray keeps the hotkey',
    body: 'With close-to-tray on, closing the window hides it so F2 still works. Tray Quit sets quit intent and exits.',
  },
  {
    id: 'never-uploads',
    title: 'never uploads',
    body: 'Capture is local-only. Nothing is published to YouTube.',
  },
]
