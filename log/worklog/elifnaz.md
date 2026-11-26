# İş günlüğü — Elifnaz

En yeni kayıt en üstte. Biçim için `README.md` dosyasına bak.

## 2026-11-24 — LLM öğrencinin şık yanıtını soru bankasıyla eşleme (FR-40 hazırlığı)

- **Ne yapıldı:** Gösterilen A/B/C/D harfini orijinal soru-şık çiftine eşleyen bağımsız adaptör ve SQLite şemasıyla testler eklendi.
- **Sonuç / dosyalar:** `src/core/llm_choice.py`, `tests/test_llm_choice.py`. Test verisi sentetiktir.
- **Kararlar / açık noktalar:** Belirsiz yanıt yanlış sayılmaz; etiketsiz yanlış yanıta yanılgı uydurulmaz. Yalnızca onaylı, görselsiz, çoktan seçmeli öğretim maddeleri kabul edilir.
- **Kimi etkiliyor:** Seray'ın şeması okunur; İrem'in ortamında değişiklik yoktur.
- **Sıradaki adım:** LLM isteminde kullanılan şık sırasını kaydetmek ve adaptörü model çağrısına bağlamak. Gerçek Eedi karşılaştırması yapılmadı.
- LLM’ye gönderilecek soru ve şıkları hazırlayan fonksiyon eklendi. Cevap anahtarı modele gönderilmiyor, şık sırası eşleme için ayrı saklanıyor. Prompt ve şık eşleme testleri yerelde geçti.
- Sahte modelle soru hazırlama ve şık eşleme birlikte doğrulandı; 8 test geçti.
- Yerel Ollama ve Qwen3 4B ile soru hazırlama, model yanıtı ve şık eşleme akışı uçtan uca doğrulandı. Gerçek model testi dahil 9 test geçti.
- qwen3:4b ile yapılan tek soruluk manuel pilotta, aynı soru ve şık sırası korunarak iki ayrı oturum çalıştırıldı. Normal öğrenci istemi B (5/6), payları ve paydaları ayrı ayrı toplayan öğrenci istemi A (2/5) üretti.
- LLM öğrenciye isteğe bağlı persona parametresi eklendi. Sahte modelle yapılan test, profilin modele iletildiğini ve karıştırılmış şıkların doğru eşlendiğini doğruladı. Yerel çalıştırmada 9 test geçti, isteğe bağlı Ollama testi atlandı.
- qwen3:4b ile Python üzerinden tek soruluk pilot yapıldı. Aynı soru ve şık sırası kullanıldı. Profil verilmediğinde B (5/6), payları ve paydaları ayrı ayrı toplayan öğrenci profiliyle A (2/5) döndü. Profilli ilk çağrı zaman aşımına uğradı; tekrarında yanıt alındı.
 - küçük pilot denemesi Doğru çözme rolü: 3/3 beklenen şık (B, C, B) anılgı rolü: 3/3 beklenen şık (A, A, A)
 ### 2026-11-25 — Ollama yanılgı pilotu
- Model: yerel Ollama `qwen3:4b`.
- Doğru çözme rolünde üç bağımsız denemede beklenen şıklar geldi: B, C, B.
- Payları ve paydaları ayrı ayrı toplama yanılgısı rolünde üç bağımsız denemede beklenen şıklar geldi: A, A, A.
- Bu küçük pilotta 6/6 yanıt beklenen şıkla eşleşti. Sonuçlar yalnızca işlev kontrolüdür; modelin genel başarısını gösteren kapsamlı bir değerlendirme veya fine-tuning sonucu değildir.
## 2026-11-26 — Eedi pilotu ve fine-tuning hazırlığı

- Eedi’de farklı paydalı basit kesirleri toplama becerisine uyan 5 aday soru bulundu. Bunların 4’ünde payları ve paydaları ayrı ayrı toplama yanılgısı etiketliydi; bu dört soru eğitim dışında tutuldu.
- Yerel `qwen3:4b`, netleştirilmiş yanılgı talimatıyla dört pilot soruda da beklenen şıkkı seçti (4/4). İlk soruda önceki talimatla hedef şıkkı seçmemişti. Bu, küçük bir prompt pilotu; fine-tuning sonucu değil. Tek harf biçimi dört sorunun tamamı için doğrulanmadı.
- Pilot dışında aynı yanılgıya uyan 10 aday bulundu. Tek hedef şıkkı olan 8 örnek, eğitim sürecini denemek için yerelde `eedi_sft_smoke.jsonl` dosyasına yazıldı. Ham Eedi dosyaları ve JSONL GitHub’a yüklenmeyecek.
- Fine-tuning başlatılmadı. Yerel bilgisayarda Intel Iris Xe görünüyor; NVIDIA GPU erişimi için haber bekleniyor.
- Devam noktası: GPU erişimi netleşince küçük eğitim denemesini çalıştır. İyileşmeyi ölçmek için dört pilot sorusundan daha geniş, eğitimden ayrı bir test seti hazırla.