# V3 Klub: strona www

Statyczna strona V3 Centrum Sportowe (V3 Klub), Poniatowskiego 24, 37-500 Jarosław.
Bez frameworków i bibliotek JS. Czysty HTML + jeden plik CSS + ~6 KB JS.

## Struktura

```
index.html, <slug>/index.html   strony (GENEROWANE, nie edytuj ręcznie)
404.html  sitemap.xml  robots.txt   (generowane)
site.webmanifest  favicon.*  apple-touch-icon.png

assets/                  wszystko, co publikowane i linkowane ze stron
  css/                   styles.css (generowany z _src/css)
  js/                    main.js
  fonts/                 woff2
  img/                   zdjęcia AVIF + WebP w kilku szerokościach, img/trenerzy/
  video/                 nagrania MP4 gotowe na stronę
  plakaty/               plakaty grafików do pobrania (webp)
  brand/                 logo, ikony PWA
  og/                    obraz podglądu w social media

_build.py                generator (dane firmy, nawigacja, SEO, schema, komponenty)
_src/                    źródła (nie są publikowane)
  pages/                 treść podstron (*.html) + opcjonalne *.schema.json
  css/                   styles.css, fontface.css
  dane/                  grafik-fight-zone.json, grafik-fitness.json, obrazy.json
  oryginaly/             surowe pliki przed obróbką
    zdjecia/             zdjęcia w pełnej jakości
    filmy/               nagrania z TikToka (INDEKS.md: nazwa pliku -> oryginalny podpis)
    plakaty/             oryginalne grafiki plakatów (PNG)
_docs/                   DO-UZUPELNIENIA.md (generowany), notatki
```

Pliki i foldery z `_` na początku nie są publikowane przez GitHub Pages (Jekyll je pomija).
Zasada: oryginał trafia do `_src/oryginaly/<typ>/`, wersja na stronę do `assets/<typ>/` pod tą samą nazwą.

## Edycja

1. Treść zmieniasz w `_src/pages/<strona>.html`, grafiki w `_src/dane/grafik-*.json`, dane firmy i godziny otwarcia w `_build.py`.
2. Uruchom `python3 _build.py`.
3. Podgląd lokalny: `python3 -m http.server` i otwórz http://localhost:8000

Nie edytuj wygenerowanych `index.html` ręcznie, build je nadpisze.

Znaczniki w `_src/pages`: `{{img name="..." alt="..." sizes="..."}}`, `{{grafik_tabela d="boks"}}`,
`{{grafik_tydzien g="fitness"}}`, `{{legenda g="fitness"}}`, `{{terminy g="fitness" d="pilates"}}`,
`{{grafik_od g="..."}}`, `{{plakat g="..."}}`, `{{wideo key="..." poster="..."}}`,
`{{faq}} ? pytanie / odpowiedź {{/faq}}`, `{{cta}}`, `{{godziny}}`, `{{tel}}` itd.
`g` to nazwa grafiku (`fight-zone` domyślnie albo `fitness`). Linki wewnętrzne pisz jako `~/slug/`, build zamieni je na ścieżki względne.

## Grafiki

Dwa grafiki, każdy w osobnym pliku JSON w `_src/dane/`:

- `grafik-fight-zone.json`: strona /grafik, tabele na stronach dyscyplin, widżet „Dziś w Fight Zone” na stronie głównej.
- `grafik-fitness.json`: grafik na /fitness-jaroslaw i /grafik oraz terminy w kartach zajęć.

Jedno zajęcie w linii: `{"dzien": 1-7, "od": "19:00", "do": "" (puste, gdy znany tylko początek), "nazwa": "...", "k": "<klucz kategorii>", "info": "..."}`.
Nowa kategoria: dopisz ją w `"kategorie"` i nadaj kolor w `_src/css/styles.css` (`[data-d="<klucz>"] { --kolor: ... }`).
Nowy plakat: oryginał do `_src/oryginaly/plakaty/`, wersję webp (`cwebp -q 82`) do `assets/plakaty/`, nazwę pliku wpisz w `"plakat"`.

## Nagrania wideo

Miejsca na nagrania są na stronie głównej (siłownia, boks, kickboxing, fitness) i na podstronach.
Wgraj plik MP4 (H.264, najlepiej pionowy 9:16, do ~8 MB, bez dźwięku) do `assets/video/`
i w `_src/pages/...` uzupełnij znacznik o `src`, np.:

```
{{wideo key="boks" src="~/assets/video/boks.mp4" poster="ring-bokserski-kaski" tytul="Sala boksu" opis="..."}}
```

Wideo ładuje się dopiero po przewinięciu do niego, gra bez dźwięku w pętli.

## Obrazy

Wszystkie zdjęcia są w AVIF + WebP w kilku szerokościach (`<picture>` + `srcset`), z `width`/`height`,
`loading="lazy"` poza pierwszym ekranem. Wyjątki PNG/JPG: ikony (`apple-touch-icon.png`, `icon-192/512.png`)
i obraz podglądu w social media `assets/og/og-v3klub.jpg` (nie każda platforma przyjmuje WebP w og:image).

## Przed publikacją

1. Ustaw docelową domenę w `_build.py` (`SITE_URL`) i uruchom build: od niej zależą canonical, sitemap, OG i schema.
2. Uzupełnij dane z `_docs/DO-UZUPELNIENIA.md` (ceny, prowadzący fitness, Facebook/Instagram, zasady samoobsługi).
3. Hosting: GitHub Pages, Netlify, Cloudflare Pages lub dowolny serwer statyczny. Adresy podstron kończą się `/`.

## Google Search Console

1. Dodaj usługę typu **Domena** (weryfikacja rekordem TXT w DNS) albo **Prefiks URL**
   (wtedy wklej tag `google-site-verification` w `_build.py`, funkcja `layout`, w miejscu komentarza w `<head>`).
2. W „Mapy witryny” zgłoś `https://<domena>/sitemap.xml`.
3. Sprawdź stronę główną i 4 główne podstrony w „Sprawdzenie adresu URL” i poproś o zindeksowanie.
4. W profilu Firmy w Google ustaw stronę www na nową domenę, żeby NAP i link były spójne.
5. Dane strukturalne sprawdzisz w https://search.google.com/test/rich-results
# v3-klub
