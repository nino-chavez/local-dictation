# Architecture

Single-process Python daemon plus a menu-bar control app, deployed as two
launchd agents. Decisions and their rationale live in [PLAN.md](../../PLAN.md);
this page is the structural view.

## Runtime pipeline

```mermaid
flowchart LR
    HK[right Option tap] -->|toggle| SM{state machine}
    SIL[2s trailing silence] -->|auto_stop| SM
    SM --> REC[Recorder<br/>sounddevice 16kHz mono]
    REC --> ASR[mlx_whisper.transcribe<br/>whisper-large-v3-turbo, on-GPU]
    ASR --> RT{starts with<br/>note phrase?}
    RT -->|no| CL[cleanup<br/>Ollama llama3.1, temp 0]
    RT -->|yes| CLN[cleanup remainder]
    CL --> PASTE[clipboard + synthetic ⌘V<br/>clipboard restored]
    CLN --> NOTES[osascript → macOS Notes<br/>background, no focus steal]
    PASTE -.-> SEAM[--on-capture hook<br/>JSON event, fire-and-forget]
    NOTES -.-> SEAM
```

Cleanup degrades gracefully: if Ollama is unreachable, the raw transcript is
delivered. Routing runs on the raw transcript because cleanup may reword the
hot phrase. The cleanup prompt is injection-hardened (transcript wrapped in
`<transcript>` tags, model forbidden from answering it) — without this,
question-shaped dictation gets answered instead of cleaned.

## Threading model

```mermaid
flowchart TB
    subgraph dictate.py process
        L[pynput Listener thread] -->|toggle| Q[(event queue)]
        A[PortAudio callback thread] -->|auto_stop| Q
        Q --> M[main loop<br/>state machine + pipeline, inline]
        M --> E[emit threads<br/>on-capture, 10s timeout]
    end
```

The pipeline runs inline in the main loop (~1.5s warm); toggles queued during
processing are drained afterwards so a stray tap can't start a phantom
recording.

## Deployment topology

```mermaid
flowchart LR
    subgraph launchd gui domain
        D[com.local-dictation.daemon<br/>dictate.py, KeepAlive]
        T[com.local-dictation.menubar<br/>menubar.py, KeepAlive]
    end
    T -->|launchctl bootstrap / kickstart / bootout| D
    T -->|pgrep poll, 3s| D
    D --> LOG[~/Library/Logs/local-dictation.log]
```

The tray never owns the daemon process — launchd is the single owner
(crash-restart, logging); the tray is a control plane and therefore needs no
TCC permissions. The daemon's TCC grants (Microphone, Accessibility, Input
Monitoring) attach to the resolved Homebrew Python binary; a Python upgrade
invalidates them (symptom: "This process is not trusted!" in the log).

## Privacy boundary

No non-localhost traffic at runtime: Whisper runs in-process (weights cached,
`HF_HUB_OFFLINE=1`), cleanup talks only to `localhost:11434`, audio lives in
memory only, and the daemon stores nothing — the `--on-capture` seam hands
events to external consumers who own storage and schema (see PLAN.md
"Product boundary").
