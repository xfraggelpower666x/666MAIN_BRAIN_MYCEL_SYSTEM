# Research Orchestra · R02 (neue getrennte Teilruntime)

**Entwicklungsstand:** `0.2.0 DEVELOPMENT_CANDIDATE` · **nicht** die wiedergefundene historische Runtime `v1.7.1-clean-system.1`.

R02 ergänzt R01 **additiv**: der Bootstrap nutzt den bestehenden SHA-256-verifizierten Recherchekern und bietet ein isoliertes Blind-A/B-Zustandsmodell. Alle Auswertungen laufen im Speicher. Es gibt weder automatische Repository-Writes noch Uploads, Audiodateierzeugung, Suno-Aktionen oder Datei-Exports.

## Start und Tests

Vom Stammverzeichnis des Research-Orchestra-Projekts:

```bash
node reimplementation/r02/cli.js status
node reimplementation/r02/cli.js search psycho
node --test reimplementation/r02/tests/blind_ab.test.js
node --test reimplementation/r01/tests/runtime.test.js reimplementation/r02/tests/blind_ab.test.js
```

Oder im Unterverzeichnis `reimplementation/r02/`: `npm test`.

## Blind A/B – Programmier-Schnittstelle

```javascript
const {boot} = require('./reimplementation/r02/src/bootstrap.js');
const {blindAB} = boot();
let session = blindAB.createSession({
  id: 'session-01',
  candidates: [{id:'A',operatorRef:'private_a.wav'},{id:'B',operatorRef:'private_b.wav'}],
  evaluators: ['judge1', 'judge2'],
  criteria: ['impact', 'clarity']
});
const packet = blindAB.evaluatorPacket(session, 'judge1');
// Externes, kontrolliertes Medienrouting muss zu jedem blindId eine neutral benannte
// Hördatei bereitstellen. Im packet stehen KEINE Originaldateinamen oder Parameter.
for (const evaluatorId of session.evaluators) {
  for (const {blindId} of session.mapping) {
    session = blindAB.submitScores(session,evaluatorId,blindId,{impact:80,clarity:75});
  }
}
session = blindAB.lock(session); // erst nach vollständigen Bewertungen
const result = blindAB.reveal(session); // vorher gesperrt
```

**Echter Blindschutz:** Nur `evaluatorPacket()` an Bewertende geben. `operatorManifest()` und `exportSession()` sind ausdrücklich **betreiberseitige, vertrauliche Daten**. Ein neutraler Packet-Name allein anonymisiert noch keine Audiodatei und garantiert keine echte Blindheit. Audio-Transport und Zugriffskontrolle sind **OFFEN**.

## Korrektheitsgrenzen

- Jede `(Evaluator, Blind-Kandidat)`-Kombination muss exakt **eine vollständige Wertung** enthalten.
- Jedes deklarierte Kriterium ist verpflichtend, numerisch, endlich und im Bereich `0–100`.
- `lock()` blockiert jede unvollständige Sitzung; `reveal()` blockiert vor `lock()`; nach dem Lock sind Änderungen blockiert.
- Import/Export ist ausdrücklich **manuell**, streng schema-validiert und **nicht kryptographisch signiert**. Die Betreiberdatei muss gegen Manipulation geschützt gespeichert werden. Keine automatische Historienübernahme.
- Reihenfolge und Kennungen werden kryptographisch zufällig erzeugt. Bewertungen bleiben zu ihren neutralen Kennungen nachvollziehbar.
- Die Runtime erzeugt keine Nutzerergebnisse, Texte, Bilder, Audios oder weiteren Archivar­tefakte.

## Weiter offen

Historischer v1.7.1-Bootstrap und 123 Originaldateien sind nicht verifiziert. Stem-Masking, Sonification, Audio-Upload, 4D-Trajektorien und weitere Spezialisten sind **nicht Teil von R02**. Es gibt keinen neuen produktiven Freeze.
