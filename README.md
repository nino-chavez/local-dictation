# local-dictation

Fully local Wispr Flow clone for macOS (Apple Silicon). Tap a hotkey, speak,
tap again (or pause ~2 s) — cleaned-up text is pasted into whatever field has
focus. Whisper (MLX, on-GPU) transcribes; Ollama removes filler words and fixes
punctuation. The only network traffic is `localhost:11434`.

See `PLAN.md` for architecture and decisions.

## Run

```sh
cd ~/Workspace/dev/wip/local-dictation
.venv/bin/python dictate.py
```

Wait for `ready — tap alt_r to dictate`, then in any app: tap **right Option**,
speak, tap again or just pause. You'll hear a Tink on start, a Pop on stop.

## First-run permissions

Grant these to the terminal app you run it from (System Settings → Privacy &
Security), then restart the daemon:

- **Microphone** — prompted automatically on first recording
- **Input Monitoring** — prompted automatically for the global hotkey
- **Accessibility** — add manually if text never appears (needed for the synthetic ⌘V)

## Run at login (launchd)

`com.nino.local-dictation.plist` is included but NOT loaded automatically —
loading it starts a background daemon with mic + Input Monitoring access, so
that's an explicit opt-in:

```sh
cp com.nino.local-dictation.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.nino.local-dictation.plist
```

Stop / remove:

```sh
launchctl bootout gui/$UID/com.nino.local-dictation
rm ~/Library/LaunchAgents/com.nino.local-dictation.plist
```

Status and logs: `launchctl print gui/$UID/com.nino.local-dictation` and
`~/Library/Logs/local-dictation.log`.

Permissions caveat: under launchd there is no hosting terminal, so macOS
attributes the TCC prompts to the `.venv` python binary itself — expect fresh
Microphone / Input Monitoring / Accessibility prompts on first launchd run
even if your terminal already has grants. The plist restarts the daemon on
crash (`KeepAlive.SuccessfulExit=false`); Ollama being down is fine — the
daemon inserts raw transcripts until it returns.

## Options

```
--key alt_r          toggle key (any pynput name: cmd_r, f13, ...)
--model llama3.1     Ollama model for the cleanup pass
--no-cleanup         insert the raw transcript, skip Ollama
--no-auto-stop       only the hotkey stops recording
--silence-secs 2.0   trailing silence before auto-stop
--language en        spoken language
--test-file f.wav    pipeline check without mic/hotkey (prints instead of pastes)
```

## Notes

- First use of a new `--whisper` model downloads weights from Hugging Face;
  after that the daemon sets `HF_HUB_OFFLINE=1` and runs fully offline.
- Text insertion goes through the clipboard (paste is reliable where synthetic
  typing is not). Your previous clipboard **text** is restored afterwards;
  non-text clipboard content (images) is not.
- If Ollama is down the raw transcript is inserted instead — dictation never
  hard-fails on the cleanup leg.
- If tapping right Option does nothing even after granting Input Monitoring
  (some keyboards remap it), pick another key: `--key f13` or `--key cmd_r`.
- Setup from scratch: `uv venv --python 3.13 .venv && uv pip install --python
  .venv/bin/python mlx-whisper sounddevice pynput` (ffmpeg via Homebrew).
