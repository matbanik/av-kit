# MCP Tool Audit Report

| Field | Value |
|---|---|
| Date | 2026-11-09T15:32:32.939Z |
| Agent | claude-code |
| Mode | authoritative |
| Backend version | 0.1.0rc2 |
| Commit | 8ce8b956067b7edc034818d081bbf678460f1ef6 |
| Server | P:\av-kit\mcp-server\dist\index.js |
| Tools / actions | 8 / 70 |
| Exit code | 0 |

Consolidation score: n/a (8 compound tools; consolidation already done, D-10).

## Scorecard

| Tool | Steps | Pass | Fail | Skip (env) | Blocked |
|---|---|---|---|---|---|
| avkit_download | 24 | 24 | 0 | 0 | 0 |
| avkit_transcript | 19 | 19 | 0 | 0 | 0 |
| avkit_tts | 5 | 5 | 0 | 0 | 0 |
| avkit_models | 11 | 11 | 0 | 0 | 0 |
| avkit_settings | 7 | 7 | 0 | 0 | 0 |
| avkit_health | 2 | 2 | 0 | 0 | 0 |
| avkit_convert | 19 | 19 | 0 | 0 | 0 |
| avkit_capture | 12 | 12 | 0 | 0 | 0 |

Totals: 99 pass, 0 fail, 0 skip_env, 0 blocked of 99.

## Lifecycle matrix

