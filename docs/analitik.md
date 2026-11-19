# Site analitiği (GoatCounter)

Site, ziyaretleri ve tıklamaları **GoatCounter** ile sayar.
- Çerez yok.
- IP adresi ve tarayıcı kimliği (User-Agent) diske yazılmaz. Kaynak: goatcounter.com/help/sessions.
- Bu yüzden çerez onay bandı gerekmez.
- Site kodu `tools/build.py` içindeki `GC_CODE` değişkeninde: şu an `vibetrack-app`.
- Panel adresi: https://vibetrack-app.goatcounter.com

## Bir kerelik kurulum (yalnız sen yapabilirsin: hesap açma)

1. https://www.goatcounter.com/signup adresini aç.
2. **Code** alanına `vibetrack-app` yaz.
   - Bu kod alınmışsa başka bir kod seç.
   - Sonra `tools/build.py` içindeki `GC_CODE` değerini o kodla değiştir.
   - `python3 tools/build.py` çalıştır, commit ve push et.
3. **Site domain** alanına `onurfeyyaz.github.io` yaz.
4. E-posta ve şifreyi gir, **Sign up**'a bas. Gelen doğrulama e-postasını onayla.
5. Panelde **Settings → Data collection** aç. **Collect "Individual pageviews"** kapalı kalsın; varsayılanı zaten kapalı.
6. Kendi ziyaretlerini saymamak için kendi tarayıcında bir kez https://onurfeyyaz.github.io/vibetrack-app/#toggle-goatcounter adresini aç. Telefonda da aynısını yap.

Hesap açılmadan gelen istekler kaybolur. Script sitede durur ama sayım hesap açıldığı andan itibaren başlar.

## Ne ölçülüyor

| Panelde görünen | Ne demek |
|---|---|
| `/vibetrack-app/` ve `/vibetrack-app/tr/` | EN ve TR sayfa ziyaretleri (tekil ziyaret, 8 saatlik oturum) |
| Referrers / Campaigns | Ziyaretçinin geldiği yer (`?ref=` ya da `utm_source` kaynağı belirler); `utm_campaign` verilirse Campaigns kutusunda ayrıca görünür |
| Locations, Languages, Systems, Sizes | Ülke, dil, iOS/masaüstü, ekran genişliği |
| `download-hero-en` / `-tr` | Üstteki App Store rozetine tıklama |
| `download-nav-*` | Üst menüdeki "Uygulamayı indir" |
| `download-sticky-*` | Mobilde alttaki sabit çubuk |
| `download-closing-*` | Sayfa sonundaki büyük buton |
| `seen-moods/features/privacy/pricing/faq/closing-*` | Bölüme kadar kaydırma (her yüklemede 1 kez); huni |
| `faq-N-*` | N'inci SSS sorusunun açılması |
| `out-privacy/terms/support/contact-*` | Alt bilgi linkleri |
| `lang-switch-tr-to-en` vb. | Dil değiştirme |

**Toplam indirme tıklaması** = bütün `download-*` olaylarının toplamı.

Bu sayı **tıklamayı** ölçer, **indirmeyi** ölçmez. App Store'a giden ziyaretçinin kaçının uygulamayı indirdiğini site göremez.

**QR taramaları** sayılmaz, çünkü QR doğrudan App Store'a gider. Bunu yalnız `pt` kampanya kodu görür (aşağıda).

## Gerçek indirmeler: App Store tarafı

- **App Store Connect → Analytics → Acquisition → Sources**: "Web Referrer" satırında `onurfeyyaz.github.io` görünür. Site üzerinden Safari'den gelip indirenler burada sayılır. Apple bir eşiğin altındaki sayıları göstermeyebilir.
- **Kampanya bazında** (hangi butondan gelip indirdi) görmek için `pt` kodu gerekir. Tarifi `docs/kampanya-linki.md`'de. Kod eklenince her buton kendi `ct` değeriyle gider (`web-tr-hero` gibi).

## Paylaşım linki ipucu

Bir yerde paylaşırken sonuna kaynak ve kampanya ekle. Örnek: `https://onurfeyyaz.github.io/vibetrack-app/?utm_source=instagram&utm_campaign=lansman`. GoatCounter bunu Campaigns kutusunda ayrı gösterir. Yalnız `?ref=instagram` eklersen kaynak olarak görünür.
