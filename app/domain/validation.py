"""Kampanya formu doğrulama kuralları (EP/BVA testleri: tests/unit/test_validation.py)."""

TITLE_MIN = 10
TITLE_MAX = 150
DESCRIPTION_MIN = 50
DESCRIPTION_MAX = 5000
GOAL_MIN = 10
GOAL_MAX = 1_000_000

"""GÖREV T1.2 — tests/unit/test_validation.py

Kuralları kontrol eder ve hataları {alan_adı: Türkçe mesaj} olarak döner.
Her şey doğruysa boş sözlük `{}` döner.

Kurallar (uzunluklar baştaki/sondaki boşluklar silindikten sonra ölçülür):
  - "title":       TITLE_MIN..TITLE_MAX karakter (sınırlar dahil)
  - "description": DESCRIPTION_MIN..DESCRIPTION_MAX karakter (sınırlar dahil)
  - "goal":        GOAL_MIN..GOAL_MAX arası tam sayı (sınırlar dahil)
"""


def validate_petition_input(title: str, description: str, goal: int) -> dict[str, str]:
    errors = {}
    if not title:
        errors["title"] = "Lütfen kampanya başlığı giriniz !"

    elif TITLE_MIN > len(title.strip()):
        errors["title"] = "Başlık en az 10 karakter olmalıdır !"
    elif len(title.strip()) > TITLE_MAX:
        errors["title"] = " Karakter sınırını aştınız !"
    if DESCRIPTION_MIN > len(description.strip()):
        errors["description"] = "Açıklama en az 50 karakter olmalıdır!"
    elif len(description.strip()) > DESCRIPTION_MAX:
        errors["description"] = "Karakter sınırını aştınız !"
    if GOAL_MIN > goal:
        errors["goal"] = "Lütfen geçerli hedef giriniz !"
    elif goal > GOAL_MAX:
        errors["goal"] = "Hedef aralığını aştınız !"
    return errors
