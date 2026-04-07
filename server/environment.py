import multiprocessing
import uuid
from typing import Any, Dict, List, Optional, Tuple

from openenv.core.env_server import Action, Environment, Observation, State

from models import CodeDebugAction, CodeDebugObservation, CodeDebugState

# ---------------------------------------------------------------------------
# Task definitions
# ---------------------------------------------------------------------------

TASKS: Dict[str, Dict[str, Any]] = {
    "easy_001": {
        "difficulty": "easy",
        "description": "Fix syntax errors in calculate_average function",
        "broken_code": (
            "def calculate_average(numbers)\n"
            "    total = 0\n"
            "    for num in numbers\n"
            "        total = total + num\n"
            "    return total / len(numbers)\n"
        ),
        "tests": [
            ("assert calculate_average([1, 2, 3]) == 2.0", "calculate_average([1, 2, 3]) == 2.0"),
            ("assert calculate_average([10, 20]) == 15.0", "calculate_average([10, 20]) == 15.0"),
            ("assert calculate_average([5]) == 5.0", "calculate_average([5]) == 5.0"),
            ("assert calculate_average([0, 0, 0]) == 0.0", "calculate_average([0, 0, 0]) == 0.0"),
            ("assert calculate_average([-1, 1]) == 0.0", "calculate_average([-1, 1]) == 0.0"),
        ],
    },
    "medium_001": {
        "difficulty": "medium",
        "description": "Fix logic errors in is_palindrome and count_vowels functions",
        "broken_code": (
            "def is_palindrome(s):\n"
            "    s = s.lower()\n"
            "    return s == s\n"
            "\n"
            "def count_vowels(text):\n"
            "    vowels = \"aeiou\"\n"
            "    count = 0\n"
            "    for char in text:\n"
            "        if char in vowels:\n"
            "            count += 2\n"
            "    return count\n"
        ),
        "tests": [
            ("assert is_palindrome('racecar') == True", "is_palindrome('racecar') == True"),
            ("assert is_palindrome('hello') == False", "is_palindrome('hello') == False"),
            ("assert is_palindrome('Madam') == True", "is_palindrome('Madam') == True"),
            ("assert count_vowels('hello') == 2", "count_vowels('hello') == 2"),
            ("assert count_vowels('aeiou') == 5", "count_vowels('aeiou') == 5"),
        ],
    },
    "hard_001": {
        "difficulty": "hard",
        "description": "Fix bugs in data stream compression, decompression, and statistics functions",
        "broken_code": (
            "def compress_stream(data):\n"
            "    if not data:\n"
            "        return []\n"
            "    compressed = []\n"
            "    i = 0\n"
            "    while i < len(data):\n"
            "        j = i\n"
            "        while j < len(data) and data[j] == data[i]:\n"
            "            j += 1\n"
            "        compressed.append((data[i], j - i - 1))\n"
            "        i = j\n"
            "    return compressed\n"
            "\n"
            "def decompress_stream(compressed):\n"
            "    data = []\n"
            "    for value, count in compressed:\n"
            "        data.append(value)\n"
            "        data.extend([value] * count)\n"
            "    return data\n"
            "\n"
            "def stream_stats(compressed):\n"
            "    if not compressed:\n"
            "        return (0, 0, 0.0)\n"
            "    total = len(compressed)\n"
            "    for _, c in compressed:\n"
            "        total += c\n"
            "    segments = len(compressed)\n"
            "    avg_len = round(total / segments, 2)\n"
            "    return (total, segments, avg_len)\n"
        ),
        "tests": [
            ("c = compress_stream([1,1,1,2,2]); assert (decompress_stream(c), stream_stats(c)) == ([1,1,1,2,2], (5, 2, 2.5))", "compress/decompress/stats for [1,1,1,2,2]"),
            ("c = compress_stream(['a','b','b','b']); assert (decompress_stream(c), stream_stats(c)) == (['a','b','b','b'], (4, 2, 2.0))", "compress/decompress/stats for ['a','b','b','b']"),
            ("c = compress_stream([7]); assert (decompress_stream(c), stream_stats(c)) == ([7], (1, 1, 1.0))", "compress/decompress/stats for [7]"),
            ("c = compress_stream([1,2,3]); assert (decompress_stream(c), stream_stats(c)) == ([1,2,3], (3, 3, 1.0))", "compress/decompress/stats for [1,2,3]"),
            ("c = compress_stream([0,0,0,0]); assert (decompress_stream(c), stream_stats(c)) == ([0,0,0,0], (4, 1, 4.0))", "compress/decompress/stats for [0,0,0,0]"),
            ("c = compress_stream([5,5,3,3,3,5,5]); assert (decompress_stream(c), stream_stats(c)) == ([5,5,3,3,3,5,5], (7, 3, 2.33))", "compress/decompress/stats for [5,5,3,3,3,5,5]"),
        ],
    },
    "easy_002": {
        "difficulty": "easy",
        "description": "Fix missing return statement and wrong comparison operator in find_max",
        "broken_code": (
            "def find_max(lst):\n"
            "    if not lst:\n"
            "        return None\n"
            "    max_val = lst[0]\n"
            "    for item in lst:\n"
            "        if item < max_val:\n"
            "            max_val = item\n"
        ),
        "tests": [
            ("assert find_max([1, 2, 3]) == 3", "find_max([1, 2, 3]) == 3"),
            ("assert find_max([5, 1, 3]) == 5", "find_max([5, 1, 3]) == 5"),
            ("assert find_max([-1, -5, -2]) == -1", "find_max([-1, -5, -2]) == -1"),
            ("assert find_max([42]) == 42", "find_max([42]) == 42"),
            ("assert find_max([]) == None", "find_max([]) == None"),
        ],
    },
    "easy_003": {
        "difficulty": "easy",
        "description": "Fix off-by-one errors in repeat_string and first_n_chars",
        "broken_code": (
            "def repeat_string(s, n):\n"
            "    return s * (n - 1)\n"
            "\n"
            "def first_n_chars(s, n):\n"
            "    return s[:n + 1]\n"
        ),
        "tests": [
            ("assert repeat_string('ab', 3) == 'ababab'", "repeat_string('ab', 3) == 'ababab'"),
            ("assert repeat_string('x', 1) == 'x'", "repeat_string('x', 1) == 'x'"),
            ("assert repeat_string('hi', 0) == ''", "repeat_string('hi', 0) == ''"),
            ("assert first_n_chars('hello', 3) == 'hel'", "first_n_chars('hello', 3) == 'hel'"),
            ("assert first_n_chars('world', 1) == 'w'", "first_n_chars('world', 1) == 'w'"),
        ],
    },
    "medium_002": {
        "difficulty": "medium",
        "description": "Fix mutable default state bug in merge_dicts and missing deduplication in unique_sorted",
        "broken_code": (
            "def merge_dicts(d1, d2):\n"
            "    result = d1\n"
            "    for key, value in d2.items():\n"
            "        result[key] = value\n"
            "    return result\n"
            "\n"
            "def unique_sorted(lst):\n"
            "    return sorted(lst)\n"
        ),
        "tests": [
            ("d = {'a': 1}; merge_dicts(d, {'b': 2}); assert d == {'a': 1}", "merge_dicts does not mutate original"),
            ("assert merge_dicts({'a': 1}, {'b': 2}) == {'a': 1, 'b': 2}", "merge_dicts combines two dicts"),
            ("assert merge_dicts({}, {'x': 1}) == {'x': 1}", "merge_dicts with empty first dict"),
            ("assert unique_sorted([3, 1, 2, 1, 3]) == [1, 2, 3]", "unique_sorted removes duplicates"),
            ("assert unique_sorted([5, 5, 5]) == [5]", "unique_sorted with all same values"),
        ],
    },
    "medium_003": {
        "difficulty": "medium",
        "description": "Fix wrong list operation in flatten_list and off-by-one in chunk_list",
        "broken_code": (
            "def flatten_list(nested):\n"
            "    result = []\n"
            "    for item in nested:\n"
            "        if isinstance(item, list):\n"
            "            result.append(item)\n"
            "        else:\n"
            "            result.append(item)\n"
            "    return result\n"
            "\n"
            "def chunk_list(lst, size):\n"
            "    return [lst[i:i+size-1] for i in range(0, len(lst), size)]\n"
        ),
        "tests": [
            ("assert flatten_list([1, [2, 3], 4]) == [1, 2, 3, 4]", "flatten_list with mixed nesting"),
            ("assert flatten_list([[1, 2], [3, 4]]) == [1, 2, 3, 4]", "flatten_list with all nested"),
            ("assert flatten_list([1, 2, 3]) == [1, 2, 3]", "flatten_list with no nesting"),
            ("assert chunk_list([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]", "chunk_list into pairs"),
            ("assert chunk_list([1, 2, 3], 3) == [[1, 2, 3]]", "chunk_list single chunk"),
        ],
    },
    "hard_002": {
        "difficulty": "hard",
        "description": "Fix bugs in a data pipeline: record parsing, filtering, sorting, and summarization",
        "broken_code": (
            "def parse_records(raw_data):\n"
            "    records = []\n"
            "    for line in raw_data.strip().split('\\n'):\n"
            "        parts = line.split('|')\n"
            "        records.append({\n"
            "            'name': parts[0].strip(),\n"
            "            'age': int(parts[1]),\n"
            "            'score': float(parts[2])\n"
            "        })\n"
            "    return records\n"
            "\n"
            "def filter_and_sort(records, min_score):\n"
            "    filtered = [r for r in records if r['score'] > min_score]\n"
            "    filtered.sort(key=lambda r: r['score'])\n"
            "    return filtered\n"
            "\n"
            "def summarize(records):\n"
            "    if not records:\n"
            "        return {'count': 0, 'avg_score': 0.0, 'top_scorer': None}\n"
            "    total = sum(r['score'] for r in records)\n"
            "    avg = total / len(records)\n"
            "    top = max(records, key=lambda r: r['age'])\n"
            "    return {'count': len(records), 'avg_score': round(avg, 2), 'top_scorer': top['name']}\n"
        ),
        "tests": [
            ("records = parse_records('Alice|30|85.5\\nBob|25|92.0\\nCharlie|35|78.0'); assert records[0] == {'name': 'Alice', 'age': 30, 'score': 85.5}", "parse_records extracts first record"),
            ("records = parse_records('Alice|30|85.5\\nBob|25|92.0\\nCharlie|35|78.0'); filtered = filter_and_sort(records, 85.5); assert len(filtered) == 2", "filter_and_sort includes boundary score"),
            ("records = parse_records('Alice|30|85.5\\nBob|25|92.0\\nCharlie|35|78.0'); filtered = filter_and_sort(records, 0); assert filtered[0]['name'] == 'Bob'", "filter_and_sort highest score first"),
            ("records = parse_records('Alice|30|85.5\\nBob|25|92.0\\nCharlie|35|78.0'); s = summarize(records); assert s['avg_score'] == 85.17", "summarize calculates correct average"),
            ("records = parse_records('Alice|30|85.5\\nBob|25|92.0\\nCharlie|35|78.0'); s = summarize(records); assert s['top_scorer'] == 'Bob'", "summarize finds top scorer by score"),
            ("records = parse_records('Solo|20|100.0'); s = summarize(records); assert s == {'count': 1, 'avg_score': 100.0, 'top_scorer': 'Solo'}", "summarize single record"),
        ],
    },
}

