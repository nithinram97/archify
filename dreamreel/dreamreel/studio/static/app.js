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

const q = (s) => JSON.stringify(String(s));              // a Python string literal
const pretty = (s) => String(s).replace(/[-_]/g, " ");
const sceneLabel = (file) => pretty(file.replace(/\.py$/, "").replace(/^\d+_/, ""));
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
  sceneText: {},          // scene file -> text as last loaded/saved
  draft: {},              // scene file -> unsaved text
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
    ["film", "⚙️", "Film"], ["screening", "🍿", "Screening room"],
  ];
  const nav = h("nav", { class: "nav", "aria-label": "Sections" },
    h("div", { class: "brand" }, reelIcon(), "dreamreel"),
    h("div", { class: "film-name" }, film.title || "Untitled film"),
    items.map(([k, ico, label]) => h("button", { class: S.view === k ? "on" : "", onclick: () => go(k) },
      h("span", { class: "ico", "aria-hidden": "true" }, ico), label)),
    h("div", { class: "spacer" }),
    h("div", { class: "hint" }, "Everything you make is saved as plain files in ",
      h("code", {}, S.state.project.root.split("/").slice(-1)[0]), "."));
  const views = { story: storyView, cast: castView, sets: setsView, film: filmView, screening: screeningView };
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
  el.value = value ?? "";
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

// ------------------------------------------------------------------ CAST
function castView() {
  const cast = S.state.cast;
  const keys = Object.keys(cast);
  if (S.castSel && !cast[S.castSel] && !S.castDraft[S.castSel]) S.castSel = null;
  const grid = h("div", { class: "cast-grid" },
    keys.map((k) => {
      const spec = S.castDraft[k] || cast[k];
      return h("div", { class: "cast-card" + (S.castSel === k ? " on" : ""), tabindex: 0, role: "button",
        onclick: () => { S.castSel = k; render(); }, onkeydown: (e) => e.key === "Enter" && (S.castSel = k, render()) },
        h("div", { class: "fig", html: figureSVG(spec, colors()) }),
        h("div", { class: "nm" }, spec.name || k));
    }),
    h("div", { class: "cast-card add", tabindex: 0, role: "button", onclick: newCharacter }, h("div", { style: "font-size:28px" }, "+"), "New character"));
  return h("div", {},
    h("div", { class: "page-head" },
      h("div", {}, h("h1", {}, "Cast"), h("p", {}, "Who's in your film. Pick a look; the drawing updates as you go.")),
      keys.length ? h("button", { class: "btn", onclick: () => job({ kind: "cast" }, () => toast("Cast photo ready in the Screening room")) }, "📸 Cast photo") : null),
    grid,
    S.castSel ? castEditor(S.castSel) : null);
}

function newCharacter() {
  const name = prompt("Character's name?");
  if (!name) return;
  const key = slug(name).replace(/-/g, "_") || "character";
  if (S.state.cast[key]) { toast("There's already a character called " + key); return; }
  S.castDraft[key] = { name: name.trim(), body: "bean", skin: "skin2", hair: "short", hair_color: "brown",
    top: "teal", bottom: "navy", shoes: "charcoal", extras: [] };
  S.castSel = key;
  saveCharacter(key).then(render);
}

async function saveCharacter(key) {
  const spec = S.castDraft[key];
  await api("PUT", `/api/cast/${key}`, { spec });
  delete S.castDraft[key];
  await refresh();
  toast(`Saved ${spec.name || key}`);
}

function castEditor(key) {
  const cat = catalog();
  const saved = S.state.cast[key] || {};
  const spec = S.castDraft[key] || (S.castDraft[key] = JSON.parse(JSON.stringify(saved)));
  const figBox = h("div", { html: figureSVG(spec, colors()) });
  const redraw = () => {
    figBox.innerHTML = figureSVG(spec, colors());
    const card = document.querySelectorAll(".cast-card.on .fig")[0];
    if (card) card.innerHTML = figureSVG(spec, colors());
  };
  const set = (k) => (v) => { spec[k] = v; redraw(); };
  const portrait = renderOf(`renders/stills/cast_${key}.png`);
  const extras = new Set(spec.extras || []);
  const voice = h("input", { type: "text", list: "voices", value: spec.voice || "", placeholder: cat.voices[0],
    oninput: (e) => (spec.voice = e.target.value) });
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
      h("div", { class: "figure-big" }, figBox,
        portrait ? h("img", { src: fileUrl(portrait.path, portrait.mtime), alt: "Rendered portrait",
          onclick: () => lightbox(fileUrl(portrait.path, portrait.mtime)) }) : null,
        h("span", { class: "muted small" }, portrait ? "Drawing (live) and last render" : "Live drawing. Render a portrait to see the real thing.")),
      h("div", { class: "stack" },
        h("div", { class: "fields" },
          h("label", { class: "field" }, "Name", h("input", { type: "text", value: spec.name || "",
            oninput: (e) => { spec.name = e.target.value; } })),
          h("label", { class: "field" }, `Height (${(spec.height || 1).toFixed(2)})`,
            h("input", { type: "range", min: 0.7, max: 1.3, step: 0.05, value: spec.height || 1,
              oninput: (e) => { spec.height = +e.target.value; e.target.previousSibling.textContent = `Height (${(+e.target.value).toFixed(2)})`; redraw(); } })),
          h("label", { class: "field" }, "Body", seg(cat.bodies, spec.body || "bean", set("body"))),
          h("label", { class: "field" }, "Outfit", seg(cat.outfits, spec.outfit || "shirt", set("outfit"))),
          h("label", { class: "field" }, "Eyes", seg(cat.eyes, spec.eyes || "normal", set("eyes"))),
          h("label", { class: "field" }, "Hair", select(cat.hair, spec.hair || "short", set("hair")))),
        h("label", { class: "field" }, "Skin", colorPicker(spec.skin || "skin2", set("skin"), { skins: true })),
        h("label", { class: "field" }, "Hair colour", colorPicker(spec.hair_color || "brown", set("hair_color"))),
        h("label", { class: "field" }, spec.outfit === "dress" ? "Dress" : "Top", colorPicker(spec.top || "blue", set("top"))),
        spec.outfit === "dress" ? null : h("label", { class: "field" }, "Trousers", colorPicker(spec.bottom || "navy", set("bottom"))),
        h("label", { class: "field" }, "Shoes", colorPicker(spec.shoes || "charcoal", set("shoes"))),
        h("div", { class: "field" }, h("span", {}, "Extras"),
          h("div", { class: "chips" }, cat.extras.map((x) => h("button", { class: "chip" + (extras.has(x) ? " on" : ""),
            "aria-pressed": extras.has(x) ? "true" : "false",
            onclick: (e) => { extras.has(x) ? extras.delete(x) : extras.add(x); spec.extras = [...extras];
              e.target.classList.toggle("on"); redraw(); } }, pretty(x))))),
        h("div", { class: "field" }, h("span", {}, "Voice"),
          h("div", { class: "row" }, voice,
            h("datalist", { id: "voices" }, cat.voices.map((v) => h("option", { value: v }))),
            h("button", { class: "btn sm", disabled: !cat.voice_engine ? true : null, title: cat.voice_engine ? "" : "Install voices: pip install piper-tts",
              onclick: () => job({ kind: "voice", voice: voice.value || cat.voices[0], text: `Hi, I'm ${spec.name || key}. Nice to meet you!` },
                (j) => { const out = j.outputs[0]; if (out) new Audio(fileUrl(out, Date.now() / 1000)).play(); }) }, "▶ Hear"),
            !cat.voice_engine ? h("span", { class: "muted small" }, "Voices need ", h("code", {}, "pip install piper-tts")) : null)))));
}

