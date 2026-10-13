"""Ayarlar ortam değişkenlerinden (.env dosyasından) okunur. Örnek: .env.example"""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

DEFAULT_SECRET_KEY = "dev-secret-change-me"


@dataclass(frozen=True)
class Settings:
    app_env: str = "dev"
    secret_key: str = DEFAULT_SECRET_KEY
    base_url: str = "http://127.0.0.1:8000"
    # Tarayıcıdaki Firebase SDK'sı için (Firebase Console > Proje ayarları > Web uygulaması)
    firebase_web_config: dict[str, str] = field(default_factory=dict)
    # Sunucu için servis hesabı: JSON dosyasının yolu ya da JSON metninin kendisi
    firebase_credentials: str | None = None

    @property
    def use_firebase(self) -> bool:
        return bool(self.firebase_credentials and self.firebase_web_config.get("apiKey"))


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    env = os.environ if env is None else env
    web_config = {
        "apiKey": env.get("FIREBASE_API_KEY", ""),
        "authDomain": env.get("FIREBASE_AUTH_DOMAIN", ""),
        "projectId": env.get("FIREBASE_PROJECT_ID", ""),
        "appId": env.get("FIREBASE_APP_ID", ""),
    }
    settings = Settings(
        app_env=env.get("APP_ENV", "dev"),
        secret_key=env.get("SECRET_KEY", DEFAULT_SECRET_KEY),
        base_url=env.get("BASE_URL", "http://127.0.0.1:8000").rstrip("/"),
        firebase_web_config=web_config if web_config["apiKey"] else {},
        firebase_credentials=env.get("FIREBASE_CREDENTIALS") or None,
    )
    if settings.app_env == "prod":
        if settings.secret_key == DEFAULT_SECRET_KEY:
            raise RuntimeError("APP_ENV=prod iken SECRET_KEY ayarlanmalı.")
        if not settings.use_firebase:
            raise RuntimeError("APP_ENV=prod iken Firebase ayarları zorunlu.")
    return settings
