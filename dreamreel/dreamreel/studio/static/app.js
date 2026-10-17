// dreamreel studio: the browser side. Plain JavaScript, no build step, no network beyond the local server.
"use strict";

// ------------------------------------------------------------------ tiny helpers
const $ = (sel, root = document) => root.querySelector(sel);

function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "html") el.innerHTML = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "value") el.value = v;
    else if (k === "checked") el.checked = !!v;
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat(Infinity)) {
    if (kid === null || kid === undefined || kid === false) continue;
    el.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  }
  return el;
}

async function api(method, path, body) {
  const r = await fetch(path, {
    method, headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || r.statusText);
  return data;
}

let toastTimer;
function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.hidden = true), 2600);
}

function fail(e) { toast(e.message || String(e)); console.error(e); }

const pretty = (s) => String(s).replace(/[-_]/g, " ");
const sceneLabel = (file) => pretty(file.replace(/\.(py|toml)$/, "").replace(/^\d+_/, ""));
const sceneNum = (file) => file.split("_")[0];
const fileUrl = (path, mtime) => `/files/${path}${mtime ? "?t=" + Math.round(mtime) : ""}`;
const slug = (s) => s.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40);
const fmtT = (t) => (Math.round(t * 10) / 10).toFixed(1) + " s";

function lightbox(src) {
  const box = h("div", { class: "lightbox", onclick: () => box.remove() }, h("img", { src, alt: "" }));
  document.body.append(box);
}

// ------------------------------------------------------------------ state
const S = {
  state: null,            // /api/state
  view: localStorage.getItem("dr.view") || "story",
  scene: localStorage.getItem("dr.scene") || null,
  castSel: null,
  setSel: null,
  checks: {},             // scene file -> check result (or {error})
  playhead: {},           // scene file -> seconds
  sceneSpec: {},          // scene file -> its beats and settings, as loaded and edited
  selBeat: {},            // scene file -> selected beat index (new beats go after it)
  newBeat: {},            // scene file -> the beat being composed
  castDraft: {},          // key -> spec being edited
  setDraft: {},           // key -> spec being edited
  watch: new Map(),       // job id -> callback when finished
  composer: { who: "", action: "say" },
  screening: null,
};

const info = () => S.state.info;
const catalog = () => S.state.info.catalog;
const colors = () => catalog().colors;

async function refresh() {
  S.state = await api("GET", "/api/state");
  render();
}

function go(view) {
  S.view = view;
  localStorage.setItem("dr.view", view);
  render();
  window.scrollTo(0, 0);
}

function rendersFor(prefix) {
  return (S.state.renders || []).filter((r) => r.path.startsWith(prefix));
}
function renderOf(path) {
  return (S.state.renders || []).find((r) => r.path === path);
}

// ------------------------------------------------------------------ jobs
async function job(body, onDone) {
  try {
    const { id } = await api("POST", "/api/jobs", body);
    if (onDone) S.watch.set(id, onDone);
    pollJobs();
    return id;
  } catch (e) { fail(e); }
}

const openLogs = new Set();
let pollTimer = null;
async function pollJobs() {
  clearTimeout(pollTimer);
  let data;
  try { data = await api("GET", "/api/jobs"); } catch { pollTimer = setTimeout(pollJobs, 3000); return; }
  const active = data.jobs.filter((j) => j.status === "running" || j.status === "queued");
  let changed = false;
  for (const j of [...data.jobs].reverse()) {
    if ((j.status === "done" || j.status === "failed" || j.status === "cancelled") && S.watch.has(j.id)) {
      const cb = S.watch.get(j.id);
      S.watch.delete(j.id);
      const full = await api("GET", `/api/jobs/${j.id}`);
      if (full.status === "failed" && !full.result) {
        failedJobs.set(j.id, full);
      }
      try { await cb(full); } catch (e) { fail(e); }
      changed = true;
    }
  }
  drawJobs(active);
  if (changed) await refresh();
  if (active.length || S.watch.size) pollTimer = setTimeout(pollJobs, 900);
}

const failedJobs = new Map();
function drawJobs(active) {
  const box = $("#jobs");
  box.replaceChildren();
  for (const j of active) {
    const pct = j.total ? Math.round((100 * (j.progress || 0)) / j.total) : null;
    box.append(h("div", { class: "job" },
      h("div", { class: "row" },
        h("span", { class: "lbl" }, j.status === "queued" ? "Waiting: " : "", j.label),
        h("span", {}, pct !== null ? `${pct}%` : `${Math.round(j.elapsed || 0)}s`, " ",
          h("button", { onclick: () => api("POST", `/api/jobs/${j.id}/cancel`).then(pollJobs) }, "Stop"))),
      h("div", { class: "bar" + (pct === null ? " indet" : "") }, h("i", { style: pct !== null ? `width:${pct}%` : "" }))));
  }
  for (const [id, j] of failedJobs) {
    box.append(h("div", { class: "job failed" },
      h("div", { class: "row" }, h("span", { class: "lbl" }, "Failed: ", j.label),
        h("button", { onclick: () => { failedJobs.delete(id); drawJobs(active); } }, "Close")),
      h("pre", {}, (j.log || []).slice(-14).join("\n"))));
  }
}

// ------------------------------------------------------------------ shell
function render() {
  const app = $("#app");
  if (!S.state) return;
  if (!S.state.project) { app.replaceChildren(welcome()); return; }
  const film = S.state.project.film;
  const items = [
    ["story", "🎬", "Story"], ["cast", "🧸", "Cast"], ["sets", "🏠", "Sets"],
    ["film", "⚙️", "Film"], ["screening", "🍿", "Screening room"], ["toolbox", "🧰", "Toolbox"],
  ];
  const nav = h("nav", { class: "nav", "aria-label": "Sections" },
    h("div", { class: "brand" }, reelIcon(), "dreamreel"),
    h("div", { class: "film-name" }, film.title || "Untitled film"),
    items.map(([k, ico, label]) => h("button", { class: S.view === k ? "on" : "", onclick: () => go(k) },
      h("span", { class: "ico", "aria-hidden": "true" }, ico), label)),
    h("div", { class: "spacer" }),
    h("div", { class: "hint" }, "Everything you make is saved as plain files in ",
      h("code", {}, S.state.project.root.split("/").slice(-1)[0]), "."));
  const views = { story: storyView, cast: castView, sets: setsView, film: filmView, screening: screeningView, toolbox: toolboxView };
  const main = h("main", { class: "main" }, (views[S.view] || storyView)());
  app.replaceChildren(h("div", { class: "shell" }, nav, main));
}

function reelIcon() {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 32 32");
  svg.setAttribute("class", "reel");
  svg.innerHTML = `<circle cx="16" cy="16" r="14" fill="#e4572e"/><circle cx="16" cy="16" r="4" fill="#fff8ef"/>
    <circle cx="16" cy="7.5" r="3" fill="#fff8ef"/><circle cx="16" cy="24.5" r="3" fill="#fff8ef"/>
    <circle cx="7.5" cy="16" r="3" fill="#fff8ef"/><circle cx="24.5" cy="16" r="3" fill="#fff8ef"/>`;
  return svg;
}

// ------------------------------------------------------------------ welcome
function welcome() {
  const title = h("input", { type: "text", placeholder: "e.g. The Last Cookie", "aria-label": "Film title" });
  const folder = h("input", { type: "text", placeholder: "the-last-cookie", "aria-label": "Folder name" });
  const example = h("input", { type: "checkbox", id: "ex" });
  title.addEventListener("input", () => { if (!folder.dataset.touched) folder.value = slug(title.value); });
  folder.addEventListener("input", () => (folder.dataset.touched = "1"));
  const create = async () => {
    try {
      await api("POST", "/api/projects", { title: title.value.trim(), name: folder.value.trim() || slug(title.value),
        example: example.checked });
      S.view = "story";
      await refresh();
    } catch (e) { fail(e); }
  };
  const path = h("input", { type: "text", placeholder: "/path/to/my-film", "aria-label": "Film folder" });
  return h("div", { class: "welcome" },
    h("div", { class: "row" }, reelIcon(), h("span", { class: "muted" }, "dreamreel studio")),
    h("h1", {}, "Your dream animated film, made easy."),
    h("p", { class: "lead" }, "Design characters, build sets, write what happens. dreamreel does the animation, the camera and the voices."),
    h("div", { class: "card stack" },
      h("h2", {}, "Start a new film"),
      h("div", { class: "fields" },
        h("label", { class: "field" }, "Title", title),
        h("label", { class: "field" }, "Folder", folder)),
      h("label", { class: "row small", for: "ex" }, example, "Start from the example film (“The Last Cookie”) to see how it works"),
      h("div", {}, h("button", { class: "btn primary", onclick: create }, "Create film")),
      h("p", { class: "muted small" }, "Created in ", h("code", {}, S.state.folder))),
    S.state.films.length ? h("div", { class: "card" }, h("h2", {}, "Open a film"),
      h("div", { class: "film-list" }, S.state.films.map((f) =>
        h("button", { onclick: () => api("POST", "/api/open", { path: f }).then(refresh).catch(fail) }, f)))) : null,
    h("div", { class: "card stack" }, h("h3", {}, "Open a film from another folder"),
      h("div", { class: "row" }, path, h("button", { class: "btn", onclick: () =>
        api("POST", "/api/open", { path: path.value }).then(refresh).catch(fail) }, "Open"))));
}