// ------------------------------------------------------------------ SETS
function setsView() {
  const sets = S.state.sets;
  const keys = Object.keys(sets);
  if (!S.setSel || (!sets[S.setSel] && !S.setDraft[S.setSel])) S.setSel = keys[0] || null;
  return h("div", {},
    h("div", { class: "page-head" },
      h("div", {}, h("h1", {}, "Sets"), h("p", {}, "The places where scenes happen. Put furniture in the room; characters can walk to it, sit on it and talk next to it.")),
      h("button", { class: "btn", onclick: newSet }, "+ New set")),
    h("div", { class: "story" },
      h("div", { class: "list-rows card", style: "padding:8px" },
        keys.map((k) => h("button", { class: S.setSel === k ? "on" : "", onclick: () => { S.setSel = k; render(); } },
          h("span", {}, pretty(k)), h("span", { class: "muted small" }, sets[k].kind || "room"))),
        !keys.length ? h("div", { class: "muted small", style: "padding:8px" }, "No sets yet.") : null),
      S.setSel ? setEditor(S.setSel) : h("div", { class: "empty" }, "Make a set to get started.")));
}

function newSet() {
  const name = prompt("Name the set (e.g. kitchen, park, office)");
  if (!name) return;
  const key = slug(name).replace(/-/g, "_");
  if (!key) return;
  const outdoor = confirm("Is it outdoors? (OK = outdoors, Cancel = a room)");
  S.setDraft[key] = outdoor
    ? { kind: "outdoor", ground: "grass", trees: 6, props: [{ type: "bench", place: "back" }] }
    : { kind: "room", size: "medium", walls: "cream", floor: "wood", props: [{ type: "door", place: "back-left" }] };
  S.setSel = key;
  saveSet(key);
}

async function saveSet(key) {
  const spec = S.setDraft[key];
  spec.props = (spec.props || []).map((p) => Object.fromEntries(Object.entries(p).filter(([, v]) => v !== "" && v !== null && !(Array.isArray(v) && !v.length))));
  await api("PUT", `/api/sets/${key}`, { spec }).catch(fail);
  delete S.setDraft[key];
  await refresh();
  toast("Saved set " + pretty(key));
}

const PROP_OPTIONS = {
  table: ["chairs", "items", "width", "color"], counter: ["items", "width", "color"], sofa: ["facing", "width", "color"],
  chair: ["facing", "color"], bench: ["facing", "color"], door: ["color"], window: ["view"], plant: ["color"],
  bookshelf: ["width", "color"], fridge: ["color"], lamp: [], rug: ["color", "width"], tree: ["scale"],
  streetlamp: [], house: ["color", "roof"],
};

