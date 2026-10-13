# Test Stratejisi

**Son güncelleme:** 13 Ekim 2026

Bu belge CEN315 *Introduction to Test Engineering* dersinin 1–4. hafta konularının projeye nasıl uygulandığını anlatır.
Raporun "Project Materials" bölümündeki test anlatımının kaynağıdır.

## 1. Amaç, doğrulama (verification) ve geçerleme (validation)

- **Verification — "ürünü doğru mu yapıyoruz?"**: kodun bu belgedeki sözleşmeye ve gereksinimlere uyması.
  Araçları: birim + entegrasyon testleri, ruff (statik analiz), PR'da kod incelemesi, CI.
- **Validation — "doğru ürünü mü yapıyoruz?"**: platformun gerçekten işe yaraması.
  Araçları: hocanın ara rapor geri bildirimi, Faz 4'te sınıf arkadaşlarıyla kabul testi (UAT).
- **QA** (süreç): TDD, CI'da kalite kapıları, PR kuralı. **QC** (ürün): testlerin ve incelemelerin sonuçları.

## 2. Gereksinimler

Her gereksinim test edilebilir (ölçülebilir) yazıldı — *testability review* (Hafta 1).

| ID | Gereksinim | Test |
|---|---|---|
| FR-1 | Giriş yapmış kullanıcı başlık (10–150), açıklama (50–5000), hedef (10–1.000.000) ile kampanya açar | T1.2, T1.6, T1.7 |
| FR-2 | Kampanyalar en yeniden eskiye listelenir | T1.5, T1.7 |
| FR-3 | Başlık/açıklamada Türkçe karakterden bağımsız arama yapılır ("kampus" → "Kampüs") | T1.4, T1.5, T1.7 |
| FR-4 | Kampanya sayfası başlık, açıklama, imza sayısı, ilerleme çubuğu, paylaşım linklerini gösterir | T1.7, T2.5 |
| FR-5 | Kullanıcı e-posta (doğrulama e-postası ile) ya da telefon (SMS kodu ile) ile giriş yapar | T2.4, T2.7 |
| FR-6 | Yalnızca e-postası **veya** telefonu doğrulanmış kullanıcı imza atabilir | T1.1, T2.1, T2.5 |
| FR-7 | Bir kullanıcı bir kampanyayı en fazla bir kez imzalar (eşzamanlı isteklerde bile) | T1.5, T2.2, T2.5, T2.6 |
| FR-8 | İlerleme yüzdesi aşağı yuvarlanır, %100'ü geçmez; sayfa yenilenmeden ≤ 5 sn'de güncellenir | T1.3, T2.5 |
| FR-9 | X, Facebook, WhatsApp, LinkedIn, Telegram paylaşım linkleri ve Open Graph etiketleri üretilir | T2.3, T1.7, T2.5 |
| FR-10 | Kampanya sahibi kampanyayı imzaya kapatabilir | T3.1 (Faz 3) |
| NFR-1 | Güvenlik: kimlik yalnızca sunucuda doğrulanmış Firebase token'ından gelir; kullanıcı içeriği HTML olarak kaçışlanır (XSS); girişten sonra yalnızca site içi adrese dönülür | T2.4, T1.7 (XSS), `test_infrastructure.py` |
| NFR-2 | Kullanılabilirlik: sayfalar 360 px genişlikte (telefon) düzgün görünür; arayüz Türkçe | T1.8 (elle), UAT |
| NFR-3 | Performans: sayfalar yerelde < 500 ms yanıt verir | Faz 3 ölçüm |
| NFR-4 | Sürdürülebilirlik: domain + services branch coverage ≥ %85 | T3.2 |

## 3. Kalite öncelikleri (ISO/IEC 25010)

| Karakteristik | Öncelik | Neden / nasıl |
|---|---|---|
| Functional suitability | Yüksek | Tüm FR'ler otomatik testli |
| Security | Yüksek | Mükerrer imza ve kimlik taklidi projenin ana riski; karar tablosu, mock'lu token testleri, XSS testi |
| Reliability | Orta | İmza sayacı transaction ile; yarış durumu testi |
| Usability | Orta | Basit formlar, Türkçe hata mesajları, mobil uyum; UAT |
| Maintainability | Orta | Katmanlı mimari, bağımlılık enjeksiyonu, ruff, coverage |
| Performance efficiency | Düşük | Küçük ölçek; 5 sn'lik yoklama yeterli |
| Portability | Düşük | README ile Windows/macOS/Linux kurulum |

