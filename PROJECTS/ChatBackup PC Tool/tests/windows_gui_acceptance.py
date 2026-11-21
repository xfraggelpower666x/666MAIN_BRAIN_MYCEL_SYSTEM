"""Windows-Tkinter-Hostprobe für das ursprüngliche 666 CHATBACKUP PC TOOL.

Startet echte Fenster aus der Python-Hauptanwendung und bedient die R5.5-
Archivfacette mit rein synthetischen Testnachrichten. Keine Produktivdaten,
kein Export-Import und keine Registry-Mutation.
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "app"), str(ROOT / "tools")]
os.environ["CHATBACKUP_BOOTSTRAP_STATUS"] = "PASS"


def walk(widget):
    yield widget
    for child in widget.winfo_children():
        yield from walk(child)


def buttons(root):
    return {
        widget.cget("text"): widget
        for widget in walk(root)
        if isinstance(widget, tk.Button)
    }


def require(condition, reason):
    if not condition:
        raise AssertionError(reason)


def load_original():
    loader = importlib.machinery.SourceFileLoader("chatbackup_gui_real_host_acceptance", str(ROOT / "app" / "chatbackup_gui.pyw"))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def main():
    assert os.name == "nt", "Windows host required"
    module = load_original()
    app = module.ChatBackupApp()
    evidence = {"schema": "666.chatbackup.windows-tk-host.v1",
                "original_identity": app.title(),
                "original_entry": "app/chatbackup_gui.pyw",
                "source_host": True,
                "compiled_exe_visual_acceptance": False,
                "tests": {}}
    archive = None
    treewin = None
    try:
        app.update_idletasks()
        app.update()
        require("666 ChatBackup PC Tool v" in app.title(), "Main app identity changed")
        evidence["tests"]["main_window"] = "PASS"
        main_buttons = buttons(app)
        require(any("Archive Intelligence" in title for title in main_buttons), "Archive button missing from original sidebar")
        app.open_archive_intelligence()
        app.update()
        archive = app._archive_intelligence_window
        require(isinstance(archive, tk.Toplevel), "Archive was not opened as a Tk child window")
        require(archive.master is app, "Archive not parented to original application")
        require(archive.winfo_exists(), "Archive window not created")
        evidence["tests"]["sidebar_to_archive"] = "PASS"
        require("Search" in buttons(archive), "Archive search button missing")
        require("View conversation" in buttons(archive), "Archive conversation viewer missing")
        app.open_archive_intelligence()
        require(app._archive_intelligence_window is archive, "Repeated open duplicated Archive window")
        evidence["tests"]["archive_reopen"] = "PASS"

        from archive_branch_tree_ui import open_branch_tree_window
        selected = []
        messages = [
            {"id": f"r55-fixture-{i}", "parent": f"r55-fixture-{i - 1}" if i else None,
             "role": "user" if i % 2 else "assistant",
             "text": f"indexed fixture message {i} special-end" if i == 429 else f"indexed fixture message {i}"}
            for i in range(430)
        ]
        treewin = open_branch_tree_window(archive, {"id": "r55-fixture", "messages": messages}, 0, selected.append)
        app.update_idletasks()
        app.update()
        require(isinstance(treewin, tk.Toplevel), "Tree window not created")
        evidence["tests"]["tree_window"] = "PASS"
        entries = [w for w in walk(treewin) if isinstance(w, tk.Entry)]
        require(entries, "Tree search entry missing")
        search = entries[0]
        search.insert(0, "indexed fixture")
        treebuttons = buttons(treewin)
        require("Search tree" in treebuttons, "Tree search action missing")
        treebuttons["Search tree"].invoke()
        app.update()
        tables = [w for w in walk(treewin) if isinstance(w, ttk.Treeview)]
        hits = next((w for w in tables if "id" in w["columns"] and "path" in w["columns"]), None)
        require(hits is not None and len(hits.get_children()) == 200, "First 200 search results not rendered")
        evidence["tests"]["search_first_page"] = "PASS"
        treebuttons["▶"].invoke()
        app.update()
        require(len(hits.get_children()) == 200, "Second search page not rendered")
        treebuttons["▶"].invoke()
        app.update()
        require(len(hits.get_children()) == 30, "Last search page not rendered")
        evidence["tests"]["search_pagination_430"] = "PASS"
        last = hits.get_children()[-1]
        require(hits.item(last, "values")[0] == "r55-fixture-429", "Final indexed ID mismatch")
        hits.selection_set(last)
        treebuttons["Open selected tree-search result"].invoke()
        app.update()
        require(selected and selected[-1] == 429, "Exact-message jump callback failed")
        evidence["tests"]["search_result_to_original_id"] = "PASS"
        require("666 ChatBackup PC Tool v" in app.title(), "Original app lost identity")
        evidence["tests"]["original_app_preserved"] = "PASS"
        print("WINDOWS_TK_REAL_HOST_INTERACTION_PASS")
    finally:
        try:
            if treewin is not None and treewin.winfo_exists():
                treewin.destroy()
            if archive is not None and archive.winfo_exists():
                archive.destroy()
            app.destroy()
        finally:
            target = ROOT / "runtime_readback" / "WINDOWS_GUI_CI_PROBE.json"
            target.parent.mkdir(exist_ok=True)
            target.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
