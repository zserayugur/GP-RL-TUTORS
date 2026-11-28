# Danışman toplantısı notları (Kasım sonu)

*Not alan: Seray · Notların paylaşıldığı tarih: 28 Kasım 2026 · Toplantı tarihi: ____ (Seray dolduracak)*
*Notlar toplantıda hızlıca alındığı için düzenlenerek yazıldı. Yorum içeren yerler "yorum" diye işaretli.*

## 1. LLM öğrenci (Simülatör C) — sorumlu: Elifnaz

- Daha güçlü, yeni bir yerel LLM kullanılacak.
- Önce kesir/matematik eğitimine özel (domain-specific) bir LLM aranacak. Bulunamazsa öğrenci simülasyonuna uygun bir dataset bulunup küçük bir yerel model eğitilecek (fine-tuning).
- Model, sorulara öğrenci gibi mantıklı (ve atanan yanılgıya uygun) cevaplar verecek şekilde eğitilmeli.
- Uygun dataset'lerin yapıları (structure) incelenecek.
- Modelin sorulara nasıl cevap verdiğini gösteren bir deneme izi (trace) çıkarılacak.
- "Tutor emülatörü" gibi hazır bir araç ve varsa benchmark'lar araştırılacak; kendi kesir alanımızda benchmark denemesi yapılacak.
- Bize uygun iyi bir survey makalesi bulunup kaynak gösterilecek.
- "Tracing ile karşılaştırma yapılacak." *Yorum:* LLM öğrencinin cevaplarını knowledge tracing (BKT) modelinin beklentisiyle karşılaştırmak olarak anlaşıldı; teyit edilmeli.
- **Mevcut durum (Elifnaz'ın iş günlüğü):** Yerel Ollama `qwen3:4b` ile küçük bir yanılgı pilotu yapıldı (6/6 beklenen şık); fine-tuning için 8 örneklik deneme dosyası hazırlandı; GPU erişimi bekleniyor.

## 2. Algoritma kararları — sorumlu: İrem

- Eylem uzayına bağlı olarak algoritma (PPO, DQN vb.) ve eylem uzayının kesikli (discrete) mi sürekli (continuous) mi olacağı kararı verilmeli ve gerekçelendirilmeli.
  - *Yorum:* Onaylı TÜBİTAK metninde ve ortamda eylem uzayı kesikli: `Discrete(37)` (6 beceri × 6 müdahale + "bitir"). Her eylem "hangi beceri + hangi müdahale" seçimi olduğu için kesikli doğal seçim; MaskablePPO kesikli eylem ve maskeyi destekliyor.
- LLM için fine-tuning mi yapılacak, yoksa hazır bir dataset/model mi bulunacak? Karar verilmeli.

## 3. GP-1 raporu — sorumlu: ekip

- 80–90 sayfalık, okunabilir ve kesintisiz tek bir belge.
- İçerik:
  - Use case diyagramları, use case açıklama tabloları ve senaryoları
  - Mockup'lar ve arayüzler
  - Kaba bir tasarım (design)
  - Birkaç üst düzey sequence diyagramı
  - "Neler yaptık": ekip olarak yapılanlar
- Bunlar için iş paketi çıkarılacak: `doc/semester-1/GP1_rapor_is_paketleri_taslak.md`.

## Onaylı metinle karşılaştırma (kapsam)

| Konu | Onaylı TÜBİTAK metni | Toplantı | Not |
|---|---|---|---|
| Eylem uzayı | Kesikli, 37 eylem | Karar ve gerekçe istendi | Değişiklik gerekmiyor; gerekçe yazılmalı |
| DQN | "Kaynak elverirse genişletme" | Algoritma seçeneği olarak anıldı | Çekirdeğe alınırsa kapsam değişikliği olarak kaydedilmeli |
| LLM fine-tuning | "Kaynak elverirse genişletme" | Domaine özel model yoksa eğitilmesi istendi | Kapsam değişikliği olarak kaydedilmeli |
| LLM yalnızca test için | Politikalar LLM üzerinde eğitilmez | — | Fine-tuning LLM öğrencinin kendisi için; bu kural değişmiyor |