function setEditor(key) {
  const cat = catalog();
  const saved = S.state.sets[key] || {};
  const spec = S.setDraft[key] || (S.setDraft[key] = JSON.parse(JSON.stringify(saved)));
  spec.props = spec.props || [];
  spec.marks = spec.marks || {};
  const outdoor = spec.kind === "outdoor";
  const setInfo = info().sets[key] || { marks: [], seats: [] };
  if (S.selProp === undefined || S.selProp >= spec.props.length) S.selProp = spec.props.length ? 0 : null;
  if (!S.selCell) S.selCell = "center";
  const saveBtn = h("button", { class: "btn", onclick: () => saveSet(key) }, "Save");
  const rerender = () => { render(); dirty2(); };
  const dirty2 = () => { const b = $("#set-save"); if (b) { b.classList.add("primary"); b.textContent = "Save changes"; } };
  saveBtn.id = "set-save";

  const places = [["back-left", "back", "back-right"], ["left", "center", "right"], ["front-left", "front", "front-right"]];
  const stage = h("div", { class: "stage" + (outdoor ? " outdoor" : "") },
    h("div", { class: "wall" }, outdoor ? "far away" : "back wall"),
    places.flat().map((pl) => h("div", { class: "cell" + (S.selCell === pl ? " on" : ""),
      onclick: (e) => { if (e.target.classList.contains("prop")) return; S.selCell = pl; render(); } },
      h("span", { class: "pl" }, pl),
      spec.props.map((p, i) => (p.place || defaultPlace(p.type)) === pl ? h("span", {
        class: "prop" + (S.selProp === i ? " on" : ""), onclick: () => { S.selProp = i; S.selCell = pl; render(); } },
        pretty(p.name || p.type), p.chairs ? ` + ${p.chairs} chairs` : "") : null))),
    h("div", { class: "cam" }, "🎥 camera side"));

  const addType = select(cat.props, "", (v) => {
    if (!v) return;
    spec.props.push({ type: v, place: S.selCell });
    S.selProp = spec.props.length - 1;
    rerender();
  }, { blank: `+ Add to ${S.selCell}…`, label: "Add furniture" });

  const p = S.selProp !== null ? spec.props[S.selProp] : null;
  const propPanel = p ? h("div", { class: "card", style: "background:var(--panel-2)" },
    h("div", { class: "card-head" }, h("h3", {}, pretty(p.name || p.type)),
      h("button", { class: "btn sm danger ghost", onclick: () => { spec.props.splice(S.selProp, 1); S.selProp = null; rerender(); } }, "Remove")),
    h("div", { class: "fields" },
      h("label", { class: "field" }, "Where", select(cat.places, p.place || defaultPlace(p.type), (v) => { p.place = v; S.selCell = v; rerender(); })),
      (PROP_OPTIONS[p.type] || []).includes("chairs") ? h("label", { class: "field" }, "Chairs", seg([["0", "none"], ["1", "1"], ["2", "2"]], String(p.chairs || 0), (v) => { p.chairs = +v || undefined; rerender(); })) : null,
      (PROP_OPTIONS[p.type] || []).includes("facing") ? h("label", { class: "field" }, "Facing", select(["camera", "left", "right", "back", ...setInfo.marks.filter((m) => !cat.places.includes(m))], p.facing || "camera", (v) => { p.facing = v; dirty2(); })) : null,
      (PROP_OPTIONS[p.type] || []).includes("width") ? h("label", { class: "field" }, "Width (m)", h("input", { type: "number", step: 0.1, min: 0.4, max: 4, value: p.width || "", placeholder: "default", oninput: (e) => { p.width = e.target.value ? +e.target.value : undefined; dirty2(); } })) : null,
      (PROP_OPTIONS[p.type] || []).includes("scale") ? h("label", { class: "field" }, "Size", h("input", { type: "number", step: 0.1, min: 0.5, max: 2.5, value: p.scale || "", placeholder: "1", oninput: (e) => { p.scale = e.target.value ? +e.target.value : undefined; dirty2(); } })) : null,
      h("label", { class: "field" }, "Name (optional)", h("input", { type: "text", value: p.name || "", placeholder: p.type, oninput: (e) => { p.name = slug(e.target.value) || undefined; dirty2(); } }))),
    (PROP_OPTIONS[p.type] || []).includes("items") ? h("div", { class: "field", style: "margin-top:12px" }, h("span", {}, "On top"),
      h("div", { class: "chips" }, cat.table_items.map((it) => {
        const on = (p.items || []).includes(it);
        return h("button", { class: "chip" + (on ? " on" : ""), onclick: () => {
          p.items = on ? p.items.filter((x) => x !== it) : [...(p.items || []), it]; rerender(); } }, pretty(it));
      }))) : null,
    (PROP_OPTIONS[p.type] || []).includes("color") ? h("div", { class: "field", style: "margin-top:12px" }, h("span", {}, "Colour"),
      colorPicker(p.color || "", (v) => { p.color = v; dirty2(); })) : null,
    (PROP_OPTIONS[p.type] || []).includes("view") ? h("div", { class: "field", style: "margin-top:12px" }, h("span", {}, "Outside the window"),
      colorPicker(p.view || "sky", (v) => { p.view = v; dirty2(); })) : null)
    : h("p", { class: "muted small" }, "Pick a place on the floor plan, then add furniture to it.");

  const mapImg = renderOf(`renders/stills/plan_${key}.png`);
  const viewImg = renderOf(`renders/stills/view_${key}.png`);
  const marksBox = h("div", { class: "stack" },
    h("h3", {}, "Spots characters can go to"),
    setInfo.error ? h("div", { class: "banner err" }, setInfo.error) : null,
    h("div", { class: "chips" }, setInfo.marks.map((m) => h("span", { class: "chip static" }, m))),
    setInfo.seats.length ? h("p", { class: "small muted", style: "margin:0" }, "Seats: ", setInfo.seats.join(", ")) : null,
    h("p", { class: "small muted", style: "margin:0" }, "Save to update this list. Add your own spot:"),
    h("div", { class: "row" },
      ...Object.entries(spec.marks).map(([n, pl]) => h("span", { class: "chip static" }, `${n} → ${pl} `,
        h("button", { class: "btn sm ghost", "aria-label": `remove ${n}`, onclick: () => { delete spec.marks[n]; rerender(); } }, "×"))),
      (() => {
        const nm = h("input", { type: "text", placeholder: "spot name", style: "width:130px" });
        const pl = select(cat.places, "center", () => {}, { label: "place" });
        return [nm, pl, h("button", { class: "btn sm", onclick: () => { const n = slug(nm.value); if (!n) return; spec.marks[n] = pl.value; rerender(); } }, "Add spot")];
      })()));

  return h("div", { class: "stack" },
    h("div", { class: "card" },
      h("div", { class: "card-head" }, h("h2", {}, pretty(key)),
        h("div", { class: "row" },
          h("button", { class: "btn danger ghost", onclick: async () => { if (!confirm(`Delete the set ${key}?`)) return; await api("DELETE", `/api/sets/${key}`).catch(fail); delete S.setDraft[key]; S.setSel = null; refresh(); } }, "Delete"),
          h("button", { class: "btn", onclick: async () => { await saveSet(key); job({ kind: "plan", set: key }, () => toast("Map ready")); } }, "🗺️ Map"),
          h("button", { class: "btn", onclick: async () => { await saveSet(key); job({ kind: "view", set: key }, () => toast("Picture ready")); } }, "📷 Picture"),
          saveBtn)),
      h("div", { class: "fields" },
        h("label", { class: "field" }, "Kind", seg([["room", "Room"], ["outdoor", "Outdoors"]], spec.kind || "room", (v) => { spec.kind = v; rerender(); })),
        !outdoor ? h("label", { class: "field" }, "Size", seg(cat.sizes, spec.size || "medium", (v) => { spec.size = v; dirty2(); })) : null,
        !outdoor ? h("label", { class: "field" }, "Floor", select(cat.floors, spec.floor || "wood", (v) => { spec.floor = v; dirty2(); })) : null,
        outdoor ? h("label", { class: "field" }, "Ground", select(cat.floors, spec.ground || "grass", (v) => { spec.ground = v; dirty2(); })) : null,
        outdoor ? h("label", { class: "field" }, "Trees", h("input", { type: "number", min: 0, max: 30, value: spec.trees ?? 6, oninput: (e) => { spec.trees = +e.target.value; dirty2(); } })) : null,
        outdoor ? h("label", { class: "field" }, "Hills", h("input", { type: "number", min: 0, max: 10, value: spec.hills ?? 3, oninput: (e) => { spec.hills = +e.target.value; dirty2(); } })) : null,
        outdoor ? h("label", { class: "field row" }, h("input", { type: "checkbox", checked: spec.path !== false, onchange: (e) => { spec.path = e.target.checked; dirty2(); } }), "Footpath") : null),
      !outdoor ? h("div", { class: "field", style: "margin-top:12px" }, h("span", {}, "Walls"), colorPicker(spec.walls || "cream", (v) => { spec.walls = v; dirty2(); })) : null),
    h("div", { class: "card" },
      h("div", { class: "card-head" }, h("h3", {}, "Floor plan"), addType),
      h("div", { class: "editor-split", style: "grid-template-columns: minmax(0,1fr) minmax(0,1fr)" }, stage, propPanel)),
    h("div", { class: "card" }, marksBox),
    (mapImg || viewImg) ? h("div", { class: "pics" },
      viewImg ? pic(viewImg, "Picture") : null, mapImg ? pic(mapImg, "Map with spot names") : null) : null);
}

