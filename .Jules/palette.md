## 2025-10-24 - Use rounded box characters for terminal logs
**Learning:** Hard-edged, square ASCII box characters can make terminal logs look dated and visually harsh. Rounded corners (`╭`, `╮`, `╰`, `╯` or `\u256d`, `\u256e`, `\u2570`, `\u256f`) provide a softer, more modern and aesthetically pleasing UI for command-line output.
**Action:** When designing terminal output or ASCII art boundaries, default to using rounded box-drawing characters for improved aesthetics. Ensure any formatting tests explicitly assert the exact character codes to prevent regression.
