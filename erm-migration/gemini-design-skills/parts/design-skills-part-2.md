# Design Skills for Gemini, part 2 of 6: Animation

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
| `gsap-scrolltrigger` | Comprehensive skill for GSAP (GreenSock Animation Platform) and ScrollTrigger plugin. Use this skill when creating web animations, scroll-driven experiences, timelines, tweens, scroll-triggered animations, pinning, scrubbing, parallax effects, or animating DOM elements, SVG, Canvas, WebGL, or Three.js. Triggers on tasks involving GSAP, ScrollTrigger, smooth animations, scroll effects, or animation sequencing. |
| `motion-framer` | Modern animation library for React and JavaScript. Create smooth, production-ready animations with motion components, variants, gestures (hover/tap/drag), layout animations, AnimatePresence exit animations, spring physics, and scroll-based effects. Use when building interactive UI components, micro-interactions, page transitions, or complex animation sequences. |
| `react-spring-physics` | Physics-based animation library combining React Spring (spring dynamics, gesture integration, 60fps animations) and Popmotion (low-level composable animation utilities, reactive streams). Use when building fluid, natural-feeling UI animations, gesture-driven interfaces, physics simulations, or spring-loaded interactions. Triggers on tasks involving React Spring hooks, spring physics, inertia scrolling, physics-based motion, animation composition, or natural UI movements. Alternative physics approach to motion-framer for more physically accurate animations. |
| `animejs` | Versatile JavaScript animation engine for DOM, CSS, SVG, and JavaScript objects. Use when creating timeline-based animations, stagger effects, SVG morphing, keyframe sequences, or complex choreographed animations. Triggers on tasks involving Anime.js, timeline animations, staggered sequences, SVG path animations, morphing, or multi-step animation choreography. Alternative to GSAP for SVG-heavy animations and React-independent projects. |
| `lottie-animations` | After Effects animation rendering for web and React applications. Use this skill when implementing Lottie animations, JSON vector animations, interactive animated icons, micro-interactions, or loading animations. Triggers on tasks involving Lottie, lottie-web, lottie-react, dotLottie, After Effects JSON export, bodymovin, animated SVG alternatives, or designer-created animations. Complements GSAP ScrollTrigger and Framer Motion for scroll-driven and interactive animations. |


# Skill: gsap-scrolltrigger


===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/SKILL.md =====

---
name: gsap-scrolltrigger
description: Comprehensive skill for GSAP (GreenSock Animation Platform) and ScrollTrigger plugin. Use this skill when creating web animations, scroll-driven experiences, timelines, tweens, scroll-triggered animations, pinning, scrubbing, parallax effects, or animating DOM elements, SVG, Canvas, WebGL, or Three.js. Triggers on tasks involving GSAP, ScrollTrigger, smooth animations, scroll effects, or animation sequencing.
---

# GSAP & ScrollTrigger Development

## Overview

GSAP (GreenSock Animation Platform) is the industry-leading JavaScript animation library for creating high-performance, production-quality animations. ScrollTrigger is GSAP's powerful plugin for scroll-driven animations. Together, they enable everything from simple UI transitions to complex scroll-based storytelling experiences.

## Core Concepts

### The Basics: Tweens

A **tween** is a single animation from point A to point B.

```javascript
// Animate TO a state (from current)
gsap.to(".box", {
  x: 200,
  rotation: 360,
  duration: 1,
  ease: "power2.inOut"
});

// Animate FROM a state (to current)
gsap.from(".box", {
  opacity: 0,
  y: -50,
  duration: 0.8
});

// Animate FROM-TO (define both start and end)
gsap.fromTo(".box",
  { opacity: 0, scale: 0.5 }, // FROM
  { opacity: 1, scale: 1, duration: 1 } // TO
);
```

### Timelines: Sequencing Animations

**Timelines** orchestrate multiple tweens in sequence or overlap.

```javascript
const tl = gsap.timeline();

// Sequential by default
tl.to(".box1", { x: 100, duration: 1 })
  .to(".box2", { y: 100, duration: 1 })
  .to(".box3", { rotation: 360, duration: 1 });

// With labels for organization
tl.addLabel("start")
  .to(".hero", { opacity: 1, duration: 1 })
  .addLabel("reveal")
  .to(".content", { y: 0, duration: 0.8 }, "reveal") // Start at "reveal" label
  .to(".cta", { scale: 1, duration: 0.5 }, "reveal+=0.5"); // 0.5s after "reveal"
```

### Position Parameter (Timeline Timing)

Control when animations start within a timeline:

```javascript
const tl = gsap.timeline();

// Default: One after another
tl.to(".box1", { x: 100 })
  .to(".box2", { x: 100 }); // Starts after box1 finishes

// Start at the same time
tl.to(".box1", { x: 100 })
  .to(".box2", { y: 100 }, 0); // Starts at 0 seconds

// Relative positioning
tl.to(".box1", { x: 100, duration: 2 })
  .to(".box2", { y: 100 }, "-=1"); // Starts 1 second before box1 ends
  .to(".box3", { rotation: 360 }, "+=0.5"); // Starts 0.5s after box2 finishes

// At a specific time
tl.to(".box1", { x: 100 }, 2.5); // Starts at 2.5 seconds
```

## ScrollTrigger Fundamentals

### Basic Scroll Animation

```javascript
gsap.registerPlugin(ScrollTrigger);

gsap.to(".box", {
  x: 500,
  scrollTrigger: {
    trigger: ".box",
    start: "top center", // When top of trigger hits center of viewport
    end: "bottom center",
    markers: true, // Development only - shows start/end positions
    scrub: true, // Links animation to scrollbar
    toggleActions: "play none none reverse" // onEnter onLeave onEnterBack onLeaveBack
  }
});
```

### Start & End Positions

Format: `"[trigger position] [viewport position]"`

```javascript
// Common patterns
start: "top top"      // Trigger top hits viewport top
start: "top center"   // Trigger top hits viewport center (default)
start: "top bottom"   // Trigger top hits viewport bottom
start: "center center" // Trigger center hits viewport center

// With offsets
start: "top top+=100"   // 100px below viewport top
start: "top 80%"        // 80% down the viewport
end: "+=500"            // 500px after start position
end: "bottom top"       // Trigger bottom hits viewport top
```

### Scrubbing (Scroll-Synced Animation)

```javascript
// Boolean: Direct link to scrollbar (immediate)
scrub: true

// Number: Smoothing delay in seconds
scrub: 1  // Takes 1 second to "catch up" to scrollbar
scrub: 0.5 // Faster, tighter feel
```

### Toggle Actions

Control animation at four scroll points:

```javascript
toggleActions: "play pause resume reset"
// onEnter | onLeave | onEnterBack | onLeaveBack

// Actions: play, pause, resume, restart, reset, complete, reverse, none
```

Common patterns:
```javascript
toggleActions: "play none none none"       // Play once on enter
toggleActions: "play none none reverse"    // Play forward, reverse back
toggleActions: "play complete reverse reset" // Full control
toggleActions: "restart pause resume pause"  // Restart on each enter
```

## Common Patterns

### 1. Fade In On Scroll

```javascript
gsap.from(".fade-in", {
  opacity: 0,
  y: 50,
  duration: 1,
  scrollTrigger: {
    trigger: ".fade-in",
    start: "top 80%",
    end: "top 50%",
    scrub: 1,
    once: true // Only animate once
  }
});
```

### 2. Pin Element While Scrolling

```javascript
ScrollTrigger.create({
  trigger: ".panel",
  start: "top top",
  end: "+=500", // Pin for 500px of scrolling
  pin: true,
  pinSpacing: true // Add spacing (default true)
});
```

### 3. Horizontal Scroll Section

```javascript
const sections = gsap.utils.toArray(".panel");

gsap.to(sections, {
  xPercent: -100 * (sections.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".container",
    pin: true,
    scrub: 1,
    end: () => "+=" + document.querySelector(".container").offsetWidth
  }
});
```

### 4. Parallax Effect

```javascript
// Slower movement (background layer)
gsap.to(".bg", {
  y: 200,
  ease: "none",
  scrollTrigger: {
    trigger: ".section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});

// Faster movement (foreground layer)
gsap.to(".fg", {
  y: -100,
  ease: "none",
  scrollTrigger: {
    trigger: ".section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});
```

### 5. Scroll-Triggered Timeline

```javascript
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".container",
    start: "top top",
    end: "+=500",
    scrub: 1,
    pin: true,
    snap: {
      snapTo: "labels", // Snap to timeline labels
      duration: { min: 0.2, max: 3 },
      delay: 0.2,
      ease: "power1.inOut"
    }
  }
});

tl.addLabel("start")
  .from(".title", { scale: 0.3, rotation: 45, autoAlpha: 0 })
  .addLabel("color")
  .from(".box", { backgroundColor: "#28a92b" })
  .addLabel("spin")
  .to(".box", { rotation: 360 })
  .addLabel("end");
```

### 6. Batch Animations (Multiple Elements)

```javascript
// Loop through multiple elements
gsap.utils.toArray(".box").forEach((box, i) => {
  gsap.from(box, {
    y: 100,
    opacity: 0,
    scrollTrigger: {
      trigger: box,
      start: "top 80%",
      end: "top 50%",
      scrub: 1
    }
  });
});

// Or use ScrollTrigger.batch
ScrollTrigger.batch(".box", {
  onEnter: batch => gsap.to(batch, { opacity: 1, y: 0, stagger: 0.15 }),
  onLeave: batch => gsap.set(batch, { opacity: 0 }),
  start: "top 80%",
  once: true
});
```

### 7. Staggered Animations

```javascript
gsap.from(".item", {
  y: 50,
  opacity: 0,
  duration: 0.8,
  stagger: 0.1, // 0.1s between each item
  scrollTrigger: {
    trigger: ".grid",
    start: "top 80%"
  }
});

// Advanced stagger
gsap.from(".item", {
  scale: 0,
  duration: 1,
  stagger: {
    each: 0.1,
    from: "center", // "start", "center", "end", "edges", or index number
    grid: "auto", // For grid layouts
    ease: "power2.inOut"
  }
});
```

## Integration Patterns

### With Three.js / WebGL

```javascript
import * as THREE from 'three';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// Animate camera
gsap.to(camera.position, {
  x: 5,
  y: 3,
  z: 10,
  scrollTrigger: {
    trigger: "#section2",
    start: "top top",
    end: "bottom top",
    scrub: 1,
    onUpdate: () => camera.lookAt(scene.position)
  }
});

// Animate mesh rotation
gsap.to(mesh.rotation, {
  y: Math.PI * 2,
  scrollTrigger: {
    trigger: "#section3",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});

// Animate material properties
gsap.to(material, {
  opacity: 0,
  scrollTrigger: {
    trigger: "#section4",
    start: "top center",
    end: "center center",
    scrub: 1
  }
});
```

### With React (useGSAP Hook)

```javascript
import { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

function Component() {
  const container = useRef();
  const box = useRef();

  useGSAP(() => {
    gsap.to(box.current, {
      x: 200,
      scrollTrigger: {
        trigger: box.current,
        start: "top center",
        end: "bottom center",
        scrub: true,
        markers: true
      }
    });
  }, { scope: container }); // Scoping for cleanup

  return (
    <div ref={container}>
      <div ref={box} className="box">Animated Box</div>
    </div>
  );
}
```

### Sharing Timeline in React

```javascript
function App() {
  const [tl, setTl] = useState();

  useGSAP(() => {
    const timeline = gsap.timeline();
    setTl(timeline);
  }, []);

  return (
    <div>
      <Box timeline={tl} index={0} />
      <Circle timeline={tl} index={1} />
    </div>
  );
}

function Box({ timeline, index }) {
  const ref = useRef();

  useGSAP(() => {
    timeline && timeline.to(ref.current, { x: 100 }, index * 0.1);
  }, [timeline, index]);

  return <div ref={ref} className="box" />;
}
```

### Locomotive Scroll Integration

```javascript
import LocomotiveScroll from 'locomotive-scroll';

const scroller = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true
});

ScrollTrigger.scrollerProxy("[data-scroll-container]", {
  scrollTop(value) {
    return arguments.length ? scroller.scrollTo(value, 0, 0) : scroller.scroll.instance.scroll.y;
  },
  getBoundingClientRect() {
    return {top: 0, left: 0, width: window.innerWidth, height: window.innerHeight};
  },
  pinType: document.querySelector("[data-scroll-container]").style.transform ? "transform" : "fixed"
});

ScrollTrigger.addEventListener("refresh", () => scroller.update());
ScrollTrigger.refresh();
```

## Advanced Techniques

### Image Sequence Scrubbing

```javascript
const canvas = document.querySelector("canvas");
const context = canvas.getContext("2d");

const images = [];
const imageCount = 147;
const currentFrame = { value: 0 };

for (let i = 0; i < imageCount; i++) {
  const img = new Image();
  img.src = `./frames/frame_${i.toString().padStart(4, '0')}.jpg`;
  images.push(img);
}

images[0].onload = () => {
  canvas.width = images[0].width;
  canvas.height = images[0].height;
  render();
};

function render() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.drawImage(images[Math.floor(currentFrame.value)], 0, 0);
}

gsap.to(currentFrame, {
  value: imageCount - 1,
  snap: "value",
  ease: "none",
  scrollTrigger: {
    trigger: canvas,
    start: "top top",
    end: "+=500%",
    scrub: true,
    pin: true
  },
  onUpdate: render
});
```

### Smooth Scroll to Element

```javascript
gsap.registerPlugin(ScrollToPlugin);

// Scroll to element
gsap.to(window, {
  duration: 1,
  scrollTo: "#section2",
  ease: "power2.inOut"
});

// With offset
gsap.to(window, {
  duration: 1.5,
  scrollTo: { y: "#section2", offsetY: 50 },
  ease: "expo.inOut"
});

// Horizontal scroll
gsap.to(".container", {
  duration: 2,
  scrollTo: { x: 1000, autoKill: true }
});
```

### Conditional Animations (Media Queries)

```javascript
ScrollTrigger.matchMedia({
  // Desktop
  "(min-width: 800px)": function() {
    gsap.to(".box", {
      x: 500,
      scrollTrigger: {
        trigger: ".box",
        start: "top center",
        end: "bottom top",
        scrub: true
      }
    });
  },

  // Mobile
  "(max-width: 799px)": function() {
    gsap.to(".box", {
      y: 200,
      scrollTrigger: {
        trigger: ".box",
        start: "top 80%",
        scrub: 1
      }
    });
  }
});
```

## Performance Best Practices

### 1. Use `will-change` CSS

```css
.animated-element {
  will-change: transform, opacity;
}
```

### 2. Limit Repaints

```javascript
// Good: Animate transform/opacity (GPU accelerated)
gsap.to(".box", { x: 100, opacity: 0.5 });

// Avoid: Animating layout properties
// gsap.to(".box", { width: 500, height: 300 }); // Causes reflow
```

### 3. Dispose of ScrollTriggers

```javascript
// Kill individual trigger
const trigger = ScrollTrigger.create({ /* ... */ });
trigger.kill();

// Kill all triggers
ScrollTrigger.getAll().forEach(t => t.kill());

// In React with cleanup
useGSAP(() => {
  const tween = gsap.to(".box", { /* ... */ });

  return () => {
    tween.kill();
  };
}, []);
```

### 4. Debounce Resize

ScrollTrigger handles this automatically, but for custom resize logic:

```javascript
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    ScrollTrigger.refresh();
  }, 250);
});
```

### 5. Use `invalidateOnRefresh`

For dynamic values that change on resize:

```javascript
gsap.to(".box", {
  x: () => window.innerWidth / 2, // Dynamic value
  scrollTrigger: {
    trigger: ".box",
    start: "top center",
    invalidateOnRefresh: true // Recalculate x on resize
  }
});
```

## Common Pitfalls

### 1. Multiple Tweens on Same Element

```javascript
// Problem: Second tween conflicts with first
gsap.to('h1', { x: 100, scrollTrigger: { /* ... */ } });
gsap.to('h1', { x: 200, scrollTrigger: { /* ... */ } }); // Jumps!

// Solution 1: Use fromTo
gsap.fromTo('h1', { x: 100 }, { x: 200, scrollTrigger: { /* ... */ } });

// Solution 2: Use immediateRender: false
gsap.to('h1', { x: 200, immediateRender: false, scrollTrigger: { /* ... */ } });

// Solution 3: Apply ScrollTrigger to timeline
const tl = gsap.timeline({ scrollTrigger: { /* ... */ } });
tl.to('h1', { x: 100 })
  .to('h1', { x: 200 });
```

### 2. Not Using Loops for Multiple Elements

```javascript
// Wrong: Animates all at once
gsap.to('.section', {
  y: -100,
  scrollTrigger: { trigger: '.section', scrub: true }
});

// Right: Loop for individual triggers
gsap.utils.toArray('.section').forEach(section => {
  gsap.to(section, {
    y: -100,
    scrollTrigger: { trigger: section, scrub: true }
  });
});
```

### 3. Forgetting to Register Plugins

```javascript
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ScrollToPlugin } from 'gsap/ScrollToPlugin';

gsap.registerPlugin(ScrollTrigger, ScrollToPlugin); // Must register!
```

### 4. Nested ScrollTriggers in Timelines

```javascript
// Wrong: ScrollTriggers on individual tweens in timeline
const tl = gsap.timeline();
tl.to('.box1', { x: 100, scrollTrigger: { /* ... */ } }) // Don't do this!
  .to('.box2', { y: 100, scrollTrigger: { /* ... */ } });

// Right: ScrollTrigger on parent timeline
const tl = gsap.timeline({
  scrollTrigger: { /* ... */ }
});
tl.to('.box1', { x: 100 })
  .to('.box2', { y: 100 });
```

## Easing Reference

```javascript
// Power easings (most common)
ease: "power1.out"  // Subtle deceleration
ease: "power2.inOut" // Smooth acceleration/deceleration
ease: "power3.in"   // Strong acceleration
ease: "power4.out"  // Very strong deceleration

// Special easings
ease: "elastic.out"  // Bouncy overshoot
ease: "back.out"     // Slight overshoot
ease: "bounce.out"   // Bouncing effect
ease: "circ.inOut"   // Circular motion feel
ease: "expo.inOut"   // Exponential (dramatic)

// Linear (for scrubbed scroll animations)
ease: "none"
```

## ScrollTrigger Methods

```javascript
// Refresh all ScrollTriggers (after DOM changes)
ScrollTrigger.refresh();

// Get all ScrollTriggers
const triggers = ScrollTrigger.getAll();

// Get specific trigger by ID
const st = ScrollTrigger.getById("myTrigger");

// Kill trigger
st.kill();

// Update trigger
st.scroll(500); // Programmatically set scroll position
st.enable();
st.disable();

// Global ScrollTrigger config
ScrollTrigger.config({
  limitCallbacks: true, // Improve performance
  syncInterval: 15 // Throttle scroll checks (ms)
});

// Debug mode
ScrollTrigger.defaults({
  markers: true // Show markers on all triggers
});
```

## Resources

This skill includes bundled resources:

### references/
- `api_reference.md`: Quick API reference (tween methods, timeline methods, ScrollTrigger properties)
- `easing_guide.md`: Visual easing reference with use cases
- `common_patterns.md`: Copy-paste patterns for common scenarios

### scripts/
- `generate_animation.py`: Generate boilerplate GSAP code
- `timeline_builder.py`: Interactive timeline sequence builder

### assets/
- `starter_scroll/`: Complete scroll-driven site template
- `easings/`: Easing visualization HTML tool
- `examples/`: Real-world ScrollTrigger examples

## When to Use This Skill

Use this skill when:
- Creating smooth web animations
- Building scroll-driven experiences
- Implementing parallax effects
- Sequencing complex animations
- Animating DOM, SVG, Canvas, or WebGL
- Integrating animations with Three.js or React
- Building scrollytelling websites
- Creating interactive UI transitions

For Three.js-specific animations, also reference the **threejs-webgl** skill.
For React components with built-in animations, reference the **motion-framer** skill.



===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/references/api_reference.md =====

# GSAP & ScrollTrigger API Quick Reference

## Core GSAP Methods

### gsap.to()
Animate FROM current state TO specified values.

```javascript
gsap.to(target, {
  x: 100,
  y: 50,
  rotation: 360,
  duration: 1,
  ease: "power2.inOut",
  onComplete: callback
});
```

### gsap.from()
Animate TO current state FROM specified values.

```javascript
gsap.from(target, {
  opacity: 0,
  y: -50,
  duration: 0.8,
  ease: "back.out"
});
```

### gsap.fromTo()
Define both starting and ending values.

```javascript
gsap.fromTo(target,
  { opacity: 0, scale: 0.5 }, // FROM
  { opacity: 1, scale: 1, duration: 1 } // TO
);
```

### gsap.set()
Immediately set properties (no animation).

```javascript
gsap.set(target, {
  x: 100,
  opacity: 0.5
});
```

## Timeline Methods

### Creating Timelines

```javascript
const tl = gsap.timeline({
  repeat: 2,
  repeatDelay: 1,
  yoyo: true,
  paused: false,
  onComplete: callback
});
```

### Adding Animations

```javascript
// Add to end of timeline
tl.to(".box", { x: 100 });

// Add at specific time
tl.to(".box", { y: 50 }, 2); // At 2 seconds

// Add relative to previous
tl.to(".box", { rotation: 360 }, "-=0.5"); // 0.5s before previous ends
tl.to(".box", { scale: 2 }, "+=1"); // 1s after previous ends

// Add at label
tl.addLabel("midpoint")
  .to(".box", { opacity: 0 }, "midpoint")
  .to(".circle", { x: 200 }, "midpoint+=0.5");
```

### Timeline Control

```javascript
tl.play();
tl.pause();
tl.resume();
tl.reverse();
tl.restart();
tl.seek(2); // Go to 2 seconds
tl.progress(0.5); // Go to 50% through timeline
tl.timeScale(2); // 2x speed
tl.kill(); // Destroy timeline
```

## Common Tween Properties

### Animation Control

```javascript
{
  duration: 1, // seconds
  delay: 0.5, // seconds before start
  repeat: 2, // times to repeat (-1 = infinite)
  repeatDelay: 1, // seconds between repeats
  yoyo: true, // alternate direction on repeat
  ease: "power2.inOut", // easing function
  paused: true, // start paused
  immediateRender: false, // don't render immediately
  overwrite: "auto" // handle conflicting tweens
}
```

### Callbacks

```javascript
{
  onStart: () => console.log("Started"),
  onUpdate: () => console.log("Updating"),
  onComplete: () => console.log("Complete"),
  onRepeat: () => console.log("Repeating"),
  onReverseComplete: () => console.log("Reversed"),
  callbackScope: this // scope for all callbacks
}
```

## Easing Functions

### Power Easings (Most Common)

```javascript
ease: "none" // Linear
ease: "power1.in"
ease: "power1.out"
ease: "power1.inOut"
ease: "power2.in"
ease: "power2.out"
ease: "power2.inOut"
ease: "power3.in"
ease: "power3.out"
ease: "power3.inOut"
ease: "power4.in"
ease: "power4.out"
ease: "power4.inOut"
```

### Special Easings

```javascript
ease: "back.in(1.7)" // Overshoot, parameter controls amount
ease: "back.out(1.7)"
ease: "back.inOut(1.7)"

ease: "elastic.in(1, 0.3)" // Elastic bounce
ease: "elastic.out(1, 0.3)"
ease: "elastic.inOut(1, 0.3)"

ease: "bounce.in"
ease: "bounce.out"
ease: "bounce.inOut"

ease: "circ.in" // Circular
ease: "circ.out"
ease: "circ.inOut"

ease: "expo.in" // Exponential
ease: "expo.out"
ease: "expo.inOut"

ease: "sine.in" // Sinusoidal
ease: "sine.out"
ease: "sine.inOut"
```

## Stagger Configuration

### Simple Stagger

```javascript
stagger: 0.1 // 0.1s between each element
```

### Advanced Stagger

```javascript
stagger: {
  each: 0.1, // time between each
  from: "center", // "start", "center", "end", "edges", "random", or index number
  grid: "auto", // [rows, columns] for grid layouts
  ease: "power2.inOut", // easing applied to stagger timing
  repeat: 2, // repeat the stagger pattern
  yoyo: true, // alternate direction
  axis: "y" // "x" or "y" for grid stagger direction
}
```

## ScrollTrigger Properties

### Core Properties

```javascript
ScrollTrigger.create({
  // Trigger & Viewport
  trigger: ".element", // Element or selector
  start: "top center", // "[trigger position] [viewport position]"
  end: "bottom top",
  endTrigger: ".other-element", // Different end trigger

  // Scrubbing
  scrub: true, // Boolean or number (smoothing seconds)
  pin: true, // Pin trigger element
  pinSpacing: true, // Add space for pinned element
  anticipatePin: 1, // Smooth pinning

  // Actions
  toggleActions: "play pause resume reset", // onEnter onLeave onEnterBack onLeaveBack
  toggleClass: "active", // CSS class to toggle

  // Animation
  animation: tween, // GSAP animation to control

  // Snapping
  snap: {
    snapTo: "labels", // "labels", 0.1, [0, 0.5, 1], or function
    duration: { min: 0.2, max: 3 },
    delay: 0.2,
    ease: "power1.inOut"
  },

  // Callbacks
  onEnter: callback,
  onLeave: callback,
  onEnterBack: callback,
  onLeaveBack: callback,
  onUpdate: (self) => {},
  onToggle: (self) => {},
  onRefresh: (self) => {},
  onScrubComplete: (self) => {},

  // Advanced
  markers: true, // Show visual markers (debug)
  id: "myTrigger", // Unique ID
  invalidateOnRefresh: false, // Recalculate values on refresh
  once: true, // Only trigger once
  horizontal: false, // Horizontal scrolling
  scroller: ".container", // Custom scroll container
  containerAnimation: timeline, // For horizontal scrolling sections
  fastScrollEnd: true // Better performance on fast scroll
});
```

### ScrollTrigger Start/End Values

```javascript
// Format: "[trigger position] [viewport position]"

start: "top top" // Trigger top hits viewport top
start: "top center" // Trigger top hits viewport center
start: "top bottom" // Trigger top hits viewport bottom
start: "center center" // Trigger center hits viewport center
start: "bottom top" // Trigger bottom hits viewport top

// With offsets
start: "top top+=100" // 100px below viewport top
start: "top 80%" // 80% down viewport
start: "top-=50 center" // 50px above trigger top

// Dynamic
start: () => "top " + (window.innerHeight * 0.8)
end: () => "+=" + element.offsetHeight
```

## ScrollTrigger Methods

### Static Methods

```javascript
// Refresh all ScrollTriggers (after DOM changes)
ScrollTrigger.refresh();

// Get all ScrollTriggers
const triggers = ScrollTrigger.getAll();

// Get by ID
const st = ScrollTrigger.getById("myTrigger");

// Kill all
ScrollTrigger.getAll().forEach(t => t.kill());

// Global configuration
ScrollTrigger.config({
  limitCallbacks: true, // Better performance
  syncInterval: 15, // Throttle scroll checks (ms)
  ignoreMobileResize: true // Don't refresh on mobile resize
});

// Defaults for all ScrollTriggers
ScrollTrigger.defaults({
  toggleActions: "play none none reverse",
  markers: false
});

// Batch animations
ScrollTrigger.batch(".element", {
  onEnter: batch => gsap.to(batch, { opacity: 1, stagger: 0.1 }),
  start: "top 80%"
});

// Match media queries
ScrollTrigger.matchMedia({
  "(min-width: 800px)": function() {
    // Desktop animations
  },
  "(max-width: 799px)": function() {
    // Mobile animations
  }
});
```

### Instance Methods

```javascript
const st = ScrollTrigger.create({ /* ... */ });

// Control
st.enable();
st.disable();
st.kill();
st.refresh();

// Query
st.isActive; // Boolean
st.progress; // 0-1
st.direction; // 1 (down) or -1 (up)
st.getVelocity(); // Scroll velocity

// Programmatic scroll
st.scroll(500); // Set scroll position

// Get animation
const tween = st.animation; // Associated animation
const scrubTween = st.getTween(); // Scrub tween
```

## Utility Methods

### gsap.utils

```javascript
// Array helpers
gsap.utils.toArray(".class"); // Convert to array
gsap.utils.shuffle(array); // Randomize array order

// Math helpers
gsap.utils.random(min, max); // Random number
gsap.utils.snap(5); // Snap to increment (returns function)
gsap.utils.clamp(min, max, value); // Clamp value
gsap.utils.interpolate(start, end, progress); // Linear interpolation
gsap.utils.wrap(min, max); // Wrap value (returns function)
gsap.utils.normalize(min, max, value); // Normalize to 0-1
gsap.utils.mapRange(inMin, inMax, outMin, outMax, value); // Map value

// Selector helpers
gsap.utils.selector(element); // Create scoped selector function

// Distribution helpers
gsap.utils.distribute({
  base: 0,
  amount: 100,
  from: "center",
  ease: "power2.out"
});
```

## Common Patterns

```javascript
// Fade in on scroll
gsap.from(".element", {
  opacity: 0,
  y: 50,
  scrollTrigger: {
    trigger: ".element",
    start: "top 80%",
    scrub: 1
  }
});

// Pin while scrolling
ScrollTrigger.create({
  trigger: ".panel",
  pin: true,
  start: "top top",
  end: "+=500"
});

// Horizontal scroll
gsap.to(".panels", {
  xPercent: -100,
  ease: "none",
  scrollTrigger: {
    trigger: ".container",
    pin: true,
    scrub: 1,
    end: () => "+=" + document.querySelector(".panels").offsetWidth
  }
});

// Parallax
gsap.to(".bg", {
  y: 300,
  ease: "none",
  scrollTrigger: {
    trigger: ".section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});

// Batch stagger
ScrollTrigger.batch(".box", {
  onEnter: batch => gsap.to(batch, { opacity: 1, y: 0, stagger: 0.15 }),
  start: "top 80%"
});
```



===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/references/common_patterns.md =====

# GSAP & ScrollTrigger Common Patterns

A collection of copy-paste ready patterns for common web animation scenarios.

---

## Table of Contents

1. [Scroll-Triggered Animations](#scroll-triggered-animations)
2. [Pinning Patterns](#pinning-patterns)
3. [Horizontal Scrolling](#horizontal-scrolling)
4. [Parallax Effects](#parallax-effects)
5. [Stagger Animations](#stagger-animations)
6. [Timeline Sequences](#timeline-sequences)
7. [Text Animations](#text-animations)
8. [Image Reveals](#image-reveals)
9. [Navigation & UI](#navigation--ui)
10. [Page Transitions](#page-transitions)
11. [Scroll Progress Indicators](#scroll-progress-indicators)
12. [Image Sequences](#image-sequences)
13. [Responsive Patterns](#responsive-patterns)
14. [Integration Patterns](#integration-patterns)

---

## Scroll-Triggered Animations

### 1.1 Basic Fade In on Scroll

```javascript
// Fade in element when it enters viewport
gsap.from(".fade-in", {
  opacity: 0,
  y: 50,
  duration: 1,
  scrollTrigger: {
    trigger: ".fade-in",
    start: "top 80%", // When top of element hits 80% of viewport
    toggleActions: "play none none none" // Play once
  }
});
```

### 1.2 Fade In with Scrub (Scroll-Controlled)

```javascript
// Animation synced to scroll position
gsap.from(".fade-in-scrub", {
  opacity: 0,
  y: 100,
  scrollTrigger: {
    trigger: ".fade-in-scrub",
    start: "top bottom",
    end: "top center",
    scrub: true // Smooth scrubbing (boolean or number for lag)
  }
});
```

### 1.3 Batch Fade In Multiple Elements

```javascript
// Efficiently animate many elements
ScrollTrigger.batch(".batch-item", {
  onEnter: batch => gsap.from(batch, {
    opacity: 0,
    y: 60,
    stagger: 0.15,
    duration: 0.8,
    ease: "power2.out"
  }),
  start: "top 90%",
  once: true // Only trigger once
});
```

### 1.4 Fade In from Different Directions

```javascript
// Left
gsap.from(".from-left", {
  x: -100,
  opacity: 0,
  scrollTrigger: {
    trigger: ".from-left",
    start: "top 80%",
    toggleActions: "play none none reverse"
  }
});

// Right
gsap.from(".from-right", {
  x: 100,
  opacity: 0,
  scrollTrigger: { trigger: ".from-right", start: "top 80%" }
});

// Scale up
gsap.from(".scale-in", {
  scale: 0.8,
  opacity: 0,
  scrollTrigger: { trigger: ".scale-in", start: "top 80%" }
});
```

### 1.5 Toggle Classes on Scroll

```javascript
// Add/remove CSS class based on scroll position
ScrollTrigger.create({
  trigger: ".section",
  start: "top center",
  end: "bottom center",
  toggleClass: { targets: ".section", className: "active" },
  // Or specific onEnter/onLeave actions
  onEnter: () => document.querySelector(".section").classList.add("active"),
  onLeave: () => document.querySelector(".section").classList.remove("active")
});
```

---

## Pinning Patterns

### 2.1 Basic Pin (Fixed Position While Scrolling)

```javascript
// Pin element while scrolling past it
ScrollTrigger.create({
  trigger: ".pin-section",
  start: "top top",
  end: "+=500", // Pin for 500px of scrolling
  pin: true,
  markers: true // Debug markers (remove in production)
});
```

### 2.2 Pin with Content Animation

```javascript
// Pin section and animate content inside
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".pin-animation",
    start: "top top",
    end: "+=1000",
    pin: true,
    scrub: 1
  }
});

tl.from(".content h1", { opacity: 0, y: 100 })
  .from(".content p", { opacity: 0, y: 50 }, "-=0.5")
  .to(".content img", { scale: 1.2, rotation: 5 });
```

### 2.3 Pin Until Another Element

```javascript
// Pin until bottom of another section
ScrollTrigger.create({
  trigger: ".hero",
  endTrigger: ".next-section", // Different end trigger
  start: "top top",
  end: "top bottom", // When top of next-section hits viewport bottom
  pin: true,
  pinSpacing: false // Don't add extra space
});
```

### 2.4 Multiple Pinned Sections (Stacked Cards)

```javascript
// Each section pins, then next one takes over
gsap.utils.toArray(".panel").forEach((panel, i) => {
  ScrollTrigger.create({
    trigger: panel,
    start: "top top",
    pin: true,
    pinSpacing: false
  });
});
```

### 2.5 Pin with Snap Points

```javascript
// Snap to specific positions while pinned
gsap.timeline({
  scrollTrigger: {
    trigger: ".snap-section",
    start: "top top",
    end: "+=2000",
    pin: true,
    scrub: 1,
    snap: {
      snapTo: [0, 0.33, 0.66, 1], // Snap to 0%, 33%, 66%, 100%
      duration: { min: 0.2, max: 0.5 },
      ease: "power1.inOut"
    }
  }
});
```

---

## Horizontal Scrolling

### 3.1 Basic Horizontal Scroll

```javascript
// Scroll horizontally when scrolling vertically
gsap.to(".horizontal-section", {
  x: () => -(document.querySelector(".horizontal-section").scrollWidth - window.innerWidth),
  ease: "none",
  scrollTrigger: {
    trigger: ".horizontal-wrapper",
    start: "top top",
    end: () => "+=" + document.querySelector(".horizontal-section").scrollWidth,
    scrub: 1,
    pin: true,
    anticipatePin: 1
  }
});
```

### 3.2 Horizontal Scroll with Multiple Sections

```javascript
// Scroll through multiple panels
const sections = gsap.utils.toArray(".panel");
const scrollTween = gsap.to(sections, {
  xPercent: -100 * (sections.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".container",
    pin: true,
    scrub: 1,
    end: () => "+=" + document.querySelector(".container").offsetWidth
  }
});

// Animate each panel individually
sections.forEach((section, i) => {
  gsap.from(section.querySelector(".content"), {
    opacity: 0,
    scale: 0.8,
    scrollTrigger: {
      trigger: section,
      containerAnimation: scrollTween, // Link to horizontal scroll
      start: "left center",
      end: "right center",
      scrub: true
    }
  });
});
```

### 3.3 Horizontal Scroll with Snap

```javascript
gsap.to(".slides", {
  xPercent: -100 * (sections.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".slider-container",
    pin: true,
    scrub: 1,
    snap: 1 / (sections.length - 1), // Snap to each section
    end: () => "+=" + document.querySelector(".slides").offsetWidth
  }
});
```

---

## Parallax Effects

### 4.1 Simple Parallax (Different Speeds)

```javascript
// Background moves slower than foreground
gsap.to(".bg", {
  y: 200,
  ease: "none",
  scrollTrigger: {
    trigger: ".parallax-section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});

// Foreground moves faster
gsap.to(".fg", {
  y: -100,
  ease: "none",
  scrollTrigger: {
    trigger: ".parallax-section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});
```

### 4.2 Multi-Layer Parallax

```javascript
// Multiple layers with different speeds
gsap.utils.toArray(".parallax-layer").forEach(layer => {
  const depth = layer.dataset.depth; // data-depth="0.2" in HTML
  const movement = -(layer.offsetHeight * depth);

  gsap.to(layer, {
    y: movement,
    ease: "none",
    scrollTrigger: {
      trigger: ".parallax-container",
      start: "top bottom",
      end: "bottom top",
      scrub: true
    }
  });
});
```

### 4.3 Parallax Hero Section

```javascript
// Hero image zooms out while scrolling
gsap.to(".hero-image", {
  scale: 1.5,
  y: 300,
  ease: "none",
  scrollTrigger: {
    trigger: ".hero",
    start: "top top",
    end: "bottom top",
    scrub: true
  }
});

// Hero text fades out
gsap.to(".hero-text", {
  opacity: 0,
  y: 100,
  ease: "none",
  scrollTrigger: {
    trigger: ".hero",
    start: "top top",
    end: "center top",
    scrub: true
  }
});
```

---

## Stagger Animations

### 5.1 Basic Stagger

```javascript
// Stagger animation across multiple elements
gsap.from(".card", {
  opacity: 0,
  y: 50,
  duration: 0.8,
  stagger: 0.2, // 0.2s delay between each
  scrollTrigger: {
    trigger: ".card-container",
    start: "top 80%"
  }
});
```

### 5.2 Stagger from Center

```javascript
// Animate from center outward
gsap.from(".item", {
  scale: 0,
  opacity: 0,
  duration: 0.6,
  stagger: {
    each: 0.1,
    from: "center", // "start", "center", "end", "edges", "random"
    ease: "power2.out"
  },
  scrollTrigger: { trigger: ".grid", start: "top 80%" }
});
```

### 5.3 Grid Stagger

```javascript
// Stagger in a grid pattern
gsap.from(".grid-item", {
  opacity: 0,
  scale: 0.5,
  duration: 0.6,
  stagger: {
    grid: "auto", // Or [rows, columns] like [3, 4]
    from: "center",
    amount: 1.5 // Total time for all staggers
  },
  scrollTrigger: { trigger: ".grid", start: "top 80%" }
});
```

### 5.4 Text Stagger (Words/Characters)

```javascript
// Split text into words
const text = new SplitText(".title", { type: "words" });

gsap.from(text.words, {
  opacity: 0,
  y: 50,
  rotationX: -90,
  stagger: 0.05,
  scrollTrigger: { trigger: ".title", start: "top 80%" }
});

// Split text into characters
const chars = new SplitText(".subtitle", { type: "chars" });

gsap.from(chars.chars, {
  opacity: 0,
  scale: 0,
  stagger: 0.02,
  ease: "back.out(1.7)",
  scrollTrigger: { trigger: ".subtitle", start: "top 80%" }
});
```

---

## Timeline Sequences

### 6.1 Basic Timeline Sequence

```javascript
// Chained animations
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".sequence-section",
    start: "top 80%"
  }
});

tl.from(".heading", { opacity: 0, y: -50, duration: 0.6 })
  .from(".subheading", { opacity: 0, y: -30, duration: 0.5 }, "-=0.3") // Overlap by 0.3s
  .from(".button", { scale: 0, duration: 0.4, ease: "back.out(1.7)" });
```

### 6.2 Timeline with Labels

```javascript
// Use labels for complex timing
const tl = gsap.timeline({
  scrollTrigger: { trigger: ".story", start: "top center" }
});

tl.addLabel("start")
  .from(".hero", { opacity: 0, scale: 0.5 }, "start")
  .from(".text", { opacity: 0, x: -100 }, "start+=0.3")
  .addLabel("reveal")
  .from(".image", { opacity: 0, scale: 1.2 }, "reveal")
  .from(".caption", { opacity: 0 }, "reveal+=0.5");
```

### 6.3 Scrubbed Timeline

```javascript
// Timeline controlled by scroll
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".animation-section",
    start: "top top",
    end: "+=1500",
    scrub: 1,
    pin: true
  }
});

tl.to(".box1", { x: 500, rotation: 360 })
  .to(".box2", { y: 300, scale: 2 }, "-=0.5")
  .to(".box3", { opacity: 0, duration: 0.3 });
```

---

## Text Animations

### 7.1 Text Reveal (Line by Line)

```javascript
// Using SplitText (Club GreenSock plugin)
const split = new SplitText(".text-reveal", { type: "lines" });

gsap.from(split.lines, {
  opacity: 0,
  y: 20,
  stagger: 0.1,
  duration: 0.6,
  scrollTrigger: { trigger: ".text-reveal", start: "top 80%" }
});
```

### 7.2 Scrambled Text Effect

```javascript
// Using ScrambleText (Club GreenSock plugin)
gsap.to(".scramble", {
  duration: 2,
  scrambleText: {
    text: "REVEALED TEXT",
    chars: "lowerCase",
    speed: 0.3
  },
  scrollTrigger: { trigger: ".scramble", start: "top 80%" }
});
```

### 7.3 Typewriter Effect

```javascript
// Simple typewriter using text content
const text = "This text appears letter by letter.";
const element = document.querySelector(".typewriter");

gsap.to(element, {
  duration: text.length * 0.05,
  text: { value: text },
  ease: "none",
  scrollTrigger: { trigger: element, start: "top 80%" }
});
```

### 7.4 Text Highlight on Scroll

```javascript
// Highlight text as you scroll through it
gsap.to(".highlight", {
  backgroundSize: "100% 100%",
  ease: "none",
  scrollTrigger: {
    trigger: ".highlight",
    start: "top 80%",
    end: "top 20%",
    scrub: true
  }
});

// CSS required:
// .highlight {
//   background: linear-gradient(to right, yellow 0%, yellow 100%);
//   background-size: 0% 100%;
//   background-repeat: no-repeat;
// }
```

---

## Image Reveals

### 8.1 Image Curtain Reveal

```html
<!-- HTML Structure -->
<div class="img-curtain">
  <div class="curtain"></div>
  <img src="image.jpg" alt="">
</div>
```

```javascript
// Curtain slides to reveal image
gsap.to(".curtain", {
  xPercent: 100,
  duration: 1,
  ease: "power2.inOut",
  scrollTrigger: {
    trigger: ".img-curtain",
    start: "top 80%"
  }
});
```

```css
/* CSS */
.img-curtain {
  position: relative;
  overflow: hidden;
}
.curtain {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000;
  z-index: 1;
}
```

### 8.2 Image Scale Reveal

```javascript
// Image scales up and reveals from clip-path
gsap.from(".img-scale", {
  scale: 1.3,
  clipPath: "inset(100% 0% 0% 0%)",
  duration: 1.5,
  ease: "power2.out",
  scrollTrigger: {
    trigger: ".img-scale",
    start: "top 80%"
  }
});
```

### 8.3 Image Parallax Zoom

```javascript
// Image zooms while container scrolls
gsap.to(".img-zoom img", {
  scale: 1.2,
  ease: "none",
  scrollTrigger: {
    trigger: ".img-zoom",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});
```

---

## Navigation & UI

### 9.1 Sticky Header with Hide/Show

```javascript
// Hide on scroll down, show on scroll up
let lastScroll = 0;

ScrollTrigger.create({
  start: 100,
  end: 99999,
  onUpdate: (self) => {
    const currentScroll = self.scroll();

    if (currentScroll > lastScroll && currentScroll > 100) {
      // Scrolling down
      gsap.to(".header", { y: -100, duration: 0.3, ease: "power2.out" });
    } else {
      // Scrolling up
      gsap.to(".header", { y: 0, duration: 0.3, ease: "power2.out" });
    }

    lastScroll = currentScroll;
  }
});
```

### 9.2 Active Nav Item Based on Section

```javascript
// Highlight nav item when section is in view
const sections = gsap.utils.toArray("section");

sections.forEach((section, i) => {
  ScrollTrigger.create({
    trigger: section,
    start: "top center",
    end: "bottom center",
    onEnter: () => setActiveNav(i),
    onEnterBack: () => setActiveNav(i)
  });
});

function setActiveNav(index) {
  document.querySelectorAll(".nav-item").forEach((item, i) => {
    item.classList.toggle("active", i === index);
  });
}
```

### 9.3 Smooth Scroll to Anchor

```javascript
// Click anchor link to smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));

    gsap.to(window, {
      duration: 1,
      scrollTo: { y: target, offsetY: 100 }, // 100px offset for header
      ease: "power2.inOut"
    });
  });
});
```

### 9.4 Drawer/Sidebar Animation

```javascript
// Open drawer
function openDrawer() {
  gsap.to(".drawer", {
    x: 0,
    duration: 0.4,
    ease: "power2.out"
  });

  gsap.to(".overlay", {
    opacity: 1,
    duration: 0.3,
    pointerEvents: "all"
  });
}

// Close drawer
function closeDrawer() {
  gsap.to(".drawer", {
    x: "100%", // Or -100% for left drawer
    duration: 0.4,
    ease: "power2.in"
  });

  gsap.to(".overlay", {
    opacity: 0,
    duration: 0.3,
    pointerEvents: "none"
  });
}
```

---

## Page Transitions

### 10.1 Basic Page Transition (Overlay)

```javascript
// On link click
function pageTransition(url) {
  const tl = gsap.timeline({
    onComplete: () => window.location.href = url
  });

  tl.to(".transition-overlay", {
    yPercent: 0,
    duration: 0.5,
    ease: "power2.inOut"
  })
  .to(".transition-overlay", {
    yPercent: -100,
    duration: 0.5,
    ease: "power2.inOut"
  }, "+=0.1");
}

// Attach to links
document.querySelectorAll("a").forEach(link => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    pageTransition(link.href);
  });
});
```

### 10.2 Fade Page Transition

```javascript
// Fade out current page, load new page
function fadeTransition(url) {
  gsap.to(".page-container", {
    opacity: 0,
    duration: 0.5,
    onComplete: () => {
      window.location.href = url;
    }
  });
}

// On page load, fade in
window.addEventListener("load", () => {
  gsap.from(".page-container", {
    opacity: 0,
    duration: 0.5
  });
});
```

---

## Scroll Progress Indicators

### 11.1 Horizontal Progress Bar

```javascript
// Progress bar at top of page
gsap.to(".progress-bar", {
  scaleX: 1,
  ease: "none",
  scrollTrigger: {
    start: "top top",
    end: "bottom bottom",
    scrub: 0.3
  }
});

// CSS: .progress-bar { transform-origin: left; }
```

### 11.2 Circular Progress Indicator

```javascript
// Circular progress (SVG circle)
const circle = document.querySelector(".progress-circle");
const length = circle.getTotalLength();

// Set up circle
gsap.set(circle, {
  strokeDasharray: length,
  strokeDashoffset: length
});

// Animate on scroll
gsap.to(circle, {
  strokeDashoffset: 0,
  ease: "none",
  scrollTrigger: {
    start: "top top",
    end: "bottom bottom",
    scrub: 0.3
  }
});
```

### 11.3 Section Progress (Multi-step)

```javascript
// Update progress indicator through sections
const sections = gsap.utils.toArray(".step");
const progressDots = gsap.utils.toArray(".progress-dot");

sections.forEach((section, i) => {
  ScrollTrigger.create({
    trigger: section,
    start: "top center",
    end: "bottom center",
    onEnter: () => activateDot(i),
    onEnterBack: () => activateDot(i)
  });
});

function activateDot(index) {
  progressDots.forEach((dot, i) => {
    if (i <= index) {
      dot.classList.add("active");
    } else {
      dot.classList.remove("active");
    }
  });
}
```

---

## Image Sequences

### 12.1 Canvas Image Sequence on Scroll

```javascript
// Scrub through image sequence
const canvas = document.querySelector("#canvas");
const context = canvas.getContext("2d");

const frameCount = 148;
const images = [];
const imageSeq = { frame: 0 };

// Preload images
for (let i = 0; i < frameCount; i++) {
  const img = new Image();
  img.src = `./frames/frame_${String(i).padStart(4, '0')}.jpg`;
  images.push(img);
}

// Render frame
function render() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.drawImage(images[imageSeq.frame], 0, 0);
}

// Animate frame property on scroll
gsap.to(imageSeq, {
  frame: frameCount - 1,
  snap: "frame",
  ease: "none",
  scrollTrigger: {
    trigger: ".image-sequence",
    start: "top top",
    end: "+=3000",
    pin: true,
    scrub: 0.5,
    onUpdate: render
  }
});

// Initial render
images[0].onload = render;
```

---

## Responsive Patterns

### 13.1 Different Animations per Breakpoint

```javascript
// Use ScrollTrigger.matchMedia for responsive animations
ScrollTrigger.matchMedia({
  // Desktop
  "(min-width: 800px)": function() {
    gsap.to(".element", {
      x: 500,
      scrollTrigger: {
        trigger: ".element",
        start: "top 80%",
        scrub: true
      }
    });
  },

  // Mobile
  "(max-width: 799px)": function() {
    gsap.to(".element", {
      y: 200, // Different animation on mobile
      scrollTrigger: {
        trigger: ".element",
        start: "top 80%",
        scrub: true
      }
    });
  }
});
```

### 13.2 Kill Animations on Mobile

```javascript
// Disable ScrollTrigger animations on mobile
if (window.innerWidth > 768) {
  // Desktop-only animations
  gsap.from(".desktop-animation", {
    opacity: 0,
    y: 100,
    scrollTrigger: {
      trigger: ".desktop-animation",
      start: "top 80%"
    }
  });
} else {
  // Simple CSS fallback on mobile
  gsap.set(".desktop-animation", { opacity: 1, y: 0 });
}
```

---

## Integration Patterns

### 14.1 GSAP + React (useGSAP hook)

```javascript
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

function Component() {
  const containerRef = useRef();

  useGSAP(() => {
    gsap.from(".box", {
      opacity: 0,
      y: 50,
      scrollTrigger: {
        trigger: ".box",
        start: "top 80%"
      }
    });
  }, { scope: containerRef }); // Scope to container

  return <div ref={containerRef}>...</div>;
}
```

### 14.2 GSAP + Three.js

```javascript
// Animate Three.js camera on scroll
gsap.to(camera.position, {
  z: 10,
  ease: "none",
  scrollTrigger: {
    trigger: ".threejs-section",
    start: "top top",
    end: "bottom top",
    scrub: true
  }
});

// Animate object rotation
gsap.to(mesh.rotation, {
  y: Math.PI * 2,
  ease: "none",
  scrollTrigger: {
    trigger: ".threejs-section",
    scrub: 1
  }
});
```

### 14.3 GSAP + Locomotive Scroll

```javascript
// Use Locomotive Scroll as the scroller
import LocomotiveScroll from 'locomotive-scroll';

const locoScroll = new LocomotiveScroll({
  el: document.querySelector(".smooth-scroll"),
  smooth: true
});

// Tell ScrollTrigger to use Locomotive Scroll
ScrollTrigger.scrollerProxy(".smooth-scroll", {
  scrollTop(value) {
    return arguments.length ? locoScroll.scrollTo(value, 0, 0) : locoScroll.scroll.instance.scroll.y;
  },
  getBoundingClientRect() {
    return { top: 0, left: 0, width: window.innerWidth, height: window.innerHeight };
  }
});

// Update ScrollTrigger when Locomotive Scroll updates
locoScroll.on("scroll", ScrollTrigger.update);
ScrollTrigger.addEventListener("refresh", () => locoScroll.update());
```

---

## Best Practices

### Performance Optimization

```javascript
// 1. Use will-change CSS for animated elements
gsap.set(".animated", { willChange: "transform, opacity" });

// 2. Kill animations when not needed
const st = ScrollTrigger.create({ /* ... */ });
st.kill(); // Clean up

// 3. Batch similar animations
ScrollTrigger.batch(".item", { /* ... */ });

// 4. Use scrub for smooth scroll-driven animations
scrub: 1 // 1 second lag for smoothness

// 5. Limit markers in production
markers: process.env.NODE_ENV === "development"
```

### Refresh After DOM Changes

```javascript
// After images load, layout shifts, etc.
window.addEventListener("load", () => {
  ScrollTrigger.refresh();
});

// Or after specific events
imagesLoaded(".gallery", () => {
  ScrollTrigger.refresh();
});
```

### Clean Up on Unmount (React/Vue)

```javascript
// React useEffect cleanup
useEffect(() => {
  const st = ScrollTrigger.create({ /* ... */ });

  return () => {
    st.kill(); // Clean up on unmount
  };
}, []);
```

---

## Common Gotchas

### ❌ Forgetting to Register Plugins

```javascript
// WRONG - ScrollTrigger won't work
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.to(".box", { scrollTrigger: { /* ... */ } }); // Error!

// CORRECT
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger);
gsap.to(".box", { scrollTrigger: { /* ... */ } }); // Works!
```

### ❌ Animating Before DOM Ready

```javascript
// WRONG - Elements may not exist yet
gsap.from(".box", { opacity: 0 });

// CORRECT
window.addEventListener("load", () => {
  gsap.from(".box", { opacity: 0 });
});

// Or with DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
  gsap.from(".box", { opacity: 0 });
});
```

### ❌ Not Refreshing After Layout Changes

```javascript
// WRONG - ScrollTrigger positions are stale
loadImages().then(() => {
  // Images loaded, layout shifted
  // ScrollTrigger positions are now wrong!
});

// CORRECT
loadImages().then(() => {
  ScrollTrigger.refresh(); // Recalculate positions
});
```

---

## Quick Copy-Paste Starter

```javascript
// Complete starter template
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

// Wait for DOM
document.addEventListener("DOMContentLoaded", () => {

  // Fade in on scroll
  gsap.utils.toArray(".fade-in").forEach(element => {
    gsap.from(element, {
      opacity: 0,
      y: 50,
      duration: 1,
      scrollTrigger: {
        trigger: element,
        start: "top 80%",
        toggleActions: "play none none reverse"
      }
    });
  });

  // Parallax
  gsap.to(".parallax", {
    y: 200,
    ease: "none",
    scrollTrigger: {
      trigger: ".parallax-section",
      start: "top bottom",
      end: "bottom top",
      scrub: true
    }
  });

  // Pin section
  ScrollTrigger.create({
    trigger: ".pin-section",
    start: "top top",
    end: "+=500",
    pin: true
  });

  // Refresh after images load
  window.addEventListener("load", () => {
    ScrollTrigger.refresh();
  });

});
```

---

## Resources

- [GSAP Documentation](https://gsap.com/docs/)
- [ScrollTrigger Demos](https://gsap.com/docs/v3/Plugins/ScrollTrigger)
- [GSAP Showcase](https://gsap.com/showcase/)
- [Codepen GSAP Examples](https://codepen.io/GreenSock/pens/popular)

---

**Remember**: Start simple, test often, and use `markers: true` during development to debug ScrollTrigger positions.



===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/references/easing_guide.md =====

# GSAP Easing Functions - Visual Guide

## What Are Easings?

Easings control the **rate of change** during an animation, making motion feel more natural and expressive. They define the acceleration curve between the start and end of an animation.

- **Linear**: Constant speed (robotic, unnatural)
- **Ease In**: Starts slow, ends fast (acceleration)
- **Ease Out**: Starts fast, ends slow (deceleration) - **Most common**
- **Ease InOut**: Starts slow, speeds up, ends slow (smooth both ends)

## Why Easings Matter

```javascript
// Without proper easing - feels robotic
gsap.to(".box", { x: 500, duration: 1, ease: "none" });

// With easing - feels natural
gsap.to(".box", { x: 500, duration: 1, ease: "power2.out" });
```

**The 80/20 Rule**: Most UI animations use `power2.out`, `power3.out`, or `back.out`.

---

## Easing Families

### 1. Power Easings (Most Common)

Power easings use polynomial curves. Higher numbers = more aggressive curves.

#### power1 (Quad)
```
Curve Shape:
  in:    ╱─────  Gentle acceleration
  out:   ─────╲  Gentle deceleration
  inOut: ╱───╲  Gentle both ends
```

**Use Cases**:
- Subtle UI transitions
- Small movements (tooltips, dropdowns)
- Background animations that shouldn't grab attention

**Example**:
```javascript
// Tooltip fade in
gsap.from(".tooltip", {
  opacity: 0,
  y: -10,
  duration: 0.3,
  ease: "power1.out"
});
```

---

#### power2 (Cubic) ⭐ MOST POPULAR
```
Curve Shape:
  in:    ╱╱────  Moderate acceleration
  out:   ────╲╲  Moderate deceleration
  inOut: ╱──╲  Moderate both ends
```

**Use Cases**:
- **Default choice for most UI animations**
- Button clicks, modal animations
- Element entrances/exits
- Smooth scrolling

**Example**:
```javascript
// Modal slide in
gsap.from(".modal", {
  y: 50,
  opacity: 0,
  duration: 0.5,
  ease: "power2.out" // ⭐ Most common choice
});
```

---

#### power3 (Quart)
```
Curve Shape:
  in:    ╱╱╱───  Strong acceleration
  out:   ───╲╲╲  Strong deceleration
  inOut: ╱─╲  Strong both ends
```

**Use Cases**:
- Hero animations
- Page transitions
- Large movements across screen
- Attention-grabbing effects

**Example**:
```javascript
// Hero section reveal
gsap.from(".hero", {
  scale: 0.8,
  opacity: 0,
  duration: 1,
  ease: "power3.out"
});
```

---

#### power4 (Quint)
```
Curve Shape:
  in:    ╱╱╱╱──  Very strong acceleration
  out:   ──╲╲╲╲  Very strong deceleration
  inOut: ╱╲  Very strong both ends
```

**Use Cases**:
- Dramatic reveals
- Full-screen transitions
- Heavy objects (metaphorically)
- When you want maximum impact

**Example**:
```javascript
// Full-screen overlay
gsap.to(".overlay", {
  scale: 1,
  opacity: 1,
  duration: 0.8,
  ease: "power4.out"
});
```

---

### 2. Back Easings (Overshoot)

Back easings **overshoot** the target, then settle back. Creates anticipation and playfulness.

```
Curve Shape:
  in:    ╲╱────  Backs up, then accelerates
  out:   ────╱╲  Overshoots, then settles
  inOut: ╲╱─╱╲  Both ends overshoot
```

**Parameters**: `back.out(1.7)` - Higher number = more overshoot (default: 1.7)

**Use Cases**:
- Playful UI elements
- Buttons with personality
- Attention-grabbing reveals
- Fun micro-interactions

**Example**:
```javascript
// Button with bounce
gsap.from(".button", {
  scale: 0,
  duration: 0.5,
  ease: "back.out(1.7)" // Classic overshoot
});

// Extreme overshoot for fun effect
gsap.from(".badge", {
  scale: 0,
  rotation: -180,
  duration: 0.8,
  ease: "back.out(3)" // More dramatic
});
```

**Pro Tip**: Use `back.out(1.2)` for subtle overshoot, `back.out(2.5)` for exaggerated effect.

---

### 3. Elastic Easings (Spring/Rubber Band)

Elastic easings create a **spring/bounce** effect, oscillating around the target.

```
Curve Shape:
  in:    ╲╱╲╱──  Oscillates, then accelerates
  out:   ──╱╲╱╲  Overshoots multiple times, then settles
  inOut: ╲╱╲╱╲  Both ends oscillate
```

**Parameters**: `elastic.out(amplitude, period)`
- **amplitude**: Strength of oscillation (default: 1)
- **period**: Frequency of oscillation (default: 0.3)

**Use Cases**:
- Cartoonish effects
- Game UI elements
- Fun landing pages
- Notification badges
- **Use sparingly** - can feel gimmicky

**Example**:
```javascript
// Notification badge
gsap.from(".badge", {
  scale: 0,
  duration: 1,
  ease: "elastic.out(1, 0.3)"
});

// Stronger spring effect
gsap.from(".icon", {
  y: -50,
  duration: 1.5,
  ease: "elastic.out(1.5, 0.4)" // More bounce
});
```

**Warning**: Elastic can feel unprofessional if overused. Best for gaming/playful interfaces.

---

### 4. Bounce Easings

Bounce easings simulate a **bouncing ball** landing.

```
Curve Shape:
  in:    ╲╱╲╱╲──  Bounces, then accelerates
  out:   ──╲╱╲╱╲  Lands with decreasing bounces
  inOut: ╲╱─╱╲  Both ends bounce
```

**Use Cases**:
- Elements "dropping" into place
- Playful UI (games, children's apps)
- Landing animations
- Fun effects (use sparingly)

**Example**:
```javascript
// Element drops in
gsap.from(".card", {
  y: -200,
  duration: 1,
  ease: "bounce.out"
});

// Multiple cards with stagger
gsap.from(".card", {
  y: -100,
  opacity: 0,
  duration: 1,
  ease: "bounce.out",
  stagger: 0.1
});
```

**Pro Tip**: Combine with `power2.in` for objects falling before bouncing.

---

### 5. Circ Easings (Circular)

Circular easings use a quarter-circle curve. Creates **sharp acceleration/deceleration**.

```
Curve Shape:
  in:    ╱╱────  Sharp acceleration (quarter circle)
  out:   ────╲╲  Sharp deceleration
  inOut: ╱──╲  Sharp both ends
```

**Use Cases**:
- Fast, snappy movements
- Material Design-style animations
- Quick transitions
- When you want instant impact

**Example**:
```javascript
// Quick slide-in drawer
gsap.to(".drawer", {
  x: 0,
  duration: 0.3,
  ease: "circ.out"
});
```

---

### 6. Expo Easings (Exponential)

Exponential easings create **very dramatic** acceleration/deceleration curves.

```
Curve Shape:
  in:    ╱╱╱───  Extremely slow start, then explodes
  out:   ───╲╲╲  Extremely fast start, then crawls
  inOut: ╱─╲  Extreme both ends
```

**Use Cases**:
- Dramatic reveals
- Cinematic effects
- Zoom-in/zoom-out animations
- When you want **maximum drama**

**Example**:
```javascript
// Dramatic zoom in
gsap.from(".hero-image", {
  scale: 5,
  opacity: 0,
  duration: 1.5,
  ease: "expo.out"
});

// Intense page transition
gsap.to(".page", {
  x: -window.innerWidth,
  duration: 1,
  ease: "expo.inOut"
});
```

---

### 7. Sine Easings

Sine easings are **extremely gentle**, using a sine wave curve.

```
Curve Shape:
  in:    ╱─────  Very gentle acceleration
  out:   ─────╲  Very gentle deceleration
  inOut: ╱───╲  Very gentle both ends
```

**Use Cases**:
- Subtle, barely-noticeable animations
- Background movements
- Ambient effects
- Parallax scrolling
- When animation should be **invisible**

**Example**:
```javascript
// Gentle parallax
gsap.to(".bg", {
  y: 100,
  ease: "sine.out",
  scrollTrigger: {
    scrub: true
  }
});

// Subtle float animation
gsap.to(".cloud", {
  y: "+=20",
  duration: 3,
  ease: "sine.inOut",
  yoyo: true,
  repeat: -1
});
```

---

### 8. None (Linear)

No easing at all - constant speed throughout.

```
Curve Shape: ──────  Perfectly straight line
```

**Use Cases**:
- **ScrollTrigger with scrub** (let user control speed)
- Loading bars (constant progress)
- Background loops
- Mechanical movements
- **Rarely used for regular animations**

**Example**:
```javascript
// Horizontal scroll (user controls speed)
gsap.to(".panels", {
  xPercent: -100,
  ease: "none", // User controls via scroll
  scrollTrigger: {
    scrub: true
  }
});

// Loading bar
gsap.to(".progress", {
  width: "100%",
  duration: 5,
  ease: "none"
});
```

---

## Quick Decision Tree

### 1. What's the purpose?

**Subtle UI transition** → `power1.out` or `power2.out`

**Standard animation** → `power2.out` ⭐ (default choice)

**Hero/dramatic effect** → `power3.out` or `power4.out`

**Playful/fun** → `back.out(1.7)` or `elastic.out()`

**Game/cartoon** → `bounce.out` or `elastic.out()`

**Scroll-driven** → `none` (with scrub)

**Background/ambient** → `sine.inOut`

---

### 2. How noticeable should it be?

```
Subtle          ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━→ Dramatic
sine.out    power1.out    power2.out    power3.out    expo.out
                              ⭐ Start here

Gentle          ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━→ Playful
circ.out    back.out(1.2)    back.out(1.7)    elastic.out()
```

---

## Common Patterns by Use Case

### UI Animations (80% of use cases)
```javascript
// Standard choice
ease: "power2.out"

// Slightly more dramatic
ease: "power3.out"

// Playful
ease: "back.out(1.7)"
```

### Scroll Animations
```javascript
// Let user control speed
ease: "none",
scrollTrigger: { scrub: true }

// Smooth snap scrolling
ease: "power2.inOut",
scrollTrigger: { snap: 1 }
```

### Micro-interactions
```javascript
// Button hover
ease: "power1.out", duration: 0.2

// Toggle switch
ease: "back.out(2)", duration: 0.4

// Ripple effect
ease: "power2.out", duration: 0.6
```

### Page Transitions
```javascript
// Standard page transition
ease: "power3.inOut", duration: 0.8

// Dramatic reveal
ease: "expo.out", duration: 1.2
```

### Loading States
```javascript
// Loading spinner
ease: "none", repeat: -1

// Progress bar
ease: "power2.out", duration: 2
```

---

## Easing Combinations

### Sequential Easings (Timeline)
```javascript
const tl = gsap.timeline();

// Slide in fast, settle slow
tl.to(".card", { y: 0, duration: 0.3, ease: "power3.in" })
  .to(".card", { scale: 1, duration: 0.4, ease: "back.out(2)" });
```

### Staggered with Different Easings
```javascript
gsap.from(".item", {
  opacity: 0,
  y: 50,
  duration: 0.6,
  ease: "power2.out",
  stagger: {
    each: 0.1,
    ease: "power1.inOut" // Easing for stagger timing itself
  }
});
```

### Physics-based Fallback
```javascript
// Light object (fast)
gsap.to(".feather", { y: 500, duration: 2, ease: "sine.in" });

// Heavy object (slow start)
gsap.to(".anvil", { y: 500, duration: 1.5, ease: "power4.in" });
```

---

## Custom Easings

### Custom Bezier Curve
```javascript
// Use CustomEase plugin (Club GreenSock)
gsap.registerPlugin(CustomEase);

CustomEase.create("customBounce", "0.5,0,0.75,1.5,1");

gsap.to(".box", {
  x: 500,
  duration: 1,
  ease: "customBounce"
});
```

### Steps (Stepped Animation)
```javascript
// Simulate frame-by-frame animation
gsap.to(".sprite", {
  x: 500,
  duration: 1,
  ease: "steps(12)" // 12 discrete steps
});
```

---

## Testing Easings

### Easing Visualizer (Inline Tool)

Save this as `easings.html` to test easings visually:

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <style>
    body { font-family: system-ui; padding: 40px; background: #1a1a2e; color: white; }
    .box { width: 50px; height: 50px; background: #00ffcc; margin: 20px 0; border-radius: 8px; }
    button { padding: 10px 20px; margin: 5px; background: #00ffcc; border: none; border-radius: 5px; cursor: pointer; }
  </style>
</head>
<body>
  <h1>GSAP Easing Tester</h1>
  <div id="boxes"></div>
  <button onclick="testAll()">Test All Easings</button>

  <script>
    const easings = [
      "none",
      "power1.out", "power2.out", "power3.out", "power4.out",
      "back.out(1.7)", "elastic.out(1, 0.3)", "bounce.out",
      "circ.out", "expo.out", "sine.out"
    ];

    const container = document.getElementById('boxes');
    easings.forEach(ease => {
      const label = document.createElement('div');
      label.textContent = ease;
      label.style.marginTop = '20px';
      container.appendChild(label);

      const box = document.createElement('div');
      box.className = 'box';
      box.dataset.ease = ease;
      container.appendChild(box);
    });

    function testAll() {
      document.querySelectorAll('.box').forEach(box => {
        gsap.fromTo(box,
          { x: 0 },
          { x: 500, duration: 1.5, ease: box.dataset.ease }
        );
      });
    }
  </script>
</body>
</html>
```

**Online Tools**:
- [GreenSock Ease Visualizer](https://gsap.com/docs/v3/Eases)
- [Cubic Bezier Generator](https://cubic-bezier.com)

---

## Performance Notes

### Do Easings Affect Performance?

**No** - Easings are mathematical functions with negligible overhead. Choose based on aesthetics, not performance.

**Exception**: Custom bezier curves with many control points can be slightly slower (still negligible).

---

## Common Mistakes

### ❌ Using Linear for UI Animations
```javascript
// Feels robotic
gsap.to(".button", { scale: 1.1, duration: 0.3, ease: "none" });
```

✅ **Fix**: Use `power2.out`
```javascript
gsap.to(".button", { scale: 1.1, duration: 0.3, ease: "power2.out" });
```

---

### ❌ Over-using Elastic/Bounce
```javascript
// Every element bounces - feels gimmicky
gsap.from(".item", { scale: 0, ease: "elastic.out(2, 0.3)", stagger: 0.1 });
```

✅ **Fix**: Use sparingly for key elements
```javascript
// Only hero element has elastic
gsap.from(".hero", { scale: 0, ease: "elastic.out(1, 0.3)" });
gsap.from(".item", { scale: 0, ease: "back.out(1.7)", stagger: 0.1 });
```

---

### ❌ Wrong Direction (in vs out)
```javascript
// Element exits with ease.in (feels slow to start)
gsap.to(".modal", { opacity: 0, ease: "power2.in" });
```

✅ **Fix**: Use `out` for exits
```javascript
gsap.to(".modal", { opacity: 0, ease: "power2.out" });
```

**Rule**:
- **Entrances** → `ease.out` (fast start, slow end)
- **Exits** → `ease.out` (consistent)
- **Both** → `ease.inOut` (smooth both ends)

---

## Best Practices

### 1. Start with power2.out
It's the goldilocks easing - not too gentle, not too aggressive.

### 2. Match Easing to Content
- **Lightweight** (modals, tooltips) → `power1.out` or `power2.out`
- **Medium** (cards, sections) → `power2.out` or `power3.out`
- **Heavy** (full pages, heroes) → `power3.out` or `power4.out`

### 3. Be Consistent
Use the same easing family throughout your project for cohesion.

### 4. Test at Different Speeds
Easings behave differently at different durations:
```javascript
// Too short - easing barely noticeable
duration: 0.1, ease: "power3.out"

// Sweet spot
duration: 0.4, ease: "power3.out"

// Too long - feels sluggish
duration: 2, ease: "power3.out"
```

### 5. Consider Context
- **Professional/Corporate** → `power2.out`, `power3.out`
- **Playful/Fun** → `back.out`, `elastic.out`
- **Luxury/Premium** → `expo.out`, `power4.out`
- **Fast/Responsive** → `circ.out`, `power2.out`

---

## Cheat Sheet

| Use Case | Easing | Duration | Notes |
|----------|--------|----------|-------|
| Default UI | `power2.out` | 0.3-0.5s | Start here |
| Hero animation | `power3.out` | 0.8-1.2s | More impact |
| Button hover | `power1.out` | 0.2s | Quick & subtle |
| Modal open | `power2.out` | 0.4s | Smooth entrance |
| Tooltip | `power1.out` | 0.2s | Fast & light |
| Scroll scrub | `none` | N/A | User-controlled |
| Page transition | `power3.inOut` | 0.8s | Smooth both ends |
| Playful button | `back.out(1.7)` | 0.5s | Overshoot |
| Notification | `back.out(2)` | 0.6s | Attention-grabbing |
| Parallax | `sine.out` | N/A | Barely noticeable |
| Loading bar | `none` | Variable | Constant speed |
| Bounce-in | `bounce.out` | 1s | Use sparingly |

---

## Summary

**The 3 Easings You Need to Know**:

1. **power2.out** ⭐ - Your default choice (80% of animations)
2. **power3.out** - For dramatic effects
3. **back.out(1.7)** - For playful interactions

**Golden Rules**:
- When in doubt, use `power2.out`
- Entrances and exits both use `.out`
- ScrollTrigger with scrub uses `none`
- Be consistent across your project
- Test different durations to find the sweet spot

**Remember**: Good easing makes animations feel natural and purposeful. Bad easing makes them feel robotic or gimmicky.



===== FILE: plugins/individual/gsap-scrolltrigger/agents/gsap-scrolltrigger-choreographer.md =====

# GSAP ScrollTrigger Animation Choreographer

## Role

Expert animation choreographer specializing in GSAP ScrollTrigger animation design, timing, and orchestration.

## Expertise

- Animation timing and easing
- Timeline sequencing
- Performance-optimized animations
- Cross-library animation integration
- Interactive animation patterns
- Scroll-driven animation design

## When to use

Activate this agent when working on:
- Complex animation sequences
- Multi-element choreography
- Scroll-triggered animations
- Interactive animation systems
- Animation performance optimization

## Approach

1. Understand animation goals and user experience
2. Design animation timing and sequencing
3. Implement using GSAP ScrollTrigger best practices
4. Optimize for smooth 60fps performance
5. Test across devices and browsers

## Tools

This agent has access to:
- GSAP ScrollTrigger skill knowledge
- Animation pattern libraries
- Performance optimization techniques
- Timeline management strategies



===== FILE: plugins/individual/gsap-scrolltrigger/commands/generate_animation.md =====

# /gsap-scrolltrigger-generate_animation

GSAP ScrollTrigger - Generate Animation

## Description

Executes the generate_animation script for GSAP ScrollTrigger.

## Usage

```bash
/gsap-scrolltrigger-generate_animation
```

## Implementation

This command runs the `generate_animation.py` script from the GSAP ScrollTrigger skill, which provides automated assistance for generate animation.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/gsap-scrolltrigger/commands/timeline_builder.md =====

# /gsap-scrolltrigger-timeline_builder

GSAP ScrollTrigger - Timeline Builder

## Description

Executes the timeline_builder script for GSAP ScrollTrigger.

## Usage

```bash
/gsap-scrolltrigger-timeline_builder
```

## Implementation

This command runs the `timeline_builder.py` script from the GSAP ScrollTrigger skill, which provides automated assistance for timeline builder.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/scripts/generate_animation.py =====

```py
#!/usr/bin/env python3
"""
GSAP Animation Code Generator

Generates boilerplate GSAP animation code for common patterns.
Supports various animation types, ScrollTrigger configurations, and export formats.

Usage:
    python3 generate_animation.py --type fade-in --trigger ".box" --output code.js
    python3 generate_animation.py --type horizontal-scroll --sections 5 --output code.js
    python3 generate_animation.py --type timeline --steps "fade,slide,scale" --output code.js
"""

import argparse
import sys
from pathlib import Path

# Animation Templates
TEMPLATES = {
    "fade-in": '''// Fade in animation
gsap.from("{trigger}", {{
  opacity: 0,
  y: {distance},
  duration: {duration},
  ease: "{ease}",
  scrollTrigger: {{
    trigger: "{trigger}",
    start: "{start}",
    end: "{end}",
    toggleActions: "{toggle_actions}"{scrub}{markers}
  }}
}});''',

    "fade-in-scrub": '''// Fade in with scroll scrubbing
gsap.from("{trigger}", {{
  opacity: 0,
  y: {distance},
  scrollTrigger: {{
    trigger: "{trigger}",
    start: "{start}",
    end: "{end}",
    scrub: {scrub_value}{markers}
  }}
}});''',

    "pin-section": '''// Pin section while scrolling
ScrollTrigger.create({{
  trigger: "{trigger}",
  start: "{start}",
  end: "{end}",
  pin: true,
  pinSpacing: {pin_spacing},
  anticipatePin: 1{markers}
}});''',

    "pin-with-animation": '''// Pin with content animation
const tl = gsap.timeline({{
  scrollTrigger: {{
    trigger: "{trigger}",
    start: "{start}",
    end: "{end}",
    pin: true,
    scrub: {scrub_value}{markers}
  }}
}});

tl.from("{trigger} .content", {{ opacity: 0, y: 100 }})
  .from("{trigger} .subtitle", {{ opacity: 0, y: 50 }}, "-=0.5")
  .to("{trigger} .image", {{ scale: 1.2, rotation: 5 }});''',

    "horizontal-scroll": '''// Horizontal scroll
const sections = gsap.utils.toArray("{trigger}");
gsap.to(sections, {{
  xPercent: -100 * (sections.length - 1),
  ease: "none",
  scrollTrigger: {{
    trigger: "{container}",
    pin: true,
    scrub: 1,
    snap: {snap},
    end: () => "+=" + document.querySelector("{container}").offsetWidth{markers}
  }}
}});''',

    "parallax": '''// Parallax effect
gsap.to("{trigger}", {{
  y: {distance},
  ease: "none",
  scrollTrigger: {{
    trigger: "{container}",
    start: "top bottom",
    end: "bottom top",
    scrub: true{markers}
  }}
}});''',

    "stagger": '''// Stagger animation
gsap.from("{trigger}", {{
  opacity: 0,
  y: {distance},
  duration: {duration},
  ease: "{ease}",
  stagger: {{
    each: {stagger_delay},
    from: "{stagger_from}"{stagger_grid}
  }},
  scrollTrigger: {{
    trigger: "{container}",
    start: "{start}"{markers}
  }}
}});''',

    "timeline": '''// Timeline sequence
const tl = gsap.timeline({{
  scrollTrigger: {{
    trigger: "{trigger}",
    start: "{start}"{markers}
  }}
}});

{timeline_steps}''',

    "batch": '''// Batch animation
ScrollTrigger.batch("{trigger}", {{
  onEnter: batch => gsap.from(batch, {{
    opacity: 0,
    y: {distance},
    stagger: {stagger_delay},
    duration: {duration},
    ease: "{ease}"
  }}),
  start: "{start}",
  once: {once}{markers}
}});''',

    "toggle-class": '''// Toggle class on scroll
ScrollTrigger.create({{
  trigger: "{trigger}",
  start: "{start}",
  end: "{end}",
  toggleClass: {{ targets: "{trigger}", className: "{class_name}" }}{markers}
}});''',

    "image-sequence": '''// Canvas image sequence
const canvas = document.querySelector("{canvas}");
const context = canvas.getContext("2d");

const frameCount = {frame_count};
const images = [];
const imageSeq = {{ frame: 0 }};

// Preload images
for (let i = 0; i < frameCount; i++) {{
  const img = new Image();
  img.src = `{image_path}/frame_${{String(i).padStart(4, '0')}}.jpg`;
  images.push(img);
}}

function render() {{
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.drawImage(images[imageSeq.frame], 0, 0);
}}

gsap.to(imageSeq, {{
  frame: frameCount - 1,
  snap: "frame",
  ease: "none",
  scrollTrigger: {{
    trigger: "{trigger}",
    start: "top top",
    end: "+=3000",
    pin: true,
    scrub: 0.5,
    onUpdate: render{markers}
  }}
}});

images[0].onload = render;''',

    "smooth-scroll-to": '''// Smooth scroll to element
document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
  anchor.addEventListener("click", function(e) {{
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));

    gsap.to(window, {{
      duration: {duration},
      scrollTo: {{ y: target, offsetY: {offset} }},
      ease: "{ease}"
    }});
  }});
}});''',

    "progress-bar": '''// Progress bar
gsap.to("{trigger}", {{
  scaleX: 1,
  ease: "none",
  scrollTrigger: {{
    start: "top top",
    end: "bottom bottom",
    scrub: 0.3{markers}
  }}
}});

// CSS required:
// {trigger} {{ transform-origin: left; }}''',
}

# Timeline step templates
TIMELINE_STEPS = {
    "fade": 'tl.from("{selector}", {{ opacity: 0, duration: 0.6 }})',
    "slide": 'tl.from("{selector}", {{ y: 50, duration: 0.5 }}, "-=0.3")',
    "scale": 'tl.from("{selector}", {{ scale: 0, duration: 0.4, ease: "back.out(1.7)" }})',
    "rotate": 'tl.to("{selector}", {{ rotation: 360, duration: 1 }})',
    "color": 'tl.to("{selector}", {{ backgroundColor: "#ff0000", duration: 0.5 }})',
}

# Preset configurations
PRESETS = {
    "subtle": {
        "duration": 0.6,
        "distance": 30,
        "ease": "power1.out"
    },
    "standard": {
        "duration": 0.8,
        "distance": 50,
        "ease": "power2.out"
    },
    "dramatic": {
        "duration": 1.2,
        "distance": 100,
        "ease": "power3.out"
    },
    "playful": {
        "duration": 0.8,
        "distance": 50,
        "ease": "back.out(1.7)"
    }
}

def generate_animation(args):
    """Generate GSAP animation code based on arguments."""

    template = TEMPLATES.get(args.type)
    if not template:
        print(f"Error: Unknown animation type '{args.type}'")
        print(f"Available types: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)

    # Get preset values
    preset = PRESETS.get(args.preset, PRESETS["standard"])

    # Prepare template variables
    variables = {
        "trigger": args.trigger,
        "container": args.container or args.trigger,
        "canvas": args.canvas or "#canvas",
        "start": args.start,
        "end": args.end,
        "duration": args.duration or preset["duration"],
        "distance": args.distance or preset["distance"],
        "ease": args.ease or preset["ease"],
        "toggle_actions": args.toggle_actions,
        "scrub": f",\n    scrub: {args.scrub}" if args.scrub and args.type != "fade-in" else "",
        "scrub_value": args.scrub if args.scrub else 1,
        "markers": f",\n    markers: {str(args.markers).lower()}" if args.markers else "",
        "pin_spacing": str(args.pin_spacing).lower(),
        "snap": f"1 / (sections.length - 1)" if args.snap else "false",
        "stagger_delay": args.stagger_delay,
        "stagger_from": args.stagger_from,
        "stagger_grid": f',\n    grid: "auto"' if args.stagger_grid else "",
        "once": str(args.once).lower(),
        "class_name": args.class_name or "active",
        "frame_count": args.frame_count or 100,
        "image_path": args.image_path or "./frames",
        "offset": args.offset or 100,
    }

    # Handle timeline steps
    if args.type == "timeline" and args.timeline_steps:
        steps = args.timeline_steps.split(",")
        timeline_code = []
        for i, step in enumerate(steps):
            step = step.strip()
            selector = f"{args.trigger} .step-{i+1}"
            if step in TIMELINE_STEPS:
                timeline_code.append(TIMELINE_STEPS[step].format(selector=selector))
        variables["timeline_steps"] = ";\n".join(timeline_code) + ";"

    # Generate code
    code = template.format(**variables)

    return code

def generate_imports(framework="vanilla"):
    """Generate import statements based on framework."""
    if framework == "vanilla":
        return '''import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

'''
    elif framework == "react":
        return '''import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

function Component() {
  const containerRef = useRef();

  useGSAP(() => {
    // Animation code goes here
'''
    elif framework == "vue":
        return '''import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { onMounted } from "vue";

gsap.registerPlugin(ScrollTrigger);

export default {
  setup() {
    onMounted(() => {
      // Animation code goes here
'''
    return ""

def generate_wrapper(code, framework="vanilla"):
    """Wrap code with framework-specific setup."""
    imports = generate_imports(framework)

    if framework == "vanilla":
        return f'''{imports}
// Wait for DOM
document.addEventListener("DOMContentLoaded", () => {{

{code}

  // Refresh after images load
  window.addEventListener("load", () => {{
    ScrollTrigger.refresh();
  }});

}});
'''
    elif framework == "react":
        return f'''{imports}
{code}

  }}, {{ scope: containerRef }});

  return <div ref={{containerRef}}>...</div>;
}}
'''
    elif framework == "vue":
        return f'''{imports}
{code}

      // Refresh after mount
      ScrollTrigger.refresh();
    }});
  }}
}};
'''
    return code

def main():
    parser = argparse.ArgumentParser(
        description="Generate GSAP animation boilerplate code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic fade in
  python3 generate_animation.py --type fade-in --trigger ".box"

  # Fade in with scrubbing
  python3 generate_animation.py --type fade-in-scrub --trigger ".hero" --markers

  # Pin section
  python3 generate_animation.py --type pin-section --trigger ".panel"

  # Horizontal scroll
  python3 generate_animation.py --type horizontal-scroll --trigger ".panel" --container ".container" --snap

  # Parallax
  python3 generate_animation.py --type parallax --trigger ".bg" --distance 200

  # Stagger animation
  python3 generate_animation.py --type stagger --trigger ".card" --stagger-from center --stagger-grid

  # Timeline with steps
  python3 generate_animation.py --type timeline --trigger ".sequence" --timeline-steps "fade,slide,scale"

  # Batch animation
  python3 generate_animation.py --type batch --trigger ".item" --once

  # Image sequence
  python3 generate_animation.py --type image-sequence --trigger ".canvas-section" --frame-count 148

  # Progress bar
  python3 generate_animation.py --type progress-bar --trigger ".progress"

  # Generate React component
  python3 generate_animation.py --type fade-in --trigger ".box" --framework react --output Component.jsx

Animation Types:
  fade-in, fade-in-scrub, pin-section, pin-with-animation, horizontal-scroll,
  parallax, stagger, timeline, batch, toggle-class, image-sequence,
  smooth-scroll-to, progress-bar
        """
    )

    parser.add_argument("--type", required=True, help="Animation type")
    parser.add_argument("--trigger", default=".element", help="Trigger element selector")
    parser.add_argument("--container", help="Container element selector")
    parser.add_argument("--canvas", help="Canvas selector for image sequences")
    parser.add_argument("--start", default="top 80%", help="ScrollTrigger start position")
    parser.add_argument("--end", default="bottom 20%", help="ScrollTrigger end position")
    parser.add_argument("--duration", type=float, help="Animation duration in seconds")
    parser.add_argument("--distance", type=int, help="Movement distance in pixels")
    parser.add_argument("--ease", help="Easing function (e.g., power2.out)")
    parser.add_argument("--scrub", type=float, help="Scrub value (true = 1, or number for lag)")
    parser.add_argument("--markers", action="store_true", help="Show debug markers")
    parser.add_argument("--pin-spacing", type=bool, default=True, help="Pin spacing for pinned sections")
    parser.add_argument("--snap", action="store_true", help="Enable snap points")
    parser.add_argument("--stagger-delay", type=float, default=0.1, help="Stagger delay between elements")
    parser.add_argument("--stagger-from", default="start", help="Stagger from (start, center, end, edges, random)")
    parser.add_argument("--stagger-grid", action="store_true", help="Enable grid stagger")
    parser.add_argument("--toggle-actions", default="play none none reverse", help="ScrollTrigger toggle actions")
    parser.add_argument("--once", action="store_true", help="Trigger animation only once")
    parser.add_argument("--class-name", help="Class name to toggle")
    parser.add_argument("--frame-count", type=int, help="Number of frames for image sequence")
    parser.add_argument("--image-path", help="Path to image sequence frames")
    parser.add_argument("--offset", type=int, help="Scroll offset in pixels")
    parser.add_argument("--timeline-steps", help="Comma-separated timeline steps (fade,slide,scale,rotate,color)")
    parser.add_argument("--preset", default="standard", choices=["subtle", "standard", "dramatic", "playful"], help="Animation preset")
    parser.add_argument("--framework", default="vanilla", choices=["vanilla", "react", "vue"], help="Framework wrapper")
    parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    # Generate animation code
    animation_code = generate_animation(args)

    # Wrap with framework setup
    full_code = generate_wrapper(animation_code, args.framework)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(full_code)
        print(f"✅ Generated animation code: {output_path}")
    else:
        print(full_code)

if __name__ == "__main__":
    main()

```


===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/scripts/timeline_builder.py =====

```py
#!/usr/bin/env python3
"""
GSAP Timeline Builder - Interactive

Interactive CLI tool to build complex GSAP timeline sequences step-by-step.
Helps visualize and generate timeline code with proper timing and positioning.

Usage:
    python3 timeline_builder.py
    python3 timeline_builder.py --output timeline.js
    python3 timeline_builder.py --load timeline.json --output code.js
"""

import argparse
import json
import sys
from pathlib import Path

class TimelineBuilder:
    """Interactive timeline builder."""

    def __init__(self):
        self.timeline_name = "tl"
        self.steps = []
        self.timeline_config = {
            "repeat": 0,
            "repeatDelay": 0,
            "yoyo": False,
            "paused": False,
            "scrollTrigger": None
        }
        self.labels = []

    def configure_timeline(self):
        """Configure timeline properties."""
        print("\n=== Timeline Configuration ===")

        name = input(f"Timeline variable name [{self.timeline_name}]: ").strip()
        if name:
            self.timeline_name = name

        repeat = input("Repeat count (0 = no repeat, -1 = infinite) [0]: ").strip()
        self.timeline_config["repeat"] = int(repeat) if repeat else 0

        if self.timeline_config["repeat"] != 0:
            repeat_delay = input("Repeat delay in seconds [0]: ").strip()
            self.timeline_config["repeatDelay"] = float(repeat_delay) if repeat_delay else 0

            yoyo = input("Yoyo (alternate direction)? (y/n) [n]: ").strip().lower()
            self.timeline_config["yoyo"] = yoyo == "y"

        paused = input("Start paused? (y/n) [n]: ").strip().lower()
        self.timeline_config["paused"] = paused == "y"

        scroll_trigger = input("Add ScrollTrigger? (y/n) [n]: ").strip().lower()
        if scroll_trigger == "y":
            self.configure_scroll_trigger()

    def configure_scroll_trigger(self):
        """Configure ScrollTrigger for timeline."""
        print("\n--- ScrollTrigger Configuration ---")

        trigger = input("Trigger element selector [.timeline-section]: ").strip()
        trigger = trigger or ".timeline-section"

        start = input("Start position [top 80%]: ").strip()
        start = start or "top 80%"

        end = input("End position (leave empty for auto): ").strip()

        scrub = input("Scrub? (y/n/number) [n]: ").strip().lower()
        if scrub == "y":
            scrub = True
        elif scrub == "n":
            scrub = None
        else:
            try:
                scrub = float(scrub)
            except:
                scrub = None

        pin = input("Pin element? (y/n) [n]: ").strip().lower()
        pin = pin == "y"

        markers = input("Show debug markers? (y/n) [n]: ").strip().lower()
        markers = markers == "y"

        self.timeline_config["scrollTrigger"] = {
            "trigger": trigger,
            "start": start,
            "end": end if end else None,
            "scrub": scrub,
            "pin": pin,
            "markers": markers
        }

    def add_step(self):
        """Add an animation step to the timeline."""
        print("\n=== Add Timeline Step ===")

        # Step type
        print("Animation type:")
        print("  1. to (animate TO values)")
        print("  2. from (animate FROM values)")
        print("  3. fromTo (define both start and end)")
        print("  4. set (instant, no animation)")
        print("  5. label (add timing label)")
        print("  6. call (callback function)")

        step_type = input("Choose type [1]: ").strip() or "1"

        if step_type == "5":
            return self.add_label()
        elif step_type == "6":
            return self.add_callback()

        # Target selector
        target = input("Target element selector (e.g., .box): ").strip()
        if not target:
            print("Error: Target is required")
            return

        # Properties
        print("\nAnimation properties (comma-separated):")
        print("  Examples: x, y, opacity, scale, rotation, backgroundColor")
        print("  Or type common presets: fade-in, slide-up, scale-up, rotate")

        props_input = input("Properties or preset: ").strip()
        props = self.parse_properties(props_input)

        # Duration
        duration = input("Duration in seconds [0.5]: ").strip()
        duration = float(duration) if duration else 0.5

        # Easing
        print("\nEasing (examples: power2.out, back.out(1.7), elastic.out)")
        ease = input("Easing [power2.out]: ").strip() or "power2.out"

        # Position parameter
        print("\nPosition in timeline:")
        print("  - Leave empty = append to end")
        print("  - Number (e.g., 2) = specific time")
        print("  - Relative (e.g., -=0.5) = 0.5s before previous ends")
        print("  - Relative (e.g., +=1) = 1s after previous ends")
        print("  - Label (e.g., midpoint) = at label position")

        position = input("Position: ").strip()

        step = {
            "type": self.get_method_name(step_type),
            "target": target,
            "properties": props,
            "duration": duration,
            "ease": ease,
            "position": position if position else None
        }

        # For fromTo, get initial values
        if step_type == "3":
            print("\nInitial values (FROM):")
            from_props = self.parse_properties(input("Properties: ").strip())
            step["from_properties"] = from_props

        self.steps.append(step)
        print(f"✅ Added: {step['type']}('{target}', ...)")

    def add_label(self):
        """Add a label to the timeline."""
        label_name = input("Label name: ").strip()
        if not label_name:
            print("Error: Label name is required")
            return

        position = input("Position (leave empty for current position): ").strip()

        self.labels.append({
            "name": label_name,
            "position": position if position else None
        })

        print(f"✅ Added label: '{label_name}'")

    def add_callback(self):
        """Add a callback to the timeline."""
        callback_name = input("Callback function name: ").strip()
        if not callback_name:
            print("Error: Callback name is required")
            return

        position = input("Position (leave empty for current position): ").strip()

        self.steps.append({
            "type": "call",
            "callback": callback_name,
            "position": position if position else None
        })

        print(f"✅ Added callback: {callback_name}()")

    def parse_properties(self, props_input):
        """Parse property input (preset or custom properties)."""
        presets = {
            "fade-in": {"opacity": 0},
            "fade-out": {"opacity": 0},
            "slide-up": {"y": 50, "opacity": 0},
            "slide-down": {"y": -50, "opacity": 0},
            "slide-left": {"x": 100, "opacity": 0},
            "slide-right": {"x": -100, "opacity": 0},
            "scale-up": {"scale": 0, "opacity": 0},
            "scale-down": {"scale": 1.5, "opacity": 0},
            "rotate": {"rotation": 360},
            "blur": {"filter": "blur(10px)"}
        }

        if props_input.lower() in presets:
            return presets[props_input.lower()]

        # Parse custom properties
        props = {}
        print("\nEnter property values (press Enter to skip):")

        prop_names = [p.strip() for p in props_input.split(",")]
        for prop_name in prop_names:
            value = input(f"  {prop_name}: ").strip()
            if value:
                # Try to convert to number
                try:
                    if "." in value:
                        props[prop_name] = float(value)
                    else:
                        props[prop_name] = int(value)
                except:
                    # Keep as string (for colors, etc.)
                    props[prop_name] = value

        return props

    def get_method_name(self, step_type):
        """Get GSAP method name from step type number."""
        methods = {
            "1": "to",
            "2": "from",
            "3": "fromTo",
            "4": "set"
        }
        return methods.get(step_type, "to")

    def visualize_timeline(self):
        """Visualize timeline structure."""
        if not self.steps:
            print("\n⚠️  Timeline is empty")
            return

        print("\n=== Timeline Visualization ===")
        print(f"Timeline: {self.timeline_name}")
        print(f"Steps: {len(self.steps)}")
        print(f"Labels: {len(self.labels)}")
        print()

        for i, step in enumerate(self.steps):
            if step["type"] == "call":
                position = step.get("position", "")
                print(f"  {i+1}. {step['type']}({step['callback']}){' at ' + position if position else ''}")
            else:
                target = step["target"]
                props = ", ".join(f"{k}={v}" for k, v in step["properties"].items())
                duration = step.get("duration", "")
                ease = step.get("ease", "")
                position = step.get("position", "")

                timing = f"{duration}s, {ease}" if duration and ease else ""
                pos_str = f" at {position}" if position else ""

                print(f"  {i+1}. {step['type']}('{target}', {{ {props} }}) [{timing}]{pos_str}")

        if self.labels:
            print("\nLabels:")
            for label in self.labels:
                pos = f" at {label['position']}" if label.get("position") else ""
                print(f"  - {label['name']}{pos}")

    def generate_code(self):
        """Generate GSAP timeline code."""
        lines = []

        # Imports
        lines.append('import gsap from "gsap";')

        if self.timeline_config.get("scrollTrigger"):
            lines.append('import { ScrollTrigger } from "gsap/ScrollTrigger";')
            lines.append('')
            lines.append('gsap.registerPlugin(ScrollTrigger);')

        lines.append('')

        # Timeline configuration
        config_parts = []

        if self.timeline_config["repeat"] != 0:
            config_parts.append(f'repeat: {self.timeline_config["repeat"]}')

            if self.timeline_config["repeatDelay"] > 0:
                config_parts.append(f'repeatDelay: {self.timeline_config["repeatDelay"]}')

            if self.timeline_config["yoyo"]:
                config_parts.append('yoyo: true')

        if self.timeline_config["paused"]:
            config_parts.append('paused: true')

        if self.timeline_config.get("scrollTrigger"):
            st = self.timeline_config["scrollTrigger"]
            st_parts = [f'trigger: "{st["trigger"]}"', f'start: "{st["start"]}"']

            if st.get("end"):
                st_parts.append(f'end: "{st["end"]}"')

            if st.get("scrub") is not None:
                if isinstance(st["scrub"], bool):
                    st_parts.append('scrub: true')
                else:
                    st_parts.append(f'scrub: {st["scrub"]}')

            if st.get("pin"):
                st_parts.append('pin: true')

            if st.get("markers"):
                st_parts.append('markers: true')

            st_config = ",\n    ".join(st_parts)
            config_parts.append(f'scrollTrigger: {{\n    {st_config}\n  }}')

        if config_parts:
            config_str = ",\n  ".join(config_parts)
            lines.append(f'const {self.timeline_name} = gsap.timeline({{')
            lines.append(f'  {config_str}')
            lines.append('});')
        else:
            lines.append(f'const {self.timeline_name} = gsap.timeline();')

        lines.append('')

        # Add steps
        for i, step in enumerate(self.steps):
            if step["type"] == "call":
                position = f', "{step["position"]}"' if step.get("position") else ""
                lines.append(f'{self.timeline_name}.call({step["callback"]}{position});')
                continue

            # Properties
            props_str = self.format_properties(step["properties"])

            # Build method call
            if step["type"] == "fromTo":
                from_props = self.format_properties(step["from_properties"])
                to_props = props_str.replace(f', duration: {step["duration"]}', "")
                to_props += f', duration: {step["duration"]}, ease: "{step["ease"]}"'

                position = f', "{step["position"]}"' if step.get("position") else ""
                lines.append(f'{self.timeline_name}.fromTo("{step["target"]}", {{ {from_props} }}, {{ {to_props} }}{position});')
            else:
                # Add duration and ease for animated methods
                if step["type"] != "set":
                    props_str += f', duration: {step["duration"]}, ease: "{step["ease"]}"'

                position = f', "{step["position"]}"' if step.get("position") else ""
                lines.append(f'{self.timeline_name}.{step["type"]}("{step["target"]}", {{ {props_str} }}{position});')

            # Add label if this step has one
            for label in self.labels:
                if label.get("after_step") == i:
                    lines.append(f'{self.timeline_name}.addLabel("{label["name"]}");')

        # Add labels at end
        for label in self.labels:
            if not label.get("after_step") and not label.get("position"):
                lines.append(f'{self.timeline_name}.addLabel("{label["name"]}");')

        return "\n".join(lines)

    def format_properties(self, props):
        """Format properties object for code generation."""
        parts = []
        for key, value in props.items():
            if isinstance(value, str):
                parts.append(f'{key}: "{value}"')
            else:
                parts.append(f'{key}: {value}')
        return ", ".join(parts)

    def save_timeline(self, filepath):
        """Save timeline configuration to JSON."""
        data = {
            "timeline_name": self.timeline_name,
            "config": self.timeline_config,
            "steps": self.steps,
            "labels": self.labels
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Timeline saved: {filepath}")

    def load_timeline(self, filepath):
        """Load timeline configuration from JSON."""
        with open(filepath, "r") as f:
            data = json.load(f)

        self.timeline_name = data.get("timeline_name", "tl")
        self.timeline_config = data.get("config", {})
        self.steps = data.get("steps", [])
        self.labels = data.get("labels", [])

        print(f"✅ Timeline loaded: {filepath}")

    def interactive_mode(self):
        """Run interactive timeline builder."""
        print("╔════════════════════════════════════════════════╗")
        print("║   GSAP Timeline Builder - Interactive Mode    ║")
        print("╚════════════════════════════════════════════════╝")

        self.configure_timeline()

        while True:
            print("\n" + "="*50)
            print("Options:")
            print("  1. Add animation step")
            print("  2. Add label")
            print("  3. Add callback")
            print("  4. Visualize timeline")
            print("  5. Generate code")
            print("  6. Save timeline (JSON)")
            print("  7. Configure timeline settings")
            print("  8. Exit")

            choice = input("\nChoose option: ").strip()

            if choice == "1":
                self.add_step()
            elif choice == "2":
                self.add_label()
            elif choice == "3":
                self.add_callback()
            elif choice == "4":
                self.visualize_timeline()
            elif choice == "5":
                code = self.generate_code()
                print("\n" + "="*50)
                print("Generated Code:")
                print("="*50)
                print(code)
                print("="*50)

                save = input("\nSave to file? (y/n): ").strip().lower()
                if save == "y":
                    filename = input("Filename [timeline.js]: ").strip() or "timeline.js"
                    Path(filename).write_text(code)
                    print(f"✅ Code saved: {filename}")
            elif choice == "6":
                filename = input("Filename [timeline.json]: ").strip() or "timeline.json"
                self.save_timeline(filename)
            elif choice == "7":
                self.configure_timeline()
            elif choice == "8":
                print("\n👋 Goodbye!")
                break
            else:
                print("⚠️  Invalid option")

def main():
    parser = argparse.ArgumentParser(
        description="Interactive GSAP Timeline Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python3 timeline_builder.py

  # Load existing timeline and generate code
  python3 timeline_builder.py --load timeline.json --output code.js

  # Save generated code to file
  python3 timeline_builder.py --output timeline.js

Workflow:
  1. Configure timeline (repeat, yoyo, ScrollTrigger)
  2. Add animation steps (to, from, fromTo, set)
  3. Add labels for complex timing
  4. Visualize timeline structure
  5. Generate and export code
        """
    )

    parser.add_argument("--load", "-l", help="Load timeline from JSON file")
    parser.add_argument("--output", "-o", help="Output file for generated code")

    args = parser.parse_args()

    builder = TimelineBuilder()

    # Load existing timeline if provided
    if args.load:
        try:
            builder.load_timeline(args.load)

            if args.output:
                # Generate and save code
                code = builder.generate_code()
                Path(args.output).write_text(code)
                print(f"✅ Generated code saved: {args.output}")
                return
        except FileNotFoundError:
            print(f"Error: File not found: {args.load}")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON file: {args.load}")
            sys.exit(1)

    # Run interactive mode
    builder.interactive_mode()

    # Save code if output specified
    if args.output and builder.steps:
        code = builder.generate_code()
        Path(args.output).write_text(code)
        print(f"\n✅ Final code saved: {args.output}")

if __name__ == "__main__":
    main()

```


===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/assets/easings/easing_visualizer.html =====

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GSAP Easing Visualizer</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 40px 20px;
      color: #333;
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
    }

    header {
      text-align: center;
      margin-bottom: 40px;
      color: white;
    }

    h1 {
      font-size: 3rem;
      margin-bottom: 10px;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    .subtitle {
      font-size: 1.2rem;
      opacity: 0.9;
    }

    .controls {
      background: white;
      padding: 30px;
      border-radius: 15px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.2);
      margin-bottom: 40px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
    }

    .control-group {
      display: flex;
      flex-direction: column;
    }

    label {
      font-weight: 600;
      margin-bottom: 8px;
      color: #555;
    }

    input, select, button {
      padding: 12px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      font-size: 1rem;
      font-family: inherit;
      transition: border-color 0.3s;
    }

    input:focus, select:focus {
      outline: none;
      border-color: #667eea;
    }

    button {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      cursor: pointer;
      font-weight: 600;
      transition: transform 0.2s, box-shadow 0.2s;
    }

    button:hover {
      transform: translateY(-2px);
      box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }

    button:active {
      transform: translateY(0);
    }

    .easing-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 30px;
      margin-bottom: 40px;
    }

    .easing-card {
      background: white;
      padding: 25px;
      border-radius: 15px;
      box-shadow: 0 5px 20px rgba(0,0,0,0.15);
      transition: transform 0.3s, box-shadow 0.3s;
    }

    .easing-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }

    .easing-name {
      font-size: 1.2rem;
      font-weight: 600;
      margin-bottom: 15px;
      color: #764ba2;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .copy-btn {
      padding: 5px 10px;
      font-size: 0.8rem;
      background: #f0f0f0;
      color: #333;
      border: 1px solid #ddd;
      cursor: pointer;
      transition: background 0.2s;
    }

    .copy-btn:hover {
      background: #e0e0e0;
    }

    .track {
      width: 100%;
      height: 60px;
      background: #f5f5f5;
      border-radius: 10px;
      margin-bottom: 15px;
      position: relative;
      overflow: hidden;
      box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
    }

    .box {
      width: 50px;
      height: 50px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 8px;
      position: absolute;
      left: 5px;
      top: 5px;
      box-shadow: 0 3px 10px rgba(0,0,0,0.2);
    }

    .curve-preview {
      width: 100%;
      height: 80px;
      background: #fafafa;
      border-radius: 8px;
      position: relative;
      border: 2px solid #e0e0e0;
    }

    .curve-line {
      stroke: #764ba2;
      stroke-width: 3;
      fill: none;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }

    .use-case {
      margin-top: 15px;
      padding: 12px;
      background: #f9f9f9;
      border-radius: 8px;
      font-size: 0.9rem;
      color: #666;
      border-left: 4px solid #667eea;
    }

    .action-bar {
      text-align: center;
      margin-bottom: 30px;
    }

    .action-bar button {
      margin: 0 10px;
      padding: 15px 30px;
      font-size: 1.1rem;
    }

    .comparison-mode {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-top: 30px;
    }

    .comparison-card {
      background: white;
      padding: 20px;
      border-radius: 12px;
      box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }

    @media (max-width: 768px) {
      h1 {
        font-size: 2rem;
      }

      .controls {
        grid-template-columns: 1fr;
      }

      .easing-grid {
        grid-template-columns: 1fr;
      }
    }

    .copied-toast {
      position: fixed;
      bottom: 30px;
      right: 30px;
      background: #4caf50;
      color: white;
      padding: 15px 25px;
      border-radius: 8px;
      box-shadow: 0 5px 20px rgba(0,0,0,0.3);
      opacity: 0;
      transform: translateY(20px);
      transition: opacity 0.3s, transform 0.3s;
      pointer-events: none;
      z-index: 1000;
    }

    .copied-toast.show {
      opacity: 1;
      transform: translateY(0);
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>⚡ GSAP Easing Visualizer</h1>
      <p class="subtitle">Explore and compare GSAP easing functions</p>
    </header>

    <div class="controls">
      <div class="control-group">
        <label for="duration">Duration (seconds)</label>
        <input type="number" id="duration" value="1.5" step="0.1" min="0.1" max="5">
      </div>

      <div class="control-group">
        <label for="distance">Distance (pixels)</label>
        <input type="number" id="distance" value="280" step="10" min="50" max="500">
      </div>

      <div class="control-group">
        <label for="category">Category Filter</label>
        <select id="category">
          <option value="all">All Easings</option>
          <option value="power">Power (Most Common)</option>
          <option value="special">Special (Back, Elastic, Bounce)</option>
          <option value="other">Other (Circ, Expo, Sine)</option>
        </select>
      </div>

      <div class="control-group">
        <button id="play-all">▶ Play All</button>
      </div>
    </div>

    <div class="action-bar">
      <button id="reset-all">↻ Reset All</button>
      <button id="toggle-curves">📊 Toggle Curves</button>
    </div>

    <div id="easing-container" class="easing-grid"></div>

    <div class="copied-toast" id="toast">Copied to clipboard!</div>
  </div>

  <script>
    // Easing functions with metadata
    const easings = [
      // Power easings
      { name: "none", category: "power", useCase: "Constant speed, scroll-driven animations" },
      { name: "power1.out", category: "power", useCase: "Subtle UI transitions, tooltips" },
      { name: "power2.out", category: "power", useCase: "⭐ Default choice for most animations" },
      { name: "power3.out", category: "power", useCase: "Hero sections, dramatic reveals" },
      { name: "power4.out", category: "power", useCase: "Full-screen transitions, maximum impact" },
      { name: "power1.in", category: "power", useCase: "Rare: elements accelerating off-screen" },
      { name: "power2.in", category: "power", useCase: "Rare: strong acceleration" },
      { name: "power1.inOut", category: "power", useCase: "Smooth start and end" },
      { name: "power2.inOut", category: "power", useCase: "Balanced animation both ends" },
      { name: "power3.inOut", category: "power", useCase: "Strong smooth both ends" },

      // Special easings
      { name: "back.out(1.7)", category: "special", useCase: "Playful buttons, fun micro-interactions" },
      { name: "back.out(2.5)", category: "special", useCase: "Exaggerated overshoot" },
      { name: "back.in(1.7)", category: "special", useCase: "Element backs up before leaving" },
      { name: "back.inOut(1.7)", category: "special", useCase: "Overshoot both ends" },
      { name: "elastic.out(1, 0.3)", category: "special", useCase: "Spring effect, notification badges" },
      { name: "elastic.in(1, 0.3)", category: "special", useCase: "Rare: elastic entrance" },
      { name: "bounce.out", category: "special", useCase: "Elements dropping into place" },
      { name: "bounce.in", category: "special", useCase: "Bouncing ball entering" },

      // Other easings
      { name: "circ.out", category: "other", useCase: "Fast snappy movements, Material Design" },
      { name: "circ.in", category: "other", useCase: "Sharp acceleration" },
      { name: "circ.inOut", category: "other", useCase: "Sharp both ends" },
      { name: "expo.out", category: "other", useCase: "Dramatic zoom effects, cinematic" },
      { name: "expo.in", category: "other", useCase: "Extremely slow start" },
      { name: "expo.inOut", category: "other", useCase: "Intense page transitions" },
      { name: "sine.out", category: "other", useCase: "Subtle parallax, ambient effects" },
      { name: "sine.in", category: "other", useCase: "Very gentle acceleration" },
      { name: "sine.inOut", category: "other", useCase: "Barely noticeable animations" },
    ];

    let duration = 1.5;
    let distance = 280;
    let showCurves = true;

    const container = document.getElementById('easing-container');
    const durationInput = document.getElementById('duration');
    const distanceInput = document.getElementById('distance');
    const categorySelect = document.getElementById('category');
    const playAllBtn = document.getElementById('play-all');
    const resetAllBtn = document.getElementById('reset-all');
    const toggleCurvesBtn = document.getElementById('toggle-curves');
    const toast = document.getElementById('toast');

    // Generate easing cards
    function renderEasings() {
      const category = categorySelect.value;
      const filtered = easings.filter(e =>
        category === 'all' || e.category === category
      );

      container.innerHTML = '';

      filtered.forEach((easing, index) => {
        const card = document.createElement('div');
        card.className = 'easing-card';
        card.innerHTML = `
          <div class="easing-name">
            <span>${easing.name}</span>
            <button class="copy-btn" data-ease="${easing.name}">Copy</button>
          </div>
          <div class="track" data-index="${index}">
            <div class="box"></div>
          </div>
          <div class="curve-preview" style="${showCurves ? '' : 'display: none;'}">
            <svg width="100%" height="100%" viewBox="0 0 100 80" preserveAspectRatio="none">
              <path class="curve-line" d="M 5 75 ${generateCurvePath(easing.name)}" />
            </svg>
          </div>
          <div class="use-case">
            <strong>Use case:</strong> ${easing.useCase}
          </div>
        `;

        container.appendChild(card);

        // Add copy functionality
        card.querySelector('.copy-btn').addEventListener('click', () => {
          copyToClipboard(easing.name);
        });

        // Add click to animate
        card.querySelector('.track').addEventListener('click', () => {
          animateBox(index, easing.name);
        });
      });
    }

    // Generate approximate curve path for visualization
    function generateCurvePath(easeName) {
      // Simplified curve representations
      const curves = {
        "none": "L 95 5",
        "power1.out": "Q 50 40, 95 5",
        "power2.out": "Q 50 50, 95 5",
        "power3.out": "Q 50 60, 95 5",
        "power4.out": "Q 50 65, 95 5",
        "power1.in": "Q 50 40, 95 75",
        "power2.in": "Q 50 30, 95 75",
        "back.out(1.7)": "Q 50 -10, 95 5",
        "back.out(2.5)": "Q 50 -20, 95 5",
        "back.in(1.7)": "Q 50 90, 95 75",
        "back.inOut(1.7)": "Q 25 -10, 50 40 T 95 5",
        "elastic.out(1, 0.3)": "Q 30 -5, 50 45 T 70 5 T 95 5",
        "bounce.out": "L 40 30 L 60 10 L 75 5 L 95 5",
        "circ.out": "Q 30 50, 95 5",
        "expo.out": "Q 20 60, 95 5",
        "sine.out": "Q 50 35, 95 5",
      };

      return curves[easeName] || "L 95 5";
    }

    // Animate individual box
    function animateBox(index, easeName) {
      const track = document.querySelector(`.track[data-index="${index}"]`);
      const box = track.querySelector('.box');

      gsap.fromTo(box,
        { x: 0 },
        {
          x: distance,
          duration: duration,
          ease: easeName,
          onComplete: () => {
            gsap.to(box, { x: 0, duration: 0.3, ease: "power1.in" });
          }
        }
      );
    }

    // Play all animations
    function playAll() {
      const tracks = document.querySelectorAll('.track');
      tracks.forEach((track, index) => {
        const box = track.querySelector('.box');
        const easeName = easings[index].name;

        gsap.fromTo(box,
          { x: 0 },
          {
            x: distance,
            duration: duration,
            ease: easeName,
            delay: index * 0.05,
            onComplete: () => {
              gsap.to(box, { x: 0, duration: 0.3, ease: "power1.in" });
            }
          }
        );
      });
    }

    // Reset all animations
    function resetAll() {
      const boxes = document.querySelectorAll('.box');
      gsap.killTweensOf(boxes);
      gsap.set(boxes, { x: 0 });
    }

    // Copy to clipboard
    function copyToClipboard(text) {
      navigator.clipboard.writeText(`ease: "${text}"`).then(() => {
        showToast();
      });
    }

    function showToast() {
      toast.classList.add('show');
      setTimeout(() => {
        toast.classList.remove('show');
      }, 2000);
    }

    // Event listeners
    durationInput.addEventListener('input', (e) => {
      duration = parseFloat(e.target.value);
    });

    distanceInput.addEventListener('input', (e) => {
      distance = parseInt(e.target.value);
    });

    categorySelect.addEventListener('change', renderEasings);

    playAllBtn.addEventListener('click', playAll);
    resetAllBtn.addEventListener('click', resetAll);

    toggleCurvesBtn.addEventListener('click', () => {
      showCurves = !showCurves;
      renderEasings();
    });

    // Initial render
    renderEasings();
  </script>
</body>
</html>

```


===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/assets/examples/README.md =====

# GSAP ScrollTrigger Examples

Real-world patterns and implementations for common ScrollTrigger use cases.

## 📚 Available Examples

### Core Patterns

All examples are self-contained HTML files demonstrating specific ScrollTrigger patterns. Open any file directly in your browser to see the demo.

---

## 🎯 Pattern Categories

### 1. Fade & Entrance Animations

**Use Cases**: Content reveals, card grids, feature sections

```javascript
// Basic fade in
gsap.from(".element", {
  opacity: 0,
  y: 50,
  scrollTrigger: {
    trigger: ".element",
    start: "top 80%"
  }
});
```

**Variations**:
- Batch animations for multiple elements
- Stagger from different directions (center, edges, random)
- Grid-based stagger patterns

---

### 2. Pinning Animations

**Use Cases**: Storytelling, feature highlights, step-by-step guides

```javascript
ScrollTrigger.create({
  trigger: ".section",
  start: "top top",
  end: "+=1000",
  pin: true,
  scrub: 1
});
```

**Variations**:
- Pin with timeline animations
- Multiple pinned sections (stacked cards)
- Pin with snap points

---

### 3. Horizontal Scrolling

**Use Cases**: Portfolios, product showcases, timelines

```javascript
gsap.to(".panels", {
  xPercent: -100 * (panels.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".container",
    pin: true,
    scrub: 1,
    end: () => "+=" + container.offsetWidth
  }
});
```

**Variations**:
- With snap points between panels
- Nested animations within panels
- Progress indicators

---

### 4. Parallax Effects

**Use Cases**: Hero sections, immersive storytelling, depth perception

```javascript
gsap.to(".bg", {
  y: 200,
  ease: "none",
  scrollTrigger: {
    trigger: ".section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});
```

**Variations**:
- Multi-layer parallax (2-5 layers)
- Parallax with zoom
- Directional parallax (horizontal/vertical)

---

### 5. Text Animations

**Use Cases**: Headlines, storytelling, attention-grabbing reveals

```javascript
// Requires SplitText plugin (Club GreenSock)
const split = new SplitText(".text", { type: "lines" });

gsap.from(split.lines, {
  opacity: 0,
  y: 20,
  stagger: 0.1,
  scrollTrigger: {
    trigger: ".text",
    start: "top 80%"
  }
});
```

**Variations**:
- Line-by-line reveals
- Character animations
- Typewriter effects
- Text masking

---

### 6. Image Reveals

**Use Cases**: Galleries, case studies, portfolio pieces

```javascript
// Curtain reveal
gsap.to(".curtain", {
  xPercent: 100,
  duration: 1,
  scrollTrigger: {
    trigger: ".image",
    start: "top 80%"
  }
});
```

**Variations**:
- Clip-path reveals
- Scale reveals
- Directional wipes
- Parallax zoom

---

## 🚀 Quick Start

### Run Any Example

1. Open any `.html` file in your browser
2. Or serve with a local server:

```bash
python -m http.server 8000
# Navigate to http://localhost:8000/pin_animation.html
```

### Integrate into Your Project

Each example is self-contained. Copy the relevant code sections:

1. **HTML Structure** - Copy the markup
2. **CSS Styles** - Copy relevant styles
3. **JavaScript** - Copy animation code, adjust selectors

---

## 📖 Learning Path

### Beginner

1. Study basic fade-in patterns
2. Experiment with stagger animations
3. Try different easing functions
4. Enable debug markers to visualize triggers

### Intermediate

1. Build pinned sections with timelines
2. Create parallax effects
3. Implement horizontal scrolling
4. Add scroll progress indicators

### Advanced

1. Create image sequence animations
2. Build complex multi-section experiences
3. Integrate with Three.js or Canvas
4. Implement custom ScrollTrigger behaviors

---

## 💡 Best Practices

### Performance

1. Use `transform` and `opacity` (GPU-accelerated)
2. Apply `will-change` to animated elements
3. Use `scrub` for smooth scroll-driven animations
4. Limit number of active ScrollTriggers

### UX

1. Keep animations subtle and purposeful
2. Test on multiple devices and screen sizes
3. Provide fallbacks for users with motion sensitivity
4. Ensure content is accessible without animations

### Development

1. Enable debug markers during development
2. Use meaningful trigger/element names
3. Comment complex animation sequences
4. Test scroll performance with DevTools

---

## 🔗 Additional Resources

### Official GSAP Resources

- [ScrollTrigger Docs](https://gsap.com/docs/v3/Plugins/ScrollTrigger)
- [GSAP Showcase](https://gsap.com/showcase/)
- [CodePen Examples](https://codepen.io/GreenSock/pens/popular)
- [GSAP Forums](https://gsap.com/community/)

### Included in This Package

- `../references/api_reference.md` - Complete GSAP & ScrollTrigger API
- `../references/easing_guide.md` - Visual easing reference
- `../references/common_patterns.md` - Copy-paste pattern library
- `../easings/easing_visualizer.html` - Interactive easing tool
- `../starter_scroll/` - Complete website template

---

## 🎨 Customization Tips

### Adjust Timing

```javascript
// Slower animation
duration: 2  // instead of 1

// More gradual scroll response
scrub: 2  // instead of true or 1
```

### Change Trigger Points

```javascript
// Trigger earlier
start: "top 90%"  // instead of "top 80%"

// Trigger later
start: "top 50%"
```

### Modify Easing

```javascript
// More dramatic
ease: "power3.out"  // instead of "power2.out"

// Playful
ease: "back.out(1.7)"
```

---

## 🐛 Common Issues

### Animation Not Triggering

- Check element selectors
- Enable debug markers: `markers: true`
- Verify trigger element exists in DOM
- Check browser console for errors

### Jumpy Animations

- Use `scrub` for smooth scroll-tied animations
- Add `anticipatePin: 1` for pinned sections
- Check for layout shifts (images without dimensions)

### Poor Performance

- Reduce number of animated elements
- Use `ScrollTrigger.batch()` for many elements
- Avoid animating expensive properties (width, height)
- Test on target devices

---

## 📱 Mobile Considerations

```javascript
// Disable complex animations on mobile
if (window.innerWidth < 768) {
  // Use simpler animations or CSS-only
}

// Or use ScrollTrigger.matchMedia()
ScrollTrigger.matchMedia({
  "(min-width: 800px)": function() {
    // Desktop animations
  },
  "(max-width: 799px)": function() {
    // Mobile animations
  }
});
```

---

## 🎯 Example Use Cases

### E-commerce

- Product reveals on scroll
- Feature highlights with pinning
- Parallax hero sections
- Image galleries with stagger

### Portfolios

- Horizontal project showcases
- Case study storytelling with pins
- Image sequence animations
- Smooth page transitions

### Marketing Sites

- Feature sections with animations
- Testimonial sliders
- Pricing table reveals
- CTA animations

### Storytelling

- Chapter-based pinned sections
- Text reveals for narrative
- Image sequences for progression
- Parallax depth for immersion

---

## 📝 Code Snippets

### Quick Copy-Paste Examples

#### Fade In on Scroll

```html
<div class="fade-in">Content here</div>

<script>
gsap.from(".fade-in", {
  opacity: 0,
  y: 50,
  duration: 1,
  scrollTrigger: {
    trigger: ".fade-in",
    start: "top 80%"
  }
});
</script>
```

#### Progress Bar

```html
<div class="progress" style="position: fixed; top: 0; left: 0; height: 4px; background: blue; transform-origin: left;"></div>

<script>
gsap.to(".progress", {
  scaleX: 1,
  ease: "none",
  scrollTrigger: {
    start: "top top",
    end: "bottom bottom",
    scrub: 0.3
  }
});
</script>
```

#### Smooth Scroll Navigation

```html
<a href="#section2">Go to Section 2</a>

<script>
gsap.registerPlugin(ScrollToPlugin);

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", function(e) {
    e.preventDefault();
    gsap.to(window, {
      duration: 1,
      scrollTo: this.getAttribute("href"),
      ease: "power2.inOut"
    });
  });
});
</script>
```

---

## 🎓 Next Steps

1. **Explore** - Open examples and study the code
2. **Modify** - Change values and see what happens
3. **Combine** - Mix patterns to create unique effects
4. **Build** - Create your own scroll-driven experience

---

**Need Help?**

- Check the [API Reference](../references/api_reference.md)
- Try the [Easing Visualizer](../easings/easing_visualizer.html)
- Browse [Common Patterns](../references/common_patterns.md)
- Visit [GSAP Forums](https://gsap.com/community/)

---

**Happy Scrolling!** 🎉



===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/assets/starter_scroll/README.md =====

# GSAP ScrollTrigger Starter Template

A production-ready, scroll-driven website template featuring modern GSAP & ScrollTrigger animations.

## ✨ Features

### Animations Included

- ✅ **Hero Section** - Parallax background with fade-out content
- ✅ **Fade-in Cards** - Staggered entrance animations
- ✅ **Parallax Section** - Multi-layer depth effect
- ✅ **Pin Section** - Content pinned while animations play
- ✅ **Stagger Gallery** - Grid animation from center
- ✅ **Horizontal Scroll** - Vertical scroll triggering horizontal movement
- ✅ **Text Reveal** - Line-by-line text animations
- ✅ **Progress Bar** - Scroll progress indicator
- ✅ **Smart Navigation** - Hide on scroll down, show on scroll up
- ✅ **Active Nav Tracking** - Highlights current section
- ✅ **Smooth Scroll** - Click anchors for smooth navigation
- ✅ **Responsive** - Mobile-optimized animations
- ✅ **Loading Screen** - Smooth intro animation

### Technical Features

- 🚀 **Performance Optimized** - GPU-accelerated animations, will-change optimization
- 📱 **Mobile Responsive** - Adapts animations for smaller screens
- 🎨 **Modern Design** - Clean, gradient-based aesthetic
- ⚡ **Zero Dependencies** - Only GSAP required (via CDN)
- 🛠 **Easy Customization** - Well-organized, commented code
- 📦 **Production Ready** - Tested and optimized for real-world use

---

## 🚀 Quick Start

### Option 1: Local Development

```bash
# Serve with any static server
python -m http.server 8000
# Or
npx serve
# Or
php -S localhost:8000
```

Open `http://localhost:8000` in your browser.

### Option 2: Direct Open

Simply open `index.html` in your browser (some animations may require a server for full functionality).

---

## 📁 Project Structure

```
starter_scroll/
├── index.html    # Main HTML structure
├── style.css     # Complete styles (~580 lines)
├── main.js       # GSAP animations (~420 lines)
└── README.md     # This file
```

---

## 🎨 Customization Guide

### 1. Change Colors

Edit CSS variables in `style.css`:

```css
:root {
  --primary: #667eea;      /* Primary gradient color */
  --secondary: #764ba2;    /* Secondary gradient color */
  --text-dark: #333;       /* Main text color */
  --text-light: #666;      /* Secondary text color */
  --bg-light: #f9f9f9;     /* Light background */
}
```

### 2. Adjust Animation Timing

In `main.js`, modify animation durations and easing:

```javascript
// Example: Hero animation
tl.from(".hero-title", {
  opacity: 0,
  y: 100,
  duration: 1,        // Change duration
  ease: "power3.out"  // Change easing
});
```

**Common Easing Options**:
- `power2.out` - Standard (most common)
- `power3.out` - Dramatic
- `back.out(1.7)` - Playful overshoot
- `elastic.out` - Bouncy
- `none` - Linear (for scrubbed animations)

### 3. Modify Scroll Trigger Points

Adjust `start` and `end` positions:

```javascript
scrollTrigger: {
  trigger: ".section",
  start: "top 80%",      // When top of section hits 80% of viewport
  end: "bottom 20%",     // When bottom hits 20% of viewport
  scrub: true            // Tie animation to scroll
}
```

**Position Format**: `"[trigger position] [viewport position]"`
- Examples: `"top top"`, `"center center"`, `"bottom 80%"`

### 4. Enable Debug Markers

In `main.js`, set `DEBUG = true`:

```javascript
const DEBUG = true;  // Shows visual scroll trigger markers
```

This displays colored markers showing trigger start/end points.

### 5. Add Your Own Sections

**HTML**:
```html
<section class="section my-section">
  <div class="container">
    <h2 class="section-title">My Section</h2>
    <p class="fade-in">Content here...</p>
  </div>
</section>
```

**JavaScript**:
```javascript
gsap.from(".my-section .fade-in", {
  opacity: 0,
  y: 50,
  duration: 1,
  scrollTrigger: {
    trigger: ".my-section",
    start: "top 80%"
  }
});
```

---

## 🎯 Animation Patterns Reference

### Fade In on Scroll

```javascript
gsap.from(".element", {
  opacity: 0,
  y: 50,
  duration: 1,
  scrollTrigger: {
    trigger: ".element",
    start: "top 80%"
  }
});
```

### Scroll-Driven Animation (Scrubbed)

```javascript
gsap.to(".element", {
  x: 500,
  scrollTrigger: {
    trigger: ".container",
    start: "top top",
    end: "bottom top",
    scrub: true  // Animation tied to scroll position
  }
});
```

### Pin Section

```javascript
ScrollTrigger.create({
  trigger: ".section",
  start: "top top",
  end: "+=1000",  // Pin for 1000px of scrolling
  pin: true,
  pinSpacing: true
});
```

### Stagger Animation

```javascript
gsap.from(".item", {
  opacity: 0,
  y: 50,
  stagger: 0.15,  // 0.15s delay between each
  scrollTrigger: {
    trigger: ".container",
    start: "top 80%"
  }
});
```

### Parallax Effect

```javascript
gsap.to(".bg", {
  y: 200,
  ease: "none",
  scrollTrigger: {
    trigger: ".section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});
```

---

## 📱 Responsive Behavior

Animations automatically adapt for mobile devices:

- Reduced animation complexity on `< 768px` screens
- `limitCallbacks` enabled for better mobile performance
- Navigation adapts to touch interactions
- Horizontal scroll becomes vertical scroll on mobile

**Manual Responsive Control**:

```javascript
ScrollTrigger.matchMedia({
  // Desktop
  "(min-width: 800px)": function() {
    // Desktop-only animations
  },

  // Mobile
  "(max-width: 799px)": function() {
    // Mobile-only animations
  }
});
```

---

## ⚡ Performance Tips

### Already Implemented

1. **GPU Acceleration** - Using `transform` and `opacity` (GPU-friendly properties)
2. **Will-change** - Applied to animated elements
3. **Efficient Selectors** - Cached element queries
4. **Debounced Resize** - Prevents excessive refresh calls
5. **Mobile Optimization** - Simplified animations on small screens

### Additional Optimizations

1. **Reduce Animation Count**

```javascript
// Instead of animating many elements
gsap.from(".item", { ... });

// Use batch for better performance
ScrollTrigger.batch(".item", {
  onEnter: batch => gsap.from(batch, { ... })
});
```

2. **Lower Scrub Precision**

```javascript
scrollTrigger: {
  scrub: 1  // Instead of true (smoother but less precise)
}
```

3. **Disable Markers in Production**

```javascript
const DEBUG = false;  // Removes visual markers
```

---

## 🐛 Troubleshooting

### Animations Not Triggering

1. Check console for errors
2. Enable debug markers: `DEBUG = true`
3. Verify element selectors match HTML
4. Ensure content is loaded: animations run after `window.load`

### Jumpy Scroll on Mobile

```javascript
// Add to ScrollTrigger config
ScrollTrigger.config({
  ignoreMobileResize: true
});
```

### Layout Shifts After Pin

```javascript
ScrollTrigger.create({
  pin: true,
  pinSpacing: true  // or false, depending on desired behavior
});
```

### Horizontal Scroll Issues

1. Check container width calculation
2. Verify number of panels
3. Test on different screen sizes

---

## 🔧 Advanced Customization

### Add Timeline Sequences

```javascript
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".section",
    start: "top 80%"
  }
});

tl.from(".title", { opacity: 0, y: -50 })
  .from(".subtitle", { opacity: 0, y: -30 }, "-=0.3")
  .from(".button", { scale: 0 }, "-=0.2");
```

### Callback Functions

```javascript
scrollTrigger: {
  trigger: ".section",
  start: "top 80%",
  onEnter: () => console.log("Entered"),
  onLeave: () => console.log("Left"),
  onEnterBack: () => console.log("Scrolled back"),
  onLeaveBack: () => console.log("Left backwards")
}
```

### Toggle Actions

```javascript
scrollTrigger: {
  toggleActions: "play pause resume reset"
  // Format: onEnter onLeave onEnterBack onLeaveBack
  // Options: play, pause, resume, reset, restart, complete, reverse, none
}
```

---

## 📚 Resources

- [GSAP Documentation](https://gsap.com/docs/)
- [ScrollTrigger Docs](https://gsap.com/docs/v3/Plugins/ScrollTrigger)
- [Easing Visualizer](../easings/easing_visualizer.html) - Included in this package
- [GSAP Forums](https://gsap.com/community/)
- [CodePen GSAP Examples](https://codepen.io/GreenSock/pens/popular)

---

## 🎓 Learning Path

### Beginner

1. Study `main.js` - Understand each animation function
2. Enable debug markers to visualize trigger points
3. Modify existing animations (timing, easing, distances)
4. Add simple fade-in animations to new elements

### Intermediate

1. Create custom timeline sequences
2. Build your own pinned sections
3. Implement custom scroll progress indicators
4. Add toggle actions and callbacks

### Advanced

1. Create image sequence animations
2. Build complex horizontal scroll experiences
3. Integrate with Three.js or Canvas
4. Implement custom easing functions

---

## 📄 Browser Compatibility

- ✅ Chrome/Edge 90+ (Excellent)
- ✅ Firefox 88+ (Excellent)
- ✅ Safari 14+ (Good)
- ⚠️ IE11 (Not supported - requires polyfills)

---

## 🚢 Deployment

### Production Checklist

1. ✅ Set `DEBUG = false` in `main.js`
2. ✅ Remove console logs (or keep welcome message)
3. ✅ Test on multiple devices and browsers
4. ✅ Optimize images and assets
5. ✅ Consider self-hosting GSAP (instead of CDN)
6. ✅ Minify CSS and JS for production
7. ✅ Test scroll performance with DevTools

### Hosting

Works with any static hosting:
- **Netlify** - Drop folder, auto-deploy
- **Vercel** - Git integration, instant deploys
- **GitHub Pages** - Free hosting from repo
- **Cloudflare Pages** - Fast global CDN

---

## 📝 License

This template is provided as-is for use in any project (personal or commercial).

GSAP is licensed under [GreenSock License](https://gsap.com/licensing/). Free for most projects, paid license required for commercial use.

---

## 🙏 Credits

Built with:
- [GSAP](https://gsap.com) - Animation library
- [ScrollTrigger](https://gsap.com/docs/v3/Plugins/ScrollTrigger) - Scroll-driven animations
- [ScrollToPlugin](https://gsap.com/docs/v3/Plugins/ScrollToPlugin) - Smooth scroll navigation

---

## 💡 Tips for Success

1. **Start Simple** - Add animations incrementally, test frequently
2. **Use Debug Markers** - Visual feedback makes learning easier
3. **Study Examples** - Check GSAP CodePens for inspiration
4. **Test on Mobile** - Performance can vary significantly
5. **Read the Docs** - ScrollTrigger has many powerful options
6. **Join Community** - GSAP forums are helpful and active

---

## 🎉 What's Next?

- Add your own content and branding
- Customize colors and typography
- Experiment with different easing functions
- Try the [Easing Visualizer](../easings/easing_visualizer.html)
- Explore advanced patterns in `common_patterns.md`
- Build something amazing! 🚀

---

**Happy Animating!** ⚡



===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/assets/starter_scroll/index.html =====

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GSAP ScrollTrigger Starter</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <!-- Loading Screen -->
  <div id="loading">
    <div class="spinner"></div>
    <p>Loading...</p>
  </div>

  <!-- Navigation -->
  <nav class="nav">
    <div class="nav-container">
      <div class="logo">ScrollSite</div>
      <ul class="nav-links">
        <li><a href="#hero" class="nav-item">Home</a></li>
        <li><a href="#features" class="nav-item">Features</a></li>
        <li><a href="#gallery" class="nav-item">Gallery</a></li>
        <li><a href="#contact" class="nav-item">Contact</a></li>
      </ul>
    </div>
  </nav>

  <!-- Progress Bar -->
  <div class="progress-bar"></div>

  <!-- Hero Section -->
  <section id="hero" class="hero">
    <div class="hero-bg"></div>
    <div class="hero-content">
      <h1 class="hero-title">Welcome to ScrollSite</h1>
      <p class="hero-subtitle">Experience smooth scroll-driven animations</p>
      <button class="cta-btn">Get Started</button>
    </div>
    <div class="scroll-indicator">
      <span>Scroll to explore</span>
      <div class="mouse"></div>
    </div>
  </section>

  <!-- Features Section (Fade In) -->
  <section id="features" class="section features-section">
    <div class="container">
      <h2 class="section-title">Features</h2>

      <div class="cards-grid">
        <div class="card fade-in">
          <div class="card-icon">🚀</div>
          <h3>Fast Performance</h3>
          <p>Optimized animations with GPU acceleration for smooth 60fps experiences.</p>
        </div>

        <div class="card fade-in">
          <div class="card-icon">🎨</div>
          <h3>Beautiful Design</h3>
          <p>Modern, responsive layouts that look stunning on all devices.</p>
        </div>

        <div class="card fade-in">
          <div class="card-icon">⚡</div>
          <h3>Easy to Use</h3>
          <p>Simple API with powerful features for creating complex animations.</p>
        </div>

        <div class="card fade-in">
          <div class="card-icon">📱</div>
          <h3>Responsive</h3>
          <p>Adapts seamlessly to desktop, tablet, and mobile screens.</p>
        </div>

        <div class="card fade-in">
          <div class="card-icon">🔧</div>
          <h3>Customizable</h3>
          <p>Easily modify animations, timing, and easing functions.</p>
        </div>

        <div class="card fade-in">
          <div class="card-icon">💎</div>
          <h3>Production Ready</h3>
          <p>Battle-tested code ready for real-world projects.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Parallax Section -->
  <section class="section parallax-section">
    <div class="parallax-bg"></div>
    <div class="parallax-content container">
      <h2 class="section-title">Parallax Effects</h2>
      <p class="section-text">Background moves at a different speed for depth perception</p>
    </div>
  </section>

  <!-- Pin Section -->
  <section class="section pin-section">
    <div class="container pin-container">
      <div class="pin-content">
        <h2 class="pin-title">Pinned Animation</h2>
        <p class="pin-text">This section stays pinned while content animates</p>

        <div class="pin-boxes">
          <div class="pin-box box-1"></div>
          <div class="pin-box box-2"></div>
          <div class="pin-box box-3"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- Image Gallery (Stagger) -->
  <section id="gallery" class="section gallery-section">
    <div class="container">
      <h2 class="section-title">Gallery</h2>

      <div class="gallery-grid">
        <div class="gallery-item">
          <div class="gallery-image" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"></div>
          <div class="gallery-overlay">
            <h3>Project 1</h3>
            <p>Creative Design</p>
          </div>
        </div>

        <div class="gallery-item">
          <div class="gallery-image" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);"></div>
          <div class="gallery-overlay">
            <h3>Project 2</h3>
            <p>Brand Identity</p>
          </div>
        </div>

        <div class="gallery-item">
          <div class="gallery-image" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);"></div>
          <div class="gallery-overlay">
            <h3>Project 3</h3>
            <p>Web Development</p>
          </div>
        </div>

        <div class="gallery-item">
          <div class="gallery-image" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);"></div>
          <div class="gallery-overlay">
            <h3>Project 4</h3>
            <p>Mobile App</p>
          </div>
        </div>

        <div class="gallery-item">
          <div class="gallery-image" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);"></div>
          <div class="gallery-overlay">
            <h3>Project 5</h3>
            <p>UI/UX Design</p>
          </div>
        </div>

        <div class="gallery-item">
          <div class="gallery-image" style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);"></div>
          <div class="gallery-overlay">
            <h3>Project 6</h3>
            <p>Motion Graphics</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Horizontal Scroll Section -->
  <section class="section horizontal-section">
    <div class="horizontal-wrapper">
      <div class="horizontal-panels">
        <div class="horizontal-panel" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <h2>Panel 1</h2>
          <p>Horizontal scrolling creates unique experiences</p>
        </div>

        <div class="horizontal-panel" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <h2>Panel 2</h2>
          <p>Each panel can have different content</p>
        </div>

        <div class="horizontal-panel" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <h2>Panel 3</h2>
          <p>Scroll vertically to move horizontally</p>
        </div>

        <div class="horizontal-panel" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
          <h2>Panel 4</h2>
          <p>Great for storytelling and portfolios</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Text Reveal Section -->
  <section class="section text-section">
    <div class="container">
      <div class="text-reveal">
        <h2 class="reveal-line">Text reveals</h2>
        <h2 class="reveal-line">line by line</h2>
        <h2 class="reveal-line">for dramatic</h2>
        <h2 class="reveal-line">storytelling</h2>
      </div>
    </div>
  </section>

  <!-- Contact Section -->
  <section id="contact" class="section contact-section">
    <div class="container">
      <h2 class="section-title">Get in Touch</h2>

      <form class="contact-form">
        <div class="form-group fade-in">
          <input type="text" placeholder="Your Name" required>
        </div>

        <div class="form-group fade-in">
          <input type="email" placeholder="Your Email" required>
        </div>

        <div class="form-group fade-in">
          <textarea placeholder="Your Message" rows="5" required></textarea>
        </div>

        <button type="submit" class="submit-btn fade-in">Send Message</button>
      </form>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <p>&copy; 2025 ScrollSite. Built with GSAP & ScrollTrigger.</p>
      <p class="footer-links">
        <a href="#">GitHub</a> •
        <a href="#">Twitter</a> •
        <a href="#">LinkedIn</a>
      </p>
    </div>
  </footer>

  <!-- GSAP Scripts -->
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollToPlugin.min.js"></script>
  <script src="main.js"></script>

</body>
</html>

```


===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/assets/starter_scroll/main.js =====

```js
// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger, ScrollToPlugin);

// ============================
// Loading Screen
// ============================

window.addEventListener("load", () => {
  const loading = document.getElementById("loading");

  gsap.to(loading, {
    opacity: 0,
    duration: 0.5,
    delay: 0.5,
    onComplete: () => {
      loading.classList.add("hidden");
      initAnimations();
    }
  });
});

// ============================
// Initialize All Animations
// ============================

function initAnimations() {
  // Refresh ScrollTrigger after initialization
  ScrollTrigger.refresh();

  // Progress Bar
  setupProgressBar();

  // Navigation
  setupNavigation();

  // Hero Section
  animateHero();

  // Features Section (Fade In Cards)
  animateFeatures();

  // Parallax Section
  setupParallax();

  // Pin Section
  setupPinSection();

  // Gallery Section (Stagger)
  animateGallery();

  // Horizontal Scroll Section
  setupHorizontalScroll();

  // Text Reveal Section
  animateTextReveal();

  // Contact Form
  animateContactForm();

  // Smooth Scroll Links
  setupSmoothScroll();

  // Active Nav Tracking
  trackActiveSection();
}

// ============================
// Progress Bar
// ============================

function setupProgressBar() {
  gsap.to(".progress-bar", {
    scaleX: 1,
    ease: "none",
    scrollTrigger: {
      start: "top top",
      end: "bottom bottom",
      scrub: 0.3
    }
  });
}

// ============================
// Navigation Hide/Show
// ============================

function setupNavigation() {
  let lastScroll = 0;
  const nav = document.querySelector(".nav");

  ScrollTrigger.create({
    start: 100,
    end: 99999,
    onUpdate: (self) => {
      const currentScroll = self.scroll();

      if (currentScroll > lastScroll && currentScroll > 100) {
        // Scrolling down - hide nav
        gsap.to(nav, { y: -100, duration: 0.3, ease: "power2.out" });
      } else {
        // Scrolling up - show nav
        gsap.to(nav, { y: 0, duration: 0.3, ease: "power2.out" });
      }

      lastScroll = currentScroll;
    }
  });
}

// ============================
// Hero Section
// ============================

function animateHero() {
  const tl = gsap.timeline();

  tl.from(".hero-title", {
    opacity: 0,
    y: 100,
    duration: 1,
    ease: "power3.out"
  })
  .from(".hero-subtitle", {
    opacity: 0,
    y: 50,
    duration: 0.8,
    ease: "power2.out"
  }, "-=0.5")
  .from(".cta-btn", {
    scale: 0,
    duration: 0.5,
    ease: "back.out(1.7)"
  }, "-=0.3")
  .from(".scroll-indicator", {
    opacity: 0,
    y: 30,
    duration: 0.8,
    ease: "power2.out"
  }, "-=0.3");

  // Parallax effect on hero background
  gsap.to(".hero-bg", {
    yPercent: 50,
    ease: "none",
    scrollTrigger: {
      trigger: ".hero",
      start: "top top",
      end: "bottom top",
      scrub: true
    }
  });

  // Fade out hero content on scroll
  gsap.to(".hero-content", {
    opacity: 0,
    y: 100,
    ease: "none",
    scrollTrigger: {
      trigger: ".hero",
      start: "top top",
      end: "bottom top",
      scrub: true
    }
  });
}

// ============================
// Features Section (Cards)
// ============================

function animateFeatures() {
  gsap.from(".card", {
    opacity: 0,
    y: 80,
    duration: 0.8,
    ease: "power2.out",
    stagger: {
      each: 0.15,
      from: "start"
    },
    scrollTrigger: {
      trigger: ".features-section",
      start: "top 80%"
    }
  });
}

// ============================
// Parallax Section
// ============================

function setupParallax() {
  gsap.to(".parallax-bg", {
    y: 200,
    ease: "none",
    scrollTrigger: {
      trigger: ".parallax-section",
      start: "top bottom",
      end: "bottom top",
      scrub: true
    }
  });

  gsap.from(".parallax-content", {
    opacity: 0,
    scale: 0.8,
    scrollTrigger: {
      trigger: ".parallax-section",
      start: "top 80%",
      end: "top 50%",
      scrub: true
    }
  });
}

// ============================
// Pin Section with Animation
// ============================

function setupPinSection() {
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: ".pin-section",
      start: "top top",
      end: "+=1000",
      pin: true,
      scrub: 1,
      anticipatePin: 1
    }
  });

  tl.from(".pin-title", { opacity: 0, y: -50 })
    .from(".pin-text", { opacity: 0, y: -30 }, "-=0.5")
    .from(".pin-box", {
      scale: 0,
      rotation: 180,
      stagger: 0.2,
      ease: "back.out(1.7)"
    })
    .to(".pin-box", {
      y: -50,
      stagger: {
        each: 0.1,
        yoyo: true,
        repeat: 1
      }
    });
}

// ============================
// Gallery Section (Stagger)
// ============================

function animateGallery() {
  gsap.from(".gallery-item", {
    opacity: 0,
    scale: 0.5,
    duration: 0.8,
    ease: "back.out(1.7)",
    stagger: {
      each: 0.15,
      from: "center",
      grid: "auto"
    },
    scrollTrigger: {
      trigger: ".gallery-section",
      start: "top 70%"
    }
  });
}

// ============================
// Horizontal Scroll Section
// ============================

function setupHorizontalScroll() {
  const panels = gsap.utils.toArray(".horizontal-panel");

  const scrollTween = gsap.to(panels, {
    xPercent: -100 * (panels.length - 1),
    ease: "none",
    scrollTrigger: {
      trigger: ".horizontal-wrapper",
      pin: true,
      scrub: 1,
      snap: {
        snapTo: 1 / (panels.length - 1),
        duration: { min: 0.2, max: 0.5 },
        ease: "power1.inOut"
      },
      end: () => "+=" + (document.querySelector(".horizontal-wrapper").offsetWidth * panels.length)
    }
  });

  // Animate content within each panel
  panels.forEach((panel, i) => {
    gsap.from(panel.children, {
      opacity: 0,
      y: 50,
      scrollTrigger: {
        trigger: panel,
        containerAnimation: scrollTween,
        start: "left center",
        end: "center center",
        scrub: true
      }
    });
  });
}

// ============================
// Text Reveal Section
// ============================

function animateTextReveal() {
  gsap.from(".reveal-line", {
    opacity: 0,
    y: 100,
    duration: 1,
    ease: "power3.out",
    stagger: 0.2,
    scrollTrigger: {
      trigger: ".text-section",
      start: "top 70%"
    }
  });
}

// ============================
// Contact Form
// ============================

function animateContactForm() {
  gsap.from(".contact-form .fade-in", {
    opacity: 0,
    y: 50,
    duration: 0.8,
    ease: "power2.out",
    stagger: 0.15,
    scrollTrigger: {
      trigger: ".contact-form",
      start: "top 80%"
    }
  });

  // Form submission animation (demo)
  const form = document.querySelector(".contact-form");
  const submitBtn = document.querySelector(".submit-btn");

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    gsap.to(submitBtn, {
      scale: 0.9,
      duration: 0.1,
      yoyo: true,
      repeat: 1,
      onComplete: () => {
        submitBtn.textContent = "✓ Message Sent!";
        submitBtn.style.background = "#4caf50";

        setTimeout(() => {
          submitBtn.textContent = "Send Message";
          submitBtn.style.background = "";
          form.reset();
        }, 3000);
      }
    });
  });
}

// ============================
// Smooth Scroll to Sections
// ============================

function setupSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));

      if (target) {
        gsap.to(window, {
          duration: 1,
          scrollTo: {
            y: target,
            offsetY: 80 // Account for fixed header
          },
          ease: "power2.inOut"
        });
      }
    });
  });
}

// ============================
// Active Navigation Tracking
// ============================

function trackActiveSection() {
  const sections = gsap.utils.toArray("section[id]");
  const navItems = gsap.utils.toArray(".nav-item");

  sections.forEach((section, i) => {
    ScrollTrigger.create({
      trigger: section,
      start: "top center",
      end: "bottom center",
      onEnter: () => setActiveNav(section.id),
      onEnterBack: () => setActiveNav(section.id)
    });
  });

  function setActiveNav(id) {
    navItems.forEach(item => {
      if (item.getAttribute("href") === `#${id}`) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });
  }
}

// ============================
// Responsive Handling
// ============================

// Disable complex animations on mobile for performance
if (window.innerWidth < 768) {
  ScrollTrigger.config({
    limitCallbacks: true,
    ignoreMobileResize: true
  });
}

// ============================
// Refresh on Resize
// ============================

let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    ScrollTrigger.refresh();
  }, 250);
});

// ============================
// Performance Optimizations
// ============================

// Add will-change to animated elements
gsap.set(".fade-in, .card, .gallery-item, .pin-box", {
  willChange: "transform, opacity"
});

// Debug mode (set to false in production)
const DEBUG = false;

if (DEBUG) {
  ScrollTrigger.defaults({
    markers: true
  });
}

// ============================
// Console Welcome Message
// ============================

console.log(
  "%c🚀 GSAP ScrollTrigger Starter",
  "font-size: 20px; font-weight: bold; color: #667eea;"
);
console.log(
  "%cBuilt with GSAP 3 & ScrollTrigger",
  "font-size: 14px; color: #764ba2;"
);

```


===== FILE: plugins/individual/gsap-scrolltrigger/skills/gsap-scrolltrigger/assets/starter_scroll/style.css =====

```css
/* ===========================
   Reset & Base Styles
   =========================== */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --primary: #667eea;
  --secondary: #764ba2;
  --text-dark: #333;
  --text-light: #666;
  --bg-light: #f9f9f9;
  --white: #ffffff;
  --shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 20px 60px rgba(0, 0, 0, 0.15);
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: var(--text-dark);
  overflow-x: hidden;
  background: var(--white);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
}

section {
  position: relative;
}

.section {
  padding: 100px 0;
}

.section-title {
  font-size: 3rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 60px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.section-text {
  font-size: 1.2rem;
  text-align: center;
  color: var(--text-light);
  max-width: 600px;
  margin: 0 auto;
}

/* ===========================
   Loading Screen
   =========================== */

#loading {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: opacity 0.5s, visibility 0.5s;
}

#loading.hidden {
  opacity: 0;
  visibility: hidden;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

#loading p {
  color: white;
  margin-top: 20px;
  font-size: 1.2rem;
}

/* ===========================
   Navigation
   =========================== */

.nav {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow);
  z-index: 1000;
  transition: transform 0.3s;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: 30px;
  list-style: none;
}

.nav-item {
  color: var(--text-dark);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
  position: relative;
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0%;
  height: 2px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  transition: width 0.3s;
}

.nav-item:hover::after,
.nav-item.active::after {
  width: 100%;
}

/* ===========================
   Progress Bar
   =========================== */

.progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  transform-origin: left;
  transform: scaleX(0);
  z-index: 1001;
}

/* ===========================
   Hero Section
   =========================== */

.hero {
  position: relative;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: white;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  z-index: -1;
}

.hero-content {
  text-align: center;
  z-index: 1;
}

.hero-title {
  font-size: 4rem;
  font-weight: 700;
  margin-bottom: 20px;
  text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
  font-size: 1.5rem;
  margin-bottom: 40px;
  opacity: 0.9;
}

.cta-btn {
  padding: 15px 40px;
  font-size: 1.1rem;
  font-weight: 600;
  border: 2px solid white;
  background: transparent;
  color: white;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
}

.cta-btn:hover {
  background: white;
  color: var(--primary);
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.scroll-indicator {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
  color: white;
  opacity: 0.8;
}

.scroll-indicator span {
  display: block;
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.mouse {
  width: 25px;
  height: 40px;
  border: 2px solid white;
  border-radius: 15px;
  margin: 0 auto;
  position: relative;
}

.mouse::before {
  content: '';
  width: 4px;
  height: 10px;
  background: white;
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 2px;
  animation: scroll 1.5s infinite;
}

@keyframes scroll {
  0% { opacity: 1; transform: translateX(-50%) translateY(0); }
  100% { opacity: 0; transform: translateX(-50%) translateY(10px); }
}

/* ===========================
   Features Section
   =========================== */

.features-section {
  background: var(--bg-light);
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.card {
  background: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: var(--shadow);
  transition: transform 0.3s, box-shadow 0.3s;
  text-align: center;
}

.card:hover {
  transform: translateY(-10px);
  box-shadow: var(--shadow-lg);
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.card h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: var(--text-dark);
}

.card p {
  color: var(--text-light);
  line-height: 1.8;
}

/* ===========================
   Parallax Section
   =========================== */

.parallax-section {
  position: relative;
  height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: white;
}

.parallax-bg {
  position: absolute;
  top: -50%;
  left: 0;
  width: 100%;
  height: 150%;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%23667eea" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,122.7C672,117,768,139,864,149.3C960,160,1056,160,1152,138.7C1248,117,1344,75,1392,53.3L1440,32L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') center/cover;
  z-index: -1;
}

.parallax-content {
  text-align: center;
  z-index: 1;
}

/* ===========================
   Pin Section
   =========================== */

.pin-section {
  min-height: 150vh;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.pin-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pin-content {
  text-align: center;
}

.pin-title {
  font-size: 3rem;
  margin-bottom: 20px;
}

.pin-text {
  font-size: 1.3rem;
  margin-bottom: 60px;
  opacity: 0.9;
}

.pin-boxes {
  display: flex;
  gap: 30px;
  justify-content: center;
}

.pin-box {
  width: 100px;
  height: 100px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

/* ===========================
   Gallery Section
   =========================== */

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.gallery-item {
  position: relative;
  height: 300px;
  border-radius: 15px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: var(--shadow);
  transition: transform 0.3s;
}

.gallery-item:hover {
  transform: scale(1.05);
}

.gallery-image {
  width: 100%;
  height: 100%;
  transition: transform 0.3s;
}

.gallery-item:hover .gallery-image {
  transform: scale(1.1);
}

.gallery-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  color: white;
}

.gallery-item:hover .gallery-overlay {
  opacity: 1;
}

.gallery-overlay h3 {
  font-size: 2rem;
  margin-bottom: 10px;
}

/* ===========================
   Horizontal Scroll Section
   =========================== */

.horizontal-section {
  padding: 0;
  background: #000;
  overflow: hidden;
}

.horizontal-wrapper {
  height: 100vh;
  display: flex;
  align-items: center;
}

.horizontal-panels {
  display: flex;
  will-change: transform;
}

.horizontal-panel {
  min-width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
  padding: 60px;
}

.horizontal-panel h2 {
  font-size: 3rem;
  margin-bottom: 20px;
}

.horizontal-panel p {
  font-size: 1.3rem;
  max-width: 500px;
}

/* ===========================
   Text Reveal Section
   =========================== */

.text-section {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-reveal {
  text-align: center;
}

.reveal-line {
  font-size: 4rem;
  font-weight: 700;
  color: white;
  text-transform: uppercase;
  line-height: 1.2;
  margin: 10px 0;
}

/* ===========================
   Contact Section
   =========================== */

.contact-section {
  background: var(--bg-light);
}

.contact-form {
  max-width: 600px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 25px;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-family: inherit;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary);
}

.submit-btn {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.submit-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
}

/* ===========================
   Footer
   =========================== */

.footer {
  background: #222;
  color: white;
  padding: 40px 0;
  text-align: center;
}

.footer-links {
  margin-top: 15px;
}

.footer-links a {
  color: white;
  text-decoration: none;
  margin: 0 10px;
  transition: opacity 0.3s;
}

.footer-links a:hover {
  opacity: 0.7;
}

/* ===========================
   Responsive
   =========================== */

@media (max-width: 768px) {
  .section {
    padding: 60px 0;
  }

  .container {
    padding: 0 20px;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .nav-links {
    gap: 15px;
    font-size: 0.9rem;
  }

  .cards-grid {
    grid-template-columns: 1fr;
  }

  .gallery-grid {
    grid-template-columns: 1fr;
  }

  .horizontal-panel h2 {
    font-size: 2rem;
  }

  .reveal-line {
    font-size: 2.5rem;
  }
}

/* ===========================
   Utility Classes
   =========================== */

.fade-in {
  opacity: 0;
  transform: translateY(50px);
}

.will-change {
  will-change: transform, opacity;
}

```


# Skill: motion-framer


===== FILE: plugins/individual/motion-framer/skills/motion-framer/SKILL.md =====

---
name: motion-framer
description: Modern animation library for React and JavaScript. Create smooth, production-ready animations with motion components, variants, gestures (hover/tap/drag), layout animations, AnimatePresence exit animations, spring physics, and scroll-based effects. Use when building interactive UI components, micro-interactions, page transitions, or complex animation sequences.
---

# Motion & Framer Motion

## Overview

Motion (formerly Framer Motion) is a production-ready animation library for React and JavaScript that enables declarative, performant animations with minimal code. It provides `motion` components that wrap HTML elements with animation superpowers, supports gesture recognition (hover, tap, drag, focus), and includes advanced features like layout animations, exit animations, and spring physics.

**When to use this skill:**
- Building interactive UI components (buttons, cards, menus)
- Creating micro-interactions and hover effects
- Implementing page transitions and route animations
- Adding scroll-based animations and parallax effects
- Animating layout changes (resizing, reordering, shared element transitions)
- Drag-and-drop interfaces
- Complex animation sequences and state-based animations
- Replacing CSS transitions with more powerful, controllable animations

**Technology:**
- **Motion** (v11+) - The modern, smaller library from Framer Motion creators
- **Framer Motion** - The full-featured predecessor (still widely used)
- React 18+ compatible, also supports Vue
- Supports TypeScript
- Works with Next.js, Vite, Remix, and all modern React frameworks

## Core Concepts

### 1. Motion Components

Convert any HTML/SVG element into an animatable component by prefixing with `motion.`:

```jsx
import { motion } from "framer-motion"

// Regular HTML becomes motion component
<motion.div />
<motion.button />
<motion.svg />
<motion.path />
```

Every motion component accepts animation props like `animate`, `initial`, `transition`, and gesture props like `whileHover`, `whileTap`, etc.

### 2. Animate Prop

The `animate` prop defines the target animation state. When values change, Motion automatically animates to them:

```jsx
// Simple animation - x position changes
<motion.div animate={{ x: 100 }} />

// Multiple properties
<motion.div animate={{ x: 100, opacity: 1, scale: 1.2 }} />

// Animates when state changes
const [isOpen, setIsOpen] = useState(false)
<motion.div animate={{ width: isOpen ? 300 : 100 }} />
```

### 3. Initial State

Set the initial state before animation using the `initial` prop:

```jsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  animate={{ opacity: 1, y: 0 }}
/>
```

Set `initial={false}` to disable initial animations on mount.

### 4. Transitions

Control how animations move between states using the `transition` prop:

```jsx
// Duration-based
<motion.div
  animate={{ x: 100 }}
  transition={{ duration: 0.5, ease: "easeInOut" }}
/>

// Spring physics
<motion.div
  animate={{ scale: 1.2 }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
/>

// Different transitions for different properties
<motion.div
  animate={{ x: 100, opacity: 1 }}
  transition={{
    x: { type: "spring", stiffness: 300 },
    opacity: { duration: 0.2 }
  }}
/>
```

**Transition types:**
- `"tween"` (default) - Duration-based with easing
- `"spring"` - Physics-based spring animation
- `"inertia"` - Decelerating animation (used in drag)

### 5. Variants

Organize animation states using named variants for cleaner code and propagation to children:

```jsx
const variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, scale: 0.9 }
}

<motion.div
  variants={variants}
  initial="hidden"
  animate="visible"
  exit="exit"
/>
```

**Variant propagation** - Children automatically inherit parent variant states:

```jsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1  // Stagger child animations
    }
  }
}

const itemVariants = {
  hidden: { x: -20, opacity: 0 },
  visible: { x: 0, opacity: 1 }
}

<motion.ul variants={containerVariants} initial="hidden" animate="visible">
  <motion.li variants={itemVariants} />
  <motion.li variants={itemVariants} />
  <motion.li variants={itemVariants} />
</motion.ul>
```

## Common Patterns

### 1. Hover Animations

Animate on hover using `whileHover` prop:

```jsx
// Simple hover effect
<motion.button
  whileHover={{ scale: 1.1 }}
  transition={{ duration: 0.2 }}
>
  Hover me
</motion.button>

// Multiple properties
<motion.div
  whileHover={{
    scale: 1.05,
    backgroundColor: "#f0f0f0",
    boxShadow: "0px 10px 30px rgba(0, 0, 0, 0.2)"
  }}
>
  Hover card
</motion.div>

// With custom transition
<motion.button
  whileHover={{
    scale: 1.2,
    transition: { duration: 0.1 }  // Transition for gesture start
  }}
  transition={{ duration: 0.5 }}  // Transition for gesture end
>
  Button
</motion.button>
```

**Hover with nested elements:**

```jsx
<motion.div whileHover="hover" variants={cardVariants}>
  <motion.h3 variants={titleVariants}>Title</motion.h3>
  <motion.img variants={imageVariants} />
</motion.div>
```

### 2. Tap/Press Animations

Animate on tap/press using `whileTap` prop:

```jsx
// Scale down on tap
<motion.button
  whileTap={{ scale: 0.9 }}
>
  Click me
</motion.button>

// Combined hover + tap
<motion.button
  whileHover={{ scale: 1.1 }}
  whileTap={{ scale: 0.95, rotate: 3 }}
>
  Interactive button
</motion.button>

// With variants
const buttonVariants = {
  rest: { scale: 1 },
  hover: { scale: 1.1 },
  pressed: { scale: 0.95 }
}

<motion.button
  variants={buttonVariants}
  initial="rest"
  whileHover="hover"
  whileTap="pressed"
>
  Button
</motion.button>
```

### 3. Drag Interactions

Make elements draggable with the `drag` prop:

```jsx
// Basic dragging (both axes)
<motion.div drag />

// Constrain to axis
<motion.div drag="x" />  // Only horizontal
<motion.div drag="y" />  // Only vertical

// Drag constraints
<motion.div
  drag
  dragConstraints={{ left: -100, right: 100, top: -100, bottom: 100 }}
/>

// Drag with parent constraints
<motion.div ref={constraintsRef}>
  <motion.div drag dragConstraints={constraintsRef} />
</motion.div>

// Visual feedback while dragging
<motion.div
  drag
  whileDrag={{
    scale: 1.1,
    boxShadow: "0px 10px 20px rgba(0,0,0,0.2)",
    cursor: "grabbing"
  }}
  dragElastic={0.1}  // Elasticity when dragging outside constraints
  dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
/>
```

**Drag events:**

```jsx
<motion.div
  drag
  onDragStart={(event, info) => console.log(info.point)}
  onDrag={(event, info) => console.log(info.offset)}
  onDragEnd={(event, info) => console.log(info.velocity)}
/>
```

### 4. Exit Animations (AnimatePresence)

Animate components when they're removed from the DOM using `AnimatePresence`:

```jsx
import { AnimatePresence } from "framer-motion"

// Basic exit animation
<AnimatePresence>
  {isVisible && (
    <motion.div
      key="modal"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    />
  )}
</AnimatePresence>
```

**Key requirements:**
- Component must be direct child of `<AnimatePresence>`
- Must have a unique `key` prop
- Use `exit` prop to define exit animation

**List items with exit animations:**

```jsx
<AnimatePresence>
  {items.map(item => (
    <motion.li
      key={item.id}
      initial={{ opacity: 0, x: -50 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 50 }}
      layout  // Smooth layout shifts
    >
      {item.name}
    </motion.li>
  ))}
</AnimatePresence>
```

**Staggered exit animations:**

```jsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      when: "beforeChildren",
      staggerChildren: 0.1
    }
  },
  exit: {
    opacity: 0,
    transition: {
      when: "afterChildren",
      staggerChildren: 0.05,
      staggerDirection: -1  // Reverse order
    }
  }
}

<AnimatePresence>
  {show && (
    <motion.div variants={containerVariants} initial="hidden" animate="visible" exit="exit">
      <motion.div variants={itemVariants} />
      <motion.div variants={itemVariants} />
      <motion.div variants={itemVariants} />
    </motion.div>
  )}
</AnimatePresence>
```

### 5. Layout Animations

Automatically animate layout changes (position, size) with the `layout` prop:

```jsx
// Animate all layout changes
<motion.div layout />

// Animate only position changes
<motion.div layout="position" />

// Animate only size changes
<motion.div layout="size" />
```

**Grid layout animation:**

```jsx
const [columns, setColumns] = useState(3)

<motion.div className="grid">
  {items.map(item => (
    <motion.div
      key={item.id}
      layout
      transition={{ layout: { duration: 0.3, ease: "easeInOut" } }}
    />
  ))}
</motion.div>
```

**Shared layout animations (layoutId):**

Connect two different elements for smooth transitions using `layoutId`:

```jsx
// Tab indicator example
<nav>
  {tabs.map(tab => (
    <button key={tab.id} onClick={() => setActive(tab.id)}>
      {tab.label}
      {activeTab === tab.id && (
        <motion.div
          layoutId="underline"
          style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 2 }}
        />
      )}
    </button>
  ))}
</nav>

// Modal opening from thumbnail
<motion.img
  src={thumbnail}
  layoutId="product-image"
  onClick={() => setExpanded(true)}
/>

<AnimatePresence>
  {expanded && (
    <motion.div layoutId="product-image">
      <img src={fullsize} />
    </motion.div>
  )}
</AnimatePresence>
```

### 6. Scroll-Based Animations

Animate elements when they enter the viewport using `whileInView`:

```jsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.8 }}  // once: trigger once, amount: 80% visible
  transition={{ duration: 0.5 }}
>
  Animates when scrolled into view
</motion.div>
```

**Viewport options:**
- `once: true` - Animation triggers only once
- `amount: 0.5` - Percentage of element visible (0-1) or "some" | "all"
- `margin: "-100px"` - Offset viewport boundaries

**Staggered scroll animations:**

```jsx
<motion.ul
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, amount: 0.3 }}
  variants={{
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    },
    hidden: { opacity: 0 }
  }}
>
  <motion.li variants={itemVariants} />
  <motion.li variants={itemVariants} />
  <motion.li variants={itemVariants} />
</motion.ul>
```

### 7. Spring Animations

Use spring physics for natural, bouncy animations:

```jsx
// Basic spring
<motion.div
  animate={{ scale: 1.2 }}
  transition={{ type: "spring" }}
/>

// Customize spring physics
<motion.div
  animate={{ x: 100 }}
  transition={{
    type: "spring",
    stiffness: 300,  // Higher = faster, snappier (default: 100)
    damping: 20,     // Higher = less bouncy (default: 10)
    mass: 1,         // Higher = more inertia (default: 1)
  }}
/>

// Visual duration (easier spring control)
<motion.div
  animate={{ rotate: 90 }}
  transition={{
    type: "spring",
    visualDuration: 0.5,  // Perceived duration
    bounce: 0.25          // Bounciness (0-1, default: 0.25)
  }}
/>
```

**Spring presets:**
- **Gentle**: `stiffness: 100, damping: 20`
- **Wobbly**: `stiffness: 200, damping: 10`
- **Stiff**: `stiffness: 400, damping: 30`
- **Slow**: `stiffness: 50, damping: 20`

## Gesture Recognition

Motion provides declarative gesture handlers:

### Gesture Props

```jsx
<motion.div
  whileHover={{ scale: 1.1 }}        // Pointer hovers over element
  whileTap={{ scale: 0.9 }}          // Primary pointer presses element
  whileFocus={{ outline: "2px" }}    // Element gains focus
  whileDrag={{ scale: 1.1 }}         // Element is being dragged
  whileInView={{ opacity: 1 }}       // Element is in viewport
/>
```

### Gesture Events

```jsx
<motion.div
  onHoverStart={(event, info) => {}}
  onHoverEnd={(event, info) => {}}
  onTap={(event, info) => {}}
  onTapStart={(event, info) => {}}
  onTapCancel={(event, info) => {}}
  onDragStart={(event, info) => {}}
  onDrag={(event, info) => {}}
  onDragEnd={(event, info) => {}}
  onViewportEnter={(entry) => {}}
  onViewportLeave={(entry) => {}}
/>
```

**Event info objects contain:**
- `point: { x, y }` - Page coordinates
- `offset: { x, y }` - Offset from drag start
- `velocity: { x, y }` - Drag velocity

## Hooks

### useAnimate

Manually control animations with the `useAnimate` hook:

```jsx
import { useAnimate } from "framer-motion"

function Component() {
  const [scope, animate] = useAnimate()

  useEffect(() => {
    // Animate multiple elements
    animate([
      [scope.current, { opacity: 1 }],
      ["li", { x: 0, opacity: 1 }, { delay: stagger(0.1) }],
      [".button", { scale: 1.2 }]
    ])
  }, [])

  return (
    <div ref={scope}>
      <ul>
        <li>Item 1</li>
        <li>Item 2</li>
      </ul>
      <button className="button">Click</button>
    </div>
  )
}
```

**Animation controls:**

```jsx
const controls = animate(element, { x: 100 })
controls.play()
controls.pause()
controls.stop()
controls.speed = 0.5
controls.time = 0  // Seek to start
```

### useSpring

Create spring-animated motion values:

```jsx
import { useSpring } from "framer-motion"

function Component() {
  const x = useSpring(0, { stiffness: 300, damping: 20 })

  return (
    <motion.div style={{ x }}>
      <button onClick={() => x.set(100)}>Move</button>
    </motion.div>
  )
}
```

### useInView

Detect when an element is in viewport:

```jsx
import { useInView } from "framer-motion"

function Component() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, amount: 0.5 })

  return (
    <div ref={ref}>
      {isInView ? "In view!" : "Not in view"}
    </div>
  )
}
```

## Integration Patterns

### With GSAP

Combine Motion for React state-based animations and GSAP for complex timelines:

```jsx
import { motion } from "framer-motion"
import gsap from "gsap"

function Component() {
  const boxRef = useRef()

  const handleClick = () => {
    // Use GSAP for complex timeline
    const tl = gsap.timeline()
    tl.to(boxRef.current, { rotation: 360, duration: 1 })
      .to(boxRef.current, { scale: 1.5, duration: 0.5 })
  }

  return (
    // Use Motion for hover/tap/layout animations
    <motion.div
      ref={boxRef}
      whileHover={{ scale: 1.1 }}
      onClick={handleClick}
    />
  )
}
```

### With React Three Fiber

Animate 3D objects using Motion values:

```jsx
import { motion } from "framer-motion"
import { useFrame } from "@react-three/fiber"

function Box() {
  const x = useMotionValue(0)

  useFrame(() => {
    // Sync Motion value with Three.js position
    meshRef.current.position.x = x.get()
  })

  return (
    <>
      <mesh ref={meshRef}>
        <boxGeometry />
        <meshStandardMaterial />
      </mesh>
      <motion.div
        style={{ x }}
        drag="x"
        dragConstraints={{ left: -5, right: 5 }}
      />
    </>
  )
}
```

### With Form Libraries

Animate form validation states:

```jsx
import { motion, AnimatePresence } from "framer-motion"

function FormField({ error }) {
  return (
    <div>
      <motion.input
        animate={{
          borderColor: error ? "#ff0000" : "#cccccc",
          x: error ? [0, -10, 10, -10, 10, 0] : 0  // Shake animation
        }}
        transition={{ duration: 0.4 }}
      />
      <AnimatePresence>
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            style={{ color: "#ff0000" }}
          >
            {error}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  )
}
```

## Performance Optimization

### 1. Use Transform Properties

Transform properties (x, y, scale, rotate) are hardware-accelerated:

```jsx
// ✅ Good - Hardware accelerated
<motion.div animate={{ x: 100, scale: 1.2 }} />

// ❌ Avoid - Triggers layout/paint
<motion.div animate={{ left: 100, width: 200 }} />
```

### 2. Individual Transform Properties

Motion supports individual transform properties for cleaner code:

```jsx
// Individual properties (Motion feature)
<motion.div style={{ x: 100, rotate: 45, scale: 1.2 }} />

// Traditional (also supported)
<motion.div style={{ transform: "translateX(100px) rotate(45deg) scale(1.2)" }} />
```

### 3. Reduce Motion for Accessibility

Respect user preferences for reduced motion:

```jsx
import { useReducedMotion } from "framer-motion"

function Component() {
  const shouldReduceMotion = useReducedMotion()

  return (
    <motion.div
      animate={{ x: 100 }}
      transition={shouldReduceMotion ? { duration: 0 } : { duration: 0.5 }}
    />
  )
}
```

### 4. Layout Animations Performance

Layout animations can be expensive. Optimize with:

```jsx
// Specify what to animate
<motion.div layout="position" />  // Only position, not size

// Optimize transition
<motion.div
  layout
  transition={{
    layout: { duration: 0.3, ease: "easeOut" }
  }}
/>
```

### 5. Use layoutId Sparingly

`layoutId` creates shared layout animations but tracks elements globally. Use only when needed.

## Common Pitfalls

### 1. Forgetting AnimatePresence for Exit Animations

**Problem:** Exit animations don't work

```jsx
// ❌ Wrong - No AnimatePresence
{show && <motion.div exit={{ opacity: 0 }} />}
```

```jsx
// ✅ Correct - Wrapped in AnimatePresence
<AnimatePresence>
  {show && <motion.div exit={{ opacity: 0 }} />}
</AnimatePresence>
```

### 2. Missing key Prop in Lists

**Problem:** AnimatePresence can't track elements

```jsx
// ❌ Wrong - No key
<AnimatePresence>
  {items.map(item => <motion.div exit={{ opacity: 0 }} />)}
</AnimatePresence>
```

```jsx
// ✅ Correct - Unique keys
<AnimatePresence>
  {items.map(item => (
    <motion.div key={item.id} exit={{ opacity: 0 }} />
  ))}
</AnimatePresence>
```

### 3. Animating Non-Transform Properties

**Problem:** Janky animations, poor performance

```jsx
// ❌ Avoid - Not hardware accelerated
<motion.div animate={{ top: 100, left: 50, width: 200 }} />
```

```jsx
// ✅ Better - Use transforms
<motion.div animate={{ x: 50, y: 100, scaleX: 2 }} />
```

### 4. Overusing Layout Animations

**Problem:** Performance issues with many layout-animated elements

```jsx
// ❌ Too many layout animations
{items.map(item => <motion.div layout>{item}</motion.div>)}
```

```jsx
// ✅ Use layout only where needed, optimize others
{items.map(item => (
  <motion.div
    key={item.id}
    animate={{ opacity: 1 }}  // Cheaper animation
    exit={{ opacity: 0 }}
  />
))}
```

### 5. Not Using Variants for Complex Animations

**Problem:** Duplicated animation code, no child orchestration

```jsx
// ❌ Repetitive
<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} />
<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} />
```

```jsx
// ✅ Use variants
const variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 }
}

<motion.div variants={variants} initial="hidden" animate="visible" />
<motion.div variants={variants} initial="hidden" animate="visible" />
```

### 6. Incorrect Transition Timing

**Problem:** Transitions don't apply to specific gestures

```jsx
// ❌ Wrong - General transition won't apply to whileHover
<motion.div
  whileHover={{ scale: 1.2 }}
  transition={{ duration: 1 }}  // This applies to animate prop, not whileHover
/>
```

```jsx
// ✅ Correct - Transition in whileHover or separate gesture transition
<motion.div
  whileHover={{
    scale: 1.2,
    transition: { duration: 0.2 }  // Applies to hover start
  }}
  transition={{ duration: 0.5 }}  // Applies to hover end
/>
```

## Resources

### Official Documentation
- [Motion Docs](https://motion.dev/) - Official Motion documentation
- [Framer Motion Docs](https://www.framer.com/motion/) - Framer Motion (legacy)
- [Motion GitHub](https://github.com/framer/motion) - Source code & examples

### Bundled Resources

This skill includes:

**references/**
- `api_reference.md` - Complete Motion API reference
- `variants_patterns.md` - Variant patterns and orchestration
- `gesture_guide.md` - Comprehensive gesture handling guide

**scripts/**
- `animation_generator.py` - Generate Motion component boilerplate
- `variant_builder.py` - Interactive variant configuration tool

**assets/**
- `starter_motion/` - Complete Motion + Vite starter template
- `examples/` - Real-world Motion component patterns

### Community Resources
- [Motion Dev Discord](https://discord.gg/motion) - Official community
- [Framer Motion Examples](https://www.framer.com/motion/examples/) - Interactive examples
- [Motion Recipes](https://motion.dev/docs/recipes) - Common patterns
- [CodeSandbox Templates](https://codesandbox.io/s/framer-motion-examples) - Live demos



===== FILE: plugins/individual/motion-framer/skills/motion-framer/references/api_reference.md =====

# Motion & Framer Motion - Complete API Reference

Comprehensive API documentation for Motion (v11+) and Framer Motion animation libraries.

## Table of Contents

1. [Motion Component Props](#motion-component-props)
2. [Animation Props](#animation-props)
3. [Gesture Props](#gesture-props)
4. [Layout Props](#layout-props)
5. [Transition Options](#transition-options)
6. [Variants](#variants)
7. [Hooks](#hooks)
8. [AnimatePresence](#animatepresence)
9. [Utilities](#utilities)

---

## Motion Component Props

All motion components (`motion.div`, `motion.button`, etc.) accept these props:

### Core Animation Props

```typescript
interface MotionProps {
  // Animation state
  animate?: AnimationControls | TargetAndTransition | VariantLabels
  initial?: boolean | Target | VariantLabels
  exit?: TargetAndTransition | VariantLabels

  // Transition
  transition?: Transition

  // Variants
  variants?: Variants

  // Style
  style?: MotionStyle

  // Layout
  layout?: boolean | "position" | "size"
  layoutId?: string
  layoutDependency?: any
  layoutScroll?: boolean

  // Gestures
  whileHover?: VariantLabels | TargetAndTransition
  whileTap?: VariantLabels | TargetAndTransition
  whileFocus?: VariantLabels | TargetAndTransition
  whileDrag?: VariantLabels | TargetAndTransition
  whileInView?: VariantLabels | TargetAndTransition

  // Drag
  drag?: boolean | "x" | "y"
  dragConstraints?: Constraints | RefObject<Element>
  dragElastic?: DragElastic
  dragMomentum?: boolean
  dragTransition?: InertiaOptions
  dragPropagation?: boolean
  dragSnapToOrigin?: boolean

  // Viewport
  viewport?: ViewportOptions

  // Events
  onUpdate?: (latest: Target) => void
  onAnimationStart?: (definition: AnimationDefinition) => void
  onAnimationComplete?: (definition: AnimationDefinition) => void

  // Hover events
  onHoverStart?: (event: MouseEvent, info: EventInfo) => void
  onHoverEnd?: (event: MouseEvent, info: EventInfo) => void

  // Tap events
  onTap?: (event: MouseEvent | TouchEvent | PointerEvent, info: TapInfo) => void
  onTapStart?: (event: MouseEvent | TouchEvent | PointerEvent, info: TapInfo) => void
  onTapCancel?: (event: MouseEvent | TouchEvent | PointerEvent, info: TapInfo) => void

  // Focus events
  onFocus?: (event: FocusEvent) => void
  onBlur?: (event: FocusEvent) => void

  // Drag events
  onDragStart?: (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => void
  onDrag?: (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => void
  onDragEnd?: (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => void

  // Viewport events
  onViewportEnter?: (entry: IntersectionObserverEntry | null) => void
  onViewportLeave?: (entry: IntersectionObserverEntry | null) => void

  // Pan events
  onPan?: (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => void
  onPanStart?: (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => void
  onPanEnd?: (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => void
}
```

---

## Animation Props

### animate

Defines the target animation state. Accepts object, variant label, or animation controls.

```typescript
// As object
<motion.div animate={{ x: 100, opacity: 1 }} />

// As variant label
<motion.div animate="visible" />

// As array of variant labels (applied in order)
<motion.div animate={["visible", "active"]} />

// Dynamic based on state
<motion.div animate={isOpen ? "open" : "closed"} />
```

**Type:**
```typescript
animate?: AnimationControls | TargetAndTransition | VariantLabels
```

### initial

Sets the initial state before animation. Set to `false` to disable initial animation.

```typescript
// As object
<motion.div initial={{ opacity: 0, y: 50 }} />

// As variant label
<motion.div initial="hidden" />

// Disable initial animation
<motion.div initial={false} />
```

**Type:**
```typescript
initial?: boolean | Target | VariantLabels
```

### exit

Defines animation when component is removed from DOM. Requires `AnimatePresence`.

```typescript
<AnimatePresence>
  {show && (
    <motion.div
      exit={{ opacity: 0, scale: 0.9 }}
    />
  )}
</AnimatePresence>
```

**Type:**
```typescript
exit?: TargetAndTransition | VariantLabels
```

### style

Motion-specific style prop that supports individual transform properties.

```typescript
<motion.div
  style={{
    x: 100,           // translateX
    y: 50,            // translateY
    scale: 1.2,       // scale
    rotate: 45,       // rotate in degrees
    rotateX: 90,      // 3D rotation
    opacity: 0.5,
    backgroundColor: "#ff0000"
  }}
/>
```

**Transform properties:**
- `x`, `y`, `z` - Translation (px)
- `scale`, `scaleX`, `scaleY` - Scale (unitless)
- `rotate`, `rotateX`, `rotateY`, `rotateZ` - Rotation (deg)
- `skew`, `skewX`, `skewY` - Skew (deg)
- `originX`, `originY`, `originZ` - Transform origin (0-1 or px)
- `perspective` - 3D perspective (px)

---

## Gesture Props

### whileHover

Animation applied while element is hovered.

```typescript
<motion.button
  whileHover={{ scale: 1.1 }}
  // Or with custom transition
  whileHover={{
    scale: 1.2,
    transition: { duration: 0.1 }
  }}
/>
```

**Type:**
```typescript
whileHover?: VariantLabels | TargetAndTransition
```

### whileTap

Animation applied while element is pressed.

```typescript
<motion.button
  whileTap={{ scale: 0.9, rotate: 3 }}
/>
```

**Type:**
```typescript
whileTap?: VariantLabels | TargetAndTransition
```

### whileFocus

Animation applied while element has focus.

```typescript
<motion.input
  whileFocus={{ borderColor: "#0066ff", scale: 1.02 }}
/>
```

**Type:**
```typescript
whileFocus?: VariantLabels | TargetAndTransition
```

### whileDrag

Animation applied while element is being dragged.

```typescript
<motion.div
  drag
  whileDrag={{ scale: 1.1, cursor: "grabbing" }}
/>
```

**Type:**
```typescript
whileDrag?: VariantLabels | TargetAndTransition
```

### whileInView

Animation applied while element is in viewport.

```typescript
<motion.div
  initial={{ opacity: 0 }}
  whileInView={{ opacity: 1 }}
  viewport={{ once: true, amount: 0.5 }}
/>
```

**Type:**
```typescript
whileInView?: VariantLabels | TargetAndTransition
```

---

## Layout Props

### layout

Enables automatic layout animations for position/size changes.

```typescript
// Animate all layout changes
<motion.div layout />

// Animate only position
<motion.div layout="position" />

// Animate only size
<motion.div layout="size" />
```

**Type:**
```typescript
layout?: boolean | "position" | "size"
```

### layoutId

Creates shared layout animations between different components.

```typescript
// Animated tab indicator
{tabs.map(tab => (
  <div key={tab.id}>
    {tab.label}
    {activeTab === tab.id && (
      <motion.div layoutId="underline" />
    )}
  </div>
))}
```

**Type:**
```typescript
layoutId?: string
```

### layoutDependency

Forces layout animation when this value changes.

```typescript
<motion.div
  layout
  layoutDependency={sortOrder}
/>
```

**Type:**
```typescript
layoutDependency?: any
```

---

## Transition Options

### Transition Interface

```typescript
interface Transition {
  // Duration-based (tween)
  duration?: number
  ease?: Easing | Easing[]
  times?: number[]

  // Spring-based
  type?: "tween" | "spring" | "inertia"
  stiffness?: number
  damping?: number
  mass?: number
  velocity?: number
  restSpeed?: number
  restDelta?: number

  // Visual spring (easier configuration)
  visualDuration?: number
  bounce?: number

  // Timing
  delay?: number
  delayChildren?: number
  staggerChildren?: number
  staggerDirection?: 1 | -1

  // Orchestration
  when?: "beforeChildren" | "afterChildren" | false
  repeat?: number
  repeatType?: "loop" | "reverse" | "mirror"
  repeatDelay?: number

  // Per-property transitions
  [key: string]: any
}
```

### Tween Transitions (Duration-based)

```typescript
<motion.div
  animate={{ x: 100 }}
  transition={{
    duration: 0.5,
    ease: "easeInOut",
    times: [0, 0.5, 1],  // Keyframe times
    delay: 0.2
  }}
/>
```

**Easing options:**
- `"linear"`
- `"easeIn"`, `"easeOut"`, `"easeInOut"`
- `"circIn"`, `"circOut"`, `"circInOut"`
- `"backIn"`, `"backOut"`, `"backInOut"`
- `"anticipate"`
- Custom array: `[0.42, 0, 0.58, 1]` (cubic-bezier)

### Spring Transitions (Physics-based)

```typescript
<motion.div
  animate={{ x: 100 }}
  transition={{
    type: "spring",
    stiffness: 300,   // Higher = faster (default: 100)
    damping: 20,      // Higher = less bouncy (default: 10)
    mass: 1,          // Higher = more inertia (default: 1)
    velocity: 50      // Initial velocity
  }}
/>
```

**Visual spring (simplified):**

```typescript
<motion.div
  animate={{ rotate: 90 }}
  transition={{
    type: "spring",
    visualDuration: 0.5,  // Perceived duration
    bounce: 0.25          // Bounciness (0-1)
  }}
/>
```

### Inertia Transitions (Decelerating)

Used automatically in drag. Can be customized:

```typescript
<motion.div
  drag
  dragTransition={{
    bounceStiffness: 600,
    bounceDamping: 20,
    power: 0.3,
    timeConstant: 200,
    min: 0,
    max: 100
  }}
/>
```

### Orchestration

**Staggering children:**

```typescript
const containerVariants = {
  visible: {
    transition: {
      staggerChildren: 0.1,        // Delay between each child
      delayChildren: 0.2,          // Delay before first child
      staggerDirection: 1,         // 1 = forward, -1 = reverse
      when: "beforeChildren"       // Animate parent before/after children
    }
  }
}
```

**Per-property transitions:**

```typescript
<motion.div
  animate={{ x: 100, opacity: 1 }}
  transition={{
    x: { type: "spring", stiffness: 300 },
    opacity: { duration: 0.2 },
    default: { ease: "linear" }
  }}
/>
```

**Repeating animations:**

```typescript
<motion.div
  animate={{ rotate: 360 }}
  transition={{
    repeat: Infinity,
    repeatType: "loop",     // "loop" | "reverse" | "mirror"
    repeatDelay: 1,
    duration: 2
  }}
/>
```

---

## Variants

Variants are predefined animation states that can be applied to components and their children.

### Variant Definition

```typescript
type Variants = {
  [key: string]: TargetAndTransition
}

// Example
const variants: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
    transition: { duration: 0.3 }
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, delay: 0.1 }
  }
}
```

### Variant Propagation

Children inherit parent variant labels automatically:

```typescript
const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const item = {
  hidden: { x: -20, opacity: 0 },
  visible: { x: 0, opacity: 1 }
}

<motion.ul variants={container} initial="hidden" animate="visible">
  <motion.li variants={item} />
  <motion.li variants={item} />
  <motion.li variants={item} />
</motion.ul>
```

### Dynamic Variants

Variants can be functions that receive custom data:

```typescript
const variants = {
  visible: (i: number) => ({
    opacity: 1,
    transition: {
      delay: i * 0.1
    }
  })
}

{items.map((item, i) => (
  <motion.div
    key={item.id}
    custom={i}
    variants={variants}
    animate="visible"
  />
))}
```

---

## Hooks

### useAnimate

Manually control animations with imperative API.

```typescript
import { useAnimate, stagger } from "framer-motion"

function Component() {
  const [scope, animate] = useAnimate()

  // Animate single element
  animate(scope.current, { x: 100 })

  // Animate with selector
  animate("li", { opacity: 1 })

  // Sequence of animations
  animate([
    [scope.current, { opacity: 1 }],
    ["li", { x: 0 }, { delay: stagger(0.1) }],
    [".button", { scale: 1.2 }]
  ])

  return <div ref={scope}>...</div>
}
```

**Returns:** `[scope: RefObject, animate: AnimateFunction]`

**AnimationControls methods:**
```typescript
const controls = animate(element, { x: 100 })
controls.play()
controls.pause()
controls.stop()
controls.cancel()
controls.speed = 0.5
controls.time = 0
controls.then(() => console.log("Complete"))
```

### useMotionValue

Create a motion value that can be read, set, and animated.

```typescript
import { useMotionValue } from "framer-motion"

const x = useMotionValue(0)

// Get value
const currentX = x.get()

// Set value
x.set(100)

// Listen to changes
x.on("change", (latest) => console.log(latest))
x.on("animationStart", () => {})
x.on("animationComplete", () => {})

// Use in component
<motion.div style={{ x }} />
```

### useTransform

Transform one motion value into another.

```typescript
import { useMotionValue, useTransform } from "framer-motion"

const x = useMotionValue(0)

// Linear interpolation
const opacity = useTransform(x, [0, 100], [1, 0])

// Custom transform function
const backgroundColor = useTransform(
  x,
  [0, 100],
  ["#ff0000", "#0000ff"]
)

<motion.div style={{ x, opacity, backgroundColor }} />
```

### useSpring

Create spring-animated motion value.

```typescript
import { useSpring, useMotionValue } from "framer-motion"

const x = useMotionValue(0)
const springX = useSpring(x, { stiffness: 300, damping: 20 })

<motion.div style={{ x: springX }} />
```

**Options:**
```typescript
interface SpringOptions {
  stiffness?: number
  damping?: number
  mass?: number
  velocity?: number
  restSpeed?: number
  restDelta?: number
}
```

### useScroll

Track scroll position and velocity.

```typescript
import { useScroll } from "framer-motion"

const { scrollX, scrollY, scrollXProgress, scrollYProgress } = useScroll()

// With element ref
const ref = useRef(null)
const { scrollYProgress } = useScroll({
  target: ref,
  offset: ["start end", "end start"]
})

<motion.div style={{ scaleX: scrollYProgress }} />
```

**Options:**
```typescript
interface ScrollOptions {
  target?: RefObject<Element>
  offset?: ["start" | "end" | string, "start" | "end" | string]
  container?: RefObject<Element>
  layoutEffect?: boolean
}
```

### useInView

Detect when element is in viewport.

```typescript
import { useInView } from "framer-motion"

const ref = useRef(null)
const isInView = useInView(ref, {
  once: true,
  amount: 0.5,
  margin: "-100px"
})

<div ref={ref}>
  {isInView ? "Visible!" : "Not visible"}
</div>
```

**Options:**
```typescript
interface InViewOptions {
  once?: boolean
  amount?: "some" | "all" | number
  margin?: string
  root?: RefObject<Element>
}
```

### useReducedMotion

Detect user's motion preferences.

```typescript
import { useReducedMotion } from "framer-motion"

const shouldReduceMotion = useReducedMotion()

<motion.div
  animate={{ x: 100 }}
  transition={shouldReduceMotion ? { duration: 0 } : { duration: 0.5 }}
/>
```

### useAnimationControls

Create animation controls for imperative animations.

```typescript
import { useAnimationControls } from "framer-motion"

const controls = useAnimationControls()

controls.start({ x: 100 })
controls.stop()
controls.set({ x: 0 })

<motion.div animate={controls} />
```

### usePresence

Detect if component is present (for custom exit animations).

```typescript
import { usePresence } from "framer-motion"

const [isPresent, safeToRemove] = usePresence()

useEffect(() => {
  if (!isPresent) {
    // Perform exit animation
    animate(ref.current, { opacity: 0 }).then(safeToRemove)
  }
}, [isPresent])
```

---

## AnimatePresence

Enables exit animations for removed components.

### Basic Usage

```typescript
import { AnimatePresence } from "framer-motion"

<AnimatePresence>
  {show && (
    <motion.div
      key="modal"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    />
  )}
</AnimatePresence>
```

### Props

```typescript
interface AnimatePresenceProps {
  // Initial animation on first mount
  initial?: boolean

  // Custom data for exit animations
  custom?: any

  // Wait for all exiting animations to complete
  mode?: "wait" | "sync" | "popLayout"

  // Callback when all exit animations complete
  onExitComplete?: () => void

  // Propagate exit to nested AnimatePresence
  propagate?: boolean
}
```

### Mode Options

**"sync"** (default) - Exit and enter animations happen simultaneously:
```typescript
<AnimatePresence mode="sync">
  <Component key={page} />
</AnimatePresence>
```

**"wait"** - Wait for exit animation before starting enter animation:
```typescript
<AnimatePresence mode="wait">
  <Component key={page} />
</AnimatePresence>
```

**"popLayout"** - Exit components render in a separate layer:
```typescript
<AnimatePresence mode="popLayout">
  {items.map(item => (
    <motion.div key={item.id} layout />
  ))}
</AnimatePresence>
```

### Custom Data

Pass data to exiting components that can't receive new props:

```typescript
<AnimatePresence custom={direction}>
  <motion.div
    key={page}
    variants={variants}
    custom={direction}
    exit="exit"
  />
</AnimatePresence>

const variants = {
  exit: (direction) => ({
    x: direction > 0 ? 300 : -300
  })
}
```

---

## Utilities

### stagger

Create staggered delays for child animations.

```typescript
import { stagger } from "framer-motion"

animate("li", { opacity: 1 }, { delay: stagger(0.1) })

// With options
stagger(0.1, {
  startDelay: 0.2,
  from: "first" | "last" | "center" | number,
  ease: "easeInOut"
})
```

### animate (standalone)

Animate any element imperatively.

```typescript
import { animate } from "framer-motion"

// Single element
animate(element, { x: 100 }, { duration: 0.5 })

// Selector
animate(".box", { opacity: 1 })

// Returns controls
const controls = animate(element, { x: 100 })
controls.pause()
```

### transform

Transform values without motion values.

```typescript
import { transform } from "framer-motion"

const output = transform(input, [0, 100], [0, 1])
```

### mix

Mix two values.

```typescript
import { mix } from "framer-motion"

const output = mix(0, 100, 0.5) // 50
```

### clamp

Clamp value between min and max.

```typescript
import { clamp } from "framer-motion"

const output = clamp(0, 100, 150) // 100
```

---

## Event Info Types

### PanInfo (Drag events)

```typescript
interface PanInfo {
  point: Point         // Page coordinates
  delta: Point         // Change since last event
  offset: Point        // Offset from gesture start
  velocity: Point      // Current velocity
}
```

### TapInfo

```typescript
interface TapInfo {
  point: Point         // Page coordinates
}
```

### Point

```typescript
interface Point {
  x: number
  y: number
}
```

---

## TypeScript Support

### Import Types

```typescript
import type {
  TargetAndTransition,
  Transition,
  Variants,
  MotionProps,
  AnimationControls,
  PanInfo,
  TapInfo
} from "framer-motion"
```

### Custom Component with Motion

```typescript
import { motion, HTMLMotionProps } from "framer-motion"

interface Props extends HTMLMotionProps<"div"> {
  customProp: string
}

const CustomComponent = ({ customProp, ...props }: Props) => {
  return <motion.div {...props}>{customProp}</motion.div>
}
```

---

## Performance Tips

1. **Use transform properties** (x, y, scale, rotate) - hardware accelerated
2. **Avoid animating** width, height, top, left, margin, padding
3. **Use `layout` sparingly** - computationally expensive
4. **Use `will-change` CSS** for complex animations
5. **Use `layoutId` only when needed** - tracks elements globally
6. **Reduce motion values** - each creates subscription overhead
7. **Use `useReducedMotion`** - respect accessibility preferences

---

## Common Patterns Quick Reference

```typescript
// Hover effect
<motion.div whileHover={{ scale: 1.1 }} />

// Tap feedback
<motion.button whileTap={{ scale: 0.95 }} />

// Drag
<motion.div drag dragConstraints={{ left: 0, right: 300 }} />

// Fade in on mount
<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} />

// Exit animation
<AnimatePresence>
  {show && <motion.div exit={{ opacity: 0 }} />}
</AnimatePresence>

// Layout animation
<motion.div layout />

// Shared layout animation
<motion.div layoutId="shared-element" />

// Scroll-triggered
<motion.div whileInView={{ opacity: 1 }} viewport={{ once: true }} />

// Stagger children
<motion.div variants={container}>
  <motion.div variants={item} />
  <motion.div variants={item} />
</motion.div>

// Spring animation
<motion.div
  animate={{ x: 100 }}
  transition={{ type: "spring", stiffness: 300 }}
/>
```

---

For more detailed examples and use cases, see the main SKILL.md and examples in the assets directory.



===== FILE: plugins/individual/motion-framer/agents/motion-framer-choreographer.md =====

# Framer Motion Animation Choreographer

## Role

Expert animation choreographer specializing in Framer Motion animation design, timing, and orchestration.

## Expertise

- Animation timing and easing
- Timeline sequencing
- Performance-optimized animations
- Cross-library animation integration
- Interactive animation patterns
- Scroll-driven animation design

## When to use

Activate this agent when working on:
- Complex animation sequences
- Multi-element choreography
- Scroll-triggered animations
- Interactive animation systems
- Animation performance optimization

## Approach

1. Understand animation goals and user experience
2. Design animation timing and sequencing
3. Implement using Framer Motion best practices
4. Optimize for smooth 60fps performance
5. Test across devices and browsers

## Tools

This agent has access to:
- Framer Motion skill knowledge
- Animation pattern libraries
- Performance optimization techniques
- Timeline management strategies



===== FILE: plugins/individual/motion-framer/commands/animation_generator.md =====

# /motion-framer-animation_generator

Framer Motion - Animation Generator

## Description

Executes the animation_generator script for Framer Motion.

## Usage

```bash
/motion-framer-animation_generator
```

## Implementation

This command runs the `animation_generator.py` script from the Framer Motion skill, which provides automated assistance for animation generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/motion-framer/commands/variant_builder.md =====

# /motion-framer-variant_builder

Framer Motion - Variant Builder

## Description

Executes the variant_builder script for Framer Motion.

## Usage

```bash
/motion-framer-variant_builder
```

## Implementation

This command runs the `variant_builder.py` script from the Framer Motion skill, which provides automated assistance for variant builder.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/motion-framer/skills/motion-framer/scripts/animation_generator.py =====

```py
#!/usr/bin/env python3
"""
Motion/Framer Motion Animation Generator
=========================================

Generate Motion component boilerplate for common animation patterns.

Usage:
    python3 animation_generator.py --type hover --name Button --output Button.jsx
    python3 animation_generator.py --type exit --name Modal --typescript
    python3 animation_generator.py --type drag --name Card --constraints
    python3 animation_generator.py --type layout --name Grid --shared-id

Animation Types:
    - hover: Hover animation with whileHover
    - tap: Tap animation with whileTap
    - drag: Draggable component with constraints
    - exit: Exit animation with AnimatePresence
    - layout: Layout animation with layout prop
    - scroll: Scroll-triggered animation with whileInView
    - spring: Spring physics animation
    - stagger: Staggered children animation
    - gesture: Combined gestures (hover + tap + drag)
    - variant: Variant-based animation system
    - custom: Custom template

Options:
    --type: Animation type (required)
    --name: Component name (default: Component)
    --output: Output file path (default: stdout)
    --typescript: Generate TypeScript component
    --constraints: Add drag constraints (for drag type)
    --shared-id: Add layoutId for shared animations
    --spring: Use spring physics for transitions
"""

import argparse
import sys
from typing import Optional, List


class MotionAnimationGenerator:
    """Generate Motion/Framer Motion animation boilerplate."""

    def __init__(
        self,
        animation_type: str,
        name: str = "Component",
        typescript: bool = False,
        constraints: bool = False,
        shared_id: Optional[str] = None,
        spring: bool = False,
    ):
        self.animation_type = animation_type
        self.name = name
        self.typescript = typescript
        self.constraints = constraints
        self.shared_id = shared_id
        self.spring = spring

    def generate(self) -> str:
        """Generate animation component code."""
        generators = {
            'hover': self._generate_hover,
            'tap': self._generate_tap,
            'drag': self._generate_drag,
            'exit': self._generate_exit,
            'layout': self._generate_layout,
            'scroll': self._generate_scroll,
            'spring': self._generate_spring,
            'stagger': self._generate_stagger,
            'gesture': self._generate_gesture,
            'variant': self._generate_variant,
            'custom': self._generate_custom,
        }

        generator = generators.get(self.animation_type)
        if not generator:
            raise ValueError(f"Unknown animation type: {self.animation_type}")

        return generator()

    def _get_imports(self, needs_presence: bool = False, needs_hooks: bool = False) -> str:
        """Generate import statements."""
        imports = ["import { motion"]

        if needs_presence:
            imports[0] += ", AnimatePresence"

        imports[0] += " } from 'framer-motion'"

        if needs_hooks:
            imports.append("import { useState } from 'react'")

        if self.typescript:
            imports.append("import type { Variants } from 'framer-motion'")

        return "\n".join(imports)

    def _get_props_interface(self) -> str:
        """Generate TypeScript props interface."""
        if not self.typescript:
            return ""

        return f"""
interface {self.name}Props {{
  children?: React.ReactNode
}}
"""

    def _generate_hover(self) -> str:
        """Generate hover animation component."""
        imports = self._get_imports()
        props_interface = self._get_props_interface()
        props_sig = f"({{ children }}: {self.name}Props)" if self.typescript else "({ children })"

        transition = "{ type: 'spring', stiffness: 300, damping: 20 }" if self.spring else "{ duration: 0.2 }"

        return f"""{imports}
{props_interface}
export function {self.name}{props_sig} {{
  return (
    <motion.div
      whileHover={{{{
        scale: 1.05,
        transition: {transition}
      }}}}
      transition={{{{ duration: 0.3 }}}}
    >
      {{children}}
    </motion.div>
  )
}}
"""

    def _generate_tap(self) -> str:
        """Generate tap animation component."""
        imports = self._get_imports()
        props_interface = self._get_props_interface()
        props_sig = f"({{ children }}: {self.name}Props)" if self.typescript else "({ children })"

        return f"""{imports}
{props_interface}
export function {self.name}{props_sig} {{
  return (
    <motion.button
      whileHover={{{{ scale: 1.05 }}}}
      whileTap={{{{ scale: 0.95, rotate: 2 }}}}
      transition={{{{ type: 'spring', stiffness: 400, damping: 17 }}}}
    >
      {{children}}
    </motion.button>
  )
}}
"""

    def _generate_drag(self) -> str:
        """Generate drag animation component."""
        imports = self._get_imports()
        props_interface = self._get_props_interface()
        props_sig = f"({{ children }}: {self.name}Props)" if self.typescript else "({ children })"

        constraints_code = ""
        if self.constraints:
            constraints_code = """
      dragConstraints={{{{ left: -100, right: 100, top: -100, bottom: 100 }}}}
      dragElastic={{0.1}}"""

        return f"""{imports}
{props_interface}
export function {self.name}{props_sig} {{
  return (
    <motion.div
      drag{constraints_code}
      whileDrag={{{{
        scale: 1.1,
        cursor: 'grabbing',
        boxShadow: '0px 10px 30px rgba(0, 0, 0, 0.3)'
      }}}}
      dragTransition={{{{ bounceStiffness: 600, bounceDamping: 20 }}}}
    >
      {{children}}
    </motion.div>
  )
}}
"""

    def _generate_exit(self) -> str:
        """Generate exit animation with AnimatePresence."""
        imports = self._get_imports(needs_presence=True, needs_hooks=True)
        props_interface = self._get_props_interface()

        return f"""{imports}
{props_interface}
export function {self.name}({{ children }}{': ' + self.name + 'Props' if self.typescript else ''}) {{
  const [isVisible, setIsVisible] = useState(true)

  return (
    <>
      <button onClick={{() => setIsVisible(!isVisible)}}>
        Toggle
      </button>

      <AnimatePresence mode="wait">
        {{isVisible && (
          <motion.div
            key="content"
            initial={{{{ opacity: 0, y: 20 }}}}
            animate={{{{ opacity: 1, y: 0 }}}}
            exit={{{{ opacity: 0, y: -20 }}}}
            transition={{{{ duration: 0.3 }}}}
          >
            {{children}}
          </motion.div>
        )}}
      </AnimatePresence>
    </>
  )
}}
"""

    def _generate_layout(self) -> str:
        """Generate layout animation component."""
        imports = self._get_imports(needs_hooks=True)
        props_interface = self._get_props_interface()

        layout_id = f'layoutId="{self.shared_id}"' if self.shared_id else ""

        return f"""{imports}
{props_interface}
export function {self.name}({{ children }}{': ' + self.name + 'Props' if self.typescript else ''}) {{
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <motion.div
      layout
      {layout_id}
      onClick={{() => setIsExpanded(!isExpanded)}}
      style={{{{
        width: isExpanded ? '400px' : '200px',
        height: isExpanded ? '300px' : '150px',
        borderRadius: '12px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        cursor: 'pointer',
        padding: '20px'
      }}}}
      transition={{{{
        layout: {{{{ duration: 0.3, ease: 'easeInOut' }}}}
      }}}}
    >
      <motion.div layout="position">
        {{children}}
      </motion.div>
    </motion.div>
  )
}}
"""

    def _generate_scroll(self) -> str:
        """Generate scroll-triggered animation."""
        imports = self._get_imports()
        props_interface = self._get_props_interface()
        props_sig = f"({{ children }}: {self.name}Props)" if self.typescript else "({ children })"

        return f"""{imports}
{props_interface}
export function {self.name}{props_sig} {{
  return (
    <motion.div
      initial={{{{ opacity: 0, y: 50 }}}}
      whileInView={{{{ opacity: 1, y: 0 }}}}
      viewport={{{{ once: true, amount: 0.3 }}}}
      transition={{{{ duration: 0.5, ease: 'easeOut' }}}}
    >
      {{children}}
    </motion.div>
  )
}}
"""

    def _generate_spring(self) -> str:
        """Generate spring physics animation."""
        imports = self._get_imports(needs_hooks=True)
        props_interface = self._get_props_interface()

        return f"""{imports}
{props_interface}
export function {self.name}({{ children }}{': ' + self.name + 'Props' if self.typescript else ''}) {{
  const [isActive, setIsActive] = useState(false)

  return (
    <motion.div
      animate={{{{
        scale: isActive ? 1.2 : 1,
        rotate: isActive ? 5 : 0
      }}}}
      transition={{{{
        type: 'spring',
        stiffness: 300,
        damping: 20,
        mass: 1
      }}}}
      onClick={{() => setIsActive(!isActive)}}
    >
      {{children}}
    </motion.div>
  )
}}
"""

    def _generate_stagger(self) -> str:
        """Generate staggered children animation."""
        imports = self._get_imports()
        if self.typescript:
            imports = self._get_imports() + "\nimport type { Variants } from 'framer-motion'"

        variants = "Variants" if self.typescript else ""

        return f"""{imports}

const container{': ' + variants if variants else ''} = {{
  hidden: {{{{ opacity: 0 }}}},
  visible: {{{{
    opacity: 1,
    transition: {{{{
      staggerChildren: 0.1,
      delayChildren: 0.2
    }}}}
  }}}}
}}

const item{': ' + variants if variants else ''} = {{
  hidden: {{{{ opacity: 0, y: 20 }}}},
  visible: {{{{
    opacity: 1,
    y: 0,
    transition: {{{{ duration: 0.5 }}}}
  }}}}
}}

export function {self.name}() {{
  const items = ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']

  return (
    <motion.ul
      variants={{container}}
      initial="hidden"
      animate="visible"
      style={{{{ listStyle: 'none', padding: 0 }}}}
    >
      {{items.map((text, index) => (
        <motion.li
          key={{index}}
          variants={{item}}
          style={{{{
            padding: '20px',
            marginBottom: '10px',
            background: '#f0f0f0',
            borderRadius: '8px'
          }}}}
        >
          {{text}}
        </motion.li>
      ))}}
    </motion.ul>
  )
}}
"""

    def _generate_gesture(self) -> str:
        """Generate combined gesture component."""
        imports = self._get_imports(needs_hooks=True)
        props_interface = self._get_props_interface()

        return f"""{imports}
{props_interface}
export function {self.name}({{ children }}{': ' + self.name + 'Props' if self.typescript else ''}) {{
  const [isDragging, setIsDragging] = useState(false)

  return (
    <motion.div
      drag
      dragConstraints={{{{ left: 0, right: 300, top: 0, bottom: 300 }}}}
      whileHover={{{{ scale: 1.05 }}}}
      whileTap={{{{ scale: 0.95 }}}}
      whileDrag={{{{ scale: 1.1, cursor: 'grabbing' }}}}
      onDragStart={{() => setIsDragging(true)}}
      onDragEnd={{() => setIsDragging(false)}}
      style={{{{
        width: '150px',
        height: '150px',
        background: isDragging ? '#667eea' : '#764ba2',
        borderRadius: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'grab',
        userSelect: 'none'
      }}}}
    >
      {{children}}
    </motion.div>
  )
}}
"""

    def _generate_variant(self) -> str:
        """Generate variant-based animation system."""
        imports = self._get_imports(needs_hooks=True)
        if self.typescript:
            imports += "\nimport type { Variants } from 'framer-motion'"

        variants_type = ": Variants" if self.typescript else ""

        return f"""{imports}

const variants{variants_type} = {{
  inactive: {{
    scale: 1,
    backgroundColor: '#cccccc',
    transition: {{{{ duration: 0.3 }}}}
  }},
  active: {{
    scale: 1.1,
    backgroundColor: '#667eea',
    transition: {{{{ type: 'spring', stiffness: 300, damping: 20 }}}}
  }},
  complete: {{
    scale: 1,
    backgroundColor: '#10b981',
    transition: {{{{ duration: 0.3 }}}}
  }}
}}

export function {self.name}() {{
  const [status, setStatus] = useState<'inactive' | 'active' | 'complete'>('inactive')

  const handleClick = () => {{
    if (status === 'inactive') {{
      setStatus('active')
      setTimeout(() => setStatus('complete'), 1000)
    }} else {{
      setStatus('inactive')
    }}
  }}

  return (
    <motion.div
      variants={{variants}}
      animate={{status}}
      onClick={{handleClick}}
      style={{{{
        width: '200px',
        height: '60px',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        color: 'white',
        fontWeight: 'bold'
      }}}}
    >
      {{status.toUpperCase()}}
    </motion.div>
  )
}}
"""

    def _generate_custom(self) -> str:
        """Generate custom template."""
        imports = self._get_imports()
        props_interface = self._get_props_interface()
        props_sig = f"({{ children }}: {self.name}Props)" if self.typescript else "({ children })"

        return f"""{imports}
{props_interface}
export function {self.name}{props_sig} {{
  return (
    <motion.div
      initial={{{{ opacity: 0 }}}}
      animate={{{{ opacity: 1 }}}}
      transition={{{{ duration: 0.5 }}}}
    >
      {{children}}
    </motion.div>
  )
}}
"""


def main():
    parser = argparse.ArgumentParser(
        description='Generate Motion/Framer Motion animation boilerplate',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--type',
        required=True,
        choices=['hover', 'tap', 'drag', 'exit', 'layout', 'scroll',
                 'spring', 'stagger', 'gesture', 'variant', 'custom'],
        help='Animation type to generate'
    )

    parser.add_argument(
        '--name',
        default='Component',
        help='Component name (default: Component)'
    )

    parser.add_argument(
        '--output',
        help='Output file path (default: stdout)'
    )

    parser.add_argument(
        '--typescript',
        action='store_true',
        help='Generate TypeScript component'
    )

    parser.add_argument(
        '--constraints',
        action='store_true',
        help='Add drag constraints (for drag type)'
    )

    parser.add_argument(
        '--shared-id',
        help='Add layoutId for shared animations'
    )

    parser.add_argument(
        '--spring',
        action='store_true',
        help='Use spring physics for transitions'
    )

    args = parser.parse_args()

    # Generate animation
    generator = MotionAnimationGenerator(
        animation_type=args.type,
        name=args.name,
        typescript=args.typescript,
        constraints=args.constraints,
        shared_id=args.shared_id,
        spring=args.spring,
    )

    try:
        code = generator.generate()

        # Output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(code)
            print(f"✅ Generated {args.name} component → {args.output}")
        else:
            print(code)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/motion-framer/skills/motion-framer/scripts/variant_builder.py =====

```py
#!/usr/bin/env python3
"""
Motion Variant Builder
======================

Interactive CLI tool to build Motion/Framer Motion variant configurations.

Usage:
    python3 variant_builder.py
    python3 variant_builder.py --preset fade --output variants.js
    python3 variant_builder.py --typescript

Presets:
    - fade: Fade in/out animation
    - slide: Slide animation (left, right, up, down)
    - scale: Scale animation
    - rotate: Rotation animation
    - stagger: Staggered children animation
    - modal: Modal enter/exit animation
    - page: Page transition animation
    - custom: Build from scratch

Features:
    - Interactive CLI for building variants
    - Multiple animation states
    - Transition configurations
    - Stagger settings for children
    - TypeScript support
    - Code generation
"""

import argparse
import sys
import json
from typing import Dict, List, Optional, Any


class VariantBuilder:
    """Build Motion variant configurations interactively."""

    PRESETS = {
        'fade': {
            'hidden': {
                'opacity': 0
            },
            'visible': {
                'opacity': 1,
                'transition': {'duration': 0.5}
            }
        },
        'slide': {
            'hidden': {
                'opacity': 0,
                'x': -100
            },
            'visible': {
                'opacity': 1,
                'x': 0,
                'transition': {'type': 'spring', 'stiffness': 300, 'damping': 30}
            }
        },
        'scale': {
            'hidden': {
                'opacity': 0,
                'scale': 0.8
            },
            'visible': {
                'opacity': 1,
                'scale': 1,
                'transition': {'duration': 0.3}
            }
        },
        'rotate': {
            'hidden': {
                'opacity': 0,
                'rotate': -180
            },
            'visible': {
                'opacity': 1,
                'rotate': 0,
                'transition': {'type': 'spring', 'stiffness': 200, 'damping': 20}
            }
        },
        'stagger': {
            'hidden': {
                'opacity': 0
            },
            'visible': {
                'opacity': 1,
                'transition': {
                    'staggerChildren': 0.1,
                    'delayChildren': 0.2
                }
            }
        },
        'modal': {
            'hidden': {
                'opacity': 0,
                'scale': 0.9,
                'y': 20
            },
            'visible': {
                'opacity': 1,
                'scale': 1,
                'y': 0,
                'transition': {
                    'type': 'spring',
                    'stiffness': 300,
                    'damping': 30
                }
            },
            'exit': {
                'opacity': 0,
                'scale': 0.9,
                'y': -20,
                'transition': {'duration': 0.2}
            }
        },
        'page': {
            'initial': {
                'opacity': 0,
                'x': 300
            },
            'in': {
                'opacity': 1,
                'x': 0,
                'transition': {'duration': 0.3}
            },
            'out': {
                'opacity': 0,
                'x': -300,
                'transition': {'duration': 0.3}
            }
        }
    }

    def __init__(self, preset: Optional[str] = None, typescript: bool = False):
        self.variants: Dict[str, Dict[str, Any]] = {}
        self.typescript = typescript

        if preset and preset in self.PRESETS:
            self.variants = self.PRESETS[preset].copy()

    def add_state(self, name: str, properties: Dict[str, Any]) -> None:
        """Add a variant state."""
        self.variants[name] = properties

    def generate_code(self) -> str:
        """Generate variant code."""
        if self.typescript:
            return self._generate_typescript()
        else:
            return self._generate_javascript()

    def _generate_javascript(self) -> str:
        """Generate JavaScript variant code."""
        code = "const variants = {\n"

        for state_name, properties in self.variants.items():
            code += f"  {state_name}: {{\n"
            code += self._format_properties(properties, indent=4)
            code += "  },\n"

        code += "}\n\nexport default variants"
        return code

    def _generate_typescript(self) -> str:
        """Generate TypeScript variant code."""
        code = "import type { Variants } from 'framer-motion'\n\n"
        code += "const variants: Variants = {\n"

        for state_name, properties in self.variants.items():
            code += f"  {state_name}: {{\n"
            code += self._format_properties(properties, indent=4)
            code += "  },\n"

        code += "}\n\nexport default variants"
        return code

    def _format_properties(self, properties: Dict[str, Any], indent: int = 0) -> str:
        """Format properties as JavaScript object."""
        lines = []
        indent_str = " " * indent

        for key, value in properties.items():
            if isinstance(value, dict):
                lines.append(f"{indent_str}{key}: {{")
                lines.append(self._format_properties(value, indent + 2).rstrip())
                lines.append(f"{indent_str}}},")
            elif isinstance(value, str):
                lines.append(f"{indent_str}{key}: '{value}',")
            elif isinstance(value, bool):
                lines.append(f"{indent_str}{key}: {str(value).lower()},")
            else:
                lines.append(f"{indent_str}{key}: {value},")

        return "\n".join(lines) + "\n"

    def interactive_build(self) -> None:
        """Interactive CLI for building variants."""
        print("\n🎨 Motion Variant Builder - Interactive Mode\n")
        print("=" * 60)

        # Choose preset or custom
        print("\nChoose a starting point:")
        print("  1. fade        - Simple fade in/out")
        print("  2. slide       - Slide animation")
        print("  3. scale       - Scale animation")
        print("  4. rotate      - Rotation animation")
        print("  5. stagger     - Staggered children")
        print("  6. modal       - Modal enter/exit")
        print("  7. page        - Page transition")
        print("  8. custom      - Build from scratch")

        choice = input("\nSelect preset (1-8): ").strip()

        preset_map = {
            '1': 'fade',
            '2': 'slide',
            '3': 'scale',
            '4': 'rotate',
            '5': 'stagger',
            '6': 'modal',
            '7': 'page',
        }

        if choice in preset_map:
            preset = preset_map[choice]
            self.variants = self.PRESETS[preset].copy()
            print(f"\n✅ Loaded '{preset}' preset")
        else:
            print("\n📝 Building custom variants...")

        # Add/modify states
        while True:
            print("\n" + "=" * 60)
            print("Current variants:")
            for state_name in self.variants.keys():
                print(f"  - {state_name}")

            print("\nOptions:")
            print("  1. Add new state")
            print("  2. Modify existing state")
            print("  3. Remove state")
            print("  4. Preview code")
            print("  5. Done")

            option = input("\nChoose option (1-5): ").strip()

            if option == '1':
                self._add_state_interactive()
            elif option == '2':
                self._modify_state_interactive()
            elif option == '3':
                self._remove_state_interactive()
            elif option == '4':
                print("\n" + "=" * 60)
                print("Generated Code:")
                print("=" * 60)
                print(self.generate_code())
            elif option == '5':
                break

    def _add_state_interactive(self) -> None:
        """Add state interactively."""
        print("\n📝 Add New State")
        state_name = input("State name (e.g., 'hidden', 'visible', 'exit'): ").strip()

        if not state_name:
            print("❌ Invalid state name")
            return

        properties = self._build_properties_interactive()
        self.variants[state_name] = properties
        print(f"✅ Added state '{state_name}'")

    def _modify_state_interactive(self) -> None:
        """Modify state interactively."""
        if not self.variants:
            print("❌ No states to modify")
            return

        print("\n✏️  Modify State")
        print("Available states:")
        for i, name in enumerate(self.variants.keys(), 1):
            print(f"  {i}. {name}")

        choice = input("\nSelect state number: ").strip()
        try:
            state_name = list(self.variants.keys())[int(choice) - 1]
            print(f"\nModifying '{state_name}'...")
            properties = self._build_properties_interactive()
            self.variants[state_name] = properties
            print(f"✅ Modified state '{state_name}'")
        except (ValueError, IndexError):
            print("❌ Invalid selection")

    def _remove_state_interactive(self) -> None:
        """Remove state interactively."""
        if not self.variants:
            print("❌ No states to remove")
            return

        print("\n🗑️  Remove State")
        print("Available states:")
        for i, name in enumerate(self.variants.keys(), 1):
            print(f"  {i}. {name}")

        choice = input("\nSelect state number: ").strip()
        try:
            state_name = list(self.variants.keys())[int(choice) - 1]
            del self.variants[state_name]
            print(f"✅ Removed state '{state_name}'")
        except (ValueError, IndexError):
            print("❌ Invalid selection")

    def _build_properties_interactive(self) -> Dict[str, Any]:
        """Build properties interactively."""
        properties = {}

        print("\nAdd properties (leave empty to skip):")

        # Common animation properties
        opacity = input("  opacity (0-1): ").strip()
        if opacity:
            properties['opacity'] = float(opacity)

        x = input("  x position (px): ").strip()
        if x:
            properties['x'] = int(x)

        y = input("  y position (px): ").strip()
        if y:
            properties['y'] = int(y)

        scale = input("  scale (0-n): ").strip()
        if scale:
            properties['scale'] = float(scale)

        rotate = input("  rotate (degrees): ").strip()
        if rotate:
            properties['rotate'] = int(rotate)

        # Transition
        add_transition = input("\nAdd transition? (y/n): ").strip().lower()
        if add_transition == 'y':
            transition = self._build_transition_interactive()
            if transition:
                properties['transition'] = transition

        return properties

    def _build_transition_interactive(self) -> Dict[str, Any]:
        """Build transition interactively."""
        transition = {}

        print("\nTransition type:")
        print("  1. tween (duration-based)")
        print("  2. spring (physics-based)")
        print("  3. stagger (for children)")

        choice = input("Select type (1-3): ").strip()

        if choice == '1':
            duration = input("  duration (seconds): ").strip()
            if duration:
                transition['duration'] = float(duration)

            ease = input("  ease (linear/easeIn/easeOut/easeInOut): ").strip()
            if ease:
                transition['ease'] = ease

        elif choice == '2':
            transition['type'] = 'spring'

            stiffness = input("  stiffness (default 100): ").strip()
            if stiffness:
                transition['stiffness'] = int(stiffness)

            damping = input("  damping (default 10): ").strip()
            if damping:
                transition['damping'] = int(damping)

        elif choice == '3':
            stagger = input("  staggerChildren (seconds): ").strip()
            if stagger:
                transition['staggerChildren'] = float(stagger)

            delay = input("  delayChildren (seconds): ").strip()
            if delay:
                transition['delayChildren'] = float(delay)

        return transition


def main():
    parser = argparse.ArgumentParser(
        description='Build Motion variant configurations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--preset',
        choices=['fade', 'slide', 'scale', 'rotate', 'stagger', 'modal', 'page'],
        help='Use a preset variant configuration'
    )

    parser.add_argument(
        '--output',
        help='Output file path (default: stdout)'
    )

    parser.add_argument(
        '--typescript',
        action='store_true',
        help='Generate TypeScript code'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )

    args = parser.parse_args()

    # Create builder
    builder = VariantBuilder(preset=args.preset, typescript=args.typescript)

    # Run interactive mode if requested or no preset given
    if args.interactive or (not args.preset and len(sys.argv) == 1):
        builder.interactive_build()

    # Generate code
    if builder.variants:
        code = builder.generate_code()

        # Output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(code)
            print(f"\n✅ Variants generated → {args.output}")
        else:
            print("\n" + "=" * 60)
            print("Generated Code:")
            print("=" * 60)
            print(code)
    else:
        print("❌ No variants to generate")
        sys.exit(1)


if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/motion-framer/skills/motion-framer/assets/examples/README.md =====

# Motion / Framer Motion Examples

Comprehensive collection of real-world animation patterns, production-ready components, and advanced techniques for building animated React applications.

## Table of Contents

- [Page Transitions](#page-transitions)
- [Route Animations](#route-animations)
- [Complex Gestures](#complex-gestures)
- [Scroll-Based Animations](#scroll-based-animations)
- [Advanced Layout Animations](#advanced-layout-animations)
- [Shared Element Transitions](#shared-element-transitions)
- [Modal & Dialog Patterns](#modal--dialog-patterns)
- [Form Animations](#form-animations)
- [Loading States](#loading-states)
- [List Animations](#list-animations)
- [Image Galleries](#image-galleries)
- [Navigation Menus](#navigation-menus)
- [Performance Optimization](#performance-optimization)

---

## Page Transitions

### Full Page Fade

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useLocation } from 'react-router-dom'

function PageTransition({ children }) {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

### Slide Transition

```jsx
function SlidePageTransition({ children }) {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ x: 300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: -300, opacity: 0 }}
        transition={{ type: 'spring', stiffness: 260, damping: 20 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

### Depth Transition (Scale + Blur)

```jsx
function DepthPageTransition({ children }) {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ scale: 0.8, opacity: 0, filter: 'blur(10px)' }}
        animate={{ scale: 1, opacity: 1, filter: 'blur(0px)' }}
        exit={{ scale: 1.2, opacity: 0, filter: 'blur(10px)' }}
        transition={{ duration: 0.5 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

### Stack Navigation

```jsx
import { useState } from 'react'

function StackNavigation() {
  const [stack, setStack] = useState([{ id: 0, component: 'Home' }])

  const push = (component) => {
    setStack([...stack, { id: stack.length, component }])
  }

  const pop = () => {
    if (stack.length > 1) {
      setStack(stack.slice(0, -1))
    }
  }

  const currentPage = stack[stack.length - 1]

  return (
    <div style={{ position: 'relative', overflow: 'hidden' }}>
      <AnimatePresence mode="popLayout">
        {stack.map((page, index) => (
          <motion.div
            key={page.id}
            initial={{ x: '100%' }}
            animate={{
              x: index === stack.length - 1 ? 0 : '-20%',
              scale: index === stack.length - 1 ? 1 : 0.95,
              opacity: index === stack.length - 1 ? 1 : 0.5
            }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            style={{
              position: index === stack.length - 1 ? 'relative' : 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0
            }}
          >
            <PageComponent name={page.component} onPush={push} onPop={pop} />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
```

---

## Route Animations

### Custom Route Transition with Direction Detection

```jsx
import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'

const routeOrder = ['/', '/about', '/services', '/contact']

function DirectionalRouteTransition({ children }) {
  const location = useLocation()
  const [direction, setDirection] = useState(0)

  useEffect(() => {
    const currentIndex = routeOrder.indexOf(location.pathname)
    const prevIndex = routeOrder.indexOf(sessionStorage.getItem('prevPath') || '/')

    setDirection(currentIndex > prevIndex ? 1 : -1)
    sessionStorage.setItem('prevPath', location.pathname)
  }, [location])

  return (
    <AnimatePresence mode="wait" custom={direction}>
      <motion.div
        key={location.pathname}
        custom={direction}
        initial={(direction) => ({
          x: direction > 0 ? 300 : -300,
          opacity: 0
        })}
        animate={{ x: 0, opacity: 1 }}
        exit={(direction) => ({
          x: direction > 0 ? -300 : 300,
          opacity: 0
        })}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

### Multi-Stage Route Transition

```jsx
function MultiStageTransition({ children }) {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 20 }}
        animate={{
          opacity: [0, 1, 1],
          y: [20, 0, 0],
          scale: [0.95, 1.02, 1]
        }}
        exit={{
          opacity: [1, 0],
          scale: [1, 0.95]
        }}
        transition={{
          duration: 0.6,
          times: [0, 0.5, 1]
        }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

---

## Complex Gestures

### Multi-Direction Swipe Handler

```jsx
import { motion, useMotionValue, useTransform, PanInfo } from 'framer-motion'

function SwipeCard() {
  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const rotateX = useTransform(y, [-200, 200], [15, -15])
  const rotateY = useTransform(x, [-200, 200], [-15, 15])

  function handleDragEnd(event: MouseEvent, info: PanInfo) {
    const threshold = 100

    if (Math.abs(info.offset.x) > threshold) {
      // Swipe left or right
      console.log(info.offset.x > 0 ? 'Swiped right' : 'Swiped left')
    } else if (Math.abs(info.offset.y) > threshold) {
      // Swipe up or down
      console.log(info.offset.y > 0 ? 'Swiped down' : 'Swiped up')
    }
  }

  return (
    <motion.div
      drag
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragElastic={0.7}
      onDragEnd={handleDragEnd}
      style={{
        x,
        y,
        rotateX,
        rotateY,
        width: 300,
        height: 400,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: 20,
        cursor: 'grab'
      }}
      whileTap={{ cursor: 'grabbing' }}
    />
  )
}
```

### Long Press Gesture

```jsx
import { motion } from 'framer-motion'
import { useState, useRef } from 'react'

function LongPressButton({ onLongPress, children }) {
  const [isPressed, setIsPressed] = useState(false)
  const timerRef = useRef(null)

  const handlePressStart = () => {
    setIsPressed(true)
    timerRef.current = setTimeout(() => {
      onLongPress()
      setIsPressed(false)
    }, 800)
  }

  const handlePressEnd = () => {
    setIsPressed(false)
    if (timerRef.current) {
      clearTimeout(timerRef.current)
    }
  }

  return (
    <motion.button
      onMouseDown={handlePressStart}
      onMouseUp={handlePressEnd}
      onMouseLeave={handlePressEnd}
      onTouchStart={handlePressStart}
      onTouchEnd={handlePressEnd}
      animate={{
        scale: isPressed ? 0.95 : 1,
        boxShadow: isPressed
          ? '0 0 0 4px rgba(99, 102, 241, 0.3)'
          : '0 0 0 0px rgba(99, 102, 241, 0)'
      }}
      transition={{ duration: 0.2 }}
      style={{
        padding: '12px 24px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        border: 'none',
        borderRadius: 8,
        cursor: 'pointer',
        position: 'relative'
      }}
    >
      {children}
      {isPressed && (
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 0.8 }}
          style={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: 3,
            background: 'white',
            transformOrigin: 'left'
          }}
        />
      )}
    </motion.button>
  )
}
```

### Pinch to Zoom

```jsx
import { motion, useMotionValue, useTransform } from 'framer-motion'
import { useEffect, useRef } from 'react'

function PinchZoomImage({ src }) {
  const scale = useMotionValue(1)
  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const containerRef = useRef(null)

  useEffect(() => {
    const element = containerRef.current
    if (!element) return

    let initialDistance = 0

    const handleTouchStart = (e: TouchEvent) => {
      if (e.touches.length === 2) {
        const touch1 = e.touches[0]
        const touch2 = e.touches[1]
        initialDistance = Math.hypot(
          touch2.clientX - touch1.clientX,
          touch2.clientY - touch1.clientY
        )
      }
    }

    const handleTouchMove = (e: TouchEvent) => {
      if (e.touches.length === 2) {
        e.preventDefault()
        const touch1 = e.touches[0]
        const touch2 = e.touches[1]
        const currentDistance = Math.hypot(
          touch2.clientX - touch1.clientX,
          touch2.clientY - touch1.clientY
        )

        const newScale = (currentDistance / initialDistance) * scale.get()
        scale.set(Math.min(Math.max(newScale, 0.5), 3))
      }
    }

    element.addEventListener('touchstart', handleTouchStart)
    element.addEventListener('touchmove', handleTouchMove)

    return () => {
      element.removeEventListener('touchstart', handleTouchStart)
      element.removeEventListener('touchmove', handleTouchMove)
    }
  }, [])

  return (
    <div ref={containerRef} style={{ overflow: 'hidden', touchAction: 'none' }}>
      <motion.img
        src={src}
        drag
        dragConstraints={containerRef}
        style={{
          scale,
          x,
          y,
          maxWidth: '100%',
          cursor: 'grab'
        }}
        whileTap={{ cursor: 'grabbing' }}
      />
    </div>
  )
}
```

---

## Scroll-Based Animations

### Parallax Scrolling

```jsx
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

function ParallaxSection() {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start']
  })

  const y = useTransform(scrollYProgress, [0, 1], ['-20%', '20%'])
  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [0, 1, 0])

  return (
    <div ref={ref} style={{ height: '100vh', position: 'relative', overflow: 'hidden' }}>
      <motion.div
        style={{
          y,
          opacity,
          position: 'absolute',
          inset: 0,
          backgroundImage: 'url(/hero-bg.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      />
      <div style={{ position: 'relative', zIndex: 1 }}>
        <h1>Parallax Content</h1>
      </div>
    </div>
  )
}
```

### Scroll Progress Indicator

```jsx
import { motion, useScroll } from 'framer-motion'

function ScrollProgressBar() {
  const { scrollYProgress } = useScroll()

  return (
    <motion.div
      style={{
        scaleX: scrollYProgress,
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: 4,
        background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
        transformOrigin: 'left',
        zIndex: 9999
      }}
    />
  )
}
```

### Scroll-Triggered Animation Sequence

```jsx
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

function ScrollSequence() {
  const containerRef = useRef(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start end', 'end start']
  })

  const scale1 = useTransform(scrollYProgress, [0, 0.3], [0.8, 1])
  const scale2 = useTransform(scrollYProgress, [0.2, 0.5], [0.8, 1])
  const scale3 = useTransform(scrollYProgress, [0.4, 0.7], [0.8, 1])
  const scale4 = useTransform(scrollYProgress, [0.6, 0.9], [0.8, 1])

  const opacity1 = useTransform(scrollYProgress, [0, 0.3], [0, 1])
  const opacity2 = useTransform(scrollYProgress, [0.2, 0.5], [0, 1])
  const opacity3 = useTransform(scrollYProgress, [0.4, 0.7], [0, 1])
  const opacity4 = useTransform(scrollYProgress, [0.6, 0.9], [0, 1])

  return (
    <div ref={containerRef} style={{ minHeight: '200vh', padding: '50vh 0' }}>
      <motion.div style={{ scale: scale1, opacity: opacity1 }}>
        <h2>Step 1</h2>
      </motion.div>
      <motion.div style={{ scale: scale2, opacity: opacity2 }}>
        <h2>Step 2</h2>
      </motion.div>
      <motion.div style={{ scale: scale3, opacity: opacity3 }}>
        <h2>Step 3</h2>
      </motion.div>
      <motion.div style={{ scale: scale4, opacity: opacity4 }}>
        <h2>Step 4</h2>
      </motion.div>
    </div>
  )
}
```

### Scroll-Based Counter

```jsx
import { motion, useScroll, useTransform, useSpring } from 'framer-motion'
import { useRef } from 'react'

function AnimatedCounter({ from = 0, to = 100 }) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end center']
  })

  const count = useTransform(scrollYProgress, [0, 1], [from, to])
  const roundedCount = useTransform(count, Math.round)
  const smoothCount = useSpring(roundedCount, { stiffness: 100, damping: 20 })

  return (
    <div ref={ref} style={{ minHeight: '50vh', display: 'flex', alignItems: 'center' }}>
      <motion.span style={{ fontSize: '4rem', fontWeight: 'bold' }}>
        {smoothCount}
      </motion.span>
    </div>
  )
}
```

### Sticky Scroll Sections

```jsx
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'

function StickyScrollSection() {
  const containerRef = useRef(null)
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end']
  })

  const sections = [
    { title: 'Introduction', color: '#667eea' },
    { title: 'Features', color: '#764ba2' },
    { title: 'Benefits', color: '#f093fb' },
    { title: 'Conclusion', color: '#f5576c' }
  ]

  return (
    <div ref={containerRef} style={{ height: '400vh', position: 'relative' }}>
      <div style={{ position: 'sticky', top: 0, height: '100vh' }}>
        {sections.map((section, index) => {
          const start = index / sections.length
          const end = (index + 1) / sections.length

          const opacity = useTransform(
            scrollYProgress,
            [start, start + 0.05, end - 0.05, end],
            [0, 1, 1, 0]
          )

          return (
            <motion.div
              key={section.title}
              style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: section.color,
                opacity
              }}
            >
              <h1 style={{ fontSize: '5rem', color: 'white' }}>{section.title}</h1>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
```

---

## Advanced Layout Animations

### Masonry Grid with Layout Animation

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function MasonryGrid() {
  const [items, setItems] = useState([
    { id: 1, height: 200 },
    { id: 2, height: 300 },
    { id: 3, height: 250 },
    { id: 4, height: 180 },
    { id: 5, height: 280 },
    { id: 6, height: 220 }
  ])

  const removeItem = (id) => {
    setItems(items.filter(item => item.id !== id))
  }

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
      gap: 16,
      padding: 20
    }}>
      <AnimatePresence>
        {items.map(item => (
          <motion.div
            key={item.id}
            layout
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{
              layout: { type: 'spring', stiffness: 300, damping: 30 },
              opacity: { duration: 0.2 }
            }}
            style={{
              height: item.height,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: 12,
              cursor: 'pointer'
            }}
            onClick={() => removeItem(item.id)}
            whileHover={{ scale: 1.05 }}
          />
        ))}
      </AnimatePresence>
    </div>
  )
}
```

### Expandable Card

```jsx
import { motion } from 'framer-motion'
import { useState } from 'react'

function ExpandableCard({ title, content }) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <motion.div
      layout
      onClick={() => setIsExpanded(!isExpanded)}
      style={{
        background: 'white',
        borderRadius: 16,
        padding: 20,
        cursor: 'pointer',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
      }}
    >
      <motion.h3 layout="position">{title}</motion.h3>
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <p>{content}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
```

### Accordion with Layout Animation

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function Accordion({ items }) {
  const [expandedIndex, setExpandedIndex] = useState(null)

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      {items.map((item, index) => {
        const isExpanded = index === expandedIndex

        return (
          <motion.div
            key={item.id}
            layout
            style={{
              background: 'white',
              borderRadius: 12,
              marginBottom: 8,
              overflow: 'hidden',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}
          >
            <motion.div
              layout="position"
              onClick={() => setExpandedIndex(isExpanded ? null : index)}
              style={{
                padding: 20,
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <h3>{item.title}</h3>
              <motion.div
                animate={{ rotate: isExpanded ? 180 : 0 }}
                transition={{ duration: 0.3 }}
              >
                ▼
              </motion.div>
            </motion.div>

            <AnimatePresence initial={false}>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  style={{ overflow: 'hidden' }}
                >
                  <div style={{ padding: '0 20px 20px' }}>
                    <p>{item.content}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )
      })}
    </div>
  )
}
```

### Grid to List View Toggle

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function ViewToggle() {
  const [isGrid, setIsGrid] = useState(true)
  const items = Array.from({ length: 12 }, (_, i) => ({ id: i + 1, title: `Item ${i + 1}` }))

  return (
    <div>
      <button onClick={() => setIsGrid(!isGrid)}>
        Toggle {isGrid ? 'List' : 'Grid'} View
      </button>

      <motion.div
        layout
        style={{
          display: 'grid',
          gridTemplateColumns: isGrid ? 'repeat(4, 1fr)' : '1fr',
          gap: 16,
          padding: 20,
          transition: 'grid-template-columns 0.3s'
        }}
      >
        {items.map(item => (
          <motion.div
            key={item.id}
            layout
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            style={{
              height: isGrid ? 150 : 80,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: 12,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontWeight: 'bold'
            }}
          >
            {item.title}
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}
```

---

## Shared Element Transitions

### Image Gallery with Shared Layout

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function SharedLayoutGallery() {
  const [selectedId, setSelectedId] = useState(null)

  const images = [
    { id: 1, src: '/image1.jpg', title: 'Image 1' },
    { id: 2, src: '/image2.jpg', title: 'Image 2' },
    { id: 3, src: '/image3.jpg', title: 'Image 3' },
    { id: 4, src: '/image4.jpg', title: 'Image 4' }
  ]

  return (
    <>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}>
        {images.map(image => (
          <motion.div
            key={image.id}
            layoutId={`image-${image.id}`}
            onClick={() => setSelectedId(image.id)}
            style={{
              borderRadius: 12,
              overflow: 'hidden',
              cursor: 'pointer'
            }}
            whileHover={{ scale: 1.05 }}
          >
            <img src={image.src} alt={image.title} style={{ width: '100%', display: 'block' }} />
          </motion.div>
        ))}
      </div>

      <AnimatePresence>
        {selectedId && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedId(null)}
              style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(0, 0, 0, 0.8)',
                zIndex: 999,
                cursor: 'pointer'
              }}
            />

            <motion.div
              layoutId={`image-${selectedId}`}
              style={{
                position: 'fixed',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                maxWidth: '90vw',
                maxHeight: '90vh',
                zIndex: 1000,
                borderRadius: 12,
                overflow: 'hidden'
              }}
            >
              <img
                src={images.find(img => img.id === selectedId)?.src}
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
              />
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
```

### Tab Indicator

```jsx
import { motion } from 'framer-motion'
import { useState } from 'react'

function TabsWithIndicator() {
  const [activeTab, setActiveTab] = useState('home')

  const tabs = [
    { id: 'home', label: 'Home' },
    { id: 'about', label: 'About' },
    { id: 'services', label: 'Services' },
    { id: 'contact', label: 'Contact' }
  ]

  return (
    <div style={{ display: 'flex', gap: 8, background: '#f3f4f6', borderRadius: 12, padding: 4 }}>
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => setActiveTab(tab.id)}
          style={{
            position: 'relative',
            padding: '12px 24px',
            border: 'none',
            background: 'transparent',
            cursor: 'pointer',
            fontWeight: activeTab === tab.id ? 600 : 400,
            color: activeTab === tab.id ? 'white' : '#6b7280',
            zIndex: 1
          }}
        >
          {activeTab === tab.id && (
            <motion.div
              layoutId="tab-indicator"
              style={{
                position: 'absolute',
                inset: 0,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: 8,
                zIndex: -1
              }}
              transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            />
          )}
          {tab.label}
        </button>
      ))}
    </div>
  )
}
```

### Card Expansion with Shared Layout

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function ExpandingCardList() {
  const [selectedId, setSelectedId] = useState(null)

  const items = [
    { id: 1, title: 'Card 1', subtitle: 'Subtitle 1', description: 'Full description...' },
    { id: 2, title: 'Card 2', subtitle: 'Subtitle 2', description: 'Full description...' },
    { id: 3, title: 'Card 3', subtitle: 'Subtitle 3', description: 'Full description...' }
  ]

  return (
    <>
      <div style={{ display: 'grid', gap: 16, padding: 20 }}>
        {items.map(item => (
          <motion.div
            key={item.id}
            layoutId={`card-${item.id}`}
            onClick={() => setSelectedId(item.id)}
            style={{
              background: 'white',
              borderRadius: 16,
              padding: 20,
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
            }}
            whileHover={{ scale: 1.02 }}
          >
            <motion.h2 layoutId={`title-${item.id}`}>{item.title}</motion.h2>
            <motion.p layoutId={`subtitle-${item.id}`}>{item.subtitle}</motion.p>
          </motion.div>
        ))}
      </div>

      <AnimatePresence>
        {selectedId && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedId(null)}
              style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(0, 0, 0, 0.5)',
                zIndex: 999
              }}
            />

            <motion.div
              layoutId={`card-${selectedId}`}
              style={{
                position: 'fixed',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '90%',
                maxWidth: 600,
                background: 'white',
                borderRadius: 16,
                padding: 32,
                zIndex: 1000
              }}
            >
              <motion.h2 layoutId={`title-${selectedId}`}>
                {items.find(i => i.id === selectedId)?.title}
              </motion.h2>
              <motion.p layoutId={`subtitle-${selectedId}`}>
                {items.find(i => i.id === selectedId)?.subtitle}
              </motion.p>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <p>{items.find(i => i.id === selectedId)?.description}</p>
              </motion.div>
              <button onClick={() => setSelectedId(null)}>Close</button>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
```

---

## Modal & Dialog Patterns

### Smooth Modal with Backdrop

```jsx
import { motion, AnimatePresence } from 'framer-motion'

function Modal({ isOpen, onClose, children }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.6)',
              backdropFilter: 'blur(4px)',
              zIndex: 999,
              cursor: 'pointer'
            }}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            style={{
              position: 'fixed',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              background: 'white',
              borderRadius: 16,
              padding: 32,
              maxWidth: 500,
              width: '90%',
              zIndex: 1000,
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
```

### Drawer / Side Panel

```jsx
import { motion, AnimatePresence } from 'framer-motion'

function Drawer({ isOpen, onClose, position = 'right', children }) {
  const variants = {
    right: {
      initial: { x: '100%' },
      animate: { x: 0 },
      exit: { x: '100%' }
    },
    left: {
      initial: { x: '-100%' },
      animate: { x: 0 },
      exit: { x: '-100%' }
    },
    top: {
      initial: { y: '-100%' },
      animate: { y: 0 },
      exit: { y: '-100%' }
    },
    bottom: {
      initial: { y: '100%' },
      animate: { y: 0 },
      exit: { y: '100%' }
    }
  }

  const positionStyles = {
    right: { top: 0, right: 0, bottom: 0, width: '400px' },
    left: { top: 0, left: 0, bottom: 0, width: '400px' },
    top: { top: 0, left: 0, right: 0, height: '400px' },
    bottom: { bottom: 0, left: 0, right: 0, height: '400px' }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.5)',
              zIndex: 999
            }}
          />

          <motion.div
            initial={variants[position].initial}
            animate={variants[position].animate}
            exit={variants[position].exit}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            style={{
              position: 'fixed',
              ...positionStyles[position],
              background: 'white',
              zIndex: 1000,
              boxShadow: '-4px 0 20px rgba(0, 0, 0, 0.1)',
              overflowY: 'auto'
            }}
          >
            <div style={{ padding: 32 }}>
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
```

### Bottom Sheet (Mobile)

```jsx
import { motion, AnimatePresence, useDragControls, PanInfo } from 'framer-motion'
import { useRef } from 'react'

function BottomSheet({ isOpen, onClose, children }) {
  const dragControls = useDragControls()
  const constraintsRef = useRef(null)

  const handleDragEnd = (event: MouseEvent, info: PanInfo) => {
    if (info.offset.y > 100) {
      onClose()
    }
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.5)',
              zIndex: 999
            }}
          />

          <motion.div
            ref={constraintsRef}
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            drag="y"
            dragControls={dragControls}
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={{ top: 0, bottom: 0.5 }}
            onDragEnd={handleDragEnd}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            style={{
              position: 'fixed',
              bottom: 0,
              left: 0,
              right: 0,
              background: 'white',
              borderTopLeftRadius: 24,
              borderTopRightRadius: 24,
              maxHeight: '90vh',
              zIndex: 1000,
              boxShadow: '0 -4px 20px rgba(0, 0, 0, 0.1)'
            }}
          >
            <div
              style={{
                padding: '16px 0',
                display: 'flex',
                justifyContent: 'center',
                cursor: 'grab'
              }}
              onPointerDown={(e) => dragControls.start(e)}
            >
              <div style={{
                width: 40,
                height: 4,
                background: '#d1d5db',
                borderRadius: 2
              }} />
            </div>

            <div style={{ padding: '0 24px 24px', overflowY: 'auto' }}>
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
```

### Confirmation Dialog with Shake

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function ConfirmDialog({ isOpen, onConfirm, onCancel, title, message }) {
  const [isShaking, setIsShaking] = useState(false)

  const handleConfirm = () => {
    setIsShaking(true)
    setTimeout(() => {
      setIsShaking(false)
      onConfirm()
    }, 600)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.5)',
              zIndex: 999
            }}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{
              opacity: 1,
              scale: 1,
              x: isShaking ? [-10, 10, -10, 10, 0] : 0
            }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{
              scale: { type: 'spring', stiffness: 300, damping: 30 },
              x: { duration: 0.5 }
            }}
            style={{
              position: 'fixed',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              background: 'white',
              borderRadius: 16,
              padding: 32,
              maxWidth: 400,
              width: '90%',
              zIndex: 1000
            }}
          >
            <h3>{title}</h3>
            <p>{message}</p>
            <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onCancel}
                style={{
                  flex: 1,
                  padding: '12px 24px',
                  border: '1px solid #d1d5db',
                  background: 'white',
                  borderRadius: 8,
                  cursor: 'pointer'
                }}
              >
                Cancel
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleConfirm}
                style={{
                  flex: 1,
                  padding: '12px 24px',
                  border: 'none',
                  background: '#ef4444',
                  color: 'white',
                  borderRadius: 8,
                  cursor: 'pointer'
                }}
              >
                Confirm
              </motion.button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
```

---

## Form Animations

### Floating Label Input

```jsx
import { motion } from 'framer-motion'
import { useState } from 'react'

function FloatingLabelInput({ label, type = 'text', ...props }) {
  const [isFocused, setIsFocused] = useState(false)
  const [hasValue, setHasValue] = useState(false)

  const isFloating = isFocused || hasValue

  return (
    <div style={{ position: 'relative', marginBottom: 24 }}>
      <motion.label
        animate={{
          y: isFloating ? -24 : 0,
          scale: isFloating ? 0.85 : 1,
          color: isFocused ? '#667eea' : '#6b7280'
        }}
        transition={{ duration: 0.2 }}
        style={{
          position: 'absolute',
          left: 12,
          top: 12,
          transformOrigin: 'left',
          pointerEvents: 'none',
          fontWeight: 500
        }}
      >
        {label}
      </motion.label>

      <motion.input
        type={type}
        onFocus={() => setIsFocused(true)}
        onBlur={(e) => {
          setIsFocused(false)
          setHasValue(e.target.value !== '')
        }}
        animate={{
          borderColor: isFocused ? '#667eea' : '#d1d5db'
        }}
        transition={{ duration: 0.2 }}
        style={{
          width: '100%',
          padding: '12px',
          paddingTop: isFloating ? 24 : 12,
          border: '2px solid',
          borderRadius: 8,
          fontSize: '1rem',
          outline: 'none'
        }}
        {...props}
      />
    </div>
  )
}
```

### Multi-Step Form with Progress

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function MultiStepForm() {
  const [step, setStep] = useState(0)
  const [direction, setDirection] = useState(1)

  const steps = [
    { title: 'Personal Info', fields: ['name', 'email'] },
    { title: 'Address', fields: ['street', 'city'] },
    { title: 'Confirmation', fields: [] }
  ]

  const nextStep = () => {
    setDirection(1)
    setStep(Math.min(step + 1, steps.length - 1))
  }

  const prevStep = () => {
    setDirection(-1)
    setStep(Math.max(step - 1, 0))
  }

  const progress = ((step + 1) / steps.length) * 100

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 40 }}>
      {/* Progress Bar */}
      <div style={{ marginBottom: 40 }}>
        <div style={{
          height: 4,
          background: '#e5e7eb',
          borderRadius: 2,
          overflow: 'hidden'
        }}>
          <motion.div
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
            style={{
              height: '100%',
              background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)'
            }}
          />
        </div>
      </div>

      {/* Step Content */}
      <AnimatePresence mode="wait" custom={direction}>
        <motion.div
          key={step}
          custom={direction}
          initial={(direction) => ({
            x: direction > 0 ? 300 : -300,
            opacity: 0
          })}
          animate={{ x: 0, opacity: 1 }}
          exit={(direction) => ({
            x: direction > 0 ? -300 : 300,
            opacity: 0
          })}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          <h2>{steps[step].title}</h2>
          <div style={{ marginTop: 24 }}>
            {steps[step].fields.map(field => (
              <FloatingLabelInput key={field} label={field} />
            ))}
            {step === steps.length - 1 && (
              <div>
                <p>Review your information and submit.</p>
              </div>
            )}
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Navigation */}
      <div style={{ display: 'flex', gap: 12, marginTop: 32 }}>
        {step > 0 && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={prevStep}
            style={{
              padding: '12px 24px',
              border: '1px solid #d1d5db',
              background: 'white',
              borderRadius: 8,
              cursor: 'pointer'
            }}
          >
            Previous
          </motion.button>
        )}
        {step < steps.length - 1 ? (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={nextStep}
            style={{
              flex: 1,
              padding: '12px 24px',
              border: 'none',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              borderRadius: 8,
              cursor: 'pointer'
            }}
          >
            Next
          </motion.button>
        ) : (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            style={{
              flex: 1,
              padding: '12px 24px',
              border: 'none',
              background: '#10b981',
              color: 'white',
              borderRadius: 8,
              cursor: 'pointer'
            }}
          >
            Submit
          </motion.button>
        )}
      </div>
    </div>
  )
}
```

### Form Validation with Animation

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function ValidatedInput({ label, validation, ...props }) {
  const [value, setValue] = useState('')
  const [error, setError] = useState('')
  const [touched, setTouched] = useState(false)

  const handleBlur = () => {
    setTouched(true)
    if (validation) {
      const errorMessage = validation(value)
      setError(errorMessage)
    }
  }

  const hasError = touched && error

  return (
    <div style={{ marginBottom: 24 }}>
      <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
        {label}
      </label>

      <motion.input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onBlur={handleBlur}
        animate={{
          borderColor: hasError ? '#ef4444' : '#d1d5db',
          x: hasError ? [-10, 10, -10, 10, 0] : 0
        }}
        transition={{
          borderColor: { duration: 0.2 },
          x: { duration: 0.4 }
        }}
        style={{
          width: '100%',
          padding: 12,
          border: '2px solid',
          borderRadius: 8,
          fontSize: '1rem',
          outline: 'none'
        }}
        {...props}
      />

      <AnimatePresence>
        {hasError && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            style={{
              marginTop: 8,
              color: '#ef4444',
              fontSize: '0.875rem'
            }}
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Usage
function ContactForm() {
  return (
    <form>
      <ValidatedInput
        label="Email"
        type="email"
        validation={(value) => {
          if (!value) return 'Email is required'
          if (!/\S+@\S+\.\S+/.test(value)) return 'Invalid email format'
          return ''
        }}
      />
      <ValidatedInput
        label="Password"
        type="password"
        validation={(value) => {
          if (!value) return 'Password is required'
          if (value.length < 8) return 'Password must be at least 8 characters'
          return ''
        }}
      />
    </form>
  )
}
```

---

## Loading States

### Skeleton Loading

```jsx
import { motion } from 'framer-motion'

function Skeleton({ width, height, borderRadius = 8 }) {
  return (
    <motion.div
      animate={{
        opacity: [0.5, 1, 0.5]
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeInOut'
      }}
      style={{
        width,
        height,
        borderRadius,
        background: 'linear-gradient(90deg, #e5e7eb 0%, #f3f4f6 50%, #e5e7eb 100%)',
        backgroundSize: '200% 100%'
      }}
    />
  )
}

function SkeletonCard() {
  return (
    <div style={{ padding: 20, background: 'white', borderRadius: 16 }}>
      <Skeleton width="100%" height={200} />
      <div style={{ marginTop: 16 }}>
        <Skeleton width="70%" height={24} />
      </div>
      <div style={{ marginTop: 12 }}>
        <Skeleton width="100%" height={16} />
        <div style={{ marginTop: 8 }}>
          <Skeleton width="90%" height={16} />
        </div>
      </div>
    </div>
  )
}
```

### Spinner with Variants

```jsx
import { motion } from 'framer-motion'

function Spinner({ size = 40, color = '#667eea' }) {
  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: 'linear'
      }}
      style={{
        width: size,
        height: size,
        border: `4px solid rgba(102, 126, 234, 0.2)`,
        borderTopColor: color,
        borderRadius: '50%'
      }}
    />
  )
}

function DotsSpinner() {
  return (
    <div style={{ display: 'flex', gap: 8 }}>
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.5, 1, 0.5]
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: index * 0.2
          }}
          style={{
            width: 12,
            height: 12,
            borderRadius: '50%',
            background: '#667eea'
          }}
        />
      ))}
    </div>
  )
}
```

### Progress Bar with Pulse

```jsx
import { motion } from 'framer-motion'

function ProgressBar({ progress }) {
  return (
    <div style={{
      width: '100%',
      height: 8,
      background: '#e5e7eb',
      borderRadius: 4,
      overflow: 'hidden',
      position: 'relative'
    }}>
      <motion.div
        animate={{ width: `${progress}%` }}
        transition={{ type: 'spring', stiffness: 100, damping: 20 }}
        style={{
          height: '100%',
          background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
          position: 'relative'
        }}
      >
        <motion.div
          animate={{
            x: ['-100%', '100%']
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'linear'
          }}
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)'
          }}
        />
      </motion.div>
    </div>
  )
}
```

### Content Fade In

```jsx
import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

function AsyncContent({ fetchData }) {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchData().then((result) => {
      setData(result)
      setIsLoading(false)
    })
  }, [])

  return (
    <AnimatePresence mode="wait">
      {isLoading ? (
        <motion.div
          key="loading"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <Spinner />
        </motion.div>
      ) : (
        <motion.div
          key="content"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {data && <div>{/* Render your data */}</div>}
        </motion.div>
      )}
    </AnimatePresence>
  )
}
```

---

## List Animations

### Animated List with Add/Remove

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function AnimatedList() {
  const [items, setItems] = useState([
    { id: 1, text: 'Item 1' },
    { id: 2, text: 'Item 2' },
    { id: 3, text: 'Item 3' }
  ])
  const [nextId, setNextId] = useState(4)

  const addItem = () => {
    setItems([...items, { id: nextId, text: `Item ${nextId}` }])
    setNextId(nextId + 1)
  }

  const removeItem = (id) => {
    setItems(items.filter(item => item.id !== id))
  }

  return (
    <div>
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={addItem}
        style={{
          marginBottom: 20,
          padding: '12px 24px',
          background: '#667eea',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          cursor: 'pointer'
        }}
      >
        Add Item
      </motion.button>

      <AnimatePresence>
        {items.map((item, index) => (
          <motion.div
            key={item.id}
            layout
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{
              layout: { type: 'spring', stiffness: 300, damping: 30 },
              opacity: { duration: 0.2 },
              x: { duration: 0.2 }
            }}
            style={{
              padding: 20,
              marginBottom: 12,
              background: 'white',
              borderRadius: 12,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}
          >
            <span>{item.text}</span>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => removeItem(item.id)}
              style={{
                padding: '8px 16px',
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: 6,
                cursor: 'pointer'
              }}
            >
              Remove
            </motion.button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
```

### Reorderable List (Drag to Reorder)

```jsx
import { motion, Reorder } from 'framer-motion'
import { useState } from 'react'

function ReorderableList() {
  const [items, setItems] = useState([
    { id: 1, text: 'Item 1' },
    { id: 2, text: 'Item 2' },
    { id: 3, text: 'Item 3' },
    { id: 4, text: 'Item 4' }
  ])

  return (
    <Reorder.Group axis="y" values={items} onReorder={setItems}>
      {items.map((item) => (
        <Reorder.Item key={item.id} value={item}>
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileDrag={{ scale: 1.05, boxShadow: '0 10px 30px rgba(0,0,0,0.2)' }}
            style={{
              padding: 20,
              marginBottom: 12,
              background: 'white',
              borderRadius: 12,
              cursor: 'grab',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              userSelect: 'none'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: '1.5rem' }}>☰</span>
              <span>{item.text}</span>
            </div>
          </motion.div>
        </Reorder.Item>
      ))}
    </Reorder.Group>
  )
}
```

### Staggered Grid

```jsx
import { motion } from 'framer-motion'

const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
}

const item = {
  hidden: { opacity: 0, scale: 0.8, y: 20 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 24
    }
  }
}

function StaggeredGrid() {
  const items = Array.from({ length: 12 }, (_, i) => ({ id: i + 1 }))

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="visible"
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: 16,
        padding: 20
      }}
    >
      {items.map((gridItem) => (
        <motion.div
          key={gridItem.id}
          variants={item}
          whileHover={{ scale: 1.05, transition: { duration: 0.2 } }}
          style={{
            height: 150,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: 12,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '2rem',
            fontWeight: 'bold'
          }}
        >
          {gridItem.id}
        </motion.div>
      ))}
    </motion.div>
  )
}
```

---

## Image Galleries

### Lightbox Gallery

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function LightboxGallery({ images }) {
  const [selectedIndex, setSelectedIndex] = useState(null)

  const handlePrevious = () => {
    setSelectedIndex((selectedIndex - 1 + images.length) % images.length)
  }

  const handleNext = () => {
    setSelectedIndex((selectedIndex + 1) % images.length)
  }

  return (
    <>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
        gap: 16,
        padding: 20
      }}>
        {images.map((image, index) => (
          <motion.div
            key={image.id}
            whileHover={{ scale: 1.05 }}
            onClick={() => setSelectedIndex(index)}
            style={{
              aspectRatio: '1',
              borderRadius: 12,
              overflow: 'hidden',
              cursor: 'pointer'
            }}
          >
            <img
              src={image.thumbnail}
              alt={image.alt}
              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
          </motion.div>
        ))}
      </div>

      <AnimatePresence>
        {selectedIndex !== null && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedIndex(null)}
              style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(0, 0, 0, 0.9)',
                zIndex: 999,
                cursor: 'pointer'
              }}
            />

            <motion.div
              key={selectedIndex}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              style={{
                position: 'fixed',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                maxWidth: '90vw',
                maxHeight: '90vh',
                zIndex: 1000
              }}
            >
              <img
                src={images[selectedIndex].full}
                alt={images[selectedIndex].alt}
                style={{
                  maxWidth: '100%',
                  maxHeight: '90vh',
                  borderRadius: 12
                }}
              />
            </motion.div>

            <button
              onClick={(e) => {
                e.stopPropagation()
                handlePrevious()
              }}
              style={{
                position: 'fixed',
                left: 20,
                top: '50%',
                transform: 'translateY(-50%)',
                zIndex: 1001,
                padding: 16,
                background: 'rgba(255, 255, 255, 0.2)',
                border: 'none',
                borderRadius: 8,
                cursor: 'pointer',
                fontSize: '2rem',
                color: 'white'
              }}
            >
              ‹
            </button>

            <button
              onClick={(e) => {
                e.stopPropagation()
                handleNext()
              }}
              style={{
                position: 'fixed',
                right: 20,
                top: '50%',
                transform: 'translateY(-50%)',
                zIndex: 1001,
                padding: 16,
                background: 'rgba(255, 255, 255, 0.2)',
                border: 'none',
                borderRadius: 8,
                cursor: 'pointer',
                fontSize: '2rem',
                color: 'white'
              }}
            >
              ›
            </button>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
```

### Carousel with Swipe

```jsx
import { motion, AnimatePresence, PanInfo } from 'framer-motion'
import { useState } from 'react'

function Carousel({ images }) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [direction, setDirection] = useState(0)

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1
    },
    exit: (direction: number) => ({
      zIndex: 0,
      x: direction < 0 ? 1000 : -1000,
      opacity: 0
    })
  }

  const swipeConfidenceThreshold = 10000
  const swipePower = (offset: number, velocity: number) => {
    return Math.abs(offset) * velocity
  }

  const paginate = (newDirection: number) => {
    setDirection(newDirection)
    setCurrentIndex((currentIndex + newDirection + images.length) % images.length)
  }

  const handleDragEnd = (e: MouseEvent, { offset, velocity }: PanInfo) => {
    const swipe = swipePower(offset.x, velocity.x)

    if (swipe < -swipeConfidenceThreshold) {
      paginate(1)
    } else if (swipe > swipeConfidenceThreshold) {
      paginate(-1)
    }
  }

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      height: 400,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      overflow: 'hidden'
    }}>
      <AnimatePresence initial={false} custom={direction}>
        <motion.img
          key={currentIndex}
          src={images[currentIndex]}
          custom={direction}
          variants={slideVariants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{
            x: { type: 'spring', stiffness: 300, damping: 30 },
            opacity: { duration: 0.2 }
          }}
          drag="x"
          dragConstraints={{ left: 0, right: 0 }}
          dragElastic={1}
          onDragEnd={handleDragEnd}
          style={{
            position: 'absolute',
            maxWidth: '100%',
            maxHeight: '100%',
            borderRadius: 12
          }}
        />
      </AnimatePresence>

      <button
        onClick={() => paginate(-1)}
        style={{
          position: 'absolute',
          left: 10,
          zIndex: 2,
          padding: 12,
          background: 'rgba(255, 255, 255, 0.8)',
          border: 'none',
          borderRadius: 8,
          cursor: 'pointer'
        }}
      >
        ‹
      </button>

      <button
        onClick={() => paginate(1)}
        style={{
          position: 'absolute',
          right: 10,
          zIndex: 2,
          padding: 12,
          background: 'rgba(255, 255, 255, 0.8)',
          border: 'none',
          borderRadius: 8,
          cursor: 'pointer'
        }}
      >
        ›
      </button>

      <div style={{
        position: 'absolute',
        bottom: 20,
        display: 'flex',
        gap: 8
      }}>
        {images.map((_, index) => (
          <div
            key={index}
            onClick={() => {
              setDirection(index > currentIndex ? 1 : -1)
              setCurrentIndex(index)
            }}
            style={{
              width: 10,
              height: 10,
              borderRadius: '50%',
              background: index === currentIndex ? 'white' : 'rgba(255, 255, 255, 0.5)',
              cursor: 'pointer'
            }}
          />
        ))}
      </div>
    </div>
  )
}
```

---

## Navigation Menus

### Animated Dropdown Menu

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function DropdownMenu({ trigger, items }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div style={{ position: 'relative' }}>
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        style={{
          padding: '12px 24px',
          background: '#667eea',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          cursor: 'pointer'
        }}
      >
        {trigger}
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              style={{
                position: 'fixed',
                inset: 0,
                zIndex: 998
              }}
            />

            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                marginTop: 8,
                minWidth: 200,
                background: 'white',
                borderRadius: 12,
                boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
                overflow: 'hidden',
                zIndex: 999
              }}
            >
              {items.map((item, index) => (
                <motion.div
                  key={index}
                  whileHover={{ background: '#f3f4f6' }}
                  onClick={() => {
                    item.onClick?.()
                    setIsOpen(false)
                  }}
                  style={{
                    padding: '12px 20px',
                    cursor: 'pointer'
                  }}
                >
                  {item.label}
                </motion.div>
              ))}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
```

### Mega Menu

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function MegaMenu() {
  const [activeMenu, setActiveMenu] = useState(null)

  const menus = {
    products: {
      sections: [
        {
          title: 'Category 1',
          items: ['Product 1', 'Product 2', 'Product 3']
        },
        {
          title: 'Category 2',
          items: ['Product 4', 'Product 5', 'Product 6']
        }
      ]
    },
    solutions: {
      sections: [
        {
          title: 'For Business',
          items: ['Enterprise', 'Small Business']
        },
        {
          title: 'For Developers',
          items: ['API', 'Documentation']
        }
      ]
    }
  }

  return (
    <nav style={{ background: 'white', padding: '16px 0', borderBottom: '1px solid #e5e7eb' }}>
      <div style={{ display: 'flex', gap: 32, maxWidth: 1200, margin: '0 auto', padding: '0 20px' }}>
        {Object.keys(menus).map((menuKey) => (
          <div
            key={menuKey}
            onMouseEnter={() => setActiveMenu(menuKey)}
            onMouseLeave={() => setActiveMenu(null)}
            style={{ position: 'relative' }}
          >
            <button
              style={{
                padding: '8px 16px',
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                fontWeight: 500,
                textTransform: 'capitalize'
              }}
            >
              {menuKey}
            </button>

            <AnimatePresence>
              {activeMenu === menuKey && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                  style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    marginTop: 8,
                    background: 'white',
                    borderRadius: 12,
                    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)',
                    padding: 32,
                    display: 'flex',
                    gap: 48,
                    minWidth: 600,
                    zIndex: 999
                  }}
                >
                  {menus[menuKey].sections.map((section, index) => (
                    <div key={index}>
                      <h4 style={{ marginBottom: 16, fontWeight: 600 }}>{section.title}</h4>
                      <ul style={{ listStyle: 'none', padding: 0 }}>
                        {section.items.map((item, itemIndex) => (
                          <motion.li
                            key={itemIndex}
                            whileHover={{ x: 4, color: '#667eea' }}
                            style={{
                              padding: '8px 0',
                              cursor: 'pointer',
                              transition: 'color 0.2s'
                            }}
                          >
                            {item}
                          </motion.li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        ))}
      </div>
    </nav>
  )
}
```

### Mobile Hamburger Menu

```jsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

function HamburgerMenu() {
  const [isOpen, setIsOpen] = useState(false)

  const menuItems = [
    { label: 'Home', href: '/' },
    { label: 'About', href: '/about' },
    { label: 'Services', href: '/services' },
    { label: 'Contact', href: '/contact' }
  ]

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 6,
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          padding: 8
        }}
      >
        <motion.span
          animate={isOpen ? { rotate: 45, y: 9 } : { rotate: 0, y: 0 }}
          style={{
            width: 30,
            height: 3,
            background: '#1f2937',
            borderRadius: 2
          }}
        />
        <motion.span
          animate={isOpen ? { opacity: 0 } : { opacity: 1 }}
          style={{
            width: 30,
            height: 3,
            background: '#1f2937',
            borderRadius: 2
          }}
        />
        <motion.span
          animate={isOpen ? { rotate: -45, y: -9 } : { rotate: 0, y: 0 }}
          style={{
            width: 30,
            height: 3,
            background: '#1f2937',
            borderRadius: 2
          }}
        />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(0, 0, 0, 0.5)',
                zIndex: 998
              }}
            />

            <motion.nav
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              style={{
                position: 'fixed',
                top: 0,
                right: 0,
                bottom: 0,
                width: '80%',
                maxWidth: 400,
                background: 'white',
                zIndex: 999,
                padding: 40
              }}
            >
              {menuItems.map((item, index) => (
                <motion.a
                  key={item.href}
                  href={item.href}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ x: 8, color: '#667eea' }}
                  style={{
                    display: 'block',
                    padding: '16px 0',
                    fontSize: '1.25rem',
                    textDecoration: 'none',
                    color: '#1f2937'
                  }}
                >
                  {item.label}
                </motion.a>
              ))}
            </motion.nav>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
```

---

## Performance Optimization

### useReducedMotion Hook

```jsx
import { useReducedMotion } from 'framer-motion'

function AccessibleAnimation() {
  const shouldReduceMotion = useReducedMotion()

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: shouldReduceMotion ? 0.01 : 0.5
      }}
    >
      Content that respects user preferences
    </motion.div>
  )
}
```

### Lazy Motion Component

```jsx
import { lazy } from 'react'
import { LazyMotion, domAnimation, m } from 'framer-motion'

// Use 'm' instead of 'motion' with LazyMotion for smaller bundle
function OptimizedComponent() {
  return (
    <LazyMotion features={domAnimation}>
      <m.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        style={{ width: 200, height: 200, background: '#667eea' }}
      />
    </LazyMotion>
  )
}
```

### will-change Optimization

```jsx
function OptimizedAnimatedBox() {
  return (
    <motion.div
      whileHover={{ scale: 1.1 }}
      style={{
        width: 200,
        height: 200,
        background: '#667eea',
        // Hint to browser that this property will change
        willChange: 'transform'
      }}
    />
  )
}
```

### Reuse Variant Objects

```jsx
// ✅ Good - reused variants
const fadeVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 }
}

function ComponentA() {
  return <motion.div variants={fadeVariants} initial="hidden" animate="visible" />
}

function ComponentB() {
  return <motion.div variants={fadeVariants} initial="hidden" animate="visible" />
}

// ❌ Bad - recreating variants
function ComponentC() {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0 },
        visible: { opacity: 1 }
      }}
      initial="hidden"
      animate="visible"
    />
  )
}
```

### Throttle Scroll Events

```jsx
import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import { useThrottle } from './useThrottle'

function ThrottledScroll() {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref })

  // Throttle scroll updates to 60fps max
  const throttledProgress = useThrottle(scrollYProgress, 16)
  const y = useTransform(throttledProgress, [0, 1], [0, -100])

  return (
    <motion.div ref={ref} style={{ y }}>
      Optimized scroll animation
    </motion.div>
  )
}
```

### Exit Before Enter (Reduce Simultaneous Animations)

```jsx
import { AnimatePresence } from 'framer-motion'

// ✅ Good - "wait" mode reduces simultaneous animations
function OptimizedPageTransition() {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      />
    </AnimatePresence>
  )
}
```

---

## Best Practices Summary

### 1. Use Transform Properties

```jsx
// ✅ Good - hardware accelerated
<motion.div animate={{ x: 100, scale: 1.2 }} />

// ❌ Bad - triggers layout reflow
<motion.div animate={{ left: 100, width: 200 }} />
```

### 2. Respect Accessibility

```jsx
import { useReducedMotion } from 'framer-motion'

function AccessibleComponent() {
  const prefersReducedMotion = useReducedMotion()

  return (
    <motion.div
      animate={{
        scale: prefersReducedMotion ? 1 : 1.2,
        transition: { duration: prefersReducedMotion ? 0 : 0.5 }
      }}
    />
  )
}
```

### 3. Optimize Bundle Size

```jsx
import { LazyMotion, domAnimation, m } from 'framer-motion'

function SmallBundle() {
  return (
    <LazyMotion features={domAnimation}>
      <m.div animate={{ opacity: 1 }} />
    </LazyMotion>
  )
}
```

### 4. Clean Up Animations

```jsx
import { useAnimation } from 'framer-motion'
import { useEffect } from 'react'

function CleanupExample() {
  const controls = useAnimation()

  useEffect(() => {
    controls.start({ opacity: 1 })

    // Cleanup on unmount
    return () => {
      controls.stop()
    }
  }, [])

  return <motion.div animate={controls} />
}
```

### 5. Debounce/Throttle Expensive Operations

```jsx
import { motion, useMotionValue } from 'framer-motion'
import { useDebounce } from './useDebounce'

function DebouncedInput() {
  const inputValue = useMotionValue('')
  const debouncedValue = useDebounce(inputValue, 300)

  return (
    <motion.input
      onChange={(e) => inputValue.set(e.target.value)}
    />
  )
}
```

---

## Additional Resources

- [Framer Motion Official Docs](https://www.framer.com/motion/)
- [Motion Dev](https://motion.dev/) - New Motion library
- [Motion Examples](https://www.framer.com/motion/examples/)
- [Motion API Reference](https://www.framer.com/motion/component/)
- [Animation Best Practices](https://web.dev/animations/)

---

## License

MIT - Free for personal and commercial use



===== FILE: plugins/individual/motion-framer/skills/motion-framer/assets/starter_motion/README.md =====

# Motion Starter Template

A minimal, production-ready starter template for building animated React applications with Framer Motion.

## Features

- ⚡️ **Vite** - Fast build tool and dev server
- ⚛️ **React 18** - Latest React with concurrent features
- 🎨 **Framer Motion** - Production-ready animation library
- 🎮 **Interactive Components** - Hover, tap, and drag interactions
- 📤 **Exit Animations** - AnimatePresence examples
- 🔄 **Layout Animations** - Smooth layout transitions
- 📜 **Stagger Effects** - Coordinated child animations

## Quick Start

### Installation

```bash
npm install
# or
yarn
# or
pnpm install
```

### Development

```bash
npm run dev
```

Opens at `http://localhost:3000`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
starter_motion/
├── index.html           # Entry HTML
├── package.json         # Dependencies
├── vite.config.js       # Vite configuration
└── src/
    ├── main.jsx         # React root
    ├── App.jsx          # Main App with examples
    ├── App.css          # Styles
    └── components/
        ├── HoverCard.jsx       # Hover animation example
        ├── DraggableBox.jsx    # Drag interaction example
        └── StaggerList.jsx     # Staggered animation example
```

## Included Examples

### 1. Hover Animations (HoverCard)

Demonstrates `whileHover` for interactive cards:
- Scale on hover
- Shadow effects
- Smooth transitions
- Combined with `whileTap`

### 2. Drag Interactions (DraggableBox)

Shows drag functionality:
- Drag constraints
- Visual feedback (`whileDrag`)
- Drag events (`onDragStart`, `onDragEnd`)
- Elastic boundaries

### 3. Staggered Animations (StaggerList)

Illustrates variant propagation:
- Container/item variant pattern
- `staggerChildren` for sequential animations
- `delayChildren` for initial delay
- Combined with hover effects

### 4. Exit Animations (Modal)

Demonstrates AnimatePresence:
- Exit animations with `exit` prop
- Modal backdrop fade
- Modal enter/exit with spring physics
- Proper cleanup

## Common Patterns

### Basic Animation

```jsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>
  Content
</motion.div>
```

### Hover Effect

```jsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
  Click me
</motion.button>
```

### Drag Interaction

```jsx
<motion.div
  drag
  dragConstraints={{ left: -100, right: 100, top: -100, bottom: 100 }}
  whileDrag={{ scale: 1.1 }}
>
  Drag me
</motion.div>
```

### Exit Animation

```jsx
<AnimatePresence>
  {show && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    />
  )}
</AnimatePresence>
```

### Variants with Stagger

```jsx
const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

<motion.ul variants={container} initial="hidden" animate="visible">
  <motion.li variants={item}>Item 1</motion.li>
  <motion.li variants={item}>Item 2</motion.li>
</motion.ul>
```

## Customization

### Add New Components

Create new components in `src/components/`:

```jsx
// src/components/MyComponent.jsx
import { motion } from 'framer-motion'

export default function MyComponent() {
  return (
    <motion.div
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
    >
      My Content
    </motion.div>
  )
}
```

Import in App.jsx:
```jsx
import MyComponent from './components/MyComponent'

// In App component:
<MyComponent />
```

### Change Transition Physics

```jsx
// Duration-based
<motion.div
  animate={{ x: 100 }}
  transition={{ duration: 0.5, ease: "easeInOut" }}
/>

// Spring-based (natural, bouncy)
<motion.div
  animate={{ x: 100 }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
/>
```

### Add Scroll Animations

```jsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.3 }}
  transition={{ duration: 0.5 }}
>
  Scroll to reveal
</motion.div>
```

### Layout Animations

```jsx
<motion.div layout>
  {/* Content that changes size/position */}
</motion.div>
```

### Shared Element Transitions

```jsx
// Tab indicator
{tabs.map(tab => (
  <div key={tab.id}>
    {tab.label}
    {activeTab === tab.id && (
      <motion.div layoutId="underline" />
    )}
  </div>
))}
```

## Performance Tips

1. **Use transform properties** - Animate `x`, `y`, `scale`, `rotate` (hardware accelerated)
2. **Avoid layout properties** - Don't animate `width`, `height`, `top`, `left`
3. **Reduce motion** - Respect accessibility preferences:
   ```jsx
   import { useReducedMotion } from "framer-motion"

   const shouldReduceMotion = useReducedMotion()
   ```
4. **Use `will-change` CSS** - For complex animations
5. **Optimize variants** - Reuse variant objects
6. **Lazy load heavy components** - Use React.lazy() for code splitting

## TypeScript Support

To add TypeScript:

```bash
npm install -D typescript @types/react @types/react-dom
```

Rename files to `.tsx`:
```bash
mv src/main.jsx src/main.tsx
mv src/App.jsx src/App.tsx
```

Add `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

## Resources

- [Framer Motion Docs](https://www.framer.com/motion/) - Official documentation
- [Motion Dev](https://motion.dev/) - New Motion library docs
- [Examples](https://www.framer.com/motion/examples/) - Interactive examples
- [API Reference](https://www.framer.com/motion/component/) - Complete API

## Troubleshooting

### Animations Not Working

- Ensure component is wrapped in `<motion.*>` not regular HTML
- Check that `initial` and `animate` props are set
- Verify transition configuration

### Exit Animations Not Working

- Wrap component in `<AnimatePresence>`
- Ensure component has unique `key` prop
- Add `exit` prop to motion component

### Performance Issues

- Use transform properties (x, y, scale, rotate)
- Avoid animating layout properties
- Reduce number of animated elements
- Use `layout="position"` instead of `layout={true}` when possible

### Drag Not Working

- Check `dragConstraints` are set properly
- Ensure parent has defined dimensions
- Verify `drag` prop is set to true or "x"/"y"

## License

MIT - Use freely for personal and commercial projects.



===== FILE: plugins/individual/motion-framer/skills/motion-framer/assets/starter_motion/index.html =====

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Motion Starter</title>
    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      html,
      body,
      #root {
        width: 100%;
        min-height: 100vh;
      }

      body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
          'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
          sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      #root {
        display: flex;
        flex-direction: column;
      }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>

```


===== FILE: plugins/individual/motion-framer/skills/motion-framer/assets/starter_motion/package.json =====

```json
{
  "name": "motion-starter",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "framer-motion": "^11.15.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.18",
    "@types/react-dom": "^18.3.5",
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.11"
  }
}

```


===== FILE: plugins/individual/motion-framer/skills/motion-framer/assets/starter_motion/src/App.css =====

```css
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  color: white;
}

.header {
  text-align: center;
  padding: 60px 20px 40px;
}

.header h1 {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 10px;
}

.header p {
  font-size: 1.2rem;
  opacity: 0.9;
}

.main {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  width: 100%;
}

.section {
  margin-bottom: 80px;
}

.section h2 {
  font-size: 2rem;
  margin-bottom: 30px;
  text-align: center;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.modal-button {
  display: block;
  margin: 0 auto;
  padding: 15px 40px;
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid white;
  border-radius: 12px;
  cursor: pointer;
  backdrop-filter: blur(10px);
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  color: #333;
  padding: 40px;
  border-radius: 20px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal h3 {
  font-size: 1.8rem;
  margin-bottom: 15px;
  color: #667eea;
}

.modal p {
  font-size: 1.1rem;
  margin-bottom: 25px;
  line-height: 1.6;
}

.close-button {
  padding: 12px 30px;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.footer {
  text-align: center;
  padding: 40px 20px;
  opacity: 0.8;
}

.footer p {
  font-size: 0.9rem;
}

```


===== FILE: plugins/individual/motion-framer/skills/motion-framer/assets/starter_motion/src/App.jsx =====

```jsx
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import HoverCard from './components/HoverCard'
import DraggableBox from './components/DraggableBox'
import StaggerList from './components/StaggerList'
import './App.css'

function App() {
  const [showModal, setShowModal] = useState(false)

  return (
    <div className="app">
      <header className="header">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          Motion Starter
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          Framer Motion animation examples
        </motion.p>
      </header>

      <main className="main">
        <section className="section">
          <h2>Hover Animations</h2>
          <div className="grid">
            <HoverCard title="Card 1">
              Hover over me to see the animation
            </HoverCard>
            <HoverCard title="Card 2">
              Different hover effects
            </HoverCard>
            <HoverCard title="Card 3">
              Smooth transitions
            </HoverCard>
          </div>
        </section>

        <section className="section">
          <h2>Drag Interaction</h2>
          <DraggableBox />
        </section>

        <section className="section">
          <h2>Staggered List</h2>
          <StaggerList />
        </section>

        <section className="section">
          <h2>Exit Animations</h2>
          <motion.button
            className="modal-button"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowModal(!showModal)}
          >
            {showModal ? 'Close' : 'Open'} Modal
          </motion.button>

          <AnimatePresence mode="wait">
            {showModal && (
              <motion.div
                key="modal"
                className="modal-backdrop"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setShowModal(false)}
              >
                <motion.div
                  className="modal"
                  initial={{ opacity: 0, scale: 0.9, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9, y: -20 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  onClick={(e) => e.stopPropagation()}
                >
                  <h3>Modal Title</h3>
                  <p>This modal animates in and out smoothly with AnimatePresence.</p>
                  <motion.button
                    className="close-button"
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setShowModal(false)}
                  >
                    Close
                  </motion.button>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>
      </main>

      <footer className="footer">
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Built with Framer Motion
        </motion.p>
      </footer>
    </div>
  )
}

export default App

```


===== FILE: plugins/individual/motion-framer/skills/motion-framer/assets/starter_motion/src/components/DraggableBox.jsx =====

```jsx
import { motion } from 'framer-motion'
import { useState } from 'react'

export default function DraggableBox() {
  const [isDragging, setIsDragging] = useState(false)

  return (
    <div style={{
      height: '300px',
      position: 'relative',
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: '16px',
      border: '2px dashed rgba(255, 255, 255, 0.3)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <motion.div
        drag
        dragConstraints={{
          left: -100,
          right: 100,
          top: -100,
          bottom: 100
        }}
        dragElastic={0.1}
        whileDrag={{
          scale: 1.1,
          cursor: 'grabbing',
          boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)'
        }}
        onDragStart={() => setIsDragging(true)}
        onDragEnd={() => setIsDragging(false)}
        style={{
          width: '150px',
          height: '150px',
          background: isDragging
            ? 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
            : 'rgba(255, 255, 255, 0.2)',
          borderRadius: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'grab',
          userSelect: 'none',
          fontWeight: 'bold',
          fontSize: '1.1rem',
        }}
      >
        {isDragging ? 'Dragging!' : 'Drag me'}
      </motion.div>
    </div>
  )
}

```


===== FILE: plugins/individual/motion-framer/skills/motion-framer/assets/starter_motion/src/components/HoverCard.jsx =====

```jsx
import { motion } from 'framer-motion'

export default function HoverCard({ title, children }) {
  return (
    <motion.div
      className="hover-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{
        scale: 1.05,
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
        transition: { duration: 0.2 }
      }}
      whileTap={{ scale: 0.98 }}
      style={{
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        borderRadius: '16px',
        padding: '30px',
        cursor: 'pointer',
      }}
    >
      <h3 style={{ fontSize: '1.5rem', marginBottom: '10px' }}>{title}</h3>
      <p style={{ opacity: 0.9 }}>{children}</p>
    </motion.div>
  )
}

```


===== FILE: plugins/individual/motion-framer/skills/motion-framer/assets/starter_motion/src/components/StaggerList.jsx =====

```jsx
import { motion } from 'framer-motion'

const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
}

const item = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.5 }
  }
}

export default function StaggerList() {
  const items = [
    { id: 1, title: 'First Item', description: 'Animates first' },
    { id: 2, title: 'Second Item', description: 'Follows with a delay' },
    { id: 3, title: 'Third Item', description: 'Then this one' },
    { id: 4, title: 'Fourth Item', description: 'And finally this' },
  ]

  return (
    <motion.ul
      variants={container}
      initial="hidden"
      animate="visible"
      style={{
        listStyle: 'none',
        maxWidth: '600px',
        margin: '0 auto'
      }}
    >
      {items.map((listItem) => (
        <motion.li
          key={listItem.id}
          variants={item}
          whileHover={{ scale: 1.02, x: 10 }}
          style={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '15px',
            cursor: 'pointer',
          }}
        >
          <h4 style={{ fontSize: '1.2rem', marginBottom: '5px' }}>
            {listItem.title}
          </h4>
          <p style={{ opacity: 0.8 }}>{listItem.description}</p>
        </motion.li>
      ))}
    </motion.ul>
  )
}

```


===== FILE: plugins/individual/motion-framer/skills/motion-framer/assets/starter_motion/src/main.jsx =====

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

```


===== FILE: plugins/individual/motion-framer/skills/motion-framer/assets/starter_motion/vite.config.js =====

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
  },
})

```


# Skill: react-spring-physics


===== FILE: plugins/individual/react-spring-physics/skills/react-spring-physics/SKILL.md =====

---
name: react-spring-physics
description: Physics-based animation library combining React Spring (spring dynamics, gesture integration, 60fps animations) and Popmotion (low-level composable animation utilities, reactive streams). Use when building fluid, natural-feeling UI animations, gesture-driven interfaces, physics simulations, or spring-loaded interactions. Triggers on tasks involving React Spring hooks, spring physics, inertia scrolling, physics-based motion, animation composition, or natural UI movements. Alternative physics approach to motion-framer for more physically accurate animations.
---

# React Spring Physics

Physics-based animation for React applications combining React Spring's declarative spring animations with Popmotion's low-level physics utilities.

## Overview

React Spring provides spring-physics animations that feel natural and interruptible. Unlike duration-based animations, springs calculate motion based on physical properties (mass, tension, friction), resulting in organic, realistic movement. Popmotion complements this with composable animation functions for keyframes, decay, and inertia.

**When to use this skill:**
- Natural, physics-based UI animations
- Gesture-driven interfaces (drag, swipe, scroll)
- Interruptible animations that respond to user input mid-motion
- Smooth transitions that maintain velocity across state changes
- Momentum scrolling and inertia effects

**Core libraries:**
- `@react-spring/web` - React hooks for spring animations
- `@react-spring/three` - Three.js integration
- `popmotion` - Low-level animation utilities (optional, for advanced use cases)

## Core Concepts

### Spring Physics

Springs animate values from current state to target state using physical simulation:

```jsx
import { useSpring, animated } from '@react-spring/web'

function SpringExample() {
  const springs = useSpring({
    from: { opacity: 0, y: -40 },
    to: { opacity: 1, y: 0 },
    config: {
      mass: 1,        // Weight of object
      tension: 170,   // Spring strength
      friction: 26    // Opposing force
    }
  })

  return <animated.div style={springs}>Hello</animated.div>
}
```

### useSpring Hook Patterns

Two initialization patterns for different use cases:

```jsx
// Object config (simpler, auto-updates on prop changes)
const springs = useSpring({
  from: { x: 0 },
  to: { x: 100 }
})

// Function config (more control, returns API for imperative updates)
const [springs, api] = useSpring(() => ({
  from: { x: 0 }
}), [])

// Trigger animation via API
const handleClick = () => {
  api.start({
    from: { x: 0 },
    to: { x: 100 }
  })
}
```

### Spring Configuration Presets

React Spring provides built-in config presets:

```jsx
import { config } from '@react-spring/web'

// Available presets
config.default  // { tension: 170, friction: 26 }
config.gentle   // { tension: 120, friction: 14 }
config.wobbly   // { tension: 180, friction: 12 }
config.stiff    // { tension: 210, friction: 20 }
config.slow     // { tension: 280, friction: 60 }
config.molasses // { tension: 280, friction: 120 }

// Usage
const springs = useSpring({
  from: { x: 0 },
  to: { x: 100 },
  config: config.wobbly
})
```

## Common Patterns

### 1. Click-Triggered Spring Animation

```jsx
import { useSpring, animated } from '@react-spring/web'

function ClickAnimated() {
  const [springs, api] = useSpring(() => ({
    from: { scale: 1 }
  }), [])

  const handleClick = () => {
    api.start({
      from: { scale: 1 },
      to: { scale: 1.2 },
      config: { tension: 300, friction: 10 }
    })
  }

  return (
    <animated.button
      onClick={handleClick}
      style={{
        transform: springs.scale.to(s => `scale(${s})`)
      }}
    >
      Click Me
    </animated.button>
  )
}
```

### 2. Multi-Element Trail Animation

```jsx
import { useTrail, animated } from '@react-spring/web'

function Trail({ items }) {
  const trails = useTrail(items.length, {
    from: { opacity: 0, x: -20 },
    to: { opacity: 1, x: 0 },
    config: config.gentle
  })

  return (
    <div>
      {trails.map((style, i) => (
        <animated.div key={i} style={style}>
          {items[i]}
        </animated.div>
      ))}
    </div>
  )
}
```

### 3. List Transitions (Enter/Exit)

```jsx
import { useTransition, animated } from '@react-spring/web'

function List({ items }) {
  const transitions = useTransition(items, {
    from: { opacity: 0, height: 0 },
    enter: { opacity: 1, height: 80 },
    leave: { opacity: 0, height: 0 },
    config: config.stiff,
    keys: item => item.id
  })

  return transitions((style, item) => (
    <animated.div style={style}>
      {item.text}
    </animated.div>
  ))
}
```

### 4. Scroll-Based Spring Animation

```jsx
import { useScroll, animated } from '@react-spring/web'

function ScrollReveal() {
  const { scrollYProgress } = useScroll()

  return (
    <animated.div
      style={{
        opacity: scrollYProgress.to([0, 0.5], [0, 1]),
        scale: scrollYProgress.to([0, 0.5], [0.8, 1])
      }}
    >
      Scroll to reveal
    </animated.div>
  )
}
```

### 5. Viewport Intersection Animation

```jsx
import { useInView, animated } from '@react-spring/web'

function FadeInOnView() {
  const [ref, springs] = useInView(
    () => ({
      from: { opacity: 0, y: 100 },
      to: { opacity: 1, y: 0 }
    }),
    { rootMargin: '-40% 0%' }
  )

  return <animated.div ref={ref} style={springs}>Content</animated.div>
}
```

### 6. Chained Async Animations

```jsx
import { useSpring, animated } from '@react-spring/web'

function ChainedAnimation() {
  const springs = useSpring({
    from: { x: 0, background: '#ff6d6d' },
    to: [
      { x: 80, background: '#fff59a' },
      { x: 0, background: '#88DFAB' },
      { x: 80, background: '#569AFF' }
    ],
    config: { tension: 200, friction: 20 },
    loop: true
  })

  return <animated.div style={springs} />
}
```

### 7. Spring with Velocity Preservation

```jsx
import { useSpring, animated } from '@react-spring/web'

function VelocityPreservation() {
  const [springs, api] = useSpring(() => ({
    x: 0,
    config: { tension: 300, friction: 30 }
  }), [])

  const handleDragEnd = () => {
    api.start({
      x: 0,
      velocity: springs.x.getVelocity(), // Preserve momentum
      config: { tension: 200, friction: 20 }
    })
  }

  return <animated.div style={springs} onMouseUp={handleDragEnd} />
}
```

## Integration Patterns

### With React Three Fiber (3D)

```jsx
import { useSpring, animated } from '@react-spring/three'
import { Canvas } from '@react-three/fiber'

const AnimatedBox = animated(MeshDistortMaterial)

function ThreeScene() {
  const [clicked, setClicked] = useState(false)

  const springs = useSpring({
    scale: clicked ? 1.5 : 1,
    color: clicked ? '#569AFF' : '#ff6d6d',
    config: { tension: 200, friction: 20 }
  })

  return (
    <Canvas>
      <mesh onClick={() => setClicked(!clicked)} scale={springs.scale}>
        <sphereGeometry args={[1, 64, 32]} />
        <AnimatedBox color={springs.color} />
      </mesh>
    </Canvas>
  )
}
```

### With Popmotion (Low-Level Physics)

```jsx
import { spring, inertia } from 'popmotion'
import { useState } from 'react'

function PopmotionIntegration() {
  const [x, setX] = useState(0)

  const handleDragEnd = (velocity) => {
    inertia({
      from: x,
      velocity: velocity,
      power: 0.3,
      timeConstant: 400,
      modifyTarget: v => Math.round(v / 100) * 100 // Snap to grid
    }).start(setX)
  }

  return <div style={{ transform: `translateX(${x}px)` }} />
}
```

### With Forms and Validation

```jsx
import { useSpring, animated } from '@react-spring/web'

function ValidatedInput() {
  const [error, setError] = useState(false)

  const shakeAnimation = useSpring({
    x: error ? [0, -10, 10, -10, 10, 0] : 0,
    config: { tension: 300, friction: 10 },
    onRest: () => setError(false)
  })

  return <animated.input style={shakeAnimation} />
}
```

## Performance Optimization

### On-Demand Rendering

```jsx
// Only re-render when animation is active
const [springs, api] = useSpring(() => ({
  from: { x: 0 },
  config: { precision: 0.01 } // Higher value = less updates
}), [])
```

### Batch Multiple Springs

```jsx
// Use useSprings for multiple similar animations
const springs = useSprings(
  items.length,
  items.map(item => ({
    from: { opacity: 0 },
    to: { opacity: 1 }
  }))
)
```

### Skip Animation (Testing/Accessibility)

```jsx
import { Globals } from '@react-spring/web'

// Skip all animations (prefers-reduced-motion)
useEffect(() => {
  Globals.assign({ skipAnimation: true })
  return () => Globals.assign({ skipAnimation: false })
}, [])
```

## Common Pitfalls

### 1. Forgetting Dependencies Array

```jsx
// ❌ Wrong: No dependencies, creates new spring every render
const springs = useSpring(() => ({ x: 0 }))

// ✅ Correct: Empty array prevents recreation
const [springs, api] = useSpring(() => ({ x: 0 }), [])
```

### 2. Mutating Spring Values

```jsx
// ❌ Wrong: Direct mutation
springs.x.set(100)

// ✅ Correct: Use API to animate
api.start({ x: 100 })
```

### 3. Ignoring Config Precision

```jsx
// ❌ Default precision too fine (0.0001), causing unnecessary renders
const springs = useSpring({ x: 0 })

// ✅ Set appropriate precision for your use case
const springs = useSpring({
  x: 0,
  config: { precision: 0.01 } // Stop updating when within 0.01 of target
})
```

### 4. Not Handling Velocity

```jsx
// ❌ Abrupt stop when interrupting animation
api.start({ x: 0 })

// ✅ Preserve momentum
api.start({
  x: 0,
  velocity: springs.x.getVelocity()
})
```

### 5. Mixing Config Patterns

```jsx
// ❌ Wrong: Using both object and function config
const springs = useSpring({
  from: { x: 0 }
})
api.start({ x: 100 }) // api is undefined

// ✅ Correct: Use function config for imperative control
const [springs, api] = useSpring(() => ({
  from: { x: 0 }
}), [])
```

### 6. Animating Non-Numerical Values

```jsx
// ❌ Wrong: Spring can't interpolate complex strings directly
const springs = useSpring({ transform: 'translateX(100px) rotate(45deg)' })

// ✅ Correct: Animate individual values
const springs = useSpring({ x: 100, rotation: 45 })
// Then combine: transform: `translateX(${x}px) rotate(${rotation}deg)`
```

## Resources

### Scripts
- `spring_generator.py` - Generate React Spring boilerplate code
- `physics_calculator.py` - Calculate optimal spring physics parameters

### References
- `react_spring_api.md` - Complete React Spring hooks and API reference
- `popmotion_api.md` - Popmotion functions and reactive streams
- `physics_guide.md` - Spring physics deep dive with tuning guide

### Assets
- `starter_spring/` - React + Vite template with React Spring examples
- `examples/` - Real-world patterns (gestures, scroll, 3D integration)

## Related Skills

- **motion-framer** - Alternative declarative animation approach with variants
- **gsap-scrolltrigger** - Timeline-based animations for complex sequences
- **react-three-fiber** - 3D scene management (use @react-spring/three for animations)
- **animated-component-libraries** - Pre-built animated components using Motion

**Physics vs Timeline**: Use React Spring for natural, physics-based motion that responds to user input. Use GSAP for precise, timeline-based choreography and complex multi-step sequences.



===== FILE: plugins/individual/react-spring-physics/skills/react-spring-physics/references/physics_guide.md =====

# Spring Physics Deep Dive

Understanding and tuning spring animations for natural, physically accurate motion.

## Table of Contents

- [Physics Fundamentals](#physics-fundamentals)
- [Spring Parameters](#spring-parameters)
- [Tuning Guide](#tuning-guide)
- [Common Configurations](#common-configurations)
- [Velocity and Momentum](#velocity-and-momentum)
- [Advanced Techniques](#advanced-techniques)

---

## Physics Fundamentals

### What is a Spring Animation?

Unlike duration-based animations (e.g., "move from A to B in 300ms"), spring animations simulate physical motion based on forces:

**Hooke's Law:**
```
F = -k * x

Where:
F = Force applied by spring
k = Spring constant (stiffness)
x = Displacement from rest position
```

**Damping Force:**
```
F_damping = -c * v

Where:
c = Damping coefficient (friction)
v = Velocity
```

**Result:** Natural, bouncy motion that **automatically calculates duration** based on physics.

---

## Spring Parameters

### Mass

**What it does:** Determines object's weight/inertia.

**Effect:**
- **Higher mass** (e.g., 5): Heavier, slower to accelerate/decelerate
- **Lower mass** (e.g., 0.5): Lighter, more responsive

**When to increase:**
- Large UI elements (modals, panels)
- Dramatic, weighty animations
- Slow, deliberate movements

**When to decrease:**
- Small UI elements (tooltips, badges)
- Quick, snappy interactions
- Lightweight, responsive feel

**Example:**
```jsx
// Heavy modal
{ mass: 5, tension: 170, friction: 26 }

// Lightweight tooltip
{ mass: 0.5, tension: 170, friction: 26 }
```

---

### Tension (Stiffness)

**What it does:** Spring's resistance to stretching (spring strength).

**Effect:**
- **Higher tension** (e.g., 300): Faster, stiffer spring
- **Lower tension** (e.g., 100): Slower, softer spring

**When to increase:**
- Quick, responsive interactions
- Snappy button feedback
- Alert animations

**When to decrease:**
- Gentle, smooth transitions
- Organic, flowing motion
- Relaxed page transitions

**Example:**
```jsx
// Snappy button press
{ tension: 300, friction: 20 }

// Gentle fade-in
{ tension: 120, friction: 14 }
```

---

### Friction (Damping)

**What it does:** Opposing force that slows motion.

**Effect:**
- **Higher friction** (e.g., 40): Less overshoot, faster settling
- **Lower friction** (e.g**, 10): More bounce, oscillation

**When to increase:**
- Minimal overshoot desired
- Professional, controlled feel
- Quick settle time

**When to decrease:**
- Playful, bouncy animations
- Noticeable spring effect
- Dramatic overshoot

**Example:**
```jsx
// Minimal bounce (controlled)
{ tension: 170, friction: 40 }

// Bouncy, playful
{ tension: 180, friction: 12 }
```

---

## Tuning Guide

### Step-by-Step Tuning Process

**1. Start with a preset:**
```jsx
import { config } from '@react-spring/web'

// Try these first:
config.default  // Balanced
config.gentle   // Smooth, slow
config.wobbly   // Bouncy
config.stiff    // Fast, minimal bounce
```

**2. Adjust tension for speed:**
```jsx
// Too slow? Increase tension
{ tension: 250, friction: 26 }

// Too fast? Decrease tension
{ tension: 120, friction: 26 }
```

**3. Adjust friction for bounce:**
```jsx
// Too bouncy? Increase friction
{ tension: 170, friction: 35 }

// Not bouncy enough? Decrease friction
{ tension: 170, friction: 15 }
```

**4. Adjust mass for weight:**
```jsx
// Feels too light? Increase mass
{ mass: 3, tension: 170, friction: 26 }

// Too heavy/sluggish? Decrease mass
{ mass: 0.7, tension: 170, friction: 26 }
```

---

### Visual Tuning Tool

React Spring provides an interactive tuning tool:

```jsx
import { useSpring, animated } from '@react-spring/web'
import { useControls } from 'leva'

function Tuner() {
  const config = useControls({
    mass: { value: 1, min: 0.1, max: 10 },
    tension: { value: 170, min: 1, max: 500 },
    friction: { value: 26, min: 1, max: 100 }
  })

  const springs = useSpring({
    from: { x: 0 },
    to: { x: 100 },
    config
  })

  return <animated.div style={springs} />
}
```

Install leva: `npm install leva`

---

## Common Configurations

### By Use Case

**Button Interactions (Quick, Responsive):**
```jsx
{ mass: 1, tension: 300, friction: 20 }
// Fast response, minimal bounce
```

**Modal Animations (Dramatic, Smooth):**
```jsx
{ mass: 2, tension: 150, friction: 30 }
// Weighty, controlled entrance
```

**Page Transitions (Smooth, Professional):**
```jsx
{ mass: 1, tension: 120, friction: 14 }
// Gentle, flowing motion
```

**Notifications/Toasts (Bouncy, Attention-Grabbing):**
```jsx
{ mass: 1, tension: 180, friction: 12 }
// Noticeable bounce, playful
```

**Drag-and-Drop (Natural Physics):**
```jsx
{ mass: 1, tension: 200, friction: 25 }
// Balanced, realistic feel
```

**Loading Indicators (Continuous, Smooth):**
```jsx
{ mass: 1, tension: 100, friction: 30 }
// Slow, controlled oscillation
```

---

### By Animation Feel

**Snappy:**
```jsx
{ mass: 0.8, tension: 300, friction: 20 }
```

**Bouncy:**
```jsx
{ mass: 1, tension: 180, friction: 12 }
```

**Smooth/Gentle:**
```jsx
{ mass: 1, tension: 120, friction: 14 }
```

**Stiff/Controlled:**
```jsx
{ mass: 1, tension: 210, friction: 20 }
```

**Slow/Lazy:**
```jsx
{ mass: 1, tension: 280, friction: 60 }
```

**Heavy/Dramatic:**
```jsx
{ mass: 5, tension: 170, friction: 26 }
```

---

## Velocity and Momentum

### Initial Velocity

Set starting velocity for momentum-based animations:

```jsx
const [springs, api] = useSpring(() => ({
  x: 0,
  config: { tension: 200, friction: 20 }
}), [])

api.start({
  x: 100,
  velocity: 500 // px/second
})
```

### Preserving Velocity (Interruptions)

Maintain momentum when interrupting an animation:

```jsx
const handleInterrupt = () => {
  api.start({
    x: newTarget,
    velocity: springs.x.getVelocity(), // Current velocity
    config: { tension: 300, friction: 25 }
  })
}
```

**Why this matters:**
- Natural feel when user changes direction mid-animation
- Smooth transitions between gesture states
- Realistic physics simulation

---

### Calculating Velocity from Gestures

```jsx
import { useDrag } from '@use-gesture/react'
import { useSpring, animated } from '@react-spring/web'

function DraggableElement() {
  const [{ x }, api] = useSpring(() => ({ x: 0 }))

  const bind = useDrag(({ down, movement: [mx], velocity: [vx] }) => {
    api.start({
      x: down ? mx : 0,
      velocity: vx * 1000, // Convert to px/second
      immediate: down,
      config: { tension: 200, friction: 30 }
    })
  })

  return <animated.div {...bind()} style={{ x }} />
}
```

---

## Advanced Techniques

### Conditional Spring Config

Different physics for different properties:

```jsx
const springs = useSpring({
  x: 100,
  scale: 1.5,
  opacity: 1,
  config: {
    x: { tension: 300, friction: 20 },      // Fast horizontal
    scale: { mass: 4, friction: 10 },       // Heavy scaling
    opacity: { tension: 120, friction: 14 }  // Gentle fade
  }
})
```

### Config as Function

Dynamic configuration based on property:

```jsx
const springs = useSpring({
  x: 100,
  y: 200,
  scale: 1.5,
  config: (key) => {
    if (key === 'scale') {
      return { mass: 4, friction: 10 }
    }
    if (key === 'x') {
      return { tension: 300, friction: 20 }
    }
    return config.default
  }
})
```

### Spring with Clamp

Prevent overshoot entirely:

```jsx
const springs = useSpring({
  x: 100,
  config: {
    tension: 300,
    friction: 20,
    clamp: true // No overshoot
  }
})
```

---

### Duration Override

Force a specific duration (not physically accurate):

```jsx
const springs = useSpring({
  x: 100,
  config: {
    duration: 500,  // Override physics
    easing: t => t  // Linear easing
  }
})
```

**Note:** When using `duration`, the animation is no longer physics-based. It becomes a traditional tween.

---

### Precision Tuning

Control when animation "completes":

```jsx
const springs = useSpring({
  x: 100,
  config: {
    tension: 170,
    friction: 26,
    precision: 0.01 // Stop when within 0.01 of target (default: 0.0001)
  }
})
```

**Higher precision (0.1):**
- Fewer updates
- Earlier completion
- Better performance
- Slight imprecision

**Lower precision (0.0001):**
- More updates
- Exact final value
- Slower performance
- Pixel-perfect

---

## Troubleshooting

### Animation Too Fast

**Solutions:**
1. Decrease `tension` (e.g., 170 → 120)
2. Increase `mass` (e.g., 1 → 2)
3. Increase `friction` (e.g., 26 → 40)

### Animation Too Slow

**Solutions:**
1. Increase `tension` (e.g., 170 → 250)
2. Decrease `mass` (e.g., 1 → 0.7)
3. Decrease `friction` (e.g., 26 → 15)

### Too Much Bounce/Overshoot

**Solutions:**
1. Increase `friction` (e.g., 26 → 40)
2. Enable `clamp: true`
3. Use `config.stiff` preset

### Not Enough Bounce

**Solutions:**
1. Decrease `friction` (e.g., 26 → 12)
2. Use `config.wobbly` preset
3. Increase `tension` slightly (e.g., 170 → 180)

### Animation Never Completes

**Solutions:**
1. Increase `precision` (e.g., 0.0001 → 0.01)
2. Check for conflicting animations
3. Ensure `restSpeed` is not set too low

---

## Mathematical Relationships

### Critical Damping

The point where spring returns to rest without oscillating:

```
c_critical = 2 * sqrt(k * m)

Where:
c = friction
k = tension
m = mass
```

**Damping Ratio:**
```
ζ = c / (2 * sqrt(k * m))

ζ > 1: Over-damped (no overshoot, slow)
ζ = 1: Critically damped (no overshoot, fast)
ζ < 1: Under-damped (overshoot, oscillation)
```

**Example:**
```jsx
// Calculate critically damped friction
const mass = 1
const tension = 170
const criticalFriction = 2 * Math.sqrt(tension * mass)
// criticalFriction ≈ 26 (default React Spring config!)

// Under-damped (bouncy)
{ mass: 1, tension: 170, friction: 12 } // ζ ≈ 0.46

// Critically damped
{ mass: 1, tension: 170, friction: 26 } // ζ = 1

// Over-damped (slow)
{ mass: 1, tension: 170, friction: 40 } // ζ ≈ 1.53
```

---

## Comparison: Duration vs Physics

### Duration-Based (Traditional)

```jsx
// CSS transition
transition: all 300ms ease-in-out;

// React Spring duration override
{ duration: 300, easing: easeInOut }
```

**Pros:**
- Predictable timing
- Easier to sync with other events
- Consistent across devices

**Cons:**
- Feels artificial when interrupted
- Loses momentum on direction change
- Not physically accurate

---

### Physics-Based (Spring)

```jsx
{ mass: 1, tension: 170, friction: 26 }
```

**Pros:**
- Natural, organic feel
- Interruptible without jarring
- Preserves momentum
- Realistic physics

**Cons:**
- Variable duration (depends on distance, velocity)
- Harder to sync precisely
- Requires tuning for desired feel

---

## Best Practices

1. **Start with presets** - Use `config.default`, `config.gentle`, etc.
2. **Tune visually** - Use Leva or similar tool to adjust in real-time
3. **Preserve velocity** - Use `getVelocity()` for interruptions
4. **Set appropriate precision** - Higher for better performance
5. **Test on target devices** - Physics may feel different on slow devices
6. **Use duration sparingly** - Only when exact timing is critical
7. **Document custom configs** - Add comments explaining physics choices
8. **Consistency matters** - Use similar configs for similar interactions

---

## Resources

- [Spring Physics Calculator](https://react-spring.dev/examples/springs) - Interactive tuning
- [Leva](https://github.com/pmndrs/leva) - Real-time config editor
- [Hooke's Law](https://en.wikipedia.org/wiki/Hooke%27s_law) - Physics fundamentals
- [Damped Harmonic Oscillator](https://en.wikipedia.org/wiki/Harmonic_oscillator#Damped_harmonic_oscillator) - Spring theory



===== FILE: plugins/individual/react-spring-physics/skills/react-spring-physics/references/popmotion_api.md =====

# Popmotion API Reference

Low-level animation library providing composable animation functions. Useful for advanced physics simulations and custom animation logic.

## Table of Contents

- [Core Animations](#core-animations)
  - [spring](#spring)
  - [inertia](#inertia)
  - [keyframes](#keyframes)
  - [decay](#decay)
  - [physics](#physics)
- [Animation Control](#animation-control)
- [Easing Functions](#easing-functions)
- [Utilities](#utilities)

---

## Core Animations

### spring

Physics-based spring animation.

**Signature:**
```typescript
spring(config: SpringConfig): Animation
```

**Config Properties:**
```typescript
interface SpringConfig {
  from?: number | object | array
  to?: number | object | array
  stiffness?: number    // Spring strength (default: 100)
  damping?: number      // Opposing force (default: 10)
  mass?: number         // Object mass (default: 1)
  velocity?: number     // Initial velocity (default: 0)
  restSpeed?: number    // Stop threshold (default: 0.001)
  restDelta?: number    // Position threshold (default: 0.01)
}
```

**Examples:**
```javascript
import { spring } from 'popmotion'

// Basic spring
spring({
  from: 0,
  to: 100,
  stiffness: 200,
  damping: 20
}).start(v => console.log(v))

// With velocity
spring({
  from: ballXY.get(),
  velocity: ballXY.getVelocity(),
  stiffness: 300,
  damping: 10
}).start(ballXY)

// Object values
spring({
  from: { x: 0, y: 0 },
  to: { x: 100, y: 200 },
  stiffness: { x: 200, y: 1000 },
  damping: { x: 10, y: 50 }
}).start(({ x, y }) => console.log(x, y))
```

**Value Types:**
- Numbers: `spring({ from: 0, to: 100 })`
- Units: `spring({ from: '0px', to: '100px' })`
- Colors: `spring({ from: '#fff', to: '#000' })`
- Objects: `spring({ from: { x: 0 }, to: { x: 100 } })`
- Arrays: `spring({ from: [0, 0], to: [100, 200] })`

---

### inertia

Momentum-based deceleration with spring-loaded boundaries.

**Signature:**
```typescript
inertia(config: InertiaConfig): Animation
```

**Config Properties:**
```typescript
interface InertiaConfig {
  from?: number
  velocity?: number       // Initial velocity (required)
  power?: number          // Deceleration strength (default: 0.8)
  timeConstant?: number   // Deceleration duration (default: 350)
  restDelta?: number      // Stop threshold (default: 0.5)
  min?: number            // Minimum boundary
  max?: number            // Maximum boundary
  bounceStiffness?: number // Boundary spring strength (default: 500)
  bounceDamping?: number  // Boundary spring damping (default: 10)
  modifyTarget?: (v: number) => number // Snap function
}
```

**Examples:**
```javascript
import { inertia } from 'popmotion'

// Basic momentum scroll
inertia({
  from: 50,
  velocity: 500
}).start(v => console.log(v))

// With boundaries
inertia({
  from: 50,
  velocity: 500,
  min: 0,
  max: 1000,
  bounceStiffness: 1000,
  bounceDamping: 300
}).start(v => console.log(v))

// Snap to grid
inertia({
  from: 50,
  velocity: 200,
  modifyTarget: v => Math.round(v / 100) * 100
}).start(v => console.log(v))
```

**Use Cases:**
- Momentum scrolling
- Swipe-to-dismiss
- Physics-based drag release
- Snap-to-grid animations

---

### keyframes

Animate through a sequence of values.

**Signature:**
```typescript
keyframes(config: KeyframesConfig): Animation
```

**Config Properties:**
```typescript
interface KeyframesConfig {
  values: any[]           // Keyframe values
  times?: number[]        // Progress points (0-1)
  duration?: number       // Total duration (default: 300)
  easings?: Easing[]      // Per-segment easings
}
```

**Examples:**
```javascript
import { keyframes, linear, easeInOut } from 'popmotion'

// Basic keyframes
keyframes({
  values: [0, 100, 200],
  duration: 1000
}).start(v => console.log(v))

// With times and easings
keyframes({
  values: [0, 100, 200],
  times: [0, 0.2, 1],
  duration: 1000,
  easings: [linear, easeInOut]
}).start(v => console.log(v))

// Color animation
keyframes({
  values: ['#fff', '#000', '#f00'],
  duration: 2000
}).start(color => console.log(color))
```

---

### decay

Exponential deceleration (no terminal velocity).

**Signature:**
```typescript
decay(config: DecayConfig): Animation
```

**Config Properties:**
```typescript
interface DecayConfig {
  from?: number
  velocity?: number     // Initial velocity (required)
  power?: number        // Deceleration strength (default: 0.8)
  timeConstant?: number // Controls decay rate (default: 350)
  restDelta?: number    // Stop threshold (default: 0.5)
  modifyTarget?: (v: number) => number
}
```

**Example:**
```javascript
import { decay } from 'popmotion'

decay({
  from: 0,
  velocity: 1000,
  power: 0.8,
  timeConstant: 400
}).start(v => console.log(v))
```

---

### physics

Integrated physics simulation (velocity, acceleration, friction, springs).

**Signature:**
```typescript
physics(config: PhysicsConfig): Animation
```

**Config Properties:**
```typescript
interface PhysicsConfig {
  from?: number
  velocity?: number         // Units per second (default: 0)
  acceleration?: number     // Increase velocity (default: 0)
  friction?: number         // 0-1 deceleration (default: 0)
  springStrength?: number   // Spring force (with `to`)
  to?: number               // Spring target (with `springStrength`)
  restSpeed?: number        // Stop threshold (default: 0.001)
}
```

**Examples:**
```javascript
import { physics } from 'popmotion'

// Accelerating object
physics({
  from: 0,
  velocity: 0,
  acceleration: 100
}).start(v => console.log(v))

// Friction-based deceleration
physics({
  from: 0,
  velocity: 1000,
  friction: 0.8
}).start(v => console.log(v))

// Spring simulation
physics({
  from: 0,
  velocity: 1000,
  friction: 0.8,
  to: 400,
  springStrength: 500
}).start(v => console.log(v))
```

**Playback Methods:**
```javascript
const animation = physics({ from: 0, velocity: 100 }).start(v => {})

animation.setVelocity(500)
animation.setAcceleration(200)
animation.setFriction(0.9)
animation.setSpringStrength(600)
animation.setSpringTarget(500)
animation.stop()
```

---

## Animation Control

All animations return playback controls via `.start()`.

**Basic Start:**
```javascript
animation.start(v => {
  // Update callback
})
```

**With Complete Callback:**
```javascript
animation.start({
  update: v => { /* on update */ },
  complete: () => { /* on complete */ }
})
```

**Common Methods:**
```javascript
const controls = animation.start(v => {})

controls.stop()  // Stop animation
```

**Chaining Methods:**
```javascript
// Filter values
spring({ from: 0, to: 100 })
  .filter(v => v > 50)
  .start(v => console.log(v)) // Only outputs values > 50

// Transform output
spring({ from: 0, to: 100 })
  .pipe(Math.round, v => v * 2)
  .start(v => console.log(v)) // Rounded and doubled

// Conditional completion
spring({ from: 0, to: 100 })
  .while(v => v < 75)
  .start(v => console.log(v)) // Stops when v >= 75
```

---

## Easing Functions

**Importing:**
```javascript
import {
  linear,
  easeIn, easeOut, easeInOut,
  circIn, circOut, circInOut,
  backIn, backOut, backInOut,
  anticipate,
  cubicBezier
} from 'popmotion'
```

**Built-in Easings:**
- `linear` - Constant speed
- `easeIn, easeOut, easeInOut` - Quadratic easing
- `circIn, circOut, circInOut` - Circular easing
- `backIn, backOut, backInOut` - Back easing (overshoot)
- `anticipate` - Pull back then overshoot

**Custom Cubic Bezier:**
```javascript
import { cubicBezier } from 'popmotion'

const customEase = cubicBezier(0.17, 0.67, 0.83, 0.67)
```

**Creating Custom Easings:**
```javascript
import {
  createExpoIn,
  createBackIn,
  createAnticipate,
  mirrorEasing,
  reverseEasing
} from 'popmotion'

// Exponential easing
const expoIn = createExpoIn(4)
const expoOut = mirrorEasing(expoIn)
const expoInOut = reverseEasing(expoIn)

// Back easing with custom overshoot
const backIn = createBackIn(4)

// Anticipate with custom power
const anticipate = createAnticipate(4)
```

**Usage with Keyframes:**
```javascript
import { keyframes, easeInOut } from 'popmotion'

keyframes({
  values: [0, 100],
  duration: 1000,
  easings: [easeInOut]
}).start(v => console.log(v))
```

---

## Utilities

### animate

High-level animation API (similar to GSAP/CSS animations).

```javascript
import { animate, spring, linear } from 'popmotion'

// Duration-based
animate({
  from: 0,
  to: 100,
  duration: 1000,
  ease: linear
}).start(v => console.log(v))

// Spring-based
animate({
  from: 0,
  to: 100,
  type: 'spring',
  stiffness: 1000,
  damping: 50
}).start(v => console.log(v))
```

### Multi-value Animations

**Objects:**
```javascript
spring({
  from: { x: 0, y: 0 },
  to: { x: 100, y: 200 }
}).start(({ x, y }) => {
  console.log(`x: ${x}, y: ${y}`)
})
```

**Arrays:**
```javascript
spring({
  from: [0, 0],
  to: [100, 200]
}).start(([x, y]) => {
  console.log(`x: ${x}, y: ${y}`)
})
```

**Complex Strings:**
```javascript
spring({
  from: '0px 0px 0px inset rgba(0, 0, 0, 0.2)',
  to: '3px 3px 10px inset rgba(0, 0, 0, 0.5)'
}).start(shadow => {
  element.style.boxShadow = shadow
})
```

---

## Integration with React Spring

Popmotion is typically used for advanced use cases where React Spring's declarative API isn't sufficient.

**Example: Custom Physics:**
```jsx
import { physics } from 'popmotion'
import { useState, useEffect } from 'react'

function CustomPhysics() {
  const [x, setX] = useState(0)

  const handleDragEnd = (velocity) => {
    physics({
      from: x,
      velocity: velocity,
      friction: 0.8,
      to: 0,
      springStrength: 500
    }).start(setX)
  }

  return <div style={{ transform: `translateX(${x}px)` }} />
}
```

**Example: Snap-to-Grid Inertia:**
```jsx
import { inertia } from 'popmotion'
import { useState } from 'react'

function SnapGrid() {
  const [x, setX] = useState(0)

  const handleDragEnd = (velocity) => {
    inertia({
      from: x,
      velocity: velocity,
      modifyTarget: v => Math.round(v / 100) * 100,
      bounceStiffness: 1000,
      bounceDamping: 300
    }).start(setX)
  }

  return <div style={{ transform: `translateX(${x}px)` }} />
}
```

---

## Performance Notes

1. **Composable** - Chain `.filter()`, `.pipe()`, `.while()` for custom behavior
2. **Low-level** - No React overhead, direct DOM manipulation
3. **Tree-shakeable** - Import only what you need
4. **Zero dependencies** - Tiny bundle size (~5KB)
5. **60fps** - Optimized for frame-based updates

---

## Common Patterns

### Drag with Inertia

```javascript
import { inertia } from 'popmotion'

let velocity = 0

// Track velocity during drag
const handleDrag = (dx, dt) => {
  velocity = dx / dt
}

// Apply inertia on release
const handleDragEnd = () => {
  inertia({
    from: currentX,
    velocity: velocity,
    power: 0.8,
    timeConstant: 400
  }).start(setX)
}
```

### Spring Taper (Follow Pointer)

```javascript
import { physics } from 'popmotion'

const springTo = physics({
  velocity: ballXY.getVelocity(),
  friction: 0.6,
  springStrength: 400,
  to: ballXY.get(),
  restSpeed: false
}).start(ballXY)

pointer(ballXY.get())
  .start(v => springTo.setSpringTarget(v))
```

### Boundary Constraints

```javascript
import { spring } from 'popmotion'

const handleRelease = () => {
  const x = handleX.get()

  if (x < 0 || x > 250) {
    spring({
      from: x,
      to: x < 0 ? 0 : 250,
      velocity: handleX.getVelocity(),
      stiffness: 900,
      damping: 30
    }).start(handleX)
  } else {
    handleX.stop()
  }
}
```



===== FILE: plugins/individual/react-spring-physics/skills/react-spring-physics/references/react_spring_api.md =====

# React Spring API Reference

Complete API documentation for React Spring hooks, components, and utilities.

## Table of Contents

- [Core Hooks](#core-hooks)
  - [useSpring](#usespring)
  - [useSprings](#usesprings)
  - [useTrail](#usetrail)
  - [useTransition](#usetransition)
  - [useSpringValue](#usespringvalue)
- [Utility Hooks](#utility-hooks)
  - [useScroll](#usescroll)
  - [useInView](#useinview)
  - [useSpringRef](#usespringref)
  - [useIsomorphicLayoutEffect](#useisomorphiclayouteffect)
- [Components](#components)
  - [animated](#animated)
- [Configuration](#configuration)
  - [Config Presets](#config-presets)
  - [Config Properties](#config-properties)
- [API Methods](#api-methods)
  - [SpringRef API](#springref-api)
  - [SpringValue Methods](#springvalue-methods)
- [Events](#events)
- [Globals](#globals)

---

## Core Hooks

### useSpring

Create a single spring animation.

**TypeScript Signature (Object Config):**
```typescript
function useSpring(config: SpringConfig): SpringValues
```

**TypeScript Signature (Function Config):**
```typescript
function useSpring(
  configFn: () => SpringConfig,
  deps?: any[]
): [SpringValues, SpringRef]
```

**Parameters:**
- `config` or `configFn` - Animation configuration
- `deps` - Dependency array for re-evaluation (function config only)

**Returns:**
- Object config: `SpringValues` for rendering
- Function config: `[SpringValues, SpringRef]` tuple

**Example (Object Config):**
```jsx
const springs = useSpring({
  from: { opacity: 0 },
  to: { opacity: 1 },
  config: { tension: 170, friction: 26 }
})
```

**Example (Function Config):**
```jsx
const [springs, api] = useSpring(() => ({
  from: { opacity: 0 },
  config: { tension: 170, friction: 26 }
}), [])

// Trigger animation imperatively
api.start({ to: { opacity: 1 } })
```

---

### useSprings

Create multiple spring animations with a unified API.

**TypeScript Signature (Object Config):**
```typescript
function useSprings(count: number, config: SpringConfig): SpringValues[]
```

**TypeScript Signature (Function Config):**
```typescript
function useSprings(
  count: number,
  configFn: (index: number) => SpringConfig,
  deps?: any[]
): [SpringValues[], SpringRef]
```

**Parameters:**
- `count` - Number of springs to create
- `config` or `configFn` - Configuration (function receives index)
- `deps` - Dependency array for re-evaluation

**Returns:**
- Object config: `SpringValues[]` array
- Function config: `[SpringValues[], SpringRef]` tuple

**Example:**
```jsx
const springs = useSprings(
  items.length,
  items.map((item, i) => ({
    from: { opacity: 0, x: -20 },
    to: { opacity: 1, x: 0 },
    delay: i * 100
  }))
)
```

---

### useTrail

Create a trailing animation where each spring follows the previous.

**TypeScript Signature (Object Config):**
```typescript
function useTrail(count: number, config: SpringConfig): SpringValues[]
```

**TypeScript Signature (Function Config):**
```typescript
function useTrail(
  count: number,
  configFn: () => SpringConfig,
  deps?: any[]
): [SpringValues[], SpringRef]
```

**Example:**
```jsx
const trails = useTrail(5, {
  from: { opacity: 0, x: -20 },
  to: { opacity: 1, x: 0 },
  config: config.gentle
})
```

---

### useTransition

Animate a dataset with enter/leave transitions.

**TypeScript Signature (Object Config):**
```typescript
function useTransition<Item>(
  data: Item[],
  config: TransitionConfig<Item>
): TransitionFn
```

**TypeScript Signature (Function Config):**
```typescript
function useTransition<Item>(
  data: Item[],
  configFn: () => TransitionConfig<Item>,
  deps?: any[]
): [TransitionFn, SpringRef]
```

**TransitionConfig Properties:**
- `from` - Initial styles for entering items
- `enter` - Target styles for entered items
- `leave` - Exit styles for leaving items
- `update` - Styles for items that update (optional)
- `keys` - Function or key to identify items

**Example:**
```jsx
const transitions = useTransition(items, {
  from: { opacity: 0, height: 0 },
  enter: { opacity: 1, height: 80 },
  leave: { opacity: 0, height: 0 },
  keys: item => item.id
})

return transitions((style, item) => (
  <animated.div style={style}>{item.text}</animated.div>
))
```

---

### useSpringValue

Create a single animated value.

**TypeScript Signature:**
```typescript
function useSpringValue<T>(
  initial: T,
  config?: SpringConfig
): SpringValue<T>
```

**Example:**
```jsx
const opacity = useSpringValue(0, {
  config: { mass: 2, friction: 5, tension: 80 }
})

// Update value
opacity.start(1)
```

---

## Utility Hooks

### useScroll

Track scroll position with spring physics.

**TypeScript Signature:**
```typescript
function useScroll(config?: ScrollConfig): {
  scrollX: SpringValue<number>
  scrollY: SpringValue<number>
  scrollXProgress: SpringValue<number>
  scrollYProgress: SpringValue<number>
}
```

**ScrollConfig Properties:**
- `container` - Scroll container ref (default: window)
- `config` - Spring configuration

**Example:**
```jsx
const { scrollYProgress } = useScroll()

return (
  <animated.div style={{ opacity: scrollYProgress }}>
    Fades in as you scroll
  </animated.div>
)
```

---

### useInView

Trigger animation when element enters viewport.

**TypeScript Signature:**
```typescript
function useInView<T extends HTMLElement>(
  configFn: () => SpringConfig,
  options?: IntersectionObserverInit
): [RefCallback<T>, SpringValues]
```

**Options (IntersectionObserverInit):**
- `root` - Viewport element (default: browser viewport)
- `rootMargin` - Margin around root (e.g., '-40% 0%')
- `threshold` - Visibility threshold (0-1)

**Example:**
```jsx
const [ref, springs] = useInView(
  () => ({
    from: { opacity: 0, y: 100 },
    to: { opacity: 1, y: 0 }
  }),
  { rootMargin: '-20% 0%' }
)

return <animated.div ref={ref} style={springs}>Content</animated.div>
```

---

### useSpringRef

Create a ref for controlling springs imperatively.

**TypeScript Signature:**
```typescript
function useSpringRef(): SpringRef
```

**Example:**
```jsx
const api = useSpringRef()

const springs = useSpring({
  ref: api,
  from: { opacity: 0 },
  to: { opacity: 1 }
})

// Control via ref
api.start({ opacity: 0.5 })
```

---

### useIsomorphicLayoutEffect

Cross-platform useLayoutEffect (server-safe).

**TypeScript Signature:**
```typescript
function useIsomorphicLayoutEffect(
  effect: EffectCallback,
  deps?: DependencyList
): void
```

**Usage:**
Use like `useLayoutEffect` but works on server-side rendering.

---

## Components

### animated

Higher-Order Component to make elements animatable.

**Built-in Animated Components:**
```jsx
import { animated } from '@react-spring/web'

animated.div
animated.span
animated.p
animated.svg
animated.path
animated.g
// ... all HTML elements
```

**Custom Component Animation:**
```jsx
import { animated } from '@react-spring/web'
import { CustomComponent } from './CustomComponent'

const AnimatedCustom = animated(CustomComponent)

// Component must forward style prop to native element
function CustomComponent({ style, ...props }) {
  return <div style={style} {...props} />
}
```

**Three.js Integration:**
```jsx
import { animated } from '@react-spring/three'
import { MeshDistortMaterial } from '@react-three/drei'

const AnimatedMaterial = animated(MeshDistortMaterial)
```

---

## Configuration

### Config Presets

Pre-defined spring configurations for common animation feels.

```jsx
import { config } from '@react-spring/web'

config.default  // { tension: 170, friction: 26 }
config.gentle   // { tension: 120, friction: 14 }
config.wobbly   // { tension: 180, friction: 12 }
config.stiff    // { tension: 210, friction: 20 }
config.slow     // { tension: 280, friction: 60 }
config.molasses // { tension: 280, friction: 120 }
```

**Usage:**
```jsx
useSpring({
  from: { x: 0 },
  to: { x: 100 },
  config: config.wobbly
})
```

---

### Config Properties

Fine-tune spring physics manually.

**SpringConfig Interface:**
```typescript
interface SpringConfig {
  mass?: number          // Mass of object (default: 1)
  tension?: number       // Spring strength (default: 170)
  friction?: number      // Opposing force (default: 26)
  clamp?: boolean        // Prevent overshooting (default: false)
  precision?: number     // Stop threshold (default: 0.0001)
  velocity?: number      // Initial velocity (default: 0)
  duration?: number      // Override physics with fixed duration
  easing?: EasingFunction // Easing function (requires duration)
  bounce?: number        // Bounce factor 0-1 (alternative to tension/friction)
}
```

**Property-Specific Config:**
```jsx
useSpring({
  x: 100,
  y: 200,
  config: {
    x: { tension: 300, friction: 20 }, // Fast horizontal
    y: { tension: 100, friction: 30 }  // Slow vertical
  }
})
```

**Config as Function:**
```jsx
useSpring({
  x: 100,
  scale: 1.5,
  config: (key) => {
    if (key === 'scale') return { mass: 4, friction: 10 }
    return config.default
  }
})
```

---

## API Methods

### SpringRef API

Imperative control interface returned by function-config hooks.

**Methods:**

#### api.start(config)

Start or update animation.

```jsx
api.start({
  from: { x: 0 },
  to: { x: 100 },
  config: { tension: 200 },
  onRest: () => console.log('Done!')
})
```

#### api.pause()

Pause all animations.

```jsx
api.pause()
```

#### api.resume()

Resume paused animations.

```jsx
api.resume()
```

#### api.stop()

Stop all animations immediately.

```jsx
api.stop()
```

#### api.set(values)

Instantly set values without animating.

```jsx
api.set({ x: 100, opacity: 1 })
```

---

### SpringValue Methods

Methods available on individual SpringValue instances.

**get()** - Get current value:
```jsx
const currentX = springs.x.get()
```

**getVelocity()** - Get current velocity:
```jsx
const velocity = springs.x.getVelocity()
```

**to()** - Transform value:
```jsx
<animated.div
  style={{
    transform: springs.x.to(x => `translateX(${x}px)`)
  }}
/>
```

**start()** - Animate this value:
```jsx
springs.opacity.start(1)
```

---

## Events

Event callbacks for animation lifecycle.

**Event Properties:**
```typescript
interface AnimationProps {
  onStart?: (result: AnimationResult) => void
  onChange?: (result: AnimationResult) => void
  onRest?: (result: AnimationResult) => void
  onPause?: () => void
  onResume?: () => void
}
```

**Global Events:**
```jsx
useSpring({
  x: 100,
  onStart: () => console.log('Animation started'),
  onRest: () => console.log('Animation completed')
})
```

**Key-Specific Events:**
```jsx
useSpring({
  x: 100,
  y: 200,
  onStart: {
    x: () => console.log('x started'),
    y: () => console.log('y started')
  }
})
```

---

## Globals

Global configuration for all animations.

**Globals.assign(config):**

```jsx
import { Globals } from '@react-spring/web'

// Skip all animations (accessibility)
Globals.assign({ skipAnimation: true })

// Custom frame loop
Globals.assign({ frameLoop: 'always' }) // or 'demand'

// Custom performance now
Globals.assign({ now: () => performance.now() })
```

**Common Use Cases:**

```jsx
// Prefers reduced motion
useEffect(() => {
  const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
  Globals.assign({ skipAnimation: mediaQuery.matches })
}, [])

// Testing mode
if (process.env.NODE_ENV === 'test') {
  Globals.assign({ skipAnimation: true })
}
```

---

## Advanced Patterns

### Chaining Animations

```jsx
const springs = useSpring({
  from: { x: 0, background: '#ff6d6d' },
  to: [
    { x: 100, background: '#fff59a' },
    { x: 0, background: '#88DFAB' }
  ],
  loop: true
})
```

### Async to Function

```jsx
const springs = useSpring({
  from: { x: 0 },
  to: async (next) => {
    await next({ x: 100 })
    await next({ x: 50 })
    await next({ x: 0 })
  }
})
```

### Conditional Animation

```jsx
const [springs, api] = useSpring(() => ({
  x: 0
}), [])

useEffect(() => {
  if (condition) {
    api.start({ x: 100 })
  } else {
    api.start({ x: 0 })
  }
}, [condition])
```

### Interpolation

```jsx
<animated.div
  style={{
    transform: springs.x.to({
      range: [0, 0.5, 1],
      output: ['translateX(0px)', 'translateX(50px)', 'translateX(100px)']
    })
  }}
/>
```

---

## Performance Tips

1. **Use function config for imperative control** - Avoids recreation on render
2. **Set appropriate precision** - Higher values reduce updates
3. **Batch similar animations** - Use `useSprings` for multiple similar items
4. **Skip animations in tests** - Use `Globals.assign({ skipAnimation: true })`
5. **Avoid animating layout** - Prefer transforms and opacity
6. **Use `immediate` for instant changes** - `api.start({ x: 100, immediate: true })`

---

## TypeScript Support

React Spring is fully typed. Key interfaces:

```typescript
import type {
  SpringValue,
  SpringValues,
  SpringRef,
  SpringConfig,
  AnimationResult
} from '@react-spring/web'
```

**Typing Custom Animations:**
```typescript
interface MySpringValues {
  x: number
  opacity: number
  color: string
}

const springs = useSpring<MySpringValues>({
  from: { x: 0, opacity: 0, color: '#fff' },
  to: { x: 100, opacity: 1, color: '#000' }
})
```



===== FILE: plugins/individual/react-spring-physics/agents/react-spring-physics-choreographer.md =====

# React Spring Animation Choreographer

## Role

Expert animation choreographer specializing in React Spring animation design, timing, and orchestration.

## Expertise

- Animation timing and easing
- Timeline sequencing
- Performance-optimized animations
- Cross-library animation integration
- Interactive animation patterns
- Scroll-driven animation design

## When to use

Activate this agent when working on:
- Complex animation sequences
- Multi-element choreography
- Scroll-triggered animations
- Interactive animation systems
- Animation performance optimization

## Approach

1. Understand animation goals and user experience
2. Design animation timing and sequencing
3. Implement using React Spring best practices
4. Optimize for smooth 60fps performance
5. Test across devices and browsers

## Tools

This agent has access to:
- React Spring skill knowledge
- Animation pattern libraries
- Performance optimization techniques
- Timeline management strategies



===== FILE: plugins/individual/react-spring-physics/commands/physics_calculator.md =====

# /react-spring-physics-physics_calculator

React Spring - Physics Calculator

## Description

Executes the physics_calculator script for React Spring.

## Usage

```bash
/react-spring-physics-physics_calculator
```

## Implementation

This command runs the `physics_calculator.py` script from the React Spring skill, which provides automated assistance for physics calculator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/react-spring-physics/commands/spring_generator.md =====

# /react-spring-physics-spring_generator

React Spring - Spring Generator

## Description

Executes the spring_generator script for React Spring.

## Usage

```bash
/react-spring-physics-spring_generator
```

## Implementation

This command runs the `spring_generator.py` script from the React Spring skill, which provides automated assistance for spring generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/react-spring-physics/skills/react-spring-physics/scripts/physics_calculator.py =====

```py
#!/usr/bin/env python3
"""
Spring Physics Calculator

Calculate optimal spring physics parameters for desired animation feel.

Usage:
    ./physics_calculator.py                          # Interactive mode
    ./physics_calculator.py --feel bouncy            # Calculate preset
    ./physics_calculator.py --tension 200 --friction 20  # Custom params
    ./physics_calculator.py --critical-damping --tension 170  # Calculate critical

Physics Concepts:
    - Mass: Weight/inertia of animated object
    - Tension: Spring strength (higher = faster)
    - Friction: Opposing force (higher = less bounce)
    - Critical Damping: No overshoot, fastest settle time
"""

import sys
import argparse
import math
from textwrap import dedent


# Preset configurations
PRESETS = {
    'default': {'mass': 1, 'tension': 170, 'friction': 26},
    'gentle': {'mass': 1, 'tension': 120, 'friction': 14},
    'wobbly': {'mass': 1, 'tension': 180, 'friction': 12},
    'stiff': {'mass': 1, 'tension': 210, 'friction': 20},
    'slow': {'mass': 1, 'tension': 280, 'friction': 60},
    'molasses': {'mass': 1, 'tension': 280, 'friction': 120},
    'snappy': {'mass': 0.8, 'tension': 300, 'friction': 20},
    'bouncy': {'mass': 1, 'tension': 180, 'friction': 12},
    'smooth': {'mass': 1, 'tension': 120, 'friction': 14},
    'heavy': {'mass': 5, 'tension': 170, 'friction': 26}
}


def calculate_damping_ratio(mass, tension, friction):
    """Calculate damping ratio (ζ) from spring parameters."""
    critical_friction = 2 * math.sqrt(tension * mass)
    damping_ratio = friction / critical_friction
    return damping_ratio


def calculate_critical_friction(mass, tension):
    """Calculate critical damping friction."""
    return 2 * math.sqrt(tension * mass)


def classify_damping(damping_ratio):
    """Classify damping behavior."""
    if damping_ratio < 1:
        return "Under-damped (oscillates/bounces)"
    elif damping_ratio == 1:
        return "Critically damped (no overshoot, fastest)"
    else:
        return "Over-damped (slow, no overshoot)"


def estimate_settle_time(mass, tension, friction):
    """Estimate approximate settle time in milliseconds."""
    damping_ratio = calculate_damping_ratio(mass, tension, friction)
    natural_frequency = math.sqrt(tension / mass)

    if damping_ratio >= 1:
        # Over-damped or critically damped
        settle_time = 4 / (damping_ratio * natural_frequency)
    else:
        # Under-damped
        damped_frequency = natural_frequency * math.sqrt(1 - damping_ratio**2)
        settle_time = 4 / (damping_ratio * natural_frequency)

    return settle_time * 1000  # Convert to ms


def display_config(config, name=None):
    """Display spring configuration with analysis."""
    mass = config['mass']
    tension = config['tension']
    friction = config['friction']

    damping_ratio = calculate_damping_ratio(mass, tension, friction)
    critical_friction = calculate_critical_friction(mass, tension)
    classification = classify_damping(damping_ratio)
    settle_time = estimate_settle_time(mass, tension, friction)

    if name:
        print(f"\n{'=' * 60}")
        print(f"Spring Configuration: {name}")
        print(f"{'=' * 60}")
    else:
        print(f"\n{'=' * 60}")
        print(f"Spring Configuration Analysis")
        print(f"{'=' * 60}")

    print(f"\nParameters:")
    print(f"  mass:     {mass}")
    print(f"  tension:  {tension}")
    print(f"  friction: {friction}")

    print(f"\nPhysics Analysis:")
    print(f"  Damping ratio (ζ):      {damping_ratio:.3f}")
    print(f"  Critical friction:      {critical_friction:.2f}")
    print(f"  Classification:         {classification}")
    print(f"  Est. settle time:       ~{settle_time:.0f}ms")

    print(f"\nReact Spring Code:")
    print(f"  config: {{ mass: {mass}, tension: {tension}, friction: {friction} }}")

    if abs(damping_ratio - 1.0) < 0.05:
        print(f"\n💡 Near critically damped - very efficient!")
    elif damping_ratio < 0.5:
        print(f"\n💡 Very bouncy - expect multiple oscillations")
    elif damping_ratio > 1.5:
        print(f"\n💡 Heavily damped - may feel sluggish")


def interactive_mode():
    """Run calculator in interactive mode."""
    print("Spring Physics Calculator")
    print("=" * 60)
    print("\nChoose an option:")
    print("  1. Use preset configuration")
    print("  2. Enter custom parameters")
    print("  3. Calculate critical damping")
    print("\nChoice (1-3): ", end='')

    try:
        choice = input().strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nCancelled.")
        return

    if choice == '1':
        # Preset mode
        print("\nAvailable presets:\n")
        for i, (name, config) in enumerate(PRESETS.items(), 1):
            print(f"  {i:2}. {name:12} - mass: {config['mass']}, tension: {config['tension']}, friction: {config['friction']}")

        print(f"\nSelect preset (1-{len(PRESETS)}): ", end='')
        try:
            preset_choice = int(input().strip()) - 1
            preset_name = list(PRESETS.keys())[preset_choice]
            config = PRESETS[preset_name]
            display_config(config, preset_name)
        except (ValueError, IndexError, KeyboardInterrupt, EOFError):
            print("\nInvalid selection.")
            return

    elif choice == '2':
        # Custom parameters
        try:
            print("\nEnter parameters:")
            mass = float(input("  mass (default 1): ") or 1)
            tension = float(input("  tension (default 170): ") or 170)
            friction = float(input("  friction (default 26): ") or 26)

            config = {'mass': mass, 'tension': tension, 'friction': friction}
            display_config(config)
        except (ValueError, KeyboardInterrupt, EOFError):
            print("\nInvalid input.")
            return

    elif choice == '3':
        # Critical damping calculator
        try:
            print("\nCalculate critical damping:")
            mass = float(input("  mass (default 1): ") or 1)
            tension = float(input("  tension (default 170): ") or 170)

            critical_friction = calculate_critical_friction(mass, tension)
            config = {'mass': mass, 'tension': tension, 'friction': critical_friction}

            print(f"\n✅ Critical friction: {critical_friction:.2f}")
            display_config(config, "Critically Damped")
        except (ValueError, KeyboardInterrupt, EOFError):
            print("\nInvalid input.")
            return
    else:
        print("\nInvalid choice.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Calculate spring physics parameters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent('''
        Examples:
          ./physics_calculator.py                      # Interactive mode
          ./physics_calculator.py --feel bouncy        # Use preset
          ./physics_calculator.py --mass 2 --tension 200 --friction 30
          ./physics_calculator.py --critical --tension 170 --mass 1
          ./physics_calculator.py --list               # List presets
        ''')
    )

    parser.add_argument(
        '--feel',
        choices=list(PRESETS.keys()),
        help='Use preset configuration'
    )

    parser.add_argument(
        '--mass', '-m',
        type=float,
        default=1,
        help='Object mass (default: 1)'
    )

    parser.add_argument(
        '--tension', '-t',
        type=float,
        default=170,
        help='Spring tension/stiffness (default: 170)'
    )

    parser.add_argument(
        '--friction', '-f',
        type=float,
        help='Spring friction/damping'
    )

    parser.add_argument(
        '--critical', '-c',
        action='store_true',
        help='Calculate critical damping friction'
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all preset configurations'
    )

    args = parser.parse_args()

    if args.list:
        print("\nAvailable preset configurations:\n")
        for name, config in PRESETS.items():
            damping_ratio = calculate_damping_ratio(config['mass'], config['tension'], config['friction'])
            print(f"  {name:12} - mass: {config['mass']:3}, tension: {config['tension']:3}, friction: {config['friction']:3}  (ζ={damping_ratio:.2f})")
        return 0

    if args.feel:
        config = PRESETS[args.feel]
        display_config(config, args.feel)
        return 0

    if args.critical:
        critical_friction = calculate_critical_friction(args.mass, args.tension)
        config = {'mass': args.mass, 'tension': args.tension, 'friction': critical_friction}
        display_config(config, "Critically Damped")
        return 0

    if args.friction is not None:
        config = {'mass': args.mass, 'tension': args.tension, 'friction': args.friction}
        display_config(config)
        return 0

    # No arguments - interactive mode
    interactive_mode()
    return 0


if __name__ == '__main__':
    sys.exit(main())

```


===== FILE: plugins/individual/react-spring-physics/skills/react-spring-physics/scripts/spring_generator.py =====

```py
#!/usr/bin/env python3
"""
React Spring Animation Generator

Generates React Spring boilerplate code for common animation patterns.

Usage:
    ./spring_generator.py                    # Interactive mode
    ./spring_generator.py --type click       # Generate click animation
    ./spring_generator.py --type scroll      # Generate scroll animation
    ./spring_generator.py --help             # Show help

Animation Types:
    click       - Click-triggered spring animation
    scroll      - Scroll-based spring animation
    trail       - Multi-element trail animation
    transition  - List enter/exit transitions
    inview      - Viewport intersection animation
    chain       - Chained async animations
    gesture     - Gesture-driven animation (drag)
"""

import sys
import argparse
from textwrap import dedent


ANIMATION_TYPES = {
    'click': {
        'name': 'Click-Triggered Spring',
        'code': '''import { useSpring, animated } from '@react-spring/web'

function ClickAnimation() {
  const [springs, api] = useSpring(() => ({
    from: { scale: 1 }
  }), [])

  const handleClick = () => {
    api.start({
      from: { scale: 1 },
      to: { scale: 1.2 },
      config: { tension: 300, friction: 10 }
    })
  }

  return (
    <animated.button
      onClick={handleClick}
      style={{
        transform: springs.scale.to(s => `scale($${s})`)
      }}
    >
      Click Me
    </animated.button>
  )
}

export default ClickAnimation'''
    },
    'scroll': {
        'name': 'Scroll-Based Spring',
        'code': '''import { useScroll, animated } from '@react-spring/web'

function ScrollAnimation() {
  const { scrollYProgress } = useScroll()

  return (
    <animated.div
      style={{
        opacity: scrollYProgress.to([0, 0.5], [0, 1]),
        scale: scrollYProgress.to([0, 0.5], [0.8, 1])
      }}
    >
      Scroll to reveal
    </animated.div>
  )
}

export default ScrollAnimation'''
    },
    'trail': {
        'name': 'Multi-Element Trail',
        'code': '''import { useTrail, animated, config } from '@react-spring/web'

function TrailAnimation({ items }) {
  const trails = useTrail(items.length, {
    from: { opacity: 0, x: -20 },
    to: { opacity: 1, x: 0 },
    config: config.gentle
  })

  return (
    <div>
      {trails.map((style, i) => (
        <animated.div key={i} style={style}>
          {items[i]}
        </animated.div>
      ))}
    </div>
  )
}

export default TrailAnimation'''
    },
    'transition': {
        'name': 'List Enter/Exit Transitions',
        'code': '''import { useTransition, animated, config } from '@react-spring/web'

function TransitionAnimation({ items }) {
  const transitions = useTransition(items, {
    from: { opacity: 0, height: 0 },
    enter: { opacity: 1, height: 80 },
    leave: { opacity: 0, height: 0 },
    config: config.stiff,
    keys: item => item.id
  })

  return (
    <div>
      {transitions((style, item) => (
        <animated.div style={style}>
          {item.text}
        </animated.div>
      ))}
    </div>
  )
}

export default TransitionAnimation'''
    },
    'inview': {
        'name': 'Viewport Intersection',
        'code': '''import { useInView, animated } from '@react-spring/web'

function InViewAnimation() {
  const [ref, springs] = useInView(
    () => ({
      from: { opacity: 0, y: 100 },
      to: { opacity: 1, y: 0 }
    }),
    { rootMargin: '-40% 0%' }
  )

  return (
    <animated.div ref={ref} style={springs}>
      Fades in when entering viewport
    </animated.div>
  )
}

export default InViewAnimation'''
    },
    'chain': {
        'name': 'Chained Async Animations',
        'code': '''import { useSpring, animated } from '@react-spring/web'

function ChainedAnimation() {
  const springs = useSpring({
    from: { x: 0, background: '#ff6d6d' },
    to: [
      { x: 80, background: '#fff59a' },
      { x: 0, background: '#88DFAB' },
      { x: 80, background: '#569AFF' }
    ],
    config: { tension: 200, friction: 20 },
    loop: true
  })

  return (
    <animated.div
      style={{
        width: 40,
        height: 40,
        borderRadius: 4,
        ...springs
      }}
    />
  )
}

export default ChainedAnimation'''
    },
    'gesture': {
        'name': 'Gesture-Driven Animation',
        'code': '''import { useSpring, animated } from '@react-spring/web'
import { useDrag } from '@use-gesture/react'

function GestureAnimation() {
  const [{ x, y }, api] = useSpring(() => ({ x: 0, y: 0 }))

  const bind = useDrag(({ down, movement: [mx, my], velocity: [vx, vy] }) => {
    api.start({
      x: down ? mx : 0,
      y: down ? my : 0,
      velocity: [vx * 1000, vy * 1000],
      immediate: down,
      config: { tension: 200, friction: 30 }
    })
  })

  return (
    <animated.div
      {...bind()}
      style={{
        x,
        y,
        width: 100,
        height: 100,
        background: '#569AFF',
        borderRadius: 8,
        touchAction: 'none'
      }}
    />
  )
}

export default GestureAnimation'''
    }
}


def generate_animation(anim_type, output_file=None):
    """Generate React Spring animation code."""
    if anim_type not in ANIMATION_TYPES:
        print(f"Error: Unknown animation type '{anim_type}'")
        print(f"Available types: {', '.join(ANIMATION_TYPES.keys())}")
        return False

    animation = ANIMATION_TYPES[anim_type]
    code = animation['code']

    if output_file:
        try:
            with open(output_file, 'w') as f:
                f.write(code)
            print(f"✅ Generated {animation['name']} → {output_file}")
            return True
        except IOError as e:
            print(f"❌ Error writing file: {e}")
            return False
    else:
        print(f"\n// {animation['name']}\n")
        print(code)
        return True


def interactive_mode():
    """Run generator in interactive mode."""
    print("React Spring Animation Generator")
    print("=" * 50)
    print("\nAvailable animation types:\n")

    for i, (key, value) in enumerate(ANIMATION_TYPES.items(), 1):
        print(f"  {i}. {value['name']} ({key})")

    print("\nSelect animation type (1-{}) or 'q' to quit: ".format(len(ANIMATION_TYPES)), end='')

    try:
        choice = input().strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nCancelled.")
        return

    if choice.lower() == 'q':
        return

    try:
        index = int(choice) - 1
        if 0 <= index < len(ANIMATION_TYPES):
            anim_type = list(ANIMATION_TYPES.keys())[index]
        else:
            print("Invalid selection.")
            return
    except ValueError:
        # Maybe they typed the key name
        if choice in ANIMATION_TYPES:
            anim_type = choice
        else:
            print("Invalid selection.")
            return

    print("\nOutput to file? (leave empty for stdout): ", end='')
    try:
        output_file = input().strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nCancelled.")
        return

    output_file = output_file if output_file else None
    generate_animation(anim_type, output_file)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate React Spring animation boilerplate',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent('''
        Examples:
          ./spring_generator.py                    # Interactive mode
          ./spring_generator.py --type click       # Generate to stdout
          ./spring_generator.py --type scroll -o ScrollAnim.jsx
          ./spring_generator.py --list             # List all types
        ''')
    )

    parser.add_argument(
        '--type', '-t',
        choices=list(ANIMATION_TYPES.keys()),
        help='Animation type to generate'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout)'
    )

    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all available animation types'
    )

    args = parser.parse_args()

    if args.list:
        print("Available animation types:\n")
        for key, value in ANIMATION_TYPES.items():
            print(f"  {key:12} - {value['name']}")
        return 0

    if args.type:
        success = generate_animation(args.type, args.output)
        return 0 if success else 1
    else:
        # Interactive mode
        interactive_mode()
        return 0


if __name__ == '__main__':
    sys.exit(main())

```


===== FILE: plugins/individual/react-spring-physics/skills/react-spring-physics/assets/README.md =====

# React Spring Physics - Assets

This directory contains starter templates and example documentation for React Spring animations.

## Contents

### Starter Template (Recommended)

For a complete React + Vite starter template with React Spring examples, use the official template:

```bash
# Create new project with Vite
npm create vite@latest my-spring-app -- --template react

# Navigate and install
cd my-spring-app
npm install

# Add React Spring
npm install @react-spring/web

# Optional: Add gesture library
npm install @use-gesture/react
```

### Official Examples

The React Spring team maintains excellent examples at:
- **Documentation**: https://react-spring.dev
- **Examples**: https://react-spring.dev/examples
- **CodeSandbox**: https://codesandbox.io/examples/package/@react-spring/web

### Recommended Examples by Category

**Basic Animations:**
- Spring basics: https://codesandbox.io/s/react-spring-spring-vqqd5
- Trails: https://codesandbox.io/s/react-spring-trail-q0zq5
- Transitions: https://codesandbox.io/s/react-spring-transition-njgm6

**Gesture Integration:**
- Draggable cards: https://codesandbox.io/s/react-spring-draggable-list-xhqod
- Viewpager: https://codesandbox.io/s/react-spring-viewpager-8tsle
- Gesture examples: https://use-gesture.netlify.app/docs/examples/

**Scroll Animations:**
- Scroll progress: https://codesandbox.io/s/react-spring-scroll-progress-8nqwt
- Parallax: https://codesandbox.io/s/react-spring-parallax-sticky-xhdn7
- useScroll hook: https://react-spring.dev/docs/components/use-scroll

**3D Integration (React Three Fiber):**
- Spring animations in 3D: https://codesandbox.io/s/react-spring-3d-ijdj2
- Interactive 3D: https://docs.pmnd.rs/react-three-fiber/tutorials/v8-migration-guide#spring

**Advanced Patterns:**
- Chained animations: https://codesandbox.io/s/react-spring-chain-dxqgq
- Auto-height accordion: https://codesandbox.io/s/react-spring-auto-height-accordion-r4qku
- Masonry grid: https://codesandbox.io/s/react-spring-masonry-5bw7y

## Quick Start Template

Minimal React Spring setup:

### package.json
```json
{
  "name": "react-spring-starter",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@react-spring/web": "^9.7.3",
    "@use-gesture/react": "^10.3.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8"
  }
}
```

### src/App.jsx
```jsx
import { useSpring, animated, config } from '@react-spring/web'
import './App.css'

function App() {
  const [springs, api] = useSpring(() => ({
    from: { y: -50, opacity: 0 }
  }), [])

  const handleClick = () => {
    api.start({
      from: { y: -50, opacity: 0 },
      to: { y: 0, opacity: 1 },
      config: config.wobbly
    })
  }

  return (
    <div className="app">
      <animated.h1 style={springs}>
        React Spring Physics
      </animated.h1>

      <button onClick={handleClick}>
        Animate
      </button>

      <div className="examples">
        <ExampleClick />
        <ExampleTrail />
      </div>
    </div>
  )
}

function ExampleClick() {
  const [springs, api] = useSpring(() => ({
    scale: 1,
    config: { tension: 300, friction: 10 }
  }), [])

  return (
    <animated.div
      className="box"
      onClick={() => api.start({ scale: 1.2 })}
      style={{
        transform: springs.scale.to(s => `scale(${s})`)
      }}
    >
      Click Me
    </animated.div>
  )
}

function ExampleTrail() {
  const items = ['React', 'Spring', 'Physics']
  const trails = useTrail(items.length, {
    from: { opacity: 0, x: -20 },
    to: { opacity: 1, x: 0 },
    config: config.gentle
  })

  return (
    <div className="trail">
      {trails.map((style, i) => (
        <animated.div key={i} style={style} className="trail-item">
          {items[i]}
        </animated.div>
      ))}
    </div>
  )
}

export default App
```

### src/App.css
```css
.app {
  text-align: center;
  padding: 2rem;
}

.examples {
  display: flex;
  gap: 2rem;
  justify-content: center;
  margin-top: 2rem;
}

.box {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.trail {
  display: flex;
  gap: 1rem;
}

.trail-item {
  padding: 1rem 2rem;
  background: #f0f0f0;
  border-radius: 8px;
  font-weight: 500;
}
```

## Common Patterns

### Pattern 1: Scroll-Triggered Animation

```jsx
import { useInView, animated } from '@react-spring/web'

function ScrollReveal({ children }) {
  const [ref, springs] = useInView(
    () => ({
      from: { opacity: 0, y: 50 },
      to: { opacity: 1, y: 0 }
    }),
    { rootMargin: '-20% 0%' }
  )

  return (
    <animated.div ref={ref} style={springs}>
      {children}
    </animated.div>
  )
}
```

### Pattern 2: List Transitions

```jsx
import { useTransition, animated } from '@react-spring/web'

function AnimatedList({ items }) {
  const transitions = useTransition(items, {
    keys: item => item.id,
    from: { opacity: 0, transform: 'translateX(-20px)' },
    enter: { opacity: 1, transform: 'translateX(0px)' },
    leave: { opacity: 0, transform: 'translateX(20px)' }
  })

  return transitions((style, item) => (
    <animated.div style={style}>
      {item.text}
    </animated.div>
  ))
}
```

### Pattern 3: Gesture-Driven Drag

```jsx
import { useSpring, animated } from '@react-spring/web'
import { useDrag } from '@use-gesture/react'

function DraggableCard() {
  const [{ x, y }, api] = useSpring(() => ({ x: 0, y: 0 }))

  const bind = useDrag(({ down, movement: [mx, my] }) => {
    api.start({
      x: down ? mx : 0,
      y: down ? my : 0,
      immediate: down
    })
  })

  return (
    <animated.div
      {...bind()}
      style={{ x, y, touchAction: 'none' }}
    />
  )
}
```

## TypeScript Support

For TypeScript projects, install types:

```bash
npm install --save-dev @types/react @types/react-dom
```

React Spring is fully typed - no additional @types package needed.

## Testing

For testing with React Spring, disable animations:

```jsx
import { Globals } from '@react-spring/web'

beforeAll(() => {
  Globals.assign({ skipAnimation: true })
})

afterAll(() => {
  Globals.assign({ skipAnimation: false })
})
```

## Additional Resources

- **React Spring Docs**: https://react-spring.dev
- **API Reference**: https://react-spring.dev/docs
- **Discord Community**: https://discord.com/invite/poimandres
- **GitHub**: https://github.com/pmndrs/react-spring
- **Use Gesture**: https://use-gesture.netlify.app (for drag/gesture support)
- **Leva**: https://github.com/pmndrs/leva (for live config tuning)

## Performance Tips

1. **Use function config** for imperative control
2. **Set appropriate precision** to reduce updates
3. **Use useSprings** for batching similar animations
4. **Avoid animating layout** - prefer transforms and opacity
5. **Enable skipAnimation** for tests and accessibility
6. **Monitor with React DevTools Profiler**

---

For more examples and patterns, refer to the skill's references:
- `react_spring_api.md` - Complete API documentation
- `popmotion_api.md` - Low-level physics utilities
- `physics_guide.md` - Spring tuning deep dive



# Skill: animejs


===== FILE: plugins/individual/animejs/skills/animejs/SKILL.md =====

---
name: animejs
description: Versatile JavaScript animation engine for DOM, CSS, SVG, and JavaScript objects. Use when creating timeline-based animations, stagger effects, SVG morphing, keyframe sequences, or complex choreographed animations. Triggers on tasks involving Anime.js, timeline animations, staggered sequences, SVG path animations, morphing, or multi-step animation choreography. Alternative to GSAP for SVG-heavy animations and React-independent projects.
---

# Anime.js

Lightweight JavaScript animation library with powerful timeline and stagger capabilities for web animations.

## Overview

Anime.js (pronounced "Anime JS") is a versatile animation engine that works with DOM elements, CSS properties, SVG attributes, and JavaScript objects. Unlike React-specific libraries, Anime.js works with vanilla JavaScript and any framework.

**When to use this skill:**
- Timeline-based animation sequences with precise choreography
- Staggered animations across multiple elements
- SVG path morphing and drawing animations
- Keyframe animations with percentage-based timing
- Framework-agnostic animation (works with React, Vue, vanilla JS)
- Complex easing functions (spring, steps, cubic-bezier)

**Core features:**
- Timeline sequencing with relative positioning
- Powerful stagger utilities (grid, from center, easing)
- SVG morphing and path animations
- Built-in spring physics easing
- Keyframe support with flexible timing
- Small bundle size (~9KB gzipped)

## Core Concepts

### Basic Animation

The `anime()` function creates animations:

```javascript
import anime from 'animejs'

anime({
  targets: '.element',
  translateX: 250,
  rotate: '1turn',
  duration: 800,
  easing: 'easeInOutQuad'
})
```

### Targets

Multiple ways to specify animation targets:

```javascript
// CSS selector
anime({ targets: '.box' })

// DOM elements
anime({ targets: document.querySelectorAll('.box') })

// Array of elements
anime({ targets: [el1, el2, el3] })

// JavaScript object
const obj = { x: 0 }
anime({ targets: obj, x: 100 })
```

### Animatable Properties

**CSS Properties:**
```javascript
anime({
  targets: '.element',
  translateX: 250,
  scale: 2,
  opacity: 0.5,
  backgroundColor: '#FFF'
})
```

**CSS Transforms (Individual):**
```javascript
anime({
  targets: '.element',
  translateX: 250,   // Individual transform
  rotate: '1turn',   // Not 'transform: rotate()'
  scale: 2
})
```

**SVG Attributes:**
```javascript
anime({
  targets: 'path',
  d: 'M10 80 Q 77.5 10, 145 80', // Path morphing
  fill: '#FF0000',
  strokeDashoffset: [anime.setDashoffset, 0] // Line drawing
})
```

**JavaScript Objects:**
```javascript
const obj = { value: 0 }
anime({
  targets: obj,
  value: 100,
  round: 1,
  update: () => console.log(obj.value)
})
```

### Timeline

Create complex sequences with precise control:

```javascript
const timeline = anime.timeline({
  duration: 750,
  easing: 'easeOutExpo'
})

timeline
  .add({
    targets: '.box1',
    translateX: 250
  })
  .add({
    targets: '.box2',
    translateX: 250
  }, '-=500') // Start 500ms before previous animation ends
  .add({
    targets: '.box3',
    translateX: 250
  }, '+=200') // Start 200ms after previous animation ends
```

## Common Patterns

### 1. Stagger Animation (Sequential Reveal)

```javascript
anime({
  targets: '.stagger-element',
  translateY: [100, 0],
  opacity: [0, 1],
  delay: anime.stagger(100), // Increase delay by 100ms
  easing: 'easeOutQuad',
  duration: 600
})
```

### 2. Stagger from Center

```javascript
anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    grid: [14, 5],
    from: 'center', // Also: 'first', 'last', index, [x, y]
    axis: 'x'       // Also: 'y', null
  }),
  easing: 'easeOutQuad'
})
```

### 3. SVG Line Drawing

```javascript
anime({
  targets: 'path',
  strokeDashoffset: [anime.setDashoffset, 0],
  easing: 'easeInOutQuad',
  duration: 2000,
  delay: (el, i) => i * 250
})
```

### 4. SVG Morphing

```javascript
anime({
  targets: '#morphing-path',
  d: [
    { value: 'M10 80 Q 77.5 10, 145 80' }, // Start shape
    { value: 'M10 80 Q 77.5 150, 145 80' }  // End shape
  ],
  duration: 2000,
  easing: 'easeInOutQuad',
  loop: true,
  direction: 'alternate'
})
```

### 5. Timeline Sequence

```javascript
const tl = anime.timeline({
  easing: 'easeOutExpo',
  duration: 750
})

tl.add({
  targets: '.title',
  translateY: [-50, 0],
  opacity: [0, 1]
})
.add({
  targets: '.subtitle',
  translateY: [-30, 0],
  opacity: [0, 1]
}, '-=500')
.add({
  targets: '.button',
  scale: [0, 1],
  opacity: [0, 1]
}, '-=300')
```

### 6. Keyframe Animation

```javascript
anime({
  targets: '.element',
  keyframes: [
    { translateX: 100 },
    { translateY: 100 },
    { translateX: 0 },
    { translateY: 0 }
  ],
  duration: 4000,
  easing: 'easeInOutQuad',
  loop: true
})
```

### 7. Scroll-Triggered Animation

```javascript
const animation = anime({
  targets: '.scroll-element',
  translateY: [100, 0],
  opacity: [0, 1],
  easing: 'easeOutQuad',
  autoplay: false
})

window.addEventListener('scroll', () => {
  const scrollPercent = window.scrollY / (document.body.scrollHeight - window.innerHeight)
  animation.seek(animation.duration * scrollPercent)
})
```

## Integration Patterns

### With React

```javascript
import { useEffect, useRef } from 'react'
import anime from 'animejs'

function AnimatedComponent() {
  const ref = useRef(null)

  useEffect(() => {
    const animation = anime({
      targets: ref.current,
      translateX: 250,
      duration: 800,
      easing: 'easeInOutQuad'
    })

    return () => animation.pause()
  }, [])

  return <div ref={ref}>Animated</div>
}
```

### With Vue

```javascript
export default {
  mounted() {
    anime({
      targets: this.$el,
      translateX: 250,
      duration: 800
    })
  }
}
```

### Path Following Animation

```javascript
const path = anime.path('#motion-path')

anime({
  targets: '.element',
  translateX: path('x'),
  translateY: path('y'),
  rotate: path('angle'),
  easing: 'linear',
  duration: 2000,
  loop: true
})
```

## Advanced Techniques

### Spring Easing

```javascript
anime({
  targets: '.element',
  translateX: 250,
  easing: 'spring(1, 80, 10, 0)', // mass, stiffness, damping, velocity
  duration: 2000
})
```

### Steps Easing

```javascript
anime({
  targets: '.element',
  translateX: 250,
  easing: 'steps(5)',
  duration: 1000
})
```

### Custom Bezier

```javascript
anime({
  targets: '.element',
  translateX: 250,
  easing: 'cubicBezier(.5, .05, .1, .3)',
  duration: 1000
})
```

### Direction and Loop

```javascript
anime({
  targets: '.element',
  translateX: 250,
  direction: 'alternate', // 'normal', 'reverse', 'alternate'
  loop: true,             // or number of iterations
  easing: 'easeInOutQuad'
})
```

### Playback Control

```javascript
const animation = anime({
  targets: '.element',
  translateX: 250,
  autoplay: false
})

animation.play()
animation.pause()
animation.restart()
animation.reverse()
animation.seek(500) // Seek to 500ms
```

## Performance Optimization

### Use Transform and Opacity

```javascript
// ✅ Good: GPU-accelerated
anime({
  targets: '.element',
  translateX: 250,
  opacity: 0.5
})

// ❌ Avoid: Triggers layout
anime({
  targets: '.element',
  left: '250px',
  width: '500px'
})
```

### Batch Similar Animations

```javascript
// ✅ Single animation for multiple targets
anime({
  targets: '.multiple-elements',
  translateX: 250
})

// ❌ Avoid: Multiple separate animations
elements.forEach(el => {
  anime({ targets: el, translateX: 250 })
})
```

### Use `will-change` for Complex Animations

```css
.animated-element {
  will-change: transform, opacity;
}
```

### Disable autoplay for Scroll Animations

```javascript
const animation = anime({
  targets: '.element',
  translateX: 250,
  autoplay: false // Control manually
})
```

## Common Pitfalls

### 1. Forgetting Unit Types

```javascript
// ❌ Wrong: No unit
anime({ targets: '.element', width: 200 })

// ✅ Correct: Include unit
anime({ targets: '.element', width: '200px' })
```

### 2. Using CSS transform Property Directly

```javascript
// ❌ Wrong: Can't animate transform string
anime({ targets: '.element', transform: 'translateX(250px)' })

// ✅ Correct: Individual transform properties
anime({ targets: '.element', translateX: 250 })
```

### 3. Not Handling Animation Cleanup

```javascript
// ❌ Wrong: Animation continues after unmount
useEffect(() => {
  anime({ targets: ref.current, translateX: 250 })
}, [])

// ✅ Correct: Pause on cleanup
useEffect(() => {
  const anim = anime({ targets: ref.current, translateX: 250 })
  return () => anim.pause()
}, [])
```

### 4. Animating Too Many Elements

```javascript
// ❌ Avoid: Animating 1000+ elements
anime({ targets: '.many-items', translateX: 250 }) // 1000+ elements

// ✅ Better: Use CSS animations for large sets
// Or reduce element count with virtualization
```

### 5. Incorrect Timeline Timing

```javascript
// ❌ Wrong: Missing offset operator
.add({ targets: '.el2' }, '500') // Treated as absolute time

// ✅ Correct: Use relative operators
.add({ targets: '.el2' }, '-=500') // Relative to previous
.add({ targets: '.el3' }, '+=200') // Relative to previous
```

### 6. Overusing Loop

```javascript
// ❌ Avoid: Infinite loops drain battery
anime({
  targets: '.element',
  rotate: '1turn',
  loop: true,
  duration: 1000
})

// ✅ Better: Use CSS animations for infinite loops
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

## Resources

### Scripts
- `animation_generator.py` - Generate Anime.js animation boilerplate (8 types)
- `timeline_builder.py` - Build complex timeline sequences

### References
- `api_reference.md` - Complete Anime.js API documentation
- `stagger_guide.md` - Stagger utilities and patterns
- `timeline_guide.md` - Timeline sequencing deep dive

### Assets
- `starter_animejs/` - Vanilla JS + Vite template with examples
- `examples/` - Real-world patterns (SVG morphing, stagger grids, timelines)

## Related Skills

- **gsap-scrolltrigger** - More powerful timeline features and scroll integration
- **motion-framer** - React-specific declarative animations
- **react-spring-physics** - Physics-based spring animations
- **lightweight-3d-effects** - Simple 3D effects (Zdog, Vanta.js)

**Anime.js vs GSAP**: Use Anime.js for SVG-heavy animations, simpler projects, or when bundle size matters. Use GSAP for complex scroll-driven experiences, advanced timelines, and professional-grade control.

**Anime.js vs Framer Motion**: Use Anime.js for framework-agnostic projects or when working outside React. Use Framer Motion for React-specific declarative animations with gesture integration.



===== FILE: plugins/individual/animejs/skills/animejs/references/api_reference.md =====

# Anime.js API Reference

Complete API documentation for Anime.js v3+.

## Table of Contents

- [anime() Function](#anime-function)
- [Targets](#targets)
- [Properties](#properties)
- [Property Parameters](#property-parameters)
- [Animation Parameters](#animation-parameters)
- [Timeline](#timeline)
- [Stagger](#stagger)
- [Easing Functions](#easing-functions)
- [Helpers](#helpers)
- [Callbacks](#callbacks)

---

## anime() Function

Main function to create animations.

```javascript
anime(options)
```

**Returns:** Animation instance with playback controls.

---

## Targets

Specify what to animate.

**CSS Selector:**
```javascript
targets: '.element'
targets: '#myId'
targets: 'div.className'
```

**DOM Element/NodeList:**
```javascript
targets: document.querySelector('.element')
targets: document.querySelectorAll('.elements')
```

**JavaScript Object:**
```javascript
const obj = { prop: 0 }
anime({ targets: obj, prop: 100 })
```

**Array:**
```javascript
targets: [el1, el2, el3]
targets: [obj1, obj2]
```

---

## Properties

### CSS Properties

**Transform (individual):**
```javascript
translateX: 250         // pixels
translateY: '10em'     // units
translateZ: '50vh'
rotate: '1turn'        // turns, deg, rad
rotateX, rotateY, rotateZ
scale: 2
scaleX, scaleY, scaleZ
skew: '10deg'
skewX, skewY
perspective: 1000
```

**Other CSS:**
```javascript
opacity: 0.5
backgroundColor: '#FFF'  // colors
borderRadius: '50%'
width: '100px'
left: '50%'
// Any valid CSS property (camelCase)
```

### SVG Attributes

```javascript
d: 'M10 80 Q 77.5 10, 145 80'  // Path morphing
points: '64 68 8 400 ...'       // Polygon points
strokeDashoffset: 100
fill: '#FF0000'
r: 50                           // Circle radius
cx, cy                          // Circle center
// Any SVG attribute
```

### DOM Attributes

```javascript
value: 100              // Input value
volume: 0.5            // Audio/video
textContent: 'Hello'   // Text content
innerHTML: '<div></div>'
// Any DOM attribute
```

### JavaScript Object Properties

```javascript
const obj = { x: 0, y: 0 }
anime({
  targets: obj,
  x: 100,
  y: 200
})
```

---

## Property Parameters

Define how each property animates.

### Value Formats

**Single Value:**
```javascript
translateX: 250  // Animate from current to 250
```

**From-To Array:**
```javascript
translateX: [0, 250]  // Explicit from/to
opacity: [0, 1]
```

**Function-Based:**
```javascript
translateX: (el, i) => 50 + (i * 50)  // Different per element
delay: (el, i, total) => i * 100
```

**Keyframes:**
```javascript
translateX: [
  { value: 100, duration: 500 },
  { value: 200, duration: 500 },
  { value: 0, duration: 500 }
]
```

### Units

```javascript
'250px'      // Pixels
'10em'       // Ems
'50%'        // Percentage
'100vh'      // Viewport
'1turn'      // Turns
'45deg'      // Degrees
'1.5rad'     // Radians
```

### Relative Values

```javascript
translateX: '+=250'   // Add 250 to current
translateX: '-=100'   // Subtract 100
translateX: '*=2'     // Multiply by 2
```

### Colors

```javascript
'#FF0000'               // Hex
'rgb(255, 0, 0)'       // RGB
'rgba(255, 0, 0, 0.5)' // RGBA
'hsl(0, 100%, 50%)'    // HSL
```

---

## Animation Parameters

Global animation settings.

```javascript
anime({
  targets: '.element',
  translateX: 250,

  // Timing
  duration: 1000,              // Milliseconds
  delay: 500,                  // Start delay
  endDelay: 200,               // End delay

  // Easing
  easing: 'easeInOutQuad',     // Built-in easing

  // Playback
  direction: 'normal',         // 'normal', 'reverse', 'alternate'
  loop: 3,                     // Number or true for infinite
  autoplay: true,              // Auto-start

  // Advanced
  round: 1,                    // Round values to 1 decimal
  specific Property Parameters
  specificProperty: {
    value: 100,
    duration: 2000,
    delay: 500,
    easing: 'linear'
  }
})
```

---

## Timeline

Chain multiple animations with precise control.

### Create Timeline

```javascript
const tl = anime.timeline({
  duration: 1000,
  easing: 'easeOutExpo',
  loop: true
})
```

### Add Animations

```javascript
tl.add({
  targets: '.el1',
  translateX: 250
})
.add({
  targets: '.el2',
  translateX: 250
}, '-=500')  // Offset
```

### Timeline Parameters

All animation parameters plus:

```javascript
anime.timeline({
  duration: 1000,        // Default duration
  delay: 500,            // Default delay
  easing: 'linear',      // Default easing
  direction: 'normal',
  loop: false,
  autoplay: true
})
```

### Offset

Control when animations start:

```javascript
'+=500'   // Start 500ms after previous ends
'-=500'   // Start 500ms before previous ends
500       // Start at absolute time 500ms
```

### Timeline Methods

```javascript
tl.play()
tl.pause()
tl.restart()
tl.reverse()
tl.seek(1000)          // Seek to 1000ms
tl.add(animation)      // Add animation
```

---

## Stagger

Distribute delays across multiple elements.

### Basic Stagger

```javascript
delay: anime.stagger(100)  // Increment by 100ms
```

### Stagger Options

```javascript
delay: anime.stagger(100, {
  start: 500,              // Start delay
  from: 'center',          // 'first', 'last', 'center', index, [x, y]
  direction: 'normal',     // 'normal', 'reverse'
  easing: 'easeOutQuad',   // Easing for delay
  grid: [10, 10],          // Grid dimensions
  axis: 'x'                // 'x', 'y', null
})
```

### Stagger Values

```javascript
// Stagger delays
delay: anime.stagger(100)

// Stagger values
translateX: anime.stagger([0, 100, 200, 300])

// Stagger ranges
scale: anime.stagger([1, 2], { from: 'center' })
```

### Grid Stagger

```javascript
anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    grid: [14, 5],
    from: 'center'
  })
})
```

---

## Easing Functions

### Built-in Easings

**Linear:**
```javascript
'linear'
```

**Ease In/Out:**
```javascript
'easeInQuad', 'easeOutQuad', 'easeInOutQuad'
'easeInCubic', 'easeOutCubic', 'easeInOutCubic'
'easeInQuart', 'easeOutQuart', 'easeInOutQuart'
'easeInQuint', 'easeOutQuint', 'easeInOutQuint'
'easeInSine', 'easeOutSine', 'easeInOutSine'
'easeInExpo', 'easeOutExpo', 'easeInOutExpo'
'easeInCirc', 'easeOutCirc', 'easeInOutCirc'
'easeInBack', 'easeOutBack', 'easeInOutBack'
'easeInElastic', 'easeOutElastic', 'easeInOutElastic'
'easeInBounce', 'easeOutBounce', 'easeInOutBounce'
```

### Custom Easings

**Cubic Bezier:**
```javascript
easing: 'cubicBezier(.5, .05, .1, .3)'
```

**Spring Physics:**
```javascript
easing: 'spring(1, 80, 10, 0)'
// mass, stiffness, damping, velocity
```

**Steps:**
```javascript
easing: 'steps(5)'  // 5 steps
```

**Linear Keyframes:**
```javascript
easing: 'linear(0, 0.5, 1)'
```

---

## Helpers

### anime.setDashoffset(el)

Calculate strokeDashoffset for line drawing:

```javascript
anime({
  targets: 'path',
  strokeDashoffset: [anime.setDashoffset, 0]
})
```

### anime.path(path)

Get coordinates and angle from SVG path:

```javascript
const path = anime.path('#motion-path')

anime({
  targets: '.element',
  translateX: path('x'),
  translateY: path('y'),
  rotate: path('angle')
})
```

### anime.random(min, max)

Generate random value:

```javascript
translateX: () => anime.random(0, 100)
```

### anime.get(targets, prop)

Get current value:

```javascript
const currentX = anime.get('.element', 'translateX')
```

### anime.set(targets, prop)

Set value without animating:

```javascript
anime.set('.element', { translateX: 100, opacity: 0.5 })
```

---

## Callbacks

### Animation Callbacks

```javascript
anime({
  targets: '.element',
  translateX: 250,

  begin: (anim) => {
    console.log('Animation begins')
  },

  update: (anim) => {
    console.log('Animation updates', anim.progress)
  },

  complete: (anim) => {
    console.log('Animation completes')
  },

  loopBegin: (anim) => {
    console.log('Loop begins')
  },

  loopComplete: (anim) => {
    console.log('Loop completes')
  },

  changeBegin: (anim) => {
    console.log('Direction changes')
  },

  changeComplete: (anim) => {
    console.log('Direction change completes')
  }
})
```

### Callback Parameters

**anim Object:**
```javascript
anim.progress      // Animation progress (0-100)
anim.currentTime   // Current time (ms)
anim.duration      // Total duration (ms)
anim.remaining     // Remaining loops
anim.reversed      // Direction reversed?
anim.paused        // Animation paused?
anim.began         // Animation began?
anim.finished      // Animation finished?
```

---

## Animation Instance

### Properties

```javascript
const animation = anime({ ... })

animation.progress      // 0-100
animation.currentTime   // Milliseconds
animation.duration      // Milliseconds
animation.remaining     // Remaining loops
animation.reversed      // Boolean
animation.paused        // Boolean
animation.began         // Boolean
animation.finished      // Boolean
animation.animatables   // Array of targets
animation.animations    // Array of property animations
```

### Methods

```javascript
animation.play()
animation.pause()
animation.restart()
animation.reverse()
animation.seek(time)       // Seek to time (ms or %)
animation.tick(time)       // Manual tick
```

---

## Examples

### Basic Animation

```javascript
anime({
  targets: '.box',
  translateX: 250,
  rotate: '1turn',
  duration: 800,
  easing: 'easeInOutQuad'
})
```

### From-To Animation

```javascript
anime({
  targets: '.element',
  translateX: [0, 250],
  opacity: [0, 1],
  duration: 1000
})
```

### Keyframe Animation

```javascript
anime({
  targets: '.element',
  keyframes: [
    { translateX: 100 },
    { translateY: 100 },
    { translateX: 0 },
    { translateY: 0 }
  ],
  duration: 4000,
  loop: true
})
```

### Timeline Animation

```javascript
const tl = anime.timeline()

tl.add({
  targets: '.box1',
  translateX: 250
})
.add({
  targets: '.box2',
  translateX: 250
}, '-=500')
```

### Stagger Animation

```javascript
anime({
  targets: '.stagger-item',
  translateY: [-50, 0],
  opacity: [0, 1],
  delay: anime.stagger(100, { from: 'center' })
})
```

### SVG Path Animation

```javascript
anime({
  targets: '#morphing-path',
  d: 'M10 80 Q 77.5 150, 145 80',
  duration: 2000,
  easing: 'easeInOutQuad'
})
```

### JavaScript Object Animation

```javascript
const obj = { count: 0 }

anime({
  targets: obj,
  count: 100,
  round: 1,
  update: () => {
    document.querySelector('.counter').textContent = obj.count
  }
})
```



===== FILE: plugins/individual/animejs/skills/animejs/references/stagger_guide.md =====

# Anime.js Stagger Guide

Complete guide to Anime.js stagger utilities for creating sequential and coordinated animations.

## Overview

Stagger distributes animation delays across multiple elements, creating cascading or wave-like effects. Anime.js provides powerful stagger options including grid-based staggering, directional control, and custom easing.

## Basic Stagger

### Time-Based Stagger

```javascript
anime({
  targets: '.element',
  translateX: 250,
  delay: anime.stagger(100) // Increment delay by 100ms
})
```

**Result:** Each element animates 100ms after the previous one.

### Value-Based Stagger

```javascript
anime({
  targets: '.element',
  translateX: anime.stagger([0, 100, 200, 300])
})
```

**Result:** Each element animates to a different translateX value.

## Stagger Options

### Complete Syntax

```javascript
anime.stagger(value, {
  start: 0,              // Starting delay (ms)
  from: 'first',         // Starting point
  direction: 'normal',   // Direction of stagger
  easing: 'linear',      // Easing for stagger progression
  grid: [rows, cols],    // Grid dimensions
  axis: null             // Grid axis ('x', 'y', or null)
})
```

---

## Stagger From

Control where the stagger starts.

### from: 'first' (default)

Start from the first element:

```javascript
anime({
  targets: '.element',
  scale: [0, 1],
  delay: anime.stagger(100, { from: 'first' })
})
```

### from: 'last'

Start from the last element:

```javascript
anime({
  targets: '.element',
  scale: [0, 1],
  delay: anime.stagger(100, { from: 'last' })
})
```

### from: 'center'

Start from the center and expand outward:

```javascript
anime({
  targets: '.element',
  scale: [0, 1],
  delay: anime.stagger(100, { from: 'center' })
})
```

### from: index

Start from a specific index:

```javascript
anime({
  targets: '.element',
  scale: [0, 1],
  delay: anime.stagger(100, { from: 5 }) // Start from 6th element (0-indexed)
})
```

### from: [x, y]

Start from specific grid coordinates:

```javascript
anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    grid: [10, 10],
    from: [5, 5] // Start from center of grid
  })
})
```

---

## Grid Stagger

Stagger elements arranged in a grid pattern.

### Basic Grid

```javascript
anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    grid: [14, 5] // 14 columns, 5 rows
  })
})
```

### Grid with from: 'center'

```javascript
anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    grid: [14, 5],
    from: 'center'
  })
})
```

**Result:** Animates from center outward in all directions.

### Grid with Axis

Control which axis dominates the stagger:

```javascript
// Horizontal waves
anime({
  targets: '.grid-item',
  translateY: [-20, 0],
  delay: anime.stagger(30, {
    grid: [10, 10],
    from: 'center',
    axis: 'x' // Stagger primarily along x-axis
  })
})

// Vertical waves
anime({
  targets: '.grid-item',
  translateY: [-20, 0],
  delay: anime.stagger(30, {
    grid: [10, 10],
    from: 'center',
    axis: 'y' // Stagger primarily along y-axis
  })
})
```

---

## Stagger Direction

### direction: 'normal' (default)

```javascript
anime({
  targets: '.element',
  scale: [0, 1],
  delay: anime.stagger(100, { direction: 'normal' })
})
```

### direction: 'reverse'

Reverse the stagger order:

```javascript
anime({
  targets: '.element',
  scale: [0, 1],
  delay: anime.stagger(100, {
    from: 'first',
    direction: 'reverse' // Last to first
  })
})
```

---

## Stagger Easing

Apply easing to the stagger progression itself.

```javascript
anime({
  targets: '.element',
  translateY: [-50, 0],
  delay: anime.stagger(100, {
    easing: 'easeOutQuad' // Ease the delay distribution
  })
})
```

**Effect:** Early elements have shorter delays, later elements have longer delays (exponential distribution).

---

## Stagger Start

Add an initial delay before stagger begins.

```javascript
anime({
  targets: '.element',
  scale: [0, 1],
  delay: anime.stagger(100, {
    start: 500 // Wait 500ms before starting stagger
  })
})
```

**Result:**
- Element 1: 500ms delay
- Element 2: 600ms delay
- Element 3: 700ms delay

---

## Common Patterns

### 1. Sequential List Reveal

```javascript
anime({
  targets: '.list-item',
  translateY: [30, 0],
  opacity: [0, 1],
  delay: anime.stagger(80),
  easing: 'easeOutQuad'
})
```

### 2. Grid Expand from Center

```javascript
anime({
  targets: '.grid-square',
  scale: [0, 1],
  delay: anime.stagger(30, {
    grid: [10, 10],
    from: 'center'
  }),
  easing: 'easeOutElastic(1, .8)'
})
```

### 3. Wave Effect

```javascript
anime({
  targets: '.wave-element',
  translateY: [
    { value: -20, duration: 300 },
    { value: 0, duration: 300 }
  ],
  delay: anime.stagger(50),
  loop: true
})
```

### 4. Diagonal Wipe

```javascript
anime({
  targets: '.tile',
  opacity: [0, 1],
  translateX: [-50, 0],
  delay: anime.stagger(20, {
    grid: [10, 10],
    from: [0, 0], // Top-left corner
    axis: null // Both axes
  })
})
```

### 5. Text Character Reveal

```javascript
// Split text into characters first
const textWrapper = document.querySelector('.text')
textWrapper.innerHTML = textWrapper.textContent.replace(/\S/g, "<span class='letter'>$&</span>")

anime({
  targets: '.letter',
  translateY: [100, 0],
  opacity: [0, 1],
  delay: anime.stagger(30),
  easing: 'easeOutExpo'
})
```

### 6. Circular Stagger

```javascript
anime({
  targets: '.circle-item',
  scale: [0, 1],
  delay: anime.stagger(100, {
    from: 'center',
    easing: 'linear'
  }),
  rotate: anime.stagger([0, 360])
})
```

### 7. Alternating Direction

```javascript
anime({
  targets: '.row',
  translateX: (el, i) => i % 2 === 0 ? [-250, 0] : [250, 0],
  opacity: [0, 1],
  delay: anime.stagger(100)
})
```

---

## Stagger with Different Properties

### Stagger Delays, Same Values

```javascript
anime({
  targets: '.element',
  translateX: 250, // Same for all
  delay: anime.stagger(100) // Different delays
})
```

### Stagger Values, Same Timing

```javascript
anime({
  targets: '.element',
  translateX: anime.stagger([0, 50, 100, 150]), // Different values
  duration: 1000 // Same duration
})
```

### Stagger Both

```javascript
anime({
  targets: '.element',
  translateX: anime.stagger([0, 50, 100, 150]),
  delay: anime.stagger(100)
})
```

---

## Advanced Techniques

### Dynamic Grid Calculation

```javascript
function getGridSize() {
  const elements = document.querySelectorAll('.grid-item')
  const cols = Math.ceil(Math.sqrt(elements.length))
  const rows = Math.ceil(elements.length / cols)
  return [cols, rows]
}

anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    grid: getGridSize(),
    from: 'center'
  })
})
```

### Stagger with Function Values

```javascript
anime({
  targets: '.element',
  translateX: anime.stagger((el, i, total) => {
    // Custom calculation
    return (i / total) * 100
  }),
  delay: anime.stagger(100)
})
```

### Multi-Property Stagger

```javascript
anime({
  targets: '.element',
  translateX: anime.stagger([0, 100]),
  translateY: anime.stagger([0, 50]),
  rotate: anime.stagger([0, 360]),
  delay: anime.stagger(100, { from: 'center' })
})
```

---

## Performance Tips

1. **Use transforms** - Stagger `translateX`, `translateY`, `scale`, `rotate` for GPU acceleration
2. **Limit element count** - Stagger works best with <100 elements
3. **Avoid layout properties** - Don't stagger `width`, `height`, `left`, `top`
4. **Use `will-change`** - Add `will-change: transform` for smoother animations
5. **Batch similar animations** - One stagger for multiple properties is more efficient than separate animations

---

## Common Mistakes

### ❌ Wrong: Stagger on Single Element

```javascript
anime({
  targets: '.single-element', // Only one element
  scale: [0, 1],
  delay: anime.stagger(100) // No effect
})
```

### ✅ Correct: Multiple Elements

```javascript
anime({
  targets: '.multiple-elements', // Multiple elements
  scale: [0, 1],
  delay: anime.stagger(100)
})
```

### ❌ Wrong: Grid Without Dimensions

```javascript
anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    from: 'center' // Missing grid dimensions!
  })
})
```

### ✅ Correct: Grid With Dimensions

```javascript
anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    grid: [10, 10],
    from: 'center'
  })
})
```

---

## Debugging Tips

**Log stagger values:**
```javascript
anime({
  targets: '.element',
  translateX: 250,
  delay: anime.stagger(100),
  begin: (anim) => {
    anim.animatables.forEach((animatable, i) => {
      console.log(`Element ${i}: delay ${animatable.delay}ms`)
    })
  }
})
```

**Visualize stagger:**
```javascript
// Add data-index to elements
document.querySelectorAll('.element').forEach((el, i) => {
  el.setAttribute('data-index', i)
})
```

---

## Resources

- Official Stagger Documentation: https://animejs.com/documentation/#stagger
- Grid Stagger Demo: https://codepen.io/juliangarnier/pen/JXaKpP
- Stagger Examples: https://animejs.com/documentation/#staggeringBasics



===== FILE: plugins/individual/animejs/skills/animejs/references/timeline_guide.md =====

# Anime.js Timeline Guide

Complete guide to creating complex animation sequences with Anime.js timelines.

## Overview

Timelines allow you to chain multiple animations with precise control over timing and sequencing. They provide a declarative way to choreograph complex multi-step animations.

## Creating a Timeline

### Basic Timeline

```javascript
const timeline = anime.timeline()
```

### Timeline with Default Parameters

```javascript
const timeline = anime.timeline({
  duration: 1000,      // Default duration for all animations
  easing: 'easeOutExpo', // Default easing
  loop: false,         // Loop entire timeline
  direction: 'normal',  // 'normal', 'reverse', 'alternate'
  autoplay: true       // Auto-start
})
```

---

## Adding Animations

### .add() Method

```javascript
timeline.add({
  targets: '.element',
  translateX: 250,
  duration: 800
})
```

### Chaining Animations

```javascript
timeline
  .add({
    targets: '.box1',
    translateX: 250
  })
  .add({
    targets: '.box2',
    translateX: 250
  })
  .add({
    targets: '.box3',
    translateX: 250
  })
```

---

## Timeline Offsets

Control when each animation starts relative to the previous one.

### Absolute Time

```javascript
timeline.add({
  targets: '.element',
  translateX: 250
}, 1000) // Start at 1000ms from timeline start
```

### Relative to Previous (+=)

```javascript
timeline
  .add({
    targets: '.box1',
    translateX: 250,
    duration: 1000
  })
  .add({
    targets: '.box2',
    translateX: 250
  }, '+=500') // Start 500ms AFTER box1 completes
```

### Overlap with Previous (-=)

```javascript
timeline
  .add({
    targets: '.box1',
    translateX: 250,
    duration: 1000
  })
  .add({
    targets: '.box2',
    translateX: 250
  }, '-=500') // Start 500ms BEFORE box1 completes (overlap)
```

---

## Common Patterns

### 1. Sequential Animations

Each animation starts after the previous completes:

```javascript
const tl = anime.timeline()

tl.add({
  targets: '.title',
  translateY: [-50, 0],
  opacity: [0, 1]
})
.add({
  targets: '.subtitle',
  translateY: [-30, 0],
  opacity: [0, 1]
})
.add({
  targets: '.button',
  scale: [0, 1]
})
```

### 2. Overlapping Animations

Create smooth transitions between animations:

```javascript
const tl = anime.timeline()

tl.add({
  targets: '.section1',
  opacity: [1, 0],
  duration: 600
})
.add({
  targets: '.section2',
  opacity: [0, 1],
  duration: 600
}, '-=300') // Overlap by 300ms for crossfade
```

### 3. Staggered Timeline

Combine timeline with stagger:

```javascript
const tl = anime.timeline()

tl.add({
  targets: '.card',
  translateY: [100, 0],
  opacity: [0, 1],
  delay: anime.stagger(100)
})
.add({
  targets: '.button',
  scale: [0, 1]
}, '-=200')
```

### 4. Multi-Stage Animation

Complex multi-step sequence:

```javascript
const tl = anime.timeline({
  easing: 'easeOutExpo',
  duration: 750
})

tl.add({
  targets: '.modal',
  scale: [0, 1],
  opacity: [0, 1]
})
.add({
  targets: '.modal-header',
  translateY: [-20, 0],
  opacity: [0, 1]
}, '-=500')
.add({
  targets: '.modal-body',
  translateY: [20, 0],
  opacity: [0, 1]
}, '-=400')
.add({
  targets: '.modal-footer',
  opacity: [0, 1]
}, '-=300')
```

### 5. Looping Timeline

```javascript
const tl = anime.timeline({
  loop: true,
  direction: 'alternate'
})

tl.add({
  targets: '.ball',
  translateY: -200,
  duration: 1000
})
.add({
  targets: '.ball',
  translateX: 200,
  duration: 1000
})
```

### 6. Loading Sequence

```javascript
const tl = anime.timeline()

tl.add({
  targets: '.loader-bg',
  scaleY: [0, 1],
  duration: 400,
  easing: 'easeInOutQuad'
})
.add({
  targets: '.loader-text',
  opacity: [0, 1],
  translateY: [20, 0],
  duration: 600
}, '-=200')
.add({
  targets: '.loader-spinner',
  rotate: '1turn',
  duration: 800,
  loop: 3
}, '-=400')
.add({
  targets: '.loader',
  opacity: 0,
  duration: 400
}, '+=500')
.add({
  targets: '.content',
  translateY: [50, 0],
  opacity: [0, 1],
  duration: 600
})
```

### 7. Page Transition

```javascript
function pageTransition(oldPage, newPage) {
  const tl = anime.timeline()

  tl.add({
    targets: oldPage,
    translateX: [0, -100],
    opacity: [1, 0],
    duration: 400,
    easing: 'easeInQuad'
  })
  .add({
    targets: newPage,
    translateX: [100, 0],
    opacity: [0, 1],
    duration: 400,
    easing: 'easeOutQuad'
  }, '-=200')

  return tl
}
```

---

## Timeline Controls

### Playback Methods

```javascript
const tl = anime.timeline({ autoplay: false })

tl.play()       // Play from current position
tl.pause()      // Pause
tl.restart()    // Restart from beginning
tl.reverse()    // Reverse direction
tl.seek(2000)   // Seek to 2000ms
```

### Properties

```javascript
tl.duration      // Total duration
tl.currentTime   // Current time
tl.progress      // Progress (0-100)
tl.reversed      // Is reversed?
tl.paused        // Is paused?
tl.began         // Has begun?
tl.finished      // Is finished?
```

---

## Advanced Techniques

### Labels

Mark specific points in the timeline:

```javascript
const tl = anime.timeline()

tl.add({
  targets: '.intro',
  opacity: [0, 1]
})
.add({}, '+=500') // Add label "intro-done" at this point
.add({
  targets: '.content',
  translateY: [50, 0],
  opacity: [0, 1]
})

// Seek to label
tl.seek('intro-done')
```

### Nested Timelines

```javascript
function createIntroTimeline() {
  const tl = anime.timeline({ autoplay: false })
  tl.add({
    targets: '.logo',
    scale: [0, 1]
  })
  .add({
    targets: '.tagline',
    opacity: [0, 1]
  })
  return tl
}

const mainTimeline = anime.timeline()
mainTimeline.add(createIntroTimeline())
```

### Timeline Callbacks

```javascript
const tl = anime.timeline({
  begin: () => console.log('Timeline begins'),
  update: (tl) => console.log('Progress:', tl.progress),
  complete: () => console.log('Timeline completes')
})
```

### Conditional Timeline

```javascript
const tl = anime.timeline()

tl.add({
  targets: '.element1',
  translateX: 250
})

if (condition) {
  tl.add({
    targets: '.element2',
    opacity: [0, 1]
  })
}

tl.add({
  targets: '.element3',
  scale: [0, 1]
})
```

---

## Timeline vs Individual Animations

### Without Timeline (Hard to Manage)

```javascript
anime({
  targets: '.box1',
  translateX: 250,
  duration: 1000
})

setTimeout(() => {
  anime({
    targets: '.box2',
    translateX: 250,
    duration: 1000
  })
}, 1000)

setTimeout(() => {
  anime({
    targets: '.box3',
    translateX: 250,
    duration: 1000
  })
}, 2000)
```

### With Timeline (Clean & Maintainable)

```javascript
const tl = anime.timeline()

tl.add({
  targets: '.box1',
  translateX: 250,
  duration: 1000
})
.add({
  targets: '.box2',
  translateX: 250,
  duration: 1000
})
.add({
  targets: '.box3',
  translateX: 250,
  duration: 1000
})
```

---

## Performance Optimization

### 1. Use Relative Offsets

```javascript
// ✅ Good: Flexible timing
.add({...}, '-=500')

// ❌ Avoid: Brittle absolute timing
.add({...}, 1500)
```

### 2. Batch Similar Animations

```javascript
// ✅ Good: Single animation
tl.add({
  targets: ['.el1', '.el2', '.el3'],
  translateX: 250
})

// ❌ Avoid: Multiple separate animations
tl.add({ targets: '.el1', translateX: 250 })
  .add({ targets: '.el2', translateX: 250 })
  .add({ targets: '.el3', translateX: 250 })
```

### 3. Set Default Parameters

```javascript
// ✅ Good: DRY
const tl = anime.timeline({
  easing: 'easeOutExpo',
  duration: 800
})

// ❌ Avoid: Repetition
tl.add({ targets: '.el1', easing: 'easeOutExpo', duration: 800 })
  .add({ targets: '.el2', easing: 'easeOutExpo', duration: 800 })
```

---

## Common Mistakes

### ❌ Wrong: Missing Offset Operator

```javascript
tl.add({
  targets: '.box1',
  translateX: 250
})
.add({
  targets: '.box2',
  translateX: 250
}, '500') // Treated as absolute time!
```

### ✅ Correct: Use Relative Operator

```javascript
tl.add({
  targets: '.box1',
  translateX: 250
})
.add({
  targets: '.box2',
  translateX: 250
}, '+=500') // Relative to previous
```

### ❌ Wrong: Forgetting autoplay: false

```javascript
const tl = anime.timeline() // Starts immediately

// Later...
button.addEventListener('click', () => {
  tl.play() // Already playing!
})
```

### ✅ Correct: Disable autoplay

```javascript
const tl = anime.timeline({ autoplay: false })

button.addEventListener('click', () => {
  tl.play() // Now it works
})
```

---

## Real-World Examples

### Hero Section Animation

```javascript
const heroTimeline = anime.timeline({
  easing: 'easeOutExpo'
})

heroTimeline
  .add({
    targets: '.hero-bg',
    scale: [1.2, 1],
    opacity: [0, 1],
    duration: 1200
  })
  .add({
    targets: '.hero-title',
    translateY: [100, 0],
    opacity: [0, 1],
    duration: 800
  }, '-=800')
  .add({
    targets: '.hero-subtitle',
    translateY: [50, 0],
    opacity: [0, 1],
    duration: 600
  }, '-=400')
  .add({
    targets: '.hero-cta',
    scale: [0, 1],
    duration: 400
  }, '-=200')
```

### Card Flip Animation

```javascript
function flipCard(card) {
  const tl = anime.timeline({ autoplay: false })

  tl.add({
    targets: card.querySelector('.front'),
    rotateY: [0, 90],
    duration: 300,
    easing: 'easeInQuad'
  })
  .add({
    targets: card.querySelector('.back'),
    rotateY: [-90, 0],
    duration: 300,
    easing: 'easeOutQuad'
  }, '-=0')

  return tl
}
```

### Notification Toast

```javascript
function showToast(toast) {
  const tl = anime.timeline()

  tl.add({
    targets: toast,
    translateX: [400, 0],
    opacity: [0, 1],
    duration: 400,
    easing: 'easeOutBack'
  })
  .add({
    targets: toast,
    opacity: [1, 0],
    duration: 300,
    easing: 'easeInQuad'
  }, '+=3000')

  return tl
}
```

---

## Debugging Timelines

### Log Timeline Progress

```javascript
const tl = anime.timeline({
  update: (tl) => {
    console.log(`Progress: ${tl.progress.toFixed(2)}%`)
    console.log(`Current time: ${tl.currentTime}ms`)
  }
})
```

### Visualize Timeline

```javascript
const tl = anime.timeline()

tl.add({
  targets: '.box1',
  translateX: 250,
  duration: 1000,
  begin: () => console.log('[0ms] Box1 begins'),
  complete: () => console.log('[1000ms] Box1 completes')
})
.add({
  targets: '.box2',
  translateX: 250,
  duration: 1000,
  begin: () => console.log('[1000ms] Box2 begins'),
  complete: () => console.log('[2000ms] Box2 completes')
}, '-=500')
```

---

## Resources

- Official Timeline Documentation: https://animejs.com/documentation/#timeline
- Timeline Examples: https://codepen.io/collection/DxpqGJ/
- Advanced Sequencing: https://animejs.com/documentation/#timelineBasics



===== FILE: plugins/individual/animejs/agents/animejs-choreographer.md =====

# Anime.js Animation Choreographer

## Role

Expert animation choreographer specializing in Anime.js animation design, timing, and orchestration.

## Expertise

- Animation timing and easing
- Timeline sequencing
- Performance-optimized animations
- Cross-library animation integration
- Interactive animation patterns
- Scroll-driven animation design

## When to use

Activate this agent when working on:
- Complex animation sequences
- Multi-element choreography
- Scroll-triggered animations
- Interactive animation systems
- Animation performance optimization

## Approach

1. Understand animation goals and user experience
2. Design animation timing and sequencing
3. Implement using Anime.js best practices
4. Optimize for smooth 60fps performance
5. Test across devices and browsers

## Tools

This agent has access to:
- Anime.js skill knowledge
- Animation pattern libraries
- Performance optimization techniques
- Timeline management strategies



===== FILE: plugins/individual/animejs/commands/animation_generator.md =====

# /animejs-animation_generator

Anime.js - Animation Generator

## Description

Executes the animation_generator script for Anime.js.

## Usage

```bash
/animejs-animation_generator
```

## Implementation

This command runs the `animation_generator.py` script from the Anime.js skill, which provides automated assistance for animation generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/animejs/commands/timeline_builder.md =====

# /animejs-timeline_builder

Anime.js - Timeline Builder

## Description

Executes the timeline_builder script for Anime.js.

## Usage

```bash
/animejs-timeline_builder
```

## Implementation

This command runs the `timeline_builder.py` script from the Anime.js skill, which provides automated assistance for timeline builder.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/animejs/skills/animejs/scripts/animation_generator.py =====

```py
#!/usr/bin/env python3
"""
Anime.js Animation Generator

Generates Anime.js animation boilerplate code for common animation patterns.

Usage:
    ./animation_generator.py                    # Interactive mode
    ./animation_generator.py --type stagger     # Generate stagger animation
    ./animation_generator.py --type timeline    # Generate timeline sequence

Animation Types:
    basic           - Simple translateX/Y, opacity animation
    stagger         - Sequential reveal with stagger
    grid-stagger    - Grid-based stagger animation
    svg-line        - SVG line drawing animation
    svg-morph       - SVG path morphing animation
    timeline        - Multi-step timeline sequence
    keyframe        - Keyframe animation with multiple steps
    scroll          - Scroll-triggered animation
"""

import sys

ANIMATION_TYPES = {
    'basic': {
        'name': 'Basic Animation',
        'description': 'Simple translateX/Y, opacity animation',
        'code': '''anime({
  targets: '.element',
  translateX: 250,
  rotate: '1turn',
  opacity: [0, 1],
  duration: 800,
  easing: 'easeInOutQuad'
})'''
    },

    'stagger': {
        'name': 'Stagger Animation',
        'description': 'Sequential reveal with stagger effect',
        'code': '''anime({
  targets: '.stagger-element',
  translateY: [100, 0],
  opacity: [0, 1],
  delay: anime.stagger(100), // Increment delay by 100ms
  easing: 'easeOutQuad',
  duration: 600
})'''
    },

    'grid-stagger': {
        'name': 'Grid Stagger Animation',
        'description': 'Grid-based stagger from center',
        'code': '''anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    grid: [14, 5],        // 14 columns, 5 rows
    from: 'center',       // Start from center
    axis: 'x'             // Primary axis
  }),
  easing: 'easeOutElastic(1, .8)',
  duration: 600
})'''
    },

    'svg-line': {
        'name': 'SVG Line Drawing',
        'description': 'SVG path line drawing animation',
        'code': '''anime({
  targets: 'path',
  strokeDashoffset: [anime.setDashoffset, 0],
  easing: 'easeInOutQuad',
  duration: 2000,
  delay: (el, i) => i * 250
})'''
    },

    'svg-morph': {
        'name': 'SVG Path Morphing',
        'description': 'Morph between SVG path shapes',
        'code': '''anime({
  targets: '#morphing-path',
  d: [
    { value: 'M10 80 Q 77.5 10, 145 80' },  // Start shape
    { value: 'M10 80 Q 77.5 150, 145 80' }  // End shape
  ],
  duration: 2000,
  easing: 'easeInOutQuad',
  loop: true,
  direction: 'alternate'
})'''
    },

    'timeline': {
        'name': 'Timeline Sequence',
        'description': 'Multi-step timeline with overlapping animations',
        'code': '''const tl = anime.timeline({
  easing: 'easeOutExpo',
  duration: 750
})

tl.add({
  targets: '.title',
  translateY: [-50, 0],
  opacity: [0, 1]
})
.add({
  targets: '.subtitle',
  translateY: [-30, 0],
  opacity: [0, 1]
}, '-=500')  // Start 500ms before previous ends
.add({
  targets: '.button',
  scale: [0, 1],
  opacity: [0, 1]
}, '-=300')'''
    },

    'keyframe': {
        'name': 'Keyframe Animation',
        'description': 'Multiple keyframes for complex motion',
        'code': '''anime({
  targets: '.element',
  keyframes: [
    { translateX: 100 },
    { translateY: 100 },
    { translateX: 0 },
    { translateY: 0 }
  ],
  duration: 4000,
  easing: 'easeInOutQuad',
  loop: true
})'''
    },

    'scroll': {
        'name': 'Scroll-Triggered Animation',
        'description': 'Animation controlled by scroll position',
        'code': '''const animation = anime({
  targets: '.scroll-element',
  translateY: [100, 0],
  opacity: [0, 1],
  easing: 'easeOutQuad',
  autoplay: false
})

window.addEventListener('scroll', () => {
  const scrollPercent = window.scrollY / (document.body.scrollHeight - window.innerHeight)
  animation.seek(animation.duration * scrollPercent)
})'''
    }
}

def print_header():
    """Print script header"""
    print("\n" + "="*60)
    print("Anime.js Animation Generator")
    print("="*60 + "\n")

def list_animation_types():
    """List all available animation types"""
    print("Available Animation Types:\n")
    for key, anim in ANIMATION_TYPES.items():
        print(f"  {key:15} - {anim['description']}")
    print()

def generate_animation(anim_type):
    """Generate animation code for given type"""
    if anim_type not in ANIMATION_TYPES:
        print(f"Error: Unknown animation type '{anim_type}'")
        print("Use --list to see available types")
        sys.exit(1)

    anim = ANIMATION_TYPES[anim_type]

    print(f"\n{anim['name']}")
    print("-" * 60)
    print(f"\n{anim['description']}\n")
    print("Generated Code:")
    print("-" * 60)
    print(anim['code'])
    print("\n" + "="*60 + "\n")

def interactive_mode():
    """Run in interactive mode"""
    print_header()
    list_animation_types()

    print("Enter animation type (or 'quit' to exit): ", end='')
    choice = input().strip().lower()

    if choice == 'quit':
        sys.exit(0)

    generate_animation(choice)

def main():
    """Main entry point"""
    args = sys.argv[1:]

    # No arguments - interactive mode
    if not args:
        interactive_mode()
        return

    # Parse arguments
    if '--list' in args:
        print_header()
        list_animation_types()
        return

    if '--type' in args:
        try:
            type_index = args.index('--type')
            anim_type = args[type_index + 1]
            print_header()
            generate_animation(anim_type)
        except IndexError:
            print("Error: --type requires an animation type")
            print("Usage: ./animation_generator.py --type <type>")
            sys.exit(1)
        return

    # Help or unknown arguments
    print(__doc__)

if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/animejs/skills/animejs/scripts/timeline_builder.py =====

```py
#!/usr/bin/env python3
"""
Anime.js Timeline Builder

Build complex Anime.js timeline sequences with interactive configuration.

Usage:
    ./timeline_builder.py                      # Interactive mode
    ./timeline_builder.py --preset hero        # Use preset configuration
    ./timeline_builder.py --preset modal       # Modal animation sequence

Timeline Presets:
    hero        - Hero section entrance animation
    modal       - Modal popup with content reveal
    cards       - Card stagger with button reveal
    loader      - Loading sequence with spinner
    page        - Page transition animation
    toast       - Notification toast animation
    menu        - Menu open/close animation
"""

import sys

TIMELINE_PRESETS = {
    'hero': {
        'name': 'Hero Section Animation',
        'description': 'Hero background, title, subtitle, and CTA reveal',
        'code': '''const heroTimeline = anime.timeline({
  easing: 'easeOutExpo'
})

heroTimeline
  .add({
    targets: '.hero-bg',
    scale: [1.2, 1],
    opacity: [0, 1],
    duration: 1200
  })
  .add({
    targets: '.hero-title',
    translateY: [100, 0],
    opacity: [0, 1],
    duration: 800
  }, '-=800')  // Overlap by 800ms
  .add({
    targets: '.hero-subtitle',
    translateY: [50, 0],
    opacity: [0, 1],
    duration: 600
  }, '-=400')
  .add({
    targets: '.hero-cta',
    scale: [0, 1],
    duration: 400
  }, '-=200')'''
    },

    'modal': {
        'name': 'Modal Popup Animation',
        'description': 'Modal entrance with header, body, and footer reveal',
        'code': '''const tl = anime.timeline({
  easing: 'easeOutExpo',
  duration: 750
})

tl.add({
  targets: '.modal',
  scale: [0, 1],
  opacity: [0, 1]
})
.add({
  targets: '.modal-header',
  translateY: [-20, 0],
  opacity: [0, 1]
}, '-=500')
.add({
  targets: '.modal-body',
  translateY: [20, 0],
  opacity: [0, 1]
}, '-=400')
.add({
  targets: '.modal-footer',
  opacity: [0, 1]
}, '-=300')'''
    },

    'cards': {
        'name': 'Card Grid Animation',
        'description': 'Cards stagger in, then button appears',
        'code': '''const tl = anime.timeline()

tl.add({
  targets: '.card',
  translateY: [100, 0],
  opacity: [0, 1],
  delay: anime.stagger(100),
  duration: 600,
  easing: 'easeOutQuad'
})
.add({
  targets: '.button',
  scale: [0, 1],
  duration: 400,
  easing: 'easeOutBack'
}, '-=200')'''
    },

    'loader': {
        'name': 'Loading Sequence',
        'description': 'Loader background, text, spinner, then fade to content',
        'code': '''const tl = anime.timeline()

tl.add({
  targets: '.loader-bg',
  scaleY: [0, 1],
  duration: 400,
  easing: 'easeInOutQuad'
})
.add({
  targets: '.loader-text',
  opacity: [0, 1],
  translateY: [20, 0],
  duration: 600
}, '-=200')
.add({
  targets: '.loader-spinner',
  rotate: '1turn',
  duration: 800,
  loop: 3
}, '-=400')
.add({
  targets: '.loader',
  opacity: 0,
  duration: 400
}, '+=500')
.add({
  targets: '.content',
  translateY: [50, 0],
  opacity: [0, 1],
  duration: 600
})'''
    },

    'page': {
        'name': 'Page Transition',
        'description': 'Slide out old page, slide in new page',
        'code': '''function pageTransition(oldPage, newPage) {
  const tl = anime.timeline()

  tl.add({
    targets: oldPage,
    translateX: [0, -100],
    opacity: [1, 0],
    duration: 400,
    easing: 'easeInQuad'
  })
  .add({
    targets: newPage,
    translateX: [100, 0],
    opacity: [0, 1],
    duration: 400,
    easing: 'easeOutQuad'
  }, '-=200')  // Overlap by 200ms for smooth transition

  return tl
}'''
    },

    'toast': {
        'name': 'Toast Notification',
        'description': 'Toast slides in, stays, then fades out',
        'code': '''function showToast(toast) {
  const tl = anime.timeline()

  tl.add({
    targets: toast,
    translateX: [400, 0],
    opacity: [0, 1],
    duration: 400,
    easing: 'easeOutBack'
  })
  .add({
    targets: toast,
    opacity: [1, 0],
    duration: 300,
    easing: 'easeInQuad'
  }, '+=3000')  // Wait 3 seconds before fading out

  return tl
}'''
    },

    'menu': {
        'name': 'Menu Open Animation',
        'description': 'Menu slides in with staggered items',
        'code': '''const tl = anime.timeline({ autoplay: false })

tl.add({
  targets: '.menu-overlay',
  translateX: ['-100%', 0],
  duration: 400,
  easing: 'easeOutQuad'
})
.add({
  targets: '.menu-item',
  translateX: [-50, 0],
  opacity: [0, 1],
  delay: anime.stagger(80),
  duration: 500,
  easing: 'easeOutExpo'
}, '-=200')

// Play on button click
document.querySelector('.menu-button').addEventListener('click', () => {
  tl.play()
})'''
    }
}

def print_header():
    """Print script header"""
    print("\n" + "="*60)
    print("Anime.js Timeline Builder")
    print("="*60 + "\n")

def list_presets():
    """List all available timeline presets"""
    print("Available Timeline Presets:\n")
    for key, preset in TIMELINE_PRESETS.items():
        print(f"  {key:12} - {preset['description']}")
    print()

def generate_timeline(preset_name):
    """Generate timeline code for given preset"""
    if preset_name not in TIMELINE_PRESETS:
        print(f"Error: Unknown preset '{preset_name}'")
        print("Use --list to see available presets")
        sys.exit(1)

    preset = TIMELINE_PRESETS[preset_name]

    print(f"\n{preset['name']}")
    print("-" * 60)
    print(f"\n{preset['description']}\n")
    print("Generated Timeline:")
    print("-" * 60)
    print(preset['code'])
    print("\n" + "="*60 + "\n")

def generate_custom_timeline():
    """Generate custom timeline with user input"""
    print("\nCustom Timeline Builder")
    print("-" * 60)
    print("\nEnter number of animation steps: ", end='')
    try:
        num_steps = int(input().strip())
    except ValueError:
        print("Error: Invalid number")
        sys.exit(1)

    if num_steps < 1 or num_steps > 10:
        print("Error: Number of steps must be between 1 and 10")
        sys.exit(1)

    print("\nGenerating timeline with", num_steps, "steps...\n")

    # Generate timeline code
    code = "const tl = anime.timeline({\n"
    code += "  duration: 750,\n"
    code += "  easing: 'easeOutExpo'\n"
    code += "})\n\n"

    for i in range(num_steps):
        code += f"tl.add({{\n"
        code += f"  targets: '.element-{i+1}',\n"
        code += f"  translateY: [50, 0],\n"
        code += f"  opacity: [0, 1]\n"
        if i > 0:
            code += f"}}, '-=300')  // Step {i+1}\n"
        else:
            code += f"}})  // Step {i+1}\n"

        if i < num_steps - 1:
            code += "\n"

    print("Generated Timeline:")
    print("-" * 60)
    print(code)
    print("\n" + "="*60 + "\n")

def interactive_mode():
    """Run in interactive mode"""
    print_header()
    list_presets()

    print("Enter preset name (or 'custom' for custom builder, 'quit' to exit): ", end='')
    choice = input().strip().lower()

    if choice == 'quit':
        sys.exit(0)
    elif choice == 'custom':
        generate_custom_timeline()
    else:
        generate_timeline(choice)

def main():
    """Main entry point"""
    args = sys.argv[1:]

    # No arguments - interactive mode
    if not args:
        interactive_mode()
        return

    # Parse arguments
    if '--list' in args:
        print_header()
        list_presets()
        return

    if '--preset' in args:
        try:
            preset_index = args.index('--preset')
            preset_name = args[preset_index + 1]
            print_header()
            generate_timeline(preset_name)
        except IndexError:
            print("Error: --preset requires a preset name")
            print("Usage: ./timeline_builder.py --preset <name>")
            sys.exit(1)
        return

    # Help or unknown arguments
    print(__doc__)

if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/animejs/skills/animejs/assets/README.md =====

# Anime.js - Assets

This directory contains starter templates and example documentation for Anime.js animations.

## Contents

### Starter Template (Recommended)

For a complete Anime.js starter template with Vite:

```bash
# Create new project with Vite (vanilla JS)
npm create vite@latest my-anime-app -- --template vanilla

# Navigate and install
cd my-anime-app
npm install

# Add Anime.js
npm install animejs
```

### Official Examples

The Anime.js team maintains excellent examples at:
- **Documentation**: https://animejs.com/documentation/
- **CodePen Examples**: https://codepen.io/collection/DxpqGJ/
- **Official Repository**: https://github.com/juliangarnier/anime

### Recommended Examples by Category

**Basic Animations:**
- Simple animation: https://codepen.io/juliangarnier/pen/KRwwOL
- Property parameters: https://codepen.io/juliangarnier/pen/LpWPgj
- Function-based values: https://codepen.io/juliangarnier/pen/gmOwJX

**Stagger Animations:**
- Basic stagger: https://codepen.io/juliangarnier/pen/PboRJN
- Stagger from center: https://codepen.io/juliangarnier/pen/WNNwQa
- Grid stagger: https://codepen.io/juliangarnier/pen/JXaKpP
- Stagger easing: https://codepen.io/juliangarnier/pen/QMMmQK

**Timeline Animations:**
- Basic timeline: https://codepen.io/juliangarnier/pen/grVWYq
- Timeline offsets: https://codepen.io/juliangarnier/pen/xLOXJX
- Timeline controls: https://codepen.io/juliangarnier/pen/oWjmWd

**SVG Animations:**
- Line drawing: https://codepen.io/juliangarnier/pen/XdqyNw
- Path morphing: https://codepen.io/juliangarnier/pen/mWEOmL
- Motion path: https://codepen.io/juliangarnier/pen/NqYKQL

**Advanced Patterns:**
- Keyframes: https://codepen.io/juliangarnier/pen/QMMmQK
- Scroll-driven: https://codepen.io/juliangarnier/pen/ZqyEJw
- Custom easing: https://codepen.io/juliangarnier/pen/YBBRvG

## Quick Start Template

Minimal Anime.js setup:

### package.json
```json
{
  "name": "animejs-starter",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "animejs": "^3.2.2"
  },
  "devDependencies": {
    "vite": "^5.0.8"
  }
}
```

### index.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Anime.js Starter</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <div class="container">
    <h1>Anime.js Animation Demo</h1>

    <div class="example basic-animation">
      <h2>Basic Animation</h2>
      <div class="box box1"></div>
      <button id="basic-btn">Play</button>
    </div>

    <div class="example stagger-animation">
      <h2>Stagger Animation</h2>
      <div class="stagger-grid">
        <div class="stagger-item"></div>
        <div class="stagger-item"></div>
        <div class="stagger-item"></div>
        <div class="stagger-item"></div>
        <div class="stagger-item"></div>
        <div class="stagger-item"></div>
      </div>
      <button id="stagger-btn">Play</button>
    </div>

    <div class="example timeline-animation">
      <h2>Timeline Animation</h2>
      <div class="timeline-elements">
        <div class="timeline-box box1"></div>
        <div class="timeline-box box2"></div>
        <div class="timeline-box box3"></div>
      </div>
      <button id="timeline-btn">Play</button>
    </div>
  </div>

  <script type="module" src="/main.js"></script>
</body>
</html>
```

### main.js
```javascript
import anime from 'animejs/lib/anime.es.js'

// Basic Animation
document.getElementById('basic-btn').addEventListener('click', () => {
  anime({
    targets: '.box1',
    translateX: 250,
    rotate: '1turn',
    scale: [0.75, 1],
    duration: 800,
    easing: 'easeInOutQuad'
  })
})

// Stagger Animation
document.getElementById('stagger-btn').addEventListener('click', () => {
  anime({
    targets: '.stagger-item',
    scale: [0, 1],
    delay: anime.stagger(100),
    easing: 'easeOutElastic(1, .8)',
    duration: 600
  })
})

// Timeline Animation
document.getElementById('timeline-btn').addEventListener('click', () => {
  const tl = anime.timeline({
    easing: 'easeOutExpo',
    duration: 750
  })

  tl.add({
    targets: '.timeline-box.box1',
    translateX: 250
  })
  .add({
    targets: '.timeline-box.box2',
    translateX: 250
  }, '-=500')
  .add({
    targets: '.timeline-box.box3',
    translateX: 250
  }, '-=500')
})
```

### style.css
```css
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  min-height: 100vh;
  padding: 2rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 3rem;
  font-size: 3rem;
}

.example {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}

h2 {
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.box {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 8px;
  margin-bottom: 1rem;
}

.stagger-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.stagger-item {
  width: 100%;
  aspect-ratio: 1;
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  border-radius: 8px;
}

.timeline-elements {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.timeline-box {
  width: 60px;
  height: 60px;
}

.timeline-box.box1 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.timeline-box.box2 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.timeline-box.box3 { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }

button {
  background: white;
  color: #764ba2;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

button:hover {
  transform: scale(1.05);
}

button:active {
  transform: scale(0.95);
}
```

## Common Patterns

### Pattern 1: Sequential List Reveal

```javascript
anime({
  targets: '.list-item',
  translateY: [30, 0],
  opacity: [0, 1],
  delay: anime.stagger(80),
  easing: 'easeOutQuad',
  duration: 600
})
```

### Pattern 2: Grid Expand from Center

```javascript
anime({
  targets: '.grid-square',
  scale: [0, 1],
  delay: anime.stagger(30, {
    grid: [10, 10],
    from: 'center'
  }),
  easing: 'easeOutElastic(1, .8)',
  duration: 600
})
```

### Pattern 3: SVG Line Drawing

```javascript
anime({
  targets: 'path',
  strokeDashoffset: [anime.setDashoffset, 0],
  easing: 'easeInOutQuad',
  duration: 2000,
  delay: (el, i) => i * 250
})
```

### Pattern 4: Timeline Sequence

```javascript
const tl = anime.timeline({
  easing: 'easeOutExpo',
  duration: 750
})

tl.add({
  targets: '.title',
  translateY: [-50, 0],
  opacity: [0, 1]
})
.add({
  targets: '.subtitle',
  translateY: [-30, 0],
  opacity: [0, 1]
}, '-=500')
.add({
  targets: '.button',
  scale: [0, 1]
}, '-=300')
```

## Framework Integration

### With React

```jsx
import { useEffect, useRef } from 'react'
import anime from 'animejs/lib/anime.es.js'

function AnimatedComponent() {
  const ref = useRef(null)

  useEffect(() => {
    const animation = anime({
      targets: ref.current,
      translateX: 250,
      duration: 800,
      easing: 'easeInOutQuad'
    })

    return () => animation.pause()
  }, [])

  return <div ref={ref}>Animated</div>
}
```

### With Vue

```javascript
export default {
  mounted() {
    anime({
      targets: this.$el,
      translateX: 250,
      duration: 800
    })
  }
}
```

## TypeScript Support

For TypeScript projects, install types:

```bash
npm install --save-dev @types/animejs
```

## Performance Tips

1. **Use transforms and opacity** - GPU-accelerated properties
2. **Batch similar animations** - One animation for multiple targets
3. **Add will-change** to CSS for complex animations
4. **Use autoplay: false** for scroll-driven animations
5. **Pause animations** on cleanup in frameworks
6. **Limit element count** - Stagger works best with <100 elements

## Additional Resources

- **Official Documentation**: https://animejs.com/documentation/
- **API Reference**: https://animejs.com/documentation/#cssProperties
- **GitHub Repository**: https://github.com/juliangarnier/anime
- **CodePen Collection**: https://codepen.io/collection/DxpqGJ/
- **Community Examples**: https://animejs.com/documentation/#communityShowcase

---

For more patterns and reference documentation, see:
- `api_reference.md` - Complete Anime.js API
- `stagger_guide.md` - Stagger utilities deep dive
- `timeline_guide.md` - Timeline sequencing guide



# Skill: lottie-animations


===== FILE: plugins/individual/lottie-animations/skills/lottie-animations/SKILL.md =====

---
name: lottie-animations
description: After Effects animation rendering for web and React applications. Use this skill when implementing Lottie animations, JSON vector animations, interactive animated icons, micro-interactions, or loading animations. Triggers on tasks involving Lottie, lottie-web, lottie-react, dotLottie, After Effects JSON export, bodymovin, animated SVG alternatives, or designer-created animations. Complements GSAP ScrollTrigger and Framer Motion for scroll-driven and interactive animations.
---

# Lottie Animations

## Overview

Lottie is a library for rendering After Effects animations in real-time on web, iOS, Android, and React Native. Created by Airbnb, it allows designers to ship animations as easily as shipping static assets. Animations are exported from After Effects as JSON files using the Bodymovin plugin, then rendered natively with minimal performance overhead.

**When to use Lottie:**
- Designer-created animations that need pixel-perfect fidelity
- Complex animated icons and micro-interactions
- Loading animations and progress indicators
- Onboarding sequences and tutorial animations
- Marketing animations and promotional content
- Alternative to GIF/video with smaller file sizes and scalability

**Key advantages:**
- Vector-based (scalable without quality loss)
- Significantly smaller file sizes than GIF or video
- Editable at runtime (colors, speed, segments)
- Full designer control via After Effects
- Cross-platform rendering consistency
- Interactive controls (play, pause, seek, loop)

## Core Concepts

### Lottie Format Types

**1. JSON Lottie (.json)**
- Original Lottie format
- Exported from After Effects via Bodymovin plugin
- Human-readable JSON structure
- Larger file sizes (not compressed)
- Widely supported across all platforms

**2. dotLottie (.lottie)**
- Modern compressed format
- ZIP archive containing JSON + assets
- Supports multiple animations and themes in one file
- Smaller file sizes (up to 90% reduction)
- Recommended for production use

### Library Options

**lottie-web** (original library):
```javascript
import lottie from 'lottie-web';

lottie.loadAnimation({
  container: document.getElementById('lottie-container'),
  renderer: 'svg', // or 'canvas', 'html'
  loop: true,
  autoplay: true,
  path: 'animation.json' // or animationData: jsonData
});
```

**@lottiefiles/dotlottie-web** (modern, recommended):
```javascript
import { DotLottie } from '@lottiefiles/dotlottie-web';

new DotLottie({
  canvas: document.getElementById('canvas'),
  src: 'animation.lottie',
  autoplay: true,
  loop: true
});
```

**@lottiefiles/dotlottie-react** (React integration):
```jsx
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

<DotLottieReact
  src="animation.lottie"
  loop
  autoplay
  style={{ height: 300 }}
/>
```

**lottie-react** (alternative React wrapper):
```jsx
import Lottie from 'lottie-react';
import animationData from './animation.json';

<Lottie animationData={animationData} loop={true} />
```

### Animation Data Sources

**1. LottieFiles** (lottie.host)
- 100,000+ free animations
- Direct URL embedding
- CDN hosting

**2. Local JSON/dotLottie files**
- Bundled with application
- Better performance (no network request)
- Version control friendly

**3. After Effects export**
- Custom designer animations
- Bodymovin plugin required
- Export settings critical for file size

## Common Patterns

### 1. Basic HTML Integration with dotLottie-web

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    #canvas {
      width: 400px;
      height: 400px;
    }
  </style>
</head>
<body>
  <canvas id="canvas"></canvas>

  <script type="module">
    import { DotLottie } from 'https://cdn.jsdelivr.net/npm/@lottiefiles/dotlottie-web/+esm';

    new DotLottie({
      canvas: document.getElementById('canvas'),
      src: 'https://lottie.host/4db68bbd-31f6-4cd8-84eb-189de081159a/IGmMCqhzpt.lottie',
      autoplay: true,
      loop: true
    });
  </script>
</body>
</html>
```

### 2. React Component with Controls

```jsx
import React from 'react';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

const AnimatedButton = () => {
  const [dotLottie, setDotLottie] = React.useState(null);

  const handlePlay = () => dotLottie?.play();
  const handlePause = () => dotLottie?.pause();
  const handleStop = () => dotLottie?.stop();
  const handleSeek = (frame) => dotLottie?.setFrame(frame);

  return (
    <div>
      <DotLottieReact
        src="button-animation.lottie"
        loop
        autoplay={false}
        dotLottieRefCallback={setDotLottie}
        style={{ height: 200 }}
      />

      <div>
        <button onClick={handlePlay}>Play</button>
        <button onClick={handlePause}>Pause</button>
        <button onClick={handleStop}>Stop</button>
        <button onClick={() => handleSeek(30)}>Seek to frame 30</button>
      </div>
    </div>
  );
};
```

### 3. Event Listeners and Lifecycle Hooks

```jsx
import React, { useEffect } from 'react';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

const EventDrivenAnimation = () => {
  const [dotLottie, setDotLottie] = React.useState(null);

  useEffect(() => {
    if (!dotLottie) return;

    const onLoad = () => console.log('Animation loaded');
    const onPlay = () => console.log('Animation started');
    const onPause = () => console.log('Animation paused');
    const onComplete = () => console.log('Animation completed');
    const onFrame = ({ currentFrame }) => console.log('Frame:', currentFrame);

    dotLottie.addEventListener('load', onLoad);
    dotLottie.addEventListener('play', onPlay);
    dotLottie.addEventListener('pause', onPause);
    dotLottie.addEventListener('complete', onComplete);
    dotLottie.addEventListener('frame', onFrame);

    return () => {
      dotLottie.removeEventListener('load', onLoad);
      dotLottie.removeEventListener('play', onPlay);
      dotLottie.removeEventListener('pause', onPause);
      dotLottie.removeEventListener('complete', onComplete);
      dotLottie.removeEventListener('frame', onFrame);
    };
  }, [dotLottie]);

  return (
    <DotLottieReact
      src="animation.lottie"
      loop
      autoplay
      dotLottieRefCallback={setDotLottie}
    />
  );
};
```

### 4. Scroll-Driven Animation with lottie-react

```jsx
import Lottie from 'lottie-react';
import robotAnimation from './robot.json';

const ScrollAnimation = () => {
  const interactivity = {
    mode: 'scroll',
    actions: [
      {
        visibility: [0, 0.2],
        type: 'stop',
        frames: [0]
      },
      {
        visibility: [0.2, 0.45],
        type: 'seek',
        frames: [0, 45]
      },
      {
        visibility: [0.45, 1.0],
        type: 'loop',
        frames: [45, 60]
      }
    ]
  };

  return (
    <Lottie
      animationData={robotAnimation}
      style={{ height: 300 }}
      interactivity={interactivity}
    />
  );
};
```

### 5. Hover-Triggered Segment Playback

```jsx
import { useLottie, useLottieInteractivity } from 'lottie-react';
import likeButton from './like-button.json';

const HoverAnimation = () => {
  const lottieObj = useLottie({
    animationData: likeButton
  });

  const Animation = useLottieInteractivity({
    lottieObj,
    mode: 'cursor',
    actions: [
      {
        position: { x: [0, 1], y: [0, 1] },
        type: 'loop',
        frames: [45, 60]
      },
      {
        position: { x: -1, y: -1 },
        type: 'stop',
        frames: [45]
      }
    ]
  });

  return <div style={{ height: 300, border: '2px solid black' }}>{Animation}</div>;
};
```

### 6. Multi-Animation and Theme Support

```jsx
import { DotLottieReact } from '@lottiefiles/dotlottie-react';
import React, { useState, useEffect } from 'react';

const ThemedAnimation = () => {
  const [dotLottie, setDotLottie] = useState(null);
  const [animations, setAnimations] = useState([]);
  const [themes, setThemes] = useState([]);
  const [currentAnimationId, setCurrentAnimationId] = useState('');
  const [currentThemeId, setCurrentThemeId] = useState('');

  useEffect(() => {
    if (!dotLottie) return;

    const onLoad = () => {
      setAnimations(dotLottie.manifest.animations || []);
      setThemes(dotLottie.manifest.themes || []);
      setCurrentAnimationId(dotLottie.activeAnimationId);
      setCurrentThemeId(dotLottie.activeThemeId);
    };

    dotLottie.addEventListener('load', onLoad);
    return () => dotLottie.removeEventListener('load', onLoad);
  }, [dotLottie]);

  return (
    <div>
      <DotLottieReact
        src="multi-animation.lottie"
        dotLottieRefCallback={setDotLottie}
        animationId={currentAnimationId}
        themeId={currentThemeId}
      />

      {themes.length > 0 && (
        <select value={currentThemeId} onChange={(e) => setCurrentThemeId(e.target.value)}>
          {themes.map((theme) => (
            <option key={theme.id} value={theme.id}>{theme.id}</option>
          ))}
        </select>
      )}

      {animations.length > 0 && (
        <select value={currentAnimationId} onChange={(e) => setCurrentAnimationId(e.target.value)}>
          {animations.map((anim) => (
            <option key={anim.id} value={anim.id}>{anim.id}</option>
          ))}
        </select>
      )}
    </div>
  );
};
```

### 7. Web Worker for Performance (DotLottieWorker)

```javascript
import { DotLottieWorker } from '@lottiefiles/dotlottie-web';

// Offload animation rendering to a web worker
new DotLottieWorker({
  canvas: document.getElementById('canvas'),
  src: 'heavy-animation.lottie',
  autoplay: true,
  loop: true,
  workerId: 'worker-1' // Group multiple animations by worker
});

// Multiple animations in separate workers
new DotLottieWorker({
  canvas: document.getElementById('canvas-2'),
  src: 'animation-2.lottie',
  autoplay: true,
  loop: true,
  workerId: 'worker-2'
});
```

## Integration Patterns

### With GSAP ScrollTrigger

```jsx
import Lottie from 'lottie-react';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';
import animationData from './animation.json';

gsap.registerPlugin(ScrollTrigger);

const GSAPLottieIntegration = () => {
  const lottieRef = React.useRef();

  React.useEffect(() => {
    const anim = lottieRef.current;
    if (!anim) return;

    // Sync Lottie with scroll
    gsap.to(anim, {
      scrollTrigger: {
        trigger: '#animation-section',
        start: 'top center',
        end: 'bottom center',
        scrub: 1,
        onUpdate: (self) => {
          const frame = Math.floor(self.progress * (anim.totalFrames - 1));
          anim.goToAndStop(frame, true);
        }
      }
    });
  }, []);

  return (
    <div id="animation-section" style={{ height: '200vh' }}>
      <Lottie
        lottieRef={lottieRef}
        animationData={animationData}
        autoplay={false}
        loop={false}
      />
    </div>
  );
};
```

### With Framer Motion

```jsx
import { motion } from 'framer-motion';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

const MotionLottie = () => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
    >
      <DotLottieReact
        src="animation.lottie"
        loop
        autoplay
        style={{ height: 400 }}
      />
    </motion.div>
  );
};
```

### Vue 3 Integration

```vue
<script setup>
import { DotLottieVue } from '@lottiefiles/dotlottie-vue';
</script>

<template>
  <DotLottieVue
    style="height: 500px; width: 500px"
    autoplay
    loop
    src="https://path-to-animation.lottie"
  />
</template>
```

### Svelte Integration

```svelte
<script lang="ts">
  import { DotLottieSvelte } from '@lottiefiles/dotlottie-svelte';
  import type { DotLottie } from '@lottiefiles/dotlottie-svelte';

  let dotLottie: DotLottie | null = null;

  function play() {
    dotLottie?.play();
  }
</script>

<DotLottieSvelte
  src="animation.lottie"
  loop={true}
  autoplay={true}
  dotLottieRefCallback={(ref) => dotLottie = ref}
/>

<button on:click={play}>Play</button>
```

## Performance Optimization

### File Size Optimization

**1. Export Settings in After Effects:**
- Enable "Skip images that aren't used"
- Use "Glyphs" instead of fonts when possible
- Simplify paths (reduce points in illustrator)
- Avoid effects that create large data (particles, noise)
- Use shape layers instead of vector layers

**2. Compression:**
- Use dotLottie format (.lottie) for automatic compression
- Run JSON through Lottie optimizer tools
- Remove unnecessary metadata

**3. Lazy Loading:**
```jsx
const LazyLottie = () => {
  const [shouldLoad, setShouldLoad] = React.useState(false);

  React.useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        setShouldLoad(true);
      }
    });

    observer.observe(document.getElementById('lottie-trigger'));
    return () => observer.disconnect();
  }, []);

  return (
    <div id="lottie-trigger">
      {shouldLoad && <DotLottieReact src="animation.lottie" loop autoplay />}
    </div>
  );
};
```

### Runtime Performance

**1. Renderer Selection:**
```javascript
// SVG: Best quality, slower for complex animations
// Canvas: Better performance, rasterized
// HTML: Limited support, use only for simple animations

// For complex animations, prefer canvas
new DotLottie({
  canvas: document.getElementById('canvas'),
  src: 'animation.lottie',
  autoplay: true,
  loop: true,
  renderConfig: {
    devicePixelRatio: window.devicePixelRatio || 1
  }
});
```

**2. Web Workers:**
```javascript
// Offload to worker for heavy animations
import { DotLottieWorker } from '@lottiefiles/dotlottie-web';

new DotLottieWorker({
  canvas: document.getElementById('canvas'),
  src: 'heavy-animation.lottie',
  autoplay: true,
  loop: true
});
```

**3. Mobile Optimization:**
```javascript
// Reduce quality on mobile
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

new DotLottie({
  canvas: document.getElementById('canvas'),
  src: isMobile ? 'animation-low.lottie' : 'animation-high.lottie',
  autoplay: true,
  loop: true,
  renderConfig: {
    devicePixelRatio: isMobile ? 1 : window.devicePixelRatio
  }
});
```

## Common Pitfalls

### 1. Memory Leaks from Improper Cleanup

**Problem:** Not destroying Lottie instances when components unmount.

**Solution:**
```jsx
const SafeAnimation = () => {
  const [dotLottie, setDotLottie] = React.useState(null);

  React.useEffect(() => {
    return () => {
      // Always destroy instance on unmount
      dotLottie?.destroy();
    };
  }, [dotLottie]);

  return <DotLottieReact src="animation.lottie" dotLottieRefCallback={setDotLottie} />;
};
```

### 2. Event Listener Cleanup

**Problem:** Event listeners not removed, causing multiple handlers.

**Solution:**
```jsx
useEffect(() => {
  if (!dotLottie) return;

  const handleComplete = () => console.log('Complete');
  dotLottie.addEventListener('complete', handleComplete);

  // MUST return cleanup function
  return () => {
    dotLottie.removeEventListener('complete', handleComplete);
  };
}, [dotLottie]);
```

### 3. Large File Sizes

**Problem:** Exported JSON files are 500KB+ for simple animations.

**Solutions:**
- Simplify After Effects composition (reduce layers, keyframes)
- Use dotLottie format for compression
- Check Bodymovin export settings (disable "Include expressions" if not needed)
- Remove unused assets before export
- Use Lottie optimizer tools: https://lottiefiles.com/tools/lottie-editor

### 4. Animation Performance Issues

**Problem:** Animation stutters or drops frames.

**Solutions:**
- Switch from SVG to Canvas renderer
- Use `DotLottieWorker` for web worker rendering
- Reduce complexity in After Effects (fewer layers, simpler shapes)
- Lower devicePixelRatio on mobile
- Avoid animating too many properties simultaneously

### 5. Incorrect Path/URL References

**Problem:** Animation doesn't load due to CORS or incorrect paths.

**Solution:**
```jsx
// Use animationData for local imports (best for bundled apps)
import animationData from './animation.json';
<Lottie animationData={animationData} />

// OR use path for external URLs (requires CORS headers)
<DotLottieReact src="https://example.com/animation.lottie" />

// For Next.js, place in public/ folder
<DotLottieReact src="/animations/animation.lottie" />
```

### 6. After Effects Export Compatibility

**Problem:** Some After Effects features don't export to Lottie.

**Unsupported features:**
- Layer effects (drop shadows, glows) - use shape layers instead
- Blending modes (limited support)
- 3D layers
- Expressions (partial support)
- Track mattes (partial support)

**Solution:**
- Test export early and often
- Use LottieFiles preview before exporting
- Check Bodymovin compatibility: https://airbnb.io/lottie/#/supported-features
- Convert effects to shapes when possible

## Resources

This skill includes:

### scripts/
- `generate_lottie_component.py` - Generate React/Vue/Svelte Lottie component boilerplate
- `optimize_lottie.py` - Optimize Lottie JSON file size

### references/
- `api_reference.md` - Complete API documentation for lottie-web, lottie-react, and dotlottie-web
- `after_effects_export.md` - Guide for exporting animations from After Effects
- `performance_guide.md` - Detailed performance optimization strategies

### assets/
- `starter_lottie/` - Complete React + Vite starter template with Lottie examples
- `examples/` - Real-world Lottie animation patterns and use cases

## Related Skills

- **gsap-scrolltrigger** - For scroll-driven Lottie animations synchronized with page scroll
- **motion-framer** - Combine with Framer Motion for layout animations wrapping Lottie
- **animated-component-libraries** - Pre-built components that may include Lottie animations
- **threejs-webgl** - For 3D animations beyond Lottie's 2D capabilities
- **react-three-fiber** - Alternative for complex 3D animated scenes



===== FILE: plugins/individual/lottie-animations/skills/lottie-animations/references/after_effects_export.md =====

# After Effects to Lottie Export Guide

Complete guide for exporting Lottie animations from After Effects using the Bodymovin plugin.

## Prerequisites

1. **Adobe After Effects** (CC 2015 or later)
2. **Bodymovin Plugin** - Install from:
   - **Recommended:** AEsc scripts panel (Extension Manager)
   - Manual: https://aescripts.com/bodymovin/
   - LottieFiles plugin: https://lottiefiles.com/plugins/after-effects

## Installation

### Method 1: ZXP Installer (Recommended)

1. Download ZXP Installer: https://aescripts.com/learn/zxp-installer/
2. Download Bodymovin ZXP file
3. Drag ZXP file to ZXP Installer
4. Restart After Effects
5. Open Window → Extensions → Bodymovin

### Method 2: Manual Installation

1. Download Bodymovin
2. Extract to:
   - **Mac:** `/Applications/Adobe After Effects [version]/Scripts/ScriptUI Panels/`
   - **Windows:** `C:\Program Files\Adobe\Adobe After Effects [version]\Support Files\Scripts\ScriptUI Panels\`
3. Restart After Effects

## Export Settings

### Basic Export

1. Open Window → Extensions → Bodymovin
2. Select composition(s) to export
3. Click "Settings" icon (gear)
4. Configure options (see below)
5. Choose destination folder
6. Click "Render"

### Recommended Settings for Web

**Essential:**
- ✅ **Glyphs** - Convert text to shapes (reduces file size)
- ✅ **Hidden** - Skip hidden layers
- ✅ **Skip images that aren't used**
- ✅ **Compress JSON** - Minify output (smaller file)
- ⬜ **Export Mode: Demo** (uncheck for production)

**Advanced:**
- **Export Format:** JSON or dotLottie (.lottie)
- **dotLottie:** Recommended for production (90% smaller)
- **Segments:** Export specific frame ranges
- **Image Quality:** 80% (balance size vs quality)

### File Size Optimization Settings

```
✅ Glyphs (text as shapes)
✅ Compress JSON
✅ Skip images that aren't used
✅ Merge Paths (when possible)
⬜ Pretty Print JSON (development only)
⬜ Include in JSON (embed images - increases size)
```

**Expected File Sizes:**
- Simple icon animation: 5-20 KB
- Complex character animation: 50-150 KB
- Heavy illustration animation: 150-500 KB
- **If >500 KB:** Optimize composition (see below)

## Supported Features

### ✅ Fully Supported

**Shapes:**
- Shape layers (rect, ellipse, polygon, star)
- Paths and bezier curves
- Stroke and fill
- Trim paths
- Merge paths
- Repeaters

**Transforms:**
- Position, scale, rotation, opacity
- Anchor points
- Parenting

**Effects:**
- Stroke (via shape layers)
- Fill (via shape layers)
- Trim paths
- Merge paths

**Masks:**
- Shape masks
- Alpha mattes
- Luma mattes (partial)

**Text:**
- As glyphs (converted to shapes)
- Character animation (requires glyphs)

### ⚠️ Partial Support

**Expressions:**
- Simple expressions work
- Complex expressions may fail
- Test thoroughly after export

**Blending Modes:**
- Limited support
- Normal, Add, Multiply work best
- Others may render incorrectly

**Track Mattes:**
- Alpha mattes: Good support
- Luma mattes: Limited support
- Inverted mattes: May fail

### ❌ Not Supported

**Layer Effects:**
- Drop Shadow → Use shape layer shadow
- Glow → Use shape layer glow
- Bevel & Emboss → Pre-render as image
- All built-in effects → Convert to shapes

**3D Layers:**
- 3D transforms
- Cameras (except 2D camera moves)
- Lights

**Advanced:**
- Adjustment layers
- Time remapping
- Frame blending
- Motion blur (partial)
- Gradient strokes (use solid color)

## Optimization Techniques

### 1. Composition Setup

**Before Animating:**
- Work at 1920x1080 or smaller
- Use round numbers for dimensions
- 30 fps or 60 fps (avoid 23.976, 29.97)
- Keep composition under 5 seconds when possible

**Comp Settings:**
```
Width: 1920px (or target size)
Height: 1080px
Frame Rate: 30 fps
Duration: 2-5 seconds
```

### 2. Shape Layer Optimization

**DO:**
```
✅ Use Shape Layers (not vector layers from AI)
✅ Combine shapes with Merge Paths
✅ Use simple gradients (2-3 colors)
✅ Minimize anchor points (simplify paths)
✅ Use solid fills over gradients when possible
```

**DON'T:**
```
❌ Import AI files directly (convert to shapes)
❌ Use too many shapes (>50 layers = slow)
❌ Animate every property (only what's needed)
❌ Use gradient strokes (solid only)
```

### 3. Image Optimization

**Embedded Images:**
- Resize to actual displayed size
- Use JPG for photos (not PNG)
- Compress before import (TinyPNG)
- Avoid embedding if possible

**Alternative:**
- Use shape layers instead
- Pre-render complex elements
- Load images separately in code

### 4. Text Optimization

**Recommended Approach:**
```
1. Create text layer
2. Enable "Glyphs" in Bodymovin settings
3. Text converts to shapes automatically
```

**Manual Alternative:**
```
1. Select text layer
2. Right-click → Create Shapes from Text
3. Delete original text layer
4. Animate shape layers
```

**Benefits:**
- No font loading required
- Smaller file size
- Guaranteed consistent rendering

### 5. Animation Optimization

**Keyframe Reduction:**
```javascript
// After Effects: Select keyframes
// Right-click → Keyframe Assistant → Reduce Keys
// Threshold: 0.5-1.0 pixels
```

**Simplify Paths:**
```javascript
// Illustrator/After Effects
// Object → Path → Simplify
// Target: 85-90% of original points
```

**Limit Properties:**
```
Only animate:
  Position, Scale, Rotation, Opacity
  (Most performant)

Avoid animating:
  Anchor Point, Shape Path
  (More expensive)
```

## Common Export Issues

### Issue 1: Huge File Size (>500 KB)

**Causes:**
- Embedded images
- Too many keyframes
- Complex paths
- Text not converted to glyphs

**Solutions:**
```
1. Enable "Glyphs" setting
2. Enable "Skip images that aren't used"
3. Reduce keyframes (Keyframe Assistant → Reduce Keys)
4. Simplify paths in Illustrator
5. Remove unused layers
6. Export as dotLottie format
```

### Issue 2: Animation Doesn't Match Preview

**Causes:**
- Unsupported features used
- Expression errors
- Blending mode issues

**Solutions:**
```
1. Check Bodymovin console for warnings
2. Replace unsupported features
3. Simplify expressions
4. Use Normal blending mode
5. Test export immediately
```

### Issue 3: Text Rendering Incorrectly

**Causes:**
- Font not supported
- Glyphs not enabled
- Special characters

**Solutions:**
```
1. Enable "Glyphs" in Bodymovin settings
2. OR manually: Create Shapes from Text
3. Avoid special Unicode characters
4. Use web-safe fonts if not using glyphs
```

### Issue 4: Colors Look Different

**Causes:**
- Color space mismatch
- Blending mode issues
- Opacity calculation differences

**Solutions:**
```
1. Work in sRGB color space
2. Use Normal blending mode
3. Check opacity values (0-100%)
4. Avoid nested transparency
```

## Testing Workflow

### 1. Export & Preview

```bash
1. Export from After Effects
2. Preview on LottieFiles:
   https://lottiefiles.com/preview
3. Check file size (aim for <100 KB)
4. Test on target devices
```

### 2. Integration Testing

```javascript
// Quick HTML test
<!DOCTYPE html>
<html>
<body>
  <div id="lottie"></div>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
  <script>
    lottie.loadAnimation({
      container: document.getElementById('lottie'),
      renderer: 'svg',
      loop: true,
      autoplay: true,
      path: 'animation.json'
    });
  </script>
</body>
</html>
```

### 3. Performance Testing

```javascript
// Monitor FPS
const animation = lottie.loadAnimation({...});

let lastTime = performance.now();
let frameCount = 0;

animation.addEventListener('enterFrame', () => {
  frameCount++;
  const currentTime = performance.now();
  if (currentTime - lastTime >= 1000) {
    console.log('FPS:', frameCount);
    frameCount = 0;
    lastTime = currentTime;
  }
});

// Target: 60 FPS on desktop, 30 FPS on mobile
```

## Best Practices

### Pre-Export Checklist

```
☐ Composition is 1920x1080 or smaller
☐ Frame rate is 30 or 60 fps
☐ Duration is under 10 seconds
☐ All layers are named descriptively
☐ Unused layers are deleted
☐ Text is converted to shapes/glyphs enabled
☐ Images are optimized/removed
☐ No unsupported effects used
☐ Tested in Bodymovin preview
☐ File size is under 100 KB (target)
```

### Export Settings Checklist

```
☐ Format: JSON or dotLottie (.lottie)
☐ Glyphs: Enabled
☐ Hidden: Checked
☐ Skip unused images: Checked
☐ Compress JSON: Enabled
☐ Pretty Print: Disabled (production)
☐ Image Quality: 80%
☐ Export Mode: Standard (not Demo)
```

### Post-Export Checklist

```
☐ Preview on LottieFiles.com
☐ Check file size (<100 KB ideal)
☐ Test in target browser/device
☐ Verify animation timing
☐ Check colors/rendering
☐ Test playback controls
☐ Verify loop behavior
☐ Test on mobile devices
```

## Resources

- **LottieFiles Preview:** https://lottiefiles.com/preview
- **Supported Features:** https://airbnb.io/lottie/#/supported-features
- **Bodymovin Plugin:** https://aescripts.com/bodymovin/
- **LottieFiles Plugin:** https://lottiefiles.com/plugins/after-effects
- **File Size Optimizer:** https://lottiefiles.com/tools/lottie-editor

## Troubleshooting

### Bodymovin Panel Not Showing

```
1. Check installation path is correct
2. Restart After Effects completely
3. Enable "Allow Scripts to Write Files"
   (Edit → Preferences → Scripting & Expressions)
4. Reinstall using ZXP Installer
```

### Export Fails/Crashes

```
1. Update to latest After Effects version
2. Update Bodymovin plugin
3. Simplify composition (remove complex features)
4. Export smaller sections separately
5. Check After Effects error log
```

### Animation Too Large

```
1. Export as dotLottie (90% smaller)
2. Reduce composition dimensions
3. Simplify paths (fewer anchor points)
4. Remove embedded images
5. Reduce keyframe count
6. Use solid colors over gradients
```



===== FILE: plugins/individual/lottie-animations/skills/lottie-animations/references/api_reference.md =====

# Lottie API Reference

Complete API documentation for lottie-web, lottie-react, dotlottie-web, and dotlottie-react libraries.

## dotlottie-web API

### DotLottie Constructor

```javascript
import { DotLottie } from '@lottiefiles/dotlottie-web';

const dotLottie = new DotLottie(config);
```

**Config Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `canvas` | HTMLCanvasElement | **required** | The canvas element to render the animation |
| `src` | string | **required** | URL to .lottie or .json file |
| `autoplay` | boolean | `true` | Auto-start animation on load |
| `loop` | boolean | `true` | Loop animation continuously |
| `speed` | number | `1.0` | Playback speed multiplier (0.5 = half speed, 2 = double speed) |
| `mode` | string | `'forward'` | Playback mode: `'forward'`, `'reverse'`, `'bounce'`, `'reverse-bounce'` |
| `backgroundColor` | string | `null` | Canvas background color |
| `renderConfig` | object | `{}` | Rendering configuration |
| `data` | string \| ArrayBuffer | `null` | Inline animation data (alternative to src) |
| `marker` | string | `null` | Named marker to play |
| `segment` | [number, number] | `null` | Frame range to play [startFrame, endFrame] |
| `useFrameInterpolation` | boolean | `true` | Smooth frame transitions |

**Render Config Options:**

```javascript
renderConfig: {
  devicePixelRatio: window.devicePixelRatio || 1, // Pixel density
  freezeOnOffscreen: false, // Pause when not visible
  imageRendering: 'auto' // 'auto', 'crisp-edges', 'pixelated'
}
```

### DotLottie Methods

**Playback Control:**

```javascript
dotLottie.play();              // Play animation
dotLottie.pause();             // Pause animation
dotLottie.stop();              // Stop and reset to frame 0
dotLottie.setSpeed(speed);     // Set playback speed (e.g., 2 for double speed)
dotLottie.setLoop(loop);       // Enable/disable looping
dotLottie.setMode(mode);       // Set playback mode ('forward', 'reverse', 'bounce')
```

**Frame Navigation:**

```javascript
dotLottie.setFrame(frame);               // Seek to specific frame (0-indexed)
dotLottie.goToAndPlay(frame, isFrame);   // Jump to frame/time and play
dotLottie.goToAndStop(frame, isFrame);   // Jump to frame/time and stop
dotLottie.playSegments(segments, forceFlag); // Play frame range
```

**Animation Management:**

```javascript
dotLottie.loadAnimation(animationId);    // Load specific animation (multi-animation files)
dotLottie.setTheme(themeId);             // Set theme (multi-theme files)
dotLottie.resize();                      // Resize to canvas dimensions
dotLottie.destroy();                     // Cleanup and destroy instance
```

**State Machine (Interactive Lottie):**

```javascript
dotLottie.loadStateMachine(stateMachineId); // Load state machine
dotLottie.startStateMachine();              // Start state machine
dotLottie.stopStateMachine();               // Stop state machine
dotLottie.postStateMachineEvent(event);     // Post event to state machine
```

**State Machine Events:**

```javascript
dotLottie.postStateMachineEvent("Bool: true");
dotLottie.postStateMachineEvent("Bool: false");
dotLottie.postStateMachineEvent("String: example");
dotLottie.postStateMachineEvent("Numeric: 42.5");
dotLottie.postStateMachineEvent("OnPointerDown: 100 200");  // x, y
dotLottie.postStateMachineEvent("OnPointerUp: 100 200");
dotLottie.postStateMachineEvent("OnPointerMove: 100 200");
dotLottie.postStateMachineEvent("OnPointerEnter: 100 200");
dotLottie.postStateMachineEvent("OnPointerExit: 100 200");
dotLottie.postStateMachineEvent("OnComplete");
```

**Layer Information:**

```javascript
const boundingBox = dotLottie.getLayerBoundingBox(layerName);
// Returns: { x, y, width, height } or null
```

### DotLottie Properties

```javascript
dotLottie.currentFrame;          // Current frame number (read-only)
dotLottie.totalFrames;           // Total number of frames (read-only)
dotLottie.duration;              // Animation duration in seconds (read-only)
dotLottie.isPlaying;             // Boolean: is currently playing (read-only)
dotLottie.isLoaded;              // Boolean: animation loaded (read-only)
dotLottie.manifest;              // Manifest object (animations, themes) (read-only)
dotLottie.activeAnimationId;     // Current animation ID (read-only)
dotLottie.activeThemeId;         // Current theme ID (read-only)
```

### DotLottie Events

```javascript
// Add event listeners
dotLottie.addEventListener('load', onLoad);
dotLottie.addEventListener('play', onPlay);
dotLottie.addEventListener('pause', onPause);
dotLottie.addEventListener('stop', onStop);
dotLottie.addEventListener('complete', onComplete);
dotLottie.addEventListener('loopComplete', onLoopComplete);
dotLottie.addEventListener('frame', onFrame);
dotLottie.addEventListener('render', onRender);
dotLottie.addEventListener('destroy', onDestroy);

// Remove event listeners
dotLottie.removeEventListener('load', onLoad);
```

**Event Callbacks:**

```javascript
function onLoad() {
  console.log('Animation loaded');
}

function onPlay() {
  console.log('Animation started');
}

function onPause() {
  console.log('Animation paused');
}

function onStop() {
  console.log('Animation stopped');
}

function onComplete() {
  console.log('Animation completed');
}

function onLoopComplete() {
  console.log('Loop completed');
}

function onFrame({ currentFrame }) {
  console.log('Current frame:', currentFrame);
}

function onRender() {
  console.log('Frame rendered');
}

function onDestroy() {
  console.log('Instance destroyed');
}
```

---

## DotLottieWorker API

**Purpose:** Offload animation rendering to a Web Worker for better performance.

```javascript
import { DotLottieWorker } from '@lottiefiles/dotlottie-web';

new DotLottieWorker({
  canvas: document.getElementById('canvas'),
  src: 'animation.lottie',
  autoplay: true,
  loop: true,
  workerId: 'worker-1' // Optional: group multiple animations by worker
});
```

**Config:** Same as `DotLottie`, plus:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `workerId` | string | auto-generated | Worker ID for grouping animations |

**Use Case:** Complex animations that cause main thread lag.

---

## dotlottie-react API

### DotLottieReact Component

```jsx
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

<DotLottieReact
  src="animation.lottie"
  loop
  autoplay
  speed={1}
  mode="forward"
  backgroundColor="#ffffff"
  style={{ height: 400, width: 400 }}
  className="lottie-animation"
  dotLottieRefCallback={(instance) => setDotLottie(instance)}
  animationId="animation-1"
  themeId="light"
  marker="intro"
  segment={[0, 60]}
  useFrameInterpolation
  data={inlineData}
  renderConfig={{ devicePixelRatio: 2 }}
/>
```

**Props:**

All `DotLottie` config options are available as props, plus:

| Prop | Type | Description |
|------|------|-------------|
| `dotLottieRefCallback` | function | Callback to get dotLottie instance |
| `style` | object | Inline styles for wrapper div |
| `className` | string | CSS class for wrapper div |

**Getting Instance Reference:**

```jsx
const [dotLottie, setDotLottie] = useState(null);

<DotLottieReact
  src="animation.lottie"
  dotLottieRefCallback={setDotLottie}
/>

// Use instance
useEffect(() => {
  if (dotLottie) {
    dotLottie.play();
  }
}, [dotLottie]);
```

---

## lottie-web API (Original Library)

### lottie.loadAnimation()

```javascript
import lottie from 'lottie-web';

const animation = lottie.loadAnimation({
  container: document.getElementById('lottie-container'), // Required
  renderer: 'svg', // 'svg', 'canvas', 'html'
  loop: true,
  autoplay: true,
  path: 'animation.json', // URL to animation
  // OR
  animationData: jsonData, // Inline JSON data
  name: 'my-animation', // Optional name
  rendererSettings: {
    preserveAspectRatio: 'xMidYMid slice',
    progressiveLoad: false,
    hideOnTransparent: true,
    className: 'lottie-svg', // SVG class
    scaleMode: 'noScale' // 'noScale', 'fill', 'fit'
  }
});
```

### lottie-web Methods

**Playback:**

```javascript
animation.play();
animation.pause();
animation.stop();
animation.setSpeed(speed);        // 1 = normal, 0.5 = half speed
animation.setDirection(direction); // 1 = forward, -1 = reverse
animation.goToAndPlay(frame, isFrame);
animation.goToAndStop(frame, isFrame);
animation.playSegments(segments, forceFlag);
```

**Segments:**

```javascript
// Play frames 0-30 only
animation.playSegments([0, 30], false);

// Play multiple segments
animation.playSegments([[0, 30], [60, 90]], false);
```

**Properties:**

```javascript
animation.totalFrames;
animation.currentFrame;
animation.frameRate;
animation.isLoaded;
animation.isPaused;
animation.renderer;    // 'svg', 'canvas', 'html'
animation.name;
```

**Utility:**

```javascript
animation.resize();
animation.setSubframe(useSubframes); // Smooth subframe rendering
animation.getDuration(inFrames);     // Duration in frames or seconds
animation.destroy();
```

### lottie-web Events

```javascript
animation.addEventListener('DOMLoaded', onDOMLoaded);
animation.addEventListener('data_ready', onDataReady);
animation.addEventListener('config_ready', onConfigReady);
animation.addEventListener('complete', onComplete);
animation.addEventListener('loopComplete', onLoopComplete);
animation.addEventListener('enterFrame', onEnterFrame);
animation.addEventListener('segmentStart', onSegmentStart);
animation.addEventListener('destroy', onDestroy);

animation.removeEventListener('complete', onComplete);
```

**Event Callbacks:**

```javascript
function onEnterFrame(event) {
  console.log('Current frame:', event.currentTime);
  console.log('Direction:', event.direction); // 1 or -1
}

function onLoopComplete(event) {
  console.log('Loop completed:', event.currentLoop);
}
```

### lottie Global Methods

```javascript
lottie.play(name);            // Play animation by name
lottie.pause(name);           // Pause animation by name
lottie.stop(name);            // Stop animation by name
lottie.setSpeed(speed, name); // Set speed for named animation
lottie.setDirection(direction, name);
lottie.destroy(name);         // Destroy animation by name
lottie.loadAnimation(config); // Load new animation
lottie.searchAnimations();    // Auto-detect and load animations
```

---

## lottie-react API

### Lottie Component

```jsx
import Lottie from 'lottie-react';
import animationData from './animation.json';

<Lottie
  animationData={animationData}  // Required
  loop={true}
  autoplay={true}
  initialSegment={[0, 60]}
  onComplete={onComplete}
  onLoopComplete={onLoopComplete}
  onEnterFrame={onEnterFrame}
  onSegmentStart={onSegmentStart}
  onConfigReady={onConfigReady}
  onDataReady={onDataReady}
  onDataFailed={onDataFailed}
  onLoadedImages={onLoadedImages}
  onDOMLoaded={onDOMLoaded}
  onDestroy={onDestroy}
  style={{ height: 400 }}
  className="lottie-animation"
  lottieRef={lottieRef}
  interactivity={interactivityConfig}
/>
```

**Props:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `animationData` | object | **required** | Lottie JSON data |
| `loop` | boolean \| number | `true` | Loop animation (true = infinite, number = loop count) |
| `autoplay` | boolean | `true` | Auto-start on load |
| `initialSegment` | [number, number] | `null` | Start frame range |
| `onComplete` | function | `null` | Callback on animation complete |
| `onLoopComplete` | function | `null` | Callback on loop complete |
| `onEnterFrame` | function | `null` | Callback on each frame |
| `onSegmentStart` | function | `null` | Callback on segment start |
| `onConfigReady` | function | `null` | Callback on config ready |
| `onDataReady` | function | `null` | Callback on data ready |
| `onDataFailed` | function | `null` | Callback on data load failure |
| `onLoadedImages` | function | `null` | Callback on images loaded |
| `onDOMLoaded` | function | `null` | Callback on DOM loaded |
| `onDestroy` | function | `null` | Callback on destroy |
| `style` | object | `{}` | Inline styles |
| `className` | string | `''` | CSS class |
| `lottieRef` | React.RefObject | `null` | Ref to lottie instance |
| `interactivity` | object | `null` | Interactivity config (scroll/cursor) |

### Using lottieRef

```jsx
const lottieRef = useRef();

<Lottie animationData={animationData} lottieRef={lottieRef} />

// Access instance
useEffect(() => {
  if (lottieRef.current) {
    lottieRef.current.setSpeed(2);
    lottieRef.current.goToAndPlay(30, true);
  }
}, []);
```

### Interactivity Config

**Scroll Mode:**

```javascript
const interactivity = {
  mode: 'scroll',
  actions: [
    {
      visibility: [0, 0.3],  // When 0-30% visible
      type: 'stop',
      frames: [0]
    },
    {
      visibility: [0.3, 1],  // When 30-100% visible
      type: 'seek',
      frames: [0, 60]
    }
  ]
};
```

**Cursor Mode:**

```javascript
const interactivity = {
  mode: 'cursor',
  actions: [
    {
      position: { x: [0, 1], y: [0, 1] }, // Inside container
      type: 'loop',
      frames: [0, 60]
    },
    {
      position: { x: -1, y: -1 }, // Outside container
      type: 'stop',
      frames: [0]
    }
  ]
};
```

**Action Types:**

- `'stop'` - Stop at specified frame
- `'play'` - Play from current frame
- `'loop'` - Loop specified segment
- `'seek'` - Scrub through frames based on scroll/cursor position

---

## useLottie Hook

```javascript
import { useLottie } from 'lottie-react';
import animationData from './animation.json';

const { View, play, pause, stop, setSpeed, goToAndPlay, goToAndStop } = useLottie({
  animationData: animationData,
  loop: true,
  autoplay: true,
  initialSegment: [0, 60]
}, style);
```

**Returns:**

| Property | Type | Description |
|----------|------|-------------|
| `View` | React.Element | Rendered Lottie component |
| `play` | function | Play animation |
| `pause` | function | Pause animation |
| `stop` | function | Stop animation |
| `setSpeed` | function | Set playback speed |
| `setDirection` | function | Set direction (1 or -1) |
| `goToAndPlay` | function | Jump to frame and play |
| `goToAndStop` | function | Jump to frame and stop |
| `playSegments` | function | Play specific segments |
| `setSubframe` | function | Enable subframe rendering |
| `getDuration` | function | Get animation duration |
| `destroy` | function | Destroy instance |

---

## useLottieInteractivity Hook

```javascript
import { useLottie, useLottieInteractivity } from 'lottie-react';

const lottieObj = useLottie({ animationData });

const Animation = useLottieInteractivity({
  lottieObj,
  mode: 'scroll', // or 'cursor'
  actions: [
    {
      visibility: [0, 1],
      type: 'seek',
      frames: [0, 60]
    }
  ]
});

return Animation;
```

---

## Best Practices

1. **Always destroy instances on unmount:**
   ```javascript
   useEffect(() => {
     return () => {
       dotLottie?.destroy();
     };
   }, [dotLottie]);
   ```

2. **Use dotLottie format (.lottie) for production** - smaller file sizes

3. **Prefer Canvas renderer for complex animations** - better performance

4. **Use Web Workers (DotLottieWorker) for heavy animations** - offload from main thread

5. **Lazy load animations** - only load when visible (IntersectionObserver)

6. **Clean up event listeners:**
   ```javascript
   useEffect(() => {
     const handler = () => {};
     dotLottie?.addEventListener('complete', handler);
     return () => dotLottie?.removeEventListener('complete', handler);
   }, [dotLottie]);
   ```

7. **Use animationData prop (not path) for bundled animations** - faster, no network request



===== FILE: plugins/individual/lottie-animations/skills/lottie-animations/references/performance_guide.md =====

# Lottie Performance Optimization Guide

Comprehensive strategies for optimizing Lottie animation performance in production.

## Performance Metrics

**Target Performance:**
- **Desktop:** 60 FPS minimum
- **Mobile:** 30-60 FPS
- **File Size:** <100 KB ideal, <200 KB acceptable
- **Load Time:** <500ms for animation ready
- **Memory:** <50 MB per animation instance

## File Size Optimization

### 1. Use dotLottie Format

```javascript
// 90% smaller file size
<DotLottieReact src="animation.lottie" />  // ✅ 10-50 KB
// vs
<Lottie animationData={jsonData} />        // ❌ 100-500 KB
```

**Benefits:**
- ZIP compression (up to 90% reduction)
- Multiple animations in one file
- Theme support
- Faster parsing

### 2. Optimize JSON

**Before Export (After Effects):**
```
- Simplify paths (reduce anchor points)
- Merge shapes when possible
- Remove unused layers/keyframes
- Use solid colors over gradients
- Enable "Compress JSON" in Bodymovin
```

**After Export:**
```bash
# Use Lottie optimizer
https://lottiefiles.com/tools/lottie-editor

# Or gzip compression (server-side)
gzip animation.json  # 60-80% reduction
```

### 3. Lazy Loading

```jsx
import { lazy, Suspense } from 'react';

const LottieAnimation = lazy(() => import('./LottieAnimation'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LottieAnimation />
    </Suspense>
  );
}
```

**Intersection Observer Pattern:**

```jsx
const LazyLottie = ({ src }) => {
  const [shouldLoad, setShouldLoad] = useState(false);
  const ref = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setShouldLoad(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={ref}>
      {shouldLoad ? <DotLottieReact src={src} /> : <div style={{ height: 300 }} />}
    </div>
  );
};
```

## Runtime Performance

### 1. Renderer Selection

**SVG Renderer:**
```javascript
// Best quality, slower performance
// Use for: Simple icons, small animations, few instances
lottie.loadAnimation({
  renderer: 'svg',  // Vector-based, scalable
  container: element,
  path: 'animation.json'
});
```

**Canvas Renderer:**
```javascript
// Better performance, rasterized
// Use for: Complex animations, many instances, mobile
new DotLottie({
  canvas: canvasElement,  // ✅ Recommended for complex animations
  src: 'animation.lottie'
});
```

**Performance Comparison:**

| Renderer | Quality | Performance | Use Case |
|----------|---------|-------------|----------|
| SVG      | Excellent | Good (simple animations) | Icons, logos, simple UI |
| Canvas   | Good | Excellent | Complex animations, mobile |
| HTML     | Poor | Poor | Legacy support only |

### 2. Web Workers (Best Performance)

```javascript
import { DotLottieWorker } from '@lottiefiles/dotlottie-web';

// Offload rendering to separate thread
new DotLottieWorker({
  canvas: document.getElementById('canvas'),
  src: 'heavy-animation.lottie',
  autoplay: true,
  loop: true,
  workerId: 'worker-1'
});
```

**Benefits:**
- No main thread blocking
- Smooth scroll performance
- Multiple animations without lag
- Better mobile performance

**When to use:**
- Animation >100 KB
- Multiple simultaneous animations
- Scroll-driven animations
- Mobile devices

### 3. Device Pixel Ratio Optimization

```javascript
// Reduce quality on low-end devices
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
const isLowEnd = navigator.deviceMemory < 4; // GB

new DotLottie({
  canvas: canvas,
  src: 'animation.lottie',
  renderConfig: {
    devicePixelRatio: (isMobile || isLowEnd) ? 1 : window.devicePixelRatio
    // 1 = standard definition (faster)
    // 2 = retina (slower, better quality)
  }
});
```

### 4. Animation Complexity Control

**Adaptive Quality:**

```javascript
const getAnimationSrc = () => {
  const isMobile = /Mobile/i.test(navigator.userAgent);
  const isSlowDevice = navigator.hardwareConcurrency < 4;

  if (isMobile || isSlowDevice) {
    return 'animation-low.lottie';  // Simplified version
  }
  return 'animation-high.lottie';    // Full quality
};

<DotLottieReact src={getAnimationSrc()} />
```

**Frame Rate Reduction:**

```javascript
// Reduce frame rate on slow devices
const targetFPS = isMobile ? 30 : 60;

new DotLottie({
  canvas: canvas,
  src: 'animation.lottie',
  speed: 1,
  // Implemented via requestAnimationFrame throttling
});
```

## Memory Management

### 1. Proper Cleanup

```jsx
const AnimationComponent = () => {
  const [dotLottie, setDotLottie] = useState(null);

  useEffect(() => {
    return () => {
      // CRITICAL: Destroy on unmount
      dotLottie?.destroy();
    };
  }, [dotLottie]);

  return <DotLottieReact dotLottieRefCallback={setDotLottie} />;
};
```

### 2. Event Listener Cleanup

```javascript
useEffect(() => {
  if (!dotLottie) return;

  const handleComplete = () => console.log('Done');

  dotLottie.addEventListener('complete', handleComplete);

  // CRITICAL: Remove listeners
  return () => {
    dotLottie.removeEventListener('complete', handleComplete);
  };
}, [dotLottie]);
```

### 3. Instance Pooling

```javascript
// Reuse animation instances
class LottiePool {
  constructor() {
    this.pool = [];
    this.active = new Set();
  }

  acquire(src) {
    let instance = this.pool.find(i => i.src === src && !this.active.has(i));

    if (!instance) {
      instance = new DotLottie({ canvas: createCanvas(), src });
      this.pool.push(instance);
    }

    this.active.add(instance);
    return instance;
  }

  release(instance) {
    instance.stop();
    this.active.delete(instance);
  }

  cleanup() {
    this.pool.forEach(i => i.destroy());
    this.pool = [];
    this.active.clear();
  }
}
```

## Network Optimization

### 1. CDN Hosting

```jsx
// Host on CDN for better caching
<DotLottieReact
  src="https://cdn.example.com/animations/hero.lottie"
  loop
  autoplay
/>
```

**Benefits:**
- Edge caching (faster loads)
- Reduced server load
- Better global performance

### 2. Preloading Critical Animations

```html
<!-- Preload animation for faster display -->
<link rel="preload" href="/animations/hero.lottie" as="fetch" crossorigin>
```

```javascript
// Programmatic preload
const preloadAnimation = async (src) => {
  const response = await fetch(src);
  const blob = await response.blob();
  return URL.createObjectURL(blob);
};

// Use preloaded blob
const blobUrl = await preloadAnimation('/animation.lottie');
<DotLottieReact src={blobUrl} />
```

### 3. Service Worker Caching

```javascript
// service-worker.js
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('lottie-v1').then((cache) => {
      return cache.addAll([
        '/animations/hero.lottie',
        '/animations/loading.lottie'
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.url.endsWith('.lottie')) {
    event.respondWith(
      caches.match(event.request).then((response) => {
        return response || fetch(event.request);
      })
    );
  }
});
```

## Mobile Optimization

### 1. Reduce Quality on Mobile

```javascript
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

<DotLottieReact
  src={isMobile ? 'animation-mobile.lottie' : 'animation-desktop.lottie'}
  renderConfig={{
    devicePixelRatio: isMobile ? 1 : window.devicePixelRatio
  }}
/>
```

### 2. Pause on Offscreen

```javascript
useEffect(() => {
  if (!dotLottie) return;

  const observer = new IntersectionObserver(([entry]) => {
    if (entry.isIntersecting) {
      dotLottie.play();
    } else {
      dotLottie.pause();
    }
  });

  observer.observe(document.getElementById('lottie-container'));

  return () => observer.disconnect();
}, [dotLottie]);
```

### 3. Battery-Aware Performance

```javascript
// Reduce animation when low battery
navigator.getBattery?.().then((battery) => {
  if (battery.level < 0.2) {
    dotLottie.setSpeed(0.5); // Slower = less CPU
  }

  battery.addEventListener('levelchange', () => {
    if (battery.level < 0.2) {
      dotLottie.stop();
    }
  });
});
```

## Monitoring Performance

### 1. FPS Monitoring

```javascript
class FPSMonitor {
  constructor() {
    this.fps = 0;
    this.frames = 0;
    this.lastTime = performance.now();
  }

  update() {
    this.frames++;
    const currentTime = performance.now();

    if (currentTime - this.lastTime >= 1000) {
      this.fps = Math.round((this.frames * 1000) / (currentTime - this.lastTime));
      console.log(`FPS: ${this.fps}`);
      this.frames = 0;
      this.lastTime = currentTime;
    }

    requestAnimationFrame(() => this.update());
  }

  start() {
    this.update();
  }
}

const monitor = new FPSMonitor();
monitor.start();
```

### 2. Memory Usage Tracking

```javascript
if (performance.memory) {
  setInterval(() => {
    const used = (performance.memory.usedJSHeapSize / 1048576).toFixed(2);
    const total = (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2);
    console.log(`Memory: ${used} MB / ${total} MB`);
  }, 5000);
}
```

### 3. Performance Marks

```javascript
// Mark start
performance.mark('lottie-load-start');

const dotLottie = new DotLottie({...});

dotLottie.addEventListener('load', () => {
  // Mark end and measure
  performance.mark('lottie-load-end');
  performance.measure('lottie-load', 'lottie-load-start', 'lottie-load-end');

  const measure = performance.getEntriesByName('lottie-load')[0];
  console.log(`Load time: ${measure.duration}ms`);
});
```

## Common Performance Issues

### Issue 1: Animation Stutters

**Symptoms:** Dropped frames, jerky playback

**Solutions:**
```
1. Switch to Canvas renderer
2. Use DotLottieWorker for web worker rendering
3. Reduce devicePixelRatio (1 instead of 2)
4. Simplify animation (fewer shapes/keyframes)
5. Reduce number of simultaneous animations
```

### Issue 2: Slow Page Load

**Symptoms:** Long initial render time

**Solutions:**
```
1. Use lazy loading with IntersectionObserver
2. Preload critical animations only
3. Use dotLottie format (smaller files)
4. Load animations after page interactive
5. Use code splitting (React.lazy)
```

### Issue 3: Memory Leaks

**Symptoms:** Memory usage increases over time

**Solutions:**
```
1. Call destroy() on unmount
2. Remove all event listeners
3. Clear animation references
4. Avoid creating new instances repeatedly
5. Use instance pooling for frequently re-created animations
```

### Issue 4: Mobile Performance Poor

**Symptoms:** Slow on phones, smooth on desktop

**Solutions:**
```
1. Create mobile-optimized version (simpler)
2. Use Canvas renderer (not SVG)
3. Set devicePixelRatio to 1
4. Reduce animation frame rate (30 FPS)
5. Use DotLottieWorker
6. Pause when offscreen
```

## Best Practices Summary

**File Size:**
- ✅ Use dotLottie format (.lottie)
- ✅ Compress JSON
- ✅ Keep under 100 KB
- ✅ Optimize images (or remove)
- ✅ Simplify paths

**Runtime:**
- ✅ Use Canvas renderer for complex animations
- ✅ Use Web Workers (DotLottieWorker)
- ✅ Destroy instances on unmount
- ✅ Remove event listeners
- ✅ Lazy load animations

**Mobile:**
- ✅ Create mobile-optimized versions
- ✅ Set devicePixelRatio to 1
- ✅ Pause when offscreen
- ✅ Reduce quality on low-end devices

**Monitoring:**
- ✅ Track FPS (target 60 on desktop, 30 on mobile)
- ✅ Monitor memory usage
- ✅ Measure load times
- ✅ Test on real devices



===== FILE: plugins/individual/lottie-animations/agents/lottie-animations-choreographer.md =====

# Lottie Animation Choreographer

## Role

Expert animation choreographer specializing in Lottie animation design, timing, and orchestration.

## Expertise

- Animation timing and easing
- Timeline sequencing
- Performance-optimized animations
- Cross-library animation integration
- Interactive animation patterns
- Scroll-driven animation design

## When to use

Activate this agent when working on:
- Complex animation sequences
- Multi-element choreography
- Scroll-triggered animations
- Interactive animation systems
- Animation performance optimization

## Approach

1. Understand animation goals and user experience
2. Design animation timing and sequencing
3. Implement using Lottie best practices
4. Optimize for smooth 60fps performance
5. Test across devices and browsers

## Tools

This agent has access to:
- Lottie skill knowledge
- Animation pattern libraries
- Performance optimization techniques
- Timeline management strategies



===== FILE: plugins/individual/lottie-animations/commands/generate_lottie_component.md =====

# /lottie-animations-generate_lottie_component

Lottie - Generate Lottie Component

## Description

Executes the generate_lottie_component script for Lottie.

## Usage

```bash
/lottie-animations-generate_lottie_component
```

## Implementation

This command runs the `generate_lottie_component.py` script from the Lottie skill, which provides automated assistance for generate lottie component.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/lottie-animations/commands/optimize_lottie.md =====

# /lottie-animations-optimize_lottie

Lottie - Optimize Lottie

## Description

Executes the optimize_lottie script for Lottie.

## Usage

```bash
/lottie-animations-optimize_lottie
```

## Implementation

This command runs the `optimize_lottie.py` script from the Lottie skill, which provides automated assistance for optimize lottie.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/lottie-animations/skills/lottie-animations/scripts/generate_lottie_component.py =====

```py
#!/usr/bin/env python3
"""
Lottie Component Generator

Generates React, Vue, or Svelte Lottie component boilerplate with common patterns.

Usage:
    ./generate_lottie_component.py                          # Interactive mode
    ./generate_lottie_component.py --framework react --type basic
    ./generate_lottie_component.py --framework vue --type interactive
"""

import argparse
import sys

TEMPLATES = {
    'react_basic': '''import React from 'react';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

export const {ComponentName} = () => {
  return (
    <DotLottieReact
      src="{animationSrc}"
      loop
      autoplay
      style=\u007b\u007b height: {height}, width: {width} \u007d\u007d
    />
  );
};
''',
    'react_interactive': '''import React, \u007b useState \u007d from 'react';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

export const {ComponentName} = () => {
  const [dotLottie, setDotLottie] = useState(null);

  const handlePlay = () => dotLottie?.play();
  const handlePause = () => dotLottie?.pause();
  const handleStop = () => dotLottie?.stop();

  return (
    <div>
      <DotLottieReact
        src="{animationSrc}"
        loop
        autoplay=\u007bfalse\u007d
        dotLottieRefCallback=\u007bsetDotLottie\u007d
        style=\u007b\u007b height: {height}, width: {width} \u007d\u007d
      />
      <div style=\u007b\u007b marginTop: 16 \u007d\u007d>
        <button onClick=\u007bhandlePlay\u007d>Play</button>
        <button onClick=\u007bhandlePause\u007d>Pause</button>
        <button onClick=\u007bhandleStop\u007d>Stop</button>
      </div>
    </div>
  );
};
''',
    'vue_basic': '''<script setup>
import { DotLottieVue } from '@lottiefiles/dotlottie-vue';
</script>

<template>
  <DotLottieVue
    src="{animationSrc}"
    :autoplay="true"
    :loop="true"
    :style="{ height: '{height}px', width: '{width}px' }"
  />
</template>
''',
    'svelte_basic': '''<script lang="ts">
  import { DotLottieSvelte } from '@lottiefiles/dotlottie-svelte';
</script>

<DotLottieSvelte
  src="{animationSrc}"
  loop=\u007btrue\u007d
  autoplay=\u007btrue\u007d
  style="height: {height}px; width: {width}px;"
/>
'''
}

def generate_component(framework, component_type, component_name, animation_src, height, width):
    """Generate component code based on parameters."""
    key = f"{framework}_{component_type}"

    if key not in TEMPLATES:
        print(f"Error: Template '{key}' not found")
        sys.exit(1)

    template = TEMPLATES[key]

    code = template.format(
        ComponentName=component_name,
        animationSrc=animation_src,
        height=height,
        width=width
    )

    return code

def interactive_mode():
    """Run interactive mode to gather component parameters."""
    print("Lottie Component Generator")
    print("-" * 40)

    # Framework selection
    print("\nSelect framework:")
    print("1. React")
    print("2. Vue")
    print("3. Svelte")
    framework_choice = input("Enter choice (1-3): ").strip()

    framework_map = {'1': 'react', '2': 'vue', '3': 'svelte'}
    framework = framework_map.get(framework_choice, 'react')

    # Component type
    if framework == 'react':
        print("\nSelect component type:")
        print("1. Basic (just displays animation)")
        print("2. Interactive (with playback controls)")
        type_choice = input("Enter choice (1-2): ").strip()
        component_type = 'interactive' if type_choice == '2' else 'basic'
    else:
        component_type = 'basic'

    # Component details
    component_name = input("\nComponent name (e.g., HeroAnimation): ").strip() or "LottieAnimation"
    animation_src = input("Animation source URL or path: ").strip() or "/animations/animation.lottie"
    height = input("Height in pixels (default 400): ").strip() or "400"
    width = input("Width in pixels (default 400): ").strip() or "400"

    code = generate_component(framework, component_type, component_name, animation_src, height, width)

    # Output
    extensions = {'react': 'jsx', 'vue': 'vue', 'svelte': 'svelte'}
    filename = f"{component_name}.{extensions[framework]}"

    print(f"\nGenerated {filename}:")
    print("-" * 40)
    print(code)

    save = input("\nSave to file? (y/n): ").strip().lower()
    if save == 'y':
        with open(filename, 'w') as f:
            f.write(code)
        print(f"✅ Saved to {filename}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate Lottie component boilerplate")
    parser.add_argument('--framework', choices=['react', 'vue', 'svelte'], help="Framework to use")
    parser.add_argument('--type', choices=['basic', 'interactive'], default='basic', help="Component type")
    parser.add_argument('--name', default='LottieAnimation', help="Component name")
    parser.add_argument('--src', default='/animations/animation.lottie', help="Animation source")
    parser.add_argument('--height', default='400', help="Height in pixels")
    parser.add_argument('--width', default='400', help="Width in pixels")
    parser.add_argument('--output', help="Output file path")

    args = parser.parse_args()

    # Interactive mode if no framework specified
    if not args.framework:
        interactive_mode()
        return

    code = generate_component(
        args.framework,
        args.type,
        args.name,
        args.src,
        args.height,
        args.width
    )

    if args.output:
        with open(args.output, 'w') as f:
            f.write(code)
        print(f"✅ Generated {args.output}")
    else:
        print(code)

if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/lottie-animations/skills/lottie-animations/scripts/optimize_lottie.py =====

```py
#!/usr/bin/env python3
"""
Lottie JSON Optimizer

Optimizes Lottie JSON files by removing whitespace, rounding numbers, and removing unnecessary data.

Usage:
    ./optimize_lottie.py animation.json                 # Output to stdout
    ./optimize_lottie.py animation.json -o optimized.json
"""

import json
import argparse
import sys

def round_number(value, precision=2):
    """Round number to specified precision."""
    if isinstance(value, (int, float)):
        return round(value, precision)
    return value

def optimize_object(obj, precision=2):
    """Recursively optimize object by rounding numbers."""
    if isinstance(obj, dict):
        return {k: optimize_object(v, precision) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [optimize_object(item, precision) for item in obj]
    elif isinstance(obj, float):
        return round(obj, precision)
    return obj

def optimize_lottie(input_path, output_path=None, precision=2):
    """Optimize Lottie JSON file."""
    try:
        # Read input
        with open(input_path, 'r') as f:
            data = json.load(f)

        # Optimize
        optimized = optimize_object(data, precision)

        # Write output
        json_str = json.dumps(optimized, separators=(',', ':'))

        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_str)
            print(f"✅ Optimized: {input_path} → {output_path}")

            # Show size reduction
            import os
            original_size = os.path.getsize(input_path)
            optimized_size = os.path.getsize(output_path)
            reduction = ((original_size - optimized_size) / original_size) * 100

            print(f"   Original: {original_size:,} bytes")
            print(f"   Optimized: {optimized_size:,} bytes")
            print(f"   Reduction: {reduction:.1f}%")
        else:
            print(json_str)

    except FileNotFoundError:
        print(f"Error: File '{input_path}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Optimize Lottie JSON files")
    parser.add_argument('input', help="Input Lottie JSON file")
    parser.add_argument('-o', '--output', help="Output file path")
    parser.add_argument('-p', '--precision', type=int, default=2, help="Number precision (default: 2)")

    args = parser.parse_args()

    optimize_lottie(args.input, args.output, args.precision)

if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/lottie-animations/skills/lottie-animations/assets/starter_lottie/README.md =====

# Lottie Starter Template

Complete React + Vite starter template with Lottie examples.

## Features

- React 18+ with TypeScript support
- Vite for fast development
- DotLottie React integration
- Example animations with controls
- Responsive design
- Production-ready configuration

## Installation

```bash
# Install dependencies
npm install

# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
starter_lottie/
├── package.json
├── vite.config.js
├── index.html
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── App.css
│   └── components/
│       ├── BasicAnimation.jsx
│       └── InteractiveAnimation.jsx
├── public/
│   └── animations/
│       └── example.lottie
└── README.md
```

## Usage Examples

### Basic Animation

```jsx
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

<DotLottieReact
  src="/animations/example.lottie"
  loop
  autoplay
  style={{ height: 400 }}
/>
```

### Interactive Animation

```jsx
const [dotLottie, setDotLottie] = useState(null);

<DotLottieReact
  src="/animations/example.lottie"
  loop
  autoplay={false}
  dotLottieRefCallback={setDotLottie}
/>

<button onClick={() => dotLottie?.play()}>Play</button>
```

## Configuration

### vite.config.js

Optimized for production builds with:
- Code splitting
- Asset optimization
- Gzip compression support

### package.json

Includes essential dependencies:
- `@lottiefiles/dotlottie-react`
- `react` and `react-dom`
- Development tools

## Deployment

Build optimized bundle:

```bash
npm run build
```

Output in `dist/` folder ready for deployment to:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Any static hosting

## License

MIT

