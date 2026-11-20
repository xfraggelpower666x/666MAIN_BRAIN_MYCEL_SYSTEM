# GTCF v1.2.0 -> 666LINGUA v3.4.6 Target-Native Adoption

SOURCE=GLOBAL_TIMEZONE_CONVERSION_FRAMEWORK_v1.2.0_FREEZE
SOURCE_STATE=FROZEN
SOURCE_MUTATION=FORBIDDEN
ADOPTION_MODE=TARGET_NATIVE

Adopted invariants:
- date-aware + DST-aware conversion
- IANA timezone resolution
- UTC normalization
- no permanent hardcoded time difference
- day/month/year rollover detection
- ambiguous/nonexistent/repeated local-time fail-safe

666LINGUA extends this only by binding temporal conversion to translation semantics, interface localization, persisted language/timezone profiles and relative-date meaning preservation.
