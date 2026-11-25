# İş günlüğü — Seray

En yeni kayıt en üstte.

## 2026-11-25 — Eedi NeurIPS lisansı doğrulandı

- **Sonuç:** Resmî sayfa (eedischool.com/projects/neurips-education-challenge) lisansı **CC BY-NC-ND 4.0** olarak veriyor. 24 Kasım kaydındaki "doğrulanamadı" notu artık geçersiz.
- **Soru resimleri:** Sayfaya göre resimler yalnızca model eğitimi için paylaşılmış; başka amaçla kullanılamaz ve paylaşılamaz. **Bu yüzden task 3-4'teki 139 resimli soru soru bankasında kullanılmayacak.** Eksik sorular ekip tarafından yazılacak (25 Kasım kararı).
- **Sorun olmayan:** G/S ve çeldirici olasılıkları gibi sayısal özetleri kullanmak ve raporlamak. Atıf: Wang ve ark. 2020, arXiv:2007.12061 ([25]).
- **Güncellenen dosya:** `doc/veri_kaynaklari.md`, 3. bölüm.

## 2026-11-25 — Karar: eksik sorular ekip tarafından yazılacak (risk 10)

- **Karar (Seray):** S1, S2, S4 ve S5'teki yaklaşık 45 eksik öğretim sorusu ekip tarafından yazılacak. Yanılgılar ve çeldiriciler Eedi'deki yanılgı etiketlerinden alınacak; ASSISTments'ta soru metni olmadığı için oradan soru alınamıyor.
- **Dayanak:** Onaylı metin "proje ekibinin hazırlayıp doğruladığı başlangıç soru bankası"na izin veriyor; risk tablosundaki 10. risk (görselli sorular çıkınca madde azalması) gerçekleşti.
- **Kimi etkiliyor:** Herkes — soru yazımının iş bölümü belirlenmeli. Sorular `item_bank` şemasına `source = 'team'` olarak girecek.

## 2026-11-25 — Simülatör A: 4 öğrenci tipi (TÜBİTAK metnine göre)

- **Karar:** Onaylı TÜBİTAK metni esas alındı: "en az 4 öğrenci profili" (İP5). 5 tipli öneri geri çekildi.
- **Ne değişti:** `src/core/simulator_a_bkt.py` içindeki tipler artık LLM öğrenciyle aynı 4 profil: hızlı öğrenen (T×2), yavaş öğrenen (T×0,5), tahminci (G ve S ×1,5), yanılgısını sürdüren. Böylece üç simülatör aynı tipleri paylaşıyor.
- **Not:** "Yanılgısını sürdüren" tip, yanılgı katmanı (FR-15) gelene kadar kalibre edilmiş öğrenci gibi davranıyor; yalnızca bir işaret taşıyor. Kalibre edilmiş değerler "base" adıyla yalnızca testler için duruyor ve örneklenmiyor. Testler güncellendi, 13/13 geçti (taklit ortamda).
- **Kimi etkiliyor:** İrem — FR-13'teki "4 öğrenci tipi" ifadesi doğru, değişiklik gerekmiyor.
- **Ayrıca fark edilen (İrem):** Onaylı metin gözlemde "son eylem" bilgisini istiyor (genel alanlar: son eylem, oturum adımı, kalan adım oranı). `fraction_tutor_env.py` son eylemi yalnızca maske için tutuyor, gözleme koymuyor. 143 boyuttaki ayrılmış (boş) alana eklenebilir.

## 2026-11-24 — Literatür notları (BKT ve simülatörler)

- **Ne yapıldı:** `ref/papers/notlar/seray_notlar.md` yazıldı. Notlar İngilizce ve hocanın istediği "önceki çalışma – sınırlılık – katkı" düzeninde. Kapsanan makaleler: Corbett & Anderson 1994 (BKT), Badrinath ve ark. 2021 (pyBKT), Käser & Alexandron 2024 (simüle öğrenciler); isteğe bağlı olarak Doroudi ve ark. 2017 (REM).
- **Dayanak:** Seray'ın 2.2–2.3 taslağı ve bugünkü sonuçlarımız. Künyeler onaylı kaynakçadan alındı. Her notta tam metinden doğrulanması gereken noktalar "Check while reading" satırında yazıyor.
- **Kimi etkiliyor:** Background bölümünü yazacak olan herkes.

## 2026-11-24 — Soru bankası iskeleti (WBS 5.2, ilk adım)