## 4. Sözleşme: hangi dosyada ne var

Testler bu adları `import` eder; kod bu adlarla yazılmak zorundadır. Sözleşme değişirse önce bu tablo ve testler güncellenir.

| Dosya | Sınıf / fonksiyon | Görevi | Görev |
|---|---|---|---|
| `app/domain/models.py` | `User` (+ `is_verified`), `Petition`, `Signature`, `PetitionStatus` | veri yapıları | T1.1 |
| `app/domain/errors.py` | `PetitionNotFoundError`, `AlreadySignedError`, `ValidationError(errors)`, `NotEligibleError(reason)` | hata türleri | hazır |
| `app/domain/validation.py` | `validate_petition_input(title, description, goal) -> dict[str, str]` | form kuralları | T1.2 |
| `app/domain/progress.py` | `progress_percent(count, goal) -> int`, `is_goal_reached(count, goal) -> bool` | ilerleme | T1.3 |
| `app/domain/search.py` | `normalize_text(text) -> str`, `matches_query(text, query) -> bool` | Türkçe arama | T1.4 |
| `app/domain/eligibility.py` | `check_can_sign(user, petition, already_signed) -> SignDecision`, `SignBlockReason` | imza kuralı | T2.1 |
| `app/domain/share.py` | `build_share_links(url, title) -> dict[str, str]`, `SHARE_PLATFORMS` | paylaşım | T2.3 |
| `app/repositories/base.py` | `PetitionRepository` (Protocol): `add_petition`, `get_petition`, `list_recent`, `search`, `add_signature`, `has_signed` | veritabanı arayüzü | hazır |
| `app/repositories/memory.py` | `InMemoryPetitionRepository` | Fake veritabanı | T1.5 |
| `app/repositories/firestore.py` | `FirestorePetitionRepository(client)` | gerçek veritabanı | T2.6 |
| `app/services/petition_service.py` | `PetitionService(repo, clock)`: `create`, `get`, `list_recent`, `search` | kampanya iş mantığı | T1.6 |
| `app/services/signature_service.py` | `SignatureService(repo, clock)`: `sign(user, petition_id) -> int` | imza iş mantığı | T2.2 |
| `app/auth/verifier.py` | `TokenVerifier` (Protocol), `StubTokenVerifier`, `FirebaseTokenVerifier(verify_fn)`, `InvalidTokenError` | token → kullanıcı | T2.4 |
| `app/clock.py` | `Clock` (Protocol), `SystemClock`, `FixedClock` | saat | hazır |
| `app/routes/pages.py` | `GET /`, `/health`, `/petitions`, `/petitions/new`, `POST /petitions`, `/petitions/{id}`, `/petitions/{id}/progress`, `POST /petitions/{id}/sign`, `/search?q=` | sayfalar | T1.7, T2.5 |
| `app/routes/auth.py` | `GET /login`, `POST /session` (form ya da JSON), `POST /logout` | giriş/çıkış | hazır |

## 5. Test seviyeleri ve piramit (Hafta 1–2)

| Seviye | Klasör | Araç | Şu anki sayı | Hedef oran |
|---|---|---|---|---|
| Birim (unit) | `tests/unit/` | pytest | 138 | ~%70 |
| Entegrasyon (API/sayfa) | `tests/integration/` | FastAPI TestClient | 38 | ~%20 |
| Sistem / E2E | `tests/e2e/` | Playwright (Faz 3) | 0 | ~%10 |
| Kabul (UAT) | — | sınıf arkadaşları + kabul kriterleri (Faz 4) | — | — |

Birim testleri hem **black-box** (EP/BVA, spesifikasyondan) hem **white-box** (karar dalları, döngü kapsamı) tasarlandı.

## 6. Test tasarım teknikleri (Hafta 1, 4)

