"""Public regression; private R02 test only if source database is present locally."""
import sys, unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
private=(root/'legacy_r02/app/lyrics_library.db').is_file()
suite=unittest.defaultTestLoader.discover(str(root/'tests'),pattern='test_*.py')
def flatten(s):
 for x in s:
  if isinstance(x,unittest.TestSuite):yield from flatten(x)
  else:yield x
tests=[t for t in flatten(suite) if private or not t.id().endswith('test_legacy_readonly')]
print('LEGACY_DB_TEST: '+('INCLUDED' if private else 'NOT_RUN_PRIVATE_FIXTURE_MISSING'))
r=unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(tests))
print(f'REGRESSION: {r.testsRun}/{len(tests)}')
sys.exit(0 if r.wasSuccessful() else 1)
