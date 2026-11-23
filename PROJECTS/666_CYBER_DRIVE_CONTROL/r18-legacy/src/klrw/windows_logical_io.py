"""Optional Windows PDH logical drive read/write rates (no WMI or drivers).

Uses English PDH counters to avoid localized counter names. Fail closed when
unsupported. A logical volume maps to its OWN LogicalDisk(X:) counter, not to a
physical disk counter by guess. Requires actual Windows GUI readback.
"""
from __future__ import annotations
import ctypes
import sys
from ctypes import wintypes
from .ssd import DiskRates

PDH_FMT_DOUBLE = 0x00000200
PDH_CSTATUS_VALID_DATA = 0
PDH_CSTATUS_NEW_DATA = 1

class _ValueUnion(ctypes.Union):
    _fields_ = [('longValue', wintypes.LONG), ('doubleValue', ctypes.c_double), ('largeValue', ctypes.c_longlong)]

class _PdhFmt(ctypes.Structure):
    _fields_ = [('CStatus', wintypes.DWORD), ('value', _ValueUnion)]


class WindowsLogicalDiskSampler:
    """PDH counter pair per Windows drive letter. No simulated activity."""
    def __init__(self, pdh=None):
        if pdh is None:
            if sys.platform != 'win32':
                raise OSError('PDH is available only on Windows')
            pdh = ctypes.WinDLL('pdh')
        self.pdh = pdh
        self.query = ctypes.c_void_p()
        self.counters = {}
        self.closed = False
        pdh.PdhOpenQueryW.argtypes = (wintypes.LPCWSTR, ctypes.c_size_t, ctypes.POINTER(ctypes.c_void_p))
        pdh.PdhOpenQueryW.restype = wintypes.DWORD
        pdh.PdhAddEnglishCounterW.argtypes = (ctypes.c_void_p,wintypes.LPCWSTR,ctypes.c_size_t,ctypes.POINTER(ctypes.c_void_p))
        pdh.PdhAddEnglishCounterW.restype = wintypes.DWORD
        pdh.PdhCollectQueryData.argtypes = (ctypes.c_void_p,)
        pdh.PdhCollectQueryData.restype = wintypes.DWORD
        pdh.PdhGetFormattedCounterValue.argtypes = (ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD),ctypes.POINTER(_PdhFmt))
        pdh.PdhGetFormattedCounterValue.restype = wintypes.DWORD
        pdh.PdhRemoveCounter.argtypes = (ctypes.c_void_p,)
        pdh.PdhRemoveCounter.restype = wintypes.DWORD
        pdh.PdhCloseQuery.argtypes = (ctypes.c_void_p,)
        pdh.PdhCloseQuery.restype = wintypes.DWORD
        rc = pdh.PdhOpenQueryW(None,0,ctypes.byref(self.query))
        if rc: raise OSError(f'PdhOpenQueryW: 0x{rc:08x}')

    def configure(self, drive_letters):
        """Reconcile live volumes; old handles must not survive USB unplug/replug."""
        wanted={s.upper() for s in drive_letters if isinstance(s,str) and len(s)==2 and s[1]==':' and s[0].isalpha()}
        for letter in list(self.counters):
            if letter not in wanted:
                for handle in self.counters.pop(letter):
                    self.pdh.PdhRemoveCounter(handle)
        for letter in sorted(wanted):
            if not isinstance(letter,str) or len(letter)!=2 or letter[1]!=':' or not letter[0].isalpha():
                continue
            letter=letter.upper()
            if letter in self.counters:continue
            handles=[]
            for metric in ('Disk Read Bytes/sec', 'Disk Write Bytes/sec'):
                counter=ctypes.c_void_p()
                path=f'\\LogicalDisk({letter})\\{metric}'
                rc=self.pdh.PdhAddEnglishCounterW(self.query,path,0,ctypes.byref(counter))
                if rc:
                    for old in handles:self.pdh.PdhRemoveCounter(old)
                    handles=[]
                    break
                handles.append(counter)
            if len(handles)==2:self.counters[letter]=tuple(handles)
        if self.counters:self.pdh.PdhCollectQueryData(self.query)

    def sample_all(self):
        if self.closed or not self.counters:return {}
        if self.pdh.PdhCollectQueryData(self.query):return {}
        result={}
        for letter,(read,write) in self.counters.items():
            values=[]
            for handle in (read,write):
                v=_PdhFmt()
                rc=self.pdh.PdhGetFormattedCounterValue(handle,PDH_FMT_DOUBLE,None,ctypes.byref(v))
                if rc or v.CStatus not in (PDH_CSTATUS_VALID_DATA, PDH_CSTATUS_NEW_DATA):
                    break
                values.append(max(0.,float(v.value.doubleValue)))
            if len(values)==2:result[letter]=DiskRates(letter,*values)
        return result

    def close(self):
        if not self.closed:
            self.closed=True
            if self.query:self.pdh.PdhCloseQuery(self.query)

