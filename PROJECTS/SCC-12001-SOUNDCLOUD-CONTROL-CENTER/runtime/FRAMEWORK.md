# SCC-12001 · Functional Framework

Die funktionale Source ist SoundCloud Control Center Scriptable v1.3.2. Der Repo-Current verwaltet Identität, Source-Lineage, LiveCircle, Rehydration, Kontinuität und den exportierbaren Scriptable-Stand.

## Funktionsbereiche

1. Token Manager mit SoundCloud OAuth/PKCE und iOS-Keychain-Speicherung.
2. Track Cleanup Manager mit Analyse und explizit gewählten Löschpfaden.
3. Likes / Favoriter Analyzer.
4. LYVRA Evidence Analyzer als SCC-Funktion; daraus folgt keine LYVRA-Authority.
5. Vollständige Kontoanalyse.
6. Account-Test.
7. Album- und Track-Export mit strikter Pagination und sichtbarer Vollständigkeitsprüfung.
8. Ownership Guard v1.3.2: OWNED, EXTERNAL, UNKNOWN_REVIEW_REQUIRED; nur API-bestätigte Eigentümer-ID darf in den Owned-Katalog gelangen.

## Source-Authority

source/CURRENT_SOURCE.json ist der Source-Carrier-Vertrag. Das Repository enthält die verifizierte v1.3.1-Basis und den v1.3.2-Patch als eigene Projekt-Provenienz. tools/materialize_source.py rekonstruiert daraus bytegenau die aktuelle .js-Source und verifiziert SHA-256 sowie Größe. Die Laufzeit benötigt dafür keine PFS-Verbindung.

Secrets, Client-Credentials und Tokens gehören ausschließlich in den Scriptable-Keychain bzw. einen ausdrücklich autorisierten privaten Runtime-Speicher. Repository-Dateien enthalten keine realen Zugangsdaten.
