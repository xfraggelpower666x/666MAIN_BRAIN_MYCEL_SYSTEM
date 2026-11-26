// KAIRON R17/R18: read-only evidence classification, no dispatch.
function diagnose(input) {
 if(!input||input.system_id!=="666TDI-001"||input.active_namespace!=="KAIRON")return {status:"READBACK_PENDING",reason:"CONTEXT_NOT_BOUND",mutation:false};
 if(input.direct!==true||!["FUCK HORST","KAIRON FUCK HORST","KAIRON VORNE"].includes(input.command))return {status:"INERT",mutation:false};
 if(!input.current_verified||!input.current_ref||!input.workspace)return {status:"READBACK_PENDING",mutation:false};
 const allowed=["STALE_STATE","WRONG_AUTHORITY","UNSUPPORTED_FACET","REPEATED_PLANNING","UNVERIFIED_SUCCESS","EXECUTION_DRIFT","HANDOFF_DRIFT"];
 const observations=Array.isArray(input.observations)?input.observations:[];
 const observed=observations.filter(x=>x&&allowed.includes(x.kind)&&typeof x.evidence_ref==="string"&&x.evidence_ref.trim()&&x.verified===true);
 const suspected=observations.filter(x=>x&&allowed.includes(x.kind)&&!observed.includes(x));
 return {status:observed.length?"OBSERVED_DRIFT":suspected.length?"SUSPECTED_DRIFT":"NO_DRIFT_EVIDENCE",observed,suspected,foreground:"KAIRON",workspace:input.workspace,restore_ref:input.current_ref,mutation:false,dispatch:false};
}
function supervise(input){
 if(!input||input.system_id!=="666TDI-001")throw Error("FOREIGN_IDENTITY");
 const receipts=Array.isArray(input.receipts)?input.receipts:[];
 const verified=receipts.filter(x=>x&&x.verified===true&&typeof x.ref==="string"&&x.ref.trim()&&["SOURCE_WRITE","REGRESSION_PASS","DIRECT_READBACK","HOST_ACCEPTANCE"].includes(x.kind));
 const kinds=new Set(verified.map(x=>x.kind));
 const missing=["SOURCE_WRITE","REGRESSION_PASS","DIRECT_READBACK","HOST_ACCEPTANCE"].filter(k=>!kinds.has(k));
 return {status:missing.length?"PARTIAL":"RECEIPTS_COMPLETE",missing,verified,planning_only:!kinds.has("SOURCE_WRITE"),independently_verified:false,release_authorized:false,next_options:missing.map(k=>({kind:k,action:"OBTAIN_AUTHORIZED_EVIDENCE"}))};
}
export { diagnose, supervise };