// ------------------------------------------------------------------ colour picker
function colorPicker(value, onPick, { skins = false } = {}) {
  const pal = colors();
  const names = Object.keys(pal).filter((n) => (skins ? n.startsWith("skin") : !n.startsWith("skin")));
  const wrap = h("div", { class: "swatches", role: "radiogroup" });
  const draw = (val) => {
    wrap.replaceChildren(
      ...names.map((n) => h("button", {
        class: "sw" + (val === n ? " on" : ""), style: `background:${pal[n]}`, title: pretty(n), "aria-label": pretty(n),
        role: "radio", "aria-checked": val === n ? "true" : "false",
        onclick: () => { onPick(n); draw(n); },
      })),
      h("input", { type: "color", class: "sw-custom", title: "Any colour", "aria-label": "Custom colour",
        value: val && val.startsWith("#") ? val : "#888888",
        oninput: (e) => { onPick(e.target.value); } }));
  };
  draw(value);
  return wrap;
}

function select(options, value, onChange, { blank, label } = {}) {
  const el = h("select", { "aria-label": label || "" },
    blank !== undefined ? h("option", { value: "" }, blank) : null,
    options.map((o) => {
      const [v, t] = Array.isArray(o) ? o : [o, pretty(o)];
      return h("option", { value: v, selected: v === value ? true : null }, t);
    }));
  if ((value !== undefined && value !== null && value !== "") || blank !== undefined) el.value = value ?? "";
  if (el.selectedIndex < 0 && el.options.length) el.selectedIndex = 0;
  el.addEventListener("change", () => onChange(el.value));
  return el;
}

function seg(options, value, onChange) {
  const wrap = h("div", { class: "seg", role: "radiogroup" });
  const draw = (val) => wrap.replaceChildren(...options.map((o) => {
    const [v, t] = Array.isArray(o) ? o : [o, pretty(o)];
    return h("button", { class: v === val ? "on" : "", role: "radio", "aria-checked": v === val ? "true" : "false",
      onclick: () => { onChange(v); draw(v); } }, t);
  }));
  draw(value);
  return wrap;
}

// ------------------------------------------------------------------ plugin schemas
// Every feature (character types, hair, props, actions, shots...) is a class in dreamreel; `dreamreel info`
// describes each one and its settings. The forms below are built from those descriptions, so features
// added in a film's extensions/ folder appear here without any change to the studio.
const plug = (kind) => (info().plugins && info().plugins[kind]) || [];
const plugOf = (kind, name) => plug(kind).find((p) => p.name === name);
const choicesOf = (kind) => plug(kind).map((p) => [p.name, p.label]);
const nameOf = (k) => (S.state.cast[k] && S.state.cast[k].name) || k;
const clone = (o) => JSON.parse(JSON.stringify(o || {}));

function multiChips(options, values, onChange) {
  const set = new Set(values || []);
  return h("div", { class: "chips" }, options.map((o) => {
    const [v, t] = Array.isArray(o) ? o : [o, pretty(o)];
    return h("button", { class: "chip" + (set.has(v) ? " on" : ""), "aria-pressed": set.has(v) ? "true" : "false",
      onclick: (e) => { set.has(v) ? set.delete(v) : set.add(v); e.target.classList.toggle("on"); onChange([...set]); } }, t);
  }));
}

