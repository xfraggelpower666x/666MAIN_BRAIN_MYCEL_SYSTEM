import pytest
from klrw.ledkit import LedKit, Capabilities, UnsupportedOperation


def test_default_simulation_and_facades():
    with LedKit() as kit:
        assert kit.snapshot() == {'caps': False, 'num': False, 'scroll': False}
        kit.caps.set()
        assert kit.caps.get()
        kit.caps.reset()
        assert not kit.caps.get()
        assert kit.num.toggle()
        assert not kit.num.toggle()
        assert not kit.capabilities.independent_physical_led


def test_set_many_preserves_untouched_lights():
    with LedKit() as kit:
        kit.scroll.set()
        assert kit.set_many({'num': True, 'caps': True}) == {'caps': True, 'num': True, 'scroll': True}


def test_input_validation():
    with LedKit() as kit:
        with pytest.raises(ValueError): kit.set('caps', 1)
        with pytest.raises(ValueError): kit.set('unknown', True)
        with pytest.raises(ValueError): kit.set_many({'unknown': False})
        with pytest.raises(ValueError): kit.set_many({'caps': 'yes'})


def test_read_only_capability():
    with LedKit(capabilities=Capabilities(write=False)) as kit:
        assert kit.caps.get() is False
        with pytest.raises(UnsupportedOperation): kit.caps.set()


def test_unreadable_capability():
    with LedKit(capabilities=Capabilities(read=False)) as kit:
        with pytest.raises(UnsupportedOperation): kit.snapshot()
        with pytest.raises(UnsupportedOperation): kit.num.toggle()


class FailingBackend:
    def __init__(self, fail_on, fail_restore=False):
        self.states = {'caps': False, 'num': False, 'scroll': False}
        self.fail_on = fail_on
        self.fail_restore = fail_restore
        self.was_failed = False
        self.closed = False
    def read(self, name): return self.states[name]
    def apply(self, name, state):
        if name == self.fail_on and not self.was_failed:
            self.was_failed = True
            raise OSError('write failed')
        if self.fail_restore and self.was_failed and name == 'caps' and state is False:
            raise OSError('restore failed')
        self.states[name] = state
    def close(self): self.closed = True


def test_group_rollback_on_backend_error():
    backend = FailingBackend('num')
    with LedKit(backend=backend) as kit:
        with pytest.raises(OSError): kit.set_many({'caps': True, 'num': True})
        assert kit.snapshot() == {'caps': False, 'num': False, 'scroll': False}
    assert backend.closed


def test_group_failed_recovery_is_not_hidden():
    with LedKit(backend=FailingBackend('num', fail_restore=True)) as kit:
        with pytest.raises(ExceptionGroup) as exc:
            kit.set_many({'caps': True, 'num': True})
        assert len(exc.value.exceptions) == 2


def test_close_guards_operations():
    kit = LedKit()
    kit.close()
    kit.close()
    with pytest.raises(RuntimeError): kit.caps.get()
    with pytest.raises(RuntimeError): kit.caps.set()


def test_empty_group_does_not_mutate():
    with LedKit() as kit:
        assert kit.set_many({}) == kit.snapshot()


def test_simulation_never_imports_or_uses_windows_backend():
    with LedKit() as kit:
        assert kit.hardware is False
        assert kit.capabilities.changes_functional_lock_state is False
