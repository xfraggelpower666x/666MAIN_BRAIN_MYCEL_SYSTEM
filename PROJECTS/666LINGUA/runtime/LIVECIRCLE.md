# ◈🌐 666LINGUA · native LiveCircle-Anbindung im Chat

Das [Original des LiveCircle](../native/runtime/LINGUA_LIVE_CIRCLE_RUNTIME_CONTRACT_v3.4.6.md), seine [Facetten](../native/registry/LINGUA_FACET_LIVE_CIRCLE_REGISTRY_v3.4.6.json) und das [native Mycel-Routing](../native/runtime/MYCEL_ROUTING_RUNTIME_CONTRACT_v3.4.6.md) sind die laufende Verfahrensgrundlage. Der [Repo-Pointer](../CURRENT_POINTER.json) macht sie zu Pflichtdateien desselben Commits.

Der Chat stellt die im nativen [Unterbrechungsvertrag](../native/docs/INTERRUPTION_PARALLEL_CONTINUATION_CONTRACT_v3.4.6.md) und [Fortsetzungsvertrag](../native/docs/CONTINUATION_TODO_CONTRACT_v3.4.6.md) verlangten Eingaben aus dem aktuellen Gespräch und dem geprüften Handoff bereit. Aufgaben-ID, letzte Evidenz und nächster Schritt stammen aus dem verifizierten Checkpoint. `666LINGUA WEITER` ruft diesen Ablauf manuell auf. Bei neuen Informationen während offener Arbeit wende die native Auswirkungsprüfung an und führe unabhängige Schritte innerhalb des aktuellen Turns fort.

`HANDOFF` und `NEW CHAT` geben den privaten, geprüften Checkpoint und den Repo-Startpfad an den Nutzer aus. Eine Wiederaufnahme benötigt den verfügbaren Sitzungsinhalt oder den beigefügten Handoff. Status und Belege werden im Chat angezeigt. Übersetzungsfunktionen und Windows-Bedienentsprechungen sind im [Funktionsvertrag](FUNCTIONS.md) beschrieben.
