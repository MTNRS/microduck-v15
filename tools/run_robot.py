"""Run the controller from a checkout, with no package install needed."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'software'))
from microduck.cli import main

if __name__ == '__main__':
    raise SystemExit(main())
