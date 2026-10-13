"""T1.4 — Türkçe arama (normalize_text, matches_query)."""

import pytest

from app.domain.search import matches_query, normalize_text

# GÖREV T1.4 — kodu yazınca BU SATIRI SİL:
pytestmark = pytest.mark.xfail(strict=True, reason="T1.4 henüz yapılmadı")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Bisiklet Yolu", "bisiklet yolu"),
        ("Kampüs", "kampus"),
        ("İSTANBUL", "istanbul"),
        ("IŞIK", "isik"),
        ("ılık", "ilik"),
        ("ÇĞÖŞÜ çğöşü", "cgosu cgosu"),
        ("  çok   fazla    boşluk  ", "cok fazla bosluk"),
        ("", ""),
    ],
)
def test_should_normalize_turkish_text(text, expected):
    assert normalize_text(text) == expected


TEXT = "Kampüse bisiklet yolu yapılsın"


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        pytest.param("kampus", True, id="turkce-karaktersiz-yazim"),
        pytest.param("BİSİKLET", True, id="buyuk-harf"),
        pytest.param("yolu kampüse", True, id="sira-onemsiz"),
        pytest.param("bisik", True, id="kelime-parcasi"),
        pytest.param("otobüs", False, id="gecmeyen-kelime"),
        pytest.param("bisiklet otobüs", False, id="kelimelerden-biri-yok"),
        pytest.param("", True, id="bos-sorgu"),
        pytest.param("   ", True, id="sadece-bosluk"),
    ],
)
def test_should_match_when_every_query_word_appears(query, expected):
    assert matches_query(TEXT, query) is expected
