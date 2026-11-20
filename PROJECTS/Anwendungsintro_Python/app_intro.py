"""Konfigurierbarer Startbildschirm für Anwendungen mit Tkinter."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from threading import Event
from time import monotonic
import tkinter as tk


class IntroResult(Enum):
    READY = "ready"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Phase:
    title: str
    detail: str
    progress: int
    duration_ms: int

    def __post_init__(self) -> None:
        if not 0 <= self.progress <= 99:
            raise ValueError("Der Fortschritt einer Phase muss zwischen 0 und 99 liegen.")
        if self.duration_ms < 0:
            raise ValueError("Die Phasendauer darf nicht negativ sein.")


@dataclass(frozen=True)
class Theme:
    background: str = "#17212b"
    foreground: str = "#f4f6f8"
    muted: str = "#bcc8d2"
    accent: str = "#79c8ff"
    progress_track: str = "#374756"
    font_family: str = "Segoe UI"


@dataclass(frozen=True)
class IntroConfig:
    title: str
    version: str = ""
    subtitle: str = ""
    banner: str | Path | None = None
    logo: str | Path | None = None
    width: int = 760
    height: int = 460
    theme: Theme = field(default_factory=Theme)
    phases: tuple[Phase, ...] = (
        Phase("Initialisierung", "Anwendung wird vorbereitet …", 25, 400),
        Phase("Start", "Oberfläche wird geladen …", 75, 600),
    )
    waiting_text: str = "Warte auf die Anwendung …"
    ready_text: str = "Bereit"
    hold_ms: int = 350
    timeout_ms: int | None = 15_000

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Ein Anwendungstitel ist erforderlich.")
        if self.width <= 0 or self.height <= 0 or self.hold_ms < 0:
            raise ValueError("Die Fenstergröße muss positiv sein. Die Haltezeit darf nicht negativ sein.")
        if self.timeout_ms is not None and self.timeout_ms <= 0:
            raise ValueError("Der Timeout muss positiv sein oder None lauten.")
        positions = [phase.progress for phase in self.phases]
        if positions != sorted(positions):
            raise ValueError("Der Fortschritt darf zwischen Phasen nicht sinken.")


class IntroWindow:
    """Zeigt das Intro in der vorhandenen Tk-Ereignisschleife."""

    def __init__(
        self,
        root: tk.Tk,
        config: IntroConfig,
        on_close: Callable[[IntroResult], None],
        *,
        ready: Event | None = None,
    ) -> None:
        self._config = config
        self._on_close = on_close
        self._ready = ready
        self._wait_started: float | None = None
        self._phase = 0
        self._complete = False
        self._after: str | None = None
        self._images: list[tk.PhotoImage] = []

        window = self._window = tk.Toplevel(root)
        try:
            window.withdraw()
            window.title(config.title)
            window.resizable(False, False)
            window.protocol("WM_DELETE_WINDOW", self.cancel)
            window.bind("<Escape>", self._cancel_on_escape)
            window.bind("<Destroy>", self._on_destroy)
            self._build()
            window.update_idletasks()
            width = min(max(config.width, window.winfo_reqwidth()), window.winfo_screenwidth())
            height = min(max(config.height, window.winfo_reqheight()), window.winfo_screenheight())
            x = (window.winfo_screenwidth() - width) // 2
            y = (window.winfo_screenheight() - height) // 2
            window.geometry(f"{width}x{height}+{x}+{y}")
            window.deiconify()
            self._after = window.after_idle(self._advance)
        except Exception:
            window.destroy()
            raise

    def _build(self) -> None:
        cfg = self._config
        theme = cfg.theme
        window = self._window
        window.configure(background=theme.background)
        panel = tk.Frame(window, bg=theme.background, padx=28, pady=22)
        panel.pack(expand=True, fill="x")
        self._image(panel, cfg.banner, min(cfg.width - 56, window.winfo_screenwidth() - 56), 100)
        self._image(panel, cfg.logo, 100, 100)
        title = f"{cfg.title}  {cfg.version}" if cfg.version else cfg.title
        self._label(panel, title, 24, theme.foreground, bold=True).pack(pady=(8, 2))
        if cfg.subtitle:
            self._label(panel, cfg.subtitle, 11, theme.muted).pack()
        self._status = self._label(panel, "", 13, theme.accent, bold=True)
        self._status.pack(pady=(18, 2))
        self._detail = self._label(panel, "", 11, theme.muted)
        self._detail.pack()
        self._progress = tk.Canvas(panel, height=8, bg=theme.progress_track, highlightthickness=0)
        self._progress.pack(fill="x", pady=(14, 0))
        self._fill = self._progress.create_rectangle(0, 0, 0, 8, fill=theme.accent, width=0)
        self._progress_value = 0
        self._progress.bind("<Configure>", self._draw_progress)

    def _label(
        self, parent: tk.Frame, text: str, size: int, color: str, *, bold: bool = False
    ) -> tk.Label:
        cfg = self._config
        weight = "bold" if bold else "normal"
        return tk.Label(
            parent, text=text, bg=cfg.theme.background, fg=color, justify="center",
            font=(cfg.theme.font_family, size, weight),
            wraplength=max(1, min(cfg.width, parent.winfo_screenwidth()) - 56),
        )

    def _image(self, parent: tk.Frame, path: str | Path | None, width: int, height: int) -> None:
        if path is None:
            return
        image = tk.PhotoImage(master=self._window, file=str(path))
        width = max(1, width)
        horizontal_step = (image.width() + width - 1) // width
        vertical_step = (image.height() + height - 1) // height
        step = max(1, horizontal_step, vertical_step)
        if step > 1:
            image = image.subsample(step)
        self._images.append(image)
        tk.Label(parent, image=image, bg=self._config.theme.background).pack(pady=(0, 5))

    def _draw_progress(self, _event: tk.Event | None = None) -> None:
        width = self._progress.winfo_width() * self._progress_value / 100
        self._progress.coords(self._fill, 0, 0, width, 8)

    def _show(self, title: str, detail: str, progress: int) -> None:
        self._status.configure(text=title)
        self._detail.configure(text=detail)
        self._progress_value = progress
        self._draw_progress()

    def _advance(self) -> None:
        self._after = None
        cfg = self._config
        if self._phase < len(cfg.phases):
            phase = cfg.phases[self._phase]
            self._phase += 1
            self._show(phase.title, phase.detail, phase.progress)
            self._after = self._window.after(phase.duration_ms, self._advance)
            return
        self._wait_for_ready()

    def _wait_for_ready(self) -> None:
        self._after = None
        cfg = self._config
        if self._ready is None or self._ready.is_set():
            self._show(cfg.ready_text, "", 100)
            self._after = self._window.after(cfg.hold_ms, self._finish_ready)
            return
        if self._wait_started is None:
            self._wait_started = monotonic()
            self._show(cfg.waiting_text, "", self._progress_value)
        elapsed_ms = (monotonic() - self._wait_started) * 1000
        if cfg.timeout_ms is not None and elapsed_ms >= cfg.timeout_ms:
            self._finish(IntroResult.TIMED_OUT)
            return
        self._after = self._window.after(50, self._wait_for_ready)

    def _finish_ready(self) -> None:
        self._after = None
        self._finish(IntroResult.READY)

    def _cancel_on_escape(self, _event: tk.Event) -> None:
        self.cancel()

    def cancel(self) -> None:
        """Schließt das Intro und meldet CANCELLED im Tk-Hauptthread."""
        self._finish(IntroResult.CANCELLED)

    def _on_destroy(self, event: tk.Event) -> None:
        if event.widget is self._window:
            self._complete = True
            self._cancel_timer()

    def _cancel_timer(self) -> None:
        if self._after is not None:
            self._window.after_cancel(self._after)
            self._after = None

    def _finish(self, result: IntroResult) -> None:
        if self._complete:
            return
        self._complete = True
        self._cancel_timer()
        self._window.destroy()
        self._on_close(result)