| Step | Tool.action | Verdict | Observable |
|---|---|---|---|
| settings.get | avkit_settings.get | pass | MCP == REST for 7 namespaces |
| settings.set | avkit_settings.set | pass | 7 leaves persisted per REST |
| settings.set.restore | avkit_settings.set | pass | 7 leaves restored per REST |
| models.available | avkit_models.available | pass | MCP == REST /models/available |
| models.downloaded.before | avkit_models.downloaded | pass | MCP == REST /models/downloaded |
| models.download | avkit_models.download | pass | REST downloaded kokoro-onnx-int8; model_quantized.onnx 92361116 B |
| models.downloaded.after | avkit_models.downloaded | pass | MCP == REST /models/downloaded |
| models.download_asset.vocab | avkit_models.download_asset | pass | tts_onnx_vocab already ready: 409 contract true; state after ready |
| models.download_asset.spacy | avkit_models.download_asset | pass | REST /health/dependencies tts_spacy_model: missing -> ready |
| models.load | avkit_models.load | pass | REST status is_loaded=true variant=kokoro-onnx-int8 |
| models.status | avkit_models.status | pass | MCP == REST /models/status |
| tts.voices | avkit_tts.voices | pass | MCP == REST /tts/voices ids=54 |
| tts.prepare | avkit_tts.prepare | pass | prepare cleaned_text 28 chars; REST 200 |
| tts.generate | avkit_tts.generate | pass | job Done; 3dbb3dfb-ce65-42bd-9ea0-cd6213b66d54.mp3 45644 B; audio header ok |
| tts.get | avkit_tts.get | pass | MCP == REST /tts/3dbb3dfb-ce65-42bd-9ea0-cd6213b66d54 |
| tts.cancel | avkit_tts.cancel | pass | attempt 1/3; before=false after=true |
| models.unload | avkit_models.unload | pass | REST status is_loaded=false |
| models.status.after | avkit_models.status | pass | MCP == REST /models/status |
| download.list.empty | avkit_download.list | pass | MCP == REST /downloads ids=0 |
| download.setup | avkit_settings.set | pass | REST /settings/downloader == {"quality":"lowest"} |
| download.add.a | avkit_download.add | pass | REST /downloads/5220fd30-442e-473e-95b4-605f6374a478 -> 200 Pending |
| download.add.b | avkit_download.add | pass | REST /downloads/f40a99b0-463a-4e0f-b815-2f8cf794ca2a -> 200 Pending |
| download.add.c | avkit_download.add | pass | REST /downloads/38bef64d-7def-4ae0-ae38-7b00821ff0ee -> 200 Pending |
| download.apply_defaults | avkit_download.apply_defaults | pass | updated=3; REST qualities lowest,lowest,lowest |
| download.reorder | avkit_download.reorder | pass | REST order 38bef64d,5220fd30,f40a99b0 |
| download.list | avkit_download.list | pass | MCP == REST /downloads ids=3 |
| download.get | avkit_download.get | pass | MCP == REST /downloads/5220fd30-442e-473e-95b4-605f6374a478 |
| download.start | avkit_download.start | pass | REST c Downloading |
| download.cancel | avkit_download.cancel | pass | REST c Cancelled, processor Idle |
| download.reset | avkit_download.reset | pass | REST c Pending |
| download.reorder.back | avkit_download.reorder | pass | REST order 5220fd30,38bef64d,f40a99b0 |
| download.start.again | avkit_download.start | pass | REST a Downloading |
| download.pause | avkit_download.pause | pass | REST processor Paused |
| download.resume | avkit_download.resume | pass | REST processor Processing |
| download.stop | avkit_download.stop | pass | REST processor Idle |
| download.get.done | avkit_download.get | pass | REST a Done; Me at the zoo.mp4 629172 B |
| download.remove | avkit_download.remove | pass | before=200 after=404 |
| download.clear | avkit_download.clear | pass | before=2 after=0 |
| download.setup.restore | avkit_settings.set | pass | REST /settings/downloader == {"quality":"1080p"} |
| transcript.list.empty | avkit_transcript.list | pass | MCP == REST /transcripts ids=0 |
| transcript.setup | avkit_settings.set | pass | REST /settings/transcript == {"delay_between_requests":3,"max_retries":0} |
| transcript.add | avkit_transcript.add | pass | REST job Pending video_count=9 output_dir in root=true |
| transcript.list | avkit_transcript.list | pass | MCP == REST /transcripts ids=1 |
| transcript.get | avkit_transcript.get | pass | MCP == REST /transcripts/61417ab3-bd59-4e04-bb78-5db1f0f3a83d |
| transcript.reorder | avkit_transcript.reorder | pass | REST order 1 job(s) |
| transcript.start | avkit_transcript.start | pass | REST job Processing (want Processing) |
| transcript.pause | avkit_transcript.pause | pass | REST job Paused (want Paused) |
| transcript.resume | avkit_transcript.resume | pass | REST job Processing (want Processing), transcripts_done 1, last_item_status Done |
| transcript.pause.again | avkit_transcript.pause | pass | REST job Paused (want Paused) |
| transcript.stop | avkit_transcript.stop | pass | REST job Cancelled (want Cancelled) |
| transcript.requeue | avkit_transcript.requeue | pass | REST job Pending |
| transcript.requeue.conflict | avkit_transcript.requeue | pass | 409 contract: ConflictError: illegal transcript transition Pending -> Pending; REST job Pending |
| transcript.retry.conflict | avkit_transcript.retry | pass | 409 contract: ConflictError: illegal transcript transition Pending -> Pending; REST job Pending |
| transcript.start.again | avkit_transcript.start | pass | REST job Processing (want Processing) |
| transcript.pause.third | avkit_transcript.pause | pass | REST job Paused (want Paused) |
| transcript.stop.again | avkit_transcript.stop | pass | REST job Cancelled (want Cancelled) |
| transcript.retry | avkit_transcript.retry | pass | REST job Pending |
| transcript.compile | avkit_transcript.compile | pass | live-rigging-snow_vol1.md 112778 B; 1 section(s), transcripts_done 1 |
| transcript.remove | avkit_transcript.remove | pass | before=200 after=404 |
| transcript.setup.restore | avkit_settings.set | pass | REST /settings/transcript == {"delay_between_requests":6,"max_retries":3} |
| convert.list.empty | avkit_convert.list | pass | MCP == REST /conversions ids=0 |
| convert.add.long1 | avkit_convert.add | pass | REST Pending output in root=true |
| convert.add.short | avkit_convert.add | pass | REST Pending output in root=true |
| convert.add.long2 | avkit_convert.add | pass | REST Pending output in root=true |
| convert.list | avkit_convert.list | pass | MCP == REST /conversions ids=3 |
| convert.get | avkit_convert.get | pass | MCP == REST /conversions/3da9fcae-99b1-41a8-82c3-1f4e3bab5a10 |
| convert.start | avkit_convert.start | pass | long1 Processing; processor Processing |
| convert.cancel | avkit_convert.cancel | pass | long1 Cancelled; processor Idle |
| convert.reset | avkit_convert.reset | pass | REST long1 Pending |
| convert.reorder | avkit_convert.reorder | pass | REST order matches=true |
| convert.start.again | avkit_convert.start | pass | short started; processor Processing |
| convert.pause | avkit_convert.pause | pass | processor Paused; processor Paused |
| convert.resume | avkit_convert.resume | pass | processor Processing; processor Processing |
| convert.cancel.again | avkit_convert.cancel | pass | a job Cancelled, processor Idle; processor Idle |
| convert.get.done | avkit_convert.get | pass | REST short Done; short_compress.mp4 54223 B |
| convert.remove | avkit_convert.remove | pass | before=200 after=404 |
| convert.clear | avkit_convert.clear | pass | before=2 after=0 |
| capture.list.empty | avkit_capture.list | pass | MCP == REST /captures ids=0 |
| capture.capture | avkit_capture.capture | pass | REST shot 200; 2026-11-09_15-32-27.png 2525318 B |
| capture.list | avkit_capture.list | pass | MCP == REST /captures ids=1 |
| capture.get | avkit_capture.get | pass | MCP == REST /captures/28a573e1-3f67-40ac-8a59-b371b72ba007 |
| capture.image | avkit_capture.image | pass | MCP image 2525318 B == REST 2525318 B: true; PNG true |
| capture.annotate | avkit_capture.annotate | pass | annotated 2026-11-09_15-32-27.annotated.png 2525376 B; sidecar 2026-11-09_15-32-27.ann.json 131 B |
| capture.image.annotated | avkit_capture.image | pass | annotated MCP 2525376 B == REST: true |
| capture.flatten | avkit_capture.flatten | pass | before={"status":200,"original_sha256":"d396b9ea23e3969498186bda6f01643d944c5794a4edb8d6fa3de7b264586385","annotated_exists":true,"backup_count":0} after={"status":200,"original_sha256":"68140407db553f824aa3c4633dffcc138b9aac5525e66a2c75fef4b580736d1b","annotated_exists":false,"backup_count":1} |
| capture.revert | avkit_capture.revert | pass | before={"status":200,"original_sha256":"68140407db553f824aa3c4633dffcc138b9aac5525e66a2c75fef4b580736d1b"} after={"status":200,"original_sha256":"d396b9ea23e3969498186bda6f01643d944c5794a4edb8d6fa3de7b264586385"} |
| capture.capture_interactive | avkit_capture.capture_interactive | pass | REST pending requests include 18d4f75d-ee51-4038-b687-30a90464a6a4: true |
| capture.list_requests | avkit_capture.list_requests | pass | MCP == REST /captures/requests?status=pending ids=1 |
| capture.remove | avkit_capture.remove | pass | before={"status":200,"present":1} after={"status":404,"present":0} |

