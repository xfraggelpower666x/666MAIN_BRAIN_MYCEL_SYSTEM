"""Deterministic read-only regression checks for 666CLS reconstruction contract adapter."""
import copy, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"runtime"))
from reconstruction_adapter import plan,catalogue

def request(profile="lyrics-fulltext-v1.1.0", operation="RECONSTRUCT"):
    ver=catalogue()["profiles"]
    p=next(x for x in ver if x["id"]==profile)
    return {"request_id":"test","target":{"profile_id":profile,"profile_version":p["version"],"operation":operation},
        "authority":{"cls_system_id":"666CLS-CORE-001","foreign_execution":False},
        "execution":{"mode":"DRY_RUN","approved_by_native_owner":False},
        "language":{},"constraints":{"allow_source_merge":False},
        "sources":[{"source_id":"s1","source_type":"LYRICS","source_ref":"local:s1","language":"de"}]}

class AdapterContractTests(unittest.TestCase):
    def test_catalogue(self):
        self.assertEqual(len(catalogue()["profiles"]),3)
    def test_never_execute(self):
        for profile in catalogue()["profiles"]:
            r=plan(request(profile["id"]))
            self.assertFalse(r["execution_performed"])
            self.assertEqual(r["mutations"],[])
    def test_english_v11(self):
        self.assertEqual(plan(request())["plan"]["target_language"],"en")
    def test_german_v154(self):
        self.assertEqual(plan(request("lyrik-reconstruction-v1.5.4"))["plan"]["target_language"],"de")
    def test_source_preserve_clean(self):
        self.assertEqual(plan(request("english-fulltext-v1.0.0","CLEAN"))["plan"]["target_language"],"de")
    def test_explicit_language(self):
        r=request();r["language"]["explicit_target"]="de"
        self.assertEqual(plan(r)["plan"]["target_language"],"de")
    def test_inert_source(self):
        r=request();r["sources"][0]["source_type"]="SYSTEM_CONFIG"
        self.assertEqual(plan(r)["status"],"HOLD")
    def test_unapproved_merge(self):
        r=request("english-fulltext-v1.0.0","MERGE")
        r["sources"].append({"source_id":"s2","source_type":"PROSE","source_ref":"local:s2"})
        self.assertEqual(plan(r)["status"],"HOLD")
        r["constraints"]["allow_source_merge"]=True
        self.assertEqual(plan(r)["status"],"READY_FOR_OWNER_REVIEW")
    def test_no_foreign_execution(self):
        r=request();r["authority"]["foreign_execution"]=True
        self.assertEqual(plan(r)["status"],"HOLD")
    def test_no_raw_text(self):
        r=request();r["sources"][0]["source_text"]="private"
        self.assertEqual(plan(r)["status"],"HOLD")
    def test_no_fake_verified_source(self):
        r=request();r["sources"][0]["integrity_status"]="VERIFIED"
        self.assertEqual(plan(r)["status"],"HOLD")
    def test_mantra_scope(self):
        r=request("english-fulltext-v1.0.0");r["constraints"]["active_mantra_id"]="neon"
        r["constraints"]["mantra_source_authorized"]=True
        self.assertEqual(plan(r)["status"],"HOLD")
    def test_wrong_version(self):
        r=request();r["target"]["profile_version"]="1.1.1"
        self.assertEqual(plan(r)["status"],"HOLD")
    def test_unknown_profile(self):
        r=request();r["target"]["profile_id"]="unknown"
        self.assertEqual(plan(r)["status"],"HOLD")
    def test_unknown_operation(self):
        r=request();r["target"]["operation"]="CLEAN"
        self.assertEqual(plan(r)["status"],"HOLD")
    def test_unapproved_creativity(self):
        r=request();r["constraints"]["allow_new_story_events"]=True
        self.assertEqual(plan(r)["status"],"HOLD")

if __name__=="__main__": unittest.main()

class AdapterHardeningTests(unittest.TestCase):
    def test_invalid_nested_containers_return_hold(self):
        for key in ("target","authority","execution","language","constraints"):
            for value in (42, "invalid", ["invalid"]):
                with self.subTest(key=key, value=value):
                    r=request();r[key]=value
                    result=plan(r)
                    self.assertEqual(result["status"],"HOLD")
                    self.assertFalse(result["execution_performed"])
    def test_unhashable_source_type_returns_hold(self):
        for value in ([], {}, ["LYRICS"]):
            with self.subTest(value=value):
                r=request();r["sources"][0]["source_type"]=value
                self.assertEqual(plan(r)["status"],"HOLD")
    def test_unhashable_source_language_returns_hold(self):
        for value in ([], {}, ["de"]):
            with self.subTest(value=value):
                r=request("lyrik-reconstruction-v1.5.4");r["sources"][0]["language"]=value
                self.assertEqual(plan(r)["status"],"HOLD")
    def test_unhashable_target_language_returns_hold(self):
        for value in ([], {}, ["en"]):
            with self.subTest(value=value):
                r=request();r["language"]["explicit_target"]=value
                self.assertEqual(plan(r)["status"],"HOLD")
    def test_missing_native_readback_returns_hold(self):
        from unittest.mock import patch
        with patch("reconstruction_adapter.rehydrate", side_effect=ValueError("broken current")):
            result=plan(request())
            self.assertEqual(result["unresolved"],["NATIVE_CURRENT_READBACK_FAILED"])
            self.assertEqual(result["mutations"],[])
    def test_wrong_native_identity_returns_hold(self):
        from unittest.mock import patch
        with patch("reconstruction_adapter.rehydrate", return_value={"status":"VERIFIZIERT","system_id":"FOREIGN"}):
            self.assertEqual(plan(request())["unresolved"],["NATIVE_CURRENT_UNVERIFIED"])
    def test_native_readback_called_for_each_plan(self):
        from unittest.mock import patch
        with patch("reconstruction_adapter.rehydrate", return_value={"status":"VERIFIZIERT","system_id":"666CLS-CORE-001"}) as mock:
            self.assertEqual(plan(request())["status"],"READY_FOR_OWNER_REVIEW")
            self.assertEqual(mock.call_count,1)
    def test_rejects_bad_profile_schema(self):
        from unittest.mock import patch
        valid_request=request()
        with patch("reconstruction_adapter.PROFILE_FILE") as mocked:
            mocked.read_text.return_value='{"schema":"WRONG","profiles":{}}'
            self.assertEqual(plan(valid_request)["unresolved"],["PROFILE_REGISTRY_INVALID"])
