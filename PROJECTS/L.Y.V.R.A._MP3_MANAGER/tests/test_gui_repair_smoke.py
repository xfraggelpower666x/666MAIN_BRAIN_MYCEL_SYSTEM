"""Virtueller Tk-Smoketest, kein nativer Windows-DPI-Nachweis."""
import pathlib,runpy,tkinter as tk
m=runpy.run_path(str(pathlib.Path(__file__).resolve().parents[1]/'MP3_Manager.pyw'),run_name='gui_test')
root=tk.Tk()
try:
 app=m['App'](root)
 for w,h in ((1024,680),(1450,900),(1920,1080)):
  root.geometry(f'{w}x{h}+0+0');root.update_idletasks();root.update()
  assert callable(app.start_repair_from_wav)
  assert app.quality_preset.get()=='maximum'
  assert app.normalize.get() is False
  assert app.audio_qc.get() is True
  all_buttons=[]
  def visit(widget):
   if isinstance(widget,tk.Button) or widget.winfo_class().endswith('Button'):
    try:all_buttons.append(widget.cget('text'))
    except:pass
   for child in widget.winfo_children():visit(child)
  visit(root)
  assert any('REPAIR' in x for x in all_buttons), all_buttons
  print('PASS virtual Tk GUI',w,h,'repair button found; maximum no normalization')
finally:root.destroy()
