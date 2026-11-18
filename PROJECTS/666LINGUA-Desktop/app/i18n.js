'use strict';

let uiLanguage = 'en';
const english = {
  'Weitere Fassungen':'Other translations',
  'Quelltext kopieren':'Copy source',
  'Übersetzung kopieren':'Copy translation',
  'Quelltext kopiert.':'Source text copied.',
  'Wörterbuch':'Dictionary','Wörterbücher':'Dictionaries','WÖRTERBUCH':'DICTIONARY',
  'Eigene Begriffe und feste Übersetzungen auf diesem PC speichern.':'Save custom terms and preferred translations on this PC.',
  'Deutsch → Englisch':'German → English','Englisch → Deutsch':'English → German',
  'Begriffe suchen':'Find terms','Quellbegriff':'Source term','Zielbegriff':'Target term',
  'Begriff speichern':'Save term','Abbrechen':'Cancel',
  'Noch keine passenden Begriffe.':'No matching terms yet.',
  'Begriff gespeichert.':'Term saved.','Begriff gelöscht.':'Term deleted.',
  'Diesen Begriff löschen?':'Delete this term?',
  'Ein gespeicherter Begriff wurde für dieses Sprachpaar verwendet.':'A saved term was used for this language pair.',
  'Ein Satzmuster hat den gespeicherten Begriff eingesetzt.':'A sentence pattern inserted the saved term.',
  'Gespeicherte Begriffe wurden in einer belegten Satzübersetzung ersetzt.':'Saved terms were substituted in a supported sentence translation.',
  'Stilfassung behält die Wörterbuchbegriffe der Hauptfassung bei.':'This variant keeps the dictionary terms from the main translation.',
  'Wähle Deutsch → Englisch oder Englisch → Deutsch.':'Select German → English or English → German.',
  'Begriff und Übersetzung brauchen jeweils eine Zeile mit 1 bis 160 Zeichen.':'Enter a single line of 1 to 160 characters for each term.',
  'App-Sprache':'App language','Profil':'Profile','Vollbild':'Full screen','Beenden':'Exit',
  'Lokal · Force Lock':'Local · Force Lock','Arbeitsbereiche':'Workspaces',
  'Übersetzen':'Translate','Lernen':'Learning','Systemnachweis':'System evidence',
  'Quelltext':'Source text','Quelle':'Source','Ziel':'Target','Zielfassungen':'Target versions',
  'BEREIT':'READY','ÜBERSETZT':'TRANSLATED','IDENTITÄT GEPRÜFT':'IDENTITY VERIFIED','BLOCKIERT':'BLOCKED',
  'Sprachrichtung tauschen':'Swap languages','Text eingeben':'Enter text','Text eingeben oder einfügen':'Type or paste text',
  'Emoji einfügen':'Insert emoji','Bedeutungsbezogene Emojis':'Semantic emoji reinforcement',
  'Vorherigen Text verwenden':'Use previous text','Zielzeitzone':'Target time zone','Zielfassung bestätigen':'Confirm target wording',
  'Die Fassungen erscheinen nach der Übersetzung.':'Translations appear here.',
  'Entscheidung & Belege':'Decision & evidence','Belege anzeigen':'Show evidence','0 Belege':'0 items',
  'Verarbeitung':'Processing','Eingabe':'Input','Trefferprüfung':'Evidence check','Freigabe':'Output',
  'Hier erscheinen Treffer, blockierte Abschnitte und die Gründe für die Ausgabe.':'Matches, blocked segments and decisions appear here.',
  'Lokales Lernen':'Local learning','Bestätigte Fassungen haben Vorrang bei gleichem Quelltext und Sprachpaar.':'Confirmed wording has priority for the same source text and language pair.',
  'Bestätigte Fassungen':'Confirmed translations','Aktualisieren':'Refresh','Quellenstand, Laufzeit und Abnahme.':'Source baseline, runtime and verification.',
  'Abdeckung und Datenhaltung':'Coverage and storage','Drittanbieter-Hinweise':'Third-party notices','Hinweise konnten nicht geladen werden.':'Could not load third-party notices.',
  'Der lokale Kern nutzt vollständige Phrasen, die übernommenen R19-Belegfälle und belegte Satzmuster. Unbekannte und mehrdeutige Abschnitte blockieren die vollständige Ausgabe. Eine von dir bestätigte Fassung wird bei derselben Eingabe künftig bevorzugt.':'The local engine uses complete phrases, R19 evidence cases and supported sentence patterns. Unknown or ambiguous parts block a full translation. Confirmed wording takes priority when the input matches.',
  'Die fünf Ausgabepositionen bleiben verfügbar. Bei fehlender eigenständiger Formulierung erscheint die Hauptfassung mit einem Hinweis. Private R19-Profile sind im Windows-Lernspeicher nicht enthalten.':'All five output slots are available. If a separate wording is unavailable, the primary wording is shown with a note. Your Windows profile is separate from the archived R19 profiles.',
  'Quelltext und letzte Eingabe sind im Fenster flüchtig. Bestätigte Übersetzungsregeln und deine Angaben im Benutzerprofil bleiben auf diesem PC.':'Source text and previous input are kept for this session. Confirmed translation rules and your profile details stay on this PC.',
  'Dialog schließen':'Close dialog','Schließen':'Close','Korrigierte Zielfassung':'Corrected target wording','Lokal bestätigen':'Confirm locally',
  'Zeit umrechnen':'Time conversion','Datum und Uhrzeit in deiner Zeitzone eingeben.':'Enter a date and time in your time zone.',
  'Datum':'Date','Uhrzeit':'Time','Umrechnen':'Convert','Lokales Benutzerprofil':'Local user profile',
  'Die Registrierung wird auf diesem PC gespeichert.':'Your registration is saved on this PC.',
  'Deine Angaben':'Your details','Geburtsdatum':'Date of birth','Sternzeichen':'Zodiac sign','Wohnort':'City','Zeitzone':'Time zone',
  'Gesprächspartner':'Conversation partner','Ich habe einen festen Gesprächspartner':'I have a regular conversation partner',
  'Zielsprache':'Target language','Profil speichern':'Save profile','Profil löschen':'Delete profile',
  'Emoji-Assistent':'Emoji picker','Emoji suchen':'Search emojis','Kategorie':'Category',
  'Teilen':'Share','Quelltext teilen':'Share source text','Übersetzung teilen':'Share translation',
  'Text teilen':'Share text','E-Mail':'Email','Weitere Apps':'More apps','Text kopiert.':'Text copied.',
  'Wähle den Empfänger in der geöffneten App.':'Choose the recipient in the opened app.',
  'Systemfreigabe nicht verfügbar. Wähle ein anderes Ziel oder kopiere den Text.':'System sharing is unavailable. Choose another destination or copy the text.',
  'Dieser Text ist für einen Freigabelink zu lang. Nutze Weitere Apps oder kopiere ihn.':'This text is too long for a share link. Use More apps or copy it.',
  'Das Teilen-Ziel konnte nicht geöffnet werden.':'Could not open the share destination.',
  'Intro überspringen':'Skip intro','666LINGUA startet …':'Starting 666LINGUA …',
  'Oberfläche lädt …':'Loading the interface …','Bereit':'Ready',
  'Kopieren':'Copy','Bearbeiten':'Edit','Löschen':'Delete','Hauptübersetzung':'Primary translation',
  'Natürlich / lokal':'Natural / local','Präzise / technisch':'Precise / technical','Emotional+':'Emotional+','Frech / spielerisch':'Cheeky / playful',
  'Hauptfassung · keine eigenständige Fassung belegt':'Primary wording · no separate phrasing available',
  'Lokale Stilregeln auf belegte Sätze angewendet':'Local style rules applied to supported sentences',
  'Beleg':'item','Belege':'items','Zielfassung kopiert.':'Translation copied.',
  'Zwischenablage nicht verfügbar. Text markieren und mit Strg+C kopieren.':'Clipboard access was unavailable. Select the text and press Ctrl+C.',
  'Kein vollständiger Treffer. Prüfe die markierten Abschnitte oder bestätige eine eigene Fassung.':'No complete match. Review the marked segments or confirm your own wording.',
  'Prüfe lokale Sprachbelege …':'Checking local language evidence …',
  'Eingabe geändert. Die neue Fassung kann jetzt übersetzt werden.':'The source changed. Translate again to process the new text.',
  'Lokal bestätigt. Die Fassung wird bei gleicher Eingabe bevorzugt.':'Confirmed locally. This wording takes priority for matching input.',
  'Lade bestätigte Fassungen …':'Loading confirmed translations …','Noch keine Zielfassung bestätigt.':'No translations confirmed yet.',
  'Diese bestätigte Fassung dauerhaft löschen?':'Delete this confirmed translation permanently?',
  'Fassung gelöscht.':'Translation removed.','Lokale Anfrage fehlgeschlagen.':'The local request failed.',
  'Letzter Quelltext aus diesem Fenster übernommen.':'Previous source text restored from this window.',
  '666LINGUA wurde beendet. Dieses Fenster kann geschlossen werden.':'666LINGUA stopped. You can close this window.',
  'Windows-Ausgabe':'Windows version','Quellenstand':'Source baseline','Autorität':'Authority','Externe Abnahme':'External acceptance',
  'Native Live-Quelle':'Native live source','Live-State und MAIN-Artefakt geprüft.':'Live state and MAIN artifact checked.',
  'Lokaler Windows-Ableger · R19 unveröffentlicht':'Local Windows edition · R19 candidate unpublished',
  'MUM-KI-Host-Abnahme offen':'MUM AI host acceptance pending',
  'Deine Ortszeit':'Your local time','Gerätezeitzone':'Device time zone','Zielzeitzone auswählen.':'Select a target time zone.',
  'Gleiches Kalenderdatum':'Same calendar date','Vorheriger Kalendertag':'Previous calendar day','Nächster Kalendertag':'Next calendar day',
  'Profil lokal gespeichert.':'Profile saved locally.','Lokales Profil gelöscht.':'Local profile deleted.',
  'Lokales Profil und Gesprächspartner löschen?':'Delete the local profile and conversation partner?',
  'Ort erkannt':'City matched','Mehrere Orte gefunden. Wähle Ort und Region.':'Multiple places found. Select a city and region.',
  'Kein eindeutiger Ort im Offline-Verzeichnis. Wähle die Zeitzone.':'No unique city in the offline directory. Choose the time zone.',
  'Ortsverzeichnis konnte nicht geladen werden.':'Could not load the offline city directory.',
  'Alle Emojis':'All emojis','Keine passenden Emojis.':'No matching emojis.','Emojis konnten nicht geladen werden.':'Could not load emojis.',
  'Emoji eingefügt.':'Emoji inserted.','Die Eingabe hat bereits 12.000 Zeichen.':'The source is at the 12,000-character limit.',
  'Vollbild konnte nicht aktiviert werden.':'Could not activate full screen.',
  'Zeitangabe im Text erkannt. Für eine Umrechnung nutze Datum, Uhrzeit und beide Zeitzonen.':'Time reference detected. Use the date, time and both zones to convert it.',
  'Eindeutige Umrechnung mit Sommerzeitregeln':'Unambiguous conversion using daylight-saving rules',
  'Zeitzone auswählen.':'Choose a valid time zone.',
  'Ein gültiges Geburtsdatum eingeben.':'Enter a valid date of birth.',
  'Bitte Name und Wohnort eintragen.':'Enter a name and city.',
  'Bitte Sprache und Zeitzone des Gesprächspartners prüfen.':'Check the partner’s language and time zone.',
  'Ein gültiges Datum und eine Uhrzeit eingeben.':'Enter a valid date and time.',
  'Diese Ortszeit existiert wegen einer Umstellung nicht.':'This local time does not exist because the clocks move forward.',
  'Diese Ortszeit kommt bei der Umstellung zweimal vor. Wähle eine eindeutige Uhrzeit.':'This local time occurs twice when the clocks change. Choose an unambiguous time.',
  'Die lokalen Einstellungen konnten nicht gelesen werden.':'Could not read local settings.',
  'Die lokalen Einstellungen konnten nicht gespeichert werden.':'Could not save local settings.',
  'Explizit bestätigte lokale Korrektur für dieses Sprachpaar.':'Explicitly confirmed local correction for this language pair.',
  'R19-Kompatibilitätsbestand mit direktem Profiltreffer.':'R19 compatibility data with an exact profile match.',
  'Vorhandene Emojis bleiben unverändert.':'Existing emojis are preserved.',
  'Die belegte Form ist in beiden Sprachprofilen gleich.':'The documented form is the same in both language profiles.',
  'Direkter lokaler Phrasentreffer.':'Direct local phrase match.',
  'Satzmuster erkannt. Die Uhrzeit wurde unverändert übernommen.':'Sentence pattern recognized. The time was preserved as written.',
  'Sinnbezogene Verstärkung an belegten Sätzen. Wiederholte Symbole werden ausgelassen.':'Semantic reinforcement for supported sentences. Repeated symbols are skipped.',
  'Mehrdeutige Phrase. Bitte Quelltext präzisieren oder eine Fassung bestätigen.':'Ambiguous phrase. Refine the source or confirm wording.',
  'Satzabsicht passt nicht zur hinterlegten Phrase.':'The sentence intent differs from the stored phrase.',
  'Für diesen Abschnitt gibt es keinen ausreichend belegten lokalen Treffer.':'No sufficiently supported local match for this segment.',
  'Geschützte Zahlen, Links oder Kennungen würden sich ändern.':'Protected numbers, links or identifiers would change.',
  'Unveränderte Ausgabe ohne belegte sprachliche Identität.':'Unchanged output without documented identity between languages.',
  'Bitte zwei unterschiedliche Sprachprofile wählen.':'Select two different language profiles.',
  'Der Quelltext muss 1 bis 12000 Zeichen umfassen.':'The source text must contain 1 to 12,000 characters.',
  'Bitte eine eigenständige Zielfassung mit bis zu 12000 Zeichen eintragen.':'Enter a distinct target text of up to 12,000 characters.',
  'Geschützte Zahlen, Links und Kennungen müssen erhalten bleiben.':'Protected numbers, links and identifiers must be preserved.',
  'Die Regel wurde zwischenzeitlich geändert. Bitte die aktuelle Fassung prüfen.':'The rule changed in the meantime. Review the current wording.',
  'Die Regel wurde zwischenzeitlich geändert.':'The rule changed in the meantime.',
  'KONTEXT':'CONTEXT','PRÜFUNG':'VALIDATION',
  'Beobachtete Hinweise':'Observed evidence','Geprüfte Lesarten':'Considered meanings','Gewählte Fassung':'Selected wording',
  'Mehrere Bedeutungen sind möglich. Der Nachbarsatz liefert keinen passenden Hinweis.':'Several meanings are possible. The adjacent sentence provides no matching clue.',
  'Die benachbarten Sätze stützen unterschiedliche Bedeutungen.':'The adjacent sentences support different meanings.',
  'Gespeicherte und kontextgestützte Fassung weichen ab. Bestätige die gesamte Satzfolge.':'The saved wording and the contextual wording differ. Confirm the full sequence.',
  'Ein benachbarter Satz stützt diese Bedeutung.':'An adjacent sentence supports this meaning.',
  'Eine bestätigte Satzfolge passt vollständig zu diesem Abschnitt.':'A confirmed sentence sequence matches this entire passage.',
  'Bestätigte Satzfolgen überlappen. Bestätige eine gemeinsame Fassung für den gesamten Abschnitt.':'Confirmed sentence sequences overlap. Confirm one translation for the combined passage.',
  'Zahlen, Links und Kennungen wurden in der Hauptfassung geprüft.':'Numbers, links and identifiers were checked in the primary wording.',
  'Stilfassung verworfen. Sie hätte geschützte Inhalte geändert.':'Style variant rejected because it would change protected content.',
  'OFFEN':'OPEN','BESTÄTIGT':'CONFIRMED','QUELLBELEG':'SOURCE EVIDENCE','IDENTITÄT':'IDENTITY','PHRASE':'PHRASE','GRAMMATIK':'GRAMMAR',
  'Steinbock':'Capricorn','Wassermann':'Aquarius','Fische':'Pisces','Widder':'Aries','Stier':'Taurus','Zwillinge':'Gemini','Krebs':'Cancer','Löwe':'Leo','Jungfrau':'Virgo','Waage':'Libra','Skorpion':'Scorpio','Schütze':'Sagittarius'
};

