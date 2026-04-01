import shlex
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from otoolbox import _main

args_line = " ".join(sys.argv[1:]).strip()
parsed_args = shlex.split(args_line)

sys.argv = [str(ROOT / "src" / "otoolbox" / "__init__.py"), *parsed_args]

_main()
