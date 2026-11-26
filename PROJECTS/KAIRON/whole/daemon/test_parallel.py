import unittest
from parallel import plan

P = 'PROJECTS/666TDI/'


def task(key, reads=(), writes=(), deps=(), auth=True, barrier=False, mode='DEEP_EVOLUTION'):
    return dict(id=key, reads=[P+x for x in reads], writes=[P+x for x in writes],
                depends_on=list(deps), authorized=auth, barrier=barrier,
                mode=mode, evidence_ref='fixture:'+key)


class ParallelTests(unittest.TestCase):
    def test_independent(self):
        self.assertEqual(plan([task('a', writes=['a']), task('b', writes=['b'])])['waves'], [['a','b']])
    def test_shared_reads(self):
        self.assertEqual(plan([task('a', reads=['a']), task('b', reads=['a'])])['waves'], [['a','b']])
    def test_parent_conflict(self):
        self.assertEqual(plan([task('a', writes=['a']), task('b', reads=['a/b'])])['waves'], [['a'],['b']])
    def test_dependency(self):
        self.assertEqual(plan([task('a', reads=['a'], deps=['b']), task('b', reads=['b'])])['waves'], [['b'],['a']])
    def test_barrier(self):
        self.assertEqual(plan([task('a', reads=['a']), task('b', reads=['b'], barrier=True)])['waves'], [['a'],['b']])
    def test_exact_not_greedy(self):
        rows=[task('a', writes=['x']), task('b', reads=['x/a']), task('c', reads=['x/b'])]
        self.assertEqual(plan(rows)['waves'], [['b','c'],['a']])
    def test_denial(self):
        p=plan([task('a', reads=['a'], auth=False), task('b', reads=['b'], deps=['a'])])
        self.assertEqual(p['waves'],[])
        self.assertEqual(p['blocked']['a'],'AUTHORIZATION_MISSING')
    def test_cycle(self):
        self.assertEqual(plan([task('a', reads=['a'], deps=['b']),task('b', reads=['b'], deps=['a'])])['status'],'PLAN_PARTIAL')
    def test_foreign(self):
        t=task('a',reads=['a']); t['reads']=['PROJECTS/LYVRA/a']
        with self.assertRaisesRegex(ValueError,'FOREIGN_SCOPE'): plan([t])
    def test_traversal(self):
        with self.assertRaisesRegex(ValueError,'INVALID_SCOPE'): plan([task('a',reads=['../a'])])
    def test_unknown(self):
        with self.assertRaisesRegex(ValueError,'UNKNOWN_DEPENDENCY'): plan([task('a',reads=['a'],deps=['b'])])
    def test_fallback_truth(self):
        p=plan([task('a',reads=['a']),task('b',reads=['b'])],max_exact=1)
        self.assertFalse(p['exact_maximum_per_wave']); self.assertFalse(p['dispatch_performed'])
    def test_alternatives(self):
        p=plan([task('a',reads=['a'],mode='CREATIVE_EXPLORATION')]); self.assertEqual(p['alternatives']['CREATIVE_EXPLORATION'],['a'])
        self.assertFalse(p['execution_verified'])

if __name__ == '__main__': unittest.main()
