"""İlerleme çubuğu hesapları (tests/unit/test_progress.py)."""


def progress_percent(count: int, goal: int) -> int:
    """GÖREV T1.3

    İmza sayısının hedefe oranını 0–100 arası TAM SAYI yüzde olarak döner.
      - Aşağı yuvarlanır: 999 / 1000 -> 99 (hedefe ulaşmadan 100 görünmemeli).
      - Hedef aşılsa bile en fazla 100 döner.
      - count < 0 ya da goal <= 0 ise ValueError fırlatır.
    """
    # Geçersiz değerler
    if count < 0 or goal <= 0:
        raise ValueError("Geçersiz sayı ya da hedef")

    # Tam sayı bölme aşağı yuvarlar
    percent = count * 100 // goal

    # En fazla 100
    if percent > 100:
        return 100
    return percent


def is_goal_reached(count: int, goal: int) -> bool:
    """GÖREV T1.3 — imza sayısı hedefe eşit ya da büyükse True."""
    return count >= goal
