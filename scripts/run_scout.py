import subprocess
import sys


def main() -> int:
    cmd = [sys.executable, "skills/course_hunter/hunt_deeplearning.py"]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
