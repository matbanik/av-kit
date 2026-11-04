# Keeping dependencies up to date

Updates are made by hand on `main` and tested locally before they're pushed. GitHub only
tells us what needs attention: Dependabot alerts are on, Dependabot pull requests are off,
and there is no `.github/dependabot.yml`.

## What runs on its own

- **Dependabot alerts:** in the repository's Security tab, visible to maintainers only.
- **Weekly report:** `.github/workflows/deps-check.yml` runs every Monday and replaces the
  body of one open issue labelled `dependency-report`. It lists known vulnerabilities in
  what ships, updates available, and whether the pinned FFmpeg URL still works. It changes
  nothing. If a scanner fails, the run goes red and the issue says which one.

GitHub turns off scheduled workflows after 60 days with no repository activity. If the
report stops updating, re-enable it on the workflow's Actions page.

You can run the same report locally:

```powershell
uv run python tools/deps_report.py --out report.md
```

## Monthly update

Do one batch a month, as one commit on `main`:

1. Update the Python packages:

   ```powershell
   uv lock --upgrade
   uv sync --all-packages
   ```

2. Update the npm packages in `ui` and in `mcp-server`. Move across a major version one
   package at a time, and read its release notes first:

   ```powershell
   npm update
   npm audit
   ```

3. Run the checks in [.agent/docs/commands.md](../../.agent/docs/commands.md), including the
   Electron suite that CI doesn't run.
4. Commit and push `main`. CI then repeats the checks on a clean machine.

Electron is a dev dependency, but it ships with the app. Treat its advisories as shipped
even though `npm audit --omit=dev` can't see them.

## The 7-day hold

New releases wait 7 days before they can be installed, which gives the registries time to
pull a bad or malicious release. The setting is `exclude-newer` in `pyproject.toml` and
`min-release-age` in `ui/.npmrc` and `mcp-server/.npmrc`.

**yt-dlp can skip the hold.** YouTube changes can break downloads overnight, and the fix is
usually a new yt-dlp. When that happens, add this line under `[tool.uv]` in `pyproject.toml`:

```toml
exclude-newer-package = { yt-dlp = false }
```

Then update only that package:

```powershell
uv lock --upgrade-package yt-dlp
```

Don't pass the override on the command line instead: `uv lock --check` then fails in CI,
because the lockfile no longer matches `pyproject.toml`. Remove the line and run `uv lock`
again once that release is more than 7 days old.

## Pinned tools

Change these on purpose, not as part of a routine update:

| Tool | Pinned in |
|---|---|
| Python | `.python-version` |
| Node | `.node-version` |
| .NET SDK | `global.json` |
| uv | `version:` in `.github/workflows/*.yml`, with a minimum in `pyproject.toml` |
| GitHub Actions | Full commit hash in `.github/workflows/*.yml` |