function defaultPlace(type) {
  return { door: "back-left", window: "back-right", counter: "back-right", fridge: "back-right", sofa: "back",
    bookshelf: "back", plant: "back-right", lamp: "back-left", tree: "back-left", streetlamp: "back-right",
    house: "back" }[type] || "center";
}

function pic(r, caption) {
  const url = fileUrl(r.path, r.mtime);
  const isVid = r.path.endsWith(".mp4");
  return h("figure", { class: "pic", style: "margin:0" },
    isVid ? h("video", { src: url, controls: true, preload: "metadata" }) : h("img", { src: url, alt: caption, onclick: () => lightbox(url) }),
    h("figcaption", { class: "cap" }, h("span", {}, caption), h("span", {}, new Date(r.mtime * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }))));
}

// ------------------------------------------------------------------ STORY (scenes)
function storyView() {
  const scenes = S.state.scenes;
  const real = scenes.filter((s) => s.exists);
  if (!S.scene || !real.find((s) => s.file === S.scene)) S.scene = real[0] ? real[0].file : null;
  localStorage.setItem("dr.scene", S.scene || "");
  return h("div", {},
    h("div", { class: "page-head" },
      h("div", {}, h("h1", {}, "Story"), h("p", {}, "Your film, scene by scene. Write what happens; dreamreel acts it out and films it.")),
      h("div", { class: "row" },
        h("button", { class: "btn", onclick: () => job({ kind: "previz" }, (j) => j.status === "done" && (toast("Previz ready"), (S.screening = j.outputs.find((o) => o.endsWith(".mp4") && !o.includes("/previz/"))), go("screening"))) }, "▶ Previz the film"),
        h("button", { class: "btn primary", onclick: () => job({ kind: "render" }, (j) => j.status === "done" && (toast("Film rendered"), go("screening"))) }, "🎞️ Render the film"))),
    h("div", { class: "story" },
      h("div", { class: "stack" }, h("div", { class: "scene-list" }, scenes.map((s, i) => sceneItem(s, i, scenes))), newSceneForm()),
      S.scene ? sceneEditor(S.scene) : h("div", { class: "empty" }, "No scenes yet. Make your first one on the left.")));
}

