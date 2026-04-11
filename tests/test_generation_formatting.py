import unittest

from ui import format_generation_distribution


class GenerationFormattingTests(unittest.TestCase):
    def test_generation_distribution_is_formatted(self) -> None:
        text = format_generation_distribution({0: 20, 1: 6, 2: 3})
        self.assertIn("g0:20", text)
        self.assertIn("g1:6", text)
        self.assertIn("g2:3", text)

    def test_generation_distribution_truncates_with_head_and_tail(self) -> None:
        distribution = {i: 1 for i in range(12)}
        text = format_generation_distribution(distribution, max_bins=6)

        # Start of history remains visible.
        self.assertIn("g0:1", text)
        self.assertIn("g1:1", text)

        # Latest generations remain visible too.
        self.assertIn("g10:1", text)
        self.assertIn("g11:1", text)

        # Truncation marker is explicit.
        self.assertIn("...", text)
        self.assertIn("hidden", text)


if __name__ == "__main__":
    unittest.main()
