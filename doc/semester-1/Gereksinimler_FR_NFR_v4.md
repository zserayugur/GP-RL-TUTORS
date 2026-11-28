# Gereksinimler ve İzlenebilirlik (WBS 4.1) — v7

*Do RL Tutors Generalize? · Hazırlayan: İrem · v7, 25 Kasım 2026 · Temel: İzlenebilirlik taslağı v3 (18 Kasım),
onaylı TÜBİTAK metni, GP-1 iş planı v5, Seray'ın Beceri Grafiği ve Use Case belgesi v2, Karar Dokümanı
(Gözlem/Eylem/Ödül), 18 Kasım danışman toplantısı tutanağı, 24 Kasım danışman görüşmesi (FR-22 onayı),
Seray'ın 25 Kasım'da bulduğu "son eylem" eksikliği, 25 Kasım açık-nokta gözden geçirmesi (§2).*

## v6 → v7 değişikliği: 13 maddelik açık liste gözden geçirildi

Bkz. §2: hangi maddelerin zaten bir karar dokümanına dayandığı (N=3, yanılgı sınıfı=3, H=60, RAG, S1→S3,
son test uzunluğu — hocaya yalnızca bilgi verilecek), hangilerinin ekip tarafından şimdi karara bağlandığı
(ayrıcalıklı öğretmen statüsü, NFR-13, 2. dönem WBS) ve hangilerinin gerçekten hocadan yeni bir karar
beklediği (maliyet/λ, maske eşiği + güvenlik kuralları, izleyici tasarımı, dil) ayrıştırıldı. Maske eşiğine
eklenecek "güvenlik kuralları" henüz tanımlanmadı, ayrıca ele alınacak.

## v5 → v6 değişikliği: "son eylem" gözleme eklendi

Seray, onaylı metnin (Yöntem §2.1) "genel düzeyde son eylem... kullanılacaktır" şartını kontrol ederken,
ortamın son eylemi yalnızca maskeleme için tuttuğunu, gözleme hiç koymadığını fark etti. `FR-21` satırına
ve `src/core/fraction_tutor_env.py`'ye işlendi (bkz. aşağıdaki tablo ve `doc/architecture/Mimari_Tasarim_v2.md`).

## v4 → v5 değişikliği: FR-22 onaylandı