- **Ne yapıldı:**
  - TÜBİTAK metnindeki alanlarla SQLite şeması yazıldı: `src/data_prep/item_bank_schema.sql`. Tablolar: beceriler, yanılgılar, sorular, şıklar, anlık görüntüler. Şemada öğretim ve test havuzları ayrı (FR-06), her yanlış şık bir yanılgıya bağlanabiliyor (FR-07), içerik onay durumları var (FR-11) ve sürümlü anlık görüntü alınabiliyor (FR-12).
  - Kurulum betiği yazıldı: `src/data_prep/build_item_bank.py`. Eedi'deki 103 kesir sorusunu şıkları ve yanılgılarıyla yüklüyor. Görselli sorular işaretli kalıyor; `usable_items` görünümüne girmiyor.
  - Veritabanı `data/interim/item_bank.sqlite` konumunda, Git'te değil (Eedi metinleri içeriyor).
- **Sonuç:** 87 kullanılabilir soru ve 101 yanılgı yüklendi. 20 öğretim sorusuna ulaşmak için eksikler: S1'de 17, S2'de 12, S4'te 8, S5'te 8 soru.
- **Ekibin dolduracakları:**
  - Kullanılabilir sorulardaki 261 yanlış şıktan 60'ında yanılgı etiketi yok; onaylı metne göre her yanlış şık bir yanılgıya bağlanmalı.
  - Her sorunun zorluğu (kolay/zor); ortamdaki "kolay soru" ve "zor soru" eylemleri buna dayanıyor.
  - İpucu, çözümlü örnek ve açıklama metinleri.
  - Kısa cevaplı ön ve son test havuzu (beceri başına en az 8 soru).
- **Sıradaki adım:** 25 Kasım'da eksik soruların nasıl tamamlanacağına karar verilmesi.

## 2026-11-24 — Veri kaynakları ve lisans kaydı (NFR-06)

- **Ne yapıldı:** Elifnaz'ın "`.gitignore` kontrolü lisans uyumunu tek başına doğrulamaz" yorumu üzerine `doc/veri_kaynaklari.md` yazıldı. Dört kaynağın (ASSISTments, Eedi Kaggle, Eedi NeurIPS, OpenStax) adresi, lisansı ve projede nasıl kullanıldığı kayıt altında.
- **Bulgular:**
  - ASSISTments'ın açık bir lisansı yok, kullanım koşulları var: veri başkasına verilmez, kod açık olmalı, atıf yapılmalı.
  - Eedi NeurIPS lisansı **doğrulanamadı**. Resmî sayfa açılmadı; bir arama sonucu CC BY-NC-ND 4.0 diyor.
- **Açık nokta:** Eedi NeurIPS lisansı doğrulanana kadar task 3-4 soru resimleri soru bankasında kullanılmamalı.
- **Kimi etkiliyor:** İrem — NFR-06'nın doğrulama yöntemi "`.gitignore` + `doc/veri_kaynaklari.md`" olarak güncellenebilir.

## 2026-11-24 — Eedi NeurIPS: çoktan seçmeli G/S ve çeldirici olasılıkları (WBS 5.5)

- **Ne yapıldı:** `src/data_prep/eedi_neurips_guess_slip.py` yazıldı. Eedi NeurIPS 2020 task 1-2'den 1.513 kesir sorusu ve 1,18 milyon cevap alındı. Beceri başına en fazla 60.000 cevaplık öğrenci örneğiyle pyBKT çalıştırıldı. Veri Git'te değil, çıktılar `data/interim/` klasöründe.
- **Sonuç (çoktan seçmeli G/S):** G 0,39–0,42; S 0,13–0,18; altı becerinin hepsi makul. Görülmemiş öğrencilerde AUC 0,68–0,71. Bu değerler Simülatör A'ya bağlandı (`MC_GUESS_SLIP`): alıştırmalar artık Eedi G/S'siyle, testler ASSISTments G/S'siyle çalışıyor. L0 ve T ASSISTments'tan alınıyor.
- **Çeldirici yoğunlaşması:** En az 50 yanlış cevabı olan 1.151 soruda, en sık seçilen yanlış şık yanlış cevapların ortanca %47'sini alıyor (rastgele seçimde %33). Onaylı metindeki %48 ile tutarlı. Aradaki küçük fark soru seçimi kuralından kaynaklanıyor: bu sefer birden fazla beceriye etiketli sorular çıkarıldı ve yalnızca 6 beceri tutuldu. Soru ve şık bazında olasılıklar `eedi_neurips_celdirici.csv` dosyasında; yanılgı katmanı (FR-15) için hazır.
- **Ek bulgu:** Task 3-4'te görselleri olan 139 kesir sorusu var (`data/images/`). Soru bankası açığı için ek kaynak olabilir; lisans koşulları kontrol edilmeli.
- **Sıradaki adım:** 5.2 soru bankası (S1, S2, S4, S5'te eksik sorular, bkz. 5.4 kaydı).

## 2026-11-24 — Kaggle Eedi kesir soruları ve yanılgı sayımı (WBS 5.4)

- **Ne yapıldı:** Kaggle "Eedi – Mining Misconceptions in Mathematics" verisi indirildi (Seray'ın hesabıyla, Git'te değil). `src/data_prep/eedi_kaggle_fractions.py` betiği S1–S6 kesir sorularını Eedi SubjectId'ye göre seçiyor, yanlış şıkların yanılgı etiketlerini sayıyor ve görsel olabilecek soruları işaretliyor. Çıktılar `data/interim/` klasörüne yazılıyor (Git'e girmiyor).
- **Sonuç:** 1.869 sorudan 103'ü kesir sorusu; 87'si görselsiz. Yanlış şıkların %77'sinde yanılgı etiketi var (101 farklı yanılgı).

  | Beceri | Soru | Görselsiz |
  |---|---|---|
  | S1 | 5 | 3 |
  | S2 | 13 | 8 |
  | S3 | 28 | 26 |
  | S4 | 14 | 12 |
  | S5 | 16 | 12 |
  | S6 | 27 | 26 |

