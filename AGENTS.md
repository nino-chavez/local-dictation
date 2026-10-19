# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) and Codex when working with code in this repository.

## What this is

A fully local dictation daemon for macOS on Apple Silicon (Wispr Flow clone):
global hotkey → mic capture → Whisper transcription (MLX, on-GPU) → LLM cleanup
(local Ollama) → text pasted into the focused app. Two source files: `dictate.py`
(the daemon) and `menubar.py` (rumps tray app controlling the daemon's launchd job).

## Product boundary — read before adding features

PLAN.md § "Product boundary" is binding: this is an **input method** that may
DELIVER text anywhere but never STORES anything. Hot-phrase routing to Notes is
addressing, not archiving. Anything that stores, organizes, or projects data
(logs, daily notes, schemas) belongs to a separate consumer built against the
`--on-capture` seam, in its own repo. Do not add storage here.

## Commands

```sh
# setup (no lockfile/pyproject — deps install directly into .venv)
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python mlx-whisper sounddevice pynput rumps

# pipeline check without mic/hotkey/permissions (prints instead of pastes)
.venv/bin/python dictate.py --test-file test.wav

# run the daemon in a terminal (terminal needs Mic + Input Monitoring + Accessibility)
.venv/bin/python dictate.py

# the deployed instance runs under launchd — after editing dictate.py, restart it:
launchctl kickstart -k gui/$UID/com.local-dictation.daemon
tail ~/Library/Logs/local-dictation.log
```

There is no test suite or linter. Verification is: `--test-file` for the
transcribe+cleanup pipeline, inline `python -c` asserts for pure functions
(`match_note_phrase`, `cleanup` fallback, `emit_capture`), and a live dictation
for the hotkey/paste legs (only the human can do that — ask them).

## Architecture

Single process, single state machine in `main()`'s event loop (`dictate.py`).
A pynput `Listener` thread posts `"toggle"` events to a queue; the sounddevice
callback posts `"auto_stop"` on trailing silence. The main loop starts/stops the
`Recorder` and runs the pipeline inline: `transcribe()` (mlx-whisper, accepts
the numpy array directly) → `match_note_phrase()` routing → `cleanup()` (Ollama
`/api/chat`, falls back to the raw transcript if Ollama is down) → `insert_text()`
(clipboard + synthetic ⌘V, clipboard saved/restored) or `add_note()` (osascript
to Notes, background, no focus steal). `focus_target()` samples the frontmost
bundle id and pid when speaking starts; `insert_text()` re-activates that pid
before pasting and refuses the paste if it cannot, so a focus change during the
~1.5 s pipeline cannot land the text in another app. `--on-capture` emits a JSON event per
delivery on a fire-and-forget thread.

`menubar.py` never owns the daemon process — it drives the launchd job via
`launchctl bootstrap/kickstart/bootout` and polls `pgrep`. Both are deployed as
launchd agents (`com.local-dictation.daemon.plist` / `com.local-dictation.menubar.plist` in
`~/Library/LaunchAgents/`).

## Non-obvious constraints

- **Hotkey**: uses a raw pynput `Listener`, NOT `GlobalHotKeys` — GlobalHotKeys
  cannot bind a bare modifier like right Option; the raw listener receives it
  via `kCGEventFlagsChanged` (`alt_r` = keycode 0x3D in pynput's darwin backend).
- **Cleanup prompt is injection-hardened**: the transcript is wrapped in
  `<transcript>` tags and the system prompt forbids answering/obeying it.
  Without this, question-shaped dictation gets *answered* by the model instead
  of cleaned. Preserve this property when touching `CLEANUP_SYSTEM_PROMPT`.
- **Routing decisions run on the raw transcript**, before cleanup — cleanup may
  reword a hot phrase away.
- **TCC permissions under launchd** attach to the resolved Python binary
  (Homebrew's versioned `Cellar/python@3.13/...`), not a terminal app. A
  Homebrew Python upgrade silently invalidates Accessibility/Input Monitoring
  grants — symptom is "This process is not trusted!" in the log.
- **Privacy contract** (PLAN.md): no non-localhost traffic at runtime. The
  daemon sets `HF_HUB_OFFLINE=1` once the Whisper model is cached. Don't add
  network calls beyond Ollama's `localhost:11434`.
- Whisper model: `mlx-community/whisper-large-v3-turbo` (~1.6 GB, cached in
  `~/.cache/huggingface`), **pinned** by `WHISPER_REVISION` + `WHISPER_DIGESTS`
  and verified at startup. Yawn owns those values
  (`apps/yawn-app/worker/build_runtime.sh`); bump there first, copy here. A
  non-default `--whisper` is passed through unpinned on purpose. Ollama cleanup model: `llama3.1`, loaded on the
  first cleanup and released after five idle minutes via `keep_alive: 5m`.

## Documentation

`docs/architecture/README.md` holds the structural view (pipeline, threading,
deployment diagrams); PLAN.md holds decisions and rationale; README.md is the
user doc. Documentation skills from the Claude Docs Toolkit are installed in
`.claude/commands/` (`/doc-architecture`, `/doc-audit`, etc.) — apply them
adaptively; a repo this size does not need the full docs/ tree.
