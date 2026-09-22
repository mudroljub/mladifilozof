"""Build the Mladi filozof static site from clean UTF-8 text files.

Only .txt files directly inside /tekstovi are published. Drafts in subfolders,
such as /tekstovi/novo, are intentionally left out.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re


ROOT = Path(__file__).parent
TEXTS = ROOT / "tekstovi"
PAGES = ROOT / "stranice"
IMAGES = ROOT / "slike.json"
CONTENTS = ROOT / "sadržaj.txt"
IMAGE_DIR = ROOT / "crtezi"
DEFAULT_COVER_FILE = "mladi-filozof-medju-zgradama-crno-beli.jpg"
# The xx- prefix marks texts intentionally outside the numbered collection.
UNNUMBERED_STORY_PREFIX = "xx-"
SENTENCE_END = re.compile(r"[.!?]+(?:[”\"']|(?=\s|$))")
BOLD_OPENING_EXCEPTIONS = frozenset({"korice"})
# These stories keep their opening plain and emphasize their second sentence.

@dataclass(frozen=True)
class Story:
    slug: str
    title: str
    content: str
    order: int
    toc_number: int | None


def title_for(source: Path) -> str:
    """Derive every navigation title from the source filename alone."""
    return source.stem.removeprefix(UNNUMBERED_STORY_PREFIX).replace("-", " ")


def display_title(title: str) -> str:
    """Use one consistently capitalized form wherever a title is shown."""
    return title[:1].upper() + title[1:]


def read_contents() -> dict[str, tuple[int, int | None]]:
    """Read the intended story order from the editable contents file."""
    if not CONTENTS.is_file():
        raise SystemExit("Nedostaje sadržaj.txt.")
    contents: dict[str, tuple[int, int | None]] = {}
    toc_number = 0
    for line in CONTENTS.read_text(encoding="utf-8-sig").splitlines():
        slug = line.strip().removesuffix(".txt")
        if not slug:
            continue
        if slug.startswith("#"):
            continue
        if slug in contents:
            raise SystemExit("sadržaj.txt sadrži duplikate.")
        display_number = None
        if slug != "naslovna" and not slug.startswith(UNNUMBERED_STORY_PREFIX):
            toc_number += 1
            display_number = toc_number
        contents[slug] = (len(contents), display_number)
    return contents


def read_stories() -> list[Story]:
    contents = read_contents()
    stories: list[Story] = []
    for source in TEXTS.glob("*.txt"):
        content = source.read_text(encoding="utf-8-sig").strip()
        if not content:
            continue
        try:
            order, toc_number = contents[source.stem]
        except KeyError:
            raise SystemExit(f"Tekst nije naveden u sadržaj.txt: {source.name}")
        stories.append(Story(source.stem, title_for(source), content, order, toc_number))
    missing = set(contents) - {story.slug for story in stories}
    if missing:
        raise SystemExit(f"U sadržaj.txt ne postoji tekst: {', '.join(sorted(missing))}")
    return sorted(stories, key=lambda story: story.order)


def image_path(file_name: str) -> Path:
    """Return an image path only when it stays inside the image directory."""
    image_root = IMAGE_DIR.resolve()
    candidate = (image_root / file_name).resolve()
    if not candidate.is_relative_to(image_root):
        raise SystemExit(f"Slika mora biti unutar crtezi/: {file_name}")
    return candidate


def read_images(story_slugs: set[str]) -> dict[str, dict[str, str]]:
    """Read and validate the optional image metadata for each page."""
    if not IMAGES.exists():
        data: dict[str, dict[str, str]] = {}
    else:
        try:
            data = json.loads(IMAGES.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise SystemExit(f"Neispravan slike.json: {error.msg}")
        if not isinstance(data, dict):
            raise SystemExit("slike.json mora sadržati objekat sa stranicama.")
    unknown_stories = set(data) - story_slugs
    if unknown_stories:
        raise SystemExit(
            "Slike su navedene za nepostojeće tekstove: "
            + ", ".join(sorted(unknown_stories))
        )
    for slug, image in data.items():
        if not isinstance(image, dict) or not isinstance(image.get("file"), str):
            raise SystemExit(f"Slika za {slug} mora imati polje 'file'.")
        if not isinstance(image.get("alt"), str):
            raise SystemExit(f"Slika za {slug} mora imati polje 'alt'.")
        if not image_path(image["file"]).is_file():
            raise SystemExit(f"Slika za {slug} ne postoji: {image['file']}")
    if "naslovna" not in data and not image_path(DEFAULT_COVER_FILE).is_file():
        raise SystemExit(f"Podrazumevana naslovna slika ne postoji: {DEFAULT_COVER_FILE}")
    return data


def validate_bold_sentences(stories: list[Story]) -> None:
    """Ensure editorial emphasis rules refer to an existing sentence."""
    story_slugs = {story.slug for story in stories}
    unknown_openings = BOLD_OPENING_EXCEPTIONS - story_slugs
    if unknown_openings:
        unknown = sorted(unknown_openings)
        raise SystemExit("Izuzetak za podebljavanje nema odgovarajući tekst: " + ", ".join(unknown))
def paragraphs(text: str, *, bold_opening: bool = False) -> str:
    blocks = re.split(r"\n\s*\n", text.strip())
    rendered = []
    for index, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
        sentence_ends = list(SENTENCE_END.finditer(block))
        if bold_opening and index == 0:
            first_line_end = len(block.split("\n", 1)[0].rstrip())
            sentence_end = sentence_ends[0].end() if sentence_ends else None
            end = min(first_line_end, sentence_end) if sentence_end else first_line_end
            inline = f"<strong>{escape(block[:end])}</strong>{escape(block[end:])}"
        else:
            inline = escape(block)
        rendered.append(f"<p>{inline.replace(chr(10), '<br>')}</p>")
    return "\n".join(rendered)


def page_shell(title: str, body: str, *, page_class: str = "", og_image: str = "") -> str:
    return f"""<!doctype html>
