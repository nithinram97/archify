# Design Skills for Gemini, part 6: index, guides and integration

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

## Index of all skills (they are in parts 1-5)

| Skill | Use it for |
|---|---|
| `aframe-webxr` | Declarative web framework for building browser-based 3D, VR, and AR experiences using HTML and entity-component architecture. Use this skill when creating WebXR applications, VR experiences, AR experiences, 360-degree media viewers, or immersive web content with minimal JavaScript. Triggers on tasks involving A-Frame, WebXR, VR development, AR development, entity-component-system, declarative 3D, or HTML-based 3D scenes. Built on Three.js with accessible HTML-first approach. |
| `animated-component-libraries` | Pre-built animated React component collections combining Magic UI (150+ TypeScript/Tailwind/Motion components) and React Bits (90+ minimal-dependency animated components). Use this skill when building landing pages, marketing sites, dashboards, or interactive UIs requiring pre-made animated components instead of hand-crafting animations. Triggers on tasks involving animated UI components, Magic UI, React Bits, shadcn/ui integration, Tailwind CSS components, or component library selection. Alternative to manually implementing animations with Framer Motion or GSAP. |
| `animejs` | Versatile JavaScript animation engine for DOM, CSS, SVG, and JavaScript objects. Use when creating timeline-based animations, stagger effects, SVG morphing, keyframe sequences, or complex choreographed animations. Triggers on tasks involving Anime.js, timeline animations, staggered sequences, SVG path animations, morphing, or multi-step animation choreography. Alternative to GSAP for SVG-heavy animations and React-independent projects. |
| `babylonjs-engine` | Comprehensive skill for Babylon.js 3D web rendering engine. Use this skill when building real-time 3D experiences, browser-based games, interactive visualizations, or immersive web applications. Triggers on tasks involving Babylon.js, 3D scenes, WebGL/WebGPU rendering, entity-component systems, physics simulations, PBR materials, shadow mapping, or 3D model loading. Alternative to Three.js with built-in editor integration and game engine features. |
| `barba-js` | Page transitions library for creating fluid, smooth transitions between website pages. Use this skill when implementing page transitions, creating SPA-like experiences, adding animated route changes, or building websites with smooth navigation. Triggers on tasks involving Barba.js, page transitions, routing, view management, transition hooks, GSAP integration, or smooth page navigation. Works with gsap-scrolltrigger for transition animations. |
| `blender-web-pipeline` | Blender to web export workflows for 3D models and animations. Use this skill when exporting Blender models to glTF for web, optimizing 3D assets for Three.js or Babylon.js, batch processing models with Python scripts, automating Blender workflows, or creating web-ready 3D pipelines. Triggers on tasks involving Blender glTF export, bpy scripting, 3D asset optimization, model compression, texture baking, or Blender automation. Exports models for threejs-webgl, react-three-fiber, and babylonjs-engine skills. |
| `gsap-scrolltrigger` | Comprehensive skill for GSAP (GreenSock Animation Platform) and ScrollTrigger plugin. Use this skill when creating web animations, scroll-driven experiences, timelines, tweens, scroll-triggered animations, pinning, scrubbing, parallax effects, or animating DOM elements, SVG, Canvas, WebGL, or Three.js. Triggers on tasks involving GSAP, ScrollTrigger, smooth animations, scroll effects, or animation sequencing. |
| `lightweight-3d-effects` | Lightweight 3D effects for decorative elements and micro-interactions using Zdog, Vanta.js, and Vanilla-Tilt.js. Use this skill when adding pseudo-3D illustrations, animated backgrounds, parallax tilt effects, decorative 3D elements, or subtle depth effects without heavy frameworks. Triggers on tasks involving Zdog pseudo-3D, Vanta.js backgrounds, Vanilla-Tilt parallax, card tilt effects, hero section animations, or lightweight landing page visuals. Ideal for performance-focused designs. |
| `locomotive-scroll` | Comprehensive skill for Locomotive Scroll smooth scrolling library with parallax effects, viewport detection, and scroll-driven animations. Use this skill when implementing smooth scrolling experiences, creating parallax effects, building scroll-triggered animations, or developing immersive scrolling websites. Triggers on tasks involving Locomotive Scroll, smooth scrolling, parallax, scroll detection, scroll events, sticky elements, horizontal scrolling, or GSAP ScrollTrigger integration. Integrates with GSAP for advanced scroll-driven animations. |
| `lottie-animations` | After Effects animation rendering for web and React applications. Use this skill when implementing Lottie animations, JSON vector animations, interactive animated icons, micro-interactions, or loading animations. Triggers on tasks involving Lottie, lottie-web, lottie-react, dotLottie, After Effects JSON export, bodymovin, animated SVG alternatives, or designer-created animations. Complements GSAP ScrollTrigger and Framer Motion for scroll-driven and interactive animations. |
| `modern-web-design` | Modern web design trends, principles, and implementation patterns for 2024-2025. Use this skill when designing websites, creating interactive experiences, implementing design systems, ensuring accessibility, or building performance-first interfaces. Triggers on tasks involving modern design trends, micro-interactions, scrollytelling, bold minimalism, cursor UX, glassmorphism, accessibility compliance, performance optimization, or design system architecture. References animation skills (GSAP, Framer Motion, React Spring), 3D skills (Three.js, R3F, Babylon.js), and component libraries for implementation guidance. |
| `motion-framer` | Modern animation library for React and JavaScript. Create smooth, production-ready animations with motion components, variants, gestures (hover/tap/drag), layout animations, AnimatePresence exit animations, spring physics, and scroll-based effects. Use when building interactive UI components, micro-interactions, page transitions, or complex animation sequences. |
| `pixijs-2d` | Fast, lightweight 2D rendering engine for creating interactive graphics, particle effects, and canvas-based applications using WebGL/WebGPU. Use this skill when building 2D games, particle systems, interactive canvases, sprite animations, or UI overlays on 3D scenes. Triggers on tasks involving PixiJS, 2D rendering, sprite sheets, particle effects, filters, or high-performance canvas graphics. Alternative to Canvas2D with WebGL acceleration for rendering thousands of sprites at 60 FPS. |
| `playcanvas-engine` | Lightweight WebGL/WebGPU game engine with entity-component architecture and visual editor integration. Use this skill when building browser-based games, interactive 3D applications, or performance-critical web experiences. Triggers on tasks involving PlayCanvas, entity-component systems, game engine development, WebGL games, 3D browser applications, editor-first workflows, or real-time 3D rendering. Alternative to Three.js with game-specific features and integrated development environment. |
| `react-spring-physics` | Physics-based animation library combining React Spring (spring dynamics, gesture integration, 60fps animations) and Popmotion (low-level composable animation utilities, reactive streams). Use when building fluid, natural-feeling UI animations, gesture-driven interfaces, physics simulations, or spring-loaded interactions. Triggers on tasks involving React Spring hooks, spring physics, inertia scrolling, physics-based motion, animation composition, or natural UI movements. Alternative physics approach to motion-framer for more physically accurate animations. |
| `react-three-fiber` | Build declarative 3D scenes with React Three Fiber (R3F) - a React renderer for Three.js. Use when building interactive 3D experiences in React applications with component-based architecture, state management, and reusable abstractions. Ideal for product configurators, portfolios, games, data visualization, and immersive web experiences. |
| `rive-interactive` | State machine-based vector animation with runtime interactivity and web integration. Use this skill when creating interactive animations, state-driven UI, animated components with logic, or designer-created animations with runtime control. Triggers on tasks involving Rive, state machines, interactive vector animations, animation with input handling, ViewModel data binding, or React Rive integration. Alternative to Lottie for animations requiring state machines and two-way interactivity. |
| `scroll-reveal-libraries` | Simple scroll-triggered reveal animations using AOS (Animate On Scroll). Use this skill when building marketing pages, landing pages, or content-heavy sites requiring basic fade/slide effects without complex animation orchestration. Triggers on tasks involving scroll animations, scroll-triggered reveals, AOS, simple animations, or basic scroll effects. Alternative to GSAP ScrollTrigger and Locomotive Scroll for simpler use cases. Compare with motion-framer for React-specific animations. |
| `spline-interactive` | Browser-based 3D design tool with visual editor, animation, and web export. Use this skill when creating 3D scenes without code, designing interactive web experiences, prototyping 3D UI, exporting to React/web, or building designer-friendly 3D content. Triggers on tasks involving Spline, no-code 3D, visual 3D editor, 3D animation, state-based interactions, React Spline integration, or scene export. Alternative to Three.js for designers who prefer visual tools over code. |
| `substance-3d-texturing` | Comprehensive skill for Adobe Substance 3D Painter texturing and material creation workflow. Use this skill when creating PBR materials, exporting textures for web/game engines, optimizing 3D assets for real-time rendering, or automating texture workflows. Triggers on tasks involving Substance 3D Painter, PBR texturing, material creation, texture export for Three.js, Babylon.js, Unity, Unreal, glTF optimization, or Python API automation. Creates optimized textures for threejs-webgl, react-three-fiber, and babylonjs-engine materials. |
| `threejs-webgl` | Comprehensive skill for Three.js 3D web development. Use this skill when building interactive 3D scenes, WebGL/WebGPU applications, product configurators, 3D visualizations, or immersive web experiences. Triggers on tasks involving Three.js, 3D rendering, scenes, cameras, meshes, materials, lights, animations, textures, or WebGL/WebGPU rendering. |
| `web3d-integration-patterns` | Meta-skill for combining Three.js, GSAP ScrollTrigger, React Three Fiber, Motion, and React Spring for complex 3D web experiences. Use when building applications that integrate multiple 3D and animation libraries, requiring architecture patterns, state management, and performance optimization across the stack. Triggers on tasks involving library integration, multi-library architectures, scroll-driven 3D experiences, physics-based 3D animations, or complex interactive 3D applications. |


