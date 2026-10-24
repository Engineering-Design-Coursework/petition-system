# Proje Planı

**Son güncelleme:** 24 Ekim 2026

Görev dağılımı (kim aldı, ne zaman bitti) ekibin Google Sheets tablosunda, **"PROJE-TASK MANAGEMENT"**, tutulur.
Kodlama görevlerinin durumu için: `python scripts/check.py` (en altta ✅ / ⏳ tablosu).
Bu dosyada yalnızca takvim ve tabloda olmayan ekip işleri var.

## Takvim

| Faz | Tarih | Hedef | Son teslim |
|---|---|---|---|
| 0 — Kurulum | 13–16 Eki | İskelet, CI, belgeler, sözleşme testleri, Firebase projesi | 16 Eki |
| 1 — Kampanya çekirdeği | 17–23 Eki | Kampanya oluştur/listele/detay/ara (demo modunda çalışır) | 23 Eki |
| 2 — İmza ve doğrulama | 24–30 Eki | Firebase girişi, tekil imza, canlı ilerleme, paylaşım | 30 Eki |
| Ara rapor | 31 Eki–1 Kas | Rapor son hali, ekran görüntüleri, PDF | **≈ 2 Kas** |
| Vize haftası | 2–9 Kas | Yalnızca hata düzeltme | — |
| 3–4 — Kalite, yayın, final | 10 Kas–6 Ara | T3.x görevleri, kabul testi, final rapor, sunum | **14. hafta ≈ 7–11 Ara** |

> Tarihler ara raporun 9. haftaya (≈ 2 Kasım) denk geldiği varsayımıyla hesaplandı. Kesin tarihler açıklanınca güncellenecek.
> Faz 1'in kalan görevleri (T1.6, T1.7, T1.8) Faz 2 haftasında bitirilecek.

## Ekip işleri (ara rapordan önce)
- [ ] Her ekip üyesi kendi bilgisayarında README'deki kurulumu yapıp `python scripts/check.py` ile "HER ŞEY TAMAM" görür
- [ ] Gereksinim listesini ([TEST_STRATEGY §2](TEST_STRATEGY.md#2-gereksinimler)) birlikte okuyup onaylayın (testability review)
- [ ] GitHub → Settings → Branches: `main` için "Require status checks (CI) to pass" kuralı
- [ ] Proje adına karar verin (raporda ve sitede kullanılacak)

## Ara rapor (31 Ekim – 1 Kasım, teslim ≈ 2 Kasım)
- [ ] `docs/report/INTERIM_REPORT.md` son okuma, yazar bilgileri ve katkılar (her üye kendi paragrafını yazar)
- [ ] Ekran görüntüleri (ana sayfa, oluşturma formu, detay + ilerleme çubuğu, giriş, CI özeti, coverage raporu)
- [ ] Kaynakların (APA 7) doğrulanması — "(verify)" notlarının kaldırılması
- [ ] Bölüm şablonuna (Word) aktarma ve PDF çıktısı; kodlar ekte kod biçimlendirme aracıyla

## Vizelerden sonra (10 Kasım – 6 Aralık)
T3.x görevleri (tabloda), kabul testi (UAT), final raporu ve sunum. Ayrıntılı plan vizelerden sonra yapılacak.
