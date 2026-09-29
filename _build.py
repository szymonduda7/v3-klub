#!/usr/bin/env python3
"""
Generator statycznej strony V3 Klub.

Treść podstron: _src/pages/<plik>.html (zwykły HTML + kilka znaczników {{...}}).
Wspólne rzeczy (head, nagłówek, stopka, NAP, schema, breadcrumbs, grafik)
są tutaj, żeby były identyczne na każdej podstronie.

Uruchom:  python3 _build.py
Wynik:    index.html, <slug>/index.html, sitemap.xml, robots.txt, 404.html,
          assets/css/styles.css, _DO-UZUPELNIENIA.md
"""
import hashlib
import html
import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "_src")

# ============================================================
# KONFIGURACJA: dane firmy (NAP spójny z profilem Google)
# ============================================================
SITE_URL = "https://v3klub.pl"  # TODO: docelowa domena (zmień tu i uruchom build)
BUILD_DATE = date.today().isoformat()

NAZWA = "V3 Centrum Sportowe"
MARKA = "V3 Klub"
ULICA = "Poniatowskiego 24"
KOD = "37-500"
MIASTO = "Jarosław"
WOJ = "podkarpackie"
TEL = "788 463 717"
TEL_E164 = "+48788463717"
TIKTOK = "https://www.tiktok.com/@v3_klub_jaroslaw"
APKA = "https://v3klub.gymmanager.io"
FACEBOOK = ""   # TODO: link do profilu Facebook
INSTAGRAM = ""  # TODO: link do profilu Instagram

_q = "V3+Centrum+Sportowe,+Poniatowskiego+24,+37-500+Jaros%C5%82aw"
MAPS = f"https://www.google.com/maps/search/?api=1&query={_q}"
MAPS_TRASA = f"https://www.google.com/maps/dir/?api=1&destination={_q}"
MAPS_EMBED = f"https://www.google.com/maps?q={_q}&output=embed"

# dzień tygodnia 1 = poniedziałek; "24:00" = północ
GODZINY = {1: ("05:00", "24:00"), 2: ("05:00", "24:00"), 3: ("05:00", "24:00"),
           4: ("05:00", "24:00"), 5: ("05:00", "24:00"), 6: ("06:00", "23:00"),
           7: ("08:00", "22:00")}