function sceneItem(s, i, scenes) {
  const chk = S.checks[s.file];
  const meta = chk && !chk.error ? `${fmtT(chk.length)} · ${chk.events.filter((e) => e.kind === "say").length} lines` : (s.set ? pretty(s.set) : "");
  const move = async (d) => {
    const film = S.state.project.film;
    const order = scenes.filter((x) => x.in_film).map((x) => x.file.replace(/\.py$/, ""));
    const name = s.file.replace(/\.py$/, "");
    const k = order.indexOf(name);
    if (k < 0 || k + d < 0 || k + d >= order.length) return;
    [order[k], order[k + d]] = [order[k + d], order[k]];
    await api("PUT", "/api/film", { scenes: order }).catch(fail);
    refresh();
  };
  const toggle = async (on) => {
    const order = scenes.filter((x) => x.in_film && (on || x.file !== s.file)).map((x) => x.file.replace(/\.py$/, ""));
    if (on) order.push(s.file.replace(/\.py$/, ""));
    await api("PUT", "/api/film", { scenes: order }).catch(fail);
    refresh();
  };
  if (!s.exists) {
    return h("div", { class: "scene-item out" },
      h("span", { class: "num" }, sceneNum(s.file)),
      h("div", { class: "grow" }, h("div", { class: "t" }, sceneLabel(s.file)), h("div", { class: "meta" }, "file missing")),
      h("button", { class: "btn sm", onclick: () => toggle(false) }, "Remove"));
  }
  return h("div", { class: "scene-item" + (S.scene === s.file ? " on" : "") + (s.in_film ? "" : " out"), tabindex: 0, role: "button",
    onclick: (e) => { if (e.target.closest(".ord, input")) return; S.scene = s.file; render(); } },
    h("span", { class: "num" }, sceneNum(s.file)),
    h("div", { class: "grow" }, h("div", { class: "t" }, sceneLabel(s.file)), h("div", { class: "meta" }, chk && chk.error ? "⚠️ needs a fix" : meta)),
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
      runCheck(r.file);
    } catch (e) { fail(e); }
  };
  return h("details", { class: "card" },
    h("summary", { style: "cursor:pointer;font-weight:700" }, "+ New scene"),
    h("div", { class: "stack", style: "margin-top:10px" },
      h("label", { class: "field" }, "What happens", name),
      h("label", { class: "field" }, "Where", setSel),
      h("div", { class: "field" }, h("span", {}, "Who's in it"),
        h("div", { class: "chips" }, Object.entries(S.state.cast).map(([k, c]) => h("button", { class: "chip",
          onclick: (e) => { cast.has(k) ? cast.delete(k) : cast.add(k); e.target.classList.toggle("on"); } }, c.name || k)))),
      h("button", { class: "btn primary", onclick: create }, "Create scene")));
}

// ---------- scene script parsing (just enough to offer the right choices)
function parseScene(text) {
  const setM = text.match(/dr\.Scene\(\s*["']([^"']+)["']/);
  const castRe = /^([ \t]*)([A-Za-z_][\w \t,]*?)\s*=\s*s\.cast\(([^)]*)\)[ \t]*$/m;
  const m = text.match(castRe);
  let cast = [];
  if (m) {
    const vars = m[2].split(",").map((v) => v.trim()).filter(Boolean);
    const keys = [...m[3].matchAll(/["']([^"']+)["']/g)].map((x) => x[1]);
    cast = keys.map((k, i) => ({ key: k, v: vars[i] || k }));
  }
  return { set: setM ? setM[1] : null, cast, castMatch: m };
}

const ACTIONS = {
  say: { label: "says", fields: ["line", "mood", "to"] },
  walk_to: { label: "walks to", fields: ["where", "speed"] },
  run_to: { label: "runs to", fields: ["where"] },
  enter: { label: "comes in at", fields: ["where"] },
  place: { label: "is standing at", fields: ["where", "facing"] },
  sit: { label: "sits on", fields: ["seat", "already"] },
  stand: { label: "stands up", fields: [] },
  turn_to: { label: "turns to", fields: ["target"] },
  look_at: { label: "looks at", fields: ["target"] },
  feel: { label: "feels", fields: ["mood!"] },
  do: { label: "does", fields: ["gesture", "target?"] },
  leave: { label: "leaves", fields: [] },
};
const SCENE_ACTIONS = {
  wait: { label: "pause", fields: ["seconds"] },
  caption: { label: "caption on screen", fields: ["text"] },
  title_card: { label: "title card before the scene", fields: ["text"] },
  "cut.wide": { label: "camera: wide shot", fields: [] },
  "cut.medium": { label: "camera: medium shot of", fields: ["char"] },
  "cut.close_up": { label: "camera: close-up of", fields: ["char"] },
  "cut.two_shot": { label: "camera: two-shot of", fields: ["char", "char2"] },
  "cut.over_shoulder": { label: "camera: over the shoulder of", fields: ["char", "on"] },
};

