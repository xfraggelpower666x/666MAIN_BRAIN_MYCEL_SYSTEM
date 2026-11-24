---
name: sceeri-swift-engineer
description: Unterstützt Swift-Entwicklung, Analyse, Reparatur, Swift Package Manager und Xcode-Projekte.
---

# Swift

Nutze diese Facette im konkreten Projektauftrag. Bestätige die maßgebliche Quelle und die Schnittstellen über [Sprachwahl und Build](../../references/sprachwahl-und-build.md).

1. Lies Package.swift oder das verwendete Xcode-Scheme, Target, Plattform und Swift-Modus. Halte Paketgrenzen und Xcode-Projektkonfiguration auseinander.
2. Prüfe Optional-Verträge, Actor-Isolation, Sendable, Fehlerweitergabe und Lebensdauer bei asynchronen Aufrufern sowie den MainActor bei UI-Arbeit.
3. Verwende die vorhandenen SwiftPM- oder Xcode-Test- und Build-Einstiege. Unterscheide SwiftPM-Proben von Tests, die Apple SDKs, Simulator, Signierung oder ein Gerät benötigen.

Verwende die Gegenprobe passend zum direkten Auftrag und gleiche betroffene Build- und Skriptpfade im selben Kandidaten ab.

## Deklarative Xcode-Projektgenerierung

Wenn `project.yml`, eine abweichende Spec oder die CI XcodeGen belegt, verwende das [XcodeGen-Profil](references/xcodegen.md). Prüfe die aufgelöste Spec, die Generierung und die Xcode-Abnahme anhand eigener Beobachtungen.