DNI = ["", "Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
DNI_EN = ["", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ============================================================
# GRAFIK FIGHT ZONE (obowiązuje od 1 września 2026)
# ============================================================
GRAFIK_OD = "1 września 2026"
DYSCYPLINY = {
    "kickboxing": ("Kickboxing", "/kickboxing-jaroslaw/"),
    "boks": ("Boks", "/boks-jaroslaw/"),
    "mma": ("MMA", "/mma-jaroslaw/"),
    "jujitsu": ("Ju-jitsu (SSW Cobra)", "/mma-jaroslaw/#ju-jitsu-i-samoobrona"),
    "samoobrona": ("Samoobrona / Krav Maga", "/mma-jaroslaw/#ju-jitsu-i-samoobrona"),
    "start": ("Trening wprowadzający", "/grafik/#trening-wprowadzajacy"),
}
def _z(dzien, od, do, nazwa, d, grupa=""):
    return {"dzien": dzien, "od": od, "do": do, "nazwa": nazwa, "d": d, "grupa": grupa}
_pn_sr = lambda dz: [
    _z(dz, "16:00", "16:45", "Kickboxing Kids", "kickboxing", "4–6 lat"),
    _z(dz, "17:00", "17:45", "Kickboxing Start", "kickboxing", "7–10 lat"),
    _z(dz, "17:45", "18:45", "Kickboxing Junior", "kickboxing", "14–18 lat"),
    _z(dz, "18:45", "20:00", "Kickboxing Fight Team", "kickboxing", "grupa zawodnicza"),
    _z(dz, "20:00", "21:15", "Kickboxing dorośli", "kickboxing", "dorośli"),
]
_wt_cz = lambda dz: [
    _z(dz, "16:00", "17:00", "Kickboxing Kadet", "kickboxing", "10–13 lat"),
    _z(dz, "17:00", "19:00", "SSW Cobra Ju-Jitsu", "jujitsu"),
    _z(dz, "19:00", "20:15", "Boks", "boks"),
    _z(dz, "20:15", "21:15", "Samoobrona / Krav Maga", "samoobrona"),
]
GRAFIK = (_pn_sr(1) + _wt_cz(2) + _pn_sr(3) + _wt_cz(4) + [
    _z(5, "17:30", "18:30", "Trening wprowadzający dla nowych", "start"),
    _z(5, "18:30", "20:00", "Kickboxing Fight Team: sparingi", "kickboxing", "grupa zawodnicza"),
    _z(5, "20:00", "21:00", "MMA", "mma"),
    _z(6, "12:00", "13:00", "MMA", "mma"),
])

# ============================================================
# NAWIGACJA I PODSTRONY
# ============================================================
NAV = [
    ("silownia-jaroslaw", "Siłownia"),
    ("boks-jaroslaw", "Boks"),
    ("kickboxing-jaroslaw", "Kickboxing"),
    ("mma-jaroslaw", "MMA"),
    ("fitness-jaroslaw", "Fitness"),
    ("grafik", "Grafik"),
    ("cennik", "Cennik"),
    ("trenerzy", "Trenerzy"),
    ("kontakt", "Kontakt"),
]

PAGES = [
    dict(slug="", src="home", crumb="Strona główna", prio="1.0",
         title="Siłownia Jarosław | V3 Centrum Sportowe, czynne 5:00–0:00",
         desc="V3 Klub przy Poniatowskiego 24 w Jarosławiu: siłownia czynna od 5:00 do północy, Fight Zone (boks, kickboxing, MMA) i zajęcia fitness. Parking przy klubie.",
         og="neon-v3klub"),
    dict(slug="silownia-jaroslaw", src="silownia", crumb="Siłownia", prio="0.9",
         title="Siłownia w Jarosławiu, Poniatowskiego 24 | V3 Klub",
         desc="Siłownia w Jarosławiu z wolnymi ciężarami, rackami, maszynami i strefą cardio. Czynna pn–pt 5:00–0:00, sob 6:00–23:00, nd 8:00–22:00. Szatnie, prysznice, parking.",
         og="silownia-strefa-wolnych-ciezarow",
         service=("Siłownia", "Siłownia w Jarosławiu")),
    dict(slug="boks-jaroslaw", src="boks", crumb="Boks", prio="0.9",
         title="Boks Jarosław | Treningi bokserskie w V3 Fight Zone",
         desc="Treningi bokserskie w Jarosławiu: wtorek i czwartek 19:00–20:15 w Fight Zone V3 Klub. Ring, worki, trenerzy z uprawnieniami. Piątkowy trening dla początkujących.",
         og="ring-bokserski-kaski",
         service=("Boks", "Treningi bokserskie w Jarosławiu")),
    dict(slug="kickboxing-jaroslaw", src="kickboxing", crumb="Kickboxing", prio="0.9",
         title="Kickboxing Jarosław | Grupy od 4 lat do dorosłych, V3 Klub",
         desc="Kickboxing w Jarosławiu dla dzieci od 4 lat, młodzieży i dorosłych. Grupy wiekowe, Fight Team ze sparingami. Trenerzy II klasy Polskiego Związku Kickboxingu.",
         og="fight-zone-sala",
         service=("Kickboxing", "Treningi kickboxingu w Jarosławiu")),
    dict(slug="mma-jaroslaw", src="mma", crumb="MMA", prio="0.9",
         title="MMA Jarosław | Treningi MMA w Fight Zone V3 Klub",
         desc="Treningi MMA w Jarosławiu: piątek 20:00–21:00 i sobota 12:00–13:00. Do tego boks, kickboxing, ju-jitsu i grappling pod jednym dachem przy Poniatowskiego 24.",
         og="fight-zone-sala",
         service=("MMA", "Treningi MMA w Jarosławiu")),
    dict(slug="fitness-jaroslaw", src="fitness", crumb="Fitness", prio="0.8",
         title="Fitness Jarosław | Pilates, joga, zumba, step w V3 Klub",
         desc="Zajęcia fitness w Jarosławiu: pilates, joga, zumba, step, aeroboxing, zdrowy kręgosłup i gimnastyka korekcyjna. Sala fitness w V3 Klub, Poniatowskiego 24.",
         og="zajecia-fitness-grupa",
         service=("Zajęcia fitness", "Zajęcia fitness w Jarosławiu")),
    dict(slug="grafik", src="grafik", crumb="Grafik zajęć", prio="0.8",
         title="Grafik zajęć | V3 Klub Jarosław, Fight Zone i fitness",
         desc="Aktualny grafik zajęć V3 Klub w Jarosławiu: kickboxing, boks, MMA, ju-jitsu, samoobrona i zajęcia fitness. Godziny na każdy dzień tygodnia.",
         og="fight-zone-sala"),
    dict(slug="cennik", src="cennik", crumb="Cennik", prio="0.8",
         title="Cennik | Karnety i wejścia na siłownię, V3 Klub Jarosław",
         desc="Cennik V3 Klub w Jarosławiu: karnety na siłownię, wejście jednorazowe, zajęcia Fight Zone i fitness, treningi personalne oraz vouchery podarunkowe.",
         og="voucher-podarunkowy"),
    dict(slug="trenerzy", src="trenerzy", crumb="Trenerzy", prio="0.7",
         title="Trenerzy | Kickboxing, boks, MMA i fitness, V3 Klub Jarosław",
         desc="Poznaj trenerów V3 Klub w Jarosławiu: Jacek, Ireneusz, Damian, Marcin, Julia i Dawid. Kickboxing, boks, grappling, taekwondo i treningi personalne.",
         og="trenerzy/jacek"),
    dict(slug="kontakt", src="kontakt", crumb="Kontakt", prio="0.7",
         title="Kontakt | V3 Centrum Sportowe, Poniatowskiego 24, Jarosław",
         desc="V3 Centrum Sportowe, Poniatowskiego 24, 37-500 Jarosław. Tel. 788 463 717. Czynne pn–pt 5:00–0:00, sob 6:00–23:00, nd 8:00–22:00. Mapa dojazdu i parking.",
         og="budynek-poniatowskiego-24", webpage_type="ContactPage"),
]

# ============================================================
# IKONY (Lucide, ISC; TikTok: Simple Icons, CC0)
# ============================================================
IKONY = {
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "menu": '<line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "plus": '<path d="M5 12h14"/><path d="M12 5v14"/>',
    "play": '<polygon points="6 3 20 12 6 21 6 3" fill="currentColor"/>',
    "nav": '<polygon points="3 11 22 2 13 21 11 13 3 11"/>',
    "calendar": '<rect width="18" height="18" x="3" y="4" rx="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/>',
    "parking": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 17V7h4a3 3 0 0 1 0 6H9"/>',
    "phone-app": '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>',
    "instagram": '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>',
    "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
}
TIKTOK_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>'

def ikona(name, cls=""):
    if name == "tiktok":
        return TIKTOK_SVG
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{IKONY[name]}</svg>')

# ============================================================
# OBRAZY
# ============================================================
MANIFEST = json.load(open(os.path.join(SRC, "images.json")))

def img(name, alt, sizes="100vw", eager=False, cls="", pos=""):
    m = MANIFEST[name]
    ws = m["widths"]
    def srcset(ext):
        return ", ".join(f"~/assets/img/{name}-{w}.{ext} {w}w" for w in ws)
    fallback = ws[1] if len(ws) > 2 else ws[-1]
    h = round(m["h"] * fallback / m["w"])
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    st = f' style="object-position:{pos}"' if pos else ""
    return (f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img src="~/assets/img/{name}-{fallback}.webp" width="{fallback}" height="{h}" '
            f'alt="{html.escape(alt)}"{c}{st} {load}></picture>')

# tło hero na stronie głównej: (nazwa sali, zdjęcie na komputer, zdjęcie na telefon)
HERO_SLAJDY = [
    ("Siłownia", "silownia-strefa-wolnych-ciezarow", "silownia-sala-glowna"),
    ("Fight Zone", "ring-bokserski-kaski", "fight-zone-sala"),
    ("Fitness", "zajecia-fitness-grupa", "zajecia-fitness-grupa"),
    ("Cardio", "cardio-air-bike", "bieznie-cardio"),
]

def hero_tlo(tylko_sale=False):
    """Zdjęcia w tle hero. Pierwsze ładuje się od razu, kolejne JS podmienia z data-srcset po załadowaniu strony."""
    def srcset(name, ext):
        return ", ".join(f"~/assets/img/{name}-{w}.{ext} {w}w" for w in MANIFEST[name]["widths"])
    slajdy, zakladki = [], []
    for i, (sala, d, m) in enumerate(HERO_SLAJDY):
        a = "srcset" if i == 0 else "data-srcset"
        src = "src" if i == 0 else "data-src"
        load = 'fetchpriority="high"' if i == 0 else 'loading="lazy"'
        mw = MANIFEST[m]["widths"][-1]
        slajdy.append(
            f'<picture class="hero__slajd{" is-aktywny" if i == 0 else ""}">'
            f'<source media="(min-width: 900px)" type="image/avif" {a}="{srcset(d, "avif")}" sizes="100vw">'
            f'<source media="(min-width: 900px)" type="image/webp" {a}="{srcset(d, "webp")}" sizes="100vw">'
            f'<source type="image/avif" {a}="{srcset(m, "avif")}" sizes="100vw">'
            f'<source type="image/webp" {a}="{srcset(m, "webp")}" sizes="100vw">'
            f'<img {src}="~/assets/img/{m}-{mw}.webp" alt="" decoding="async" {load}></picture>')
        cur = ' aria-current="true"' if i == 0 else ""
        zakladki.append(f'<li><button type="button" data-slajd="{i}"{cur}>{sala}</button></li>')
    if tylko_sale:
        return f'<ul class="hero__sale" aria-label="Zdjęcie w tle">{"".join(zakladki)}</ul>'
    return f'<div class="hero__tlo" aria-hidden="true">{"".join(slajdy)}</div>'

def img_abs(name):
    m = MANIFEST[name]
    return f"{SITE_URL}/assets/img/{name}-{m['widths'][-1]}.webp"

# ============================================================
# KOMPONENTY
# ============================================================
def fmt_h(t):
    return "0:00" if t == "24:00" else t.lstrip("0") if not t.startswith("0:") else t

def godz_tekst(d):
    o, c = GODZINY[d]
    return f"{fmt_h(o)}–{fmt_h(c)}"

def tabela_godzin(cls="godziny"):
    rows = "".join(
        f'<tr data-dzien="{d}"><th scope="row">{DNI[d]}</th><td>{godz_tekst(d)}</td></tr>'
        for d in range(1, 8))
    return f'<table class="{cls}"><caption class="sr-only">Godziny otwarcia V3 Centrum Sportowe</caption><tbody>{rows}</tbody></table>'

def zaj_link(z):
    nazwa, url = DYSCYPLINY[z["d"]]
    return url

def grafik_tabela(dys):
    keys = [k.strip() for k in dys.split(",")]
    rows = [z for z in GRAFIK if z["d"] in keys]
    body = ""
    for z in rows:
        grupa = z["grupa"] or "wszyscy"
        body += (f'<tr><th scope="row">{DNI[z["dzien"]]}</th>'
                 f'<td class="num">{fmt_h(z["od"])}–{fmt_h(z["do"])}</td>'
                 f'<td>{z["nazwa"]}</td><td>{grupa}</td></tr>')
    return ('<div class="tabela"><table><caption class="sr-only">Godziny zajęć</caption>'
            '<thead><tr><th scope="col">Dzień</th><th scope="col">Godzina</th><th scope="col">Zajęcia</th><th scope="col">Grupa</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>'
            f'<p class="przypis">Grafik Fight Zone obowiązuje od {GRAFIK_OD}. Pełny tydzień: <a class="link" href="~/grafik/">grafik zajęć</a>.</p>')

def grafik_tydzien():
    out = '<div class="grafik-dni">'
    for d in range(1, 8):
        zz = [z for z in GRAFIK if z["dzien"] == d]
        out += f'<section class="dzien" data-dzien="{d}" aria-labelledby="dzien-{d}"><h3 id="dzien-{d}">{DNI[d]} <small>dziś</small></h3><ul>'
        if not zz:
            out += (f'<li class="zajecia"><span class="zajecia__czas">cały dzień</span>'
                    f'<span class="zajecia__nazwa"><span>Brak zajęć w Fight Zone<span class="zajecia__grupa">Siłownia czynna {godz_tekst(d)}</span></span></span></li>')
        for z in zz:
            url = DYSCYPLINY[z["d"]][1]
            grupa = f'<span class="zajecia__grupa">{z["grupa"]}</span>' if z["grupa"] else ""
            out += (f'<li class="zajecia"><span class="zajecia__czas">{fmt_h(z["od"])}–{fmt_h(z["do"])}</span>'
                    f'<span class="zajecia__nazwa" data-d="{z["d"]}"><span class="tag" aria-hidden="true"></span>'
                    f'<span><a href="~{url}">{z["nazwa"]}</a>{grupa}</span></span></li>')
        out += "</ul></section>"
    return out + "</div>"

def legenda():
    items = "".join(
        f'<li data-d="{k}"><span class="tag" aria-hidden="true"></span><a href="~{v[1]}">{v[0]}</a></li>'
        for k, v in DYSCYPLINY.items())
    return f'<ul class="legenda" aria-label="Dyscypliny">{items}</ul>'

def wideo(attrs):
    key = attrs.get("key", "")
    tytul = attrs.get("tytul", "")
    opis = attrs.get("opis", "")
    src = attrs.get("src", "")
    poster = attrs.get("poster")
    poziome = " wideo--poziome" if "poziome" in attrs else ""
    p = img(poster, "", "(min-width: 1100px) 25vw, (min-width: 700px) 50vw, 100vw") if poster else ""
    if src:
        karta = " wideo--karta" if "karta" in attrs else ""
        podpis = f'<figcaption>{tytul}<span>{opis}</span></figcaption>' if not karta else ""
        return (f'<figure class="wideo wideo--gotowe{poziome}{karta}" data-src="{src}" data-opis="{html.escape(tytul)}">'
                f'<div class="wideo__ekran">{p}<button class="wideo__otworz" type="button" '
                f'aria-label="Otwórz nagranie na pełnym ekranie: {html.escape(tytul)}">'
                f'<span class="wideo__play">{ikona("play")}</span></button></div>{podpis}</figure>')
    return (f'<!-- WIDEO ({key}): wgraj plik do assets/video/{key}.mp4 i wpisz data-src="~/assets/video/{key}.mp4" -->'
            f'<figure class="wideo{poziome}" data-src="{src}" data-opis="{html.escape(tytul)}">'
            f'<div class="wideo__ekran">{p}<div class="wideo__znacznik"><span class="wideo__play">{ikona("play")}</span>'
            f'<span>Nagranie z treningu<br>pojawi się wkrótce</span></div></div>'
            f'<figcaption>{tytul}<span>{opis}</span></figcaption></figure>')

def cta(attrs):
    t = attrs.get("tytul", "Wpadnij na trening")
    txt = attrs.get("tekst", f"{NAZWA}, {ULICA}, {MIASTO}. Zadzwoń albo przyjdź do recepcji, pokażemy klub i dobierzemy karnet.")
    return (f'<section class="cta"><div class="wrap cta__in"><div><h2 class="h2">{t}</h2>'
            f'<p class="mt-5">{txt}</p></div><div class="btn-rzad">'
            f'<a class="btn btn--neon" href="tel:{TEL_E164}">{ikona("phone")}{TEL}</a>'
            f'<a class="btn btn--obrys" href="{MAPS_TRASA}" rel="noopener" target="_blank">{ikona("nav")}Wyznacz trasę</a>'
            f'</div></div></section>')

def faq_block(inner, faq_acc):
    items = re.split(r"^\?\s+", inner.strip(), flags=re.M)
    out = '<div class="faq">'
    for it in items:
        if not it.strip():
            continue
        q, _, a = it.partition("\n")
        q, a = q.strip(), a.strip()
        a_html = "".join(f"<p>{p.strip()}</p>" for p in re.split(r"\n\s*\n", a) if p.strip())
        faq_acc.append((q, a_html))
        out += (f'<details><summary>{q}{ikona("plus")}</summary>'
                f'<div class="faq__odp">{a_html}</div></details>')
    return out + "</div>"

def crumbs(page):
    if not page["slug"]:
        return ""
    return ('<nav class="crumbs" aria-label="Okruszki"><ol>'
            '<li><a href="~/">Strona główna</a></li>'
            f'<li><span aria-current="page">{page["crumb"]}</span></li></ol></nav>')

# ============================================================
# SCHEMA.ORG
# ============================================================
def schema_klub():
    open_spec = []
    groups = {}
    for d, (o, c) in GODZINY.items():
        groups.setdefault((o, c), []).append(DNI_EN[d])
    for (o, c), days in groups.items():
        open_spec.append({"@type": "OpeningHoursSpecification", "dayOfWeek": days,
                          "opens": o, "closes": "23:59" if c == "24:00" else c})
    same = [u for u in (TIKTOK, FACEBOOK, INSTAGRAM) if u]
    return {
        "@type": ["ExerciseGym", "SportsActivityLocation"],
        "@id": f"{SITE_URL}/#klub",
        "name": NAZWA,
        "alternateName": [MARKA, "V3 Centrum Sportowe (siłownia)", "V3KLUB"],
        "description": "Centrum sportowe w Jarosławiu: siłownia, Fight Zone (boks, kickboxing, MMA, ju-jitsu, samoobrona) i zajęcia fitness.",
        "url": f"{SITE_URL}/",
        "telephone": "+48 788 463 717",
        "logo": f"{SITE_URL}/assets/brand/icon-512.png",
        "image": [img_abs("neon-v3klub"), img_abs("silownia-strefa-wolnych-ciezarow"), img_abs("fight-zone-sala")],
        "address": {"@type": "PostalAddress", "streetAddress": ULICA, "postalCode": KOD,
                    "addressLocality": MIASTO, "addressRegion": WOJ, "addressCountry": "PL"},
        # TODO: "geo": {"@type": "GeoCoordinates", "latitude": ..., "longitude": ...} z pinezki Google
        "hasMap": MAPS,
        "areaServed": {"@type": "City", "name": MIASTO},
        "openingHoursSpecification": open_spec,
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": n, "value": True}
            for n in ("Parking", "Szatnie z szafkami", "Prysznice", "Sklepik z napojami i suplementami", "Sala sportów walki z ringiem", "Sala fitness")
        ],
        "sameAs": same,
    }

def schema_for(page, faq_items, extra_nodes):
    url = f"{SITE_URL}/{page['slug']}/" if page["slug"] else f"{SITE_URL}/"
    graph = [schema_klub()]
    webpage = {
        "@type": page.get("webpage_type", "WebPage"),
        "@id": f"{url}#strona",
        "url": url,
        "name": page["title"],
        "description": page["desc"],
        "inLanguage": "pl-PL",
        "isPartOf": {"@id": f"{SITE_URL}/#witryna"},
        "about": {"@id": f"{SITE_URL}/#klub"},
        "primaryImageOfPage": img_abs(page["og"]),
    }
    if not page["slug"]:
        graph.append({"@type": "WebSite", "@id": f"{SITE_URL}/#witryna", "url": f"{SITE_URL}/",
                      "name": MARKA, "alternateName": NAZWA, "inLanguage": "pl-PL",
                      "publisher": {"@id": f"{SITE_URL}/#klub"}})
    else:
        webpage["breadcrumb"] = {"@id": f"{url}#okruszki"}
        graph.append({"@type": "BreadcrumbList", "@id": f"{url}#okruszki", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Strona główna", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": page["crumb"], "item": url}]})
    graph.append(webpage)
    if page.get("service"):
        typ, nazwa = page["service"]
        graph.append({"@type": "Service", "@id": f"{url}#usluga", "name": nazwa, "serviceType": typ,
                      "provider": {"@id": f"{SITE_URL}/#klub"},
                      "areaServed": {"@type": "City", "name": MIASTO}, "url": url})
    if faq_items:
        graph.append({"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a).strip()}}
            for q, a in faq_items]})
    graph.extend(extra_nodes)
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))

