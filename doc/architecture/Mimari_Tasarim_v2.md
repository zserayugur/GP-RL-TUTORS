# Sistem Mimarisi ve Ödünleşimler (WBS 4.3) — v3

*Do RL Tutors Generalize? · Hazırlayan: İrem · v3, 24 Kasım 2026 · Temel: İzlenebilirlik/Mimari taslağı v3 (18 Kasım),
onaylı TÜBİTAK metni (Şekil 1), Karar Dokümanı (Gözlem/Eylem/Ödül), Seray'ın Beceri Grafiği ve Use Case belgesi v2,
24 Kasım danışman görüşmesi (FR-22 onayı).*

## v2 → v3 değişikliği: FR-22 onaylandı

**24 Kasım 2026'da hoca, Katman 3'teki ödül tasarımını (FR-22) onayladı** ("ödülle uyumlu olmalı"): eğitimde
A/B simülatörlerinde gizli durumdan hesaplanan beklenen kazanç − maliyet (ayrıcalıklı bilgiyle eğitim), gizli
durumun gözleme asla verilmemesi. Koşul: WBS 8.4 ablasyonları ve gözlem/maske tasarımı bu ana ödül tanımıyla
tutarlı kalmalı. Aşağıdaki katman tablosu ve ödünleşim tablosu buna göre güncellendi.

## v1(taslak v3 içindeki) → v2 değişiklikleri

