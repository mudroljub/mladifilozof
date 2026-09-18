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
CSS = ROOT / "css"
IMAGES = ROOT / "slike.json"
BOLD_OPENING_EXCEPTIONS = frozenset({"34-korice"})

@dataclass(frozen=True)
class Story:
    source: Path
    slug: str
    title: str
    content: str
    order: tuple[int, int, str]


def title_for(source: Path) -> str:
    """Derive every navigation title from the source filename alone."""
    return re.sub(r"^(?:\d{2}|xx)-", "", source.stem).replace("-", " ")


def display_title(title: str) -> str:
    """Use one consistently capitalized form wherever a title is shown."""
    return title[:1].upper() + title[1:]


def sort_key(source: Path) -> tuple[int, int, str]:
    prefix = source.stem.split("-", 1)[0]
    if prefix.isdigit():
        return (0, int(prefix), source.name)
    if prefix == "xx":
        return (2, 0, source.name)
    return (1, 0, source.name)


def read_stories() -> list[Story]:
    stories = []
    for source in TEXTS.glob("*.txt"):
        content = source.read_text(encoding="utf-8-sig").strip()
        if not content:
            continue
        stories.append(
            Story(source, source.stem, title_for(source), content, sort_key(source))
        )
    return sorted(stories, key=lambda story: story.order)