# ============================================================
# LAYOUT
# ============================================================
def header(page):
    items = ""
    mob = ""
    for slug, label in NAV:
        cur = ' aria-current="page"' if slug == page["slug"] else ""
        items += f'<li><a href="~/{slug}/"{cur}>{label}</a></li>'
        mob += f'<li><a href="~/{slug}/"{cur}>{label}</a></li>'
    return f'''<a class="skip-link" href="#tresc">Przejdź do treści</a>
<header class="site-header">
  <div class="wrap site-header__in">
    <a class="logo" href="~/" aria-label="{MARKA}, strona główna"><img src="~/assets/brand/v3klub-wordmark.svg" alt="V3 Klub" width="142" height="30"></a>
    <nav class="nav" aria-label="Główne menu"><ul>{items}</ul></nav>
    <a class="btn btn--neon header-tel" href="tel:{TEL_E164}">{ikona("phone")}{TEL}</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu-panel">{ikona("menu", "ik-menu")}{ikona("x", "ik-zamknij")}<span class="menu-btn__txt">Menu</span></button>
  </div>
</header>
<div class="menu-panel" id="menu-panel" inert>
  <nav aria-label="Menu mobilne"><ul>{mob}</ul></nav>
  <a class="btn btn--neon" href="tel:{TEL_E164}">{ikona("phone")}Zadzwoń: {TEL}</a>
  <p class="menu-panel__info">{ULICA}, {KOD} {MIASTO}<br>pn–pt {godz_tekst(1)} · sob {godz_tekst(6)} · nd {godz_tekst(7)}</p>
</div>'''

