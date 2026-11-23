"""Persistent drive selections, conservative I/O identity mapping, hot-plug inventory.

Volume IDs and I/O counter keys are DIFFERENT namespaces. No guessed association.
All state saved as user-local JSON; never silently writes to external devices.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import json
import os
import sys
import tempfile
import psutil

DRIVE_SEED = ('A:', 'B:', 'C:', 'E:', 'F:', 'X:', 'Y:', 'Z:')


def default_path() -> Path:
    base = os.environ.get('LOCALAPPDATA') if sys.platform == 'win32' else None
    if not base:
        base = str(Path.home() / '.config')
    return Path(base) / 'KeyboardLEDRemapper' / 'drive_workspace.json'


def normalized_mount(mount: str) -> str:
    text = str(mount).strip().replace('/', '\\')
    if len(text) >= 2 and text[1] == ':' and text[0].isalpha():
        return text[:2].upper()
    return text


def stable_volume_key(part, volume_id=None) -> str:
    """Windows volume GUID takes precedence when available; fallback mount key only.

    Fallbacks cannot guarantee persistence across drive letter changes.
    """
    if volume_id:
        return 'volume:' + volume_id.casefold()
    return 'mount:' + normalized_mount(part.mountpoint).casefold()


@dataclass(frozen=True)
class DriveInfo:
    key: str
    mount: str
    label: str
    device: str
    filesystem: str
    io_key: str | None = None
    removable: bool = False


def windows_volume_guid(mount: str) -> str | None:
    if sys.platform != 'win32' or len(mount) < 2 or mount[1] != ':':
        return None
    try:
        import ctypes
        from ctypes import wintypes
        buffer = ctypes.create_unicode_buffer(512)
        fn = ctypes.windll.kernel32.GetVolumeNameForVolumeMountPointW
        fn.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        fn.restype = wintypes.BOOL
        if fn(mount[:2] + '\\', buffer, len(buffer)):
            return buffer.value.rstrip('\\')
    except (OSError, ValueError, AttributeError):
        pass
    return None


def windows_volume_label(mount: str) -> str:
    if sys.platform != 'win32' or len(mount) < 2 or mount[1] != ':':
        return ''
    try:
        import ctypes
        from ctypes import wintypes
        name = ctypes.create_unicode_buffer(256)
        serial = wintypes.DWORD()
        max_comp = wintypes.DWORD()
        flags = wintypes.DWORD()
        fstype = ctypes.create_unicode_buffer(256)
        fn = ctypes.windll.kernel32.GetVolumeInformationW
        ok = fn(mount[:2] + '\\', name, len(name), ctypes.byref(serial), ctypes.byref(max_comp), ctypes.byref(flags), fstype, len(fstype))
        return name.value if ok else ''
    except (OSError, ValueError, AttributeError):
        return ''


def enumerate_drives(ps=psutil, *, guid_reader=windows_volume_guid, label_reader=windows_volume_label) -> list[DriveInfo]:
    """Read-only volume inventory. WMI/Windows per-volume I/O correlation is not assumed."""
    found: dict[str, DriveInfo] = {}
    try:
        parts = ps.disk_partitions(all=False)
    except (OSError, RuntimeError):
        parts = []
    for p in parts:
        mount = normalized_mount(p.mountpoint)
        if not mount:
            continue
        guid = guid_reader(mount)
        key = stable_volume_key(p, guid)
        try: label = label_reader(mount)
        except (OSError, AttributeError): label = ''
        opts = str(getattr(p, 'opts', '')).lower()
        found[key] = DriveInfo(key, mount, label, str(p.device), str(p.fstype), None, 'removable' in opts)
    return sorted(found.values(), key=lambda d: (d.mount.casefold(), d.key))


def exact_io_map(drives: list[DriveInfo], io_devices: set[str]) -> dict[str, str]:
    """Permit only exact device name match; never map C: to PhysicalDrive0 by guess."""
    return {d.key:d.device for d in drives if d.device in io_devices}


def default_entry():
    return {'tray': False, 'overlay': False, 'keyboard': False}


def default_state():
    return {'schema':1,'drives':{},'letter_preferences':{
        m:{'tray': True,'overlay':True,'keyboard':False} for m in DRIVE_SEED},
        'overlay':{'x':110,'y':110,'locked':False,'alpha':0.92,'size':1.0,'layout':'vertical'},
        'read_color':'#35E0FF','write_color':'#FF4FD8', 'interval_ms':500,
        'speed_unit':'KiB/s', 'speed_decimals':1, 'display_mode':'detailed', 'activity_threshold_bps':4096,'burst_bps':16384,'led_hold_ms':180,'led_quiet_ms':450}


class Workspace:
    def __init__(self,path=None):
        self.path = Path(path) if path is not None else default_path()
        self.data = default_state()
        self.load()

    def load(self):
        if not self.path.is_file(): return
        try:
            content = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(content,dict) or content.get('schema') != 1: return
            if isinstance(content.get('drives'),dict):
                for key,val in content['drives'].items():
                    if isinstance(key,str) and isinstance(val,dict):
                        self.data['drives'][key] = {k:bool(val.get(k,False)) for k in ('tray','overlay','keyboard')}
            if isinstance(content.get('letter_preferences'),dict):
                for key,val in content['letter_preferences'].items():
                    if isinstance(key,str) and isinstance(val,dict):
                        self.data['letter_preferences'][key] = {k:bool(val.get(k,False)) for k in ('tray','overlay','keyboard')}
            if isinstance(content.get('overlay'),dict):
                p=content['overlay']
                for coord in ('x','y'):
                    if isinstance(p.get(coord),int) and not isinstance(p.get(coord),bool) and -10000<=p[coord]<=10000:
                        self.data['overlay'][coord]=p[coord]
                self.data['overlay']['locked']=bool(p.get('locked',False))
                if p.get('layout') in ('vertical','horizontal','minimal'):
                    self.data['overlay']['layout']=p['layout']
                if isinstance(p.get('alpha'),(int,float)) and 0.35<=p['alpha']<=1:
                    self.data['overlay']['alpha']=float(p['alpha'])
                if isinstance(p.get('size'),(int,float)) and 0.65<=p['size']<=2:
                    self.data['overlay']['size']=float(p['size'])
            for k in ('read_color','write_color'):
                value=content.get(k)
                if isinstance(value,str) and len(value)==7 and value[0]=='#' and all(c in '0123456789abcdefABCDEF' for c in value[1:]):
                    self.data[k]=value
            unit=content.get('speed_unit')
            if unit in ('KiB/s','MiB/s','MB/s','bit/s'):self.data['speed_unit']=unit
            decimals=content.get('speed_decimals')
            if type(decimals)==int and 0<=decimals<=3:self.data['speed_decimals']=decimals
            mode=content.get('display_mode')
            if mode in ('compact','detailed'):self.data['display_mode']=mode
            threshold=content.get('activity_threshold_bps')
            if type(threshold)==int and 0<=threshold<=1_000_000:self.data['activity_threshold_bps']=threshold
            for key,minimum,maximum in (('burst_bps',0,104857600),('led_hold_ms',40,2000),('led_quiet_ms',100,10000)):
                val=content.get(key)
                if type(val)==int and minimum<=val<=maximum:self.data[key]=val
            iv=content.get('interval_ms')
            if type(iv)==int and 150<=iv<=10000:self.data['interval_ms']=iv
        except (OSError, ValueError, UnicodeError):
            # Unreadable preference file must not abort monitor; untouched on disk.
            pass

    def preferences(self, drive:DriveInfo):
        if drive.key not in self.data['drives']:
            self.data['drives'][drive.key] = dict(self.data['letter_preferences'].get(drive.mount,default_entry()))
        return self.data['drives'][drive.key]

    def save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        # atomic replace to avoid partial config after crash
        fd, tmp = tempfile.mkstemp(prefix='.drive_workspace_',suffix='.json',dir=self.path.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as stream:
                json.dump(self.data,stream,indent=2,ensure_ascii=False)
            os.replace(tmp,self.path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
