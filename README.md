# İmza Kampanyası Platformu

CEN317 Engineering Design dönem projesi (Çukurova Üniversitesi, Bilgisayar Mühendisliği).

Kullanıcılar toplumsal ya da kurum içi sorunlar için **imza kampanyası başlatır** ve **destek toplar**.

- **Mükerrer imza engeli:** her kampanya, doğrulanmış (e-posta ya da telefon) bir hesapla yalnızca bir kez imzalanabilir.
- **Anlık ilerleme çubuğu:** imza sayısı sayfa yenilenmeden 5 saniyede bir güncellenir.
- **Sosyal medya paylaşımı:** X, Facebook, WhatsApp, LinkedIn ve Telegram linkleri ile Open Graph etiketleri.

| Katman | Teknoloji |
|---|---|
| Sunucu | Python 3.12+, FastAPI |
| Sayfalar | Jinja2 şablonları (HTML), CSS, htmx |
| Giriş | Firebase Authentication (e-posta + telefon/SMS) |
| Veritabanı | Google Firestore (Firebase yokken bellek içi demo veritabanı) |
| Test | pytest, pytest-cov, FastAPI TestClient, ruff |
| CI | GitHub Actions |
| Yayın | Render |

Belgeler: [Proje planı](docs/PROJECT_PLAN.md) · [Test stratejisi](docs/TEST_STRATEGY.md) ·
[Mimari kararlar](docs/DECISIONS.md) · [Ara rapor](docs/report/INTERIM_REPORT.md)

---

## 1. Kurulum (yeni bir bilgisayarda)

### Gerekenler
- **Python 3.12 ya da üstü** (3.13 önerilir): https://www.python.org/downloads/
  Windows'ta kurarken **"Add python.exe to PATH"** kutusunu işaretle.
- **Git**: https://git-scm.com/downloads
- (İsteğe bağlı) PyCharm ya da VS Code

