"""Read-only filesystem capacity monitoring (distinct from SSD I/O and SMART health)."""
from dataclasses import dataclass, asdict
import math
import psutil

@dataclass(frozen=True)
class Volume:
    mountpoint: str
    device: str
    filesystem: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    used_percent: float
    status: str


def severity(percent, warning=80.0, critical=95.0):
    values=(percent,warning,critical)
    if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) for v in values):
        raise ValueError("percent and thresholds must be finite numbers")
    if not 0 <= percent <= 100 or not 0 <= warning < critical <= 100:
        raise ValueError("invalid utilization or threshold range")
    return "critical" if percent >= critical else "warning" if percent >= warning else "ok"


class VolumeSampler:
    def __init__(self, ps=psutil, warning=80., critical=95., include_remote=False):
        severity(0., warning, critical)
        self.ps=ps
        self.warning=float(warning)
        self.critical=float(critical)
        self.include_remote=bool(include_remote)

    def sample(self):
        result=[]
        seen=set()
        failures={}
        for part in self.ps.disk_partitions(all=False):
            path=part.mountpoint
            if not path or path in seen:
                continue
            seen.add(path)
            if not self.include_remote and (str(part.fstype).lower() in ("nfs","cifs","smbfs","smb3") or str(part.device).startswith("\\\\")):
                continue
            try:
                usage=self.ps.disk_usage(path)
                if usage.total <= 0:
                    failures[path]="zero total bytes"
                    continue
                percent=max(0.,min(100.,100*usage.used/usage.total))
                result.append(Volume(str(path),str(part.device),str(part.fstype),int(usage.total),int(usage.used),int(usage.free),round(percent,2),severity(percent,self.warning,self.critical)))
            except (OSError,PermissionError,ValueError) as exc:
                failures[path]=type(exc).__name__
        return tuple(result), failures


def compact_free_gib(volume):
    return round(volume.free_bytes / (1024 ** 3),1)
