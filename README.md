# V3 Klub: strona www

Statyczna strona V3 Centrum Sportowe (V3 Klub), Poniatowskiego 24, 37-500 Jarosław.
Bez frameworków i bibliotek JS. Czysty HTML + jeden plik CSS + ~6 KB JS.

## Struktura

```
index.html                 strona główna
silownia-jaroslaw/         /silownia-jaroslaw/
boks-jaroslaw/             /boks-jaroslaw/
kickboxing-jaroslaw/       /kickboxing-jaroslaw/
mma-jaroslaw/              /mma-jaroslaw/
fitness-jaroslaw/          /fitness-jaroslaw/
grafik/  cennik/  trenerzy/  kontakt/
404.html  sitemap.xml  robots.txt  site.webmanifest  favicon.*
assets/css  assets/js  assets/fonts  assets/img  assets/brand  assets/og

_build.py                  generator (dane firmy, grafik, nawigacja, schema, SEO)
_src/pages/*.html          treść podstron
_src/styles.css            style (build dokleja @font-face i zapisuje do assets/css)
_DO-UZUPELNIENIA.md        lista brakujących danych (generowana przy buildzie)
```

Pliki i foldery z `_` na początku nie są publikowane przez GitHub Pages (Jekyll je pomija).

## Edycja

1. Treść zmieniasz w `_src/pages/<strona>.html`, dane firmy, godziny i grafik w `_build.py`.
2. Uruchom `python3 _build.py`.
3. Podgląd lokalny: `python3 -m http.server` i otwórz http://localhost:8000

Nie edytuj wygenerowanych `index.html` ręcznie, build je nadpisze.

Znaczniki w `_src/pages`: `{{img name="..." alt="..." sizes="..."}}`, `{{grafik_tabela d="boks"}}`,
`{{grafik_tydzien}}`, `{{wideo key="..." poster="..."}}`, `{{faq}} ? pytanie / odpowiedź {{/faq}}`,
`{{cta}}`, `{{godziny}}`, `{{tel}}` itd. Linki wewnętrzne pisz jako `~/slug/`, build zamieni je na ścieżki względne.

## Grafik

Grafik Fight Zone jest w `_build.py` (lista `GRAFIK`). Po zmianie buildu aktualizują się naraz:
strona /grafik, tabele na stronach dyscyplin i widżet „Dziś w Fight Zone” na stronie głównej.

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
2. Uzupełnij dane z `_DO-UZUPELNIENIA.md` (ceny, grafik fitness, Facebook/Instagram, zasady samoobsługi).
3. Hosting: GitHub Pages, Netlify, Cloudflare Pages lub dowolny serwer statyczny. Adresy podstron kończą się `/`.

## Google Search Console

1. Dodaj usługę typu **Domena** (weryfikacja rekordem TXT w DNS) albo **Prefiks URL**
   (wtedy wklej tag `google-site-verification` w `_build.py`, funkcja `layout`, w miejscu komentarza w `<head>`).
2. W „Mapy witryny” zgłoś `https://<domena>/sitemap.xml`.
3. Sprawdź stronę główną i 4 główne podstrony w „Sprawdzenie adresu URL” i poproś o zindeksowanie.
4. W profilu Firmy w Google ustaw stronę www na nową domenę, żeby NAP i link były spójne.
5. Dane strukturalne sprawdzisz w https://search.google.com/test/rich-results
# v3-klub