- **Açık nokta (risk):** İP1 başarı ölçütü beceri başına en az 20 öğretim maddesi istiyor. S1, S2, S4 ve S5 bunun altında kalıyor. Seçenekler: (a) ekip, Eedi'deki yanılgı etiketlerini kullanarak eksik soruları yazar (onaylı metin ekip tarafından hazırlanan soruya izin veriyor); (b) yakın konular eklenir (ör. 227 "Simplifying Fractions" → S1, 7 soru). Ekip kararı gerekli.
- **Not:** Görsel işareti sezgisel, elle kontrol edilmeli. Ön ve son test kısa cevaplı ve ekip tarafından yazılacağı için bu sayılar yalnızca öğretim havuzunu etkiliyor.
- **Kimi etkiliyor:** Elifnaz (içerik) ve 5.2 soru bankası.
- **Sıradaki adım:** 5.5 Eedi NeurIPS'ten çoktan seçmeli G/S; ardından 5.2 soru bankası.

## 2026-11-24 — Simülatör A, ilk sürüm (WBS 6.2)

- **Ne yapıldı:** BKT tabanlı Simülatör A yazıldı (`src/core/simulator_a_bkt.py`). Ortamın `StudentModel` arayüzüne uyuyor (`reset`, `answer`). Parametreler 6.1'deki pyBKT sonuçları. 12 birim testi eklendi (`tests/test_simulator_a_bkt.py`).
- **Öğrenci tipleri (öneri):** ortalama, hızlı öğrenen (T×2), yavaş öğrenen (T×0,5), düşük ön bilgili (L0×0,5), tahminci (G ve S ×1,5). Sayı onaylı metinde sabit değil: devir notu ve WBS 5 diyor, FR listesi v4 ise 4 diyor. Ekipçe karar verilmeli; `PROFILES` sözlüğünden kolayca değişir.
- **Varsayımlar (kodda "ASSUMPTION" diye işaretli):**
  - İpucu, çözümlü örnek ve konu anlatımı için ek öğrenme olasılığı çarpan × T olarak alındı; varsayılan çarpan 1 (0,5–2 aralığı, WBS 6.4).
  - Zor soruda G yarıya iniyor, S 1,5 katına çıkıyor.
  - Çoktan seçmeli G/S Eedi'den (5.5) gelene kadar kısa cevap değerleri kullanılıyor.
  - Yanılgı katmanı henüz yok (FR-15, 2. dönem). Bu yüzden geri bildirim eylemi maskeli kalıyor.
- **Kontrol:** 60 adımlık sabit müfredatla 1.000 öğrenci üzerinde ortalama g_norm: ortalama 0,28; hızlı 0,36; yavaş 0,18; düşük ön bilgili 0,40; tahminci 0,18. Tipler beklenen yönde ayrışıyor.
- **Kimi etkiliyor:** İrem — ortamda iki bağlantı eksik:
  1. Alıştırma dışı eylemlerde `student_model.teach(beceri, eylem)` çağrılmalı. Şu an ipucu ve örnek öğrenciyi etkilemiyor.
  2. Oturum başında ve sonunda `expected_test_score()` ile `pretest_score` ve `_post_test_score` doldurulmalı (FR-22). Şu an son test puanı hiç atanmadığı için ödül hep 0.
  - Ayrıca `bkt_params=list(ASSISTMENTS_BKT_PARAMS)` verilirse BKT izleyicisi gerçek parametrelerle çalışır; `bkt_tracker.py`'yi değiştirmeye gerek yok.
- **Not:** Testler gerçek pytest/gymnasium ile değil, bu Mac'te geçici bir taklit ortamla çalıştırıldı (18/18 geçti). Ekipte biri `pytest` ile bir kez çalıştırmalı.
- **Sıradaki adım:** 5.5 Eedi NeurIPS'ten çoktan seçmeli G/S.

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