- **Gözlem boyutu netleştirildi:** Katman 3 ve FR-21 artık **143 boyut** olarak anılıyor (18 Kasım ekip kararı:
  gözlem boyutu ve "bitir" maskesinde Elifnaz'ın formal RL tanımı esas alınır). Zeynep'in karar dokümanındaki
  ~117 boyut / ilk 5 adım maskesi **artık geçerli değil**; bu, uygulanan `src/core/fraction_tutor_env.py`
  iskeletiyle de tutarlı (143-dim `Box`, `MIN_STEPS_BEFORE_FINISH = 6`).
- **Katman 4 kabul kriterine not eklendi:** Eğitim simülatörleri yalnızca A/B değil, **BKT-PFA karışımını** da
  kapsamalı (onaylı metin, Yöntem §2.1 ve B. Şekil 1 — "BKT, PFA ve BKT-PFA karışımı").
- **NFR-02 (bilgi sızıntısı) artık doğrulanmış durumda:** Birim testi yazıldı ve geçiyor
  (`tests/test_fraction_tutor_env.py`, 11 test — gizli durumun `reset()`/`step()` çıktısına hiçbir biçimde
  sızmadığını doğrular).
- **Ayrıcalıklı öğretmenin statüsü değişmedi** — hâlâ hocaya sorulacak (bkz. §5).

## 1. Genel yaklaşım

Mimari, TÜBİTAK Şekil 1'i izler: veri ve içerik katmanı üç öğrenci simülatöründen ayrılır; simülatörler ortak yanıt
şemasıyla Gymnasium ortamına bağlanır. Politika hangi simülatörün kullanıldığını görmez, yalnızca ortak gözlem
vektörünü alır ve aynı eylem uzayından seçim yapar. Böylece RQ2'de ölçülen kayıp arayüz farkından değil öğrenci
modelinden kaynaklanır.

## 2. Katmanlar

| Katman | Sorumluluk | Gereksinimler |
|---|---|---|
| 1 · Alan, veri ve içerik | Beceri grafiği (yapılandırma dosyası), SQLite soru/içerik havuzu, ASSISTments ve Eedi ön işleme betikleri. Öğretmen içeriği taslak → onay bekliyor → onaylandı/reddedildi durumlarından geçer; deneyler onaylı havuzun sürümlü anlık görüntüsüyle çalışır. | FR-01–12, FR-32 |
| 2 · Öğrenci simülatörleri | A (BKT), B (AFM/PFA), C (LLM, yalnızca test). Hepsi aynı reset/step/response sözleşmesini ve ortak yanıt şemasını (doğruluk, seçilen şık, yanılgı kodu) uygular. | FR-13–17 |
| 3 · Gymnasium ortamı | POMDP: 37 eylem, eylem maskesi, **143 boyutlu** yalnızca gözlenebilir gözlem, R = g_norm − Σ c(a) (FR-22, **onaylandı — hoca, 24 Kasım**). Oturum "bitir" eylemiyle (6. adımdan sonra açılır) veya **H = 60** adımda biter, ardından son test yapılır. | FR-18–22, FR-33, FR-38 |
| 4 · Eğitmen politikaları | 3 baseline, LinUCB, MaskablePPO (SB3). Eğitim simülatörleri **BKT, PFA ve BKT-PFA karışımını** kapsar. Politika tarafındaki BKT izleyicisi tahmini ustalığı gözlemden hesaplar; gizli duruma erişmez. | FR-23, FR-24, FR-34 |
| 5 · Deney ve değerlendirme | Yapılandırma + tohum ile tek komut; çapraz simülatör matrisi, DR ve K0–K3 ablasyonları; bootstrap GA, Wilcoxon + Holm, A12; eylem dağılımı ve ödül sömürüsü raporu. | FR-25–27, FR-35, FR-36, FR-39, FR-40 |
| 6 · Arayüz (Streamlit) | Araştırmacı paneli (oturum kaydından tekrar oynatma, matris), öğrenci demo, içerik yükleme/onay ekranları; giriş ve rol tabanlı erişim. | FR-09–11, FR-28–31, FR-37 |

Politika hangi simülatörün kullanıldığını görmez: A, O ve R üç simülatörde aynı; yalnızca T ve Z değişir.
Gizli durum yalnızca eğitim ödülünde ve UC-07 inceleme ekranında kullanılır.

## 3. Tasarım kararları ve ödünleşimler

| Karar | Kazanç | Bedel / risk |
|---|---|---|
| Ortak gözlem/eylem/ödül; yalnızca T ve Z değişir | RQ2'deki kayıp arayüz farkına değil öğrenci modeline bağlanabilir. | LLM'in zengin çıktısı (güven, serbest metin) politikaya verilemez. |
| Eğitimde beklenen puan ödülü (gizli durumdan) | Ölçüm gürültüsü eğitim sinyalinden çıkar. | Ayrıcalıklı bilgi; sızıntı riskine karşı ödül ve gözlem kodu ayrı modülde (**doğrulandı**: `_build_observation` gizli duruma erişmiyor, birim testiyle kontrol edildi). **Onaylandı** (hoca, 24 Kasım — FR-22); WBS 8.4 ablasyonları bu ödül tanımıyla tutarlı kalmalı. |
| BKT izleyicisi politika tarafında | Kısmi gözlemlenebilirlikte geçmişin özeti; maske gizli duruma dayanmaz. | İzleyici yanılırsa maske gereksiz eylemleri kapatabilir. |
| SQLite + sürümlü anlık görüntü | Tek dosya, kurulum yok; deneyler sonradan eklenen içerikten etkilenmez. | Çok kullanıcılı eşzamanlı yazma sınırlı (demo için yeterli). |
| Streamlit arayüz | Python ekibi için hızlı; 1. dönem 9.1 ile uyumlu. | Rol tabanlı erişim ve çok ekranlı akış için ek iş gerekir (2. dönem). |
| Yerel LLM + önbellek | Maliyet sınırlı, tekrarlanabilir yanıtlar. | Yerel modelin kalitesi büyük modellerden düşük olabilir. |

## 4. Genişletme kuralı

Yeni simülatör ortak sözleşmeyi uygulayınca mevcut politikalarla test edilir (NFR-10 — bkz. `FakeStudentModel`
entegrasyon testi). Yeni eylem eklenirse içerik kaydı, simülatör etkisi, gözlem sayacı, maske, maliyet ve birim
testleri birlikte güncellenir.

## 5. Hâlâ açık olan noktalar

- ~~**FR-22 ödülü**~~ — ✅ 24 Kasım'da onaylandı, bkz. §0 ve Katman 3.
- **Ayrıcalıklı öğretmen:** Baseline değil, yalnızca üst sınır referansı olarak mı tutulsun?
- **S1 → S3 oku:** Veri desteği zayıf; alan gerekçesi yeterli mi?
- **2. dönem WBS:** D2-11–14 GP-1'de taslak kalsın, kesin hâli GP-2'de mi belirlensin?