## Functional results

| Step | Tool.action | Status | Error | Notes |
|---|---|---|---|---|
| health.liveness | avkit_health.liveness | pass |  | REST /health -> 200 {"status":"ok"} |
| health.dependencies | avkit_health.dependencies | pass |  | MCP == REST /health/dependencies |
| models.download_runtime | avkit_models.download_runtime | pass |  | MCP == REST /models/download-runtime |
| download.sabr_get | avkit_download.sabr_get | pass |  | MCP == REST /downloads/sabr |
| download.cookies_test | avkit_download.cookies_test | pass |  | MCP ok=true REST ok=true |
| download.sabr_force | avkit_download.sabr_force | pass |  | REST sabr active/forced |
| download.sabr_check | avkit_download.sabr_check | pass |  | REST sabr inactive checked_at=2026-11-09T15:31:55.501802+00:00 |
| download.sabr_clear | avkit_download.sabr_clear | pass |  | REST sabr inactive |
| convert.gpu | avkit_convert.gpu | pass |  | MCP == REST /conversions/gpu |
| convert.gpu_refresh | avkit_convert.gpu_refresh | pass |  | REST checked_at=2026-11-09T15:32:24.066787+00:00 |

## Issues log

None.

## Discovery findings

None.

## Regression delta

No change against the baseline.

## Cleanup

| ok | backend exited | root removed | residuals |
|---|---|---|---|
| true | true | true | none |

## Isolation

| Setting | Path |
|---|---|
| downloader.path | C:\Temp\av-kit\s57\tmp\avkit-mcp-audit-BxR872\out\downloads |
| transcript.output_dir | C:\Temp\av-kit\s57\tmp\avkit-mcp-audit-BxR872\out\transcripts |
| tts.models_directory | C:\Temp\av-kit\s57\tmp\avkit-mcp-audit-BxR872\out\models |
| tts.output_path | C:\Temp\av-kit\s57\tmp\avkit-mcp-audit-BxR872\out\tts |
| converter.output_dir | C:\Temp\av-kit\s57\tmp\avkit-mcp-audit-BxR872\out\convert |
| capture.inbox_dir | C:\Temp\av-kit\s57\tmp\avkit-mcp-audit-BxR872\out\captures |
| capture.backup_dir | C:\Temp\av-kit\s57\tmp\avkit-mcp-audit-BxR872\out\capture_backups |