function t(term) { return uiLanguage === 'de' ? term : (english[term] ?? term); }
function locale() { return uiLanguage === 'de' ? 'de-DE' : 'en-GB'; }

function localizedError(message) {
  const byCode={
    INVALID_PAIR:'Bitte zwei unterschiedliche Sprachprofile wählen.',INVALID_ZONE:'Zeitzone auswählen.',INVALID_BIRTH:'Ein gültiges Geburtsdatum eingeben.',
    PROFILE_REQUIRED:'Bitte Name und Wohnort eintragen.',INVALID_PARTNER:'Bitte Sprache und Zeitzone des Gesprächspartners prüfen.',
    INVALID_WALL_TIME:'Ein gültiges Datum und eine Uhrzeit eingeben.',
    CLOCK_GAP:'Diese Ortszeit existiert wegen einer Umstellung nicht.',
    CLOCK_FOLD:'Diese Ortszeit kommt bei der Umstellung zweimal vor. Wähle eine eindeutige Uhrzeit.',
    SETTINGS_READ:'Die lokalen Einstellungen konnten nicht gelesen werden.',
    SETTINGS_WRITE:'Die lokalen Einstellungen konnten nicht gespeichert werden.'
  };
  return t(byCode[message.split(':')[0]] || message);
}

const textBindings=[];
const attributes = ['aria-label','placeholder','title'];
function bindStaticLocalization() {
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  while(walker.nextNode()){
    const item=walker.currentNode, key=item.nodeValue.trim();
    if (Object.hasOwn(english,key) && !item.parentElement.closest('[data-i18n]')) textBindings.push([item,key,item.nodeValue]);
  }
  for(const element of document.querySelectorAll(attributes.map(a=>'['+a+']').join(','))){
    for(const attr of attributes){
      const key=element.getAttribute(attr);
      if(Object.hasOwn(english,key)) textBindings.push([element,key,attr]);
    }
  }
}

function setStaticLanguage(language) {
  uiLanguage=language;
  document.documentElement.lang=language;
  for(const item of document.querySelectorAll('[data-i18n]')) item.textContent=t(item.dataset.i18n);
  for(const [item,key,original] of textBindings) {
    if(item.nodeType===Node.TEXT_NODE) item.nodeValue=original.replace(key,t(key));
    else item.setAttribute(original,t(key));
  }
}
bindStaticLocalization();
setStaticLanguage('en');
