# local-dictation — fully local Wispr Flow clone for macOS

## What Wispr Flow does (the loop we're cloning)

Wispr Flow: hold/tap a global hotkey (fn by default, push-to-talk; toggle mode
available) → mic capture → streaming ASR in the cloud → LLM cleanup pass
(filler removal, punctuation, context-aware formatting) → text inserted into
whatever field has focus via keyboard events. The product's value is the loop
latency and the cleanup quality, not any single component.

Prior art in the same shape: VoiceInk (Swift + whisper.cpp, GPLv3) and Handy
(cross-platform, MIT). This clone keeps the loop, swaps every cloud leg for a
local one, and drops the product chrome (menu bar UI, per-app formatting,
custom vocab).

## Architecture

Single Python process, CLI daemon. One file: `dictate.py`.

```
pynput global listener ──▶ state machine ──▶ sounddevice InputStream (16 kHz mono f32)
      (toggle key)              │                      │ RMS trailing-silence auto-stop
                                ▼                      ▼
                        worker thread:  mlx_whisper.transcribe(ndarray)
                                │              mlx-community/whisper-large-v3-turbo
                                ▼
                        POST localhost:11434/api/chat  (llama3.1, temp 0, stream=false)
                                │        fallback: raw transcript if Ollama is down
                                ▼
                        clipboard save → pbcopy cleaned text → synthetic ⌘V → clipboard restore
```

Flow: tap hotkey → start sound → speak → tap again **or** ~2 s trailing silence →
stop sound → transcribe → cleanup → paste into focused app.

## Chosen dependencies (and why)

