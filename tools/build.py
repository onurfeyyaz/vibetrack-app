#!/usr/bin/env python3
"""Vibe Track tanitim sitesini uretir: index.html (EN) ve tr/index.html (TR).

    python3 tools/build.py

Her metin bir iddiadir. Kaynaklari:
  - canli App Store 2.2 aciklamasi (ASC, 14 yerel ayar)
  - uygulama kodu (149 mood / 16 aile: moods.json, uygulamanin kendi listesinden)
Mock ekran rakamlari metne GIRMEZ.
"""
import html, json, re, subprocess, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

APP_ID = "6737136337"
SITE = "https://onurfeyyaz.github.io/vibetrack-app/"
# App Store Connect > Analytics > Acquisition > Campaigns > "Generate Campaign Link"
# ekranindaki provider token. Bos kalirsa link kampanyasiz gider (calisir,
# yalnizca kaynak sayilmaz). Tarif: docs/kampanya-linki.md
PT = ""

# GoatCounter site kodu: https://<GC_CODE>.goatcounter.com (cerezsiz sayim).
# Bos birakilirsa analitik scripti hic eklenmez. Tarif: docs/analitik.md
GC_CODE = "vibetrack-app"

def store_url(ct: str) -> str:
    base = f"https://apps.apple.com/app/apple-store/id{APP_ID}"
    if not PT:
        return f"https://apps.apple.com/app/id{APP_ID}"
    return f"{base}?pt={PT}&ct={ct}&mt=8"

# ---------------------------------------------------------------- icons
CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
SHIELD = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l7.5 3v5.5c0 4.6-3.2 8.3-7.5 9.5-4.3-1.2-7.5-4.9-7.5-9.5V6L12 3z"/><path d="M8.8 12.2l2.2 2.2 4.3-4.4"/></svg>'
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v12m0 0l-5-5m5 5l5-5M5 20h14"/></svg>'

# ---------------------------------------------------------------- strings
FAMILIES = [  # (raw, EN, TR, renk) — sayilar moods.json'dan sayiliyor
    ("joy", "Joy", "Neşe", "yellow"), ("energy", "Energy", "Enerji", "orange"),
    ("calm", "Calm", "Sakinlik", "mint"), ("gratitude", "Gratitude", "Şükran", "green"),
    ("affection", "Affection", "Sevgi", "pink"), ("confidence", "Confidence", "Özgüven", "indigo"),
    ("focus", "Focus", "Odak", "blue"), ("creativity", "Creativity", "Yaratıcılık", "purple"),
    ("connection", "Connection", "Bağ", "teal"), ("neutral", "Neutral", "Nötr", "gray"),
    ("anxiety", "Anxiety", "Kaygı", "purple"), ("sadness", "Sadness", "Üzüntü", "blue"),
    ("anger", "Anger", "Öfke", "red"), ("stress", "Stress", "Stres", "orange"),
    ("fatigue", "Fatigue", "Yorgunluk", "brown"), ("shame", "Shame", "Utanç", "pink"),
]

