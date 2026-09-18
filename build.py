"""Build the Mladi Filozof static site from clean UTF-8 text files.

Only .txt files directly inside /tekstovi are published. Drafts in subfolders,
such as /tekstovi/novo, are intentionally left out.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).parent
TEXTS = ROOT / "tekstovi"
PAGES = ROOT / "stranice"
ASSETS = ROOT / "assets"

# Naslovi za navigaciju. Tekstovi ostaju bez metapodataka i HTML oznaka.
TITLES = {
    "00-naslovna": "Mladi Filozof",
    "01-hvala": "Hvala drvetu",
    "02-o-njemu": "O njemu",
    "03-njegova-najveca-tajna": "Njegova najveća tajna",
    "04-nije-hteo-ponovo-da-odraste": "Nije hteo ponovo da odraste",
    "05-trazi-osecanja": "Traži osećanja",
    "06-voleo-da-se-ljubi": "Voleo da se ljubi",
    "07-igrao-sa-lazi": "Igrao se sa laži",
    "08-proizvodio-moc": "Proizvodio moć",
    "09-pitao-da-li-postoji": "Pitao da li postoji",
    "10-chesto-je-moj-gost": "Često je moj gost",
    "11-susreo-duha-vremena": "Susreo duha vremena",
    "12-pronasao-gresku": "Pronašao grešku",
    "13-danas-postao-chovek": "Danas postao čovek",
    "14-bes-ga-je-savladao": "Bes ga je savladao",
    "15-trazio-ljude": "Tražio ljude",
    "16-isao-da-studira-filozofiju": "Išao da studira filozofiju",
    "17-nocas-ostao-budan": "Noćas ostao budan",
    "18-bezao-od-ljudi": "Bežao od ljudi",
    "19-pretvorio-se-u-ono-protiv-chega-se-borio": "Pretvorio se u ono protiv čega se borio",
    "20-bio-besan": "Bio besan",
    "21-postao-kamen": "Postao kamen",
    "22-povracao-bol": "Povraćao bol",
    "23-zatvorio-ochi": "Zatvorio oči",
    "24-gledao-sunce": "Gledao sunce",
    "25-tri-velike-recenice": "Tri velike rečenice",
    "26-sanjao-da-bude-slobodan": "Sanjao da bude slobodan",
    "27-ubrao-cvet": "Ubrao cvet",
    "28-zaljubljen-u-sebe": "Zaljubljen u sebe",
    "29-mesec-je-nocas-lajao": "Mesec je noćas lajao",
    "30-osecao-svet": "Osećao svet",
    "31-znao-da-su-svi-u-pravu": "Znao da su svi u pravu",
    "32-prerastao-odrastanje": "Prerastao odrastanje",
    "33-filozofovo-prorocanstvo": "Filozofovo proročanstvo",
    "34-korice": "Korice",
    "xx-mu-se-spava": "Mu se spava",
}


@dataclass(frozen=True)
class Story:
    source: Path
    slug: str
    title: str
    content: str
    order: tuple[int, int, str]


def title_for(source: Path, content: str) -> str:
    """Use the clean filename as the stable title; retain the book title on 00."""
    if source.stem in TITLES:
        return TITLES[source.stem]
    if source.stem == "00-naslovna":
        return next(line.strip() for line in content.splitlines() if line.strip())
    label = re.sub(r"^(?:\d{2}|xx)-", "", source.stem).replace("-", " ")
    return label[:1].upper() + label[1:]


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
            Story(source, source.stem, title_for(source, content), content, sort_key(source))
        )
    return sorted(stories, key=lambda story: story.order)


def paragraphs(text: str) -> str:
    blocks = re.split(r"\n\s*\n", text.strip())
    return "\n".join(
        f"<p>{escape(block.strip()).replace(chr(10), '<br>')}</p>" for block in blocks if block.strip()
    )


def page_shell(title: str, body: str, *, page_class: str = "") -> str:
    return f"""<!doctype html>
<html lang="sr-Latn">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <link rel="stylesheet" href="{'../' if page_class else ''}assets/site.css">
</head>
<body class="{page_class}">
{body}
</body>
</html>
"""


def index_page(stories: list[Story]) -> str:
    entries = []
    for story in stories:
        number = story.slug.split("-", 1)[0] if story.slug[:2].isdigit() else "—"
        entries.append(
            f"""<li>
  <span class="toc-number">{escape(number)}</span>
  <a href="stranice/{escape(story.slug)}.html">{escape(story.title)}</a>
</li>"""
        )
    body = f"""<header class="site-header">
  <a class="wordmark" href="index.html">Mladi Filozof</a>
</header>
<main>
  <section class="opening" aria-labelledby="site-title">
    <div class="opening-copy">
      <h1 id="site-title">Mladi<br>Filozof</h1>
      <blockquote>„Nikada važniji poduhvat nije započet — stvaranje sebe.”</blockquote>
    </div>
    <figure class="opening-image">
      <img src="slike/mladi-filozof-medju-zgradama-crno-beli.jpg" alt="">
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
    return page_shell("Mladi Filozof", body)


