from __future__ import annotations

import gzip
import hashlib
import io
import json
import mimetypes
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
import urllib.parse
import urllib.request
import webbrowser
import zipfile
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable

try:
    from PIL import Image, ImageTk

    PIL_AVAILABLE = True
except Exception:  # pragma: no cover - bootstrap installs Pillow for source runs
    Image = None  # type: ignore[assignment]
    ImageTk = None  # type: ignore[assignment]
    PIL_AVAILABLE = False


def _redirect_direct_source_start_through_bootstrap() -> None:
    """Route direct .py/.pyw starts through the Windows dependency bootstrap."""
    if os.name != "nt" or getattr(sys, "frozen", False):
        return
    if os.environ.get("CHATBACKUP_BOOTSTRAP_STATUS") == "PASS":
        return

    project_root = Path(__file__).resolve().parent.parent
    bootstrap = project_root / "bootstrap" / "bootstrap.ps1"
    if not bootstrap.exists():
        return

    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        subprocess.Popen(
            [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(bootstrap),
                "-Mode",
                "Run",
                "-ForceSource",
                "-LaunchHidden",
            ],
            cwd=str(project_root),
            creationflags=creation_flags,
        )
    except OSError:
        return
    raise SystemExit(0)


_redirect_direct_source_start_through_bootstrap()

from chatbackup_core import (  # noqa: E402
    APP_VERSION,
    USER_AGENT,
    ChatAsset,
    ChatBackup,
    ChatBackupError,
    chat_asset_key,
    build_javascript_export,
    build_json_export,
    build_jsonl_export,
    build_markdown,
    build_parser_receipt,
    build_raw_source_bundle,
    build_structure_inspector_json,
    file_date_stamp,
    load_chat_backup,
    sanitize_file_name,
    unique_path,
    write_verified,
)

from chatbackup_backend import BackendConfig, ChatBackend  # noqa: E402
from safe_image_fetch import fetch_chat_image  # noqa: E402

# ---------------------------------------------------------------------------
# Cyber-neon visual system
# ---------------------------------------------------------------------------
BG = "#070B14"
SURFACE = "#0B1220"
PANEL = "#10192A"
PANEL_ALT = "#0A1322"
TEXT = "#F4F7FF"
MUTED = "#8EA7C9"
CYAN = "#00E8FF"
CYAN_SOFT = "#123B50"
PINK = "#FF2ACB"
PINK_SOFT = "#4D1644"
PURPLE = "#A855F7"
PURPLE_SOFT = "#2B1950"
RED = "#FF416C"
RED_SOFT = "#4B1825"
GREEN = "#46F59A"
GREEN_SOFT = "#123A2A"
WHITE = "#FFFFFF"
BORDER = "#263451"

COPYRIGHT_TEXT = "COPYRIGHT 2026 BY FRAGGLEPOWER666 - 666SOUNDsDESIGN"


def _asset_root() -> Path:
    """Return runtime asset directory for source and PyInstaller builds."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS")) / "assets"
    return Path(__file__).resolve().parent.parent / "assets"


def _settings_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
        return base / "666SOUNDsDESIGN" / "666ChatBackup"
    return Path.home() / ".config" / "666soundsdesign" / "666chatbackup"


DEFAULT_SETTINGS = {
    "default_export_dir": str(Path.home() / "Documents"),
    "remember_last_directory": True,
    "autosave_after_link_load": False,
    "line_endings": "Original",
    "verify_exports": True,
    "editor_font_size": 11,
    "show_banner": True,
    "animations": True,
    "window_mode": "Large",
    "language": "en",
    "integrate_images": True,
    "download_share_images": True,
    "open_image_browser_after_load": False,
    "preserve_raw_share_source": True,
}


TRANSLATIONS = {
    "en": {
        "CHAT SICHERN  •  WISSEN BEWAHREN": "SAVE CHATS  •  PRESERVE KNOWLEDGE",
        "⌂  ChatBackup": "⌂  ChatBackup",
        "▣  Chat-Bilder": "▣  Chat Images",
        "⌬  Struktur-Inspector": "⌬  Structure Inspector",
        "⚙  Einstellungen": "⚙  Settings",
        "🌐  Sprache": "🌐  Language",
        "❓  Hilfe": "❓  Help",
        "⇩  Privat / Manuell": "⇩  Private / Manual",
        "Privater / manueller Chat-Import": "Private / Manual Chat Import",
        "Chattext aus Zwischenablage analysieren": "Analyze Chat Text from Clipboard",
        "Privaten Chat im Browser öffnen": "Open Private Chat in Browser",
        "▤  Protokoll": "▤  Activity Log",
        "◉  Systemstatus": "◉  System Status",
        "ⓘ  Über": "ⓘ  About",
        "● BEREIT": "● READY",
        "● ARBEITET": "● WORKING",
        "1. Öffentlicher ChatGPT-Share-Link": "1. Public ChatGPT Share Link",
        "Aus Zwischenablage": "Paste from Clipboard",
        "Link laden": "Load Link",
        "Link leeren": "Clear Link",
        "2. Titel / Dateiname": "2. Title / File Name",
        "Modus: manuell": "Mode: manual",
        "3. Chatbackup / manueller Text": "3. Chat Backup / Manual Text",
        "Inhalt leeren": "Clear Content",
        "Alles markieren": "Select All",
        "Text einfügen": "Paste Text",
        "Bereit": "Ready",
        "Alle 5 Formate": "All 5 Formats",
        "Beenden": "Exit",
        "SYSTEMPRÜFUNG PASS — bereit.": "SYSTEM CHECK PASS — ready.",
        "Systemstatus": "System Status",
        "Chat-Bilder ansehen & auswählen": "View & Select Chat Images",
        "Lokales Bild +": "Local Image +",
        "Struktur-Inspector": "Structure Inspector",
        "Bitte zuerst einen Chat laden oder manuellen Chattext einfügen. Der Inspector zeigt die analysierte Struktur.": "Please load a chat or paste manual chat text first. The inspector shows the analyzed structure.",
        "Nachricht auswählen": "Select Message",
        "Komplette Struktur JSON": "Full Structure JSON",
        "Nachricht JSON": "Message JSON",
        "Schließen": "Close",
        "Einstellungen": "Settings",
        "Standard-Speicherordner": "Default Export Folder",
        "Wählen": "Browse",
        "Zeilenumbrüche": "Line Endings",
        "Editor-Schriftgröße": "Editor Font Size",
        "Startfenster": "Startup Window",
        "Groß": "Large",
        "Maximiert": "Maximized",
        "Letzten Speicherordner merken": "Remember Last Export Folder",
        "Nach Share-Link-Laden automatisch alle 5 Formate speichern": "Automatically save all 5 formats after loading a share link",
        "Export nach dem Schreiben bytegenau verifizieren": "Byte-verify exports after writing",
        "Cyber-Neon-Banner anzeigen": "Show Cyber-Neon Banner",
        "UI-Animationen / Fortschrittsanzeigen": "UI Animations / Progress Indicators",
        "Bilder in Portable-Backups integrieren": "Include Images in Portable Backups",
        "Direkt erreichbare Bilder aus Share-Chats herunterladen": "Download Directly Reachable Images from Shared Chats",
        "Chat-Bildbrowser nach dem Laden automatisch öffnen": "Open Chat Image Browser Automatically After Loading",
        "Original-Share-Quelldaten für Reparse/Archiv erhalten": "Preserve Original Share Source for Reparse / Archive",
        "Standard": "Defaults",
        "Abbrechen": "Cancel",
        "Speichern": "Save",
        "Zurücksetzen": "Reset",
        "Alle Einstellungen auf Standard zurücksetzen?": "Reset all settings to defaults?",
        "EINSTELLUNGEN — gespeichert.": "SETTINGS — saved.",
        "Lokale Zusatzbilder": "Local Additional Images",
        "Diese Funktion ist nur für zusätzliche lokale Bilder. Chat-Bilder werden im Bildbrowser ausgewählt.": "This function is only for additional local images. Chat images are selected in the image browser.",
        "Weitere hinzufügen": "Add More",
        "Auswahl entfernen": "Remove Selection",
        "Alle entfernen": "Remove All",
        "Fertig": "Done",
        "Original im Browser": "Open Original in Browser",
        "Vorschau wird geladen …": "Loading preview …",
        "Direkt erreichbar": "Directly Reachable",
        "Asset-Pointer / nur Metadaten": "Asset Pointer / Metadata Only",
        "Mit Backup speichern": "Include in Backup",
        "Großansicht": "Large Preview",
        "Browser": "Browser",
        "Download": "Download",
        "Ausgewählte herunterladen": "Download Selected",
        "Alle erreichbaren herunterladen": "Download All Reachable",
        "Bilder herunterladen": "Download Images",
        "Download abgeschlossen": "Download Complete",
        "Keine direkt erreichbaren Bilder": "No Directly Reachable Images",
        "Für die gewählte Auswahl sind keine direkt erreichbaren Bilddaten verfügbar.": "No directly reachable image data is available for the selected items.",
        "Alle auswählen": "Select All",
        "Keine": "None",
        "Nur direkt erreichbare": "Only Directly Reachable",
        "Lokale Zusatzbilder": "Local Additional Images",
        "Auswahl übernehmen": "Apply Selection",
        "Portables ChatBackup-Paket speichern": "Save Portable ChatBackup Package",
        "Kein Inhalt": "No Content",
        "Bitte zuerst einen Link laden oder Chattext einfügen.": "Please load a link or paste chat text first.",
        "Gespeichert": "Saved",
        "Speichern fehlgeschlagen": "Save Failed",
        "Alle Formate gespeichert": "All Formats Saved",
        "Automatischer Systemstatus": "Automatic System Status",
        "Protokoll": "Activity Log",
        "Über 666 ChatBackup": "About 666 ChatBackup",
        "Bitte warten": "Please Wait",
        "Es werden gerade Daten in den Editor eingefügt.": "Data is currently being inserted into the editor.",
        "Zwischenablage": "Clipboard",
        "Die Zwischenablage enthält keinen Text.": "The clipboard does not contain text.",
        "Link fehlt": "Missing Link",
        "Bitte zuerst einen öffentlichen ChatGPT-Share-Link eingeben.": "Please enter a public ChatGPT share link first.",
        "Chat-Export fehlgeschlagen": "Chat Export Failed",
        "Bildvorschau": "Image Preview",
        "Pillow ist nicht verfügbar; eine große Vorschau kann nicht erzeugt werden.": "Pillow is not available; a large preview cannot be created.",
        "Struktur-JSON": "Structure JSON",
        "Bitte zuerst eine Nachricht auswählen.": "Please select a message first.",
        "Struktur-JSON gespeichert": "Structure JSON Saved",
        "Portable Backup fehlgeschlagen": "Portable Backup Failed",
        "Datei erfolgreich gespeichert:\n\n": "File saved successfully:\n\n",
        "Systemstatus": "System Status",
        "Automatischer Systemstatus": "Automatic System Status",
        "Statusdatei konnte nicht gelesen werden:\n\n": "Could not read the status file:\n\n",
        "Noch keine Protokolleinträge.": "No activity log entries yet.",
        "Protokoll konnte nicht gelesen werden: ": "Could not read activity log: ",
        "Chat-Bilder: 0 · ausgewählt: 0": "Chat Images: 0 · selected: 0",
        "Weitere hinzufügen": "Add More",
        "Auswahl entfernen": "Remove Selection",
        "Alle entfernen": "Remove All",
        "Fertig": "Done",
        "Lokale Bilder verwalten": "Manage Local Images",
        "Zeilen: 1  •  Zeichen: 0": "Lines: 1  •  Characters: 0",
    },
    "de": {}
}

HELP_TEXT = {
    "en": """666 ChatBackup PC Tool — Help

QUICK START — PUBLIC SHARE LINK
1. Open the conversation in ChatGPT.
2. Use ChatGPT's Share / Teilen control near the conversation header or menu.
3. Create or update the public shared link, then choose Copy link.
4. Return to 666 ChatBackup, paste the link into “Public ChatGPT Share Link”, and click “Load Link”.
5. Review the result, inspect images/structure if needed, then export.

IMPORTANT PRIVACY NOTE
A public share link is not a private /c/ link. Anyone who receives the public share URL may be able to view the shared conversation. Do not create/share a public link for sensitive material unless that is acceptable to you. Remove/disable the shared link in ChatGPT when you no longer need it.

PRIVATE CHAT (/c/) — MANUAL WORKFLOW
Private ChatGPT /c/ URLs cannot be downloaded by this tool without your authenticated ChatGPT session. The tool does not bypass login or copy private session cookies. Instead:
1. Open the private chat in ChatGPT while you are logged in.
2. Copy the complete visible conversation text. For long chats, use ChatGPT/browser selection and copy as much of the conversation as available.
3. In 666 ChatBackup choose “Private / Manual” in the left menu, then “Analyze Chat Text from Clipboard”, or paste with Ctrl+Shift+V.
4. The tool analyzes explicit role markers such as “You said”, “User”, “Benutzer”, “Du”, “ChatGPT said”, “ChatGPT”, “Assistant” and Markdown headings.
5. If reliable role markers are present, the text is rebuilt into structured messages for JSON/JSONL, Structure Inspector and Portable Backup. If markers are not reliable, the complete paste is preserved as one manual message — the tool does not invent turns.
6. Copy/UI fields inside pasted code are still analyzed statically where possible.

MANUAL COPY / PASTE ANALYSIS
A manual paste is not treated as an unstructured blob anymore. After pasting, ChatBackup creates a manual-transcript analysis. Machine exports receive message IDs, roles, rendered text, raw source text, Copy/UI fields and warnings. Markdown is rebuilt from the recovered message structure. TXT/JavaScript use the normalized transcript content, while JSON/JSONL preserve the full machine structure.

WHEN CHATGPT SAYS THE CHAT IS FULL
Sometimes ChatGPT reports that the conversation is full and asks you to open a new chat. In that state the normal Share / Copy link control may no longer produce a usable link.

Observed temporary workaround (ChatGPT behavior can change; not guaranteed):
1. Enter an additional short prompt in the full conversation.
2. ChatGPT may remove/replace that last input and begin processing again.
3. While ChatGPT has started thinking/generating, the Share / Copy link control can briefly become available again.
4. Copy the share link immediately during that short window.
5. Once ChatGPT returns to the “chat full” state, sharing may stop working again.

This workaround is opportunistic, not a guaranteed API. If it does not work, use the private/manual copy workflow so the chat can still be archived.

GROUP CHATS / MULTI-PARTICIPANT HISTORY
ChatBackup v1.8 can preserve explicit participant identity when ChatGPT delivers it in structured share data. Each message can carry participantId, displayName, username, participant kind and resolution status. The machine JSON, JSONL, Raw Source and Structure Inspector keep this information.

For manually copied group history, labels such as “Alice:”, “Bob:” and “ChatGPT:” can be recovered as separate speakers. Generic names are only accepted when the transcript provides multiple explicit speaker labels; the tool does not guess identities. If participant information is missing from the source, the message remains UNRESOLVED instead of being assigned to a person.

Depending on the current ChatGPT product state, older group chats may be read-only or may not offer the same sharing controls as normal chats. If a public share link is unavailable, copy the visible group history and use Private / Manual. Images/files still require source URLs or asset metadata; plain clipboard text cannot recreate missing bytes.

STRUCTURE INSPECTOR
“Message JSON” saves the selected message. “Full Structure JSON” saves the complete structured inspector state. Portable ZIP also includes source/structure_inspector.json.

CHAT IMAGES
Shared-chat images are detected from structured share data. Directly reachable images can be previewed and downloaded immediately from the Chat Image Browser: use Download on one image, Download Selected for the checked images, or Download All Reachable for every image whose bytes can actually be fetched. Internal asset pointers without downloadable bytes are preserved as metadata. Manual clipboard text alone cannot recreate image bytes that were not copied; if images matter, prefer a public share link while it is still available.

PORTABLE BACKUP
Portable ZIP stores selected reachable images as real binary image files inside assets/ — not as Base64. If assets/ contains no images, the selected share assets were not directly downloadable, image integration/download was disabled, or the remote image request failed. Pointer-only images are still recorded in JSON/package_manifest.json with their status. The package also contains TXT, Markdown, JavaScript, JSON, JSONL, package_manifest.json and — when available — raw source artifacts for later re-parsing.

LANGUAGE
Choose English or Deutsch from Language in the left menu. The choice is saved and restored automatically on the next system start. English is the default on a first start.

SHORTCUTS
Ctrl+L: focus share-link field
F5: load share link
Ctrl+Shift+V: paste and analyze chat text
Ctrl+Shift+S: save all five formats
Ctrl+I: open chat image browser

LIMITS
Public share pages can be loaded without login. Private /c/ pages require the manual workflow unless a public share link is created in ChatGPT. Dynamic UI bindings, private asset bytes, deleted content and data never delivered/copied cannot be reconstructed. Visual parity is never claimed.
""",
    "de": """666 ChatBackup PC Tool — Hilfe

