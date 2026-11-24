---
name: sceeri-go-engineer
description: Unterstützt Go-Entwicklung, Analyse, Reparatur und Build für Dienste, CLI und Windows-Launcher mit Go-Modulen.
---

# Go

Nutze diese Facette im konkreten Projektauftrag. Bestätige die maßgebliche Quelle und die Schnittstellen über [Sprachwahl und Build](../../references/sprachwahl-und-build.md).

1. Lies go.mod, go.work, belegte Go-Version, main-Paket, Build-Tags und Embed-Regeln. Bestimme für jedes Ziel GOOS, GOARCH und CGO aus der vorhandenen Projektmatrix.
2. Prüfe Context-Cancellation, Fehlerweitergabe, Goroutine-Lebensdauer, Nebenläufigkeit und bei Launchern Ressourcenpfade sowie den aufrufenden Prozess.
3. Führe passende vorhandene Go-Tests und zielbezogene Builds aus. Prüfe den Dateinamen und die Architektur des Outputs. Führe bei eingebettetem Frontend die belegten Payload-Tests zusätzlich aus.

Verwende die Gegenprobe passend zum direkten Auftrag und gleiche betroffene Build- und Skriptpfade im selben Kandidaten ab.
