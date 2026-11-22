'use strict';
/** Additive R02 bootstrap: R01 research access + R02 blind A/B protocol, no historical promotion. */
const research = require('../../r01/src/runtime.js');
const blindAB = require('./blind_ab.js');
const ID = '666-RESEARCH-ORCHESTRA-REIMPLEMENTATION-R02';
function boot(root = research.ROOT) {
  const loaded = research.loadCatalog(root); // fail closed on SHA-256 mismatch
  const report = research.report(loaded);
  if (report.issues.length || report.state !== 'VERIFIED_REIMPLEMENTATION_SUBSET') {
    throw new Error('RESEARCH_CORE_UNVERIFIED');
  }
  return {
    identity: ID, version: '0.2.0', release: 'DEVELOPMENT_CANDIDATE', production: false,
    historicalRelease: 'v1.7.1-clean-system.1', historicalReadback: 'PENDING',
    report: {...report, blindAB: 'NEW_ISOLATED_IN_MEMORY_R02'},
    search: (q, limit) => research.search(loaded.registry, q, limit),
    get: (id, kind) => research.get(loaded.registry, id, kind),
    prompt: (id, variables) => research.renderPrompt(loaded.registry, id, variables),
    blindAB
  };
}
module.exports = {ID, boot};
