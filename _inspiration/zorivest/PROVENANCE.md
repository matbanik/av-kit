# Zorivest copies

av-kit's own copies of the Zorivest files its canon cites by path. av-kit never reads
the Zorivest checkout; these files record where a pattern or value came from. Session 31b
amendment A-1 (decisions D-89 to D-91, Mat 2026-10-17) made them.

- Each file is the blob at the named commit, taken with `git show <commit>:<path>`, never
  from a working tree.
- `blob` is the git object id; `git hash-object <file>` in this repository gives the same id.
- `sha256` is over the LF content (the stored blob), so a CRLF checkout still matches.
- `plan_checks.py decouple` (Session 31b) checks both for every row.
- A copy is never edited. To take a newer version, replace the file and its row together.
- Only `globals.css` stays in this repository. The `gui-actions-index.md` and
  `05n-agent-connect.md` copies were removed on 2026-11-03, before the repository went
  public, because Zorivest's source is closed.

| File | Source path | Commit | Date | Blob | sha256 | Bytes |
|------|-------------|--------|------|------|--------|-------|
| `globals.css` | `ui/src/renderer/src/globals.css` | `1f25483294b375a557e1972981be6aa152b1309e` | 2026-10-16 | `746a7093808e859a5e811aa7dfd01e36c4165b6d` | `dabc229aeb9f331c7db5914a6a90d19c64de84601dfc59121c8bbcc4cb26415f` | 14513 |

## Why each copy exists

| File | Cited by | Use |
|------|----------|-----|
| `globals.css` | `ui/tests/unit/queue-canon.test.ts` (AC-41.3 `PILL_TOKEN_SOURCE`); `docs/build-plan/10-queue-card-ui.md` §Status token table | The palette av-kit's queue pills follow. Seeded at `61243baf` (D-90); bumped to `1f254832` (Zorivest MEU-662, the darker light hexes) by Mat's ruling of 2026-10-26, with the eight light pill tokens in `styles.css` |