### 6.1 Denklik sınıfları (EP) ve sınır değerler (BVA) — `validate_petition_input`
| Alan | Geçersiz (alt) | Geçerli | Geçersiz (üst) | BVA değerleri |
|---|---|---|---|---|
| Başlık uzunluğu | < 10, sadece boşluk | 10–150 | > 150 | 0, 9, 10, 11, 149, 150, 151 |
| Açıklama uzunluğu | < 50 | 50–5000 | > 5000 | 49, 50, 51, 4999, 5000, 5001 |
| Hedef | ≤ 9 (negatif, 0) | 10–1.000.000 | > 1.000.000 | -5, 0, 9, 10, 11, 999.999, 1.000.000, 1.000.001 |
Uzunluk boşluklar kırpıldıktan sonra ölçülür (ek sınıf: kenarında boşluk olan girdiler).

### 6.2 BVA — `progress_percent`
0, 1, hedefin hemen altı (99/100, 999/1000 → 99: hedefe ulaşmadan %100 görünmemeli), tam hedef, hedefin üstü
(üst sınır %100), aşağı yuvarlama (2/3 → 66), geçersiz girdiler (negatif sayı, hedef ≤ 0 → `ValueError`).
`<` ile `<=` karışması gibi **decision mutasyonlarını** öldürmek için özellikle seçildi.

### 6.3 Karar tablosu — `check_can_sign`
| Kural | Giriş | Kampanya | Doğrulanmış | Önceden imzalamış | Sonuç |
|---|---|---|---|---|---|
| R1 | hayır | - | - | - | NOT_LOGGED_IN |
| R2 | evet | kapalı | - | - | PETITION_CLOSED |
| R3 | evet | açık | hayır | - | NOT_VERIFIED |
| R4 | evet | açık | evet | evet | ALREADY_SIGNED |
| R5 | evet | açık | evet | hayır | izin |
Öncelik testleri ("-" sütunlarının sonucu değiştirmediği) ayrı satırlarla doğrulanır.

### 6.4 Koşul / MC/DC — `User.is_verified = (email AND email_verified) OR phone`
Her koşulun sonucu tek başına değiştirdiği çiftler: (e-posta+doğrulandı ↔ doğrulanmadı), (telefon var ↔ yok),
(e-posta yokken doğrulandı bayrağı) → 6 test.

### 6.5 Döngü kapsamı — `list_recent`, `search`
0 kayıt, 1 kayıt, çok kayıt ve `limit` sınırı.

## 7. Test double'ları (Hafta 3)

| Tür | Projede | Nerede |
|---|---|---|
| Fake | `InMemoryPetitionRepository` (çalışan hafif veritabanı) | servis ve sayfa testleri |
| Stub | `StubTokenVerifier` (token → hazır kullanıcı), `FixedClock` | entegrasyon testleri |
| Mock | `Mock(return_value=claims)` yerine Firebase `verify_id_token` | `test_firebase_verifier.py` |
| Spy | `Mock(wraps=repo)` ile çağrı kaydı | `test_signature_service.py`, `test_petition_service.py` |
| Hata enjeksiyonu | `side_effect=AlreadySignedError()` ile yarış durumu | `test_signature_service.py` |

Kural: kendi modellerimizi/algoritmalarımızı mock'lamıyoruz; yalnızca dış bağımlılıkları (Firebase, saat) taklit ediyoruz.
Testlerin hiçbiri ağa çıkmaz; zaman sabit (`FixedClock`), id'ler sıralı → **flaky test yok**.

## 8. TDD ve "önce sözleşme" iş akışı (Hafta 3)

1. Claude faz başında o fazın tüm testlerini yazar; her test dosyasının başında
   `pytestmark = pytest.mark.xfail(strict=True, reason="T1.3 henüz yapılmadı")` bulunur.
2. CI yeşil kalır ama özet "25 passed, 151 xfailed" gibi ilerlemeyi gösterir; `scripts/check.py` görev tablosu basar.
3. Geliştirici işareti siler (**Red**), en basit kodu yazar (**Green**), temizler (**Refactor**).
4. `strict=True`: kod çalıştığı halde işaret silinmezse test **XPASS(strict)** ile başarısız olur → unutulamaz.
5. Testler eklenmeden önce geçici bir kopyada örnek çözümle hepsinin geçebildiği doğrulanır (bugün: 176/176).