Kontrol: terminalde `python --version` ve `git --version` çalışmalı. (macOS/Linux'ta `python` yerine `python3` yazman gerekebilir.)

### Adımlar

```bash
# 1) Projeyi indir
git clone https://github.com/Engineering-Design-Coursework/petition-system.git
cd petition-system

# 2) Sanal ortam oluştur (projeye özel paket klasörü)
python -m venv .venv
```

```bash
# 3) Sanal ortamı aktif et — her yeni terminalde tekrar gerekir
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (cmd):
.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate
```

Aktif olunca satır başında `(.venv)` görünür. PowerShell "running scripts is disabled" hatası verirse bir kez şunu çalıştır:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

```bash
# 4) Paketleri kur
pip install -r requirements-dev.txt

# 5) Ayar dosyasını oluştur (Windows: copy .env.example .env)
cp .env.example .env
```

`.env` dosyasını olduğu gibi bırakırsan uygulama **demo modunda** çalışır: Firebase gerekmez, veriler bellekte tutulur
(sunucu kapanınca silinir), giriş sayfasında hazır demo kullanıcılar çıkar.

### Çalıştırma

```bash
uvicorn app.main:create_app --factory --reload
```

Tarayıcıda http://127.0.0.1:8000 adresini aç. `--reload` sayesinde kodu kaydettikçe sunucu kendini yeniler.
Durdurmak için terminalde `Ctrl + C`.

### Testleri çalıştırma

```bash
python scripts/check.py                          # her şey: stil düzeltme + statik analiz + tüm testler + görev durumu
pytest                                           # sadece testler
pytest tests/unit/test_progress.py               # tek bir dosya
pytest --cov=app --cov-branch --cov-report=html  # kapsam (coverage) raporu -> htmlcov/index.html
```

---

## 2. Elle geliştirme rehberi (Claude kullanmadan)

Bu projede **testler koddan önce yazılır** (TDD). Her görevin testleri hazırdır ve "bekliyor" olarak işaretlidir.
Senin işin: testleri geçirecek kodu yazmak. **Testleri değiştirmezsin.**

### Bir görevi baştan sona yapmak

**1. Güncel kodu al ve görev için yeni dal aç**
```bash
git switch main
git pull
git switch -c gorev/t1-3-ilerleme
```

**2. Görevi seç.** `python scripts/check.py` çalıştır; en altta görev listesi çıkar:
```
⏳ T1.3  İlerleme yüzdesi (progress_percent)    tests/unit/test_progress.py
```
Görevler arasındaki sıra için aşağıdaki [görev sırası](#görev-sırası) tablosuna bak.

**3. Testi "aç".** Görevin test dosyasını aç (ör. `tests/unit/test_progress.py`). En üstte şu iki satır var:
```python
# GÖREV T1.3 — kodu yazınca BU SATIRI SİL:
pytestmark = pytest.mark.xfail(strict=True, reason="T1.3 henüz yapılmadı")
```
**Bu iki satırı sil.** Testin geri kalanına dokunma. Testleri oku: neyin beklendiğini en net onlar söyler.

**4. Kırmızıyı gör.** `pytest tests/unit/test_progress.py` → testler kırmızı (FAILED). Bu normal; kod henüz yok.

**5. Kodu yaz.** İlgili dosyayı aç (ör. `app/domain/progress.py`). Fonksiyonun açıklamasında (docstring) ne yapacağı
yazıyor. `raise NotImplementedError` satırını sil, yerine kodunu yaz.

**6. Yeşili gör.** `pytest tests/unit/test_progress.py` → hepsi geçene kadar 5. adıma dön.

**7. Temizle ve kontrol et.** Kodu okunur hale getir (refactor), sonra:
```bash
python scripts/check.py
```
Sonda **"HER ŞEY TAMAM ✅"** görmelisin. Görmüyorsan mesajda ne yapman gerektiği yazar.

**8. Gönder.**
```bash
git add .
git commit -m "feat: ilerleme yüzdesi hesaplandı (T1.3)"
git push -u origin gorev/t1-3-ilerleme
```
GitHub'da çıkan **"Compare & pull request"** butonuyla PR aç. GitHub Actions testleri otomatik çalıştırır
(PR sayfasında yeşil ✓ ya da kırmızı ✗). Yeşilse takım arkadaşın inceleyip merge eder.
Son olarak ekibin görev tablosunda (Google Sheets) görevin tamamlanma tarihini yaz.

### Hata mesajları ne demek?

| Görürsen | Anlamı | Ne yapmalı |
|---|---|---|
| `XPASS(strict)` | Kod çalışıyor ama "bekliyor" işareti hâlâ duruyor | Test dosyasındaki `pytestmark = ...` satırını sil |
| `NotImplementedError` | Fonksiyon henüz yazılmamış | `raise NotImplementedError` satırını kendi kodunla değiştir |
| `FAILED ... assert 66 == 67` | Kodun sonucu (solda) beklenenden (sağda) farklı | Testteki örneğe bak, kodu düzelt |
| `ImportError` / `AttributeError` | Fonksiyon/sınıf adı beklenenden farklı | Adı değiştirme; [sözleşme tablosu](docs/TEST_STRATEGY.md#4-sözleşme-hangi-dosyada-ne-var) ile karşılaştır |
| `ModuleNotFoundError: fastapi` | Sanal ortam aktif değil | Kurulumdaki 3. adımı tekrarla |
| Ruff `E501 Line too long` vb. | Kod stili sorunu | `python scripts/check.py` çoğunu otomatik düzeltir; kalanı mesajdaki satırda düzelt |
| `xfailed` | Henüz yapılmamış görevlerin testleri | Normal, bir şey yapma |

### Kurallar
- **Testleri değiştirme.** Bir test yanlış ya da eksik görünüyorsa GitHub'da Issue aç ya da takım arkadaşına söyle; testler Claude ile düzeltilir.
- **`main` dalına doğrudan push yapma**, her görev kendi dalında ve PR ile gelir.
- **`.env` ve Firebase anahtar dosyalarını asla commit'leme** (`.gitignore` bunları zaten dışarıda tutar).
- Fonksiyon/sınıf adlarını ve dosya yerlerini değiştirme; testler bu adlarla çalışır.
- Şablonlardaki `data-...` öznitelikleri (`data-count`, `data-error` vb.) testlerin okuduğu işaretlerdir, silme.
  Tasarımı (HTML yapısı, CSS) istediğin gibi değiştirebilirsin.

### Görev sırası

Bir görevin testleri önceki görevlerin kodunu kullanabilir. Bu sırayla gitmek en kolayı:

| Görev | Dosya | Önce bitmesi gerekenler |
|---|---|---|
| T1.1 Kullanıcı doğrulanmış mı | `app/domain/models.py` | — |
| T1.2 Form doğrulama | `app/domain/validation.py` | — |
| T1.3 İlerleme yüzdesi | `app/domain/progress.py` | — |
| T1.4 Türkçe arama | `app/domain/search.py` | — |
| T1.5 Bellek içi veritabanı | `app/repositories/memory.py` | T1.4 |
| T1.6 Kampanya servisi | `app/services/petition_service.py` | T1.2, T1.5 |
| T1.7 Kampanya sayfaları | `app/routes/pages.py` | T1.3, T1.6 |
| T2.1 İmza uygunluğu | `app/domain/eligibility.py` | T1.1 |
| T2.2 İmza servisi | `app/services/signature_service.py` | T1.5, T2.1 |
| T2.3 Paylaşım linkleri | `app/domain/share.py` | — |
| T2.4 Firebase token doğrulama | `app/auth/verifier.py` | — |
| T2.5 İmza sayfası ve canlı ilerleme | `app/routes/pages.py` | T1.7, T2.2, T2.3 |

### Kısa Git kopya kâğıdı

| Komut | Ne yapar |
|---|---|
| `git status` | Neler değişti? |
| `git switch main` + `git pull` | Ana dala geç, en güncel hali al |
| `git switch -c gorev/isim` | Yeni dal aç ve ona geç |
| `git add .` + `git commit -m "mesaj"` | Değişiklikleri kaydet |
| `git push -u origin gorev/isim` | GitHub'a gönder |
| `git merge main` | Dalındayken main'deki yenilikleri dalına al |

---

## 3. Klasör yapısı

```
app/
  main.py              uygulamayı kuran create_app() fonksiyonu
  config.py            .env ayarları
  clock.py             saat (testlerde sabit saat kullanılır)
  domain/              saf iş kuralları: modeller, doğrulama, ilerleme, arama, imza uygunluğu, paylaşım
  repositories/        veritabanı: base.py (arayüz), memory.py (demo/test), firestore.py (gerçek)
  services/            kampanya ve imza iş mantığı
  auth/                Firebase token doğrulama, demo kullanıcılar
  routes/              sayfalar (pages.py), giriş/çıkış (auth.py), yardımcılar (deps.py)
  templates/           Jinja2 HTML şablonları
  static/              CSS (ve sadece giriş için küçük bir JS dosyası)
tests/
  unit/                birim testleri (hızlı, veritabanı/ağ yok)
  integration/         sayfa/uç nokta testleri (FastAPI TestClient)
  helpers.py, conftest.py  ortak test verileri ve fixture'lar
scripts/check.py       tek komutla kontrol
docs/                  plan, test stratejisi, kararlar, rapor
```

**Jinja2 nedir?** Python'un HTML şablon dili. HTML içine `{{ petition.title }}` ile değişken, `{% for p in petitions %}`
ile döngü yazılır; sunucu sayfayı doldurup tarayıcıya hazır HTML gönderir. Ortak menü `base.html`'de bir kez yazılır,
diğer sayfalar `{% extends "base.html" %}` ile onu kullanır.

---

## 4. Firebase'i bağlama (Faz 2)

1. https://console.firebase.google.com → **Proje ekle**.
2. **Authentication → Sign-in method:** "E-posta/Şifre" ve "Telefon" sağlayıcılarını aç.
   Telefon için **"Test için telefon numaraları"** bölümüne birkaç sahte numara + kod ekle (gerçek SMS harcamaz).
3. **Firestore Database → Veritabanı oluştur** (production modu, bölge: `europe-west`).
4. **Proje ayarları → Genel → Web uygulaması ekle:** çıkan `firebaseConfig` değerlerini `.env` içindeki
   `FIREBASE_API_KEY`, `FIREBASE_AUTH_DOMAIN`, `FIREBASE_PROJECT_ID`, `FIREBASE_APP_ID` alanlarına yaz.
5. **Proje ayarları → Hizmet hesapları → Yeni özel anahtar oluştur:** inen dosyayı proje klasörüne
   `firebase-key.json` adıyla koy ve `.env` içinde `FIREBASE_CREDENTIALS=firebase-key.json` yaz.
   Bu dosya gizlidir; `.gitignore` onu commit'lemez, kimseyle paylaşma.
6. Sunucuyu yeniden başlat. Artık giriş sayfası Firebase'i kullanır.

## 5. Yayına alma (Render)

GitHub Pages yalnızca statik dosya sunar, Python çalıştıramaz; bu yüzden ücretsiz **Render** kullanıyoruz.

1. https://render.com → GitHub ile giriş → **New → Web Service** → bu repoyu seç.
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn app.main:create_app --factory --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips "*"`
4. **Environment** bölümüne ekle: `APP_ENV=prod`, `SECRET_KEY` (uzun rastgele metin), `BASE_URL`
   (ör. `https://imza.onrender.com`), dört `FIREBASE_*` değeri ve `FIREBASE_CREDENTIALS` (anahtar JSON dosyasının
   **içeriğinin tamamı**).
5. Firebase Console → Authentication → Settings → **Authorized domains** listesine Render adresini ekle.
6. Her `main` push'unda Render otomatik yeniden yayınlar. Ücretsiz planda site 15 dk boşta kalınca uyur;
   ilk açılış ~30 sn sürebilir (sunumdan önce siteyi bir kez aç).
