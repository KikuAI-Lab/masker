## 2024-05-23 - [Optimizing String Replacements]
**Learning:** Repeated string concatenation in loops (`str = str + replacement`) is O(N^2) (in Python) and can be a significant bottleneck for large texts or many replacements.
**Action:** Use list accumulation and `"".join()` or `io.StringIO` for linear time string construction. When replacing parts of a string based on indices, collecting parts in a list and joining them is cleaner and faster.
