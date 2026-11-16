# Mat's look at the TTS status pill (MEU-149, row 5, D-806, M-10)

decision: approve
human_message_reference: USER_EXPLICIT 2026-11-16 'approved'

Mat gave this answer by choosing the option "approved" in an AskUserQuestion prompt on 2026-11-16. The other option was "Not yet checked", and he could also type his own text. His words are quoted above, verbatim.

## What Mat was asked

After row 4's Green, the executor launched the dev app detached (`implementation-plan.md` §Verification Plan 3). The coordinator relayed the plan's request to Mat verbatim:

> The TTS page's status pill is now a tinted chip. Please look at it in the dev app that just opened, in both themes:
>
> 1. Open TTS. With a model loaded, the pill reads **Idle**.
> 2. Type a sentence or two and press **Generate**. While it runs, the pill reads **Generating** and the bar shows a percentage, such as `25%`, instead of `Segments 250/1000`.
> 3. When it finishes, the pill reads **Done**. If you press **Cancel** during a run instead, it reads **Cancelled**.
> 4. Switch theme in **Settings** (Light, or Ctrl+Shift+L), and repeat steps 1 to 3 in the other theme.
> 5. Quit the app from the tray.
>
> Is each pill easy to read in both themes? Say "approved", or tell me what to change.

The coordinator added the line the task row names: in the light theme the chip's 10% tint is faint by design (about rgb 223,231,237 on the f5f6fa page for Generating), and the word carries the status, so Mat judges whether it is too faint (D-956).

## The launch

- `dev-app-procs.py record` recorded 14 processes under the launched pwsh (pid 50952), the Electron and backend roles among them (`C:/Temp/av-kit/tts-page-polish/tpp-dev-app-record.txt`, record `C:/Temp/av-kit/tts-page-polish/dev-app-launch.json`). The app's log ends `starting electron app...` with the renderer on 127.0.0.1:5173 (`C:/Temp/av-kit/tts-page-polish/tpp-dev-app.txt`).
- The app was still open after Mat's answer: `check` listed 14 of this launch's processes and 0 others (`C:/Temp/av-kit/tts-page-polish/tpp-dev-app-precheck.txt`, exit 1).
- `check --stop` ended this launch's processes by id and then listed 0 of this launch's and 0 others (`C:/Temp/av-kit/tts-page-polish/tpp-dev-app-stop.txt`, exit 0). It printed `stopped` for the first four processes in its list (50952, 67844, 70248, 71364). It checks each process again before ending it, and the other ten had already exited by their turn, after their parents ended. No process outside this launch was touched, and the avkit MCP servers were never counted.
- The row's own `check` then ran into `C:/Temp/av-kit/tts-page-polish/tpp-dev-app-check.txt`.
