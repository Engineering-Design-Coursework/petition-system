"""T2.3 — Paylaşım linkleri (build_share_links). Linkler çözümlenip (parse) kontrol edilir."""

from urllib.parse import parse_qs, urlsplit

import pytest

from app.domain.share import SHARE_PLATFORMS, build_share_links

URL = "https://imza.example.com/petitions/42"
TITLE = "Kampüse bisiklet yolu"


def _split(link: str) -> tuple[str, dict[str, str]]:
    """Linki 'adres' ve 'parametreler' olarak ayırır."""
    parts = urlsplit(link)
    params = {key: values[0] for key, values in parse_qs(parts.query).items()}
    return f"{parts.scheme}://{parts.netloc}{parts.path}", params


def test_should_build_a_link_for_every_platform():
    links = build_share_links(URL, TITLE)

    assert set(links) == set(SHARE_PLATFORMS)
    assert all(link.startswith("https://") for link in links.values())


@pytest.mark.parametrize(
    ("platform", "base", "expected_params"),
    [
        ("x", "https://x.com/intent/tweet", {"url": URL, "text": TITLE}),
        ("facebook", "https://www.facebook.com/sharer/sharer.php", {"u": URL}),
        ("whatsapp", "https://wa.me/", {"text": f"{TITLE} {URL}"}),
        ("linkedin", "https://www.linkedin.com/sharing/share-offsite/", {"url": URL}),
        ("telegram", "https://t.me/share/url", {"url": URL, "text": TITLE}),
    ],
)
def test_should_build_correct_link_for_platform(platform, base, expected_params):
    link = build_share_links(URL, TITLE)[platform]

    assert _split(link) == (base, expected_params)


def test_should_encode_special_characters_in_title():
    tricky_title = "Çevre & Şehir #1 ?"

    link = build_share_links(URL, tricky_title)["x"]

    # Kodlanmasaydı "&" ve "#" linki bozardı ve başlık geri okunamazdı.
    assert _split(link)[1] == {"url": URL, "text": tricky_title}
    assert " " not in link


def test_should_raise_value_error_when_url_is_empty():
    with pytest.raises(ValueError):
        build_share_links("", TITLE)
