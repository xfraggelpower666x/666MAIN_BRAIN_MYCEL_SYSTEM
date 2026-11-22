from types import SimpleNamespace as NS
from klrw.metrics import SystemSampler

class PS:
    def __init__(self): self.n=0
    def disk_io_counters(self): return NS(read_bytes=100+self.n*100,write_bytes=200+self.n*200)
    def net_io_counters(self): return NS(bytes_recv=300+self.n*300,bytes_sent=400+self.n*400)
    def cpu_percent(self,interval=None): return 44
    def virtual_memory(self): return NS(percent=55)

def test_rates_and_first_baseline():
    p=PS()
    times=iter([10.,12.])
    m=SystemSampler(ps=p,clock=lambda:next(times))
    assert m.sample().disk_read == 0
    p.n=1
    s=m.sample()
    assert (s.disk_read,s.disk_write,s.network_rx,s.network_tx)==(50,100,150,200)
    assert (s.cpu,s.memory)==(44,55)

def test_counter_reset_does_not_go_negative():
    p=PS(); times=iter([1.,2.])
    m=SystemSampler(ps=p,clock=lambda:next(times))
    p.n=3; m.sample(); p.n=1
    assert m.sample().disk_read == 0
