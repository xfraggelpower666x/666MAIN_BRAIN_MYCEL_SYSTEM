import unittest
from radiostreamer.engine import crossfade_mix


class CrossfadeAudioTests(unittest.TestCase):
    def test_progress_zero_keeps_outgoing_track(self):
        a = (1000).to_bytes(2, "little", signed=True) * 8
        b = (2000).to_bytes(2, "little", signed=True) * 8
        out = crossfade_mix(a, b, 0.0)
        self.assertEqual(out, a)

    def test_progress_one_uses_incoming_track(self):
        a = (1000).to_bytes(2, "little", signed=True) * 8
        b = (2000).to_bytes(2, "little", signed=True) * 8
        out = crossfade_mix(a, b, 1.0)
        self.assertEqual(out, b)

    def test_midpoint_is_linear_blend(self):
        a = (1000).to_bytes(2, "little", signed=True) * 8
        b = (3000).to_bytes(2, "little", signed=True) * 8
        out = crossfade_mix(a, b, 0.5)
        self.assertEqual(int.from_bytes(out[:2], "little", signed=True), 2000)

    def test_progress_is_clamped(self):
        a = (1000).to_bytes(2, "little", signed=True) * 8
        b = (2000).to_bytes(2, "little", signed=True) * 8
        self.assertEqual(crossfade_mix(a, b, -1.0), a)
        self.assertEqual(crossfade_mix(a, b, 2.0), b)

    def test_mismatched_chunks_are_safely_aligned(self):
        a = (1000).to_bytes(2, "little", signed=True) * 8
        b = (2000).to_bytes(2, "little", signed=True) * 4
        self.assertEqual(len(crossfade_mix(a, b, 0.5)), len(b))


if __name__ == "__main__":
    unittest.main()
