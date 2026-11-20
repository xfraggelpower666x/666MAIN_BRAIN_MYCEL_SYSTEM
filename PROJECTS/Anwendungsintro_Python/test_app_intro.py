"""Prüft den Ablauf ohne Grafikserver mit der Tcl-Ereignisschleife."""
from threading import Event
import tkinter as tk
from unittest import TestCase, main
from unittest.mock import patch

from app_intro import IntroConfig, IntroResult, IntroWindow, Phase


class IntroFlowTests(TestCase):
    def setUp(self):
        self.tcl = tk.Tcl()
        self.outcomes = []
        self.updates = []

    def make_intro(self, config, ready=None):
        # Nur die Tk-Grafik wird ersetzt. Timer laufen in der echten Tcl-Schleife.
        with patch.object(tk, "Toplevel", return_value=self.tcl), patch.multiple(
            self.tcl, create=True, withdraw=lambda: None, title=lambda _: None,
            resizable=lambda *_: None, protocol=lambda *_: None, bind=lambda *_: None,
            winfo_reqwidth=lambda: 100, winfo_reqheight=lambda: 100,
            winfo_screenwidth=lambda: 1024, winfo_screenheight=lambda: 768,
            geometry=lambda _: None, deiconify=lambda: None, destroy=lambda: None,
        ), patch.object(IntroWindow, "_build", lambda intro: setattr(intro, "_progress_value", 0)):
            intro = IntroWindow(self.tcl, config, self.outcomes.append, ready=ready)

        def show(title, detail, percent):
            intro._progress_value = percent
            self.updates.append((title, detail, percent))

        intro._show = show
        self.tcl.destroy = lambda: None
        self.addCleanup(intro.cancel)
        return intro

    def run_for(self, milliseconds):
        done = tk.BooleanVar(master=self.tcl, value=False)
        self.tcl.after(milliseconds, done.set, True)
        self.tcl.tk.call("vwait", str(done))

    def test_phase_then_ready(self):
        intro = self.make_intro(IntroConfig(
            "Test", phases=(Phase("Laden", "", 20, 0),), hold_ms=0,
        ))
        self.tcl.update()
        intro.cancel()
        self.assertEqual(self.updates, [("Laden", "", 20), ("Bereit", "", 100)])
        self.assertEqual(self.outcomes, [IntroResult.READY])

    def test_wait_for_readiness_signal(self):
        ready = Event()
        self.make_intro(IntroConfig("Test", phases=(), hold_ms=0), ready=ready)
        self.tcl.update()
        self.assertEqual(self.outcomes, [])
        ready.set()
        self.run_for(90)
        self.assertEqual(self.outcomes, [IntroResult.READY])

    def test_timeout_never_reports_ready(self):
        self.make_intro(IntroConfig("Test", phases=(), timeout_ms=1), ready=Event())
        self.run_for(90)
        self.assertEqual(self.outcomes, [IntroResult.TIMED_OUT])
        self.assertTrue(all(percent < 100 for _, _, percent in self.updates))

    def test_cancel_removes_scheduled_callback(self):
        intro = self.make_intro(IntroConfig("Test"))
        intro.cancel()
        intro.cancel()
        self.tcl.update()
        self.assertEqual(self.updates, [])
        self.assertEqual(self.outcomes, [IntroResult.CANCELLED])

    def test_rejects_decreasing_progress(self):
        with self.assertRaises(ValueError):
            IntroConfig("Test", phases=(Phase("A", "", 50, 20), Phase("B", "", 10, 20)))


if __name__ == "__main__":
    main()