<html lang="sr-Latn">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>{og_image}
  <link rel="stylesheet" href="{'../' if page_class else ''}css/site.css">
</head>
<body class="{page_class}">
{body}
</body>
</html>
"""


def index_page(stories: list[Story], images: dict[str, dict[str, str]]) -> str:
    entries = []
    for story in stories:
        # The cover is already the index page's opening section, so it does not
        # need a duplicate entry in the table of contents.
        if story.slug == "naslovna":
            continue
        display_number = f"{story.toc_number:02d}" if story.toc_number is not None else "—"
        entries.append(
            f"""<li>
  <span class="toc-number">{display_number}</span>
  <a href="stranice/{escape(story.slug)}.html">{escape(display_title(story.title))}</a>
</li>"""
        )
    cover = images.get("naslovna")
    cover_file = cover["file"] if cover else DEFAULT_COVER_FILE
    cover_alt = cover["alt"] if cover else ""
    body = f"""<header class="site-header">
  <a class="wordmark" href="index.html">Mladi filozof</a>
</header>
<main>
  <section class="opening" aria-labelledby="site-title">
    <div class="opening-copy">
      <h1 id="site-title">Mladi<br>Filozof</h1>
      <blockquote>„Nikada važniji poduhvat nije započet — stvaranje sebe.”</blockquote>
    </div>
    <figure class="opening-image">
      <img src="crtezi/{escape(cover_file)}" alt="{escape(cover_alt)}">
    </figure>
  </section>
  <section class="contents" id="sadrzaj" aria-labelledby="contents-title">
    <div class="contents-heading">
      <h2 id="contents-title">Sadržaj</h2>
    </div>
    <ol class="toc">
{''.join(entries)}
    </ol>
  </section>
</main>
"""
    return page_shell(
        "Mladi filozof",
        body,
        og_image=f'\n  <meta property="og:image" content="https://mudroljub.github.io/mladifilozof/crtezi/{escape(cover_file, quote=True)}">',
    )


def story_page(
    story: Story, index: int, stories: list[Story], images: dict[str, dict[str, str]]
) -> str:
    previous = stories[index - 1] if index else None
    following = stories[index + 1] if index + 1 < len(stories) else None
    navigation = []
    if previous:
        navigation.append(f'<a href="{escape(previous.slug)}.html">← {escape(display_title(previous.title))}</a>')
    else:
        navigation.append('<span></span>')
    if following:
        navigation.append(f'<a class="next" href="{escape(following.slug)}.html">{escape(display_title(following.title))} →</a>')
    else:
        navigation.append('<span></span>')
    image = images.get(story.slug)
    image_markup = ""
    if image and story.slug != "naslovna":
        image_markup = f'''    <figure class="story-image">
      <img src="../crtezi/{escape(image["file"])}" alt="{escape(image["alt"])}">
    </figure>
'''
    body = f"""<header class="site-header">
  <a class="wordmark" href="../index.html">Mladi filozof</a>
  <a class="contents-link" href="../index.html#sadrzaj">Sadržaj</a>
</header>
<main class="story-layout">
  <article>
    <div class="story-text">
{paragraphs(
    story.content,
    bold_opening=story.slug not in BOLD_OPENING_EXCEPTIONS,
)}
    </div>
{image_markup}  </article>
  <nav class="story-navigation">
    {''.join(navigation)}
  </nav>
</main>"""
    return page_shell(display_title(story.title), body, page_class="story-page")


def remove_stale_pages(current_pages: set[str]) -> list[str]:
    """Keep the build-owned pages directory aligned with current source texts."""
    removed = []
    for page in sorted(PAGES.glob("*.html")):
        if page.name in current_pages:
            continue
        if not page.is_file() and not page.is_symlink():
            raise SystemExit(f"Stara generisana stranica nije fajl: {page}")
        page.unlink()
        removed.append(page.name)
    return removed


def main() -> None:
    stories = read_stories()
    if not stories:
        raise SystemExit("Nema tekstova za objavljivanje u tekstovi/.")
    validate_bold_sentences(stories)
    images = read_images({story.slug for story in stories})
    current_pages = {f"{story.slug}.html" for story in stories}
    PAGES.mkdir(exist_ok=True)
    (ROOT / "index.html").write_text(index_page(stories, images), encoding="utf-8")
    for index, story in enumerate(stories):
        (PAGES / f"{story.slug}.html").write_text(
            story_page(story, index, stories, images), encoding="utf-8"
        )
    removed_pages = remove_stale_pages(current_pages)
    print(f"Napravljeno: index.html i {len(stories)} stranica iz {TEXTS.name}/.")
    if removed_pages:
        print(f"Uklonjene zastarele stranice: {', '.join(removed_pages)}")


if __name__ == "__main__":
    main()
