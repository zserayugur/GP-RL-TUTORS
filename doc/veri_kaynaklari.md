# Veri kaynakları ve kullanım koşulları (NFR-06)

*Hazırlayan: Seray · 24 Kasım 2026 · Amaç: `.gitignore` kontrolüne ek olarak, her veri kaynağının nereden geldiğini, hangi koşullarla kullanılabildiğini ve projede nasıl kullanıldığını kayıt altına almak.*

Genel kural: **Ham veri ve ondan türetilen satır düzeyindeki dosyalar Git'e konmaz.** Depoya yalnızca indirme ve işleme betikleri ile özet sonuçlar (ör. beceri başına parametreler, sayımlar) girer. Betik çıktıları `data/interim/` klasörüne yazılır; bu klasör `.gitignore`'dadır.

## Özet tablo

| Kaynak | Kullanım | Lisans / koşul | Doğrulama durumu | Git'te mi? |
|---|---|---|---|---|
| ASSISTments 2009–2010 Skill Builder | BKT L0, T ve kısa cevap G/S (WBS 6.1) | Açık lisans adı yok; ASSISTments kullanım koşulları geçerli | Koşullar resmî sayfadan okundu (24.11.2026) | Hayır |
| Eedi "Mining Misconceptions in Mathematics" (Kaggle) | Soru metinleri, çeldiriciler, yanılgı etiketleri (WBS 5.4, 5.2) | CC BY-NC 4.0 ve yarışma kuralları; yeniden dağıtılamaz | Onaylı TÜBİTAK metninde [23]; Kaggle'da kurallar kabul edildi | Hayır |
| Eedi NeurIPS 2020 Education Challenge | Çoktan seçmeli G/S, çeldirici olasılıkları (WBS 5.5), FR-40 karşılaştırması | **Doğrulanmadı** (aşağıya bkz.) | Resmî sayfa açılamadı | Hayır |
| OpenStax Prealgebra 2e, kesirler bölümü | Kısa konu anlatımları | CC BY-NC-SA 4.0 | Onaylı TÜBİTAK metninde [35] | Türetilen metinler aynı lisansla girebilir |

## 1. ASSISTments 2009–2010 Skill Builder

- **Kaynak sayfa:** https://sites.google.com/site/assistmentsdata/home/2009-2010-assistment-data/skill-builder-data-2009-2010
- **Kullanım koşulları:** https://sites.google.com/site/assistmentsdata/termsofuseforusingdata
- **Koşulların özeti (24.11.2026'da okundu):**
  - Veriden öğrencilerin kimliği çıkarılmaya çalışılmaz. Kimlik bilgisi bulunursa silinir ve ASSISTments'a bildirilir.
  - Veri başkasına verilmez ve yalnızca belirtilen amaçla kullanılır.
  - Yayınlarda ASSISTments TestBed kullanımı belirtilir.
  - Yayınlanan çalışmalarda kullanılan veri ve algoritmalar açık olmalıdır. Sayfadaki nota göre kaynak kodunu paylaşmak istemeyen bu veriyi kullanamaz.
  - Atıf: Veri setinin tam adresi (yukarıdaki kaynak sayfa) yayında yazılmalı, ayrıca Feng, Heffernan & Koedinger (2009) makalesine atıf yapılmalı. Bu makale onaylı metinde [16] olarak zaten var.
  - Not: Koşul sayfası ASSISTments TestBed için yazılmış. Kamuya açık 2009–2010 dosyalarına da uygulandığını varsayıyoruz.
- **Projedeki kullanım:** Seray'ın indirdiği `assistments_fractions.csv`, `assistments_temizle.py` ile temizlendi (51.131 satır, 2.025 öğrenci). Temiz dosya ekibin ortak Drive'ında tutuluyor.
- **Dikkat:**
  - "Veri başkasına verilmez" maddesi nedeniyle temiz CSV yalnızca proje ekibi içinde paylaşılmalı.
  - Kaynak sayfada, tekrarlanan kayıtların düzeltildiği bir sürümün de olduğu yazıyor. Biz tekrarları kendi betiğimizle temizledik (2.250 tekrar silindi). Raporda bu belirtilmeli.
  - Kodun açık olma şartı bizim depomuzla uyumlu.

## 2. Eedi "Mining Misconceptions in Mathematics" (Kaggle)

- **Kaynak:** https://www.kaggle.com/competitions/eedi-mining-misconceptions-in-mathematics
- **Lisans:** CC BY-NC 4.0. Yarışma kuralları gereği yalnızca ticari olmayan akademik kullanım; **yeniden dağıtılamaz** (onaylı metin, kaynak [23]).
- **Projedeki kullanım:** `src/data_prep/eedi_kaggle_fractions.py` (WBS 5.4). 103 kesir sorusu seçildi.
- **Kural:** Her ekip üyesi veriyi kendi Kaggle hesabıyla, yarışma kurallarını kabul ederek indirir. Ekip içinde dosya olarak paylaşılmaz.

## 3. Eedi NeurIPS 2020 Education Challenge

- **İndirme adresi:** https://dqanonymousdata.blob.core.windows.net/neurips-public/data.zip
- **Belge:** Wang ve ark. 2020, "Instructions and Guide for Diagnostic Questions: The NeurIPS 2020 Education Challenge", arXiv:2007.12061 (onaylı metinde [25]).
- **Lisans: DOĞRULANMADI.**
  - Zip dosyasının içinde lisans dosyası yok.
  - Eedi'nin yarışma sayfası (eedi.com/projects/neurips-education-challenge) 24.11.2026'da açılamadı (404).
  - Bir arama sonucu, bu sayfada verinin **CC BY-NC-ND 4.0** ile lisanslandığının yazdığını belirtiyor; ama bunu sayfanın kendisinden göremedik.
- **Projedeki kullanım:** `src/data_prep/eedi_neurips_guess_slip.py` (WBS 5.5). Yalnızca sayısal özetler (G/S, çeldirici olasılıkları) kullanılıyor.
- **Dikkat:** Lisans gerçekten "NoDerivatives" (ND) ise, `data/images/` içindeki soru resimlerini metne çevirip soru bankasına koymak türev eser sayılabilir. **Lisans doğrulanmadan bu resimler soru bankasında kullanılmamalı.** Doğrulama için Eedi'ye ya da danışmana sorulabilir.

## 4. OpenStax Prealgebra 2e

- **Lisans:** CC BY-NC-SA 4.0 (onaylı metin, kaynak [35]). CC BY değildir.
- **Projedeki kullanım:** Kısa konu anlatımları bu kaynaktan türetilecek. Türetilen metinler ticari olmayan kullanımla sınırlı kalır ve aynı lisansla paylaşılır.
- **Not:** Kesirler bölümündeki alıştırmalar, soru bankası açığını kapatmak için soru gövdesi kaynağı olarak da kullanılabilir (aynı lisans koşullarıyla).

## Bakım

Yeni bir veri kaynağı eklenince bu dosyaya bir bölüm eklenir: kaynak adresi, lisans, doğrulama tarihi, kullanım şekli ve Git durumu.
