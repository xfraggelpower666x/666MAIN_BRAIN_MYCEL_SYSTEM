"""Adversarial R08 trust rotation tests, no real owner identity claims."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from candidate.signed_provenance_r07 import canonical_bytes,ENVELOPE_SCHEMA
from candidate.source_registry_r06 import REGISTRY_SCHEMA
from candidate.trust_rotation_r08 import (
    ROTATION_SCHEMA,REVOCATION_SCHEMA,SCHEMA,verify_rotated_sources
)


def pubkey(k):
    return k.public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw).hex()


def fixture():
    old=Ed25519PrivateKey.generate();new=Ed25519PrivateKey.generate();admin=Ed25519PrivateKey.generate()
    text='CLAIM CAUSE A -> B';digest=hashlib.sha256(text.encode()).hexdigest()
    doc={'document_id':'docA','source_text':text,'observed_at':'2026-11-20T10:00:00Z','source_group':'groupA'}
    reg={'schema':REGISTRY_SCHEMA,'review_status':'EXTERNAL_REVIEW_REQUIRED','entries':[
       {'document_id':'docA','source_group':'groupA','observed_at':doc['observed_at'],'content_sha256':digest,'provenance_ref':'read_only','issuer_id':'issuerA'}]}
    rev={'revision_id':'rev1','document_id':'docA','observed_at':doc['observed_at'],'parent_revisions':[],'status':'ACTIVE','content_sha256':digest}
    payload={'registry':reg,'sequence':20,'revisions':[rev],'revocations':[],'issued_at':'2026-11-22T10:00:00Z'}
    policy={'schema':'666CURES_R08_EXTERNAL_TRUST_POLICY_V1','issuer_id':'issuerA',
            'pinned_keys':{'old':pubkey(old),'admin':pubkey(admin)},'authorized_rotations':{},
            'revocation_authority_keys':['admin']}
    rp={'rotation_id':'rot1','issuer_id':'issuerA','old_key_id':'old','new_key_id':'new',
        'new_public_key_hex':pubkey(new),'effective_sequence':19,'observed_at':'2026-11-21T00:00:00Z'}
    policy['authorized_rotations']['rot1']=hashlib.sha256(canonical_bytes(rp)).hexdigest()
    rot={'schema':ROTATION_SCHEMA,'payload':rp,'old_signature_hex':old.sign(canonical_bytes(rp)).hex(),
         'new_signature_hex':new.sign(canonical_bytes(rp)).hex()}
    def envelope(p=payload,key=new,kid='new'):
        return {'schema':ENVELOPE_SCHEMA,'key_id':kid,'signature_hex':key.sign(canonical_bytes(p)).hex(),'payload':copy.deepcopy(p)}
    def event(subject='docB',subject_type='DOCUMENT',seq=1,event_id='evt1',key=admin,kid='admin'):
        p={'event_id':event_id,'issuer_id':'issuerA','sequence':seq,'issued_at':'2026-11-22T11:00:00Z',
           'subject_type':subject_type,'subject_id':subject,'reason':'Owner-supplied withdrawal'}
        return {'schema':REVOCATION_SCHEMA,'key_id':kid,'signature_hex':key.sign(canonical_bytes(p)).hex(),'payload':p}
    return dict(docs=[doc],payload=payload,policy=policy,rotation=rot,envelope=envelope,event=event,old=old,new=new,admin=admin)

class TestR08(unittest.TestCase):
    def setUp(self):self.f=fixture()
    def verify(self,**kw):
        f=self.f;args={'documents':f['docs'],'envelope':f['envelope'](),
                        'external_trust_policy':f['policy'],'minimum_sequence':20,
                        'rotation':f['rotation'],'revocation_events':[], 'minimum_event_sequence':0}
        args.update(kw)
        return verify_rotated_sources(**args)
    def rejects(self,**kw):
        with self.assertRaises(ValueError):self.verify(**kw)

    def test_01_happy_dual_attestation(self):
        r=self.verify();self.assertEqual(r['schema'],SCHEMA);self.assertTrue(r['rotation']['dual_signature_verified'])
    def test_02_no_trust_on_first_use(self):
        p=copy.deepcopy(self.f['policy']);p['authorized_rotations']={};self.rejects(external_trust_policy=p)
    def test_03_new_key_injection_rejected(self):
        p=copy.deepcopy(self.f['policy']);p['pinned_keys']={};self.rejects(external_trust_policy=p)
    def test_04_old_signature_corruption(self):
        r=copy.deepcopy(self.f['rotation']);r['old_signature_hex']='00'*64;self.rejects(rotation=r)
    def test_05_new_signature_corruption(self):
        r=copy.deepcopy(self.f['rotation']);r['new_signature_hex']='00'*64;self.rejects(rotation=r)
    def test_06_rotation_tamper(self):
        r=copy.deepcopy(self.f['rotation']);r['payload']['effective_sequence']=200;self.rejects(rotation=r)
    def test_07_unknown_issuer(self):
        r=copy.deepcopy(self.f['rotation']);r['payload']['issuer_id']='attacker';self.rejects(rotation=r)
    def test_08_future_rotation(self):
        r=copy.deepcopy(self.f['rotation']);r['payload']['effective_sequence']=21
        self.rejects(rotation=r)
    def test_09_replay_registry_floor(self):self.rejects(minimum_sequence=21)
    def test_10_bool_sequence_invalid(self):self.rejects(minimum_sequence=True)
    def test_11_missing_sequence_invalid(self):self.rejects(minimum_sequence=None)
    def test_12_old_signed_envelope_after_rotation(self):
        f=self.f;self.rejects(envelope=f['envelope'](key=f['old'],kid='old'))
    def test_13_unknown_key(self):
        f=self.f;self.rejects(envelope=f['envelope'](kid='alien'))
    def test_14_invalid_registry_signature(self):
        e=self.f['envelope']();e['signature_hex']='aa'*64;self.rejects(envelope=e)
    def test_15_modified_document(self):
        docs=copy.deepcopy(self.f['docs']);docs[0]['source_text']='DENY CAUSE A -> B';self.rejects(documents=docs)
    def test_16_signed_revocation_other_document(self):
        r=self.verify(revocation_events=[self.f['event']() ],minimum_event_sequence=1)
        self.assertEqual(r['revocation_events'][0]['subject_id'],'docB')
    def test_17_signed_revocation_current_document(self):
        self.rejects(revocation_events=[self.f['event']('docA')],minimum_event_sequence=1)
    def test_18_signing_key_revoked(self):
        self.rejects(revocation_events=[self.f['event']('new','KEY')],minimum_event_sequence=1)
    def test_19_revocation_bad_signature(self):
        e=self.f['event']();e['signature_hex']='00'*64;self.rejects(revocation_events=[e])
    def test_20_revocation_wrong_authority(self):
        f=self.f;self.rejects(revocation_events=[f['event'](key=f['old'],kid='old')])
    def test_21_replay_event_floor(self):
        self.rejects(revocation_events=[self.f['event']()],minimum_event_sequence=2)
    def test_22_no_events_but_floor_nonzero(self):self.rejects(minimum_event_sequence=1)
    def test_23_duplicate_event_id(self):
        f=self.f;self.rejects(revocation_events=[f['event'](),f['event'](seq=2)])
    def test_24_out_of_order_events(self):
        f=self.f;self.rejects(revocation_events=[f['event'](seq=3),f['event'](seq=2,event_id='evt2')])
    def test_25_cross_issuer_revocation(self):
        e=self.f['event']();e['payload']['issuer_id']='attacker';self.rejects(revocation_events=[e])
    def test_26_missing_external_policy(self):self.rejects(external_trust_policy={})
    def test_27_issuer_identity_not_claimed(self):
        r=self.verify();self.assertFalse(r['external_identity_verified']);self.assertFalse(r['external_truth_verified'])
    def test_28_no_execution_or_mutations(self):
        r=self.verify();self.assertFalse(r['autoload']);self.assertFalse(r['allowed_to_execute']);self.assertEqual(r['mutations'],[])
    def test_29_rotation_absent_with_pinned_old_key(self):
        f=self.f;r=self.verify(rotation=None,envelope=f['envelope'](key=f['old'],kid='old'))
        self.assertIsNone(r['rotation'])
    def test_30_unpinned_admin_invalid(self):
        p=copy.deepcopy(self.f['policy']);p['revocation_authority_keys']=['missing'];self.rejects(external_trust_policy=p)
    def test_31_multiple_independent_claims_not_truth(self):
        f=self.f;d=copy.deepcopy(f['docs'][0]);d['document_id']='docB';d['source_group']='groupB'
        digest=hashlib.sha256(d['source_text'].encode()).hexdigest()
        p=copy.deepcopy(f['payload']);p['registry']['entries'].append(dict(p['registry']['entries'][0], document_id='docB',source_group='groupB'))
        p['revisions'].append(dict(p['revisions'][0], revision_id='revB', document_id='docB'))
        r=self.verify(documents=[f['docs'][0],d],envelope=f['envelope'](p));self.assertFalse(r['external_truth_verified'])
    def test_32_cross_document_revision_edge(self):
        f=self.f;p=copy.deepcopy(f['payload']);p['revisions'].append(dict(p['revisions'][0],revision_id='revB',document_id='docB',parent_revisions=['rev1']))
        self.rejects(envelope=f['envelope'](p))
    def test_33_revision_fork_preserved(self):
        f=self.f;p=copy.deepcopy(f['payload']);p['revisions']+=[dict(p['revisions'][0],revision_id='rev2',parent_revisions=['rev1']),dict(p['revisions'][0],revision_id='rev3',parent_revisions=['rev1'])]
        r=self.verify(envelope=f['envelope'](p));self.assertEqual(r['revision_graph']['forks']['rev1'],['rev2','rev3'])
    def test_34_conflicting_source_status_preserved(self):
        f=self.f;p=copy.deepcopy(f['payload']);p['revisions']+=[dict(p['revisions'][0],revision_id='rev2',status='DISPUTED',parent_revisions=['rev1'])]
        r=self.verify(envelope=f['envelope'](p));self.assertTrue(r['revision_graph']['temporal_status_conflicts'])
    def test_35_cls_reference_not_executable(self):
        j=json.loads((BASE/'integrations'/'CLS_REFERENCE_INTERFACE_R08.json').read_text())
        self.assertFalse(j['autoload']);self.assertFalse(j['allowed_to_execute']);self.assertEqual(j['native_integration'],'PROPOSAL_ONLY_NOT_APPLIED')
    def test_36_malformed_empty_revocation_event_collection(self):
        self.rejects(revocation_events={})
    def test_37_rotation_claim_ambiguous(self):
        r=copy.deepcopy(self.f['rotation']);r['payload']['old_key_id']='new';self.rejects(rotation=r)

if __name__=='__main__':unittest.main()