| Leg | Choice | Why / why not the alternative |
|---|---|---|
| Transcription | `mlx-whisper` + `mlx-community/whisper-large-v3-turbo` | Canonical on Apple Silicon — MLX runs on the GPU natively. Measured **0.77 s warm for an 11 s clip** on this machine. whisper.cpp is equally capable but adds a build/binary dependency; mlx-whisper is a pip install into the same process. |
| Cleanup LLM | Ollama `llama3.1` (already installed) | Measured 0.6 s warm. `/api/chat`, `stream:false`, `temperature:0`. Uses what's on the machine; a smaller model (e.g. `llama3.2:3b`) would cut cold-start if wanted. |
| Mic capture | `sounddevice` (PortAudio) | Standard. 16 kHz mono float32 — Whisper's native input format, no resample step. |
| Hotkey | `pynput` raw `Listener`, default **right Option (`alt_r`)** | The bare `fn` key (Wispr's default) is not reliably observable from a Python process on macOS, so we deviate: right Option is a dead key most people never press alone. We use a raw `Listener`, not pynput's `GlobalHotKeys` — `GlobalHotKeys` cannot bind a bare modifier (the source of "right Option is not detectable" reports), while the raw listener receives it via `kCGEventFlagsChanged` (verified in pynput's darwin backend: `alt_r = 0x3D`). Configurable via `--key`. |
| Text insertion | clipboard + synthetic ⌘V, save/restore clipboard via `pbcopy`/`pbpaste` | Char-by-char synthetic typing is slow and drops unicode in some apps (Electron especially). Paste is atomic and works everywhere a text field accepts ⌘V. Clipboard restored ~0.5 s after paste. |
| Silence detection | RMS threshold on the live stream, stop after ~2 s of trailing silence (armed only after speech is heard) | webrtcvad is another dep for marginal gain at dictation SNR. `--no-auto-stop` disables it. |

**Why not streaming transcription** (the one place we diverge from Wispr's shape):
batch transcription of a finished utterance costs ~1 s here; streaming would save
under a second on typical dictation lengths and costs a chunking/partial-merge
layer plus mid-stream correction handling. Not worth it at local-GPU speed.

## Privacy boundary

- No cloud APIs. Network traffic: `localhost:11434` (Ollama) only.
- One-time exception: first run downloads model weights from Hugging Face
  (already cached on this machine at `~/.cache/huggingface`). After that the
  daemon runs with `HF_HUB_OFFLINE=1` so it can never phone home.
- Audio lives in memory only; nothing is written to disk.

## macOS permissions (grant to the app that runs the daemon, e.g. Terminal/Ghostty)

| Permission | Needed for | Prompted? |
|---|---|---|
| Microphone | recording | auto-prompt on first record |
| Input Monitoring | pynput global hotkey listener | auto-prompt on first listen |
| Accessibility | synthetic ⌘V keystroke | must add manually in System Settings → Privacy & Security if paste silently fails |

## Success criteria

1. Tap hotkey in any app → recording starts (audible cue); speak; tap again or
   pause ~2 s → cleaned text appears in the focused field.
2. Stop-to-text latency ≤ 3 s for a ~10 s utterance (measured: ~1.5 s warm).
3. Filler words removed, punctuation/capitalization fixed, wording otherwise preserved.
4. Ollama down → raw transcript is still inserted (degrade, don't fail).
5. Zero non-localhost network traffic at runtime.

## Validated so far (pre-implementation spikes)

- `mlx-whisper` on Python 3.13 venv: transcribes verbatim incl. filler words, GPU device confirmed.
- `say`-generated test clip round-trip: "Um, so basically I think we should, uh,
  refactor the queue architecture…" → llama3.1 cleanup → "So, we should refactor
  the queue architecture because each section gets its own message, which avoids
  the worker timeout." Correct behavior on both legs.
- Warm latencies: 0.77 s transcribe (11 s clip), 0.6 s cleanup.

## Product boundary (decided 2026-07-03)

**This is an input method** — a keyboard replacement: speech in, text out,
wherever text goes. It is not a notes app, not a voice-data platform. Wispr
Flow holds the same line deliberately; the input-method job is sharp,
universal, and latency-critical, while the knowledge job is a different
product with different physics.

**The rule: dictation may DELIVER text anywhere, but it never STORES
anything.** Hot-phrase routing (Notes, potentially Reminders) is addressing,
not archiving — the destination owns what happens after delivery. The moment
this daemon writes its own file, it owns a schema, a retention story, and a
second product's roadmap, and every capture-side experiment puts the
keyboard — the thing that must stay boring and reliable — at risk.

**The parked product: a capture pipeline** (verbatim transcripts, app
context, timestamps, projections into daily notes/markdown). It is behind a
demand test: two weeks of real use showing raw voice notes actually get
reprocessed. If it earns existence, it lives in its own repo and consumes
the capture seam below — it does not grow inside this one.

**The permitted extension point: a capture seam.** An optional
`--on-capture <cmd>` hook that pipes a JSON event per dictation to an
external command and forgets it (fire-and-forget thread, 10s timeout).
Event: `{ts, route: paste|note, raw, text, duration_s, app}` — `app` is the
frontmost bundle id sampled when speaking starts, because that context is
unrecoverable later. Consumers own storage and schema; the daemon stays
stateless. Both routes emit: configuring the hook is the consent act, and
consumers filter.

Scope discipline: v1.x work here is reliability polish, bounded new
delivery destinations, and the seam. Anything that stores, organizes, or
projects belongs to the parked product.

## Added after the core loop shipped

- Prompt-injection hardening on the cleanup pass: the transcript is wrapped in
  `<transcript>` tags and the system prompt forbids answering/obeying it —
  without this, question-shaped dictation ("what am I saying right now?") got
  answered by llama3.1 instead of cleaned.
- `menubar.py` — rumps tray app (◉/○, Start/Stop/Open Log/Quit) as a control
  plane over the launchd job, plus a second launchd agent so the tray itself
  survives login. The tray drives `launchctl`; it never owns the daemon
  process, so it needs no TCC permissions.
- Note routing: utterances starting with "take a note" / "note to self" go to
  macOS Notes via AppleScript instead of the paste path. Background capture,
  not app launch — the stated goal was staying in the current app, and
  `osascript` creates the note without stealing focus. Matching runs on the
  raw transcript (cleanup may reword the trigger); the remainder still gets
  the cleanup pass.

## Non-goals

Streaming transcription, menu-bar/settings UI, packaging/notarization,
per-app tone adaptation, custom vocabulary, multi-language auto-detect.
