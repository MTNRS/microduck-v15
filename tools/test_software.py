"""Run the software tests on a PC without Raspberry Pi dependencies."""

from pathlib import Path
import sys
import unittest

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'software'))
result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(root / 'tests')))
raise SystemExit(0 if result.wasSuccessful() and result.testsRun else 1)
