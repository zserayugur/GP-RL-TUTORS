# İş günlüğü (worklog)

Bu klasör, ekipte kimin ne yaptığını tek yerde tutmak için var. Amaç karışıklığı önlemek: biri bir işi bitirdiğinde ya da bir karar aldığında, diğerleri (ve onların yapay zekâ asistanları) bunu buradan görür.

## Dosyalar

| Dosya | Kim yazar |
|---|---|
| `seray.md` | Zeynep Seray Uğur (Üye 1: veri, simülatörler, baseline'lar, LinUCB) |
| `irem.md` | İrem Nur Yavuz (Üye 2: ortam, PPO, mimari) |
| `elifnaz.md` | Elifnaz Köseoğlu (Üye 3: LLM öğrenci, içerik, dokümantasyon) |

Herkes yalnızca **kendi dosyasına** yazar. Böylece aynı satırı iki kişi değiştirmez ve Git'te çakışma (merge conflict) olmaz.

## Ne zaman yazılır?

- Bir iş bittiğinde ya da önemli bir ara sonuç çıktığında
- Bir karar alındığında (ör. "H = 60", "λ = 0,003")
- Bir şey değiştiğinde ve başkasını etkilediğinde (ör. bir fonksiyonun adı, bir dosyanın yeri, bir parametre)
- Push etmeden önce: aynı commit'e günlük kaydı da girsin

## Kayıt biçimi

En yeni kayıt **en üste** yazılır.

```markdown
## 2026-11-24 — BKT kalibrasyonu (WBS 6.1)

- **Ne yapıldı:** pyBKT ile S1–S6 için L0, T, G, S bulundu; öğrenci bazlı 5 katlı çapraz doğrulama yapıldı.
- **Sonuç / dosyalar:** `doc/...`, `src/...` (veri dosyaları Git'te değil, Drive'da)
- **Kararlar / açık noktalar:** S6'da T çok düşük, hocaya sorulacak.
- **Kimi etkiliyor:** İrem — `src/core/bkt_tracker.py` içindeki yer tutucu parametreler değişecek.
- **Sıradaki adım:** WBS 6.2, beş öğrenci tipli simülatör.
```

## Kurallar

- Kısa yaz: 3–6 madde yeterli.
- Gizli bilgi yok: TC kimlik no, IBAN, telefon, e-posta, şifre, API anahtarı yazılmaz.
- Veri dosyası eklenmez. ASSISTments ve Eedi verileri Git'e konmaz (lisans gereği); yalnızca dosyanın adı ve nerede durduğu yazılır.
- Kaynak gösterilecekse yalnızca doğrulanmış kaynak yazılır; uydurma kaynak yok.
- Yapay zekâ asistanı kullanıyorsan ona `ai/prompts/worklog_prompt.md` dosyasındaki istemi ver. O da her iş sonunda bu klasöre kayıt ekler.
