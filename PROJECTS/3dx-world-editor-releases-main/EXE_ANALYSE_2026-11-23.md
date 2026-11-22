# 3DX World Editor — technische EXE-Inventur

**Analysezeitpunkt:** 2026-11-23 (Europe/Berlin)  
**Quelle:** vom Nutzer hochgeladene `3DXWorldEditor.exe`  
**Status:** VERIFIZIERT (statische Dateistruktur) · PARTIAL (Quellcode-Recovery und Laufzeittest offen)

## 1. Herkunft und Integrität

- Datei: `3DXWorldEditor.exe`
- Dateigröße: **33.655.303 Bytes**
- SHA-256: `e78b12d008a19b658fce5b7c8f912dac93f2516d04c7149ceff434d96f166e20`
- PE-Format: **PE32+**, Windows **x86-64**, 7 Sections
- Die Datei wurde **statisch untersucht, nicht gestartet**.
- Der Hash dokumentiert exakt die analysierte Benutzerdatei; er ist **kein** Nachweis, dass die Datei einem bestimmten veröffentlichten Release entspricht.

## 2. Verpackung / Laufzeit

- PyInstaller-CArchive-Magic `MEI\x0c\x0b\x0a\x0b\x0e` im Dateiende identifiziert.
- CArchive-TOC erfolgreich geparst: **328 Einträge**.
- Erkannte Python-Laufzeit: `python312.dll` / Python **3.12**.
- TOC-Typen: 315 `b` (Binärdateien/Daten), 6 `s` (Scripts), 5 `m` (Module), 1 `o`, 1 `z`.
- Python-Anwendungseinstieg: `server` (Typ `s`, unkomprimiert 20.454 Bytes). Der Eintrag ist **kein gesicherter Original-Quelltext**.

## 3. Nachgewiesene eingebettete Dateien (Auswahl)

| Archivpfad | Befund |
| --- | --- |
| `server` | kompilierter Python-Anwendungseinstieg |
| `UnityPy\\__init__.py` | mitgelieferte Bibliotheks-Quelldatei |
| `UnityPy\\UnityPyBoost.cp312-win_amd64.pyd` | natives Python-Erweiterungsmodul |
| `unitypy-1.25.4.dist-info\\METADATA` | UnityPy-Version **1.25.4** |
| `docs\\js\\world.js` | eingebettete JavaScript-Ressource |
| `docs\\js\\unity\\typetrees.json` | Unity-Typdaten |
| `docs\\lite\\catalog-lite.json` | JSON-Katalogdatei |
| `docs\\worlds\\SNL-Monopoly-version.world` | enthaltene WORLD-Beispieldatei |
| `numpy-2.5.3.dist-info\\METADATA` | NumPy-Version **2.5.3** |
| `lz4-4.4.5.dist-info\\METADATA` | LZ4-Version **4.4.5** |

Die Versionsangaben stammen aus eingebetteten Paket-Metadaten bzw. Python-Laufzeitbezeichnern. Das Archiv wurde **nicht vollständig entpackt oder ausgeführt**.

## 4. Bewertung für Weiterentwicklung

**VERIFIZIERT**
- Die EXE enthält einen PyInstaller-Container mit Codeartefakten, Laufzeitkomponenten und eingebetteten Web-/Unity-Ressourcen.
- Teile der Ressourcen (`.js`, `.json`, `.py`) können prinzipiell separat in einen bearbeitbaren Arbeitsbaum exportiert werden.

**ABGELEITET**
- Der Name `server` und die Dateien unter `docs/` deuten auf einen Python-Anwendungseinstieg mit Web-Ressourcen hin. Die genaue Architektur und tatsächlichen Schnittstellen sind aus der Inventur allein **nicht bestätigt**.

**OFFEN**
- Vollständige, sichere Einzeldatei-Extraktion inklusive Integritätsprüfung und Lizenzprüfung.
- Analyse der tatsächlichen Programmlogik und der Ein-/Ausgabewege für `.world`.
- Gegebenenfalls nachvollziehbare Rekonstruktion einzelner Codekomponenten; rekonstruierten Code **nicht** als Original-Source ausgeben.
- Windows-Laufzeitprüfung, Dependency-Rekonstruktion und funktionsfähiger lokaler Entwicklungsstart.
- Abgleich der Nutzer-EXE gegen ein offizielles Release-Manifest bzw. SHA-256-Manifest.

## 5. Repository-Grenzen und nächster Schritt

Dies ist **nur ein Analyse-Dokument**. Weder die EXE noch Bytecode noch eine dekompilierte Fassung werden hier als angeblich ursprünglicher Projektquellcode eingefügt. Bestehende `README.md`, andere Projekte und native Systemzustände bleiben unverändert.

Empfohlener nächster Arbeitsschritt: vorhandene, textbasierte Anwendungskomponenten aus der konkret gehashten EXE in eine **klar markierte** `recovered/`-Struktur extrahieren und ihre Herkunft protokollieren — erst nach gesondertem Entwicklungsauftrag. Originalcode, Drittanbieterbibliotheken und rekonstruiertes Material getrennt halten.
