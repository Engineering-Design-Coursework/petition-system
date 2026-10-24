# Proje Planı

**Son güncelleme:** 24 Ekim 2026

Görevler kişiye atanmamıştır; ekip kendi arasında paylaşır. Kodlama görevlerinin testleri hazırdır
(`python scripts/check.py` en altta hangi görevin bitip hangisinin beklediğini gösterir).
"(Claude)" işaretli işler ajan tarafından yapılır.

## Takvim

| Faz | Tarih | Hedef | Son teslim |
|---|---|---|---|
| 0 — Kurulum | 13–16 Eki | İskelet, CI, belgeler, sözleşme testleri, Firebase projesi | 16 Eki |
| 1 — Kampanya çekirdeği | 17–23 Eki | Kampanya oluştur/listele/detay/ara (demo modunda çalışır) | 23 Eki |
| 2 — İmza ve doğrulama | 24–30 Eki | Firebase girişi, tekil imza, canlı ilerleme, paylaşım | 30 Eki |
| Ara rapor | 31 Eki–1 Kas | Rapor son hali, ekran görüntüleri, PDF | **≈ 2 Kas** |
| Vize haftası | 2–9 Kas | Yalnızca hata düzeltme | — |
| 3 — Kalite ve yayın | 10–23 Kas | Geri bildirim, mutation testing, E2E, Render'a yayın | 23 Kas |
| 4 — Final | 24 Kas–6 Ara | Kabul testi (UAT), final rapor, sunum | **14. hafta ≈ 7–11 Ara** |

> Tarihler ara raporun 9. haftaya (≈ 2 Kasım) denk geldiği varsayımıyla hesaplandı. Kesin tarihler açıklanınca güncellenecek.

