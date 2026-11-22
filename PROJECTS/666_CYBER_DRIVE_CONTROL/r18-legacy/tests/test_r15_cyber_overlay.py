"""R15 non-invasive regression tests for display layouts and idle filtering."""
from types import SimpleNamespace
from klrw.drive_workspace import Workspace, DriveInfo
from klrw.bicolor_activity import BicolorActivity, CYAN, PINK, OFF
from klrw.drive_workspace_window import DriveWorkspaceWindow

def _rate(r,w):
    return SimpleNamespace(read_bps=r,write_bps=w)

def test_bicolor_colors_and_hold():
    x=BicolorActivity()
    assert x.sample('C',_rate(0,0),0)==OFF
    assert x.sample('C',_rate(60_000,0),500)==CYAN
    assert x.sample('C',_rate(0,0),600)==CYAN
    assert x.sample('C',_rate(0,0),700)==OFF
    assert x.sample('C',_rate(0,80_000),1000)==PINK

def test_idle_noise_no_permanent_light():
    x=BicolorActivity()
    for i in range(100):
        assert x.sample('C',_rate(0,3000),i*500)==OFF

def test_sustained_background_adaptive():
    x=BicolorActivity()
    results=[x.sample('C',_rate(0,25_000),i*500) for i in range(90)]
    assert results[-15:]==[OFF]*15

def test_missing_rate_is_not_activity():
    x=BicolorActivity()
    assert x.sample('USB',_rate(80000,0),0)==CYAN
    assert x.sample('USB',None,30)==OFF
    x.forget_missing({'other'})
    assert 'USB' not in x.states

def test_preferences_layout_timing_and_colors(tmp_path):
    path=tmp_path/'prefs.json'
    w=Workspace(path)
    w.data['overlay']['layout']='horizontal'
    w.data['led_hold_ms']=400
    w.data['led_quiet_ms']=700
    w.save()
    loaded=Workspace(path)
    assert loaded.data['overlay']['layout']=='horizontal'
    assert loaded.data['led_hold_ms']==400
    assert loaded.data['led_quiet_ms']==700
    assert loaded.data['read_color']==CYAN and loaded.data['write_color']==PINK

class CanvasFake:
    def __init__(self):
        self.ovals=0
        self.width=0
        self.height=0
    def config(self,**kw):
        self.width=kw['width'];self.height=kw['height']
    def delete(self,*args):pass
    def create_text(self,*args,**kw):pass
    def create_oval(self,*args,**kw):self.ovals+=1

class OverlayFake:
    def winfo_exists(self):return True

class SamplerFake:
    def devices(self):return []

def test_overlay_has_one_led_per_drive_in_both_modes(tmp_path):
    w=Workspace(tmp_path/'prefs.json')
    drives=[DriveInfo('mount:a:','A:','A','','NTFS'),DriveInfo('mount:c:','C:','C','','NTFS')]
    for d in drives:w.preferences(d)['overlay']=True
    obj=object.__new__(DriveWorkspaceWindow)
    obj.overlay=OverlayFake()
    obj.overlay_canvas=CanvasFake()
    obj.drives=drives
    obj.workspace=w
    obj.sampler=SamplerFake()
    obj.bicolor=BicolorActivity()
    w.data['overlay']['layout']='vertical'
    obj.redraw_overlay({})
    assert obj.overlay_canvas.ovals==2
    vertical=(obj.overlay_canvas.width,obj.overlay_canvas.height)
    obj.overlay_canvas.ovals=0
    w.data['overlay']['layout']='horizontal'
    obj.redraw_overlay({})
    assert obj.overlay_canvas.ovals==2
    horizontal=(obj.overlay_canvas.width,obj.overlay_canvas.height)
    assert horizontal[1] < vertical[1]
