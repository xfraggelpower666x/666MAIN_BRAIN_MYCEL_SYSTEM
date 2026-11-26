import tempfile
import unittest
from pathlib import Path
from engine import mandala, preset_evidence, musical_forces

class EmergentEvolutionTests(unittest.TestCase):
    def report(self):
        return {'system_id':'666TDI-001','classification':'PRESET_CANDIDATE',
                'mandala_candidate':True,
                'signal_evidence':{'MANTRA':['mantra'],'SPACE':['orbit'],'MOTION':['rolling bass']},
                'negated_signals':{},
                'functional_relations':[{'from':'MOTION','to':'SPACE','relation':'ANCHOR','impact':'review'}],
                'preset_candidate':{'functional_bundles':['MOTION','SPACE'],'lyrics_embedded':False,'genre':'psy','bpm':144}}

    def test_dynamic_rings(self):
        r=mandala.arrange(self.report())
        self.assertEqual(r['dynamic_rings'],['CENTER','INNER','OUTER'])
        self.assertEqual(r['functional_edges'][0]['to_ring'],'OUTER')

    def test_negated_edge_removed(self):
        r=self.report()
        r['negated_signals']['MOTION']=['no rolling bass']
        self.assertEqual(mandala.arrange(r)['functional_edges'],[])

    def test_explicit_versions(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError,'CREATOR_APPROVAL'):
                preset_evidence.persist(root,'test',self.report())
            first=preset_evidence.persist(root,'test',self.report(),creator_approved=True)
            second=preset_evidence.persist(root,'test',self.report(),creator_approved=True,expected_version=1)
            self.assertEqual(second['previous_sha256'],first['sha256'])
            self.assertEqual(len(preset_evidence.read_versions(root,'test')),2)
            with self.assertRaisesRegex(ValueError,'VERSION_CONFLICT'):
                preset_evidence.persist(root,'test',self.report(),creator_approved=True)
            (Path(root)/'presets/test/00000001.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'INTEGRITY'):
                preset_evidence.read_versions(root,'test')

    def test_chaos_edge_hold(self):
        intent={'system_id':'666TDI-001','mid':'directed chaos shared motif digital clipping'}
        sem={'system_id':'666TDI-001','functions':[]}
        ca={'system_id':'666TDI-001','emergences':[]}
        r=musical_forces.derive(intent,sem,ca)
        self.assertEqual(r['functional_edges'][0]['status'],'HOLD')
        self.assertFalse(r['audio_verified'])

    def test_spatial_contrast_edge(self):
        intent={'system_id':'666TDI-001','story':'hope'}
        sem={'system_id':'666TDI-001','functions':[
          {'id':key,'status':'SUPPORTED','support_evidence':[{'field':'high','text':key}]}
          for key in ('SPATIAL_MOTION','LOW_ANCHOR','DYNAMIC_CONTRAST')]}
        ca={'system_id':'666TDI-001','emergences':[]}
        r=musical_forces.derive(intent,sem,ca)
        self.assertIn('CONTRAST_SPATIAL_MOVEMENT',[x['relation'] for x in r['functional_edges']])
        self.assertIn('EMOTIONAL_SPACE',[x['relation'] for x in r['functional_edges']])
