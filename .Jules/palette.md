## 2026-06-09 - Terminal Box UI
**Learning:** Hard-angled (square) ASCII box-drawing characters (`┌`, `┐`, `└`, `┘`) can make a terminal interface feel stark and dated. Switching to rounded corners (`╭`, `╮`, `╰`, `╯`) provides a subtly softer, more modern, and more approachable aesthetic without changing the layout.
**Action:** Default to using rounded corner characters (`\u256d`, `\u256e`, `\u2570`, `\u256f`) for all terminal box decorations unless a specific rigid structure requires sharp corners.