def footer():
    oferta = "".join(f'<li><a href="~/{s}/">{l}</a></li>' for s, l in NAV[:5])
    klub = "".join(f'<li><a href="~/{s}/">{l}</a></li>' for s, l in NAV[5:])
    rows = "".join(f'<tr data-dzien="{d}"><th scope="row">{DNI[d]}</th><td>{godz_tekst(d)}</td></tr>' for d in range(1, 8))
    social = f'<li><a href="{TIKTOK}" rel="noopener" target="_blank">TikTok</a></li>'
    social += f'<li><a href="{APKA}" rel="noopener" target="_blank">Aplikacja klubu</a></li>'
    if FACEBOOK: social += f'<li><a href="{FACEBOOK}" rel="noopener" target="_blank">Facebook</a></li>'
    if INSTAGRAM: social += f'<li><a href="{INSTAGRAM}" rel="noopener" target="_blank">Instagram</a></li>'
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="stopka-grid">
      <div>
        <a class="stopka-logo" href="~/" aria-label="{MARKA}, strona główna"><img src="~/assets/brand/v3klub-logo.svg" alt="V3 Klub" width="147" height="110" loading="lazy"></a>
        <address class="stopka-nap"><strong>{NAZWA}</strong><br>{ULICA}<br>{KOD} {MIASTO}<br><a href="tel:{TEL_E164}">tel. {TEL}</a></address>
      </div>
      <div><h2>Oferta</h2><ul>{oferta}</ul></div>
      <div><h2>Klub</h2><ul>{klub}{social}</ul></div>
      <div><h2>Godziny otwarcia</h2><table class="stopka-godziny"><tbody>{rows}</tbody></table></div>
    </div>
    <div class="stopka-dol"><span>© {date.today().year} {NAZWA} · {MARKA}</span><a href="{MAPS}" rel="noopener" target="_blank">Profil w Mapach Google</a></div>
  </div>
