## 2024-05-18 - Rounded corners for softer UI
**Learning:** Hard square edges in terminal output can feel a bit rigid. Replacing box characters with rounded edges adds a softer, more modern aesthetic, which users tend to perceive as friendlier and easier to read, thereby subtly improving the micro-UX of the log output.
**Action:** Replaced `\u250c`, `\u2510`, `\u2514`, `\u2518` (square) with `\u256d`, `\u256e`, `\u2570`, `\u256f` (rounded) in the terminal log box borders to improve visual appeal.
