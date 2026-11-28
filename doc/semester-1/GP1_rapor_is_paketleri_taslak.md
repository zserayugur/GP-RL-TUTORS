# GP-1 raporu: bölüm planı ve iş paketleri (TASLAK)

*Hazırlayan: Seray · 28 Kasım 2026 · Durum: ekibin onayına açık taslak. Sorumlular, mevcut görev dağılımına göre önerildi; ekipçe değiştirilebilir.*
*Hedef: 80–90 sayfa, tek ve kesintisiz bir belge (danışman isteği). Teslim: yaklaşık 4 Ocak 2027 (H13). Dil: İngilizce.*

## Bölüm planı

| # | Bölüm | İçerik | Sayfa | Sorumlu | Mevcut kaynak |
|---|---|---|---|---|---|
| 1 | Introduction | Problem, motivasyon, RQ1–RQ4, hipotezler, katkılar | 4 | İrem | TÜBİTAK 1.1–1.2 |
| 2 | Background and related work | "Önceki çalışma – sınırlılık – katkı" düzeninde: öğrenci modelleri ve simülatörler, sağlam değerlendirme (REM), RL ile öğretim, LLM öğrenciler | 12 | Herkes (Seray 2.2–2.3, İrem RL, Elifnaz LLM) | Literatür notları, Seray'ın 2.2–2.3 taslağı |
| 3 | Requirements | FR/NFR tabloları, kabul kriterleri, izlenebilirlik | 8 | İrem | `Gereksinimler_FR_NFR_v4.md` |
| 4 | Use case model | Tek use case diyagramı, açıklama tabloları ve senaryolar (UC-01–UC-15) | 16 | Seray (UC-01–07, UC-11–15), Elifnaz (UC-08–10) | Seray v2 belgesi, diyagram v4 |
| 5 | System design | Mimari (6 katman), kaba modül/sınıf tasarımı, veri modeli (soru bankası şeması), 4 üst düzey sequence diyagramı | 14 | İrem (mimari), Seray (veri modeli, 2 diyagram), Elifnaz (1 diyagram) | `Mimari_Tasarim_v2.md`, `item_bank_schema.sql` |
| 6 | User interface | Mockup'lar ve arayüzler: öğrenci, öğretmen/araştırmacı, içerik denetçisi, yönetici ekranları | 8 | Elifnaz (arayüz), Seray (öğrenci ve araştırmacı ekranları) | — |
| 7 | Data and student simulators | ASSISTments ve Eedi hazırlığı, BKT kalibrasyonu ve doğrulama, Simülatör A, öğrenci tipleri, soru bankası, lisanslar | 10 | Seray | İş günlüğü, raporlar, `veri_kaynaklari.md` |
| 8 | RL formulation and environment | POMDP, gözlem/eylem/ödül, maskeler, kesikli eylem uzayı ve algoritma seçimi gerekçesi | 8 | İrem, Elifnaz (formal tanım) | Karar dokümanı, formal tanım belgesi |
| 9 | LLM student (pilot) | Model seçimi, persona/yanılgı istemi, trace örnekleri, ilk pilot | 5 | Elifnaz | Elifnaz'ın iş günlüğü |
| 10 | Work done, plan and risks | Ekip olarak yapılanlar, 2. dönem planı, risk tablosu | 5 | Herkes | İş günlükleri, risk tablosu |
| | **Toplam** | | **90** | | |

Sayfalar hedefe göre ±%10 ayarlanabilir. Kaynakça ve ekler sayıma dahil değil.

## Üst düzey sequence diyagramları (öneri)

1. **Öğretim oturumu (UC-03):** Öğrenci → Arayüz → Ortam → Politika → Simülatör/öğrenci → Ortam (gözlem, maske) → Politika … → son test. *Sorumlu: Seray*
2. **Deney çalıştırma (UC-05):** Araştırmacı → Deney yöneticisi → Ortam + simülatörler → Politika eğitimi → Değerlendirme → Sonuç paneli. *Sorumlu: İrem*
3. **Simülatör kalibrasyonu (UC-15):** Araştırmacı → Veri hazırlama betikleri → pyBKT → parametre dosyası → Simülatör A. *Sorumlu: Seray*
4. **İçerik ekleme ve onay (UC-08–10):** Öğretmen → İçerik deposu → Otomatik doğrulama → Denetçi → Onaylı havuz → Anlık görüntü. *Sorumlu: Elifnaz*

## Zaman planı

| Hafta | Tarih | Hedef |
|---|---|---|
| H8 | 30 Kas – 6 Ara | Bölüm planının onayı; herkes kendi bölümünün iskeletini (başlıklar ve maddeler) yazar |
| H9 | 7 – 13 Ara | Bölüm 3, 4 ve 7'nin ilk taslağı; use case diyagramı ve tabloları |
| H10 | 14 – 20 Ara | Bölüm 5, 6, 8 ve 9'un ilk taslağı; mockup'lar ve sequence diyagramları |
| H11 | 21 – 27 Ara | Bölüm 1, 2 ve 10; bütün belgeyi birleştirme |
| H12 | 28 Ara – 3 Oca | Tutarlılık ve kaynak kontrolü, sayfa ayarı, son okuma |
| H13 | 4 Oca | Teslim ve sunum |

## Notlar

- Her bölüm onaylı TÜBİTAK metnine sadık kalmalı; değişiklikler "değişiklik" olarak açıkça işaretlenmeli.
- Kaynaklar yalnızca doğrulanmış künyelerle yazılır.
