# Design Skills for Gemini, part 4 of 6: 2D, components and design

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
| `pixijs-2d` | Fast, lightweight 2D rendering engine for creating interactive graphics, particle effects, and canvas-based applications using WebGL/WebGPU. Use this skill when building 2D games, particle systems, interactive canvases, sprite animations, or UI overlays on 3D scenes. Triggers on tasks involving PixiJS, 2D rendering, sprite sheets, particle effects, filters, or high-performance canvas graphics. Alternative to Canvas2D with WebGL acceleration for rendering thousands of sprites at 60 FPS. |
| `animated-component-libraries` | Pre-built animated React component collections combining Magic UI (150+ TypeScript/Tailwind/Motion components) and React Bits (90+ minimal-dependency animated components). Use this skill when building landing pages, marketing sites, dashboards, or interactive UIs requiring pre-made animated components instead of hand-crafting animations. Triggers on tasks involving animated UI components, Magic UI, React Bits, shadcn/ui integration, Tailwind CSS components, or component library selection. Alternative to manually implementing animations with Framer Motion or GSAP. |
| `modern-web-design` | Modern web design trends, principles, and implementation patterns for 2024-2025. Use this skill when designing websites, creating interactive experiences, implementing design systems, ensuring accessibility, or building performance-first interfaces. Triggers on tasks involving modern design trends, micro-interactions, scrollytelling, bold minimalism, cursor UX, glassmorphism, accessibility compliance, performance optimization, or design system architecture. References animation skills (GSAP, Framer Motion, React Spring), 3D skills (Three.js, R3F, Babylon.js), and component libraries for implementation guidance. |


# Skill: pixijs-2d


===== FILE: plugins/individual/pixijs-2d/skills/pixijs-2d/SKILL.md =====

---
name: pixijs-2d
description: Fast, lightweight 2D rendering engine for creating interactive graphics, particle effects, and canvas-based applications using WebGL/WebGPU. Use this skill when building 2D games, particle systems, interactive canvases, sprite animations, or UI overlays on 3D scenes. Triggers on tasks involving PixiJS, 2D rendering, sprite sheets, particle effects, filters, or high-performance canvas graphics. Alternative to Canvas2D with WebGL acceleration for rendering thousands of sprites at 60 FPS.
---

# PixiJS 2D Rendering Skill

Fast, lightweight 2D rendering engine for creating interactive graphics, particle effects, and canvas-based applications using WebGL/WebGPU.

---

## When to Use This Skill

Trigger this skill when you encounter:
- "Create 2D particle effects" or "animated particles"
- "2D sprite animation" or "sprite sheet handling"
- "Interactive canvas graphics" or "2D game"
- "UI overlays on 3D scenes" or "HUD layer"
- "Draw shapes programmatically" or "vector graphics API"
- "Optimize rendering performance" or "thousands of sprites"
- "Apply visual filters" or "blur/displacement effects"
- "Lightweight 2D engine" or "alternative to Canvas2D"

**Use PixiJS for**: High-performance 2D rendering (up to 100,000+ sprites), particle systems, interactive UI, 2D games, data visualization with WebGL acceleration.

**Don't use for**: 3D graphics (use Three.js/R3F), simple animations (use Motion/GSAP), basic DOM manipulation.

---

## Core Concepts

### 1. Application & Renderer

The entry point for PixiJS applications:

```javascript
import { Application } from 'pixi.js';

const app = new Application();

await app.init({
  width: 800,
  height: 600,
  backgroundColor: 0x1099bb,
  antialias: true,  // Smooth edges
  resolution: window.devicePixelRatio || 1
});

document.body.appendChild(app.canvas);
```

**Key Properties**:
- `app.stage`: Root container for all display objects
- `app.renderer`: WebGL/WebGPU renderer instance
- `app.ticker`: Update loop for animations
- `app.screen`: Canvas dimensions

---

### 2. Sprites & Textures

Core visual elements loaded from images:

```javascript
import { Assets, Sprite } from 'pixi.js';

// Load texture
const texture = await Assets.load('path/to/image.png');

// Create sprite
const sprite = new Sprite(texture);
sprite.anchor.set(0.5);  // Center pivot
sprite.position.set(400, 300);
sprite.scale.set(2);  // 2x scale
sprite.rotation = Math.PI / 4;  // 45 degrees
sprite.alpha = 0.8;  // 80% opacity
sprite.tint = 0xff0000;  // Red tint

app.stage.addChild(sprite);
```

**Quick Creation**:
```javascript
const sprite = Sprite.from('path/to/image.png');
```

---

### 3. Graphics API

Draw vector shapes programmatically:

```javascript
import { Graphics } from 'pixi.js';

const graphics = new Graphics();

// Rectangle
graphics.rect(50, 50, 100, 100).fill('blue');

// Circle with stroke
graphics.circle(200, 100, 50).fill('red').stroke({ width: 2, color: 'white' });

// Complex path
graphics
  .moveTo(300, 100)
  .lineTo(350, 150)
  .lineTo(250, 150)
  .closePath()
  .fill({ color: 0x00ff00, alpha: 0.5 });

app.stage.addChild(graphics);
```

**SVG Support**:
```javascript
graphics.svg('<svg><path d="M 100 350 q 150 -300 300 0" /></svg>');
```

---

### 4. ParticleContainer

Optimized container for rendering thousands of sprites:

```javascript
import { ParticleContainer, Particle, Texture } from 'pixi.js';

const texture = Texture.from('particle.png');

const container = new ParticleContainer({
  dynamicProperties: {
    position: true,   // Allow position updates
    scale: false,     // Static scale
    rotation: false,  // Static rotation
    color: false      // Static color
  }
});

// Add 10,000 particles
for (let i = 0; i < 10000; i++) {
  const particle = new Particle({
    texture,
    x: Math.random() * 800,
    y: Math.random() * 600
  });

  container.addParticle(particle);
}

app.stage.addChild(container);
```

**Performance**: Up to 10x faster than regular Container for static properties.

---

### 5. Filters

Apply per-pixel effects using WebGL shaders:

```javascript
import { BlurFilter, DisplacementFilter, ColorMatrixFilter } from 'pixi.js';

// Blur
const blurFilter = new BlurFilter({ strength: 8, quality: 4 });
sprite.filters = [blurFilter];

// Multiple filters
sprite.filters = [
  new BlurFilter({ strength: 4 }),
  new ColorMatrixFilter()  // Color transforms
];

// Custom filter area for performance
sprite.filterArea = new Rectangle(0, 0, 200, 100);
```

**Available Filters**:
- `BlurFilter`: Gaussian blur
- `ColorMatrixFilter`: Color transformations (sepia, grayscale, etc.)
- `DisplacementFilter`: Warp/distort pixels
- `AlphaFilter`: Flatten alpha across children
- `NoiseFilter`: Random grain effect
- `FXAAFilter`: Anti-aliasing

---

### 6. Text Rendering

Display text with styling:

```javascript
import { Text, BitmapText, TextStyle } from 'pixi.js';

// Standard Text
const style = new TextStyle({
  fontFamily: 'Arial',
  fontSize: 36,
  fill: '#ffffff',
  stroke: { color: '#000000', width: 4 },
  filters: [new BlurFilter()]  // Bake filter into texture
});

const text = new Text({ text: 'Hello PixiJS!', style });
text.position.set(100, 100);

// BitmapText (faster for dynamic text)
const bitmapText = new BitmapText({
  text: 'Score: 0',
  style: { fontFamily: 'MyBitmapFont', fontSize: 24 }
});
```

**Performance Tip**: Use `BitmapText` for frequently changing text (scores, counters).

---

## Common Patterns

### Pattern 1: Basic Interactive Sprite

```javascript
import { Application, Assets, Sprite } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);

const texture = await Assets.load('bunny.png');
const bunny = new Sprite(texture);

bunny.anchor.set(0.5);
bunny.position.set(400, 300);
bunny.eventMode = 'static';  // Enable interactivity
bunny.cursor = 'pointer';

// Events
bunny.on('pointerdown', () => {
  bunny.scale.set(1.2);
});

bunny.on('pointerup', () => {
  bunny.scale.set(1.0);
});

bunny.on('pointerover', () => {
  bunny.tint = 0xff0000;  // Red on hover
});

bunny.on('pointerout', () => {
  bunny.tint = 0xffffff;  // Reset
});

app.stage.addChild(bunny);

// Animation loop
app.ticker.add((ticker) => {
  bunny.rotation += 0.01 * ticker.deltaTime;
});
```

---

### Pattern 2: Drawing with Graphics

```javascript
import { Graphics, Application } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);

const graphics = new Graphics();

// Rectangle with gradient
graphics.rect(50, 50, 200, 100).fill({
  color: 0x3399ff,
  alpha: 0.8
});

// Circle with stroke
graphics.circle(400, 300, 80)
  .fill('yellow')
  .stroke({ width: 4, color: 'orange' });

// Star shape
graphics.star(600, 300, 5, 50, 0).fill({ color: 0xffdf00, alpha: 0.9 });

// Custom path
graphics
  .moveTo(100, 400)
  .bezierCurveTo(150, 300, 250, 300, 300, 400)
  .stroke({ width: 3, color: 'white' });

// Holes
graphics
  .rect(450, 400, 150, 100).fill('red')
  .beginHole()
  .circle(525, 450, 30)
  .endHole();

app.stage.addChild(graphics);

// Dynamic drawing (animation)
app.ticker.add(() => {
  graphics.clear();

  const time = Date.now() * 0.001;
  const x = 400 + Math.cos(time) * 100;
  const y = 300 + Math.sin(time) * 100;

  graphics.circle(x, y, 20).fill('cyan');
});
```

---

### Pattern 3: Particle System with ParticleContainer

```javascript
import { Application, ParticleContainer, Particle, Texture } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600, backgroundColor: 0x000000 });
document.body.appendChild(app.canvas);

const texture = Texture.from('spark.png');

const particles = new ParticleContainer({
  dynamicProperties: {
    position: true,  // Update positions every frame
    scale: true,     // Fade out by scaling
    rotation: true,  // Rotate particles
    color: false     // Static color
  }
});

const particleData = [];

// Create particles
for (let i = 0; i < 5000; i++) {
  const particle = new Particle({
    texture,
    x: 400,
    y: 300,
    scaleX: 0.5,
    scaleY: 0.5
  });

  particles.addParticle(particle);

  particleData.push({
    particle,
    vx: (Math.random() - 0.5) * 5,
    vy: (Math.random() - 0.5) * 5 - 2,  // Slight upward bias
    life: 1.0
  });
}

app.stage.addChild(particles);

// Update loop
app.ticker.add((ticker) => {
  particleData.forEach(data => {
    // Physics
    data.particle.x += data.vx * ticker.deltaTime;
    data.particle.y += data.vy * ticker.deltaTime;
    data.vy += 0.1 * ticker.deltaTime;  // Gravity

    // Fade out
    data.life -= 0.01 * ticker.deltaTime;
    data.particle.scaleX = data.life * 0.5;
    data.particle.scaleY = data.life * 0.5;

    // Reset particle
    if (data.life <= 0) {
      data.particle.x = 400;
      data.particle.y = 300;
      data.vx = (Math.random() - 0.5) * 5;
      data.vy = (Math.random() - 0.5) * 5 - 2;
      data.life = 1.0;
    }
  });
});
```

---

### Pattern 4: Applying Filters

```javascript
import { Application, Sprite, Assets, BlurFilter, DisplacementFilter } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);

const texture = await Assets.load('photo.jpg');
const photo = new Sprite(texture);
photo.position.set(100, 100);

// Blur filter
const blurFilter = new BlurFilter({ strength: 5, quality: 4 });

// Displacement filter (wavy effect)
const displacementTexture = await Assets.load('displacement.jpg');
const displacementSprite = Sprite.from(displacementTexture);
const displacementFilter = new DisplacementFilter({
  sprite: displacementSprite,
  scale: 50
});

// Apply multiple filters
photo.filters = [blurFilter, displacementFilter];

// Optimize with filterArea
photo.filterArea = new Rectangle(0, 0, photo.width, photo.height);

app.stage.addChild(photo);

// Animate displacement
app.ticker.add((ticker) => {
  displacementSprite.x += 1 * ticker.deltaTime;
  displacementSprite.y += 0.5 * ticker.deltaTime;
});
```

---

### Pattern 5: Custom Filter with Shaders

```javascript
import { Filter, GlProgram } from 'pixi.js';

const vertex = `
  in vec2 aPosition;
  out vec2 vTextureCoord;

  uniform vec4 uInputSize;
  uniform vec4 uOutputFrame;
  uniform vec4 uOutputTexture;

  vec4 filterVertexPosition() {
    vec2 position = aPosition * uOutputFrame.zw + uOutputFrame.xy;
    position.x = position.x * (2.0 / uOutputTexture.x) - 1.0;
    position.y = position.y * (2.0*uOutputTexture.z / uOutputTexture.y) - uOutputTexture.z;
    return vec4(position, 0.0, 1.0);
  }

  vec2 filterTextureCoord() {
    return aPosition * (uOutputFrame.zw * uInputSize.zw);
  }

  void main() {
    gl_Position = filterVertexPosition();
    vTextureCoord = filterTextureCoord();
  }
`;

const fragment = `
  in vec2 vTextureCoord;
  uniform sampler2D uTexture;
  uniform float uTime;

  void main() {
    vec2 uv = vTextureCoord;

    // Wave distortion
    float wave = sin(uv.y * 10.0 + uTime) * 0.05;
    vec4 color = texture(uTexture, vec2(uv.x + wave, uv.y));

    gl_FragColor = color;
  }
`;

const customFilter = new Filter({
  glProgram: new GlProgram({ fragment, vertex }),
  resources: {
    timeUniforms: {
      uTime: { value: 0.0, type: 'f32' }
    }
  }
});

sprite.filters = [customFilter];

// Update uniform
app.ticker.add((ticker) => {
  customFilter.resources.timeUniforms.uniforms.uTime += 0.04 * ticker.deltaTime;
});
```

---

### Pattern 6: Sprite Sheet Animation

```javascript
import { Application, Assets, AnimatedSprite } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);

// Load sprite sheet
await Assets.load('spritesheet.json');

// Create animation from frames
const frames = [];
for (let i = 0; i < 10; i++) {
  frames.push(Texture.from(`frame_${i}.png`));
}

const animation = new AnimatedSprite(frames);
animation.anchor.set(0.5);
animation.position.set(400, 300);
animation.animationSpeed = 0.16;  // ~10 FPS
animation.play();

app.stage.addChild(animation);

// Control playback
animation.stop();
animation.gotoAndPlay(0);
animation.onComplete = () => {
  console.log('Animation completed!');
};
```

---

### Pattern 7: Object Pooling for Performance

```javascript
class SpritePool {
  constructor(texture, initialSize = 100) {
    this.texture = texture;
    this.available = [];
    this.active = [];

    // Pre-create sprites
    for (let i = 0; i < initialSize; i++) {
      this.createSprite();
    }
  }

  createSprite() {
    const sprite = new Sprite(this.texture);
    sprite.visible = false;
    this.available.push(sprite);
    return sprite;
  }

  spawn(x, y) {
    let sprite = this.available.pop();

    if (!sprite) {
      sprite = this.createSprite();
    }

    sprite.position.set(x, y);
    sprite.visible = true;
    this.active.push(sprite);

    return sprite;
  }

  despawn(sprite) {
    sprite.visible = false;
    const index = this.active.indexOf(sprite);

    if (index > -1) {
      this.active.splice(index, 1);
      this.available.push(sprite);
    }
  }

  reset() {
    this.active.forEach(sprite => {
      sprite.visible = false;
      this.available.push(sprite);
    });
    this.active = [];
  }
}

// Usage
const bulletTexture = Texture.from('bullet.png');
const bulletPool = new SpritePool(bulletTexture, 50);

// Spawn bullet
const bullet = bulletPool.spawn(100, 200);
app.stage.addChild(bullet);

// Despawn after 2 seconds
setTimeout(() => {
  bulletPool.despawn(bullet);
}, 2000);
```

---

## Integration Patterns

### React Integration

```jsx
import { useEffect, useRef } from 'react';
import { Application } from 'pixi.js';

function PixiCanvas() {
  const canvasRef = useRef(null);
  const appRef = useRef(null);

  useEffect(() => {
    const init = async () => {
      const app = new Application();

      await app.init({
        width: 800,
        height: 600,
        backgroundColor: 0x1099bb
      });

      canvasRef.current.appendChild(app.canvas);
      appRef.current = app;

      // Setup scene
      // ... add sprites, graphics, etc.
    };

    init();

    return () => {
      if (appRef.current) {
        appRef.current.destroy(true, { children: true });
      }
    };
  }, []);

  return <div ref={canvasRef} />;
}
```

---

### Three.js Overlay (2D UI on 3D)

```javascript
import * as THREE from 'three';
import { Application, Sprite, Text } from 'pixi.js';

// Three.js scene
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight);
const renderer = new THREE.WebGLRenderer();
document.body.appendChild(renderer.domElement);

// PixiJS overlay
const pixiApp = new Application();
await pixiApp.init({
  width: window.innerWidth,
  height: window.innerHeight,
  backgroundAlpha: 0  // Transparent background
});

pixiApp.canvas.style.position = 'absolute';
pixiApp.canvas.style.top = '0';
pixiApp.canvas.style.left = '0';
pixiApp.canvas.style.pointerEvents = 'none';  // Click through
document.body.appendChild(pixiApp.canvas);

// Add UI elements
const scoreText = new Text({ text: 'Score: 0', style: { fontSize: 24, fill: 'white' } });
scoreText.position.set(20, 20);
pixiApp.stage.addChild(scoreText);

// Render loop
function animate() {
  requestAnimationFrame(animate);

  renderer.render(scene, camera);  // 3D scene
  pixiApp.renderer.render(pixiApp.stage);  // 2D overlay
}

animate();
```

---

## Performance Best Practices

### 1. Use ParticleContainer for Large Sprite Counts

```javascript
// DON'T: Regular Container (slow for 1000+ sprites)
const container = new Container();
for (let i = 0; i < 10000; i++) {
  container.addChild(new Sprite(texture));
}

// DO: ParticleContainer (10x faster)
const particles = new ParticleContainer({
  dynamicProperties: { position: true }
});
for (let i = 0; i < 10000; i++) {
  particles.addParticle(new Particle({ texture }));
}
```

---

### 2. Optimize Filter Usage

```javascript
// Set filterArea to avoid runtime measurement
sprite.filterArea = new Rectangle(0, 0, 200, 100);

// Release filters when not needed
sprite.filters = null;

// Bake filters into Text at creation
const style = new TextStyle({
  filters: [new BlurFilter()]  // Applied once at texture creation
});
```

---

### 3. Manage Texture Memory

```javascript
// Destroy textures when done
texture.destroy();

// Batch destruction with delays to prevent frame drops
textures.forEach((tex, i) => {
  setTimeout(() => tex.destroy(), Math.random() * 100);
});
```

---

### 4. Enable Culling for Off-Screen Objects

```javascript
sprite.cullable = true;  // Skip rendering if outside viewport

// Use CullerPlugin
import { CullerPlugin } from 'pixi.js';
```

---

### 5. Cache Static Graphics as Bitmaps

```javascript
// Convert complex graphics to texture for faster rendering
const complexShape = new Graphics();
// ... draw many shapes

complexShape.cacheAsBitmap = true;  // Renders to texture once
```

---

### 6. Optimize Renderer Settings

```javascript
const app = new Application();
await app.init({
  antialias: false,  // Disable on mobile for performance
  resolution: 1,     // Lower resolution on low-end devices
  autoDensity: true
});
```

---

### 7. Use BitmapText for Dynamic Text

```javascript
// DON'T: Standard Text (expensive updates)
const text = new Text({ text: `Score: ${score}` });
app.ticker.add(() => {
  text.text = `Score: ${++score}`;  // Re-renders texture each frame
});

// DO: BitmapText (much faster)
const bitmapText = new BitmapText({ text: `Score: ${score}` });
app.ticker.add(() => {
  bitmapText.text = `Score: ${++score}`;
});
```

---

## Common Pitfalls

### Pitfall 1: Not Destroying Objects

**Problem**: Memory leaks from unreleased GPU resources.

**Solution**:
```javascript
// Always destroy sprites and textures
sprite.destroy({ children: true, texture: true, baseTexture: true });

// Destroy filters
sprite.filters = null;

// Destroy graphics
graphics.destroy();
```

---

### Pitfall 2: Updating Static ParticleContainer Properties

**Problem**: Changing `scale` when `dynamicProperties.scale = false` has no effect.

**Solution**:
```javascript
const container = new ParticleContainer({
  dynamicProperties: {
    position: true,
    scale: true,  // Enable if you need to update
    rotation: true,
    color: true
  }
});

// If properties are static but you change them, call update:
container.update();
```

---

### Pitfall 3: Excessive Filter Usage

**Problem**: Filters are expensive; too many cause performance issues.

**Solution**:
```javascript
// Limit filter usage
sprite.filters = [blurFilter];  // 1-2 filters max

// Use filterArea to constrain processing
sprite.filterArea = new Rectangle(0, 0, sprite.width, sprite.height);

// Bake filters into textures when possible
const filteredTexture = renderer.filters.generateFilteredTexture({
  texture,
  filters: [blurFilter]
});
```

---

### Pitfall 4: Frequent Text Updates

**Problem**: Updating Text re-generates texture every time.

**Solution**:
```javascript
// Use BitmapText for frequently changing text
const bitmapText = new BitmapText({ text: 'Score: 0' });

// Reduce resolution for less memory
text.resolution = 1;  // Lower than device pixel ratio
```

---

### Pitfall 5: Graphics Clear() Without Redraw

**Problem**: Calling `clear()` removes all geometry but doesn't automatically redraw.

**Solution**:
```javascript
graphics.clear();  // Remove all shapes

// Redraw new shapes
graphics.rect(0, 0, 100, 100).fill('blue');
```

---

### Pitfall 6: Not Using Asset Loading

**Problem**: Creating sprites from URLs causes async issues.

**Solution**:
```javascript
// DON'T:
const sprite = Sprite.from('image.png');  // May load asynchronously

// DO:
const texture = await Assets.load('image.png');
const sprite = new Sprite(texture);
```

---

## Resources

- **Official Site**: https://pixijs.com
- **API Documentation**: https://pixijs.download/release/docs/
- **Examples**: https://pixijs.io/examples/
- **GitHub**: https://github.com/pixijs/pixijs
- **Filters Library**: @pixi/filter-* packages
- **Community**: https://github.com/pixijs/pixijs/discussions

---

## Related Skills

- **threejs-webgl**: For 3D graphics; PixiJS can provide 2D UI overlays
- **gsap-scrolltrigger**: For animating PixiJS properties with scroll
- **motion-framer**: For React component animations alongside PixiJS canvas
- **react-three-fiber**: Similar React integration patterns

---

## Summary

PixiJS excels at high-performance 2D rendering with WebGL acceleration. Key strengths:

1. **Performance**: Render 100,000+ sprites at 60 FPS
2. **ParticleContainer**: 10x faster for static properties
3. **Filters**: WebGL-powered visual effects
4. **Graphics API**: Intuitive vector drawing
5. **Asset Management**: Robust texture and sprite sheet handling

Use for particle systems, 2D games, data visualizations, and interactive canvas applications where performance is critical.



===== FILE: plugins/individual/pixijs-2d/skills/pixijs-2d/references/api_reference.md =====

# PixiJS API Reference

Complete API reference for PixiJS v8+ core classes and methods.

---

## Table of Contents

1. [Application](#application)
2. [Sprite](#sprite)
3. [Texture](#texture)
4. [Graphics](#graphics)
5. [Container](#container)
6. [ParticleContainer](#particlecontainer)
7. [Filters](#filters)
8. [Text](#text)
9. [Assets](#assets)
10. [Renderer](#renderer)
11. [DisplayObject](#displayobject)
12. [Events](#events)

---

## Application

Core application class that manages the renderer, stage, and update loop.

### Constructor

```typescript
new Application()
```

### Methods

#### `init(options)`

Initialize the application with configuration options.

```typescript
await app.init({
  width: 800,
  height: 600,
  backgroundColor: 0x1099bb,
  backgroundAlpha: 1,
  antialias: true,
  resolution: window.devicePixelRatio || 1,
  autoDensity: true,
  powerPreference: 'high-performance',
  hello: true  // Show PixiJS banner in console
});
```

**Options**:
- `width: number` - Canvas width (default: 800)
- `height: number` - Canvas height (default: 600)
- `backgroundColor: number` - Background color (default: 0x000000)
- `backgroundAlpha: number` - Background alpha 0-1 (default: 1)
- `antialias: boolean` - Enable antialiasing (default: false)
- `resolution: number` - Device pixel ratio (default: 1)
- `autoDensity: boolean` - Adjust CSS pixel size automatically
- `powerPreference: string` - 'high-performance' | 'low-power' | 'default'
- `hello: boolean` - Show PixiJS banner (default: false)

#### `destroy(removeView, stageOptions)`

Destroy the application and release resources.

```typescript
app.destroy(true, { children: true, texture: true });
```

**Parameters**:
- `removeView: boolean` - Remove canvas from DOM (default: false)
- `stageOptions: object` - Options for stage destruction
  - `children: boolean` - Destroy all children
  - `texture: boolean` - Destroy textures
  - `baseTexture: boolean` - Destroy base textures

#### `resizeCanvas()`

Resize canvas to fill window.

```typescript
window.addEventListener('resize', () => {
  app.resizeCanvas();
});
```

### Properties

```typescript
app.stage: Container          // Root display object container
app.renderer: Renderer        // WebGL/WebGPU renderer instance
app.ticker: Ticker            // Update loop manager
app.canvas: HTMLCanvasElement // Canvas element
app.screen: Rectangle         // Screen dimensions
app.view: HTMLCanvasElement   // Alias for canvas (deprecated)
```

### Plugins

```typescript
// Ticker Plugin - manages update loop
app.ticker.add((ticker) => {
  // Update logic
  sprite.rotation += 0.01 * ticker.deltaTime;
});

app.ticker.stop();
app.ticker.start();
app.ticker.speed = 0.5;  // Half speed

// Resize Plugin
app.resizeTo = window;  // Auto-resize to window

// Culler Plugin - automatic viewport culling
app.cullable = true;
```

**API References**:
- TickerPlugin: https://pixijs.download/release/docs/app.TickerPlugin.html
- ResizePlugin: https://pixijs.download/release/docs/app.ResizePlugin.html
- CullerPlugin: https://pixijs.download/release/docs/app.CullerPlugin.html

---

## Sprite

Visual element that displays a texture.

### Constructor

```typescript
new Sprite(texture: Texture)
Sprite.from(source: string | Texture)  // Convenience method
```

### Properties

```typescript
sprite.texture: Texture       // The texture to display
sprite.anchor: ObservablePoint // Pivot point (0-1, default: 0,0)
sprite.tint: number           // Color tint (0xRRGGBB)
sprite.blendMode: BLEND_MODES // How sprite blends with background

// Transform properties (inherited from DisplayObject)
sprite.position: ObservablePoint  // x, y position
sprite.scale: ObservablePoint     // x, y scale
sprite.rotation: number           // Rotation in radians
sprite.pivot: ObservablePoint     // Rotation pivot point
sprite.skew: ObservablePoint      // x, y skew

// Visibility
sprite.alpha: number              // Opacity (0-1)
sprite.visible: boolean           // Show/hide
sprite.renderable: boolean        // Should render

// Interaction
sprite.eventMode: string          // 'none' | 'passive' | 'static' | 'dynamic'
sprite.cursor: string             // CSS cursor
sprite.hitArea: Rectangle | Circle | Polygon  // Custom hit area

// Performance
sprite.cullable: boolean          // Enable viewport culling
sprite.cacheAsBitmap: boolean     // Convert to texture for performance
```

### Methods

```typescript
// Anchor
sprite.anchor.set(x, y)
sprite.anchor.set(0.5)  // Center (shorthand)

// Position
sprite.position.set(x, y)
sprite.setTransform(x, y, scaleX, scaleY, rotation, skewX, skewY, pivotX, pivotY)

// Bounds
sprite.getBounds()
sprite.getLocalBounds()

// Destroy
sprite.destroy({ children: true, texture: false, baseTexture: false })
```

### Example

```typescript
import { Sprite, Texture } from 'pixi.js';

const texture = Texture.from('bunny.png');
const sprite = new Sprite(texture);

sprite.anchor.set(0.5);
sprite.position.set(400, 300);
sprite.scale.set(2);
sprite.rotation = Math.PI / 4;
sprite.tint = 0xff0000;
sprite.alpha = 0.8;

app.stage.addChild(sprite);
```

---

## Texture

Image data that can be rendered by Sprites and Graphics.

### Static Methods

```typescript
Texture.from(source: string | HTMLImageElement | HTMLCanvasElement)
Texture.fromURL(url: string, options?: object)
Texture.fromBuffer(buffer: Uint8Array, width: number, height: number)
```

### Properties

```typescript
texture.width: number           // Texture width
texture.height: number          // Texture height
texture.baseTexture: BaseTexture  // Underlying GPU texture
texture.frame: Rectangle        // Region of baseTexture to use
texture.source: TextureSource   // Source data
```

### Methods

```typescript
texture.destroy(destroyBase?: boolean)
texture.update()                // Update from source
texture.clone()                 // Create copy
```

### Example

```typescript
import { Texture, Assets } from 'pixi.js';

// Load texture
const texture = await Assets.load('image.png');

// From URL
const tex = Texture.from('https://example.com/image.png');

// From canvas
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
// ... draw on canvas
const canvasTex = Texture.from(canvas);

// Destroy
texture.destroy(true);  // Also destroy baseTexture
```

**API Reference**: https://pixijs.download/release/docs/rendering.Texture.html

---

## Graphics

API for drawing vector shapes programmatically.

### Constructor

```typescript
new Graphics()
new Graphics(context: GraphicsContext)  // Share geometry
```

### Shape Methods

All shape methods return `this` for chaining.

```typescript
graphics.rect(x, y, width, height)
graphics.circle(x, y, radius)
graphics.ellipse(x, y, radiusX, radiusY)
graphics.roundRect(x, y, width, height, radius)
graphics.poly(points: number[] | Point[])
graphics.star(x, y, points, radius, innerRadius?, rotation?)
```

### Path Methods

```typescript
graphics.moveTo(x, y)
graphics.lineTo(x, y)
graphics.bezierCurveTo(cpX, cpY, cpX2, cpY2, toX, toY)
graphics.quadraticCurveTo(cpX, cpY, toX, toY)
graphics.arcTo(x1, y1, x2, y2, radius)
graphics.arc(x, y, radius, startAngle, endAngle, anticlockwise?)
graphics.closePath()
```

### Fill & Stroke

```typescript
// Fill
graphics.fill(color: number | string)
graphics.fill({ color, alpha })
graphics.fill(texture: Texture)

// Stroke
graphics.stroke({ width, color, alpha, alignment, cap, join })

// Options
{
  width: number,          // Line width
  color: number | string, // Line color
  alpha: number,          // Line opacity (0-1)
  alignment: number,      // 0=inner, 0.5=middle, 1=outer
  cap: string,            // 'butt' | 'round' | 'square'
  join: string            // 'miter' | 'round' | 'bevel'
}
```

### Holes

```typescript
graphics.rect(0, 0, 100, 100).fill('red')
  .beginHole()
  .circle(50, 50, 20)
  .endHole();
```

### SVG Support

```typescript
graphics.svg('<svg><path d="M 100 350 q 150 -300 300 0" /></svg>');
```

### Other Methods

```typescript
graphics.clear()                    // Remove all shapes
graphics.clone()                    // Create copy
graphics.destroy(options)           // Destroy and release memory

// Context sharing
const context = new GraphicsContext().circle(50, 50, 30).fill('red');
const g1 = new Graphics(context);
const g2 = new Graphics(context);  // Shares same geometry
```

### Properties

```typescript
graphics.context: GraphicsContext   // Drawing instructions
graphics.pixelLine: boolean         // Force 1px line width regardless of scale
graphics.fillStyle: FillStyle       // Current fill style
graphics.lineStyle: StrokeStyle     // Current line style
```

### Example

```typescript
import { Graphics } from 'pixi.js';

const graphics = new Graphics();

// Rectangle with gradient
graphics.rect(50, 50, 200, 100).fill({ color: 0x3399ff, alpha: 0.8 });

// Circle with stroke
graphics.circle(400, 300, 80)
  .fill('yellow')
  .stroke({ width: 4, color: 'orange' });

// Star
graphics.star(600, 300, 5, 50).fill(0xffdf00);

// Custom path
graphics
  .moveTo(100, 400)
  .bezierCurveTo(150, 300, 250, 300, 300, 400)
  .stroke({ width: 3, color: 'white' });

// Hole
graphics.rect(450, 400, 150, 100).fill('red')
  .beginHole()
  .circle(525, 450, 30)
  .endHole();

app.stage.addChild(graphics);
```

**API References**:
- Graphics: https://pixijs.download/release/docs/scene.Graphics.html
- GraphicsContext: https://pixijs.download/release/docs/scene.GraphicsContext.html
- FillStyle: https://pixijs.download/release/docs/scene.FillStyle.html
- StrokeStyle: https://pixijs.download/release/docs/scene.StrokeStyle.html

---

## Container

Display object that can contain children (like a group).

### Constructor

```typescript
new Container()
```

### Children Management

```typescript
container.addChild(child: DisplayObject)
container.addChildAt(child: DisplayObject, index: number)
container.removeChild(child: DisplayObject)
container.removeChildAt(index: number)
container.removeChildren(beginIndex?, endIndex?)
container.getChildAt(index: number)
container.getChildIndex(child: DisplayObject)
container.setChildIndex(child: DisplayObject, index: number)
container.swapChildren(child1: DisplayObject, child2: DisplayObject)
```

### Properties

```typescript
container.children: DisplayObject[]  // Array of children
container.width: number               // Combined width of children
container.height: number              // Combined height of children
container.sortableChildren: boolean   // Enable z-index sorting
container.interactiveChildren: boolean // Enable child interaction
```

### Filters

```typescript
container.filters: Filter[]          // Array of filters
container.filterArea: Rectangle      // Filter bounding box
```

### Iteration

```typescript
for (const child of container.children) {
  // Process child
}

container.children.forEach(child => {
  // Process child
});
```

### Example

```typescript
import { Container, Sprite } from 'pixi.js';

const container = new Container();
container.position.set(100, 100);

// Add children
const sprite1 = Sprite.from('image1.png');
const sprite2 = Sprite.from('image2.png');
sprite2.x = 50;

container.addChild(sprite1, sprite2);

// Z-index sorting
container.sortableChildren = true;
sprite1.zIndex = 2;
sprite2.zIndex = 1;  // Renders behind sprite1

app.stage.addChild(container);
```

---

## ParticleContainer

Optimized container for rendering thousands of sprites with limited transform capabilities.

### Constructor

```typescript
new ParticleContainer(options?: ParticleContainerOptions)
```

**Options**:
```typescript
{
  maxSize: number,          // Max particles (default: 1500)
  dynamicProperties: {
    position: boolean,      // Allow position updates (default: true)
    scale: boolean,         // Allow scale updates (default: false)
    rotation: boolean,      // Allow rotation updates (default: false)
    color: boolean          // Allow tint/alpha updates (default: false)
  }
}
```

### Methods

```typescript
container.addParticle(particle: Particle)
container.removeParticle(particle: Particle)
container.update()  // Call if changing static properties
container.destroy()
```

### Properties

```typescript
container.maxSize: number                // Maximum particle count
container.dynamicProperties: object      // Which properties can change
container.particleChildren: Particle[]   // Array of particles
```

### Particle Interface

```typescript
interface IParticle {
  x: number;
  y: number;
  scaleX: number;
  scaleY: number;
  anchorX: number;
  anchorY: number;
  rotation: number;
  color: number;    // Tint
  texture: Texture;
}

// Create particle
const particle = new Particle({
  texture: Texture.from('spark.png'),
  x: 100,
  y: 200,
  scaleX: 0.5,
  scaleY: 0.5,
  rotation: 0,
  tint: 0xffffff,
  alpha: 1.0
});
```

### Example

```typescript
import { ParticleContainer, Particle, Texture } from 'pixi.js';

const texture = Texture.from('particle.png');

const particles = new ParticleContainer({
  maxSize: 10000,
  dynamicProperties: {
    position: true,   // Update positions
    scale: true,      // Update scale
    rotation: false,  // Static rotation
    color: false      // Static color
  }
});

for (let i = 0; i < 10000; i++) {
  const particle = new Particle({
    texture,
    x: Math.random() * 800,
    y: Math.random() * 600
  });

  particles.addParticle(particle);
}

app.stage.addChild(particles);

// Update loop
app.ticker.add(() => {
  particles.particleChildren.forEach(p => {
    p.y += 1;  // Move down
    if (p.y > 600) p.y = 0;
  });
});
```

---

## Filters

WebGL shader-based effects applied to display objects.

### Built-in Filters

#### BlurFilter

```typescript
import { BlurFilter } from 'pixi.js';

const blur = new BlurFilter({
  strength: 8,      // Blur amount (default: 8)
  quality: 4,       // Iterations (default: 4)
  kernelSize: 5     // Sample size: 5, 7, 9, 11, 13, 15
});

sprite.filters = [blur];
```

#### ColorMatrixFilter

```typescript
import { ColorMatrixFilter } from 'pixi.js';

const colorMatrix = new ColorMatrixFilter();

// Presets
colorMatrix.greyscale(0.5);     // 0-1
colorMatrix.sepia();
colorMatrix.blackAndWhite();
colorMatrix.contrast(1.5);      // >1 increases
colorMatrix.saturate(2);        // -1 to 1
colorMatrix.brightness(1.2);    // >1 brightens
colorMatrix.hue(45);            // Rotate hue (degrees)
colorMatrix.negative();
colorMatrix.kodachrome();
colorMatrix.technicolor();
colorMatrix.polaroid();
colorMatrix.vintage();

sprite.filters = [colorMatrix];
```

#### DisplacementFilter

```typescript
import { DisplacementFilter, Sprite } from 'pixi.js';

const displacementSprite = Sprite.from('displacement.jpg');
const displacementFilter = new DisplacementFilter({
  sprite: displacementSprite,
  scale: 50  // Displacement amount
});

sprite.filters = [displacementFilter];

// Animate displacement
app.ticker.add(() => {
  displacementSprite.x += 1;
});
```

#### AlphaFilter

```typescript
import { AlphaFilter } from 'pixi.js';

const alphaFilter = new AlphaFilter(0.5);  // 0-1
container.filters = [alphaFilter];  // Flattens alpha across children
```

#### NoiseFilter

```typescript
import { NoiseFilter } from 'pixi.js';

const noise = new NoiseFilter({
  noise: 0.5,  // Amount (0-1)
  seed: Math.random()
});

sprite.filters = [noise];
```

#### FXAAFilter

```typescript
import { FXAAFilter } from 'pixi.js';

const fxaa = new FXAAFilter();
sprite.filters = [fxaa];  // Anti-aliasing
```

### Custom Filters

```typescript
import { Filter, GlProgram } from 'pixi.js';

const vertex = `...`;  // Vertex shader
const fragment = `...`;  // Fragment shader

const customFilter = new Filter({
  glProgram: new GlProgram({ vertex, fragment }),
  resources: {
    customUniforms: {
      uTime: { value: 0.0, type: 'f32' },
      uColor: { value: [1.0, 0.0, 0.0], type: 'vec3<f32>' }
    }
  }
});

sprite.filters = [customFilter];

// Update uniforms
app.ticker.add((ticker) => {
  customFilter.resources.customUniforms.uniforms.uTime += 0.01 * ticker.deltaTime;
});
```

### Filter Optimization

```typescript
// Specify filterArea to avoid runtime measurement
sprite.filterArea = new Rectangle(0, 0, sprite.width, sprite.height);

// Release filters
sprite.filters = null;

// Generate filtered texture (apply once)
const filteredTexture = renderer.filters.generateFilteredTexture({
  texture: originalTexture,
  filters: [blurFilter]
});
```

**API References**:
- BlurFilter: @pixi/filter-blur
- ColorMatrixFilter: @pixi/filter-color-matrix
- DisplacementFilter: @pixi/filter-displacement
- AlphaFilter: @pixi/filter-alpha
- NoiseFilter: @pixi/filter-noise
- FXAAFilter: @pixi/filter-fxaa

---

## Text

Render styled text as a texture.

### Text

Standard text rendering:

```typescript
import { Text, TextStyle } from 'pixi.js';

const style = new TextStyle({
  fontFamily: 'Arial',
  fontSize: 36,
  fontStyle: 'italic',
  fontWeight: 'bold',
  fill: '#ffffff',
  stroke: { color: '#000000', width: 4 },
  dropShadow: {
    alpha: 0.5,
    angle: Math.PI / 6,
    blur: 4,
    color: '#000000',
    distance: 6
  },
  wordWrap: true,
  wordWrapWidth: 400,
  align: 'center',
  filters: [new BlurFilter()]  // Bake filter into texture
});

const text = new Text({
  text: 'Hello PixiJS!',
  style
});

text.position.set(100, 100);
app.stage.addChild(text);

// Update text
text.text = 'New text';

// Adjust resolution
text.resolution = 2;  // Higher = sharper but more memory
```

### BitmapText

High-performance text for dynamic content:

```typescript
import { BitmapText } from 'pixi.js';

// Requires bitmap font asset
const bitmapText = new BitmapText({
  text: 'Score: 0',
  style: {
    fontFamily: 'MyBitmapFont',
    fontSize: 24,
    tint: 0xff0000
  }
});

app.stage.addChild(bitmapText);

// Update frequently (very fast)
app.ticker.add(() => {
  bitmapText.text = `Score: ${++score}`;
});
```

### TextStyle Options

```typescript
interface TextStyleOptions {
  // Font
  fontFamily: string | string[];
  fontSize: number | string;
  fontStyle: 'normal' | 'italic' | 'oblique';
  fontWeight: 'normal' | 'bold' | '100-900';

  // Fill
  fill: number | string | string[] | number[];  // Gradient support
  fillGradientStops: number[];

  // Stroke
  stroke: { color: number | string, width: number, alpha?: number };

  // Shadow
  dropShadow: {
    alpha: number,
    angle: number,
    blur: number,
    color: number | string,
    distance: number
  };

  // Layout
  align: 'left' | 'center' | 'right' | 'justify';
  wordWrap: boolean;
  wordWrapWidth: number;
  breakWords: boolean;
  lineHeight: number;
  letterSpacing: number;
  leading: number;

  // Other
  padding: number;
  trim: boolean;
  whiteSpace: 'normal' | 'pre' | 'pre-line';
}
```

---

## Assets

Asset loading and management system.

### Loading Assets

```typescript
import { Assets } from 'pixi.js';

// Load single asset
const texture = await Assets.load('image.png');
const spritesheet = await Assets.load('spritesheet.json');

// Load multiple assets
const assets = await Assets.load([
  'image1.png',
  'image2.png',
  'sound.mp3'
]);

// Load with aliases
await Assets.add({ alias: 'hero', src: 'hero.png' });
const heroTexture = await Assets.load('hero');

// Load bundle
Assets.addBundle('game', {
  player: 'player.png',
  enemy: 'enemy.png',
  background: 'bg.jpg'
});
const bundle = await Assets.loadBundle('game');

// Access loaded assets
const playerTexture = Assets.get('player');
```

### Progress Tracking

```typescript
Assets.load('large-file.png', (progress) => {
  console.log(`Loading: ${Math.round(progress * 100)}%`);
});

// Or with promises
const promise = Assets.load(['file1.png', 'file2.png']);
promise.progress = (progress) => {
  console.log(`Progress: ${progress * 100}%`);
};
await promise;
```

### Background Loading

```typescript
// Load in background (non-blocking)
Assets.backgroundLoad(['asset1.png', 'asset2.png']);

// Check if loaded
if (Assets.cache.has('asset1.png')) {
  const texture = Assets.get('asset1.png');
}
```

### Unloading Assets

```typescript
// Unload single asset
await Assets.unload('image.png');

// Unload bundle
await Assets.unloadBundle('game');

// Clear cache
Assets.reset();
```

---

## Renderer

Low-level rendering system (WebGL/WebGPU).

### Properties

```typescript
renderer.type: string              // 'webgl' | 'webgpu'
renderer.width: number
renderer.height: number
renderer.resolution: number
renderer.backgroundColor: number
renderer.backgroundAlpha: number
```

### Methods

```typescript
// Manual rendering
renderer.render(container);

// Resize
renderer.resize(width, height);

// Clear
renderer.clear();

// Generate texture from display object
const texture = renderer.generateTexture(displayObject, {
  resolution: 1,
  frame: new Rectangle(0, 0, 100, 100)
});

// Destroy
renderer.destroy();
```

---

## DisplayObject

Base class for all renderable objects (Sprite, Graphics, Container, etc.).

### Transform Properties

```typescript
displayObject.position: ObservablePoint     // x, y
displayObject.scale: ObservablePoint        // x, y scale
displayObject.rotation: number              // Radians
displayObject.pivot: ObservablePoint        // Rotation pivot
displayObject.skew: ObservablePoint         // x, y skew
displayObject.angle: number                 // Degrees (converts to rotation)
```

### Visibility

```typescript
displayObject.alpha: number                 // 0-1 opacity
displayObject.visible: boolean              // Show/hide
displayObject.renderable: boolean           // Render flag
displayObject.cullable: boolean             // Viewport culling
displayObject.mask: Graphics | Sprite       // Masking
```

### Hierarchy

```typescript
displayObject.parent: Container
displayObject.children: DisplayObject[]  // If Container
displayObject.zIndex: number             // Render order (if sortableChildren enabled)
displayObject.removeFromParent()
displayObject.destroy(options)
```

### Bounds

```typescript
displayObject.getBounds()           // Global bounds
displayObject.getLocalBounds()      // Local bounds
displayObject.width: number         // Bounding width
displayObject.height: number        // Bounding height
```

### Interaction

```typescript
displayObject.eventMode: string     // 'none' | 'passive' | 'static' | 'dynamic'
displayObject.cursor: string        // CSS cursor
displayObject.hitArea: Shape        // Custom hit detection area
displayObject.interactive: boolean  // Enable events (deprecated, use eventMode)
```

---

## Events

Interactive event system.

### Event Modes

```typescript
sprite.eventMode = 'static';   // Enable interaction
sprite.eventMode = 'dynamic';  // Enable + propagate to children
sprite.eventMode = 'passive';  // Receive events but don't block
sprite.eventMode = 'none';     // No interaction (default)
```

### Mouse Events

```typescript
sprite.on('pointerdown', (event) => {
  console.log('Clicked at:', event.global.x, event.global.y);
});

sprite.on('pointerup', handler);
sprite.on('pointermove', handler);
sprite.on('pointerover', handler);   // Mouse enter
sprite.on('pointerout', handler);    // Mouse leave
sprite.on('pointerupoutside', handler);  // Released outside

// Once
sprite.once('pointerdown', handler);

// Remove
sprite.off('pointerdown', handler);
sprite.removeAllListeners();
```

### Touch Events

```typescript
sprite.on('touchstart', handler);
sprite.on('touchend', handler);
sprite.on('touchmove', handler);
sprite.on('tap', handler);
```

### Event Object

```typescript
interface FederatedPointerEvent {
  global: Point;         // Global coordinates
  client: Point;         // Client coordinates
  screen: Point;         // Screen coordinates
  movement: Point;       // Delta movement
  page: Point;           // Page coordinates
  button: number;        // Mouse button (0=left, 1=middle, 2=right)
  buttons: number;       // Bitmask of pressed buttons
  target: DisplayObject; // Event target
  currentTarget: DisplayObject;
  type: string;          // Event type
  preventDefault(): void;
  stopPropagation(): void;
}
```

### Custom Cursor

```typescript
sprite.cursor = 'pointer';
sprite.cursor = 'grab';
sprite.cursor = 'help';
```

### Hit Area

```typescript
import { Rectangle, Circle, Polygon } from 'pixi.js';

// Rectangle hit area
sprite.hitArea = new Rectangle(0, 0, 100, 100);

// Circle hit area
sprite.hitArea = new Circle(50, 50, 30);

// Polygon hit area
sprite.hitArea = new Polygon([0,0, 100,0, 100,100, 0,100]);
```

---

## Utility Classes

### Rectangle

```typescript
const rect = new Rectangle(x, y, width, height);
rect.contains(x, y);
rect.intersects(otherRect);
```

### Circle

```typescript
const circle = new Circle(x, y, radius);
circle.contains(x, y);
```

### Point

```typescript
const point = new Point(x, y);
point.set(x, y);
point.clone();
point.equals(otherPoint);
```

### ObservablePoint

```typescript
const observable = new ObservablePoint(callback, scope);
observable.set(x, y);
observable.x = 100;  // Triggers callback
```

---

## Performance APIs

### CacheAsBitmap

```typescript
// Convert to texture for faster rendering
displayObject.cacheAsBitmap = true;

// Disable when updating frequently
displayObject.cacheAsBitmap = false;
```

### Ticker

```typescript
import { Ticker } from 'pixi.js';

const ticker = Ticker.shared;

ticker.add((delta) => {
  // Update logic
  // delta = time since last frame
});

ticker.speed = 0.5;  // Half speed
ticker.maxFPS = 30;  // Cap at 30 FPS
ticker.minFPS = 10;  // Min for deltaTime calculation

ticker.stop();
ticker.start();
```

---

## Constants

### Blend Modes

```typescript
import { BLEND_MODES } from 'pixi.js';

sprite.blendMode = BLEND_MODES.NORMAL;
sprite.blendMode = BLEND_MODES.ADD;
sprite.blendMode = BLEND_MODES.MULTIPLY;
sprite.blendMode = BLEND_MODES.SCREEN;
sprite.blendMode = BLEND_MODES.OVERLAY;
sprite.blendMode = BLEND_MODES.DARKEN;
sprite.blendMode = BLEND_MODES.LIGHTEN;
sprite.blendMode = BLEND_MODES.COLOR_DODGE;
sprite.blendMode = BLEND_MODES.COLOR_BURN;
sprite.blendMode = BLEND_MODES.HARD_LIGHT;
sprite.blendMode = BLEND_MODES.SOFT_LIGHT;
sprite.blendMode = BLEND_MODES.DIFFERENCE;
sprite.blendMode = BLEND_MODES.EXCLUSION;
sprite.blendMode = BLEND_MODES.HUE;
sprite.blendMode = BLEND_MODES.SATURATION;
sprite.blendMode = BLEND_MODES.COLOR;
sprite.blendMode = BLEND_MODES.LUMINOSITY;
```

### Scale Modes

```typescript
import { SCALE_MODES } from 'pixi.js';

texture.baseTexture.scaleMode = SCALE_MODES.LINEAR;   // Smooth (default)
texture.baseTexture.scaleMode = SCALE_MODES.NEAREST;  // Pixelated
```

---

## TypeScript Support

PixiJS is written in TypeScript and provides full type definitions.

```typescript
import { Application, Sprite, Texture, Container } from 'pixi.js';

const app: Application = new Application();
const sprite: Sprite = new Sprite(Texture.WHITE);
const container: Container = new Container();
```

---

## Official API Documentation

- **Main Docs**: https://pixijs.download/release/docs/
- **Examples**: https://pixijs.io/examples/
- **GitHub**: https://github.com/pixijs/pixijs

---

This API reference covers PixiJS v8+ core functionality. For advanced features, plugins, and detailed shader programming, consult the official documentation.



===== FILE: plugins/individual/pixijs-2d/skills/pixijs-2d/references/filters_effects.md =====

# PixiJS Filters & Visual Effects Guide

Comprehensive guide to using and creating visual effects with PixiJS filters and shaders.

---

## Table of Contents

1. [Filter Basics](#filter-basics)
2. [Built-in Filters](#built-in-filters)
3. [Custom Filters](#custom-filters)
4. [Shader Programming](#shader-programming)
5. [Effect Combinations](#effect-combinations)
6. [Performance Tips](#performance-tips)

---

## Filter Basics

### Applying Filters

Filters are WebGL/WebGPU shader programs applied to display objects after rendering.

```javascript
import { BlurFilter, Sprite } from 'pixi.js';

const sprite = Sprite.from('image.png');

// Single filter
sprite.filters = [new BlurFilter()];

// Multiple filters (applied in order)
sprite.filters = [
  new BlurFilter({ strength: 4 }),
  new ColorMatrixFilter()
];

// Remove filters
sprite.filters = null;
```

### Filter Area Optimization

```javascript
import { Rectangle } from 'pixi.js';

// Specify filter bounds for performance
sprite.filterArea = new Rectangle(0, 0, sprite.width, sprite.height);

// PixiJS won't need to measure bounds at runtime
```

### Filter on Containers

```javascript
import { Container } from 'pixi.js';

const container = new Container();
container.addChild(sprite1, sprite2, sprite3);

// Filter applied to entire container
container.filters = [new BlurFilter()];
```

---

## Built-in Filters

### BlurFilter

Gaussian blur effect for depth of field, motion blur, or soft focus.

```javascript
import { BlurFilter } from 'pixi.js';

const blur = new BlurFilter({
  strength: 8,      // Blur radius (default: 8)
  quality: 4,       // Number of passes (1-5, default: 4)
  kernelSize: 5     // Sample size: 5, 7, 9, 11, 13, 15 (default: 5)
});

sprite.filters = [blur];

// Adjust blur dynamically
app.ticker.add(() => {
  blur.blur = 5 + Math.sin(Date.now() * 0.001) * 5;  // Pulsing blur
});
```

**Use Cases**:
- Depth of field effects
- Focus/unfocus transitions
- Motion blur
- Background blur (foreground sharp)

**Performance**: Higher quality and kernelSize = slower. Use lower values for real-time effects.

---

### ColorMatrixFilter

Transform colors using matrix multiplication. Includes preset effects.

```javascript
import { ColorMatrixFilter } from 'pixi.js';

const colorMatrix = new ColorMatrixFilter();

// Grayscale
colorMatrix.greyscale(0.5);  // 0 = color, 1 = full grayscale

// Sepia tone
colorMatrix.sepia();

// Black and white
colorMatrix.blackAndWhite();

// Adjust contrast
colorMatrix.contrast(1.5);  // >1 = more contrast

// Adjust saturation
colorMatrix.saturate(0.5);  // <1 = desaturate, >1 = supersaturate

// Adjust brightness
colorMatrix.brightness(1.2);  // >1 = brighter

// Hue rotation
colorMatrix.hue(45);  // Rotate hue in degrees

// Negative (invert)
colorMatrix.negative();

// Vintage film effects
colorMatrix.kodachrome();
colorMatrix.technicolor();
colorMatrix.polaroid();
colorMatrix.vintage();

sprite.filters = [colorMatrix];
```

**Chaining Effects**:
```javascript
colorMatrix.greyscale(0.3).contrast(1.2).brightness(1.1);
```

**Custom Color Matrix**:
```javascript
// 5x4 color matrix [R, G, B, A, offset]
const matrix = [
  1, 0, 0, 0, 0,  // Red
  0, 1, 0, 0, 0,  // Green
  0, 0, 1, 0, 0,  // Blue
  0, 0, 0, 1, 0   // Alpha
];

colorMatrix.matrix = matrix;
```

**Use Cases**:
- Photo filters (Instagram-style)
- Color grading
- Night vision effect
- Damage/flash effects

---

### DisplacementFilter

Warp/distort pixels based on a displacement map texture.

```javascript
import { DisplacementFilter, Sprite } from 'pixi.js';

// Create displacement sprite (usually perlin noise or cloud texture)
const displacementSprite = Sprite.from('displacement.jpg');
displacementSprite.texture.baseTexture.wrapMode = WRAP_MODES.REPEAT;

const displacementFilter = new DisplacementFilter({
  sprite: displacementSprite,
  scale: 50  // Displacement amount
});

sprite.filters = [displacementFilter];
app.stage.addChild(displacementSprite);

// Animate displacement
app.ticker.add(() => {
  displacementSprite.x += 1;
  displacementSprite.y += 0.5;
});
```

**Parameters**:
- `sprite`: Displacement map (red channel = X offset, green channel = Y offset)
- `scale`: Displacement intensity (default: 20)

**Use Cases**:
- Water ripple effects
- Heat distortion
- Portal effects
- Liquid/jelly animations
- Flag waving

**Creating Displacement Maps**:
```javascript
// Generate noise texture
const canvas = document.createElement('canvas');
canvas.width = 256;
canvas.height = 256;
const ctx = canvas.getContext('2d');

// Draw perlin noise or clouds
// ... (use simplex-noise library or draw manually)

const displacementTexture = Texture.from(canvas);
const displacementSprite = new Sprite(displacementTexture);
```

---

### AlphaFilter

Flatten alpha across all children in a container.

```javascript
import { AlphaFilter, Container } from 'pixi.js';

const container = new Container();
container.addChild(sprite1, sprite2, sprite3);

const alphaFilter = new AlphaFilter(0.5);  // 50% opacity
container.filters = [alphaFilter];

// Without filter: each sprite has individual alpha
// With filter: entire container rendered at 50% alpha
```

**Use Cases**:
- Fade entire UI panel
- Composite transparency
- Layer blending

---

### NoiseFilter

Add random grain/noise for film grain or static effects.

```javascript
import { NoiseFilter } from 'pixi.js';

const noise = new NoiseFilter({
  noise: 0.5,  // Amount (0-1, default: 0.5)
  seed: Math.random()  // Random seed
});

sprite.filters = [noise];

// Animated noise
app.ticker.add(() => {
  noise.seed = Math.random();
});
```

**Use Cases**:
- Film grain
- Old TV static
- Analog distortion
- Glitch effects

---

### FXAAFilter

Fast approximate anti-aliasing for smooth edges.

```javascript
import { FXAAFilter } from 'pixi.js';

const fxaa = new FXAAFilter();
sprite.filters = [fxaa];
```

**Use Cases**:
- Smooth jagged edges
- Improve visual quality on low-res displays
- Reduce aliasing artifacts

---

## Custom Filters

### Creating a Custom Filter

Custom filters use GLSL shaders for GPU-accelerated effects.

```javascript
import { Filter, GlProgram } from 'pixi.js';

const vertex = `
  in vec2 aPosition;
  out vec2 vTextureCoord;

  uniform vec4 uInputSize;
  uniform vec4 uOutputFrame;
  uniform vec4 uOutputTexture;

  vec4 filterVertexPosition() {
    vec2 position = aPosition * uOutputFrame.zw + uOutputFrame.xy;
    position.x = position.x * (2.0 / uOutputTexture.x) - 1.0;
    position.y = position.y * (2.0*uOutputTexture.z / uOutputTexture.y) - uOutputTexture.z;
    return vec4(position, 0.0, 1.0);
  }

  vec2 filterTextureCoord() {
    return aPosition * (uOutputFrame.zw * uInputSize.zw);
  }

  void main() {
    gl_Position = filterVertexPosition();
    vTextureCoord = filterTextureCoord();
  }
`;

const fragment = `
  in vec2 vTextureCoord;
  uniform sampler2D uTexture;
  uniform float uTime;

  void main() {
    vec2 uv = vTextureCoord;

    // Wave distortion
    float wave = sin(uv.y * 10.0 + uTime) * 0.05;
    vec4 color = texture(uTexture, vec2(uv.x + wave, uv.y));

    gl_FragColor = color;
  }
`;

const waveFilter = new Filter({
  glProgram: new GlProgram({ vertex, fragment }),
  resources: {
    timeUniforms: {
      uTime: { value: 0.0, type: 'f32' }
    }
  }
});

sprite.filters = [waveFilter];

// Update uniform
app.ticker.add((ticker) => {
  waveFilter.resources.timeUniforms.uniforms.uTime += 0.04 * ticker.deltaTime;
});
```

---

### Example: Pixelate Filter

```javascript
const pixelateVertex = `
  in vec2 aPosition;
  out vec2 vTextureCoord;

  uniform vec4 uInputSize;
  uniform vec4 uOutputFrame;
  uniform vec4 uOutputTexture;

  vec4 filterVertexPosition() {
    vec2 position = aPosition * uOutputFrame.zw + uOutputFrame.xy;
    position.x = position.x * (2.0 / uOutputTexture.x) - 1.0;
    position.y = position.y * (2.0*uOutputTexture.z / uOutputTexture.y) - uOutputTexture.z;
    return vec4(position, 0.0, 1.0);
  }

  vec2 filterTextureCoord() {
    return aPosition * (uOutputFrame.zw * uInputSize.zw);
  }

  void main() {
    gl_Position = filterVertexPosition();
    vTextureCoord = filterTextureCoord();
  }
`;

const pixelateFragment = `
  in vec2 vTextureCoord;
  uniform sampler2D uTexture;
  uniform vec2 uSize;
  uniform float uPixelSize;

  void main() {
    vec2 coord = vTextureCoord * uSize;
    vec2 pixelCoord = floor(coord / uPixelSize) * uPixelSize;
    vec2 pixelUV = pixelCoord / uSize;

    gl_FragColor = texture(uTexture, pixelUV);
  }
`;

class PixelateFilter extends Filter {
  constructor(pixelSize = 10) {
    super({
      glProgram: new GlProgram({
        vertex: pixelateVertex,
        fragment: pixelateFragment
      }),
      resources: {
        pixelateUniforms: {
          uSize: { value: new Float32Array([800, 600]), type: 'vec2<f32>' },
          uPixelSize: { value: pixelSize, type: 'f32' }
        }
      }
    });
  }

  get pixelSize() {
    return this.resources.pixelateUniforms.uniforms.uPixelSize;
  }

  set pixelSize(value) {
    this.resources.pixelateUniforms.uniforms.uPixelSize = value;
  }
}

// Usage
const pixelate = new PixelateFilter(5);
sprite.filters = [pixelate];

// Animate
app.ticker.add(() => {
  pixelate.pixelSize = 5 + Math.sin(Date.now() * 0.001) * 4;
});
```

---

### Example: Chromatic Aberration

```javascript
const chromaticFragment = `
  in vec2 vTextureCoord;
  uniform sampler2D uTexture;
  uniform float uAmount;

  void main() {
    vec2 uv = vTextureCoord;

    // Offset RGB channels
    float r = texture(uTexture, uv + vec2(uAmount, 0.0)).r;
    float g = texture(uTexture, uv).g;
    float b = texture(uTexture, uv - vec2(uAmount, 0.0)).b;

    gl_FragColor = vec4(r, g, b, 1.0);
  }
`;

class ChromaticAberrationFilter extends Filter {
  constructor(amount = 0.005) {
    super({
      glProgram: new GlProgram({
        vertex: defaultVertex,  // Use default vertex shader
        fragment: chromaticFragment
      }),
      resources: {
        chromaticUniforms: {
          uAmount: { value: amount, type: 'f32' }
        }
      }
    });
  }

  get amount() {
    return this.resources.chromaticUniforms.uniforms.uAmount;
  }

  set amount(value) {
    this.resources.chromaticUniforms.uniforms.uAmount = value;
  }
}

// Usage
const chromatic = new ChromaticAberrationFilter(0.01);
sprite.filters = [chromatic];
```

---

### Example: Vignette Filter

```javascript
const vignetteFragment = `
  in vec2 vTextureCoord;
  uniform sampler2D uTexture;
  uniform float uIntensity;
  uniform float uSoftness;

  void main() {
    vec4 color = texture(uTexture, vTextureCoord);
    vec2 uv = vTextureCoord - 0.5;
    float dist = length(uv);
    float vignette = smoothstep(uIntensity, uIntensity - uSoftness, dist);

    gl_FragColor = vec4(color.rgb * vignette, color.a);
  }
`;

class VignetteFilter extends Filter {
  constructor(intensity = 0.5, softness = 0.3) {
    super({
      glProgram: new GlProgram({
        vertex: defaultVertex,
        fragment: vignetteFragment
      }),
      resources: {
        vignetteUniforms: {
          uIntensity: { value: intensity, type: 'f32' },
          uSoftness: { value: softness, type: 'f32' }
        }
      }
    });
  }

  get intensity() {
    return this.resources.vignetteUniforms.uniforms.uIntensity;
  }

  set intensity(value) {
    this.resources.vignetteUniforms.uniforms.uIntensity = value;
  }

  get softness() {
    return this.resources.vignetteUniforms.uniforms.uSoftness;
  }

  set softness(value) {
    this.resources.vignetteUniforms.uniforms.uSoftness = value;
  }
}
```

---

## Shader Programming

### GLSL Basics

**Data Types**:
```glsl
float x = 1.0;
vec2 position = vec2(0.5, 0.5);
vec3 color = vec3(1.0, 0.0, 0.0);  // RGB
vec4 rgba = vec4(1.0, 0.0, 0.0, 1.0);  // RGBA

sampler2D texture;  // Texture sampler
```

**Built-in Functions**:
```glsl
// Math
sin(x), cos(x), tan(x)
abs(x), sign(x)
floor(x), ceil(x), fract(x)
min(a, b), max(a, b), clamp(x, min, max)
mix(a, b, t)  // Linear interpolation
smoothstep(edge0, edge1, x)  // Smooth interpolation

// Vector
length(v)  // Vector length
distance(a, b)  // Distance between vectors
dot(a, b)  // Dot product
normalize(v)  // Unit vector

// Texture sampling
texture(sampler, uv)  // Sample texture at UV coordinates
```

**Vertex Shader Template**:
```glsl
in vec2 aPosition;
out vec2 vTextureCoord;

uniform vec4 uInputSize;
uniform vec4 uOutputFrame;
uniform vec4 uOutputTexture;

void main() {
  gl_Position = filterVertexPosition();
  vTextureCoord = filterTextureCoord();
}
```

**Fragment Shader Template**:
```glsl
in vec2 vTextureCoord;
uniform sampler2D uTexture;

void main() {
  vec4 color = texture(uTexture, vTextureCoord);

  // Modify color
  color.rgb *= 0.5;  // Darken

  gl_FragColor = color;
}
```

---

### Uniforms

Pass data from JavaScript to shaders.

```javascript
const filter = new Filter({
  glProgram: new GlProgram({ vertex, fragment }),
  resources: {
    customUniforms: {
      uTime: { value: 0.0, type: 'f32' },
      uColor: { value: [1.0, 0.0, 0.0], type: 'vec3<f32>' },
      uPosition: { value: new Float32Array([0.5, 0.5]), type: 'vec2<f32>' },
      uTexture2: { value: secondTexture, type: 'sampler2D' }
    }
  }
});

// Access uniforms
filter.resources.customUniforms.uniforms.uTime = 5.0;
filter.resources.customUniforms.uniforms.uColor = [0.0, 1.0, 0.0];
```

**In Shader**:
```glsl
uniform float uTime;
uniform vec3 uColor;
uniform vec2 uPosition;
uniform sampler2D uTexture2;

void main() {
  // Use uniforms
  float wave = sin(vTextureCoord.y * 10.0 + uTime);
  vec4 color = texture(uTexture, vTextureCoord) * vec4(uColor, 1.0);
  gl_FragColor = color;
}
```

---

### Multi-Pass Filters

Apply multiple shader passes for complex effects.

```javascript
class MultiPassFilter extends Filter {
  constructor() {
    // First pass: Blur horizontal
    const pass1 = new Filter({
      glProgram: new GlProgram({ vertex: defaultVertex, fragment: blurHorizontalFragment })
    });

    // Second pass: Blur vertical
    const pass2 = new Filter({
      glProgram: new GlProgram({ vertex: defaultVertex, fragment: blurVerticalFragment })
    });

    // Combine passes
    super({
      glProgram: new GlProgram({ vertex: defaultVertex, fragment: combineFragment }),
      resources: {
        pass1Texture: { value: null, type: 'sampler2D' },
        pass2Texture: { value: null, type: 'sampler2D' }
      }
    });
  }
}
```

---

## Effect Combinations

### Glow Effect

Blur + Additive Blend

```javascript
import { BlurFilter, BLEND_MODES } from 'pixi.js';

// Original sprite
const sprite = Sprite.from('star.png');

// Glow sprite (blurred copy)
const glowSprite = new Sprite(sprite.texture);
glowSprite.filters = [new BlurFilter({ strength: 15 })];
glowSprite.blendMode = BLEND_MODES.ADD;
glowSprite.alpha = 0.8;

const container = new Container();
container.addChild(glowSprite, sprite);  // Glow behind

app.stage.addChild(container);
```

---

### Outline Effect

Multiple displacement passes

```javascript
const outlineFragment = `
  in vec2 vTextureCoord;
  uniform sampler2D uTexture;
  uniform float uThickness;
  uniform vec3 uColor;

  void main() {
    vec4 color = texture(uTexture, vTextureCoord);
    float alpha = color.a;

    // Sample neighboring pixels
    alpha += texture(uTexture, vTextureCoord + vec2(uThickness, 0.0)).a;
    alpha += texture(uTexture, vTextureCoord - vec2(uThickness, 0.0)).a;
    alpha += texture(uTexture, vTextureCoord + vec2(0.0, uThickness)).a;
    alpha += texture(uTexture, vTextureCoord - vec2(0.0, uThickness)).a;

    // Create outline
    float outline = step(0.1, alpha) * (1.0 - color.a);

    vec3 finalColor = mix(color.rgb, uColor, outline);
    float finalAlpha = max(color.a, outline);

    gl_FragColor = vec4(finalColor, finalAlpha);
  }
`;

class OutlineFilter extends Filter {
  constructor(thickness = 0.01, color = [1, 1, 1]) {
    super({
      glProgram: new GlProgram({ vertex: defaultVertex, fragment: outlineFragment }),
      resources: {
        outlineUniforms: {
          uThickness: { value: thickness, type: 'f32' },
          uColor: { value: color, type: 'vec3<f32>' }
        }
      }
    });
  }
}
```

---

### CRT Monitor Effect

Scanlines + chromatic aberration + curve

```javascript
const crtFragment = `
  in vec2 vTextureCoord;
  uniform sampler2D uTexture;
  uniform float uTime;

  void main() {
    vec2 uv = vTextureCoord;

    // Curve screen
    uv = uv * 2.0 - 1.0;
    uv *= 1.0 + 0.1 * dot(uv, uv);
    uv = (uv + 1.0) * 0.5;

    // Chromatic aberration
    float r = texture(uTexture, uv + vec2(0.002, 0.0)).r;
    float g = texture(uTexture, uv).g;
    float b = texture(uTexture, uv - vec2(0.002, 0.0)).b;

    // Scanlines
    float scanline = sin(uv.y * 800.0) * 0.1 + 0.9;

    // Flicker
    float flicker = sin(uTime * 50.0) * 0.02 + 0.98;

    vec3 color = vec3(r, g, b) * scanline * flicker;

    gl_FragColor = vec4(color, 1.0);
  }
`;
```

---

### Film Grain + Vignette

```javascript
sprite.filters = [
  new NoiseFilter({ noise: 0.2 }),
  new VignetteFilter(0.5, 0.3),
  new ColorMatrixFilter().sepia()
];
```

---

## Performance Tips

### 1. Minimize Filter Count

```javascript
// ❌ BAD: Too many filters
sprite.filters = [blur1, blur2, colorMatrix, noise, vignette];

// ✅ GOOD: Combine into single custom filter
sprite.filters = [combinedFilter];
```

---

### 2. Set Filter Area

```javascript
sprite.filters = [blurFilter];
sprite.filterArea = new Rectangle(0, 0, sprite.width, sprite.height);
```

---

### 3. Bake Static Filters

```javascript
// Apply filter once, generate texture
const filteredTexture = renderer.filters.generateFilteredTexture({
  texture: originalTexture,
  filters: [blurFilter, colorMatrix]
});

const sprite = new Sprite(filteredTexture);
// No runtime filter cost
```

---

### 4. Use Lower Quality

```javascript
const blur = new BlurFilter({
  strength: 8,
  quality: 2,  // Lower = faster (1-5)
  kernelSize: 5  // Smaller = faster
});
```

---

### 5. Toggle Filters Based on Performance

```javascript
let filtersEnabled = true;

app.ticker.add(() => {
  const fps = Math.round(1000 / app.ticker.deltaMS);

  if (fps < 30 && filtersEnabled) {
    sprite.filters = null;  // Disable filters
    filtersEnabled = false;
  } else if (fps > 55 && !filtersEnabled) {
    sprite.filters = [blurFilter];  // Re-enable
    filtersEnabled = true;
  }
});
```

---

## Filter Examples Library

### Glass/Frosted Effect
```javascript
sprite.filters = [
  new BlurFilter({ strength: 10 }),
  new ColorMatrixFilter().brightness(1.2)
];
sprite.alpha = 0.8;
```

### Night Vision
```javascript
const nightVision = new ColorMatrixFilter();
nightVision.greyscale(1);
nightVision.contrast(1.5);
nightVision.brightness(1.5);
sprite.filters = [nightVision];
sprite.tint = 0x00ff00;  // Green tint
```

### X-Ray
```javascript
const xray = new ColorMatrixFilter();
xray.negative();
xray.contrast(2);
sprite.filters = [xray];
```

### Underwater
```javascript
sprite.filters = [
  new DisplacementFilter({ sprite: waveSprite, scale: 20 }),
  new ColorMatrixFilter().saturate(0.7)
];
sprite.tint = 0x88ccff;
```

---

This guide provides comprehensive coverage of PixiJS filters, from built-in options to custom shader programming for advanced visual effects.



===== FILE: plugins/individual/pixijs-2d/skills/pixijs-2d/references/performance_guide.md =====

# PixiJS Performance Optimization Guide

Comprehensive guide to optimizing PixiJS applications for maximum performance and smooth 60 FPS rendering.

---

## Table of Contents

1. [Performance Profiling](#performance-profiling)
2. [Rendering Optimization](#rendering-optimization)
3. [Texture Management](#texture-management)
4. [Container Optimization](#container-optimization)
5. [Filter Performance](#filter-performance)
6. [Text Rendering](#text-rendering)
7. [Memory Management](#memory-management)
8. [Mobile Optimization](#mobile-optimization)
9. [Advanced Techniques](#advanced-techniques)

---

## Performance Profiling

### Built-in Stats

```javascript
import { Application } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600 });

// Access stats
app.ticker.add(() => {
  const stats = app.renderer.stats;

  console.log('FPS:', Math.round(1000 / app.ticker.deltaMS));
  console.log('Draw calls:', stats.drawCalls);
  console.log('Texture bind count:', stats.textureCount);
  console.log('Shader bind count:', stats.shaderCount);
});
```

### Custom Performance Monitor

```javascript
class PerformanceMonitor {
  constructor(app) {
    this.app = app;
    this.frameCount = 0;
    this.lastTime = performance.now();
    this.fps = 60;
    this.drawCalls = 0;

    this.createDisplay();
    this.app.ticker.add(this.update.bind(this));
  }

  createDisplay() {
    this.container = document.createElement('div');
    this.container.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      background: rgba(0,0,0,0.8);
      color: #0f0;
      padding: 10px;
      font-family: monospace;
      font-size: 12px;
      z-index: 10000;
    `;
    document.body.appendChild(this.container);
  }

  update() {
    this.frameCount++;
    const now = performance.now();

    if (now - this.lastTime >= 1000) {
      this.fps = Math.round(this.frameCount * 1000 / (now - this.lastTime));
      this.frameCount = 0;
      this.lastTime = now;

      const stats = this.app.renderer.stats;
      this.drawCalls = stats.drawCalls.total;

      this.render();
    }
  }

  render() {
    const color = this.fps >= 55 ? '#0f0' : this.fps >= 30 ? '#ff0' : '#f00';
    this.container.style.color = color;

    this.container.innerHTML = `
      FPS: ${this.fps}<br>
      Draw Calls: ${this.drawCalls}<br>
      Sprites: ${this.countSprites()}<br>
      Memory: ${this.getMemoryUsage()}
    `;
  }

  countSprites() {
    let count = 0;
    const traverse = (container) => {
      if (container.children) {
        container.children.forEach(child => {
          count++;
          traverse(child);
        });
      }
    };
    traverse(this.app.stage);
    return count;
  }

  getMemoryUsage() {
    if (performance.memory) {
      const mb = (performance.memory.usedJSHeapSize / 1048576).toFixed(2);
      return `${mb} MB`;
    }
    return 'N/A';
  }
}

// Usage
const monitor = new PerformanceMonitor(app);
```

---

## Rendering Optimization

### 1. Use ParticleContainer for Large Sprite Counts

**Problem**: Rendering 1,000+ sprites with regular Container is slow.

**Solution**: Use ParticleContainer with static properties.

```javascript
import { ParticleContainer, Particle, Texture } from 'pixi.js';

// ❌ BAD: Regular container (slow)
const container = new Container();
for (let i = 0; i < 10000; i++) {
  const sprite = new Sprite(texture);
  sprite.x = Math.random() * 800;
  sprite.y = Math.random() * 600;
  container.addChild(sprite);
}

// ✅ GOOD: ParticleContainer (10x faster)
const particles = new ParticleContainer({
  maxSize: 10000,
  dynamicProperties: {
    position: true,   // Only if you need to update positions
    scale: false,     // Static scale
    rotation: false,  // Static rotation
    color: false      // Static color
  }
});

for (let i = 0; i < 10000; i++) {
  const particle = new Particle({
    texture,
    x: Math.random() * 800,
    y: Math.random() * 600
  });
  particles.addParticle(particle);
}

app.stage.addChild(particles);
```

**Performance Gain**: Up to 10x faster rendering for static properties.

---

### 2. Minimize Draw Calls

**Problem**: Each texture/shader switch triggers a new draw call.

**Solution**: Batch sprites with the same texture and blend mode.

```javascript
// ❌ BAD: Different textures interspersed
const sprites = [];
for (let i = 0; i < 100; i++) {
  const tex = i % 2 === 0 ? texture1 : texture2;
  sprites.push(new Sprite(tex));
}

// ✅ GOOD: Group by texture
const group1 = new Container();
const group2 = new Container();

for (let i = 0; i < 50; i++) {
  group1.addChild(new Sprite(texture1));
  group2.addChild(new Sprite(texture2));
}

app.stage.addChild(group1, group2);
```

**Tip**: Use sprite atlases (texture packing) to combine multiple images into one texture.

---

### 3. Enable Culling for Off-Screen Objects

**Problem**: Rendering objects outside viewport wastes GPU cycles.

**Solution**: Enable viewport culling.

```javascript
import { Application } from 'pixi.js';

const app = new Application();
await app.init({
  width: 800,
  height: 600,
  cullable: true  // Enable automatic culling
});

// Or per-object
sprite.cullable = true;

// Manual culling
app.ticker.add(() => {
  const bounds = app.screen;

  sprites.forEach(sprite => {
    const spriteBounds = sprite.getBounds();

    // Check if sprite is in viewport
    sprite.renderable = (
      spriteBounds.x < bounds.width &&
      spriteBounds.x + spriteBounds.width > 0 &&
      spriteBounds.y < bounds.height &&
      spriteBounds.y + spriteBounds.height > 0
    );
  });
});
```

**CullerPlugin**:
```javascript
// Automatic viewport culling plugin
import { CullerPlugin } from 'pixi.js';

// Enabled by default in Application
app.cullable = true;
```

**Performance Gain**: Up to 50% for scenes with many off-screen objects.

---

### 4. Cache Static Graphics as Bitmaps

**Problem**: Complex vector graphics re-render every frame.

**Solution**: Convert to texture using `cacheAsBitmap`.

```javascript
import { Graphics } from 'pixi.js';

const complexShape = new Graphics();

// Draw many shapes
for (let i = 0; i < 100; i++) {
  complexShape.circle(
    Math.random() * 200,
    Math.random() * 200,
    Math.random() * 10
  ).fill(Math.random() * 0xffffff);
}

// ✅ Cache as bitmap for static graphics
complexShape.cacheAsBitmap = true;

// ❌ Don't use for frequently changing graphics
// complexShape.cacheAsBitmap = false;  // If updating often
```

**When to Use**:
- ✅ Static UI elements
- ✅ Backgrounds
- ✅ Complex shapes that don't change
- ❌ Animated graphics
- ❌ Frequently updated elements

---

### 5. Reduce Resolution on Low-End Devices

**Problem**: High-resolution rendering on mobile drains battery and causes lag.

**Solution**: Adjust resolution based on device capabilities.

```javascript
const isMobile = /Mobi|Android/i.test(navigator.userAgent);
const resolution = isMobile ? 1 : window.devicePixelRatio || 1;

const app = new Application();
await app.init({
  width: 800,
  height: 600,
  resolution,
  autoDensity: true
});

// Dynamic resolution scaling
function adjustResolution() {
  const fps = Math.round(1000 / app.ticker.deltaMS);

  if (fps < 30 && app.renderer.resolution > 1) {
    app.renderer.resolution *= 0.9;
  } else if (fps > 55 && app.renderer.resolution < window.devicePixelRatio) {
    app.renderer.resolution = Math.min(app.renderer.resolution * 1.1, window.devicePixelRatio);
  }
}

app.ticker.add(adjustResolution);
```

---

## Texture Management

### 1. Destroy Unused Textures

**Problem**: Textures consume GPU memory even when not displayed.

**Solution**: Explicitly destroy textures when done.

```javascript
import { Texture } from 'pixi.js';

const texture = Texture.from('image.png');
const sprite = new Sprite(texture);

// When done
sprite.destroy({ texture: true, baseTexture: true });

// Or destroy texture directly
texture.destroy(true);  // true = also destroy baseTexture
```

**Batch Destruction with Delay**:
```javascript
// Prevent frame drops by staggering destruction
const textures = [tex1, tex2, tex3, tex4];

textures.forEach((tex, index) => {
  setTimeout(() => {
    tex.destroy(true);
  }, index * 50 + Math.random() * 50);
});
```

---

### 2. Use Texture Atlases (Sprite Sheets)

**Problem**: Loading many individual images causes numerous HTTP requests and draw calls.

**Solution**: Pack images into sprite sheets.

```javascript
import { Assets, Sprite } from 'pixi.js';

// Load sprite sheet
await Assets.load('spritesheet.json');

// Access individual frames
const texture1 = Texture.from('frame1.png');
const texture2 = Texture.from('frame2.png');

const sprite1 = new Sprite(texture1);
const sprite2 = new Sprite(texture2);

// All batched in single draw call
app.stage.addChild(sprite1, sprite2);
```

**Tools for Creating Sprite Sheets**:
- TexturePacker: https://www.codeandweb.com/texturepacker
- ShoeBox: https://renderhjs.net/shoebox/
- Free Texture Packer: https://free-tex-packer.com/

---

### 3. Optimize Texture Sizes

**Problem**: Large textures consume excessive memory.

**Solution**: Use appropriate sizes and compression.

```javascript
// ❌ BAD: 4096x4096 texture (64MB RGBA)
const hugeTexture = Texture.from('huge-image-4k.png');

// ✅ GOOD: 1024x1024 texture (4MB RGBA)
const optimizedTexture = Texture.from('optimized-image-1k.png');

// Power-of-2 sizes for best performance
// Good sizes: 256, 512, 1024, 2048
// Avoid odd sizes: 300, 500, 1500

// Use NEAREST for pixel art
texture.baseTexture.scaleMode = SCALE_MODES.NEAREST;

// Use LINEAR for photos
texture.baseTexture.scaleMode = SCALE_MODES.LINEAR;
```

---

### 4. Lazy Load Assets

**Problem**: Loading all assets upfront delays game start.

**Solution**: Load assets on-demand.

```javascript
import { Assets } from 'pixi.js';

// Preload critical assets
const criticalAssets = await Assets.load([
  'ui/background.png',
  'ui/logo.png'
]);

// Background load game assets
Assets.backgroundLoad([
  'characters/hero.png',
  'characters/enemy.png',
  'levels/level1.jpg'
]);

// Check if asset is loaded
if (Assets.cache.has('characters/hero.png')) {
  const heroTexture = Assets.get('characters/hero.png');
  const hero = new Sprite(heroTexture);
}

// Load on-demand
async function showLevel(levelNumber) {
  const levelTexture = await Assets.load(`levels/level${levelNumber}.jpg`);
  // Use texture
}
```

---

## Container Optimization

### 1. Disable Unnecessary Features

```javascript
import { Container } from 'pixi.js';

const container = new Container();

// ❌ Don't enable unless needed
container.sortableChildren = false;  // Z-index sorting (expensive)
container.interactiveChildren = false;  // Child interaction (expensive)

// ✅ Enable only when required
if (needsSorting) {
  container.sortableChildren = true;
}
```

---

### 2. Use Object Pooling

**Problem**: Creating/destroying objects causes garbage collection pauses.

**Solution**: Reuse objects via pooling.

```javascript
class SpritePool {
  constructor(texture, initialSize = 100) {
    this.texture = texture;
    this.available = [];
    this.active = [];

    for (let i = 0; i < initialSize; i++) {
      this.createSprite();
    }
  }

  createSprite() {
    const sprite = new Sprite(this.texture);
    sprite.visible = false;
    this.available.push(sprite);
    return sprite;
  }

  spawn(x, y) {
    let sprite = this.available.pop();

    if (!sprite) {
      sprite = this.createSprite();
    }

    sprite.position.set(x, y);
    sprite.visible = true;
    this.active.push(sprite);

    return sprite;
  }

  despawn(sprite) {
    sprite.visible = false;
    const index = this.active.indexOf(sprite);

    if (index > -1) {
      this.active.splice(index, 1);
      this.available.push(sprite);
    }
  }

  reset() {
    this.active.forEach(sprite => {
      sprite.visible = false;
      this.available.push(sprite);
    });
    this.active = [];
  }
}

// Usage
const bulletPool = new SpritePool(bulletTexture, 50);

// Spawn
const bullet = bulletPool.spawn(100, 200);
app.stage.addChild(bullet);

// Despawn
bulletPool.despawn(bullet);
```

**Performance Gain**: Eliminates GC pauses, smoother frame times.

---

### 3. Flatten Hierarchy

**Problem**: Deep nesting requires traversing many containers.

**Solution**: Keep hierarchy shallow when possible.

```javascript
// ❌ BAD: Deep nesting
const root = new Container();
const level1 = new Container();
const level2 = new Container();
const level3 = new Container();

root.addChild(level1);
level1.addChild(level2);
level2.addChild(level3);
level3.addChild(sprite);

// ✅ GOOD: Flat structure
const root = new Container();
root.addChild(sprite);

// Use position offsets instead of nested containers
sprite.x = parentX + childX;
sprite.y = parentY + childY;
```

---

## Filter Performance

### 1. Limit Filter Usage

**Problem**: Filters are expensive WebGL operations.

**Solution**: Use sparingly, optimize where possible.

```javascript
import { BlurFilter } from 'pixi.js';

// ❌ BAD: Filter on every sprite
sprites.forEach(sprite => {
  sprite.filters = [new BlurFilter()];
});

// ✅ GOOD: Filter on container
const container = new Container();
sprites.forEach(sprite => container.addChild(sprite));
container.filters = [new BlurFilter()];

// ✅ BETTER: Bake filter into texture
const filteredTexture = renderer.filters.generateFilteredTexture({
  texture: originalTexture,
  filters: [new BlurFilter({ strength: 5 })]
});

const sprite = new Sprite(filteredTexture);
```

---

### 2. Specify Filter Area

**Problem**: PixiJS measures filter bounds at runtime (expensive).

**Solution**: Manually specify `filterArea`.

```javascript
import { BlurFilter, Rectangle } from 'pixi.js';

const sprite = new Sprite(texture);
sprite.filters = [new BlurFilter()];

// ✅ Specify filter area for performance
sprite.filterArea = new Rectangle(0, 0, sprite.width, sprite.height);

// Update if sprite resizes
sprite.on('resize', () => {
  sprite.filterArea = new Rectangle(0, 0, sprite.width, sprite.height);
});
```

**Performance Gain**: Avoids runtime bounds calculation.

---

### 3. Release Filters When Not Needed

```javascript
// Enable filter
sprite.filters = [new BlurFilter()];

// Disable filter (releases GPU memory)
sprite.filters = null;

// Toggle based on game state
if (gameState === 'paused') {
  sprite.filters = [new BlurFilter()];
} else {
  sprite.filters = null;
}
```

---

## Text Rendering

### 1. Use BitmapText for Dynamic Text

**Problem**: Standard Text re-renders texture on every update.

**Solution**: Use BitmapText for frequently changing text.

```javascript
import { Text, BitmapText } from 'pixi.js';

// ❌ BAD: Standard Text (expensive updates)
const scoreText = new Text({ text: 'Score: 0' });

app.ticker.add(() => {
  scoreText.text = `Score: ${++score}`;  // Re-renders texture every frame
});

// ✅ GOOD: BitmapText (much faster)
const scoreBitmap = new BitmapText({
  text: 'Score: 0',
  style: { fontFamily: 'MyBitmapFont', fontSize: 24 }
});

app.ticker.add(() => {
  scoreBitmap.text = `Score: ${++score}`;  // Fast glyph updates
});
```

**Performance**: BitmapText is 10-50x faster for dynamic text.

---

### 2. Reduce Text Resolution

**Problem**: High-resolution text consumes memory.

**Solution**: Lower resolution for less critical text.

```javascript
import { Text, TextStyle } from 'pixi.js';

const style = new TextStyle({ fontSize: 36 });
const text = new Text({ text: 'Hello', style });

// Default resolution matches renderer (e.g., 2 on Retina)
text.resolution = 1;  // Reduce to 1 for memory savings

// Still looks good, uses less memory
```

---

### 3. Bake Filters into Text

**Problem**: Runtime filters on text are expensive.

**Solution**: Apply filters at texture creation.

```javascript
import { Text, TextStyle, BlurFilter } from 'pixi.js';

const style = new TextStyle({
  fontFamily: 'Arial',
  fontSize: 36,
  fill: '#ffffff',
  filters: [new BlurFilter()]  // Baked into texture at creation
});

const text = new Text({ text: 'Glowing Text', style });

// Filter applied once at creation, not every frame
```

---

## Memory Management

### 1. Destroy Display Objects Properly

```javascript
import { Sprite, Container } from 'pixi.js';

const sprite = new Sprite(texture);
const container = new Container();

// ✅ GOOD: Destroy with options
sprite.destroy({
  children: true,      // Destroy children
  texture: false,      // Keep texture (if used elsewhere)
  baseTexture: false   // Keep baseTexture
});

// Destroy container and all children
container.destroy({ children: true });

// Destroy texture when completely done
texture.destroy(true);  // true = also destroy baseTexture
```

---

### 2. Clear Event Listeners

```javascript
const sprite = new Sprite(texture);

sprite.on('pointerdown', onPointerDown);
sprite.on('pointermove', onPointerMove);

// ✅ Remove listeners before destroying
sprite.off('pointerdown', onPointerDown);
sprite.off('pointermove', onPointerMove);

// Or remove all
sprite.removeAllListeners();

sprite.destroy();
```

---

### 3. Monitor Memory Usage

```javascript
function logMemoryUsage() {
  if (performance.memory) {
    const used = (performance.memory.usedJSHeapSize / 1048576).toFixed(2);
    const total = (performance.memory.totalJSHeapSize / 1048576).toFixed(2);
    const limit = (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2);

    console.log(`Memory: ${used}MB / ${total}MB (Limit: ${limit}MB)`);
  }
}

setInterval(logMemoryUsage, 5000);
```

---

## Mobile Optimization

### 1. Disable Anti-Aliasing

```javascript
const app = new Application();
await app.init({
  width: 800,
  height: 600,
  antialias: false,  // Faster on mobile
  resolution: 1       // Lower resolution
});
```

---

### 2. Reduce Particle Count

```javascript
const isMobile = /Mobi|Android/i.test(navigator.userAgent);
const particleCount = isMobile ? 1000 : 5000;

for (let i = 0; i < particleCount; i++) {
  particles.addParticle(new Particle({ texture }));
}
```

---

### 3. Limit Frame Rate on Battery

```javascript
import { Ticker } from 'pixi.js';

function checkBattery() {
  if ('getBattery' in navigator) {
    navigator.getBattery().then(battery => {
      if (battery.charging === false && battery.level < 0.2) {
        Ticker.shared.maxFPS = 30;  // Reduce to 30 FPS
      } else {
        Ticker.shared.maxFPS = 60;
      }
    });
  }
}

checkBattery();
```

---

## Advanced Techniques

### 1. Use WebWorkers for Heavy Calculations

```javascript
// worker.js
self.onmessage = function(e) {
  const { particles, delta } = e.data;

  // Update particle physics
  particles.forEach(p => {
    p.vx += (Math.random() - 0.5) * 0.1;
    p.vy += 0.05;
    p.x += p.vx * delta;
    p.y += p.vy * delta;
  });

  self.postMessage(particles);
};

// main.js
const worker = new Worker('worker.js');

worker.onmessage = function(e) {
  const updatedParticles = e.data;

  // Apply to PixiJS particles
  updatedParticles.forEach((data, i) => {
    particles.particleChildren[i].x = data.x;
    particles.particleChildren[i].y = data.y;
  });
};

app.ticker.add((ticker) => {
  const particleData = particles.particleChildren.map(p => ({
    x: p.x,
    y: p.y,
    vx: p.vx || 0,
    vy: p.vy || 0
  }));

  worker.postMessage({ particles: particleData, delta: ticker.deltaTime });
});
```

---

### 2. Implement Spatial Hashing for Collision Detection

```javascript
class SpatialHash {
  constructor(cellSize) {
    this.cellSize = cellSize;
    this.grid = new Map();
  }

  clear() {
    this.grid.clear();
  }

  insert(sprite) {
    const cells = this.getCells(sprite);
    cells.forEach(cell => {
      const key = `${cell.x},${cell.y}`;
      if (!this.grid.has(key)) {
        this.grid.set(key, []);
      }
      this.grid.get(key).push(sprite);
    });
  }

  getCells(sprite) {
    const bounds = sprite.getBounds();
    const cells = [];

    const minX = Math.floor(bounds.x / this.cellSize);
    const maxX = Math.floor((bounds.x + bounds.width) / this.cellSize);
    const minY = Math.floor(bounds.y / this.cellSize);
    const maxY = Math.floor((bounds.y + bounds.height) / this.cellSize);

    for (let x = minX; x <= maxX; x++) {
      for (let y = minY; y <= maxY; y++) {
        cells.push({ x, y });
      }
    }

    return cells;
  }

  getNearby(sprite) {
    const cells = this.getCells(sprite);
    const nearby = new Set();

    cells.forEach(cell => {
      const key = `${cell.x},${cell.y}`;
      const sprites = this.grid.get(key);
      if (sprites) {
        sprites.forEach(s => {
          if (s !== sprite) nearby.add(s);
        });
      }
    });

    return Array.from(nearby);
  }
}

// Usage
const spatialHash = new SpatialHash(100);

app.ticker.add(() => {
  spatialHash.clear();

  // Insert all sprites
  sprites.forEach(sprite => spatialHash.insert(sprite));

  // Check collisions only with nearby sprites
  sprites.forEach(sprite => {
    const nearby = spatialHash.getNearby(sprite);
    nearby.forEach(other => {
      if (checkCollision(sprite, other)) {
        handleCollision(sprite, other);
      }
    });
  });
});
```

**Performance**: O(n) instead of O(n²) for collision detection.

---

## Performance Checklist

✅ **Rendering**
- [ ] Use ParticleContainer for 1,000+ sprites
- [ ] Batch sprites by texture
- [ ] Enable culling for off-screen objects
- [ ] Cache static graphics as bitmaps
- [ ] Minimize draw calls

✅ **Textures**
- [ ] Destroy unused textures
- [ ] Use sprite atlases
- [ ] Optimize texture sizes (power-of-2)
- [ ] Lazy load non-critical assets

✅ **Containers**
- [ ] Disable sortableChildren unless needed
- [ ] Use object pooling
- [ ] Keep hierarchy shallow

✅ **Filters**
- [ ] Limit filter usage (1-2 per scene)
- [ ] Specify filterArea
- [ ] Release filters when not needed
- [ ] Bake filters into textures

✅ **Text**
- [ ] Use BitmapText for dynamic text
- [ ] Reduce text resolution
- [ ] Bake filters into TextStyle

✅ **Memory**
- [ ] Destroy objects properly
- [ ] Clear event listeners
- [ ] Monitor memory usage

✅ **Mobile**
- [ ] Disable anti-aliasing
- [ ] Reduce particle counts
- [ ] Lower resolution
- [ ] Limit frame rate on battery

---

## Debugging Performance Issues

### Identify Bottlenecks

```javascript
// Measure specific operations
console.time('particleUpdate');
updateParticles();
console.timeEnd('particleUpdate');

// Profile draw calls
console.log('Draw calls:', app.renderer.stats.drawCalls.total);

// Check texture count
console.log('Textures bound:', app.renderer.stats.textureCount);
```

### Common Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Low FPS | Too many draw calls | Batch sprites, use atlases |
| Stuttering | GC pauses | Use object pooling |
| High memory | Texture leaks | Destroy textures properly |
| Slow filters | Too many filters | Limit usage, bake into textures |
| Laggy text | Text updates | Use BitmapText |

---

This guide provides comprehensive strategies for optimizing PixiJS applications to achieve smooth 60 FPS performance across devices.



===== FILE: plugins/individual/pixijs-2d/agents/pixijs-2d-architect.md =====

# PixiJS 2D Architect

## Role

Expert 3D/graphics architect specializing in PixiJS 2D scene design, optimization, and best practices.

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
3. Implement best practices from PixiJS 2D ecosystem
4. Optimize for target platforms and devices
5. Provide detailed implementation guidance

## Tools

This agent has access to:
- PixiJS 2D skill knowledge
- Optimization checklists and patterns
- Performance profiling guidance
- Asset pipeline recommendations



===== FILE: plugins/individual/pixijs-2d/commands/particle_builder.md =====

# /pixijs-2d-particle_builder

PixiJS 2D - Particle Builder

## Description

Executes the particle_builder script for PixiJS 2D.

## Usage

```bash
/pixijs-2d-particle_builder
```

## Implementation

This command runs the `particle_builder.py` script from the PixiJS 2D skill, which provides automated assistance for particle builder.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/pixijs-2d/commands/sprite_generator.md =====

# /pixijs-2d-sprite_generator

PixiJS 2D - Sprite Generator

## Description

Executes the sprite_generator script for PixiJS 2D.

## Usage

```bash
/pixijs-2d-sprite_generator
```

## Implementation

This command runs the `sprite_generator.py` script from the PixiJS 2D skill, which provides automated assistance for sprite generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/pixijs-2d/skills/pixijs-2d/scripts/particle_builder.py =====

```py
#!/usr/bin/env python3
"""
PixiJS Particle Builder
Generates high-performance particle systems using ParticleContainer.

Usage:
    Interactive mode:
        python particle_builder.py

    CLI mode:
        python particle_builder.py --type fountain --count 5000 --output ./
        python particle_builder.py -t fire -c 2000 -o ./my-project/
"""

import argparse
import os
import sys
from typing import Dict, Tuple


def generate_fountain_particles(count: int = 5000) -> str:
    """Generate fountain particle system"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Fountain Particles</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #0a0a0a;
        }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h3>Fountain Particles</h3>
        <p>Particles: {count}</p>
        <p>FPS: <span id="fps">--</span></p>
    </div>

    <script src="https://pixijs.download/release/pixi.js"></script>
    <script>
        (async () => {{
            const app = new PIXI.Application();

            await app.init({{
                width: 800,
                height: 600,
                backgroundColor: 0x0a0a0a,
                antialias: true
            }});

            document.body.appendChild(app.canvas);

            // Create particle texture
            const graphics = new PIXI.Graphics();
            graphics.circle(5, 5, 5).fill(0xffffff);
            const particleTexture = app.renderer.generateTexture(graphics);

            // Create particle container
            const particles = new PIXI.ParticleContainer({{
                maxSize: {count},
                dynamicProperties: {{
                    position: true,
                    scale: true,
                    rotation: false,
                    color: true
                }}
            }});

            app.stage.addChild(particles);

            // Particle data
            const particleData = [];

            for (let i = 0; i < {count}; i++) {{
                const particle = new PIXI.Particle({{
                    texture: particleTexture,
                    x: 400,
                    y: 550
                }});

                particles.addParticle(particle);

                particleData.push({{
                    particle,
                    vx: (Math.random() - 0.5) * 8,
                    vy: -(Math.random() * 12 + 8),
                    life: 1.0,
                    gravity: 0.2
                }});
            }}

            // Update loop
            app.ticker.add((ticker) => {{
                particleData.forEach(data => {{
                    // Physics
                    data.particle.x += data.vx * ticker.deltaTime;
                    data.particle.y += data.vy * ticker.deltaTime;
                    data.vy += data.gravity * ticker.deltaTime;

                    // Fade out
                    data.life -= 0.01 * ticker.deltaTime;

                    if (data.life > 0) {{
                        const color = Math.floor(data.life * 255);
                        data.particle.tint = (color << 16) | (color << 8) | 255;
                        data.particle.alpha = data.life;
                    }} else {{
                        // Reset particle
                        data.particle.x = 400;
                        data.particle.y = 550;
                        data.vx = (Math.random() - 0.5) * 8;
                        data.vy = -(Math.random() * 12 + 8);
                        data.life = 1.0;
                    }}
                }});

                // Update FPS
                document.getElementById('fps').textContent = Math.round(app.ticker.FPS);
            }});
        }})();
    </script>
</body>
</html>"""


def generate_fire_particles(count: int = 2000) -> str:
    """Generate fire particle system"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Fire Particles</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #1a0a00;
        }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h3>Fire Particles</h3>
        <p>Particles: {count}</p>
        <p>FPS: <span id="fps">--</span></p>
    </div>

    <script src="https://pixijs.download/release/pixi.js"></script>
    <script>
        (async () => {{
            const app = new PIXI.Application();

            await app.init({{
                width: 800,
                height: 600,
                backgroundColor: 0x1a0a00,
                antialias: true
            }});

            document.body.appendChild(app.canvas);

            // Create particle texture
            const graphics = new PIXI.Graphics();
            graphics.circle(8, 8, 8).fill(0xffffff);
            const particleTexture = app.renderer.generateTexture(graphics);

            // Create particle container
            const particles = new PIXI.ParticleContainer({{
                maxSize: {count},
                dynamicProperties: {{
                    position: true,
                    scale: true,
                    rotation: true,
                    color: true
                }}
            }});

            app.stage.addChild(particles);

            // Particle data
            const particleData = [];

            for (let i = 0; i < {count}; i++) {{
                const particle = new PIXI.Particle({{
                    texture: particleTexture,
                    x: 400,
                    y: 550
                }});

                particles.addParticle(particle);

                particleData.push({{
                    particle,
                    vx: (Math.random() - 0.5) * 2,
                    vy: -(Math.random() * 3 + 2),
                    life: Math.random(),
                    maxLife: Math.random() * 0.5 + 0.5
                }});
            }}

            // Update loop
            app.ticker.add((ticker) => {{
                particleData.forEach(data => {{
                    // Physics
                    data.particle.x += data.vx * ticker.deltaTime;
                    data.particle.y += data.vy * ticker.deltaTime;

                    // Wind
                    data.vx += (Math.random() - 0.5) * 0.1 * ticker.deltaTime;

                    // Rise
                    data.vy -= 0.05 * ticker.deltaTime;

                    // Fade
                    data.life -= 0.01 * ticker.deltaTime;

                    if (data.life > 0) {{
                        const t = data.life / data.maxLife;

                        // Color gradient: yellow -> orange -> red -> black
                        let r, g, b;
                        if (t > 0.66) {{
                            // Yellow to orange
                            const localT = (t - 0.66) / 0.34;
                            r = 255;
                            g = Math.floor(255 * localT);
                            b = 0;
                        }} else if (t > 0.33) {{
                            // Orange to red
                            const localT = (t - 0.33) / 0.33;
                            r = 255;
                            g = Math.floor(128 * localT);
                            b = 0;
                        }} else {{
                            // Red to black
                            r = Math.floor(255 * (t / 0.33));
                            g = 0;
                            b = 0;
                        }}

                        data.particle.tint = (r << 16) | (g << 8) | b;
                        data.particle.alpha = t;
                        data.particle.scaleX = t * 1.5;
                        data.particle.scaleY = t * 1.5;
                        data.particle.rotation += 0.1 * ticker.deltaTime;
                    }} else {{
                        // Reset particle
                        data.particle.x = 400 + (Math.random() - 0.5) * 100;
                        data.particle.y = 550;
                        data.vx = (Math.random() - 0.5) * 2;
                        data.vy = -(Math.random() * 3 + 2);
                        data.life = data.maxLife;
                    }}
                }});

                document.getElementById('fps').textContent = Math.round(app.ticker.FPS);
            }});
        }})();
    </script>
</body>
</html>"""


def generate_snow_particles(count: int = 3000) -> str:
    """Generate snow particle system"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Snow Particles</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: linear-gradient(to bottom, #2c3e50, #34495e);
        }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h3>Snow Particles</h3>
        <p>Particles: {count}</p>
        <p>FPS: <span id="fps">--</span></p>
    </div>

    <script src="https://pixijs.download/release/pixi.js"></script>
    <script>
        (async () => {{
            const app = new PIXI.Application();

            await app.init({{
                width: 800,
                height: 600,
                backgroundAlpha: 0,
                antialias: true
            }});

            document.body.appendChild(app.canvas);

            // Create snowflake texture
            const graphics = new PIXI.Graphics();
            graphics.circle(3, 3, 3).fill(0xffffff);
            const snowTexture = app.renderer.generateTexture(graphics);

            // Create particle container
            const particles = new PIXI.ParticleContainer({{
                maxSize: {count},
                dynamicProperties: {{
                    position: true,
                    scale: true,
                    rotation: true,
                    color: false
                }}
            }});

            app.stage.addChild(particles);

            // Particle data
            const particleData = [];

            for (let i = 0; i < {count}; i++) {{
                const particle = new PIXI.Particle({{
                    texture: snowTexture,
                    x: Math.random() * 800,
                    y: Math.random() * 600,
                    scaleX: Math.random() * 0.5 + 0.5,
                    scaleY: Math.random() * 0.5 + 0.5,
                    alpha: Math.random() * 0.5 + 0.5
                }});

                particles.addParticle(particle);

                particleData.push({{
                    particle,
                    speed: Math.random() * 1 + 0.5,
                    sway: Math.random() * Math.PI * 2,
                    swaySpeed: Math.random() * 0.02 + 0.01
                }});
            }}

            // Update loop
            app.ticker.add((ticker) => {{
                particleData.forEach(data => {{
                    // Fall down
                    data.particle.y += data.speed * ticker.deltaTime;

                    // Sway left and right
                    data.sway += data.swaySpeed * ticker.deltaTime;
                    data.particle.x += Math.sin(data.sway) * 0.5 * ticker.deltaTime;

                    // Rotate
                    data.particle.rotation += 0.01 * ticker.deltaTime;

                    // Reset if below screen
                    if (data.particle.y > 600) {{
                        data.particle.y = -10;
                        data.particle.x = Math.random() * 800;
                    }}
                }});

                document.getElementById('fps').textContent = Math.round(app.ticker.FPS);
            }});
        }})();
    </script>
</body>
</html>"""


def generate_explosion_particles(count: int = 1000) -> str:
    """Generate explosion particle system"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Explosion Particles</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #0a0a0a;
        }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h3>Explosion Particles</h3>
        <p>Click to explode</p>
        <p>FPS: <span id="fps">--</span></p>
    </div>

    <script src="https://pixijs.download/release/pixi.js"></script>
    <script>
        (async () => {{
            const app = new PIXI.Application();

            await app.init({{
                width: 800,
                height: 600,
                backgroundColor: 0x0a0a0a,
                antialias: true
            }});

            document.body.appendChild(app.canvas);

            // Create particle texture
            const graphics = new PIXI.Graphics();
            graphics.circle(4, 4, 4).fill(0xffffff);
            const particleTexture = app.renderer.generateTexture(graphics);

            // Create particle container
            const particles = new PIXI.ParticleContainer({{
                maxSize: {count},
                dynamicProperties: {{
                    position: true,
                    scale: true,
                    rotation: false,
                    color: true
                }}
            }});

            app.stage.addChild(particles);

            // Particle pool
            const particleData = [];

            for (let i = 0; i < {count}; i++) {{
                const particle = new PIXI.Particle({{
                    texture: particleTexture,
                    x: -100,
                    y: -100
                }});

                particle.alpha = 0;
                particles.addParticle(particle);

                particleData.push({{
                    particle,
                    vx: 0,
                    vy: 0,
                    life: 0,
                    active: false
                }});
            }}

            // Explosion function
            function explode(x, y) {{
                let spawned = 0;

                particleData.forEach(data => {{
                    if (!data.active && spawned < 100) {{
                        const angle = Math.random() * Math.PI * 2;
                        const speed = Math.random() * 8 + 4;

                        data.particle.x = x;
                        data.particle.y = y;
                        data.vx = Math.cos(angle) * speed;
                        data.vy = Math.sin(angle) * speed;
                        data.life = 1.0;
                        data.active = true;
                        data.particle.alpha = 1;

                        spawned++;
                    }}
                }});
            }}

            // Click to explode
            app.canvas.addEventListener('click', (e) => {{
                const rect = app.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                explode(x, y);
            }});

            // Update loop
            app.ticker.add((ticker) => {{
                particleData.forEach(data => {{
                    if (data.active) {{
                        // Physics
                        data.particle.x += data.vx * ticker.deltaTime;
                        data.particle.y += data.vy * ticker.deltaTime;

                        // Gravity
                        data.vy += 0.2 * ticker.deltaTime;

                        // Drag
                        data.vx *= 0.98;
                        data.vy *= 0.98;

                        // Fade
                        data.life -= 0.02 * ticker.deltaTime;

                        if (data.life > 0) {{
                            // Color: white -> yellow -> orange -> red
                            let r, g, b;
                            if (data.life > 0.75) {{
                                r = 255;
                                g = 255;
                                b = 255;
                            }} else if (data.life > 0.5) {{
                                r = 255;
                                g = 255;
                                b = Math.floor((data.life - 0.5) * 4 * 255);
                            }} else if (data.life > 0.25) {{
                                r = 255;
                                g = Math.floor((data.life - 0.25) * 4 * 255);
                                b = 0;
                            }} else {{
                                r = Math.floor(data.life * 4 * 255);
                                g = 0;
                                b = 0;
                            }}

                            data.particle.tint = (r << 16) | (g << 8) | b;
                            data.particle.alpha = data.life;
                            data.particle.scaleX = data.life;
                            data.particle.scaleY = data.life;
                        }} else {{
                            data.active = false;
                            data.particle.alpha = 0;
                        }}
                    }}
                }});

                document.getElementById('fps').textContent = Math.round(app.ticker.FPS);
            }});

            // Initial explosion
            explode(400, 300);
        }})();
    </script>
</body>
</html>"""


def generate_stars_particles(count: int = 5000) -> str:
    """Generate starfield particle system"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Starfield</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #000000;
        }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h3>Starfield</h3>
        <p>Stars: {count}</p>
        <p>FPS: <span id="fps">--</span></p>
    </div>

    <script src="https://pixijs.download/release/pixi.js"></script>
    <script>
        (async () => {{
            const app = new PIXI.Application();

            await app.init({{
                width: 800,
                height: 600,
                backgroundColor: 0x000000,
                antialias: true
            }});

            document.body.appendChild(app.canvas);

            // Create star texture
            const graphics = new PIXI.Graphics();
            graphics.circle(2, 2, 2).fill(0xffffff);
            const starTexture = app.renderer.generateTexture(graphics);

            // Create particle container
            const particles = new PIXI.ParticleContainer({{
                maxSize: {count},
                dynamicProperties: {{
                    position: true,
                    scale: true,
                    rotation: false,
                    color: false
                }}
            }});

            app.stage.addChild(particles);

            // Particle data
            const particleData = [];

            for (let i = 0; i < {count}; i++) {{
                const particle = new PIXI.Particle({{
                    texture: starTexture,
                    x: Math.random() * 800,
                    y: Math.random() * 600,
                    scaleX: Math.random(),
                    scaleY: Math.random(),
                    alpha: Math.random()
                }});

                particles.addParticle(particle);

                particleData.push({{
                    particle,
                    z: Math.random() * 1000,
                    speed: Math.random() * 2 + 1
                }});
            }}

            // Update loop
            const centerX = 400;
            const centerY = 300;

            app.ticker.add((ticker) => {{
                particleData.forEach(data => {{
                    // Move toward camera
                    data.z -= data.speed * ticker.deltaTime;

                    if (data.z <= 0) {{
                        data.z = 1000;
                    }}

                    // Project 3D to 2D
                    const scale = 1000 / data.z;
                    const x = (data.particle.x - centerX) * scale + centerX;
                    const y = (data.particle.y - centerY) * scale + centerY;

                    data.particle.x = x;
                    data.particle.y = y;
                    data.particle.scaleX = scale;
                    data.particle.scaleY = scale;
                    data.particle.alpha = Math.min(scale, 1);

                    // Reset if off screen
                    if (x < 0 || x > 800 || y < 0 || y > 600) {{
                        data.particle.x = Math.random() * 800;
                        data.particle.y = Math.random() * 600;
                        data.z = 1000;
                    }}
                }});

                document.getElementById('fps').textContent = Math.round(app.ticker.FPS);
            }});
        }})();
    </script>
</body>
</html>"""


# Particle type registry
PARTICLE_TYPES: Dict[str, Dict] = {
    'fountain': {
        'name': 'Fountain',
        'description': 'Particles shooting upward with gravity',
        'default_count': 5000,
        'generator': generate_fountain_particles
    },
    'fire': {
        'name': 'Fire',
        'description': 'Fire effect with color gradient',
        'default_count': 2000,
        'generator': generate_fire_particles
    },
    'snow': {
        'name': 'Snow',
        'description': 'Falling snowflakes with sway',
        'default_count': 3000,
        'generator': generate_snow_particles
    },
    'explosion': {
        'name': 'Explosion',
        'description': 'Click-triggered explosions',
        'default_count': 1000,
        'generator': generate_explosion_particles
    },
    'stars': {
        'name': 'Starfield',
        'description': '3D starfield effect',
        'default_count': 5000,
        'generator': generate_stars_particles
    }
}


def interactive_mode():
    """Run interactive particle builder"""
    print("\n" + "="*60)
    print("PixiJS Particle Builder - Interactive Mode")
    print("="*60)

    # Show particle types
    print("\nAvailable particle systems:")
    print("-" * 60)
    for idx, (key, info) in enumerate(PARTICLE_TYPES.items(), 1):
        print(f"{idx}. {info['name']:15} - {info['description']} ({info['default_count']} particles)")

    # Get particle type
    while True:
        try:
            choice = input(f"\nSelect particle type (1-{len(PARTICLE_TYPES)}): ").strip()
            idx = int(choice)
            if 1 <= idx <= len(PARTICLE_TYPES):
                particle_type = list(PARTICLE_TYPES.keys())[idx - 1]
                break
            print(f"Error: Please enter a number between 1 and {len(PARTICLE_TYPES)}")
        except ValueError:
            print("Error: Please enter a valid number")

    # Get particle count
    default_count = PARTICLE_TYPES[particle_type]['default_count']
    count_input = input(f"\nParticle count (default: {default_count}): ").strip()
    count = int(count_input) if count_input else default_count

    # Get output directory
    output_dir = input("\nOutput directory (default: current directory): ").strip()
    if not output_dir:
        output_dir = "."

    # Generate particles
    print("\n" + "-"*60)
    print("Generating particle system...")

    try:
        generator = PARTICLE_TYPES[particle_type]['generator']
        html = generator(count)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Write HTML file
        filename = f"{particle_type}_particles.html"
        html_path = os.path.join(output_dir, filename)

        with open(html_path, 'w') as f:
            f.write(html)

        print(f"\n✓ Particle system created: {html_path}")
        print(f"\nParticle type: {PARTICLE_TYPES[particle_type]['name']}")
        print(f"Particle count: {count}")
        print(f"Lines of code: {len(html.splitlines())}")

        print("\nTo view:")
        print(f"  Open {html_path} in a web browser")
        print(f"  Or run: python -m http.server 8000")

    except Exception as e:
        print(f"\nError: Failed to generate particle system: {e}")
        return 1

    return 0


def cli_mode(args):
    """Run CLI particle builder"""
    particle_type = args.type
    count = args.count
    output_dir = args.output

    # Validate particle type
    if particle_type not in PARTICLE_TYPES:
        print(f"Error: Unknown particle type '{particle_type}'")
        print(f"Available types: {', '.join(PARTICLE_TYPES.keys())}")
        return 1

    # Use default count if not specified
    if count is None:
        count = PARTICLE_TYPES[particle_type]['default_count']

    # Generate particles
    try:
        generator = PARTICLE_TYPES[particle_type]['generator']
        html = generator(count)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Write HTML file
        filename = f"{particle_type}_particles.html"
        html_path = os.path.join(output_dir, filename)

        with open(html_path, 'w') as f:
            f.write(html)

        print(f"✓ Particle system created: {html_path}")
        return 0

    except Exception as e:
        print(f"Error: Failed to generate particle system: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='PixiJS Particle Builder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python particle_builder.py

  Generate fountain particles:
    python particle_builder.py --type fountain --count 5000 --output ./

  Generate fire particles:
    python particle_builder.py -t fire -c 2000 -o ./effects/

  Generate snow particles:
    python particle_builder.py -t snow -c 3000

Available particle types:
  fountain   - Particles shooting upward with gravity
  fire       - Fire effect with color gradient
  snow       - Falling snowflakes with sway
  explosion  - Click-triggered explosions
  stars      - 3D starfield effect
        """
    )

    parser.add_argument(
        '-t', '--type',
        choices=list(PARTICLE_TYPES.keys()),
        help='Particle system type'
    )

    parser.add_argument(
        '-c', '--count',
        type=int,
        help='Number of particles'
    )

    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output directory (default: current directory)'
    )

    args = parser.parse_args()

    # Run interactive mode if no particle type specified
    if not args.type:
        return interactive_mode()

    return cli_mode(args)


if __name__ == '__main__':
    sys.exit(main())

```


===== FILE: plugins/individual/pixijs-2d/skills/pixijs-2d/scripts/sprite_generator.py =====

```py
#!/usr/bin/env python3
"""
PixiJS Sprite Generator
Generates PixiJS sprite-based applications with various templates.

Usage:
    Interactive mode:
        python sprite_generator.py

    CLI mode:
        python sprite_generator.py --type basic --output ./
        python sprite_generator.py -t interactive -o ./my-project/
        python sprite_generator.py -t animated --name MySprite
"""

import argparse
import os
import sys
from typing import Dict, Tuple


def generate_basic_sprite() -> Tuple[str, str]:
    """Generate basic sprite example"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Basic Sprite</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #1a1a2e;
        }
        #info {
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div id="info">
        <h3>Basic Sprite</h3>
        <p>Click the sprite to change color</p>
    </div>

    <script src="https://pixijs.download/release/pixi.js"></script>
    <script>
        (async () => {
            // Create application
            const app = new PIXI.Application();

            await app.init({
                width: 800,
                height: 600,
                backgroundColor: 0x1a1a2e,
                antialias: true
            });

            document.body.appendChild(app.canvas);

            // Create sprite
            const graphics = new PIXI.Graphics();
            graphics.rect(0, 0, 100, 100).fill(0x3498db);

            const texture = app.renderer.generateTexture(graphics);
            const sprite = new PIXI.Sprite(texture);

            sprite.anchor.set(0.5);
            sprite.position.set(400, 300);
            sprite.eventMode = 'static';
            sprite.cursor = 'pointer';

            app.stage.addChild(sprite);

            // Rotate animation
            app.ticker.add((ticker) => {
                sprite.rotation += 0.01 * ticker.deltaTime;
            });

            // Click event
            const colors = [0x3498db, 0xe74c3c, 0x2ecc71, 0xf39c12, 0x9b59b6];
            let colorIndex = 0;

            sprite.on('pointerdown', () => {
                colorIndex = (colorIndex + 1) % colors.length;

                const newGraphics = new PIXI.Graphics();
                newGraphics.rect(0, 0, 100, 100).fill(colors[colorIndex]);
                sprite.texture = app.renderer.generateTexture(newGraphics);
            });
        })();
    </script>
</body>
</html>"""

    js = """// Standalone JavaScript version
import { Application, Sprite, Graphics } from 'pixi.js';

(async () => {
    const app = new Application();

    await app.init({
        width: 800,
        height: 600,
        backgroundColor: 0x1a1a2e,
        antialias: true
    });

    document.body.appendChild(app.canvas);

    // Create sprite
    const graphics = new Graphics();
    graphics.rect(0, 0, 100, 100).fill(0x3498db);

    const texture = app.renderer.generateTexture(graphics);
    const sprite = new Sprite(texture);

    sprite.anchor.set(0.5);
    sprite.position.set(400, 300);
    sprite.eventMode = 'static';
    sprite.cursor = 'pointer';

    app.stage.addChild(sprite);

    // Rotate animation
    app.ticker.add((ticker) => {
        sprite.rotation += 0.01 * ticker.deltaTime;
    });

    // Click event
    const colors = [0x3498db, 0xe74c3c, 0x2ecc71, 0xf39c12, 0x9b59b6];
    let colorIndex = 0;

    sprite.on('pointerdown', () => {
        colorIndex = (colorIndex + 1) % colors.length;

        const newGraphics = new Graphics();
        newGraphics.rect(0, 0, 100, 100).fill(colors[colorIndex]);
        sprite.texture = app.renderer.generateTexture(newGraphics);
    });
})();
"""

    return html, js


def generate_interactive_sprite() -> Tuple[str, str]:
    """Generate interactive sprite with drag and hover"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Interactive Sprite</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #0f0f23;
        }
        #info {
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div id="info">
        <h3>Interactive Sprite</h3>
        <p>Drag to move • Hover to scale</p>
    </div>

    <script src="https://pixijs.download/release/pixi.js"></script>
    <script>
        (async () => {
            const app = new PIXI.Application();

            await app.init({
                width: 800,
                height: 600,
                backgroundColor: 0x0f0f23,
                antialias: true
            });

            document.body.appendChild(app.canvas);

            // Create draggable sprite
            function createDraggableSprite(x, y, color) {
                const graphics = new PIXI.Graphics();
                graphics.circle(50, 50, 50).fill(color);

                const texture = app.renderer.generateTexture(graphics);
                const sprite = new PIXI.Sprite(texture);

                sprite.anchor.set(0.5);
                sprite.position.set(x, y);
                sprite.eventMode = 'static';
                sprite.cursor = 'pointer';

                // Drag state
                sprite.dragging = false;
                sprite.dragData = null;
                sprite.originalScale = 1.0;

                // Pointer events
                sprite.on('pointerdown', onDragStart);
                sprite.on('pointerup', onDragEnd);
                sprite.on('pointerupoutside', onDragEnd);
                sprite.on('pointermove', onDragMove);
                sprite.on('pointerover', onHoverStart);
                sprite.on('pointerout', onHoverEnd);

                function onDragStart(event) {
                    sprite.dragging = true;
                    sprite.dragData = event.data;
                    sprite.alpha = 0.7;
                }

                function onDragEnd() {
                    sprite.dragging = false;
                    sprite.dragData = null;
                    sprite.alpha = 1.0;
                }

                function onDragMove() {
                    if (sprite.dragging) {
                        const newPosition = sprite.dragData.global;
                        sprite.position.set(newPosition.x, newPosition.y);
                    }
                }

                function onHoverStart() {
                    app.canvas.style.cursor = 'grab';
                    if (!sprite.dragging) {
                        sprite.scale.set(1.2);
                    }
                }

                function onHoverEnd() {
                    app.canvas.style.cursor = 'default';
                    if (!sprite.dragging) {
                        sprite.scale.set(sprite.originalScale);
                    }
                }

                return sprite;
            }

            // Create multiple draggable sprites
            const colors = [0xe74c3c, 0x3498db, 0x2ecc71, 0xf39c12, 0x9b59b6];

            for (let i = 0; i < 5; i++) {
                const x = 150 + i * 120;
                const y = 300;
                const sprite = createDraggableSprite(x, y, colors[i]);
                app.stage.addChild(sprite);
            }
        })();
    </script>
</body>
</html>"""

    js = ""  # Standalone JS same as embedded
    return html, js


def generate_animated_sprite() -> Tuple[str, str]:
    """Generate sprite sheet animation"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Animated Sprite</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #2c3e50;
        }
        #controls {
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }
        button {
            margin: 5px;
            padding: 5px 10px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div id="controls">
        <h3>Animated Sprite</h3>
        <button id="play">Play</button>
        <button id="stop">Stop</button>
        <button id="faster">Faster</button>
        <button id="slower">Slower</button>
    </div>

    <script src="https://pixijs.download/release/pixi.js"></script>
    <script>
        (async () => {
            const app = new PIXI.Application();

            await app.init({
                width: 800,
                height: 600,
                backgroundColor: 0x2c3e50,
                antialias: true
            });

            document.body.appendChild(app.canvas);

            // Generate sprite sheet frames
            const frames = [];
            for (let i = 0; i < 12; i++) {
                const graphics = new PIXI.Graphics();

                // Animate a growing/shrinking circle
                const scale = 0.5 + Math.sin(i / 12 * Math.PI * 2) * 0.5;
                const radius = 50 * scale;

                graphics.circle(50, 50, radius).fill(0x3498db);

                const texture = app.renderer.generateTexture(graphics);
                frames.push(texture);
            }

            // Create animated sprite
            const animation = new PIXI.AnimatedSprite(frames);
            animation.anchor.set(0.5);
            animation.position.set(400, 300);
            animation.animationSpeed = 0.16;
            animation.play();

            app.stage.addChild(animation);

            // Controls
            document.getElementById('play').addEventListener('click', () => {
                animation.play();
            });

            document.getElementById('stop').addEventListener('click', () => {
                animation.stop();
            });

            document.getElementById('faster').addEventListener('click', () => {
                animation.animationSpeed *= 1.5;
            });

            document.getElementById('slower').addEventListener('click', () => {
                animation.animationSpeed /= 1.5;
            });

            // Rotate animation
            app.ticker.add((ticker) => {
                animation.rotation += 0.01 * ticker.deltaTime;
            });
        })();
    </script>
</body>
</html>"""

    js = ""
    return html, js


def generate_tiled_sprites() -> Tuple[str, str]:
    """Generate tiled sprite pattern"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Tiled Sprites</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #34495e;
        }
        #info {
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div id="info">
        <h3>Tiled Sprites</h3>
        <p>Scrolling background pattern</p>
    </div>

    <script src="https://pixijs.download/release/pixi.js"></script>
    <script>
        (async () => {
            const app = new PIXI.Application();

            await app.init({
                width: 800,
                height: 600,
                backgroundColor: 0x34495e,
                antialias: true
            });

            document.body.appendChild(app.canvas);

            // Create tile texture
            const graphics = new PIXI.Graphics();
            graphics.rect(0, 0, 64, 64).fill(0x3498db);
            graphics.rect(4, 4, 56, 56).fill(0x2980b9);

            const tileTexture = app.renderer.generateTexture(graphics);

            // Create tiling sprite
            const tilingSprite = new PIXI.TilingSprite({
                texture: tileTexture,
                width: app.screen.width,
                height: app.screen.height
            });

            app.stage.addChild(tilingSprite);

            // Scroll animation
            app.ticker.add((ticker) => {
                tilingSprite.tilePosition.x += 1 * ticker.deltaTime;
                tilingSprite.tilePosition.y += 0.5 * ticker.deltaTime;
            });
        })();
    </script>
</body>
</html>"""

    js = ""
    return html, js


def generate_spritesheet_atlas() -> Tuple[str, str]:
    """Generate sprite sheet with texture atlas"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Sprite Sheet</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #1a1a2e;
        }
        #info {
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div id="info">
        <h3>Sprite Sheet Atlas</h3>
        <p>Multiple sprites from texture atlas</p>
    </div>

    <script src="https://pixijs.download/release/pixi.js"></script>
    <script>
        (async () => {
            const app = new PIXI.Application();

            await app.init({
                width: 800,
                height: 600,
                backgroundColor: 0x1a1a2e,
                antialias: true
            });

            document.body.appendChild(app.canvas);

            // Create texture atlas (sprite sheet)
            const atlas = {};
            const shapes = ['circle', 'square', 'triangle', 'star', 'hexagon'];
            const colors = [0xe74c3c, 0x3498db, 0x2ecc71, 0xf39c12, 0x9b59b6];

            shapes.forEach((shape, index) => {
                const graphics = new PIXI.Graphics();

                switch(shape) {
                    case 'circle':
                        graphics.circle(25, 25, 25).fill(colors[index]);
                        break;
                    case 'square':
                        graphics.rect(0, 0, 50, 50).fill(colors[index]);
                        break;
                    case 'triangle':
                        graphics.poly([25, 0, 50, 50, 0, 50]).fill(colors[index]);
                        break;
                    case 'star':
                        graphics.star(25, 25, 5, 25).fill(colors[index]);
                        break;
                    case 'hexagon':
                        graphics.poly([
                            25, 0, 45, 12.5, 45, 37.5, 25, 50, 5, 37.5, 5, 12.5
                        ]).fill(colors[index]);
                        break;
                }

                atlas[shape] = app.renderer.generateTexture(graphics);
            });

            // Create sprites from atlas
            shapes.forEach((shape, index) => {
                const sprite = new PIXI.Sprite(atlas[shape]);
                sprite.anchor.set(0.5);
                sprite.position.set(150 + index * 120, 300);
                sprite.eventMode = 'static';
                sprite.cursor = 'pointer';

                // Hover effect
                sprite.on('pointerover', () => {
                    sprite.scale.set(1.2);
                });

                sprite.on('pointerout', () => {
                    sprite.scale.set(1.0);
                });

                // Click to rotate
                sprite.on('pointerdown', () => {
                    sprite.rotation += Math.PI / 4;
                });

                app.stage.addChild(sprite);

                // Floating animation
                const startY = sprite.y;
                app.ticker.add(() => {
                    sprite.y = startY + Math.sin(Date.now() * 0.001 + index) * 20;
                });
            });
        })();
    </script>
</body>
</html>"""

    js = ""
    return html, js


def generate_masked_sprite() -> Tuple[str, str]:
    """Generate sprite with mask"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Masked Sprite</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
            background: #2c3e50;
        }
        #info {
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div id="info">
        <h3>Masked Sprite</h3>
        <p>Circular mask reveals gradient</p>
    </div>

    <script src="https://pixijs.download/release/pixi.js"></script>
    <script>
        (async () => {
            const app = new PIXI.Application();

            await app.init({
                width: 800,
                height: 600,
                backgroundColor: 0x2c3e50,
                antialias: true
            });

            document.body.appendChild(app.canvas);

            // Create gradient texture
            const canvas = document.createElement('canvas');
            canvas.width = 400;
            canvas.height = 400;
            const ctx = canvas.getContext('2d');

            const gradient = ctx.createLinearGradient(0, 0, 400, 400);
            gradient.addColorStop(0, '#e74c3c');
            gradient.addColorStop(0.5, '#3498db');
            gradient.addColorStop(1, '#2ecc71');

            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, 400, 400);

            const gradientTexture = PIXI.Texture.from(canvas);
            const sprite = new PIXI.Sprite(gradientTexture);
            sprite.anchor.set(0.5);
            sprite.position.set(400, 300);

            // Create circular mask
            const mask = new PIXI.Graphics();
            mask.circle(400, 300, 150).fill(0xffffff);

            sprite.mask = mask;

            app.stage.addChild(mask, sprite);

            // Animate mask
            let growing = true;
            let radius = 150;

            app.ticker.add((ticker) => {
                sprite.rotation += 0.01 * ticker.deltaTime;

                // Pulse mask
                if (growing) {
                    radius += 1;
                    if (radius > 200) growing = false;
                } else {
                    radius -= 1;
                    if (radius < 100) growing = true;
                }

                mask.clear();
                mask.circle(400, 300, radius).fill(0xffffff);
            });
        })();
    </script>
</body>
</html>"""

    js = ""
    return html, js


# Sprite type registry
SPRITE_TYPES: Dict[str, Dict] = {
    'basic': {
        'name': 'Basic Sprite',
        'description': 'Simple rotating sprite with color change on click',
        'generator': generate_basic_sprite
    },
    'interactive': {
        'name': 'Interactive Sprite',
        'description': 'Draggable sprites with hover effects',
        'generator': generate_interactive_sprite
    },
    'animated': {
        'name': 'Animated Sprite',
        'description': 'Sprite sheet animation with playback controls',
        'generator': generate_animated_sprite
    },
    'tiled': {
        'name': 'Tiled Sprite',
        'description': 'Scrolling background with tiling sprite',
        'generator': generate_tiled_sprites
    },
    'atlas': {
        'name': 'Sprite Sheet Atlas',
        'description': 'Multiple sprites from texture atlas',
        'generator': generate_spritesheet_atlas
    },
    'masked': {
        'name': 'Masked Sprite',
        'description': 'Sprite with animated circular mask',
        'generator': generate_masked_sprite
    }
}


def interactive_mode():
    """Run interactive sprite generator"""
    print("\n" + "="*60)
    print("PixiJS Sprite Generator - Interactive Mode")
    print("="*60)

    # Show sprite types
    print("\nAvailable sprite types:")
    print("-" * 60)
    for idx, (key, info) in enumerate(SPRITE_TYPES.items(), 1):
        print(f"{idx}. {info['name']:25} - {info['description']}")

    # Get sprite type
    while True:
        try:
            choice = input(f"\nSelect sprite type (1-{len(SPRITE_TYPES)}): ").strip()
            idx = int(choice)
            if 1 <= idx <= len(SPRITE_TYPES):
                sprite_type = list(SPRITE_TYPES.keys())[idx - 1]
                break
            print(f"Error: Please enter a number between 1 and {len(SPRITE_TYPES)}")
        except ValueError:
            print("Error: Please enter a valid number")

    # Get output directory
    output_dir = input("\nOutput directory (default: current directory): ").strip()
    if not output_dir:
        output_dir = "."

    # Get filename
    filename = input("\nFilename (default: sprite.html): ").strip()
    if not filename:
        filename = "sprite.html"

    if not filename.endswith('.html'):
        filename += '.html'

    # Generate sprite
    print("\n" + "-"*60)
    print("Generating sprite...")

    try:
        generator = SPRITE_TYPES[sprite_type]['generator']
        html, js = generator()

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Write HTML file
        html_path = os.path.join(output_dir, filename)
        with open(html_path, 'w') as f:
            f.write(html)

        print(f"\n✓ Sprite created: {html_path}")
        print(f"\nSprite type: {SPRITE_TYPES[sprite_type]['name']}")
        print(f"Lines of code: {len(html.splitlines())}")

        print("\nTo view:")
        print(f"  Open {html_path} in a web browser")
        print(f"  Or run: python -m http.server 8000")

    except Exception as e:
        print(f"\nError: Failed to generate sprite: {e}")
        return 1

    return 0


def cli_mode(args):
    """Run CLI sprite generator"""
    sprite_type = args.type
    output_dir = args.output
    name = args.name or 'sprite'

    # Validate sprite type
    if sprite_type not in SPRITE_TYPES:
        print(f"Error: Unknown sprite type '{sprite_type}'")
        print(f"Available types: {', '.join(SPRITE_TYPES.keys())}")
        return 1

    # Generate sprite
    try:
        generator = SPRITE_TYPES[sprite_type]['generator']
        html, js = generator()

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Write HTML file
        filename = f"{name}.html"
        html_path = os.path.join(output_dir, filename)

        with open(html_path, 'w') as f:
            f.write(html)

        print(f"✓ Sprite created: {html_path}")
        return 0

    except Exception as e:
        print(f"Error: Failed to generate sprite: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='PixiJS Sprite Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python sprite_generator.py

  Generate basic sprite:
    python sprite_generator.py --type basic --output ./

  Generate interactive sprite:
    python sprite_generator.py -t interactive -o ./my-project/

  Generate animated sprite:
    python sprite_generator.py -t animated --name MyAnimation

Available sprite types:
  basic       - Simple rotating sprite with color change
  interactive - Draggable sprites with hover effects
  animated    - Sprite sheet animation with controls
  tiled       - Scrolling background pattern
  atlas       - Multiple sprites from texture atlas
  masked      - Sprite with animated mask
        """
    )

    parser.add_argument(
        '-t', '--type',
        choices=list(SPRITE_TYPES.keys()),
        help='Sprite type'
    )

    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output directory (default: current directory)'
    )

    parser.add_argument(
        '-n', '--name',
        help='Output filename (default: sprite)'
    )

    args = parser.parse_args()

    # Run interactive mode if no sprite type specified
    if not args.type:
        return interactive_mode()

    return cli_mode(args)


if __name__ == '__main__':
    sys.exit(main())

```


===== FILE: plugins/individual/pixijs-2d/skills/pixijs-2d/assets/examples/README.md =====

# PixiJS Examples and Patterns

Comprehensive real-world examples and patterns for building production-ready PixiJS applications.

## Table of Contents

1. [Basic Applications](#basic-applications)
2. [Interactive Elements](#interactive-elements)
3. [Particle Systems](#particle-systems)
4. [Filters and Effects](#filters-and-effects)
5. [Custom Shaders](#custom-shaders)
6. [Animation Patterns](#animation-patterns)
7. [Performance Optimization](#performance-optimization)
8. [Game Development](#game-development)
9. [UI Components](#ui-components)
10. [Framework Integration](#framework-integration)
11. [Mobile Optimization](#mobile-optimization)
12. [Advanced Techniques](#advanced-techniques)

---

## Basic Applications

### 1. Minimal PixiJS Application

The absolute minimum code to get started with PixiJS v8+:

```javascript
(async () => {
    const app = new PIXI.Application();

    await app.init({
        width: 800,
        height: 600,
        backgroundColor: 0x1099bb
    });

    document.body.appendChild(app.canvas);

    // Create a sprite
    const texture = await PIXI.Assets.load('bunny.png');
    const bunny = new PIXI.Sprite(texture);

    bunny.anchor.set(0.5);
    bunny.position.set(400, 300);

    app.stage.addChild(bunny);

    // Animation loop
    app.ticker.add((ticker) => {
        bunny.rotation += 0.05 * ticker.deltaTime;
    });
})();
```

### 2. Responsive Canvas Application

Canvas that automatically resizes to fill the window:

```javascript
(async () => {
    const app = new PIXI.Application();

    await app.init({
        width: window.innerWidth,
        height: window.innerHeight,
        backgroundColor: 0x1a1a2e,
        antialias: true,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true
    });

    document.body.appendChild(app.canvas);

    // Handle window resize
    window.addEventListener('resize', () => {
        app.renderer.resize(window.innerWidth, window.innerHeight);

        // Reposition elements if needed
        updateLayout();
    });

    function updateLayout() {
        // Center content or adjust layout based on new dimensions
        const centerX = app.screen.width / 2;
        const centerY = app.screen.height / 2;

        // Update element positions...
    }
})();
```

### 3. Asset Loading with Progress

Load multiple assets with loading screen:

```javascript
(async () => {
    const app = new PIXI.Application();
    await app.init({ width: 800, height: 600 });
    document.body.appendChild(app.canvas);

    // Create loading text
    const loadingText = new PIXI.Text({
        text: 'Loading: 0%',
        style: { fontSize: 32, fill: 0xffffff }
    });
    loadingText.anchor.set(0.5);
    loadingText.position.set(400, 300);
    app.stage.addChild(loadingText);

    // Assets to load
    const assets = [
        { alias: 'bunny', src: 'bunny.png' },
        { alias: 'spritesheet', src: 'spritesheet.json' },
        { alias: 'background', src: 'background.jpg' }
    ];

    // Load assets with progress
    PIXI.Assets.load(assets, (progress) => {
        loadingText.text = `Loading: ${Math.round(progress * 100)}%`;
    }).then((textures) => {
        // Remove loading screen
        app.stage.removeChild(loadingText);

        // Start application with loaded assets
        startApp(textures);
    });

    function startApp(textures) {
        const bunny = new PIXI.Sprite(textures.bunny);
        bunny.position.set(400, 300);
        app.stage.addChild(bunny);
    }
})();
```

### 4. Multi-Scene Application

Manage multiple scenes/screens:

```javascript
class SceneManager {
    constructor(app) {
        this.app = app;
        this.scenes = new Map();
        this.currentScene = null;
    }

    addScene(name, scene) {
        this.scenes.set(name, scene);
        scene.visible = false;
        this.app.stage.addChild(scene);
    }

    switchTo(name) {
        if (this.currentScene) {
            this.currentScene.visible = false;
            this.currentScene.onExit?.();
        }

        const scene = this.scenes.get(name);
        if (scene) {
            scene.visible = true;
            scene.onEnter?.();
            this.currentScene = scene;
        }
    }
}

// Usage
(async () => {
    const app = new PIXI.Application();
    await app.init({ width: 800, height: 600 });
    document.body.appendChild(app.canvas);

    const sceneManager = new SceneManager(app);

    // Create scenes
    const menuScene = new PIXI.Container();
    menuScene.onEnter = () => console.log('Entered menu');
    menuScene.onExit = () => console.log('Exited menu');

    const gameScene = new PIXI.Container();
    gameScene.onEnter = () => console.log('Game started');
    gameScene.onExit = () => console.log('Game paused');

    // Add menu content
    const menuText = new PIXI.Text({
        text: 'Main Menu',
        style: { fontSize: 48, fill: 0xffffff }
    });
    menuText.position.set(300, 250);
    menuScene.addChild(menuText);

    const startButton = new PIXI.Text({
        text: 'Start Game',
        style: { fontSize: 32, fill: 0x00ff00 }
    });
    startButton.position.set(320, 350);
    startButton.eventMode = 'static';
    startButton.cursor = 'pointer';
    startButton.on('pointerdown', () => sceneManager.switchTo('game'));
    menuScene.addChild(startButton);

    // Add game content
    const gameText = new PIXI.Text({
        text: 'Game Scene',
        style: { fontSize: 48, fill: 0xffffff }
    });
    gameText.position.set(300, 300);
    gameScene.addChild(gameText);

    // Register scenes
    sceneManager.addScene('menu', menuScene);
    sceneManager.addScene('game', gameScene);

    // Start with menu
    sceneManager.switchTo('menu');
})();
```

---

## Interactive Elements

### 1. Draggable Sprites

Implement drag-and-drop functionality:

```javascript
function makeDraggable(sprite) {
    sprite.eventMode = 'static';
    sprite.cursor = 'pointer';

    let dragData = null;

    sprite.on('pointerdown', (event) => {
        dragData = event.global.clone();
        sprite.alpha = 0.5;
        app.stage.on('pointermove', onDragMove);
    });

    sprite.on('pointerup', onDragEnd);
    sprite.on('pointerupoutside', onDragEnd);

    function onDragMove(event) {
        if (dragData) {
            const newPosition = event.global;
            sprite.x += newPosition.x - dragData.x;
            sprite.y += newPosition.y - dragData.y;
            dragData = newPosition.clone();
        }
    }

    function onDragEnd() {
        if (dragData) {
            sprite.alpha = 1;
            dragData = null;
            app.stage.off('pointermove', onDragMove);
        }
    }
}

// Usage
const sprite = new PIXI.Sprite(texture);
sprite.position.set(100, 100);
app.stage.addChild(sprite);
makeDraggable(sprite);
```

### 2. Hover Effects

Add visual feedback on mouse hover:

```javascript
function addHoverEffect(sprite, options = {}) {
    const {
        hoverScale = 1.2,
        hoverTint = 0xffff00,
        animationSpeed = 0.1
    } = options;

    sprite.eventMode = 'static';
    sprite.cursor = 'pointer';

    const originalScale = sprite.scale.x;
    const originalTint = sprite.tint;

    sprite.on('pointerover', () => {
        animateScale(sprite, hoverScale, animationSpeed);
        sprite.tint = hoverTint;
    });

    sprite.on('pointerout', () => {
        animateScale(sprite, originalScale, animationSpeed);
        sprite.tint = originalTint;
    });
}

function animateScale(sprite, targetScale, speed) {
    const ticker = (delta) => {
        const currentScale = sprite.scale.x;
        const diff = targetScale - currentScale;

        if (Math.abs(diff) < 0.01) {
            sprite.scale.set(targetScale);
            app.ticker.remove(ticker);
        } else {
            const newScale = currentScale + diff * speed * delta.deltaTime;
            sprite.scale.set(newScale);
        }
    };

    app.ticker.add(ticker);
}

// Usage
const sprite = new PIXI.Sprite(texture);
addHoverEffect(sprite, { hoverScale: 1.3, hoverTint: 0x00ff00 });
```

### 3. Button Component

Reusable button with states:

```javascript
class Button extends PIXI.Container {
    constructor(text, options = {}) {
        super();

        const {
            width = 200,
            height = 60,
            backgroundColor = 0x4CAF50,
            hoverColor = 0x45a049,
            textColor = 0xffffff,
            fontSize = 24,
            borderRadius = 10
        } = options;

        // Background
        this.background = new PIXI.Graphics();
        this.drawBackground(backgroundColor, width, height, borderRadius);
        this.addChild(this.background);

        // Text
        this.label = new PIXI.Text({
            text,
            style: {
                fontSize,
                fill: textColor,
                fontWeight: 'bold'
            }
        });
        this.label.anchor.set(0.5);
        this.label.position.set(width / 2, height / 2);
        this.addChild(this.label);

        // Interactive
        this.eventMode = 'static';
        this.cursor = 'pointer';

        // Store colors
        this.normalColor = backgroundColor;
        this.hoverColor = hoverColor;
        this.width = width;
        this.height = height;
        this.borderRadius = borderRadius;

        // Events
        this.on('pointerover', () => {
            this.drawBackground(this.hoverColor, this.width, this.height, this.borderRadius);
        });

        this.on('pointerout', () => {
            this.drawBackground(this.normalColor, this.width, this.height, this.borderRadius);
        });

        this.on('pointerdown', () => {
            this.scale.set(0.95);
        });

        this.on('pointerup', () => {
            this.scale.set(1);
        });
    }

    drawBackground(color, width, height, borderRadius) {
        this.background.clear();
        this.background.roundRect(0, 0, width, height, borderRadius).fill(color);
    }

    setText(text) {
        this.label.text = text;
    }

    onClick(callback) {
        this.on('pointerdown', callback);
        return this;
    }
}

// Usage
const playButton = new Button('Play Game', {
    width: 250,
    height: 70,
    backgroundColor: 0x3498db,
    hoverColor: 0x2980b9
});

playButton.position.set(275, 400);
playButton.onClick(() => {
    console.log('Play button clicked!');
    startGame();
});

app.stage.addChild(playButton);
```

### 4. Click Detection with Shapes

Detect clicks on custom shapes (not just sprites):

```javascript
const graphics = new PIXI.Graphics();
graphics.circle(400, 300, 100).fill(0xff0000);

graphics.eventMode = 'static';
graphics.cursor = 'pointer';
graphics.hitArea = new PIXI.Circle(400, 300, 100);

graphics.on('pointerdown', (event) => {
    console.log('Circle clicked!');
    graphics.tint = Math.random() * 0xffffff;
});

app.stage.addChild(graphics);

// Custom polygon hit area
const star = new PIXI.Graphics();
star.star(400, 300, 5, 50, 25).fill(0xffff00);

star.eventMode = 'static';
star.cursor = 'pointer';

// Define hit area as polygon
const starPoints = [
    400, 250,  // Top
    420, 290,
    460, 300,
    430, 330,
    440, 370,
    400, 350,
    360, 370,
    370, 330,
    340, 300,
    380, 290
];
star.hitArea = new PIXI.Polygon(starPoints);

star.on('pointerdown', () => {
    console.log('Star clicked!');
});

app.stage.addChild(star);
```

---

## Particle Systems

### 1. Basic Particle Emitter

Simple particle emitter with gravity:

```javascript
class ParticleEmitter {
    constructor(app, texture) {
        this.app = app;
        this.texture = texture;
        this.particles = [];
        this.maxParticles = 1000;

        this.container = new PIXI.ParticleContainer(this.maxParticles, {
            position: true,
            rotation: true,
            scale: true,
            tint: true,
            alpha: true
        });

        app.stage.addChild(this.container);

        app.ticker.add((ticker) => this.update(ticker));
    }

    emit(x, y, count = 10) {
        for (let i = 0; i < count; i++) {
            if (this.particles.length >= this.maxParticles) break;

            const particle = new PIXI.Sprite(this.texture);
            particle.anchor.set(0.5);
            particle.position.set(x, y);

            // Random velocity
            particle.vx = (Math.random() - 0.5) * 10;
            particle.vy = -Math.random() * 10;

            // Lifetime
            particle.life = 1.0;
            particle.maxLife = 1.0;

            this.container.addChild(particle);
            this.particles.push(particle);
        }
    }

    update(ticker) {
        const gravity = 0.5;
        const delta = ticker.deltaTime;

        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];

            // Apply physics
            p.vy += gravity * delta;
            p.x += p.vx * delta;
            p.y += p.vy * delta;

            // Update life
            p.life -= 0.02 * delta;
            p.alpha = p.life / p.maxLife;
            p.scale.set(p.alpha);

            // Remove dead particles
            if (p.life <= 0) {
                this.container.removeChild(p);
                p.destroy();
                this.particles.splice(i, 1);
            }
        }
    }
}

// Usage
const particleTexture = createCircleTexture(10, 0xffffff);
const emitter = new ParticleEmitter(app, particleTexture);

// Emit on click
app.stage.eventMode = 'static';
app.stage.on('pointerdown', (event) => {
    emitter.emit(event.global.x, event.global.y, 50);
});

function createCircleTexture(radius, color) {
    const graphics = new PIXI.Graphics();
    graphics.circle(radius, radius, radius).fill(color);
    return app.renderer.generateTexture(graphics);
}
```

### 2. Fire Effect

Realistic fire particle effect:

```javascript
class FireEmitter {
    constructor(app, x, y) {
        this.app = app;
        this.x = x;
        this.y = y;
        this.particles = [];

        this.container = new PIXI.ParticleContainer(2000, {
            position: true,
            scale: true,
            tint: true,
            alpha: true
        });

        app.stage.addChild(this.container);

        // Create particle texture
        const graphics = new PIXI.Graphics();
        graphics.circle(8, 8, 8).fill(0xffffff);
        this.texture = app.renderer.generateTexture(graphics);

        // Emit continuously
        app.ticker.add((ticker) => this.update(ticker));
    }

    update(ticker) {
        const delta = ticker.deltaTime;

        // Emit new particles
        for (let i = 0; i < 5; i++) {
            this.emitParticle();
        }

        // Update existing particles
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];

            // Rise upward with slight horizontal drift
            p.y += p.vy * delta;
            p.x += p.vx * delta;

            // Update life
            p.life -= 0.02 * delta;

            // Color transition: yellow -> orange -> red -> transparent
            const t = 1 - p.life;
            if (t < 0.33) {
                // Yellow to orange
                const localT = t / 0.33;
                p.tint = this.colorLerp(0xffff00, 0xff8800, localT);
            } else if (t < 0.66) {
                // Orange to red
                const localT = (t - 0.33) / 0.33;
                p.tint = this.colorLerp(0xff8800, 0xff0000, localT);
            } else {
                // Red to dark red
                const localT = (t - 0.66) / 0.34;
                p.tint = this.colorLerp(0xff0000, 0x880000, localT);
            }

            p.alpha = p.life;
            p.scale.set(p.life * 1.5);

            // Remove dead particles
            if (p.life <= 0) {
                this.container.removeChild(p);
                p.destroy();
                this.particles.splice(i, 1);
            }
        }
    }

    emitParticle() {
        const particle = new PIXI.Sprite(this.texture);
        particle.anchor.set(0.5);
        particle.position.set(
            this.x + (Math.random() - 0.5) * 20,
            this.y
        );

        particle.vx = (Math.random() - 0.5) * 2;
        particle.vy = -2 - Math.random() * 3;
        particle.life = 1.0;

        this.container.addChild(particle);
        this.particles.push(particle);
    }

    colorLerp(color1, color2, t) {
        const r1 = (color1 >> 16) & 0xff;
        const g1 = (color1 >> 8) & 0xff;
        const b1 = color1 & 0xff;

        const r2 = (color2 >> 16) & 0xff;
        const g2 = (color2 >> 8) & 0xff;
        const b2 = color2 & 0xff;

        const r = Math.floor(r1 + (r2 - r1) * t);
        const g = Math.floor(g1 + (g2 - g1) * t);
        const b = Math.floor(b1 + (b2 - b1) * t);

        return (r << 16) | (g << 8) | b;
    }
}

// Usage
const fireEmitter = new FireEmitter(app, 400, 500);
```

### 3. Trail Effect

Create motion trails behind moving objects:

```javascript
class TrailEffect {
    constructor(app, target, options = {}) {
        this.app = app;
        this.target = target;
        this.trailSegments = [];
        this.maxSegments = options.maxSegments || 20;
        this.segmentLife = options.segmentLife || 0.5;

        this.container = new PIXI.Container();
        app.stage.addChildAt(this.container, 0);  // Behind target

        app.ticker.add((ticker) => this.update(ticker));
    }

    update(ticker) {
        const delta = ticker.deltaTime;

        // Create new segment at target position
        const segment = new PIXI.Graphics();
        segment.circle(0, 0, this.target.width / 2).fill(this.target.tint);
        segment.position.set(this.target.x, this.target.y);
        segment.life = this.segmentLife;
        segment.maxLife = this.segmentLife;

        this.container.addChild(segment);
        this.trailSegments.push(segment);

        // Remove old segments
        if (this.trailSegments.length > this.maxSegments) {
            const old = this.trailSegments.shift();
            this.container.removeChild(old);
            old.destroy();
        }

        // Update existing segments
        for (const seg of this.trailSegments) {
            seg.life -= 0.016 * delta;
            seg.alpha = seg.life / seg.maxLife;
        }
    }

    destroy() {
        for (const seg of this.trailSegments) {
            seg.destroy();
        }
        this.container.destroy();
    }
}

// Usage
const sprite = new PIXI.Sprite(texture);
sprite.anchor.set(0.5);
sprite.position.set(400, 300);
app.stage.addChild(sprite);

const trail = new TrailEffect(app, sprite, {
    maxSegments: 30,
    segmentLife: 0.8
});

// Move sprite with mouse
app.stage.eventMode = 'static';
app.stage.on('pointermove', (event) => {
    sprite.position.set(event.global.x, event.global.y);
});
```

### 4. Explosion Effect

One-shot explosion particle effect:

```javascript
class Explosion {
    constructor(app, x, y, particleCount = 50) {
        this.app = app;
        this.particles = [];

        const graphics = new PIXI.Graphics();
        graphics.circle(5, 5, 5).fill(0xffffff);
        const texture = app.renderer.generateTexture(graphics);

        const container = new PIXI.ParticleContainer(particleCount, {
            position: true,
            rotation: true,
            scale: true,
            tint: true,
            alpha: true
        });

        app.stage.addChild(container);

        // Create particles
        for (let i = 0; i < particleCount; i++) {
            const angle = (Math.PI * 2 * i) / particleCount;
            const speed = 5 + Math.random() * 5;

            const particle = new PIXI.Sprite(texture);
            particle.anchor.set(0.5);
            particle.position.set(x, y);
            particle.vx = Math.cos(angle) * speed;
            particle.vy = Math.sin(angle) * speed;
            particle.life = 1.0;
            particle.tint = Math.random() > 0.5 ? 0xff8800 : 0xffff00;

            container.addChild(particle);
            this.particles.push(particle);
        }

        // Update and cleanup
        const ticker = (delta) => {
            let allDead = true;

            for (const p of this.particles) {
                p.x += p.vx * delta.deltaTime;
                p.y += p.vy * delta.deltaTime;
                p.vy += 0.3 * delta.deltaTime;  // Gravity

                p.life -= 0.02 * delta.deltaTime;
                p.alpha = p.life;
                p.scale.set(p.life);

                if (p.life > 0) allDead = false;
            }

            if (allDead) {
                app.ticker.remove(ticker);
                container.destroy({ children: true });
            }
        };

        app.ticker.add(ticker);
    }
}

// Usage - trigger on click
app.stage.eventMode = 'static';
app.stage.on('pointerdown', (event) => {
    new Explosion(app, event.global.x, event.global.y, 100);
});
```

---

## Filters and Effects

### 1. Glow Effect

Add glowing outline to sprites:

```javascript
import { BlurFilter, ColorMatrixFilter } from 'pixi.js';

function addGlowEffect(sprite, options = {}) {
    const {
        glowColor = [1, 1, 0],  // Yellow
        glowStrength = 2,
        blurStrength = 10
    } = options;

    // Create blur filter
    const blurFilter = new BlurFilter();
    blurFilter.strength = blurStrength;

    // Create color filter for glow
    const colorFilter = new ColorMatrixFilter();
    colorFilter.brightness(glowStrength, false);

    // Apply filters
    sprite.filters = [blurFilter, colorFilter];

    return { blurFilter, colorFilter };
}

// Usage
const sprite = new PIXI.Sprite(texture);
sprite.position.set(400, 300);
app.stage.addChild(sprite);

const glow = addGlowEffect(sprite, {
    glowColor: [0, 1, 1],  // Cyan
    glowStrength: 3,
    blurStrength: 15
});

// Animate glow intensity
let time = 0;
app.ticker.add((ticker) => {
    time += 0.05 * ticker.deltaTime;
    const intensity = Math.sin(time) * 0.5 + 1.5;
    glow.blurFilter.strength = 10 + intensity * 5;
});
```

### 2. Chromatic Aberration

RGB color separation effect:

```javascript
import { Filter, GlProgram } from 'pixi.js';

class ChromaticAberrationFilter extends Filter {
    constructor(offset = 5) {
        const fragment = `
            in vec2 vTextureCoord;
            uniform sampler2D uTexture;
            uniform vec2 uOffset;

            out vec4 finalColor;

            void main() {
                vec2 coord = vTextureCoord;
                float r = texture(uTexture, coord + uOffset).r;
                float g = texture(uTexture, coord).g;
                float b = texture(uTexture, coord - uOffset).b;
                float a = texture(uTexture, coord).a;

                finalColor = vec4(r, g, b, a);
            }
        `;

        super({
            glProgram: new GlProgram({
                fragment,
                vertex: GlProgram.defaultVertexSrc
            }),
            resources: {
                chromaUniforms: {
                    uOffset: {
                        value: new Float32Array([offset / 800, 0]),
                        type: 'vec2<f32>'
                    }
                }
            }
        });
    }

    set offset(value) {
        this.resources.chromaUniforms.uniforms.uOffset[0] = value / 800;
    }
}

// Usage
const sprite = new PIXI.Sprite(texture);
sprite.position.set(400, 300);
app.stage.addChild(sprite);

const chromaFilter = new ChromaticAberrationFilter(10);
sprite.filters = [chromaFilter];

// Animate offset
let time = 0;
app.ticker.add((ticker) => {
    time += 0.1 * ticker.deltaTime;
    chromaFilter.offset = Math.sin(time) * 20;
});
```

### 3. CRT Monitor Effect

Old-school CRT screen effect with scanlines and curvature:

```javascript
class CRTFilter extends Filter {
    constructor() {
        const fragment = `
            in vec2 vTextureCoord;
            uniform sampler2D uTexture;
            uniform float uTime;

            out vec4 finalColor;

            void main() {
                vec2 uv = vTextureCoord;

                // Screen curvature
                vec2 dc = uv - 0.5;
                float dist = dot(dc, dc);
                uv = uv + dc * dist * 0.1;

                // Scanlines
                float scanline = sin(uv.y * 800.0) * 0.04;

                // Vignette
                float vignette = 1.0 - dist * 1.5;

                // Color aberration on edges
                float r = texture(uTexture, uv + vec2(0.001, 0.0)).r;
                float g = texture(uTexture, uv).g;
                float b = texture(uTexture, uv - vec2(0.001, 0.0)).b;

                vec3 color = vec3(r, g, b);
                color -= scanline;
                color *= vignette;

                // Flicker
                color *= 0.95 + 0.05 * sin(uTime * 100.0);

                finalColor = vec4(color, 1.0);
            }
        `;

        super({
            glProgram: new GlProgram({
                fragment,
                vertex: GlProgram.defaultVertexSrc
            }),
            resources: {
                crtUniforms: {
                    uTime: { value: 0, type: 'f32' }
                }
            }
        });

        this.time = 0;
    }

    update(deltaTime) {
        this.time += deltaTime * 0.016;
        this.resources.crtUniforms.uniforms.uTime = this.time;
    }
}

// Usage
const crtFilter = new CRTFilter();
app.stage.filters = [crtFilter];

app.ticker.add((ticker) => {
    crtFilter.update(ticker.deltaTime);
});
```

### 4. Displacement Map Effect

Create water ripple or distortion effects:

```javascript
import { DisplacementFilter } from 'pixi.js';

(async () => {
    // Create displacement sprite
    const displacementSprite = PIXI.Sprite.from('displacement_map.png');
    displacementSprite.texture.baseTexture.wrapMode = PIXI.WRAP_MODES.REPEAT;

    // Create displacement filter
    const displacementFilter = new DisplacementFilter({
        sprite: displacementSprite,
        scale: 50
    });

    // Apply to stage or specific sprite
    app.stage.filters = [displacementFilter];

    // Animate displacement
    app.ticker.add((ticker) => {
        displacementSprite.x += 1 * ticker.deltaTime;
        displacementSprite.y += 0.5 * ticker.deltaTime;
    });
})();

// Generate displacement map programmatically
function createDisplacementMap(size = 512) {
    const graphics = new PIXI.Graphics();

    for (let i = 0; i < 50; i++) {
        const x = Math.random() * size;
        const y = Math.random() * size;
        const radius = Math.random() * 50 + 20;

        graphics.circle(x, y, radius)
            .fill({ color: 0xffffff, alpha: Math.random() * 0.5 });
    }

    const texture = app.renderer.generateTexture(graphics, {
        resolution: 1,
        multisample: PIXI.MSAA_QUALITY.NONE
    });

    return PIXI.Sprite.from(texture);
}
```

---

## Custom Shaders

### 1. Wave Distortion Shader

Create animated wave distortion:

```javascript
import { Filter, GlProgram } from 'pixi.js';

class WaveFilter extends Filter {
    constructor() {
        const fragment = `
            in vec2 vTextureCoord;
            uniform sampler2D uTexture;
            uniform float uTime;
            uniform float uAmplitude;
            uniform float uFrequency;

            out vec4 finalColor;

            void main() {
                vec2 coord = vTextureCoord;

                // Apply wave distortion
                coord.x += sin(coord.y * uFrequency + uTime) * uAmplitude;
                coord.y += cos(coord.x * uFrequency + uTime) * uAmplitude;

                finalColor = texture(uTexture, coord);
            }
        `;

        super({
            glProgram: new GlProgram({
                fragment,
                vertex: GlProgram.defaultVertexSrc
            }),
            resources: {
                waveUniforms: {
                    uTime: { value: 0, type: 'f32' },
                    uAmplitude: { value: 0.01, type: 'f32' },
                    uFrequency: { value: 10.0, type: 'f32' }
                }
            }
        });
    }

    set time(value) {
        this.resources.waveUniforms.uniforms.uTime = value;
    }

    set amplitude(value) {
        this.resources.waveUniforms.uniforms.uAmplitude = value;
    }

    set frequency(value) {
        this.resources.waveUniforms.uniforms.uFrequency = value;
    }
}

// Usage
const sprite = new PIXI.Sprite(texture);
sprite.position.set(400, 300);
app.stage.addChild(sprite);

const waveFilter = new WaveFilter();
sprite.filters = [waveFilter];

let time = 0;
app.ticker.add((ticker) => {
    time += 0.05 * ticker.deltaTime;
    waveFilter.time = time;
});
```

### 2. Pixelate Shader

Dynamic pixelation effect:

```javascript
class PixelateFilter extends Filter {
    constructor(pixelSize = 10) {
        const fragment = `
            in vec2 vTextureCoord;
            uniform sampler2D uTexture;
            uniform vec2 uSize;
            uniform float uPixelSize;

            out vec4 finalColor;

            void main() {
                vec2 coord = vTextureCoord * uSize;
                vec2 pixelCoord = floor(coord / uPixelSize) * uPixelSize;
                vec2 pixelUV = pixelCoord / uSize;

                finalColor = texture(uTexture, pixelUV);
            }
        `;

        super({
            glProgram: new GlProgram({
                fragment,
                vertex: GlProgram.defaultVertexSrc
            }),
            resources: {
                pixelateUniforms: {
                    uSize: {
                        value: new Float32Array([800, 600]),
                        type: 'vec2<f32>'
                    },
                    uPixelSize: { value: pixelSize, type: 'f32' }
                }
            }
        });
    }

    set pixelSize(value) {
        this.resources.pixelateUniforms.uniforms.uPixelSize = value;
    }

    setSize(width, height) {
        this.resources.pixelateUniforms.uniforms.uSize[0] = width;
        this.resources.pixelateUniforms.uniforms.uSize[1] = height;
    }
}

// Usage with animated pixelation
const pixelateFilter = new PixelateFilter(1);
app.stage.filters = [pixelateFilter];

let pixelSize = 1;
let direction = 1;

app.ticker.add(() => {
    pixelSize += direction * 0.5;

    if (pixelSize >= 20) direction = -1;
    if (pixelSize <= 1) direction = 1;

    pixelateFilter.pixelSize = pixelSize;
});
```

### 3. Color Grading Shader

Professional color grading with adjustable parameters:

```javascript
class ColorGradingFilter extends Filter {
    constructor(options = {}) {
        const {
            brightness = 0,
            contrast = 0,
            saturation = 0,
            temperature = 0
        } = options;

        const fragment = `
            in vec2 vTextureCoord;
            uniform sampler2D uTexture;
            uniform float uBrightness;
            uniform float uContrast;
            uniform float uSaturation;
            uniform float uTemperature;

            out vec4 finalColor;

            void main() {
                vec4 color = texture(uTexture, vTextureCoord);

                // Brightness
                color.rgb += uBrightness;

                // Contrast
                color.rgb = (color.rgb - 0.5) * (1.0 + uContrast) + 0.5;

                // Saturation
                float gray = dot(color.rgb, vec3(0.299, 0.587, 0.114));
                color.rgb = mix(vec3(gray), color.rgb, 1.0 + uSaturation);

                // Temperature (blue/orange tint)
                color.r += uTemperature * 0.1;
                color.b -= uTemperature * 0.1;

                finalColor = color;
            }
        `;

        super({
            glProgram: new GlProgram({
                fragment,
                vertex: GlProgram.defaultVertexSrc
            }),
            resources: {
                colorGradingUniforms: {
                    uBrightness: { value: brightness, type: 'f32' },
                    uContrast: { value: contrast, type: 'f32' },
                    uSaturation: { value: saturation, type: 'f32' },
                    uTemperature: { value: temperature, type: 'f32' }
                }
            }
        });
    }

    set brightness(value) {
        this.resources.colorGradingUniforms.uniforms.uBrightness = value;
    }

    set contrast(value) {
        this.resources.colorGradingUniforms.uniforms.uContrast = value;
    }

    set saturation(value) {
        this.resources.colorGradingUniforms.uniforms.uSaturation = value;
    }

    set temperature(value) {
        this.resources.colorGradingUniforms.uniforms.uTemperature = value;
    }
}

// Usage with UI controls
const colorFilter = new ColorGradingFilter({
    brightness: 0.1,
    contrast: 0.2,
    saturation: 0.3,
    temperature: 0.5
});

app.stage.filters = [colorFilter];

// Interactive controls
document.getElementById('brightness').addEventListener('input', (e) => {
    colorFilter.brightness = parseFloat(e.target.value);
});

document.getElementById('contrast').addEventListener('input', (e) => {
    colorFilter.contrast = parseFloat(e.target.value);
});
```

### 4. Outline Shader

Add colored outline to sprites:

```javascript
class OutlineFilter extends Filter {
    constructor(thickness = 2, color = 0xffffff) {
        const fragment = `
            in vec2 vTextureCoord;
            uniform sampler2D uTexture;
            uniform vec2 uTextureSize;
            uniform float uThickness;
            uniform vec3 uOutlineColor;

            out vec4 finalColor;

            void main() {
                vec2 pixelSize = 1.0 / uTextureSize;

                // Sample surrounding pixels
                float alpha = 0.0;
                for (float x = -uThickness; x <= uThickness; x++) {
                    for (float y = -uThickness; y <= uThickness; y++) {
                        vec2 offset = vec2(x, y) * pixelSize;
                        alpha = max(alpha, texture(uTexture, vTextureCoord + offset).a);
                    }
                }

                vec4 original = texture(uTexture, vTextureCoord);

                // If pixel is transparent but surrounded by opaque, it's an outline
                if (original.a < 0.5 && alpha > 0.5) {
                    finalColor = vec4(uOutlineColor, 1.0);
                } else {
                    finalColor = original;
                }
            }
        `;

        super({
            glProgram: new GlProgram({
                fragment,
                vertex: GlProgram.defaultVertexSrc
            }),
            resources: {
                outlineUniforms: {
                    uTextureSize: {
                        value: new Float32Array([256, 256]),
                        type: 'vec2<f32>'
                    },
                    uThickness: { value: thickness, type: 'f32' },
                    uOutlineColor: {
                        value: new Float32Array([
                            ((color >> 16) & 0xff) / 255,
                            ((color >> 8) & 0xff) / 255,
                            (color & 0xff) / 255
                        ]),
                        type: 'vec3<f32>'
                    }
                }
            }
        });
    }

    set thickness(value) {
        this.resources.outlineUniforms.uniforms.uThickness = value;
    }

    set color(value) {
        this.resources.outlineUniforms.uniforms.uOutlineColor[0] = ((value >> 16) & 0xff) / 255;
        this.resources.outlineUniforms.uniforms.uOutlineColor[1] = ((value >> 8) & 0xff) / 255;
        this.resources.outlineUniforms.uniforms.uOutlineColor[2] = (value & 0xff) / 255;
    }
}

// Usage
const sprite = new PIXI.Sprite(texture);
sprite.position.set(400, 300);
app.stage.addChild(sprite);

const outlineFilter = new OutlineFilter(3, 0xffff00);
sprite.filters = [outlineFilter];

// Animate outline color
let hue = 0;
app.ticker.add(() => {
    hue = (hue + 1) % 360;
    outlineFilter.color = hslToHex(hue, 100, 50);
});

function hslToHex(h, s, l) {
    l /= 100;
    const a = s * Math.min(l, 1 - l) / 100;
    const f = n => {
        const k = (n + h / 30) % 12;
        const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
        return Math.round(255 * color);
    };
    return (f(0) << 16) | (f(8) << 8) | f(4);
}
```

---

## Animation Patterns

### 1. Sprite Sheet Animation

Load and play sprite sheet animations:

```javascript
(async () => {
    // Load sprite sheet
    await PIXI.Assets.load('spritesheet.json');

    // Get animation frames
    const frames = [];
    for (let i = 0; i < 30; i++) {
        frames.push(PIXI.Texture.from(`run_${i}.png`));
    }

    // Create animated sprite
    const animatedSprite = new PIXI.AnimatedSprite(frames);
    animatedSprite.anchor.set(0.5);
    animatedSprite.position.set(400, 300);
    animatedSprite.animationSpeed = 0.5;
    animatedSprite.play();

    app.stage.addChild(animatedSprite);

    // Control playback
    document.getElementById('play').addEventListener('click', () => {
        animatedSprite.play();
    });

    document.getElementById('pause').addEventListener('click', () => {
        animatedSprite.stop();
    });

    document.getElementById('speed').addEventListener('input', (e) => {
        animatedSprite.animationSpeed = parseFloat(e.target.value);
    });
})();
```

### 2. Tweening Library Integration (GSAP)

Smooth animations with GSAP:

```javascript
import gsap from 'gsap';
import { PixiPlugin } from 'gsap/PixiPlugin';

// Register PIXI plugin
gsap.registerPlugin(PixiPlugin);
PixiPlugin.registerPIXI(PIXI);

// Create sprite
const sprite = new PIXI.Sprite(texture);
sprite.anchor.set(0.5);
sprite.position.set(100, 300);
app.stage.addChild(sprite);

// Animate with GSAP
gsap.to(sprite, {
    pixi: {
        x: 700,
        rotation: 360,
        scale: 1.5,
        tint: 0xff0000
    },
    duration: 2,
    ease: 'elastic.out(1, 0.5)',
    onComplete: () => {
        console.log('Animation complete!');
    }
});

// Complex timeline
const timeline = gsap.timeline({ repeat: -1, yoyo: true });

timeline
    .to(sprite, { pixi: { y: 100 }, duration: 1, ease: 'power2.out' })
    .to(sprite, { pixi: { x: 700 }, duration: 1, ease: 'power2.inOut' })
    .to(sprite, { pixi: { y: 500 }, duration: 1, ease: 'power2.in' })
    .to(sprite, { pixi: { x: 100 }, duration: 1, ease: 'power2.inOut' });
```

### 3. Custom Easing Functions

Implement custom easing without external libraries:

```javascript
class Tween {
    constructor(target, to, duration, easing = 'linear') {
        this.target = target;
        this.from = {};
        this.to = to;
        this.duration = duration;
        this.elapsed = 0;
        this.easing = this.easingFunctions[easing] || this.easingFunctions.linear;
        this.complete = false;
        this.onCompleteCallback = null;

        // Store starting values
        for (const key in to) {
            this.from[key] = target[key];
        }
    }

    easingFunctions = {
        linear: t => t,
        easeInQuad: t => t * t,
        easeOutQuad: t => t * (2 - t),
        easeInOutQuad: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
        easeInCubic: t => t * t * t,
        easeOutCubic: t => (--t) * t * t + 1,
        easeInOutCubic: t => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
        elastic: t => {
            if (t === 0 || t === 1) return t;
            const p = 0.3;
            return -Math.pow(2, 10 * (t - 1)) * Math.sin(((t - 1 - p / 4) * (2 * Math.PI)) / p);
        },
        bounce: t => {
            if (t < 1 / 2.75) {
                return 7.5625 * t * t;
            } else if (t < 2 / 2.75) {
                return 7.5625 * (t -= 1.5 / 2.75) * t + 0.75;
            } else if (t < 2.5 / 2.75) {
                return 7.5625 * (t -= 2.25 / 2.75) * t + 0.9375;
            } else {
                return 7.5625 * (t -= 2.625 / 2.75) * t + 0.984375;
            }
        }
    };

    update(deltaTime) {
        if (this.complete) return;

        this.elapsed += deltaTime;
        const progress = Math.min(this.elapsed / this.duration, 1);
        const easedProgress = this.easing(progress);

        // Update target properties
        for (const key in this.to) {
            const from = this.from[key];
            const to = this.to[key];
            this.target[key] = from + (to - from) * easedProgress;
        }

        // Check completion
        if (progress >= 1) {
            this.complete = true;
            if (this.onCompleteCallback) {
                this.onCompleteCallback();
            }
        }
    }

    onComplete(callback) {
        this.onCompleteCallback = callback;
        return this;
    }
}

// Tween manager
class TweenManager {
    constructor(app) {
        this.app = app;
        this.tweens = [];

        app.ticker.add((ticker) => this.update(ticker.deltaTime));
    }

    to(target, to, duration, easing) {
        const tween = new Tween(target, to, duration, easing);
        this.tweens.push(tween);
        return tween;
    }

    update(deltaTime) {
        for (let i = this.tweens.length - 1; i >= 0; i--) {
            const tween = this.tweens[i];
            tween.update(deltaTime * 0.016);  // Convert to seconds

            if (tween.complete) {
                this.tweens.splice(i, 1);
            }
        }
    }
}

// Usage
const tweenManager = new TweenManager(app);

const sprite = new PIXI.Sprite(texture);
sprite.position.set(100, 300);
app.stage.addChild(sprite);

tweenManager
    .to(sprite.position, { x: 700 }, 2, 'elastic')
    .onComplete(() => {
        console.log('Move complete!');

        tweenManager
            .to(sprite, { rotation: Math.PI * 2 }, 1, 'easeOutCubic')
            .onComplete(() => {
                console.log('Rotation complete!');
            });
    });
```

### 4. Path Following Animation

Make sprites follow curved paths:

```javascript
class PathFollower {
    constructor(sprite, path, duration) {
        this.sprite = sprite;
        this.path = path;  // Array of {x, y} points
        this.duration = duration;
        this.elapsed = 0;
    }

    update(deltaTime) {
        this.elapsed += deltaTime;
        const progress = Math.min(this.elapsed / this.duration, 1);

        // Get position along path
        const position = this.getPositionAtProgress(progress);
        this.sprite.position.set(position.x, position.y);

        // Get rotation based on direction
        if (progress < 1) {
            const futureProgress = Math.min(progress + 0.01, 1);
            const futurePosition = this.getPositionAtProgress(futureProgress);
            const angle = Math.atan2(
                futurePosition.y - position.y,
                futurePosition.x - position.x
            );
            this.sprite.rotation = angle;
        }

        return progress >= 1;
    }

    getPositionAtProgress(t) {
        // Catmull-Rom spline interpolation
        const points = this.path;
        const segmentCount = points.length - 1;
        const segment = Math.floor(t * segmentCount);
        const localT = (t * segmentCount) - segment;

        const p0 = points[Math.max(0, segment - 1)];
        const p1 = points[segment];
        const p2 = points[Math.min(points.length - 1, segment + 1)];
        const p3 = points[Math.min(points.length - 1, segment + 2)];

        const t2 = localT * localT;
        const t3 = t2 * localT;

        const x = 0.5 * (
            (2 * p1.x) +
            (-p0.x + p2.x) * localT +
            (2 * p0.x - 5 * p1.x + 4 * p2.x - p3.x) * t2 +
            (-p0.x + 3 * p1.x - 3 * p2.x + p3.x) * t3
        );

        const y = 0.5 * (
            (2 * p1.y) +
            (-p0.y + p2.y) * localT +
            (2 * p0.y - 5 * p1.y + 4 * p2.y - p3.y) * t2 +
            (-p0.y + 3 * p1.y - 3 * p2.y + p3.y) * t3
        );

        return { x, y };
    }
}

// Usage
const sprite = new PIXI.Sprite(texture);
sprite.anchor.set(0.5);
app.stage.addChild(sprite);

const path = [
    { x: 100, y: 300 },
    { x: 300, y: 100 },
    { x: 500, y: 300 },
    { x: 700, y: 500 },
    { x: 400, y: 550 }
];

const pathFollower = new PathFollower(sprite, path, 5000);

app.ticker.add((ticker) => {
    const complete = pathFollower.update(ticker.deltaTime * 16);
    if (complete) {
        console.log('Path complete!');
    }
});

// Visualize path
const graphics = new PIXI.Graphics();
graphics.moveTo(path[0].x, path[0].y);
for (let i = 1; i < path.length; i++) {
    graphics.lineTo(path[i].x, path[i].y);
}
graphics.stroke({ width: 2, color: 0xffffff, alpha: 0.3 });
app.stage.addChild(graphics);
```

---

## Performance Optimization

### 1. Object Pooling System

Reuse objects to avoid garbage collection:

```javascript
class ObjectPool {
    constructor(createFunc, resetFunc, initialSize = 100) {
        this.createFunc = createFunc;
        this.resetFunc = resetFunc;
        this.available = [];
        this.active = new Set();

        // Pre-create objects
        for (let i = 0; i < initialSize; i++) {
            this.available.push(this.createFunc());
        }
    }

    acquire() {
        let obj;

        if (this.available.length > 0) {
            obj = this.available.pop();
        } else {
            obj = this.createFunc();
            console.warn('Pool exhausted, creating new object');
        }

        this.active.add(obj);
        return obj;
    }

    release(obj) {
        if (this.active.has(obj)) {
            this.active.delete(obj);
            this.resetFunc(obj);
            this.available.push(obj);
        }
    }

    releaseAll() {
        for (const obj of this.active) {
            this.resetFunc(obj);
            this.available.push(obj);
        }
        this.active.clear();
    }

    getStats() {
        return {
            available: this.available.length,
            active: this.active.size,
            total: this.available.length + this.active.size
        };
    }
}

// Usage
const texture = await PIXI.Assets.load('bullet.png');

const bulletPool = new ObjectPool(
    // Create function
    () => {
        const bullet = new PIXI.Sprite(texture);
        bullet.anchor.set(0.5);
        return bullet;
    },
    // Reset function
    (bullet) => {
        bullet.visible = false;
        bullet.position.set(0, 0);
        bullet.rotation = 0;
    },
    50  // Initial size
);

// Shoot bullet
function shootBullet(x, y, angle) {
    const bullet = bulletPool.acquire();
    bullet.position.set(x, y);
    bullet.rotation = angle;
    bullet.visible = true;
    bullet.vx = Math.cos(angle) * 5;
    bullet.vy = Math.sin(angle) * 5;
    app.stage.addChild(bullet);
}

// Update bullets
app.ticker.add((ticker) => {
    for (const bullet of bulletPool.active) {
        bullet.x += bullet.vx * ticker.deltaTime;
        bullet.y += bullet.vy * ticker.deltaTime;

        // Release off-screen bullets
        if (bullet.x < 0 || bullet.x > 800 || bullet.y < 0 || bullet.y > 600) {
            app.stage.removeChild(bullet);
            bulletPool.release(bullet);
        }
    }
});

// Monitor pool
setInterval(() => {
    console.log('Bullet pool:', bulletPool.getStats());
}, 1000);
```

### 2. Viewport Culling

Only render visible sprites:

```javascript
class ViewportCuller {
    constructor(app, margin = 100) {
        this.app = app;
        this.margin = margin;
        this.trackedSprites = new Set();
    }

    track(sprite) {
        this.trackedSprites.add(sprite);
    }

    untrack(sprite) {
        this.trackedSprites.delete(sprite);
    }

    update() {
        const bounds = {
            left: -this.margin,
            right: this.app.screen.width + this.margin,
            top: -this.margin,
            bottom: this.app.screen.height + this.margin
        };

        for (const sprite of this.trackedSprites) {
            const spriteBounds = sprite.getBounds();

            const visible = (
                spriteBounds.x + spriteBounds.width >= bounds.left &&
                spriteBounds.x <= bounds.right &&
                spriteBounds.y + spriteBounds.height >= bounds.top &&
                spriteBounds.y <= bounds.bottom
            );

            sprite.renderable = visible;
        }
    }
}

// Usage
const culler = new ViewportCuller(app, 50);

// Create many sprites
for (let i = 0; i < 1000; i++) {
    const sprite = new PIXI.Sprite(texture);
    sprite.x = Math.random() * 2000 - 500;
    sprite.y = Math.random() * 2000 - 500;
    app.stage.addChild(sprite);
    culler.track(sprite);
}

app.ticker.add(() => {
    culler.update();
});

// Camera/viewport movement
let cameraX = 0;
let cameraY = 0;

window.addEventListener('keydown', (e) => {
    const speed = 10;
    switch (e.key) {
        case 'ArrowLeft': cameraX += speed; break;
        case 'ArrowRight': cameraX -= speed; break;
        case 'ArrowUp': cameraY += speed; break;
        case 'ArrowDown': cameraY -= speed; break;
    }

    app.stage.position.set(cameraX, cameraY);
});
```

### 3. Texture Atlases

Combine multiple textures into one for reduced draw calls:

```javascript
// Generate texture atlas programmatically
class TextureAtlas {
    constructor(app, textures, padding = 2) {
        this.app = app;
        this.textures = textures;
        this.padding = padding;
        this.atlas = null;
        this.frames = {};

        this.generate();
    }

    generate() {
        // Calculate atlas size using bin packing
        const rects = Object.entries(this.textures).map(([name, texture]) => ({
            name,
            width: texture.width + this.padding * 2,
            height: texture.height + this.padding * 2,
            texture
        }));

        // Sort by height (descending) for better packing
        rects.sort((a, b) => b.height - a.height);

        // Simple shelf packing algorithm
        let atlasWidth = 0;
        let atlasHeight = 0;
        let shelfY = 0;
        let shelfX = 0;
        let shelfHeight = 0;

        const packed = [];

        for (const rect of rects) {
            // Check if we need a new shelf
            if (shelfX + rect.width > 2048) {  // Max texture size
                shelfY += shelfHeight;
                shelfX = 0;
                shelfHeight = 0;
            }

            rect.x = shelfX + this.padding;
            rect.y = shelfY + this.padding;

            shelfX += rect.width;
            shelfHeight = Math.max(shelfHeight, rect.height);

            atlasWidth = Math.max(atlasWidth, shelfX);
            atlasHeight = Math.max(atlasHeight, shelfY + shelfHeight);

            packed.push(rect);
        }

        // Round up to power of 2
        atlasWidth = Math.pow(2, Math.ceil(Math.log2(atlasWidth)));
        atlasHeight = Math.pow(2, Math.ceil(Math.log2(atlasHeight)));

        // Create canvas for atlas
        const canvas = document.createElement('canvas');
        canvas.width = atlasWidth;
        canvas.height = atlasHeight;
        const ctx = canvas.getContext('2d');

        // Draw all textures to canvas
        for (const rect of packed) {
            const source = rect.texture.source;
            ctx.drawImage(
                source.resource,
                rect.x,
                rect.y,
                rect.texture.width,
                rect.texture.height
            );

            // Store frame data
            this.frames[rect.name] = {
                x: rect.x,
                y: rect.y,
                width: rect.texture.width,
                height: rect.texture.height
            };
        }

        // Create PixiJS texture from canvas
        this.atlas = PIXI.Texture.from(canvas);
    }

    getFrame(name) {
        const frame = this.frames[name];
        if (!frame) return null;

        return new PIXI.Texture({
            source: this.atlas.source,
            frame: new PIXI.Rectangle(frame.x, frame.y, frame.width, frame.height)
        });
    }
}

// Usage
const textures = {
    'player': await PIXI.Assets.load('player.png'),
    'enemy': await PIXI.Assets.load('enemy.png'),
    'bullet': await PIXI.Assets.load('bullet.png'),
    'powerup': await PIXI.Assets.load('powerup.png')
};

const atlas = new TextureAtlas(app, textures);

// Use frames from atlas
const player = new PIXI.Sprite(atlas.getFrame('player'));
const enemy = new PIXI.Sprite(atlas.getFrame('enemy'));

// All sprites now share one texture = one draw call!
```

### 4. Spatial Hashing for Collisions

Optimize collision detection from O(n²) to O(n):

```javascript
class SpatialHash {
    constructor(cellSize = 100) {
        this.cellSize = cellSize;
        this.cells = new Map();
    }

    clear() {
        this.cells.clear();
    }

    insert(obj) {
        const bounds = obj.getBounds();
        const cells = this.getCellsForBounds(bounds);

        for (const cellKey of cells) {
            if (!this.cells.has(cellKey)) {
                this.cells.set(cellKey, new Set());
            }
            this.cells.get(cellKey).add(obj);
        }
    }

    getCellsForBounds(bounds) {
        const cells = [];

        const minX = Math.floor(bounds.x / this.cellSize);
        const maxX = Math.floor((bounds.x + bounds.width) / this.cellSize);
        const minY = Math.floor(bounds.y / this.cellSize);
        const maxY = Math.floor((bounds.y + bounds.height) / this.cellSize);

        for (let x = minX; x <= maxX; x++) {
            for (let y = minY; y <= maxY; y++) {
                cells.push(`${x},${y}`);
            }
        }

        return cells;
    }

    getNearby(obj) {
        const bounds = obj.getBounds();
        const cells = this.getCellsForBounds(bounds);
        const nearby = new Set();

        for (const cellKey of cells) {
            const cell = this.cells.get(cellKey);
            if (cell) {
                for (const other of cell) {
                    if (other !== obj) {
                        nearby.add(other);
                    }
                }
            }
        }

        return nearby;
    }
}

// Usage
const spatialHash = new SpatialHash(100);
const sprites = [];

// Create many sprites
for (let i = 0; i < 500; i++) {
    const sprite = new PIXI.Sprite(texture);
    sprite.position.set(
        Math.random() * 800,
        Math.random() * 600
    );
    sprite.vx = (Math.random() - 0.5) * 3;
    sprite.vy = (Math.random() - 0.5) * 3;
    app.stage.addChild(sprite);
    sprites.push(sprite);
}

app.ticker.add((ticker) => {
    // Update positions
    for (const sprite of sprites) {
        sprite.x += sprite.vx * ticker.deltaTime;
        sprite.y += sprite.vy * ticker.deltaTime;

        // Bounce off edges
        if (sprite.x < 0 || sprite.x > 800) sprite.vx *= -1;
        if (sprite.y < 0 || sprite.y > 600) sprite.vy *= -1;
    }

    // Rebuild spatial hash
    spatialHash.clear();
    for (const sprite of sprites) {
        spatialHash.insert(sprite);
    }

    // Check collisions (only nearby sprites)
    for (const sprite of sprites) {
        const nearby = spatialHash.getNearby(sprite);

        for (const other of nearby) {
            if (checkCollision(sprite, other)) {
                // Handle collision
                sprite.tint = 0xff0000;
                other.tint = 0xff0000;
            } else {
                sprite.tint = 0xffffff;
            }
        }
    }
});

function checkCollision(a, b) {
    const ab = a.getBounds();
    const bb = b.getBounds();

    return ab.x < bb.x + bb.width &&
           ab.x + ab.width > bb.x &&
           ab.y < bb.y + bb.height &&
           ab.y + ab.height > bb.y;
}
```

---

## Game Development

### 1. Simple Platformer Physics

Basic 2D platformer with jumping and gravity:

```javascript
class Player {
    constructor(app, x, y) {
        this.app = app;

        // Create sprite
        const graphics = new PIXI.Graphics();
        graphics.rect(0, 0, 32, 48).fill(0x3498db);
        const texture = app.renderer.generateTexture(graphics);
        this.sprite = new PIXI.Sprite(texture);
        this.sprite.position.set(x, y);
        app.stage.addChild(this.sprite);

        // Physics
        this.vx = 0;
        this.vy = 0;
        this.isGrounded = false;
        this.gravity = 0.5;
        this.jumpPower = -12;
        this.moveSpeed = 5;

        // Input
        this.keys = {};
        this.setupInput();
    }

    setupInput() {
        window.addEventListener('keydown', (e) => {
            this.keys[e.key] = true;

            if (e.key === ' ' && this.isGrounded) {
                this.vy = this.jumpPower;
                this.isGrounded = false;
            }
        });

        window.addEventListener('keyup', (e) => {
            this.keys[e.key] = false;
        });
    }

    update(platforms) {
        // Horizontal movement
        this.vx = 0;
        if (this.keys['ArrowLeft']) this.vx = -this.moveSpeed;
        if (this.keys['ArrowRight']) this.vx = this.moveSpeed;

        // Apply gravity
        if (!this.isGrounded) {
            this.vy += this.gravity;
        }

        // Update position
        this.sprite.x += this.vx;
        this.sprite.y += this.vy;

        // Check platform collisions
        this.isGrounded = false;

        for (const platform of platforms) {
            if (this.checkCollision(platform)) {
                // Resolve collision
                const playerBottom = this.sprite.y + this.sprite.height;
                const platformTop = platform.y;

                if (this.vy > 0 && playerBottom <= platformTop + this.vy) {
                    // Landing on platform
                    this.sprite.y = platformTop - this.sprite.height;
                    this.vy = 0;
                    this.isGrounded = true;
                }
            }
        }

        // Keep in bounds
        if (this.sprite.x < 0) this.sprite.x = 0;
        if (this.sprite.x > 800 - this.sprite.width) {
            this.sprite.x = 800 - this.sprite.width;
        }
    }

    checkCollision(platform) {
        return this.sprite.x < platform.x + platform.width &&
               this.sprite.x + this.sprite.width > platform.x &&
               this.sprite.y < platform.y + platform.height &&
               this.sprite.y + this.sprite.height > platform.y;
    }
}

// Usage
const player = new Player(app, 100, 100);

// Create platforms
const platforms = [
    { x: 0, y: 550, width: 800, height: 50 },    // Ground
    { x: 200, y: 450, width: 150, height: 20 },
    { x: 450, y: 350, width: 150, height: 20 },
    { x: 100, y: 250, width: 150, height: 20 }
];

// Draw platforms
for (const platform of platforms) {
    const graphics = new PIXI.Graphics();
    graphics.rect(platform.x, platform.y, platform.width, platform.height)
        .fill(0x2ecc71);
    app.stage.addChild(graphics);
}

// Game loop
app.ticker.add(() => {
    player.update(platforms);
});
```

### 2. Top-Down Movement

8-direction movement with collision:

```javascript
class TopDownCharacter {
    constructor(app, x, y) {
        this.app = app;

        const graphics = new PIXI.Graphics();
        graphics.circle(16, 16, 16).fill(0xe74c3c);
        const texture = app.renderer.generateTexture(graphics);
        this.sprite = new PIXI.Sprite(texture);
        this.sprite.anchor.set(0.5);
        this.sprite.position.set(x, y);
        app.stage.addChild(this.sprite);

        this.speed = 3;
        this.keys = {};

        window.addEventListener('keydown', (e) => this.keys[e.key] = true);
        window.addEventListener('keyup', (e) => this.keys[e.key] = false);
    }

    update(obstacles = []) {
        let dx = 0;
        let dy = 0;

        if (this.keys['w'] || this.keys['ArrowUp']) dy -= this.speed;
        if (this.keys['s'] || this.keys['ArrowDown']) dy += this.speed;
        if (this.keys['a'] || this.keys['ArrowLeft']) dx -= this.speed;
        if (this.keys['d'] || this.keys['ArrowRight']) dx += this.speed;

        // Normalize diagonal movement
        if (dx !== 0 && dy !== 0) {
            dx *= 0.707;  // 1/√2
            dy *= 0.707;
        }

        // Try horizontal movement
        this.sprite.x += dx;
        if (this.checkCollisions(obstacles)) {
            this.sprite.x -= dx;
        }

        // Try vertical movement
        this.sprite.y += dy;
        if (this.checkCollisions(obstacles)) {
            this.sprite.y -= dy;
        }

        // Face movement direction
        if (dx !== 0 || dy !== 0) {
            this.sprite.rotation = Math.atan2(dy, dx);
        }
    }

    checkCollisions(obstacles) {
        for (const obstacle of obstacles) {
            const bounds = this.sprite.getBounds();

            if (bounds.x < obstacle.x + obstacle.width &&
                bounds.x + bounds.width > obstacle.x &&
                bounds.y < obstacle.y + obstacle.height &&
                bounds.y + bounds.height > obstacle.y) {
                return true;
            }
        }
        return false;
    }
}

// Usage
const character = new TopDownCharacter(app, 400, 300);

const obstacles = [
    { x: 200, y: 200, width: 100, height: 100 },
    { x: 500, y: 300, width: 80, height: 120 }
];

// Draw obstacles
for (const obstacle of obstacles) {
    const graphics = new PIXI.Graphics();
    graphics.rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
        .fill(0x95a5a6);
    app.stage.addChild(graphics);
}

app.ticker.add(() => {
    character.update(obstacles);
});
```

### 3. Health Bar Component

Reusable health bar UI:

```javascript
class HealthBar extends PIXI.Container {
    constructor(maxHealth = 100, width = 100, height = 10) {
        super();

        this.maxHealth = maxHealth;
        this.currentHealth = maxHealth;
        this.barWidth = width;
        this.barHeight = height;

        // Background (red)
        this.background = new PIXI.Graphics();
        this.background.rect(0, 0, width, height).fill(0xff0000);
        this.addChild(this.background);

        // Foreground (green)
        this.foreground = new PIXI.Graphics();
        this.foreground.rect(0, 0, width, height).fill(0x00ff00);
        this.addChild(this.foreground);

        // Border
        this.border = new PIXI.Graphics();
        this.border.rect(0, 0, width, height)
            .stroke({ width: 2, color: 0x000000 });
        this.addChild(this.border);
    }

    setHealth(value) {
        this.currentHealth = Math.max(0, Math.min(value, this.maxHealth));
        this.updateBar();
    }

    damage(amount) {
        this.setHealth(this.currentHealth - amount);
    }

    heal(amount) {
        this.setHealth(this.currentHealth + amount);
    }

    updateBar() {
        const percentage = this.currentHealth / this.maxHealth;
        const newWidth = this.barWidth * percentage;

        // Animate width
        this.foreground.clear();
        this.foreground.rect(0, 0, newWidth, this.barHeight).fill(this.getHealthColor());
    }

    getHealthColor() {
        const percentage = this.currentHealth / this.maxHealth;

        if (percentage > 0.5) return 0x00ff00;  // Green
        if (percentage > 0.25) return 0xffff00; // Yellow
        return 0xff0000;  // Red
    }
}

// Usage
const enemy = new PIXI.Sprite(texture);
enemy.position.set(400, 300);
app.stage.addChild(enemy);

const healthBar = new HealthBar(100, 80, 8);
healthBar.position.set(enemy.x - 40, enemy.y - 50);
app.stage.addChild(healthBar);

// Damage over time
setInterval(() => {
    healthBar.damage(10);

    if (healthBar.currentHealth === 0) {
        console.log('Enemy defeated!');
    }
}, 1000);
```

### 4. State Machine for Game Logic

Manage game states (menu, playing, paused, game over):

```javascript
class StateMachine {
    constructor() {
        this.states = new Map();
        this.currentState = null;
    }

    addState(name, state) {
        this.states.set(name, state);
    }

    setState(name) {
        if (this.currentState) {
            this.currentState.exit?.();
        }

        const newState = this.states.get(name);
        if (newState) {
            this.currentState = newState;
            newState.enter?.();
        }
    }

    update(deltaTime) {
        this.currentState?.update?.(deltaTime);
    }

    render() {
        this.currentState?.render?.();
    }
}

// Game states
class MenuState {
    constructor(app, stateMachine) {
        this.app = app;
        this.stateMachine = stateMachine;
        this.container = new PIXI.Container();

        const title = new PIXI.Text({
            text: 'Main Menu',
            style: { fontSize: 64, fill: 0xffffff }
        });
        title.anchor.set(0.5);
        title.position.set(400, 200);
        this.container.addChild(title);

        const startButton = new PIXI.Text({
            text: 'Start Game',
            style: { fontSize: 32, fill: 0x00ff00 }
        });
        startButton.anchor.set(0.5);
        startButton.position.set(400, 350);
        startButton.eventMode = 'static';
        startButton.cursor = 'pointer';
        startButton.on('pointerdown', () => {
            stateMachine.setState('playing');
        });
        this.container.addChild(startButton);
    }

    enter() {
        this.app.stage.addChild(this.container);
    }

    exit() {
        this.app.stage.removeChild(this.container);
    }
}

class PlayingState {
    constructor(app, stateMachine) {
        this.app = app;
        this.stateMachine = stateMachine;
        this.container = new PIXI.Container();
        this.score = 0;

        this.scoreText = new PIXI.Text({
            text: 'Score: 0',
            style: { fontSize: 24, fill: 0xffffff }
        });
        this.scoreText.position.set(10, 10);
        this.container.addChild(this.scoreText);

        // Setup pause key
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.stateMachine.currentState === this) {
                this.stateMachine.setState('paused');
            }
        });
    }

    enter() {
        this.app.stage.addChild(this.container);
        this.score = 0;
    }

    exit() {
        // Keep container for paused state
    }

    update(deltaTime) {
        // Game logic here
        this.score++;
        this.scoreText.text = `Score: ${Math.floor(this.score / 60)}`;
    }
}

class PausedState {
    constructor(app, stateMachine) {
        this.app = app;
        this.stateMachine = stateMachine;
        this.container = new PIXI.Container();

        const overlay = new PIXI.Graphics();
        overlay.rect(0, 0, 800, 600).fill({ color: 0x000000, alpha: 0.7 });
        this.container.addChild(overlay);

        const pausedText = new PIXI.Text({
            text: 'PAUSED',
            style: { fontSize: 64, fill: 0xffffff }
        });
        pausedText.anchor.set(0.5);
        pausedText.position.set(400, 250);
        this.container.addChild(pausedText);

        const resumeButton = new PIXI.Text({
            text: 'Resume',
            style: { fontSize: 32, fill: 0x00ff00 }
        });
        resumeButton.anchor.set(0.5);
        resumeButton.position.set(400, 350);
        resumeButton.eventMode = 'static';
        resumeButton.cursor = 'pointer';
        resumeButton.on('pointerdown', () => {
            stateMachine.setState('playing');
        });
        this.container.addChild(resumeButton);
    }

    enter() {
        this.app.stage.addChild(this.container);
    }

    exit() {
        this.app.stage.removeChild(this.container);
    }
}

// Usage
const stateMachine = new StateMachine();

stateMachine.addState('menu', new MenuState(app, stateMachine));
stateMachine.addState('playing', new PlayingState(app, stateMachine));
stateMachine.addState('paused', new PausedState(app, stateMachine));

stateMachine.setState('menu');

app.ticker.add((ticker) => {
    stateMachine.update(ticker.deltaTime);
});
```

---

## UI Components

### 1. Progress Bar

Animated progress bar with percentage:

```javascript
class ProgressBar extends PIXI.Container {
    constructor(width = 200, height = 30, options = {}) {
        super();

        const {
            backgroundColor = 0x333333,
            fillColor = 0x3498db,
            borderColor = 0xffffff,
            borderWidth = 2,
            showPercentage = true
        } = options;

        this.barWidth = width;
        this.barHeight = height;
        this.progress = 0;
        this.targetProgress = 0;
        this.animationSpeed = 0.05;

        // Background
        this.background = new PIXI.Graphics();
        this.background.roundRect(0, 0, width, height, 5).fill(backgroundColor);
        this.addChild(this.background);

        // Fill
        this.fill = new PIXI.Graphics();
        this.addChild(this.fill);

        // Border
        this.border = new PIXI.Graphics();
        this.border.roundRect(0, 0, width, height, 5)
            .stroke({ width: borderWidth, color: borderColor });
        this.addChild(this.border);

        // Percentage text
        if (showPercentage) {
            this.percentageText = new PIXI.Text({
                text: '0%',
                style: {
                    fontSize: height * 0.6,
                    fill: 0xffffff,
                    fontWeight: 'bold'
                }
            });
            this.percentageText.anchor.set(0.5);
            this.percentageText.position.set(width / 2, height / 2);
            this.addChild(this.percentageText);
        }

        this.fillColor = fillColor;
        this.updateBar();
    }

    setProgress(value, animate = true) {
        this.targetProgress = Math.max(0, Math.min(1, value));
        if (!animate) {
            this.progress = this.targetProgress;
            this.updateBar();
        }
    }

    update() {
        if (Math.abs(this.targetProgress - this.progress) > 0.001) {
            this.progress += (this.targetProgress - this.progress) * this.animationSpeed;
            this.updateBar();
        }
    }

    updateBar() {
        const fillWidth = this.barWidth * this.progress;

        this.fill.clear();
        if (fillWidth > 0) {
            this.fill.roundRect(0, 0, fillWidth, this.barHeight, 5).fill(this.fillColor);
        }

        if (this.percentageText) {
            this.percentageText.text = `${Math.round(this.progress * 100)}%`;
        }
    }
}

// Usage
const loadingBar = new ProgressBar(400, 40, {
    backgroundColor: 0x2c3e50,
    fillColor: 0x27ae60,
    showPercentage: true
});

loadingBar.position.set(200, 280);
app.stage.addChild(loadingBar);

// Simulate loading
let loaded = 0;
const interval = setInterval(() => {
    loaded += 0.1;
    loadingBar.setProgress(loaded);

    if (loaded >= 1) {
        clearInterval(interval);
        console.log('Loading complete!');
    }
}, 100);

app.ticker.add(() => {
    loadingBar.update();
});
```

### 2. Modal Dialog

Reusable modal dialog component:

```javascript
class Modal extends PIXI.Container {
    constructor(title, message, buttons = ['OK']) {
        super();

        // Dark overlay
        this.overlay = new PIXI.Graphics();
        this.overlay.rect(0, 0, 800, 600).fill({ color: 0x000000, alpha: 0.7 });
        this.overlay.eventMode = 'static';  // Block clicks
        this.addChild(this.overlay);

        // Modal background
        this.modal = new PIXI.Graphics();
        this.modal.roundRect(200, 150, 400, 300, 10).fill(0xffffff);
        this.modal.roundRect(200, 150, 400, 300, 10)
            .stroke({ width: 3, color: 0x3498db });
        this.addChild(this.modal);

        // Title
        const titleText = new PIXI.Text({
            text: title,
            style: {
                fontSize: 32,
                fill: 0x2c3e50,
                fontWeight: 'bold'
            }
        });
        titleText.anchor.set(0.5, 0);
        titleText.position.set(400, 170);
        this.addChild(titleText);

        // Message
        const messageText = new PIXI.Text({
            text: message,
            style: {
                fontSize: 20,
                fill: 0x34495e,
                align: 'center',
                wordWrap: true,
                wordWrapWidth: 350
            }
        });
        messageText.anchor.set(0.5);
        messageText.position.set(400, 280);
        this.addChild(messageText);

        // Buttons
        const buttonContainer = new PIXI.Container();
        const buttonWidth = 120;
        const buttonSpacing = 20;
        const totalWidth = buttons.length * buttonWidth + (buttons.length - 1) * buttonSpacing;

        buttons.forEach((label, index) => {
            const button = this.createButton(label, buttonWidth, 40);
            button.position.set(
                index * (buttonWidth + buttonSpacing),
                0
            );
            buttonContainer.addChild(button);
        });

        buttonContainer.position.set(400 - totalWidth / 2, 380);
        this.addChild(buttonContainer);

        this.visible = false;
    }

    createButton(label, width, height) {
        const button = new PIXI.Container();

        const bg = new PIXI.Graphics();
        bg.roundRect(0, 0, width, height, 5).fill(0x3498db);
        button.addChild(bg);

        const text = new PIXI.Text({
            text: label,
            style: {
                fontSize: 18,
                fill: 0xffffff,
                fontWeight: 'bold'
            }
        });
        text.anchor.set(0.5);
        text.position.set(width / 2, height / 2);
        button.addChild(text);

        button.eventMode = 'static';
        button.cursor = 'pointer';

        button.on('pointerover', () => {
            bg.clear();
            bg.roundRect(0, 0, width, height, 5).fill(0x2980b9);
        });

        button.on('pointerout', () => {
            bg.clear();
            bg.roundRect(0, 0, width, height, 5).fill(0x3498db);
        });

        button.on('pointerdown', () => {
            this.visible = false;
            this.emit('buttonClick', label);
        });

        return button;
    }

    show() {
        this.visible = true;
    }

    hide() {
        this.visible = false;
    }
}

// Usage
const modal = new Modal(
    'Game Over',
    'You scored 1,234 points!\nWould you like to play again?',
    ['Play Again', 'Main Menu', 'Quit']
);

app.stage.addChild(modal);

modal.on('buttonClick', (button) => {
    console.log(`Clicked: ${button}`);

    if (button === 'Play Again') {
        startGame();
    } else if (button === 'Main Menu') {
        showMenu();
    } else if (button === 'Quit') {
        quitGame();
    }
});

// Show modal after 3 seconds
setTimeout(() => {
    modal.show();
}, 3000);
```

### 3. Slider Component

Interactive slider for settings:

```javascript
class Slider extends PIXI.Container {
    constructor(min = 0, max = 100, value = 50, width = 200) {
        super();

        this.min = min;
        this.max = max;
        this.value = value;
        this.width = width;
        this.isDragging = false;

        // Track
        this.track = new PIXI.Graphics();
        this.track.roundRect(0, -2, width, 4, 2).fill(0x7f8c8d);
        this.addChild(this.track);

        // Fill
        this.fill = new PIXI.Graphics();
        this.addChild(this.fill);

        // Handle
        this.handle = new PIXI.Graphics();
        this.handle.circle(0, 0, 10).fill(0x3498db);
        this.handle.circle(0, 0, 10).stroke({ width: 2, color: 0xffffff });
        this.handle.eventMode = 'static';
        this.handle.cursor = 'pointer';
        this.addChild(this.handle);

        // Events
        this.handle.on('pointerdown', this.onDragStart.bind(this));
        this.handle.on('pointerup', this.onDragEnd.bind(this));
        this.handle.on('pointerupoutside', this.onDragEnd.bind(this));

        this.updateVisuals();
    }

    onDragStart(event) {
        this.isDragging = true;
        this.handle.on('globalpointermove', this.onDragMove.bind(this));
    }

    onDragMove(event) {
        if (!this.isDragging) return;

        const localX = event.global.x - this.getGlobalPosition().x;
        const percentage = Math.max(0, Math.min(1, localX / this.width));
        this.setValue(this.min + (this.max - this.min) * percentage);
    }

    onDragEnd() {
        this.isDragging = false;
        this.handle.off('globalpointermove');
    }

    setValue(value) {
        this.value = Math.max(this.min, Math.min(this.max, value));
        this.updateVisuals();
        this.emit('change', this.value);
    }

    updateVisuals() {
        const percentage = (this.value - this.min) / (this.max - this.min);
        const handleX = this.width * percentage;

        // Update fill
        this.fill.clear();
        this.fill.roundRect(0, -2, handleX, 4, 2).fill(0x3498db);

        // Update handle position
        this.handle.position.set(handleX, 0);
    }
}

// Usage
const volumeSlider = new Slider(0, 100, 75, 250);
volumeSlider.position.set(275, 300);
app.stage.addChild(volumeSlider);

const label = new PIXI.Text({
    text: 'Volume: 75',
    style: { fontSize: 20, fill: 0xffffff }
});
label.position.set(275, 270);
app.stage.addChild(label);

volumeSlider.on('change', (value) => {
    label.text = `Volume: ${Math.round(value)}`;
    console.log('Volume changed to:', value);
});
```

---

(Continuing with Framework Integration, Mobile Optimization, and Advanced Techniques in next message due to length constraints...)

## Framework Integration

### 1. React Integration with @pixi/react

Use PixiJS components in React:

```javascript
// Install: npm install @pixi/react pixi.js

import { Stage, Container, Sprite, useApp, useTick } from '@pixi/react';
import { useState, useCallback } from 'react';
import * as PIXI from 'pixi.js';

// Animated sprite component
function RotatingSprite({ x, y, texture }) {
    const [rotation, setRotation] = useState(0);

    useTick((delta) => {
        setRotation((prev) => prev + 0.05 * delta);
    });

    return (
        <Sprite
            texture={texture}
            x={x}
            y={y}
            anchor={0.5}
            rotation={rotation}
        />
    );
}

// Interactive sprite
function DraggableSprite({ initialX, initialY, texture }) {
    const [position, setPosition] = useState({ x: initialX, y: initialY });
    const [isDragging, setIsDragging] = useState(false);

    const handlePointerDown = useCallback(() => {
        setIsDragging(true);
    }, []);

    const handlePointerUp = useCallback(() => {
        setIsDragging(false);
    }, []);

    const handlePointerMove = useCallback((event) => {
        if (isDragging) {
            setPosition({
                x: event.global.x,
                y: event.global.y
            });
        }
    }, [isDragging]);

    return (
        <Sprite
            texture={texture}
            x={position.x}
            y={position.y}
            anchor={0.5}
            interactive
            pointerdown={handlePointerDown}
            pointerup={handlePointerUp}
            pointerupoutside={handlePointerUp}
            pointermove={handlePointerMove}
            cursor="pointer"
        />
    );
}

// Main app component
function PixiApp() {
    const [bunnyTexture] = useState(() => PIXI.Texture.from('bunny.png'));
    const [spriteCount, setSpriteCount] = useState(5);

    return (
        <div>
            <button onClick={() => setSpriteCount(prev => prev + 5)}>
                Add Sprites
            </button>
            <Stage width={800} height={600} options={{ backgroundColor: 0x1099bb }}>
                <Container>
                    {Array.from({ length: spriteCount }, (_, i) => (
                        <RotatingSprite
                            key={i}
                            x={Math.random() * 800}
                            y={Math.random() * 600}
                            texture={bunnyTexture}
                        />
                    ))}
                    <DraggableSprite
                        initialX={400}
                        initialY={300}
                        texture={bunnyTexture}
                    />
                </Container>
            </Stage>
        </div>
    );
}

export default PixiApp;
```

### 2. Vue Integration

```javascript
// Install: npm install vue pixi.js

<template>
  <div>
    <div ref="pixiContainer"></div>
    <div class="controls">
      <button @click="addSprite">Add Sprite</button>
      <button @click="clearSprites">Clear</button>
      <p>Sprites: {{ sprites.length }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import * as PIXI from 'pixi.js';

export default {
    setup() {
        const pixiContainer = ref(null);
        let app = null;
        const sprites = ref([]);

        onMounted(async () => {
            app = new PIXI.Application();

            await app.init({
                width: 800,
                height: 600,
                backgroundColor: 0x1099bb
            });

            pixiContainer.value.appendChild(app.canvas);

            // Start ticker
            app.ticker.add((ticker) => {
                sprites.value.forEach(sprite => {
                    sprite.rotation += 0.05 * ticker.deltaTime;
                });
            });
        });

        onUnmounted(() => {
            app?.destroy(true, { children: true });
        });

        const addSprite = async () => {
            if (!app) return;

            const texture = await PIXI.Assets.load('bunny.png');
            const sprite = new PIXI.Sprite(texture);

            sprite.anchor.set(0.5);
            sprite.position.set(
                Math.random() * 800,
                Math.random() * 600
            );

            app.stage.addChild(sprite);
            sprites.value.push(sprite);
        };

        const clearSprites = () => {
            sprites.value.forEach(sprite => {
                app.stage.removeChild(sprite);
                sprite.destroy();
            });
            sprites.value = [];
        };

        return {
            pixiContainer,
            sprites,
            addSprite,
            clearSprites
        };
    }
};
</script>

<style scoped>
.controls {
    margin-top: 20px;
}

button {
    margin-right: 10px;
    padding: 10px 20px;
}
</style>
```

---

## Mobile Optimization

### 1. Touch Controls

Implement mobile-friendly touch controls:

```javascript
class TouchJoystick {
    constructor(app, options = {}) {
        this.app = app;
        this.container = new PIXI.Container();
        this.isActive = false;
        this.centerX = 0;
        this.centerY = 0;
        this.touchId = null;

        const { radius = 60, color = 0x3498db } = options;

        // Outer circle (base)
        this.base = new PIXI.Graphics();
        this.base.circle(0, 0, radius).fill({ color: 0x000000, alpha: 0.3 });
        this.base.circle(0, 0, radius).stroke({ width: 3, color, alpha: 0.5 });
        this.container.addChild(this.base);

        // Inner circle (stick)
        this.stick = new PIXI.Graphics();
        this.stick.circle(0, 0, radius / 2).fill({ color, alpha: 0.7 });
        this.container.addChild(this.stick);

        this.radius = radius;
        this.container.position.set(100, app.screen.height - 100);
        this.container.alpha = 0.5;

        app.stage.addChild(this.container);

        // Touch events
        app.stage.eventMode = 'static';
        app.stage.on('pointerdown', this.onTouchStart.bind(this));
        app.stage.on('pointermove', this.onTouchMove.bind(this));
        app.stage.on('pointerup', this.onTouchEnd.bind(this));
        app.stage.on('pointerupoutside', this.onTouchEnd.bind(this));

        this.direction = { x: 0, y: 0 };
        this.magnitude = 0;
    }

    onTouchStart(event) {
        const pos = event.global;
        const dist = this.distance(
            pos.x,
            pos.y,
            this.container.x,
            this.container.y
        );

        if (dist < this.radius * 1.5) {
            this.isActive = true;
            this.touchId = event.pointerId;
            this.container.alpha = 1;
        }
    }

    onTouchMove(event) {
        if (!this.isActive || event.pointerId !== this.touchId) return;

        const pos = event.global;
        const dx = pos.x - this.container.x;
        const dy = pos.y - this.container.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist > this.radius) {
            // Clamp to radius
            this.stick.position.set(
                (dx / dist) * this.radius,
                (dy / dist) * this.radius
            );
            this.magnitude = 1;
        } else {
            this.stick.position.set(dx, dy);
            this.magnitude = dist / this.radius;
        }

        // Normalized direction
        if (dist > 0) {
            this.direction.x = dx / dist;
            this.direction.y = dy / dist;
        }
    }

    onTouchEnd(event) {
        if (event.pointerId === this.touchId) {
            this.isActive = false;
            this.touchId = null;
            this.stick.position.set(0, 0);
            this.container.alpha = 0.5;
            this.direction = { x: 0, y: 0 };
            this.magnitude = 0;
        }
    }

    distance(x1, y1, x2, y2) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        return Math.sqrt(dx * dx + dy * dy);
    }

    getDirection() {
        return {
            x: this.direction.x * this.magnitude,
            y: this.direction.y * this.magnitude
        };
    }
}

// Usage
const joystick = new TouchJoystick(app, { radius: 70, color: 0xe74c3c });

const player = new PIXI.Sprite(texture);
player.anchor.set(0.5);
player.position.set(400, 300);
app.stage.addChild(player);

app.ticker.add((ticker) => {
    const dir = joystick.getDirection();
    const speed = 5;

    player.x += dir.x * speed * ticker.deltaTime;
    player.y += dir.y * speed * ticker.deltaTime;

    // Keep in bounds
    player.x = Math.max(0, Math.min(app.screen.width, player.x));
    player.y = Math.max(0, Math.min(app.screen.height, player.y));
});
```

### 2. Device Detection and Adaptive Settings

```javascript
class DeviceOptimizer {
    constructor(app) {
        this.app = app;
        this.isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        this.isLowEnd = this.detectLowEndDevice();

        this.applyOptimizations();
    }

    detectLowEndDevice() {
        // Check hardware concurrency (CPU cores)
        const cores = navigator.hardwareConcurrency || 2;

        // Check device memory (if available)
        const memory = navigator.deviceMemory || 4;

        // Low-end: < 4 cores or < 4GB RAM
        return cores < 4 || memory < 4 || this.isMobile;
    }

    applyOptimizations() {
        if (this.isLowEnd) {
            console.log('Applying low-end device optimizations');

            // Reduce resolution
            this.app.renderer.resolution = 1;

            // Disable antialiasing
            this.app.renderer.antialias = false;

            // Reduce max FPS
            this.app.ticker.maxFPS = 30;

            return {
                maxSprites: 50,
                particleLimit: 100,
                enableFilters: false,
                textureQuality: 'low'
            };
        } else {
            console.log('Using high-quality settings');

            return {
                maxSprites: 500,
                particleLimit: 5000,
                enableFilters: true,
                textureQuality: 'high'
            };
        }
    }

    getOptimalSettings() {
        return this.applyOptimizations();
    }
}

// Usage
(async () => {
    const app = new PIXI.Application();
    await app.init({
        width: window.innerWidth,
        height: window.innerHeight,
        backgroundColor: 0x1a1a2e
    });

    const optimizer = new DeviceOptimizer(app);
    const settings = optimizer.getOptimalSettings();

    console.log('Device settings:', settings);

    // Use settings to configure game
    for (let i = 0; i < settings.maxSprites; i++) {
        const sprite = new PIXI.Sprite(texture);
        // ... create sprites based on limit
    }
})();
```

---

## Advanced Techniques

### 1. Custom Render Texture

Render to texture for post-processing or caching:

```javascript
class RenderTextureEffect {
    constructor(app) {
        this.app = app;

        // Create render texture
        this.renderTexture = PIXI.RenderTexture.create({
            width: app.screen.width,
            height: app.screen.height
        });

        // Sprite to display the rendered texture
        this.outputSprite = new PIXI.Sprite(this.renderTexture);

        // Container for objects to render
        this.sceneContainer = new PIXI.Container();
    }

    render() {
        // Render scene to texture
        this.app.renderer.render({
            container: this.sceneContainer,
            target: this.renderTexture,
            clear: true
        });
    }

    getSprite() {
        return this.outputSprite;
    }

    getContainer() {
        return this.sceneContainer;
    }
}

// Usage - Create trail effect
const effect = new RenderTextureEffect(app);

const sprite = new PIXI.Sprite(texture);
sprite.position.set(400, 300);
effect.getContainer().addChild(sprite);

// Display render texture with alpha
const outputSprite = effect.getSprite();
outputSprite.alpha = 0.9;  // Fade effect
app.stage.addChild(outputSprite);

// Move sprite with mouse
app.stage.eventMode = 'static';
app.stage.on('pointermove', (event) => {
    sprite.position.set(event.global.x, event.global.y);
});

// Render each frame
app.ticker.add(() => {
    effect.render();
});
```

### 2. Multi-Pass Shader Effects

Chain multiple shader passes:

```javascript
class MultiPassFilter {
    constructor(app) {
        this.app = app;
        this.passes = [];
        this.renderTextures = [];
    }

    addPass(filter) {
        this.passes.push(filter);

        // Create render texture for this pass
        const rt = PIXI.RenderTexture.create({
            width: this.app.screen.width,
            height: this.app.screen.height
        });
        this.renderTextures.push(rt);
    }

    render(source) {
        let currentSource = source;

        for (let i = 0; i < this.passes.length; i++) {
            const filter = this.passes[i];
            const target = this.renderTextures[i];

            // Apply filter
            currentSource.filters = [filter];

            // Render to texture
            this.app.renderer.render({
                container: currentSource,
                target,
                clear: true
            });

            // Use output as input for next pass
            const sprite = new PIXI.Sprite(target);
            currentSource = sprite;
        }

        return currentSource;
    }
}

// Usage - Blur then chromatic aberration
const multiPass = new MultiPassFilter(app);

const blurFilter = new PIXI.BlurFilter();
blurFilter.strength = 5;

const chromaFilter = new ChromaticAberrationFilter(10);

multiPass.addPass(blurFilter);
multiPass.addPass(chromaFilter);

const scene = new PIXI.Container();
const sprite = new PIXI.Sprite(texture);
sprite.position.set(400, 300);
scene.addChild(sprite);

const result = multiPass.render(scene);
app.stage.addChild(result);
```

### 3. WebWorker Integration

Offload heavy calculations to worker threads:

```javascript
// worker.js
self.onmessage = function(e) {
    const { type, data } = e.data;

    if (type === 'calculateParticles') {
        const { count, width, height } = data;
        const particles = [];

        for (let i = 0; i < count; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 2,
                vy: (Math.random() - 0.5) * 2
            });
        }

        self.postMessage({ type: 'particlesCalculated', particles });
    } else if (type === 'updateParticles') {
        const { particles, width, height, deltaTime } = data;

        particles.forEach(p => {
            p.x += p.vx * deltaTime;
            p.y += p.vy * deltaTime;

            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;
        });

        self.postMessage({ type: 'particlesUpdated', particles });
    }
};

// main.js
const worker = new Worker('worker.js');
const particles = [];
const sprites = [];

worker.onmessage = function(e) {
    const { type, particles: updatedParticles } = e.data;

    if (type === 'particlesCalculated') {
        // Create sprites for particles
        updatedParticles.forEach(p => {
            const sprite = new PIXI.Sprite(texture);
            sprite.position.set(p.x, p.y);
            app.stage.addChild(sprite);
            sprites.push(sprite);
        });

        particles.push(...updatedParticles);
    } else if (type === 'particlesUpdated') {
        // Update sprite positions
        updatedParticles.forEach((p, i) => {
            sprites[i].position.set(p.x, p.y);
        });

        particles.length = 0;
        particles.push(...updatedParticles);
    }
};

// Initial creation
worker.postMessage({
    type: 'calculateParticles',
    data: {
        count: 10000,
        width: 800,
        height: 600
    }
});

// Update loop
app.ticker.add((ticker) => {
    if (particles.length > 0) {
        worker.postMessage({
            type: 'updateParticles',
            data: {
                particles,
                width: 800,
                height: 600,
                deltaTime: ticker.deltaTime
            }
        });
    }
});
```

---

## Conclusion

These examples cover the most common PixiJS patterns and use cases for production applications:

- **Basic Applications**: Foundation for any PixiJS project
- **Interactive Elements**: User input and engagement
- **Particle Systems**: Visual effects and ambiance
- **Filters & Effects**: Visual polish and style
- **Custom Shaders**: Advanced visual customization
- **Animation**: Smooth motion and transitions
- **Performance**: Optimization for 60 FPS
- **Game Development**: Core gameplay mechanics
- **UI Components**: Professional user interfaces
- **Framework Integration**: React, Vue compatibility
- **Mobile Optimization**: Touch controls and adaptive settings
- **Advanced Techniques**: Render textures, multi-pass effects, WebWorkers

For more examples, visit:
- [PixiJS Examples](https://pixijs.com/examples)
- [PixiJS Playground](https://pixijs.io/playground)
- [GitHub PixiJS Demos](https://github.com/pixijs/pixijs/tree/dev/examples)



===== FILE: plugins/individual/pixijs-2d/skills/pixijs-2d/assets/starter_pixijs/README.md =====

# PixiJS Starter Template

A modern, production-ready PixiJS starter template with interactive sprites, real-time performance monitoring, and responsive UI controls.

## Features

- **High-Performance Rendering**: Uses PixiJS v8+ with WebGL/WebGPU
- **Interactive Sprites**: Click to change colors, drag and interact
- **Physics Simulation**: Bouncing sprites with velocity and collision detection
- **Performance Monitoring**: Real-time FPS, sprite count, and draw call tracking
- **Responsive Design**: Mobile-friendly UI with glassmorphism effects
- **Modern UI**: Clean, professional interface with gradient accents
- **Easy Customization**: Well-structured code for quick modifications

## Quick Start

### 1. Local Development

Simply open `index.html` in a modern web browser:

```bash
# Using Python's built-in server (recommended)
python3 -m http.server 8000

# Or using Node.js http-server
npx http-server -p 8000

# Then open http://localhost:8000
```

### 2. Live Server (VS Code)

If using VS Code with the Live Server extension:

1. Right-click on `index.html`
2. Select "Open with Live Server"

### 3. Production Deployment

For production, serve the files through any static hosting:

- **Vercel**: `vercel --prod`
- **Netlify**: Drag and drop the folder
- **GitHub Pages**: Push to repository and enable Pages
- **AWS S3**: Upload as static website

## Project Structure

```
starter_pixijs/
├── index.html          # Main HTML structure
├── styles.css          # Responsive styling with glassmorphism
├── main.js             # PixiJS application logic
└── README.md           # This file
```

## Usage

### Controls

- **Toggle Stats**: Show/hide performance statistics panel
- **Add Sprites**: Add 20 random sprites to the canvas
- **Clear**: Remove all sprites from the canvas

### Interactions

- **Click Sprites**: Change sprite color randomly
- **Watch Physics**: Sprites bounce off edges automatically

## Customization

### Change Background Color

In `main.js` line 10:

```javascript
await app.init({
    backgroundColor: 0x1a1a2e,  // Change this hex color
    // ...
});
```

### Modify Sprite Colors

In `main.js` lines 35-40, edit the color palette:

```javascript
const textures = [
    createSpriteTexture(0xe74c3c),  // Red
    createSpriteTexture(0x3498db),  // Blue
    createSpriteTexture(0x2ecc71),  // Green
    createSpriteTexture(0xf39c12),  // Orange
    createSpriteTexture(0x9b59b6)   // Purple
];
```

### Adjust Sprite Size

In `main.js` line 31, change the circle radius:

```javascript
graphics.circle(25, 25, 25).fill(color);  // Last parameter is radius
```

### Change Initial Sprite Count

In `main.js` line 140:

```javascript
addSprites(50);  // Change from 50 to your desired count
```

### Modify Physics Behavior

In `main.js` lines 57-58, adjust velocity ranges:

```javascript
sprite.vx = (Math.random() - 0.5) * 2;  // Horizontal speed
sprite.vy = (Math.random() - 0.5) * 2;  // Vertical speed
```

### Disable Rotation

In `main.js`, comment out or remove line 124:

```javascript
// sprite.rotation += 0.01 * ticker.deltaTime;
```

## Advanced Customization

### Add Sprite Textures from Images

Replace the procedural graphics with image textures:

```javascript
// Load texture from image
const texture = await PIXI.Assets.load('path/to/sprite.png');

// Create sprite
const sprite = new PIXI.Sprite(texture);
```

### Add Filters and Effects

Apply blur, glow, or other effects:

```javascript
import { BlurFilter } from 'pixi.js';

const blurFilter = new BlurFilter();
blurFilter.strength = 8;

sprite.filters = [blurFilter];
```

### Implement Sprite Pooling

For better performance with many sprites:

```javascript
class SpritePool {
    constructor(texture, size = 100) {
        this.available = [];
        this.active = [];

        for (let i = 0; i < size; i++) {
            const sprite = new PIXI.Sprite(texture);
            sprite.visible = false;
            this.available.push(sprite);
        }
    }

    spawn(x, y) {
        let sprite = this.available.pop();
        if (!sprite) {
            sprite = new PIXI.Sprite(this.texture);
        }

        sprite.position.set(x, y);
        sprite.visible = true;
        this.active.push(sprite);
        return sprite;
    }

    despawn(sprite) {
        sprite.visible = false;
        const index = this.active.indexOf(sprite);
        if (index > -1) {
            this.active.splice(index, 1);
            this.available.push(sprite);
        }
    }
}

const pool = new SpritePool(texture);
const sprite = pool.spawn(100, 100);
// Later: pool.despawn(sprite);
```

### Add Particle Effects

Use ParticleContainer for thousands of sprites:

```javascript
const particles = new PIXI.ParticleContainer(10000, {
    position: true,
    rotation: true,
    scale: true,
    tint: true
});

for (let i = 0; i < 10000; i++) {
    const particle = new PIXI.Sprite(texture);
    particle.x = Math.random() * app.screen.width;
    particle.y = Math.random() * app.screen.height;
    particles.addChild(particle);
}

app.stage.addChild(particles);
```

### Add Custom Shaders

Create custom visual effects with GLSL:

```javascript
import { Filter, GlProgram } from 'pixi.js';

const fragment = `
    in vec2 vTextureCoord;
    uniform sampler2D uTexture;
    uniform float uTime;

    void main() {
        vec2 coord = vTextureCoord;
        coord.x += sin(coord.y * 10.0 + uTime) * 0.01;
        gl_FragColor = texture(uTexture, coord);
    }
`;

const waveFilter = new Filter({
    glProgram: new GlProgram({ fragment }),
    resources: {
        waveUniforms: {
            uTime: { value: 0, type: 'f32' }
        }
    }
});

// Update in ticker
app.ticker.add(() => {
    waveFilter.resources.waveUniforms.uniforms.uTime += 0.1;
});

sprite.filters = [waveFilter];
```

## Performance Tips

### For Desktop (High-End)

- Increase sprite count for stress testing
- Enable antialiasing for smoother edges
- Use higher resolution textures
- Add complex filters and effects

```javascript
await app.init({
    antialias: true,
    resolution: 2,  // Higher resolution
    // ...
});

addSprites(500);  // More sprites
```

### For Mobile (Low-End)

- Reduce sprite count
- Disable antialiasing
- Use lower resolution
- Avoid heavy filters

```javascript
await app.init({
    antialias: false,
    resolution: 1,
    // ...
});

addSprites(50);  // Fewer sprites
```

### General Optimization

1. **Use ParticleContainer** for static sprites (10x faster)
2. **Enable cacheAsBitmap** for complex static graphics
3. **Minimize draw calls** with texture atlases
4. **Cull off-screen objects** for large scenes
5. **Pool objects** to avoid garbage collection
6. **Limit filters** to specific areas with `filterArea`

## Troubleshooting

### Issue: Black screen or no rendering

**Solution**: Check browser console for errors. Ensure:
- PixiJS CDN is loading correctly
- No JavaScript errors in console
- Browser supports WebGL (check `https://get.webgl.org/`)

### Issue: Low FPS on mobile

**Solution**: Reduce sprite count and disable antialiasing:

```javascript
await app.init({
    antialias: false,
    resolution: 1
});

addSprites(25);  // Fewer sprites
```

### Issue: Sprites disappearing at edges

**Solution**: Ensure sprites are kept within bounds (lines 120-121 in main.js handle this)

### Issue: Memory leaks over time

**Solution**: Properly destroy sprites when clearing:

```javascript
function clearSprites() {
    sprites.forEach(sprite => {
        sprite.destroy({ texture: false });  // Keep texture
    });
    sprites.length = 0;
    spriteContainer.removeChildren();
}
```

## Browser Support

- **Chrome/Edge**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support (iOS 15+)
- **Mobile browsers**: Supported with reduced features

Requires WebGL support. Check compatibility at [caniuse.com/webgl](https://caniuse.com/webgl).

## Next Steps

### Learning Resources

- [PixiJS Official Documentation](https://pixijs.com/docs)
- [PixiJS Examples](https://pixijs.com/examples)
- [PixiJS Playground](https://pixijs.io/playground)
- [WebGL Fundamentals](https://webglfundamentals.org/)

### Extend the Template

1. **Add Sprite Sheet Animations**: Use `AnimatedSprite` for frame-based animation
2. **Implement Collision Detection**: Check sprite overlaps and interactions
3. **Add Sound Effects**: Integrate Howler.js or Web Audio API
4. **Create Game Logic**: Add scoring, levels, or gameplay mechanics
5. **Integrate with React**: Use `@pixi/react` for component-based approach

### Example Extensions

**Collision Detection**:
```javascript
function checkCollision(sprite1, sprite2) {
    const bounds1 = sprite1.getBounds();
    const bounds2 = sprite2.getBounds();

    return bounds1.x < bounds2.x + bounds2.width &&
           bounds1.x + bounds1.width > bounds2.x &&
           bounds1.y < bounds2.y + bounds2.height &&
           bounds1.y + bounds1.height > bounds2.y;
}

app.ticker.add(() => {
    for (let i = 0; i < sprites.length; i++) {
        for (let j = i + 1; j < sprites.length; j++) {
            if (checkCollision(sprites[i], sprites[j])) {
                // Handle collision
            }
        }
    }
});
```

**Sprite Sheet Animation**:
```javascript
// Load sprite sheet
const sheet = await PIXI.Assets.load('spritesheet.json');

// Create animated sprite
const animatedSprite = new PIXI.AnimatedSprite(sheet.animations['run']);
animatedSprite.animationSpeed = 0.1;
animatedSprite.play();

app.stage.addChild(animatedSprite);
```

**React Integration**:
```javascript
import { Stage, Container, Sprite } from '@pixi/react';

function App() {
    return (
        <Stage width={800} height={600}>
            <Container>
                <Sprite texture={texture} x={100} y={100} />
            </Container>
        </Stage>
    );
}
```

## Deployment

### Static Hosting

**Vercel**:
```bash
npm install -g vercel
vercel --prod
```

**Netlify**:
```bash
npm install -g netlify-cli
netlify deploy --prod --dir .
```

**GitHub Pages**:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/username/repo.git
git push -u origin main

# Enable Pages in repository settings
```

### CDN Considerations

The template uses PixiJS from CDN:
```html
<script src="https://pixijs.download/release/pixi.js"></script>
```

For production, consider:
1. **Self-hosting** for better caching and control
2. **npm installation** for bundled builds
3. **Specific version** to avoid breaking changes

**npm approach**:
```bash
npm install pixi.js
```

```javascript
// main.js
import * as PIXI from 'pixi.js';

// Use bundler like Vite or Webpack
```

## License

This starter template is provided as-is for learning and development purposes.

PixiJS is MIT licensed. See [PixiJS GitHub](https://github.com/pixijs/pixijs) for details.

## Support

For PixiJS questions:
- [PixiJS Discord](https://discord.gg/CPTjeb28nH)
- [PixiJS GitHub Discussions](https://github.com/pixijs/pixijs/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/pixi.js)

---

**Happy Coding!** 🎨✨



===== FILE: plugins/individual/pixijs-2d/skills/pixijs-2d/assets/starter_pixijs/index.html =====

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PixiJS Starter</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- UI Overlay -->
    <div id="ui-overlay">
        <div id="info-panel">
            <h1>PixiJS Starter</h1>
            <p>High-performance 2D rendering</p>
        </div>

        <div id="stats-panel">
            <div class="stat">
                <span class="label">FPS:</span>
                <span id="fps">--</span>
            </div>
            <div class="stat">
                <span class="label">Sprites:</span>
                <span id="sprite-count">--</span>
            </div>
            <div class="stat">
                <span class="label">Draw Calls:</span>
                <span id="draw-calls">--</span>
            </div>
        </div>

        <div id="controls-panel">
            <button id="toggle-stats">Toggle Stats</button>
            <button id="add-sprites">Add Sprites</button>
            <button id="clear-sprites">Clear</button>
        </div>
    </div>

    <!-- PixiJS CDN -->
    <script src="https://pixijs.download/release/pixi.js"></script>
    <script src="main.js"></script>
</body>
</html>

```


===== FILE: plugins/individual/pixijs-2d/skills/pixijs-2d/assets/starter_pixijs/main.js =====

```js
/**
 * PixiJS Starter Project
 * Main application initialization
 */

(async () => {
    // Create PixiJS application
    const app = new PIXI.Application();

    await app.init({
        width: window.innerWidth,
        height: window.innerHeight,
        backgroundColor: 0x1a1a2e,
        antialias: true,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true
    });

    document.body.appendChild(app.canvas);

    // Create sprite container
    const spriteContainer = new PIXI.Container();
    app.stage.addChild(spriteContainer);

    // Sprite collection
    const sprites = [];

    // Create sprite texture
    function createSpriteTexture(color) {
        const graphics = new PIXI.Graphics();
        graphics.circle(25, 25, 25).fill(color);
        return app.renderer.generateTexture(graphics);
    }

    const textures = [
        createSpriteTexture(0xe74c3c),
        createSpriteTexture(0x3498db),
        createSpriteTexture(0x2ecc71),
        createSpriteTexture(0xf39c12),
        createSpriteTexture(0x9b59b6)
    ];

    // Add sprites function
    function addSprites(count = 10) {
        for (let i = 0; i < count; i++) {
            const texture = textures[Math.floor(Math.random() * textures.length)];
            const sprite = new PIXI.Sprite(texture);

            sprite.anchor.set(0.5);
            sprite.position.set(
                Math.random() * app.screen.width,
                Math.random() * app.screen.height
            );
            sprite.scale.set(Math.random() * 0.5 + 0.5);

            // Velocity
            sprite.vx = (Math.random() - 0.5) * 2;
            sprite.vy = (Math.random() - 0.5) * 2;

            // Interactive
            sprite.eventMode = 'static';
            sprite.cursor = 'pointer';

            sprite.on('pointerdown', () => {
                sprite.tint = Math.random() * 0xffffff;
            });

            spriteContainer.addChild(sprite);
            sprites.push(sprite);
        }

        updateSpriteCount();
    }

    // Clear sprites function
    function clearSprites() {
        sprites.forEach(sprite => sprite.destroy());
        sprites.length = 0;
        spriteContainer.removeChildren();
        updateSpriteCount();
    }

    // Update sprite count display
    function updateSpriteCount() {
        document.getElementById('sprite-count').textContent = sprites.length;
    }

    // Setup UI controls
    let statsVisible = true;

    document.getElementById('toggle-stats').addEventListener('click', () => {
        statsVisible = !statsVisible;
        document.getElementById('stats-panel').classList.toggle('hidden');
    });

    document.getElementById('add-sprites').addEventListener('click', () => {
        addSprites(20);
    });

    document.getElementById('clear-sprites').addEventListener('click', () => {
        clearSprites();
    });

    // Update loop
    app.ticker.add((ticker) => {
        // Move sprites
        sprites.forEach(sprite => {
            sprite.x += sprite.vx * ticker.deltaTime;
            sprite.y += sprite.vy * ticker.deltaTime;

            // Bounce off edges
            if (sprite.x < 0 || sprite.x > app.screen.width) {
                sprite.vx *= -1;
            }
            if (sprite.y < 0 || sprite.y > app.screen.height) {
                sprite.vy *= -1;
            }

            // Keep within bounds
            sprite.x = Math.max(0, Math.min(app.screen.width, sprite.x));
            sprite.y = Math.max(0, Math.min(app.screen.height, sprite.y));

            // Rotate
            sprite.rotation += 0.01 * ticker.deltaTime;
        });

        // Update stats
        if (statsVisible) {
            document.getElementById('fps').textContent = Math.round(app.ticker.FPS);
            document.getElementById('draw-calls').textContent = app.renderer.stats.drawCalls.total || 0;
        }
    });

    // Handle window resize
    window.addEventListener('resize', () => {
        app.renderer.resize(window.innerWidth, window.innerHeight);
    });

    // Initial sprites
    addSprites(50);

    console.log('PixiJS application initialized');
    console.log('Canvas size:', app.screen.width, 'x', app.screen.height);
    console.log('Resolution:', app.renderer.resolution);
})();

```


===== FILE: plugins/individual/pixijs-2d/skills/pixijs-2d/assets/starter_pixijs/styles.css =====

```css
/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body {
    width: 100%;
    height: 100%;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: #1a1a2e;
    color: #fff;
}

/* Canvas Styles */
canvas {
    display: block;
    width: 100%;
    height: 100%;
}

/* UI Overlay */
#ui-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 10;
}

#ui-overlay > * {
    pointer-events: auto;
}

/* Info Panel */
#info-panel {
    position: absolute;
    top: 20px;
    left: 20px;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
    padding: 20px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

#info-panel h1 {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 8px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

#info-panel p {
    font-size: 14px;
    opacity: 0.8;
}

/* Stats Panel */
#stats-panel {
    position: absolute;
    top: 20px;
    right: 20px;
    background: rgba(0, 0, 0, 0.8);
    backdrop-filter: blur(10px);
    padding: 15px;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    min-width: 180px;
}

#stats-panel.hidden {
    display: none;
}

.stat {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    font-size: 14px;
}

.stat:last-child {
    margin-bottom: 0;
}

.stat .label {
    opacity: 0.7;
    margin-right: 15px;
}

.stat span:last-child {
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}

/* Controls Panel */
#controls-panel {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    gap: 10px;
}

button {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #fff;
    padding: 12px 24px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

button:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

button:active {
    transform: translateY(0);
}

/* Mobile Responsive */
@media (max-width: 768px) {
    #info-panel {
        top: 10px;
        left: 10px;
        padding: 15px;
    }

    #info-panel h1 {
        font-size: 20px;
    }

    #info-panel p {
        font-size: 12px;
    }

    #stats-panel {
        top: 10px;
        right: 10px;
        padding: 10px;
        min-width: 150px;
    }

    .stat {
        font-size: 12px;
    }

    #controls-panel {
        bottom: 10px;
        flex-direction: column;
        gap: 8px;
    }

    button {
        padding: 10px 20px;
        font-size: 13px;
    }
}

```


# Skill: animated-component-libraries


===== FILE: plugins/individual/animated-component-libraries/skills/animated-component-libraries/SKILL.md =====

---
name: animated-component-libraries
description: Pre-built animated React component collections combining Magic UI (150+ TypeScript/Tailwind/Motion components) and React Bits (90+ minimal-dependency animated components). Use this skill when building landing pages, marketing sites, dashboards, or interactive UIs requiring pre-made animated components instead of hand-crafting animations. Triggers on tasks involving animated UI components, Magic UI, React Bits, shadcn/ui integration, Tailwind CSS components, or component library selection. Alternative to manually implementing animations with Framer Motion or GSAP.
---

# Animated Component Libraries

## Overview

This skill provides expertise in pre-built animated React component libraries, specifically Magic UI and React Bits. These libraries offer production-ready, animated components that significantly accelerate development of modern, interactive web applications.

**Magic UI** provides 150+ TypeScript components built on Tailwind CSS and Framer Motion, designed for seamless integration with shadcn/ui. Components are copy-paste ready and highly customizable.

**React Bits** offers 90+ animated React components with minimal dependencies, focusing on visual effects, backgrounds, and micro-interactions. Components emphasize performance and ease of customization.

Both libraries follow modern React patterns, support TypeScript, and integrate with popular design systems.

## Core Concepts

### Magic UI Architecture

Magic UI components are built on three foundational technologies:

1. **Tailwind CSS**: Utility-first styling with full customization via `tailwind.config.js`
2. **Framer Motion**: Physics-based animations and gesture recognition
3. **shadcn/ui Integration**: Follows shadcn conventions for CLI installation and component structure

**Installation Methods**:

```bash
# Via shadcn CLI (recommended)
npx shadcn@latest add https://magicui.design/r/animated-beam

# Manual installation
# 1. Copy component code to components/ui/
# 2. Install motion: npm install motion
# 3. Add required CSS animations to globals.css
# 4. Ensure cn() utility exists in lib/utils.ts
```

**Component Structure**:

```typescript
// All Magic UI components follow this pattern:
import { cn } from "@/lib/utils"
import { motion } from "motion/react"

interface ComponentProps extends React.ComponentPropsWithoutRef<"div"> {
  customProp?: string
  className?: string
}

export function MagicComponent({ className, customProp, ...props }: ComponentProps) {
  return (
    <motion.div
      className={cn("base-styles", className)}
      {...props}
    >
      {/* Component content */}
    </motion.div>
  )
}
```

### React Bits Architecture

React Bits emphasizes lightweight, standalone components with minimal dependencies:

1. **Self-Contained**: Each component has minimal external dependencies
2. **CSS-in-JS Optional**: Many components use inline styles or CSS modules
3. **Performance-First**: Optimized for 60fps animations
4. **WebGL Support**: Some components (Particles, Plasma) use WebGL for advanced effects

**Installation**:

```bash
# Manual copy-paste (primary method)
# Copy component files from reactbits.dev to your project

# Key dependencies (install as needed):
npm install framer-motion  # For animation-heavy components
npm install ogl           # For WebGL components (Particles, Plasma)
```

**Component Categories**:

- **Text Animations**: BlurText, CircularText, CountUp, SpinningText
- **Interactive Elements**: MagicButton, Magnet, Dock, Stepper
- **Backgrounds**: Aurora, Plasma, Particles
- **Lists & Layouts**: AnimatedList, Bento Grid

## Common Patterns

### 1. Magic UI: Animated Background Patterns

Create dynamic background effects with SVG-based patterns:

```typescript
import { GridPattern } from "@/components/ui/grid-pattern"
import { AnimatedGridPattern } from "@/components/ui/animated-grid-pattern"
import { cn } from "@/lib/utils"

export default function HeroSection() {
  return (
    <div className="relative flex h-[500px] w-full items-center justify-center overflow-hidden rounded-lg border">
      {/* Static Grid Pattern */}
      <GridPattern
        squares={[
          [4, 4], [5, 1], [8, 2], [5, 3], [10, 10], [12, 15]
        ]}
        className={cn(
          "[mask-image:radial-gradient(400px_circle_at_center,white,transparent)]",
          "fill-gray-400/30 stroke-gray-400/30"
        )}
      />

      {/* Animated Interactive Grid */}
      <AnimatedGridPattern
        numSquares={50}
        maxOpacity={0.5}
        duration={4}
        repeatDelay={0.5}
        className={cn(
          "[mask-image:radial-gradient(500px_circle_at_center,white,transparent)]",
          "inset-x-0 inset-y-[-30%] h-[200%] skew-y-12"
        )}
      />

      <h1 className="relative z-10 text-6xl font-bold">
        Your Content Here
      </h1>
    </div>
  )
}
```

### 2. React Bits: Text Reveal Animations

Implement scroll-triggered text reveals with BlurText:

```jsx
import BlurText from './components/BlurText'

export default function MarketingSection() {
  return (
    <section className="py-20">
      {/* Word-by-word reveal */}
      <BlurText
        text="Transform your ideas into reality"
        delay={100}
        animateBy="words"
        direction="top"
        className="text-5xl font-bold text-center mb-8"
      />

      {/* Character-by-character reveal with custom easing */}
      <BlurText
        text="Pixel-perfect animations at your fingertips"
        delay={50}
        animateBy="characters"
        direction="bottom"
        threshold={0.3}
        stepDuration={0.4}
        animationFrom={{ filter: 'blur(20px)', opacity: 0, y: 50 }}
        animationTo={{ filter: 'blur(0px)', opacity: 1, y: 0 }}
        className="text-2xl text-gray-600 text-center"
      />
    </section>
  )
}
```

### 3. Magic UI: Button Components with Effects

Create interactive buttons with shimmer and border beam effects:

```typescript
import { ShimmerButton } from "@/components/ui/shimmer-button"
import { BorderBeam } from "@/components/ui/border-beam"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export default function CTASection() {
  return (
    <div className="flex gap-4 items-center">
      {/* Shimmer Button */}
      <ShimmerButton
        shimmerColor="#ffffff"
        shimmerSize="0.05em"
        shimmerDuration="3s"
        borderRadius="100px"
        background="rgba(0, 0, 0, 1)"
        className="px-8 py-3"
      >
        Get Started
      </ShimmerButton>

      {/* Card with Animated Border */}
      <Card className="relative w-[350px] overflow-hidden">
        <div className="p-6">
          <h3 className="text-2xl font-bold">Premium Plan</h3>
          <p className="text-gray-600">Unlock all features</p>
          <Button className="mt-4">Subscribe</Button>
        </div>
        <BorderBeam duration={8} size={100} />
      </Card>
    </div>
  )
}
```

### 4. React Bits: Interactive Dock Navigation

Implement macOS-style dock with magnification effects:

```jsx
import Dock from './components/Dock'
import { VscHome, VscArchive, VscAccount, VscSettingsGear } from 'react-icons/vsc'
import { useNavigate } from 'react-router-dom'

export default function AppNavigation() {
  const navigate = useNavigate()

  const dockItems = [
    {
      icon: <VscHome size={24} />,
      label: 'Dashboard',
      onClick: () => navigate('/dashboard')
    },
    {
      icon: <VscArchive size={24} />,
      label: 'Projects',
      onClick: () => navigate('/projects')
    },
    {
      icon: <VscAccount size={24} />,
      label: 'Profile',
      onClick: () => navigate('/profile')
    },
    {
      icon: <VscSettingsGear size={24} />,
      label: 'Settings',
      onClick: () => navigate('/settings')
    }
  ]

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2">
      <Dock
        items={dockItems}
        spring={{ mass: 0.15, stiffness: 200, damping: 15 }}
        magnification={80}
        distance={250}
        panelHeight={70}
        baseItemSize={55}
      />
    </div>
  )
}
```

### 5. React Bits: Animated Statistics with CountUp

Display animated numbers for dashboards and landing pages:

```jsx
import CountUp from './components/CountUp'

export default function Statistics() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 py-16">
      {/* Revenue Counter */}
      <div className="stat-card text-center">
        <CountUp
          start={0}
          end={1000000}
          duration={3}
          separator=","
          prefix="$"
          className="text-6xl font-bold text-blue-600"
        />
        <p className="text-xl text-gray-600 mt-2">Revenue Generated</p>
      </div>

      {/* Uptime Percentage */}
      <div className="stat-card text-center">
        <CountUp
          end={99.9}
          duration={2.5}
          decimals={1}
          suffix="%"
          className="text-6xl font-bold text-green-600"
        />
        <p className="text-xl text-gray-600 mt-2">Uptime</p>
      </div>

      {/* Customer Count */}
      <div className="stat-card text-center">
        <CountUp
          end={10000}
          duration={2}
          separator=","
          className="text-6xl font-bold text-purple-600"
        />
        <p className="text-xl text-gray-600 mt-2">Happy Customers</p>
      </div>
    </div>
  )
}
```

### 6. Magic UI: Marquee Component for Infinite Scroll

Create infinite scrolling content displays:

```typescript
import { Marquee } from "@/components/ui/marquee"

const testimonials = [
  { name: "John Doe", text: "Amazing product!", avatar: "/avatar1.jpg" },
  { name: "Jane Smith", text: "Exceeded expectations", avatar: "/avatar2.jpg" },
  { name: "Bob Johnson", text: "Highly recommend", avatar: "/avatar3.jpg" }
]

export default function Testimonials() {
  return (
    <section className="py-20">
      <h2 className="text-4xl font-bold text-center mb-12">
        What Our Customers Say
      </h2>

      {/* Horizontal Marquee */}
      <Marquee pauseOnHover className="[--duration:40s]">
        {testimonials.map((item, idx) => (
          <div key={idx} className="mx-4 w-[350px] rounded-lg border p-6">
            <p className="text-lg mb-4">"{item.text}"</p>
            <div className="flex items-center gap-3">
              <img src={item.avatar} alt={item.name} className="w-10 h-10 rounded-full" />
              <p className="font-semibold">{item.name}</p>
            </div>
          </div>
        ))}
      </Marquee>

      {/* Vertical Marquee */}
      <Marquee vertical reverse className="h-[400px] mt-8">
        {testimonials.map((item, idx) => (
          <div key={idx} className="my-4 w-full max-w-md rounded-lg border p-6">
            <p>{item.text}</p>
          </div>
        ))}
      </Marquee>
    </section>
  )
}
```

### 7. React Bits: WebGL Background Effects

Add high-performance animated backgrounds:

```jsx
import Particles from './components/Particles'
import Plasma from './components/Plasma'
import Aurora from './components/Aurora'

// Particles Effect
export default function ParticlesHero() {
  return (
    <section style={{ position: 'relative', height: '100vh' }}>
      <Particles
        particleCount={200}
        particleColors={['#FF6B6B', '#4ECDC4', '#45B7D1']}
        particleSpread={10}
        speed={0.12}
        moveParticlesOnHover={true}
        particleHoverFactor={2}
        particleBaseSize={100}
        sizeRandomness={1.2}
        alphaParticles={true}
        cameraDistance={20}
        className="particles-bg"
      />
      <div className="relative z-10 flex items-center justify-center h-full">
        <h1 className="text-7xl font-bold text-white">
          Welcome to the Future
        </h1>
      </div>
    </section>
  )
}

// Plasma Effect
export default function PlasmaBackground() {
  return (
    <div className="relative min-h-screen">
      <Plasma
        color1="#FF0080"
        color2="#7928CA"
        color3="#00DFD8"
        speed={0.8}
        blur={30}
        className="plasma-bg"
      />
      <div className="relative z-10 p-8">
        <h1>Content with Plasma Background</h1>
      </div>
    </div>
  )
}

// Aurora Effect
export default function AuroraHero() {
  return (
    <div className="relative min-h-screen">
      <Aurora
        colors={['#FF00FF', '#00FFFF', '#FFFF00']}
        speed={0.5}
        blur={80}
      />
      <main className="relative z-10">
        <h1>Cyberpunk Aurora Effect</h1>
      </main>
    </div>
  )
}
```

## Integration Patterns

### Integration with shadcn/ui

Magic UI components are designed to work seamlessly with shadcn/ui:

```bash
# Install shadcn/ui component
npx shadcn@latest add button card

# Install Magic UI component
npx shadcn@latest add https://magicui.design/r/shimmer-button

# Use together in components
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ShimmerButton } from "@/components/ui/shimmer-button"
import { BorderBeam } from "@/components/ui/border-beam"
```

**Utility Function Required** (`lib/utils.ts`):

```typescript
import clsx, { ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### Integration with Framer Motion

Both libraries leverage Framer Motion for animations:

```jsx
import { motion } from "framer-motion"
import { Magnet } from './components/Magnet'

// Combine React Bits Magnet with Framer Motion gestures
export default function InteractiveCard() {
  return (
    <Magnet magnitude={0.4} maxDistance={180}>
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="card p-6 rounded-xl shadow-lg"
      >
        <h3>Interactive Card</h3>
        <p>Combines magnetic pull with scale animation</p>
      </motion.div>
    </Magnet>
  )
}
```

### Integration with React Router

Combine animated components with routing:

```jsx
import { AnimatePresence, motion } from "framer-motion"
import { useLocation, Routes, Route } from "react-router-dom"
import { Dock } from './components/Dock'

export default function App() {
  const location = useLocation()

  return (
    <>
      {/* Animated Page Transitions */}
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <HomePage />
            </motion.div>
          } />
        </Routes>
      </AnimatePresence>

      {/* Persistent Dock Navigation */}
      <Dock items={navItems} />
    </>
  )
}
```

### Combining Magic UI and React Bits

Leverage strengths of both libraries in a single project:

```jsx
// Magic UI: Patterns and structural components
import { GridPattern } from "@/components/ui/grid-pattern"
import { BorderBeam } from "@/components/ui/border-beam"
import { Marquee } from "@/components/ui/marquee"

// React Bits: Interactive elements and effects
import BlurText from './components/BlurText'
import CountUp from './components/CountUp'
import Particles from './components/Particles'

export default function LandingPage() {
  return (
    <main>
      {/* Hero with React Bits background + Magic UI pattern */}
      <section className="relative h-screen">
        <Particles particleCount={150} />
        <GridPattern
          squares={[[4,4], [8,2], [12,6]]}
          className="opacity-30"
        />
        <BlurText
          text="Next-Generation Platform"
          className="text-7xl font-bold"
        />
      </section>

      {/* Stats with React Bits CountUp */}
      <section>
        <CountUp end={10000} suffix="+" />
      </section>

      {/* Testimonials with Magic UI Marquee */}
      <section>
        <Marquee>
          {/* Testimonial cards */}
        </Marquee>
      </section>
    </main>
  )
}
```

## Performance Optimization

### Magic UI Performance Tips

1. **Use CSS Masks Instead of Clipping**: More performant for large patterns

```typescript
<GridPattern
  className="[mask-image:radial-gradient(400px_circle_at_center,white,transparent)]"
/>
```

2. **Reduce Animation Complexity**: Lower `numSquares` for AnimatedGridPattern on mobile

```typescript
const isMobile = window.innerWidth < 768
<AnimatedGridPattern
  numSquares={isMobile ? 20 : 50}
  duration={isMobile ? 6 : 4}
/>
```

3. **Lazy Load Components**: Use React.lazy for heavy components

```typescript
const AnimatedGridPattern = React.lazy(() =>
  import("@/components/ui/animated-grid-pattern")
)
```

### React Bits Performance Tips

1. **WebGL Components**: Reduce particle count on low-end devices

```jsx
const particleCount = navigator.hardwareConcurrency > 4 ? 300 : 150

<Particles
  particleCount={particleCount}
  speed={0.1}
/>
```

2. **Disable Animations on Reduced Motion**:

```jsx
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

<BlurText
  text="Accessible text"
  delay={prefersReducedMotion ? 0 : 100}
  animateBy={prefersReducedMotion ? "none" : "words"}
/>
```

3. **Optimize Marquee Content**: Limit items for better performance

```typescript
<Marquee repeat={2}> {/* Instead of default 4 */}
  {items.slice(0, 10)} {/* Limit items */}
</Marquee>
```

4. **Use RequestIdleCallback for Non-Critical Animations**:

```jsx
useEffect(() => {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      // Initialize expensive animations
    })
  }
}, [])
```

## Common Pitfalls

### 1. Missing Dependencies

**Problem**: Component breaks due to missing `motion` or utility functions.

**Solution**: Always install required dependencies and utilities:

```bash
# Magic UI requirements
npm install motion clsx tailwind-merge

# React Bits WebGL components
npm install ogl

# Ensure cn() utility exists
```

```typescript
// lib/utils.ts
import clsx, { ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### 2. CSS Animations Not Applied

**Problem**: Magic UI animations don't work after manual installation.

**Solution**: Add required CSS animations to `globals.css`:

```css
/* app/globals.css */
@theme inline {
  --animate-ripple: ripple var(--duration, 2s) ease calc(var(--i, 0) * 0.2s) infinite;
  --animate-shimmer-slide: shimmer-slide var(--speed) ease-in-out infinite alternate;
  --animate-marquee: marquee var(--duration) linear infinite;
  --animate-marquee-vertical: marquee-vertical var(--duration) linear infinite;
}

@keyframes ripple {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, -50%) scale(0.9); }
}

@keyframes shimmer-slide {
  to { transform: translate(calc(100cqw - 100%), 0); }
}

@keyframes marquee {
  from { transform: translateX(0); }
  to { transform: translateX(calc(-100% - var(--gap))); }
}

@keyframes marquee-vertical {
  from { transform: translateY(0); }
  to { transform: translateY(calc(-100% - var(--gap))); }
}
```

### 3. Z-Index Conflicts

**Problem**: Background patterns or effects cover foreground content.

**Solution**: Use proper z-index layering:

```jsx
<div className="relative">
  {/* Background (z-0 or negative) */}
  <GridPattern className="absolute inset-0 -z-10" />

  {/* Content (higher z-index) */}
  <div className="relative z-10">
    <h1>Content appears above pattern</h1>
  </div>
</div>
```

### 4. Performance Issues with Multiple Animated Components

**Problem**: Page lags when multiple heavy animations run simultaneously.

**Solution**: Implement progressive enhancement and conditional rendering:

```jsx
import { useState, useEffect } from 'react'

export default function OptimizedPage() {
  const [enableHeavyEffects, setEnableHeavyEffects] = useState(false)

  useEffect(() => {
    // Check device capability
    const isHighEnd = navigator.hardwareConcurrency > 4 &&
                     !navigator.userAgent.includes('Mobile')
    setEnableHeavyEffects(isHighEnd)
  }, [])

  return (
    <section className="relative">
      {enableHeavyEffects ? (
        <Particles particleCount={300} />
      ) : (
        <GridPattern /> {/* Lighter alternative */}
      )}

      <div className="content">
        {/* Page content */}
      </div>
    </section>
  )
}
```

### 5. TypeScript Type Errors

**Problem**: TypeScript complains about component props.

**Solution**: Extend proper base types:

```typescript
// Magic UI pattern
interface CustomComponentProps extends React.ComponentPropsWithoutRef<"div"> {
  customProp?: string
  className?: string
}

// React Bits pattern
interface CustomProps extends React.HTMLAttributes<HTMLDivElement> {
  customProp?: string
}
```

### 6. Tailwind Classes Not Applied

**Problem**: Custom Tailwind classes in Magic UI components don't work.

**Solution**: Ensure content paths include component directory:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}", // Include components directory
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

## Resources

### Official Documentation
- **Magic UI**: https://magicui.design
- **React Bits**: https://reactbits.dev
- **shadcn/ui**: https://ui.shadcn.com
- **Framer Motion**: https://motion.dev

### Key Scripts
- `scripts/component_importer.py` - Import and customize components from both libraries
- `scripts/props_generator.py` - Generate component prop configurations

### References
- `references/magic_ui_components.md` - Complete Magic UI component catalog with usage examples
- `references/react_bits_components.md` - React Bits component library reference
- `references/customization_guide.md` - Prop-based customization patterns for both libraries

### Starter Assets
- `assets/component_showcase/` - Interactive demo of all components
- `assets/examples/` - Landing page sections, dashboard widgets, micro-interactions

## Related Skills

- **motion-framer**: For understanding underlying animation concepts used by both libraries
- **gsap-scrolltrigger**: Alternative approach for scroll-driven animations
- **react-spring-physics**: Alternative physics-based animation library
- **threejs-webgl**: For 3D background effects as alternative to Particles/Plasma



===== FILE: plugins/individual/animated-component-libraries/skills/animated-component-libraries/references/customization_guide.md =====

# Component Customization Guide

Comprehensive guide for customizing Magic UI and React Bits components through props, styling, and composition.

## Customization Principles

Both libraries follow similar customization patterns:

1. **Prop-Based Customization**: Modify behavior through component props
2. **Class-Based Styling**: Use `className` prop with Tailwind CSS
3. **Composition**: Combine components for complex effects
4. **Theming**: Leverage CSS variables and Tailwind config

## Magic UI Customization

### Pattern Customization

#### Grid Pattern Masking

Create spotlight effects with CSS masks:

```typescript
// Radial gradient mask
<GridPattern
  className="[mask-image:radial-gradient(400px_circle_at_center,white,transparent)]"
/>

// Linear gradient mask
<GridPattern
  className="[mask-image:linear-gradient(to_bottom,white,transparent)]"
/>

// Elliptical mask
<GridPattern
  className="[mask-image:radial-gradient(600px_ellipse_at_top,white,transparent)]"
/>

// Combined with positioning
<GridPattern
  squares={[[4,4], [8,2]]}
  className={cn(
    "[mask-image:radial-gradient(400px_circle_at_center,white,transparent)]",
    "opacity-30",
    "fill-blue-400/20 stroke-blue-400/20"
  )}
/>
```

#### Animated Grid Pattern Timing

Control animation parameters for different effects:

```typescript
// Fast, subtle animation
<AnimatedGridPattern
  numSquares={30}
  maxOpacity={0.3}
  duration={2}
  repeatDelay={0.2}
/>

// Slow, dramatic animation
<AnimatedGridPattern
  numSquares={80}
  maxOpacity={0.8}
  duration={8}
  repeatDelay={1}
/>

// Responsive animation
const isMobile = typeof window !== 'undefined' && window.innerWidth < 768

<AnimatedGridPattern
  numSquares={isMobile ? 20 : 50}
  maxOpacity={isMobile ? 0.3 : 0.5}
  duration={isMobile ? 6 : 4}
/>
```

### Button Customization

#### Shimmer Button Variations

```typescript
// Minimal shimmer
<ShimmerButton
  shimmerColor="rgba(255,255,255,0.2)"
  shimmerSize="0.02em"
  shimmerDuration="4s"
  background="rgba(100,100,100,1)"
  className="px-6 py-2 text-sm"
>
  Subtle Effect
</ShimmerButton>

// Intense shimmer
<ShimmerButton
  shimmerColor="#FFD700"
  shimmerSize="0.1em"
  shimmerDuration="1.5s"
  background="rgba(0,0,0,1)"
  className="px-12 py-4 text-xl font-bold"
>
  Attention Grabber
</ShimmerButton>

// Branded shimmer
<ShimmerButton
  shimmerColor="var(--brand-primary)"
  borderRadius="8px"
  background="var(--brand-secondary)"
  className="px-8 py-3 font-semibold"
>
  Brand Button
</ShimmerButton>
```

#### Border Beam Customization

```typescript
// Slow, wide beam
<BorderBeam duration={20} size={300} />

// Fast, narrow beam
<BorderBeam duration={5} size={80} />

// Multiple beams
<div className="relative">
  <BorderBeam duration={8} size={100} />
  <BorderBeam duration={12} size={150} className="opacity-50" />
</div>
```

### Marquee Customization

#### Speed and Direction

```typescript
// Slow horizontal scroll
<Marquee className="[--duration:60s]">
  {items}
</Marquee>

// Fast horizontal scroll
<Marquee className="[--duration:20s]">
  {items}
</Marquee>

// Reverse direction
<Marquee reverse className="[--duration:40s]">
  {items}
</Marquee>

// Vertical with custom gap
<Marquee
  vertical
  className="h-[600px] [--gap:2rem]"
>
  {items}
</Marquee>
```

#### Content Repetition

```typescript
// Minimal repetition (better performance)
<Marquee repeat={2} className="[--duration:30s]">
  {largeItems}
</Marquee>

// Maximum repetition (smoother loop)
<Marquee repeat={6} className="[--duration:50s]">
  {smallItems}
</Marquee>
```

## React Bits Customization

### BlurText Customization

#### Animation Styles

```tsx
// Fade in from top
<BlurText
  text="Elegant entrance"
  direction="top"
  animationFrom={{ filter: 'blur(10px)', opacity: 0, y: -50 }}
  animationTo={{ filter: 'blur(0px)', opacity: 1, y: 0 }}
/>

// Zoom and blur
<BlurText
  text="Dynamic reveal"
  animationFrom={{ filter: 'blur(20px)', opacity: 0, scale: 0.5 }}
  animationTo={{ filter: 'blur(0px)', opacity: 1, scale: 1 }}
/>

// Slide from side with rotation
<BlurText
  text="Creative animation"
  direction="left"
  animationFrom={{ filter: 'blur(15px)', opacity: 0, x: -100, rotate: -15 }}
  animationTo={{ filter: 'blur(0px)', opacity: 1, x: 0, rotate: 0 }}
/>
```

#### Multi-Stage Animations

```tsx
<BlurText
  text="Complex reveal"
  animateBy="characters"
  animationFrom={{ filter: 'blur(20px)', opacity: 0, y: 100, scale: 0.8 }}
  animationTo={[
    { filter: 'blur(10px)', opacity: 0.3, y: 50, scale: 0.9 },
    { filter: 'blur(5px)', opacity: 0.7, y: 10, scale: 1 },
    { filter: 'blur(0px)', opacity: 1, y: 0, scale: 1 }
  ]}
  stepDuration={0.4}
  easing={(t) => t * t * (3 - 2 * t)} // Smoothstep easing
/>
```

#### Timing Control

```tsx
// Fast reveal
<BlurText
  text="Quick appearance"
  delay={30}
  stepDuration={0.03}
/>

// Slow, dramatic reveal
<BlurText
  text="Suspenseful entrance"
  delay={200}
  stepDuration={0.15}
/>

// Viewport-triggered with custom threshold
<BlurText
  text="Scroll-activated"
  threshold={0.5}
  rootMargin="-50px"
/>
```

### CountUp Customization

#### Formatting Options

```tsx
// Currency formatting
<CountUp
  end={1234567.89}
  duration={3}
  decimals={2}
  prefix="$"
  separator=","
/>
// Displays: $1,234,567.89

// Percentage
<CountUp
  end={75.5}
  decimals={1}
  suffix="%"
/>
// Displays: 75.5%

// Abbreviated large numbers
<CountUp
  end={1500000}
  separator=","
  suffix="+"
/>
// Displays: 1,500,000+

// Compact notation (custom implementation)
const formatCompact = (value) => {
  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`
  return value.toString()
}
```

### Magnet Customization

#### Effect Strength Variations

```tsx
// Subtle magnetic effect
<Magnet
  magnitude={0.15}
  maxDistance={100}
  damping={30}
  stiffness={180}
>
  <button>Gentle Pull</button>
</Magnet>

// Strong magnetic effect
<Magnet
  magnitude={0.6}
  maxDistance={250}
  damping={15}
  stiffness={120}
>
  <div className="card">Strong Attraction</div>
</Magnet>

// Directional restriction (custom)
<Magnet
  magnitude={0.4}
  transformStyle={(x, y) => ({
    transform: `translate(${x}px, 0)` // Only horizontal movement
  })}
>
  <h1>Horizontal Only</h1>
</Magnet>
```

### Dock Customization

#### Physics and Sizing

```tsx
// Bouncy, playful dock
<Dock
  items={items}
  spring={{ mass: 0.2, stiffness: 250, damping: 10 }}
  magnification={100}
  distance={300}
  panelHeight={80}
  baseItemSize={60}
/>

// Smooth, minimal dock
<Dock
  items={items}
  spring={{ mass: 0.08, stiffness: 180, damping: 18 }}
  magnification={50}
  distance={120}
  panelHeight={50}
  baseItemSize={40}
/>

// Professional dock
<Dock
  items={items}
  spring={{ mass: 0.1, stiffness: 200, damping: 15 }}
  magnification={70}
  distance={200}
  panelHeight={64}
  baseItemSize={48}
  className="shadow-xl bg-gray-900/90 backdrop-blur-md rounded-2xl p-2"
/>
```

### Particles Customization

#### Visual Styles

```tsx
// Minimal particles
<Particles
  particleCount={50}
  particleColors={['#ffffff']}
  particleSpread={20}
  speed={0.03}
  particleBaseSize={60}
  sizeRandomness={0.3}
  alphaParticles={true}
  disableRotation={true}
/>

// Dense, colorful particles
<Particles
  particleCount={500}
  particleColors={['#FF0080', '#00FFFF', '#FFFF00', '#00FF00']}
  particleSpread={8}
  speed={0.2}
  particleBaseSize={80}
  sizeRandomness={2}
  alphaParticles={false}
/>

// Interactive particles
<Particles
  particleCount={200}
  particleColors={['#4ECDC4', '#45B7D1']}
  moveParticlesOnHover={true}
  particleHoverFactor={3}
  speed={0.08}
/>
```

## Cross-Library Combinations

### Magic UI Patterns + React Bits Text

```tsx
<div className="relative h-screen">
  {/* Magic UI background */}
  <AnimatedGridPattern
    numSquares={50}
    className="[mask-image:radial-gradient(500px_circle_at_center,white,transparent)]"
  />

  {/* React Bits text animation */}
  <div className="relative z-10 flex items-center justify-center h-full">
    <BlurText
      text="Powerful Combination"
      animateBy="words"
      className="text-7xl font-bold"
    />
  </div>
</div>
```

### Shimmer Button + Magnet Effect

```tsx
import { ShimmerButton } from "@/components/ui/shimmer-button"
import Magnet from "./components/Magnet"

<Magnet magnitude={0.3}>
  <ShimmerButton
    shimmerDuration="3s"
    className="px-8 py-3"
  >
    Interactive CTA
  </ShimmerButton>
</Magnet>
```

### Marquee + CountUp Statistics

```tsx
import { Marquee } from "@/components/ui/marquee"
import CountUp from "./components/CountUp"

<Marquee pauseOnHover>
  {stats.map((stat) => (
    <div key={stat.id} className="mx-8 text-center">
      <CountUp
        end={stat.value}
        separator=","
        className="text-4xl font-bold"
      />
      <p className="text-sm text-gray-600">{stat.label}</p>
    </div>
  ))}
</Marquee>
```

## Theming with CSS Variables

### Creating Theme Variables

```css
/* app/globals.css */
:root {
  --component-duration: 3s;
  --component-primary: #4F46E5;
  --component-secondary: #06B6D4;
  --component-radius: 8px;
  --component-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.dark {
  --component-primary: #818CF8;
  --component-secondary: #22D3EE;
  --component-shadow: 0 10px 40px rgba(255,255,255,0.05);
}
```

### Using Theme Variables

```tsx
// Magic UI with theme
<ShimmerButton
  shimmerColor="var(--component-primary)"
  shimmerDuration="var(--component-duration)"
  borderRadius="var(--component-radius)"
  className="shadow-[var(--component-shadow)]"
>
  Themed Button
</ShimmerButton>

// React Bits with theme
<Particles
  particleColors={[
    'var(--component-primary)',
    'var(--component-secondary)'
  ]}
  speed={0.1}
/>
```

## Responsive Customization

### Breakpoint-Based Props

```tsx
import { useState, useEffect } from 'react'

function useBreakpoint() {
  const [breakpoint, setBreakpoint] = useState('desktop')

  useEffect(() => {
    const updateBreakpoint = () => {
      if (window.innerWidth < 640) setBreakpoint('mobile')
      else if (window.innerWidth < 1024) setBreakpoint('tablet')
      else setBreakpoint('desktop')
    }

    updateBreakpoint()
    window.addEventListener('resize', updateBreakpoint)
    return () => window.removeEventListener('resize', updateBreakpoint)
  }, [])

  return breakpoint
}

export default function ResponsiveComponent() {
  const breakpoint = useBreakpoint()

  const particleConfig = {
    mobile: { count: 50, spread: 15, size: 60 },
    tablet: { count: 150, spread: 12, size: 80 },
    desktop: { count: 300, spread: 10, size: 100 }
  }

  const config = particleConfig[breakpoint]

  return (
    <Particles
      particleCount={config.count}
      particleSpread={config.spread}
      particleBaseSize={config.size}
    />
  )
}
```

### Tailwind Responsive Classes

```tsx
<BlurText
  text="Responsive Text"
  className="text-2xl md:text-4xl lg:text-6xl"
  delay={50}
/>

<AnimatedGridPattern
  numSquares={50}
  className="hidden md:block"
/>

<Marquee className="[--duration:60s] md:[--duration:40s] lg:[--duration:30s]">
  {items}
</Marquee>
```

## Accessibility Customization

### Respect User Preferences

```tsx
const prefersReducedMotion =
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

// Disable animations for reduced motion
<BlurText
  text="Accessible text"
  delay={prefersReducedMotion ? 0 : 100}
  animateBy="none" // Skip animation entirely
/>

<Particles
  particleCount={prefersReducedMotion ? 0 : 200}
  speed={prefersReducedMotion ? 0 : 0.1}
/>

// Or provide alternative visual effect
{prefersReducedMotion ? (
  <div className="gradient-bg static" />
) : (
  <AnimatedGridPattern numSquares={50} />
)}
```

### ARIA Labels and Semantic HTML

```tsx
<div role="presentation" aria-hidden="true">
  <GridPattern /> {/* Decorative only */}
</div>

<Dock
  items={navItems}
  role="navigation"
  aria-label="Main navigation"
/>

<CountUp
  end={10000}
  aria-live="polite"
  aria-label="Total users: 10,000"
/>
```

## Performance Customization

### Conditional Rendering

```tsx
const [isLowPowerMode, setIsLowPowerMode] = useState(false)

useEffect(() => {
  // Detect low power mode or battery status
  if ('getBattery' in navigator) {
    navigator.getBattery().then((battery) => {
      setIsLowPowerMode(battery.level < 0.2)
    })
  }
}, [])

return isLowPowerMode ? (
  <StaticBackground />
) : (
  <Particles particleCount={300} />
)
```

### Lazy Loading Heavy Components

```tsx
import { lazy, Suspense } from 'react'

const Particles = lazy(() => import('./components/Particles'))
const Plasma = lazy(() => import('./components/Plasma'))

export default function OptimizedPage() {
  return (
    <Suspense fallback={<div className="gradient-bg" />}>
      <Particles particleCount={200} />
    </Suspense>
  )
}
```

## Advanced Customization Patterns

### Component Composition

```tsx
// Layered effects
<div className="relative">
  <Particles particleCount={100} className="absolute inset-0" />
  <AnimatedGridPattern
    numSquares={30}
    className="absolute inset-0 opacity-50"
  />
  <div className="relative z-10">
    <BlurText text="Layered Effects" />
  </div>
</div>
```

### Custom Animation Sequences

```tsx
import { motion, AnimatePresence } from "framer-motion"

<AnimatePresence>
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    transition={{ delay: 0.5 }}
  >
    <BlurText text="Delayed text" />

    <motion.div
      initial={{ y: 50 }}
      animate={{ y: 0 }}
      transition={{ delay: 1.5 }}
    >
      <CountUp end={10000} />
    </motion.div>
  </motion.div>
</AnimatePresence>
```

This guide covers the most common customization patterns. For advanced customizations, consult the component source code and extend as needed.



===== FILE: plugins/individual/animated-component-libraries/skills/animated-component-libraries/references/magic_ui_components.md =====

# Magic UI Component Catalog

Complete reference for Magic UI components built on Tailwind CSS, Framer Motion, and shadcn/ui.

## Installation

```bash
# Via shadcn CLI (recommended)
npx shadcn@latest add https://magicui.design/r/[component-name]

# Manual installation
# 1. Copy component code to components/ui/
# 2. Install dependencies: npm install motion clsx tailwind-merge
# 3. Add required CSS animations to globals.css
# 4. Ensure cn() utility exists in lib/utils.ts
```

## Background Patterns

### Grid Pattern

Static SVG grid pattern for backgrounds.

**Props**:
- `width` (number): Grid cell width, default 40
- `height` (number): Grid cell height, default 40
- `x` (number): X offset, default -1
- `y` (number): Y offset, default -1
- `squares` (Array<[x, y]>): Highlighted squares
- `strokeDasharray` (string): Dash pattern, default "0"
- `className` (string): Additional CSS classes

**Usage**:
```typescript
<GridPattern
  squares={[[4, 4], [5, 1], [8, 2]]}
  className="[mask-image:radial-gradient(400px_circle_at_center,white,transparent)]"
/>
```

### Animated Grid Pattern

Animated version with dynamic square animations.

**Props**:
- All GridPattern props
- `numSquares` (number): Number of animated squares, default 50
- `maxOpacity` (number): Maximum opacity, default 0.5
- `duration` (number): Animation duration in seconds, default 4
- `repeatDelay` (number): Delay between repeats, default 0.5

**Usage**:
```typescript
<AnimatedGridPattern
  numSquares={50}
  maxOpacity={0.5}
  duration={4}
  repeatDelay={0.5}
  className="inset-x-0 inset-y-[-30%] h-[200%] skew-y-12"
/>
```

### Interactive Grid Pattern

Grid pattern with interactive squares.

**Props**:
- `width` (number): Cell width, default 40
- `height` (number): Cell height, default 40
- `squares` ([horizontal, vertical]): Grid dimensions, default [24, 24]
- `squaresClassName` (string): Class for squares
- `className` (string): Container class

**Usage**:
```typescript
<InteractiveGridPattern
  squares={[24, 24]}
  className="[mask-image:radial-gradient(400px_circle_at_center,white,transparent)]"
/>
```

### Striped Pattern

Diagonal striped background pattern.

**Props**:
- `direction` ("left" | "right"): Stripe direction, default "left"
- `width` (number): Pattern width, default 10
- `height` (number): Pattern height, default 10
- `className` (string): Additional CSS classes

**Usage**:
```typescript
<StripedPattern
  direction="left"
  className="[mask-image:radial-gradient(300px_circle_at_center,white,transparent)]"
/>
```

## Buttons & Interactive Elements

### Shimmer Button

Button with animated shimmer effect.

**Props**:
- `shimmerColor` (string): Shimmer color, default "#ffffff"
- `shimmerSize` (string): Shimmer size, default "0.05em"
- `shimmerDuration` (string): Animation duration, default "3s"
- `borderRadius` (string): Border radius, default "100px"
- `background` (string): Background color, default "rgba(0, 0, 0, 1)"
- `className` (string): Additional CSS classes
- `children` (ReactNode): Button content
- All standard button props

**Usage**:
```typescript
<ShimmerButton
  shimmerColor="#ffffff"
  shimmerDuration="3s"
  background="rgba(0, 0, 0, 1)"
  className="px-8 py-3"
>
  Get Started
</ShimmerButton>
```

### Border Beam

Animated gradient border effect for containers.

**Props**:
- `duration` (number): Animation duration in seconds, default 15
- `size` (number): Beam width in pixels, default 200
- `className` (string): Additional CSS classes

**Usage**:
```typescript
<Card className="relative overflow-hidden">
  <CardContent>Your content</CardContent>
  <BorderBeam duration={8} size={100} />
</Card>
```

## Text & Typography

### Spinning Text

Text arranged in a circular path with rotation.

**Props**:
- `children` (string): Text content (use • for separators)
- `radius` (number): Circle radius, default 5
- `duration` (number): Rotation duration in seconds, default 10
- `reverse` (boolean): Reverse rotation direction, default false
- `className` (string): Additional CSS classes

**Usage**:
```typescript
<SpinningText
  reverse={false}
  className="text-4xl"
  duration={4}
  radius={6}
>
  learn more • earn more • grow more •
</SpinningText>
```

## Layout Components

### Marquee

Infinite scrolling content container.

**Props**:
- `className` (string): Additional CSS classes
- `reverse` (boolean): Reverse scroll direction, default false
- `pauseOnHover` (boolean): Pause on mouse hover, default false
- `vertical` (boolean): Vertical scrolling, default false
- `repeat` (number): Number of content repetitions, default 4
- `children` (ReactNode): Content to scroll

**Usage**:
```typescript
// Horizontal marquee
<Marquee pauseOnHover className="[--duration:40s]">
  {items.map((item) => (
    <div key={item.id} className="mx-4">
      {item.content}
    </div>
  ))}
</Marquee>

// Vertical marquee
<Marquee vertical reverse className="h-[400px]">
  {items.map((item) => (
    <div key={item.id}>{item.content}</div>
  ))}
</Marquee>
```

### Bento Grid

Responsive grid layout for product features.

**Props**:
- `children` (ReactNode): BentoCard components
- `className` (string): Grid customization classes

**BentoCard Props**:
- `name` (string): Card title
- `className` (string): Card size/position classes
- `background` (ReactNode): Background component/image
- `Icon` (React.ElementType): Icon component
- `description` (string): Card description
- `href` (string): Link URL
- `cta` (string): Call-to-action text

**Usage**:
```typescript
<BentoGrid className="grid-cols-3 gap-4">
  <BentoCard
    name="Feature Name"
    className="col-span-2"
    background={<div className="bg-gradient" />}
    Icon={FeatureIcon}
    description="Description text"
    href="/feature"
    cta="Learn More"
  />
</BentoGrid>
```

## 3D & Visual Effects

### Globe

Interactive 3D globe visualization.

**Props**:
- `className` (string): Additional CSS classes
- Additional THREE.js globe configuration props

**Usage**:
```typescript
<div className="relative flex size-full max-w-lg items-center justify-center">
  <span className="text-8xl font-semibold">Globe</span>
  <Globe className="top-28" />
</div>
```

## Required CSS Animations

Add these to `app/globals.css` for manual installations:

```css
@theme inline {
  --animate-ripple: ripple var(--duration, 2s) ease calc(var(--i, 0) * 0.2s) infinite;
  --animate-shimmer-slide: shimmer-slide var(--speed) ease-in-out infinite alternate;
  --animate-spin-around: spin-around calc(var(--speed) * 2) infinite linear;
  --animate-marquee: marquee var(--duration) linear infinite;
  --animate-marquee-vertical: marquee-vertical var(--duration) linear infinite;
  --animate-beam: beam 3s linear infinite;
}

@keyframes ripple {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    transform: translate(-50%, -50%) scale(0.9);
  }
}

@keyframes shimmer-slide {
  to {
    transform: translate(calc(100cqw - 100%), 0);
  }
}

@keyframes spin-around {
  0% {
    transform: translateZ(0) rotate(0);
  }
  15%, 35% {
    transform: translateZ(0) rotate(90deg);
  }
  65%, 85% {
    transform: translateZ(0) rotate(270deg);
  }
  100% {
    transform: translateZ(0) rotate(360deg);
  }
}

@keyframes marquee {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(calc(-100% - var(--gap)));
  }
}

@keyframes marquee-vertical {
  from {
    transform: translateY(0);
  }
  to {
    transform: translateY(calc(-100% - var(--gap)));
  }
}

@keyframes beam {
  0% {
    background-position: 0% 50%;
  }
  100% {
    background-position: 100% 50%;
  }
}
```

## Utility Function Required

All Magic UI components require the `cn()` utility function:

```typescript
// lib/utils.ts
import clsx, { ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

## Common Component Combinations

### Hero Section with Pattern
```typescript
<div className="relative flex h-screen items-center justify-center">
  <AnimatedGridPattern
    numSquares={50}
    className="[mask-image:radial-gradient(500px_circle_at_center,white,transparent)]"
  />
  <h1 className="relative z-10 text-7xl font-bold">Hero Title</h1>
</div>
```

### CTA Card with Border Beam
```typescript
<Card className="relative overflow-hidden">
  <CardHeader>
    <CardTitle>Premium Plan</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Get all features</p>
    <Button>Subscribe</Button>
  </CardContent>
  <BorderBeam duration={8} />
</Card>
```

### Testimonial Carousel
```typescript
<Marquee pauseOnHover className="py-4">
  {testimonials.map((t) => (
    <div key={t.id} className="mx-4 w-[350px] rounded-lg border p-6">
      <p className="mb-4">"{t.text}"</p>
      <div className="flex gap-3">
        <img src={t.avatar} className="w-10 h-10 rounded-full" />
        <p className="font-semibold">{t.name}</p>
      </div>
    </div>
  ))}
</Marquee>
```

## Tailwind Configuration

Ensure Tailwind can find Magic UI components:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

## Performance Tips

1. **Use CSS Masks**: More performant than clipping paths
2. **Limit Animated Elements**: Reduce `numSquares` on mobile devices
3. **Lazy Load Heavy Components**: Use React.lazy() for Globe and complex components
4. **Optimize Marquee**: Limit `repeat` prop and number of items
5. **Consider Reduced Motion**: Check `prefers-reduced-motion` media query

## TypeScript Support

All Magic UI components are fully typed. Extend props interface when customizing:

```typescript
interface CustomGridPatternProps extends React.ComponentPropsWithoutRef<"svg"> {
  customProp?: string
}
```

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- CSS Grid support required
- SVG support required
- Framer Motion browser requirements apply



===== FILE: plugins/individual/animated-component-libraries/skills/animated-component-libraries/references/react_bits_components.md =====

# React Bits Component Library Reference

Complete reference for React Bits - 90+ animated React components with minimal dependencies.

## Installation

React Bits uses a copy-paste installation model. Visit [reactbits.dev](https://reactbits.dev), browse components, and copy the code directly into your project.

**Common Dependencies**:
```bash
npm install framer-motion  # For animation-heavy components
npm install ogl           # For WebGL components (Particles, Plasma, Aurora)
npm install react-icons   # For icon components (Dock)
```

## Text Animation Components

### BlurText

Text reveal animation with blur effect, triggered by viewport intersection.

**Props**:
- `text` (string, required): Text to animate
- `delay` (number): Delay between characters/words in ms, default 50
- `animateBy` ("characters" | "words"): Animation unit, default "words"
- `direction` ("top" | "bottom" | "left" | "right"): Animation direction, default "top"
- `threshold` (number): Intersection Observer threshold, default 0.1
- `rootMargin` (string): Intersection Observer root margin, default "0px"
- `stepDuration` (number): Duration per step in seconds, default 0.06
- `animationFrom` (object): Initial animation state, default `{ filter: 'blur(10px)', opacity: 0, y: -50 }`
- `animationTo` (object | array): Final animation state(s)
- `easing` (function): Custom easing function
- `onAnimationComplete` (function): Callback when animation completes
- `className` (string): Additional CSS classes

**Usage**:
```jsx
// Basic word-by-word reveal
<BlurText
  text="Transform your ideas into reality"
  delay={100}
  animateBy="words"
  direction="top"
  className="text-5xl font-bold"
/>

// Character-by-character with custom animation
<BlurText
  text="Pixel-perfect animations"
  delay={50}
  animateBy="characters"
  direction="bottom"
  threshold={0.3}
  animationFrom={{ filter: 'blur(20px)', opacity: 0, y: 50, scale: 0.8 }}
  animationTo={{ filter: 'blur(0px)', opacity: 1, y: 0, scale: 1 }}
  easing={(t) => t * t * (3 - 2 * t)} // Smoothstep
  className="text-2xl"
/>
```

### CircularText

Arranges text in a circular path with optional rotation.

**Props**:
- `text` (string, required): Text to display
- `radius` (number): Circle radius in pixels, default 100
- `fontSize` (number): Font size in pixels, default 16
- `rotateText` (boolean): Enable rotation, default false
- `rotationSpeed` (number): Rotation speed, default 1
- `direction` ("clockwise" | "counterclockwise"): Rotation direction, default "clockwise"
- `className` (string): Additional CSS classes

**Usage**:
```jsx
// Static circular text
<CircularText
  text="REACT BITS • REACT BITS • "
  radius={100}
  fontSize={16}
  className="text-blue-500"
/>

// Rotating circular badge
<div className="relative">
  <CircularText
    text="★ NEW FEATURE ★ AVAILABLE NOW ★ "
    radius={80}
    fontSize={14}
    rotateText={true}
    rotationSpeed={0.5}
    direction="clockwise"
    className="text-yellow-400 font-bold"
  />
  <div className="absolute inset-0 flex items-center justify-center">
    <span className="text-2xl font-bold">NEW</span>
  </div>
</div>
```

### CountUp

Animates numbers from start to end value with formatting options.

**Props**:
- `start` (number): Starting number, default 0
- `end` (number, required): Ending number
- `duration` (number): Animation duration in seconds, default 2
- `decimals` (number): Decimal places, default 0
- `prefix` (string): Text before number, default ""
- `suffix` (string): Text after number, default ""
- `separator` (string): Thousands separator, default ""
- `threshold` (number): Intersection Observer threshold, default 0.1
- `rootMargin` (string): Intersection Observer root margin, default "0px"
- `className` (string): Additional CSS classes

**Usage**:
```jsx
// Revenue counter
<CountUp
  start={0}
  end={1000000}
  duration={3}
  separator=","
  prefix="$"
  className="text-6xl font-bold text-blue-600"
/>

// Percentage counter
<CountUp
  end={99.9}
  duration={2.5}
  decimals={1}
  suffix="%"
  className="text-5xl font-bold text-green-600"
/>

// Simple counter
<CountUp
  end={10000}
  duration={2}
  separator=","
  className="text-6xl font-bold"
/>
```

### SpinningText

Similar to CircularText but from React Bits (verify exact component name in library).

## Interactive Components

### Magnet

Creates magnetic pull effect on child elements when cursor is nearby.

**Props**:
- `magnitude` (number): Pull strength, default 0.3
- `maxDistance` (number): Max distance for effect in pixels, default 150
- `damping` (number): Spring damping, default 25
- `stiffness` (number): Spring stiffness, default 200
- `className` (string): Additional CSS classes
- `children` (ReactNode, required): Element to apply effect to

**Usage**:
```jsx
// Magnetic button
<Magnet>
  <button className="px-8 py-3 bg-blue-600 text-white rounded-lg">
    Click Me
  </button>
</Magnet>

// Customized magnetic pull
<Magnet
  magnitude={0.5}
  maxDistance={200}
  damping={20}
  stiffness={150}
>
  <div className="card p-6">
    <h3>Hover to feel the pull</h3>
  </div>
</Magnet>
```

### Dock

macOS-style dock with magnification effect.

**Props**:
- `items` (array, required): Array of dock items
  - Each item: `{ icon: ReactNode, label: string, onClick: function, className?: string }`
- `spring` (object): Spring physics `{ mass, stiffness, damping }`, default `{ mass: 0.1, stiffness: 150, damping: 12 }`
- `magnification` (number): Magnification amount in pixels, default 60
- `distance` (number): Activation distance in pixels, default 140
- `panelHeight` (number): Dock panel height, default 60
- `baseItemSize` (number): Base icon size, default 48
- `dockHeight` (number): Max dock height, default 250
- `className` (string): Additional CSS classes

**Usage**:
```jsx
import Dock from './components/Dock'
import { VscHome, VscArchive, VscAccount } from 'react-icons/vsc'

const dockItems = [
  {
    icon: <VscHome size={24} />,
    label: 'Dashboard',
    onClick: () => navigate('/dashboard')
  },
  {
    icon: <VscArchive size={24} />,
    label: 'Projects',
    onClick: () => navigate('/projects')
  },
  {
    icon: <VscAccount size={24} />,
    label: 'Profile',
    onClick: () => navigate('/profile')
  }
]

<Dock
  items={dockItems}
  spring={{ mass: 0.15, stiffness: 200, damping: 15 }}
  magnification={80}
  distance={250}
  className="dock-custom"
/>
```

### Stepper

Multi-step form/wizard component with navigation.

**Props**:
- `initialStep` (number): Starting step (1-indexed), default 1
- `onStepChange` (function): Callback when step changes `(step: number) => void`
- `onFinalStepCompleted` (function): Callback when final step is completed
- `stepCircleContainerClassName` (string): Step indicator container styles
- `stepContainerClassName` (string): Individual step indicator styles
- `contentClassName` (string): Content area styles
- `footerClassName` (string): Footer area styles
- `backButtonText` (string): Back button text, default "Back"
- `nextButtonText` (string): Next button text, default "Next"
- `backButtonProps` (object): Props for back button
- `nextButtonProps` (object): Props for next button
- `renderStepIndicator` (function): Custom indicator renderer
- `disableStepIndicators` (boolean): Hide step indicators, default false
- `children` (Step components, required): Step content

**Step Component Props**:
- `children` (ReactNode, required): Step content

**Usage**:
```jsx
import Stepper, { Step } from './components/Stepper'

// Basic stepper
<Stepper
  initialStep={1}
  onStepChange={(step) => console.log('Step:', step)}
  onFinalStepCompleted={() => console.log('Complete!')}
>
  <Step>
    <h2>Step 1: Welcome</h2>
    <p>Getting started content</p>
  </Step>
  <Step>
    <h2>Step 2: Profile</h2>
    <input type="text" placeholder="Name" />
  </Step>
  <Step>
    <h2>Step 3: Preferences</h2>
    <label><input type="checkbox" /> Enable notifications</label>
  </Step>
</Stepper>

// Custom styled stepper
<Stepper
  initialStep={1}
  stepContainerClassName="custom-indicators"
  contentClassName="p-8"
  footerClassName="border-t"
  backButtonText="Previous"
  nextButtonText="Continue"
  backButtonProps={{ className: 'btn-secondary' }}
  nextButtonProps={{ className: 'btn-primary' }}
>
  {/* Steps */}
</Stepper>
```

### MagicButton

Button component with special visual effects (verify exact implementation in library).

## Layout Components

### AnimatedList

List container with staggered entrance animations for children.

**Props**:
- `stagger` (number): Delay between items in seconds, default 0.1
- `duration` (number): Animation duration per item in seconds, default 0.5
- `initial` (object): Initial animation state, default `{ opacity: 0, y: 20 }`
- `animate` (object): Final animation state, default `{ opacity: 1, y: 0 }`
- `exit` (object): Exit animation state, default `{ opacity: 0, y: -20 }`
- `className` (string): Additional CSS classes
- `children` (ReactNode, required): List items

**Usage**:
```jsx
// Basic animated list
<AnimatedList className="space-y-4">
  {notifications.map((notif) => (
    <div key={notif.id} className="notification-item">
      <p>{notif.text}</p>
      <span>{notif.time}</span>
    </div>
  ))}
</AnimatedList>

// Custom animation
<AnimatedList
  stagger={0.15}
  duration={0.6}
  initial={{ opacity: 0, x: -50, scale: 0.8 }}
  animate={{ opacity: 1, x: 0, scale: 1 }}
  exit={{ opacity: 0, x: 50, scale: 0.8 }}
>
  {items.map((item) => (
    <div key={item.id}>{item.content}</div>
  ))}
</AnimatedList>
```

## Background & Visual Effects

### Particles

WebGL-powered 3D particle system.

**Props**:
- `particleCount` (number): Number of particles, default 200
- `particleColors` (string[]): Particle colors array, default `['#ffffff']`
- `particleSpread` (number): Spread factor, default 10
- `speed` (number): Movement speed, default 0.1
- `moveParticlesOnHover` (boolean): Mouse interaction, default false
- `particleHoverFactor` (number): Hover effect strength, default 1
- `disableRotation` (boolean): Disable auto-rotation, default false
- `particleBaseSize` (number): Base particle size, default 100
- `sizeRandomness` (number): Size variation factor, default 1
- `alphaParticles` (boolean): Enable transparency, default false
- `cameraDistance` (number): Camera distance, default 20
- `className` (string): Container CSS classes

**Usage**:
```jsx
// Basic particle background
<section style={{ position: 'relative', height: '100vh' }}>
  <Particles className="absolute inset-0" />
  <div className="relative z-10">
    <h1>Content with particles</h1>
  </div>
</section>

// Customized branded particles
<Particles
  particleCount={300}
  particleColors={['#FF6B6B', '#4ECDC4', '#45B7D1']}
  particleSpread={12}
  speed={0.15}
  moveParticlesOnHover={true}
  particleHoverFactor={2}
  particleBaseSize={120}
  sizeRandomness={1.5}
  alphaParticles={true}
  cameraDistance={25}
/>
```

### Plasma

Organic plasma effect using WebGL.

**Props**:
- `color1` (string): First color, default varies
- `color2` (string): Second color, default varies
- `color3` (string): Third color, default varies
- `speed` (number): Animation speed, default 1
- `blur` (number): Blur amount in pixels, default 50
- `className` (string): Additional CSS classes

**Usage**:
```jsx
// Default plasma
<div className="relative min-h-screen">
  <Plasma />
  <div className="relative z-10 p-8">Content</div>
</div>

// Custom colors and speed
<Plasma
  color1="#FF0080"
  color2="#7928CA"
  color3="#00DFD8"
  speed={0.8}
  blur={30}
  className="plasma-bg"
/>
```

### Aurora

Dynamic gradient aurora effect.

**Props**:
- `colors` (string[]): Color array, default varies
- `speed` (number): Animation speed, default 1
- `blur` (number): Blur amount in pixels, default 50
- `className` (string): Additional CSS classes

**Usage**:
```jsx
// Basic aurora
<div style={{ position: 'relative', minHeight: '100vh' }}>
  <Aurora />
  <main style={{ position: 'relative', zIndex: 1 }}>Content</main>
</div>

// Custom aurora colors
<Aurora
  colors={['#FF00FF', '#00FFFF', '#FFFF00']}
  speed={0.5}
  blur={80}
/>
```

### BlobCursor

Custom cursor with blob trail effect.

**Props**:
- `blobType` ("circle" | "square"): Blob shape, default "circle"
- `fillColor` (string): Blob color, default "#5227FF"
- `trailCount` (number): Number of trail blobs, default 3
- `sizes` (number[]): Blob sizes array, default `[40, 80, 120]`
- Additional customization props

**Usage**:
```jsx
<BlobCursor
  blobType="circle"
  fillColor="#5227FF"
  trailCount={3}
  sizes={[60, 125, 75]}
/>
```

## Performance Optimization

### WebGL Components (Particles, Plasma, Aurora)

1. **Reduce Particle Count on Low-End Devices**:
```jsx
const particleCount = navigator.hardwareConcurrency > 4 ? 300 : 150

<Particles particleCount={particleCount} speed={0.1} />
```

2. **Conditional Loading**:
```jsx
const [enableWebGL, setEnableWebGL] = useState(false)

useEffect(() => {
  const isHighEnd = !navigator.userAgent.includes('Mobile') &&
                   navigator.hardwareConcurrency > 4
  setEnableWebGL(isHighEnd)
}, [])

return enableWebGL ? <Particles /> : <div className="gradient-bg" />
```

### Text Animations

1. **Respect Reduced Motion**:
```jsx
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

<BlurText
  text="Accessible text"
  delay={prefersReducedMotion ? 0 : 100}
  animateBy={prefersReducedMotion ? "none" : "words"}
/>
```

2. **Use RequestIdleCallback**:
```jsx
useEffect(() => {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      // Initialize non-critical animations
    })
  }
}, [])
```

## Common Component Combinations

### Hero with Particles + Text Animation
```jsx
<section style={{ position: 'relative', height: '100vh' }}>
  <Particles
    particleCount={200}
    particleColors={['#4ECDC4']}
    className="absolute inset-0"
  />
  <div className="relative z-10 flex items-center justify-center h-full">
    <BlurText
      text="Welcome to the Future"
      delay={100}
      animateBy="words"
      className="text-7xl font-bold"
    />
  </div>
</section>
```

### Dashboard Stats
```jsx
<div className="grid grid-cols-3 gap-8">
  <div className="text-center">
    <CountUp end={10000} separator="," className="text-5xl font-bold" />
    <p>Users</p>
  </div>
  <div className="text-center">
    <CountUp end={99.9} decimals={1} suffix="%" className="text-5xl font-bold" />
    <p>Uptime</p>
  </div>
  <div className="text-center">
    <CountUp end={1000000} prefix="$" separator="," className="text-5xl font-bold" />
    <p>Revenue</p>
  </div>
</div>
```

### Onboarding Flow
```jsx
<Stepper
  initialStep={1}
  onFinalStepCompleted={() => navigate('/dashboard')}
>
  <Step>
    <BlurText text="Welcome!" className="text-4xl font-bold mb-4" />
    <p>Let's get started</p>
  </Step>
  <Step>
    <h2>Profile Setup</h2>
    <form>{/* Form fields */}</form>
  </Step>
  <Step>
    <h2>All Set!</h2>
    <CountUp end={100} suffix="%" />
  </Step>
</Stepper>
```

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- WebGL support required for Particles, Plasma, Aurora
- Intersection Observer support required for BlurText, CountUp
- Framer Motion browser requirements apply

## TypeScript Support

React Bits components include TypeScript definitions. Extend interfaces as needed:

```typescript
interface CustomBlurTextProps extends React.HTMLAttributes<HTMLDivElement> {
  customProp?: string
}
```



===== FILE: plugins/individual/animated-component-libraries/agents/animated-component-libraries-specialist.md =====

# Animated Component Libraries Specialist

## Role

Expert specialist in Animated Component Libraries implementation, patterns, and best practices.

## Expertise

- Animated Component Libraries core concepts and patterns
- Integration with other libraries and frameworks
- Performance optimization
- Common pitfalls and solutions
- Best practices and conventions

## When to use

Activate this agent when working on:
- Animated Component Libraries implementation challenges
- Integration with other technologies
- Performance optimization
- Troubleshooting and debugging
- Architecture decisions

## Approach

1. Understand project requirements and context
2. Apply Animated Component Libraries best practices
3. Recommend optimal implementation patterns
4. Identify and solve common issues
5. Provide detailed guidance and examples

## Tools

This agent has access to:
- Animated Component Libraries skill knowledge
- Pattern libraries and examples
- Troubleshooting guides
- Integration patterns



===== FILE: plugins/individual/animated-component-libraries/commands/component_importer.md =====

# /animated-component-libraries-component_importer

Animated Component Libraries - Component Importer

## Description

Executes the component_importer script for Animated Component Libraries.

## Usage

```bash
/animated-component-libraries-component_importer
```

## Implementation

This command runs the `component_importer.py` script from the Animated Component Libraries skill, which provides automated assistance for component importer.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/animated-component-libraries/commands/props_generator.md =====

# /animated-component-libraries-props_generator

Animated Component Libraries - Props Generator

## Description

Executes the props_generator script for Animated Component Libraries.

## Usage

```bash
/animated-component-libraries-props_generator
```

## Implementation

This command runs the `props_generator.py` script from the Animated Component Libraries skill, which provides automated assistance for props generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/animated-component-libraries/skills/animated-component-libraries/scripts/component_importer.py =====

```py
#!/usr/bin/env python3
"""
Component Importer

Assists with importing and customizing components from Magic UI and React Bits.
Generates installation commands and boilerplate code for selected components.

Usage:
    ./component_importer.py                      # Interactive mode
    ./component_importer.py --library magicui --component grid-pattern
    ./component_importer.py --library reactbits --component blur-text
"""

import sys
import argparse

# Magic UI components catalog
MAGIC_UI_COMPONENTS = {
    "grid-pattern": {
        "name": "Grid Pattern",
        "install": "npx shadcn@latest add https://magicui.design/r/grid-pattern",
        "deps": ["motion", "clsx", "tailwind-merge"],
        "css_required": False
    },
    "animated-grid-pattern": {
        "name": "Animated Grid Pattern",
        "install": "npx shadcn@latest add https://magicui.design/r/animated-grid-pattern",
        "deps": ["motion", "clsx", "tailwind-merge"],
        "css_required": True,
        "css_keyframes": ["grid-fade"]
    },
    "shimmer-button": {
        "name": "Shimmer Button",
        "install": "npx shadcn@latest add https://magicui.design/r/shimmer-button",
        "deps": ["motion", "clsx", "tailwind-merge"],
        "css_required": True,
        "css_keyframes": ["shimmer-slide", "spin-around"]
    },
    "border-beam": {
        "name": "Border Beam",
        "install": "npx shadcn@latest add https://magicui.design/r/border-beam",
        "deps": ["motion", "clsx", "tailwind-merge"],
        "css_required": True,
        "css_keyframes": ["beam"]
    },
    "marquee": {
        "name": "Marquee",
        "install": "npx shadcn@latest add https://magicui.design/r/marquee",
        "deps": ["motion", "clsx", "tailwind-merge"],
        "css_required": True,
        "css_keyframes": ["marquee", "marquee-vertical"]
    },
    "spinning-text": {
        "name": "Spinning Text",
        "install": "npx shadcn@latest add https://magicui.design/r/spinning-text",
        "deps": ["motion", "clsx", "tailwind-merge"],
        "css_required": False
    },
    "bento-grid": {
        "name": "Bento Grid",
        "install": "Manual installation (copy from website)",
        "deps": ["@radix-ui/react-icons"],
        "css_required": False
    }
}

# React Bits components catalog
REACT_BITS_COMPONENTS = {
    "blur-text": {
        "name": "BlurText",
        "install": "Manual copy from reactbits.dev",
        "deps": ["framer-motion"],
        "path": "components/BlurText.jsx"
    },
    "count-up": {
        "name": "CountUp",
        "install": "Manual copy from reactbits.dev",
        "deps": ["framer-motion"],
        "path": "components/CountUp.jsx"
    },
    "magnet": {
        "name": "Magnet",
        "install": "Manual copy from reactbits.dev",
        "deps": ["framer-motion"],
        "path": "components/Magnet.jsx"
    },
    "dock": {
        "name": "Dock",
        "install": "Manual copy from reactbits.dev",
        "deps": ["framer-motion", "react-icons"],
        "path": "components/Dock.jsx"
    },
    "stepper": {
        "name": "Stepper",
        "install": "Manual copy from reactbits.dev",
        "deps": ["framer-motion"],
        "path": "components/Stepper.jsx"
    },
    "particles": {
        "name": "Particles (WebGL)",
        "install": "Manual copy from reactbits.dev",
        "deps": ["ogl"],
        "path": "components/Particles.jsx"
    },
    "plasma": {
        "name": "Plasma",
        "install": "Manual copy from reactbits.dev",
        "deps": ["ogl"],
        "path": "components/Plasma.jsx"
    },
    "aurora": {
        "name": "Aurora",
        "install": "Manual copy from reactbits.dev",
        "deps": [],
        "path": "components/Aurora.jsx"
    }
}


def print_magic_ui_instructions(component_key):
    """Print installation instructions for Magic UI component."""
    comp = MAGIC_UI_COMPONENTS.get(component_key)
    if not comp:
        print(f"Error: Component '{component_key}' not found in Magic UI catalog")
        return

    print(f"\n{'='*60}")
    print(f"Magic UI: {comp['name']}")
    print(f"{'='*60}\n")

    print("Step 1: Install component")
    print(f"  {comp['install']}\n")

    if comp['deps']:
        print("Step 2: Install dependencies")
        deps_cmd = "npm install " + " ".join(comp['deps'])
        print(f"  {deps_cmd}\n")

    if comp.get('css_required'):
        print("Step 3: Add CSS animations to globals.css")
        print("  See references/magic_ui_components.md for keyframes\n")

    print("Step 4: Ensure cn() utility exists")
    print("  lib/utils.ts should contain the cn() function\n")

    print("Usage example:")
    if component_key == "grid-pattern":
        print("""  import { GridPattern } from "@/components/ui/grid-pattern"

  <GridPattern
    squares={[[4, 4], [8, 2]]}
    className="[mask-image:radial-gradient(400px_circle_at_center,white,transparent)]"
  />""")
    elif component_key == "shimmer-button":
        print("""  import { ShimmerButton } from "@/components/ui/shimmer-button"

  <ShimmerButton
    shimmerDuration="3s"
    className="px-8 py-3"
  >
    Click Me
  </ShimmerButton>""")
    elif component_key == "marquee":
        print("""  import { Marquee } from "@/components/ui/marquee"

  <Marquee pauseOnHover className="[--duration:40s]">
    {items.map((item) => <div key={item.id}>{item.content}</div>)}
  </Marquee>""")

    print()


def print_react_bits_instructions(component_key):
    """Print installation instructions for React Bits component."""
    comp = REACT_BITS_COMPONENTS.get(component_key)
    if not comp:
        print(f"Error: Component '{component_key}' not found in React Bits catalog")
        return

    print(f"\n{'='*60}")
    print(f"React Bits: {comp['name']}")
    print(f"{'='*60}\n")

    print("Step 1: Copy component code")
    print(f"  Visit https://reactbits.dev")
    print(f"  Find '{comp['name']}' component")
    print(f"  Copy code to: {comp['path']}\n")

    if comp['deps']:
        print("Step 2: Install dependencies")
        deps_cmd = "npm install " + " ".join(comp['deps'])
        print(f"  {deps_cmd}\n")

    print("Usage example:")
    if component_key == "blur-text":
        print("""  import BlurText from './components/BlurText'

  <BlurText
    text="Animated text reveal"
    delay={100}
    animateBy="words"
    className="text-5xl font-bold"
  />""")
    elif component_key == "count-up":
        print("""  import CountUp from './components/CountUp'

  <CountUp
    end={10000}
    duration={3}
    separator=","
    className="text-6xl font-bold"
  />""")
    elif component_key == "particles":
        print("""  import Particles from './components/Particles'

  <Particles
    particleCount={200}
    particleColors={['#FF6B6B', '#4ECDC4']}
    className="absolute inset-0"
  />""")

    print()


def interactive_mode():
    """Run interactive component selector."""
    print("\nComponent Importer - Interactive Mode")
    print("="*60)

    print("\nSelect library:")
    print("  1. Magic UI")
    print("  2. React Bits")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "1":
        print("\nMagic UI Components:")
        components = list(MAGIC_UI_COMPONENTS.keys())
        for idx, key in enumerate(components, 1):
            print(f"  {idx}. {MAGIC_UI_COMPONENTS[key]['name']}")

        comp_choice = input(f"\nSelect component (1-{len(components)}): ").strip()
        try:
            comp_idx = int(comp_choice) - 1
            if 0 <= comp_idx < len(components):
                print_magic_ui_instructions(components[comp_idx])
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")

    elif choice == "2":
        print("\nReact Bits Components:")
        components = list(REACT_BITS_COMPONENTS.keys())
        for idx, key in enumerate(components, 1):
            print(f"  {idx}. {REACT_BITS_COMPONENTS[key]['name']}")

        comp_choice = input(f"\nSelect component (1-{len(components)}): ").strip()
        try:
            comp_idx = int(comp_choice) - 1
            if 0 <= comp_idx < len(components):
                print_react_bits_instructions(components[comp_idx])
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")
    else:
        print("Invalid library choice")


def main():
    parser = argparse.ArgumentParser(
        description="Import and customize Magic UI or React Bits components"
    )
    parser.add_argument(
        "--library",
        choices=["magicui", "reactbits"],
        help="Component library (magicui or reactbits)"
    )
    parser.add_argument(
        "--component",
        help="Component name (e.g., 'grid-pattern', 'blur-text')"
    )

    args = parser.parse_args()

    if args.library and args.component:
        # CLI mode
        if args.library == "magicui":
            print_magic_ui_instructions(args.component)
        elif args.library == "reactbits":
            print_react_bits_instructions(args.component)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()

```


===== FILE: plugins/individual/animated-component-libraries/skills/animated-component-libraries/scripts/props_generator.py =====

```py
#!/usr/bin/env python3
"""
Props Generator

Generates component prop configurations for Magic UI and React Bits components.
Outputs TypeScript/JSX code with customizable prop values.

Usage:
    ./props_generator.py                                    # Interactive mode
    ./props_generator.py --component shimmer-button --format typescript
    ./props_generator.py --component blur-text --format jsx
"""

import sys
import argparse
import json

# Component prop templates
COMPONENT_PROPS = {
    "shimmer-button": {
        "library": "Magic UI",
        "props": {
            "shimmerColor": {"type": "string", "default": "#ffffff"},
            "shimmerSize": {"type": "string", "default": "0.05em"},
            "shimmerDuration": {"type": "string", "default": "3s"},
            "borderRadius": {"type": "string", "default": "100px"},
            "background": {"type": "string", "default": "rgba(0, 0, 0, 1)"},
            "className": {"type": "string", "default": "px-8 py-3"}
        }
    },
    "grid-pattern": {
        "library": "Magic UI",
        "props": {
            "width": {"type": "number", "default": 40},
            "height": {"type": "number", "default": 40},
            "x": {"type": "number", "default": -1},
            "y": {"type": "number", "default": -1},
            "squares": {"type": "array", "default": "[[4, 4], [8, 2]]"},
            "strokeDasharray": {"type": "string", "default": "0"},
            "className": {"type": "string", "default": ""}
        }
    },
    "animated-grid-pattern": {
        "library": "Magic UI",
        "props": {
            "numSquares": {"type": "number", "default": 50},
            "maxOpacity": {"type": "number", "default": 0.5},
            "duration": {"type": "number", "default": 4},
            "repeatDelay": {"type": "number", "default": 0.5},
            "className": {"type": "string", "default": ""}
        }
    },
    "blur-text": {
        "library": "React Bits",
        "props": {
            "text": {"type": "string", "default": "Your text here", "required": True},
            "delay": {"type": "number", "default": 100},
            "animateBy": {"type": "enum", "values": ["characters", "words"], "default": "words"},
            "direction": {"type": "enum", "values": ["top", "bottom", "left", "right"], "default": "top"},
            "threshold": {"type": "number", "default": 0.1},
            "className": {"type": "string", "default": ""}
        }
    },
    "count-up": {
        "library": "React Bits",
        "props": {
            "start": {"type": "number", "default": 0},
            "end": {"type": "number", "default": 100, "required": True},
            "duration": {"type": "number", "default": 2},
            "decimals": {"type": "number", "default": 0},
            "prefix": {"type": "string", "default": ""},
            "suffix": {"type": "string", "default": ""},
            "separator": {"type": "string", "default": ""},
            "className": {"type": "string", "default": ""}
        }
    },
    "particles": {
        "library": "React Bits",
        "props": {
            "particleCount": {"type": "number", "default": 200},
            "particleColors": {"type": "array", "default": "['#ffffff']"},
            "particleSpread": {"type": "number", "default": 10},
            "speed": {"type": "number", "default": 0.1},
            "moveParticlesOnHover": {"type": "boolean", "default": False},
            "particleBaseSize": {"type": "number", "default": 100},
            "className": {"type": "string", "default": ""}
        }
    },
    "magnet": {
        "library": "React Bits",
        "props": {
            "magnitude": {"type": "number", "default": 0.3},
            "maxDistance": {"type": "number", "default": 150},
            "damping": {"type": "number", "default": 25},
            "stiffness": {"type": "number", "default": 200},
            "className": {"type": "string", "default": ""}
        }
    },
    "marquee": {
        "library": "Magic UI",
        "props": {
            "reverse": {"type": "boolean", "default": False},
            "pauseOnHover": {"type": "boolean", "default": False},
            "vertical": {"type": "boolean", "default": False},
            "repeat": {"type": "number", "default": 4},
            "className": {"type": "string", "default": ""}
        }
    }
}


def format_prop_value(prop_type, value):
    """Format prop value based on type."""
    if prop_type == "string":
        return f'"{value}"'
    elif prop_type == "boolean":
        return "true" if value else "false"
    elif prop_type == "array":
        return value  # Already formatted
    elif prop_type == "enum":
        return f'"{value}"'
    else:  # number
        return str(value)


def generate_tsx_code(component_name, custom_props=None):
    """Generate TypeScript/JSX code for component."""
    if component_name not in COMPONENT_PROPS:
        return f"Error: Component '{component_name}' not found"

    comp = COMPONENT_PROPS[component_name]
    props = comp["props"].copy()

    # Apply custom props
    if custom_props:
        for key, value in custom_props.items():
            if key in props:
                props[key]["default"] = value

    # Generate import statement
    if comp["library"] == "Magic UI":
        component_pascal = ''.join(word.capitalize() for word in component_name.split('-'))
        import_stmt = f'import {{ {component_pascal} }} from "@/components/ui/{component_name}"'
    else:  # React Bits
        component_pascal = ''.join(word.capitalize() for word in component_name.split('-'))
        import_stmt = f'import {component_pascal} from "./components/{component_pascal}"'

    # Generate component code
    code_lines = [import_stmt, "", f"<{component_pascal}"]

    for prop_name, prop_info in props.items():
        value = format_prop_value(prop_info["type"], prop_info["default"])

        # Skip empty strings for className
        if prop_name == "className" and prop_info["default"] == "":
            continue

        code_lines.append(f"  {prop_name}={{{value}}}")

    code_lines.append(">")

    # Add children for certain components
    if component_name in ["shimmer-button", "magnet"]:
        code_lines.append("  {children}")
        code_lines.append(f"</{component_pascal}>")
    elif component_name == "marquee":
        code_lines.append("  {items.map((item) => (")
        code_lines.append("    <div key={item.id}>{item.content}</div>")
        code_lines.append("  ))}")
        code_lines.append(f"</{component_pascal}>")
    else:
        code_lines.append(f"/>")

    return "\n".join(code_lines)


def generate_jsx_code(component_name, custom_props=None):
    """Generate JSX code for component (similar to TSX but without type annotations)."""
    # For this simple generator, JSX is the same as TSX
    return generate_tsx_code(component_name, custom_props)


def list_available_components():
    """List all available components."""
    print("\nAvailable Components:")
    print("="*60)

    magic_ui = [k for k, v in COMPONENT_PROPS.items() if v["library"] == "Magic UI"]
    react_bits = [k for k, v in COMPONENT_PROPS.items() if v["library"] == "React Bits"]

    print("\nMagic UI:")
    for comp in magic_ui:
        print(f"  - {comp}")

    print("\nReact Bits:")
    for comp in react_bits:
        print(f"  - {comp}")

    print()


def interactive_mode():
    """Run interactive props generator."""
    print("\nProps Generator - Interactive Mode")
    print("="*60)

    list_available_components()

    component = input("Enter component name: ").strip().lower()

    if component not in COMPONENT_PROPS:
        print(f"Error: Component '{component}' not found")
        return

    comp_info = COMPONENT_PROPS[component]

    print(f"\n{comp_info['library']}: {component}")
    print("="*60)

    print("\nAvailable props (press Enter to use default):")

    custom_props = {}
    for prop_name, prop_info in comp_info["props"].items():
        required_marker = " (required)" if prop_info.get("required") else ""
        default_display = prop_info["default"]

        if prop_info["type"] == "enum":
            print(f"\n{prop_name}{required_marker} (options: {', '.join(prop_info['values'])})")
        else:
            print(f"\n{prop_name}{required_marker}")

        print(f"  Type: {prop_info['type']}")
        print(f"  Default: {default_display}")

        value = input(f"  Value: ").strip()

        if value:
            # Convert value based on type
            if prop_info["type"] == "number":
                try:
                    custom_props[prop_name] = float(value) if '.' in value else int(value)
                except ValueError:
                    print("  Invalid number, using default")
            elif prop_info["type"] == "boolean":
                custom_props[prop_name] = value.lower() in ["true", "yes", "1"]
            else:
                custom_props[prop_name] = value

    print("\nGenerated code:")
    print("="*60)
    print(generate_tsx_code(component, custom_props))
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Generate component prop configurations"
    )
    parser.add_argument(
        "--component",
        help="Component name (e.g., 'shimmer-button', 'blur-text')"
    )
    parser.add_argument(
        "--format",
        choices=["tsx", "jsx"],
        default="tsx",
        help="Output format (tsx or jsx)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available components"
    )
    parser.add_argument(
        "--props",
        help="Custom props as JSON string"
    )

    args = parser.parse_args()

    if args.list:
        list_available_components()
    elif args.component:
        custom_props = None
        if args.props:
            try:
                custom_props = json.loads(args.props)
            except json.JSONDecodeError:
                print("Error: Invalid JSON in --props argument")
                return

        if args.format == "tsx":
            print(generate_tsx_code(args.component, custom_props))
        else:
            print(generate_jsx_code(args.component, custom_props))
    else:
        interactive_mode()


if __name__ == "__main__":
    main()

```


===== FILE: plugins/individual/animated-component-libraries/skills/animated-component-libraries/assets/README.md =====

# Animated Component Libraries - Assets

This directory contains starter templates and example code for Magic UI and React Bits components.

## Quick Start Templates

### Magic UI + shadcn/ui Starter

Create a new Next.js project with Magic UI components:

```bash
# Create Next.js app with TypeScript and Tailwind
npx create-next-app@latest my-magic-ui-app --typescript --tailwind --app

cd my-magic-ui-app

# Install dependencies
npm install motion clsx tailwind-merge

# Install shadcn/ui
npx shadcn@latest init

# Add Magic UI components
npx shadcn@latest add https://magicui.design/r/grid-pattern
npx shadcn@latest add https://magicui.design/r/shimmer-button
npx shadcn@latest add https://magicui.design/r/marquee
```

**Required: lib/utils.ts**
```typescript
import clsx, { ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

**Required: app/globals.css (add animations)**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@theme inline {
  --animate-marquee: marquee var(--duration) linear infinite;
  --animate-shimmer-slide: shimmer-slide var(--speed) ease-in-out infinite alternate;
}

@keyframes marquee {
  from { transform: translateX(0); }
  to { transform: translateX(calc(-100% - var(--gap))); }
}

@keyframes shimmer-slide {
  to { transform: translate(calc(100cqw - 100%), 0); }
}
```

### React Bits Starter

Create a Vite + React project with React Bits components:

```bash
# Create Vite app
npm create vite@latest my-react-bits-app -- --template react

cd my-react-bits-app

# Install dependencies
npm install
npm install framer-motion
npm install ogl  # For WebGL components (Particles, Plasma, Aurora)
```

**Copy components from reactbits.dev**:
- Visit https://reactbits.dev
- Browse component gallery
- Click "View Code" on desired component
- Copy to `src/components/`

## Example Implementations

### Landing Page with Magic UI

**app/page.tsx**
```typescript
import { GridPattern } from "@/components/ui/grid-pattern"
import { AnimatedGridPattern } from "@/components/ui/animated-grid-pattern"
import { ShimmerButton } from "@/components/ui/shimmer-button"
import { Marquee } from "@/components/ui/marquee"
import { cn } from "@/lib/utils"

const testimonials = [
  { id: 1, name: "John Doe", text: "Amazing product!", avatar: "/avatar1.jpg" },
  { id: 2, name: "Jane Smith", text: "Exceeded expectations", avatar: "/avatar2.jpg" }
]

export default function Home() {
  return (
    <main>
      {/* Hero Section */}
      <section className="relative flex h-screen items-center justify-center overflow-hidden">
        <AnimatedGridPattern
          numSquares={50}
          maxOpacity={0.5}
          duration={4}
          className={cn(
            "[mask-image:radial-gradient(500px_circle_at_center,white,transparent)]",
            "inset-x-0 inset-y-[-30%] h-[200%] skew-y-12"
          )}
        />
        <div className="relative z-10 text-center">
          <h1 className="text-7xl font-bold mb-8">Welcome to the Future</h1>
          <ShimmerButton
            shimmerDuration="3s"
            className="px-8 py-3"
          >
            Get Started
          </ShimmerButton>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20">
        <h2 className="text-4xl font-bold text-center mb-12">Testimonials</h2>
        <Marquee pauseOnHover className="[--duration:40s]">
          {testimonials.map((item) => (
            <div key={item.id} className="mx-4 w-[350px] rounded-lg border p-6">
              <p className="text-lg mb-4">"{item.text}"</p>
              <div className="flex items-center gap-3">
                <img src={item.avatar} alt={item.name} className="w-10 h-10 rounded-full" />
                <p className="font-semibold">{item.name}</p>
              </div>
            </div>
          ))}
        </Marquee>
      </section>
    </main>
  )
}
```

### Interactive Dashboard with React Bits

**src/App.jsx**
```jsx
import { useState } from 'react'
import CountUp from './components/CountUp'
import BlurText from './components/BlurText'
import Particles from './components/Particles'
import './App.css'

function App() {
  return (
    <div className="app">
      {/* Background */}
      <Particles
        particleCount={150}
        particleColors={['#4ECDC4', '#45B7D1']}
        particleSpread={10}
        speed={0.1}
        className="fixed inset-0"
      />

      {/* Content */}
      <div className="relative z-10 min-h-screen p-8">
        <BlurText
          text="Analytics Dashboard"
          delay={100}
          animateBy="words"
          className="text-6xl font-bold text-center mb-16"
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Stats */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-8 text-center">
            <CountUp
              end={10000}
              duration={2}
              separator=","
              className="text-5xl font-bold text-blue-500"
            />
            <p className="text-xl mt-2">Active Users</p>
          </div>

          <div className="bg-white/10 backdrop-blur-md rounded-xl p-8 text-center">
            <CountUp
              end={99.9}
              duration={2.5}
              decimals={1}
              suffix="%"
              className="text-5xl font-bold text-green-500"
            />
            <p className="text-xl mt-2">Uptime</p>
          </div>

          <div className="bg-white/10 backdrop-blur-md rounded-xl p-8 text-center">
            <CountUp
              end={1000000}
              duration={3}
              prefix="$"
              separator=","
              className="text-5xl font-bold text-purple-500"
            />
            <p className="text-xl mt-2">Revenue</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
```

## Component Showcase Examples

### Complete examples are available at:

**Magic UI**:
- Official examples: https://magicui.design
- GitHub repository: https://github.com/magicuidesign/magicui
- Component registry: Browse site for live demos

**React Bits**:
- Official examples: https://reactbits.dev
- Component demos: Each component page includes live preview
- GitHub: https://github.com/davidhdev/react-bits

## Integration Examples

### Combining Libraries

Both libraries can be used together in the same project:

```jsx
// Magic UI for structural patterns
import { GridPattern } from "@/components/ui/grid-pattern"
import { Marquee } from "@/components/ui/marquee"

// React Bits for interactive elements
import BlurText from './components/BlurText'
import CountUp from './components/CountUp'
import Particles from './components/Particles'

export default function HybridPage() {
  return (
    <div className="relative">
      {/* React Bits background */}
      <Particles particleCount={100} className="fixed inset-0" />

      {/* Magic UI pattern overlay */}
      <GridPattern
        squares={[[4,4], [8,2]]}
        className="absolute inset-0 opacity-30 -z-10"
      />

      {/* Content */}
      <div className="relative z-10 p-8">
        <BlurText
          text="Best of Both Worlds"
          className="text-6xl font-bold mb-8"
        />

        <Marquee>
          {items.map((item) => (
            <div key={item.id} className="mx-4">
              <CountUp end={item.value} />
            </div>
          ))}
        </Marquee>
      </div>
    </div>
  )
}
```

## Production-Ready Patterns

### Performance-Optimized Setup

```jsx
import { lazy, Suspense, useState, useEffect } from 'react'

// Lazy load heavy components
const Particles = lazy(() => import('./components/Particles'))
const AnimatedGridPattern = lazy(() => import('@/components/ui/animated-grid-pattern'))

export default function OptimizedPage() {
  const [enableHeavyEffects, setEnableHeavyEffects] = useState(false)

  useEffect(() => {
    // Enable on high-end devices only
    const isHighEnd = navigator.hardwareConcurrency > 4 &&
                     !navigator.userAgent.includes('Mobile')
    setEnableHeavyEffects(isHighEnd)
  }, [])

  return (
    <div className="relative">
      {enableHeavyEffects ? (
        <Suspense fallback={<div className="gradient-bg" />}>
          <Particles particleCount={200} />
        </Suspense>
      ) : (
        <div className="static-gradient-bg" />
      )}

      {/* Content */}
    </div>
  )
}
```

### Accessibility-First Implementation

```jsx
const prefersReducedMotion =
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

<BlurText
  text="Accessible text reveal"
  delay={prefersReducedMotion ? 0 : 100}
  animateBy={prefersReducedMotion ? "none" : "words"}
/>

<div role="presentation" aria-hidden="true">
  <GridPattern /> {/* Decorative only */}
</div>

<CountUp
  end={10000}
  aria-live="polite"
  aria-label="Total users: 10,000"
/>
```

## Additional Resources

- **Magic UI Documentation**: https://magicui.design/docs
- **React Bits Documentation**: https://reactbits.dev/docs
- **Framer Motion**: https://motion.dev
- **shadcn/ui**: https://ui.shadcn.com
- **Tailwind CSS**: https://tailwindcss.com

## Scripts

Use the provided scripts to assist with component implementation:

```bash
# Import component with instructions
../scripts/component_importer.py

# Generate component props
../scripts/props_generator.py
```

## Notes

1. **Magic UI** requires shadcn/ui setup and cn() utility
2. **React Bits** uses manual copy-paste installation
3. **WebGL components** (Particles, Plasma, Aurora) require `ogl` package
4. **Performance**: Test on target devices, especially for WebGL components
5. **Accessibility**: Always test with screen readers and keyboard navigation



# Skill: modern-web-design


===== FILE: plugins/individual/modern-web-design/skills/modern-web-design/SKILL.md =====

---
name: modern-web-design
description: Modern web design trends, principles, and implementation patterns for 2024-2025. Use this skill when designing websites, creating interactive experiences, implementing design systems, ensuring accessibility, or building performance-first interfaces. Triggers on tasks involving modern design trends, micro-interactions, scrollytelling, bold minimalism, cursor UX, glassmorphism, accessibility compliance, performance optimization, or design system architecture. References animation skills (GSAP, Framer Motion, React Spring), 3D skills (Three.js, R3F, Babylon.js), and component libraries for implementation guidance.
---

# Modern Web Design

## Overview

Modern web design in 2024-2025 emphasizes performance, accessibility, and meaningful interactions. This skill provides comprehensive guidance on current design trends, implementation patterns, and best practices for creating engaging, accessible, and performant web experiences.

This meta-skill synthesizes knowledge from all animation, interaction, and 3D skills in this repository to provide holistic design guidance.

## Core Design Principles (2024-2025)

### 1. Performance-First Design

**Philosophy**: Design decisions should prioritize Core Web Vitals and user experience on all devices.

**Key Metrics**:
- Largest Contentful Paint (LCP): < 2.5s
- First Input Delay (FID): < 100ms
- Cumulative Layout Shift (CLS): < 0.1
- Interaction to Next Paint (INP): < 200ms

**Implementation Guidelines**:
- Defer non-critical animations until after page load
- Use CSS transforms/opacity for animations (GPU-accelerated)
- Implement lazy loading for images, videos, and 3D content
- Progressive enhancement: core content without JavaScript

**Related Skills**: `gsap-scrolltrigger`, `motion-framer`, `lottie-animations` for optimized animations

### 2. Bold Minimalism

**Characteristics**:
- Large, impactful typography (clamp() for fluid sizing)
- Ample white space (negative space as design element)
- Limited color palettes (3-5 primary colors)
- Intentional use of bold accent colors
- Geometric shapes and clean lines

**Typography Scale** (Modern fluid system):
```css
/* Fluid typography using clamp() */
--font-size-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
--font-size-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
--font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
--font-size-lg: clamp(1.25rem, 1.1rem + 0.75vw, 1.75rem);
--font-size-xl: clamp(1.75rem, 1.5rem + 1.25vw, 2.5rem);
--font-size-2xl: clamp(2.5rem, 2rem + 2.5vw, 4rem);
--font-size-3xl: clamp(3.5rem, 2.5rem + 5vw, 6rem);
```

**Color System** (Accessibility-first):
```css
/* WCAG AAA compliant color system */
--color-primary: oklch(50% 0.2 250); /* Blue */
--color-accent: oklch(65% 0.25 30);  /* Coral */
--color-neutral-50: oklch(98% 0 0);
--color-neutral-900: oklch(20% 0 0);
/* Contrast ratio: minimum 7:1 for text */
```

**Related Skills**: `animated-component-libraries` for UI components

### 3. Micro-Interactions

**Definition**: Small, purposeful animations that provide feedback, guide users, and enhance perceived performance.

**Categories**:

**a) Hover States** (Desktop):
- Scale transformations (1.05-1.1x)
- Color transitions (200-300ms)
- Shadow depth changes
- Cursor transformations

**b) Loading States**:
- Skeleton screens (better than spinners)
- Progressive image loading (blur-up technique)
- Optimistic UI updates
- Staggered content reveals

**c) Interactive Feedback**:
- Button press states (scale down 0.95x)
- Toggle switches with spring physics
- Form field validation (immediate, kind feedback)
- Success/error states with motion

**Implementation Example** (Framer Motion):
```jsx
// Button with micro-interaction
<motion.button
  whileHover={{ scale: 1.05, y: -2 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  Click me
</motion.button>
```

**Related Skills**: `motion-framer`, `react-spring-physics`, `animejs` for micro-interactions

### 4. Scrollytelling

**Definition**: Narrative-driven experiences where content reveals and transforms as the user scrolls.

**Patterns**:

**a) Scroll-Triggered Reveals**:
- Fade-in on scroll entry (with offset)
- Slide-in from sides with stagger
- Scale + opacity transitions
- Clip-path reveals

**b) Scroll-Linked Animations**:
- Parallax layers (different scroll speeds)
- Horizontal scrolling sections
- Pinned sections with scrubbing animations
- 3D object rotation tied to scroll

**c) Progress Indicators**:
- Reading progress bars
- Step-by-step visual guides
- Animated SVG paths following scroll

**Implementation Example** (GSAP ScrollTrigger):
```javascript
// Scroll-linked 3D rotation
gsap.to(".cube", {
  scrollTrigger: {
    trigger: ".section",
    start: "top top",
    end: "bottom top",
    scrub: 1, // Smooth scrubbing
  },
  rotationY: 360,
  ease: "none"
});
```

**Related Skills**: `gsap-scrolltrigger`, `locomotive-scroll`, `scroll-reveal-libraries`, `react-three-fiber` for 3D scrollytelling

### 5. Cursor UX

**Evolution**: Custom cursors that enhance interaction and provide contextual feedback.

**Patterns**:

**a) Custom Cursor Shapes**:
- Circle/dot followers (delayed with easing)
- Text-based cursors ("View", "Drag", "Click")
- Blend modes for visual interest
- Scale/morph on hover

**b) Contextual Transformations**:
- Expand on links/buttons
- Magnetic attraction to interactive elements
- Color inversion over images
- Custom icons for actions (play, zoom, expand)

**c) Performance Considerations**:
- Use CSS transforms only (no top/left)
- RequestAnimationFrame for JS cursors
- Disable on mobile/touch devices
- Respect `prefers-reduced-motion`

**Implementation Example**:
```javascript
// Simple smooth cursor follower
const cursor = document.querySelector('.cursor');
let mouseX = 0, mouseY = 0;
let cursorX = 0, cursorY = 0;

document.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
});

function updateCursor() {
  // Smooth easing
  cursorX += (mouseX - cursorX) * 0.1;
  cursorY += (mouseY - cursorY) * 0.1;

  cursor.style.transform = `translate(${cursorX}px, ${cursorY}px)`;
  requestAnimationFrame(updateCursor);
}
updateCursor();
```

**Related Skills**: `gsap-scrolltrigger` (for easing), `motion-framer` (for React cursor components)

### 6. Glassmorphism & Depth

**Characteristics**:
- Frosted glass effect (backdrop-filter)
- Layered UI with depth hierarchy
- Subtle shadows and borders
- Translucent backgrounds

**Modern Glassmorphism** (2024):
```css
.glass-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
}
```

**Depth System** (Layering):
```css
/* Elevation scale */
--elevation-1: 0 1px 3px rgba(0,0,0,0.12);
--elevation-2: 0 4px 8px rgba(0,0,0,0.15);
--elevation-3: 0 8px 16px rgba(0,0,0,0.18);
--elevation-4: 0 16px 32px rgba(0,0,0,0.2);
```

**Related Skills**: `animated-component-libraries` for glassmorphic components

### 7. AI-Enhanced Personalization

**Patterns**:

**a) Adaptive Content**:
- Dynamic layout based on user behavior
- Personalized content recommendations
- Adaptive color schemes (system preference + user history)
- Smart defaults based on context

**b) Intelligent Interactions**:
- Predictive search with instant results
- Smart form completion
- Context-aware suggestions
- Progressive disclosure based on usage

**c) Performance + Privacy**:
- Client-side personalization (localStorage, IndexedDB)
- Edge computing for fast personalization
- Privacy-preserving analytics
- Transparent data usage

**Implementation Considerations**:
- Fallback to default experience
- No layout shift from personalization
- Respect "Do Not Track"
- GDPR/CCPA compliance

## Common Design Patterns

### Pattern 1: Immersive Hero Section

**Use Case**: Landing pages, product launches, portfolio sites

**Characteristics**:
- Full viewport height
- Subtle 3D background or animated gradient
- Large headline with fluid typography
- Smooth scroll indicator
- Parallax on scroll exit

**Implementation** (Combined approach):

**HTML Structure**:
```html
<section class="hero">
  <div id="bg-canvas"></div>
  <div class="hero__content">
    <h1 class="hero__title">Modern Design</h1>
    <p class="hero__subtitle">Performance meets beauty</p>
    <button class="hero__cta">Explore</button>
  </div>
  <div class="scroll-indicator">
    <span>Scroll</span>
  </div>
</section>
```

**Technologies**:
- Background: Vanta.js WAVES effect (`lightweight-3d-effects`)
- Text animation: GSAP SplitText with stagger (`gsap-scrolltrigger`)
- Button: Framer Motion hover states (`motion-framer`)
- Scroll indicator: CSS animation + GSAP fade out on scroll

**Related Skills**: `lightweight-3d-effects`, `gsap-scrolltrigger`, `motion-framer`

### Pattern 2: Horizontal Scroll Gallery

**Use Case**: Portfolio work, product showcases, case studies

**Implementation** (GSAP ScrollTrigger):
```javascript
gsap.to(".gallery__track", {
  x: () => -(document.querySelector(".gallery__track").scrollWidth - window.innerWidth),
  ease: "none",
  scrollTrigger: {
    trigger: ".gallery",
    pin: true,
    scrub: 1,
    end: () => "+=" + document.querySelector(".gallery__track").scrollWidth
  }
});
```

**Enhancements**:
- Lazy load images as they scroll into view
- Parallax within cards
- Scale transformation on active card
- Smooth momentum scrolling with Locomotive

**Related Skills**: `gsap-scrolltrigger`, `locomotive-scroll`

### Pattern 3: 3D Product Viewer

**Use Case**: E-commerce, product marketing, showcases

**Implementation** (React Three Fiber):
```jsx
import { Canvas } from '@react-three/fiber'
import { OrbitControls, useGLTF } from '@react-three/drei'

function ProductViewer() {
  return (
    <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <spotLight position={[10, 10, 10]} angle={0.15} />
      <Product />
      <OrbitControls
        enableZoom={false}
        autoRotate
        autoRotateSpeed={2}
      />
    </Canvas>
  )
}
```

**Enhancements**:
- Material variants (color picker)
- Hotspots with annotations
- AR mode on mobile
- Screenshot/share functionality

**Related Skills**: `react-three-fiber`, `threejs-webgl`, `model-viewer-component`

### Pattern 4: Animated Data Visualization

**Use Case**: Dashboards, analytics, infographics

**Patterns**:
- Count-up animations on scroll into view
- Animated chart reveals (progress bars, pie charts)
- Staggered grid animations
- Particle backgrounds representing data

**Implementation** (Framer Motion + IntersectionObserver):
```jsx
function AnimatedStat({ end, label }) {
  const [count, setCount] = useState(0);
  const ref = useRef();
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (isInView) {
      // Count up animation
      const duration = 2000;
      const steps = 60;
      const increment = end / steps;
      let current = 0;

      const timer = setInterval(() => {
        current += increment;
        if (current >= end) {
          setCount(end);
          clearInterval(timer);
        } else {
          setCount(Math.floor(current));
        }
      }, duration / steps);
    }
  }, [isInView, end]);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6 }}
    >
      <h2>{count}+</h2>
      <p>{label}</p>
    </motion.div>
  );
}
```

**Related Skills**: `motion-framer`, `pixijs-2d` for canvas-based visualizations

### Pattern 5: Page Transitions

**Use Case**: Multi-page apps, portfolio sites, storytelling experiences

**Implementation** (Barba.js + GSAP):
```javascript
barba.init({
  transitions: [{
    name: 'slide',
    leave(data) {
      return gsap.to(data.current.container, {
        xPercent: -100,
        duration: 0.5
      });
    },
    enter(data) {
      return gsap.from(data.next.container, {
        xPercent: 100,
        duration: 0.5
      });
    }
  }]
});
```

**Modern Alternatives**:
- View Transitions API (Chrome 111+, progressive enhancement)
- Framer Motion's AnimatePresence for React SPAs
- Shared element transitions

**Related Skills**: `barba-js`, `gsap-scrolltrigger`, `motion-framer`

### Pattern 6: Interactive Cursor Effects

**Use Case**: Creative agencies, portfolios, interactive experiences

**Patterns**:
- Text cursor that follows with delay
- Magnetic buttons (cursor attracted to elements)
- Blend mode cursor (inverts colors)
- Cursor that reveals content

**Implementation** (Vanilla JS + GSAP):
```javascript
const links = document.querySelectorAll('a');
const cursor = document.querySelector('.cursor');

links.forEach(link => {
  link.addEventListener('mouseenter', () => {
    gsap.to(cursor, {
      scale: 2,
      duration: 0.3,
      ease: "power2.out"
    });
  });

  link.addEventListener('mouseleave', () => {
    gsap.to(cursor, {
      scale: 1,
      duration: 0.3,
      ease: "power2.out"
    });
  });
});
```

**Related Skills**: `gsap-scrolltrigger`, `motion-framer`

### Pattern 7: Staggered Content Reveals

**Use Case**: Feature sections, testimonials, team grids

**Implementation** (Framer Motion variants):
```jsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

function FeatureGrid() {
  return (
    <motion.div
      variants={container}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.3 }}
      className="grid"
    >
      {features.map((feature, i) => (
        <motion.div key={i} variants={item}>
          {feature}
        </motion.div>
      ))}
    </motion.div>
  );
}
```

**Related Skills**: `motion-framer`, `gsap-scrolltrigger`, `scroll-reveal-libraries`

## Integration with Other Skills

### Animation Skills Integration

**GSAP ScrollTrigger** (`gsap-scrolltrigger`):
- Use for scroll-driven storytelling
- Pin sections for multi-step reveals
- Scrub animations tied to scroll position
- Batch animations for performance

**Framer Motion** (`motion-framer`):
- React component animations
- Page transitions with AnimatePresence
- Gesture-based interactions (drag, hover, tap)
- Layout animations (shared element transitions)

**React Spring** (`react-spring-physics`):
- Physics-based animations (more natural feel)
- Interactive springs (drag, pull)
- Trail animations (sequential reveals)
- Use for UI feedback that feels "real"

**Anime.js** (`animejs`):
- SVG path animations (line drawing)
- SVG morphing transitions
- Stagger grid animations
- Timeline-based sequences

**Lottie** (`lottie-animations`):
- Complex designer-created animations
- Icon animations and micro-interactions
- Loading states
- Scroll-driven playback

### 3D Skills Integration

**Three.js** (`threejs-webgl`):
- Custom 3D scenes and experiences
- Shader effects and post-processing
- WebGL-based particle systems
- Advanced lighting and materials

**React Three Fiber** (`react-three-fiber`):
- 3D in React applications
- Product viewers and configurators
- Interactive 3D UI components
- Scroll-driven 3D animations

**Babylon.js** (`babylonjs-engine`):
- Physics-based 3D experiences
- VR/XR applications
- Game-like interactions
- PBR materials for realism

**Lightweight 3D** (`lightweight-3d-effects`):
- Background effects (Vanta.js)
- Subtle 3D illustrations (Zdog)
- Tilt effects (Vanilla-Tilt)
- Performance-friendly 3D accents

### Component Libraries

**Animated Components** (`animated-component-libraries`):
- Magic UI components (backgrounds, text effects)
- Pre-built interactive components
- Design system foundations
- Rapid prototyping

**Scroll Reveals** (`scroll-reveal-libraries`):
- Simple fade/slide on scroll
- AOS library integration
- Lightweight alternative to ScrollTrigger
- Quick implementation for basic reveals

## Accessibility Best Practices

### 1. Motion & Animation

**Respect User Preferences**:
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**JavaScript Detection**:
```javascript
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (prefersReducedMotion) {
  // Disable or simplify animations
  gsap.config({ nullTargetWarn: false });
  // Skip scroll animations, use instant reveals
}
```

### 2. Color Contrast

**WCAG AAA Standards**:
- Normal text: 7:1 contrast ratio
- Large text (18pt+): 4.5:1 contrast ratio
- Use OKLCH color space for perceptual uniformity

**Testing**:
```javascript
// Check contrast ratio
function getContrastRatio(color1, color2) {
  const l1 = getLuminance(color1);
  const l2 = getLuminance(color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}
```

### 3. Keyboard Navigation

**Requirements**:
- All interactive elements focusable
- Visible focus indicators (not outline: none)
- Logical tab order
- Skip links for long navigation
- Escape key closes modals/overlays

**Focus Styles** (Modern):
```css
:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Remove focus ring for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}
```

### 4. Screen Reader Support

**Semantic HTML**:
- Use proper heading hierarchy (h1-h6)
- Landmark regions (header, nav, main, footer)
- aria-labels for icon buttons
- aria-live regions for dynamic content

**Animation Announcements**:
```html
<!-- Announce when content loads -->
<div role="status" aria-live="polite" aria-atomic="true">
  Loading complete. 12 items displayed.
</div>
```

### 5. Touch Targets

**Minimum Size**: 44x44px (iOS), 48x48px (Android)

**Spacing**: Minimum 8px between touch targets

**Implementation**:
```css
.button {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 24px;
  /* Tap target includes padding */
}
```

## Performance Optimization

### 1. Animation Performance

**60 FPS Checklist**:
- Use CSS transforms (translateX/Y/Z, scale, rotate) - GPU accelerated
- Use opacity for fades - GPU accelerated
- Avoid: top/left, width/height, margin, padding animations
- Use `will-change` sparingly (memory cost)
- RequestAnimationFrame for JS animations

**GSAP Performance**:
```javascript
// Force GPU acceleration
gsap.set(element, { force3D: true });

// Use will-change during animation only
gsap.to(element, {
  x: 100,
  onStart: () => element.style.willChange = 'transform',
  onComplete: () => element.style.willChange = 'auto'
});
```

### 2. Loading Strategies

**Critical Path**:
- Inline critical CSS (above-the-fold)
- Defer non-critical CSS
- Async JavaScript loading
- Preload fonts and hero images

**Progressive Enhancement**:
```html
<!-- Load essential styles first -->
<style>
  /* Critical CSS inlined */
</style>

<!-- Defer non-critical styles -->
<link rel="preload" href="animations.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="animations.css"></noscript>
```

### 3. Image Optimization

**Modern Formats**:
```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Description" loading="lazy">
</picture>
```

**Responsive Images**:
```html
<img
  srcset="image-400.jpg 400w,
          image-800.jpg 800w,
          image-1200.jpg 1200w"
  sizes="(max-width: 640px) 100vw,
         (max-width: 1024px) 50vw,
         33vw"
  src="image-800.jpg"
  alt="Description"
  loading="lazy"
>
```

### 4. 3D Content Optimization

**Loading Strategy**:
- Show placeholder while loading
- Load low-poly model first
- Progressive enhancement with high-poly
- Lazy load 3D scenes below fold

**Runtime Performance**:
- Use object pooling
- Implement LOD (Level of Detail)
- Frustum culling
- Texture compression (Basis Universal)

**Related Skills**: `threejs-webgl`, `react-three-fiber`, `babylonjs-engine`

### 5. JavaScript Bundle Size

**Code Splitting**:
```javascript
// Dynamic imports
const AnimationModule = lazy(() => import('./animations'));

// Route-based splitting
const Gallery = lazy(() => import('./pages/Gallery'));
```

**Tree Shaking**:
- Use ES6 imports
- Import only what you need
- Use modern build tools (Vite, esbuild)

## Common Pitfalls

### Pitfall 1: Over-Animation

**Problem**: Too many animations distract from content and hurt performance.

**Solution**:
- Limit animations to meaningful interactions
- Use animation to guide attention, not demand it
- Follow the principle: "Animation with purpose"
- Measure performance impact (Chrome DevTools Performance tab)

**Rule of Thumb**: If you can't explain why an animation exists, remove it.

### Pitfall 2: Ignoring Mobile Performance

**Problem**: Animations work on desktop but lag on mobile devices.

**Solution**:
- Test on real devices (not just simulators)
- Reduce animation complexity on mobile
- Disable expensive effects (parallax, 3D) on low-end devices
- Use `matchMedia` for device-specific experiences

```javascript
const isLowEndDevice = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) &&
         navigator.hardwareConcurrency < 4;
};

if (isLowEndDevice()) {
  // Simplify or disable animations
}
```

### Pitfall 3: Missing Fallbacks

**Problem**: Experience breaks without JavaScript or on older browsers.

**Solution**:
- Progressive enhancement mindset
- Core content accessible without JS
- Feature detection before using modern APIs
- Polyfills for critical features

```javascript
// Feature detection
if ('IntersectionObserver' in window) {
  // Use scroll-triggered animations
} else {
  // Show content immediately
}
```

### Pitfall 4: Accessibility Oversight

**Problem**: Forgetting keyboard users, screen readers, or motion-sensitive users.

**Solution**:
- Test with keyboard only
- Test with screen reader (NVDA, VoiceOver)
- Always check `prefers-reduced-motion`
- Use semantic HTML
- Maintain proper focus management

**Checklist**:
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible
- [ ] Color contrast meets WCAG AAA
- [ ] Motion can be disabled
- [ ] Screen reader announcements make sense

### Pitfall 5: Ignoring Loading States

**Problem**: Blank screen or layout shifts during content load.

**Solution**:
- Skeleton screens for predictable layouts
- Smooth loading transitions
- Reserve space for dynamic content
- Show meaningful loading indicators

```jsx
// Skeleton screen pattern
function ProductCard({ loading, data }) {
  if (loading) {
    return (
      <div className="skeleton">
        <div className="skeleton__image" />
        <div className="skeleton__title" />
        <div className="skeleton__price" />
      </div>
    );
  }

  return <ProductCardContent data={data} />;
}
```

### Pitfall 6: Scroll Hijacking

**Problem**: Overriding native scroll behavior frustrates users.

**Solution**:
- Preserve browser's native scroll (momentum, keyboard)
- Use ScrollTrigger/Locomotive without changing scroll physics
- Allow users to scroll at their own pace
- Never disable scroll entirely
- Avoid scroll-jacking for full-page sections

**Good Practice**: Enhance scroll, don't replace it.

## Design System Architecture

### Token Structure

**Modern Design Tokens** (CSS Custom Properties):
```css
:root {
  /* Colors - OKLCH for perceptual uniformity */
  --color-primary: oklch(50% 0.2 250);
  --color-accent: oklch(65% 0.25 30);

  /* Spacing - Consistent scale */
  --space-2xs: clamp(0.25rem, 0.2rem + 0.25vw, 0.375rem);
  --space-xs: clamp(0.5rem, 0.4rem + 0.5vw, 0.75rem);
  --space-sm: clamp(0.75rem, 0.6rem + 0.75vw, 1.125rem);
  --space-md: clamp(1rem, 0.8rem + 1vw, 1.5rem);
  --space-lg: clamp(1.5rem, 1.2rem + 1.5vw, 2.25rem);
  --space-xl: clamp(2rem, 1.6rem + 2vw, 3rem);
  --space-2xl: clamp(3rem, 2.4rem + 3vw, 4.5rem);

  /* Typography - Fluid scale */
  --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);

  /* Animation - Consistent timing */
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;

  /* Easing - Natural motion */
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### Component Architecture

**Atomic Design** (Brad Frost):
1. **Atoms**: Buttons, inputs, labels
2. **Molecules**: Form fields, cards
3. **Organisms**: Navigation, hero sections
4. **Templates**: Page layouts
5. **Pages**: Specific instances

**Related Skills**: `animated-component-libraries` for component patterns

## Resources

This skill references the following skills for implementation:

### Animation & Interaction
- `gsap-scrolltrigger` - Scroll-driven animations, pinning, scrubbing
- `motion-framer` - React animations, gestures, layout animations
- `react-spring-physics` - Physics-based animations
- `animejs` - SVG animations, stagger effects
- `lottie-animations` - Designer-created animations
- `scroll-reveal-libraries` - Simple scroll reveals (AOS)

### 3D & WebGL
- `threejs-webgl` - Custom 3D scenes and effects
- `react-three-fiber` - 3D in React applications
- `babylonjs-engine` - Physics-based 3D, VR/XR
- `lightweight-3d-effects` - Vanta.js backgrounds, Zdog illustrations

### Page Transitions & Scroll
- `barba-js` - Page transitions
- `locomotive-scroll` - Smooth scrolling

### Component Libraries
- `animated-component-libraries` - Magic UI, React Bits
- `pixijs-2d` - Canvas-based 2D graphics

### Detailed References

See the `references/` directory for in-depth documentation:
- `design_trends_2024.md` - Current web design trends and forecasts
- `interaction_patterns.md` - Comprehensive micro-interaction catalog
- `accessibility_guide.md` - WCAG compliance patterns and testing
- `performance_checklist.md` - Optimization strategies and metrics

### Scripts

The `scripts/` directory includes tools for implementing design patterns:
- `pattern_generator.py` - Generate design pattern boilerplate
- `design_audit.py` - Audit existing designs for compliance

### Assets

The `assets/` directory contains design system templates and starter files. See `assets/README.md` for details.



===== FILE: plugins/individual/modern-web-design/skills/modern-web-design/references/accessibility_guide.md =====

# Web Accessibility Guide (WCAG AAA Compliance)

## Overview

Comprehensive guide to web accessibility compliance following WCAG 2.1/2.2 Level AAA standards. This guide covers the most critical accessibility requirements for modern web design.

**Target Standard**: WCAG 2.1 Level AAA (where practical) with Level AA as minimum baseline.

---

## Table of Contents

1. [Color & Contrast](#color--contrast)
2. [Typography & Readability](#typography--readability)
3. [Keyboard Navigation](#keyboard-navigation)
4. [Screen Reader Support](#screen-reader-support)
5. [Motion & Animation](#motion--animation)
6. [Touch Targets & Mobile](#touch-targets--mobile)
7. [Forms & Input](#forms--input)
8. [Focus Management](#focus-management)
9. [Semantic HTML](#semantic-html)
10. [Testing & Auditing](#testing--auditing)

---

## Color & Contrast

### WCAG Contrast Requirements

**Level AA (Minimum)**:
- Normal text (< 18pt): 4.5:1 contrast ratio
- Large text (≥ 18pt or 14pt bold): 3:1 contrast ratio

**Level AAA (Enhanced)**:
- Normal text: **7:1 contrast ratio**
- Large text: **4.5:1 contrast ratio**

### Checking Contrast

**Manual Calculation**:
```javascript
function getLuminance(r, g, b) {
  const [rs, gs, bs] = [r, g, b].map(c => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function getContrastRatio(rgb1, rgb2) {
  const l1 = getLuminance(...rgb1);
  const l2 = getLuminance(...rgb2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// Example usage
const textColor = [0, 0, 0]; // Black
const bgColor = [255, 255, 255]; // White
const ratio = getContrastRatio(textColor, bgColor);
console.log(ratio); // 21:1 (AAA compliant)
```

**Tools**:
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Stark (Figma plugin)
- Chrome DevTools Accessibility Panel

### Color System (AAA Compliant)

**Using OKLCH Color Space**:
```css
:root {
  /* Text on white background (AAA compliant) */
  --color-text-primary: oklch(20% 0 0); /* #1a1a1a, 11.6:1 */
  --color-text-secondary: oklch(40% 0 0); /* #666666, 7.3:1 */

  /* Backgrounds */
  --color-bg-primary: oklch(98% 0 0); /* Near white */
  --color-bg-secondary: oklch(95% 0 0); /* Light gray */

  /* Accent colors (AAA on white) */
  --color-accent-blue: oklch(45% 0.2 250); /* 7.1:1 */
  --color-accent-green: oklch(50% 0.15 140); /* 7.2:1 */

  /* Interactive states */
  --color-link: oklch(40% 0.2 250); /* Blue, 8.3:1 */
  --color-link-hover: oklch(35% 0.25 250); /* Darker blue, 10.5:1 */
}
```

### Color Blindness Considerations

**Avoid**:
- Red-green as only distinguisher (affects 8% of males)
- Relying on color alone for meaning

**Best Practices**:
- Use patterns, shapes, or icons alongside color
- Test with color blindness simulators
- Provide high-contrast mode

**Simulation Tools**:
- Chrome DevTools: Rendering > Emulate vision deficiencies
- Colorblindly (browser extension)
- Stark (Figma)

---

## Typography & Readability

### Font Size Requirements

**WCAG Guidelines**:
- Body text: Minimum 16px (1rem)
- Small text: Minimum 14px (0.875rem)
- Users must be able to zoom to 200% without loss of functionality

**Recommended Sizes**:
```css
:root {
  /* Fluid typography */
  --font-size-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
  --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
  --font-size-lg: clamp(1.25rem, 1.1rem + 0.75vw, 1.75rem);
  --font-size-xl: clamp(1.75rem, 1.5rem + 1.25vw, 2.5rem);
}

body {
  font-size: var(--font-size-base);
  line-height: 1.5; /* WCAG minimum for body text */
}
```

### Line Height & Spacing

**WCAG 1.4.12 (Level AAA)**:
- Line height: Minimum 1.5× font size
- Paragraph spacing: Minimum 2× font size
- Letter spacing: Minimum 0.12× font size
- Word spacing: Minimum 0.16× font size

**Implementation**:
```css
p {
  font-size: 1rem;
  line-height: 1.6; /* 1.5× minimum */
  margin-bottom: 2rem; /* 2× font size */
  letter-spacing: 0.01em; /* Slight increase */
  word-spacing: 0.05em;
}
```

### Font Choices

**Accessible Fonts**:
- Sans-serif: Inter, Roboto, Open Sans, Atkinson Hyperlegible
- Serif: Georgia, Merriweather, Lora
- Avoid: Overly decorative, thin weights (< 300), all-caps for long text

**Dyslexia-Friendly**:
- OpenDyslexic
- Atkinson Hyperlegible
- Comic Sans (surprisingly good for dyslexia)

---

## Keyboard Navigation

### Requirements

**All interactive elements must be**:
- Focusable with Tab key
- Activatable with Enter or Space
- Dismissible with Escape (modals, dropdowns)
- Navigable with arrow keys (where appropriate)

### Tab Order

**Logical Tab Order**:
```html
<!-- Natural DOM order is best -->
<button tabindex="0">First</button>
<button tabindex="0">Second</button>
<button tabindex="0">Third</button>

<!-- Avoid tabindex > 0 (creates unpredictable order) -->
<button tabindex="3">Third</button> <!-- BAD -->
<button tabindex="1">First</button> <!-- BAD -->
```

**Skip Links**:
```html
<a href="#main-content" class="skip-link">
  Skip to main content
</a>

<nav>...</nav>

<main id="main-content">
  <!-- Main content -->
</main>
```

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

### Focus Indicators

**WCAG 2.4.7 (Level AA)**:
- Focus indicator must be visible
- Minimum 2px thick
- Sufficient contrast (3:1 against background)

**Modern Focus Styles**:
```css
/* Remove default outline */
*:focus {
  outline: none;
}

/* Custom focus indicator */
:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Remove focus ring for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}

/* Button focus */
button:focus-visible {
  outline: 3px solid #3b82f6;
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}
```

### Keyboard Patterns

**Modal Dialogs**:
```javascript
function trapFocus(element) {
  const focusableElements = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  element.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      } else if (!e.shiftKey && document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    }

    if (e.key === 'Escape') {
      closeModal();
    }
  });

  firstFocusable.focus();
}
```

**Dropdown Menus**:
```javascript
function handleDropdownKeys(e) {
  const items = Array.from(dropdown.querySelectorAll('[role="menuitem"]'));
  const currentIndex = items.indexOf(document.activeElement);

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault();
      const nextIndex = (currentIndex + 1) % items.length;
      items[nextIndex].focus();
      break;

    case 'ArrowUp':
      e.preventDefault();
      const prevIndex = (currentIndex - 1 + items.length) % items.length;
      items[prevIndex].focus();
      break;

    case 'Home':
      e.preventDefault();
      items[0].focus();
      break;

    case 'End':
      e.preventDefault();
      items[items.length - 1].focus();
      break;

    case 'Escape':
      closeDropdown();
      triggerButton.focus();
      break;
  }
}
```

---

## Screen Reader Support

### ARIA Attributes

**Essential ARIA**:

**Landmarks**:
```html
<header role="banner">
  <nav role="navigation" aria-label="Main">
    <!-- Navigation -->
  </nav>
</header>

<main role="main">
  <!-- Main content -->
</main>

<aside role="complementary" aria-label="Related articles">
  <!-- Sidebar -->
</aside>

<footer role="contentinfo">
  <!-- Footer -->
</footer>
```

**Buttons**:
```html
<!-- Icon button needs label -->
<button aria-label="Close menu">
  <svg>...</svg>
</button>

<!-- Button with visible text -->
<button>
  <svg aria-hidden="true">...</svg>
  Submit
</button>
```

**Live Regions**:
```html
<!-- Announce loading state -->
<div role="status" aria-live="polite" aria-atomic="true">
  Loading content...
</div>

<!-- Announce errors -->
<div role="alert" aria-live="assertive">
  Error: Form submission failed.
</div>
```

**Custom Components**:
```html
<!-- Accordion -->
<div class="accordion">
  <h3>
    <button
      aria-expanded="false"
      aria-controls="panel-1"
      id="button-1"
    >
      Section 1
    </button>
  </h3>
  <div
    id="panel-1"
    role="region"
    aria-labelledby="button-1"
    hidden
  >
    Content...
  </div>
</div>

<!-- Tab panel -->
<div role="tablist" aria-label="Content sections">
  <button role="tab" aria-selected="true" aria-controls="panel-1">
    Tab 1
  </button>
  <button role="tab" aria-selected="false" aria-controls="panel-2">
    Tab 2
  </button>
</div>
<div role="tabpanel" id="panel-1" aria-labelledby="tab-1">
  Panel content...
</div>
```

### Alt Text Guidelines

**Images**:
```html
<!-- Informative image -->
<img src="chart.png" alt="Bar chart showing 50% increase in sales">

<!-- Decorative image -->
<img src="decorative.png" alt="" role="presentation">

<!-- Complex image -->
<img src="infographic.png" alt="Sales data for Q4" longdesc="sales-data.html">
```

**Best Practices**:
- Describe the content/function, not "image of..."
- Keep under 150 characters (screen readers pause)
- Use empty alt (`alt=""`) for decorative images
- Provide long descriptions for complex images

---

## Motion & Animation

### Reduced Motion Preference

**WCAG 2.3.3 (Level AAA)**:
Users must be able to disable non-essential motion.

**Implementation**:
```css
/* Default: animations enabled */
.animated-element {
  animation: slide-in 0.5s ease;
}

/* Respect user preference */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  /* Keep essential animations but reduce */
  .loading-spinner {
    animation-duration: 1s; /* Slower */
  }
}
```

**JavaScript Detection**:
```javascript
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

if (prefersReducedMotion) {
  // Disable or simplify animations
  gsap.config({ nullTargetWarn: false, force3D: false });

  // Skip scroll animations
  ScrollTrigger.getAll().forEach(st => st.kill());
}
```

### Animation Guidelines

**Safe Animations**:
- Fade in/out (opacity)
- Slide short distances (< 50px)
- Scale small amounts (0.95-1.05)
- Avoid: flashing, rapid movement, parallax

**Vestibular Disorders**:
Avoid animations that can cause dizziness or nausea:
- Large parallax effects
- Continuous rotation
- Zoom effects
- Perspective transforms

---

## Touch Targets & Mobile

### WCAG 2.5.5 (Level AAA)

**Target Size**: Minimum 44×44px (iOS) or 48×48px (Android)

**Spacing**: Minimum 8px between targets

**Implementation**:
```css
button, a {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 24px;
  /* Touch target includes padding */
}

/* Increase tap target without changing visual size */
button::before {
  content: '';
  position: absolute;
  inset: -8px; /* Extends tap target by 8px all sides */
}
```

### Mobile Considerations

**Viewport**:
```html
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5">
```
*Note*: Allow zoom up to 5× (WCAG requirement)

**Touch Gestures**:
- Avoid complex gestures (multi-finger, long-press)
- Provide alternative interactions
- Don't rely on hover states

---

## Forms & Input

### Labels & Instructions

**WCAG 3.3.2 (Level A)**:
Every input must have a visible label.

**Implementation**:
```html
<!-- Explicit label -->
<label for="email">Email address</label>
<input id="email" type="email" required aria-describedby="email-help">
<small id="email-help">We'll never share your email.</small>

<!-- Error state -->
<input
  id="email"
  type="email"
  aria-invalid="true"
  aria-describedby="email-error"
>
<div id="email-error" role="alert">
  Please enter a valid email address.
</div>
```

### Form Validation

**Accessible Validation**:
```javascript
function validateEmail(input) {
  const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value);

  if (isValid) {
    input.setAttribute('aria-invalid', 'false');
    input.removeAttribute('aria-describedby');
    removeError(input);
  } else {
    input.setAttribute('aria-invalid', 'true');
    input.setAttribute('aria-describedby', `${input.id}-error`);
    showError(input, 'Please enter a valid email address.');
  }
}

function showError(input, message) {
  const errorElement = document.getElementById(`${input.id}-error`) ||
                       createErrorElement(input.id);
  errorElement.textContent = message;
  errorElement.setAttribute('role', 'alert'); // Announces to screen readers
}
```

### Required Fields

**Indication**:
```html
<label for="name">
  Full name
  <abbr title="required" aria-label="required">*</abbr>
</label>
<input id="name" type="text" required aria-required="true">
```

**Visual + Programmatic**:
- Visual indicator (asterisk, "required")
- `required` attribute
- `aria-required="true"`

---

## Focus Management

### Managing Focus States

**After Modal Opens**:
```javascript
function openModal() {
  modal.style.display = 'block';
  modal.setAttribute('aria-hidden', 'false');

  // Focus first focusable element
  const firstFocusable = modal.querySelector('button, [href], input');
  firstFocusable.focus();

  // Trap focus
  trapFocus(modal);
}
```

**After Modal Closes**:
```javascript
function closeModal() {
  modal.style.display = 'none';
  modal.setAttribute('aria-hidden', 'true');

  // Return focus to trigger button
  triggerButton.focus();
}
```

### Focus Order

**Best Practices**:
- Follow visual order (top to bottom, left to right)
- Group related elements
- Use `tabindex="-1"` for programmatic focus only
- Avoid `tabindex > 0` (creates unpredictable order)

---

## Semantic HTML

### Heading Hierarchy

**WCAG 1.3.1 (Level A)**:
Use proper heading levels (h1-h6) without skipping.

**Correct**:
```html
<h1>Page Title</h1>
<h2>Section</h2>
<h3>Subsection</h3>
<h3>Another Subsection</h3>
<h2>Another Section</h2>
```

**Incorrect**:
```html
<h1>Page Title</h1>
<h3>Section</h3> <!-- Skipped h2 -->
```

### Landmark Regions

**Essential Landmarks**:
```html
<header>
  <nav aria-label="Main navigation">
    <!-- Primary nav -->
  </nav>
</header>

<main>
  <article>
    <header>
      <h1>Article Title</h1>
    </header>
    <!-- Article content -->
  </article>

  <aside aria-label="Related links">
    <!-- Sidebar -->
  </aside>
</main>

<footer>
  <nav aria-label="Footer navigation">
    <!-- Footer nav -->
  </nav>
</footer>
```

### Lists & Tables

**Lists**:
```html
<!-- Use proper list elements -->
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
</ul>

<!-- Not divs styled as lists -->
```

**Tables**:
```html
<table>
  <caption>Sales Data Q4 2024</caption>
  <thead>
    <tr>
      <th scope="col">Month</th>
      <th scope="col">Sales</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>October</td>
      <td>$50,000</td>
    </tr>
  </tbody>
</table>
```

---

## Testing & Auditing

### Automated Testing Tools

**Browser Extensions**:
- axe DevTools (Chrome/Firefox)
- WAVE (Web Accessibility Evaluation Tool)
- Lighthouse (Chrome DevTools)

**Command Line**:
```bash
# pa11y
npm install -g pa11y
pa11y https://example.com

# axe-core CLI
npm install -g @axe-core/cli
axe https://example.com
```

### Manual Testing Checklist

**Keyboard Navigation**:
- [ ] Tab through all interactive elements
- [ ] Activate with Enter/Space
- [ ] Close modals with Escape
- [ ] Navigate dropdowns with arrow keys

**Screen Reader Testing**:
- [ ] Test with NVDA (Windows), VoiceOver (Mac), JAWS
- [ ] Check heading structure
- [ ] Verify alt text
- [ ] Test form labels and errors

**Visual Testing**:
- [ ] Zoom to 200%
- [ ] Test color contrast
- [ ] Check focus indicators
- [ ] Review with color blindness simulator

**Motion Testing**:
- [ ] Enable `prefers-reduced-motion`
- [ ] Verify animations are disabled/reduced
- [ ] Check for essential animations that remain

### Screen Reader Testing Commands

**NVDA (Windows)**:
- Toggle: Caps Lock or Insert
- Next heading: H
- Next landmark: D
- Read all: Caps Lock + Down Arrow

**VoiceOver (Mac)**:
- Toggle: Cmd + F5
- Rotor: Ctrl + Option + U
- Next heading: Ctrl + Option + Cmd + H

**JAWS (Windows)**:
- List headings: Insert + F6
- List links: Insert + F7
- Next heading: H

---

## Common Accessibility Patterns

### Accessible Modal

```jsx
function AccessibleModal({ isOpen, onClose, children }) {
  const modalRef = useRef(null);
  const triggerRef = useRef(document.activeElement);

  useEffect(() => {
    if (isOpen) {
      // Trap focus
      trapFocus(modalRef.current);

      // Focus first element
      const firstFocusable = modalRef.current.querySelector('button, [href], input');
      firstFocusable?.focus();

      // Prevent body scroll
      document.body.style.overflow = 'hidden';
    } else {
      // Return focus
      triggerRef.current?.focus();
      document.body.style.overflow = '';
    }

    // Listen for Escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleEscape);

    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="modal-backdrop"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={modalRef}
        className="modal"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="modal-title">Modal Title</h2>
        {children}
        <button onClick={onClose} aria-label="Close modal">
          ×
        </button>
      </div>
    </div>
  );
}
```

### Accessible Accordion

```html
<div class="accordion">
  <h3>
    <button
      aria-expanded="false"
      aria-controls="panel-1"
      id="accordion-button-1"
    >
      <span class="accordion-title">Section 1</span>
      <svg class="accordion-icon" aria-hidden="true">...</svg>
    </button>
  </h3>
  <div
    id="panel-1"
    role="region"
    aria-labelledby="accordion-button-1"
    hidden
  >
    <p>Content for section 1...</p>
  </div>
</div>
```

```javascript
function initAccordion() {
  const buttons = document.querySelectorAll('.accordion button');

  buttons.forEach(button => {
    button.addEventListener('click', () => {
      const expanded = button.getAttribute('aria-expanded') === 'true';
      const panel = document.getElementById(button.getAttribute('aria-controls'));

      button.setAttribute('aria-expanded', !expanded);
      panel.hidden = expanded;
    });
  });
}
```

---

## WCAG Quick Reference

**Level A (Must Have)**:
- Text alternatives (alt text)
- Keyboard accessible
- Color not only means of conveying info
- Labeled form inputs
- Proper heading hierarchy

**Level AA (Should Have)**:
- 4.5:1 contrast for normal text
- 3:1 contrast for large text
- Resize text to 200%
- Focus visible
- Multiple ways to find pages

**Level AAA (Nice to Have)**:
- 7:1 contrast for normal text
- 4.5:1 contrast for large text
- Target size 44×44px minimum
- No timing restrictions
- Help available

---

*Last updated: 2024*
*Based on WCAG 2.1 and WCAG 2.2 standards*



===== FILE: plugins/individual/modern-web-design/skills/modern-web-design/references/design_trends_2024.md =====

# Web Design Trends 2024-2025

## Overview

This document catalogs the dominant web design trends, aesthetic movements, and interaction paradigms shaping modern web experiences in 2024-2025. Updated regularly based on industry analysis, award-winning sites, and emerging patterns.

## Visual Design Trends

### 1. Bold Minimalism

**Definition**: Minimalist foundations enhanced with bold typography, intentional color, and confident white space.

**Key Characteristics**:
- Ultra-large typography (80px-200px+ headlines)
- Limited color palettes (2-4 colors max)
- Generous white space (breathing room)
- High contrast (black/white, bold accent colors)
- Geometric shapes and clean lines
- Sans-serif dominance (Inter, Space Grotesk, Sora)

**Examples**:
- Apple product pages
- Linear.app
- Stripe documentation
- Vercel website

**Implementation Tips**:
```css
/* Fluid typography for bold headlines */
h1 {
  font-size: clamp(3rem, 8vw, 10rem);
  font-weight: 700;
  line-height: 0.95;
  letter-spacing: -0.03em;
}

/* Generous spacing */
section {
  padding: clamp(3rem, 10vw, 8rem) 0;
}
```

**Why It Works**: Reduces cognitive load, focuses attention, loads fast, works across devices.

---

### 2. Kinetic Typography

**Definition**: Text that moves, transforms, and responds to user interaction.

**Patterns**:

**a) Variable Font Animations**:
- Weight transitions (100 → 900)
- Width morphing (condensed → expanded)
- Slant/italic transformations
- Multiple axes animating simultaneously

**Implementation**:
```css
@font-face {
  font-family: 'Inter';
  src: url('Inter-Variable.woff2') format('woff2-variations');
  font-weight: 100 900;
}

h1 {
  font-variation-settings: 'wght' 300;
  transition: font-variation-settings 0.3s;
}

h1:hover {
  font-variation-settings: 'wght' 900;
}
```

**b) Text Split & Stagger**:
- Reveal by character, word, or line
- Staggered entrance animations
- 3D text transformations

**c) Scroll-Linked Text**:
- Text color change on scroll
- Weight increase/decrease
- Size transformations
- Parallax text layers

**Related Skills**: `gsap-scrolltrigger` for text animations, `motion-framer` for React text effects

---

### 3. Glassmorphism 2.0

**Evolution**: Refined frosted-glass aesthetic with better accessibility and performance.

**Modern Approach** (2024):
```css
.glass-card {
  /* More subtle, accessible backgrounds */
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(12px) saturate(150%);

  /* Higher contrast borders */
  border: 1px solid rgba(255, 255, 255, 0.18);

  /* Softer, more realistic shadows */
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);

  border-radius: 16px;
}

/* Dark mode variant */
@media (prefers-color-scheme: dark) {
  .glass-card {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }
}
```

**Accessibility Considerations**:
- Ensure text has 4.5:1+ contrast on glass backgrounds
- Test with screen readers (ensure content is readable)
- Provide high-contrast mode alternative

**Performance**:
- `backdrop-filter` can be expensive on mobile
- Use sparingly (2-3 glass elements max per viewport)
- Consider `will-change: backdrop-filter` during animations only

---

### 4. Gradient Mesh Backgrounds

**Definition**: Complex, multi-color gradients with organic blob shapes.

**Tools**:
- CSS: `background: radial-gradient()` layering
- SVG: Gradient mesh filters
- Canvas/WebGL: Shader-based gradients (Vanta.js)

**Modern Gradient System**:
```css
:root {
  /* Define gradient stops */
  --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-2: radial-gradient(circle at 20% 50%, #f093fb 0%, #f5576c 100%);
  --gradient-mesh:
    radial-gradient(at 27% 37%, hsla(215, 98%, 61%, 1) 0px, transparent 50%),
    radial-gradient(at 97% 21%, hsla(125, 98%, 72%, 1) 0px, transparent 50%),
    radial-gradient(at 52% 99%, hsla(354, 98%, 61%, 1) 0px, transparent 50%),
    radial-gradient(at 10% 29%, hsla(256, 96%, 67%, 1) 0px, transparent 50%);
}

.hero {
  background: var(--gradient-mesh);
  background-size: 400% 400%;
  animation: gradient-shift 15s ease infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

**Animated Gradients** (WebGL approach with Vanta.js):
- WAVES effect with custom colors
- CELLS effect for organic feel
- FOG for atmospheric backgrounds

**Related Skills**: `lightweight-3d-effects` (Vanta.js backgrounds)

---

### 5. Neumorphism (Evolved)

**Status**: Declining but still used for specific contexts (iOS apps, dashboards).

**Modern Implementation** (Improved contrast):
```css
.neomorphic-card {
  background: #e0e5ec;
  box-shadow:
    /* Light shadow */
    8px 8px 16px rgba(163, 177, 198, 0.6),
    /* Dark shadow */
    -8px -8px 16px rgba(255, 255, 255, 0.8);

  border-radius: 16px;
  padding: 2rem;

  /* CRITICAL: Ensure contrast for accessibility */
  color: #1a1a1a; /* 11.6:1 contrast ratio */
}

/* Interactive state */
.neomorphic-card:active {
  box-shadow:
    inset 4px 4px 8px rgba(163, 177, 198, 0.6),
    inset -4px -4px 8px rgba(255, 255, 255, 0.8);
}
```

**Why It's Declining**: Accessibility concerns (low contrast), limited color palette, heavy shadows impact performance.

---

### 6. Dark Mode as Default

**Trend**: Many sites now default to dark mode with light mode as alternative.

**Best Practices** (2024):
```css
/* Use system preference as default */
:root {
  color-scheme: light dark;
}

/* Dark mode first */
:root {
  --color-bg: #0a0a0a;
  --color-text: #e5e5e5;
  --color-accent: #3b82f6;
}

/* Light mode override */
@media (prefers-color-scheme: light) {
  :root {
    --color-bg: #ffffff;
    --color-text: #171717;
    --color-accent: #2563eb;
  }
}

/* Manual toggle support */
[data-theme="light"] {
  --color-bg: #ffffff;
  --color-text: #171717;
}

[data-theme="dark"] {
  --color-bg: #0a0a0a;
  --color-text: #e5e5e5;
}
```

**Color Adjustments for Dark Mode**:
- Reduce saturation by 10-20%
- Lower brightness for vibrant colors
- Use warmer blacks (#0a0a0a, not pure #000)
- Increase contrast for text (7:1+ ratio)

---

### 7. Asymmetric Layouts

**Definition**: Breaking the grid for visual interest and hierarchy.

**Patterns**:
- Split-screen layouts (60/40, 70/30)
- Overlapping elements with z-index
- Diagonal sections
- Off-grid text positioning
- Broken grid systems

**CSS Grid Implementation**:
```css
.asymmetric-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 2rem;
}

.feature-1 {
  /* Spans 7 columns, offset by 1 */
  grid-column: 2 / 9;
  grid-row: 1;
}

.feature-2 {
  /* Overlaps with feature-1 */
  grid-column: 8 / 13;
  grid-row: 1;
  margin-top: 4rem; /* Offset vertically */
  z-index: 2;
}
```

**Examples**:
- Awwwards winners (70%+ use asymmetry)
- Design agency portfolios
- Product launch pages

---

## Interaction Trends

### 8. Micro-Interactions Everywhere

**Definition**: Small, delightful animations that provide feedback and enhance usability.

**Categories & Examples**:

**a) Button Interactions**:
- Hover lift (transform: translateY(-2px))
- Press down (scale: 0.98)
- Ripple effect on click
- Color shift transitions

**b) Form Feedback**:
- Input focus animations (border glow)
- Success/error state transitions
- Character count with progress ring
- Password strength indicator

**c) Loading States**:
- Skeleton screens (better than spinners)
- Progress indicators
- Optimistic UI updates
- Staggered content reveals

**d) Navigation**:
- Hamburger to X transitions
- Dropdown reveals with stagger
- Active state indicators
- Scroll progress bars

**Implementation** (Framer Motion):
```jsx
const buttonVariants = {
  idle: { scale: 1, y: 0 },
  hover: { scale: 1.05, y: -2 },
  tap: { scale: 0.98, y: 0 }
};

<motion.button
  variants={buttonVariants}
  initial="idle"
  whileHover="hover"
  whileTap="tap"
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  Click me
</motion.button>
```

**Related Skills**: `motion-framer`, `react-spring-physics`, `animejs`

---

### 9. Scroll-Driven Storytelling

**Definition**: Content reveals, transforms, and tells a story as the user scrolls.

**Techniques**:

**a) Pinned Sections with Scrubbing**:
```javascript
// Pin section while content scrubs through
gsap.to(".content", {
  scrollTrigger: {
    trigger: ".section",
    start: "top top",
    end: "+=3000", // 3000px of scroll
    scrub: 1,
    pin: true
  },
  opacity: 1,
  scale: 1.2
});
```

**b) Horizontal Scroll Galleries**:
- Card-based portfolios
- Timeline experiences
- Product showcases

**c) Parallax Layers**:
- Foreground, midground, background at different speeds
- 3D depth illusion
- Hero section parallax

**d) Progress Indicators**:
- Reading progress bars
- Section progress dots
- Animated SVG paths

**Examples**:
- Apple product pages (iPhone, MacBook)
- Stripe's annual reports
- Web agency showcases

**Related Skills**: `gsap-scrolltrigger`, `locomotive-scroll`

---

### 10. Cursor Effects & Custom Cursors

**Trend**: Custom cursors that enhance interaction and provide visual delight.

**Patterns**:

**a) Dot Follower**:
```javascript
const cursor = { x: 0, y: 0 };
const follower = { x: 0, y: 0 };

document.addEventListener('mousemove', (e) => {
  cursor.x = e.clientX;
  cursor.y = e.clientY;
});

function updateCursor() {
  // Smooth follow with easing
  follower.x += (cursor.x - follower.x) * 0.1;
  follower.y += (cursor.y - follower.y) * 0.1;

  cursorDot.style.transform = `translate(${follower.x}px, ${follower.y}px)`;
  requestAnimationFrame(updateCursor);
}
```

**b) Contextual Cursors**:
- "View" on images
- "Drag" on sliders
- "Play" on videos
- Magnetic attraction to buttons

**c) Blend Mode Cursors**:
```css
.cursor {
  mix-blend-mode: difference;
  /* Inverts colors underneath */
}
```

**Accessibility**:
- Hide on touch devices
- Respect `prefers-reduced-motion`
- Don't hide native cursor completely (layer on top)

---

### 11. 3D Elements & WebGL

**Status**: Increasingly mainstream with improved performance and tooling.

**Use Cases**:
- Hero backgrounds (Vanta.js waves, particles)
- Product viewers (rotate, zoom, configure)
- Data visualization (3D charts, globes)
- Immersive experiences (games, virtual tours)

**Performance-First Approach**:
```javascript
// Lazy load 3D content
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      // Load 3D scene
      loadThreeJSScene();
      observer.unobserve(entry.target);
    }
  });
});

observer.observe(document.querySelector('.3d-container'));
```

**Lightweight 3D Options**:
- Vanta.js for backgrounds (uses Three.js)
- Zdog for flat-style 3D illustrations
- Spline for designer-friendly 3D

**Full 3D Engines**:
- Three.js for custom scenes
- React Three Fiber for React apps
- Babylon.js for physics and VR

**Related Skills**: `threejs-webgl`, `react-three-fiber`, `lightweight-3d-effects`

---

### 12. Voice & Conversational UI

**Emerging Trend**: Voice commands and conversational interfaces.

**Patterns**:
- Voice search integration
- Chatbot interfaces (natural language)
- Voice-controlled navigation
- Audio feedback for interactions

**Implementation Considerations**:
- Web Speech API for voice input
- Text-to-speech for feedback
- Fallback to text input
- Accessibility: don't require voice-only

---

## Technical Trends

### 13. Performance-First Design

**Core Web Vitals as Design Constraints**:

**LCP (Largest Contentful Paint) < 2.5s**:
- Optimize hero images (WebP/AVIF)
- Inline critical CSS
- Preload key resources
- Avoid layout shifts

**FID (First Input Delay) < 100ms**:
- Defer non-critical JavaScript
- Split code bundles
- Use passive event listeners
- Minimize main thread work

**CLS (Cumulative Layout Shift) < 0.1**:
- Reserve space for images (aspect-ratio)
- Avoid inserting content above existing content
- Use CSS transforms, not position changes

**Design Implications**:
- Avoid web fonts that cause FOIT/FOUT
- Use system fonts for body text
- Lazy load below-fold content
- Progressive enhancement mindset

---

### 14. Component-Driven Design Systems

**Approach**: Design and build in reusable components.

**Tools**:
- Figma with variants and auto-layout
- Storybook for component documentation
- Design tokens (JSON format)
- Automated design-to-code (Figma plugins)

**Component Architecture**:
```
Design System/
├── Foundations/
│   ├── Colors (tokens)
│   ├── Typography (scales)
│   ├── Spacing (scales)
│   └── Shadows (elevation)
├── Components/
│   ├── Atoms (Button, Input, Icon)
│   ├── Molecules (SearchBar, Card)
│   ├── Organisms (Header, Footer)
│   └── Templates (PageLayout)
└── Patterns/
    ├── Navigation patterns
    ├── Form patterns
    └── Animation patterns
```

**Related Skills**: `animated-component-libraries`

---

### 15. AI-Enhanced Design

**Applications**:

**a) Content Generation**:
- AI-written copy (with human editing)
- Image generation (Midjourney, DALL-E)
- Icon generation
- Design variations

**b) Personalization**:
- Dynamic layouts based on user behavior
- A/B testing with AI optimization
- Adaptive color schemes
- Content recommendations

**c) Accessibility**:
- AI-generated alt text
- Automatic color contrast adjustments
- Smart keyboard navigation
- Content simplification

**Implementation**:
- Edge functions for fast personalization
- Client-side ML models (TensorFlow.js)
- Privacy-preserving personalization

---

### 16. Progressive Web Apps (PWAs)

**Status**: Mainstream adoption, especially for mobile-first products.

**Key Features**:
- Offline functionality
- Install to home screen
- Push notifications
- Background sync
- Native-like performance

**Design Considerations**:
- Mobile-first responsive design
- Touch-friendly interactions (44px+ targets)
- Offline-first content strategy
- Loading states for sync
- Native-feeling animations

---

## Color Trends

### 17. Color Palette Trends (2024-2025)

**Trending Color Schemes**:

**a) High Contrast Duotone**:
- Black + bright accent (electric blue, hot pink, lime green)
- Minimal, punchy, attention-grabbing

**b) Muted Earth Tones**:
- Terracotta, sage green, warm beige
- Natural, calming, sustainable aesthetic

**c) Neon Gradients**:
- Bright, saturated gradient meshes
- Cyberpunk aesthetic
- Gaming and tech brands

**d) Monochromatic + Accent**:
- Single hue with varying lightness
- One bold accent color
- Sophisticated, cohesive

**Color Space Evolution**:
```css
/* OKLCH for perceptual uniformity */
:root {
  --color-primary: oklch(60% 0.2 250);
  /* 60% lightness, 0.2 chroma, 250° hue */

  /* Benefits: */
  /* - Perceptually uniform lightness */
  /* - Wider color gamut than RGB */
  /* - Easier to create accessible palettes */
}
```

---

## Typography Trends

### 18. Variable Fonts Mainstream

**Adoption**: Major sites now using variable fonts by default.

**Popular Variable Fonts**:
- Inter (UI text)
- Space Grotesk (headlines)
- Recursive (code & UI)
- Fraunces (display serif)
- Outfit (geometric sans)

**Advantages**:
- Single file, multiple weights/styles
- Animation possibilities
- Fine-grained control (weight: 347)
- Smaller file size than multiple weights

**Implementation**:
```css
@font-face {
  font-family: 'Inter';
  src: url('Inter-Variable.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
}

h1 {
  font-family: 'Inter', sans-serif;
  font-weight: 750; /* Any value 100-900 */
}
```

---

### 19. Oversized Typography

**Trend**: Headlines at 100px-300px for desktop.

**Fluid Typography System**:
```css
:root {
  --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
  --font-size-lg: clamp(1.5rem, 1.2rem + 1.5vw, 2.5rem);
  --font-size-xl: clamp(2rem, 1.5rem + 2.5vw, 4rem);
  --font-size-2xl: clamp(3rem, 2rem + 5vw, 8rem);
  --font-size-3xl: clamp(4rem, 2rem + 10vw, 12rem);
}

h1 {
  font-size: var(--font-size-3xl);
  line-height: 0.95;
  letter-spacing: -0.03em;
}
```

**Design Considerations**:
- Tight line-height (0.9-1.0)
- Negative letter-spacing (-0.02 to -0.04em)
- Strong font weight (700-900)
- Responsive scaling with clamp()

---

## Layout Trends

### 20. Broken Grid Layouts

**Definition**: Intentionally breaking traditional grid systems for visual interest.

**Techniques**:
- Overlapping elements
- Off-grid positioning
- Diagonal layouts
- Negative space as design element
- Z-axis layering

**CSS Grid + Subgrid**:
```css
.parent-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 2rem;
}

.child {
  /* Subgrid inherits parent's columns */
  display: grid;
  grid-template-columns: subgrid;
  grid-column: span 6;
}
```

---

### 21. Single-Page Experiences

**Trend**: Entire site on one scrollable page.

**Patterns**:
- Section-based navigation (anchor links)
- Full-screen sections
- Scroll-driven reveals
- Smooth scrolling between sections

**Benefits**:
- Cohesive narrative flow
- No page load transitions
- Mobile-friendly (swipe to scroll)
- Performance (single bundle)

**Challenges**:
- SEO (use meaningful sections with h2-h6)
- Deep linking (use hash routing)
- Back button behavior
- Large bundle size

---

## Emerging & Experimental

### 22. AI-Generated Visuals

**Tools**:
- Midjourney for illustrations
- DALL-E 3 for specific images
- Stable Diffusion for customization

**Use Cases**:
- Hero backgrounds
- Blog post headers
- Icon generation
- Abstract patterns

**Ethical Considerations**:
- Disclose AI-generated content
- Review for bias and appropriateness
- Ensure licensing rights
- Don't replace human designers for key visuals

---

### 23. Web3 Design Patterns

**Characteristics**:
- Wallet connection UIs
- NFT galleries
- Token-gated content
- Blockchain transaction states
- Decentralized identity

**Design Challenges**:
- Explaining complex concepts simply
- Transaction loading states (slow blockchains)
- Error handling (failed transactions)
- Gas fee transparency

---

### 24. Spatial Computing & 3D Interfaces

**Future Trend**: Preparing for AR/VR mainstream adoption.

**Patterns**:
- Depth-based layering
- 3D navigation
- Gesture controls
- Spatial audio cues

**Implementation**: WebXR API, A-Frame, Babylon.js

**Related Skills**: `aframe-webxr`, `babylonjs-engine`

---

## Anti-Trends (What to Avoid)

### Declining Patterns:

1. **Carousels**: Low engagement, poor accessibility
2. **Auto-Playing Videos**: Annoying, data-hungry
3. **Hamburger Menus Only**: Hide navigation
4. **Stock Photos**: Generic, unauthentic
5. **Neumorphism**: Accessibility issues
6. **Long Scroll Animations**: Frustrating on mobile
7. **Overuse of Parallax**: Motion sickness, poor performance
8. **Chatbots as First Contact**: Often unhelpful, annoying
9. **Cookie Banners That Block Content**: Poor UX
10. **Infinite Scroll Without Pagination**: SEO and UX issues

---

## Resources & Inspiration

**Award Sites**:
- Awwwards.com (daily winners)
- CSS Design Awards
- The FWA

**Trend Reports**:
- Webflow's Annual Design Report
- Dribbble Year in Review
- Behance Featured Projects

**Design Systems**:
- Material Design 3 (Google)
- Fluent 2 (Microsoft)
- Polaris (Shopify)
- Carbon (IBM)

**Tools**:
- Figma (design)
- Webflow (visual development)
- Framer (design + code)
- Spline (3D design)

---

## Forecasts (2025+)

**Emerging Trends to Watch**:

1. **AI-Personalized Experiences**: Every user sees a unique layout
2. **Voice-First Interfaces**: Beyond chatbots to full voice navigation
3. **Spatial Web**: 3D interfaces for AR/VR headsets
4. **Sustainability Indicators**: Carbon footprint of web experiences
5. **Ethical Design Standards**: Privacy, accessibility, inclusivity as default
6. **Real-Time Collaboration**: Multiplayer web experiences
7. **Generative Art**: Unique visuals for each visitor
8. **Biometric Interfaces**: Face/voice recognition for auth and personalization

**Technology Shifts**:
- WebGPU mainstream adoption (faster 3D)
- Container queries (component-based responsive design)
- View Transitions API (smooth SPA transitions)
- CSS Houdini (custom CSS magic)

---

*Last updated: 2024*
*Review quarterly for updates*



===== FILE: plugins/individual/modern-web-design/skills/modern-web-design/references/interaction_patterns.md =====

# Micro-Interaction Patterns Catalog

## Overview

Comprehensive catalog of micro-interactions for modern web interfaces. Each pattern includes implementation code, accessibility considerations, and performance notes.

Micro-interactions are small, purposeful animations that provide feedback, guide users, and enhance perceived performance.

---

## Table of Contents

1. [Button Interactions](#button-interactions)
2. [Form & Input Interactions](#form--input-interactions)
3. [Loading States](#loading-states)
4. [Navigation Interactions](#navigation-interactions)
5. [Hover Effects](#hover-effects)
6. [Toggle & Switch Interactions](#toggle--switch-interactions)
7. [Card Interactions](#card-interactions)
8. [Scroll Interactions](#scroll-interactions)
9. [Modal & Dialog Interactions](#modal--dialog-interactions)
10. [Toast & Notification Interactions](#toast--notification-interactions)

---

## Button Interactions

### 1.1 Hover Lift

**Effect**: Button lifts up slightly on hover, creating depth.

**Implementation** (CSS):
```css
.button-lift {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.button-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.button-lift:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
```

**Framer Motion**:
```jsx
<motion.button
  whileHover={{ y: -2, boxShadow: "0 4px 12px rgba(0,0,0,0.15)" }}
  whileTap={{ y: 0, boxShadow: "0 2px 4px rgba(0,0,0,0.1)" }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  Click me
</motion.button>
```

**Accessibility**: Preserve for keyboard focus states.

---

### 1.2 Ripple Effect

**Effect**: Material Design-style ripple on click.

**Implementation** (JavaScript):
```javascript
function createRipple(event) {
  const button = event.currentTarget;
  const ripple = document.createElement('span');
  const rect = button.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const x = event.clientX - rect.left - size / 2;
  const y = event.clientY - rect.top - size / 2;

  ripple.style.width = ripple.style.height = `${size}px`;
  ripple.style.left = `${x}px`;
  ripple.style.top = `${y}px`;
  ripple.classList.add('ripple');

  button.appendChild(ripple);

  setTimeout(() => ripple.remove(), 600);
}

document.querySelectorAll('.button-ripple').forEach(button => {
  button.addEventListener('click', createRipple);
});
```

**CSS**:
```css
.button-ripple {
  position: relative;
  overflow: hidden;
}

.ripple {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  transform: scale(0);
  animation: ripple-animation 0.6s ease-out;
}

@keyframes ripple-animation {
  to {
    transform: scale(4);
    opacity: 0;
  }
}
```

**Performance**: Use `will-change: transform` sparingly.

---

### 1.3 Magnetic Button

**Effect**: Button magnetically attracts cursor on proximity.

**Implementation** (GSAP):
```javascript
const button = document.querySelector('.magnetic-button');
const magneticStrength = 0.3;

button.addEventListener('mousemove', (e) => {
  const rect = button.getBoundingClientRect();
  const centerX = rect.left + rect.width / 2;
  const centerY = rect.top + rect.height / 2;
  const distanceX = (e.clientX - centerX) * magneticStrength;
  const distanceY = (e.clientY - centerY) * magneticStrength;

  gsap.to(button, {
    x: distanceX,
    y: distanceY,
    duration: 0.3,
    ease: "power2.out"
  });
});

button.addEventListener('mouseleave', () => {
  gsap.to(button, {
    x: 0,
    y: 0,
    duration: 0.5,
    ease: "elastic.out(1, 0.3)"
  });
});
```

**Accessibility**: Disable on mobile/touch devices.

---

### 1.4 Loading Button State

**Effect**: Button morphs into loading spinner.

**Framer Motion**:
```jsx
function LoadingButton() {
  const [isLoading, setIsLoading] = useState(false);

  return (
    <motion.button
      onClick={() => setIsLoading(true)}
      animate={isLoading ? "loading" : "idle"}
      disabled={isLoading}
      style={{ position: 'relative', overflow: 'hidden' }}
    >
      <motion.span
        variants={{
          idle: { opacity: 1 },
          loading: { opacity: 0 }
        }}
      >
        Submit
      </motion.span>

      <motion.div
        className="spinner"
        variants={{
          idle: { opacity: 0, scale: 0 },
          loading: { opacity: 1, scale: 1 }
        }}
        style={{ position: 'absolute', inset: 0 }}
      >
        <Spinner />
      </motion.div>
    </motion.button>
  );
}
```

**Accessibility**: Announce loading state to screen readers.

---

## Form & Input Interactions

### 2.1 Floating Label

**Effect**: Label floats up when input is focused or filled.

**Implementation**:
```css
.input-wrapper {
  position: relative;
  margin: 1rem 0;
}

.input-field {
  width: 100%;
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.input-field:focus {
  outline: none;
  border-color: #3b82f6;
}

.input-label {
  position: absolute;
  left: 1rem;
  top: 1rem;
  pointer-events: none;
  transition: all 0.2s ease;
  color: #666;
}

.input-field:focus + .input-label,
.input-field:not(:placeholder-shown) + .input-label {
  top: -0.5rem;
  left: 0.75rem;
  font-size: 0.75rem;
  background: white;
  padding: 0 0.25rem;
  color: #3b82f6;
}
```

**HTML**:
```html
<div class="input-wrapper">
  <input
    class="input-field"
    type="text"
    placeholder=" "
    required
  />
  <label class="input-label">Email address</label>
</div>
```

---

### 2.2 Input Validation Feedback

**Effect**: Instant feedback on validation state.

**React + Framer Motion**:
```jsx
function ValidatedInput({ label, validator }) {
  const [value, setValue] = useState('');
  const [isValid, setIsValid] = useState(null);

  const handleChange = (e) => {
    const newValue = e.target.value;
    setValue(newValue);
    setIsValid(validator(newValue));
  };

  return (
    <div className="input-wrapper">
      <motion.input
        value={value}
        onChange={handleChange}
        animate={{
          borderColor: isValid === null ? '#ccc' :
                      isValid ? '#10b981' : '#ef4444'
        }}
        transition={{ duration: 0.2 }}
      />

      <AnimatePresence>
        {isValid === true && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            className="success-icon"
          >
            ✓
          </motion.div>
        )}

        {isValid === false && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -10 }}
            className="error-icon"
          >
            ✗
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
```

**Accessibility**: Provide error messages, not just icons.

---

### 2.3 Password Strength Indicator

**Effect**: Visual indicator of password strength.

**Implementation**:
```jsx
function PasswordStrengthIndicator({ password }) {
  const strength = calculateStrength(password);

  const variants = {
    weak: { width: '33%', backgroundColor: '#ef4444' },
    medium: { width: '66%', backgroundColor: '#f59e0b' },
    strong: { width: '100%', backgroundColor: '#10b981' }
  };

  return (
    <div className="strength-bar-container">
      <motion.div
        className="strength-bar"
        variants={variants}
        animate={strength}
        transition={{ duration: 0.3 }}
      />
      <p className="strength-label">
        Password strength: <strong>{strength}</strong>
      </p>
    </div>
  );
}

function calculateStrength(password) {
  if (password.length < 6) return 'weak';
  if (password.length < 10) return 'medium';
  return 'strong';
}
```

---

### 2.4 Character Count with Progress

**Effect**: Shows remaining characters with visual indicator.

**Implementation**:
```jsx
function TextareaWithCount({ maxLength = 280 }) {
  const [text, setText] = useState('');
  const remaining = maxLength - text.length;
  const percentage = (text.length / maxLength) * 100;

  return (
    <div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        maxLength={maxLength}
      />

      <div className="count-indicator">
        <motion.svg
          width="40"
          height="40"
          style={{ transform: 'rotate(-90deg)' }}
        >
          <circle
            cx="20"
            cy="20"
            r="16"
            stroke="#e5e7eb"
            strokeWidth="3"
            fill="none"
          />
          <motion.circle
            cx="20"
            cy="20"
            r="16"
            stroke={remaining < 20 ? '#ef4444' : '#3b82f6'}
            strokeWidth="3"
            fill="none"
            strokeDasharray={`${2 * Math.PI * 16}`}
            animate={{
              strokeDashoffset: (1 - percentage / 100) * (2 * Math.PI * 16)
            }}
          />
        </motion.svg>
        <span className="count-text">{remaining}</span>
      </div>
    </div>
  );
}
```

---

## Loading States

### 3.1 Skeleton Screen

**Effect**: Content placeholder that mimics layout.

**Implementation**:
```css
.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s ease-in-out infinite;
  border-radius: 4px;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-text {
  height: 1rem;
  margin-bottom: 0.5rem;
}

.skeleton-title {
  height: 2rem;
  width: 60%;
  margin-bottom: 1rem;
}

.skeleton-image {
  width: 100%;
  aspect-ratio: 16 / 9;
}
```

**React Component**:
```jsx
function SkeletonCard() {
  return (
    <div className="card">
      <div className="skeleton skeleton-image" />
      <div className="skeleton skeleton-title" />
      <div className="skeleton skeleton-text" />
      <div className="skeleton skeleton-text" style={{ width: '80%' }} />
    </div>
  );
}
```

---

### 3.2 Progress Bar

**Effect**: Linear progress indicator.

**Framer Motion**:
```jsx
function ProgressBar({ progress }) {
  return (
    <div className="progress-container">
      <motion.div
        className="progress-bar"
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      />
    </div>
  );
}
```

**CSS**:
```css
.progress-container {
  width: 100%;
  height: 4px;
  background: #e5e7eb;
  border-radius: 9999px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 9999px;
}
```

---

### 3.3 Spinner

**Effect**: Rotating loading indicator.

**CSS**:
```css
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(59, 130, 246, 0.1);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

**Framer Motion (Advanced)**:
```jsx
function Spinner() {
  return (
    <motion.div
      className="spinner-container"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
    >
      <motion.div
        className="spinner"
        animate={{ rotate: 360 }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: "linear"
        }}
      />
    </motion.div>
  );
}
```

---

## Navigation Interactions

### 4.1 Hamburger Menu Animation

**Effect**: Hamburger transforms into X on click.

**CSS**:
```css
.hamburger {
  width: 30px;
  height: 20px;
  position: relative;
  cursor: pointer;
}

.hamburger span {
  display: block;
  position: absolute;
  height: 3px;
  width: 100%;
  background: #333;
  border-radius: 3px;
  transition: all 0.3s ease;
}

.hamburger span:nth-child(1) { top: 0; }
.hamburger span:nth-child(2) { top: 50%; transform: translateY(-50%); }
.hamburger span:nth-child(3) { bottom: 0; }

.hamburger.active span:nth-child(1) {
  top: 50%;
  transform: translateY(-50%) rotate(45deg);
}

.hamburger.active span:nth-child(2) {
  opacity: 0;
}

.hamburger.active span:nth-child(3) {
  bottom: 50%;
  transform: translateY(50%) rotate(-45deg);
}
```

---

### 4.2 Dropdown Menu Reveal

**Effect**: Dropdown slides down with stagger.

**Framer Motion**:
```jsx
const menuVariants = {
  closed: {
    opacity: 0,
    y: -20,
    transition: { staggerChildren: 0.05, staggerDirection: -1 }
  },
  open: {
    opacity: 1,
    y: 0,
    transition: { staggerChildren: 0.07, delayChildren: 0.1 }
  }
};

const itemVariants = {
  closed: { opacity: 0, x: -20 },
  open: { opacity: 1, x: 0 }
};

function DropdownMenu({ isOpen }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.ul
          className="dropdown"
          variants={menuVariants}
          initial="closed"
          animate="open"
          exit="closed"
        >
          {items.map((item) => (
            <motion.li key={item} variants={itemVariants}>
              {item}
            </motion.li>
          ))}
        </motion.ul>
      )}
    </AnimatePresence>
  );
}
```

---

### 4.3 Active Link Indicator

**Effect**: Animated underline follows active link.

**Framer Motion**:
```jsx
function TabNavigation() {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <nav className="tabs">
      {tabs.map((tab, index) => (
        <button
          key={tab}
          onClick={() => setActiveTab(index)}
          className={activeTab === index ? 'active' : ''}
        >
          {tab}
          {activeTab === index && (
            <motion.div
              className="active-indicator"
              layoutId="activeTab"
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
            />
          )}
        </button>
      ))}
    </nav>
  );
}
```

**CSS**:
```css
.tabs {
  display: flex;
  gap: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.tabs button {
  position: relative;
  padding: 1rem 0;
  background: none;
  border: none;
  cursor: pointer;
}

.active-indicator {
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #3b82f6;
}
```

---

## Hover Effects

### 5.1 Image Zoom on Hover

**Effect**: Image scales up slightly on hover.

**CSS**:
```css
.image-container {
  overflow: hidden;
  border-radius: 8px;
}

.image-container img {
  transition: transform 0.3s ease;
  display: block;
  width: 100%;
}

.image-container:hover img {
  transform: scale(1.05);
}
```

---

### 5.2 Tilt Effect

**Effect**: Card tilts based on mouse position.

**Vanilla-Tilt**:
```javascript
VanillaTilt.init(document.querySelectorAll(".tilt-card"), {
  max: 15,
  speed: 400,
  glare: true,
  "max-glare": 0.3
});
```

**Manual Implementation**:
```javascript
const card = document.querySelector('.tilt-card');

card.addEventListener('mousemove', (e) => {
  const rect = card.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  const centerX = rect.width / 2;
  const centerY = rect.height / 2;

  const rotateX = (y - centerY) / 10;
  const rotateY = (centerX - x) / 10;

  card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
});

card.addEventListener('mouseleave', () => {
  card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
});
```

---

### 5.3 Reveal on Hover

**Effect**: Content reveals on hover with slide/fade.

**CSS**:
```css
.card {
  position: relative;
  overflow: hidden;
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transform: translateY(100%);
  transition: all 0.3s ease;
}

.card:hover .card-overlay {
  opacity: 1;
  transform: translateY(0);
}
```

---

## Toggle & Switch Interactions

### 6.1 Toggle Switch

**Effect**: Smooth toggle with spring animation.

**Framer Motion**:
```jsx
function ToggleSwitch({ enabled, setEnabled }) {
  return (
    <motion.div
      className="switch"
      data-enabled={enabled}
      onClick={() => setEnabled(!enabled)}
      animate={{ backgroundColor: enabled ? '#3b82f6' : '#d1d5db' }}
    >
      <motion.div
        className="switch-handle"
        layout
        transition={{ type: "spring", stiffness: 500, damping: 30 }}
        style={{ justifyContent: enabled ? 'flex-end' : 'flex-start' }}
      />
    </motion.div>
  );
}
```

**CSS**:
```css
.switch {
  width: 50px;
  height: 28px;
  border-radius: 14px;
  padding: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.switch-handle {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
```

---

## Card Interactions

### 7.1 Card Expand

**Effect**: Card expands to full screen on click.

**Framer Motion with `layout`**:
```jsx
function ExpandableCard() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <motion.div
      layout
      className={isExpanded ? 'card-expanded' : 'card'}
      onClick={() => setIsExpanded(!isExpanded)}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <motion.h2 layout="position">Title</motion.h2>
      <motion.p layout="position">Content</motion.p>

      {isExpanded && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          Additional content...
        </motion.div>
      )}
    </motion.div>
  );
}
```

---

## Scroll Interactions

### 8.1 Fade In on Scroll

**Effect**: Elements fade in as they enter viewport.

**Framer Motion + `useInView`**:
```jsx
function FadeInSection({ children }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6 }}
    >
      {children}
    </motion.div>
  );
}
```

---

### 8.2 Scroll Progress Indicator

**Effect**: Shows reading progress.

**Implementation**:
```jsx
function ScrollProgress() {
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const updateProgress = () => {
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      const progress = (window.scrollY / scrollHeight) * 100;
      setScrollProgress(progress);
    };

    window.addEventListener('scroll', updateProgress);
    return () => window.removeEventListener('scroll', updateProgress);
  }, []);

  return (
    <motion.div
      className="progress-bar"
      style={{ scaleX: scrollProgress / 100, transformOrigin: 'left' }}
    />
  );
}
```

---

## Modal & Dialog Interactions

### 9.1 Modal Fade & Scale

**Effect**: Modal fades in and scales up.

**Framer Motion**:
```jsx
function Modal({ isOpen, onClose, children }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="modal-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          <motion.div
            className="modal"
            initial={{ opacity: 0, scale: 0.8, y: 50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 50 }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
          >
            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
```

**Accessibility**: Trap focus, close on Escape key, focus first element.

---

## Toast & Notification Interactions

### 10.1 Toast Notification

**Effect**: Toast slides in from top/bottom with auto-dismiss.

**Framer Motion**:
```jsx
function Toast({ message, type, onDismiss }) {
  useEffect(() => {
    const timer = setTimeout(onDismiss, 3000);
    return () => clearTimeout(timer);
  }, [onDismiss]);

  return (
    <motion.div
      className={`toast toast-${type}`}
      initial={{ opacity: 0, y: -50, scale: 0.8 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -50, scale: 0.8 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
    >
      {message}
      <button onClick={onDismiss}>×</button>
    </motion.div>
  );
}
```

---

## Accessibility Checklist

For all micro-interactions:

- [ ] **Respect `prefers-reduced-motion`**: Disable or simplify animations
- [ ] **Keyboard accessible**: All interactions work without mouse
- [ ] **Focus indicators**: Visible focus states
- [ ] **Screen reader friendly**: Announce state changes with `aria-live`
- [ ] **Touch targets**: Minimum 44x44px for mobile
- [ ] **Escape key**: Close modals/overlays
- [ ] **Loading states**: Indicate when actions are processing
- [ ] **Error states**: Clear error messages, not just visual indicators

---

## Performance Checklist

- [ ] **GPU-accelerated properties**: Use `transform` and `opacity` only
- [ ] **Avoid layout thrash**: Batch DOM reads/writes
- [ ] **RequestAnimationFrame**: For JavaScript animations
- [ ] **Will-change sparingly**: Only during active animations
- [ ] **Debounce scroll/resize**: Avoid excessive repaints
- [ ] **Lazy load**: Defer non-critical animations
- [ ] **Test on low-end devices**: Ensure 60 FPS

---

*This catalog is a living document. Patterns are updated based on modern web standards and user research.*



===== FILE: plugins/individual/modern-web-design/skills/modern-web-design/references/performance_checklist.md =====

# Web Performance Optimization Checklist

## Overview

Comprehensive performance optimization guide targeting Core Web Vitals and 60 FPS experiences. This checklist covers measurement, optimization strategies, and modern best practices.

**Performance Budget Targets**:
- Largest Contentful Paint (LCP): < 2.5s
- First Input Delay (FID): < 100ms
- Cumulative Layout Shift (CLS): < 0.1
- Interaction to Next Paint (INP): < 200ms
- Time to Interactive (TTI): < 3.8s
- First Contentful Paint (FCP): < 1.8s

---

## Table of Contents

1. [Core Web Vitals](#core-web-vitals)
2. [Animation Performance](#animation-performance)
3. [Image Optimization](#image-optimization)
4. [Font Loading](#font-loading)
5. [JavaScript Optimization](#javascript-optimization)
6. [CSS Optimization](#css-optimization)
7. [3D & WebGL Optimization](#3d--webgl-optimization)
8. [Loading Strategies](#loading-strategies)
9. [Caching & CDN](#caching--cdn)
10. [Monitoring & Measurement](#monitoring--measurement)

---

## Core Web Vitals

### Largest Contentful Paint (LCP)

**Target**: < 2.5 seconds

**What it measures**: Time until largest content element is visible.

**Optimization Checklist**:
- [ ] Optimize hero images (WebP/AVIF, < 100KB)
- [ ] Preload critical resources (`<link rel="preload">`)
- [ ] Eliminate render-blocking resources
- [ ] Use CDN for static assets
- [ ] Implement efficient server response time (< 200ms TTFB)
- [ ] Remove unused CSS/JS
- [ ] Enable compression (Brotli/gzip)

**Implementation**:
```html
<!-- Preload critical resources -->
<link rel="preload" as="image" href="hero.webp" type="image/webp">
<link rel="preload" as="font" href="inter-var.woff2" type="font/woff2" crossorigin>

<!-- Modern image formats -->
<picture>
  <source srcset="hero.avif" type="image/avif">
  <source srcset="hero.webp" type="image/webp">
  <img src="hero.jpg" alt="Hero" loading="eager" fetchpriority="high">
</picture>
```

**Debugging**:
```javascript
// Measure LCP
new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1];
  console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime);
}).observe({ entryTypes: ['largest-contentful-paint'] });
```

---

### First Input Delay (FID) / Interaction to Next Paint (INP)

**Target**: FID < 100ms, INP < 200ms

**What it measures**: Responsiveness to user interactions.

**Optimization Checklist**:
- [ ] Split long tasks (< 50ms each)
- [ ] Defer non-critical JavaScript
- [ ] Use web workers for heavy computation
- [ ] Implement code splitting
- [ ] Avoid long-running event handlers
- [ ] Debounce scroll/resize listeners
- [ ] Use passive event listeners

**Implementation**:
```javascript
// Split long tasks
function yieldToMain() {
  return new Promise(resolve => {
    setTimeout(resolve, 0);
  });
}

async function processLargeArray(array) {
  for (let i = 0; i < array.length; i++) {
    processItem(array[i]);

    // Yield every 50 items
    if (i % 50 === 0) {
      await yieldToMain();
    }
  }
}

// Passive event listeners
window.addEventListener('scroll', handleScroll, { passive: true });

// Debounced resize handler
const debouncedResize = debounce(() => {
  handleResize();
}, 150);

window.addEventListener('resize', debouncedResize);
```

---

### Cumulative Layout Shift (CLS)

**Target**: < 0.1

**What it measures**: Visual stability during page load.

**Optimization Checklist**:
- [ ] Reserve space for images (use `aspect-ratio`)
- [ ] Reserve space for ads and embeds
- [ ] Avoid inserting content above existing content
- [ ] Use CSS transforms instead of position changes
- [ ] Set explicit dimensions for iframes
- [ ] Avoid web fonts that cause FOUT/FOIT
- [ ] Use `font-display: swap` or `font-display: optional`

**Implementation**:
```css
/* Reserve space for images */
img {
  aspect-ratio: attr(width) / attr(height);
  width: 100%;
  height: auto;
}

/* Or explicit aspect ratio */
.hero-image {
  aspect-ratio: 16 / 9;
}

/* Animations: use transform, not position */
.animated {
  transform: translateX(0);
  transition: transform 0.3s;
}

.animated.active {
  transform: translateX(100px); /* Good */
  /* left: 100px; Bad - causes layout shift */
}
```

**Debugging**:
```javascript
// Measure CLS
let clsValue = 0;
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) {
      clsValue += entry.value;
      console.log('CLS:', clsValue);
    }
  }
}).observe({ entryTypes: ['layout-shift'] });
```

---

## Animation Performance

### 60 FPS Checklist

**Target**: < 16.67ms per frame

**GPU-Accelerated Properties (Use These)**:
- `transform` (translate, scale, rotate)
- `opacity`
- `filter` (some, like blur - be careful)

**Avoid Animating**:
- `top`, `left`, `right`, `bottom`
- `width`, `height`
- `margin`, `padding`
- `border-width`

**Implementation**:
```css
/* Good: GPU-accelerated */
.animated {
  transform: translateX(0);
  opacity: 1;
  transition: transform 0.3s, opacity 0.3s;
}

.animated.active {
  transform: translateX(100px) scale(1.1);
  opacity: 0.8;
}

/* Bad: triggers layout/paint */
.animated-bad {
  left: 0;
  width: 100px;
  transition: left 0.3s, width 0.3s;
}
```

### Will-Change Optimization

**Use Sparingly**:
```css
/* Only during animation */
.will-animate {
  /* Don't set will-change here */
}

.will-animate.animating {
  will-change: transform; /* Set on animation start */
}

.will-animate.done {
  will-change: auto; /* Remove after animation */
}
```

**JavaScript Control**:
```javascript
element.addEventListener('mouseenter', () => {
  element.style.willChange = 'transform';
});

element.addEventListener('mouseleave', () => {
  // Remove after animation completes
  element.addEventListener('transitionend', () => {
    element.style.willChange = 'auto';
  }, { once: true });
});
```

### RequestAnimationFrame

**Always use for JavaScript animations**:
```javascript
// Good
function animate() {
  element.style.transform = `translateX(${x}px)`;
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);

// Bad
setInterval(() => {
  element.style.transform = `translateX(${x}px)`;
}, 16); // Not synced with browser paint
```

### Performance Monitoring

**Chrome DevTools**:
```javascript
// Mark start of expensive operation
performance.mark('animation-start');

// ... do animation work ...

// Mark end
performance.mark('animation-end');

// Measure duration
performance.measure('animation-duration', 'animation-start', 'animation-end');

// Get measurement
const measure = performance.getEntriesByName('animation-duration')[0];
console.log(`Animation took ${measure.duration}ms`);
```

---

## Image Optimization

### Format Selection

**Decision Tree**:
1. **Photos**: AVIF > WebP > JPEG
2. **Graphics/logos**: SVG > WebP > PNG
3. **Animations**: WebP animated > GIF
4. **Icons**: SVG or icon fonts

**Implementation**:
```html
<picture>
  <!-- Modern browsers: AVIF (best compression) -->
  <source srcset="image.avif" type="image/avif">

  <!-- Fallback: WebP (good compression) -->
  <source srcset="image.webp" type="image/webp">

  <!-- Final fallback: JPEG -->
  <img src="image.jpg" alt="Description" loading="lazy">
</picture>
```

### Responsive Images

**Checklist**:
- [ ] Use `srcset` for multiple resolutions
- [ ] Define `sizes` attribute
- [ ] Serve appropriately sized images (not full-res everywhere)
- [ ] Use lazy loading for below-fold images
- [ ] Set explicit dimensions to prevent CLS

**Implementation**:
```html
<img
  src="image-800.jpg"
  srcset="
    image-400.jpg 400w,
    image-800.jpg 800w,
    image-1200.jpg 1200w,
    image-1600.jpg 1600w
  "
  sizes="
    (max-width: 640px) 100vw,
    (max-width: 1024px) 50vw,
    33vw
  "
  alt="Description"
  loading="lazy"
  width="1200"
  height="800"
>
```

### Image Compression

**Tools**:
- **CLI**: ImageMagick, Sharp (Node.js)
- **GUI**: Squoosh (web), ImageOptim (Mac)
- **Build tools**: imagemin, @squoosh/lib

**Example (Sharp)**:
```javascript
const sharp = require('sharp');

await sharp('input.jpg')
  .resize(1200, 800, { fit: 'cover' })
  .webp({ quality: 80 })
  .toFile('output.webp');

await sharp('input.jpg')
  .resize(1200, 800, { fit: 'cover' })
  .avif({ quality: 70 })
  .toFile('output.avif');
```

### Lazy Loading

**Native Lazy Loading**:
```html
<!-- Lazy load below-fold images -->
<img src="image.jpg" loading="lazy" alt="Description">

<!-- Eager load above-fold images -->
<img src="hero.jpg" loading="eager" fetchpriority="high" alt="Hero">
```

**Intersection Observer (Advanced)**:
```javascript
const imageObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.classList.remove('lazy');
      observer.unobserve(img);
    }
  });
});

document.querySelectorAll('img[data-src]').forEach(img => {
  imageObserver.observe(img);
});
```

---

## Font Loading

### Font Display Strategy

**Options**:
- `swap`: Show fallback, swap when loaded (FOUT - Flash of Unstyled Text)
- `optional`: Use cached font if available, otherwise use fallback
- `fallback`: Brief block, swap if fast, fallback if slow

**Recommended**:
```css
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap; /* Show fallback immediately */
}
```

### Font Subsetting

**Reduce file size by including only needed characters**:

**Tools**: `pyftsubset` (part of fonttools)

```bash
# Include only Latin characters
pyftsubset input.ttf \
  --output-file=output.woff2 \
  --flavor=woff2 \
  --layout-features=* \
  --unicodes=U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD
```

### Preload Critical Fonts

```html
<link
  rel="preload"
  as="font"
  href="/fonts/inter-var.woff2"
  type="font/woff2"
  crossorigin
>
```

### System Font Stack

**Performance-first approach**:
```css
body {
  font-family:
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    Oxygen,
    Ubuntu,
    Cantarell,
    sans-serif;
}
```

---

## JavaScript Optimization

### Code Splitting

**Route-based splitting**:
```javascript
// React Router
const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));
const Gallery = lazy(() => import('./pages/Gallery'));

<Suspense fallback={<Loading />}>
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/about" element={<About />} />
    <Route path="/gallery" element={<Gallery />} />
  </Routes>
</Suspense>
```

**Component-based splitting**:
```javascript
// Load heavy components only when needed
const HeavyChart = lazy(() => import('./components/HeavyChart'));

function Dashboard() {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <button onClick={() => setShowChart(true)}>Show Chart</button>
      {showChart && (
        <Suspense fallback={<Skeleton />}>
          <HeavyChart />
        </Suspense>
      )}
    </div>
  );
}
```

### Tree Shaking

**Ensure tree shaking works**:
```javascript
// Good: Named imports
import { map, filter } from 'lodash-es';

// Bad: Default import (imports entire library)
import _ from 'lodash';
```

### Bundle Analysis

**Webpack Bundle Analyzer**:
```bash
npm install --save-dev webpack-bundle-analyzer

# Add to webpack.config.js
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

plugins: [
  new BundleAnalyzerPlugin()
]
```

**Vite**:
```bash
npm install --save-dev rollup-plugin-visualizer

# vite.config.js
import { visualizer } from 'rollup-plugin-visualizer';

export default {
  plugins: [visualizer({ open: true })]
}
```

---

## CSS Optimization

### Critical CSS

**Inline above-the-fold CSS**:
```html
<style>
  /* Critical CSS inlined */
  body { font-family: sans-serif; }
  .hero { height: 100vh; }
</style>

<!-- Defer non-critical CSS -->
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="styles.css"></noscript>
```

**Tools**:
- Critical (npm package)
- Critters (Vite/Webpack plugin)

### Remove Unused CSS

**PurgeCSS**:
```javascript
// postcss.config.js
module.exports = {
  plugins: [
    require('@fullhuman/postcss-purgecss')({
      content: ['./src/**/*.html', './src/**/*.jsx'],
      defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || []
    })
  ]
}
```

### CSS Containment

**Improve rendering performance**:
```css
.card {
  /* Isolate layout calculations */
  contain: layout style paint;
}

.article {
  /* More aggressive containment */
  contain: strict;
}
```

---

## 3D & WebGL Optimization

### Loading Strategy

**Checklist**:
- [ ] Show placeholder while loading
- [ ] Load 3D content below fold lazily
- [ ] Use low-poly models initially
- [ ] Progressive enhancement with high-poly

**Implementation**:
```javascript
// Lazy load Three.js scene
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      loadThreeJSScene();
      observer.unobserve(entry.target);
    }
  });
});

observer.observe(document.querySelector('.3d-container'));
```

### Runtime Performance

**Checklist**:
- [ ] Implement object pooling (reuse objects)
- [ ] Use LOD (Level of Detail)
- [ ] Frustum culling (don't render off-screen objects)
- [ ] Texture compression (Basis Universal, KTX2)
- [ ] Reduce polygon count (< 100k for real-time)
- [ ] Limit draw calls (< 100 per frame)
- [ ] Use instancing for repeated geometry

**Three.js Example**:
```javascript
// Object pooling
const objectPool = [];

function getObject() {
  return objectPool.length > 0 ? objectPool.pop() : createNewObject();
}

function releaseObject(obj) {
  objectPool.push(obj);
}

// LOD (Level of Detail)
const lod = new THREE.LOD();
lod.addLevel(highPolyMesh, 0);   // 0-50m
lod.addLevel(mediumPolyMesh, 50); // 50-100m
lod.addLevel(lowPolyMesh, 100);   // 100m+
scene.add(lod);

// Instancing
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshStandardMaterial();
const count = 10000;

const mesh = new THREE.InstancedMesh(geometry, material, count);
scene.add(mesh);
```

### Texture Optimization

**Checklist**:
- [ ] Use power-of-two dimensions (512, 1024, 2048)
- [ ] Compress textures (Basis, KTX2)
- [ ] Use texture atlases
- [ ] Reduce texture resolution (don't use 4K everywhere)
- [ ] Enable mipmaps

---

## Loading Strategies

### Critical Rendering Path

**Optimize the order**:

1. **HTML** (initial)
2. **Critical CSS** (inlined)
3. **Critical JavaScript** (defer rest)
4. **Fonts** (preload, font-display: swap)
5. **Images** (lazy load below-fold)

**Implementation**:
```html
<!DOCTYPE html>
<html>
<head>
  <!-- Critical CSS inlined -->
  <style>/* Critical styles */</style>

  <!-- Preload critical resources -->
  <link rel="preload" as="font" href="font.woff2" type="font/woff2" crossorigin>
  <link rel="preload" as="image" href="hero.webp">

  <!-- Defer non-critical CSS -->
  <link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">

  <!-- Defer JavaScript -->
  <script defer src="main.js"></script>
</head>
<body>
  <!-- Content -->
</body>
</html>
```

### Resource Hints

**Preconnect** (DNS, TCP, TLS):
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://cdn.example.com">
```

**DNS-Prefetch**:
```html
<link rel="dns-prefetch" href="https://analytics.example.com">
```

**Prefetch** (next page):
```html
<link rel="prefetch" href="/next-page.html">
```

---

## Caching & CDN

### HTTP Caching Headers

**Static Assets** (immutable):
```
Cache-Control: public, max-age=31536000, immutable
```

**HTML** (revalidate):
```
Cache-Control: no-cache
```

**API Responses**:
```
Cache-Control: public, max-age=3600, must-revalidate
```

### Service Worker Caching

**Workbox**:
```javascript
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { CacheFirst, NetworkFirst } from 'workbox-strategies';

// Precache build assets
precacheAndRoute(self.__WB_MANIFEST);

// Cache images
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({ cacheName: 'images' })
);

// Network-first for HTML
registerRoute(
  ({ request }) => request.mode === 'navigate',
  new NetworkFirst({ cacheName: 'pages' })
);
```

---

## Monitoring & Measurement

### Real User Monitoring (RUM)

**Web Vitals**:
```bash
npm install web-vitals
```

```javascript
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics({ name, value, id }) {
  // Send to your analytics endpoint
  fetch('/analytics', {
    method: 'POST',
    body: JSON.stringify({ name, value, id })
  });
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

### Performance Budget

**Lighthouse CI**:
```json
// lighthouserc.json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "first-contentful-paint": ["error", {"maxNumericValue": 1800}],
        "largest-contentful-paint": ["error", {"maxNumericValue": 2500}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}],
        "total-blocking-time": ["error", {"maxNumericValue": 200}]
      }
    }
  }
}
```

### Chrome DevTools

**Performance Panel**:
1. Open DevTools (F12)
2. Performance tab
3. Click Record
4. Interact with page
5. Stop recording
6. Analyze flame chart

**Look for**:
- Long tasks (> 50ms)
- Excessive layout thrashing
- Forced synchronous layouts
- Paint flashing

---

## Quick Wins Checklist

**Immediate Impact**:
- [ ] Enable Brotli/gzip compression
- [ ] Implement lazy loading for images
- [ ] Add `width` and `height` to images (prevent CLS)
- [ ] Use modern image formats (WebP/AVIF)
- [ ] Preload critical resources
- [ ] Defer non-critical JavaScript
- [ ] Use CDN for static assets
- [ ] Enable HTTP/2 or HTTP/3
- [ ] Minify CSS and JavaScript
- [ ] Remove unused CSS/JS

**High Impact**:
- [ ] Implement code splitting
- [ ] Optimize images (< 100KB)
- [ ] Use system fonts or preload web fonts
- [ ] Inline critical CSS
- [ ] Implement service worker caching
- [ ] Optimize animation performance (use transforms)
- [ ] Reduce JavaScript bundle size (< 200KB)
- [ ] Set up performance monitoring

---

*Last updated: 2024*
*Benchmarks based on median 4G mobile connections*



===== FILE: plugins/individual/modern-web-design/agents/modern-web-design-specialist.md =====

# Modern Web Design Specialist

## Role

Expert specialist in Modern Web Design implementation, patterns, and best practices.

## Expertise

- Modern Web Design core concepts and patterns
- Integration with other libraries and frameworks
- Performance optimization
- Common pitfalls and solutions
- Best practices and conventions

## When to use

Activate this agent when working on:
- Modern Web Design implementation challenges
- Integration with other technologies
- Performance optimization
- Troubleshooting and debugging
- Architecture decisions

## Approach

1. Understand project requirements and context
2. Apply Modern Web Design best practices
3. Recommend optimal implementation patterns
4. Identify and solve common issues
5. Provide detailed guidance and examples

## Tools

This agent has access to:
- Modern Web Design skill knowledge
- Pattern libraries and examples
- Troubleshooting guides
- Integration patterns



===== FILE: plugins/individual/modern-web-design/commands/design_audit.md =====

# /modern-web-design-design_audit

Modern Web Design - Design Audit

## Description

Executes the design_audit script for Modern Web Design.

## Usage

```bash
/modern-web-design-design_audit
```

## Implementation

This command runs the `design_audit.py` script from the Modern Web Design skill, which provides automated assistance for design audit.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/modern-web-design/commands/pattern_generator.md =====

# /modern-web-design-pattern_generator

Modern Web Design - Pattern Generator

## Description

Executes the pattern_generator script for Modern Web Design.

## Usage

```bash
/modern-web-design-pattern_generator
```

## Implementation

This command runs the `pattern_generator.py` script from the Modern Web Design skill, which provides automated assistance for pattern generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/modern-web-design/skills/modern-web-design/scripts/design_audit.py =====

```py
#!/usr/bin/env python3
"""
Modern Web Design Auditor

Audits HTML/CSS code for:
- Accessibility compliance (WCAG)
- Performance best practices
- Modern design pattern usage
- SEO basics

Usage:
    ./design_audit.py                              # Interactive mode
    ./design_audit.py --file index.html            # Audit specific file
    ./design_audit.py --file index.html --report audit.txt  # Save report
"""

import sys
import argparse
import re
from pathlib import Path
from collections import defaultdict


class DesignAuditor:
    """Audits web design code for best practices."""

    def __init__(self, html_content):
        self.html = html_content
        self.issues = defaultdict(list)
        self.warnings = defaultdict(list)
        self.passes = defaultdict(list)

    def audit(self):
        """Run all audits."""
        self.audit_accessibility()
        self.audit_performance()
        self.audit_seo()
        self.audit_responsive()
        self.audit_modern_practices()

    def audit_accessibility(self):
        """Audit for accessibility issues."""
        category = 'Accessibility'

        # Check for alt attributes on images
        imgs_without_alt = re.findall(r'<img(?![^>]*alt=)[^>]*>', self.html, re.IGNORECASE)
        if imgs_without_alt:
            self.issues[category].append(
                f"Found {len(imgs_without_alt)} images without alt attributes"
            )
        else:
            self.passes[category].append("All images have alt attributes")

        # Check for lang attribute
        if not re.search(r'<html[^>]+lang=', self.html, re.IGNORECASE):
            self.issues[category].append("Missing lang attribute on <html> element")
        else:
            self.passes[category].append("HTML lang attribute present")

        # Check for semantic HTML
        if '<div class="header"' in self.html or '<div id="header"' in self.html:
            self.warnings[category].append("Consider using <header> instead of div with class/id 'header'")

        if '<div class="nav"' in self.html or '<div id="nav"' in self.html:
            self.warnings[category].append("Consider using <nav> instead of div with class/id 'nav'")

        if '<div class="footer"' in self.html or '<div id="footer"' in self.html:
            self.warnings[category].append("Consider using <footer> instead of div with class/id 'footer'")

        # Check for proper heading hierarchy
        h1_count = len(re.findall(r'<h1[^>]*>', self.html, re.IGNORECASE))
        if h1_count == 0:
            self.issues[category].append("No <h1> element found")
        elif h1_count > 1:
            self.warnings[category].append(f"Multiple <h1> elements found ({h1_count}). Consider using only one per page")

        # Check for aria-labels on icon buttons
        button_pattern = r'<button[^>]*>[\s]*<(?:svg|i|span)[^>]*>[\s]*</(?:svg|i|span)>[\s]*</button>'
        icon_buttons = re.findall(button_pattern, self.html, re.IGNORECASE)
        for button in icon_buttons:
            if 'aria-label' not in button:
                self.warnings[category].append("Icon button found without aria-label")
                break

        # Check for form labels
        inputs = re.findall(r'<input[^>]*>', self.html, re.IGNORECASE)
        for input_tag in inputs:
            if 'id=' in input_tag:
                input_id = re.search(r'id="([^"]+)"', input_tag)
                if input_id:
                    label_pattern = f'for="{input_id.group(1)}"'
                    if label_pattern not in self.html:
                        self.warnings[category].append(f"Input with id='{input_id.group(1)}' has no associated label")

        # Check for skip links
        if not re.search(r'skip to (main |)content', self.html, re.IGNORECASE):
            self.warnings[category].append("Consider adding a skip link for keyboard navigation")

    def audit_performance(self):
        """Audit for performance issues."""
        category = 'Performance'

        # Check for inline styles (should be minimal)
        inline_styles = re.findall(r'style="[^"]*"', self.html)
        if len(inline_styles) > 10:
            self.warnings[category].append(
                f"Found {len(inline_styles)} inline styles. Consider moving to external CSS."
            )

        # Check for lazy loading
        imgs = re.findall(r'<img[^>]*>', self.html, re.IGNORECASE)
        lazy_imgs = [img for img in imgs if 'loading="lazy"' in img or "loading='lazy'" in img]
        if imgs and not lazy_imgs:
            self.warnings[category].append(
                "Consider adding loading='lazy' to below-fold images"
            )

        # Check for modern image formats
        if re.search(r'<img[^>]+src="[^"]+\.(jpg|jpeg|png)"', self.html, re.IGNORECASE):
            if not re.search(r'<picture>|<source[^>]+type="image/webp"', self.html, re.IGNORECASE):
                self.warnings[category].append(
                    "Consider using modern image formats (WebP/AVIF) with <picture> element"
                )

        # Check for preload/prefetch
        if re.search(r'<link[^>]+rel="preload"', self.html, re.IGNORECASE):
            self.passes[category].append("Using preload for critical resources")

        # Check for async/defer on scripts
        scripts = re.findall(r'<script[^>]*src="[^"]*"[^>]*>', self.html, re.IGNORECASE)
        scripts_without_async_defer = [s for s in scripts if 'async' not in s and 'defer' not in s]
        if scripts_without_async_defer:
            self.warnings[category].append(
                f"Found {len(scripts_without_async_defer)} script tags without async or defer attributes"
            )

        # Check for width/height on images (prevents CLS)
        imgs_without_dimensions = [
            img for img in imgs
            if not ('width=' in img and 'height=' in img)
            and 'aspect-ratio' not in self.html
        ]
        if imgs_without_dimensions:
            self.warnings[category].append(
                f"Found {len(imgs_without_dimensions)} images without explicit dimensions (width/height). This can cause Cumulative Layout Shift."
            )

    def audit_seo(self):
        """Audit for SEO basics."""
        category = 'SEO'

        # Check for title tag
        if not re.search(r'<title>[^<]+</title>', self.html, re.IGNORECASE):
            self.issues[category].append("Missing <title> tag")
        else:
            title = re.search(r'<title>([^<]+)</title>', self.html, re.IGNORECASE)
            if title and len(title.group(1)) < 10:
                self.warnings[category].append("Title tag is too short (< 10 characters)")
            else:
                self.passes[category].append("Title tag present and sufficient length")

        # Check for meta description
        if not re.search(r'<meta[^>]+name="description"', self.html, re.IGNORECASE):
            self.warnings[category].append("Missing meta description tag")
        else:
            self.passes[category].append("Meta description present")

        # Check for viewport meta tag
        if not re.search(r'<meta[^>]+name="viewport"', self.html, re.IGNORECASE):
            self.issues[category].append("Missing viewport meta tag (required for mobile)")
        else:
            self.passes[category].append("Viewport meta tag present")

        # Check for charset
        if not re.search(r'<meta[^>]+charset=', self.html, re.IGNORECASE):
            self.warnings[category].append("Missing charset declaration")
        else:
            self.passes[category].append("Charset declaration present")

    def audit_responsive(self):
        """Audit for responsive design."""
        category = 'Responsive Design'

        # Check for viewport meta tag
        if re.search(r'<meta[^>]+name="viewport"', self.html, re.IGNORECASE):
            self.passes[category].append("Viewport meta tag present")
        else:
            self.issues[category].append("Missing viewport meta tag")

        # Check for media queries in CSS
        if re.search(r'@media[^{]+{', self.html, re.IGNORECASE):
            self.passes[category].append("Media queries found (responsive CSS)")
        else:
            self.warnings[category].append("No media queries found. Consider adding responsive styles.")

        # Check for clamp() or min/max functions (modern responsive approach)
        if re.search(r'clamp\(|min\(|max\(', self.html, re.IGNORECASE):
            self.passes[category].append("Using modern CSS functions (clamp/min/max) for fluid sizing")

    def audit_modern_practices(self):
        """Audit for modern design practices."""
        category = 'Modern Practices'

        # Check for CSS custom properties
        if re.search(r'--[a-z-]+:', self.html, re.IGNORECASE):
            self.passes[category].append("Using CSS custom properties (variables)")

        # Check for CSS Grid or Flexbox
        if re.search(r'display:\s*(grid|flex)', self.html, re.IGNORECASE):
            self.passes[category].append("Using modern layout (Grid or Flexbox)")

        # Check for prefers-reduced-motion
        if re.search(r'prefers-reduced-motion', self.html, re.IGNORECASE):
            self.passes[category].append("Respecting prefers-reduced-motion preference")
        else:
            if re.search(r'animation:|transition:', self.html, re.IGNORECASE):
                self.warnings[category].append(
                    "Animations found but no @media (prefers-reduced-motion) rule detected"
                )

        # Check for semantic HTML5 elements
        semantic_elements = ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer']
        found_semantic = [el for el in semantic_elements if f'<{el}' in self.html.lower()]
        if found_semantic:
            self.passes[category].append(f"Using semantic HTML5 elements: {', '.join(found_semantic)}")
        else:
            self.warnings[category].append("No semantic HTML5 elements found. Consider using <header>, <nav>, <main>, etc.")

        # Check for focus-visible
        if ':focus-visible' in self.html:
            self.passes[category].append("Using :focus-visible for keyboard navigation")
        elif ':focus' in self.html:
            self.passes[category].append("Using :focus styles (consider upgrading to :focus-visible)")

    def generate_report(self):
        """Generate audit report."""
        report = []
        report.append("=" * 70)
        report.append("Modern Web Design Audit Report")
        report.append("=" * 70)
        report.append("")

        # Summary
        total_issues = sum(len(v) for v in self.issues.values())
        total_warnings = sum(len(v) for v in self.warnings.values())
        total_passes = sum(len(v) for v in self.passes.values())

        report.append("SUMMARY")
        report.append("-" * 70)
        report.append(f"❌ Issues: {total_issues}")
        report.append(f"⚠️  Warnings: {total_warnings}")
        report.append(f"✅ Passes: {total_passes}")
        report.append("")

        # Score calculation
        score = (total_passes / (total_passes + total_warnings + total_issues)) * 100 if (total_passes + total_warnings + total_issues) > 0 else 0
        report.append(f"Overall Score: {score:.1f}/100")
        report.append("")

        # Detailed results
        categories = set(list(self.issues.keys()) + list(self.warnings.keys()) + list(self.passes.keys()))

        for category in sorted(categories):
            report.append(f"\n{category}")
            report.append("-" * 70)

            if category in self.issues:
                report.append("\n❌ ISSUES (must fix):")
                for issue in self.issues[category]:
                    report.append(f"   • {issue}")

            if category in self.warnings:
                report.append("\n⚠️  WARNINGS (should fix):")
                for warning in self.warnings[category]:
                    report.append(f"   • {warning}")

            if category in self.passes:
                report.append("\n✅ PASSES:")
                for passing in self.passes[category]:
                    report.append(f"   • {passing}")

            report.append("")

        # Recommendations
        report.append("\nRECOMMENDATIONS")
        report.append("-" * 70)

        if total_issues > 0:
            report.append("1. Address all ISSUES first (accessibility and critical SEO)")
        if total_warnings > 5:
            report.append("2. Review WARNINGS and implement fixes where applicable")
        if score < 70:
            report.append("3. Consider a comprehensive design review")
        else:
            report.append("Good job! Your design follows many modern best practices.")

        report.append("")
        report.append("=" * 70)

        return "\n".join(report)


def audit_file(filepath, output_file=None):
    """Audit a specific file."""
    path = Path(filepath)

    if not path.exists():
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)

    if not path.suffix in ['.html', '.htm']:
        print(f"Warning: File '{filepath}' is not an HTML file.")

    print(f"Auditing: {path}")
    print("Please wait...\n")

    html_content = path.read_text()
    auditor = DesignAuditor(html_content)
    auditor.audit()
    report = auditor.generate_report()

    if output_file:
        output_path = Path(output_file)
        output_path.write_text(report)
        print(f"✅ Audit complete!")
        print(f"   Report saved to: {output_path}")
    else:
        print(report)


def interactive_mode():
    """Interactive audit mode."""
    print("\n" + "="*70)
    print("Modern Web Design Auditor")
    print("="*70)
    print("\nThis tool audits HTML files for:")
    print("  • Accessibility (WCAG compliance)")
    print("  • Performance best practices")
    print("  • SEO basics")
    print("  • Responsive design")
    print("  • Modern CSS/HTML practices")
    print("")

    filepath = input("Enter path to HTML file: ").strip()

    if not filepath:
        print("Error: No file path provided.")
        sys.exit(1)

    save_report = input("\nSave report to file? (y/n): ").strip().lower()

    if save_report == 'y':
        output_file = input("Enter output filename (e.g., audit-report.txt): ").strip()
        if not output_file:
            output_file = "audit-report.txt"
        audit_file(filepath, output_file)
    else:
        audit_file(filepath)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Audit web design code for best practices'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='HTML file to audit'
    )
    parser.add_argument(
        '--report',
        type=str,
        help='Output file for audit report'
    )

    args = parser.parse_args()

    if args.file:
        audit_file(args.file, args.report)
    else:
        interactive_mode()


if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/modern-web-design/skills/modern-web-design/scripts/pattern_generator.py =====

```py
#!/usr/bin/env python3
"""
Modern Web Design Pattern Generator

Generates boilerplate code for common modern web design patterns including:
- Hero sections
- Card layouts
- Navigation patterns
- Form patterns
- Animation patterns

Usage:
    ./pattern_generator.py                          # Interactive mode
    ./pattern_generator.py --pattern hero           # Generate specific pattern
    ./pattern_generator.py --pattern card --output card.html  # Output to file
"""

import sys
import argparse
from pathlib import Path

# Pattern templates
PATTERNS = {
    'hero': {
        'name': 'Immersive Hero Section',
        'description': 'Full-viewport hero with animated background',
        'html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hero Section</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        .hero {
            position: relative;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .hero__bg {
            position: absolute;
            inset: 0;
            opacity: 0.3;
        }

        .hero__content {
            position: relative;
            z-index: 2;
            text-align: center;
            color: white;
            max-width: 800px;
            padding: 2rem;
        }

        .hero__title {
            font-size: clamp(3rem, 8vw, 6rem);
            font-weight: 700;
            line-height: 0.95;
            letter-spacing: -0.03em;
            margin-bottom: 1.5rem;
            animation: fadeInUp 0.8s ease;
        }

        .hero__subtitle {
            font-size: clamp(1.25rem, 2.5vw, 1.75rem);
            margin-bottom: 2rem;
            opacity: 0.9;
            animation: fadeInUp 0.8s ease 0.2s backwards;
        }

        .hero__cta {
            display: inline-block;
            padding: 1rem 2.5rem;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 1.125rem;
            transition: transform 0.2s, box-shadow 0.2s;
            animation: fadeInUp 0.8s ease 0.4s backwards;
        }

        .hero__cta:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }

        .scroll-indicator {
            position: absolute;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            opacity: 0.7;
            animation: bounce 2s infinite;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes bounce {
            0%, 100% { transform: translateX(-50%) translateY(0); }
            50% { transform: translateX(-50%) translateY(-10px); }
        }

        /* Respect reduced motion preference */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
</head>
<body>
    <section class="hero">
        <div class="hero__bg" id="bg"></div>
        <div class="hero__content">
            <h1 class="hero__title">Modern Design</h1>
            <p class="hero__subtitle">Performance meets beauty in every pixel</p>
            <a href="#content" class="hero__cta">Explore</a>
        </div>
        <div class="scroll-indicator">
            <span>↓ Scroll</span>
        </div>
    </section>

    <section id="content" style="padding: 4rem 2rem; text-align: center;">
        <h2>Your content here</h2>
    </section>
</body>
</html>'''
    },

    'card': {
        'name': 'Interactive Card Grid',
        'description': 'Responsive card grid with hover effects',
        'html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Card Grid</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f7fa;
            padding: 4rem 2rem;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 2rem;
        }

        .card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        }

        .card__image {
            width: 100%;
            aspect-ratio: 16 / 9;
            object-fit: cover;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .card__content {
            padding: 1.5rem;
        }

        .card__title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: #1a1a1a;
        }

        .card__description {
            color: #666;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .card__link {
            display: inline-flex;
            align-items: center;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            transition: transform 0.2s;
        }

        .card__link:hover {
            transform: translateX(4px);
        }

        /* Accessibility */
        .card:focus-within {
            outline: 3px solid #667eea;
            outline-offset: 2px;
        }

        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="margin-bottom: 3rem; font-size: 2.5rem;">Featured Content</h1>

        <div class="card-grid">
            <article class="card">
                <img class="card__image" src="" alt="Card image" aria-hidden="true">
                <div class="card__content">
                    <h2 class="card__title">Card Title 1</h2>
                    <p class="card__description">
                        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                        Sed do eiusmod tempor incididunt ut labore.
                    </p>
                    <a href="#" class="card__link">
                        Learn more →
                    </a>
                </div>
            </article>

            <article class="card">
                <img class="card__image" src="" alt="Card image" aria-hidden="true">
                <div class="card__content">
                    <h2 class="card__title">Card Title 2</h2>
                    <p class="card__description">
                        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                        Sed do eiusmod tempor incididunt ut labore.
                    </p>
                    <a href="#" class="card__link">
                        Learn more →
                    </a>
                </div>
            </article>

            <article class="card">
                <img class="card__image" src="" alt="Card image" aria-hidden="true">
                <div class="card__content">
                    <h2 class="card__title">Card Title 3</h2>
                    <p class="card__description">
                        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                        Sed do eiusmod tempor incididunt ut labore.
                    </p>
                    <a href="#" class="card__link">
                        Learn more →
                    </a>
                </div>
            </article>
        </div>
    </div>
</body>
</html>'''
    },

    'navigation': {
        'name': 'Responsive Navigation',
        'description': 'Mobile-friendly navigation with hamburger menu',
        'html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Navigation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            z-index: 100;
        }

        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        .nav__logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #667eea;
            text-decoration: none;
        }

        .nav__toggle {
            display: none;
            background: none;
            border: none;
            cursor: pointer;
            padding: 0.5rem;
        }

        .nav__toggle span {
            display: block;
            width: 25px;
            height: 3px;
            background: #333;
            margin: 5px 0;
            transition: transform 0.3s, opacity 0.3s;
        }

        .nav__toggle.active span:nth-child(1) {
            transform: translateY(8px) rotate(45deg);
        }

        .nav__toggle.active span:nth-child(2) {
            opacity: 0;
        }

        .nav__toggle.active span:nth-child(3) {
            transform: translateY(-8px) rotate(-45deg);
        }

        .nav__menu {
            display: flex;
            list-style: none;
            gap: 2rem;
        }

        .nav__link {
            color: #333;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }

        .nav__link:hover {
            color: #667eea;
        }

        .nav__link:focus-visible {
            outline: 3px solid #667eea;
            outline-offset: 4px;
            border-radius: 4px;
        }

        @media (max-width: 768px) {
            .nav__toggle {
                display: block;
            }

            .nav__menu {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                flex-direction: column;
                background: white;
                padding: 1rem;
                gap: 0;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                transform: translateY(-100%);
                opacity: 0;
                pointer-events: none;
                transition: transform 0.3s, opacity 0.3s;
            }

            .nav__menu.active {
                transform: translateY(0);
                opacity: 1;
                pointer-events: all;
            }

            .nav__menu li {
                border-bottom: 1px solid #eee;
            }

            .nav__menu li:last-child {
                border-bottom: none;
            }

            .nav__link {
                display: block;
                padding: 1rem;
            }
        }

        .main {
            margin-top: 80px;
            padding: 4rem 2rem;
        }

        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <nav class="nav" role="navigation" aria-label="Main">
            <a href="#" class="nav__logo">Logo</a>

            <button class="nav__toggle" aria-label="Toggle navigation" aria-expanded="false">
                <span></span>
                <span></span>
                <span></span>
            </button>

            <ul class="nav__menu" id="navMenu">
                <li><a href="#" class="nav__link">Home</a></li>
                <li><a href="#" class="nav__link">About</a></li>
                <li><a href="#" class="nav__link">Services</a></li>
                <li><a href="#" class="nav__link">Contact</a></li>
            </ul>
        </nav>
    </header>

    <main class="main">
        <h1>Main Content</h1>
        <p>Your content goes here...</p>
    </main>

    <script>
        const toggle = document.querySelector('.nav__toggle');
        const menu = document.querySelector('.nav__menu');

        toggle.addEventListener('click', () => {
            const isExpanded = toggle.getAttribute('aria-expanded') === 'true';

            toggle.classList.toggle('active');
            menu.classList.toggle('active');
            toggle.setAttribute('aria-expanded', !isExpanded);
        });

        // Close menu on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && menu.classList.contains('active')) {
                toggle.classList.remove('active');
                menu.classList.remove('active');
                toggle.setAttribute('aria-expanded', 'false');
                toggle.focus();
            }
        });
    </script>
</body>
</html>'''
    },

    'form': {
        'name': 'Accessible Form',
        'description': 'Form with validation and accessibility features',
        'html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Form</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f7fa;
            padding: 4rem 2rem;
        }

        .form-container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        h1 {
            margin-bottom: 2rem;
            color: #1a1a1a;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #333;
        }

        .required {
            color: #ef4444;
            margin-left: 0.25rem;
        }

        input, textarea {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 1rem;
            font-family: inherit;
            transition: border-color 0.2s;
        }

        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        input[aria-invalid="true"], textarea[aria-invalid="true"] {
            border-color: #ef4444;
        }

        .help-text {
            font-size: 0.875rem;
            color: #666;
            margin-top: 0.25rem;
        }

        .error-message {
            color: #ef4444;
            font-size: 0.875rem;
            margin-top: 0.25rem;
            display: none;
        }

        .error-message.visible {
            display: block;
        }

        .success-message {
            color: #10b981;
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }

        button {
            background: #667eea;
            color: white;
            padding: 0.875rem 2rem;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s, transform 0.2s;
            min-height: 44px;
        }

        button:hover {
            background: #5568d3;
            transform: translateY(-1px);
        }

        button:active {
            transform: translateY(0);
        }

        button:focus-visible {
            outline: 3px solid #667eea;
            outline-offset: 2px;
        }

        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h1>Contact Us</h1>

        <form id="contactForm" novalidate>
            <div class="form-group">
                <label for="name">
                    Full Name
                    <abbr class="required" title="required" aria-label="required">*</abbr>
                </label>
                <input
                    type="text"
                    id="name"
                    name="name"
                    required
                    aria-required="true"
                    aria-describedby="name-error"
                >
                <div id="name-error" class="error-message" role="alert">
                    Please enter your name
                </div>
            </div>

            <div class="form-group">
                <label for="email">
                    Email Address
                    <abbr class="required" title="required" aria-label="required">*</abbr>
                </label>
                <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    aria-required="true"
                    aria-describedby="email-help email-error"
                >
                <p id="email-help" class="help-text">
                    We'll never share your email
                </p>
                <div id="email-error" class="error-message" role="alert">
                    Please enter a valid email address
                </div>
            </div>

            <div class="form-group">
                <label for="message">
                    Message
                    <abbr class="required" title="required" aria-label="required">*</abbr>
                </label>
                <textarea
                    id="message"
                    name="message"
                    rows="5"
                    required
                    aria-required="true"
                    aria-describedby="message-error"
                ></textarea>
                <div id="message-error" class="error-message" role="alert">
                    Please enter a message
                </div>
            </div>

            <button type="submit">Send Message</button>
        </form>
    </div>

    <script>
        const form = document.getElementById('contactForm');

        form.addEventListener('submit', (e) => {
            e.preventDefault();

            let isValid = true;

            // Validate name
            const name = document.getElementById('name');
            const nameError = document.getElementById('name-error');
            if (!name.value.trim()) {
                nameError.classList.add('visible');
                name.setAttribute('aria-invalid', 'true');
                isValid = false;
            } else {
                nameError.classList.remove('visible');
                name.setAttribute('aria-invalid', 'false');
            }

            // Validate email
            const email = document.getElementById('email');
            const emailError = document.getElementById('email-error');
            const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
            if (!emailRegex.test(email.value)) {
                emailError.classList.add('visible');
                email.setAttribute('aria-invalid', 'true');
                isValid = false;
            } else {
                emailError.classList.remove('visible');
                email.setAttribute('aria-invalid', 'false');
            }

            // Validate message
            const message = document.getElementById('message');
            const messageError = document.getElementById('message-error');
            if (!message.value.trim()) {
                messageError.classList.add('visible');
                message.setAttribute('aria-invalid', 'true');
                isValid = false;
            } else {
                messageError.classList.remove('visible');
                message.setAttribute('aria-invalid', 'false');
            }

            if (isValid) {
                alert('Form submitted successfully!');
                form.reset();
            } else {
                // Focus first invalid field
                const firstInvalid = form.querySelector('[aria-invalid="true"]');
                if (firstInvalid) firstInvalid.focus();
            }
        });

        // Real-time validation
        ['name', 'email', 'message'].forEach(id => {
            const field = document.getElementById(id);
            field.addEventListener('blur', () => {
                // Trigger validation on blur
                form.dispatchEvent(new Event('submit'));
            });
        });
    </script>
</body>
</html>'''
    }
}


def list_patterns():
    """List all available patterns."""
    print("\nAvailable patterns:\n")
    for key, pattern in PATTERNS.items():
        print(f"  {key:<15} - {pattern['name']}")
        print(f"  {'':<15}   {pattern['description']}\n")


def generate_pattern(pattern_key, output_file=None):
    """Generate pattern code."""
    if pattern_key not in PATTERNS:
        print(f"Error: Pattern '{pattern_key}' not found.")
        print("\nRun './pattern_generator.py --list' to see available patterns.")
        sys.exit(1)

    pattern = PATTERNS[pattern_key]
    code = pattern['html']

    if output_file:
        output_path = Path(output_file)
        output_path.write_text(code)
        print(f"✅ Generated '{pattern['name']}' pattern")
        print(f"   Saved to: {output_path}")
    else:
        print(f"\n{'='*60}")
        print(f"{pattern['name']}")
        print(f"{'='*60}\n")
        print(code)


def interactive_mode():
    """Interactive pattern generation."""
    print("\n" + "="*60)
    print("Modern Web Design Pattern Generator")
    print("="*60)

    list_patterns()

    pattern_key = input("Select a pattern (or 'q' to quit): ").strip().lower()

    if pattern_key == 'q':
        print("Goodbye!")
        sys.exit(0)

    if pattern_key not in PATTERNS:
        print(f"Error: '{pattern_key}' is not a valid pattern.")
        sys.exit(1)

    save = input("\nSave to file? (y/n): ").strip().lower()

    if save == 'y':
        filename = input("Enter filename (e.g., hero.html): ").strip()
        if not filename:
            filename = f"{pattern_key}.html"
        generate_pattern(pattern_key, filename)
    else:
        generate_pattern(pattern_key)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate modern web design pattern boilerplate'
    )
    parser.add_argument(
        '--pattern',
        type=str,
        help='Pattern to generate (hero, card, navigation, form)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available patterns'
    )

    args = parser.parse_args()

    if args.list:
        list_patterns()
        sys.exit(0)

    if args.pattern:
        generate_pattern(args.pattern, args.output)
    else:
        interactive_mode()


if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/modern-web-design/skills/modern-web-design/assets/README.md =====

# Modern Web Design Assets

## Overview

This directory contains design system templates, starter files, and reusable assets for modern web development. All assets follow accessibility, performance, and modern design best practices.

## Available Assets

### 1. Design Tokens

**Location**: Would be in `tokens/` subdirectory

**What's included**:
- CSS custom properties (variables) for:
  - Colors (OKLCH color space, AAA compliant)
  - Typography scales (fluid sizing with clamp())
  - Spacing scales (consistent rhythm)
  - Shadows (elevation system)
  - Border radius (consistent rounding)
  - Animation timing (duration & easing)

**Usage**:
```css
/* Import design tokens */
@import url('tokens/colors.css');
@import url('tokens/typography.css');
@import url('tokens/spacing.css');

/* Use in your styles */
.button {
  background: var(--color-primary);
  padding: var(--space-md) var(--space-lg);
  font-size: var(--font-size-base);
  transition: transform var(--duration-fast) var(--ease-out);
}
```

### 2. Component Library

**Location**: Would be in `components/` subdirectory

**What's included**:
- Button variants (primary, secondary, ghost, danger)
- Form components (inputs, textareas, select, checkbox, radio)
- Card layouts
- Navigation components
- Modal/Dialog components
- Toast notifications
- Loading states (spinners, skeletons, progress bars)

**Features**:
- Fully accessible (WCAG AAA where possible)
- Keyboard navigable
- Screen reader friendly
- Dark mode variants
- Responsive by default

### 3. Layout Templates

**Location**: Would be in `layouts/` subdirectory

**What's included**:
- Landing page template
- Portfolio/Agency template
- Blog/Article template
- Dashboard/App template
- E-commerce template

**Features**:
- Modern CSS Grid & Flexbox
- Responsive breakpoints
- Print stylesheets
- Semantic HTML5

### 4. Animation Presets

**Location**: Would be in `animations/` subdirectory

**What's included**:
- CSS keyframe animations
- Transition presets
- Easing functions
- GSAP animation snippets
- Framer Motion variants

**Categories**:
- Fade (in/out, up/down/left/right)
- Slide (all directions)
- Scale (grow/shrink)
- Rotate
- Bounce
- Elastic
- Custom easings

### 5. Icon System

**Location**: Would be in `icons/` subdirectory

**What's included**:
- SVG icon set (inline-ready)
- Icon sprite sheet
- Icon font (optional)

**Features**:
- Accessibility ready (proper aria-hidden/labels)
- Consistent sizing
- Color customizable via CSS

### 6. Utility Classes

**Location**: Would be in `utilities/` subdirectory

**What's included**:
- Display utilities (flex, grid, block, inline, none)
- Spacing utilities (margin, padding)
- Typography utilities (size, weight, align)
- Color utilities (text, background)
- Layout utilities (container, aspect-ratio)
- Accessibility utilities (sr-only, focus-visible)

**Example**:
```html
<div class="flex items-center gap-md p-lg bg-primary text-white rounded-lg">
  Content
</div>
```

### 7. Reset & Base Styles

**Location**: Would be in `base/` subdirectory

**What's included**:
- Modern CSS reset (based on modern-normalize)
- Base typography styles
- Accessible focus styles
- Print styles

---

## How to Use These Assets

### Option 1: Copy Individual Files

Copy only the files you need into your project:

```bash
# Copy design tokens
cp assets/tokens/colors.css src/styles/
cp assets/tokens/typography.css src/styles/

# Copy specific components
cp assets/components/button.css src/components/
```

### Option 2: Import Everything

Import the complete design system:

```html
<link rel="stylesheet" href="assets/design-system.css">
```

Or in your CSS:

```css
@import url('../assets/design-system.css');
```

### Option 3: Use as Reference

Browse the assets to understand patterns and adapt them to your own design system.

---

## Customization Guide

### Colors

Modify color tokens to match your brand:

```css
:root {
  /* Update these values */
  --color-primary: oklch(50% 0.2 250); /* Your brand blue */
  --color-accent: oklch(65% 0.25 30);  /* Your accent color */

  /* System will generate variants automatically */
  --color-primary-hover: oklch(45% 0.2 250);
  --color-primary-active: oklch(40% 0.2 250);
}
```

### Typography

Adjust type scale for your design:

```css
:root {
  /* Base size (1rem = 16px by default) */
  --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);

  /* Adjust ratio for scale */
  --font-scale-ratio: 1.25; /* Minor third */

  /* Or use pre-calculated values */
  --font-size-sm: clamp(0.875rem, ...);
  --font-size-lg: clamp(1.25rem, ...);
}
```

### Spacing

Customize spacing scale:

```css
:root {
  /* 8px base unit */
  --space-unit: 0.5rem;

  /* Scale multiples */
  --space-xs: calc(var(--space-unit) * 1);  /* 8px */
  --space-sm: calc(var(--space-unit) * 2);  /* 16px */
  --space-md: calc(var(--space-unit) * 4);  /* 32px */
  --space-lg: calc(var(--space-unit) * 6);  /* 48px */
  --space-xl: calc(var(--space-unit) * 8);  /* 64px */
}
```

---

## Design System Principles

### 1. Mobile-First

All components are designed mobile-first with progressive enhancement for larger screens.

```css
/* Mobile first */
.component {
  font-size: 1rem;
}

/* Enhance for larger screens */
@media (min-width: 768px) {
  .component {
    font-size: 1.25rem;
  }
}
```

### 2. Accessibility First

- AAA color contrast ratios where possible (7:1)
- Keyboard navigable (visible focus states)
- Screen reader friendly (proper ARIA labels)
- Respects motion preferences

### 3. Performance Optimized

- CSS-only animations where possible
- GPU-accelerated transforms
- Minimal JavaScript
- Lazy-loadable components

### 4. Design Token Driven

Everything is configurable via design tokens:
- Easy rebranding
- Consistent visual language
- Dark mode support built-in

---

## File Structure

```
assets/
├── README.md (this file)
├── tokens/
│   ├── colors.css
│   ├── typography.css
│   ├── spacing.css
│   ├── shadows.css
│   └── animation.css
├── base/
│   ├── reset.css
│   ├── typography.css
│   └── print.css
├── components/
│   ├── button.css
│   ├── card.css
│   ├── form.css
│   ├── modal.css
│   └── ...
├── layouts/
│   ├── landing.html
│   ├── dashboard.html
│   └── ...
├── animations/
│   ├── fade.css
│   ├── slide.css
│   └── gsap-presets.js
├── utilities/
│   └── utilities.css
└── design-system.css (imports all)
```

---

## Browser Support

**Modern Browsers** (recommended):
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

**Fallbacks provided for**:
- CSS Grid → Flexbox
- CSS custom properties → Fallback values
- Modern CSS functions → Static values

**Progressive Enhancement**:
```css
/* Fallback */
.container {
  padding: 2rem; /* Static value */
}

/* Enhanced */
@supports (padding: clamp(1rem, 5vw, 3rem)) {
  .container {
    padding: clamp(1rem, 5vw, 3rem);
  }
}
```

---

## Contributing

When adding new assets:

1. **Follow naming conventions**: kebab-case for files, BEM for CSS classes
2. **Include accessibility**: ARIA labels, keyboard support, focus states
3. **Document usage**: Add examples and notes in component files
4. **Test thoroughly**: Cross-browser, keyboard, screen reader
5. **Optimize**: Remove unused code, minimize file size

---

## Related Skills

For implementation guidance, reference:
- `gsap-scrolltrigger` - Animation patterns
- `motion-framer` - React component animations
- `animated-component-libraries` - Pre-built components
- `threejs-webgl` - 3D backgrounds and effects

---

## License

All assets follow the Apache 2.0 license (same as the skill).

---

*Last updated: 2024*

