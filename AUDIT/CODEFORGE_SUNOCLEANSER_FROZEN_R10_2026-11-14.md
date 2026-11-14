# CodeForge R10 · SunoCleanser Frozen-Lock-Abnahme

Datum: 2026-11-14  
GitHub-Basis: `d4326e1594985fd5d7b6961f72c3796df7f5b524`  
Geprüfter Projekt-Tree: `c3d936b6ec20bbd0e60fd744bcb71e6c925fe4ae`  
Lokaler Quellkandidat: `f9d644ebd4b5f6c4b757d06febd672e48f9f3d23`

Die lokale Kopie stammt aus einem Git-Archiv des R09-Kandidaten. Ihre Projekt-Tree-ID wurde direkt mit GitHub verglichen. Alle gelisteten Projektprüfsummen stimmten vor dem Build.

| Prüfung | Ergebnis |
|---|---|
| Frische Umgebung | Linux x86_64, Python 3.12.14. Alle sechs Versionen aus `requirements.lock` installiert. pytest 9.2.0 diente als Testwerkzeug. |
| Abhängigkeiten | `pip check` meldete keine Konflikte. |
| Projekttests | 24/24 PASS mit deaktiviertem automatischem pytest-Plugin-Loading. |
| Paketinstallation | Wheel aus dem Projekt gebaut und mit `pip install --no-deps .` in die Frozen-Umgebung installiert. |
| Installierter CLI-Einstieg | `suno-clean smoke.wav --out-dir result --quiet` aus einem separaten Arbeitsverzeichnis. Zwei Stereo-PCM-24-WAVs mit je 16.000 Frames bei 16 kHz und lesbarer JSON-Bericht. Synthetische WAV als Eingabe. |

JUnit-Bericht SHA-256: `2edb486c373fff0ec101697b3efef05fdfda1d063a598c3014d9947461d92c41`  
Wheel SHA-256 des lokalen Builds: `7c2c0216ff4cd0bdabb07b88fcc574e04881ec31b95d7b8f063107bb9bcaed9e`

Die Abnahme belegt den Linux-CLI-Einstieg unter den festgelegten Laufzeitversionen. Ein Windows-Host mit interaktiver GUI stand für diesen Lauf nicht bereit. Fresh-Chat- und UCA-Host-Abnahme bleiben offen.
