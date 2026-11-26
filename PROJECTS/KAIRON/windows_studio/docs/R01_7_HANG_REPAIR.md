# R01.7 HANG REPAIR

Beobachtung: Intro bleibt nach R01.6 auf Windows haengen. Fehlerhypothese: WinForms-Timer-Callback erreicht Abschluss nicht. Reparatur: deterministische DoEvents-Schleife mit 8000 ms Endbedingung und kurzen PATH-Probes. Original-System und Bild bleiben unveraendert. Windows-Readback offen.