## Faz 0 — Kurulum (13–16 Ekim)
- [x] FastAPI + Jinja2 iskeleti, eski Flask taslağının taşınması (Claude)
- [x] GitHub Actions CI: ruff + pytest + branch coverage + görev özeti (Claude)
- [x] Faz 1–2 sözleşme testleri, `xfail` olarak (Claude)
- [x] README (kurulum + elle geliştirme rehberi), AGENTS.md, test stratejisi, kararlar, rapor iskeleti (Claude)
- [ ] Her iki ekip üyesi kendi bilgisayarında README'deki kurulumu yapıp `python scripts/check.py` ile "HER ŞEY TAMAM" görür
- [ ] Gereksinim listesini ([TEST_STRATEGY §2](TEST_STRATEGY.md#2-gereksinimler)) birlikte okuyup onaylayın (testability review)
- [x] Firebase projesi oluştur (README §4, adım 1–3), test telefon numaralarını ekle
- [ ] GitHub → Settings → Branches: `main` için "Require status checks (CI) to pass" kuralı
- [ ] Proje adına karar verin (raporda ve sitede kullanılacak)

## Faz 1 — Kampanya çekirdeği (17–23 Ekim)
- [x] **T1.1** Kullanıcı doğrulanmış mı — `app/domain/models.py` → `tests/unit/test_models.py`
- [x] **T1.2** Form doğrulama — `app/domain/validation.py` → `tests/unit/test_validation.py`
- [x] **T1.3** İlerleme yüzdesi — `app/domain/progress.py` → `tests/unit/test_progress.py`
- [x] **T1.4** Türkçe arama — `app/domain/search.py` → `tests/unit/test_search.py`
- [ ] **T1.5** Bellek içi veritabanı — `app/repositories/memory.py` → `tests/unit/test_memory_repository.py` (önce T1.4)
- [ ] **T1.6** Kampanya servisi — `app/services/petition_service.py` → `tests/unit/test_petition_service.py` (önce T1.2, T1.5)
- [ ] **T1.7** Kampanya sayfaları — `app/routes/pages.py` → `tests/integration/test_petition_pages.py` (önce T1.3, T1.6)
- [ ] **T1.8** Tasarım: CSS, mobil uyum, ana sayfa görünümü (testi yok; tarayıcıda telefon ve masaüstü boyutunda kontrol)
- [ ] Demo modunda uçtan uca elle deneme: kampanya aç → listede gör → ara → detayını aç

## Faz 2 — İmza ve doğrulama (24–30 Ekim)
- [x] **T2.1** İmza uygunluğu (karar tablosu) — `app/domain/eligibility.py` → `tests/unit/test_eligibility.py` (önce T1.1)
- [ ] **T2.2** İmza servisi — `app/services/signature_service.py` → `tests/unit/test_signature_service.py` (önce T1.5, T2.1)
- [ ] **T2.3** Paylaşım linkleri — `app/domain/share.py` → `tests/unit/test_share.py`
- [x] **T2.4** Firebase token doğrulama — `app/auth/verifier.py` → `tests/unit/test_firebase_verifier.py`
- [ ] **T2.5** İmza sayfası + canlı ilerleme + paylaşım — `app/routes/pages.py` → `tests/integration/test_signing.py` (önce T1.7, T2.2, T2.3)
- [ ] **T2.6** Firestore veritabanı — `app/repositories/firestore.py` (docstring'deki örnek; elle test, Faz 3'te emulator testi)
- [x] **T2.7** Giriş sayfası: Firebase e-posta (doğrulama e-postası) + telefon (SMS) girişi, `static/js/auth.js` (Claude)
- [x] **T2.8** Firebase Console: web uygulaması + servis hesabı anahtarı, `.env` doldurma (README §4)
- [ ] Gerçek Firebase ile elle deneme: e-posta ile kayıt → doğrulama → imza; aynı hesapla ikinci imza reddedilir

## Ara rapor (31 Ekim – 1 Kasım, teslim ≈ 2 Kasım)
- [ ] `docs/report/INTERIM_REPORT.md` son okuma, yazar bilgileri ve katkılar
- [ ] Ekran görüntüleri (ana sayfa, oluşturma formu, detay + ilerleme çubuğu, giriş, CI özeti, coverage raporu)
- [ ] Kaynakların (APA 7) doğrulanması — "(verify)" notlarının kaldırılması
- [ ] Bölüm şablonuna (Word) aktarma ve PDF çıktısı; kodlar ekte kod biçimlendirme aracıyla

## Faz 3 — Kalite ve yayın (10–23 Kasım)
- [ ] Hoca geri bildirimlerinin plana işlenmesi
- [ ] **T3.1** Kampanya sahibinin kampanyayı kapatabilmesi (testleri Claude yazacak)
- [ ] **T3.2** Coverage kapısı: `domain` + `services` için branch coverage ≥ %85, CI'da zorunlu
- [ ] **T3.3** Mutation testing (mutmut) haftalık CI işi, mutation score ve hayatta kalan mutant analizi
- [ ] **T3.4** Firestore Emulator ile `FirestorePetitionRepository` entegrasyon testleri
- [ ] **T3.5** Playwright ile 2–3 uçtan uca test (kampanya aç → imzala → çubuk artar)
- [ ] **T3.6** Render'a yayın + duman testi (smoke test): `/health`, ana sayfa, giriş
- [ ] **T3.7** `pip-audit` (bağımlılık güvenlik taraması) CI adımı
- [ ] **T3.8** Erişilebilirlik temel kontrolü (etiketler, kontrast, klavye ile gezinme)

## Faz 4 — Final (24 Kasım – 6 Aralık)
- [ ] Kabul testi (UAT): en az 5 sınıf arkadaşı, kabul kriterleri listesi ile (ör. "kullanıcı 2 dakikada kampanya açabilir")
- [ ] UAT'ta çıkan hataların düzeltilmesi
- [ ] Final raporu (ara rapordan türetilir), sonuçlar: coverage, mutation score, UAT sonuçları
- [ ] Sunum slaytları + canlı demo + yedek demo videosu
