# Mimari ve Proje Kararları (ADR)

Her karar: bağlam → karar → değerlendirilen alternatifler → sonuçlar. Yeni kararlar sona eklenir.

## ADR-1 — Backend: FastAPI + Jinja2 (13 Eki 2026)
- **Bağlam:** Ekipten biri yalnızca Python biliyor. İlk taslak Flask + Jinja2 ile yazılmıştı.
- **Karar:** FastAPI, sunucu tarafında Jinja2 ile HTML üretimi (SPA yok).
- **Alternatifler:** Flask'ta kalmak (öğrenmesi kolay ama doğrulama/test araçları daha zayıf); JS SPA (ekip JS bilmiyor).
- **Sonuç:** Jinja2 şablonları Flask'takiyle aynı; FastAPI `TestClient` entegrasyon testlerini kolaylaştırıyor; `/docs`
  otomatik API sayfası. Eski taslağın rotaları ve navbar'ı taşındı.

## ADR-2 — Anlık ilerleme çubuğu: htmx ile 5 sn yoklama (13 Eki 2026)
- **Karar:** `hx-get` + `hx-trigger="every 5s"` ile `/petitions/{id}/progress` parçası yenilenir.
- **Alternatifler:** WebSocket/SSE (sunucu karmaşıklığı), tarayıcıda Firestore dinleyicisi (JS gerektirir).
- **Sonuç:** JS yazmadan "anlık" güncelleme; parça uç noktası ayrıca test edilebilir. Gecikme ≤ 5 sn kabul edildi.

## ADR-3 — Veritabanı: Firestore + bellek içi Fake (13 Eki 2026)
- **Karar:** Üretimde Firestore; testlerde ve demo modunda `InMemoryPetitionRepository`. İkisi aynı `PetitionRepository`
  arayüzünü uygular.
- **Alternatifler:** SQLite + SQLAlchemy (ücretsiz sunucularda dosya kalıcı değil, PostgreSQL'e geçiş gerekirdi).
- **Sonuç:** Firebase tek hesapta auth + veri; testler hızlı ve ağsız. Firestore'a özgü davranış Faz 3'te emulator ile test edilecek.

## ADR-4 — Doğrulama: e-posta VEYA telefon (13 Eki 2026)
- **Karar:** Firebase Authentication; imza için doğrulanmış e-posta ya da doğrulanmış telefon yeterli.
- **Alternatifler:** İkisini birden zorunlu tutmak (SMS maliyeti, kullanıcı sürtünmesi); TC Kimlik No kontrolü
  (KVKK kapsamında hassas kişisel veri — reddedildi).
- **Sonuç:** Kalıntı risk: bir kişi e-posta ve telefonla iki hesap açabilir (TEST_STRATEGY risk R3), raporda belirtilir.

## ADR-5 — Oturum: token sunucuda doğrulanır, imzalı çerezde tutulur (13 Eki 2026)
- **Karar:** Tarayıcı Firebase ID token'ını `POST /session`'a yollar; sunucu `verify_id_token` ile doğrular ve kullanıcı
  bilgisini Starlette `SessionMiddleware` ile imzalı çereze yazar.
- **Sonuç:** Her istekte Firebase'e gitmeye gerek yok; çerez `SECRET_KEY` ile imzalı olduğundan değiştirilemez.
  E-postasını sonradan doğrulayan kullanıcı yeniden giriş yapmalı (giriş sayfası bunu yönetecek).

## ADR-6 — Mükerrer imza engeli veritabanı seviyesinde (13 Eki 2026)
- **Karar:** İmza belgesinin id'si `{petition_id}_{uid}`; ekleme ve sayaç artışı tek Firestore transaction'ında.
- **Sonuç:** Uygulama kontrolü atlansa ya da iki istek aynı anda gelse bile ikinci imza oluşamaz.

## ADR-7 — Yayın: Render (13 Eki 2026)
- **Karar:** Ücretsiz Render web service.
- **Alternatifler:** GitHub Pages yalnızca statik dosya sunar, Python çalıştıramaz. "Sadece JS + GitHub Pages +
  Firestore Security Rules" mimarisi değerlendirildi; ekibin JS öğrenmesini gerektirdiği ve iş kurallarını tarayıcıya
  taşıdığı için reddedildi.
- **Sonuç:** Ücretsiz planda uyku gecikmesi (~30 sn) var; sunumdan önce site ısıtılır.

## ADR-8 — Önce sözleşme testleri + strict xfail (13 Eki 2026)
- **Karar:** Testleri Claude kod yazılmadan önce yazar; yapılmamış görevlerin testleri `xfail(strict=True)`.
- **Sonuç:** CI her zaman yeşil kalırken ilerleme ölçülebilir; görev bitince işaretin silinmesi zorunlu. Testler örnek
  çözümle doğrulanmadan eklenmez.

## ADR-9 — Demo modu (13 Eki 2026)
- **Karar:** Firebase ayarları yoksa uygulama bellek içi veritabanı ve hazır demo kullanıcılarla çalışır.
  `APP_ENV=prod` iken Firebase ve `SECRET_KEY` zorunludur (yoksa uygulama başlamaz).
- **Sonuç:** Yeni bir bilgisayarda hiçbir hesap açmadan proje çalıştırılabilir ve geliştirilebilir.

## ADR-10 — Firebase projesine ekip erişimi (24 Eki 2026)
- **Karar:** Projeyi (`imza-kampanyasi-cen317`) tek kişi kurar, diğer üyeler Console'dan **Editör** olarak eklenir.
  Herkes kendi servis hesabı anahtarını indirir (`firebase-key.json`); anahtar paylaşılmaz. Web ayarları
  (`FIREBASE_API_KEY` vb.) gizli değildir, ekipte paylaşılabilir. Ücretsiz Spark planı, Firestore `europe-west1`,
  güvenlik kuralları production modu (yalnızca sunucu Admin SDK ile erişir).
- **Alternatifler:** Tek anahtarı herkesle paylaşmak (sızarsa kimden sızdığı bilinmez, iptal herkesi etkiler) — reddedildi.
- **Sonuç:** Anahtarlar kişi bazında iptal edilebilir. Firebase'e erişimi olmayan üye demo modunda çalışmaya devam eder.
