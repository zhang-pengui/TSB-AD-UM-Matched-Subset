"""Read-only release gate: payload integrity, provenance, and authorization are separate."""
import argparse
import csv
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath

ALLOWLIST = "manifests/release_allowlist.json"
AUTHORIZATION = "manifests/release_authorization.json"
REQUIRED_PERMISSIONS = ("original_scripts", "original_tests", "documentation", "mapping_csv",
                        "source_filename_hash_metadata", "frozen_statistics", "third_party_notices", "source_rights_scope")
SHA = re.compile(r"[0-9a-f]{64}")
CONTENT_CHECKS = {
    "PRIVATE_ABSOLUTE_WINDOWS_PATH": r"(?<![A-Za-z])[A-Za-z]:[\\/][A-Za-z0-9_\u4e00-\u9fff]",
    "PRIVATE_USER_DIRECTORY": r"(?:/Users/|/home/)[A-Za-z0-9_\u4e00-\u9fff]+/",
    "EMAIL_ADDRESS": r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
    "POSSIBLE_API_KEY": r"\b(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16})\b",
    "FAKE_PUBLIC_LINK": r"https?://(?:example\.(?:com|org)|[^\s/]*placeholder[^\s/]*)",
}

def file_hash(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def safe_relative(root, name):
    if not isinstance(name,str) or not name or "\\" in name: raise ValueError("Invalid relative path")
    rel=PurePosixPath(name)
    if rel.is_absolute() or ".." in rel.parts or any(":" in x for x in rel.parts): raise ValueError("Invalid relative path")
    path=root.joinpath(*rel.parts)
    if not path.resolve().is_relative_to(root.resolve()): raise ValueError("Path escapes package")
    return path

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def scope_digest(entries):
    material=[dict(path=r["path"],sha256=r["sha256"]) for r in entries
              if r["path"] not in {ALLOWLIST,AUTHORIZATION}]
    return hashlib.sha256(json.dumps(sorted(material,key=lambda r:r["path"]),sort_keys=True,separators=(",",":")).encode()).hexdigest()

def read_allowlist(root):
    data=load_json(root/ALLOWLIST);entries=data["files"]
    if data.get("schema_version")!=1 or not isinstance(entries,list) or not entries: raise ValueError("Invalid allowlist")
    names=[r["path"] for r in entries]
    if len(names)!=len(set(names)) or ALLOWLIST in names: raise ValueError("Duplicate/self-referential inventory")
    for r in entries:
        safe_relative(root,r["path"])
        if not SHA.fullmatch(r["sha256"]): raise ValueError("Invalid inventory digest")
    return entries

def generated_artifact(root,rel,allowed):
    p=PurePosixPath(rel)
    if "__pycache__" in p.parts:
        match=re.fullmatch(r"(.+)\.(?:cpython-\d+|pypy\d+)(?:\.opt-\d)?\.pyc",p.name)
        if match and (p.parent.parent/(match[1]+".py")).as_posix() in allowed:
            with (root/rel).open("rb") as f:header=f.read(16)
            if len(header)==16 and header[2:4]==b"\r\n" and int.from_bytes(header[4:8],"little") in {0,1,3}:
                return "BYTECODE_FOR_ALLOWLISTED_SOURCE"
    if rel.startswith(".pytest_cache/"):
        try:
            f=root/rel
            if f.stat().st_size<=128*1024:
                key=rel[len(".pytest_cache/"):];text=f.read_text(encoding="utf-8")
                if key=="README.md" and text.startswith("# pytest cache directory #"):return "KNOWN_PYTEST_METADATA"
                if key=="CACHEDIR.TAG" and text.startswith("Signature: 8a477f597d28d172789f06886806bc55"):return "KNOWN_PYTEST_METADATA"
                if key==".gitignore" and text.strip()=="# Created by pytest automatically.\n*":return "KNOWN_PYTEST_METADATA"
                if key in {"v/cache/nodeids","v/cache/lastfailed","v/cache/stepwise"}:
                    obj=json.loads(text)
                    if key=="v/cache/lastfailed" and isinstance(obj,dict) and all(isinstance(k,str) and isinstance(v,bool) for k,v in obj.items()):return "KNOWN_PYTEST_METADATA"
                    if key!="v/cache/lastfailed" and isinstance(obj,list) and all(isinstance(x,str) for x in obj):return "KNOWN_PYTEST_METADATA"
        except (ValueError,OSError):pass
    if rel in {"reports/cpu_tests.json","reports/release_scan.json"}:
        try:
            d=load_json(root/rel)
            if rel.endswith("cpu_tests.json") and d.get("command")=="python -B -m unittest discover -s tests -v" and isinstance(d.get("test_case_count"),int): return "CPU_TEST_RUN_REPORT"
            if rel.endswith("release_scan.json") and isinstance(d.get("scanned_files"),int) and isinstance(d.get("content_findings"),list): return "RELEASE_SCAN_RUN_REPORT"
        except (ValueError,OSError): pass
    if rel=="reports/cpu_tests.log":
        try:
            text=(root/rel).read_text(encoding="utf-8")
            if re.search(r"Ran \d+ tests? in",text) and ("\nOK" in text or "\nFAILED" in text): return "CPU_TEST_RUN_LOG"
        except (ValueError,OSError): pass
    return None

def content_findings(path,rel):
    found=[]
    if path.suffix.casefold() in {".zip",".pt",".pth",".ckpt",".npz",".npy",".pkl",".pickle"}: found.append(dict(file=rel,kind="RAW_ARCHIVE_CHECKPOINT_OR_BINARY_DATA"))
    if path.stat().st_size>5*1024*1024: return found+[dict(file=rel,kind="LARGE_FILE_REQUIRES_REVIEW")]
    try:text=path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError,OSError):return found+[dict(file=rel,kind="UNINSPECTED_BINARY")]
    for kind,pattern in CONTENT_CHECKS.items():
        if re.search(pattern,text):found.append(dict(file=rel,kind=kind))
    if path.suffix.casefold()==".csv":
        header=next(csv.reader(text.splitlines()),[])
        if any(x.casefold()=="label" for x in header) and any(x.casefold()=="data" for x in header):found.append(dict(file=rel,kind="POSSIBLE_RAW_SIGNAL_CSV"))
    if path.suffix in {".md",".json"} and re.search(r"\b(?:TODO|FIXME|TBD)\b",text):found.append(dict(file=rel,kind="UNRESOLVED_DRAFT_MARKER"))
    return found

