'use strict';
// Pure, read-only validator: deny stale, malformed, or injected device/provider data.
const SCHEMA='666.streamtranscoder.desktop-status.v1';
const components=['source','monitor','encoder','server','relay','error'];
const statuses=new Set(['off','live','connecting','error']);
const allowed=new Set(['active','connected','connecting','starting','retrying','error','idle','off','unknown']);
function validateStatus(data, now=Date.now()) {
  if (!data || typeof data!=='object' || Array.isArray(data) ||
      data.schema!==SCHEMA || !Number.isSafeInteger(data.timestamp_ms) ||
      data.timestamp_ms>now+1000 || now-data.timestamp_ms>5000 ||
      !statuses.has(data.status) || typeof data.on_air!=='boolean' ||
      typeof data.monitor_active!=='boolean' ||
      !Number.isSafeInteger(data.pid) || data.pid<=0) return null;
  for (const key of ['input_dbfs','output_dbfs']) {
    if (data[key]!==null && (typeof data[key]!=='number' ||
        !Number.isFinite(data[key]) || data[key]<-120 || data[key]>12)) return null;
  }
  if (!data.components || typeof data.components!=='object' || Array.isArray(data.components)) return null;
  const safe = {};
  for (const key of components) {
    if (!allowed.has(data.components[key])) return null;
    safe[key] = data.components[key];
  }
  if (data.on_air && data.status!=='live') return null;
  return {schema:SCHEMA, timestamp_ms:data.timestamp_ms, status:data.status,
    on_air:data.on_air, monitor_active:data.monitor_active,
    input_dbfs:data.input_dbfs, output_dbfs:data.output_dbfs, components:safe};
}
module.exports={validateStatus};
