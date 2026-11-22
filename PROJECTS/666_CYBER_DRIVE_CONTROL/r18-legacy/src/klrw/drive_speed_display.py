"""Independent drive speed presentation inspired by observed features, no foreign code."""
from __future__ import annotations

FACTORS = {'KiB/s': 1024.0, 'MiB/s': 1024.0 * 1024.0, 'MB/s': 1_000_000.0, 'bit/s': 0.125}

def format_speed(bps: float, unit: str='KiB/s', decimals: int=1) -> str:
    if unit not in FACTORS: raise ValueError('unsupported speed unit')
    if type(decimals) is not int or not 0 <= decimals <= 3: raise ValueError('invalid precision')
    return f'{max(0.0,float(bps))/FACTORS[unit]:.{decimals}f} {unit}'

def describe_rate(rate, preferences: dict, *, compact: bool=False) -> str:
    if rate is None: return 'I/O nicht verfuegbar'
    unit=preferences.get('speed_unit','KiB/s')
    decimals=preferences.get('speed_decimals',1)
    if compact:
        r=format_speed(rate.read_bps,unit,decimals).split()[0]
        w=format_speed(rate.write_bps,unit,decimals).split()[0]
        return f'R {r} / W {w} {unit}'
    return f'Lesen {format_speed(rate.read_bps,unit,decimals)} | Schreiben {format_speed(rate.write_bps,unit,decimals)}'

def active_channels(rate, threshold_bps=4096):
    if rate is None:return (False,False)
    if type(threshold_bps) is not int or threshold_bps<0:raise ValueError('invalid threshold')
    return (rate.read_bps>threshold_bps,rate.write_bps>threshold_bps)
