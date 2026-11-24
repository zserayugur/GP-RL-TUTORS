# İş günlüğü — Elifnaz

En yeni kayıt en üstte. Biçim için `README.md` dosyasına bak.

## 2026-11-24 — LLM öğrencinin şık yanıtını soru bankasıyla eşleme (FR-40 hazırlığı)

- **Ne yapıldı:** Gösterilen A/B/C/D harfini orijinal soru-şık çiftine eşleyen bağımsız adaptör ve SQLite şemasıyla testler eklendi.
- **Sonuç / dosyalar:** `src/core/llm_choice.py`, `tests/test_llm_choice.py`. Test verisi sentetiktir.
- **Kararlar / açık noktalar:** Belirsiz yanıt yanlış sayılmaz; etiketsiz yanlış yanıta yanılgı uydurulmaz. Yalnızca onaylı, görselsiz, çoktan seçmeli öğretim maddeleri kabul edilir.
- **Kimi etkiliyor:** Seray'ın şeması okunur; İrem'in ortamında değişiklik yoktur.
- **Sıradaki adım:** LLM isteminde kullanılan şık sırasını kaydetmek ve adaptörü model çağrısına bağlamak. Gerçek Eedi karşılaştırması yapılmadı.
