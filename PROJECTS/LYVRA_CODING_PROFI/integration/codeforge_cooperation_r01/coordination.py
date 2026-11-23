"""Evidence-bound LYVRA Coding Profi peer coordination. Does not execute or grant permissions."""
from dataclasses import dataclass, asdict
from typing import Literal
import json
import re
FAMILIES=frozenset({"CODING_PROFI","666CLIC","666DEV","666MAIN_BRAIN","LYVRA","666PFS","666STREAM"})
STATES=frozenset({"SOURCE_VERIFIED","READBACK_PENDING","CONFLICT_QUARANTINE"})
SHA40=re.compile(r"^[a-f0-9]{40}$")
@dataclass(frozen=True)
class SourceReceipt:
    family: str
    repository: str | None
    branch: str | None
    commit: str | None
    status: str
    readback: bool
    def validate(self):
        if self.family not in FAMILIES: raise ValueError("unknown native family")
        if self.status not in STATES: raise ValueError("unknown source status")
        if self.readback and (not self.repository or not self.branch or not self.commit or not SHA40.fullmatch(self.commit)):
            raise ValueError("incomplete source readback")
        if self.status == "SOURCE_VERIFIED" and not self.readback:
            raise ValueError("unread source cannot be verified")
@dataclass(frozen=True)
class WorkOffer:
    offer_id: str
    coordinator: Literal["CODING_PROFI"]
    native_owner: str
    source: SourceReceipt
    target_paths: tuple[str,...]
    goal: str
    mode: Literal["READ_ONLY","PATCH_PROPOSAL"]
    user_write_authorization: bool=False
    def validate(self):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,79}",self.offer_id): raise ValueError("invalid offer id")
        if self.coordinator != "CODING_PROFI": raise ValueError("wrong coordinator")
        if self.native_owner not in FAMILIES: raise ValueError("unknown native owner")
        self.source.validate()
        if self.source.family != self.native_owner: raise ValueError("owner/source mismatch")
        if not self.goal.strip() or not self.target_paths: raise ValueError("missing goal or paths")
        for path in self.target_paths:
            if not path or path.startswith("/") or chr(92) in path or ".." in path.split("/") or any(ord(ch) in (0, 10, 13) for ch in path):
                raise ValueError("unsafe relative path")
        if self.mode not in ("READ_ONLY","PATCH_PROPOSAL"): raise ValueError("mode not supported")
        if self.user_write_authorization: raise ValueError("offers cannot confer write authorization")
    def decision(self):
        self.validate()
        return "READY_FOR_READ_ONLY_COORDINATION" if self.source.status=="SOURCE_VERIFIED" else self.source.status
    def to_json(self):
        return json.dumps({**asdict(self),"target_paths":list(self.target_paths)},ensure_ascii=False,indent=2)
def coordination_summary(offers):
    seen=set()
    result=[]
    for offer in offers:
        if offer.offer_id in seen: raise ValueError("duplicate offer")
        seen.add(offer.offer_id)
        result.append({"offer_id":offer.offer_id,"native_owner":offer.native_owner,"decision":offer.decision(),"host_execution":"NOT_PROVEN","write_permitted":False})
    return {"lead":"CODING_PROFI","native_authority_override":False,"external_writes":False,"offers":result}
