# Yapay zekâ asistanı için istem: iş günlüğü

Bu istemi kullandığın yapay zekâ asistanına (Claude, ChatGPT, Copilot, Cursor vb.) oturumun başında yapıştır. Claude Code ve Codex gibi araçlar bunu depodaki `CLAUDE.md` / `AGENTS.md` dosyaları üzerinden kendiliğinden okur.

---

Bu depo "Do RL Tutors Generalize?" bitirme projesinin deposudur (GP-RL-TUTORS). Ekipte üç kişi var: Seray (veri, simülatörler, baseline'lar, LinUCB), İrem (Gymnasium ortamı, PPO, mimari) ve Elifnaz (LLM öğrenci, içerik, dokümantasyon). Bana yardım ederken şu kurallara uy:

1. **Başlamadan önce oku.** `log/worklog/` klasöründeki üç dosyanın (`seray.md`, `irem.md`, `elifnaz.md`) en üstteki kayıtlarını oku. Ekibin son durumunu, kararları ve başkalarının değiştirdiği şeyleri buradan öğren. Başkasının bitirdiği bir işi baştan yapma; bir kararla çelişen bir şey önerirsen bunu açıkça belirt.

2. **İş bitince kayıt ekle.** Bir görevi bitirdiğinde ya da önemli bir karar alındığında, **yalnızca benim dosyama** (`log/worklog/<adım>.md`) en üste yeni bir kayıt ekle. Başkasının dosyasını değiştirme. Biçim:

   ```markdown
   ## YYYY-AA-GG — <kısa başlık> (varsa WBS no)

   - **Ne yapıldı:** ...
   - **Sonuç / dosyalar:** ...
   - **Kararlar / açık noktalar:** ...
   - **Kimi etkiliyor:** ... (yoksa "—")
   - **Sıradaki adım:** ...
   ```

   3–6 kısa madde yeterli. Tarih gerçek bugünün tarihi olsun.

3. **Commit'e dahil et.** Kod ya da belge değişikliğini commit'lerken günlük kaydını da aynı commit'e koy. Böylece push edildiğinde notlar da gider.

4. **Yazmaman gerekenler:**
   - Kişisel ya da gizli bilgi: TC kimlik no, IBAN, telefon, e-posta, şifre, API anahtarı.
   - Veri dosyaları: ASSISTments ve Eedi verileri lisans gereği Git'e konmaz; yalnızca dosyanın adını ve nerede durduğunu yaz (`data/raw/` ve `data/interim/` zaten `.gitignore`'da).
   - Uydurma kaynak: Kaynak yazacaksan yalnızca doğrulanmış olanı yaz; emin değilsen "doğrulanmadı" diye işaretle.

5. **Kapsama sadık kal.** Danışmanın onayladığı TÜBİTAK 2209-A metnindeki kapsamın dışına çıkma. Yeni bir şey önerirsen bunu günlükte "öneri / değişiklik" olarak açıkça işaretle.

6. **Dil.** Günlük kayıtları Türkçe yazılır. Kod, kod yorumları ve İngilizce raporlar İngilizce kalabilir.
