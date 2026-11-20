# Human Review Evidence Weighting v1.7.0

Human review is authoritative for intended meaning, relationship tone and self-identification. Automated checks remain authoritative only for structural facts such as JSON validity, hash equality and ZIP CRC.

Priority:
1. explicit user correction;
2. bilingual human acceptance tied to exact source/output hashes;
3. repeated consistent correction evidence;
4. regression evidence;
5. heuristic model score.

A lower tier cannot override a higher tier. Conflicting reviews enter `CONFLICT_QUARANTINE`.
