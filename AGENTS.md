# Agent instructions

## Termux diagnostic output and clipboard

- Show actual stdout and stderr for diagnostics pasted into chat; copy output (not command text) with `termux-clipboard-set`.
- Use `mktemp "${TMPDIR:-$PREFIX/tmp}/diagnostic.XXXXXX"` for temporary Termux logs, not `$HOME` or hardcoded `/tmp`. Remove them after clipboard copying. Keep files in `$HOME` only for explicitly requested persistent recordings, captures, or logs.
- For non-hardware diagnostics, live clipboard pipelines may be used, but can obscure exit status. Prefer sequential temporary-file logging when status matters.
- **Never use a live clipboard pipeline with USB-sensitive commands**, including `termux-usb` handoff and RTL-SDR capture. This can hang USB handoff.
- Wait for hardware commands to finish before copying logs; preserve hardware exit status independently of clipboard status.
- Generic safe example:
  ```bash
  LOG="$(mktemp "${TMPDIR:-$PREFIX/tmp}/diagnostic.XXXXXX")"
  trap 'rm -f "$LOG"' EXIT
  hardware_command > "$LOG" 2>&1
  STATUS=$?
  cat "$LOG"
  echo "Hardware exit status: $STATUS"
  timeout 5 termux-clipboard-set < "$LOG"
  echo "Clipboard exit status: $?"
  exit "$STATUS"
  ```
- For libSDRForge IQ captures, prefer `bash scripts/run_rtlsdr_termux_logged.sh examples/rds_iq_replay.py capture --frequency 94.7 --seconds 3 --acquisition-mode async --output "$HOME/probe.iq"` in libSDRForge. The explicitly saved IQ file is a persistent artifact; do not wrap the launcher in a live clipboard pipeline.
- Complete Termux:API GPS lookups before USB-authorized capture. Never expose GPS coordinates in diagnostic logs by default.
- On Termux, RTL-SDR acquisition must use **async** mode, never sync.
