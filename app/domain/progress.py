"""İlerleme çubuğu hesapları (tests/unit/test_progress.py)."""


def progress_percent(count: int, goal: int) -> int:
    """GÖREV T1.3

    İmza sayısının hedefe oranını 0–100 arası TAM SAYI yüzde olarak döner.
      - Aşağı yuvarlanır: 999 / 1000 -> 99 (hedefe ulaşmadan 100 görünmemeli).
      - Hedef aşılsa bile en fazla 100 döner.
      - count < 0 ya da goal <= 0 ise ValueError fırlatır.
    """
    raise NotImplementedError


def is_goal_reached(count: int, goal: int) -> bool:
    """GÖREV T1.3 — imza sayısı hedefe eşit ya da büyükse True."""
    raise NotImplementedError
