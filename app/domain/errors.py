"""Uygulama genelinde kullanılan hata (exception) sınıfları. Hazır, değiştirmeye gerek yok."""


class PetitionNotFoundError(Exception):
    """İstenen kampanya yok."""


class AlreadySignedError(Exception):
    """Kullanıcı bu kampanyayı zaten imzalamış (repository seviyesinde)."""


class ValidationError(Exception):
    """Form verisi kurallara uymuyor.

    `errors` sözlüğü alan adı -> hata mesajı içerir, ör. {"title": "..."}.
    """

    def __init__(self, errors: dict[str, str]):
        super().__init__(", ".join(errors.values()))
        self.errors = errors


class NotEligibleError(Exception):
    """Kullanıcı imza atamaz. `reason` bir `SignBlockReason` değeridir."""

    def __init__(self, reason):
        super().__init__(str(reason))
        self.reason = reason
