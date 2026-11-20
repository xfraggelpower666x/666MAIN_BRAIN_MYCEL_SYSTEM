# Software Requirements Specification — LYVRA DOLMETSCHER v1.2.3

**SYSTEM_ID:** `LYVRA-DOLMETSCHER-001`  
**ENTRY_ID:** `LYVRA-DOLMETSCHER-13001`  
**Stage:** `STAGE_02`  
**Status:** `COMPLETED_LOCAL`  
**Engine-Mutation:** `0`

## 1. Zweck

Dieses SRS konsolidiert die bereits implementierten und getesteten Anforderungen des LYVRA DOLMETSCHERS. Es ergänzt die eingefrorene v1.2.2-Basis dokumentarisch und verändert keine Übersetzungsengine, keinen LYVRA-Core, kein 666PFS und kein Drive.

## 2. Systemgrenze

Das Produkt ist ein eigenständiges, rollenbasiertes Übersetzungs-, Dolmetscher- und Lokalisierungsframework. Aktive Fremdrouter, parallele Bootstrap-Roots, direkte kanonische Lernwrites und Cross-System-Merges sind ausgeschlossen.

## 3. Funktionsbereiche

- eindeutiger Paket- und Textbootstrap
- sechs feste Sprachprofile mit 30 direkten gerichteten Routen
- getrennte Erkennung von Eingangs-, Ziel- und Systemsprache
- MICRO_HOLD, BATCH_HOLD, FIFO-Queue und automatische Fortsetzung
- Register für Terminologie, Beziehungen, Sprecher, Pronomen und unveränderliche Tokens
- Format-Preservation für strukturierte Inhalte
- kausale Emoji-Verstärkung ohne Bedeutungsdrift
- Reverse-Semantic-Audit, minimalinvasive Reparatur, Freeze und Recovery
- Long-Text-, Dokument- und Untertitelverarbeitung

## 4. Qualitäts- und Sicherheitsanforderungen

- Rohtext bleibt unverändert referenzierbar.
- Sprecher- und Intent-Eigentum bleiben beim Quellsprecher.
- Reparaturen sind auf drei Durchläufe begrenzt und werden re-auditiert.
- Freeze setzt Audit-PASS, SHA-256-Manifest und ZIP-CRC-Readback voraus.
- Secrets, Tokens und Zugangsdaten werden nicht offengelegt.
- Externe Systeme bleiben unverändert.

## 5. Rückverfolgbarkeit

Die vollständige ID-Liste mit Test- und Evidenzzuordnung befindet sich in `REQUIREMENT_TRACEABILITY_v1.2.3.json`. Insgesamt sind **40 Anforderungen** auf die vorhandenen **100 maschinenlesbaren Tests** und statische Paketartefakte abgebildet.
