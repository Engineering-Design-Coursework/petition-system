"""Arama yardımcıları (tests/unit/test_search.py)."""


def normalize_text(text: str) -> str:
    """GÖREV T1.4

    Aramada karşılaştırma yapabilmek için metni sadeleştirir:
      1. Türkçe büyük harfleri doğru küçült: "İ" -> "i", "I" -> "ı"
         (Python'un "I".lower() sonucu "i"dir, bu yüzden önce bu ikisini elle değiştir.)
      2. Türkçe harfleri Latin karşılığına çevir: ç->c, ğ->g, ı->i, ö->o, ş->s, ü->u
         (böylece "kampus" araması "Kampüs" kelimesini bulur).
      3. Baştaki/sondaki boşlukları sil, aradaki birden çok boşluğu tek boşluk yap.

    Örnek: "  KAMPÜS   Işıkları " -> "kampus isiklari"
    """
    raise NotImplementedError


def matches_query(text: str, query: str) -> bool:
    """GÖREV T1.4

    Sorgudaki HER kelime (normalize edilmiş haliyle) metnin normalize edilmiş halinde
    geçiyorsa True döner. Kelimelerin sırası önemli değildir.
    Boş ya da sadece boşluktan oluşan sorgu her metinle eşleşir (True).
    """
    raise NotImplementedError