EN = dict(
    lang="en", og_locale="en_US", home_path="", other_lang="tr", other_lang_label="Türkçe",
    badge_lang="en-us",
    meta_title="Vibe Track — a mood tracker with 149 ways to say how you are",
    meta_desc="Log a mood in seconds with 149 moods in 16 families. See how your sleep and tags move with your mood, keep a streak with friends, and keep your notes out of analytics. Free on iPhone.",
    skip="Skip to content", nav_label="Main", footer_label="Footer",
    cta_short="Get the app",
    badge_alt="Download Vibe Track on the App Store",
    hero_eyebrow="Mood tracker for iPhone",
    hero_h1=" ways to say <em>how you are.</em>",
    hero_lede="Log a mood in seconds. Over time, Vibe Track shows you which parts of your life your mood actually moves with.",
    qr_note="Scan with your iPhone camera",
    hero_fine="Free to download. Premium is optional.",
    chip_1="Works fully without an account", chip_2="Notes never sent to analytics", chip_3="No countdowns, ever",
    cloud_eyebrow="149 moods · 16 families",
    cloud_h2="Five faces can't hold a <em>Tuesday.</em>",
    cloud_lede="Most trackers give you a handful of smileys. Vibe Track gives you the words — so “fine” can finally become <em>restless</em>, <em>proud</em> or <em>quietly hopeful</em>.",
    cloud_sr="Vibe Track includes 149 moods, from happy and calm to anxious and exhausted.",
    cloud_count="Every mood here is one you can log in the app.",
    atlas_eyebrow="Emotion Atlas",
    atlas_h2="Your vocabulary, <em>on a map.</em>",
    atlas_lede="Sixteen families, filled in by the moods you've already logged. No quiz, no setup — the map grows as you write.",
    corr_eyebrow="Correlations",
    corr_h2="See why your better days <em>were better.</em>",
    corr_lede="Vibe Track lines your mood up against your sleep and your own tags, and shows you the difference in plain numbers from your own days.",
    corr_t1="<strong>Sleep</strong> from Apple Health — read only if you connect it",
    corr_t2="<strong>Your tags</strong> — whatever you choose to track",
    corr_t3="Patterns in your own entries — <strong>not a diagnosis</strong>",
    prog_eyebrow="Progress, gently",
    prog_h2="Rest whenever <em>you need to.</em>",
    prog_lede="Levels, weekly quests, streaks and badges keep you coming back. A skipped week costs you nothing — there are no countdowns.",
    prog_t1="<strong>Levels and weekly quests</strong> for showing up",
    prog_t2="<strong>Streak badges</strong> count your best run, so a break doesn't undo them",
    prog_t3="<strong>A weekly summary</strong> of how it went",
    fr_eyebrow="Friends",
    fr_h2="Together — a total that <em>only ever grows.</em>",
    fr_lede="Add a friend and keep a streak together. Miss a day and nothing is subtracted; the shared total only moves up.",
    fr_t1="<strong>Share an entry</strong> when you want to — and only then",
    fr_t2="Send a <strong>heart or a hug</strong> back",
    fr_t3="<strong>Ask for strength anonymously</strong> on a hard day",
    ch_eyebrow="Chapters &amp; PDF",
    ch_h2="A month, in a few <em>honest lines.</em>",
    ch_lede="Chapters turn a stretch of your life into something you can look back on. Need to bring it to a session? Export a clean PDF.",
    ch_t1="<strong>Your notes stay out</strong> of the PDF unless you put them in",
    ch_t2="<strong>CSV export</strong> of all your entries is free, always",
    pv_eyebrow="Privacy",
    pv_h2="Nothing you write goes to <em>our analytics.</em>",
    pv_lede="A mood journal only works if you can be honest in it. So we drew the line where it matters.",
    pv_site_note="This website sets no cookies. Visits are counted anonymously with GoatCounter, which never stores your IP address.",
    pv_1="Your notes are never sent to analytics",
    pv_2="Works with no account at all",
    pv_3="Apple Health is read only if you connect it",
    pv_4="Fewer offers on a hard week — decided on your phone",
    pv_5="Delete your account any time from Settings",
    pr_eyebrow="Pricing",
    pr_h2="Free to keep. <em>Premium to go deeper.</em>",
    pr_lede="Everything you need to log every day is free, with no time limit.",
    pr_free="Free", pr_free_price="$0",
    pr_pro_price="$4.99/mo · $29.99/yr",
    free_list=["One-tap logging with notes and tags", "149 moods and the Emotion Atlas", "List and calendar views",
               "Levels, weekly quests, streaks and badges", "Weekly summary", "Friends and the leaderboard",
               "CSV export", "Works without an account"],
    pro_list=["Correlations with sleep and tags", "PDF to bring to a session", "Chapters",
              "Cloud backup", "Search notes and pick any date range", "No 280-character note limit"],
    pr_legal="Prices in US dollars; they may vary by region and are shown in your currency on the App Store. Subscriptions renew automatically unless cancelled at least 24 hours before the end of the period. Manage or cancel any time in your Apple ID settings.",
    faq_eyebrow="Questions", faq_h2="Good to <em>know.</em>",
    faq=[
        ("Do I need an account?", "No. Vibe Track works fully without an account. An account is only needed for things that involve other people or the cloud, such as friends and backup."),
        ("Who can read my notes?", "Your notes are never sent to analytics. If you add friends, they see the entries you choose to share, plus your level and whether you're a member."),
        ("Is Vibe Track a medical app?", "No. Vibe Track is not a medical service and does not diagnose anything. What it shows are patterns in your own entries. If you are in crisis, please contact your local emergency services."),
        ("What does Premium cost, and how do I cancel?", "$4.99 a month or $29.99 a year (prices may vary by region). You can cancel any time in your Apple ID subscription settings; you keep everything you've logged."),
        ("Can I take my data with me?", "Yes. CSV export of all your entries is free. You can also delete your account from Settings."),
    ],
    close_h2="Start with how you are <em>today.</em>",
    close_p="One tap. One word that fits. That's the whole first step.",
    close_cta="Get Vibe Track — free",
    sticky_sub="Mood tracker · Free on iPhone",
    f_privacy="Privacy", f_terms="Terms of Use", f_support="Support", f_contact="Contact",
    f_medical="Vibe Track is not a medical service and does not diagnose. In an emergency, contact your local emergency services.",
    f_tm="Apple, the Apple logo, iPhone and App Store are trademarks of Apple Inc., registered in the U.S. and other countries.",
)

