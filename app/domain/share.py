"""Sosyal medya paylaşım linkleri (tests/unit/test_share.py)."""

from urllib.parse import urlencode

SHARE_PLATFORMS = ("x", "facebook", "whatsapp", "linkedin", "telegram")


def build_share_links(url: str, title: str) -> dict[str, str]:
    """Kampanya için sosyal medya paylaşım linkleri oluşturur."""
    if not url:
        raise ValueError("Kampanya URL'si boş olamaz.")

    x_query = urlencode({"url": url, "text": title})
    facebook_query = urlencode({"u": url})
    whatsapp_query = urlencode({"text": f"{title} {url}"})
    linkedin_query = urlencode({"url": url})
    telegram_query = urlencode({"url": url, "text": title})

    return {
        "x": f"https://x.com/intent/tweet?{x_query}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?{facebook_query}",
        "whatsapp": f"https://wa.me/?{whatsapp_query}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?{linkedin_query}",
        "telegram": f"https://t.me/share/url?{telegram_query}",
    }