def story_page(story: Story, index: int, stories: list[Story]) -> str:
    previous = stories[index - 1] if index else None
    following = stories[index + 1] if index + 1 < len(stories) else None
    navigation = []
    if previous:
        navigation.append(f'<a href="{escape(previous.slug)}.html">← {escape(previous.title)}</a>')
    else:
        navigation.append('<span></span>')
    if following:
        navigation.append(f'<a class="next" href="{escape(following.slug)}.html">{escape(following.title)} →</a>')
    else:
        navigation.append('<span></span>')
    number = story.slug.split("-", 1)[0]
    body = f"""<header class="site-header">
  <a class="wordmark" href="../index.html">Mladi Filozof</a>
  <a class="contents-link" href="../index.html#sadrzaj">Sadržaj</a>
</header>
<main class="story-layout">
  <article>
    <p class="section-label">{escape(number)}</p>
    <h1>{escape(story.title)}</h1>
    <div class="story-text">
{paragraphs(story.content)}
    </div>
  </article>
  <nav class="story-navigation">
    {''.join(navigation)}
  </nav>
</main>"""
    return page_shell(story.title, body, page_class="story-page")


def write_styles() -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "site.css").write_text("""@charset "UTF-8";
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
.site-header { width: min(1200px, calc(100% - 3rem)); margin: 0 auto; min-height: 5rem; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--line); font: .75rem/1 var(--sans); letter-spacing: .03em; }
.wordmark { text-decoration: none; font: 600 1rem/1 var(--sans); letter-spacing: -.03em; }
.contents-link { text-underline-offset: .3em; }
.opening { width: min(1200px, calc(100% - 3rem)); margin: 0 auto; min-height: min(730px, calc(100vh - 5rem)); display: grid; grid-template-columns: minmax(0, .92fr) minmax(340px, 1.08fr); align-items: center; gap: clamp(3rem, 8vw, 9rem); padding: clamp(4rem, 10vh, 8rem) 0; }
.opening-copy { max-width: 34rem; }
.opening-kicker, .section-label { margin: 0 0 1.15rem; color: var(--water); font: 600 .72rem/1 var(--sans); letter-spacing: .09em; text-transform: uppercase; }
h1, h2 { font-weight: 400; }
.opening h1 { margin: 0; font-size: clamp(4.5rem, 10vw, 8.5rem); line-height: .82; letter-spacing: -.075em; }
blockquote { max-width: 26rem; margin: 3rem 0 0; padding-left: 1.25rem; border-left: 2px solid var(--water); font-size: clamp(1.12rem, 2vw, 1.4rem); line-height: 1.55; }
.begin-link { display: inline-block; margin-top: 2.4rem; font: 600 .83rem/1 var(--sans); }
.opening-image { margin: 0; align-self: stretch; min-height: 28rem; background: var(--night); }
.opening-image img { width: 100%; height: 100%; display: block; object-fit: cover; mix-blend-mode: screen; opacity: .86; }
.contents { width: min(1000px, calc(100% - 3rem)); margin: 0 auto; padding: 7rem 0 6rem; }
.contents-heading { display: flex; justify-content: space-between; gap: 2rem; align-items: baseline; border-bottom: 2px solid var(--ink); padding-bottom: 1.1rem; }
.contents h2 { margin: 0; font-size: clamp(1.5rem, 3vw, 2.4rem); letter-spacing: -.04em; }
.toc { max-width: 42rem; list-style: none; margin: 0; padding: 0; }
.toc li { break-inside: avoid; display: grid; grid-template-columns: 2.75rem 1fr; gap: .6rem; padding: 1rem 0 .9rem; border-bottom: 1px solid var(--line); font-size: 1.16rem; line-height: 1.25; }
.toc-number { color: var(--muted); font: .72rem/1.8 var(--sans); }
footer { width: min(1200px, calc(100% - 3rem)); margin: 0 auto; padding: 1.6rem 0 2.5rem; border-top: 1px solid var(--line); color: var(--muted); font-size: .94rem; }
.story-layout { width: min(760px, calc(100% - 3rem)); margin: 0 auto; padding: clamp(5rem, 12vh, 10rem) 0 4rem; }
.story-layout article { max-width: 40rem; }
.story-layout h1 { margin: 0 0 3rem; font-size: clamp(2.8rem, 6vw, 5.2rem); line-height: .94; letter-spacing: -.06em; }
.story-text { font-size: clamp(1.15rem, 2vw, 1.32rem); line-height: 1.78; }
.story-text p { margin: 0 0 1.65em; }
.story-navigation { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 5rem; padding-top: 1.3rem; border-top: 1px solid var(--line); font: .78rem/1.45 var(--sans); }
.story-navigation .next { text-align: right; }
@media (max-width: 700px) {
  .site-header, .opening, .contents, footer, .story-layout { width: min(100% - 2rem, 760px); }
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
    if not stories:
        raise SystemExit("Nema tekstova za objavljivanje u tekstovi/.")
    PAGES.mkdir(exist_ok=True)
    write_styles()
    (ROOT / "index.html").write_text(index_page(stories), encoding="utf-8")
    for index, story in enumerate(stories):
        (PAGES / f"{story.slug}.html").write_text(
            story_page(story, index, stories), encoding="utf-8"
        )
    print(f"Napravljeno: index.html i {len(stories)} stranica iz {TEXTS.name}/.")


if __name__ == "__main__":
    main()
