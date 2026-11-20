# Performance- und Komplexitätsbudget v2.1.0

## Zweck

Performance wird beobachtet, nicht durch Bedeutungsverlust erkauft.

## Budgets für Stage 02

- genau ein Orchestrator
- höchstens drei Self-Repair-Pässe
- keine erneute Vollanalyse, wenn sich nur ein eindeutig isolierter Format-Layer ändert
- vollständige Neuinterpretation bei Bedeutungs-, Beziehungs-, Intent- oder Korrekturänderung
- Ledger speichert standardmäßig Hashes und minimale Merkmale, keinen Rohtext
- Share-Adapter arbeitet ausschließlich auf final freigegebenem Output
- Messdaten dürfen keine Secrets oder Rohtexte enthalten

## Nicht zulässige Optimierungen

Caching falscher oder unbestätigter Bedeutung, Überspringen des Reverse-Semantic-Audits, Entfernen der Emoji-/Typografie-Integritätsprüfung oder Zusammenlegen unabhängiger Nachrichten.
