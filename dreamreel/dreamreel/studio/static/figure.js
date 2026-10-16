// A front-view drawing of a dreamreel character, from its cast spec. It follows the same proportions as
// dreamreel/character.py, so people can design a character instantly and render it only to check.
(function () {
  let uid = 0;

  function color(c, palette, fallback) {
    if (!c) return fallback;
    if (typeof c === "string" && c.startsWith("#")) return c;
    return (palette && palette[c]) || fallback;
  }

  function figureSVG(spec, palette) {
    spec = spec || {};
    const id = "f" + (++uid);
    const body = spec.body || "bean";
    const H = (spec.height || 1) * (body === "kid" ? 0.75 : 1);
    const C = (k, d) => color(spec[k], palette, d);
    const skin = C("skin", "#eec1a0"), hairC = C("hair_color", "#5a3825"), top = C("top", "#3d7dd8"),
      bottom = C("bottom", "#26375f"), shoes = C("shoes", "#3a3a40");
    const hairStyle = spec.hair || "short";
    const extras = spec.extras || [];
    const es = { small: 0.8, normal: 1, big: 1.3 }[spec.eyes || "normal"] || 1;

    // metres, z up; the drawing flips y
    const hip = 0.29 * H;
    const r = ({ round: 0.19, tall: 0.15 }[body] || 0.165) * H;
    const len = ({ round: 0.08, tall: 0.2 }[body] || 0.12) * H;
    const cz = hip - 0.06 * H + r + len / 2;
    const neck = cz + len / 2 + r * 0.82;
    const hr = (body === "kid" ? 0.21 : body === "tall" ? 0.17 : 0.19) * H;
    const hc = neck + hr * 0.62;
    const shoulder = cz + len / 2 + r * 0.25;
    const split = hip + 0.03 * H;

    const U = 100;               // px per metre
    const X = (x) => 75 + x * U;
    const Y = (z) => 196 - z * U;
    const S = (v) => v * U;
    const parts = [];
    const add = (s) => parts.push(s);
    const ell = (x, z, rx, rz, fill, extra = "") =>
      add(`<ellipse cx="${X(x)}" cy="${Y(z)}" rx="${S(rx)}" ry="${S(rz)}" fill="${fill}" ${extra}/>`);
    const rrect = (x0, z0, x1, z1, rad, fill, extra = "") =>
      add(`<rect x="${X(Math.min(x0, x1))}" y="${Y(Math.max(z0, z1))}" width="${S(Math.abs(x1 - x0))}" height="${S(Math.abs(z1 - z0))}" rx="${S(rad)}" fill="${fill}" ${extra}/>`);

    // ground shadow
    ell(0, 0.005, 0.24 * H, 0.03 * H, "rgba(60,40,20,.15)");

    // hair behind the head
    if (hairStyle === "long") ell(0, hc - hr * 0.55, hr * 0.98, hr * 1.2, hairC);
    if (hairStyle === "bun") ell(0, hc + hr * 1.0, hr * 0.42, hr * 0.42, hairC);
    if (hairStyle === "ponytail") ell(hr * 0.9, hc - hr * 0.2, hr * 0.28, hr * 0.7, hairC, `transform="rotate(-12 ${X(hr * 0.9)} ${Y(hc)})"`);

    // legs and shoes
    for (const s of [1, -1]) {
      rrect(s * 0.075 * H - 0.055 * H, 0.05 * H, s * 0.075 * H + 0.055 * H, hip, 0.055 * H, bottom);
      rrect(s * 0.075 * H - 0.0625 * H, 0, s * 0.075 * H + 0.0625 * H, 0.07 * H, 0.03 * H, shoes);
    }

    // arms (behind the body)
    for (const s of [1, -1]) {
      const x = s * r * 0.86;
      const ax = x + s * 0.03 * H;
      add(`<line x1="${X(x)}" y1="${Y(shoulder)}" x2="${X(ax)}" y2="${Y(shoulder - 0.22 * H)}" stroke="${top}" stroke-width="${S(0.094 * H)}" stroke-linecap="round"/>`);
      ell(ax + s * 0.005 * H, shoulder - 0.27 * H, 0.058 * H, 0.058 * H, skin);
    }

    // body: a capsule, top colour above the waist, trousers below (or a skirt)
    const bodyPath = `M ${X(-r)} ${Y(cz + len / 2)} A ${S(r)} ${S(r)} 0 0 1 ${X(r)} ${Y(cz + len / 2)} L ${X(r)} ${Y(cz - len / 2)} A ${S(r)} ${S(r)} 0 0 1 ${X(-r)} ${Y(cz - len / 2)} Z`;
    add(`<clipPath id="${id}t"><rect x="0" y="0" width="200" height="${Y(split)}"/></clipPath>`);
    if (spec.outfit === "dress") {
      const z0 = hip - 0.14 * H, z1 = z0 + 0.2 * H;
      add(`<path d="M ${X(-r * 1.02)} ${Y(z0)} L ${X(r * 1.02)} ${Y(z0)} L ${X(r * 0.8)} ${Y(z1)} L ${X(-r * 0.8)} ${Y(z1)} Z" fill="${top}"/>`);
      add(`<path d="${bodyPath}" fill="${top}" clip-path="url(#${id}t)"/>`);
    } else {
      add(`<path d="${bodyPath}" fill="${bottom}"/>`);
      add(`<path d="${bodyPath}" fill="${top}" clip-path="url(#${id}t)"/>`);
    }
    if (extras.includes("scarf")) rrect(-r * 0.75, neck - 0.065 * H, r * 0.75, neck + 0.0, 0.04 * H, color("red", palette, "#e4572e"));
    if (extras.includes("tie")) add(`<path d="M ${X(-0.018 * H)} ${Y(neck - 0.03 * H)} L ${X(0.018 * H)} ${Y(neck - 0.03 * H)} L ${X(0.025 * H)} ${Y(neck - 0.2 * H)} L 75 ${Y(neck - 0.23 * H)} L ${X(-0.025 * H)} ${Y(neck - 0.2 * H)} Z" fill="${color("red", palette, "#e4572e")}"/>`);

    // head
    ell(0, hc, hr, hr, skin);

    // hair on top
    if (hairStyle !== "none") {
      const cut = hairStyle === "short" || hairStyle === "spiky" || hairStyle === "mohawk" ? hc + hr * 0.42 : hc + hr * 0.32;
      add(`<clipPath id="${id}h"><rect x="0" y="0" width="200" height="${Y(cut)}"/></clipPath>`);
      if (hairStyle === "mohawk") ell(0, hc + 0.03 * H, hr * 0.37, hr * 1.06, hairC, `clip-path="url(#${id}h)"`);
      else ell(0, hc, hr * 1.06, hr * 1.06, hairC, `clip-path="url(#${id}h)"`);
      if (hairStyle === "bob") for (const s of [1, -1]) ell(s * hr * 0.78, hc - hr * 0.2, hr * 0.36, hr * 0.62, hairC);
      if (hairStyle === "long") for (const s of [1, -1]) ell(s * hr * 0.86, hc - hr * 0.3, hr * 0.26, hr * 0.8, hairC);
      if (hairStyle === "spiky") for (let i = 0; i < 7; i++) {
        const a = (-60 + i * 20) * Math.PI / 180, x = Math.sin(a) * hr * 0.62, z = hc + Math.cos(a) * hr * 0.92;
        add(`<path d="M ${X(x - hr * 0.16)} ${Y(z - hr * 0.05)} L ${X(x + Math.sin(a) * hr * 0.2)} ${Y(z + hr * 0.38)} L ${X(x + hr * 0.16)} ${Y(z - hr * 0.05)} Z" fill="${hairC}"/>`);
      }
      if (hairStyle === "curly") for (let i = 0; i < 9; i++) {
        const a = (-80 + i * 20) * Math.PI / 180;
        ell(Math.sin(a) * hr * 0.92, hc + Math.cos(a) * hr * 0.88, hr * 0.3, hr * 0.3, hairC);
      }
    }

    // face
    const fz = (dz) => hc + dz * H;
    for (const s of [1, -1]) {
      ell(s * 0.075 * H, fz(0.02), 0.03 * H * es, 0.043 * H * es, "#161414");
      ell(s * 0.075 * H + 0.01 * H * es, fz(0.02) + 0.016 * H * es, 0.011 * H * es, 0.011 * H * es, "#fff");
      rrect(s * 0.075 * H - 0.027 * H, fz(0.085) - 0.011 * H, s * 0.075 * H + 0.027 * H, fz(0.085) + 0.011 * H,
        0.011 * H, hairStyle !== "none" ? hairC : "#3a3a40");
      if (spec.blush !== false) ell(s * 0.115 * H, fz(-0.035), 0.032 * H, 0.019 * H, "#f19aa6", `opacity=".9"`);
    }
    if (spec.nose !== false) ell(0, fz(-0.015), 0.022 * H, 0.022 * H, skin, `stroke="rgba(0,0,0,.08)" stroke-width="1"`);
    add(`<path d="M ${X(-0.04 * H)} ${Y(fz(-0.062))} Q 75 ${Y(fz(-0.1))} ${X(0.04 * H)} ${Y(fz(-0.062))}" stroke="#5b1e2c" stroke-width="${S(0.016 * H)}" fill="none" stroke-linecap="round"/>`);
    if (extras.includes("moustache")) for (const s of [1, -1]) ell(s * 0.032 * H, fz(-0.045), 0.038 * H, 0.014 * H, hairC);
    if (extras.includes("beard")) {
      add(`<clipPath id="${id}b"><rect x="0" y="${Y(fz(-0.07))}" width="200" height="200"/></clipPath>`);
      ell(0, hc - hr * 0.45, hr * 0.78, hr * 0.62, hairC, `clip-path="url(#${id}b)"`);
    }
    if (extras.includes("glasses")) {
      for (const s of [1, -1]) add(`<circle cx="${X(s * 0.075 * H)}" cy="${Y(fz(0.02))}" r="${S(0.047 * H)}" fill="rgba(255,255,255,.15)" stroke="#222" stroke-width="${S(0.012 * H)}"/>`);
      add(`<line x1="${X(-0.028 * H)}" y1="${Y(fz(0.03))}" x2="${X(0.028 * H)}" y2="${Y(fz(0.03))}" stroke="#222" stroke-width="${S(0.01 * H)}"/>`);
    }
    if (extras.includes("hat")) {
      rrect(-hr * 1.45, hc + hr * 0.62, hr * 1.45, hc + hr * 0.62 + 0.02 * H, 0.01 * H, "#3a3a40");
      add(`<path d="M ${X(-hr * 0.92)} ${Y(hc + hr * 0.62)} L ${X(hr * 0.92)} ${Y(hc + hr * 0.62)} L ${X(hr * 0.88)} ${Y(hc + hr * 1.37)} L ${X(-hr * 0.88)} ${Y(hc + hr * 1.37)} Z" fill="#3a3a40"/>`);
    }
    if (extras.includes("cap")) {
      add(`<clipPath id="${id}c"><rect x="0" y="0" width="200" height="${Y(hc + hr * 0.3)}"/></clipPath>`);
      ell(0, hc, hr * 1.08, hr * 1.08, color("red", palette, "#e4572e"), `clip-path="url(#${id}c)"`);
      rrect(-hr * 0.6, hc + hr * 0.3, hr * 0.6, hc + hr * 0.38, 0.01 * H, color("red", palette, "#e4572e"));
    }
    if (extras.includes("bow")) for (const s of [1, -1]) ell(s * hr * 0.3, hc + hr * 0.98, hr * 0.28, hr * 0.2, color("pink", palette, "#ef7aa1"));
    if (extras.includes("headphones")) {
      add(`<path d="M ${X(-hr * 1.05)} ${Y(hc)} A ${S(hr * 1.08)} ${S(hr * 1.08)} 0 0 1 ${X(hr * 1.05)} ${Y(hc)}" stroke="#3a3a40" stroke-width="${S(0.028 * H)}" fill="none"/>`);
      for (const s of [1, -1]) rrect(s * hr * 1.02 - 0.03 * H, hc - 0.05 * H, s * hr * 1.02 + 0.03 * H, hc + 0.05 * H, 0.02 * H, "#3a3a40");
    }
    const vtop = Math.max(0, Y(hc + hr * (extras.includes("hat") || hairStyle === "bun" || hairStyle === "spiky" ? 1.55 : 1.15)) - 6);
    const vh = 205 - vtop, vw = Math.max(vh * 0.62, 2 * S(r) + 40);
    return `<svg viewBox="${75 - vw / 2} ${vtop} ${vw} ${vh}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${(spec.name || "character").replace(/"/g, "")}">${parts.join("")}</svg>`;
  }

  window.figureSVG = figureSVG;
})();
