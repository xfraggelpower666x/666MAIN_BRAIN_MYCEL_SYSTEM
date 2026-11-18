# SCC Source Carrier

Die aktuelle funktionale Source ist Scriptable v1.3.2. Sie wird nicht als ZIP geführt.

Der Repository-Carrier besteht aus der byteverifizierten v1.3.1-Basis und dem transparenten v1.3.2-Patch. Beide liegen jetzt innerhalb dieses SCC-Projekts unter provenance/pfs-child-history. tools/materialize_source.py erzeugt daraus die aktuelle .js-Datei und akzeptiert sie nur bei exakt passendem SHA-256 und Byteumfang.

provenance/pfs-child-history bleibt historische Evidenz; die neue SCC-Runtime besitzt eine eigene Authority und benötigt zur Laufzeit keine PFS-Verbindung.
