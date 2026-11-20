# Repair v1.0.9 · 2026-11-14

- Gemeinsamer öffentlicher Import für Menü und Abnahme mit direkter Quelle, Fetched-HTML-WebView und Live-WebView.
- Der Receipt enthält `importPath` und `importAttempts`.
- Ein Live-WebView kann den Chat auch ohne verfügbares Quell-HTML importieren. In diesem Fall fehlt die HTML-Datei im Beleg und der Source-Fingerprint bleibt leer.
- Wiederholte Abnahmeläufe in derselben Sekunde erhalten getrennte Ordner.

Node-Gegenprobe aus dem entpackten Ordner

```sh
node tests/host_acceptance.test.cjs 666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.9.js
```

Geräteabnahme in Scriptable über Diagnostics / Self-Test → Run host acceptance.
