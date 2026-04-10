import unittest

from ui import format_generation_distribution


class GenerationFormattingTests(unittest.TestCase):
    def test_generation_distribution_is_formatted(self) -> None:
        text = format_generation_distribution({0: 20, 1: 6, 2: 3})
        self.assertIn("g0:20", text)
        self.assertIn("g1:6", text)
        self.assertIn("g2:3", text)

    def test_generation_distribution_truncates_when_too_many_bins(self) -> None:
        distribution = {i: 1 for i in range(12)}
        text = format_generation_distribution(distribution, max_bins=5)
        self.assertIn("g0:1", text)
        self.assertIn("(+7 bins)", text)


if __name__ == "__main__":
    unittest.main()
