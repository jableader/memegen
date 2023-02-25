import unittest
from PIL import Image, ImageDraw
from app import stitch_frames


class TestStitchFrames(unittest.TestCase):
    def setUp(self):
        colors = ["red", "green", "blue", "purple"]
        self.frames = [Image.new("RGB", (100, 100), c) for c in colors]
        self.captions = ["Caption 1", "Caption 2", "Caption 3", "Caption 4"]

    def test_stitch_frames(self):
        result = stitch_frames(self.frames, self.captions)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (200, 200))
        draw = ImageDraw.Draw(result)
        for i in range(4):
            expected_text = self.captions[i]
            expected_size = (50, 20)  # The size of the text box
            expected_position = (i % 2 * 100, i // 2 * 100 + 80)  # The position of the text box
            text = draw.textsize(expected_text)
            self.assertEqual(text, expected_size)
            actual_text = draw.text((expected_position[0] + 25 - text[0] // 2, expected_position[1]), expected_text, (0, 0, 0))
            self.assertEqual(actual_text, expected_text)


if __name__ == "__main__":
    unittest.main()
