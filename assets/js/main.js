/* V3 Klub: drobny JS bez bibliotek */
(function () {
  "use strict";

  /* ---------- menu mobilne ---------- */
  var btn = document.querySelector(".menu-btn");
  var panel = document.getElementById("menu-panel");
  if (btn && panel) {
    var setOpen = function (open) {
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      btn.querySelector(".menu-btn__txt").textContent = open ? "Zamknij" : "Menu";
      panel.classList.toggle("is-open", open);
      document.body.style.overflow = open ? "hidden" : "";
      if (open) panel.removeAttribute("inert"); else panel.setAttribute("inert", "");
    };
    btn.addEventListener("click", function () { setOpen(btn.getAttribute("aria-expanded") !== "true"); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && btn.getAttribute("aria-expanded") === "true") { setOpen(false); btn.focus(); }
    });
    window.matchMedia("(min-width: 1180px)").addEventListener("change", function (m) { if (m.matches) setOpen(false); });
  }

  /* ---------- czas w Jarosławiu (Europe/Warsaw) ---------- */
  function warsawNow() {
    var parts = {};
    new Intl.DateTimeFormat("en-GB", {
      timeZone: "Europe/Warsaw", weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23"
    }).formatToParts(new Date()).forEach(function (p) { parts[p.type] = p.value; });
    var days = { Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6, Sun: 7 };
    return { day: days[parts.weekday], min: parseInt(parts.hour, 10) * 60 + parseInt(parts.minute, 10) };
  }
  var now = warsawNow();
  var DNI = ["", "poniedziałek", "wtorek", "środa", "czwartek", "piątek", "sobota", "niedziela"];
  var toMin = function (t) { var a = t.split(":"); return (+a[0]) * 60 + (+a[1]); };
  var fmt = function (t) { return t.replace(/^0/, ""); };

  /* godziny otwarcia: [dzień] = [otwarcie, zamknięcie]; "24:00" = północ */
  var hoursEl = document.getElementById("dane-godziny");
  var HOURS = hoursEl ? JSON.parse(hoursEl.textContent) : null;

  /* ---------- dzisiejsze godziny otwarcia (hero) ---------- */
  var dzisGodz = document.querySelector("[data-dzis-godziny]");
  if (dzisGodz && HOURS && HOURS[now.day]) {
    var hd = HOURS[now.day];
    dzisGodz.querySelector(".hero__dzis-dzien").textContent = "Dziś, " + DNI[now.day];
    dzisGodz.querySelector(".hero__dzis-godz").textContent = fmt(hd[0]) + "–" + (hd[1] === "24:00" ? "0:00" : fmt(hd[1]));
  }

  /* ---------- hero: zdjęcia sal zmieniają się same w tle ---------- */
  var hero = document.querySelector(".hero");
  var slajdy = hero ? hero.querySelectorAll(".hero__slajd") : [];
  if (slajdy.length > 1 && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var CZAS = 6000, akt = 0, timer = null;
    /* kolejne zdjęcia pobieramy dopiero po załadowaniu strony */
    var doladuj = function () {
      hero.querySelectorAll("[data-srcset]").forEach(function (el) { el.srcset = el.getAttribute("data-srcset"); el.removeAttribute("data-srcset"); });
      hero.querySelectorAll("img[data-src]").forEach(function (el) { el.src = el.getAttribute("data-src"); el.removeAttribute("data-src"); });
    };
    var gotowe = function (i) { var im = slajdy[i].querySelector("img"); return im.complete && im.naturalWidth > 0; };
    var start = function () {
      if (timer) return;
      timer = setInterval(function () {
        var nast = (akt + 1) % slajdy.length;
        if (!gotowe(nast)) return;
        slajdy[akt].classList.remove("is-aktywny");
        akt = nast;
        slajdy[akt].classList.add("is-aktywny");
      }, CZAS);
    };
    var stop = function () { clearInterval(timer); timer = null; };
    document.addEventListener("visibilitychange", function () { if (document.hidden) stop(); else start(); });
    if (document.readyState === "complete") { doladuj(); start(); }
    else window.addEventListener("load", function () { doladuj(); start(); });
  }

  /* podświetl dzisiejszy dzień w tabelach godzin i w grafiku */
  document.querySelectorAll('[data-dzien="' + now.day + '"]').forEach(function (el) { el.classList.add("is-dzis"); });

  /* ---------- dziś w Fight Zone (strona główna) ---------- */
  var dzis = document.querySelector("[data-dzis]");
  var schedEl = document.getElementById("dane-grafik");
  if (dzis && schedEl) {
    var S = JSON.parse(schedEl.textContent);
    var list = dzis.querySelector(".dzis__lista");
    var title = dzis.querySelector(".dzis__tytul");
    var items = S.zajecia.filter(function (z) { return z.dzien === now.day && toMin(z.do) > now.min; });
    var label = "Dziś w Fight Zone";
    if (!items.length) {
      /* najbliższy dzień z zajęciami */
      for (var i = 1; i <= 7; i++) {
        var d = (now.day + i - 1) % 7 + 1;
        var z = S.zajecia.filter(function (x) { return x.dzien === d; });
        if (z.length) { items = z; label = (i === 1 ? "Jutro" : "W " + DNI[d]) + " w Fight Zone"; break; }
      }
    }
    title.textContent = label;
    list.innerHTML = "";
    items.forEach(function (z) {
      var li = document.createElement("li");
      var t = document.createElement("span");
      t.className = "dzis__godz";
      t.textContent = fmt(z.od) + "–" + fmt(z.do);
      var name = document.createElement(z.url ? "a" : "span");
      if (z.url) name.href = z.url;
      name.textContent = z.nazwa + (z.grupa ? " · " + z.grupa : "");
      li.appendChild(t); li.appendChild(name);
      list.appendChild(li);
    });
  }

  /* ---------- sloty wideo: wideo ładuje się dopiero przy przewinięciu ---------- */
  var slots = document.querySelectorAll(".wideo[data-src]");
  if (slots.length) {
    var mount = function (fig) {
      var src = fig.getAttribute("data-src");
      if (!src || fig.classList.contains("ma-wideo")) return;
      var v = document.createElement("video");
      v.muted = true; v.loop = true; v.playsInline = true; v.preload = "metadata";
      v.setAttribute("playsinline", "");
      v.setAttribute("aria-label", fig.getAttribute("data-opis") || "Nagranie z treningu w V3 Klub");
      var poster = fig.querySelector("img");
      if (poster) v.poster = poster.currentSrc || poster.src;
      var s = document.createElement("source"); s.src = src; s.type = "video/mp4"; v.appendChild(s);
      var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (reduce) { v.controls = true; } else { v.autoplay = true; }
      fig.querySelector(".wideo__ekran").appendChild(v);
      fig.classList.add("ma-wideo");
    };
    /* na telefonie nagrania nie grają w sekcjach: miniatura + otwieranie na pełnym ekranie */
    var telefon = window.matchMedia("(max-width: 699px)").matches;
    if (telefon) {
      /* nic nie montujemy */
    } else if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) { mount(e.target); io.unobserve(e.target); } });
      }, { rootMargin: "200px" });
      slots.forEach(function (s) { if (s.getAttribute("data-src")) io.observe(s); });
    } else {
      slots.forEach(mount);
    }
  }

  /* ---------- karuzele na telefonie: kropki pokazujące pozycję ---------- */
  if (window.matchMedia("(max-width: 699px)").matches) {
    document.querySelectorAll(".opinie, .dyscypliny").forEach(function (tor, n) {
      var el = Array.prototype.slice.call(tor.children);
      if (el.length < 2) return;
      var kropki = document.createElement("div");
      kropki.className = "kropki";
      var btns = el.map(function (item, i) {
        var b = document.createElement("button");
        b.type = "button";
        b.setAttribute("aria-label", "Pokaż " + (i + 1) + " z " + el.length);
        b.addEventListener("click", function () {
          tor.scrollTo({ left: item.offsetLeft - tor.offsetLeft - parseFloat(getComputedStyle(tor).paddingLeft), behavior: "smooth" });
        });
        kropki.appendChild(b);
        return b;
      });
      tor.after(kropki);
      var ustaw = function () {
        var start = tor.getBoundingClientRect().left + parseFloat(getComputedStyle(tor).paddingLeft);
        var best = 0, bestD = Infinity;
        el.forEach(function (item, i) { var d = Math.abs(item.getBoundingClientRect().left - start); if (d < bestD) { bestD = d; best = i; } });
        btns.forEach(function (b, i) { if (i === best) b.setAttribute("aria-current", "true"); else b.removeAttribute("aria-current"); });
      };
      var raf = 0;
      tor.addEventListener("scroll", function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(ustaw); }, { passive: true });
      ustaw();
    });
  }

  /* ---------- nagranie na pełnym ekranie ---------- */
  var otworz = document.querySelectorAll(".wideo__otworz");
  if (otworz.length && window.HTMLDialogElement) {
    var box = document.createElement("dialog");
    box.className = "lightbox";
    box.innerHTML = '<button class="lightbox__zamknij" type="button" aria-label="Zamknij nagranie">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></button>' +
      '<video playsinline controls loop></video>';
    document.body.appendChild(box);
    var lbVideo = box.querySelector("video");
    var zamknij = function () { if (box.open) box.close(); };
    box.querySelector(".lightbox__zamknij").addEventListener("click", zamknij);
    /* klik w czarne tło (poza nagraniem) też zamyka */
    box.addEventListener("click", function (e) { if (e.target === box) zamknij(); });
    box.addEventListener("close", function () {
      lbVideo.pause(); lbVideo.removeAttribute("src"); lbVideo.load();
      document.body.style.overflow = "";
      /* wznów nagrania grające w sekcjach */
      document.querySelectorAll(".wideo.ma-wideo video").forEach(function (v) { if (v.autoplay) v.play().catch(function () {}); });
    });
    otworz.forEach(function (b) {
      b.addEventListener("click", function () {
        var fig = b.closest(".wideo");
        document.querySelectorAll(".wideo.ma-wideo video").forEach(function (v) { v.pause(); });
        lbVideo.src = fig.getAttribute("data-src");
        lbVideo.setAttribute("aria-label", fig.getAttribute("data-opis") || "Nagranie z treningu w V3 Klub");
        lbVideo.muted = true;
        document.body.style.overflow = "hidden";
        box.showModal();
        lbVideo.play().catch(function () {});
      });
    });
  }

  /* ---------- mapa Google ładowana po kliknięciu ---------- */
  document.querySelectorAll("[data-mapa]").forEach(function (b) {
    b.addEventListener("click", function () {
      var box = b.closest(".mapa");
      var f = document.createElement("iframe");
      f.src = b.getAttribute("data-mapa");
      f.title = "Mapa dojazdu: V3 Centrum Sportowe, Poniatowskiego 24, Jarosław";
      f.loading = "lazy";
      f.referrerPolicy = "no-referrer-when-downgrade";
      f.allowFullscreen = true;
      box.innerHTML = "";
      box.appendChild(f);
    });
  });
})();