TR = dict(
    lang="tr", og_locale="tr_TR", home_path="tr/", other_lang="en", other_lang_label="English",
    badge_lang="tr-tr",
    meta_title="Vibe Track — nasıl olduğunu söylemenin 149 yolu",
    meta_desc="16 aileden 149 duyguyla saniyeler içinde kayıt al. Uykunun ve etiketlerinin ruh halinle nasıl değiştiğini gör, arkadaşlarınla birlikte seri tut; notların analitiğe gitmez. iPhone'da ücretsiz.",
    skip="İçeriğe geç", nav_label="Ana menü", footer_label="Alt menü",
    cta_short="Uygulamayı indir",
    badge_alt="Vibe Track'i App Store'dan indir",
    hero_eyebrow="iPhone için duygu takibi",
    hero_h1=" yolla söyle: <em>nasılsın?</em>",
    hero_lede="Ruh halini saniyeler içinde kaydet. Zamanla Vibe Track, ruh halinin hayatının hangi parçalarıyla birlikte değiştiğini gösterir.",
    qr_note="iPhone kameranla tara",
    hero_fine="İndirmesi ücretsiz. Premium isteğe bağlı.",
    chip_1="Hesapsız tam çalışır", chip_2="Notlar analitiğe gitmez", chip_3="Geri sayım yok, hiç",
    cloud_eyebrow="149 duygu · 16 aile",
    cloud_h2="Beş surat bir <em>salıyı</em> taşıyamaz.",
    cloud_lede="Çoğu uygulama birkaç surat verir. Vibe Track kelimeleri verir — “idare eder” sonunda <em>huzursuz</em>, <em>gururlu</em> ya da <em>sessizce umutlu</em> olabilir.",
    cloud_sr="Vibe Track'te mutlu ve sakinden kaygılı ve bitkine kadar 149 duygu var.",
    cloud_count="Buradaki her duyguyu uygulamada kaydedebilirsin.",
    atlas_eyebrow="Duygu Atlası",
    atlas_h2="Sözlüğün, <em>bir haritada.</em>",
    atlas_lede="On altı aile, zaten kaydettiğin duygularla doluyor. Test yok, kurulum yok — harita sen yazdıkça büyür.",
    corr_eyebrow="Korelasyonlar",
    corr_h2="Neden iyi günlerin <em>iyiydi.</em>",
    corr_lede="Vibe Track ruh halini uykunla ve kendi etiketlerinle yan yana koyar; farkı kendi günlerinden, sade rakamlarla gösterir.",
    corr_t1="<strong>Uyku</strong> Apple Health'ten — yalnızca bağlarsan okunur",
    corr_t2="<strong>Etiketlerin</strong> — takip etmek istediğin her şey",
    corr_t3="Kendi kayıtlarındaki örüntüler — <strong>teşhis değil</strong>",
    prog_eyebrow="Nazik ilerleme",
    prog_h2="Dinlen, <em>ihtiyacın olduğu her an.</em>",
    prog_lede="Seviyeler, haftalık görevler, seriler ve rozetler seni geri getirir. Atladığın hafta sana hiçbir şeye mal olmaz — geri sayım yok.",
    prog_t1="Gelmenin karşılığı <strong>seviyeler ve haftalık görevler</strong>",
    prog_t2="En iyi serini sayan <strong>seri rozetleri</strong> — ara vermek onları silmez",
    prog_t3="Haftanın nasıl geçtiğine dair <strong>haftalık özet</strong>",
    fr_eyebrow="Arkadaşlar",
    fr_h2="Birlikte — <em>yalnızca büyüyen</em> ortak bir toplam.",
    fr_lede="Bir arkadaş ekle, birlikte seri tutun. Bir gün kaçırırsan hiçbir şey eksilmez; ortak toplam yalnızca artar.",
    fr_t1="İstediğinde — ve yalnızca o zaman — <strong>kaydını paylaş</strong>",
    fr_t2="Karşılığında <strong>kalp ya da sarılma</strong> gönder",
    fr_t3="Zor bir günde <strong>anonim olarak güç iste</strong>",
    ch_eyebrow="Bölümler ve PDF",
    ch_h2="Bir ay, birkaç <em>dürüst satırda.</em>",
    ch_lede="Bölümler hayatının bir dönemini dönüp bakabileceğin bir şeye çevirir. Seansa götürmen mi gerekiyor? Temiz bir PDF al.",
    ch_t1="<strong>Notların PDF'e girmez</strong>, sen eklemedikçe",
    ch_t2="Bütün kayıtlarının <strong>CSV dışa aktarımı</strong> her zaman ücretsiz",
    pv_eyebrow="Gizlilik",
    pv_h2="Yazdığın hiçbir şey <em>analitiğe gitmez.</em>",
    pv_lede="Bir duygu günlüğü ancak içinde dürüst olabilirsen işe yarar. Bu yüzden çizgiyi önemli olan yere çektik.",
    pv_site_note="Bu web sitesi çerez kullanmaz. Ziyaretler GoatCounter ile anonim sayılır; IP adresin saklanmaz.",
    pv_1="Notların asla analitiğe gönderilmez",
    pv_2="Hiç hesap açmadan çalışır",
    pv_3="Apple Health yalnızca bağlarsan okunur",
    pv_4="Zor haftada teklifler azalır — karar telefonunda verilir",
    pv_5="Hesabını istediğin an Ayarlar'dan sil",
    pr_eyebrow="Fiyat",
    pr_h2="Ücretsiz kullan. <em>Derine inmek için Premium.</em>",
    pr_lede="Her gün kayıt tutmak için gereken her şey ücretsiz, süre sınırı yok.",
    pr_free="Ücretsiz", pr_free_price="0 $",
    pr_pro_price="4,99 $/ay · 29,99 $/yıl",
    free_list=["Not ve etiketle tek dokunuşla kayıt", "149 duygu ve Duygu Atlası", "Liste ve takvim görünümü",
               "Seviyeler, haftalık görevler, seriler ve rozetler", "Haftalık özet", "Arkadaşlar ve sıralama",
               "CSV dışa aktarma", "Hesapsız çalışır"],
    pro_list=["Uyku ve etiketlerle korelasyonlar", "Seansa götürülecek PDF", "Bölümler",
              "Bulut yedek", "Notlarda arama ve dilediğin tarih aralığı", "280 karakter not sınırı yok"],
    pr_legal="Fiyatlar ABD doları cinsindendir; bölgeye göre değişebilir ve App Store'da kendi para biriminle gösterilir. Abonelik, dönem bitiminden en az 24 saat önce iptal edilmezse otomatik yenilenir. Apple Kimliği ayarlarından istediğin an yönetebilir ya da iptal edebilirsin.",
    faq_eyebrow="Sorular", faq_h2="Bilmekte <em>fayda var.</em>",
    faq=[
        ("Hesap açmam gerekiyor mu?", "Hayır. Vibe Track hesapsız tam çalışır. Hesap yalnızca başka insanları ya da bulutu içeren şeyler için gerekir: arkadaşlar ve yedek gibi."),
        ("Notlarımı kim okuyabilir?", "Notların asla analitiğe gönderilmez. Arkadaş eklersen, paylaşmayı seçtiğin kayıtları, seviyeni ve üye olup olmadığını görürler."),
        ("Vibe Track tıbbi bir uygulama mı?", "Hayır. Vibe Track tıbbi hizmet değildir ve teşhis koymaz. Gösterdiği şey kendi kayıtlarındaki örüntülerdir. Kriz anındaysan lütfen yerel acil servislere (Türkiye'de 112) başvur."),
        ("Premium ne kadar, nasıl iptal ederim?", "Ayda 4,99 $ ya da yılda 29,99 $ (bölgeye göre değişebilir). Apple Kimliği abonelik ayarlarından istediğin an iptal edebilirsin; kaydettiğin her şey sende kalır."),
        ("Verilerimi alıp götürebilir miyim?", "Evet. Bütün kayıtlarının CSV dışa aktarımı ücretsiz. Hesabını da Ayarlar'dan silebilirsin."),
    ],
    close_h2="Bugün nasıl olduğunla <em>başla.</em>",
    close_p="Bir dokunuş. Tam oturan bir kelime. İlk adımın hepsi bu.",
    close_cta="Vibe Track'i ücretsiz indir",
    sticky_sub="Duygu takibi · iPhone'da ücretsiz",
    f_privacy="Gizlilik", f_terms="Kullanım Koşulları", f_support="Destek", f_contact="İletişim",
    f_medical="Vibe Track tıbbi hizmet değildir ve teşhis koymaz. Acil durumda yerel acil servislere (112) başvur.",
    f_tm="Apple, Apple logosu, iPhone ve App Store, Apple Inc.'in ABD'de ve diğer ülkelerde tescilli ticari markalarıdır.",
)

