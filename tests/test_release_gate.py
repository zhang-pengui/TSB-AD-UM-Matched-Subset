"""Synthetic release-policy fixtures are not real approval or provenance evidence."""
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

PACKAGE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("release_gate_under_test",PACKAGE/"scripts/check_release.py")
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="gate_fixture_",dir=PACKAGE/"tests")
        self.root=Path(self.temp.name)/"package";self.root.mkdir()
        self.evidence_root=Path(self.temp.name)/"private_review";self.evidence_root.mkdir()
        self.write("scripts/sample.py","pass\n")
        self.write("DATA_SOURCES.md","LEVEL 2: historical archive identity is unverified.\n")
        (self.evidence_root/"approval_test_fixture.txt").write_text("SYNTHETIC TEST FIXTURE ONLY; NOT AUTHOR APPROVAL.\n",encoding="utf-8")
        self.snapshot=dict(evidence_level="LEVEL_2",official_current_snapshot_verified=True,
                           historical_download_archive_identity="NOT_VERIFIED",
                           by_track={"U":{"EXACT_BYTE_MATCH":350},"M":{"EXACT_BYTE_MATCH":180}})
        self.source_rows=[]
        for track,n in (("U",350),("M",180)):
            for i in range(n):
                self.source_rows.append(dict(track=track,eval_relative_path=f"{track}_{i}.csv",
                    official_file_sha256="1"*64,local_file_sha256="1"*64,
                    verification_status="EXACT_BYTE_MATCH",byte_identical="True",signal_identical="True",
                    label_identical="True",boundary_identical="True"))
        self.save_sources()
        self.json(gate.AUTHORIZATION,dict(schema_version=2,public_release_approved=False))
        self.private_json(dict(schema_version=2,publication_approval=dict(status="PENDING"),component_permissions={}))
        self.inventory()
    def tearDown(self):self.temp.cleanup()
    def write(self,rel,text):
        p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding="utf-8")
    def json(self,rel,value):self.write(rel,json.dumps(value,indent=2)+"\n")
    def private_json(self,value):
        (self.evidence_root/"authorization_review.json").write_text(json.dumps(value)+"\n",encoding="utf-8")
    def save_sources(self):
        self.json("manifests/public_current_official_snapshot.json",self.snapshot)
        p=self.root/"manifests/official_evaluation_verification.csv";p.parent.mkdir(exist_ok=True)
        with p.open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(self.source_rows[0]));w.writeheader();w.writerows(self.source_rows)
    def inventory(self):
        self.entries=[dict(path=p.relative_to(self.root).as_posix(),sha256=gate.file_hash(p))
                      for p in sorted(self.root.rglob("*")) if p.is_file() and p.relative_to(self.root).as_posix()!=gate.ALLOWLIST]
        self.json(gate.ALLOWLIST,dict(schema_version=1,files=self.entries))
    def approve_fixture(self):
        self.json(gate.AUTHORIZATION,dict(schema_version=2,public_release_approved=True))
        self.inventory()
        record=dict(status="VERIFIED",scope_sha256=gate.scope_digest(self.entries),
                    evidence_file="approval_test_fixture.txt",evidence_sha256=gate.file_hash(self.evidence_root/"approval_test_fixture.txt"))
        self.private_json(dict(schema_version=2,scope_sha256=gate.scope_digest(self.entries),publication_approval=record,
            manual_release_review=dict(**record,reviewed_by="SYNTHETIC REVIEWER",reviewed_at="SYNTHETIC TIME"),component_permissions={k:record for k in gate.REQUIRED_PERMISSIONS}))
    def scan(self):return gate.scan(self.root,authorization_root=self.evidence_root)
    def kinds(self):return {x["kind"] for x in self.scan()["content_findings"]}
    def test_level2_without_authorization_remains_not_ready(self):
        r=self.scan();self.assertEqual(r["status"],"NOT_READY");self.assertEqual(r["provenance"]["status"],"PASS_WITH_LIMITATIONS")
        self.assertIn("AUTHOR_PUBLICATION_APPROVAL_NOT_VERIFIED",r["release_blockers"])
    def test_level2_verified_synthetic_records_reaches_next_gate(self):
        self.approve_fixture();r=self.scan();self.assertEqual(r["status"],"READY_WITH_LIMITATIONS");self.assertEqual(r["content_findings"],[])
    def test_actual_content_mismatch_blocks_even_reinventoried(self):
        self.source_rows[0]["local_file_sha256"]="2"*64;self.save_sources();self.approve_fixture()
        r=self.scan();self.assertEqual(r["status"],"NOT_READY");self.assertIn("ACTUAL_OFFICIAL_CONTENT_MISMATCH",r["release_blockers"])
    def test_source_evidence_missing_blocks(self):
        (self.root/"manifests/public_current_official_snapshot.json").unlink()
        self.assertIn("SOURCE_EVIDENCE_MISSING_OR_UNREADABLE",self.scan()["release_blockers"])
    def test_level1_cannot_be_claimed_by_status_string(self):
        self.snapshot.update(evidence_level="LEVEL_1",historical_download_archive_identity="VERIFIED")
        self.save_sources();self.approve_fixture();self.assertIn("UNSUPPORTED_LEVEL_1_CLAIM",self.scan()["release_blockers"])
    def test_duplicate_source_identity_blocks(self):
        self.source_rows[1]["eval_relative_path"]=self.source_rows[0]["eval_relative_path"]
        self.save_sources();self.approve_fixture();self.assertIn("OFFICIAL_EVALUATION_COVERAGE_INVALID",self.scan()["release_blockers"])
    def test_level2_disclosure_required(self):
        self.write("DATA_SOURCES.md","Current contents verified.\n");self.approve_fixture()
        self.assertIn("LEVEL_2_LIMITATION_NOT_DISCLOSED",self.scan()["release_blockers"])
    def test_git_metadata_is_not_payload(self):
        p=self.root/".git/objects/ab/object";p.parent.mkdir(parents=True);p.write_bytes(bytes([255,0,1]))
        self.approve_fixture_without_new_inventory()
        r=self.scan();self.assertFalse(any(x["file"].startswith(".git/") for x in r["content_findings"]))
        self.assertTrue(any(x["reason"]=="GIT_METADATA_NOT_PUBLISH_PAYLOAD" for x in r["excluded_nonpayload"]))
    def approve_fixture_without_new_inventory(self):
        # Existing payload inventory is deliberately retained for unknown-file tests.
        self.json(gate.AUTHORIZATION,dict(schema_version=2,public_release_approved=True))
        for entry in self.entries:
            if entry["path"]==gate.AUTHORIZATION:entry["sha256"]=gate.file_hash(self.root/gate.AUTHORIZATION)
        self.json(gate.ALLOWLIST,dict(schema_version=1,files=self.entries))
        record=dict(status="VERIFIED",scope_sha256=gate.scope_digest(self.entries),evidence_file="approval_test_fixture.txt",evidence_sha256=gate.file_hash(self.evidence_root/"approval_test_fixture.txt"))
        self.private_json(dict(schema_version=2,scope_sha256=gate.scope_digest(self.entries),publication_approval=record,
            manual_release_review=dict(**record,reviewed_by="SYNTHETIC REVIEWER",reviewed_at="SYNTHETIC TIME"),component_permissions={k:record for k in gate.REQUIRED_PERMISSIONS}))
    def test_known_bytecode_excluded(self):
        import importlib.util
        import marshal
        p=self.root/"scripts/__pycache__/sample.cpython-312.pyc";p.parent.mkdir()
        p.write_bytes(importlib.util.MAGIC_NUMBER+b"\0"*12+marshal.dumps(compile("pass","sample.py","exec")))
        self.assertNotIn("UNINSPECTED_BINARY",self.kinds())
        self.assertEqual(len(self.scan()["excluded_nonpayload"]),1)
    def test_misnamed_binary_is_not_recognized_bytecode(self):
        p=self.root/"scripts/__pycache__/sample.cpython-312.pyc";p.parent.mkdir();p.write_bytes(b"PK not a bytecode cache")
        self.assertIn("UNKNOWN_PAYLOAD_FILE_REQUIRES_REVIEW",self.kinds())
    def test_unknown_checkpoint_in_cache_rejected(self):
        p=self.root/"scripts/__pycache__/model.pt";p.parent.mkdir();p.write_bytes(b"checkpoint")
        self.assertIn("RAW_ARCHIVE_CHECKPOINT_OR_BINARY_DATA",self.kinds());self.assertIn("UNKNOWN_PAYLOAD_FILE_REQUIRES_REVIEW",self.kinds())
    def test_known_pytest_metadata_excluded(self):
        self.write(".pytest_cache/v/cache/nodeids","[]");self.assertEqual(self.scan()["content_findings"],[])
    def test_unknown_pytest_file_rejected(self):
        self.write(".pytest_cache/private.csv","data,label\n1,0\n");self.assertIn("POSSIBLE_RAW_SIGNAL_CSV",self.kinds())
    def test_pytest_known_name_requires_recognized_content(self):
        self.write(".pytest_cache/v/cache/nodeids","not pytest JSON\n")
        self.assertIn("UNKNOWN_PAYLOAD_FILE_REQUIRES_REVIEW",self.kinds())
    def test_generated_run_reports_excluded(self):
        self.json("reports/cpu_tests.json",dict(command="python -B -m unittest discover -s tests -v",test_case_count=34))
        self.json("reports/release_scan.json",dict(scanned_files=5,content_findings=[]))
        self.write("reports/cpu_tests.log","Ran 34 tests in 0.5s\n\nOK\n")
        self.assertEqual(len(self.scan()["excluded_nonpayload"]),3);self.assertEqual(self.scan()["content_findings"],[])
    def test_unknown_log_rejected(self):
        self.write("reports/private.log","private run\n");self.assertIn("UNKNOWN_PAYLOAD_FILE_REQUIRES_REVIEW",self.kinds())
    def test_known_cache_still_checked_for_sensitive_text(self):
        self.write(".pytest_cache/README.md","# pytest cache directory #\nContact "+"private"+"@"+"mail.test")
        self.assertIn("EMAIL_ADDRESS",self.kinds())
    def test_gitignore_does_not_hide_unknown_payload(self):
        self.write(".gitignore","*.csv\n");self.write("hidden.csv","data,label\n1,0\n")
        self.assertIn("UNKNOWN_PAYLOAD_FILE_REQUIRES_REVIEW",self.kinds());self.assertIn("POSSIBLE_RAW_SIGNAL_CSV",self.kinds())
    def test_missing_allowlist_blocks(self):
        (self.root/gate.ALLOWLIST).unlink();self.assertIn("RELEASE_ALLOWLIST_MISSING_OR_INVALID",self.scan()["release_blockers"])
    def test_changed_payload_hash_blocks(self):
        self.write("scripts/sample.py","pass\npass\n");self.assertIn("PAYLOAD_HASH_MISMATCH",self.kinds())
    def test_missing_payload_blocks(self):
        (self.root/"scripts/sample.py").unlink();self.assertIn("ALLOWLISTED_FILE_MISSING",self.kinds())
    def test_allowlist_path_traversal_rejected(self):
        self.entries[0]["path"]="../outside.txt";self.json(gate.ALLOWLIST,dict(schema_version=1,files=self.entries))
        self.assertIn("RELEASE_ALLOWLIST_MISSING_OR_INVALID",self.scan()["release_blockers"])
    def test_duplicate_allowlist_entry_rejected(self):
        self.entries.append(self.entries[0]);self.json(gate.ALLOWLIST,dict(schema_version=1,files=self.entries))
        self.assertIn("RELEASE_ALLOWLIST_MISSING_OR_INVALID",self.scan()["release_blockers"])
    def test_invalid_allowlist_json_rejected(self):
        self.write(gate.ALLOWLIST,"{");self.assertIn("RELEASE_ALLOWLIST_MISSING_OR_INVALID",self.scan()["release_blockers"])
    def test_approval_status_without_evidence_not_sufficient(self):
        self.private_json(dict(schema_version=2,publication_approval=dict(status="VERIFIED"),component_permissions={}))
        self.inventory();self.assertIn("AUTHOR_PUBLICATION_APPROVAL_NOT_VERIFIED",self.scan()["release_blockers"])
    def test_approval_scope_mismatch_rejected(self):
        self.approve_fixture();d=gate.load_json(self.evidence_root/"authorization_review.json");d["publication_approval"]["scope_sha256"]="0"*64
        self.private_json(d);self.assertIn("AUTHOR_PUBLICATION_APPROVAL_NOT_VERIFIED",self.scan()["release_blockers"])
    def test_approval_evidence_hash_mismatch_rejected(self):
        self.approve_fixture();(self.evidence_root/"approval_test_fixture.txt").write_text("Different synthetic fixture.\n",encoding="utf-8")
        self.assertIn("AUTHOR_PUBLICATION_APPROVAL_NOT_VERIFIED",self.scan()["release_blockers"])
    def test_actual_candidate_is_not_authorized(self):
        d=gate.load_json(PACKAGE/gate.AUTHORIZATION)
        self.assertFalse(d["public_release_approved"])
        self.assertNotEqual(d["status"],"VERIFIED")
    def test_private_evidence_is_not_public_payload(self):
        self.approve_fixture();r=self.scan()
        self.assertEqual(r["status"],"READY_WITH_LIMITATIONS")
        self.assertNotIn("approval_test_fixture.txt",r["payload_files"])
        self.assertNotIn("SYNTHETIC REVIEWER",json.dumps(r))
    def test_external_review_not_implicitly_read(self):
        self.approve_fixture();r=gate.scan(self.root)
        self.assertEqual(r["status"],"NOT_READY");self.assertIn("INTERNAL_AUTHORIZATION_REVIEW_NOT_PROVIDED",r["release_blockers"])
    def test_review_store_inside_public_package_rejected(self):
        self.approve_fixture();r=gate.scan(self.root,authorization_root=self.root/"private_review")
        self.assertIn("AUTHORIZATION_RECORD_MISSING_OR_UNREADABLE",r["release_blockers"])
    def test_review_store_parent_of_package_rejected(self):
        self.approve_fixture();r=gate.scan(self.root,authorization_root=self.root.parent)
        self.assertIn("AUTHORIZATION_RECORD_MISSING_OR_UNREADABLE",r["release_blockers"])
    def test_public_status_without_private_evidence_fails(self):
        self.json(gate.AUTHORIZATION,dict(schema_version=2,public_release_approved=True));self.inventory()
        self.assertEqual(self.scan()["status"],"NOT_READY")
    def test_public_approval_string_is_not_boolean_approval(self):
        self.approve_fixture();self.json(gate.AUTHORIZATION,dict(schema_version=2,public_release_approved="YES"));self.inventory()
        self.assertIn("PUBLIC_RELEASE_NOT_APPROVED",self.scan()["release_blockers"])
    def test_manual_release_review_required(self):
        self.approve_fixture();d=gate.load_json(self.evidence_root/"authorization_review.json");d.pop("manual_release_review")
        self.private_json(d);self.assertIn("FINAL_HUMAN_RELEASE_REVIEW_NOT_VERIFIED",self.scan()["release_blockers"])
    def test_internal_review_scope_must_match(self):
        self.approve_fixture();d=gate.load_json(self.evidence_root/"authorization_review.json");d["scope_sha256"]="0"*64
        self.private_json(d);self.assertIn("INTERNAL_REVIEW_SCOPE_MISMATCH",self.scan()["release_blockers"])
    def test_pending_public_approval_cannot_be_overridden(self):
        self.approve_fixture();self.json(gate.AUTHORIZATION,dict(schema_version=2,public_release_approved=False));self.inventory()
        self.assertIn("PUBLIC_RELEASE_NOT_APPROVED",self.scan()["release_blockers"])
    def test_internal_evidence_path_traversal_rejected(self):
        self.approve_fixture();d=gate.load_json(self.evidence_root/"authorization_review.json");d["publication_approval"]["evidence_file"]="../not_allowed.txt"
        self.private_json(d);self.assertIn("AUTHOR_PUBLICATION_APPROVAL_NOT_VERIFIED",self.scan()["release_blockers"])
    def test_license_choice_is_not_release_permission(self):
        self.approve_fixture();d=gate.load_json(self.evidence_root/"authorization_review.json");d["component_permissions"]["original_scripts"]["status"]="LICENSE_CHOICE_DECIDED"
        self.private_json(d);self.assertIn("PERMISSION_NOT_VERIFIED:original_scripts",self.scan()["release_blockers"])
    def test_invalid_private_review_json_fails_closed(self):
        self.approve_fixture();(self.evidence_root/"authorization_review.json").write_text("[]",encoding="utf-8")
        self.assertEqual(self.scan()["status"],"NOT_READY")
    def test_mit_scope_covers_only_present_python(self):
        d=gate.load_json(PACKAGE/"manifests/code_license_scope.json")
        actual={p.relative_to(PACKAGE).as_posix() for folder in ["scripts","tests"] for p in (PACKAGE/folder).glob("*.py")}
        self.assertEqual({r["path"] for r in d["files"]},actual)
        self.assertEqual(d["copyright_holder"],"Peng Zhang");self.assertEqual(d["license"],"MIT")
        self.assertEqual(d["copyright_year"],2026)
        self.assertTrue(all(gate.file_hash(PACKAGE/r["path"])==r["sha256"] for r in d["files"]))
    def test_mit_does_not_assign_noncode_license(self):
        d=gate.load_json(PACKAGE/"manifests/code_license_scope.json")
        self.assertFalse(d["public_release_approved"])
        self.assertIn("Copyright (c) 2026 Peng Zhang",(PACKAGE/"LICENSES/MIT.txt").read_text(encoding="utf-8"))
        self.assertTrue(all(r["path"].endswith(".py") for r in d["files"]))
    def test_clean_test_runner_creates_output_directory(self):
        import shutil
        import subprocess
        import sys
        fixture=Path(self.temp.name)/"clean_run"; (fixture/"scripts").mkdir(parents=True);(fixture/"tests").mkdir()
        shutil.copyfile(PACKAGE/"scripts/run_cpu_tests.py",fixture/"scripts/run_cpu_tests.py")
        (fixture/"tests/test_stub.py").write_text("import unittest\nclass Stub(unittest.TestCase):\n    def test_ok(self): self.assertTrue(True)\n",encoding="utf-8")
        p=subprocess.run([sys.executable,"-B",str(fixture/"scripts/run_cpu_tests.py")],capture_output=True,text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=="win32" else 0)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(gate.load_json(fixture/"reports/cpu_tests.json")["test_case_count"],1)

if __name__=="__main__":unittest.main()
