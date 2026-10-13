"""Sosyal medya paylaşım linkleri (tests/unit/test_share.py)."""

SHARE_PLATFORMS = ("x", "facebook", "whatsapp", "linkedin", "telegram")


def build_share_links(url: str, title: str) -> dict[str, str]:
    """GÖREV T2.3

    Kampanya adresi ve başlığından paylaşım linkleri üretir. Anahtarlar SHARE_PLATFORMS'tur.
    Parametre değerleri `urllib.parse.urlencode` (ya da `quote`) ile kodlanmalıdır.

      "x":        https://x.com/intent/tweet?url=<url>&text=<title>
      "facebook": https://www.facebook.com/sharer/sharer.php?u=<url>
      "whatsapp": https://wa.me/?text=<title + " " + url>
      "linkedin": https://www.linkedin.com/sharing/share-offsite/?url=<url>
      "telegram": https://t.me/share/url?url=<url>&text=<title>

    `url` boşsa ValueError fırlatır.
    """
    raise NotImplementedError