def provenance_gate(root):
    blockers=[];warnings=[];level="UNKNOWN"
    try:
        d=load_json(root/"manifests/public_current_official_snapshot.json");level=d.get("evidence_level","UNKNOWN")
        if level not in {"LEVEL_1","LEVEL_2"}:blockers.append("SOURCE_EVIDENCE_LEVEL_UNSUPPORTED_OR_MISSING")
        if d.get("official_current_snapshot_verified") is not True:blockers.append("CURRENT_OFFICIAL_CONTENT_NOT_VERIFIED")
        with (root/"manifests/official_evaluation_verification.csv").open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
        counts={t:sum(r.get("track")==t for r in rows) for t in ["U","M"]}
        keys={(r.get("track"),r.get("eval_relative_path")) for r in rows}
        if counts!={"U":350,"M":180} or len(keys)!=530:blockers.append("OFFICIAL_EVALUATION_COVERAGE_INVALID")
        for r in rows:
            if (r.get("verification_status")!="EXACT_BYTE_MATCH" or r.get("official_file_sha256")!=r.get("local_file_sha256") or
                not SHA.fullmatch(r.get("official_file_sha256","")) or any(r.get(k)!="True" for k in ["byte_identical","signal_identical","label_identical","boundary_identical"])):
                blockers.append("ACTUAL_OFFICIAL_CONTENT_MISMATCH");break
        if d.get("by_track")!={"U":{"EXACT_BYTE_MATCH":350},"M":{"EXACT_BYTE_MATCH":180}}:blockers.append("SOURCE_SUMMARY_DETAIL_CONFLICT")
        if level=="LEVEL_1":
            # A changed status string is not historical evidence. LEVEL 1 needs
            # separately reviewed, hash-bound evidence for both archive tracks.
            history=d.get("historical_evidence",{})
            valid=d.get("historical_download_archive_identity")=="VERIFIED"
            for track in ("U","M"):
                record=history.get(track,{}) if isinstance(history,dict) else {}
                try:
                    evidence=safe_relative(root,record.get("evidence_file"))
                    valid=valid and record.get("review_status")=="VERIFIED" and bool(record.get("upstream_checksum_url")) and SHA.fullmatch(record.get("archive_sha256","")) is not None and SHA.fullmatch(record.get("evidence_sha256","")) is not None and evidence.is_file() and file_hash(evidence)==record["evidence_sha256"]
                except (ValueError,OSError,TypeError):valid=False
            if not valid:blockers.append("UNSUPPORTED_LEVEL_1_CLAIM")
        if level=="LEVEL_2":
            warnings.append("HISTORICAL_ARCHIVE_IDENTITY_LIMITATION_DISCLOSED")
            text=(root/"DATA_SOURCES.md").read_text(encoding="utf-8").lower()
            if "level 2" not in text or "historical" not in text or "unverified" not in text:blockers.append("LEVEL_2_LIMITATION_NOT_DISCLOSED")
    except (ValueError,OSError,KeyError,TypeError):blockers.append("SOURCE_EVIDENCE_MISSING_OR_UNREADABLE")
    return dict(level=level,status="PASS_WITH_LIMITATIONS" if not blockers and warnings else "PASS" if not blockers else "FAIL",blockers=blockers,warnings=warnings)

