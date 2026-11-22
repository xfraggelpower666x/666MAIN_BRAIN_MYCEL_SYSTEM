"""Optional local Tk capacity window; does not touch physical LEDs or change lock states."""
import tkinter as tk
from .volumes import VolumeSampler


def main():
    root=tk.Tk()
    root.title("Keyboard LED Remapper | Storage Capacity")
    root.geometry("460x310")
    root.configure(bg="#121625")
    text=tk.Text(root,bg="#121625",fg="#b6ffe8",font=("Consolas",11),borderwidth=0,highlightthickness=0)
    text.pack(fill="both",expand=True,padx=12,pady=12)
    sampler=VolumeSampler()
    def refresh():
        items,errors=sampler.sample()
        text.configure(state="normal")
        text.delete("1.0","end")
        text.insert("end","STORAGE CAPACITY | READ-ONLY\n\n")
        for v in items:
            text.insert("end",f"{v.mountpoint}  {v.free_bytes/1024**3:.1f} GiB free\n  {v.used_percent:.1f}% used  [{v.status.upper()}]\n\n")
        for mount,why in errors.items():
            text.insert("end",f"{mount}: unavailable ({why})\n")
        text.configure(state="disabled")
        root.after(5000,refresh)
    refresh()
    root.mainloop()

if __name__=="__main__": main()
