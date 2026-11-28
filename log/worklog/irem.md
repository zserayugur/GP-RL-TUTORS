# İş günlüğü — İrem

En yeni kayıt en üstte. Biçim için `README.md` dosyasına bak.

## 2026-11-25 — Açık nokta listesi (13 madde) gözden geçirildi, bazıları karara bağlandı

- **Ne yapıldı:** FR/NFR ve mimari belgelerindeki "hocaya sorulacaklar" listesindeki 13 madde tek tek
  incelendi: hangilerinin zaten Karar Dokümanı/onaylı metinde cevabı olduğu (N=3, yanılgı sınıfı=3+diğer,
  H=60, RAG, S1→S3, son test uzunluğu — hocaya yalnızca bilgi verilecek), hangilerinin ekip tarafından şimdi
  karara bağlanabileceği, hangilerinin gerçekten hocadan yeni karar beklediği ayrıştırıldı.
- **Sonuç / dosyalar:** `Gereksinimler_FR_NFR_v4.md` (v7), `Mimari_Tasarim_v2.md` (v5), kök `README.md`
  (NFR-13 kararı gereği kurulum adımları eklendi).
- **Kararlar / açık noktalar:**
  - **Ekip kararı:** Ayrıcalıklı öğretmen (kâhin) baseline değil, Adv formülüne girmez. NFR-13: README
    zorunlu, Docker isteğe bağlı. 2. dönem WBS paketleri GP-1'de taslak kalır.
  - **Hâlâ hocaya sorulacak:** eylem maliyetleri/λ, maske eşiği (0,6) + tanımlanmamış "iki güvenlik kuralı"
    (henüz netleşmedi, ayrıca ele alınacak), BKT izleyicisi tasarımının onayı, içerik/arayüz dili.
- **Kimi etkiliyor:** —
- **Sıradaki adım:** Maske eşiğine eklenecek güvenlik kurallarının netleştirilmesi; hocayla görüşmede bu
  4 maddenin cevaplanması.

## 2026-11-25 — Simülatör A'nın gerçek BKT parametreleri politika izleyicisine bağlandı

- **Ne yapıldı:** `bkt_tracker.py`'deki politika tarafı izleyici, varsayılan olarak hâlâ yer tutucu
  uniform parametreleri (L0=0,3 hepsi) kullanıyordu; Seray'ın WBS 6.1'de ASSISTments'tan fitlediği gerçek
  `ASSISTMENTS_BKT_PARAMS` değerleriyle bağlı değildi. `simulator_a_bkt.py`'ye `make_env()` yardımcı
  fonksiyonu eklendi (Simülatör A + gerçek parametrelerle izleyici birlikte kurulur); Seray'ın
  `test_works_inside_env` testi bunu kullanacak şekilde güncellendi.
- **Sonuç / dosyalar:** `src/core/simulator_a_bkt.py` (`make_env`), `tests/test_simulator_a_bkt.py`
  (güncellendi + 1 yeni test). Toplam 40/40 test geçiyor.
- **Kararlar / açık noktalar:** —
- **Kimi etkiliyor:** Seray (kendi testi `make_env()` kullanacak şekilde değişti, davranışı aynı kaldı).
- **Sıradaki adım:** Simülatör B/C hazır olunca benzer bir `make_env()` eklenmesi gerekecek.

## 2026-11-25 — Gözlemde "son eylem" eksikliği düzeltildi (WBS 7.1)

- **Ne yapıldı:** Seray, onaylı TÜBİTAK metninin (Yöntem §2.1: "genel düzeyde son eylem... kullanılacaktır")
  gerektirdiği "son eylem" bilgisinin ortamda yalnızca maskeleme için tutulduğunu, gözleme hiç
  eklenmediğini fark etti. `fraction_tutor_env.py`'de son eylem türü (7: 6 eylem + "bitir") ve
  hedeflediği beceri (6) artık 143 boyutun rezerve kısmından kullanılarak gözleme ekleniyor.
