"""Start mit: python demo.py"""
import tkinter as tk
from tkinter import ttk

from app_intro import IntroConfig, IntroResult, IntroWindow, Phase


def main() -> None:
    root = tk.Tk()
    root.withdraw()
    root.title("Beispielanwendung")
    root.geometry("600x360")
    ttk.Label(root, text="Die Anwendung ist gestartet.").pack(expand=True)

    def after_intro(result: IntroResult) -> None:
        if result is IntroResult.READY:
            root.deiconify()
        else:
            root.destroy()

    IntroWindow(
        root,
        IntroConfig(
            title="Beispielanwendung",
            version="1.0",
            phases=(
                Phase("Initialisierung", "Start wird vorbereitet …", 25, 450),
                Phase("Anwendung", "Übergabe an das Hauptfenster …", 80, 550),
            ),
        ),
        after_intro,
    )
    root.mainloop()


if __name__ == "__main__":
    main()