**24 Kasım 2026'daki danışman görüşmesinde hoca, FR-22'deki ödül yaklaşımını onayladı** ("ödülle uyumlu
olmalı"): beklenen kazanç − maliyet ödülü (R = g_norm − Σc(a)), eğitimde A/B simülatörlerinde ön/son test
puanının gizli durumdan **beklenen değer** olarak hesaplanması (ayrıcalıklı bilgiyle eğitim) ve gizli durumun
politikanın gözlemine hiçbir zaman verilmemesi — onaylı metinde yazan yaklaşımın aynısı. Koşul: WBS 8.4'teki
ablasyonlar (beklenen vs. örneklemeli ödül dahil) ve gözlem/maske tasarımı bu ana ödül tanımıyla tutarlı
kalmalı. *Not: Tam tarih/toplantı kaydı ekip tutanağına da işlenmeli; bu belgeye İrem'in aktarımıyla girildi.*

## v3 → v4 değişiklikleri ve gerekçeleri

v3'te "ekip onayı bekleyenler" (§4.3) olarak işaretlenmiş üç maddeden ikisi, 18 Kasım'dan bu yana alınan
kararlarla artık çözülmüş durumda. Üçüncüsü ve hocaya sorulacak diğer maddeler **hâlâ açık**, değiştirilmedi.

| Madde | v3 durumu | Güncel durum | Dayanak |
|---|---|---|---|
| FR-38 (oturum bitişi, H) | Öneri, H değeri açık | **Kabul edildi**, H = 60 | Ekip kararı 18 Kasım (gece), Seray'ın UC-03/UC-04 belgesinde H=60 zaten kullanılıyor |
| FR-39 (eylem dağılımı / ödül sömürüsü raporu) | Öneri | **Kabul edildi** | Seray'ın UC-06/UC-07 belgesinde zaten atıflı kullanılıyor; onaylı metnin reward-hacking kontrol gerekliliğiyle uyumlu |
| NFR-13 (Docker + README) | Öneri | **Değişmedi** — hâlâ ekip/hoca onayı bekliyor | Hiçbir belgede onaylandığına dair kayıt yok |
| FR-24 / FR-27 kabul kriteri | BKT-PFA karışımı koşulu eksik | **Eklendi**: "BKT, PFA ve BKT-PFA karışımı" eğitim koşullarını kapsamalı | Onaylı TÜBİTAK metni, Yöntem §2.1: "...PFA ASSISTments verisiyle...", B. Çıktı/Şekil 1: eğitim simülatörleri "BKT, PFA ve BKT-PFA karışımı" |
| FR-22 (ödül) | Onay bekliyor | **✅ Onaylandı (hoca, 24 Kasım)** — yukarıya bkz. | Danışman görüşmesi, 24 Kasım 2026 |
| Gözlem boyutu (FR-21) | — | Not eklendi: **143 boyut** (Elifnaz'ın formal tanım belgesi esas) | 18 Kasım ekip kararı: gözlem boyutu ve "bitir" maskesinde Elifnaz'ın değerleri esas alınır (Zeynep'in karar dokümanındaki ~117 boyut / ilk 5 adım değil) |

## 1. İzlenebilirlik tablosu (FR → RQ / WBS / UC)

Okuma: ✓ tamamlandı. * işaretli WBS numaraları 2. dönem paketleridir (bkz. §1.3). Sarı olarak işaretlenen satırlar
v4'te kabul edilmiştir (FR-38, FR-39); NFR-13 hâlâ öneri durumunda.

### Veri ve kalibrasyon

| ID | Gereksinim (kısa) | RQ / H | WBS | UC | Dönem |
|---|---|---|---|---|---|
| FR-01 | ASSISTments ön işleme | RQ1 | 5.3 ✓ | — | 1 |
| FR-02 | BKT parametre kestirimi | RQ1, H1 | 6.1 | — | 1 |
| FR-03 | AFM/PFA parametre kestirimi | RQ2 | D2-11* | — | 2 |
| FR-04 | Tahmin/sürçme ve çeldirici olasılıkları (Eedi) | RQ2, RQ4 | 5.5 | — | 1–2 |

### İçerik ve soru bankası

| ID | Gereksinim (kısa) | RQ / H | WBS | UC | Dönem |
|---|---|---|---|---|---|
| FR-05 | Beceri grafiği (6 beceri) | RQ1 | 5.1 ✓ | UC-01 | 1 |
| FR-06 | Ayrı öğretim / test havuzları | RQ1 | 5.2, 6.3 | UC-02, UC-04 | 1 |
| FR-07 | 4 şık + yanılgı kodu | RQ4 | 5.2, 5.4 | UC-03 | 1 |
| FR-08 | Kısa cevap normalizasyonu | RQ1, RQ4 | 6.3 | UC-02, UC-04 | 1 |
| FR-09 | İçerik yükleme (form / JSON / CSV) | — (destek) | D2-14* | UC-08 | 2 |
| FR-10 | Yüklenen içeriği doğrulama | — (destek) | D2-14* (5.2 betiği) | UC-08 | 2 |
| FR-11 | İçerik denetimi ve onay | — (destek) | D2-14* | UC-09, UC-10 | 2 |
| FR-12 | Sürümlü havuz anlık görüntüsü | RQ1–RQ3 | 7.3* | UC-05 | 1–2 |
| FR-32 | Öğretim içeriği deposu (ipucu, örnek, …) | RQ1, H5 | 5.2*, 6.4* | UC-03 | 1–2 |

### Öğrenci simülatörleri

| ID | Gereksinim (kısa) | RQ / H | WBS | UC | Dönem |
|---|---|---|---|---|---|
| FR-13 | Simülatör A (BKT), 4 öğrenci tipi | RQ1 | 6.2 | — | 1 |
| FR-14 | Simülatör B (AFM/PFA) | RQ2 | D2-11* | — | 2 |
| FR-15 | Yanılgı katmanı (şık seçimi) | RQ2, RQ4 | D2-11* (5.5 verisi) | — | 2 |
| FR-16 | Simülatör C (LLM öğrenci) | RQ2, RQ4 | D2-12* | — | 2 |
| FR-17 | Test sorusu öğrenme yaratmaz | RQ1 | 6.3 | UC-02 | 1 |

### Öğretim ortamı (Gymnasium)

| ID | Gereksinim (kısa) | RQ / H | WBS | UC | Dönem |
|---|---|---|---|---|---|
| FR-18 | Gymnasium arayüzü (reset/step) | RQ1 | 7.1 | — | 1 |
| FR-19 | Eylem uzayı Discrete(37) | RQ1, H5 | 7.1, 6.4* | UC-03 | 1–2 |
| FR-20 | Eylem maskesi — **uygulandı** (ön koşul eşiği 0,6; yanılgı geri bildirimi; tekrarlayan konu anlatımı) | RQ1 | 7.1 | UC-03 | 1 |
| FR-21 | Gözlem vektörü (143 boyut, Elifnaz'ın formal tanımı esas) — **düzeltme (25 Kasım, Seray'ın bulduğu eksiklik):** "son eylem" artık gözlemde (önceden yalnızca maskeleme için tutuluyordu, onaylı metin Yöntem §2.1'in gerektirdiği gibi gözleme eklenmemişti) | RQ1, RQ2 | 7.1 | UC-02, UC-03 | 1 |
| FR-22 | Ödül (beklenen kazanç − maliyet) **— onaylandı (hoca, 24 Kasım)** | RQ1 | 7.1, 8.4* | — | 1 |
| FR-33 | Oturum adım kaydı | RQ1 (analiz) | 7.3*, 9.1* | UC-03, UC-07 | 1 |
| FR-34 | Politika tarafı BKT izleyicisi — **uygulandı**: `src/core/bkt_tracker.py`, yalnızca gözlenen cevaplardan hesaplıyor (simülatör içi duruma erişmiyor); L0/T/G/S değerleri WBS 6.1 (Seray, pyBKT) tamamlanana kadar yer tutucu | RQ1, RQ2 | 7.1* (6.1 param.) | UC-03 | 1 |
| FR-38 | Oturum bitişi: "bitir" veya H adım → son test. **Kabul edildi, H = 60** (ekip kararı, 18 Kasım) | RQ1 | 7.1 | UC-03, UC-04 | 1 |

### Politikalar, deneyler ve analiz

| ID | Gereksinim (kısa) | RQ / H | WBS | UC | Dönem |
|---|---|---|---|---|---|
| FR-23 | Baseline politikalar (3); ayrıcalıklı öğretmen (kâhin) **baseline değil**, yalnızca üst sınır referansı — Adv formülüne girmez (**ekip kararı, 25 Kasım**) | RQ1, H1 | 7.2 | UC-05 | 1 |
| FR-24 | LinUCB ve MaskablePPO; **kabul kriteri: eğitim simülatörleri BKT, PFA ve BKT-PFA karışımını kapsar** | RQ1, H1 | 8.1, 8.2 | UC-05 | 1 |
| FR-25 | Tek komutla deney (yapılandırma + tohum) | RQ1–RQ3 | 7.3, 8.3 | UC-05 | 1 |
| FR-26 | Çapraz simülatör matrisi, transfer açığı | RQ2, H2 | D2-13* | UC-05, UC-06 | 2 |
| FR-27 | Domain randomization ve ablasyonlar; **kabul kriteri: BKT-PFA karışımını da kapsar** | RQ3, H3, H5 | 8.4, 6.4 · DR: D2-13* | UC-05, UC-06 | 1–2 |
| FR-35 | LLM yanılgı tutarlılığı ölçümü | RQ4, H4 | D2-12* | UC-06 | 2 |
| FR-40 | LLM öğrenci şık seçimi ↔ Eedi gerçek dağılımı (onaylı metinde var) | RQ2, RQ4 | D2-12* | UC-06 | 2 |
| FR-36 | İstatistiksel raporlama | RQ1–RQ4 | 8.3* | UC-06 | 1 |
| FR-39 | Eylem dağılımı ve ödül sömürüsü raporu. **Kabul edildi** | RQ1, RQ2 | 8.3*, 9.1 | UC-06, UC-07 | 1–2 |

### Dashboard ve kullanıcılar

| ID | Gereksinim (kısa) | RQ / H | WBS | UC | Dönem |
|---|---|---|---|---|---|
| FR-28 | Oturum tekrar oynatma | RQ1 (inceleme) | 9.1 | UC-07 | 1 |
| FR-29 | Sonuç karşılaştırma ve dışa aktarma | RQ2 | D2-13* | UC-06 | 2 |
| FR-30 | Kullanıcı ve rol yönetimi | — (destek) | D2-14* | UC-11 | 2 |
| FR-31 | Öğrenci demo arayüzü | — (destek) | D2-14* | UC-01–UC-04 | 2 |
| FR-37 | Giriş ve rol tabanlı erişim | — (destek) | D2-14* | UC-01–UC-11 | 2 |

## 1.1 Fonksiyonel olmayan gereksinimler

| ID | Gereksinim | İlgili FR | WBS | Doğrulama |
|---|---|---|---|---|
| NFR-01 | Tekrarlanabilirlik | FR-25, FR-33 | 7.3 | Aynı deney iki kez çalıştırılır |
| NFR-02 | Bilgi sızıntısı yok | FR-21, FR-22, FR-34 | 7.1, 7.3 | Gözlem birim testi — **uygulandı**: `tests/test_fraction_tutor_env.py` (11 test, hepsi geçiyor) |
| NFR-03 | Test kapsamı ≥ %70 | — | 7.3 | Kapsam raporu |
| NFR-04 | Performans (100 bin adım < 30 dk) | FR-24 | 8.2 | İlk PPO denemesinde ölçüm |
| NFR-05 | LLM bütçesi ve önbellek | FR-16, FR-26 | D2-12* | Önbellek isabet raporu |
| NFR-06 | Lisans (Eedi, OpenStax) | FR-32 | 1.3, 5.4 | .gitignore kontrolü — **uygulandı** (bkz. repo `.gitignore`) |
| NFR-07 | Gizlilik | — | Tümü (TÜBİTAK 2.8) | İstem şablonu incelemesi |
| NFR-08 | Sürümleme (Git) | FR-25 | 1.3 | Deney kaydında commit kimliği |
| NFR-09 | Kapsam kısıtı (yeni beceri yok, görselsiz) | FR-10 | 5.4 | Doğrulama betiği |
| NFR-10 | Genişletilebilirlik (ortak simülatör arayüzü) | FR-18 | 7.1 · test D2-11* | Sahte simülatörle entegrasyon testi — **uygulandı**: `FakeStudentModel` (`tests/test_fraction_tutor_env.py`) |
| NFR-11 | Kullanılabilirlik (dashboard) | FR-28, FR-29 | 9.1 · D2-13* | Ekip dışı kullanım denemesi |
| NFR-12 | Güvenlik (hash, sunucu tarafı yetki) | FR-30, FR-37 | D2-14* | Yetkisiz istek testi |
| NFR-13 | Kurulum ve belgeleme: **README zorunlu, Docker isteğe bağlı** (**ekip kararı, 25 Kasım**) — uygulandı: kök `README.md`'de kurulum adımları | FR-25 | 1.3, 7.3 | Temiz makinede README ile kurulum denemesi |

## 1.2 Ters kontrol: her RQ'yu karşılayan gereksinimler

| RQ / Hipotez | Soru | Gereksinimler | Dönem |
|---|---|---|---|
| RQ1 / H1 | RL eğitmeni kendi simülatöründe baseline'ları geçer mi? | FR-01, 02, 05–08, 13, 17–25, 32–34, 36, 38, 39 | 1 |
| RQ2 / H2 | Simülatör değişince ne kadar performans kaybolur? | FR-03, 04, 14–16, 21, 26, 29, 34, 36, 39, 40 | 2 |
| RQ3 / H3, H5 | Domain randomization transfer açığını azaltır mı? | FR-13, 14, 19, 26, 27, 32, 36 | 1 (ablasyon) – 2 (DR) |
| RQ4 / H4 | LLM öğrenci atanan yanılgıyı korur mu? | FR-04, 07, 08, 15, 16, 35, 36, 40 | 2 |

Kontrol sonucu: Her RQ en az bir veri, bir simülatör, bir deney ve bir analiz gereksinimine bağlı. RQ'ya
bağlanmayan FR'ler (FR-09–11, FR-30, FR-31, FR-37) hocanın istediği kullanıcı ve ekranları karşılayan destek
gereksinimleridir.

## 1.3 2. dönem için önerilen WBS paketleri

| Paket | İçerik | Kapsadığı gereksinimler |
|---|---|---|
| D2-11 | Simülatör B (AFM/PFA) ve yanılgı katmanı | FR-03, FR-14, FR-15, NFR-10 |
| D2-12 | Simülatör C (LLM öğrenci) ve RQ4 ölçümü | FR-16, FR-35, FR-40, NFR-05 |
| D2-13 | Çapraz simülatör deneyleri, domain randomization, sonuç paneli | FR-26, FR-27 (DR), FR-29, NFR-11 |
| D2-14 | İçerik yönetimi, kullanıcılar ve öğrenci demo arayüzü | FR-09–11, FR-30, FR-31, FR-37, NFR-12 |

Numaralar öneridir; GP-2 iş planı yazılırken kesinleşecek — **ekip kararı: GP-1'de taslak kalır** (bkz. §2.3).

## 2. Açık noktaların durumu (25 Kasım, İrem'in sentezi)

13 maddelik açık liste gözden geçirildi: hangilerinin zaten bir karar dokümanına/onaylı metne dayandığı,
hangilerinin gerçekten hocadan yeni bir karar beklediği ayrıştırıldı.

### 2.1 Hocaya sorulacaklar (gerçekten açık, yeni karar gerekiyor)

- ~~**FR-22 ödülü**~~ — ✅ 24 Kasım'da onaylandı.
- **Eylem maliyetleri ve λ:** TÜBİTAK metni "pilotla belirlenip sabit tutulacak" diyor ama λ'yı hiç
  belirtmiyor. Öneri: sabit bir ana değer (λ = 0,003) + duyarlılık analizi (λ ∈ {0; 0,0015; 0,003; 0,006}).
  Literatüre dayalı tek bir değer mi, yoksa bu duyarlılık analizi yeterli mi?
- **Maske eşiği (0,6) ve ek güvenlik kuralları:** Eşiğin kendisi öneri olarak duruyor; kilitlenmeyi
  önleyecek ek kurallar henüz netleşmedi — **ayrıca ele alınacak.**
- **BKT izleyicisini gözleme koymak:** Onaylı metinde zaten bu şekilde (MLP + izleyici), alternatifi
  (RecurrentPPO) metinde yok. Öneri: mevcut tasarım korunsun, izleyicisiz gözlem ayrı bir ablasyon olarak
  eklensin. Bu çerçeveyi onaylıyor musunuz?
- **İçerik ve arayüz dili:** Hiçbir belgede karar yok. Öneri: deneyler İngilizce yürütülsün (kaynaklar zaten
  İngilizce). Onaylıyor musunuz?

### 2.2 Hocaya bilgi verilecekler (ekip kararı var, onay değil bilgilendirme yeterli)

- **Son N cevap = 3:** Karar Dokümanı'nda zaten var ("son 3 cevap", 18 boyut); kodda da varsayılan bu
  (`LAST_N_ANSWERS_DEFAULT = 3`).
- **Yanılgı sözlüğü = 3 sınıf + "diğer":** Karar Dokümanı'nda zaten var ("becerinin en sık 3 yanılgısı,
  one-hot"); kodda da bu şekilde uygulandı (`NUM_MISCONCEPTION_CLASSES = 3` + "yok/diğer" durumu).
- **Son test uzunluğu = beceri başına 2 soru:** Öneri olarak zaten vardı, yeterli kabul edildi.
- **S1 → S3 oku:** Seray'ın belgesinde veri desteğinin zayıf olduğu zaten açıkça yazılı; alan gerekçesiyle
  (ortak payda = denk kesir gerekir) korunuyor, oklu/oksuz ablasyonla kontrol edilecek.
- **RAG kapsamı:** 17 Kasım'da ekip kararı zaten alındı (yalnızca PoC/çevrimdışı/etiket tabanlı); değişiklik yok.
- **H = 60:** 18 Kasım ekip kararı; değişiklik yok.

### 2.3 Ekip kararları (yeni karar verildi, 25 Kasım)

- **Ayrıcalıklı öğretmen (kâhin):** Karar Dokümanı'ndaki "üst sınır, yalnızca karşılaştırma" ifadesi
  netleştirildi: **baseline değil**, Adv(π,k) formülündeki "en güçlü baseline" hesabına **girmez**, yalnızca
  iç kontrol/üst sınır referansı olarak raporlanır. FR-23'e işlendi.
- **NFR-13 (kurulum/belgeleme):** **README zorunlu, Docker isteğe bağlı.** Kök dizindeki `README.md`'ye
  kurulum adımları eklendi (bkz. repo).
- **2. dönem WBS paketleri (D2-11–14):** GP-1'de taslak olarak kalır; kesin hâli GP-2 iş planında
  belirlenecek.
