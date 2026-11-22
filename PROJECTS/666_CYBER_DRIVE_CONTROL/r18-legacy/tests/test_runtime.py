from klrw.runtime import Monitor
from klrw.model import Config
from klrw.metrics import Sample
from klrw.leds import PreviewBackend

class MockSampler:
    def sample(self): return Sample(80,30,0,4000,0,0)

def test_runtime_finishes_and_restores():
    results=[]
    backend=PreviewBackend()
    m=Monitor(Config(interval=.2),on_update=lambda s,l:results.append(l.copy()),sampler=MockSampler(),backend=backend)
    m.run(count=2)
    assert len(results)==2
    assert not any(backend.states.values())
    assert m.error is None

def test_runtime_thread_stop():
    backend=PreviewBackend()
    m=Monitor(Config(interval=.2),sampler=MockSampler(),backend=backend)
    m.start();m.stop()
    assert not m.worker.is_alive()