</footer>
<nav class="pasek-akcji" aria-label="Szybkie akcje">
  <a href="tel:{TEL_E164}">{ikona("phone")}Zadzwoń</a>
  <a href="{MAPS_TRASA}" rel="noopener" target="_blank">{ikona("nav")}Trasa</a>
  <a href="~/grafik/">{ikona("calendar")}Grafik</a>
</nav>'''

def layout(page, body, schema, css_v, js_v, noindex=False):
    url = f"{SITE_URL}/{page['slug']}/" if page["slug"] else f"{SITE_URL}/"
    og_img = f"{SITE_URL}/assets/og/og-v3klub.jpg"
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    canonical = "" if noindex else f'<link rel="canonical" href="{url}">\n'
    data_godziny = json.dumps({d: list(v) for d, v in GODZINY.items()}, separators=(",", ":"))
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page["title"])}</title>
<meta name="description" content="{html.escape(page["desc"])}">
{canonical}<meta name="robots" content="{robots}">
<!-- Google Search Console: jeśli weryfikujesz tagiem HTML, wklej tu <meta name="google-site-verification" content="..."> -->
<meta name="theme-color" content="#111312">
<meta name="format-detection" content="telephone=no">
<link rel="preload" href="~/assets/fonts/archivo-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="~/assets/fonts/instrument-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="~/assets/css/styles.css?v={css_v}">
<link rel="icon" href="~/favicon.ico" sizes="32x32">
<link rel="icon" href="~/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="~/apple-touch-icon.png">
<link rel="manifest" href="~/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="{MARKA}">
<meta property="og:title" content="{html.escape(page["title"])}">
<meta property="og:description" content="{html.escape(page["desc"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Podświetlony znak V3 KLUB na ceglanej ścianie siłowni w Jarosławiu">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{schema}</script>
<script type="application/json" id="dane-godziny">{data_godziny}</script>
<script src="~/assets/js/main.js?v={js_v}" defer></script>
</head>
<body>
{header(page)}
<main id="tresc">
{body}
</main>
{footer()}
</body>
</html>
'''

