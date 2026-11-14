'use strict';
(()=>{
  const dictionaries={
    'en-US':{
      gpuDisplay1:'DISPLAY OUTPUT · DISPLAY 1',display2:'DISPLAY 2',startOutput:'START OUTPUT',
      visualizerWindow:'VISUALIZER WINDOW',autoFit:'AUTO-FIT',stopOutput:'STOP OUTPUT',
      openVisualizer:'OPEN VISUALIZER',showVisualizer:'SHOW VISUALIZER',hideVisualizer:'HIDE VISUALIZER',
      outputsStopped:'VISUAL OUTPUTS STOPPED',outputsActive:'VISUAL OUTPUTS ACTIVE',
      monitorReady:'MONITOR OUTPUT READY',stream:'STREAM',
      listenersOnline:'LISTENERS (ONLINE)',peakListeners:'PEAK LISTENERS',
      listenerLimit:'LISTENER LIMIT',uniqueListeners:'UNIQUE LISTENERS',bitrate:'BITRATE',
      djLive:'DJ LIVE',lastUpdate:'LAST UPDATE',tracksHistory:'TRACKS IN HISTORY',
      streamSettings:'MANUAL STREAM / FALLBACK SETTINGS',primaryStream:'Primary stream URL',
      fallbackStream:'Fallback stream URL',saveStream:'SAVE STREAM SETTINGS',
      restoreDefaults:'RESTORE BUILT-IN DEFAULTS',openScBrowser:'OPEN SOUNDCLOUD BROWSER',
      apiCredentials:'API CREDENTIALS',saveScCredentials:'SAVE ENCRYPTED CREDENTIALS',
      aboutTitle:'About · 666SOUNDsDESIGn',support:'Support',
      supportPaypal:'Support via PayPal',websitesProjects:'Websites & Projects'
    },
    'de-DE':{
      gpuDisplay1:'MONITOR-AUSGANG · MONITOR 1',display2:'MONITOR 2',startOutput:'AUSGABE STARTEN',
      visualizerWindow:'VISUALIZER-FENSTER',autoFit:'AUTOMATISCH ANPASSEN',stopOutput:'AUSGABE STOPPEN',
      openVisualizer:'VISUALIZER ÖFFNEN',showVisualizer:'VISUALIZER ANZEIGEN',hideVisualizer:'VISUALIZER AUSBLENDEN',
      outputsStopped:'VISUAL-AUSGABE GESTOPPT',outputsActive:'VISUAL-AUSGABE AKTIV',
      monitorReady:'MONITOR-AUSGABE BEREIT',stream:'STREAM',
      listenersOnline:'ZUHÖRER (LIVE)',peakListeners:'ZUHÖRER-HÖCHSTSTAND',
      listenerLimit:'ZUHÖRER-LIMIT',uniqueListeners:'EINZIGARTIGE ZUHÖRER',bitrate:'BITRATE',
      djLive:'DJ LIVE',lastUpdate:'LETZTE AKTUALISIERUNG',tracksHistory:'TITEL IM VERLAUF',
      streamSettings:'MANUELLE STREAM-/FALLBACK-EINSTELLUNGEN',primaryStream:'Hauptstream-URL',
      fallbackStream:'Fallback-Stream-URL',saveStream:'STREAM-EINSTELLUNGEN SPEICHERN',
      restoreDefaults:'INTEGRIERTE STANDARDWERTE LADEN',openScBrowser:'SOUNDCLOUD-BROWSER ÖFFNEN',
      apiCredentials:'API-ZUGANGSDATEN',saveScCredentials:'VERSCHLÜSSELT SPEICHERN',
      aboutTitle:'Info · 666SOUNDsDESIGn',support:'Unterstützen',
      supportPaypal:'Mit PayPal unterstützen',websitesProjects:'Websites & Projekte'
    }
  };
  const staticGerman={
    'Source Hub':'Quellenzentrale','LOCAL':'LOKAL','RADIO READY':'RADIO BEREIT',
    'Admin password':'Admin-Passwort','LOGIN':'ANMELDEN','AUTODJ SKIP':'AUTODJ ÜBERSPRINGEN',
    'Player Messenger · 240 chars':'Player-Messenger · 240 Zeichen','SEND → PLAYERS':'AN PLAYER SENDEN',
    'PLAYER MESSENGER · WAITING':'PLAYER-MESSENGER · WARTET',
    'MESSENGER HISTORY':'NACHRICHTENVERLAUF','STREAM HISTORY':'STREAM-VERLAUF',
    'MESSENGER HISTORY · NOT LOADED':'NACHRICHTENVERLAUF · NICHT GELADEN',
    'STREAM HISTORY · NOT LOADED':'STREAM-VERLAUF · NICHT GELADEN',
    'Discord message':'Discord-Nachricht','SEND → DISCORD':'AN DISCORD SENDEN',
    'NOW PLAYING':'JETZT LÄUFT','DISCORD HISTORY · NO SENT MESSAGES':'DISCORD-VERLAUF · KEINE GESENDETEN NACHRICHTEN',
    'REMOTE · READY':'FERNSTEUERUNG · BEREIT','REMOTE HEALTH · CHECKING':'FERNSTATUS · WIRD GEPRÜFT',
    'REFRESH MY MUSIC':'MEINE MUSIK AKTUALISIEREN','Client ID':'Client-ID','Client Secret':'Client-Secret',
    'Credentials remain in encrypted Windows user storage.':'Zugangsdaten bleiben verschlüsselt im Windows-Benutzerprofil.',
    'Library loads from the official SoundCloud API.':'Bibliothek wird über die offizielle SoundCloud-API geladen.',
    'Optional: SoundCloud track / playlist URL':'Optional: SoundCloud-Titel-/Playlist-URL',
    'LOAD URL':'URL LADEN','◀ PREV':'◀ ZURÜCK','NEXT ▶':'WEITER ▶',
    'OPEN ON SOUNDCLOUD':'AUF SOUNDCLOUD ÖFFNEN','Audio source: SoundCloud · creator attribution shown after resolve':'Audioquelle: SoundCloud · Urheberhinweis nach dem Laden',
    'Secure Main-Process resolver · credentials not stored in renderer':'Sicherer Main-Prozess-Resolver · Zugangsdaten nicht im Renderer gespeichert',
    'SOUNDCLOUD HEALTH · CHECKING':'SOUNDCLOUD-STATUS · WIRD GEPRÜFT',
    'Radio Admin':'Radio-Administration','Password Worker · authenticated stream configuration tools':'Password Worker · geschützte Stream-Konfiguration',
    'Updates are confirmed before commit. Editable fields: primary / backup / emergency stream URLs and metadata upstreams.':'Änderungen werden vor dem Speichern bestätigt. Änderbare Felder: Haupt-, Backup- und Notfall-Stream-URLs sowie Metadatenquellen.',
    'LOAD CURRENT CONFIG':'AKTUELLE KONFIGURATION LADEN','LIST BACKUPS':'BACKUPS ANZEIGEN',
    'LOG OUT':'ABMELDEN','Radio runtime stream configuration':'Radio-Laufzeit-Streamkonfiguration',
    'SAVE CONFIG':'KONFIGURATION SPEICHERN','ROLL BACK LATEST':'LETZTE ÄNDERUNG ZURÜCKNEHMEN',
    'ADMIN CONFIG · LOGIN REQUIRED':'ADMIN-KONFIGURATION · ANMELDUNG ERFORDERLICH',
    'Media Library':'Medienbibliothek','1. Audio Song File':'1. Audiodatei',
    'Add Audio / Video Files':'Audio-/Videodateien hinzufügen','ADD MEDIA FOLDER':'MEDIENORDNER HINZUFÜGEN',
    'No audio loaded':'Keine Audiodatei geladen',
    'DROP MEDIA FILES HERE · USE ADD MEDIA FOLDER FOR FOLDERS':'MEDIENDATEIEN HIER ABLEGEN · FÜR ORDNER „MEDIENORDNER HINZUFÜGEN“ NUTZEN',
    'Playback depends on codecs available in this Electron / Windows build.':'Wiedergabe hängt von den Codecs dieser Electron-/Windows-Version ab.',
    'SHUFFLE':'ZUFÄLLIG','CLEAR':'LEEREN','SAVE PLAYLIST':'PLAYLIST SPEICHERN',
    'LOAD PLAYLIST':'PLAYLIST LADEN','Shuffle playback':'Zufallswiedergabe',
    'Track transition':'Titelübergang','Fade':'Überblendung','LOCAL QUEUE · 0 TRACKS':'LOKALE WARTESCHLANGE · 0 TITEL',
    '2. Background Image':'2. Hintergrundbild','Select Background Image':'Hintergrundbild auswählen',
    'Default Starfield active':'Standard-Sternenfeld aktiv','Sound Settings':'Toneinstellungen',
    'Enable 3-band equalizer':'3-Band-Equalizer aktivieren','Enable output booster':'Ausgangsverstärkung aktivieren',
    'Low':'Tiefen','Mid':'Mitten','High':'Höhen','Booster':'Verstärkung',
    'High boost can cause clipping or speaker distortion.':'Starke Höhenanhebung kann Übersteuerungen oder Lautsprecherverzerrungen verursachen.',
    'AUDIO PROCESSING · READY':'AUDIOVERARBEITUNG · BEREIT','Wave Design':'Wellendesign',
    'Soundwave Style':'Soundwave-Stil','Glowing Linear Bars':'Leuchtende lineare Balken',
    'Circular Ripple Rings':'Kreisförmige Wellenringe','Fluid Wave Curves':'Fließende Wellenkurven',
    'Radial Starburst Particles':'Radiale Sternenpartikel','Digital Matrix HUD':'Digitale Matrix-Anzeige',
    'Neon Oscilloscope':'Neon-Oszilloskop','3D Wireframe Orbit':'3D-Drahtgitter-Orbit',
    'Mirrored Wave Borders':'Gespiegelte Wellenränder','AI Voice Assistant Wave':'KI-Sprachassistent-Welle',
    'Digital Water Ripple':'Digitale Wasserwellen','Volumetric Glow Ribbon':'Volumetrisches Leuchtband',
    'Equalizer Wave Ribbons':'Equalizer-Wellenbänder','Orbital Voice Blobs':'Orbitale Klangformen',
    'Digital Matrix Sphere':'Digitale Matrixkugel','Neon Fiber Wavefront':'Neon-Faserwellenfront',
    'Color Theme':'Farbthema','Primary Color':'Primärfarbe','Secondary Color':'Sekundärfarbe',
    'Gradient Blend':'Farbverlauf','Solid primary':'Einfarbig: Primärfarbe','Dynamic Rainbow':'Dynamischer Regenbogen',
    'Glow Intensity':'Leuchtstärke','Audio Sensitivity':'Audioempfindlichkeit',
    'Position & Size':'Position und Größe','Move and resize the wave animation anywhere in the frame.':'Verschiebe und skaliere die Wellenanimation an eine beliebige Stelle im Bild.',
    'Visualizer Size Scale':'Visualizer-Größe','Visualizer Transparency':'Visualizer-Transparenz',
    'X-Position (Horizontal)':'X-Position (horizontal)','Y-Position (Vertical)':'Y-Position (vertikal)',
    'Center':'Mitte','Bar Width':'Balkenbreite','Circle Inner Radius':'Innerer Kreisradius',
    'Text Overlays':'Texteinblendungen','Song Title':'Songtitel','E.g., Moonlight Sonar':'Z. B. Moonlight Sonar',
    'Artist / Subtitle':'Interpret / Untertitel','E.g., Synthwave Echo':'Z. B. Synthwave Echo',
    'Typography Style':'Schriftstil','Syne (Futuristic Bold)':'Syne (futuristisch, fett)',
    'Outfit (Sleek Modern)':'Outfit (schlank, modern)','Montserrat (Classic Clean)':'Montserrat (klassisch, klar)',
    'Playfair Display (Elegant Serif)':'Playfair Display (elegante Serifenschrift)',
    'Space Grotesk (Tech Monospace)':'Space Grotesk (technische Monospace-Schrift)',
    'Beat Reactive Text (Pulses to Audio Bass)':'Beat-reaktiver Text (Pulsiert zum Bass)',
    'Presentation & Engines':'Darstellung und Engines','Visual Engine':'Visual-Engine',
    'Shader Scene':'Shader-Szene','3D Scene':'3D-Szene','FULLSCREEN':'VOLLBILD',
    'Display 1':'Monitor 1','Display 2 (optional)':'Monitor 2 (optional)','Disabled':'Deaktiviert',
    'Radio metadata ticker':'Radio-Metadatenlaufband','Radio status panel':'Radio-Statusanzeige',
    'Second display mode':'Modus für zweiten Monitor','Visualizer only':'Nur Visualizer',
    'Visualizer + ticker':'Visualizer + Laufband','Visualizer + ticker + status':'Visualizer + Laufband + Status',
    'MilkDrop Studio':'MilkDrop-Studio','ACTIVATE MILKDROP':'MILKDROP AKTIVIEREN',
    'IMPORT .MILK':' .MILK IMPORTIEREN','IMPORT PRESET FOLDER':'PRESET-ORDNER IMPORTIEREN',
    'IMPORT PERSONAL LIBRARY ZIP':'PERSÖNLICHE BIBLIOTHEK ALS ZIP IMPORTIEREN',
    'PERSONAL LIBRARY · NOT INSTALLED':'PERSÖNLICHE BIBLIOTHEK · NICHT INSTALLIERT',
    'Lock Preset':'Preset sperren','Auto Cycle':'Automatischer Wechsel','Auto Cycle Mode':'Automatischer Wechselmodus',
    'Never Repeat':'Nicht wiederholen','Next on Track Change':'Beim Titelwechsel weiter',
    'Bars per Preset':'Balken pro Preset','Seconds per Preset':'Sekunden pro Preset',
    'No-Repeat Memory':'Wiederholungsspeicher','Audio Hardcut':'Audio-Hardcut',
    'BASS IMPACT':'BASS-IMPULS','TREBLE IMPACT':'HÖHEN-IMPULS','SMART · BASS OR TREBLE':'SMART · BASS ODER HÖHEN',
    'PRESET · MANUAL':'PRESET · MANUELL','CYCLE · OFF':'ZYKLUS · AUS',
    'GPU feedback renderer · real audio analyser':'GPU-Feedback-Renderer · echte Audioanalyse',
    'Diagnostics':'Diagnose','REFRESH':'AKTUALISIEREN','RUN REAL HOST CHECK':'ECHTEN HOST-CHECK STARTEN',
    'EXPORT JSON':'JSON EXPORTIEREN','EXPORT RUNTIME DIAGNOSTICS':'LAUFZEITDIAGNOSE EXPORTIEREN',
    'READY':'BEREIT','HOST CHECK · NOT RUN':'HOST-CHECK · NICHT AUSGEFÜHRT',
    'Displays / Monitor':'Monitore','Visualizer Outputs':'Visualizer-Ausgaben',
    'Worker · Watchguard · Stream Telemetry':'Worker · Watchguard · Streamtelemetrie',
    'GPU':'GPU','Runtime':'Laufzeit','Export Studio':'Exportstudio',
    'Aspect Ratio / Layout':'Seitenverhältnis / Layout','Widescreen 16:9 (1920x1080) - YouTube':'Breitbild 16:9 (1920x1080) – YouTube',
    'Vertical 9:16 (1080x1920) - Shorts/TikTok':'Hochformat 9:16 (1080x1920) – Shorts/TikTok',
    'Square 1:1 (1080x1080) - Instagram':'Quadrat 1:1 (1080x1080) – Instagram',
    'Export Framerate':'Export-Bildrate','60 FPS (Ultra Smooth)':'60 FPS (sehr flüssig)',
    '30 FPS (Standard)':'30 FPS (Standard)','Start Recording':'Aufnahme starten',
    'PAUSE':'PAUSE','PLAY MEDIA FILE':'MEDIENDATEI ABSPIELEN','RECORDING · READY':'AUFNAHME · BEREIT',
    '☰ CONTROLS':'☰ STEUERUNG','LANGUAGE':'SPRACHE','🇺🇸 English (USA)':'🇺🇸 Englisch (USA)',
    '🇩🇪 German':'🇩🇪 Deutsch','GPU / monitor controls':'GPU-/Monitorsteuerung',
    'Status:':'Status:','Idle':'Inaktiv','Bass Peak:':'Bass-Spitze:','Audio Signal:':'Audiosignal:',
    'Active Resolution:':'Aktuelle Auflösung:','Low-frequency signal level':'Tieffrequenzpegel',
    'Mid-frequency signal level':'Mittenfrequenzpegel','High-frequency signal level':'Hochfrequenzpegel',
    'Drag slider coordinates to adjust soundwave location':'Mit den Reglern die Position der Soundwave anpassen',
    'COPYRIGHT 2026 BY FRAGGLEPOWER666 - 666SOUNDsDESIGn':'COPYRIGHT 2026 VON FRAGGLEPOWER666 – 666SOUNDsDESIGn',
    'External links open in your default browser.':'Externe Links werden im Standardbrowser geöffnet.',
    'Support':'Unterstützung','Support via PayPal':'Mit PayPal unterstützen',
    'Websites & Projects':'Websites und Projekte',
    'MAIN':'HAUPT','BACKUPS · NOT LOADED':'BACKUPS · NICHT GELADEN',
    'MUTE':'STUMM','SECONDS':'SEKUNDEN','OFF':'AUS','ALL':'ALLE',
    'WEBGL2 · CHECKING GPU':'WEBGL2 · GPU WIRD GEPRÜFT','LIVE STREAM STATUS':'LIVE-STREAMSTATUS',
    'Writing stream...':'Stream wird geschrieben …',
    'Your audio and soundwaves are being rendered to a file.':'Audio und Soundwellen werden in eine Datei gerendert.'
  };
  const germanToEnglish=Object.fromEntries(Object.entries(staticGerman).map(([english,german])=>[german,english]));
  const language=()=>document.documentElement.lang==='de-DE'?'de-DE':'en-US';
  const localizeValue=value=>{
    const table=language()==='de-DE'?staticGerman:germanToEnglish;
    const text=String(value??''),trimmed=text.trim();
    if(!trimmed)return text;
    const translated=table[trimmed];
    if(!translated)return text;
    const start=text.indexOf(trimmed);
    return text.slice(0,start)+translated+text.slice(start+trimmed.length);
  };
  const apply=()=>{
    const dictionary=dictionaries[language()];
    document.querySelectorAll('[data-i18n]').forEach(element=>{
      const value=dictionary[element.dataset.i18n];
      if(value&&element.textContent!==value)element.textContent=value;
    });
    const langLabel=document.querySelector('label[for="app-language"] span');
    const languageLabel=language()==='de-DE'?'SPRACHE':'LANGUAGE';
    if(langLabel&&langLabel.textContent!==languageLabel)langLabel.textContent=languageLabel;
    const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
    while(walker.nextNode()){
      const node=walker.currentNode;
      if(!node.parentElement?.closest('script,style')){
        const translated=localizeValue(node.nodeValue);
        if(translated!==node.nodeValue)node.nodeValue=translated;
      }
    }
    document.querySelectorAll('input,button,select,[role="meter"]').forEach(element=>{
      for(const attribute of ['aria-label','placeholder','title']){
        if(element.hasAttribute(attribute)){
          const current=element.getAttribute(attribute),translated=localizeValue(current);
          if(translated!==current)element.setAttribute(attribute,translated);
        }
      }
    });
  };
  let scheduled=false;
  const scheduleApply=()=>{
    if(scheduled)return;
    scheduled=true;
    queueMicrotask(()=>{scheduled=false;apply();});
  };
  window.RWLocalize=Object.freeze({apply,language});
  window.addEventListener('rw:language-changed',apply);
  apply();
  new MutationObserver(scheduleApply).observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['aria-label','placeholder','title']});
})();
