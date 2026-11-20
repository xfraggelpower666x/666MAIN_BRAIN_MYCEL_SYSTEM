# ◈🌐 666LINGUA · native LiveCircle-Anbindung im Chat

Das [Original des LiveCircle](../native/runtime/LINGUA_LIVE_CIRCLE_RUNTIME_CONTRACT_v3.4.6.md), seine [Facetten](../native/registry/LINGUA_FACET_LIVE_CIRCLE_REGISTRY_v3.4.6.json) und das [native Mycel-Routing](../native/runtime/MYCEL_ROUTING_RUNTIME_CONTRACT_v3.4.6.md) sind die laufende Verfahrensgrundlage. Der [Repo-Pointer](../CURRENT_POINTER.json) macht sie zu Pflichtdateien desselben Commits.

Der Chat stellt die im nativen [Unterbrechungsvertrag](../native/docs/INTERRUPTION_PARALLEL_CONTINUATION_CONTRACT_v3.4.6.md) und [Fortsetzungsvertrag](../native/docs/CONTINUATION_TODO_CONTRACT_v3.4.6.md) verlangten Eingaben aus dem aktuellen Gespräch und dem geprüften Handoff bereit. Aufgaben-ID, letzte Evidenz und nächster Schritt stammen aus dem verifizierten Checkpoint. `666LINGUA WEITER` ruft diesen Ablauf manuell auf. Bei neuen Informationen während offener Arbeit wende die native Auswirkungsprüfung an und führe unabhängige Schritte innerhalb des aktuellen Turns fort.

`HANDOFF` und `NEW CHAT` geben den privaten, geprüften Checkpoint und den Repo-Startpfad an den Nutzer aus. Eine Wiederaufnahme benötigt den verfügbaren Sitzungsinhalt oder den beigefügten Handoff. Status und Belege werden im Chat angezeigt. Übersetzungsfunktionen und Windows-Bedienentsprechungen sind im [Funktionsvertrag](FUNCTIONS.md) beschrieben.

## Quellen für den Live-Betrieb

Der GitHub-Current unter `PROJECTS/666LINGUA` ist die laufende Framework-Quelle. Google Drive hat die Rolle `HISTORY_ONLY`. Historische Drive-Dateien dienen auf ausdrücklichen Wunsch der Herkunftsprüfung oder dem gezielten historischen Vergleich. SYSTEMSTART, WEITER, UPDATE und die laufende Rehydration verwenden GitHub und den verfügbaren privaten Sitzungsstand. Bei fehlendem GitHub-Readback gilt der Rehydrationsvertrag für Repo-Snapshots. Die älteren Drive-Speicheranweisungen in den nativen R18-Dateien gelten für ihren historischen Stand.

## Windows-App bei Live-Änderungen prüfen

1. Ermittle bei einem Live-Update den tatsächlichen Unterschied zur verifizierten GitHub-Revision. Prüfe, ob der Unterschied eine Windows-Funktion oder ihr Verhalten betreffen kann. Dazu zählen Übersetzungs- und Bedeutungsregeln, Sprachprofile, Wörterbücher, Lernen, Zeit und Zeitzonen, Emojis, Ausgabe und Zustandskompatibilität. Bei reinen Chat-, Repo- oder Dokumentationsänderungen prüfe kurz, ob ein gemeinsamer Vertrag betroffen ist. Wenn keiner betroffen ist, halte fest, warum die App davon unberührt ist.
2. Ist eine gemeinsame Funktion möglicherweise betroffen, lies die in `desktopParity.path` eingetragene Windows-App im selben Repo und Branch. Fixiere den gelesenen Commit und ermittle die Desktop-Version. Vergleiche den neuen Live-Vertrag mit dem tatsächlichen Windows-Verhalten entlang des betroffenen Einstiegspfads. Nutze dazu relevante Implementierung, Tests oder beobachtbare Laufzeitergebnisse. Vergleiche Hardware- und Host-Grenzen anhand ihrer Wirkung auf die Funktion.
3. Dokumentiere vor dem abschließenden Pointer-Schritt pro betroffener Funktion den Live-Unterschied, die Desktop-Fundstelle mit Revision oder die genaue Nachweislücke und den Befund. `UPDATE_REQUIRED` bedeutet, dass die App ein belegtes Verhalten ändern muss. `NO_UPDATE_NEEDED` bedeutet, dass das Verhalten bereits abgedeckt oder von der Änderung unberührt ist. `OPEN` bedeutet, dass eine konkrete Prüfung offen ist. Ein offener Befund gilt nicht als bestätigte Gleichwertigkeit. Nenne bei Bedarf den nächsten ausführbaren Desktop-Schritt und ob dieser bereits im freigegebenen Umfang ausgeführt wurde. Die Prüfung selbst führt keinen App-Write aus.

Normale Übersetzungen ohne Framework-Änderung durchlaufen diesen Prüfschritt nicht.
