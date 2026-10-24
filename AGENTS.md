# AGENTS.md — Yapay zekâ ajanları için proje kuralları

Bu dosya bu repoda çalışan her ajan (Claude Code vb.) için bağlayıcıdır. İnsanlar için rehber: `README.md`.

## Proje
CEN317 Engineering Design dönem projesi: change.org benzeri **imza kampanyası platformu**.
Zorunlu özellikler: kampanya başlatma/destek toplama, **mükerrer imzayı engelleyen e-posta/telefon doğrulaması**,
**anlık ilerleme çubuğu**, **sosyal medya paylaşımı**. Ekip 3 kişi; biri yalnızca Python biliyor.

- Mimari ve gerekçeler: `docs/DECISIONS.md`
- Sözleşme (hangi dosyada hangi sınıf/fonksiyon), test teknikleri, risk tablosu: `docs/TEST_STRATEGY.md`
- Takvim ve ekip işleri: `docs/PROJECT_PLAN.md`
- Görev dağılımı (kim, ne zaman): ekibin Google Sheets tablosu "PROJE-TASK MANAGEMENT" (link repoda yok, repo herkese açık)
- Ders raporu (İngilizce, şablona birebir uygun): `docs/report/INTERIM_REPORT.md`

## Komutlar
```bash
pip install -r requirements-dev.txt
python scripts/check.py                               # ruff --fix + format + ruff check + pytest + görev durumu
pytest                                                # testler
pytest --cov=app --cov-branch --cov-report=term       # kapsam
uvicorn app.main:create_app --factory --reload        # uygulama (Firebase yoksa demo modu)
```

## Mimari özeti
FastAPI + Jinja2 (sunucu tarafında HTML) + htmx (ilerleme çubuğu yoklaması) + Firebase Auth + Firestore.
`create_app(settings, repo, verifier, clock)` bağımlılıkları dışarıdan alır; testler `InMemoryPetitionRepository`
(Fake), `StubTokenVerifier` (Stub) ve `FixedClock` kullanır. Katmanlar: `domain` (saf fonksiyonlar) →
`repositories` (Protocol + memory + firestore) → `services` → `routes`.

## Kurallar

### 1. Testler (TDD, "önce sözleşme")
- **Testlerin tamamını ajan (Claude) yazar.** Kod yazılmadan önce yazılır ve sözleşmeyi (dosya, ad, imza, davranış) tanımlar.
- Yeni bir görevin test dosyası şu biçimde başlar (`scripts/check.py` bunu okur, biçimi bozma):
  ```python
  """T3.1 — Kısa Türkçe başlık (fonksiyon_adi). Ek açıklama."""

  ...
  # GÖREV T3.1 — kodu yazınca BU SATIRI SİL:
  pytestmark = pytest.mark.xfail(strict=True, reason="T3.1 henüz yapılmadı")
  ```
  Üretim kodunda karşılığı docstring'li bir iskelet + `raise NotImplementedError` olur.
- Yeni testi eklemeden önce, geçici bir kopyada örnek çözümle **tüm testlerin geçebildiğini doğrula**
  (çelişkili/yapılamaz test ekipte zaman kaybettirir). Örnek çözümü repoya koyma.
- Stil: Arrange-Act-Assert, ad `test_should_<sonuç>_when_<koşul>`, test başına tek davranış,
  `pytest.mark.parametrize` ile EP/BVA, karar tabloları için `pytest.param(..., id="R1-...")`.
- Test double seçimi: kendi kodumuz için Fake (InMemory repo), dış bağımlılık (Firebase, saat, ağ) için
  Stub/Mock. Kendi modellerimizi/algoritmalarımızı mock'lama. Testler ağa ve gerçek Firebase'e asla çıkmaz.
- Testler deterministik olmalı: `FixedClock`, sıralı id'ler, rastgelelik yok.
- Sözleşme değişirse önce `docs/TEST_STRATEGY.md` tablosu ve testler, sonra kod güncellenir.

### 2. Kod yazma (bir görevi uygularken)
- Görevin `pytestmark` satırlarını sil → kırmızıyı gör → en basit kodla yeşile çek → refactor.
- **Testin beklentisini (assert) koda uydurmak için değiştirme.** Test gerçekten hatalıysa ayrı bir `test:` commit'i ile,
  gerekçesini mesajda yazarak düzelt.
- Kod başlangıç seviyesindeki bir Python geliştiricisinin okuyabileceği sadelikte olmalı. Docstring ve yorumlar Türkçe,
  arayüz metinleri Türkçe.
- **JavaScript yazma**; tek istisna giriş için `app/static/js/auth.js`. Etkileşim gerekiyorsa önce htmx öznitelikleri.
- Şablonlardaki `data-*` test işaretlerini koru. Kullanıcı içeriğini asla `|safe` ile basma (XSS).
- Güvenlik kararları sunucuda verilir: kullanıcı kimliği yalnızca doğrulanmış token/oturumdan alınır, formdan asla.

### 3. Git
- Her anlamlı ve **`python scripts/check.py` ile yeşil** adımın sonunda **kendiliğinden commit ve push** yap
  (kullanıcıya ayrıca sormadan). Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `ci:`, `chore:`.
  Mesajlar kısa ve Türkçe olabilir; görev numarasını ekle: `feat: ilerleme yüzdesi (T1.3)`.
- Çalışılan dala push et (`git push -u origin <dal>`). **`main`'e doğrudan push yapma.**
- **Pull request açmadan önce mutlaka kullanıcıdan açık onay al** ("PR açayım mı?"). Onay yoksa PR açma.
- `.env`, `firebase-key*.json`, servis hesabı anahtarları ve diğer sırlar asla commit'lenmez.

### 4. Belgeleri güncel tut (her anlamlı adımda, aynı commit'te ya da hemen ardından)
- Görev tablosu (Google Sheets): görevi alan ve tarihler. Ajan tabloya erişebiliyorsa kendi görevlerini orada günceller.
- `docs/PROJECT_PLAN.md`: yalnızca takvim ya da ekip işleri değişirse, "Son güncelleme" tarihiyle.
- `docs/report/INTERIM_REPORT.md` (İngilizce): ilgili bölümler — özellikle *3. Project Materials*,
  *4. Current State of the Project*, *5. Future Improvements*, Appendix (klasör yapısı, test özeti) ve en üstteki
  "Last updated" satırı. Yeni kaynak kullanıldıysa APA 7 ile *References*'a ekle. Uydurma kaynak ekleme;
  emin olunmayan künye "(verify)" notuyla işaretlenir.
- `README.md`: kurulum/çalıştırma/bağımlılık değişirse.
- `docs/DECISIONS.md`: yeni mimari/proje kararı alınırsa yeni ADR.
- `docs/TEST_STRATEGY.md`: sözleşme, risk tablosu, kapsam/mutation sonuçları değişirse.

## Takvim (özet)
Ara rapor ≈ **2 Kasım 2026** (kesin tarih bekleniyor), 2–9 Kasım vizeler, final rapor + sunum 14. hafta (≈ 7–11 Aralık 2026).
Ayrıntı: `docs/PROJECT_PLAN.md`.
