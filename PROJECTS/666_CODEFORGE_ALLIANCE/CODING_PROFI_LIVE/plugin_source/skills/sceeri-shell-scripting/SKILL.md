---
name: sceeri-shell-scripting
description: Schreibt, analysiert und repariert Bash-, POSIX-Shell- und CI-Skripte anhand von Shebang, Aufrufer und Laufzeit.
---

# Bash und POSIX Shell

Nutze diese Facette im konkreten Projektauftrag. Bestätige die maßgebliche Quelle und die Schnittstellen über [Sprachwahl und Build](../../references/sprachwahl-und-build.md).

1. Prüfe tatsächlich aufgerufene Shell, Shebang, Arbeitsverzeichnis und Umgebungsübergabe. Bash-Features brauchen eine passende Bash-Ausführung.
2. Verfolge Quoting, Argumentgrenzen, Pipelines, Prozessstatus, traps und Cleanup. Prüfe, wie Fehler im aufrufenden Build oder CI-Job ankommen.
3. Verwende Syntaxprobe mit dem belegten Interpreter und vorhandenes Linting. Teste den eigentlichen Aufruf mit Leerzeichen und absichtlich fehlschlagendem Kindprozess, wenn der Auftrag die Ausführung umfasst.

Verwende die Gegenprobe passend zum direkten Auftrag und gleiche betroffene Build- und Skriptpfade im selben Kandidaten ab.