# ============================================================
# RENDER
# ============================================================
def attrs_of(s):
    a = dict(re.findall(r'(\w+)="([^"]*)"', s))
    for flag in re.findall(r'(?:^|\s)(\w+)(?=\s|$)', re.sub(r'\w+="[^"]*"', "", s)):
        a[flag] = True
    return a

def render_body(raw, page, faq_acc):
    raw = re.sub(r"\{\{faq\}\}(.*?)\{\{/faq\}\}", lambda m: faq_block(m.group(1), faq_acc), raw, flags=re.S)
    def repl(m):
        tag, rest = m.group(1), (m.group(2) or "").strip()
        a = attrs_of(rest)
        if tag == "img":
            return img(a["name"], a.get("alt", ""), a.get("sizes", "100vw"), bool(a.get("eager")), a.get("class", ""), a.get("pos", ""))
        if tag == "ikona": return ikona(rest)
        if tag == "crumbs": return crumbs(page)
        if tag == "godziny": return tabela_godzin()
        if tag == "godz": return godz_tekst(int(rest))
        if tag == "grafik_tabela": return grafik_tabela(a["d"])
        if tag == "grafik_tydzien": return grafik_tydzien()
        if tag == "legenda": return legenda()
        if tag == "wideo": return wideo(a)
        if tag == "hero_tlo": return hero_tlo()
        if tag == "hero_sale": return hero_tlo(tylko_sale=True)
        if tag == "cta": return cta(a)
        if tag == "dane_grafik":
            data = {"zajecia": [dict(z, url="~" + DYSCYPLINY[z["d"]][1]) for z in GRAFIK]}
            return f'<script type="application/json" id="dane-grafik">{json.dumps(data, ensure_ascii=False, separators=(",", ":"))}</script>'
        simple = {"tel": TEL, "tel_href": f"tel:{TEL_E164}", "maps": MAPS, "maps_trasa": MAPS_TRASA,
                  "maps_embed": MAPS_EMBED, "apka": APKA, "tiktok": TIKTOK, "grafik_od": GRAFIK_OD,
                  "ulica": ULICA, "kod": KOD, "miasto": MIASTO, "nazwa": NAZWA, "marka": MARKA}
        if tag in simple: return simple[tag]
        raise ValueError(f"Nieznany znacznik {{{{{tag}}}}} w {page['src']}")
    return re.sub(r"\{\{(\w+)(?:\s+([^}]*))?\}\}", repl, raw)