function composer(file, ta, onInsert) {
  const cat = catalog();
  const text = ta.value;
  const parsed = parseScene(text);
  const setInfo = (parsed.set && info().sets[parsed.set]) || { marks: [], seats: [] };
  const castKeys = Object.keys(S.state.cast);
  const C = S.composer;
  if (!C.who || (C.who !== "_scene" && !castKeys.includes(C.who))) C.who = parsed.cast[0] ? parsed.cast[0].key : castKeys[0] || "_scene";
  const isScene = C.who === "_scene";
  const acts = isScene ? SCENE_ACTIONS : ACTIONS;
  if (!acts[C.action]) C.action = Object.keys(acts)[0];
  const vals = (C.vals = C.vals || {});
  const others = parsed.cast.filter((c) => c.key !== C.who);
  const nameOf = (k) => (S.state.cast[k] && S.state.cast[k].name) || k;

  const charOpts = (incl) => parsed.cast.filter((c) => incl || c.key !== C.who).map((c) => ["@" + c.key, nameOf(c.key)]);
  const places = new Set(cat.places);
  const marks = [...setInfo.marks.filter((m) => !places.has(m)), ...setInfo.marks.filter((m) => places.has(m))];
  const targetOpts = [...others.map((c) => ["@" + c.key, "👤 " + nameOf(c.key)]), ...marks.map((m) => [m, "📍 " + m])];
  const field = (f) => {
    const opt = f.endsWith("?");
    const name = f.replace(/[?!]$/, "");
    const bind = (v) => (vals[name] = v);
    switch (name) {
      case "line": case "text": {
        const inp = h("input", { type: "text", class: "say-line", placeholder: name === "line" ? "What do they say?" : "Text", value: vals[name] || "",
          oninput: (e) => bind(e.target.value), onkeydown: (e) => e.key === "Enter" && add() });
        return inp;
      }
      case "mood": return select(cat.moods, vals.mood ?? (f.endsWith("!") ? "happy" : ""), bind, f.endsWith("!") ? { label: "mood" } : { blank: "(same mood)", label: "mood" });
      case "to": return select(charOpts(false), vals.to || "", bind, { blank: others.length ? "(to whoever is nearest)" : "(to nobody)", label: "to" });
      case "where": return select(targetOpts, vals.where || (marks[0] || ""), bind, { label: "where" });
      case "target": return select([...targetOpts, ["camera", "🎥 the camera"]], vals.target || (targetOpts[0] || [""])[0], bind, opt ? { blank: "(no one)", label: "target" } : { label: "target" });
      case "facing": return select([...targetOpts, ["camera", "🎥 the camera"]], vals.facing || "", bind, { blank: "(facing anywhere)", label: "facing" });
      case "speed": return select(cat.speeds, vals.speed || "normal", bind, { label: "speed" });
      case "seat": return select(setInfo.seats, vals.seat || setInfo.seats[0], bind, { label: "seat" });
      case "already": return h("label", { class: "row small" }, h("input", { type: "checkbox", checked: vals.already, onchange: (e) => bind(e.target.checked) }), "already sitting when the scene starts");
      case "gesture": return select(cat.gestures, vals.gesture || "wave", bind, { label: "gesture" });
      case "seconds": return h("input", { type: "number", min: 0.2, step: 0.1, value: vals.seconds || 1, style: "width:90px", oninput: (e) => bind(e.target.value) });
      case "char": return select(charOpts(true), vals.char || ("@" + ((parsed.cast[0] || {}).key || "")), bind, { label: "character" });
      case "char2": case "on": return select(charOpts(true), vals[name] || ("@" + ((parsed.cast[1] || parsed.cast[0] || {}).key || "")), bind, { label: "character" });
    }
    return null;
  };

  const add = () => {
    const vOf = (k) => { const c = parsed.cast.find((x) => x.key === k); return c ? c.v : k.replace(/-/g, "_"); };
    const tgt = (t) => (t && t.startsWith("@") ? vOf(t.slice(1)) : q(t));
    const a = C.action;
    const fs = acts[a].fields.map((f) => f.replace(/[?!]$/, ""));
    const get = (k, d) => (vals[k] !== undefined && vals[k] !== "" ? vals[k] : d);
    let line;
    if (isScene) {
      if (a === "wait") line = `s.wait(${+get("seconds", 1) || 1})`;
      else if (a === "caption" || a === "title_card") { if (!get("text")) return toast("Type the text first"); line = `s.${a}(${q(get("text"))})`; }
      else if (a === "cut.wide") line = "s.cut.wide()";
      else if (a === "cut.two_shot") line = `s.cut.two_shot(${tgt(get("char", "@" + (parsed.cast[0] || {}).key))}, ${tgt(get("char2", "@" + (parsed.cast[1] || {}).key))})`;
      else if (a === "cut.over_shoulder") line = `s.cut.over_shoulder(${tgt(get("char", "@" + (parsed.cast[0] || {}).key))}, on=${tgt(get("on", "@" + (parsed.cast[1] || {}).key))})`;
      else line = `s.${a}(${tgt(get("char", "@" + (parsed.cast[0] || {}).key))})`;
    } else {
      const v = vOf(C.who);
      const args = [];
      if (a === "say") {
        if (!get("line")) return toast("Type what they say first");
        args.push(q(get("line")));
        if (get("mood")) args.push(`mood=${q(get("mood"))}`);
        if (get("to")) args.push(`to=${tgt(get("to"))}`);
      } else if (fs.includes("where")) {
        args.push(tgt(get("where", marks[0])));
        if (a === "walk_to" && get("speed", "normal") !== "normal") args.push(`speed=${q(get("speed"))}`);
        if (a === "place" && get("facing")) args.push(`facing=${tgt(get("facing"))}`);
      } else if (a === "sit") {
        if (!setInfo.seats.length) return toast("This set has nothing to sit on. Add a chair, sofa or bench.");
        args.push(q(get("seat", setInfo.seats[0])));
        if (get("already")) args.push("already=True");
      } else if (a === "feel") args.push(q(get("mood", "happy")));
      else if (a === "do") { args.push(q(get("gesture", "wave"))); if (get("target")) args.push(`target=${tgt(get("target"))}`); }
      else if (a === "turn_to" || a === "look_at") args.push(tgt(get("target", (targetOpts[0] || ["camera"])[0])));
      line = `${v}.${a}(${args.join(", ")})`;
    }
    onInsert(line, isScene ? null : C.who);
    if (vals.line) vals.line = "";
    if (vals.text) vals.text = "";
  };

  const whoSel = select([...castKeys.map((k) => [k, "👤 " + nameOf(k)]), ["_scene", "🎬 The scene"]], C.who,
    (v) => { C.who = v; C.action = v === "_scene" ? "wait" : "say"; rebuild(); }, { label: "who" });
  const actSel = select(Object.entries(acts).map(([k, a]) => [k, a.label]), C.action, (v) => { C.action = v; rebuild(); }, { label: "action" });
  const box = h("div", { class: "composer" });
  const rebuild = () => box.replaceWith(composer(file, ta, onInsert));
  box.append(...[
    h("div", { class: "row" },
      h("strong", { class: "small" }, "Add a line:"), whoSel, actSel,
      ...acts[C.action].fields.map(field),
      h("button", { class: "btn primary sm", onclick: add }, "Add ⏎")),
    !isScene && parsed.cast.length && !parsed.cast.find((c) => c.key === C.who)
      ? h("div", { class: "small muted", style: "margin-top:6px" }, `${nameOf(C.who)} isn't in this scene yet; adding a line brings them in.`) : null].filter(Boolean));
  return box;
}