# ---------------------------------------------------------------- helpers
def tr_cap(s: str) -> str:
    if not s: return s
    first = {"i": "İ", "ı": "I"}.get(s[0], s[0].upper())
    return first + s[1:]

def mood_rows(moods, lang):
    items = []
    for m in moods:
        name = m["en"] if lang == "en" else tr_cap(m["tr"])
        emoji = m.get("e") or ""
        cls = "mood" if emoji else "mood noemoji"
        inner = (f'<i>{emoji}</i>' if emoji else "") + html.escape(name)
        items.append(f'<span class="{cls}" style="--c:var(--{m["c"]})">{inner}</span>')
    # 3 sira, aileler karisik dursun diye adim 3 ile dagit
    rows = [items[i::3] for i in range(3)]
    out = []
    for i, r in enumerate(rows):
        body = "".join(r)
        rev = " rev" if i == 1 else ""
        dur = [150, 170, 160][i]
        out.append(f'<div class="row{rev}" style="--dur:{dur}s">{body}<span class="dup" style="display:contents">{body}</span></div>')
    return "\n    ".join(out)

def family_cards(moods, lang):
    counts = {}
    for m in moods: counts[m["f"]] = counts.get(m["f"], 0) + 1
    assert sum(counts.values()) == 149 and len(counts) == 16, counts
    out = []
    for raw, en, tr, c in FAMILIES:
        out.append(f'<div class="fam" style="--c:var(--{c})"><b>{counts[raw]}</b><span>{en if lang=="en" else tr}</span></div>')
    return "".join(out)

