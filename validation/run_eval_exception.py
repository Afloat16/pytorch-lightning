import json
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

BASE = "84df182f50ab34301aabb3c0eb4031815bfb413d"
HEAD = "441c3f9ee6e6d7a04b4d8f022da755ad44eb5a53"
FILES = ["src/lightning/pytorch/loops/evaluation_loop.py", "src/lightning/pytorch/loops/prediction_loop.py", "tests/tests_pytorch/loops/test_evaluation_exception_modes.py"]
SOURCES = FILES[:2]
TEST = FILES[2]
subprocess.run(["git", "fetch", "--no-tags", "--depth=1", "origin", BASE, HEAD], check=True)
for path in FILES:
    assert Path(path).read_bytes() == subprocess.check_output(["git", "show", f"{HEAD}:{path}"]), path

def run(label, tests):
    args = [sys.executable, "-m", "pytest", "-q", *tests, f"--junitxml={label}.xml"]
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    Path(f"{label}.log").write_text(p.stdout)
    print(p.stdout, flush=True)
    root = ElementTree.parse(f"{label}.xml").getroot()
    out = {k: sum(int(s.get(k, 0)) for s in root.iter("testsuite")) for k in ("tests", "failures", "errors", "skipped")}
    out["returncode"] = p.returncode
    print(label, out, flush=True)
    return out

fixed = {path: Path(path).read_bytes() for path in SOURCES}
try:
    for path in SOURCES:
        Path(path).write_bytes(subprocess.check_output(["git", "show", f"{BASE}:{path}"]))
    before = run("before", [TEST])
finally:
    for path, contents in fixed.items():
        Path(path).write_bytes(contents)
after = run("after", [TEST])
existing = run("existing", ["tests/tests_pytorch/loops/test_evaluation_loop.py", "tests/tests_pytorch/loops/test_prediction_loop.py"])
result = {"base": BASE, "head": HEAD, "before": before, "after": after, "existing": existing}
Path("validation_result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2), flush=True)
assert before["returncode"] == 1 and before["failures"] > 0 and before["errors"] == 0, before
assert after == {"tests": 27, "failures": 0, "errors": 0, "skipped": 0, "returncode": 0}, after
assert existing["returncode"] == existing["failures"] == existing["errors"] == 0, existing
for path in FILES:
    assert Path(path).read_bytes() == subprocess.check_output(["git", "show", f"{HEAD}:{path}"]), path
