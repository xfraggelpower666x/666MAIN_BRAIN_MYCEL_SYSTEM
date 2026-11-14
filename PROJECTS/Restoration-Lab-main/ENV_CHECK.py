"""Pruefskript fuer die Windows-Batchdateien von Restoration Lab.

  --runtime  Python 3.10-3.14, 64 Bit, Tk 8.6+
  --deps     Pakete aus requirements.txt, MP3-Decoder, PortAudio
  --audio    Ausgabegeraete auflisten
Rueckgabe 0 = in Ordnung, 1 = Problem.
"""
import sys


def check_runtime():
    problems = []
    v = sys.version_info
    if not ((3, 10) <= v[:2] <= (3, 14)):
        problems.append('Python %d.%d wird nicht unterstuetzt (erlaubt: 3.10-3.14).' % v[:2])
    if v.releaselevel != 'final':
        problems.append('Keine finale Python-Version (%s).' % v.releaselevel)
    if sys.maxsize <= 2 ** 32:
        problems.append('Es wird ein 64-Bit-Python benoetigt.')
    try:
        import tkinter
        if tkinter.TkVersion < 8.6:
            problems.append('Tk %s ist zu alt (8.6 noetig).' % tkinter.TkVersion)
    except Exception as exc:
        problems.append('tkinter nicht verfuegbar: %s (Python mit Tcl/Tk neu installieren).' % exc)
    for p in problems:
        print('[PROBLEM]', p)
    if not problems:
        print('[PASS] Python %d.%d.%d, Tk OK' % v[:3])
    return 0 if not problems else 1


def check_deps():
    modules = [('numpy', 'numpy'), ('scipy', 'scipy'), ('soundfile', 'soundfile'),
               ('pywt', 'PyWavelets'), ('sounddevice', 'sounddevice'),
               ('PIL', 'Pillow'), ('pyloudnorm', 'pyloudnorm')]
    bad = 0
    for module, package in modules:
        try:
            __import__(module)
            print('[PASS]', package)
        except Exception as exc:
            bad += 1
            print('[FEHLT] %s (%s: %s)' % (package, type(exc).__name__, exc))
    if bad == 0:
        import soundfile as sf
        import sounddevice as sd
        if 'MP3' not in sf.available_formats():
            bad += 1
            print('[FEHLT] MP3-Decoder in libsndfile (soundfile neu installieren).')
        else:
            print('[PASS] MP3-Decoder vorhanden')
        print('[PASS] PortAudio:', sd.get_portaudio_version()[1])
    return 0 if bad == 0 else 1


def check_audio():
    try:
        import sounddevice as sd
        devices = sd.query_devices()
    except Exception as exc:
        print('[FEHLER] Audio-Abfrage fehlgeschlagen:', exc)
        return 1
    outs = [d for d in devices if d['max_output_channels'] > 0]
    for d in outs:
        print('  Ausgabe:', d['name'])
    if not outs:
        print('[FEHLER] Kein Ausgabegeraet gefunden. Windows-Sound-Einstellungen pruefen.')
        return 1
    try:
        print('[PASS] Standard-Ausgabe:', sd.query_devices(kind='output')['name'])
    except Exception as exc:
        print('[WARNUNG] Kein Standardgeraet:', exc)
    return 0


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else '--runtime'
    sys.exit({'--runtime': check_runtime, '--deps': check_deps, '--audio': check_audio}.get(mode, check_runtime)())