SHOT_W = (400, 760)
def shot(lang, n, alt, eager=False):
    base = ROOT / "assets" / "shots" / lang
    files = sorted((base / "light").glob(f"{n}-*-{SHOT_W[0]}.webp"))
    if not files:
        sys.exit(f"eksik ekran: {lang}/light/{n}")
    stem = files[0].name.rsplit("-", 1)[0]
    def srcset(theme):
        return ", ".join(f"{{root}}assets/shots/{lang}/{theme}/{stem}-{w}.webp {w}w" for w in SHOT_W)
    sizes = "(max-width: 899px) 74vw, 360px"
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="{srcset("dark")}" sizes="{sizes}">'
            f'<img src="{{root}}assets/shots/{lang}/light/{stem}-{SHOT_W[0]}.webp" srcset="{srcset("light")}" sizes="{sizes}" '
            f'width="1206" height="2622" alt="{html.escape(alt)}" {load}></picture>')

def qr_svg(url):
    """segno varsa uretir ve src/qr/ altina onbellege yazar; yoksa onbellekten okur
    (segno: pip install segno). Onbellek URL'ye gore adlanir, PT degisirse yeniden uretilir."""
    import hashlib
    cache = SRC / "qr" / (hashlib.sha1(url.encode()).hexdigest()[:12] + ".svg")
    try:
        import segno, io
    except ImportError:
        if cache.exists():
            return cache.read_text()
        sys.exit("segno yok ve QR onbellegi bos: pip install segno")
    buf = io.BytesIO()
    segno.make(url, error="m").save(buf, kind="svg", xmldecl=False, svgns=True, border=0, dark="#171528", omitsize=True)
    svg = buf.getvalue().decode()
    cache.parent.mkdir(exist_ok=True)
    cache.write_text(svg)
    return svg