def rel_root(slug):
    return "./" if not slug else "../"

def extra_nodes_for(page):
    path = os.path.join(SRC, "pages", page["src"] + ".schema.json")
    if os.path.exists(path):
        s = open(path).read().replace("{{SITE_URL}}", SITE_URL)
        return json.loads(s)
    return []

def version(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()[:8]

def build():
    # CSS: font-face + style
    css = open(os.path.join(SRC, "fontface.css")).read() + "\n" + open(os.path.join(SRC, "styles.css")).read()
    os.makedirs(os.path.join(ROOT, "assets/css"), exist_ok=True)
    open(os.path.join(ROOT, "assets/css/styles.css"), "w").write(css)
    css_v = version(os.path.join(ROOT, "assets/css/styles.css"))
    js_v = version(os.path.join(ROOT, "assets/js/main.js"))

    todos = []
    for page in PAGES:
        srcf = os.path.join(SRC, "pages", page["src"] + ".html")
        if not os.path.exists(srcf):
            print("pomijam (brak pliku):", page["src"]); continue
        raw = open(srcf).read()
        faq_acc = []
        body = render_body(raw, page, faq_acc)
        schema = schema_for(page, faq_acc, extra_nodes_for(page))
        out = layout(page, body, schema, css_v, js_v).replace("~/", rel_root(page["slug"]))
        assert "—" not in out, f"em dash w {page['src']}"
        dest = os.path.join(ROOT, page["slug"], "index.html") if page["slug"] else os.path.join(ROOT, "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, "w").write(out)
        # zbierz braki
        for t in re.findall(r'<span class="todo"[^>]*>(.*?)</span>', body, re.S):
            todos.append((page, "na stronie", re.sub(r"<[^>]+>", "", t)))
        for t in re.findall(r"<!--\s*TODO:?\s*(.*?)-->", raw, re.S):
            todos.append((page, "w kodzie", " ".join(t.split())))

    # 404
    p404 = dict(slug="404", src="404", crumb="Nie znaleziono", title="Nie ma takiej strony | V3 Klub Jarosław",
                desc="Ta strona nie istnieje. Sprawdź grafik, cennik albo kontakt V3 Klub w Jarosławiu.", og="neon-v3klub")
    raw404 = open(os.path.join(SRC, "pages", "404.html")).read()
    out404 = layout(dict(p404, slug=""), render_body(raw404, p404, []), schema_for(dict(p404, slug=""), [], []), css_v, js_v, noindex=True)
    # 404 bywa serwowane pod dowolnym adresem, więc ścieżki muszą być od korzenia domeny
    open(os.path.join(ROOT, "404.html"), "w").write(out404.replace("~/", "/"))

    # sitemap + robots
    urls = "".join(
        f"<url><loc>{SITE_URL}/{p['slug'] + '/' if p['slug'] else ''}</loc><lastmod>{BUILD_DATE}</lastmod><priority>{p['prio']}</priority></url>\n"
        for p in PAGES)
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")

    # lista braków
    lines = ["# Dane do uzupełnienia", "",
             "Plik generowany przez `_build.py` z oznaczeń `<span class=\"todo\">` i komentarzy `<!-- TODO -->` w `_src/pages/`.",
             "Po uzupełnieniu treści usuń oznaczenie i uruchom `python3 _build.py`.", "",
             "## Globalne (w `_build.py`)", "",
             f"- Domena docelowa: `SITE_URL` (teraz `{SITE_URL}`), od niej zależą canonical, sitemap, OG i schema",
             "- Facebook i Instagram: `FACEBOOK`, `INSTAGRAM` (puste = nie wyświetlają się)",
             "- Współrzędne geo z pinezki Google do schema (`geo`)", ""]
    cur = None
    for page, where, t in todos:
        if page["src"] != cur:
            cur = page["src"]
            lines += ["", f"## /{page['slug']}" if page["slug"] else "## / (strona główna)", ""]
        lines.append(f"- ({where}) {t}")
    open(os.path.join(ROOT, "_DO-UZUPELNIENIA.md"), "w").write("\n".join(lines) + "\n")
    print(f"OK: {len(PAGES)} podstron + 404, braków do uzupełnienia: {len(todos)}")

if __name__ == "__main__":
    build()
