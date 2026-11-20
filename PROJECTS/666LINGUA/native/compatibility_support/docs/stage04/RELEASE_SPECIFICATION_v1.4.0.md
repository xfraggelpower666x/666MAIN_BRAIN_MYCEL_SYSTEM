# Stage 04 Release Specification v1.4.0

## Releaseart

`RELEASE_CANDIDATE_FROZEN`

Der Kandidat enthält den vollständigen Systembestand, Stage-03-Laufzeitvalidierung und Stage-04-
Sprachabnahme. Er ist lokal reproduzierbar und paketintern verifizierbar.

## Freigabekriterien

- 48/48 lokale Runtime-Vertragstests PASS
- 30/30 direkte Sprachprofilrouten vorhanden und abgenommen
- 12/12 erweiterte Sprach- und Verhaltensfälle PASS
- Audit PASS
- Manifest PASS
- ZIP-CRC PASS
- vollständiger Readback PASS
- keine PFS-, Drive-, Registry-, Pointer- oder LYVRA-Mutation

## Aussagegrenze

Die Freigabe ist kein Eintrag in einer externen Registry und keine Zertifizierung als professioneller
Übersetzungsdienst. Eine unabhängige zweisprachige Humanabnahme wurde nicht durchgeführt.
