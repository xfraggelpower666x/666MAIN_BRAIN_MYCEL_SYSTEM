# Delete-and-Forget Graph v1.7.0

`SOURCE_INPUT → HOLD_ENTRY → CONTEXT_LEDGER_ENTRY → CORRECTION_LINEAGE → OUTPUT_CACHE → LEARNING_CANDIDATE → REGRESSION_FIXTURE`

Deletion begins from any known node, resolves the shared lineage identifier, deletes content-bearing nodes, redacts derived evidence and records only a non-content deletion receipt.

Failure to reach a node yields `DELETE_PARTIAL` and blocks claims of complete deletion.
