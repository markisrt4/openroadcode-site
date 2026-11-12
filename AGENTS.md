# Agent instructions

## Termux diagnostic output and clipboard

- When providing Termux diagnostics for the user to paste into chat, keep **actual stdout and stderr** visible and copy the output (not the command text) to the Android clipboard.
- For ordinary, non-hardware diagnostics, `2>&1 | tee >(termux-clipboard-set)` may be used. Be mindful that pipelines and process substitution affect process lifetime and may obscure exit codes.
- **Never use a live clipboard pipeline such as `tee >(termux-clipboard-set)` around USB-sensitive commands**, including `termux-usb` authorization/handoff, RTL-SDR capture, or other hardware launchers. This pattern has caused the RTL-SDR Termux launcher to hang.
- For USB-sensitive commands, first redirect stdout and stderr to a log; wait until the hardware command exits; then display the log and copy it with a bounded timeout. Report the hardware exit status separately from clipboard status.
- Generic safe example:
  ```bash
  LOG="$HOME/hardware_diagnostic.log"
  hardware_command > "$LOG" 2>&1
  STATUS=$?
  cat "$LOG"
  echo "Hardware exit status: $STATUS"
  timeout 5 termux-clipboard-set < "$LOG"
  echo "Clipboard exit status: $?"
  ```
- For libSDRForge IQ captures, prefer `bash scripts/run_rtlsdr_termux_logged.sh examples/rds_iq_replay.py capture --frequency 94.7 --seconds 3 --acquisition-mode async --output "$HOME/probe.iq"` from the libSDRForge repository. Do not add a live `tee` pipeline around this wrapper.
- Finish Termux:API GPS lookup before entering the USB-authorized capture subprocess. Never expose GPS coordinates in diagnostic logs by default.
- On Termux, RTL-SDR hardware acquisition must use **async** mode, never sync.