- **Sonuç / dosyalar:** `src/core/fraction_tutor_env.py` (`_encode_last_action`), 3 yeni test
  (`tests/test_fraction_tutor_env.py`). Toplam 39/39 test geçiyor (Seray'ın Simülatör A testleri dahil).
  `doc/semester-1/Gereksinimler_FR_NFR_v4.md` (v6) ve `doc/architecture/Mimari_Tasarim_v2.md` (v4) güncellendi.
- **Kararlar / açık noktalar:** —
- **Kimi etkiliyor:** Elifnaz'ın formal RL tanım belgesi (gözlem 143 boyutun bu alt kırılımını da içermeli).
- **Sıradaki adım:** Elifnaz'ın formal tanım belgesi gelince gözlemdeki geri kalan ~12 rezerve boyutu
  doldurmak.

## 2026-11-24/25 — Ortam iskeleti, BKT izleyicisi, FR/NFR ve mimari tamamlandı (WBS 4.1, 4.3, 7.1)

- **Ne yapıldı:**
  - Gymnasium ortam iskeleti: `Discrete(37)` eylem, `Box(143,)` gözlem, H=60, "bitir" ilk 6 adımda maskeli,
    λ=0,003 maliyet katsayısı.
  - Eylem maskeleri uygulandı: ön koşul (BKT izleyici eşiği 0,6), yanılgı geri bildirimi, tekrarlayan
    konu anlatımı. Havuz tükenmesi maskesi WBS 5.2 bekliyor.
  - Politika tarafı BKT izleyicisi (FR-34) ayrı modülde (`bkt_tracker.py`): yalnızca gözlenen cevaplardan
    hesaplıyor, simülatör iç durumuna erişmiyor (hangi simülatör olursa olsun aynı şekilde çalışır).
  - Gizli durumun gözleme/`info`'ya asla sızmadığını doğrulayan birim testleri yazıldı.
  - FR/NFR izlenebilirlik tablosu (4.1) ve mimari/ödünleşim belgesi (4.3) bitirildi; FR-38, FR-39 kabul
    edildi olarak işaretlendi, BKT-PFA karışımı FR-24/FR-27 kabul kriterine eklendi.
  - **FR-22 ödülü hoca tarafından onaylandı** (24 Kasım, danışman görüşmesi) — belgelere işlendi.
  - GP-1 v5 iş planındaki "five baselines"→"three" ve DQN düzeltmesi için bul-değiştir notu hazırlandı
    (gerçek docx Zeynep'te olduğu için metinden düzenlenemedi, Zeynep'e iletildi).
- **Sonuç / dosyalar:** `src/core/fraction_tutor_env.py`, `src/core/bkt_tracker.py`,
  `tests/test_fraction_tutor_env.py`, `tests/test_bkt_tracker.py`,
  `doc/semester-1/Gereksinimler_FR_NFR_v4.md`, `doc/architecture/Mimari_Tasarim_v2.md`,
  `doc/semester-1/GP1_v5_duzeltmeleri.md`.
- **Kararlar / açık noktalar:** Hâlâ hoca/ekip onayı bekleyenler: ayrıcalıklı öğretmen (kâhin) statüsü,
  S1→S3 ön koşul oku, NFR-13 (Docker+README), içerik/arayüz dili, 2. dönem WBS paketleri (D2-11–14),
  son cevap penceresi N (3 mü 5 mi), yanılgı sözlüğü sınıf sayısı, eylem maliyeti ölçeği/λ.
- **Kimi etkiliyor:** Zeynep (GP-1 v5 düzeltmesini uygulaması gerekiyor), Elifnaz (formal RL tanım
  belgesi 143 boyutun kesin kırılımını belirleyecek).
- **Sıradaki adım:** Yukarıdaki açık maddeler hocayla netleşince belgeleri güncellemek; soru
  havuzu/SQLite şeması Seray'ın WBS 5.2 işi bitince ele alınacak.
