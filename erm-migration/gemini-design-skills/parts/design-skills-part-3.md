# Design Skills for Gemini, part 3 of 6: Scroll and page transitions

This file is a library of **22 design and animation skills** (3D/WebGL, animation, scroll, 2D, design
systems and authoring tools). Each skill has a SKILL.md (when to use it, core patterns, pitfalls),
references (API notes, guides), agents (expert roles), commands (task recipes), scripts and asset templates.

**How to use this file**
1. Find the skill that matches the task in the index below (match on technology or on what the user wants to build).
2. Read that skill's `SKILL.md` first and follow its patterns, then its `references/` for API details.
3. A file under `commands/` is a ready-made recipe: when the user asks for that task (or types `/command-name`),
   follow its steps. A file under `agents/` describes an expert role you can adopt.
4. Several skills can combine (e.g. Three.js + GSAP scroll); `web3d-integration-patterns` covers how.
5. Write complete, runnable code. Prefer the versions and APIs shown in the skill; say so when you go beyond them.

Every file starts with a line `===== FILE: <path> =====`.

## Skills in this part

| Skill | Use it for |
|---|---|
| `locomotive-scroll` | Comprehensive skill for Locomotive Scroll smooth scrolling library with parallax effects, viewport detection, and scroll-driven animations. Use this skill when implementing smooth scrolling experiences, creating parallax effects, building scroll-triggered animations, or developing immersive scrolling websites. Triggers on tasks involving Locomotive Scroll, smooth scrolling, parallax, scroll detection, scroll events, sticky elements, horizontal scrolling, or GSAP ScrollTrigger integration. Integrates with GSAP for advanced scroll-driven animations. |
| `barba-js` | Page transitions library for creating fluid, smooth transitions between website pages. Use this skill when implementing page transitions, creating SPA-like experiences, adding animated route changes, or building websites with smooth navigation. Triggers on tasks involving Barba.js, page transitions, routing, view management, transition hooks, GSAP integration, or smooth page navigation. Works with gsap-scrolltrigger for transition animations. |
| `scroll-reveal-libraries` | Simple scroll-triggered reveal animations using AOS (Animate On Scroll). Use this skill when building marketing pages, landing pages, or content-heavy sites requiring basic fade/slide effects without complex animation orchestration. Triggers on tasks involving scroll animations, scroll-triggered reveals, AOS, simple animations, or basic scroll effects. Alternative to GSAP ScrollTrigger and Locomotive Scroll for simpler use cases. Compare with motion-framer for React-specific animations. |
| `lightweight-3d-effects` | Lightweight 3D effects for decorative elements and micro-interactions using Zdog, Vanta.js, and Vanilla-Tilt.js. Use this skill when adding pseudo-3D illustrations, animated backgrounds, parallax tilt effects, decorative 3D elements, or subtle depth effects without heavy frameworks. Triggers on tasks involving Zdog pseudo-3D, Vanta.js backgrounds, Vanilla-Tilt parallax, card tilt effects, hero section animations, or lightweight landing page visuals. Ideal for performance-focused designs. |


# Skill: locomotive-scroll


===== FILE: plugins/individual/locomotive-scroll/skills/locomotive-scroll/SKILL.md =====

---
name: locomotive-scroll
description: Comprehensive skill for Locomotive Scroll smooth scrolling library with parallax effects, viewport detection, and scroll-driven animations. Use this skill when implementing smooth scrolling experiences, creating parallax effects, building scroll-triggered animations, or developing immersive scrolling websites. Triggers on tasks involving Locomotive Scroll, smooth scrolling, parallax, scroll detection, scroll events, sticky elements, horizontal scrolling, or GSAP ScrollTrigger integration. Integrates with GSAP for advanced scroll-driven animations.
---

# Locomotive Scroll

Comprehensive guide for implementing smooth scrolling, parallax effects, and scroll-driven animations using Locomotive Scroll.

## Overview

Locomotive Scroll is a JavaScript library that provides:
- **Smooth scrolling**: Hardware-accelerated smooth scroll with customizable easing
- **Parallax effects**: Element-level speed control for depth
- **Viewport detection**: Track when elements enter/exit viewport
- **Scroll events**: Monitor scroll progress for animation synchronization
- **Sticky elements**: Pin elements within defined boundaries
- **Horizontal scrolling**: Support for horizontal scroll layouts

**When to use Locomotive Scroll:**
- Building immersive landing pages with parallax
- Creating smooth, Apple-style scroll experiences
- Implementing scroll-triggered animations
- Developing narrative/storytelling websites
- Adding depth and motion to long-form content

**Trade-offs:**
- Scroll-hijacking can impact accessibility (provide disable option)
- Performance overhead on low-end devices (detect and disable)
- Mobile touch scrolling feels different (test extensively)
- Fixed positioning requires workarounds

## Installation

```bash
npm install locomotive-scroll
```

```javascript
// ES6
import LocomotiveScroll from 'locomotive-scroll';
import 'locomotive-scroll/dist/locomotive-scroll.css';

// Or via CDN
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/locomotive-scroll/dist/locomotive-scroll.min.css">
<script src="https://cdn.jsdelivr.net/npm/locomotive-scroll/dist/locomotive-scroll.min.js"></script>
```

## Core Concepts

### 1. HTML Structure

Every Locomotive Scroll implementation requires specific data attributes:

```html
<!-- Scroll container (required) -->
<div data-scroll-container>

  <!-- Scroll sections (optional, improves performance) -->
  <div data-scroll-section>

    <!-- Tracked elements -->
    <h1 data-scroll>Basic detection</h1>

    <!-- Parallax element -->
    <div data-scroll data-scroll-speed="2">
      Moves faster than scroll
    </div>

    <!-- Sticky element -->
    <div data-scroll data-scroll-sticky>
      Sticks within section
    </div>

    <!-- Element with ID for tracking -->
    <div data-scroll data-scroll-id="hero">
      Accessible via JavaScript
    </div>

    <!-- Call event trigger -->
    <div data-scroll data-scroll-call="fadeIn">
      Triggers custom event
    </div>

  </div>
</div>
```

### 2. Initialization

```javascript
const scroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,
  lerp: 0.1,        // Smoothness (0-1, lower = smoother)
  multiplier: 1,    // Speed multiplier
  class: 'is-inview', // Class added to visible elements
  repeat: false,    // Repeat in-view detection
  offset: [0, 0]    // Global trigger offset [bottom, top]
});
```

### 3. Data Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-scroll` | Enable detection | `data-scroll` |
| `data-scroll-speed` | Parallax speed | `data-scroll-speed="2"` |
| `data-scroll-direction` | Parallax axis | `data-scroll-direction="horizontal"` |
| `data-scroll-sticky` | Sticky positioning | `data-scroll-sticky` |
| `data-scroll-target` | Sticky boundary | `data-scroll-target="#section"` |
| `data-scroll-offset` | Trigger offset | `data-scroll-offset="20%"` |
| `data-scroll-repeat` | Repeat detection | `data-scroll-repeat` |
| `data-scroll-call` | Event trigger | `data-scroll-call="myFunction"` |
| `data-scroll-id` | Unique identifier | `data-scroll-id="hero"` |
| `data-scroll-class` | Custom class | `data-scroll-class="is-visible"` |

## Common Patterns

### 1. Basic Smooth Scrolling

```javascript
import LocomotiveScroll from 'locomotive-scroll';

const scroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true
});
```

```html
<div data-scroll-container>
  <div data-scroll-section>
    <h1>Smooth scrolling enabled</h1>
  </div>
</div>
```

### 2. Parallax Effects

```html
<!-- Slow parallax -->
<div data-scroll data-scroll-speed="0.5">
  Moves slower than scroll (background effect)
</div>

<!-- Fast parallax -->
<div data-scroll data-scroll-speed="3">
  Moves faster than scroll (foreground effect)
</div>

<!-- Reverse parallax -->
<div data-scroll data-scroll-speed="-2">
  Moves in opposite direction
</div>

<!-- Horizontal parallax -->
<div data-scroll data-scroll-speed="2" data-scroll-direction="horizontal">
  Moves horizontally
</div>
```

### 3. Viewport Detection and Callbacks

```javascript
// Track scroll progress
scroll.on('scroll', (args) => {
  console.log(args.scroll.y); // Current scroll position
  console.log(args.speed);    // Scroll speed
  console.log(args.direction); // Scroll direction

  // Access specific element progress
  if (args.currentElements['hero']) {
    const progress = args.currentElements['hero'].progress;
    console.log(`Hero progress: ${progress}`); // 0 to 1
  }
});

// Call events
scroll.on('call', (value, way, obj) => {
  console.log(`Event triggered: ${value}`);
  // value = data-scroll-call attribute value
  // way = 'enter' or 'exit'
  // obj = {id, el}
});
```

```html
<div data-scroll data-scroll-id="hero">Hero section</div>
<div data-scroll data-scroll-call="playVideo">Video section</div>
```

### 4. Sticky Elements

```html
<!-- Stick within parent section -->
<div data-scroll-section>
  <div data-scroll data-scroll-sticky>
    I stick while section is in view
  </div>
</div>

<!-- Stick with specific target -->
<div id="sticky-container">
  <div data-scroll data-scroll-sticky data-scroll-target="#sticky-container">
    I stick within #sticky-container
  </div>
</div>
```

### 5. Programmatic Scrolling

```javascript
// Scroll to element
scroll.scrollTo('#target-section');

// Scroll to top
scroll.scrollTo('top');

// Scroll to bottom
scroll.scrollTo('bottom');

// Scroll with options
scroll.scrollTo('#target', {
  offset: -100,      // Offset in pixels
  duration: 1000,    // Duration in ms
  easing: [0.25, 0.0, 0.35, 1.0], // Cubic bezier
  disableLerp: true, // Disable smooth lerp
  callback: () => console.log('Scrolled!')
});

// Scroll to pixel value
scroll.scrollTo(500);
```

### 6. Horizontal Scrolling

```javascript
const scroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,
  direction: 'horizontal'
});
```

```html
<div data-scroll-container>
  <div data-scroll-section style="display: flex; width: 300vw;">
    <div>Section 1</div>
    <div>Section 2</div>
    <div>Section 3</div>
  </div>
</div>
```

### 7. Mobile Responsiveness

```javascript
const scroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,

  // Tablet settings
  tablet: {
    smooth: true,
    breakpoint: 1024
  },

  // Smartphone settings
  smartphone: {
    smooth: false, // Disable on mobile for performance
    breakpoint: 768
  }
});
```

## Integration with GSAP ScrollTrigger

Locomotive Scroll and GSAP ScrollTrigger work together for advanced animations:

```javascript
import LocomotiveScroll from 'locomotive-scroll';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const locoScroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true
});

// Sync Locomotive Scroll with ScrollTrigger
locoScroll.on('scroll', ScrollTrigger.update);

ScrollTrigger.scrollerProxy('[data-scroll-container]', {
  scrollTop(value) {
    return arguments.length
      ? locoScroll.scrollTo(value, 0, 0)
      : locoScroll.scroll.instance.scroll.y;
  },
  getBoundingClientRect() {
    return {
      top: 0,
      left: 0,
      width: window.innerWidth,
      height: window.innerHeight
    };
  },
  pinType: document.querySelector('[data-scroll-container]').style.transform
    ? 'transform'
    : 'fixed'
});

// GSAP animation with ScrollTrigger
gsap.to('.fade-in', {
  scrollTrigger: {
    trigger: '.fade-in',
    scroller: '[data-scroll-container]',
    start: 'top bottom',
    end: 'top center',
    scrub: true
  },
  opacity: 1,
  y: 0
});

// Update ScrollTrigger when Locomotive updates
ScrollTrigger.addEventListener('refresh', () => locoScroll.update());
ScrollTrigger.refresh();
```

## Instance Methods

```javascript
const scroll = new LocomotiveScroll();

// Lifecycle
scroll.init();     // Reinitialize
scroll.update();   // Refresh element positions
scroll.destroy();  // Clean up
scroll.start();    // Resume scrolling
scroll.stop();     // Pause scrolling

// Navigation
scroll.scrollTo(target, options);
scroll.setScroll(x, y);

// Events
scroll.on('scroll', callback);
scroll.on('call', callback);
scroll.off('scroll', callback);
```

## Performance Optimization

1. **Use `data-scroll-section`** to segment long pages:
```html
<div data-scroll-container>
  <div data-scroll-section>Section 1</div>
  <div data-scroll-section>Section 2</div>
  <div data-scroll-section>Section 3</div>
</div>
```

2. **Limit parallax elements** - Too many can impact performance

3. **Disable on mobile** if performance is poor:
```javascript
smartphone: { smooth: false }
```

4. **Update on resize**:
```javascript
window.addEventListener('resize', () => {
  scroll.update();
});
```

5. **Destroy when not needed**:
```javascript
scroll.destroy();
```

## Common Pitfalls

### 1. Fixed Positioning Issues

**Problem**: `position: fixed` elements break with smooth scroll

**Solution**: Use `data-scroll-sticky` instead or add fixed elements outside container:
```html
<!-- Fixed nav outside container -->
<nav style="position: fixed;">Navigation</nav>

<div data-scroll-container>
  <!-- Page content -->
</div>
```

### 2. Images Not Lazy Loading

**Problem**: All images load at once

**Solution**: Integrate with lazy loading:
```html
<img data-scroll data-src="image.jpg" class="lazy">
```

```javascript
scroll.on('call', (func) => {
  if (func === 'lazyLoad') {
    // Trigger lazy load
  }
});
```

### 3. Scroll Position Not Updating

**Problem**: Dynamic content doesn't update scroll positions

**Solution**: Call `update()` after DOM changes:
```javascript
// After adding content
addDynamicContent();
scroll.update();
```

### 4. Accessibility Concerns

**Problem**: Screen readers and keyboard navigation broken

**Solution**: Provide disable option:
```javascript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const scroll = new LocomotiveScroll({
  smooth: !prefersReducedMotion
});
```

### 5. Memory Leaks

**Problem**: Scroll instance not cleaned up on route changes (SPAs)

**Solution**: Always destroy on unmount:
```javascript
// React example
useEffect(() => {
  const scroll = new LocomotiveScroll();

  return () => scroll.destroy();
}, []);
```

### 6. Z-Index Fighting

**Problem**: Parallax elements overlap incorrectly

**Solution**: Set explicit z-index on parallax layers:
```css
[data-scroll-speed] {
  position: relative;
  z-index: var(--layer-depth);
}
```

## Related Skills

- **gsap-scrolltrigger**: Advanced scroll-driven animations (use together)
- **barba-js**: Page transitions with Locomotive Scroll integration
- **scroll-reveal-libraries**: Simpler alternative for basic fade-in effects
- **react-three-fiber**: Scroll-driven 3D scenes (sync with Locomotive events)
- **motion-framer**: Alternative scroll animations in React

## Resources

- **Scripts**: `generate_config.py` - Configuration generator, `integration_helper.py` - GSAP integration code
- **References**: `api_reference.md` - Complete API, `gsap_integration.md` - GSAP ScrollTrigger patterns
- **Assets**: `starter_locomotive/` - Complete starter template with examples



===== FILE: plugins/individual/locomotive-scroll/skills/locomotive-scroll/references/api_reference.md =====

# Locomotive Scroll API Reference

Complete API documentation for Locomotive Scroll.

## Table of Contents

- [Constructor Options](#constructor-options)
- [Data Attributes](#data-attributes)
- [Instance Methods](#instance-methods)
- [Events](#events)
- [Properties](#properties)

## Constructor Options

```javascript
new LocomotiveScroll(options)
```

### Global Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `el` | HTMLElement | `document` | Scroll container element |
| `name` | string | `'scroll'` | Data attribute prefix |
| `offset` | array | `[0, 0]` | Global offset `[bottom, top]` in px or % |
| `repeat` | boolean | `false` | Repeat in-view detection |
| `smooth` | boolean | `false` | Enable smooth scrolling |
| `initPosition` | object | `{x: 0, y: 0}` | Initial scroll position |
| `direction` | string | `'vertical'` | Scroll direction: `'vertical'` or `'horizontal'` |
| `gestureDirection` | string | `'vertical'` | Gesture direction: `'vertical'`, `'horizontal'`, or `'both'` |
| `reloadOnContextChange` | boolean | `false` | Reload on window resize |
| `lerp` | number | `0.1` | Linear interpolation amount (0-1, lower = smoother) |
| `class` | string | `'is-inview'` | Class applied to in-view elements |
| `scrollbarContainer` | HTMLElement/boolean | `false` | Custom scrollbar container or `false` to hide |
| `scrollbarClass` | string | `'c-scrollbar'` | Custom scrollbar class |
| `scrollingClass` | string | `'has-scroll-scrolling'` | Class added while scrolling |
| `draggingClass` | string | `'has-scroll-dragging'` | Class added while dragging scrollbar |
| `smoothClass` | string | `'has-scroll-smooth'` | Class added when smooth enabled |
| `initClass` | string | `'has-scroll-init'` | Class added on init |
| `getSpeed` | boolean | `false` | Add scroll speed to event |
| `getDirection` | boolean | `false` | Add scroll direction to event |
| `scrollFromAnywhere` | boolean | `false` | Trigger smooth scroll from anywhere |
| `multiplier` | number | `1` | Scroll speed multiplier |
| `firefoxMultiplier` | number | `50` | Firefox-specific multiplier |
| `touchMultiplier` | number | `2` | Touch scroll multiplier |
| `resetNativeScroll` | boolean | `true` | Reset scroll on refresh |

### Mobile/Tablet Options

```javascript
{
  tablet: {
    smooth: boolean,
    direction: string,
    gestureDirection: string,
    breakpoint: number  // Default: 1024
  },
  smartphone: {
    smooth: boolean,
    direction: string,
    gestureDirection: string,
    breakpoint: number  // Default: 767
  }
}
```

**Example**:
```javascript
new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,
  tablet: {
    smooth: true,
    breakpoint: 1024
  },
  smartphone: {
    smooth: false,
    breakpoint: 768
  }
});
```

## Data Attributes

### Container Attributes

| Attribute | Description |
|-----------|-------------|
| `data-scroll-container` | Main scroll container (required) |
| `data-scroll-section` | Section wrapper for performance optimization |

**Example**:
```html
<div data-scroll-container>
  <div data-scroll-section>
    <!-- Content -->
  </div>
</div>
```

### Element Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `data-scroll` | - | Mark element for detection |
| `data-scroll-id` | string | Unique identifier for element |
| `data-scroll-class` | string | Custom class when in view |
| `data-scroll-offset` | string | Element-specific offset (px or %) |
| `data-scroll-repeat` | boolean | Repeat in-view detection |
| `data-scroll-call` | string | Function to call when in view |
| `data-scroll-speed` | number | Parallax speed multiplier |
| `data-scroll-direction` | string | Parallax direction: `'vertical'` or `'horizontal'` |
| `data-scroll-delay` | number | Parallax delay (0-1) |
| `data-scroll-position` | string | When to start parallax: `'top'`, `'bottom'`, `'left'`, `'right'` |
| `data-scroll-target` | string | Target element selector for position reference |
| `data-scroll-sticky` | - | Enable sticky positioning |

### Detailed Attribute Explanations

#### `data-scroll-speed`

Controls parallax intensity:
- **Positive values**: Element moves faster than scroll
- **Negative values**: Element moves in opposite direction
- **0-1**: Element moves slower than scroll
- **> 1**: Element moves faster than scroll

```html
<!-- Background layer (slow) -->
<div data-scroll data-scroll-speed="0.5">Slow</div>

<!-- Normal speed -->
<div data-scroll data-scroll-speed="1">Normal</div>

<!-- Foreground layer (fast) -->
<div data-scroll data-scroll-speed="3">Fast</div>

<!-- Reverse -->
<div data-scroll data-scroll-speed="-2">Reverse</div>
```

#### `data-scroll-direction`

Axis for parallax effect:

```html
<!-- Vertical parallax (default) -->
<div data-scroll data-scroll-speed="2" data-scroll-direction="vertical">V</div>

<!-- Horizontal parallax -->
<div data-scroll data-scroll-speed="2" data-scroll-direction="horizontal">H</div>
```

#### `data-scroll-offset`

Custom trigger point:

```html
<!-- Trigger when element is 20% from bottom -->
<div data-scroll data-scroll-offset="20%">Offset %</div>

<!-- Trigger 100px from bottom -->
<div data-scroll data-scroll-offset="100">Offset px</div>

<!-- Different bottom/top offsets -->
<div data-scroll data-scroll-offset="10%,30%">Custom offsets</div>
```

#### `data-scroll-sticky`

Pin element within boundaries:

```html
<!-- Sticky within section -->
<div data-scroll-section>
  <div data-scroll data-scroll-sticky>
    Sticks within section
  </div>
</div>

<!-- Sticky with custom target -->
<div id="container">
  <div data-scroll data-scroll-sticky data-scroll-target="#container">
    Sticks within #container
  </div>
</div>
```

#### `data-scroll-call`

Trigger callback when in view:

```html
<div data-scroll data-scroll-call="myFunction">
  Triggers 'myFunction' when visible
</div>
```

```javascript
scroll.on('call', (func, way, obj) => {
  if (func === 'myFunction') {
    console.log('Element is', way); // 'enter' or 'exit'
  }
});
```

#### `data-scroll-repeat`

Re-trigger detection on each scroll:

```html
<!-- Fires once (default) -->
<div data-scroll>Fires once</div>

<!-- Fires every time -->
<div data-scroll data-scroll-repeat>Fires repeatedly</div>
```

## Instance Methods

### `init()`

Reinitialize scroll instance.

```javascript
scroll.init();
```

### `update()`

Recalculate element positions. Call after DOM changes.

```javascript
// After adding content
addContent();
scroll.update();
```

### `destroy()`

Remove event listeners and clean up. Essential for SPAs.

```javascript
scroll.destroy();
```

### `start()`

Resume scrolling after `stop()`.

```javascript
scroll.start();
```

### `stop()`

Pause scrolling (disable smooth scroll).

```javascript
scroll.stop();
```

### `scrollTo(target, options)`

Programmatically scroll to target.

**Parameters**:
- `target`: Can be:
  - `'top'` - Scroll to top
  - `'bottom'` - Scroll to bottom
  - `number` - Pixel value
  - `string` - CSS selector
  - `HTMLElement` - DOM element

- `options` (optional):
  ```javascript
  {
    offset: number,           // Offset in pixels (default: 0)
    callback: function,       // Callback after scroll
    duration: number,         // Duration in ms (default: 1000)
    easing: [n,n,n,n],       // Cubic bezier array (default: [0.25, 0.00, 0.35, 1.00])
    disableLerp: boolean,    // Disable smooth lerp (default: false)
    onComplete: function     // Same as callback
  }
  ```

**Examples**:
```javascript
// Scroll to top
scroll.scrollTo('top');

// Scroll to element
scroll.scrollTo('#section');

// Scroll to pixel value
scroll.scrollTo(500);

// Scroll with options
scroll.scrollTo('#section', {
  offset: -100,
  duration: 2000,
  easing: [0.25, 0.0, 0.35, 1.0],
  callback: () => console.log('Done!')
});

// Instant scroll (no smooth)
scroll.scrollTo('#section', {
  disableLerp: true
});
```

### `setScroll(x, y)`

Set scroll position instantly without animation.

```javascript
scroll.setScroll(0, 500); // x, y
```

### `on(event, callback)`

Add event listener.

```javascript
scroll.on('scroll', (args) => {
  console.log(args);
});
```

### `off(event, callback)`

Remove event listener.

```javascript
const handler = (args) => console.log(args);
scroll.on('scroll', handler);
scroll.off('scroll', handler);
```

## Events

### `scroll`

Fires on scroll. Receives object with:

```javascript
scroll.on('scroll', (args) => {
  // Scroll position
  console.log(args.scroll.x);     // Horizontal scroll
  console.log(args.scroll.y);     // Vertical scroll

  // Scroll limits
  console.log(args.limit.x);      // Max horizontal scroll
  console.log(args.limit.y);      // Max vertical scroll

  // Speed (if getSpeed: true)
  console.log(args.speed);

  // Direction (if getDirection: true)
  console.log(args.direction);    // 'up', 'down', 'left', 'right'

  // Current in-view elements
  console.log(args.currentElements);

  // Access specific element
  if (args.currentElements['hero']) {
    const el = args.currentElements['hero'];
    console.log(el.progress);  // 0 to 1
    console.log(el.el);        // DOM element
    console.log(el.id);        // data-scroll-id value
  }
});
```

**currentElements structure**:
```javascript
{
  'element-id': {
    el: HTMLElement,      // DOM element
    id: string,           // data-scroll-id
    class: string,        // data-scroll-class
    top: number,          // Distance from top
    middle: number,       // Distance from middle
    bottom: number,       // Distance from bottom
    offset: object,       // {top, bottom}
    progress: number,     // 0 to 1
    inView: boolean,      // Is in view
    call: string          // data-scroll-call value
  }
}
```

### `call`

Fires when element with `data-scroll-call` enters/exits viewport.

```javascript
scroll.on('call', (func, way, obj) => {
  console.log(func);  // data-scroll-call value
  console.log(way);   // 'enter' or 'exit'
  console.log(obj);   // {el, id}
});
```

**Example**:
```html
<div data-scroll data-scroll-call="playVideo">Video</div>
```

```javascript
scroll.on('call', (func, way) => {
  if (func === 'playVideo' && way === 'enter') {
    video.play();
  }
});
```

## Properties

### `scroll.scroll`

Current scroll state:

```javascript
console.log(scroll.scroll);
// {
//   x: 0,      // Horizontal position
//   y: 150     // Vertical position
// }
```

### `scroll.limit`

Max scroll values:

```javascript
console.log(scroll.limit);
// {
//   x: 0,      // Max horizontal
//   y: 2500    // Max vertical
// }
```

### `scroll.speed`

Current scroll speed (if `getSpeed: true`):

```javascript
console.log(scroll.speed); // Number
```

### `scroll.direction`

Current scroll direction (if `getDirection: true`):

```javascript
console.log(scroll.direction); // 'up' | 'down' | 'left' | 'right'
```

## Complete Usage Example

```javascript
import LocomotiveScroll from 'locomotive-scroll';

const scroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,
  lerp: 0.05,
  multiplier: 1,
  class: 'is-inview',
  repeat: false,
  offset: ['10%', 0],
  getSpeed: true,
  getDirection: true,
  smartphone: {
    smooth: false,
    breakpoint: 768
  }
});

// Track scroll
scroll.on('scroll', (args) => {
  console.log(args.scroll.y);

  if (args.currentElements['hero']) {
    const progress = args.currentElements['hero'].progress;
    // Sync with animation
  }
});

// Handle call events
scroll.on('call', (func, way) => {
  if (func === 'lazyLoad' && way === 'enter') {
    loadImages();
  }
});

// Update on window resize
window.addEventListener('resize', () => scroll.update());

// Cleanup on unmount
window.addEventListener('beforeunload', () => scroll.destroy());
```



===== FILE: plugins/individual/locomotive-scroll/skills/locomotive-scroll/references/gsap_integration.md =====

# GSAP ScrollTrigger Integration with Locomotive Scroll

Complete guide for integrating Locomotive Scroll with GSAP ScrollTrigger for advanced scroll-driven animations.

## Table of Contents

- [Why Combine Them](#why-combine-them)
- [Basic Integration](#basic-integration)
- [ScrollTrigger Proxy Setup](#scrolltrigger-proxy-setup)
- [Common Animation Patterns](#common-animation-patterns)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## Why Combine Them

**Locomotive Scroll** provides:
- Smooth scrolling UX
- Parallax effects
- Viewport detection

**GSAP ScrollTrigger** provides:
- Advanced timeline control
- Precise scrubbing
- Pin/snap functionality
- Complex animation sequencing

**Together** they create:
- Smooth scroll + scroll-driven animations
- Parallax + complex timelines
- Premium scroll experiences

## Basic Integration

### 1. Installation

```bash
npm install locomotive-scroll gsap
```

### 2. Complete Integration Setup

```javascript
import LocomotiveScroll from 'locomotive-scroll';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// Initialize Locomotive Scroll
const locoScroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,
  smartphone: {
    smooth: true
  },
  tablet: {
    smooth: true
  }
});

// Sync Locomotive Scroll with ScrollTrigger
locoScroll.on('scroll', ScrollTrigger.update);

// Tell ScrollTrigger to use Locomotive Scroll's scroller
ScrollTrigger.scrollerProxy('[data-scroll-container]', {
  scrollTop(value) {
    return arguments.length
      ? locoScroll.scrollTo(value, {duration: 0, disableLerp: true})
      : locoScroll.scroll.instance.scroll.y;
  },
  getBoundingClientRect() {
    return {
      top: 0,
      left: 0,
      width: window.innerWidth,
      height: window.innerHeight
    };
  },
  pinType: document.querySelector('[data-scroll-container]').style.transform
    ? 'transform'
    : 'fixed'
});

// Update ScrollTrigger when Locomotive Scroll updates
ScrollTrigger.addEventListener('refresh', () => locoScroll.update());

// Refresh both after DOM loads
ScrollTrigger.refresh();
```

## ScrollTrigger Proxy Setup

### Understanding scrollerProxy

The `scrollerProxy` tells ScrollTrigger how to interact with Locomotive Scroll's custom scroller:

```javascript
ScrollTrigger.scrollerProxy('[data-scroll-container]', {
  // Get/Set scroll position
  scrollTop(value) {
    if (arguments.length) {
      // Setter - scroll to position
      locoScroll.scrollTo(value, {
        duration: 0,        // Instant
        disableLerp: true   // No smooth interpolation
      });
    } else {
      // Getter - return current position
      return locoScroll.scroll.instance.scroll.y;
    }
  },

  // Define scroller dimensions
  getBoundingClientRect() {
    return {
      top: 0,
      left: 0,
      width: window.innerWidth,
      height: window.innerHeight
    };
  },

  // pinType determines how pinning works
  // 'transform' for smooth scroll, 'fixed' for native
  pinType: document.querySelector('[data-scroll-container]').style.transform
    ? 'transform'
    : 'fixed'
});
```

### For Horizontal Scroll

```javascript
ScrollTrigger.scrollerProxy('[data-scroll-container]', {
  scrollLeft(value) {
    return arguments.length
      ? locoScroll.scrollTo(value, {duration: 0, disableLerp: true})
      : locoScroll.scroll.instance.scroll.x;
  },
  getBoundingClientRect() {
    return {
      top: 0,
      left: 0,
      width: window.innerWidth,
      height: window.innerHeight
    };
  }
});
```

## Common Animation Patterns

### 1. Fade In on Scroll

```javascript
gsap.to('.fade-in', {
  scrollTrigger: {
    trigger: '.fade-in',
    scroller: '[data-scroll-container]',
    start: 'top 80%',
    end: 'top 50%',
    scrub: true,
    markers: true // Debug markers
  },
  opacity: 1,
  y: 0,
  duration: 1
});
```

```html
<div class="fade-in" style="opacity: 0; transform: translateY(50px);">
  Fades in on scroll
</div>
```

### 2. Pin Section While Scrolling

```javascript
ScrollTrigger.create({
  trigger: '#pinned-section',
  scroller: '[data-scroll-container]',
  pin: true,
  start: 'top top',
  end: 'bottom bottom',
  pinSpacing: false
});
```

```html
<div data-scroll-section id="pinned-section">
  This section pins while you scroll
</div>
```

### 3. Scrubbed Timeline Animation

```javascript
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '#animated-section',
    scroller: '[data-scroll-container]',
    start: 'top top',
    end: 'bottom bottom',
    scrub: 1, // Smooth scrubbing (1 second delay)
    pin: true
  }
});

tl.from('.box-1', { x: -100, opacity: 0 })
  .from('.box-2', { x: 100, opacity: 0 })
  .from('.box-3', { y: 100, opacity: 0 })
  .to('.box-1', { rotation: 360, scale: 1.5 });
```

### 4. Progress-Based Animation

Sync animations with Locomotive Scroll's progress values:

```javascript
locoScroll.on('scroll', (args) => {
  if (args.currentElements['hero']) {
    const progress = args.currentElements['hero'].progress;

    // Animate based on progress (0 to 1)
    gsap.to('#hero-image', {
      scale: 1 + progress * 0.5,
      rotation: progress * 360,
      duration: 0
    });
  }
});
```

```html
<div data-scroll data-scroll-id="hero">
  <img id="hero-image" src="hero.jpg" alt="Hero">
</div>
```

### 5. Horizontal Scroll Animation

```javascript
const sections = gsap.utils.toArray('.panel');

gsap.to(sections, {
  xPercent: -100 * (sections.length - 1),
  ease: 'none',
  scrollTrigger: {
    trigger: '#horizontal-container',
    scroller: '[data-scroll-container]',
    pin: true,
    scrub: 1,
    end: () => `+=${document.querySelector('#horizontal-container').offsetWidth}`
  }
});
```

```html
<div data-scroll-section id="horizontal-container">
  <div class="panel">Panel 1</div>
  <div class="panel">Panel 2</div>
  <div class="panel">Panel 3</div>
</div>
```

```css
#horizontal-container {
  display: flex;
  width: 300vw;
}
.panel {
  width: 100vw;
  height: 100vh;
}
```

### 6. Stagger Animation

```javascript
gsap.from('.item', {
  scrollTrigger: {
    trigger: '.items-container',
    scroller: '[data-scroll-container]',
    start: 'top 80%',
    end: 'top 30%',
    scrub: 1
  },
  y: 100,
  opacity: 0,
  stagger: 0.2
});
```

```html
<div class="items-container" data-scroll-section>
  <div class="item">Item 1</div>
  <div class="item">Item 2</div>
  <div class="item">Item 3</div>
  <div class="item">Item 4</div>
</div>
```

### 7. Image Reveal Effect

```javascript
gsap.to('.reveal-image img', {
  scrollTrigger: {
    trigger: '.reveal-image',
    scroller: '[data-scroll-container]',
    start: 'top 80%',
    end: 'top 30%',
    scrub: true
  },
  scale: 1,
  clipPath: 'inset(0% 0% 0% 0%)'
});
```

```html
<div class="reveal-image">
  <img src="image.jpg" style="scale: 1.2; clip-path: inset(10% 10% 10% 10%);">
</div>
```

### 8. Text Split Animation

```javascript
// Split text into characters
const text = document.querySelector('.split-text');
const chars = text.textContent.split('');
text.innerHTML = chars.map(char => `<span>${char}</span>`).join('');

// Animate each character
gsap.from('.split-text span', {
  scrollTrigger: {
    trigger: '.split-text',
    scroller: '[data-scroll-container]',
    start: 'top 80%',
    end: 'top 50%',
    scrub: 1
  },
  opacity: 0,
  y: 50,
  rotationX: -90,
  stagger: 0.02
});
```

## Performance Optimization

### 1. Refresh Strategy

Only refresh when needed:

```javascript
// Update Locomotive Scroll on window resize
let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    locoScroll.update();
    ScrollTrigger.refresh();
  }, 250);
});
```

### 2. Lazy Initialization

Create ScrollTriggers only when sections are near viewport:

```javascript
locoScroll.on('call', (func, way, obj) => {
  if (func === 'initAnimations' && way === 'enter') {
    // Initialize animations for this section
    initSectionAnimations(obj.el);
  }
});
```

```html
<div data-scroll data-scroll-call="initAnimations">
  <!-- Animations initialized only when visible -->
</div>
```

### 3. Kill ScrollTriggers

Destroy when no longer needed:

```javascript
const st = ScrollTrigger.create({
  trigger: '.temp-animation',
  scroller: '[data-scroll-container]',
  onEnter: () => {
    // Animation complete
    st.kill(); // Remove ScrollTrigger
  }
});
```

### 4. Use will-change Sparingly

```css
[data-scroll] {
  /* Only on elements that actually animate */
  will-change: transform;
}
```

### 5. Normalize ScrollTrigger Updates

```javascript
// Throttle updates
let ticking = false;

locoScroll.on('scroll', () => {
  if (!ticking) {
    window.requestAnimationFrame(() => {
      ScrollTrigger.update();
      ticking = false;
    });
    ticking = true;
  }
});
```

## Complete React Example

```javascript
import { useEffect, useRef } from 'react';
import LocomotiveScroll from 'locomotive-scroll';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

function App() {
  const scrollRef = useRef(null);
  const locoScrollRef = useRef(null);

  useEffect(() => {
    const locoScroll = new LocomotiveScroll({
      el: scrollRef.current,
      smooth: true,
      smartphone: { smooth: true },
      tablet: { smooth: true }
    });

    locoScrollRef.current = locoScroll;

    locoScroll.on('scroll', ScrollTrigger.update);

    ScrollTrigger.scrollerProxy(scrollRef.current, {
      scrollTop(value) {
        return arguments.length
          ? locoScroll.scrollTo(value, {duration: 0, disableLerp: true})
          : locoScroll.scroll.instance.scroll.y;
      },
      getBoundingClientRect() {
        return {
          top: 0,
          left: 0,
          width: window.innerWidth,
          height: window.innerHeight
        };
      },
      pinType: scrollRef.current.style.transform ? 'transform' : 'fixed'
    });

    ScrollTrigger.addEventListener('refresh', () => locoScroll.update());
    ScrollTrigger.refresh();

    // Cleanup
    return () => {
      locoScroll.destroy();
      ScrollTrigger.getAll().forEach(st => st.kill());
    };
  }, []);

  useEffect(() => {
    // Animation example
    gsap.to('.animated-element', {
      scrollTrigger: {
        trigger: '.animated-element',
        scroller: scrollRef.current,
        start: 'top 80%',
        scrub: true
      },
      opacity: 1,
      y: 0
    });
  }, []);

  return (
    <div data-scroll-container ref={scrollRef}>
      <div data-scroll-section>
        <h1 className="animated-element">Hello World</h1>
      </div>
    </div>
  );
}
```

## Troubleshooting

### Issue: Animations Don't Trigger

**Cause**: ScrollTrigger not synced properly

**Solution**: Ensure scroller proxy is set correctly:
```javascript
ScrollTrigger.scrollerProxy('[data-scroll-container]', {
  // ... proxy setup
});
```

### Issue: Pin Not Working

**Cause**: pinType mismatch

**Solution**: Check transform vs fixed:
```javascript
pinType: document.querySelector('[data-scroll-container]').style.transform
  ? 'transform'
  : 'fixed'
```

### Issue: Scroll Position Jumps

**Cause**: Conflicting smooth scroll implementations

**Solution**: Disable lerp in scrollTo:
```javascript
scrollTop(value) {
  return arguments.length
    ? locoScroll.scrollTo(value, {duration: 0, disableLerp: true})
    : locoScroll.scroll.instance.scroll.y;
}
```

### Issue: Markers Not Showing

**Cause**: Markers are positioned for native scroll

**Solution**: Use ScrollTrigger's built-in markers with scroller specified:
```javascript
scrollTrigger: {
  scroller: '[data-scroll-container]',
  markers: true
}
```

### Issue: Performance Degradation

**Solutions**:
1. Reduce `scrub` value (use `scrub: 1` instead of `scrub: true`)
2. Limit number of ScrollTriggers
3. Use `once: true` for one-time animations
4. Throttle scroll updates

### Issue: React/SPA Route Changes

**Cause**: ScrollTriggers and Locomotive Scroll not cleaned up

**Solution**: Always destroy on unmount:
```javascript
useEffect(() => {
  const scroll = new LocomotiveScroll();

  return () => {
    scroll.destroy();
    ScrollTrigger.getAll().forEach(st => st.kill());
  };
}, []);
```

## Advanced Pattern: Locomotive + ScrollTrigger + Three.js

```javascript
import * as THREE from 'three';

// Three.js scene setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight);
const renderer = new THREE.WebGLRenderer();

// Locomotive Scroll + ScrollTrigger setup
const locoScroll = new LocomotiveScroll({ /* ... */ });

// Sync 3D camera with scroll
locoScroll.on('scroll', (args) => {
  const scrollY = args.scroll.y;
  camera.position.y = scrollY * 0.001;
  renderer.render(scene, camera);
});

// GSAP timeline for 3D objects
gsap.to(mesh.rotation, {
  scrollTrigger: {
    trigger: '#3d-section',
    scroller: '[data-scroll-container]',
    scrub: 1
  },
  y: Math.PI * 2
});
```

## Resources

- [Locomotive Scroll GitHub](https://github.com/locomotivemtl/locomotive-scroll)
- [GSAP ScrollTrigger Docs](https://greensock.com/docs/v3/Plugins/ScrollTrigger)
- [CodePen Examples](https://codepen.io/tag/locomotive-scroll)



===== FILE: plugins/individual/locomotive-scroll/agents/locomotive-scroll-specialist.md =====

# Locomotive Scroll Specialist

## Role

Expert specialist in Locomotive Scroll implementation, patterns, and best practices.

## Expertise

- Locomotive Scroll core concepts and patterns
- Integration with other libraries and frameworks
- Performance optimization
- Common pitfalls and solutions
- Best practices and conventions

## When to use

Activate this agent when working on:
- Locomotive Scroll implementation challenges
- Integration with other technologies
- Performance optimization
- Troubleshooting and debugging
- Architecture decisions

## Approach

1. Understand project requirements and context
2. Apply Locomotive Scroll best practices
3. Recommend optimal implementation patterns
4. Identify and solve common issues
5. Provide detailed guidance and examples

## Tools

This agent has access to:
- Locomotive Scroll skill knowledge
- Pattern libraries and examples
- Troubleshooting guides
- Integration patterns



===== FILE: plugins/individual/locomotive-scroll/commands/generate_config.md =====

# /locomotive-scroll-generate_config

Locomotive Scroll - Generate Config

## Description

Executes the generate_config script for Locomotive Scroll.

## Usage

```bash
/locomotive-scroll-generate_config
```

## Implementation

This command runs the `generate_config.py` script from the Locomotive Scroll skill, which provides automated assistance for generate config.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/locomotive-scroll/commands/integration_helper.md =====

# /locomotive-scroll-integration_helper

Locomotive Scroll - Integration Helper

## Description

Executes the integration_helper script for Locomotive Scroll.

## Usage

```bash
/locomotive-scroll-integration_helper
```

## Implementation

This command runs the `integration_helper.py` script from the Locomotive Scroll skill, which provides automated assistance for integration helper.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/locomotive-scroll/skills/locomotive-scroll/scripts/generate_config.py =====

```py
#!/usr/bin/env python3
"""
Locomotive Scroll Configuration Generator

Generates Locomotive Scroll configuration code with customizable options.

Usage:
    ./generate_config.py                    # Interactive mode
    ./generate_config.py --smooth           # Quick smooth scroll setup
    ./generate_config.py --horizontal       # Horizontal scroll setup
    ./generate_config.py --preset performance  # Use performance preset
"""

import sys
import json

PRESETS = {
    "basic": {
        "name": "Basic Smooth Scroll",
        "options": {
            "smooth": True,
            "lerp": 0.1,
            "multiplier": 1,
        }
    },
    "smooth": {
        "name": "Premium Smooth Experience",
        "options": {
            "smooth": True,
            "lerp": 0.05,
            "multiplier": 1,
            "class": "is-inview",
            "offset": ["10%", 0],
            "getSpeed": True,
            "getDirection": True,
        }
    },
    "performance": {
        "name": "Performance Optimized",
        "options": {
            "smooth": True,
            "lerp": 0.1,
            "multiplier": 1,
            "smartphone": {
                "smooth": False,
                "breakpoint": 768
            },
            "tablet": {
                "smooth": True,
                "breakpoint": 1024
            }
        }
    },
    "horizontal": {
        "name": "Horizontal Scroll",
        "options": {
            "smooth": True,
            "direction": "horizontal",
            "lerp": 0.1,
            "multiplier": 1,
        }
    },
    "parallax": {
        "name": "Parallax & Detection",
        "options": {
            "smooth": True,
            "lerp": 0.08,
            "class": "is-inview",
            "offset": ["10%", 0],
            "repeat": False,
        }
    }
}


def print_header():
    print("=" * 60)
    print("Locomotive Scroll Configuration Generator")
    print("=" * 60)
    print()


def print_presets():
    print("Available Presets:")
    print()
    for i, (key, preset) in enumerate(PRESETS.items(), 1):
        print(f"  {i}. {preset['name']} ({key})")
    print()


def get_user_choice(prompt, options, default=None):
    """Get validated user input"""
    while True:
        if default:
            choice = input(f"{prompt} (default: {default}): ").strip() or default
        else:
            choice = input(f"{prompt}: ").strip()

        if choice in options:
            return choice
        print(f"Invalid choice. Please choose from: {', '.join(options)}")


def get_bool_input(prompt, default=True):
    """Get boolean input from user"""
    default_str = "Y/n" if default else "y/N"
    while True:
        choice = input(f"{prompt} ({default_str}): ").strip().lower() or ("y" if default else "n")
        if choice in ["y", "yes"]:
            return True
        elif choice in ["n", "no"]:
            return False
        print("Please enter 'y' or 'n'")


def get_number_input(prompt, default, min_val=None, max_val=None):
    """Get numeric input with validation"""
    while True:
        value = input(f"{prompt} (default: {default}): ").strip() or str(default)
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                print(f"Value must be >= {min_val}")
                continue
            if max_val is not None and num > max_val:
                print(f"Value must be <= {max_val}")
                continue
            return num
        except ValueError:
            print("Please enter a valid number")


def interactive_config():
    """Interactive configuration builder"""
    print_header()
    print("Let's build your Locomotive Scroll configuration!\n")

    # Ask if user wants a preset
    use_preset = get_bool_input("Start with a preset?", default=True)

    if use_preset:
        print_presets()
        preset_choice = get_user_choice(
            "Choose preset",
            list(PRESETS.keys()),
            default="basic"
        )
        config = PRESETS[preset_choice]["options"].copy()
        print(f"\n✅ Starting with '{PRESETS[preset_choice]['name']}' preset\n")
    else:
        config = {}

    # Core options
    print("Core Options:")
    print("-" * 40)

    if "smooth" not in config:
        config["smooth"] = get_bool_input("Enable smooth scrolling?", default=True)

    if config.get("smooth"):
        if "lerp" not in config:
            config["lerp"] = get_number_input(
                "Lerp value (smoothness, lower = smoother)",
                default=0.1,
                min_val=0.01,
                max_val=1.0
            )

    if "direction" not in config:
        direction = get_user_choice(
            "Scroll direction",
            ["vertical", "horizontal"],
            default="vertical"
        )
        if direction != "vertical":
            config["direction"] = direction

    if "multiplier" not in config:
        config["multiplier"] = get_number_input(
            "Speed multiplier",
            default=1,
            min_val=0.1,
            max_val=5.0
        )

    # Advanced options
    print("\nAdvanced Options:")
    print("-" * 40)

    if get_bool_input("Configure viewport detection?", default=False):
        config["class"] = input("In-view class name (default: is-inview): ").strip() or "is-inview"
        config["repeat"] = get_bool_input("Repeat in-view detection?", default=False)

        if get_bool_input("Set global offset?", default=False):
            bottom = input("Bottom offset (default: 0): ").strip() or "0"
            top = input("Top offset (default: 0): ").strip() or "0"
            config["offset"] = [bottom, top]

    if get_bool_input("Enable scroll tracking (speed/direction)?", default=False):
        config["getSpeed"] = True
        config["getDirection"] = True

    # Mobile options
    print("\nMobile/Tablet Options:")
    print("-" * 40)

    if get_bool_input("Configure mobile settings?", default=True):
        # Smartphone
        config["smartphone"] = {
            "smooth": get_bool_input("Enable smooth scroll on smartphones?", default=False),
            "breakpoint": int(get_number_input("Smartphone breakpoint", default=768, min_val=320))
        }

        # Tablet
        config["tablet"] = {
            "smooth": get_bool_input("Enable smooth scroll on tablets?", default=True),
            "breakpoint": int(get_number_input("Tablet breakpoint", default=1024, min_val=768))
        }

    return config


def generate_js_code(config):
    """Generate JavaScript initialization code"""
    code = f"""// Locomotive Scroll Configuration
import LocomotiveScroll from 'locomotive-scroll';
import 'locomotive-scroll/dist/locomotive-scroll.css';

const scroll = new LocomotiveScroll({{
  el: document.querySelector('[data-scroll-container]'),
{format_config_object(config, indent=1)}
}});

// Update on window resize
let resizeTimer;
window.addEventListener('resize', () => {{
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => scroll.update(), 250);
}});

// Cleanup
window.addEventListener('beforeunload', () => scroll.destroy());

export default scroll;
"""
    return code


def format_config_object(config, indent=0):
    """Format configuration object for JavaScript"""
    lines = []
    indent_str = "  " * indent

    for key, value in config.items():
        if isinstance(value, bool):
            lines.append(f"{indent_str}{key}: {str(value).lower()},")
        elif isinstance(value, (int, float)):
            lines.append(f"{indent_str}{key}: {value},")
        elif isinstance(value, str):
            lines.append(f"{indent_str}{key}: '{value}',")
        elif isinstance(value, list):
            formatted_list = str(value).replace("'", '"')
            lines.append(f"{indent_str}{key}: {formatted_list},")
        elif isinstance(value, dict):
            lines.append(f"{indent_str}{key}: {{")
            lines.append(format_config_object(value, indent + 1))
            lines.append(f"{indent_str}}},")

    return "\n".join(lines)


def generate_html_template():
    """Generate HTML template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Locomotive Scroll</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/locomotive-scroll/dist/locomotive-scroll.min.css">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    [data-scroll-container] {
      /* Container styles */
    }

    [data-scroll-section] {
      min-height: 100vh;
      padding: 4rem 2rem;
    }

    .is-inview {
      opacity: 1;
      transform: translateY(0);
      transition: opacity 0.6s, transform 0.6s;
    }

    [data-scroll] {
      opacity: 0;
      transform: translateY(50px);
    }
  </style>
</head>
<body>
  <div data-scroll-container>

    <div data-scroll-section>
      <h1 data-scroll data-scroll-speed="2">
        Locomotive Scroll
      </h1>
      <p data-scroll data-scroll-speed="1">
        Smooth scrolling experience
      </p>
    </div>

    <div data-scroll-section>
      <h2 data-scroll>Section 2</h2>
      <div data-scroll data-scroll-sticky>
        Sticky element
      </div>
    </div>

    <div data-scroll-section>
      <h2 data-scroll>Section 3</h2>
      <p data-scroll data-scroll-call="playVideo">
        Triggers callback
      </p>
    </div>

  </div>

  <script type="module" src="main.js"></script>
</body>
</html>
"""


def main():
    """Main function"""
    # Check for CLI arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lstrip('-')

        if arg in PRESETS:
            config = PRESETS[arg]["options"].copy()
            print(f"✅ Using '{PRESETS[arg]['name']}' preset")
        elif arg == "help":
            print(__doc__)
            return
        else:
            print(f"Unknown option: {arg}")
            print("Available presets:", ", ".join(PRESETS.keys()))
            return
    else:
        # Interactive mode
        config = interactive_config()

    # Generate code
    print("\n" + "=" * 60)
    print("Generated Configuration")
    print("=" * 60 + "\n")

    js_code = generate_js_code(config)
    print("JavaScript (main.js):")
    print("-" * 60)
    print(js_code)

    # Ask if user wants HTML template
    if get_bool_input("\nGenerate HTML template?", default=True):
        html = generate_html_template()
        print("\nHTML (index.html):")
        print("-" * 60)
        print(html)

    # Save to files?
    if get_bool_input("\nSave to files?", default=True):
        with open("locomotive-config.js", "w") as f:
            f.write(js_code)
        print("✅ Saved to locomotive-config.js")

        with open("locomotive-template.html", "w") as f:
            f.write(generate_html_template())
        print("✅ Saved to locomotive-template.html")

        # Save config as JSON
        with open("locomotive-config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("✅ Saved to locomotive-config.json")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()

```


===== FILE: plugins/individual/locomotive-scroll/skills/locomotive-scroll/scripts/integration_helper.py =====

```py
#!/usr/bin/env python3
"""
Locomotive Scroll + GSAP ScrollTrigger Integration Helper

Generates integration code for Locomotive Scroll with GSAP ScrollTrigger.

Usage:
    ./integration_helper.py                           # Interactive mode
    ./integration_helper.py --pattern fade-in         # Generate specific pattern
    ./integration_helper.py --framework react         # Framework-specific code
"""

import sys

ANIMATION_PATTERNS = {
    "fade-in": {
        "name": "Fade In on Scroll",
        "description": "Elements fade in as they enter viewport",
        "code": """gsap.to('.fade-in', {
  scrollTrigger: {
    trigger: '.fade-in',
    scroller: '[data-scroll-container]',
    start: 'top 80%',
    end: 'top 50%',
    scrub: true
  },
  opacity: 1,
  y: 0,
  duration: 1
});""",
        "html": """<div class="fade-in" style="opacity: 0; transform: translateY(50px);">
  Fades in on scroll
</div>"""
    },
    "pin-section": {
        "name": "Pin Section",
        "description": "Pin section while scrolling",
        "code": """ScrollTrigger.create({
  trigger: '#pinned-section',
  scroller: '[data-scroll-container]',
  pin: true,
  start: 'top top',
  end: 'bottom bottom',
  pinSpacing: false
});""",
        "html": """<div data-scroll-section id="pinned-section">
  This section pins while you scroll
</div>"""
    },
    "timeline": {
        "name": "Scrubbed Timeline",
        "description": "Timeline scrubbed with scroll progress",
        "code": """const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '#animated-section',
    scroller: '[data-scroll-container]',
    start: 'top top',
    end: 'bottom bottom',
    scrub: 1,
    pin: true
  }
});

tl.from('.box-1', { x: -100, opacity: 0 })
  .from('.box-2', { x: 100, opacity: 0 })
  .from('.box-3', { y: 100, opacity: 0 })
  .to('.box-1', { rotation: 360, scale: 1.5 });""",
        "html": """<div data-scroll-section id="animated-section">
  <div class="box-1">Box 1</div>
  <div class="box-2">Box 2</div>
  <div class="box-3">Box 3</div>
</div>"""
    },
    "horizontal-scroll": {
        "name": "Horizontal Scroll",
        "description": "Horizontal scrolling panels",
        "code": """const sections = gsap.utils.toArray('.panel');

gsap.to(sections, {
  xPercent: -100 * (sections.length - 1),
  ease: 'none',
  scrollTrigger: {
    trigger: '#horizontal-container',
    scroller: '[data-scroll-container]',
    pin: true,
    scrub: 1,
    end: () => `+=\${document.querySelector('#horizontal-container').offsetWidth}`
  }
});""",
        "html": """<div data-scroll-section id="horizontal-container" style="display: flex; width: 300vw;">
  <div class="panel" style="width: 100vw;">Panel 1</div>
  <div class="panel" style="width: 100vw;">Panel 2</div>
  <div class="panel" style="width: 100vw;">Panel 3</div>
</div>"""
    },
    "stagger": {
        "name": "Stagger Animation",
        "description": "Staggered element animations",
        "code": """gsap.from('.item', {
  scrollTrigger: {
    trigger: '.items-container',
    scroller: '[data-scroll-container]',
    start: 'top 80%',
    end: 'top 30%',
    scrub: 1
  },
  y: 100,
  opacity: 0,
  stagger: 0.2
});""",
        "html": """<div class="items-container" data-scroll-section>
  <div class="item">Item 1</div>
  <div class="item">Item 2</div>
  <div class="item">Item 3</div>
  <div class="item">Item 4</div>
</div>"""
    },
    "progress-based": {
        "name": "Progress-Based Animation",
        "description": "Sync with Locomotive Scroll progress",
        "code": """locoScroll.on('scroll', (args) => {
  if (args.currentElements['hero']) {
    const progress = args.currentElements['hero'].progress;

    gsap.to('#hero-image', {
      scale: 1 + progress * 0.5,
      rotation: progress * 360,
      duration: 0
    });
  }
});""",
        "html": """<div data-scroll data-scroll-id="hero">
  <img id="hero-image" src="hero.jpg" alt="Hero">
</div>"""
    }
}


def print_header():
    print("=" * 70)
    print("Locomotive Scroll + GSAP ScrollTrigger Integration Helper")
    print("=" * 70)
    print()


def print_patterns():
    print("Available Animation Patterns:")
    print()
    for i, (key, pattern) in enumerate(ANIMATION_PATTERNS.items(), 1):
        print(f"  {i}. {pattern['name']} ({key})")
        print(f"     {pattern['description']}")
        print()


def get_user_choice(prompt, options, default=None):
    """Get validated user input"""
    while True:
        if default:
            choice = input(f"{prompt} (default: {default}): ").strip() or default
        else:
            choice = input(f"{prompt}: ").strip()

        if choice in options:
            return choice
        print(f"Invalid choice. Please choose from: {', '.join(options)}")


def get_bool_input(prompt, default=True):
    """Get boolean input from user"""
    default_str = "Y/n" if default else "y/N"
    while True:
        choice = input(f"{prompt} ({default_str}): ").strip().lower() or ("y" if default else "n")
        if choice in ["y", "yes"]:
            return True
        elif choice in ["n", "no"]:
            return False
        print("Please enter 'y' or 'n'")


def generate_base_integration():
    """Generate base Locomotive + GSAP integration code"""
    return """// Locomotive Scroll + GSAP ScrollTrigger Integration
import LocomotiveScroll from 'locomotive-scroll';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// Initialize Locomotive Scroll
const locoScroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,
  smartphone: {
    smooth: true
  },
  tablet: {
    smooth: true
  }
});

// Sync Locomotive Scroll with ScrollTrigger
locoScroll.on('scroll', ScrollTrigger.update);

// Tell ScrollTrigger to use Locomotive Scroll's scroller
ScrollTrigger.scrollerProxy('[data-scroll-container]', {
  scrollTop(value) {
    return arguments.length
      ? locoScroll.scrollTo(value, {duration: 0, disableLerp: true})
      : locoScroll.scroll.instance.scroll.y;
  },
  getBoundingClientRect() {
    return {
      top: 0,
      left: 0,
      width: window.innerWidth,
      height: window.innerHeight
    };
  },
  pinType: document.querySelector('[data-scroll-container]').style.transform
    ? 'transform'
    : 'fixed'
});

// Update ScrollTrigger when Locomotive Scroll updates
ScrollTrigger.addEventListener('refresh', () => locoScroll.update());

// Refresh both after DOM loads
ScrollTrigger.refresh();
"""


def generate_react_integration():
    """Generate React-specific integration"""
    return """import { useEffect, useRef } from 'react';
import LocomotiveScroll from 'locomotive-scroll';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

function App() {
  const scrollRef = useRef(null);
  const locoScrollRef = useRef(null);

  useEffect(() => {
    const locoScroll = new LocomotiveScroll({
      el: scrollRef.current,
      smooth: true,
      smartphone: { smooth: true },
      tablet: { smooth: true }
    });

    locoScrollRef.current = locoScroll;

    locoScroll.on('scroll', ScrollTrigger.update);

    ScrollTrigger.scrollerProxy(scrollRef.current, {
      scrollTop(value) {
        return arguments.length
          ? locoScroll.scrollTo(value, {duration: 0, disableLerp: true})
          : locoScroll.scroll.instance.scroll.y;
      },
      getBoundingClientRect() {
        return {
          top: 0,
          left: 0,
          width: window.innerWidth,
          height: window.innerHeight
        };
      },
      pinType: scrollRef.current.style.transform ? 'transform' : 'fixed'
    });

    ScrollTrigger.addEventListener('refresh', () => locoScroll.update());
    ScrollTrigger.refresh();

    // Cleanup
    return () => {
      locoScroll.destroy();
      ScrollTrigger.getAll().forEach(st => st.kill());
    };
  }, []);

  // Add your animations in separate useEffect
  useEffect(() => {
    // Animation code here
  }, []);

  return (
    <div data-scroll-container ref={scrollRef}>
      <div data-scroll-section>
        {/* Your content */}
      </div>
    </div>
  );
}

export default App;
"""


def generate_vue_integration():
    """Generate Vue-specific integration"""
    return """<template>
  <div data-scroll-container ref="scrollContainer">
    <div data-scroll-section>
      <!-- Your content -->
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import LocomotiveScroll from 'locomotive-scroll';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default {
  setup() {
    const scrollContainer = ref(null);
    let locoScroll = null;

    onMounted(() => {
      locoScroll = new LocomotiveScroll({
        el: scrollContainer.value,
        smooth: true
      });

      locoScroll.on('scroll', ScrollTrigger.update);

      ScrollTrigger.scrollerProxy(scrollContainer.value, {
        scrollTop(value) {
          return arguments.length
            ? locoScroll.scrollTo(value, {duration: 0, disableLerp: true})
            : locoScroll.scroll.instance.scroll.y;
        },
        getBoundingClientRect() {
          return {
            top: 0,
            left: 0,
            width: window.innerWidth,
            height: window.innerHeight
          };
        },
        pinType: scrollContainer.value.style.transform ? 'transform' : 'fixed'
      });

      ScrollTrigger.addEventListener('refresh', () => locoScroll.update());
      ScrollTrigger.refresh();
    });

    onUnmounted(() => {
      if (locoScroll) locoScroll.destroy();
      ScrollTrigger.getAll().forEach(st => st.kill());
    });

    return { scrollContainer };
  }
};
</script>
"""


def main():
    """Main function"""
    # Check for CLI arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lstrip('-')

        if arg == "help":
            print(__doc__)
            return
        elif arg == "pattern":
            if len(sys.argv) > 2:
                pattern_key = sys.argv[2]
                if pattern_key in ANIMATION_PATTERNS:
                    pattern = ANIMATION_PATTERNS[pattern_key]
                    print(f"\n{pattern['name']}")
                    print("=" * 60)
                    print(f"{pattern['description']}\n")
                    print("JavaScript:")
                    print(pattern['code'])
                    print("\nHTML:")
                    print(pattern['html'])
                else:
                    print(f"Unknown pattern: {pattern_key}")
                    print("Available patterns:", ", ".join(ANIMATION_PATTERNS.keys()))
            else:
                print("Please specify a pattern")
            return
        elif arg == "framework":
            if len(sys.argv) > 2:
                framework = sys.argv[2].lower()
                if framework == "react":
                    print(generate_react_integration())
                elif framework == "vue":
                    print(generate_vue_integration())
                else:
                    print(f"Framework '{framework}' not supported. Available: react, vue")
            else:
                print("Please specify a framework (react or vue)")
            return

    # Interactive mode
    print_header()

    # Framework choice
    print("Choose your framework:")
    print("  1. Vanilla JavaScript")
    print("  2. React")
    print("  3. Vue")
    print()

    framework = get_user_choice("Framework", ["1", "2", "3"], default="1")

    print("\nGenerating base integration code...\n")
    print("=" * 70)

    if framework == "1":
        base_code = generate_base_integration()
        print(base_code)
    elif framework == "2":
        base_code = generate_react_integration()
        print(base_code)
    elif framework == "3":
        base_code = generate_vue_integration()
        print(base_code)

    # Add animation patterns
    if get_bool_input("\nAdd animation patterns?", default=True):
        print_patterns()

        patterns_to_add = []
        while True:
            pattern_key = get_user_choice(
                "Choose pattern (or 'done' to finish)",
                list(ANIMATION_PATTERNS.keys()) + ["done"],
                default="done"
            )

            if pattern_key == "done":
                break

            patterns_to_add.append(pattern_key)
            print(f"✅ Added {ANIMATION_PATTERNS[pattern_key]['name']}")

        if patterns_to_add:
            print("\n" + "=" * 70)
            print("Animation Patterns")
            print("=" * 70 + "\n")

            for pattern_key in patterns_to_add:
                pattern = ANIMATION_PATTERNS[pattern_key]
                print(f"// {pattern['name']}")
                print(f"// {pattern['description']}")
                print(pattern['code'])
                print()

            print("\n" + "=" * 70)
            print("Required HTML")
            print("=" * 70 + "\n")

            for pattern_key in patterns_to_add:
                pattern = ANIMATION_PATTERNS[pattern_key]
                print(f"<!-- {pattern['name']} -->")
                print(pattern['html'])
                print()

    # Save to file?
    if get_bool_input("\nSave to file?", default=True):
        filename = "locomotive-gsap-integration.js"

        with open(filename, "w") as f:
            f.write(base_code)

            if 'patterns_to_add' in locals() and patterns_to_add:
                f.write("\n// Animation Patterns\n")
                for pattern_key in patterns_to_add:
                    pattern = ANIMATION_PATTERNS[pattern_key]
                    f.write(f"\n// {pattern['name']}\n")
                    f.write(pattern['code'])
                    f.write("\n")

        print(f"✅ Saved to {filename}")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()

```


===== FILE: plugins/individual/locomotive-scroll/skills/locomotive-scroll/assets/starter_locomotive/README.md =====

# Locomotive Scroll Starter Template

Complete starter template demonstrating Locomotive Scroll features including smooth scrolling, parallax effects, sticky elements, viewport detection, and scroll events.

## Features

This template includes examples of:

- ✅ **Smooth Scrolling** - Hardware-accelerated smooth scroll with customizable lerp
- ✅ **Parallax Effects** - Multi-layered parallax with different speeds
- ✅ **Sticky Elements** - Elements that stick within defined boundaries
- ✅ **Viewport Detection** - Track when elements enter/exit viewport
- ✅ **Scroll Events** - Monitor scroll position, speed, and direction
- ✅ **Call Events** - Trigger callbacks when elements become visible
- ✅ **Progress Tracking** - Track element visibility progress (0 to 1)
- ✅ **Programmatic Scrolling** - Scroll to elements via JavaScript
- ✅ **Mobile Responsive** - Optimized settings for tablet and smartphone

## Quick Start

### Installation

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

### Build for Production

```bash
npm run build
```

## File Structure

```
starter_locomotive/
├── index.html          # Main HTML with Locomotive Scroll markup
├── style.css           # Styles including responsive design
├── main.js             # Locomotive Scroll initialization and events
├── package.json        # Dependencies
└── README.md           # This file
```

## Understanding the Code

### HTML Structure

Every Locomotive Scroll project requires specific data attributes:

```html
<!-- Main scroll container (required) -->
<div data-scroll-container>

  <!-- Section wrapper (optional, improves performance) -->
  <div data-scroll-section>

    <!-- Tracked element -->
    <h1 data-scroll data-scroll-speed="2">
      Smooth Parallax
    </h1>

  </div>
</div>
```

### Key Data Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `data-scroll` | Enable detection | `data-scroll` |
| `data-scroll-speed` | Parallax speed | `data-scroll-speed="2"` |
| `data-scroll-sticky` | Sticky positioning | `data-scroll-sticky` |
| `data-scroll-call` | Event trigger | `data-scroll-call="fadeIn"` |
| `data-scroll-id` | Unique identifier | `data-scroll-id="hero"` |

### Initialization Options

The template uses these configuration options:

```javascript
const scroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,         // Enable smooth scrolling
  lerp: 0.1,            // Smoothness (0-1, lower = smoother)
  multiplier: 1,        // Speed multiplier
  class: 'is-inview',   // Class added to visible elements
  repeat: true,         // Repeat in-view detection
  offset: ['10%', 0],   // Global offset [bottom, top]
  getSpeed: true,       // Track scroll speed
  getDirection: true,   // Track scroll direction

  // Mobile settings
  smartphone: {
    smooth: true,
    breakpoint: 768
  }
});
```

## Examples in the Template

### 1. Parallax Effects

```html
<!-- Slow parallax (background) -->
<div data-scroll data-scroll-speed="0.5">
  Background Layer
</div>

<!-- Fast parallax (foreground) -->
<div data-scroll data-scroll-speed="3">
  Foreground Layer
</div>

<!-- Reverse parallax -->
<div data-scroll data-scroll-speed="-2">
  Reverse Layer
</div>
```

### 2. Sticky Element

```html
<div data-scroll-section>
  <div data-scroll data-scroll-sticky>
    I stick while section is in view
  </div>
</div>
```

### 3. Scroll Call Events

```html
<div data-scroll data-scroll-call="fadeIn">
  Triggers callback when visible
</div>
```

```javascript
scroll.on('call', (func, way) => {
  if (func === 'fadeIn' && way === 'enter') {
    // Element entered viewport
  }
});
```

### 4. Progress Tracking

```html
<h1 data-scroll data-scroll-id="hero-title">
  Hero Title
</h1>
```

```javascript
scroll.on('scroll', (args) => {
  if (args.currentElements['hero-title']) {
    const progress = args.currentElements['hero-title'].progress;
    // progress ranges from 0 to 1
  }
});
```

### 5. Programmatic Scrolling

```javascript
// Scroll to top
scroll.scrollTo('top');

// Scroll to element
scroll.scrollTo('#section');

// Scroll with options
scroll.scrollTo('#section', {
  offset: -100,
  duration: 1000,
  callback: () => console.log('Done!')
});
```

## Performance Optimization

### Use data-scroll-section

Segment long pages into sections for better performance:

```html
<div data-scroll-container>
  <div data-scroll-section>Section 1</div>
  <div data-scroll-section>Section 2</div>
  <div data-scroll-section>Section 3</div>
</div>
```

### Update on Resize

The template includes resize handling:

```javascript
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => scroll.update(), 250);
});
```

### Cleanup

Always destroy the scroll instance:

```javascript
window.addEventListener('beforeunload', () => {
  scroll.destroy();
});
```

## Mobile Optimization

The template includes mobile-specific settings:

```javascript
smartphone: {
  smooth: true,      // Enable/disable smooth scroll
  breakpoint: 768    // Breakpoint in pixels
},
tablet: {
  smooth: true,
  breakpoint: 1024
}
```

For best mobile performance, consider:
- Disabling smooth scroll on smartphones: `smooth: false`
- Reducing parallax speeds
- Limiting number of tracked elements

## Accessibility

The template includes:
- Semantic HTML structure
- Proper heading hierarchy
- Color contrast compliance
- Keyboard navigation support

Consider adding:
- `prefers-reduced-motion` detection
- Skip to content link
- ARIA labels where appropriate

## Next Steps

1. **Customize styles** - Edit `style.css` to match your design
2. **Add content** - Replace placeholder content in `index.html`
3. **Integrate GSAP** - See GSAP integration examples in skill references
4. **Add animations** - Use scroll events to trigger custom animations
5. **Optimize** - Test on real devices and optimize for performance

## Troubleshooting

### Fixed elements not working?

Place fixed elements outside the scroll container:

```html
<nav style="position: fixed;">Navigation</nav>

<div data-scroll-container>
  <!-- Content -->
</div>
```

### Scroll position not updating?

Call `update()` after DOM changes:

```javascript
addContent();
scroll.update();
```

### Accessibility concerns?

Provide option to disable smooth scroll:

```javascript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const scroll = new LocomotiveScroll({
  smooth: !prefersReducedMotion
});
```

## Resources

- [Locomotive Scroll GitHub](https://github.com/locomotivemtl/locomotive-scroll)
- [Official Documentation](https://locomotivemtl.github.io/locomotive-scroll/)
- [CodePen Examples](https://codepen.io/tag/locomotive-scroll)

## License

This starter template is free to use for any purpose.



===== FILE: plugins/individual/locomotive-scroll/skills/locomotive-scroll/assets/starter_locomotive/index.html =====

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Locomotive Scroll Starter</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/locomotive-scroll@4/dist/locomotive-scroll.min.css">
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <!-- Fixed Navigation (outside scroll container) -->
  <nav class="nav">
    <div class="nav-container">
      <a href="#" class="logo">Locomotive</a>
      <div class="nav-links">
        <a href="#hero">Home</a>
        <a href="#parallax">Parallax</a>
        <a href="#sticky">Sticky</a>
        <a href="#horizontal">Horizontal</a>
      </div>
    </div>
  </nav>

  <!-- Scroll Container -->
  <div data-scroll-container>

    <!-- Hero Section -->
    <section data-scroll-section class="hero" id="hero">
      <h1 data-scroll data-scroll-speed="2" data-scroll-id="hero-title">
        Locomotive Scroll
      </h1>
      <p data-scroll data-scroll-speed="1" data-scroll-delay="0.1">
        Premium smooth scrolling experience
      </p>
      <div data-scroll data-scroll-speed="0.5" class="hero-bg"></div>
    </section>

    <!-- Parallax Section -->
    <section data-scroll-section class="parallax-section" id="parallax">
      <h2 data-scroll data-scroll-speed="1">Parallax Effects</h2>

      <div class="parallax-container">
        <!-- Background layer (slow) -->
        <div
          data-scroll
          data-scroll-speed="0.5"
          class="parallax-layer layer-bg"
        >
          Background Layer
        </div>

        <!-- Middle layer (normal) -->
        <div
          data-scroll
          data-scroll-speed="1"
          class="parallax-layer layer-mid"
        >
          Middle Layer
        </div>

        <!-- Foreground layer (fast) -->
        <div
          data-scroll
          data-scroll-speed="3"
          class="parallax-layer layer-fg"
        >
          Foreground Layer
        </div>

        <!-- Reverse parallax -->
        <div
          data-scroll
          data-scroll-speed="-2"
          class="parallax-layer layer-reverse"
        >
          Reverse Layer
        </div>
      </div>
    </section>

    <!-- Sticky Section -->
    <section data-scroll-section class="sticky-section" id="sticky">
      <h2 data-scroll>Sticky Elements</h2>

      <div class="sticky-container">
        <div
          data-scroll
          data-scroll-sticky
          data-scroll-target=".sticky-container"
          class="sticky-element"
        >
          <h3>I'm Sticky!</h3>
          <p>I stick while the section scrolls</p>
        </div>

        <div class="sticky-content">
          <p data-scroll>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
          <p data-scroll>Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
          <p data-scroll>Ut enim ad minim veniam, quis nostrud exercitation ullamco.</p>
          <p data-scroll>Duis aute irure dolor in reprehenderit in voluptate velit esse.</p>
        </div>
      </div>
    </section>

    <!-- Horizontal Scroll Section (requires JavaScript setup) -->
    <section data-scroll-section class="horizontal-section" id="horizontal">
      <h2 data-scroll>Scroll-Triggered Elements</h2>

      <div class="grid">
        <div
          data-scroll
          data-scroll-call="fadeIn"
          data-scroll-repeat
          class="card"
        >
          <h3>Card 1</h3>
          <p>Triggers callback on scroll</p>
        </div>

        <div
          data-scroll
          data-scroll-offset="20%"
          class="card"
        >
          <h3>Card 2</h3>
          <p>Custom trigger offset</p>
        </div>

        <div
          data-scroll
          data-scroll-class="is-visible"
          class="card"
        >
          <h3>Card 3</h3>
          <p>Custom in-view class</p>
        </div>

        <div
          data-scroll
          data-scroll-id="special-card"
          class="card"
        >
          <h3>Card 4</h3>
          <p>Tracked by JavaScript</p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer data-scroll-section class="footer">
      <p data-scroll>© 2025 Locomotive Scroll Starter</p>
      <p data-scroll data-scroll-speed="2">Built with Locomotive Scroll</p>
    </footer>

  </div>

  <script type="module" src="main.js"></script>
</body>
</html>

```


===== FILE: plugins/individual/locomotive-scroll/skills/locomotive-scroll/assets/starter_locomotive/main.js =====

```js
/**
 * Locomotive Scroll Starter - Main JavaScript
 *
 * This file initializes Locomotive Scroll and demonstrates:
 * - Basic smooth scrolling
 * - Scroll event handling
 * - Call events
 * - Progress tracking
 * - Programmatic scrolling
 */

import LocomotiveScroll from 'https://cdn.skypack.dev/locomotive-scroll@4';

// Initialize Locomotive Scroll
const scroll = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true,
  lerp: 0.1,          // Smoothness (0-1, lower = smoother)
  multiplier: 1,      // Speed multiplier
  class: 'is-inview', // Class added to visible elements
  repeat: true,       // Repeat in-view detection
  offset: ['10%', 0], // Global offset [bottom, top]
  getSpeed: true,     // Track scroll speed
  getDirection: true, // Track scroll direction

  // Tablet settings
  tablet: {
    smooth: true,
    breakpoint: 1024
  },

  // Smartphone settings
  smartphone: {
    smooth: true,
    breakpoint: 768
  }
});

// Update on window resize
let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    scroll.update();
  }, 250);
});

// Scroll event - Fires on every scroll update
scroll.on('scroll', (args) => {
  // Current scroll position
  const scrollY = args.scroll.y;

  // Scroll speed and direction
  const speed = args.speed;
  const direction = args.direction; // 'up', 'down', 'left', 'right'

  // Log scroll info (remove in production)
  // console.log('Scroll Y:', scrollY, 'Speed:', speed, 'Direction:', direction);

  // Track specific element progress
  if (args.currentElements['hero-title']) {
    const progress = args.currentElements['hero-title'].progress;
    // Use progress (0 to 1) for custom animations
    // console.log('Hero title progress:', progress);
  }

  // Track special card
  if (args.currentElements['special-card']) {
    const el = args.currentElements['special-card'];
    // console.log('Special card in view:', el.inView);
  }
});

// Call event - Fires when elements with data-scroll-call enter/exit viewport
scroll.on('call', (func, way, obj) => {
  console.log(`Call event: ${func} - ${way}`);

  // Handle specific callbacks
  if (func === 'fadeIn') {
    if (way === 'enter') {
      console.log('Element entered viewport:', obj.el);
      obj.el.style.opacity = '1';
    } else if (way === 'exit') {
      console.log('Element exited viewport:', obj.el);
    }
  }
});

// Smooth scroll to section on nav click
document.querySelectorAll('.nav-links a').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const target = link.getAttribute('href');

    if (target === '#hero') {
      scroll.scrollTo('top');
    } else {
      scroll.scrollTo(target, {
        offset: -80,      // Offset for fixed nav
        duration: 1000,   // Duration in ms
        easing: [0.25, 0.0, 0.35, 1.0] // Cubic bezier
      });
    }
  });
});

// Example: Programmatic scrolling
// Uncomment to test scrolling to specific elements
/*
setTimeout(() => {
  // Scroll to parallax section after 3 seconds
  scroll.scrollTo('#parallax', {
    offset: -100,
    duration: 2000,
    callback: () => console.log('Scrolled to parallax section!')
  });
}, 3000);
*/

// Example: Stop/Start scrolling
/*
// Stop scrolling
scroll.stop();

// Resume scrolling
setTimeout(() => {
  scroll.start();
}, 2000);
*/

// Example: Set scroll position directly (no animation)
/*
scroll.setScroll(0, 500); // x, y
*/

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  scroll.destroy();
});

// Log initialization
console.log('Locomotive Scroll initialized');
console.log('Scroll instance:', scroll);

// Export for debugging
window.locomotiveScroll = scroll;

```


===== FILE: plugins/individual/locomotive-scroll/skills/locomotive-scroll/assets/starter_locomotive/package.json =====

```json
{
  "name": "locomotive-scroll-starter",
  "version": "1.0.0",
  "description": "Locomotive Scroll starter template with examples",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "locomotive-scroll": "^4.1.4"
  },
  "devDependencies": {
    "vite": "^5.0.0"
  }
}

```


===== FILE: plugins/individual/locomotive-scroll/skills/locomotive-scroll/assets/starter_locomotive/style.css =====

```css
/* Reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  color: #333;
  line-height: 1.6;
  overflow-x: hidden;
}

/* Fixed Navigation */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
  color: #333;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-links a {
  text-decoration: none;
  color: #666;
  transition: color 0.3s;
}

.nav-links a:hover {
  color: #333;
}

/* Scroll Container */
[data-scroll-container] {
  padding-top: 60px; /* Account for fixed nav */
}

/* Sections */
section {
  min-height: 100vh;
  padding: 4rem 2rem;
}

h1, h2, h3 {
  margin-bottom: 1rem;
}

/* Hero Section */
.hero {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  overflow: hidden;
}

.hero h1 {
  font-size: clamp(3rem, 10vw, 6rem);
  font-weight: bold;
  margin-bottom: 1rem;
}

.hero p {
  font-size: clamp(1.2rem, 3vw, 1.8rem);
  opacity: 0.9;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at center, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

/* Parallax Section */
.parallax-section {
  background: #f8f9fa;
  position: relative;
}

.parallax-section h2 {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 3rem;
}

.parallax-container {
  position: relative;
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.parallax-layer {
  padding: 2rem 3rem;
  border-radius: 12px;
  font-size: 1.2rem;
  font-weight: 600;
  text-align: center;
  margin: 1rem;
}

.layer-bg {
  background: rgba(102, 126, 234, 0.2);
  color: #667eea;
}

.layer-mid {
  background: rgba(118, 75, 162, 0.2);
  color: #764ba2;
}

.layer-fg {
  background: rgba(237, 100, 166, 0.2);
  color: #ed64a6;
}

.layer-reverse {
  background: rgba(56, 178, 172, 0.2);
  color: #38b2ac;
}

/* Sticky Section */
.sticky-section {
  background: white;
}

.sticky-section h2 {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 3rem;
}

.sticky-container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 4rem;
  align-items: start;
}

.sticky-element {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3rem 2rem;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.sticky-element h3 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.sticky-content p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s, transform 0.6s;
}

.sticky-content p.is-inview {
  opacity: 1;
  transform: translateY(0);
}

/* Horizontal Section */
.horizontal-section {
  background: #f8f9fa;
}

.horizontal-section h2 {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 3rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  opacity: 0;
  transform: translateY(50px);
  transition: opacity 0.6s, transform 0.6s;
}

.card.is-inview,
.card.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.card h3 {
  color: #667eea;
  margin-bottom: 0.5rem;
}

/* Footer */
.footer {
  background: #333;
  color: white;
  text-align: center;
  min-height: auto;
  padding: 3rem 2rem;
}

.footer p {
  margin-bottom: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .sticky-container {
    grid-template-columns: 1fr;
  }

  .nav-links {
    gap: 1rem;
    font-size: 0.9rem;
  }

  .parallax-container {
    flex-direction: column;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}

/* Loading State */
html.has-scroll-smooth {
  overflow: hidden;
}

html.has-scroll-dragging {
  user-select: none;
}

/* Scrollbar Customization */
.c-scrollbar {
  position: absolute;
  right: 0;
  top: 0;
  width: 11px;
  height: 100%;
  transform-origin: center right;
  transition: transform 0.3s, opacity 0.3s;
  opacity: 0;
}

.c-scrollbar:hover {
  transform: scaleX(1.45);
}

.c-scrollbar:hover,
.has-scroll-scrolling .c-scrollbar,
.has-scroll-dragging .c-scrollbar {
  opacity: 1;
}

.c-scrollbar_thumb {
  position: absolute;
  top: 0;
  right: 0;
  background-color: #667eea;
  opacity: 0.5;
  width: 7px;
  border-radius: 10px;
  margin: 2px;
  cursor: grab;
}

.has-scroll-dragging .c-scrollbar_thumb {
  cursor: grabbing;
}

```


# Skill: barba-js


===== FILE: plugins/individual/barba-js/skills/barba-js/SKILL.md =====

---
name: barba-js
description: Page transitions library for creating fluid, smooth transitions between website pages. Use this skill when implementing page transitions, creating SPA-like experiences, adding animated route changes, or building websites with smooth navigation. Triggers on tasks involving Barba.js, page transitions, routing, view management, transition hooks, GSAP integration, or smooth page navigation. Works with gsap-scrolltrigger for transition animations.
---

# Barba.js

Modern page transition library for creating fluid, smooth transitions between website pages. Barba.js makes multi-page websites feel like Single Page Applications (SPAs) by hijacking navigation and managing transitions without full page reloads.

## Overview

Barba.js is a lightweight (7kb minified and compressed) JavaScript library that intercepts navigation between pages, fetches new content via AJAX, and smoothly transitions between old and new containers. It reduces page load delays and HTTP requests while maintaining the benefits of traditional multi-page architecture.

**Core Features**:
- Smooth page transitions without full reloads
- Lifecycle hooks for precise control over transition phases
- View-based logic for page-specific behaviors
- Built-in routing with @barba/router plugin
- Extensible plugin system
- Small footprint and high performance
- Framework-agnostic (works with vanilla JS, GSAP, anime.js, etc.)

## Core Concepts

### 1. Wrapper, Container, and Namespace

Barba.js uses a specific DOM structure to manage transitions:

**HTML Structure**:
```html
<body data-barba="wrapper">
  <!-- Static elements (header, nav) stay outside container -->
  <header>
    <nav>
      <a href="/">Home</a>
      <a href="/about">About</a>
    </nav>
  </header>

  <!-- Dynamic content goes in container -->
  <main data-barba="container" data-barba-namespace="home">
    <!-- This content changes on navigation -->
    <h1>Home Page</h1>
    <p>Content that will transition out...</p>
  </main>

  <!-- Static footer outside container -->
  <footer>© 2025</footer>
</body>
```

**Three Key Elements**:

1. **Wrapper** (`data-barba="wrapper"`)
   - Outermost container
   - Everything inside wrapper but outside container stays persistent
   - Ideal for headers, navigation, footers that don't change

2. **Container** (`data-barba="container"`)
   - Dynamic content area that updates on navigation
   - Only this section gets replaced during transitions
   - Must exist on every page

3. **Namespace** (`data-barba-namespace="home"`)
   - Unique identifier for each page type
   - Used in transition rules and view logic
   - Examples: "home", "about", "product", "blog-post"

### 2. Transition Lifecycle

Barba.js follows a precise lifecycle for each navigation:

**Default Async Flow**:
1. User clicks link
2. Barba intercepts navigation
3. Prefetch next page (via AJAX)
4. Cache new content
5. **Leave hook** - Animate current page out
6. Wait for leave animation to complete
7. Remove old container, insert new container
8. **Enter hook** - Animate new page in
9. Wait for enter animation to complete
10. Update browser history

**Sync Flow** (with `sync: true`):
1. User clicks link
2. Barba intercepts navigation
3. Prefetch next page
4. Wait for new page to load
5. **Leave and Enter hooks run simultaneously** (crossfade effect)
6. Swap containers
7. Update browser history

### 3. Hooks

Barba provides 11 lifecycle hooks for controlling transitions:

**Hook Execution Order**:
```
Initial page load:
  beforeOnce → once → afterOnce

Every navigation:
  before → beforeLeave → leave → afterLeave →
  beforeEnter → enter → afterEnter → after
```

**Hook Types**:
- **Global hooks**: Run on every transition (`barba.hooks.before()`)
- **Transition hooks**: Defined within specific transition objects
- **View hooks**: Defined within view objects for page-specific logic

**Common Hook Use Cases**:
- `beforeLeave` - Reset scroll position, prepare animations
- `leave` - Animate current page out
- `afterLeave` - Clean up old page
- `beforeEnter` - Prepare new page (hide elements, set initial states)
- `enter` - Animate new page in
- `afterEnter` - Initialize page scripts, analytics tracking

### 4. Views

Views are page-specific logic containers that run based on namespace:

```javascript
barba.init({
  views: [{
    namespace: 'home',
    beforeEnter() {
      // Home-specific setup
      console.log('Entering home page');
    },
    afterEnter() {
      // Initialize home page features
      initHomeSlider();
    }
  }, {
    namespace: 'product',
    beforeEnter() {
      console.log('Entering product page');
    },
    afterEnter() {
      initProductGallery();
    }
  }]
});
```

## Common Patterns

### 1. Basic Setup

**Installation**:
```bash
npm install --save-dev @barba/core
# or
yarn add @barba/core --dev
```

**Minimal Configuration**:
```javascript
import barba from '@barba/core';

barba.init({
  transitions: [{
    name: 'default',
    leave({ current }) {
      // Fade out current page
      return gsap.to(current.container, {
        opacity: 0,
        duration: 0.5
      });
    },
    enter({ next }) {
      // Fade in new page
      return gsap.from(next.container, {
        opacity: 0,
        duration: 0.5
      });
    }
  }]
});
```

### 2. Fade Transition (Async)

Classic fade-out, fade-in transition:

```javascript
import barba from '@barba/core';
import gsap from 'gsap';

barba.init({
  transitions: [{
    name: 'fade',
    async leave({ current }) {
      await gsap.to(current.container, {
        opacity: 0,
        duration: 0.5,
        ease: 'power2.inOut'
      });
    },
    async enter({ next }) {
      // Start invisible
      gsap.set(next.container, { opacity: 0 });

      // Fade in
      await gsap.to(next.container, {
        opacity: 1,
        duration: 0.5,
        ease: 'power2.inOut'
      });
    }
  }]
});
```

### 3. Crossfade Transition (Sync)

Simultaneous fade between pages:

```javascript
barba.init({
  transitions: [{
    name: 'crossfade',
    sync: true, // Enable sync mode
    leave({ current }) {
      return gsap.to(current.container, {
        opacity: 0,
        duration: 0.8,
        ease: 'power2.inOut'
      });
    },
    enter({ next }) {
      return gsap.from(next.container, {
        opacity: 0,
        duration: 0.8,
        ease: 'power2.inOut'
      });
    }
  }]
});
```

### 4. Slide Transition with Overlap

Slide old page out, new page in with overlap:

```javascript
barba.init({
  transitions: [{
    name: 'slide',
    sync: true,
    leave({ current }) {
      return gsap.to(current.container, {
        x: '-100%',
        duration: 0.7,
        ease: 'power3.inOut'
      });
    },
    enter({ next }) {
      // Start off-screen right
      gsap.set(next.container, { x: '100%' });

      // Slide in from right
      return gsap.to(next.container, {
        x: '0%',
        duration: 0.7,
        ease: 'power3.inOut'
      });
    }
  }]
});
```

### 5. Transition Rules (Conditional Transitions)

Define different transitions based on navigation context:

```javascript
barba.init({
  transitions: [
    // Home to any page: fade
    {
      name: 'from-home-fade',
      from: { namespace: 'home' },
      leave({ current }) {
        return gsap.to(current.container, {
          opacity: 0,
          duration: 0.5
        });
      },
      enter({ next }) {
        return gsap.from(next.container, {
          opacity: 0,
          duration: 0.5
        });
      }
    },
    // Product to product: slide left
    {
      name: 'product-to-product',
      from: { namespace: 'product' },
      to: { namespace: 'product' },
      leave({ current }) {
        return gsap.to(current.container, {
          x: '-100%',
          duration: 0.6
        });
      },
      enter({ next }) {
        gsap.set(next.container, { x: '100%' });
        return gsap.to(next.container, {
          x: '0%',
          duration: 0.6
        });
      }
    },
    // Default fallback
    {
      name: 'default',
      leave({ current }) {
        return gsap.to(current.container, {
          opacity: 0,
          duration: 0.3
        });
      },
      enter({ next }) {
        return gsap.from(next.container, {
          opacity: 0,
          duration: 0.3
        });
      }
    }
  ]
});
```

### 6. Router Plugin for Route-Based Transitions

Use `@barba/router` for route-specific transitions:

**Installation**:
```bash
npm install --save-dev @barba/router
```

**Usage**:
```javascript
import barba from '@barba/core';
import barbaPrefetch from '@barba/prefetch';
import barbaRouter from '@barba/router';

// Define routes
barbaRouter.init({
  routes: [
    { path: '/', name: 'home' },
    { path: '/about', name: 'about' },
    { path: '/products/:id', name: 'product' }, // Dynamic segment
    { path: '/blog/:category/:slug', name: 'blog-post' }
  ]
});

barba.use(barbaRouter);
barba.use(barbaPrefetch); // Optional: prefetch on hover

barba.init({
  transitions: [{
    name: 'product-transition',
    to: { route: 'product' }, // Trigger on route name
    leave({ current }) {
      return gsap.to(current.container, {
        scale: 0.95,
        opacity: 0,
        duration: 0.5
      });
    },
    enter({ next }) {
      return gsap.from(next.container, {
        scale: 1.05,
        opacity: 0,
        duration: 0.5
      });
    }
  }]
});
```

### 7. Loading Indicator

Show loading state during page fetch:

```javascript
barba.init({
  transitions: [{
    async leave({ current }) {
      // Show loader
      const loader = document.querySelector('.loader');
      gsap.set(loader, { display: 'flex', opacity: 0 });
      gsap.to(loader, { opacity: 1, duration: 0.3 });

      // Fade out page
      await gsap.to(current.container, {
        opacity: 0,
        duration: 0.5
      });
    },
    async enter({ next }) {
      // Hide loader
      const loader = document.querySelector('.loader');
      await gsap.to(loader, { opacity: 0, duration: 0.3 });
      gsap.set(loader, { display: 'none' });

      // Fade in page
      await gsap.from(next.container, {
        opacity: 0,
        duration: 0.5
      });
    }
  }]
});
```

## Integration Patterns

### GSAP Integration

Barba.js works seamlessly with GSAP for animations:

**Timeline-Based Transitions**:
```javascript
import barba from '@barba/core';
import gsap from 'gsap';

barba.init({
  transitions: [{
    async leave({ current }) {
      const tl = gsap.timeline();

      tl.to(current.container.querySelector('h1'), {
        y: -50,
        opacity: 0,
        duration: 0.3
      })
      .to(current.container.querySelector('.content'), {
        y: -30,
        opacity: 0,
        duration: 0.3
      }, '-=0.2')
      .to(current.container, {
        opacity: 0,
        duration: 0.2
      });

      await tl.play();
    },
    async enter({ next }) {
      const tl = gsap.timeline();

      // Set initial states
      gsap.set(next.container, { opacity: 0 });
      gsap.set(next.container.querySelector('h1'), { y: 50, opacity: 0 });
      gsap.set(next.container.querySelector('.content'), { y: 30, opacity: 0 });

      tl.to(next.container, {
        opacity: 1,
        duration: 0.2
      })
      .to(next.container.querySelector('h1'), {
        y: 0,
        opacity: 1,
        duration: 0.5,
        ease: 'power3.out'
      })
      .to(next.container.querySelector('.content'), {
        y: 0,
        opacity: 1,
        duration: 0.5,
        ease: 'power3.out'
      }, '-=0.3');

      await tl.play();
    }
  }]
});
```

**Reference gsap-scrolltrigger skill** for advanced GSAP integration patterns.

### View-Specific Initialization

Initialize libraries or scripts per page:

```javascript
barba.init({
  views: [
    {
      namespace: 'home',
      afterEnter() {
        // Initialize home page features
        initHomepageSlider();
        initParallaxEffects();
      },
      beforeLeave() {
        // Clean up
        destroyHomepageSlider();
      }
    },
    {
      namespace: 'gallery',
      afterEnter() {
        initLightbox();
        initMasonry();
      },
      beforeLeave() {
        destroyLightbox();
      }
    }
  ]
});
```

### Analytics Tracking

Track page views on navigation:

```javascript
barba.hooks.after(() => {
  // Google Analytics
  if (typeof gtag !== 'undefined') {
    gtag('config', 'GA_MEASUREMENT_ID', {
      page_path: window.location.pathname
    });
  }

  // Or use data layer
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: 'pageview',
    page: window.location.pathname
  });
});
```

### Third-Party Script Re-Initialization

Re-run scripts after page transitions:

```javascript
barba.hooks.after(() => {
  // Re-initialize third-party widgets
  if (typeof twttr !== 'undefined') {
    twttr.widgets.load(); // Twitter widgets
  }

  if (typeof FB !== 'undefined') {
    FB.XFBML.parse(); // Facebook widgets
  }

  // Re-run syntax highlighting
  if (typeof Prism !== 'undefined') {
    Prism.highlightAll();
  }
});
```

## Performance Optimization

### 1. Prefetching

Use `@barba/prefetch` to load pages on hover:

```bash
npm install --save-dev @barba/prefetch
```

```javascript
import barba from '@barba/core';
import barbaPrefetch from '@barba/prefetch';

barba.use(barbaPrefetch);

barba.init({
  // Prefetch fires on link hover by default
  prefetch: {
    root: null, // Observe all links
    timeout: 3000 // Cache timeout in ms
  }
});
```

### 2. Prevent Layout Shift

Set container min-height to prevent content jump:

```css
[data-barba="container"] {
  min-height: 100vh;
  /* Or use viewport height minus header/footer */
  min-height: calc(100vh - 80px - 60px);
}
```

### 3. Optimize Animations

Use GPU-accelerated properties:

```javascript
// ✅ Good - GPU accelerated
gsap.to(element, {
  opacity: 0,
  x: -100,
  scale: 0.9,
  rotation: 45
});

// ❌ Avoid - causes reflow/repaint
gsap.to(element, {
  width: '50%',
  height: '300px',
  top: '100px'
});
```

### 4. Clean Up Event Listeners

Remove listeners in `beforeLeave` or view hooks:

```javascript
barba.init({
  views: [{
    namespace: 'home',
    afterEnter() {
      // Add listeners
      this.clickHandler = () => console.log('clicked');
      document.querySelector('.btn').addEventListener('click', this.clickHandler);
    },
    beforeLeave() {
      // Remove listeners
      document.querySelector('.btn').removeEventListener('click', this.clickHandler);
    }
  }]
});
```

### 5. Lazy Load Images

Defer image loading until after transition:

```javascript
barba.init({
  transitions: [{
    async enter({ next }) {
      // Complete transition first
      await gsap.from(next.container, {
        opacity: 0,
        duration: 0.5
      });

      // Then load images
      const images = next.container.querySelectorAll('img[data-src]');
      images.forEach(img => {
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
      });
    }
  }]
});
```

## Common Pitfalls

### 1. Forgetting to Return Promises

**Problem**: Transitions complete instantly without waiting for animations.

**Solution**: Always return promises or use `async/await`:

```javascript
// ❌ Wrong - animation starts but doesn't wait
leave({ current }) {
  gsap.to(current.container, { opacity: 0, duration: 0.5 });
}

// ✅ Correct - returns promise
leave({ current }) {
  return gsap.to(current.container, { opacity: 0, duration: 0.5 });
}

// ✅ Also correct - async/await
async leave({ current }) {
  await gsap.to(current.container, { opacity: 0, duration: 0.5 });
}
```

### 2. Not Preventing Default Link Behavior

**Problem**: Some links cause full page reloads.

**Solution**: Barba automatically prevents default on internal links, but you may need to exclude external links:

```javascript
barba.init({
  prevent: ({ href }) => {
    // Allow external links
    if (href.indexOf('http') > -1 && href.indexOf(window.location.host) === -1) {
      return true;
    }
    return false;
  }
});
```

### 3. CSS Conflicts Between Pages

**Problem**: Old page CSS affects new page layout during transition.

**Solution**: Use namespace-specific CSS or reset styles:

```css
/* Namespace-specific styles */
[data-barba-namespace="home"] .hero {
  background: blue;
}

[data-barba-namespace="about"] .hero {
  background: red;
}
```

Or reset in `beforeEnter`:

```javascript
beforeEnter({ next }) {
  // Reset scroll position
  window.scrollTo(0, 0);

  // Reset any global state
  document.body.classList.remove('menu-open');
}
```

### 4. Not Updating Document Title and Meta Tags

**Problem**: Page title and meta tags don't update on navigation.

**Solution**: Use `@barba/head` plugin or update manually:

```bash
npm install --save-dev @barba/head
```

```javascript
import barba from '@barba/core';
import barbaHead from '@barba/head';

barba.use(barbaHead);

barba.init({
  // Head plugin automatically updates <head> tags
});
```

Or manually:

```javascript
barba.hooks.after(({ next }) => {
  // Update title
  document.title = next.html.querySelector('title').textContent;

  // Update meta tags
  const newMeta = next.html.querySelectorAll('meta');
  newMeta.forEach(meta => {
    const name = meta.getAttribute('name') || meta.getAttribute('property');
    if (name) {
      const existing = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
      if (existing) {
        existing.setAttribute('content', meta.getAttribute('content'));
      }
    }
  });
});
```

### 5. Animation Flicker on Enter

**Problem**: New page flashes visible before enter animation starts.

**Solution**: Set initial invisible state in CSS or `beforeEnter`:

```css
/* CSS approach */
[data-barba="container"] {
  opacity: 0;
}

[data-barba="container"].is-visible {
  opacity: 1;
}
```

```javascript
// JavaScript approach
beforeEnter({ next }) {
  gsap.set(next.container, { opacity: 0 });
}
```

### 6. Sync Transitions Without Proper Positioning

**Problem**: Sync transitions cause layout shift as containers stack.

**Solution**: Position containers absolutely during transition:

```css
[data-barba="wrapper"] {
  position: relative;
}

[data-barba="container"] {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}
```

Or manage in JavaScript:

```javascript
barba.init({
  transitions: [{
    sync: true,
    beforeLeave({ current }) {
      gsap.set(current.container, {
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%'
      });
    }
  }]
});
```

## Resources

This skill includes:

### scripts/
Executable utilities for common Barba.js tasks:
- `transition_generator.py` - Generate transition boilerplate code
- `project_setup.py` - Initialize Barba.js project structure

### references/
Detailed documentation:
- `api_reference.md` - Complete Barba.js API (hooks, transitions, views, router)
- `hooks_guide.md` - All 11 hooks with execution order and use cases
- `gsap_integration.md` - GSAP animation patterns for Barba transitions
- `transition_patterns.md` - Common transition implementations

### assets/
Templates and starter projects:
- `starter_barba/` - Complete Barba.js + GSAP starter template
- `examples/` - Real-world transition implementations

## Related Skills

- **gsap-scrolltrigger** - For advanced GSAP animations in transitions
- **locomotive-scroll** - Can be combined with Barba for smooth scrolling between pages
- **motion-framer** - Alternative approach for React-based page transitions



===== FILE: plugins/individual/barba-js/skills/barba-js/references/api_reference.md =====

# Barba.js API Reference

Complete reference for Barba.js core API, plugins, and configuration options.

## Table of Contents

- [Core API](#core-api)
  - [barba.init()](#barbainit)
  - [barba.go()](#barbago)
  - [barba.hooks](#barbahooks)
  - [barba.history](#barbahistory)
  - [barba.url](#barbaurl)
  - [barba.use()](#barbause)
- [Transitions](#transitions)
- [Views](#views)
- [Hooks](#hooks)
- [Data Object](#data-object)
- [Router Plugin](#router-plugin)
- [Prefetch Plugin](#prefetch-plugin)
- [CSS Plugin](#css-plugin)
- [Head Plugin](#head-plugin)

---

## Core API

### barba.init()

Initialize Barba with configuration options.

**Syntax**:
```javascript
barba.init({
  debug: false,
  logLevel: 'off',
  timeout: 2000,
  cacheIgnore: false,
  preventRunning: true,
  prevent: null,
  requestError: null,
  schema: {
    prefix: 'data-barba',
    wrapper: 'wrapper',
    container: 'container',
    namespace: 'namespace'
  },
  transitions: [],
  views: []
});
```

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | `boolean` | `false` | Enable debug mode (logs to console) |
| `logLevel` | `string` | `'off'` | Logging level: `'off'`, `'error'`, `'warning'`, `'info'`, `'debug'` |
| `timeout` | `number` | `2000` | Request timeout in milliseconds |
| `cacheIgnore` | `boolean\|string\|function` | `false` | Disable cache, specific query string, or custom function |
| `preventRunning` | `boolean` | `true` | Prevent transitions if one is already running |
| `prevent` | `function` | `null` | Custom function to prevent Barba on specific links |
| `requestError` | `function` | `null` | Custom request error handler |
| `schema` | `object` | See above | Custom data attribute names |
| `transitions` | `array` | `[]` | Array of transition objects |
| `views` | `array` | `[]` | Array of view objects |

**Examples**:

```javascript
// Minimal setup
barba.init();

// Custom configuration
barba.init({
  debug: true,
  timeout: 5000,
  prevent: ({ el, href }) => {
    // Prevent external links
    return href.indexOf('http') > -1 && href.indexOf(window.location.host) === -1;
  },
  requestError: (trigger, action, url, response) => {
    // Redirect to 404 page
    if (action === 'click' && response.status === 404) {
      barba.go('/404');
    }
  }
});

// Custom schema (use different data attributes)
barba.init({
  schema: {
    prefix: 'data-custom',
    wrapper: 'page-wrapper',
    container: 'page-container',
    namespace: 'page-type'
  }
});
```

### barba.go()

Programmatically navigate to a URL.

**Syntax**:
```javascript
barba.go(href, trigger, event);
```

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `href` | `string` | - | Target URL (relative or absolute) |
| `trigger` | `string` | `'barba'` | Trigger identifier (appears in `data.trigger`) |
| `event` | `object` | `null` | Event object (appears in `data.event`) |

**Examples**:

```javascript
// Navigate to URL
barba.go('/about');

// Navigate with custom trigger
barba.go('/contact', 'custom-button');

// Navigate with event data
barba.go('/products/123', 'product-link', { productId: 123 });

// Conditional navigation
if (userLoggedIn) {
  barba.go('/dashboard');
} else {
  barba.go('/login');
}
```

### barba.hooks

Global hooks object for registering lifecycle hooks.

**Available Hooks**:

All hooks receive a `data` object as parameter:

```javascript
barba.hooks.beforeOnce(data => { /* ... */ });
barba.hooks.once(data => { /* ... */ });
barba.hooks.afterOnce(data => { /* ... */ });
barba.hooks.before(data => { /* ... */ });
barba.hooks.beforeLeave(data => { /* ... */ });
barba.hooks.leave(data => { /* ... */ });
barba.hooks.afterLeave(data => { /* ... */ });
barba.hooks.beforeEnter(data => { /* ... */ });
barba.hooks.enter(data => { /* ... */ });
barba.hooks.afterEnter(data => { /* ... */ });
barba.hooks.after(data => { /* ... */ });
```

**Examples**:

```javascript
// Reset scroll on every transition
barba.hooks.beforeEnter(() => {
  window.scrollTo(0, 0);
});

// Track page views
barba.hooks.after(({ next }) => {
  gtag('config', 'GA_MEASUREMENT_ID', {
    page_path: next.url.path
  });
});

// Show/hide loading indicator
barba.hooks.before(() => {
  document.querySelector('.loader').classList.add('active');
});

barba.hooks.after(() => {
  document.querySelector('.loader').classList.remove('active');
});

// Re-initialize scripts
barba.hooks.afterEnter(() => {
  if (typeof Prism !== 'undefined') {
    Prism.highlightAll();
  }
});
```

### barba.history

Access browser history and navigation state.

**Properties**:

| Property | Type | Description |
|----------|------|-------------|
| `previous` | `object` | Previous page data |
| `current` | `object` | Current page data |
| `size` | `number` | Number of items in history |
| `direction` | `string` | Navigation direction: `'forward'`, `'back'`, or `null` |

**Methods**:

| Method | Description |
|--------|-------------|
| `add(url, trigger)` | Add entry to history |
| `cancel()` | Cancel current transition |

**Examples**:

```javascript
// Check navigation direction
barba.hooks.before(({ current, next }) => {
  const direction = barba.history.direction;

  if (direction === 'back') {
    console.log('User went back');
  } else if (direction === 'forward') {
    console.log('User went forward');
  } else {
    console.log('Normal navigation');
  }
});

// Access previous page
const previousUrl = barba.history.previous.url.href;
const previousNamespace = barba.history.previous.namespace;

// Cancel transition programmatically
if (someCondition) {
  barba.history.cancel();
}
```

### barba.url

URL manipulation utilities.

**Methods**:

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `getAbsoluteHref(href)` | `string` | `string` | Convert relative URL to absolute |
| `getHref(url)` | `string` | `string` | Get clean href (without hash) |
| `getOrigin(url)` | `string` | `string` | Get origin from URL |
| `getPath(url)` | `string` | `string` | Get path from URL |
| `getPathname(url)` | `string` | `string` | Get pathname from URL |
| `getPort(url)` | `string` | `string` | Get port from URL |

**Examples**:

```javascript
// Get absolute URL
const absolute = barba.url.getAbsoluteHref('/about');
// Returns: "https://example.com/about"

// Get path without query/hash
const path = barba.url.getPath('/products?id=123#details');
// Returns: "/products"

// Get pathname
const pathname = barba.url.getPathname('https://example.com/blog/post-1');
// Returns: "/blog/post-1"
```

### barba.use()

Register Barba plugins.

**Syntax**:
```javascript
barba.use(plugin, options);
```

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `plugin` | `object` | Plugin object with `install()` method |
| `options` | `object` | Plugin-specific options |

**Examples**:

```javascript
import barba from '@barba/core';
import barbaRouter from '@barba/router';
import barbaPrefetch from '@barba/prefetch';
import barbaHead from '@barba/head';

// Register router
barba.use(barbaRouter, {
  routes: [
    { path: '/', name: 'home' },
    { path: '/about', name: 'about' }
  ]
});

// Register prefetch
barba.use(barbaPrefetch);

// Register head plugin
barba.use(barbaHead);

barba.init();
```

---

## Transitions

Transition objects define how pages animate during navigation.

**Transition Object Structure**:

```javascript
{
  name: 'transition-name',
  from: { /* rules */ },
  to: { /* rules */ },
  sync: false,
  once() { /* ... */ },
  leave() { /* ... */ },
  enter() { /* ... */ },
  // ... other hooks
}
```

**Properties**:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `name` | `string` | - | Unique transition identifier |
| `from` | `object` | - | Rules for leaving page |
| `to` | `object` | - | Rules for entering page |
| `sync` | `boolean` | `false` | Sync mode (play leave/enter simultaneously) |

**Rules**:

Rules determine when a transition applies:

```javascript
// Namespace rule
{ namespace: 'home' }
{ namespace: ['home', 'about'] }

// Route rule (requires @barba/router)
{ route: 'product' }

// Custom rule
{ custom: ({ current, next }) => current.namespace === next.namespace }
```

**Rule Priority** (highest to lowest):
1. `custom`
2. `route` (requires @barba/router)
3. `namespace`

**Transition Selection Examples**:

```javascript
barba.init({
  transitions: [
    // Only from home
    {
      name: 'from-home',
      from: { namespace: 'home' }
    },

    // Only to about
    {
      name: 'to-about',
      to: { namespace: 'about' }
    },

    // From home to about
    {
      name: 'home-to-about',
      from: { namespace: 'home' },
      to: { namespace: 'about' }
    },

    // Multiple namespaces
    {
      name: 'from-pages',
      from: { namespace: ['about', 'contact', 'services'] }
    },

    // Custom rule
    {
      name: 'same-namespace',
      custom: ({ current, next }) => current.namespace === next.namespace
    },

    // Always matches (fallback)
    {
      name: 'default'
    }
  ]
});
```

**Sync Mode**:

```javascript
// Async (default): leave → wait → swap → enter
{
  sync: false,
  async leave({ current }) {
    await gsap.to(current.container, { opacity: 0 });
  },
  async enter({ next }) {
    await gsap.from(next.container, { opacity: 0 });
  }
}

// Sync: wait → (leave + enter simultaneously) → swap
{
  sync: true,
  leave({ current }) {
    return gsap.to(current.container, { opacity: 0 });
  },
  enter({ next }) {
    return gsap.from(next.container, { opacity: 0 });
  }
}
```

---

## Views

View objects provide page-specific logic based on namespace.

**View Object Structure**:

```javascript
{
  namespace: 'page-namespace',
  beforeOnce() { /* ... */ },
  afterOnce() { /* ... */ },
  beforeLeave() { /* ... */ },
  afterLeave() { /* ... */ },
  beforeEnter() { /* ... */ },
  afterEnter() { /* ... */ }
}
```

**Properties**:

| Property | Type | Description |
|----------|------|-------------|
| `namespace` | `string` | Target namespace (matches `data-barba-namespace`) |

**Examples**:

```javascript
barba.init({
  views: [
    {
      namespace: 'home',
      beforeEnter() {
        console.log('About to enter home page');
      },
      afterEnter() {
        // Initialize home-specific features
        initHomeSlider();
        initParallax();
      },
      beforeLeave() {
        // Clean up
        destroyHomeSlider();
      }
    },
    {
      namespace: 'product',
      afterEnter({ next }) {
        // Get product ID from URL
        const productId = next.url.path.split('/').pop();
        loadProduct(productId);
      }
    },
    {
      namespace: 'gallery',
      afterEnter() {
        initMasonry();
        initLightbox();
      },
      beforeLeave() {
        destroyMasonry();
        destroyLightbox();
      }
    }
  ]
});
```

---

## Hooks

Complete reference for all 11 Barba.js hooks.

### Hook Execution Order

**Initial page load**:
```
beforeOnce → once → afterOnce
```

**Every navigation**:
```
before → beforeLeave → leave → afterLeave →
beforeEnter → enter → afterEnter → after
```

### Hook Contexts

Hooks can be defined in three places:

1. **Global hooks**: Run on every transition
   ```javascript
   barba.hooks.before(() => { /* ... */ });
   ```

2. **Transition hooks**: Run when that transition matches
   ```javascript
   barba.init({
     transitions: [{
       name: 'fade',
       leave() { /* ... */ }
     }]
   });
   ```

3. **View hooks**: Run for specific namespaces
   ```javascript
   barba.init({
     views: [{
       namespace: 'home',
       afterEnter() { /* ... */ }
     }]
   });
   ```

### Async Hooks

Hooks can be synchronous or asynchronous:

```javascript
// Synchronous
leave({ current }) {
  current.container.style.opacity = 0;
}

// Promise
leave({ current }) {
  return gsap.to(current.container, { opacity: 0 });
}

// Async/await
async leave({ current }) {
  await gsap.to(current.container, { opacity: 0 });
}

// Manual async with this.async()
leave({ current }) {
  const done = this.async();

  setTimeout(() => {
    gsap.to(current.container, { opacity: 0 });
    done();
  }, 500);
}
```

### Individual Hook Reference

#### beforeOnce

Runs once before initial page load (before `once` hook).

**Available in**: Transitions only
**When**: Before first page render
**Use for**: Initial setup, loading screens

```javascript
{
  beforeOnce() {
    console.log('Before initial page render');
    document.querySelector('.loader').classList.add('visible');
  }
}
```

#### once

Runs once on initial page load (animations for first view).

**Available in**: Transitions only
**When**: During first page render
**Use for**: Intro animations

```javascript
{
  async once({ next }) {
    await gsap.from(next.container, {
      opacity: 0,
      y: 50,
      duration: 1
    });
  }
}
```

#### afterOnce

Runs once after initial page load (after `once` hook).

**Available in**: Transitions only
**When**: After first page render completes
**Use for**: Post-intro initialization

```javascript
{
  afterOnce() {
    document.querySelector('.loader').classList.remove('visible');
    console.log('Initial page loaded');
  }
}
```

#### before

Runs before every transition starts.

**Available in**: Transitions only
**When**: Start of every navigation (except first load)
**Use for**: Pre-transition setup, loading indicators

```javascript
{
  before() {
    document.querySelector('.loader').classList.add('visible');
    console.log('Transition starting');
  }
}
```

#### beforeLeave

Runs before leaving current page.

**Available in**: Transitions and Views
**When**: Before leave animation
**Use for**: Preparing leave animation, resetting scroll

```javascript
{
  beforeLeave({ current }) {
    // Reset scroll
    window.scrollTo(0, 0);

    // Prepare elements
    gsap.set(current.container.querySelectorAll('.fade'), { opacity: 1 });
  }
}
```

#### leave

Main hook for animating current page out.

**Available in**: Transitions only
**When**: Current page exit animation
**Use for**: Exit animations

```javascript
{
  async leave({ current }) {
    await gsap.to(current.container, {
      opacity: 0,
      x: -100,
      duration: 0.5
    });
  }
}
```

#### afterLeave

Runs after leaving current page.

**Available in**: Transitions and Views
**When**: After leave animation completes
**Use for**: Cleanup, removing event listeners

```javascript
{
  afterLeave({ current }) {
    // Remove event listeners
    current.container.querySelectorAll('button').forEach(btn => {
      btn.removeEventListener('click', handleClick);
    });

    console.log('Left page:', current.namespace);
  }
}
```

#### beforeEnter

Runs before entering new page.

**Available in**: Transitions and Views
**When**: Before enter animation (after new container inserted)
**Use for**: Preparing enter animation, setting initial states

```javascript
{
  beforeEnter({ next }) {
    // Set initial state for enter animation
    gsap.set(next.container, { opacity: 0, x: 100 });

    // Prepare page-specific elements
    const images = next.container.querySelectorAll('img[data-src]');
    images.forEach(img => {
      img.src = img.dataset.src;
    });
  }
}
```

#### enter

Main hook for animating new page in.

**Available in**: Transitions only
**When**: New page entrance animation
**Use for**: Entrance animations

```javascript
{
  async enter({ next }) {
    await gsap.to(next.container, {
      opacity: 1,
      x: 0,
      duration: 0.5
    });
  }
}
```

#### afterEnter

Runs after entering new page.

**Available in**: Transitions and Views
**When**: After enter animation completes
**Use for**: Initializing page features, analytics

```javascript
{
  afterEnter({ next }) {
    // Initialize page features
    initSlider(next.container);

    // Track page view
    gtag('config', 'GA_ID', {
      page_path: next.url.path
    });

    console.log('Entered page:', next.namespace);
  }
}
```

#### after

Runs after every transition completes.

**Available in**: Transitions only
**When**: End of every navigation (except first load)
**Use for**: Final cleanup, hiding loading indicators

```javascript
{
  after() {
    document.querySelector('.loader').classList.remove('visible');
    console.log('Transition complete');
  }
}
```

---

## Data Object

All hooks receive a `data` object with information about current and next pages.

**Data Object Structure**:

```javascript
{
  current: {
    container: HTMLElement,
    html: string,
    namespace: string,
    url: { href, path, port, query }
  },
  next: {
    container: HTMLElement,
    html: string,
    namespace: string,
    url: { href, path, port, query }
  },
  trigger: string | HTMLElement,
  event: Event
}
```

**Properties**:

### current

Information about the page being left.

| Property | Type | Description |
|----------|------|-------------|
| `container` | `HTMLElement` | Current page's `data-barba="container"` element |
| `html` | `string` | Full HTML of current page |
| `namespace` | `string` | Current page namespace |
| `url` | `object` | URL information |
| `url.href` | `string` | Full URL |
| `url.path` | `string` | Path without query/hash |
| `url.port` | `string` | Port number |
| `url.query` | `object` | Query parameters as key-value pairs |

### next

Information about the page being entered.

Same structure as `current`.

### trigger

Source of the navigation.

| Value | Type | Description |
|-------|------|-------------|
| Link element | `HTMLElement` | User clicked a link |
| `'barba'` | `string` | Programmatic navigation via `barba.go()` |
| `'back'` | `string` | Browser back button |
| `'forward'` | `string` | Browser forward button |

### event

The triggering event object (if navigation was from user interaction).

**Usage Examples**:

```javascript
barba.hooks.before(({ current, next, trigger, event }) => {
  console.log('Leaving:', current.namespace);
  console.log('Entering:', next.namespace);
  console.log('Current URL:', current.url.href);
  console.log('Next URL:', next.url.href);
  console.log('Trigger:', trigger);

  // Check trigger type
  if (trigger === 'back') {
    console.log('User went back');
  } else if (trigger instanceof HTMLElement) {
    console.log('User clicked:', trigger.href);
  }

  // Access query parameters
  if (next.url.query.id) {
    console.log('Product ID:', next.url.query.id);
  }
});
```

---

## Router Plugin

**Package**: `@barba/router`

Add route-based transition rules using path patterns.

**Installation**:
```bash
npm install --save-dev @barba/router
```

**API**:

```javascript
import barbaRouter from '@barba/router';

barbaRouter.init({
  routes: [
    { path: '/', name: 'home' },
    { path: '/about', name: 'about' },
    { path: '/products/:id', name: 'product' },
    { path: '/blog/:category/:slug', name: 'blog-post' },
    { path: '/:lang(en|fr)/:page', name: 'localized-page' }
  ]
});

barba.use(barbaRouter);
```

**Route Properties**:

| Property | Type | Description |
|----------|------|-------------|
| `path` | `string` | URL pattern (supports path-to-regexp syntax) |
| `name` | `string` | Route name (used in transition rules) |

**Path Patterns**:

```javascript
'/products/:id'              // Dynamic segment
'/blog/:category/:slug'      // Multiple segments
'/:lang(en|fr)/:page'        // Alternatives
'/files/:path*'              // Wildcard (0 or more)
'/files/:path+'              // Wildcard (1 or more)
'/products/:id?'             // Optional segment
```

**Usage in Transitions**:

```javascript
barba.init({
  transitions: [{
    name: 'product-transition',
    to: { route: 'product' },  // Matches route name
    enter({ next }) {
      // Get route params from URL
      const productId = next.url.path.split('/').pop();
      console.log('Loading product:', productId);
    }
  }]
});
```

---

## Prefetch Plugin

**Package**: `@barba/prefetch`

Prefetch pages on link hover for faster navigation.

**Installation**:
```bash
npm install --save-dev @barba/prefetch
```

**API**:

```javascript
import barbaPrefetch from '@barba/prefetch';

barba.use(barbaPrefetch);

barba.init({
  prefetch: {
    root: null,        // Element to observe (null = document)
    timeout: 3000      // Cache timeout in ms
  }
});
```

**How It Works**:

1. User hovers over a link
2. Plugin fetches the page via AJAX
3. Page is cached
4. On click, cached page loads instantly (if still in cache)

**Manual Prefetching**:

```javascript
// Prefetch specific URL
barba.prefetch('/about');

// Prefetch multiple URLs
['/about', '/contact', '/services'].forEach(url => {
  barba.prefetch(url);
});
```

---

## CSS Plugin

**Package**: `@barba/css`

CSS-based transitions without writing JavaScript.

**Installation**:
```bash
npm install --save-dev @barba/css
```

**Usage**:

```javascript
import barbaCSS from '@barba/css';

barba.use(barbaCSS);
barba.init();
```

**CSS Classes**:

Barba adds classes during transitions:

| Class | When | Description |
|-------|------|-------------|
| `.barba-once` | Initial load | Applied to wrapper during `once` hook |
| `.barba-leave` | Leave phase | Applied to current container |
| `.barba-leave-active` | Leave active | Added when animation starts |
| `.barba-leave-to` | Leave end | Added when animation should end |
| `.barba-enter` | Enter phase | Applied to next container |
| `.barba-enter-active` | Enter active | Added when animation starts |
| `.barba-enter-to` | Enter end | Added when animation should end |

**Example CSS**:

```css
/* Initial page load */
.barba-once [data-barba="container"] {
  opacity: 0;
  transform: translateY(50px);
  transition: opacity 0.5s, transform 0.5s;
}

.barba-once.barba-once-active [data-barba="container"] {
  opacity: 1;
  transform: translateY(0);
}

/* Leave transition */
.barba-leave-active [data-barba="container"] {
  opacity: 1;
  transition: opacity 0.5s;
}

.barba-leave-to [data-barba="container"] {
  opacity: 0;
}

/* Enter transition */
.barba-enter [data-barba="container"] {
  opacity: 0;
}

.barba-enter-active [data-barba="container"] {
  opacity: 1;
  transition: opacity 0.5s;
}
```

---

## Head Plugin

**Package**: `@barba/head`

Automatically update `<head>` tags (title, meta) on navigation.

**Installation**:
```bash
npm install --save-dev @barba/head
```

**Usage**:

```javascript
import barbaHead from '@barba/head';

barba.use(barbaHead);
barba.init();
```

**What It Updates**:

The plugin updates these `<head>` tags automatically:
- `<title>`
- `<meta>` (name, property, http-equiv)
- `<link>` (canonical, alternate)
- `<script>` (application/ld+json)

**Manual Head Updates**:

If not using the plugin, update manually:

```javascript
barba.hooks.after(({ next }) => {
  // Update title
  document.title = next.html.match(/<title>(.*?)<\/title>/i)[1];

  // Update meta description
  const metaDesc = next.html.match(/<meta name="description" content="(.*?)"/i);
  if (metaDesc) {
    document.querySelector('meta[name="description"]').content = metaDesc[1];
  }
});
```



===== FILE: plugins/individual/barba-js/skills/barba-js/references/gsap_integration.md =====

# Barba.js + GSAP Integration Guide

Complete guide to using GSAP (Green Sock Animation Platform) with Barba.js for smooth, performant page transitions.

## Table of Contents

- [Why GSAP + Barba](#why-gsap--barba)
- [Setup](#setup)
- [Basic Integration Patterns](#basic-integration-patterns)
- [Timeline-Based Transitions](#timeline-based-transitions)
- [Advanced Patterns](#advanced-patterns)
- [Performance Tips](#performance-tips)
- [Common Issues](#common-issues)

---

## Why GSAP + Barba

**Barba.js** handles navigation and lifecycle management.
**GSAP** handles the actual animations.

This combination provides:
- **Performance**: GSAP uses GPU acceleration and optimized rendering
- **Control**: Precise timing with timelines, stagger, and easing
- **Simplicity**: GSAP returns promises that Barba can await
- **Power**: Complex sequences, morphing, and advanced effects

---

## Setup

### Installation

```bash
# Install both libraries
npm install --save-dev @barba/core gsap

# Optional: GSAP plugins
npm install --save-dev gsap/ScrollTrigger
```

### Basic Import

```javascript
import barba from '@barba/core';
import gsap from 'gsap';

// Optional GSAP plugins
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);
```

---

## Basic Integration Patterns

### Pattern 1: Simple Fade

```javascript
barba.init({
  transitions: [{
    name: 'fade',

    async leave({ current }) {
      await gsap.to(current.container, {
        opacity: 0,
        duration: 0.5,
        ease: 'power2.inOut'
      });
    },

    async enter({ next }) {
      // Set initial state
      gsap.set(next.container, { opacity: 0 });

      // Animate in
      await gsap.to(next.container, {
        opacity: 1,
        duration: 0.5,
        ease: 'power2.inOut'
      });
    }
  }]
});
```

**Key Points**:
- GSAP's `to()` returns a promise
- Use `await` to make Barba wait for animation completion
- `gsap.set()` sets initial state without animation

### Pattern 2: Slide Transitions

```javascript
{
  name: 'slide',
  sync: true, // Play leave and enter simultaneously

  leave({ current }) {
    return gsap.to(current.container, {
      x: '-100%',
      duration: 0.7,
      ease: 'power3.inOut'
    });
  },

  enter({ next }) {
    // Start off-screen
    gsap.set(next.container, { x: '100%' });

    // Slide in
    return gsap.to(next.container, {
      x: '0%',
      duration: 0.7,
      ease: 'power3.inOut'
    });
  }
}
```

**Key Points**:
- `sync: true` enables crossfade/overlap effect
- Use `return` instead of `await` (same result)
- GPU-accelerated properties (`x`, `y`, `opacity`, `scale`)

### Pattern 3: Scale and Fade

```javascript
{
  name: 'scale-fade',

  async leave({ current }) {
    await gsap.to(current.container, {
      opacity: 0,
      scale: 0.95,
      duration: 0.5,
      ease: 'power2.in'
    });
  },

  async enter({ next }) {
    await gsap.fromTo(next.container,
      // From
      {
        opacity: 0,
        scale: 1.05
      },
      // To
      {
        opacity: 1,
        scale: 1,
        duration: 0.5,
        ease: 'power2.out'
      }
    );
  }
}
```

**Key Points**:
- `fromTo()` sets initial state and animates to final state
- Different easings for enter/exit (asymmetric feel)

---

## Timeline-Based Transitions

GSAP Timelines provide precise control over complex sequences.

### Basic Timeline

```javascript
{
  name: 'timeline-fade',

  async leave({ current }) {
    const tl = gsap.timeline();

    tl.to(current.container.querySelector('h1'), {
      y: -50,
      opacity: 0,
      duration: 0.3
    })
    .to(current.container.querySelector('.content'), {
      y: -30,
      opacity: 0,
      duration: 0.3
    }, '-=0.2') // Overlap by 0.2s
    .to(current.container, {
      opacity: 0,
      duration: 0.2
    });

    await tl.play();
  },

  async enter({ next }) {
    const tl = gsap.timeline();

    // Set initial states
    gsap.set(next.container, { opacity: 1 });
    gsap.set(next.container.querySelector('h1'), { y: 50, opacity: 0 });
    gsap.set(next.container.querySelector('.content'), { y: 30, opacity: 0 });

    tl.to(next.container.querySelector('h1'), {
      y: 0,
      opacity: 1,
      duration: 0.5,
      ease: 'power3.out'
    })
    .to(next.container.querySelector('.content'), {
      y: 0,
      opacity: 1,
      duration: 0.5,
      ease: 'power3.out'
    }, '-=0.3');

    await tl.play();
  }
}
```

**Timeline Position Parameter**:
- `'-=0.2'` - Start 0.2s before previous animation ends (overlap)
- `'+=0.2'` - Start 0.2s after previous animation ends (delay)
- `'<'` - Start at beginning of previous animation
- `'>'` - Start at end of previous animation

### Staggered Elements

```javascript
{
  async leave({ current }) {
    const tl = gsap.timeline();

    tl.to(current.container.querySelectorAll('.item'), {
      y: -30,
      opacity: 0,
      duration: 0.4,
      stagger: 0.05, // 0.05s delay between each item
      ease: 'power2.in'
    })
    .to(current.container, {
      opacity: 0,
      duration: 0.3
    });

    await tl.play();
  },

  async enter({ next }) {
    const tl = gsap.timeline();

    gsap.set(next.container.querySelectorAll('.item'), { y: 30, opacity: 0 });

    tl.to(next.container.querySelectorAll('.item'), {
      y: 0,
      opacity: 1,
      duration: 0.5,
      stagger: 0.05,
      ease: 'power2.out'
    });

    await tl.play();
  }
}
```

**Stagger Options**:
```javascript
stagger: {
  amount: 0.5,      // Total duration for all staggers
  from: 'start',    // 'start', 'end', 'center', or index number
  grid: [5, 10],    // For grid layouts [rows, columns]
  axis: 'y',        // 'x', 'y', or null
  ease: 'power2.in' // Easing for stagger distribution
}
```

### Timeline with Labels

```javascript
{
  async leave({ current }) {
    const tl = gsap.timeline();

    // Add labels for reference
    tl.addLabel('start')
      .to(current.container.querySelector('.hero'), {
        scale: 0.9,
        opacity: 0,
        duration: 0.5
      })
      .addLabel('hero-done')
      .to(current.container.querySelector('.content'), {
        y: -50,
        opacity: 0,
        duration: 0.4
      }, 'hero-done-=0.2') // Start 0.2s before hero-done
      .addLabel('content-done')
      .to(current.container, {
        opacity: 0,
        duration: 0.2
      }, 'content-done');

    await tl.play();
  }
}
```

---

## Advanced Patterns

### Pattern 1: Conditional Animations

```javascript
{
  async leave({ current, next }) {
    const isProduct = current.namespace === 'product' && next.namespace === 'product';

    if (isProduct) {
      // Fast transition between products
      await gsap.to(current.container, {
        opacity: 0,
        scale: 0.95,
        duration: 0.3
      });
    } else {
      // Slower, more elaborate transition
      const tl = gsap.timeline();

      tl.to(current.container.querySelectorAll('.fade-item'), {
        y: -30,
        opacity: 0,
        duration: 0.4,
        stagger: 0.05
      })
      .to(current.container, {
        opacity: 0,
        duration: 0.3
      });

      await tl.play();
    }
  }
}
```

### Pattern 2: Direction-Based Transitions

```javascript
{
  async leave({ current }) {
    const direction = barba.history.direction;
    const isBack = direction === 'back';

    await gsap.to(current.container, {
      x: isBack ? '100%' : '-100%', // Slide right if going back
      duration: 0.6,
      ease: 'power2.inOut'
    });
  },

  async enter({ next }) {
    const direction = barba.history.direction;
    const isBack = direction === 'back';

    gsap.set(next.container, {
      x: isBack ? '-100%' : '100%' // Come from left if going back
    });

    await gsap.to(next.container, {
      x: '0%',
      duration: 0.6,
      ease: 'power2.inOut'
    });
  }
}
```

### Pattern 3: Curtain Effect

```javascript
{
  async leave({ current }) {
    // Animate curtain down
    const curtain = document.querySelector('.transition-curtain');

    await gsap.fromTo(curtain,
      { yPercent: -100 },
      {
        yPercent: 0,
        duration: 0.6,
        ease: 'power2.inOut'
      }
    );
  },

  async enter({ next }) {
    // Animate curtain up
    const curtain = document.querySelector('.transition-curtain');

    await gsap.to(curtain, {
      yPercent: 100,
      duration: 0.6,
      ease: 'power2.inOut'
    });
  }
}
```

**HTML for Curtain**:
```html
<div class="transition-curtain"></div>
```

**CSS for Curtain**:
```css
.transition-curtain {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000;
  z-index: 9999;
  pointer-events: none;
  transform: translateY(-100%);
}
```

### Pattern 4: Morphing Transitions

```javascript
import { MorphSVGPlugin } from 'gsap/MorphSVGPlugin';
gsap.registerPlugin(MorphSVGPlugin);

{
  async leave({ current }) {
    const shape = document.querySelector('.transition-shape path');

    await gsap.to(shape, {
      morphSVG: '.shape-expanded',
      duration: 0.8,
      ease: 'power2.inOut'
    });
  },

  async enter({ next }) {
    const shape = document.querySelector('.transition-shape path');

    await gsap.to(shape, {
      morphSVG: '.shape-collapsed',
      duration: 0.8,
      ease: 'power2.inOut'
    });
  }
}
```

### Pattern 5: Split Text Animations

```javascript
import { SplitText } from 'gsap/SplitText';
gsap.registerPlugin(SplitText);

{
  async enter({ next }) {
    const title = next.container.querySelector('h1');
    const split = new SplitText(title, { type: 'chars,words' });

    await gsap.from(split.chars, {
      opacity: 0,
      y: 50,
      rotationX: -90,
      stagger: 0.02,
      duration: 0.8,
      ease: 'back.out(1.7)'
    });

    // Clean up
    split.revert();
  }
}
```

### Pattern 6: Parallax Layers

```javascript
{
  sync: true,

  async leave({ current }) {
    const tl = gsap.timeline();

    tl.to(current.container.querySelector('.layer-1'), {
      y: -100,
      opacity: 0,
      duration: 0.8
    }, 0)
    .to(current.container.querySelector('.layer-2'), {
      y: -50,
      opacity: 0,
      duration: 0.8
    }, 0)
    .to(current.container.querySelector('.layer-3'), {
      y: -25,
      opacity: 0,
      duration: 0.8
    }, 0);

    await tl.play();
  },

  async enter({ next }) {
    const tl = gsap.timeline();

    gsap.set(next.container.querySelectorAll('[class^="layer-"]'), {
      opacity: 0
    });

    tl.from(next.container.querySelector('.layer-1'), {
      y: 100,
      opacity: 0,
      duration: 0.8
    }, 0)
    .from(next.container.querySelector('.layer-2'), {
      y: 50,
      opacity: 0,
      duration: 0.8
    }, 0)
    .from(next.container.querySelector('.layer-3'), {
      y: 25,
      opacity: 0,
      duration: 0.8
    }, 0);

    await tl.play();
  }
}
```

---

## Performance Tips

### 1. Use GPU-Accelerated Properties

```javascript
// ✅ Good - GPU accelerated
gsap.to(element, {
  x: 100,
  y: 50,
  opacity: 0.5,
  scale: 1.2,
  rotation: 45
});

// ❌ Avoid - causes reflow/repaint
gsap.to(element, {
  left: '100px',
  top: '50px',
  width: '200px',
  height: '300px'
});
```

### 2. Use will-change with Caution

```css
/* Add to elements that will animate */
[data-barba="container"] {
  will-change: transform, opacity;
}

/* Remove after transition */
```

```javascript
barba.hooks.after(() => {
  // Remove will-change after transition
  document.querySelectorAll('[data-barba="container"]').forEach(el => {
    el.style.willChange = 'auto';
  });
});
```

### 3. Kill Running Animations

```javascript
{
  beforeLeave({ current }) {
    // Kill any running animations on current page
    gsap.killTweensOf(current.container.querySelectorAll('*'));
  }
}
```

### 4. Batch DOM Queries

```javascript
// ❌ Slow - queries DOM multiple times
{
  async leave({ current }) {
    await gsap.to(current.container.querySelector('h1'), { opacity: 0 });
    await gsap.to(current.container.querySelector('.content'), { opacity: 0 });
    await gsap.to(current.container.querySelector('.footer'), { opacity: 0 });
  }
}

// ✅ Fast - queries DOM once
{
  async leave({ current }) {
    const h1 = current.container.querySelector('h1');
    const content = current.container.querySelector('.content');
    const footer = current.container.querySelector('.footer');

    const tl = gsap.timeline();

    tl.to(h1, { opacity: 0 })
      .to(content, { opacity: 0 }, '<')
      .to(footer, { opacity: 0 }, '<');

    await tl.play();
  }
}
```

### 5. Use force3D for Mobile

```javascript
gsap.to(element, {
  x: 100,
  force3D: true, // Force GPU acceleration
  duration: 0.5
});
```

---

## Common Issues

### Issue 1: Animation Doesn't Wait

**Problem**: Page transitions instantly without animation.

**Solution**: Always return promise or use `await`:

```javascript
// ❌ Wrong
leave({ current }) {
  gsap.to(current.container, { opacity: 0 });
}

// ✅ Correct
leave({ current }) {
  return gsap.to(current.container, { opacity: 0 });
}

// ✅ Also correct
async leave({ current }) {
  await gsap.to(current.container, { opacity: 0 });
}
```

### Issue 2: Flash of Content (FOUC)

**Problem**: New page visible before enter animation.

**Solution**: Set initial state in `beforeEnter` or CSS:

```javascript
beforeEnter({ next }) {
  gsap.set(next.container, { opacity: 0 });
}
```

Or in CSS:
```css
[data-barba="container"] {
  opacity: 0;
}
```

### Issue 3: Sync Mode Layout Shift

**Problem**: Containers stack during sync transitions.

**Solution**: Position absolutely during transition:

```css
[data-barba="wrapper"] {
  position: relative;
}

[data-barba="container"] {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}
```

Or in JavaScript:
```javascript
{
  sync: true,
  beforeLeave({ current }) {
    gsap.set(current.container, {
      position: 'absolute',
      top: 0,
      width: '100%'
    });
  }
}
```

### Issue 4: ScrollTrigger Conflicts

**Problem**: ScrollTrigger instances persist after page change.

**Solution**: Kill ScrollTriggers in `beforeLeave`:

```javascript
import { ScrollTrigger } from 'gsap/ScrollTrigger';

barba.hooks.beforeLeave(() => {
  // Kill all ScrollTrigger instances
  ScrollTrigger.getAll().forEach(trigger => trigger.kill());
});

// Or use scoped instances
barba.init({
  views: [{
    namespace: 'home',
    afterEnter() {
      // Create ScrollTriggers
      this.scrollTriggers = [];

      this.scrollTriggers.push(
        ScrollTrigger.create({
          trigger: '.section',
          // ...
        })
      );
    },
    beforeLeave() {
      // Kill scoped ScrollTriggers
      this.scrollTriggers.forEach(trigger => trigger.kill());
    }
  }]
});
```

### Issue 5: Memory Leaks

**Problem**: Timelines/tweens accumulate.

**Solution**: Kill tweens before creating new ones:

```javascript
barba.hooks.beforeLeave(({ current }) => {
  // Kill all tweens on current page
  gsap.killTweensOf(current.container);
  gsap.killTweensOf(current.container.querySelectorAll('*'));
});
```

### Issue 6: Timeline Doesn't Await

**Problem**: Timeline starts but doesn't wait for completion.

**Solution**: Call `.play()` on timeline (it returns a promise):

```javascript
// ❌ Wrong
async leave({ current }) {
  const tl = gsap.timeline();
  tl.to(current.container, { opacity: 0 });
  // Timeline starts but function returns immediately
}

// ✅ Correct
async leave({ current }) {
  const tl = gsap.timeline();
  tl.to(current.container, { opacity: 0 });
  await tl.play(); // Wait for timeline to complete
}
```

---

## Easing Reference

Common GSAP easings for transitions:

```javascript
// Smooth and natural
ease: 'power2.inOut'

// Gentle acceleration
ease: 'power1.out'

// Strong deceleration
ease: 'power3.out'

// Bounce effect
ease: 'back.out(1.7)'

// Elastic effect
ease: 'elastic.out(1, 0.3)'

// Custom bezier
ease: 'cubic-bezier(0.4, 0, 0.2, 1)'
```

**Recommended for Barba transitions**:
- Leave: `'power2.in'` or `'power2.inOut'`
- Enter: `'power2.out'` or `'power3.out'`



===== FILE: plugins/individual/barba-js/skills/barba-js/references/hooks_guide.md =====

# Barba.js Hooks Guide

Comprehensive guide to all 11 Barba.js lifecycle hooks with execution order, use cases, and examples.

## Table of Contents

- [Hook Execution Order](#hook-execution-order)
- [Hook Types and Contexts](#hook-types-and-contexts)
- [Async Hook Patterns](#async-hook-patterns)
- [Individual Hooks](#individual-hooks)
- [Common Hook Patterns](#common-hook-patterns)
- [Best Practices](#best-practices)

---

## Hook Execution Order

### Initial Page Load

When the website first loads:

```
beforeOnce → once → afterOnce
```

**Timeline**:
1. `beforeOnce` - Setup before first render
2. `once` - Intro animation plays
3. `afterOnce` - Cleanup after first render

### Every Navigation

When navigating between pages:

```
before → beforeLeave → leave → afterLeave →
beforeEnter → enter → afterEnter → after
```

**Timeline**:
1. `before` - Transition starts
2. `beforeLeave` - Prepare to leave current page
3. `leave` - Animate current page out
4. `afterLeave` - Cleanup after leaving
5. **[Container swap happens here]**
6. `beforeEnter` - Prepare to enter new page
7. `enter` - Animate new page in
8. `afterEnter` - Initialize new page
9. `after` - Transition complete

### Sync Mode Execution Order

With `sync: true`, the order changes:

```
before → beforeLeave → beforeEnter →
(leave + enter simultaneously) →
afterLeave → afterEnter → after
```

**Key Difference**: `leave` and `enter` run at the same time (crossfade effect).

---

## Hook Types and Contexts

### 1. Global Hooks

Run on **every** transition, registered via `barba.hooks`:

```javascript
barba.hooks.before(() => {
  console.log('Every transition');
});

barba.hooks.afterEnter(({ next }) => {
  console.log('Entered:', next.namespace);
});
```

**Use for**:
- Universal behavior (analytics, scroll reset)
- Debug logging
- Loading indicators
- Third-party script re-initialization

### 2. Transition Hooks

Run when a **specific transition** matches:

```javascript
barba.init({
  transitions: [{
    name: 'fade',
    leave({ current }) {
      return gsap.to(current.container, { opacity: 0 });
    },
    enter({ next }) {
      return gsap.from(next.container, { opacity: 0 });
    }
  }]
});
```

**Use for**:
- Transition-specific animations
- Conditional behaviors based on navigation context

### 3. View Hooks

Run for **specific namespaces**:

```javascript
barba.init({
  views: [{
    namespace: 'home',
    afterEnter() {
      console.log('Home page entered');
      initHomeFeatures();
    },
    beforeLeave() {
      console.log('Leaving home page');
      cleanupHomeFeatures();
    }
  }]
});
```

**Use for**:
- Page-specific initialization
- Feature cleanup before leaving page

### Hook Availability Matrix

| Hook | Global | Transition | View |
|------|--------|------------|------|
| `beforeOnce` | ✅ | ✅ | ❌ |
| `once` | ✅ | ✅ | ❌ |
| `afterOnce` | ✅ | ✅ | ❌ |
| `before` | ✅ | ✅ | ❌ |
| `beforeLeave` | ✅ | ✅ | ✅ |
| `leave` | ✅ | ✅ | ❌ |
| `afterLeave` | ✅ | ✅ | ✅ |
| `beforeEnter` | ✅ | ✅ | ✅ |
| `enter` | ✅ | ✅ | ❌ |
| `afterEnter` | ✅ | ✅ | ✅ |
| `after` | ✅ | ✅ | ❌ |

---

## Async Hook Patterns

Hooks can be synchronous or asynchronous. Barba waits for async hooks to complete before continuing.

### Pattern 1: Returning Promises

```javascript
leave({ current }) {
  // Return the promise
  return gsap.to(current.container, {
    opacity: 0,
    duration: 0.5
  });
}
```

### Pattern 2: Async/Await

```javascript
async leave({ current }) {
  await gsap.to(current.container, {
    opacity: 0,
    duration: 0.5
  });

  // Can chain multiple awaits
  await someOtherAsyncOperation();
}
```

### Pattern 3: Manual async() Method

```javascript
leave({ current }) {
  const done = this.async();

  setTimeout(() => {
    gsap.to(current.container, { opacity: 0 });
    done(); // Signal completion
  }, 500);
}
```

### Pattern 4: Promise.all for Parallel Operations

```javascript
async leave({ current }) {
  // Run animations in parallel
  await Promise.all([
    gsap.to(current.container.querySelector('h1'), { opacity: 0 }),
    gsap.to(current.container.querySelector('.content'), { y: -50 }),
    fetch('/api/track-exit')
  ]);
}
```

---

## Individual Hooks

### beforeOnce

**Execution**: Before initial page load
**Available in**: Global, Transition
**Async**: Yes

**Purpose**: Setup before the first page renders.

**Common Use Cases**:
- Show loading screen
- Prepare intro animation
- Initial app setup

**Examples**:

```javascript
// Show loader
barba.hooks.beforeOnce(() => {
  document.querySelector('.loader').style.display = 'flex';
});

// In transition
{
  beforeOnce() {
    gsap.set('.intro-title', { opacity: 0, y: 50 });
  }
}
```

---

### once

**Execution**: During initial page load
**Available in**: Global, Transition
**Async**: Yes

**Purpose**: Animate the first page view (intro animation).

**Common Use Cases**:
- Intro animations
- Reveal content on first load
- Splash screen effects

**Examples**:

```javascript
// Simple fade in
{
  async once({ next }) {
    await gsap.from(next.container, {
      opacity: 0,
      duration: 1
    });
  }
}

// Complex intro sequence
{
  async once({ next }) {
    const tl = gsap.timeline();

    tl.to('.loader', { opacity: 0, duration: 0.5 })
      .set('.loader', { display: 'none' })
      .from('.intro-title', { opacity: 0, y: 50, duration: 0.8 })
      .from('.intro-subtitle', { opacity: 0, y: 30, duration: 0.6 }, '-=0.4')
      .from(next.container, { opacity: 0, duration: 0.5 });

    await tl.play();
  }
}
```

---

### afterOnce

**Execution**: After initial page load
**Available in**: Global, Transition
**Async**: Yes

**Purpose**: Cleanup or initialization after intro animation.

**Common Use Cases**:
- Hide loading screen
- Initialize page features
- Track page load

**Examples**:

```javascript
barba.hooks.afterOnce(() => {
  // Hide loader
  document.querySelector('.loader').style.display = 'none';

  // Track page load
  gtag('event', 'page_load', { page: window.location.pathname });
});
```

---

### before

**Execution**: Before every transition starts
**Available in**: Global, Transition
**Async**: Yes

**Purpose**: Setup before transition begins.

**Common Use Cases**:
- Show loading indicator
- Prepare global state
- Disable interactions during transition

**Examples**:

```javascript
// Global loading indicator
barba.hooks.before(() => {
  document.body.classList.add('is-transitioning');
  document.querySelector('.page-loader').classList.add('active');
});

// Disable scroll during transition
barba.hooks.before(() => {
  document.body.style.overflow = 'hidden';
});
```

---

### beforeLeave

**Execution**: Before leaving current page
**Available in**: Global, Transition, View
**Async**: Yes

**Purpose**: Prepare current page before leave animation.

**Common Use Cases**:
- Reset scroll position
- Prepare elements for leave animation
- Save page state

**Examples**:

```javascript
// Reset scroll (global)
barba.hooks.beforeLeave(() => {
  window.scrollTo(0, 0);
});

// Prepare animation elements
{
  beforeLeave({ current }) {
    // Reset any transforms that might interfere
    gsap.set(current.container.querySelectorAll('.animated'), {
      clearProps: 'all'
    });
  }
}

// View-specific cleanup
{
  views: [{
    namespace: 'gallery',
    beforeLeave() {
      // Save scroll position for this page
      sessionStorage.setItem('galleryScroll', window.scrollY);
    }
  }]
}
```

---

### leave

**Execution**: Current page exit animation
**Available in**: Global, Transition
**Async**: Yes (must return promise or use async/await)

**Purpose**: Animate current page out.

**Common Use Cases**:
- Fade out animation
- Slide out animation
- Complex exit sequences

**Examples**:

```javascript
// Simple fade out
{
  async leave({ current }) {
    await gsap.to(current.container, {
      opacity: 0,
      duration: 0.5
    });
  }
}

// Slide out left
{
  leave({ current }) {
    return gsap.to(current.container, {
      x: '-100%',
      duration: 0.6,
      ease: 'power2.inOut'
    });
  }
}

// Complex staggered exit
{
  async leave({ current }) {
    const tl = gsap.timeline();

    tl.to(current.container.querySelector('h1'), {
      y: -50,
      opacity: 0,
      duration: 0.3
    })
    .to(current.container.querySelectorAll('.content > *'), {
      y: -30,
      opacity: 0,
      duration: 0.3,
      stagger: 0.05
    }, '-=0.2')
    .to(current.container, {
      opacity: 0,
      duration: 0.2
    });

    await tl.play();
  }
}
```

---

### afterLeave

**Execution**: After leaving current page
**Available in**: Global, Transition, View
**Async**: Yes

**Purpose**: Cleanup after current page has animated out.

**Common Use Cases**:
- Remove event listeners
- Clean up third-party widgets
- Debug logging

**Examples**:

```javascript
// Global cleanup
barba.hooks.afterLeave(({ current }) => {
  console.log('Left page:', current.namespace);
});

// View-specific cleanup
{
  views: [{
    namespace: 'video-gallery',
    afterLeave({ current }) {
      // Pause all videos
      current.container.querySelectorAll('video').forEach(video => {
        video.pause();
        video.currentTime = 0;
      });

      // Remove event listeners
      current.container.querySelectorAll('.video-play').forEach(btn => {
        btn.removeEventListener('click', handleVideoPlay);
      });
    }
  }]
}
```

---

### beforeEnter

**Execution**: Before entering new page
**Available in**: Global, Transition, View
**Async**: Yes

**Purpose**: Prepare new page before enter animation.

**Common Use Cases**:
- Set initial animation states
- Load images
- Prepare page-specific features

**Examples**:

```javascript
// Set initial state for animation
{
  beforeEnter({ next }) {
    gsap.set(next.container, { opacity: 0 });
  }
}

// Load images
barba.hooks.beforeEnter(({ next }) => {
  const images = next.container.querySelectorAll('img[data-src]');
  images.forEach(img => {
    img.src = img.dataset.src;
    img.removeAttribute('data-src');
  });
});

// Restore scroll position
{
  views: [{
    namespace: 'gallery',
    beforeEnter() {
      const savedScroll = sessionStorage.getItem('galleryScroll');
      if (savedScroll) {
        window.scrollTo(0, parseInt(savedScroll));
      }
    }
  }]
}
```

---

### enter

**Execution**: New page entrance animation
**Available in**: Global, Transition
**Async**: Yes (must return promise or use async/await)

**Purpose**: Animate new page in.

**Common Use Cases**:
- Fade in animation
- Slide in animation
- Complex entrance sequences

**Examples**:

```javascript
// Simple fade in
{
  async enter({ next }) {
    await gsap.from(next.container, {
      opacity: 0,
      duration: 0.5
    });
  }
}

// Slide in from right
{
  enter({ next }) {
    return gsap.from(next.container, {
      x: '100%',
      duration: 0.6,
      ease: 'power2.inOut'
    });
  }
}

// Complex staggered entrance
{
  async enter({ next }) {
    const tl = gsap.timeline();

    // Set initial states
    gsap.set(next.container, { opacity: 1 });
    gsap.set(next.container.querySelector('h1'), { y: 50, opacity: 0 });
    gsap.set(next.container.querySelectorAll('.content > *'), { y: 30, opacity: 0 });

    tl.to(next.container.querySelector('h1'), {
      y: 0,
      opacity: 1,
      duration: 0.5,
      ease: 'power3.out'
    })
    .to(next.container.querySelectorAll('.content > *'), {
      y: 0,
      opacity: 1,
      duration: 0.5,
      stagger: 0.05,
      ease: 'power2.out'
    }, '-=0.3');

    await tl.play();
  }
}
```

---

### afterEnter

**Execution**: After entering new page
**Available in**: Global, Transition, View
**Async**: Yes

**Purpose**: Initialize features after new page has animated in.

**Common Use Cases**:
- Initialize page features
- Track page views
- Start auto-playing content

**Examples**:

```javascript
// Global analytics tracking
barba.hooks.afterEnter(({ next }) => {
  gtag('config', 'GA_MEASUREMENT_ID', {
    page_path: next.url.path,
    page_title: document.title
  });
});

// Re-initialize third-party scripts
barba.hooks.afterEnter(() => {
  if (typeof Prism !== 'undefined') {
    Prism.highlightAll();
  }

  if (typeof twttr !== 'undefined') {
    twttr.widgets.load();
  }
});

// View-specific initialization
{
  views: [
    {
      namespace: 'home',
      afterEnter() {
        initHomeSlider();
        initParallaxEffects();
      }
    },
    {
      namespace: 'product',
      afterEnter({ next }) {
        const productId = next.url.path.split('/').pop();
        loadProductData(productId);
      }
    },
    {
      namespace: 'video',
      afterEnter({ next }) {
        const video = next.container.querySelector('video');
        if (video) {
          video.play();
        }
      }
    }
  ]
}
```

---

### after

**Execution**: After every transition completes
**Available in**: Global, Transition
**Async**: Yes

**Purpose**: Final cleanup after transition.

**Common Use Cases**:
- Hide loading indicators
- Re-enable interactions
- Debug logging

**Examples**:

```javascript
// Global loading indicator
barba.hooks.after(() => {
  document.body.classList.remove('is-transitioning');
  document.querySelector('.page-loader').classList.remove('active');
});

// Re-enable scroll
barba.hooks.after(() => {
  document.body.style.overflow = '';
});

// Debug transition
barba.hooks.after(({ current, next }) => {
  console.log(`Transition complete: ${current.namespace} → ${next.namespace}`);
});
```

---

## Common Hook Patterns

### Pattern 1: Loading Indicator

```javascript
barba.hooks.before(() => {
  gsap.to('.loader', { opacity: 1, duration: 0.3 });
});

barba.hooks.after(() => {
  gsap.to('.loader', { opacity: 0, duration: 0.3 });
});
```

### Pattern 2: Scroll Management

```javascript
barba.hooks.beforeLeave(() => {
  // Save current scroll position
  sessionStorage.setItem('scrollPos', window.scrollY);
});

barba.hooks.beforeEnter(({ next }) => {
  // Reset to top for new pages
  window.scrollTo(0, 0);

  // Or restore scroll for same page
  // const savedScroll = sessionStorage.getItem('scrollPos');
  // if (savedScroll) window.scrollTo(0, parseInt(savedScroll));
});
```

### Pattern 3: Analytics Tracking

```javascript
barba.hooks.after(({ next }) => {
  // Google Analytics 4
  gtag('config', 'GA_MEASUREMENT_ID', {
    page_path: next.url.path,
    page_title: document.title
  });

  // Or GTM data layer
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: 'pageview',
    page: next.url.path
  });
});
```

### Pattern 4: Third-Party Script Re-Init

```javascript
barba.hooks.afterEnter(() => {
  // Syntax highlighting
  if (typeof Prism !== 'undefined') {
    Prism.highlightAll();
  }

  // Social widgets
  if (typeof twttr !== 'undefined') {
    twttr.widgets.load();
  }

  if (typeof FB !== 'undefined') {
    FB.XFBML.parse();
  }

  // Custom form library
  if (typeof customForms !== 'undefined') {
    customForms.init();
  }
});
```

### Pattern 5: View-Specific Features

```javascript
barba.init({
  views: [
    {
      namespace: 'home',
      afterEnter() {
        initHomeSlider();
        initParallax();
      },
      beforeLeave() {
        destroyHomeSlider();
      }
    },
    {
      namespace: 'shop',
      afterEnter() {
        initProductFilters();
        initAddToCart();
      },
      beforeLeave() {
        // Cleanup
        document.querySelectorAll('.product-quick-view').forEach(el => {
          el.remove();
        });
      }
    }
  ]
});
```

### Pattern 6: Conditional Transitions

```javascript
barba.init({
  transitions: [
    // Slow fade for first visit
    {
      name: 'first-visit',
      once: async ({ next }) => {
        await gsap.from(next.container, {
          opacity: 0,
          duration: 1.5
        });
      }
    },
    // Fast fade for same namespace
    {
      name: 'same-page-type',
      custom: ({ current, next }) => current.namespace === next.namespace,
      leave: ({ current }) => {
        return gsap.to(current.container, { opacity: 0, duration: 0.2 });
      },
      enter: ({ next }) => {
        return gsap.from(next.container, { opacity: 0, duration: 0.2 });
      }
    },
    // Slower transition for different page types
    {
      name: 'different-page-type',
      leave: ({ current }) => {
        return gsap.to(current.container, { opacity: 0, duration: 0.5 });
      },
      enter: ({ next }) => {
        return gsap.from(next.container, { opacity: 0, duration: 0.5 });
      }
    }
  ]
});
```

---

## Best Practices

### 1. Always Return Promises or Use Async/Await

```javascript
// ❌ Wrong - animation won't wait
leave({ current }) {
  gsap.to(current.container, { opacity: 0 });
}

// ✅ Correct - returns promise
leave({ current }) {
  return gsap.to(current.container, { opacity: 0 });
}

// ✅ Also correct - async/await
async leave({ current }) {
  await gsap.to(current.container, { opacity: 0 });
}
```

### 2. Use Global Hooks for Universal Behavior

```javascript
// ✅ Good - analytics tracking applies everywhere
barba.hooks.after(({ next }) => {
  gtag('config', 'GA_ID', { page_path: next.url.path });
});

// ❌ Avoid - repeating in every transition
{
  transitions: [{
    after({ next }) {
      gtag('config', 'GA_ID', { page_path: next.url.path });
    }
  }]
}
```

### 3. Use View Hooks for Page-Specific Logic

```javascript
// ✅ Good - isolated to home page
{
  views: [{
    namespace: 'home',
    afterEnter() {
      initHomeSlider();
    }
  }]
}

// ❌ Avoid - checking namespace manually
barba.hooks.afterEnter(({ next }) => {
  if (next.namespace === 'home') {
    initHomeSlider();
  }
});
```

### 4. Clean Up in beforeLeave, Not afterLeave

```javascript
// ✅ Good - cleanup before leaving
{
  views: [{
    namespace: 'video',
    beforeLeave({ current }) {
      current.container.querySelectorAll('video').forEach(v => v.pause());
    }
  }]
}

// ❌ Risky - container might already be removed
{
  views: [{
    namespace: 'video',
    afterLeave({ current }) {
      // current.container might not be in DOM anymore
      current.container.querySelectorAll('video').forEach(v => v.pause());
    }
  }]
}
```

### 5. Set Initial States in beforeEnter, Not enter

```javascript
// ✅ Good - prevents flash of content
{
  beforeEnter({ next }) {
    gsap.set(next.container, { opacity: 0 });
  },
  enter({ next }) {
    return gsap.to(next.container, { opacity: 1 });
  }
}

// ❌ Risky - might flash visible
{
  enter({ next }) {
    return gsap.from(next.container, { opacity: 0 });
  }
}
```

### 6. Use Hook Contexts Appropriately

```javascript
// ✅ Correct usage
barba.init({
  // Global hooks - universal behavior
  hooks: {
    after: () => { /* ... */ }
  },

  // Transitions - animation logic
  transitions: [{
    leave() { /* ... */ },
    enter() { /* ... */ }
  }],

  // Views - page-specific logic
  views: [{
    namespace: 'home',
    afterEnter() { /* ... */ }
  }]
});
```

### 7. Handle Errors Gracefully

```javascript
barba.hooks.afterEnter(({ next }) => {
  try {
    initPageFeatures(next.container);
  } catch (error) {
    console.error('Failed to initialize page features:', error);
    // Fallback or report error
  }
});
```



===== FILE: plugins/individual/barba-js/skills/barba-js/references/transition_patterns.md =====

# Barba.js Transition Patterns Library

Copy-paste transition implementations for common page transition effects.

## Table of Contents

- [Fade Transitions](#fade-transitions)
- [Slide Transitions](#slide-transitions)
- [Scale Transitions](#scale-transitions)
- [Creative Transitions](#creative-transitions)
- [Conditional Transitions](#conditional-transitions)
- [Production Examples](#production-examples)

---

## Fade Transitions

### Simple Fade

Classic fade out → fade in:

```javascript
{
  name: 'fade',

  async leave({ current }) {
    await gsap.to(current.container, {
      opacity: 0,
      duration: 0.5,
      ease: 'power2.inOut'
    });
  },

  async enter({ next }) {
    gsap.set(next.container, { opacity: 0 });

    await gsap.to(next.container, {
      opacity: 1,
      duration: 0.5,
      ease: 'power2.inOut'
    });
  }
}
```

### Crossfade (Sync)

Both pages fade simultaneously:

```javascript
{
  name: 'crossfade',
  sync: true,

  leave({ current }) {
    return gsap.to(current.container, {
      opacity: 0,
      duration: 0.8,
      ease: 'power2.inOut'
    });
  },

  enter({ next }) {
    return gsap.from(next.container, {
      opacity: 0,
      duration: 0.8,
      ease: 'power2.inOut'
    });
  }
}
```

### Fade with Scale

Fade + subtle zoom:

```javascript
{
  name: 'fade-scale',

  async leave({ current }) {
    await gsap.to(current.container, {
      opacity: 0,
      scale: 0.95,
      duration: 0.5,
      ease: 'power2.in'
    });
  },

  async enter({ next }) {
    await gsap.fromTo(next.container,
      {
        opacity: 0,
        scale: 1.05
      },
      {
        opacity: 1,
        scale: 1,
        duration: 0.6,
        ease: 'power2.out'
      }
    );
  }
}
```

---

## Slide Transitions

### Horizontal Slide

Old page slides left, new page slides in from right:

```javascript
{
  name: 'slide-horizontal',
  sync: true,

  leave({ current }) {
    return gsap.to(current.container, {
      x: '-100%',
      duration: 0.7,
      ease: 'power3.inOut'
    });
  },

  enter({ next }) {
    gsap.set(next.container, { x: '100%' });

    return gsap.to(next.container, {
      x: '0%',
      duration: 0.7,
      ease: 'power3.inOut'
    });
  }
}
```

### Vertical Slide

Old page slides up, new page slides in from bottom:

```javascript
{
  name: 'slide-vertical',
  sync: true,

  leave({ current }) {
    return gsap.to(current.container, {
      y: '-100%',
      duration: 0.7,
      ease: 'power3.inOut'
    });
  },

  enter({ next }) {
    gsap.set(next.container, { y: '100%' });

    return gsap.to(next.container, {
      y: '0%',
      duration: 0.7,
      ease: 'power3.inOut'
    });
  }
}
```

### Direction-Based Slide

Slide direction based on browser history:

```javascript
{
  name: 'slide-smart',
  sync: true,

  leave({ current }) {
    const direction = barba.history.direction;
    const isBack = direction === 'back';

    return gsap.to(current.container, {
      x: isBack ? '100%' : '-100%',
      duration: 0.6,
      ease: 'power2.inOut'
    });
  },

  enter({ next }) {
    const direction = barba.history.direction;
    const isBack = direction === 'back';

    gsap.set(next.container, {
      x: isBack ? '-100%' : '100%'
    });

    return gsap.to(next.container, {
      x: '0%',
      duration: 0.6,
      ease: 'power2.inOut'
    });
  }
}
```

**CSS Required** (for sync mode):
```css
[data-barba="wrapper"] {
  position: relative;
  overflow: hidden;
}

[data-barba="container"] {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}
```

---

## Scale Transitions

### Zoom Out → Zoom In

```javascript
{
  name: 'zoom',

  async leave({ current }) {
    await gsap.to(current.container, {
      opacity: 0,
      scale: 0.8,
      duration: 0.5,
      ease: 'power2.in'
    });
  },

  async enter({ next }) {
    await gsap.fromTo(next.container,
      {
        opacity: 0,
        scale: 1.2
      },
      {
        opacity: 1,
        scale: 1,
        duration: 0.6,
        ease: 'power2.out'
      }
    );
  }
}
```

### Rotate Zoom

3D rotation with zoom:

```javascript
{
  name: 'rotate-zoom',

  async leave({ current }) {
    await gsap.to(current.container, {
      opacity: 0,
      scale: 0.9,
      rotationY: 15,
      duration: 0.6,
      ease: 'power2.in'
    });
  },

  async enter({ next }) {
    await gsap.fromTo(next.container,
      {
        opacity: 0,
        scale: 0.9,
        rotationY: -15
      },
      {
        opacity: 1,
        scale: 1,
        rotationY: 0,
        duration: 0.7,
        ease: 'power2.out'
      }
    );
  }
}
```

**CSS Required**:
```css
[data-barba="wrapper"] {
  perspective: 1000px;
}
```

---

## Creative Transitions

### Curtain Effect

Animated overlay curtain:

```javascript
{
  name: 'curtain',

  async leave({ current }) {
    const curtain = document.querySelector('.transition-curtain');

    // Bring curtain down
    await gsap.fromTo(curtain,
      { yPercent: -100 },
      {
        yPercent: 0,
        duration: 0.6,
        ease: 'power2.inOut'
      }
    );
  },

  async enter({ next }) {
    const curtain = document.querySelector('.transition-curtain');

    // Lift curtain up
    await gsap.to(curtain, {
      yPercent: 100,
      duration: 0.6,
      ease: 'power2.inOut'
    });
  }
}
```

**HTML Required**:
```html
<div class="transition-curtain"></div>
```

**CSS Required**:
```css
.transition-curtain {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 9999;
  pointer-events: none;
  transform: translateY(-100%);
}
```

### Wipe Effect

Diagonal wipe transition:

```javascript
{
  name: 'wipe',

  async leave({ current }) {
    const wipe = document.querySelector('.transition-wipe');

    await gsap.fromTo(wipe,
      {
        xPercent: -100,
        skewX: -10
      },
      {
        xPercent: 0,
        skewX: 0,
        duration: 0.8,
        ease: 'power2.inOut'
      }
    );
  },

  async enter({ next }) {
    const wipe = document.querySelector('.transition-wipe');

    gsap.set(next.container, { opacity: 1 });

    await gsap.to(wipe, {
      xPercent: 100,
      skewX: 10,
      duration: 0.8,
      ease: 'power2.inOut'
    });
  }
}
```

**HTML Required**:
```html
<div class="transition-wipe"></div>
```

**CSS Required**:
```css
.transition-wipe {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000;
  z-index: 9999;
  pointer-events: none;
  transform: translateX(-100%);
}
```

### Staggered Elements

Elements animate out/in individually:

```javascript
{
  name: 'stagger',

  async leave({ current }) {
    const tl = gsap.timeline();

    tl.to(current.container.querySelectorAll('.stagger-item'), {
      y: -50,
      opacity: 0,
      duration: 0.5,
      stagger: 0.05,
      ease: 'power2.in'
    })
    .to(current.container, {
      opacity: 0,
      duration: 0.3
    }, '-=0.2');

    await tl.play();
  },

  async enter({ next }) {
    const tl = gsap.timeline();

    gsap.set(next.container.querySelectorAll('.stagger-item'), {
      y: 50,
      opacity: 0
    });

    tl.to(next.container.querySelectorAll('.stagger-item'), {
      y: 0,
      opacity: 1,
      duration: 0.6,
      stagger: 0.05,
      ease: 'power2.out'
    });

    await tl.play();
  }
}
```

**HTML Classes Required**:
```html
<div data-barba="container">
  <h1 class="stagger-item">Title</h1>
  <p class="stagger-item">Paragraph 1</p>
  <p class="stagger-item">Paragraph 2</p>
  <div class="stagger-item">Content</div>
</div>
```

---

## Conditional Transitions

### Different Transition Per Namespace

```javascript
barba.init({
  transitions: [
    // From home: fade
    {
      name: 'from-home',
      from: { namespace: 'home' },

      async leave({ current }) {
        await gsap.to(current.container, {
          opacity: 0,
          duration: 0.5
        });
      },

      async enter({ next }) {
        await gsap.from(next.container, {
          opacity: 0,
          duration: 0.5
        });
      }
    },

    // To/from product: slide
    {
      name: 'product-transition',
      from: { namespace: 'product' },
      to: { namespace: 'product' },
      sync: true,

      leave({ current }) {
        return gsap.to(current.container, {
          x: '-100%',
          duration: 0.6
        });
      },

      enter({ next }) {
        gsap.set(next.container, { x: '100%' });
        return gsap.to(next.container, {
          x: '0%',
          duration: 0.6
        });
      }
    },

    // Default: crossfade
    {
      name: 'default',
      sync: true,

      leave({ current }) {
        return gsap.to(current.container, {
          opacity: 0,
          duration: 0.4
        });
      },

      enter({ next }) {
        return gsap.from(next.container, {
          opacity: 0,
          duration: 0.4
        });
      }
    }
  ]
});
```

### Custom Rule Based on Data Attribute

```javascript
{
  name: 'article-to-article',
  custom: ({ current, next }) => {
    // Check if both pages have data-article attribute
    return current.container.dataset.article && next.container.dataset.article;
  },

  async leave({ current }) {
    await gsap.to(current.container, {
      opacity: 0,
      scale: 0.95,
      duration: 0.3
    });
  },

  async enter({ next }) {
    await gsap.fromTo(next.container,
      { opacity: 0, scale: 1.05 },
      { opacity: 1, scale: 1, duration: 0.4 }
    );
  }
}
```

---

## Production Examples

### E-commerce Product Pages

Fast transitions between products, slower elsewhere:

```javascript
barba.init({
  transitions: [
    // Product to product: fast slide
    {
      name: 'product-to-product',
      from: { namespace: 'product' },
      to: { namespace: 'product' },
      sync: true,

      leave({ current }) {
        return gsap.to(current.container, {
          x: '-50%',
          opacity: 0,
          duration: 0.4,
          ease: 'power2.inOut'
        });
      },

      enter({ next }) {
        gsap.set(next.container, { x: '50%', opacity: 0 });

        return gsap.to(next.container, {
          x: '0%',
          opacity: 1,
          duration: 0.4,
          ease: 'power2.inOut'
        });
      }
    },

    // Default: elegant fade
    {
      name: 'default',

      async leave({ current }) {
        await gsap.to(current.container, {
          opacity: 0,
          y: -30,
          duration: 0.6,
          ease: 'power2.in'
        });
      },

      async enter({ next }) {
        await gsap.fromTo(next.container,
          { opacity: 0, y: 30 },
          { opacity: 1, y: 0, duration: 0.7, ease: 'power2.out' }
        );
      }
    }
  ]
});
```

### Portfolio with Loading Indicator

```javascript
barba.init({
  transitions: [{
    name: 'portfolio',

    async leave({ current }) {
      const loader = document.querySelector('.page-loader');

      // Fade out content
      await gsap.to(current.container, {
        opacity: 0,
        duration: 0.4
      });

      // Show loader
      gsap.to(loader, {
        opacity: 1,
        duration: 0.3
      });
    },

    async enter({ next }) {
      const loader = document.querySelector('.page-loader');

      // Hide loader
      await gsap.to(loader, {
        opacity: 0,
        duration: 0.3
      });

      // Fade in content
      await gsap.from(next.container, {
        opacity: 0,
        duration: 0.5
      });
    }
  }]
});
```

**HTML**:
```html
<div class="page-loader">Loading...</div>
```

**CSS**:
```css
.page-loader {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.5rem;
  opacity: 0;
  z-index: 9998;
  pointer-events: none;
}
```

### Blog with Staggered Content

```javascript
barba.init({
  transitions: [{
    name: 'blog',

    async leave({ current }) {
      const tl = gsap.timeline();

      tl.to(current.container.querySelector('.post-header'), {
        y: -50,
        opacity: 0,
        duration: 0.4
      })
      .to(current.container.querySelectorAll('.post-content > *'), {
        y: -30,
        opacity: 0,
        duration: 0.3,
        stagger: 0.03
      }, '-=0.3')
      .to(current.container, {
        opacity: 0,
        duration: 0.2
      });

      await tl.play();
    },

    async enter({ next }) {
      const tl = gsap.timeline();

      gsap.set(next.container.querySelector('.post-header'), {
        y: 50,
        opacity: 0
      });
      gsap.set(next.container.querySelectorAll('.post-content > *'), {
        y: 30,
        opacity: 0
      });

      tl.to(next.container.querySelector('.post-header'), {
        y: 0,
        opacity: 1,
        duration: 0.6,
        ease: 'power3.out'
      })
      .to(next.container.querySelectorAll('.post-content > *'), {
        y: 0,
        opacity: 1,
        duration: 0.5,
        stagger: 0.05,
        ease: 'power2.out'
      }, '-=0.4');

      await tl.play();
    }
  }]
});
```

### Agency Site with Parallax Layers

```javascript
barba.init({
  transitions: [{
    name: 'parallax',
    sync: true,

    async leave({ current }) {
      const tl = gsap.timeline();

      // Parallax effect - different speeds
      tl.to(current.container.querySelector('.layer-bg'), {
        y: -50,
        opacity: 0,
        duration: 0.8
      }, 0)
      .to(current.container.querySelector('.layer-mid'), {
        y: -100,
        opacity: 0,
        duration: 0.8
      }, 0)
      .to(current.container.querySelector('.layer-front'), {
        y: -150,
        opacity: 0,
        duration: 0.8
      }, 0);

      await tl.play();
    },

    async enter({ next }) {
      const tl = gsap.timeline();

      gsap.set(next.container.querySelectorAll('[class^="layer-"]'), {
        opacity: 0
      });

      tl.from(next.container.querySelector('.layer-bg'), {
        y: 50,
        opacity: 0,
        duration: 0.8
      }, 0)
      .from(next.container.querySelector('.layer-mid'), {
        y: 100,
        opacity: 0,
        duration: 0.8
      }, 0)
      .from(next.container.querySelector('.layer-front'), {
        y: 150,
        opacity: 0,
        duration: 0.8
      }, 0);

      await tl.play();
    }
  }]
});
```

### SaaS Dashboard with Minimal Transition

Fast, subtle transitions for app-like feel:

```javascript
barba.init({
  transitions: [{
    name: 'dashboard',

    async leave({ current }) {
      await gsap.to(current.container, {
        opacity: 0,
        duration: 0.2,
        ease: 'power1.inOut'
      });
    },

    async enter({ next }) {
      gsap.set(next.container, { opacity: 0 });

      await gsap.to(next.container, {
        opacity: 1,
        duration: 0.2,
        ease: 'power1.inOut'
      });
    }
  }]
});
```

---

## Complete Starter Template

Full implementation with multiple transitions:

```javascript
import barba from '@barba/core';
import gsap from 'gsap';

barba.init({
  transitions: [
    // Initial page load
    {
      name: 'initial-load',
      once: async ({ next }) => {
        const loader = document.querySelector('.page-loader');

        await gsap.to(loader, {
          opacity: 0,
          duration: 0.5,
          delay: 0.5
        });

        gsap.set(loader, { display: 'none' });

        await gsap.from(next.container, {
          opacity: 0,
          y: 50,
          duration: 0.8,
          ease: 'power2.out'
        });
      }
    },

    // Same namespace: fast transition
    {
      name: 'same-namespace',
      custom: ({ current, next }) => current.namespace === next.namespace,

      async leave({ current }) {
        await gsap.to(current.container, {
          opacity: 0,
          duration: 0.3
        });
      },

      async enter({ next }) {
        await gsap.from(next.container, {
          opacity: 0,
          duration: 0.3
        });
      }
    },

    // Default: elegant fade
    {
      name: 'default',

      async leave({ current }) {
        await gsap.to(current.container, {
          opacity: 0,
          y: -30,
          duration: 0.5,
          ease: 'power2.in'
        });
      },

      async enter({ next }) {
        await gsap.fromTo(next.container,
          { opacity: 0, y: 30 },
          { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out' }
        );
      }
    }
  ]
});

// Global hooks
barba.hooks.beforeEnter(() => {
  window.scrollTo(0, 0);
});

barba.hooks.after(({ next }) => {
  // Analytics
  if (typeof gtag !== 'undefined') {
    gtag('config', 'GA_MEASUREMENT_ID', {
      page_path: next.url.path
    });
  }

  // Re-initialize scripts
  if (typeof Prism !== 'undefined') {
    Prism.highlightAll();
  }
});
```



===== FILE: plugins/individual/barba-js/agents/barba-js-specialist.md =====

# Barba.js Specialist

## Role

Expert specialist in Barba.js implementation, patterns, and best practices.

## Expertise

- Barba.js core concepts and patterns
- Integration with other libraries and frameworks
- Performance optimization
- Common pitfalls and solutions
- Best practices and conventions

## When to use

Activate this agent when working on:
- Barba.js implementation challenges
- Integration with other technologies
- Performance optimization
- Troubleshooting and debugging
- Architecture decisions

## Approach

1. Understand project requirements and context
2. Apply Barba.js best practices
3. Recommend optimal implementation patterns
4. Identify and solve common issues
5. Provide detailed guidance and examples

## Tools

This agent has access to:
- Barba.js skill knowledge
- Pattern libraries and examples
- Troubleshooting guides
- Integration patterns



===== FILE: plugins/individual/barba-js/commands/project_setup.md =====

# /barba-js-project_setup

Barba.js - Project Setup

## Description

Executes the project_setup script for Barba.js.

## Usage

```bash
/barba-js-project_setup
```

## Implementation

This command runs the `project_setup.py` script from the Barba.js skill, which provides automated assistance for project setup.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/barba-js/commands/transition_generator.md =====

# /barba-js-transition_generator

Barba.js - Transition Generator

## Description

Executes the transition_generator script for Barba.js.

## Usage

```bash
/barba-js-transition_generator
```

## Implementation

This command runs the `transition_generator.py` script from the Barba.js skill, which provides automated assistance for transition generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/barba-js/skills/barba-js/scripts/project_setup.py =====

````py
#!/usr/bin/env python3
"""
Barba.js Project Setup Script

Initializes a new Barba.js project with boilerplate HTML, CSS, and JavaScript files.

Usage:
    ./project_setup.py                       # Interactive mode
    ./project_setup.py --name my-project     # Create project in ./my-project
    ./project_setup.py --name my-project --transition fade
    ./project_setup.py --name my-project --minimal  # Minimal setup without examples

Options:
    --name NAME           Project directory name (required in CLI mode)
    --transition TYPE     Transition type (fade, slide, scale, stagger, curtain)
    --minimal             Create minimal setup without example pages
    --no-install          Skip npm install step
    --output-dir DIR      Parent directory for project (default: current directory)
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def create_package_json(project_name: str) -> str:
    """Generate package.json content."""
    return f'''{{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "Barba.js page transition project",
  "main": "src/main.js",
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "keywords": ["barba", "page-transitions", "gsap"],
  "author": "",
  "license": "MIT",
  "devDependencies": {{
    "@barba/core": "^2.9.7",
    "gsap": "^3.12.5",
    "vite": "^5.0.0"
  }}
}}
'''


def create_index_html(minimal: bool = False) -> str:
    """Generate index.html content."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Home - Barba.js Project</title>
  <meta name="description" content="Home page with Barba.js transitions">
  <link rel="stylesheet" href="/src/style.css">
</head>
<body data-barba="wrapper">
  <header class="site-header">
    <nav>
      <a href="/" class="logo">Barba.js</a>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/about.html">About</a></li>
        <li><a href="/contact.html">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main data-barba="container" data-barba-namespace="home">
    <div class="hero">
      <h1 class="stagger-item">Welcome to Barba.js</h1>
      <p class="stagger-item">Smooth page transitions without full page reloads</p>
      <a href="/about.html" class="btn stagger-item">Learn More</a>
    </div>

    <section class="features">
      <div class="feature stagger-item">
        <h2>Fast</h2>
        <p>No page reloads, instant transitions</p>
      </div>
      <div class="feature stagger-item">
        <h2>Smooth</h2>
        <p>Beautiful GSAP-powered animations</p>
      </div>
      <div class="feature stagger-item">
        <h2>Easy</h2>
        <p>Simple API, powerful results</p>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <p>&copy; 2025 Barba.js Project</p>
  </footer>

  <div class="page-loader">Loading...</div>
  <div class="transition-curtain"></div>

  <script type="module" src="/src/main.js"></script>
</body>
</html>
'''


def create_about_html() -> str:
    """Generate about.html content."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>About - Barba.js Project</title>
  <meta name="description" content="About page with Barba.js transitions">
  <link rel="stylesheet" href="/src/style.css">
</head>
<body data-barba="wrapper">
  <header class="site-header">
    <nav>
      <a href="/" class="logo">Barba.js</a>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/about.html">About</a></li>
        <li><a href="/contact.html">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main data-barba="container" data-barba-namespace="about">
    <div class="content-page">
      <h1 class="stagger-item">About Barba.js</h1>
      <p class="stagger-item">Barba.js is a small (7kb minified and compressed) library that helps you create fluid and smooth transitions between your website's pages.</p>
      <p class="stagger-item">It helps reduce the delay between your pages, minimize browser HTTP requests and enhance your user's web experience.</p>
      <a href="/contact.html" class="btn stagger-item">Get in Touch</a>
    </div>
  </main>

  <footer class="site-footer">
    <p>&copy; 2025 Barba.js Project</p>
  </footer>

  <div class="page-loader">Loading...</div>
  <div class="transition-curtain"></div>

  <script type="module" src="/src/main.js"></script>
</body>
</html>
'''


def create_contact_html() -> str:
    """Generate contact.html content."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Contact - Barba.js Project</title>
  <meta name="description" content="Contact page with Barba.js transitions">
  <link rel="stylesheet" href="/src/style.css">
</head>
<body data-barba="wrapper">
  <header class="site-header">
    <nav>
      <a href="/" class="logo">Barba.js</a>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/about.html">About</a></li>
        <li><a href="/contact.html">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main data-barba="container" data-barba-namespace="contact">
    <div class="content-page">
      <h1 class="stagger-item">Contact Us</h1>
      <p class="stagger-item">Get in touch to learn more about Barba.js.</p>
      <form class="contact-form stagger-item">
        <input type="text" placeholder="Name" required>
        <input type="email" placeholder="Email" required>
        <textarea placeholder="Message" rows="5" required></textarea>
        <button type="submit" class="btn">Send Message</button>
      </form>
    </div>
  </main>

  <footer class="site-footer">
    <p>&copy; 2025 Barba.js Project</p>
  </footer>

  <div class="page-loader">Loading...</div>
  <div class="transition-curtain"></div>

  <script type="module" src="/src/main.js"></script>
</body>
</html>
'''


def create_css() -> str:
    """Generate style.css content."""
    return '''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: #333;
}

/* Header */
.site-header {
  background: #667eea;
  color: white;
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.site-header nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.site-header .logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.site-header ul {
  display: flex;
  list-style: none;
  gap: 2rem;
}

.site-header a {
  color: white;
  text-decoration: none;
  transition: opacity 0.3s;
}

.site-header a:hover {
  opacity: 0.8;
}

/* Container */
[data-barba="container"] {
  min-height: calc(100vh - 60px - 80px);
}

/* Hero */
.hero {
  padding: 4rem 2rem;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.25rem;
  margin-bottom: 2rem;
}

/* Features */
.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  padding: 4rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.feature {
  padding: 2rem;
  background: #f5f5f5;
  border-radius: 8px;
  text-align: center;
}

.feature h2 {
  margin-bottom: 1rem;
  color: #667eea;
}

/* Content Page */
.content-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 4rem 2rem;
}

.content-page h1 {
  margin-bottom: 2rem;
  color: #667eea;
}

.content-page p {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

/* Contact Form */
.contact-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 2rem;
}

.contact-form input,
.contact-form textarea {
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.contact-form input:focus,
.contact-form textarea:focus {
  outline: none;
  border-color: #667eea;
}

/* Button */
.btn {
  display: inline-block;
  padding: 0.75rem 2rem;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.btn:hover {
  background: #5568d3;
}

/* Footer */
.site-footer {
  background: #333;
  color: white;
  text-align: center;
  padding: 2rem;
}

/* Page Loader */
.page-loader {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.5rem;
  color: #667eea;
  opacity: 0;
  z-index: 9998;
  pointer-events: none;
}

/* Transition Curtain */
.transition-curtain {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 9999;
  pointer-events: none;
  transform: translateY(-100%);
}

/* Responsive */
@media (max-width: 768px) {
  .hero h1 {
    font-size: 2rem;
  }

  .hero p {
    font-size: 1rem;
  }

  .site-header ul {
    gap: 1rem;
  }
}
'''


def create_main_js(transition_type: str = 'fade') -> str:
    """Generate main.js content with specified transition."""
    transitions_code = {
        'fade': '''    {
      name: 'fade',
      async leave({ current }) {
        await gsap.to(current.container, {
          opacity: 0,
          duration: 0.5,
          ease: 'power2.inOut'
        });
      },
      async enter({ next }) {
        gsap.set(next.container, { opacity: 0 });
        await gsap.to(next.container, {
          opacity: 1,
          duration: 0.5,
          ease: 'power2.inOut'
        });
      }
    }''',

        'slide': '''    {
      name: 'slide',
      sync: true,
      leave({ current }) {
        return gsap.to(current.container, {
          x: '-100%',
          duration: 0.7,
          ease: 'power3.inOut'
        });
      },
      enter({ next }) {
        gsap.set(next.container, { x: '100%' });
        return gsap.to(next.container, {
          x: '0%',
          duration: 0.7,
          ease: 'power3.inOut'
        });
      }
    }''',

        'scale': '''    {
      name: 'scale-fade',
      async leave({ current }) {
        await gsap.to(current.container, {
          opacity: 0,
          scale: 0.95,
          duration: 0.5,
          ease: 'power2.in'
        });
      },
      async enter({ next }) {
        await gsap.fromTo(next.container,
          { opacity: 0, scale: 1.05 },
          { opacity: 1, scale: 1, duration: 0.6, ease: 'power2.out' }
        );
      }
    }''',

        'stagger': '''    {
      name: 'stagger',
      async leave({ current }) {
        const tl = gsap.timeline();
        tl.to(current.container.querySelectorAll('.stagger-item'), {
          y: -50,
          opacity: 0,
          duration: 0.5,
          stagger: 0.05,
          ease: 'power2.in'
        })
        .to(current.container, {
          opacity: 0,
          duration: 0.3
        }, '-=0.2');
        await tl.play();
      },
      async enter({ next }) {
        const tl = gsap.timeline();
        gsap.set(next.container.querySelectorAll('.stagger-item'), {
          y: 50,
          opacity: 0
        });
        tl.to(next.container.querySelectorAll('.stagger-item'), {
          y: 0,
          opacity: 1,
          duration: 0.6,
          stagger: 0.05,
          ease: 'power2.out'
        });
        await tl.play();
      }
    }''',

        'curtain': '''    {
      name: 'curtain',
      async leave({ current }) {
        const curtain = document.querySelector('.transition-curtain');
        await gsap.fromTo(curtain,
          { yPercent: -100 },
          { yPercent: 0, duration: 0.6, ease: 'power2.inOut' }
        );
      },
      async enter({ next }) {
        const curtain = document.querySelector('.transition-curtain');
        await gsap.to(curtain, {
          yPercent: 100,
          duration: 0.6,
          ease: 'power2.inOut'
        });
      }
    }'''
    }

    transition_code = transitions_code.get(transition_type, transitions_code['fade'])

    return f'''import barba from '@barba/core';
import gsap from 'gsap';

// Initialize Barba.js
barba.init({{
  transitions: [
{transition_code}
  ]
}});

// Global hooks
barba.hooks.beforeEnter(() => {{
  // Reset scroll position
  window.scrollTo(0, 0);
}});

barba.hooks.before(() => {{
  // Show loader
  gsap.to('.page-loader', {{ opacity: 1, duration: 0.3 }});
}});

barba.hooks.after(() => {{
  // Hide loader
  gsap.to('.page-loader', {{ opacity: 0, duration: 0.3 }});
}});

// Contact form handler (demo)
document.addEventListener('submit', (e) => {{
  if (e.target.classList.contains('contact-form')) {{
    e.preventDefault();
    alert('Form submission would happen here!');
  }}
}});
'''


def create_vite_config() -> str:
    """Generate vite.config.js content."""
    return '''import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: 'index.html',
        about: 'about.html',
        contact: 'contact.html'
      }
    }
  }
});
'''


def create_readme(project_name: str) -> str:
    """Generate README.md content."""
    return f'''# {project_name}

Barba.js page transition project with GSAP animations.

## Setup

Install dependencies:

```bash
npm install
```

## Development

Start development server:

```bash
npm run dev
```

Open http://localhost:5173 in your browser.

## Build

Build for production:

```bash
npm run build
```

Output will be in `dist/` directory.

## Preview Production Build

```bash
npm run preview
```

## Project Structure

```
{project_name}/
├── index.html              # Home page
├── about.html              # About page
├── contact.html            # Contact page
├── src/
│   ├── main.js            # Barba.js initialization
│   └── style.css          # Global styles
├── package.json
├── vite.config.js
└── README.md
```

## Customization

### Change Transition

Edit `src/main.js` and modify the transition in `barba.init()`.

See available transition types in the Barba.js documentation.

### Add More Pages

1. Create new HTML file (e.g., `services.html`)
2. Add `data-barba="container"` to main content
3. Add `data-barba-namespace="services"` to identify the page
4. Add link to navigation
5. Update `vite.config.js` to include the new page in build

## Resources

- [Barba.js Documentation](https://barba.js.org)
- [GSAP Documentation](https://greensock.com/docs/)
- [Vite Documentation](https://vitejs.dev)
'''


def create_project(
    name: str,
    output_dir: str = '.',
    transition: str = 'fade',
    minimal: bool = False,
    no_install: bool = False
) -> None:
    """Create Barba.js project structure."""
    project_path = Path(output_dir) / name

    # Check if directory exists
    if project_path.exists():
        print(f"❌ Error: Directory '{project_path}' already exists")
        sys.exit(1)

    print(f"🎬 Creating Barba.js project: {name}")
    print(f"📁 Location: {project_path}")
    print()

    # Create directories
    project_path.mkdir(parents=True)
    (project_path / 'src').mkdir()

    print("✅ Created project directory")

    # Create files
    files = {
        'package.json': create_package_json(name),
        'index.html': create_index_html(minimal),
        'src/style.css': create_css(),
        'src/main.js': create_main_js(transition),
        'vite.config.js': create_vite_config(),
        'README.md': create_readme(name)
    }

    if not minimal:
        files['about.html'] = create_about_html()
        files['contact.html'] = create_contact_html()

    for file_path, content in files.items():
        full_path = project_path / file_path
        full_path.write_text(content)
        print(f"✅ Created {file_path}")

    print()
    print("=" * 50)
    print("✅ Project created successfully!")
    print()
    print("Next steps:")
    print(f"  1. cd {name}")

    if not no_install:
        print("  2. Running npm install...")
        print()
        try:
            subprocess.run(['npm', 'install'], cwd=project_path, check=True)
            print()
            print("✅ Dependencies installed!")
            print()
            print("To start development:")
            print(f"  cd {name}")
            print("  npm run dev")
        except subprocess.CalledProcessError:
            print("❌ npm install failed. Run manually:")
            print(f"  cd {name}")
            print("  npm install")
            print("  npm run dev")
        except FileNotFoundError:
            print("⚠️  npm not found. Install dependencies manually:")
            print(f"  cd {name}")
            print("  npm install")
            print("  npm run dev")
    else:
        print("  2. npm install")
        print("  3. npm run dev")

    print()


def interactive_mode():
    """Run setup in interactive mode with prompts."""
    print("🎬 Barba.js Project Setup")
    print("=" * 50)
    print()

    # Project name
    name = input("Project name: ").strip()
    if not name:
        print("❌ Project name is required")
        sys.exit(1)

    # Transition type
    print()
    print("Available transition types:")
    print("  1. fade (simple fade)")
    print("  2. slide (horizontal slide)")
    print("  3. scale (zoom with fade)")
    print("  4. stagger (staggered elements)")
    print("  5. curtain (curtain overlay)")
    print()
    transition_choice = input("Select transition (1-5, default: 1): ").strip()

    transitions = ['fade', 'slide', 'scale', 'stagger', 'curtain']
    try:
        transition_idx = int(transition_choice) - 1 if transition_choice else 0
        transition = transitions[transition_idx]
    except (ValueError, IndexError):
        transition = 'fade'

    # Minimal setup
    print()
    minimal_input = input("Minimal setup? (no example pages) [y/N]: ").strip().lower()
    minimal = minimal_input in ['y', 'yes']

    # Install dependencies
    print()
    no_install_input = input("Skip npm install? [y/N]: ").strip().lower()
    no_install = no_install_input in ['y', 'yes']

    print()
    print("=" * 50)
    print()

    # Create project
    create_project(name, '.', transition, minimal, no_install)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Initialize a new Barba.js project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--name',
        help='Project directory name'
    )

    parser.add_argument(
        '--transition',
        choices=['fade', 'slide', 'scale', 'stagger', 'curtain'],
        default='fade',
        help='Transition type (default: fade)'
    )

    parser.add_argument(
        '--minimal',
        action='store_true',
        help='Create minimal setup without example pages'
    )

    parser.add_argument(
        '--no-install',
        action='store_true',
        help='Skip npm install step'
    )

    parser.add_argument(
        '--output-dir',
        default='.',
        help='Parent directory for project (default: current directory)'
    )

    args = parser.parse_args()

    # Interactive mode if no name specified
    if not args.name:
        interactive_mode()
        return

    # CLI mode
    create_project(
        args.name,
        args.output_dir,
        args.transition,
        args.minimal,
        args.no_install
    )


if __name__ == '__main__':
    main()

````


===== FILE: plugins/individual/barba-js/skills/barba-js/scripts/transition_generator.py =====

```py
#!/usr/bin/env python3
"""
Barba.js Transition Generator

Generates boilerplate code for Barba.js page transitions with GSAP animations.

Usage:
    ./transition_generator.py                          # Interactive mode
    ./transition_generator.py --type fade              # Generate fade transition
    ./transition_generator.py --type slide --sync      # Generate sync slide transition
    ./transition_generator.py --type custom --name my-transition

Transition Types:
    - fade: Simple fade in/out
    - crossfade: Simultaneous fade (sync mode)
    - slide: Horizontal slide
    - slide-vertical: Vertical slide
    - scale: Zoom with fade
    - stagger: Staggered element animation
    - curtain: Curtain overlay effect
    - custom: Empty template for custom transitions

Options:
    --type TYPE        Transition type (required in CLI mode)
    --name NAME        Custom transition name (default: based on type)
    --sync             Enable sync mode (leave and enter simultaneously)
    --duration SECS    Animation duration in seconds (default: 0.5)
    --ease EASE        GSAP easing (default: power2.inOut)
    --output FILE      Output file path (default: stdout)
"""

import sys
import argparse
from typing import Dict, Optional


TRANSITION_TEMPLATES = {
    'fade': {
        'name': 'fade',
        'sync': False,
        'code': '''{{
  name: '{name}',

  async leave({{ current }}) {{
    await gsap.to(current.container, {{
      opacity: 0,
      duration: {duration},
      ease: '{ease}'
    }});
  }},

  async enter({{ next }}) {{
    gsap.set(next.container, {{ opacity: 0 }});

    await gsap.to(next.container, {{
      opacity: 1,
      duration: {duration},
      ease: '{ease}'
    }});
  }}
}}'''
    },

    'crossfade': {
        'name': 'crossfade',
        'sync': True,
        'code': '''{{
  name: '{name}',
  sync: true,

  leave({{ current }}) {{
    return gsap.to(current.container, {{
      opacity: 0,
      duration: {duration},
      ease: '{ease}'
    }});
  }},

  enter({{ next }}) {{
    return gsap.from(next.container, {{
      opacity: 0,
      duration: {duration},
      ease: '{ease}'
    }});
  }}
}}'''
    },

    'slide': {
        'name': 'slide-horizontal',
        'sync': True,
        'code': '''{{
  name: '{name}',
  sync: true,

  leave({{ current }}) {{
    return gsap.to(current.container, {{
      x: '-100%',
      duration: {duration},
      ease: '{ease}'
    }});
  }},

  enter({{ next }}) {{
    gsap.set(next.container, {{ x: '100%' }});

    return gsap.to(next.container, {{
      x: '0%',
      duration: {duration},
      ease: '{ease}'
    }});
  }}
}}

/* CSS Required:
[data-barba="wrapper"] {{
  position: relative;
  overflow: hidden;
}}

[data-barba="container"] {{
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}}
*/'''
    },

    'slide-vertical': {
        'name': 'slide-vertical',
        'sync': True,
        'code': '''{{
  name: '{name}',
  sync: true,

  leave({{ current }}) {{
    return gsap.to(current.container, {{
      y: '-100%',
      duration: {duration},
      ease: '{ease}'
    }});
  }},

  enter({{ next }}) {{
    gsap.set(next.container, {{ y: '100%' }});

    return gsap.to(next.container, {{
      y: '0%',
      duration: {duration},
      ease: '{ease}'
    }});
  }}
}}

/* CSS Required:
[data-barba="wrapper"] {{
  position: relative;
  overflow: hidden;
}}

[data-barba="container"] {{
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}}
*/'''
    },

    'scale': {
        'name': 'scale-fade',
        'sync': False,
        'code': '''{{
  name: '{name}',

  async leave({{ current }}) {{
    await gsap.to(current.container, {{
      opacity: 0,
      scale: 0.95,
      duration: {duration},
      ease: 'power2.in'
    }});
  }},

  async enter({{ next }}) {{
    await gsap.fromTo(next.container,
      {{
        opacity: 0,
        scale: 1.05
      }},
      {{
        opacity: 1,
        scale: 1,
        duration: {duration},
        ease: 'power2.out'
      }}
    );
  }}
}}'''
    },

    'stagger': {
        'name': 'stagger',
        'sync': False,
        'code': '''{{
  name: '{name}',

  async leave({{ current }}) {{
    const tl = gsap.timeline();

    tl.to(current.container.querySelectorAll('.stagger-item'), {{
      y: -50,
      opacity: 0,
      duration: {duration},
      stagger: 0.05,
      ease: 'power2.in'
    }})
    .to(current.container, {{
      opacity: 0,
      duration: 0.3
    }}, '-=0.2');

    await tl.play();
  }},

  async enter({{ next }}) {{
    const tl = gsap.timeline();

    gsap.set(next.container.querySelectorAll('.stagger-item'), {{
      y: 50,
      opacity: 0
    }});

    tl.to(next.container.querySelectorAll('.stagger-item'), {{
      y: 0,
      opacity: 1,
      duration: {duration},
      stagger: 0.05,
      ease: 'power2.out'
    }});

    await tl.play();
  }}
}}

/* HTML Required: Add class="stagger-item" to elements you want to animate */'''
    },

    'curtain': {
        'name': 'curtain',
        'sync': False,
        'code': '''{{
  name: '{name}',

  async leave({{ current }}) {{
    const curtain = document.querySelector('.transition-curtain');

    await gsap.fromTo(curtain,
      {{ yPercent: -100 }},
      {{
        yPercent: 0,
        duration: {duration},
        ease: '{ease}'
      }}
    );
  }},

  async enter({{ next }}) {{
    const curtain = document.querySelector('.transition-curtain');

    await gsap.to(curtain, {{
      yPercent: 100,
      duration: {duration},
      ease: '{ease}'
    }});
  }}
}}

/* HTML Required:
<div class="transition-curtain"></div>
*/

/* CSS Required:
.transition-curtain {{
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 9999;
  pointer-events: none;
  transform: translateY(-100%);
}}
*/'''
    },

    'custom': {
        'name': 'custom-transition',
        'sync': False,
        'code': '''{{
  name: '{name}',

  async leave({{ current }}) {{
    // TODO: Add your leave animation here
    await gsap.to(current.container, {{
      opacity: 0,
      duration: {duration}
    }});
  }},

  async enter({{ next }}) {{
    // TODO: Add your enter animation here
    await gsap.from(next.container, {{
      opacity: 0,
      duration: {duration}
    }});
  }}
}}'''
    }
}


def generate_transition(
    transition_type: str,
    name: Optional[str] = None,
    sync: Optional[bool] = None,
    duration: float = 0.5,
    ease: str = 'power2.inOut'
) -> str:
    """Generate transition code based on type and options."""
    if transition_type not in TRANSITION_TEMPLATES:
        raise ValueError(f"Unknown transition type: {transition_type}. "
                        f"Available types: {', '.join(TRANSITION_TEMPLATES.keys())}")

    template = TRANSITION_TEMPLATES[transition_type]

    # Use custom name if provided, otherwise use template default
    transition_name = name if name else template['name']

    # Use custom sync if provided, otherwise use template default
    # (but only if the template supports it)
    use_sync = sync if sync is not None else template.get('sync', False)

    # Format the template
    code = template['code'].format(
        name=transition_name,
        duration=duration,
        ease=ease
    )

    # Override sync mode if explicitly requested
    if sync is not None and sync != template.get('sync', False):
        if sync:
            # Convert to sync mode
            code = code.replace('async leave', 'leave')
            code = code.replace('async enter', 'enter')
            code = code.replace('await gsap.to', 'return gsap.to')
            code = code.replace('await gsap.from', 'return gsap.from')
            if 'sync: true' not in code:
                code = code.replace("name: '" + transition_name + "',",
                                  "name: '" + transition_name + "',\n  sync: true,")
        else:
            # Convert to async mode
            code = code.replace('leave({', 'async leave({')
            code = code.replace('enter({', 'async enter({')
            code = code.replace('return gsap.to', 'await gsap.to')
            code = code.replace('return gsap.from', 'await gsap.from')
            code = code.replace('\n  sync: true,', '')

    return code


def interactive_mode():
    """Run generator in interactive mode with prompts."""
    print("🎬 Barba.js Transition Generator")
    print("=" * 50)
    print()

    # Choose transition type
    print("Available transition types:")
    for i, (key, value) in enumerate(TRANSITION_TEMPLATES.items(), 1):
        sync_indicator = " (sync)" if value.get('sync') else ""
        print(f"  {i}. {key}{sync_indicator}")

    print()
    choice = input("Select transition type (1-{}): ".format(len(TRANSITION_TEMPLATES)))

    try:
        choice_idx = int(choice) - 1
        transition_type = list(TRANSITION_TEMPLATES.keys())[choice_idx]
    except (ValueError, IndexError):
        print("❌ Invalid choice. Using 'fade' as default.")
        transition_type = 'fade'

    # Custom name
    default_name = TRANSITION_TEMPLATES[transition_type]['name']
    name = input(f"Transition name (default: {default_name}): ").strip()
    if not name:
        name = default_name

    # Sync mode
    sync_default = TRANSITION_TEMPLATES[transition_type].get('sync', False)
    sync_input = input(f"Sync mode? [y/N] (default: {'y' if sync_default else 'n'}): ").strip().lower()
    if sync_input in ['y', 'yes']:
        sync = True
    elif sync_input in ['n', 'no']:
        sync = False
    else:
        sync = sync_default

    # Duration
    duration_input = input("Animation duration in seconds (default: 0.5): ").strip()
    try:
        duration = float(duration_input) if duration_input else 0.5
    except ValueError:
        print("❌ Invalid duration. Using 0.5s as default.")
        duration = 0.5

    # Easing
    print()
    print("Common GSAP easings:")
    print("  - power2.inOut (smooth acceleration/deceleration)")
    print("  - power2.in (accelerate)")
    print("  - power2.out (decelerate)")
    print("  - power3.inOut (stronger curve)")
    print("  - back.out(1.7) (overshoot)")
    print("  - elastic.out(1, 0.3) (elastic bounce)")
    ease = input("Easing function (default: power2.inOut): ").strip()
    if not ease:
        ease = 'power2.inOut'

    print()
    print("=" * 50)
    print("Generating transition...")
    print()

    # Generate code
    code = generate_transition(transition_type, name, sync, duration, ease)

    # Output
    print(code)
    print()
    print("✅ Transition generated successfully!")
    print()
    print("To use this transition:")
    print("1. Import Barba.js and GSAP:")
    print("   import barba from '@barba/core';")
    print("   import gsap from 'gsap';")
    print()
    print("2. Add the transition to your Barba.init() call:")
    print("   barba.init({")
    print("     transitions: [")
    print("       // ... paste the generated code here")
    print("     ]")
    print("   });")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate Barba.js transition boilerplate code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--type',
        choices=list(TRANSITION_TEMPLATES.keys()),
        help='Transition type'
    )

    parser.add_argument(
        '--name',
        help='Custom transition name'
    )

    parser.add_argument(
        '--sync',
        action='store_true',
        help='Enable sync mode (leave and enter simultaneously)'
    )

    parser.add_argument(
        '--duration',
        type=float,
        default=0.5,
        help='Animation duration in seconds (default: 0.5)'
    )

    parser.add_argument(
        '--ease',
        default='power2.inOut',
        help='GSAP easing function (default: power2.inOut)'
    )

    parser.add_argument(
        '--output',
        help='Output file path (default: stdout)'
    )

    args = parser.parse_args()

    # Interactive mode if no type specified
    if not args.type:
        interactive_mode()
        return

    # CLI mode
    try:
        code = generate_transition(
            args.type,
            args.name,
            args.sync,
            args.duration,
            args.ease
        )

        if args.output:
            with open(args.output, 'w') as f:
                f.write(code)
            print(f"✅ Transition written to {args.output}")
        else:
            print(code)

    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/barba-js/skills/barba-js/assets/README.md =====

# Barba.js Assets

This directory contains information about assets and starter templates for Barba.js projects.

## Starter Templates

Complete Barba.js starter templates are generated automatically by the `project_setup.py` script.

### Usage

Run the project setup script to generate a complete Barba.js project:

```bash
../scripts/project_setup.py
```

Or in CLI mode:

```bash
../scripts/project_setup.py --name my-project --transition fade
```

### Generated Project Structure

The script creates a complete project with:

```
my-project/
├── index.html              # Home page with Barba structure
├── about.html              # Example about page
├── contact.html            # Example contact page
├── src/
│   ├── main.js            # Barba.js initialization with transitions
│   └── style.css          # Complete styling with transition support
├── package.json            # Dependencies (@barba/core, gsap, vite)
├── vite.config.js          # Vite configuration for multi-page app
└── README.md               # Project-specific documentation
```

### Available Transition Types

The generated project includes one of these transitions:

1. **fade** - Simple fade in/out
2. **slide** - Horizontal slide transition
3. **scale** - Zoom with fade effect
4. **stagger** - Staggered element animations
5. **curtain** - Curtain overlay effect

### Features

Generated projects include:

- Complete HTML structure with proper `data-barba` attributes
- Responsive navigation that persists across page transitions
- GSAP-powered animations
- Loading indicator
- Transition curtain element
- Mobile-responsive styling
- Vite dev server and build setup
- Example pages demonstrating namespace-based routing

### Customization

After generating a project:

1. Modify transitions in `src/main.js`
2. Add custom styles in `src/style.css`
3. Create additional pages following the same structure
4. Update `vite.config.js` to include new pages in build

### Example HTML Structure

All generated pages follow this structure:

```html
<body data-barba="wrapper">
  <!-- Persistent header (outside container) -->
  <header class="site-header">
    <nav><!-- Navigation links --></nav>
  </header>

  <!-- Dynamic content (inside container) -->
  <main data-barba="container" data-barba-namespace="page-name">
    <!-- Page content that transitions -->
  </main>

  <!-- Persistent footer (outside container) -->
  <footer class="site-footer"><!-- Footer content --></footer>

  <!-- Transition elements -->
  <div class="page-loader">Loading...</div>
  <div class="transition-curtain"></div>

  <script type="module" src="/src/main.js"></script>
</body>
```

### Development Workflow

1. Generate project: `../scripts/project_setup.py --name my-site`
2. Navigate to project: `cd my-site`
3. Install dependencies: `npm install` (auto-run unless `--no-install`)
4. Start dev server: `npm run dev`
5. Open browser: `http://localhost:5173`
6. Build for production: `npm run build`

### Additional Examples

For custom transition code snippets, use the transition generator:

```bash
../scripts/transition_generator.py
```

This generates just the JavaScript transition code that you can copy into your project.

## Manual Setup (Without Scripts)

If you prefer to set up manually:

### 1. Install Dependencies

```bash
npm install --save-dev @barba/core gsap
```

### 2. Create HTML Structure

Add Barba attributes to your HTML:

```html
<body data-barba="wrapper">
  <main data-barba="container" data-barba-namespace="home">
    <!-- Your content -->
  </main>
</body>
```

### 3. Initialize Barba

Create JavaScript file:

```javascript
import barba from '@barba/core';
import gsap from 'gsap';

barba.init({
  transitions: [{
    name: 'fade',
    async leave({ current }) {
      await gsap.to(current.container, { opacity: 0 });
    },
    async enter({ next }) {
      await gsap.from(next.container, { opacity: 0 });
    }
  }]
});
```

### 4. Add to HTML

```html
<script type="module" src="/path/to/your/script.js"></script>
```

## Resources

- **SKILL.md** - Complete Barba.js guide with patterns and examples
- **references/api_reference.md** - Full API documentation
- **references/hooks_guide.md** - Lifecycle hooks reference
- **references/gsap_integration.md** - GSAP animation patterns
- **references/transition_patterns.md** - Ready-to-use transition code
- **scripts/transition_generator.py** - Generate custom transition code
- **scripts/project_setup.py** - Generate complete starter projects



# Skill: scroll-reveal-libraries


===== FILE: plugins/individual/scroll-reveal-libraries/skills/scroll-reveal-libraries/SKILL.md =====

---
name: scroll-reveal-libraries
description: Simple scroll-triggered reveal animations using AOS (Animate On Scroll). Use this skill when building marketing pages, landing pages, or content-heavy sites requiring basic fade/slide effects without complex animation orchestration. Triggers on tasks involving scroll animations, scroll-triggered reveals, AOS, simple animations, or basic scroll effects. Alternative to GSAP ScrollTrigger and Locomotive Scroll for simpler use cases. Compare with motion-framer for React-specific animations.
---

# Scroll Reveal Libraries

## Overview

This skill covers AOS (Animate On Scroll), a lightweight CSS-driven library for scroll-triggered animations. AOS excels at simple fade, slide, and zoom effects activated when elements enter the viewport.

**Key Features**:
- **Minimal Setup**: Single JavaScript file + CSS
- **Data Attribute API**: Configure animations in HTML
- **Performance**: CSS-driven, GPU-accelerated animations
- **50+ Built-in Animations**: Fades, slides, zooms, flips
- **Framework Agnostic**: Works with vanilla JS, React, Vue, etc.

**When to Use**:
- Marketing/landing pages with simple scroll effects
- Content-heavy sites (blogs, documentation)
- Quick prototypes requiring scroll animations
- Projects where GSAP/Framer Motion complexity isn't needed

**When NOT to Use**:
- Complex animation timelines or orchestration → Use GSAP ScrollTrigger
- Physics-based animations → Use React Spring or Framer Motion
- Precise scroll-synced animations → Use GSAP ScrollTrigger
- Heavy interactive animations → Use Framer Motion

## Core Concepts

### Installation

**CDN (Quickest)**:
```html
<head>
  <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
</head>
<body>
  <!-- Content with data-aos attributes -->

  <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
  <script>
    AOS.init();
  </script>
</body>
```

**NPM/Yarn (Recommended)**:
```bash
npm install aos@next
# or
yarn add aos@next
```

```javascript
import AOS from 'aos';
import 'aos/dist/aos.css';

AOS.init();
```

### Basic Usage

Apply animations using the `data-aos` attribute:

```html
<!-- Fade in -->
<div data-aos="fade-in">Content</div>

<!-- Fade up -->
<div data-aos="fade-up">Content</div>

<!-- Slide from right -->
<div data-aos="slide-left">Content</div>

<!-- Zoom in -->
<div data-aos="zoom-in">Content</div>
```

### Configuration Options

**Global Configuration**:
```javascript
AOS.init({
  // Animation settings
  duration: 800,  // Animation duration (ms): 0-3000
  delay: 0,       // Delay before animation (ms): 0-3000
  offset: 120,    // Offset from trigger point (px)
  easing: 'ease', // Easing function
  once: false,    // Animate only once (true) or every time (false)
  mirror: false,  // Animate out when scrolling past

  // Placement
  anchorPlacement: 'top-bottom', // Which position triggers animation

  // Performance
  disable: false,                // Disable on mobile/tablet
  startEvent: 'DOMContentLoaded', // Initialization event
  debounceDelay: 50,             // Window resize debounce
  throttleDelay: 99              // Scroll throttle
});
```

**Per-Element Overrides**:
```html
<div
  data-aos="fade-up"
  data-aos-duration="1000"
  data-aos-delay="200"
  data-aos-offset="50"
  data-aos-easing="ease-in-out"
  data-aos-once="true"
  data-aos-mirror="true"
  data-aos-anchor-placement="center-bottom"
>
  Custom configured element
</div>
```

## Common Patterns

### 1. Landing Page Hero Section

```html
<section class="hero">
  <!-- Staggered heading words -->
  <h1
    data-aos="fade-down"
    data-aos-duration="800"
  >
    Welcome to the Future
  </h1>

  <!-- Delayed subheading -->
  <p
    data-aos="fade-up"
    data-aos-delay="200"
    data-aos-duration="600"
  >
    Transform your ideas into reality
  </p>

  <!-- CTA button -->
  <button
    data-aos="zoom-in"
    data-aos-delay="400"
    data-aos-duration="500"
  >
    Get Started
  </button>
</section>
```

### 2. Feature Cards Grid

```html
<div class="features-grid">
  <!-- Stagger cards with increasing delays -->
  <div
    class="feature-card"
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="0"
  >
    <h3>Feature 1</h3>
    <p>Description...</p>
  </div>

  <div
    class="feature-card"
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="100"
  >
    <h3>Feature 2</h3>
    <p>Description...</p>
  </div>

  <div
    class="feature-card"
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="200"
  >
    <h3>Feature 3</h3>
    <p>Description...</p>
  </div>
</div>
```

### 3. Alternating Content Sections

```html
<!-- Content from left -->
<div class="section">
  <div
    class="content"
    data-aos="slide-right"
    data-aos-duration="800"
  >
    <h2>Section Title</h2>
    <p>Content slides in from left...</p>
  </div>
  <img
    src="image1.jpg"
    data-aos="fade-left"
    data-aos-delay="200"
  />
</div>

<!-- Content from right -->
<div class="section reverse">
  <img
    src="image2.jpg"
    data-aos="fade-right"
  />
  <div
    class="content"
    data-aos="slide-left"
    data-aos-duration="800"
    data-aos-delay="200"
  >
    <h2>Section Title</h2>
    <p>Content slides in from right...</p>
  </div>
</div>
```

### 4. Scroll-Triggered Testimonials

```html
<div class="testimonials">
  <div
    class="testimonial"
    data-aos="zoom-in"
    data-aos-duration="500"
  >
    <blockquote>"Amazing product!"</blockquote>
    <cite>- John Doe</cite>
  </div>

  <div
    class="testimonial"
    data-aos="zoom-in"
    data-aos-duration="500"
    data-aos-delay="100"
  >
    <blockquote>"Exceeded expectations"</blockquote>
    <cite>- Jane Smith</cite>
  </div>
</div>
```

### 5. Custom Anchor Triggers

Trigger animations based on a different element's scroll position:

```html
<!-- Fixed sidebar animates based on main content scroll -->
<div class="main-content">
  <div id="trigger-point" data-aos-id="sidebar-trigger">
    <!-- Content -->
  </div>
</div>

<aside
  class="sidebar"
  data-aos="fade-left"
  data-aos-anchor="#trigger-point"
>
  Sidebar content
</aside>
```

### 6. Sequential Animation Chain

```html
<div class="animation-sequence">
  <!-- Step 1: Heading -->
  <h2
    data-aos="fade-down"
    data-aos-duration="600"
    data-aos-delay="0"
  >
    Our Process
  </h2>

  <!-- Step 2: Description -->
  <p
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="200"
  >
    Follow these simple steps
  </p>

  <!-- Step 3-5: Process cards -->
  <div
    class="process-step"
    data-aos="flip-left"
    data-aos-delay="400"
  >
    Step 1
  </div>

  <div
    class="process-step"
    data-aos="flip-left"
    data-aos-delay="600"
  >
    Step 2
  </div>

  <div
    class="process-step"
    data-aos="flip-left"
    data-aos-delay="800"
  >
    Step 3
  </div>
</div>
```

### 7. Image Gallery with Zoom Effects

```html
<div class="gallery">
  <img
    src="photo1.jpg"
    data-aos="zoom-in-up"
    data-aos-duration="800"
  />
  <img
    src="photo2.jpg"
    data-aos="zoom-in-up"
    data-aos-duration="800"
    data-aos-delay="100"
  />
  <img
    src="photo3.jpg"
    data-aos="zoom-in-up"
    data-aos-duration="800"
    data-aos-delay="200"
  />
</div>
```

## Integration Patterns

### React Integration

**Basic Setup**:
```jsx
import { useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';

function App() {
  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true,
      offset: 100
    });
  }, []);

  return (
    <div>
      <h1 data-aos="fade-down">Welcome</h1>
      <p data-aos="fade-up">Content here</p>
    </div>
  );
}
```

**Refreshing on Route Changes**:
```jsx
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import AOS from 'aos';

function App() {
  const location = useLocation();

  useEffect(() => {
    AOS.init({ duration: 800 });
  }, []);

  // Refresh AOS on route change
  useEffect(() => {
    AOS.refresh();
  }, [location]);

  return <Routes>{/* routes */}</Routes>;
}
```

**Dynamic Content Updates**:
```jsx
import { useState, useEffect } from 'react';
import AOS from 'aos';

function DynamicList() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    AOS.init();
  }, []);

  const addItem = () => {
    setItems([...items, { id: Date.now(), text: 'New Item' }]);

    // Refresh AOS to detect new elements
    setTimeout(() => AOS.refresh(), 50);
  };

  return (
    <div>
      <button onClick={addItem}>Add Item</button>
      <ul>
        {items.map((item) => (
          <li key={item.id} data-aos="fade-in">
            {item.text}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**Component Wrapper Pattern**:
```jsx
import AOS from 'aos';
import 'aos/dist/aos.css';

function AnimatedSection({ children, animation = "fade-up", delay = 0, ...props }) {
  return (
    <div
      data-aos={animation}
      data-aos-delay={delay}
      {...props}
    >
      {children}
    </div>
  );
}

// Usage
<AnimatedSection animation="slide-right" delay={200}>
  <h2>Animated Content</h2>
</AnimatedSection>
```

### Vue.js Integration

```vue
<template>
  <div>
    <h1 data-aos="fade-down">Vue + AOS</h1>
    <div
      v-for="(item, index) in items"
      :key="item.id"
      data-aos="fade-up"
      :data-aos-delay="index * 100"
    >
      {{ item.text }}
    </div>
  </div>
</template>

<script>
import AOS from 'aos';
import 'aos/dist/aos.css';

export default {
  mounted() {
    AOS.init({ duration: 800 });
  },
  updated() {
    // Refresh when component updates
    this.$nextTick(() => {
      AOS.refresh();
    });
  },
  data() {
    return {
      items: [/*...*/]
    };
  }
};
</script>
```

### Next.js Integration

```jsx
// pages/_app.js
import { useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true
    });
  }, []);

  return <Component {...pageProps} />;
}

export default MyApp;
```

```jsx
// pages/index.js
export default function Home() {
  return (
    <main>
      <h1 data-aos="fade-down">Next.js + AOS</h1>
      <p data-aos="fade-up">Server-side rendered content with animations</p>
    </main>
  );
}
```

## Performance Optimization

### 1. Disable on Mobile Devices

```javascript
AOS.init({
  disable: 'mobile', // Disable on mobile
  // Or use function for custom logic
  disable: function() {
    return window.innerWidth < 768;
  }
});
```

### 2. Use Once for Better Performance

```javascript
AOS.init({
  once: true, // Animate only once (better performance)
  mirror: false // Don't animate out
});
```

### 3. Optimize Throttle and Debounce

```javascript
AOS.init({
  throttleDelay: 99,  // Scroll event throttle (default)
  debounceDelay: 50   // Resize event debounce (default)
});
```

### 4. Disable Mutation Observer for Static Content

```javascript
AOS.init({
  disableMutationObserver: true // Disable for fully static content
});
```

### 5. Reduce Animation Complexity

```html
<!-- Simpler animations perform better -->
<div data-aos="fade-in">Simple fade</div>

<!-- Complex animations may cause jank -->
<div data-aos="flip-left">Complex flip</div>
```

### 6. Use RequestIdleCallback for Initialization

```javascript
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    AOS.init({ duration: 800 });
  });
} else {
  AOS.init({ duration: 800 });
}
```

## Common Pitfalls

### 1. Forgetting to Refresh After DOM Changes

**Problem**: New elements don't animate after being added dynamically.

**Solution**: Call `AOS.refresh()` or `AOS.refreshHard()`:

```javascript
// After adding elements to DOM
const newElement = document.createElement('div');
newElement.setAttribute('data-aos', 'fade-in');
container.appendChild(newElement);

// Refresh AOS
AOS.refresh(); // Recalculate positions
// or
AOS.refreshHard(); // Reinitialize completely
```

### 2. Animations Not Working in React

**Problem**: AOS doesn't detect elements on first render or route changes.

**Solution**: Initialize in `useEffect` and refresh on route/content changes:

```jsx
useEffect(() => {
  AOS.init();
  return () => AOS.refresh(); // Cleanup
}, []);

useEffect(() => {
  AOS.refresh(); // Refresh on route change
}, [location.pathname]);
```

### 3. Scroll Performance Issues

**Problem**: Page scrolling feels janky with many animated elements.

**Solution**: Reduce animated elements and use `once: true`:

```javascript
AOS.init({
  once: true, // Animate only once
  disable: window.innerWidth < 768 // Disable on mobile
});
```

### 4. CSS Conflicts

**Problem**: Custom CSS interferes with AOS animations.

**Solution**: Use more specific selectors and avoid `!important`:

```css
/* Bad: Conflicts with AOS */
div {
  opacity: 1 !important;
}

/* Good: Specific selector */
.my-content > div {
  /* styles */
}
```

### 5. Anchor Placement Confusion

**Problem**: Animations trigger at unexpected scroll positions.

**Solution**: Understand anchor placement options:

```javascript
// Triggers when element's top hits viewport bottom
data-aos-anchor-placement="top-bottom"

// Triggers when element's center hits viewport center
data-aos-anchor-placement="center-center"

// Triggers when element's bottom hits viewport top
data-aos-anchor-placement="bottom-top"
```

### 6. Duration/Delay Limits

**Problem**: Values above 3000ms don't work.

**Solution**: Add custom CSS for extended durations:

```css
body[data-aos-duration='4000'] [data-aos],
[data-aos][data-aos][data-aos-duration='4000'] {
  transition-duration: 4000ms;
}
```

```html
<div data-aos="fade-in" data-aos-duration="4000">
  Long animation
</div>
```

## Built-in Animations

### Fade Animations
- `fade-in` - Simple fade in
- `fade-up` - Fade in from bottom
- `fade-down` - Fade in from top
- `fade-left` - Fade in from right
- `fade-right` - Fade in from left
- `fade-up-right` - Diagonal fade
- `fade-up-left` - Diagonal fade
- `fade-down-right` - Diagonal fade
- `fade-down-left` - Diagonal fade

### Slide Animations
- `slide-up` - Slide from bottom
- `slide-down` - Slide from top
- `slide-left` - Slide from right
- `slide-right` - Slide from left

### Zoom Animations
- `zoom-in` - Zoom in
- `zoom-in-up` - Zoom in from bottom
- `zoom-in-down` - Zoom in from top
- `zoom-in-left` - Zoom in from right
- `zoom-in-right` - Zoom in from left
- `zoom-out` - Zoom out
- `zoom-out-up` - Zoom out to top
- `zoom-out-down` - Zoom out to bottom
- `zoom-out-left` - Zoom out to left
- `zoom-out-right` - Zoom out to right

### Flip Animations
- `flip-up` - Flip from bottom
- `flip-down` - Flip from top
- `flip-left` - Flip from right
- `flip-right` - Flip from left

## Custom Animations

Create custom animations with CSS:

```css
[data-aos="custom-slide-bounce"] {
  opacity: 0;
  transform: translateY(100px);
  transition-property: transform, opacity;
}

[data-aos="custom-slide-bounce"].aos-animate {
  opacity: 1;
  transform: translateY(0);
  animation: bounce 0.5s;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}
```

```html
<div data-aos="custom-slide-bounce">
  Custom animation
</div>
```

## Comparison with Alternatives

### AOS vs GSAP ScrollTrigger

| Feature | AOS | GSAP ScrollTrigger |
|---------|-----|-------------------|
| **Complexity** | Simple, data-attribute based | Advanced, JavaScript API |
| **Use Case** | Simple reveals | Complex timelines |
| **File Size** | ~13KB | ~27KB (GSAP) + ScrollTrigger |
| **Performance** | CSS-driven | JavaScript-driven |
| **Learning Curve** | Minutes | Hours |
| **Customization** | Limited | Extensive |
| **Best For** | Marketing pages | Interactive experiences |

**Use AOS when**:
- Simple fade/slide/zoom effects
- Quick implementation needed
- Minimal JavaScript preferred
- Basic scroll reveals sufficient

**Use GSAP ScrollTrigger when**:
- Complex animation sequences
- Precise scroll-synced animations
- Timeline orchestration needed
- Advanced easing/physics required

## Resources

### Official Documentation
- **AOS**: https://michalsnik.github.io/aos/
- **GitHub**: https://github.com/michalsnik/aos

### Key Scripts
- `scripts/aos_generator.py` - Generate AOS HTML boilerplate
- `scripts/config_builder.py` - Build AOS configuration

### References
- `references/aos_api.md` - Complete AOS API reference
- `references/animation_catalog.md` - All built-in animations with demos
- `references/integration_patterns.md` - Framework integration guides

### Starter Assets
- `assets/starter_aos/` - Complete AOS starter template
- `assets/examples/` - Production-ready patterns

## Related Skills

- **gsap-scrolltrigger**: For complex scroll-driven animations
- **motion-framer**: For React-specific animations with physics
- **locomotive-scroll**: For smooth scrolling with parallax
- **animated-component-libraries**: For pre-built animated React components



===== FILE: plugins/individual/scroll-reveal-libraries/skills/scroll-reveal-libraries/references/animation_catalog.md =====

# AOS Animation Catalog

Complete catalog of all 50+ built-in animations available in AOS (Animate On Scroll).

## Table of Contents

- [Fade Animations](#fade-animations)
- [Slide Animations](#slide-animations)
- [Zoom Animations](#zoom-animations)
- [Flip Animations](#flip-animations)
- [Animation Combinations](#animation-combinations)
- [Custom Animations](#custom-animations)

## Fade Animations

Fade animations gradually change opacity. These are the simplest and most performant animations.

### Basic Fade

#### `fade-in`

Simple fade in from transparent to opaque.

```html
<div data-aos="fade-in">Fades in</div>
```

**Use cases**: Simple reveals, subtle content appearance

### Directional Fades

#### `fade-up`

Fades in while moving upward from below.

```html
<div data-aos="fade-up">Fades up from bottom</div>
```

**Use cases**: Content blocks, cards, text sections, CTA buttons

#### `fade-down`

Fades in while moving downward from above.

```html
<div data-aos="fade-down">Fades down from top</div>
```

**Use cases**: Headers, hero titles, navigation menus

#### `fade-left`

Fades in while moving left (coming from the right).

```html
<div data-aos="fade-left">Fades left from right</div>
```

**Use cases**: Text blocks, images on right side of layout

#### `fade-right`

Fades in while moving right (coming from the left).

```html
<div data-aos="fade-right">Fades right from left</div>
```

**Use cases**: Text blocks, images on left side of layout

### Diagonal Fades

#### `fade-up-right`

Fades in while moving diagonally up and to the right.

```html
<div data-aos="fade-up-right">Fades up-right diagonally</div>
```

**Use cases**: Grid items, cards in top-left position

#### `fade-up-left`

Fades in while moving diagonally up and to the left.

```html
<div data-aos="fade-up-left">Fades up-left diagonally</div>
```

**Use cases**: Grid items, cards in top-right position

#### `fade-down-right`

Fades in while moving diagonally down and to the right.

```html
<div data-aos="fade-down-right">Fades down-right diagonally</div>
```

**Use cases**: Grid items, cards in bottom-left position

#### `fade-down-left`

Fades in while moving diagonally down and to the left.

```html
<div data-aos="fade-down-left">Fades down-left diagonally</div>
```

**Use cases**: Grid items, cards in bottom-right position

## Slide Animations

Slide animations move elements without changing opacity. More dramatic than fades.

### `slide-up`

Slides up from below (no fade).

```html
<div data-aos="slide-up">Slides up</div>
```

**Use cases**: Modal overlays, bottom sheets, notifications

### `slide-down`

Slides down from above (no fade).

```html
<div data-aos="slide-down">Slides down</div>
```

**Use cases**: Dropdown menus, alerts, top banners

### `slide-left`

Slides left from the right (no fade).

```html
<div data-aos="slide-left">Slides left</div>
```

**Use cases**: Side panels, drawer menus, image carousels

### `slide-right`

Slides right from the left (no fade).

```html
<div data-aos="slide-right">Slides right</div>
```

**Use cases**: Side panels, drawer menus, timeline items

## Zoom Animations

Zoom animations scale elements from small to normal size (or vice versa).

### Basic Zoom

#### `zoom-in`

Zooms in from smaller to normal size, centered.

```html
<div data-aos="zoom-in">Zooms in</div>
```

**Use cases**: Featured images, product photos, logos, icons

#### `zoom-out`

Zooms out from larger to normal size, centered.

```html
<div data-aos="zoom-out">Zooms out</div>
```

**Use cases**: Background images, hero sections, splash screens

### Directional Zoom In

#### `zoom-in-up`

Zooms in while moving upward.

```html
<div data-aos="zoom-in-up">Zooms in from bottom</div>
```

**Use cases**: Gallery images, product cards, testimonials

#### `zoom-in-down`

Zooms in while moving downward.

```html
<div data-aos="zoom-in-down">Zooms in from top</div>
```

**Use cases**: Headers, hero content, call-to-action sections

#### `zoom-in-left`

Zooms in while moving left (from right).

```html
<div data-aos="zoom-in-left">Zooms in from right</div>
```

**Use cases**: Content blocks, feature highlights (right side)

#### `zoom-in-right`

Zooms in while moving right (from left).

```html
<div data-aos="zoom-in-right">Zooms in from left</div>
```

**Use cases**: Content blocks, feature highlights (left side)

### Directional Zoom Out

#### `zoom-out-up`

Zooms out while moving upward.

```html
<div data-aos="zoom-out-up">Zooms out moving up</div>
```

**Use cases**: Attention-grabbing elements, special announcements

#### `zoom-out-down`

Zooms out while moving downward.

```html
<div data-aos="zoom-out-down">Zooms out moving down</div>
```

**Use cases**: Hero overlays, introductory content

#### `zoom-out-left`

Zooms out while moving left.

```html
<div data-aos="zoom-out-left">Zooms out moving left</div>
```

**Use cases**: Dynamic content transitions

#### `zoom-out-right`

Zooms out while moving right.

```html
<div data-aos="zoom-out-right">Zooms out moving right</div>
```

**Use cases**: Dynamic content transitions

## Flip Animations

Flip animations create 3D rotation effects. These are more complex and should be used sparingly.

### `flip-up`

Flips up (rotates around X-axis).

```html
<div data-aos="flip-up">Flips up</div>
```

**Use cases**: Cards, product reveals, special features

**Note**: More CPU-intensive than other animations

### `flip-down`

Flips down (rotates around X-axis).

```html
<div data-aos="flip-down">Flips down</div>
```

**Use cases**: Cards, dropdown reveals

**Note**: More CPU-intensive than other animations

### `flip-left`

Flips left (rotates around Y-axis).

```html
<div data-aos="flip-left">Flips left</div>
```

**Use cases**: Card flips, panel transitions

**Note**: More CPU-intensive than other animations

### `flip-right`

Flips right (rotates around Y-axis).

```html
<div data-aos="flip-right">Flips right</div>
```

**Use cases**: Card flips, panel transitions

**Note**: More CPU-intensive than other animations

## Animation Combinations

### Staggered Animations

Create sequential reveals by using delays:

```html
<div class="feature-grid">
  <div data-aos="fade-up" data-aos-delay="0">Item 1</div>
  <div data-aos="fade-up" data-aos-delay="100">Item 2</div>
  <div data-aos="fade-up" data-aos-delay="200">Item 3</div>
  <div data-aos="fade-up" data-aos-delay="300">Item 4</div>
</div>
```

**Recommended delay increment**: 50-150ms between items

### Mixed Animations

Combine different animation types for visual interest:

```html
<!-- Hero section -->
<h1 data-aos="fade-down">Heading</h1>
<p data-aos="fade-up" data-aos-delay="200">Subtext</p>
<button data-aos="zoom-in" data-aos-delay="400">CTA</button>
```

### Alternating Patterns

Create rhythm with alternating directions:

```html
<div class="content-section">
  <div class="item" data-aos="fade-right">From left</div>
  <div class="item" data-aos="fade-left">From right</div>
  <div class="item" data-aos="fade-right">From left</div>
  <div class="item" data-aos="fade-left">From right</div>
</div>
```

## Custom Animations

Create custom animations using CSS:

### Example: Custom Bounce

```css
/* Define animation */
@keyframes custom-bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-30px);
  }
  60% {
    transform: translateY(-15px);
  }
}

/* Apply to AOS element */
[data-aos="custom-bounce"] {
  opacity: 0;
  transform: translateY(100px);
  transition-property: transform, opacity;
}

[data-aos="custom-bounce"].aos-animate {
  opacity: 1;
  transform: translateY(0);
  animation: custom-bounce 1s ease-out;
}
```

```html
<div data-aos="custom-bounce">Bounces in!</div>
```

### Example: Custom Rotate

```css
[data-aos="rotate-in"] {
  opacity: 0;
  transform: rotate(-180deg) scale(0.5);
  transition-property: transform, opacity;
}

[data-aos="rotate-in"].aos-animate {
  opacity: 1;
  transform: rotate(0) scale(1);
}
```

```html
<div data-aos="rotate-in" data-aos-duration="1000">Rotates in!</div>
```

### Example: Custom Slide Bounce

```css
[data-aos="slide-bounce"] {
  opacity: 0;
  transform: translateX(-100px);
  transition-property: transform, opacity;
}

[data-aos="slide-bounce"].aos-animate {
  opacity: 1;
  transform: translateX(0);
  animation: bounce-effect 0.6s;
}

@keyframes bounce-effect {
  0% { transform: translateX(-100px); }
  60% { transform: translateX(10px); }
  80% { transform: translateX(-5px); }
  100% { transform: translateX(0); }
}
```

```html
<div data-aos="slide-bounce">Slides with bounce!</div>
```

## Animation Performance Guide

### Performance Ranking (Best to Worst)

1. **Fade** animations (opacity only)
   - Best performance, GPU-accelerated
   - Use for most content

2. **Slide** and **Zoom** animations (transform only)
   - Good performance, GPU-accelerated
   - Use for featured content

3. **Flip** animations (3D transforms)
   - Lower performance, more CPU-intensive
   - Use sparingly for special elements

### Optimization Tips

#### 1. Prefer Simpler Animations

```html
<!-- Better performance -->
<div data-aos="fade-up">Content</div>

<!-- Lower performance -->
<div data-aos="flip-left">Content</div>
```

#### 2. Limit Animation Count

```html
<!-- Good: Selective animation -->
<div class="grid">
  <div data-aos="fade-up">Animated</div>
  <div>Static</div>
  <div>Static</div>
  <div data-aos="fade-up">Animated</div>
</div>

<!-- Avoid: Everything animated -->
<div class="grid">
  <div data-aos="fade-up">Item 1</div>
  <div data-aos="fade-up">Item 2</div>
  <div data-aos="fade-up">Item 3</div>
  <!-- ...50 more animated items -->
</div>
```

#### 3. Use Shorter Durations

```html
<!-- Fast, smooth -->
<div data-aos="fade-up" data-aos-duration="400">Content</div>

<!-- Potentially janky on slower devices -->
<div data-aos="flip-left" data-aos-duration="1500">Content</div>
```

#### 4. Disable on Mobile (Optional)

```javascript
AOS.init({
  disable: 'mobile' // or window.innerWidth < 768
});
```

## Animation Selection Guide

### By Content Type

| Content Type | Recommended Animation | Alternative |
|--------------|----------------------|-------------|
| Hero Heading | `fade-down` | `zoom-in-down` |
| Hero Subtext | `fade-up` | `slide-up` |
| CTA Button | `zoom-in` | `fade-up` |
| Feature Cards | `fade-up` (staggered) | `zoom-in-up` |
| Image Gallery | `zoom-in-up` | `fade-in` |
| Testimonials | `zoom-in` | `fade-in` |
| Statistics | `zoom-in` | `fade-up` |
| Timeline Items | `slide-right` / `slide-left` | `fade-right` / `fade-left` |
| Modal Overlay | `zoom-in` | `fade-in` |
| Notifications | `slide-down` | `fade-down` |
| Product Cards | `zoom-in-up` | `fade-up` |
| Text Blocks | `fade-right` / `fade-left` | `slide-right` / `slide-left` |
| Icons | `zoom-in` | `fade-in` |
| Navigation | `fade-down` | `slide-down` |

### By User Experience Goal

| Goal | Animation | Example |
|------|-----------|---------|
| **Subtle** | `fade-in`, `fade-up` | About text, descriptions |
| **Attention-grabbing** | `zoom-in`, `zoom-out` | CTA buttons, special offers |
| **Directional flow** | `slide-*`, `fade-*` with direction | Reading flow, timelines |
| **Playful** | `flip-*`, diagonal fades | Portfolio items, creative sections |
| **Professional** | `fade-up`, `fade-in` | Corporate sites, documentation |

## Quick Reference

### Fade Animations (9)
- `fade-in`
- `fade-up`, `fade-down`, `fade-left`, `fade-right`
- `fade-up-right`, `fade-up-left`, `fade-down-right`, `fade-down-left`

### Slide Animations (4)
- `slide-up`, `slide-down`, `slide-left`, `slide-right`

### Zoom Animations (11)
- `zoom-in`, `zoom-out`
- `zoom-in-up`, `zoom-in-down`, `zoom-in-left`, `zoom-in-right`
- `zoom-out-up`, `zoom-out-down`, `zoom-out-left`, `zoom-out-right`

### Flip Animations (4)
- `flip-up`, `flip-down`, `flip-left`, `flip-right`

**Total**: 28 built-in animations

## Best Practices

1. **Consistency**: Stick to 2-3 animation types per page
2. **Hierarchy**: Use more dramatic animations (zoom, flip) for important content
3. **Direction**: Match animation direction to layout flow
4. **Timing**: Use delays to create sequences (100-200ms between items)
5. **Performance**: Prefer fade/slide over flip animations
6. **Mobile**: Consider disabling or simplifying animations on mobile
7. **Accessibility**: Respect `prefers-reduced-motion` user preference

```javascript
// Respect reduced motion preference
AOS.init({
  disable: function() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
});
```



===== FILE: plugins/individual/scroll-reveal-libraries/skills/scroll-reveal-libraries/references/aos_api.md =====

# AOS API Reference

Complete reference for AOS (Animate On Scroll) configuration, methods, and data attributes.

## Table of Contents

- [Initialization](#initialization)
- [Global Configuration Options](#global-configuration-options)
- [Data Attributes](#data-attributes)
- [JavaScript Methods](#javascript-methods)
- [Events](#events)
- [Easing Functions](#easing-functions)
- [Anchor Placement Values](#anchor-placement-values)
- [Disable Options](#disable-options)

## Initialization

### Basic Initialization

```javascript
import AOS from 'aos';
import 'aos/dist/aos.css';

AOS.init();
```

### With Configuration

```javascript
AOS.init({
  // Global settings
  duration: 800,
  easing: 'ease-in-out',
  once: true,
  offset: 120
});
```

## Global Configuration Options

All options can be set globally via `AOS.init()` or overridden per-element using data attributes.

### Animation Settings

#### `duration`

- **Type**: `number`
- **Default**: `400`
- **Range**: `0` - `3000`
- **Description**: Animation duration in milliseconds

```javascript
AOS.init({ duration: 800 });
```

```html
<div data-aos="fade-up" data-aos-duration="1000">Content</div>
```

#### `delay`

- **Type**: `number`
- **Default**: `0`
- **Range**: `0` - `3000`
- **Description**: Delay before animation starts (ms)

```javascript
AOS.init({ delay: 100 });
```

```html
<div data-aos="fade-up" data-aos-delay="200">Content</div>
```

#### `easing`

- **Type**: `string`
- **Default**: `"ease"`
- **Description**: CSS easing function for animations
- **See**: [Easing Functions](#easing-functions) for all available values

```javascript
AOS.init({ easing: 'ease-in-out' });
```

```html
<div data-aos="fade-up" data-aos-easing="ease-out-cubic">Content</div>
```

### Trigger Settings

#### `offset`

- **Type**: `number`
- **Default**: `120`
- **Description**: Offset (in pixels) from the original trigger point

```javascript
AOS.init({ offset: 200 });
```

```html
<div data-aos="fade-up" data-aos-offset="100">Content</div>
```

#### `anchorPlacement`

- **Type**: `string`
- **Default**: `"top-bottom"`
- **Description**: Defines which position of the element regarding the viewport should trigger the animation
- **See**: [Anchor Placement Values](#anchor-placement-values) for all options

```javascript
AOS.init({ anchorPlacement: 'center-center' });
```

```html
<div data-aos="fade-up" data-aos-anchor-placement="top-center">Content</div>
```

#### `anchor`

- **Type**: `string | null`
- **Default**: `null`
- **Description**: CSS selector of element whose scroll position will be used to trigger animation

```html
<div id="trigger-element">Scroll past this...</div>
<div data-aos="fade-up" data-aos-anchor="#trigger-element">Animates when trigger scrolls</div>
```

### Behavior Settings

#### `once`

- **Type**: `boolean`
- **Default**: `false`
- **Description**: Whether animation should happen only once - while scrolling down

```javascript
AOS.init({ once: true });
```

```html
<div data-aos="fade-up" data-aos-once="true">Content</div>
```

#### `mirror`

- **Type**: `boolean`
- **Default**: `false`
- **Description**: Whether elements should animate out while scrolling past them

```javascript
AOS.init({ mirror: true });
```

```html
<div data-aos="fade-up" data-aos-mirror="true">Content</div>
```

### Device Settings

#### `disable`

- **Type**: `boolean | string | function`
- **Default**: `false`
- **Description**: Condition when AOS should be disabled
- **See**: [Disable Options](#disable-options) for details

```javascript
// Disable on mobile
AOS.init({ disable: 'mobile' });

// Disable with function
AOS.init({
  disable: function() {
    return window.innerWidth < 768;
  }
});
```

### Performance Settings

#### `startEvent`

- **Type**: `string`
- **Default**: `"DOMContentLoaded"`
- **Values**: `"DOMContentLoaded"`, `"load"`
- **Description**: Name of the event dispatched on the document, that AOS should initialize on

```javascript
AOS.init({ startEvent: 'load' });
```

#### `throttleDelay`

- **Type**: `number`
- **Default**: `99`
- **Description**: The delay on throttle used while scrolling (in ms)

```javascript
AOS.init({ throttleDelay: 120 });
```

#### `debounceDelay`

- **Type**: `number`
- **Default**: `50`
- **Description**: The delay on debounce used while resizing window (in ms)

```javascript
AOS.init({ debounceDelay: 80 });
```

#### `disableMutationObserver`

- **Type**: `boolean`
- **Default**: `false`
- **Description**: Disables automatic mutations' detections (advanced)

```javascript
AOS.init({ disableMutationObserver: true });
```

## Data Attributes

All configuration options can be set per-element using data attributes:

### `data-aos`

**Required**. Specifies the animation type.

```html
<div data-aos="fade-up">Content</div>
```

See Animation Catalog for all available animations.

### `data-aos-duration`

Animation duration (overrides global `duration`)

```html
<div data-aos="fade-up" data-aos-duration="1000">Content</div>
```

### `data-aos-delay`

Animation delay (overrides global `delay`)

```html
<div data-aos="fade-up" data-aos-delay="500">Content</div>
```

### `data-aos-easing`

Animation easing (overrides global `easing`)

```html
<div data-aos="fade-up" data-aos-easing="ease-in-cubic">Content</div>
```

### `data-aos-offset`

Offset from trigger point (overrides global `offset`)

```html
<div data-aos="fade-up" data-aos-offset="200">Content</div>
```

### `data-aos-anchor`

Element whose offset will be used to trigger animation

```html
<div data-aos="fade-up" data-aos-anchor="#trigger">Content</div>
```

### `data-aos-anchor-placement`

Anchor placement (overrides global `anchorPlacement`)

```html
<div data-aos="fade-up" data-aos-anchor-placement="top-center">Content</div>
```

### `data-aos-once`

Whether to animate only once (overrides global `once`)

```html
<div data-aos="fade-up" data-aos-once="true">Content</div>
```

### `data-aos-mirror`

Whether to animate out (overrides global `mirror`)

```html
<div data-aos="fade-up" data-aos-mirror="true">Content</div>
```

### `data-aos-id`

Optional ID for specific element (used with anchors)

```html
<div data-aos="fade-up" data-aos-id="my-element">Content</div>
```

## JavaScript Methods

### `AOS.init(options)`

Initialize AOS with optional configuration.

```javascript
AOS.init({
  duration: 800,
  once: true
});
```

**Parameters:**
- `options` (Object): Configuration object

**Returns:** `void`

### `AOS.refresh()`

Recalculate all offsets and positions of elements. Should be called after dynamic content changes.

```javascript
// After adding new elements
const newElement = document.createElement('div');
newElement.setAttribute('data-aos', 'fade-in');
container.appendChild(newElement);

AOS.refresh(); // Recalculate positions
```

**Returns:** `void`

### `AOS.refreshHard()`

Reinitialize array with AOS elements and trigger refresh. More comprehensive than `refresh()`.

```javascript
// After major DOM changes
AOS.refreshHard();
```

**Returns:** `void`

## Events

AOS dispatches custom events on animated elements:

### `aos:in`

Fired when element enters the viewport and animation starts.

```javascript
document.addEventListener('aos:in', ({ detail }) => {
  console.log('Animated element:', detail);
});
```

### `aos:out`

Fired when element leaves the viewport (when `mirror: true`).

```javascript
document.addEventListener('aos:out', ({ detail }) => {
  console.log('Animation reversed:', detail);
});
```

### Event Details

Event detail object contains:
- Element reference
- Animation name
- Configuration

```javascript
document.addEventListener('aos:in', ({ detail }) => {
  console.log(detail); // HTMLElement with AOS attributes
});
```

## Easing Functions

Available easing values for `easing` option:

### Standard Easing

- `linear`
- `ease`
- `ease-in`
- `ease-out`
- `ease-in-out`

### Back Easing

- `ease-in-back`
- `ease-out-back`
- `ease-in-out-back`

### Sine Easing

- `ease-in-sine`
- `ease-out-sine`
- `ease-in-out-sine`

### Quad Easing

- `ease-in-quad`
- `ease-out-quad`
- `ease-in-out-quad`

### Cubic Easing

- `ease-in-cubic`
- `ease-out-cubic`
- `ease-in-out-cubic`

### Quart Easing

- `ease-in-quart`
- `ease-out-quart`
- `ease-in-out-quart`

### Usage Example

```javascript
AOS.init({ easing: 'ease-out-cubic' });
```

```html
<div data-aos="fade-up" data-aos-easing="ease-in-out-sine">Content</div>
```

## Anchor Placement Values

Defines which position of element and viewport triggers animation.

Format: `{element-position}-{viewport-position}`

### Element Positions

- `top` - Top edge of element
- `center` - Center of element
- `bottom` - Bottom edge of element

### Viewport Positions

- `top` - Top edge of viewport
- `center` - Center of viewport
- `bottom` - Bottom edge of viewport

### All Combinations

| Value | Description |
|-------|-------------|
| `top-bottom` | Element's top edge hits viewport's bottom edge |
| `top-center` | Element's top edge hits viewport's center |
| `top-top` | Element's top edge hits viewport's top edge |
| `center-bottom` | Element's center hits viewport's bottom edge |
| `center-center` | Element's center hits viewport's center |
| `center-top` | Element's center hits viewport's top edge |
| `bottom-bottom` | Element's bottom edge hits viewport's bottom edge |
| `bottom-center` | Element's bottom edge hits viewport's center |
| `bottom-top` | Element's bottom edge hits viewport's top edge |

### Visual Examples

```
top-bottom (default):
┌─────────────┐
│  Viewport   │
│             │
│             │
│          ┌──┼──┐  ← Element top hits viewport bottom
└──────────┼──┘  │
           │ El  │
           └─────┘

center-center:
┌─────────────┐
│  Viewport   │
│      ┌──────┼────┐  ← Element center hits viewport center
│      │ Elem │    │
│      └──────┼────┘
└─────────────┘

bottom-top:
           ┌─────┐
           │ El  │
┌──────────┼──┐  │  ← Element bottom hits viewport top
│          └──┼──┘
│  Viewport   │
│             │
└─────────────┘
```

### Usage

```html
<!-- Trigger early (when bottom of element reaches top of viewport) -->
<div data-aos="fade-up" data-aos-anchor-placement="bottom-top">
  Content
</div>

<!-- Trigger when centered -->
<div data-aos="fade-up" data-aos-anchor-placement="center-center">
  Content
</div>
```

## Disable Options

The `disable` option controls when AOS is disabled.

### Boolean

```javascript
AOS.init({ disable: false }); // Always enabled
AOS.init({ disable: true });  // Always disabled
```

### String Values

#### `"mobile"`

Disables on mobile devices (phones and tablets).

```javascript
AOS.init({ disable: 'mobile' });
```

Matches: `window.innerWidth < 768 || navigator.userAgent.match(/Mobile|Tablet/)`

#### `"phone"`

Disables only on phones.

```javascript
AOS.init({ disable: 'phone' });
```

Matches: `window.innerWidth < 480`

#### `"tablet"`

Disables only on tablets.

```javascript
AOS.init({ disable: 'tablet' });
```

Matches: `window.innerWidth < 1024 && window.innerWidth >= 768`

### Function

Custom function for fine-grained control.

```javascript
AOS.init({
  disable: function() {
    // Disable on small screens
    return window.innerWidth < 768;
  }
});
```

```javascript
AOS.init({
  disable: function() {
    // Disable in IE
    return /MSIE|Trident/.test(navigator.userAgent);
  }
});
```

```javascript
AOS.init({
  disable: function() {
    // Disable based on user preference
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
});
```

## Complete Example

```javascript
import AOS from 'aos';
import 'aos/dist/aos.css';

// Initialize with full configuration
AOS.init({
  // Animation settings
  duration: 800,
  delay: 0,
  easing: 'ease-out-cubic',

  // Trigger settings
  offset: 120,
  anchorPlacement: 'top-bottom',

  // Behavior
  once: true,
  mirror: false,

  // Device settings
  disable: 'mobile',

  // Performance
  startEvent: 'DOMContentLoaded',
  throttleDelay: 99,
  debounceDelay: 50,
  disableMutationObserver: false
});

// Listen to events
document.addEventListener('aos:in', ({ detail }) => {
  console.log('Element animated in:', detail);
});

// Refresh after dynamic changes
function addNewElement() {
  const el = document.createElement('div');
  el.setAttribute('data-aos', 'fade-up');
  el.textContent = 'New content';
  document.body.appendChild(el);

  // Refresh AOS to detect new element
  AOS.refresh();
}
```

## Browser Support

AOS works in all modern browsers:

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- iOS Safari (latest)
- Chrome for Android (latest)

**Note**: IE11 support requires polyfills for:
- `Array.prototype.forEach`
- `Element.prototype.classList`
- `Object.assign`

## Performance Considerations

### Best Practices

1. **Use `once: true` for better performance**
   ```javascript
   AOS.init({ once: true });
   ```

2. **Increase throttle/debounce delays on slower devices**
   ```javascript
   AOS.init({
     throttleDelay: 120,
     debounceDelay: 80
   });
   ```

3. **Disable on mobile if not needed**
   ```javascript
   AOS.init({ disable: 'mobile' });
   ```

4. **Use simpler animations**
   - Prefer `fade-*` over `flip-*`
   - Avoid excessive animation count

5. **Call `refresh()` sparingly**
   - Only after actual DOM changes
   - Debounce if calling frequently

### Accessibility

Respect user preferences for reduced motion:

```javascript
AOS.init({
  disable: function() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
});
```

## Troubleshooting

### Animations not triggering

1. Verify AOS is initialized: `AOS.init()`
2. Check CSS is imported: `import 'aos/dist/aos.css'`
3. Ensure `data-aos` attribute is set
4. Call `AOS.refresh()` after dynamic content

### Elements flash before animating

Add to global CSS:

```css
[data-aos] {
  pointer-events: none;
}

[data-aos].aos-animate {
  pointer-events: auto;
}
```

### Animations not working in React

Initialize in `useEffect`:

```jsx
useEffect(() => {
  AOS.init();
}, []);
```

Refresh on route changes:

```jsx
const location = useLocation();

useEffect(() => {
  AOS.refresh();
}, [location]);
```



===== FILE: plugins/individual/scroll-reveal-libraries/agents/scroll-reveal-libraries-specialist.md =====

# Scroll Reveal Libraries Specialist

## Role

Expert specialist in Scroll Reveal Libraries implementation, patterns, and best practices.

## Expertise

- Scroll Reveal Libraries core concepts and patterns
- Integration with other libraries and frameworks
- Performance optimization
- Common pitfalls and solutions
- Best practices and conventions

## When to use

Activate this agent when working on:
- Scroll Reveal Libraries implementation challenges
- Integration with other technologies
- Performance optimization
- Troubleshooting and debugging
- Architecture decisions

## Approach

1. Understand project requirements and context
2. Apply Scroll Reveal Libraries best practices
3. Recommend optimal implementation patterns
4. Identify and solve common issues
5. Provide detailed guidance and examples

## Tools

This agent has access to:
- Scroll Reveal Libraries skill knowledge
- Pattern libraries and examples
- Troubleshooting guides
- Integration patterns



===== FILE: plugins/individual/scroll-reveal-libraries/commands/aos_generator.md =====

# /scroll-reveal-libraries-aos_generator

Scroll Reveal Libraries - Aos Generator

## Description

Executes the aos_generator script for Scroll Reveal Libraries.

## Usage

```bash
/scroll-reveal-libraries-aos_generator
```

## Implementation

This command runs the `aos_generator.py` script from the Scroll Reveal Libraries skill, which provides automated assistance for aos generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/scroll-reveal-libraries/commands/config_builder.md =====

# /scroll-reveal-libraries-config_builder

Scroll Reveal Libraries - Config Builder

## Description

Executes the config_builder script for Scroll Reveal Libraries.

## Usage

```bash
/scroll-reveal-libraries-config_builder
```

## Implementation

This command runs the `config_builder.py` script from the Scroll Reveal Libraries skill, which provides automated assistance for config builder.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/scroll-reveal-libraries/skills/scroll-reveal-libraries/scripts/aos_generator.py =====

```py
#!/usr/bin/env python3
"""
AOS HTML Generator

Generates HTML boilerplate with AOS scroll animations.
Creates ready-to-use HTML files with common AOS patterns.

Usage:
    ./aos_generator.py                          # Interactive mode
    ./aos_generator.py --template landing      # Use template
    ./aos_generator.py --template hero --output hero.html
"""

import sys
import argparse
import os

# HTML Templates
TEMPLATES = {
    "hero": {
        "name": "Hero Section",
        "description": "Animated hero section with heading, subtext, and CTA",
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AOS Hero Section</title>
  <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }

    .hero {
      text-align: center;
      padding: 2rem;
      max-width: 800px;
    }

    h1 {
      font-size: 3.5rem;
      font-weight: 800;
      margin-bottom: 1.5rem;
      line-height: 1.2;
    }

    p {
      font-size: 1.25rem;
      margin-bottom: 2rem;
      opacity: 0.9;
    }

    .cta-button {
      display: inline-block;
      padding: 1rem 2.5rem;
      font-size: 1.1rem;
      font-weight: 600;
      color: #667eea;
      background: white;
      border: none;
      border-radius: 50px;
      cursor: pointer;
      text-decoration: none;
      transition: transform 0.2s;
    }

    .cta-button:hover {
      transform: scale(1.05);
    }
  </style>
</head>
<body>
  <section class="hero">
    <h1 data-aos="fade-down" data-aos-duration="800">
      Welcome to the Future
    </h1>

    <p data-aos="fade-up" data-aos-delay="200" data-aos-duration="600">
      Transform your ideas into reality with cutting-edge technology
    </p>

    <a href="#" class="cta-button" data-aos="zoom-in" data-aos-delay="400" data-aos-duration="500">
      Get Started
    </a>
  </section>

  <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
  <script>
    AOS.init({
      duration: 800,
      once: true
    });
  </script>
</body>
</html>"""
    },
    "features": {
        "name": "Feature Cards",
        "description": "Grid of animated feature cards",
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AOS Feature Cards</title>
  <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f7fafc;
      padding: 4rem 2rem;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
    }

    h1 {
      text-align: center;
      font-size: 2.5rem;
      margin-bottom: 3rem;
      color: #2d3748;
    }

    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 2rem;
    }

    .feature-card {
      background: white;
      padding: 2rem;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      transition: transform 0.3s, box-shadow 0.3s;
    }

    .feature-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }

    .feature-icon {
      width: 60px;
      height: 60px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2rem;
      margin-bottom: 1rem;
    }

    h3 {
      font-size: 1.5rem;
      margin-bottom: 0.75rem;
      color: #2d3748;
    }

    p {
      color: #718096;
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1 data-aos="fade-down">Our Features</h1>

    <div class="features-grid">
      <div class="feature-card" data-aos="fade-up" data-aos-duration="600" data-aos-delay="0">
        <div class="feature-icon">🚀</div>
        <h3>Fast Performance</h3>
        <p>Lightning-fast load times and smooth interactions for the best user experience.</p>
      </div>

      <div class="feature-card" data-aos="fade-up" data-aos-duration="600" data-aos-delay="100">
        <div class="feature-icon">🎨</div>
        <h3>Beautiful Design</h3>
        <p>Carefully crafted interfaces that are both functional and aesthetically pleasing.</p>
      </div>

      <div class="feature-card" data-aos="fade-up" data-aos-duration="600" data-aos-delay="200">
        <div class="feature-icon">🔒</div>
        <h3>Secure</h3>
        <p>Enterprise-grade security to keep your data safe and protected.</p>
      </div>

      <div class="feature-card" data-aos="fade-up" data-aos-duration="600" data-aos-delay="300">
        <div class="feature-icon">📱</div>
        <h3>Responsive</h3>
        <p>Works perfectly on all devices from mobile phones to desktop computers.</p>
      </div>

      <div class="feature-card" data-aos="fade-up" data-aos-duration="600" data-aos-delay="400">
        <div class="feature-icon">⚡</div>
        <h3>Easy to Use</h3>
        <p>Intuitive interface that requires no training to get started.</p>
      </div>

      <div class="feature-card" data-aos="fade-up" data-aos-duration="600" data-aos-delay="500">
        <div class="feature-icon">🌟</div>
        <h3>Quality Support</h3>
        <p>24/7 customer support ready to help you whenever you need assistance.</p>
      </div>
    </div>
  </div>

  <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
  <script>
    AOS.init({
      duration: 800,
      once: true
    });
  </script>
</body>
</html>"""
    },
    "landing": {
        "name": "Landing Page",
        "description": "Complete landing page with multiple sections",
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AOS Landing Page</title>
  <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: #2d3748;
      line-height: 1.6;
    }

    section {
      padding: 5rem 2rem;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
    }

    /* Hero */
    .hero {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      text-align: center;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .hero h1 {
      font-size: 3.5rem;
      margin-bottom: 1.5rem;
    }

    .hero p {
      font-size: 1.25rem;
      margin-bottom: 2rem;
      opacity: 0.9;
    }

    .cta-button {
      display: inline-block;
      padding: 1rem 2.5rem;
      font-size: 1.1rem;
      font-weight: 600;
      color: #667eea;
      background: white;
      border-radius: 50px;
      text-decoration: none;
      transition: transform 0.2s;
    }

    .cta-button:hover {
      transform: scale(1.05);
    }

    /* Features */
    .features {
      background: #f7fafc;
    }

    .features h2 {
      text-align: center;
      font-size: 2.5rem;
      margin-bottom: 3rem;
    }

    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 2rem;
    }

    .feature {
      text-align: center;
      padding: 2rem;
    }

    .feature-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
    }

    /* Testimonials */
    .testimonials {
      background: white;
    }

    .testimonials h2 {
      text-align: center;
      font-size: 2.5rem;
      margin-bottom: 3rem;
    }

    .testimonial {
      background: #f7fafc;
      padding: 2rem;
      border-radius: 12px;
      margin-bottom: 2rem;
    }

    .testimonial p {
      font-size: 1.1rem;
      margin-bottom: 1rem;
      font-style: italic;
    }

    .testimonial cite {
      font-weight: 600;
      color: #667eea;
    }

    /* CTA */
    .cta-section {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      text-align: center;
    }

    .cta-section h2 {
      font-size: 2.5rem;
      margin-bottom: 1.5rem;
    }
  </style>
</head>
<body>
  <!-- Hero Section -->
  <section class="hero">
    <div class="container">
      <h1 data-aos="fade-down" data-aos-duration="800">
        Build Something Amazing
      </h1>
      <p data-aos="fade-up" data-aos-delay="200" data-aos-duration="600">
        The most powerful platform for creating extraordinary experiences
      </p>
      <a href="#" class="cta-button" data-aos="zoom-in" data-aos-delay="400">
        Start Free Trial
      </a>
    </div>
  </section>

  <!-- Features Section -->
  <section class="features">
    <div class="container">
      <h2 data-aos="fade-down">Why Choose Us</h2>

      <div class="features-grid">
        <div class="feature" data-aos="fade-up" data-aos-delay="0">
          <div class="feature-icon">🚀</div>
          <h3>Lightning Fast</h3>
          <p>Optimized for speed and performance</p>
        </div>

        <div class="feature" data-aos="fade-up" data-aos-delay="100">
          <div class="feature-icon">🎨</div>
          <h3>Beautiful UI</h3>
          <p>Stunning designs that users love</p>
        </div>

        <div class="feature" data-aos="fade-up" data-aos-delay="200">
          <div class="feature-icon">🔒</div>
          <h3>Secure</h3>
          <p>Enterprise-grade security built-in</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Testimonials Section -->
  <section class="testimonials">
    <div class="container">
      <h2 data-aos="fade-down">What Our Customers Say</h2>

      <div class="testimonial" data-aos="zoom-in" data-aos-duration="500">
        <p>"This product completely transformed how we work. Incredible!"</p>
        <cite>— Sarah Johnson, CEO at TechCorp</cite>
      </div>

      <div class="testimonial" data-aos="zoom-in" data-aos-duration="500" data-aos-delay="100">
        <p>"Best investment we've made this year. Highly recommended!"</p>
        <cite>— Michael Chen, Founder at StartupXYZ</cite>
      </div>

      <div class="testimonial" data-aos="zoom-in" data-aos-duration="500" data-aos-delay="200">
        <p>"The support team is amazing and the product is even better."</p>
        <cite>— Emma Davis, Designer at CreativeStudio</cite>
      </div>
    </div>
  </section>

  <!-- CTA Section -->
  <section class="cta-section">
    <div class="container">
      <h2 data-aos="fade-down">Ready to Get Started?</h2>
      <p data-aos="fade-up" data-aos-delay="200">
        Join thousands of happy customers today
      </p>
      <a href="#" class="cta-button" data-aos="zoom-in" data-aos-delay="400">
        Start Free Trial
      </a>
    </div>
  </section>

  <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
  <script>
    AOS.init({
      duration: 800,
      once: true,
      offset: 100
    });
  </script>
</body>
</html>"""
    },
    "gallery": {
        "name": "Image Gallery",
        "description": "Animated image gallery with zoom effects",
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AOS Image Gallery</title>
  <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f7fafc;
      padding: 4rem 2rem;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
    }

    h1 {
      text-align: center;
      font-size: 2.5rem;
      margin-bottom: 3rem;
      color: #2d3748;
    }

    .gallery {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 2rem;
    }

    .gallery-item {
      position: relative;
      overflow: hidden;
      border-radius: 12px;
      aspect-ratio: 4/3;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      cursor: pointer;
      transition: transform 0.3s;
    }

    .gallery-item:hover {
      transform: scale(1.02);
    }

    .gallery-item::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.3);
      opacity: 0;
      transition: opacity 0.3s;
    }

    .gallery-item:hover::before {
      opacity: 1;
    }

    .gallery-caption {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 1.5rem;
      color: white;
      background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
      transform: translateY(100%);
      transition: transform 0.3s;
    }

    .gallery-item:hover .gallery-caption {
      transform: translateY(0);
    }

    .gallery-caption h3 {
      font-size: 1.25rem;
      margin-bottom: 0.5rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1 data-aos="fade-down">Our Portfolio</h1>

    <div class="gallery">
      <div class="gallery-item" data-aos="zoom-in-up" data-aos-duration="800" data-aos-delay="0">
        <div class="gallery-caption">
          <h3>Project Alpha</h3>
          <p>Modern web application</p>
        </div>
      </div>

      <div class="gallery-item" data-aos="zoom-in-up" data-aos-duration="800" data-aos-delay="100">
        <div class="gallery-caption">
          <h3>Project Beta</h3>
          <p>E-commerce platform</p>
        </div>
      </div>

      <div class="gallery-item" data-aos="zoom-in-up" data-aos-duration="800" data-aos-delay="200">
        <div class="gallery-caption">
          <h3>Project Gamma</h3>
          <p>Mobile app design</p>
        </div>
      </div>

      <div class="gallery-item" data-aos="zoom-in-up" data-aos-duration="800" data-aos-delay="300">
        <div class="gallery-caption">
          <h3>Project Delta</h3>
          <p>Brand identity</p>
        </div>
      </div>

      <div class="gallery-item" data-aos="zoom-in-up" data-aos-duration="800" data-aos-delay="400">
        <div class="gallery-caption">
          <h3>Project Epsilon</h3>
          <p>Marketing campaign</p>
        </div>
      </div>

      <div class="gallery-item" data-aos="zoom-in-up" data-aos-duration="800" data-aos-delay="500">
        <div class="gallery-caption">
          <h3>Project Zeta</h3>
          <p>Product photography</p>
        </div>
      </div>
    </div>
  </div>

  <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
  <script>
    AOS.init({
      duration: 800,
      once: true
    });
  </script>
</body>
</html>"""
    },
    "timeline": {
        "name": "Timeline",
        "description": "Vertical timeline with alternating content",
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AOS Timeline</title>
  <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f7fafc;
      padding: 4rem 2rem;
    }

    .container {
      max-width: 900px;
      margin: 0 auto;
    }

    h1 {
      text-align: center;
      font-size: 2.5rem;
      margin-bottom: 4rem;
      color: #2d3748;
    }

    .timeline {
      position: relative;
      padding-left: 3rem;
    }

    .timeline::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 2px;
      background: #667eea;
    }

    .timeline-item {
      position: relative;
      margin-bottom: 3rem;
    }

    .timeline-item::before {
      content: '';
      position: absolute;
      left: -3.5rem;
      top: 0;
      width: 1rem;
      height: 1rem;
      background: #667eea;
      border-radius: 50%;
      border: 3px solid #f7fafc;
    }

    .timeline-content {
      background: white;
      padding: 2rem;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .timeline-date {
      color: #667eea;
      font-weight: 600;
      margin-bottom: 0.5rem;
    }

    .timeline-content h3 {
      font-size: 1.5rem;
      margin-bottom: 0.75rem;
      color: #2d3748;
    }

    .timeline-content p {
      color: #718096;
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1 data-aos="fade-down">Our Journey</h1>

    <div class="timeline">
      <div class="timeline-item" data-aos="slide-right" data-aos-duration="800">
        <div class="timeline-content">
          <div class="timeline-date">January 2020</div>
          <h3>Company Founded</h3>
          <p>Started with a vision to transform the industry and make a difference.</p>
        </div>
      </div>

      <div class="timeline-item" data-aos="slide-right" data-aos-duration="800" data-aos-delay="100">
        <div class="timeline-content">
          <div class="timeline-date">June 2020</div>
          <h3>First Product Launch</h3>
          <p>Released our flagship product to market with overwhelming positive response.</p>
        </div>
      </div>

      <div class="timeline-item" data-aos="slide-right" data-aos-duration="800" data-aos-delay="200">
        <div class="timeline-content">
          <div class="timeline-date">December 2020</div>
          <h3>Reached 10,000 Users</h3>
          <p>Hit a major milestone with rapid user growth and engagement.</p>
        </div>
      </div>

      <div class="timeline-item" data-aos="slide-right" data-aos-duration="800" data-aos-delay="300">
        <div class="timeline-content">
          <div class="timeline-date">March 2021</div>
          <h3>Series A Funding</h3>
          <p>Secured significant investment to scale operations and expand the team.</p>
        </div>
      </div>

      <div class="timeline-item" data-aos="slide-right" data-aos-duration="800" data-aos-delay="400">
        <div class="timeline-content">
          <div class="timeline-date">Present</div>
          <h3>Global Expansion</h3>
          <p>Continuing to grow and serve customers worldwide with innovative solutions.</p>
        </div>
      </div>
    </div>
  </div>

  <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
  <script>
    AOS.init({
      duration: 800,
      once: true
    });
  </script>
</body>
</html>"""
    }
}


def list_templates():
    """List all available templates."""
    print("\nAvailable Templates:")
    print("=" * 60)

    for template_id, template in TEMPLATES.items():
        print(f"\n{template_id}")
        print(f"  Name: {template['name']}")
        print(f"  Description: {template['description']}")

    print()


def generate_html(template_name, output_path=None):
    """Generate HTML from template."""
    if template_name not in TEMPLATES:
        print(f"Error: Template '{template_name}' not found")
        print("\nAvailable templates:")
        for tid in TEMPLATES.keys():
            print(f"  - {tid}")
        return False

    template = TEMPLATES[template_name]
    html_content = template["html"]

    if output_path:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✓ Generated {template['name']}: {output_path}")
            return True
        except Exception as e:
            print(f"Error writing file: {e}")
            return False
    else:
        # Output to stdout
        print(html_content)
        return True


def interactive_mode():
    """Run interactive HTML generator."""
    print("\nAOS HTML Generator - Interactive Mode")
    print("=" * 60)

    list_templates()

    print("Enter template name:")
    template_name = input("> ").strip().lower()

    if template_name not in TEMPLATES:
        print(f"Error: Template '{template_name}' not found")
        return

    print("\nEnter output filename (or press Enter to print to console):")
    output_path = input("> ").strip()

    if not output_path:
        output_path = None

    generate_html(template_name, output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML boilerplate with AOS animations"
    )
    parser.add_argument(
        "--template",
        choices=list(TEMPLATES.keys()),
        help="Template to use"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: print to console)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available templates"
    )

    args = parser.parse_args()

    if args.list:
        list_templates()
    elif args.template:
        generate_html(args.template, args.output)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()

```


===== FILE: plugins/individual/scroll-reveal-libraries/skills/scroll-reveal-libraries/scripts/config_builder.py =====

```py
#!/usr/bin/env python3
"""
AOS Config Builder

Generates AOS initialization configurations with customizable options.
Outputs JavaScript code for AOS.init() with selected settings.

Usage:
    ./config_builder.py                              # Interactive mode
    ./config_builder.py --preset marketing          # Use preset
    ./config_builder.py --duration 1000 --once true # Custom config
"""

import sys
import argparse
import json

# Configuration presets
PRESETS = {
    "marketing": {
        "name": "Marketing Page",
        "description": "Optimized for marketing/landing pages with once-only animations",
        "config": {
            "duration": 800,
            "delay": 0,
            "offset": 120,
            "easing": "ease-out",
            "once": True,
            "mirror": False,
            "anchorPlacement": "top-bottom",
            "disable": "mobile"
        }
    },
    "interactive": {
        "name": "Interactive Experience",
        "description": "Repeating animations for interactive scrolling experiences",
        "config": {
            "duration": 600,
            "delay": 0,
            "offset": 80,
            "easing": "ease-in-out",
            "once": False,
            "mirror": True,
            "anchorPlacement": "center-center",
            "disable": False
        }
    },
    "blog": {
        "name": "Blog/Content Site",
        "description": "Subtle animations for content-heavy sites",
        "config": {
            "duration": 500,
            "delay": 0,
            "offset": 100,
            "easing": "ease",
            "once": True,
            "mirror": False,
            "anchorPlacement": "top-bottom",
            "disable": False
        }
    },
    "performance": {
        "name": "Performance Optimized",
        "description": "Minimal animations for best performance",
        "config": {
            "duration": 400,
            "delay": 0,
            "offset": 50,
            "easing": "linear",
            "once": True,
            "mirror": False,
            "anchorPlacement": "top-bottom",
            "disable": "mobile",
            "disableMutationObserver": True,
            "throttleDelay": 120,
            "debounceDelay": 80
        }
    },
    "showcase": {
        "name": "Portfolio/Showcase",
        "description": "Dramatic animations for portfolios and showcases",
        "config": {
            "duration": 1200,
            "delay": 100,
            "offset": 150,
            "easing": "ease-out-cubic",
            "once": False,
            "mirror": True,
            "anchorPlacement": "center-center",
            "disable": False
        }
    }
}

# Available configuration options
CONFIG_OPTIONS = {
    "duration": {
        "type": "number",
        "default": 800,
        "range": [0, 3000],
        "description": "Animation duration in milliseconds"
    },
    "delay": {
        "type": "number",
        "default": 0,
        "range": [0, 3000],
        "description": "Delay before animation starts (ms)"
    },
    "offset": {
        "type": "number",
        "default": 120,
        "description": "Offset (in px) from original trigger point"
    },
    "easing": {
        "type": "enum",
        "default": "ease",
        "values": [
            "linear", "ease", "ease-in", "ease-out", "ease-in-out",
            "ease-in-back", "ease-out-back", "ease-in-out-back",
            "ease-in-sine", "ease-out-sine", "ease-in-out-sine",
            "ease-in-quad", "ease-out-quad", "ease-in-out-quad",
            "ease-in-cubic", "ease-out-cubic", "ease-in-out-cubic",
            "ease-in-quart", "ease-out-quart", "ease-in-out-quart"
        ],
        "description": "Easing function for animations"
    },
    "once": {
        "type": "boolean",
        "default": False,
        "description": "Whether animation should happen only once"
    },
    "mirror": {
        "type": "boolean",
        "default": False,
        "description": "Whether elements should animate out while scrolling past them"
    },
    "anchorPlacement": {
        "type": "enum",
        "default": "top-bottom",
        "values": [
            "top-bottom", "top-center", "top-top",
            "center-bottom", "center-center", "center-top",
            "bottom-bottom", "bottom-center", "bottom-top"
        ],
        "description": "Anchor placement - which position triggers animation"
    },
    "disable": {
        "type": "mixed",
        "default": False,
        "values": [False, "mobile", "phone", "tablet"],
        "description": "Disable AOS on specific devices"
    },
    "startEvent": {
        "type": "enum",
        "default": "DOMContentLoaded",
        "values": ["DOMContentLoaded", "load"],
        "description": "Event on which AOS should be initialized"
    },
    "disableMutationObserver": {
        "type": "boolean",
        "default": False,
        "description": "Disable mutation observer (for static content)"
    },
    "throttleDelay": {
        "type": "number",
        "default": 99,
        "description": "Delay on throttle used while scrolling (ms)"
    },
    "debounceDelay": {
        "type": "number",
        "default": 50,
        "description": "Delay on debounce used while resizing window (ms)"
    }
}


def format_value(key, value):
    """Format configuration value for JavaScript output."""
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, str):
        return f"'{value}'"
    elif value is False:
        return "false"
    else:
        return str(value)


def generate_js_config(config, format_type="modern"):
    """Generate JavaScript AOS initialization code."""
    lines = []

    if format_type == "modern":
        lines.append("import AOS from 'aos';")
        lines.append("import 'aos/dist/aos.css';")
        lines.append("")
    elif format_type == "cdn":
        lines.append("<!-- Add to <head> -->")
        lines.append('<link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />')
        lines.append("")
        lines.append("<!-- Add before </body> -->")
        lines.append('<script src="https://unpkg.com/aos@next/dist/aos.js"></script>')
        lines.append("<script>")

    lines.append("AOS.init({")

    # Sort config keys for consistent output
    sorted_config = sorted(config.items())

    for i, (key, value) in enumerate(sorted_config):
        comma = "," if i < len(sorted_config) - 1 else ""

        # Add comment for each option
        if key in CONFIG_OPTIONS:
            lines.append(f"  // {CONFIG_OPTIONS[key]['description']}")

        lines.append(f"  {key}: {format_value(key, value)}{comma}")

    lines.append("});")

    if format_type == "cdn":
        lines.append("</script>")

    return "\n".join(lines)


def generate_react_config(config):
    """Generate React AOS initialization code."""
    lines = [
        "import { useEffect } from 'react';",
        "import AOS from 'aos';",
        "import 'aos/dist/aos.css';",
        "",
        "function App() {",
        "  useEffect(() => {",
        "    AOS.init({"
    ]

    sorted_config = sorted(config.items())

    for i, (key, value) in enumerate(sorted_config):
        comma = "," if i < len(sorted_config) - 1 else ""
        lines.append(f"      {key}: {format_value(key, value)}{comma}")

    lines.extend([
        "    });",
        "  }, []);",
        "",
        "  return (",
        "    <div>",
        "      <h1 data-aos=\"fade-down\">Your Content</h1>",
        "    </div>",
        "  );",
        "}"
    ])

    return "\n".join(lines)


def list_presets():
    """List all available configuration presets."""
    print("\nAvailable Presets:")
    print("=" * 60)

    for preset_id, preset in PRESETS.items():
        print(f"\n{preset_id}")
        print(f"  Name: {preset['name']}")
        print(f"  Description: {preset['description']}")
        print(f"  Config: {json.dumps(preset['config'], indent=2)}")

    print()


def interactive_mode():
    """Run interactive configuration builder."""
    print("\nAOS Config Builder - Interactive Mode")
    print("=" * 60)

    # Ask if user wants to start from a preset
    print("\nWould you like to start from a preset? (y/n)")
    use_preset = input("> ").strip().lower()

    config = {}

    if use_preset == 'y':
        list_presets()
        print("Enter preset name (or press Enter for default):")
        preset_name = input("> ").strip().lower()

        if preset_name in PRESETS:
            config = PRESETS[preset_name]["config"].copy()
            print(f"\nStarting with '{PRESETS[preset_name]['name']}' preset")
        else:
            print("\nNo preset selected, building from scratch")

    print("\nConfigure AOS options (press Enter to use default/current):")
    print("=" * 60)

    for option_name, option_info in CONFIG_OPTIONS.items():
        current_value = config.get(option_name, option_info["default"])

        print(f"\n{option_name}")
        print(f"  Description: {option_info['description']}")
        print(f"  Type: {option_info['type']}")
        print(f"  Current: {current_value}")

        if option_info["type"] == "enum" or option_info["type"] == "mixed":
            print(f"  Options: {', '.join(str(v) for v in option_info['values'])}")
        elif "range" in option_info:
            print(f"  Range: {option_info['range'][0]} - {option_info['range'][1]}")

        value = input("  Value: ").strip()

        if value:
            # Convert value based on type
            if option_info["type"] == "number":
                try:
                    config[option_name] = float(value) if '.' in value else int(value)
                except ValueError:
                    print("  Invalid number, using current value")
                    config[option_name] = current_value
            elif option_info["type"] == "boolean":
                config[option_name] = value.lower() in ["true", "yes", "1"]
            elif option_info["type"] == "mixed":
                if value.lower() in ["false", "no", "0"]:
                    config[option_name] = False
                else:
                    config[option_name] = value
            else:
                config[option_name] = value
        else:
            config[option_name] = current_value

    # Select output format
    print("\n\nSelect output format:")
    print("  1. Modern ES6 (import)")
    print("  2. CDN (script tags)")
    print("  3. React")

    format_choice = input("\nFormat (1-3): ").strip()

    print("\n" + "=" * 60)
    print("Generated Configuration:")
    print("=" * 60 + "\n")

    if format_choice == "2":
        print(generate_js_config(config, "cdn"))
    elif format_choice == "3":
        print(generate_react_config(config))
    else:
        print(generate_js_config(config, "modern"))

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate AOS initialization configurations"
    )
    parser.add_argument(
        "--preset",
        choices=list(PRESETS.keys()),
        help="Use a configuration preset"
    )
    parser.add_argument(
        "--format",
        choices=["modern", "cdn", "react"],
        default="modern",
        help="Output format (default: modern)"
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List available presets"
    )

    # Individual config options
    for option_name, option_info in CONFIG_OPTIONS.items():
        arg_name = f"--{option_name.replace('_', '-')}"

        if option_info["type"] == "boolean":
            parser.add_argument(arg_name, type=lambda x: x.lower() == 'true')
        elif option_info["type"] == "number":
            parser.add_argument(arg_name, type=int)
        else:
            parser.add_argument(arg_name, type=str)

    args = parser.parse_args()

    if args.list_presets:
        list_presets()
    elif args.preset or any(getattr(args, opt.replace('-', '_'), None) is not None
                           for opt in CONFIG_OPTIONS.keys()):
        # CLI mode with preset or custom config
        if args.preset:
            config = PRESETS[args.preset]["config"].copy()
        else:
            config = {}

        # Override with CLI arguments
        for option_name in CONFIG_OPTIONS.keys():
            arg_value = getattr(args, option_name, None)
            if arg_value is not None:
                config[option_name] = arg_value

        if args.format == "react":
            print(generate_react_config(config))
        else:
            print(generate_js_config(config, args.format))
    else:
        interactive_mode()


if __name__ == "__main__":
    main()

```


===== FILE: plugins/individual/scroll-reveal-libraries/skills/scroll-reveal-libraries/assets/README.md =====

# AOS Examples and Integration Patterns

Production-ready code examples for AOS (Animate On Scroll) integration across different frameworks and use cases.

## Table of Contents

- [Quick Start Templates](#quick-start-templates)
- [React Integration](#react-integration)
- [Next.js Integration](#nextjs-integration)
- [Vue.js Integration](#vuejs-integration)
- [Common Patterns](#common-patterns)
- [Performance Examples](#performance-examples)
- [Accessibility Patterns](#accessibility-patterns)

## Quick Start Templates

### Minimal CDN Setup

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AOS Minimal Example</title>
  <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
</head>
<body>
  <h1 data-aos="fade-down">Hello World</h1>
  <p data-aos="fade-up" data-aos-delay="200">
    This content fades in with a delay.
  </p>

  <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
  <script>
    AOS.init({ duration: 800, once: true });
  </script>
</body>
</html>
```

### NPM Setup (ES6)

```bash
npm install aos@next
```

```javascript
// main.js
import AOS from 'aos';
import 'aos/dist/aos.css';

AOS.init({
  duration: 800,
  once: true,
  offset: 100
});
```

```html
<!-- index.html -->
<div data-aos="fade-up">Content here</div>
```

## React Integration

### Basic React Setup

```jsx
// App.jsx
import { useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';

function App() {
  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true,
      offset: 100,
      easing: 'ease-out-cubic'
    });
  }, []);

  return (
    <div>
      <h1 data-aos="fade-down">Welcome</h1>
      <p data-aos="fade-up" data-aos-delay="200">
        Your content here
      </p>
    </div>
  );
}

export default App;
```

### React with React Router

```jsx
// App.jsx
import { useEffect } from 'react';
import { useLocation, Routes, Route } from 'react-router-dom';
import AOS from 'aos';
import 'aos/dist/aos.css';
import Home from './pages/Home';
import About from './pages/About';

function App() {
  const location = useLocation();

  // Initialize AOS on mount
  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true,
      offset: 100
    });
  }, []);

  // Refresh AOS on route change
  useEffect(() => {
    AOS.refresh();
  }, [location.pathname]);

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/about" element={<About />} />
    </Routes>
  );
}

export default App;
```

### React Wrapper Component

```jsx
// components/AnimatedSection.jsx
import React from 'react';

const AnimatedSection = ({
  children,
  animation = 'fade-up',
  delay = 0,
  duration = 800,
  offset = 100,
  once = true,
  className = '',
  ...props
}) => {
  return (
    <div
      data-aos={animation}
      data-aos-delay={delay}
      data-aos-duration={duration}
      data-aos-offset={offset}
      data-aos-once={once}
      className={className}
      {...props}
    >
      {children}
    </div>
  );
};

export default AnimatedSection;
```

Usage:

```jsx
// pages/Home.jsx
import AnimatedSection from '../components/AnimatedSection';

function Home() {
  return (
    <main>
      <AnimatedSection animation="fade-down">
        <h1>Hero Title</h1>
      </AnimatedSection>

      <AnimatedSection animation="fade-up" delay={200}>
        <p>Hero subtext</p>
      </AnimatedSection>

      <AnimatedSection animation="zoom-in" delay={400}>
        <button>Get Started</button>
      </AnimatedSection>
    </main>
  );
}
```

### React with Dynamic Content

```jsx
// components/DynamicList.jsx
import { useState, useEffect } from 'react';
import AOS from 'aos';

function DynamicList() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    AOS.init({ duration: 600 });
  }, []);

  const addItem = () => {
    const newItem = {
      id: Date.now(),
      text: `Item ${items.length + 1}`
    };

    setItems([...items, newItem]);

    // Refresh AOS after adding to DOM
    setTimeout(() => AOS.refresh(), 50);
  };

  const removeItem = (id) => {
    setItems(items.filter(item => item.id !== id));
    setTimeout(() => AOS.refresh(), 50);
  };

  return (
    <div>
      <button onClick={addItem}>Add Item</button>

      <div className="list">
        {items.map((item, index) => (
          <div
            key={item.id}
            data-aos="fade-in"
            data-aos-delay={index * 50}
          >
            {item.text}
            <button onClick={() => removeItem(item.id)}>Remove</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DynamicList;
```

## Next.js Integration

### Next.js App Router (_app.js)

```jsx
// pages/_app.js
import { useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';
import '../styles/globals.css';

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true,
      offset: 100,
      easing: 'ease-out-cubic'
    });
  }, []);

  return <Component {...pageProps} />;
}

export default MyApp;
```

### Next.js Page Example

```jsx
// pages/index.js
export default function Home() {
  return (
    <main>
      <section className="hero">
        <h1 data-aos="fade-down">Next.js + AOS</h1>
        <p data-aos="fade-up" data-aos-delay="200">
          Server-side rendered content with scroll animations
        </p>
      </section>

      <section className="features">
        {features.map((feature, index) => (
          <div
            key={feature.id}
            data-aos="fade-up"
            data-aos-delay={index * 100}
            className="feature-card"
          >
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
          </div>
        ))}
      </section>
    </main>
  );
}

const features = [
  { id: 1, title: 'Fast', description: 'Lightning fast performance' },
  { id: 2, title: 'Secure', description: 'Enterprise-grade security' },
  { id: 3, title: 'Scalable', description: 'Grows with your needs' }
];
```

### Next.js with TypeScript

```tsx
// pages/_app.tsx
import { useEffect } from 'react';
import type { AppProps } from 'next/app';
import AOS from 'aos';
import 'aos/dist/aos.css';

function MyApp({ Component, pageProps }: AppProps) {
  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true
    });
  }, []);

  return <Component {...pageProps} />;
}

export default MyApp;
```

```tsx
// components/AnimatedCard.tsx
interface AnimatedCardProps {
  title: string;
  description: string;
  delay?: number;
}

const AnimatedCard = ({ title, description, delay = 0 }: AnimatedCardProps) => {
  return (
    <div
      data-aos="fade-up"
      data-aos-delay={delay}
      className="card"
    >
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
};

export default AnimatedCard;
```

## Vue.js Integration

### Vue 3 Composition API

```vue
<!-- App.vue -->
<template>
  <div>
    <h1 data-aos="fade-down">Vue 3 + AOS</h1>

    <div
      v-for="(item, index) in items"
      :key="item.id"
      data-aos="fade-up"
      :data-aos-delay="index * 100"
    >
      {{ item.text }}
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import AOS from 'aos';
import 'aos/dist/aos.css';

const items = ref([
  { id: 1, text: 'Item 1' },
  { id: 2, text: 'Item 2' },
  { id: 3, text: 'Item 3' }
]);

onMounted(() => {
  AOS.init({
    duration: 800,
    once: true
  });
});
</script>
```

### Vue 3 with Dynamic Updates

```vue
<!-- DynamicList.vue -->
<template>
  <div>
    <button @click="addItem">Add Item</button>

    <div
      v-for="(item, index) in items"
      :key="item.id"
      data-aos="fade-in"
      :data-aos-delay="index * 50"
      class="list-item"
    >
      {{ item.text }}
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue';
import AOS from 'aos';
import 'aos/dist/aos.css';

const items = ref([]);

onMounted(() => {
  AOS.init({ duration: 600 });
});

const addItem = async () => {
  items.value.push({
    id: Date.now(),
    text: `Item ${items.value.length + 1}`
  });

  // Wait for DOM update, then refresh AOS
  await nextTick();
  AOS.refresh();
};
</script>
```

### Vue 2 Options API

```vue
<!-- App.vue -->
<template>
  <div>
    <h1 data-aos="fade-down">Vue 2 + AOS</h1>
    <p data-aos="fade-up">Content here</p>
  </div>
</template>

<script>
import AOS from 'aos';
import 'aos/dist/aos.css';

export default {
  name: 'App',
  mounted() {
    AOS.init({
      duration: 800,
      once: true
    });
  },
  updated() {
    // Refresh when component updates
    this.$nextTick(() => {
      AOS.refresh();
    });
  }
};
</script>
```

## Common Patterns

### Landing Page Pattern

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AOS Landing Page</title>
  <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

    /* Hero */
    .hero {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 2rem;
    }

    .hero h1 { font-size: 3rem; margin-bottom: 1rem; }
    .hero p { font-size: 1.25rem; margin-bottom: 2rem; }
    .hero button {
      padding: 1rem 2.5rem;
      font-size: 1.1rem;
      background: white;
      color: #667eea;
      border: none;
      border-radius: 50px;
      cursor: pointer;
    }

    /* Features */
    .features {
      padding: 5rem 2rem;
      max-width: 1200px;
      margin: 0 auto;
    }

    .features h2 {
      text-align: center;
      font-size: 2.5rem;
      margin-bottom: 3rem;
    }

    .feature-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 2rem;
    }

    .feature-card {
      background: white;
      padding: 2rem;
      border-radius: 12px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      text-align: center;
    }

    .feature-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
    }
  </style>
</head>
<body>
  <!-- Hero Section -->
  <section class="hero">
    <div>
      <h1 data-aos="fade-down" data-aos-duration="800">
        Build Something Amazing
      </h1>
      <p data-aos="fade-up" data-aos-delay="200" data-aos-duration="600">
        The most powerful platform for creating extraordinary experiences
      </p>
      <button data-aos="zoom-in" data-aos-delay="400" data-aos-duration="500">
        Get Started
      </button>
    </div>
  </section>

  <!-- Features Section -->
  <section class="features">
    <h2 data-aos="fade-down">Why Choose Us</h2>

    <div class="feature-grid">
      <div class="feature-card" data-aos="fade-up" data-aos-delay="0">
        <div class="feature-icon">🚀</div>
        <h3>Lightning Fast</h3>
        <p>Optimized for speed and performance</p>
      </div>

      <div class="feature-card" data-aos="fade-up" data-aos-delay="100">
        <div class="feature-icon">🎨</div>
        <h3>Beautiful UI</h3>
        <p>Stunning designs that users love</p>
      </div>

      <div class="feature-card" data-aos="fade-up" data-aos-delay="200">
        <div class="feature-icon">🔒</div>
        <h3>Secure</h3>
        <p>Enterprise-grade security built-in</p>
      </div>
    </div>
  </section>

  <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
  <script>
    AOS.init({
      duration: 800,
      once: true,
      offset: 100
    });
  </script>
</body>
</html>
```

### Staggered Grid Pattern

```jsx
// React example
function ProductGrid({ products }) {
  useEffect(() => {
    AOS.init({ duration: 600, once: true });
  }, []);

  return (
    <div className="product-grid">
      {products.map((product, index) => (
        <div
          key={product.id}
          data-aos="zoom-in-up"
          data-aos-delay={index * 50}
          className="product-card"
        >
          <img src={product.image} alt={product.name} />
          <h3>{product.name}</h3>
          <p>{product.price}</p>
        </div>
      ))}
    </div>
  );
}
```

### Alternating Content Pattern

```html
<!-- Alternating image-text sections -->
<div class="content-sections">
  <!-- Section 1: Image on right -->
  <section class="content-row">
    <div class="text-col" data-aos="slide-right" data-aos-duration="800">
      <h2>Feature One</h2>
      <p>Description of the feature...</p>
    </div>
    <div class="image-col" data-aos="fade-left" data-aos-delay="200">
      <img src="feature1.jpg" alt="Feature 1">
    </div>
  </section>

  <!-- Section 2: Image on left -->
  <section class="content-row reverse">
    <div class="image-col" data-aos="fade-right">
      <img src="feature2.jpg" alt="Feature 2">
    </div>
    <div class="text-col" data-aos="slide-left" data-aos-duration="800" data-aos-delay="200">
      <h2>Feature Two</h2>
      <p>Description of the feature...</p>
    </div>
  </section>
</div>
```

## Performance Examples

### Optimized Configuration

```javascript
// Best performance configuration
AOS.init({
  // Animation settings
  duration: 400,  // Shorter = smoother
  easing: 'ease',  // Simple easing

  // Behavior
  once: true,  // Animate only once (better performance)
  mirror: false,  // Don't animate out

  // Device settings
  disable: function() {
    // Disable on mobile or reduced motion preference
    return window.innerWidth < 768 ||
           window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },

  // Performance tuning
  throttleDelay: 120,  // Increase for slower devices
  debounceDelay: 80,
  disableMutationObserver: true  // For fully static content
});
```

### Selective Animation

```jsx
// Don't animate everything - be selective
function BlogPost({ post }) {
  return (
    <article>
      {/* Animate hero elements */}
      <h1 data-aos="fade-down">{post.title}</h1>
      <p className="meta" data-aos="fade-up" data-aos-delay="100">
        {post.author} • {post.date}
      </p>

      {/* Don't animate body text - better for readability */}
      <div className="content">
        {post.content}
      </div>

      {/* Animate CTA */}
      <button data-aos="fade-up" className="cta">
        Share This Post
      </button>
    </article>
  );
}
```

## Accessibility Patterns

### Reduced Motion Support

```javascript
// Respect user's motion preferences
AOS.init({
  disable: function() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }
});
```

### Conditional Animation

```jsx
// React: Disable animations based on user preference
import { useEffect, useState } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';

function App() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = () => setPrefersReducedMotion(mediaQuery.matches);
    mediaQuery.addEventListener('change', handleChange);

    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  useEffect(() => {
    if (!prefersReducedMotion) {
      AOS.init({ duration: 800, once: true });
    }
  }, [prefersReducedMotion]);

  return (
    <div>
      <h1 data-aos={prefersReducedMotion ? undefined : "fade-down"}>
        Accessible Heading
      </h1>
    </div>
  );
}
```

### ARIA-friendly Animations

```html
<!-- Use aria-live for important content -->
<div
  data-aos="fade-up"
  aria-live="polite"
  aria-atomic="true"
>
  <h2>Important Update</h2>
  <p>This content will be announced to screen readers</p>
</div>

<!-- Mark decorative animations -->
<div
  data-aos="zoom-in"
  aria-hidden="true"
  role="presentation"
>
  Decorative element
</div>
```

## Best Practices Summary

### Do's

✅ Initialize AOS once on app mount
✅ Use `AOS.refresh()` after dynamic content changes
✅ Prefer simpler animations (fade, slide) over complex (flip)
✅ Use `once: true` for better performance
✅ Disable on mobile if not needed
✅ Respect `prefers-reduced-motion` preference
✅ Be selective - don't animate everything
✅ Use consistent animation types per page (2-3 max)

### Don'ts

❌ Don't initialize AOS multiple times
❌ Don't forget to call `AOS.refresh()` after adding elements
❌ Don't animate too many elements at once
❌ Don't use very long durations (>1500ms)
❌ Don't ignore accessibility
❌ Don't animate critical content (nav, forms, body text)
❌ Don't mix too many animation types

## Troubleshooting Checklist

- [ ] AOS initialized? (`AOS.init()` called)
- [ ] CSS imported? (`import 'aos/dist/aos.css'`)
- [ ] Valid `data-aos` attribute?
- [ ] Called `AOS.refresh()` after dynamic changes?
- [ ] Check browser console for errors
- [ ] Try simplified config (duration, once, offset only)
- [ ] Verify element is in viewport when scrolling
- [ ] Check for CSS conflicts (`opacity`, `transform`)

## Additional Resources

- **Scripts**: Use `scripts/aos_generator.py` to generate HTML templates
- **Scripts**: Use `scripts/config_builder.py` to build custom configurations
- **References**: See `references/aos_api.md` for complete API documentation
- **References**: See `references/animation_catalog.md` for all 28 built-in animations
- **Official Docs**: https://michalsnik.github.io/aos/



# Skill: lightweight-3d-effects


===== FILE: plugins/individual/lightweight-3d-effects/skills/lightweight-3d-effects/SKILL.md =====

---
name: lightweight-3d-effects
description: Lightweight 3D effects for decorative elements and micro-interactions using Zdog, Vanta.js, and Vanilla-Tilt.js. Use this skill when adding pseudo-3D illustrations, animated backgrounds, parallax tilt effects, decorative 3D elements, or subtle depth effects without heavy frameworks. Triggers on tasks involving Zdog pseudo-3D, Vanta.js backgrounds, Vanilla-Tilt parallax, card tilt effects, hero section animations, or lightweight landing page visuals. Ideal for performance-focused designs.
---

# Lightweight 3D Effects Skill

## Overview

This skill combines three powerful libraries for decorative 3D elements and micro-interactions:
- **Zdog**: Pseudo-3D engine for designer-friendly vector illustrations
- **Vanta.js**: Animated 3D backgrounds powered by Three.js/p5.js
- **Vanilla-Tilt.js**: Smooth parallax tilt effects responding to mouse/gyroscope

## When to Use This Skill
- Add decorative 3D illustrations without heavy frameworks
- Create animated backgrounds for hero sections
- Implement subtle parallax tilt effects on cards/images
- Build lightweight landing pages with visual depth
- Add micro-interactions that enhance UX without performance impact

## Zdog - Pseudo-3D Illustrations

### Core Concepts

Zdog is a pseudo-3D engine that renders flat, round designs in 3D space using Canvas or SVG.

**Key Features:**
- Designer-friendly declarative API
- Small file size (~28kb minified)
- Canvas or SVG rendering
- Drag rotation built-in
- Smooth animations

### Basic Setup

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://unpkg.com/zdog@1/dist/zdog.dist.min.js"></script>
  <style>
    .zdog-canvas {
      display: block;
      margin: 0 auto;
      background: #FDB;
      cursor: move;
    }
  </style>
</head>
<body>
  <canvas class="zdog-canvas" width="240" height="240"></canvas>

  <script>
    let isSpinning = true;

    let illo = new Zdog.Illustration({
      element: '.zdog-canvas',
      zoom: 4,
      dragRotate: true,
      onDragStart: function() {
        isSpinning = false;
      },
    });

    // Add shapes
    new Zdog.Ellipse({
      addTo: illo,
      diameter: 20,
      translate: { z: 10 },
      stroke: 5,
      color: '#636',
    });

    new Zdog.Rect({
      addTo: illo,
      width: 20,
      height: 20,
      translate: { z: -10 },
      stroke: 3,
      color: '#E62',
      fill: true,
    });

    function animate() {
      illo.rotate.y += isSpinning ? 0.03 : 0;
      illo.updateRenderGraph();
      requestAnimationFrame(animate);
    }
    animate();
  </script>
</body>
</html>
```

### Zdog Shapes

**Basic Shapes:**

```javascript
// Circle
new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636',
});

// Rectangle
new Zdog.Rect({
  addTo: illo,
  width: 80,
  height: 60,
  stroke: 10,
  color: '#E62',
  fill: true,
});

// Rounded Rectangle
new Zdog.RoundedRect({
  addTo: illo,
  width: 60,
  height: 40,
  cornerRadius: 10,
  stroke: 4,
  color: '#C25',
  fill: true,
});

// Polygon
new Zdog.Polygon({
  addTo: illo,
  radius: 40,
  sides: 5,
  stroke: 8,
  color: '#EA0',
  fill: true,
});

// Line
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: -40, y: 0 },
    { x: 40, y: 0 },
  ],
  stroke: 6,
  color: '#636',
});

// Bezier Curve
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: -40, y: -20 },
    {
      bezier: [
        { x: -40, y: 20 },
        { x: 40, y: 20 },
        { x: 40, y: -20 },
      ],
    },
  ],
  stroke: 4,
  color: '#C25',
  closed: false,
});
```

### Zdog Groups

Organize shapes into groups for complex models:

```javascript
// Create a group
let head = new Zdog.Group({
  addTo: illo,
  translate: { y: -40 },
});

// Add shapes to group
new Zdog.Ellipse({
  addTo: head,
  diameter: 60,
  stroke: 30,
  color: '#FED',
});

// Eyes
new Zdog.Ellipse({
  addTo: head,
  diameter: 8,
  stroke: 4,
  color: '#333',
  translate: { x: -10, z: 15 },
});

new Zdog.Ellipse({
  addTo: head,
  diameter: 8,
  stroke: 4,
  color: '#333',
  translate: { x: 10, z: 15 },
});

// Mouth
new Zdog.Shape({
  addTo: head,
  path: [
    { x: -10, y: 0 },
    {
      bezier: [
        { x: -5, y: 5 },
        { x: 5, y: 5 },
        { x: 10, y: 0 },
      ],
    },
  ],
  stroke: 2,
  color: '#333',
  translate: { y: 5, z: 15 },
  closed: false,
});

// Rotate entire group
head.rotate.y = Math.PI / 4;
```

### Zdog Animation

```javascript
// Continuous rotation
function animate() {
  illo.rotate.y += 0.03;
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();

// Bounce animation
let t = 0;
function bounceAnimate() {
  t += 0.05;
  illo.translate.y = Math.sin(t) * 20;
  illo.updateRenderGraph();
  requestAnimationFrame(bounceAnimate);
}
bounceAnimate();

// Interactive rotation with easing
let targetRotateY = 0;
let currentRotateY = 0;

document.addEventListener('mousemove', (event) => {
  targetRotateY = (event.clientX / window.innerWidth - 0.5) * Math.PI;
});

function smoothAnimate() {
  // Ease towards target
  currentRotateY += (targetRotateY - currentRotateY) * 0.1;
  illo.rotate.y = currentRotateY;
  illo.updateRenderGraph();
  requestAnimationFrame(smoothAnimate);
}
smoothAnimate();
```

---

## Vanta.js - Animated 3D Backgrounds

### Core Concepts

Vanta.js provides animated WebGL backgrounds with minimal setup, powered by Three.js or p5.js.

**Key Features:**
- 14+ animated effects (Waves, Birds, Net, Clouds, etc.)
- Mouse/touch interaction
- Customizable colors and settings
- ~120KB total (including Three.js)
- 60fps on most devices

### Basic Setup

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    #vanta-bg {
      width: 100%;
      height: 100vh;
    }
    .content {
      position: relative;
      z-index: 1;
      color: white;
      text-align: center;
      padding: 100px 20px;
    }
  </style>
</head>
<body>
  <div id="vanta-bg">
    <div class="content">
      <h1>My Animated Background</h1>
      <p>Content goes here</p>
    </div>
  </div>

  <!-- Three.js (required) -->
  <script src="https://cdn.jsdelivr.net/npm/three@0.134.0/build/three.min.js"></script>

  <!-- Vanta.js effect -->
  <script src="https://cdn.jsdelivr.net/npm/vanta@0.5.24/dist/vanta.waves.min.js"></script>

  <script>
    VANTA.WAVES({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      color: 0x23153c,
      shininess: 30.00,
      waveHeight: 15.00,
      waveSpeed: 0.75,
      zoom: 0.65
    });
  </script>
</body>
</html>
```

### Available Effects

**1. WAVES** (Three.js)
```javascript
VANTA.WAVES({
  el: "#vanta-bg",
  color: 0x23153c,
  shininess: 30,
  waveHeight: 15,
  waveSpeed: 0.75,
  zoom: 0.65
});
```

**2. CLOUDS** (Three.js)
```javascript
VANTA.CLOUDS({
  el: "#vanta-bg",
  skyColor: 0x68b8d7,
  cloudColor: 0xadc1de,
  cloudShadowColor: 0x183550,
  sunColor: 0xff9919,
  sunGlareColor: 0xff6633,
  sunlightColor: 0xff9933,
  speed: 1.0
});
```

**3. BIRDS** (p5.js required)
```html
<script src="https://cdn.jsdelivr.net/npm/p5@1.4.0/lib/p5.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@0.5.24/dist/vanta.birds.min.js"></script>

<script>
  VANTA.BIRDS({
    el: "#vanta-bg",
    backgroundColor: 0x23153c,
    color1: 0xff0000,
    color2: 0x0000ff,
    birdSize: 1.5,
    wingSpan: 20,
    speedLimit: 5,
    separation: 40,
    alignment: 40,
    cohesion: 40,
    quantity: 3
  });
</script>
```

**4. NET** (Three.js)
```javascript
VANTA.NET({
  el: "#vanta-bg",
  color: 0x3fff00,
  backgroundColor: 0x23153c,
  points: 10,
  maxDistance: 20,
  spacing: 15,
  showDots: true
});
```

**5. CELLS** (p5.js required)
```javascript
VANTA.CELLS({
  el: "#vanta-bg",
  color1: 0x00ff00,
  color2: 0xff0000,
  size: 1.5,
  speed: 1.0,
  scale: 1.0
});
```

**6. FOG** (Three.js)
```javascript
VANTA.FOG({
  el: "#vanta-bg",
  highlightColor: 0xff3f81,
  midtoneColor: 0x1d004d,
  lowlightColor: 0x2b1a5e,
  baseColor: 0x000000,
  blurFactor: 0.6,
  speed: 1.0,
  zoom: 1.0
});
```

**Other effects:** GLOBE, TRUNK, TOPOLOGY, DOTS, HALO, RINGS

### Configuration Options

```javascript
// Common options for all effects
{
  el: "#element-id",              // Required: target element
  mouseControls: true,             // Enable mouse interaction
  touchControls: true,             // Enable touch interaction
  gyroControls: false,             // Device orientation
  minHeight: 200.00,               // Minimum height
  minWidth: 200.00,                // Minimum width
  scale: 1.00,                     // Size scale
  scaleMobile: 1.00,               // Mobile scale

  // Colors (hex numbers, not strings)
  color: 0x23153c,
  backgroundColor: 0x000000,

  // Performance
  forceAnimate: false,             // Force animation even when hidden

  // Effect-specific options vary by effect
}
```

### Vanta.js Methods

```javascript
// Initialize and store reference
const vantaEffect = VANTA.WAVES({
  el: "#vanta-bg",
  // ... options
});

// Destroy when done (important for SPAs)
vantaEffect.destroy();

// Update options dynamically
vantaEffect.setOptions({
  color: 0xff0000,
  waveHeight: 20
});

// Resize (usually automatic)
vantaEffect.resize();
```

### React Integration

```jsx
import { useEffect, useRef, useState } from 'react';
import VANTA from 'vanta/dist/vanta.waves.min';
import * as THREE from 'three';

function VantaBackground() {
  const vantaRef = useRef(null);
  const [vantaEffect, setVantaEffect] = useState(null);

  useEffect(() => {
    if (!vantaEffect) {
      setVantaEffect(VANTA.WAVES({
        el: vantaRef.current,
        THREE: THREE,
        mouseControls: true,
        touchControls: true,
        color: 0x23153c,
        shininess: 30,
        waveHeight: 15,
        waveSpeed: 0.75
      }));
    }

    return () => {
      if (vantaEffect) vantaEffect.destroy();
    };
  }, [vantaEffect]);

  return (
    <div ref={vantaRef} style={{ width: '100%', height: '100vh' }}>
      <div className="content">
        <h1>React + Vanta.js</h1>
      </div>
    </div>
  );
}
```

---

## Vanilla-Tilt.js - Parallax Tilt Effects

### Core Concepts

Vanilla-Tilt.js adds smooth 3D tilt effects responding to mouse movement and device orientation.

**Key Features:**
- Lightweight (~8.5kb minified)
- No dependencies
- Gyroscope support
- Optional glare effect
- Smooth transitions

### Basic Setup

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    .tilt-card {
      width: 300px;
      height: 400px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 15px;
      margin: 50px auto;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 24px;
      transform-style: preserve-3d;
    }

    .tilt-inner {
      transform: translateZ(60px);
    }
  </style>
</head>
<body>
  <div class="tilt-card" data-tilt>
    <div class="tilt-inner">Hover Me!</div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/vanilla-tilt@1.8.1/dist/vanilla-tilt.min.js"></script>
</body>
</html>
```

### Configuration Options

```javascript
VanillaTilt.init(document.querySelector(".tilt-card"), {
  // Rotation
  max: 25,                    // Max tilt angle (degrees)
  reverse: false,             // Reverse tilt direction
  startX: 0,                  // Initial tilt X (degrees)
  startY: 0,                  // Initial tilt Y (degrees)

  // Appearance
  perspective: 1000,          // Transform perspective (lower = more intense)
  scale: 1.1,                 // Scale on hover (1 = no scale)

  // Animation
  speed: 400,                 // Transition speed (ms)
  transition: true,           // Enable smooth transitions
  easing: "cubic-bezier(.03,.98,.52,.99)",

  // Behavior
  axis: null,                 // Restrict to "x" or "y" axis
  reset: true,                // Reset on mouse leave
  "reset-to-start": true,     // Reset to start position vs [0,0]

  // Glare effect
  glare: true,                // Enable glare
  "max-glare": 0.5,          // Glare opacity (0-1)
  "glare-prerender": false,   // Pre-render glare elements

  // Advanced
  full-page-listening: false, // Listen to entire page
  gyroscope: true,            // Enable device orientation
  gyroscopeMinAngleX: -45,    // Min X angle
  gyroscopeMaxAngleX: 45,     // Max X angle
  gyroscopeMinAngleY: -45,    // Min Y angle
  gyroscopeMaxAngleY: 45,     // Max Y angle
  gyroscopeSamples: 10        // Calibration samples
});
```

### Advanced Examples

**Card with Glare Effect:**

```html
<div class="tilt-card" data-tilt
     data-tilt-glare
     data-tilt-max-glare="0.5"
     data-tilt-scale="1.1">
  <div class="tilt-inner">
    <h3>Premium Card</h3>
    <p>With glare effect</p>
  </div>
</div>
```

**Layered 3D Effect:**

```html
<style>
  .tilt-card {
    transform-style: preserve-3d;
  }
  .layer-1 {
    transform: translateZ(20px);
  }
  .layer-2 {
    transform: translateZ(40px);
  }
  .layer-3 {
    transform: translateZ(60px);
  }
</style>

<div class="tilt-card" data-tilt data-tilt-max="15">
  <div class="layer-1">Background</div>
  <div class="layer-2">Middle</div>
  <div class="layer-3">Front</div>
</div>
```

**Programmatic Control:**

```javascript
const element = document.querySelector(".tilt-card");

VanillaTilt.init(element, {
  max: 25,
  speed: 400,
  glare: true,
  "max-glare": 0.5
});

// Get tilt values
element.addEventListener("tiltChange", (e) => {
  console.log("Tilt:", e.detail);
});

// Reset programmatically
element.vanillaTilt.reset();

// Destroy instance
element.vanillaTilt.destroy();

// Get current values
const values = element.vanillaTilt.getValues();
console.log(values); // { tiltX, tiltY, percentageX, percentageY, angle }
```

### React Integration

```jsx
import { useEffect, useRef } from 'react';
import VanillaTilt from 'vanilla-tilt';

function TiltCard({ children, options }) {
  const tiltRef = useRef(null);

  useEffect(() => {
    const element = tiltRef.current;

    VanillaTilt.init(element, {
      max: 25,
      speed: 400,
      glare: true,
      "max-glare": 0.5,
      ...options
    });

    return () => {
      element.vanillaTilt.destroy();
    };
  }, [options]);

  return (
    <div ref={tiltRef} className="tilt-card">
      {children}
    </div>
  );
}

// Usage
<TiltCard options={{ max: 30, scale: 1.1 }}>
  <h3>My Card</h3>
</TiltCard>
```

---

## Common Patterns

### Pattern 1: Hero Section with Vanta + Content

```html
<section id="hero">
  <div class="hero-content">
    <h1>Welcome</h1>
    <p>Animated background with content overlay</p>
    <button>Get Started</button>
  </div>
</section>

<style>
  #hero {
    position: relative;
    width: 100%;
    height: 100vh;
    overflow: hidden;
  }

  .hero-content {
    position: relative;
    z-index: 1;
    color: white;
    text-align: center;
    padding-top: 20vh;
  }
</style>

<script src="https://cdn.jsdelivr.net/npm/three@0.134.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@0.5.24/dist/vanta.waves.min.js"></script>

<script>
  VANTA.WAVES({
    el: "#hero",
    mouseControls: true,
    touchControls: true,
    color: 0x23153c,
    waveHeight: 20,
    waveSpeed: 1.0
  });
</script>
```

### Pattern 2: Zdog Icon Grid

```html
<div class="icon-grid">
  <canvas class="icon" width="120" height="120"></canvas>
  <canvas class="icon" width="120" height="120"></canvas>
  <canvas class="icon" width="120" height="120"></canvas>
</div>

<script src="https://unpkg.com/zdog@1/dist/zdog.dist.min.js"></script>

<script>
  document.querySelectorAll('.icon').forEach((canvas, index) => {
    let illo = new Zdog.Illustration({
      element: canvas,
      zoom: 3,
      dragRotate: true
    });

    // Create different icon for each canvas
    const icons = [
      createHeartIcon,
      createStarIcon,
      createCheckIcon
    ];

    icons[index](illo);

    function animate() {
      illo.rotate.y += 0.02;
      illo.updateRenderGraph();
      requestAnimationFrame(animate);
    }
    animate();
  });

  function createHeartIcon(illo) {
    new Zdog.Shape({
      addTo: illo,
      path: [
        { x: 0, y: -10 },
        {
          bezier: [
            { x: -20, y: -20 },
            { x: -20, y: 0 },
            { x: 0, y: 10 }
          ]
        },
        {
          bezier: [
            { x: 20, y: 0 },
            { x: 20, y: -20 },
            { x: 0, y: -10 }
          ]
        }
      ],
      stroke: 6,
      color: '#E62',
      fill: true,
      closed: false
    });
  }
</script>
```

### Pattern 3: Tilt Card Gallery

```html
<div class="card-gallery">
  <div class="card" data-tilt data-tilt-glare data-tilt-max-glare="0.3">
    <img src="product1.jpg" alt="Product 1">
    <h3>Product 1</h3>
  </div>

  <div class="card" data-tilt data-tilt-glare data-tilt-max-glare="0.3">
    <img src="product2.jpg" alt="Product 2">
    <h3>Product 2</h3>
  </div>

  <div class="card" data-tilt data-tilt-glare data-tilt-max-glare="0.3">
    <img src="product3.jpg" alt="Product 3">
    <h3>Product 3</h3>
  </div>
</div>

<style>
  .card-gallery {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    padding: 50px;
  }

  .card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transform-style: preserve-3d;
  }

  .card img {
    width: 100%;
    border-radius: 10px;
    transform: translateZ(40px);
  }

  .card h3 {
    margin-top: 15px;
    transform: translateZ(60px);
  }
</style>

<script src="https://cdn.jsdelivr.net/npm/vanilla-tilt@1.8.1/dist/vanilla-tilt.min.js"></script>
```

### Pattern 4: Combined Effect - Vanta Background + Tilt Cards

```html
<div id="vanta-section">
  <div class="container">
    <h1>Our Services</h1>

    <div class="services-grid">
      <div class="service-card" data-tilt data-tilt-scale="1.05">
        <div class="icon">🚀</div>
        <h3>Fast</h3>
        <p>Lightning quick performance</p>
      </div>

      <div class="service-card" data-tilt data-tilt-scale="1.05">
        <div class="icon">🎨</div>
        <h3>Beautiful</h3>
        <p>Stunning visual design</p>
      </div>

      <div class="service-card" data-tilt data-tilt-scale="1.05">
        <div class="icon">💪</div>
        <h3>Powerful</h3>
        <p>Feature-rich platform</p>
      </div>
    </div>
  </div>
</div>

<script>
  // Vanta background
  VANTA.NET({
    el: "#vanta-section",
    color: 0x3fff00,
    backgroundColor: 0x23153c,
    points: 10,
    maxDistance: 20
  });

  // Tilt cards
  VanillaTilt.init(document.querySelectorAll(".service-card"), {
    max: 15,
    speed: 400,
    glare: true,
    "max-glare": 0.3
  });
</script>
```

---

## Performance Best Practices

### Zdog Optimization

1. **Limit Shape Count**: Keep total shapes under 100 for smooth 60fps
2. **Use Groups**: Organize related shapes for easier management
3. **Optimize Animation Loop**: Only call `updateRenderGraph()` when needed
4. **Canvas vs SVG**: Canvas is faster for animations, SVG for static illustrations

### Vanta.js Optimization

1. **Single Instance**: Use only 1-2 Vanta effects per page
2. **Mobile Fallback**: Disable on mobile or use static background
3. **Destroy on Unmount**: Always call `.destroy()` in SPAs
4. **Reduce Particle Count**: Lower `points`, `quantity` for better performance

```javascript
// Mobile detection and fallback
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

if (!isMobile) {
  VANTA.WAVES({
    el: "#hero",
    // ... options
  });
} else {
  document.getElementById('hero').style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
}
```

### Vanilla-Tilt Optimization

1. **Limit Instances**: Apply to visible elements only
2. **Reduce `gyroscopeSamples`**: Lower for better mobile performance
3. **Disable on Low-End Devices**: Check device capabilities
4. **Use CSS `will-change`**: Hint browser for transforms

```css
.tilt-card {
  will-change: transform;
}
```

---

## Common Pitfalls

### Pitfall 1: Multiple Vanta Instances

**Problem**: Multiple Vanta effects cause performance issues

**Solution**: Use only one effect, or lazy-load effects per section

```javascript
// Intersection Observer to load Vanta only when visible
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !entry.target.vantaEffect) {
      entry.target.vantaEffect = VANTA.WAVES({
        el: entry.target,
        // ... options
      });
    }
  });
});

observer.observe(document.getElementById('hero'));
```

### Pitfall 2: Memory Leaks in SPAs

**Problem**: Vanta/Tilt not destroyed on component unmount

**Solution**: Always clean up

```javascript
// React useEffect cleanup
useEffect(() => {
  const effect = VANTA.WAVES({ el: vantaRef.current });

  return () => {
    effect.destroy(); // Important!
  };
}, []);
```

### Pitfall 3: Zdog Not Rendering

**Problem**: Canvas appears blank

**Causes**:
- Forgot to call `updateRenderGraph()`
- Canvas size is 0
- Shapes are outside view

**Solution**:

```javascript
// Always call updateRenderGraph after shape changes
illo.updateRenderGraph();

// Ensure canvas has dimensions
<canvas width="240" height="240"></canvas>

// Check shape positions are visible
new Zdog.Ellipse({
  addTo: illo,
  diameter: 20,
  translate: { z: 0 }, // Keep close to origin
});
```

### Pitfall 4: Tilt Not Working on Mobile

**Problem**: Tilt doesn't respond on mobile devices

**Solution**: Enable gyroscope controls

```javascript
VanillaTilt.init(element, {
  gyroscope: true,
  gyroscopeMinAngleX: -45,
  gyroscopeMaxAngleX: 45
});
```

### Pitfall 5: Color Format Confusion (Vanta.js)

**Problem**: Colors don't work

**Cause**: Vanta.js uses hex **numbers**, not strings

```javascript
// ❌ Wrong
color: "#23153c"

// ✅ Correct
color: 0x23153c
```

---

## Resources

**Zdog:**
- [Zdog Documentation](https://zzz.dog/)
- [Zdog GitHub](https://github.com/metafizzy/zdog)
- [Zdog Codepen Examples](https://codepen.io/collection/DzdGMe/)

**Vanta.js:**
- [Vanta.js Official Site](https://www.vantajs.com/)
- [Vanta.js GitHub](https://github.com/tengbao/vanta)
- [Effect Customizer](https://www.vantajs.com/?effect=waves)

**Vanilla-Tilt.js:**
- [Vanilla-Tilt GitHub](https://github.com/micku7zu/vanilla-tilt.js)
- [NPM Package](https://www.npmjs.com/package/vanilla-tilt)

## Related Skills

- **threejs-webgl**: For more complex 3D graphics beyond decorative effects
- **gsap-scrolltrigger**: For animating these effects on scroll
- **motion-framer**: For React component animations alongside these effects
- **react-three-fiber**: Advanced 3D when lightweight effects aren't enough



===== FILE: plugins/individual/lightweight-3d-effects/skills/lightweight-3d-effects/references/tilt_patterns.md =====

# Vanilla-Tilt.js Patterns Reference

Complete reference for Vanilla-Tilt.js - smooth 3D tilt effect for any DOM element.

**Version**: 1.8.1
**License**: MIT
**GitHub**: https://github.com/micku7zu/vanilla-tilt.js

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Configuration Options](#configuration-options)
3. [Methods](#methods)
4. [Events](#events)
5. [Common Patterns](#common-patterns)
6. [Advanced Techniques](#advanced-techniques)
7. [Framework Integration](#framework-integration)
8. [Performance](#performance)

---

## Getting Started

### CDN Installation

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.1/vanilla-tilt.min.js"></script>

<div class="tilt-card" data-tilt></div>

<script>
VanillaTilt.init(document.querySelector(".tilt-card"));
</script>
```

---

### NPM Installation

```bash
npm install vanilla-tilt
```

```javascript
import VanillaTilt from 'vanilla-tilt';

VanillaTilt.init(document.querySelector(".tilt-card"));
```

---

### Basic Usage

**HTML Attribute (No JavaScript)**:

```html
<div class="tilt-card" data-tilt></div>
```

**JavaScript Initialization**:

```html
<div class="tilt-card"></div>

<script>
VanillaTilt.init(document.querySelector(".tilt-card"), {
  max: 25,
  speed: 400,
  glare: true,
  "max-glare": 0.5
});
</script>
```

**Multiple Elements**:

```javascript
VanillaTilt.init(document.querySelectorAll(".tilt-card"));
```

---

## Configuration Options

### Complete Options Reference

```javascript
VanillaTilt.init(element, {
  // Rotation
  reverse: false,               // Reverse tilt direction
  max: 15,                      // Max tilt angle (degrees)
  startX: 0,                    // Starting tilt on X axis (degrees)
  startY: 0,                    // Starting tilt on Y axis (degrees)
  perspective: 1000,            // Transform perspective (px)

  // Scale
  scale: 1.0,                   // Scale on hover (2 = 200%)

  // Speed & Easing
  speed: 300,                   // Transition speed (ms)
  transition: true,             // Enable/disable transition
  easing: "cubic-bezier(.03,.98,.52,.99)",  // CSS easing

  // Axis Control
  axis: null,                   // Restrict axis ("x" or "y")
  reset: true,                  // Reset on mouseout
  "reset-to-start": true,       // Reset to startX/startY values

  // Glare Effect
  glare: false,                 // Enable glare effect
  "max-glare": 1,               // Max glare opacity (0-1)
  "glare-prerender": false,     // Pre-render glare element

  // Mouse/Touch
  "mouse-event-element": null,  // Element for mouse detection
  "full-page-listening": false, // Listen to mouse on entire page
  gyroscope: true,              // Enable gyroscope (mobile)
  gyroscopeMinAngleX: -45,      // Min gyro angle X
  gyroscopeMaxAngleX: 45,       // Max gyro angle X
  gyroscopeMinAngleY: -45,      // Min gyro angle Y
  gyroscopeMaxAngleY: 45        // Max gyro angle Y
});
```

---

## Configuration Options Details

### Rotation Options

#### max

Maximum tilt angle in degrees.

```javascript
// Subtle tilt
VanillaTilt.init(element, { max: 10 });

// Dramatic tilt
VanillaTilt.init(element, { max: 35 });

// Extreme tilt
VanillaTilt.init(element, { max: 50 });
```

**Recommended**: 15-25 for most use cases

---

#### reverse

Reverse the tilt direction.

```javascript
VanillaTilt.init(element, {
  reverse: true  // Tilts opposite to mouse movement
});
```

**Use case**: Parallax layers moving in opposite directions

---

#### startX / startY

Initial tilt angle (degrees).

```javascript
VanillaTilt.init(element, {
  startX: 10,    // Start tilted 10° on X axis
  startY: -5     // Start tilted -5° on Y axis
});
```

---

#### perspective

CSS perspective value (pixels).

```javascript
// Subtle 3D
VanillaTilt.init(element, { perspective: 2000 });

// Strong 3D
VanillaTilt.init(element, { perspective: 500 });
```

**Lower values = stronger 3D effect**

---

### Scale Options

#### scale

Element scale on hover (1.0 = 100%).

```javascript
// Subtle zoom
VanillaTilt.init(element, { scale: 1.05 });

// Noticeable zoom
VanillaTilt.init(element, { scale: 1.2 });

// Dramatic zoom
VanillaTilt.init(element, { scale: 1.5 });
```

---

### Speed & Easing

#### speed

Transition duration in milliseconds.

```javascript
// Fast (snappy)
VanillaTilt.init(element, { speed: 200 });

// Smooth (recommended)
VanillaTilt.init(element, { speed: 400 });

// Slow (fluid)
VanillaTilt.init(element, { speed: 800 });
```

---

#### easing

CSS easing function for transitions.

```javascript
// Linear
VanillaTilt.init(element, {
  easing: "linear"
});

// Ease out (recommended)
VanillaTilt.init(element, {
  easing: "cubic-bezier(.03,.98,.52,.99)"
});

// Bounce
VanillaTilt.init(element, {
  easing: "cubic-bezier(.68,-0.55,.265,1.55)"
});

// Elastic
VanillaTilt.init(element, {
  easing: "cubic-bezier(.6,.04,.98,.335)"
});
```

---

#### transition

Enable/disable CSS transitions.

```javascript
// Disable for instant response
VanillaTilt.init(element, { transition: false });
```

---

### Axis Control

#### axis

Restrict tilt to one axis.

```javascript
// Horizontal tilt only
VanillaTilt.init(element, { axis: "x" });

// Vertical tilt only
VanillaTilt.init(element, { axis: "y" });

// Both axes (default)
VanillaTilt.init(element, { axis: null });
```

---

#### reset

Reset tilt when mouse leaves element.

```javascript
// Keep tilt on mouseout
VanillaTilt.init(element, { reset: false });

// Reset on mouseout (default)
VanillaTilt.init(element, { reset: true });
```

---

#### reset-to-start

Reset to startX/startY values instead of 0.

```javascript
VanillaTilt.init(element, {
  startX: 10,
  startY: -5,
  "reset-to-start": true  // Resets to (10, -5) not (0, 0)
});
```

---

### Glare Effect

#### glare

Enable glossy glare overlay.

```javascript
VanillaTilt.init(element, {
  glare: true,
  "max-glare": 0.5  // 50% max opacity
});
```

**Note**: Automatically adds a `.js-tilt-glare` element inside the tilt element.

---

#### max-glare

Maximum glare opacity (0 to 1).

```javascript
// Subtle glare
VanillaTilt.init(element, {
  glare: true,
  "max-glare": 0.2
});

// Strong glare
VanillaTilt.init(element, {
  glare: true,
  "max-glare": 0.8
});
```

---

#### glare-prerender

Pre-render glare element in HTML (performance optimization).

```html
<div class="tilt-card" data-tilt>
  <div class="js-tilt-glare">
    <div class="js-tilt-glare-inner"></div>
  </div>
  <!-- Your content -->
</div>
```

```javascript
VanillaTilt.init(element, {
  glare: true,
  "glare-prerender": true
});
```

---

### Mouse/Touch Options

#### mouse-event-element

Use different element for mouse tracking.

```javascript
VanillaTilt.init(element, {
  "mouse-event-element": document.querySelector(".parent")
});
```

**Use case**: Tilt element based on mouse position over larger container.

---

#### full-page-listening

Track mouse position across entire page.

```javascript
VanillaTilt.init(element, {
  "full-page-listening": true
});
```

**Use case**: Parallax effects that respond to page-wide mouse movement.

---

### Gyroscope Options

#### gyroscope

Enable device orientation (mobile).

```javascript
VanillaTilt.init(element, {
  gyroscope: true,
  gyroscopeMinAngleX: -45,
  gyroscopeMaxAngleX: 45,
  gyroscopeMinAngleY: -45,
  gyroscopeMaxAngleY: 45
});
```

**Note**: Requires HTTPS and user permission on iOS.

---

## Methods

### destroy()

Remove tilt effect and event listeners.

```javascript
const element = document.querySelector(".tilt-card");
VanillaTilt.init(element);

// Later...
element.vanillaTilt.destroy();
```

**Important**: Always call `destroy()` when removing elements to prevent memory leaks.

---

### reset()

Reset tilt to default position.

```javascript
element.vanillaTilt.reset();
```

---

### getValues()

Get current tilt values.

```javascript
const values = element.vanillaTilt.getValues();

console.log(values);
// {
//   tiltX: 10.5,
//   tiltY: -5.2,
//   percentageX: 52.5,
//   percentageY: 47.8,
//   angle: 11.7
// }
```

**Return values**:
- `tiltX`: Current X-axis tilt (degrees)
- `tiltY`: Current Y-axis tilt (degrees)
- `percentageX`: Mouse X position as percentage (0-100)
- `percentageY`: Mouse Y position as percentage (0-100)
- `angle`: Total tilt angle (degrees)

---

### setOptions(options)

Update options after initialization.

```javascript
element.vanillaTilt.setOptions({
  max: 35,
  speed: 600
});
```

---

## Events

### tiltChange

Fired when tilt changes.

```javascript
element.addEventListener("tiltChange", (e) => {
  console.log("Tilt changed:", e.detail);
  // {
  //   tiltX: 10.5,
  //   tiltY: -5.2,
  //   percentageX: 52.5,
  //   percentageY: 47.8,
  //   angle: 11.7
  // }
});
```

---

### mouseLeave

Fired when mouse leaves element.

```javascript
element.addEventListener("mouseLeave", () => {
  console.log("Mouse left tilt element");
});
```

---

### mouseEnter

Fired when mouse enters element.

```javascript
element.addEventListener("mouseEnter", () => {
  console.log("Mouse entered tilt element");
});
```

---

## Common Patterns

### Pattern 1: Card Gallery

Tilting card grid with glare.

```html
<div class="card-grid">
  <div class="tilt-card" data-tilt>
    <img src="image1.jpg" alt="Card 1">
    <h3>Card Title</h3>
  </div>
  <div class="tilt-card" data-tilt>
    <img src="image2.jpg" alt="Card 2">
    <h3>Card Title</h3>
  </div>
  <!-- More cards... -->
</div>
```

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 2rem;
}

.tilt-card {
  background: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  transform-style: preserve-3d;
}

.tilt-card img {
  width: 100%;
  display: block;
  transform: translateZ(20px);
}

.tilt-card h3 {
  padding: 1rem;
  transform: translateZ(40px);
}
```

```javascript
VanillaTilt.init(document.querySelectorAll(".tilt-card"), {
  max: 15,
  speed: 400,
  glare: true,
  "max-glare": 0.3,
  scale: 1.05
});
```

---

### Pattern 2: Parallax Layers

Multiple layered elements with different tilt depths.

```html
<div class="parallax-container" data-tilt>
  <div class="layer layer-1">Background</div>
  <div class="layer layer-2">Midground</div>
  <div class="layer layer-3">Foreground</div>
</div>
```

```css
.parallax-container {
  position: relative;
  width: 400px;
  height: 400px;
  transform-style: preserve-3d;
}

.layer {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

.layer-1 {
  background: #667eea;
  transform: translateZ(-50px);
}

.layer-2 {
  background: #764ba2;
  opacity: 0.8;
  transform: translateZ(0px);
}

.layer-3 {
  background: #f093fb;
  opacity: 0.6;
  transform: translateZ(50px);
}
```

```javascript
VanillaTilt.init(document.querySelector(".parallax-container"), {
  max: 25,
  speed: 400,
  perspective: 1000
});
```

---

### Pattern 3: Hover Reveal

Reveal content on tilt hover.

```html
<div class="reveal-card" data-tilt>
  <div class="card-front">
    <h2>Hover Me</h2>
  </div>
  <div class="card-back">
    <p>Hidden content revealed!</p>
  </div>
</div>
```

```css
.reveal-card {
  width: 300px;
  height: 400px;
  position: relative;
  transform-style: preserve-3d;
}

.card-front,
.card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-front {
  background: #667eea;
  transform: translateZ(20px);
}

.card-back {
  background: #764ba2;
  transform: translateZ(-20px) rotateY(180deg);
  opacity: 0;
  transition: opacity 0.3s;
}

.reveal-card:hover .card-back {
  opacity: 1;
}
```

```javascript
VanillaTilt.init(document.querySelector(".reveal-card"), {
  max: 25,
  speed: 400,
  glare: true
});
```

---

### Pattern 4: 3D Button

Elevated button with shadow that follows tilt.

```html
<button class="tilt-button" data-tilt>
  <span>Click Me</span>
</button>
```

```css
.tilt-button {
  padding: 1.5rem 3rem;
  font-size: 1.2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transform-style: preserve-3d;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  transition: box-shadow 0.3s;
}

.tilt-button span {
  display: block;
  transform: translateZ(20px);
}

.tilt-button:hover {
  box-shadow: 0 15px 40px rgba(0,0,0,0.4);
}
```

```javascript
VanillaTilt.init(document.querySelector(".tilt-button"), {
  max: 20,
  speed: 300,
  scale: 1.1,
  glare: true,
  "max-glare": 0.5
});
```

---

### Pattern 5: Product Showcase

E-commerce product card with layered depth.

```html
<div class="product-card" data-tilt>
  <div class="product-badge">NEW</div>
  <img src="product.jpg" alt="Product" class="product-image">
  <div class="product-info">
    <h3 class="product-title">Product Name</h3>
    <p class="product-price">$99.99</p>
    <button class="product-button">Add to Cart</button>
  </div>
</div>
```

```css
.product-card {
  width: 320px;
  background: white;
  border-radius: 15px;
  overflow: hidden;
  transform-style: preserve-3d;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.product-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #ff6b6b;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  transform: translateZ(60px);
  z-index: 10;
}

.product-image {
  width: 100%;
  display: block;
  transform: translateZ(30px);
}

.product-info {
  padding: 1.5rem;
  transform: translateZ(40px);
}

.product-button {
  width: 100%;
  padding: 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transform: translateZ(50px);
}
```

```javascript
VanillaTilt.init(document.querySelector(".product-card"), {
  max: 15,
  speed: 400,
  glare: true,
  "max-glare": 0.2,
  scale: 1.03
});
```

---

## Advanced Techniques

### Dynamic Tilt Values

Update tilt based on external data.

```javascript
const element = document.querySelector(".tilt-card");
VanillaTilt.init(element);

element.addEventListener("tiltChange", (e) => {
  const { tiltX, tiltY, angle } = e.detail;

  // Update background color based on tilt
  const hue = Math.abs(tiltX * 10);
  element.style.background = `hsl(${hue}, 70%, 50%)`;

  // Update text based on angle
  element.querySelector(".angle-display").textContent =
    `Angle: ${angle.toFixed(1)}°`;
});
```

---

### Conditional Tilt

Enable tilt based on conditions.

```javascript
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

if (!isMobile) {
  VanillaTilt.init(document.querySelectorAll(".tilt-card"), {
    max: 25,
    speed: 400
  });
} else {
  // Enable gyroscope on mobile
  VanillaTilt.init(document.querySelectorAll(".tilt-card"), {
    max: 15,
    speed: 600,
    gyroscope: true
  });
}
```

---

### Sync Multiple Elements

Tilt multiple elements together.

```javascript
const cards = document.querySelectorAll(".sync-card");

// Initialize all cards
VanillaTilt.init(cards, {
  max: 20,
  speed: 400
});

// Sync tilt values
cards[0].addEventListener("tiltChange", (e) => {
  const { tiltX, tiltY } = e.detail;

  // Apply same tilt to other cards
  cards.forEach((card, index) => {
    if (index > 0) {
      card.style.transform =
        `perspective(1000px) rotateY(${tiltX}deg) rotateX(${-tiltY}deg)`;
    }
  });
});
```

---

### Tilt with Scroll

Combine tilt with scroll position.

```javascript
const element = document.querySelector(".tilt-card");
VanillaTilt.init(element);

window.addEventListener("scroll", () => {
  const scrollPercent = window.scrollY / (document.body.scrollHeight - window.innerHeight);
  const rotation = scrollPercent * 360;

  element.style.transform += ` rotate(${rotation}deg)`;
});
```

---

### Custom Glare Colors

Change glare color dynamically.

```javascript
VanillaTilt.init(element, {
  glare: true,
  "max-glare": 0.5
});

element.addEventListener("tiltChange", (e) => {
  const glareEl = element.querySelector(".js-tilt-glare-inner");
  const { percentageX } = e.detail;

  // Color shifts from blue to purple
  const hue = 200 + (percentageX * 0.8);
  glareEl.style.background =
    `linear-gradient(0deg, transparent, hsl(${hue}, 70%, 50%))`;
});
```

---

## Framework Integration

### React

```jsx
import React, { useEffect, useRef } from 'react';
import VanillaTilt from 'vanilla-tilt';

function TiltCard({ children, options }) {
  const tiltRef = useRef(null);

  useEffect(() => {
    VanillaTilt.init(tiltRef.current, options);

    return () => {
      tiltRef.current.vanillaTilt.destroy();
    };
  }, [options]);

  return (
    <div ref={tiltRef} className="tilt-card">
      {children}
    </div>
  );
}

// Usage
<TiltCard options={{ max: 25, speed: 400, glare: true }}>
  <h2>Card Content</h2>
</TiltCard>
```

---

### Vue 3

```vue
<template>
  <div ref="tiltRef" class="tilt-card">
    <slot></slot>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import VanillaTilt from 'vanilla-tilt';

const props = defineProps({
  options: {
    type: Object,
    default: () => ({ max: 25, speed: 400 })
  }
});

const tiltRef = ref(null);

onMounted(() => {
  VanillaTilt.init(tiltRef.value, props.options);
});

onUnmounted(() => {
  tiltRef.value.vanillaTilt.destroy();
});
</script>
```

---

### Angular

```typescript
import { Component, ElementRef, Input, OnInit, OnDestroy } from '@angular/core';
import VanillaTilt from 'vanilla-tilt';

@Component({
  selector: 'app-tilt-card',
  template: `
    <div class="tilt-card">
      <ng-content></ng-content>
    </div>
  `
})
export class TiltCardComponent implements OnInit, OnDestroy {
  @Input() options: any = { max: 25, speed: 400 };

  constructor(private el: ElementRef) {}

  ngOnInit() {
    VanillaTilt.init(this.el.nativeElement.querySelector('.tilt-card'), this.options);
  }

  ngOnDestroy() {
    this.el.nativeElement.querySelector('.tilt-card').vanillaTilt.destroy();
  }
}
```

---

### Svelte

```svelte
<script>
  import { onMount, onDestroy } from 'svelte';
  import VanillaTilt from 'vanilla-tilt';

  export let options = { max: 25, speed: 400 };

  let tiltRef;

  onMount(() => {
    VanillaTilt.init(tiltRef, options);
  });

  onDestroy(() => {
    if (tiltRef && tiltRef.vanillaTilt) {
      tiltRef.vanillaTilt.destroy();
    }
  });
</script>

<div bind:this={tiltRef} class="tilt-card">
  <slot></slot>
</div>
```

---

## Performance

### Optimization Tips

**1. Disable on mobile for better performance**

```javascript
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

if (!isMobile) {
  VanillaTilt.init(document.querySelectorAll(".tilt-card"));
}
```

**2. Use transform: translateZ for GPU acceleration**

```css
.tilt-card {
  transform: translateZ(0);  /* Force GPU layer */
}
```

**3. Limit tilt to visible elements**

```javascript
let observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      VanillaTilt.init(entry.target);
    } else {
      if (entry.target.vanillaTilt) {
        entry.target.vanillaTilt.destroy();
      }
    }
  });
});

document.querySelectorAll('.tilt-card').forEach(el => {
  observer.observe(el);
});
```

**4. Reduce max angle for subtle effects**

```javascript
// Less intensive
VanillaTilt.init(element, { max: 10 });

// More intensive
VanillaTilt.init(element, { max: 50 });
```

**5. Disable glare on low-end devices**

```javascript
const hasGoodGPU = navigator.hardwareConcurrency > 4;

VanillaTilt.init(element, {
  max: 25,
  glare: hasGoodGPU,
  "max-glare": hasGoodGPU ? 0.5 : 0
});
```

---

## Troubleshooting

### Tilt Not Working

**Check**:
1. Element exists when initializing
2. Element has dimensions (width/height > 0)
3. No CSS conflicts with `transform`

```javascript
// Wait for DOM
document.addEventListener('DOMContentLoaded', () => {
  VanillaTilt.init(document.querySelector(".tilt-card"));
});
```

---

### Glare Not Showing

**Solution**: Ensure element has `overflow: hidden` or `border-radius`.

```css
.tilt-card {
  overflow: hidden;  /* Required for glare */
  border-radius: 10px;
}
```

---

### Memory Leaks in SPAs

**Solution**: Always destroy on unmount.

```javascript
// Store reference
const element = document.querySelector(".tilt-card");
VanillaTilt.init(element);

// Before removing element
element.vanillaTilt.destroy();
```

---

## Resources

- **GitHub**: https://github.com/micku7zu/vanilla-tilt.js
- **NPM**: `npm install vanilla-tilt`
- **Examples**: https://micku7zu.github.io/vanilla-tilt.js/

---

## License

MIT License - Free for commercial and personal use.



===== FILE: plugins/individual/lightweight-3d-effects/skills/lightweight-3d-effects/references/vantajs_effects.md =====

# Vanta.js Effects Reference

Complete reference for Vanta.js - animated WebGL backgrounds powered by Three.js.

**Version**: 0.5.24
**License**: MIT
**Website**: https://www.vantajs.com

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Available Effects](#available-effects)
3. [Common Options](#common-options)
4. [Effect-Specific Options](#effect-specific-options)
5. [Methods](#methods)
6. [Framework Integration](#framework-integration)
7. [Performance](#performance)

---

## Getting Started

### Basic Setup

```html
<!-- Three.js (required for all effects) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>

<!-- Vanta.js effect (choose one) -->
<script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.waves.min.js"></script>

<div id="vanta-bg"></div>

<script>
VANTA.WAVES({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  scaleMobile: 1.00
});
</script>
```

### NPM Installation

```bash
npm install vanta
```

```javascript
import * as THREE from 'three';
import WAVES from 'vanta/dist/vanta.waves.min.js';

const vantaEffect = WAVES({
  el: "#vanta-bg",
  THREE: THREE
});
```

---

## Available Effects

### 1. WAVES

Animated wave surface effect.

**CDN**: `vanta.waves.min.js`

```javascript
VANTA.WAVES({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  scaleMobile: 1.00,
  color: 0x23153c,         // Hex number
  shininess: 30.00,
  waveHeight: 15.00,
  waveSpeed: 0.75,
  zoom: 0.65
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `color` | Number | 0x23153c | Wave color (hex number) |
| `shininess` | Number | 30 | Surface reflectivity (0-100) |
| `waveHeight` | Number | 15 | Wave amplitude |
| `waveSpeed` | Number | 0.75 | Animation speed (0-2) |
| `zoom` | Number | 0.65 | Camera zoom level |

---

### 2. CLOUDS

Volumetric cloud-like effect.

**CDN**: `vanta.clouds.min.js`

```javascript
VANTA.CLOUDS({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  skyColor: 0x68b8d7,
  cloudColor: 0xadc1de,
  cloudShadowColor: 0x183550,
  sunColor: 0xff9919,
  sunGlareColor: 0xff6633,
  sunlightColor: 0xff9933,
  speed: 1.00
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `skyColor` | Number | 0x68b8d7 | Sky background color |
| `cloudColor` | Number | 0xadc1de | Cloud base color |
| `cloudShadowColor` | Number | 0x183550 | Cloud shadow color |
| `sunColor` | Number | 0xff9919 | Sun body color |
| `sunGlareColor` | Number | 0xff6633 | Sun glare color |
| `sunlightColor` | Number | 0xff9933 | Sunlight color |
| `speed` | Number | 1.00 | Cloud movement speed |

---

### 3. BIRDS

Flocking birds simulation.

**CDN**: `vanta.birds.min.js`

```javascript
VANTA.BIRDS({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  scaleMobile: 1.00,
  backgroundColor: 0x23153c,
  color1: 0xff0090,
  color2: 0xff6633,
  colorMode: "lerp",       // "lerp" or "lerpGradient"
  birdSize: 1.00,
  wingSpan: 20.00,
  speedLimit: 5.00,
  separation: 20.00,
  alignment: 20.00,
  cohesion: 20.00,
  quantity: 3.00
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backgroundColor` | Number | 0x23153c | Scene background |
| `color1` | Number | 0xff0090 | Primary bird color |
| `color2` | Number | 0xff6633 | Secondary bird color |
| `colorMode` | String | "lerp" | Color blending mode |
| `birdSize` | Number | 1.00 | Bird scale multiplier |
| `wingSpan` | Number | 20 | Wing spread distance |
| `speedLimit` | Number | 5 | Maximum flight speed |
| `separation` | Number | 20 | Avoid crowding force |
| `alignment` | Number | 20 | Align with neighbors |
| `cohesion` | Number | 20 | Move toward center |
| `quantity` | Number | 3 | Number of birds |

---

### 4. NET

Particle network with connecting lines.

**CDN**: `vanta.net.min.js`

```javascript
VANTA.NET({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  scaleMobile: 1.00,
  color: 0x3fafff,
  backgroundColor: 0x23153c,
  points: 10.00,
  maxDistance: 20.00,
  spacing: 15.00,
  showDots: true
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `color` | Number | 0x3fafff | Line/point color |
| `backgroundColor` | Number | 0x23153c | Background color |
| `points` | Number | 10 | Number of points |
| `maxDistance` | Number | 20 | Max connection distance |
| `spacing` | Number | 15 | Point spacing |
| `showDots` | Boolean | true | Display dots |

---

### 5. CELLS

Organic cellular growth pattern.

**CDN**: `vanta.cells.min.js`

```javascript
VANTA.CELLS({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  color1: 0x18b0c6,
  color2: 0xff6633,
  size: 1.50,
  speed: 1.00
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `color1` | Number | 0x18b0c6 | Primary cell color |
| `color2` | Number | 0xff6633 | Secondary cell color |
| `size` | Number | 1.50 | Cell size multiplier |
| `speed` | Number | 1.00 | Growth animation speed |

---

### 6. FOG

Misty fog effect with depth.

**CDN**: `vanta.fog.min.js`

```javascript
VANTA.FOG({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  highlightColor: 0xff3f81,
  midtoneColor: 0xff1f51,
  lowlightColor: 0x2d1b46,
  baseColor: 0xffebff,
  blurFactor: 0.60,
  speed: 1.00,
  zoom: 1.00
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `highlightColor` | Number | 0xff3f81 | Bright fog color |
| `midtoneColor` | Number | 0xff1f51 | Mid fog color |
| `lowlightColor` | Number | 0x2d1b46 | Dark fog color |
| `baseColor` | Number | 0xffebff | Base background |
| `blurFactor` | Number | 0.60 | Blur intensity (0-1) |
| `speed` | Number | 1.00 | Movement speed |
| `zoom` | Number | 1.00 | Camera zoom |

---

### 7. GLOBE

Rotating globe with points.

**CDN**: `vanta.globe.min.js`

```javascript
VANTA.GLOBE({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  scaleMobile: 1.00,
  color: 0x3fafff,
  color2: 0xff6633,
  size: 1.50,
  backgroundColor: 0x23153c
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `color` | Number | 0x3fafff | Primary globe color |
| `color2` | Number | 0xff6633 | Secondary color |
| `size` | Number | 1.50 | Globe size |
| `backgroundColor` | Number | 0x23153c | Background color |

---

### 8. RINGS

Concentric animated rings.

**CDN**: `vanta.rings.min.js`

```javascript
VANTA.RINGS({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  scaleMobile: 1.00,
  backgroundColor: 0x23153c,
  color: 0xff3f81
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backgroundColor` | Number | 0x23153c | Background color |
| `color` | Number | 0xff3f81 | Ring color |

---

### 9. HALO

Glowing halo particle effect.

**CDN**: `vanta.halo.min.js`

```javascript
VANTA.HALO({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  backgroundColor: 0x111122,
  size: 1.50,
  xOffset: 0.20,
  yOffset: 0.10
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backgroundColor` | Number | 0x111122 | Background color |
| `size` | Number | 1.50 | Halo size |
| `xOffset` | Number | 0.20 | Horizontal position |
| `yOffset` | Number | 0.10 | Vertical position |

---

### 10. TRUNK

Abstract trunk/tree structure.

**CDN**: `vanta.trunk.min.js`

```javascript
VANTA.TRUNK({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  scaleMobile: 1.00,
  backgroundColor: 0x23153c,
  color: 0xff3f81,
  spacing: 2.00,
  chaos: 4.00
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backgroundColor` | Number | 0x23153c | Background color |
| `color` | Number | 0xff3f81 | Trunk color |
| `spacing` | Number | 2.00 | Branch spacing |
| `chaos` | Number | 4.00 | Randomness factor |

---

### 11. TOPOLOGY

Topographic mesh surface.

**CDN**: `vanta.topology.min.js`

```javascript
VANTA.TOPOLOGY({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  scaleMobile: 1.00,
  color: 0xff3f81,
  backgroundColor: 0x23153c
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `color` | Number | 0xff3f81 | Mesh line color |
| `backgroundColor` | Number | 0x23153c | Background color |

---

### 12. DOTS

Particle dot field effect.

**CDN**: `vanta.dots.min.js`

```javascript
VANTA.DOTS({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  scaleMobile: 1.00,
  color: 0xff3f81,
  color2: 0xffffff,
  backgroundColor: 0x23153c,
  size: 3.00,
  spacing: 35.00
});
```

**Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `color` | Number | 0xff3f81 | Primary dot color |
| `color2` | Number | 0xffffff | Secondary dot color |
| `backgroundColor` | Number | 0x23153c | Background color |
| `size` | Number | 3.00 | Dot size |
| `spacing` | Number | 35.00 | Dot spacing |

---

### 13. CLOUDS2

Alternative cloud implementation.

**CDN**: `vanta.clouds2.min.js`

```javascript
VANTA.CLOUDS2({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  backgroundColor: 0x23153c,
  skyColor: 0x3f7fb7,
  cloudColor: 0x28496e,
  lightColor: 0xff8800,
  speed: 1.00
});
```

---

### 14. RIPPLE

Water ripple effect.

**Dependencies**: `vanta.ripple.min.js` + `p5.js`

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.ripple.min.js"></script>
```

```javascript
VANTA.RIPPLE({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  color: 0x3f7fb7
});
```

---

## Common Options

These options work with most/all Vanta effects.

### Control Options

```javascript
{
  el: "#vanta-bg",              // Required: DOM element or selector
  mouseControls: true,          // Mouse movement interaction
  touchControls: true,          // Touch interaction
  gyroControls: false,          // Gyroscope interaction (mobile)
  minHeight: 200.00,            // Minimum height before effect pauses
  minWidth: 200.00,             // Minimum width before effect pauses
  scale: 1.00,                  // Desktop scale
  scaleMobile: 1.00             // Mobile scale multiplier
}
```

### Color Format

**IMPORTANT**: Colors must be hex numbers, NOT strings.

```javascript
// ✅ Correct
color: 0xff3f81

// ❌ Incorrect
color: "#ff3f81"
color: "0xff3f81"
```

**Conversion**:
```javascript
// String to number
let colorString = "#ff3f81";
let colorNumber = parseInt(colorString.replace("#", "0x"));

// Number to string
let colorNumber = 0xff3f81;
let colorString = "#" + colorNumber.toString(16).padStart(6, '0');
```

---

## Methods

All Vanta effects return an instance with these methods:

### destroy()

Remove the effect and clean up resources.

```javascript
let vantaEffect = VANTA.WAVES({ el: "#vanta-bg" });

// Later...
vantaEffect.destroy();
```

**Important**: Always call `destroy()` when removing the effect to prevent memory leaks.

---

### setOptions(options)

Update effect options dynamically.

```javascript
let vantaEffect = VANTA.WAVES({
  el: "#vanta-bg",
  color: 0x23153c
});

// Update color
vantaEffect.setOptions({
  color: 0xff3f81,
  waveHeight: 20
});
```

---

### resize()

Manually trigger a resize recalculation.

```javascript
window.addEventListener('resize', () => {
  vantaEffect.resize();
});
```

**Note**: Vanta usually auto-detects resize, but manual calls help in edge cases.

---

## Framework Integration

### React

```jsx
import React, { useState, useEffect, useRef } from 'react';
import * as THREE from 'three';
import WAVES from 'vanta/dist/vanta.waves.min.js';

function VantaBackground() {
  const [vantaEffect, setVantaEffect] = useState(null);
  const vantaRef = useRef(null);

  useEffect(() => {
    if (!vantaEffect) {
      setVantaEffect(
        WAVES({
          el: vantaRef.current,
          THREE: THREE,
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          color: 0x23153c,
          shininess: 30,
          waveHeight: 15,
          zoom: 0.65
        })
      );
    }

    return () => {
      if (vantaEffect) vantaEffect.destroy();
    };
  }, [vantaEffect]);

  return (
    <div ref={vantaRef} style={{ width: '100%', height: '100vh' }}>
      <h1>Content over Vanta</h1>
    </div>
  );
}

export default VantaBackground;
```

---

### Vue 3

```vue
<template>
  <div ref="vantaRef" class="vanta-container">
    <slot></slot>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import * as THREE from 'three';
import WAVES from 'vanta/dist/vanta.waves.min.js';

const vantaRef = ref(null);
let vantaEffect = null;

onMounted(() => {
  vantaEffect = WAVES({
    el: vantaRef.value,
    THREE: THREE,
    mouseControls: true,
    touchControls: true,
    color: 0x23153c
  });
});

onUnmounted(() => {
  if (vantaEffect) vantaEffect.destroy();
});
</script>

<style scoped>
.vanta-container {
  width: 100%;
  height: 100vh;
}
</style>
```

---

### Angular

```typescript
import { Component, OnInit, OnDestroy, ElementRef, ViewChild } from '@angular/core';
import * as THREE from 'three';
import WAVES from 'vanta/dist/vanta.waves.min.js';

@Component({
  selector: 'app-vanta-bg',
  template: `
    <div #vantaRef class="vanta-container">
      <ng-content></ng-content>
    </div>
  `,
  styles: [`
    .vanta-container {
      width: 100%;
      height: 100vh;
    }
  `]
})
export class VantaBgComponent implements OnInit, OnDestroy {
  @ViewChild('vantaRef') vantaRef!: ElementRef;
  vantaEffect: any;

  ngOnInit() {
    this.vantaEffect = WAVES({
      el: this.vantaRef.nativeElement,
      THREE: THREE,
      mouseControls: true,
      touchControls: true,
      color: 0x23153c
    });
  }

  ngOnDestroy() {
    if (this.vantaEffect) this.vantaEffect.destroy();
  }
}
```

---

### Svelte

```svelte
<script>
  import { onMount, onDestroy } from 'svelte';
  import * as THREE from 'three';
  import WAVES from 'vanta/dist/vanta.waves.min.js';

  let vantaRef;
  let vantaEffect;

  onMount(() => {
    vantaEffect = WAVES({
      el: vantaRef,
      THREE: THREE,
      mouseControls: true,
      touchControls: true,
      color: 0x23153c
    });
  });

  onDestroy(() => {
    if (vantaEffect) vantaEffect.destroy();
  });
</script>

<div bind:this={vantaRef} class="vanta-container">
  <slot></slot>
</div>

<style>
  .vanta-container {
    width: 100%;
    height: 100vh;
  }
</style>
```

---

## Performance

### Optimization Tips

**1. Disable unused controls**

```javascript
VANTA.WAVES({
  el: "#vanta-bg",
  mouseControls: false,    // Disable if not needed
  touchControls: false,
  gyroControls: false
});
```

**2. Reduce complexity on mobile**

```javascript
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

VANTA.WAVES({
  el: "#vanta-bg",
  scaleMobile: 0.5,        // Smaller scale
  waveHeight: isMobile ? 10 : 15,
  points: isMobile ? 5 : 10
});
```

**3. Pause when not visible**

```javascript
let vantaEffect = VANTA.WAVES({ el: "#vanta-bg" });

let observer = new IntersectionObserver(([entry]) => {
  if (entry.isIntersecting) {
    vantaEffect.restart();
  } else {
    vantaEffect.destroy();
  }
});

observer.observe(document.querySelector("#vanta-bg"));
```

**4. Set minHeight/minWidth**

```javascript
VANTA.WAVES({
  el: "#vanta-bg",
  minHeight: 200,
  minWidth: 200
  // Effect pauses below these dimensions
});
```

**5. Use simpler effects on low-end devices**

```javascript
const isLowEnd = navigator.hardwareConcurrency <= 4;

const effect = isLowEnd
  ? VANTA.DOTS  // Simpler effect
  : VANTA.WAVES; // Complex effect

effect({ el: "#vanta-bg" });
```

---

### Effect Performance Ranking

**Most performant** (lightest):
1. DOTS
2. NET
3. RINGS
4. TOPOLOGY

**Moderate**:
5. WAVES
6. CELLS
7. FOG
8. HALO

**Intensive** (heaviest):
9. BIRDS
10. CLOUDS
11. GLOBE
12. TRUNK

---

### Mobile Fallbacks

**Option 1: Disable on mobile**

```javascript
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

if (!isMobile) {
  VANTA.WAVES({ el: "#vanta-bg" });
} else {
  document.querySelector("#vanta-bg").style.background = '#23153c';
}
```

**Option 2: Static image fallback**

```css
.vanta-container {
  background: url('fallback-image.jpg') center/cover;
}

.vanta-container.has-vanta {
  background: none;
}
```

```javascript
VANTA.WAVES({ el: "#vanta-bg" });
document.querySelector("#vanta-bg").classList.add('has-vanta');
```

---

## Troubleshooting

### Multiple Vanta Instances

**Problem**: Only one effect renders.

**Solution**: Use unique elements.

```javascript
// ❌ Wrong - same element
VANTA.WAVES({ el: ".vanta-bg" });
VANTA.BIRDS({ el: ".vanta-bg" });

// ✅ Correct - different elements
VANTA.WAVES({ el: "#vanta-bg-1" });
VANTA.BIRDS({ el: "#vanta-bg-2" });
```

---

### Memory Leaks in SPAs

**Problem**: Effect persists after navigation.

**Solution**: Always destroy on unmount.

```javascript
// Store reference
let vantaEffect = VANTA.WAVES({ el: "#vanta-bg" });

// Cleanup (React example)
useEffect(() => {
  return () => {
    if (vantaEffect) vantaEffect.destroy();
  };
}, []);
```

---

### Color Not Changing

**Problem**: Color updates don't work.

**Solution**: Use hex numbers, not strings.

```javascript
// ❌ Wrong
vantaEffect.setOptions({ color: "#ff3f81" });

// ✅ Correct
vantaEffect.setOptions({ color: 0xff3f81 });
```

---

### Effect Not Responsive

**Problem**: Effect doesn't resize with window.

**Solution**: Call resize() or enable auto-resize.

```javascript
window.addEventListener('resize', () => {
  vantaEffect.resize();
});
```

---

## Resources

- **Official Site**: https://www.vantajs.com
- **GitHub**: https://github.com/tengbao/vanta
- **Interactive Gallery**: https://www.vantajs.com/?effect=waves
- **NPM**: `npm install vanta`

---

## License

MIT License - Free for commercial and personal use.



===== FILE: plugins/individual/lightweight-3d-effects/skills/lightweight-3d-effects/references/zdog_api.md =====

# Zdog API Reference

Complete API documentation for Zdog - a pseudo-3D engine for canvas and SVG.

**Version**: 1.1.3
**License**: MIT
**CDN**: `https://unpkg.com/zdog@1/dist/zdog.dist.min.js`

---

## Table of Contents

1. [Core Classes](#core-classes)
2. [Shape Types](#shape-types)
3. [Properties](#properties)
4. [Methods](#methods)
5. [Animation](#animation)
6. [Advanced Techniques](#advanced-techniques)

---

## Core Classes

### Zdog.Illustration

The root display object that manages the scene and rendering.

```javascript
let illo = new Zdog.Illustration({
  element: '.zdog-canvas',  // CSS selector or DOM element
  zoom: 4,                  // Scale multiplier
  dragRotate: false,        // Enable drag-to-rotate
  resize: false,            // Auto-resize to element
  centered: true,           // Center origin
  onDragStart: function() {},
  onDragMove: function() {},
  onDragEnd: function() {},
  onResize: function(width, height) {}
});
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `element` | String\|Element | Required | Canvas or SVG element |
| `zoom` | Number | 1 | Scale multiplier |
| `dragRotate` | Boolean\|Zdog.Anchor | false | Enable drag rotation |
| `resize` | Boolean | false | Auto-resize to fit element |
| `centered` | Boolean | true | Center scene at origin |
| `rotate` | Zdog.Vector | {x:0,y:0,z:0} | Rotation in radians |
| `translate` | Zdog.Vector | {x:0,y:0,z:0} | Position offset |

#### Methods

```javascript
// Render scene
illo.updateRenderGraph();

// Update size
illo.setSize(width, height);
```

---

### Zdog.Anchor

Group container for organizing and transforming child shapes.

```javascript
let group = new Zdog.Anchor({
  addTo: illo,
  translate: { x: 0, y: 0, z: 0 },
  rotate: { x: 0, y: 0, z: 0 },
  scale: 1
});
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `addTo` | Zdog.Anchor | null | Parent object |
| `translate` | Object | {x:0,y:0,z:0} | Position |
| `rotate` | Object | {x:0,y:0,z:0} | Rotation (radians) |
| `scale` | Number\|Object | 1 | Uniform or {x,y,z} scale |

#### Methods

```javascript
// Add child
group.addChild(shape);

// Remove child
group.removeChild(shape);

// Remove from parent
group.remove();

// Copy all properties
let copy = group.copy();

// Copy with options
let copy = group.copyGraph({
  translate: { x: 10 }
});
```

---

### Zdog.Shape

Base class for all rendered shapes (usually not used directly).

```javascript
let shape = new Zdog.Shape({
  addTo: group,
  stroke: 1,
  fill: false,
  color: '#333',
  visible: true,
  backface: true
});
```

#### Common Shape Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `stroke` | Number | 1 | Line thickness |
| `fill` | Boolean | false | Fill shape interior |
| `color` | String | '#333' | CSS color value |
| `visible` | Boolean | true | Render visibility |
| `backface` | Boolean\|String | true | Show back face / color |
| `front` | Object | {z:0} | Front face offset |
| `closed` | Boolean | true | Close path |

---

## Shape Types

### Ellipse

Circle or ellipse shape.

```javascript
new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,        // Circle
  // OR
  width: 80,           // Ellipse width
  height: 40,          // Ellipse height
  quarters: 4,         // Number of curve segments
  stroke: 20,
  color: '#636',
  fill: true
});
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `diameter` | Number | 1 | Circle diameter |
| `width` | Number | diameter | Ellipse width |
| `height` | Number | diameter | Ellipse height |
| `quarters` | Number | 4 | Bezier curve segments (4 = smooth) |

---

### Rect

Rectangle shape.

```javascript
new Zdog.Rect({
  addTo: illo,
  width: 80,
  height: 60,
  stroke: 2,
  color: '#E62',
  fill: true
});
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `width` | Number | 1 | Rectangle width |
| `height` | Number | 1 | Rectangle height |

---

### RoundedRect

Rectangle with rounded corners.

```javascript
new Zdog.RoundedRect({
  addTo: illo,
  width: 80,
  height: 60,
  cornerRadius: 10,
  stroke: 2,
  color: '#E62',
  fill: true
});
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `width` | Number | 1 | Rectangle width |
| `height` | Number | 1 | Rectangle height |
| `cornerRadius` | Number | 0 | Corner curve radius |

---

### Polygon

Multi-sided polygon shape.

```javascript
// Triangle
new Zdog.Polygon({
  addTo: illo,
  sides: 3,
  radius: 40,
  stroke: 2,
  color: '#EA0',
  fill: true
});

// Pentagon
new Zdog.Polygon({
  sides: 5,
  radius: 40
});

// Star (using path hack)
new Zdog.Polygon({
  sides: 5,
  radius: 40,
  rotate: { z: -Math.PI/2 }
});
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `sides` | Number | 3 | Number of sides |
| `radius` | Number | 1 | Distance from center |

---

### Line

Straight line segment.

```javascript
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: -40, y: 0, z: 0 },  // Start point
    { x: 40, y: 0, z: 0 }    // End point
  ],
  stroke: 4,
  color: '#636'
});
```

---

### Bezier

Bezier curve path.

```javascript
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: -40, y: 0 },           // Start
    {
      bezier: [
        { x: -20, y: -40 },     // Control point 1
        { x: 20, y: -40 },      // Control point 2
        { x: 40, y: 0 }         // End point
      ]
    }
  ],
  stroke: 4,
  color: '#E62'
});
```

---

### Hemisphere

Half-sphere shape.

```javascript
new Zdog.Hemisphere({
  addTo: illo,
  diameter: 80,
  stroke: 5,
  color: '#EA0',
  fill: true,
  // Render semi-circles
});
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `diameter` | Number | 1 | Sphere diameter |

---

### Cylinder

Cylindrical shape.

```javascript
new Zdog.Cylinder({
  addTo: illo,
  diameter: 80,
  length: 120,
  stroke: 5,
  color: '#636',
  fill: true,
  frontFace: '#EA0',   // Front cap color
  backface: '#E62'     // Back cap color
});
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `diameter` | Number | 1 | Cylinder diameter |
| `length` | Number | 1 | Cylinder length (depth) |
| `frontFace` | String\|Boolean | true | Front cap color |

---

### Cone

Conical shape.

```javascript
new Zdog.Cone({
  addTo: illo,
  diameter: 80,
  length: 120,
  stroke: 5,
  color: '#636',
  fill: true,
  backface: '#E62'
});
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `diameter` | Number | 1 | Base diameter |
| `length` | Number | 1 | Cone height |

---

### Box

3D box shape (composed of rectangles).

```javascript
new Zdog.Box({
  addTo: illo,
  width: 80,
  height: 100,
  depth: 60,
  stroke: 2,
  color: '#C25',
  fill: true,
  frontFace: '#EA0',
  rearFace: '#E62',
  leftFace: '#636',
  rightFace: '#C25',
  topFace: '#EA0',
  bottomFace: '#E62'
});
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `width` | Number | 1 | Box width (x-axis) |
| `height` | Number | 1 | Box height (y-axis) |
| `depth` | Number | 1 | Box depth (z-axis) |
| `frontFace` | String\|Boolean | true | Front face color |
| `rearFace` | String\|Boolean | true | Rear face color |
| `leftFace` | String\|Boolean | true | Left face color |
| `rightFace` | String\|Boolean | true | Right face color |
| `topFace` | String\|Boolean | true | Top face color |
| `bottomFace` | String\|Boolean | true | Bottom face color |

---

## Properties

### Transform Properties

Available on all Zdog.Anchor and Zdog.Shape objects.

#### translate

Position in 3D space.

```javascript
shape.translate = { x: 0, y: 0, z: 0 };
shape.translate.x = 10;
shape.translate.y += 5;
```

#### rotate

Rotation in radians around each axis.

```javascript
shape.rotate = { x: 0, y: 0, z: 0 };
shape.rotate.y = Math.PI / 4;  // 45 degrees
shape.rotate.z += 0.03;        // Incremental
```

**Helper**: Convert degrees to radians
```javascript
const TAU = Math.PI * 2;
let degrees = 90;
let radians = degrees / 360 * TAU;
```

#### scale

Uniform or per-axis scaling.

```javascript
// Uniform scale
shape.scale = 2;

// Per-axis scale
shape.scale = { x: 1, y: 2, z: 1 };
```

---

### Appearance Properties

#### color

CSS color string.

```javascript
shape.color = '#E62';
shape.color = 'rgb(255, 100, 50)';
shape.color = 'hsl(200, 100%, 50%)';
```

#### stroke

Line thickness.

```javascript
shape.stroke = 10;
```

#### fill

Fill interior of closed shapes.

```javascript
shape.fill = true;
```

#### visible

Control rendering visibility.

```javascript
shape.visible = false;  // Hidden but still in scene
```

#### backface

Control back face rendering.

```javascript
// Show back face with same color
shape.backface = true;

// Hide back face
shape.backface = false;

// Different back face color
shape.backface = '#EA0';
```

---

## Methods

### Rendering

#### updateRenderGraph()

Update and render the entire scene graph.

```javascript
function animate() {
  illo.rotate.y += 0.03;
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

**Important**: Must call on root Illustration, not individual shapes.

---

### Hierarchy

#### addChild(shape)

Add a child shape to an anchor.

```javascript
let group = new Zdog.Anchor({ addTo: illo });
let shape = new Zdog.Ellipse({ diameter: 40 });
group.addChild(shape);
```

#### removeChild(shape)

Remove a child from an anchor.

```javascript
group.removeChild(shape);
```

#### remove()

Remove shape from its parent.

```javascript
shape.remove();
```

---

### Copying

#### copy(options)

Create a duplicate of a shape.

```javascript
let original = new Zdog.Ellipse({
  addTo: illo,
  diameter: 40,
  color: '#636'
});

let duplicate = original.copy({
  translate: { x: 50 },
  color: '#E62'
});
```

#### copyGraph(options)

Copy shape including all children.

```javascript
let group = new Zdog.Anchor({ addTo: illo });
// ... add children ...

let groupCopy = group.copyGraph({
  translate: { x: 100 }
});
```

---

## Animation

### Basic Animation Loop

```javascript
let illo = new Zdog.Illustration({
  element: '.zdog-canvas'
});

let shape = new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636'
});

function animate() {
  // Update properties
  shape.rotate.y += 0.03;

  // Render
  illo.updateRenderGraph();

  // Loop
  requestAnimationFrame(animate);
}

animate();
```

---

### Rotation Animation

```javascript
// Continuous rotation
function animate() {
  illo.rotate.y += 0.03;
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}

// Rotate specific shape
function animate() {
  shape.rotate.z += 0.05;
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}

// Multi-axis rotation
function animate() {
  shape.rotate.x += 0.02;
  shape.rotate.y += 0.03;
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

---

### Position Animation

```javascript
let time = 0;

function animate() {
  time += 0.05;

  // Sine wave motion
  shape.translate.y = Math.sin(time) * 40;

  // Circular motion
  shape.translate.x = Math.cos(time) * 50;
  shape.translate.y = Math.sin(time) * 50;

  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

---

### Scale Animation

```javascript
let time = 0;

function animate() {
  time += 0.05;

  // Pulsing scale
  let scale = 1 + Math.sin(time) * 0.3;
  shape.scale = scale;

  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

---

### Color Animation

Zdog doesn't support direct color interpolation. Use external libraries or manual RGB interpolation.

```javascript
// Manual RGB interpolation
function lerpColor(color1, color2, t) {
  let r1 = parseInt(color1.substr(1,2), 16);
  let g1 = parseInt(color1.substr(3,2), 16);
  let b1 = parseInt(color1.substr(5,2), 16);

  let r2 = parseInt(color2.substr(1,2), 16);
  let g2 = parseInt(color2.substr(3,2), 16);
  let b2 = parseInt(color2.substr(5,2), 16);

  let r = Math.round(r1 + (r2 - r1) * t);
  let g = Math.round(g1 + (g2 - g1) * t);
  let b = Math.round(b1 + (b2 - b1) * t);

  return `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${b.toString(16).padStart(2,'0')}`;
}

let time = 0;
function animate() {
  time += 0.05;
  let t = (Math.sin(time) + 1) / 2;  // 0 to 1
  shape.color = lerpColor('#636', '#E62', t);

  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

---

### Easing

Use easing functions for smooth animations.

```javascript
// Easing functions
const easing = {
  linear: t => t,
  easeInOut: t => t < 0.5
    ? 2 * t * t
    : -1 + (4 - 2 * t) * t,
  easeOut: t => t * (2 - t),
  easeIn: t => t * t
};

// Animate with easing
let progress = 0;
function animate() {
  progress += 0.01;
  if (progress > 1) progress = 0;

  let eased = easing.easeInOut(progress);
  shape.translate.x = eased * 100 - 50;

  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

---

### Interactive Animation

```javascript
let isDragging = false;

let illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  dragRotate: true,
  onDragStart: function() {
    isDragging = true;
  },
  onDragEnd: function() {
    isDragging = false;
  }
});

// Auto-rotate when not dragging
function animate() {
  if (!isDragging) {
    illo.rotate.y += 0.01;
  }
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

---

## Advanced Techniques

### Custom Paths

Create complex shapes using path arrays.

```javascript
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: 0, y: -40 },           // Start point
    { x: 40, y: 0 },            // Line to
    { x: 0, y: 40 },            // Line to
    { x: -40, y: 0 },           // Line to
  ],
  closed: true,
  stroke: 4,
  color: '#636',
  fill: true
});
```

---

### Bezier Curves

```javascript
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: -60, y: 0 },
    {
      bezier: [
        { x: -30, y: -60 },    // Control 1
        { x: 30, y: -60 },     // Control 2
        { x: 60, y: 0 }        // End point
      ]
    },
    {
      bezier: [
        { x: 30, y: 60 },
        { x: -30, y: 60 },
        { x: -60, y: 0 }
      ]
    }
  ],
  closed: true,
  stroke: 4,
  color: '#E62',
  fill: true
});
```

---

### Arc Curves

```javascript
new Zdog.Shape({
  addTo: illo,
  path: [
    { x: -40, y: 0 },
    {
      arc: [
        { x: 0, y: -40 },      // Corner
        { x: 40, y: 0 }        // End
      ]
    }
  ],
  stroke: 4,
  color: '#636'
});
```

---

### Complex Models

Build complex 3D objects using groups.

```javascript
// Robot example
let robot = new Zdog.Anchor({
  addTo: illo,
  translate: { y: -40 }
});

// Head
new Zdog.Box({
  addTo: robot,
  width: 40,
  height: 40,
  depth: 40,
  stroke: 2,
  color: '#636',
  topFace: '#EA0',
  bottomFace: '#E62'
});

// Body
new Zdog.Box({
  addTo: robot,
  translate: { y: 50 },
  width: 50,
  height: 60,
  depth: 40,
  stroke: 2,
  color: '#636'
});

// Arms (group for symmetry)
[-1, 1].forEach(xSide => {
  new Zdog.Box({
    addTo: robot,
    translate: { x: xSide * 40, y: 50 },
    width: 20,
    height: 60,
    depth: 20,
    stroke: 2,
    color: '#C25'
  });
});

// Legs
[-1, 1].forEach(xSide => {
  new Zdog.Box({
    addTo: robot,
    translate: { x: xSide * 15, y: 100 },
    width: 20,
    height: 60,
    depth: 20,
    stroke: 2,
    color: '#C25'
  });
});

// Animate
function animate() {
  robot.rotate.y += 0.03;
  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();
```

---

### Instancing

Efficiently create multiple copies.

```javascript
// Create template
let sphere = new Zdog.Hemisphere({
  diameter: 20,
  stroke: 2,
  color: '#636',
  fill: true
});

// Instance grid
for (let x = -100; x <= 100; x += 40) {
  for (let y = -100; y <= 100; y += 40) {
    sphere.copy({
      addTo: illo,
      translate: { x, y },
      color: `hsl(${(x+100)/2}, 70%, 50%)`
    });
  }
}
```

---

### Responsive Sizing

Make Zdog canvas responsive to container.

```javascript
let illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  resize: true,
  onResize: function(width, height) {
    // Adjust zoom based on size
    this.zoom = Math.min(width, height) / 200;
  }
});

// Manual resize handling
function handleResize() {
  let container = document.querySelector('.zdog-container');
  illo.setSize(container.offsetWidth, container.offsetHeight);
}

window.addEventListener('resize', handleResize);
handleResize();
```

---

### Performance Optimization

**1. Limit Update Frequency**

```javascript
let needsUpdate = false;

element.addEventListener('mousemove', () => {
  needsUpdate = true;
});

function animate() {
  if (needsUpdate) {
    illo.updateRenderGraph();
    needsUpdate = false;
  }
  requestAnimationFrame(animate);
}
```

**2. Use Visibility**

```javascript
// Hide off-screen objects
shapes.forEach(shape => {
  shape.visible = isInView(shape);
});
```

**3. Throttle Drag Rotation**

```javascript
let lastUpdate = 0;

let illo = new Zdog.Illustration({
  element: '.zdog-canvas',
  dragRotate: true,
  onDragMove: function() {
    const now = Date.now();
    if (now - lastUpdate > 16) {  // ~60fps
      this.updateRenderGraph();
      lastUpdate = now;
    }
  }
});
```

---

### SVG vs Canvas

**Canvas** (default):
- Better performance
- Smaller file size
- Rasterized output

```javascript
let illo = new Zdog.Illustration({
  element: 'canvas'  // Canvas element
});
```

**SVG**:
- Vector output (scalable)
- Accessible/indexable
- Slower performance

```javascript
let illo = new Zdog.Illustration({
  element: 'svg'  // SVG element
});
```

---

### Coordinate System

Zdog uses a right-handed coordinate system:

- **X-axis**: Right (+) / Left (-)
- **Y-axis**: Down (+) / Up (-)
- **Z-axis**: Forward (+) / Back (-)

```javascript
// Move right
shape.translate.x = 50;

// Move up
shape.translate.y = -50;

// Move forward
shape.translate.z = 50;
```

---

### Rotation Order

Rotations apply in ZYX order (z-axis first, then y, then x).

```javascript
shape.rotate = {
  x: Math.PI / 4,   // Pitch (applied last)
  y: Math.PI / 6,   // Yaw (applied second)
  z: Math.PI / 8    // Roll (applied first)
};
```

---

## Common Patterns

### Clickable Shapes

Zdog doesn't have built-in click detection. Use canvas coordinates.

```javascript
let canvas = document.querySelector('canvas');

canvas.addEventListener('click', (event) => {
  let rect = canvas.getBoundingClientRect();
  let x = event.clientX - rect.left;
  let y = event.clientY - rect.top;

  // Check if click is near shape (approximate)
  let shapeX = shape.translate.x * illo.zoom + canvas.width / 2;
  let shapeY = shape.translate.y * illo.zoom + canvas.height / 2;

  let distance = Math.sqrt(
    Math.pow(x - shapeX, 2) +
    Math.pow(y - shapeY, 2)
  );

  if (distance < 50) {
    console.log('Shape clicked!');
  }
});
```

---

### Sprite Sheets

Animate through multiple Zdog illustrations.

```javascript
let frames = [];

// Create frames
for (let i = 0; i < 10; i++) {
  let illo = new Zdog.Illustration({
    element: '.canvas',
    zoom: 4
  });

  let shape = new Zdog.Ellipse({
    addTo: illo,
    diameter: 20,
    rotate: { y: i * Math.PI / 10 }
  });

  illo.updateRenderGraph();
  frames.push(illo);
}

// Play frames
let currentFrame = 0;
function animate() {
  currentFrame = (currentFrame + 1) % frames.length;
  frames[currentFrame].updateRenderGraph();
  requestAnimationFrame(animate);
}
```

---

### Particle Systems

Create simple particle effects.

```javascript
let particles = [];

for (let i = 0; i < 50; i++) {
  particles.push({
    shape: new Zdog.Ellipse({
      addTo: illo,
      diameter: 4,
      stroke: 2,
      color: '#636'
    }),
    velocity: {
      x: (Math.random() - 0.5) * 4,
      y: (Math.random() - 0.5) * 4
    }
  });
}

function animate() {
  particles.forEach(p => {
    p.shape.translate.x += p.velocity.x;
    p.shape.translate.y += p.velocity.y;

    // Bounce off edges
    if (Math.abs(p.shape.translate.x) > 100) {
      p.velocity.x *= -1;
    }
    if (Math.abs(p.shape.translate.y) > 100) {
      p.velocity.y *= -1;
    }
  });

  illo.updateRenderGraph();
  requestAnimationFrame(animate);
}
```

---

## TypeScript Support

Zdog includes TypeScript definitions.

```typescript
import Zdog from 'zdog';

const illo: Zdog.Illustration = new Zdog.Illustration({
  element: '.zdog-canvas',
  zoom: 4
});

const shape: Zdog.Ellipse = new Zdog.Ellipse({
  addTo: illo,
  diameter: 80,
  stroke: 20,
  color: '#636'
});
```

---

## Browser Support

- Chrome: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Edge: ✅ Full support
- IE11: ⚠️ Requires polyfills

---

## Resources

- **Official Site**: https://zzz.dog
- **GitHub**: https://github.com/metafizzy/zdog
- **CodePen Examples**: https://codepen.io/desandro/
- **NPM**: `npm install zdog`

---

## License

MIT License - Free for commercial and personal use.



===== FILE: plugins/individual/lightweight-3d-effects/agents/lightweight-3d-effects-architect.md =====

# Lightweight 3D Effects Architect

## Role

Expert 3D/graphics architect specializing in Lightweight 3D Effects scene design, optimization, and best practices.

## Expertise

- Scene architecture and organization
- Performance optimization techniques
- Material and lighting setup
- Asset management and loading strategies
- Rendering optimization
- Cross-browser compatibility

## When to use

Activate this agent when working on:
- Complex 3D scene architecture
- Performance optimization challenges
- Advanced rendering techniques
- Large-scale 3D applications
- Graphics pipeline optimization

## Approach

1. Analyze scene requirements and constraints
2. Design optimal architecture for performance
3. Implement best practices from Lightweight 3D Effects ecosystem
4. Optimize for target platforms and devices
5. Provide detailed implementation guidance

## Tools

This agent has access to:
- Lightweight 3D Effects skill knowledge
- Optimization checklists and patterns
- Performance profiling guidance
- Asset pipeline recommendations



===== FILE: plugins/individual/lightweight-3d-effects/commands/generate_zdog.md =====

# /lightweight-3d-effects-generate_zdog

Lightweight 3D Effects - Generate Zdog

## Description

Executes the generate_zdog script for Lightweight 3D Effects.

## Usage

```bash
/lightweight-3d-effects-generate_zdog
```

## Implementation

This command runs the `generate_zdog.py` script from the Lightweight 3D Effects skill, which provides automated assistance for generate zdog.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/lightweight-3d-effects/commands/setup_vanta.md =====

# /lightweight-3d-effects-setup_vanta

Lightweight 3D Effects - Setup Vanta

## Description

Executes the setup_vanta script for Lightweight 3D Effects.

## Usage

```bash
/lightweight-3d-effects-setup_vanta
```

## Implementation

This command runs the `setup_vanta.py` script from the Lightweight 3D Effects skill, which provides automated assistance for setup vanta.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/lightweight-3d-effects/skills/lightweight-3d-effects/scripts/generate_zdog.py =====

```py
#!/usr/bin/env python3
"""
Zdog Illustration Generator

Generates Zdog pseudo-3D illustrations with various shapes, animations, and complexity levels.

Usage:
    python generate_zdog.py                    # Interactive mode
    python generate_zdog.py --type cube        # Generate cube
    python generate_zdog.py --list             # List available types
"""

import argparse
import os
import sys
from pathlib import Path


def create_html_template(title, zdog_code, css_styles=""):
    """Create complete HTML template with Zdog"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: white;
    }}

    .container {{
      text-align: center;
      padding: 2rem;
    }}

    h1 {{
      font-size: 2.5rem;
      margin-bottom: 1rem;
      text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }}

    .canvas-wrapper {{
      background: rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 2rem;
      backdrop-filter: blur(10px);
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      margin: 2rem auto;
      display: inline-block;
    }}

    canvas {{
      display: block;
      cursor: grab;
    }}

    canvas:active {{
      cursor: grabbing;
    }}

    .info {{
      font-size: 1rem;
      opacity: 0.9;
      margin-top: 1rem;
    }}

    .controls {{
      margin-top: 2rem;
      display: flex;
      gap: 1rem;
      justify-content: center;
      flex-wrap: wrap;
    }}

    button {{
      padding: 0.75rem 1.5rem;
      font-size: 1rem;
      background: rgba(255, 255, 255, 0.2);
      color: white;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.3s;
      backdrop-filter: blur(10px);
    }}

    button:hover {{
      background: rgba(255, 255, 255, 0.3);
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}

    button:active {{
      transform: translateY(0);
    }}

    {css_styles}
  </style>
</head>
<body>
  <div class="container">
    <h1>{title}</h1>
    <div class="canvas-wrapper">
      <canvas class="zdog-canvas" width="480" height="480"></canvas>
    </div>
    <div class="info">
      Drag to rotate • Click controls to interact
    </div>
    <div class="controls" id="controls"></div>
  </div>

  <script src="https://unpkg.com/zdog@1/dist/zdog.dist.min.js"></script>
  <script>
{zdog_code}
  </script>
</body>
</html>"""


def generate_basic_shapes():
    """Generate basic Zdog shapes"""
    code = """    // Create illustration
    let illo = new Zdog.Illustration({
      element: '.zdog-canvas',
      zoom: 4,
      dragRotate: true,
      onDragStart: function() {
        isSpinning = false;
      }
    });

    let isSpinning = true;

    // Ellipse
    new Zdog.Ellipse({
      addTo: illo,
      diameter: 20,
      translate: { x: -60, y: -40 },
      stroke: 5,
      color: '#636',
    });

    // Rectangle
    new Zdog.Rect({
      addTo: illo,
      width: 20,
      height: 20,
      translate: { x: 0, y: -40 },
      stroke: 3,
      color: '#E62',
      fill: true,
    });

    // Rounded Rectangle
    new Zdog.RoundedRect({
      addTo: illo,
      width: 20,
      height: 20,
      cornerRadius: 5,
      translate: { x: 60, y: -40 },
      stroke: 3,
      color: '#EA0',
      fill: true,
    });

    // Polygon (Triangle)
    new Zdog.Polygon({
      addTo: illo,
      sides: 3,
      radius: 12,
      translate: { x: -60, y: 0 },
      stroke: 3,
      color: '#19F',
      fill: true,
    });

    // Polygon (Pentagon)
    new Zdog.Polygon({
      addTo: illo,
      sides: 5,
      radius: 12,
      translate: { x: 0, y: 0 },
      stroke: 3,
      color: '#C25',
      fill: true,
    });

    // Polygon (Hexagon)
    new Zdog.Polygon({
      addTo: illo,
      sides: 6,
      radius: 12,
      translate: { x: 60, y: 0 },
      stroke: 3,
      color: '#4A9',
      fill: true,
    });

    // Hemisphere
    new Zdog.Hemisphere({
      addTo: illo,
      diameter: 20,
      translate: { x: -60, y: 40 },
      stroke: 5,
      color: '#636',
      fill: true,
    });

    // Cylinder
    new Zdog.Cylinder({
      addTo: illo,
      diameter: 16,
      length: 10,
      translate: { x: 0, y: 40 },
      stroke: 3,
      color: '#E62',
      fill: true,
    });

    // Cone
    new Zdog.Cone({
      addTo: illo,
      diameter: 16,
      length: 16,
      translate: { x: 60, y: 40 },
      stroke: 3,
      color: '#EA0',
      fill: true,
    });

    // Animation
    function animate() {
      if (isSpinning) {
        illo.rotate.y += 0.03;
      }
      illo.updateRenderGraph();
      requestAnimationFrame(animate);
    }

    animate();

    // Controls
    const controls = document.getElementById('controls');

    const playBtn = document.createElement('button');
    playBtn.textContent = 'Pause';
    playBtn.addEventListener('click', () => {
      isSpinning = !isSpinning;
      playBtn.textContent = isSpinning ? 'Pause' : 'Play';
    });
    controls.appendChild(playBtn);

    const resetBtn = document.createElement('button');
    resetBtn.textContent = 'Reset';
    resetBtn.addEventListener('click', () => {
      illo.rotate.x = 0;
      illo.rotate.y = 0;
      illo.rotate.z = 0;
    });
    controls.appendChild(resetBtn);"""

    return code


def generate_3d_cube():
    """Generate animated 3D cube"""
    code = """    let illo = new Zdog.Illustration({
      element: '.zdog-canvas',
      zoom: 4,
      dragRotate: true,
    });

    let isSpinning = true;

    // Cube using Box
    let cube = new Zdog.Box({
      addTo: illo,
      width: 40,
      height: 40,
      depth: 40,
      stroke: 2,
      color: '#C25',
      fill: true,
      frontFace: '#EA0',
      rearFace: '#E62',
      leftFace: '#636',
      rightFace: '#C25',
      topFace: '#4A9',
      bottomFace: '#19F'
    });

    function animate() {
      if (isSpinning) {
        cube.rotate.x += 0.02;
        cube.rotate.y += 0.03;
      }
      illo.updateRenderGraph();
      requestAnimationFrame(animate);
    }

    animate();

    // Controls
    const controls = document.getElementById('controls');

    const playBtn = document.createElement('button');
    playBtn.textContent = 'Pause';
    playBtn.addEventListener('click', () => {
      isSpinning = !isSpinning;
      playBtn.textContent = isSpinning ? 'Pause' : 'Play';
    });
    controls.appendChild(playBtn);

    const randomizeBtn = document.createElement('button');
    randomizeBtn.textContent = 'Randomize Colors';
    randomizeBtn.addEventListener('click', () => {
      const randomColor = () => '#' + Math.floor(Math.random()*16777215).toString(16);
      cube.frontFace = randomColor();
      cube.rearFace = randomColor();
      cube.leftFace = randomColor();
      cube.rightFace = randomColor();
      cube.topFace = randomColor();
      cube.bottomFace = randomColor();
    });
    controls.appendChild(randomizeBtn);"""

    return code


def generate_robot():
    """Generate robot character"""
    code = """    let illo = new Zdog.Illustration({
      element: '.zdog-canvas',
      zoom: 3,
      dragRotate: true,
    });

    let isSpinning = true;

    // Robot anchor
    let robot = new Zdog.Anchor({
      addTo: illo,
      translate: { y: -20 }
    });

    // Head
    new Zdog.Box({
      addTo: robot,
      width: 30,
      height: 30,
      depth: 30,
      stroke: 2,
      color: '#636',
      topFace: '#EA0',
      bottomFace: '#E62',
      fill: true
    });

    // Eyes
    [-1, 1].forEach(xSide => {
      new Zdog.Ellipse({
        addTo: robot,
        diameter: 6,
        translate: { x: xSide * 8, y: -4, z: 15 },
        stroke: 2,
        color: '#19F',
        fill: true
      });
    });

    // Antenna
    new Zdog.Shape({
      addTo: robot,
      path: [
        { y: -15 },
        { y: -25 }
      ],
      stroke: 2,
      color: '#EA0'
    });

    new Zdog.Ellipse({
      addTo: robot,
      diameter: 6,
      translate: { y: -25 },
      stroke: 2,
      color: '#E62',
      fill: true
    });

    // Body
    new Zdog.Box({
      addTo: robot,
      translate: { y: 35 },
      width: 35,
      height: 40,
      depth: 25,
      stroke: 2,
      color: '#636',
      fill: true
    });

    // Arms
    [-1, 1].forEach(xSide => {
      let arm = new Zdog.Anchor({
        addTo: robot,
        translate: { x: xSide * 25, y: 25 }
      });

      new Zdog.Box({
        addTo: arm,
        translate: { y: 15 },
        width: 12,
        height: 40,
        depth: 12,
        stroke: 2,
        color: '#C25',
        fill: true
      });

      // Hand
      new Zdog.Ellipse({
        addTo: arm,
        diameter: 10,
        translate: { y: 38 },
        stroke: 2,
        color: '#EA0',
        fill: true
      });
    });

    // Legs
    [-1, 1].forEach(xSide => {
      let leg = new Zdog.Anchor({
        addTo: robot,
        translate: { x: xSide * 10, y: 55 }
      });

      new Zdog.Box({
        addTo: leg,
        translate: { y: 20 },
        width: 12,
        height: 40,
        depth: 12,
        stroke: 2,
        color: '#C25',
        fill: true
      });

      // Foot
      new Zdog.Box({
        addTo: leg,
        translate: { y: 42, z: 5 },
        width: 12,
        height: 8,
        depth: 20,
        stroke: 2,
        color: '#EA0',
        fill: true
      });
    });

    function animate() {
      if (isSpinning) {
        robot.rotate.y += 0.02;
      }
      illo.updateRenderGraph();
      requestAnimationFrame(animate);
    }

    animate();

    // Controls
    const controls = document.getElementById('controls');

    const playBtn = document.createElement('button');
    playBtn.textContent = 'Pause';
    playBtn.addEventListener('click', () => {
      isSpinning = !isSpinning;
      playBtn.textContent = isSpinning ? 'Pause' : 'Play';
    });
    controls.appendChild(playBtn);

    const waveBtn = document.createElement('button');
    waveBtn.textContent = 'Wave';
    let waving = false;
    waveBtn.addEventListener('click', () => {
      if (!waving) {
        waving = true;
        // Simple wave animation would go here
        setTimeout(() => waving = false, 1000);
      }
    });
    controls.appendChild(waveBtn);"""

    return code


def generate_icon_grid():
    """Generate grid of animated icons"""
    code = """    let illo = new Zdog.Illustration({
      element: '.zdog-canvas',
      zoom: 3,
      dragRotate: true,
    });

    const icons = [];
    const colors = ['#636', '#E62', '#EA0', '#19F', '#C25', '#4A9'];
    let time = 0;

    // Create icon grid
    for (let x = -60; x <= 60; x += 40) {
      for (let y = -60; y <= 60; y += 40) {
        const iconGroup = new Zdog.Anchor({
          addTo: illo,
          translate: { x, y }
        });

        // Random icon type
        const iconType = Math.floor(Math.random() * 3);

        if (iconType === 0) {
          // Star
          new Zdog.Polygon({
            addTo: iconGroup,
            sides: 5,
            radius: 8,
            stroke: 2,
            color: colors[Math.floor(Math.random() * colors.length)],
            fill: true
          });
        } else if (iconType === 1) {
          // Heart
          new Zdog.Ellipse({
            addTo: iconGroup,
            diameter: 8,
            translate: { x: -4, y: -2 },
            stroke: 2,
            color: '#E62',
            fill: true
          });
          new Zdog.Ellipse({
            addTo: iconGroup,
            diameter: 8,
            translate: { x: 4, y: -2 },
            stroke: 2,
            color: '#E62',
            fill: true
          });
        } else {
          // Diamond
          new Zdog.Polygon({
            addTo: iconGroup,
            sides: 4,
            radius: 8,
            stroke: 2,
            color: colors[Math.floor(Math.random() * colors.length)],
            fill: true
          });
        }

        icons.push({
          group: iconGroup,
          baseY: y,
          phase: Math.random() * Math.PI * 2
        });
      }
    }

    function animate() {
      time += 0.03;

      // Animate each icon with sine wave
      icons.forEach(icon => {
        icon.group.translate.z = Math.sin(time + icon.phase) * 10;
        icon.group.rotate.z = Math.sin(time + icon.phase) * 0.5;
      });

      illo.rotate.y += 0.01;
      illo.updateRenderGraph();
      requestAnimationFrame(animate);
    }

    animate();

    // Controls
    const controls = document.getElementById('controls');

    const resetBtn = document.createElement('button');
    resetBtn.textContent = 'Reset View';
    resetBtn.addEventListener('click', () => {
      illo.rotate.x = 0;
      illo.rotate.y = 0;
      illo.rotate.z = 0;
    });
    controls.appendChild(resetBtn);"""

    return code


def generate_particle_system():
    """Generate particle system"""
    code = """    let illo = new Zdog.Illustration({
      element: '.zdog-canvas',
      zoom: 2,
      dragRotate: true,
    });

    const particles = [];
    const particleCount = 50;

    // Create particles
    for (let i = 0; i < particleCount; i++) {
      const particle = new Zdog.Ellipse({
        addTo: illo,
        diameter: 4,
        stroke: 2,
        color: `hsl(${Math.random() * 360}, 70%, 60%)`,
        fill: true
      });

      particles.push({
        shape: particle,
        velocity: {
          x: (Math.random() - 0.5) * 3,
          y: (Math.random() - 0.5) * 3,
          z: (Math.random() - 0.5) * 3
        },
        rotation: {
          x: (Math.random() - 0.5) * 0.1,
          y: (Math.random() - 0.5) * 0.1,
          z: (Math.random() - 0.5) * 0.1
        }
      });
    }

    const bounds = 100;

    function animate() {
      particles.forEach(p => {
        // Update position
        p.shape.translate.x += p.velocity.x;
        p.shape.translate.y += p.velocity.y;
        p.shape.translate.z += p.velocity.z;

        // Update rotation
        p.shape.rotate.x += p.rotation.x;
        p.shape.rotate.y += p.rotation.y;
        p.shape.rotate.z += p.rotation.z;

        // Bounce off boundaries
        if (Math.abs(p.shape.translate.x) > bounds) {
          p.velocity.x *= -1;
        }
        if (Math.abs(p.shape.translate.y) > bounds) {
          p.velocity.y *= -1;
        }
        if (Math.abs(p.shape.translate.z) > bounds) {
          p.velocity.z *= -1;
        }
      });

      illo.updateRenderGraph();
      requestAnimationFrame(animate);
    }

    animate();

    // Controls
    const controls = document.getElementById('controls');

    const resetBtn = document.createElement('button');
    resetBtn.textContent = 'Reset Particles';
    resetBtn.addEventListener('click', () => {
      particles.forEach(p => {
        p.shape.translate.x = 0;
        p.shape.translate.y = 0;
        p.shape.translate.z = 0;
      });
    });
    controls.appendChild(resetBtn);

    const speedUpBtn = document.createElement('button');
    speedUpBtn.textContent = 'Speed Up';
    speedUpBtn.addEventListener('click', () => {
      particles.forEach(p => {
        p.velocity.x *= 1.2;
        p.velocity.y *= 1.2;
        p.velocity.z *= 1.2;
      });
    });
    controls.appendChild(speedUpBtn);

    const slowDownBtn = document.createElement('button');
    slowDownBtn.textContent = 'Slow Down';
    slowDownBtn.addEventListener('click', () => {
      particles.forEach(p => {
        p.velocity.x *= 0.8;
        p.velocity.y *= 0.8;
        p.velocity.z *= 0.8;
      });
    });
    controls.appendChild(slowDownBtn);"""

    return code


def generate_spiral():
    """Generate spiral animation"""
    code = """    let illo = new Zdog.Illustration({
      element: '.zdog-canvas',
      zoom: 2,
      dragRotate: true,
    });

    let isSpinning = true;
    const spiral = new Zdog.Anchor({ addTo: illo });
    const spheres = [];

    // Create spiral
    const turns = 5;
    const sphereCount = 50;

    for (let i = 0; i < sphereCount; i++) {
      const progress = i / sphereCount;
      const angle = progress * Math.PI * 2 * turns;
      const radius = progress * 60;

      const hue = progress * 360;

      const sphere = new Zdog.Ellipse({
        addTo: spiral,
        diameter: 6,
        translate: {
          x: Math.cos(angle) * radius,
          y: progress * 80 - 40,
          z: Math.sin(angle) * radius
        },
        stroke: 3,
        color: `hsl(${hue}, 70%, 60%)`,
        fill: true
      });

      spheres.push({ shape: sphere, angle: angle, radius: radius });
    }

    let time = 0;

    function animate() {
      time += 0.02;

      if (isSpinning) {
        spiral.rotate.y += 0.02;
      }

      // Animate each sphere
      spheres.forEach((s, i) => {
        const progress = i / sphereCount;
        const wave = Math.sin(time + progress * Math.PI * 2) * 5;
        s.shape.translate.z = Math.sin(s.angle) * s.radius + wave;
      });

      illo.updateRenderGraph();
      requestAnimationFrame(animate);
    }

    animate();

    // Controls
    const controls = document.getElementById('controls');

    const playBtn = document.createElement('button');
    playBtn.textContent = 'Pause';
    playBtn.addEventListener('click', () => {
      isSpinning = !isSpinning;
      playBtn.textContent = isSpinning ? 'Pause' : 'Play';
    });
    controls.appendChild(playBtn);

    const resetBtn = document.createElement('button');
    resetBtn.textContent = 'Reset View';
    resetBtn.addEventListener('click', () => {
      illo.rotate.x = 0;
      illo.rotate.y = 0;
      illo.rotate.z = 0;
    });
    controls.appendChild(resetBtn);"""

    return code


ILLUSTRATION_TYPES = {
    'shapes': {
        'name': 'Basic Shapes',
        'description': 'Grid of all basic Zdog shapes',
        'generator': generate_basic_shapes
    },
    'cube': {
        'name': '3D Cube',
        'description': 'Animated 3D cube with colored faces',
        'generator': generate_3d_cube
    },
    'robot': {
        'name': 'Robot Character',
        'description': 'Complex robot model with multiple parts',
        'generator': generate_robot
    },
    'icons': {
        'name': 'Icon Grid',
        'description': 'Grid of animated icons with wave effect',
        'generator': generate_icon_grid
    },
    'particles': {
        'name': 'Particle System',
        'description': 'Bouncing particle system',
        'generator': generate_particle_system
    },
    'spiral': {
        'name': 'Spiral Animation',
        'description': 'Rotating spiral with wave animation',
        'generator': generate_spiral
    }
}


def list_types():
    """List all available illustration types"""
    print("\n📦 Available Zdog Illustration Types:\n")
    for key, info in ILLUSTRATION_TYPES.items():
        print(f"  {key:12} - {info['name']}")
        print(f"               {info['description']}")
        print()


def generate_illustration(type_key, output_path):
    """Generate Zdog illustration"""
    if type_key not in ILLUSTRATION_TYPES:
        print(f"❌ Error: Unknown type '{type_key}'")
        print(f"   Use --list to see available types")
        return False

    info = ILLUSTRATION_TYPES[type_key]

    print(f"\n🎨 Generating {info['name']}...")

    # Generate code
    code = info['generator']()

    # Create HTML
    html = create_html_template(info['name'], code)

    # Write file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(html)

    print(f"✅ Generated: {output_file}")
    print(f"   Open in browser to view")

    return True


def interactive_mode():
    """Interactive CLI mode"""
    print("\n" + "="*60)
    print("  🎨 Zdog Illustration Generator")
    print("="*60)

    print("\nSelect illustration type:\n")
    types_list = list(ILLUSTRATION_TYPES.keys())
    for i, key in enumerate(types_list, 1):
        info = ILLUSTRATION_TYPES[key]
        print(f"  {i}. {info['name']}")
        print(f"     {info['description']}")
        print()

    while True:
        try:
            choice = input("Enter number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return False

            choice_num = int(choice)
            if 1 <= choice_num <= len(types_list):
                type_key = types_list[choice_num - 1]
                break
            else:
                print(f"❌ Please enter 1-{len(types_list)}")
        except ValueError:
            print("❌ Please enter a valid number")

    # Get output filename
    default_name = f"zdog_{type_key}.html"
    output_name = input(f"\nOutput filename [{default_name}]: ").strip()
    if not output_name:
        output_name = default_name

    output_path = Path.cwd() / output_name

    return generate_illustration(type_key, output_path)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Zdog pseudo-3D illustrations',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--type',
        choices=list(ILLUSTRATION_TYPES.keys()),
        help='Illustration type to generate'
    )

    parser.add_argument(
        '--output',
        default='zdog_illustration.html',
        help='Output HTML file path (default: zdog_illustration.html)'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available illustration types'
    )

    args = parser.parse_args()

    # List types
    if args.list:
        list_types()
        return 0

    # Interactive mode
    if not args.type:
        success = interactive_mode()
        return 0 if success else 1

    # Direct generation
    success = generate_illustration(args.type, args.output)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

```


===== FILE: plugins/individual/lightweight-3d-effects/skills/lightweight-3d-effects/scripts/setup_vanta.py =====

```py
#!/usr/bin/env python3
"""
Vanta.js Background Setup Script

Generates Vanta.js animated backgrounds with various effects and configurations.

Usage:
    python setup_vanta.py                      # Interactive mode
    python setup_vanta.py --effect waves       # Generate waves effect
    python setup_vanta.py --list               # List available effects
"""

import argparse
import os
import sys
from pathlib import Path


def create_html_template(title, effect_name, effect_code, css_styles=""):
    """Create complete HTML template with Vanta.js effect"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      overflow-x: hidden;
    }}

    #vanta-bg {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100vh;
      z-index: -1;
    }}

    .container {{
      position: relative;
      z-index: 1;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: white;
      text-align: center;
      padding: 2rem;
    }}

    h1 {{
      font-size: 4rem;
      margin-bottom: 1rem;
      text-shadow: 0 4px 20px rgba(0,0,0,0.3);
      font-weight: 700;
    }}

    .subtitle {{
      font-size: 1.5rem;
      opacity: 0.9;
      margin-bottom: 2rem;
      text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }}

    .controls {{
      display: flex;
      gap: 1rem;
      margin-top: 2rem;
      flex-wrap: wrap;
      justify-content: center;
    }}

    button {{
      padding: 1rem 2rem;
      font-size: 1rem;
      background: rgba(255, 255, 255, 0.2);
      color: white;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-radius: 50px;
      cursor: pointer;
      transition: all 0.3s;
      backdrop-filter: blur(10px);
      font-weight: 600;
    }}

    button:hover {{
      background: rgba(255, 255, 255, 0.3);
      transform: translateY(-2px);
      box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }}

    button:active {{
      transform: translateY(0);
    }}

    .card {{
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border-radius: 20px;
      padding: 3rem;
      margin-top: 3rem;
      border: 1px solid rgba(255, 255, 255, 0.2);
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      max-width: 600px;
    }}

    .card h2 {{
      margin-bottom: 1rem;
      font-size: 2rem;
    }}

    .card p {{
      font-size: 1.1rem;
      line-height: 1.6;
      opacity: 0.9;
    }}

    {css_styles}
  </style>
</head>
<body>
  <div id="vanta-bg"></div>

  <div class="container">
    <h1>{title}</h1>
    <div class="subtitle">Animated with Vanta.js {effect_name} effect</div>

    <div class="card">
      <h2>About This Effect</h2>
      <p>This background is powered by Vanta.js, a library for animated 3D backgrounds using WebGL and Three.js.</p>
    </div>

    <div class="controls" id="controls"></div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
  <script src="{effect_code['cdn']}"></script>
  <script>
    let vantaEffect = {effect_code['init']}

    // Controls
    const controls = document.getElementById('controls');

    const destroyBtn = document.createElement('button');
    destroyBtn.textContent = 'Pause Effect';
    let isDestroyed = false;
    destroyBtn.addEventListener('click', () => {{
      if (!isDestroyed) {{
        vantaEffect.destroy();
        isDestroyed = true;
        destroyBtn.textContent = 'Resume Effect';
      }} else {{
        vantaEffect = {effect_code['init']}
        isDestroyed = false;
        destroyBtn.textContent = 'Pause Effect';
      }}
    }});
    controls.appendChild(destroyBtn);

    {effect_code.get('controls', '')}
  </script>
</body>
</html>"""


def generate_waves():
    """Generate WAVES effect"""
    return {
        'cdn': 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.waves.min.js',
        'init': """VANTA.WAVES({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      color: 0x23153c,
      shininess: 30.00,
      waveHeight: 15.00,
      waveSpeed: 0.75,
      zoom: 0.65
    });""",
        'controls': """
    const increaseWavesBtn = document.createElement('button');
    increaseWavesBtn.textContent = 'Bigger Waves';
    increaseWavesBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ waveHeight: 25 });
      }
    });
    controls.appendChild(increaseWavesBtn);

    const fasterBtn = document.createElement('button');
    fasterBtn.textContent = 'Faster';
    fasterBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ waveSpeed: 1.5 });
      }
    });
    controls.appendChild(fasterBtn);"""
    }


def generate_clouds():
    """Generate CLOUDS effect"""
    return {
        'cdn': 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.clouds.min.js',
        'init': """VANTA.CLOUDS({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      skyColor: 0x68b8d7,
      cloudColor: 0xadc1de,
      cloudShadowColor: 0x183550,
      sunColor: 0xff9919,
      sunGlareColor: 0xff6633,
      sunlightColor: 0xff9933,
      speed: 1.00
    });""",
        'controls': """
    const fasterBtn = document.createElement('button');
    fasterBtn.textContent = 'Faster';
    fasterBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ speed: 2.0 });
      }
    });
    controls.appendChild(fasterBtn);

    const slowerBtn = document.createElement('button');
    slowerBtn.textContent = 'Slower';
    slowerBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ speed: 0.5 });
      }
    });
    controls.appendChild(slowerBtn);"""
    }


def generate_birds():
    """Generate BIRDS effect"""
    return {
        'cdn': 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.birds.min.js',
        'init': """VANTA.BIRDS({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      backgroundColor: 0x23153c,
      color1: 0xff0090,
      color2: 0xff6633,
      colorMode: "lerp",
      birdSize: 1.00,
      wingSpan: 20.00,
      speedLimit: 5.00,
      separation: 20.00,
      alignment: 20.00,
      cohesion: 20.00,
      quantity: 3.00
    });""",
        'controls': """
    const moreBirdsBtn = document.createElement('button');
    moreBirdsBtn.textContent = 'More Birds';
    moreBirdsBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ quantity: 5.00 });
      }
    });
    controls.appendChild(moreBirdsBtn);

    const biggerBirdsBtn = document.createElement('button');
    biggerBirdsBtn.textContent = 'Bigger Birds';
    biggerBirdsBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ birdSize: 1.5, wingSpan: 30 });
      }
    });
    controls.appendChild(biggerBirdsBtn);"""
    }


def generate_net():
    """Generate NET effect"""
    return {
        'cdn': 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js',
        'init': """VANTA.NET({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      color: 0x3fafff,
      backgroundColor: 0x23153c,
      points: 10.00,
      maxDistance: 20.00,
      spacing: 15.00,
      showDots: true
    });""",
        'controls': """
    const morePointsBtn = document.createElement('button');
    morePointsBtn.textContent = 'More Points';
    morePointsBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ points: 15.00 });
      }
    });
    controls.appendChild(morePointsBtn);

    const denseNetBtn = document.createElement('button');
    denseNetBtn.textContent = 'Dense Network';
    denseNetBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ maxDistance: 30.00, spacing: 10.00 });
      }
    });
    controls.appendChild(denseNetBtn);"""
    }


def generate_cells():
    """Generate CELLS effect"""
    return {
        'cdn': 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.cells.min.js',
        'init': """VANTA.CELLS({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      color1: 0x18b0c6,
      color2: 0xff6633,
      size: 1.50,
      speed: 1.00
    });""",
        'controls': """
    const biggerCellsBtn = document.createElement('button');
    biggerCellsBtn.textContent = 'Bigger Cells';
    biggerCellsBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ size: 2.50 });
      }
    });
    controls.appendChild(biggerCellsBtn);

    const fasterBtn = document.createElement('button');
    fasterBtn.textContent = 'Faster Growth';
    fasterBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ speed: 2.00 });
      }
    });
    controls.appendChild(fasterBtn);"""
    }


def generate_fog():
    """Generate FOG effect"""
    return {
        'cdn': 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.fog.min.js',
        'init': """VANTA.FOG({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      highlightColor: 0xff3f81,
      midtoneColor: 0xff1f51,
      lowlightColor: 0x2d1b46,
      baseColor: 0xffebff,
      blurFactor: 0.60,
      speed: 1.00,
      zoom: 1.00
    });""",
        'controls': """
    const moreBlurBtn = document.createElement('button');
    moreBlurBtn.textContent = 'More Blur';
    moreBlurBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ blurFactor: 0.90 });
      }
    });
    controls.appendChild(moreBlurBtn);

    const fasterBtn = document.createElement('button');
    fasterBtn.textContent = 'Faster';
    fasterBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ speed: 2.00 });
      }
    });
    controls.appendChild(fasterBtn);"""
    }


def generate_globe():
    """Generate GLOBE effect"""
    return {
        'cdn': 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.globe.min.js',
        'init': """VANTA.GLOBE({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      color: 0x3fafff,
      color2: 0xff6633,
      size: 1.50,
      backgroundColor: 0x23153c
    });""",
        'controls': """
    const biggerGlobeBtn = document.createElement('button');
    biggerGlobeBtn.textContent = 'Bigger Globe';
    biggerGlobeBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ size: 2.00 });
      }
    });
    controls.appendChild(biggerGlobeBtn);"""
    }


def generate_rings():
    """Generate RINGS effect"""
    return {
        'cdn': 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.rings.min.js',
        'init': """VANTA.RINGS({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      backgroundColor: 0x23153c,
      color: 0xff3f81
    });""",
        'controls': ''
    }


def generate_dots():
    """Generate DOTS effect"""
    return {
        'cdn': 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.dots.min.js',
        'init': """VANTA.DOTS({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      color: 0xff3f81,
      color2: 0xffffff,
      backgroundColor: 0x23153c,
      size: 3.00,
      spacing: 35.00
    });""",
        'controls': """
    const biggerDotsBtn = document.createElement('button');
    biggerDotsBtn.textContent = 'Bigger Dots';
    biggerDotsBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ size: 5.00 });
      }
    });
    controls.appendChild(biggerDotsBtn);

    const moreDotsBtn = document.createElement('button');
    moreDotsBtn.textContent = 'More Dots';
    moreDotsBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ spacing: 25.00 });
      }
    });
    controls.appendChild(moreDotsBtn);"""
    }


def generate_topology():
    """Generate TOPOLOGY effect"""
    return {
        'cdn': 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.topology.min.js',
        'init': """VANTA.TOPOLOGY({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      color: 0xff3f81,
      backgroundColor: 0x23153c
    });""",
        'controls': ''
    }


def generate_trunk():
    """Generate TRUNK effect"""
    return {
        'cdn': 'https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.trunk.min.js',
        'init': """VANTA.TRUNK({
      el: "#vanta-bg",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      backgroundColor: 0x23153c,
      color: 0xff3f81,
      spacing: 2.00,
      chaos: 4.00
    });""",
        'controls': """
    const moreChaosBtn = document.createElement('button');
    moreChaosBtn.textContent = 'More Chaos';
    moreChaosBtn.addEventListener('click', () => {
      if (vantaEffect && vantaEffect.setOptions) {
        vantaEffect.setOptions({ chaos: 8.00 });
      }
    });
    controls.appendChild(moreChaosBtn);"""
    }


VANTA_EFFECTS = {
    'waves': {
        'name': 'Waves',
        'description': 'Animated wave surface with reflections',
        'generator': generate_waves
    },
    'clouds': {
        'name': 'Clouds',
        'description': 'Volumetric cloud effect with sun',
        'generator': generate_clouds
    },
    'birds': {
        'name': 'Birds',
        'description': 'Flocking birds simulation',
        'generator': generate_birds
    },
    'net': {
        'name': 'Network',
        'description': 'Particle network with connecting lines',
        'generator': generate_net
    },
    'cells': {
        'name': 'Cells',
        'description': 'Organic cellular growth pattern',
        'generator': generate_cells
    },
    'fog': {
        'name': 'Fog',
        'description': 'Misty fog effect with depth',
        'generator': generate_fog
    },
    'globe': {
        'name': 'Globe',
        'description': 'Rotating globe with points',
        'generator': generate_globe
    },
    'rings': {
        'name': 'Rings',
        'description': 'Concentric animated rings',
        'generator': generate_rings
    },
    'dots': {
        'name': 'Dots',
        'description': 'Particle dot field effect',
        'generator': generate_dots
    },
    'topology': {
        'name': 'Topology',
        'description': 'Topographic mesh surface',
        'generator': generate_topology
    },
    'trunk': {
        'name': 'Trunk',
        'description': 'Abstract trunk/tree structure',
        'generator': generate_trunk
    }
}


def list_effects():
    """List all available Vanta effects"""
    print("\n✨ Available Vanta.js Effects:\n")
    for key, info in VANTA_EFFECTS.items():
        print(f"  {key:12} - {info['name']}")
        print(f"               {info['description']}")
        print()


def generate_effect(effect_key, output_path):
    """Generate Vanta.js effect"""
    if effect_key not in VANTA_EFFECTS:
        print(f"❌ Error: Unknown effect '{effect_key}'")
        print(f"   Use --list to see available effects")
        return False

    info = VANTA_EFFECTS[effect_key]

    print(f"\n✨ Generating {info['name']} effect...")

    # Generate effect code
    effect_code = info['generator']()

    # Create HTML
    html = create_html_template(
        f"Vanta.js {info['name']}",
        info['name'],
        effect_code
    )

    # Write file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(html)

    print(f"✅ Generated: {output_file}")
    print(f"   Open in browser to view")

    return True


def interactive_mode():
    """Interactive CLI mode"""
    print("\n" + "="*60)
    print("  ✨ Vanta.js Background Setup")
    print("="*60)

    print("\nSelect Vanta effect:\n")
    effects_list = list(VANTA_EFFECTS.keys())
    for i, key in enumerate(effects_list, 1):
        info = VANTA_EFFECTS[key]
        print(f"  {i:2}. {info['name']}")
        print(f"      {info['description']}")
        print()

    while True:
        try:
            choice = input("Enter number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return False

            choice_num = int(choice)
            if 1 <= choice_num <= len(effects_list):
                effect_key = effects_list[choice_num - 1]
                break
            else:
                print(f"❌ Please enter 1-{len(effects_list)}")
        except ValueError:
            print("❌ Please enter a valid number")

    # Get output filename
    default_name = f"vanta_{effect_key}.html"
    output_name = input(f"\nOutput filename [{default_name}]: ").strip()
    if not output_name:
        output_name = default_name

    output_path = Path.cwd() / output_name

    return generate_effect(effect_key, output_path)


def main():
    parser = argparse.ArgumentParser(
        description='Setup Vanta.js animated backgrounds',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--effect',
        choices=list(VANTA_EFFECTS.keys()),
        help='Vanta effect to generate'
    )

    parser.add_argument(
        '--output',
        default='vanta_background.html',
        help='Output HTML file path (default: vanta_background.html)'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available effects'
    )

    args = parser.parse_args()

    # List effects
    if args.list:
        list_effects()
        return 0

    # Interactive mode
    if not args.effect:
        success = interactive_mode()
        return 0 if success else 1

    # Direct generation
    success = generate_effect(args.effect, args.output)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

```


===== FILE: plugins/individual/lightweight-3d-effects/skills/lightweight-3d-effects/assets/examples/README.md =====

# Lightweight 3D Effects - Production Examples

Real-world patterns and examples combining Vanta.js, Zdog, and Vanilla-Tilt for production applications.

---

## Table of Contents

1. [Hero Sections](#1-hero-sections)
2. [Product Cards](#2-product-cards)
3. [Portfolio Layouts](#3-portfolio-layouts)
4. [Interactive Dashboards](#4-interactive-dashboards)
5. [Marketing Pages](#5-marketing-pages)
6. [E-Commerce](#6-e-commerce)
7. [SaaS Landing Pages](#7-saas-landing-pages)
8. [Performance Patterns](#8-performance-patterns)

---

## 1. Hero Sections

### Example 1.1: Split Hero with Vanta + Zdog Logo

**Use Case**: SaaS landing page with animated background and brand icon

```html
<div class="hero-split">
  <div id="vanta-bg"></div>

  <div class="hero-content">
    <canvas class="logo-zdog" width="200" height="200"></canvas>
    <h1>Welcome to Your Product</h1>
    <p>Tagline describing your amazing service</p>
    <button class="cta-button tilt-btn" data-tilt>Get Started</button>
  </div>
</div>
```

```css
.hero-split {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

#vanta-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}

.hero-content {
  text-align: center;
  z-index: 1;
  color: white;
}

.logo-zdog {
  display: block;
  margin: 0 auto 2rem;
  filter: drop-shadow(0 10px 30px rgba(0,0,0,0.3));
}

.cta-button {
  padding: 1rem 3rem;
  font-size: 1.2rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
  border-radius: 50px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  transform-style: preserve-3d;
}
```

```javascript
// Vanta background
VANTA.NET({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  color: 0x3fafff,
  backgroundColor: 0x23153c,
  points: 10,
  maxDistance: 20
});

// Zdog logo
const logoIllo = new Zdog.Illustration({
  element: '.logo-zdog',
  zoom: 3,
  dragRotate: false
});

// Create your brand icon here
const logo = new Zdog.Shape({
  addTo: logoIllo,
  path: [
    { x: -30, y: -30 },
    { x: 30, y: -30 },
    { x: 0, y: 30 }
  ],
  closed: true,
  stroke: 8,
  color: '#fff',
  fill: true
});

function animate() {
  logo.rotate.y += 0.02;
  logoIllo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();

// Tilt button
VanillaTilt.init(document.querySelector(".cta-button"), {
  max: 15,
  glare: true,
  "max-glare": 0.5,
  scale: 1.1
});
```

---

### Example 1.2: Full-Screen Hero with Scroll Indicator

**Use Case**: Portfolio site with immersive background and scroll prompt

```html
<section class="hero-fullscreen">
  <div id="vanta-bg"></div>

  <div class="hero-content">
    <h1 class="hero-title">Creative Developer</h1>
    <p class="hero-subtitle">Building beautiful experiences</p>

    <div class="scroll-indicator">
      <canvas class="scroll-zdog" width="60" height="80"></canvas>
      <span>Scroll to explore</span>
    </div>
  </div>
</section>
```

```javascript
// Vanta clouds
VANTA.CLOUDS({
  el: "#vanta-bg",
  skyColor: 0x68b8d7,
  cloudColor: 0xadc1de,
  speed: 0.5
});

// Animated scroll indicator
const scrollIllo = new Zdog.Illustration({
  element: '.scroll-zdog',
  zoom: 2
});

// Mouse with scrolling animation
const mouse = new Zdog.RoundedRect({
  addTo: scrollIllo,
  width: 20,
  height: 30,
  cornerRadius: 10,
  stroke: 2,
  color: '#fff'
});

const wheel = new Zdog.Ellipse({
  addTo: scrollIllo,
  diameter: 4,
  translate: { y: -8 },
  stroke: 2,
  color: '#fff',
  fill: true
});

let wheelY = -8;
function animate() {
  wheelY += 0.5;
  if (wheelY > 8) wheelY = -8;
  wheel.translate.y = wheelY;

  scrollIllo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();
```

---

## 2. Product Cards

### Example 2.1: Pricing Cards with Tilt + Zdog Icons

**Use Case**: SaaS pricing page with interactive plan cards

```html
<div class="pricing-grid">
  <div class="pricing-card tilt-card" data-tilt>
    <canvas class="plan-icon" width="100" height="100"></canvas>
    <h3>Starter</h3>
    <p class="price">$9<span>/mo</span></p>
    <ul>
      <li>Feature 1</li>
      <li>Feature 2</li>
      <li>Feature 3</li>
    </ul>
    <button class="select-btn">Select Plan</button>
  </div>

  <!-- Repeat for Pro and Enterprise -->
</div>
```

```javascript
// Initialize tilt for all cards
VanillaTilt.init(document.querySelectorAll(".pricing-card"), {
  max: 10,
  speed: 400,
  glare: true,
  "max-glare": 0.2,
  scale: 1.02
});

// Create unique Zdog icon for each plan
const starterIcon = new Zdog.Illustration({
  element: document.querySelectorAll('.plan-icon')[0],
  zoom: 2
});

new Zdog.Ellipse({
  addTo: starterIcon,
  diameter: 30,
  stroke: 5,
  color: '#4CAF50',
  fill: true
});

// Animate
function animate() {
  starterIcon.rotate.y += 0.02;
  starterIcon.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();
```

```css
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  padding: 4rem 2rem;
}

.pricing-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
  transform-style: preserve-3d;
}

.plan-icon {
  display: block;
  margin: 0 auto 1.5rem;
  transform: translateZ(30px);
}

.price {
  font-size: 3rem;
  font-weight: 700;
  transform: translateZ(20px);
}

.select-btn {
  transform: translateZ(40px);
  /* Additional button styles */
}
```

---

### Example 2.2: Product Showcase Gallery

**Use Case**: E-commerce product grid with hover effects

```html
<div class="product-gallery">
  <div class="product-card tilt-card" data-tilt>
    <div class="product-badge">NEW</div>
    <img src="product1.jpg" alt="Product" class="product-image">
    <canvas class="product-icon" width="80" height="80"></canvas>
    <h3>Product Name</h3>
    <p class="product-price">$99.99</p>
    <button class="add-to-cart">Add to Cart</button>
  </div>
</div>
```

```javascript
VanillaTilt.init(document.querySelectorAll(".product-card"), {
  max: 12,
  speed: 400,
  glare: true,
  "max-glare": 0.3,
  scale: 1.05
});

// Add floating Zdog indicator on each card
document.querySelectorAll('.product-icon').forEach((canvas, i) => {
  const illo = new Zdog.Illustration({
    element: canvas,
    zoom: 1.5
  });

  // Star rating indicator
  for (let j = 0; j < 5; j++) {
    new Zdog.Polygon({
      addTo: illo,
      sides: 5,
      radius: 6,
      translate: { x: (j - 2) * 14 },
      stroke: 2,
      color: '#FFD700',
      fill: true
    });
  }

  function animate() {
    illo.rotate.z = Math.sin(Date.now() * 0.001 + i) * 0.1;
    illo.updateRenderGraph();
    requestAnimationFrame(animate);
  }
  animate();
});
```

---

## 3. Portfolio Layouts

### Example 3.1: Project Grid with Vanta Backgrounds

**Use Case**: Portfolio with per-project animated backgrounds

```html
<div class="portfolio-grid">
  <div class="project-card">
    <div class="project-vanta" data-effect="waves"></div>
    <div class="project-content tilt-content" data-tilt>
      <canvas class="project-icon" width="80" height="80"></canvas>
      <h3>Project Title</h3>
      <p>Project description</p>
      <a href="#" class="view-project">View Project →</a>
    </div>
  </div>
</div>
```

```javascript
// Initialize Vanta for each project card
document.querySelectorAll('.project-card').forEach((card, index) => {
  const vantaEl = card.querySelector('.project-vanta');
  const effect = vantaEl.dataset.effect;

  const effects = {
    waves: () => VANTA.WAVES({
      el: vantaEl,
      color: 0x23153c,
      waveHeight: 10,
      zoom: 0.75
    }),
    cells: () => VANTA.CELLS({
      el: vantaEl,
      color1: 0x18b0c6,
      size: 1.5
    }),
    net: () => VANTA.NET({
      el: vantaEl,
      color: 0x3fafff,
      points: 8
    })
  };

  effects[effect]();

  // Tilt only the content overlay
  VanillaTilt.init(card.querySelector('.project-content'), {
    max: 8,
    scale: 1.02,
    glare: true,
    "max-glare": 0.2
  });
});
```

```css
.project-card {
  position: relative;
  height: 400px;
  border-radius: 20px;
  overflow: hidden;
}

.project-vanta {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.project-content {
  position: relative;
  z-index: 2;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  padding: 2rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transform-style: preserve-3d;
}

.project-icon {
  transform: translateZ(30px);
}

.project-content h3 {
  transform: translateZ(20px);
}
```

---

## 4. Interactive Dashboards

### Example 4.1: Stats Dashboard with Zdog Charts

**Use Case**: Analytics dashboard with 3D data visualization

```html
<div class="dashboard">
  <div id="vanta-bg"></div>

  <div class="stats-grid">
    <div class="stat-card tilt-card" data-tilt>
      <canvas class="stat-chart" width="200" height="200"></canvas>
      <h3>Users</h3>
      <p class="stat-value">12,345</p>
      <span class="stat-change">+12.5%</span>
    </div>
  </div>
</div>
```

```javascript
// Subtle background
VANTA.TOPOLOGY({
  el: "#vanta-bg",
  color: 0x667eea,
  backgroundColor: 0xf8f9fa
});

// Zdog bar chart
const chartIllo = new Zdog.Illustration({
  element: '.stat-chart',
  zoom: 2,
  dragRotate: true
});

const data = [10, 25, 15, 30, 20, 35, 28];
const barWidth = 8;
const spacing = 12;

data.forEach((value, i) => {
  new Zdog.Box({
    addTo: chartIllo,
    width: barWidth,
    height: value,
    depth: barWidth,
    translate: {
      x: (i - 3) * spacing,
      y: value / 2
    },
    stroke: 1,
    color: `hsl(${220 + i * 10}, 70%, 60%)`,
    fill: true,
    topFace: '#667eea',
    bottomFace: '#764ba2'
  });
});

function animate() {
  chartIllo.rotate.y += 0.01;
  chartIllo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();

// Tilt cards
VanillaTilt.init(document.querySelectorAll(".stat-card"), {
  max: 5,
  glare: false,
  scale: 1.01
});
```

---

## 5. Marketing Pages

### Example 5.1: Feature Showcase with Staggered Animations

**Use Case**: Product marketing page with animated feature cards

```html
<section class="features-section">
  <div id="vanta-bg"></div>

  <div class="features-container">
    <div class="feature-item tilt-card" data-tilt>
      <canvas class="feature-icon" width="120" height="120"></canvas>
      <h3>Lightning Fast</h3>
      <p>Optimized for performance</p>
    </div>

    <div class="feature-item tilt-card" data-tilt data-delay="100">
      <canvas class="feature-icon" width="120" height="120"></canvas>
      <h3>Secure</h3>
      <p>Enterprise-grade security</p>
    </div>

    <div class="feature-item tilt-card" data-tilt data-delay="200">
      <canvas class="feature-icon" width="120" height="120"></canvas>
      <h3>Scalable</h3>
      <p>Grows with your business</p>
    </div>
  </div>
</section>
```

```javascript
// Vanta background
VANTA.DOTS({
  el: "#vanta-bg",
  color: 0xff3f81,
  backgroundColor: 0xffffff,
  size: 2,
  spacing: 30
});

// Staggered tilt initialization
document.querySelectorAll('.feature-item').forEach((item, index) => {
  const delay = parseInt(item.dataset.delay) || 0;

  setTimeout(() => {
    VanillaTilt.init(item, {
      max: 12,
      speed: 400,
      glare: true,
      "max-glare": 0.2
    });

    // Fade in animation
    item.style.opacity = '1';
    item.style.transform = 'translateY(0)';
  }, delay);

  // Initial state
  item.style.opacity = '0';
  item.style.transform = 'translateY(20px)';
  item.style.transition = 'opacity 0.6s, transform 0.6s';
});

// Create unique Zdog icons
const icons = document.querySelectorAll('.feature-icon');

// Lightning icon
const lightning = new Zdog.Illustration({
  element: icons[0],
  zoom: 2
});

new Zdog.Shape({
  addTo: lightning,
  path: [
    { x: 0, y: -30 },
    { x: 10, y: 0 },
    { x: -5, y: 0 },
    { x: 0, y: 30 }
  ],
  closed: true,
  stroke: 3,
  color: '#FFD700',
  fill: true
});

function animateLightning() {
  lightning.rotate.z = Math.sin(Date.now() * 0.002) * 0.2;
  lightning.updateRenderGraph();
  requestAnimationFrame(animateLightning);
}
animateLightning();

// Similar patterns for other icons...
```

---

## 6. E-Commerce

### Example 6.1: Product Detail Page with 360° View

**Use Case**: Product page with interactive 3D model

```html
<div class="product-detail">
  <div class="product-view">
    <canvas class="product-3d" width="600" height="600"></canvas>
    <div class="view-controls">
      <button id="rotate-left">←</button>
      <button id="rotate-right">→</button>
      <button id="zoom-in">+</button>
      <button id="zoom-out">−</button>
    </div>
  </div>

  <div class="product-info tilt-card" data-tilt>
    <h1>Product Name</h1>
    <p class="price">$299.99</p>
    <button class="buy-now">Buy Now</button>
  </div>
</div>
```

```javascript
// Zdog 3D product model
const productIllo = new Zdog.Illustration({
  element: '.product-3d',
  zoom: 3,
  dragRotate: true
});

// Example: Watch model
const watch = new Zdog.Anchor({
  addTo: productIllo
});

// Watch body
new Zdog.Cylinder({
  addTo: watch,
  diameter: 30,
  length: 10,
  stroke: 2,
  color: '#333',
  fill: true
});

// Watch face
new Zdog.Ellipse({
  addTo: watch,
  diameter: 28,
  translate: { z: 6 },
  stroke: 1,
  color: '#fff',
  fill: true
});

// Watch hands
new Zdog.Shape({
  addTo: watch,
  path: [{ y: 0 }, { y: -10 }],
  translate: { z: 7 },
  stroke: 2,
  color: '#333'
});

let rotationSpeed = 0;

function animate() {
  watch.rotate.y += rotationSpeed;
  productIllo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();

// Control buttons
document.getElementById('rotate-left').addEventListener('click', () => {
  rotationSpeed = -0.05;
  setTimeout(() => rotationSpeed = 0, 500);
});

document.getElementById('rotate-right').addEventListener('click', () => {
  rotationSpeed = 0.05;
  setTimeout(() => rotationSpeed = 0, 500);
});

let currentZoom = 3;
document.getElementById('zoom-in').addEventListener('click', () => {
  currentZoom += 0.5;
  productIllo.zoom = currentZoom;
});

document.getElementById('zoom-out').addEventListener('click', () => {
  currentZoom = Math.max(1, currentZoom - 0.5);
  productIllo.zoom = currentZoom;
});

// Tilt info card
VanillaTilt.init(document.querySelector('.product-info'), {
  max: 8,
  glare: true,
  "max-glare": 0.2
});
```

---

## 7. SaaS Landing Pages

### Example 7.1: Feature Comparison Table

**Use Case**: SaaS pricing page with interactive comparison

```html
<section class="comparison-section">
  <div id="vanta-bg"></div>

  <table class="comparison-table">
    <thead>
      <tr>
        <th>Features</th>
        <th class="plan-column tilt-column" data-tilt>
          <canvas class="plan-icon" width="60" height="60"></canvas>
          <span>Starter</span>
        </th>
        <th class="plan-column tilt-column" data-tilt>
          <canvas class="plan-icon" width="60" height="60"></canvas>
          <span>Pro</span>
        </th>
        <th class="plan-column tilt-column" data-tilt>
          <canvas class="plan-icon" width="60" height="60"></canvas>
          <span>Enterprise</span>
        </th>
      </tr>
    </thead>
    <tbody>
      <!-- Feature rows -->
    </tbody>
  </table>
</section>
```

```javascript
// Subtle background
VANTA.RINGS({
  el: "#vanta-bg",
  backgroundColor: 0xf8f9fa,
  color: 0x667eea
});

// Tilt plan columns
VanillaTilt.init(document.querySelectorAll('.plan-column'), {
  max: 5,
  glare: true,
  "max-glare": 0.1,
  scale: 1.02,
  axis: 'y'  // Only tilt vertically
});

// Zdog icons for each plan
const plans = document.querySelectorAll('.plan-icon');

// Starter: Single star
const starter = new Zdog.Illustration({
  element: plans[0],
  zoom: 1.5
});

new Zdog.Polygon({
  addTo: starter,
  sides: 5,
  radius: 15,
  stroke: 2,
  color: '#4CAF50',
  fill: true
});

// Pro: Two stars
const pro = new Zdog.Illustration({
  element: plans[1],
  zoom: 1.5
});

[-8, 8].forEach(x => {
  new Zdog.Polygon({
    addTo: pro,
    sides: 5,
    radius: 12,
    translate: { x },
    stroke: 2,
    color: '#2196F3',
    fill: true
  });
});

// Enterprise: Three stars
const enterprise = new Zdog.Illustration({
  element: plans[2],
  zoom: 1.5
});

[-12, 0, 12].forEach(x => {
  new Zdog.Polygon({
    addTo: enterprise,
    sides: 5,
    radius: 10,
    translate: { x },
    stroke: 2,
    color: '#9C27B0',
    fill: true
  });
});

// Animate all
function animate() {
  starter.rotate.z += 0.02;
  pro.rotate.z += 0.02;
  enterprise.rotate.z += 0.02;

  starter.updateRenderGraph();
  pro.updateRenderGraph();
  enterprise.updateRenderGraph();

  requestAnimationFrame(animate);
}
animate();
```

---

## 8. Performance Patterns

### Example 8.1: Lazy Loading Vanta Backgrounds

**Use Case**: Improve initial page load by deferring Vanta initialization

```javascript
// Lazy load Vanta when section is visible
const vantaSections = document.querySelectorAll('[data-vanta]');

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const section = entry.target;
      const effect = section.dataset.vanta;

      // Load effect
      if (effect === 'waves') {
        VANTA.WAVES({
          el: section,
          color: 0x23153c,
          waveHeight: 15
        });
      }

      // Stop observing
      observer.unobserve(section);
    }
  });
}, { threshold: 0.1 });

vantaSections.forEach(section => observer.observe(section));
```

---

### Example 8.2: Conditional Effect Loading Based on Device

```javascript
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
const isLowEnd = navigator.hardwareConcurrency <= 4;

if (!isMobile && !isLowEnd) {
  // Full effects
  VANTA.WAVES({
    el: "#vanta-bg",
    color: 0x23153c,
    waveHeight: 20,
    waveSpeed: 1.0
  });

  VanillaTilt.init(document.querySelectorAll(".tilt-card"), {
    max: 25,
    glare: true,
    "max-glare": 0.5
  });
} else if (isMobile && !isLowEnd) {
  // Mobile-optimized
  VANTA.DOTS({  // Lighter effect
    el: "#vanta-bg",
    size: 2,
    spacing: 40
  });

  // No tilt on mobile, use gyro instead
  VanillaTilt.init(document.querySelectorAll(".tilt-card"), {
    max: 10,
    gyroscope: true,
    glare: false
  });
} else {
  // Low-end devices: static gradient
  document.getElementById('vanta-bg').style.background =
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';

  // No tilt effects
}
```

---

### Example 8.3: Request Idle Callback for Zdog Animations

```javascript
// Use requestIdleCallback for non-critical animations
let zdogQueue = [];

function animateZdog() {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      zdogQueue.forEach(illo => illo.updateRenderGraph());
      requestAnimationFrame(animateZdog);
    });
  } else {
    // Fallback
    zdogQueue.forEach(illo => illo.updateRenderGraph());
    requestAnimationFrame(animateZdog);
  }
}

// Add illustrations to queue
zdogQueue.push(illo1, illo2, illo3);
animateZdog();
```

---

### Example 8.4: Debounced Resize Handling

```javascript
let resizeTimer;
let vantaEffect;

function initVanta() {
  vantaEffect = VANTA.WAVES({ el: "#vanta-bg" });
}

window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);

  resizeTimer = setTimeout(() => {
    // Destroy and recreate on significant resize
    if (vantaEffect) {
      vantaEffect.destroy();
    }

    initVanta();
  }, 500);
});

initVanta();
```

---

## Complete Integration Example

### Full-Stack Landing Page

Combining all three libraries for a production landing page:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Production Landing Page</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <!-- Hero with Vanta -->
  <section class="hero" id="hero">
    <div id="vanta-bg"></div>
    <div class="hero-content">
      <canvas class="logo-zdog" width="200" height="200"></canvas>
      <h1>Your Amazing Product</h1>
      <p>The tagline that converts</p>
      <button class="cta-btn tilt-btn" data-tilt>Get Started Free</button>
    </div>
  </section>

  <!-- Features with Tilt Cards -->
  <section class="features">
    <h2>Features</h2>
    <div class="feature-grid">
      <div class="feature-card tilt-card" data-tilt>
        <canvas class="feature-icon" width="100" height="100"></canvas>
        <h3>Fast</h3>
        <p>Lightning-fast performance</p>
      </div>

      <div class="feature-card tilt-card" data-tilt>
        <canvas class="feature-icon" width="100" height="100"></canvas>
        <h3>Secure</h3>
        <p>Bank-level security</p>
      </div>

      <div class="feature-card tilt-card" data-tilt>
        <canvas class="feature-icon" width="100" height="100"></canvas>
        <h3>Scalable</h3>
        <p>Grows with you</p>
      </div>
    </div>
  </section>

  <!-- Pricing with Zdog + Tilt -->
  <section class="pricing" data-vanta="topology">
    <h2>Pricing</h2>
    <div class="pricing-grid">
      <!-- Pricing cards here -->
    </div>
  </section>

  <!-- Scripts -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.waves.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.topology.min.js"></script>
  <script src="https://unpkg.com/zdog@1/dist/zdog.dist.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.1/vanilla-tilt.min.js"></script>
  <script src="app.js"></script>
</body>
</html>
```

```javascript
// app.js

// Performance check
const performanceLevel = (() => {
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  const cores = navigator.hardwareConcurrency || 2;

  if (isMobile && cores <= 4) return 'low';
  if (isMobile || cores <= 4) return 'medium';
  return 'high';
})();

console.log('Performance level:', performanceLevel);

// Conditional initialization
if (performanceLevel === 'high') {
  // Full effects
  initFullEffects();
} else if (performanceLevel === 'medium') {
  initMediumEffects();
} else {
  initLowEffects();
}

function initFullEffects() {
  // Hero Vanta
  VANTA.WAVES({
    el: "#vanta-bg",
    color: 0x23153c,
    waveHeight: 20,
    waveSpeed: 1.0
  });

  // Pricing Vanta (lazy load)
  const pricingObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        VANTA.TOPOLOGY({
          el: entry.target,
          color: 0x667eea
        });
        pricingObserver.unobserve(entry.target);
      }
    });
  });
  pricingObserver.observe(document.querySelector('[data-vanta="topology"]'));

  // Zdog icons
  initZdogIcons();

  // Vanilla Tilt
  VanillaTilt.init(document.querySelectorAll(".tilt-card"), {
    max: 15,
    glare: true,
    "max-glare": 0.3,
    scale: 1.05
  });

  VanillaTilt.init(document.querySelector(".cta-btn"), {
    max: 20,
    glare: true,
    "max-glare": 0.5,
    scale: 1.1
  });
}

function initMediumEffects() {
  // Simpler Vanta
  VANTA.DOTS({
    el: "#vanta-bg",
    size: 2,
    spacing: 40
  });

  // Zdog without heavy animations
  initZdogIcons();

  // Lighter tilt
  VanillaTilt.init(document.querySelectorAll(".tilt-card"), {
    max: 10,
    glare: false,
    scale: 1.02
  });
}

function initLowEffects() {
  // Static gradient
  document.getElementById('vanta-bg').style.background =
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';

  // Static Zdog icons
  initZdogIcons(false);  // No animation

  // No tilt effects
}

function initZdogIcons(animate = true) {
  // Logo
  const logoIllo = new Zdog.Illustration({
    element: '.logo-zdog',
    zoom: 3
  });

  const logo = new Zdog.Box({
    addTo: logoIllo,
    width: 30,
    height: 30,
    depth: 30,
    stroke: 2,
    color: '#fff',
    fill: true
  });

  if (animate) {
    function animateLogo() {
      logo.rotate.y += 0.02;
      logoIllo.updateRenderGraph();
      requestAnimationFrame(animateLogo);
    }
    animateLogo();
  } else {
    logoIllo.updateRenderGraph();
  }

  // Feature icons
  const featureIcons = document.querySelectorAll('.feature-icon');

  featureIcons.forEach((canvas, i) => {
    const illo = new Zdog.Illustration({
      element: canvas,
      zoom: 2
    });

    // Different icon for each feature
    if (i === 0) {
      // Lightning
      new Zdog.Shape({
        addTo: illo,
        path: [
          { x: 0, y: -20 },
          { x: 8, y: 0 },
          { x: -4, y: 0 },
          { x: 0, y: 20 }
        ],
        closed: true,
        stroke: 3,
        color: '#FFD700',
        fill: true
      });
    } else if (i === 1) {
      // Shield
      new Zdog.Shape({
        addTo: illo,
        path: [
          { x: 0, y: -20 },
          { x: 15, y: -10 },
          { x: 15, y: 10 },
          { x: 0, y: 20 },
          { x: -15, y: 10 },
          { x: -15, y: -10 }
        ],
        closed: true,
        stroke: 3,
        color: '#4CAF50',
        fill: true
      });
    } else {
      // Graph
      [5, 15, 10, 20].forEach((h, j) => {
        new Zdog.Rect({
          addTo: illo,
          width: 6,
          height: h,
          translate: { x: (j - 1.5) * 8, y: h / 2 - 10 },
          stroke: 2,
          color: '#2196F3',
          fill: true
        });
      });
    }

    if (animate) {
      function animateFeature() {
        illo.rotate.y += 0.01;
        illo.updateRenderGraph();
        requestAnimationFrame(animateFeature);
      }
      animateFeature();
    } else {
      illo.updateRenderGraph();
    }
  });
}

// Cleanup
window.addEventListener('beforeunload', () => {
  document.querySelectorAll('.tilt-card').forEach(card => {
    if (card.vanillaTilt) card.vanillaTilt.destroy();
  });
});
```

---

## Best Practices Summary

1. **Performance First**
   - Test on low-end devices
   - Implement conditional loading
   - Use lazy loading for off-screen effects

2. **Accessibility**
   - Provide fallbacks for disabled animations
   - Maintain sufficient color contrast
   - Ensure interactive elements are keyboard-accessible

3. **Mobile Optimization**
   - Disable heavy effects on mobile
   - Use simpler Vanta effects (DOTS, RINGS)
   - Consider using gyroscope for tilt on mobile

4. **Memory Management**
   - Always destroy effects on unmount
   - Clean up event listeners
   - Use Intersection Observer for visibility detection

5. **User Experience**
   - Keep animations subtle (max tilt: 10-15°)
   - Provide pause/play controls for accessibility
   - Test cross-browser compatibility

---

These examples demonstrate production-ready patterns for building stunning, performant web experiences with lightweight 3D effects.



===== FILE: plugins/individual/lightweight-3d-effects/skills/lightweight-3d-effects/assets/starter_lightweight/README.md =====

# Lightweight 3D Effects - Starter Template

Production-ready template combining **Vanta.js**, **Zdog**, and **Vanilla-Tilt** for stunning 3D effects with minimal overhead.

---

## Features

- 🌊 **Vanta.js Background** - Animated WebGL waves effect
- 🎨 **Zdog Illustrations** - Multiple pseudo-3D graphics
- 🎯 **Vanilla Tilt Cards** - Interactive 3D tilt effects with glare
- 📱 **Responsive Design** - Mobile-optimized with performance considerations
- ♿ **Accessible** - Semantic HTML and proper contrast
- 🚀 **Fast Loading** - CDN-based, optimized assets

---

## Quick Start

### 1. View Locally

Simply open `index.html` in a modern web browser. All dependencies are loaded via CDN.

```bash
# Option 1: Direct open
open index.html

# Option 2: Local server (recommended)
python -m http.server 8000
# Visit http://localhost:8000
```

### 2. Customize Colors

Edit `main.js` to change effect colors:

```javascript
// Vanta.js waves color
let vantaEffect = VANTA.WAVES({
  el: "#vanta-bg",
  color: 0x23153c,  // Change this hex number
  waveHeight: 15.00,
  waveSpeed: 0.75
});

// Zdog colors
const heroCube = new Zdog.Box({
  frontFace: '#667eea',  // Change face colors
  rearFace: '#764ba2'
});
```

### 3. Change Vanta Effect

Replace WAVES with any other Vanta effect:

```javascript
// Change from WAVES to BIRDS
<script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.birds.min.js"></script>

let vantaEffect = VANTA.BIRDS({
  el: "#vanta-bg",
  backgroundColor: 0x23153c,
  color1: 0xff0090,
  quantity: 5
});
```

Available effects: WAVES, CLOUDS, BIRDS, NET, CELLS, FOG, GLOBE, RINGS, DOTS, TOPOLOGY, TRUNK

---

## Project Structure

```
starter_lightweight/
├── index.html          # Main HTML structure
├── style.css           # Styling and responsive design
├── main.js             # All effects initialization
└── README.md           # This file
```

---

## What's Included

### Vanta.js Background

**Type**: WAVES effect
**Purpose**: Immersive animated background
**Performance**: ~15-20ms per frame on desktop

```javascript
// Located in main.js
let vantaEffect = VANTA.WAVES({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  color: 0x23153c,
  waveHeight: 15.00,
  zoom: 0.65
});
```

**Customization Options**:
- `color`: Wave color (hex number)
- `waveHeight`: Wave amplitude (0-30)
- `waveSpeed`: Animation speed (0-2)
- `shininess`: Surface reflectivity (0-100)

---

### Zdog Illustrations

**5 Different Illustrations**:

1. **Hero Cube** (`.hero-zdog`)
   - Rotating 3D cube with colored faces
   - Auto-animation on X and Y axes

2. **Card Icon 1 - Globe** (`.zdog-icon-1`)
   - Orbiting globe with particles
   - Represents Vanta.js

3. **Card Icon 2 - 3D Z** (`.zdog-icon-2`)
   - Layered "Z" letter with depth
   - Represents Zdog

4. **Card Icon 3 - Tilted Square** (`.zdog-icon-3`)
   - Stacked squares with parallax
   - Represents Vanilla-Tilt

5. **Demo Model** (`.demo-zdog`)
   - Interactive sphere with orbiting boxes
   - Drag to rotate
   - Control buttons for color/spin

**How to Add More**:

```javascript
const newIllo = new Zdog.Illustration({
  element: '.your-canvas-class',
  zoom: 2
});

new Zdog.Ellipse({
  addTo: newIllo,
  diameter: 40,
  stroke: 5,
  color: '#667eea'
});

function animate() {
  newIllo.rotate.y += 0.03;
  newIllo.updateRenderGraph();
  requestAnimationFrame(animate);
}
animate();
```

---

### Vanilla Tilt Cards

**Applied to**: `.tilt-card` elements
**Features**:
- 15° max tilt
- Glare effect at 30% opacity
- 3% scale on hover
- 1000px perspective

**Configuration** (in `main.js`):

```javascript
VanillaTilt.init(document.querySelectorAll(".tilt-card"), {
  max: 15,            // Max tilt angle
  speed: 400,         // Transition speed (ms)
  glare: true,        // Enable glare
  "max-glare": 0.3,   // Max glare opacity
  scale: 1.03,        // Scale multiplier
  perspective: 1000   // CSS perspective
});
```

**3D Transform Layers**:

```css
.card-icon {
  transform: translateZ(30px);
}
.card h2 {
  transform: translateZ(20px);
}
.card-btn {
  transform: translateZ(40px);
}
```

This creates depth when tilting.

---

## Customization Guide

### Change Hero Title

Edit `index.html`:

```html
<h1>Lightweight 3D Effects</h1>
<!-- Change to: -->
<h1>Your Custom Title</h1>
```

### Modify Card Content

Edit `index.html` card sections:

```html
<div class="card tilt-card" data-tilt>
  <canvas class="card-icon zdog-icon-1" width="120" height="120"></canvas>
  <h2>Your Title</h2>
  <p>Your description text here.</p>
  <button class="card-btn">Learn More</button>
</div>
```

### Add New Zdog Icon

1. Add canvas to HTML:
```html
<canvas class="zdog-icon-4" width="120" height="120"></canvas>
```

2. Create illustration in `main.js`:
```javascript
const icon4 = new Zdog.Illustration({
  element: '.zdog-icon-4',
  zoom: 2
});

new Zdog.Polygon({
  addTo: icon4,
  sides: 6,
  radius: 20,
  stroke: 3,
  color: '#667eea',
  fill: true
});

function animateIcon4() {
  icon4.rotate.z += 0.02;
  icon4.updateRenderGraph();
  requestAnimationFrame(animateIcon4);
}
animateIcon4();
```

### Change Tilt Settings per Card

Instead of global init, initialize individually:

```javascript
VanillaTilt.init(document.querySelector(".card-1"), {
  max: 25,
  glare: true
});

VanillaTilt.init(document.querySelector(".card-2"), {
  max: 10,
  glare: false
});
```

---

## Performance Optimization

### Mobile Optimization

**Automatic optimizations included**:

1. **Tilt disabled on mobile** (< 768px width)
```javascript
if (window.innerWidth < 768) {
  document.querySelectorAll('.tilt-card').forEach(card => {
    if (card.vanillaTilt) {
      card.vanillaTilt.destroy();
    }
  });
}
```

2. **Vanta mobile scale**
```javascript
scaleMobile: 1.00  // Adjust to 0.5 for better performance
```

3. **Responsive CSS**
```css
@media (max-width: 768px) {
  .hero h1 {
    font-size: 2.5rem;
  }
}
```

### Further Optimizations

**1. Reduce Vanta complexity**

```javascript
VANTA.WAVES({
  el: "#vanta-bg",
  points: 5,           // Lower = faster (default: 10)
  maxDistance: 15,     // Lower = faster (default: 20)
  waveHeight: 10       // Lower = faster (default: 15)
});
```

**2. Limit Zdog animations**

```javascript
// Only animate when visible
let isVisible = true;

let observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    isVisible = entry.isIntersecting;
  });
});

observer.observe(document.querySelector('.hero-zdog'));

function animate() {
  if (isVisible) {
    heroCube.rotate.x += 0.01;
    heroIllo.updateRenderGraph();
  }
  requestAnimationFrame(animate);
}
```

**3. Pause Vanta when not visible**

```javascript
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    if (vantaEffect) vantaEffect.destroy();
  } else {
    vantaEffect = VANTA.WAVES({ el: "#vanta-bg" });
  }
});
```

---

## Browser Support

| Browser | Vanta.js | Zdog | Vanilla-Tilt |
|---------|----------|------|--------------|
| Chrome  | ✅       | ✅   | ✅           |
| Firefox | ✅       | ✅   | ✅           |
| Safari  | ✅       | ✅   | ✅           |
| Edge    | ✅       | ✅   | ✅           |
| IE11    | ❌       | ✅   | ✅           |

**Notes**:
- Vanta.js requires WebGL support
- All effects gracefully degrade if unavailable
- Mobile gyroscope requires HTTPS

---

## Common Issues

### Vanta Not Loading

**Problem**: Background stays gradient, no animation

**Solutions**:
1. Check browser console for errors
2. Ensure Three.js loads before Vanta
3. Verify WebGL is enabled:
   ```javascript
   const canvas = document.createElement('canvas');
   const gl = canvas.getContext('webgl');
   console.log('WebGL:', gl ? 'Enabled' : 'Disabled');
   ```

### Tilt Not Working

**Problem**: Cards don't tilt on hover

**Solutions**:
1. Ensure `data-tilt` attribute exists
2. Check if Vanilla-Tilt script loaded
3. Verify card has dimensions:
   ```css
   .card {
     width: 300px;
     height: 400px;
   }
   ```

### Zdog Canvas Blank

**Problem**: Canvas shows nothing

**Solutions**:
1. Verify canvas dimensions are set
2. Check if illustration is updating:
   ```javascript
   console.log('Illustration:', illo);
   illo.updateRenderGraph();  // Force render
   ```
3. Ensure shapes have `stroke` or `fill`

---

## Deployment

### CDN Dependencies

All dependencies load from CDN (no build step required):

- Three.js: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js`
- Vanta.js: `https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.waves.min.js`
- Zdog: `https://unpkg.com/zdog@1/dist/zdog.dist.min.js`
- Vanilla-Tilt: `https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.1/vanilla-tilt.min.js`

### Hosting

**Static Hosting** (recommended):
- Netlify: Drag & drop folder
- Vercel: `vercel deploy`
- GitHub Pages: Push to `gh-pages` branch
- Cloudflare Pages: Connect repository

**Example Netlify Deploy**:
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=.
```

### Build for Production (Optional)

For bundling with your app:

```bash
npm install three vanta zdog vanilla-tilt
```

```javascript
import * as THREE from 'three';
import WAVES from 'vanta/dist/vanta.waves.min.js';
import Zdog from 'zdog';
import VanillaTilt from 'vanilla-tilt';

// Use as before
```

---

## Advanced Examples

### Dynamic Effect Switching

```javascript
let effects = ['WAVES', 'BIRDS', 'NET'];
let currentEffect = 0;

document.getElementById('switchEffect').addEventListener('click', () => {
  vantaEffect.destroy();

  currentEffect = (currentEffect + 1) % effects.length;
  const effect = effects[currentEffect];

  if (effect === 'WAVES') {
    vantaEffect = VANTA.WAVES({ el: "#vanta-bg" });
  } else if (effect === 'BIRDS') {
    vantaEffect = VANTA.BIRDS({ el: "#vanta-bg" });
  } else {
    vantaEffect = VANTA.NET({ el: "#vanta-bg" });
  }
});
```

### Synchronized Animations

```javascript
let masterTime = 0;

function animateAll() {
  masterTime += 0.02;

  // Sync hero cube
  heroCube.rotate.y = Math.sin(masterTime) * Math.PI;

  // Sync demo model
  demoModel.rotate.y = masterTime;

  // Update all
  heroIllo.updateRenderGraph();
  demoIllo.updateRenderGraph();

  requestAnimationFrame(animateAll);
}
animateAll();
```

### Scroll-Based Effects

```javascript
window.addEventListener('scroll', () => {
  const scrollPercent = window.scrollY / (document.body.scrollHeight - window.innerHeight);

  // Rotate demo model based on scroll
  demoModel.rotate.y = scrollPercent * Math.PI * 2;
  demoIllo.updateRenderGraph();

  // Change Vanta color
  const hue = Math.floor(scrollPercent * 360);
  const color = parseInt(`0x${hue.toString(16).padStart(6, '0')}`);
  vantaEffect.setOptions({ color });
});
```

---

## Resources

### Documentation
- **Vanta.js**: https://www.vantajs.com
- **Zdog**: https://zzz.dog
- **Vanilla-Tilt**: https://github.com/micku7zu/vanilla-tilt.js

### Inspiration
- **Vanta Gallery**: https://www.vantajs.com/?effect=waves
- **Zdog Examples**: https://codepen.io/desandro/
- **Tilt Patterns**: https://micku7zu.github.io/vanilla-tilt.js/

---

## License

This template is MIT licensed - free for personal and commercial use.

**Dependencies**:
- Three.js: MIT
- Vanta.js: MIT
- Zdog: MIT
- Vanilla-Tilt: MIT

---

## Support

For issues or questions:
1. Check browser console for errors
2. Review the [Common Issues](#common-issues) section
3. Consult official library documentation
4. Test in a different browser

---

**Built with ❤️ using lightweight 3D effects libraries**



===== FILE: plugins/individual/lightweight-3d-effects/skills/lightweight-3d-effects/assets/starter_lightweight/index.html =====

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lightweight 3D Effects - Starter Template</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- Vanta.js Background -->
  <div id="vanta-bg"></div>

  <!-- Main Content -->
  <div class="container">
    <!-- Hero Section -->
    <section class="hero">
      <canvas class="hero-zdog" width="200" height="200"></canvas>
      <h1>Lightweight 3D Effects</h1>
      <p class="subtitle">Combining Vanta.js, Zdog, and Vanilla-Tilt</p>
    </section>

    <!-- Feature Cards -->
    <section class="cards">
      <div class="card tilt-card" data-tilt>
        <canvas class="card-icon zdog-icon-1" width="120" height="120"></canvas>
        <h2>Vanta.js</h2>
        <p>Animated WebGL backgrounds powered by Three.js for immersive visual experiences.</p>
        <button class="card-btn">Learn More</button>
      </div>

      <div class="card tilt-card" data-tilt>
        <canvas class="card-icon zdog-icon-2" width="120" height="120"></canvas>
        <h2>Zdog</h2>
        <p>Pseudo-3D engine for canvas and SVG. Create flat designs with dimensional depth.</p>
        <button class="card-btn">Learn More</button>
      </div>

      <div class="card tilt-card" data-tilt>
        <canvas class="card-icon zdog-icon-3" width="120" height="120"></canvas>
        <h2>Vanilla-Tilt</h2>
        <p>Smooth 3D tilt effect for any DOM element. Perfect for interactive cards.</p>
        <button class="card-btn">Learn More</button>
      </div>
    </section>

    <!-- Interactive Demo -->
    <section class="demo-section">
      <div class="demo-card tilt-card" data-tilt>
        <canvas class="demo-zdog" width="300" height="300"></canvas>
        <div class="demo-controls">
          <h3>Interactive Demo</h3>
          <p>Hover and drag to interact</p>
          <div class="control-buttons">
            <button id="toggleSpin">Pause</button>
            <button id="changeColor">Change Color</button>
            <button id="resetView">Reset</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer>
      <p>Built with ❤️ using Vanta.js, Zdog, and Vanilla-Tilt</p>
      <div class="footer-links">
        <a href="https://www.vantajs.com" target="_blank">Vanta.js</a>
        <a href="https://zzz.dog" target="_blank">Zdog</a>
        <a href="https://github.com/micku7zu/vanilla-tilt.js" target="_blank">Vanilla-Tilt</a>
      </div>
    </footer>
  </div>

  <!-- Scripts -->
  <!-- Three.js (required for Vanta) -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>

  <!-- Vanta.js WAVES effect -->
  <script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.waves.min.js"></script>

  <!-- Zdog -->
  <script src="https://unpkg.com/zdog@1/dist/zdog.dist.min.js"></script>

  <!-- Vanilla Tilt -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/vanilla-tilt/1.8.1/vanilla-tilt.min.js"></script>

  <!-- Main JavaScript -->
  <script src="main.js"></script>
</body>
</html>

```


===== FILE: plugins/individual/lightweight-3d-effects/skills/lightweight-3d-effects/assets/starter_lightweight/main.js =====

```js
// Lightweight 3D Effects - Starter Template
// Combining Vanta.js, Zdog, and Vanilla-Tilt

console.log('Lightweight 3D Effects initialized');

// ============================================================================
// VANTA.JS BACKGROUND
// ============================================================================

let vantaEffect = VANTA.WAVES({
  el: "#vanta-bg",
  mouseControls: true,
  touchControls: true,
  gyroControls: false,
  minHeight: 200.00,
  minWidth: 200.00,
  scale: 1.00,
  scaleMobile: 1.00,
  color: 0x23153c,
  shininess: 30.00,
  waveHeight: 15.00,
  waveSpeed: 0.75,
  zoom: 0.65
});

console.log('Vanta.js background initialized');

// ============================================================================
// ZDOG ILLUSTRATIONS
// ============================================================================

// Hero Zdog Icon (Rotating Cube)
const heroIllo = new Zdog.Illustration({
  element: '.hero-zdog',
  zoom: 2,
  dragRotate: false
});

const heroCube = new Zdog.Box({
  addTo: heroIllo,
  width: 40,
  height: 40,
  depth: 40,
  stroke: 2,
  color: '#fff',
  fill: true,
  frontFace: '#667eea',
  rearFace: '#764ba2',
  leftFace: '#5568d3',
  rightFace: '#8568df',
  topFace: '#98d5e8',
  bottomFace: '#f093fb'
});

// Animate hero cube
function animateHeroCube() {
  heroCube.rotate.x += 0.01;
  heroCube.rotate.y += 0.02;
  heroIllo.updateRenderGraph();
  requestAnimationFrame(animateHeroCube);
}
animateHeroCube();

// ============================================================================
// Card Icon 1 - Vanta (Globe)
const icon1 = new Zdog.Illustration({
  element: '.zdog-icon-1',
  zoom: 2,
  dragRotate: false
});

// Globe with particles
const globe1 = new Zdog.Anchor({
  addTo: icon1
});

new Zdog.Ellipse({
  addTo: globe1,
  diameter: 40,
  stroke: 2,
  color: '#667eea',
});

new Zdog.Ellipse({
  addTo: globe1,
  diameter: 40,
  rotate: { y: Math.PI/2 },
  stroke: 2,
  color: '#764ba2',
});

// Particles around globe
for (let i = 0; i < 8; i++) {
  const angle = (i / 8) * Math.PI * 2;
  new Zdog.Ellipse({
    addTo: globe1,
    diameter: 4,
    translate: {
      x: Math.cos(angle) * 30,
      y: Math.sin(angle) * 30
    },
    stroke: 2,
    color: '#fff',
    fill: true
  });
}

function animateIcon1() {
  globe1.rotate.y += 0.03;
  icon1.updateRenderGraph();
  requestAnimationFrame(animateIcon1);
}
animateIcon1();

// ============================================================================
// Card Icon 2 - Zdog (3D Z)
const icon2 = new Zdog.Illustration({
  element: '.zdog-icon-2',
  zoom: 3,
  dragRotate: false
});

const zShape = new Zdog.Anchor({
  addTo: icon2
});

// Draw "Z" with 3D depth
new Zdog.Shape({
  addTo: zShape,
  path: [
    { x: -15, y: -15 },
    { x: 15, y: -15 },
    { x: -15, y: 15 },
    { x: 15, y: 15 }
  ],
  stroke: 8,
  color: '#667eea'
});

// Add depth layers
for (let i = 0; i < 5; i++) {
  new Zdog.Shape({
    addTo: zShape,
    path: [
      { x: -15, y: -15, z: -i*2 },
      { x: 15, y: -15, z: -i*2 },
      { x: -15, y: 15, z: -i*2 },
      { x: 15, y: 15, z: -i*2 }
    ],
    stroke: 8,
    color: `hsl(${240 + i*10}, 70%, ${60 - i*5}%)`
  });
}

function animateIcon2() {
  zShape.rotate.y += 0.02;
  zShape.rotate.x += 0.01;
  icon2.updateRenderGraph();
  requestAnimationFrame(animateIcon2);
}
animateIcon2();

// ============================================================================
// Card Icon 3 - Vanilla Tilt (Tilted Square)
const icon3 = new Zdog.Illustration({
  element: '.zdog-icon-3',
  zoom: 2,
  dragRotate: false
});

const tiltSquare = new Zdog.Anchor({
  addTo: icon3,
  rotate: { x: Math.PI/6, y: Math.PI/6 }
});

// Layered squares
for (let i = 0; i < 3; i++) {
  new Zdog.Rect({
    addTo: tiltSquare,
    width: 35 - i*5,
    height: 35 - i*5,
    translate: { z: i*10 },
    stroke: 3,
    color: `hsl(${240 + i*30}, 70%, 60%)`,
    fill: true
  });
}

// Subtle rotation
function animateIcon3() {
  tiltSquare.rotate.y += 0.01;
  icon3.updateRenderGraph();
  requestAnimationFrame(animateIcon3);
}
animateIcon3();

// ============================================================================
// Demo Zdog (Interactive)
const demoIllo = new Zdog.Illustration({
  element: '.demo-zdog',
  zoom: 2,
  dragRotate: true,
  onDragStart: function() {
    isSpinning = false;
  }
});

let isSpinning = true;
let currentColor = '#667eea';

// Create complex 3D model
const demoModel = new Zdog.Anchor({
  addTo: demoIllo
});

// Center sphere
const centerSphere = new Zdog.Hemisphere({
  addTo: demoModel,
  diameter: 40,
  stroke: 5,
  color: currentColor,
  fill: true
});

// Orbiting elements
const orbitRadius = 60;
const orbitCount = 6;
const orbitingShapes = [];

for (let i = 0; i < orbitCount; i++) {
  const angle = (i / orbitCount) * Math.PI * 2;

  const orbitAnchor = new Zdog.Anchor({
    addTo: demoModel,
    rotate: { y: angle }
  });

  const shape = new Zdog.Box({
    addTo: orbitAnchor,
    width: 15,
    height: 15,
    depth: 15,
    translate: { z: orbitRadius },
    stroke: 2,
    color: `hsl(${(i / orbitCount) * 360}, 70%, 60%)`,
    fill: true
  });

  orbitingShapes.push({ anchor: orbitAnchor, shape: shape, angle: angle });
}

// Animation
let time = 0;
function animateDemo() {
  time += 0.02;

  if (isSpinning) {
    demoModel.rotate.y += 0.02;
  }

  // Animate orbiting shapes
  orbitingShapes.forEach((item, i) => {
    const wave = Math.sin(time + item.angle) * 10;
    item.shape.translate.z = orbitRadius + wave;
    item.shape.rotate.x += 0.03;
    item.shape.rotate.y += 0.02;
  });

  demoIllo.updateRenderGraph();
  requestAnimationFrame(animateDemo);
}
animateDemo();

// ============================================================================
// VANILLA TILT
// ============================================================================

VanillaTilt.init(document.querySelectorAll(".tilt-card"), {
  max: 15,
  speed: 400,
  glare: true,
  "max-glare": 0.3,
  scale: 1.03,
  perspective: 1000
});

console.log('Vanilla Tilt initialized');

// ============================================================================
// DEMO CONTROLS
// ============================================================================

document.getElementById('toggleSpin').addEventListener('click', function() {
  isSpinning = !isSpinning;
  this.textContent = isSpinning ? 'Pause' : 'Play';
});

document.getElementById('changeColor').addEventListener('click', function() {
  // Generate random color
  const hue = Math.floor(Math.random() * 360);
  currentColor = `hsl(${hue}, 70%, 60%)`;
  centerSphere.color = currentColor;

  // Randomize orbiting shapes
  orbitingShapes.forEach(item => {
    const randomHue = Math.floor(Math.random() * 360);
    item.shape.color = `hsl(${randomHue}, 70%, 60%)`;
  });
});

document.getElementById('resetView').addEventListener('click', function() {
  demoModel.rotate.x = 0;
  demoModel.rotate.y = 0;
  demoModel.rotate.z = 0;
  isSpinning = true;
  document.getElementById('toggleSpin').textContent = 'Pause';
});

// ============================================================================
// CARD BUTTON INTERACTIONS
// ============================================================================

document.querySelectorAll('.card-btn').forEach(btn => {
  btn.addEventListener('click', function(e) {
    e.stopPropagation(); // Prevent tilt effect from interfering

    const card = this.closest('.card');
    const cardTitle = card.querySelector('h2').textContent;

    console.log(`Button clicked: ${cardTitle}`);

    // Add visual feedback
    this.style.transform = 'translateZ(40px) scale(0.95)';
    setTimeout(() => {
      this.style.transform = 'translateZ(40px) scale(1)';
    }, 100);

    // You can add navigation or modal logic here
    alert(`Learn more about ${cardTitle}!`);
  });
});

// ============================================================================
// RESPONSIVE HANDLING
// ============================================================================

// Disable tilt on mobile for better performance
if (window.innerWidth < 768) {
  document.querySelectorAll('.tilt-card').forEach(card => {
    if (card.vanillaTilt) {
      card.vanillaTilt.destroy();
    }
  });
  console.log('Tilt disabled on mobile');
}

// Resize handler for Vanta
let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    if (vantaEffect && vantaEffect.resize) {
      vantaEffect.resize();
    }
  }, 250);
});

// ============================================================================
// CLEANUP ON PAGE UNLOAD
// ============================================================================

window.addEventListener('beforeunload', () => {
  if (vantaEffect && vantaEffect.destroy) {
    vantaEffect.destroy();
  }

  document.querySelectorAll('.tilt-card').forEach(card => {
    if (card.vanillaTilt) {
      card.vanillaTilt.destroy();
    }
  });

  console.log('Effects cleaned up');
});

// ============================================================================
// PERFORMANCE MONITORING
// ============================================================================

if (typeof performance !== 'undefined' && performance.now) {
  const startTime = performance.now();

  window.addEventListener('load', () => {
    const loadTime = performance.now() - startTime;
    console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
  });
}

console.log('All effects initialized successfully');

```


===== FILE: plugins/individual/lightweight-3d-effects/skills/lightweight-3d-effects/assets/starter_lightweight/style.css =====

```css
/* Reset and Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  overflow-x: hidden;
  color: white;
}

/* Vanta Background */
#vanta-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  z-index: -1;
}

/* Container */
.container {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

/* Hero Section */
.hero {
  text-align: center;
  padding: 4rem 2rem;
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.hero-zdog {
  display: block;
  margin: 0 auto 2rem;
  filter: drop-shadow(0 10px 30px rgba(0,0,0,0.3));
}

.hero h1 {
  font-size: 4rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 0 4px 20px rgba(0,0,0,0.3);
  background: linear-gradient(135deg, #fff 0%, #e0e0ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 1.5rem;
  opacity: 0.9;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
  margin-bottom: 2rem;
}

/* Feature Cards */
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin: 4rem 0;
  padding: 0 1rem;
}

.card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  transition: all 0.3s ease;
  transform-style: preserve-3d;
  text-align: center;
}

.card:hover {
  box-shadow: 0 30px 80px rgba(0,0,0,0.4);
}

.card-icon {
  display: block;
  margin: 0 auto 1.5rem;
  transform: translateZ(30px);
}

.card h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
  transform: translateZ(20px);
}

.card p {
  font-size: 1.1rem;
  line-height: 1.6;
  opacity: 0.9;
  margin-bottom: 1.5rem;
  transform: translateZ(15px);
}

.card-btn {
  padding: 0.75rem 2rem;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
  transform: translateZ(40px);
}

.card-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateZ(40px) translateY(-2px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

/* Demo Section */
.demo-section {
  margin: 6rem 0;
  display: flex;
  justify-content: center;
}

.demo-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 30px;
  padding: 3rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 30px 80px rgba(0,0,0,0.3);
  max-width: 600px;
  width: 100%;
  transform-style: preserve-3d;
}

.demo-zdog {
  display: block;
  margin: 0 auto 2rem;
  cursor: grab;
  transform: translateZ(40px);
}

.demo-zdog:active {
  cursor: grabbing;
}

.demo-controls {
  text-align: center;
  transform: translateZ(30px);
}

.demo-controls h3 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.demo-controls p {
  opacity: 0.8;
  margin-bottom: 1.5rem;
}

.control-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.control-buttons button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}

.control-buttons button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.control-buttons button:active {
  transform: translateY(0);
}

/* Footer */
footer {
  text-align: center;
  padding: 3rem 2rem;
  margin-top: 4rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

footer p {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  opacity: 0.9;
}

.footer-links {
  display: flex;
  gap: 2rem;
  justify-content: center;
  flex-wrap: wrap;
}

.footer-links a {
  color: white;
  text-decoration: none;
  opacity: 0.8;
  transition: opacity 0.3s;
  font-size: 1rem;
}

.footer-links a:hover {
  opacity: 1;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero h1 {
    font-size: 2.5rem;
  }

  .subtitle {
    font-size: 1.2rem;
  }

  .cards {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .demo-card {
    padding: 2rem;
  }

  .demo-zdog {
    width: 250px;
    height: 250px;
  }

  .footer-links {
    flex-direction: column;
    gap: 1rem;
  }
}

/* Glare Effect (from Vanilla Tilt) */
.js-tilt-glare {
  border-radius: 20px;
}

/* Loading State */
body.loading #vanta-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

```
