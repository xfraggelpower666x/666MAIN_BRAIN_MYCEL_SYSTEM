---
name: sceeri-rust-engineer
description: Unterstützt Entwicklung, Audit und Reparatur von Rust-Code, Cargo-Workspaces, CLI und Rust-FFI anhand der belegten Targets.
---

# Rust

Nutze diese Facette im konkreten Projektauftrag. Bestätige die maßgebliche Quelle und die Schnittstellen über [Sprachwahl und Build](../../references/sprachwahl-und-build.md).

1. Lies Cargo-Workspace, rust-toolchain falls vorhanden, Features, Target-Triple, build.rs und die relevanten Abhängigkeiten. Verfolge aktive Features bis zum konkreten Artefakt.
2. Prüfe Ownership, Fehlerketten, Cancellation, Send/Sync und dokumentierte Voraussetzungen von unsafe oder FFI anhand ihrer tatsächlichen Aufrufer.
3. Verwende die etablierten cargo check-, Test- oder Build-Befehle mit den Ziel-Features. Prüfe für Cross-Builds Linker und erzeugtes Format. Laufzeittests brauchen die passende Zielumgebung.

Verwende die Gegenprobe passend zum direkten Auftrag und gleiche betroffene Build- und Skriptpfade im selben Kandidaten ab.
