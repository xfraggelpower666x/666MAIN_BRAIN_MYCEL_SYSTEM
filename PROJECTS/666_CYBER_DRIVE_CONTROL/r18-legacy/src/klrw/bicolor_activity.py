"""Cyber overlay: baseline-aware activity pulse state for one bicolor LED per drive.

Deterministic rate input, monotonic timestamps; no device writes.
Stable background activity is learned gradually and does not hold an LED forever.
"""
from dataclasses import dataclass

CYAN = "#35E0FF"
PINK = "#FF4FD8"
PURPLE = "#A855FF"
OFF = "#394354"

@dataclass
class ActivityState:
    read_baseline: float = 0.0
    write_baseline: float = 0.0
    lit_until_ms: float = 0.0
    last_qualified_ms: float = -1.0
    color: str = OFF
    initialized: bool = False

class BicolorActivity:
    """Adaptive idle baseline with minimum threshold and finite pulse hold.

    A stable sustained stream is gradually regarded as background. An above-baseline
    burst causes a short pulse; writes win if both channels are active.
    """
    def __init__(self):
        self.states: dict[str, ActivityState] = {}

    def forget_missing(self, keys):
        self.states = {k:v for k,v in self.states.items() if k in keys}

    def sample(self, key, rate, now_ms, *, threshold_bps=4096,
               burst_bps=16384, hold_ms=180, quiet_ms=300):
        st = self.states.setdefault(key, ActivityState())
        if rate is None:
            st.color=OFF
            st.lit_until_ms=0
            return OFF
        read=max(0.,float(rate.read_bps))
        write=max(0.,float(rate.write_bps))
        if not st.initialized:
            # Start from zero so the first burst is visible; baseline then tracks noise.
            st.initialized=True
        read_hit=read>threshold_bps and read>st.read_baseline+burst_bps
        write_hit=write>threshold_bps and write>st.write_baseline+burst_bps
        # A modest background smoother learns persistent activity and does not
        # accumulate without bound. It is independent for read and write.
        rate_alpha=0.08
        st.read_baseline += rate_alpha*(read-st.read_baseline)
        st.write_baseline += rate_alpha*(write-st.write_baseline)
        if read_hit or write_hit:
            new_color=PINK if write_hit else CYAN
            # Prevent a steady workload from extending the LED indefinitely:
            # only the first crossing after a quiet period triggers the pulse.
            if st.last_qualified_ms < 0 or now_ms-st.last_qualified_ms >= quiet_ms:
                st.color=new_color
                st.lit_until_ms=now_ms+hold_ms
                st.last_qualified_ms=now_ms
        if now_ms>=st.lit_until_ms:
            st.color=OFF
        return st.color