def verified_record(evidence_root,record,digest):
    """Check a private, explicitly supplied review store, not the public allowlist."""
    if not isinstance(record,dict) or record.get("status")!="VERIFIED" or record.get("scope_sha256")!=digest:return False
    ref=record.get("evidence_file")
    try:
        f=safe_relative(evidence_root,ref)
        return f.is_file() and not f.is_symlink() and SHA.fullmatch(record.get("evidence_sha256","")) is not None and file_hash(f)==record["evidence_sha256"]
    except (ValueError,OSError,TypeError):return False

def authorization_gate(root,entries,authorization_root=None):
    blockers=[];digest=scope_digest(entries)
    try:
        public=load_json(root/AUTHORIZATION)
        if not isinstance(public,dict):raise ValueError("Invalid public summary")
        if public.get("schema_version")!=2:raise ValueError("Unsupported public summary")
        if public.get("public_release_approved") is not True:blockers.append("PUBLIC_RELEASE_NOT_APPROVED")
        if authorization_root is None:
            return dict(status="PENDING_OR_UNVERIFIED",blockers=blockers+["INTERNAL_AUTHORIZATION_REVIEW_NOT_PROVIDED"],scope_sha256=digest,
                verification_limit="Private approval evidence is not distributed. A local author must provide an external review store and perform final human review.")
        evidence_root=Path(authorization_root).resolve()
        if evidence_root.is_relative_to(root.resolve()) or root.resolve().is_relative_to(evidence_root):
            raise ValueError("Review store must be separate from public package")
        d=load_json(evidence_root/"authorization_review.json")
        if not isinstance(d,dict):raise ValueError("Invalid internal review")
        if d.get("schema_version")!=2 or d.get("scope_sha256")!=digest:blockers.append("INTERNAL_REVIEW_SCOPE_MISMATCH")
        if not verified_record(evidence_root,d.get("publication_approval"),digest):blockers.append("AUTHOR_PUBLICATION_APPROVAL_NOT_VERIFIED")
        manual=d.get("manual_release_review",{})
        if not isinstance(manual,dict):manual={}
        if not (verified_record(evidence_root,manual,digest) and manual.get("reviewed_by") and manual.get("reviewed_at")):
            blockers.append("FINAL_HUMAN_RELEASE_REVIEW_NOT_VERIFIED")
        permissions=d.get("component_permissions",{})
        for key in REQUIRED_PERMISSIONS:
            if not verified_record(evidence_root,permissions.get(key),digest):blockers.append("PERMISSION_NOT_VERIFIED:"+key)
    except (ValueError,OSError,KeyError,TypeError):blockers.append("AUTHORIZATION_RECORD_MISSING_OR_UNREADABLE")
    return dict(status="VERIFIED_RECORDS_PRESENT" if not blockers else "PENDING_OR_UNVERIFIED",blockers=blockers,scope_sha256=digest,
                private_evidence_distributed=False,
                verification_limit="Checks private evidence files, scope binding, hashes and an explicit human-review record; cannot establish rights-holder identity, legal sufficiency or authenticity of approval")