MAX_STEPS = 5
EXEC_TIMEOUT = 3


def _exec_in_process(
    code: str, tests: List[Tuple[str, str]], result_queue: multiprocessing.Queue
) -> None:
    """Target for subprocess — runs code + tests and puts result on queue."""
    total = len(tests)
    passed = 0
    feedback_lines: List[str] = []

    namespace: Dict[str, Any] = {}
    try:
        exec(compile(code, "<submitted>", "exec"), namespace)  # noqa: S102
    except Exception as exc:
        result_queue.put((0, total, f"Code failed to execute: {type(exc).__name__}: {exc}"))
        return

    for assertion, description in tests:
        try:
            exec(compile(assertion, "<test>", "exec"), namespace)  # noqa: S102
            passed += 1
        except AssertionError:
            feedback_lines.append(f"FAIL: {description}")
        except Exception as exc:
            feedback_lines.append(f"ERROR ({type(exc).__name__}): {description}")

    if passed == total:
        feedback = "All tests passed!"
    else:
        feedback = f"{passed}/{total} tests passed.\n" + "\n".join(feedback_lines)

    result_queue.put((passed, total, feedback))


def _run_tests(
    code: str, tests: List[Tuple[str, str]]
) -> Tuple[int, int, str]:
    """Execute *code* then run each test assertion in a subprocess with timeout."""
    total = len(tests)
    queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=_exec_in_process, args=(code, tests, queue))
    proc.start()
    proc.join(timeout=EXEC_TIMEOUT)

    if proc.is_alive():
        proc.kill()
        proc.join()
        return 0, total, "Code execution timed out (possible infinite loop)"

    if queue.empty():
        return 0, total, "Code execution failed unexpectedly"

    return queue.get()


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------