SCHNELLSTART — ÖFFENTLICHER SHARE-LINK
1. Den gewünschten Chat in ChatGPT öffnen.
2. In ChatGPT oben beim Chat bzw. im Menü „Teilen / Share“ öffnen.
3. Einen öffentlichen Freigabelink erstellen bzw. aktualisieren und „Link kopieren“ wählen.
4. Zurück in 666 ChatBackup den Link in „Öffentlicher ChatGPT-Share-Link“ einfügen und „Link laden“ anklicken.
5. Ergebnis prüfen, bei Bedarf Bilder und Struktur ansehen und anschließend exportieren.

WICHTIGER DATENSCHUTZHINWEIS
Ein öffentlicher Share-Link ist nicht dasselbe wie der private /c/-Link. Wer den öffentlichen Freigabelink erhält, kann den freigegebenen Chat möglicherweise ansehen. Für sensible Inhalte nur verwenden, wenn das für dich in Ordnung ist, und die Freigabe in ChatGPT wieder entfernen/deaktivieren, wenn du sie nicht mehr brauchst.

PRIVATER CHAT (/c/) — MANUELLER WORKFLOW
Private ChatGPT-/c/-Links kann dieses Tool ohne deine angemeldete ChatGPT-Sitzung nicht direkt herunterladen. Das Tool umgeht keine Anmeldung und übernimmt keine privaten Session-Cookies. Stattdessen:
1. Den privaten Chat in ChatGPT öffnen, während du angemeldet bist.
2. Den kompletten sichtbaren Chattext kopieren. Bei sehr langen Chats möglichst den gesamten verfügbaren Verlauf markieren und kopieren.
3. In 666 ChatBackup links „Privat / Manuell“ wählen und „Chattext aus Zwischenablage analysieren“ anklicken — oder Ctrl+Shift+V verwenden.
4. Das Tool erkennt explizite Rollenmarker wie „You said“, „User“, „Benutzer“, „Du“, „ChatGPT said“, „ChatGPT“, „Assistant“ sowie Markdown-Überschriften.
5. Sind verlässliche Rollenmarker vorhanden, wird der Text wieder in strukturierte Nachrichten zerlegt und für JSON/JSONL, Struktur-Inspector und Portable Backup aufbereitet. Sind keine sicheren Marker vorhanden, bleibt der komplette Text als eine manuelle Nachricht erhalten — es werden keine Gesprächswechsel erfunden.
6. Copy-/UI-Felder in eingefügtem Code werden weiterhin soweit möglich statisch analysiert.

MANUELLES KOPIEREN / EINFÜGEN / ANALYSIEREN
Ein manuell eingefügter Chat wird nicht mehr nur als großer Textblock behandelt. Nach dem Einfügen erzeugt ChatBackup eine Manual-Transcript-Analyse. Maschinenexporte erhalten Nachrichten-IDs, Rollen, gerenderten Text, erhaltenen Quelltext, Copy-/UI-Felder und Warnungen. Markdown wird aus der erkannten Nachrichtenstruktur neu aufgebaut. TXT/JavaScript verwenden den normalisierten Chatinhalt; JSON/JSONL erhalten die vollständige Maschinenstruktur.

WENN CHATGPT „CHAT VOLL“ MELDET
Manchmal meldet ChatGPT, dass der Chat voll ist und ein neuer Chat geöffnet werden soll. In diesem Zustand funktioniert „Teilen / Link kopieren“ häufig nicht mehr zuverlässig.

Beobachteter kurzfristiger Workaround (ChatGPT kann dieses Verhalten jederzeit ändern; keine Garantie):
1. Im vollen Chat noch eine zusätzliche kurze Eingabe senden.
2. ChatGPT kann diese letzte Eingabe wieder entfernen/ersetzen und erneut mit der Verarbeitung beginnen.
3. Sobald ChatGPT angefangen hat zu denken/generieren, kann der „Teilen / Link kopieren“-Button für kurze Zeit wieder funktionieren.
4. Den Share-Link in diesem kurzen Zeitfenster sofort kopieren.
5. Sobald ChatGPT wieder „Chat voll“ meldet, kann das Teilen erneut nicht mehr funktionieren.

Das ist kein garantierter API-Weg, sondern ein beobachtetes Zeitfenster. Wenn es nicht klappt, den privaten/manuellen Kopierworkflow verwenden, damit der Chat trotzdem archiviert werden kann.

GRUPPENCHATS / MEHRERE TEILNEHMENDE
ChatBackup v1.8 erhält explizite Teilnehmeridentitäten, wenn ChatGPT sie im strukturierten Share-Datensatz liefert. Jede Nachricht kann participantId, Anzeigename, Benutzername, Teilnehmerart und Auflösungsstatus enthalten. Maschinen-JSON, JSONL, Raw Source und Struktur-Inspector bewahren diese Informationen.

Bei manuell kopierten Gruppenverläufen können Marker wie „Alice:“, „Bob:“ und „ChatGPT:“ als getrennte Sprecher rekonstruiert werden. Freie Namen werden nur akzeptiert, wenn der kopierte Verlauf mehrere eindeutige Sprecherkennzeichnungen liefert; das Tool erfindet keine Identitäten. Fehlen Teilnehmerdaten in der Quelle, bleibt die Nachricht UNRESOLVED, statt einer Person zugeschrieben zu werden.

Je nach aktuellem ChatGPT-Produktstand können ältere Gruppenchats schreibgeschützt sein oder andere Freigabemöglichkeiten besitzen als normale Chats. Ist kein öffentlicher Share-Link verfügbar, den sichtbaren Gruppenverlauf kopieren und „Privat / Manuell“ verwenden. Bilder/Dateien benötigen weiterhin erreichbare URLs oder Asset-Metadaten; reiner Zwischenablage-Text kann fehlende Bytes nicht rekonstruieren.

STRUKTUR-INSPECTOR
„Nachricht JSON“ speichert die ausgewählte Nachricht. „Komplette Struktur JSON“ speichert den vollständigen strukturierten Inspector-Zustand. Das Portable-ZIP enthält zusätzlich automatisch source/structure_inspector.json.

CHAT-BILDER
Bilder aus einem Share-Chat werden aus den strukturierten Freigabedaten erkannt. Direkt erreichbare Bilder können angesehen und gespeichert werden. Interne Asset-Pointer ohne erreichbare Bildbytes bleiben als Metadaten erhalten. Aus rein manuell kopiertem Text können Bildbytes nicht wiederhergestellt werden, wenn sie nicht mitkopiert wurden. Wenn Bilder wichtig sind, möglichst rechtzeitig einen öffentlichen Share-Link sichern.

PORTABLE BACKUP
Das Portable-ZIP enthält TXT, Markdown, JavaScript, JSON, JSONL, ausgewählte Bilder, package_manifest.json und — wenn vorhanden — Raw-Source-Artefakte für spätere Neuinterpretation.

SPRACHE
Links im Menü kann English oder Deutsch gewählt werden. Die Auswahl wird gespeichert und beim nächsten Systemstart wiederhergestellt. Beim ersten Start ist Englisch Standard.

TASTENKÜRZEL
Ctrl+L: Share-Link-Feld fokussieren
F5: Share-Link laden
Ctrl+Shift+V: Chattext einfügen und analysieren
Ctrl+Shift+S: alle fünf Formate speichern
Ctrl+I: Chat-Bildbrowser öffnen

GRENZEN
Öffentliche Share-Seiten können ohne Anmeldung geladen werden. Private /c/-Seiten benötigen den manuellen Workflow, solange in ChatGPT kein öffentlicher Share-Link erstellt wurde. Dynamische UI-Bindungen, private Bildbytes, gelöschte Inhalte und Daten, die nie geliefert oder kopiert wurden, können nicht rekonstruiert werden. Visuelle Parität wird nicht behauptet.
"""
}


class NeonButton(tk.Button):
    """Tk button with a lightweight neon hover effect and no external runtime deps."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        text: str,
        command: Callable[[], None] | None = None,
        accent: str = CYAN,
        surface: str = SURFACE,
        danger: bool = False,
        compact: bool = False,
        **kwargs: object,
    ) -> None:
        self.accent = RED if danger else accent
        self.surface = RED_SOFT if danger else surface
        self.hover_bg = self._blend(self.surface, self.accent, 0.30 if not danger else 0.24)
        super().__init__(
            master,
            text=text,
            command=command,
            bg=self.surface,
            fg=TEXT,
            activebackground=self.hover_bg,
            activeforeground=WHITE,
            disabledforeground="#60708A",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.accent,
            highlightcolor=self.accent,
            cursor="hand2",
            padx=10 if compact else 14,
            pady=6 if compact else 9,
            font=("Segoe UI", 9 if compact else 10, "bold"),
            takefocus=True,
            **kwargs,
        )
        self.bind("<Enter>", self._enter, add="+")
        self.bind("<Leave>", self._leave, add="+")
        self.bind("<FocusIn>", self._enter, add="+")
        self.bind("<FocusOut>", self._leave, add="+")

    @staticmethod
    def _blend(a: str, b: str, ratio: float) -> str:
        def rgb(value: str) -> tuple[int, int, int]:
            value = value.lstrip("#")
            return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]

        ar, ag, ab = rgb(a)
        br, bg, bb = rgb(b)
        vals = [round(x + (y - x) * ratio) for x, y in ((ar, br), (ag, bg), (ab, bb))]
        return "#" + "".join(f"{v:02X}" for v in vals)

    def _enter(self, _event: tk.Event | None = None) -> None:
        if str(self.cget("state")) == "disabled":
            return
        self.configure(bg=self.hover_bg, fg=WHITE, highlightthickness=2)

    def _leave(self, _event: tk.Event | None = None) -> None:
        if str(self.cget("state")) == "disabled":
            return
        self.configure(bg=self.surface, fg=TEXT, highlightthickness=1)


class NeonPanel(tk.Frame):
    def __init__(self, master: tk.Misc, *, accent: str = BORDER, bg: str = PANEL, **kwargs: object) -> None:
        super().__init__(
            master,
            bg=bg,
            highlightthickness=1,
            highlightbackground=accent,
            bd=0,
            **kwargs,
        )


class ChatBackupApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"666 ChatBackup PC Tool v{APP_VERSION}")
        self.configure(bg=BG)

        self.result_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self.current_source_url = ""
        self.current_source_mode = "manual"
        self.current_title = "ChatGPT Backup"
        self.current_chat: ChatBackup | None = None
        self.manual_images: list[Path] = []
        self.chat_image_selection: set[str] = set()
        self.chat_image_selection_initialized = False
        self.chat_image_preview_cache: dict[str, tuple[bytes, str]] = {}
        self.chat_image_preview_errors: dict[str, str] = {}
        self.editor_programmatic_change = False
        self.insert_in_progress = False
        self.insert_cancelled = False
        self._last_action_layout = ""
        self._resize_job: str | None = None
        self._photos: dict[str, tk.PhotoImage] = {}
        self.bootstrap_status_file = os.environ.get("CHATBACKUP_BOOTSTRAP_STATUS_FILE", "")

        self.settings_path = _settings_dir() / "settings.json"
        self.log_path = _settings_dir() / "activity.log"
        self.settings = self._load_settings()
        self.last_directory = str(self.settings.get("default_export_dir") or Path.home() / "Documents")

        self._configure_window_geometry()
        self._build_style()
        self._load_images()
        self._build_ui()
        self._bind_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(150, self._poll_result_queue)
        self.after(250, self._update_editor_stats)
        self.after(350, self._apply_window_mode)
        self._log(f"START v{APP_VERSION}")

    # ------------------------------------------------------------------
    # Settings / startup
    # ------------------------------------------------------------------
    def _load_settings(self) -> dict[str, object]:
        settings = dict(DEFAULT_SETTINGS)
        try:
            if self.settings_path.exists():
                loaded = json.loads(self.settings_path.read_text(encoding="utf-8-sig"))
                if isinstance(loaded, dict):
                    for key in DEFAULT_SETTINGS:
                        if key in loaded:
                            settings[key] = loaded[key]
        except Exception:
            pass
        return settings

    def _save_settings(self) -> None:
        try:
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            self.settings_path.write_text(
                json.dumps(self.settings, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except Exception as exc:
            self._log(f"SETTINGS_SAVE_FAIL {exc}")

    def _lang(self) -> str:
        value = str(self.settings.get("language", "en")).lower()
        return value if value in {"en", "de"} else "en"

    def _t(self, text: str) -> str:
        if self._lang() == "de":
            return text
        return TRANSLATIONS.get("en", {}).get(text, text)

    def _bi(self, english: str, german: str) -> str:
        return english if self._lang() == "en" else german

    def _set_language(self, language: str) -> None:
        language = language.lower()
        if language not in {"en", "de"}:
            return
        if self._lang() == language:
            return
        self.settings["language"] = language
        self._save_settings()
        self._log(f"LANGUAGE_SET {language}")
        # Rebuild the visible UI immediately while preserving loaded content/state.
        editor_text = self.editor.get("1.0", "end-1c") if hasattr(self, "editor") else ""
        url_text = self.url_var.get() if hasattr(self, "url_var") else ""
        title_text = self.title_var.get() if hasattr(self, "title_var") else self.current_title
        for child in list(self.winfo_children()):
            child.destroy()
        self._build_ui()
        self.url_var.set(url_text)
        self.title_var.set(title_text)
        if editor_text:
            self.editor.insert("1.0", editor_text)
        self._update_image_summary()
        self._update_editor_stats()
        self.status_var.set(self._t("Bereit"))

    def open_language_selector(self) -> None:
        win = tk.Toplevel(self)
        win.title("666 ChatBackup — " + self._t("🌐  Sprache").strip("🌐  "))
        win.configure(bg=BG)
        win.geometry("460x280")
        win.resizable(False, False)
        panel = NeonPanel(win, accent=PURPLE, bg=PANEL)
        panel.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(panel, text=self._t("🌐  Sprache").strip("🌐  "), bg=PANEL, fg=PINK, font=("Segoe UI", 18, "bold")).pack(pady=(24, 8))
        desc = "Choose the language for the entire application. Your choice is saved for the next system start." if self._lang() == "en" else "Wähle die Sprache für die gesamte Anwendung. Die Auswahl wird für den nächsten Systemstart gespeichert."
        tk.Label(panel, text=desc, bg=PANEL, fg=TEXT, wraplength=390, justify="center", font=("Segoe UI", 10)).pack(padx=20, pady=(0, 18))
        row = tk.Frame(panel, bg=PANEL)
        row.pack(fill="x", padx=26, pady=8)
        row.grid_columnconfigure(0, weight=1); row.grid_columnconfigure(1, weight=1)
        NeonButton(row, text="English" + ("  ✓" if self._lang()=="en" else ""), command=lambda: (win.destroy(), self._set_language("en")), accent=CYAN).grid(row=0,column=0,sticky="ew",padx=6)
        NeonButton(row, text="Deutsch" + ("  ✓" if self._lang()=="de" else ""), command=lambda: (win.destroy(), self._set_language("de")), accent=PINK).grid(row=0,column=1,sticky="ew",padx=6)

    def show_help(self) -> None:
        win = tk.Toplevel(self)
        win.title("666 ChatBackup — " + self._t("❓  Hilfe").strip("❓  "))
        win.configure(bg=BG)
        win.geometry("980x720")
        panel = NeonPanel(win, accent=CYAN, bg=PANEL)
        panel.pack(fill="both", expand=True, padx=12, pady=12)
        top = tk.Frame(panel, bg=PANEL)
        top.pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(top, text=self._t("❓  Hilfe").strip("❓  "), bg=PANEL, fg=PINK, font=("Segoe UI", 18, "bold")).pack(side="left")
        text = tk.Text(panel, bg="#050A12", fg="#EAF2FF", insertbackground=CYAN, wrap="word", relief="flat", padx=16, pady=14, font=("Segoe UI", 10))
        text.pack(fill="both", expand=True, padx=12, pady=6)
        text.insert("1.0", HELP_TEXT[self._lang()])
        text.configure(state="disabled")
        bottom = tk.Frame(panel, bg=PANEL)
        bottom.pack(fill="x", padx=12, pady=(6, 12))
        NeonButton(bottom, text="English", command=lambda: self._replace_help_text(text, "en"), accent=CYAN, compact=True).pack(side="left", padx=4)
        NeonButton(bottom, text="Deutsch", command=lambda: self._replace_help_text(text, "de"), accent=PINK, compact=True).pack(side="left", padx=4)
        NeonButton(bottom, text=self._t("Schließen"), command=win.destroy, accent=PURPLE, compact=True).pack(side="right", padx=4)

    @staticmethod
    def _replace_help_text(widget: tk.Text, language: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", HELP_TEXT[language])
        widget.configure(state="disabled")

    def _localize_runtime(self, text: object) -> str:
        value = str(text)
        if self._lang() == "de":
            return value
        exact = {
            "Bitte einen ChatGPT-Share-Link eingeben.": "Please enter a ChatGPT share link.",
            "Der eingegebene Link ist ungültig.": "The entered link is invalid.",
            "Der Link gehört nicht zu ChatGPT.": "The link does not belong to ChatGPT.",
            "Zeitüberschreitung beim Laden des Share-Links.": "Timed out while loading the share link.",
            "Unbekannter Downloadfehler.": "Unknown download error.",
            "Keine Gesprächsdaten im Share-Link.": "No conversation data found in the share link.",
            "Im Share-Link wurden keine sichtbaren Nachrichten gefunden.": "No visible messages were found in the share link.",
            "Die Datei wurde nach dem Schreiben nicht gefunden.": "The file was not found after writing.",
            "Für dieses Chat-Bild ist keine direkt erreichbare Bild-URL vorhanden.": "No directly reachable image URL is available for this chat image.",
            "Das Bild ist für die Vorschau größer als 30 MB.": "The image is larger than 30 MB and cannot be previewed.",
            "Der Bildserver hat keine Bilddaten geliefert.": "The image server returned no image data.",
        }
        if value in exact:
            return exact[value]
        prefixes = [
            ("Netzwerkfehler: ", "Network error: "),
            ("ZIP-CRC-Prüfung fehlgeschlagen bei: ", "ZIP CRC check failed for: "),
            ("Protokoll konnte nicht gelesen werden: ", "Could not read activity log: "),
        ]
        for old, new in prefixes:
            if value.startswith(old):
                return new + value[len(old):]
        return value

    def _configure_window_geometry(self) -> None:
        self.update_idletasks()
        sw = max(self.winfo_screenwidth(), 1200)
        sh = max(self.winfo_screenheight(), 760)
        width = min(1600, max(1240, sw - 120))
        height = min(930, max(720, sh - 130))
        x = max(0, (sw - width) // 2)
        y = max(0, (sh - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(1040, 680)

    def _apply_window_mode(self) -> None:
        if self.settings.get("window_mode") in {"Maximized", "Maximiert"} and os.name == "nt":
            try:
                self.state("zoomed")
            except tk.TclError:
                pass

    def _build_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Neon.Horizontal.TProgressbar",
            troughcolor="#07101E",
            background=PINK,
            lightcolor=PINK,
            darkcolor=PURPLE,
            bordercolor=CYAN,
            thickness=16,
        )
        style.configure(
            "Neon.Vertical.TScrollbar",
            troughcolor="#08111E",
            background="#243B5E",
            bordercolor="#08111E",
            arrowcolor=CYAN,
        )
        style.configure(
            "Neon.Horizontal.TScrollbar",
            troughcolor="#08111E",
            background="#243B5E",
            bordercolor="#08111E",
            arrowcolor=CYAN,
        )
        style.configure(
            "Neon.TCombobox",
            fieldbackground="#07101E",
            background=PANEL,
            foreground=TEXT,
            arrowcolor=CYAN,
            bordercolor=CYAN,
            lightcolor=CYAN,
            darkcolor=CYAN,
            padding=5,
        )

    def _load_images(self) -> None:
        assets = _asset_root()
        for key, name in {
            "banner": "header_banner.png",
            "logo": "app_logo.png",
            "icon": "app_icon_64.png",
        }.items():
            path = assets / name
            if not path.exists():
                continue
            try:
                self._photos[key] = tk.PhotoImage(file=str(path))
            except tk.TclError:
                pass
        if "icon" in self._photos:
            try:
                self.iconphoto(True, self._photos["icon"])
            except tk.TclError:
                pass
        ico = assets / "chatbackup.ico"
        if ico.exists():
            try:
                self.iconbitmap(default=str(ico))
            except tk.TclError:
                pass

    def _bind_shortcuts(self) -> None:
        self.bind_all("<Control-l>", lambda _e: self._focus_url())
        self.bind_all("<Control-L>", lambda _e: self._focus_url())
        self.bind_all("<F5>", lambda _e: self.start_link_load())
        self.bind_all("<Control-Shift-V>", lambda _e: self.paste_text())
        self.bind_all("<Control-Shift-v>", lambda _e: self.paste_text())
        self.bind_all("<Control-Shift-S>", lambda _e: self.save_all())
        self.bind_all("<Control-Shift-s>", lambda _e: self.save_all())
        self.bind_all("<Control-i>", lambda _e: self.open_chat_image_browser())
        self.bind_all("<Control-I>", lambda _e: self.open_chat_image_browser())

    def _focus_url(self) -> str:
        self.url_entry.focus_set()
        self.url_entry.selection_range(0, "end")
        return "break"

    # ------------------------------------------------------------------
    # Main GUI
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.banner_frame = tk.Frame(self, bg=BG, height=190)
        self.banner_frame.grid(row=0, column=0, sticky="ew")
        self.banner_frame.grid_propagate(False)
        self._build_banner(self.banner_frame)
        if not bool(self.settings.get("show_banner", True)):
            self.banner_frame.grid_remove()

        body = tk.Frame(self, bg=BG, padx=12, pady=10)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        self.sidebar = NeonPanel(body, accent=PURPLE, bg="#090F1B", width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 10))
        self.sidebar.grid_propagate(False)
        self._build_sidebar(self.sidebar)

        main = tk.Frame(body, bg=BG)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(2, weight=1)

        self._build_link_panel(main)
        self._build_meta_panel(main)
        self._build_editor_panel(main)
        self._build_progress(main)
        self._build_actions(main)

        self._build_footer()
        self.bind("<Configure>", self._on_root_configure, add="+")
        self.after_idle(self._layout_action_buttons)

    def _build_banner(self, master: tk.Misc) -> None:
        canvas = tk.Canvas(master, bg=BG, height=190, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)
        self.banner_canvas = canvas
        if "banner" in self._photos:
            img = self._photos["banner"]
            canvas.create_image(0, 0, image=img, anchor="nw", tags="bannerimage")
        else:
            canvas.create_rectangle(0, 0, 2000, 250, fill="#0A1130", outline="")

        # dark glass strip: practical readable app identification over the image
        canvas.create_rectangle(0, 0, 2000, 45, fill="#060B17", outline="", stipple="gray50")
        title_text = f"666 ChatBackup PC Tool  •  v{APP_VERSION}"
        # layered text creates a subtle laser-neon glow without external GUI libraries
        for dx, dy, glow in ((-1, 0, "#4D1644"), (1, 0, "#4D1644"), (0, -1, "#3B185D"), (0, 1, "#3B185D")):
            canvas.create_text(
                18 + dx,
                22 + dy,
                anchor="w",
                text=title_text,
                fill=glow,
                font=("Segoe UI", 16, "bold"),
            )
        canvas.create_text(
            18,
            22,
            anchor="w",
            text=title_text,
            fill=PINK,
            font=("Segoe UI", 16, "bold"),
        )
        canvas.create_text(
            520,
            22,
            anchor="w",
            text=self._t("CHAT SICHERN  •  WISSEN BEWAHREN"),
            fill=CYAN,
            font=("Segoe UI", 10, "bold"),
        )
        canvas.bind("<Configure>", self._center_banner_image, add="+")

    def _center_banner_image(self, _event: tk.Event | None = None) -> None:
        if "banner" not in self._photos:
            return
        width = self.banner_canvas.winfo_width()
        img = self._photos["banner"]
        x = max(0, (width - img.width()) // 2)
        self.banner_canvas.coords("bannerimage", x, 0)

    def _build_sidebar(self, master: tk.Frame) -> None:
        logo_box = tk.Frame(master, bg="#090F1B")
        logo_box.pack(fill="x", padx=10, pady=(12, 8))
        if "logo" in self._photos:
            tk.Label(logo_box, image=self._photos["logo"], bg="#090F1B", bd=0).pack(pady=(0, 6))
        tk.Label(
            master,
            text="666GPT CHATBACKUP",
            bg="#090F1B",
            fg=CYAN,
            font=("Segoe UI", 11, "bold"),
        ).pack(pady=(0, 12))

        NeonButton(master, text=self._t("⌂  ChatBackup"), command=lambda: self.editor.focus_set(), accent=PINK).pack(
            fill="x", padx=12, pady=4
        )
        NeonButton(master, text=self._t("▣  Chat-Bilder"), command=self.open_chat_image_browser, accent=PINK).pack(
            fill="x", padx=12, pady=4
        )
        NeonButton(master, text=self._t("⌬  Struktur-Inspector"), command=self.open_structure_inspector, accent=CYAN).pack(
            fill="x", padx=12, pady=4
        )
        NeonButton(master, text=self._t("⚙  Einstellungen"), command=self.open_settings, accent=PURPLE).pack(
            fill="x", padx=12, pady=4
        )
        NeonButton(master, text=f"{self._t('🌐  Sprache')}: {self._lang().upper()}", command=self.open_language_selector, accent=CYAN).pack(
            fill="x", padx=12, pady=4
        )
        NeonButton(master, text=self._t("⇩  Privat / Manuell"), command=self.open_private_manual_import, accent=PURPLE).pack(
            fill="x", padx=12, pady=4
        )
        NeonButton(master, text=self._t("❓  Hilfe"), command=self.show_help, accent=PINK).pack(
            fill="x", padx=12, pady=4
        )
        NeonButton(master, text=self._t("▤  Protokoll"), command=self.show_log, accent=CYAN).pack(
            fill="x", padx=12, pady=4
        )
        NeonButton(master, text=self._t("◉  Systemstatus"), command=self.show_system_status, accent=GREEN).pack(
            fill="x", padx=12, pady=4
        )
        NeonButton(master, text=self._t("ⓘ  Über"), command=self.show_about, accent=PURPLE).pack(
            fill="x", padx=12, pady=4
        )

        self.side_status_var = tk.StringVar(value=self._t("● BEREIT"))
        tk.Label(
            master,
            textvariable=self.side_status_var,
            bg="#090F1B",
            fg=GREEN,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(side="bottom", fill="x", padx=14, pady=14)

    def _section_title(self, master: tk.Misc, text: str, accent: str) -> tk.Label:
        return tk.Label(master, text=text, bg=master.cget("bg"), fg=accent, font=("Segoe UI", 10, "bold"))

    def _build_link_panel(self, master: tk.Frame) -> None:
        panel = NeonPanel(master, accent=CYAN, bg=PANEL)
        panel.grid(row=0, column=0, sticky="ew", pady=(0, 9))
        panel.grid_columnconfigure(0, weight=1)
        self._section_title(panel, self._t("1. Öffentlicher ChatGPT-Share-Link"), CYAN).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(9, 5)
        )

        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(
            panel,
            textvariable=self.url_var,
            bg="#07101E",
            fg=TEXT,
            insertbackground=WHITE,
            selectbackground=PURPLE,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#2A476E",
            highlightcolor=CYAN,
            font=("Segoe UI", 10),
        )
        self.url_entry.grid(row=1, column=0, sticky="ew", padx=(12, 8), pady=(0, 10), ipady=7)

        self.paste_link_button = NeonButton(
            panel, text=self._t("Aus Zwischenablage"), command=self.paste_link, accent=CYAN, compact=True
        )
        self.paste_link_button.grid(row=1, column=1, padx=4, pady=(0, 10))
        self.load_button = NeonButton(
            panel, text=self._t("Link laden"), command=self.start_link_load, accent=PINK, surface=PINK_SOFT, compact=True
        )
        self.load_button.grid(row=1, column=2, padx=4, pady=(0, 10))
        self.clear_link_button = NeonButton(
            panel, text=self._t("Link leeren"), command=lambda: self.url_var.set(""), accent=PURPLE, compact=True
        )
        self.clear_link_button.grid(row=1, column=3, padx=(4, 12), pady=(0, 10))

    def _build_meta_panel(self, master: tk.Frame) -> None:
        panel = NeonPanel(master, accent=PURPLE, bg=PANEL_ALT)
        panel.grid(row=1, column=0, sticky="ew", pady=(0, 9))
        panel.grid_columnconfigure(0, weight=1)
        self._section_title(panel, self._t("2. Titel / Dateiname"), PURPLE).grid(
            row=0, column=0, sticky="w", padx=12, pady=(8, 4)
        )
        self.title_var = tk.StringVar(value=self.current_title)
        self.title_entry = tk.Entry(
            panel,
            textvariable=self.title_var,
            bg="#07101E",
            fg=TEXT,
            insertbackground=WHITE,
            selectbackground=PURPLE,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#40335E",
            highlightcolor=PINK,
            font=("Segoe UI", 10),
        )
        self.title_entry.grid(row=1, column=0, sticky="ew", padx=(12, 8), pady=(0, 9), ipady=6)
        self.mode_var = tk.StringVar(value=self._bi("Mode: manual", "Modus: manuell"))
        tk.Label(
            panel,
            textvariable=self.mode_var,
            bg=PANEL_ALT,
            fg=MUTED,
            font=("Segoe UI", 9),
            anchor="e",
        ).grid(row=1, column=1, sticky="e", padx=(0, 12), pady=(0, 5))

        image_row = tk.Frame(panel, bg=PANEL_ALT)
        image_row.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        image_row.grid_columnconfigure(0, weight=1)
        self.image_summary_var = tk.StringVar(value=self._bi("Chat Images: 0 · selected: 0", "Chat-Bilder: 0 · ausgewählt: 0"))
        tk.Label(
            image_row,
            textvariable=self.image_summary_var,
            bg=PANEL_ALT,
            fg=CYAN,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        NeonButton(
            image_row,
            text=self._t("Chat-Bilder ansehen & auswählen"),
            command=self.open_chat_image_browser,
            accent=PINK,
            surface=PINK_SOFT,
            compact=True,
        ).grid(row=0, column=1, padx=4)
        NeonButton(image_row, text=self._t("Lokales Bild +"), command=self.add_images, accent=PURPLE, compact=True).grid(
            row=0, column=2, padx=(4, 0)
        )

    def _build_editor_panel(self, master: tk.Frame) -> None:
        panel = NeonPanel(master, accent=PINK, bg=PANEL)
        panel.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = tk.Frame(panel, bg=PANEL)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 6))
        header.grid_columnconfigure(0, weight=1)
        self._section_title(header, self._t("3. Chatbackup / manueller Text"), PINK).grid(row=0, column=0, sticky="w")
        self.editor_stats_var = tk.StringVar(value=self._bi("Lines: 1  •  Characters: 0", "Zeilen: 1  •  Zeichen: 0"))
        tk.Label(header, textvariable=self.editor_stats_var, bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).grid(
            row=0, column=1, sticky="e", padx=(8, 12)
        )
        NeonButton(header, text=self._t("Inhalt leeren"), command=self.clear_editor, accent=RED, compact=True).grid(
            row=0, column=2, padx=3
        )
        NeonButton(header, text=self._t("Alles markieren"), command=self.select_all, accent=PURPLE, compact=True).grid(
            row=0, column=3, padx=3
        )
        self.paste_text_button = NeonButton(
            header, text=self._t("Text einfügen"), command=self.paste_text, accent=CYAN, compact=True
        )
        self.paste_text_button.grid(row=0, column=4, padx=(3, 0))

        text_frame = tk.Frame(panel, bg=PANEL)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        self.editor = tk.Text(
            text_frame,
            wrap="word",
            undo=True,
            bg="#050A12",
            fg="#EAF2FF",
            insertbackground=CYAN,
            selectbackground="#4D1B71",
            selectforeground=WHITE,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground="#173557",
            highlightcolor=PINK,
            padx=14,
            pady=12,
            font=("Consolas", int(self.settings.get("editor_font_size", 11))),
        )
        yscroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.editor.yview, style="Neon.Vertical.TScrollbar")
        xscroll = ttk.Scrollbar(
            text_frame, orient="horizontal", command=self.editor.xview, style="Neon.Horizontal.TScrollbar"
        )
        self.editor.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.editor.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        self.editor.bind("<<Modified>>", self._on_editor_modified)

    def _build_progress(self, master: tk.Frame) -> None:
        self.progress_frame = tk.Frame(master, bg=BG)
        self.progress_frame.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        self.progress_frame.grid_columnconfigure(1, weight=1)
        self.progress_label_var = tk.StringVar(value=self._t("Bereit"))
        tk.Label(
            self.progress_frame,
            textvariable=self.progress_label_var,
            bg=BG,
            fg=CYAN,
            font=("Segoe UI", 9, "bold"),
            width=24,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(2, 8))
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            mode="determinate",
            maximum=100,
            style="Neon.Horizontal.TProgressbar",
        )
        self.progress.grid(row=0, column=1, sticky="ew")
        self.progress_frame.grid_remove()

    def _build_actions(self, master: tk.Frame) -> None:
        self.action_bar = tk.Frame(master, bg=BG)
        self.action_bar.grid(row=4, column=0, sticky="ew")
        self.action_buttons = [
            NeonButton(self.action_bar, text="TXT", command=lambda: self.save_single("txt"), accent=CYAN),
            NeonButton(self.action_bar, text="Markdown", command=lambda: self.save_single("md"), accent=PURPLE),
            NeonButton(self.action_bar, text="JavaScript", command=lambda: self.save_single("js"), accent=CYAN),
            NeonButton(self.action_bar, text="Maschinen-JSON", command=lambda: self.save_single("json"), accent=GREEN),
            NeonButton(
                self.action_bar,
                text=self._t("Alle 5 Formate"),
                command=self.save_all,
                accent=PINK,
                surface=PINK_SOFT,
            ),
            NeonButton(
                self.action_bar,
                text="Portable ZIP + Bilder",
                command=self.save_portable_zip,
                accent=PURPLE,
                surface=PURPLE_SOFT,
            ),
            NeonButton(self.action_bar, text=self._t("Beenden"), command=self.on_close, danger=True),
        ]

    def _build_footer(self) -> None:
        footer = tk.Frame(self, bg="#050912", height=36, highlightthickness=1, highlightbackground=PURPLE)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)
        footer.grid_columnconfigure(1, weight=1)
        self.status_var = tk.StringVar(value="SYSTEMPRÜFUNG PASS — bereit.")
        tk.Label(
            footer,
            textvariable=self.status_var,
            bg="#050912",
            fg=GREEN,
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=12, pady=7)
        tk.Label(
            footer,
            text=COPYRIGHT_TEXT,
            bg="#050912",
            fg="#A9BEE8",
            font=("Segoe UI", 9, "bold"),
            anchor="center",
        ).grid(row=0, column=1, sticky="ew", padx=10)
        NeonButton(
            footer,
            text=self._t("Systemstatus"),
            command=self.show_system_status,
            accent=GREEN,
            surface="#0D241C",
            compact=True,
        ).grid(row=0, column=2, sticky="e", padx=8, pady=3)

    def _on_root_configure(self, _event: tk.Event) -> None:
        if self._resize_job:
            try:
                self.after_cancel(self._resize_job)
            except tk.TclError:
                pass
        self._resize_job = self.after(100, self._layout_action_buttons)

    def _layout_action_buttons(self) -> None:
        self._resize_job = None
        if not hasattr(self, "action_bar"):
            return
        width = self.winfo_width()
        layout = "wide" if width >= 1500 else "compact"
        if layout == self._last_action_layout:
            return
        self._last_action_layout = layout
        for button in self.action_buttons:
            button.grid_forget()
        for col in range(7):
            self.action_bar.grid_columnconfigure(col, weight=0)
        if layout == "wide":
            for col in range(7):
                self.action_bar.grid_columnconfigure(col, weight=1, uniform="actions")
            for idx, button in enumerate(self.action_buttons):
                button.grid(row=0, column=idx, sticky="ew", padx=3, pady=2)
        else:
            for col in range(4):
                self.action_bar.grid_columnconfigure(col, weight=1, uniform="actions")
            positions = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 3)]
            for button, (row, col) in zip(self.action_buttons, positions):
                button.grid(row=row, column=col, sticky="ew", padx=4, pady=3)

    # ------------------------------------------------------------------
    # Progress / chunked insertion
    # ------------------------------------------------------------------
    def _show_progress(self, label: str, *, indeterminate: bool = False) -> None:
        self.progress_frame.grid()
        self.progress_label_var.set(label)
        self.progress_var.set(0)
        if indeterminate:
            self.progress.configure(mode="indeterminate")
            self.progress.start(10)
        else:
            self.progress.stop()
            self.progress.configure(mode="determinate")

    def _hide_progress_later(self, delay: int = 850) -> None:
        def hide() -> None:
            self.progress.stop()
            self.progress.configure(mode="determinate")
            self.progress_var.set(0)
            self.progress_frame.grid_remove()

        self.after(delay, hide)

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        for button in (self.load_button, self.paste_text_button, self.paste_link_button, self.clear_link_button):
            button.configure(state=state)
        self.side_status_var.set("● ARBEITET" if busy else "● BEREIT")

    def _start_chunked_insert(
        self,
        text: str,
        *,
        replace: bool,
        label: str,
        on_complete: Callable[[], None] | None = None,
    ) -> None:
        if self.insert_in_progress:
            messagebox.showinfo(self._t("Bitte warten"), self._t("Es werden gerade Daten in den Editor eingefügt."))
            return
        self.insert_in_progress = True
        self.insert_cancelled = False
        self._set_busy(True)
        self._show_progress(f"{label} 0%")
        self.editor_programmatic_change = replace
        if replace:
            self.editor.delete("1.0", "end")
        total = max(len(text), 1)
        # ~32 KiB per UI tick: keeps even multi-MB chat text responsive.
        chunk_size = 32768 if bool(self.settings.get("animations", True)) else max(len(text), 1)
        pos = 0
        insert_index = "1.0" if replace else "insert"

        def step() -> None:
            nonlocal pos, insert_index
            if self.insert_cancelled:
                finish(cancelled=True)
                return
            end = min(pos + chunk_size, len(text))
            chunk = text[pos:end]
            if chunk:
                self.editor.insert(insert_index, chunk)
                if not replace:
                    insert_index = "insert"
                else:
                    insert_index = "end-1c"
            pos = end
            pct = int(round((pos / total) * 100))
            self.progress_var.set(pct)
            self.progress_label_var.set(f"{label} {pct}%")
            if pos < len(text):
                self.after(1, step)
            else:
                finish(cancelled=False)

        def finish(*, cancelled: bool) -> None:
            self.insert_in_progress = False
            self.editor_programmatic_change = False
            self._set_busy(False)
            self.editor.edit_modified(False)
            self._update_editor_stats()
            if cancelled:
                self.progress_label_var.set(self._bi("Insertion cancelled", "Einfügen abgebrochen"))
                self.status_var.set(self._bi("CANCELLED — insertion was stopped.", "ABGEBROCHEN — Einfügen wurde gestoppt."))
            else:
                self.progress_var.set(100)
                self.progress_label_var.set(f"{label} 100% — fertig")
                if on_complete:
                    on_complete()
            self._hide_progress_later()

        self.after(1, step)

    # ------------------------------------------------------------------
    # Import / editor
    # ------------------------------------------------------------------
    def paste_link(self) -> None:
        try:
            self.url_var.set(self.clipboard_get().strip())
            self.status_var.set(self._bi("CLIPBOARD — link pasted.", "ZWISCHENABLAGE — Link übernommen."))
            self._log("LINK_PASTED")
        except tk.TclError:
            messagebox.showwarning(self._t("Zwischenablage"), self._t("Die Zwischenablage enthält keinen Text."))

    def paste_text(self) -> None:
        try:
            text = self.clipboard_get()
        except tk.TclError:
            messagebox.showwarning(self._t("Zwischenablage"), self._t("Die Zwischenablage enthält keinen Text."))
            return
        if not text:
            return

        def done() -> None:
            self._analyze_manual_editor()

        self._start_chunked_insert(text, replace=False, label=self._bi("Pasting …", "Einfügen läuft …"), on_complete=done)

    def _analyze_manual_editor(self, *, source_text: str | None = None) -> None:
        raw = source_text if source_text is not None else self.editor.get("1.0", "end-1c")
        if not raw.strip():
            return
        backend = ChatBackend()
        chat = backend.analyze_manual_text(raw, title=self._title())
        self.current_source_mode = "manual-analyzed"
        self.current_source_url = ""
        self.current_chat = chat
        self.chat_image_selection.clear()
        self.chat_image_selection_initialized = False
        self.chat_image_preview_cache.clear()
        self.chat_image_preview_errors.clear()
        self._update_image_summary()
        self.mode_var.set(self._bi(
            f"Mode: manual analyzed · {len(chat.messages)} message(s)",
            f"Modus: manuell analysiert · {len(chat.messages)} Nachricht(en)",
        ))
        self.status_var.set(self._bi(
            f"ANALYZED — {len(chat.messages)} structured message(s) recovered.",
            f"ANALYSIERT — {len(chat.messages)} strukturierte Nachricht(en) erkannt.",
        ))
        self._log(f"MANUAL_ANALYSIS messages={len(chat.messages)} parser={chat.parser}")

    def open_private_manual_import(self) -> None:
        win = tk.Toplevel(self)
        win.title("666 ChatBackup — " + self._t("Privater / manueller Chat-Import"))
        win.configure(bg=BG)
        win.geometry("760x560")
        win.minsize(680, 500)
        panel = NeonPanel(win, accent=PURPLE, bg=PANEL)
        panel.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(panel, text=self._t("Privater / manueller Chat-Import"), bg=PANEL, fg=PINK, font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=18, pady=(18, 8))
        body_en = (
            "Private /c/ links cannot be downloaded without your authenticated ChatGPT session. "
            "Open the private chat in ChatGPT, copy the complete visible conversation text, then use the button below. "
            "ChatBackup will recover explicit User/ChatGPT role blocks when possible and preserve the complete text when a safe split is not possible."
        )
        body_de = (
            "Private /c/-Links können ohne deine angemeldete ChatGPT-Sitzung nicht direkt heruntergeladen werden. "
            "Öffne den privaten Chat in ChatGPT, kopiere den kompletten sichtbaren Gesprächsverlauf und nutze danach den Button unten. "
            "ChatBackup rekonstruiert sichere Benutzer-/ChatGPT-Blöcke und bewahrt den vollständigen Text, falls keine zuverlässige Trennung möglich ist."
        )
        tk.Label(panel, text=self._bi(body_en, body_de), bg=PANEL, fg=TEXT, justify="left", wraplength=690, font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 12))
        full_en = (
            "If ChatGPT says the chat is full, sharing may stop working. A temporary window can sometimes appear after sending one extra short prompt while ChatGPT starts thinking again. Copy the share link immediately if Share becomes available; this is not guaranteed. Otherwise use manual copy/import."
        )
        full_de = (
            "Wenn ChatGPT 'Chat voll' meldet, kann das Teilen ausfallen. Manchmal entsteht nach einer zusätzlichen kurzen Eingabe während des erneuten Denkens kurz ein Zeitfenster, in dem 'Teilen / Link kopieren' wieder funktioniert. Dann den Link sofort kopieren; garantiert ist das nicht. Andernfalls den manuellen Kopier-/Importweg verwenden."
        )
        tk.Label(panel, text=self._bi(full_en, full_de), bg=PANEL_ALT, fg=CYAN, justify="left", wraplength=680, padx=12, pady=12, font=("Segoe UI", 9, "bold")).pack(fill="x", padx=18, pady=8)
        btns = tk.Frame(panel, bg=PANEL)
        btns.pack(fill="x", padx=18, pady=14)
        NeonButton(btns, text=self._t("Chattext aus Zwischenablage analysieren"), command=lambda: (win.destroy(), self.paste_text()), accent=PINK).pack(fill="x", pady=5)
        private_url = self.url_var.get().strip()
        if re.search(r"https://(?:www\\.)?(?:chatgpt\\.com|chat\\.openai\\.com)/c/", private_url, re.IGNORECASE):
            NeonButton(btns, text=self._t("Privaten Chat im Browser öffnen"), command=lambda: webbrowser.open(private_url), accent=CYAN).pack(fill="x", pady=5)
        NeonButton(btns, text=self._t("❓  Hilfe"), command=self.show_help, accent=PURPLE).pack(fill="x", pady=5)
        NeonButton(btns, text=self._t("Schließen"), command=win.destroy, accent=CYAN, compact=True).pack(fill="x", pady=5)

    def clear_editor(self) -> None:
        if self.insert_in_progress:
            return
        if self.editor.get("1.0", "end-1c").strip() and not messagebox.askyesno(
            "Inhalt leeren", "Soll der komplette Textbereich wirklich geleert werden?"
        ):
            return
        self._set_editor_text("")
        self.current_source_mode = "manual"
        self.current_source_url = ""
        self.current_chat = None
        self.chat_image_selection.clear()
        self.chat_image_selection_initialized = False
        self.chat_image_preview_cache.clear()
        self.chat_image_preview_errors.clear()
        self._update_image_summary()
        self.mode_var.set(self._bi("Mode: manual", "Modus: manuell"))
        self.status_var.set(self._bi("READY — editor cleared.", "BEREIT — Textbereich geleert."))
        self._log("EDITOR_CLEARED")

    def select_all(self) -> str:
        self.editor.tag_add("sel", "1.0", "end-1c")
        self.editor.mark_set("insert", "1.0")
        self.editor.see("insert")
        return "break"

    def _on_editor_modified(self, _event: tk.Event) -> None:
        if self.editor.edit_modified():
            self.editor.edit_modified(False)
            self.after_idle(self._update_editor_stats)
            if not self.editor_programmatic_change:
                if not self.current_source_url:
                    self.current_source_mode = "manual-edited"
                    self.current_chat = None
                    self.mode_var.set(self._bi("Mode: manual / edited — analysis refreshes on export", "Modus: manuell / bearbeitet — Analyse wird beim Export erneuert"))
                else:
                    self.current_source_mode = "share-link-edited"
                    self.mode_var.set(self._bi("Mode: share link / edited", "Modus: Share-Link / nachbearbeitet"))

    def _update_editor_stats(self) -> None:
        if not hasattr(self, "editor"):
            return
        text = self.editor.get("1.0", "end-1c")
        lines = text.count("\n") + 1 if text else 1
        chars = len(text)
        self.editor_stats_var.set(f"Zeilen: {lines:,}  •  Zeichen: {chars:,}".replace(",", "."))

    def start_link_load(self) -> None:
        if self.insert_in_progress:
            return
        url = self.url_var.get().strip()
        if re.search(r"https://(?:www\.)?(?:chatgpt\.com|chat\.openai\.com)/c/", url, re.IGNORECASE):
            self.open_private_manual_import()
            return
        if not url:
            messagebox.showwarning(self._t("Link fehlt"), self._t("Bitte zuerst einen öffentlichen ChatGPT-Share-Link eingeben."))
            self.url_entry.focus_set()
            return
        self._set_busy(True)
        self._show_progress("Share-Link wird geladen …", indeterminate=True)
        self.status_var.set(self._bi("LOADING — validating and processing share link …", "LADEN — Share-Link wird geprüft und verarbeitet …"))
        self._log(f"LINK_LOAD_START {url}")
        worker = threading.Thread(target=self._load_worker, args=(url,), daemon=True)
        worker.start()

    def _load_worker(self, url: str) -> None:
        try:
            backend = ChatBackend(
                BackendConfig(
                    preserve_raw_source=bool(self.settings.get("preserve_raw_share_source", True)),
                    max_raw_html_chars=12_000_000,
                )
            )
            chat = backend.load(url)
            from chatbackup_core import build_markdown

            markdown = build_markdown(chat)
            self.result_queue.put(("success", (chat, markdown)))
        except Exception as exc:
            self.result_queue.put(("error", exc))

    def _poll_result_queue(self) -> None:
        try:
            while True:
                kind, payload = self.result_queue.get_nowait()
                self.progress.stop()
                self.progress.configure(mode="determinate")
                if kind == "success":
                    chat, markdown = payload  # type: ignore[misc]
                    self.current_source_url = chat.source_url
                    self.current_source_mode = "share-link"
                    self.current_chat = chat
                    self.current_title = chat.title
                    self.title_var.set(chat.title)
                    self.mode_var.set(f"Modus: Share-Link · Parser: {chat.parser}")
                    self._reset_chat_image_selection(select_all=True)

                    def done() -> None:
                        self.status_var.set(
                            f"VERIFIZIERT — {len(chat.messages)} Nachrichten geladen · Integrität {chat.stats.integrity_status}."
                        )
                        self._log(
                            f"LINK_LOAD_PASS messages={len(chat.messages)} parser={chat.parser} integrity={chat.stats.integrity_status}"
                        )
                        if bool(self.settings.get("autosave_after_link_load", False)):
                            self._autosave_loaded_chat()
                        if self._share_image_entries() and bool(self.settings.get("open_image_browser_after_load", False)):
                            self.after(120, self.open_chat_image_browser)

                    # large chats no longer block the GUI while the text widget is filled
                    self.insert_in_progress = False
                    self._set_busy(False)
                    self._start_chunked_insert(markdown, replace=True, label="Chat wird eingefügt …", on_complete=done)
                else:
                    self._set_busy(False)
                    self._hide_progress_later(100)
                    exc = payload
                    text = str(exc)
                    if isinstance(exc, ChatBackupError):
                        text = str(exc)
                    self.status_var.set(self._bi("ERROR — share link could not be processed.", "FEHLER — Share-Link konnte nicht verarbeitet werden."))
                    self._log(f"LINK_LOAD_FAIL {text}")
                    messagebox.showerror(self._t("Chat-Export fehlgeschlagen"), self._localize_runtime(text))
        except queue.Empty:
            pass
        self.after(150, self._poll_result_queue)

    def _set_editor_text(self, text: str) -> None:
        self.editor_programmatic_change = True
        try:
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", text)
            self.editor.edit_reset()
            self.editor.edit_modified(False)
            self._update_editor_stats()
        finally:
            self.editor_programmatic_change = False

    # ------------------------------------------------------------------
    # Image integration / chat image browser
    # ------------------------------------------------------------------
    def _share_image_entries(self) -> list[dict[str, object]]:
        entries: list[dict[str, object]] = []
        if self.current_chat is None:
            return entries
        for message_index, message in enumerate(self.current_chat.messages, start=1):
            for asset_index, asset in enumerate(message.assets, start=1):
                if asset.kind != "image":
                    continue
                entries.append(
                    {
                        "key": chat_asset_key(message_index, asset_index, asset),
                        "messageIndex": message_index,
                        "assetIndex": asset_index,
                        "role": message.role,
                        "author": message.author,
                        "asset": asset,
                    }
                )
        return entries

    def _share_image_assets(self) -> list[ChatAsset]:
        return [entry["asset"] for entry in self._share_image_entries()]  # type: ignore[list-item]

    def _reset_chat_image_selection(self, *, select_all: bool = True) -> None:
        entries = self._share_image_entries()
        self.chat_image_selection = {str(entry["key"]) for entry in entries} if select_all else set()
        self.chat_image_selection_initialized = bool(entries)
        self.chat_image_preview_cache.clear()
        self.chat_image_preview_errors.clear()
        self._update_image_summary()

    def _selected_chat_image_keys_for_export(self) -> set[str] | None:
        if self.current_chat is None:
            return None
        entries = self._share_image_entries()
        if not entries:
            return None
        if not self.chat_image_selection_initialized:
            return {str(entry["key"]) for entry in entries}
        return set(self.chat_image_selection)

    def _is_chat_image_selected(self, key: str) -> bool:
        if not self.chat_image_selection_initialized:
            return True
        return key in self.chat_image_selection

    def _update_image_summary(self) -> None:
        if not hasattr(self, "image_summary_var"):
            return
        entries = self._share_image_entries()
        selected = sum(1 for entry in entries if self._is_chat_image_selected(str(entry["key"])))
        direct = sum(
            1
            for entry in entries
            if isinstance(entry.get("asset"), ChatAsset)
            and str(entry["asset"].url).startswith(("http://", "https://"))  # type: ignore[union-attr]
        )
        local_suffix = f" · lokal: {len(self.manual_images)}" if self.manual_images else ""
        self.image_summary_var.set(
            f"Chat-Bilder: {len(entries)} · ausgewählt: {selected} · direkt erreichbar: {direct}{local_suffix}"
        )

    def add_images(self) -> None:
        selected = filedialog.askopenfilenames(
            title="Lokale Bilder zum ChatBackup hinzufügen",
            initialdir=self.last_directory,
            filetypes=[
                ("Bilddateien", "*.png *.jpg *.jpeg *.webp *.gif *.bmp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("WebP", "*.webp"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if not selected:
            return
        existing = {str(path.resolve()).lower() for path in self.manual_images if path.exists()}
        added = 0
        for item in selected:
            path = Path(item)
            key = str(path.resolve()).lower()
            if path.is_file() and key not in existing:
                self.manual_images.append(path)
                existing.add(key)
                added += 1
        self._update_image_summary()
        self.status_var.set(f"BILDER — {added} lokales Bild(er) hinzugefügt.")
        self._log(f"LOCAL_IMAGES_ADDED count={added}")

    def manage_images(self) -> None:
        """Legacy local-image manager retained as a secondary workflow."""
        win = tk.Toplevel(self)
        win.title("666 ChatBackup — " + self._t("Lokale Bilder verwalten"))
        win.configure(bg=BG)
        win.geometry("760x460")
        win.transient(self)
        win.grab_set()

        panel = NeonPanel(win, accent=PURPLE, bg=PANEL)
        panel.pack(fill="both", expand=True, padx=14, pady=14)
        tk.Label(panel, text=self._t("Lokale Zusatzbilder"), bg=PANEL, fg=PURPLE, font=("Segoe UI", 16, "bold")).pack(
            anchor="w", padx=14, pady=(12, 8)
        )
        tk.Label(
            panel,
            text=self._t("Diese Funktion ist nur für zusätzliche lokale Bilder. Chat-Bilder werden im Bildbrowser ausgewählt."),
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=14, pady=(0, 8))
        listbox = tk.Listbox(
            panel,
            bg="#050A12",
            fg=TEXT,
            selectbackground=PURPLE,
            selectforeground=WHITE,
            relief="flat",
            highlightthickness=1,
            highlightbackground=CYAN,
            font=("Consolas", 10),
        )
        listbox.pack(fill="both", expand=True, padx=14, pady=8)

        def refresh() -> None:
            listbox.delete(0, "end")
            for path in self.manual_images:
                listbox.insert("end", str(path))
            self._update_image_summary()

        def remove_selected() -> None:
            indexes = list(listbox.curselection())
            for index in reversed(indexes):
                if 0 <= index < len(self.manual_images):
                    self.manual_images.pop(index)
            refresh()

        buttons = tk.Frame(panel, bg=PANEL)
        buttons.pack(fill="x", padx=10, pady=(4, 12))
        NeonButton(buttons, text=self._t("Weitere hinzufügen"), command=self.add_images, accent=CYAN).pack(side="left", padx=4)
        NeonButton(buttons, text=self._t("Auswahl entfernen"), command=remove_selected, accent=RED).pack(side="left", padx=4)
        NeonButton(buttons, text=self._t("Alle entfernen"), command=lambda: (self.manual_images.clear(), refresh()), accent=PURPLE).pack(
            side="left", padx=4
        )
        NeonButton(buttons, text=self._t("Fertig"), command=win.destroy, accent=PINK, surface=PINK_SOFT).pack(side="right", padx=4)
        refresh()

    def _fetch_chat_image_bytes(self, entry: dict[str, object], *, max_bytes: int = 30 * 1024 * 1024) -> tuple[bytes, str]:
        key = str(entry["key"])
        cached = self.chat_image_preview_cache.get(key)
        if cached is not None:
            return cached
        asset = entry.get("asset")
        if not isinstance(asset, ChatAsset) or not asset.url.startswith(("http://", "https://")):
            raise ChatBackupError("Für dieses Chat-Bild ist keine direkt erreichbare Bild-URL vorhanden.")
        # All remote image requests must pass the pinned public-IP boundary.
        # Never forward private chat URLs as HTTP Referer.
        data, content_type = fetch_chat_image(asset.url, max_bytes=max_bytes)
        if len(data) > max_bytes:
            raise ChatBackupError("Das Bild ist für die Vorschau größer als 30 MB.")
        if not data:
            raise ChatBackupError("Der Bildserver hat keine Bilddaten geliefert.")
        self.chat_image_preview_cache[key] = (data, content_type)
        return data, content_type

    @staticmethod
    def _photo_from_image_bytes(data: bytes, max_size: tuple[int, int]) -> object | None:
        if not PIL_AVAILABLE or Image is None or ImageTk is None:
            return None
        with Image.open(io.BytesIO(data)) as source:
            source.seek(0)
            image = source.convert("RGBA")
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image.copy())

    def _chat_image_download_name(self, entry: dict[str, object], data: bytes, content_type: str) -> str:
        asset = entry.get("asset")
        if not isinstance(asset, ChatAsset):
            return "chat_image.img"
        parsed = urllib.parse.urlsplit(asset.url or "")
        suffix = Path(parsed.path).suffix.lower()
        if not suffix:
            mime = (asset.mime_type or content_type.split(";", 1)[0] or "").strip()
            suffix = mimetypes.guess_extension(mime) or ".img"
        fallback = f"chat_image_{entry.get('messageIndex', 0)}_{entry.get('assetIndex', 0)}{suffix}"
        filename = self._safe_asset_filename(asset.name, fallback)
        if not Path(filename).suffix:
            filename += suffix
        return filename

    def _download_chat_image_single(self, entry: dict[str, object], *, parent: tk.Misc | None = None) -> None:
        asset = entry.get("asset")
        if not isinstance(asset, ChatAsset) or not asset.url.startswith(("http://", "https://")):
            messagebox.showinfo(
                self._t("Bilder herunterladen"),
                self._t("Für die gewählte Auswahl sind keine direkt erreichbaren Bilddaten verfügbar."),
                parent=parent,
            )
            return
        try:
            data, content_type = self._fetch_chat_image_bytes(entry)
            suggested = self._chat_image_download_name(entry, data, content_type)
            target = filedialog.asksaveasfilename(
                parent=parent,
                title=self._t("Bilder herunterladen"),
                initialdir=self.last_directory,
                initialfile=suggested,
                defaultextension=Path(suggested).suffix or ".img",
                filetypes=[(self._bi("Image files", "Bilddateien"), "*.png *.jpg *.jpeg *.webp *.gif *.bmp *.avif *.img"), (self._bi("All files", "Alle Dateien"), "*.*")],
            )
            if not target:
                return
            path = self._write_binary_verified(target, data)
            self.last_directory = str(path.parent)
            self._remember_directory()
            self._log(f"CHAT_IMAGE_DOWNLOAD_SINGLE_PASS key={entry.get('key')} path={path}")
            messagebox.showinfo(self._t("Download abgeschlossen"), self._bi(f"Image saved:\n\n{path}", f"Bild gespeichert:\n\n{path}"), parent=parent)
        except Exception as exc:
            self._log(f"CHAT_IMAGE_DOWNLOAD_SINGLE_FAIL key={entry.get('key')} error={exc}")
            messagebox.showerror(self._t("Bilder herunterladen"), str(exc), parent=parent)

    def _download_chat_image_batch(self, entries: list[dict[str, object]], *, parent: tk.Misc | None = None, label: str = "selected") -> None:
        reachable = []
        for entry in entries:
            asset = entry.get("asset")
            if isinstance(asset, ChatAsset) and asset.url.startswith(("http://", "https://")):
                reachable.append(entry)
        if not reachable:
            messagebox.showinfo(
                self._t("Keine direkt erreichbaren Bilder"),
                self._t("Für die gewählte Auswahl sind keine direkt erreichbaren Bilddaten verfügbar."),
                parent=parent,
            )
            return
        folder = filedialog.askdirectory(parent=parent, title=self._t("Bilder herunterladen"), initialdir=self.last_directory)
        if not folder:
            return
        destination = Path(folder)
        ok = 0
        failed: list[str] = []
        for entry in reachable:
            try:
                data, content_type = self._fetch_chat_image_bytes(entry)
                filename = self._chat_image_download_name(entry, data, content_type)
                target = self._unique_asset_path(destination, filename)
                self._write_binary_verified(target, data)
                ok += 1
            except Exception as exc:
                failed.append(f"#{entry.get('messageIndex')}/{entry.get('assetIndex')}: {exc}")
        self.last_directory = str(destination)
        self._remember_directory()
        self._log(f"CHAT_IMAGE_DOWNLOAD_BATCH label={label} ok={ok} failed={len(failed)} dir={destination}")
        message = self._bi(
            f"Downloaded {ok} image(s) to:\n{destination}",
            f"{ok} Bild(er) heruntergeladen nach:\n{destination}",
        )
        if failed:
            message += self._bi("\n\nFailed: ", "\n\nFehlgeschlagen: ") + str(len(failed)) + "\n" + "\n".join(failed[:8])
        messagebox.showinfo(self._t("Download abgeschlossen"), message, parent=parent)

    def _open_chat_image_detail(self, entry: dict[str, object]) -> None:
        key = str(entry["key"])
        asset = entry.get("asset")
        if not isinstance(asset, ChatAsset):
            return
        cached = self.chat_image_preview_cache.get(key)
        if cached is None:
            messagebox.showinfo(
                "Bildvorschau",
                "Die große Vorschau ist noch nicht verfügbar. Bei direkt erreichbaren Bildern wird sie im Hintergrund geladen.",
            )
            return
        photo = self._photo_from_image_bytes(cached[0], (1050, 700))
        if photo is None:
            messagebox.showwarning(self._t("Bildvorschau"), self._t("Pillow ist nicht verfügbar; eine große Vorschau kann nicht erzeugt werden."))
            return
        win = tk.Toplevel(self)
        win.title(f"{self._bi('Chat Image', 'Chat-Bild')} — {asset.name}")
        win.configure(bg=BG)
        win.geometry("1120x820")
        win.minsize(720, 520)
        win.transient(self)
        panel = NeonPanel(win, accent=PINK, bg=PANEL)
        panel.pack(fill="both", expand=True, padx=12, pady=12)
        label = tk.Label(panel, image=photo, bg="#03070D", bd=0)
        label.image = photo  # type: ignore[attr-defined]
        label.pack(fill="both", expand=True, padx=10, pady=10)
        info = tk.Label(
            panel,
            text=f"Nachricht #{entry['messageIndex']} · {entry['role']} · {asset.name}",
            bg=PANEL,
            fg=CYAN,
            font=("Segoe UI", 10, "bold"),
        )
        info.pack(anchor="w", padx=10, pady=(0, 8))
        buttons = tk.Frame(panel, bg=PANEL)
        buttons.pack(fill="x", padx=8, pady=(0, 10))
        if asset.url.startswith(("http://", "https://")):
            NeonButton(buttons, text=self._t("Download"), command=lambda: self._download_chat_image_single(entry, parent=win), accent=GREEN).pack(
                side="left", padx=4
            )
            NeonButton(buttons, text=self._t("Original im Browser"), command=lambda: webbrowser.open(asset.url), accent=CYAN).pack(
                side="left", padx=4
            )
        NeonButton(buttons, text=self._t("Schließen"), command=win.destroy, accent=PINK, surface=PINK_SOFT).pack(side="right", padx=4)

    def open_structure_inspector(self) -> None:
        if self.current_chat is None and self._content().strip() and not self.current_source_url:
            self._ensure_manual_analysis_for_export()
        chat = self.current_chat
        if chat is None:
            messagebox.showinfo(
                self._t("Struktur-Inspector"),
                self._t("Bitte zuerst einen Chat laden oder manuellen Chattext einfügen. Der Inspector zeigt die analysierte Struktur."),
            )
            return

        win = tk.Toplevel(self)
        win.title(f"666 ChatBackup — {self._t('Struktur-Inspector')} v{APP_VERSION}")
        win.configure(bg=BG)
        win.geometry("1180x760")
        win.minsize(900, 620)
        try:
            if "icon" in self._photos:
                win.iconphoto(True, self._photos["icon"])
        except tk.TclError:
            pass

        panel = NeonPanel(win, accent=CYAN, bg=PANEL)
        panel.pack(fill="both", expand=True, padx=14, pady=14)
        panel.grid_columnconfigure(1, weight=1)
        panel.grid_rowconfigure(2, weight=1)

        profile = chat.integrity_profile()
        summary = self._bi(
            f"Parser: {chat.parser} · Messages: {len(chat.messages)} · "
            f"Copy Fields: {chat.stats.copy_fields_detected} detected / "
            f"{chat.stats.copy_fields_resolved} resolved / {chat.stats.copy_fields_unresolved} open · "
            f"Raw: {profile['rawPreservation']} · "
            f"Group: {'YES' if chat.is_group_chat else 'NO'} · Participants: {len(chat.participants)}",
            f"Parser: {chat.parser} · Nachrichten: {len(chat.messages)} · "
            f"Copy-Felder: {chat.stats.copy_fields_detected} erkannt / "
            f"{chat.stats.copy_fields_resolved} gelöst / {chat.stats.copy_fields_unresolved} offen · "
            f"Raw: {profile['rawPreservation']} · "
            f"Gruppe: {'JA' if chat.is_group_chat else 'NEIN'} · Teilnehmende: {len(chat.participants)}",
        )
        tk.Label(panel, text=self._bi("CHAT STRUCTURE / RAW SOURCE / COPY FIELDS", "CHAT-STRUKTUR / RAW SOURCE / COPY-FIELDS"), bg=PANEL, fg=PINK,
                 font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 4))
        tk.Label(panel, text=summary, bg=PANEL, fg=CYAN, font=("Segoe UI", 9, "bold"),
                 anchor="w").grid(row=1, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 10))

        left = tk.Frame(panel, bg=PANEL_ALT, highlightthickness=1, highlightbackground=BORDER)
        left.grid(row=2, column=0, sticky="nsw", padx=(14, 8), pady=(0, 12))
        right = tk.Frame(panel, bg=PANEL_ALT, highlightthickness=1, highlightbackground=PURPLE)
        right.grid(row=2, column=1, sticky="nsew", padx=(0, 14), pady=(0, 12))
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        listbox = tk.Listbox(left, width=36, bg="#07101E", fg=TEXT, selectbackground=PINK_SOFT,
                             selectforeground=WHITE, relief="flat", highlightthickness=0,
                             font=("Consolas", 9))
        listbox.pack(fill="both", expand=True, padx=8, pady=8)
        for index, message in enumerate(chat.messages, 1):
            copy_badge = f" C:{len(message.copy_fields)}" if message.copy_fields else ""
            asset_badge = f" A:{len(message.assets)}" if message.assets else ""
            participant_badge = (message.participant_display_name or message.author)[:18]
            label = f"{index:04d}  {message.role:<9} {participant_badge:<18}{copy_badge}{asset_badge}"
            listbox.insert("end", label)

        header_var = tk.StringVar(value="Nachricht auswählen")
        tk.Label(right, textvariable=header_var, bg=PANEL_ALT, fg=CYAN,
                 font=("Segoe UI", 11, "bold"), anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        detail = tk.Text(right, wrap="word", bg="#050A12", fg=TEXT, insertbackground=WHITE,
                         relief="flat", highlightthickness=0, font=("Consolas", 10))
        detail.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        scroll = tk.Scrollbar(right, command=detail.yview)
        scroll.grid(row=1, column=1, sticky="ns", pady=(0, 8))
        detail.configure(yscrollcommand=scroll.set)

        def show_message(_event: tk.Event | None = None) -> None:
            selection = listbox.curselection()
            if not selection:
                return
            index = int(selection[0])
            message = chat.messages[index]
            header_var.set(
                f"#{index + 1} · {message.author} · id={message.message_id or '—'} · content={message.content_type or '—'}"
            )
            payload = {
                "id": message.message_id or None,
                "role": message.role,
                "author": message.author,
                "participantId": message.participant_id or None,
                "participantDisplayName": message.participant_display_name or message.author,
                "participantKind": message.participant_kind or None,
                "participantUsername": message.participant_username or None,
                "participantResolution": message.participant_resolution,
                "recipient": message.recipient,
                "status": message.status or None,
                "contentType": message.content_type or None,
                "createdAtUnix": message.created_at,
                "copyFields": [
                    {
                        "identifier": f.identifier,
                        "label": f.label,
                        "resolved": f.resolved,
                        "text": f.text,
                        "utf16Length": f.utf16_length,
                    }
                    for f in message.copy_fields
                ],
                "warnings": message.warnings,
                "rawContent": message.raw_content,
                "rawMetadata": message.raw_metadata,
                "renderedText": message.text,
            }
            detail.configure(state="normal")
            detail.delete("1.0", "end")
            detail.insert("1.0", json.dumps(payload, ensure_ascii=False, indent=2))
            detail.configure(state="disabled")

        listbox.bind("<<ListboxSelect>>", show_message)
        if chat.messages:
            listbox.selection_set(0)
            show_message()

        footer = tk.Frame(panel, bg=PANEL)
        footer.grid(row=3, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 12))
        footer.grid_columnconfigure(0, weight=1)
        tk.Label(footer, text=(
            f"Quell-HTML: {chat.source_html_chars:,} Zeichen · SHA-256: "
            f"{chat.source_html_sha256[:16] + '…' if chat.source_html_sha256 else 'nicht vorhanden'} · "
            f"Visuelle Parität: NOT_CLAIMED"
        ).replace(",", "."), bg=PANEL, fg=MUTED, font=("Segoe UI", 9), anchor="w").grid(row=0, column=0, sticky="ew")

        def save_current_structure_json() -> None:
            selection = listbox.curselection()
            if not selection:
                messagebox.showinfo(self._t("Struktur-JSON"), self._t("Bitte zuerst eine Nachricht auswählen."), parent=win)
                return
            index = int(selection[0])
            full_payload = json.loads(build_structure_inspector_json(chat))
            payload = {
                "schema": "666.chatbackup.structure-inspector.message.v1",
                "schemaVersion": "1.0.0",
                "toolVersion": APP_VERSION,
                "title": chat.title,
                "sourceUrl": chat.source_url,
                "shareId": chat.share_id,
                "message": full_payload["messages"][index],
            }
            target = filedialog.asksaveasfilename(
                parent=win,
                title="Ausgewählte Inspector-Nachricht als JSON speichern",
                initialdir=self.last_directory,
                initialfile=f"{sanitize_file_name(self._title())}_MESSAGE_{index + 1:04d}_STRUCTURE.json",
                defaultextension=".json",
                filetypes=[("Struktur-JSON", "*.json"), ("Alle Dateien", "*.*")],
            )
            if not target:
                return
            path = self._write_export(target, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            self.last_directory = str(path.parent)
            self._remember_directory()
            self._log(f"STRUCTURE_MESSAGE_JSON_PASS {path}")
            messagebox.showinfo(self._t("Struktur-JSON gespeichert"), ((f"Message #{index + 1} was saved:\n\n{path}") if self._lang()=="en" else (f"Nachricht #{index + 1} wurde gespeichert:\n\n{path}")), parent=win)

        def save_full_structure_json() -> None:
            target = filedialog.asksaveasfilename(
                parent=win,
                title="Komplette Inspector-Struktur als JSON speichern",
                initialdir=self.last_directory,
                initialfile=f"{sanitize_file_name(self._title())}_STRUCTURE_INSPECTOR.json",
                defaultextension=".json",
                filetypes=[("Struktur-JSON", "*.json"), ("Alle Dateien", "*.*")],
            )
            if not target:
                return
            path = self._write_export(target, build_structure_inspector_json(chat))
            self.last_directory = str(path.parent)
            self._remember_directory()
            self._log(f"STRUCTURE_FULL_JSON_PASS {path}")
            messagebox.showinfo(self._t("Struktur-JSON gespeichert"), ((f"Complete inspector structure was saved:\n\n{path}") if self._lang()=="en" else (f"Komplette Inspector-Struktur wurde gespeichert:\n\n{path}")), parent=win)

        button_row = tk.Frame(footer, bg=PANEL)
        button_row.grid(row=0, column=1, sticky="e")
        NeonButton(button_row, text=self._t("Nachricht JSON"), command=save_current_structure_json, accent=CYAN, compact=True).pack(side="left", padx=(0, 6))
        NeonButton(button_row, text=self._t("Komplette Struktur JSON"), command=save_full_structure_json, accent=PURPLE, compact=True).pack(side="left", padx=(0, 6))
        NeonButton(button_row, text=self._t("Schließen"), command=win.destroy, accent=PINK, compact=True).pack(side="left")

    def open_chat_image_browser(self) -> None:
        entries = self._share_image_entries()
        if not entries:
            messagebox.showinfo(
                "Chat-Bildbrowser",
                "Im aktuell geladenen strukturierten Share-Chat wurden keine Bild-Assets gefunden.\n\n"
                "Hinweis: Nur Bilder, die im öffentlichen Share-Datensatz als Bild-Asset enthalten sind, können hier erscheinen.",
            )
            return
        if not self.chat_image_selection_initialized:
            self.chat_image_selection = {str(entry["key"]) for entry in entries}
            self.chat_image_selection_initialized = True

        win = tk.Toplevel(self)
        win.title("666 ChatBackup — " + self._bi("Chat Image Browser", "Chat-Bildbrowser"))
        win.configure(bg=BG)
        width = min(1280, max(980, self.winfo_width() - 120))
        height = min(840, max(650, self.winfo_height() - 100))
        win.geometry(f"{width}x{height}")
        win.minsize(900, 600)
        win.transient(self)

        outer = NeonPanel(win, accent=PINK, bg=PANEL)
        outer.pack(fill="both", expand=True, padx=12, pady=12)
        outer.grid_rowconfigure(2, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        title_row = tk.Frame(outer, bg=PANEL)
        title_row.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        title_row.grid_columnconfigure(0, weight=1)
        tk.Label(
            title_row,
            text="Chat-Bildbrowser",
            bg=PANEL,
            fg=PINK,
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w")
        count_var = tk.StringVar()
        tk.Label(title_row, textvariable=count_var, bg=PANEL, fg=CYAN, font=("Segoe UI", 10, "bold")).grid(
            row=0, column=1, sticky="e"
        )

        hint = (
            "Bilder aus dem geladenen Chat werden wie in einer Galerie angezeigt. Häkchen bestimmt, welche Bilder "
            "im Portable-ZIP gespeichert werden. Asset-Pointer ohne öffentliche URL bleiben im JSON erhalten."
        )
        tk.Label(outer, text=hint, bg=PANEL, fg=MUTED, font=("Segoe UI", 9), anchor="w", justify="left", wraplength=1120).grid(
            row=1, column=0, sticky="ew", padx=14, pady=(0, 8)
        )

        browser_shell = tk.Frame(outer, bg="#050A12", highlightthickness=1, highlightbackground=CYAN)
        browser_shell.grid(row=2, column=0, sticky="nsew", padx=14, pady=6)
        browser_shell.grid_rowconfigure(0, weight=1)
        browser_shell.grid_columnconfigure(0, weight=1)
        canvas = tk.Canvas(browser_shell, bg="#050A12", highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(browser_shell, orient="vertical", command=canvas.yview, style="Neon.Vertical.TScrollbar")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        grid = tk.Frame(canvas, bg="#050A12")
        window_id = canvas.create_window((0, 0), window=grid, anchor="nw")

        def on_grid_configure(_event: tk.Event | None = None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event: tk.Event) -> None:
            canvas.itemconfigure(window_id, width=event.width)

        grid.bind("<Configure>", on_grid_configure, add="+")
        canvas.bind("<Configure>", on_canvas_configure, add="+")

        def wheel(event: tk.Event) -> str:
            delta = -1 if getattr(event, "delta", 0) > 0 else 1
            canvas.yview_scroll(delta * 3, "units")
            return "break"

        canvas.bind("<MouseWheel>", wheel, add="+")
        grid.bind("<MouseWheel>", wheel, add="+")

        select_vars: dict[str, tk.BooleanVar] = {}
        preview_labels: dict[str, tk.Label] = {}
        preview_queue: queue.Queue[tuple[str, str, object]] = queue.Queue()

        def refresh_count() -> None:
            selected_count = sum(1 for entry in entries if self._is_chat_image_selected(str(entry["key"])))
            direct_count = sum(
                1
                for entry in entries
                if isinstance(entry.get("asset"), ChatAsset)
                and entry["asset"].url.startswith(("http://", "https://"))  # type: ignore[union-attr]
            )
            count_var.set(f"{selected_count}/{len(entries)} ausgewählt · {direct_count} " + self._bi("directly reachable", "direkt erreichbar"))
            self._update_image_summary()

        def toggle(key: str, var: tk.BooleanVar) -> None:
            if var.get():
                self.chat_image_selection.add(key)
            else:
                self.chat_image_selection.discard(key)
            self.chat_image_selection_initialized = True
            refresh_count()

        columns = 3
        for col in range(columns):
            grid.grid_columnconfigure(col, weight=1, uniform="gallery")

        for position, entry in enumerate(entries):
            key = str(entry["key"])
            asset = entry.get("asset")
            if not isinstance(asset, ChatAsset):
                continue
            row, col = divmod(position, columns)
            card = NeonPanel(grid, accent=PURPLE if col % 2 else CYAN, bg=PANEL_ALT)
            card.grid(row=row, column=col, sticky="nsew", padx=7, pady=7)
            card.grid_columnconfigure(0, weight=1)

            preview = tk.Label(
                card,
                text="Vorschau wird geladen …" if asset.url.startswith(("http://", "https://")) else "CHATGPT ASSET-POINTER\nKeine direkte Vorschau-URL",
                bg="#03070D",
                fg=CYAN if asset.url.startswith(("http://", "https://")) else MUTED,
                font=("Segoe UI", 10, "bold"),
                height=9,
                anchor="center",
                justify="center",
                cursor="hand2" if asset.url.startswith(("http://", "https://")) else "arrow",
            )
            preview.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 6))
            preview_labels[key] = preview
            preview.bind("<Double-Button-1>", lambda _e, item=entry: self._open_chat_image_detail(item), add="+")

            name = asset.name or f"Chat-Bild {position + 1}"
            tk.Label(
                card,
                text=name,
                bg=PANEL_ALT,
                fg=TEXT,
                font=("Segoe UI", 10, "bold"),
                anchor="w",
                justify="left",
                wraplength=300,
            ).grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 2))
            role = str(entry.get("role") or "unbekannt")
            author = str(entry.get("author") or role)
            status_text = "Direkt erreichbar" if asset.url.startswith(("http://", "https://")) else "Asset-Pointer / nur Metadaten"
            tk.Label(
                card,
                text=f"Nachricht #{entry['messageIndex']} · {author}\n{status_text}",
                bg=PANEL_ALT,
                fg=GREEN if asset.url.startswith(("http://", "https://")) else "#F5C451",
                font=("Segoe UI", 8),
                anchor="w",
                justify="left",
            ).grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 4))

            var = tk.BooleanVar(value=self._is_chat_image_selected(key))
            select_vars[key] = var
            check = tk.Checkbutton(
                card,
                text=self._t("Mit Backup speichern"),
                variable=var,
                command=lambda k=key, v=var: toggle(k, v),
                bg=PANEL_ALT,
                fg=PINK,
                activebackground=PANEL_ALT,
                activeforeground=WHITE,
                selectcolor="#07101E",
                font=("Segoe UI", 9, "bold"),
            )
            check.grid(row=3, column=0, sticky="w", padx=8, pady=(0, 4))
            actions = tk.Frame(card, bg=PANEL_ALT)
            actions.grid(row=4, column=0, sticky="ew", padx=6, pady=(0, 8))
            NeonButton(actions, text=self._t("Großansicht"), command=lambda item=entry: self._open_chat_image_detail(item), accent=PINK, compact=True).pack(
                side="left", padx=3
            )
            if asset.url.startswith(("http://", "https://")):
                NeonButton(actions, text=self._t("Download"), command=lambda item=entry: self._download_chat_image_single(item, parent=win), accent=GREEN, compact=True).pack(
                    side="left", padx=3
                )
                NeonButton(actions, text=self._t("Browser"), command=lambda url=asset.url: webbrowser.open(url), accent=CYAN, compact=True).pack(
                    side="left", padx=3
                )

        controls = tk.Frame(outer, bg=PANEL)
        controls.grid(row=3, column=0, sticky="ew", padx=10, pady=(6, 12))

        def apply_selection(mode: str) -> None:
            for entry in entries:
                key = str(entry["key"])
                asset = entry.get("asset")
                wanted = mode == "all"
                if mode == "none":
                    wanted = False
                elif mode == "direct":
                    wanted = isinstance(asset, ChatAsset) and asset.url.startswith(("http://", "https://"))
                var = select_vars[key]
                var.set(bool(wanted))
                if wanted:
                    self.chat_image_selection.add(key)
                else:
                    self.chat_image_selection.discard(key)
            self.chat_image_selection_initialized = True
            refresh_count()

        NeonButton(controls, text=self._t("Alle auswählen"), command=lambda: apply_selection("all"), accent=CYAN, compact=True).pack(side="left", padx=4)
        NeonButton(controls, text=self._t("Keine"), command=lambda: apply_selection("none"), accent=PURPLE, compact=True).pack(side="left", padx=4)
        NeonButton(controls, text=self._t("Nur direkt erreichbare"), command=lambda: apply_selection("direct"), accent=GREEN, compact=True).pack(side="left", padx=4)
        NeonButton(controls, text=self._t("Ausgewählte herunterladen"), command=lambda: self._download_chat_image_batch(
            [entry for entry in entries if self._is_chat_image_selected(str(entry["key"]))], parent=win, label="selected"
        ), accent=CYAN, compact=True).pack(side="left", padx=4)
        NeonButton(controls, text=self._t("Alle erreichbaren herunterladen"), command=lambda: self._download_chat_image_batch(
            list(entries), parent=win, label="all-reachable"
        ), accent=GREEN, compact=True).pack(side="left", padx=4)
        NeonButton(controls, text=self._t("Lokale Zusatzbilder"), command=self.manage_images, accent=PURPLE, compact=True).pack(side="left", padx=4)
        NeonButton(controls, text=self._t("Auswahl übernehmen"), command=win.destroy, accent=PINK, surface=PINK_SOFT).pack(side="right", padx=4)
        refresh_count()

        jobs: queue.Queue[dict[str, object]] = queue.Queue()
        for entry in entries:
            asset = entry.get("asset")
            if isinstance(asset, ChatAsset) and asset.url.startswith(("http://", "https://")):
                jobs.put(entry)

        def worker() -> None:
            while True:
                try:
                    entry = jobs.get_nowait()
                except queue.Empty:
                    return
                key = str(entry["key"])
                try:
                    data, content_type = self._fetch_chat_image_bytes(entry)
                    preview_queue.put((key, "ok", (data, content_type)))
                except Exception as exc:
                    self.chat_image_preview_errors[key] = str(exc)
                    preview_queue.put((key, "error", str(exc)))
                finally:
                    jobs.task_done()

        for _ in range(min(4, jobs.qsize())):
            threading.Thread(target=worker, daemon=True).start()

        def poll_previews() -> None:
            if not win.winfo_exists():
                return
            try:
                while True:
                    key, status, payload = preview_queue.get_nowait()
                    label = preview_labels.get(key)
                    if label is None or not label.winfo_exists():
                        continue
                    if status == "ok":
                        data, _content_type = payload  # type: ignore[misc]
                        photo = self._photo_from_image_bytes(data, (310, 175))
                        if photo is not None:
                            label.configure(image=photo, text="", height=0)
                            label.image = photo  # type: ignore[attr-defined]
                        else:
                            label.configure(text="Bild geladen\nPillow-Vorschau nicht verfügbar", fg=GREEN)
                    else:
                        label.configure(text="Vorschau nicht ladbar\nDoppelklick für Details", fg=RED)
            except queue.Empty:
                pass
            win.after(120, poll_previews)

        win.after(80, poll_previews)

    def _local_asset_metadata(self) -> list[dict[str, object]]:
        result: list[dict[str, object]] = []
        for path in self.manual_images:
            if not path.is_file():
                continue
            data = path.read_bytes()
            result.append(
                {
                    "kind": "image",
                    "name": path.name,
                    "mimeType": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                    "size": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "source": "local-user-selected",
                }
            )
        return result

    @staticmethod
    def _safe_asset_filename(name: str, fallback: str) -> str:
        source = Path(name or fallback)
        stem = sanitize_file_name(source.stem or Path(fallback).stem)
        suffix = source.suffix.lower()
        if not suffix:
            suffix = Path(fallback).suffix.lower()
        return f"{stem}{suffix}" if suffix else stem

    @staticmethod
    def _unique_asset_path(directory: Path, name: str) -> Path:
        candidate = directory / name
        if not candidate.exists():
            return candidate
        stem = candidate.stem
        suffix = candidate.suffix
        index = 2
        while True:
            alternative = directory / f"{stem}_{index}{suffix}"
            if not alternative.exists():
                return alternative
            index += 1

    def _download_share_images(self, assets_dir: Path) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []
        entries = self._share_image_entries()
        for index, entry in enumerate(entries, start=1):
            key = str(entry["key"])
            asset = entry.get("asset")
            if not isinstance(asset, ChatAsset):
                continue
            selected = self._is_chat_image_selected(key)
            record: dict[str, object] = {
                "assetKey": key,
                "messageIndex": entry.get("messageIndex"),
                "assetIndex": entry.get("assetIndex"),
                "selected": selected,
                "name": asset.name,
                "mimeType": asset.mime_type,
                "url": asset.url,
                "assetPointer": asset.asset_pointer,
                "source": asset.source,
            }
            if not selected:
                record["status"] = "SKIPPED_BY_USER"
                records.append(record)
                continue
            if not bool(self.settings.get("download_share_images", True)):
                record["status"] = "SKIPPED_BY_SETTING"
                records.append(record)
                continue
            if not asset.url.startswith(("http://", "https://")):
                record["status"] = "UNRESOLVED_ASSET_POINTER"
                records.append(record)
                continue
            try:
                data, content_type = self._fetch_chat_image_bytes(entry)
                parsed = urllib.parse.urlsplit(asset.url)
                suffix = Path(parsed.path).suffix.lower()
                if not suffix:
                    suffix = mimetypes.guess_extension(asset.mime_type or content_type.split(";", 1)[0]) or ".img"
                filename = self._safe_asset_filename(asset.name, f"share_image_{index}{suffix}")
                if not Path(filename).suffix:
                    filename += suffix
                target = self._unique_asset_path(assets_dir, filename)
                target.write_bytes(data)
                record.update(
                    {
                        "status": "DOWNLOADED",
                        "packagePath": f"assets/{target.name}",
                        "size": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(),
                    }
                )
            except Exception as exc:
                record["status"] = "DOWNLOAD_FAILED"
                record["error"] = str(exc)[:300]
            records.append(record)
        return records

    def _write_binary_verified(self, target: str | Path, data: bytes) -> Path:
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        if bool(self.settings.get("verify_exports", True)):
            readback = path.read_bytes()
            if len(readback) != len(data) or hashlib.sha256(readback).digest() != hashlib.sha256(data).digest():
                raise ChatBackupError("Das gespeicherte Binärpaket stimmt nach dem Rücklesen nicht mit dem Export überein.")
        return path

    def save_portable_zip(self) -> None:
        if not self._content().strip():
            messagebox.showwarning(self._t("Kein Inhalt"), self._t("Bitte zuerst einen Link laden oder Chattext einfügen."))
            return
        target = filedialog.asksaveasfilename(
            title="Portables ChatBackup-Paket speichern",
            initialdir=self.last_directory,
            initialfile=self._default_name("zip").replace(".zip", "_PORTABLE.zip"),
            defaultextension=".zip",
            filetypes=[("ZIP-Backup", "*.zip"), ("Alle Dateien", "*.*")],
        )
        if not target:
            return

        try:
            self._show_progress("Portable Backup 0%")
            self.update_idletasks()
            with tempfile.TemporaryDirectory(prefix="666chatbackup_") as temp_dir:
                root = Path(temp_dir) / "666_CHATBACKUP_PORTABLE"
                assets_dir = root / "assets"
                source_dir = root / "source"
                root.mkdir(parents=True, exist_ok=True)
                assets_dir.mkdir(parents=True, exist_ok=True)
                source_dir.mkdir(parents=True, exist_ok=True)

                local_records: list[dict[str, object]] = []
                share_records: list[dict[str, object]] = []
                if bool(self.settings.get("integrate_images", True)):
                    for path in self.manual_images:
                        if not path.is_file():
                            continue
                        target_image = self._unique_asset_path(assets_dir, self._safe_asset_filename(path.name, "image"))
                        shutil.copy2(path, target_image)
                        data = target_image.read_bytes()
                        local_records.append(
                            {
                                "kind": "image",
                                "name": path.name,
                                "status": "COPIED",
                                "packagePath": f"assets/{target_image.name}",
                                "mimeType": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                                "size": len(data),
                                "sha256": hashlib.sha256(data).hexdigest(),
                                "source": "local-user-selected",
                            }
                        )
                    share_records = self._download_share_images(assets_dir)

                self.progress_var.set(24)
                self.progress_label_var.set("Portable Backup 24% — Bilder / Assets")
                self.update_idletasks()

                base = sanitize_file_name(self._title())
                markdown = self._content_for_extension("md")
                integrated_lines: list[str] = []
                for record in local_records:
                    if record.get("status") == "COPIED" and record.get("packagePath"):
                        integrated_lines.append(f"![{record.get('name', 'Bild')}]({record['packagePath']})")
                for record in share_records:
                    if record.get("status") == "DOWNLOADED" and record.get("packagePath"):
                        integrated_lines.append(f"![{record.get('name', 'Chat-Bild')}]({record['packagePath']})")
                if integrated_lines:
                    markdown = markdown.rstrip() + "\n\n---\n\n## Integrierte Bilder\n\n" + "\n\n".join(integrated_lines) + "\n"

                machine_kwargs = {
                    "content": self._content(),
                    "title": self._title(),
                    "source_url": self.current_source_url,
                    "source_mode": self.current_source_mode,
                    "chat": self.current_chat,
                    "local_assets": local_records,
                    "selected_asset_keys": self._selected_chat_image_keys_for_export(),
                }
                exports = {
                    f"{base}.txt": self._content_for_extension("txt"),
                    f"{base}.md": self._apply_line_endings(markdown),
                    f"{base}.js": self._content_for_extension("js"),
                    f"{base}.json": self._apply_line_endings(build_json_export(**machine_kwargs)),
                    f"{base}.jsonl": self._apply_line_endings(build_jsonl_export(**machine_kwargs)),
                }

                export_manifest: list[dict[str, object]] = []
                for idx, (name, text) in enumerate(exports.items(), start=1):
                    data = text.encode("utf-8")
                    (root / name).write_bytes(data)
                    export_manifest.append(
                        {
                            "path": name,
                            "size": len(data),
                            "sha256": hashlib.sha256(data).hexdigest(),
                        }
                    )
                    pct = 24 + int((idx / len(exports)) * 40)
                    self.progress_var.set(pct)
                    self.progress_label_var.set(f"Portable Backup {pct}% — {Path(name).suffix[1:].upper()}")
                    self.update_idletasks()

                source_records: list[dict[str, object]] = []
                if self.current_chat is not None:
                    raw_bundle_text = json.dumps(
                        build_raw_source_bundle(self.current_chat),
                        ensure_ascii=False,
                        indent=2,
                    ) + "\n"
                    raw_path = source_dir / "conversation.raw.json"
                    raw_bytes = raw_bundle_text.encode("utf-8")
                    raw_path.write_bytes(raw_bytes)
                    source_records.append({
                        "path": "source/conversation.raw.json",
                        "size": len(raw_bytes),
                        "sha256": hashlib.sha256(raw_bytes).hexdigest(),
                        "kind": "RAW_MESSAGE_BUNDLE",
                    })

                    receipt_text = json.dumps(
                        build_parser_receipt(self.current_chat),
                        ensure_ascii=False,
                        indent=2,
                    ) + "\n"
                    receipt_path = source_dir / "parser_receipt.json"
                    receipt_bytes = receipt_text.encode("utf-8")
                    receipt_path.write_bytes(receipt_bytes)
                    source_records.append({
                        "path": "source/parser_receipt.json",
                        "size": len(receipt_bytes),
                        "sha256": hashlib.sha256(receipt_bytes).hexdigest(),
                        "kind": "PARSER_RECEIPT",
                    })

                    inspector_text = build_structure_inspector_json(self.current_chat)
                    inspector_path = source_dir / "structure_inspector.json"
                    inspector_bytes = inspector_text.encode("utf-8")
                    inspector_path.write_bytes(inspector_bytes)
                    source_records.append({
                        "path": "source/structure_inspector.json",
                        "size": len(inspector_bytes),
                        "sha256": hashlib.sha256(inspector_bytes).hexdigest(),
                        "kind": "STRUCTURE_INSPECTOR_SNAPSHOT",
                    })

                    if bool(self.settings.get("preserve_raw_share_source", True)) and self.current_chat.source_html:
                        source_html_bytes = self.current_chat.source_html.encode("utf-8", errors="replace")
                        compressed = gzip.compress(source_html_bytes, compresslevel=9)
                        html_path = source_dir / "share-source.html.gz"
                        html_path.write_bytes(compressed)
                        source_records.append({
                            "path": "source/share-source.html.gz",
                            "size": len(compressed),
                            "sha256": hashlib.sha256(compressed).hexdigest(),
                            "uncompressedSize": len(source_html_bytes),
                            "uncompressedSha256": hashlib.sha256(source_html_bytes).hexdigest(),
                            "kind": "REPARSE_SOURCE_HTML_GZIP",
                        })

                manifest = {
                    "schema": "666.chatbackup.portable-package.v1",
                    "toolVersion": APP_VERSION,
                    "createdAt": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "title": self._title(),
                    "sourceMode": self.current_source_mode,
                    "sourceUrl": self.current_source_url,
                    "files": export_manifest,
                    "sourceArtifacts": source_records,
                    "backend": {
                        "machineSchemaVersion": "1.2.0",
                        "rawSourcePreservation": bool(self.current_chat and self.current_chat.source_html),
                        "reparseReady": bool(self.current_chat and self.current_chat.source_html),
                        "copyFieldsDetected": int(self.current_chat.stats.copy_fields_detected) if self.current_chat else 0,
                        "copyFieldsResolved": int(self.current_chat.stats.copy_fields_resolved) if self.current_chat else 0,
                        "copyFieldsUnresolved": int(self.current_chat.stats.copy_fields_unresolved) if self.current_chat else 0,
                    },
                    "images": {
                        "integrationEnabled": bool(self.settings.get("integrate_images", True)),
                        "local": local_records,
                        "share": share_records,
                        "selectedChatImageCount": sum(1 for row in share_records if row.get("selected") is True),
                        "skippedByUserCount": sum(1 for row in share_records if row.get("status") == "SKIPPED_BY_USER"),
                        "downloadedCount": sum(1 for row in share_records if row.get("status") == "DOWNLOADED")
                        + len(local_records),
                        "unresolvedCount": sum(
                            1
                            for row in share_records
                            if row.get("status") in {"UNRESOLVED_ASSET_POINTER", "DOWNLOAD_FAILED"}
                        ),
                    },
                }
                manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
                (root / "package_manifest.json").write_text(manifest_text, encoding="utf-8")
                (root / "README_PACKAGE.txt").write_text(
                    "666 ChatBackup Portable Package\n\n"
                    "Enthalten: TXT, Markdown, JavaScript, strukturiertes JSON, JSONL und - soweit erreichbar - Bilder im assets-Ordner.\n"
                    "Das Markdown enthält nur für ausgewählte und erfolgreich integrierte Bilder relative assets/-Verweise.\n"
                    "Die Auswahl aus dem Chat-Bildbrowser wird in JSON und package_manifest.json maschinenlesbar protokolliert.\n"
                    "ChatGPT-interne Asset-Pointer ohne direkt erreichbare URL bleiben im maschinenlesbaren JSON erhalten und werden im Manifest als UNRESOLVED_ASSET_POINTER markiert.\n"
                    "Der source/-Ordner enthält bei Share-Chats Raw-Message-Bundle, Parser-Receipt, structure_inspector.json und - sofern aktiviert/verfügbar - komprimiertes Original-Share-HTML für spätere Reparse-Läufe.\n",
                    encoding="utf-8",
                )

                self.progress_var.set(74)
                self.progress_label_var.set("Portable Backup 74% — Manifest")
                self.update_idletasks()

                archive_path = Path(temp_dir) / "package.zip"
                with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                    for file_path in sorted(root.rglob("*")):
                        if file_path.is_file():
                            archive.write(file_path, file_path.relative_to(root))
                with zipfile.ZipFile(archive_path, "r") as archive:
                    bad = archive.testzip()
                    if bad:
                        raise ChatBackupError(f"ZIP-CRC-Prüfung fehlgeschlagen bei: {bad}")
                data = archive_path.read_bytes()
                self.progress_var.set(90)
                self.progress_label_var.set("Portable Backup 90% — Byte-Readback")
                self.update_idletasks()
                path = self._write_binary_verified(target, data)

            self.last_directory = str(path.parent)
            self._remember_directory()
            self.progress_var.set(100)
            self.progress_label_var.set("Portable Backup 100% — verifiziert")
            self.status_var.set(f"PORTABLE BACKUP PASS — {path}")
            self._log(f"PORTABLE_ZIP_PASS {path}")
            self._hide_progress_later()
            messagebox.showinfo(
                "Portable Backup gespeichert",
                f"ZIP inklusive Maschinenformaten und Bildintegration gespeichert:\n\n{path}",
            )
        except Exception as exc:
            self._hide_progress_later(100)
            self.status_var.set("FEHLER — Portable Backup konnte nicht gespeichert werden.")
            self._log(f"PORTABLE_ZIP_FAIL {exc}")
            messagebox.showerror(self._t("Portable Backup fehlgeschlagen"), self._localize_runtime(exc))

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def _content(self) -> str:
        return self.editor.get("1.0", "end-1c")

    def _title(self) -> str:
        title = self.title_var.get().strip()
        return title or "ChatGPT Backup"

    def _default_name(self, extension: str) -> str:
        return f"{sanitize_file_name(self._title())}_{file_date_stamp()}.{extension}"

    def _apply_line_endings(self, content: str) -> str:
        mode = str(self.settings.get("line_endings", "Original"))
        if mode == "Windows (CRLF)":
            return content.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
        if mode == "Unix (LF)":
            return content.replace("\r\n", "\n").replace("\r", "\n")
        return content

    def _ensure_manual_analysis_for_export(self) -> None:
        if self.current_source_url:
            return
        content = self._content()
        if not content.strip():
            return
        if self.current_chat is None or not self.current_source_mode.startswith("manual-analyzed"):
            backend = ChatBackend()
            self.current_chat = backend.analyze_manual_text(content, title=self._title())
            self.current_source_mode = "manual-analyzed"
            self._log(f"MANUAL_EXPORT_ANALYSIS messages={len(self.current_chat.messages)}")

    def _manual_plaintext(self) -> str:
        if self.current_chat is None:
            return self._content()
        parts: list[str] = []
        for message in self.current_chat.messages:
            parts.extend([message.author, message.text.strip(), ""])
        return "\n".join(parts).rstrip() + "\n" if parts else self._content()

    def _machine_export_kwargs(self) -> dict[str, object]:
        self._ensure_manual_analysis_for_export()
        return {
            "content": self._content(),
            "title": self._title(),
            "source_url": self.current_source_url,
            "source_mode": self.current_source_mode,
            "chat": self.current_chat,
            "local_assets": self._local_asset_metadata(),
            "selected_asset_keys": self._selected_chat_image_keys_for_export(),
        }

    def _content_for_extension(self, extension: str) -> str:
        self._ensure_manual_analysis_for_export()
        content = self._content()
        if self.current_chat is not None and not self.current_source_url and self.current_source_mode.startswith("manual-analyzed"):
            if extension == "md":
                return self._apply_line_endings(build_markdown(self.current_chat))
            if extension == "txt":
                return self._apply_line_endings(self._manual_plaintext())
            if extension == "js":
                content = self._manual_plaintext()
        if extension == "js":
            content = build_javascript_export(
                content=content,
                title=self._title(),
                source_url=self.current_source_url,
                source_mode=self.current_source_mode,
            )
            return self._apply_line_endings(content)
        if extension == "json":
            return self._apply_line_endings(build_json_export(**self._machine_export_kwargs()))
        if extension == "jsonl":
            return self._apply_line_endings(build_jsonl_export(**self._machine_export_kwargs()))
        if content and not content.endswith(("\n", "\r")):
            content += "\n"
        return self._apply_line_endings(content)

    def _write_export(self, target: str | Path, content: str) -> Path:
        if bool(self.settings.get("verify_exports", True)):
            return write_verified(target, content)
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content.encode("utf-8"))
        return path

    def save_single(self, extension: str) -> None:
        if not self._content().strip():
            messagebox.showwarning(self._t("Kein Inhalt"), self._t("Bitte zuerst einen Link laden oder Chattext einfügen."))
            return
        file_types = {
            "txt": [("Textdatei", "*.txt"), ("Alle Dateien", "*.*")],
            "md": [("Markdown-Datei", "*.md"), ("Alle Dateien", "*.*")],
            "js": [("JavaScript-Datei", "*.js"), ("Alle Dateien", "*.*")],
            "json": [("Maschinenlesbares JSON", "*.json"), ("Alle Dateien", "*.*")],
            "jsonl": [("JSON Lines", "*.jsonl"), ("Alle Dateien", "*.*")],
        }
        target = filedialog.asksaveasfilename(
            title=f"Chatbackup als {extension.upper()} speichern",
            initialdir=self.last_directory,
            initialfile=self._default_name(extension),
            defaultextension=f".{extension}",
            filetypes=file_types[extension],
        )
        if not target:
            self.status_var.set("ABGEBROCHEN — Es wurde keine Datei gespeichert.")
            return
        try:
            self._show_progress(f"{extension.upper()} wird gespeichert …", indeterminate=True)
            self.update_idletasks()
            path = self._write_export(target, self._content_for_extension(extension))
            self.last_directory = str(path.parent)
            self._remember_directory()
            self.progress.stop()
            self.progress.configure(mode="determinate")
            self.progress_var.set(100)
            self.progress_label_var.set("Speichern 100% — verifiziert")
            self.status_var.set(f"VERIFIZIERT GESPEICHERT — {path}")
            self._log(f"SAVE_{extension.upper()}_PASS {path}")
            self._hide_progress_later()
            messagebox.showinfo(self._t("Gespeichert"), self._t("Datei erfolgreich gespeichert:\n\n") + str(path))
        except Exception as exc:
            self.progress.stop()
            self._hide_progress_later(100)
            self.status_var.set("FEHLER — Datei konnte nicht gespeichert werden.")
            self._log(f"SAVE_{extension.upper()}_FAIL {exc}")
            messagebox.showerror(self._t("Speichern fehlgeschlagen"), self._localize_runtime(exc))

    def save_all(self) -> None:
        if not self._content().strip():
            messagebox.showwarning(self._t("Kein Inhalt"), self._t("Bitte zuerst einen Link laden oder Chattext einfügen."))
            return
        directory = filedialog.askdirectory(
            title="Zielordner für TXT, MD, JavaScript, JSON und JSONL auswählen",
            initialdir=self.last_directory,
            mustexist=True,
        )
        if not directory:
            self.status_var.set("ABGEBROCHEN — Es wurde kein Zielordner ausgewählt.")
            return
        self._save_all_to_directory(directory, interactive=True)

    def _save_all_to_directory(self, directory: str, *, interactive: bool) -> list[Path]:
        base_name = f"{sanitize_file_name(self._title())}_{file_date_stamp()}"
        saved: list[Path] = []
        try:
            self._show_progress("Export 0%")
            extensions = ("txt", "md", "js", "json", "jsonl")
            for idx, extension in enumerate(extensions, start=1):
                path = unique_path(directory, base_name, extension)
                saved.append(self._write_export(path, self._content_for_extension(extension)))
                pct = int((idx / len(extensions)) * 100)
                self.progress_var.set(pct)
                self.progress_label_var.set(f"Export {pct}% — {extension.upper()}")
                self.update_idletasks()
            self.last_directory = directory
            self._remember_directory()
            self.status_var.set(f"VERIFIZIERT GESPEICHERT — 5 Dateien in {directory}")
            self._log(f"SAVE_ALL_PASS {directory}")
            self._hide_progress_later()
            if interactive:
                messagebox.showinfo(
                    "Alle Formate gespeichert",
                    "TXT, MD, JavaScript, JSON und JSONL wurden gespeichert"
                    + (" und zurückgelesen" if bool(self.settings.get("verify_exports", True)) else "")
                    + ":\n\n"
                    + "\n".join(str(path) for path in saved),
                )
            return saved
        except Exception as exc:
            self._hide_progress_later(100)
            self.status_var.set("FEHLER — Nicht alle Dateien konnten gespeichert werden.")
            self._log(f"SAVE_ALL_FAIL {exc}")
            if interactive:
                messagebox.showerror(self._t("Speichern fehlgeschlagen"), self._localize_runtime(exc))
            return saved

    def _autosave_loaded_chat(self) -> None:
        directory = str(self.settings.get("default_export_dir") or self.last_directory)
        Path(directory).mkdir(parents=True, exist_ok=True)
        saved = self._save_all_to_directory(directory, interactive=False)
        if len(saved) == 5:
            self.status_var.set(f"AUTO-SAVE PASS — 5 Formate in {directory}")

    def _remember_directory(self) -> None:
        if bool(self.settings.get("remember_last_directory", True)):
            self.settings["default_export_dir"] = self.last_directory
            self._save_settings()

    # ------------------------------------------------------------------
    # Settings / dialogs
    # ------------------------------------------------------------------
    def open_settings(self) -> None:
        win = tk.Toplevel(self)
        win.title("666 ChatBackup — " + self._t("Einstellungen"))
        win.configure(bg=BG)
        win.geometry("700x730")
        win.minsize(620, 650)
        win.transient(self)
        win.grab_set()
        try:
            if "icon" in self._photos:
                win.iconphoto(True, self._photos["icon"])
        except tk.TclError:
            pass

        panel = NeonPanel(win, accent=PURPLE, bg=PANEL)
        panel.pack(fill="both", expand=True, padx=14, pady=14)
        panel.grid_columnconfigure(1, weight=1)

        tk.Label(panel, text=self._t("Einstellungen"), bg=PANEL, fg=PINK, font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(14, 16)
        )

        export_var = tk.StringVar(value=str(self.settings.get("default_export_dir", self.last_directory)))
        remember_var = tk.BooleanVar(value=bool(self.settings.get("remember_last_directory", True)))
        autosave_var = tk.BooleanVar(value=bool(self.settings.get("autosave_after_link_load", False)))
        verify_var = tk.BooleanVar(value=bool(self.settings.get("verify_exports", True)))
        banner_var = tk.BooleanVar(value=bool(self.settings.get("show_banner", True)))
        animations_var = tk.BooleanVar(value=bool(self.settings.get("animations", True)))
        line_var = tk.StringVar(value=str(self.settings.get("line_endings", "Original")))
        font_var = tk.IntVar(value=int(self.settings.get("editor_font_size", 11)))
        window_mode_value = str(self.settings.get("window_mode", "Large"))
        window_var = tk.StringVar(value=self._t("Maximiert") if window_mode_value in {"Maximized", "Maximiert"} else self._t("Groß"))
        integrate_images_var = tk.BooleanVar(value=bool(self.settings.get("integrate_images", True)))
        download_share_images_var = tk.BooleanVar(value=bool(self.settings.get("download_share_images", True)))
        open_image_browser_var = tk.BooleanVar(value=bool(self.settings.get("open_image_browser_after_load", False)))
        preserve_raw_var = tk.BooleanVar(value=bool(self.settings.get("preserve_raw_share_source", True)))

        def label(row: int, text: str) -> None:
            tk.Label(panel, text=text, bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(
                row=row, column=0, sticky="w", padx=(16, 10), pady=8
            )

        label(1, self._t("Standard-Speicherordner"))
        entry = tk.Entry(
            panel,
            textvariable=export_var,
            bg="#07101E",
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat",
            highlightthickness=1,
            highlightbackground=CYAN,
        )
        entry.grid(row=1, column=1, sticky="ew", pady=8, ipady=5)

        def browse() -> None:
            chosen = filedialog.askdirectory(title=self._t("Standard-Speicherordner"), initialdir=export_var.get() or self.last_directory)
            if chosen:
                export_var.set(chosen)

        NeonButton(panel, text=self._t("Wählen"), command=browse, accent=CYAN, compact=True).grid(
            row=1, column=2, sticky="e", padx=12, pady=8
        )

        label(2, self._t("Zeilenumbrüche"))
        combo = ttk.Combobox(
            panel,
            textvariable=line_var,
            values=("Original", "Windows (CRLF)", "Unix (LF)"),
            state="readonly",
            style="Neon.TCombobox",
        )
        combo.grid(row=2, column=1, columnspan=2, sticky="ew", padx=(0, 12), pady=8)

        label(3, self._t("Editor-Schriftgröße"))
        scale = tk.Scale(
            panel,
            variable=font_var,
            from_=9,
            to=18,
            orient="horizontal",
            bg=PANEL,
            fg=TEXT,
            troughcolor="#08111E",
            activebackground=PINK,
            highlightthickness=0,
        )
        scale.grid(row=3, column=1, columnspan=2, sticky="ew", padx=(0, 12), pady=8)

        label(4, self._t("Startfenster"))
        window_combo = ttk.Combobox(
            panel,
            textvariable=window_var,
            values=(self._t("Groß"), self._t("Maximiert")),
            state="readonly",
            style="Neon.TCombobox",
        )
        window_combo.grid(row=4, column=1, columnspan=2, sticky="ew", padx=(0, 12), pady=8)

        checks = [
            (5, self._t("Letzten Speicherordner merken"), remember_var),
            (6, self._t("Nach Share-Link-Laden automatisch alle 5 Formate speichern"), autosave_var),
            (7, self._t("Export nach dem Schreiben bytegenau verifizieren"), verify_var),
            (8, self._t("Cyber-Neon-Banner anzeigen"), banner_var),
            (9, self._t("UI-Animationen / Fortschrittsanzeigen"), animations_var),
            (10, self._t("Bilder in Portable-Backups integrieren"), integrate_images_var),
            (11, self._t("Direkt erreichbare Bilder aus Share-Chats herunterladen"), download_share_images_var),
            (12, self._t("Chat-Bildbrowser nach dem Laden automatisch öffnen"), open_image_browser_var),
            (13, self._t("Original-Share-Quelldaten für Reparse/Archiv erhalten"), preserve_raw_var),
        ]
        for row, text, var in checks:
            chk = tk.Checkbutton(
                panel,
                text=text,
                variable=var,
                bg=PANEL,
                fg=TEXT,
                activebackground=PANEL,
                activeforeground=CYAN,
                selectcolor="#07101E",
                highlightthickness=0,
                font=("Segoe UI", 10),
                anchor="w",
            )
            chk.grid(row=row, column=0, columnspan=3, sticky="w", padx=16, pady=6)

        buttons = tk.Frame(panel, bg=PANEL)
        buttons.grid(row=14, column=0, columnspan=3, sticky="ew", padx=16, pady=(20, 14))
        buttons.grid_columnconfigure(0, weight=1)
        buttons.grid_columnconfigure(1, weight=1)
        buttons.grid_columnconfigure(2, weight=1)

        def save() -> None:
            self.settings.update(
                {
                    "default_export_dir": export_var.get().strip() or self.last_directory,
                    "remember_last_directory": remember_var.get(),
                    "autosave_after_link_load": autosave_var.get(),
                    "verify_exports": verify_var.get(),
                    "show_banner": banner_var.get(),
                    "animations": animations_var.get(),
                    "line_endings": line_var.get(),
                    "editor_font_size": int(font_var.get()),
                    "window_mode": "Maximized" if window_var.get() in {"Maximized", "Maximiert"} else "Large",
                    "integrate_images": integrate_images_var.get(),
                    "download_share_images": download_share_images_var.get(),
                    "open_image_browser_after_load": open_image_browser_var.get(),
                    "preserve_raw_share_source": preserve_raw_var.get(),
                }
            )
            self.last_directory = str(self.settings["default_export_dir"])
            self.editor.configure(font=("Consolas", int(font_var.get())))
            if banner_var.get():
                self.banner_frame.grid()
            else:
                self.banner_frame.grid_remove()
            self._save_settings()
            self.status_var.set(self._t("EINSTELLUNGEN — gespeichert."))
            self._log("SETTINGS_SAVED")
            win.destroy()

        def reset() -> None:
            if not messagebox.askyesno(self._t("Zurücksetzen"), self._t("Alle Einstellungen auf Standard zurücksetzen?"), parent=win):
                return
            self.settings = dict(DEFAULT_SETTINGS)
            self._save_settings()
            win.destroy()
            self.open_settings()

        NeonButton(buttons, text=self._t("Standard"), command=reset, accent=PURPLE).grid(row=0, column=0, sticky="ew", padx=4)
        NeonButton(buttons, text=self._t("Abbrechen"), command=win.destroy, accent=CYAN).grid(row=0, column=1, sticky="ew", padx=4)
        NeonButton(buttons, text=self._t("Speichern"), command=save, accent=PINK, surface=PINK_SOFT).grid(
            row=0, column=2, sticky="ew", padx=4
        )

    def show_system_status(self) -> None:
        status_path = Path(self.bootstrap_status_file) if self.bootstrap_status_file else None
        lines = [f"666 ChatBackup PC Tool v{APP_VERSION}", "", "Node.js: NOT_REQUIRED", "NPM: NOT_REQUIRED"]
        if not status_path or not status_path.exists():
            lines.extend(
                [
                    self._bi("Bootstrap log: not available / standalone start", "Bootstrap-Protokoll: nicht vorhanden / Standalone-Start"),
                    self._bi("Application: STARTED", "Anwendung: GESTARTET"),
                    "GUI: PASS",
                ]
            )
            messagebox.showinfo(self._t("Systemstatus"), "\n".join(lines))
            return
        try:
            payload = json.loads(status_path.read_text(encoding="utf-8-sig"))
            details = payload.get("details", {})
            python_info = details.get("python", {}) if isinstance(details, dict) else {}
            tkinter_info = details.get("tkinter", {}) if isinstance(details, dict) else {}
            pillow_info = details.get("pillow", {}) if isinstance(details, dict) else {}
            lines.insert(1, f"{self._bi('Status', 'Status')}: {payload.get('status', self._bi('UNKNOWN', 'UNBEKANNT'))}")
            lines.insert(2, f"{self._bi('Summary', 'Zusammenfassung')}: {payload.get('summary', '')}")
            if isinstance(python_info, dict):
                if python_info.get("required") is False:
                    lines.append(self._bi("Python: not required for standalone EXE", "Python: für Standalone-EXE nicht erforderlich"))
                elif python_info.get("version"):
                    lines.append(f"Python: {python_info.get('version')}")
            if isinstance(tkinter_info, dict) and tkinter_info.get("present"):
                lines.append(f"Tkinter/Tk: {tkinter_info.get('version', self._bi('available', 'verfügbar'))}")
            if isinstance(pillow_info, dict) and pillow_info.get("present"):
                lines.append(f"{self._bi('Pillow/Image Preview', 'Pillow/Bildvorschau')}: {pillow_info.get('version', self._bi('available', 'verfügbar'))}")
            lines.append(f"{self._bi('Log', 'Protokoll')}: {payload.get('logPath', '')}")
            messagebox.showinfo(self._t("Automatischer Systemstatus"), "\n".join(lines))
        except Exception as exc:
            messagebox.showerror(self._t("Systemstatus"), self._t("Statusdatei konnte nicht gelesen werden:\n\n") + self._localize_runtime(exc))

    def show_log(self) -> None:
        win = tk.Toplevel(self)
        win.title("666 ChatBackup — " + self._t("Protokoll"))
        win.configure(bg=BG)
        win.geometry("900x560")
        text = tk.Text(
            win,
            bg="#050A12",
            fg="#DCE9FF",
            insertbackground=CYAN,
            font=("Consolas", 10),
            wrap="none",
            relief="flat",
            padx=12,
            pady=12,
        )
        text.pack(fill="both", expand=True, padx=12, pady=(12, 6))
        try:
            content = self.log_path.read_text(encoding="utf-8-sig") if self.log_path.exists() else self._t("Noch keine Protokolleinträge.")
        except Exception as exc:
            content = self._t("Protokoll konnte nicht gelesen werden: ") + str(exc)
        text.insert("1.0", content)
        text.configure(state="disabled")
        NeonButton(win, text=self._t("Schließen"), command=win.destroy, accent=PINK).pack(pady=(0, 12))

    def show_about(self) -> None:
        messagebox.showinfo(
            self._t("Über 666 ChatBackup"),
            (f"666 ChatBackup PC Tool v{APP_VERSION}\n\n" +
             ("Load public ChatGPT share links or paste chat text manually, edit it, and export as TXT, MD, JavaScript, JSON or JSONL. The v1.5 Chat Backend preserves raw content/metadata, parser provenance and Copy/UI fields; the Structure Inspector makes these data visible. v1.8 adds explicit multi-participant/group-chat preservation for structured shares and manual transcripts. The Chat Image Browser controls selective image preservation in Portable ZIP backups." if self._lang()=="en" else
              "ChatGPT-Share-Link laden oder Chattext manuell einfügen, bearbeiten und als TXT, MD, JavaScript, JSON oder JSONL exportieren. Das v1.5-ChatBackend erhält Raw Content/Metadata, Parser-Provenienz und Copy-/UI-Felder; der Struktur-Inspector macht diese Daten sichtbar. v1.8 ergänzt die explizite Mehrteilnehmer-/Gruppenchat-Erhaltung für strukturierte Shares und manuelle Verläufe. Der Chat-Bildbrowser steuert weiterhin die selektive Bildsicherung im Portable ZIP.") +
             f"\n\n{COPYRIGHT_TEXT}"),
        )

    def _log(self, message: str) -> None:
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().astimezone().isoformat(timespec="seconds")
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(f"{stamp} | {message}\n")
        except Exception:
            pass

    def on_close(self) -> None:
        self._save_settings()
        self._log("EXIT")
        self.destroy()


def main() -> None:
    app = ChatBackupApp()
    app.mainloop()


if __name__ == "__main__":
    main()
