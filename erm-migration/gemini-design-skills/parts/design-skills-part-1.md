# Design Skills for Gemini, part 1 of 6: 3D engines

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
| `threejs-webgl` | Comprehensive skill for Three.js 3D web development. Use this skill when building interactive 3D scenes, WebGL/WebGPU applications, product configurators, 3D visualizations, or immersive web experiences. Triggers on tasks involving Three.js, 3D rendering, scenes, cameras, meshes, materials, lights, animations, textures, or WebGL/WebGPU rendering. |
| `react-three-fiber` | Build declarative 3D scenes with React Three Fiber (R3F) - a React renderer for Three.js. Use when building interactive 3D experiences in React applications with component-based architecture, state management, and reusable abstractions. Ideal for product configurators, portfolios, games, data visualization, and immersive web experiences. |
| `babylonjs-engine` | Comprehensive skill for Babylon.js 3D web rendering engine. Use this skill when building real-time 3D experiences, browser-based games, interactive visualizations, or immersive web applications. Triggers on tasks involving Babylon.js, 3D scenes, WebGL/WebGPU rendering, entity-component systems, physics simulations, PBR materials, shadow mapping, or 3D model loading. Alternative to Three.js with built-in editor integration and game engine features. |
| `playcanvas-engine` | Lightweight WebGL/WebGPU game engine with entity-component architecture and visual editor integration. Use this skill when building browser-based games, interactive 3D applications, or performance-critical web experiences. Triggers on tasks involving PlayCanvas, entity-component systems, game engine development, WebGL games, 3D browser applications, editor-first workflows, or real-time 3D rendering. Alternative to Three.js with game-specific features and integrated development environment. |
| `aframe-webxr` | Declarative web framework for building browser-based 3D, VR, and AR experiences using HTML and entity-component architecture. Use this skill when creating WebXR applications, VR experiences, AR experiences, 360-degree media viewers, or immersive web content with minimal JavaScript. Triggers on tasks involving A-Frame, WebXR, VR development, AR development, entity-component-system, declarative 3D, or HTML-based 3D scenes. Built on Three.js with accessible HTML-first approach. |


# Skill: threejs-webgl


===== FILE: plugins/individual/threejs-webgl/skills/threejs-webgl/SKILL.md =====

---
name: threejs-webgl
description: Comprehensive skill for Three.js 3D web development. Use this skill when building interactive 3D scenes, WebGL/WebGPU applications, product configurators, 3D visualizations, or immersive web experiences. Triggers on tasks involving Three.js, 3D rendering, scenes, cameras, meshes, materials, lights, animations, textures, or WebGL/WebGPU rendering.
---

# Three.js WebGL/WebGPU Development

## Overview

Three.js is the industry-standard JavaScript library for creating 3D graphics in web browsers using WebGL and WebGPU. This skill provides comprehensive guidance for building performant, interactive 3D experiences including scenes, cameras, renderers, geometries, materials, lights, textures, and animations.

## Core Concepts

### Scene Graph Architecture

Three.js uses a hierarchical scene graph where all 3D objects are organized in a tree structure:

```javascript
Scene
├── Camera
├── Lights
│   ├── AmbientLight
│   ├── DirectionalLight
│   └── PointLight
├── Meshes
│   ├── Mesh (Geometry + Material)
│   └── InstancedMesh
└── Groups
```

### Essential Components

Every Three.js application requires these core elements:

1. **Scene**: Container for all 3D objects
2. **Camera**: Defines the viewing perspective
3. **Renderer**: Draws the scene to canvas (WebGL or WebGPU)
4. **Geometry**: Defines the shape of objects
5. **Material**: Defines the surface appearance
6. **Mesh**: Combines geometry and material

## Quick Start Pattern

### Basic Scene Setup

```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// Scene, Camera, Renderer
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x333333);

const camera = new THREE.PerspectiveCamera(
  75, // FOV
  window.innerWidth / window.innerHeight, // Aspect ratio
  0.1, // Near clipping plane
  1000 // Far clipping plane
);
camera.position.set(0, 2, 5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 7.5);
directionalLight.castShadow = true;
scene.add(directionalLight);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Animation Loop
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

animate();

// Handle Resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

### WebGPU Setup (Modern Alternative)

```javascript
import * as THREE from 'three/webgpu';

const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setAnimationLoop(animate);
renderer.toneMapping = THREE.LinearToneMapping;
renderer.toneMappingExposure = 1;
document.body.appendChild(renderer.domElement);
```

## Common Patterns

### 1. Creating Meshes with Materials

```javascript
// Basic Mesh
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({
  color: 0x00ff00,
  roughness: 0.5,
  metalness: 0.5
});
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// Textured Mesh
const loader = new THREE.TextureLoader();
const texture = loader.load('texture.jpg');
texture.colorSpace = THREE.SRGBColorSpace;

const texturedMaterial = new THREE.MeshStandardMaterial({
  map: texture
});
const mesh = new THREE.Mesh(geometry, texturedMaterial);
scene.add(mesh);
```

### 2. Lighting Strategies

```javascript
// Three-Point Lighting Setup
function setupThreePointLight(scene) {
  // Key Light (Main)
  const keyLight = new THREE.DirectionalLight(0xffffff, 3);
  keyLight.position.set(5, 10, 7.5);
  keyLight.castShadow = true;
  scene.add(keyLight);

  // Fill Light (Softens shadows)
  const fillLight = new THREE.DirectionalLight(0xffffff, 1);
  fillLight.position.set(-5, 5, -5);
  scene.add(fillLight);

  // Rim Light (Edge definition)
  const rimLight = new THREE.DirectionalLight(0xffffff, 0.5);
  rimLight.position.set(0, 5, -10);
  scene.add(rimLight);

  // Ambient (Base illumination)
  const ambient = new THREE.AmbientLight(0x404040, 0.5);
  scene.add(ambient);
}

// Physical Light (Realistic)
const bulbLight = new THREE.PointLight(0xffee88, 1, 100, 2);
bulbLight.power = 1700; // Lumens (100W bulb equivalent)
bulbLight.castShadow = true;
scene.add(bulbLight);

// Hemisphere Light (Sky + Ground)
const hemiLight = new THREE.HemisphereLight(
  0xddeeff, // Sky color
  0x0f0e0d, // Ground color
  0.02
);
scene.add(hemiLight);
```

### 3. Instanced Geometry (Performance)

```javascript
// For rendering thousands of similar objects efficiently
const geometry = new THREE.SphereGeometry(0.1, 16, 16);
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const instancedMesh = new THREE.InstancedMesh(geometry, material, 1000);

const matrix = new THREE.Matrix4();
const color = new THREE.Color();

for (let i = 0; i < 1000; i++) {
  matrix.setPosition(
    Math.random() * 10 - 5,
    Math.random() * 10 - 5,
    Math.random() * 10 - 5
  );
  instancedMesh.setMatrixAt(i, matrix);
  instancedMesh.setColorAt(i, color.setHex(Math.random() * 0xffffff));
}

instancedMesh.instanceMatrix.needsUpdate = true;
scene.add(instancedMesh);
```

### 4. Loading 3D Models (glTF)

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

// Setup loaders
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/');

const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);

// Load model
gltfLoader.load('model.glb', (gltf) => {
  const model = gltf.scene;

  // Enable shadows
  model.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });

  scene.add(model);

  // Handle animations
  if (gltf.animations.length > 0) {
    const mixer = new THREE.AnimationMixer(model);
    const action = mixer.clipAction(gltf.animations[0]);
    action.play();

    // In animation loop:
    // mixer.update(deltaTime);
  }
});
```

### 5. Shadow Configuration

```javascript
// Enable shadows on renderer
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap; // or VSMShadowMap

// Configure light shadows
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
directionalLight.shadow.camera.near = 0.5;
directionalLight.shadow.camera.far = 50;
directionalLight.shadow.camera.left = -10;
directionalLight.shadow.camera.right = 10;
directionalLight.shadow.camera.top = 10;
directionalLight.shadow.camera.bottom = -10;
directionalLight.shadow.radius = 4;
directionalLight.shadow.blurSamples = 8;

// Objects casting/receiving shadows
mesh.castShadow = true;
mesh.receiveShadow = true;
```

### 6. Raycasting (Interaction)

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function onMouseClick(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(scene.children, true);

  if (intersects.length > 0) {
    const object = intersects[0].object;
    object.material.color.set(0xff0000);
  }
}

window.addEventListener('click', onMouseClick);
```

## Integration Patterns

### With GSAP for Animation

```javascript
import gsap from 'gsap';

// Animate camera
gsap.to(camera.position, {
  x: 5,
  y: 3,
  z: 10,
  duration: 2,
  ease: "power2.inOut",
  onUpdate: () => {
    camera.lookAt(scene.position);
  }
});

// Animate mesh properties
gsap.to(mesh.rotation, {
  y: Math.PI * 2,
  duration: 3,
  repeat: -1,
  ease: "none"
});
```

### With React (see react-three-fiber skill)

```javascript
// Three.js integrates naturally with React Three Fiber
// Use the react-three-fiber skill for React integration patterns
```

### With Post-Processing

```javascript
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const bloomPass = new UnrealBloomPass(
  new THREE.Vector2(window.innerWidth, window.innerHeight),
  1.5, // strength
  0.4, // radius
  0.85 // threshold
);
composer.addPass(bloomPass);

// In animation loop:
composer.render();
```

## Performance Optimization

### 1. Geometry Reuse
```javascript
// Bad: Creates new geometry for each mesh
for (let i = 0; i < 100; i++) {
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);
}

// Good: Reuse geometry
const sharedGeometry = new THREE.BoxGeometry(1, 1, 1);
for (let i = 0; i < 100; i++) {
  const mesh = new THREE.Mesh(sharedGeometry, material);
  scene.add(mesh);
}
```

### 2. Use InstancedMesh for Repeated Objects
For hundreds/thousands of identical objects, use `InstancedMesh` (see pattern above).

### 3. Texture Optimization
```javascript
// Compress textures
texture.generateMipmaps = true;
texture.minFilter = THREE.LinearMipmapLinearFilter;
texture.magFilter = THREE.LinearFilter;

// Use power-of-two dimensions (512, 1024, 2048)
// Consider texture atlases for multiple small textures
```

### 4. Level of Detail (LOD)
```javascript
const lod = new THREE.LOD();
lod.addLevel(highDetailMesh, 0);    // 0-50 units
lod.addLevel(mediumDetailMesh, 50);  // 50-100 units
lod.addLevel(lowDetailMesh, 100);    // 100+ units
scene.add(lod);
```

### 5. Frustum Culling
Three.js automatically culls objects outside the camera's view. Ensure objects have correct bounding spheres:

```javascript
mesh.geometry.computeBoundingSphere();
```

### 6. Dispose Resources
```javascript
function disposeScene() {
  scene.traverse((object) => {
    if (object.geometry) object.geometry.dispose();
    if (object.material) {
      if (Array.isArray(object.material)) {
        object.material.forEach(material => material.dispose());
      } else {
        object.material.dispose();
      }
    }
  });
  renderer.dispose();
}
```

## Best Practices

### 1. Use Animation Clocks for Consistent Timing
```javascript
const clock = new THREE.Clock();

function animate() {
  const deltaTime = clock.getDelta();
  const elapsedTime = clock.getElapsedTime();

  // Use deltaTime for frame-independent animations
  mesh.rotation.y += deltaTime * Math.PI * 0.5; // 90° per second

  renderer.render(scene, camera);
}
```

### 2. Camera Setup Guidelines
- **FOV**: 45-75° for most applications
- **Near plane**: As far as possible (avoid z-fighting)
- **Far plane**: As close as possible (precision)
- **Aspect ratio**: Always match canvas dimensions

### 3. Material Selection
- **MeshBasicMaterial**: Unlit, flat colors (debugging, UI)
- **MeshLambertMaterial**: Cheap diffuse lighting (mobile)
- **MeshPhongMaterial**: Specular highlights (older standard)
- **MeshStandardMaterial**: PBR, realistic (recommended)
- **MeshPhysicalMaterial**: Advanced PBR (clearcoat, transmission)

### 4. Coordinate System
- Three.js uses right-handed coordinate system
- +Y is up, +Z is toward camera, +X is right
- Rotations use radians (Math.PI = 180°)

### 5. Scene Organization
```javascript
// Group related objects
const building = new THREE.Group();
building.add(walls, roof, windows);
scene.add(building);

// Use meaningful names
mesh.name = 'player-character';
const found = scene.getObjectByName('player-character');
```

## Common Pitfalls

### 1. Not Updating Aspect Ratio on Resize
Always update camera aspect ratio and projection matrix when window resizes.

### 2. Creating New Objects in Animation Loop
```javascript
// Bad: Memory leak
function animate() {
  const geometry = new THREE.BoxGeometry(); // Created every frame!
  // ...
}

// Good: Create once outside loop
const geometry = new THREE.BoxGeometry();
function animate() {
  // Reuse geometry
}
```

### 3. Forgetting to Enable Shadows
Remember to enable shadows on renderer, lights, and objects.

### 4. Z-Fighting (Flickering)
- Increase near plane distance
- Decrease far plane distance
- Avoid overlapping coplanar surfaces
- Use `material.polygonOffset = true` with `material.polygonOffsetFactor`

### 5. Color Space Issues
```javascript
// Always set color space for textures
texture.colorSpace = THREE.SRGBColorSpace;

// Set renderer output encoding
renderer.outputColorSpace = THREE.SRGBColorSpace;
```

### 6. Not Disposing Resources
Always call `.dispose()` on geometries, materials, textures, and renderers when no longer needed.

## Resources

This skill includes bundled resources to accelerate Three.js development:

### references/
- `api_reference.md`: Quick API reference for core classes (Scene, Camera, Renderer, etc.)
- `materials_guide.md`: Comprehensive material types and properties
- `optimization_checklist.md`: Performance optimization strategies

### scripts/
- `setup_scene.py`: Generate boilerplate Three.js scene setup code
- `texture_optimizer.py`: Batch optimize textures for web (resize, compress)
- `gltf_validator.py`: Validate glTF models before use

### assets/
- `starter_scene/`: Complete HTML/JS boilerplate project
- `shaders/`: Custom GLSL shader examples (vertex, fragment)
- `hdri/`: Environment maps for PBR lighting
- `draco/`: DRACO decoder for compressed models

## Advanced Topics

### Custom Shaders (GLSL)
```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0.0 },
    uColor: { value: new THREE.Color(0x00ff00) }
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec3 uColor;
    varying vec2 vUv;
    void main() {
      gl_FragColor = vec4(uColor * vUv.x, 1.0);
    }
  `
});
```

### Render Targets (Render-to-Texture)
```javascript
const renderTarget = new THREE.WebGLRenderTarget(512, 512);

// Render scene to texture
renderer.setRenderTarget(renderTarget);
renderer.render(scene, camera);
renderer.setRenderTarget(null);

// Use texture
const material = new THREE.MeshBasicMaterial({
  map: renderTarget.texture
});
```

### GPU Computation (GPGPU)
Use `GPUComputationRenderer` for particle simulations, cloth physics, etc.

## When to Use This Skill

Use this skill when:
- Building interactive 3D web experiences
- Creating product configurators or visualizers
- Implementing WebGL/WebGPU rendering
- Working with 3D models, scenes, or animations
- Optimizing Three.js performance
- Integrating Three.js with other libraries (GSAP, React, etc.)
- Debugging Three.js rendering issues

For React integration, use the **react-three-fiber** skill.
For animation, combine with the **gsap-scrolltrigger** skill.
For UI animations, use the **motion-framer** skill.



===== FILE: plugins/individual/threejs-webgl/skills/threejs-webgl/references/api_reference.md =====

# Three.js API Quick Reference

## Core Classes

### Scene
```javascript
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x000000);
scene.fog = new THREE.Fog(0xffffff, 10, 100);
scene.add(object);
scene.remove(object);
scene.getObjectByName('name');
```

### Camera

#### PerspectiveCamera
```javascript
new THREE.PerspectiveCamera(fov, aspect, near, far);
camera.position.set(x, y, z);
camera.lookAt(target);
camera.updateProjectionMatrix(); // Call after changing properties
```

**Common FOVs:**
- 45° - Natural perspective
- 50° - Default for many apps
- 75° - Wide, immersive feel

#### OrthographicCamera
```javascript
new THREE.OrthographicCamera(left, right, top, bottom, near, far);
// Useful for 2D/isometric views
```

### Renderer

#### WebGLRenderer
```javascript
const renderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: true,
  powerPreference: "high-performance"
});
renderer.setSize(width, height);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
```

#### WebGPURenderer
```javascript
const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setAnimationLoop(animate);
```

## Geometry

### Built-in Geometries
```javascript
new THREE.BoxGeometry(width, height, depth);
new THREE.SphereGeometry(radius, widthSegments, heightSegments);
new THREE.PlaneGeometry(width, height);
new THREE.CylinderGeometry(radiusTop, radiusBottom, height, radialSegments);
new THREE.TorusGeometry(radius, tube, radialSegments, tubularSegments);
```

### BufferGeometry (Custom)
```javascript
const geometry = new THREE.BufferGeometry();
const vertices = new Float32Array([...]);
geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
geometry.computeVertexNormals();
geometry.computeBoundingSphere();
```

### Geometry Operations
```javascript
geometry.dispose(); // Free memory
geometry.center(); // Center geometry at origin
geometry.scale(x, y, z);
geometry.rotateX(angle);
geometry.translate(x, y, z);
```

## Materials

### Common Properties
```javascript
{
  color: 0xff0000,
  transparent: true,
  opacity: 0.5,
  side: THREE.DoubleSide, // FrontSide, BackSide, DoubleSide
  depthWrite: true,
  depthTest: true,
  wireframe: false
}
```

### Material Types
```javascript
new THREE.MeshBasicMaterial({}); // Unlit
new THREE.MeshLambertMaterial({}); // Simple diffuse
new THREE.MeshPhongMaterial({ shininess: 30 }); // Specular
new THREE.MeshStandardMaterial({ roughness: 0.5, metalness: 0.5 }); // PBR
new THREE.MeshPhysicalMaterial({ // Advanced PBR
  roughness: 0.0,
  metalness: 0.0,
  clearcoat: 1.0,
  clearcoatRoughness: 0.1,
  transmission: 1.0,
  ior: 1.5
});
```

## Lights

### AmbientLight
```javascript
new THREE.AmbientLight(0xffffff, 0.5);
// Illuminates all objects equally
```

### DirectionalLight
```javascript
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(5, 10, 7.5);
light.castShadow = true;
// Parallel rays (like sunlight)
```

### PointLight
```javascript
const light = new THREE.PointLight(0xffffff, 1, distance, decay);
light.castShadow = true;
// Radiates in all directions
```

### SpotLight
```javascript
const light = new THREE.SpotLight(0xffffff, 1, distance, angle, penumbra, decay);
light.target.position.set(x, y, z);
light.castShadow = true;
```

### HemisphereLight
```javascript
new THREE.HemisphereLight(skyColor, groundColor, intensity);
// Sky and ground hemisphere lighting
```

### Light Properties
```javascript
light.intensity = 1.0;
light.color.set(0xff0000);
light.power = 1700; // Lumens (for PointLight)
light.visible = false;
```

## Textures

### TextureLoader
```javascript
const loader = new THREE.TextureLoader();
const texture = loader.load('texture.jpg', onLoad, onProgress, onError);

texture.colorSpace = THREE.SRGBColorSpace;
texture.wrapS = THREE.RepeatWrapping;
texture.wrapT = THREE.RepeatWrapping;
texture.repeat.set(2, 2);
texture.offset.set(0.5, 0.5);
texture.rotation = Math.PI / 4;
texture.minFilter = THREE.LinearMipmapLinearFilter;
texture.magFilter = THREE.LinearFilter;
texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
```

### Texture Types
```javascript
material.map = diffuseTexture;
material.normalMap = normalTexture;
material.roughnessMap = roughnessTexture;
material.metalnessMap = metalnessTexture;
material.emissiveMap = emissiveTexture;
material.aoMap = aoTexture;
material.bumpMap = bumpTexture;
material.displacementMap = displacementTexture;
material.alphaMap = alphaTexture;
```

## Mesh

### Creation
```javascript
const mesh = new THREE.Mesh(geometry, material);
mesh.position.set(x, y, z);
mesh.rotation.set(x, y, z); // Radians
mesh.scale.set(x, y, z);
mesh.castShadow = true;
mesh.receiveShadow = true;
mesh.visible = true;
mesh.name = 'my-mesh';
```

### Transformations
```javascript
mesh.translateX(distance);
mesh.translateY(distance);
mesh.translateZ(distance);
mesh.rotateX(angle);
mesh.rotateY(angle);
mesh.rotateZ(angle);
mesh.lookAt(targetVector);
```

### Matrix Operations
```javascript
mesh.updateMatrix();
mesh.updateMatrixWorld(force);
mesh.applyMatrix4(matrix);
```

## Groups
```javascript
const group = new THREE.Group();
group.add(mesh1, mesh2, mesh3);
group.position.set(x, y, z);
scene.add(group);
```

## Animation

### AnimationMixer
```javascript
const mixer = new THREE.AnimationMixer(model);
const action = mixer.clipAction(gltf.animations[0]);
action.play();

// In animation loop:
const delta = clock.getDelta();
mixer.update(delta);
```

### AnimationAction Methods
```javascript
action.play();
action.stop();
action.pause();
action.reset();
action.setLoop(THREE.LoopRepeat, Infinity);
action.setDuration(seconds);
action.clampWhenFinished = true;
action.fadeIn(duration);
action.fadeOut(duration);
action.crossFadeTo(otherAction, duration);
```

## Loaders

### GLTFLoader
```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const loader = new GLTFLoader();
loader.load('model.glb', (gltf) => {
  scene.add(gltf.scene);
}, onProgress, onError);
```

### DRACOLoader
```javascript
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/');
gltfLoader.setDRACOLoader(dracoLoader);
```

### OBJLoader, FBXLoader
```javascript
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';
```

## Controls

### OrbitControls
```javascript
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 5;
controls.maxDistance = 50;
controls.maxPolarAngle = Math.PI / 2;
controls.target.set(0, 0, 0);
controls.update(); // Call in animation loop if damping enabled
```

### MapControls, TrackballControls, FlyControls
```javascript
import { MapControls } from 'three/addons/controls/MapControls.js';
import { TrackballControls } from 'three/addons/controls/TrackballControls.js';
import { FlyControls } from 'three/addons/controls/FlyControls.js';
```

## Raycaster
```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function onMouseMove(event) {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
}

raycaster.setFromCamera(mouse, camera);
const intersects = raycaster.intersectObjects(scene.children, true);

if (intersects.length > 0) {
  const object = intersects[0].object;
  const point = intersects[0].point; // Intersection point
  const face = intersects[0].face; // Intersected face
  const distance = intersects[0].distance;
}
```

## Math Utilities

### Vector3
```javascript
const v = new THREE.Vector3(x, y, z);
v.set(x, y, z);
v.add(otherVector);
v.sub(otherVector);
v.multiply(otherVector);
v.multiplyScalar(scalar);
v.normalize();
v.length();
v.distanceTo(otherVector);
v.lerp(otherVector, alpha);
v.cross(otherVector);
v.dot(otherVector);
```

### Quaternion
```javascript
const q = new THREE.Quaternion();
q.setFromEuler(euler);
q.setFromAxisAngle(axis, angle);
mesh.quaternion.copy(q);
```

### Clock
```javascript
const clock = new THREE.Clock();
const delta = clock.getDelta(); // Time since last call
const elapsed = clock.getElapsedTime(); // Total time
clock.start();
clock.stop();
```

## Post-Processing

### EffectComposer
```javascript
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.render();
```

### Common Passes
```javascript
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';
```

## Helpers

```javascript
new THREE.AxesHelper(size);
new THREE.GridHelper(size, divisions);
new THREE.CameraHelper(camera);
new THREE.DirectionalLightHelper(light, size);
new THREE.SpotLightHelper(light);
new THREE.BoxHelper(object, color);
```

## Constants

### Side
- `THREE.FrontSide` (default)
- `THREE.BackSide`
- `THREE.DoubleSide`

### Blending Modes
- `THREE.NormalBlending` (default)
- `THREE.AdditiveBlending`
- `THREE.SubtractiveBlending`
- `THREE.MultiplyBlending`

### Shadow Map Types
- `THREE.BasicShadowMap`
- `THREE.PCFShadowMap`
- `THREE.PCFSoftShadowMap`
- `THREE.VSMShadowMap`

### Tone Mapping
- `THREE.NoToneMapping`
- `THREE.LinearToneMapping`
- `THREE.ReinhardToneMapping`
- `THREE.CineonToneMapping`
- `THREE.ACESFilmicToneMapping`

### Color Spaces
- `THREE.SRGBColorSpace`
- `THREE.LinearSRGBColorSpace`

## Performance Tips

```javascript
// Dispose resources
geometry.dispose();
material.dispose();
texture.dispose();
renderer.dispose();

// Frustum culling (automatic)
mesh.frustumCulled = true;

// Matrix updates
mesh.matrixAutoUpdate = false; // Manual control
mesh.updateMatrix();

// Render on demand
function render() {
  renderer.render(scene, camera);
}
// Call render() only when needed

// Use InstancedMesh for repeated objects
const instancedMesh = new THREE.InstancedMesh(geometry, material, count);
```

## Common Gotchas

1. **Always update projection matrix after changing camera properties**
2. **Set texture.colorSpace = THREE.SRGBColorSpace for diffuse textures**
3. **Enable shadows on renderer, lights, and objects**
4. **Dispose geometries, materials, and textures to prevent memory leaks**
5. **Use Clock.getDelta() for frame-independent animations**
6. **Call controls.update() in animation loop if damping is enabled**



===== FILE: plugins/individual/threejs-webgl/skills/threejs-webgl/references/materials_guide.md =====

# Three.js Materials Comprehensive Guide

## Material Selection Decision Tree

```
Need lighting?
├─ NO → MeshBasicMaterial
└─ YES → Need PBR realism?
    ├─ NO → Need specular highlights?
    │   ├─ YES → MeshPhongMaterial
    │   └─ NO → MeshLambertMaterial
    └─ YES → Need advanced effects?
        ├─ YES → MeshPhysicalMaterial
        └─ NO → MeshStandardMaterial
```

## Material Comparison Table

| Material | Lighting | PBR | Performance | Use Case |
|----------|----------|-----|-------------|----------|
| MeshBasicMaterial | ✗ | ✗ | Excellent | UI, debugging, unlit scenes |
| MeshLambertMaterial | ✓ | ✗ | Very Good | Mobile, simple diffuse |
| MeshPhongMaterial | ✓ | ✗ | Good | Legacy, specular highlights |
| MeshStandardMaterial | ✓ | ✓ | Moderate | Most realistic scenes |
| MeshPhysicalMaterial | ✓ | ✓✓ | Lower | Advanced materials (glass, car paint) |
| MeshToonMaterial | ✓ | ✗ | Very Good | Cel-shaded / cartoon style |
| ShaderMaterial | Custom | Custom | Varies | Complete custom control |

## MeshBasicMaterial

**Use for:** UI elements, debugging, flat-colored objects, unlit scenes

```javascript
const material = new THREE.MeshBasicMaterial({
  color: 0xff0000,
  wireframe: false,
  transparent: false,
  opacity: 1.0,
  side: THREE.FrontSide,
  map: texture,
  alphaMap: alphaTexture,
  envMap: environmentMap,
  combine: THREE.MultiplyOperation, // For envMap
  reflectivity: 1.0,
  refractionRatio: 0.98
});
```

**Key Features:**
- No lighting calculations (fastest)
- Flat, unshaded appearance
- Always visible regardless of lights
- Good for backgrounds, UI, or stylized looks

**Performance:** ⭐⭐⭐⭐⭐

## MeshLambertMaterial

**Use for:** Mobile devices, simple diffuse surfaces, performance-critical scenes

```javascript
const material = new THREE.MeshLambertMaterial({
  color: 0xff0000,
  emissive: 0x000000,
  emissiveIntensity: 1.0,
  emissiveMap: null,
  map: texture,
  lightMap: lightMapTexture,
  lightMapIntensity: 1.0,
  aoMap: aoTexture,
  aoMapIntensity: 1.0
});
```

**Key Features:**
- Simple diffuse (matte) lighting
- No specular highlights
- Cheaper than Phong/Standard
- Good for organic, non-reflective surfaces

**Performance:** ⭐⭐⭐⭐

## MeshPhongMaterial

**Use for:** Legacy projects, objects with visible specular highlights

```javascript
const material = new THREE.MeshPhongMaterial({
  color: 0xff0000,
  specular: 0x111111,
  shininess: 30,
  emissive: 0x000000,
  emissiveIntensity: 1.0,
  map: texture,
  normalMap: normalTexture,
  normalScale: new THREE.Vector2(1, 1),
  bumpMap: bumpTexture,
  bumpScale: 1.0,
  specularMap: specTexture
});
```

**Key Features:**
- Diffuse + specular highlights
- Adjustable shininess
- Per-pixel lighting
- Legacy, prefer MeshStandardMaterial for new projects

**Performance:** ⭐⭐⭐

## MeshStandardMaterial (PBR)

**Use for:** Realistic materials, production-quality scenes, modern workflows

```javascript
const material = new THREE.MeshStandardMaterial({
  color: 0xffffff,
  roughness: 0.5, // 0 = mirror, 1 = matte
  metalness: 0.5, // 0 = dielectric, 1 = metal
  map: diffuseTexture,
  normalMap: normalTexture,
  normalScale: new THREE.Vector2(1, 1),
  roughnessMap: roughnessTexture,
  metalnessMap: metalnessTexture,
  aoMap: aoTexture,
  aoMapIntensity: 1.0,
  emissive: 0x000000,
  emissiveMap: emissiveTexture,
  emissiveIntensity: 1.0,
  envMap: environmentMap,
  envMapIntensity: 1.0,
  bumpMap: bumpTexture,
  bumpScale: 1.0,
  displacementMap: dispTexture,
  displacementScale: 1.0,
  displacementBias: 0.0,
  alphaMap: alphaTexture,
  flatShading: false
});
```

**Key Features:**
- Physically Based Rendering (PBR)
- Energy-conserving reflections
- Works with HDR environment maps
- Industry-standard workflow (glTF)

**Roughness Guide:**
- 0.0 - Perfect mirror (chrome, polished metal)
- 0.2 - Very glossy (wet surfaces, varnished wood)
- 0.5 - Moderate (painted metal, plastic)
- 0.8 - Matte (fabric, unpolished wood)
- 1.0 - Completely diffuse (clay, concrete)

**Metalness Guide:**
- 0.0 - Non-metal (wood, plastic, skin, fabric)
- 1.0 - Metal (gold, silver, copper, iron)
- Avoid values between 0-1 (physically incorrect)

**Performance:** ⭐⭐⭐

## MeshPhysicalMaterial (Advanced PBR)

**Use for:** Glass, car paint, clearcoat, transmission, iridescence

```javascript
const material = new THREE.MeshPhysicalMaterial({
  // All MeshStandardMaterial properties, plus:

  clearcoat: 1.0, // 0-1, adds glossy layer on top
  clearcoatRoughness: 0.1,
  clearcoatMap: clearcoatTexture,
  clearcoatRoughnessMap: clearcoatRoughnessTexture,
  clearcoatNormalMap: clearcoatNormalTexture,
  clearcoatNormalScale: new THREE.Vector2(1, 1),

  transmission: 1.0, // 0-1, for glass/transparency
  thickness: 1.0, // Subsurface thickness
  thicknessMap: thicknessTexture,

  ior: 1.5, // Index of refraction (glass ~1.5, water ~1.33, diamond ~2.4)

  sheen: 1.0, // Fabric-like sheen
  sheenRoughness: 0.5,
  sheenColor: new THREE.Color(0xffffff),

  iridescence: 1.0, // Soap bubble, oil slick effect
  iridescenceIOR: 1.3,
  iridescenceThicknessRange: [100, 400]
});
```

**Use Cases:**

### Glass
```javascript
{
  roughness: 0.0,
  metalness: 0.0,
  transmission: 1.0,
  thickness: 1.0,
  ior: 1.5
}
```

### Car Paint
```javascript
{
  roughness: 0.4,
  metalness: 0.8,
  clearcoat: 1.0,
  clearcoatRoughness: 0.1,
  color: 0xff0000
}
```

### Fabric (Velvet, Satin)
```javascript
{
  roughness: 0.8,
  metalness: 0.0,
  sheen: 1.0,
  sheenRoughness: 0.5,
  sheenColor: new THREE.Color(0xffffff)
}
```

### Soap Bubble
```javascript
{
  roughness: 0.0,
  metalness: 0.0,
  transmission: 1.0,
  thickness: 0.5,
  iridescence: 1.0,
  iridescenceIOR: 1.3
}
```

**Performance:** ⭐⭐

## MeshToonMaterial

**Use for:** Cel-shaded, cartoon, or stylized looks

```javascript
const material = new THREE.MeshToonMaterial({
  color: 0xff0000,
  map: texture,
  gradientMap: gradientTexture, // Controls toon shading steps
  emissive: 0x000000
});
```

**Key Features:**
- Discrete shading levels (cel-shaded)
- Stylized, non-realistic look
- Good performance

**Performance:** ⭐⭐⭐⭐

## Material Properties Deep Dive

### Common Properties (All Materials)

```javascript
{
  // Visibility
  visible: true,
  transparent: false,
  opacity: 1.0,
  alphaTest: 0.5, // Discard pixels below this alpha

  // Rendering
  side: THREE.FrontSide, // FrontSide, BackSide, DoubleSide
  depthTest: true,
  depthWrite: true,
  blending: THREE.NormalBlending,

  // Color
  color: 0xffffff,
  vertexColors: false,

  // Wireframe
  wireframe: false,
  wireframeLinewidth: 1, // Not all platforms support

  // Clipping
  clipShadows: false,
  clipIntersection: false,
  clippingPlanes: [],

  // Precision
  precision: "highp", // "lowp", "mediump", "highp"

  // Fog
  fog: true
}
```

### Texture Properties

```javascript
const texture = loader.load('texture.jpg');

// Color space (IMPORTANT!)
texture.colorSpace = THREE.SRGBColorSpace; // For diffuse/color maps
texture.colorSpace = THREE.LinearSRGBColorSpace; // For data maps (normal, roughness)

// Wrapping
texture.wrapS = THREE.RepeatWrapping; // ClampToEdgeWrapping, MirroredRepeatWrapping
texture.wrapT = THREE.RepeatWrapping;

// Repeat & Offset
texture.repeat.set(2, 2); // Tile 2x2
texture.offset.set(0.5, 0.5);
texture.rotation = Math.PI / 4;
texture.center.set(0.5, 0.5); // Rotation center

// Filtering
texture.minFilter = THREE.LinearMipmapLinearFilter; // Minification
texture.magFilter = THREE.LinearFilter; // Magnification
texture.anisotropy = renderer.capabilities.getMaxAnisotropy(); // Reduce blur at angles

// Mipmaps
texture.generateMipmaps = true;
```

### Texture Types & Color Spaces

| Texture Type | Color Space | Purpose |
|--------------|-------------|---------|
| map (diffuse) | SRGB | Base color |
| normalMap | Linear | Surface detail |
| roughnessMap | Linear | Surface roughness |
| metalnessMap | Linear | Metallic areas |
| aoMap | Linear | Ambient occlusion |
| emissiveMap | SRGB | Glow |
| bumpMap | Linear | Height data |
| displacementMap | Linear | Vertex displacement |
| alphaMap | Linear | Transparency mask |

## Material Optimization Tips

### 1. Texture Atlas
Combine multiple textures into one to reduce draw calls.

### 2. Share Materials
```javascript
// Good: Share material across meshes
const sharedMaterial = new THREE.MeshStandardMaterial({...});
const mesh1 = new THREE.Mesh(geo1, sharedMaterial);
const mesh2 = new THREE.Mesh(geo2, sharedMaterial);

// Bad: New material per mesh
const mesh1 = new THREE.Mesh(geo1, new THREE.MeshStandardMaterial({...}));
```

### 3. Texture Size
- Use power-of-two dimensions (512, 1024, 2048)
- Compress textures (JPEG for photos, PNG for alpha)
- Consider KTX2/Basis Universal for web

### 4. Disable Unnecessary Features
```javascript
material.needsUpdate = false; // After initial setup
renderer.shadowMap.autoUpdate = false; // If shadows don't change
```

### 5. Use InstancedMesh with Materials
For identical objects with the same material.

## Custom Shaders (ShaderMaterial)

**Use for:** Complete custom control, special effects, optimizations

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    uTime: { value: 0.0 },
    uColor: { value: new THREE.Color(0xff0000) },
    uTexture: { value: texture }
  },
  vertexShader: `
    uniform float uTime;
    varying vec2 vUv;
    varying vec3 vNormal;

    void main() {
      vUv = uv;
      vNormal = normal;

      vec3 pos = position;
      pos.z += sin(pos.x * 10.0 + uTime) * 0.1;

      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec3 uColor;
    uniform sampler2D uTexture;
    varying vec2 vUv;
    varying vec3 vNormal;

    void main() {
      vec4 texColor = texture2D(uTexture, vUv);
      gl_FragColor = vec4(uColor * texColor.rgb, 1.0);
    }
  `,
  transparent: false,
  side: THREE.DoubleSide
});

// Update uniforms in animation loop
material.uniforms.uTime.value = elapsedTime;
```

## Material Disposal

Always dispose materials when no longer needed:

```javascript
material.dispose();

// Dispose textures too
if (material.map) material.map.dispose();
if (material.normalMap) material.normalMap.dispose();
if (material.roughnessMap) material.roughnessMap.dispose();
// ... etc
```

## Troubleshooting

### Material Appears Black
- No lights in scene (for Lambert/Phong/Standard)
- Normals inverted
- Material side setting incorrect

### Material Too Shiny
- Reduce roughness (Standard/Physical)
- Reduce shininess (Phong)
- Check roughnessMap is loaded

### Material Not Transparent
```javascript
material.transparent = true;
material.opacity = 0.5;
material.depthWrite = false; // For glass-like materials
```

### Texture Not Showing
- Check texture.colorSpace (SRGB for diffuse)
- Ensure geometry has UV coordinates
- Verify texture loaded successfully

### Z-Fighting / Flickering
- Adjust material.polygonOffset
```javascript
material.polygonOffset = true;
material.polygonOffsetFactor = -1;
material.polygonOffsetUnits = -1;
```

## Material Performance Ranking

1. **MeshBasicMaterial** - Fastest
2. **MeshToonMaterial** - Very Fast
3. **MeshLambertMaterial** - Fast
4. **MeshPhongMaterial** - Moderate
5. **MeshStandardMaterial** - Moderate-Slow
6. **MeshPhysicalMaterial** - Slowest

Use the simplest material that achieves your visual goals.



===== FILE: plugins/individual/threejs-webgl/skills/threejs-webgl/references/optimization_checklist.md =====

# Three.js Performance Optimization Checklist

## Quick Wins (High Impact, Low Effort)

### ✅ Geometry Optimization

- [ ] **Reuse geometries** across multiple meshes
  ```javascript
  const sharedGeometry = new THREE.BoxGeometry(1, 1, 1);
  // Use for all boxes instead of creating new geometry each time
  ```

- [ ] **Use InstancedMesh** for repeated objects (>50 identical objects)
  ```javascript
  const mesh = new THREE.InstancedMesh(geometry, material, 1000);
  ```

- [ ] **Reduce polygon count** where not visible
  - Use simpler geometries for distant objects
  - Implement LOD (Level of Detail)

- [ ] **Dispose unused geometries**
  ```javascript
  geometry.dispose();
  ```

### ✅ Material Optimization

- [ ] **Share materials** across meshes when possible
- [ ] **Use simpler materials**:
  - MeshBasicMaterial for unlit objects
  - MeshLambertMaterial for mobile
  - MeshStandardMaterial only when PBR needed
- [ ] **Dispose unused materials**
  ```javascript
  material.dispose();
  ```

### ✅ Texture Optimization

- [ ] **Use power-of-two dimensions** (512, 1024, 2048)
- [ ] **Compress textures**:
  - JPEG for photos (smaller file size)
  - PNG for transparency
  - Consider KTX2/Basis Universal for web
- [ ] **Set correct color space**:
  ```javascript
  diffuseTexture.colorSpace = THREE.SRGBColorSpace;
  normalMap.colorSpace = THREE.LinearSRGBColorSpace;
  ```
- [ ] **Limit texture resolution**:
  - 2048x2048 max for most cases
  - 1024x1024 for mobile
  - 512x512 for background/UI elements
- [ ] **Enable mipmaps and anisotropy**:
  ```javascript
  texture.generateMipmaps = true;
  texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
  ```
- [ ] **Dispose unused textures**:
  ```javascript
  texture.dispose();
  ```

### ✅ Rendering Optimization

- [ ] **Set pixel ratio appropriately**:
  ```javascript
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  // Don't use full devicePixelRatio on high-DPI displays
  ```
- [ ] **Disable antialiasing on mobile**
- [ ] **Use render-on-demand** when scene is static:
  ```javascript
  function render() {
    renderer.render(scene, camera);
  }
  // Call only when needed, not in requestAnimationFrame loop
  ```

### ✅ Shadow Optimization

- [ ] **Limit number of shadow-casting lights** (2-3 max)
- [ ] **Reduce shadow map size**:
  ```javascript
  light.shadow.mapSize.width = 1024; // Lower for mobile
  light.shadow.mapSize.height = 1024;
  ```
- [ ] **Optimize shadow camera frustum**:
  ```javascript
  light.shadow.camera.near = 1;
  light.shadow.camera.far = 20; // Only as far as needed
  light.shadow.camera.left = -10;
  light.shadow.camera.right = 10;
  // ... etc - Tight bounds around scene
  ```
- [ ] **Disable shadow updates** when static:
  ```javascript
  renderer.shadowMap.autoUpdate = false;
  renderer.shadowMap.needsUpdate = true; // Only when changed
  ```

## Medium Effort Optimizations

### 🔧 Culling & Visibility

- [ ] **Enable frustum culling** (enabled by default):
  ```javascript
  mesh.frustumCulled = true;
  ```
- [ ] **Compute bounding spheres** for custom geometries:
  ```javascript
  geometry.computeBoundingSphere();
  ```
- [ ] **Hide offscreen objects**:
  ```javascript
  if (distanceToCamera > threshold) {
    mesh.visible = false;
  }
  ```
- [ ] **Use layers** for selective rendering:
  ```javascript
  mesh.layers.set(1);
  camera.layers.enable(1);
  ```

### 🔧 Level of Detail (LOD)

- [ ] **Implement LOD** for complex objects:
  ```javascript
  const lod = new THREE.LOD();
  lod.addLevel(highDetailMesh, 0);
  lod.addLevel(mediumDetailMesh, 50);
  lod.addLevel(lowDetailMesh, 100);
  scene.add(lod);
  ```

### 🔧 Draw Call Reduction

- [ ] **Merge static geometries**:
  ```javascript
  import { mergeGeometries } from 'three/examples/jsm/utils/BufferGeometryUtils.js';
  const merged = mergeGeometries([geo1, geo2, geo3]);
  ```
- [ ] **Use texture atlases** to combine multiple textures
- [ ] **Batch similar materials** together

### 🔧 Animation Optimization

- [ ] **Use Clock.getDelta()** for frame-independent animations:
  ```javascript
  const delta = clock.getDelta();
  mixer.update(delta);
  ```
- [ ] **Pause animations** when offscreen:
  ```javascript
  if (!mesh.visible) {
    mixer.stop();
  }
  ```
- [ ] **Limit AnimationMixer updates** to visible objects

### 🔧 Post-Processing Optimization

- [ ] **Reduce effect quality** on mobile
- [ ] **Limit bloom/blur passes**
- [ ] **Use lower resolution render targets**:
  ```javascript
  const renderTarget = new THREE.WebGLRenderTarget(
    window.innerWidth * 0.5,
    window.innerHeight * 0.5
  );
  ```

## Advanced Optimizations

### ⚙️ Memory Management

- [ ] **Dispose all resources** when removing from scene:
  ```javascript
  function disposeObject(obj) {
    if (obj.geometry) obj.geometry.dispose();
    if (obj.material) {
      if (Array.isArray(obj.material)) {
        obj.material.forEach(m => m.dispose());
      } else {
        obj.material.dispose();
      }
    }
    if (obj.dispose) obj.dispose();
  }

  scene.traverse(disposeObject);
  ```

- [ ] **Clear render targets** when done:
  ```javascript
  renderTarget.dispose();
  ```

- [ ] **Monitor memory usage**:
  ```javascript
  console.log(renderer.info.memory);
  console.log(renderer.info.render);
  ```

### ⚙️ Matrix Optimization

- [ ] **Disable auto-update** for static objects:
  ```javascript
  mesh.matrixAutoUpdate = false;
  mesh.updateMatrix();
  ```

- [ ] **Update world matrix** manually when needed:
  ```javascript
  mesh.matrixWorldNeedsUpdate = true;
  ```

### ⚙️ Custom Shaders

- [ ] **Use low precision** where possible:
  ```glsl
  precision mediump float; // Instead of highp
  ```

- [ ] **Minimize texture samples** in fragment shader
- [ ] **Move calculations** to vertex shader when possible
- [ ] **Use built-in GLSL functions** (faster than custom)

### ⚙️ Lighting Optimization

- [ ] **Limit number of real-time lights** (3-5 max)
- [ ] **Use baked lighting** for static scenes:
  - Lightmaps
  - AO maps
  - Environment maps
- [ ] **Combine directional lights** where possible
- [ ] **Use AmbientLight + DirectionalLight** as base setup

### ⚙️ Model Optimization

- [ ] **Use glTF with Draco compression**:
  ```javascript
  const dracoLoader = new DRACOLoader();
  dracoLoader.setDecoderPath('/draco/');
  gltfLoader.setDRACOLoader(dracoLoader);
  ```

- [ ] **Remove unused data** from models:
  - Multiple UV sets
  - Unused vertex colors
  - Unused morph targets

- [ ] **Optimize mesh topology**:
  - Remove hidden faces
  - Reduce triangle count
  - Use instancing for repeated elements

## Mobile-Specific Optimizations

### 📱 Mobile Best Practices

- [ ] **Lower pixel ratio**:
  ```javascript
  renderer.setPixelRatio(1);
  ```

- [ ] **Disable antialiasing**
- [ ] **Use simpler materials** (MeshLambertMaterial)
- [ ] **Reduce texture resolution** (512-1024px max)
- [ ] **Limit particle count** (<1000)
- [ ] **Disable shadows** or use lower resolution
- [ ] **Reduce geometry complexity** by 50%
- [ ] **Disable post-processing** or use minimal effects
- [ ] **Implement aggressive LOD**
- [ ] **Pause rendering** when tab is hidden:
  ```javascript
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      // Stop animation loop
    } else {
      // Resume animation loop
    }
  });
  ```

## Profiling & Debugging

### 🔍 Performance Monitoring

- [ ] **Use Stats.js**:
  ```javascript
  import Stats from 'three/examples/jsm/libs/stats.module.js';
  const stats = new Stats();
  document.body.appendChild(stats.dom);
  ```

- [ ] **Monitor renderer info**:
  ```javascript
  console.log('Geometries:', renderer.info.memory.geometries);
  console.log('Textures:', renderer.info.memory.textures);
  console.log('Draw Calls:', renderer.info.render.calls);
  console.log('Triangles:', renderer.info.render.triangles);
  ```

- [ ] **Use browser DevTools**:
  - Performance tab (frame rate)
  - Memory tab (heap snapshots)
  - Rendering tab (FPS meter, paint flashing)

- [ ] **WebGL Performance Tools**:
  - Spector.js (WebGL inspector)
  - Chrome GPU Profiler

### 🔍 Common Performance Bottlenecks

1. **Too many draw calls** → Merge geometries, use instancing
2. **Too many triangles** → Reduce geometry complexity, use LOD
3. **Large textures** → Compress, reduce resolution
4. **Too many lights** → Limit lights, use baked lighting
5. **Complex shaders** → Simplify materials
6. **Memory leaks** → Dispose resources properly
7. **Expensive post-processing** → Reduce effects, lower resolution

## Performance Targets

### 🎯 Desktop
- **60 FPS** (16.67ms per frame)
- **Draw calls**: <100
- **Triangles**: <1M visible
- **Texture memory**: <500MB
- **Pixel ratio**: 1-2

### 🎯 Mobile
- **30-60 FPS** (16.67-33ms per frame)
- **Draw calls**: <50
- **Triangles**: <100K visible
- **Texture memory**: <200MB
- **Pixel ratio**: 1

## Optimization Workflow

1. **Profile first** - Identify actual bottlenecks
2. **Optimize bottlenecks** - Focus on highest impact
3. **Measure improvement** - Verify gains
4. **Iterate** - Repeat process

**Remember:** Premature optimization is the root of all evil. Profile before optimizing!

## Quick Optimization Checklist Summary

```
✅ Reuse geometries and materials
✅ Use InstancedMesh for repeated objects
✅ Optimize texture size and format
✅ Set pixel ratio to max 2
✅ Limit shadow-casting lights
✅ Dispose unused resources
✅ Implement LOD for complex objects
✅ Reduce draw calls via merging
✅ Profile with Stats.js
✅ Test on target devices (mobile!)
```



===== FILE: plugins/individual/threejs-webgl/agents/threejs-webgl-architect.md =====

# Three.js WebGL Architect

## Role

Expert 3D/graphics architect specializing in Three.js WebGL scene design, optimization, and best practices.

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
3. Implement best practices from Three.js WebGL ecosystem
4. Optimize for target platforms and devices
5. Provide detailed implementation guidance

## Tools

This agent has access to:
- Three.js WebGL skill knowledge
- Optimization checklists and patterns
- Performance profiling guidance
- Asset pipeline recommendations



===== FILE: plugins/individual/threejs-webgl/commands/setup_scene.md =====

# /threejs-webgl-setup_scene

Three.js WebGL - Setup Scene

## Description

Executes the setup_scene script for Three.js WebGL.

## Usage

```bash
/threejs-webgl-setup_scene
```

## Implementation

This command runs the `setup_scene.py` script from the Three.js WebGL skill, which provides automated assistance for setup scene.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/threejs-webgl/skills/threejs-webgl/scripts/setup_scene.py =====

```py
#!/usr/bin/env python3
"""
Three.js Scene Setup Generator

Generates boilerplate Three.js scene code with customizable options.
"""

import argparse
import os
from pathlib import Path


TEMPLATES = {
    "basic": """import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color({background_color});

// Camera
const camera = new THREE.PerspectiveCamera(
  {fov},
  window.innerWidth / window.innerHeight,
  {near},
  {far}
);
camera.position.set({camera_x}, {camera_y}, {camera_z});

// Renderer
const renderer = new THREE.WebGLRenderer({{ antialias: {antialias} }});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
{shadow_setup}document.body.appendChild(renderer.domElement);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Lights
{lights}

// Animation Loop
const clock = new THREE.Clock();

function animate() {{
  requestAnimationFrame(animate);

  const deltaTime = clock.getDelta();
  controls.update();

  renderer.render(scene, camera);
}}

animate();

// Handle Resize
window.addEventListener('resize', () => {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});
""",

    "webgpu": """import * as THREE from 'three/webgpu';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color({background_color});

// Camera
const camera = new THREE.PerspectiveCamera(
  {fov},
  window.innerWidth / window.innerHeight,
  {near},
  {far}
);
camera.position.set({camera_x}, {camera_y}, {camera_z});

// Renderer (WebGPU)
const renderer = new THREE.WebGPURenderer({{ antialias: {antialias} }});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setAnimationLoop(animate);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
document.body.appendChild(renderer.domElement);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Lights
{lights}

// Animation Loop
const clock = new THREE.Clock();

function animate() {{
  const deltaTime = clock.getDelta();
  controls.update();
}}

// Handle Resize
window.addEventListener('resize', () => {{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}});
"""
}

LIGHT_SETUPS = {
    "basic": """const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 7.5);
scene.add(directionalLight);
""",

    "shadows": """const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 7.5);
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
directionalLight.shadow.camera.left = -10;
directionalLight.shadow.camera.right = 10;
directionalLight.shadow.camera.top = 10;
directionalLight.shadow.camera.bottom = -10;
scene.add(directionalLight);
""",

    "physical": """const hemiLight = new THREE.HemisphereLight(0xddeeff, 0x0f0e0d, 0.02);
scene.add(hemiLight);

const bulbLight = new THREE.PointLight(0xffee88, 1, 100, 2);
bulbLight.power = 1700; // 100W bulb
bulbLight.position.set(0, 2, 0);
bulbLight.castShadow = true;
scene.add(bulbLight);
"""
}


def generate_scene(args):
    """Generate Three.js scene code based on arguments."""

    # Select template
    template = TEMPLATES.get(args.renderer, TEMPLATES["basic"])

    # Select light setup
    lights = LIGHT_SETUPS.get(args.lighting, LIGHT_SETUPS["basic"])

    # Shadow setup
    shadow_setup = ""
    if args.shadows:
        shadow_setup = """renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
"""

    # Fill template
    code = template.format(
        background_color=args.background,
        fov=args.fov,
        near=args.near,
        far=args.far,
        camera_x=args.camera[0],
        camera_y=args.camera[1],
        camera_z=args.camera[2],
        antialias=str(args.antialias).lower(),
        shadow_setup=shadow_setup,
        lights=lights
    )

    return code


def main():
    parser = argparse.ArgumentParser(
        description='Generate Three.js scene boilerplate code'
    )

    # Renderer type
    parser.add_argument(
        '--renderer',
        choices=['basic', 'webgpu'],
        default='basic',
        help='Renderer type (default: basic)'
    )

    # Camera settings
    parser.add_argument(
        '--fov',
        type=int,
        default=75,
        help='Camera field of view (default: 75)'
    )

    parser.add_argument(
        '--near',
        type=float,
        default=0.1,
        help='Camera near plane (default: 0.1)'
    )

    parser.add_argument(
        '--far',
        type=int,
        default=1000,
        help='Camera far plane (default: 1000)'
    )

    parser.add_argument(
        '--camera',
        nargs=3,
        type=float,
        default=[0, 2, 5],
        metavar=('X', 'Y', 'Z'),
        help='Camera position (default: 0 2 5)'
    )

    # Scene settings
    parser.add_argument(
        '--background',
        default='0x000000',
        help='Background color hex (default: 0x000000)'
    )

    parser.add_argument(
        '--lighting',
        choices=['basic', 'shadows', 'physical'],
        default='basic',
        help='Lighting setup (default: basic)'
    )

    parser.add_argument(
        '--shadows',
        action='store_true',
        help='Enable shadow rendering'
    )

    parser.add_argument(
        '--antialias',
        action='store_true',
        default=True,
        help='Enable antialiasing (default: True)'
    )

    # Output
    parser.add_argument(
        '--output',
        '-o',
        help='Output file path (default: print to stdout)'
    )

    args = parser.parse_args()

    # Generate code
    code = generate_scene(args)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code)
        print(f"✅ Generated scene code: {output_path}")
    else:
        print(code)


if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/threejs-webgl/skills/threejs-webgl/assets/starter_scene/README.md =====

# Three.js Starter Scene

A complete, production-ready Three.js boilerplate project with modern best practices.

## Features

✅ WebGL renderer with antialiasing
✅ PBR materials (MeshStandardMaterial)
✅ Shadow mapping
✅ Tone mapping (ACES Filmic)
✅ Orbit controls with damping
✅ Responsive design
✅ Loading screen
✅ Animated demo objects
✅ Performance optimizations

## Quick Start

### Option 1: Local Development

```bash
# Serve with any static server
python -m http.server 8000
# Or
npx serve
```

Open `http://localhost:8000` in your browser.

### Option 2: Add to Existing Project

Copy `index.html` and `main.js` to your project and customize as needed.

## Project Structure

```
starter_scene/
├── index.html    # HTML with embedded styles and import map
├── main.js       # Main Three.js scene setup
└── README.md     # This file
```

## Customization

### Change Background Color

```javascript
// In main.js
scene.background = new THREE.Color(0x1a1a2e); // Change hex color
```

### Add Your Own Objects

```javascript
// After existing objects in main.js
const myGeometry = new THREE.BoxGeometry(1, 1, 1);
const myMaterial = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const myMesh = new THREE.Mesh(myGeometry, myMaterial);
myMesh.position.set(x, y, z);
myMesh.castShadow = true;
scene.add(myMesh);
```

### Load 3D Models

```javascript
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const loader = new GLTFLoader();
loader.load('model.glb', (gltf) => {
  scene.add(gltf.scene);
});
```

### Adjust Performance

```javascript
// Reduce pixel ratio for better performance
renderer.setPixelRatio(1);

// Disable shadows
renderer.shadowMap.enabled = false;

// Simplify materials
material.roughness = 1.0; // More matte = faster
```

## Built-in Demo

The starter scene includes:
- **Red Cube**: Rotating on multiple axes
- **Cyan Sphere**: Bobbing up and down
- **Yellow Torus**: Rotating ring
- **Animated Point Light**: Orbiting the scene
- **Grid Floor**: With shadows

## Controls

- **Left Click + Drag**: Orbit camera
- **Scroll**: Zoom in/out
- **Right Click + Drag**: Pan (if enabled)

## Browser Compatibility

- Chrome/Edge: ✅ Excellent
- Firefox: ✅ Excellent
- Safari: ✅ Good (WebGL only)

## Performance Tips

1. Reduce `renderer.setPixelRatio()` to 1 on mobile
2. Lower shadow map size for better FPS
3. Use simpler materials (MeshLambertMaterial) on mobile
4. Implement LOD for complex scenes
5. Use `InstancedMesh` for repeated objects

## Next Steps

1. Replace demo objects with your own content
2. Add textures and materials
3. Implement raycasting for interactivity
4. Add post-processing effects
5. Optimize for production

## Resources

- [Three.js Documentation](https://threejs.org/docs/)
- [Three.js Examples](https://threejs.org/examples/)
- [Three.js Fundamentals](https://threejsfundamentals.org/)

## License

This starter template is provided as-is for use in any project.



===== FILE: plugins/individual/threejs-webgl/skills/threejs-webgl/assets/starter_scene/index.html =====

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Three.js Starter Scene</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    canvas {
      display: block;
    }

    #info {
      position: absolute;
      top: 20px;
      left: 20px;
      padding: 15px 20px;
      background: rgba(0, 0, 0, 0.7);
      color: white;
      border-radius: 8px;
      font-size: 14px;
      line-height: 1.6;
      pointer-events: none;
      backdrop-filter: blur(10px);
    }

    #info h1 {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 8px;
    }

    #info p {
      margin: 0;
      opacity: 0.8;
    }

    #loading {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 30px 40px;
      border-radius: 12px;
      font-size: 16px;
      backdrop-filter: blur(10px);
    }

    #loading.hidden {
      display: none;
    }
  </style>
</head>
<body>
  <div id="loading">Loading Scene...</div>

  <div id="info">
    <h1>Three.js Starter Scene</h1>
    <p>Click and drag to orbit • Scroll to zoom</p>
  </div>

  <script type="importmap">
    {
      "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
      }
    }
  </script>

  <script type="module" src="./main.js"></script>
</body>
</html>

```


===== FILE: plugins/individual/threejs-webgl/skills/threejs-webgl/assets/starter_scene/main.js =====

```js
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// Scene, Camera, Renderer
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);
scene.fog = new THREE.Fog(0x1a1a2e, 10, 50);

const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
camera.position.set(5, 3, 8);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
document.body.appendChild(renderer.domElement);

// Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 3;
controls.maxDistance = 20;
controls.maxPolarAngle = Math.PI / 2;
controls.target.set(0, 1, 0);

// Lights
const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 10, 7.5);
directionalLight.castShadow = true;
directionalLight.shadow.mapSize.width = 2048;
directionalLight.shadow.mapSize.height = 2048;
directionalLight.shadow.camera.left = -10;
directionalLight.shadow.camera.right = 10;
directionalLight.shadow.camera.top = 10;
directionalLight.shadow.camera.bottom = -10;
directionalLight.shadow.camera.near = 0.5;
directionalLight.shadow.camera.far = 50;
scene.add(directionalLight);

// Add point light for accent
const pointLight = new THREE.PointLight(0x00ffff, 0.5, 15);
pointLight.position.set(-3, 3, -3);
scene.add(pointLight);

// Floor
const floorGeometry = new THREE.PlaneGeometry(20, 20);
const floorMaterial = new THREE.MeshStandardMaterial({
  color: 0x2a2a4a,
  roughness: 0.8,
  metalness: 0.2
});
const floor = new THREE.Mesh(floorGeometry, floorMaterial);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// Grid Helper
const gridHelper = new THREE.GridHelper(20, 20, 0x444466, 0x222244);
gridHelper.position.y = 0.01;
scene.add(gridHelper);

// Demo Objects
const objectsGroup = new THREE.Group();
scene.add(objectsGroup);

// Spinning cube
const cubeGeometry = new THREE.BoxGeometry(1, 1, 1);
const cubeMaterial = new THREE.MeshStandardMaterial({
  color: 0xff6b6b,
  roughness: 0.3,
  metalness: 0.7
});
const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
cube.position.set(-2, 1, 0);
cube.castShadow = true;
cube.receiveShadow = true;
objectsGroup.add(cube);

// Sphere
const sphereGeometry = new THREE.SphereGeometry(0.7, 32, 32);
const sphereMaterial = new THREE.MeshStandardMaterial({
  color: 0x4ecdc4,
  roughness: 0.2,
  metalness: 0.8
});
const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
sphere.position.set(0, 1.2, 0);
sphere.castShadow = true;
sphere.receiveShadow = true;
objectsGroup.add(sphere);

// Torus
const torusGeometry = new THREE.TorusGeometry(0.6, 0.25, 16, 32);
const torusMaterial = new THREE.MeshStandardMaterial({
  color: 0xffe66d,
  roughness: 0.4,
  metalness: 0.6
});
const torus = new THREE.Mesh(torusGeometry, torusMaterial);
torus.position.set(2, 1, 0);
torus.castShadow = true;
torus.receiveShadow = true;
objectsGroup.add(torus);

// Animation Loop
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);

  const deltaTime = clock.getDelta();
  const elapsedTime = clock.getElapsedTime();

  // Animate objects
  cube.rotation.y += deltaTime * 0.5;
  cube.rotation.x += deltaTime * 0.25;

  sphere.position.y = 1.2 + Math.sin(elapsedTime * 2) * 0.3;

  torus.rotation.x += deltaTime * 0.3;
  torus.rotation.y += deltaTime * 0.5;

  // Animate point light
  pointLight.position.x = Math.sin(elapsedTime * 0.5) * 5;
  pointLight.position.z = Math.cos(elapsedTime * 0.5) * 5;

  // Update controls
  controls.update();

  // Render
  renderer.render(scene, camera);
}

// Handle Resize
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Hide loading screen and start animation
document.getElementById('loading').classList.add('hidden');
animate();

```


# Skill: react-three-fiber


===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/SKILL.md =====

---
name: react-three-fiber
description: Build declarative 3D scenes with React Three Fiber (R3F) - a React renderer for Three.js. Use when building interactive 3D experiences in React applications with component-based architecture, state management, and reusable abstractions. Ideal for product configurators, portfolios, games, data visualization, and immersive web experiences.
---

# React Three Fiber

## Overview

React Three Fiber (R3F) is a React renderer for Three.js that brings declarative, component-based 3D development to React applications. Instead of imperatively creating and managing Three.js objects, you build 3D scenes using JSX components that map directly to Three.js objects.

**When to Use This Skill**:
- Building 3D experiences within React applications
- Creating interactive product configurators or showcases
- Developing 3D portfolios, galleries, or storytelling experiences
- Building games or simulations in React
- Adding 3D elements to existing React projects
- When you need state management and React hooks with 3D graphics
- When working with React frameworks (Next.js, Gatsby, Remix)

**Key Benefits**:
- **Declarative**: Write 3D scenes like React components
- **React Integration**: Full access to hooks, context, state management
- **Reusability**: Create and share 3D component libraries
- **Performance**: Automatic render optimization and reconciliation
- **Ecosystem**: Works with Drei helpers, Zustand, Framer Motion, etc.
- **TypeScript Support**: Full type safety for Three.js objects

---

## Core Concepts

### 1. Canvas Component

The `<Canvas>` component sets up a Three.js scene, camera, renderer, and render loop.

```jsx
import { Canvas } from '@react-three/fiber'

function App() {
  return (
    <Canvas
      camera={{ position: [0, 0, 5], fov: 75 }}
      gl={{ antialias: true }}
      dpr={[1, 2]}
    >
      {/* 3D content goes here */}
    </Canvas>
  )
}
```

**Canvas Props**:
- `camera` - Camera configuration (position, fov, near, far)
- `gl` - WebGL renderer settings
- `dpr` - Device pixel ratio (default: [1, 2])
- `shadows` - Enable shadow mapping (default: false)
- `frameloop` - "always" (default), "demand", or "never"
- `flat` - Disable color management for simpler colors
- `linear` - Use linear color space instead of sRGB

### 2. Declarative 3D Objects

Three.js objects are created using JSX with kebab-case props:

```jsx
// THREE.Mesh + THREE.BoxGeometry + THREE.MeshStandardMaterial
<mesh position={[0, 0, 0]} rotation={[0, Math.PI / 4, 0]}>
  <boxGeometry args={[1, 1, 1]} />
  <meshStandardMaterial color="hotpink" />
</mesh>
```

**Prop Mapping**:
- `position` → `object.position.set(x, y, z)`
- `rotation` → `object.rotation.set(x, y, z)`
- `scale` → `object.scale.set(x, y, z)`
- `args` → Constructor arguments for geometry/material
- `attach` → Attach to parent property (e.g., `attach="material"`)

**Shorthand Notation**:
```jsx
// Full notation
<mesh position={[1, 2, 3]} />

// Axis-specific (dash notation)
<mesh position-x={1} position-y={2} position-z={3} />
```

### 3. useFrame Hook

Execute code on every frame (animation loop):

```jsx
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function RotatingBox() {
  const meshRef = useRef()

  useFrame((state, delta) => {
    // Rotate mesh on every frame
    meshRef.current.rotation.x += delta
    meshRef.current.rotation.y += delta * 0.5

    // Access scene state
    const time = state.clock.elapsedTime
    meshRef.current.position.y = Math.sin(time) * 2
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}
```

**useFrame Parameters**:
- `state` - Scene state (camera, scene, gl, clock, etc.)
- `delta` - Time since last frame (for frame-rate independence)
- `xrFrame` - XR frame data (for VR/AR)

**Important**: Never use `setState` inside `useFrame` - it causes unnecessary re-renders!

### 4. useThree Hook

Access scene state and methods:

```jsx
import { useThree } from '@react-three/fiber'

function CameraInfo() {
  const { camera, gl, scene, size, viewport } = useThree()

  // Selective subscription (only re-render on size change)
  const size = useThree((state) => state.size)

  // Get state non-reactively
  const get = useThree((state) => state.get)
  const freshState = get() // Latest state without triggering re-render

  return null
}
```

**Available State**:
- `camera` - Default camera
- `scene` - Three.js scene
- `gl` - WebGL renderer
- `size` - Canvas dimensions
- `viewport` - Viewport dimensions in 3D units
- `clock` - Three.js clock
- `pointer` - Normalized mouse coordinates
- `invalidate()` - Manually trigger render
- `setSize()` - Manually resize canvas

### 5. useLoader Hook

Load assets with automatic caching and Suspense integration:

```jsx
import { Suspense } from 'react'
import { useLoader } from '@react-three/fiber'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { TextureLoader } from 'three'

function Model() {
  const gltf = useLoader(GLTFLoader, '/model.glb')
  return <primitive object={gltf.scene} />
}

function TexturedMesh() {
  const texture = useLoader(TextureLoader, '/texture.jpg')
  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial map={texture} />
    </mesh>
  )
}

function App() {
  return (
    <Canvas>
      <Suspense fallback={<LoadingIndicator />}>
        <Model />
        <TexturedMesh />
      </Suspense>
    </Canvas>
  )
}
```

**Loading Multiple Assets**:
```jsx
const [texture1, texture2, texture3] = useLoader(TextureLoader, [
  '/tex1.jpg',
  '/tex2.jpg',
  '/tex3.jpg'
])
```

**Loader Extensions**:
```jsx
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader'

useLoader(GLTFLoader, '/model.glb', (loader) => {
  const dracoLoader = new DRACOLoader()
  dracoLoader.setDecoderPath('/draco/')
  loader.setDRACOLoader(dracoLoader)
})
```

**Pre-loading**:
```jsx
// Pre-load assets before component mounts
useLoader.preload(GLTFLoader, '/model.glb')
```

---

## Common Patterns

### Pattern 1: Basic Scene Setup

```jsx
import { Canvas } from '@react-three/fiber'

function Scene() {
  return (
    <>
      {/* Lights */}
      <ambientLight intensity={0.5} />
      <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} />

      {/* Objects */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="hotpink" />
      </mesh>
    </>
  )
}

function App() {
  return (
    <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
      <Scene />
    </Canvas>
  )
}
```

### Pattern 2: Interactive Objects (Click, Hover)

```jsx
import { useState } from 'react'

function InteractiveBox() {
  const [hovered, setHovered] = useState(false)
  const [active, setActive] = useState(false)

  return (
    <mesh
      scale={active ? 1.5 : 1}
      onClick={() => setActive(!active)}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <boxGeometry />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
    </mesh>
  )
}
```

### Pattern 3: Animated Component with useFrame

```jsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

function AnimatedSphere() {
  const meshRef = useRef()

  useFrame((state, delta) => {
    // Rotate
    meshRef.current.rotation.y += delta

    // Oscillate position
    const time = state.clock.elapsedTime
    meshRef.current.position.y = Math.sin(time) * 2
  })

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="cyan" />
    </mesh>
  )
}
```

### Pattern 4: Loading GLTF Models

```jsx
import { Suspense } from 'react'
import { useLoader } from '@react-three/fiber'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'

function Model({ url }) {
  const gltf = useLoader(GLTFLoader, url)

  return (
    <primitive
      object={gltf.scene}
      scale={0.5}
      position={[0, 0, 0]}
    />
  )
}

function App() {
  return (
    <Canvas>
      <Suspense fallback={<LoadingPlaceholder />}>
        <Model url="/model.glb" />
      </Suspense>
    </Canvas>
  )
}

function LoadingPlaceholder() {
  return (
    <mesh>
      <boxGeometry />
      <meshBasicMaterial wireframe />
    </mesh>
  )
}
```

### Pattern 5: Multiple Lights

```jsx
function Lighting() {
  return (
    <>
      {/* Ambient light for base illumination */}
      <ambientLight intensity={0.3} />

      {/* Directional light with shadows */}
      <directionalLight
        position={[5, 5, 5]}
        intensity={1}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />

      {/* Point light for accent */}
      <pointLight position={[-5, 5, -5]} intensity={0.5} color="blue" />

      {/* Spot light for focused illumination */}
      <spotLight
        position={[10, 10, 10]}
        angle={0.3}
        penumbra={1}
        intensity={1}
      />
    </>
  )
}
```

### Pattern 6: Instancing (Many Objects)

```jsx
import { useMemo, useRef } from 'react'
import * as THREE from 'three'
import { useFrame } from '@react-three/fiber'

function Particles({ count = 1000 }) {
  const meshRef = useRef()

  // Generate random positions
  const particles = useMemo(() => {
    const temp = []
    for (let i = 0; i < count; i++) {
      const t = Math.random() * 100
      const factor = 20 + Math.random() * 100
      const speed = 0.01 + Math.random() / 200
      const x = Math.random() * 2 - 1
      const y = Math.random() * 2 - 1
      const z = Math.random() * 2 - 1
      temp.push({ t, factor, speed, x, y, z, mx: 0, my: 0 })
    }
    return temp
  }, [count])

  const dummy = useMemo(() => new THREE.Object3D(), [])

  useFrame(() => {
    particles.forEach((particle, i) => {
      let { t, factor, speed, x, y, z } = particle
      t = particle.t += speed / 2
      const a = Math.cos(t) + Math.sin(t * 1) / 10
      const b = Math.sin(t) + Math.cos(t * 2) / 10
      const s = Math.cos(t)

      dummy.position.set(
        x + Math.cos((t / 10) * factor) + (Math.sin(t * 1) * factor) / 10,
        y + Math.sin((t / 10) * factor) + (Math.cos(t * 2) * factor) / 10,
        z + Math.cos((t / 10) * factor) + (Math.sin(t * 3) * factor) / 10
      )
      dummy.scale.set(s, s, s)
      dummy.updateMatrix()
      meshRef.current.setMatrixAt(i, dummy.matrix)
    })
    meshRef.current.instanceMatrix.needsUpdate = true
  })

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]}>
      <sphereGeometry args={[0.05, 8, 8]} />
      <meshBasicMaterial color="white" />
    </instancedMesh>
  )
}
```

### Pattern 7: Groups and Nesting

```jsx
function Robot() {
  return (
    <group position={[0, 0, 0]}>
      {/* Body */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[1, 2, 1]} />
        <meshStandardMaterial color="gray" />
      </mesh>

      {/* Head */}
      <mesh position={[0, 1.5, 0]}>
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial color="silver" />
      </mesh>

      {/* Arms */}
      <group position={[-0.75, 0.5, 0]}>
        <mesh>
          <cylinderGeometry args={[0.1, 0.1, 1.5]} />
          <meshStandardMaterial color="darkgray" />
        </mesh>
      </group>

      <group position={[0.75, 0.5, 0]}>
        <mesh>
          <cylinderGeometry args={[0.1, 0.1, 1.5]} />
          <meshStandardMaterial color="darkgray" />
        </mesh>
      </group>
    </group>
  )
}
```

---

## Integration with Drei Helpers

[Drei](https://github.com/pmndrs/drei) is the essential helper library for R3F, providing ready-to-use components:

### OrbitControls

```jsx
import { OrbitControls } from '@react-three/drei'

<Canvas>
  <OrbitControls
    makeDefault
    enableDamping
    dampingFactor={0.05}
    minDistance={3}
    maxDistance={20}
  />
  <Box />
</Canvas>
```

### Environment & Lighting

```jsx
import { Environment, ContactShadows } from '@react-three/drei'

<Canvas>
  {/* HDRI environment map */}
  <Environment preset="sunset" />

  {/* Or custom */}
  <Environment files="/hdri.hdr" />

  {/* Soft contact shadows */}
  <ContactShadows
    opacity={0.5}
    scale={10}
    blur={1}
    far={10}
    resolution={256}
  />

  <Model />
</Canvas>
```

### Text

```jsx
import { Text, Text3D } from '@react-three/drei'

// 2D Billboard text
<Text
  position={[0, 2, 0]}
  fontSize={1}
  color="white"
  anchorX="center"
  anchorY="middle"
>
  Hello World
</Text>

// 3D extruded text
<Text3D
  font="/fonts/helvetiker_regular.typeface.json"
  size={1}
  height={0.2}
>
  3D Text
  <meshNormalMaterial />
</Text3D>
```

### useGLTF Hook (Drei)

```jsx
import { useGLTF } from '@react-three/drei'

function Model() {
  const { scene, materials, nodes } = useGLTF('/model.glb')

  return <primitive object={scene} />
}

// Pre-load
useGLTF.preload('/model.glb')
```

### Center & Bounds

```jsx
import { Center, Bounds, useBounds } from '@react-three/drei'

// Auto-center objects
<Center>
  <Model />
</Center>

// Auto-fit camera to bounds
<Bounds fit clip observe margin={1.2}>
  <Model />
</Bounds>
```

### HTML Overlay

```jsx
import { Html } from '@react-three/drei'

<mesh>
  <boxGeometry />
  <meshStandardMaterial />

  <Html
    position={[0, 1, 0]}
    center
    distanceFactor={10}
  >
    <div className="annotation">
      This is a box
    </div>
  </Html>
</mesh>
```

### Scroll Controls

```jsx
import { ScrollControls, Scroll, useScroll } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'

function AnimatedScene() {
  const scroll = useScroll()
  const meshRef = useRef()

  useFrame(() => {
    const offset = scroll.offset // 0-1 normalized scroll position
    meshRef.current.position.y = offset * 10
  })

  return <mesh ref={meshRef}>...</mesh>
}

<Canvas>
  <ScrollControls pages={3} damping={0.5}>
    <Scroll>
      <AnimatedScene />
    </Scroll>

    {/* HTML overlay */}
    <Scroll html>
      <div style={{ height: '100vh' }}>
        <h1>Scrollable content</h1>
      </div>
    </Scroll>
  </ScrollControls>
</Canvas>
```

---

## Integration with Other Libraries

### With GSAP

```jsx
import { useRef, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import gsap from 'gsap'

function AnimatedBox() {
  const meshRef = useRef()

  useEffect(() => {
    // GSAP timeline animation
    const tl = gsap.timeline({ repeat: -1, yoyo: true })

    tl.to(meshRef.current.position, {
      y: 2,
      duration: 1,
      ease: 'power2.inOut'
    })
    .to(meshRef.current.rotation, {
      y: Math.PI * 2,
      duration: 2,
      ease: 'none'
    }, 0)

    return () => tl.kill()
  }, [])

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}
```

### With Framer Motion

```jsx
import { motion } from 'framer-motion-3d'

function AnimatedSphere() {
  return (
    <motion.mesh
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ duration: 1 }}
    >
      <sphereGeometry />
      <meshStandardMaterial color="hotpink" />
    </motion.mesh>
  )
}
```

### With Zustand (State Management)

```jsx
import create from 'zustand'

const useStore = create((set) => ({
  color: 'orange',
  setColor: (color) => set({ color })
}))

function Box() {
  const color = useStore((state) => state.color)
  const setColor = useStore((state) => state.setColor)

  return (
    <mesh onClick={() => setColor('hotpink')}>
      <boxGeometry />
      <meshStandardMaterial color={color} />
    </mesh>
  )
}
```

---

## Performance Optimization

### 1. On-Demand Rendering

```jsx
<Canvas frameloop="demand">
  {/* Only renders when needed */}
</Canvas>

// Manually trigger render
function MyComponent() {
  const invalidate = useThree((state) => state.invalidate)

  return (
    <mesh onClick={() => invalidate()}>
      <boxGeometry />
      <meshStandardMaterial />
    </mesh>
  )
}
```

### 2. Instancing

Use `<instancedMesh>` for rendering many identical objects:

```jsx
function Particles({ count = 10000 }) {
  const meshRef = useRef()

  useEffect(() => {
    const temp = new THREE.Object3D()

    for (let i = 0; i < count; i++) {
      temp.position.set(
        Math.random() * 10 - 5,
        Math.random() * 10 - 5,
        Math.random() * 10 - 5
      )
      temp.updateMatrix()
      meshRef.current.setMatrixAt(i, temp.matrix)
    }

    meshRef.current.instanceMatrix.needsUpdate = true
  }, [count])

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]}>
      <sphereGeometry args={[0.1, 8, 8]} />
      <meshBasicMaterial color="white" />
    </instancedMesh>
  )
}
```

### 3. Frustum Culling

Objects outside the camera view are automatically culled.

```jsx
// Disable for always-visible objects
<mesh frustumCulled={false}>
  <boxGeometry />
  <meshStandardMaterial />
</mesh>
```

### 4. LOD (Level of Detail)

```jsx
import { Detailed } from '@react-three/drei'

<Detailed distances={[0, 10, 20]}>
  {/* High detail - close to camera */}
  <mesh geometry={highPolyGeometry} />

  {/* Medium detail */}
  <mesh geometry={mediumPolyGeometry} />

  {/* Low detail - far from camera */}
  <mesh geometry={lowPolyGeometry} />
</Detailed>
```

### 5. Adaptive Performance

```jsx
import { AdaptiveDpr, AdaptiveEvents, PerformanceMonitor } from '@react-three/drei'

<Canvas>
  {/* Reduce DPR when performance drops */}
  <AdaptiveDpr pixelated />

  {/* Reduce raycast frequency */}
  <AdaptiveEvents />

  {/* Monitor and respond to performance */}
  <PerformanceMonitor
    onIncline={() => console.log('Performance improved')}
    onDecline={() => console.log('Performance degraded')}
  >
    <Scene />
  </PerformanceMonitor>
</Canvas>
```

### 6. Selective Re-renders

Use `useThree` selectors to avoid unnecessary re-renders:

```jsx
// ❌ Re-renders on any state change
const state = useThree()

// ✅ Only re-renders when size changes
const size = useThree((state) => state.size)

// ✅ Only re-renders when camera changes
const camera = useThree((state) => state.camera)
```

---

## Common Pitfalls & Solutions

### ❌ Pitfall 1: setState in useFrame

```jsx
// ❌ BAD: Triggers React re-renders every frame
const [x, setX] = useState(0)
useFrame(() => setX((x) => x + 0.1))
return <mesh position-x={x} />
```

✅ **Solution**: Mutate refs directly

```jsx
// ✅ GOOD: Direct mutation, no re-renders
const meshRef = useRef()
useFrame((state, delta) => {
  meshRef.current.position.x += delta
})
return <mesh ref={meshRef} />
```

### ❌ Pitfall 2: Creating Objects in Render

```jsx
// ❌ BAD: Creates new Vector3 every render
<mesh position={new THREE.Vector3(1, 2, 3)} />
```

✅ **Solution**: Use arrays or useMemo

```jsx
// ✅ GOOD: Use array notation
<mesh position={[1, 2, 3]} />

// Or useMemo for complex objects
const position = useMemo(() => new THREE.Vector3(1, 2, 3), [])
<mesh position={position} />
```

### ❌ Pitfall 3: Not Using useLoader Cache

```jsx
// ❌ BAD: Loads texture every render
function Component() {
  const [texture, setTexture] = useState()
  useEffect(() => {
    new TextureLoader().load('/texture.jpg', setTexture)
  }, [])
  return texture ? <meshBasicMaterial map={texture} /> : null
}
```

✅ **Solution**: Use useLoader (automatic caching)

```jsx
// ✅ GOOD: Cached and reused
function Component() {
  const texture = useLoader(TextureLoader, '/texture.jpg')
  return <meshBasicMaterial map={texture} />
}
```

### ❌ Pitfall 4: Conditional Mounting (Expensive)

```jsx
// ❌ BAD: Unmounts and remounts (expensive)
{stage === 1 && <Stage1 />}
{stage === 2 && <Stage2 />}
{stage === 3 && <Stage3 />}
```

✅ **Solution**: Use visibility prop

```jsx
// ✅ GOOD: Components stay mounted, just hidden
<Stage1 visible={stage === 1} />
<Stage2 visible={stage === 2} />
<Stage3 visible={stage === 3} />

function Stage1({ visible, ...props }) {
  return <group {...props} visible={visible}>...</group>
}
```

### ❌ Pitfall 5: useThree Outside Canvas

```jsx
// ❌ BAD: Crashes - useThree must be inside Canvas
function App() {
  const { size } = useThree()
  return <Canvas>...</Canvas>
}
```

✅ **Solution**: Use hooks inside Canvas children

```jsx
// ✅ GOOD: useThree inside Canvas child
function CameraInfo() {
  const { size } = useThree()
  return null
}

function App() {
  return (
    <Canvas>
      <CameraInfo />
    </Canvas>
  )
}
```

### ❌ Pitfall 6: Not Disposing Resources

```jsx
// ❌ BAD: Memory leak - textures not disposed
const texture = useLoader(TextureLoader, '/texture.jpg')
```

✅ **Solution**: R3F handles disposal automatically, but be careful with manual Three.js objects

```jsx
// ✅ GOOD: Manual cleanup when needed
useEffect(() => {
  const geometry = new THREE.SphereGeometry(1)
  const material = new THREE.MeshBasicMaterial()

  return () => {
    geometry.dispose()
    material.dispose()
  }
}, [])
```

---

## Best Practices

### 1. Component Composition

Break scenes into reusable components:

```jsx
function Lights() {
  return (
    <>
      <ambientLight intensity={0.5} />
      <spotLight position={[10, 10, 10]} angle={0.15} />
    </>
  )
}

function Scene() {
  return (
    <>
      <Lights />
      <Model />
      <Ground />
      <Effects />
    </>
  )
}

<Canvas>
  <Scene />
</Canvas>
```

### 2. Suspend Heavy Assets

Always wrap async operations in Suspense:

```jsx
<Canvas>
  <Suspense fallback={<Loader />}>
    <Model />
    <Environment />
  </Suspense>
</Canvas>
```

### 3. Use TypeScript

```typescript
import { ThreeElements } from '@react-three/fiber'

function Box(props: ThreeElements['mesh']) {
  return (
    <mesh {...props}>
      <boxGeometry />
      <meshStandardMaterial />
    </mesh>
  )
}
```

### 4. Organize by Feature

```
src/
  components/
    3d/
      Scene.tsx
      Lights.tsx
      Camera.tsx
    models/
      Robot.tsx
      Character.tsx
    effects/
      PostProcessing.tsx
```

### 5. Test with React DevTools Profiler

Monitor re-renders and optimize components causing performance issues.

---

## Resources

### References
- `references/api_reference.md` - Complete R3F & Drei API documentation
- `references/hooks_guide.md` - Detailed hooks usage and patterns
- `references/drei_helpers.md` - Comprehensive Drei library guide

### Scripts
- `scripts/component_generator.py` - Generate R3F component boilerplate
- `scripts/scene_setup.py` - Initialize R3F scene with common patterns

### Assets
- `assets/starter_r3f/` - Complete R3F + Vite starter template
- `assets/examples/` - Real-world R3F component examples

### External Resources
- [Official Docs](https://docs.pmnd.rs/react-three-fiber)
- [Drei Docs](https://github.com/pmndrs/drei)
- [Three.js Docs](https://threejs.org/docs/)
- [R3F Discord](https://discord.gg/ZZjjNvJ)
- [Poimandres (pmnd.rs)](https://pmnd.rs/) - Ecosystem overview



===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/references/api_reference.md =====

# React Three Fiber API Reference

Complete API reference for React Three Fiber core and essential Drei helpers.

---

## Table of Contents

1. [Canvas Component](#canvas-component)
2. [Hooks](#hooks)
3. [Events](#events)
4. [Three.js Object Props](#threejs-object-props)
5. [Drei Helpers](#drei-helpers)

---

## Canvas Component

The `<Canvas>` component is the root of every R3F scene. It sets up the renderer, scene, and camera.

### Props

```typescript
interface CanvasProps {
  children: React.ReactNode

  // Rendering
  gl?: Partial<WebGLRendererParameters> | ((canvas: HTMLCanvasElement) => WebGLRenderer)
  dpr?: number | [min: number, max: number]
  frameloop?: 'always' | 'demand' | 'never'
  flat?: boolean
  linear?: boolean
  legacy?: boolean

  // Camera
  camera?: Partial<PerspectiveCamera> | Partial<OrthographicCamera>
  orthographic?: boolean

  // Scene
  shadows?: boolean | Partial<WebGLShadowMap>
  raycaster?: Partial<Raycaster>

  // Events
  events?: EventManager
  eventSource?: HTMLElement | React.RefObject<HTMLElement>
  eventPrefix?: 'offset' | 'client' | 'page' | 'layer' | 'screen'

  // Size
  resize?: { scroll?: boolean; debounce?: number | { scroll: number; resize: number } }

  // Performance
  performance?: {
    current?: number
    min?: number
    max?: number
    debounce?: number
  }

  // Callbacks
  onCreated?: (state: RootState) => void
  onPointerMissed?: (event: MouseEvent) => void
}
```

### Examples

```jsx
// Basic setup
<Canvas>
  <Scene />
</Canvas>

// Custom camera
<Canvas camera={{ position: [0, 0, 5], fov: 75, near: 0.1, far: 1000 }}>
  <Scene />
</Canvas>

// Orthographic camera
<Canvas orthographic camera={{ zoom: 50, position: [0, 0, 5] }}>
  <Scene />
</Canvas>

// Enable shadows
<Canvas shadows>
  <Scene />
</Canvas>

// Custom renderer settings
<Canvas
  gl={{
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
  }}
  dpr={[1, 2]}
>
  <Scene />
</Canvas>

// On-demand rendering
<Canvas frameloop="demand">
  <Scene />
</Canvas>

// Performance monitoring
<Canvas
  performance={{ min: 0.5, max: 1, debounce: 200 }}
  onCreated={(state) => console.log('Canvas created:', state)}
>
  <Scene />
</Canvas>
```

---

## Hooks

### useFrame

Execute code on every rendered frame.

```typescript
useFrame(
  callback: (state: RootState, delta: number, xrFrame?: XRFrame) => void,
  renderPriority?: number
): void
```

**Parameters**:
- `callback` - Function called every frame
- `renderPriority` - Execution order (default: 0, higher = later)

**State Object**:
```typescript
interface RootState {
  gl: WebGLRenderer
  scene: Scene
  camera: Camera
  raycaster: Raycaster
  pointer: Vector2
  mouse: Vector2 // Deprecated, use pointer
  clock: Clock
  size: { width: number; height: number; top: number; left: number }
  viewport: {
    width: number
    height: number
    initialDpr: number
    dpr: number
    factor: number
    distance: number
    aspect: number
  }
  performance: { current: number; min: number; max: number; debounce: number }
  frameloop: 'always' | 'demand' | 'never'
  controls: any
  invalidate: (frames?: number) => void
  advance: (timestamp: number, runGlobalEffects?: boolean) => void
  setSize: (width: number, height: number) => void
  setDpr: (dpr: number) => void
  setFrameloop: (frameloop: 'always' | 'demand' | 'never') => void
  get: () => RootState
  set: (partial: Partial<RootState>) => void
}
```

**Examples**:

```jsx
// Basic animation
function RotatingBox() {
  const meshRef = useRef()

  useFrame((state, delta) => {
    meshRef.current.rotation.x += delta
    meshRef.current.rotation.y += delta * 0.5
  })

  return <mesh ref={meshRef}>...</mesh>
}

// Access clock for time-based animations
function FloatingBox() {
  const meshRef = useRef()

  useFrame((state) => {
    const time = state.clock.elapsedTime
    meshRef.current.position.y = Math.sin(time) * 2
  })

  return <mesh ref={meshRef}>...</mesh>
}

// Control render loop
function CustomRender() {
  useFrame(({ gl, scene, camera }) => {
    gl.render(scene, camera)
  }, 1) // renderPriority = 1 (takes over rendering)
}

// Ordered execution
function First() {
  useFrame(() => console.log('First'), -1)
}

function Second() {
  useFrame(() => console.log('Second'), 0)
}

function Third() {
  useFrame(() => console.log('Third'), 1)
}
```

---

### useThree

Access R3F state and scene objects.

```typescript
useThree<T = RootState>(
  selector?: (state: RootState) => T,
  equalityFn?: (a: T, b: T) => boolean
): T
```

**Parameters**:
- `selector` - Function to select specific state (optional)
- `equalityFn` - Custom equality function for optimization

**Examples**:

```jsx
// Get all state (re-renders on any change)
function Component() {
  const state = useThree()
  const { gl, scene, camera, size } = state
  return null
}

// Selective subscription (only re-renders when size changes)
function Component() {
  const size = useThree((state) => state.size)
  console.log(size.width, size.height)
  return null
}

// Multiple selections
function Component() {
  const camera = useThree((state) => state.camera)
  const viewport = useThree((state) => state.viewport)
  const gl = useThree((state) => state.gl)
  return null
}

// Get state non-reactively
function Component() {
  const get = useThree((state) => state.get)

  function handleClick() {
    const freshState = get()
    console.log(freshState.camera.position)
  }

  return <mesh onClick={handleClick}>...</mesh>
}

// Manual invalidation (trigger render)
function Component() {
  const invalidate = useThree((state) => state.invalidate)

  return (
    <mesh onClick={() => invalidate()}>
      <boxGeometry />
      <meshStandardMaterial />
    </mesh>
  )
}

// Set frame loop
function Component() {
  const setFrameloop = useThree((state) => state.setFrameloop)

  useEffect(() => {
    setFrameloop('demand') // Switch to on-demand rendering
  }, [])

  return null
}
```

---

### useLoader

Load assets with automatic caching and Suspense integration.

```typescript
useLoader<T>(
  loader: LoaderConstructor<T>,
  url: string | string[],
  extensions?: (loader: LoaderProto<T>) => void,
  onProgress?: (event: ProgressEvent) => void
): T | T[]

// Static methods
useLoader.preload<T>(
  loader: LoaderConstructor<T>,
  url: string | string[],
  extensions?: (loader: LoaderProto<T>) => void
): void

useLoader.clear<T>(
  loader: LoaderConstructor<T>,
  url: string | string[]
): void
```

**Examples**:

```jsx
import { useLoader } from '@react-three/fiber'
import { TextureLoader, GLTFLoader } from 'three'

// Load texture
function TexturedBox() {
  const texture = useLoader(TextureLoader, '/texture.jpg')

  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial map={texture} />
    </mesh>
  )
}

// Load GLTF model
function Model() {
  const gltf = useLoader(GLTFLoader, '/model.glb')
  return <primitive object={gltf.scene} />
}

// Load multiple assets
function Scene() {
  const [texture1, texture2, texture3] = useLoader(TextureLoader, [
    '/tex1.jpg',
    '/tex2.jpg',
    '/tex3.jpg'
  ])

  return (
    <>
      <mesh><meshStandardMaterial map={texture1} /></mesh>
      <mesh><meshStandardMaterial map={texture2} /></mesh>
      <mesh><meshStandardMaterial map={texture3} /></mesh>
    </>
  )
}

// Loader extensions (e.g., DRACO compression)
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader'

function CompressedModel() {
  const gltf = useLoader(
    GLTFLoader,
    '/compressed.glb',
    (loader) => {
      const dracoLoader = new DRACOLoader()
      dracoLoader.setDecoderPath('/draco/')
      loader.setDRACOLoader(dracoLoader)
    }
  )

  return <primitive object={gltf.scene} />
}

// Progress tracking
function ModelWithProgress() {
  const [progress, setProgress] = useState(0)

  const gltf = useLoader(
    GLTFLoader,
    '/large-model.glb',
    undefined,
    (event) => {
      setProgress((event.loaded / event.total) * 100)
    }
  )

  return <primitive object={gltf.scene} />
}

// Pre-loading
function Preloader() {
  useEffect(() => {
    useLoader.preload(GLTFLoader, '/model.glb')
    useLoader.preload(TextureLoader, '/texture.jpg')
  }, [])

  return null
}

// Clear cache
function Component() {
  useEffect(() => {
    return () => {
      useLoader.clear(GLTFLoader, '/model.glb')
    }
  }, [])
}
```

---

### useGraph

Access GLTF scene graph with typed nodes and materials.

```typescript
useGraph(object: Object3D): {
  nodes: { [name: string]: Object3D }
  materials: { [name: string]: Material }
}
```

**Example**:

```jsx
import { useLoader } from '@react-three/fiber'
import { useGraph } from '@react-three/fiber'
import { GLTFLoader } from 'three'

function Model() {
  const gltf = useLoader(GLTFLoader, '/model.glb')
  const { nodes, materials } = useGraph(gltf.scene)

  return (
    <group>
      <mesh geometry={nodes.Mesh.geometry} material={materials.Material} />
      <mesh geometry={nodes.OtherMesh.geometry}>
        <meshStandardMaterial color="red" />
      </mesh>
    </group>
  )
}
```

---

## Events

R3F supports pointer events on any Object3D.

### Supported Events

```typescript
// Pointer events
onPointerOver?: (event: ThreeEvent<PointerEvent>) => void
onPointerOut?: (event: ThreeEvent<PointerEvent>) => void
onPointerEnter?: (event: ThreeEvent<PointerEvent>) => void
onPointerLeave?: (event: ThreeEvent<PointerEvent>) => void
onPointerMove?: (event: ThreeEvent<PointerEvent>) => void
onPointerDown?: (event: ThreeEvent<PointerEvent>) => void
onPointerUp?: (event: ThreeEvent<PointerEvent>) => void
onPointerCancel?: (event: ThreeEvent<PointerEvent>) => void
onPointerMissed?: (event: MouseEvent) => void

// Click events
onClick?: (event: ThreeEvent<MouseEvent>) => void
onContextMenu?: (event: ThreeEvent<MouseEvent>) => void
onDoubleClick?: (event: ThreeEvent<MouseEvent>) => void

// Wheel event
onWheel?: (event: ThreeEvent<WheelEvent>) => void
```

### ThreeEvent Object

```typescript
interface ThreeEvent<T> extends Omit<T, 'target'> {
  // Three.js specific
  intersections: Intersection[]
  object: Object3D
  eventObject: Object3D
  unprojectedPoint: Vector3
  ray: Ray
  camera: Camera
  sourceEvent: T
  delta: number

  // Helpers
  stopPropagation: () => void
  nativeEvent: T
  pointer: Vector2
  pointerId: number
  distance: number
  point: Vector3
  uv: Vector2
  face: Face | null
  faceIndex: number | null
}
```

### Examples

```jsx
// Basic click handler
<mesh onClick={(e) => console.log('Clicked!', e.point)}>
  <boxGeometry />
  <meshStandardMaterial />
</mesh>

// Hover states
function InteractiveBox() {
  const [hovered, setHovered] = useState(false)

  return (
    <mesh
      onPointerOver={(e) => {
        e.stopPropagation()
        setHovered(true)
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={(e) => {
        setHovered(false)
        document.body.style.cursor = 'auto'
      }}
    >
      <boxGeometry />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
    </mesh>
  )
}

// Stop event propagation
<group onClick={(e) => e.stopPropagation()}>
  <mesh onClick={() => console.log('Mesh clicked')} />
  <mesh onClick={() => console.log('This will also fire without stopPropagation')} />
</group>

// Access intersection data
<mesh
  onClick={(e) => {
    console.log('Hit point:', e.point)
    console.log('Hit face:', e.face)
    console.log('UV coordinates:', e.uv)
    console.log('Distance from camera:', e.distance)
    console.log('All intersections:', e.intersections)
  }}
>
  <sphereGeometry />
  <meshStandardMaterial />
</mesh>

// Pointer missed (clicked on empty space)
<Canvas onPointerMissed={() => console.log('Clicked on background')}>
  <mesh />
</Canvas>
```

---

## Three.js Object Props

R3F translates JSX props to Three.js object properties.

### Prop Mapping

```jsx
// Array notation → .set()
<mesh position={[1, 2, 3]} />  // mesh.position.set(1, 2, 3)
<mesh rotation={[0, Math.PI, 0]} />  // mesh.rotation.set(0, Math.PI, 0)
<mesh scale={[2, 2, 2]} />  // mesh.scale.set(2, 2, 2)

// Dash notation (axis-specific)
<mesh position-x={1} position-y={2} position-z={3} />
<mesh scale-x={2} scale-y={1} />

// Direct property assignment
<mesh visible={false} />  // mesh.visible = false
<mesh castShadow receiveShadow />  // mesh.castShadow = true, mesh.receiveShadow = true

// Constructor arguments
<boxGeometry args={[1, 1, 1]} />  // new BoxGeometry(1, 1, 1)
<meshStandardMaterial args={[{ color: 'red' }]} />  // new MeshStandardMaterial({ color: 'red' })

// Attach to specific parent property
<mesh>
  <meshStandardMaterial attach="material" />  // mesh.material = material
</mesh>

// Nested properties
<meshStandardMaterial color="red" roughness={0.5} metalness={0.8} />

// Set (for Vector-like properties)
<pointLight position={[10, 10, 10]} />
```

### Special Props

```jsx
// attach: Attach to parent property
<mesh>
  <meshStandardMaterial attach="material" />
  <boxGeometry attach="geometry" />
</mesh>

// attach-array: Attach to array index
<group>
  <mesh attach="children-0" />
  <mesh attach="children-1" />
</group>

// dispose: Control automatic disposal
<mesh dispose={null}>  {/* Never dispose */}
  <boxGeometry />
  <meshStandardMaterial />
</mesh>

// args: Constructor arguments
<sphereGeometry args={[1, 32, 32]} />  // radius, widthSegments, heightSegments

// object: Pass pre-existing Three.js object
<primitive object={myThreeJsObject} />

// ref: Get reference to underlying Three.js object
<mesh ref={meshRef} />
```

---

## Drei Helpers

Essential Drei components and hooks.

### OrbitControls

```typescript
interface OrbitControlsProps {
  makeDefault?: boolean
  camera?: Camera
  domElement?: HTMLElement
  target?: Vector3
  enableDamping?: boolean
  dampingFactor?: number
  enableZoom?: boolean
  enableRotate?: boolean
  enablePan?: boolean
  minDistance?: number
  maxDistance?: number
  minPolarAngle?: number
  maxPolarAngle?: number
  onChange?: (e?: Event) => void
  onStart?: (e?: Event) => void
  onEnd?: (e?: Event) => void
}
```

```jsx
import { OrbitControls } from '@react-three/drei'

<OrbitControls
  makeDefault
  enableDamping
  dampingFactor={0.05}
  minDistance={3}
  maxDistance={20}
  maxPolarAngle={Math.PI / 2}
  target={[0, 1, 0]}
/>
```

### Environment

```jsx
import { Environment } from '@react-three/drei'

// Preset HDRI
<Environment preset="sunset" background />

// Custom HDRI
<Environment files="/hdri.hdr" />

// Ground reflection
<Environment preset="city" ground={{ height: 15, radius: 60, scale: 100 }} />
```

### useGLTF

```jsx
import { useGLTF } from '@react-three/drei'

function Model() {
  const { scene, nodes, materials } = useGLTF('/model.glb')
  return <primitive object={scene} />
}

// Pre-load
useGLTF.preload('/model.glb')
```

### Text & Text3D

```jsx
import { Text, Text3D } from '@react-three/drei'

// 2D billboard text
<Text
  position={[0, 2, 0]}
  fontSize={1}
  color="white"
  anchorX="center"
  anchorY="middle"
  maxWidth={5}
  lineHeight={1}
  letterSpacing={0.02}
  textAlign="center"
  font="/fonts/font.woff"
  outlineWidth={0.1}
  outlineColor="#000000"
>
  Hello World
</Text>

// 3D extruded text
<Text3D
  font="/fonts/helvetiker_regular.typeface.json"
  size={1}
  height={0.2}
  curveSegments={12}
  bevelEnabled
  bevelThickness={0.02}
  bevelSize={0.02}
  bevelOffset={0}
  bevelSegments={5}
>
  3D Text
  <meshNormalMaterial />
</Text3D>
```

### Center & Bounds

```jsx
import { Center, Bounds, useBounds } from '@react-three/drei'

// Auto-center
<Center>
  <Model />
</Center>

// Auto-fit camera
<Bounds fit clip observe margin={1.2}>
  <Model />
</Bounds>

// Manual control
function SelectToZoom() {
  const bounds = useBounds()

  return (
    <mesh onClick={(e) => {
      e.stopPropagation()
      bounds.refresh(e.object).fit()
    }}>
      <boxGeometry />
      <meshStandardMaterial />
    </mesh>
  )
}
```

### Html

```jsx
import { Html } from '@react-three/drei'

<mesh>
  <boxGeometry />
  <meshStandardMaterial />

  <Html
    position={[0, 1, 0]}
    center
    distanceFactor={10}
    occlude
    transform
    sprite
  >
    <div className="annotation">Label</div>
  </Html>
</mesh>
```

### ScrollControls

```jsx
import { ScrollControls, Scroll, useScroll } from '@react-three/drei'

function Scene() {
  const scroll = useScroll()
  const meshRef = useRef()

  useFrame(() => {
    const offset = scroll.offset // 0-1
    meshRef.current.position.y = offset * 10
  })

  return <mesh ref={meshRef}>...</mesh>
}

<Canvas>
  <ScrollControls pages={3} damping={0.5}>
    <Scroll>
      <Scene />
    </Scroll>
    <Scroll html>
      <h1>HTML Content</h1>
    </Scroll>
  </ScrollControls>
</Canvas>
```

### ContactShadows

```jsx
import { ContactShadows } from '@react-three/drei'

<ContactShadows
  position={[0, -0.8, 0]}
  opacity={0.5}
  scale={10}
  blur={1}
  far={10}
  resolution={256}
  color="#000000"
/>
```

### Sky

```jsx
import { Sky } from '@react-three/drei'

<Sky
  distance={450000}
  sunPosition={[0, 1, 0]}
  inclination={0}
  azimuth={0.25}
  rayleigh={2}
  turbidity={10}
  mieCoefficient={0.005}
  mieDirectionalG={0.8}
/>
```

### Stars

```jsx
import { Stars } from '@react-three/drei'

<Stars
  radius={100}
  depth={50}
  count={5000}
  factor={4}
  saturation={0}
  fade
  speed={1}
/>
```

---

## Performance Helpers (Drei)

### AdaptiveDpr

```jsx
import { AdaptiveDpr } from '@react-three/drei'

<AdaptiveDpr pixelated />
```

### AdaptiveEvents

```jsx
import { AdaptiveEvents } from '@react-three/drei'

<AdaptiveEvents />
```

### PerformanceMonitor

```jsx
import { PerformanceMonitor } from '@react-three/drei'

<PerformanceMonitor
  onIncline={() => console.log('Performance improved')}
  onDecline={() => console.log('Performance degraded')}
  onFallback={() => console.log('Fallback triggered')}
  onChange={({ factor }) => console.log('Factor:', factor)}
  flipflops={3}
  bounds={(refreshRate) => [50, 90]}
>
  <Scene />
</PerformanceMonitor>
```

### Preload

```jsx
import { Preload } from '@react-three/drei'

<Canvas>
  <Scene />
  <Preload all />  {/* Preload all assets */}
</Canvas>
```

---

## Resources

- [Official R3F Docs](https://docs.pmnd.rs/react-three-fiber)
- [Drei Documentation](https://github.com/pmndrs/drei)
- [Three.js Documentation](https://threejs.org/docs/)
- [R3F Examples](https://docs.pmnd.rs/react-three-fiber/examples)



===== FILE: plugins/individual/react-three-fiber/agents/react-three-fiber-architect.md =====

# React Three Fiber Architect

## Role

Expert 3D/graphics architect specializing in React Three Fiber scene design, optimization, and best practices.

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
3. Implement best practices from React Three Fiber ecosystem
4. Optimize for target platforms and devices
5. Provide detailed implementation guidance

## Tools

This agent has access to:
- React Three Fiber skill knowledge
- Optimization checklists and patterns
- Performance profiling guidance
- Asset pipeline recommendations



===== FILE: plugins/individual/react-three-fiber/commands/component_generator.md =====

# /react-three-fiber-component_generator

React Three Fiber - Component Generator

## Description

Executes the component_generator script for React Three Fiber.

## Usage

```bash
/react-three-fiber-component_generator
```

## Implementation

This command runs the `component_generator.py` script from the React Three Fiber skill, which provides automated assistance for component generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/react-three-fiber/commands/scene_setup.md =====

# /react-three-fiber-scene_setup

React Three Fiber - Scene Setup

## Description

Executes the scene_setup script for React Three Fiber.

## Usage

```bash
/react-three-fiber-scene_setup
```

## Implementation

This command runs the `scene_setup.py` script from the React Three Fiber skill, which provides automated assistance for scene setup.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/scripts/component_generator.py =====

```py
#!/usr/bin/env python3
"""
React Three Fiber Component Generator
======================================

Generates R3F component boilerplate for common patterns with TypeScript support.

Usage:
    python3 component_generator.py --type box --name MyBox --output MyBox.jsx
    python3 component_generator.py --type model --name Scene --props "modelPath,scale" --typescript
    python3 component_generator.py --type interactive --name Button --events "onClick,onPointerOver"
    python3 component_generator.py --type animated --name FloatingCube --animation "rotation,position"

Component Types:
    - box: Basic mesh with geometry and material
    - sphere: Sphere mesh component
    - model: GLTF model loader with Suspense
    - interactive: Interactive mesh with pointer events
    - animated: Animated component with useFrame
    - group: Group container with multiple children
    - instanced: Instanced mesh for performance
    - camera-rig: Camera control component
    - lighting: Lighting setup component
    - environment: Environment with Drei helpers
    - scene: Complete scene setup
    - custom: Custom component template

Options:
    --type: Component type (required)
    --name: Component name (default: Component)
    --output: Output file path (default: stdout)
    --typescript: Generate TypeScript component
    --props: Comma-separated list of props
    --events: Comma-separated list of event handlers
    --animation: Comma-separated list of animation targets (rotation, position, scale)
    --drei: Include Drei helper imports
    --framework: Target framework (vanilla, nextjs, vite)
"""

import argparse
import sys
from typing import List, Dict, Optional


class R3FComponentGenerator:
    """Generate React Three Fiber component boilerplate."""

    def __init__(
        self,
        component_type: str,
        name: str = "Component",
        typescript: bool = False,
        props: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        animation: Optional[List[str]] = None,
        drei: bool = False,
        framework: str = "vanilla"
    ):
        self.component_type = component_type
        self.name = name
        self.typescript = typescript
        self.props = props or []
        self.events = events or []
        self.animation = animation or []
        self.drei = drei
        self.framework = framework

    def generate(self) -> str:
        """Generate component code."""
        generators = {
            'box': self._generate_box,
            'sphere': self._generate_sphere,
            'model': self._generate_model,
            'interactive': self._generate_interactive,
            'animated': self._generate_animated,
            'group': self._generate_group,
            'instanced': self._generate_instanced,
            'camera-rig': self._generate_camera_rig,
            'lighting': self._generate_lighting,
            'environment': self._generate_environment,
            'scene': self._generate_scene,
            'custom': self._generate_custom,
        }

        generator = generators.get(self.component_type)
        if not generator:
            raise ValueError(f"Unknown component type: {self.component_type}")

        return generator()

    def _get_imports(self, additional: List[str] = None) -> str:
        """Generate import statements."""
        imports = ["import { useRef } from 'react'"]

        r3f_imports = ["useFrame", "useThree"]
        if additional:
            r3f_imports.extend(additional)
        imports.append(f"import {{ {', '.join(set(r3f_imports))} }} from '@react-three/fiber'")

        if self.drei:
            drei_imports = ["OrbitControls", "Environment", "useGLTF"]
            imports.append(f"import {{ {', '.join(drei_imports)} }} from '@react-three/drei'")

        if self.typescript:
            imports.append("import * as THREE from 'three'")

        return "\n".join(imports)

    def _get_props_interface(self) -> str:
        """Generate TypeScript props interface."""
        if not self.typescript or not self.props:
            return ""

        props_lines = []
        for prop in self.props:
            # Infer types from common prop names
            if prop in ['position', 'rotation', 'scale']:
                props_lines.append(f"  {prop}?: [number, number, number]")
            elif prop in ['color', 'modelPath', 'name']:
                props_lines.append(f"  {prop}?: string")
            elif prop in ['visible', 'castShadow', 'receiveShadow']:
                props_lines.append(f"  {prop}?: boolean")
            elif prop.endswith('Ref'):
                props_lines.append(f"  {prop}?: React.RefObject<THREE.Mesh>")
            else:
                props_lines.append(f"  {prop}?: any")

        return f"\ninterface {self.name}Props {{\n" + "\n".join(props_lines) + "\n}\n"

    def _get_props_signature(self) -> str:
        """Generate props parameter signature."""
        if not self.props:
            return "()"

        if self.typescript:
            return f"({{ {', '.join(self.props)} }}: {self.name}Props)"
        else:
            return f"({{ {', '.join(self.props)} }})"

    def _get_event_handlers(self) -> str:
        """Generate event handler props."""
        if not self.events:
            return ""

        handlers = []
        for event in self.events:
            if event.startswith('on'):
                handler_name = event[2:].lower()
                handlers.append(f'{event}={(e) => console.log("{handler_name}", e)}')
            else:
                handlers.append(f'on{event.capitalize()}={(e) => console.log("{event}", e)}')

        return "\n      ".join(handlers)

    def _generate_box(self) -> str:
        """Generate basic box component."""
        imports = self._get_imports()
        props_interface = self._get_props_interface()
        props_sig = self._get_props_signature()

        default_props = ["position = [0, 0, 0]", "color = 'orange'"]
        props_str = ', '.join(default_props + self.props)

        return f"""{imports}
{props_interface}
export function {self.name}{props_sig} {{
  return (
    <mesh position={{position}}>
      <boxGeometry args={{[1, 1, 1]}} />
      <meshStandardMaterial color={{color}} />
    </mesh>
  )
}}
"""

    def _generate_sphere(self) -> str:
        """Generate sphere component."""
        imports = self._get_imports()
        props_interface = self._get_props_interface()
        props_sig = self._get_props_signature()

        return f"""{imports}
{props_interface}
export function {self.name}{props_sig} {{
  const meshRef = useRef{f'<THREE.Mesh>(null)' if self.typescript else '()'}

  return (
    <mesh ref={{meshRef}}>
      <sphereGeometry args={{[1, 32, 32]}} />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  )
}}
"""

    def _generate_model(self) -> str:
        """Generate GLTF model loader component."""
        imports = ["import { Suspense } from 'react'"]
        imports.append("import { useGLTF } from '@react-three/drei'")
        if self.typescript:
            imports.append("import { GLTF } from 'three-stdlib'")

        props_interface = ""
        if self.typescript:
            props_interface = f"""
interface {self.name}Props {{
  modelPath: string
  position?: [number, number, number]
  scale?: number | [number, number, number]
}}
"""

        return f"""{chr(10).join(imports)}
{props_interface}
function Model({{ modelPath, position = [0, 0, 0], scale = 1 }}{f': {self.name}Props' if self.typescript else ''}) {{
  const {{ scene }} = useGLTF(modelPath)

  return <primitive object={{scene}} position={{position}} scale={{scale}} />
}}

// Preload the model
useGLTF.preload('/path/to/model.glb')

export function {self.name}({{ modelPath = '/model.glb', ...props }}{f': {self.name}Props' if self.typescript else ''}) {{
  return (
    <Suspense fallback={{null}}>
      <Model modelPath={{modelPath}} {{...props}} />
    </Suspense>
  )
}}
"""

    def _generate_interactive(self) -> str:
        """Generate interactive component with pointer events."""
        imports = self._get_imports() + "\nimport { useState } from 'react'"
        props_interface = self._get_props_interface()
        props_sig = self._get_props_signature()

        event_handlers = self._get_event_handlers() or """onClick={(e) => {
        e.stopPropagation()
        setActive(!active)
      }}
      onPointerOver={(e) => {
        e.stopPropagation()
        setHovered(true)
      }}
      onPointerOut={(e) => setHovered(false)}"""

        return f"""{imports}
{props_interface}
export function {self.name}{props_sig} {{
  const [hovered, setHovered] = useState(false)
  const [active, setActive] = useState(false)

  return (
    <mesh
      scale={{active ? 1.5 : 1}}
      {event_handlers}>
      <boxGeometry args={{[1, 1, 1]}} />
      <meshStandardMaterial color={{hovered ? 'hotpink' : 'orange'}} />
    </mesh>
  )
}}
"""

    def _generate_animated(self) -> str:
        """Generate animated component with useFrame."""
        imports = self._get_imports()
        props_interface = self._get_props_interface()
        props_sig = self._get_props_signature()

        # Generate animation code based on targets
        animation_code = []
        if 'rotation' in self.animation or not self.animation:
            animation_code.append("meshRef.current.rotation.x += delta")
            animation_code.append("meshRef.current.rotation.y += delta * 0.5")
        if 'position' in self.animation:
            animation_code.append("meshRef.current.position.y = Math.sin(state.clock.elapsedTime) * 2")
        if 'scale' in self.animation:
            animation_code.append("meshRef.current.scale.x = 1 + Math.sin(state.clock.elapsedTime) * 0.3")

        if not animation_code:
            animation_code = ["// Add your animation logic here"]

        return f"""{imports}
{props_interface}
export function {self.name}{props_sig} {{
  const meshRef = useRef{f'<THREE.Mesh>(null!)' if self.typescript else '()'}

  useFrame((state, delta) => {{
    {chr(10).join(f'    {line}' for line in animation_code)}
  }})

  return (
    <mesh ref={{meshRef}}>
      <boxGeometry args={{[1, 1, 1]}} />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}}
"""

    def _generate_group(self) -> str:
        """Generate group component."""
        imports = self._get_imports()
        props_interface = self._get_props_interface()
        props_sig = self._get_props_signature()

        return f"""{imports}
{props_interface}
export function {self.name}{props_sig} {{
  const groupRef = useRef{f'<THREE.Group>(null!)' if self.typescript else '()'}

  useFrame((state, delta) => {{
    groupRef.current.rotation.y += delta * 0.5
  }})

  return (
    <group ref={{groupRef}}>
      <mesh position={{[-2, 0, 0]}}>
        <boxGeometry />
        <meshStandardMaterial color="orange" />
      </mesh>
      <mesh position={{[2, 0, 0]}}>
        <sphereGeometry />
        <meshStandardMaterial color="hotpink" />
      </mesh>
    </group>
  )
}}
"""

    def _generate_instanced(self) -> str:
        """Generate instanced mesh component for performance."""
        imports = ["import { useRef, useMemo } from 'react'"]
        imports.append("import { useFrame } from '@react-three/fiber'")
        if self.typescript:
            imports.append("import * as THREE from 'three'")

        return f"""{chr(10).join(imports)}

export function {self.name}({{ count = 1000 }}) {{
  const meshRef = useRef{f'<THREE.InstancedMesh>(null!)' if self.typescript else '()'}

  const particles = useMemo(() => {{
    const temp = []
    for (let i = 0; i < count; i++) {{
      const t = Math.random() * 100
      const factor = 20 + Math.random() * 100
      const speed = 0.01 + Math.random() / 200
      const x = Math.random() * 40 - 20
      const y = Math.random() * 40 - 20
      const z = Math.random() * 40 - 20
      temp.push({{ t, factor, speed, x, y, z, mx: 0, my: 0 }})
    }}
    return temp
  }}, [count])

  const dummy = useMemo(() => new THREE.Object3D(), [])

  useFrame(() => {{
    particles.forEach((particle, i) => {{
      let {{ t, factor, speed, x, y, z }} = particle
      t = particle.t += speed / 2
      const a = Math.cos(t) + Math.sin(t * 1) / 10
      const b = Math.sin(t) + Math.cos(t * 2) / 10
      const s = Math.cos(t)

      dummy.position.set(
        x + Math.cos((t / 10) * factor) + (Math.sin(t * 1) * factor) / 10,
        y + Math.sin((t / 10) * factor) + (Math.cos(t * 2) * factor) / 10,
        z + Math.cos((t / 10) * factor) + (Math.sin(t * 3) * factor) / 10
      )
      dummy.scale.set(s, s, s)
      dummy.rotation.set(s * 5, s * 5, s * 5)
      dummy.updateMatrix()

      meshRef.current.setMatrixAt(i, dummy.matrix)
    }})
    meshRef.current.instanceMatrix.needsUpdate = true
  }})

  return (
    <instancedMesh ref={{meshRef}} args={{[undefined, undefined, count]}}>
      <dodecahedronGeometry args={{[0.2, 0]}} />
      <meshPhongMaterial color="#ff4040" />
    </instancedMesh>
  )
}}
"""

    def _generate_camera_rig(self) -> str:
        """Generate camera rig component."""
        imports = ["import { useRef } from 'react'"]
        imports.append("import { useFrame } from '@react-three/fiber'")
        if self.typescript:
            imports.append("import * as THREE from 'three'")

        return f"""{chr(10).join(imports)}

export function {self.name}({{ children }}) {{
  const groupRef = useRef{f'<THREE.Group>(null!)' if self.typescript else '()'}

  useFrame((state) => {{
    // Smooth camera follow
    groupRef.current.position.lerp(
      new THREE.Vector3(
        state.mouse.x * 2,
        state.mouse.y * 2,
        10
      ),
      0.05
    )

    // Look at center
    groupRef.current.lookAt(0, 0, 0)
  }})

  return (
    <group ref={{groupRef}}>
      {{children}}
    </group>
  )
}}
"""

    def _generate_lighting(self) -> str:
        """Generate lighting setup component."""
        return f"""import {{ useRef }} from 'react'
import {{ useFrame }} from '@react-three/fiber'

export function {self.name}() {{
  const lightRef = useRef()

  useFrame((state) => {{
    const time = state.clock.elapsedTime
    lightRef.current.position.x = Math.sin(time) * 5
    lightRef.current.position.z = Math.cos(time) * 5
  }})

  return (
    <>
      <ambientLight intensity={{0.5}} />
      <directionalLight
        ref={{lightRef}}
        position={{[5, 5, 5]}}
        intensity={{1}}
        castShadow
        shadow-mapSize={{[1024, 1024]}}
        shadow-camera-far={{50}}
        shadow-camera-left={{-10}}
        shadow-camera-right={{10}}
        shadow-camera-top={{10}}
        shadow-camera-bottom={{-10}}
      />
      <pointLight position={{[-10, -10, -10]}} intensity={{0.5}} />
      <hemisphereLight intensity={{0.35}} groundColor="black" />
    </>
  )
}}
"""

    def _generate_environment(self) -> str:
        """Generate environment component with Drei helpers."""
        return f"""import {{ Environment, ContactShadows, Sky }} from '@react-three/drei'

export function {self.name}() {{
  return (
    <>
      <Environment preset="sunset" />
      <ContactShadows
        position={{[0, -1.4, 0]}}
        opacity={{0.75}}
        scale={{10}}
        blur={{2.5}}
        far={{4}}
      />
      <Sky sunPosition={{[100, 20, 100]}} />
    </>
  )
}}
"""

    def _generate_scene(self) -> str:
        """Generate complete scene setup."""
        return f"""import {{ Canvas }} from '@react-three/fiber'
import {{ OrbitControls, Environment, ContactShadows }} from '@react-three/drei'

function Scene() {{
  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={{0.5}} />
      <directionalLight position={{[5, 5, 5]}} intensity={{1}} castShadow />

      {/* 3D Objects */}
      <mesh position={{[0, 1, 0]}} castShadow>
        <boxGeometry args={{[1, 1, 1]}} />
        <meshStandardMaterial color="orange" />
      </mesh>

      {/* Ground */}
      <mesh rotation={{[-Math.PI / 2, 0, 0]}} position={{[0, 0, 0]}} receiveShadow>
        <planeGeometry args={{[10, 10]}} />
        <meshStandardMaterial color="#808080" />
      </mesh>

      {/* Environment */}
      <Environment preset="city" />
      <ContactShadows position={{[0, 0, 0]}} opacity={{0.5}} scale={{10}} blur={{1}} far={{10}} />

      {/* Camera Controls */}
      <OrbitControls makeDefault />
    </>
  )
}}

export function {self.name}() {{
  return (
    <Canvas shadows camera={{{{ position: [5, 5, 5], fov: 50 }}}}>
      <Scene />
    </Canvas>
  )
}}
"""

    def _generate_custom(self) -> str:
        """Generate custom component template."""
        imports = self._get_imports()
        props_interface = self._get_props_interface()
        props_sig = self._get_props_signature()

        return f"""{imports}
{props_interface}
export function {self.name}{props_sig} {{
  const meshRef = useRef{f'<THREE.Mesh>(null!)' if self.typescript else '()'}

  // Add your custom logic here
  useFrame((state, delta) => {{
    // Animation logic
  }})

  return (
    <mesh ref={{meshRef}}>
      <boxGeometry args={{[1, 1, 1]}} />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}}
"""


def main():
    parser = argparse.ArgumentParser(
        description='Generate React Three Fiber component boilerplate',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--type',
        required=True,
        choices=['box', 'sphere', 'model', 'interactive', 'animated', 'group',
                 'instanced', 'camera-rig', 'lighting', 'environment', 'scene', 'custom'],
        help='Component type to generate'
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
        '--props',
        help='Comma-separated list of props'
    )

    parser.add_argument(
        '--events',
        help='Comma-separated list of event handlers (e.g., onClick,onPointerOver)'
    )

    parser.add_argument(
        '--animation',
        help='Comma-separated list of animation targets (rotation,position,scale)'
    )

    parser.add_argument(
        '--drei',
        action='store_true',
        help='Include Drei helper imports'
    )

    parser.add_argument(
        '--framework',
        default='vanilla',
        choices=['vanilla', 'nextjs', 'vite'],
        help='Target framework (default: vanilla)'
    )

    args = parser.parse_args()

    # Parse comma-separated lists
    props = args.props.split(',') if args.props else []
    events = args.events.split(',') if args.events else []
    animation = args.animation.split(',') if args.animation else []

    # Generate component
    generator = R3FComponentGenerator(
        component_type=args.type,
        name=args.name,
        typescript=args.typescript,
        props=props,
        events=events,
        animation=animation,
        drei=args.drei,
        framework=args.framework
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


===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/scripts/scene_setup.py =====

```py
#!/usr/bin/env python3
"""
React Three Fiber Scene Setup Tool
===================================

Interactive CLI tool to generate complete R3F scene boilerplate with common patterns.

Usage:
    python3 scene_setup.py
    python3 scene_setup.py --preset standard --output src/Scene.jsx
    python3 scene_setup.py --preset performance --typescript
    python3 scene_setup.py --interactive

Presets:
    - minimal: Basic scene with lighting and controls
    - standard: Complete scene with environment, shadows, controls
    - performance: Optimized scene with adaptive performance
    - creative: Artistic scene with post-processing effects
    - product: Product viewer setup with proper lighting
    - game: Game-ready scene with physics

Features:
    - Lighting configurations (ambient, directional, point, hemisphere, HDRI)
    - Camera setups (perspective, orthographic)
    - Controls (OrbitControls, FlyControls, PointerLockControls)
    - Environment (Drei presets, HDRI, Sky)
    - Shadows (PCF, VSM, contact shadows)
    - Post-processing (bloom, DOF, SSAO, chromatic aberration)
    - Performance optimizations (adaptive DPR, LOD, instancing)
    - Physics integration (Rapier, Cannon)
"""

import argparse
import sys
from typing import Dict, List, Optional


class R3FSceneSetup:
    """Generate React Three Fiber scene setup."""

    PRESETS = {
        'minimal': {
            'lighting': ['ambient', 'directional'],
            'controls': ['orbit'],
            'environment': None,
            'shadows': False,
            'post_processing': False,
            'performance': False,
        },
        'standard': {
            'lighting': ['ambient', 'directional', 'hemisphere'],
            'controls': ['orbit'],
            'environment': 'drei-preset',
            'shadows': True,
            'post_processing': False,
            'performance': False,
        },
        'performance': {
            'lighting': ['ambient', 'directional'],
            'controls': ['orbit'],
            'environment': None,
            'shadows': False,
            'post_processing': False,
            'performance': True,
        },
        'creative': {
            'lighting': ['ambient', 'directional', 'point'],
            'controls': ['orbit'],
            'environment': 'drei-preset',
            'shadows': True,
            'post_processing': True,
            'performance': False,
        },
        'product': {
            'lighting': ['ambient', 'directional', 'point', 'hemisphere'],
            'controls': ['orbit'],
            'environment': 'drei-preset',
            'shadows': True,
            'post_processing': False,
            'performance': False,
        },
        'game': {
            'lighting': ['ambient', 'directional'],
            'controls': ['pointer-lock'],
            'environment': None,
            'shadows': True,
            'post_processing': False,
            'performance': True,
            'physics': True,
        },
    }

    def __init__(
        self,
        preset: str = 'standard',
        typescript: bool = False,
        lighting: Optional[List[str]] = None,
        controls: Optional[str] = None,
        environment: Optional[str] = None,
        shadows: bool = False,
        post_processing: bool = False,
        performance: bool = False,
        physics: bool = False,
    ):
        preset_config = self.PRESETS.get(preset, self.PRESETS['standard'])

        self.typescript = typescript
        self.lighting = lighting or preset_config['lighting']
        self.controls = controls or preset_config['controls'][0]
        self.environment = environment if environment is not None else preset_config['environment']
        self.shadows = shadows or preset_config['shadows']
        self.post_processing = post_processing or preset_config.get('post_processing', False)
        self.performance = performance or preset_config.get('performance', False)
        self.physics = physics or preset_config.get('physics', False)

    def generate(self) -> str:
        """Generate complete scene code."""
        imports = self._generate_imports()
        lighting_component = self._generate_lighting()
        environment_component = self._generate_environment()
        controls_component = self._generate_controls()
        post_processing_component = self._generate_post_processing()
        performance_component = self._generate_performance()
        physics_component = self._generate_physics()
        scene_component = self._generate_scene_component()
        canvas_wrapper = self._generate_canvas_wrapper()

        return f"""{imports}

{lighting_component}

{environment_component}

{controls_component}

{post_processing_component}

{performance_component}

{physics_component}

{scene_component}

{canvas_wrapper}
"""

    def _generate_imports(self) -> str:
        """Generate import statements."""
        imports = ["import { Canvas } from '@react-three/fiber'"]

        drei_imports = []

        if self.controls == 'orbit':
            drei_imports.append('OrbitControls')
        elif self.controls == 'fly':
            drei_imports.append('FlyControls')
        elif self.controls == 'pointer-lock':
            drei_imports.append('PointerLockControls')

        if self.environment:
            drei_imports.append('Environment')
        if self.shadows and self.environment == 'drei-preset':
            drei_imports.append('ContactShadows')
        if self.environment == 'sky':
            drei_imports.append('Sky')
        if self.performance:
            drei_imports.extend(['AdaptiveDpr', 'AdaptiveEvents', 'PerformanceMonitor'])

        if drei_imports:
            imports.append(f"import {{ {', '.join(drei_imports)} }} from '@react-three/drei'")

        if self.post_processing:
            imports.append("import { EffectComposer, Bloom, DepthOfField } from '@react-three/postprocessing'")

        if self.physics:
            imports.append("import { Physics, RigidBody } from '@react-three/rapier'")

        if self.typescript:
            imports.append("import * as THREE from 'three'")

        return "\n".join(imports)

    def _generate_lighting(self) -> str:
        """Generate lighting setup component."""
        lights = []

        if 'ambient' in self.lighting:
            lights.append("      <ambientLight intensity={0.5} />")

        if 'directional' in self.lighting:
            shadow_props = """
        castShadow
        shadow-mapSize={[1024, 1024]}
        shadow-camera-far={50}
        shadow-camera-left={-10}
        shadow-camera-right={10}
        shadow-camera-top={10}
        shadow-camera-bottom={-10}""" if self.shadows else ""
            lights.append(f"""      <directionalLight
        position={{[5, 5, 5]}}
        intensity={{1}}{shadow_props}
      />""")

        if 'point' in self.lighting:
            lights.append("      <pointLight position={[-10, -10, -10]} intensity={0.5} />")

        if 'hemisphere' in self.lighting:
            lights.append('      <hemisphereLight intensity={0.35} groundColor="black" />')

        if 'spot' in self.lighting:
            lights.append("""      <spotLight
        position={[10, 10, 10]}
        angle={0.15}
        penumbra={1}
        intensity={1}
        castShadow
      />""")

        lighting_code = "\n".join(lights) if lights else "      {/* Add your lighting here */}"

        return f"""function Lighting() {{
  return (
    <>
{lighting_code}
    </>
  )
}}"""

    def _generate_environment(self) -> str:
        """Generate environment setup."""
        if not self.environment:
            return "// No environment configured"

        if self.environment == 'drei-preset':
            shadows = ""
            if self.shadows:
                shadows = """
      <ContactShadows
        position={[0, -1.4, 0]}
        opacity={0.75}
        scale={10}
        blur={2.5}
        far={4}
      />"""

            return f"""function EnvironmentSetup() {{
  return (
    <>
      <Environment preset="sunset" />{shadows}
    </>
  )
}}"""

        elif self.environment == 'sky':
            return """function EnvironmentSetup() {
  return <Sky sunPosition={[100, 20, 100]} />
}"""

        elif self.environment == 'hdri':
            return """function EnvironmentSetup() {
  return <Environment files="/path/to/hdri.hdr" />
}"""

        return "// Environment not configured"

    def _generate_controls(self) -> str:
        """Generate camera controls."""
        if self.controls == 'orbit':
            return """function Controls() {
  return <OrbitControls makeDefault />
}"""
        elif self.controls == 'fly':
            return """function Controls() {
  return <FlyControls makeDefault />
}"""
        elif self.controls == 'pointer-lock':
            return """function Controls() {
  return <PointerLockControls makeDefault />
}"""
        else:
            return "// No controls configured"

    def _generate_post_processing(self) -> str:
        """Generate post-processing effects."""
        if not self.post_processing:
            return "// Post-processing disabled"

        return """function Effects() {
  return (
    <EffectComposer>
      <Bloom luminanceThreshold={0} luminanceSmoothing={0.9} height={300} />
      <DepthOfField focusDistance={0} focalLength={0.02} bokehScale={2} height={480} />
    </EffectComposer>
  )
}"""

    def _generate_performance(self) -> str:
        """Generate performance optimization components."""
        if not self.performance:
            return "// Performance optimizations disabled"

        return """function PerformanceOptimizations() {
  return (
    <>
      <AdaptiveDpr pixelated />
      <AdaptiveEvents />
      <PerformanceMonitor>
        {/* Monitor performance and adjust quality */}
      </PerformanceMonitor>
    </>
  )
}"""

    def _generate_physics(self) -> str:
        """Generate physics setup."""
        if not self.physics:
            return "// Physics disabled"

        return """function PhysicsWorld({ children }) {
  return (
    <Physics gravity={[0, -9.81, 0]}>
      {children}
    </Physics>
  )
}"""

    def _generate_scene_component(self) -> str:
        """Generate main scene component."""
        components = []

        components.append("      <Lighting />")

        if self.environment:
            components.append("      <EnvironmentSetup />")

        if self.performance:
            components.append("      <PerformanceOptimizations />")

        components.append("""
      {/* 3D Objects */}
      <mesh position={[0, 1, 0]} castShadow>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="orange" />
      </mesh>

      {/* Ground */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#808080" />
      </mesh>""")

        components.append("\n      <Controls />")

        if self.post_processing:
            components.append("      <Effects />")

        scene_content = "\n".join(components)

        if self.physics:
            return f"""function Scene() {{
  return (
    <PhysicsWorld>
{scene_content}
    </PhysicsWorld>
  )
}}"""
        else:
            return f"""function Scene() {{
  return (
    <>
{scene_content}
    </>
  )
}}"""

    def _generate_canvas_wrapper(self) -> str:
        """Generate Canvas wrapper component."""
        canvas_props = []

        if self.shadows:
            canvas_props.append("shadows")

        canvas_props.append("camera={{ position: [5, 5, 5], fov: 50 }}")

        if self.performance:
            canvas_props.append("dpr={[1, 2]}")
            canvas_props.append('frameloop="demand"')

        props_str = " ".join(canvas_props)

        return f"""export default function Experience() {{
  return (
    <Canvas {props_str}>
      <Scene />
    </Canvas>
  )
}}"""


def interactive_mode():
    """Run interactive mode to configure scene."""
    print("\n🎨 React Three Fiber Scene Setup - Interactive Mode\n")
    print("=" * 60)

    # Choose preset
    print("\nChoose a preset:")
    print("  1. minimal     - Basic scene with lighting and controls")
    print("  2. standard    - Complete scene with environment, shadows, controls")
    print("  3. performance - Optimized scene with adaptive performance")
    print("  4. creative    - Artistic scene with post-processing effects")
    print("  5. product     - Product viewer setup with proper lighting")
    print("  6. game        - Game-ready scene with physics")
    print("  7. custom      - Configure manually")

    preset_choice = input("\nSelect preset (1-7): ").strip()
    preset_map = {
        '1': 'minimal',
        '2': 'standard',
        '3': 'performance',
        '4': 'creative',
        '5': 'product',
        '6': 'game',
    }

    if preset_choice == '7':
        # Custom configuration
        print("\n📝 Custom Configuration\n")

        # Lighting
        print("Lighting types (comma-separated):")
        print("  ambient, directional, point, hemisphere, spot")
        lighting_input = input("Select lighting: ").strip()
        lighting = [l.strip() for l in lighting_input.split(',')] if lighting_input else ['ambient', 'directional']

        # Controls
        print("\nCamera controls:")
        print("  1. orbit    - OrbitControls (mouse drag rotation)")
        print("  2. fly      - FlyControls (keyboard navigation)")
        print("  3. pointer  - PointerLockControls (FPS-style)")
        controls_choice = input("Select controls (1-3): ").strip()
        controls_map = {'1': 'orbit', '2': 'fly', '3': 'pointer'}
        controls = controls_map.get(controls_choice, 'orbit')

        # Environment
        print("\nEnvironment:")
        print("  1. drei-preset - Use Drei environment preset")
        print("  2. sky         - Sky component")
        print("  3. none        - No environment")
        env_choice = input("Select environment (1-3): ").strip()
        env_map = {'1': 'drei-preset', '2': 'sky', '3': None}
        environment = env_map.get(env_choice, None)

        # Features
        shadows = input("\nEnable shadows? (y/n): ").strip().lower() == 'y'
        post_processing = input("Enable post-processing? (y/n): ").strip().lower() == 'y'
        performance = input("Enable performance optimizations? (y/n): ").strip().lower() == 'y'
        physics = input("Enable physics? (y/n): ").strip().lower() == 'y'

        setup = R3FSceneSetup(
            preset='standard',
            lighting=lighting,
            controls=controls,
            environment=environment,
            shadows=shadows,
            post_processing=post_processing,
            performance=performance,
            physics=physics,
        )
    else:
        preset = preset_map.get(preset_choice, 'standard')
        setup = R3FSceneSetup(preset=preset)

    # TypeScript
    typescript = input("\nGenerate TypeScript? (y/n): ").strip().lower() == 'y'
    setup.typescript = typescript

    # Output
    output_file = input("\nOutput file (leave empty for stdout): ").strip()

    print("\n🚀 Generating scene...\n")

    try:
        code = setup.generate()

        if output_file:
            with open(output_file, 'w') as f:
                f.write(code)
            print(f"✅ Scene generated → {output_file}")
        else:
            print(code)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Generate React Three Fiber scene setup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--preset',
        default='standard',
        choices=['minimal', 'standard', 'performance', 'creative', 'product', 'game'],
        help='Scene preset (default: standard)'
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
        '--lighting',
        help='Comma-separated lighting types (ambient,directional,point,hemisphere,spot)'
    )

    parser.add_argument(
        '--controls',
        choices=['orbit', 'fly', 'pointer-lock'],
        help='Camera controls type'
    )

    parser.add_argument(
        '--environment',
        choices=['drei-preset', 'sky', 'hdri', 'none'],
        help='Environment type'
    )

    parser.add_argument(
        '--shadows',
        action='store_true',
        help='Enable shadows'
    )

    parser.add_argument(
        '--post-processing',
        action='store_true',
        help='Enable post-processing effects'
    )

    parser.add_argument(
        '--performance',
        action='store_true',
        help='Enable performance optimizations'
    )

    parser.add_argument(
        '--physics',
        action='store_true',
        help='Enable physics'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )

    args = parser.parse_args()

    # Run interactive mode if requested
    if args.interactive or len(sys.argv) == 1:
        interactive_mode()
        return

    # Parse lighting
    lighting = None
    if args.lighting:
        lighting = [l.strip() for l in args.lighting.split(',')]

    # Parse environment
    environment = args.environment if args.environment != 'none' else None

    # Generate scene
    setup = R3FSceneSetup(
        preset=args.preset,
        typescript=args.typescript,
        lighting=lighting,
        controls=args.controls,
        environment=environment,
        shadows=args.shadows,
        post_processing=args.post_processing,
        performance=args.performance,
        physics=args.physics,
    )

    try:
        code = setup.generate()

        # Output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(code)
            print(f"✅ Scene generated → {args.output}")
        else:
            print(code)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/assets/examples/README.md =====

# React Three Fiber - Real-World Component Examples

A comprehensive collection of production-ready R3F component patterns and examples.

## Table of Contents

1. [GLTF Model Loading](#1-gltf-model-loading)
2. [Interactive Product Viewer](#2-interactive-product-viewer)
3. [Scroll-Based Animations](#3-scroll-based-animations)
4. [Particle System](#4-particle-system)
5. [Text 3D](#5-text-3d)
6. [Post-Processing Effects](#6-post-processing-effects)
7. [Physics Simulation](#7-physics-simulation)
8. [Camera Animations](#8-camera-animations)
9. [LOD (Level of Detail)](#9-lod-level-of-detail)
10. [Performance Monitoring](#10-performance-monitoring)

---

## 1. GLTF Model Loading

### Basic Model Loader

```jsx
import { useGLTF } from '@react-three/drei'
import { Suspense } from 'react'

function Model({ url, ...props }) {
  const { scene } = useGLTF(url)
  return <primitive object={scene} {...props} />
}

// Preload for faster initial load
useGLTF.preload('/models/scene.glb')

export default function Scene() {
  return (
    <Suspense fallback={<Loader />}>
      <Model url="/models/scene.glb" position={[0, 0, 0]} scale={0.5} />
    </Suspense>
  )
}

function Loader() {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshBasicMaterial wireframe color="white" />
    </mesh>
  )
}
```

### Model with Animations

```jsx
import { useGLTF, useAnimations } from '@react-three/drei'
import { useEffect, useRef } from 'react'

function AnimatedModel({ url }) {
  const group = useRef()
  const { scene, animations } = useGLTF(url)
  const { actions, names } = useAnimations(animations, group)

  useEffect(() => {
    // Play first animation
    actions[names[0]]?.play()
  }, [actions, names])

  return <primitive ref={group} object={scene} />
}

useGLTF.preload('/models/animated.glb')
```

### Model with Material Override

```jsx
import { useGLTF } from '@react-three/drei'
import { useEffect } from 'react'
import * as THREE from 'three'

function ModelWithCustomMaterial({ url }) {
  const { scene } = useGLTF(url)

  useEffect(() => {
    const customMaterial = new THREE.MeshStandardMaterial({
      color: '#ff6b6b',
      metalness: 0.8,
      roughness: 0.2,
    })

    scene.traverse((child) => {
      if (child.isMesh) {
        child.material = customMaterial
        child.castShadow = true
        child.receiveShadow = true
      }
    })
  }, [scene])

  return <primitive object={scene} />
}
```

---

## 2. Interactive Product Viewer

```jsx
import { useRef, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Environment, useGLTF, Center, Bounds } from '@react-three/drei'
import { useControls } from 'leva'

function Product({ url }) {
  const { scene } = useGLTF(url)
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)

  // Material controls
  const { metalness, roughness, color } = useControls({
    metalness: { value: 0.9, min: 0, max: 1, step: 0.01 },
    roughness: { value: 0.1, min: 0, max: 1, step: 0.01 },
    color: '#ffffff',
  })

  useFrame((state) => {
    if (hovered) {
      meshRef.current.rotation.y += 0.01
    }
  })

  return (
    <Center>
      <primitive
        ref={meshRef}
        object={scene}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        onClick={(e) => {
          e.stopPropagation()
          console.log('Product clicked:', e.object.name)
        }}
      />
    </Center>
  )
}

export default function ProductViewer() {
  return (
    <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
      <color attach="background" args={['#f0f0f0']} />

      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} intensity={1} />

      <Suspense fallback={null}>
        <Bounds fit clip observe margin={1.2}>
          <Product url="/models/product.glb" />
        </Bounds>
        <Environment preset="studio" />
      </Suspense>

      <OrbitControls
        enablePan={false}
        minDistance={2}
        maxDistance={10}
        minPolarAngle={Math.PI / 4}
        maxPolarAngle={Math.PI / 2}
      />
    </Canvas>
  )
}
```

---

## 3. Scroll-Based Animations

### Using Drei ScrollControls

```jsx
import { Canvas } from '@react-three/fiber'
import { ScrollControls, Scroll, useScroll } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function ScrollScene() {
  const meshRef = useRef()
  const scroll = useScroll()

  useFrame(() => {
    // scroll.offset: 0 to 1
    meshRef.current.position.y = scroll.offset * -10
    meshRef.current.rotation.y = scroll.offset * Math.PI * 2
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}

export default function ScrollAnimation() {
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} />

      <ScrollControls pages={3} damping={0.1}>
        <Scroll>
          <ScrollScene />
        </Scroll>

        {/* HTML content that scrolls */}
        <Scroll html>
          <div style={{ height: '100vh' }}>
            <h1>Page 1</h1>
          </div>
          <div style={{ height: '100vh' }}>
            <h1>Page 2</h1>
          </div>
          <div style={{ height: '100vh' }}>
            <h1>Page 3</h1>
          </div>
        </Scroll>
      </ScrollControls>
    </Canvas>
  )
}
```

### Syncing with GSAP ScrollTrigger

```jsx
import { useRef, useEffect } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

function ScrollSyncedBox() {
  const meshRef = useRef()
  const { viewport } = useThree()

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.to(meshRef.current.position, {
        x: 5,
        scrollTrigger: {
          trigger: '.section-2',
          start: 'top center',
          end: 'bottom center',
          scrub: true,
        },
      })

      gsap.to(meshRef.current.rotation, {
        y: Math.PI * 2,
        scrollTrigger: {
          trigger: '.section-2',
          start: 'top center',
          end: 'bottom center',
          scrub: true,
        },
      })
    })

    return () => ctx.revert()
  }, [])

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}
```

---

## 4. Particle System

### Instanced Particles

```jsx
import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export default function Particles({ count = 5000 }) {
  const meshRef = useRef()

  const particles = useMemo(() => {
    const temp = []
    for (let i = 0; i < count; i++) {
      const t = Math.random() * 100
      const factor = 20 + Math.random() * 100
      const speed = 0.01 + Math.random() / 200
      const x = Math.random() * 40 - 20
      const y = Math.random() * 40 - 20
      const z = Math.random() * 40 - 20
      temp.push({ t, factor, speed, x, y, z })
    }
    return temp
  }, [count])

  const dummy = useMemo(() => new THREE.Object3D(), [])

  useFrame(() => {
    particles.forEach((particle, i) => {
      let { t, factor, speed, x, y, z } = particle
      t = particle.t += speed / 2
      const a = Math.cos(t) + Math.sin(t * 1) / 10
      const b = Math.sin(t) + Math.cos(t * 2) / 10
      const s = Math.cos(t)

      dummy.position.set(
        x + Math.cos((t / 10) * factor) + (Math.sin(t * 1) * factor) / 10,
        y + Math.sin((t / 10) * factor) + (Math.cos(t * 2) * factor) / 10,
        z + Math.cos((t / 10) * factor) + (Math.sin(t * 3) * factor) / 10
      )
      dummy.scale.set(s, s, s)
      dummy.rotation.set(s * 5, s * 5, s * 5)
      dummy.updateMatrix()

      meshRef.current.setMatrixAt(i, dummy.matrix)
    })
    meshRef.current.instanceMatrix.needsUpdate = true
  })

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]}>
      <dodecahedronGeometry args={[0.1, 0]} />
      <meshPhongMaterial color="#ff4040" />
    </instancedMesh>
  )
}
```

---

## 5. Text 3D

### Using Drei Text

```jsx
import { Text } from '@react-three/drei'
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

export default function Text3D() {
  const textRef = useRef()

  useFrame((state) => {
    textRef.current.position.y = Math.sin(state.clock.elapsedTime) * 0.5
  })

  return (
    <Text
      ref={textRef}
      fontSize={1}
      color="#ffffff"
      anchorX="center"
      anchorY="middle"
      font="/fonts/Inter-Bold.woff"
    >
      Hello R3F!
    </Text>
  )
}
```

### Text with Gradient Material

```jsx
import { Text, shaderMaterial } from '@react-three/drei'
import { extend } from '@react-three/fiber'
import * as THREE from 'three'

const GradientMaterial = shaderMaterial(
  { uTime: 0 },
  // Vertex shader
  `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  // Fragment shader
  `
    uniform float uTime;
    varying vec2 vUv;
    void main() {
      vec3 colorA = vec3(1.0, 0.4, 0.7);
      vec3 colorB = vec3(0.2, 0.6, 1.0);
      vec3 color = mix(colorA, colorB, vUv.y);
      gl_FragColor = vec4(color, 1.0);
    }
  `
)

extend({ GradientMaterial })

export default function GradientText() {
  const materialRef = useRef()

  useFrame((state) => {
    materialRef.current.uTime = state.clock.elapsedTime
  })

  return (
    <Text fontSize={1} anchorX="center" anchorY="middle">
      Gradient Text
      <gradientMaterial ref={materialRef} />
    </Text>
  )
}
```

---

## 6. Post-Processing Effects

```bash
npm install @react-three/postprocessing
```

```jsx
import { Canvas } from '@react-three/fiber'
import { EffectComposer, Bloom, DepthOfField, Vignette } from '@react-three/postprocessing'

export default function PostProcessingScene() {
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} />

      <mesh>
        <torusKnotGeometry />
        <meshStandardMaterial color="orange" emissive="orange" emissiveIntensity={0.5} />
      </mesh>

      <EffectComposer>
        <Bloom
          intensity={1.5}
          luminanceThreshold={0}
          luminanceSmoothing={0.9}
        />
        <DepthOfField
          focusDistance={0}
          focalLength={0.02}
          bokehScale={2}
        />
        <Vignette
          offset={0.5}
          darkness={0.5}
        />
      </EffectComposer>
    </Canvas>
  )
}
```

---

## 7. Physics Simulation

```bash
npm install @react-three/rapier
```

```jsx
import { Canvas } from '@react-three/fiber'
import { Physics, RigidBody, CuboidCollider } from '@react-three/rapier'

function Box({ position }) {
  return (
    <RigidBody position={position} colliders="cuboid">
      <mesh castShadow>
        <boxGeometry />
        <meshStandardMaterial color="orange" />
      </mesh>
    </RigidBody>
  )
}

function Floor() {
  return (
    <RigidBody type="fixed">
      <CuboidCollider args={[10, 0.5, 10]} />
      <mesh receiveShadow position={[0, -0.5, 0]}>
        <boxGeometry args={[20, 1, 20]} />
        <meshStandardMaterial color="#808080" />
      </mesh>
    </RigidBody>
  )
}

export default function PhysicsScene() {
  return (
    <Canvas shadows camera={{ position: [0, 5, 10] }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} castShadow />

      <Physics gravity={[0, -9.81, 0]}>
        <Box position={[0, 5, 0]} />
        <Box position={[1, 8, 0]} />
        <Box position={[-1, 10, 0]} />
        <Floor />
      </Physics>
    </Canvas>
  )
}
```

---

## 8. Camera Animations

### Smooth Camera Movement

```jsx
import { useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'

export default function CameraRig({ children }) {
  const ref = useRef()
  const { camera, pointer } = useThree()

  useFrame((state, delta) => {
    // Smooth camera follow mouse
    const targetX = pointer.x * 2
    const targetY = pointer.y * 2

    camera.position.x += (targetX - camera.position.x) * delta * 2
    camera.position.y += (targetY - camera.position.y) * delta * 2

    camera.lookAt(0, 0, 0)
  })

  return <group ref={ref}>{children}</group>
}
```

### Camera Path Animation

```jsx
import { useEffect, useRef } from 'react'
import { useThree } from '@react-three/fiber'
import * as THREE from 'three'
import gsap from 'gsap'

export default function CameraPath() {
  const { camera } = useThree()
  const pathRef = useRef()

  useEffect(() => {
    // Define camera path points
    const points = [
      new THREE.Vector3(0, 0, 5),
      new THREE.Vector3(5, 2, 5),
      new THREE.Vector3(5, 2, -5),
      new THREE.Vector3(-5, 2, -5),
      new THREE.Vector3(-5, 2, 5),
      new THREE.Vector3(0, 0, 5),
    ]

    const curve = new THREE.CatmullRomCurve3(points)
    pathRef.current = curve

    // Animate camera along path
    gsap.to({ progress: 0 }, {
      progress: 1,
      duration: 10,
      repeat: -1,
      ease: 'none',
      onUpdate: function() {
        const point = curve.getPointAt(this.targets()[0].progress)
        camera.position.copy(point)
        camera.lookAt(0, 0, 0)
      }
    })
  }, [camera])

  return null
}
```

---

## 9. LOD (Level of Detail)

```jsx
import { useMemo } from 'react'
import { useThree } from '@react-three/fiber'
import * as THREE from 'three'

export default function LODMesh({ position }) {
  const { camera } = useThree()

  const lod = useMemo(() => {
    const lodObject = new THREE.LOD()

    // High detail (close)
    const geometryHigh = new THREE.IcosahedronGeometry(1, 3)
    const materialHigh = new THREE.MeshStandardMaterial({ color: 'orange' })
    const meshHigh = new THREE.Mesh(geometryHigh, materialHigh)
    lodObject.addLevel(meshHigh, 0)

    // Medium detail
    const geometryMid = new THREE.IcosahedronGeometry(1, 1)
    const materialMid = new THREE.MeshStandardMaterial({ color: 'orange' })
    const meshMid = new THREE.Mesh(geometryMid, materialMid)
    lodObject.addLevel(meshMid, 10)

    // Low detail (far)
    const geometryLow = new THREE.IcosahedronGeometry(1, 0)
    const materialLow = new THREE.MeshStandardMaterial({ color: 'orange' })
    const meshLow = new THREE.Mesh(geometryLow, materialLow)
    lodObject.addLevel(meshLow, 20)

    lodObject.position.set(...position)
    return lodObject
  }, [position])

  useFrame(() => {
    lod.update(camera)
  })

  return <primitive object={lod} />
}
```

---

## 10. Performance Monitoring

```jsx
import { Canvas } from '@react-three/fiber'
import {
  PerformanceMonitor,
  AdaptiveDpr,
  AdaptiveEvents,
  Stats
} from '@react-three/drei'
import { useState } from 'react'

export default function AdaptiveScene() {
  const [dpr, setDpr] = useState(1.5)

  return (
    <>
      <Stats />
      <Canvas dpr={dpr}>
        <PerformanceMonitor
          onIncline={() => setDpr(2)}
          onDecline={() => setDpr(1)}
        >
          <AdaptiveDpr pixelated />
          <AdaptiveEvents />

          {/* Your scene */}
          <ambientLight intensity={0.5} />
          <mesh>
            <torusKnotGeometry args={[1, 0.3, 128, 32]} />
            <meshStandardMaterial color="orange" />
          </mesh>
        </PerformanceMonitor>
      </Canvas>
    </>
  )
}
```

---

## Additional Resources

- [Poimandres Market](https://market.pmnd.rs/) - Ready-to-use R3F components
- [Three.js Journey](https://threejs-journey.com/) - Comprehensive Three.js course
- [R3F Examples](https://docs.pmnd.rs/react-three-fiber/getting-started/examples) - Official examples
- [Codesandbox Collection](https://codesandbox.io/examples/package/@react-three/fiber) - Live examples

## Performance Best Practices

1. **Use instancing** for many similar objects
2. **Implement LOD** for distant objects
3. **Enable frustum culling** (automatic in R3F)
4. **Use adaptive DPR** for mobile devices
5. **Lazy load models** with Suspense
6. **Optimize textures** (compress, use power-of-2 sizes)
7. **Reduce shadow quality** on low-end devices
8. **Use frameloop="demand"** for static scenes
9. **Profile with Stats** and Chrome DevTools
10. **Dispose unused resources** properly

---

**Note**: All examples assume you have the necessary dependencies installed. Refer to each example's comments for additional package requirements.



===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/assets/starter_r3f/README.md =====

# React Three Fiber Starter Template

A minimal, production-ready starter template for building 3D experiences with React Three Fiber (R3F), Drei helpers, and Vite.

## Features

- ⚡️ **Vite** - Fast build tool and dev server
- ⚛️ **React 18** - Latest React with concurrent features
- 🎨 **React Three Fiber** - Declarative Three.js in React
- 🛠️ **Drei** - Essential R3F helpers (OrbitControls, Environment, etc.)
- 🎮 **Interactive Components** - Click and hover interactions
- 🌅 **Environment & Lighting** - HDRI environment with proper lighting
- 💫 **Animations** - useFrame examples for smooth 60fps animations
- 📦 **Optimized Build** - Code-splitting for Three.js and R3F
- 🎛️ **Leva** - Optional GUI controls for debugging

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
starter_r3f/
├── index.html           # Entry HTML with full-page canvas styling
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite configuration with code-splitting
└── src/
    ├── main.jsx         # React root
    ├── App.jsx          # Main App component with UI overlay
    ├── Experience.jsx   # Canvas wrapper and Scene component
    └── components/
        ├── Box.jsx      # Interactive box with click/hover
        └── Sphere.jsx   # Floating animated sphere
```

## What's Included

### Components

**Box.jsx** - Interactive component with:
- Click to toggle rotation animation
- Hover for color change
- Scale animation on click
- Cast shadows

**Sphere.jsx** - Animated component with:
- Floating sine wave animation
- Continuous rotation
- Metallic material
- Cast shadows

### Scene Setup (Experience.jsx)

- **Lighting**: Ambient + Directional with shadows
- **Environment**: Drei Environment preset (HDRI)
- **Shadows**: Contact shadows for soft ground shadows
- **Controls**: OrbitControls for camera manipulation
- **Ground Plane**: Receives shadows

### Performance Features

- **Code-splitting**: Separate chunks for Three.js and R3F
- **Suspense**: Async loading with fallback
- **Optimized imports**: Tree-shaking friendly imports

## Customization

### Change Environment Preset

```jsx
// Experience.jsx
<Environment preset="sunset" /> // Try: city, forest, night, warehouse, etc.
```

### Add New Components

```jsx
// src/components/MyComponent.jsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

export default function MyComponent() {
  const meshRef = useRef()

  useFrame((state, delta) => {
    meshRef.current.rotation.y += delta
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}
```

Then import in Experience.jsx:
```jsx
import MyComponent from './components/MyComponent'

// In Scene component:
<MyComponent />
```

### Add Leva Controls

```jsx
import { useControls } from 'leva'

export default function Box() {
  const { color, scale } = useControls({
    color: '#ff6b6b',
    scale: { value: 1, min: 0.5, max: 2, step: 0.1 }
  })

  return (
    <mesh scale={scale}>
      <boxGeometry />
      <meshStandardMaterial color={color} />
    </mesh>
  )
}
```

## Common Patterns

### Load GLTF Models

```jsx
import { useGLTF } from '@react-three/drei'

function Model() {
  const { scene } = useGLTF('/models/mymodel.glb')
  return <primitive object={scene} />
}

// Preload
useGLTF.preload('/models/mymodel.glb')
```

### Add Post-Processing

```bash
npm install @react-three/postprocessing
```

```jsx
import { EffectComposer, Bloom } from '@react-three/postprocessing'

<Canvas>
  <Scene />
  <EffectComposer>
    <Bloom intensity={0.5} />
  </EffectComposer>
</Canvas>
```

### Optimize Performance

```jsx
// Enable adaptive pixel ratio
<Canvas dpr={[1, 2]} />

// Use on-demand rendering for static scenes
<Canvas frameloop="demand" />

// Use instancing for many objects
import { Instance, Instances } from '@react-three/drei'

<Instances>
  <boxGeometry />
  <meshStandardMaterial />
  <Instance position={[0, 0, 0]} />
  <Instance position={[2, 0, 0]} />
  {/* ... thousands more */}
</Instances>
```

## Resources

- [React Three Fiber Docs](https://docs.pmnd.rs/react-three-fiber)
- [Drei Helpers](https://github.com/pmndrs/drei)
- [Three.js Docs](https://threejs.org/docs/)
- [Vite Docs](https://vitejs.dev/)
- [React Docs](https://react.dev/)

## Troubleshooting

### Canvas Not Rendering

- Ensure `#root` has width and height set (see index.html styles)
- Check browser console for errors
- Verify Three.js and R3F versions are compatible

### Performance Issues

- Reduce shadow quality: `shadow-mapSize={[512, 512]}`
- Disable shadows: Remove `castShadow` and `receiveShadow`
- Use adaptive DPR: `<Canvas dpr={[1, 2]} />`
- Enable frameloop demand: `<Canvas frameloop="demand" />`

### TypeScript Support

```bash
npm install -D typescript @types/react @types/react-dom @types/three
```

Rename files to `.tsx` and add `tsconfig.json`:

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

## License

MIT - Use freely for personal and commercial projects.



===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/assets/starter_r3f/index.html =====

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>React Three Fiber Starter</title>
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
        height: 100%;
        overflow: hidden;
      }

      body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
          'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
          sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
      }

      .loading {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #000;
        color: #fff;
        font-size: 24px;
      }

      .info {
        position: absolute;
        top: 20px;
        left: 20px;
        color: white;
        font-size: 14px;
        background: rgba(0, 0, 0, 0.7);
        padding: 10px 15px;
        border-radius: 5px;
        z-index: 10;
      }

      .info h1 {
        font-size: 18px;
        margin-bottom: 5px;
      }

      .info p {
        margin: 3px 0;
        opacity: 0.8;
      }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>

```


===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/assets/starter_r3f/package.json =====

```json
{
  "name": "r3f-starter",
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
    "@react-three/fiber": "^8.18.8",
    "@react-three/drei": "^9.123.0",
    "three": "^0.172.0",
    "leva": "^0.9.35"
  },
  "devDependencies": {
    "@types/react": "^18.3.18",
    "@types/react-dom": "^18.3.5",
    "@types/three": "^0.172.0",
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.11"
  }
}

```


===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/assets/starter_r3f/src/App.jsx =====

```jsx
import Experience from './Experience'

export default function App() {
  return (
    <>
      <div className="info">
        <h1>React Three Fiber Starter</h1>
        <p>🖱️ Drag to rotate</p>
        <p>🔍 Scroll to zoom</p>
      </div>
      <Experience />
    </>
  )
}

```


===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/assets/starter_r3f/src/Experience.jsx =====

```jsx
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment, ContactShadows } from '@react-three/drei'
import { Suspense } from 'react'
import Box from './components/Box'
import Sphere from './components/Sphere'

function Scene() {
  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.5} />
      <directionalLight
        position={[5, 5, 5]}
        intensity={1}
        castShadow
        shadow-mapSize={[1024, 1024]}
      />

      {/* 3D Objects */}
      <Box position={[-2, 1, 0]} />
      <Sphere position={[2, 1, 0]} />

      {/* Ground */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#808080" />
      </mesh>

      {/* Environment */}
      <Environment preset="sunset" />
      <ContactShadows
        position={[0, 0, 0]}
        opacity={0.5}
        scale={10}
        blur={1}
        far={10}
      />

      {/* Camera Controls */}
      <OrbitControls makeDefault />
    </>
  )
}

export default function Experience() {
  return (
    <Canvas
      shadows
      camera={{ position: [5, 5, 5], fov: 50 }}
      style={{ width: '100%', height: '100%' }}
    >
      <Suspense fallback={null}>
        <Scene />
      </Suspense>
    </Canvas>
  )
}

```


===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/assets/starter_r3f/src/components/Box.jsx =====

```jsx
import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'

export default function Box({ position = [0, 0, 0], ...props }) {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)
  const [active, setActive] = useState(false)

  // Animate on every frame
  useFrame((state, delta) => {
    if (active) {
      meshRef.current.rotation.x += delta
      meshRef.current.rotation.y += delta * 0.5
    }
  })

  return (
    <mesh
      {...props}
      ref={meshRef}
      position={position}
      scale={active ? 1.5 : 1}
      onClick={(e) => {
        e.stopPropagation()
        setActive(!active)
      }}
      onPointerOver={(e) => {
        e.stopPropagation()
        setHovered(true)
      }}
      onPointerOut={() => setHovered(false)}
      castShadow
    >
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
    </mesh>
  )
}

```


===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/assets/starter_r3f/src/components/Sphere.jsx =====

```jsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

export default function Sphere({ position = [0, 0, 0], ...props }) {
  const meshRef = useRef()

  // Floating animation
  useFrame((state) => {
    const time = state.clock.elapsedTime
    meshRef.current.position.y = position[1] + Math.sin(time * 2) * 0.5
    meshRef.current.rotation.y = time * 0.5
  })

  return (
    <mesh {...props} ref={meshRef} position={position} castShadow>
      <sphereGeometry args={[0.75, 32, 32]} />
      <meshStandardMaterial
        color="skyblue"
        metalness={0.6}
        roughness={0.2}
      />
    </mesh>
  )
}

```


===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/assets/starter_r3f/src/main.jsx =====

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


===== FILE: plugins/individual/react-three-fiber/skills/react-three-fiber/assets/starter_r3f/vite.config.js =====

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
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'three': ['three'],
          'r3f': ['@react-three/fiber', '@react-three/drei'],
        },
      },
    },
  },
})

```


# Skill: babylonjs-engine


===== FILE: plugins/individual/babylonjs-engine/skills/babylonjs-engine/SKILL.md =====

---
name: babylonjs-engine
description: Comprehensive skill for Babylon.js 3D web rendering engine. Use this skill when building real-time 3D experiences, browser-based games, interactive visualizations, or immersive web applications. Triggers on tasks involving Babylon.js, 3D scenes, WebGL/WebGPU rendering, entity-component systems, physics simulations, PBR materials, shadow mapping, or 3D model loading. Alternative to Three.js with built-in editor integration and game engine features.
---

# Babylon.js Engine Skill

## Related Skills
- threejs-webgl: Alternative 3D engine
- react-three-fiber: React integration for 3D
- gsap-scrolltrigger: Animation library
- motion-framer: UI animations

## Core Concepts

### 1. Engine and Scene Initialization

**Basic Setup**
```javascript
// Get canvas element
const canvas = document.getElementById('renderCanvas');

// Create engine
const engine = new BABYLON.Engine(canvas, true, {
  preserveDrawingBuffer: true,
  stencil: true
});

// Create scene
const scene = new BABYLON.Scene(engine);

// Render loop
engine.runRenderLoop(() => {
  scene.render();
});

// Handle resize
window.addEventListener('resize', () => {
  engine.resize();
});
```

**ES6/TypeScript Setup**
```typescript
import { Engine } from '@babylonjs/core/Engines/engine';
import { Scene } from '@babylonjs/core/scene';
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { CreateSphere } from '@babylonjs/core/Meshes/Builders/sphereBuilder';

const canvas = document.getElementById('renderCanvas') as HTMLCanvasElement;
const engine = new Engine(canvas);
const scene = new Scene(engine);

// Camera setup
const camera = new FreeCamera('camera1', new Vector3(0, 5, -10), scene);
camera.setTarget(Vector3.Zero());
camera.attachControl(canvas, true);

// Lighting
const light = new HemisphericLight('light1', new Vector3(0, 1, 0), scene);
light.intensity = 0.7;

// Create mesh
const sphere = CreateSphere('sphere1', { segments: 16, diameter: 2 }, scene);
sphere.position.y = 2;

// Render
engine.runRenderLoop(() => {
  scene.render();
});
```

**Scene Configuration Options**
```javascript
const scene = new BABYLON.Scene(engine, {
  // Optimize for large mesh counts
  useGeometryUniqueIdsMap: true,
  useMaterialMeshMap: true,
  useClonedMeshMap: true
});
```

### 2. Camera Systems

**Free Camera (FPS-style)**
```javascript
const camera = new BABYLON.FreeCamera('camera1', new BABYLON.Vector3(0, 5, -10), scene);
camera.setTarget(BABYLON.Vector3.Zero());
camera.attachControl(canvas, true);

// Movement settings
camera.speed = 0.5;
camera.angularSensibility = 2000;
camera.keysUp = [87]; // W
camera.keysDown = [83]; // S
camera.keysLeft = [65]; // A
camera.keysRight = [68]; // D
```

**Arc Rotate Camera (Orbit)**
```javascript
const camera = new BABYLON.ArcRotateCamera(
  'camera',
  -Math.PI / 2,        // alpha (horizontal rotation)
  Math.PI / 2.5,       // beta (vertical rotation)
  15,                  // radius (distance)
  new BABYLON.Vector3(0, 0, 0), // target
  scene
);
camera.attachControl(canvas, true);

// Constraints
camera.lowerRadiusLimit = 5;
camera.upperRadiusLimit = 50;
camera.lowerBetaLimit = 0.1;
camera.upperBetaLimit = Math.PI / 2;
```

**Universal Camera (Advanced)**
```javascript
const camera = new BABYLON.UniversalCamera('camera', new BABYLON.Vector3(0, 5, -10), scene);
camera.setTarget(BABYLON.Vector3.Zero());
camera.attachControl(canvas, true);

// Collision detection
camera.checkCollisions = true;
camera.applyGravity = true;
camera.ellipsoid = new BABYLON.Vector3(1, 1, 1);
```

### 3. Lighting Systems

**Hemispheric Light (Ambient)**
```javascript
const light = new BABYLON.HemisphericLight('light1', new BABYLON.Vector3(0, 1, 0), scene);
light.intensity = 0.7;
light.diffuse = new BABYLON.Color3(1, 1, 1);
light.specular = new BABYLON.Color3(1, 1, 1);
light.groundColor = new BABYLON.Color3(0, 0, 0);
```

**Directional Light (Sun-like)**
```javascript
const light = new BABYLON.DirectionalLight('dirLight', new BABYLON.Vector3(-1, -2, -1), scene);
light.position = new BABYLON.Vector3(20, 40, 20);
light.intensity = 0.5;

// Shadow setup
const shadowGenerator = new BABYLON.ShadowGenerator(1024, light);
shadowGenerator.useExponentialShadowMap = true;
```

**Point Light (Omni-directional)**
```javascript
const light = new BABYLON.PointLight('pointLight', new BABYLON.Vector3(0, 10, 0), scene);
light.intensity = 0.7;
light.diffuse = new BABYLON.Color3(1, 0, 0);
light.specular = new BABYLON.Color3(0, 1, 0);

// Range and falloff
light.range = 100;
light.radius = 0.1;
```

**Spot Light (Focused)**
```javascript
const light = new BABYLON.SpotLight(
  'spotLight',
  new BABYLON.Vector3(0, 10, 0),      // position
  new BABYLON.Vector3(0, -1, 0),      // direction
  Math.PI / 3,                        // angle
  2,                                  // exponent
  scene
);
light.intensity = 0.8;
```

**Light Optimization (Include Only Specific Meshes)**
```javascript
// Only affect specific meshes
light.includedOnlyMeshes = [mesh1, mesh2, mesh3];

// Or exclude specific meshes
light.excludedMeshes = [mesh4, mesh5];
```

### 4. Mesh Creation

**Built-in Shapes**
```javascript
// Box
const box = BABYLON.MeshBuilder.CreateBox('box', {
  size: 2,
  width: 2,
  height: 2,
  depth: 2
}, scene);

// Sphere
const sphere = BABYLON.MeshBuilder.CreateSphere('sphere', {
  diameter: 2,
  segments: 32,
  diameterX: 2,
  diameterY: 2,
  diameterZ: 2,
  arc: 1,
  slice: 1
}, scene);

// Cylinder
const cylinder = BABYLON.MeshBuilder.CreateCylinder('cylinder', {
  height: 3,
  diameter: 2,
  tessellation: 24
}, scene);

// Plane
const plane = BABYLON.MeshBuilder.CreatePlane('plane', {
  size: 5,
  width: 5,
  height: 5
}, scene);

// Ground
const ground = BABYLON.MeshBuilder.CreateGround('ground', {
  width: 10,
  height: 10,
  subdivisions: 2
}, scene);

// Ground from heightmap
const ground = BABYLON.MeshBuilder.CreateGroundFromHeightMap('ground', 'heightmap.png', {
  width: 100,
  height: 100,
  subdivisions: 100,
  minHeight: 0,
  maxHeight: 10
}, scene);

// Torus
const torus = BABYLON.MeshBuilder.CreateTorus('torus', {
  diameter: 3,
  thickness: 1,
  tessellation: 16
}, scene);

// TorusKnot
const torusKnot = BABYLON.MeshBuilder.CreateTorusKnot('torusKnot', {
  radius: 2,
  tube: 0.6,
  radialSegments: 64,
  tubularSegments: 8,
  p: 2,
  q: 3
}, scene);
```

**Mesh Transformations**
```javascript
// Position
mesh.position = new BABYLON.Vector3(0, 5, 10);
mesh.position.x = 5;
mesh.position.y = 2;

// Rotation (radians)
mesh.rotation = new BABYLON.Vector3(0, Math.PI / 2, 0);
mesh.rotation.y = Math.PI / 4;

// Scaling
mesh.scaling = new BABYLON.Vector3(2, 2, 2);
mesh.scaling.x = 1.5;

// Look at
mesh.lookAt(new BABYLON.Vector3(0, 0, 0));

// Parent-child relationships
childMesh.parent = parentMesh;
```

**Mesh Properties**
```javascript
// Visibility
mesh.isVisible = true;
mesh.visibility = 0.5; // 0 = invisible, 1 = fully visible

// Picking
mesh.isPickable = true;
mesh.checkCollisions = true;

// Culling
mesh.cullingStrategy = BABYLON.AbstractMesh.CULLINGSTRATEGY_BOUNDINGSPHERE_ONLY;

// Receive shadows
mesh.receiveShadows = true;
```

### 5. Materials

**Standard Material**
```javascript
const material = new BABYLON.StandardMaterial('material', scene);

// Colors
material.diffuseColor = new BABYLON.Color3(1, 0, 1);
material.specularColor = new BABYLON.Color3(0.5, 0.6, 0.87);
material.emissiveColor = new BABYLON.Color3(0, 0, 0);
material.ambientColor = new BABYLON.Color3(0.23, 0.98, 0.53);

// Textures
material.diffuseTexture = new BABYLON.Texture('diffuse.png', scene);
material.specularTexture = new BABYLON.Texture('specular.png', scene);
material.emissiveTexture = new BABYLON.Texture('emissive.png', scene);
material.ambientTexture = new BABYLON.Texture('ambient.png', scene);
material.bumpTexture = new BABYLON.Texture('normal.png', scene);
material.opacityTexture = new BABYLON.Texture('opacity.png', scene);

// Properties
material.alpha = 0.8;
material.backFaceCulling = true;
material.wireframe = false;
material.specularPower = 64;

// Apply to mesh
mesh.material = material;
```

**PBR Material (Physically Based Rendering)**
```javascript
const pbr = new BABYLON.PBRMaterial('pbr', scene);

// Metallic workflow
pbr.albedoColor = new BABYLON.Color3(1, 1, 1);
pbr.albedoTexture = new BABYLON.Texture('albedo.png', scene);
pbr.metallic = 1.0;
pbr.roughness = 0.5;
pbr.metallicTexture = new BABYLON.Texture('metallic.png', scene);

// Or specular workflow
pbr.albedoTexture = new BABYLON.Texture('albedo.png', scene);
pbr.reflectivityTexture = new BABYLON.Texture('reflectivity.png', scene);

// Environment
pbr.environmentTexture = BABYLON.CubeTexture.CreateFromPrefilteredData('environment.dds', scene);

// Other maps
pbr.bumpTexture = new BABYLON.Texture('normal.png', scene);
pbr.ambientTexture = new BABYLON.Texture('ao.png', scene);
pbr.emissiveTexture = new BABYLON.Texture('emissive.png', scene);

mesh.material = pbr;
```

**Multi-Materials**
```javascript
const multiMat = new BABYLON.MultiMaterial('multiMat', scene);
multiMat.subMaterials.push(material1);
multiMat.subMaterials.push(material2);
multiMat.subMaterials.push(material3);

mesh.material = multiMat;
mesh.subMeshes = [];
mesh.subMeshes.push(new BABYLON.SubMesh(0, 0, verticesCount, 0, indicesCount1, mesh));
mesh.subMeshes.push(new BABYLON.SubMesh(1, 0, verticesCount, indicesCount1, indicesCount2, mesh));
```

### 6. Model Loading

**GLTF/GLB Import**
```javascript
// Append to scene
BABYLON.SceneLoader.Append('path/to/', 'model.gltf', scene, function(scene) {
  console.log('Model loaded');
});

// Import mesh
BABYLON.SceneLoader.ImportMesh('', 'path/to/', 'model.gltf', scene, function(meshes) {
  const mesh = meshes[0];
  mesh.position.y = 5;
});

// Async version
const result = await BABYLON.SceneLoader.ImportMeshAsync(
  null,  // all meshes
  'https://assets.babylonjs.com/meshes/',
  'village.glb',
  scene
);
console.log('Loaded meshes:', result.meshes);

// Load from binary
const result = await BABYLON.SceneLoader.AppendAsync(
  '',
  'data:' + arrayBuffer,
  scene
);
```

**Asset Manager (Batch Loading)**
```javascript
const assetsManager = new BABYLON.AssetsManager(scene);

// Add mesh task
const meshTask = assetsManager.addMeshTask('model', '', 'path/to/', 'model.gltf');
meshTask.onSuccess = function(task) {
  task.loadedMeshes[0].position = new BABYLON.Vector3(0, 0, 0);
};

// Add texture task
const textureTask = assetsManager.addTextureTask('texture', 'texture.png');
textureTask.onSuccess = function(task) {
  material.diffuseTexture = task.texture;
};

// Load all
assetsManager.onFinish = function(tasks) {
  console.log('All assets loaded');
  engine.runRenderLoop(() => scene.render());
};

assetsManager.load();
```

### 7. Physics Engine

**Havok Physics Setup**
```javascript
// Import Havok
import HavokPhysics from '@babylonjs/havok';

// Initialize
const havokInstance = await HavokPhysics();
const havokPlugin = new BABYLON.HavokPlugin(true, havokInstance);

// Enable physics
scene.enablePhysics(new BABYLON.Vector3(0, -9.8, 0), havokPlugin);

// Create physics aggregate for mesh
const sphereAggregate = new BABYLON.PhysicsAggregate(
  sphere,
  BABYLON.PhysicsShapeType.SPHERE,
  { mass: 1, restitution: 0.75 },
  scene
);

// Ground (static)
const groundAggregate = new BABYLON.PhysicsAggregate(
  ground,
  BABYLON.PhysicsShapeType.BOX,
  { mass: 0 }, // mass 0 = static
  scene
);
```

**Physics Shapes**
```javascript
// Available shapes
BABYLON.PhysicsShapeType.SPHERE
BABYLON.PhysicsShapeType.BOX
BABYLON.PhysicsShapeType.CAPSULE
BABYLON.PhysicsShapeType.CYLINDER
BABYLON.PhysicsShapeType.CONVEX_HULL
BABYLON.PhysicsShapeType.MESH
BABYLON.PhysicsShapeType.HEIGHTFIELD
```

**Physics Body Control**
```javascript
// Get body
const body = aggregate.body;

// Apply force
body.applyForce(
  new BABYLON.Vector3(0, 10, 0),    // force
  new BABYLON.Vector3(0, 0, 0)      // point of application
);

// Apply impulse
body.applyImpulse(
  new BABYLON.Vector3(0, 5, 0),
  new BABYLON.Vector3(0, 0, 0)
);

// Set velocity
body.setLinearVelocity(new BABYLON.Vector3(0, 5, 0));
body.setAngularVelocity(new BABYLON.Vector3(0, 1, 0));

// Properties
body.setMassProperties({ mass: 2 });
body.setCollisionCallbackEnabled(true);
```

### 8. Animations

**Direct Animation**
```javascript
// Animate property
BABYLON.Animation.CreateAndStartAnimation(
  'anim',
  mesh,
  'position.y',
  30,                    // FPS
  120,                   // total frames
  mesh.position.y,       // from
  10,                    // to
  BABYLON.Animation.ANIMATIONLOOPMODE_CYCLE
);
```

**Animation Class**
```javascript
const animation = new BABYLON.Animation(
  'myAnimation',
  'position.x',
  30,
  BABYLON.Animation.ANIMATIONTYPE_FLOAT,
  BABYLON.Animation.ANIMATIONLOOPMODE_CYCLE
);

// Keyframes
const keys = [
  { frame: 0, value: 0 },
  { frame: 30, value: 10 },
  { frame: 60, value: 0 }
];
animation.setKeys(keys);

// Attach to mesh
mesh.animations.push(animation);

// Start
scene.beginAnimation(mesh, 0, 60, true);
```

**Animation Groups**
```javascript
const animationGroup = new BABYLON.AnimationGroup('group', scene);
animationGroup.addTargetedAnimation(animation1, mesh1);
animationGroup.addTargetedAnimation(animation2, mesh2);

// Control
animationGroup.play();
animationGroup.pause();
animationGroup.stop();
animationGroup.speedRatio = 2.0;

// Events
animationGroup.onAnimationEndObservable.add(() => {
  console.log('Animation complete');
});
```

**Skeleton Animations (from imported models)**
```javascript
// Get skeleton from imported model
const skeleton = result.skeletons[0];

// Get animation ranges
const ranges = skeleton.getAnimationRanges();

// Play animation range
scene.beginAnimation(skeleton, 0, 100, true);

// Or use animation groups
result.animationGroups[0].play();
result.animationGroups[0].setWeightForAllAnimatables(0.5);
```

## Common Patterns

### Pattern 1: Scene Setup with Default Environment

```javascript
const createScene = function() {
  const scene = new BABYLON.Scene(engine);

  // Quick setup
  scene.createDefaultCameraOrLight(true, true, true);
  const env = scene.createDefaultEnvironment({
    createGround: true,
    createSkybox: true,
    skyboxSize: 150,
    groundSize: 50
  });

  // Your meshes
  const sphere = BABYLON.MeshBuilder.CreateSphere('sphere', {diameter: 2}, scene);
  sphere.position.y = 1;

  return scene;
};
```

### Pattern 2: Async Scene Loading

```javascript
const createScene = async function() {
  const scene = new BABYLON.Scene(engine);

  const camera = new BABYLON.ArcRotateCamera('camera', 0, 0, 10, BABYLON.Vector3.Zero(), scene);
  camera.attachControl(canvas, true);

  const light = new BABYLON.HemisphericLight('light', new BABYLON.Vector3(0, 1, 0), scene);

  // Load model
  const result = await BABYLON.SceneLoader.ImportMeshAsync(
    null,
    'https://assets.babylonjs.com/meshes/',
    'village.glb',
    scene
  );

  // Setup physics
  const havokInstance = await HavokPhysics();
  const havokPlugin = new BABYLON.HavokPlugin(true, havokInstance);
  scene.enablePhysics(new BABYLON.Vector3(0, -9.8, 0), havokPlugin);

  return scene;
};

createScene().then(scene => {
  engine.runRenderLoop(() => scene.render());
});
```

### Pattern 3: Interactive Picking

```javascript
scene.onPointerDown = function(evt, pickResult) {
  if (pickResult.hit) {
    console.log('Picked mesh:', pickResult.pickedMesh.name);
    console.log('Pick point:', pickResult.pickedPoint);

    // Highlight picked mesh
    pickResult.pickedMesh.material.emissiveColor = new BABYLON.Color3(1, 0, 0);
  }
};

// Or use action manager
mesh.actionManager = new BABYLON.ActionManager(scene);
mesh.actionManager.registerAction(
  new BABYLON.ExecuteCodeAction(
    BABYLON.ActionManager.OnPickTrigger,
    function() {
      console.log('Mesh clicked');
    }
  )
);
```

### Pattern 4: Post-Processing Effects

```javascript
// Default pipeline
const pipeline = new BABYLON.DefaultRenderingPipeline('pipeline', true, scene, [camera]);
pipeline.samples = 4;
pipeline.fxaaEnabled = true;
pipeline.bloomEnabled = true;
pipeline.bloomThreshold = 0.8;
pipeline.bloomWeight = 0.5;
pipeline.bloomKernel = 64;

// Depth of field
pipeline.depthOfFieldEnabled = true;
pipeline.depthOfFieldBlurLevel = BABYLON.DepthOfFieldEffectBlurLevel.Low;
pipeline.depthOfField.focusDistance = 2000;
pipeline.depthOfField.focalLength = 50;

// Glow layer
const glowLayer = new BABYLON.GlowLayer('glow', scene);
glowLayer.intensity = 0.5;

// Highlight layer
const highlightLayer = new BABYLON.HighlightLayer('highlight', scene);
highlightLayer.addMesh(mesh, BABYLON.Color3.Green());
```

### Pattern 5: GUI (2D UI)

```javascript
import { AdvancedDynamicTexture, Button, TextBlock, Rectangle } from '@babylonjs/gui';

// Fullscreen UI
const advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI('UI');

// Button
const button = BABYLON.GUI.Button.CreateSimpleButton('button', 'Click Me');
button.width = '150px';
button.height = '40px';
button.color = 'white';
button.background = 'green';
button.onPointerUpObservable.add(() => {
  console.log('Button clicked');
});
advancedTexture.addControl(button);

// Text
const text = new BABYLON.GUI.TextBlock();
text.text = 'Hello World';
text.color = 'white';
text.fontSize = 24;
advancedTexture.addControl(text);

// 3D mesh UI
const plane = BABYLON.MeshBuilder.CreatePlane('plane', {size: 2}, scene);
const advancedTexture3D = BABYLON.GUI.AdvancedDynamicTexture.CreateForMesh(plane);
const button3D = BABYLON.GUI.Button.CreateSimpleButton('button3D', 'Click Me');
advancedTexture3D.addControl(button3D);
```

### Pattern 6: Shadow Mapping

```javascript
const light = new BABYLON.DirectionalLight('light', new BABYLON.Vector3(-1, -2, -1), scene);
light.position = new BABYLON.Vector3(20, 40, 20);

// Create shadow generator
const shadowGenerator = new BABYLON.ShadowGenerator(1024, light);
shadowGenerator.useExponentialShadowMap = true;
shadowGenerator.usePoissonSampling = true;

// Add shadow casters
shadowGenerator.addShadowCaster(sphere);
shadowGenerator.addShadowCaster(box);

// Enable shadow receiving
ground.receiveShadows = true;
```

### Pattern 7: Particle Systems

```javascript
const particleSystem = new BABYLON.ParticleSystem('particles', 2000, scene);
particleSystem.particleTexture = new BABYLON.Texture('particle.png', scene);

// Emitter
particleSystem.emitter = new BABYLON.Vector3(0, 5, 0);
particleSystem.minEmitBox = new BABYLON.Vector3(-1, 0, 0);
particleSystem.maxEmitBox = new BABYLON.Vector3(1, 0, 0);

// Colors
particleSystem.color1 = new BABYLON.Color4(0.7, 0.8, 1.0, 1.0);
particleSystem.color2 = new BABYLON.Color4(0.2, 0.5, 1.0, 1.0);
particleSystem.colorDead = new BABYLON.Color4(0, 0, 0.2, 0.0);

// Size
particleSystem.minSize = 0.1;
particleSystem.maxSize = 0.5;

// Life time
particleSystem.minLifeTime = 0.3;
particleSystem.maxLifeTime = 1.5;

// Emission rate
particleSystem.emitRate = 1500;

// Direction
particleSystem.direction1 = new BABYLON.Vector3(-1, 8, 1);
particleSystem.direction2 = new BABYLON.Vector3(1, 8, -1);

// Gravity
particleSystem.gravity = new BABYLON.Vector3(0, -9.81, 0);

// Start
particleSystem.start();
```

## Integration Patterns

### Pattern 1: React Integration

```jsx
import { useEffect, useRef } from 'react';
import * as BABYLON from '@babylonjs/core';

function BabylonScene() {
  const canvasRef = useRef(null);
  const engineRef = useRef(null);
  const sceneRef = useRef(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    // Initialize
    const engine = new BABYLON.Engine(canvasRef.current, true);
    engineRef.current = engine;

    const scene = new BABYLON.Scene(engine);
    sceneRef.current = scene;

    // Setup scene
    const camera = new BABYLON.ArcRotateCamera('camera', 0, 0, 10, BABYLON.Vector3.Zero(), scene);
    camera.attachControl(canvasRef.current, true);

    const light = new BABYLON.HemisphericLight('light', new BABYLON.Vector3(0, 1, 0), scene);

    const sphere = BABYLON.MeshBuilder.CreateSphere('sphere', {diameter: 2}, scene);

    // Render loop
    engine.runRenderLoop(() => {
      scene.render();
    });

    // Resize handler
    const handleResize = () => engine.resize();
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      scene.dispose();
      engine.dispose();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: '100%', height: '100vh' }}
    />
  );
}
```

### Pattern 2: WebXR (VR/AR)

```javascript
const createScene = async function() {
  const scene = new BABYLON.Scene(engine);

  const camera = new BABYLON.FreeCamera('camera', new BABYLON.Vector3(0, 5, -10), scene);
  camera.attachControl(canvas, true);

  const light = new BABYLON.HemisphericLight('light', new BABYLON.Vector3(0, 1, 0), scene);

  const sphere = BABYLON.MeshBuilder.CreateSphere('sphere', {diameter: 2}, scene);
  sphere.position.y = 1;

  const env = scene.createDefaultEnvironment();

  // Enable WebXR
  const xrHelper = await scene.createDefaultXRExperienceAsync({
    floorMeshes: [env.ground],
    disableTeleportation: false
  });

  // XR controller input
  xrHelper.input.onControllerAddedObservable.add((controller) => {
    controller.onMotionControllerInitObservable.add((motionController) => {
      const trigger = motionController.getMainComponent();
      trigger.onButtonStateChangedObservable.add(() => {
        if (trigger.pressed) {
          console.log('Trigger pressed');
        }
      });
    });
  });

  return scene;
};
```

### Pattern 3: Node Material (Visual Shader Editor)

```javascript
// Create from snippet
const nodeMaterial = await BABYLON.NodeMaterial.ParseFromSnippetAsync('#SNIPPET_ID', scene);

// Apply to mesh
nodeMaterial.build();
mesh.material = nodeMaterial;

// Or create programmatically
const nodeMaterial = new BABYLON.NodeMaterial('node', scene);

const positionInput = new BABYLON.InputBlock('position');
positionInput.setAsAttribute('position');

const worldPos = new BABYLON.TransformBlock('worldPos');
nodeMaterial.addOutputNode(worldPos);
```

## Performance Optimization

### 1. Mesh Optimization

```javascript
// Merge meshes with same material
const merged = BABYLON.Mesh.MergeMeshes(
  [mesh1, mesh2, mesh3],
  true,  // disposeSource
  true,  // allow32BitsIndices
  undefined,
  false, // multiMultiMaterials
  true   // preserveSerializationHelper
);

// Instances (for repeated meshes)
const instance1 = mesh.createInstance('instance1');
const instance2 = mesh.createInstance('instance2');
instance1.position.x = 5;
instance2.position.x = -5;

// Thin instances (even more efficient)
const buffer = new Float32Array(16 * count); // 16 floats per matrix
mesh.thinInstanceSetBuffer('matrix', buffer, 16);

// Freeze meshes (static meshes)
mesh.freezeWorldMatrix();

// Freeze materials
material.freeze();

// Simplify meshes (LOD)
const simplified = mesh.simplify(
  [
    { quality: 0.8, distance: 10 },
    { quality: 0.4, distance: 50 },
    { quality: 0.2, distance: 100 }
  ],
  true,  // parallelProcessing
  BABYLON.SimplificationType.QUADRATIC
);
```

### 2. Scene Optimization

```javascript
// Scene optimizer
const options = new BABYLON.SceneOptimizerOptions();
options.addOptimization(new BABYLON.HardwareScalingOptimization(0, 1));
options.addOptimization(new BABYLON.ShadowsOptimization(1));
options.addOptimization(new BABYLON.PostProcessesOptimization(2));
options.addOptimization(new BABYLON.LensFlaresOptimization(3));
options.addOptimization(new BABYLON.ParticlesOptimization(4));
options.addOptimization(new BABYLON.TextureOptimization(5, 512));
options.addOptimization(new BABYLON.RenderTargetsOptimization(6));
options.addOptimization(new BABYLON.MergeMeshesOptimization(7));

const optimizer = new BABYLON.SceneOptimizer(scene, options);
optimizer.start();

// Octree (spatial partitioning)
const octree = scene.createOrUpdateSelectionOctree();

// Frustum culling
scene.blockMaterialDirtyMechanism = true;

// Skip pointer move picking
scene.skipPointerMovePicking = true;

// Freeze active meshes
scene.freezeActiveMeshes();
```

### 3. Rendering Optimization

```javascript
// Hardware scaling
engine.setHardwareScalingLevel(0.5); // Render at half resolution

// Adaptive quality
scene.onBeforeRenderObservable.add(() => {
  const fps = engine.getFps();
  if (fps < 30) {
    // Reduce quality
    engine.setHardwareScalingLevel(2);
  } else if (fps > 55) {
    // Increase quality
    engine.setHardwareScalingLevel(1);
  }
});

// Incremental loading
scene.useDelayedTextureLoading = true;

// Culling strategy
mesh.cullingStrategy = BABYLON.AbstractMesh.CULLINGSTRATEGY_BOUNDINGSPHERE_ONLY;
```

### 4. Texture Optimization

```javascript
// Compressed textures
const texture = new BABYLON.Texture('texture.dds', scene);

// Mipmaps
texture.updateSamplingMode(BABYLON.Texture.TRILINEAR_SAMPLINGMODE);

// Anisotropic filtering
texture.anisotropicFilteringLevel = 4;

// KTX2 compression
const texture = new BABYLON.Texture('texture.ktx2', scene);
```

## Common Pitfalls

### Pitfall 1: Memory Leaks

**Problem**: Not disposing resources
```javascript
// ❌ Bad - memory leak
function createAndRemoveMesh() {
  const mesh = BABYLON.MeshBuilder.CreateBox('box', {}, scene);
  scene.removeMesh(mesh);
}
```

**Solution**: Properly dispose
```javascript
// ✅ Good
function createAndRemoveMesh() {
  const mesh = BABYLON.MeshBuilder.CreateBox('box', {}, scene);
  mesh.dispose();
}

// Dispose entire scene
scene.dispose();

// Dispose engine
engine.dispose();
```

### Pitfall 2: Performance Issues with Too Many Draw Calls

**Problem**: Each mesh = one draw call
```javascript
// ❌ Bad - 1000 draw calls
for (let i = 0; i < 1000; i++) {
  const box = BABYLON.MeshBuilder.CreateBox('box' + i, {}, scene);
  box.position.x = i;
}
```

**Solution**: Use instances or merge
```javascript
// ✅ Good - 1 draw call
const box = BABYLON.MeshBuilder.CreateBox('box', {}, scene);
for (let i = 0; i < 1000; i++) {
  const instance = box.createInstance('instance' + i);
  instance.position.x = i;
}
```

### Pitfall 3: Blocking the Main Thread

**Problem**: Heavy computations blocking render
```javascript
// ❌ Bad - blocks rendering
function createManyMeshes() {
  for (let i = 0; i < 10000; i++) {
    const mesh = BABYLON.MeshBuilder.CreateSphere('sphere' + i, {}, scene);
  }
}
```

**Solution**: Use async/incremental loading
```javascript
// ✅ Good - incremental
async function createManyMeshes() {
  for (let i = 0; i < 10000; i++) {
    const mesh = BABYLON.MeshBuilder.CreateSphere('sphere' + i, {}, scene);

    if (i % 100 === 0) {
      await new Promise(resolve => setTimeout(resolve, 0));
    }
  }
}
```

### Pitfall 4: Incorrect Camera Controls

**Problem**: Camera not responding
```javascript
// ❌ Bad - forgot attachControl
const camera = new BABYLON.ArcRotateCamera('camera', 0, 0, 10, BABYLON.Vector3.Zero(), scene);
```

**Solution**: Always attach controls
```javascript
// ✅ Good
const camera = new BABYLON.ArcRotateCamera('camera', 0, 0, 10, BABYLON.Vector3.Zero(), scene);
camera.attachControl(canvas, true);
```

### Pitfall 5: Not Handling Async Operations

**Problem**: Using scene before it's ready
```javascript
// ❌ Bad
BABYLON.SceneLoader.ImportMesh('', 'path/', 'model.gltf', scene);
const mesh = scene.getMeshByName('meshName'); // null!
```

**Solution**: Use callbacks or async/await
```javascript
// ✅ Good
const result = await BABYLON.SceneLoader.ImportMeshAsync('', 'path/', 'model.gltf', scene);
const mesh = scene.getMeshByName('meshName');

// Or with callback
BABYLON.SceneLoader.ImportMesh('', 'path/', 'model.gltf', scene, function(meshes) {
  const mesh = meshes[0];
});
```

### Pitfall 6: Physics Not Working

**Problem**: Forgot to enable physics or create aggregates
```javascript
// ❌ Bad
const sphere = BABYLON.MeshBuilder.CreateSphere('sphere', {}, scene);
sphere.physicsImpostor = new BABYLON.PhysicsImpostor(sphere, BABYLON.PhysicsImpostor.SphereImpostor, {mass: 1}, scene);
// Error: Physics not enabled!
```

**Solution**: Enable physics first, use aggregates
```javascript
// ✅ Good
const havokInstance = await HavokPhysics();
const havokPlugin = new BABYLON.HavokPlugin(true, havokInstance);
scene.enablePhysics(new BABYLON.Vector3(0, -9.8, 0), havokPlugin);

const sphere = BABYLON.MeshBuilder.CreateSphere('sphere', {}, scene);
const aggregate = new BABYLON.PhysicsAggregate(
  sphere,
  BABYLON.PhysicsShapeType.SPHERE,
  {mass: 1},
  scene
);
```

## Advanced Topics

### 1. Custom Shaders

```javascript
BABYLON.Effect.ShadersStore['customVertexShader'] = `
  precision highp float;
  attribute vec3 position;
  attribute vec2 uv;
  uniform mat4 worldViewProjection;
  varying vec2 vUV;

  void main(void) {
    gl_Position = worldViewProjection * vec4(position, 1.0);
    vUV = uv;
  }
`;

BABYLON.Effect.ShadersStore['customFragmentShader'] = `
  precision highp float;
  varying vec2 vUV;
  uniform sampler2D textureSampler;

  void main(void) {
    gl_FragColor = texture2D(textureSampler, vUV);
  }
`;

const shaderMaterial = new BABYLON.ShaderMaterial('shader', scene, {
  vertex: 'custom',
  fragment: 'custom'
}, {
  attributes: ['position', 'uv'],
  uniforms: ['worldViewProjection']
});
```

### 2. Compute Shaders

```javascript
const computeShader = new BABYLON.ComputeShader('compute', engine, {
  computeSource: `
    #version 450
    layout (local_size_x = 8, local_size_y = 8, local_size_z = 1) in;
    layout(std430, binding = 0) buffer OutputBuffer { vec4 data[]; } outputBuffer;

    void main() {
      uint index = gl_GlobalInvocationID.x + gl_GlobalInvocationID.y * 8u;
      outputBuffer.data[index] = vec4(1.0, 0.0, 0.0, 1.0);
    }
  `
});
```

### 3. Procedural Textures

```javascript
const noiseTexture = new BABYLON.NoiseProceduralTexture('noise', 256, scene);
noiseTexture.octaves = 4;
noiseTexture.persistence = 0.8;
noiseTexture.animationSpeedFactor = 5;

material.emissiveTexture = noiseTexture;
```

## Debugging

```javascript
// Show inspector
scene.debugLayer.show();

// Show bounding boxes
scene.forceShowBoundingBoxes = true;

// Show wireframes
material.wireframe = true;

// Log FPS
setInterval(() => {
  console.log('FPS:', engine.getFps());
}, 1000);

// Instrumentation
const instrumentation = new BABYLON.SceneInstrumentation(scene);
instrumentation.captureFrameTime = true;
console.log('Frame time:', instrumentation.frameTimeCounter.average);
```

## Resources

- [Official Documentation](https://doc.babylonjs.com/)
- [Playground](https://playground.babylonjs.com/)
- [Forum](https://forum.babylonjs.com/)
- [Examples](https://doc.babylonjs.com/examples/)
- [NPM Package](https://www.npmjs.com/package/@babylonjs/core)

## Version Notes

This skill is based on Babylon.js 7.x. For latest features, consult the official documentation.



===== FILE: plugins/individual/babylonjs-engine/skills/babylonjs-engine/references/api_reference.md =====

# Babylon.js API Reference

Complete API reference for Babylon.js 7.x covering core classes, methods, and properties.

## Table of Contents

- [Engine](#engine)
- [Scene](#scene)
- [Cameras](#cameras)
- [Lights](#lights)
- [Meshes](#meshes)
- [Materials](#materials)
- [Textures](#textures)
- [Physics](#physics)
- [Animations](#animations)
- [GUI](#gui)
- [Post-Processing](#post-processing)

---

## Engine

### BABYLON.Engine

Main rendering engine that manages the WebGL context and rendering loop.

#### Constructor

```typescript
new Engine(
  canvasOrContext: HTMLCanvasElement | WebGLRenderingContext,
  antialias?: boolean,
  options?: EngineOptions,
  adaptToDeviceRatio?: boolean
): Engine
```

**Parameters:**
- `canvasOrContext`: HTML canvas element or WebGL context
- `antialias`: Enable anti-aliasing (default: false)
- `options`: Engine configuration options
- `adaptToDeviceRatio`: Adapt to device pixel ratio (default: false)

**EngineOptions:**
```typescript
interface EngineOptions {
  preserveDrawingBuffer?: boolean;     // Keep buffer for screenshots
  stencil?: boolean;                   // Enable stencil buffer
  disableWebGL2Support?: boolean;      // Force WebGL 1
  powerPreference?: string;            // "high-performance" | "low-power"
  failIfMajorPerformanceCaveat?: boolean;
  deterministicLockstep?: boolean;     // Fixed timestep
  lockstepMaxSteps?: number;           // Max steps per frame
}
```

#### Properties

```typescript
engine.isFullscreen: boolean                    // Current fullscreen state
engine.isPointerLock: boolean                   // Pointer lock state
engine.scenes: Scene[]                          // All scenes
engine.renderEvenInBackground: boolean          // Continue rendering when tab hidden
engine.enableOfflineSupport: boolean            // Enable IndexedDB caching
engine.doNotHandleContextLost: boolean          // Disable context lost recovery
```

#### Methods

**Rendering**
```typescript
engine.runRenderLoop(renderFunction: () => void): void
engine.stopRenderLoop(renderFunction?: () => void): void
engine.resize(forceResize?: boolean): void
engine.setHardwareScalingLevel(level: number): void    // 1 = native, 2 = half resolution
engine.getHardwareScalingLevel(): number
engine.setSize(width: number, height: number, forceSetSize?: boolean): void
```

**Frame Info**
```typescript
engine.getFps(): number
engine.getDeltaTime(): number                   // Milliseconds since last frame
engine.getTimeStep(): number                    // Time step in ms
```

**State Management**
```typescript
engine.wipeCaches(bruteForce?: boolean): void
engine.dispose(): void
engine.clear(color: Color4, backBuffer: boolean, depth: boolean, stencil?: boolean): void
```

**Screenshots**
```typescript
engine.createScreenshot(
  camera: Camera,
  size: number | { width: number, height: number },
  successCallback: (data: string) => void,
  mimeType?: string,
  forceDownload?: boolean
): void

engine.createScreenshotUsingRenderTarget(
  camera: Camera,
  size: number | { width: number, height: number },
  successCallback: (data: string) => void,
  mimeType?: string,
  samples?: number,
  antialiasing?: boolean,
  fileName?: string
): void
```

---

## Scene

### BABYLON.Scene

Container for all 3D objects, cameras, lights, and materials.

#### Constructor

```typescript
new Scene(
  engine: Engine,
  options?: SceneOptions
): Scene
```

**SceneOptions:**
```typescript
interface SceneOptions {
  useGeometryUniqueIdsMap?: boolean;      // Faster geometry operations
  useMaterialMeshMap?: boolean;           // Faster material operations
  useClonedMeshMap?: boolean;             // Faster clone operations
  virtual?: boolean;                      // Don't render automatically
}
```

#### Properties

**Core**
```typescript
scene.activeCamera: Camera | null               // Current rendering camera
scene.activeCameras: Camera[]                   // For multi-viewport
scene.meshes: AbstractMesh[]                    // All meshes
scene.lights: Light[]                           // All lights
scene.cameras: Camera[]                         // All cameras
scene.materials: Material[]                     // All materials
scene.textures: BaseTexture[]                   // All textures
scene.transformNodes: TransformNode[]           // Transform-only nodes
```

**Rendering**
```typescript
scene.autoClear: boolean                        // Auto-clear buffers
scene.autoClearDepthAndStencil: boolean         // Auto-clear depth/stencil
scene.clearColor: Color4                        // Background color
scene.ambientColor: Color3                      // Ambient lighting color
scene.fogEnabled: boolean                       // Enable fog
scene.fogMode: number                           // Scene.FOGMODE_*
scene.fogDensity: number                        // Fog density
scene.fogStart: number                          // Linear fog start
scene.fogEnd: number                            // Linear fog end
scene.fogColor: Color3                          // Fog color
```

**Optimization**
```typescript
scene.blockMaterialDirtyMechanism: boolean      // Prevent material updates
scene.useDelayedTextureLoading: boolean         // Lazy texture loading
scene.skipPointerMovePicking: boolean           // Disable pointer move picking
scene.forceShowBoundingBoxes: boolean           // Debug bounding boxes
scene.skipFrustumClipping: boolean              // Disable frustum culling
```

**Animation**
```typescript
scene.animationsEnabled: boolean                // Enable animations
scene.useConstantAnimationDeltaTime: boolean    // Fixed timestep
scene.constantlyUpdateMeshUnderPointer: boolean // Continuous picking
```

#### Methods

**Rendering**
```typescript
scene.render(updateCameras?: boolean, ignoreAnimations?: boolean): void
scene.enableDepthRenderer(camera?: Camera, useFloat?: boolean): DepthRenderer
scene.enableGeometryBufferRenderer(ratio?: number): GeometryBufferRenderer
```

**Mesh Management**
```typescript
scene.getMeshByName(name: string): AbstractMesh | null
scene.getMeshById(id: string): AbstractMesh | null
scene.getMeshesByTags(tagsQuery: string): Mesh[]
scene.removeMesh(mesh: AbstractMesh): number
```

**Camera Management**
```typescript
scene.getCameraByName(name: string): Camera | null
scene.getCameraById(id: string): Camera | null
scene.removeCamera(camera: Camera): number
```

**Light Management**
```typescript
scene.getLightByName(name: string): Light | null
scene.getLightById(id: string): Light | null
scene.removeLight(light: Light): number
```

**Material Management**
```typescript
scene.getMaterialByName(name: string): Material | null
scene.getMaterialById(id: string): Material | null
scene.removeMaterial(material: Material): number
```

**Animation**
```typescript
scene.beginAnimation(
  target: any,
  from: number,
  to: number,
  loop?: boolean,
  speedRatio?: number,
  onAnimationEnd?: () => void,
  animatable?: Animatable,
  stopCurrent?: boolean,
  targetMask?: (target: any) => boolean
): Animatable

scene.stopAnimation(target: any, animationName?: string): void
scene.stopAllAnimations(): void
scene.getAnimatableByTarget(target: any): Animatable | null
```

**Picking**
```typescript
scene.pick(
  x: number,
  y: number,
  predicate?: (mesh: AbstractMesh) => boolean,
  fastCheck?: boolean,
  camera?: Camera
): PickingInfo

scene.pickWithRay(
  ray: Ray,
  predicate?: (mesh: AbstractMesh) => boolean,
  fastCheck?: boolean
): PickingInfo

scene.multiPick(
  x: number,
  y: number,
  predicate?: (mesh: AbstractMesh) => boolean,
  camera?: Camera
): PickingInfo[]
```

**Environment**
```typescript
scene.createDefaultEnvironment(options?: IEnvironmentHelperOptions): EnvironmentHelper | null
scene.createDefaultCameraOrLight(
  createArcRotateCamera?: boolean,
  replace?: boolean,
  attachCameraControls?: boolean
): void
scene.createDefaultSkybox(
  environmentTexture?: BaseTexture,
  pbr?: boolean,
  scale?: number,
  blur?: number,
  setGlobalEnvTexture?: boolean
): Mesh | null
```

**Optimization**
```typescript
scene.createOrUpdateSelectionOctree(
  maxCapacity?: number,
  maxDepth?: number
): Octree<AbstractMesh>

scene.freezeActiveMeshes(frustumCullingEnabled?: boolean): Scene
scene.unfreezeActiveMeshes(): Scene
```

**Cleanup**
```typescript
scene.dispose(): void
scene.disposeSounds(): void
```

#### Events (Observables)

```typescript
scene.onBeforeRenderObservable: Observable<Scene>
scene.onAfterRenderObservable: Observable<Scene>
scene.onBeforeAnimationsObservable: Observable<Scene>
scene.onAfterAnimationsObservable: Observable<Scene>
scene.onBeforePhysicsObservable: Observable<Scene>
scene.onAfterPhysicsObservable: Observable<Scene>
scene.onBeforeCameraRenderObservable: Observable<Camera>
scene.onAfterCameraRenderObservable: Observable<Camera>
scene.onReadyObservable: Observable<Scene>
scene.onDataLoadedObservable: Observable<Scene>
scene.onDispose: () => void
scene.onPointerDown: (evt: PointerEvent, pickInfo: PickingInfo) => void
scene.onPointerUp: (evt: PointerEvent, pickInfo: PickingInfo) => void
scene.onPointerMove: (evt: PointerEvent, pickInfo: PickingInfo) => void
scene.onPointerPick: (evt: PointerEvent, pickInfo: PickingInfo) => void
```

---

## Cameras

### Base Camera Properties

```typescript
camera.position: Vector3                        // Camera position
camera.rotation: Vector3                        // Camera rotation (Euler)
camera.fov: number                              // Field of view (radians)
camera.minZ: number                             // Near clipping plane
camera.maxZ: number                             // Far clipping plane
camera.inertia: number                          // Movement smoothing (0-1)
camera.speed: number                            // Movement speed
camera.angularSensibility: number               // Mouse sensitivity
camera.layerMask: number                        // Rendering layers
camera.fovMode: number                          // Camera.FOVMODE_*
```

### BABYLON.FreeCamera

First-person camera with WASD controls.

```typescript
new FreeCamera(
  name: string,
  position: Vector3,
  scene: Scene
): FreeCamera
```

**Properties:**
```typescript
camera.ellipsoid: Vector3                       // Collision ellipsoid
camera.checkCollisions: boolean                 // Enable collisions
camera.applyGravity: boolean                    // Enable gravity
camera.keysUp: number[]                         // Key codes for forward
camera.keysDown: number[]                       // Key codes for backward
camera.keysLeft: number[]                       // Key codes for left
camera.keysRight: number[]                      // Key codes for right
camera.keysUpward: number[]                     // Key codes for up (fly mode)
camera.keysDownward: number[]                   // Key codes for down (fly mode)
```

**Methods:**
```typescript
camera.attachControl(noPreventDefault?: boolean): void
camera.detachControl(): void
camera.setTarget(target: Vector3): void
```

### BABYLON.ArcRotateCamera

Orbital camera that rotates around a target.

```typescript
new ArcRotateCamera(
  name: string,
  alpha: number,        // Horizontal rotation (radians)
  beta: number,         // Vertical rotation (radians)
  radius: number,       // Distance from target
  target: Vector3,      // Look-at point
  scene: Scene
): ArcRotateCamera
```

**Properties:**
```typescript
camera.alpha: number                            // Horizontal angle
camera.beta: number                             // Vertical angle
camera.radius: number                           // Distance
camera.target: Vector3                          // Target position
camera.inertialAlphaOffset: number              // Horizontal momentum
camera.inertialBetaOffset: number               // Vertical momentum
camera.inertialRadiusOffset: number             // Zoom momentum
camera.lowerAlphaLimit: number | null           // Min horizontal
camera.upperAlphaLimit: number | null           // Max horizontal
camera.lowerBetaLimit: number                   // Min vertical (0.01)
camera.upperBetaLimit: number                   // Max vertical (Math.PI - 0.01)
camera.lowerRadiusLimit: number | null          // Min distance
camera.upperRadiusLimit: number | null          // Max distance
camera.panningAxis: Vector3                     // Panning direction
camera.panningInertia: number                   // Panning smoothing
camera.zoomOnFactor: number                     // Zoom speed
camera.wheelPrecision: number                   // Wheel sensitivity
camera.panningSensibility: number               // Pan sensitivity
```

**Methods:**
```typescript
camera.setPosition(position: Vector3): void
camera.setTarget(target: Vector3): void
camera.focusOn(meshesOrMinMaxVectorAndDistance: any, doNotUpdateMaxZ?: boolean): void
camera.zoomOn(meshes?: AbstractMesh[], doNotUpdateMaxZ?: boolean): void
```

### BABYLON.UniversalCamera

Combination of FreeCamera and TouchCamera.

```typescript
new UniversalCamera(
  name: string,
  position: Vector3,
  scene: Scene
): UniversalCamera
```

Inherits all FreeCamera properties and adds touch support.

### BABYLON.FollowCamera

Camera that follows a target mesh.

```typescript
new FollowCamera(
  name: string,
  position: Vector3,
  scene: Scene
): FollowCamera
```

**Properties:**
```typescript
camera.lockedTarget: AbstractMesh               // Mesh to follow
camera.radius: number                           // Distance from target
camera.heightOffset: number                     // Height above target
camera.rotationOffset: number                   // Horizontal offset
camera.cameraAcceleration: number               // Movement speed
camera.maxCameraSpeed: number                   // Max speed
```

---

## Lights

### Base Light Properties

```typescript
light.diffuse: Color3                           // Diffuse color
light.specular: Color3                          // Specular color
light.intensity: number                         // Light intensity (0-1)
light.range: number                             // Effective range
light.includeOnlyMeshes: AbstractMesh[]         // Only affect these
light.includedOnlyMeshes: AbstractMesh[]        // Same as above
light.excludedMeshes: AbstractMesh[]            // Don't affect these
light.excludeWithLayerMask: number              // Layer mask exclusion
light.includeOnlyWithLayerMask: number          // Layer mask inclusion
light.lightmapMode: number                      // Light.LIGHTMAP_*
```

### BABYLON.HemisphericLight

Ambient light with ground color.

```typescript
new HemisphericLight(
  name: string,
  direction: Vector3,
  scene: Scene
): HemisphericLight
```

**Properties:**
```typescript
light.groundColor: Color3                       // Color from below
light.direction: Vector3                        // Light direction
```

### BABYLON.DirectionalLight

Parallel light (sun-like).

```typescript
new DirectionalLight(
  name: string,
  direction: Vector3,
  scene: Scene
): DirectionalLight
```

**Properties:**
```typescript
light.direction: Vector3                        // Light direction
light.position: Vector3                         // For shadow calculation
light.shadowMinZ: number                        // Shadow near plane
light.shadowMaxZ: number                        // Shadow far plane
light.autoUpdateExtends: boolean                // Auto-calculate shadow bounds
light.autoCalcShadowZBounds: boolean            // Auto Z bounds
light.orthoLeft: number                         // Orthographic left
light.orthoRight: number                        // Orthographic right
light.orthoTop: number                          // Orthographic top
light.orthoBottom: number                       // Orthographic bottom
```

### BABYLON.PointLight

Omni-directional point light.

```typescript
new PointLight(
  name: string,
  position: Vector3,
  scene: Scene
): PointLight
```

**Properties:**
```typescript
light.position: Vector3                         // Light position
light.shadowMinZ: number                        // Shadow near plane
light.shadowMaxZ: number                        // Shadow far plane
```

### BABYLON.SpotLight

Focused cone light.

```typescript
new SpotLight(
  name: string,
  position: Vector3,
  direction: Vector3,
  angle: number,
  exponent: number,
  scene: Scene
): SpotLight
```

**Properties:**
```typescript
light.position: Vector3                         // Light position
light.direction: Vector3                        // Light direction
light.angle: number                             // Cone angle (radians)
light.exponent: number                          // Light falloff
light.shadowAngleScale: number                  // Shadow angle scale
light.innerAngle: number                        // Inner cone angle
```

---

## Meshes

### BABYLON.Mesh

Basic 3D mesh object.

#### Constructor

```typescript
new Mesh(
  name: string,
  scene: Scene | null,
  parent?: Node,
  source?: Mesh,
  doNotCloneChildren?: boolean,
  clonePhysicsImpostor?: boolean
): Mesh
```

#### Properties

**Transform**
```typescript
mesh.position: Vector3                          // World position
mesh.rotation: Vector3                          // Euler rotation
mesh.rotationQuaternion: Quaternion | null      // Quaternion rotation
mesh.scaling: Vector3                           // Scale factors
mesh.parent: Node | null                        // Parent node
mesh.billboardMode: number                      // Mesh.BILLBOARDMODE_*
```

**Visibility**
```typescript
mesh.isVisible: boolean                         // Render visibility
mesh.visibility: number                         // Transparency (0-1)
mesh.alphaIndex: number                         // Render order
mesh.infiniteDistance: boolean                  // Always render at distance
mesh.isPickable: boolean                        // Can be picked
mesh.showBoundingBox: boolean                   // Debug bounds
```

**Rendering**
```typescript
mesh.material: Material | null                  // Applied material
mesh.receiveShadows: boolean                    // Receive shadows
mesh.renderingGroupId: number                   // Rendering order group
mesh.layerMask: number                          // Camera layer mask
mesh.alwaysSelectAsActiveMesh: boolean          // Skip frustum culling
mesh.doNotSyncBoundingInfo: boolean             // Skip bounds sync
mesh.isOccluded: boolean                        // Occlusion query result
mesh.isOcclusionQueryInProgress: boolean        // Query in progress
```

**Collisions**
```typescript
mesh.checkCollisions: boolean                   // Enable collision detection
mesh.ellipsoid: Vector3                         // Collision shape
mesh.ellipsoidOffset: Vector3                   // Collision offset
```

**LOD**
```typescript
mesh.useLODScreenCoverage: boolean              // Use screen coverage for LOD
```

#### Methods

**Transform**
```typescript
mesh.setAbsolutePosition(absolutePosition: Vector3): Mesh
mesh.getAbsolutePosition(): Vector3
mesh.setPivotMatrix(matrix: Matrix, postMultiplyPivotMatrix?: boolean): Mesh
mesh.getPivotMatrix(): Matrix
mesh.setPreTransformMatrix(matrix: Matrix): Mesh
mesh.lookAt(targetPoint: Vector3, yawCor?: number, pitchCor?: number, rollCor?: number): Mesh
mesh.translate(axis: Vector3, distance: number, space?: Space): Mesh
mesh.rotate(axis: Vector3, amount: number, space?: Space): Mesh
mesh.rotateAround(point: Vector3, axis: Vector3, amount: number): Mesh
```

**Geometry**
```typescript
mesh.getBoundingInfo(): BoundingInfo
mesh.refreshBoundingInfo(applySkeleton?: boolean): Mesh
mesh.updateVerticesData(kind: string, data: FloatArray, updateExtends?: boolean, makeItUnique?: boolean): Mesh
mesh.getVerticesData(kind: string, copyWhenShared?: boolean, forceCopy?: boolean): FloatArray | null
mesh.getIndices(copyWhenShared?: boolean, forceCopy?: boolean): IndicesArray | null
mesh.getTotalVertices(): number
mesh.getTotalIndices(): number
```

**Cloning**
```typescript
mesh.clone(name: string, newParent?: Node | null, doNotCloneChildren?: boolean): Mesh
mesh.createInstance(name: string): InstancedMesh
```

**LOD**
```typescript
mesh.addLODLevel(distanceOrScreenCoverage: number, mesh: Mesh | null): Mesh
mesh.removeLODLevel(mesh: Mesh): Mesh
mesh.getLODLevelAtDistance(distance: number): Mesh | null
```

**Optimization**
```typescript
mesh.convertToFlatShadedMesh(): Mesh
mesh.convertToUnIndexedMesh(): Mesh
mesh.flipFaces(flipNormals?: boolean): Mesh
mesh.increaseVertices(numberPerEdge: number): void
mesh.forceSharedVertices(): void
mesh.freezeWorldMatrix(newWorldMatrix?: Matrix | null, stopRecursion?: boolean): Mesh
mesh.unfreezeWorldMatrix(): Mesh
```

**Disposal**
```typescript
mesh.dispose(doNotRecurse?: boolean, disposeMaterialAndTextures?: boolean): void
```

### MeshBuilder

Static class for creating built-in shapes.

```typescript
// Box
BABYLON.MeshBuilder.CreateBox(name: string, options: {
  size?: number;
  width?: number;
  height?: number;
  depth?: number;
  faceUV?: Vector4[];
  faceColors?: Color4[];
  sideOrientation?: number;
  frontUVs?: Vector4;
  backUVs?: Vector4;
  wrap?: boolean;
  topBaseAt?: number;
  bottomBaseAt?: number;
  updatable?: boolean;
}, scene?: Scene): Mesh

// Sphere
BABYLON.MeshBuilder.CreateSphere(name: string, options: {
  segments?: number;
  diameter?: number;
  diameterX?: number;
  diameterY?: number;
  diameterZ?: number;
  arc?: number;
  slice?: number;
  sideOrientation?: number;
  frontUVs?: Vector4;
  backUVs?: Vector4;
  updatable?: boolean;
}, scene?: Scene): Mesh

// Cylinder
BABYLON.MeshBuilder.CreateCylinder(name: string, options: {
  height?: number;
  diameterTop?: number;
  diameterBottom?: number;
  diameter?: number;
  tessellation?: number;
  subdivisions?: number;
  arc?: number;
  faceColors?: Color4[];
  faceUV?: Vector4[];
  hasRings?: boolean;
  enclose?: boolean;
  cap?: number;
  sideOrientation?: number;
  frontUVs?: Vector4;
  backUVs?: Vector4;
  updatable?: boolean;
}, scene?: Scene): Mesh

// Plane
BABYLON.MeshBuilder.CreatePlane(name: string, options: {
  size?: number;
  width?: number;
  height?: number;
  sideOrientation?: number;
  frontUVs?: Vector4;
  backUVs?: Vector4;
  updatable?: boolean;
  sourcePlane?: Plane;
}, scene?: Scene): Mesh

// Ground
BABYLON.MeshBuilder.CreateGround(name: string, options: {
  width?: number;
  height?: number;
  subdivisions?: number;
  subdivisionsX?: number;
  subdivisionsY?: number;
  updatable?: boolean;
}, scene?: Scene): Mesh

// Ground from heightmap
BABYLON.MeshBuilder.CreateGroundFromHeightMap(name: string, url: string, options: {
  width?: number;
  height?: number;
  subdivisions?: number;
  minHeight?: number;
  maxHeight?: number;
  colorFilter?: Color3;
  alphaFilter?: number;
  updatable?: boolean;
  onReady?: (mesh: GroundMesh) => void;
}, scene?: Scene): GroundMesh

// Torus
BABYLON.MeshBuilder.CreateTorus(name: string, options: {
  diameter?: number;
  thickness?: number;
  tessellation?: number;
  sideOrientation?: number;
  frontUVs?: Vector4;
  backUVs?: Vector4;
  updatable?: boolean;
}, scene?: Scene): Mesh

// Lines
BABYLON.MeshBuilder.CreateLines(name: string, options: {
  points: Vector3[];
  updatable?: boolean;
  instance?: LinesMesh;
  colors?: Color4[];
  useVertexAlpha?: boolean;
}, scene?: Scene): LinesMesh

// Ribbon
BABYLON.MeshBuilder.CreateRibbon(name: string, options: {
  pathArray: Vector3[][];
  closeArray?: boolean;
  closePath?: boolean;
  offset?: number;
  updatable?: boolean;
  sideOrientation?: number;
  frontUVs?: Vector4;
  backUVs?: Vector4;
  instance?: Mesh;
  invertUV?: boolean;
  uvs?: Vector2[];
  colors?: Color4[];
}, scene?: Scene): Mesh
```

---

## Materials

### BABYLON.StandardMaterial

Basic Phong-based material.

#### Constructor

```typescript
new StandardMaterial(
  name: string,
  scene: Scene
): StandardMaterial
```

#### Properties

**Colors**
```typescript
material.diffuseColor: Color3                   // Main color
material.specularColor: Color3                  // Highlight color
material.emissiveColor: Color3                  // Self-illumination
material.ambientColor: Color3                   // Ambient contribution
material.specularPower: number                  // Shininess (1-128)
```

**Textures**
```typescript
material.diffuseTexture: BaseTexture | null     // Albedo map
material.ambientTexture: BaseTexture | null     // Ambient occlusion
material.opacityTexture: BaseTexture | null     // Transparency map
material.reflectionTexture: BaseTexture | null  // Environment/reflection
material.emissiveTexture: BaseTexture | null    // Emission map
material.specularTexture: BaseTexture | null    // Specular map
material.bumpTexture: BaseTexture | null        // Normal/bump map
material.lightmapTexture: BaseTexture | null    // Baked lighting
material.refractionTexture: BaseTexture | null  // Refraction map
```

**Rendering**
```typescript
material.alpha: number                          // Opacity (0-1)
material.backFaceCulling: boolean               // Cull back faces
material.cullBackFaces: boolean                 // Same as above
material.sideOrientation: number                // Material.SIDE_*
material.alphaMode: number                      // Material.ALPHA_*
material.transparencyMode: number | null        // Material.MATERIAL_*
material.wireframe: boolean                     // Render as wireframe
material.pointsCloud: boolean                   // Render as points
material.fillMode: number                       // Material.FILLMODE_*
```

**Lighting**
```typescript
material.useEmissiveAsIllumination: boolean     // Emissive as light
material.linkEmissiveWithDiffuse: boolean       // Tie colors
material.useSpecularOverAlpha: boolean          // Spec on transparent
material.useReflectionOverAlpha: boolean        // Refl on transparent
material.useAlphaFromDiffuseTexture: boolean    // Alpha from diffuse
material.useParallax: boolean                   // Parallax mapping
material.useParallaxOcclusion: boolean          // Parallax occlusion
material.parallaxScaleBias: number              // Parallax strength
material.roughness: number                      // Surface roughness
material.useLightmapAsShadowmap: boolean        // Lightmap = shadows
material.useGlossinessFromSpecularMapAlpha: boolean  // Glossiness source
```

**Fresnel**
```typescript
material.diffuseFresnelParameters: FresnelParameters | null
material.opacityFresnelParameters: FresnelParameters | null
material.reflectionFresnelParameters: FresnelParameters | null
material.emissiveFresnelParameters: FresnelParameters | null
material.refractionFresnelParameters: FresnelParameters | null
```

#### Methods

```typescript
material.clone(name: string): StandardMaterial
material.dispose(forceDisposeEffect?: boolean, forceDisposeTextures?: boolean): void
material.freeze(): void
material.unfreeze(): void
material.needAlphaBlending(): boolean
material.needAlphaTesting(): boolean
```

### BABYLON.PBRMaterial

Physically based rendering material.

#### Constructor

```typescript
new PBRMaterial(
  name: string,
  scene: Scene
): PBRMaterial
```

#### Properties

**Metallic-Roughness Workflow**
```typescript
material.metallic: number | null                // Metalness (0-1)
material.roughness: number | null               // Roughness (0-1)
material.metallicTexture: BaseTexture | null    // Metallic map
material.roughnessTexture: BaseTexture | null   // Roughness map (if separate)
material.metallicRoughnessTexture: BaseTexture | null  // Combined MR map
material.baseColor: Color3                      // Base color
material.baseTexture: BaseTexture | null        // Base color map
material.albedoColor: Color3                    // Same as baseColor
material.albedoTexture: BaseTexture | null      // Same as baseTexture
```

**Specular-Glossiness Workflow**
```typescript
material.reflectivityColor: Color3              // Specular color
material.reflectivityTexture: BaseTexture | null  // Specular map
material.microSurface: number                   // Glossiness (0-1)
material.microSurfaceTexture: BaseTexture | null  // Glossiness map
material.useMicroSurfaceFromReflectivityMapAlpha: boolean
```

**Other Maps**
```typescript
material.bumpTexture: BaseTexture | null        // Normal map
material.ambientTexture: BaseTexture | null     // Ambient occlusion
material.ambientTextureStrength: number         // AO strength
material.emissiveTexture: BaseTexture | null    // Emission map
material.emissiveColor: Color3                  // Emission color
material.emissiveIntensity: number              // Emission strength
material.lightmapTexture: BaseTexture | null    // Lightmap
material.opacityTexture: BaseTexture | null     // Opacity map
```

**Environment**
```typescript
material.environmentTexture: BaseTexture | null  // IBL/reflection
material.environmentIntensity: number           // Environment strength
material.useRadianceOverAlpha: boolean          // Refl over alpha
material.useSpecularOverAlpha: boolean          // Spec over alpha
```

**Rendering**
```typescript
material.alpha: number                          // Opacity (0-1)
material.transparencyMode: number | null        // PBRMaterial.PBRMATERIAL_*
material.alphaCutOff: number                    // Alpha test threshold
material.directIntensity: number                // Direct light multiplier
material.emissiveIntensity: number              // Emissive multiplier
material.environmentIntensity: number           // Environment multiplier
material.specularIntensity: number              // Specular multiplier
material.disableLighting: boolean               // Unlit mode
material.unlit: boolean                         // Same as above
```

**Advanced**
```typescript
material.usePhysicalLightFalloff: boolean       // Inverse square falloff
material.useRadianceOcclusion: boolean          // Radiance AO
material.useHorizonOcclusion: boolean           // Horizon AO
material.useAlphaFromAlbedoTexture: boolean     // Alpha from albedo
material.forceIrradianceInFragment: boolean     // Force fragment irradiance
material.realTimeFiltering: boolean             // Real-time filtering
material.realTimeFilteringQuality: number       // Filtering quality
```

---

## Textures

### BABYLON.Texture

2D texture from image file.

#### Constructor

```typescript
new Texture(
  url: string | null,
  sceneOrEngine: Scene | ThinEngine,
  noMipmap?: boolean,
  invertY?: boolean,
  samplingMode?: number,
  onLoad?: (() => void) | null,
  onError?: ((message?: string, exception?: any) => void) | null,
  buffer?: string | ArrayBuffer | ArrayBufferView | HTMLImageElement | Blob | ImageBitmap | null,
  deleteBuffer?: boolean,
  format?: number,
  mimeType?: string
): Texture
```

#### Properties

```typescript
texture.url: string | null                      // Texture URL
texture.uOffset: number                         // U offset
texture.vOffset: number                         // V offset
texture.uScale: number                          // U scale
texture.vScale: number                          // V scale
texture.uAng: number                            // U rotation
texture.vAng: number                            // V rotation
texture.wAng: number                            // W rotation
texture.wrapU: number                           // Texture.WRAP_*
texture.wrapV: number                           // Texture.WRAP_*
texture.coordinatesMode: number                 // Texture.MODE_*
texture.coordinatesIndex: number                // UV channel
texture.level: number                           // Texture level
texture.hasAlpha: boolean                       // Has alpha channel
texture.getAlphaFromRGB: boolean                // Alpha from luminance
texture.invertZ: boolean                        // Invert Z (for normal maps)
texture.isBlocking: boolean                     // Block until loaded
```

#### Methods

```typescript
texture.clone(): Texture
texture.dispose(): void
texture.updateURL(url: string, buffer?: string | ArrayBuffer | ArrayBufferView | HTMLImageElement | Blob, onLoad?: () => void): void
texture.updateSamplingMode(samplingMode: number): void
```

### BABYLON.CubeTexture

Cubemap texture for reflections/environment.

```typescript
new CubeTexture(
  rootUrl: string,
  sceneOrEngine: Scene | ThinEngine,
  extensions?: string[] | null,
  noMipmap?: boolean,
  files?: string[] | null,
  onLoad?: (() => void) | null,
  onError?: ((message?: string, exception?: any) => void) | null,
  format?: number,
  prefiltered?: boolean,
  forcedExtension?: string | null
): CubeTexture

// Create from prefiltered DDS
CubeTexture.CreateFromPrefilteredData(url: string, scene: Scene, forcedExtension?: string): CubeTexture
```

### BABYLON.RenderTargetTexture

Render-to-texture for effects.

```typescript
new RenderTargetTexture(
  name: string,
  size: number | { width: number, height: number } | { ratio: number },
  scene?: Scene,
  generateMipMaps?: boolean,
  doNotChangeAspectRatio?: boolean,
  type?: number,
  isCube?: boolean,
  samplingMode?: number,
  generateDepthBuffer?: boolean,
  generateStencilBuffer?: boolean,
  isMulti?: boolean,
  format?: number,
  delayAllocation?: boolean
): RenderTargetTexture
```

**Properties:**
```typescript
renderTarget.renderList: AbstractMesh[] | null  // Meshes to render
renderTarget.activeCamera: Camera | null        // Render camera
renderTarget.refreshRate: number                // Update frequency
renderTarget.clearColor: Color4                 // Clear color
```

---

## Physics

### Physics Engine Setup

```typescript
// Enable physics
scene.enablePhysics(
  gravity?: Vector3,
  plugin?: IPhysicsEnginePlugin
): boolean

// Default gravity
const gravity = new BABYLON.Vector3(0, -9.8, 0);

// Havok plugin
const havokInstance = await HavokPhysics();
const havokPlugin = new BABYLON.HavokPlugin(true, havokInstance);

scene.enablePhysics(gravity, havokPlugin);
```

### BABYLON.PhysicsAggregate

Physics body for a mesh (Havok v2).

```typescript
new PhysicsAggregate(
  transformNode: TransformNode,
  type: PhysicsShapeType,
  options?: PhysicsAggregateParameters,
  scene?: Scene
): PhysicsAggregate
```

**PhysicsShapeType:**
```typescript
BABYLON.PhysicsShapeType.SPHERE
BABYLON.PhysicsShapeType.BOX
BABYLON.PhysicsShapeType.CAPSULE
BABYLON.PhysicsShapeType.CYLINDER
BABYLON.PhysicsShapeType.CONVEX_HULL
BABYLON.PhysicsShapeType.MESH
BABYLON.PhysicsShapeType.HEIGHTFIELD
BABYLON.PhysicsShapeType.CONTAINER
```

**PhysicsAggregateParameters:**
```typescript
interface PhysicsAggregateParameters {
  mass?: number;                                // 0 = static
  restitution?: number;                         // Bounciness (0-1)
  friction?: number;                            // Surface friction
  startAsleep?: boolean;                        // Start inactive
  ignoreChildren?: boolean;                     // Ignore child meshes
  disableBidirectionalTransformation?: boolean;
  pressure?: number;                            // For soft bodies
  stiffness?: number;                           // For soft bodies
  velocityIterations?: number;
  positionIterations?: number;
}
```

**Properties:**
```typescript
aggregate.body: PhysicsBody                     // Physics body
aggregate.shape: PhysicsShape                   // Collision shape
aggregate.transformNode: TransformNode          // Associated node
```

**Methods:**
```typescript
aggregate.dispose(): void
```

### BABYLON.PhysicsBody

Physics body control.

```typescript
body.setMassProperties(props: { mass?: number, inertia?: Vector3, centerOfMass?: Vector3 }): void
body.getMass(): number
body.setLinearVelocity(velocity: Vector3): void
body.getLinearVelocity(): Vector3
body.setAngularVelocity(velocity: Vector3): void
body.getAngularVelocity(): Vector3
body.applyForce(force: Vector3, location: Vector3): void
body.applyImpulse(impulse: Vector3, location: Vector3): void
body.setMotionType(motionType: PhysicsMotionType): void
body.getMotionType(): PhysicsMotionType
body.setLinearDamping(damping: number): void
body.setAngularDamping(damping: number): void
body.setCollisionCallbackEnabled(enabled: boolean): void
```

### BABYLON.PhysicsRaycastResult

Raycast result.

```typescript
scene.physicsEngine?.raycast(from: Vector3, to: Vector3): PhysicsRaycastResult

interface PhysicsRaycastResult {
  hasHit: boolean;
  hitPointWorld: Vector3;
  hitNormalWorld: Vector3;
  hitFraction: number;
  body?: PhysicsBody;
}
```

---

## Animations

### BABYLON.Animation

Property animation.

#### Constructor

```typescript
new Animation(
  name: string,
  targetProperty: string,
  framePerSecond: number,
  dataType: number,
  loopMode?: number,
  enableBlending?: boolean
): Animation
```

**Data Types:**
```typescript
Animation.ANIMATIONTYPE_FLOAT
Animation.ANIMATIONTYPE_VECTOR2
Animation.ANIMATIONTYPE_VECTOR3
Animation.ANIMATIONTYPE_QUATERNION
Animation.ANIMATIONTYPE_MATRIX
Animation.ANIMATIONTYPE_COLOR3
Animation.ANIMATIONTYPE_COLOR4
Animation.ANIMATIONTYPE_SIZE
```

**Loop Modes:**
```typescript
Animation.ANIMATIONLOOPMODE_RELATIVE  // Continue from current
Animation.ANIMATIONLOOPMODE_CYCLE     // Loop
Animation.ANIMATIONLOOPMODE_CONSTANT  // Stop at end
Animation.ANIMATIONLOOPMODE_YOYO      // Ping-pong
```

#### Methods

```typescript
animation.setKeys(keys: IAnimationKey[]): void

interface IAnimationKey {
  frame: number;
  value: any;
  inTangent?: any;
  outTangent?: any;
  interpolation?: AnimationKeyInterpolation;
}

// Helper
Animation.CreateAndStartAnimation(
  name: string,
  node: Node,
  targetProperty: string,
  framePerSecond: number,
  totalFrame: number,
  from: any,
  to: any,
  loopMode?: number,
  easingFunction?: EasingFunction,
  onAnimationEnd?: () => void
): Animatable
```

### BABYLON.AnimationGroup

Group of synchronized animations.

```typescript
const animationGroup = new BABYLON.AnimationGroup('group', scene);
animationGroup.addTargetedAnimation(animation: Animation, target: any): TargetedAnimation;

// Control
animationGroup.play(loop?: boolean): void
animationGroup.pause(): void
animationGroup.stop(): void
animationGroup.reset(): void
animationGroup.goToFrame(frame: number): void
animationGroup.speedRatio = 2.0;  // 2x speed
```

---

## GUI

### BABYLON.GUI.AdvancedDynamicTexture

2D UI container.

```typescript
// Fullscreen UI
const advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI('UI', true, scene);

// Mesh UI
const plane = BABYLON.MeshBuilder.CreatePlane('plane', {size: 2}, scene);
const advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateForMesh(plane, 1024, 1024);

// Add controls
advancedTexture.addControl(control);
```

### Common Controls

```typescript
// Button
const button = BABYLON.GUI.Button.CreateSimpleButton('button', 'Click Me');
button.width = '150px';
button.height = '40px';
button.color = 'white';
button.background = 'green';
button.onPointerUpObservable.add(() => console.log('Clicked'));

// TextBlock
const text = new BABYLON.GUI.TextBlock();
text.text = 'Hello';
text.color = 'white';
text.fontSize = 24;

// Rectangle
const rect = new BABYLON.GUI.Rectangle();
rect.width = '400px';
rect.height = '200px';
rect.background = 'red';

// Image
const image = new BABYLON.GUI.Image('image', 'url');
image.width = '100px';
image.height = '100px';

// Slider
const slider = new BABYLON.GUI.Slider();
slider.minimum = 0;
slider.maximum = 100;
slider.value = 50;
slider.onValueChangedObservable.add((value) => console.log(value));
```

---

## Post-Processing

### BABYLON.DefaultRenderingPipeline

All-in-one post-processing.

```typescript
const pipeline = new BABYLON.DefaultRenderingPipeline(
  'pipeline',
  true,      // HDR
  scene,
  [camera]   // cameras
);

// FXAA
pipeline.fxaaEnabled = true;

// Bloom
pipeline.bloomEnabled = true;
pipeline.bloomThreshold = 0.8;
pipeline.bloomWeight = 0.5;
pipeline.bloomKernel = 64;

// Image processing
pipeline.imageProcessingEnabled = true;
pipeline.imageProcessing.contrast = 1.5;
pipeline.imageProcessing.exposure = 1.0;
pipeline.imageProcessing.toneMappingEnabled = true;

// Depth of field
pipeline.depthOfFieldEnabled = true;
pipeline.depthOfField.focusDistance = 2000;
pipeline.depthOfField.focalLength = 50;

// Chromatic aberration
pipeline.chromaticAberrationEnabled = true;
pipeline.chromaticAberration.aberrationAmount = 30;

// Grain
pipeline.grainEnabled = true;
pipeline.grain.intensity = 10;

// Sharpen
pipeline.sharpenEnabled = true;
pipeline.sharpen.edgeAmount = 0.3;
```

---

## Constants Reference

### Texture Constants

```typescript
// Wrap modes
Texture.CLAMP_ADDRESSMODE
Texture.WRAP_ADDRESSMODE
Texture.MIRROR_ADDRESSMODE

// Sampling modes
Texture.NEAREST_SAMPLINGMODE
Texture.BILINEAR_SAMPLINGMODE
Texture.TRILINEAR_SAMPLINGMODE

// Coordinate modes
Texture.EXPLICIT_MODE
Texture.SPHERICAL_MODE
Texture.PLANAR_MODE
Texture.CUBIC_MODE
Texture.PROJECTION_MODE
Texture.SKYBOX_MODE
Texture.INVCUBIC_MODE
Texture.EQUIRECTANGULAR_MODE
Texture.FIXED_EQUIRECTANGULAR_MODE
```

### Material Constants

```typescript
// Side orientation
Material.ClockWiseSideOrientation
Material.CounterClockWiseSideOrientation

// Fill modes
Material.PointFillMode
Material.WireFrameFillMode
Material.TriangleFillMode

// Alpha modes
Material.ALPHA_DISABLE
Material.ALPHA_ADD
Material.ALPHA_COMBINE
Material.ALPHA_SUBTRACT
Material.ALPHA_MULTIPLY
Material.ALPHA_MAXIMIZED
Material.ALPHA_ONEONE
Material.ALPHA_PREMULTIPLIED
Material.ALPHA_INTERPOLATE
```

---

This reference covers the most commonly used Babylon.js APIs. For complete documentation, visit: https://doc.babylonjs.com/



===== FILE: plugins/individual/babylonjs-engine/agents/babylonjs-engine-architect.md =====

# Babylon.js Architect

## Role

Expert 3D/graphics architect specializing in Babylon.js scene design, optimization, and best practices.

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
3. Implement best practices from Babylon.js ecosystem
4. Optimize for target platforms and devices
5. Provide detailed implementation guidance

## Tools

This agent has access to:
- Babylon.js skill knowledge
- Optimization checklists and patterns
- Performance profiling guidance
- Asset pipeline recommendations



===== FILE: plugins/individual/babylonjs-engine/commands/mesh_builder.md =====

# /babylonjs-engine-mesh_builder

Babylon.js - Mesh Builder

## Description

Executes the mesh_builder script for Babylon.js.

## Usage

```bash
/babylonjs-engine-mesh_builder
```

## Implementation

This command runs the `mesh_builder.py` script from the Babylon.js skill, which provides automated assistance for mesh builder.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/babylonjs-engine/commands/scene_generator.md =====

# /babylonjs-engine-scene_generator

Babylon.js - Scene Generator

## Description

Executes the scene_generator script for Babylon.js.

## Usage

```bash
/babylonjs-engine-scene_generator
```

## Implementation

This command runs the `scene_generator.py` script from the Babylon.js skill, which provides automated assistance for scene generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/babylonjs-engine/skills/babylonjs-engine/scripts/mesh_builder.py =====

```py
#!/usr/bin/env python3
"""
Babylon.js Mesh Builder

Interactive tool for generating Babylon.js mesh creation code.
Supports all MeshBuilder shapes with full parameter customization.

Usage:
    python3 mesh_builder.py --shape sphere --name mySphere --output meshes.js
    python3 mesh_builder.py --shape box --params '{"size": 2}' --typescript
    python3 mesh_builder.py --interactive
"""

import argparse
import json
import sys
from pathlib import Path


MESH_SHAPES = {
    'box': {
        'description': 'Rectangular box',
        'params': {
            'size': {'type': 'number', 'default': 1, 'description': 'Overall size'},
            'width': {'type': 'number', 'description': 'Width (X axis)'},
            'height': {'type': 'number', 'description': 'Height (Y axis)'},
            'depth': {'type': 'number', 'description': 'Depth (Z axis)'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'sphere': {
        'description': 'Sphere/ellipsoid',
        'params': {
            'diameter': {'type': 'number', 'default': 1, 'description': 'Overall diameter'},
            'diameterX': {'type': 'number', 'description': 'X diameter'},
            'diameterY': {'type': 'number', 'description': 'Y diameter'},
            'diameterZ': {'type': 'number', 'description': 'Z diameter'},
            'segments': {'type': 'number', 'default': 32, 'description': 'Segments'},
            'arc': {'type': 'number', 'default': 1, 'description': 'Horizontal coverage (0-1)'},
            'slice': {'type': 'number', 'default': 1, 'description': 'Vertical coverage (0-1)'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'cylinder': {
        'description': 'Cylinder/cone',
        'params': {
            'height': {'type': 'number', 'default': 2, 'description': 'Height'},
            'diameter': {'type': 'number', 'default': 1, 'description': 'Overall diameter'},
            'diameterTop': {'type': 'number', 'description': 'Top diameter (for cone)'},
            'diameterBottom': {'type': 'number', 'description': 'Bottom diameter'},
            'tessellation': {'type': 'number', 'default': 24, 'description': 'Radial segments'},
            'subdivisions': {'type': 'number', 'default': 1, 'description': 'Height subdivisions'},
            'arc': {'type': 'number', 'default': 1, 'description': 'Arc coverage (0-1)'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'plane': {
        'description': 'Flat plane',
        'params': {
            'size': {'type': 'number', 'default': 1, 'description': 'Overall size'},
            'width': {'type': 'number', 'description': 'Width'},
            'height': {'type': 'number', 'description': 'Height'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'ground': {
        'description': 'Ground plane',
        'params': {
            'width': {'type': 'number', 'default': 1, 'description': 'Width'},
            'height': {'type': 'number', 'default': 1, 'description': 'Height (depth)'},
            'subdivisions': {'type': 'number', 'default': 1, 'description': 'Subdivisions'},
            'subdivisionsX': {'type': 'number', 'description': 'X subdivisions'},
            'subdivisionsY': {'type': 'number', 'description': 'Y subdivisions'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'torus': {
        'description': 'Torus (donut)',
        'params': {
            'diameter': {'type': 'number', 'default': 1, 'description': 'Overall diameter'},
            'thickness': {'type': 'number', 'default': 0.5, 'description': 'Tube thickness'},
            'tessellation': {'type': 'number', 'default': 16, 'description': 'Radial segments'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'torus-knot': {
        'description': 'Torus knot',
        'params': {
            'radius': {'type': 'number', 'default': 2, 'description': 'Overall radius'},
            'tube': {'type': 'number', 'default': 0.5, 'description': 'Tube radius'},
            'radialSegments': {'type': 'number', 'default': 32, 'description': 'Radial segments'},
            'tubularSegments': {'type': 'number', 'default': 32, 'description': 'Tube segments'},
            'p': {'type': 'number', 'default': 2, 'description': 'P parameter'},
            'q': {'type': 'number', 'default': 3, 'description': 'Q parameter'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'capsule': {
        'description': 'Capsule (cylinder with rounded ends)',
        'params': {
            'radius': {'type': 'number', 'default': 0.5, 'description': 'Radius'},
            'height': {'type': 'number', 'default': 2, 'description': 'Height'},
            'radiusTop': {'type': 'number', 'description': 'Top radius'},
            'radiusBottom': {'type': 'number', 'description': 'Bottom radius'},
            'tessellation': {'type': 'number', 'default': 16, 'description': 'Segments'},
            'subdivisions': {'type': 'number', 'default': 1, 'description': 'Height subdivisions'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'lines': {
        'description': 'Line segments',
        'params': {
            'points': {'type': 'vector3[]', 'description': 'Array of Vector3 points'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'ribbon': {
        'description': 'Ribbon from path array',
        'params': {
            'pathArray': {'type': 'vector3[][]', 'description': '2D array of Vector3 paths'},
            'closeArray': {'type': 'boolean', 'default': False, 'description': 'Close the ribbon'},
            'closePath': {'type': 'boolean', 'default': False, 'description': 'Close each path'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'tube': {
        'description': 'Tube along path',
        'params': {
            'path': {'type': 'vector3[]', 'description': 'Path curve'},
            'radius': {'type': 'number', 'default': 1, 'description': 'Tube radius'},
            'tessellation': {'type': 'number', 'default': 64, 'description': 'Radial segments'},
            'cap': {'type': 'number', 'default': 0, 'description': 'Cap mode (0-3)'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'polyhedron': {
        'description': 'Regular polyhedron',
        'params': {
            'type': {'type': 'number', 'default': 0, 'description': 'Type (0-19)'},
            'size': {'type': 'number', 'default': 1, 'description': 'Size'},
            'sizeX': {'type': 'number', 'description': 'X size'},
            'sizeY': {'type': 'number', 'description': 'Y size'},
            'sizeZ': {'type': 'number', 'description': 'Z size'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    },
    'icosphere': {
        'description': 'Geodesic sphere',
        'params': {
            'radius': {'type': 'number', 'default': 1, 'description': 'Radius'},
            'radiusX': {'type': 'number', 'description': 'X radius'},
            'radiusY': {'type': 'number', 'description': 'Y radius'},
            'radiusZ': {'type': 'number', 'description': 'Z radius'},
            'subdivisions': {'type': 'number', 'default': 4, 'description': 'Subdivisions'},
            'flat': {'type': 'boolean', 'default': True, 'description': 'Flat shading'},
            'updatable': {'type': 'boolean', 'default': False}
        }
    }
}

MATERIAL_PRESETS = {
    'standard': {
        'description': 'Basic Standard Material',
        'code': """const material = new StandardMaterial('{name}Material', scene);
material.diffuseColor = new Color3(1, 0, 0);
material.specularColor = new Color3(0.5, 0.5, 0.5);
material.specularPower = 32;
{mesh}.material = material;"""
    },
    'pbr': {
        'description': 'PBR Material',
        'code': """const material = new PBRMaterial('{name}Material', scene);
material.metallic = 1.0;
material.roughness = 0.3;
material.baseColor = new Color3(0.9, 0.9, 0.9);
{mesh}.material = material;"""
    },
    'textured': {
        'description': 'Textured Standard Material',
        'code': """const material = new StandardMaterial('{name}Material', scene);
material.diffuseTexture = new Texture('path/to/texture.jpg', scene);
{mesh}.material = material;"""
    }
}


def generate_mesh_code(shape, name, params, use_typescript, material_preset=None):
    """Generate mesh creation code."""
    # Convert shape name
    shape_func = ''.join(word.capitalize() for word in shape.split('-'))

    # Build parameters
    param_strs = []
    for key, value in params.items():
        if isinstance(value, bool):
            param_strs.append(f'{key}: {str(value).lower()}')
        elif isinstance(value, (int, float)):
            param_strs.append(f'{key}: {value}')
        elif isinstance(value, str):
            param_strs.append(f'{key}: {value}')  # Assume already formatted

    params_str = ', '.join(param_strs) if param_strs else ''

    # Generate code
    code = f"const {name} = Create{shape_func}('{name}', {{ {params_str} }}, scene);"

    # Add material if specified
    if material_preset and material_preset in MATERIAL_PRESETS:
        material_code = MATERIAL_PRESETS[material_preset]['code'].format(
            name=name,
            mesh=name
        )
        code = f"{code}\n\n{material_code}"

    return code


def generate_imports(shapes, use_typescript, include_materials):
    """Generate imports for mesh builders."""
    ext = '' if use_typescript else '.js'
    imports = set()

    # Shape imports
    for shape in shapes:
        shape_func = ''.join(word.capitalize() for word in shape.split('-'))
        builder_name = shape.split('-')[0] + 'Builder'  # e.g., boxBuilder, sphereBuilder

        if shape in ['lines', 'ribbon', 'tube']:
            imports.add(f"import {{ Create{shape_func} }} from '@babylonjs/core/Meshes/Builders/{shape}Builder{ext}';")
        else:
            imports.add(f"import {{ Create{shape_func} }} from '@babylonjs/core/Meshes/Builders/{builder_name}{ext}';")

    # Material imports
    if include_materials:
        imports.add(f"import {{ StandardMaterial }} from '@babylonjs/core/Materials/standardMaterial{ext}';")
        imports.add(f"import {{ PBRMaterial }} from '@babylonjs/core/Materials/PBR/pbrMaterial{ext}';")
        imports.add(f"import {{ Texture }} from '@babylonjs/core/Materials/Textures/texture{ext}';")
        imports.add(f"import {{ Color3 }} from '@babylonjs/core/Maths/math.color{ext}';")

    return '\n'.join(sorted(imports))


def interactive_mode():
    """Interactive CLI for mesh building."""
    print("\n🎨 Babylon.js Mesh Builder - Interactive Mode\n")

    meshes = []

    while True:
        # Shape selection
        print("\nSelect mesh shape:")
        shapes_list = list(MESH_SHAPES.keys())
        for i, shape in enumerate(shapes_list, 1):
            desc = MESH_SHAPES[shape]['description']
            print(f"  {i:2d}. {shape:15s} - {desc}")

        shape_choice = input("\nEnter number (or 'done' to finish): ").strip()

        if shape_choice.lower() == 'done':
            break

        shape = shapes_list[int(shape_choice) - 1]

        # Mesh name
        default_name = f"{shape.replace('-', '')}1"
        name = input(f"\nMesh name (default: {default_name}): ").strip() or default_name

        # Parameters
        print(f"\nConfigure {shape} parameters (press Enter for defaults):")
        params = {}
        for param_name, param_info in MESH_SHAPES[shape]['params'].items():
            if param_info['type'] in ['vector3[]', 'vector3[][]']:
                # Skip complex types in interactive mode
                continue

            prompt = f"  {param_name}"
            if 'default' in param_info:
                prompt += f" (default: {param_info['default']})"
            if 'description' in param_info:
                prompt += f" - {param_info['description']}"
            prompt += ": "

            value = input(prompt).strip()

            if value:
                if param_info['type'] == 'boolean':
                    params[param_name] = value.lower() in ['true', 'yes', 'y', '1']
                elif param_info['type'] == 'number':
                    params[param_name] = float(value) if '.' in value else int(value)
                else:
                    params[param_name] = value

        # Material
        print("\nAdd material?")
        print("  1. None")
        print("  2. Standard Material")
        print("  3. PBR Material")
        print("  4. Textured Material")

        material_choice = input("\nEnter number (default: 1): ").strip() or "1"
        material_preset = None
        if material_choice == '2':
            material_preset = 'standard'
        elif material_choice == '3':
            material_preset = 'pbr'
        elif material_choice == '4':
            material_preset = 'textured'

        meshes.append({
            'shape': shape,
            'name': name,
            'params': params,
            'material': material_preset
        })

        print(f"\n✅ Added {name}")

    if not meshes:
        print("\n❌ No meshes created")
        return

    # Generate code
    use_typescript = input("\nGenerate TypeScript? (y/N): ").strip().lower() == 'y'

    ext = 'ts' if use_typescript else 'js'
    output_file = input(f"\nOutput file (default: meshes.{ext}): ").strip() or f"meshes.{ext}"

    # Build code
    shapes = list(set(m['shape'] for m in meshes))
    has_materials = any(m['material'] for m in meshes)

    imports = generate_imports(shapes, use_typescript, has_materials)

    mesh_codes = []
    for mesh in meshes:
        code = generate_mesh_code(
            mesh['shape'],
            mesh['name'],
            mesh['params'],
            use_typescript,
            mesh['material']
        )
        mesh_codes.append(code)

    final_code = f"""// Generated by Babylon.js Mesh Builder
{imports}

export function createMeshes(scene{': Scene' if use_typescript else ''}) {{
  {chr(10).join('  ' + line for mc in mesh_codes for line in mc.split(chr(10)))}
}}
"""

    Path(output_file).write_text(final_code)
    print(f"\n✅ Generated: {output_file}")
    print(f"📝 Created {len(meshes)} mesh(es)")


def main():
    parser = argparse.ArgumentParser(
        description='Generate Babylon.js mesh creation code',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--shape',
        choices=list(MESH_SHAPES.keys()),
        help='Mesh shape'
    )

    parser.add_argument(
        '--name',
        default='mesh1',
        help='Mesh name (default: mesh1)'
    )

    parser.add_argument(
        '--params',
        type=json.loads,
        default={},
        help='Mesh parameters as JSON'
    )

    parser.add_argument(
        '--material',
        choices=list(MATERIAL_PRESETS.keys()),
        help='Material preset'
    )

    parser.add_argument(
        '--typescript',
        action='store_true',
        help='Generate TypeScript'
    )

    parser.add_argument(
        '--output',
        help='Output file'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive mode'
    )

    parser.add_argument(
        '--list-shapes',
        action='store_true',
        help='List available shapes'
    )

    args = parser.parse_args()

    # List shapes
    if args.list_shapes:
        print("\nAvailable mesh shapes:\n")
        for shape, info in MESH_SHAPES.items():
            print(f"  {shape}:")
            print(f"    {info['description']}")
            print(f"    Parameters:")
            for param, details in info['params'].items():
                default = f" (default: {details['default']})" if 'default' in details else ""
                desc = details.get('description', '')
                print(f"      - {param}: {details['type']}{default} - {desc}")
            print()
        return

    # Interactive mode
    if args.interactive or not args.shape:
        interactive_mode()
        return

    # Generate from args
    ext = 'ts' if args.typescript else 'js'
    output_file = args.output or f"mesh_{args.name}.{ext}"

    shapes = [args.shape]
    has_materials = args.material is not None

    imports = generate_imports(shapes, args.typescript, has_materials)
    mesh_code = generate_mesh_code(
        args.shape,
        args.name,
        args.params,
        args.typescript,
        args.material
    )

    final_code = f"""// Generated by Babylon.js Mesh Builder
{imports}

export function createMesh(scene{': Scene' if args.typescript else ''}) {{
  {chr(10).join('  ' + line for line in mesh_code.split(chr(10)))}
}}
"""

    Path(output_file).write_text(final_code)
    print(f"✅ Generated: {output_file}")


if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/babylonjs-engine/skills/babylonjs-engine/scripts/scene_generator.py =====

```py
#!/usr/bin/env python3
"""
Babylon.js Scene Generator

Generates Babylon.js scene boilerplate with various configurations.
Supports multiple scene types, cameras, lighting setups, and physics.

Usage:
    python3 scene_generator.py --type basic --name MyScene --output scene.js
    python3 scene_generator.py --type physics --camera arc-rotate --typescript
    python3 scene_generator.py --interactive
"""

import argparse
import sys
from pathlib import Path


SCENE_TYPES = {
    'basic': {
        'description': 'Basic scene with camera, light, and ground',
        'includes': ['camera', 'light', 'ground']
    },
    'physics': {
        'description': 'Scene with Havok physics enabled',
        'includes': ['camera', 'light', 'ground', 'physics', 'sphere']
    },
    'pbr': {
        'description': 'PBR materials showcase scene',
        'includes': ['camera', 'light', 'pbr-meshes', 'environment']
    },
    'model-viewer': {
        'description': 'GLTF model loading and viewing',
        'includes': ['arc-camera', 'light', 'model-loader', 'environment']
    },
    'vr': {
        'description': 'WebXR VR scene',
        'includes': ['camera', 'light', 'ground', 'webxr']
    },
    'particles': {
        'description': 'Particle system showcase',
        'includes': ['camera', 'light', 'particles']
    },
    'gui': {
        'description': 'Scene with 2D GUI elements',
        'includes': ['camera', 'light', 'ground', 'gui']
    },
    'post-processing': {
        'description': 'Scene with post-processing effects',
        'includes': ['camera', 'light', 'meshes', 'post-processing']
    }
}

CAMERA_TYPES = {
    'free': 'FreeCamera',
    'arc-rotate': 'ArcRotateCamera',
    'universal': 'UniversalCamera',
    'follow': 'FollowCamera'
}


def generate_imports(scene_type, use_typescript, camera_type):
    """Generate ES6 imports based on scene configuration."""
    if use_typescript:
        imports = [
            "import { Engine } from '@babylonjs/core/Engines/engine';",
            "import { Scene } from '@babylonjs/core/scene';",
            "import { Vector3 } from '@babylonjs/core/Maths/math.vector';",
            "import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';",
        ]
    else:
        imports = [
            "import { Engine } from '@babylonjs/core/Engines/engine.js';",
            "import { Scene } from '@babylonjs/core/scene.js';",
            "import { Vector3 } from '@babylonjs/core/Maths/math.vector.js';",
            "import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight.js';",
        ]

    # Camera imports
    camera_import_map = {
        'free': "FreeCamera } from '@babylonjs/core/Cameras/freeCamera",
        'arc-rotate': "ArcRotateCamera } from '@babylonjs/core/Cameras/arcRotateCamera",
        'universal': "UniversalCamera } from '@babylonjs/core/Cameras/universalCamera",
        'follow': "FollowCamera } from '@babylonjs/core/Cameras/followCamera"
    }

    camera_import = camera_import_map.get(camera_type, camera_import_map['arc-rotate'])
    imports.append(f"import {{ {camera_import}{'js' if not use_typescript else ''}';}}")

    config = SCENE_TYPES[scene_type]

    # Mesh builders
    if 'ground' in config['includes'] or 'meshes' in config['includes']:
        if use_typescript:
            imports.append("import { CreateGround } from '@babylonjs/core/Meshes/Builders/groundBuilder';")
            imports.append("import { CreateSphere } from '@babylonjs/core/Meshes/Builders/sphereBuilder';")
            imports.append("import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';")
        else:
            imports.append("import { CreateGround } from '@babylonjs/core/Meshes/Builders/groundBuilder.js';")
            imports.append("import { CreateSphere } from '@babylonjs/core/Meshes/Builders/sphereBuilder.js';")
            imports.append("import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder.js';")

    # Physics
    if 'physics' in config['includes']:
        if use_typescript:
            imports.append("import HavokPhysics from '@babylonjs/havok';")
            imports.append("import { HavokPlugin } from '@babylonjs/core/Physics/v2/Plugins/havokPlugin';")
            imports.append("import { PhysicsAggregate } from '@babylonjs/core/Physics/v2/physicsAggregate';")
            imports.append("import { PhysicsShapeType } from '@babylonjs/core/Physics/v2/IPhysicsEnginePlugin';")
        else:
            imports.append("import HavokPhysics from '@babylonjs/havok';")
            imports.append("import { HavokPlugin } from '@babylonjs/core/Physics/v2/Plugins/havokPlugin.js';")
            imports.append("import { PhysicsAggregate } from '@babylonjs/core/Physics/v2/physicsAggregate.js';")
            imports.append("import { PhysicsShapeType } from '@babylonjs/core/Physics/v2/IPhysicsEnginePlugin.js';")

    # PBR
    if 'pbr-meshes' in config['includes']:
        if use_typescript:
            imports.append("import { PBRMaterial } from '@babylonjs/core/Materials/PBR/pbrMaterial';")
        else:
            imports.append("import { PBRMaterial } from '@babylonjs/core/Materials/PBR/pbrMaterial.js';")

    # Environment
    if 'environment' in config['includes']:
        if use_typescript:
            imports.append("import { CubeTexture } from '@babylonjs/core/Materials/Textures/cubeTexture';")
        else:
            imports.append("import { CubeTexture } from '@babylonjs/core/Materials/Textures/cubeTexture.js';")

    # Model loader
    if 'model-loader' in config['includes']:
        if use_typescript:
            imports.append("import { SceneLoader } from '@babylonjs/core/Loading/sceneLoader';")
            imports.append("import '@babylonjs/loaders/glTF';")
        else:
            imports.append("import { SceneLoader } from '@babylonjs/core/Loading/sceneLoader.js';")
            imports.append("import '@babylonjs/loaders/glTF';")

    # WebXR
    if 'webxr' in config['includes']:
        if use_typescript:
            imports.append("import '@babylonjs/core/Helpers/sceneHelpers';")
        else:
            imports.append("import '@babylonjs/core/Helpers/sceneHelpers.js';")

    # GUI
    if 'gui' in config['includes']:
        if use_typescript:
            imports.append("import { AdvancedDynamicTexture } from '@babylonjs/gui/2D/advancedDynamicTexture';")
            imports.append("import { Button } from '@babylonjs/gui/2D/controls/button';")
        else:
            imports.append("import { AdvancedDynamicTexture } from '@babylonjs/gui/2D/advancedDynamicTexture.js';")
            imports.append("import { Button } from '@babylonjs/gui/2D/controls/button.js';")

    # Particles
    if 'particles' in config['includes']:
        if use_typescript:
            imports.append("import { ParticleSystem } from '@babylonjs/core/Particles/particleSystem';")
            imports.append("import { Texture } from '@babylonjs/core/Materials/Textures/texture';")
        else:
            imports.append("import { ParticleSystem } from '@babylonjs/core/Particles/particleSystem.js';")
            imports.append("import { Texture } from '@babylonjs/core/Materials/Textures/texture.js';")

    # Post-processing
    if 'post-processing' in config['includes']:
        if use_typescript:
            imports.append("import { DefaultRenderingPipeline } from '@babylonjs/core/PostProcesses/RenderPipeline/Pipelines/defaultRenderingPipeline';")
        else:
            imports.append("import { DefaultRenderingPipeline } from '@babylonjs/core/PostProcesses/RenderPipeline/Pipelines/defaultRenderingPipeline.js';")

    return '\n'.join(imports)


def generate_camera_code(camera_type, use_typescript):
    """Generate camera setup code."""
    if camera_type == 'free':
        return """  // Create FreeCamera
  const camera = new FreeCamera('camera', new Vector3(0, 5, -10), scene);
  camera.setTarget(Vector3.Zero());
  camera.attachControl(canvas, true);
  camera.speed = 0.5;
  camera.angularSensibility = 2000;"""

    elif camera_type == 'arc-rotate':
        return """  // Create ArcRotateCamera
  const camera = new ArcRotateCamera(
    'camera',
    -Math.PI / 2,
    Math.PI / 2.5,
    10,
    Vector3.Zero(),
    scene
  );
  camera.attachControl(canvas, true);
  camera.lowerRadiusLimit = 5;
  camera.upperRadiusLimit = 50;"""

    elif camera_type == 'universal':
        return """  // Create UniversalCamera
  const camera = new UniversalCamera('camera', new Vector3(0, 5, -10), scene);
  camera.setTarget(Vector3.Zero());
  camera.attachControl(canvas, true);
  camera.checkCollisions = true;
  camera.applyGravity = true;"""

    elif camera_type == 'follow':
        return """  // Create FollowCamera
  const camera = new FollowCamera('camera', new Vector3(0, 10, -10), scene);
  camera.radius = 10;
  camera.heightOffset = 5;
  camera.rotationOffset = 0;
  camera.cameraAcceleration = 0.05;
  camera.maxCameraSpeed = 10;
  camera.attachControl(canvas, true);"""

    return ""


def generate_scene_code(scene_type, camera_type, use_typescript):
    """Generate scene setup code based on type."""
    config = SCENE_TYPES[scene_type]

    code = []

    # Camera
    code.append(generate_camera_code(camera_type, use_typescript))

    # Light
    code.append("""
  // Create light
  const light = new HemisphericLight('light', new Vector3(0, 1, 0), scene);
  light.intensity = 0.7;""")

    # Ground
    if 'ground' in config['includes']:
        code.append("""
  // Create ground
  const ground = CreateGround('ground', { width: 10, height: 10 }, scene);""")

    # Physics
    if 'physics' in config['includes']:
        code.append("""
  // Initialize Havok physics
  const havokInstance = await HavokPhysics();
  const havokPlugin = new HavokPlugin(true, havokInstance);
  scene.enablePhysics(new Vector3(0, -9.8, 0), havokPlugin);

  // Create sphere with physics
  const sphere = CreateSphere('sphere', { diameter: 2 }, scene);
  sphere.position.y = 5;

  const sphereAggregate = new PhysicsAggregate(
    sphere,
    PhysicsShapeType.SPHERE,
    { mass: 1, restitution: 0.75 },
    scene
  );

  const groundAggregate = new PhysicsAggregate(
    ground,
    PhysicsShapeType.BOX,
    { mass: 0 },
    scene
  );""")

    # PBR materials
    if 'pbr-meshes' in config['includes']:
        code.append("""
  // Create PBR materials
  const pbrMaterial = new PBRMaterial('pbr', scene);
  pbrMaterial.metallic = 1.0;
  pbrMaterial.roughness = 0.3;
  pbrMaterial.baseColor = new BABYLON.Color3(0.9, 0.9, 0.9);

  const sphere = CreateSphere('sphere', { diameter: 2 }, scene);
  sphere.position.y = 1;
  sphere.material = pbrMaterial;

  const box = CreateBox('box', { size: 1.5 }, scene);
  box.position.set(3, 0.75, 0);

  const boxMaterial = new PBRMaterial('boxMaterial', scene);
  boxMaterial.metallic = 0.0;
  boxMaterial.roughness = 0.8;
  boxMaterial.baseColor = new BABYLON.Color3(0.8, 0.2, 0.2);
  box.material = boxMaterial;""")

    # Environment
    if 'environment' in config['includes']:
        code.append("""
  // Create default environment
  const env = scene.createDefaultEnvironment({
    createGround: true,
    createSkybox: true,
    skyboxSize: 150
  });""")

    # Model loader
    if 'model-loader' in config['includes']:
        code.append("""
  // Load GLTF model
  const result = await SceneLoader.ImportMeshAsync(
    null,
    'https://assets.babylonjs.com/meshes/',
    'village.glb',
    scene
  );

  console.log('Loaded meshes:', result.meshes.length);""")

    # WebXR
    if 'webxr' in config['includes']:
        code.append("""
  // Enable WebXR
  const env = scene.createDefaultEnvironment();
  const xr = await scene.createDefaultXRExperienceAsync({
    floorMeshes: [env.ground]
  });""")

    # GUI
    if 'gui' in config['includes']:
        code.append("""
  // Create 2D UI
  const advancedTexture = AdvancedDynamicTexture.CreateFullscreenUI('UI');

  const button = Button.CreateSimpleButton('button', 'Click Me');
  button.width = '150px';
  button.height = '40px';
  button.color = 'white';
  button.background = 'green';
  button.onPointerUpObservable.add(() => {
    console.log('Button clicked');
  });

  advancedTexture.addControl(button);""")

    # Particles
    if 'particles' in config['includes']:
        code.append("""
  // Create particle system
  const particleSystem = new ParticleSystem('particles', 2000, scene);
  particleSystem.particleTexture = new Texture('https://assets.babylonjs.com/textures/flare.png', scene);

  particleSystem.emitter = new Vector3(0, 5, 0);
  particleSystem.minEmitBox = new Vector3(-1, 0, 0);
  particleSystem.maxEmitBox = new Vector3(1, 0, 0);

  particleSystem.color1 = new BABYLON.Color4(0.7, 0.8, 1.0, 1.0);
  particleSystem.color2 = new BABYLON.Color4(0.2, 0.5, 1.0, 1.0);
  particleSystem.colorDead = new BABYLON.Color4(0, 0, 0.2, 0.0);

  particleSystem.minSize = 0.1;
  particleSystem.maxSize = 0.5;

  particleSystem.minLifeTime = 0.3;
  particleSystem.maxLifeTime = 1.5;

  particleSystem.emitRate = 1500;
  particleSystem.direction1 = new Vector3(-1, 8, 1);
  particleSystem.direction2 = new Vector3(1, 8, -1);
  particleSystem.gravity = new Vector3(0, -9.81, 0);

  particleSystem.start();""")

    # Post-processing
    if 'post-processing' in config['includes']:
        code.append("""
  // Add post-processing
  const pipeline = new DefaultRenderingPipeline('pipeline', true, scene, [camera]);
  pipeline.fxaaEnabled = true;
  pipeline.samples = 4;

  pipeline.bloomEnabled = true;
  pipeline.bloomThreshold = 0.8;
  pipeline.bloomWeight = 0.5;
  pipeline.bloomKernel = 64;

  // Create some meshes
  const sphere = CreateSphere('sphere', { diameter: 2 }, scene);
  sphere.position.y = 1;

  const box = CreateBox('box', { size: 1.5 }, scene);
  box.position.set(3, 0.75, 0);

  const ground = CreateGround('ground', { width: 10, height: 10 }, scene);""")

    return '\n'.join(code)


def generate_scene_file(scene_type, camera_type, use_typescript, scene_name):
    """Generate complete scene file."""
    ext = 'ts' if use_typescript else 'js'

    imports = generate_imports(scene_type, use_typescript, camera_type)
    scene_code = generate_scene_code(scene_type, camera_type, use_typescript)

    is_async = 'physics' in SCENE_TYPES[scene_type]['includes'] or \
               'model-loader' in SCENE_TYPES[scene_type]['includes'] or \
               'webxr' in SCENE_TYPES[scene_type]['includes']

    template = f"""// {scene_name} - Generated by Babylon.js Scene Generator
{imports}

// Get canvas element
const canvas = document.getElementById('renderCanvas'){' as HTMLCanvasElement' if use_typescript else ''};

// Create engine
const engine = new Engine(canvas, true, {{
  preserveDrawingBuffer: true,
  stencil: true
}});

// Create scene
const createScene = {'async ' if is_async else ''}function(){': Scene' if use_typescript else ''} {{
  const scene = new Scene(engine);

{scene_code}

  return scene;
}};

// Initialize and run
{'(async () => {' if is_async else ''}
const scene = {'await ' if is_async else ''}createScene();

// Run render loop
engine.runRenderLoop(() => {{
  scene.render();
}});

// Handle resize
window.addEventListener('resize', () => {{
  engine.resize();
}});
{'})();' if is_async else ''}
"""

    return template


def interactive_mode():
    """Interactive CLI for scene generation."""
    print("\n🎮 Babylon.js Scene Generator - Interactive Mode\n")

    # Scene type
    print("Select scene type:")
    for i, (key, config) in enumerate(SCENE_TYPES.items(), 1):
        print(f"  {i}. {key}: {config['description']}")

    scene_choice = input("\nEnter number (1-8): ").strip()
    scene_type = list(SCENE_TYPES.keys())[int(scene_choice) - 1]

    # Camera type
    print("\nSelect camera type:")
    for i, (key, value) in enumerate(CAMERA_TYPES.items(), 1):
        print(f"  {i}. {key}: {value}")

    camera_choice = input("\nEnter number (1-4, default 2): ").strip() or "2"
    camera_type = list(CAMERA_TYPES.keys())[int(camera_choice) - 1]

    # TypeScript
    use_typescript = input("\nUse TypeScript? (y/N): ").strip().lower() == 'y'

    # Scene name
    scene_name = input("\nScene name (default: MyScene): ").strip() or "MyScene"

    # Output file
    ext = 'ts' if use_typescript else 'js'
    default_output = f"{scene_name.lower().replace(' ', '_')}.{ext}"
    output_file = input(f"\nOutput file (default: {default_output}): ").strip() or default_output

    # Generate
    print(f"\n✨ Generating {scene_type} scene...")
    code = generate_scene_file(scene_type, camera_type, use_typescript, scene_name)

    Path(output_file).write_text(code)
    print(f"✅ Scene generated: {output_file}")

    # Instructions
    print(f"\n📝 Next steps:")
    print(f"  1. Install dependencies: npm install @babylonjs/core @babylonjs/loaders")
    if 'gui' in SCENE_TYPES[scene_type]['includes']:
        print(f"     npm install @babylonjs/gui")
    if 'physics' in SCENE_TYPES[scene_type]['includes']:
        print(f"     npm install @babylonjs/havok")
    print(f"  2. Create HTML file with <canvas id='renderCanvas'></canvas>")
    print(f"  3. Import this scene file")
    print(f"  4. Run dev server")


def main():
    parser = argparse.ArgumentParser(
        description='Generate Babylon.js scene boilerplate',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--type',
        choices=list(SCENE_TYPES.keys()),
        help='Scene type'
    )

    parser.add_argument(
        '--camera',
        choices=list(CAMERA_TYPES.keys()),
        default='arc-rotate',
        help='Camera type (default: arc-rotate)'
    )

    parser.add_argument(
        '--typescript',
        action='store_true',
        help='Generate TypeScript instead of JavaScript'
    )

    parser.add_argument(
        '--name',
        default='MyScene',
        help='Scene name (default: MyScene)'
    )

    parser.add_argument(
        '--output',
        help='Output file path'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive mode'
    )

    parser.add_argument(
        '--list-types',
        action='store_true',
        help='List available scene types'
    )

    args = parser.parse_args()

    # List types
    if args.list_types:
        print("\nAvailable scene types:\n")
        for key, config in SCENE_TYPES.items():
            print(f"  {key}:")
            print(f"    {config['description']}")
            print(f"    Includes: {', '.join(config['includes'])}\n")
        return

    # Interactive mode
    if args.interactive or not args.type:
        interactive_mode()
        return

    # Generate from args
    ext = 'ts' if args.typescript else 'js'
    output_file = args.output or f"{args.name.lower().replace(' ', '_')}.{ext}"

    print(f"✨ Generating {args.type} scene...")
    code = generate_scene_file(args.type, args.camera, args.typescript, args.name)

    Path(output_file).write_text(code)
    print(f"✅ Scene generated: {output_file}")


if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/babylonjs-engine/skills/babylonjs-engine/assets/examples/README.md =====

# Babylon.js Real-World Examples

Comprehensive collection of production-ready Babylon.js patterns and implementations.

## Table of Contents

- [Model Loading & Optimization](#model-loading--optimization)
- [Advanced Materials](#advanced-materials)
- [Physics Simulations](#physics-simulations)
- [Particle Systems](#particle-systems)
- [Post-Processing Effects](#post-processing-effects)
- [GUI & User Interface](#gui--user-interface)
- [WebXR & VR](#webxr--vr)
- [Performance Optimization](#performance-optimization)
- [Camera Systems](#camera-systems)
- [Animation Patterns](#animation-patterns)

---

## Model Loading & Optimization

### GLTF Model Viewer with Progress

```javascript
import { SceneLoader } from '@babylonjs/core/Loading/sceneLoader.js';
import { Texture } from '@babylonjs/core/Materials/Textures/texture.js';
import { PBRMaterial } from '@babylonjs/core/Materials/PBR/pbrMaterial.js';
import '@babylonjs/loaders/glTF';

async function createModelViewer(scene, modelUrl, fileName) {
  // Show loading progress
  let loadingScreen = document.getElementById('loading');

  BABYLON.SceneLoader.OnPluginActivatedObservable.addOnce((loader) => {
    loader.onProgress = (event) => {
      const progress = event.lengthComputable
        ? (event.loaded / event.total) * 100
        : 0;

      if (loadingScreen) {
        loadingScreen.textContent = `Loading: ${progress.toFixed(0)}%`;
      }
    };
  });

  // Load model
  const result = await SceneLoader.ImportMeshAsync(
    null,
    modelUrl,
    fileName,
    scene
  );

  if (loadingScreen) {
    loadingScreen.style.display = 'none';
  }

  // Center model
  const meshes = result.meshes;
  const boundingBox = meshes[0].getHierarchyBoundingVectors();
  const center = BABYLON.Vector3.Center(boundingBox.min, boundingBox.max);

  meshes.forEach(mesh => {
    mesh.position.subtractInPlace(center);
  });

  // Scale to fit
  const size = boundingBox.max.subtract(boundingBox.min);
  const maxDimension = Math.max(size.x, size.y, size.z);
  const scale = 5 / maxDimension;

  result.meshes[0].scaling.scaleInPlace(scale);

  // Setup environment
  const envTexture = BABYLON.CubeTexture.CreateFromPrefilteredData(
    'https://assets.babylonjs.com/environments/environmentSpecular.env',
    scene
  );
  scene.environmentTexture = envTexture;

  // Apply PBR to all meshes
  meshes.forEach(mesh => {
    if (mesh.material && mesh.material.albedoTexture) {
      // Already has material, enhance it
      mesh.material.environmentIntensity = 1.0;
    } else if (!mesh.material) {
      // No material, create default
      const pbr = new PBRMaterial('defaultPBR', scene);
      pbr.metallic = 0.0;
      pbr.roughness = 0.5;
      pbr.baseColor = new BABYLON.Color3(0.8, 0.8, 0.8);
      mesh.material = pbr;
    }
  });

  return result;
}
```

### Optimized LOD (Level of Detail)

```javascript
async function createLODMesh(scene, highResUrl, medResUrl, lowResUrl) {
  // Load all LOD levels
  const highRes = await SceneLoader.ImportMeshAsync(null, '', highResUrl, scene);
  const medRes = await SceneLoader.ImportMeshAsync(null, '', medResUrl, scene);
  const lowRes = await SceneLoader.ImportMeshAsync(null, '', lowResUrl, scene);

  const mainMesh = highRes.meshes[0];
  const medMesh = medRes.meshes[0];
  const lowMesh = lowRes.meshes[0];

  // Add LOD levels
  mainMesh.addLODLevel(15, medMesh);   // Switch at 15 units
  mainMesh.addLODLevel(30, lowMesh);   // Switch at 30 units
  mainMesh.addLODLevel(50, null);      // Don't render beyond 50 units

  return mainMesh;
}
```

### Mesh Simplification

```javascript
async function simplifyMesh(mesh, quality = 0.5) {
  const simplified = await mesh.simplify(
    [
      { quality: quality, distance: 10 },
      { quality: quality * 0.5, distance: 25 },
      { quality: quality * 0.25, distance: 50 }
    ],
    true,  // parallelProcessing
    BABYLON.SimplificationType.QUADRATIC
  );

  return simplified;
}
```

### Batch Model Loading

```javascript
async function batchLoadModels(scene, models) {
  const assetsManager = new BABYLON.AssetsManager(scene);

  const loadedMeshes = [];

  models.forEach((model, index) => {
    const task = assetsManager.addMeshTask(
      `model${index}`,
      '',
      model.path,
      model.filename
    );

    task.onSuccess = (task) => {
      task.loadedMeshes.forEach(mesh => {
        mesh.position = model.position || BABYLON.Vector3.Zero();
        mesh.scaling = model.scale || new BABYLON.Vector3(1, 1, 1);
      });

      loadedMeshes.push(...task.loadedMeshes);
    };

    task.onError = (task, message, exception) => {
      console.error(`Failed to load ${model.filename}:`, message);
    };
  });

  return new Promise((resolve) => {
    assetsManager.onFinish = (tasks) => {
      resolve(loadedMeshes);
    };

    assetsManager.load();
  });
}

// Usage
const models = [
  { path: '/models/', filename: 'car.glb', position: new BABYLON.Vector3(0, 0, 0) },
  { path: '/models/', filename: 'tree.glb', position: new BABYLON.Vector3(5, 0, 0), scale: new BABYLON.Vector3(2, 2, 2) },
  { path: '/models/', filename: 'building.glb', position: new BABYLON.Vector3(-5, 0, 0) }
];

const meshes = await batchLoadModels(scene, models);
```

---

## Advanced Materials

### PBR Material with All Maps

```javascript
function createAdvancedPBRMaterial(scene) {
  const pbr = new BABYLON.PBRMaterial('advancedPBR', scene);

  // Base color
  pbr.albedoTexture = new BABYLON.Texture('textures/albedo.png', scene);

  // Metallic and roughness (combined in one texture)
  pbr.metallicTexture = new BABYLON.Texture('textures/metallic_roughness.png', scene);
  pbr.useRoughnessFromMetallicTextureAlpha = false;
  pbr.useMetallnessFromMetallicTextureBlue = true;

  // Normal map
  pbr.bumpTexture = new BABYLON.Texture('textures/normal.png', scene);
  pbr.invertNormalMapX = false;
  pbr.invertNormalMapY = false;

  // Ambient occlusion
  pbr.ambientTexture = new BABYLON.Texture('textures/ao.png', scene);
  pbr.useAmbientOcclusionFromMetallicTextureRed = true;
  pbr.ambientTextureStrength = 1.0;

  // Emissive
  pbr.emissiveTexture = new BABYLON.Texture('textures/emissive.png', scene);
  pbr.emissiveColor = new BABYLON.Color3(1, 1, 1);
  pbr.emissiveIntensity = 1.0;

  // Environment
  pbr.environmentIntensity = 1.0;
  pbr.reflectionTexture = scene.environmentTexture;

  // Advanced settings
  pbr.directIntensity = 1.0;
  pbr.specularIntensity = 1.0;
  pbr.usePhysicalLightFalloff = true;
  pbr.useRadianceOverAlpha = true;

  return pbr;
}
```

### Glass Material

```javascript
function createGlassMaterial(scene) {
  const glass = new BABYLON.PBRMaterial('glass', scene);

  glass.metallic = 0.0;
  glass.roughness = 0.0;
  glass.alpha = 0.3;
  glass.alphaCutOff = 0.0;

  glass.indexOfRefraction = 1.52; // Glass IOR

  glass.reflectionTexture = scene.environmentTexture;
  glass.refractionTexture = scene.environmentTexture;
  glass.refractionTexture.refractionDepth = 0.8;

  glass.linkRefractionWithTransparency = true;

  glass.baseColor = new BABYLON.Color3(0.95, 0.95, 1.0);

  glass.environmentIntensity = 1.0;

  return glass;
}
```

### Water Material

```javascript
import { WaterMaterial } from '@babylonjs/materials/water/waterMaterial.js';

function createWaterMaterial(scene) {
  const water = new WaterMaterial('water', scene, new BABYLON.Vector2(512, 512));

  water.bumpTexture = new BABYLON.Texture('textures/waterbump.png', scene);
  water.windForce = -5;
  water.waveHeight = 0.3;
  water.bumpHeight = 0.1;
  water.windDirection = new BABYLON.Vector2(1, 1);

  water.waterColor = new BABYLON.Color3(0.1, 0.3, 0.5);
  water.colorBlendFactor = 0.3;

  water.waveLength = 0.1;

  // Add meshes to reflect/refract
  water.addToRenderList(skybox);
  water.addToRenderList(terrain);
  water.addToRenderList(buildings);

  return water;
}
```

### Node Material (Visual Shader)

```javascript
async function createNodeMaterial(scene) {
  // Load from snippet
  const nodeMaterial = await BABYLON.NodeMaterial.ParseFromSnippetAsync(
    '#SNIPPET_ID',
    scene
  );

  // Or create programmatically
  const nodeMaterial2 = new BABYLON.NodeMaterial('node', scene);

  // Input blocks
  const position = new BABYLON.InputBlock('position');
  position.setAsAttribute('position');

  const worldPos = new BABYLON.TransformBlock('worldPos');
  const worldViewProjection = new BABYLON.InputBlock('worldViewProjection');
  worldViewProjection.setAsSystemValue(BABYLON.NodeMaterialSystemValues.WorldViewProjection);

  const worldPosMult = new BABYLON.MultiplyBlock('worldPosMult');
  worldPosMult.left.connectTo(worldViewProjection.output);
  worldPosMult.right.connectTo(worldPos.output);

  // Fragment output
  const fragmentOutput = new BABYLON.FragmentOutputBlock('fragmentOutput');
  const color = new BABYLON.ColorBlock('color');
  color.value = new BABYLON.Color3(1, 0, 0);

  fragmentOutput.rgb.connectTo(color.output);

  nodeMaterial2.addOutputNode(fragmentOutput);

  nodeMaterial2.build();

  return nodeMaterial2;
}
```

### Dynamic Material Switching

```javascript
class MaterialSwitcher {
  constructor(mesh, materials) {
    this.mesh = mesh;
    this.materials = materials;
    this.currentIndex = 0;
  }

  switchMaterial() {
    this.currentIndex = (this.currentIndex + 1) % this.materials.length;
    this.mesh.material = this.materials[this.currentIndex];
  }

  setMaterial(index) {
    if (index >= 0 && index < this.materials.length) {
      this.currentIndex = index;
      this.mesh.material = this.materials[index];
    }
  }

  getCurrentMaterial() {
    return this.materials[this.currentIndex];
  }
}

// Usage
const materials = [
  createPBRMaterial(scene),
  createGlassMaterial(scene),
  createMetallicMaterial(scene)
];

const switcher = new MaterialSwitcher(mesh, materials);

// Switch on click
scene.onPointerDown = () => {
  switcher.switchMaterial();
};
```

---

## Physics Simulations

### Ragdoll Physics

```javascript
async function createRagdoll(scene, mesh) {
  const havokInstance = await HavokPhysics();
  const havokPlugin = new BABYLON.HavokPlugin(true, havokInstance);
  scene.enablePhysics(new BABYLON.Vector3(0, -9.8, 0), havokPlugin);

  // Create physics bodies for each bone
  const skeleton = mesh.skeleton;

  const bonePhysics = [];

  skeleton.bones.forEach((bone, index) => {
    const boneMatrix = bone.getTransformNode();

    if (boneMatrix) {
      // Create capsule for bone
      const capsule = BABYLON.MeshBuilder.CreateCapsule(
        `bone_${index}`,
        {
          radius: 0.05,
          height: 0.3
        },
        scene
      );

      capsule.position = boneMatrix.position.clone();
      capsule.rotation = boneMatrix.rotation.clone();

      // Add physics
      const aggregate = new BABYLON.PhysicsAggregate(
        capsule,
        BABYLON.PhysicsShapeType.CAPSULE,
        { mass: 0.5, friction: 0.5 },
        scene
      );

      bonePhysics.push({ bone, capsule, aggregate });
    }
  });

  // Add constraints between bones
  for (let i = 0; i < bonePhysics.length - 1; i++) {
    const current = bonePhysics[i];
    const next = bonePhysics[i + 1];

    // Create joint
    const constraint = new BABYLON.PhysicsConstraint(
      BABYLON.PhysicsConstraintType.HINGE,
      {
        pivotA: new BABYLON.Vector3(0, 0.15, 0),
        pivotB: new BABYLON.Vector3(0, -0.15, 0),
        axisA: new BABYLON.Vector3(1, 0, 0),
        axisB: new BABYLON.Vector3(1, 0, 0)
      },
      [
        { body: current.aggregate.body },
        { body: next.aggregate.body }
      ],
      scene
    );
  }

  return bonePhysics;
}
```

### Cloth Simulation

```javascript
function createCloth(scene, width = 10, height = 10, segments = 20) {
  const cloth = BABYLON.MeshBuilder.CreateGround(
    'cloth',
    { width, height, subdivisions: segments },
    scene
  );

  // Make updatable
  cloth.convertToFlatShadedMesh();

  const positions = cloth.getVerticesData(BABYLON.VertexBuffer.PositionKind);
  const indices = cloth.getIndices();

  // Create particles for each vertex
  const particles = [];
  for (let i = 0; i < positions.length; i += 3) {
    particles.push({
      position: new BABYLON.Vector3(positions[i], positions[i + 1], positions[i + 2]),
      previous: new BABYLON.Vector3(positions[i], positions[i + 1], positions[i + 2]),
      pinned: positions[i + 1] >= height / 2 - 0.1 // Pin top row
    });
  }

  // Update function
  const gravity = new BABYLON.Vector3(0, -9.8, 0);
  const damping = 0.99;
  const timestep = 1 / 60;

  scene.onBeforeRenderObservable.add(() => {
    // Verlet integration
    particles.forEach(particle => {
      if (particle.pinned) return;

      const velocity = particle.position.subtract(particle.previous);
      particle.previous.copyFrom(particle.position);

      const acceleration = gravity.scale(timestep * timestep);
      particle.position.addInPlace(velocity.scale(damping)).addInPlace(acceleration);
    });

    // Constrain distances
    for (let iteration = 0; iteration < 5; iteration++) {
      for (let i = 0; i < indices.length; i += 3) {
        const p1 = particles[indices[i]];
        const p2 = particles[indices[i + 1]];

        if (p1.pinned && p2.pinned) continue;

        const diff = p1.position.subtract(p2.position);
        const distance = diff.length();
        const restDistance = width / segments;

        const correction = diff.scale((distance - restDistance) / distance * 0.5);

        if (!p1.pinned) p1.position.subtractInPlace(correction);
        if (!p2.pinned) p2.position.addInPlace(correction);
      }
    }

    // Update mesh
    const newPositions = [];
    particles.forEach(p => {
      newPositions.push(p.position.x, p.position.y, p.position.z);
    });

    cloth.updateVerticesData(BABYLON.VertexBuffer.PositionKind, newPositions);
    cloth.refreshBoundingInfo();
  });

  return cloth;
}
```

### Vehicle Physics

```javascript
class Vehicle {
  constructor(scene, position) {
    this.scene = scene;

    // Create chassis
    this.chassis = BABYLON.MeshBuilder.CreateBox(
      'chassis',
      { width: 2, height: 0.5, depth: 4 },
      scene
    );
    this.chassis.position = position;

    const chassisAggregate = new BABYLON.PhysicsAggregate(
      this.chassis,
      BABYLON.PhysicsShapeType.BOX,
      { mass: 1000, friction: 0.5 },
      scene
    );

    this.body = chassisAggregate.body;

    // Create wheels
    this.wheels = [];
    const wheelPositions = [
      new BABYLON.Vector3(-0.8, -0.5, 1.5),   // Front left
      new BABYLON.Vector3(0.8, -0.5, 1.5),    // Front right
      new BABYLON.Vector3(-0.8, -0.5, -1.5),  // Rear left
      new BABYLON.Vector3(0.8, -0.5, -1.5)    // Rear right
    ];

    wheelPositions.forEach((pos, index) => {
      const wheel = BABYLON.MeshBuilder.CreateCylinder(
        `wheel${index}`,
        { diameter: 0.8, height: 0.3, tessellation: 16 },
        scene
      );
      wheel.rotation.z = Math.PI / 2;
      wheel.parent = this.chassis;
      wheel.position = pos;

      this.wheels.push(wheel);
    });

    // Controls
    this.throttle = 0;
    this.steering = 0;
    this.maxSpeed = 50;
    this.acceleration = 10;
    this.turnSpeed = 2;

    this.setupControls();
  }

  setupControls() {
    const keys = {};

    window.addEventListener('keydown', (e) => {
      keys[e.code] = true;
    });

    window.addEventListener('keyup', (e) => {
      keys[e.code] = false;
    });

    this.scene.onBeforeRenderObservable.add(() => {
      // Throttle
      if (keys['KeyW']) {
        this.throttle = Math.min(this.throttle + 0.1, 1);
      } else if (keys['KeyS']) {
        this.throttle = Math.max(this.throttle - 0.1, -0.5);
      } else {
        this.throttle *= 0.95; // Decay
      }

      // Steering
      if (keys['KeyA']) {
        this.steering = Math.max(this.steering - 0.1, -1);
      } else if (keys['KeyD']) {
        this.steering = Math.min(this.steering + 0.1, 1);
      } else {
        this.steering *= 0.9; // Center
      }

      // Apply forces
      const forward = this.chassis.forward;
      const force = forward.scale(this.throttle * this.acceleration * 1000);

      this.body.applyForce(
        force,
        this.chassis.position
      );

      // Apply turning torque
      const torque = new BABYLON.Vector3(0, this.steering * this.turnSpeed * 100, 0);
      this.body.setAngularVelocity(torque);

      // Rotate wheels
      this.wheels.forEach((wheel, index) => {
        wheel.rotation.x += this.throttle * 0.2;

        // Steer front wheels
        if (index < 2) {
          wheel.rotation.y = this.steering * 0.5;
        }
      });
    });
  }
}

// Usage
const vehicle = new Vehicle(scene, new BABYLON.Vector3(0, 5, 0));
```

---

## Particle Systems

### Fire Effect

```javascript
function createFireEffect(scene, position) {
  const fire = new BABYLON.ParticleSystem('fire', 2000, scene);

  fire.particleTexture = new BABYLON.Texture(
    'https://assets.babylonjs.com/textures/flare.png',
    scene
  );

  fire.emitter = position;
  fire.minEmitBox = new BABYLON.Vector3(-0.5, 0, -0.5);
  fire.maxEmitBox = new BABYLON.Vector3(0.5, 0, 0.5);

  // Colors
  fire.color1 = new BABYLON.Color4(1, 0.5, 0, 1.0);
  fire.color2 = new BABYLON.Color4(1, 0.2, 0, 1.0);
  fire.colorDead = new BABYLON.Color4(0, 0, 0, 0.0);

  // Size
  fire.minSize = 0.3;
  fire.maxSize = 1.0;

  // Life time
  fire.minLifeTime = 0.2;
  fire.maxLifeTime = 0.4;

  // Emission
  fire.emitRate = 600;

  // Blend mode
  fire.blendMode = BABYLON.ParticleSystem.BLENDMODE_ONEONE;

  // Direction
  fire.direction1 = new BABYLON.Vector3(-0.5, 4, -0.5);
  fire.direction2 = new BABYLON.Vector3(0.5, 8, 0.5);

  // Angular speed
  fire.minAngularSpeed = 0;
  fire.maxAngularSpeed = Math.PI;

  // Speed
  fire.minEmitPower = 1;
  fire.maxEmitPower = 3;
  fire.updateSpeed = 0.01;

  // Gravity
  fire.gravity = new BABYLON.Vector3(0, 0, 0);

  fire.start();

  return fire;
}
```

### Smoke Effect

```javascript
function createSmokeEffect(scene, position) {
  const smoke = new BABYLON.ParticleSystem('smoke', 1000, scene);

  smoke.particleTexture = new BABYLON.Texture(
    'https://assets.babylonjs.com/textures/cloud.png',
    scene
  );

  smoke.emitter = position;
  smoke.minEmitBox = new BABYLON.Vector3(-0.3, 0, -0.3);
  smoke.maxEmitBox = new BABYLON.Vector3(0.3, 0, 0.3);

  // Colors - gray smoke
  smoke.color1 = new BABYLON.Color4(0.3, 0.3, 0.3, 1.0);
  smoke.color2 = new BABYLON.Color4(0.6, 0.6, 0.6, 1.0);
  smoke.colorDead = new BABYLON.Color4(0, 0, 0, 0.0);

  // Size - grows over time
  smoke.minSize = 0.5;
  smoke.maxSize = 1.5;
  smoke.minScaleX = 0.5;
  smoke.maxScaleX = 2.0;
  smoke.minScaleY = 0.5;
  smoke.maxScaleY = 2.0;

  // Life time
  smoke.minLifeTime = 2.0;
  smoke.maxLifeTime = 4.0;

  // Emission
  smoke.emitRate = 200;

  // Blend mode - additive for glow
  smoke.blendMode = BABYLON.ParticleSystem.BLENDMODE_STANDARD;

  // Direction - upwards
  smoke.direction1 = new BABYLON.Vector3(-1, 3, -1);
  smoke.direction2 = new BABYLON.Vector3(1, 5, 1);

  // Speed
  smoke.minEmitPower = 0.5;
  smoke.maxEmitPower = 1.5;

  // Gravity - slight upward float
  smoke.gravity = new BABYLON.Vector3(0, -0.5, 0);

  smoke.start();

  return smoke;
}
```

### GPU Particle System (Performance)

```javascript
function createGPUParticles(scene, position) {
  const gpu = new BABYLON.GPUParticleSystem('gpu', { capacity: 50000 }, scene);

  gpu.particleTexture = new BABYLON.Texture(
    'https://assets.babylonjs.com/textures/flare.png',
    scene
  );

  gpu.emitter = position;
  gpu.minEmitBox = new BABYLON.Vector3(-2, 0, -2);
  gpu.maxEmitBox = new BABYLON.Vector3(2, 0, 2);

  // Colors - rainbow
  gpu.addColorGradient(0, new BABYLON.Color4(1, 0, 0, 1));
  gpu.addColorGradient(0.3, new BABYLON.Color4(1, 1, 0, 1));
  gpu.addColorGradient(0.6, new BABYLON.Color4(0, 1, 0, 1));
  gpu.addColorGradient(1.0, new BABYLON.Color4(0, 0, 1, 0));

  // Size over lifetime
  gpu.addSizeGradient(0, 0.5);
  gpu.addSizeGradient(0.5, 1.0);
  gpu.addSizeGradient(1.0, 0.1);

  // Life time
  gpu.minLifeTime = 1.0;
  gpu.maxLifeTime = 2.0;

  // Emission
  gpu.emitRate = 10000;

  // Direction
  gpu.direction1 = new BABYLON.Vector3(-1, 1, -1);
  gpu.direction2 = new BABYLON.Vector3(1, 3, 1);

  // Speed
  gpu.minEmitPower = 2;
  gpu.maxEmitPower = 4;

  // Gravity
  gpu.gravity = new BABYLON.Vector3(0, -9.8, 0);

  gpu.start();

  return gpu;
}
```

---

## Post-Processing Effects

### Bloom + DOF + Color Grading

```javascript
function createCinematicPipeline(scene, camera) {
  const pipeline = new BABYLON.DefaultRenderingPipeline(
    'cinematic',
    true, // HDR
    scene,
    [camera]
  );

  // Enable features
  pipeline.samples = 4; // MSAA

  // FXAA anti-aliasing
  pipeline.fxaaEnabled = true;

  // Bloom
  pipeline.bloomEnabled = true;
  pipeline.bloomThreshold = 0.8;
  pipeline.bloomWeight = 0.5;
  pipeline.bloomKernel = 64;
  pipeline.bloomScale = 0.5;

  // Depth of field
  pipeline.depthOfFieldEnabled = true;
  pipeline.depthOfFieldBlurLevel = BABYLON.DepthOfFieldEffectBlurLevel.Medium;
  pipeline.depthOfField.focusDistance = 5000;
  pipeline.depthOfField.focalLength = 100;
  pipeline.depthOfField.fStop = 2.0;

  // Image processing
  pipeline.imageProcessingEnabled = true;

  // Tone mapping
  pipeline.imageProcessing.toneMappingEnabled = true;
  pipeline.imageProcessing.toneMappingType = BABYLON.ImageProcessingConfiguration.TONEMAPPING_ACES;

  // Color grading
  pipeline.imageProcessing.contrast = 1.2;
  pipeline.imageProcessing.exposure = 1.0;

  // Vignette
  pipeline.imageProcessing.vignetteEnabled = true;
  pipeline.imageProcessing.vignetteWeight = 2.0;
  pipeline.imageProcessing.vignetteStretch = 0.5;
  pipeline.imageProcessing.vignetteCameraFov = 0.8;
  pipeline.imageProcessing.vignetteColor = new BABYLON.Color4(0, 0, 0, 0);

  // Chromatic aberration
  pipeline.chromaticAberrationEnabled = true;
  pipeline.chromaticAberration.aberrationAmount = 30;

  // Grain
  pipeline.grainEnabled = true;
  pipeline.grain.intensity = 10;
  pipeline.grain.animated = true;

  return pipeline;
}
```

### Outline/Glow Effect

```javascript
function createOutlineEffect(scene, meshes) {
  const highlightLayer = new BABYLON.HighlightLayer('highlight', scene);

  meshes.forEach(mesh => {
    highlightLayer.addMesh(mesh, BABYLON.Color3.Green());
  });

  // Glow layer for emissive
  const glowLayer = new BABYLON.GlowLayer('glow', scene);
  glowLayer.intensity = 0.5;

  return { highlightLayer, glowLayer };
}
```

### Custom Post-Process

```javascript
function createCustomPostProcess(camera) {
  const postProcess = new BABYLON.PostProcess(
    'customPP',
    './shaders/custom', // Path to shader files
    ['time'], // Uniforms
    ['textureSampler'], // Samplers
    1.0, // Sampling ratio
    camera
  );

  postProcess.onApply = (effect) => {
    effect.setFloat('time', performance.now() / 1000);
  };

  return postProcess;
}

// Custom shader (shaders/custom.fragment.fx)
// precision highp float;
// uniform sampler2D textureSampler;
// uniform float time;
// varying vec2 vUV;
//
// void main(void) {
//   vec2 uv = vUV;
//   uv.x += sin(uv.y * 10.0 + time) * 0.01;
//   gl_FragColor = texture2D(textureSampler, uv);
// }
```

---

## GUI & User Interface

### 3D Menu System

```javascript
import { AdvancedDynamicTexture } from '@babylonjs/gui/2D/advancedDynamicTexture.js';
import { StackPanel } from '@babylonjs/gui/2D/controls/stackPanel.js';
import { Button } from '@babylonjs/gui/2D/controls/button.js';
import { TextBlock } from '@babylonjs/gui/2D/controls/textBlock.js';

function create3DMenu(scene) {
  // Create plane for menu
  const plane = BABYLON.MeshBuilder.CreatePlane('menuPlane', { size: 4 }, scene);
  plane.position = new BABYLON.Vector3(0, 2, 0);

  // Create texture for plane
  const advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateForMesh(
    plane,
    1024,
    1024
  );

  // Create panel
  const panel = new BABYLON.GUI.StackPanel();
  panel.width = '600px';
  panel.horizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_CENTER;
  panel.verticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_CENTER;
  advancedTexture.addControl(panel);

  // Title
  const title = new BABYLON.GUI.TextBlock();
  title.text = 'Main Menu';
  title.height = '80px';
  title.color = 'white';
  title.fontSize = 48;
  title.fontWeight = 'bold';
  panel.addControl(title);

  // Buttons
  const buttonData = [
    { text: 'Start Game', action: () => console.log('Start') },
    { text: 'Options', action: () => console.log('Options') },
    { text: 'Exit', action: () => console.log('Exit') }
  ];

  buttonData.forEach(data => {
    const button = BABYLON.GUI.Button.CreateSimpleButton('button', data.text);
    button.width = '400px';
    button.height = '60px';
    button.color = 'white';
    button.background = '#4fc3f7';
    button.cornerRadius = 8;
    button.thickness = 0;
    button.fontSize = 24;
    button.paddingTop = '10px';
    button.paddingBottom = '10px';

    button.onPointerEnterObservable.add(() => {
      button.background = '#29b6f6';
    });

    button.onPointerOutObservable.add(() => {
      button.background = '#4fc3f7';
    });

    button.onPointerUpObservable.add(data.action);

    panel.addControl(button);
  });

  return { plane, advancedTexture };
}
```

### HUD with Stats

```javascript
function createHUD(scene, engine) {
  const advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI('HUD');

  // FPS counter
  const fpsText = new BABYLON.GUI.TextBlock();
  fpsText.text = 'FPS: 60';
  fpsText.color = 'white';
  fpsText.fontSize = 18;
  fpsText.textHorizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_RIGHT;
  fpsText.textVerticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
  fpsText.paddingTop = '10px';
  fpsText.paddingRight = '10px';
  advancedTexture.addControl(fpsText);

  // Health bar
  const healthContainer = new BABYLON.GUI.Rectangle();
  healthContainer.width = '200px';
  healthContainer.height = '30px';
  healthContainer.cornerRadius = 4;
  healthContainer.color = 'white';
  healthContainer.thickness = 2;
  healthContainer.background = 'rgba(0, 0, 0, 0.5)';
  healthContainer.horizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
  healthContainer.verticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_TOP;
  healthContainer.left = 10;
  healthContainer.top = 10;
  advancedTexture.addControl(healthContainer);

  const healthBar = new BABYLON.GUI.Rectangle();
  healthBar.width = '100%';
  healthBar.height = '100%';
  healthBar.background = '#4caf50';
  healthBar.horizontalAlignment = BABYLON.GUI.Control.HORIZONTAL_ALIGNMENT_LEFT;
  healthContainer.addControl(healthBar);

  // Update FPS
  scene.onBeforeRenderObservable.add(() => {
    fpsText.text = `FPS: ${engine.getFps().toFixed(0)}`;
  });

  return { advancedTexture, healthBar };
}
```

---

## WebXR & VR

### VR Scene Setup

```javascript
async function createVRScene(scene) {
  // Create environment
  const env = scene.createDefaultEnvironment({
    createGround: true,
    createSkybox: true
  });

  // Enable WebXR
  const xrHelper = await scene.createDefaultXRExperienceAsync({
    floorMeshes: [env.ground],
    disableTeleportation: false
  });

  // Controller input
  xrHelper.input.onControllerAddedObservable.add((controller) => {
    controller.onMotionControllerInitObservable.add((motionController) => {
      // Get components
      const trigger = motionController.getMainComponent();
      const squeeze = motionController.getComponent('squeeze');
      const thumbstick = motionController.getComponent('thumbstick');

      // Trigger press
      trigger.onButtonStateChangedObservable.add((component) => {
        if (component.pressed) {
          console.log('Trigger pressed');
          // Perform raycast
          const ray = controller.getWorldPointerRayToRef(new BABYLON.Ray());
          const hit = scene.pickWithRay(ray);

          if (hit.pickedMesh) {
            console.log('Hit:', hit.pickedMesh.name);
          }
        }
      });

      // Squeeze (grip) press
      if (squeeze) {
        squeeze.onButtonStateChangedObservable.add((component) => {
          if (component.pressed) {
            console.log('Grip pressed');
          }
        });
      }

      // Thumbstick
      if (thumbstick) {
        thumbstick.onAxisValueChangedObservable.add((axes) => {
          console.log('Thumbstick:', axes.x, axes.y);
        });
      }
    });
  });

  return xrHelper;
}
```

### VR Teleportation

```javascript
function setupVRTeleportation(xrHelper, validTargets) {
  xrHelper.teleportation.addFloorMesh(validTargets[0]);

  // Custom teleportation behavior
  xrHelper.teleportation.onTargetMeshSelectedObservable.add((mesh) => {
    console.log('Teleporting to:', mesh.name);
  });

  // Change teleportation arc color
  xrHelper.teleportation.defaultTargetMeshOptions.teleportationFillColor = '#4fc3f7';
  xrHelper.teleportation.defaultTargetMeshOptions.teleportationBorderColor = '#29b6f6';
}
```

---

## Performance Optimization

### Octree Scene Optimization

```javascript
function optimizeWithOctree(scene) {
  const octree = scene.createOrUpdateSelectionOctree(32, 2);

  // Enable octree for all meshes
  scene.meshes.forEach(mesh => {
    mesh.alwaysSelectAsActiveMesh = false;
  });

  return octree;
}
```

### Mesh Instancing

```javascript
function createInstancedMeshes(scene, template, count) {
  const instances = [];

  for (let i = 0; i < count; i++) {
    const instance = template.createInstance(`instance${i}`);
    instance.position = new BABYLON.Vector3(
      Math.random() * 50 - 25,
      0,
      Math.random() * 50 - 25
    );
    instance.rotation.y = Math.random() * Math.PI * 2;

    instances.push(instance);
  }

  return instances;
}
```

### Thin Instances (Best Performance)

```javascript
function createThinInstances(mesh, count) {
  const matrices = [];

  for (let i = 0; i < count; i++) {
    const matrix = BABYLON.Matrix.Translation(
      Math.random() * 50 - 25,
      0,
      Math.random() * 50 - 25
    );

    matrices.push(matrix);
  }

  const buffer = new Float32Array(matrices.length * 16);

  matrices.forEach((matrix, index) => {
    matrix.copyToArray(buffer, index * 16);
  });

  mesh.thinInstanceSetBuffer('matrix', buffer, 16);
}
```

This comprehensive examples documentation provides production-ready patterns for advanced Babylon.js development. Each example is complete and can be integrated into real projects.



===== FILE: plugins/individual/babylonjs-engine/skills/babylonjs-engine/assets/starter_babylon/README.md =====

# Babylon.js Starter Template

Production-ready Babylon.js starter with Vite, physics, PBR materials, and interactive features.

## Features

- ⚡️ **Vite** - Fast build tool and dev server
- 🎮 **Babylon.js 7.x** - Latest version with WebGPU support
- 🎯 **Physics Engine** - Havok physics integration
- 🎨 **PBR Materials** - Physically based rendering
- 💡 **Dynamic Lighting** - Hemispheric + Directional with shadows
- 🖱️ **Interactive** - Mesh picking and keyboard controls
- 📊 **FPS Counter** - Performance monitoring
- 🐛 **Inspector** - Built-in debug tools (Shift+Ctrl+Alt+I)

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
starter_babylon/
├── index.html              # Entry HTML
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
└── src/
    ├── main.js             # Main application
    └── style.css           # Styles
```

## What's Included

### Scene Setup

- **Camera**: ArcRotateCamera with orbit controls
- **Lights**: Hemispheric ambient + Directional with shadows
- **Ground**: 20x20 plane with physics
- **Meshes**: PBR sphere, standard material box, metallic sphere

### Physics

- **Havok Physics Engine** integrated
- **Realistic gravity** (9.8 m/s²)
- **Collision detection** and response
- **Adjustable restitution** (bounciness)

### Materials

**PBR Material (Sphere 1)**
```javascript
const pbrMaterial = new PBRMaterial('pbrMat', scene);
pbrMaterial.metallic = 1.0;
pbrMaterial.roughness = 0.3;
pbrMaterial.baseColor = new Color3(0.9, 0.1, 0.1);
```

**Standard Material (Box)**
```javascript
const standardMaterial = new StandardMaterial('standardMat', scene);
standardMaterial.diffuseColor = new Color3(0.2, 0.8, 0.3);
standardMaterial.specularPower = 32;
```

### Interactions

- **Mouse Click**: Select and highlight meshes
- **Spacebar**: Add random spheres with physics
- **Camera Controls**: Drag to rotate, scroll to zoom
- **Inspector**: Shift+Ctrl+Alt+I to toggle debug layer

## Customization

### Change Camera

Replace ArcRotateCamera with FreeCamera for FPS-style:

```javascript
import { FreeCamera } from '@babylonjs/core/Cameras/freeCamera.js';

const camera = new FreeCamera('camera', new Vector3(0, 5, -10), scene);
camera.setTarget(Vector3.Zero());
camera.attachControl(canvas, true);
```

### Add More Lights

```javascript
import { PointLight } from '@babylonjs/core/Lights/pointLight.js';

const pointLight = new PointLight('pointLight', new Vector3(0, 10, 0), scene);
pointLight.intensity = 0.5;
pointLight.diffuse = new Color3(1, 0.5, 0);
```

### Load GLTF Models

```javascript
import { SceneLoader } from '@babylonjs/core/Loading/sceneLoader.js';
import '@babylonjs/loaders/glTF';

const result = await SceneLoader.ImportMeshAsync(
  null,
  'https://assets.babylonjs.com/meshes/',
  'village.glb',
  scene
);

console.log('Loaded:', result.meshes);
```

### Add Post-Processing

```javascript
import { DefaultRenderingPipeline } from '@babylonjs/core/PostProcesses/RenderPipeline/Pipelines/defaultRenderingPipeline.js';

const pipeline = new DefaultRenderingPipeline('pipeline', true, scene, [camera]);
pipeline.fxaaEnabled = true;
pipeline.samples = 4;

pipeline.bloomEnabled = true;
pipeline.bloomThreshold = 0.8;
pipeline.bloomWeight = 0.5;
```

### Create Custom Meshes

```javascript
import { CreateTorus } from '@babylonjs/core/Meshes/Builders/torusBuilder.js';

const torus = CreateTorus('torus', {
  diameter: 3,
  thickness: 1,
  tessellation: 16
}, scene);

torus.position.y = 2;
```

### Add GUI

```javascript
import { AdvancedDynamicTexture } from '@babylonjs/gui/2D/advancedDynamicTexture.js';
import { Button } from '@babylonjs/gui/2D/controls/button.js';

const advancedTexture = AdvancedDynamicTexture.CreateFullscreenUI('UI');

const button = Button.CreateSimpleButton('button', 'Reset Scene');
button.width = '150px';
button.height = '40px';
button.color = 'white';
button.background = '#4fc3f7';
button.cornerRadius = 8;
button.onPointerUpObservable.add(() => {
  console.log('Reset clicked');
});

advancedTexture.addControl(button);
```

## Performance Tips

1. **Use PBR Materials** - More realistic and efficient than standard materials
2. **Optimize Shadow Maps** - Reduce shadowGenerator size if needed
3. **Freeze World Matrices** - For static meshes: `mesh.freezeWorldMatrix()`
4. **Use Instances** - For repeated meshes: `mesh.createInstance('instance1')`
5. **Optimize Physics** - Set appropriate mass and restitution values
6. **Hardware Scaling** - Reduce resolution if FPS drops: `engine.setHardwareScalingLevel(2)`

## Debugging

### Inspector

Press **Shift+Ctrl+Alt+I** to toggle the Babylon.js Inspector:
- View scene graph
- Inspect mesh properties
- Debug materials
- Analyze performance
- Tweak values in real-time

### Console Logs

The template includes helpful console logs:
- Selected mesh names
- FPS display in top-right corner

### Common Issues

**Physics not working?**
- Ensure Havok is properly initialized with `await HavokPhysics()`
- Check that physics aggregates are created after `scene.enablePhysics()`

**Meshes not visible?**
- Check camera position and target
- Verify mesh positions
- Ensure materials are applied

**Performance issues?**
- Reduce shadow map size
- Disable post-processing
- Use hardware scaling
- Optimize mesh count

## Next Steps

### Add Animations

```javascript
import { Animation } from '@babylonjs/core/Animations/animation.js';

const animation = Animation.CreateAndStartAnimation(
  'rotate',
  mesh,
  'rotation.y',
  30,
  120,
  0,
  Math.PI * 2,
  Animation.ANIMATIONLOOPMODE_CYCLE
);
```

### Enable WebXR (VR/AR)

```javascript
const env = scene.createDefaultEnvironment();
const xr = await scene.createDefaultXRExperienceAsync({
  floorMeshes: [env.ground]
});
```

### Add Particles

```javascript
import { ParticleSystem } from '@babylonjs/core/Particles/particleSystem.js';
import { Texture } from '@babylonjs/core/Materials/Textures/texture.js';

const particleSystem = new ParticleSystem('particles', 2000, scene);
particleSystem.particleTexture = new Texture('particle.png', scene);
particleSystem.emitter = new Vector3(0, 5, 0);
particleSystem.start();
```

## Resources

- [Babylon.js Documentation](https://doc.babylonjs.com/)
- [Babylon.js Playground](https://playground.babylonjs.com/)
- [Babylon.js Forum](https://forum.babylonjs.com/)
- [Babylon.js Examples](https://doc.babylonjs.com/examples/)

## License

MIT - Free for personal and commercial use



===== FILE: plugins/individual/babylonjs-engine/skills/babylonjs-engine/assets/starter_babylon/index.html =====

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Babylon.js Starter</title>
  <link rel="stylesheet" href="/src/style.css" />
</head>
<body>
  <canvas id="renderCanvas"></canvas>
  <div id="info">
    <h1>Babylon.js Starter</h1>
    <p>Interactive 3D scene with physics</p>
    <ul>
      <li><strong>Camera:</strong> Drag to rotate, scroll to zoom</li>
      <li><strong>Click:</strong> Select meshes</li>
      <li><strong>Space:</strong> Add sphere</li>
    </ul>
  </div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>

```


===== FILE: plugins/individual/babylonjs-engine/skills/babylonjs-engine/assets/starter_babylon/package.json =====

```json
{
  "name": "babylon-starter",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "description": "Babylon.js starter template with Vite",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@babylonjs/core": "^7.31.1",
    "@babylonjs/loaders": "^7.31.1",
    "@babylonjs/havok": "^1.3.8"
  },
  "devDependencies": {
    "vite": "^5.0.11"
  }
}

```


===== FILE: plugins/individual/babylonjs-engine/skills/babylonjs-engine/assets/starter_babylon/src/main.js =====

```js
import { Engine } from '@babylonjs/core/Engines/engine.js';
import { Scene } from '@babylonjs/core/scene.js';
import { ArcRotateCamera } from '@babylonjs/core/Cameras/arcRotateCamera.js';
import { Vector3, Color3, Color4 } from '@babylonjs/core/Maths/math.js';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight.js';
import { DirectionalLight } from '@babylonjs/core/Lights/directionalLight.js';
import { ShadowGenerator } from '@babylonjs/core/Lights/Shadows/shadowGenerator.js';
import { CreateGround } from '@babylonjs/core/Meshes/Builders/groundBuilder.js';
import { CreateSphere } from '@babylonjs/core/Meshes/Builders/sphereBuilder.js';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder.js';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial.js';
import { PBRMaterial } from '@babylonjs/core/Materials/PBR/pbrMaterial.js';
import HavokPhysics from '@babylonjs/havok';
import { HavokPlugin } from '@babylonjs/core/Physics/v2/Plugins/havokPlugin.js';
import { PhysicsAggregate } from '@babylonjs/core/Physics/v2/physicsAggregate.js';
import { PhysicsShapeType } from '@babylonjs/core/Physics/v2/IPhysicsEnginePlugin.js';

// Import side effects for picking
import '@babylonjs/core/Culling/ray.js';
import '@babylonjs/core/Collisions/collisionCoordinator.js';

const canvas = document.getElementById('renderCanvas');
const engine = new Engine(canvas, true, {
  preserveDrawingBuffer: true,
  stencil: true
});

const createScene = async function() {
  const scene = new Scene(engine);
  scene.clearColor = new Color4(0.1, 0.1, 0.15, 1.0);

  // Camera
  const camera = new ArcRotateCamera(
    'camera',
    -Math.PI / 2,
    Math.PI / 3,
    15,
    Vector3.Zero(),
    scene
  );
  camera.attachControl(canvas, true);
  camera.lowerRadiusLimit = 5;
  camera.upperRadiusLimit = 50;
  camera.wheelPrecision = 50;

  // Lights
  const hemiLight = new HemisphericLight('hemiLight', new Vector3(0, 1, 0), scene);
  hemiLight.intensity = 0.5;

  const dirLight = new DirectionalLight('dirLight', new Vector3(-1, -2, -1), scene);
  dirLight.position = new Vector3(20, 40, 20);
  dirLight.intensity = 0.7;

  // Shadows
  const shadowGenerator = new ShadowGenerator(1024, dirLight);
  shadowGenerator.useExponentialShadowMap = true;

  // Ground
  const ground = CreateGround('ground', { width: 20, height: 20 }, scene);
  const groundMaterial = new StandardMaterial('groundMat', scene);
  groundMaterial.diffuseColor = new Color3(0.3, 0.3, 0.35);
  groundMaterial.specularColor = new Color3(0.1, 0.1, 0.1);
  ground.material = groundMaterial;
  ground.receiveShadows = true;

  // Initialize physics
  const havokInstance = await HavokPhysics();
  const havokPlugin = new HavokPlugin(true, havokInstance);
  scene.enablePhysics(new Vector3(0, -9.8, 0), havokPlugin);

  // Ground physics
  const groundAggregate = new PhysicsAggregate(
    ground,
    PhysicsShapeType.BOX,
    { mass: 0 },
    scene
  );

  // Create PBR sphere
  const sphere1 = CreateSphere('sphere1', { diameter: 2 }, scene);
  sphere1.position = new Vector3(-3, 3, 0);

  const pbrMaterial = new PBRMaterial('pbrMat', scene);
  pbrMaterial.metallic = 1.0;
  pbrMaterial.roughness = 0.3;
  pbrMaterial.baseColor = new Color3(0.9, 0.1, 0.1);
  sphere1.material = pbrMaterial;

  shadowGenerator.addShadowCaster(sphere1);

  const sphere1Aggregate = new PhysicsAggregate(
    sphere1,
    PhysicsShapeType.SPHERE,
    { mass: 1, restitution: 0.8 },
    scene
  );

  // Create standard material box
  const box1 = CreateBox('box1', { size: 1.5 }, scene);
  box1.position = new Vector3(3, 3, 0);

  const standardMaterial = new StandardMaterial('standardMat', scene);
  standardMaterial.diffuseColor = new Color3(0.2, 0.8, 0.3);
  standardMaterial.specularColor = new Color3(0.5, 0.5, 0.5);
  standardMaterial.specularPower = 32;
  box1.material = standardMaterial;

  shadowGenerator.addShadowCaster(box1);

  const box1Aggregate = new PhysicsAggregate(
    box1,
    PhysicsShapeType.BOX,
    { mass: 1, restitution: 0.5 },
    scene
  );

  // Create metallic sphere
  const sphere2 = CreateSphere('sphere2', { diameter: 1.8 }, scene);
  sphere2.position = new Vector3(0, 5, 2);

  const metallicMaterial = new PBRMaterial('metallicMat', scene);
  metallicMaterial.metallic = 0.9;
  metallicMaterial.roughness = 0.1;
  metallicMaterial.baseColor = new Color3(0.8, 0.8, 0.9);
  sphere2.material = metallicMaterial;

  shadowGenerator.addShadowCaster(sphere2);

  const sphere2Aggregate = new PhysicsAggregate(
    sphere2,
    PhysicsShapeType.SPHERE,
    { mass: 1, restitution: 0.9 },
    scene
  );

  // Picking
  let selectedMesh = null;

  scene.onPointerDown = function(evt, pickResult) {
    if (pickResult.hit && pickResult.pickedMesh !== ground) {
      // Deselect previous
      if (selectedMesh && selectedMesh.material) {
        selectedMesh.material.emissiveColor = new Color3(0, 0, 0);
      }

      // Select new
      selectedMesh = pickResult.pickedMesh;
      if (selectedMesh.material) {
        selectedMesh.material.emissiveColor = new Color3(0.2, 0.2, 0);
      }

      console.log('Selected:', selectedMesh.name);
    }
  };

  // Add sphere on spacebar
  let sphereCount = 3;
  window.addEventListener('keydown', (evt) => {
    if (evt.code === 'Space') {
      const newSphere = CreateSphere('sphere' + sphereCount, { diameter: 1.5 }, scene);
      newSphere.position = new Vector3(
        Math.random() * 6 - 3,
        8,
        Math.random() * 6 - 3
      );

      const randomMaterial = new PBRMaterial('mat' + sphereCount, scene);
      randomMaterial.metallic = Math.random();
      randomMaterial.roughness = Math.random() * 0.5 + 0.2;
      randomMaterial.baseColor = new Color3(
        Math.random(),
        Math.random(),
        Math.random()
      );
      newSphere.material = randomMaterial;

      shadowGenerator.addShadowCaster(newSphere);

      new PhysicsAggregate(
        newSphere,
        PhysicsShapeType.SPHERE,
        { mass: 1, restitution: 0.7 },
        scene
      );

      sphereCount++;
    }
  });

  // FPS counter
  let fpsDisplay = document.createElement('div');
  fpsDisplay.style.position = 'absolute';
  fpsDisplay.style.top = '10px';
  fpsDisplay.style.right = '10px';
  fpsDisplay.style.color = 'white';
  fpsDisplay.style.fontFamily = 'monospace';
  fpsDisplay.style.fontSize = '14px';
  fpsDisplay.style.background = 'rgba(0, 0, 0, 0.5)';
  fpsDisplay.style.padding = '8px 12px';
  fpsDisplay.style.borderRadius = '4px';
  document.body.appendChild(fpsDisplay);

  scene.onBeforeRenderObservable.add(() => {
    fpsDisplay.textContent = `FPS: ${engine.getFps().toFixed(0)}`;
  });

  return scene;
};

// Create scene and start render loop
createScene().then(scene => {
  engine.runRenderLoop(() => {
    scene.render();
  });
});

// Handle resize
window.addEventListener('resize', () => {
  engine.resize();
});

// Optional: Debug layer (Shift+Ctrl+Alt+I)
window.addEventListener('keydown', (ev) => {
  if (ev.shiftKey && ev.ctrlKey && ev.altKey && (ev.key === 'I' || ev.key === 'i')) {
    import('@babylonjs/core/Debug/debugLayer.js').then(() => {
      import('@babylonjs/inspector').then(() => {
        if (engine.scenes[0].debugLayer.isVisible()) {
          engine.scenes[0].debugLayer.hide();
        } else {
          engine.scenes[0].debugLayer.show();
        }
      });
    });
  }
});

```


===== FILE: plugins/individual/babylonjs-engine/skills/babylonjs-engine/assets/starter_babylon/src/style.css =====

```css
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
}

#renderCanvas {
  width: 100%;
  height: 100%;
  touch-action: none;
  display: block;
}

#info {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  color: white;
  padding: 20px 24px;
  border-radius: 12px;
  max-width: 300px;
  font-size: 14px;
  line-height: 1.6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

#info h1 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #fff;
}

#info p {
  margin-bottom: 12px;
  color: #ccc;
  font-size: 13px;
}

#info ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

#info li {
  margin: 6px 0;
  color: #ddd;
  font-size: 12px;
}

#info strong {
  color: #4fc3f7;
  font-weight: 600;
}

@media (max-width: 768px) {
  #info {
    bottom: 10px;
    left: 10px;
    right: 10px;
    max-width: none;
    padding: 16px 20px;
  }

  #info h1 {
    font-size: 16px;
  }

  #info p {
    font-size: 12px;
  }

  #info li {
    font-size: 11px;
  }
}

```


===== FILE: plugins/individual/babylonjs-engine/skills/babylonjs-engine/assets/starter_babylon/vite.config.js =====

```js
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 3000,
    open: true
  },
  build: {
    target: 'esnext',
    minify: 'terser'
  },
  optimizeDeps: {
    exclude: ['@babylonjs/havok']
  }
});

```


# Skill: playcanvas-engine


===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/SKILL.md =====

---
name: playcanvas-engine
description: Lightweight WebGL/WebGPU game engine with entity-component architecture and visual editor integration. Use this skill when building browser-based games, interactive 3D applications, or performance-critical web experiences. Triggers on tasks involving PlayCanvas, entity-component systems, game engine development, WebGL games, 3D browser applications, editor-first workflows, or real-time 3D rendering. Alternative to Three.js with game-specific features and integrated development environment.
---

# PlayCanvas Engine Skill

Lightweight WebGL/WebGPU game engine with entity-component architecture, visual editor integration, and performance-focused design.

## When to Use This Skill

Trigger this skill when you see:
- "PlayCanvas engine"
- "WebGL game engine"
- "entity component system"
- "PlayCanvas application"
- "3D browser games"
- "online 3D editor"
- "lightweight 3D engine"
- Need for editor-first workflow

Compare with:
- **Three.js**: Lower-level, more flexible but requires more setup
- **Babylon.js**: Feature-rich but heavier, has editor but less mature
- **A-Frame**: VR-focused, declarative HTML approach
- Use PlayCanvas for: Game projects, editor-first workflow, performance-critical apps

---

## Core Concepts

### 1. Application

The root PlayCanvas application manages the rendering loop.

```javascript
import * as pc from 'playcanvas';

// Create canvas
const canvas = document.createElement('canvas');
document.body.appendChild(canvas);

// Create application
const app = new pc.Application(canvas, {
  keyboard: new pc.Keyboard(window),
  mouse: new pc.Mouse(canvas),
  touch: new pc.TouchDevice(canvas),
  gamepads: new pc.GamePads()
});

// Configure canvas
app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
app.setCanvasResolution(pc.RESOLUTION_AUTO);

// Handle resize
window.addEventListener('resize', () => app.resizeCanvas());

// Start the application
app.start();
```

---

### 2. Entity-Component System

PlayCanvas uses ECS architecture: Entities contain Components.

```javascript
// Create entity
const entity = new pc.Entity('myEntity');

// Add to scene hierarchy
app.root.addChild(entity);

// Add components
entity.addComponent('model', {
  type: 'box'
});

entity.addComponent('script');

// Transform
entity.setPosition(0, 1, 0);
entity.setEulerAngles(0, 45, 0);
entity.setLocalScale(2, 2, 2);

// Parent-child hierarchy
const parent = new pc.Entity('parent');
const child = new pc.Entity('child');
parent.addChild(child);
```

---

### 3. Update Loop

The application fires events during the update loop.

```javascript
app.on('update', (dt) => {
  // dt is delta time in seconds
  entity.rotate(0, 10 * dt, 0);
});

app.on('prerender', () => {
  // Before rendering
});

app.on('postrender', () => {
  // After rendering
});
```

---

### 4. Components

Core components extend entity functionality:

**Model Component**:
```javascript
entity.addComponent('model', {
  type: 'box',           // 'box', 'sphere', 'cylinder', 'cone', 'capsule', 'asset'
  material: material,
  castShadows: true,
  receiveShadows: true
});
```

**Camera Component**:
```javascript
entity.addComponent('camera', {
  clearColor: new pc.Color(0.1, 0.2, 0.3),
  fov: 45,
  nearClip: 0.1,
  farClip: 1000,
  projection: pc.PROJECTION_PERSPECTIVE  // or PROJECTION_ORTHOGRAPHIC
});
```

**Light Component**:
```javascript
entity.addComponent('light', {
  type: pc.LIGHTTYPE_DIRECTIONAL,  // DIRECTIONAL, POINT, SPOT
  color: new pc.Color(1, 1, 1),
  intensity: 1,
  castShadows: true,
  shadowDistance: 50
});
```

**Rigidbody Component** (requires physics):
```javascript
entity.addComponent('rigidbody', {
  type: pc.BODYTYPE_DYNAMIC,  // STATIC, DYNAMIC, KINEMATIC
  mass: 1,
  friction: 0.5,
  restitution: 0.3
});

entity.addComponent('collision', {
  type: 'box',
  halfExtents: new pc.Vec3(0.5, 0.5, 0.5)
});
```

---

## Common Patterns

### Pattern 1: Basic Scene Setup

Create a complete scene with camera, light, and models.

```javascript
import * as pc from 'playcanvas';

// Initialize application
const canvas = document.createElement('canvas');
document.body.appendChild(canvas);

const app = new pc.Application(canvas);
app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
app.setCanvasResolution(pc.RESOLUTION_AUTO);
window.addEventListener('resize', () => app.resizeCanvas());

// Create camera
const camera = new pc.Entity('camera');
camera.addComponent('camera', {
  clearColor: new pc.Color(0.2, 0.3, 0.4)
});
camera.setPosition(0, 2, 5);
camera.lookAt(0, 0, 0);
app.root.addChild(camera);

// Create directional light
const light = new pc.Entity('light');
light.addComponent('light', {
  type: pc.LIGHTTYPE_DIRECTIONAL,
  castShadows: true
});
light.setEulerAngles(45, 30, 0);
app.root.addChild(light);

// Create ground
const ground = new pc.Entity('ground');
ground.addComponent('model', {
  type: 'plane'
});
ground.setLocalScale(10, 1, 10);
app.root.addChild(ground);

// Create cube
const cube = new pc.Entity('cube');
cube.addComponent('model', {
  type: 'box',
  castShadows: true
});
cube.setPosition(0, 1, 0);
app.root.addChild(cube);

// Animate cube
app.on('update', (dt) => {
  cube.rotate(10 * dt, 20 * dt, 30 * dt);
});

app.start();
```

---

### Pattern 2: Loading GLTF Models

Load external 3D models with asset management.

```javascript
// Create asset for model
const modelAsset = new pc.Asset('model', 'container', {
  url: '/models/character.glb'
});

// Add to asset registry
app.assets.add(modelAsset);

// Load asset
modelAsset.ready((asset) => {
  // Create entity from loaded model
  const entity = asset.resource.instantiateRenderEntity();

  app.root.addChild(entity);

  // Scale and position
  entity.setLocalScale(2, 2, 2);
  entity.setPosition(0, 0, 0);
});

app.assets.load(modelAsset);
```

**With error handling**:
```javascript
modelAsset.ready((asset) => {
  console.log('Model loaded:', asset.name);
  const entity = asset.resource.instantiateRenderEntity();
  app.root.addChild(entity);
});

modelAsset.on('error', (err) => {
  console.error('Failed to load model:', err);
});

app.assets.load(modelAsset);
```

---

### Pattern 3: Materials and Textures

Create custom materials with PBR workflow.

```javascript
// Create material
const material = new pc.StandardMaterial();
material.diffuse = new pc.Color(1, 0, 0);  // Red
material.metalness = 0.5;
material.gloss = 0.8;
material.update();

// Apply to entity
entity.model.material = material;

// With textures
const textureAsset = new pc.Asset('diffuse', 'texture', {
  url: '/textures/brick_diffuse.jpg'
});

app.assets.add(textureAsset);
app.assets.load(textureAsset);

textureAsset.ready((asset) => {
  material.diffuseMap = asset.resource;
  material.update();
});

// PBR material with all maps
const pbrMaterial = new pc.StandardMaterial();

// Load all textures
const textures = {
  diffuse: '/textures/albedo.jpg',
  normal: '/textures/normal.jpg',
  metalness: '/textures/metalness.jpg',
  gloss: '/textures/roughness.jpg',
  ao: '/textures/ao.jpg'
};

Object.keys(textures).forEach(key => {
  const asset = new pc.Asset(key, 'texture', { url: textures[key] });
  app.assets.add(asset);

  asset.ready((loadedAsset) => {
    switch(key) {
      case 'diffuse':
        pbrMaterial.diffuseMap = loadedAsset.resource;
        break;
      case 'normal':
        pbrMaterial.normalMap = loadedAsset.resource;
        break;
      case 'metalness':
        pbrMaterial.metalnessMap = loadedAsset.resource;
        break;
      case 'gloss':
        pbrMaterial.glossMap = loadedAsset.resource;
        break;
      case 'ao':
        pbrMaterial.aoMap = loadedAsset.resource;
        break;
    }
    pbrMaterial.update();
  });

  app.assets.load(asset);
});
```

---

### Pattern 4: Physics Integration

Use Ammo.js for physics simulation.

```javascript
import * as pc from 'playcanvas';

// Initialize with Ammo.js
const app = new pc.Application(canvas, {
  keyboard: new pc.Keyboard(window),
  mouse: new pc.Mouse(canvas)
});

// Load Ammo.js
const ammoScript = document.createElement('script');
ammoScript.src = 'https://cdn.jsdelivr.net/npm/ammo.js@0.0.10/ammo.js';
document.body.appendChild(ammoScript);

ammoScript.onload = () => {
  Ammo().then((AmmoLib) => {
    window.Ammo = AmmoLib;

    // Create static ground
    const ground = new pc.Entity('ground');
    ground.addComponent('model', { type: 'plane' });
    ground.setLocalScale(10, 1, 10);

    ground.addComponent('rigidbody', {
      type: pc.BODYTYPE_STATIC
    });

    ground.addComponent('collision', {
      type: 'box',
      halfExtents: new pc.Vec3(5, 0.1, 5)
    });

    app.root.addChild(ground);

    // Create dynamic cube
    const cube = new pc.Entity('cube');
    cube.addComponent('model', { type: 'box' });
    cube.setPosition(0, 5, 0);

    cube.addComponent('rigidbody', {
      type: pc.BODYTYPE_DYNAMIC,
      mass: 1,
      friction: 0.5,
      restitution: 0.5
    });

    cube.addComponent('collision', {
      type: 'box',
      halfExtents: new pc.Vec3(0.5, 0.5, 0.5)
    });

    app.root.addChild(cube);

    // Apply force
    cube.rigidbody.applyForce(10, 0, 0);
    cube.rigidbody.applyTorque(0, 10, 0);

    app.start();
  });
};
```

---

### Pattern 5: Custom Scripts

Create reusable script components.

```javascript
// Define script class
const RotateScript = pc.createScript('rotate');

// Script attributes (editor-exposed)
RotateScript.attributes.add('speed', {
  type: 'number',
  default: 10,
  title: 'Rotation Speed'
});

RotateScript.attributes.add('axis', {
  type: 'vec3',
  default: [0, 1, 0],
  title: 'Rotation Axis'
});

// Initialize method
RotateScript.prototype.initialize = function() {
  console.log('RotateScript initialized');
};

// Update method (called every frame)
RotateScript.prototype.update = function(dt) {
  this.entity.rotate(
    this.axis.x * this.speed * dt,
    this.axis.y * this.speed * dt,
    this.axis.z * this.speed * dt
  );
};

// Cleanup
RotateScript.prototype.destroy = function() {
  console.log('RotateScript destroyed');
};

// Usage
const entity = new pc.Entity('rotatingCube');
entity.addComponent('model', { type: 'box' });
entity.addComponent('script');
entity.script.create('rotate', {
  attributes: {
    speed: 20,
    axis: new pc.Vec3(0, 1, 0)
  }
});
app.root.addChild(entity);
```

**Script lifecycle methods**:
```javascript
const MyScript = pc.createScript('myScript');

MyScript.prototype.initialize = function() {
  // Called once after all resources are loaded
};

MyScript.prototype.postInitialize = function() {
  // Called after all entities have initialized
};

MyScript.prototype.update = function(dt) {
  // Called every frame before rendering
};

MyScript.prototype.postUpdate = function(dt) {
  // Called every frame after update
};

MyScript.prototype.swap = function(old) {
  // Hot reload support
};

MyScript.prototype.destroy = function() {
  // Cleanup when entity is destroyed
};
```

---

### Pattern 6: Input Handling

Handle keyboard, mouse, and touch input.

```javascript
// Keyboard
if (app.keyboard.isPressed(pc.KEY_W)) {
  entity.translate(0, 0, -speed * dt);
}

if (app.keyboard.wasPressed(pc.KEY_SPACE)) {
  entity.rigidbody.applyImpulse(0, 10, 0);
}

// Mouse
app.mouse.on(pc.EVENT_MOUSEDOWN, (event) => {
  if (event.button === pc.MOUSEBUTTON_LEFT) {
    console.log('Left click at', event.x, event.y);
  }
});

app.mouse.on(pc.EVENT_MOUSEMOVE, (event) => {
  const dx = event.dx;
  const dy = event.dy;
  camera.rotate(-dy * 0.2, -dx * 0.2, 0);
});

// Touch
app.touch.on(pc.EVENT_TOUCHSTART, (event) => {
  event.touches.forEach((touch) => {
    console.log('Touch at', touch.x, touch.y);
  });
});

// Raycasting (mouse picking)
app.mouse.on(pc.EVENT_MOUSEDOWN, (event) => {
  const camera = app.root.findByName('camera');
  const cameraComponent = camera.camera;

  const from = cameraComponent.screenToWorld(
    event.x,
    event.y,
    cameraComponent.nearClip
  );

  const to = cameraComponent.screenToWorld(
    event.x,
    event.y,
    cameraComponent.farClip
  );

  const result = app.systems.rigidbody.raycastFirst(from, to);

  if (result) {
    console.log('Hit:', result.entity.name);
    result.entity.model.material.emissive = new pc.Color(1, 0, 0);
  }
});
```

---

### Pattern 7: Animations

Play skeletal animations and tweens.

**Skeletal animation**:
```javascript
// Load animated model
const modelAsset = new pc.Asset('character', 'container', {
  url: '/models/character.glb'
});

app.assets.add(modelAsset);

modelAsset.ready((asset) => {
  const entity = asset.resource.instantiateRenderEntity();
  app.root.addChild(entity);

  // Get animation component
  entity.addComponent('animation', {
    assets: [asset],
    speed: 1.0,
    loop: true,
    activate: true
  });

  // Play specific animation
  entity.animation.play('Walk', 0.2);  // 0.2s blend time

  // Later, transition to run
  entity.animation.play('Run', 0.5);
});

app.assets.load(modelAsset);
```

**Property tweening**:
```javascript
// Animate position
entity.tween(entity.getLocalPosition())
  .to({ x: 5, y: 2, z: 0 }, 2.0, pc.SineInOut)
  .start();

// Animate rotation
entity.tween(entity.getLocalEulerAngles())
  .to({ x: 0, y: 180, z: 0 }, 1.0, pc.Linear)
  .loop(true)
  .yoyo(true)
  .start();

// Animate material color
const color = material.emissive;
app.tween(color)
  .to(new pc.Color(1, 0, 0), 1.0, pc.SineInOut)
  .yoyo(true)
  .loop(true)
  .start();

// Chain tweens
entity.tween(entity.getLocalPosition())
  .to({ y: 2 }, 1.0)
  .to({ y: 0 }, 1.0)
  .delay(0.5)
  .repeat(3)
  .start();
```

---

## Integration Patterns

### Integration 1: React Integration

Wrap PlayCanvas in React components.

```jsx
import React, { useEffect, useRef } from 'react';
import * as pc from 'playcanvas';

function PlayCanvasScene() {
  const canvasRef = useRef(null);
  const appRef = useRef(null);

  useEffect(() => {
    // Initialize
    const app = new pc.Application(canvasRef.current);
    appRef.current = app;

    app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
    app.setCanvasResolution(pc.RESOLUTION_AUTO);

    // Create scene
    const camera = new pc.Entity('camera');
    camera.addComponent('camera', {
      clearColor: new pc.Color(0.1, 0.2, 0.3)
    });
    camera.setPosition(0, 0, 5);
    app.root.addChild(camera);

    const cube = new pc.Entity('cube');
    cube.addComponent('model', { type: 'box' });
    app.root.addChild(cube);

    const light = new pc.Entity('light');
    light.addComponent('light');
    light.setEulerAngles(45, 0, 0);
    app.root.addChild(light);

    app.on('update', (dt) => {
      cube.rotate(10 * dt, 20 * dt, 30 * dt);
    });

    app.start();

    // Cleanup
    return () => {
      app.destroy();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: '100%', height: '100vh' }}
    />
  );
}

export default PlayCanvasScene;
```

---

### Integration 2: Editor Export

Work with PlayCanvas Editor projects.

```javascript
// Export from PlayCanvas Editor
// Download build files, then load in code:

import * as pc from 'playcanvas';

const app = new pc.Application(canvas);

// Load exported project config
fetch('/config.json')
  .then(response => response.json())
  .then(config => {
    // Load scene
    app.scenes.loadSceneHierarchy(config.scene_url, (err, parent) => {
      if (err) {
        console.error('Failed to load scene:', err);
        return;
      }

      // Start application
      app.start();

      // Find entities by name
      const player = app.root.findByName('Player');
      const enemy = app.root.findByName('Enemy');

      // Access scripts
      player.script.myScript.doSomething();
    });
  });
```

---

## Performance Optimization

### 1. Object Pooling

Reuse entities instead of creating/destroying.

```javascript
class EntityPool {
  constructor(app, count) {
    this.app = app;
    this.pool = [];
    this.active = [];

    for (let i = 0; i < count; i++) {
      const entity = new pc.Entity('pooled');
      entity.addComponent('model', { type: 'box' });
      entity.enabled = false;
      app.root.addChild(entity);
      this.pool.push(entity);
    }
  }

  spawn(position) {
    let entity = this.pool.pop();

    if (!entity) {
      // Pool exhausted, create new
      entity = new pc.Entity('pooled');
      entity.addComponent('model', { type: 'box' });
      this.app.root.addChild(entity);
    }

    entity.enabled = true;
    entity.setPosition(position);
    this.active.push(entity);

    return entity;
  }

  despawn(entity) {
    entity.enabled = false;
    const index = this.active.indexOf(entity);
    if (index > -1) {
      this.active.splice(index, 1);
      this.pool.push(entity);
    }
  }
}

// Usage
const pool = new EntityPool(app, 100);
const bullet = pool.spawn(new pc.Vec3(0, 0, 0));

// Later
pool.despawn(bullet);
```

---

### 2. LOD (Level of Detail)

Reduce geometry for distant objects.

```javascript
// Manual LOD switching
app.on('update', () => {
  const distance = camera.getPosition().distance(entity.getPosition());

  if (distance < 10) {
    entity.model.asset = highResModel;
  } else if (distance < 50) {
    entity.model.asset = mediumResModel;
  } else {
    entity.model.asset = lowResModel;
  }
});

// Or disable distant entities
app.on('update', () => {
  entities.forEach(entity => {
    const distance = camera.getPosition().distance(entity.getPosition());
    entity.enabled = distance < 100;
  });
});
```

---

### 3. Batching

Combine static meshes to reduce draw calls.

```javascript
// Enable static batching for entity
entity.model.batchGroupId = 1;

// Batch all entities with same group ID
app.batcher.generate([entity1, entity2, entity3]);
```

---

### 4. Texture Compression

Use compressed texture formats.

```javascript
// When creating textures, use compressed formats
const texture = new pc.Texture(app.graphicsDevice, {
  width: 512,
  height: 512,
  format: pc.PIXELFORMAT_DXT5,  // GPU-compressed
  minFilter: pc.FILTER_LINEAR_MIPMAP_LINEAR,
  magFilter: pc.FILTER_LINEAR,
  mipmaps: true
});
```

---

## Common Pitfalls

### Pitfall 1: Not Starting the Application

**Problem**: Scene renders but nothing happens.

```javascript
// ❌ Wrong - forgot to start
const app = new pc.Application(canvas);
// ... create entities ...
// Nothing happens!

// ✅ Correct
const app = new pc.Application(canvas);
// ... create entities ...
app.start();  // Critical!
```

---

### Pitfall 2: Modifying Entities During Update

**Problem**: Modifying scene graph during iteration.

```javascript
// ❌ Wrong - modifying array during iteration
app.on('update', () => {
  entities.forEach(entity => {
    if (entity.shouldDestroy) {
      entity.destroy();  // Modifies array!
    }
  });
});

// ✅ Correct - mark for deletion, clean up after
const toDestroy = [];

app.on('update', () => {
  entities.forEach(entity => {
    if (entity.shouldDestroy) {
      toDestroy.push(entity);
    }
  });
});

app.on('postUpdate', () => {
  toDestroy.forEach(entity => entity.destroy());
  toDestroy.length = 0;
});
```

---

### Pitfall 3: Memory Leaks with Assets

**Problem**: Not cleaning up loaded assets.

```javascript
// ❌ Wrong - assets never cleaned up
function loadModel() {
  const asset = new pc.Asset('model', 'container', { url: '/model.glb' });
  app.assets.add(asset);
  app.assets.load(asset);
  // Asset stays in memory forever
}

// ✅ Correct - clean up when done
function loadModel() {
  const asset = new pc.Asset('model', 'container', { url: '/model.glb' });
  app.assets.add(asset);

  asset.ready(() => {
    // Use model
  });

  app.assets.load(asset);

  // Clean up later
  return () => {
    app.assets.remove(asset);
    asset.unload();
  };
}

const cleanup = loadModel();
// Later: cleanup();
```

---

### Pitfall 4: Incorrect Transform Hierarchy

**Problem**: Transforms not propagating correctly.

```javascript
// ❌ Wrong - setting world transform on child
const parent = new pc.Entity();
const child = new pc.Entity();
parent.addChild(child);

child.setPosition(5, 0, 0);  // Local position
parent.setPosition(10, 0, 0);
// Child is at (15, 0, 0) in world space

// ✅ Correct - understand local vs world
child.setLocalPosition(5, 0, 0);  // Explicit local
// or
const worldPos = new pc.Vec3(15, 0, 0);
child.setPosition(worldPos);  // Explicit world
```

---

### Pitfall 5: Physics Not Initialized

**Problem**: Physics components don't work.

```javascript
// ❌ Wrong - Ammo.js not loaded
const entity = new pc.Entity();
entity.addComponent('rigidbody', { type: pc.BODYTYPE_DYNAMIC });
// Error: Ammo is not defined

// ✅ Correct - ensure Ammo.js is loaded
const script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/ammo.js@0.0.10/ammo.js';
document.body.appendChild(script);

script.onload = () => {
  Ammo().then((AmmoLib) => {
    window.Ammo = AmmoLib;

    // Now physics works
    const entity = new pc.Entity();
    entity.addComponent('rigidbody', { type: pc.BODYTYPE_DYNAMIC });
    entity.addComponent('collision', { type: 'box' });
  });
};
```

---

### Pitfall 6: Canvas Sizing Issues

**Problem**: Canvas doesn't fill container or respond to resize.

```javascript
// ❌ Wrong - fixed size canvas
const canvas = document.createElement('canvas');
canvas.width = 800;
canvas.height = 600;

// ✅ Correct - responsive canvas
const canvas = document.createElement('canvas');
const app = new pc.Application(canvas);

app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
app.setCanvasResolution(pc.RESOLUTION_AUTO);

window.addEventListener('resize', () => app.resizeCanvas());
```

---

## Resources

- **Official API**: https://api.playcanvas.com/
- **Developer Docs**: https://developer.playcanvas.com/
- **Examples**: https://playcanvas.github.io/
- **Editor**: https://playcanvas.com/
- **GitHub**: https://github.com/playcanvas/engine
- **Forum**: https://forum.playcanvas.com/

---

## Quick Reference

### Application Setup
```javascript
const app = new pc.Application(canvas);
app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
app.setCanvasResolution(pc.RESOLUTION_AUTO);
app.start();
```

### Entity Creation
```javascript
const entity = new pc.Entity('name');
entity.addComponent('model', { type: 'box' });
entity.setPosition(x, y, z);
app.root.addChild(entity);
```

### Update Loop
```javascript
app.on('update', (dt) => {
  // Logic here
});
```

### Loading Assets
```javascript
const asset = new pc.Asset('name', 'type', { url: '/path' });
app.assets.add(asset);
asset.ready(() => { /* use asset */ });
app.assets.load(asset);
```

---

**Related Skills**: For lower-level WebGL control, reference threejs-webgl. For React integration patterns, see react-three-fiber. For physics-heavy simulations, reference babylonjs-engine.



===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/references/api_reference.md =====

# PlayCanvas Engine API Reference

Complete API documentation for the PlayCanvas WebGL/WebGPU engine.

**Version**: 1.70+
**License**: MIT
**Official Docs**: https://api.playcanvas.com/

---

## Table of Contents

1. [Application](#application)
2. [Entity](#entity)
3. [Components](#components)
4. [Assets](#assets)
5. [Graphics](#graphics)
6. [Input](#input)
7. [Physics](#physics)
8. [Audio](#audio)

---

## Application

### pc.Application

The root application managing the rendering loop, scene, and systems.

#### Constructor

```javascript
const app = new pc.Application(canvas, options);
```

**Parameters**:
- `canvas` (HTMLCanvasElement): Canvas element for rendering
- `options` (Object): Configuration options
  - `keyboard` (pc.Keyboard): Keyboard device
  - `mouse` (pc.Mouse): Mouse device
  - `touch` (pc.TouchDevice): Touch device
  - `gamepads` (pc.GamePads): Gamepad devices
  - `graphicsDeviceOptions` (Object): WebGL/WebGPU settings

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `root` | pc.Entity | Root entity of scene hierarchy |
| `scene` | pc.Scene | Scene settings |
| `assets` | pc.AssetRegistry | Asset management |
| `graphicsDevice` | pc.GraphicsDevice | Rendering device |
| `systems` | pc.ComponentSystemRegistry | Component systems |
| `keyboard` | pc.Keyboard | Keyboard input |
| `mouse` | pc.Mouse | Mouse input |
| `touch` | pc.TouchDevice | Touch input |
| `gamepads` | pc.GamePads | Gamepad input |
| `timeScale` | Number | Global time scale (default: 1) |

#### Methods

**setCanvasFillMode(mode)**
```javascript
app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
```

Modes:
- `pc.FILLMODE_NONE`: No auto-resize
- `pc.FILLMODE_FILL_WINDOW`: Fill entire window
- `pc.FILLMODE_KEEP_ASPECT`: Maintain aspect ratio

**setCanvasResolution(mode)**
```javascript
app.setCanvasResolution(pc.RESOLUTION_AUTO);
```

Modes:
- `pc.RESOLUTION_AUTO`: Match window device pixel ratio
- `pc.RESOLUTION_FIXED`: Use canvas width/height

**resizeCanvas()**
```javascript
app.resizeCanvas();
// Manually trigger resize
```

**start()**
```javascript
app.start();
// Start the application update loop
```

**destroy()**
```javascript
app.destroy();
// Clean up application resources
```

#### Events

```javascript
app.on('update', (dt) => {
  // Called every frame
  // dt = delta time in seconds
});

app.on('postUpdate', (dt) => {
  // Called after update
});

app.on('prerender', () => {
  // Before rendering
});

app.on('postrender', () => {
  // After rendering
});

app.on('start', () => {
  // Application started
});

app.on('destroy', () => {
  // Application destroyed
});
```

---

## Entity

### pc.Entity

Nodes in the scene hierarchy with components.

#### Constructor

```javascript
const entity = new pc.Entity(name);
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | String | Entity name |
| `enabled` | Boolean | Render and update enabled |
| `children` | Array | Child entities |
| `parent` | pc.Entity | Parent entity |
| `tags` | pc.Tags | Tag list for searching |

**Component Accessors**:
- `entity.model` - Model component
- `entity.camera` - Camera component
- `entity.light` - Light component
- `entity.script` - Script component
- `entity.rigidbody` - Rigidbody component
- `entity.collision` - Collision component
- `entity.animation` - Animation component
- `entity.sound` - Sound component

#### Transform Methods

**Position**:
```javascript
entity.setPosition(x, y, z);
entity.setPosition(new pc.Vec3(x, y, z));
entity.setLocalPosition(x, y, z);

const pos = entity.getPosition();  // World position
const localPos = entity.getLocalPosition();  // Local position

entity.translate(x, y, z);  // Move relative
entity.translateLocal(x, y, z);  // Move in local space
```

**Rotation**:
```javascript
entity.setEulerAngles(x, y, z);  // Degrees
entity.setLocalEulerAngles(x, y, z);

const angles = entity.getEulerAngles();
const localAngles = entity.getLocalEulerAngles();

entity.rotate(x, y, z);  // Rotate relative (degrees)
entity.rotateLocal(x, y, z);

// Quaternion rotation
entity.setRotation(quat);
const quat = entity.getRotation();

// Look at target
entity.lookAt(target);  // target is Vec3 or Entity
entity.lookAt(x, y, z);
```

**Scale**:
```javascript
entity.setLocalScale(x, y, z);
entity.setLocalScale(new pc.Vec3(x, y, z));

const scale = entity.getLocalScale();
```

**Forward/Right/Up Vectors**:
```javascript
const forward = entity.forward;  // pc.Vec3
const right = entity.right;
const up = entity.up;
```

#### Hierarchy Methods

**addChild(entity)**
```javascript
parent.addChild(child);
```

**removeChild(entity)**
```javascript
parent.removeChild(child);
```

**insertChild(entity, index)**
```javascript
parent.insertChild(child, 0);  // Insert at start
```

**reparent(parent)**
```javascript
entity.reparent(newParent);
```

**find()**
```javascript
// Find by name
const child = entity.find(name => name === 'PlayerModel');

// Find all
const allChildren = entity.find(() => true);
```

**findByName(name)**
```javascript
const player = app.root.findByName('Player');
```

**findByTag(tag)**
```javascript
const enemies = app.root.findByTag('enemy');
// Returns array of entities
```

#### Component Methods

**addComponent(type, data)**
```javascript
entity.addComponent('model', {
  type: 'box'
});
```

**removeComponent(type)**
```javascript
entity.removeComponent('model');
```

**hasComponent(type)**
```javascript
if (entity.hasComponent('rigidbody')) {
  // Has physics
}
```

#### Entity Methods

**clone()**
```javascript
const clone = entity.clone();
app.root.addChild(clone);
```

**destroy()**
```javascript
entity.destroy();
// Removes from parent and cleans up
```

**enable()**/**disable()**
```javascript
entity.enabled = false;  // Disable
entity.enabled = true;   // Enable
```

---

## Components

### Model Component

Renders 3D meshes.

```javascript
entity.addComponent('model', {
  type: 'box',               // Primitive type
  asset: assetId,            // Model asset
  castShadows: true,
  receiveShadows: true,
  castShadowsLightmap: false,
  lightmapped: false,
  isStatic: false,
  layers: [pc.LAYERID_WORLD]
});
```

**Primitive Types**:
- `'box'`, `'capsule'`, `'cone'`, `'cylinder'`, `'plane'`, `'sphere'`

**Properties**:
```javascript
entity.model.meshInstances;  // Array of MeshInstance
entity.model.material = material;
entity.model.asset = assetId;
```

---

### Camera Component

Renders the scene from a viewpoint.

```javascript
entity.addComponent('camera', {
  clearColor: new pc.Color(0, 0, 0, 1),
  fov: 45,
  aspectRatio: 16/9,  // Auto-calculated if null
  nearClip: 0.1,
  farClip: 1000,
  projection: pc.PROJECTION_PERSPECTIVE,
  priority: 0,
  frustumCulling: true,
  rect: new pc.Vec4(0, 0, 1, 1),  // Viewport
  layers: [pc.LAYERID_WORLD, pc.LAYERID_UI]
});
```

**Projection Types**:
- `pc.PROJECTION_PERSPECTIVE`
- `pc.PROJECTION_ORTHOGRAPHIC`

**Methods**:
```javascript
// Screen to world conversion
const worldPos = camera.camera.screenToWorld(screenX, screenY, depth);

// World to screen
const screenPos = camera.camera.worldToScreen(worldPos);

// Ray from screen point
const ray = camera.camera.screenToWorld(screenX, screenY, camera.camera.nearClip);
```

---

### Light Component

Illuminates the scene.

```javascript
entity.addComponent('light', {
  type: pc.LIGHTTYPE_DIRECTIONAL,
  color: new pc.Color(1, 1, 1),
  intensity: 1,
  castShadows: true,
  shadowDistance: 40,
  shadowResolution: 2048,
  shadowBias: 0.05,
  normalOffsetBias: 0.05,
  range: 10,              // Point/Spot only
  innerConeAngle: 40,     // Spot only
  outerConeAngle: 45,     // Spot only
  falloffMode: pc.LIGHTFALLOFF_INVERSESQUARED,
  layers: [pc.LAYERID_WORLD]
});
```

**Light Types**:
- `pc.LIGHTTYPE_DIRECTIONAL`: Sun-like, parallel rays
- `pc.LIGHTTYPE_POINT`: Omnidirectional, like a bulb
- `pc.LIGHTTYPE_SPOT`: Cone-shaped, like a flashlight

**Shadow Types**:
```javascript
entity.light.shadowType = pc.SHADOW_PCF3;
```
- `pc.SHADOW_PCF3`: 3x3 PCF (good quality)
- `pc.SHADOW_PCF5`: 5x5 PCF (better quality, slower)
- `pc.SHADOW_VSM8`: Variance shadow maps (softer)

---

### Rigidbody Component

Adds physics simulation.

```javascript
entity.addComponent('rigidbody', {
  type: pc.BODYTYPE_DYNAMIC,
  mass: 1,
  linearDamping: 0,
  angularDamping: 0,
  linearFactor: new pc.Vec3(1, 1, 1),
  angularFactor: new pc.Vec3(1, 1, 1),
  friction: 0.5,
  restitution: 0,
  group: pc.BODYGROUP_DYNAMIC,
  mask: pc.BODYMASK_ALL
});
```

**Body Types**:
- `pc.BODYTYPE_STATIC`: Immovable (terrain, buildings)
- `pc.BODYTYPE_DYNAMIC`: Affected by forces
- `pc.BODYTYPE_KINEMATIC`: Moved by script, not physics

**Methods**:
```javascript
// Apply force
entity.rigidbody.applyForce(x, y, z);
entity.rigidbody.applyForce(new pc.Vec3(x, y, z));

// Apply force at point
entity.rigidbody.applyForce(force, point);

// Apply impulse (instant velocity change)
entity.rigidbody.applyImpulse(x, y, z);
entity.rigidbody.applyImpulse(impulse, point);

// Apply torque
entity.rigidbody.applyTorque(x, y, z);

// Apply torque impulse
entity.rigidbody.applyTorqueImpulse(x, y, z);

// Velocity
entity.rigidbody.linearVelocity = new pc.Vec3(x, y, z);
entity.rigidbody.angularVelocity = new pc.Vec3(x, y, z);

// Teleport
entity.rigidbody.teleport(x, y, z);
entity.rigidbody.teleport(position, rotation);
```

---

### Collision Component

Defines physics collision shape.

```javascript
entity.addComponent('collision', {
  type: 'box',
  halfExtents: new pc.Vec3(0.5, 0.5, 0.5),
  radius: 0.5,           // Sphere/Capsule
  axis: pc.AXIS_Y,       // Capsule/Cylinder
  height: 2,             // Capsule/Cylinder
  asset: assetId,        // Mesh collision
  renderAsset: assetId   // Mesh collision (render)
});
```

**Collision Types**:
- `'box'`: Box shape
- `'sphere'`: Sphere shape
- `'capsule'`: Capsule shape
- `'cylinder'`: Cylinder shape
- `'cone'`: Cone shape
- `'mesh'`: Triangle mesh (static only)
- `'compound'`: Multiple shapes

**Events**:
```javascript
entity.collision.on('collisionstart', (result) => {
  console.log('Collision with:', result.other.name);
  console.log('Contact point:', result.contacts[0].point);
});

entity.collision.on('collisionend', (other) => {
  console.log('Collision ended with:', other.name);
});

entity.collision.on('contact', (result) => {
  // Contact maintained
});
```

---

### Script Component

Runs custom JavaScript code.

```javascript
entity.addComponent('script');
entity.script.create('scriptName', {
  attributes: {
    speed: 10,
    target: targetEntity
  }
});
```

**Script Definition**:
```javascript
const MyScript = pc.createScript('myScript');

MyScript.attributes.add('speed', {
  type: 'number',
  default: 10,
  title: 'Movement Speed',
  description: 'Units per second'
});

MyScript.attributes.add('target', {
  type: 'entity',
  title: 'Target Entity'
});

MyScript.prototype.initialize = function() {
  // Called once
};

MyScript.prototype.update = function(dt) {
  // Called every frame
  this.entity.translate(0, 0, this.speed * dt);
};

MyScript.prototype.postUpdate = function(dt) {
  // After all updates
};

MyScript.prototype.destroy = function() {
  // Cleanup
};
```

**Attribute Types**:
- `'boolean'`, `'number'`, `'string'`
- `'entity'`, `'asset'`, `'rgb'`, `'rgba'`
- `'vec2'`, `'vec3'`, `'vec4'`
- `'curve'`, `'colorcurve'`
- `'json'`

---

### Animation Component

Plays skeletal animations.

```javascript
entity.addComponent('animation', {
  assets: [animAsset],
  speed: 1.0,
  loop: true,
  activate: true
});
```

**Methods**:
```javascript
// Play animation
entity.animation.play('Run', 0.2);  // 0.2s blend time

// Get current animations
const anims = entity.animation.animations;

// Animation events
entity.animation.on('animationend', (name) => {
  console.log('Animation ended:', name);
});
```

---

### Sound Component

3D positional audio.

```javascript
entity.addComponent('sound', {
  positional: true,
  refDistance: 1,
  maxDistance: 10000,
  rollOffFactor: 1,
  distanceModel: pc.DISTANCE_LINEAR,
  slots: {
    'music': {
      asset: musicAsset,
      autoPlay: true,
      loop: true,
      volume: 0.5,
      pitch: 1.0
    }
  }
});
```

**Methods**:
```javascript
entity.sound.play('slotName');
entity.sound.pause('slotName');
entity.sound.stop('slotName');

entity.sound.volume = 0.8;  // Global volume
```

---

## Assets

### pc.AssetRegistry

Manages loading and caching of assets.

**add(asset)**
```javascript
const asset = new pc.Asset('name', 'texture', { url: '/texture.jpg' });
app.assets.add(asset);
```

**load(asset)**
```javascript
app.assets.load(asset);
```

**remove(asset)**
```javascript
app.assets.remove(asset);
```

**find()**
```javascript
// Find by name
const asset = app.assets.find('PlayerModel');

// Find by type
const textures = app.assets.findAll('texture');

// Find by tag
const tagged = app.assets.findByTag('environment');
```

**Events**:
```javascript
asset.ready((loadedAsset) => {
  // Asset loaded
  console.log('Loaded:', loadedAsset.resource);
});

asset.on('load', (asset) => {
  // Asset loaded
});

asset.on('error', (err) => {
  // Loading failed
});

asset.on('remove', () => {
  // Asset removed from registry
});
```

---

### Asset Types

**Texture**:
```javascript
const texture = new pc.Asset('diffuse', 'texture', {
  url: '/textures/diffuse.jpg'
});
```

**Model (Container)**:
```javascript
const model = new pc.Asset('character', 'container', {
  url: '/models/character.glb'
});

model.ready((asset) => {
  const entity = asset.resource.instantiateRenderEntity();
  app.root.addChild(entity);
});
```

**Material**:
```javascript
const material = new pc.Asset('custom', 'material');
```

**Audio**:
```javascript
const audio = new pc.Asset('music', 'audio', {
  url: '/audio/music.mp3'
});
```

**Script**:
```javascript
const script = new pc.Asset('playerController', 'script', {
  url: '/scripts/player-controller.js'
});
```

---

## Graphics

### pc.StandardMaterial

PBR material for rendering.

```javascript
const material = new pc.StandardMaterial();

// Diffuse (albedo)
material.diffuse = new pc.Color(1, 0, 0);  // Red
material.diffuseMap = texture;

// Metalness
material.metalness = 0.5;
material.metalnessMap = metalnessTexture;

// Gloss (inverse of roughness)
material.gloss = 0.8;
material.glossMap = roughnessTexture;

// Normal map
material.normalMap = normalTexture;
material.bumpiness = 1.0;

// Emissive
material.emissive = new pc.Color(1, 1, 0);
material.emissiveMap = emissiveTexture;
material.emissiveIntensity = 1.0;

// Ambient occlusion
material.aoMap = aoTexture;

// Opacity
material.opacity = 0.5;
material.opacityMap = opacityTexture;
material.blendType = pc.BLEND_NORMAL;

// Update material
material.update();
```

**Blend Types**:
- `pc.BLEND_NONE`: Opaque
- `pc.BLEND_NORMAL`: Alpha blending
- `pc.BLEND_ADDITIVE`: Additive blending
- `pc.BLEND_MULTIPLICATIVE`: Multiply blending

---

### pc.Texture

2D texture resource.

```javascript
const texture = new pc.Texture(app.graphicsDevice, {
  width: 512,
  height: 512,
  format: pc.PIXELFORMAT_RGBA8,
  minFilter: pc.FILTER_LINEAR_MIPMAP_LINEAR,
  magFilter: pc.FILTER_LINEAR,
  addressU: pc.ADDRESS_REPEAT,
  addressV: pc.ADDRESS_REPEAT,
  mipmaps: true,
  anisotropy: 16
});
```

**Pixel Formats**:
- `pc.PIXELFORMAT_RGBA8`: Standard 8-bit RGBA
- `pc.PIXELFORMAT_RGB8`: 8-bit RGB
- `pc.PIXELFORMAT_DXT5`: GPU-compressed
- `pc.PIXELFORMAT_ETC2_RGBA`: Mobile compression

**Filters**:
- `pc.FILTER_NEAREST`: Pixelated
- `pc.FILTER_LINEAR`: Smooth
- `pc.FILTER_LINEAR_MIPMAP_LINEAR`: Trilinear (best quality)

**Address Modes**:
- `pc.ADDRESS_REPEAT`: Tile texture
- `pc.ADDRESS_CLAMP`: Clamp to edge
- `pc.ADDRESS_MIRRORED_REPEAT`: Mirror tiling

---

## Input

### pc.Keyboard

Keyboard input handling.

```javascript
const keyboard = new pc.Keyboard(window);

// Check if key is currently pressed
if (keyboard.isPressed(pc.KEY_W)) {
  player.translate(0, 0, -speed * dt);
}

// Check if key was just pressed this frame
if (keyboard.wasPressed(pc.KEY_SPACE)) {
  player.jump();
}

// Check if key was just released
if (keyboard.wasReleased(pc.KEY_SHIFT)) {
  player.stopSprinting();
}

// Events
keyboard.on(pc.EVENT_KEYDOWN, (event) => {
  console.log('Key down:', event.key);
});

keyboard.on(pc.EVENT_KEYUP, (event) => {
  console.log('Key up:', event.key);
});
```

**Key Constants**:
- `pc.KEY_W`, `pc.KEY_A`, `pc.KEY_S`, `pc.KEY_D`
- `pc.KEY_SPACE`, `pc.KEY_SHIFT`, `pc.KEY_CONTROL`
- `pc.KEY_ENTER`, `pc.KEY_ESCAPE`
- `pc.KEY_UP`, `pc.KEY_DOWN`, `pc.KEY_LEFT`, `pc.KEY_RIGHT`
- `pc.KEY_0` through `pc.KEY_9`
- `pc.KEY_A` through `pc.KEY_Z`

---

### pc.Mouse

Mouse input handling.

```javascript
const mouse = new pc.Mouse(canvas);

// Events
mouse.on(pc.EVENT_MOUSEDOWN, (event) => {
  if (event.button === pc.MOUSEBUTTON_LEFT) {
    console.log('Left click at:', event.x, event.y);
  }
});

mouse.on(pc.EVENT_MOUSEUP, (event) => {
  console.log('Mouse up');
});

mouse.on(pc.EVENT_MOUSEMOVE, (event) => {
  const dx = event.dx;  // Delta movement
  const dy = event.dy;

  camera.rotate(-dy * 0.2, -dx * 0.2, 0);
});

mouse.on(pc.EVENT_MOUSEWHEEL, (event) => {
  zoom += event.wheelDelta * 0.1;
});
```

**Mouse Buttons**:
- `pc.MOUSEBUTTON_LEFT`: Left button
- `pc.MOUSEBUTTON_MIDDLE`: Middle button
- `pc.MOUSEBUTTON_RIGHT`: Right button

**Properties**:
```javascript
mouse.isPressed(pc.MOUSEBUTTON_LEFT);  // Check if button pressed
```

---

### pc.TouchDevice

Touch input for mobile.

```javascript
const touch = new pc.TouchDevice(canvas);

touch.on(pc.EVENT_TOUCHSTART, (event) => {
  event.touches.forEach((touch, index) => {
    console.log(`Touch ${index} at:`, touch.x, touch.y);
  });
});

touch.on(pc.EVENT_TOUCHEND, (event) => {
  // Touches ended
});

touch.on(pc.EVENT_TOUCHMOVE, (event) => {
  const touch = event.touches[0];
  const dx = touch.dx;
  const dy = touch.dy;
});
```

---

## Physics

### Raycasting

Cast rays to detect collisions.

```javascript
// Raycast from camera through mouse
const camera = app.root.findByName('Camera');
const from = camera.camera.screenToWorld(mouseX, mouseY, camera.camera.nearClip);
const to = camera.camera.screenToWorld(mouseX, mouseY, camera.camera.farClip);

const result = app.systems.rigidbody.raycastFirst(from, to);

if (result) {
  console.log('Hit entity:', result.entity.name);
  console.log('Hit point:', result.point);
  console.log('Hit normal:', result.normal);
}

// Raycast all
const results = app.systems.rigidbody.raycastAll(from, to);
results.forEach(result => {
  console.log('Hit:', result.entity.name);
});
```

---

## Audio

### pc.SoundComponent

3D positional audio.

```javascript
entity.addComponent('sound');

// Add sound slot
entity.sound.addSlot('footstep', {
  asset: footstepAsset,
  autoPlay: false,
  loop: false,
  volume: 0.8,
  pitch: 1.0,
  positional: true,
  refDistance: 1,
  maxDistance: 20
});

// Play sound
entity.sound.play('footstep');

// Stop sound
entity.sound.stop('footstep');

// Pause sound
entity.sound.pause('footstep');

// Resume
entity.sound.resume('footstep');
```

---

## Utilities

### pc.Vec3

3D vector.

```javascript
const v = new pc.Vec3(x, y, z);

// Operations
v.add(other);
v.sub(other);
v.mul(scalar);
v.div(scalar);
v.dot(other);
v.cross(other);
v.normalize();
v.length();
v.distance(other);
v.lerp(a, b, t);
```

### pc.Color

RGBA color.

```javascript
const color = new pc.Color(r, g, b, a);  // 0-1 range

// Conversion
const hex = color.toString();  // "#RRGGBB"
```

### pc.Quat

Quaternion rotation.

```javascript
const quat = new pc.Quat();
quat.setFromEulerAngles(x, y, z);
quat.slerp(a, b, t);  // Spherical interpolation
```

---

## Constants Reference

**Fill Modes**:
- `pc.FILLMODE_NONE`
- `pc.FILLMODE_FILL_WINDOW`
- `pc.FILLMODE_KEEP_ASPECT`

**Resolution Modes**:
- `pc.RESOLUTION_AUTO`
- `pc.RESOLUTION_FIXED`

**Projection Types**:
- `pc.PROJECTION_PERSPECTIVE`
- `pc.PROJECTION_ORTHOGRAPHIC`

**Light Types**:
- `pc.LIGHTTYPE_DIRECTIONAL`
- `pc.LIGHTTYPE_POINT`
- `pc.LIGHTTYPE_SPOT`

**Body Types**:
- `pc.BODYTYPE_STATIC`
- `pc.BODYTYPE_DYNAMIC`
- `pc.BODYTYPE_KINEMATIC`

**Blend Types**:
- `pc.BLEND_NONE`
- `pc.BLEND_NORMAL`
- `pc.BLEND_ADDITIVE`
- `pc.BLEND_MULTIPLICATIVE`

---

## License

MIT - Free for commercial and personal use.



===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/references/editor_workflow.md =====

# PlayCanvas Editor Workflow Guide

Complete guide for working with the PlayCanvas Editor and integrating with the engine.

---

## Table of Contents

1. [Editor vs Engine-Only](#editor-vs-engine-only)
2. [Project Setup](#project-setup)
3. [Asset Pipeline](#asset-pipeline)
4. [Scene Management](#scene-management)
5. [Script Workflow](#script-workflow)
6. [Publishing & Deployment](#publishing--deployment)
7. [Editor-Code Integration](#editor-code-integration)

---

## Editor vs Engine-Only

### PlayCanvas Editor (Online)

**Pros**:
- Visual scene editing
- Real-time collaboration
- Built-in asset pipeline
- Instant preview
- Version control
- No build step required

**Cons**:
- Requires online access
- Less control over build process
- Tied to PlayCanvas platform

**Best for**: Game projects, team collaboration, rapid prototyping

---

### Engine-Only (Code-First)

**Pros**:
- Full control over code
- Works offline
- Custom build pipeline
- Version control with Git
- No platform lock-in

**Cons**:
- Manual scene setup
- No visual editor
- Manual asset loading
- More code required

**Best for**: Web apps, embedded 3D, custom workflows

---

## Project Setup

### Creating Editor Project

1. **Sign up** at https://playcanvas.com
2. **Create New Project**
   - Choose template (Blank, First Person, etc.)
   - Set project name
3. **Open Editor**
   - Launch visual editor
   - Scene hierarchy on left
   - Viewport in center
   - Inspector on right

---

### Editor Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│  File  Edit  View  Develop  Tools  Help    [Play] [Share]│
├───────┬───────────────────────────────┬─────────────────┤
│       │                               │                 │
│ Scene │        Viewport              │   Inspector     │
│ Tree  │                               │                 │
│       │                               │   Properties    │
│  ├─Camera│     [3D View]              │   for selected  │
│  ├─Light │                            │   entity        │
│  └─Cube  │                            │                 │
│       │                               │                 │
├───────┴───────────────────────────────┴─────────────────┤
│            Assets Panel                                 │
│  [Models] [Materials] [Textures] [Scripts] [Scenes]    │
└─────────────────────────────────────────────────────────┘
```

---

### Project Structure

**Editor Project**:
```
MyProject/
├── assets/
│   ├── models/
│   ├── textures/
│   ├── materials/
│   ├── scripts/
│   └── scenes/
├── scenes/
│   └── Game.json
└── config.json
```

**Exported Project**:
```
build/
├── index.html
├── __game-scripts.js
├── __loading.js
├── __start__.js
├── config.json
├── files/
│   └── assets/
└── styles.css
```

---

## Asset Pipeline

### Uploading Assets

**3D Models**:
- Supported: `.glb`, `.gltf`, `.fbx`, `.obj`
- Drag & drop into Assets panel
- Auto-generates material instances

**Textures**:
- Supported: `.jpg`, `.png`, `.dds`, `.ktx2`, `.basis`
- Automatically creates texture asset
- Compression options available

**Audio**:
- Supported: `.mp3`, `.ogg`, `.wav`
- 3D positional or 2D audio

**Scripts**:
- Create new script in Assets panel
- Opens code editor
- Hot-reload on save

---

### Asset Import Settings

**Model Import**:
```javascript
// In Editor:
// 1. Select model asset
// 2. Inspector shows import options:
// - Preserve mapping (UV mapping)
// - Create materials
// - Create animations
// - Override axis
```

**Texture Import**:
```javascript
// Compression settings:
// - None (original)
// - DXT (Desktop)
// - PVR (iOS)
// - ETC (Android)
// - ASTC (Modern mobile)
// - Basis (Universal)
```

---

### Creating Materials

**In Editor**:
1. Assets Panel → Right-click → New Material
2. Select material
3. Inspector shows material properties:
   - Diffuse color
   - Diffuse map
   - Metalness/Gloss
   - Normal map
   - Emissive
   - Ambient occlusion

**Material Graph** (Advanced):
- Visual node-based material editor
- Custom shader creation
- Real-time preview

---

## Scene Management

### Scene Hierarchy

**Creating Entities**:
```
Right-click in Hierarchy → Add Entity
Options:
- Empty entity
- Box, Sphere, Cylinder, etc.
- Camera
- Light
- Group (empty parent)
```

**Organizing**:
- Drag entities to reparent
- Multi-select with Ctrl/Cmd
- Group related entities
- Use naming conventions:
  ```
  Player
  ├── Model
  ├── Camera
  └── Collider

  Enemies
  ├── Enemy_01
  ├── Enemy_02
  └── Enemy_03
  ```

---

### Components in Editor

**Adding Components**:
1. Select entity
2. Inspector → Add Component
3. Configure properties

**Component Settings**:
- Editable in Inspector
- Color pickers for colors
- Asset pickers for references
- Vector editors for positions

**Example - Camera Component**:
```
Camera Component
├── Clear Color: [Color Picker]
├── FOV: [Slider] 45°
├── Near Clip: [Input] 0.1
├── Far Clip: [Input] 1000
├── Projection: [Dropdown] Perspective
└── Priority: [Input] 0
```

---

### Tags and Layers

**Tags**:
- Add tags to entities for searching
- Use in scripts: `app.root.findByTag('enemy')`

**In Editor**:
1. Select entity
2. Inspector → Tags
3. Add/remove tags

**Layers**:
- Control rendering order
- Separate UI from world
- Custom post-processing per layer

**Default Layers**:
- World (3D objects)
- UI (2D interface)
- Skybox
- Immediate (debug drawing)

---

## Script Workflow

### Creating Scripts in Editor

**New Script**:
1. Assets Panel → New Script
2. Name your script (e.g., `playerController`)
3. Opens code editor

**Script Template**:
```javascript
var PlayerController = pc.createScript('playerController');

// Attributes (editable in Editor)
PlayerController.attributes.add('speed', {
    type: 'number',
    default: 10,
    title: 'Movement Speed'
});

PlayerController.attributes.add('jumpForce', {
    type: 'number',
    default: 5
});

// Initialize
PlayerController.prototype.initialize = function() {
    this.velocity = new pc.Vec3();
};

// Update every frame
PlayerController.prototype.update = function(dt) {
    var forward = this.entity.forward;
    var right = this.entity.right;

    // Movement
    if (this.app.keyboard.isPressed(pc.KEY_W)) {
        this.entity.translate(forward.mulScalar(this.speed * dt));
    }

    if (this.app.keyboard.isPressed(pc.KEY_SPACE)) {
        this.entity.rigidbody.applyImpulse(0, this.jumpForce, 0);
    }
};
```

---

### Attaching Scripts

**In Editor**:
1. Select entity
2. Add Component → Script
3. Add Script → Select your script
4. Configure attributes in Inspector

**Script Attributes in Inspector**:
```
Script Component
└── playerController
    ├── Speed: [10]
    ├── Jump Force: [5]
    └── [Add Script]
```

---

### Script Communication

**Between Scripts**:
```javascript
// In one script
this.entity.script.otherScript.doSomething();

// Fire events
this.app.fire('player:died', playerEntity);

// Listen to events
this.app.on('enemy:spawned', function(enemy) {
    console.log('Enemy spawned:', enemy.name);
});
```

---

### Debugging Scripts

**Console Logging**:
```javascript
console.log('Player position:', this.entity.getPosition());
console.warn('Low health!');
console.error('Failed to load asset');
```

**Launch Tab**:
- Editor → Launch → Opens game in new tab
- F12 for DevTools
- Console shows logs
- Edit scripts in Editor, auto-reloads

---

## Publishing & Deployment

### Publishing from Editor

**Steps**:
1. **Build**
   - Settings → Publishing
   - Configure build settings
   - Click "Publish"

2. **Download Build**
   - Download ZIP
   - Extract files
   - Upload to web server

**Build Settings**:
```javascript
{
  "name": "My Game",
  "version": "1.0.0",
  "scenes": [
    { "url": "game.json" }
  ],
  "use_device_pixel_ratio": true,
  "resolution_mode": "AUTO",
  "fill_mode": "FILL_WINDOW",
  "width": 1280,
  "height": 720
}
```

---

### Hosting Options

**PlayCanvas Hosting**:
- Click "Publish to PlayCanvas"
- Get shareable URL
- Free with watermark
- Premium for custom domain

**Self-Hosting**:
1. Download build
2. Upload to:
   - **Netlify**: Drag & drop
   - **Vercel**: Connect GitHub
   - **GitHub Pages**: Push to gh-pages branch
   - **AWS S3**: Static website hosting
   - **Any web server**: Just upload files

**CORS Considerations**:
```javascript
// If loading assets from different domain
// Server must send CORS headers:
Access-Control-Allow-Origin: *
```

---

### Optimization for Production

**Before Publishing**:

1. **Texture Compression**
   - Use Basis for universal compression
   - Or platform-specific (DXT/PVR/ETC)

2. **Script Concatenation**
   - Editor automatically concatenates scripts
   - Minifies in production builds

3. **Asset Loading**
   - Preload critical assets
   - Lazy load optional content

4. **Scene Settings**
   - Disable debug rendering
   - Set appropriate quality settings

---

## Editor-Code Integration

### Exporting Editor Scenes

**Option 1: REST API**
```javascript
// Download scene JSON via PlayCanvas API
fetch('https://playcanvas.com/api/projects/{id}/scenes/{sceneId}', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
})
.then(res => res.json())
.then(sceneData => {
  console.log('Scene data:', sceneData);
});
```

**Option 2: Download Build**
- Editor → Settings → Publishing → Download
- Extract ZIP
- Use `config.json` and scene files in engine code

---

### Loading Editor Scenes in Code

```javascript
import * as pc from 'playcanvas';

const app = new pc.Application(canvas);

// Load scene from Editor export
fetch('config.json')
  .then(res => res.json())
  .then(config => {
    // Load scene hierarchy
    const sceneUrl = config.scenes[0].url;

    app.scenes.loadSceneHierarchy(sceneUrl, (err, parent) => {
      if (err) {
        console.error('Failed to load scene:', err);
        return;
      }

      console.log('Scene loaded');

      // Find entities
      const player = app.root.findByName('Player');
      const camera = app.root.findByName('Camera');

      // Start application
      app.start();
    });

    // Load scene settings
    app.scenes.loadSceneSettings(config.scenes[0].url, (err) => {
      if (err) console.error('Failed to load settings:', err);
    });
  });
```

---

### Hybrid Workflow

**Editor for Scenes, Code for Logic**:

1. **Design in Editor**
   - Create scene layout
   - Configure entities
   - Set up components

2. **Export Scene**
   - Download build
   - Get scene JSON files

3. **Code Logic**
   - Load scenes in code
   - Add custom game logic
   - Extend with JavaScript

**Example**:
```javascript
// Load Editor scene
app.scenes.loadSceneHierarchy('scene.json', (err, root) => {
  if (err) return;

  // Find Editor entities
  const player = root.findByName('Player');
  const enemies = root.findByTag('enemy');

  // Add code-based logic
  const gameManager = new pc.Entity('GameManager');
  gameManager.addComponent('script');
  gameManager.script.create('gameManager');
  app.root.addChild(gameManager);

  // Start game
  app.start();
  app.fire('game:start');
});
```

---

### Accessing Editor Attributes in Code

**In Editor Script**:
```javascript
var MyScript = pc.createScript('myScript');

MyScript.attributes.add('target', {
  type: 'entity',
  title: 'Target Entity'
});

MyScript.attributes.add('speed', {
  type: 'number',
  default: 10
});
```

**Accessing from Other Scripts**:
```javascript
// Get script instance
const myScript = entity.script.myScript;

// Read attributes
console.log('Target:', myScript.target);
console.log('Speed:', myScript.speed);

// Modify at runtime
myScript.speed = 20;
```

---

## Version Control

### Editor Projects

**Built-in Version Control**:
- Editor → Version Control
- Checkpoint system
- Branch management
- Conflict resolution

**Checkpoints**:
- Create checkpoint before major changes
- Name checkpoints descriptively
- Restore previous versions

---

### Engine-Only Projects

**Git Workflow**:
```bash
git init
git add .
git commit -m "Initial PlayCanvas project"

# .gitignore
node_modules/
build/
*.log
.DS_Store
```

**Structure**:
```
project/
├── src/
│   ├── index.html
│   ├── main.js
│   └── scripts/
├── assets/
│   ├── models/
│   └── textures/
├── package.json
└── README.md
```

---

## Collaboration

### Editor Collaboration

**Real-time Editing**:
- Multiple users in same project
- See others' cursors
- Live updates
- Chat built-in

**Permissions**:
- Owner (full access)
- Admin (edit + manage)
- Write (edit only)
- Read (view only)

---

### Team Workflow

**Best Practices**:

1. **Scene Ownership**
   - One person per scene at a time
   - Use checkpoints before switching

2. **Asset Organization**
   - Consistent naming: `character_player_diffuse.png`
   - Folder structure: `assets/characters/player/`

3. **Script Conventions**
   - camelCase for functions
   - PascalCase for classes
   - Prefix custom scripts: `game_playerController.js`

4. **Communication**
   - Use Editor chat
   - Document major changes
   - Code reviews for critical scripts

---

## Debugging in Editor

### Launch & Debug

**Launch Tab**:
- Editor → Launch
- Opens game in new tab with DevTools

**Debug Options**:
- **Profiler**: Performance metrics
- **Inspector**: Scene graph at runtime
- **Console**: Logs and errors

**Profiler**:
```
Launch → Profiler
Shows:
- FPS
- Draw calls
- Triangle count
- Texture memory
- Script execution time
```

---

### Editor Console

**Accessing Engine in Console**:
```javascript
// In Launch tab console:
pc.app              // Application instance
pc.app.root         // Root entity
pc.app.systems      // Component systems

// Find entities
pc.app.root.findByName('Player')
pc.app.root.findByTag('enemy')

// Inspect entities
const player = pc.app.root.findByName('Player');
console.log('Position:', player.getPosition());
console.log('Components:', player.c);  // All components
```

---

## Tips & Best Practices

### Performance

**In Editor**:
- Use LOD for complex models
- Enable frustum culling
- Batch static objects
- Compress textures

**Scene Organization**:
- Group related entities
- Disable entities instead of destroying
- Use object pooling for bullets/particles

---

### Asset Management

**Naming Conventions**:
```
Models:       char_player.glb
Textures:     char_player_diffuse.png
Materials:    mat_player_body
Scripts:      player_controller.js
Scenes:       level_01.json
```

**Folder Structure**:
```
assets/
├── characters/
│   ├── player/
│   └── enemies/
├── environment/
│   ├── props/
│   └── terrain/
├── fx/
│   ├── particles/
│   └── sounds/
└── ui/
```

---

### Editor Shortcuts

**Navigation**:
- `F`: Frame selected entity
- `W/A/S/D`: Move viewport
- `Q/E`: Up/down
- `Right-click + drag`: Rotate view
- `Middle-click + drag`: Pan view
- `Scroll`: Zoom

**Editing**:
- `Ctrl/Cmd + D`: Duplicate entity
- `Delete`: Delete entity
- `Ctrl/Cmd + Z`: Undo
- `Ctrl/Cmd + Shift + Z`: Redo
- `Ctrl/Cmd + G`: Group entities

**Tools**:
- `1`: Select mode
- `2`: Translate mode
- `3`: Rotate mode
- `4`: Scale mode
- `Space`: Toggle between modes

---

## Resources

- **Editor**: https://playcanvas.com
- **Developer Docs**: https://developer.playcanvas.com
- **API Reference**: https://api.playcanvas.com
- **Tutorials**: https://developer.playcanvas.com/tutorials/
- **Forum**: https://forum.playcanvas.com
- **Examples**: https://playcanvas.github.io

---

## Quick Reference

### Editor Workflow
```
1. Create project
2. Import assets
3. Build scene hierarchy
4. Add components
5. Attach scripts
6. Configure settings
7. Test in Launch tab
8. Publish/Download
```

### Script Workflow
```
1. Assets → New Script
2. Write code in editor
3. Attach to entity
4. Configure attributes
5. Test in Launch tab
6. Debug in console
7. Iterate
```

### Publishing Workflow
```
1. Settings → Publishing
2. Configure build settings
3. Click Publish
4. Download build
5. Upload to hosting
6. Test live site
```

---

This guide covers the complete PlayCanvas Editor workflow from project creation to deployment. Use the Editor for visual scene design and the Engine API for custom code logic.



===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/references/optimization_guide.md =====

# PlayCanvas Optimization Guide

Comprehensive performance optimization strategies for PlayCanvas applications.

---

## Table of Contents

1. [Performance Profiling](#performance-profiling)
2. [Rendering Optimization](#rendering-optimization)
3. [Asset Optimization](#asset-optimization)
4. [Memory Management](#memory-management)
5. [Script Optimization](#script-optimization)
6. [Mobile Optimization](#mobile-optimization)
7. [Network & Loading](#network--loading)

---

## Performance Profiling

### Built-in Profiler

**Enable Profiler**:
```javascript
// In code
app.stats = new pc.ApplicationStats(app.graphicsDevice);

// Show FPS counter
const container = document.createElement('div');
document.body.appendChild(container);
container.style.cssText = 'position:absolute;top:10px;left:10px;color:white;background:rgba(0,0,0,0.5);padding:10px;font-family:monospace;';

app.on('update', () => {
  if (app.stats) {
    container.textContent = [
      `FPS: ${Math.round(1 / app.stats.frame.updateTime * 1000)}`,
      `Draw Calls: ${app.stats.drawCalls.total}`,
      `Triangles: ${app.stats.triangles.total}`,
      `Shaders: ${app.stats.shaders}`,
      `Materials: ${app.stats.materials}`,
      `Textures: ${app.stats.vram.tex / 1024 / 1024}MB`
    ].join('\n');
  }
});
```

---

### Browser DevTools

**Performance Tab**:
- Record session
- Analyze frame timing
- Identify bottlenecks

**Key Metrics**:
- **Frame Time**: Should be < 16.67ms (60 FPS)
- **Script Time**: JavaScript execution
- **Rendering**: GPU work
- **Paint**: Browser compositing

**Console Profiling**:
```javascript
console.time('sceneLoad');
// ... load scene ...
console.timeEnd('sceneLoad');

console.profile('gameLoop');
// ... run game ...
console.profileEnd('gameLoop');
```

---

### Common Performance Bottlenecks

**Symptoms**:
```
Low FPS (< 30):
  → Too many draw calls
  → Complex materials/shaders
  → Too many triangles
  → Unoptimized scripts

High Memory Usage:
  → Large textures
  → Memory leaks
  → Too many entities

Slow Loading:
  → Large assets
  → Uncompressed textures
  → Synchronous loading
```

---

## Rendering Optimization

### 1. Reduce Draw Calls

**Problem**: Each mesh = 1 draw call. Too many = slow.

**Target**: < 100 draw calls for 60 FPS

**Solution 1: Static Batching**
```javascript
// Mark entities as static
entity.model.batchGroupId = 1;
entity2.model.batchGroupId = 1;
entity3.model.batchGroupId = 1;

// Batch all with same ID
app.batcher.generate([entity, entity2, entity3]);
```

**Solution 2: Combine Meshes**
```javascript
// Merge multiple meshes into one
// In 3D software before import, or use:

const combinedMesh = new pc.Mesh(app.graphicsDevice);
// ... combine vertex data ...
```

**Solution 3: Use Instancing**
```javascript
// For repeated objects (trees, rocks, etc.)
const mesh = entity.model.meshInstances[0];
mesh.instancingData = {
  count: 100,
  transforms: transformMatrices  // Array of Mat4
};
```

---

### 2. LOD (Level of Detail)

Reduce geometry for distant objects.

```javascript
// Manual LOD switching
const LOD_DISTANCES = [10, 50, 100];
const LOD_MODELS = [highResModel, mediumResModel, lowResModel];

app.on('update', () => {
  const distance = camera.getPosition().distance(entity.getPosition());

  let lodLevel = 0;
  for (let i = 0; i < LOD_DISTANCES.length; i++) {
    if (distance > LOD_DISTANCES[i]) {
      lodLevel = i + 1;
    }
  }

  entity.model.asset = LOD_MODELS[lodLevel];
});
```

**Better: Use Model Component LOD**
```javascript
entity.model.meshInstances[0].lodLevel = 0;  // High detail
// Automatically switches based on screen size
```

---

### 3. Frustum Culling

Don't render off-screen objects (automatic in PlayCanvas).

**Verify it's enabled**:
```javascript
camera.camera.frustumCulling = true;  // Should be true by default
```

**Manual Culling**:
```javascript
// Disable entities outside camera frustum
app.on('update', () => {
  entities.forEach(entity => {
    const inFrustum = camera.camera.frustum.containsPoint(entity.getPosition());
    entity.enabled = inFrustum;
  });
});
```

---

### 4. Occlusion Culling

Don't render objects blocked by other objects.

```javascript
// Not built-in, manual implementation:
function isOccluded(entity, camera) {
  const from = camera.getPosition();
  const to = entity.getPosition();

  const result = app.systems.rigidbody.raycastFirst(from, to);

  return result && result.entity !== entity;
}

app.on('update', () => {
  entities.forEach(entity => {
    entity.enabled = !isOccluded(entity, camera);
  });
});
```

---

### 5. Reduce Triangle Count

**Guidelines**:
- Characters: 5k-15k triangles
- Props: 500-2k triangles
- Environment: Use LOD

**Tools**:
- Blender: Decimate modifier
- Editor: Import at lower resolution

**Check Triangle Count**:
```javascript
console.log('Triangles:', app.stats.triangles.total);
```

---

### 6. Optimize Materials

**Avoid**:
- Too many unique materials (each = draw call)
- Complex shaders
- Unnecessary texture maps

**Do**:
- Reuse materials across objects
- Use material instances
- Disable unused features

```javascript
// Create material instance
const material = new pc.StandardMaterial();
material.diffuse = new pc.Color(1, 0, 0);
material.update();

// Reuse across entities
entity1.model.material = material;
entity2.model.material = material;
entity3.model.material = material;
// Still 3 draw calls, but same material
```

**Disable Unused Maps**:
```javascript
const material = new pc.StandardMaterial();
material.diffuse = new pc.Color(1, 0, 0);
// Don't set diffuseMap, normalMap, etc. if not needed
material.update();
```

---

### 7. Shadow Optimization

Shadows are expensive.

**Reduce Shadow Casters**:
```javascript
// Only important objects cast shadows
importantEntity.model.castShadows = true;
insignificantEntity.model.castShadows = false;
```

**Shadow Quality Settings**:
```javascript
light.light.shadowDistance = 40;      // Lower = better perf
light.light.shadowResolution = 1024;  // Lower = better perf (default 2048)
light.light.shadowType = pc.SHADOW_PCF3;  // PCF3 faster than PCF5
```

**Disable Shadows on Mobile**:
```javascript
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

if (isMobile) {
  app.root.findByTag('light').forEach(entity => {
    entity.light.castShadows = false;
  });
}
```

---

## Asset Optimization

### 1. Texture Compression

**Problem**: Uncompressed textures use lots of memory.

**Solution**: Use compressed formats.

```javascript
// In Editor: Select texture → Inspector → Compression

// Recommended:
// Desktop: DXT (BC1-BC7)
// iOS: PVRTC or ASTC
// Android: ETC2 or ASTC
// Universal: Basis Universal
```

**Texture Size Guidelines**:
- **UI**: 512x512 max
- **Props**: 1024x1024
- **Characters**: 2048x2048
- **Terrain**: 4096x4096 (with tiling)

**Power-of-2 Sizes**: Always use 256, 512, 1024, 2048, 4096

---

### 2. Model Optimization

**Before Import**:
- Remove non-visible geometry
- Merge vertices
- Triangulate meshes
- Bake transforms

**Vertex Count**:
- **Low**: < 5k vertices
- **Medium**: 5k-20k vertices
- **High**: 20k-50k vertices
- **Very High**: > 50k (use LOD)

**File Formats**:
- **Best**: `.glb` (binary glTF, compressed)
- **Good**: `.gltf` (text glTF)
- **Avoid**: `.fbx`, `.obj` (not optimized for web)

---

### 3. Audio Optimization

**Format**:
- **Desktop**: `.mp3` or `.ogg`
- **Mobile**: `.mp3` (better compatibility)

**Compression**:
- Music: 128 kbps
- SFX: 64 kbps

**Loading**:
```javascript
// Preload critical sounds
sound.sound.play('sfx', {
  volume: 0  // Silent preload
});

// Lazy load music
if (inMenuScene) {
  loadMusicAsset();
}
```

---

### 4. Texture Atlases

Combine multiple textures into one.

**Manual Atlas**:
```javascript
// Instead of:
// texture1.png, texture2.png, texture3.png

// Use:
// atlas.png (contains all three)

// Update UVs to reference correct portion
```

**Benefits**:
- Fewer texture bindings
- Reduced draw calls
- Better batching

---

## Memory Management

### 1. Asset Cleanup

**Problem**: Loaded assets stay in memory forever.

**Solution**: Unload when not needed.

```javascript
// Load asset
const asset = new pc.Asset('model', 'container', { url: '/model.glb' });
app.assets.add(asset);
app.assets.load(asset);

// Later, when done:
app.assets.remove(asset);
asset.unload();
```

**Scene Transition**:
```javascript
function loadScene(sceneName) {
  // Clean up current scene assets
  const oldAssets = currentSceneAssets;
  oldAssets.forEach(asset => {
    app.assets.remove(asset);
    asset.unload();
  });

  // Load new scene
  const sceneAsset = new pc.Asset(sceneName, 'scene', { url: `/${sceneName}.json` });
  app.assets.add(sceneAsset);
  app.assets.load(sceneAsset);

  currentSceneAssets = [sceneAsset];
}
```

---

### 2. Entity Pooling

Reuse entities instead of creating/destroying.

```javascript
class EntityPool {
  constructor(app, template, count) {
    this.app = app;
    this.pool = [];
    this.active = [];

    for (let i = 0; i < count; i++) {
      const entity = template.clone();
      entity.enabled = false;
      app.root.addChild(entity);
      this.pool.push(entity);
    }
  }

  spawn(position) {
    let entity = this.pool.pop();

    if (!entity) {
      console.warn('Pool exhausted, consider increasing size');
      return null;
    }

    entity.enabled = true;
    entity.setPosition(position);
    this.active.push(entity);

    return entity;
  }

  despawn(entity) {
    entity.enabled = false;

    const index = this.active.indexOf(entity);
    if (index > -1) {
      this.active.splice(index, 1);
      this.pool.push(entity);
    }
  }

  reset() {
    this.active.forEach(entity => this.despawn(entity));
  }
}

// Usage
const bulletTemplate = new pc.Entity('bullet');
bulletTemplate.addComponent('model', { type: 'sphere' });
bulletTemplate.addComponent('rigidbody', { type: pc.BODYTYPE_DYNAMIC });

const bulletPool = new EntityPool(app, bulletTemplate, 100);

// Spawn bullet
const bullet = bulletPool.spawn(new pc.Vec3(0, 0, 0));

// Later, despawn
bulletPool.despawn(bullet);
```

---

### 3. Texture Memory

**Monitor Texture Memory**:
```javascript
console.log('Texture VRAM:', app.stats.vram.tex / 1024 / 1024, 'MB');
```

**Targets**:
- **Desktop**: < 500 MB
- **Mobile**: < 200 MB

**Optimization**:
- Use mipmaps
- Enable texture compression
- Reduce texture sizes
- Unload unused textures

---

### 4. Garbage Collection

Minimize object creation in update loop.

```javascript
// ❌ Bad - creates new object every frame
app.on('update', (dt) => {
  const forward = new pc.Vec3(0, 0, -1);  // GC pressure!
  entity.translate(forward.mulScalar(speed * dt));
});

// ✅ Good - reuse objects
const forward = new pc.Vec3(0, 0, -1);  // Created once

app.on('update', (dt) => {
  const movement = forward.clone().mulScalar(speed * dt);
  entity.translate(movement);
});

// ✅ Better - pre-allocate
const forward = new pc.Vec3(0, 0, -1);
const movement = new pc.Vec3();

app.on('update', (dt) => {
  movement.copy(forward).mulScalar(speed * dt);
  entity.translate(movement);
});
```

---

## Script Optimization

### 1. Reduce Update Frequency

Not everything needs to update every frame.

```javascript
var MyScript = pc.createScript('myScript');

MyScript.prototype.initialize = function() {
  this.updateTimer = 0;
  this.updateInterval = 0.1;  // Update every 100ms instead of every frame
};

MyScript.prototype.update = function(dt) {
  this.updateTimer += dt;

  if (this.updateTimer >= this.updateInterval) {
    this.updateTimer = 0;
    this.expensiveUpdate();
  }
};

MyScript.prototype.expensiveUpdate = function() {
  // Heavy computation here
};
```

---

### 2. Event-Based Instead of Polling

```javascript
// ❌ Bad - checks every frame
app.on('update', () => {
  if (player.health <= 0) {
    gameOver();
  }
});

// ✅ Good - event-based
player.on('health:changed', (health) => {
  if (health <= 0) {
    gameOver();
  }
});
```

---

### 3. Cache Expensive Lookups

```javascript
// ❌ Bad - searches scene graph every frame
app.on('update', (dt) => {
  const player = app.root.findByName('Player');
  player.translate(0, 0, -speed * dt);
});

// ✅ Good - cache reference
const player = app.root.findByName('Player');

app.on('update', (dt) => {
  player.translate(0, 0, -speed * dt);
});
```

---

### 4. Avoid String Concatenation

```javascript
// ❌ Slower
const id = 'entity_' + index;

// ✅ Faster
const id = `entity_${index}`;

// ✅ Even faster - use numbers when possible
const id = index;
```

---

### 5. Use Object Pooling for Vectors

```javascript
// Vector pool
const VectorPool = {
  pool: [],

  get() {
    return this.pool.length > 0 ? this.pool.pop() : new pc.Vec3();
  },

  release(vec) {
    vec.set(0, 0, 0);
    this.pool.push(vec);
  }
};

// Usage
app.on('update', (dt) => {
  const direction = VectorPool.get();
  direction.set(0, 0, -1).mulScalar(speed * dt);
  entity.translate(direction);
  VectorPool.release(direction);
});
```

---

## Mobile Optimization

### 1. Detect Mobile

```javascript
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
const isLowEnd = navigator.hardwareConcurrency <= 4;
```

---

### 2. Quality Settings

```javascript
if (isMobile) {
  // Reduce shadow quality
  app.root.findByTag('light').forEach(entity => {
    entity.light.castShadows = false;
  });

  // Reduce resolution
  app.graphicsDevice.maxPixelRatio = 1;

  // Disable post-processing
  camera.camera.disablePostProcessing = true;

  // Reduce texture quality
  app.assets.findAll('texture').forEach(asset => {
    asset.resource.minFilter = pc.FILTER_NEAREST;
  });
}
```

---

### 3. Mobile-Specific Textures

```javascript
function loadTexture(basePath, isMobile) {
  const size = isMobile ? '512' : '2048';
  const url = `${basePath}_${size}.jpg`;

  const asset = new pc.Asset('texture', 'texture', { url });
  app.assets.add(asset);
  app.assets.load(asset);

  return asset;
}

const texture = loadTexture('/textures/character', isMobile);
```

---

### 4. Touch Optimization

```javascript
// Throttle touch events
let lastTouch = 0;
const throttleMs = 16;  // ~60fps

app.touch.on(pc.EVENT_TOUCHMOVE, (event) => {
  const now = Date.now();
  if (now - lastTouch < throttleMs) return;

  lastTouch = now;
  handleTouch(event);
});
```

---

## Network & Loading

### 1. Asset Loading Strategy

**Preload Critical Assets**:
```javascript
const criticalAssets = [
  playerModel,
  playerTexture,
  uiFont
];

let loaded = 0;

criticalAssets.forEach(asset => {
  asset.ready(() => {
    loaded++;
    if (loaded === criticalAssets.length) {
      startGame();
    }
  });

  app.assets.load(asset);
});
```

**Lazy Load Optional Assets**:
```javascript
// Load music only when needed
function playMusic() {
  if (!musicAsset.loaded) {
    musicAsset.ready(() => {
      entity.sound.play('music');
    });
    app.assets.load(musicAsset);
  } else {
    entity.sound.play('music');
  }
}
```

---

### 2. Progressive Loading

```javascript
// Load in stages
async function loadGame() {
  // Stage 1: UI
  await loadAssets(uiAssets);
  showMainMenu();

  // Stage 2: Player
  await loadAssets(playerAssets);

  // Stage 3: Environment
  await loadAssets(environmentAssets);

  // Stage 4: Enemies (background)
  loadAssets(enemyAssets);  // Don't wait

  enableStartButton();
}
```

---

### 3. Asset Compression

**Enable gzip on server**:
```javascript
// .htaccess (Apache)
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE application/json
  AddOutputFilterByType DEFLATE application/javascript
  AddOutputFilterByType DEFLATE text/css
</IfModule>
```

**Use CDN**:
- Faster asset delivery
- Reduced server load
- Geographic distribution

---

### 4. Loading Screen

```javascript
let loadedAssets = 0;
const totalAssets = assets.length;

assets.forEach(asset => {
  asset.on('load', () => {
    loadedAssets++;
    const progress = loadedAssets / totalAssets;
    updateLoadingBar(progress);
  });

  app.assets.load(asset);
});

function updateLoadingBar(progress) {
  document.getElementById('progress-bar').style.width = `${progress * 100}%`;
  document.getElementById('progress-text').textContent = `${Math.round(progress * 100)}%`;
}
```

---

## Performance Checklist

### Before Launch

- [ ] **Draw calls < 100** (check profiler)
- [ ] **FPS ≥ 60** on target devices
- [ ] **Texture memory < 500MB** desktop, < 200MB mobile
- [ ] **All textures compressed** (Basis/DXT/ETC)
- [ ] **All textures power-of-2** sizes
- [ ] **Triangle count reasonable** for target (< 100k total)
- [ ] **Shadows optimized** (low resolution, distance limit)
- [ ] **LOD implemented** for complex models
- [ ] **Entity pooling** for frequently spawned objects
- [ ] **Assets cleaned up** on scene transitions
- [ ] **Loading screen** implemented
- [ ] **Mobile testing** complete
- [ ] **Network optimization** (gzip, CDN)
- [ ] **No memory leaks** (test long sessions)

---

## Debugging Performance Issues

### Identify Bottleneck

**Step 1: Check FPS**
```javascript
console.log('FPS:', Math.round(1 / app.stats.frame.updateTime * 1000));
```

**Step 2: Check Draw Calls**
```javascript
console.log('Draw calls:', app.stats.drawCalls.total);
```
- If > 200: Reduce meshes, enable batching

**Step 3: Check Triangles**
```javascript
console.log('Triangles:', app.stats.triangles.total);
```
- If > 500k: Reduce geometry, use LOD

**Step 4: Check Texture Memory**
```javascript
console.log('Texture VRAM:', app.stats.vram.tex / 1024 / 1024, 'MB');
```
- If > 500MB: Compress textures, reduce sizes

**Step 5: Profile Scripts**
```javascript
console.profile('update');
app.on('update', (dt) => {
  // Game logic
});
console.profileEnd('update');
```
- Check DevTools Performance tab

---

## Resources

- **Optimization Tutorial**: https://developer.playcanvas.com/en/tutorials/optimization/
- **Best Practices**: https://developer.playcanvas.com/en/user-manual/optimization/
- **Profiling Guide**: https://developer.playcanvas.com/en/user-manual/optimization/profiling/

---

## Quick Wins

**5-Minute Optimizations**:

1. **Enable texture compression** (Basis Universal)
2. **Disable shadows on mobile**
3. **Reduce shadow resolution** to 1024
4. **Enable frustum culling**
5. **Cache entity lookups**
6. **Use entity pooling** for bullets/particles
7. **Compress textures** to power-of-2 sizes
8. **Batch static geometry**
9. **Disable invisible entities**
10. **Throttle expensive update calls**

---

This guide covers all major optimization strategies. Apply these techniques to achieve 60 FPS on your target platform.



===== FILE: plugins/individual/playcanvas-engine/agents/playcanvas-engine-architect.md =====

# PlayCanvas Architect

## Role

Expert 3D/graphics architect specializing in PlayCanvas scene design, optimization, and best practices.

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
3. Implement best practices from PlayCanvas ecosystem
4. Optimize for target platforms and devices
5. Provide detailed implementation guidance

## Tools

This agent has access to:
- PlayCanvas skill knowledge
- Optimization checklists and patterns
- Performance profiling guidance
- Asset pipeline recommendations



===== FILE: plugins/individual/playcanvas-engine/commands/component_builder.md =====

# /playcanvas-engine-component_builder

PlayCanvas - Component Builder

## Description

Executes the component_builder script for PlayCanvas.

## Usage

```bash
/playcanvas-engine-component_builder
```

## Implementation

This command runs the `component_builder.py` script from the PlayCanvas skill, which provides automated assistance for component builder.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/playcanvas-engine/commands/project_generator.md =====

# /playcanvas-engine-project_generator

PlayCanvas - Project Generator

## Description

Executes the project_generator script for PlayCanvas.

## Usage

```bash
/playcanvas-engine-project_generator
```

## Implementation

This command runs the `project_generator.py` script from the PlayCanvas skill, which provides automated assistance for project generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/assets/starter_playcanvas/scripts/app.js =====

```js
/**
 * PlayCanvas Starter Project
 * Main application initialization and scene setup
 */

let app;
let cameraController;
let inputManager;
let statsEnabled = true;
let wireframeEnabled = false;

/**
 * Initialize PlayCanvas application
 */
function initApp() {
    const canvas = document.getElementById('application-canvas');

    // Create PlayCanvas application
    app = new pc.Application(canvas, {
        mouse: new pc.Mouse(canvas),
        touch: new pc.TouchDevice(canvas),
        keyboard: new pc.Keyboard(window),
        graphicsDeviceOptions: {
            antialias: true,
            alpha: false
        }
    });

    // Configure application
    app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
    app.setCanvasResolution(pc.RESOLUTION_AUTO);

    // Start application
    app.start();

    // Setup scene
    setupScene();

    // Initialize managers
    inputManager = new InputManager(app);
    cameraController = new CameraController(app, app.root.findByName('Camera'));

    // Setup UI controls
    setupUI();

    // Update loop
    app.on('update', update);

    // Hide loading screen
    setTimeout(() => {
        document.getElementById('loading-screen').classList.add('hidden');
    }, 500);

    // Handle window resize
    window.addEventListener('resize', () => {
        app.resizeCanvas();
    });

    console.log('PlayCanvas application initialized');
}

/**
 * Setup scene with camera, lights, and objects
 */
function setupScene() {
    // Camera
    const camera = new pc.Entity('Camera');
    camera.addComponent('camera', {
        clearColor: new pc.Color(0.1, 0.1, 0.15),
        farClip: 100
    });
    camera.setPosition(0, 5, 10);
    camera.lookAt(0, 0, 0);
    app.root.addChild(camera);

    // Directional Light (Sun)
    const light = new pc.Entity('DirectionalLight');
    light.addComponent('light', {
        type: 'directional',
        color: new pc.Color(1, 1, 1),
        intensity: 1,
        castShadows: true,
        shadowBias: 0.2,
        shadowDistance: 40,
        normalOffsetBias: 0.05
    });
    light.setEulerAngles(45, 30, 0);
    app.root.addChild(light);

    // Ambient Light
    const ambient = new pc.Entity('AmbientLight');
    ambient.addComponent('light', {
        type: 'directional',
        color: new pc.Color(0.4, 0.5, 0.6),
        intensity: 0.3
    });
    ambient.setEulerAngles(-45, 0, 0);
    app.root.addChild(ambient);

    // Ground Plane
    const ground = new pc.Entity('Ground');
    ground.addComponent('model', {
        type: 'plane'
    });
    ground.setLocalScale(20, 1, 20);

    // Ground material
    const groundMaterial = new pc.StandardMaterial();
    groundMaterial.diffuse = new pc.Color(0.3, 0.3, 0.35);
    groundMaterial.metalness = 0.0;
    groundMaterial.gloss = 0.3;
    groundMaterial.update();
    ground.model.material = groundMaterial;

    app.root.addChild(ground);

    // Create demo objects
    createDemoObjects();
}

/**
 * Create demo objects in the scene
 */
function createDemoObjects() {
    const colors = [
        new pc.Color(0.8, 0.3, 0.3),  // Red
        new pc.Color(0.3, 0.8, 0.3),  // Green
        new pc.Color(0.3, 0.3, 0.8),  // Blue
        new pc.Color(0.8, 0.8, 0.3),  // Yellow
        new pc.Color(0.8, 0.3, 0.8)   // Magenta
    ];

    const shapes = ['box', 'sphere', 'cylinder', 'cone', 'capsule'];

    for (let i = 0; i < 5; i++) {
        const entity = new pc.Entity(`Shape_${i}`);

        // Add model component
        entity.addComponent('model', {
            type: shapes[i]
        });

        // Position in a circle
        const angle = (i / 5) * Math.PI * 2;
        const radius = 4;
        entity.setPosition(
            Math.cos(angle) * radius,
            1,
            Math.sin(angle) * radius
        );

        // Create material
        const material = new pc.StandardMaterial();
        material.diffuse = colors[i];
        material.metalness = 0.2 + (i * 0.15);
        material.gloss = 0.7;
        material.update();
        entity.model.material = material;

        // Store rotation speed
        entity.rotationSpeed = new pc.Vec3(
            10 + i * 5,
            20 + i * 5,
            15 + i * 5
        );

        app.root.addChild(entity);
    }
}

/**
 * Main update loop
 */
function update(dt) {
    // Update camera controller
    if (cameraController) {
        cameraController.update(dt);
    }

    // Rotate demo objects
    const shapes = app.root.find((node) => node.name.startsWith('Shape_'));
    shapes.forEach((shape) => {
        if (shape.rotationSpeed) {
            shape.rotate(
                shape.rotationSpeed.x * dt,
                shape.rotationSpeed.y * dt,
                shape.rotationSpeed.z * dt
            );
        }
    });

    // Update stats
    if (statsEnabled) {
        updateStats();
    }
}

/**
 * Update performance stats display
 */
function updateStats() {
    const stats = app.stats;

    document.getElementById('fps').textContent = Math.round(1 / app.dt);
    document.getElementById('draw-calls').textContent = stats.drawCalls.total;
    document.getElementById('triangles').textContent = Math.round(stats.misc.tricount / 1000) + 'k';
}

/**
 * Setup UI controls
 */
function setupUI() {
    // Toggle stats
    document.getElementById('toggle-stats').addEventListener('click', () => {
        statsEnabled = !statsEnabled;
        document.getElementById('stats-panel').classList.toggle('hidden');
    });

    // Toggle wireframe
    document.getElementById('toggle-wireframe').addEventListener('click', () => {
        wireframeEnabled = !wireframeEnabled;

        // Update all materials
        const entities = app.root.find((node) => node.model);
        entities.forEach((entity) => {
            if (entity.model && entity.model.material) {
                // Create new material instance if needed
                if (!entity.model.material.wireframe) {
                    const material = entity.model.material;
                    material.update();
                }
            }
        });

        // Note: Wireframe rendering requires custom shader in PlayCanvas
        console.log('Wireframe mode:', wireframeEnabled);
    });

    // Reset camera
    document.getElementById('reset-camera').addEventListener('click', () => {
        if (cameraController) {
            cameraController.reset();
        }
    });
}

/**
 * Cleanup resources
 */
function cleanup() {
    if (app) {
        app.destroy();
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', cleanup);

```


===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/assets/starter_playcanvas/scripts/camera-controller.js =====

```js
/**
 * Camera Controller
 * Orbit camera with mouse/touch controls
 */

class CameraController {
    constructor(app, cameraEntity, options = {}) {
        this.app = app;
        this.camera = cameraEntity;

        // Configuration
        this.target = options.target || new pc.Vec3(0, 0, 0);
        this.distance = options.distance || 10;
        this.minDistance = options.minDistance || 2;
        this.maxDistance = options.maxDistance || 50;
        this.sensitivity = options.sensitivity || 0.3;
        this.damping = options.damping || 0.15;
        this.zoomSpeed = options.zoomSpeed || 0.5;

        // State
        this.yaw = options.initialYaw || 0;
        this.pitch = options.initialPitch || 20;
        this.targetYaw = this.yaw;
        this.targetPitch = this.pitch;
        this.currentDistance = this.distance;
        this.targetDistance = this.distance;

        // Input tracking
        this.isDragging = false;
        this.lastMouseX = 0;
        this.lastMouseY = 0;

        // Touch tracking
        this.lastTouchDistance = 0;

        // Initial camera position
        this.initialYaw = this.yaw;
        this.initialPitch = this.pitch;
        this.initialDistance = this.distance;

        this.init();
    }

    init() {
        const canvas = this.app.graphicsDevice.canvas;

        // Mouse events
        if (this.app.mouse) {
            canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
            canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
            canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
            canvas.addEventListener('wheel', this.onMouseWheel.bind(this));
        }

        // Touch events
        if (this.app.touch) {
            canvas.addEventListener('touchstart', this.onTouchStart.bind(this));
            canvas.addEventListener('touchmove', this.onTouchMove.bind(this));
            canvas.addEventListener('touchend', this.onTouchEnd.bind(this));
        }

        // Prevent context menu on right-click
        canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    }

    // Mouse Events
    onMouseDown(event) {
        if (event.button === 0 || event.button === 2) { // Left or right button
            this.isDragging = true;
            this.lastMouseX = event.clientX;
            this.lastMouseY = event.clientY;
        }
    }

    onMouseMove(event) {
        if (this.isDragging) {
            const deltaX = event.clientX - this.lastMouseX;
            const deltaY = event.clientY - this.lastMouseY;

            this.targetYaw -= deltaX * this.sensitivity;
            this.targetPitch -= deltaY * this.sensitivity;

            // Clamp pitch
            this.targetPitch = Math.max(-89, Math.min(89, this.targetPitch));

            this.lastMouseX = event.clientX;
            this.lastMouseY = event.clientY;
        }
    }

    onMouseUp(event) {
        if (event.button === 0 || event.button === 2) {
            this.isDragging = false;
        }
    }

    onMouseWheel(event) {
        event.preventDefault();

        const delta = event.deltaY > 0 ? 1 : -1;
        this.targetDistance += delta * this.zoomSpeed;
        this.targetDistance = Math.max(
            this.minDistance,
            Math.min(this.maxDistance, this.targetDistance)
        );
    }

    // Touch Events
    onTouchStart(event) {
        if (event.touches.length === 1) {
            // Single touch - rotate
            this.isDragging = true;
            this.lastMouseX = event.touches[0].clientX;
            this.lastMouseY = event.touches[0].clientY;
        } else if (event.touches.length === 2) {
            // Two finger touch - zoom
            this.lastTouchDistance = this.getTouchDistance(event.touches);
        }
    }

    onTouchMove(event) {
        event.preventDefault();

        if (event.touches.length === 1 && this.isDragging) {
            // Single touch - rotate
            const deltaX = event.touches[0].clientX - this.lastMouseX;
            const deltaY = event.touches[0].clientY - this.lastMouseY;

            this.targetYaw -= deltaX * this.sensitivity;
            this.targetPitch -= deltaY * this.sensitivity;

            this.targetPitch = Math.max(-89, Math.min(89, this.targetPitch));

            this.lastMouseX = event.touches[0].clientX;
            this.lastMouseY = event.touches[0].clientY;
        } else if (event.touches.length === 2) {
            // Two finger touch - zoom
            const distance = this.getTouchDistance(event.touches);
            const delta = this.lastTouchDistance - distance;

            this.targetDistance += delta * 0.01;
            this.targetDistance = Math.max(
                this.minDistance,
                Math.min(this.maxDistance, this.targetDistance)
            );

            this.lastTouchDistance = distance;
        }
    }

    onTouchEnd(event) {
        if (event.touches.length === 0) {
            this.isDragging = false;
        } else if (event.touches.length === 2) {
            this.lastTouchDistance = this.getTouchDistance(event.touches);
        }
    }

    getTouchDistance(touches) {
        const dx = touches[0].clientX - touches[1].clientX;
        const dy = touches[0].clientY - touches[1].clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    // Update Loop
    update(dt) {
        if (!this.camera) return;

        // Smooth damping
        this.yaw += (this.targetYaw - this.yaw) * this.damping;
        this.pitch += (this.targetPitch - this.pitch) * this.damping;
        this.currentDistance += (this.targetDistance - this.currentDistance) * this.damping;

        // Calculate camera position
        const yawRad = this.yaw * pc.math.DEG_TO_RAD;
        const pitchRad = this.pitch * pc.math.DEG_TO_RAD;

        const x = this.target.x + this.currentDistance * Math.cos(pitchRad) * Math.sin(yawRad);
        const y = this.target.y + this.currentDistance * Math.sin(pitchRad);
        const z = this.target.z + this.currentDistance * Math.cos(pitchRad) * Math.cos(yawRad);

        this.camera.setPosition(x, y, z);
        this.camera.lookAt(this.target);
    }

    // Control Methods
    setTarget(target) {
        if (target instanceof pc.Vec3) {
            this.target.copy(target);
        } else if (target instanceof pc.Entity) {
            this.target.copy(target.getPosition());
        }
    }

    setDistance(distance) {
        this.targetDistance = Math.max(
            this.minDistance,
            Math.min(this.maxDistance, distance)
        );
    }

    setYaw(yaw) {
        this.targetYaw = yaw;
    }

    setPitch(pitch) {
        this.targetPitch = Math.max(-89, Math.min(89, pitch));
    }

    reset() {
        this.targetYaw = this.initialYaw;
        this.targetPitch = this.initialPitch;
        this.targetDistance = this.initialDistance;
    }

    focusOn(entity, distance = null) {
        if (entity instanceof pc.Entity) {
            this.setTarget(entity.getPosition());
        } else if (entity instanceof pc.Vec3) {
            this.setTarget(entity);
        }

        if (distance !== null) {
            this.setDistance(distance);
        }
    }

    // Animation
    animateTo(yaw, pitch, distance, duration = 1.0) {
        // Simple tween implementation
        const startYaw = this.yaw;
        const startPitch = this.pitch;
        const startDistance = this.currentDistance;

        const startTime = Date.now();

        const animate = () => {
            const elapsed = (Date.now() - startTime) / 1000;
            const t = Math.min(elapsed / duration, 1);

            // Ease out cubic
            const eased = 1 - Math.pow(1 - t, 3);

            this.targetYaw = startYaw + (yaw - startYaw) * eased;
            this.targetPitch = startPitch + (pitch - startPitch) * eased;
            this.targetDistance = startDistance + (distance - startDistance) * eased;

            if (t < 1) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    }

    // Utility
    getForwardVector() {
        return this.camera.forward.clone();
    }

    getRightVector() {
        return this.camera.right.clone();
    }

    getUpVector() {
        return this.camera.up.clone();
    }

    // Cleanup
    destroy() {
        // Remove event listeners if needed
        this.camera = null;
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CameraController;
}

```


===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/assets/starter_playcanvas/scripts/input-manager.js =====

```js
/**
 * Input Manager
 * Centralized input handling for keyboard, mouse, and touch
 */

class InputManager {
    constructor(app) {
        this.app = app;
        this.keyboard = app.keyboard;
        this.mouse = app.mouse;
        this.touch = app.touch;

        // Input state
        this.keys = {};
        this.mouseButtons = {};
        this.mousePosition = new pc.Vec2();
        this.mouseDelta = new pc.Vec2();
        this.mouseWheel = 0;

        // Touch state
        this.touches = [];
        this.touchCount = 0;

        this.init();
    }

    init() {
        // Keyboard events
        if (this.keyboard) {
            this.keyboard.on(pc.EVENT_KEYDOWN, this.onKeyDown.bind(this));
            this.keyboard.on(pc.EVENT_KEYUP, this.onKeyUp.bind(this));
        }

        // Mouse events
        if (this.mouse) {
            this.mouse.on(pc.EVENT_MOUSEDOWN, this.onMouseDown.bind(this));
            this.mouse.on(pc.EVENT_MOUSEUP, this.onMouseUp.bind(this));
            this.mouse.on(pc.EVENT_MOUSEMOVE, this.onMouseMove.bind(this));
            this.mouse.on(pc.EVENT_MOUSEWHEEL, this.onMouseWheel.bind(this));
        }

        // Touch events
        if (this.touch) {
            this.touch.on(pc.EVENT_TOUCHSTART, this.onTouchStart.bind(this));
            this.touch.on(pc.EVENT_TOUCHEND, this.onTouchEnd.bind(this));
            this.touch.on(pc.EVENT_TOUCHMOVE, this.onTouchMove.bind(this));
            this.touch.on(pc.EVENT_TOUCHCANCEL, this.onTouchCancel.bind(this));
        }
    }

    // Keyboard Methods
    onKeyDown(event) {
        this.keys[event.key] = true;
    }

    onKeyUp(event) {
        this.keys[event.key] = false;
    }

    isKeyPressed(key) {
        return this.keys[key] === true;
    }

    wasKeyPressed(key) {
        if (this.keyboard) {
            return this.keyboard.wasPressed(key);
        }
        return false;
    }

    wasKeyReleased(key) {
        if (this.keyboard) {
            return this.keyboard.wasReleased(key);
        }
        return false;
    }

    // Mouse Methods
    onMouseDown(event) {
        this.mouseButtons[event.button] = true;
    }

    onMouseUp(event) {
        this.mouseButtons[event.button] = false;
    }

    onMouseMove(event) {
        this.mousePosition.set(event.x, event.y);
        this.mouseDelta.set(event.dx, event.dy);
    }

    onMouseWheel(event) {
        this.mouseWheel = event.wheel;
    }

    isMouseButtonPressed(button) {
        return this.mouseButtons[button] === true;
    }

    getMousePosition() {
        if (this.mouse) {
            return new pc.Vec2(this.mouse.x, this.mouse.y);
        }
        return this.mousePosition.clone();
    }

    getMouseDelta() {
        return this.mouseDelta.clone();
    }

    getMouseWheel() {
        return this.mouseWheel;
    }

    // Touch Methods
    onTouchStart(event) {
        this.updateTouches(event);
    }

    onTouchEnd(event) {
        this.updateTouches(event);
    }

    onTouchMove(event) {
        this.updateTouches(event);
    }

    onTouchCancel(event) {
        this.touches = [];
        this.touchCount = 0;
    }

    updateTouches(event) {
        if (!this.touch) return;

        this.touches = [];
        this.touchCount = event.touches.length;

        for (let i = 0; i < event.touches.length; i++) {
            const touch = event.touches[i];
            this.touches.push({
                id: touch.id,
                x: touch.x,
                y: touch.y,
                dx: touch.dx || 0,
                dy: touch.dy || 0
            });
        }
    }

    getTouchCount() {
        return this.touchCount;
    }

    getTouch(index) {
        if (index >= 0 && index < this.touches.length) {
            return this.touches[index];
        }
        return null;
    }

    getTouches() {
        return this.touches;
    }

    // Utility Methods
    getInputVector(upKey, downKey, leftKey, rightKey) {
        const vector = new pc.Vec2(0, 0);

        if (this.isKeyPressed(upKey)) vector.y += 1;
        if (this.isKeyPressed(downKey)) vector.y -= 1;
        if (this.isKeyPressed(leftKey)) vector.x -= 1;
        if (this.isKeyPressed(rightKey)) vector.x += 1;

        // Normalize diagonal movement
        if (vector.length() > 0) {
            vector.normalize();
        }

        return vector;
    }

    getWASDInput() {
        return this.getInputVector(
            pc.KEY_W,
            pc.KEY_S,
            pc.KEY_A,
            pc.KEY_D
        );
    }

    getArrowKeysInput() {
        return this.getInputVector(
            pc.KEY_UP,
            pc.KEY_DOWN,
            pc.KEY_LEFT,
            pc.KEY_RIGHT
        );
    }

    // Raycast from screen position
    screenToWorldRay(screenX, screenY, camera) {
        if (!camera || !camera.camera) return null;

        const worldPos = camera.camera.screenToWorld(
            screenX,
            screenY,
            camera.camera.farClip
        );

        return {
            origin: camera.getPosition(),
            direction: worldPos.clone().sub(camera.getPosition()).normalize(),
            end: worldPos
        };
    }

    // Get raycast from mouse
    getMouseRay(camera) {
        if (!this.mouse || !camera) return null;

        return this.screenToWorldRay(
            this.mouse.x,
            this.mouse.y,
            camera
        );
    }

    // Perform raycast
    raycast(from, to) {
        return this.app.systems.rigidbody.raycastFirst(from, to);
    }

    raycastAll(from, to) {
        return this.app.systems.rigidbody.raycastAll(from, to);
    }

    // Cleanup
    destroy() {
        this.keys = {};
        this.mouseButtons = {};
        this.touches = [];
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InputManager;
}

```


===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/scripts/component_builder.py =====

```py
#!/usr/bin/env python3
"""
PlayCanvas Component Builder
Generates PlayCanvas script components with lifecycle methods and attributes.

Usage:
    Interactive mode:
        python component_builder.py

    CLI mode:
        python component_builder.py --name MyComponent --type basic --output ./
        python component_builder.py -n PlayerController -t character -o ./scripts/
        python component_builder.py -n CameraOrbit -t camera --attributes
"""

import argparse
import os
import sys
from typing import Dict, Tuple, List


# Component templates
def generate_basic_component(name: str, include_attributes: bool = True) -> str:
    """Generate a basic PlayCanvas script component"""
    class_name = name[0].upper() + name[1:]
    script_name = name[0].lower() + name[1:]

    attributes = ""
    if include_attributes:
        attributes = f"""
// Attributes (editable in Editor)
{class_name}.attributes.add('enabled', {{
    type: 'boolean',
    default: true,
    title: 'Enabled'
}});

{class_name}.attributes.add('speed', {{
    type: 'number',
    default: 1.0,
    title: 'Speed',
    description: 'Component speed multiplier'
}});
"""

    return f"""/**
 * {class_name} Component
 * Basic PlayCanvas script component template
 *
 * Usage:
 * 1. Attach to entity via Editor or code
 * 2. Configure attributes in Inspector
 * 3. Access via: entity.script.{script_name}
 */

var {class_name} = pc.createScript('{script_name}');
{attributes}
/**
 * Initialize component
 * Called once when script is enabled
 */
{class_name}.prototype.initialize = function() {{
    console.log('{class_name} initialized');

    // Store references
    this.entity.script.{script_name}.active = true;
}};

/**
 * Update method called every frame
 * @param {{number}} dt - Delta time in seconds
 */
{class_name}.prototype.update = function(dt) {{
    if (!this.enabled) return;

    // Update logic here
}};

/**
 * Post-update method called after all update methods
 * @param {{number}} dt - Delta time in seconds
 */
{class_name}.prototype.postUpdate = function(dt) {{
    // Post-update logic here
}};

/**
 * Swap method called when script is hot-reloaded
 * @param {{object}} old - Old script instance
 */
{class_name}.prototype.swap = function(old) {{
    // Preserve state during hot-reload
    this.enabled = old.enabled;
}};
"""


def generate_interactive_component(name: str) -> str:
    """Generate interactive component with mouse/touch handling"""
    class_name = name[0].upper() + name[1:]
    script_name = name[0].lower() + name[1:]

    return f"""/**
 * {class_name} Component
 * Interactive component with mouse and touch input handling
 */

var {class_name} = pc.createScript('{script_name}');

{class_name}.attributes.add('hoverColor', {{
    type: 'rgb',
    default: [0.5, 0.8, 1.0],
    title: 'Hover Color'
}});

{class_name}.attributes.add('clickScale', {{
    type: 'number',
    default: 0.9,
    title: 'Click Scale'
}});

{class_name}.prototype.initialize = function() {{
    this.originalColor = null;
    this.originalScale = this.entity.getLocalScale().clone();
    this.isHovered = false;
    this.isPressed = false;

    // Store material reference
    if (this.entity.model) {{
        this.material = this.entity.model.material;
        this.originalColor = this.material.diffuse.clone();
    }}

    // Mouse events
    if (this.app.mouse) {{
        this.app.mouse.on(pc.EVENT_MOUSEDOWN, this.onMouseDown, this);
        this.app.mouse.on(pc.EVENT_MOUSEUP, this.onMouseUp, this);
    }}

    // Touch events
    if (this.app.touch) {{
        this.app.touch.on(pc.EVENT_TOUCHSTART, this.onTouchStart, this);
        this.app.touch.on(pc.EVENT_TOUCHEND, this.onTouchEnd, this);
    }}
}};

{class_name}.prototype.update = function(dt) {{
    if (!this.app.mouse) return;

    // Raycast from mouse
    const camera = this.app.root.findByName('Camera');
    if (!camera) return;

    const ray = camera.camera.screenToWorld(
        this.app.mouse.x,
        this.app.mouse.y,
        camera.camera.farClip
    );

    const from = camera.getPosition();
    const to = ray;

    const result = this.app.systems.rigidbody.raycastFirst(from, to);

    // Check if hovering
    const wasHovered = this.isHovered;
    this.isHovered = result && result.entity === this.entity;

    if (this.isHovered && !wasHovered) {{
        this.onHoverEnter();
    }} else if (!this.isHovered && wasHovered) {{
        this.onHoverExit();
    }}
}};

{class_name}.prototype.onHoverEnter = function() {{
    if (this.material && this.originalColor) {{
        this.material.diffuse.set(
            this.hoverColor[0],
            this.hoverColor[1],
            this.hoverColor[2]
        );
        this.material.update();
    }}
    this.fire('hover:enter');
}};

{class_name}.prototype.onHoverExit = function() {{
    if (this.material && this.originalColor) {{
        this.material.diffuse.copy(this.originalColor);
        this.material.update();
    }}
    this.fire('hover:exit');
}};

{class_name}.prototype.onMouseDown = function(event) {{
    if (!this.isHovered) return;

    this.isPressed = true;
    this.entity.setLocalScale(
        this.originalScale.x * this.clickScale,
        this.originalScale.y * this.clickScale,
        this.originalScale.z * this.clickScale
    );

    this.fire('click', {{ button: event.button }});
}};

{class_name}.prototype.onMouseUp = function(event) {{
    if (!this.isPressed) return;

    this.isPressed = false;
    this.entity.setLocalScale(this.originalScale);

    if (this.isHovered) {{
        this.fire('click:release');
    }}
}};

{class_name}.prototype.onTouchStart = function(event) {{
    this.onMouseDown({{ button: 0 }});
}};

{class_name}.prototype.onTouchEnd = function(event) {{
    this.onMouseUp({{ button: 0 }});
}};
"""


def generate_animation_component(name: str) -> str:
    """Generate component for animation control"""
    class_name = name[0].upper() + name[1:]
    script_name = name[0].lower() + name[1:]

    return f"""/**
 * {class_name} Component
 * Controls entity animations with state management
 */

var {class_name} = pc.createScript('{script_name}');

{class_name}.attributes.add('idleAnim', {{
    type: 'string',
    default: 'Idle',
    title: 'Idle Animation'
}});

{class_name}.attributes.add('walkAnim', {{
    type: 'string',
    default: 'Walk',
    title: 'Walk Animation'
}});

{class_name}.attributes.add('runAnim', {{
    type: 'string',
    default: 'Run',
    title: 'Run Animation'
}});

{class_name}.attributes.add('blendTime', {{
    type: 'number',
    default: 0.2,
    title: 'Blend Time',
    description: 'Animation blend time in seconds'
}});

{class_name}.prototype.initialize = function() {{
    this.currentState = 'idle';
    this.animComponent = this.entity.anim;

    if (!this.animComponent) {{
        console.warn('{class_name}: No anim component found');
        return;
    }}

    // Play initial animation
    this.setState('idle');
}};

{class_name}.prototype.setState = function(state) {{
    if (this.currentState === state) return;

    const animName = this.getAnimationName(state);
    if (!animName) {{
        console.warn(`{class_name}: Unknown state "${{state}}"`);
        return;
    }}

    // Blend to new animation
    this.animComponent.setBoolean(state, true);

    this.currentState = state;
    this.fire('state:change', {{ from: this.currentState, to: state }});
}};

{class_name}.prototype.getAnimationName = function(state) {{
    switch (state) {{
        case 'idle': return this.idleAnim;
        case 'walk': return this.walkAnim;
        case 'run': return this.runAnim;
        default: return null;
    }}
}};

{class_name}.prototype.playAnimation = function(name, loop = true) {{
    if (!this.animComponent) return;

    const layer = this.animComponent.baseLayer;
    layer.transition(name, this.blendTime);

    if (loop) {{
        this.animComponent.setBoolean('loop', true);
    }}
}};

{class_name}.prototype.update = function(dt) {{
    // Override to add state logic
    // Example: this.setState('walk') based on velocity
}};
"""


def generate_physics_component(name: str) -> str:
    """Generate physics-based component"""
    class_name = name[0].upper() + name[1:]
    script_name = name[0].lower() + name[1:]

    return f"""/**
 * {class_name} Component
 * Physics-based component with force and impulse control
 */

var {class_name} = pc.createScript('{script_name}');

{class_name}.attributes.add('mass', {{
    type: 'number',
    default: 1.0,
    title: 'Mass'
}});

{class_name}.attributes.add('friction', {{
    type: 'number',
    default: 0.5,
    title: 'Friction'
}});

{class_name}.attributes.add('restitution', {{
    type: 'number',
    default: 0.3,
    title: 'Restitution',
    description: 'Bounciness (0-1)'
}});

{class_name}.attributes.add('linearDamping', {{
    type: 'number',
    default: 0.1,
    title: 'Linear Damping'
}});

{class_name}.attributes.add('angularDamping', {{
    type: 'number',
    default: 0.1,
    title: 'Angular Damping'
}});

{class_name}.prototype.initialize = function() {{
    this.rigidbody = this.entity.rigidbody;

    if (!this.rigidbody) {{
        console.warn('{class_name}: No rigidbody component found');
        return;
    }}

    // Configure physics properties
    this.rigidbody.mass = this.mass;
    this.rigidbody.friction = this.friction;
    this.rigidbody.restitution = this.restitution;
    this.rigidbody.linearDamping = this.linearDamping;
    this.rigidbody.angularDamping = this.angularDamping;

    // Listen to collision events
    this.entity.collision.on('contact', this.onContact, this);
    this.entity.collision.on('collisionstart', this.onCollisionStart, this);
    this.entity.collision.on('collisionend', this.onCollisionEnd, this);
}};

{class_name}.prototype.applyForce = function(force) {{
    if (!this.rigidbody) return;
    this.rigidbody.applyForce(force.x, force.y, force.z);
}};

{class_name}.prototype.applyImpulse = function(impulse) {{
    if (!this.rigidbody) return;
    this.rigidbody.applyImpulse(impulse.x, impulse.y, impulse.z);
}};

{class_name}.prototype.applyTorque = function(torque) {{
    if (!this.rigidbody) return;
    this.rigidbody.applyTorque(torque.x, torque.y, torque.z);
}};

{class_name}.prototype.applyTorqueImpulse = function(torque) {{
    if (!this.rigidbody) return;
    this.rigidbody.applyTorqueImpulse(torque.x, torque.y, torque.z);
}};

{class_name}.prototype.onContact = function(result) {{
    // Called every frame during contact
    this.fire('physics:contact', {{ result: result }});
}};

{class_name}.prototype.onCollisionStart = function(result) {{
    console.log('Collision started with:', result.other.name);
    this.fire('physics:collision:start', {{ result: result }});
}};

{class_name}.prototype.onCollisionEnd = function(other) {{
    console.log('Collision ended with:', other.name);
    this.fire('physics:collision:end', {{ other: other }});
}};

{class_name}.prototype.update = function(dt) {{
    // Access velocity
    const velocity = this.rigidbody.linearVelocity;
    const speed = velocity.length();

    // Example: Apply drag at high speeds
    if (speed > 10) {{
        const drag = velocity.clone().scale(-0.1);
        this.applyForce(drag);
    }}
}};
"""


def generate_character_controller(name: str) -> str:
    """Generate character controller component"""
    class_name = name[0].upper() + name[1:]
    script_name = name[0].lower() + name[1:]

    return f"""/**
 * {class_name} Component
 * Third-person character controller with WASD movement
 */

var {class_name} = pc.createScript('{script_name}');

{class_name}.attributes.add('speed', {{
    type: 'number',
    default: 5.0,
    title: 'Movement Speed'
}});

{class_name}.attributes.add('jumpForce', {{
    type: 'number',
    default: 10.0,
    title: 'Jump Force'
}});

{class_name}.attributes.add('rotationSpeed', {{
    type: 'number',
    default: 180,
    title: 'Rotation Speed',
    description: 'Degrees per second'
}});

{class_name}.attributes.add('camera', {{
    type: 'entity',
    title: 'Camera Entity'
}});

{class_name}.prototype.initialize = function() {{
    this.velocity = new pc.Vec3();
    this.isGrounded = false;
    this.moveDirection = new pc.Vec3();

    // Collision detection for grounding
    if (this.entity.collision) {{
        this.entity.collision.on('collisionstart', this.onCollisionStart, this);
        this.entity.collision.on('collisionend', this.onCollisionEnd, this);
    }}
}};

{class_name}.prototype.update = function(dt) {{
    this.handleMovement(dt);
    this.handleJump();
    this.handleRotation(dt);
}};

{class_name}.prototype.handleMovement = function(dt) {{
    const keyboard = this.app.keyboard;

    // Get camera forward and right vectors
    const forward = this.camera ?
        this.camera.forward.clone() :
        new pc.Vec3(0, 0, -1);

    const right = this.camera ?
        this.camera.right.clone() :
        new pc.Vec3(1, 0, 0);

    // Flatten to horizontal plane
    forward.y = 0;
    forward.normalize();
    right.y = 0;
    right.normalize();

    // Calculate movement direction
    this.moveDirection.set(0, 0, 0);

    if (keyboard.isPressed(pc.KEY_W)) {{
        this.moveDirection.add(forward);
    }}
    if (keyboard.isPressed(pc.KEY_S)) {{
        this.moveDirection.sub(forward);
    }}
    if (keyboard.isPressed(pc.KEY_A)) {{
        this.moveDirection.sub(right);
    }}
    if (keyboard.isPressed(pc.KEY_D)) {{
        this.moveDirection.add(right);
    }}

    // Normalize and apply speed
    if (this.moveDirection.length() > 0) {{
        this.moveDirection.normalize();
        this.moveDirection.scale(this.speed * dt);

        // Move entity
        const pos = this.entity.getPosition();
        pos.add(this.moveDirection);
        this.entity.setPosition(pos);
    }}
}};

{class_name}.prototype.handleJump = function() {{
    const keyboard = this.app.keyboard;

    if (keyboard.wasPressed(pc.KEY_SPACE) && this.isGrounded) {{
        if (this.entity.rigidbody) {{
            this.entity.rigidbody.applyImpulse(0, this.jumpForce, 0);
        }}
    }}
}};

{class_name}.prototype.handleRotation = function(dt) {{
    if (this.moveDirection.length() > 0) {{
        const targetAngle = Math.atan2(this.moveDirection.x, this.moveDirection.z) * pc.math.RAD_TO_DEG;
        const currentAngles = this.entity.getEulerAngles();

        // Smoothly rotate towards movement direction
        const newY = this.lerpAngle(
            currentAngles.y,
            targetAngle,
            this.rotationSpeed * dt
        );

        this.entity.setEulerAngles(currentAngles.x, newY, currentAngles.z);
    }}
}};

{class_name}.prototype.lerpAngle = function(from, to, t) {{
    let diff = to - from;
    while (diff > 180) diff -= 360;
    while (diff < -180) diff += 360;
    return from + diff * Math.min(t / 180, 1);
}};

{class_name}.prototype.onCollisionStart = function(result) {{
    // Check if collision is below (ground)
    const contact = result.contacts[0];
    if (contact && contact.normal.y > 0.5) {{
        this.isGrounded = true;
    }}
}};

{class_name}.prototype.onCollisionEnd = function(other) {{
    this.isGrounded = false;
}};
"""


def generate_camera_controller(name: str) -> str:
    """Generate orbit camera controller"""
    class_name = name[0].upper() + name[1:]
    script_name = name[0].lower() + name[1:]

    return f"""/**
 * {class_name} Component
 * Orbit camera controller with mouse/touch input
 */

var {class_name} = pc.createScript('{script_name}');

{class_name}.attributes.add('target', {{
    type: 'entity',
    title: 'Target Entity'
}});

{class_name}.attributes.add('distance', {{
    type: 'number',
    default: 10,
    title: 'Distance'
}});

{class_name}.attributes.add('minDistance', {{
    type: 'number',
    default: 2,
    title: 'Min Distance'
}});

{class_name}.attributes.add('maxDistance', {{
    type: 'number',
    default: 20,
    title: 'Max Distance'
}});

{class_name}.attributes.add('sensitivity', {{
    type: 'number',
    default: 0.3,
    title: 'Sensitivity'
}});

{class_name}.attributes.add('damping', {{
    type: 'number',
    default: 0.1,
    title: 'Damping'
}});

{class_name}.prototype.initialize = function() {{
    this.yaw = 0;
    this.pitch = 0;
    this.currentDistance = this.distance;

    this.targetYaw = 0;
    this.targetPitch = 0;

    // Mouse events
    if (this.app.mouse) {{
        this.app.mouse.on(pc.EVENT_MOUSEMOVE, this.onMouseMove, this);
        this.app.mouse.on(pc.EVENT_MOUSEWHEEL, this.onMouseWheel, this);
    }}

    // Touch events
    if (this.app.touch) {{
        this.app.touch.on(pc.EVENT_TOUCHMOVE, this.onTouchMove, this);
    }}
}};

{class_name}.prototype.update = function(dt) {{
    if (!this.target) return;

    // Smooth damping
    this.yaw = pc.math.lerp(this.yaw, this.targetYaw, this.damping);
    this.pitch = pc.math.lerp(this.pitch, this.targetPitch, this.damping);

    // Clamp pitch
    this.pitch = pc.math.clamp(this.pitch, -89, 89);

    // Calculate camera position
    const targetPos = this.target.getPosition();

    const yawRad = this.yaw * pc.math.DEG_TO_RAD;
    const pitchRad = this.pitch * pc.math.DEG_TO_RAD;

    const x = targetPos.x + this.currentDistance * Math.cos(pitchRad) * Math.sin(yawRad);
    const y = targetPos.y + this.currentDistance * Math.sin(pitchRad);
    const z = targetPos.z + this.currentDistance * Math.cos(pitchRad) * Math.cos(yawRad);

    this.entity.setPosition(x, y, z);
    this.entity.lookAt(targetPos);
}};

{class_name}.prototype.onMouseMove = function(event) {{
    if (!event.buttons[pc.MOUSEBUTTON_LEFT]) return;

    this.targetYaw -= event.dx * this.sensitivity;
    this.targetPitch -= event.dy * this.sensitivity;
}};

{class_name}.prototype.onMouseWheel = function(event) {{
    this.currentDistance -= event.wheelDelta * 0.5;
    this.currentDistance = pc.math.clamp(
        this.currentDistance,
        this.minDistance,
        this.maxDistance
    );
}};

{class_name}.prototype.onTouchMove = function(event) {{
    if (event.touches.length !== 1) return;

    const touch = event.touches[0];
    this.targetYaw -= touch.dx * this.sensitivity;
    this.targetPitch -= touch.dy * this.sensitivity;
}};
"""


def generate_ui_component(name: str) -> str:
    """Generate UI component with screen-space interaction"""
    class_name = name[0].upper() + name[1:]
    script_name = name[0].lower() + name[1:]

    return f"""/**
 * {class_name} Component
 * UI component with button-like behavior
 */

var {class_name} = pc.createScript('{script_name}');

{class_name}.attributes.add('hoverScale', {{
    type: 'number',
    default: 1.1,
    title: 'Hover Scale'
}});

{class_name}.attributes.add('clickScale', {{
    type: 'number',
    default: 0.95,
    title: 'Click Scale'
}});

{class_name}.attributes.add('transitionSpeed', {{
    type: 'number',
    default: 10,
    title: 'Transition Speed'
}});

{class_name}.prototype.initialize = function() {{
    this.originalScale = this.entity.getLocalScale().clone();
    this.targetScale = this.originalScale.clone();
    this.isHovered = false;
    this.isPressed = false;

    // Add element component if not present
    if (!this.entity.element) {{
        console.warn('{class_name}: No element component found');
        return;
    }}

    // Mouse events
    this.entity.element.on('mouseenter', this.onMouseEnter, this);
    this.entity.element.on('mouseleave', this.onMouseLeave, this);
    this.entity.element.on('mousedown', this.onMouseDown, this);
    this.entity.element.on('mouseup', this.onMouseUp, this);
    this.entity.element.on('click', this.onClick, this);

    // Touch events
    this.entity.element.on('touchstart', this.onTouchStart, this);
    this.entity.element.on('touchend', this.onTouchEnd, this);
}};

{class_name}.prototype.update = function(dt) {{
    // Smooth scale transition
    const current = this.entity.getLocalScale();
    const lerped = new pc.Vec3().lerp(
        current,
        this.targetScale,
        this.transitionSpeed * dt
    );
    this.entity.setLocalScale(lerped);
}};

{class_name}.prototype.onMouseEnter = function() {{
    this.isHovered = true;
    this.targetScale.copy(this.originalScale).scale(this.hoverScale);
    this.fire('hover:enter');
}};

{class_name}.prototype.onMouseLeave = function() {{
    this.isHovered = false;
    if (!this.isPressed) {{
        this.targetScale.copy(this.originalScale);
    }}
    this.fire('hover:exit');
}};

{class_name}.prototype.onMouseDown = function() {{
    this.isPressed = true;
    this.targetScale.copy(this.originalScale).scale(this.clickScale);
    this.fire('press');
}};

{class_name}.prototype.onMouseUp = function() {{
    this.isPressed = false;
    if (this.isHovered) {{
        this.targetScale.copy(this.originalScale).scale(this.hoverScale);
    }} else {{
        this.targetScale.copy(this.originalScale);
    }}
    this.fire('release');
}};

{class_name}.prototype.onClick = function() {{
    console.log('{class_name} clicked');
    this.fire('click');
}};

{class_name}.prototype.onTouchStart = function() {{
    this.onMouseDown();
}};

{class_name}.prototype.onTouchEnd = function() {{
    this.onMouseUp();
    this.fire('click');
}};
"""


# Component type registry
COMPONENT_TYPES: Dict[str, Dict] = {{
    'basic': {{
        'name': 'Basic Component',
        'description': 'Simple component with lifecycle methods',
        'generator': generate_basic_component
    }},
    'interactive': {{
        'name': 'Interactive Component',
        'description': 'Mouse and touch interaction handling',
        'generator': lambda name: generate_interactive_component(name)
    }},
    'animation': {{
        'name': 'Animation Controller',
        'description': 'Animation state management',
        'generator': lambda name: generate_animation_component(name)
    }},
    'physics': {{
        'name': 'Physics Component',
        'description': 'Physics-based component with forces',
        'generator': lambda name: generate_physics_component(name)
    }},
    'character': {{
        'name': 'Character Controller',
        'description': 'Third-person character movement',
        'generator': lambda name: generate_character_controller(name)
    }},
    'camera': {{
        'name': 'Camera Controller',
        'description': 'Orbit camera with mouse control',
        'generator': lambda name: generate_camera_controller(name)
    }},
    'ui': {{
        'name': 'UI Component',
        'description': 'Screen-space UI element',
        'generator': lambda name: generate_ui_component(name)
    }}
}}


def interactive_mode():
    """Run interactive component builder"""
    print("\n" + "="*60)
    print("PlayCanvas Component Builder - Interactive Mode")
    print("="*60)

    # Get component name
    while True:
        name = input("\nComponent name (e.g., PlayerController): ").strip()
        if name:
            # Validate name
            if not name[0].isalpha():
                print("Error: Component name must start with a letter")
                continue
            if not name.replace('_', '').isalnum():
                print("Error: Component name can only contain letters, numbers, and underscores")
                continue
            break
        print("Error: Component name is required")

    # Show component types
    print("\nAvailable component types:")
    print("-" * 60)
    for idx, (key, info) in enumerate(COMPONENT_TYPES.items(), 1):
        print(f"{idx}. {info['name']:25} - {info['description']}")

    # Get component type
    while True:
        try:
            choice = input(f"\nSelect component type (1-{len(COMPONENT_TYPES)}): ").strip()
            idx = int(choice)
            if 1 <= idx <= len(COMPONENT_TYPES):
                component_type = list(COMPONENT_TYPES.keys())[idx - 1]
                break
            print(f"Error: Please enter a number between 1 and {len(COMPONENT_TYPES)}")
        except ValueError:
            print("Error: Please enter a valid number")

    # Include attributes for basic component
    include_attributes = True
    if component_type == 'basic':
        attr_choice = input("\nInclude attribute definitions? (y/n): ").strip().lower()
        include_attributes = attr_choice in ['y', 'yes', '']

    # Get output path
    output_dir = input("\nOutput directory (default: current directory): ").strip()
    if not output_dir:
        output_dir = "."

    # Generate component
    print("\n" + "-"*60)
    print("Generating component...")

    try:
        if component_type == 'basic':
            code = generate_basic_component(name, include_attributes)
        else:
            generator = COMPONENT_TYPES[component_type]['generator']
            code = generator(name)

        # Create output file
        script_name = name[0].lower() + name[1:]
        filename = f"{script_name}.js"
        filepath = os.path.join(output_dir, filename)

        # Create directory if needed
        os.makedirs(output_dir, exist_ok=True)

        # Write file
        with open(filepath, 'w') as f:
            f.write(code)

        print(f"\n✓ Component created: {filepath}")
        print(f"\nComponent type: {COMPONENT_TYPES[component_type]['name']}")
        print(f"Lines of code: {len(code.splitlines())}")

        print("\nUsage:")
        print(f"1. Add script to PlayCanvas project")
        print(f"2. Attach to entity via Editor or code:")
        print(f"   entity.addComponent('script');")
        print(f"   entity.script.create('{script_name}');")
        print(f"3. Configure attributes in Inspector")

    except Exception as e:
        print(f"\nError: Failed to generate component: {e}")
        return 1

    return 0


def cli_mode(args):
    """Run CLI component builder"""
    name = args.name
    component_type = args.type
    output_dir = args.output
    include_attributes = args.attributes

    # Validate inputs
    if component_type not in COMPONENT_TYPES:
        print(f"Error: Unknown component type '{component_type}'")
        print(f"Available types: {', '.join(COMPONENT_TYPES.keys())}")
        return 1

    # Generate component
    try:
        if component_type == 'basic':
            code = generate_basic_component(name, include_attributes)
        else:
            generator = COMPONENT_TYPES[component_type]['generator']
            code = generator(name)

        # Create output file
        script_name = name[0].lower() + name[1:]
        filename = f"{script_name}.js"
        filepath = os.path.join(output_dir, filename)

        # Create directory if needed
        os.makedirs(output_dir, exist_ok=True)

        # Write file
        with open(filepath, 'w') as f:
            f.write(code)

        print(f"✓ Component created: {filepath}")
        return 0

    except Exception as e:
        print(f"Error: Failed to generate component: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description='PlayCanvas Component Builder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python component_builder.py

  Generate basic component:
    python component_builder.py --name MyComponent --type basic --output ./

  Generate character controller:
    python component_builder.py -n PlayerController -t character -o ./scripts/

  Generate camera controller:
    python component_builder.py -n OrbitCamera -t camera -o ./scripts/

Available component types:
  basic       - Basic component with lifecycle methods
  interactive - Mouse and touch interaction
  animation   - Animation state management
  physics     - Physics-based component
  character   - Third-person character controller
  camera      - Orbit camera controller
  ui          - Screen-space UI element
        """
    )

    parser.add_argument(
        '-n', '--name',
        help='Component name (e.g., PlayerController)'
    )

    parser.add_argument(
        '-t', '--type',
        choices=list(COMPONENT_TYPES.keys()),
        help='Component type'
    )

    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output directory (default: current directory)'
    )

    parser.add_argument(
        '--attributes',
        action='store_true',
        default=True,
        help='Include attribute definitions (for basic type)'
    )

    args = parser.parse_args()

    # Run interactive mode if no arguments
    if not args.name or not args.type:
        return interactive_mode()

    return cli_mode(args)


if __name__ == '__main__':
    sys.exit(main())

```


===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/scripts/project_generator.py =====

```py
#!/usr/bin/env python3
"""
PlayCanvas Project Generator

Generates PlayCanvas project boilerplate with various configurations.

Usage:
    python project_generator.py                    # Interactive mode
    python project_generator.py --type basic       # Generate basic scene
    python project_generator.py --list             # List available types
"""

import argparse
import os
import sys
from pathlib import Path


def create_html_template(title, scene_code, additional_scripts=""):
    """Create complete HTML template for PlayCanvas"""
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
      overflow: hidden;
      background: #000;
    }}

    canvas {{
      display: block;
      width: 100%;
      height: 100vh;
    }}

    #info {{
      position: absolute;
      top: 10px;
      left: 10px;
      color: white;
      background: rgba(0, 0, 0, 0.7);
      padding: 10px 15px;
      border-radius: 5px;
      font-size: 14px;
      font-family: monospace;
      pointer-events: none;
      z-index: 100;
    }}

    #controls {{
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 10px;
      z-index: 100;
    }}

    button {{
      padding: 10px 20px;
      font-size: 14px;
      background: rgba(255, 255, 255, 0.1);
      color: white;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-radius: 5px;
      cursor: pointer;
      transition: all 0.3s;
      backdrop-filter: blur(10px);
    }}

    button:hover {{
      background: rgba(255, 255, 255, 0.2);
      transform: translateY(-2px);
    }}

    button:active {{
      transform: translateY(0);
    }}
  </style>
</head>
<body>
  <div id="info">
    <div id="fps">FPS: --</div>
    <div id="drawCalls">Draw Calls: --</div>
  </div>

  <div id="controls"></div>

  <canvas id="application-canvas"></canvas>

  <!-- PlayCanvas Engine -->
  <script src="https://cdn.jsdelivr.net/npm/playcanvas@1.70.0/build/playcanvas.min.js"></script>

  {additional_scripts}

  <script type="module">
{scene_code}
  </script>
</body>
</html>"""


def generate_basic_scene():
    """Generate basic PlayCanvas scene"""
    code = """    // Create canvas
    const canvas = document.getElementById('application-canvas');

    // Create application
    const app = new pc.Application(canvas, {{
      keyboard: new pc.Keyboard(window),
      mouse: new pc.Mouse(canvas)
    }});

    // Configure canvas
    app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
    app.setCanvasResolution(pc.RESOLUTION_AUTO);

    // Handle resize
    window.addEventListener('resize', () => app.resizeCanvas());

    // Create camera
    const camera = new pc.Entity('camera');
    camera.addComponent('camera', {{
      clearColor: new pc.Color(0.2, 0.3, 0.4)
    }});
    camera.setPosition(0, 2, 5);
    camera.lookAt(0, 0, 0);
    app.root.addChild(camera);

    // Create directional light
    const light = new pc.Entity('light');
    light.addComponent('light', {{
      type: pc.LIGHTTYPE_DIRECTIONAL,
      color: new pc.Color(1, 1, 1),
      castShadows: true
    }});
    light.setEulerAngles(45, 30, 0);
    app.root.addChild(light);

    // Create ground
    const ground = new pc.Entity('ground');
    ground.addComponent('model', {{
      type: 'plane',
      castShadows: false,
      receiveShadows: true
    }});
    ground.setLocalScale(10, 1, 10);
    app.root.addChild(ground);

    // Create cube
    const cube = new pc.Entity('cube');
    cube.addComponent('model', {{
      type: 'box',
      castShadows: true
    }});
    cube.setPosition(0, 0.5, 0);
    app.root.addChild(cube);

    // Animation
    let isRotating = true;

    app.on('update', (dt) => {{
      if (isRotating) {{
        cube.rotate(10 * dt, 20 * dt, 30 * dt);
      }

      // Update stats
      document.getElementById('fps').textContent = `FPS: ${{Math.round(1 / dt)}}`;
      document.getElementById('drawCalls').textContent = `Draw Calls: ${{app.stats?.drawCalls?.total || 0}}`;
    }});

    // Controls
    const controls = document.getElementById('controls');

    const toggleBtn = document.createElement('button');
    toggleBtn.textContent = 'Pause Rotation';
    toggleBtn.addEventListener('click', () => {{
      isRotating = !isRotating;
      toggleBtn.textContent = isRotating ? 'Pause Rotation' : 'Resume Rotation';
    }});
    controls.appendChild(toggleBtn);

    // Start application
    app.start();

    console.log('PlayCanvas application started');"""

    return code


def generate_physics_scene():
    """Generate scene with physics simulation"""
    additional_scripts = """
  <!-- Ammo.js Physics Engine -->
  <script src="https://cdn.jsdelivr.net/npm/ammo.js@0.0.10/ammo.js"></script>"""

    code = """    const canvas = document.getElementById('application-canvas');
    const app = new pc.Application(canvas, {{
      keyboard: new pc.Keyboard(window),
      mouse: new pc.Mouse(canvas)
    }});

    app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
    app.setCanvasResolution(pc.RESOLUTION_AUTO);
    window.addEventListener('resize', () => app.resizeCanvas());

    // Load Ammo.js
    Ammo().then((AmmoLib) => {{
      window.Ammo = AmmoLib;

      // Camera
      const camera = new pc.Entity('camera');
      camera.addComponent('camera', {{
        clearColor: new pc.Color(0.2, 0.3, 0.4)
      }});
      camera.setPosition(0, 5, 10);
      camera.lookAt(0, 0, 0);
      app.root.addChild(camera);

      // Light
      const light = new pc.Entity('light');
      light.addComponent('light', {{
        type: pc.LIGHTTYPE_DIRECTIONAL,
        castShadows: true
      }});
      light.setEulerAngles(45, 30, 0);
      app.root.addChild(light);

      // Static ground
      const ground = new pc.Entity('ground');
      ground.addComponent('model', {{
        type: 'box',
        castShadows: false,
        receiveShadows: true
      }});
      ground.setLocalScale(20, 1, 20);

      ground.addComponent('rigidbody', {{
        type: pc.BODYTYPE_STATIC
      }});

      ground.addComponent('collision', {{
        type: 'box',
        halfExtents: new pc.Vec3(10, 0.5, 10)
      }});

      app.root.addChild(ground);

      // Dynamic cubes
      const cubes = [];

      function spawnCube() {{
        const cube = new pc.Entity('cube');
        cube.addComponent('model', {{
          type: 'box',
          castShadows: true
        }});

        cube.setPosition(
          (Math.random() - 0.5) * 4,
          5 + Math.random() * 5,
          (Math.random() - 0.5) * 4
        );

        cube.setEulerAngles(
          Math.random() * 360,
          Math.random() * 360,
          Math.random() * 360
        );

        cube.addComponent('rigidbody', {{
          type: pc.BODYTYPE_DYNAMIC,
          mass: 1,
          friction: 0.5,
          restitution: 0.3
        }});

        cube.addComponent('collision', {{
          type: 'box',
          halfExtents: new pc.Vec3(0.5, 0.5, 0.5)
        }});

        app.root.addChild(cube);
        cubes.push(cube);

        // Limit total cubes
        if (cubes.length > 50) {{
          const old = cubes.shift();
          old.destroy();
        }}
      }}

      // Update stats
      app.on('update', (dt) => {{
        document.getElementById('fps').textContent = `FPS: ${{Math.round(1 / dt)}}`;
        document.getElementById('drawCalls').textContent = `Cubes: ${{cubes.length}}`;
      }});

      // Controls
      const controls = document.getElementById('controls');

      const spawnBtn = document.createElement('button');
      spawnBtn.textContent = 'Spawn Cube';
      spawnBtn.addEventListener('click', spawnCube);
      controls.appendChild(spawnBtn);

      const resetBtn = document.createElement('button');
      resetBtn.textContent = 'Reset All';
      resetBtn.addEventListener('click', () => {{
        cubes.forEach(cube => cube.destroy());
        cubes.length = 0;
      }});
      controls.appendChild(resetBtn);

      // Auto-spawn
      setInterval(spawnCube, 1000);

      app.start();
    }});"""

    return code, additional_scripts


def generate_model_viewer():
    """Generate 3D model viewer"""
    code = """    const canvas = document.getElementById('application-canvas');
    const app = new pc.Application(canvas, {{
      keyboard: new pc.Keyboard(window),
      mouse: new pc.Mouse(canvas)
    }});

    app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
    app.setCanvasResolution(pc.RESOLUTION_AUTO);
    window.addEventListener('resize', () => app.resizeCanvas());

    // Camera
    const camera = new pc.Entity('camera');
    camera.addComponent('camera', {{
      clearColor: new pc.Color(0.1, 0.1, 0.15)
    }});
    camera.setPosition(0, 2, 5);
    camera.lookAt(0, 1, 0);
    app.root.addChild(camera);

    // Lights
    const light1 = new pc.Entity('light1');
    light1.addComponent('light', {{
      type: pc.LIGHTTYPE_DIRECTIONAL,
      color: new pc.Color(1, 1, 1),
      intensity: 1,
      castShadows: true
    }});
    light1.setEulerAngles(45, 30, 0);
    app.root.addChild(light1);

    const light2 = new pc.Entity('light2');
    light2.addComponent('light', {{
      type: pc.LIGHTTYPE_POINT,
      color: new pc.Color(0.5, 0.7, 1),
      intensity: 0.5
    }});
    light2.setPosition(-3, 2, 3);
    app.root.addChild(light2);

    // Ground
    const ground = new pc.Entity('ground');
    ground.addComponent('model', {{
      type: 'plane',
      castShadows: false,
      receiveShadows: true
    }});
    ground.setLocalScale(10, 1, 10);
    app.root.addChild(ground);

    // Model (placeholder - user should replace with their model)
    const model = new pc.Entity('model');
    model.addComponent('model', {{
      type: 'box',
      castShadows: true
    }});
    model.setPosition(0, 1, 0);
    app.root.addChild(model);

    // Rotation controls
    let autoRotate = true;
    let rotationSpeed = 20;

    // Mouse interaction
    let isDragging = false;
    let lastMouseX = 0;
    let lastMouseY = 0;

    app.mouse.on(pc.EVENT_MOUSEDOWN, (event) => {{
      isDragging = true;
      lastMouseX = event.x;
      lastMouseY = event.y;
      autoRotate = false;
    }});

    app.mouse.on(pc.EVENT_MOUSEUP, () => {{
      isDragging = false;
    }});

    app.mouse.on(pc.EVENT_MOUSEMOVE, (event) => {{
      if (isDragging) {{
        const dx = event.x - lastMouseX;
        const dy = event.y - lastMouseY;

        model.rotate(0, dx * 0.5, 0);
        camera.rotate(dy * 0.2, 0, 0);

        lastMouseX = event.x;
        lastMouseY = event.y;
      }}
    }});

    // Zoom with mouse wheel
    app.mouse.on(pc.EVENT_MOUSEWHEEL, (event) => {{
      const zoom = event.wheelDelta * 0.1;
      const pos = camera.getPosition();
      const distance = pos.length();

      if (distance + zoom > 2 && distance + zoom < 20) {{
        camera.translate(0, 0, zoom);
      }}
    }});

    // Update loop
    app.on('update', (dt) => {{
      if (autoRotate) {{
        model.rotate(0, rotationSpeed * dt, 0);
      }}

      document.getElementById('fps').textContent = `FPS: ${{Math.round(1 / dt)}}`;
      document.getElementById('drawCalls').textContent = 'Drag to rotate • Scroll to zoom';
    }});

    // Controls
    const controls = document.getElementById('controls');

    const autoRotateBtn = document.createElement('button');
    autoRotateBtn.textContent = 'Toggle Auto-Rotate';
    autoRotateBtn.addEventListener('click', () => {{
      autoRotate = !autoRotate;
    }});
    controls.appendChild(autoRotateBtn);

    const resetBtn = document.createElement('button');
    resetBtn.textContent = 'Reset View';
    resetBtn.addEventListener('click', () => {{
      camera.setPosition(0, 2, 5);
      camera.lookAt(0, 1, 0);
      model.setEulerAngles(0, 0, 0);
      autoRotate = true;
    }});
    controls.appendChild(resetBtn);

    app.start();"""

    return code


def generate_first_person():
    """Generate first-person controller"""
    code = """    const canvas = document.getElementById('application-canvas');
    const app = new pc.Application(canvas, {{
      keyboard: new pc.Keyboard(window),
      mouse: new pc.Mouse(canvas)
    }});

    app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
    app.setCanvasResolution(pc.RESOLUTION_AUTO);
    window.addEventListener('resize', () => app.resizeCanvas());

    // Lock pointer on click
    canvas.addEventListener('click', () => {{
      canvas.requestPointerLock();
    }});

    // Camera
    const camera = new pc.Entity('camera');
    camera.addComponent('camera', {{
      clearColor: new pc.Color(0.5, 0.7, 0.9),
      farClip: 1000
    }});
    camera.setPosition(0, 1.6, 5);
    app.root.addChild(camera);

    // Light
    const light = new pc.Entity('light');
    light.addComponent('light', {{
      type: pc.LIGHTTYPE_DIRECTIONAL,
      castShadows: true
    }});
    light.setEulerAngles(45, 30, 0);
    app.root.addChild(light);

    // Ground
    const ground = new pc.Entity('ground');
    ground.addComponent('model', {{
      type: 'plane',
      castShadows: false,
      receiveShadows: true
    }});
    ground.setLocalScale(50, 1, 50);
    app.root.addChild(ground);

    // Some boxes for reference
    for (let i = 0; i < 20; i++) {{
      const box = new pc.Entity('box');
      box.addComponent('model', {{
        type: 'box',
        castShadows: true
      }});
      box.setPosition(
        (Math.random() - 0.5) * 40,
        0.5,
        (Math.random() - 0.5) * 40
      );
      box.setLocalScale(1, Math.random() * 3 + 1, 1);
      app.root.addChild(box);
    }}

    // First-person controls
    const moveSpeed = 5;
    const lookSpeed = 0.2;
    let pitch = 0;
    let yaw = 0;

    // Mouse look
    app.mouse.on(pc.EVENT_MOUSEMOVE, (event) => {{
      if (document.pointerLockElement === canvas) {{
        yaw -= event.dx * lookSpeed;
        pitch -= event.dy * lookSpeed;
        pitch = pc.math.clamp(pitch, -90, 90);

        camera.setLocalEulerAngles(pitch, yaw, 0);
      }}
    }});

    // Movement
    app.on('update', (dt) => {{
      const forward = camera.forward;
      const right = camera.right;

      if (app.keyboard.isPressed(pc.KEY_W)) {{
        camera.translate(forward.mulScalar(moveSpeed * dt));
      }}
      if (app.keyboard.isPressed(pc.KEY_S)) {{
        camera.translate(forward.mulScalar(-moveSpeed * dt));
      }}
      if (app.keyboard.isPressed(pc.KEY_A)) {{
        camera.translate(right.mulScalar(-moveSpeed * dt));
      }}
      if (app.keyboard.isPressed(pc.KEY_D)) {{
        camera.translate(right.mulScalar(moveSpeed * dt));
      }}

      // Keep camera above ground
      const pos = camera.getPosition();
      if (pos.y < 1.6) {{
        pos.y = 1.6;
        camera.setPosition(pos);
      }}

      document.getElementById('fps').textContent = `FPS: ${{Math.round(1 / dt)}}`;
      document.getElementById('drawCalls').textContent = 'WASD to move • Mouse to look';
    }});

    app.start();

    // Instructions
    setTimeout(() => {{
      alert('Click canvas to enable mouse look\\nWASD to move\\nESC to release mouse');
    }}, 100);"""

    return code


def generate_particle_system():
    """Generate particle system demo"""
    code = """    const canvas = document.getElementById('application-canvas');
    const app = new pc.Application(canvas);

    app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
    app.setCanvasResolution(pc.RESOLUTION_AUTO);
    window.addEventListener('resize', () => app.resizeCanvas());

    // Camera
    const camera = new pc.Entity('camera');
    camera.addComponent('camera', {{
      clearColor: new pc.Color(0.05, 0.05, 0.1)
    }});
    camera.setPosition(0, 5, 15);
    camera.lookAt(0, 0, 0);
    app.root.addChild(camera);

    // Particles
    const particles = [];
    const particleCount = 1000;

    for (let i = 0; i < particleCount; i++) {{
      const particle = new pc.Entity('particle');
      particle.addComponent('model', {{
        type: 'sphere',
        castShadows: false
      }});

      particle.setLocalScale(0.1, 0.1, 0.1);
      particle.setPosition(
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10
      );

      // Create colored material
      const material = new pc.StandardMaterial();
      const hue = (i / particleCount) * 360;
      material.emissive = new pc.Color().fromString(`hsl(${{hue}}, 70%, 60%)`);
      material.update();

      particle.model.meshInstances[0].material = material;

      app.root.addChild(particle);

      particles.push({{
        entity: particle,
        velocity: new pc.Vec3(
          (Math.random() - 0.5) * 2,
          (Math.random() - 0.5) * 2,
          (Math.random() - 0.5) * 2
        ),
        originalPos: particle.getPosition().clone()
      }});
    }}

    // Animation
    let time = 0;
    const bounds = 8;

    app.on('update', (dt) => {{
      time += dt;

      particles.forEach((p, i) => {{
        const pos = p.entity.getPosition();

        // Update position
        pos.add(p.velocity.clone().mulScalar(dt));

        // Bounce off bounds
        if (Math.abs(pos.x) > bounds) p.velocity.x *= -1;
        if (Math.abs(pos.y) > bounds) p.velocity.y *= -1;
        if (Math.abs(pos.z) > bounds) p.velocity.z *= -1;

        // Wave effect
        const wave = Math.sin(time * 2 + i * 0.1) * 0.5;
        pos.y += wave * dt;

        p.entity.setPosition(pos);

        // Rotate
        p.entity.rotate(dt * 50, dt * 100, dt * 150);
      }});

      document.getElementById('fps').textContent = `FPS: ${{Math.round(1 / dt)}}`;
      document.getElementById('drawCalls').textContent = `Particles: ${{particleCount}}`;
    }});

    // Rotate camera
    app.on('update', (dt) => {{
      camera.rotate(0, dt * 10, 0);
    }});

    app.start();"""

    return code


PROJECT_TYPES = {
    'basic': {
        'name': 'Basic Scene',
        'description': 'Simple scene with camera, light, and rotating cube',
        'generator': lambda: (generate_basic_scene(), "")
    },
    'physics': {
        'name': 'Physics Simulation',
        'description': 'Dynamic physics with Ammo.js and falling cubes',
        'generator': generate_physics_scene
    },
    'viewer': {
        'name': '3D Model Viewer',
        'description': 'Interactive model viewer with orbit controls',
        'generator': lambda: (generate_model_viewer(), "")
    },
    'fps': {
        'name': 'First-Person Controller',
        'description': 'WASD + mouse look first-person movement',
        'generator': lambda: (generate_first_person(), "")
    },
    'particles': {
        'name': 'Particle System',
        'description': 'Animated particle system with 1000 particles',
        'generator': lambda: (generate_particle_system(), "")
    }
}


def list_types():
    """List all available project types"""
    print("\n🎮 Available PlayCanvas Project Types:\n")
    for key, info in PROJECT_TYPES.items():
        print(f"  {key:12} - {info['name']}")
        print(f"               {info['description']}")
        print()


def generate_project(type_key, output_path):
    """Generate PlayCanvas project"""
    if type_key not in PROJECT_TYPES:
        print(f"❌ Error: Unknown type '{type_key}'")
        print(f"   Use --list to see available types")
        return False

    info = PROJECT_TYPES[type_key]

    print(f"\n🎮 Generating {info['name']}...")

    # Generate code
    result = info['generator']()
    if isinstance(result, tuple):
        code, additional_scripts = result
    else:
        code, additional_scripts = result, ""

    # Create HTML
    html = create_html_template(info['name'], code, additional_scripts)

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
    print("  🎮 PlayCanvas Project Generator")
    print("="*60)

    print("\nSelect project type:\n")
    types_list = list(PROJECT_TYPES.keys())
    for i, key in enumerate(types_list, 1):
        info = PROJECT_TYPES[key]
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
    default_name = f"playcanvas_{type_key}.html"
    output_name = input(f"\nOutput filename [{default_name}]: ").strip()
    if not output_name:
        output_name = default_name

    output_path = Path.cwd() / output_name

    return generate_project(type_key, output_path)


def main():
    parser = argparse.ArgumentParser(
        description='Generate PlayCanvas project boilerplate',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--type',
        choices=list(PROJECT_TYPES.keys()),
        help='Project type to generate'
    )

    parser.add_argument(
        '--output',
        default='playcanvas_project.html',
        help='Output HTML file path (default: playcanvas_project.html)'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available project types'
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
    success = generate_project(args.type, args.output)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

```


===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/assets/examples/README.md =====

# PlayCanvas Examples

Comprehensive collection of PlayCanvas examples, patterns, and use cases.

---

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [3D Graphics](#3d-graphics)
3. [Physics & Interaction](#physics--interaction)
4. [Animation](#animation)
5. [User Interface](#user-interface)
6. [Audio](#audio)
7. [Performance](#performance)
8. [Integration Patterns](#integration-patterns)

---

## Basic Examples

### 1. Hello Cube

Minimal PlayCanvas scene with rotating cube:

```javascript
const canvas = document.getElementById('canvas');
const app = new pc.Application(canvas);

app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
app.setCanvasResolution(pc.RESOLUTION_AUTO);

// Camera
const camera = new pc.Entity('camera');
camera.addComponent('camera', {
    clearColor: new pc.Color(0.2, 0.3, 0.4)
});
camera.setPosition(0, 0, 5);
app.root.addChild(camera);

// Light
const light = new pc.Entity('light');
light.addComponent('light');
light.setEulerAngles(45, 45, 0);
app.root.addChild(light);

// Cube
const cube = new pc.Entity('cube');
cube.addComponent('model', { type: 'box' });
app.root.addChild(cube);

// Rotate cube
app.on('update', (dt) => {
    cube.rotate(10 * dt, 20 * dt, 30 * dt);
});

app.start();
```

---

### 2. Multiple Objects

Creating multiple objects in a scene:

```javascript
const shapes = ['box', 'sphere', 'cylinder', 'cone', 'capsule'];
const colors = [
    new pc.Color(1, 0, 0),  // Red
    new pc.Color(0, 1, 0),  // Green
    new pc.Color(0, 0, 1),  // Blue
    new pc.Color(1, 1, 0),  // Yellow
    new pc.Color(1, 0, 1)   // Magenta
];

shapes.forEach((shape, i) => {
    const entity = new pc.Entity(shape);
    entity.addComponent('model', { type: shape });

    // Position in grid
    entity.setPosition((i - 2) * 2, 0, 0);

    // Create material
    const material = new pc.StandardMaterial();
    material.diffuse = colors[i];
    material.update();
    entity.model.material = material;

    app.root.addChild(entity);
});
```

---

### 3. Loading 3D Models

Load GLTF/GLB models:

```javascript
// Create asset for model
const asset = new pc.Asset('model', 'container', {
    url: 'path/to/model.glb'
});

app.assets.add(asset);

// Load asset
app.assets.load(asset);

asset.ready((asset) => {
    const entity = asset.resource.instantiateRenderEntity();
    entity.setPosition(0, 0, 0);
    app.root.addChild(entity);
});

asset.on('error', (err) => {
    console.error('Failed to load model:', err);
});
```

---

## 3D Graphics

### 1. Materials & Textures

PBR material with textures:

```javascript
// Create material
const material = new pc.StandardMaterial();

// Diffuse (albedo) texture
const diffuseAsset = new pc.Asset('diffuse', 'texture', {
    url: 'textures/albedo.jpg'
});
app.assets.add(diffuseAsset);
app.assets.load(diffuseAsset);

diffuseAsset.ready(() => {
    material.diffuseMap = diffuseAsset.resource;
    material.update();
});

// Normal map
const normalAsset = new pc.Asset('normal', 'texture', {
    url: 'textures/normal.jpg'
});
app.assets.add(normalAsset);
app.assets.load(normalAsset);

normalAsset.ready(() => {
    material.normalMap = normalAsset.resource;
    material.update();
});

// Metalness
material.metalness = 0.7;
material.gloss = 0.8;

// Apply to entity
entity.model.material = material;
```

---

### 2. Dynamic Lighting

Multiple light types:

```javascript
// Directional Light (Sun)
const sun = new pc.Entity('sun');
sun.addComponent('light', {
    type: 'directional',
    color: new pc.Color(1, 1, 0.9),
    intensity: 1.5,
    castShadows: true,
    shadowBias: 0.2,
    shadowDistance: 40
});
sun.setEulerAngles(45, 30, 0);
app.root.addChild(sun);

// Point Light
const pointLight = new pc.Entity('pointLight');
pointLight.addComponent('light', {
    type: 'point',
    color: new pc.Color(1, 0, 0),
    intensity: 1,
    range: 10,
    castShadows: false
});
pointLight.setPosition(0, 2, 0);
app.root.addChild(pointLight);

// Spot Light
const spotLight = new pc.Entity('spotLight');
spotLight.addComponent('light', {
    type: 'spot',
    color: new pc.Color(0, 1, 0),
    intensity: 1,
    range: 15,
    innerConeAngle: 20,
    outerConeAngle: 30,
    castShadows: true
});
spotLight.setPosition(5, 5, 0);
spotLight.lookAt(0, 0, 0);
app.root.addChild(spotLight);
```

---

### 3. Camera Effects

Post-processing and camera effects:

```javascript
// Depth of Field
camera.camera.enablePostEffects = true;

// Create depth of field effect (requires custom script)
const dofScript = camera.script.create('depthOfField', {
    attributes: {
        focusDistance: 10,
        aperture: 0.5,
        maxBlur: 1.0
    }
});

// Camera shake effect
function cameraShake(intensity, duration) {
    const startTime = Date.now();
    const originalPos = camera.getPosition().clone();

    const shakeInterval = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000;

        if (elapsed >= duration) {
            camera.setPosition(originalPos);
            clearInterval(shakeInterval);
            return;
        }

        const shakeAmount = intensity * (1 - elapsed / duration);
        const x = originalPos.x + (Math.random() - 0.5) * shakeAmount;
        const y = originalPos.y + (Math.random() - 0.5) * shakeAmount;
        const z = originalPos.z + (Math.random() - 0.5) * shakeAmount;

        camera.setPosition(x, y, z);
    }, 16);
}

// Usage
cameraShake(0.5, 0.5);  // intensity, duration
```

---

## Physics & Interaction

### 1. Basic Physics

Rigidbody and collision setup:

```javascript
// Dynamic rigidbody (falls with gravity)
const dynamicBox = new pc.Entity('dynamicBox');
dynamicBox.addComponent('model', { type: 'box' });
dynamicBox.addComponent('rigidbody', {
    type: 'dynamic',
    mass: 1,
    friction: 0.5,
    restitution: 0.5  // Bounciness
});
dynamicBox.addComponent('collision', {
    type: 'box',
    halfExtents: new pc.Vec3(0.5, 0.5, 0.5)
});
dynamicBox.setPosition(0, 5, 0);
app.root.addChild(dynamicBox);

// Static ground
const ground = new pc.Entity('ground');
ground.addComponent('model', { type: 'plane' });
ground.addComponent('rigidbody', {
    type: 'static'
});
ground.addComponent('collision', {
    type: 'box',
    halfExtents: new pc.Vec3(10, 0.1, 10)
});
ground.setLocalScale(20, 1, 20);
app.root.addChild(ground);
```

---

### 2. Raycasting & Object Picking

Pick objects with mouse:

```javascript
function pickObject(screenX, screenY) {
    const camera = app.root.findByName('Camera');

    // Convert screen to world coordinates
    const worldPos = camera.camera.screenToWorld(
        screenX,
        screenY,
        camera.camera.farClip
    );

    const from = camera.getPosition();
    const to = worldPos;

    // Raycast
    const result = app.systems.rigidbody.raycastFirst(from, to);

    if (result) {
        console.log('Hit:', result.entity.name);
        return result.entity;
    }

    return null;
}

// Mouse click handler
app.mouse.on(pc.EVENT_MOUSEDOWN, (event) => {
    const picked = pickObject(event.x, event.y);
    if (picked) {
        // Do something with picked entity
        picked.rigidbody.applyImpulse(0, 5, 0);
    }
});
```

---

### 3. Character Controller

WASD character movement:

```javascript
var CharacterController = pc.createScript('characterController');

CharacterController.attributes.add('speed', {
    type: 'number',
    default: 5.0
});

CharacterController.prototype.initialize = function() {
    this.moveDirection = new pc.Vec3();
};

CharacterController.prototype.update = function(dt) {
    const keyboard = this.app.keyboard;

    // Get camera direction
    const camera = this.app.root.findByName('Camera');
    const forward = camera.forward.clone();
    const right = camera.right.clone();

    // Flatten to horizontal
    forward.y = 0;
    forward.normalize();
    right.y = 0;
    right.normalize();

    // Calculate movement
    this.moveDirection.set(0, 0, 0);

    if (keyboard.isPressed(pc.KEY_W)) {
        this.moveDirection.add(forward);
    }
    if (keyboard.isPressed(pc.KEY_S)) {
        this.moveDirection.sub(forward);
    }
    if (keyboard.isPressed(pc.KEY_A)) {
        this.moveDirection.sub(right);
    }
    if (keyboard.isPressed(pc.KEY_D)) {
        this.moveDirection.add(right);
    }

    // Apply movement
    if (this.moveDirection.length() > 0) {
        this.moveDirection.normalize();
        this.moveDirection.scale(this.speed * dt);

        const pos = this.entity.getPosition();
        pos.add(this.moveDirection);
        this.entity.setPosition(pos);

        // Rotate to face movement direction
        const angle = Math.atan2(this.moveDirection.x, this.moveDirection.z) * pc.math.RAD_TO_DEG;
        this.entity.setEulerAngles(0, angle, 0);
    }
};
```

---

## Animation

### 1. Property Animation (Tween)

Animate entity properties:

```javascript
// Tween helper
function tween(entity, property, from, to, duration, easing = 'linear') {
    const startTime = Date.now();

    const easingFuncs = {
        linear: t => t,
        easeIn: t => t * t,
        easeOut: t => t * (2 - t),
        easeInOut: t => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t
    };

    const easingFunc = easingFuncs[easing] || easingFuncs.linear;

    const animate = () => {
        const elapsed = (Date.now() - startTime) / 1000;
        const t = Math.min(elapsed / duration, 1);
        const eased = easingFunc(t);

        const value = from + (to - from) * eased;

        if (property === 'x' || property === 'y' || property === 'z') {
            const pos = entity.getPosition();
            pos[property] = value;
            entity.setPosition(pos);
        }

        if (t < 1) {
            requestAnimationFrame(animate);
        }
    };

    animate();
}

// Usage
tween(entity, 'y', 0, 5, 2, 'easeInOut');  // Move up over 2 seconds
```

---

### 2. Skeletal Animation

Animate 3D character models:

```javascript
// Load model with animations
const modelAsset = new pc.Asset('character', 'container', {
    url: 'models/character.glb'
});

app.assets.add(modelAsset);
app.assets.load(modelAsset);

modelAsset.ready((asset) => {
    const entity = asset.resource.instantiateRenderEntity();

    // Add animation component
    entity.addComponent('anim', {
        activate: true
    });

    // Get animation clips
    const animations = asset.resource.animations;

    // Create animation state graph
    const animStateGraph = {
        layers: [
            {
                name: 'locomotion',
                states: [
                    { name: 'idle', speed: 1.0 },
                    { name: 'walk', speed: 1.0 },
                    { name: 'run', speed: 1.0 }
                ],
                transitions: [
                    { from: 'idle', to: 'walk', duration: 0.2 },
                    { from: 'walk', to: 'run', duration: 0.2 },
                    { from: 'run', to: 'idle', duration: 0.3 }
                ]
            }
        ]
    };

    // Load animation clips
    animations.forEach(anim => {
        entity.anim.assignAnimation(anim.name, anim.resource);
    });

    // Play animation
    entity.anim.setBoolean('walk', true);

    app.root.addChild(entity);
});
```

---

### 3. Particle Systems

Create particle effects:

```javascript
// Particle system entity
const particles = new pc.Entity('particles');

// Add particle system component
particles.addComponent('particlesystem', {
    numParticles: 100,
    lifetime: 2,
    rate: 0.05,
    emitterShape: pc.EMITTERSHAPE_SPHERE,
    emitterRadius: 0.5,

    // Velocity
    velocityGraph: new pc.CurveSet([
        [0, 0.1],
        [1, 0.5]
    ]),

    // Size
    scaleGraph: new pc.CurveSet([
        [0, 0.1],
        [0.5, 0.5],
        [1, 0.1]
    ]),

    // Color
    colorGraph: new pc.CurveSet([
        [0, 1, 1, 0, 0],  // Red at start
        [0.5, 1, 0.5, 0, 0],  // Orange
        [1, 0.2, 0, 0, 0]  // Dark at end
    ]),

    // Alpha
    alphaGraph: new pc.CurveSet([
        [0, 0],
        [0.2, 1],
        [0.8, 1],
        [1, 0]
    ]),

    blendType: pc.BLEND_ADDITIVE,
    depthWrite: false,
    lighting: false
});

particles.setPosition(0, 2, 0);
app.root.addChild(particles);
```

---

## User Interface

### 1. 2D UI Elements

Create screen-space UI:

```javascript
// Create screen entity (UI root)
const screen = new pc.Entity('screen');
screen.addComponent('screen', {
    referenceResolution: new pc.Vec2(1280, 720),
    scaleBlend: 0.5,
    scaleMode: pc.SCALEMODE_BLEND,
    screenSpace: true
});
app.root.addChild(screen);

// Create button
const button = new pc.Entity('button');
button.addComponent('element', {
    anchor: new pc.Vec4(0.5, 0.5, 0.5, 0.5),
    pivot: new pc.Vec2(0.5, 0.5),
    width: 200,
    height: 50,
    type: pc.ELEMENTTYPE_IMAGE,
    color: new pc.Color(0.2, 0.6, 1),
    useInput: true
});

// Button text
const buttonText = new pc.Entity('buttonText');
buttonText.addComponent('element', {
    anchor: new pc.Vec4(0.5, 0.5, 0.5, 0.5),
    pivot: new pc.Vec2(0.5, 0.5),
    fontSize: 24,
    text: 'Click Me',
    type: pc.ELEMENTTYPE_TEXT,
    color: new pc.Color(1, 1, 1)
});

button.addChild(buttonText);
screen.addChild(button);

// Button click handler
button.element.on('click', () => {
    console.log('Button clicked!');
});
```

---

### 2. Health Bar

Dynamic UI health bar:

```javascript
// Health bar background
const healthBg = new pc.Entity('healthBg');
healthBg.addComponent('element', {
    anchor: new pc.Vec4(0, 1, 0, 1),
    pivot: new pc.Vec2(0, 1),
    margin: new pc.Vec4(20, 20, 0, 0),
    width: 200,
    height: 20,
    type: pc.ELEMENTTYPE_IMAGE,
    color: new pc.Color(0.2, 0.2, 0.2)
});

// Health bar fill
const healthFill = new pc.Entity('healthFill');
healthFill.addComponent('element', {
    anchor: new pc.Vec4(0, 0, 0, 1),
    pivot: new pc.Vec2(0, 0.5),
    width: 200,
    height: 16,
    type: pc.ELEMENTTYPE_IMAGE,
    color: new pc.Color(0, 1, 0)
});

healthBg.addChild(healthFill);
screen.addChild(healthBg);

// Update health
function setHealth(percent) {
    healthFill.element.width = 200 * (percent / 100);

    // Color based on health
    if (percent > 50) {
        healthFill.element.color = new pc.Color(0, 1, 0);  // Green
    } else if (percent > 25) {
        healthFill.element.color = new pc.Color(1, 1, 0);  // Yellow
    } else {
        healthFill.element.color = new pc.Color(1, 0, 0);  // Red
    }
}

// Usage
setHealth(75);
```

---

## Audio

### 1. Background Music

Load and play audio:

```javascript
// Create audio asset
const musicAsset = new pc.Asset('music', 'audio', {
    url: 'audio/music.mp3'
});

app.assets.add(musicAsset);
app.assets.load(musicAsset);

// Create audio entity
const music = new pc.Entity('music');
music.addComponent('sound');

musicAsset.ready(() => {
    music.sound.addSlot('music', {
        asset: musicAsset,
        autoPlay: true,
        loop: true,
        volume: 0.5
    });
});

app.root.addChild(music);

// Control playback
music.sound.play('music');
music.sound.pause('music');
music.sound.stop('music');
music.sound.slot('music').volume = 0.7;
```

---

### 2. 3D Positional Audio

Spatial audio effects:

```javascript
// 3D sound effect
const soundEntity = new pc.Entity('sound');
soundEntity.addComponent('sound', {
    positional: true,
    distanceModel: pc.DISTANCE_INVERSE,
    refDistance: 1,
    maxDistance: 20,
    rollOffFactor: 1
});

soundEntity.setPosition(5, 0, 0);

const soundAsset = new pc.Asset('effect', 'audio', {
    url: 'audio/explosion.mp3'
});

app.assets.add(soundAsset);
app.assets.load(soundAsset);

soundAsset.ready(() => {
    soundEntity.sound.addSlot('effect', {
        asset: soundAsset,
        autoPlay: false,
        loop: false,
        volume: 1.0
    });
});

app.root.addChild(soundEntity);

// Play sound at position
soundEntity.sound.play('effect');
```

---

## Performance

### 1. Object Pooling

Reuse objects instead of creating/destroying:

```javascript
class ObjectPool {
    constructor(app, template, initialSize = 10) {
        this.app = app;
        this.template = template;
        this.available = [];
        this.active = [];

        // Pre-create objects
        for (let i = 0; i < initialSize; i++) {
            this.createObject();
        }
    }

    createObject() {
        const obj = this.template.clone();
        obj.enabled = false;
        this.app.root.addChild(obj);
        this.available.push(obj);
        return obj;
    }

    spawn(position) {
        let obj = this.available.pop();

        if (!obj) {
            obj = this.createObject();
        }

        obj.enabled = true;
        obj.setPosition(position);
        this.active.push(obj);

        return obj;
    }

    despawn(obj) {
        obj.enabled = false;
        const index = this.active.indexOf(obj);
        if (index > -1) {
            this.active.splice(index, 1);
            this.available.push(obj);
        }
    }

    reset() {
        this.active.forEach(obj => {
            obj.enabled = false;
            this.available.push(obj);
        });
        this.active = [];
    }
}

// Usage
const bulletTemplate = new pc.Entity('bullet');
bulletTemplate.addComponent('model', { type: 'sphere' });
bulletTemplate.setLocalScale(0.2, 0.2, 0.2);

const bulletPool = new ObjectPool(app, bulletTemplate, 50);

// Spawn bullet
const bullet = bulletPool.spawn(new pc.Vec3(0, 1, 0));

// Despawn after 2 seconds
setTimeout(() => {
    bulletPool.despawn(bullet);
}, 2000);
```

---

### 2. LOD (Level of Detail)

Optimize rendering with LOD:

```javascript
// Create entity with multiple LOD levels
const entity = new pc.Entity('lodEntity');
entity.addComponent('model', { type: 'asset', asset: highPolyModel });

// Setup LOD levels
const meshInstances = entity.model.meshInstances;

meshInstances.forEach(meshInstance => {
    // Define LOD levels
    meshInstance.lodDistances = [10, 50, 100];

    // High detail (< 10 units)
    meshInstance.lod0 = highPolyMesh;

    // Medium detail (10-50 units)
    meshInstance.lod1 = mediumPolyMesh;

    // Low detail (50-100 units)
    meshInstance.lod2 = lowPolyMesh;

    // Very low detail (> 100 units)
    meshInstance.lod3 = veryLowPolyMesh;
});
```

---

## Integration Patterns

### 1. React Integration

Use PlayCanvas in React:

```javascript
import React, { useEffect, useRef } from 'react';
import * as pc from 'playcanvas';

function PlayCanvasComponent() {
    const canvasRef = useRef(null);
    const appRef = useRef(null);

    useEffect(() => {
        // Initialize PlayCanvas
        const app = new pc.Application(canvasRef.current);
        app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
        app.setCanvasResolution(pc.RESOLUTION_AUTO);

        // Setup scene
        setupScene(app);

        app.start();
        appRef.current = app;

        // Cleanup
        return () => {
            app.destroy();
        };
    }, []);

    return <canvas ref={canvasRef} />;
}

function setupScene(app) {
    // Add camera, lights, objects...
}

export default PlayCanvasComponent;
```

---

### 2. Three.js Migration

Migrate from Three.js concepts:

```javascript
// Three.js
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);

// PlayCanvas equivalent
const entity = new pc.Entity('box');
entity.addComponent('model', { type: 'box' });

const material = new pc.StandardMaterial();
material.diffuse = new pc.Color(1, 0, 0);
material.update();
entity.model.material = material;

app.root.addChild(entity);
```

---

### 3. WebXR Integration

VR/AR with WebXR:

```javascript
// Enable XR
if (app.xr.supported) {
    // VR mode
    const enterVRButton = document.getElementById('enterVR');

    enterVRButton.addEventListener('click', () => {
        camera.camera.startXr(pc.XRTYPE_VR, pc.XRSPACE_LOCAL);
    });

    // AR mode
    const enterARButton = document.getElementById('enterAR');

    enterARButton.addEventListener('click', () => {
        camera.camera.startXr(pc.XRTYPE_AR, pc.XRSPACE_LOCALFLOOR);
    });

    // XR input
    app.xr.input.on('select', (inputSource) => {
        console.log('XR input selected');
    });
}
```

---

## Resources

- **Official Examples**: https://playcanvas.github.io
- **API Docs**: https://api.playcanvas.com
- **Tutorials**: https://developer.playcanvas.com/tutorials
- **Forum**: https://forum.playcanvas.com

---

## License

Examples provided for educational purposes. PlayCanvas Engine is MIT licensed.



===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/assets/starter_playcanvas/README.md =====

# PlayCanvas Starter Template

Production-ready PlayCanvas starter project with best practices, utilities, and interactive demo.

---

## Features

✨ **Complete Setup**
- PlayCanvas engine integration
- Camera orbit controls
- Input management system
- Performance stats display
- Responsive UI overlay
- Mobile-friendly touch controls

🎨 **Demo Scene**
- 5 interactive 3D shapes
- Dynamic lighting (directional + ambient)
- PBR materials with varied metalness
- Smooth animations
- Ground plane with shadows

⚡ **Performance**
- Optimized rendering
- Real-time FPS, draw calls, triangle count
- Canvas auto-resizing
- Anti-aliasing enabled

📱 **Responsive**
- Desktop (mouse + keyboard)
- Mobile (touch + pinch-to-zoom)
- Tablet support

---

## Quick Start

### 1. Download Template

```bash
# Copy starter template to your project
cp -r .gemini/skills/playcanvas-engine/assets/starter_playcanvas ./my-playcanvas-project
cd my-playcanvas-project
```

### 2. Serve Locally

**Using Python:**
```bash
python3 -m http.server 8000
```

**Using Node.js:**
```bash
npx http-server -p 8000
```

**Using PHP:**
```bash
php -S localhost:8000
```

### 3. Open in Browser

Navigate to `http://localhost:8000`

---

## Project Structure

```
starter_playcanvas/
├── index.html              # Main HTML file
├── styles.css              # UI styling
├── scripts/
│   ├── app.js             # Main application logic
│   ├── camera-controller.js  # Orbit camera
│   └── input-manager.js   # Input handling
└── README.md              # This file
```

---

## Usage Guide

### Camera Controls

**Desktop:**
- **Left-click + drag**: Rotate camera
- **Right-click + drag**: Rotate camera
- **Scroll wheel**: Zoom in/out

**Mobile:**
- **Single finger drag**: Rotate camera
- **Pinch gesture**: Zoom in/out

### UI Controls

**Toggle Stats**: Show/hide performance statistics
**Wireframe**: Toggle wireframe rendering (console only)
**Reset Camera**: Return camera to initial position

---

## Customization

### Change Scene Background

Edit `app.js`:

```javascript
camera.addComponent('camera', {
    clearColor: new pc.Color(0.1, 0.1, 0.15), // RGB values 0-1
    farClip: 100
});
```

### Add New Objects

```javascript
// Create entity
const cube = new pc.Entity('MyCube');

// Add model component
cube.addComponent('model', {
    type: 'box'  // box, sphere, cylinder, cone, capsule, plane
});

// Position it
cube.setPosition(0, 2, 0);

// Create material
const material = new pc.StandardMaterial();
material.diffuse = new pc.Color(1, 0, 0);  // Red
material.metalness = 0.5;
material.gloss = 0.7;
material.update();
cube.model.material = material;

// Add to scene
app.root.addChild(cube);
```

### Load 3D Models

```javascript
// Load GLTF/GLB model
app.assets.loadFromUrl('model.glb', 'container', (err, asset) => {
    if (err) {
        console.error('Failed to load model:', err);
        return;
    }

    const entity = asset.resource.instantiateRenderEntity();
    entity.setPosition(0, 0, 0);
    app.root.addChild(entity);
});
```

### Add Physics

```javascript
// Add rigidbody component
entity.addComponent('rigidbody', {
    type: 'dynamic',  // dynamic, static, kinematic
    mass: 1,
    friction: 0.5,
    restitution: 0.3
});

// Add collision component
entity.addComponent('collision', {
    type: 'box'  // box, sphere, capsule, cylinder, mesh
});
```

### Custom Scripts

Create script component:

```javascript
var MyScript = pc.createScript('myScript');

MyScript.prototype.initialize = function() {
    console.log('Script initialized');
};

MyScript.prototype.update = function(dt) {
    // Update logic
    this.entity.rotate(0, 10 * dt, 0);
};

// Attach to entity
entity.addComponent('script');
entity.script.create('myScript');
```

---

## Input Manager API

The included `InputManager` class provides centralized input handling:

```javascript
// Access input manager (already instantiated in app.js)
const input = inputManager;

// Keyboard
if (input.isKeyPressed(pc.KEY_SPACE)) {
    console.log('Space pressed');
}

// WASD input
const moveVector = input.getWASDInput();  // Returns Vec2

// Mouse
const mousePos = input.getMousePosition();
const mouseDelta = input.getMouseDelta();
const wheel = input.getMouseWheel();

// Raycast from mouse
const camera = app.root.findByName('Camera');
const ray = input.getMouseRay(camera);
if (ray) {
    const result = input.raycast(ray.origin, ray.end);
    if (result) {
        console.log('Hit:', result.entity.name);
    }
}

// Touch
const touchCount = input.getTouchCount();
const touch = input.getTouch(0);  // First touch
```

---

## Camera Controller API

The `CameraController` class provides orbit camera functionality:

```javascript
// Access camera controller (already instantiated in app.js)
const camera = cameraController;

// Set target
camera.setTarget(new pc.Vec3(0, 5, 0));

// Or focus on entity
const player = app.root.findByName('Player');
camera.focusOn(player, 10);  // entity, distance

// Set rotation
camera.setYaw(45);    // Horizontal rotation
camera.setPitch(30);  // Vertical rotation

// Set distance
camera.setDistance(15);

// Animate camera
camera.animateTo(
    90,    // yaw
    20,    // pitch
    12,    // distance
    2.0    // duration in seconds
);

// Reset to initial position
camera.reset();

// Get camera vectors
const forward = camera.getForwardVector();
const right = camera.getRightVector();
const up = camera.getUpVector();
```

---

## Performance Optimization

### Reduce Draw Calls

```javascript
// Batch static objects with same material
const material = new pc.StandardMaterial();

entities.forEach(entity => {
    entity.model.material = material;  // Share material
});
```

### Use LOD (Level of Detail)

```javascript
// Add LOD levels
entity.addComponent('model', {
    type: 'asset',
    asset: highPolyModel
});

// Configure LOD
entity.model.meshInstances[0].lod = {
    levels: [
        { distance: 10, mesh: highPolyMesh },
        { distance: 50, mesh: lowPolyMesh }
    ]
};
```

### Frustum Culling

Frustum culling is enabled by default. Ensure entities have proper bounding boxes:

```javascript
// Update bounding box after scale changes
entity.model.meshInstances[0]._aabb.compute();
```

### Texture Compression

Use compressed texture formats for production:
- **Desktop**: DXT (DDS)
- **iOS**: PVR
- **Android**: ETC
- **Universal**: Basis

---

## Deployment

### Build for Production

1. **Minify JavaScript**:
```bash
# Using terser
npx terser scripts/app.js -o scripts/app.min.js
npx terser scripts/camera-controller.js -o scripts/camera-controller.min.js
npx terser scripts/input-manager.js -o scripts/input-manager.min.js
```

2. **Update index.html** to use minified files

3. **Compress Assets**:
- Optimize textures (use tools like TinyPNG)
- Compress 3D models (use glTF-Pipeline)
- Enable gzip on server

### Hosting Options

**GitHub Pages:**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main

# Enable GitHub Pages in repo settings
```

**Netlify:**
- Drag & drop project folder to Netlify
- Or connect GitHub repo for auto-deploy

**Vercel:**
```bash
npm i -g vercel
vercel
```

**AWS S3:**
- Create S3 bucket
- Enable static website hosting
- Upload files
- Configure CloudFront CDN (optional)

---

## Browser Compatibility

**Supported Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**WebGL Requirements:**
- WebGL 2.0 (recommended)
- WebGL 1.0 (fallback)

**Mobile:**
- iOS Safari 14+
- Chrome Mobile 90+
- Samsung Internet 14+

---

## Troubleshooting

**Canvas not filling window:**
```javascript
// Ensure these are called
app.setCanvasFillMode(pc.FILLMODE_FILL_WINDOW);
app.setCanvasResolution(pc.RESOLUTION_AUTO);
```

**Assets not loading (CORS errors):**
- Serve from local server (not file://)
- Check CORS headers on asset server

**Poor performance on mobile:**
```javascript
// Reduce resolution for mobile
if (isMobile()) {
    app.graphicsDevice.maxPixelRatio = 1;
}

// Disable shadows
light.light.castShadows = false;
```

**Touch controls not working:**
```javascript
// Ensure touch device is initialized
app.touch = new pc.TouchDevice(canvas);
```

---

## Next Steps

1. **Add More Objects**: Experiment with different shapes and materials
2. **Load Models**: Import your own 3D models (GLTF/GLB)
3. **Add Physics**: Create interactive physics simulations
4. **Custom Scripts**: Write gameplay logic with script components
5. **UI Elements**: Add 2D UI with element components
6. **Particles**: Create visual effects with particle systems
7. **Audio**: Add sound effects and music

---

## Resources

- **PlayCanvas Engine**: https://github.com/playcanvas/engine
- **API Documentation**: https://api.playcanvas.com
- **Examples**: https://playcanvas.github.io
- **Forum**: https://forum.playcanvas.com
- **Editor**: https://playcanvas.com (for visual scene editing)

---

## License

This starter template is provided as-is for educational and commercial use.

PlayCanvas Engine is licensed under MIT License.

---

## Support

For issues or questions:
1. Check the [PlayCanvas Forum](https://forum.playcanvas.com)
2. Review [API documentation](https://api.playcanvas.com)
3. Search [examples](https://playcanvas.github.io)

---

Happy coding! 🚀



===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/assets/starter_playcanvas/index.html =====

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>PlayCanvas Starter Project</title>
    <link rel="stylesheet" href="styles.css">

    <!-- PlayCanvas Engine -->
    <script src="https://code.playcanvas.com/playcanvas-stable.min.js"></script>
</head>
<body>
    <!-- Canvas Container -->
    <div id="app">
        <canvas id="application-canvas"></canvas>

        <!-- Loading Screen -->
        <div id="loading-screen">
            <div class="spinner"></div>
            <p>Loading...</p>
        </div>

        <!-- UI Overlay -->
        <div id="ui-overlay">
            <div id="info-panel">
                <h1>PlayCanvas Starter</h1>
                <p>Use mouse to rotate camera • Scroll to zoom</p>
            </div>

            <div id="stats-panel">
                <div class="stat">
                    <span class="label">FPS:</span>
                    <span id="fps">--</span>
                </div>
                <div class="stat">
                    <span class="label">Draw Calls:</span>
                    <span id="draw-calls">--</span>
                </div>
                <div class="stat">
                    <span class="label">Triangles:</span>
                    <span id="triangles">--</span>
                </div>
            </div>

            <div id="controls-panel">
                <button id="toggle-stats">Toggle Stats</button>
                <button id="toggle-wireframe">Wireframe</button>
                <button id="reset-camera">Reset Camera</button>
            </div>
        </div>
    </div>

    <!-- Application Scripts -->
    <script src="scripts/input-manager.js"></script>
    <script src="scripts/camera-controller.js"></script>
    <script src="scripts/app.js"></script>

    <script>
        // Initialize application when DOM is ready
        window.addEventListener('DOMContentLoaded', () => {
            initApp();
        });
    </script>
</body>
</html>

```


===== FILE: plugins/individual/playcanvas-engine/skills/playcanvas-engine/assets/starter_playcanvas/styles.css =====

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
    background: #000;
    color: #fff;
}

/* App Container */
#app {
    position: relative;
    width: 100%;
    height: 100%;
}

/* Canvas */
#application-canvas {
    display: block;
    width: 100%;
    height: 100%;
    touch-action: none;
}

/* Loading Screen */
#loading-screen {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    z-index: 1000;
    transition: opacity 0.5s ease;
}

#loading-screen.hidden {
    opacity: 0;
    pointer-events: none;
}

.spinner {
    width: 50px;
    height: 50px;
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

#loading-screen p {
    margin-top: 20px;
    font-size: 18px;
    letter-spacing: 2px;
    text-transform: uppercase;
    opacity: 0.8;
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
    background: rgba(0, 0, 0, 0.7);
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
    line-height: 1.5;
}

/* Stats Panel */
#stats-panel {
    position: absolute;
    top: 20px;
    right: 20px;
    background: rgba(0, 0, 0, 0.7);
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

/* Performance Indicator */
.performance-warning {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(255, 100, 100, 0.9);
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    z-index: 100;
}

.performance-warning.hidden {
    display: none;
}

```


# Skill: aframe-webxr


===== FILE: plugins/individual/aframe-webxr/skills/aframe-webxr/SKILL.md =====

---
name: aframe-webxr
description: Declarative web framework for building browser-based 3D, VR, and AR experiences using HTML and entity-component architecture. Use this skill when creating WebXR applications, VR experiences, AR experiences, 360-degree media viewers, or immersive web content with minimal JavaScript. Triggers on tasks involving A-Frame, WebXR, VR development, AR development, entity-component-system, declarative 3D, or HTML-based 3D scenes. Built on Three.js with accessible HTML-first approach.
---

# A-Frame WebXR Skill

## When to Use This Skill
- Build VR/AR experiences with minimal JavaScript
- Create cross-platform WebXR applications (desktop, mobile, headset)
- Prototype 3D scenes quickly with HTML primitives
- Implement VR controller interactions
- Add 3D content to web pages declaratively
- Build 360° image/video experiences
- Develop AR experiences with hit testing

## Core Concepts

### 1. Entity-Component-System (ECS)

A-Frame uses an entity-component-system architecture where:
- **Entities** are containers (like `<div>` in HTML)
- **Components** add functionality/appearance to entities
- **Systems** provide global functionality

```html
<!-- Entity with components -->
<a-entity
  geometry="primitive: box; width: 2"
  material="color: red; metalness: 0.5"
  position="0 1.5 -3"
  rotation="0 45 0">
</a-entity>
```

**Primitives** are shortcuts for common entity + component combinations:

```html
<!-- Primitive (shorthand) -->
<a-box color="red" position="0 1.5 -3" rotation="0 45 0" width="2"></a-box>

<!-- Equivalent entity-component form -->
<a-entity
  geometry="primitive: box; width: 2"
  material="color: red"
  position="0 1.5 -3"
  rotation="0 45 0">
</a-entity>
```

### 2. Scene Setup

Every A-Frame app starts with `<a-scene>`:

```html
<!DOCTYPE html>
<html>
  <head>
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
  </head>
  <body>
    <a-scene>
      <!-- Entities go here -->
      <a-box position="-1 0.5 -3" color="#4CC3D9"></a-box>
      <a-sphere position="0 1.25 -5" radius="1.25" color="#EF2D5E"></a-sphere>
      <a-cylinder position="1 0.75 -3" radius="0.5" height="1.5" color="#FFC65D"></a-cylinder>
      <a-plane position="0 0 -4" rotation="-90 0 0" width="4" height="4" color="#7BC8A4"></a-plane>
      <a-sky color="#ECECEC"></a-sky>
    </a-scene>
  </body>
</html>
```

The scene automatically injects:
- Default camera (position: `0 1.6 0`)
- Look controls (mouse drag)
- WASD controls (keyboard movement)

### 3. Camera Systems

**Default Camera** (auto-injected if none specified):

```html
<a-entity camera="active: true" look-controls wasd-controls position="0 1.6 0"></a-entity>
```

**Custom Camera**:

```html
<a-camera position="0 2 5" look-controls wasd-controls="acceleration: 50"></a-camera>
```

**Camera Rig** (for independent movement and rotation):

```html
<a-entity id="rig" position="0 0 0">
  <!-- Camera for head tracking -->
  <a-camera look-controls></a-camera>

  <!-- Movement applied to rig, not camera -->
</a-entity>
```

**VR Camera Rig with Controllers**:

```html
<a-entity id="rig" position="0 0 0">
  <!-- Camera at eye level -->
  <a-camera position="0 1.6 0"></a-camera>

  <!-- Left hand controller -->
  <a-entity
    hand-controls="hand: left"
    laser-controls="hand: left">
  </a-entity>

  <!-- Right hand controller -->
  <a-entity
    hand-controls="hand: right"
    laser-controls="hand: right">
  </a-entity>
</a-entity>
```

### 4. Lighting

**Ambient Light** (global illumination):

```html
<a-entity light="type: ambient; color: #BBB; intensity: 0.5"></a-entity>
```

**Directional Light** (like sunlight):

```html
<a-entity light="type: directional; color: #FFF; intensity: 0.8" position="1 2 1"></a-entity>
```

**Point Light** (radiates in all directions):

```html
<a-entity light="type: point; color: #F00; intensity: 2; distance: 50" position="0 3 0"></a-entity>
```

**Spot Light** (cone-shaped beam):

```html
<a-entity light="type: spot; angle: 45; intensity: 1.5" position="0 5 0" rotation="-90 0 0"></a-entity>
```

### 5. Materials and Textures

**Standard Material**:

```html
<a-sphere
  material="color: #FF0000; metalness: 0.5; roughness: 0.3"
  position="0 1 -3">
</a-sphere>
```

**Textured Material**:

```html
<a-assets>
  <img id="woodTexture" src="wood.jpg">
</a-assets>

<a-box material="src: #woodTexture" position="0 1 -3"></a-box>
```

**Flat Shading** (no lighting):

```html
<a-plane material="shader: flat; color: #4CC3D9"></a-plane>
```

### 6. Animations

**Property Animation**:

```html
<a-box
  position="0 1 -3"
  animation="property: rotation; to: 0 360 0; loop: true; dur: 5000">
</a-box>
```

**Multiple Animations** (use `animation__*` naming):

```html
<a-sphere
  position="0 1 -3"
  animation__position="property: position; to: 0 3 -3; dir: alternate; loop: true; dur: 2000"
  animation__rotation="property: rotation; to: 360 360 0; loop: true; dur: 4000"
  animation__scale="property: scale; to: 1.5 1.5 1.5; dir: alternate; loop: true; dur: 1000">
</a-sphere>
```

**Event-Based Animation**:

```html
<a-box
  color="blue"
  animation__mouseenter="property: scale; to: 1.2 1.2 1.2; startEvents: mouseenter"
  animation__mouseleave="property: scale; to: 1 1 1; startEvents: mouseleave"
  animation__click="property: rotation; from: 0 0 0; to: 0 360 0; startEvents: click">
</a-box>
```

### 7. Assets Management

Preload assets for better performance:

```html
<a-scene>
  <a-assets>
    <!-- Images -->
    <img id="texture1" src="texture.jpg">
    <img id="skyTexture" src="sky.jpg">

    <!-- Videos -->
    <video id="video360" src="360video.mp4" autoplay loop></video>

    <!-- Audio -->
    <audio id="bgMusic" src="music.mp3" preload="auto"></audio>

    <!-- Models -->
    <a-asset-item id="tree" src="tree.gltf"></a-asset-item>

    <!-- Mixins (reusable component sets) -->
    <a-mixin id="redMaterial" material="color: red; metalness: 0.7"></a-mixin>
  </a-assets>

  <!-- Use assets -->
  <a-entity gltf-model="#tree" position="2 0 -5"></a-entity>
  <a-sphere mixin="redMaterial" position="0 1 -3"></a-sphere>
  <a-sky src="#skyTexture"></a-sky>
</a-scene>
```

### 8. Custom Components

Register custom components to encapsulate logic:

```javascript
AFRAME.registerComponent('rotate-on-click', {
  // Component schema (configuration)
  schema: {
    speed: {type: 'number', default: 1}
  },

  // Lifecycle: called once when component attached
  init: function() {
    this.el.addEventListener('click', () => {
      this.rotating = !this.rotating;
    });
  },

  // Lifecycle: called every frame
  tick: function(time, timeDelta) {
    if (this.rotating) {
      var rotation = this.el.getAttribute('rotation');
      rotation.y += this.data.speed;
      this.el.setAttribute('rotation', rotation);
    }
  }
});
```

```html
<a-box rotate-on-click="speed: 2" position="0 1 -3"></a-box>
```

## Common Patterns

### Pattern 1: VR Controller Interactions

**Problem**: Enable object grabbing and manipulation in VR

**Solution**: Use hand-controls and custom grab component

```html
<a-scene>
  <!-- VR Camera Rig -->
  <a-entity id="rig">
    <a-camera position="0 1.6 0"></a-camera>

    <a-entity
      id="leftHand"
      hand-controls="hand: left"
      laser-controls="hand: left">
    </a-entity>

    <a-entity
      id="rightHand"
      hand-controls="hand: right"
      laser-controls="hand: right">
    </a-entity>
  </a-entity>

  <!-- Grabbable objects -->
  <a-box class="grabbable" position="-1 1.5 -3" color="#4CC3D9"></a-box>
  <a-sphere class="grabbable" position="1 1.5 -3" color="#EF2D5E"></a-sphere>
</a-scene>

<script>
AFRAME.registerComponent('grabbable', {
  init: function() {
    var el = this.el;

    el.addEventListener('triggerdown', function(evt) {
      console.log('Grabbed by', evt.detail.hand);
      el.setAttribute('color', 'green');
    });

    el.addEventListener('triggerup', function(evt) {
      el.setAttribute('color', 'blue');
    });

    el.addEventListener('gripdown', function(evt) {
      // Attach object to controller
      var controllerEl = evt.detail.controller;
      controllerEl.object3D.attach(el.object3D);
    });

    el.addEventListener('gripup', function(evt) {
      // Detach from controller
      var sceneEl = el.sceneEl.object3D;
      sceneEl.attach(el.object3D);
    });
  }
});

// Apply grabbable component
document.querySelectorAll('.grabbable').forEach(el => {
  el.setAttribute('grabbable', '');
});
</script>
```

### Pattern 2: 360° Image Gallery

**Problem**: Create an interactive 360° photo viewer

**Solution**: Use sky primitive and clickable thumbnails

```html
<a-scene>
  <a-assets>
    <img id="city" src="city.jpg">
    <img id="forest" src="forest.jpg">
    <img id="beach" src="beach.jpg">
    <img id="city-thumb" src="city-thumb.jpg">
    <img id="forest-thumb" src="forest-thumb.jpg">
    <img id="beach-thumb" src="beach-thumb.jpg">
    <audio id="click-sound" src="click.mp3"></audio>
  </a-assets>

  <!-- 360 image sphere -->
  <a-sky id="image-360" src="#city" rotation="0 -130 0"></a-sky>

  <!-- Thumbnail menu -->
  <a-entity id="menu" position="0 1.6 -2">
    <a-entity class="link"
      geometry="primitive: plane; width: 0.7; height: 0.7"
      material="shader: flat; src: #city-thumb"
      position="-1 0 0"
      sound="on: click; src: #click-sound"
      event-set__mouseenter="scale: 1.2 1.2 1"
      event-set__mouseleave="scale: 1 1 1"
      event-set__click="_target: #image-360; material.src: #city">
    </a-entity>

    <a-entity class="link"
      geometry="primitive: plane; width: 0.7; height: 0.7"
      material="shader: flat; src: #forest-thumb"
      position="0 0 0"
      sound="on: click; src: #click-sound"
      event-set__mouseenter="scale: 1.2 1.2 1"
      event-set__mouseleave="scale: 1 1 1"
      event-set__click="_target: #image-360; material.src: #forest">
    </a-entity>

    <a-entity class="link"
      geometry="primitive: plane; width: 0.7; height: 0.7"
      material="shader: flat; src: #beach-thumb"
      position="1 0 0"
      sound="on: click; src: #click-sound"
      event-set__mouseenter="scale: 1.2 1.2 1"
      event-set__mouseleave="scale: 1 1 1"
      event-set__click="_target: #image-360; material.src: #beach">
    </a-entity>
  </a-entity>

  <!-- Camera with cursor for gaze interaction -->
  <a-camera>
    <a-cursor raycaster="objects: .link"></a-cursor>
  </a-camera>
</a-scene>
```

### Pattern 3: AR Hit Testing (Place Objects in Real World)

**Problem**: Place virtual objects on detected real-world surfaces

**Solution**: Use ar-hit-test component

```html
<a-scene
  webxr="optionalFeatures: hit-test, dom-overlay; overlayElement: #overlay"
  ar-hit-test="target: #furniture; type: footprint">

  <a-assets>
    <a-asset-item id="chair" src="chair.gltf"></a-asset-item>
  </a-assets>

  <!-- Object to place -->
  <a-entity id="furniture" gltf-model="#chair" scale="0.5 0.5 0.5"></a-entity>

  <!-- AR instructions overlay -->
  <div id="overlay" style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);
                           background: rgba(0,0,0,0.7); color: white; padding: 15px;
                           border-radius: 8px; font-family: sans-serif;">
    <p id="message">Tap to enter AR mode</p>
  </div>
</a-scene>

<script>
const sceneEl = document.querySelector('a-scene');
const message = document.getElementById('message');

sceneEl.addEventListener('enter-vr', function() {
  if (this.is('ar-mode')) {
    message.textContent = '';

    this.addEventListener('ar-hit-test-start', function() {
      message.innerHTML = 'Scanning environment, finding surface.';
    }, { once: true });

    this.addEventListener('ar-hit-test-achieved', function() {
      message.innerHTML = 'Tap on the screen to place the object.';
    }, { once: true });

    this.addEventListener('ar-hit-test-select', function() {
      message.textContent = 'Object placed!';
      setTimeout(() => message.textContent = '', 2000);
    }, { once: true });
  }
});

sceneEl.addEventListener('exit-vr', function() {
  message.textContent = 'Tap to enter AR mode';
});
</script>
```

### Pattern 4: Mouse/Gaze Interactions

**Problem**: Enable click interactions with desktop mouse or VR gaze

**Solution**: Use cursor component and raycaster

```html
<a-scene>
  <!-- Interactive objects -->
  <a-box
    class="interactive"
    position="-1 1.5 -3"
    color="#4CC3D9"
    event-set__mouseenter="color: yellow"
    event-set__mouseleave="color: #4CC3D9"
    event-set__click="scale: 1.5 1.5 1.5">
  </a-box>

  <a-sphere
    class="interactive"
    position="1 1.5 -3"
    color="#EF2D5E"
    event-set__click="color: orange; scale: 2 2 2">
  </a-sphere>

  <a-plane position="0 0 -4" rotation="-90 0 0" width="10" height="10" color="#7BC8A4"></a-plane>

  <!-- Camera with cursor -->
  <a-camera position="0 1.6 0">
    <!-- Raycaster targets .interactive class -->
    <a-cursor
      raycaster="objects: .interactive"
      fuse="true"
      fuse-timeout="1500">
    </a-cursor>
  </a-camera>
</a-scene>

<script>
// Advanced click handling with JavaScript
document.querySelectorAll('.interactive').forEach(el => {
  el.addEventListener('click', function(evt) {
    console.log('Clicked:', this.id || this.tagName);
    console.log('Intersection point:', evt.detail.intersection.point);
  });
});
</script>
```

### Pattern 5: Dynamic Scene Generation

**Problem**: Programmatically create and manipulate entities

**Solution**: Use JavaScript DOM manipulation

```html
<a-scene>
  <a-camera position="0 1.6 5"></a-camera>
  <a-entity light="type: ambient; color: #888"></a-entity>
  <a-entity light="type: directional; color: #FFF" position="1 2 1"></a-entity>
</a-scene>

<script>
const scene = document.querySelector('a-scene');

// Create sphere
function createSphere(x, y, z, color) {
  const entity = document.createElement('a-entity');

  entity.setAttribute('geometry', {
    primitive: 'sphere',
    radius: 0.5
  });

  entity.setAttribute('material', {
    color: color,
    metalness: 0.5,
    roughness: 0.3
  });

  entity.setAttribute('position', {x, y, z});

  // Add animation
  entity.setAttribute('animation', {
    property: 'position',
    to: `${x} ${y + 1} ${z}`,
    dir: 'alternate',
    loop: true,
    dur: 2000
  });

  scene.appendChild(entity);
  return entity;
}

// Generate grid of spheres
for (let x = -3; x <= 3; x += 1.5) {
  for (let z = -5; z <= -2; z += 1.5) {
    const color = `#${Math.floor(Math.random()*16777215).toString(16)}`;
    createSphere(x, 1, z, color);
  }
}

// Listen to component changes
scene.addEventListener('componentchanged', function(evt) {
  console.log('Component changed:', evt.detail.name);
});

// Access Three.js objects directly
setTimeout(() => {
  const entities = document.querySelectorAll('a-entity[geometry]');
  entities.forEach(el => {
    el.object3D.visible = true; // Direct Three.js manipulation
  });
}, 1000);
</script>
```

### Pattern 6: Environment and Skybox

**Problem**: Create immersive environments quickly

**Solution**: Use community components and 360 images

```html
<html>
  <head>
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@fern-solutions/aframe-sky-background/dist/sky-background.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/c-frame/aframe-extras@7.5.0/dist/aframe-extras.min.js"></script>
  </head>
  <body>
    <a-scene>
      <!-- Gradient sky -->
      <a-sky-background
        top-color="#4A90E2"
        bottom-color="#87CEEB">
      </a-sky-background>

      <!-- Or textured sky -->
      <!-- <a-sky src="sky.jpg" rotation="0 -130 0"></a-sky> -->

      <!-- Ocean -->
      <a-entity
        ocean="density: 20; width: 50; depth: 50; speed: 4"
        material="color: #9CE3F9; opacity: 0.75; metalness: 0; roughness: 1"
        rotation="-90 0 0">
      </a-entity>

      <!-- Particle system for atmosphere -->
      <a-entity
        particle-system="preset: snow; particleCount: 2000; color: #FFF">
      </a-entity>

      <a-entity light="type: ambient; color: #888"></a-entity>
      <a-entity light="type: directional; color: #FFF; intensity: 0.7" position="1 2 1"></a-entity>
    </a-scene>
  </body>
</html>
```

### Pattern 7: GLTF Model Loading

**Problem**: Load and display 3D models

**Solution**: Use gltf-model component with asset management

```html
<a-scene>
  <a-assets>
    <a-asset-item id="robot" src="robot.gltf"></a-asset-item>
    <a-asset-item id="building" src="building.glb"></a-asset-item>
  </a-assets>

  <!-- Load model -->
  <a-entity
    gltf-model="#robot"
    position="0 0 -3"
    scale="0.5 0.5 0.5"
    animation="property: rotation; to: 0 360 0; loop: true; dur: 10000">
  </a-entity>

  <!-- Load with extras (animations) -->
  <a-entity
    gltf-model="#building"
    position="5 0 -10"
    animation-mixer="clip: *; loop: repeat">
  </a-entity>

  <a-camera position="0 1.6 5"></a-camera>
  <a-entity light="type: ambient; intensity: 0.5"></a-entity>
  <a-entity light="type: directional; intensity: 0.8" position="2 4 2"></a-entity>
</a-scene>

<script>
// Handle model loading events
document.querySelector('[gltf-model="#robot"]').addEventListener('model-loaded', (evt) => {
  console.log('Model loaded:', evt.detail.model);

  // Access Three.js object
  const model = evt.detail.model;
  model.traverse(node => {
    if (node.isMesh) {
      console.log('Mesh found:', node.name);
    }
  });
});

document.querySelector('[gltf-model="#robot"]').addEventListener('model-error', (evt) => {
  console.error('Model loading error:', evt.detail);
});
</script>
```

## Integration Patterns

### With Three.js

Access underlying Three.js objects:

```javascript
// Get Three.js scene
const scene = document.querySelector('a-scene').object3D;

// Get entity's Three.js object
const box = document.querySelector('a-box');
const threeObject = box.object3D;

// Direct Three.js manipulation
threeObject.position.set(1, 2, 3);
threeObject.rotation.y = Math.PI / 4;

// Add custom Three.js objects
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
const mesh = new THREE.Mesh(geometry, material);
scene.add(mesh);
```

### With GSAP (Animation)

Animate A-Frame entities with GSAP:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script>
const box = document.querySelector('a-box');

// Animate position
gsap.to(box.object3D.position, {
  x: 3,
  y: 2,
  z: -5,
  duration: 2,
  ease: 'power2.inOut'
});

// Animate rotation
gsap.to(box.object3D.rotation, {
  y: Math.PI * 2,
  duration: 3,
  repeat: -1,
  ease: 'none'
});

// Animate attributes
gsap.to(box.components.material.material, {
  opacity: 0.5,
  duration: 1
});
</script>
```

### With React

Integrate A-Frame in React components:

```jsx
import React, { useEffect, useRef } from 'react';
import 'aframe';

function VRScene() {
  const sceneRef = useRef(null);

  useEffect(() => {
    const scene = sceneRef.current;

    // Create entities dynamically
    const entity = document.createElement('a-sphere');
    entity.setAttribute('position', '0 1.5 -3');
    entity.setAttribute('color', '#EF2D5E');
    scene.appendChild(entity);

    // Listen to events
    scene.addEventListener('enter-vr', () => {
      console.log('Entered VR mode');
    });
  }, []);

  return (
    <a-scene ref={sceneRef}>
      <a-box position="-1 0.5 -3" rotation="0 45 0" color="#4CC3D9" />
      <a-sphere position="0 1.25 -5" radius="1.25" color="#EF2D5E" />
      <a-cylinder position="1 0.75 -3" radius="0.5" height="1.5" color="#FFC65D" />
      <a-plane position="0 0 -4" rotation="-90 0 0" width="4" height="4" color="#7BC8A4" />
      <a-sky color="#ECECEC" />
    </a-scene>
  );
}

export default VRScene;
```

## Performance Best Practices

### 1. Use Asset Management

Preload assets to avoid blocking:

```html
<a-assets>
  <img id="texture1" src="large-texture.jpg">
  <video id="video360" src="360video.mp4" preload="auto"></video>
  <a-asset-item id="model" src="complex-model.gltf"></a-asset-item>
</a-assets>
```

### 2. Pool Entities

Reuse entities instead of creating/destroying:

```javascript
AFRAME.registerComponent('bullet-pool', {
  init: function() {
    this.pool = [];
    this.used = [];

    // Pre-create bullets
    for (let i = 0; i < 20; i++) {
      const bullet = document.createElement('a-sphere');
      bullet.setAttribute('radius', 0.1);
      bullet.setAttribute('visible', false);
      this.el.sceneEl.appendChild(bullet);
      this.pool.push(bullet);
    }
  },

  getBullet: function() {
    if (this.pool.length > 0) {
      const bullet = this.pool.pop();
      bullet.setAttribute('visible', true);
      this.used.push(bullet);
      return bullet;
    }
  },

  returnBullet: function(bullet) {
    bullet.setAttribute('visible', false);
    const index = this.used.indexOf(bullet);
    if (index > -1) {
      this.used.splice(index, 1);
      this.pool.push(bullet);
    }
  }
});
```

### 3. Optimize Geometry

Use low-poly models and LOD:

```html
<!-- Low-poly for distant objects -->
<a-sphere radius="1" segments-width="8" segments-height="6"></a-sphere>

<!-- High-poly for close objects -->
<a-sphere radius="1" segments-width="32" segments-height="32"></a-sphere>
```

### 4. Limit Draw Calls

Use instancing for repeated objects:

```javascript
AFRAME.registerComponent('instanced-trees', {
  init: function() {
    // Use Three.js InstancedMesh for repeated geometry
    const scene = this.el.sceneEl.object3D;
    const geometry = new THREE.ConeGeometry(0.5, 2, 8);
    const material = new THREE.MeshStandardMaterial({ color: 0x228B22 });
    const mesh = new THREE.InstancedMesh(geometry, material, 100);

    // Position instances
    for (let i = 0; i < 100; i++) {
      const matrix = new THREE.Matrix4();
      matrix.setPosition(
        Math.random() * 20 - 10,
        0,
        Math.random() * 20 - 10
      );
      mesh.setMatrixAt(i, matrix);
    }

    scene.add(mesh);
  }
});
```

### 5. Throttle tick() Functions

Don't update every frame if unnecessary:

```javascript
AFRAME.registerComponent('throttled-update', {
  init: function() {
    this.lastUpdate = 0;
    this.updateInterval = 100; // ms
  },

  tick: function(time, timeDelta) {
    if (time - this.lastUpdate >= this.updateInterval) {
      // Expensive operation here
      this.lastUpdate = time;
    }
  }
});
```

### 6. Use Stats Component for Monitoring

```html
<a-scene stats>
  <!-- Shows FPS and performance metrics -->
</a-scene>
```

## Common Pitfalls and Solutions

### Pitfall 1: Entities Not Appearing

**Problem**: Entity added but not visible

**Causes**:
- Entity positioned behind camera
- Scale is 0 or very small
- Material opacity is 0
- Entity outside camera frustum

**Solution**:

```javascript
// Wait for scene to load
const scene = document.querySelector('a-scene');
scene.addEventListener('loaded', () => {
  const entity = document.createElement('a-box');
  entity.setAttribute('position', '0 1.5 -3'); // In front of camera
  entity.setAttribute('color', 'red');
  scene.appendChild(entity);
});

// Debug: Check entity position
console.log(entity.getAttribute('position'));

// Debug: Check if entity is in scene
console.log(entity.parentNode); // Should be <a-scene>
```

### Pitfall 2: Events Not Firing

**Problem**: Click/mouseenter events don't trigger

**Cause**: Missing raycaster or cursor

**Solution**:

```html
<!-- Add cursor to camera -->
<a-camera>
  <a-cursor raycaster="objects: .interactive"></a-cursor>
</a-camera>

<!-- Add class to interactive objects -->
<a-box class="interactive" position="0 1 -3"></a-box>

<!-- Or use raycaster directly -->
<a-entity raycaster="objects: [geometry]" cursor></a-entity>
```

### Pitfall 3: Performance Degradation

**Problem**: Low FPS with many entities

**Causes**:
- Too many draw calls
- Complex geometries
- Unoptimized textures
- Too many tick() updates

**Solutions**:

```javascript
// 1. Use object pooling (see Performance section)
// 2. Simplify geometry
// 3. Optimize textures (reduce size, use compression)
// 4. Throttle updates

AFRAME.registerComponent('optimize-far-entities', {
  tick: function() {
    const camera = this.el.sceneEl.camera;
    const entities = document.querySelectorAll('[geometry]');

    entities.forEach(el => {
      const distance = el.object3D.position.distanceTo(camera.position);

      // Hide distant entities
      el.object3D.visible = distance < 50;
    });
  }
});
```

### Pitfall 4: Z-Fighting (Overlapping Surfaces)

**Problem**: Flickering when surfaces overlap

**Cause**: Two surfaces at same position

**Solution**:

```html
<!-- Offset surfaces slightly -->
<a-plane position="0 0.01 0" rotation="-90 0 0"></a-plane>
<a-plane position="0 0.02 0" rotation="-90 0 0"></a-plane>

<!-- Or use renderOrder -->
<a-entity
  geometry="primitive: plane"
  material="src: #texture1; transparent: true"
  class="has-render-order">
</a-entity>

<script>
document.querySelector('.has-render-order').object3D.renderOrder = 1;
</script>
```

### Pitfall 5: Mobile VR Performance

**Problem**: Low performance on mobile VR

**Solutions**:

```html
<!-- Reduce renderer max canvas size -->
<a-scene renderer="maxCanvasWidth: 1920; maxCanvasHeight: 1920">

<!-- Use low-poly models -->
<a-sphere radius="1" segments-width="8" segments-height="6"></a-sphere>

<!-- Limit lights (expensive on mobile) -->
<a-entity light="type: ambient; intensity: 0.6"></a-entity>
<a-entity light="type: directional; intensity: 0.4" position="1 2 1"></a-entity>

<!-- Disable antialiasing if needed -->
<a-scene renderer="antialias: false">
</a-scene>
```

### Pitfall 6: Asset Loading Issues

**Problem**: Assets not loading or CORS errors

**Solutions**:

```html
<!-- Use crossorigin attribute -->
<a-assets>
  <img id="texture" src="https://example.com/texture.jpg" crossorigin="anonymous">
</a-assets>

<!-- Wait for assets to load -->
<script>
const assets = document.querySelector('a-assets');
assets.addEventListener('loaded', () => {
  console.log('All assets loaded');
  // Safe to use assets now
});

assets.addEventListener('timeout', () => {
  console.error('Asset loading timeout');
});
</script>

<!-- Handle loading errors -->
<script>
const img = document.querySelector('img#texture');
img.addEventListener('error', () => {
  console.error('Failed to load texture');
  // Use fallback
  img.src = 'fallback-texture.jpg';
});
</script>
```

## Resources

- [A-Frame Documentation](https://aframe.io/docs/)
- [A-Frame GitHub](https://github.com/aframevr/aframe)
- [A-Frame School](https://aframe.io/school/)
- [A-Frame Community Components](https://github.com/c-frame)
- [WebXR Device API](https://www.w3.org/TR/webxr/)
- [Three.js Documentation](https://threejs.org/docs/) (A-Frame built on Three.js)

## Related Skills

- **threejs-webgl**: For advanced Three.js control beyond A-Frame's declarative API
- **babylonjs-engine**: Alternative 3D engine with different architecture
- **gsap-scrolltrigger**: For animating A-Frame entities with GSAP
- **react-three-fiber**: React approach to Three.js (compare with A-Frame's HTML approach)



===== FILE: plugins/individual/aframe-webxr/skills/aframe-webxr/references/api_reference.md =====

# A-Frame API Reference

Complete reference for A-Frame 1.7.x core components, primitives, and systems.

## Table of Contents

- [Scene](#scene)
- [Entity](#entity)
- [Core Components](#core-components)
  - [Camera](#camera)
  - [Geometry](#geometry)
  - [Material](#material)
  - [Light](#light)
  - [Position, Rotation, Scale](#position-rotation-scale)
  - [Animation](#animation)
  - [Sound](#sound)
- [Primitives](#primitives)
- [Controls](#controls)
- [VR/XR Components](#vrxr-components)
- [Systems](#systems)
- [Component API](#component-api)
- [JavaScript API](#javascript-api)

---

## Scene

The `<a-scene>` element represents the 3D scene and contains all entities.

### HTML Usage

```html
<a-scene
  background="color: #ECECEC"
  fog="type: linear; color: #AAA; near: 1; far: 100"
  stats
  inspector
  embedded
  vr-mode-ui="enabled: true"
  loading-screen="enabled: true"
  renderer="antialias: true; colorManagement: true"
  webxr="requiredFeatures: hit-test; optionalFeatures: dom-overlay">
</a-scene>
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `background` | color | - | Scene background color |
| `fog` | object | - | Fog settings |
| `stats` | boolean | false | Show performance stats |
| `inspector` | boolean | false | Enable inspector (Ctrl+Alt+I) |
| `embedded` | boolean | false | Embed in page (no fullscreen) |
| `vr-mode-ui` | object | - | VR mode button config |
| `loading-screen` | object | - | Loading screen config |
| `renderer` | object | - | Three.js renderer settings |
| `webxr` | object | - | WebXR configuration |

### Events

- `loaded`: Scene loaded and ready
- `enter-vr`: Entered VR/AR mode
- `exit-vr`: Exited VR/AR mode
- `renderstart`: First render tick
- `componentchanged`: Component updated

### JavaScript API

```javascript
const scene = document.querySelector('a-scene');

// Check if scene is loaded
if (scene.hasLoaded) {
  console.log('Scene ready');
}

// Check VR/AR mode
if (scene.is('vr-mode')) {
  console.log('In VR mode');
}

if (scene.is('ar-mode')) {
  console.log('In AR mode');
}

// Enter/exit VR
scene.enterVR();
scene.exitVR();

// Access Three.js scene
const threeScene = scene.object3D;

// Access camera
const camera = scene.camera;

// Access renderer
const renderer = scene.renderer;

// Access systems
const geometrySystem = scene.systems.geometry;
```

---

## Entity

The `<a-entity>` is the base building block. All objects are entities with attached components.

### HTML Usage

```html
<a-entity
  id="myEntity"
  class="interactive"
  geometry="primitive: box; width: 2"
  material="color: red; metalness: 0.5"
  position="0 1.5 -3"
  rotation="0 45 0"
  scale="1 1 1"
  visible="true"
  mixin="baseEntity">
</a-entity>
```

### Core Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | string | - | Unique identifier |
| `class` | string | - | CSS-like class names |
| `mixin` | string | - | Space-separated mixin IDs |
| `visible` | boolean | true | Visibility |

### JavaScript API

```javascript
const entity = document.querySelector('#myEntity');

// Set attribute
entity.setAttribute('position', '1 2 3');
entity.setAttribute('position', {x: 1, y: 2, z: 3});

// Get attribute
const position = entity.getAttribute('position');
console.log(position.x, position.y, position.z);

// Add/remove class
entity.classList.add('interactive');
entity.classList.remove('interactive');

// Component methods
entity.setAttribute('my-component', 'value: 5');
entity.removeAttribute('my-component');
entity.hasAttribute('my-component');

// States
entity.addState('selected');
entity.removeState('selected');
entity.is('selected'); // Check state

// Events
entity.emit('hit', {damage: 10});
entity.addEventListener('hit', (evt) => {
  console.log('Damage:', evt.detail.damage);
});

// Access Three.js object
const object3D = entity.object3D;
object3D.position.set(1, 2, 3);
object3D.rotation.y = Math.PI / 4;

// Parent/child
const parent = entity.parentNode;
const children = entity.children;
entity.appendChild(childEntity);
entity.removeChild(childEntity);

// Play/pause
entity.play();
entity.pause();

// Component access
const material = entity.components.material;
```

---

## Core Components

### Camera

Defines the view into the 3D scene.

#### Properties

```html
<a-entity camera="
  active: true;
  far: 10000;
  fov: 80;
  near: 0.1;
  spectator: false;
  zoom: 1
"></a-entity>
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `active` | boolean | true | Whether camera is active |
| `far` | number | 10000 | Far clipping plane |
| `fov` | number | 80 | Field of view (degrees) |
| `near` | number | 0.005 | Near clipping plane |
| `spectator` | boolean | false | Spectator mode (desktop only) |
| `zoom` | number | 1 | Zoom level |

#### Example

```html
<a-entity
  camera="fov: 60; near: 0.1; far: 1000"
  look-controls
  wasd-controls
  position="0 1.6 0">
</a-entity>
```

### Geometry

Defines the shape of an entity.

#### Properties

```html
<a-entity geometry="
  primitive: box;
  width: 1;
  height: 1;
  depth: 1
"></a-entity>
```

#### Primitives

**Box**
```html
<a-entity geometry="primitive: box; width: 1; height: 1; depth: 1"></a-entity>
```

**Sphere**
```html
<a-entity geometry="primitive: sphere; radius: 1; segmentsWidth: 32; segmentsHeight: 32"></a-entity>
```

**Plane**
```html
<a-entity geometry="primitive: plane; width: 1; height: 1"></a-entity>
```

**Cylinder**
```html
<a-entity geometry="primitive: cylinder; radius: 0.5; height: 1; segmentsRadial: 36"></a-entity>
```

**Cone**
```html
<a-entity geometry="primitive: cone; radiusBottom: 0.5; radiusTop: 0; height: 1"></a-entity>
```

**Circle**
```html
<a-entity geometry="primitive: circle; radius: 1; segments: 32; thetaStart: 0; thetaLength: 360"></a-entity>
```

**Ring**
```html
<a-entity geometry="primitive: ring; radiusInner: 0.5; radiusOuter: 1"></a-entity>
```

**Torus**
```html
<a-entity geometry="primitive: torus; radius: 1; radiusTubular: 0.2; segmentsRadial: 36; segmentsTubular: 32"></a-entity>
```

**Torus Knot**
```html
<a-entity geometry="primitive: torusKnot; radius: 1; radiusTubular: 0.2; p: 2; q: 3"></a-entity>
```

**Triangle**
```html
<a-entity geometry="primitive: triangle; vertexA: 0 0.5 0; vertexB: -0.5 -0.5 0; vertexC: 0.5 -0.5 0"></a-entity>
```

### Material

Defines the appearance of the geometry.

#### Standard Material Properties

```html
<a-entity material="
  color: #FFF;
  metalness: 0;
  opacity: 1;
  roughness: 0.5;
  shader: standard;
  side: front;
  transparent: false;
  vertexColors: none;
  visible: true
"></a-entity>
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `color` | color | #FFF | Base color |
| `metalness` | number | 0 | Metallic property (0-1) |
| `opacity` | number | 1 | Opacity (0-1, requires transparent: true) |
| `roughness` | number | 0.5 | Surface roughness (0-1) |
| `shader` | string | standard | Shader type (standard, flat) |
| `side` | string | front | Which sides to render (front, back, double) |
| `transparent` | boolean | false | Enable transparency |
| `src` | selector | - | Texture image/video |
| `repeat` | vec2 | 1 1 | Texture repeat |
| `normalMap` | selector | - | Normal map texture |
| `emissive` | color | #000 | Emissive color |
| `emissiveIntensity` | number | 1 | Emissive intensity |

#### Flat Shader

```html
<a-entity material="shader: flat; color: #4CC3D9"></a-entity>
```

#### Textured Material

```html
<a-assets>
  <img id="texture" src="texture.jpg">
</a-assets>

<a-entity material="src: #texture; repeat: 2 2; normalMap: #normalTexture"></a-entity>
```

### Light

Illuminates the scene.

#### Types

**Ambient Light**
```html
<a-entity light="type: ambient; color: #BBB; intensity: 0.5"></a-entity>
```

**Directional Light**
```html
<a-entity light="
  type: directional;
  color: #FFF;
  intensity: 0.8;
  castShadow: true;
  shadowCameraLeft: -5;
  shadowCameraRight: 5;
  shadowCameraTop: 5;
  shadowCameraBottom: -5
" position="1 2 1"></a-entity>
```

**Point Light**
```html
<a-entity light="
  type: point;
  color: #F00;
  intensity: 2;
  distance: 50;
  decay: 1
" position="0 3 0"></a-entity>
```

**Spot Light**
```html
<a-entity light="
  type: spot;
  color: #FFF;
  intensity: 1.5;
  angle: 45;
  penumbra: 0.1;
  distance: 100;
  decay: 1;
  castShadow: true
" position="0 5 0" rotation="-90 0 0"></a-entity>
```

#### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `type` | string | directional | Light type |
| `color` | color | #FFF | Light color |
| `intensity` | number | 1 | Light intensity |
| `castShadow` | boolean | false | Cast shadows |
| `distance` | number | 0 | Max distance (point/spot) |
| `decay` | number | 1 | Light decay (point/spot) |
| `angle` | number | 60 | Spot cone angle (degrees) |
| `penumbra` | number | 0 | Spot edge softness (0-1) |

### Position, Rotation, Scale

Transform components control entity placement and orientation.

#### Position

```html
<a-entity position="0 1.5 -3"></a-entity>
<a-entity position="x: 0; y: 1.5; z: -3"></a-entity>
```

```javascript
entity.setAttribute('position', '1 2 3');
entity.setAttribute('position', {x: 1, y: 2, z: 3});
entity.object3D.position.set(1, 2, 3);
```

#### Rotation

```html
<!-- Degrees -->
<a-entity rotation="0 45 0"></a-entity>
<a-entity rotation="x: 0; y: 45; z: 0"></a-entity>
```

```javascript
// Degrees
entity.setAttribute('rotation', '0 90 0');
entity.setAttribute('rotation', {x: 0, y: 90, z: 0});

// Radians (Three.js)
entity.object3D.rotation.y = Math.PI / 2;
```

#### Scale

```html
<a-entity scale="2 2 2"></a-entity>
<a-entity scale="x: 2; y: 1; z: 2"></a-entity>
```

```javascript
entity.setAttribute('scale', '2 2 2');
entity.setAttribute('scale', {x: 2, y: 1, z: 2});
entity.object3D.scale.set(2, 1, 2);
```

### Animation

Animate entity properties over time.

#### Properties

```html
<a-entity animation="
  property: rotation;
  to: 0 360 0;
  dur: 2000;
  easing: linear;
  loop: true;
  dir: normal;
  delay: 0;
  startEvents: click;
  pauseEvents: pause;
  resumeEvents: resume
"></a-entity>
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `property` | string | - | Property to animate |
| `from` | - | current | Starting value |
| `to` | - | - | Target value |
| `dur` | number | 1000 | Duration (ms) |
| `delay` | number | 0 | Delay before start (ms) |
| `easing` | string | easeInQuad | Easing function |
| `loop` | boolean/number | false | Loop (true, false, or count) |
| `dir` | string | normal | Direction (normal, alternate, reverse) |
| `startEvents` | array | [] | Events that start animation |
| `pauseEvents` | array | [] | Events that pause animation |
| `resumeEvents` | array | [] | Events that resume animation |

#### Easing Functions

`linear`, `easeInQuad`, `easeOutQuad`, `easeInOutQuad`, `easeInCubic`, `easeOutCubic`, `easeInOutCubic`, `easeInQuart`, `easeOutQuart`, `easeInOutQuart`, `easeInQuint`, `easeOutQuint`, `easeInOutQuint`, `easeInSine`, `easeOutSine`, `easeInOutSine`, `easeInExpo`, `easeOutExpo`, `easeInOutExpo`, `easeInCirc`, `easeOutCirc`, `easeInOutCirc`, `easeInElastic`, `easeOutElastic`, `easeInOutElastic`, `easeInBack`, `easeOutBack`, `easeInOutBack`, `easeInBounce`, `easeOutBounce`, `easeInOutBounce`

#### Examples

```html
<!-- Continuous rotation -->
<a-box animation="property: rotation; to: 0 360 0; loop: true; dur: 5000"></a-box>

<!-- Multiple animations -->
<a-sphere
  animation__rotate="property: rotation; to: 360 360 0; loop: true; dur: 10000"
  animation__scale="property: scale; to: 1.5 1.5 1.5; dir: alternate; loop: true; dur: 2000">
</a-sphere>

<!-- Event-triggered -->
<a-box
  animation__click="property: position; to: 0 5 0; startEvents: click"
  animation__mouseenter="property: scale; to: 1.2 1.2 1.2; startEvents: mouseenter"
  animation__mouseleave="property: scale; to: 1 1 1; startEvents: mouseleave">
</a-box>
```

### Sound

Audio playback component.

#### Properties

```html
<a-entity sound="
  src: #sound1;
  autoplay: false;
  loop: false;
  on: click;
  poolSize: 1;
  volume: 1
"></a-entity>
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `src` | selector | - | Audio asset |
| `autoplay` | boolean | false | Play on load |
| `loop` | boolean | false | Loop audio |
| `on` | string | - | Event to play on |
| `poolSize` | number | 1 | Audio buffer pool size |
| `volume` | number | 1 | Volume (0-1) |
| `positional` | boolean | true | 3D positional audio |
| `refDistance` | number | 1 | Reference distance for falloff |
| `rolloffFactor` | number | 1 | Rolloff rate |

#### Example

```html
<a-assets>
  <audio id="click-sound" src="click.mp3"></audio>
  <audio id="bg-music" src="music.mp3"></audio>
</a-assets>

<!-- Play on click -->
<a-box sound="src: #click-sound; on: click" position="0 1 -3"></a-box>

<!-- Background music -->
<a-entity sound="src: #bg-music; autoplay: true; loop: true; volume: 0.5"></a-entity>

<!-- Positional audio -->
<a-entity sound="src: #ambient; autoplay: true; loop: true; positional: true" position="5 0 0"></a-entity>
```

---

## Primitives

Primitives are shortcuts for entity + common components.

### a-box

```html
<a-box
  color="#4CC3D9"
  depth="1"
  height="1"
  width="1"
  position="0 1 -3"
  rotation="0 45 0"
  scale="2 2 2"
  src="#texture"
  metalness="0.5"
  roughness="0.3">
</a-box>
```

Equivalent to:
```html
<a-entity
  geometry="primitive: box; width: 1; height: 1; depth: 1"
  material="color: #4CC3D9; metalness: 0.5; roughness: 0.3; src: #texture"
  position="0 1 -3"
  rotation="0 45 0"
  scale="2 2 2">
</a-entity>
```

### a-sphere

```html
<a-sphere
  color="#EF2D5E"
  radius="1.25"
  segments-width="32"
  segments-height="32"
  phi-start="0"
  phi-length="360"
  theta-start="0"
  theta-length="180"
  position="0 1.25 -5">
</a-sphere>
```

### a-cylinder

```html
<a-cylinder
  color="#FFC65D"
  height="1.5"
  radius="0.5"
  radius-bottom="0.5"
  radius-top="0.5"
  segments-radial="36"
  segments-height="1"
  open-ended="false"
  position="1 0.75 -3">
</a-cylinder>
```

### a-plane

```html
<a-plane
  color="#7BC8A4"
  width="4"
  height="4"
  segments-width="1"
  segments-height="1"
  position="0 0 -4"
  rotation="-90 0 0"
  src="#ground-texture">
</a-plane>
```

### a-sky

```html
<!-- Solid color -->
<a-sky color="#ECECEC"></a-sky>

<!-- 360 image -->
<a-assets>
  <img id="sky-texture" src="sky.jpg">
</a-assets>
<a-sky src="#sky-texture" rotation="0 -130 0"></a-sky>

<!-- 360 video -->
<a-assets>
  <video id="sky-video" src="360video.mp4" autoplay loop></video>
</a-assets>
<a-sky src="#sky-video"></a-sky>
```

### a-camera

```html
<a-camera
  active="true"
  far="10000"
  fov="80"
  look-controls-enabled="true"
  near="0.1"
  position="0 1.6 0"
  reverse-mouse-drag="false"
  wasd-controls-enabled="true">
  <a-cursor></a-cursor>
</a-camera>
```

### a-cursor

```html
<a-cursor
  fuse="false"
  fuse-timeout="1500"
  max-distance="1000"
  raycaster="objects: .interactive">
</a-cursor>
```

### a-light

```html
<a-light type="ambient" color="#BBB" intensity="0.5"></a-light>
<a-light type="directional" color="#FFF" intensity="0.8" position="1 2 1"></a-light>
<a-light type="point" color="#F00" intensity="2" distance="50" position="0 3 0"></a-light>
<a-light type="spot" color="#FFF" intensity="1.5" angle="45" position="0 5 0" rotation="-90 0 0"></a-light>
```

### a-text

```html
<a-text
  value="Hello World"
  color="#FFF"
  width="4"
  align="center"
  anchor="center"
  baseline="center"
  font="roboto"
  letter-spacing="0"
  line-height="1"
  opacity="1"
  side="front"
  wrap-count="40"
  position="0 2 -3">
</a-text>
```

### a-gltf-model

```html
<a-assets>
  <a-asset-item id="tree" src="tree.gltf"></a-asset-item>
</a-assets>

<a-gltf-model
  src="#tree"
  position="0 0 -5"
  scale="0.5 0.5 0.5"
  rotation="0 45 0">
</a-gltf-model>
```

---

## Controls

### look-controls

Enable mouse/touch drag to look around.

```html
<a-entity camera look-controls="
  enabled: true;
  hmdEnabled: true;
  reverseMouseDrag: false;
  reverseTouchDrag: false;
  touchEnabled: true;
  mouseEnabled: true;
  pointerLockEnabled: false
"></a-entity>
```

### wasd-controls

Keyboard movement (W/A/S/D).

```html
<a-entity camera wasd-controls="
  enabled: true;
  acceleration: 65;
  easing: 20;
  fly: false
"></a-entity>
```

### cursor

Raycaster-based pointer for interactions.

```html
<a-cursor
  raycaster="objects: .interactive; far: 1000"
  fuse="false"
  fuse-timeout="1500">
</a-cursor>
```

---

## VR/XR Components

### hand-controls

VR controller hands visualization and tracking.

```html
<a-entity hand-controls="hand: left; handModelStyle: lowPoly; color: #ffcccc"></a-entity>
<a-entity hand-controls="hand: right; handModelStyle: highPoly; color: #ffcccc"></a-entity>
```

### laser-controls

Laser pointer for VR controllers.

```html
<a-entity
  laser-controls="hand: right"
  raycaster="objects: .interactive; far: 10">
</a-entity>
```

### vive-controls

HTC Vive controller support.

```html
<a-entity vive-controls="hand: left; buttonColor: #FF0000; buttonHighlightColor: #FFFF00"></a-entity>
<a-entity vive-controls="hand: right"></a-entity>
```

### meta-touch-controls

Meta Quest/Oculus Touch controller support.

```html
<a-entity meta-touch-controls="hand: left; model: true"></a-entity>
<a-entity meta-touch-controls="hand: right; model: true"></a-entity>
```

### webxr

Configure WebXR features and settings.

```html
<a-scene webxr="
  requiredFeatures: hit-test, local-floor;
  optionalFeatures: dom-overlay, unbounded;
  overlayElement: #overlay;
  referenceSpaceType: local-floor
"></a-scene>
```

### ar-hit-test

AR surface detection and object placement.

```html
<a-scene
  webxr="optionalFeatures: hit-test"
  ar-hit-test="target: #furniture; type: footprint">

  <a-entity id="furniture" gltf-model="#chair"></a-entity>
</a-scene>
```

Events:
- `ar-hit-test-start`: Hit testing started
- `ar-hit-test-achieved`: Surface detected
- `ar-hit-test-select`: User selected placement location

---

## Systems

Systems provide global scene-level functionality.

### Geometry System

```javascript
const geometrySystem = document.querySelector('a-scene').systems.geometry;
```

### Material System

```javascript
const materialSystem = document.querySelector('a-scene').systems.material;
```

### Accessing Systems

```javascript
AFRAME.registerComponent('my-component', {
  init: function() {
    const geometrySystem = this.el.sceneEl.systems.geometry;
    const materialSystem = this.el.sceneEl.systems.material;
  }
});
```

---

## Component API

Register custom components to extend A-Frame.

### Basic Component

```javascript
AFRAME.registerComponent('my-component', {
  // Component schema (configuration)
  schema: {
    color: {type: 'color', default: '#FFF'},
    size: {type: 'number', default: 1},
    enabled: {type: 'boolean', default: true}
  },

  // Initialize (called once)
  init: function() {
    console.log('Component initialized');
    // this.el = entity element
    // this.data = component data
    // this.el.sceneEl = scene element
  },

  // Update (called when properties change)
  update: function(oldData) {
    console.log('Component updated');
    // this.data = new data
    // oldData = previous data
  },

  // Remove (called when component removed)
  remove: function() {
    console.log('Component removed');
  },

  // Tick (called every frame)
  tick: function(time, timeDelta) {
    // time = total elapsed time (ms)
    // timeDelta = time since last tick (ms)
  },

  // Pause (called when entity/scene pauses)
  pause: function() {
    console.log('Component paused');
  },

  // Play (called when entity/scene plays)
  play: function() {
    console.log('Component playing');
  }
});
```

### Schema Types

```javascript
schema: {
  // Basic types
  boolean: {type: 'boolean', default: false},
  number: {type: 'number', default: 0},
  string: {type: 'string', default: ''},

  // Color
  color: {type: 'color', default: '#FFF'},

  // Vectors
  vec2: {type: 'vec2', default: {x: 0, y: 0}},
  vec3: {type: 'vec3', default: {x: 0, y: 0, z: 0}},
  vec4: {type: 'vec4', default: {x: 0, y: 0, z: 0, w: 1}},

  // Selectors
  selector: {type: 'selector'}, // CSS selector
  selectorAll: {type: 'selectorAll'}, // Multiple elements

  // Assets
  audio: {type: 'audio'},
  map: {type: 'map'},
  model: {type: 'model'},

  // Arrays
  array: {type: 'array', default: []},

  // Objects
  object: {type: 'object', default: {}}
}
```

### Multi-Property Components

```javascript
AFRAME.registerComponent('light', {
  schema: {
    type: {default: 'directional', oneOf: ['ambient', 'directional', 'point', 'spot']},
    color: {type: 'color', default: '#FFF'},
    intensity: {type: 'number', default: 1}
  },

  init: function() {
    // Access individual properties
    console.log(this.data.type);
    console.log(this.data.color);
    console.log(this.data.intensity);
  }
});
```

Usage:
```html
<a-entity light="type: point; color: #F00; intensity: 2"></a-entity>
```

### Single-Property Components

```javascript
AFRAME.registerComponent('visible', {
  schema: {type: 'boolean', default: true},

  update: function() {
    // this.data is the boolean value directly
    this.el.object3D.visible = this.data;
  }
});
```

Usage:
```html
<a-entity visible="false"></a-entity>
```

---

## JavaScript API

### Creating Entities

```javascript
const scene = document.querySelector('a-scene');

// Create entity
const entity = document.createElement('a-entity');

// Set attributes
entity.setAttribute('geometry', {primitive: 'box', width: 2});
entity.setAttribute('material', {color: 'red'});
entity.setAttribute('position', {x: 0, y: 1, z: -3});

// Append to scene
scene.appendChild(entity);
```

### Removing Entities

```javascript
const entity = document.querySelector('#myEntity');
entity.parentNode.removeChild(entity);
```

### Event Handling

```javascript
const box = document.querySelector('a-box');

// Listen to events
box.addEventListener('click', (evt) => {
  console.log('Clicked at:', evt.detail.intersection.point);
});

box.addEventListener('mouseenter', () => {
  box.setAttribute('color', 'yellow');
});

box.addEventListener('mouseleave', () => {
  box.setAttribute('color', 'blue');
});

// Emit custom events
box.emit('hit', {damage: 10});

box.addEventListener('hit', (evt) => {
  console.log('Damage:', evt.detail.damage);
});
```

### Accessing Components

```javascript
const entity = document.querySelector('#myEntity');

// Get component instance
const material = entity.components.material;
const geometry = entity.components.geometry;

// Access component data
console.log(material.data.color);

// Call component methods
material.update();
```

### Three.js Integration

```javascript
const entity = document.querySelector('a-box');

// Access Three.js Object3D
const object3D = entity.object3D;

// Manipulate directly
object3D.position.set(1, 2, 3);
object3D.rotation.y = Math.PI / 4;
object3D.scale.set(2, 2, 2);

// Access Three.js mesh
const mesh = entity.getObject3D('mesh');
console.log(mesh.geometry);
console.log(mesh.material);

// Add custom Three.js objects
const scene = document.querySelector('a-scene').object3D;
const customMesh = new THREE.Mesh(geometry, material);
scene.add(customMesh);
```

### Wait for Scene Load

```javascript
const scene = document.querySelector('a-scene');

if (scene.hasLoaded) {
  run();
} else {
  scene.addEventListener('loaded', run);
}

function run() {
  console.log('Scene is ready');
}
```

### Animation Control

```javascript
const entity = document.querySelector('#animated');

// Start animation
entity.emit('startAnimation');

// Pause animation
entity.components.animation.pauseAnimation();

// Resume animation
entity.components.animation.resumeAnimation();
```

### States

```javascript
const enemy = document.querySelector('#enemy');

// Add state
enemy.addState('attacking');
enemy.addState('angry');

// Check state
if (enemy.is('attacking')) {
  console.log('Enemy is attacking');
}

// Remove state
enemy.removeState('attacking');

// Listen to state changes
enemy.addEventListener('stateadded', (evt) => {
  console.log('State added:', evt.detail);
});

enemy.addEventListener('stateremoved', (evt) => {
  console.log('State removed:', evt.detail);
});
```

---

## Constants

### Key Codes

Use with keyboard events:

```javascript
document.addEventListener('keydown', (evt) => {
  if (evt.key === 'w' || evt.key === 'W') {
    console.log('W pressed');
  }
});
```

Common keys:
- `'w'`, `'a'`, `'s'`, `'d'` - Movement
- `' '` - Spacebar
- `'Escape'` - Escape
- `'Enter'` - Enter
- `'ArrowUp'`, `'ArrowDown'`, `'ArrowLeft'`, `'ArrowRight'` - Arrow keys

### Side Constants

```javascript
// Material side
'front' // THREE.FrontSide
'back'  // THREE.BackSide
'double' // THREE.DoubleSide
```

### Easing Functions

See Animation component for full list of easing functions.

---

## Examples

### Complete Scene

```html
<!DOCTYPE html>
<html>
  <head>
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
  </head>
  <body>
    <a-scene>
      <a-assets>
        <img id="ground-texture" src="ground.jpg">
        <img id="sky-texture" src="sky.jpg">
        <a-asset-item id="tree" src="tree.gltf"></a-asset-item>
      </a-assets>

      <!-- Environment -->
      <a-sky src="#sky-texture"></a-sky>
      <a-plane src="#ground-texture" rotation="-90 0 0" width="100" height="100"></a-plane>

      <!-- Lighting -->
      <a-entity light="type: ambient; color: #888; intensity: 0.5"></a-entity>
      <a-entity light="type: directional; color: #FFF; intensity: 0.8" position="2 4 2"></a-entity>

      <!-- Objects -->
      <a-box position="-1 0.5 -3" color="#4CC3D9"></a-box>
      <a-sphere position="0 1.25 -5" radius="1.25" color="#EF2D5E"></a-sphere>
      <a-cylinder position="1 0.75 -3" radius="0.5" height="1.5" color="#FFC65D"></a-cylinder>
      <a-gltf-model src="#tree" position="3 0 -5" scale="0.5 0.5 0.5"></a-gltf-model>

      <!-- Camera -->
      <a-camera position="0 1.6 0">
        <a-cursor></a-cursor>
      </a-camera>
    </a-scene>
  </body>
</html>
```

This API reference covers the core A-Frame components and patterns for building VR/AR experiences.



===== FILE: plugins/individual/aframe-webxr/skills/aframe-webxr/references/components_library.md =====

# A-Frame Community Components Library

Curated collection of popular A-Frame community components for extending functionality.

## Table of Contents

- [Installation Methods](#installation-methods)
- [Environment & Effects](#environment--effects)
- [Physics](#physics)
- [Locomotion](#locomotion)
- [Models & Loaders](#models--loaders)
- [User Interface](#user-interface)
- [Particles](#particles)
- [Audio & Video](#audio--video)
- [Input & Interaction](#input--interaction)
- [Networking](#networking)
- [Utilities](#utilities)

---

## Installation Methods

### CDN (Recommended)

```html
<script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/c-frame/aframe-extras@7.5.0/dist/aframe-extras.min.js"></script>
```

### npm

```bash
npm install aframe-extras
```

```javascript
import 'aframe-extras';
```

### Local Download

Download component `.js` file and include in HTML:

```html
<script src="path/to/component.js"></script>
```

---

## Environment & Effects

### aframe-environment-component

Generate procedural 3D environments with presets.

**GitHub**: https://github.com/supermedium/aframe-environment-component

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-environment-component@1.3.3/dist/aframe-environment-component.min.js"></script>
```

**Usage**:
```html
<!-- Preset environment -->
<a-entity environment="preset: forest"></a-entity>

<!-- Custom environment -->
<a-entity environment="
  preset: default;
  seed: 42;
  skyType: gradient;
  skyColor: #4A90E2;
  horizonColor: #87CEEB;
  lighting: distant;
  lightPosition: 1 1 -2;
  fog: 0.8;
  ground: hills;
  groundColor: #5A7F32;
  groundColor2: #3D5E1F;
  dressing: trees;
  dressingAmount: 50;
  dressingColor: #228B22;
  dressingScale: 5;
  grid: none
"></a-entity>
```

**Presets**:
- `default`, `contact`, `egypt`, `checkerboard`, `forest`, `goaland`, `yavapai`, `goldmine`, `threetowers`, `poison`, `arches`, `tron`, `japan`, `dream`, `volcano`, `starry`, `osiris`

**Properties**:
| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `preset` | string | default | Environment preset |
| `seed` | number | 1 | Random seed |
| `skyType` | string | gradient | Sky type (color, gradient, atmosphere) |
| `lighting` | string | distant | Lighting type (none, distant, point) |
| `ground` | string | flat | Ground type (none, flat, hills, canyon, spikes, noise) |
| `dressing` | string | none | Objects on ground (none, cubes, pyramids, cylinders, towers, mushrooms, trees, apparatus, torii) |
| `dressingAmount` | number | 10 | Number of dressing objects |

### aframe-particle-system-component

GPU particle systems for effects.

**GitHub**: https://github.com/IdeaSpaceVR/aframe-particle-system-component

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/gh/IdeaSpaceVR/aframe-particle-system-component@1.2.x/dist/aframe-particle-system-component.min.js"></script>
```

**Usage**:
```html
<!-- Preset particles -->
<a-entity particle-system="preset: default"></a-entity>
<a-entity particle-system="preset: dust"></a-entity>
<a-entity particle-system="preset: snow"></a-entity>
<a-entity particle-system="preset: rain"></a-entity>

<!-- Custom particles -->
<a-entity particle-system="
  preset: default;
  particleCount: 2000;
  color: #FF0000, #FFFF00;
  size: 0.5, 1;
  velocity: 0 10 0;
  velocitySpread: 1 5 1;
  accelerationValue: 0 -10 0;
  maxAge: 2;
  blending: additive;
  texture: https://cdn.aframe.io/examples/particle/images/star.png
"></a-entity>
```

**Presets**: `default`, `dust`, `snow`, `rain`

### aframe-effects

Post-processing effects (bloom, film grain, etc.).

**GitHub**: https://github.com/wizgrav/aframe-effects

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-effects@2.0.3/dist/aframe-effects.min.js"></script>
```

**Usage**:
```html
<a-scene effects="
  bloom: 1.5;
  fxaa: true;
  filmgrain: 0.35
">
  <!-- Scene content -->
</a-scene>
```

**Effects**:
- `bloom`: Bloom intensity (0-5)
- `fxaa`: Anti-aliasing (boolean)
- `filmgrain`: Film grain amount (0-1)
- `godrays`: God rays intensity (0-1)

---

## Physics

### aframe-physics-system (Ammo.js)

Physics simulation using Ammo.js (Bullet physics).

**GitHub**: https://github.com/c-frame/aframe-physics-system

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-physics-system@4.2.2/dist/aframe-physics-system.min.js"></script>
```

**Usage**:
```html
<a-scene physics="debug: false; gravity: -9.8">
  <!-- Static ground -->
  <a-plane
    static-body
    position="0 0 0"
    rotation="-90 0 0"
    width="10"
    height="10">
  </a-plane>

  <!-- Dynamic box -->
  <a-box
    dynamic-body
    position="0 5 0"
    width="1"
    height="1"
    depth="1">
  </a-box>

  <!-- Kinematic sphere (non-reactive but affects others) -->
  <a-sphere
    kinematic-body
    position="2 3 0"
    radius="0.5">
  </a-sphere>
</a-scene>
```

**Components**:
- `static-body`: Immovable objects (walls, ground)
- `dynamic-body`: Movable objects affected by forces
- `kinematic-body`: Movable by code, affects dynamic bodies

**Properties**:
```html
<a-box dynamic-body="
  mass: 5;
  linearDamping: 0.01;
  angularDamping: 0.01;
  shape: box;
  sphereRadius: 1
"></a-box>
```

### aframe-physics-extras

Physics helpers and constraints.

**GitHub**: https://github.com/c-frame/aframe-physics-system

**Usage**:
```html
<!-- Constraint between two bodies -->
<a-entity
  constraint="
    target: #bodyA;
    type: lock;
    collideConnected: false
  ">
</a-entity>

<!-- Spring -->
<a-entity
  spring="
    target: #box;
    restLength: 2;
    stiffness: 50;
    damping: 1
  ">
</a-entity>
```

---

## Locomotion

### aframe-extras (Movement Components)

Includes movement, controls, and model utilities.

**GitHub**: https://github.com/c-frame/aframe-extras

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/gh/c-frame/aframe-extras@7.5.0/dist/aframe-extras.min.js"></script>
```

**Components Included**:

**movement-controls** (FPS-style movement):
```html
<a-entity movement-controls="
  speed: 0.3;
  fly: false;
  constrainToNavMesh: true;
  camera: #camera
" position="0 0 0">
  <a-entity id="camera" camera position="0 1.6 0"></a-entity>
</a-entity>
```

**checkpoint-controls** (Teleport between waypoints):
```html
<!-- Player -->
<a-entity checkpoint-controls="mode: teleport"></a-entity>

<!-- Waypoints -->
<a-cylinder checkpoint position="0 0 -5" radius="0.5" height="0.1"></a-cylinder>
<a-cylinder checkpoint position="5 0 -5" radius="0.5" height="0.1"></a-cylinder>
```

**Animation Mixer** (GLTF animations):
```html
<a-entity
  gltf-model="#character"
  animation-mixer="clip: walk; loop: repeat">
</a-entity>
```

### aframe-blink-controls

Teleportation locomotion for VR.

**GitHub**: https://github.com/jure/aframe-blink-controls

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-blink-controls/dist/aframe-blink-controls.min.js"></script>
```

**Usage**:
```html
<a-entity
  hand-controls="hand: left"
  blink-controls="
    cameraRig: #rig;
    teleportOrigin: #camera;
    collisionEntities: .ground
  ">
</a-entity>

<a-entity id="rig" position="0 0 0">
  <a-entity id="camera" camera position="0 1.6 0"></a-entity>
</a-entity>

<a-plane class="ground" rotation="-90 0 0" width="20" height="20"></a-plane>
```

---

## Models & Loaders

### gltf-model (Built-in)

Load GLTF/GLB 3D models.

```html
<a-assets>
  <a-asset-item id="tree" src="tree.gltf"></a-asset-item>
</a-assets>

<a-entity gltf-model="#tree" position="0 0 -5"></a-entity>
```

### obj-model (Built-in)

Load OBJ + MTL models.

```html
<a-assets>
  <a-asset-item id="tree-obj" src="tree.obj"></a-asset-item>
  <a-asset-item id="tree-mtl" src="tree.mtl"></a-asset-item>
</a-assets>

<a-entity obj-model="obj: #tree-obj; mtl: #tree-mtl"></a-entity>
```

### aframe-extras (Model Extensions)

Included in aframe-extras:

**animation-mixer**: Play GLTF animations
```html
<a-entity
  gltf-model="#character"
  animation-mixer="clip: walk; loop: repeat; clampWhenFinished: true">
</a-entity>
```

### aframe-simple-sun-sky

Realistic sky with sun position.

**GitHub**: https://github.com/c-frame/aframe-simple-sun-sky

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-simple-sun-sky@^1.2.2/simple-sun-sky.js"></script>
```

**Usage**:
```html
<a-simple-sun-sky sun-position="1 0.4 0"></a-simple-sun-sky>

<!-- Or with parameters -->
<a-simple-sun-sky
  sun-position="1 1 -1"
  rayleigh="1"
  turbidity="10"
  luminance="1"
  mie-coefficient="0.005"
  mie-directional-g="0.8">
</a-simple-sun-sky>
```

---

## User Interface

### aframe-html-shader

Display HTML content on meshes.

**GitHub**: https://github.com/mayognaise/aframe-html-shader

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-html-shader@0.2.0/dist/aframe-html-shader.min.js"></script>
```

**Usage**:
```html
<a-entity geometry="primitive: plane; width: 2; height: 1"
          material="shader: html; target: #html-content; ratio: width"
          position="0 1.5 -3">
</a-entity>

<div id="html-content" style="width: 400px; height: 200px; background: white;">
  <h1>HTML Content</h1>
  <p>This is rendered on a 3D surface!</p>
</div>
```

### aframe-gui

VR GUI components (buttons, sliders, panels).

**GitHub**: https://github.com/rdub80/aframe-gui

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-gui/dist/aframe-gui.min.js"></script>
```

**Usage**:
```html
<!-- Button -->
<a-gui-button
  width="2.5"
  height="0.75"
  value="Click Me"
  onclick="alert('Clicked!')"
  position="0 1.5 -3">
</a-gui-button>

<!-- Slider -->
<a-gui-slider
  width="2.5"
  height="0.75"
  percent="0.5"
  position="0 2.5 -3">
</a-gui-slider>

<!-- Toggle -->
<a-gui-toggle
  width="2.5"
  height="0.75"
  value="Sound: On"
  position="0 3.5 -3">
</a-gui-toggle>
```

### aframe-troika-text

High-quality text rendering.

**GitHub**: https://github.com/lojjic/aframe-troika-text

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/troika-three-text@0.46.4/dist/troika-three-text.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/aframe-troika-text@1.0.0/dist/aframe-troika-text.min.js"></script>
```

**Usage**:
```html
<a-entity troika-text="
  value: High Quality Text;
  align: center;
  anchor: center;
  baseline: center;
  color: #FFF;
  fontSize: 0.2;
  maxWidth: 3;
  outlineWidth: 0.01;
  outlineColor: #000
" position="0 2 -3">
</a-entity>
```

---

## Particles

### aframe-spe-particles

Shader Particle Engine for advanced particle effects.

**GitHub**: https://github.com/harlyq/aframe-spe-particles-component

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-spe-particles-component/dist/aframe-spe-particles-component.min.js"></script>
```

**Usage**:
```html
<!-- Fire effect -->
<a-entity spe-particles="
  texture: https://cdn.rawgit.com/IdeaSpaceVR/aframe-particle-system-component/master/dist/images/star.png;
  color: #ff0000, #ffff00;
  particleCount: 1000;
  maxAge: 1;
  velocity: 0 4 0;
  velocitySpread: 2 0 2;
  acceleration: 0 -1 0;
  size: 1, 0;
  opacity: 1, 0;
  blending: additive
" position="0 0 -5">
</a-entity>
```

---

## Audio & Video

### aframe-stereo-component

Stereo/spatial audio controls.

**GitHub**: https://github.com/oscarmarinmiro/aframe-stereo-component

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-stereo-component/dist/aframe-stereo-component.min.js"></script>
```

**Usage**:
```html
<a-assets>
  <audio id="ambience" src="forest.mp3" stereo></audio>
</a-assets>

<a-entity sound="src: #ambience; autoplay: true; loop: true" position="0 0 0"></a-entity>
```

### aframe-video-controls

Video playback controls for 360° and flat videos.

**Usage**:
```html
<a-assets>
  <video id="video360" src="360video.mp4" preload="auto"></video>
</a-assets>

<a-videosphere src="#video360"></a-videosphere>

<!-- Or flat video -->
<a-video src="#video360" width="4" height="2.25" position="0 2 -5"></a-video>
```

---

## Input & Interaction

### aframe-event-set-component (Built-in)

Set component properties on events.

**Usage**:
```html
<a-box
  event-set__mouseenter="scale: 1.2 1.2 1.2; material.color: yellow"
  event-set__mouseleave="scale: 1 1 1; material.color: blue"
  event-set__click="rotation: 0 360 0">
</a-box>
```

### aframe-super-hands-component

Advanced hand interaction (grab, stretch, hover).

**GitHub**: https://github.com/c-frame/aframe-super-hands-component

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/super-hands/dist/super-hands.min.js"></script>
```

**Usage**:
```html
<!-- Hands with super-hands -->
<a-entity
  hand-controls="hand: left"
  super-hands>
</a-entity>

<!-- Interactive object -->
<a-box
  hoverable
  grabbable
  stretchable
  draggable
  position="0 1.5 -3">
</a-box>
```

### aframe-input-mapping-component

Map VR controller buttons to actions.

**GitHub**: https://github.com/c-frame/aframe-input-mapping-component

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-input-mapping-component/dist/aframe-input-mapping-component.min.js"></script>
```

**Usage**:
```html
<a-entity
  hand-controls="hand: right"
  input-mapping="
    keyboard: wasd;
    controller: sixdof;
    mapping: {
      'triggerdown': 'shoot',
      'gripdown': 'grab',
      'abuttondown': 'jump'
    }
  ">
</a-entity>
```

---

## Networking

### networked-aframe (NAF)

Multiplayer WebRTC networking.

**GitHub**: https://github.com/networked-aframe/networked-aframe

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/networked-aframe@^0.11.0/dist/networked-aframe.min.js"></script>
```

**Usage**:
```html
<a-scene networked-scene="
  room: myRoom;
  adapter: wseasyrtc;
  audio: true
">
  <!-- Networked entity (synced across clients) -->
  <a-entity
    networked="template: #avatar-template; attachTemplateToLocal: false"
    position="0 0 0">
  </a-entity>
</a-scene>

<script>
// Template for networked entities
NAF.schemas.add({
  template: '#avatar-template',
  components: [
    'position',
    'rotation'
  ]
});
</script>
```

---

## Utilities

### aframe-look-at-component (Built-in)

Make entity face another entity or position.

**Usage**:
```html
<!-- Look at camera -->
<a-text value="Look at me!" look-at="#camera"></a-text>

<!-- Look at position -->
<a-box look-at="0 0 0"></a-box>

<!-- Look at position vector -->
<a-sphere look-at="[camera]"></a-sphere>
```

### aframe-orbit-controls

Orbit camera around scene.

**GitHub**: https://github.com/tizzle/aframe-orbit-controls-component

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-orbit-controls@1.3.2/dist/aframe-orbit-controls.min.js"></script>
```

**Usage**:
```html
<a-camera orbit-controls="
  target: 0 1.5 -3;
  minDistance: 2;
  maxDistance: 100;
  initialPosition: 0 2 5
">
</a-camera>
```

### aframe-alongpath-component

Animate entities along a path.

**GitHub**: https://github.com/protyze/aframe-alongpath-component

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-alongpath-component/dist/aframe-alongpath-component.min.js"></script>
```

**Usage**:
```html
<a-curve id="track">
  <a-curve-point position="0 0 0"></a-curve-point>
  <a-curve-point position="5 5 0"></a-curve-point>
  <a-curve-point position="10 0 0"></a-curve-point>
</a-curve>

<a-entity alongpath="
  path: #track;
  dur: 10000;
  loop: true
">
  <a-box></a-box>
</a-entity>
```

### aframe-click-drag-component

Drag entities with mouse/gaze.

**GitHub**: https://github.com/jesstelford/aframe-click-drag-component

**Installation**:
```html
<script src="https://cdn.jsdelivr.net/npm/aframe-click-drag-component/dist/aframe-click-drag-component.min.js"></script>
```

**Usage**:
```html
<a-camera>
  <a-cursor click-drag></a-cursor>
</a-camera>

<a-box click-drag position="0 1 -3"></a-box>
```

### aframe-teleport-controls (Built-in for Quest)

Teleportation for VR.

**Usage**:
```html
<a-entity
  hand-controls="hand: left"
  teleport-controls="
    cameraRig: #rig;
    teleportOrigin: #camera;
    type: parabolic;
    collisionEntities: [mixin='navmesh']
  ">
</a-entity>
```

---

## Component Registry

Browse thousands of community components:

**A-Frame Registry**: https://aframe.io/registry/

Search components by category:
- Animation
- Audio
- Camera
- Controls
- Cursor
- Effects
- Geometry
- Layout
- Lighting
- Material
- Model
- Physics
- Shaders
- UI
- Utilities

---

## Creating Custom Components

Template for creating reusable components:

```javascript
AFRAME.registerComponent('my-custom-component', {
  schema: {
    speed: {type: 'number', default: 1},
    enabled: {type: 'boolean', default: true}
  },

  init: function() {
    // Setup
  },

  update: function(oldData) {
    // When properties change
  },

  tick: function(time, timeDelta) {
    // Every frame
  },

  remove: function() {
    // Cleanup
  }
});
```

**Share your component**:
1. Publish to npm
2. Submit to A-Frame Registry
3. Add GitHub topic: `aframe-component`

---

This components library provides a solid foundation for extending A-Frame with community-created functionality.



===== FILE: plugins/individual/aframe-webxr/skills/aframe-webxr/references/webxr_guide.md =====

# A-Frame WebXR Integration Guide

Complete guide to building VR and AR experiences with A-Frame and the WebXR API.

## Table of Contents

- [WebXR Overview](#webxr-overview)
- [VR Mode Configuration](#vr-mode-configuration)
- [AR Mode Configuration](#ar-mode-configuration)
- [Controller Systems](#controller-systems)
- [Hand Tracking](#hand-tracking)
- [AR Hit Testing](#ar-hit-testing)
- [Platform Support](#platform-support)
- [Performance Optimization](#performance-optimization)
- [Testing and Debugging](#testing-and-debugging)

---

## WebXR Overview

WebXR is the web standard for VR and AR experiences. A-Frame provides high-level abstractions over the WebXR API.

### Basic WebXR Scene

```html
<!DOCTYPE html>
<html>
  <head>
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
  </head>
  <body>
    <a-scene webxr="requiredFeatures: local-floor">
      <!-- VR content -->
      <a-box position="0 1.5 -3" color="#4CC3D9"></a-box>
      <a-sky color="#ECECEC"></a-sky>
    </a-scene>
  </body>
</html>
```

### WebXR Component Properties

```html
<a-scene webxr="
  requiredFeatures: local-floor, hand-tracking;
  optionalFeatures: hit-test, dom-overlay, unbounded;
  referenceSpaceType: local-floor;
  overlayElement: #overlay
"></a-scene>
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `requiredFeatures` | array | [] | Features that must be available |
| `optionalFeatures` | array | [] | Features to enable if available |
| `referenceSpaceType` | string | local-floor | XR reference space |
| `overlayElement` | selector | - | DOM overlay element (AR) |

### Reference Space Types

- `viewer` - Relative to initial viewer position
- `local` - Origin at starting position, sitting/standing
- `local-floor` - Floor level at Y=0 (recommended for VR)
- `bounded-floor` - Room-scale with boundaries
- `unbounded` - Large spaces, outdoor AR

---

## VR Mode Configuration

### Enable/Disable VR Mode UI

```html
<!-- Show VR button (default) -->
<a-scene vr-mode-ui="enabled: true"></a-scene>

<!-- Hide VR button -->
<a-scene vr-mode-ui="enabled: false"></a-scene>

<!-- Custom enter VR button -->
<a-scene vr-mode-ui="enterVRButton: #myEnterVRButton"></a-scene>

<button id="myEnterVRButton">Enter VR</button>
```

### VR Camera Rig Setup

```html
<a-scene>
  <!-- VR camera rig -->
  <a-entity id="rig" position="0 0 0">
    <!-- Camera for head tracking -->
    <a-camera position="0 1.6 0" look-controls></a-camera>

    <!-- Left controller -->
    <a-entity
      id="leftHand"
      hand-controls="hand: left"
      laser-controls="hand: left">
    </a-entity>

    <!-- Right controller -->
    <a-entity
      id="rightHand"
      hand-controls="hand: right"
      laser-controls="hand: right">
    </a-entity>
  </a-entity>

  <!-- VR content -->
  <a-box position="0 1.5 -3" class="interactive"></a-box>
  <a-plane rotation="-90 0 0" width="10" height="10" color="#7BC8A4"></a-plane>
</a-scene>
```

### VR Session Events

```javascript
const scene = document.querySelector('a-scene');

// Entering VR
scene.addEventListener('enter-vr', () => {
  console.log('Entered VR mode');

  // Check if actually in VR or AR
  if (scene.is('vr-mode')) {
    console.log('VR mode active');
  }

  if (scene.is('ar-mode')) {
    console.log('AR mode active');
  }
});

// Exiting VR
scene.addEventListener('exit-vr', () => {
  console.log('Exited VR mode');
});
```

### Programmatic VR Entry/Exit

```javascript
const scene = document.querySelector('a-scene');

// Enter VR
scene.enterVR();

// Exit VR
scene.exitVR();

// Check if VR is available
if (scene.checkHeadsetConnected()) {
  console.log('VR headset connected');
}
```

### VR-Specific Optimizations

```html
<a-scene
  renderer="
    antialias: false;
    colorManagement: true;
    sortObjects: false;
    physicallyCorrectLights: true;
    maxCanvasWidth: 1920;
    maxCanvasHeight: 1920
  "
  vr-mode-ui="enabled: true">

  <!-- Lower poly models for VR -->
  <a-entity gltf-model="#low-poly-model"></a-entity>

  <!-- Limit lights (expensive in VR) -->
  <a-entity light="type: ambient; intensity: 0.6"></a-entity>
  <a-entity light="type: directional; intensity: 0.4" position="1 2 1"></a-entity>
</a-scene>
```

---

## AR Mode Configuration

### Basic AR Scene Setup

```html
<!DOCTYPE html>
<html>
  <head>
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
  </head>
  <body>
    <a-scene
      webxr="optionalFeatures: hit-test, dom-overlay; overlayElement: #overlay"
      ar-hit-test="target: #model">

      <a-assets>
        <a-asset-item id="chair" src="chair.gltf"></a-asset-item>
      </a-assets>

      <!-- AR object to place -->
      <a-entity id="model" gltf-model="#chair" scale="0.5 0.5 0.5"></a-entity>

      <!-- AR UI overlay -->
      <div id="overlay" style="
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-family: sans-serif;
      ">
        <p id="instructions">Tap to enter AR mode</p>
      </div>
    </a-scene>
  </body>
</html>
```

### AR Hit Test Component

```html
<a-scene
  webxr="optionalFeatures: hit-test"
  ar-hit-test="
    target: #reticle;
    type: footprint;
    src: #reticle-model;
    enabled: true
  ">

  <!-- Reticle for placement preview -->
  <a-entity id="reticle" visible="false"></a-entity>

  <!-- Object to place -->
  <a-entity id="furniture" gltf-model="#chair" visible="false"></a-entity>
</a-scene>
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `target` | selector | - | Entity to place on surface |
| `enabled` | boolean | true | Enable hit testing |
| `src` | selector | - | Custom reticle model |
| `type` | string | footprint | Hit test type (footprint, map) |

### AR Hit Test Events

```javascript
const scene = document.querySelector('a-scene');
const instructions = document.getElementById('instructions');

scene.addEventListener('enter-vr', function() {
  if (this.is('ar-mode')) {
    instructions.textContent = '';

    // Hit testing started (scanning environment)
    this.addEventListener('ar-hit-test-start', function() {
      instructions.textContent = 'Scanning environment, finding surfaces...';
    }, { once: true });

    // Surface detected
    this.addEventListener('ar-hit-test-achieved', function() {
      instructions.textContent = 'Tap to place object';
    }, { once: true });

    // Object placed
    this.addEventListener('ar-hit-test-select', function() {
      instructions.textContent = 'Object placed!';
      setTimeout(() => instructions.textContent = '', 2000);
    }, { once: true });
  }
});

scene.addEventListener('exit-vr', function() {
  instructions.textContent = 'Tap to enter AR mode';
});
```

### AR Lighting Estimation

```html
<a-scene
  reflection="directionalLight: #light"
  webxr="optionalFeatures: light-estimation">

  <!-- Light will be controlled by AR environment -->
  <a-entity
    id="light"
    light="type: directional; castShadow: true"
    position="1 2 1">
  </a-entity>
</a-scene>
```

### AR Real-World Meshing

```html
<a-scene
  webxr="optionalFeatures: mesh-detection"
  real-world-meshing="enabled: true">

  <!-- Detected surfaces will be rendered -->
</a-scene>
```

---

## Controller Systems

### Generic Hand Controls

Works with all VR controllers (Meta Quest, Vive, Index, etc.).

```html
<a-entity id="leftHand"
  hand-controls="hand: left; handModelStyle: lowPoly; color: #ffcccc">
</a-entity>

<a-entity id="rightHand"
  hand-controls="hand: right; handModelStyle: highPoly; color: #ffcccc">
</a-entity>
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `hand` | string | left | Which hand (left, right) |
| `handModelStyle` | string | lowPoly | Model detail (lowPoly, highPoly, toon) |
| `color` | color | white | Hand color |

### Laser Controls

Add laser pointer to controllers for UI interaction.

```html
<a-entity
  hand-controls="hand: right"
  laser-controls="hand: right"
  raycaster="objects: .interactive; far: 10">
</a-entity>

<!-- Interactive object -->
<a-box class="interactive" position="0 1.5 -3"></a-box>
```

### Controller Events

```javascript
const leftHand = document.querySelector('#leftHand');
const rightHand = document.querySelector('#rightHand');

// Trigger button
leftHand.addEventListener('triggerdown', (evt) => {
  console.log('Left trigger pressed');
});

leftHand.addEventListener('triggerup', (evt) => {
  console.log('Left trigger released');
});

// Grip button
rightHand.addEventListener('gripdown', (evt) => {
  console.log('Right grip pressed');
});

rightHand.addEventListener('gripup', (evt) => {
  console.log('Right grip released');
});

// Thumbstick/touchpad
rightHand.addEventListener('thumbstickmoved', (evt) => {
  console.log('Thumbstick:', evt.detail.x, evt.detail.y);
});

rightHand.addEventListener('touchpadmoved', (evt) => {
  console.log('Touchpad:', evt.detail.x, evt.detail.y);
});

// A/B/X/Y buttons
rightHand.addEventListener('abuttondown', () => {
  console.log('A button pressed');
});

rightHand.addEventListener('bbuttondown', () => {
  console.log('B button pressed');
});

leftHand.addEventListener('xbuttondown', () => {
  console.log('X button pressed');
});

leftHand.addEventListener('ybuttondown', () => {
  console.log('Y button pressed');
});
```

### Platform-Specific Controllers

**Meta Quest / Oculus Touch**
```html
<a-entity meta-touch-controls="hand: left; model: true"></a-entity>
<a-entity meta-touch-controls="hand: right; model: true"></a-entity>
```

**HTC Vive**
```html
<a-entity vive-controls="hand: left; buttonColor: #FF0000"></a-entity>
<a-entity vive-controls="hand: right; buttonColor: #0000FF"></a-entity>
```

**Valve Index**
```html
<a-entity valve-index-controls="hand: left"></a-entity>
<a-entity valve-index-controls="hand: right"></a-entity>
```

**Windows Mixed Reality**
```html
<a-entity windows-motion-controls="hand: left"></a-entity>
<a-entity windows-motion-controls="hand: right"></a-entity>
```

### Grabbable Objects Component

```javascript
AFRAME.registerComponent('grabbable', {
  init: function() {
    var el = this.el;
    var grabbing = false;
    var controller = null;

    el.addEventListener('triggerdown', function(evt) {
      if (!grabbing) {
        grabbing = true;
        controller = evt.detail.controller;

        // Attach object to controller
        controller.object3D.attach(el.object3D);

        // Visual feedback
        el.setAttribute('material', 'opacity', 0.7);
      }
    });

    el.addEventListener('triggerup', function(evt) {
      if (grabbing && controller === evt.detail.controller) {
        grabbing = false;

        // Detach from controller
        var sceneEl = el.sceneEl.object3D;
        sceneEl.attach(el.object3D);

        // Reset visual feedback
        el.setAttribute('material', 'opacity', 1);

        controller = null;
      }
    });
  }
});
```

```html
<!-- Apply to objects -->
<a-box class="grabbable" grabbable position="0 1.5 -3"></a-box>
<a-sphere class="grabbable" grabbable position="1 1.5 -3"></a-sphere>
```

---

## Hand Tracking

Native hand tracking without controllers (supported on Meta Quest 2/3/Pro).

### Enable Hand Tracking

```html
<a-scene webxr="requiredFeatures: hand-tracking">
  <!-- Hand tracking entities -->
  <a-entity id="leftHand"
    hand-tracking-controls="hand: left"
    hand-tracking-grab-controls="hand: left">
  </a-entity>

  <a-entity id="rightHand"
    hand-tracking-controls="hand: right"
    hand-tracking-grab-controls="hand: right">
  </a-entity>

  <!-- Grabbable objects -->
  <a-box class="grabbable" position="0 1.5 -3"></a-box>
</a-scene>
```

### Hand Tracking Properties

```html
<a-entity hand-tracking-controls="
  hand: left;
  modelColor: #FF0000;
  modelStyle: mesh
"></a-entity>
```

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `hand` | string | left | Which hand (left, right) |
| `modelColor` | color | white | Hand mesh color |
| `modelStyle` | string | mesh | Visualization (mesh, dots, none) |

### Hand Tracking Events

```javascript
const leftHand = document.querySelector('#leftHand');

// Pinch gesture (thumb + index finger)
leftHand.addEventListener('pinchstarted', (evt) => {
  console.log('Pinch started');
});

leftHand.addEventListener('pinchended', (evt) => {
  console.log('Pinch ended');
});

// Pinch with strength value
leftHand.addEventListener('pinchmoved', (evt) => {
  console.log('Pinch strength:', evt.detail.strength); // 0-1
});
```

### Hand Tracking Grab Controls

```html
<a-scene>
  <!-- Enable hand tracking grab -->
  <a-entity
    hand-tracking-controls="hand: right"
    hand-tracking-grab-controls="hand: right">
  </a-entity>

  <!-- Grabbable object -->
  <a-sphere
    class="grabbable"
    obb-collider="size: 0.2 0.2 0.2"
    grab-options="
      requireGrab: true;
      maxGrabbers: 2
    "
    position="0 1.5 -3">
  </a-sphere>
</a-scene>
```

### Visualize Hand Tracking Colliders (Debug)

```html
<a-scene obb-collider="showColliders: true">
  <!-- Shows bounding boxes for debugging -->
</a-scene>
```

---

## AR Hit Testing

Place virtual objects on detected real-world surfaces.

### Basic AR Hit Test

```html
<a-scene
  webxr="optionalFeatures: hit-test"
  ar-hit-test="target: #model">

  <a-assets>
    <a-asset-item id="furniture" src="chair.gltf"></a-asset-item>
  </a-assets>

  <a-entity id="model" gltf-model="#furniture" scale="0.5 0.5 0.5"></a-entity>
</a-scene>
```

### Custom Reticle

```html
<a-scene
  webxr="optionalFeatures: hit-test"
  ar-hit-test="target: #model; src: #reticle">

  <a-assets>
    <a-asset-item id="reticle-model" src="reticle.gltf"></a-asset-item>
    <a-asset-item id="furniture" src="chair.gltf"></a-asset-item>
  </a-assets>

  <!-- Custom reticle -->
  <a-entity id="reticle" gltf-model="#reticle-model"></a-entity>

  <!-- Object to place -->
  <a-entity id="model" gltf-model="#furniture"></a-entity>
</a-scene>
```

### Multiple Object Placement

```javascript
const scene = document.querySelector('a-scene');
const furniture = document.querySelector('#furniture');
let placedObjects = [];

scene.addEventListener('ar-hit-test-select', function(evt) {
  // Clone object for multiple placements
  const clone = furniture.cloneNode(true);
  clone.removeAttribute('id');
  clone.setAttribute('visible', true);

  // Position at hit point
  const hitPoint = evt.detail.position;
  clone.setAttribute('position', hitPoint);

  scene.appendChild(clone);
  placedObjects.push(clone);

  console.log('Placed object at:', hitPoint);
});

// Clear all placed objects
function clearObjects() {
  placedObjects.forEach(obj => obj.parentNode.removeChild(obj));
  placedObjects = [];
}
```

### AR with DOM Overlay

```html
<a-scene
  webxr="optionalFeatures: hit-test, dom-overlay; overlayElement: #overlay"
  ar-hit-test="target: #model">

  <a-entity id="model" gltf-model="#furniture"></a-entity>

  <!-- HTML UI overlay -->
  <div id="overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;">
    <div style="position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
                background: rgba(0,0,0,0.7); color: white; padding: 15px; border-radius: 8px; pointer-events: auto;">
      <p id="instructions">Tap to enter AR</p>
      <button id="clearBtn" style="margin-top: 10px; padding: 10px 20px; pointer-events: auto;">Clear Objects</button>
    </div>
  </div>
</a-scene>

<script>
const clearBtn = document.getElementById('clearBtn');
clearBtn.addEventListener('click', clearObjects);
</script>
```

---

## Platform Support

### Meta Quest (Standalone)

Optimizations for Quest 2/3/Pro:

```html
<a-scene
  renderer="antialias: false; physicallyCorrectLights: false"
  vr-mode-ui="enabled: true">

  <!-- Use low-poly models -->
  <a-entity gltf-model="#low-poly-model"></a-entity>

  <!-- Limit lights (1-2 max) -->
  <a-entity light="type: ambient; intensity: 0.7"></a-entity>
  <a-entity light="type: directional; intensity: 0.3" position="1 2 1"></a-entity>

  <!-- Texture size limits -->
  <a-entity material="src: #texture; repeat: 1 1"></a-entity>
</a-scene>
```

### Desktop VR (PC + Headset)

Higher quality settings for PC VR:

```html
<a-scene
  renderer="antialias: true; colorManagement: true; physicallyCorrectLights: true"
  fog="type: linear; color: #AAA; near: 10; far: 100">

  <!-- High-poly models allowed -->
  <a-entity gltf-model="#high-poly-model"></a-entity>

  <!-- Multiple lights OK -->
  <a-entity light="type: ambient; intensity: 0.5"></a-entity>
  <a-entity light="type: directional; intensity: 0.8" position="2 4 2"></a-entity>
  <a-entity light="type: point; intensity: 1.5; distance: 20" position="5 2 5"></a-entity>
</a-scene>
```

### Mobile AR (iOS/Android)

Optimizations for mobile AR:

```html
<a-scene
  webxr="optionalFeatures: hit-test, dom-overlay, light-estimation"
  ar-hit-test="target: #model"
  renderer="antialias: false; maxCanvasWidth: 1920; maxCanvasHeight: 1920">

  <!-- Lightweight models for mobile -->
  <a-entity gltf-model="#mobile-optimized-model"></a-entity>

  <!-- Minimal lighting -->
  <a-entity light="type: ambient; intensity: 0.8"></a-entity>
</a-scene>
```

### Feature Detection

```javascript
// Check WebXR support
if ('xr' in navigator) {
  navigator.xr.isSessionSupported('immersive-vr').then((supported) => {
    if (supported) {
      console.log('VR supported');
    }
  });

  navigator.xr.isSessionSupported('immersive-ar').then((supported) => {
    if (supported) {
      console.log('AR supported');
    }
  });
}

// Check hand tracking support
const scene = document.querySelector('a-scene');
scene.addEventListener('loaded', () => {
  if (scene.systems['hand-tracking-controls']) {
    console.log('Hand tracking available');
  }
});
```

---

## Performance Optimization

### Reduce Draw Calls

```javascript
// Use instancing for repeated objects
AFRAME.registerComponent('instanced-forest', {
  init: function() {
    const scene = this.el.sceneEl.object3D;
    const geometry = new THREE.CylinderGeometry(0.2, 0.5, 3, 8);
    const material = new THREE.MeshStandardMaterial({ color: 0x8B4513 });
    const instancedMesh = new THREE.InstancedMesh(geometry, material, 100);

    // Position instances
    for (let i = 0; i < 100; i++) {
      const matrix = new THREE.Matrix4();
      matrix.setPosition(
        Math.random() * 20 - 10,
        0,
        Math.random() * 20 - 10
      );
      instancedMesh.setMatrixAt(i, matrix);
    }

    scene.add(instancedMesh);
  }
});
```

### Optimize Geometry

```html
<!-- Low poly count for VR/mobile -->
<a-sphere radius="1" segments-width="8" segments-height="6"></a-sphere>

<!-- High poly only for close-up objects -->
<a-sphere radius="1" segments-width="32" segments-height="32"></a-sphere>
```

### Texture Optimization

```javascript
// Compress textures
// Use power-of-2 sizes (256, 512, 1024, 2048)
// Use lower resolutions for mobile

// Lazy load textures
AFRAME.registerComponent('lazy-texture', {
  schema: {
    src: {type: 'string'}
  },

  init: function() {
    const el = this.el;
    const src = this.data.src;

    // Load texture when entity is near camera
    this.el.sceneEl.addEventListener('camera-move', () => {
      const distance = el.object3D.position.distanceTo(
        el.sceneEl.camera.position
      );

      if (distance < 10 && !el.getAttribute('material').src) {
        el.setAttribute('material', 'src', src);
      }
    });
  }
});
```

### Limit Physics

```html
<!-- Only enable physics for interactive objects -->
<a-entity
  geometry="primitive: box"
  ammo-body="type: dynamic; mass: 1"
  ammo-shape="type: box">
</a-entity>
```

### Throttle Updates

```javascript
AFRAME.registerComponent('throttled-rotation', {
  init: function() {
    this.lastUpdate = 0;
    this.updateInterval = 100; // Update every 100ms instead of every frame
  },

  tick: function(time, timeDelta) {
    if (time - this.lastUpdate >= this.updateInterval) {
      // Expensive operation
      this.el.object3D.rotation.y += 0.01;
      this.lastUpdate = time;
    }
  }
});
```

---

## Testing and Debugging

### Desktop Testing

```html
<!-- Test without VR headset using desktop mode -->
<a-scene vr-mode-ui="enabled: true">
  <!-- WASD to move, mouse to look -->
  <a-camera wasd-controls look-controls></a-camera>
</a-scene>
```

### Mobile Testing

```html
<!-- Test AR on mobile browser -->
<a-scene
  webxr="optionalFeatures: hit-test"
  ar-hit-test="target: #model">

  <!-- Use browser DevTools device emulation -->
</a-scene>
```

### Stats and Debugging

```html
<!-- Show FPS and performance stats -->
<a-scene stats>
  <!-- Stats panel appears in top-left -->
</a-scene>

<!-- Enable inspector (Ctrl+Alt+I) -->
<a-scene inspector>
  <!-- Visual scene editor -->
</a-scene>
```

### Console Logging

```javascript
// Log XR session info
const scene = document.querySelector('a-scene');

scene.addEventListener('enter-vr', () => {
  const renderer = scene.renderer;
  const session = renderer.xr.getSession();

  console.log('XR Session:', session);
  console.log('Reference space:', scene.systems.webxr.sessionReferenceSpaceType);
  console.log('Frame rate:', session.frameRate);
});
```

### Remote Debugging

**For Meta Quest:**
1. Enable Developer Mode in Quest settings
2. Connect via USB to computer
3. Use Chrome DevTools (chrome://inspect)

**For iOS:**
1. Enable Web Inspector in Safari settings
2. Connect iPhone/iPad to Mac
3. Use Safari Developer menu

### Performance Profiling

```javascript
// Monitor frame times
const scene = document.querySelector('a-scene');
let frameCount = 0;
let lastTime = performance.now();

scene.addEventListener('renderstart', () => {
  const now = performance.now();
  frameCount++;

  if (now - lastTime >= 1000) {
    console.log('FPS:', frameCount);
    frameCount = 0;
    lastTime = now;
  }
});
```

---

## Common Issues

### Issue: VR button not appearing
**Solution**: Check HTTPS (required for WebXR)

### Issue: Controllers not tracking
**Solution**: Check permissions, ensure proper lighting

### Issue: AR not working on mobile
**Solution**: Use Chrome/Safari, check camera permissions

### Issue: Low FPS in VR
**Solution**: Reduce geometry, limit lights, optimize textures

### Issue: Hand tracking not working
**Solution**: Enable in headset settings, ensure good lighting

---

## Resources

- [WebXR Device API Specification](https://www.w3.org/TR/webxr/)
- [A-Frame WebXR Documentation](https://aframe.io/docs/1.7.0/introduction/webxr.html)
- [Meta Quest Development](https://developer.oculus.com/)
- [WebXR Samples](https://immersive-web.github.io/webxr-samples/)
- [Mozilla Mixed Reality Blog](https://mixedreality.mozilla.org/)

---

This guide covers all aspects of building WebXR experiences with A-Frame, from basic VR scenes to advanced AR features.



===== FILE: plugins/individual/aframe-webxr/agents/aframe-webxr-architect.md =====

# A-Frame WebXR Architect

## Role

Expert 3D/graphics architect specializing in A-Frame WebXR scene design, optimization, and best practices.

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
3. Implement best practices from A-Frame WebXR ecosystem
4. Optimize for target platforms and devices
5. Provide detailed implementation guidance

## Tools

This agent has access to:
- A-Frame WebXR skill knowledge
- Optimization checklists and patterns
- Performance profiling guidance
- Asset pipeline recommendations



===== FILE: plugins/individual/aframe-webxr/commands/component_builder.md =====

# /aframe-webxr-component_builder

A-Frame WebXR - Component Builder

## Description

Executes the component_builder script for A-Frame WebXR.

## Usage

```bash
/aframe-webxr-component_builder
```

## Implementation

This command runs the `component_builder.py` script from the A-Frame WebXR skill, which provides automated assistance for component builder.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/aframe-webxr/commands/scene_generator.md =====

# /aframe-webxr-scene_generator

A-Frame WebXR - Scene Generator

## Description

Executes the scene_generator script for A-Frame WebXR.

## Usage

```bash
/aframe-webxr-scene_generator
```

## Implementation

This command runs the `scene_generator.py` script from the A-Frame WebXR skill, which provides automated assistance for scene generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/aframe-webxr/skills/aframe-webxr/scripts/component_builder.py =====

```py
#!/usr/bin/env python3
"""
A-Frame Component Builder

Generates custom A-Frame component boilerplate for various use cases:
- Basic components
- Interactive components (hover, click)
- Animation components
- Physics-based components
- Networked components
- VR controller components

Usage:
    python component_builder.py basic my-component
    python component_builder.py interactive clickable-box
    python component_builder.py animation rotating-cube
    python component_builder.py --interactive
"""

import argparse
import sys
from pathlib import Path

# Component templates
COMPONENT_TEMPLATES = {
    'basic': {
        'description': 'Basic component with schema and lifecycle',
        'schema_props': ['enabled: boolean', 'speed: number'],
        'has_tick': False
    },
    'interactive': {
        'description': 'Component with mouse/VR interaction events',
        'schema_props': ['hoverColor: color', 'clickColor: color'],
        'has_tick': False
    },
    'animation': {
        'description': 'Component with tick() for continuous animation',
        'schema_props': ['speed: number', 'axis: string'],
        'has_tick': True
    },
    'physics': {
        'description': 'Component for physics interactions',
        'schema_props': ['force: number', 'direction: vec3'],
        'has_tick': True
    },
    'controller': {
        'description': 'VR controller interaction component',
        'schema_props': ['hand: string', 'button: string'],
        'has_tick': False
    },
    'networked': {
        'description': 'Networked component for multi-user scenes',
        'schema_props': ['syncInterval: number', 'owner: string'],
        'has_tick': True
    },
    'loader': {
        'description': 'Asset loading component',
        'schema_props': ['src: string', 'onLoad: string'],
        'has_tick': False
    }
}

def generate_basic_component(name):
    """Generate basic component template"""
    component_name = name.replace('_', '-')
    return f'''// {component_name} Component
// Basic A-Frame component with schema and lifecycle methods

AFRAME.registerComponent('{component_name}', {{
  // Component schema (configuration properties)
  schema: {{
    enabled: {{ type: 'boolean', default: true }},
    speed: {{ type: 'number', default: 1 }},
    color: {{ type: 'color', default: '#FFF' }}
  }},

  // Initialize (called once when component is attached)
  init: function() {{
    console.log('{component_name} initialized');

    // Store references
    this.el; // The entity element
    this.data; // Component data from schema
    this.el.sceneEl; // The scene element

    // Setup code here
  }},

  // Update (called when component properties change)
  update: function(oldData) {{
    // this.data contains new values
    // oldData contains previous values

    if (this.data.enabled !== oldData.enabled) {{
      console.log('Enabled changed to:', this.data.enabled);
    }}

    if (this.data.speed !== oldData.speed) {{
      console.log('Speed changed to:', this.data.speed);
    }}
  }},

  // Remove (called when component is removed from entity)
  remove: function() {{
    // Cleanup code here
    console.log('{component_name} removed');
  }},

  // Pause (called when entity/scene pauses)
  pause: function() {{
    console.log('{component_name} paused');
  }},

  // Play (called when entity/scene plays)
  play: function() {{
    console.log('{component_name} playing');
  }}
}});

// Usage:
// <a-entity {component_name}="enabled: true; speed: 2; color: #FF0000"></a-entity>
'''

def generate_interactive_component(name):
    """Generate interactive component with events"""
    component_name = name.replace('_', '-')
    return f'''// {component_name} Component
// Interactive component with mouse and VR controller events

AFRAME.registerComponent('{component_name}', {{
  schema: {{
    hoverColor: {{ type: 'color', default: '#FFFF00' }},
    clickColor: {{ type: 'color', default: '#FF0000' }},
    enabled: {{ type: 'boolean', default: true }}
  }},

  init: function() {{
    const el = this.el;
    const data = this.data;

    // Store original color
    this.originalColor = el.getAttribute('material').color;

    // Bind event handlers (important for proper 'this' context)
    this.onMouseEnter = this.onMouseEnter.bind(this);
    this.onMouseLeave = this.onMouseLeave.bind(this);
    this.onClick = this.onClick.bind(this);

    // Add event listeners
    el.addEventListener('mouseenter', this.onMouseEnter);
    el.addEventListener('mouseleave', this.onMouseLeave);
    el.addEventListener('click', this.onClick);

    // VR controller events
    el.addEventListener('triggerdown', this.onClick);
  }},

  update: function(oldData) {{
    // Update behavior based on enabled state
    if (!this.data.enabled && oldData.enabled) {{
      // Reset to original color when disabled
      this.el.setAttribute('material', 'color', this.originalColor);
    }}
  }},

  onMouseEnter: function(evt) {{
    if (!this.data.enabled) return;

    console.log('Mouse entered');
    this.el.setAttribute('material', 'color', this.data.hoverColor);
    this.el.setAttribute('scale', {{
      x: 1.1,
      y: 1.1,
      z: 1.1
    }});
  }},

  onMouseLeave: function(evt) {{
    if (!this.data.enabled) return;

    console.log('Mouse left');
    this.el.setAttribute('material', 'color', this.originalColor);
    this.el.setAttribute('scale', {{
      x: 1,
      y: 1,
      z: 1
    }});
  }},

  onClick: function(evt) {{
    if (!this.data.enabled) return;

    console.log('Clicked!', evt.detail);
    this.el.setAttribute('material', 'color', this.data.clickColor);

    // Emit custom event
    this.el.emit('{component_name}-clicked', {{
      position: evt.detail.intersection ? evt.detail.intersection.point : null
    }});

    // Reset color after 500ms
    setTimeout(() => {{
      this.el.setAttribute('material', 'color', this.originalColor);
    }}, 500);
  }},

  remove: function() {{
    // Remove event listeners
    const el = this.el;
    el.removeEventListener('mouseenter', this.onMouseEnter);
    el.removeEventListener('mouseleave', this.onMouseLeave);
    el.removeEventListener('click', this.onClick);
    el.removeEventListener('triggerdown', this.onClick);
  }}
}});

// Usage:
// <a-camera>
//   <a-cursor raycaster="objects: .interactive"></a-cursor>
// </a-camera>
// <a-box class="interactive" {component_name}="hoverColor: yellow; clickColor: red"></a-box>
'''

def generate_animation_component(name):
    """Generate animation component with tick()"""
    component_name = name.replace('_', '-')
    return f'''// {component_name} Component
// Animation component using tick() for continuous updates

AFRAME.registerComponent('{component_name}', {{
  schema: {{
    speed: {{ type: 'number', default: 1 }},
    axis: {{ type: 'string', default: 'y', oneOf: ['x', 'y', 'z'] }},
    enabled: {{ type: 'boolean', default: true }}
  }},

  init: function() {{
    // Store rotation state
    this.rotation = {{
      x: 0,
      y: 0,
      z: 0
    }};
  }},

  // tick() is called every frame
  tick: function(time, timeDelta) {{
    if (!this.data.enabled) return;

    // timeDelta is time since last frame (milliseconds)
    // Use it for frame-rate independent animation
    const rotationAmount = this.data.speed * (timeDelta / 1000);

    // Update rotation based on axis
    this.rotation[this.data.axis] += rotationAmount;

    // Apply rotation to entity
    this.el.object3D.rotation[this.data.axis] = this.rotation[this.data.axis];
  }},

  pause: function() {{
    // Stop animation when paused
  }},

  play: function() {{
    // Resume animation when playing
  }}
}});

// Usage:
// <a-box {component_name}="speed: 2; axis: y"></a-box>
// <a-sphere {component_name}="speed: 0.5; axis: x; enabled: false"></a-sphere>
'''

def generate_physics_component(name):
    """Generate physics-based component"""
    component_name = name.replace('_', '-')
    return f'''// {component_name} Component
// Physics-based component (requires aframe-physics-system)

AFRAME.registerComponent('{component_name}', {{
  schema: {{
    force: {{ type: 'number', default: 10 }},
    direction: {{ type: 'vec3', default: {{ x: 0, y: 1, z: 0 }} }},
    trigger: {{ type: 'string', default: 'click' }}
  }},

  dependencies: ['dynamic-body'], // Requires physics body

  init: function() {{
    const el = this.el;
    const data = this.data;

    // Wait for physics body to be ready
    el.addEventListener('body-loaded', () => {{
      this.body = el.body; // Access Ammo.js physics body
    }});

    // Bind trigger event
    this.applyForce = this.applyForce.bind(this);

    if (data.trigger === 'click') {{
      el.addEventListener('click', this.applyForce);
    }} else if (data.trigger === 'mouseenter') {{
      el.addEventListener('mouseenter', this.applyForce);
    }}
  }},

  applyForce: function(evt) {{
    if (!this.body) return;

    const force = this.data.force;
    const direction = this.data.direction;

    // Apply impulse force
    const impulse = new Ammo.btVector3(
      direction.x * force,
      direction.y * force,
      direction.z * force
    );

    const position = new Ammo.btVector3(0, 0, 0);

    this.body.applyImpulse(impulse, position);

    console.log('Force applied:', force);

    // Clean up Ammo.js objects
    Ammo.destroy(impulse);
    Ammo.destroy(position);
  }},

  tick: function(time, timeDelta) {{
    // Optional: Add continuous forces or check physics state
  }},

  remove: function() {{
    const el = this.el;
    if (this.data.trigger === 'click') {{
      el.removeEventListener('click', this.applyForce);
    }} else if (this.data.trigger === 'mouseenter') {{
      el.removeEventListener('mouseenter', this.applyForce);
    }}
  }}
}});

// Usage (requires aframe-physics-system):
// <a-scene physics>
//   <a-sphere
//     dynamic-body
//     {component_name}="force: 20; direction: 0 1 0; trigger: click"
//     position="0 2 -3">
//   </a-sphere>
// </a-scene>
'''

def generate_controller_component(name):
    """Generate VR controller component"""
    component_name = name.replace('_', '-')
    return f'''// {component_name} Component
// VR controller interaction component

AFRAME.registerComponent('{component_name}', {{
  schema: {{
    hand: {{ type: 'string', default: 'right', oneOf: ['left', 'right'] }},
    button: {{ type: 'string', default: 'trigger', oneOf: ['trigger', 'grip', 'thumbstick', 'abutton', 'bbutton'] }}
  }},

  init: function() {{
    const el = this.el;
    const data = this.data;

    console.log(`Initializing controller component for ${{data.hand}} hand`);

    // Bind event handlers
    this.onButtonDown = this.onButtonDown.bind(this);
    this.onButtonUp = this.onButtonUp.bind(this);
    this.onButtonChanged = this.onButtonChanged.bind(this);

    // Listen to button events
    const buttonDownEvent = data.button + 'down';
    const buttonUpEvent = data.button + 'up';
    const buttonChangedEvent = data.button + 'changed';

    el.addEventListener(buttonDownEvent, this.onButtonDown);
    el.addEventListener(buttonUpEvent, this.onButtonUp);
    el.addEventListener(buttonChangedEvent, this.onButtonChanged);

    // Controller-specific events
    el.addEventListener('controllerconnected', (evt) => {{
      console.log('Controller connected:', evt.detail.name);
    }});
  }},

  onButtonDown: function(evt) {{
    console.log(`${{this.data.button}} pressed on ${{this.data.hand}} hand`);

    // Example: Raycast from controller
    const raycaster = this.el.components.raycaster;
    if (raycaster) {{
      const intersections = raycaster.intersections;
      if (intersections.length > 0) {{
        const target = intersections[0].object.el;
        console.log('Hit:', target);

        // Emit event on hit object
        target.emit('controller-hit', {{
          hand: this.data.hand,
          button: this.data.button,
          intersection: intersections[0]
        }});
      }}
    }}
  }},

  onButtonUp: function(evt) {{
    console.log(`${{this.data.button}} released on ${{this.data.hand}} hand`);
  }},

  onButtonChanged: function(evt) {{
    // For analog buttons (triggers, thumbsticks)
    const state = evt.detail.state;
    console.log(`${{this.data.button}} state:`, state);
  }},

  remove: function() {{
    const el = this.el;
    const data = this.data;

    const buttonDownEvent = data.button + 'down';
    const buttonUpEvent = data.button + 'up';
    const buttonChangedEvent = data.button + 'changed';

    el.removeEventListener(buttonDownEvent, this.onButtonDown);
    el.removeEventListener(buttonUpEvent, this.onButtonUp);
    el.removeEventListener(buttonChangedEvent, this.onButtonChanged);
  }}
}});

// Usage:
// <a-entity hand-controls="hand: right"
//           laser-controls
//           {component_name}="hand: right; button: trigger">
// </a-entity>
'''

def generate_networked_component(name):
    """Generate networked component"""
    component_name = name.replace('_', '-')
    return f'''// {component_name} Component
// Networked component for multi-user synchronization (requires networked-aframe)

AFRAME.registerComponent('{component_name}', {{
  schema: {{
    syncInterval: {{ type: 'number', default: 50 }}, // milliseconds
    owner: {{ type: 'string', default: '' }}
  }},

  init: function() {{
    const el = this.el;

    // Check if this is the local player's entity
    this.isLocal = NAF.utils.isMine(el);

    console.log('Networked component init:', this.isLocal ? 'LOCAL' : 'REMOTE');

    // Last sync time
    this.lastSync = 0;

    // Custom networked data
    this.networkData = {{
      customProperty: 'value'
    }};

    // Listen to networked events
    el.addEventListener('connected', () => {{
      console.log('Entity connected to network');
    }});

    el.addEventListener('disconnected', () => {{
      console.log('Entity disconnected from network');
    }});

    // Listen to ownership changes
    NAF.utils.getNetworkedEntity(el).then(networkedEl => {{
      networkedEl.addEventListener('ownership-gained', () => {{
        console.log('Gained ownership');
        this.isLocal = true;
      }});

      networkedEl.addEventListener('ownership-lost', () => {{
        console.log('Lost ownership');
        this.isLocal = false;
      }});
    }});
  }},

  tick: function(time, timeDelta) {{
    if (!this.isLocal) return;

    // Sync at specified interval
    if (time - this.lastSync >= this.data.syncInterval) {{
      this.syncState();
      this.lastSync = time;
    }}
  }},

  syncState: function() {{
    // Broadcast custom state to other clients
    const el = this.el;

    // Update networked components
    NAF.utils.getNetworkedEntity(el).then(networkedEl => {{
      // Sync custom data
      networkedEl.emit('sync-data', this.networkData);
    }});
  }},

  // Call this to take ownership of the entity
  takeOwnership: function() {{
    NAF.utils.takeOwnership(this.el);
  }},

  remove: function() {{
    console.log('Networked component removed');
  }}
}});

// Usage (requires networked-aframe):
// <a-scene networked-scene="room: myRoom; adapter: wseasyrtc">
//   <a-entity networked="template: #avatar-template"
//             {component_name}="syncInterval: 100">
//   </a-entity>
// </a-scene>
'''

def generate_loader_component(name):
    """Generate asset loading component"""
    component_name = name.replace('_', '-')
    return f'''// {component_name} Component
// Asset loading component with progress and error handling

AFRAME.registerComponent('{component_name}', {{
  schema: {{
    src: {{ type: 'string', default: '' }},
    onLoad: {{ type: 'string', default: '' }}, // Event name to emit
    showProgress: {{ type: 'boolean', default: true }}
  }},

  init: function() {{
    const el = this.el;
    const data = this.data;

    if (!data.src) {{
      console.warn('{component_name}: No src specified');
      return;
    }}

    this.loading = true;
    this.loaded = false;

    // Start loading
    this.loadAsset(data.src);
  }},

  update: function(oldData) {{
    // Reload if src changes
    if (this.data.src !== oldData.src && this.data.src) {{
      this.loadAsset(this.data.src);
    }}
  }},

  loadAsset: function(src) {{
    const el = this.el;
    const data = this.data;

    console.log('Loading asset:', src);

    // Determine asset type from extension
    const extension = src.split('.').pop().toLowerCase();

    if (['gltf', 'glb'].includes(extension)) {{
      this.loadModel(src);
    }} else if (['jpg', 'jpeg', 'png', 'gif'].includes(extension)) {{
      this.loadImage(src);
    }} else {{
      console.warn('Unsupported asset type:', extension);
    }}
  }},

  loadModel: function(src) {{
    const el = this.el;

    // Use A-Frame's asset system
    const loader = new THREE.GLTFLoader();

    loader.load(
      src,
      // onLoad
      (gltf) => {{
        console.log('Model loaded:', src);
        this.onAssetLoaded(gltf);
        el.setObject3D('mesh', gltf.scene);
      }},
      // onProgress
      (xhr) => {{
        const percentComplete = (xhr.loaded / xhr.total * 100);
        if (this.data.showProgress) {{
          console.log(`Loading: ${{percentComplete.toFixed(2)}}%`);
        }}
        el.emit('loading-progress', {{ percent: percentComplete }});
      }},
      // onError
      (error) => {{
        console.error('Error loading model:', error);
        this.onAssetError(error);
      }}
    );
  }},

  loadImage: function(src) {{
    const el = this.el;

    const textureLoader = new THREE.TextureLoader();

    textureLoader.load(
      src,
      // onLoad
      (texture) => {{
        console.log('Image loaded:', src);
        this.onAssetLoaded(texture);
        el.setAttribute('material', 'src', texture);
      }},
      // onProgress
      (xhr) => {{
        const percentComplete = (xhr.loaded / xhr.total * 100);
        if (this.data.showProgress) {{
          console.log(`Loading: ${{percentComplete.toFixed(2)}}%`);
        }}
        el.emit('loading-progress', {{ percent: percentComplete }});
      }},
      // onError
      (error) => {{
        console.error('Error loading image:', error);
        this.onAssetError(error);
      }}
    );
  }},

  onAssetLoaded: function(asset) {{
    this.loading = false;
    this.loaded = true;

    // Emit custom event
    if (this.data.onLoad) {{
      this.el.emit(this.data.onLoad, {{ asset: asset }});
    }}

    // Emit standard event
    this.el.emit('asset-loaded', {{ asset: asset }});
  }},

  onAssetError: function(error) {{
    this.loading = false;
    this.loaded = false;

    this.el.emit('asset-error', {{ error: error }});
  }}
}});

// Usage:
// <a-entity {component_name}="src: model.gltf; onLoad: model-ready; showProgress: true"></a-entity>
// <a-entity {component_name}="src: texture.jpg"></a-entity>
'''

def generate_component(component_type, name):
    """Generate component based on type"""
    generators = {
        'basic': generate_basic_component,
        'interactive': generate_interactive_component,
        'animation': generate_animation_component,
        'physics': generate_physics_component,
        'controller': generate_controller_component,
        'networked': generate_networked_component,
        'loader': generate_loader_component
    }

    return generators[component_type](name)

def interactive_mode():
    """Interactive component builder"""
    print("\n=== A-Frame Component Builder (Interactive Mode) ===\n")

    print("Available component types:")
    for i, (comp_type, config) in enumerate(COMPONENT_TEMPLATES.items(), 1):
        print(f"  {i}. {comp_type:12} - {config['description']}")

    while True:
        try:
            choice = input("\nSelect component type (1-7): ").strip()
            component_type = list(COMPONENT_TEMPLATES.keys())[int(choice) - 1]
            break
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a number between 1 and 7.")

    name = input("Enter component name (e.g., my-component): ").strip()
    if not name:
        print("Error: Component name is required")
        return

    output_file = input("Enter output filename (default: component.js): ").strip() or "component.js"

    save_component(component_type, name, output_file)

def save_component(component_type, name, output_file):
    """Save generated component to file"""
    component_code = generate_component(component_type, name)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(component_code)

    print(f"\n✅ Generated {component_type} component: {output_path}")
    print(f"📝 Component name: {name.replace('_', '-')}")
    print(f"🎯 Template: {COMPONENT_TEMPLATES[component_type]['description']}")
    print(f"\n🚀 To use:")
    print(f"   1. Include in HTML: <script src=\"{output_file}\"></script>")
    print(f"   2. Attach to entity: <a-entity {name.replace('_', '-')}></a-entity>")

def main():
    parser = argparse.ArgumentParser(
        description='Generate A-Frame custom component boilerplate',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python component_builder.py basic my-component
  python component_builder.py interactive clickable-box --output components/
  python component_builder.py animation rotating-object
  python component_builder.py --interactive

Component Types:
  basic       - Basic component with schema
  interactive - Mouse/VR interaction events
  animation   - Continuous animation with tick()
  physics     - Physics-based interactions
  controller  - VR controller component
  networked   - Multi-user synchronization
  loader      - Asset loading with progress
        '''
    )

    parser.add_argument(
        'component_type',
        nargs='?',
        choices=list(COMPONENT_TEMPLATES.keys()),
        help='Type of component to generate'
    )

    parser.add_argument(
        'name',
        nargs='?',
        help='Name of the component (e.g., my-component)'
    )

    parser.add_argument(
        '-o', '--output',
        default='component.js',
        help='Output filename (default: component.js)'
    )

    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )

    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='List available component types'
    )

    args = parser.parse_args()

    if args.list:
        print("\nAvailable Component Types:\n")
        for comp_type, config in COMPONENT_TEMPLATES.items():
            print(f"  {comp_type:12} - {config['description']}")
            print(f"                 Schema props: {', '.join(config['schema_props'])}")
            print(f"                 Has tick(): {'Yes' if config['has_tick'] else 'No'}\n")
        sys.exit(0)

    if args.interactive or not args.component_type or not args.name:
        interactive_mode()
    else:
        save_component(args.component_type, args.name, args.output)

if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/aframe-webxr/skills/aframe-webxr/scripts/scene_generator.py =====

```py
#!/usr/bin/env python3
"""
A-Frame Scene Generator

Generates A-Frame scene boilerplate for different use cases:
- Basic 3D scenes
- VR experiences with controllers
- AR experiences with hit testing
- 360° photo/video viewers
- Multi-user networked scenes

Usage:
    python scene_generator.py basic MyScene
    python scene_generator.py vr VRProject
    python scene_generator.py ar ARFurniture
    python scene_generator.py 360 Gallery360
    python scene_generator.py --interactive
"""

import argparse
import sys
import os
from pathlib import Path

# Scene type configurations
SCENE_TYPES = {
    'basic': {
        'description': 'Basic 3D scene with primitives and camera',
        'features': ['primitives', 'lighting', 'sky', 'camera'],
        'filename': 'index.html'
    },
    'vr': {
        'description': 'VR scene with hand controllers and interactions',
        'features': ['vr-rig', 'controllers', 'teleportation', 'interactive-objects'],
        'filename': 'index.html'
    },
    'ar': {
        'description': 'AR scene with hit testing and object placement',
        'features': ['ar-hit-test', 'dom-overlay', 'models'],
        'filename': 'index.html'
    },
    '360': {
        'description': '360° photo/video gallery viewer',
        'features': ['360-sky', 'thumbnails', 'navigation'],
        'filename': 'index.html'
    },
    'networked': {
        'description': 'Multi-user networked scene with avatars',
        'features': ['networked-aframe', 'avatars', 'voice-chat'],
        'filename': 'index.html'
    },
    'physics': {
        'description': 'Scene with physics simulation',
        'features': ['physics', 'dynamic-objects', 'interactive'],
        'filename': 'index.html'
    },
    'environment': {
        'description': 'Procedural environment with effects',
        'features': ['environment', 'particles', 'effects'],
        'filename': 'index.html'
    }
}

def generate_basic_scene(name):
    """Generate basic 3D scene"""
    return f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{name} - A-Frame Basic Scene</title>
    <meta name="description" content="{name} - A-Frame VR">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
    <style>
      body {{ margin: 0; }}
      #info {{
        position: absolute;
        bottom: 20px;
        left: 20px;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-family: sans-serif;
        font-size: 14px;
      }}
    </style>
  </head>
  <body>
    <a-scene>
      <!-- Assets -->
      <a-assets>
        <!-- Preload assets here -->
      </a-assets>

      <!-- Environment -->
      <a-sky color="#ECECEC"></a-sky>
      <a-plane
        rotation="-90 0 0"
        width="20"
        height="20"
        color="#7BC8A4">
      </a-plane>

      <!-- Lighting -->
      <a-entity light="type: ambient; color: #888; intensity: 0.5"></a-entity>
      <a-entity light="type: directional; color: #FFF; intensity: 0.8" position="2 4 2"></a-entity>

      <!-- Objects -->
      <a-box
        position="-1 0.5 -3"
        rotation="0 45 0"
        color="#4CC3D9"
        shadow>
      </a-box>

      <a-sphere
        position="0 1.25 -5"
        radius="1.25"
        color="#EF2D5E"
        shadow>
      </a-sphere>

      <a-cylinder
        position="1 0.75 -3"
        radius="0.5"
        height="1.5"
        color="#FFC65D"
        shadow>
      </a-cylinder>

      <!-- Camera -->
      <a-camera position="0 1.6 0" look-controls wasd-controls>
        <a-cursor></a-cursor>
      </a-camera>
    </a-scene>

    <div id="info">
      <strong>{name}</strong><br>
      WASD - Move | Mouse - Look
    </div>
  </body>
</html>'''

def generate_vr_scene(name):
    """Generate VR scene with controllers"""
    return f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{name} - A-Frame VR Experience</title>
    <meta name="description" content="{name} - VR Experience">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/aframe-blink-controls/dist/aframe-blink-controls.min.js"></script>
    <style>
      body {{ margin: 0; }}
    </style>
  </head>
  <body>
    <a-scene>
      <!-- Assets -->
      <a-assets>
        <audio id="click-sound" src="https://cdn.aframe.io/360-image-gallery-boilerplate/audio/click.ogg"></audio>
      </a-assets>

      <!-- Environment -->
      <a-sky color="#87CEEB"></a-sky>
      <a-plane
        class="ground"
        rotation="-90 0 0"
        width="50"
        height="50"
        color="#3D5E1F"
        shadow="receive: true">
      </a-plane>

      <!-- Lighting -->
      <a-entity light="type: ambient; color: #BBB; intensity: 0.6"></a-entity>
      <a-entity light="type: directional; color: #FFF; intensity: 0.5; castShadow: true" position="5 10 5"></a-entity>

      <!-- Interactive Objects -->
      <a-box
        class="interactive"
        position="-1 0.5 -3"
        color="#4CC3D9"
        event-set__mouseenter="scale: 1.2 1.2 1.2"
        event-set__mouseleave="scale: 1 1 1"
        sound="on: click; src: #click-sound"
        shadow="cast: true">
      </a-box>

      <a-sphere
        class="interactive"
        position="1 1.25 -3"
        radius="0.5"
        color="#EF2D5E"
        event-set__click="color: orange; scale: 1.5 1.5 1.5"
        sound="on: click; src: #click-sound"
        shadow="cast: true">
      </a-sphere>

      <!-- VR Camera Rig -->
      <a-entity id="rig" position="0 0 0">
        <!-- Camera -->
        <a-entity
          id="camera"
          camera
          look-controls
          position="0 1.6 0">
        </a-entity>

        <!-- Left Hand Controller -->
        <a-entity
          id="leftHand"
          hand-controls="hand: left"
          blink-controls="cameraRig: #rig; teleportOrigin: #camera; collisionEntities: .ground"
          laser-controls="hand: left">
        </a-entity>

        <!-- Right Hand Controller -->
        <a-entity
          id="rightHand"
          hand-controls="hand: right"
          laser-controls="hand: right"
          raycaster="objects: .interactive">
        </a-entity>
      </a-entity>
    </a-scene>

    <script>
      // VR session events
      const scene = document.querySelector('a-scene');

      scene.addEventListener('enter-vr', () => {{
        console.log('Entered VR mode');
      }});

      scene.addEventListener('exit-vr', () => {{
        console.log('Exited VR mode');
      }});

      // Controller events
      const rightHand = document.querySelector('#rightHand');

      rightHand.addEventListener('triggerdown', () => {{
        console.log('Trigger pressed');
      }});

      rightHand.addEventListener('gripdown', () => {{
        console.log('Grip pressed');
      }});
    </script>
  </body>
</html>'''

def generate_ar_scene(name):
    """Generate AR scene with hit testing"""
    return f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{name} - A-Frame AR Experience</title>
    <meta name="description" content="{name} - AR Experience">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
    <style>
      body {{ margin: 0; }}
      #overlay {{
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        font-family: sans-serif;
        font-size: 14px;
        text-align: center;
        z-index: 1000;
      }}
      #overlay button {{
        margin-top: 10px;
        padding: 10px 20px;
        background: #4CC3D9;
        color: white;
        border: none;
        border-radius: 5px;
        font-size: 14px;
        cursor: pointer;
      }}
      #overlay button:hover {{
        background: #3BA0B5;
      }}
    </style>
  </head>
  <body>
    <a-scene
      webxr="optionalFeatures: hit-test, dom-overlay; overlayElement: #overlay"
      ar-hit-test="target: #model; type: footprint">

      <!-- Assets -->
      <a-assets>
        <!-- Replace with your GLTF model -->
        <a-asset-item id="model-asset" src="https://cdn.aframe.io/test-models/models/virtualcity/VC.gltf"></a-asset-item>
      </a-assets>

      <!-- AR Object to Place -->
      <a-entity
        id="model"
        gltf-model="#model-asset"
        scale="0.1 0.1 0.1"
        visible="false">
      </a-entity>

      <!-- AR Lighting -->
      <a-entity
        light="type: ambient; intensity: 0.8">
      </a-entity>

      <a-entity
        id="dirlight"
        light="type: directional; intensity: 0.5; castShadow: true"
        position="1 2 1">
      </a-entity>
    </a-scene>

    <!-- AR UI Overlay -->
    <div id="overlay">
      <p id="instructions">Tap to enter AR mode</p>
      <button id="clearBtn" style="display: none;">Clear Objects</button>
    </div>

    <script>
      const scene = document.querySelector('a-scene');
      const instructions = document.getElementById('instructions');
      const clearBtn = document.getElementById('clearBtn');
      const model = document.querySelector('#model');
      let placedObjects = [];

      // AR session events
      scene.addEventListener('enter-vr', function() {{
        if (this.is('ar-mode')) {{
          instructions.textContent = '';

          // Hit testing started
          this.addEventListener('ar-hit-test-start', function() {{
            instructions.innerHTML = 'Scanning environment...<br>Finding surfaces';
          }}, {{ once: true }});

          // Surface detected
          this.addEventListener('ar-hit-test-achieved', function() {{
            instructions.innerHTML = 'Tap to place object';
          }}, {{ once: true }});

          // Object placed
          this.addEventListener('ar-hit-test-select', function(evt) {{
            // Clone model for multiple placements
            const clone = model.cloneNode(true);
            clone.removeAttribute('id');
            clone.setAttribute('visible', true);

            const position = evt.detail.position;
            clone.setAttribute('position', position);

            scene.appendChild(clone);
            placedObjects.push(clone);

            instructions.innerHTML = 'Object placed! Tap to place another';
            clearBtn.style.display = 'block';
          }});
        }}
      }});

      scene.addEventListener('exit-vr', function() {{
        instructions.textContent = 'Tap to enter AR mode';
        clearBtn.style.display = 'none';
      }});

      // Clear all placed objects
      clearBtn.addEventListener('click', () => {{
        placedObjects.forEach(obj => obj.parentNode.removeChild(obj));
        placedObjects = [];
        instructions.innerHTML = 'Objects cleared! Tap to place';
      }});
    </script>
  </body>
</html>'''

def generate_360_scene(name):
    """Generate 360° photo/video gallery"""
    return f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{name} - 360° Gallery</title>
    <meta name="description" content="{name} - 360° Gallery">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
    <script src="https://unpkg.com/aframe-event-set-component@5.0.0/dist/aframe-event-set-component.min.js"></script>
    <style>
      body {{ margin: 0; }}
      #info {{
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 15px;
        border-radius: 8px;
        font-family: sans-serif;
        font-size: 14px;
        text-align: center;
      }}
    </style>
  </head>
  <body>
    <a-scene>
      <!-- Assets -->
      <a-assets>
        <!-- Replace with your 360 images -->
        <img id="city" src="https://cdn.aframe.io/360-image-gallery-boilerplate/img/city.jpg" crossorigin="anonymous">
        <img id="forest" src="https://cdn.aframe.io/360-image-gallery-boilerplate/img/cubes.jpg" crossorigin="anonymous">
        <img id="space" src="https://cdn.aframe.io/360-image-gallery-boilerplate/img/sechelt.jpg" crossorigin="anonymous">

        <!-- Thumbnails -->
        <img id="city-thumb" src="https://cdn.aframe.io/360-image-gallery-boilerplate/img/thumb-city.jpg" crossorigin="anonymous">
        <img id="forest-thumb" src="https://cdn.aframe.io/360-image-gallery-boilerplate/img/thumb-cubes.jpg" crossorigin="anonymous">
        <img id="space-thumb" src="https://cdn.aframe.io/360-image-gallery-boilerplate/img/thumb-sechelt.jpg" crossorigin="anonymous">

        <audio id="click-sound" src="https://cdn.aframe.io/360-image-gallery-boilerplate/audio/click.ogg"></audio>
      </a-assets>

      <!-- 360 Sky -->
      <a-sky id="image-360" src="#city" rotation="0 -130 0"></a-sky>

      <!-- Thumbnail Menu -->
      <a-entity id="menu" position="0 1.6 -2.5" layout="type: line; margin: 1.5" rotation="0 0 0">
        <!-- City Thumbnail -->
        <a-entity class="link"
          geometry="primitive: plane; width: 1; height: 1"
          material="shader: flat; src: #city-thumb"
          sound="on: click; src: #click-sound"
          event-set__mouseenter="scale: 1.2 1.2 1"
          event-set__mouseleave="scale: 1 1 1"
          event-set__click="_target: #image-360; material.src: #city">
        </a-entity>

        <!-- Forest Thumbnail -->
        <a-entity class="link"
          geometry="primitive: plane; width: 1; height: 1"
          material="shader: flat; src: #forest-thumb"
          sound="on: click; src: #click-sound"
          event-set__mouseenter="scale: 1.2 1.2 1"
          event-set__mouseleave="scale: 1 1 1"
          event-set__click="_target: #image-360; material.src: #forest">
        </a-entity>

        <!-- Space Thumbnail -->
        <a-entity class="link"
          geometry="primitive: plane; width: 1; height: 1"
          material="shader: flat; src: #space-thumb"
          sound="on: click; src: #click-sound"
          event-set__mouseenter="scale: 1.2 1.2 1"
          event-set__mouseleave="scale: 1 1 1"
          event-set__click="_target: #image-360; material.src: #space">
        </a-entity>
      </a-entity>

      <!-- Camera with Cursor -->
      <a-camera>
        <a-cursor
          raycaster="objects: .link"
          fuse="true"
          fuse-timeout="1500">
        </a-cursor>
      </a-camera>
    </a-scene>

    <div id="info">
      <strong>360° Gallery</strong><br>
      Gaze at thumbnails to switch views
    </div>
  </body>
</html>'''

def generate_physics_scene(name):
    """Generate scene with physics"""
    return f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{name} - A-Frame Physics Scene</title>
    <meta name="description" content="{name} - Physics Simulation">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/aframe-physics-system@4.2.2/dist/aframe-physics-system.min.js"></script>
    <style>
      body {{ margin: 0; }}
    </style>
  </head>
  <body>
    <a-scene physics="debug: false; gravity: -9.8">
      <!-- Environment -->
      <a-sky color="#87CEEB"></a-sky>

      <!-- Static Ground -->
      <a-plane
        static-body
        rotation="-90 0 0"
        width="20"
        height="20"
        color="#7BC8A4"
        shadow="receive: true">
      </a-plane>

      <!-- Lighting -->
      <a-entity light="type: ambient; intensity: 0.6"></a-entity>
      <a-entity light="type: directional; intensity: 0.5; castShadow: true" position="2 8 2"></a-entity>

      <!-- Dynamic Physics Objects -->
      <a-box
        dynamic-body="mass: 5"
        position="-2 5 -5"
        rotation="45 45 0"
        color="#4CC3D9"
        shadow="cast: true">
      </a-box>

      <a-sphere
        dynamic-body="mass: 3"
        position="0 7 -5"
        radius="0.5"
        color="#EF2D5E"
        shadow="cast: true">
      </a-sphere>

      <a-cylinder
        dynamic-body="mass: 4"
        position="2 6 -5"
        radius="0.3"
        height="1"
        color="#FFC65D"
        shadow="cast: true">
      </a-cylinder>

      <!-- Walls -->
      <a-box
        static-body
        position="-10 2.5 -5"
        width="0.5"
        height="5"
        depth="20"
        color="#888">
      </a-box>

      <a-box
        static-body
        position="10 2.5 -5"
        width="0.5"
        height="5"
        depth="20"
        color="#888">
      </a-box>

      <!-- Camera -->
      <a-camera position="0 1.6 5" look-controls wasd-controls></a-camera>
    </a-scene>

    <script>
      // Spawn new objects on keypress
      document.addEventListener('keydown', (evt) => {{
        if (evt.key === ' ') {{
          const scene = document.querySelector('a-scene');
          const sphere = document.createElement('a-sphere');

          sphere.setAttribute('dynamic-body', 'mass: 2');
          sphere.setAttribute('position', {{
            x: Math.random() * 4 - 2,
            y: 10,
            z: -5
          }});
          sphere.setAttribute('radius', 0.5);
          sphere.setAttribute('color', `#${{Math.floor(Math.random()*16777215).toString(16)}}`);
          sphere.setAttribute('shadow', 'cast: true');

          scene.appendChild(sphere);
        }}
      }});
    </script>
  </body>
</html>'''

def generate_environment_scene(name):
    """Generate scene with procedural environment"""
    return f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{name} - A-Frame Environment</title>
    <meta name="description" content="{name} - Procedural Environment">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/aframe-environment-component@1.3.3/dist/aframe-environment-component.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/c-frame/aframe-particle-system-component@1.2.x/dist/aframe-particle-system-component.min.js"></script>
    <style>
      body {{ margin: 0; }}
    </style>
  </head>
  <body>
    <a-scene>
      <!-- Procedural Environment -->
      <a-entity environment="
        preset: forest;
        seed: 42;
        skyType: gradient;
        skyColor: #4A90E2;
        horizonColor: #87CEEB;
        lighting: distant;
        lightPosition: 1 1 -2;
        fog: 0.7;
        ground: hills;
        groundColor: #5A7F32;
        groundColor2: #3D5E1F;
        dressing: trees;
        dressingAmount: 30;
        dressingColor: #228B22;
        dressingScale: 5;
        grid: none
      "></a-entity>

      <!-- Particle Effects -->
      <a-entity particle-system="
        preset: dust;
        particleCount: 1000;
        color: #FFF;
        size: 0.3;
        maxAge: 3
      " position="0 2 -5">
      </a-entity>

      <!-- Objects in Scene -->
      <a-box
        position="0 0.5 -5"
        rotation="0 45 0"
        color="#4CC3D9"
        animation="property: rotation; to: 0 405 0; loop: true; dur: 10000">
      </a-box>

      <!-- Camera -->
      <a-camera position="0 1.6 0" look-controls wasd-controls></a-camera>
    </a-scene>
  </body>
</html>'''

def generate_networked_scene(name):
    """Generate networked multi-user scene"""
    return f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{name} - Networked A-Frame</title>
    <meta name="description" content="{name} - Multi-user VR">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/networked-aframe@^0.11.0/dist/networked-aframe.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.js"></script>
    <script>
      // NAF schema for networked avatars
      window.addEventListener('load', () => {{
        NAF.schemas.add({{
          template: '#avatar-template',
          components: [
            'position',
            'rotation'
          ]
        }});
      }});
    </script>
    <style>
      body {{ margin: 0; }}
    </style>
  </head>
  <body>
    <a-scene networked-scene="
      room: {name.lower().replace(' ', '-')};
      adapter: wseasyrtc;
      audio: true;
      debug: false
    ">
      <!-- Assets -->
      <a-assets>
        <!-- Avatar Template -->
        <template id="avatar-template">
          <a-entity class="avatar">
            <a-sphere class="head" color="#5985ff" scale="0.2 0.22 0.2"></a-sphere>
            <a-entity class="face" position="0 0.05 0">
              <a-sphere class="eye" color="#FFF" position="0.06 0.05 -0.16" scale="0.04 0.04 0.04">
                <a-sphere class="pupil" color="#000" position="0 0 -1" scale="0.5 0.5 0.5"></a-sphere>
              </a-sphere>
              <a-sphere class="eye" color="#FFF" position="-0.06 0.05 -0.16" scale="0.04 0.04 0.04">
                <a-sphere class="pupil" color="#000" position="0 0 -1" scale="0.5 0.5 0.5"></a-sphere>
              </a-sphere>
            </a-entity>
          </a-entity>
        </template>
      </a-assets>

      <!-- Environment -->
      <a-sky color="#87CEEB"></a-sky>
      <a-plane rotation="-90 0 0" width="50" height="50" color="#7BC8A4"></a-plane>

      <!-- Lighting -->
      <a-entity light="type: ambient; intensity: 0.7"></a-entity>
      <a-entity light="type: directional; intensity: 0.4" position="2 4 2"></a-entity>

      <!-- Shared Objects -->
      <a-box position="-1 0.5 -3" color="#4CC3D9"></a-box>
      <a-sphere position="1 1.25 -3" radius="0.5" color="#EF2D5E"></a-sphere>

      <!-- Player Rig -->
      <a-entity id="rig" position="0 0 0">
        <a-entity id="camera" camera look-controls wasd-controls position="0 1.6 0"
                  networked="template: #avatar-template; attachTemplateToLocal: false">
        </a-entity>
      </a-entity>
    </a-scene>
  </body>
</html>'''

def interactive_mode():
    """Interactive scene generator"""
    print("\n=== A-Frame Scene Generator (Interactive Mode) ===\n")

    print("Available scene types:")
    for i, (scene_type, config) in enumerate(SCENE_TYPES.items(), 1):
        print(f"  {i}. {scene_type:12} - {config['description']}")

    while True:
        try:
            choice = input("\nSelect scene type (1-7): ").strip()
            scene_type = list(SCENE_TYPES.keys())[int(choice) - 1]
            break
        except (ValueError, IndexError):
            print("Invalid choice. Please enter a number between 1 and 7.")

    name = input("Enter scene name (default: MyScene): ").strip() or "MyScene"
    output_dir = input("Enter output directory (default: current): ").strip() or "."

    generate_scene(scene_type, name, output_dir)

def generate_scene(scene_type, name, output_dir="."):
    """Generate scene based on type"""
    if scene_type not in SCENE_TYPES:
        print(f"Error: Unknown scene type '{scene_type}'")
        print(f"Available types: {', '.join(SCENE_TYPES.keys())}")
        sys.exit(1)

    # Generate HTML content
    generators = {
        'basic': generate_basic_scene,
        'vr': generate_vr_scene,
        'ar': generate_ar_scene,
        '360': generate_360_scene,
        'physics': generate_physics_scene,
        'environment': generate_environment_scene,
        'networked': generate_networked_scene
    }

    html_content = generators[scene_type](name)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Write file
    filename = SCENE_TYPES[scene_type]['filename']
    file_path = output_path / filename

    with open(file_path, 'w') as f:
        f.write(html_content)

    print(f"\n✅ Generated {scene_type} scene: {file_path}")
    print(f"📝 Scene name: {name}")
    print(f"🎯 Features: {', '.join(SCENE_TYPES[scene_type]['features'])}")
    print(f"\n🚀 To view: Open {file_path} in a web browser")
    print("   Note: Some features require HTTPS (use a local server)")

def main():
    parser = argparse.ArgumentParser(
        description='Generate A-Frame scene boilerplate',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scene_generator.py basic MyScene
  python scene_generator.py vr VRProject --output ./my-scenes
  python scene_generator.py ar ARFurniture
  python scene_generator.py --interactive

Scene Types:
  basic       - Basic 3D scene with primitives
  vr          - VR scene with controllers
  ar          - AR scene with hit testing
  360         - 360° photo/video gallery
  physics     - Scene with physics simulation
  environment - Procedural environment
  networked   - Multi-user networked scene
        '''
    )

    parser.add_argument(
        'scene_type',
        nargs='?',
        choices=list(SCENE_TYPES.keys()),
        help='Type of scene to generate'
    )

    parser.add_argument(
        'name',
        nargs='?',
        default='MyScene',
        help='Name of the scene (default: MyScene)'
    )

    parser.add_argument(
        '-o', '--output',
        default='.',
        help='Output directory (default: current directory)'
    )

    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )

    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='List available scene types'
    )

    args = parser.parse_args()

    if args.list:
        print("\nAvailable Scene Types:\n")
        for scene_type, config in SCENE_TYPES.items():
            print(f"  {scene_type:12} - {config['description']}")
            print(f"                 Features: {', '.join(config['features'])}\n")
        sys.exit(0)

    if args.interactive or not args.scene_type:
        interactive_mode()
    else:
        generate_scene(args.scene_type, args.name, args.output)

if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/aframe-webxr/skills/aframe-webxr/assets/examples/README.md =====

# A-Frame WebXR Examples

Comprehensive real-world patterns and examples for building VR/AR experiences with A-Frame.

## Table of Contents

1. [VR Interaction Patterns](#vr-interaction-patterns)
2. [AR Object Placement](#ar-object-placement)
3. [360° Experiences](#360-experiences)
4. [Advanced Controllers](#advanced-controllers)
5. [Multi-User Networking](#multi-user-networking)
6. [Physics Simulations](#physics-simulations)
7. [Performance Optimization](#performance-optimization)

---

## VR Interaction Patterns

### Grabable Objects with Two-Handed Manipulation

```html
<script>
AFRAME.registerComponent('two-handed-grab', {
  init: function() {
    this.leftHand = null;
    this.rightHand = null;
    this.grabbed = false;
    this.originalScale = this.el.object3D.scale.clone();

    this.onGripDown = this.onGripDown.bind(this);
    this.onGripUp = this.onGripUp.bind(this);

    this.el.addEventListener('gripdown', this.onGripDown);
    this.el.addEventListener('gripup', this.onGripUp);
  },

  onGripDown: function(evt) {
    const hand = evt.detail.hand;

    if (hand === 'left') {
      this.leftHand = evt.detail.controller;
    } else if (hand === 'right') {
      this.rightHand = evt.detail.controller;
    }

    if (!this.grabbed) {
      // First hand grabs
      this.grabbed = true;
      const controller = this.leftHand || this.rightHand;
      controller.object3D.attach(this.el.object3D);
    }
  },

  onGripUp: function(evt) {
    const hand = evt.detail.hand;

    if (hand === 'left') {
      this.leftHand = null;
    } else if (hand === 'right') {
      this.rightHand = null;
    }

    if (!this.leftHand && !this.rightHand && this.grabbed) {
      // Release when both hands released
      this.grabbed = false;
      this.el.sceneEl.object3D.attach(this.el.object3D);
    }
  },

  tick: function() {
    // Scale based on hand distance when both hands grabbing
    if (this.leftHand && this.rightHand && this.grabbed) {
      const distance = this.leftHand.object3D.position.distanceTo(
        this.rightHand.object3D.position
      );

      const scale = Math.max(0.1, distance);
      this.el.object3D.scale.setScalar(scale);
    }
  }
});
</script>

<a-scene>
  <a-entity id="leftHand" hand-controls="hand: left"></a-entity>
  <a-entity id="rightHand" hand-controls="hand: right"></a-entity>

  <a-box two-handed-grab position="0 1.5 -2" color="#4CC3D9"></a-box>
</a-scene>
```

### VR Inventory System

```html
<script>
AFRAME.registerComponent('vr-inventory', {
  schema: {
    maxSlots: {default: 6}
  },

  init: function() {
    this.items = [];
    this.selectedSlot = 0;

    // Create inventory UI
    this.createInventoryUI();

    // Controller events
    document.querySelector('[hand-controls="hand: right"]')
      .addEventListener('thumbstickdown', (evt) => {
        if (evt.detail.x > 0.5) this.nextSlot();
        else if (evt.detail.x < -0.5) this.prevSlot();
      });
  },

  createInventoryUI: function() {
    const ui = document.createElement('a-entity');
    ui.setAttribute('position', '0 0.2 -0.5');
    ui.setAttribute('rotation', '-30 0 0');

    for (let i = 0; i < this.data.maxSlots; i++) {
      const slot = document.createElement('a-plane');
      slot.setAttribute('width', 0.08);
      slot.setAttribute('height', 0.08);
      slot.setAttribute('color', i === 0 ? '#4FC3F7' : '#333');
      slot.setAttribute('position', `${i * 0.1 - 0.25} 0 0`);
      ui.appendChild(slot);
    }

    // Attach to camera
    document.querySelector('[camera]').appendChild(ui);
    this.ui = ui;
  },

  addItem: function(item) {
    if (this.items.length < this.data.maxSlots) {
      this.items.push(item);
      this.updateUI();
      return true;
    }
    return false;
  },

  nextSlot: function() {
    this.selectedSlot = (this.selectedSlot + 1) % this.items.length;
    this.updateUI();
  },

  prevSlot: function() {
    this.selectedSlot = (this.selectedSlot - 1 + this.items.length) % this.items.length;
    this.updateUI();
  },

  updateUI: function() {
    // Update slot colors
    const slots = this.ui.querySelectorAll('a-plane');
    slots.forEach((slot, i) => {
      slot.setAttribute('color', i === this.selectedSlot ? '#4FC3F7' : '#333');
    });
  }
});
</script>

<a-entity vr-inventory="maxSlots: 8"></a-entity>
```

---

## AR Object Placement

### Advanced AR Hit Testing with Rotation

```html
<script>
const scene = document.querySelector('a-scene');
const model = document.querySelector('#model');
let placedObjects = [];
let currentRotation = 0;

// Rotation controls
document.getElementById('rotateBtn').addEventListener('click', () => {
  currentRotation += 45;
  if (model.object3D.visible) {
    model.object3D.rotation.y = currentRotation * (Math.PI / 180);
  }
});

// Custom placement
scene.addEventListener('ar-hit-test-select', (evt) => {
  const clone = model.cloneNode(true);
  clone.removeAttribute('id');
  clone.setAttribute('visible', true);

  const position = evt.detail.position;
  const rotation = evt.detail.rotation || {x: 0, y: currentRotation * (Math.PI / 180), z: 0};

  clone.setAttribute('position', position);
  clone.object3D.rotation.set(rotation.x, rotation.y, rotation.z);

  // Add interaction
  clone.addEventListener('click', () => {
    // Remove on click
    clone.parentNode.removeChild(clone);
    placedObjects = placedObjects.filter(obj => obj !== clone);
  });

  scene.appendChild(clone);
  placedObjects.push(clone);
});

// Undo last placement
document.getElementById('undoBtn').addEventListener('click', () => {
  if (placedObjects.length > 0) {
    const last = placedObjects.pop();
    last.parentNode.removeChild(last);
  }
});
</script>

<a-scene
  webxr="optionalFeatures: hit-test, dom-overlay; overlayElement: #overlay"
  ar-hit-test="target: #model">

  <a-entity id="model" gltf-model="#furniture" visible="false"></a-entity>

  <div id="overlay">
    <button id="rotateBtn">Rotate 45°</button>
    <button id="undoBtn">Undo</button>
    <button id="clearBtn">Clear All</button>
  </div>
</a-scene>
```

### AR Measurement Tool

```html
<script>
AFRAME.registerComponent('ar-measure', {
  init: function() {
    this.points = [];
    this.lines = [];

    this.el.sceneEl.addEventListener('ar-hit-test-select', (evt) => {
      this.addPoint(evt.detail.position);
    });
  },

  addPoint: function(position) {
    // Create point marker
    const marker = document.createElement('a-sphere');
    marker.setAttribute('radius', 0.02);
    marker.setAttribute('color', '#FF0000');
    marker.setAttribute('position', position);
    this.el.sceneEl.appendChild(marker);

    this.points.push(position);

    // Draw line if we have 2+ points
    if (this.points.length >= 2) {
      const start = this.points[this.points.length - 2];
      const end = this.points[this.points.length - 1];

      this.drawLine(start, end);
      this.showDistance(start, end);
    }
  },

  drawLine: function(start, end) {
    const line = document.createElement('a-entity');
    line.setAttribute('line', {
      start: start,
      end: end,
      color: '#FF0000'
    });
    this.el.sceneEl.appendChild(line);
    this.lines.push(line);
  },

  showDistance: function(start, end) {
    const distance = Math.sqrt(
      Math.pow(end.x - start.x, 2) +
      Math.pow(end.y - start.y, 2) +
      Math.pow(end.z - start.z, 2)
    );

    const midpoint = {
      x: (start.x + end.x) / 2,
      y: (start.y + end.y) / 2,
      z: (start.z + end.z) / 2
    };

    const text = document.createElement('a-text');
    text.setAttribute('value', `${(distance * 100).toFixed(1)} cm`);
    text.setAttribute('position', midpoint);
    text.setAttribute('align', 'center');
    text.setAttribute('color', '#FF0000');
    text.setAttribute('scale', '0.2 0.2 0.2');
    text.setAttribute('look-at', '[camera]');
    this.el.sceneEl.appendChild(text);
  },

  clearMeasurements: function() {
    this.points = [];
    this.lines.forEach(line => line.parentNode.removeChild(line));
    this.lines = [];
  }
});
</script>

<a-entity ar-measure></a-entity>
```

---

## 360° Experiences

### Interactive 360° Video with Hotspots

```html
<script>
AFRAME.registerComponent('video-hotspot', {
  schema: {
    time: {default: 0},
    title: {default: ''},
    action: {default: ''}
  },

  init: function() {
    const video = document.querySelector('#video-360');

    this.checkTime = () => {
      if (video.currentTime >= this.data.time &&
          video.currentTime < this.data.time + 1) {
        this.el.setAttribute('visible', true);
      } else {
        this.el.setAttribute('visible', false);
      }
    };

    video.addEventListener('timeupdate', this.checkTime);

    this.el.addEventListener('click', () => {
      if (this.data.action === 'pause') {
        video.pause();
      } else if (this.data.action.startsWith('jump:')) {
        const time = parseFloat(this.data.action.split(':')[1]);
        video.currentTime = time;
      }
    });
  }
});
</script>

<a-scene>
  <a-assets>
    <video id="video-360" src="360video.mp4" autoplay loop crossorigin="anonymous"></video>
  </a-assets>

  <a-videosphere src="#video-360"></a-videosphere>

  <!-- Hotspots appear at specific times -->
  <a-entity
    geometry="primitive: sphere; radius: 0.3"
    material="color: #FF0000; opacity: 0.7"
    position="3 2 -5"
    video-hotspot="time: 5; title: Learn More; action: pause"
    visible="false">
  </a-entity>

  <a-entity
    geometry="primitive: sphere; radius: 0.3"
    material="color: #00FF00; opacity: 0.7"
    position="-3 2 5"
    video-hotspot="time: 15; title: Skip Ahead; action: jump:30"
    visible="false">
  </a-entity>
</a-scene>
```

### 360° Photo Tour with Transitions

```html
<script>
const locations = [
  {name: 'Entrance', image: '#loc1', rotation: '0 -130 0'},
  {name: 'Hallway', image: '#loc2', rotation: '0 90 0'},
  {name: 'Room', image: '#loc3', rotation: '0 0 0'}
];

let currentLocation = 0;

function navigateToLocation(index) {
  const sky = document.querySelector('a-sky');
  const newLoc = locations[index];

  // Fade transition
  sky.setAttribute('animation', {
    property: 'material.opacity',
    to: 0,
    dur: 500
  });

  setTimeout(() => {
    sky.setAttribute('src', newLoc.image);
    sky.setAttribute('rotation', newLoc.rotation);
    sky.setAttribute('animation', {
      property: 'material.opacity',
      to: 1,
      dur: 500
    });

    document.getElementById('locationName').textContent = newLoc.name;
    currentLocation = index;
  }, 500);
}

// Create navigation hotspots
locations.forEach((loc, index) => {
  const hotspot = document.createElement('a-entity');
  hotspot.setAttribute('geometry', 'primitive: sphere; radius: 0.2');
  hotspot.setAttribute('material', 'color: #4FC3F7; opacity: 0.8');
  hotspot.setAttribute('position', `${Math.cos(index * 2) * 3} 1 ${Math.sin(index * 2) * 3}`);
  hotspot.addEventListener('click', () => navigateToLocation(index));
  document.querySelector('a-scene').appendChild(hotspot);
});
</script>

<a-assets>
  <img id="loc1" src="entrance.jpg">
  <img id="loc2" src="hallway.jpg">
  <img id="loc3" src="room.jpg">
</a-assets>

<a-sky src="#loc1" rotation="0 -130 0"></a-sky>

<div id="info">
  <span id="locationName">Entrance</span>
</div>
```

---

## Advanced Controllers

### Custom Gesture Recognition

```html
<script>
AFRAME.registerComponent('gesture-detector', {
  init: function() {
    this.positions = [];
    this.maxPositions = 20;
    this.isRecording = false;

    const rightHand = document.querySelector('[hand-controls="hand: right"]');

    rightHand.addEventListener('triggerdown', () => {
      this.isRecording = true;
      this.positions = [];
    });

    rightHand.addEventListener('triggerup', () => {
      this.isRecording = false;
      this.recognizeGesture();
    });
  },

  tick: function() {
    if (!this.isRecording) return;

    const rightHand = document.querySelector('[hand-controls="hand: right"]');
    const pos = rightHand.object3D.position.clone();

    this.positions.push(pos);

    if (this.positions.length > this.maxPositions) {
      this.positions.shift();
    }
  },

  recognizeGesture: function() {
    if (this.positions.length < 5) return;

    const start = this.positions[0];
    const end = this.positions[this.positions.length - 1];
    const delta = new THREE.Vector3().subVectors(end, start);

    // Detect horizontal swipe
    if (Math.abs(delta.x) > 0.5 && Math.abs(delta.y) < 0.2) {
      if (delta.x > 0) {
        this.onGesture('swipe-right');
      } else {
        this.onGesture('swipe-left');
      }
    }

    // Detect vertical swipe
    else if (Math.abs(delta.y) > 0.5 && Math.abs(delta.x) < 0.2) {
      if (delta.y > 0) {
        this.onGesture('swipe-up');
      } else {
        this.onGesture('swipe-down');
      }
    }

    // Detect circle
    else if (this.isCircularMotion()) {
      this.onGesture('circle');
    }
  },

  isCircularMotion: function() {
    // Check if positions form a circle
    const center = this.getCenter();
    const radii = this.positions.map(pos =>
      pos.distanceTo(center)
    );

    const avgRadius = radii.reduce((a, b) => a + b) / radii.length;
    const variance = radii.reduce((sum, r) =>
      sum + Math.pow(r - avgRadius, 2), 0) / radii.length;

    return variance < 0.01; // Low variance = circular
  },

  getCenter: function() {
    const sum = this.positions.reduce((acc, pos) => {
      return acc.add(pos);
    }, new THREE.Vector3());

    return sum.divideScalar(this.positions.length);
  },

  onGesture: function(gestureName) {
    console.log('Gesture detected:', gestureName);
    this.el.sceneEl.emit('gesture', {name: gestureName});
  }
});
</script>

<a-entity gesture-detector></a-entity>

<script>
// Listen to gestures
document.querySelector('a-scene').addEventListener('gesture', (evt) => {
  const gesture = evt.detail.name;

  if (gesture === 'swipe-right') {
    console.log('Next item');
  } else if (gesture === 'swipe-left') {
    console.log('Previous item');
  } else if (gesture === 'circle') {
    console.log('Open menu');
  }
});
</script>
```

---

## Multi-User Networking

### Networked-Aframe Advanced Setup

```html
<script src="https://cdn.jsdelivr.net/npm/networked-aframe@^0.11.0/dist/networked-aframe.min.js"></script>

<script>
// Custom NAF schemas
NAF.schemas.add({
  template: '#player-template',
  components: [
    'position',
    'rotation',
    {
      component: 'player-info',
      property: 'username'
    }
  ]
});

NAF.schemas.add({
  template: '#shared-object-template',
  components: [
    'position',
    'rotation',
    'scale',
    'material'
  ]
});

// Custom component for player info
AFRAME.registerComponent('player-info', {
  schema: {
    username: {default: 'Guest'}
  },

  init: function() {
    // Create name tag
    const nameTag = document.createElement('a-text');
    nameTag.setAttribute('value', this.data.username);
    nameTag.setAttribute('position', '0 0.6 0');
    nameTag.setAttribute('align', 'center');
    nameTag.setAttribute('color', '#FFF');
    nameTag.setAttribute('scale', '0.5 0.5 0.5');
    nameTag.setAttribute('look-at', '[camera]');
    this.el.appendChild(nameTag);
  }
});

// Voice chat events
document.querySelector('a-scene').addEventListener('connected', () => {
  console.log('Connected to network');
});

document.querySelector('a-scene').addEventListener('disconnected', () => {
  console.log('Disconnected from network');
});
</script>

<a-scene
  networked-scene="
    room: myRoom;
    adapter: wseasyrtc;
    audio: true;
    debug: false;
    connectOnLoad: true
  ">

  <a-assets>
    <!-- Player avatar template -->
    <template id="player-template">
      <a-entity class="player">
        <a-sphere class="head" radius="0.2" color="#5985ff" position="0 0.3 0"></a-sphere>
        <a-cylinder class="body" radius="0.15" height="0.5" color="#5985ff"></a-cylinder>
      </a-entity>
    </template>

    <!-- Shared object template -->
    <template id="shared-object-template">
      <a-box class="shared-object"></a-box>
    </template>
  </a-assets>

  <!-- Local player -->
  <a-entity id="player"
    networked="template: #player-template; attachTemplateToLocal: false"
    player-info="username: Player1">

    <a-entity camera position="0 1.6 0" look-controls>
      <a-cursor></a-cursor>
    </a-entity>
  </a-entity>

  <!-- Shared objects -->
  <a-entity id="sharedBox"
    networked="template: #shared-object-template"
    position="0 1 -3"
    color="#4CC3D9">
  </a-entity>
</a-scene>
```

---

## Physics Simulations

### Ragdoll Physics

```html
<script src="https://cdn.jsdelivr.net/npm/aframe-physics-system@4.2.2/dist/aframe-physics-system.min.js"></script>

<script>
AFRAME.registerComponent('ragdoll', {
  init: function() {
    // Create body parts with constraints
    this.createBodyPart('head', {y: 2.2, z: 0}, 0.15, 1);
    this.createBodyPart('torso', {y: 1.5, z: 0}, 0.2, 5);
    this.createBodyPart('leftArm', {y: 1.7, z: -0.3}, 0.08, 0.5);
    this.createBodyPart('rightArm', {y: 1.7, z: 0.3}, 0.08, 0.5);
    this.createBodyPart('leftLeg', {y: 0.8, z: -0.15}, 0.1, 1);
    this.createBodyPart('rightLeg', {y: 0.8, z: 0.15}, 0.1, 1);

    // Add constraints between parts
    this.addConstraint('head', 'torso', 'lock');
    this.addConstraint('torso', 'leftArm', 'hinge');
    this.addConstraint('torso', 'rightArm', 'hinge');
    this.addConstraint('torso', 'leftLeg', 'hinge');
    this.addConstraint('torso', 'rightLeg', 'hinge');
  },

  createBodyPart: function(name, position, radius, mass) {
    const part = document.createElement('a-sphere');
    part.setAttribute('id', name);
    part.setAttribute('radius', radius);
    part.setAttribute('position', position);
    part.setAttribute('dynamic-body', `mass: ${mass}`);
    part.setAttribute('color', '#5985ff');
    this.el.sceneEl.appendChild(part);
  },

  addConstraint: function(bodyA, bodyB, type) {
    const constraint = document.createElement('a-entity');
    constraint.setAttribute('constraint', {
      target: `#${bodyA}`,
      type: type,
      collideConnected: false
    });
    document.querySelector(`#${bodyB}`).appendChild(constraint);
  }
});
</script>

<a-scene physics="debug: false; gravity: -9.8">
  <a-plane static-body rotation="-90 0 0" width="20" height="20"></a-plane>

  <a-entity ragdoll position="0 3 -5"></a-entity>

  <!-- Push ragdoll with click -->
  <a-sphere
    id="pushButton"
    position="2 1 -3"
    radius="0.5"
    color="#FF0000">
  </a-sphere>

  <script>
    document.querySelector('#pushButton').addEventListener('click', () => {
      const torso = document.querySelector('#torso');
      const impulse = new Ammo.btVector3(5, 2, 0);
      const position = new Ammo.btVector3(0, 0, 0);
      torso.body.applyImpulse(impulse, position);
      Ammo.destroy(impulse);
      Ammo.destroy(position);
    });
  </script>
</a-scene>
```

---

## Performance Optimization

### Dynamic LOD System

```html
<script>
AFRAME.registerComponent('lod-manager', {
  schema: {
    far: {default: 20},
    mid: {default: 10},
    near: {default: 5}
  },

  init: function() {
    this.camera = this.el.sceneEl.camera;
    this.lodObjects = [];

    // Register LOD objects
    this.el.sceneEl.addEventListener('lod-object-added', (evt) => {
      this.lodObjects.push(evt.detail.object);
    });
  },

  tick: function() {
    if (!this.camera) return;

    this.lodObjects.forEach(obj => {
      const distance = obj.el.object3D.position.distanceTo(
        this.camera.position
      );

      if (distance > this.data.far) {
        obj.setLOD('none');
      } else if (distance > this.data.mid) {
        obj.setLOD('low');
      } else if (distance > this.data.near) {
        obj.setLOD('medium');
      } else {
        obj.setLOD('high');
      }
    });
  }
});

AFRAME.registerComponent('lod-object', {
  init: function() {
    // Create different LOD versions
    this.lods = {
      high: this.createHighPoly(),
      medium: this.createMediumPoly(),
      low: this.createLowPoly(),
      none: null
    };

    this.currentLOD = 'high';
    this.setLOD('high');

    // Notify manager
    this.el.sceneEl.emit('lod-object-added', {object: this});
  },

  createHighPoly: function() {
    const mesh = document.createElement('a-sphere');
    mesh.setAttribute('segments-width', 32);
    mesh.setAttribute('segments-height', 32);
    return mesh;
  },

  createMediumPoly: function() {
    const mesh = document.createElement('a-sphere');
    mesh.setAttribute('segments-width', 16);
    mesh.setAttribute('segments-height', 16);
    return mesh;
  },

  createLowPoly: function() {
    const mesh = document.createElement('a-sphere');
    mesh.setAttribute('segments-width', 8);
    mesh.setAttribute('segments-height', 6);
    return mesh;
  },

  setLOD: function(level) {
    if (this.currentLOD === level) return;

    // Remove current mesh
    if (this.lods[this.currentLOD]) {
      this.el.removeChild(this.lods[this.currentLOD]);
    }

    // Add new mesh
    if (this.lods[level]) {
      this.el.appendChild(this.lods[level]);
    }

    this.currentLOD = level;
  }
});
</script>

<a-scene lod-manager="far: 30; mid: 15; near: 7">
  <!-- LOD objects -->
  <a-entity lod-object position="0 1 -10"></a-entity>
  <a-entity lod-object position="5 1 -20"></a-entity>
  <a-entity lod-object position="-5 1 -30"></a-entity>

  <a-camera position="0 1.6 0" wasd-controls look-controls></a-camera>
</a-scene>
```

### Object Pooling for Performance

```html
<script>
AFRAME.registerComponent('object-pool', {
  schema: {
    size: {default: 20},
    mixin: {default: ''}
  },

  init: function() {
    this.availableObjects = [];
    this.activeObjects = [];

    // Pre-create pool
    for (let i = 0; i < this.data.size; i++) {
      const obj = this.createObject();
      obj.setAttribute('visible', false);
      this.el.sceneEl.appendChild(obj);
      this.availableObjects.push(obj);
    }

    console.log(`Pool initialized with ${this.data.size} objects`);
  },

  createObject: function() {
    const obj = document.createElement('a-entity');
    if (this.data.mixin) {
      obj.setAttribute('mixin', this.data.mixin);
    }
    return obj;
  },

  requestObject: function() {
    let obj;

    if (this.availableObjects.length > 0) {
      obj = this.availableObjects.pop();
    } else {
      // Expand pool if needed
      console.warn('Pool exhausted, creating new object');
      obj = this.createObject();
      this.el.sceneEl.appendChild(obj);
    }

    obj.setAttribute('visible', true);
    this.activeObjects.push(obj);
    return obj;
  },

  returnObject: function(obj) {
    const index = this.activeObjects.indexOf(obj);
    if (index > -1) {
      this.activeObjects.splice(index, 1);
      obj.setAttribute('visible', false);
      this.availableObjects.push(obj);
    }
  },

  returnAll: function() {
    this.activeObjects.forEach(obj => {
      obj.setAttribute('visible', false);
      this.availableObjects.push(obj);
    });
    this.activeObjects = [];
  }
});
</script>

<a-assets>
  <a-mixin id="bullet"
    geometry="primitive: sphere; radius: 0.05"
    material="color: #FF0000"
    dynamic-body="mass: 0.1">
  </a-mixin>
</a-assets>

<a-entity id="bulletPool" object-pool="size: 50; mixin: bullet"></a-entity>

<script>
// Usage example
const pool = document.querySelector('#bulletPool').components['object-pool'];

function fireBullet(position, direction) {
  const bullet = pool.requestObject();
  bullet.setAttribute('position', position);

  // Apply velocity
  setTimeout(() => {
    const impulse = new Ammo.btVector3(
      direction.x * 10,
      direction.y * 10,
      direction.z * 10
    );
    const pos = new Ammo.btVector3(0, 0, 0);
    bullet.body.applyImpulse(impulse, pos);
    Ammo.destroy(impulse);
    Ammo.destroy(pos);
  }, 10);

  // Return to pool after 3 seconds
  setTimeout(() => {
    pool.returnObject(bullet);
  }, 3000);
}
</script>
```

---

## Summary

These examples demonstrate production-ready patterns for:

- **VR**: Advanced controller interactions, two-handed manipulation, inventory systems
- **AR**: Object placement with rotation, measurement tools, multi-object management
- **360°**: Interactive hotspots, location tours with transitions
- **Controllers**: Custom gesture recognition, advanced input handling
- **Networking**: Multi-user sync, voice chat, shared object manipulation
- **Physics**: Ragdoll simulation, constraints, impulse forces
- **Optimization**: LOD systems, object pooling, performance monitoring

All patterns are production-tested and VR/AR headset compatible.



===== FILE: plugins/individual/aframe-webxr/skills/aframe-webxr/assets/starter_aframe/README.md =====

# A-Frame Starter Template

Production-ready A-Frame starter template with interactive objects, animations, and VR support.

## Features

- 🎮 **Interactive Objects** - Click and hover interactions
- ✨ **Animations** - Rotation, position, and scale animations
- 🎯 **Cursor Controls** - Mouse and gaze-based interaction
- 🌐 **VR Ready** - Works with all WebXR headsets
- 💡 **Lighting & Shadows** - Ambient + directional lights
- 📱 **Responsive** - Works on desktop and mobile

## Quick Start

### View Locally

Simply open `index.html` in a web browser.

**Note**: For full VR features, you need HTTPS. Use a local server:

```bash
# Python 3
python -m http.server 8000

# Node.js (http-server)
npx http-server -p 8000

# PHP
php -S localhost:8000
```

Then visit `http://localhost:8000`

### VR Mode

1. Open on a VR-capable device (Quest, PC + headset, etc.)
2. Click the "Enter VR" button in the bottom-right
3. Use controllers to interact with objects

## Project Structure

```
starter_aframe/
├── index.html        # Main HTML file with A-Frame scene
├── style.css         # Styling for info panel
├── main.js           # JavaScript for interactions
└── README.md         # This file
```

## What's Included

### Scene Setup

- **Environment**: Sky + ground plane
- **Lighting**: Ambient light + directional light with shadows
- **Camera**: Desktop (WASD + mouse) and VR controls
- **Cursor**: Raycaster-based interaction

### Interactive Objects

**Box** (Blue)
- Continuous rotation animation
- Click to randomize color
- Hover to scale

**Sphere** (Red)
- Bouncing position animation
- Click to scale pulse
- Hover effects

**Cylinder** (Yellow)
- Click to spin 360°
- Hover color change

## Keyboard Shortcuts

- **WASD** - Move camera
- **Mouse** - Look around
- **R** - Randomize all object colors
- **Ctrl+Alt+I** - Toggle A-Frame Inspector

## Customization

### Change Colors

```html
<a-box color="#FF0000" position="0 1 -3"></a-box>
```

### Add New Objects

```html
<!-- Add to <a-scene> -->
<a-sphere
  class="interactive"
  position="2 1 -4"
  radius="0.5"
  color="#00FF00"
  shadow="cast: true"
  event-set__click="color: blue">
</a-sphere>
```

### Modify Animations

```html
<!-- Rotation animation -->
<a-box
  animation="property: rotation; to: 0 360 0; loop: true; dur: 5000">
</a-box>

<!-- Position animation -->
<a-sphere
  animation="property: position; to: 0 3 -5; dir: alternate; loop: true; dur: 2000">
</a-sphere>

<!-- Multiple animations -->
<a-cylinder
  animation__rotate="property: rotation; to: 0 360 0; loop: true; dur: 10000"
  animation__scale="property: scale; to: 1.5 1.5 1.5; dir: alternate; loop: true; dur: 3000">
</a-cylinder>
```

### Add Textures

```html
<a-assets>
  <img id="wood" src="textures/wood.jpg">
</a-assets>

<a-box material="src: #wood" position="0 1 -3"></a-box>
```

### Load 3D Models

```html
<a-assets>
  <a-asset-item id="tree" src="models/tree.gltf"></a-asset-item>
</a-assets>

<a-entity gltf-model="#tree" position="3 0 -5" scale="0.5 0.5 0.5"></a-entity>
```

## Adding VR Controllers

Replace the camera with a VR rig:

```html
<!-- Remove simple camera, add VR rig -->
<a-entity id="rig" position="0 0 0">
  <!-- Camera -->
  <a-entity
    id="camera"
    camera
    look-controls
    position="0 1.6 0">
  </a-entity>

  <!-- Left Hand Controller -->
  <a-entity
    hand-controls="hand: left"
    laser-controls="hand: left">
  </a-entity>

  <!-- Right Hand Controller -->
  <a-entity
    hand-controls="hand: right"
    laser-controls="hand: right"
    raycaster="objects: .interactive">
  </a-entity>
</a-entity>
```

## Performance Tips

1. **Limit Draw Calls** - Use fewer, simpler geometries
2. **Optimize Textures** - Use power-of-2 sizes (256, 512, 1024)
3. **Reduce Shadows** - Only cast shadows on key objects
4. **Use Fog** - Hide distant objects: `<a-scene fog="type: linear; color: #AAA">`
5. **Mobile Optimization** - Lower poly count for mobile devices

## Debugging

### A-Frame Inspector

Press **Ctrl+Alt+I** to open the visual scene inspector:
- View scene graph
- Edit entity properties in real-time
- Test materials and lighting
- Debug positioning

### Console Logs

The template includes console logs for:
- Scene load events
- Object interactions
- VR mode changes

Open browser DevTools (F12) to view logs.

## Common Issues

### VR Button Not Appearing

- **Solution**: Use HTTPS (required for WebXR)
- Run a local server with SSL or deploy to HTTPS host

### Objects Not Clickable

- **Solution**: Ensure cursor raycaster targets correct objects
```html
<a-cursor raycaster="objects: .interactive"></a-cursor>
```

### Performance Issues

- **Solution**: Reduce geometry complexity
```html
<!-- Low poly (faster) -->
<a-sphere segments-width="8" segments-height="6"></a-sphere>

<!-- High poly (slower) -->
<a-sphere segments-width="32" segments-height="32"></a-sphere>
```

## Next Steps

### Add Physics

```html
<script src="https://cdn.jsdelivr.net/npm/aframe-physics-system@4.2.2/dist/aframe-physics-system.min.js"></script>

<a-scene physics>
  <a-plane static-body></a-plane>
  <a-box dynamic-body position="0 5 -3"></a-box>
</a-scene>
```

### Add Environment

```html
<script src="https://cdn.jsdelivr.net/npm/aframe-environment-component@1.3.3/dist/aframe-environment-component.min.js"></script>

<a-entity environment="preset: forest"></a-entity>
```

### Add Particles

```html
<script src="https://cdn.jsdelivr.net/gh/c-frame/aframe-particle-system-component@1.2.x/dist/aframe-particle-system-component.min.js"></script>

<a-entity particle-system="preset: snow"></a-entity>
```

## Resources

- [A-Frame Documentation](https://aframe.io/docs/)
- [A-Frame School](https://aframe.io/school/)
- [A-Frame Examples](https://aframe.io/examples/)
- [A-Frame Community Components](https://github.com/c-frame)
- [WebXR Guide](https://immersiveweb.dev/)

## License

MIT - Free for personal and commercial use



===== FILE: plugins/individual/aframe-webxr/skills/aframe-webxr/assets/starter_aframe/index.html =====

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>A-Frame Starter Scene</title>
    <meta name="description" content="A-Frame VR/AR Starter Template">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <a-scene>
      <!-- Assets -->
      <a-assets>
        <audio id="click-sound" src="https://cdn.aframe.io/360-image-gallery-boilerplate/audio/click.ogg"></audio>
      </a-assets>

      <!-- Environment -->
      <a-sky color="#87CEEB"></a-sky>
      <a-plane
        rotation="-90 0 0"
        width="20"
        height="20"
        color="#7BC8A4"
        shadow="receive: true">
      </a-plane>

      <!-- Lighting -->
      <a-entity light="type: ambient; color: #BBB; intensity: 0.6"></a-entity>
      <a-entity
        light="type: directional; color: #FFF; intensity: 0.5; castShadow: true"
        position="5 10 5">
      </a-entity>

      <!-- Interactive Objects -->
      <a-box
        id="box1"
        class="interactive"
        position="-1 0.5 -3"
        rotation="0 45 0"
        color="#4CC3D9"
        shadow="cast: true"
        animation="property: rotation; to: 0 405 0; loop: true; dur: 10000; easing: linear"
        event-set__mouseenter="scale: 1.2 1.2 1.2"
        event-set__mouseleave="scale: 1 1 1"
        sound="on: click; src: #click-sound">
      </a-box>

      <a-sphere
        id="sphere1"
        class="interactive"
        position="0 1.25 -5"
        radius="0.5"
        color="#EF2D5E"
        shadow="cast: true"
        animation__position="property: position; to: 0 2 -5; dir: alternate; loop: true; dur: 2000; easing: easeInOutQuad"
        event-set__click="color: orange"
        sound="on: click; src: #click-sound">
      </a-sphere>

      <a-cylinder
        id="cylinder1"
        class="interactive"
        position="1 0.75 -3"
        radius="0.3"
        height="1.5"
        color="#FFC65D"
        shadow="cast: true"
        event-set__mouseenter="color: yellow"
        event-set__mouseleave="color: #FFC65D"
        sound="on: click; src: #click-sound">
      </a-cylinder>

      <!-- Camera -->
      <a-camera position="0 1.6 0" look-controls wasd-controls>
        <a-cursor
          raycaster="objects: .interactive"
          fuse="false">
        </a-cursor>
      </a-camera>
    </a-scene>

    <!-- Info Panel -->
    <div id="info">
      <strong>A-Frame Starter Scene</strong><br>
      WASD - Move | Mouse - Look<br>
      Click on objects to interact
    </div>

    <script src="main.js"></script>
  </body>
</html>

```


===== FILE: plugins/individual/aframe-webxr/skills/aframe-webxr/assets/starter_aframe/main.js =====

```js
// A-Frame Starter Template - Main JavaScript

console.log('A-Frame scene initialized');

// Wait for scene to load
const scene = document.querySelector('a-scene');

scene.addEventListener('loaded', () => {
  console.log('Scene loaded and ready');

  // Get interactive objects
  const box = document.querySelector('#box1');
  const sphere = document.querySelector('#sphere1');
  const cylinder = document.querySelector('#cylinder1');

  // Add click handlers
  box.addEventListener('click', (evt) => {
    console.log('Box clicked at:', evt.detail.intersection.point);
    // Randomize color
    box.setAttribute('color', `#${Math.floor(Math.random()*16777215).toString(16)}`);
  });

  sphere.addEventListener('click', (evt) => {
    console.log('Sphere clicked');
    // Scale animation
    sphere.setAttribute('animation__scale', {
      property: 'scale',
      to: '1.5 1.5 1.5',
      dur: 500,
      dir: 'alternate',
      loop: 1
    });
  });

  cylinder.addEventListener('click', (evt) => {
    console.log('Cylinder clicked');
    // Rotate animation
    const rotation = cylinder.getAttribute('rotation');
    cylinder.setAttribute('animation__spin', {
      property: 'rotation',
      to: `${rotation.x} ${rotation.y + 360} ${rotation.z}`,
      dur: 1000
    });
  });
});

// VR mode events
scene.addEventListener('enter-vr', () => {
  console.log('Entered VR mode');
  // Hide desktop UI if needed
  document.querySelector('#info').style.display = 'none';
});

scene.addEventListener('exit-vr', () => {
  console.log('Exited VR mode');
  // Show desktop UI
  document.querySelector('#info').style.display = 'block';
});

// Keyboard shortcuts
document.addEventListener('keydown', (evt) => {
  // Press R to randomize object colors
  if (evt.key === 'r' || evt.key === 'R') {
    const interactiveObjects = document.querySelectorAll('.interactive');
    interactiveObjects.forEach(el => {
      const randomColor = `#${Math.floor(Math.random()*16777215).toString(16)}`;
      el.setAttribute('color', randomColor);
    });
    console.log('Randomized colors');
  }

  // Press I to toggle inspector (Ctrl+Alt+I also works)
  if ((evt.key === 'i' || evt.key === 'I') && evt.ctrlKey && evt.altKey) {
    // Inspector toggle is built-in to A-Frame
    console.log('Inspector toggled');
  }
});

```


===== FILE: plugins/individual/aframe-webxr/skills/aframe-webxr/assets/starter_aframe/style.css =====

```css
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
}

#info {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  color: white;
  padding: 20px 24px;
  border-radius: 12px;
  max-width: 300px;
  font-size: 14px;
  line-height: 1.6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 1000;
}

#info strong {
  font-size: 16px;
  font-weight: 600;
  display: block;
  margin-bottom: 8px;
  color: #4FC3F7;
}

@media (max-width: 768px) {
  #info {
    bottom: 10px;
    left: 10px;
    right: 10px;
    max-width: none;
    padding: 16px 20px;
    font-size: 13px;
  }

  #info strong {
    font-size: 15px;
  }
}

```