# Guides and integration agents


===== FILE: README.md =====

# Gemini Design Skillstack

**Professional design agency skillstack for 3D/WebGL, animation, and modern web development**

Gemini Code plugin marketplace providing comprehensive coverage of modern web technologies including Three.js, GSAP, React Three Fiber, Framer Motion, Babylon.js, and more.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Plugins: 27](https://img.shields.io/badge/Plugins-27-blue.svg)](#available-plugins)
[![Skills: 22](https://img.shields.io/badge/Skills-22-green.svg)](#available-skills)
[![Status: Production](https://img.shields.io/badge/Status-Production-brightgreen.svg)](#status)

## 🚀 Quick Start (Plugin Marketplace)

**New**: Install skills as plugins directly from this marketplace!

```bash
# Add marketplace to Gemini Code
/plugin marketplace add freshtechbro/geminidesignskills

# Install individual plugins
/plugin install threejs-webgl
/plugin install gsap-scrolltrigger
/plugin install react-three-fiber

# Or install complete bundles
/plugin install core-3d-animation        # 5 skills: Three.js, GSAP, R3F, Motion, Babylon
/plugin install extended-3d-scroll       # 6 skills: A-Frame, Vanta, PlayCanvas, PixiJS, Locomotive, Barba
/plugin install animation-components     # 5 skills: React Spring, Magic UI, AOS, Anime.js, Lottie
/plugin install authoring-motion         # 4 skills: Blender, Spline, Rive, Substance 3D
/plugin install meta-skills             # 2 skills: Integration patterns, Modern design
```

**Each plugin includes**:
- ✅ Complete skill content with SKILL.md
- ✅ 1-3 slash commands for quick actions
- ✅ 1-2 specialized agents for domain expertise
- ✅ Scripts, references, and asset templates

📚 **[View complete marketplace documentation →](MARKETPLACE.md)**

## Overview

**27 plugins (22 individual + 5 bundles)** extending Gemini Code with specialized knowledge for cutting-edge web technologies.

**Key Features**:
- 🏪 Plugin marketplace with 27 ready-to-install plugins
- ✅ 22 individual skills + 5 category bundles
- 🔧 50+ slash commands for instant boilerplate generation
- 🤖 27+ specialized agents for domain expertise
- 📚 Comprehensive patterns, examples, and integration guides
- 🚀 Auto-activates when Gemini detects relevant tasks

## What are Gemini Skills?

Modular packages that teach Gemini specific technologies. Each contains:
- **SKILL.md** - Instructions and patterns
- **references/** - API docs and guides
- **scripts/** - Automation utilities
- **assets/** - Templates and examples

Progressive disclosure: Gemini loads only what's needed per task.

## Available Plugins

### Individual Plugins (22)

All plugins include slash commands and specialized agents. [Full details →](MARKETPLACE.md)

### Category Bundles (5)

- **core-3d-animation** - Three.js, GSAP, R3F, Motion, Babylon.js (5 skills, 9 commands, 6 agents)
- **extended-3d-scroll** - A-Frame, Vanta, PlayCanvas, PixiJS, Locomotive, Barba (6 skills, 12 commands, 7 agents)
- **animation-components** - React Spring, Magic UI, AOS, Anime.js, Lottie (5 skills, 10 commands, 6 agents)
- **authoring-motion** - Blender, Spline, Rive, Substance 3D (4 skills, 10 commands, 5 agents)
- **meta-skills** - Integration patterns, Modern design (2 skills, 4 commands, 3 agents)

## Available Skills

### Core 3D & Animation (5)
**threejs-webgl** • **gsap-scrolltrigger** • **react-three-fiber** • **motion-framer** • **babylonjs-engine**

### Extended 3D & Scroll (6)
**aframe-webxr** • **lightweight-3d-effects** • **playcanvas-engine** • **pixijs-2d** • **locomotive-scroll** • **barba-js**

### Animation & Components (5)
**react-spring-physics** • **animated-component-libraries** • **scroll-reveal-libraries** • **animejs** • **lottie-animations**

### 3D Authoring & Motion (4)
**blender-web-pipeline** • **spline-interactive** • **rive-interactive** • **substance-3d-texturing**

### Meta-Skills (2)
**web3d-integration-patterns** • **modern-web-design**

## Installation

**Prerequisites**: Gemini Code CLI or [gemini.com/code](https://claude.com/code)

### Option 1: Plugin Marketplace (Recommended - New!)

Install directly from the marketplace:

```bash
# Add marketplace
/plugin marketplace add freshtechbro/geminidesignskills

# Browse and install plugins
/plugin install threejs-webgl
/plugin install core-3d-animation  # Bundle: 5 skills + commands + agents
```

**Benefits**:
- ✅ One-command installation
- ✅ Includes slash commands for quick actions
- ✅ Specialized agents for domain expertise
- ✅ Automatic updates when repo updates
- ✅ Individual plugins or category bundles

### Option 2: Upload to gemini.ai

Upload individual skills directly to [gemini.ai](https://claude.ai):

1. Go to **Settings > Features > Skills**
2. Click **Upload skill**
3. Select any `.zip` file from `.gemini/skills/`
4. Skill activates automatically when Gemini detects relevant tasks

**All skills are properly packaged** with:
- ✅ SKILL.md at root level with valid YAML frontmatter
- ✅ No nested zip files
- ✅ Correct directory structure for gemini.ai

### Option 3: Clone Repository (Development)

Clone for skill development or local customization:

```bash
git clone https://github.com/freshtechbro/claudedesignskills.git
cd geminidesignskills
```

Skills auto-activate when triggered. Example prompts:
- "Create a Three.js scene with PBR materials" → `threejs-webgl`
- "Add GSAP scroll animations" → `gsap-scrolltrigger`
- "Build React Three Fiber component with physics" → `react-three-fiber`

### Option 4: Individual Skills (Local Projects)

Copy individual skills to your project:

```bash
# Extract skill contents (not the zip itself)
unzip .gemini/skills/threejs-webgl.zip -d your-project/.gemini/skills/threejs-webgl/
```

## Creating Skills

```bash
# Initialize new skill
.gemini/skills/skill-creator/scripts/init_skill.py my-skill --path .gemini/skills

# Validate
.gemini/skills/skill-creator/scripts/quick_validate.py .gemini/skills/my-skill

# Package (auto-validates)
.gemini/skills/skill-creator/scripts/package_skill.py .gemini/skills/my-skill
```

### Packaging Requirements

All skills in this repository meet gemini.ai upload requirements:

**Required ZIP Structure**:
```
skill-name.zip
├── SKILL.md              ← Must be at root level!
├── references/
│   └── api_reference.md
├── scripts/
│   └── helper_script.py
└── assets/
    └── templates/
```

**Automatic Validation**:
- `package_skill.py` ensures correct structure
- Skips `.zip` files to prevent nesting
- Places SKILL.md at root level (not in subdirectory)
- Validates YAML frontmatter before packaging

**Common Errors** (all fixed in this repo):
- ❌ SKILL.md inside subdirectory (e.g., `skill-name/SKILL.md`)
- ❌ Nested .zip files inside archive
- ❌ Missing or invalid YAML frontmatter

## Generator Scripts

Each skill includes automation utilities. Examples:

- **threejs-webgl**: `setup_scene.py` - Three.js boilerplate
- **react-three-fiber**: `component_generator.py` - 12 R3F component types
- **motion-framer**: `animation_generator.py` - 11 animation types
- **babylonjs-engine**: `scene_generator.py` - 8 scene types, `mesh_builder.py` - 13 shapes
- **gsap-scrolltrigger**: `generate_animation.py`, `timeline_builder.py`

50+ generators total across all skills.

## Repository Verification

```bash
# Count skills (should be 23)
ls -d .gemini/skills/*/ | wc -l

# Count packages (should be 22)
find .gemini/skills -name "*.zip" -type f | wc -l

# Validate all
for skill in .gemini/skills/*/; do
  .gemini/skills/skill-creator/scripts/quick_validate.py "$skill"
done
```

## Skill Relationships

**Foundation**: `threejs-webgl` (used by R3F, A-Frame, Vanta) • `gsap-scrolltrigger` (integrates with most) • `motion-framer` (used by component libs)

**Alternatives**: 3D (`threejs-webgl` vs `babylonjs-engine` vs `playcanvas-engine`) • Animation (`gsap` vs `motion` vs `react-spring`) • Scroll (`locomotive` vs `AOS`)

**Common Integrations**: Three.js + GSAP • R3F + Motion • Vanta + GSAP

## Contributing

1. Fork repo
2. Create/improve skill using `init_skill.py`
3. Follow [Gemini Skills standards](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
4. Validate with `quick_validate.py`
5. Submit PR with packaged skill

**Guidelines**: Imperative form in SKILL.md • Runnable examples • Executable scripts (`chmod +x`) • Python 3 stdlib only • Proper YAML frontmatter

## Documentation

- **GEMINI.md** - Repository guidance for Gemini Code
- **Official Docs** - [Gemini Skills guidelines](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- **Individual Skills** - Each SKILL.md contains detailed instructions

## License

MIT License - see [LICENSE](LICENSE) file

## Status

✅ **Production Ready** - All 22 skills complete, validated, and packaged
🏪 **Plugin Marketplace** - 27 plugins (22 individual + 5 bundles) ready to install
📦 **22 Skills** - 3D graphics, animation, scroll effects, interactive web
🔧 **50+ Commands** - Slash commands for instant boilerplate
🤖 **27+ Agents** - Specialized domain experts
📚 **Fully Documented** - Guides, patterns, examples
🚀 **Upload Ready** - All skills meet gemini.ai packaging requirements

### Recent Updates

**2025-11-13**: Launched Plugin Marketplace
- ✅ Created 27 plugins (22 individual + 5 category bundles)
- ✅ Added 50+ slash commands for quick actions
- ✅ Created 27+ specialized agents for domain expertise
- ✅ Published marketplace.json for easy installation
- ✅ Full marketplace documentation in MARKETPLACE.md

**2025-10-25**: Fixed packaging script for gemini.ai compatibility
- ✅ Corrected ZIP structure (SKILL.md at root level)
- ✅ Removed nested .zip files
- ✅ All 22 skills re-packaged with correct structure
- ✅ Verified upload compatibility with gemini.ai

Built following [Anthropic's Gemini Skills guidelines](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview).

**Ready to use**: Upload any skill to [gemini.ai](https://claude.ai) or clone the repository!

---

**Star this repository** to stay updated with new skills and features!



===== FILE: MARKETPLACE.md =====

# Gemini Design Skillstack - Plugin Marketplace

**Professional design agency skillstack for 3D/WebGL, animation, and modern web development**

This repository serves as both a development workspace for skills and a plugin marketplace for Gemini Code, providing comprehensive coverage of modern web technologies including Three.js, GSAP, React Three Fiber, Framer Motion, Babylon.js, and more.

---

## 🚀 Quick Start

### Installing the Marketplace

Add this marketplace to your Gemini Code:

```bash
/plugin marketplace add freshtechbro/geminidesignskills
```

### Installing Individual Plugins

```bash
# Install a specific skill
/plugin install threejs-webgl
/plugin install gsap-scrolltrigger
/plugin install react-three-fiber
```

### Installing Category Bundles

```bash
# Install complete 3D & animation stack
/plugin install core-3d-animation

# Install extended 3D & scroll effects
/plugin install extended-3d-scroll

# Install animation & component libraries
/plugin install animation-components

# Install 3D authoring pipeline
/plugin install authoring-motion

# Install meta-skills (integration patterns & design)
/plugin install meta-skills
```

---

## 📦 Available Plugins

### Individual Plugins (22)

All individual plugins include:
- ✅ Complete skill content with SKILL.md
- ✅ 1-3 slash commands for quick actions
- ✅ 1-2 specialized agents for domain expertise
- ✅ Scripts, references, and asset templates

#### Core 3D & Animation (5 plugins)

1. **threejs-webgl** - Three.js WebGL/WebGPU 3D Graphics
   - Commands: `/threejs-webgl-setup_scene`
   - Agent: Three.js Architect
   - Use for: 3D scenes, WebGL rendering, interactive visualizations

2. **gsap-scrolltrigger** - GSAP Animation & ScrollTrigger
   - Commands: `/gsap-scrolltrigger-generate_animation`, `/gsap-scrolltrigger-timeline_builder`
   - Agent: GSAP ScrollTrigger Animation Choreographer
   - Use for: Scroll-driven animations, complex timelines, performance-optimized motion

3. **react-three-fiber** - React Three Fiber (R3F)
   - Commands: `/react-three-fiber-component_generator`, `/react-three-fiber-scene_setup`
   - Agent: React Three Fiber Architect
   - Use for: React + Three.js integration, declarative 3D, component-based 3D

4. **motion-framer** - Framer Motion
   - Commands: `/motion-framer-animation_generator`, `/motion-framer-variant_builder`
   - Agent: Framer Motion Animation Choreographer
   - Use for: React animations, gesture-driven UI, layout animations

5. **babylonjs-engine** - Babylon.js Game Engine
   - Commands: `/babylonjs-engine-scene_generator`, `/babylonjs-engine-mesh_builder`
   - Agent: Babylon.js Architect
   - Use for: Game development, physics simulations, advanced 3D rendering

#### Extended 3D & Scroll (6 plugins)

6. **aframe-webxr** - A-Frame WebXR
   - Commands: `/aframe-webxr-scene_generator`, `/aframe-webxr-component_builder`
   - Agent: A-Frame WebXR Architect
   - Use for: VR/AR experiences, WebXR applications, 360° media

7. **lightweight-3d-effects** - Zdog, Vanta.js, Vanilla Tilt
   - Commands: `/lightweight-3d-effects-generate_zdog`, `/lightweight-3d-effects-setup_vanta`
   - Agent: Lightweight 3D Effects Architect
   - Use for: Decorative 3D, animated backgrounds, subtle depth effects

8. **playcanvas-engine** - PlayCanvas Game Engine
   - Commands: `/playcanvas-engine-project_generator`, `/playcanvas-engine-component_builder`
   - Agent: PlayCanvas Architect
   - Use for: Browser-based games, real-time 3D apps, editor-first workflows

9. **pixijs-2d** - PixiJS 2D Rendering
   - Commands: `/pixijs-2d-sprite_generator`, `/pixijs-2d-particle_builder`
   - Agent: PixiJS 2D Architect
   - Use for: 2D games, particle effects, high-performance canvas graphics

10. **locomotive-scroll** - Locomotive Scroll
    - Commands: `/locomotive-scroll-generate_config`, `/locomotive-scroll-integration_helper`
    - Agent: Locomotive Scroll Specialist
    - Use for: Smooth scrolling, parallax effects, scroll detection

11. **barba-js** - Barba.js Page Transitions
    - Commands: `/barba-js-project_setup`, `/barba-js-transition_generator`
    - Agent: Barba.js Specialist
    - Use for: Page transitions, SPA-like experiences, routing animations

#### Animation & Components (5 plugins)

12. **react-spring-physics** - React Spring Physics
    - Commands: `/react-spring-physics-spring_generator`, `/react-spring-physics-physics_calculator`
    - Agent: React Spring Animation Choreographer
    - Use for: Physics-based animations, spring dynamics, natural motion

13. **animated-component-libraries** - Magic UI & React Bits
    - Commands: `/animated-component-libraries-component_importer`, `/animated-component-libraries-props_generator`
    - Agent: Animated Component Libraries Specialist
    - Use for: Pre-built animated components, landing pages, marketing sites

14. **scroll-reveal-libraries** - AOS (Animate On Scroll)
    - Commands: `/scroll-reveal-libraries-aos_generator`, `/scroll-reveal-libraries-config_builder`
    - Agent: Scroll Reveal Libraries Specialist
    - Use for: Scroll-triggered reveals, simple scroll animations

15. **animejs** - Anime.js
    - Commands: `/animejs-animation_generator`, `/animejs-timeline_builder`
    - Agent: Anime.js Animation Choreographer
    - Use for: Timeline animations, SVG morphing, stagger effects

16. **lottie-animations** - Lottie
    - Commands: `/lottie-animations-generate_lottie_component`, `/lottie-animations-optimize_lottie`
    - Agent: Lottie Animation Choreographer
    - Use for: After Effects animations, JSON vector animations, micro-interactions

#### 3D Authoring & Motion (4 plugins)

17. **blender-web-pipeline** - Blender Web Export Pipeline
    - Commands: `/blender-web-pipeline-batch_export`, `/blender-web-pipeline-optimize_model`, `/blender-web-pipeline-generate_lods`
    - Agent: Blender Web Pipeline Specialist
    - Use for: Blender → glTF export, 3D asset optimization, batch processing

18. **spline-interactive** - Spline 3D Design Tool
    - Commands: `/spline-interactive-project_generator`, `/spline-interactive-component_builder`
    - Agent: Spline Pipeline Specialist
    - Use for: No-code 3D design, visual 3D editor, designer-friendly workflows

19. **rive-interactive** - Rive Interactive Animations
    - Commands: `/rive-interactive-component_generator`, `/rive-interactive-viewmodel_builder`
    - Agent: Rive Interactive Animation Choreographer
    - Use for: State machine animations, interactive vector graphics, runtime control

20. **substance-3d-texturing** - Substance 3D Painter
    - Commands: `/substance-3d-texturing-batch_export`, `/substance-3d-texturing-web_optimizer`, `/substance-3d-texturing-generate_export_preset`
    - Agent: Substance 3D Pipeline Specialist
    - Use for: PBR texturing, material creation, texture optimization for web

#### Meta-Skills (2 plugins)

21. **web3d-integration-patterns** - Web3D Integration Patterns
    - Commands: `/web3d-integration-patterns-setup`, `/web3d-integration-patterns-help`
    - Agent: Web3D Integration Patterns Specialist
    - Use for: Multi-library integration, architecture patterns, complex 3D apps

22. **modern-web-design** - Modern Web Design Trends
    - Commands: `/modern-web-design-pattern_generator`, `/modern-web-design-design_audit`
    - Agent: Modern Web Design Specialist
    - Use for: Design trends, UX best practices, accessibility compliance

---

### Bundle Plugins (5)

Bundles combine multiple related skills with integrated commands and cross-skill agents.

1. **core-3d-animation** (5 skills, 9 commands, 6 agents)
   - Includes: threejs-webgl, gsap-scrolltrigger, react-three-fiber, motion-framer, babylonjs-engine
   - Use for: Complete 3D & animation development stack
   - Agent: Core 3D & Animation Integration Specialist

2. **extended-3d-scroll** (6 skills, 12 commands, 7 agents)
   - Includes: aframe-webxr, lightweight-3d-effects, playcanvas-engine, pixijs-2d, locomotive-scroll, barba-js
   - Use for: Extended 3D graphics and smooth scroll experiences
   - Agent: Extended 3D & Scroll Integration Specialist

3. **animation-components** (5 skills, 10 commands, 6 agents)
   - Includes: react-spring-physics, animated-component-libraries, scroll-reveal-libraries, animejs, lottie-animations
   - Use for: Comprehensive animation and UI component development
   - Agent: Animation & Components Integration Specialist

4. **authoring-motion** (4 skills, 10 commands, 5 agents)
   - Includes: blender-web-pipeline, spline-interactive, rive-interactive, substance-3d-texturing
   - Use for: Professional 3D authoring and motion graphics pipeline
   - Agent: 3D Authoring & Motion Integration Specialist

5. **meta-skills** (2 skills, 4 commands, 3 agents)
   - Includes: web3d-integration-patterns, modern-web-design
   - Use for: Integration patterns and modern design guidelines
   - Agent: Meta Skills Integration Specialist

---

## 🎯 Use Cases

### For 3D Developers
- **Three.js Projects**: Install `threejs-webgl` or `core-3d-animation` bundle
- **React + 3D**: Install `react-three-fiber` + `threejs-webgl`
- **Game Development**: Install `babylonjs-engine` or `playcanvas-engine`
- **WebXR/VR**: Install `aframe-webxr`

### For Animation Designers
- **Scroll Animations**: Install `gsap-scrolltrigger` or `locomotive-scroll`
- **React Animations**: Install `motion-framer` or `react-spring-physics`
- **Timeline Animations**: Install `animejs` or `gsap-scrolltrigger`
- **After Effects Integration**: Install `lottie-animations`

### For Full-Stack Agencies
- **Complete Stack**: Install `core-3d-animation` + `animation-components` bundles
- **Landing Pages**: Install `animated-component-libraries` + `gsap-scrolltrigger`
- **Product Configurators**: Install `threejs-webgl` + `react-three-fiber`

### For 3D Artists/Pipeline TDs
- **Blender → Web**: Install `blender-web-pipeline`
- **Texturing Pipeline**: Install `substance-3d-texturing`
- **No-Code 3D**: Install `spline-interactive`
- **Interactive Graphics**: Install `rive-interactive`

---

## 📚 Documentation

### Command Usage

All slash commands follow this pattern:

```bash
# Basic usage
/<plugin-name>-<command-name>

# Examples
/threejs-webgl-setup_scene
/gsap-scrolltrigger-generate_animation
/react-three-fiber-component_generator
```

### Agent Activation

Agents activate automatically based on task context. Examples:

- **"Help me build a Three.js scene"** → Activates threejs-webgl-architect
- **"Create GSAP scroll animation"** → Activates gsap-scrolltrigger-choreographer
- **"Optimize Blender model for web"** → Activates blender-web-pipeline-pipeline

### Skill References

Each plugin includes comprehensive references:
- API documentation
- Pattern libraries
- Integration guides
- Optimization checklists
- Troubleshooting guides

---

## 🛠️ Development

### Repository Structure

```
geminiskills/
├── .gemini/
│   ├── skills/              # Skill development workspace
│   └── plugins/             # Generated plugins
│       ├── individual/      # 22 individual plugins
│       └── bundles/         # 5 category bundles
├── .gemini-plugin/
│   └── marketplace.json     # Marketplace manifest
└── scripts/
    └── marketplace/         # Plugin generation scripts
        ├── generate_plugin.py
        ├── generate_bundle.py
        ├── generate_marketplace.py
        └── validate_marketplace.py
```

### Updating Plugins

To regenerate plugins after skill updates:

```bash
# Regenerate all individual plugins
./scripts/marketplace/generate_plugin.py --all

# Regenerate all bundles
./scripts/marketplace/generate_bundle.py --all

# Regenerate marketplace manifest
./scripts/marketplace/generate_marketplace.py

# Validate everything
./scripts/marketplace/validate_marketplace.py
```

---

## 📄 License

All plugins are licensed under Apache License 2.0.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branches
3. Submit pull requests
4. Follow existing skill patterns

---

## 🔗 Links

- **Repository**: https://github.com/freshtechbro/claudedesignskills
- **Issues**: https://github.com/freshtechbro/claudedesignskills/issues
- **Gemini Code Docs**: https://docs.claude.com/en/docs/claude-code/overview

---

## 📞 Support

For questions or issues:
- Open a GitHub issue
- Review the skill documentation in `.gemini/skills/`
- Check the Gemini Code documentation

---

**Built with ❤️ for the design and development community**



===== FILE: GEMINI.md =====

# GEMINI.md

This file provides guidance to Gemini Code (gemini.ai/code) when working with code in this repository.

## Instructions

Be concise and to the point. Sacrifice grammar and punctuation for clarity and conciseness.

## Repository Overview

This is a **dual-purpose repository**:
1. **Development Workspace** - Create and manage Gemini skills in `.gemini/skills/`
2. **Plugin Marketplace** - Distribute skills as plugins via `.gemini/plugins/` and `.gemini-plugin/marketplace.json`

Skills are modular, self-contained packages that extend Gemini's capabilities by providing specialized knowledge, workflows, and tools. Each skill acts as an "onboarding guide" for specific domains or tasks.

The repository focuses on creating comprehensive skills for a design agency's web development toolstack, particularly 3D/WebGL and animation technologies, then packaging them as plugins with slash commands and specialized agents.

## Official Documentation Reference

**IMPORTANT**: All skills in this repository MUST follow Gemini's official skill standards.

📚 **Official Gemini Skill Documentation**: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview

Key resources:
- Skill Overview: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- Creating Skills: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/creating-skills
- Skill Structure: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/skill-structure

When creating or modifying skills, **always consult the official documentation** to ensure compliance with the latest standards.

## Quick Reference

**Skill Development Workflows**:

```bash
# Create a new skill
.gemini/skills/skill-creator/scripts/init_skill.py my-new-skill --path .gemini/skills

# Validate a skill
.gemini/skills/skill-creator/scripts/quick_validate.py .gemini/skills/my-new-skill

# Package a skill (automatically validates first)
.gemini/skills/skill-creator/scripts/package_skill.py .gemini/skills/my-new-skill

# Validate all skills
for skill in .gemini/skills/*/; do
  .gemini/skills/skill-creator/scripts/quick_validate.py "$skill"
done

# Make a script executable (required after creating new scripts)
chmod +x .gemini/skills/my-skill/scripts/my_script.py
```

**Plugin Marketplace Workflows**:

```bash
# Generate individual plugin from skill
./scripts/marketplace/generate_plugin.py threejs-webgl

# Generate all individual plugins
./scripts/marketplace/generate_plugin.py --all

# Generate category bundle plugin
./scripts/marketplace/generate_bundle.py core-3d-animation

# Generate all bundles
./scripts/marketplace/generate_bundle.py --all

# Generate marketplace.json manifest
./scripts/marketplace/generate_marketplace.py

# Validate marketplace and all plugins
./scripts/marketplace/validate_marketplace.py
```

**User Installation Workflows**:

```bash
# Add marketplace to Gemini Code
/plugin marketplace add freshtechbro/geminidesignskills

# Install individual plugin
/plugin install threejs-webgl

# Install bundle plugin
/plugin install core-3d-animation
```

**Skill Activation**:
- Skills auto-activate when Gemini detects trigger keywords from the description
- Mention specific technologies: "Three.js", "GSAP", "React Three Fiber"
- Describe tasks: "create 3D scene", "scroll-driven animations", "physics-based motion"

## Repository Structure

```
geminiskills/
├── GEMINI.md                      # This file - repository guidance
├── MARKETPLACE.md                 # Plugin marketplace documentation
├── README.md                      # Public-facing documentation
│
├── .gemini/
│   ├── skills/                    # Skill development workspace
│   │   ├── skill-creator/         # Meta-skill for creating skills
│   │   ├── threejs-webgl/         # ✅ Complete (22 total)
│   │   ├── gsap-scrolltrigger/
│   │   └── ...                    # (20 more skills)
│   │
│   └── plugins/                   # Generated plugins for distribution
│       ├── individual/            # 22 individual skill plugins
│       │   ├── threejs-webgl/     # Each includes skills/, commands/, agents/
│       │   ├── gsap-scrolltrigger/
│       │   └── ...
│       │
│       └── bundles/               # 5 category bundle plugins
│           ├── core-3d-animation/
│           ├── extended-3d-scroll/
│           ├── animation-components/
│           ├── authoring-motion/
│           └── meta-skills/
│
├── .gemini-plugin/
│   └── marketplace.json           # Marketplace manifest (27 plugins)
│
└── scripts/
    ├── skill-creator/             # (existing skill scripts)
    └── marketplace/               # Marketplace automation
        ├── generate_plugin.py     # Convert skill → plugin
        ├── generate_bundle.py     # Create category bundles
        ├── generate_marketplace.py # Build marketplace.json
        └── validate_marketplace.py # Validate all plugins
```

**Each skill directory contains**:
- `SKILL.md` - Main instructions
- `scripts/` - Automation utilities
- `references/` - Documentation
- `assets/` - Templates and starter projects

**Each plugin directory contains**:
- `.gemini-plugin/plugin.json` - Plugin manifest
- `skills/<skill-name>/` - Skill content (copied from `.gemini/skills/`)
- `commands/` - Slash commands (1-3 per plugin)
- `agents/` - Specialized agents (1-2 per plugin)

## Current Repository State

**Skills**: 22/22 complete (100%) - All skills packaged and ready for distribution

**Plugins**: 27/27 complete (100%) - 22 individual + 5 bundles with commands and agents

**Marketplace**: ✅ Active - marketplace.json published

**All Skills Complete**:
- **Core 3D & Animation (5)**: threejs-webgl, gsap-scrolltrigger, react-three-fiber, motion-framer, babylonjs-engine
- **Extended 3D & Scroll (6)**: aframe-webxr, lightweight-3d-effects, playcanvas-engine, pixijs-2d, locomotive-scroll, barba-js
- **Animation & Components (5)**: react-spring-physics, animated-component-libraries, scroll-reveal-libraries, animejs, lottie-animations
- **3D Authoring & Motion (4)**: blender-web-pipeline, spline-interactive, rive-interactive, substance-3d-texturing
- **Meta-Skills (2)**: web3d-integration-patterns, modern-web-design

**All Plugins Complete**:
- **Individual (22)**: Each with 1-3 slash commands + 1-2 specialized agents
- **Bundles (5)**: core-3d-animation, extended-3d-scroll, animation-components, authoring-motion, meta-skills

Each skill directory contains SKILL.md, references/, scripts/, assets/, and a packaged .zip file.
Each plugin directory contains plugin.json manifest, skills/, commands/, and agents/.

## Common Commands

### Initialize a New Skill

```bash
.gemini/skills/skill-creator/scripts/init_skill.py <skill-name> --path .gemini/skills
```

Requirements:
- Skill name must be in hyphen-case (e.g., `my-new-skill`)
- Lowercase letters, digits, and hyphens only
- Maximum 40 characters
- Must match directory name exactly

This creates:
- `SKILL.md` with proper YAML frontmatter and TODO placeholders
- `scripts/` directory with example Python script
- `references/` directory with example reference documentation
- `assets/` directory with example asset placeholder

### Validate a Skill

```bash
.gemini/skills/skill-creator/scripts/quick_validate.py <path/to/skill>
```

Checks:
- SKILL.md exists
- Valid YAML frontmatter format
- Required fields present (name, description)
- Naming conventions followed
- No angle brackets in description

### Package a Skill

```bash
.gemini/skills/skill-creator/scripts/package_skill.py <path/to/skill> [output-directory]
```

Automatically validates before packaging. Creates a distributable zip file named `<skill-name>.zip`.

#### ZIP Structure Requirements

**CRITICAL**: Gemini.ai requires a specific ZIP structure for skill uploads:

**Required Structure** (correct):
```
skill-name.zip
├── SKILL.md              ← Must be at root level!
├── references/
│   └── api_reference.md
├── scripts/
│   └── helper_script.py
└── assets/
    └── templates/
```

**Common Errors** (will be rejected):
- ❌ SKILL.md inside subdirectory (e.g., `skill-name/SKILL.md`)
- ❌ Nested .zip files inside the archive
- ❌ Missing YAML frontmatter in SKILL.md

**How package_skill.py Ensures Correct Structure**:
1. **Root-level files**: Uses `relative_to(skill_path)` to place SKILL.md at root
2. **No nested zips**: Automatically skips .zip files during packaging
3. **Safe output location**: Outputs to parent directory by default to avoid nesting
4. **Validation first**: Runs validation before creating the zip file

**Upload Requirements** (from gemini.ai):
- ZIP file must include exactly one SKILL.md file at the root level
- SKILL.md must contain valid YAML frontmatter with `name` and `description`
- No nested zip files are allowed in the archive

### Python Script Requirements

**CRITICAL**: All Python scripts in skills MUST meet these standards:

#### 1. Shebang Line (MANDATORY)
Every Python script MUST start with:
```python
#!/usr/bin/env python3
```

**Why**: Allows scripts to be executed directly with `./script.py`

#### 2. Executable Permissions (MANDATORY)
All scripts MUST have executable permissions:
```bash
chmod +x script.py
```

**Verification**: Check with `ls -l script.py` - should show `-rwxr-xr-x`

**Common Error**: Forgetting to set executable permissions after creating scripts. Scripts will have `-rw-r--r--` permissions by default.

#### 3. Documentation (MANDATORY)
Every script MUST include:
- Module-level docstring describing purpose
- Usage examples in docstring or comments
- Argument descriptions if script accepts parameters

**Example**:
```python
#!/usr/bin/env python3
"""
Three.js Scene Setup Generator

Generates boilerplate Three.js scene code with customizable options.

Usage:
    ./setup_scene.py                    # Interactive mode
    ./setup_scene.py --renderer webgl   # CLI mode
"""
```

#### 4. Dependencies (REQUIRED)
- Use ONLY Python 3 standard library
- No external dependencies (no pip packages)
- Script must be self-contained and portable

#### 5. Execution Methods
Scripts should support both:
```bash
./script.py              # Direct execution (requires executable permissions)
python3 script.py        # Explicit Python invocation
```

#### 6. Quality Standards
- Single responsibility - one clear purpose per script
- Error handling with helpful messages
- Input validation
- Exit codes (0 for success, non-zero for errors)

### Common Script Execution Patterns

**Interactive Mode** (most scripts support this):
```bash
.gemini/skills/skill-creator/scripts/init_skill.py
# Script will prompt for required information
```

**CLI Mode** (with arguments):
```bash
.gemini/skills/skill-creator/scripts/init_skill.py my-skill --path .gemini/skills
```

**Validation Before Packaging**:
```bash
# Validate first (optional, but recommended during development)
.gemini/skills/skill-creator/scripts/quick_validate.py .gemini/skills/my-skill

# Package (automatically validates)
.gemini/skills/skill-creator/scripts/package_skill.py .gemini/skills/my-skill
```

### Available Skill-Specific Generators

Each completed skill includes custom generator scripts:

**threejs-webgl**:
- `setup_scene.py` - Generate Three.js scene boilerplate

**gsap-scrolltrigger**:
- `generate_animation.py` - Generate GSAP animation code
- `timeline_builder.py` - Build animation timeline sequences

**react-three-fiber**:
- `component_generator.py` - Generate R3F components (12 types)
- `scene_setup.py` - R3F scene setup with presets

**motion-framer**:
- `animation_generator.py` - Generate Motion component boilerplate (11 animation types)
- `variant_builder.py` - Build variant configurations (7 presets)

**babylonjs-engine**:
- `scene_generator.py` - Babylon scene boilerplate (8 scene types)
- `mesh_builder.py` - Mesh creation tool (13 shapes)

**aframe-webxr**:
- `scene_generator.py` - A-Frame scene boilerplate (7 scene types)
- `component_builder.py` - Custom component generator (7 component types)

**lightweight-3d-effects**:
- `generate_zdog.py` - Zdog illustration generator (6 illustration types)
- `setup_vanta.py` - Vanta.js background setup (11 effects)

These scripts can be referenced when creating similar generators for new skills.

## Official Gemini Skill Standards

### Critical Requirements

**EVERY skill MUST comply with these standards** (per Gemini's official documentation):

#### 1. YAML Frontmatter (MANDATORY)

Every `SKILL.md` file **MUST start** with YAML frontmatter:

```yaml
---
name: skill-name
description: What the skill does and when to use it
---
```

**Frontmatter Requirements**:
- Must be at the **very beginning** of SKILL.md (line 1)
- Must start with `---` and end with `---`
- Must contain exactly two required fields: `name` and `description`
- No optional fields are currently supported

#### 2. Name Field Requirements

The `name` field MUST:
- Match the directory name **exactly** (case-sensitive)
- Use hyphen-case (lowercase with hyphens): `my-skill-name`
- Contain only: lowercase letters (a-z), digits (0-9), and hyphens (-)
- Be between 1-40 characters
- Not contain spaces, underscores, or special characters
- Not start or end with a hyphen

**Examples**:
- ✅ Correct: `threejs-webgl`, `gsap-scrolltrigger`, `react-three-fiber`
- ❌ Wrong: `ThreeJS-WebGL` (uppercase), `three_js_webgl` (underscores), `three.js.webgl` (periods)

#### 3. Description Field Requirements

The `description` field MUST:
- Be **non-empty** (minimum 10 characters recommended)
- Be **maximum 1024 characters**
- **Not contain angle brackets** (`<` or `>`) - these cause validation errors
- Explain **WHAT the skill does** and **WHEN Gemini should use it**
- Use **third person** language (e.g., "This skill should be used when...")
- Include **clear trigger scenarios** so Gemini knows when to activate the skill

**Description Best Practices**:

1. **Start with what it does**:
   ```yaml
   description: Comprehensive skill for Three.js WebGL/WebGPU development...
   ```

2. **Include trigger scenarios**:
   ```yaml
   description: Use this skill when building 3D scenes, creating WebGL applications, implementing 3D visualizations...
   ```

3. **List specific keywords/technologies**:
   ```yaml
   description: Triggers on tasks involving Three.js, scene graphs, meshes, materials, lighting, animations, or WebGL rendering...
   ```

4. **Mention alternatives/comparisons**:
   ```yaml
   description: Alternative to Babylon.js with lighter footprint and more flexible architecture...
   ```

**Complete Example**:
```yaml
---
name: threejs-webgl
description: Comprehensive skill for Three.js WebGL/WebGPU 3D graphics development. Use this skill when building 3D scenes, creating interactive visualizations, implementing game graphics, or developing immersive web experiences. Triggers on tasks involving Three.js, scene graphs, geometries, meshes, materials, textures, lighting, cameras, animations, shaders, or WebGL/WebGPU rendering. Alternative to Babylon.js and PlayCanvas with more flexibility.
---
```

#### 4. Validation Requirements

**Before considering a skill complete**, it MUST:
- Pass `quick_validate.py` script without errors
- Have valid YAML frontmatter structure
- Have name matching directory name
- Have non-empty description
- Have no angle brackets in description
- Contain actual content after frontmatter

**How to Validate**:
```bash
.gemini/skills/skill-creator/scripts/quick_validate.py .gemini/skills/my-skill
```

**Expected output**: `Skill is valid!`

#### 5. Common Validation Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "SKILL.md not found" | File missing or wrong name | Create `SKILL.md` (exact name, case-sensitive) |
| "No YAML frontmatter found" | Missing `---` delimiters | Add YAML block at beginning of file |
| "Missing required field: name" | No `name:` field | Add `name: skill-name` to frontmatter |
| "Missing required field: description" | No `description:` field | Add `description: ...` to frontmatter |
| "Name mismatch" | `name` doesn't match directory | Change name to match directory exactly |
| "Invalid name format" | Contains invalid characters | Use only lowercase, digits, hyphens |
| "Angle brackets in description" | Description contains `<` or `>` | Remove or replace angle brackets |
| "Empty description" | Description field is blank | Add meaningful description with triggers |

### Recent Validation Audit Results

**Audit Date**: 2025 (Latest)

**Findings**: 4 out of 9 skills (44%) were **non-compliant** and missing YAML frontmatter entirely.

**Fixed Skills**:
- `babylonjs-engine` - Added proper YAML frontmatter ✅
- `aframe-webxr` - Added proper YAML frontmatter ✅
- `lightweight-3d-effects` - Added proper YAML frontmatter ✅
- `playcanvas-engine` - Added proper YAML frontmatter ✅

**Current Status**: 9/9 skills (100%) now compliant ✅

**Key Lesson**: The most common error is completely omitting YAML frontmatter. Skills with `## Description` markdown sections instead of YAML frontmatter will **not work** with Gemini's skill system.

## Skill Architecture

### Required Components

Every skill MUST have:
- **SKILL.md** - Main skill file with:
  - **YAML frontmatter** containing `name` and `description` (see "Official Gemini Skill Standards" above)
  - Markdown instructions in imperative/infinitive form (verb-first, not second person)

### Optional Components

Skills may include any combination of:

1. **scripts/** - Executable code (Python/Bash) for deterministic operations
   - Token efficient
   - May be executed without loading into context
   - Use when code is repeatedly rewritten or reliability is critical

2. **references/** - Documentation loaded into context as needed
   - API documentation, schemas, policies, detailed workflow guides
   - Loaded only when Gemini determines it's needed
   - For large files (>10k words), include grep search patterns in SKILL.md

3. **assets/** - Files used in output, not loaded into context
   - Templates, images, fonts, boilerplate code
   - Copied or modified in final output

### Progressive Disclosure System

Skills use three-level loading:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Gemini (unlimited for scripts)

## Skill Creation Workflow

When creating or editing skills, follow this process:

1. **Review Official Standards** - Read the "Official Gemini Skill Standards" section above and consult https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview

2. **Understand with Concrete Examples** - Gather real usage examples from official documentation

3. **Plan Reusable Contents** - Identify needed scripts/references/assets

4. **Fetch Documentation** - Use Context7 MCP to get latest library docs:
   - `mcp__context7__resolve-library-id` to find the library ID
   - `mcp__context7__get-library-docs` to retrieve documentation
   - If library not found, use `WebFetch` on official documentation

5. **Initialize** - Run `init_skill.py` for new skills (automatically creates proper YAML frontmatter)

6. **Write Description** - Craft description with:
   - What the skill does
   - When to use it (trigger scenarios)
   - Key technologies/keywords
   - Alternatives/comparisons
   - No angle brackets (`<` or `>`)
   - Max 1024 characters

7. **Edit Content** - Customize SKILL.md body and resources:
   - Use imperative/infinitive form (not second person)
   - Include core concepts, patterns, integrations, pitfalls
   - Delete unused example content
   - Keep SKILL.md focused, move details to references/

8. **Validate Early and Often** - Run validation after major changes:
   ```bash
   .gemini/skills/skill-creator/scripts/quick_validate.py .gemini/skills/my-skill
   ```

9. **Package** - Run `package_skill.py` to validate and create distributable zip:
   ```bash
   .gemini/skills/skill-creator/scripts/package_skill.py .gemini/skills/my-skill
   ```

10. **Iterate** - Test skill activation, improve based on real usage, re-validate

### Documentation Sources

When creating skills, always use the most current documentation:
- **Context7 MCP Server** - Primary source for library documentation (see commands above)
- **WebFetch** - For official documentation websites when Context7 doesn't have the library
- **Skill Creator** - Follow the guidance in `.gemini/skills/skill-creator/SKILL.md`

## Key Conventions

### Naming
- Skills: hyphen-case, lowercase only (e.g., `skill-creator`)
- Skill titles: Title Case in SKILL.md (e.g., "Skill Creator")
- Directory name must match YAML `name` field exactly

### Writing Style
- Use imperative/infinitive form throughout SKILL.md
- Write "To accomplish X, do Y" not "You should do X"
- Maintain objective, instructional language for AI consumption
- Avoid second person ("you") - Gemini is the consumer, not the end user

### YAML Frontmatter
- `name`: Must match directory name exactly (hyphen-case)
- `description`: Should explain WHAT the skill does and WHEN to use it
- Use third person (e.g., "This skill should be used when...")
- No angle brackets allowed (`<` or `>`)
- See "Official Gemini Skill Standards" section for complete requirements

### Avoid Duplication
- Information should live in either SKILL.md or references files, not both
- Prefer references files for detailed information
- Keep SKILL.md lean with only essential procedural instructions

## Skill Creation Best Practices

### 1. Writing Effective Descriptions

**Goal**: Help Gemini understand when to activate the skill.

**Formula**:
```
[What it does] + [When to use it] + [Trigger keywords] + [Alternatives/comparisons]
```

**Example**:
```yaml
description: Comprehensive skill for Three.js WebGL/WebGPU 3D graphics development. Use this skill when building 3D scenes, creating interactive visualizations, implementing game graphics, or developing immersive web experiences. Triggers on tasks involving Three.js, scene graphs, geometries, meshes, materials, textures, lighting, cameras, animations, shaders, or WebGL/WebGPU rendering. Alternative to Babylon.js and PlayCanvas with more flexibility.
```

### 2. Structuring SKILL.md Content

**Recommended sections** (in order):

1. **Overview** - Brief introduction (2-3 paragraphs)
2. **Core Concepts** - Fundamental concepts with code examples
3. **Common Patterns** - 5-7 real-world patterns with full implementations
4. **Integration Patterns** - How to use with other libraries/frameworks
5. **Performance Optimization** - Best practices and anti-patterns
6. **Common Pitfalls** - Issues developers face and solutions
7. **Resources** - Links to official docs, examples, communities
8. **Related Skills** - Cross-references to other skills in repository

### 3. Code Examples

**All code examples must**:
- Be complete and runnable
- Include imports/dependencies
- Show realistic use cases
- Include comments explaining key concepts
- Follow language/framework conventions

### 4. Validation Workflow

**Validate continuously during development**:

```bash
# After creating skill
.gemini/skills/skill-creator/scripts/init_skill.py my-skill

# After writing description
.gemini/skills/skill-creator/scripts/quick_validate.py .gemini/skills/my-skill

# After adding content
.gemini/skills/skill-creator/scripts/quick_validate.py .gemini/skills/my-skill

# Before marking complete
.gemini/skills/skill-creator/scripts/package_skill.py .gemini/skills/my-skill
```

### 5. Testing Skill Activation

**How to verify Gemini uses your skill**:

1. **Trigger words**: Include specific keywords from description in prompts
2. **Use cases**: Request tasks described in "when to use it" scenarios
3. **Technology names**: Mention the library/framework by name
4. **Check activation**: Gemini should reference the skill when responding

**Example**: For `threejs-webgl` skill:
- ✅ Trigger: "Help me create a Three.js scene with a rotating cube"
- ✅ Trigger: "I need to implement WebGL rendering for 3D visualization"
- ❌ Won't trigger: "Help me with 3D" (too vague, no specific keywords)

### 6. Maintaining Skills

**When updating skills**:

1. Update description if trigger scenarios change
2. Re-validate after any changes to frontmatter
3. Keep examples current with latest library versions
4. Add new patterns as they emerge
5. Document breaking changes in references/
6. Update related skills cross-references

### 7. Common Mistakes to Avoid

❌ **Don't**:
- Omit YAML frontmatter
- Write descriptions without trigger keywords
- Use second person ("you") in skill content
- Include angle brackets in descriptions
- Copy-paste content from other skills without customization
- Skip validation
- Create skills without consulting official Gemini docs
- **Forget to make scripts executable** (`chmod +x`)
- **Leave template files** (example.py, example_asset.txt) in production skills
- Create scripts with external dependencies

✅ **Do**:
- Always include proper YAML frontmatter
- Write comprehensive descriptions with clear triggers
- Use imperative/infinitive form
- Test skill activation with real prompts
- Validate early and often
- Follow official Gemini standards
- Cross-reference related skills
- **Set executable permissions on all scripts** immediately after creation
- **Remove template/example files** before marking skill complete
- Use only Python 3 standard library in scripts

## Skill Quality Standards

Each completed skill must include:

### SKILL.md Requirements
- Clear description with trigger scenarios (when to use)
- Core concepts with examples
- Common patterns (3-7 real-world examples)
- Integration patterns (with other skills/libraries)
- Performance best practices
- Common pitfalls and solutions
- Resource references (scripts/references/assets)

### References Requirements
- Detailed API documentation
- Advanced patterns and techniques
- Migration guides (if applicable)
- Troubleshooting guides

### Scripts Requirements
- Python/Bash automation utilities
- Boilerplate generators
- Validation/optimization tools
- All scripts executable and documented

### Assets Requirements
- Complete starter projects/templates
- Example implementations
- Configuration files
- Design system tokens (where applicable)

## Skill Relationships and Dependencies

Understanding skill relationships helps when creating integration patterns:

**Foundation Skills** (used by others):
- `threejs-webgl` → Used by react-three-fiber, aframe-webxr, lightweight-3d-effects (Vanta.js)
- `gsap-scrolltrigger` → Integrates with most animation and 3D skills
- `motion-framer` → Used by animated-component-libraries, integrates with R3F

**Alternative Skills** (similar use cases):
- 3D engines: `threejs-webgl` vs `babylonjs-engine` vs `playcanvas-engine`
- Animation: `gsap-scrolltrigger` vs `motion-framer` vs `react-spring-physics`
- Smooth scroll: `locomotive-scroll` vs `scroll-reveal-libraries`

**Integration Patterns**:
- Three.js + GSAP: Scroll-driven 3D animations
- React Three Fiber + Framer Motion: Interactive 3D UI components
- Vanta.js (uses Three.js) + GSAP: Animated backgrounds with scroll triggers

When creating a new skill, reference related skills in existing skill directories for integration examples.

## Development Workflow

When working on skills in this repository:

1. **Complete one skill at a time** - Finish all components (SKILL.md, references, scripts, assets) before moving to the next
2. **Validate frequently** - Run `quick_validate.py` after significant changes
3. **Package when complete** - Use `package_skill.py` to create distributable zip

## Repository Verification

To verify the integrity of the entire repository:

```bash
# Count total skills (should be 23 including skill-creator)
ls -d .gemini/skills/*/ | wc -l

# Verify all skills have SKILL.md
find .gemini/skills -name "SKILL.md" -type f | wc -l

# Verify all skills are packaged (should be 22, excluding skill-creator)
find .gemini/skills -name "*.zip" -type f | wc -l

# Validate all skills at once
for skill in .gemini/skills/*/; do
  skill_name=$(basename "$skill")
  echo "Validating $skill_name..."
  .gemini/skills/skill-creator/scripts/quick_validate.py "$skill" 2>&1 | grep -q "valid" && echo "✅ $skill_name" || echo "❌ $skill_name"
done

# Verify script permissions (all should be executable)
find .gemini/skills -name "*.py" -type f ! -perm -111 -print
# (No output means all scripts are executable)
```

## Troubleshooting

### Script Permission Issues

If a script is not executable:
```bash
chmod +x .gemini/skills/skill-creator/scripts/init_skill.py
```

### Validation Errors

**See "Official Gemini Skill Standards" section above for comprehensive validation error reference.**

Quick fixes for common issues:

1. **Missing YAML frontmatter** (MOST COMMON):
   - **Problem**: SKILL.md doesn't start with `---`
   - **Fix**: Add YAML frontmatter at the very beginning (line 1)
   - **Example**:
     ```yaml
     ---
     name: my-skill
     description: What the skill does and when to use it
     ---
     ```

2. **Name mismatch**:
   - **Problem**: `name:` field doesn't match directory name
   - **Fix**: Make name match directory exactly (hyphen-case, lowercase)

3. **Angle brackets in description**:
   - **Problem**: Description contains `<` or `>`
   - **Fix**: Remove or replace with words (e.g., `less than` instead of `<`)

4. **Empty description**:
   - **Problem**: Description field is blank or too short
   - **Fix**: Write comprehensive description with trigger scenarios (see standards above)

5. **Invalid name format**:
   - **Problem**: Name contains uppercase, underscores, periods, or spaces
   - **Fix**: Use only lowercase letters, digits, and hyphens

### Running Validation

**Always validate before considering a skill complete**:

```bash
# Validate single skill
.gemini/skills/skill-creator/scripts/quick_validate.py .gemini/skills/my-skill

# Validate all skills
for skill in .gemini/skills/*/; do
  echo "Validating $skill"
  .gemini/skills/skill-creator/scripts/quick_validate.py "$skill"
done
```

**Expected output**: `Skill is valid!`

### Context7 MCP Documentation Fetching

When creating skills for libraries:
1. First resolve the library ID: `mcp__context7__resolve-library-id` with library name
2. Then fetch documentation: `mcp__context7__get-library-docs` with the resolved ID
3. If library not found in Context7, use `WebFetch` on official documentation

### Skill Quality Checklist

Before marking a skill complete, ensure:

**Critical (Must Pass)**:
- [ ] ✅ **YAML frontmatter present** with `name` and `description` fields
- [ ] ✅ **Name matches directory name** exactly (hyphen-case)
- [ ] ✅ **Description is complete** with trigger scenarios (10-1024 chars)
- [ ] ✅ **No angle brackets** in description
- [ ] ✅ **All scripts are executable**: Run `ls -l scripts/*.py` - all should show `-rwxr-xr-x`
- [ ] ✅ **All scripts have shebang**: First line is `#!/usr/bin/env python3`
- [ ] ✅ **No template files remain**: No `example.py` or `example_asset.txt` files
- [ ] ✅ **Passes validation script**: `quick_validate.py` returns "Skill is valid!"
- [ ] ✅ **Packages successfully**: `package_skill.py` completes without errors

**Content Quality (Recommended)**:
- [ ] SKILL.md includes all required sections (overview, core concepts, common patterns, integration patterns, performance, pitfalls)
- [ ] All scripts include comprehensive documentation (docstrings with usage examples)
- [ ] Scripts handle errors gracefully with helpful messages
- [ ] References directory contains detailed API documentation
- [ ] Assets directory includes complete starter templates
- [ ] Documentation is current and accurate
- [ ] Examples are tested and working

**Repository Hygiene**:
- [ ] Related skills are cross-referenced
- [ ] Integration patterns documented

### Historical Issues

**2025 YAML Frontmatter Audit**:
- 44% of skills (4 out of 9) were missing YAML frontmatter entirely
- Skills had `## Description` markdown sections instead of YAML
- This caused skills to not be recognized by Gemini's system
- All skills have been fixed and now validate successfully

**2025 Script Executability Audit**:
- 100% of custom scripts (13 out of 13) were missing executable permissions
- Scripts had `-rw-r--r--` instead of `-rwxr-xr-x` permissions
- Users had to use `python3 script.py` instead of `./script.py`
- Template files (example.py, example_asset.txt) remained in 2 skills
- All issues fixed: scripts now executable, template files removed

**2025 Full Repository Completion**:
- All 22 skills now complete with SKILL.md, references/, scripts/, and assets/
- All skills validated and packaged as distributable .zip files
- Repository ready for production use

**Key Takeaways**:
1. YAML frontmatter is **not optional** - skills without it won't work
2. Scripts **must be executable** - set permissions immediately after creation
3. **Remove template files** before marking skills complete
4. **Verify all directories** (scripts, references, assets) have actual content

## License

All skills in this repository are licensed under Apache License 2.0.



===== FILE: plugins/bundles/animation-components/agents/animation-components-integration.md =====

# Animation & Components Integration Specialist

## Role

Expert integration specialist for combining Animation & Components technologies into cohesive applications.

## Expertise

- Cross-library integration patterns
- Technology stack orchestration
- Performance optimization across libraries
- Unified architecture design
- Best practices for combined workflows

## Bundle Contents

This bundle includes:
- react-spring-physics
- animated-component-libraries
- scroll-reveal-libraries
- animejs
- lottie-animations

## When to use

Activate this agent when working on:
- Projects using multiple libraries from this bundle
- Cross-library integration challenges
- Architecture decisions spanning multiple technologies
- Performance optimization across the stack
- Unified workflow design

## Approach

1. Understand project requirements across all technologies
2. Design cohesive architecture leveraging each library's strengths
3. Implement integration patterns proven for this stack
4. Optimize for overall system performance
5. Provide guidance on library coordination

## Tools

This agent has access to:
- All skills in the Animation & Components bundle
- Cross-library integration patterns
- Performance optimization techniques
- Architecture best practices



===== FILE: plugins/bundles/authoring-motion/agents/authoring-motion-integration.md =====

# 3D Authoring & Motion Integration Specialist

## Role

Expert integration specialist for combining 3D Authoring & Motion technologies into cohesive applications.

## Expertise

- Cross-library integration patterns
- Technology stack orchestration
- Performance optimization across libraries
- Unified architecture design
- Best practices for combined workflows

## Bundle Contents

This bundle includes:
- blender-web-pipeline
- spline-interactive
- rive-interactive
- substance-3d-texturing

## When to use

Activate this agent when working on:
- Projects using multiple libraries from this bundle
- Cross-library integration challenges
- Architecture decisions spanning multiple technologies
- Performance optimization across the stack
- Unified workflow design

## Approach

1. Understand project requirements across all technologies
2. Design cohesive architecture leveraging each library's strengths
3. Implement integration patterns proven for this stack
4. Optimize for overall system performance
5. Provide guidance on library coordination

## Tools

This agent has access to:
- All skills in the 3D Authoring & Motion bundle
- Cross-library integration patterns
- Performance optimization techniques
- Architecture best practices



===== FILE: plugins/bundles/core-3d-animation/agents/core-3d-animation-integration.md =====

# Core 3D & Animation Integration Specialist

## Role

Expert integration specialist for combining Core 3D & Animation technologies into cohesive applications.

## Expertise

- Cross-library integration patterns
- Technology stack orchestration
- Performance optimization across libraries
- Unified architecture design
- Best practices for combined workflows

## Bundle Contents

This bundle includes:
- threejs-webgl
- gsap-scrolltrigger
- react-three-fiber
- motion-framer
- babylonjs-engine

## When to use

Activate this agent when working on:
- Projects using multiple libraries from this bundle
- Cross-library integration challenges
- Architecture decisions spanning multiple technologies
- Performance optimization across the stack
- Unified workflow design

## Approach

1. Understand project requirements across all technologies
2. Design cohesive architecture leveraging each library's strengths
3. Implement integration patterns proven for this stack
4. Optimize for overall system performance
5. Provide guidance on library coordination

## Tools

This agent has access to:
- All skills in the Core 3D & Animation bundle
- Cross-library integration patterns
- Performance optimization techniques
- Architecture best practices



===== FILE: plugins/bundles/extended-3d-scroll/agents/extended-3d-scroll-integration.md =====

# Extended 3D & Scroll Integration Specialist

## Role

Expert integration specialist for combining Extended 3D & Scroll technologies into cohesive applications.

## Expertise

- Cross-library integration patterns
- Technology stack orchestration
- Performance optimization across libraries
- Unified architecture design
- Best practices for combined workflows

## Bundle Contents

This bundle includes:
- aframe-webxr
- lightweight-3d-effects
- playcanvas-engine
- pixijs-2d
- locomotive-scroll
- barba-js

## When to use

Activate this agent when working on:
- Projects using multiple libraries from this bundle
- Cross-library integration challenges
- Architecture decisions spanning multiple technologies
- Performance optimization across the stack
- Unified workflow design

## Approach

1. Understand project requirements across all technologies
2. Design cohesive architecture leveraging each library's strengths
3. Implement integration patterns proven for this stack
4. Optimize for overall system performance
5. Provide guidance on library coordination

## Tools

This agent has access to:
- All skills in the Extended 3D & Scroll bundle
- Cross-library integration patterns
- Performance optimization techniques
- Architecture best practices



===== FILE: plugins/bundles/meta-skills/agents/meta-skills-integration.md =====

# Meta Skills Integration Specialist

## Role

Expert integration specialist for combining Meta Skills technologies into cohesive applications.

## Expertise

- Cross-library integration patterns
- Technology stack orchestration
- Performance optimization across libraries
- Unified architecture design
- Best practices for combined workflows

## Bundle Contents

This bundle includes:
- web3d-integration-patterns
- modern-web-design

## When to use

Activate this agent when working on:
- Projects using multiple libraries from this bundle
- Cross-library integration challenges
- Architecture decisions spanning multiple technologies
- Performance optimization across the stack
- Unified workflow design

## Approach

1. Understand project requirements across all technologies
2. Design cohesive architecture leveraging each library's strengths
3. Implement integration patterns proven for this stack
4. Optimize for overall system performance
5. Provide guidance on library coordination

## Tools

This agent has access to:
- All skills in the Meta Skills bundle
- Cross-library integration patterns
- Performance optimization techniques
- Architecture best practices



# Licence (original notice, kept unchanged as the MIT licence requires)

```
MIT License

Copyright (c) 2025 Claude Skills Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```
