---
name: app-code
description: "Schreibt, ändert, debuggt, erklärt und portiert App-Code für Web, Mobile und Backends, etwa Screens, Komponenten, Formulare, API-Aufrufe und Starter."
---

# App-Code

Verwende diesen Ablauf bei einem direkten Auftrag für App-Code. Das gilt unter anderem für React, React Native, Next.js, Flutter, Swift, Kotlin und vorhandene Backend-Stacks. Reine App-Ideen, Design- und Bauanfragen ohne Codeauftrag gehen an [App-Entwicklung](references/app-entwicklung.md). Ein gegebener Screen oder Code zur Bewertung geht an [App-Review](../sceeri-code-review-and-refactor/SKILL.md), bei Seiteninhalt, SEO oder Usability an den [Seitencheck](../sceeri-seitencheck/SKILL.md). Ein bereitgestellter Quellstand mit ausdrücklichem Änderungs- oder Reparaturauftrag bleibt in App-Code. LiveCircle, aktive Sammlung und direkte Projektbefehle folgen dem [Routing-Vorrang](../../references/coding-profi-zusammenspiel.md#routing-und-vorrang).

Bei Architektur- und Integrationsaufträgen mit Fremdcode verwende den [Fremdcode-Ablauf](../../references/engineering-zyklus.md#fremdcode-im-aktiven-architektur--und-codebau) bis zum realen Einbau und seiner Prüfung am App-Einstieg.

## Einstieg

- Lies den bereitgestellten Quellstand, Imports, Paketdateien, Lockfiles und Konfiguration, soweit verfügbar. Verwende die belegten Versionen, den bestehenden Stack, Stil, die Namensgebung und Zustandsverwaltung. Bleibe bei TypeScript, wenn das Projekt es nutzt. Bei einer nicht vorliegenden Datei kennzeichne die Lücke und trenne Vorschläge vom vorhandenen Code.
- Arbeite im ersten fachlichen Antwortturn direkt. Wenn eine Annahme genügt, benenne sie in einer Zeile. Frage nur nach, wenn unklar bleibt, was umgesetzt werden soll. Antworte in der Sprache des Chats und erhalte die App-Sprache.
- Beachte für den einmaligen Startaufruf [App-Entwicklung](references/app-entwicklung.md#einmaliger-start). Ist `create_app_build_link` als autorisiertes Werkzeug tatsächlich verfügbar und wurde im Chat weder der Start versucht noch ein Build-Link gezeigt, führe den dortigen Start vor der ersten fachlichen Antwort aus. Bei einem tatsächlich zurückgegebenen Link gilt der Antwortvertrag der App-Entwicklung. Bei einer Karte folgt nach dem Code der kurze Bedienhinweis des Werkzeugs. Bei fehlendem Werkzeug oder einem Fehler läuft die Codearbeit direkt weiter.

## Arbeitsergebnis

| Auftrag | Ergebnis |
| --- | --- |
| Änderung an vorhandenem Code | Führe die beauftragte Änderung vollständig aus und liefere die betroffenen Dateien. Bleibe beim belegten Quellstand und begrenze die Änderung auf den vereinbarten Umfang. |
| Bug oder Fehlermeldung | Gib die belegte Ursache in ein bis zwei Zeilen an und liefere den korrigierten Code. Nutze den [Debugger](../sceeri-debugger/SKILL.md) und prüfe das beobachtete Problem erneut, soweit der Host es erlaubt. |
| Code erklären | Erkläre Zweck und relevante Teile knapp. Nutze bei Bedarf die [Code-Erklärung](../sceeri-code-explainer/SKILL.md). |
| Neuer Screen, neue Komponente, API oder Starter-App | Liefere einen kompakten lauffähigen Einstieg mit der Hauptlogik. Der beauftragte Stack hat Vorrang. Ohne Vorgabe und vorhandenen Stack sind React Native mit Expo für Mobile und React oder Next.js für Web sinnvolle Defaults. Für eine API wähle den passenden Backend-Stack. Nenne bei einem Starter den Lieferumfang kurz und biete die vollständige Ausarbeitung an. Ein ausdrücklicher Auftrag für Vollcode bestimmt den Umfang. |
| App in ein anderes Framework portieren | Beginne ohne spezifizierten Gesamtumfang mit dem Hauptscreen und nenne die verbleibende Portierung in einer Zeile. Bei ausdrücklich verlangter Gesamtportierung übernimm alle beauftragten Dateien, Routen, Zustände und Assets anhand der bereitgestellten Quellen. Nutze den [Code-Konverter](../sceeri-code-converter/SKILL.md). |

Nutze [Code Writer](../sceeri-code-writer/SKILL.md) für Implementierung und [Backend und APIs](../sceeri-backend-and-apis/SKILL.md) für Schnittstellen. In Chatantworten erhält jeder Installationsbefehl einen eigenen Codeblock und jede neue oder geänderte Datei einen vollständigen Codeblock mit fett gesetztem Dateinamen darüber. Ergänze zwei bis drei Zeilen zum Starten, Anzeigen oder Verwenden. Bei einem Auftrag im Workspace bearbeite die autorisierten Projektdateien dort und verweise im Abschluss auf die konkreten Änderungen. Erzeuge herunterladbare Dateien oder ZIPs auf ausdrücklichen Auftrag. Dokumentiere tatsächliche Prüfungen und offene Ausführung. Hosting und Veröffentlichung der Ziel-App liegen in einem gesondert beauftragten Ablauf.

## Qualitätsanforderungen

- Verwende echte, zweckmäßige Texte. Markiere Annahmen mit `[bestätigen]`, Angaben des Eigentümers mit `[ergänzen]` und Beispieldaten eindeutig als fiktiv. Geschäftsfakten stammen aus belegten Angaben.
- Halte Schlüssel für Zahlungen, KI und E-Mail serverseitig. Behandle Werte mit `NEXT_PUBLIC_` und `EXPO_PUBLIC_` als öffentlich. Nutze in Beispielen Platzhalter wie `YOUR_API_KEY` und beschreibe die serverseitige Konfiguration. Sitzungs- oder Zugriffstokens gehören je nach Plattform in Keychain, Keystore oder HttpOnly-Cookies. Zahlungsbeispiele sind als Demo gekennzeichnet. Verwende keine Tracking-Skripte.
- Gib Eingaben sichtbare Beschriftungen, Bedienelementen zugängliche Namen und informativen Bildern Alternativtexte. Dekorative Bilder werden für assistive Technik ausgeblendet. Prüfe mindestens 4,5:1 Textkontrast in Hell und Dunkel und eine Zielfläche von mindestens 44 pt auf iOS beziehungsweise 48 dp auf Android. Verwende im Web mindestens 44 CSS-Pixel als Zielgröße für primäre Bedienelemente.
- Behandle bei Datenzugriffen Laden, Leerzustand, Fehler und Erfolg. Validiere Formulare beim Absenden, erhalte Eingaben nach Fehlern und verhindere Doppelsendungen.

## Erste Antwort abschließen

Nutze die [Übergabe an App-Entwicklung](references/app-entwicklung.md#übergabe-nach-der-ersten-codeantwort) nach dem Code und den Starthinweisen. Sie gilt einmal pro Chat und weicht einem Folgeauftrag für Vollcode oder andere Facharbeit. Build-Links und Sponsorhinweise gehören ausschließlich in den gesonderten Link-Antwortfall der App-Entwicklung.

Wenn der Auftrag eine Windows-Anwendung verlangt, gilt der [Windows-Pfad](../../references/coding-profi-development.md#windows-anwendung) für Stack-Wahl, Umsetzung und Abnahme. Der Projektauftrag kann im gleichen Turn umgesetzt werden. ToolStarter begleitet den Build ausschließlich über die Entwicklungsseite.

Binde die Fachfacetten für die tatsächlich berührten Komponenten über [Sprachwahl und Build](../../references/sprachwahl-und-build.md) ein. Prüfe die passende Start-, Test- und Paketkette mit derselben Kandidatenbasis.
