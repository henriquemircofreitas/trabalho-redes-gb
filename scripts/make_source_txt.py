"""Build the ASCII message in data/source.txt from a public-domain text.

Downloads Dom Casmurro (Machado de Assis, public domain) from Project Gutenberg,
keeps the first chapters up to >= 12,500 characters (>= 100,000 message bits)
and transliterates them to 7-bit printable ASCII ("ação" -> "acao").

Run: uv run python scripts/make_source_txt.py
"""

import unicodedata
import urllib.request
from pathlib import Path

URL = "https://www.gutenberg.org/cache/epub/55752/pg55752.txt"
MIN_CHARS = 12_500
OUT = Path(__file__).resolve().parent.parent / "data" / "source.txt"

# Characters NFKD cannot reduce to ASCII; everything else non-ASCII is dropped.
PUNCTUATION = {"«": '"', "»": '"', "“": '"', "”": '"', "‘": "'", "’": "'", "—": "-", "–": "-", "…": "..."}


def to_ascii(text: str) -> str:
    text = "".join(PUNCTUATION.get(c, c) for c in text)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def main() -> None:
    raw = urllib.request.urlopen(URL).read().decode("utf-8").replace("\r\n", "\n")
    body = raw[raw.index("I\n\nDo titulo.") :]  # skip Gutenberg header and title page
    end = body.index("\n\n", MIN_CHARS)  # cut at the first paragraph break after the minimum
    text = to_ascii(body[:end]) + "\n"
    assert len(text) >= MIN_CHARS and all(c == "\n" or " " <= c <= "~" for c in text)
    OUT.write_text(text, encoding="ascii", newline="\n")
    print(f"{OUT}: {len(text)} chars = {8 * len(text)} message bits")


if __name__ == "__main__":
    main()