class CodeDebugEnvironment(Environment):
    """Python code-debugging environment with 3 hardcoded tasks."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._state = CodeDebugState()
        self._current_task: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # reset
    # ------------------------------------------------------------------

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> CodeDebugObservation:
        # Pick task from episode_id or default to first
        task_id = episode_id or "easy_001"
        task = TASKS.get(task_id)
        if task is None:
            task_id = "easy_001"
            task = TASKS[task_id]

        self._current_task = task
        self._state = CodeDebugState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            current_task_id=task_id,
            difficulty=task["difficulty"],
        )

        return CodeDebugObservation(
            done=False,
            reward=None,
            task_id=task_id,
            difficulty=task["difficulty"],
            broken_code=task["broken_code"],
            description=task["description"],
            score=0.0,
            tests_passed=0,
            total_tests=len(task["tests"]),
            feedback="Fix the broken code and submit your solution.",
        )

    # ------------------------------------------------------------------
    # step
    # ------------------------------------------------------------------

    def step(
        self,
        action: Action,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> CodeDebugObservation:
        assert isinstance(action, CodeDebugAction)
        task = self._current_task
        if task is None:
            return CodeDebugObservation(
                done=True,
                reward=0.0,
                feedback="No active task. Call reset first.",
            )

        self._state.step_count += 1
        tests_passed, total_tests, feedback = _run_tests(
            action.fixed_code, task["tests"]
        )
        score = tests_passed / total_tests if total_tests > 0 else 0.0
        done = score == 1.0 or self._state.step_count >= MAX_STEPS

        return CodeDebugObservation(
            done=done,
            reward=score,
            task_id=self._state.current_task_id,
            difficulty=self._state.difficulty,
            broken_code=task["broken_code"],
            description=task["description"],
            score=score,
            tests_passed=tests_passed,
            total_tests=total_tests,
            feedback=feedback,
        )

    # ------------------------------------------------------------------
    # state
    # ------------------------------------------------------------------

    @property
    def state(self) -> CodeDebugState:
        return self._state
