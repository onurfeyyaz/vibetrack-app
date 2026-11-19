# App Store kampanya linki (`pt` jetonu)

Sitedeki her "İndir" düğmesi ayrı bir `ct` (kampanya) adıyla gider:
`web-en-hero`, `web-en-nav`, `web-en-sticky`, `web-en-closing`, `web-en-qr` (TR için `web-tr-…`).
App Store Connect bu adları **yalnızca `pt` (provider token) da linkte varsa** sayar.
`pt` olmadan linkler çalışır, sadece kaynak raporu boş kalır.

## `pt` nasıl alınır (bir kez)

1. https://appstoreconnect.apple.com → **Apps** → **Vibe Track**.
2. Üstte **Analytics** sekmesi → solda **Acquisition** → **Campaigns**.
3. Sağ üstte **Generate Campaign Link** düğmesi.
4. Campaign alanına herhangi bir şey yaz (ör. `web`) → oluşan linkte `pt=123456` kısmını kopyala.
   Bu sayı hesaba özeldir, gizli değildir (her kampanya linkinde açıkça görünür).

## Siteye işlemek

1. `tools/build.py` içinde `PT = ""` satırını `PT = "123456"` yap.
2. `python3 tools/build.py`
3. Commit + push. Rapor, ilk indirmelerden 1–2 gün sonra Campaigns ekranında görünür.

## Görselleri yenilemek

VibeTrack deposunda:

    SIM="iPhone 17 Pro" LANGS="en tr" THEMES="dark light" scripts/store-capture.sh

Sonra bu depoda:

    python3 tools/prep_assets.py && python3 tools/build.py
