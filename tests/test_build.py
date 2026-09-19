from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import build


class ParagraphTests(unittest.TestCase):
    def test_second_sentence_can_be_bolded(self) -> None:
        rendered = build.paragraphs("Prva rečenica. Druga rečenica.", bold_sentence=2)

        self.assertEqual(
            rendered,
            "<p>Prva rečenica. <strong>Druga rečenica.</strong></p>",
        )

    def test_second_sentence_exceptions_have_two_sentences(self) -> None:
        build.validate_bold_sentences(build.read_stories())

class ContentsTests(unittest.TestCase):
    def test_contents_numbers_only_non_xx_stories(self) -> None:
        all_stories = build.read_stories()
        stories = {story.slug: story for story in all_stories}
        numbered = [
            story.toc_number
            for story in all_stories
            if story.slug != "naslovna" and not story.slug.startswith(build.UNNUMBERED_STORY_PREFIX)
        ]
        unnumbered = [
            story.toc_number
            for story in all_stories
            if story.slug.startswith(build.UNNUMBERED_STORY_PREFIX)
        ]

        self.assertEqual(stories["mladi-filozof-je-znao-da-su-svi-u-pravu"].toc_number, 34)
        self.assertEqual(stories["mladi-filozof-je-prerastao-odrastanje"].toc_number, 35)
        self.assertEqual(numbered, list(range(1, len(numbered) + 1)))
        self.assertTrue(all(number is None for number in unnumbered))

    def test_xx_story_does_not_consume_a_number(self) -> None:
        original_contents = build.CONTENTS
        try:
            with TemporaryDirectory() as directory:
                build.CONTENTS = Path(directory) / "sadržaj.txt"
                build.CONTENTS.write_text(
                    "naslovna\nprva\nxx-dodatak\ndruga\n", encoding="utf-8"
                )

                contents = build.read_contents()

                self.assertIsNone(contents["naslovna"][1])
                self.assertEqual(contents["prva"][1], 1)
                self.assertIsNone(contents["xx-dodatak"][1])
                self.assertEqual(contents["druga"][1], 2)
        finally:
            build.CONTENTS = original_contents


class StalePageCleanupTests(unittest.TestCase):
    def test_pages_without_a_current_source_are_removed(self) -> None:
        original_pages = build.PAGES
        try:
            with TemporaryDirectory() as directory:
                build.PAGES = Path(directory)
                stale = build.PAGES / "old.html"
                current = build.PAGES / "current.html"
                asset = build.PAGES / "notes.txt"
                stale.write_text("stale", encoding="utf-8")
                current.write_text("current", encoding="utf-8")
                asset.write_text("not a page", encoding="utf-8")

                removed = build.remove_stale_pages({"current.html"})

                self.assertEqual(removed, ["old.html"])
                self.assertFalse(stale.exists())
                self.assertTrue(current.exists())
                self.assertTrue(asset.exists())
        finally:
            build.PAGES = original_pages


class ImageValidationTests(unittest.TestCase):
    def test_image_path_cannot_escape_image_directory(self) -> None:
        original_images = build.IMAGES
        original_image_dir = build.IMAGE_DIR
        try:
            with TemporaryDirectory() as directory:
                root = Path(directory)
                build.IMAGE_DIR = root / "crtezi"
                build.IMAGE_DIR.mkdir()
                build.IMAGES = root / "slike.json"
                build.IMAGES.write_text(
                    json.dumps({"tekst": {"file": "../outside.jpg", "alt": "Slika"}}),
                    encoding="utf-8",
                )

                with self.assertRaises(SystemExit):
                    build.read_images({"tekst"})
        finally:
            build.IMAGES = original_images
            build.IMAGE_DIR = original_image_dir


if __name__ == "__main__":
    unittest.main()