def read_images() -> dict[str, dict[str, str]]:
    """Read and validate the optional image metadata for each page."""
    if not IMAGES.exists():
        return {}
    data = json.loads(IMAGES.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("slike.json mora sadržati objekat sa stranicama.")
    for slug, image in data.items():
        if not isinstance(image, dict) or not isinstance(image.get("file"), str):
            raise SystemExit(f"Slika za {slug} mora imati polje 'file'.")
        if not isinstance(image.get("alt"), str):
            raise SystemExit(f"Slika za {slug} mora imati polje 'alt'.")
        if not (ROOT / "slike" / image["file"]).is_file():
            raise SystemExit(f"Slika za {slug} ne postoji: {image['file']}")
    return data


def paragraphs(text: str, *, bold_opening: bool = False) -> str:
    blocks = re.split(r"\n\s*\n", text.strip())
    rendered = []
    for index, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
        if bold_opening and index == 0:
            first_line_end = len(block.split("\n", 1)[0].rstrip())
            sentence_end = re.search(r"[.!?](?:[”\"']|(?=\s|$))", block)
            sentence_end = sentence_end.end() if sentence_end else None
            end = min(
                first_line_end,
                sentence_end,
            ) if sentence_end else first_line_end
            inline = f"<strong>{escape(block[:end])}</strong>{escape(block[end:])}"
        else:
            inline = escape(block)
        rendered.append(f"<p>{inline.replace(chr(10), '<br>')}</p>")
    return "\n".join(rendered)


def page_shell(title: str, body: str, *, page_class: str = "") -> str:
    return f"""<!doctype html>
<html lang="sr-Latn">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
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
        if story.slug == "00-naslovna":
            continue
        entries.append(
            f"""<li>
  <span class="toc-number">{escape(story.slug.split('-', 1)[0] if story.slug[:2].isdigit() else '—')}</span>
  <a href="stranice/{escape(story.slug)}.html">{escape(display_title(story.title))}</a>
</li>"""
        )
    cover = images.get("00-naslovna")
    cover_file = cover["file"] if cover else "mladi-filozof-medju-zgradama-crno-beli.jpg"
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
      <img src="slike/{escape(cover_file)}" alt="{escape(cover_alt)}">
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
    return page_shell("Mladi filozof", body)


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
    if image and story.slug != "00-naslovna":
        image_markup = f'''    <figure class="story-image">
      <img src="../slike/{escape(image["file"])}" alt="{escape(image["alt"])}">
    </figure>
'''
    body = f"""<header class="site-header">
  <a class="wordmark" href="../index.html">Mladi filozof</a>
  <a class="contents-link" href="../index.html#sadrzaj">Sadržaj</a>
</header>
<main class="story-layout">
  <article>
    <div class="story-text">
{paragraphs(story.content, bold_opening=story.slug not in BOLD_OPENING_EXCEPTIONS)}
    </div>
{image_markup}  </article>
  <nav class="story-navigation">
    {''.join(navigation)}
  </nav>
</main>"""
    return page_shell(display_title(story.title), body, page_class="story-page")


def write_styles() -> None:
    CSS.mkdir(exist_ok=True)
    (CSS / "site.css").write_text("""@charset "UTF-8";
:root {
  --paper: #f1f3ef;
  --ink: #16242d;
  --muted: #66747b;
  --line: #b8c6c6;
  --water: #496f7a;
  --night: #1d3944;
  --serif: Iowan Old Style, Palatino Linotype, Book Antiqua, Georgia, serif;
  --sans: Avenir Next, Avenir, Segoe UI, sans-serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; color: var(--ink); background: var(--paper); font-family: var(--serif); }
a { color: inherit; text-decoration-thickness: 1px; text-underline-offset: .16em; }
a:hover { color: var(--water); }
a:focus-visible { outline: 3px solid var(--water); outline-offset: 4px; }
.index-layout { width: min(1000px, calc(100% - 3rem)); margin: 0 auto; padding: clamp(4rem, 12vh, 9rem) 0 6rem; }
.index-intro { max-width: 42rem; margin-bottom: clamp(3rem, 8vh, 6rem); padding-bottom: 2.5rem; border-bottom: 2px solid var(--ink); }
.index-intro p { margin: 0; }
.index-intro p:first-child { font-size: clamp(3.5rem, 9vw, 7rem); line-height: .85; letter-spacing: -.07em; }
.index-intro p + p { max-width: 28rem; margin-top: 2.75rem; padding-left: 1.25rem; border-left: 2px solid var(--water); font-size: clamp(1.12rem, 2vw, 1.4rem); line-height: 1.55; }
.site-header { width: min(1200px, calc(100% - 3rem)); margin: 0 auto; min-height: 5rem; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--line); font: .75rem/1 var(--sans); letter-spacing: .03em; }
.story-page .site-header { width: min(760px, calc(100% - 3rem)); }
.wordmark { text-decoration: none; font: 600 1rem/1 var(--sans); letter-spacing: -.03em; }
.contents-link { text-underline-offset: .3em; }
.opening { width: min(1200px, calc(100% - 3rem)); margin: 0 auto; min-height: min(730px, calc(100vh - 5rem)); display: grid; grid-template-columns: minmax(0, .92fr) minmax(340px, 1.08fr); align-items: center; gap: clamp(3rem, 8vw, 9rem); padding: clamp(4rem, 10vh, 8rem) 0; }
.opening-copy { max-width: 34rem; }
h1, h2 { font-weight: 400; }
.opening h1 { margin: 0; font-size: clamp(4.5rem, 10vw, 8.5rem); line-height: .82; letter-spacing: -.075em; }
blockquote { max-width: 26rem; margin: 3rem 0 0; padding-left: 1.25rem; border-left: 2px solid var(--water); font-size: clamp(1.12rem, 2vw, 1.4rem); line-height: 1.55; }
.begin-link { display: inline-block; margin-top: 2.4rem; font: 600 .83rem/1 var(--sans); }
.opening-image { margin: 0; align-self: stretch; min-height: 28rem; background: var(--night); }
.opening-image img { width: 100%; height: 100%; display: block; object-fit: contain; mix-blend-mode: screen; opacity: .86; }
.contents { width: min(1000px, calc(100% - 3rem)); margin: 0 auto; padding: 7rem 0 6rem; }
.contents-heading { display: flex; justify-content: space-between; gap: 2rem; align-items: baseline; border-bottom: 2px solid var(--ink); padding-bottom: 1.1rem; }
.contents h2 { margin: 0; font-size: clamp(1.5rem, 3vw, 2.4rem); letter-spacing: -.04em; }
.toc { max-width: 42rem; list-style: none; margin: 0; padding: 0; }
.toc li { break-inside: avoid; display: grid; grid-template-columns: 2.75rem 1fr; gap: .6rem; padding: 1rem 0 .9rem; border-bottom: 1px solid var(--line); font-size: 1.16rem; line-height: 1.25; }
.toc-number { color: var(--muted); font: .72rem/1.8 var(--sans); }
footer { width: min(1200px, calc(100% - 3rem)); margin: 0 auto; padding: 1.6rem 0 2.5rem; border-top: 1px solid var(--line); color: var(--muted); font-size: .94rem; }
.story-layout { width: min(760px, calc(100% - 3rem)); min-height: calc(100vh - 5rem); margin: 0 auto; padding: clamp(5rem, 12vh, 10rem) 0 4rem; display: flex; flex-direction: column; }
.story-layout article { max-width: 40rem; margin-bottom: 5rem; }
.story-image { margin: 4rem 0 3rem; }
.story-image img { display: block; width: 100%; height: auto; }
.story-layout h1 { margin: 0 0 3rem; font-size: clamp(2.8rem, 6vw, 5.2rem); line-height: .94; letter-spacing: -.06em; }
.story-text { font-size: clamp(1.15rem, 2vw, 1.32rem); line-height: 1.78; }
.story-text p { margin: 0 0 1.65em; }
.story-navigation { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: auto; padding-top: 1.3rem; border-top: 1px solid var(--line); font: .78rem/1.45 var(--sans); }
.story-navigation .next { text-align: right; }
@media (max-width: 700px) {
  .index-layout, .site-header, .opening, .contents, footer, .story-layout { width: min(100% - 2rem, 760px); }
  .index-layout { padding-top: 4rem; }
  .opening { grid-template-columns: 1fr; gap: 3rem; min-height: auto; padding: 4rem 0; }
  .opening-image { min-height: 17rem; order: -1; }
  .opening h1 { font-size: clamp(4.5rem, 22vw, 7rem); }
  .contents { padding: 4rem 0; }
  .contents-heading { display: block; }
  .contents h2 { margin-top: .3rem; }
  .story-layout { padding-top: 4rem; }
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
""", encoding="utf-8")


def main() -> None:
    stories = read_stories()
    images = read_images()
    if not stories:
        raise SystemExit("Nema tekstova za objavljivanje u tekstovi/.")
    PAGES.mkdir(exist_ok=True)
    write_styles()
    (ROOT / "index.html").write_text(index_page(stories, images), encoding="utf-8")
    for index, story in enumerate(stories):
        (PAGES / f"{story.slug}.html").write_text(
            story_page(story, index, stories, images), encoding="utf-8"
        )
    print(f"Napravljeno: index.html i {len(stories)} stranica iz {TEXTS.name}/.")


if __name__ == "__main__":
    main()