function sceneEditor(file) {
  const meta = S.state.scenes.find((s) => s.file === file);
  const wrap = h("div", { class: "stack" });
  const ta = h("textarea", { class: "code", spellcheck: "false", "aria-label": "Scene script" });
  const gutter = h("div", { class: "gutter", "aria-hidden": "true" });
  const saveBtn = h("button", { class: "btn" }, "Save");
  const status = h("span", { class: "small muted" });
  const chk = S.checks[file];

  const drawGutter = () => {
    const n = ta.value.split("\n").length;
    codeWrap.style.setProperty("--code-h", `${Math.max(240, Math.min(560, n * 20.8 + 60))}px`);
    const errLine = chk && chk.line;
    gutter.innerHTML = Array.from({ length: n }, (_, i) => (i + 1 === errLine ? `<span class="err">${i + 1}</span>` : i + 1)).join("\n");
    gutter.scrollTop = ta.scrollTop;
  };
  const isDirty = () => ta.value !== S.sceneText[file];
  const markDirty = () => {
    S.draft[file] = ta.value;
    saveBtn.classList.toggle("primary", isDirty());
    status.replaceChildren(isDirty() ? h("span", {}, h("span", { class: "dirty-dot" }), " not saved") : "");
  };
  ta.addEventListener("input", () => { drawGutter(); markDirty(); });
  ta.addEventListener("scroll", () => { gutter.scrollTop = ta.scrollTop; S.view_ed = { file, scroll: ta.scrollTop }; });
  ta.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); save(true); }
    if (e.key === "Tab") { e.preventDefault(); insertText(ta, "    "); }
  });
  const save = async (check) => {
    try {
      await api("PUT", `/api/scenes/${file}`, { text: ta.value });
      S.sceneText[file] = ta.value;
      delete S.draft[file];
      markDirty();
      if (check) runCheck(file);
    } catch (e) { fail(e); }
  };
  saveBtn.addEventListener("click", () => save(true));

  const load = async () => {
    if (S.draft[file] !== undefined) { ta.value = S.draft[file]; }
    else {
      const r = await api("GET", `/api/scenes/${file}`);
      S.sceneText[file] = r.text;
      ta.value = r.text;
    }
    drawGutter(); markDirty();
    if (S.view_ed && S.view_ed.file === file) { ta.scrollTop = S.view_ed.scroll; gutter.scrollTop = ta.scrollTop; }
    if (S.lastCaret && S.lastCaret.file === file) ta.setSelectionRange(S.lastCaret.pos, S.lastCaret.pos);
    composerSlot.replaceChildren(composer(file, ta, insertLine));
    if (!S.checks[file]) runCheck(file);
  };

  const insertLine = (line, whoKey) => {
    // bring the character into the scene if needed
    if (whoKey) ensureCast(ta, whoKey);
    const val = ta.value;
    let pos = ta.selectionEnd;
    if (document.activeElement !== ta && S.lastCaret && S.lastCaret.file === file) pos = S.lastCaret.pos;
    if (pos === undefined || pos === null || pos > val.length || (!S.lastCaret && document.activeElement !== ta)) pos = val.length;
    // insert after the line the caret is on, keeping its indentation
    let end = val.indexOf("\n", pos);
    if (end < 0) end = val.length;
    const start = val.lastIndexOf("\n", end - 1) + 1;
    const cur = val.slice(start, end);
    let indent = (cur.match(/^\s*/) || [""])[0];
    if (/:\s*$/.test(cur)) indent += "    ";
    let insert = (cur.trim() === "" && end === val.length ? "" : "\n") + indent + line;
    if (end === val.length && !val.endsWith("\n") && cur.trim() === "") insert = indent + line;
    ta.focus();
    ta.setSelectionRange(end, end);
    insertText(ta, insert);
    S.lastCaret = { file, pos: ta.selectionEnd };
    drawGutter(); markDirty();
    save(true);
  };
  ta.addEventListener("blur", () => (S.lastCaret = { file, pos: ta.selectionEnd }));

  const together = () => {
    let { selectionStart: a, selectionEnd: b, value: v } = ta;
    a = v.lastIndexOf("\n", a - 1) + 1;
    let e = v.indexOf("\n", b - (b > a && v[b - 1] === "\n" ? 1 : 0));
    if (e < 0) e = v.length;
    const block = v.slice(a, e);
    if (!block.trim()) return toast("Select the lines that should happen at the same time");
    const ind = (block.match(/^\s*/) || [""])[0];
    const out = `${ind}with s.together():\n` + block.split("\n").map((l) => (l.trim() ? "    " + l : l)).join("\n");
    ta.focus(); ta.setSelectionRange(a, e); insertText(ta, out);
    drawGutter(); markDirty();
  };

  const composerSlot = h("div", {});
  const codeWrap = h("div", { class: "code-wrap" }, gutter, ta);
  const tl = chk && !chk.error ? timeline(file, chk) : null;
  const errBanner = chk && chk.error ? h("div", { class: "banner err", role: "alert" },
    h("div", {}, h("strong", {}, chk.line ? `Line ${chk.line}: ` : ""), chk.error.replace(/^[A-Za-z]+Error: /, ""),
      chk.line ? h("div", {}, h("button", { class: "btn sm", style: "margin-top:6px", onclick: () => goToLine(ta, chk.line) }, "Show me")) : null)) : null;
  const warns = chk && chk.warnings && chk.warnings.length ? h("div", { class: "banner warn" }, "⚠️ ", chk.warnings.join("; ")) : null;
  const t = S.playhead[file] ?? null;
  const stem = file.replace(/\.py$/, "");
  const contact = renderOf(`renders/stills/${stem}_contact.png`);
  const stills = rendersFor(`renders/stills/${stem}_`).filter((r) => !r.path.endsWith("_contact.png")).slice(0, 3);
  const previz = renderOf(`renders/previz/${stem}.mp4`);
  const final = renderOf(`renders/final/${stem}.mp4`);

  wrap.append(...[
    h("div", { class: "card" },
      h("div", { class: "card-head" },
        h("div", {}, h("h2", {}, `${sceneNum(file)} · ${sceneLabel(file)}`),
          h("div", { class: "small muted" }, meta && meta.set ? `Set: ${pretty(meta.set)}` : "", chk && !chk.error ? ` · ${fmtT(chk.length)} · ${chk.cast.join(", ")}` : "")),
        h("div", { class: "row" }, status,
          h("button", { class: "btn ghost danger sm", onclick: async () => { if (!confirm(`Delete scene ${file}?`)) return; await api("DELETE", `/api/scenes/${file}`).catch(fail); S.scene = null; refresh(); } }, "Delete"),
          h("button", { class: "btn sm", title: "Select some lines first", onclick: together }, "⇉ At the same time"),
          h("button", { class: "btn sm", onclick: () => { insertLine("s.wait(1)"); } }, "⏸ Pause"),
          saveBtn)),
      composerSlot,
      h("div", { style: "height:10px" }),
      codeWrap,
      h("p", { class: "small muted", style: "margin:8px 0 0" }, "Each line happens after the one before. ",
        h("kbd", {}, "Ctrl"), "+", h("kbd", {}, "S"), " saves and checks. Lines are added after the cursor.")),
    errBanner, warns,
    h("div", { class: "card" },
      h("div", { class: "card-head" }, h("h3", {}, "Timeline"),
        h("div", { class: "row" },
          h("button", { class: "btn sm", onclick: () => save(true) }, "↻ Check"),
          h("button", { class: "btn sm", disabled: t === null ? true : null, onclick: () => job({ kind: "still", scene: file, times: [t] }, () => toast("Frame ready")) },
            t === null ? "📷 Click the timeline to pick a moment" : `📷 Frame at ${fmtT(t)}`),
          h("button", { class: "btn sm", onclick: () => job({ kind: "contact", scene: file, count: 6 }, () => toast("Contact sheet ready")) }, "🖼️ Contact sheet"),
          h("button", { class: "btn sm", onclick: () => job({ kind: "previz", scene: file }, () => toast("Previz ready")) }, "▶ Previz scene"),
          h("button", { class: "btn sm primary", onclick: () => job({ kind: "render", scene: file }, () => toast("Scene rendered")) }, "🎞️ Render scene"))),
      tl || h("div", { class: "empty" }, chk ? "Fix the problem above to see the timeline." : "Checking…")),
    (contact || stills.length || previz || final) ? h("div", { class: "card" }, h("h3", { style: "margin-bottom:10px" }, "Pictures and videos"),
      h("div", { class: "pics" },
        final ? pic(final, "Final render") : null, previz ? pic(previz, "Previz") : null,
        contact ? pic(contact, "Contact sheet") : null, stills.map((r) => pic(r, "Frame at " + r.path.match(/_([\d.]+)s\.png$/)[1].replace(/^0+(?=\d)/, "") + " s")))) : null].filter(Boolean));
  load().catch(fail);
  return wrap;
}

