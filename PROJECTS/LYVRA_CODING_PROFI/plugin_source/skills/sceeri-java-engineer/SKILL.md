---
name: sceeri-java-engineer
description: Use to create, read, audit, refactor, diagnose and safely test Java code and Maven or Gradle projects.
---

# Java Engineering

Read pom.xml/build.gradle and wrappers, JDK target, source sets, module boundaries, tests and dependency versions. Detect null handling, checked exceptions, collection mutation, concurrency, transactions, path traversal and resource closure. Map call graph to likely cause before editing. Never upgrade Java or framework versions opportunistically. Prefer JUnit tests where already present; check compilation with the project's established build when authorized in isolated environment. Record dependency and network requirements, no automatic downloads. Supply full .java files or exact diffs and test results. Never assume JS and Java are the same language.

## Versionsgebundener Java-Review

Prüfe Ziel-JDK, Build-Toolchain, Compilerziel und Bibliotheksgrenzen. Unterscheide Java-17-, Java-21- und Java-25-Profile sowie Vorschaufunktionen. Wähle Records, Sealed Types und Pattern Matching nach stabilem Vertrag und unterstützter Version. Prüfe Ressourcenfreigabe und Null-Verhalten. Bei neuen oder korrigierten Tests prüfe Verhalten und Fehlerfälle über die vorhandenen JUnit-/Mocking-Konventionen. Passe Erklärungen an Lern- oder Produktivkontext an.