def scan(root,authorization_root=None):
    root=Path(root).resolve();findings=[];excluded=[];payload=[];blockers=[]
    try:entries=read_allowlist(root)
    except (ValueError,OSError,KeyError,TypeError):entries=[];blockers.append("RELEASE_ALLOWLIST_MISSING_OR_INVALID")
    allowed={r["path"]:r for r in entries}
    for base,dirs,files in os.walk(root,followlinks=False):
        base=Path(base)
        if base==root and ".git" in dirs:dirs.remove(".git");excluded.append(dict(path=".git/",reason="GIT_METADATA_NOT_PUBLISH_PAYLOAD"))
        for dirname in list(dirs):
            if (base/dirname).is_symlink():findings.append(dict(file=(base/dirname).relative_to(root).as_posix(),kind="SYMLINK_REQUIRES_REVIEW"));dirs.remove(dirname)
        for name in sorted(files):
            f=base/name;rel=f.relative_to(root).as_posix()
            if rel==".git":excluded.append(dict(path=rel,reason="GIT_WORKTREE_METADATA"));continue
            if f.is_symlink():findings.append(dict(file=rel,kind="SYMLINK_REQUIRES_REVIEW"));continue
            ignored=generated_artifact(root,rel,allowed) if rel not in allowed else None
            if ignored:
                excluded.append(dict(path=rel,reason=ignored))
                if not rel.endswith(".pyc"):findings.extend(content_findings(f,rel))
                continue
            payload.append(rel)
            if rel not in allowed and rel!=ALLOWLIST:findings.append(dict(file=rel,kind="UNKNOWN_PAYLOAD_FILE_REQUIRES_REVIEW"))
            findings.extend(content_findings(f,rel))
    for rel,r in allowed.items():
        try:
            f=safe_relative(root,rel)
            if not f.is_file():findings.append(dict(file=rel,kind="ALLOWLISTED_FILE_MISSING"))
            elif file_hash(f)!=r["sha256"]:findings.append(dict(file=rel,kind="PAYLOAD_HASH_MISMATCH"))
        except (ValueError,OSError):findings.append(dict(file=rel,kind="ALLOWLISTED_FILE_INVALID"))
    source=provenance_gate(root);auth=authorization_gate(root,entries,authorization_root)
    blockers+=source["blockers"]+auth["blockers"]
    status="NOT_READY" if findings or blockers else "READY_WITH_LIMITATIONS" if source["warnings"] else "READY"
    return dict(status=status,scanned_files=len(payload),scanned_payload_files=len(payload),payload_files=sorted(payload),excluded_nonpayload=excluded,
                scan_ignores_gitignore=False,content_findings=findings,release_blockers=blockers,provenance=source,authorization=auth,
                manual_checks=["Only the explicit payload inventory is eligible for publication; Git, cache and validated run artifacts are not payload",
                               "LEVEL 2 with disclosed historical limits is not an authorization decision",
                               "Hash-bound records do not independently authenticate human/legal authority; no permission is inferred from public availability"])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument("--output",type=Path)
    p.add_argument("--authorization-root",type=Path,help="Optional private local review directory OUTSIDE the public package; never copied or printed")
    a=p.parse_args();result=scan(a.root,a.authorization_root)
    if a.output:
        if not a.output.resolve().is_relative_to(a.root.resolve()):p.error("Output must remain inside package root")
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result["status"] in {"READY","READY_WITH_LIMITATIONS"} else 2

if __name__=="__main__":raise SystemExit(main())
