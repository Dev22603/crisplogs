## 2026-06-30 - Modernize logging boxes with rounded corners
**Learning:** Hard-angled (square) box corners in terminal outputs can feel rigid or outdated. Swapping standard line-drawing characters for rounded variants (`\u256d`, `\u256e`, `\u2570`, `\u256f`) provides a softer, more modern and accessible aesthetic to developers reviewing logs, easing cognitive load when scanning verbose terminal output.
**Action:** Default to rounded corners for purely decorative bounding boxes or borders in CLI/terminal UI contexts unless a rigid table structure specifically calls for square intersections.