ALTS = {
    "en": dict(hero="Vibe Track mood picker with mood families", atlas="Emotion Atlas screen",
               corr="Insights screen comparing mood with sleep and tags", prog="Home screen with level, streak and weekly quests",
               friends="Friends screen with a shared streak", chapters="Chapters screen"),
    "tr": dict(hero="Vibe Track duygu seçici ekranı", atlas="Duygu Atlası ekranı",
               corr="Ruh halini uyku ve etiketlerle karşılaştıran içgörü ekranı", prog="Seviye, seri ve haftalık görevlerin olduğu ana ekran",
               friends="Ortak serinin göründüğü arkadaşlar ekranı", chapters="Bölümler ekranı"),
}

def build(t, moods, ver):
    lang = t["lang"]
    root = "" if lang == "en" else "../"
    v = dict(t)
    v.update(
        root=root, site=SITE, app_id=APP_ID, ver=ver, year=str(date.today().year),
        canonical=SITE + t["home_path"],
        other_lang_href=(root + ("tr/" if lang == "en" else "")) or "./",
        store_url_nav=store_url(f"web-{lang}-nav"), store_url_hero=store_url(f"web-{lang}-hero"),
        store_url_close=store_url(f"web-{lang}-closing"), store_url_sticky=store_url(f"web-{lang}-sticky"),
        qr_svg=qr_svg(store_url(f"web-{lang}-qr")),
        check=CHECK, shield=SHIELD, apple=ARROW,
        mood_rows=mood_rows(moods, lang), family_cards=family_cards(moods, lang),
        free_items="".join(f"<li><span>{x}</span></li>" for x in t["free_list"]),
        pro_items="".join(f"<li><span>{x}</span></li>" for x in t["pro_list"]),
        gc_script=(f'<script data-goatcounter="https://{GC_CODE}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>' if GC_CODE else ""),
        faq_items="".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in t["faq"]),
    )
    a = ALTS[lang]
    v.update(
        shot_hero=shot(lang, "01", a["hero"], eager=True), shot_atlas=shot(lang, "07", a["atlas"]),
        shot_corr=shot(lang, "02", a["corr"]), shot_prog=shot(lang, "03", a["prog"]),
        shot_friends=shot(lang, "04", a["friends"]), shot_chapters=shot(lang, "05", a["chapters"]),
    )
    v["jsonld"] = json.dumps({
        "@context": "https://schema.org", "@type": "MobileApplication",
        "name": "Vibe Track", "operatingSystem": "iOS", "applicationCategory": "HealthApplication",
        "description": t["meta_desc"], "url": SITE + t["home_path"], "inLanguage": lang,
        "image": SITE + "assets/img/icon-512.png",
        "installUrl": f"https://apps.apple.com/app/id{APP_ID}",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "publisher": {"@type": "Organization", "name": "Wipa Studio"},
    }, ensure_ascii=False)

    tpl = (SRC / "template.html").read_text()
    # iki tur: shot() icinde {root} var
    def fill(s):
        return re.sub(r"\{\{(\w+)\}\}", lambda m: str(v[m.group(1)]) if m.group(1) in v else sys.exit(f"eksik anahtar: {m.group(1)}"), s)
    out = fill(tpl).replace("{root}", root)
    left = re.findall(r"\{\{\w+\}\}", out)
    assert not left, left
    return out

def main():
    moods = json.loads((SRC / "moods.json").read_text())
    css = (SRC / "styles.css").read_text()
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets" / "styles.css").write_text(css)
    import hashlib
    ver = hashlib.sha1(css.encode()).hexdigest()[:8]
    (ROOT / "index.html").write_text(build(EN, moods, ver))
    (ROOT / "tr").mkdir(exist_ok=True)
    (ROOT / "tr" / "index.html").write_text(build(TR, moods, ver))
    print("✓ index.html, tr/index.html")

if __name__ == "__main__":
    main()
