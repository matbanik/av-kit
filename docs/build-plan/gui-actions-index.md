# av-kit — GUI actions index

> Canon for every user-visible action. av-kit owns this index; it was modelled on Zorivest's.
> Implement with a typed `CommandRegistryEntry` (`id`, `label`, `category`, `keywords`, `action`, optional `shortcut`).
> **Palette-eligible** ≠ **all actions**. Local table buttons stay in this index (testid + REST) even when they are not in Ctrl+K. Eligible rows are listed per page and state (06 §Command palette curation).

| `id` | Trigger | Palette | REST / IPC | Status | Owner |
|------|---------|---------|------------|--------|-------|
| `nav:downloader` | Nav rail / Ctrl+1 | yes | route `/` | specified | [06-gui.md](06-gui.md) |
| `nav:transcript` | Nav rail / Ctrl+2 | yes | route `/transcript` | specified | 06-gui |
| `nav:tts` | Nav rail / Ctrl+3 | yes | route `/tts` | specified | 06-gui |
| `nav:convert` | Nav rail / Ctrl+4 | yes | route `/convert` | specified | [08-video-conversion.md](08-video-conversion.md) |
| `nav:capture` | Nav rail / Ctrl+5 | yes | route `/capture` | specified | [09-screenshot-capture.md](09-screenshot-capture.md) |
| `nav:settings` | Nav rail / Ctrl+, | yes | route `/settings` | specified | 06-gui |
| `nav:collapse` | Rail / Ctrl+B | yes | `ui.rail.collapsed` | specified | 06-gui |
| `palette:open` | Ctrl+K | no | CommandPalette | specified | 06-gui |
| `download:add` | Add button / Ctrl+L | yes | `POST /downloads` | specified | 04 / 06 |
| `download:start` | Start | yes | `POST /downloads/start` | specified | 04 / 06 |
| `download:pause` | Pause | yes | `POST /downloads/pause` | specified | 04 / 06 |
| `download:resume` | Resume | yes | `POST /downloads/resume` | specified | 04 / 06 |
| `download:cancel` | Cancel | yes | `POST /downloads/cancel` | specified | 04 / 06 |
| `download:clear` | Clear queue | yes | `DELETE /downloads` | specified | 04 / 06 |
| `download:remove` | Row delete | no | `DELETE /downloads/{id}` | specified | 04 / 06 |
| `download:reset` | Reset failed | no | `POST /downloads/{id}/reset` | specified | 04 / 06 |
| `download:reorder` | Drag row | no | `PUT /downloads/reorder` | specified | 04 / 06 |
| `download:sabr_check` | Check SABR | yes | `POST /downloads/sabr/check` | specified | 04 / 06 |
| `download:sabr_force` | Force SABR | no | `POST /downloads/sabr/force` | specified | 04 / 06 |
| `download:sabr_clear` | Clear SABR | no | `POST /downloads/sabr/clear` | specified | 04 / 06 |
| `download:cookies_test` | Test cookies | no | `POST /downloads/cookies/test` | specified | 04 / 06 |
| `download:open_file` | Row open | no | IPC `openPath` | specified | 06 IPC |
| `download:open_folder` | Row folder | no | IPC `showItemInFolder` | specified | 06 IPC |
| `download:apply_quality_pending` | Settings “Apply to pending” | no | `POST /downloads/apply-defaults` | specified | 03 / 04 / 06 |
| `download:browse_path` | Download path Browse | no | IPC `showDirectoryDialog` | specified | 06 |
| `transcript:add` | Add channel / Ctrl+L | yes | `POST /transcripts` | specified | 04 / 06 |
| `transcript:start` | Start | yes | `POST /transcripts/start` | specified | 04 / 06 |
| `transcript:pause` | Pause | yes | `POST /transcripts/pause` | specified | 04 / 06 |
| `transcript:resume` | Resume | yes | `POST /transcripts/resume` | specified | 04 / 06 |
| `transcript:stop` | Stop | yes | `POST /transcripts/stop` | specified | 03 / 04 / 06 |
| `transcript:requeue` | Requeue cancelled | no | `POST /transcripts/{id}/requeue` | specified | 03 / 04 / 06 |
| `transcript:retry` | Retry failed | no | `POST /transcripts/{id}/retry` | specified | 03 / 04 / 06 |
| `transcript:reorder` | Card drag / up-down | no | `PUT /transcripts/reorder` | specified | 04 / 06 |
| `transcript:compile` | Compile | no | `POST /transcripts/{id}/compile` | specified | 04 / 06 |
| `transcript:remove` | Remove | no | `DELETE /transcripts/{id}` | specified | 04 / 06 |
| `transcript:open_compiled` | View compiled | no | IPC `openPath` | specified | 06 IPC |
| `transcript:open_zip` | Open ZIP | no | IPC `openPath` | specified | 06 IPC |
| `transcript:open_folder` | Open folder | no | IPC `openPath` | specified | 06 IPC |
| `tts:load_file` | Load file | no | IPC `readTextFile` | specified | 06 IPC |
| `tts:browse_output` | Generate-bar output Path picker | no | IPC `showDirectoryDialog` + `tts.output_path` | specified | 06 |
| `tts:paste` | Paste | no | IPC `readClipboardText` | specified | 06 IPC |
| `tts:prepare` | Preview cleaned | yes | `POST /tts/prepare` | specified | 04 / 06 |
| `tts:generate` | Generate | yes | `POST /tts/generate` | specified | 04 / 06 |
| `tts:cancel` | Cancel generate | no | `DELETE /tts/{id}` | specified | 04 / 06 |
| `tts:open_output` | Open file | no | IPC `openPath` | specified | 06 IPC |
| `tts:open_output_folder` | Open folder | no | IPC `showItemInFolder` | specified | 06 IPC |
| `convert:add` | Add | yes | `POST /conversions` | specified | 08 |
| `convert:start` | Start | yes | `POST /conversions/start` | specified | 08 |
| `convert:pause` | Pause | yes | `POST /conversions/pause` | specified | 08 |
| `convert:resume` | Resume | yes | `POST /conversions/resume` | specified | 08 |
| `convert:cancel` | Cancel | yes | `POST /conversions/cancel` | specified | 08 |
| `convert:clear` | Clear queue | yes | `DELETE /conversions` | specified | 08 |
| `convert:remove` | Row delete | no | `DELETE /conversions/{id}` | specified | 08 |
| `convert:reset` | Reset failed | no | `POST /conversions/{id}/reset` | specified | 08 |
| `convert:reorder` | Drag / up-down | no | `PUT /conversions/reorder` | specified | 08 |
| `convert:browse` | Browse files / Ctrl+O | yes | IPC `showOpenDialog` multi | specified | 08 |
| `convert:drop` | Drop files | no | preload paths → `POST /conversions` | specified | 08 |
| `convert:open_file` | Row open | no | IPC `openPath` | specified | 08 |
| `convert:open_folder` | Row folder | no | IPC `showItemInFolder` | specified | 08 |
| `convert:gpu_refresh` | Refresh GPU chip | no | `POST /conversions/gpu/refresh` | specified | 08 |
| `convert:browse_output_dir` | Output folder Browse | no | IPC `showDirectoryDialog` + `converter.output_dir` | specified | 08 / 06 |
| `capture:region` | Capture region / F2 | yes | IPC `capture-region` then `POST /captures` | specified | 09 |
| `capture:save` | Save annotated / Ctrl+S | yes | `POST /captures/{id}/annotate` | specified | 09 |
| `capture:open_file` | Open file | no | IPC `openPath` | specified | 09 / 06 IPC |
| `capture:open_folder` | Open folder | yes | IPC `showItemInFolder` | specified | 09 / 06 IPC |
| `capture:delete` | Delete shot | no | `DELETE /captures/{id}` | specified | 09 |
| `capture:copy_path` | Copy full path (thumbnail menu) | no | IPC `writeClipboardText` | specified | 09 |
| `capture:copy_image` | Copy image (thumbnail menu) | no | IPC `writeClipboardImage` | specified | 09 |
| `capture:menu_delete` | Delete (thumbnail menu) | no | `DELETE /captures/{id}` | specified | 09 |
| `capture:batch_delete` | Delete {n} shots (thumbnail menu, ticked shots or Shift-click range) | no | `DELETE /captures/{id}` per shot | specified | 09 |
| `capture:apply_image` | Apply to image (bake saved marks after a backup) | no | `POST /captures/{id}/flatten` | specified | 09 |
| `capture:revert_image` | Revert image from its newest backup | no | `POST /captures/{id}/revert` | specified | 09 |
| `capture:tool_arrow` | Arrow tool | no | local canvas | specified | 09 |
| `capture:tool_box` | Box tool | no | local canvas | specified | 09 |
| `capture:tool_highlight` | Highlight tool | no | local canvas | specified | 09 |
| `capture:tool_text` | Text tool | no | local canvas | specified | 09 |
| `capture:tool_pixelate` | Pixelate tool | no | local canvas | specified | 09 |
| `capture:tool_eraser` | Eraser tool | no | local canvas | specified | 09 |
| `capture:tool_lock` | Keep tool after drawing (tool lock) | no | local canvas | specified | 09 |
| `capture:undo` | Undo overlay; Ctrl+Z on the image | no | local | specified | 09 |
| `capture:redo` | Redo overlay; Ctrl+Y or Ctrl+Shift+Z on the image | no | local | specified | 09 |
| `capture:zoom_in` | Zoom in (button / Ctrl+= / wheel) | no | local view | specified | 09 |
| `capture:zoom_out` | Zoom out (button / Ctrl+- / wheel) | no | local view | specified | 09 |
| `capture:zoom_fit` | Fit to view (button / Ctrl+0) | no | local view | specified | 09 |
| `settings:browse_capture_dir` | Capture Inbox Browse | no | IPC `showDirectoryDialog` + `capture.inbox_dir` | specified | 09 / 06 |
| `settings:browse_capture_backup_dir` | Capture Backup folder Browse | no | IPC `showDirectoryDialog` + `capture.backup_dir` | specified | 09 / 06 |
| `models:download` | Get model | no | `POST /models/download` | specified | 04 / 06 |
| `models:load` | Load | no | `POST /models/load` | specified | 04 / 06 |
| `models:unload` | Unload | no | `POST /models/unload` | specified | 04 / 06 |
| `settings:save` | Auto on change | no | `PUT /settings/{namespace}` | specified | 04 / 06 |
| `settings:check_deps` | Check dependencies | yes | `GET /health/dependencies` | specified | 04 / 06 |
| `appearance:dark` | Appearance: Dark / Ctrl+Shift+D | yes | `PUT /settings/{namespace}` | specified | 06 |
| `appearance:light` | Appearance: Light / Ctrl+Shift+L | yes | `PUT /settings/{namespace}` | specified | 06 |
| `settings:copy_mcp` | Copy MCP config | no | IPC `copyMcpConfig` (no token to renderer) | specified | 06 / 07 |
| `settings:pin_mcp` | Pin current endpoint | no | `copyMcpConfig({ pinEndpoint: true })` | specified | 06 / 07 |
| `settings:copy_mcp_prompt` | Copy prompt | no | IPC `getMcpSetupPrompt` + `writeClipboardText` (no token) | specified | 07 / 06 |
| `settings:ffmpeg_browse` | FFmpeg path Browse | no | IPC `showFileDialog` + `downloader.ffmpeg_path` | specified | 06 / 07 |
| `settings:browse_cookie_file` | Cookie File Path Browse | no | IPC `showFileDialog` + `downloader.cookie_file_path` | specified | 06 |
| `settings:browse_transcript_dir` | Transcript Output Directory Browse | no | IPC `showDirectoryDialog` + `transcript.output_dir` | specified | 06 |
| `settings:browse_models_dir` | Models Directory Browse | no | IPC `showDirectoryDialog` + `tts.models_directory` | specified | 06 |
| `settings:browse_convert_dir` | Convert Output Directory Browse | no | IPC `showDirectoryDialog` + `converter.output_dir` | specified | 08 / 06 |
| `settings:login_item` | Start av-kit when I sign in | no | IPC `login-item-set` | specified | 06 / 07 |
| `settings:start_minimized` | Start minimized (login item) | no | IPC `login-item-set` | specified | 06 / 07 |
| `settings:copy_espeak_link` | Copy link | no | IPC `writeClipboardText` | specified | 06 |
| `settings:copy_log_path` | Copy path | no | IPC `writeClipboardText` | specified | 06 |
| `console:filter` | Exclusive level buttons: the level and above | no | local | specified | 06 |
| `console:search` | Search | no | local | specified | 06 |
| `console:clear` | Clear view | no | local | specified | 06 |
| `console:copy` | Copy lines | no | IPC `writeClipboardText` | specified | 06 |
| `console:toggle` | Header Console / palette / Ctrl+J | yes | `av-kit:toggle-console` | specified | 06 |
| `console:expand` | Expand / restore width | no | `ui.panel.console.expanded` | specified | 06 |
| `console:close` | Close X | no | `ui.panel.console.visible` | specified | 06 |
| `console:collapse` | Side-sheet collapse | no | `ui.panel.console.expanded` | specified | 06 |
| `help:toggle` | Per-page HelpCard / F1 | yes | local content module | specified | 06 |
| `page:primary` | Ctrl+Enter | no | local (clicks the page's enabled primary button) | specified | 06 |

Every row needs a `data-testid` (central `ui/tests/e2e/test-ids.ts` or feature-local file). Interactive-element rule (Zorivest AC-38): a page is incomplete if a button/input has no testid.

**Bidirectional audit (Phase 6 gate):** (1) every `Palette = yes` id is registered; (2) every Phase 6 button/control has a row here; (3) every REST/IPC cell exists in Phase 4 or the preload allowlist. A row that points at a service method with no route is a defect.
