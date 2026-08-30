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
                        focus guard (restore captured pid) → clipboard save →
                        pbcopy cleaned text → synthetic ⌘V → clipboard restore
```

Flow: tap hotkey → start sound → speak → tap again **or** ~2 s trailing silence →
stop sound → transcribe → cleanup → paste into focused app.

## Chosen dependencies (and why)

| Leg | Choice | Why / why not the alternative |
|---|---|---|
| Transcription | `mlx-whisper` + `mlx-community/whisper-large-v3-turbo`, pinned to one revision | Canonical on Apple Silicon — MLX runs on the GPU natively. Measured **0.77 s warm for an 11 s clip** on this machine. whisper.cpp is equally capable but adds a build/binary dependency; mlx-whisper is a pip install into the same process. |
| Cleanup LLM | Ollama `llama3.1` (already installed) | Measured 0.6 s warm. `/api/chat`, `stream:false`, `temperature:0`. Uses what's on the machine; a smaller model (e.g. `llama3.2:3b`) would cut cold-start if wanted. |
| Mic capture | `sounddevice` (PortAudio) | Standard. 16 kHz mono float32 — Whisper's native input format, no resample step. |
| Hotkey | `pynput` raw `Listener`, default **right Option (`alt_r`)** | The bare `fn` key (Wispr's default) is not reliably observable from a Python process on macOS, so we deviate: right Option is a dead key most people never press alone. We use a raw `Listener`, not pynput's `GlobalHotKeys` — `GlobalHotKeys` cannot bind a bare modifier (the source of "right Option is not detectable" reports), while the raw listener receives it via `kCGEventFlagsChanged` (verified in pynput's darwin backend: `alt_r = 0x3D`). Configurable via `--key`. |
| Text insertion | clipboard + synthetic ⌘V, save/restore clipboard via `pbcopy`/`pbpaste`, guarded by a focus target | Char-by-char synthetic typing is slow and drops unicode in some apps (Electron especially). Paste is atomic and works everywhere a text field accepts ⌘V. Clipboard restored ~0.5 s after paste. The frontmost pid is sampled when speaking starts and re-activated before pasting: transcribe + cleanup is ~1.5 s, long enough for a notification or a click to move focus, and a paste into the wrong app is silent and unrecoverable. If the pid cannot be brought back, the paste is refused and the error sound plays — the text stays in the log. |
| Silence detection | RMS threshold on the live stream, stop after ~2 s of trailing silence (armed only after speech is heard) | webrtcvad is another dep for marginal gain at dictation SNR. `--no-auto-stop` disables it. |

**Why not streaming transcription** (the one place we diverge from Wispr's shape):
batch transcription of a finished utterance costs ~1 s here; streaming would save
under a second on typical dictation lengths and costs a chunking/partial-merge
layer plus mid-stream correction handling. Not worth it at local-GPU speed.

## Privacy boundary

- No cloud APIs. Network traffic: `localhost:11434` (Ollama) only.
- One-time exception: first run downloads model weights from Hugging Face
  (already cached on this machine at `~/.cache/huggingface`). After that the
  daemon runs with `HF_HUB_OFFLINE=1` so it can never phone home. The download
  names a revision, so a cleared cache refetches the same snapshot rather than
  whatever the repo's main branch has moved to.
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

## Measured latency (2026-08-30, M3 Max)

The spike numbers above are pre-implementation and measure only the two legs
that existed then. This is the whole loop, on the shipped code.

**Start — tap to microphone running: 83 ms median, 92 ms p90** (n=10 warm).
`sd.InputStream(...)` is 45 ms of it and `.start()` 38 ms; `focus_target()` is
0.1 ms and does not register. It cannot clip speech: `play(SOUND_START)` is
fired after `recorder.start()` and through a non-blocking `Popen`, so capture
is already running before the user is told to speak. Cold — the first tap after
the daemon starts — is 194-260 ms across three fresh processes, ~90 ms of it
`import sounddevice`.

One outlier is recorded rather than averaged away: the very first measured
cycle took 36 s. It did not reproduce in any later run and is most plausibly
macOS evaluating the microphone grant for that Python binary in a new exec
context. Not a number to design against; noted so the next person who sees it
knows it has been seen.

**Stop to text — 6.5 s clip, warm:**

| Leg | Median |
|---|---|
| transcribe (mlx-whisper) | 0.40 s (16x realtime) |
| cleanup (Ollama, model resident) | 0.32 s |
| **total** | **0.72 s** |

Against a 3.0 s success criterion, so the loop runs about 4x inside its own
budget. Cold first transcribe is 3.11 s (model load onto the GPU).

**The one real latency cost is the cleanup model going cold.** `keep_alive: 5m`
releases llama3.1 after five idle minutes, and reloading 9 GB onto the GPU costs
**1.71 s against 0.32 s warm — a 1.39 s penalty**, measured by stopping the model
and re-running. So a burst of dictation runs at ~0.72 s stop-to-text and the
first one after a break runs at ~2.1 s. Both pass, but the second is the one
that gets noticed, and it is the common case for intermittent use.

That is the tradeoff the on-demand load bought (commit e4b973a): 9 GB of
resident GPU memory against 1.39 s on the first dictation after a pause. The
third option is the one this file already named and never priced — a smaller
cleanup model such as `llama3.2:3b` — which would shrink both sides at some
cost to cleanup quality, and cleanup quality is half of what the product is.
Unmeasured: no small model is installed on this machine.

### What this settles about the FluidVoice borrows

Three candidates from the 2026-08-30 comparison die here, on measurement:

- **A direct Core Audio input path** (FluidVoice's `DirectCoreAudioInput`,
  built for "faster recording start"). 83 ms is already absorbed before the
  audio cue. There is no clipping to fix.
- **Parakeet as a faster model.** Transcription is 0.40 s of a 0.72 s loop that
  is 4x inside budget. A faster model saves time nobody is waiting on.
- **Re-opening the streaming question.** The rejection above was reasoned at
  Whisper batch speed and the argument was that a faster model might change the
  input. It does not, because the model is not the constraint and there is no
  constraint.

What survives from that comparison is the focus guard, already shipped, and the
shared model pin below.

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

- Focus guard on the paste path (borrowed from FluidVoice's `TypingService`
  behavior, reimplemented — that code is GPLv3 and this is not). The frontmost
  pid is now sampled on every dictation, not only when `--on-capture` is set,
  and `insert_text` re-activates it before pasting. The window it closes is the
  ~1.5 s of transcribe + cleanup, during which a notification or a click can
  move focus; the old code pasted into whatever was in front by then, silently.
  When the captured pid cannot be brought back the paste is refused rather than
  aimed blind — the text is already in the log, so a refusal is recoverable and
  a misdelivery is not. Not borrowed: paste verification via the accessibility
  API. Many apps (terminals, Electron) do not expose `AXValue`, so it needs
  FluidVoice's enum of unverifiable outcomes to avoid crying wolf on exactly
  the apps this daemon is used in.

- Whisper snapshot pinned by revision and digest, shared with Yawn. Both tools
  run `mlx-community/whisper-large-v3-turbo` off the same Hugging Face cache
  entry, but only Yawn pinned it — `mlx_whisper` calls `snapshot_download()`
  with no revision, so this daemon followed the repo's main branch and the two
  would have diverged on the next cache clear with nothing to report it. They
  are on the same bytes today by coincidence of download date, which is not a
  mechanism. Yawn stays the owner of the three values because its build fails
  on a mismatch and it ships the model in a DMG; this repo copies them and
  checks on startup. The weights check is free — the hub stores large blobs
  under a name that is their sha256, so the snapshot symlink already carries
  the digest and the 1.6 GB is never read. `--whisper` still passes any other
  repo or path straight through unpinned.

## Non-goals

Streaming transcription, menu-bar/settings UI, packaging/notarization,
per-app tone adaptation, custom vocabulary, multi-language auto-detect.
