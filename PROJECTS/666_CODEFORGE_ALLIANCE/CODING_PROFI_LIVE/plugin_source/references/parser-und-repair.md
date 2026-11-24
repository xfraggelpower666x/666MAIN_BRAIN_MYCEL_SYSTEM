# Parser- und Reparaturablauf

1. Inventarisiere sichtbare Dateien und die relevanten Sprachversionen. Für Python prüfe Syntax und Bindungen, für Java Klassen, Typen und die Unterschiede zwischen Parsing und Kompilierung. Unterscheide JavaScript-Module und Skripte sowie TypeScript-Syntax und Typprüfung. Prüfe bei HTML Dokumentbaum und Einbettung von Skripten und Styles. CSS und dynamische Kanten erhalten einen eigenen Abdeckungsstatus.
2. Ein tatsächlicher Parserbeleg braucht Werkzeug, Eingabe, Version, Fundstelle und beobachtetes Ergebnis. Bei Chatinspektion ohne Parser kennzeichne Hinweise als statisch abgeleitet. Ein fehlerkorrigierender HTML-Parser kann Struktur stillschweigend ergänzen. Vergleiche beabsichtigten und beobachteten Baum.
3. Erstelle einen kleinen Diff auf bestätigter Basis. Prüfe genaue Originalstellen, Encoding, Zeilenenden, mögliche Unicode-Offsets und zusammengehörige Änderungen. Die früheren Vorschläge für konstante Ausdrücke und DOCTYPE-Format dienen als Prüffälle. Schlage solche Änderungen nur bei belegter Notwendigkeit und geeigneter Verhaltensprüfung vor.
4. Vergleiche dieselbe Basis und denselben Fall in getrennten autorisierten Kandidatenständen. Führe Audit, Repair, Re-Audit, gezielte Regression und gegebenenfalls Build aus, soweit die Host-Umgebung tatsächlich geeignet ist. Protokolliere Testumfang, Ergebnis und Lücken. Friere die prüfbare Übergabe mit Basis, Diff, Rückkehrpunkt und Belegen ein. Konflikte und Änderungen an der Basis vor Wiederaufnahme klären.

## Freeze und Recovery

Vergleiche die Basis vor und nach dem Prüfzyklus. Trenne bekannte Syntax- oder Parserdiagnosen, Compilerlauf und die gezielten Verhaltenstests. Eine bestandene Syntaxprüfung reicht nur für den dazu passenden Nachweisumfang. Bei misslungener Pflichtprüfung oder Basisdrift bleibt der Freeze blockiert. Erfasse Pfad, Originalstand, Diff, Kandidat und die realen Nachweise mit Prüfdatum und Toolversion.

Prüfe für Recovery die Zuordnung des Kandidaten zu gesicherten Originalbytes. Wenn ein autorisierter Host eine Wiederherstellungskopie schreiben kann, verwende ein neues Ziel und vergleiche deren Inhalt danach mit dem Original. Bei fehlenden Hash- oder Bytebelegen beschreibe die noch offene Prüfung. Bei Zweifeln am Umfang vergleiche denselben fachlichen Test mit gleichen Eingaben in getrennten Basis- und Kandidatenständen.
