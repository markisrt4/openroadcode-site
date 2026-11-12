# Agent instructions

## Termux diagnostic output and clipboard

- When providing Termux shell commands whose output the user will paste back into chat, keep stdout and stderr visible in the Termux terminal **and** copy the resulting output to the Android clipboard using `2>&1 | tee >(termux-clipboard-set)`.
- Example: `PYTHONPATH="$PWD:$PWD/src" python -u examples/diagnostic.py 2>&1 | tee >(termux-clipboard-set)` (adapt the actual command and paths to the repository).
- Pipe the **output**, not the command string, to `termux-clipboard-set`. Do not use `printf 'command' | termux-clipboard-set`, `termux_terminal_set`, or `> /dev/tty` as substitutes for output capture.
- For multi-command diagnostics, group commands and redirect the group's combined output: `{ command_one; command_two; } 2>&1 | tee >(termux-clipboard-set)`.
- On Termux, RTL-SDR hardware acquisition must use **async** mode; never recommend sync acquisition as a fallback.
