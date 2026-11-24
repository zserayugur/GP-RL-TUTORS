# İş günlüğü — Seray

En yeni kayıt en üstte.

## 2026-11-24 — BKT kalibrasyonu (WBS 6.1)

- **Ne yapıldı:** pyBKT 1.4.3 ile S1–S6 için BKT parametreleri (L0, T, G, S) temiz ASSISTments verisinden bulundu. G ve S kısa cevaplı (sa) ve çoktan seçmeli (mc) sorular için ayrı tutuldu; mc yalnızca S2'de var. Öğrenci bazlı 5 katlı çapraz doğrulama yapıldı.
- **Veri:** `assistments_kesir_temiz.csv` (51.131 satır, 2.025 öğrenci). S6'daki 3 çoktan seçmeli satır çıkarıldı, 51.128 satır kullanıldı. Veri Git'te değil.
- **Parametreler (tüm veri):**

  | Beceri | L0 | T | G | S |
  |---|---|---|---|---|
  | S1 | 0,627 | 0,093 | 0,081 | 0,293 |
  | S2 (sa) | 0,633 | 0,066 | 0,489 | 0,045 |
  | S2 (mc) | 0,633 | 0,066 | 0,522 | 0,096 |
  | S3 | 0,752 | 0,089 | 0,110 | 0,198 |
  | S4 | 0,578 | 0,134 | 0,305 | 0,214 |
  | S5 | 0,708 | 0,190 | 0,107 | 0,195 |
  | S6 | 0,608 | 0,015 | 0,424 | 0,202 |

- **Çapraz doğrulama:** Görülmemiş öğrencilerde AUC 0,66–0,74. Altı becerinin hepsinde RMSE ve log-loss, ortalama doğruluğu tahmin eden referans modelden daha iyi.
- **Açık noktalar:**
  - S2'de G yüksek (sa 0,49, mc 0,52; mc makullük sınırı 0,5'i aşıyor). Plan gereği mc G/S Eedi'den alınacak.
  - S6'da T çok düşük (0,015): simülatörde S6 çok yavaş öğrenilir. Hocaya sorulacak.
- **Kimi etkiliyor:** İrem — `src/core/bkt_tracker.py` içindeki `DEFAULT_PARAMS` yer tutucu; bu değerlerle beceri başına parametreye geçilebilir (sa değerleri).
- **Sıradaki adım:** WBS 6.2, beş öğrenci tipli Simülatör A.