## 9. Risk tabanlı test (Hafta 1)

RPN = Olasılık (L) × Etki (I) × Tespit zorluğu (D), 1–5 ölçeği. Yüksek RPN → daha derin test.

| # | Risk | L | I | D | RPN | Önlem / test |
|---|---|---|---|---|---|---|
| R3 | Bir kişinin e-posta ve telefonla iki ayrı hesap açıp iki kez imzalaması | 3 | 3 | 5 | 45 | **Kabul edilen kalıntı risk**; raporda belirtilir. Gelecek: hesap birleştirme |
| R2 | Sahte/süresi dolmuş token ile kimlik taklidi | 2 | 5 | 4 | 40 | Sunucuda `verify_id_token`; mock'lu hata testleri (T2.4); uid formdan alınmaz |
| R6 | Kampanya metninde XSS | 3 | 4 | 3 | 36 | Jinja2 otomatik kaçışlama + XSS testi (T1.7); `|safe` yasak |
| R4 | Eşzamanlı imzada sayaç/tekillik bozulması | 2 | 4 | 4 | 32 | Firestore transaction + belge id `{kampanya}_{uid}`; yarış testi (T2.2); emulator testi (T3.4) |
| R1 | Aynı hesapla mükerrer imza | 3 | 5 | 2 | 30 | Karar tablosu (T2.1), repo testi (T1.5), sayfa testi 409 (T2.5) |
| R9 | Gizli anahtarın repoya sızması | 2 | 5 | 3 | 30 | `.gitignore`, ortam değişkenleri, GitHub secret scanning |
| R5 | Doğrulanmamış kullanıcının imzası | 3 | 4 | 2 | 24 | MC/DC testleri (T1.1), karar tablosu (T2.1), 403 testi (T2.5) |
| R7 | Girişten sonra dış siteye yönlendirme (open redirect) | 2 | 3 | 3 | 18 | `safe_next` testleri (hazır) |
| R8 | SMS kotasının/maliyetinin aşılması | 3 | 2 | 2 | 12 | Geliştirmede Firebase test telefon numaraları |
| R10 | Ücretsiz sunucunun uykuya geçmesi (demo gecikmesi) | 5 | 2 | 1 | 10 | Sunumdan önce siteyi ısıtma |

## 10. Statik test (Hafta 1)

- **ruff**: stil + olası hatalar (pyflakes, bugbear, pyupgrade, import sırası); CI'da zorunlu.
- **Gereksinim incelemesi** (§2) ve her PR'da **kod incelemesi** (en az bir ekip üyesi).
- **GitHub secret scanning** (sızan anahtarlar), Faz 3'te **pip-audit** (bağımlılık açıkları).

## 11. CI hattı (Hafta 3)

`.github/workflows/ci.yml` — her push ve PR'da: checkout → Python 3.13 + pip önbelleği → paket kurulumu →
`ruff check` + `ruff format --check` → `pytest --cov=app --cov-branch` → görev özet tablosu (Actions özet sayfası) →
HTML coverage raporu (indirilebilir artifact). Hedef süre < 2 dk. `main` dalında "CI geçmeden merge yok" kuralı.

## 12. Kapsam (coverage) ve mutation testing (Hafta 4)

- **Branch coverage** (`pytest-cov --cov-branch`): hedef `app/domain` + `app/services` için ≥ %85 (T3.2'de CI kapısı).
  Coverage bir hedef değil gösterge olarak kullanılır (Goodhart yasası); assertion'sız test yazılmaz.
- **Mutation testing** (mutmut, Faz 3): `app/domain` üzerinde haftalık CI işi. Mutation score =
  öldürülen / (toplam − eşdeğer). Hayatta kalan mutantlar incelenip ya yeni test yazılır ya da eşdeğer olarak belgelenir.
  Not: mutmut Windows'ta doğrudan çalışmaz; CI (Linux) ya da WSL üzerinden çalıştırılır.
- Sonuçlar (yüzde, mutation score, örnek hayatta kalan mutant) final raporuna eklenir.
