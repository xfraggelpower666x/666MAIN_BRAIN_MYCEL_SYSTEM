# ACE-Step ComfyUI · Local Queue Repair R16

Basis: `c2407287e2c25b644e7dba85fbd77accdb9aba83` (Merge von PR #13).

Der lokale Queue-Adapter rief `startswith` auf dem Audiofeld auf, bevor er dessen Typ prüfte. Eine erfolgreiche Queue-Antwort mit `file: null` führte im Original zu einem `AttributeError`. Der Adapter meldet jetzt einen definierten Queue-Fehler bei leeren oder nicht als String gelieferten Pfaden. Gültige Pfade werden weiterhin über den bestehenden lokalen Audio-Endpunkt geladen.

`python -m unittest discover -s tests -p test_local_queue.py -v` ergab im isolierten Quellaufbau **6/6 PASS**. Die neue Regression deckt null, Zahl und Liste ab und bestätigt, dass kein Audioabruf folgt. Die HTTP-Antworten stammen aus Test-Doubles. Die interaktive DAW-/ComfyUI-Laufzeit und die Fresh-Chat-/Provider-Abnahmen bleiben offen.
