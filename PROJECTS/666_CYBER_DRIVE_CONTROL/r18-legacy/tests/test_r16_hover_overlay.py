"""R16: compact one-LED overlay and read-only mouseover information."""
from types import SimpleNamespace
from klrw.drive_workspace import Workspace,DriveInfo
from klrw.drive_workspace_window import DriveWorkspaceWindow, drive_hover_details
from klrw.bicolor_activity import OFF, CYAN

class FakeCanvas:
    def __init__(self): self.ovals=[];self.width=0;self.height=0
    def config(self,**kw):self.width=kw['width'];self.height=kw['height']
    def delete(self,*args):pass
    def create_text(self,*args,**kw):pass
    def create_oval(self,*args,**kw):self.ovals.append((args,kw))
class FakeOverlay:
    def winfo_exists(self):return True
class FakeSampler:
    def devices(self):return []
class FakeBicolor:
    states={}

def test_minimal_layout_saved_and_rendered(tmp_path):
    w=Workspace(tmp_path/'config.json')
    assert w.data['led_hold_ms']==180
    assert w.data['led_quiet_ms']==450
    assert w.data['activity_threshold_bps']==4096
    w.data['overlay']['layout']='minimal';w.save()
    w=Workspace(tmp_path/'config.json')
    assert w.data['overlay']['layout']=='minimal'
    drives=[DriveInfo(f'drive:{letter}',letter,letter,'','NTFS') for letter in ('A:','C:','Z:')]
    for d in drives:w.preferences(d)['overlay']=True
    obj=object.__new__(DriveWorkspaceWindow)
    obj.overlay=FakeOverlay();obj.overlay_canvas=FakeCanvas();obj.drives=drives
    obj.workspace=w;obj.sampler=FakeSampler();obj.bicolor=FakeBicolor()
    obj.redraw_overlay({})
    assert len(obj.overlay_canvas.ovals)==3
    assert len(obj._hover_regions)==3
    assert obj.overlay_canvas.width < 120
    assert obj.overlay_canvas.height > obj.overlay_canvas.width

def test_mouseover_shows_detailed_labels_and_io():
    d=DriveInfo('k','C:','WINDOWS 11 PRO x64','\\\\device','NTFS')
    cfg=Workspace().data
    rate=SimpleNamespace(read_bps=1234.0,write_bps=118000.0)
    description=drive_hover_details(d,rate,cfg,CYAN)
    assert 'WINDOWS 11 PRO x64' in description
    assert 'C:' in description
    assert 'Lesen' in description
    assert 'Schreiben' not in description.splitlines()[1]
    assert 'NTFS' in description
    assert 'Messung verfügbar' in description
    missing=drive_hover_details(d,None,cfg,OFF)
    assert 'nicht zugeordnet' in missing
