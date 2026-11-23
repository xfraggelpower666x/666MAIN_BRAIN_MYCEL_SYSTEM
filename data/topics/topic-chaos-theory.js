ResearchDB.registerTopic({
  id: "chaos-theory",
  title: "Chaos-Theorie",
  category: "Mathematik / Dynamische Systeme",
  version: "1.0.0",
  status: "active",
  updatedAt: "2026-06-30T20:45:00+02:00",
  description: "Grundlagen deterministischen Chaos: Sensitivität, Phasenraum, Attraktoren, Bifurkationen, Periodenverdopplung, Lyapunov-Exponenten, Zeitreihenrekonstruktion, Kontrolle und methodische Grenzen.",
  scope: {
    included: [
      "Deterministische nichtlineare Systeme",
      "Kontinuierliche Flüsse und diskrete Abbildungen",
      "Sensitivität gegenüber Anfangsbedingungen",
      "Bifurkationen und Periodenverdopplung",
      "Strange Attractors",
      "Lyapunov-Exponenten",
      "Zeitreihenrekonstruktion",
      "Chaoskontrolle"
    ],
    excluded: [
      "Quantenchaos",
      "Reine Zufallsprozesse ohne deterministisches Modell",
      "Populäre Metaphern ohne mathematische Prüfbarkeit",
      "Esoterische Verwendungen des Chaosbegriffs"
    ]
  },
  researchQuestions: [
    "Was unterscheidet deterministisches Chaos von Zufall?",
    "Warum begrenzt Sensitivität die langfristige Vorhersagbarkeit?",
    "Welche mathematischen Strukturen und Messgrößen charakterisieren Chaos?",
    "Wie entstehen chaotische Regime durch Bifurkationen?",
    "Wie lässt sich Dynamik aus Messzeitreihen rekonstruieren?",
    "Unter welchen Bedingungen kann chaotisches Verhalten kontrolliert werden?",
    "Welche Fehlinterpretationen entstehen bei kurzen, verrauschten oder nichtstationären Daten?"
  ],
  sections: [
    { id: "foundations", title: "Grundlagen" },
    { id: "mechanisms", title: "Mechanismen und Kennzahlen" },
    { id: "methods", title: "Messung, Rekonstruktion und Kontrolle" },
    { id: "limits", title: "Grenzen und Fehlinterpretationen" }
  ],
  entries: [
    {
      id: "chaos-001",
      title: "Deterministisches Chaos ist nicht dasselbe wie Zufall",
      status: "confirmed",
      confidence: 100,
      summary: "Nichtlineare deterministische Gleichungen können gebundene, nichtperiodische und praktisch schwer vorhersagbare Verläufe erzeugen, obwohl die Entwicklung durch feste Regeln bestimmt ist.",
      details: "Lorenz zeigte dies an einem stark vereinfachten Konvektionsmodell; May demonstrierte, dass bereits einfache Differenzengleichungen von stabilen Fixpunkten über Zyklen bis zu scheinbar zufälligen Schwankungen reichen können. Determinismus beschreibt die Regelhaftigkeit der Entwicklung, nicht automatisch langfristige praktische Vorhersagbarkeit.",
      sourceIds: ["src-chaos-lorenz-1963", "src-chaos-may-1976"],
      tags: ["determinism", "nonlinearity", "aperiodic", "predictability"]
    },
    {
      id: "chaos-002",
      title: "Sensitivität gegenüber Anfangsbedingungen",
      status: "confirmed",
      confidence: 100,
      summary: "Nahe Anfangszustände können sich unter chaotischer Dynamik stark auseinanderentwickeln, wodurch Messfehler und Rundung den nutzbaren Vorhersagehorizont begrenzen.",
      details: "Lorenz beschrieb nichtperiodische Lösungen als gewöhnlich instabil gegenüber kleinen Modifikationen und verband dies ausdrücklich mit der begrenzten Machbarkeit sehr langfristiger Wettervorhersagen. Die Aussage ist keine Behauptung absoluter Unvorhersagbarkeit: kurzfristige Prognosen und statistische Strukturen können weiterhin sinnvoll sein.",
      sourceIds: ["src-chaos-lorenz-1963", "src-chaos-oseledets-1968"],
      tags: ["initial-conditions", "forecast-horizon", "lyapunov", "weather"]
    },
    {
      id: "chaos-003",
      title: "Phasenraum, Trajektorien und Attraktoren",
      status: "confirmed",
      confidence: 98,
      summary: "Dynamische Zustände werden als Punkte im Phasenraum dargestellt; ihre zeitliche Entwicklung bildet Trajektorien, deren langfristiges Verhalten durch invariante Mengen oder Attraktoren organisiert werden kann.",
      details: "Lorenz identifizierte Lösungen gewöhnlicher Differentialgleichungen mit Phasenraumtrajektorien. Takens unterschied glatte torusartige Attraktoren von Strange Attractors, die häufig positive Entropie und nichtganzzahlige Dimension aufweisen. Diese Merkmale sind typische Strukturhinweise, aber nicht in jedem Kontext eine alleinige vollständige Chaosdefinition.",
      sourceIds: ["src-chaos-lorenz-1963", "src-chaos-takens-1981", "src-chaos-smale-1967"],
      tags: ["phase-space", "trajectory", "attractor", "fractal-dimension"]
    },
    {
      id: "chaos-004",
      title: "Diskrete Abbildungen und die logistische Familie",
      status: "confirmed",
      confidence: 100,
      summary: "Eindimensionale Iterationen können trotz extrem einfacher Form eine Abfolge von Fixpunkten, periodischen Zyklen, Bifurkationen und chaotischen Fenstern erzeugen.",
      details: "May nutzte nichtlineare Differenzengleichungen als anschauliche Modelle unter anderem für Populationen. Der Modellwert liegt nicht darin, jede reale Population exakt abzubilden, sondern zu zeigen, dass komplexe Zeitverläufe aus einfacher deterministischer Rückkopplung entstehen können.",
      sourceIds: ["src-chaos-may-1976", "src-chaos-li-yorke-1975"],
      tags: ["logistic-map", "iteration", "population", "difference-equation"]
    },
    {
      id: "chaos-005",
      title: "Periodenverdopplung und universelle Skalierung",
      status: "confirmed",
      confidence: 100,
      summary: "Bei einer breiten Klasse nichtlinearer Abbildungen häufen sich aufeinanderfolgende Periodenverdopplungen nach universellen Skalierungsverhältnissen.",
      details: "Feigenbaum zeigte für Klassen unimodaler Rekursionen, dass Details höherer Stabilitätsbereiche asymptotisch unabhängig von der konkreten Rekursionsfunktion werden. Für quadratische Maxima tritt unter anderem die bekannte Parameterskalierung mit dem Grenzverhältnis δ ≈ 4,669201609 auf.",
      sourceIds: ["src-chaos-feigenbaum-1978"],
      tags: ["period-doubling", "bifurcation", "universality", "feigenbaum"]
    },
    {
      id: "chaos-006",
      title: "Periode drei impliziert komplexe Intervall-Dynamik",
      status: "confirmed",
      confidence: 100,
      summary: "Besitzt eine stetige Abbildung eines Intervalls einen Orbit der Periode drei, existieren periodische Punkte jeder positiven ganzzahligen Periode sowie eine überabzählbare Menge nicht asymptotisch periodischer Punkte.",
      details: "Das Resultat von Li und Yorke gab dem mathematischen Forschungsfeld den Begriff 'Chaos' im Titel und verbindet eine einzelne Periodenstruktur mit einem reichen Spektrum weiterer Orbits. Der Satz gilt unter seinen präzisen Voraussetzungen für stetige Intervallabbildungen und darf nicht ungeprüft auf beliebige Systeme übertragen werden.",
      sourceIds: ["src-chaos-li-yorke-1975"],
      tags: ["period-three", "li-yorke", "interval-map", "periodic-orbits"]
    },
    {
      id: "chaos-007",
      title: "Lyapunov-Exponenten als lokale Wachstumsraten",
      status: "confirmed",
      confidence: 96,
      summary: "Lyapunov-Exponenten beschreiben asymptotische Wachstums- oder Schrumpfungsraten infinitesimaler Störungen entlang verschiedener Richtungen eines dynamischen Systems.",
      details: "Oseledets' multiplikativer Ergodensatz liefert unter mathematischen Voraussetzungen die theoretische Grundlage für solche charakteristischen Exponenten. Ein positiver maximaler Exponent ist ein starkes Indiz für exponentielle Trennung naher Trajektorien, ersetzt aber keine Prüfung von Datenqualität, Einbettung, Stationarität und Modellannahmen.",
      sourceIds: ["src-chaos-oseledets-1968"],
      tags: ["lyapunov-exponent", "stability", "divergence", "ergodic-theorem"]
    },
    {
      id: "chaos-008",
      title: "Rekonstruktion aus einer einzelnen Messzeitreihe",
      status: "confirmed",
      confidence: 98,
      summary: "Unter geeigneten Glattheits- und Generizitätsbedingungen kann die Geometrie eines Attraktors aus zeitverzögerten Kopien einer skalaren Beobachtung rekonstruiert werden.",
      details: "Takens entwickelte dafür einen Einbettungsansatz, der experimentelle Daten selbst statt nur ihres Leistungsspektrums verwendet. Praktisch bleiben Wahl von Verzögerung und Einbettungsdimension, Messrauschen, endliche Datenlänge und Nichtstationarität kritische Fehlerquellen.",
      sourceIds: ["src-chaos-takens-1981"],
      tags: ["delay-embedding", "time-series", "reconstruction", "takens"]
    },
    {
      id: "chaos-009",
      title: "Chaotische Dynamik kann gezielt stabilisiert werden",
      status: "confirmed",
      confidence: 100,
      summary: "Chaotische Attraktoren enthalten zahlreiche instabile periodische Orbits, von denen ausgewählte durch kleine zeitabhängige Parameteränderungen stabilisiert werden können.",
      details: "Ott, Grebogi und Yorke zeigten eine Methode, die kleine Störungen eines verfügbaren Systemparameters und Delay-Coordinate-Information nutzt. Kontrolle bedeutet hier nicht, jede Dynamik zu eliminieren, sondern einen gewünschten eingebetteten Orbit anzusteuern und zu stabilisieren.",
      sourceIds: ["src-chaos-ogy-1990", "src-chaos-takens-1981"],
      tags: ["chaos-control", "ogy", "unstable-periodic-orbit", "feedback"]
    },
    {
      id: "chaos-010",
      title: "Chaosnachweis aus realen Daten ist methodisch anspruchsvoll",
      status: "confirmed",
      confidence: 95,
      summary: "Unregelmäßigkeit allein beweist kein deterministisches Chaos; Rauschen, Nichtstationarität, zu kurze Zeitreihen und ungeeignete Rekonstruktionsparameter können ähnliche Signaturen erzeugen.",
      details: "Takens formulierte Rekonstruktionsverfahren unter expliziten mathematischen Voraussetzungen und nannte Kriterien, bei deren Nichterfüllung eine Strange-Attractor-Erklärung verworfen werden sollte. Seriöse Analyse kombiniert daher mehrere Diagnosewege und dokumentiert Unsicherheit statt ein einzelnes buntes Phasenportrait als Beweis zu behandeln.",
      sourceIds: ["src-chaos-takens-1981", "src-chaos-may-1976"],
      tags: ["noise", "nonstationarity", "false-positive", "methodology"]
    }
  ],
  sources: [
    {
      id: "src-chaos-lorenz-1963",
      title: "Deterministic Nonperiodic Flow",
      author: "Edward N. Lorenz",
      sourceType: "primary-research-paper",
      trustLevel: "A",
      publishedAt: "1963-03-01",
      accessedAt: "2026-06-30",
      url: "https://journals.ametsoc.org/view/journals/atsc/20/2/1520-0469_1963_020_0130_dnf_2_0_co_2.xml",
      doi: "10.1175/1520-0469(1963)020<0130:DNF>2.0.CO;2",
      notes: "Grundarbeit zu gebundenem deterministischem nichtperiodischem Fluss und Anfangswertsensitivität.",
      usedFor: ["chaos-001", "chaos-002", "chaos-003"]
    },
    {
      id: "src-chaos-smale-1967",
      title: "Differentiable Dynamical Systems",
      author: "Stephen Smale",
      sourceType: "primary-research-paper",
      trustLevel: "A",
      publishedAt: "1967-11-01",
      accessedAt: "2026-06-30",
      url: "https://doi.org/10.1090/S0002-9904-1967-11798-1",
      doi: "10.1090/S0002-9904-1967-11798-1",
      notes: "Grundlegende globale Theorie differenzierbarer dynamischer Systeme, Hyperbolizität und strukturelle Stabilität.",
      usedFor: ["chaos-003"]
    },
    {
      id: "src-chaos-oseledets-1968",
      title: "A Multiplicative Ergodic Theorem: Lyapunov Characteristic Numbers for Dynamical Systems",
      author: "Valery I. Oseledets",
      sourceType: "primary-research-paper",
      trustLevel: "A",
      publishedAt: "1968-01-01",
      accessedAt: "2026-06-30",
      url: "https://www.mathnet.ru/eng/mmo214",
      notes: "Theoretische Grundlage der Lyapunov-charakteristischen Exponenten.",
      usedFor: ["chaos-002", "chaos-007"]
    },
    {
      id: "src-chaos-li-yorke-1975",
      title: "Period Three Implies Chaos",
      author: "Tien-Yien Li; James A. Yorke",
      sourceType: "primary-research-paper",
      trustLevel: "A",
      publishedAt: "1975-12-01",
      accessedAt: "2026-06-30",
      url: "https://doi.org/10.1080/00029890.1975.11994008",
      doi: "10.1080/00029890.1975.11994008",
      notes: "Beweist für stetige Intervallabbildungen den Zusammenhang zwischen Periode drei, Perioden aller Längen und einer überabzählbaren nichtperiodischen Menge.",
      usedFor: ["chaos-004", "chaos-006"]
    },
    {
      id: "src-chaos-may-1976",
      title: "Simple Mathematical Models with Very Complicated Dynamics",
      author: "Robert M. May",
      sourceType: "primary-research-review",
      trustLevel: "A",
      publishedAt: "1976-06-10",
      accessedAt: "2026-06-30",
      url: "https://doi.org/10.1038/261459a0",
      doi: "10.1038/261459a0",
      notes: "Zeigt die reiche Dynamik einfacher nichtlinearer Differenzengleichungen und diskutiert Anwendungen und Grenzen.",
      usedFor: ["chaos-001", "chaos-004", "chaos-010"]
    },
    {
      id: "src-chaos-feigenbaum-1978",
      title: "Quantitative Universality for a Class of Nonlinear Transformations",
      author: "Mitchell J. Feigenbaum",
      sourceType: "primary-research-paper",
      trustLevel: "A",
      publishedAt: "1978-07-01",
      accessedAt: "2026-06-30",
      url: "https://doi.org/10.1007/BF01020332",
      doi: "10.1007/BF01020332",
      notes: "Universelle Skalierungsstruktur von Periodenverdopplungskaskaden in Klassen nichtlinearer Abbildungen.",
      usedFor: ["chaos-005"]
    },
    {
      id: "src-chaos-takens-1981",
      title: "Detecting Strange Attractors in Turbulence",
      author: "Floris Takens",
      sourceType: "primary-research-paper",
      trustLevel: "A",
      publishedAt: "1981-01-01",
      accessedAt: "2026-06-30",
      url: "https://doi.org/10.1007/BFb0091924",
      doi: "10.1007/BFb0091924",
      notes: "Einbettungs- und Rekonstruktionsgrundlage für die Analyse dynamischer Strukturen aus Messzeitreihen.",
      usedFor: ["chaos-003", "chaos-008", "chaos-009", "chaos-010"]
    },
    {
      id: "src-chaos-ogy-1990",
      title: "Controlling Chaos",
      author: "Edward Ott; Celso Grebogi; James A. Yorke",
      sourceType: "primary-research-paper",
      trustLevel: "A",
      publishedAt: "1990-03-12",
      accessedAt: "2026-06-30",
      url: "https://doi.org/10.1103/PhysRevLett.64.1196",
      doi: "10.1103/PhysRevLett.64.1196",
      notes: "Kleine zeitabhängige Parameterstörungen können ausgewählte periodische Bewegungen in einem chaotischen Attraktor stabilisieren.",
      usedFor: ["chaos-009"]
    }
  ],
  openQuestions: [
    "Welche Kombination von Surrogatentests, Lyapunov-Schätzung und Dimensionsanalyse ist für kurze verrauschte Messreihen am robustesten?",
    "Wie verändert Nichtstationarität die Zuverlässigkeit klassischer Chaosdiagnostik?",
    "Wie sollte ein praktischer Vorhersagehorizont aus Unsicherheit und lokalen Expansionsraten abgeleitet werden?",
    "Welche Teile realer Hochdimensionssysteme lassen sich sinnvoll durch niedrigdimensionale Attraktormodelle approximieren?",
    "Wie kann Chaoskontrolle bei Parameterdrift, Zeitverzögerung und Messrauschen robust gehalten werden?"
  ],
  contradictions: [
    {
      id: "chaos-contradiction-001",
      summary: "Populäre Darstellungen setzen Chaos häufig mit Zufall gleich; die mathematische Literatur behandelt dagegen regelbestimmte Dynamik mit komplexem, oft nichtperiodischem Verhalten.",
      resolution: "Begriffe Determinismus, Zufall, Sensitivität und Vorhersagbarkeit getrennt verwenden."
    },
    {
      id: "chaos-contradiction-002",
      summary: "Ein unregelmäßiges Signal kann sowohl deterministisches Chaos als auch stochastisches Rauschen oder Nichtstationarität widerspiegeln.",
      resolution: "Keinen Chaosnachweis aus bloßer visueller Unregelmäßigkeit ableiten; mehrere Diagnosen und Datenannahmen dokumentieren."
    }
  ],
  quarantine: [
    {
      id: "chaos-quarantine-001",
      claim: "Der Schmetterlingseffekt bedeutet, dass jede beliebig kleine Änderung immer jede gewünschte große Wirkung erzeugt.",
      reason: "Übergeneralisierung. Sensitivität beschreibt Zustandsdivergenz innerhalb einer konkreten Dynamik, keine frei steuerbare universelle Kausalmacht."
    },
    {
      id: "chaos-quarantine-002",
      claim: "Ein fraktal wirkendes Diagramm oder ein positiver geschätzter Exponent beweist allein sicher Chaos.",
      reason: "Endliche Daten, Rauschen, schlechte Einbettung und methodische Verzerrungen können falsch-positive Signaturen erzeugen."
    }
  ],
  changelog: [
    {
      date: "2026-06-30",
      version: "1.0.0",
      change: "Grundlagenmodul mit zehn geprüften Kerneinträgen und acht Primärquellen integriert."
    }
  ]
});