function insertText(ta, text) {
  ta.focus();
  if (!document.execCommand || !document.execCommand("insertText", false, text)) {
    ta.setRangeText(text, ta.selectionStart, ta.selectionEnd, "end");
  }
  ta.dispatchEvent(new Event("input"));
}

function goToLine(ta, n) {
  const lines = ta.value.split("\n");
  const a = lines.slice(0, n - 1).join("\n").length + (n > 1 ? 1 : 0);
  ta.focus();
  ta.setSelectionRange(a, a + (lines[n - 1] || "").length);
  ta.scrollTop = Math.max(0, (n - 5) * 20.8);
}

function ensureCast(ta, key) {
  const text = ta.value;
  const p = parseScene(text);
  if (p.cast.find((c) => c.key === key)) return;
  const v = key.replace(/-/g, "_");
  const cast = [...p.cast, { key, v }];
  const line = `${cast.map((c) => c.v).join(", ")} = s.cast(${cast.map((c) => q(c.key)).join(", ")})`;
  if (p.castMatch) {
    const a = p.castMatch.index;
    ta.setSelectionRange(a, a + p.castMatch[0].length);
    insertText(ta, p.castMatch[1] + line);
  } else {
    const m = text.match(/^.*dr\.Scene\(.*\).*$/m);
    const at = m ? m.index + m[0].length : text.length;
    ta.setSelectionRange(at, at);
    insertText(ta, "\n" + line);
  }
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
      const text = e.kind === "say" ? `“${e.line}”` : e.kind === "gesture" ? e.gesture : "walks";
      return h("div", { class: `tl-b ${e.kind}`, style: `left:${pct(e.t)};width:${pct(w)}`, title: `${fmtT(e.t)} ${who}: ${text}` }, text);
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
        h("label", { class: "field" }, "Frames per second", select([["24", "24 (film)"], ["25", "25"], ["30", "30"]], String(film.fps || 24), (v) => (film.fps = +v)))),
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
  if (Object.keys(S.draft).some((f) => S.draft[f] !== S.sceneText[f])) { e.preventDefault(); e.returnValue = ""; }
});
refresh().then(pollJobs).catch(fail);