// a control for one setting; ctx = { cast: keys in the scene, who, setInfo, name }
function paramField(p, value, onChange, ctx = {}) {
  const cat = catalog();
  const setInfo = ctx.setInfo || { marks: [], seats: [], props: [] };
  const places = new Set(cat.places);
  const marks = [...setInfo.marks.filter((m) => !places.has(m)), ...setInfo.marks.filter((m) => places.has(m))];
  const people = (ctx.cast || []).filter((k) => k !== ctx.who).map((k) => [k, "👤 " + nameOf(k)]);
  const opt = (blank) => (p.required ? { label: p.label } : { blank, label: p.label });
  let el;
  switch (p.type) {
    case "text":
      el = h("input", { type: "text", class: p.name === "line" ? "say-line" : "", value: value ?? "", placeholder: p.label,
        oninput: (e) => onChange(e.target.value) });
      break;
    case "number":
      el = h("input", { type: "number", min: p.min, max: p.max, step: p.step ?? "any", value: value ?? p.default ?? "",
        style: "width:96px", "aria-label": p.label, oninput: (e) => onChange(e.target.value === "" ? undefined : +e.target.value) });
      break;
    case "bool":
      el = h("label", { class: "row small" }, h("input", { type: "checkbox", checked: value ?? p.default ?? false,
        onchange: (e) => onChange(e.target.checked) }), ctx.inline ? p.label : "");
      break;
    case "color": el = colorPicker(value ?? p.default ?? "", onChange); break;
    case "skin": el = colorPicker(value ?? p.default ?? "skin2", onChange, { skins: true }); break;
    case "choice": {
      const num = typeof (p.choices || [])[0] === "number";
      const conv = (x) => (x === "" ? undefined : num ? +x : x);
      const ch = p.choices.map(String);
      if (p.default === undefined || p.default === null) {   // no default: the class decides unless you choose
        el = select(ch, value === undefined || value === null ? "" : String(value), (x) => onChange(conv(x)), { label: p.label, blank: "(automatic)" });
        break;
      }
      const v = String(value ?? p.default);
      el = ch.length <= 4 && !ctx.inline ? seg(ch, v, (x) => onChange(conv(x))) : select(ch, v, (x) => onChange(conv(x)), { label: p.label });
      break;
    }
    case "choices": el = multiChips(p.choices, value, onChange); break;
    case "extras": el = multiChips(choicesOf("extra"), value, onChange); break;
    case "items": el = multiChips(choicesOf("item"), value, onChange); break;
    case "hair": el = select(choicesOf("hair"), value ?? p.default, onChange, { label: p.label }); break;
    case "mood": el = select(choicesOf("mood"), value ?? (p.required ? p.default : ""), onChange, opt("(same mood)")); break;
    case "gesture": {
      const g = plug("gesture").filter((x) => !ctx.who || canDo(ctx.who, x));
      el = select(g.map((x) => [x.name, x.label]), value ?? p.default, onChange, { label: p.label });
      break;
    }
    case "shot": el = select(choicesOf("shot"), value ?? p.default, onChange, { label: p.label }); break;
    case "voice": el = voiceField(value, onChange, ctx); break;
    case "place": el = select(cat.places, value ?? p.default ?? ctx.defaultPlace ?? "center", onChange, { label: p.label }); break;
    case "facing":
      el = select([["camera", "the camera"], ["left", "left"], ["right", "right"], ["back", "the back"],
        ...marks.filter((m) => !places.has(m)).map((m) => [m, "📍 " + m])], value ?? p.default ?? "camera", onChange, { label: p.label });
      break;
    case "mark": el = select(marks.map((m) => [m, "📍 " + m]), value, onChange, opt("—")); break;
    case "seat": el = select(setInfo.seats.map((m) => [m, "🪑 " + m]), value, onChange, opt("—")); break;
    case "model": el = select((info().models || []).map((m) => [m, "🧍 " + m.replace(/^models\//, "")]), value ?? "", onChange,
      { label: p.label, blank: (info().models || []).length ? "—" : "(put .glb/.fbx/.obj files in models/)" }); break;
    case "outfit": {
      const body = (ctx.spec && ctx.spec.body) || "woman";
      el = pictureGrid(((assets().outfits || {})[body] || []).map((o) => [o, pretty(o), `${body}_${o}`]), value ?? p.default,
        onChange, "Download the people pack (Toolbox → 3D packs) to dress them");
      break;
    }
    case "species":
      el = pictureGrid((assets().species || []).map((s) => [s, pretty(s), `animal_${s}`]), value, onChange,
        "Download the animals pack (Toolbox → 3D packs) to choose one");
      break;
    case "motion": el = select((info().motions || []).map((m) => [m, "🎞 " + m]), value ?? "", onChange,
      { label: p.label, blank: (info().motions || []).length ? "—" : "(add clips to motions/)" }); break;
    case "surface": el = select((setInfo.surfaces || []).map((m) => [m, m]), value ?? "", onChange, opt("(the floor)")); break;
    case "thing": {
      const things = [...(setInfo.things || []).map((m) => [m, "✋ " + m]), ...choicesOf("item").filter(([n]) => !(setInfo.things || []).includes(n)).map(([n, l]) => [n, "＋ a new " + l])];
      el = select(things, value ?? "", onChange, opt("(what they're holding)"));
      break;
    }
    case "prop": el = select(setInfo.props || [], value, onChange, opt("—")); break;
    case "character": el = select(people, value ?? "", onChange, opt(p.name === "to" ? "(whoever is nearest)" : "(no one)")); break;
    case "target":
      el = select([...people, ...marks.map((m) => [m, "📍 " + m]), ["camera", "🎥 the camera"]], value ?? "", onChange, opt("(no one)"));
      break;
    default:
      el = plug(p.type).length ? select(choicesOf(p.type), value ?? p.default, onChange, opt("—"))
        : h("input", { type: "text", value: value ?? "", oninput: (e) => onChange(e.target.value) });
  }
  // a required menu shows its first choice: store it, so what you see is what's saved
  if (el.tagName === "SELECT" && (value === undefined || value === null || value === "") && el.value) onChange(el.value, true);
  return el;
}

const assets = () => info().assets || {};
const thumbUrl = (key) => (assets().thumbs || []).includes(key) ? `/thumbs/${key}.png` : null;

// pick one of several things by its picture (outfits, animals)
function pictureGrid(options, value, onChange, empty) {
  if (!options.length) return h("div", { class: "muted small" }, empty);
  const grid = h("div", { class: "pick-grid" });
  const draw = (v) => grid.replaceChildren(...options.map(([val, label, key]) => {
    const src = thumbUrl(key);
    return h("button", { type: "button", class: "pick" + (val === v ? " on" : ""), title: label,
      onclick: () => { onChange(val); draw(val); } },
      src ? h("img", { src, alt: "", loading: "lazy" }) : h("div", { class: "avatar sm" }, label.slice(0, 1).toUpperCase()),
      h("span", {}, label));
  }));
  draw(value);
  return grid;
}

function voiceField(value, onChange, ctx) {
  const cat = catalog();
  const inp = h("input", { type: "text", list: "voices", value: value || "", placeholder: cat.voices[0], oninput: (e) => onChange(e.target.value) });
  return h("div", { class: "row" }, inp, h("datalist", { id: "voices" }, cat.voices.map((v) => h("option", { value: v }))),
    h("button", { class: "btn sm", disabled: cat.voice_engine ? null : true, title: cat.voice_engine ? "" : "Voices need Piper: pip install piper-tts",
      onclick: () => job({ kind: "voice", voice: inp.value || cat.voices[0], text: `Hi, I'm ${ctx.name || "here"}. Nice to meet you!` },
        (j) => { const out = j.outputs[0]; if (out) new Audio(fileUrl(out, Date.now() / 1000)).play(); }) }, "▶ Hear"),
    cat.voice_engine ? null : h("span", { class: "muted small" }, "Voices need ", h("code", {}, "pip install piper-tts")));
}

// lay out a plugin's settings: small controls in a grid, wide ones (colours, chips) on their own rows
function paramForm(params, values, onChange, ctx = {}, skip = []) {
  const wide = new Set(["color", "skin", "extras", "items", "choices", "voice", "outfit", "species"]);
  const small = [], big = [];
  for (const p of params) {
    if (skip.includes(p.name)) continue;
    const field = paramField(p, values[p.name], (v, quiet) => onChange(p.name, v, quiet), ctx);
    const box = p.type === "bool" ? h("label", { class: "field row", title: p.help || null }, field, p.label)
      : h(wide.has(p.type) ? "div" : "label", { class: "field", title: p.help || null }, h("span", {}, p.label), field);
    (wide.has(p.type) ? big : small).push(box);
  }
  return h("div", { class: "stack" }, small.length ? h("div", { class: "fields" }, small) : null, big);
}

// ------------------------------------------------------------------ CAST
function castView() {
  const cast = S.state.cast;
  const keys = Object.keys(cast);
  if (S.castSel && !cast[S.castSel] && !S.castDraft[S.castSel]) S.castSel = null;
  return h("div", {},
    h("div", { class: "page-head" },
      h("div", {}, h("h1", {}, "Cast"), h("p", {}, "Who's in your film: people and animals from the 3D packs, toy figures, creatures, or your own models.")),
      keys.length ? h("button", { class: "btn", onclick: () => job({ kind: "cast" }, () => toast("Cast photo ready in the Screening room")) }, "📸 Cast photo") : null),
    packsCard({ compact: true }),
    h("div", { class: "cast-grid" },
      keys.map((k) => {
        const spec = S.castDraft[k] || cast[k];
        return h("div", { class: "cast-card" + (S.castSel === k ? " on" : ""), tabindex: 0, role: "button",
          onclick: () => { S.castSel = k; render(); }, onkeydown: (e) => e.key === "Enter" && ((S.castSel = k), render()) },
          h("div", { class: "fig" }, characterPicture(k, spec)), h("div", { class: "nm" }, spec.name || k),
          (spec.type && spec.type !== "toy") ? h("div", { class: "small muted" }, (plugOf("character", spec.type) || {}).label || spec.type) : null);
      }),
      h("div", { class: "cast-card add", tabindex: 0, role: "button", onclick: newCharacter }, h("div", { style: "font-size:28px" }, "+"), "New character")),
    S.castSel ? castEditor(S.castSel) : null);
}

// a picture straight from the asset packs, for people and animals (no rendering needed)
function packPicture(spec) {
  if (spec.type === "person") return thumbUrl(`${spec.body || "woman"}_${String(spec.outfit || "casual").toLowerCase()}`);
  if (spec.type === "animal" && spec.species) return thumbUrl(`animal_${String(spec.species).toLowerCase()}`);
  return null;
}

function characterPicture(key, spec, { live = false } = {}) {
  const t = plugOf("character", spec.type || "toy") || {};
  if (t.drawing === "toy") return h("div", { html: figureSVG(spec, colors()) });
  const thumb = packPicture(spec);
  if (thumb) return h("img", { src: thumb, alt: spec.name || key, class: "thumb-fig" });
  const r = renderOf(`renders/stills/cast_${key}.png`);
  if (r && !live) return h("img", { src: fileUrl(r.path, r.mtime), alt: spec.name || key, style: "object-fit:cover;border-radius:10px" });
  return h("div", { class: "avatar" }, (spec.name || key).slice(0, 1).toUpperCase());
}

function newCharacter() {
  const name = prompt("Character's name?");
  if (!name) return;
  const key = slug(name).replace(/-/g, "_") || "character";
  if (S.state.cast[key]) { toast("There's already a character called " + key); return; }
  const people = ((assets().outfits || {}).woman || []).length;
  S.castDraft[key] = people ? { name: name.trim(), type: "person", body: "woman", outfit: "casual" }   // Quaternius people
    : { name: name.trim(), skin: "skin2", hair: "short", hair_color: "brown", top: "teal", bottom: "navy" };
  S.castSel = key;
  saveCharacter(key).then(render);
}

async function saveCharacter(key) {
  const spec = S.castDraft[key];
  await api("PUT", `/api/cast/${key}`, { spec });
  delete S.castDraft[key];
  await refresh();
  toast(`Saved ${spec.name || key}`);
  const t = plugOf("character", spec.type || "toy") || {};
  if (t.drawing !== "toy" && !packPicture(spec)) {      // creatures, robots, your own models: show the real thing
    job({ kind: "cast", names: [key] }, () => render());
  }
}

function castEditor(key) {
  const spec = S.castDraft[key] || (S.castDraft[key] = clone(S.state.cast[key]));
  const types = plug("character");
  const tdef = plugOf("character", spec.type || "toy") || types[0];
  const live = (tdef && tdef.drawing === "toy") || ["person", "animal"].includes(spec.type);
  const figBox = h("div", {}, characterPicture(key, spec, { live }));
  const redraw = () => {
    if (!live) return;
    figBox.replaceChildren(characterPicture(key, spec, { live }));
    const card = $(".cast-card.on .fig");
    if (card) card.replaceChildren(characterPicture(key, spec));
  };
  const portrait = renderOf(`renders/stills/cast_${key}.png`);
  const form = paramForm(tdef ? tdef.params : [], spec, (k, v, quiet) => {
    if (v === undefined) delete spec[k]; else spec[k] = v;
    if (k === "body" && !quiet) { delete spec.outfit; render(); return; }    // outfits differ for women and men
    redraw();
  }, { name: spec.name || key, spec });
  return h("div", { class: "card", style: "margin-top:16px" },
    h("div", { class: "card-head" },
      h("h2", {}, spec.name || key),
      h("div", { class: "row" },
        h("button", { class: "btn danger ghost", onclick: async () => {
          if (!confirm(`Remove ${spec.name || key} from the cast? Scenes that use them will stop working.`)) return;
          await api("DELETE", `/api/cast/${key}`).catch(fail); delete S.castDraft[key]; S.castSel = null; refresh();
        } }, "Remove"),
        h("button", { class: "btn", onclick: async () => { await saveCharacter(key);
          job({ kind: "cast", names: [key] }, () => toast("Portrait rendered")); } }, "📸 Save & render portrait"),
        h("button", { class: "btn primary", onclick: () => saveCharacter(key).catch(fail) }, "Save"))),
    h("div", { class: "editor-split" },
      h("div", { class: "figure-big" }, live ? figBox : null,
        portrait && (live || true) ? h("img", { src: fileUrl(portrait.path, portrait.mtime), alt: "Rendered portrait",
          onclick: () => lightbox(fileUrl(portrait.path, portrait.mtime)) }) : (!live ? figBox : null),
        h("span", { class: "muted small" }, ["person", "animal"].includes(spec.type) ? "From the 3D pack (Quaternius, free). Render a portrait to see them in your film's look."
          : live ? (portrait ? "Drawing (live) and last render" : "Live drawing. Render a portrait to see the real thing.")
          : "Render a portrait to see this character.")),
      h("div", { class: "stack" },
        types.length > 1 ? h("label", { class: "field" }, h("span", {}, "Kind of character"),
          select(types.map((t) => [t.name, t.label + (t.source !== "built-in" ? " ✦" : "")]), spec.type || "toy",
            (v) => { if (v === "toy") delete spec.type; else spec.type = v; render(); }, { label: "Kind" }),
          tdef && tdef.description ? h("span", { class: "muted small", style: "font-weight:400" }, tdef.description) : null) : null,
        form)));
}

// ------------------------------------------------------------------ SETS
function setsView() {
  const sets = S.state.sets;
  const keys = Object.keys(sets);
  if (!S.setSel || (!sets[S.setSel] && !S.setDraft[S.setSel])) S.setSel = keys[0] || null;
  return h("div", {},
    h("div", { class: "page-head" },
      h("div", {}, h("h1", {}, "Sets"), h("p", {}, "The places where scenes happen. Put things in them; characters can walk to them, sit on them and talk next to them.")),
      h("button", { class: "btn", onclick: newSet }, "+ New set")),
    h("div", { class: "story" },
      h("div", { class: "list-rows card", style: "padding:8px" },
        keys.map((k) => h("button", { class: S.setSel === k ? "on" : "", onclick: () => { S.setSel = k; render(); } },
          h("span", {}, pretty(k)), h("span", { class: "muted small" }, (plugOf("set", sets[k].kind || "room") || {}).label || sets[k].kind))),
        !keys.length ? h("div", { class: "muted small", style: "padding:8px" }, "No sets yet.") : null),
      S.setSel ? setEditor(S.setSel) : h("div", { class: "empty" }, "Make a set to get started.")));
}

function newSet() {
  const name = prompt("Name the set (e.g. kitchen, park, office)");
  if (!name) return;
  const key = slug(name).replace(/-/g, "_");
  if (!key) return;
  S.setDraft[key] = { kind: "room", props: [{ type: "door", place: "back-left" }] };
  S.setSel = key;
  saveSet(key);
}

async function saveSet(key) {
  const spec = S.setDraft[key];
  const empty = (v) => v === undefined || v === null || v === "" || (Array.isArray(v) && !v.length);
  spec.props = (spec.props || []).map((p) => Object.fromEntries(Object.entries(p).filter(([, v]) => !empty(v))));
  if (spec.marks && !Object.keys(spec.marks).length) delete spec.marks;
  await api("PUT", `/api/sets/${key}`, { spec }).catch(fail);
  delete S.setDraft[key];
  await refresh();
  toast("Saved set " + pretty(key));
}

function setEditor(key) {
  const cat = catalog();
  const spec = S.setDraft[key] || (S.setDraft[key] = clone(S.state.sets[key]));
  spec.props = spec.props || [];
  const kind = plugOf("set", spec.kind || "room") || plug("set")[0];
  const outdoor = (spec.kind || "room") !== "room";
  const setInfo = info().sets[key] || { marks: [], seats: [], props: [] };
  if (S.selProp === undefined || S.selProp === null || S.selProp >= spec.props.length) S.selProp = spec.props.length ? 0 : null;
  if (!S.selCell) S.selCell = "center";
  const dirty = () => { const b = $("#set-save"); if (b) { b.classList.add("primary"); b.textContent = "Save changes"; } };
  const rerender = () => { render(); dirty(); };
  const placeOf = (p) => p.place || (plugOf("prop", p.type) || {}).default_place || "center";

  const grid = [["back-left", "back", "back-right"], ["left", "center", "right"], ["front-left", "front", "front-right"]];
  const stage = h("div", { class: "stage" + (outdoor ? " outdoor" : "") },
    h("div", { class: "wall" }, outdoor ? "far away" : "back wall"),
    grid.flat().map((pl) => h("div", { class: "cell" + (S.selCell === pl ? " on" : ""),
      onclick: (e) => { if (e.target.classList.contains("prop")) return; S.selCell = pl; render(); } },
      h("span", { class: "pl" }, pl),
      spec.props.map((p, i) => placeOf(p) === pl ? h("span", {
        class: "prop" + (S.selProp === i ? " on" : ""), onclick: () => { S.selProp = i; S.selCell = pl; render(); } },
        pretty(p.name || (plugOf("prop", p.type) || {}).label || p.type), p.chairs ? ` + ${p.chairs} chairs` : "") : null))),
    h("div", { class: "cam" }, "🎥 camera side"));

  const addType = select(plug("prop").map((p) => [p.name, p.label + (p.source !== "built-in" ? " ✦" : "")]), "", (v) => {
    if (!v) return;
    spec.props.push({ type: v, place: S.selCell });
    S.selProp = spec.props.length - 1;
    rerender();
  }, { blank: `+ Add to ${S.selCell}…`, label: "Add something" });

  const p = S.selProp !== null ? spec.props[S.selProp] : null;
  const pdef = p ? plugOf("prop", p.type) : null;
  const propPanel = p ? h("div", { class: "card", style: "background:var(--panel-2)" },
    h("div", { class: "card-head" }, h("div", {}, h("h3", {}, pretty(p.name || (pdef || {}).label || p.type)),
      pdef && pdef.description ? h("div", { class: "small muted" }, pdef.description) : null),
      h("button", { class: "btn sm danger ghost", onclick: () => { spec.props.splice(S.selProp, 1); S.selProp = null; rerender(); } }, "Remove")),
    pdef ? paramForm(pdef.params, p, (k, v, quiet) => {
      if (v === undefined) delete p[k]; else p[k] = k === "name" ? slug(String(v)) || undefined : v;
      if (k === "place") { S.selCell = v; if (!quiet) rerender(); } else if (!quiet) dirty();
    }, { setInfo, defaultPlace: placeOf(p) }) : h("div", { class: "banner err" }, `Unknown kind of thing: ${p.type}`))
    : h("p", { class: "muted small" }, "Pick a place on the floor plan, then add something to it.");

  const mapImg = renderOf(`renders/stills/plan_${key}.png`);
  const viewImg = renderOf(`renders/stills/view_${key}.png`);
  spec.marks = spec.marks || {};
  const nm = h("input", { type: "text", placeholder: "spot name", style: "width:130px" });
  const pl = select(cat.places, "center", () => {}, { label: "place" });
  return h("div", { class: "stack" },
    h("div", { class: "card" },
      h("div", { class: "card-head" }, h("h2", {}, pretty(key)),
        h("div", { class: "row" },
          h("button", { class: "btn danger ghost", onclick: async () => { if (!confirm(`Delete the set ${key}?`)) return; await api("DELETE", `/api/sets/${key}`).catch(fail); delete S.setDraft[key]; S.setSel = null; refresh(); } }, "Delete"),
          h("button", { class: "btn", onclick: async () => { await saveSet(key); job({ kind: "plan", set: key }, () => toast("Map ready")); } }, "🗺️ Map"),
          h("button", { class: "btn", onclick: async () => { await saveSet(key); job({ kind: "view", set: key }, () => toast("Picture ready")); } }, "📷 Picture"),
          h("button", { class: "btn", id: "set-save", onclick: () => saveSet(key) }, "Save"))),
      h("div", { class: "stack" },
        h("label", { class: "field" }, h("span", {}, "Kind of place"),
          select(plug("set").map((k) => [k.name, k.label + (k.source !== "built-in" ? " ✦" : "")]), spec.kind || "room",
            (v) => { spec.kind = v; rerender(); }, { label: "Kind" }),
          kind && kind.description ? h("span", { class: "muted small", style: "font-weight:400" }, kind.description) : null),
        kind ? paramForm(kind.params, spec, (k, v, quiet) => { if (v === undefined) delete spec[k]; else spec[k] = v; if (!quiet) dirty(); }) : null)),
    h("div", { class: "card" },
      h("div", { class: "card-head" }, h("h3", {}, "Floor plan"), addType),
      h("div", { class: "editor-split", style: "grid-template-columns: minmax(0,1fr) minmax(0,1fr)" }, stage, propPanel)),
    h("div", { class: "card stack" },
      h("h3", {}, "Spots characters can go to"),
      setInfo.error ? h("div", { class: "banner err" }, setInfo.error) : null,
      h("div", { class: "chips" }, setInfo.marks.map((m) => h("span", { class: "chip static" }, m))),
      setInfo.seats.length ? h("p", { class: "small muted", style: "margin:0" }, "Seats: ", setInfo.seats.join(", ")) : null,
      h("p", { class: "small muted", style: "margin:0" }, "Save to update this list. Add your own spot:"),
      h("div", { class: "row" },
        Object.entries(spec.marks).map(([n, place]) => h("span", { class: "chip static" }, `${n} → ${place} `,
          h("button", { class: "btn sm ghost", "aria-label": `remove ${n}`, onclick: () => { delete spec.marks[n]; rerender(); } }, "×"))),
        nm, pl, h("button", { class: "btn sm", onclick: () => { const n = slug(nm.value); if (!n) return; spec.marks[n] = pl.value; rerender(); } }, "Add spot"))),
    (mapImg || viewImg) ? h("div", { class: "pics" }, viewImg ? pic(viewImg, "Picture") : null, mapImg ? pic(mapImg, "Map with spot names") : null) : null);
}

function pic(r, caption) {
  const url = fileUrl(r.path, r.mtime);
  const isVid = r.path.endsWith(".mp4");
  return h("figure", { class: "pic", style: "margin:0" },
    isVid ? h("video", { src: url, controls: true, preload: "metadata" }) : h("img", { src: url, alt: caption, onclick: () => lightbox(url) }),
    h("figcaption", { class: "cap" }, h("span", {}, caption), h("span", {}, new Date(r.mtime * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }))));
}

// ------------------------------------------------------------------ STORY (scenes made of beats)
function storyView() {
  const scenes = S.state.scenes;
  const real = scenes.filter((s) => s.exists);
  if (!S.scene || !real.find((s) => s.file === S.scene)) S.scene = real[0] ? real[0].file : null;
  localStorage.setItem("dr.scene", S.scene || "");
  return h("div", {},
    h("div", { class: "page-head" },
      h("div", {}, h("h1", {}, "Story"), h("p", {}, "Your film, scene by scene. Say what happens, beat by beat; dreamreel acts it out and films it.")),
      h("div", { class: "row" },
        h("button", { class: "btn", onclick: () => job({ kind: "previz" }, (j) => j.status === "done" && (toast("Previz ready"), (S.screening = j.outputs.find((o) => o.endsWith(".mp4") && !o.includes("/previz/"))), go("screening"))) }, "▶ Previz the film"),
        h("button", { class: "btn primary", onclick: () => job({ kind: "render" }, (j) => j.status === "done" && (toast("Film rendered"), go("screening"))) }, "🎞️ Render the film"))),
    h("div", { class: "story" },
      h("div", { class: "stack" }, h("div", { class: "scene-list" }, scenes.map((s) => sceneItem(s, scenes))), newSceneForm()),
      S.scene ? sceneEditor(S.scene) : h("div", { class: "empty" }, "No scenes yet. Make your first one on the left.")));
}

const stemOf = (f) => f.replace(/\.(toml|py)$/, "");

function sceneItem(s, scenes) {
  const chk = S.checks[s.file];
  const meta = chk && !chk.error ? `${fmtT(chk.length)} · ${chk.events.filter((e) => e.kind === "say").length} lines` : (s.set ? pretty(s.set) : "");
  const order = () => scenes.filter((x) => x.in_film && x.exists).map((x) => stemOf(x.file));
  const move = async (d) => {
    const o = order();
    const k = o.indexOf(stemOf(s.file));
    if (k < 0 || k + d < 0 || k + d >= o.length) return;
    [o[k], o[k + d]] = [o[k + d], o[k]];
    await api("PUT", "/api/film", { scenes: o }).catch(fail);
    refresh();
  };
  const toggle = async (on) => {
    const o = order().filter((x) => on || x !== stemOf(s.file));
    if (on) o.push(stemOf(s.file));
    await api("PUT", "/api/film", { scenes: o }).catch(fail);
    refresh();
  };
  if (!s.exists) {
    return h("div", { class: "scene-item out" }, h("span", { class: "num" }, sceneNum(s.file)),
      h("div", { class: "grow" }, h("div", { class: "t" }, sceneLabel(s.file)), h("div", { class: "meta" }, "file missing")),
      h("button", { class: "btn sm", onclick: () => toggle(false) }, "Remove"));
  }
  return h("div", { class: "scene-item" + (S.scene === s.file ? " on" : "") + (s.in_film ? "" : " out"), tabindex: 0, role: "button",
    onclick: (e) => { if (e.target.closest(".ord, input")) return; S.scene = s.file; render(); } },
    h("span", { class: "num" }, sceneNum(s.file)),
    h("div", { class: "grow" }, h("div", { class: "t" }, sceneLabel(s.file), s.kind === "script" ? " 📜" : ""),
      h("div", { class: "meta" }, chk && chk.error ? "⚠️ needs a fix" : meta)),
    h("input", { type: "checkbox", checked: s.in_film, title: "In the film", "aria-label": "In the film", onchange: (e) => toggle(e.target.checked) }),
    s.in_film ? h("div", { class: "ord" }, h("button", { title: "Earlier", "aria-label": "Move earlier", onclick: () => move(-1) }, "▲"), h("button", { title: "Later", "aria-label": "Move later", onclick: () => move(1) }, "▼")) : null);
}

function newSceneForm() {
  const sets = Object.keys(S.state.sets);
  const name = h("input", { type: "text", placeholder: "e.g. the argument" });
  const setSel = select(sets, sets[0], () => {}, { label: "Set" });
  const cast = new Set();
  const create = async () => {
    if (!name.value.trim()) { name.focus(); return; }
    try {
      const r = await api("POST", "/api/scenes", { name: name.value, set: setSel.value, cast: [...cast] });
      S.scene = r.file;
      await refresh();
    } catch (e) { fail(e); }
  };
  return h("details", { class: "card" },
    h("summary", { style: "cursor:pointer;font-weight:700" }, "+ New scene"),
    h("div", { class: "stack", style: "margin-top:10px" },
      h("label", { class: "field" }, "What happens", name),
      h("label", { class: "field" }, "Where", setSel),
      h("div", { class: "field" }, h("span", {}, "Who's in it"),
        multiChips(Object.keys(S.state.cast).map((k) => [k, nameOf(k)]), [], (v) => { cast.clear(); v.forEach((x) => cast.add(x)); })),
      h("button", { class: "btn primary", onclick: create }, "Create scene")));
}

// ---------- editing one scene
const saveTimers = {};
function scheduleSave(file, now) {
  clearTimeout(saveTimers[file]);
  const status = $("#save-status");
  if (status) status.textContent = "saving…";
  saveTimers[file] = setTimeout(async () => {
    try {
      await api("PUT", `/api/scenes/${file}`, { spec: S.sceneSpec[file] });
      const st = $("#save-status");
      if (st) st.textContent = "saved";
      runCheck(file);
    } catch (e) { fail(e); }
  }, now ? 0 : 700);
}

async function loadScene(file) {
  const r = await api("GET", `/api/scenes/${file}`);
  if (r.script) S.sceneSpec[file] = { script: true };
  else S.sceneSpec[file] = r.spec;
  render();
  if (!S.checks[file]) runCheck(file);
}

function sceneEditor(file) {
  const spec = S.sceneSpec[file];
  if (!spec) { loadScene(file).catch(fail); return h("div", { class: "empty" }, "Opening…"); }
  const chk = S.checks[file];
  const head = sceneHeader(file, spec, chk);
  const parts = [head];
  if (spec.script) {
    parts.push(h("div", { class: "banner ok" }, "📜 This scene is a script written by a developer or an AI agent, for things beats can't say yet. ",
      "It plays, previews and renders here like any other scene. To change it, ask your AI agent."));
  } else {
    parts.push(beatsCard(file, spec, chk));
  }
  if (chk && chk.error && (spec.script || chk.beat === undefined || chk.beat === null)) {
    parts.push(h("div", { class: "banner err", role: "alert" }, chk.error));
  }
  if (chk && chk.warnings && chk.warnings.length) parts.push(h("div", { class: "banner warn" }, "⚠️ ", chk.warnings.join("; ")));
  parts.push(timelineCard(file, chk), picturesCard(file));
  return h("div", { class: "stack" }, parts.filter(Boolean));
}

function sceneHeader(file, spec, chk) {
  const meta = S.state.scenes.find((s) => s.file === file) || {};
  const edit = !spec.script;
  const sets = Object.keys(S.state.sets);
  const change = (k, v) => { spec[k] = v; scheduleSave(file); render(); };
  return h("div", { class: "card" },
    h("div", { class: "card-head" },
      h("div", {}, h("h2", {}, `${sceneNum(file)} · ${sceneLabel(file)}`),
        h("div", { class: "small muted" }, chk && !chk.error ? `${fmtT(chk.length)} · ${chk.cast.join(", ")}` : (meta.set ? `Set: ${pretty(meta.set)}` : ""))),
      h("div", { class: "row" }, edit ? h("span", { id: "save-status", class: "small muted" }) : null,
        h("button", { class: "btn ghost danger sm", onclick: async () => { if (!confirm(`Delete scene ${sceneLabel(file)}?`)) return; await api("DELETE", `/api/scenes/${file}`).catch(fail); delete S.sceneSpec[file]; S.scene = null; refresh(); } }, "Delete"))),
    edit ? h("div", { class: "fields" },
      h("label", { class: "field" }, h("span", {}, "Where"), select(sets, spec.set, (v) => change("set", v), { label: "Set" })),
      h("label", { class: "field" }, h("span", {}, "Time of day"),
        select(choicesOf("time"), spec.time_of_day || "day", (v) => change("time_of_day", v === "day" ? undefined : v), { label: "Time of day" })),
      h("label", { class: "field" }, h("span", {}, "Weather"),
        select(choicesOf("weather"), spec.weather || "clear", (v) => change("weather", v === "clear" ? undefined : v), { label: "Weather" })),
      spec.weather && spec.weather !== "clear" ? h("label", { class: "field" }, h("span", {}, "How much"),
        h("input", { type: "number", min: 0.2, max: 2.5, step: 0.1, style: "width:96px", value: spec.weather_strength ?? "",
          placeholder: "1", "aria-label": "Weather strength",
          onchange: (e) => change("weather_strength", e.target.value === "" ? undefined : +e.target.value) })) : null,
      h("div", { class: "field", style: "grid-column: span 2" }, h("span", {}, "Who's in it"),
        multiChips(Object.keys(S.state.cast).map((k) => [k, nameOf(k)]), spec.cast || [], (v) => {
          const gone = (spec.cast || []).filter((k) => !v.includes(k));
          const used = gone.filter((k) => (spec.beats || []).some((b) => b.who === k));
          if (used.length && !confirm(`${used.map(nameOf).join(", ")} still has beats in this scene. Remove anyway?`)) { render(); return; }
          spec.cast = v; scheduleSave(file); render();
        })),
      h("label", { class: "field" }, h("span", {}, "Look"),
        select(choicesOf("style"), spec.style || "", (v) => change("style", v || undefined), { label: "Scene look", blank: "(the film's look)" })),
      transitionFields(spec, change)) : null);
}

// how the scene comes in after the one before it (a transition plugin, plus the options it uses)
function transitionFields(spec, change) {
  const all = plug("transition");
  if (!all.length) return null;
  const t = plugOf("transition", spec.transition || "cut") || { uses: [], name: "cut" };
  const out = [h("label", { class: "field" }, h("span", {}, "Comes in with"),
    select(all.map((x) => [x.name, x.label]), spec.transition || "cut", (v) => {
      change("transition", v === "cut" ? undefined : v);
    }, { label: "Transition" }))];
  if (t.name !== "cut") {
    out.push(h("label", { class: "field" }, h("span", {}, "Seconds"),
      h("input", { type: "number", min: 0.1, max: 5, step: 0.1, style: "width:96px", value: spec.transition_duration ?? "",
        placeholder: String(t.default_duration ?? ""), "aria-label": "Transition seconds",
        onchange: (e) => change("transition_duration", e.target.value === "" ? undefined : +e.target.value) })));
    if ((t.uses || []).includes("direction")) {
      const dirs = t.name === "iris" ? ["out", "in"] : ["left", "right", "up", "down"];
      out.push(h("label", { class: "field" }, h("span", {}, "Direction"),
        select(dirs, spec.transition_direction || dirs[0], (v) => change("transition_direction", v === dirs[0] ? undefined : v), { label: "Direction" })));
    }
    if ((t.uses || []).includes("color")) {
      out.push(h("div", { class: "field", style: "grid-column: span 2" }, h("span", {}, "Colour"),
        colorPicker(spec.transition_color || "", (v) => change("transition_color", v || undefined))));
    }
  }
  return out;
}

function capsOf(who) {
  const spec = S.state.cast[who] || {};
  const t = plugOf("character", spec.type || "toy") || {};
  const caps = new Set(t.capabilities || []);
  const bodyParam = (t.params || []).find((p) => p.type === "body");
  if (bodyParam) {   // a character type built from body plans (like "creature")
    const plan = plugOf("body", spec.body || bodyParam.default);
    if (plan) plan.capabilities.forEach((c) => caps.add(c));
    if (spec.wings) { caps.add("wings"); caps.add("fly"); }
  }
  return caps;
}
const canDo = (who, item) => !(item.needs || []).some((n) => !capsOf(who).has(n));

function actionsFor(who) {
  return plug("action").filter((a) => (who === "_scene" ? a.scope === "scene" : a.scope !== "scene" && canDo(who, a)));
}

function beatRow(file, spec, i, chk) {
  const b = spec.beats[i];
  const cast = spec.cast || [];
  const setInfo = info().sets[spec.set] || { marks: [], seats: [], props: [] };
  const who = b.who || "_scene";
  const act = plugOf("action", b.do);
  const sel = S.selBeat[file] === i;
  const err = chk && chk.beat === i ? chk.error : null;
  const save = () => scheduleSave(file);
  const whoSel = select([...cast.map((k) => [k, "👤 " + nameOf(k)]), ["_scene", "🎬 Scene"]], who, (v) => {
    const wasScene = who === "_scene";
    if (v === "_scene") { delete b.who; } else b.who = v;
    if ((v === "_scene") !== wasScene) { const first = actionsFor(v)[0]; Object.keys(b).forEach((k) => k !== "who" && k !== "with_previous" && delete b[k]); b.do = first.name; }
    save(); render();
  }, { label: "Who" });
  const actSel = select(actionsFor(who).map((a) => [a.name, a.label + (a.source !== "built-in" ? " ✦" : "")]), b.do, (v) => {
    const keep = new Set(["who", "with_previous", "do"]);
    Object.keys(b).forEach((k) => !keep.has(k) && delete b[k]);
    b.do = v; save(); render();
  }, { label: "What" });
  const ekey = `${file}#${i}`;
  const open = S.expanded && S.expanded[ekey];
  const shown = (p, k) => open || act.params.length <= 5 || k < 3 || p.required || (b[p.name] !== undefined && b[p.name] !== "");
  const hidden = act ? act.params.filter((p, k) => !shown(p, k)).length : 0;
  const fields = act ? act.params.filter((p, k) => shown(p, k)).map((p, k) => {
    const ctx = { cast, who: b.who, setInfo, inline: true };
    const el = paramField(p, b[p.name], (v, quiet) => { if (v === undefined || v === "") delete b[p.name]; else b[p.name] = v; if (!quiet) save(); }, ctx);
    return p.type === "bool" ? el : h("span", { class: "bf", title: p.label }, k > 0 && p.type !== "text" ? h("small", { class: "bl" }, p.label.toLowerCase()) : null, el);
  }) : [h("span", { class: "banner err" }, `Unknown action: ${b.do}`)];
  if (act && (hidden || open) && act.params.length > 5) {
    fields.push(h("button", { class: "tool", onclick: () => { S.expanded = S.expanded || {}; S.expanded[ekey] = !open; render(); } },
      open ? "less" : `+ ${hidden} more`));
  }
  const move = (d) => { const j = i + d; if (j < 0 || j >= spec.beats.length) return; [spec.beats[i], spec.beats[j]] = [spec.beats[j], spec.beats[i]]; S.selBeat[file] = j; save(); render(); };
  return h("div", { class: "beat" + (sel ? " sel" : "") + (err ? " err" : "") + (b.with_previous ? " linked" : ""), id: `beat-${i}`,
    onclick: (e) => { if (e.target.closest("select, input, button, .chips")) return; S.selBeat[file] = sel ? null : i; render(); } },
    h("div", { class: "beat-main" },
      h("span", { class: "num" }, i + 1), whoSel, actSel, h("span", { class: "beat-fields" }, fields)),
    h("div", { class: "beat-tools" },
      i > 0 ? h("button", { class: "tool" + (b.with_previous ? " on" : ""), title: "Happens at the same time as the beat above",
        "aria-pressed": b.with_previous ? "true" : "false", onclick: () => { if (b.with_previous) delete b.with_previous; else b.with_previous = true; save(); render(); } }, "⇉ together") : null,
      h("button", { class: "tool", title: "Move up", "aria-label": "Move up", onclick: () => move(-1) }, "↑"),
      h("button", { class: "tool", title: "Move down", "aria-label": "Move down", onclick: () => move(1) }, "↓"),
      h("button", { class: "tool", title: "Duplicate", "aria-label": "Duplicate", onclick: () => { spec.beats.splice(i + 1, 0, clone(b)); S.selBeat[file] = i + 1; save(); render(); } }, "⧉"),
      h("button", { class: "tool danger", title: "Delete", "aria-label": "Delete", onclick: () => { spec.beats.splice(i, 1); S.selBeat[file] = null; save(); render(); } }, "✕")),
    err ? h("div", { class: "beat-err" }, err.replace(/^Beat \d+ \([^)]*\): /, "")) : null);
}

function beatsCard(file, spec, chk) {
  spec.beats = spec.beats || [];
  const cast = spec.cast || [];
  const nb = S.newBeat[file] || (S.newBeat[file] = { who: cast[0] || "_scene", do: cast[0] ? "say" : "wait" });
  if (nb.who !== "_scene" && !cast.includes(nb.who)) { nb.who = cast[0] || "_scene"; nb.do = cast[0] ? "say" : "wait"; }
  const setInfo = info().sets[spec.set] || { marks: [], seats: [], props: [] };
  const act = plugOf("action", nb.do) || actionsFor(nb.who)[0];
  const at = S.selBeat[file];
  const add = () => {
    const beat = { ...(nb.who !== "_scene" ? { who: nb.who } : {}), do: act.name };
    for (const p of act.params) if (nb[p.name] !== undefined && nb[p.name] !== "") beat[p.name] = nb[p.name];
    const missing = act.params.filter((p) => p.required && beat[p.name] === undefined && p.default === undefined);
    if (missing.length) { toast(`Fill in: ${missing.map((p) => p.label).join(", ")}`); return; }
    const pos = at !== null && at !== undefined ? at + 1 : spec.beats.length;
    spec.beats.splice(pos, 0, beat);
    S.selBeat[file] = at !== null && at !== undefined ? pos : null;
    for (const p of act.params) if (p.type === "text") delete nb[p.name];
    scheduleSave(file, true);
    render();
    const el = document.getElementById(`beat-${pos}`);
    if (el) el.scrollIntoView({ block: "nearest" });
  };
  const composer = h("div", { class: "composer" },
    h("div", { class: "row" },
      h("strong", { class: "small" }, at !== null && at !== undefined ? `Add after beat ${at + 1}:` : "Add a beat:"),
      select([...cast.map((k) => [k, "👤 " + nameOf(k)]), ["_scene", "🎬 Scene"]], nb.who, (v) => {
        nb.who = v; const a = actionsFor(v); if (!a.find((x) => x.name === nb.do)) nb.do = a[0].name; render(); }, { label: "Who" }),
      select(actionsFor(nb.who).map((a) => [a.name, a.label + (a.source !== "built-in" ? " ✦" : "")]), act.name, (v) => { nb.do = v; render(); }, { label: "What" }),
      act.params.filter((p, k) => S.composerMore || act.params.length <= 5 || k < 3 || p.required).map((p, k) => {
        const el = paramField(p, nb[p.name], (v) => { nb[p.name] = v; }, { cast, who: nb.who === "_scene" ? null : nb.who, setInfo, inline: true });
        if (p.type === "text") el.addEventListener("keydown", (e) => e.key === "Enter" && add());
        return p.type === "bool" ? el : h("span", { class: "bf" }, k > 0 && p.type !== "text" ? h("small", { class: "bl" }, p.label.toLowerCase()) : null, el);
      }),
      act.params.length > 5 ? h("button", { class: "tool", onclick: () => { S.composerMore = !S.composerMore; render(); } },
        S.composerMore ? "fewer options" : "more options") : null,
      h("button", { class: "btn primary sm", onclick: add }, "Add ⏎")),
    !cast.length ? h("div", { class: "small muted", style: "margin-top:6px" }, "Add people to the scene above to give them things to do.") : null);
  return h("div", { class: "card" },
    h("div", { class: "card-head" }, h("h3", {}, "What happens"),
      h("span", { class: "small muted" }, "Beats play in order. ⇉ together starts a beat with the one above. Click a beat to add after it.")),
    h("div", { class: "beats" }, spec.beats.length ? spec.beats.map((_, i) => beatRow(file, spec, i, chk))
      : h("div", { class: "empty" }, "Nothing happens yet. Add the first beat below.")),
    h("div", { style: "height:10px" }), composer);
}

const checkSeen = {};  // scene file -> id of the newest check applied (results can arrive out of order)
async function runCheck(file) {
  return job({ kind: "check", scene: file }, (j) => {
    if ((checkSeen[file] || 0) > j.id) return;
    checkSeen[file] = j.id;
    const r = (j.result || [])[0];
    S.checks[file] = r || { error: (j.log || []).slice(-6).join("\n") || "The check failed" };
  });
}

function timelineCard(file, chk) {
  const t = S.playhead[file] ?? null;
  return h("div", { class: "card" },
    h("div", { class: "card-head" }, h("h3", {}, "Timeline"),
      h("div", { class: "row" },
        h("button", { class: "btn sm", onclick: () => runCheck(file) }, "↻ Check"),
        h("button", { class: "btn sm", disabled: t === null ? true : null, onclick: () => job({ kind: "still", scene: file, times: [t] }, () => toast("Frame ready")) },
          t === null ? "📷 Click the timeline to pick a moment" : `📷 Frame at ${fmtT(t)}`),
        h("button", { class: "btn sm", onclick: () => job({ kind: "contact", scene: file, count: 6 }, () => toast("Contact sheet ready")) }, "🖼️ Contact sheet"),
        h("button", { class: "btn sm", onclick: () => job({ kind: "previz", scene: file }, () => toast("Previz ready")) }, "▶ Previz scene"),
        h("button", { class: "btn sm primary", onclick: () => job({ kind: "render", scene: file }, () => toast("Scene rendered")) }, "🎞️ Render scene"))),
    chk && !chk.error ? timeline(file, chk) : h("div", { class: "empty" }, chk ? "Fix the problem above to see the timeline." : "Checking…"));
}

function picturesCard(file) {
  const stem = stemOf(file);
  const contact = renderOf(`renders/stills/${stem}_contact.png`);
  const stills = rendersFor(`renders/stills/${stem}_`).filter((r) => !r.path.endsWith("_contact.png")).slice(0, 3);
  const previz = renderOf(`renders/previz/${stem}.mp4`);
  const final = renderOf(`renders/final/${stem}.mp4`);
  if (!(contact || stills.length || previz || final)) return null;
  return h("div", { class: "card" }, h("h3", { style: "margin-bottom:10px" }, "Pictures and videos"),
    h("div", { class: "pics" },
      final ? pic(final, "Final render") : null, previz ? pic(previz, "Previz") : null,
      contact ? pic(contact, "Contact sheet") : null,
      stills.map((r) => pic(r, "Frame at " + r.path.match(/_([\d.]+)s\.png$/)[1].replace(/^0+(?=\d)/, "") + " s"))));
}

// ------------------------------------------------------------------ TOOLBOX (every feature, from the plugins)
const KIND_TITLES = [
  ["character", "Kinds of character"], ["hair", "Hair"], ["extra", "Extras"], ["mood", "Moods"], ["gesture", "Gestures"],
  ["action", "Things characters and scenes can do"], ["set", "Kinds of place"], ["biome", "Landscapes"],
  ["scenery", "Nature and scenery"], ["prop", "Things in sets"], ["item", "Things on tables"],
  ["time", "Times of day"], ["weather", "Weather"], ["style", "Looks"], ["body", "Body plans"],
  ["shot", "Camera shots"], ["move", "Camera moves"], ["transition", "Transitions"], ["screen", "Screen effects"],
  ["voice", "Voice engines"],
];

// Quaternius's free (CC0) packs: what's downloaded, and pictures of the people and animals
function packsCard({ compact = false } = {}) {
  const packs = assets().packs || {};
  const names = Object.keys(packs);
  if (!names.length) return null;
  const missing = names.filter((n) => !packs[n].installed);
  const after = () => job({ kind: "thumbs" }, async () => { await api("GET", "/api/info").catch(fail); await refresh(); });
  const get = (pack) => job({ kind: "assets", pack }, async () => { toast(`Downloaded ${pack || "the 3D packs"}`); after(); });
  if (compact) {
    if (packs.women && packs.women.installed && packs.men && packs.men.installed) return null;
    return h("div", { class: "banner ok", style: "margin-bottom:14px" },
      h("div", {}, h("strong", {}, "Real people and animals: "), "download Quaternius's free 3D packs (women and men in many outfits, ",
        "dogs, horses, deer...) and cast them here, walking and acting with their own animation."),
      h("button", { class: "btn primary", onclick: () => ["women", "men", "animals"].forEach(get) }, "⬇ Get people and animals"));
  }
  const thumbs = assets().thumbs || [];
  return h("div", { class: "card" },
    h("div", { class: "card-head" },
      h("h3", {}, "3D packs ", h("span", { class: "muted small" }, "(Quaternius, free CC0: downloaded to your computer, not into the film)")),
      missing.length ? h("button", { class: "btn primary", onclick: () => get(null) }, `⬇ Download all (${missing.length})`) : null),
    h("div", { class: "toolbox" }, names.map((n) => h("div", { class: "tool-item" },
      h("div", { class: "ti-name" }, pretty(n), " ", packs[n].installed ? h("span", { class: "ok-tag" }, "✓ ready")
        : h("button", { class: "btn sm", onclick: () => get(n) }, "⬇ Get")),
      h("div", { class: "small muted" }, packs[n].about)))),
    thumbs.length ? h("div", { class: "pick-grid gallery", style: "margin-top:12px" },
      thumbs.map((t) => h("div", { class: "pick", title: pretty(t) }, h("img", { src: `/thumbs/${t}.png`, alt: "", loading: "lazy" }),
        h("span", {}, pretty(t.replace(/^animal_/, "")))))) : null);
}

function toolboxView() {
  const all = info().plugins || {};
  const custom = Object.values(all).flat().filter((p) => p.source !== "built-in").length;
  return h("div", {},
    h("div", { class: "page-head" },
      h("div", {}, h("h1", {}, "Toolbox"), h("p", {}, "Everything your film can use. Items marked ✦ were added for this film.")),
      h("button", { class: "btn", onclick: async () => { await api("GET", "/api/info").catch(fail); await refresh(); toast("Toolbox reloaded"); } }, "↻ Reload")),
    packsCard(),
    h("div", { class: "banner ok", style: "margin-bottom:14px" },
      h("div", {}, h("strong", {}, "Need something that isn't here?"), " Ask your AI agent for it (a new prop, gesture, kind of character, camera shot...). ",
        "It adds it to this film's ", h("code", {}, "extensions"), " folder and it appears in these menus. ",
        custom ? `This film has ${custom} addition${custom > 1 ? "s" : ""}.` : "")),
    KIND_TITLES.filter(([k]) => (all[k] || []).length).map(([k, title]) => h("div", { class: "card" },
      h("h3", { style: "margin-bottom:10px" }, title, " ", h("span", { class: "muted small" }, `(${all[k].length})`)),
      h("div", { class: "toolbox" }, all[k].map((p) => h("div", { class: "tool-item" + (p.source !== "built-in" ? " custom" : "") },
        h("div", { class: "ti-name" }, p.label, p.source !== "built-in" ? " ✦" : ""),
        p.description ? h("div", { class: "small muted" }, p.description) : null))))));
}

// ---------- the visual timeline
function timeline(file, chk) {
  const L = Math.max(chk.length, 1);
  const pct = (t) => `${(100 * t) / L}%`;
  const rulerStep = L > 60 ? 10 : L > 25 ? 5 : L > 10 ? 2 : 1;
  const ruler = h("div", { class: "tl-ruler" },
    Array.from({ length: Math.floor(L / rulerStep) + 1 }, (_, i) => h("span", { style: `left:${pct(i * rulerStep)}` }, `${i * rulerStep}s`)));
  const lanes = [];
  const lane = (who, blocks) => {
    const l = h("div", { class: "tl-lane" }, blocks);
    l.addEventListener("click", (e) => {
      const r = l.getBoundingClientRect();
      const t = Math.max(0, Math.min(L, ((e.clientX - r.left) / r.width) * L));
      S.playhead[file] = Math.round(t * 10) / 10;
      render();
    });
    lanes.push(h("div", { class: "tl-track" }, h("div", { class: "who" }, who), l));
  };
  const cuts = chk.events.filter((e) => e.kind === "cut");
  lane("🎥 Camera", cuts.map((c, i) => {
    const end = i + 1 < cuts.length ? cuts[i + 1].t : L;
    return h("div", { class: "tl-b cut", style: `left:${pct(c.t)};width:${pct(end - c.t)}`, title: `${fmtT(c.t)} ${c.shot}` }, c.shot.replace(/_/g, " "));
  }));
  for (const who of chk.cast) {
    const evs = chk.events.filter((e) => e.who === who);
    lane(who, evs.map((e) => {
      const w = Math.max((e.end ?? e.t + 0.6) - e.t, 0.3);
      const text = e.kind === "say" ? `“${e.line}”` : e.kind === "gesture" ? pretty(e.gesture) : "walks";
      const hl = e.beat !== null && e.beat !== undefined && S.selBeat[file] === e.beat;
      return h("div", { class: `tl-b ${e.kind}` + (hl ? " hl" : ""), style: `left:${pct(e.t)};width:${pct(w)}`, title: `${fmtT(e.t)} ${who}: ${text}`,
        onclick: (ev) => {
          if (e.beat === null || e.beat === undefined) return;
          ev.stopPropagation();
          S.selBeat[file] = e.beat;
          S.playhead[file] = Math.round(e.t * 10) / 10;
          render();
          const el = document.getElementById(`beat-${e.beat}`);
          if (el) el.scrollIntoView({ block: "center", behavior: "smooth" });
        } }, text);
    }));
  }
  const caps = chk.events.filter((e) => e.kind === "caption");
  if (caps.length) lane("Captions", caps.map((e) => h("div", { class: "tl-b caption", style: `left:${pct(e.t)};width:${pct(e.end - e.t)}` }, e.text)));
  const t = S.playhead[file];
  const inner = h("div", { class: "tl", style: `min-width:${Math.round(90 + L * 46)}px` }, ruler, lanes);
  const box = h("div", { class: "tl-scroll" }, inner);
  if (t !== undefined && t !== null) {
    const head = h("div", { class: "tl-head", "data-t": fmtT(t) });
    head.style.left = `calc(90px + (100% - 90px) * ${t / L})`;
    inner.append(head);
  }
  return box;
}

// ------------------------------------------------------------------ FILM settings
function filmView() {
  const film = JSON.parse(JSON.stringify(S.state.project.film));
  const res = (film.resolution || [1920, 1080]).join("x");
  const save = async () => {
    await api("PUT", "/api/film", { title: film.title, fps: film.fps, resolution: film.resolution, music: film.music || null,
      style: film.style && film.style !== "toy" ? film.style : null,
      voices: film.voices === false ? false : null }).catch(fail);
    await refresh();
    toast("Saved");
  };
  const music = film.music || {};
  return h("div", {},
    h("div", { class: "page-head" }, h("div", {}, h("h1", {}, "Film"), h("p", {}, "Settings for the whole film."))),
    h("div", { class: "card stack" },
      h("div", { class: "fields" },
        h("label", { class: "field" }, "Title", h("input", { type: "text", value: film.title || "", oninput: (e) => (film.title = e.target.value) })),
        h("label", { class: "field" }, "Picture", select([["1280x720", "HD 720p"], ["1920x1080", "Full HD 1080p"], ["3840x2160", "4K"], ["1080x1920", "Vertical (phones)"], ["1080x1080", "Square"]], res,
          (v) => (film.resolution = v.split("x").map(Number)))),
        h("label", { class: "field" }, "Frames per second", select([["24", "24 (film)"], ["25", "25"], ["30", "30"]], String(film.fps || 24), (v) => (film.fps = +v))),
        h("label", { class: "field" }, "Look", select(choicesOf("style"), film.style || "toy", (v) => (film.style = v), { label: "Look" }))),
      h("div", { class: "fields" },
        h("label", { class: "field" }, "Music", select(S.state.music, music.file || "", (v) => (film.music = v ? { file: v, volume: music.volume || 0.35 } : null), { blank: S.state.music.length ? "(no music)" : "(put music files in audio/music)" })),
        h("label", { class: "field" }, "Music volume", h("input", { type: "range", min: 0.05, max: 1, step: 0.05, value: music.volume || 0.35,
          oninput: (e) => { if (film.music) film.music.volume = +e.target.value; } })),
        h("label", { class: "field row" }, h("input", { type: "checkbox", checked: film.voices !== false, onchange: (e) => (film.voices = e.target.checked) }), "Characters speak out loud")),
      h("div", {}, h("button", { class: "btn primary", onclick: save }, "Save"))),
    h("div", { class: "card", style: "margin-top:14px" },
      h("h3", {}, "Make the film"),
      h("p", { class: "muted" }, "Previz is quick and rough: check timing, voices and camera. The final render is the real thing and takes longer. Scenes you haven't changed are not rendered again."),
      h("div", { class: "row" },
        h("button", { class: "btn", onclick: () => job({ kind: "previz" }, () => go("screening")) }, "▶ Previz the film"),
        h("button", { class: "btn primary", onclick: () => job({ kind: "render" }, () => go("screening")) }, "🎞️ Render the film"),
        h("button", { class: "btn ghost", onclick: () => job({ kind: "render", percent: 50 }, () => go("screening")) }, "Render at half size"))));
}

// ------------------------------------------------------------------ SCREENING room
function screeningView() {
  const all = S.state.renders || [];
  const films = all.filter((r) => /^renders\/[^/]+\.mp4$/.test(r.path));
  const scenes = all.filter((r) => /^renders\/(previz|final)\/.+\.mp4$/.test(r.path));
  const stills = all.filter((r) => r.path.endsWith(".png")).slice(0, 24);
  const vids = [...films, ...scenes];
  if (!S.screening || !vids.find((v) => v.path === S.screening)) S.screening = vids[0] ? vids[0].path : null;
  const cur = vids.find((v) => v.path === S.screening);
  const labelOf = (p) => {
    if (/^renders\/[^/]+\.mp4$/.test(p)) return (p.includes("-previz") ? "Film (previz)" : "Film") + " · " + p.split("/").pop();
    const [, kind, f] = p.match(/^renders\/(\w+)\/(.+)\.mp4$/);
    return `${kind === "final" ? "Scene" : "Scene previz"} · ${sceneLabel(f)}`;
  };
  return h("div", {},
    h("div", { class: "page-head" }, h("div", {}, h("h1", {}, "Screening room"), h("p", {}, "Everything you've rendered."))),
    vids.length ? h("div", { class: "story" },
      h("div", { class: "card list-rows", style: "padding:8px" }, vids.map((v) =>
        h("button", { class: v.path === S.screening ? "on" : "", onclick: () => { S.screening = v.path; render(); } },
          h("span", {}, labelOf(v.path)), h("span", { class: "muted small" }, `${(v.size / 1e6).toFixed(1)} MB`)))),
      h("div", { class: "card screen" },
        cur ? h("video", { src: fileUrl(cur.path, cur.mtime), controls: true, autoplay: false, preload: "metadata" }) : null,
        cur ? h("div", { class: "row", style: "margin-top:10px;justify-content:space-between" },
          h("strong", {}, labelOf(cur.path)),
          h("a", { href: fileUrl(cur.path, cur.mtime), download: cur.path.split("/").pop(), class: "btn sm" }, "⬇ Download")) : null))
      : h("div", { class: "empty" }, "Nothing rendered yet. Go to Story and press ", h("strong", {}, "Previz the film"), "."),
    stills.length ? h("div", { class: "card", style: "margin-top:14px" }, h("h3", { style: "margin-bottom:10px" }, "Pictures"),
      h("div", { class: "pics" }, stills.map((r) => pic(r, r.path.split("/").pop().replace(/\.png$/, "").replace(/_/g, " "))))) : null);
}

// ------------------------------------------------------------------ start
window.addEventListener("beforeunload", (e) => {
  if (Object.values(saveTimers).some(Boolean) && $("#save-status") && $("#save-status").textContent === "saving…") { e.preventDefault(); e.returnValue = ""; }
});
refresh().then(pollJobs).catch(fail);
