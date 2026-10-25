# Design Skills for Gemini, part 5 of 6: Authoring tools and integration

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
| `blender-web-pipeline` | Blender to web export workflows for 3D models and animations. Use this skill when exporting Blender models to glTF for web, optimizing 3D assets for Three.js or Babylon.js, batch processing models with Python scripts, automating Blender workflows, or creating web-ready 3D pipelines. Triggers on tasks involving Blender glTF export, bpy scripting, 3D asset optimization, model compression, texture baking, or Blender automation. Exports models for threejs-webgl, react-three-fiber, and babylonjs-engine skills. |
| `spline-interactive` | Browser-based 3D design tool with visual editor, animation, and web export. Use this skill when creating 3D scenes without code, designing interactive web experiences, prototyping 3D UI, exporting to React/web, or building designer-friendly 3D content. Triggers on tasks involving Spline, no-code 3D, visual 3D editor, 3D animation, state-based interactions, React Spline integration, or scene export. Alternative to Three.js for designers who prefer visual tools over code. |
| `rive-interactive` | State machine-based vector animation with runtime interactivity and web integration. Use this skill when creating interactive animations, state-driven UI, animated components with logic, or designer-created animations with runtime control. Triggers on tasks involving Rive, state machines, interactive vector animations, animation with input handling, ViewModel data binding, or React Rive integration. Alternative to Lottie for animations requiring state machines and two-way interactivity. |
| `substance-3d-texturing` | Comprehensive skill for Adobe Substance 3D Painter texturing and material creation workflow. Use this skill when creating PBR materials, exporting textures for web/game engines, optimizing 3D assets for real-time rendering, or automating texture workflows. Triggers on tasks involving Substance 3D Painter, PBR texturing, material creation, texture export for Three.js, Babylon.js, Unity, Unreal, glTF optimization, or Python API automation. Creates optimized textures for threejs-webgl, react-three-fiber, and babylonjs-engine materials. |
| `web3d-integration-patterns` | Meta-skill for combining Three.js, GSAP ScrollTrigger, React Three Fiber, Motion, and React Spring for complex 3D web experiences. Use when building applications that integrate multiple 3D and animation libraries, requiring architecture patterns, state management, and performance optimization across the stack. Triggers on tasks involving library integration, multi-library architectures, scroll-driven 3D experiences, physics-based 3D animations, or complex interactive 3D applications. |


# Skill: blender-web-pipeline


===== FILE: plugins/individual/blender-web-pipeline/skills/blender-web-pipeline/SKILL.md =====

---
name: blender-web-pipeline
description: Blender to web export workflows for 3D models and animations. Use this skill when exporting Blender models to glTF for web, optimizing 3D assets for Three.js or Babylon.js, batch processing models with Python scripts, automating Blender workflows, or creating web-ready 3D pipelines. Triggers on tasks involving Blender glTF export, bpy scripting, 3D asset optimization, model compression, texture baking, or Blender automation. Exports models for threejs-webgl, react-three-fiber, and babylonjs-engine skills.
---

# Blender Web Pipeline

## Overview

Blender Web Pipeline skill provides workflows for exporting 3D models and animations from Blender to web-optimized formats (primarily glTF 2.0). It covers Python scripting for batch processing, optimization techniques for web performance, and integration with web 3D libraries like Three.js and Babylon.js.

**When to use this skill:**
- Exporting Blender models for web applications
- Batch processing multiple 3D assets
- Optimizing file sizes for web delivery
- Automating repetitive Blender tasks
- Creating production pipelines for 3D web content
- Converting legacy formats to glTF

**Key capabilities:**
- glTF 2.0 export with optimization
- Python (bpy) automation scripts
- Texture baking and compression
- LOD (Level of Detail) generation
- Batch processing workflows
- Material and lighting optimization for web

## Core Concepts

### glTF 2.0 Format

**Why glTF for Web:**
- Industry-standard 3D format for web
- Efficient binary encoding (.glb)
- PBR materials support
- Animation and skinning
- Extensible with custom data
- Wide library support (Three.js, Babylon.js, etc.)

**glTF vs GLB:**
```
.gltf = JSON + external .bin + external textures
.glb  = Single binary file (recommended for web)
```

### Blender Python API (bpy)

**Access Blender data and operations via Python:**

```python
import bpy

# Access scene data
scene = bpy.context.scene
objects = bpy.data.objects

# Modify objects
obj = bpy.data.objects['Cube']
obj.location = (0, 0, 1)
obj.scale = (2, 2, 2)

# Export glTF
bpy.ops.export_scene.gltf(
    filepath='/path/to/model.glb',
    export_format='GLB'
)
```

### Web Optimization Goals

**Target Metrics:**
- File size: <5 MB per model (ideal <1 MB)
- Polygon count: <50k triangles for real-time
- Texture resolution: 2048x2048 max (1024x1024 preferred)
- Draw calls: Minimize via texture atlases
- Load time: <2 seconds on average connection

## Common Patterns

### 1. Basic glTF Export (Manual)

```python
# Blender Python Console or script

import bpy

# Select objects to export (optional - exports all if none selected)
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects['MyModel'].select_set(True)

# Export as GLB
bpy.ops.export_scene.gltf(
    filepath='/path/to/output.glb',
    export_format='GLB',                # Binary format
    use_selection=True,                 # Export selected only
    export_apply=True,                  # Apply modifiers
    export_texcoords=True,              # UV coordinates
    export_normals=True,                # Normals
    export_materials='EXPORT',          # Export materials
    export_colors=True,                 # Vertex colors
    export_cameras=False,               # Skip cameras
    export_lights=False,                # Skip lights
    export_animations=True,             # Include animations
    export_draco_mesh_compression_enable=True,  # Compress geometry
    export_draco_mesh_compression_level=6,      # 0-10 (6 recommended)
    export_draco_position_quantization=14,      # 8-14 bits
    export_draco_normal_quantization=10,        # 8-10 bits
    export_draco_texcoord_quantization=12       # 8-12 bits
)
```

### 2. Python Script for Batch Export

```python
#!/usr/bin/env blender --background --python
"""
Batch export all .blend files in a directory to glTF
Usage: blender --background --python batch_export.py -- /path/to/blend/files
"""

import bpy
import os
import sys

# Get command line arguments after --
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []

input_dir = argv[0] if argv else "/path/to/models"
output_dir = argv[1] if len(argv) > 1 else input_dir + "_gltf"

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Find all .blend files
blend_files = [f for f in os.listdir(input_dir) if f.endswith('.blend')]

print(f"Found {len(blend_files)} .blend files")

for blend_file in blend_files:
    input_path = os.path.join(input_dir, blend_file)
    output_name = blend_file.replace('.blend', '.glb')
    output_path = os.path.join(output_dir, output_name)

    print(f"Processing: {blend_file}")

    # Open blend file
    bpy.ops.wm.open_mainfile(filepath=input_path)

    # Export as GLB with optimizations
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6
    )

    print(f"  Exported: {output_name}")

print("Batch export complete!")
```

**Run batch script:**

```bash
blender --background --python batch_export.py -- /models/source /models/output
```

### 3. Optimize Model for Web (Decimation)

```python
import bpy

def optimize_mesh(obj, target_ratio=0.5):
    """Reduce polygon count using decimation modifier."""

    if obj.type != 'MESH':
        return

    # Add Decimate modifier
    decimate = obj.modifiers.new(name='Decimate', type='DECIMATE')
    decimate.ratio = target_ratio  # 0.5 = 50% of original polygons
    decimate.use_collapse_triangulate = True

    # Apply modifier
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier='Decimate')

    print(f"Optimized {obj.name}: {len(obj.data.polygons)} polygons")

# Optimize all selected meshes
for obj in bpy.context.selected_objects:
    optimize_mesh(obj, target_ratio=0.3)
```

### 4. Texture Baking for Web

```python
import bpy

def bake_textures(obj, resolution=1024):
    """Bake all materials to single texture."""

    # Setup bake settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.bake_type = 'COMBINED'

    # Create bake image
    bake_image = bpy.data.images.new(
        name=f"{obj.name}_bake",
        width=resolution,
        height=resolution
    )

    # Create bake material
    mat = bpy.data.materials.new(name=f"{obj.name}_baked")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Add Image Texture node
    tex_node = nodes.new(type='ShaderNodeTexImage')
    tex_node.image = bake_image
    tex_node.select = True
    nodes.active = tex_node

    # Assign material
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # Select object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Bake
    bpy.ops.object.bake(type='COMBINED')

    # Save baked texture
    bake_image.filepath_raw = f"/tmp/{obj.name}_bake.png"
    bake_image.file_format = 'PNG'
    bake_image.save()

    print(f"Baked {obj.name} to {bake_image.filepath_raw}")

# Bake selected objects
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        bake_textures(obj, resolution=2048)
```

### 5. Generate LOD (Level of Detail)

```python
import bpy

def generate_lods(obj, lod_levels=[0.75, 0.5, 0.25]):
    """Generate LOD copies with decreasing polygon counts."""

    lod_objects = []

    for i, ratio in enumerate(lod_levels):
        # Duplicate object
        lod_obj = obj.copy()
        lod_obj.data = obj.data.copy()
        lod_obj.name = f"{obj.name}_LOD{i}"

        # Link to scene
        bpy.context.collection.objects.link(lod_obj)

        # Add Decimate modifier
        decimate = lod_obj.modifiers.new(name='Decimate', type='DECIMATE')
        decimate.ratio = ratio

        # Apply modifier
        bpy.context.view_layer.objects.active = lod_obj
        bpy.ops.object.modifier_apply(modifier='Decimate')

        lod_objects.append(lod_obj)

        print(f"Created {lod_obj.name}: {len(lod_obj.data.polygons)} polygons")

    return lod_objects

# Generate LODs for selected object
if bpy.context.active_object:
    generate_lods(bpy.context.active_object)
```

### 6. Export with Texture Compression

```python
import bpy
import os

def export_optimized_gltf(filepath, texture_max_size=1024):
    """Export glTF with downscaled textures."""

    # Downscale all textures
    for img in bpy.data.images:
        if img.size[0] > texture_max_size or img.size[1] > texture_max_size:
            img.scale(texture_max_size, texture_max_size)
            print(f"Downscaled {img.name} to {texture_max_size}x{texture_max_size}")

    # Export with Draco compression
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        export_apply=True,
        export_image_format='JPEG',  # JPEG for smaller size (or PNG for quality)
        export_jpeg_quality=85,       # 0-100
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=8,  # Max compression
        export_draco_position_quantization=12,
        export_draco_normal_quantization=8,
        export_draco_texcoord_quantization=10
    )

# Export optimized
export_optimized_gltf('/path/to/optimized.glb', texture_max_size=512)
```

### 7. Command-Line Automation

```bash
#!/bin/bash
# Batch export Blender files to glTF without opening GUI

SCRIPT_DIR="$(dirname "$0")"

# Export all .blend files in current directory
for blend_file in *.blend; do
    echo "Exporting $blend_file..."

    blender --background "$blend_file" --python - <<EOF
import bpy
import os

# Get output filename
filename = os.path.splitext(bpy.data.filepath)[0]
output = filename + '.glb'

# Export
bpy.ops.export_scene.gltf(
    filepath=output,
    export_format='GLB',
    export_apply=True,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6
)

print(f'Exported to {output}')
EOF

done

echo "All files exported!"
```

## Integration Patterns

### With Three.js

```javascript
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const loader = new GLTFLoader();

// Setup Draco decoder for compressed models
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/');
loader.setDRACOLoader(dracoLoader);

// Load Blender export
loader.load('/models/exported.glb', (gltf) => {
  scene.add(gltf.scene);

  // Play animations
  if (gltf.animations.length > 0) {
    const mixer = new THREE.AnimationMixer(gltf.scene);
    const action = mixer.clipAction(gltf.animations[0]);
    action.play();
  }
});
```

### With React Three Fiber

```jsx
import { useGLTF } from '@react-three/drei';

function Model() {
  const { scene } = useGLTF('/models/exported.glb');
  return <primitive object={scene} />;
}

// Preload for better performance
useGLTF.preload('/models/exported.glb');
```

### With Babylon.js

```javascript
import * as BABYLON from '@babylonjs/core';
import '@babylonjs/loaders/glTF';

BABYLON.SceneLoader.ImportMesh(
  '',
  '/models/',
  'exported.glb',
  scene,
  (meshes) => {
    console.log('Loaded meshes:', meshes);
  }
);
```

## Optimization Techniques

### 1. Geometry Optimization

**Decimate Modifier:**
```python
# Reduce polygon count by 70%
obj.modifiers.new(name='Decimate', type='DECIMATE')
obj.modifiers['Decimate'].ratio = 0.3
```

**Merge by Distance:**
```python
# Remove duplicate vertices
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0001)
bpy.ops.object.mode_set(mode='OBJECT')
```

**Triangulate Faces:**
```python
# Ensure all faces are triangles (required for some engines)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.quads_convert_to_tris()
bpy.ops.object.mode_set(mode='OBJECT')
```

### 2. Texture Optimization

**Image Compression:**
```python
# Save textures as JPEG (lossy but smaller)
for img in bpy.data.images:
    img.file_format = 'JPEG'
    img.filepath_raw = f"/output/{img.name}.jpg"
    img.save()
```

**Texture Atlas:**
```python
# Combine multiple textures into one atlas
# Use Smart UV Project for automatic atlasing
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')
```

### 3. Material Simplification

**Convert to PBR:**
```python
# Ensure materials use Principled BSDF (glTF standard)
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes = True

    nodes = mat.node_tree.nodes
    principled = nodes.get('Principled BSDF')

    if not principled:
        principled = nodes.new(type='ShaderNodeBsdfPrincipled')
        output = nodes.get('Material Output')
        mat.node_tree.links.new(principled.outputs[0], output.inputs[0])
```

## Common Pitfalls

### 1. Large File Sizes

**Problem:** Exported .glb files are 20+ MB

**Solutions:**
- Enable Draco compression (60-90% reduction)
- Reduce texture resolution (2048 → 1024 or 512)
- Use JPEG instead of PNG for textures
- Decimate geometry (target <50k triangles)
- Remove unused materials/textures

### 2. Missing Textures in Export

**Problem:** Textures don't appear in web viewer

**Solutions:**
- Ensure all images are saved (not packed)
- Use relative paths for textures
- Export with "Export Images" enabled
- Check image format compatibility (PNG/JPEG)

### 3. Animations Not Playing

**Problem:** Animations don't export or play incorrectly

**Solutions:**
- Ensure animations are on timeline (not NLA strips)
- Export with "Export Animations" enabled
- Check animation actions are assigned to objects
- Use "Bake Actions" for complex rigs

### 4. Materials Look Different

**Problem:** Materials render differently in web vs Blender

**Solutions:**
- Use Principled BSDF (maps to glTF PBR)
- Avoid custom shader nodes (won't export)
- Use supported texture types (Base Color, Metallic, Roughness, Normal, Emission)
- Test in glTF viewer before deploying

### 5. Slow Export Times

**Problem:** Export takes 10+ minutes

**Solutions:**
- Apply modifiers before export (don't export non-destructively)
- Reduce geometry complexity
- Remove unused data (orphan cleanup)
- Use command-line export (faster than GUI)

### 6. Performance Issues in Browser

**Problem:** Model lags in browser

**Solutions:**
- Generate LODs (Level of Detail)
- Use instancing for repeated objects
- Limit draw calls (merge objects, texture atlases)
- Reduce polygon count (<50k triangles)
- Optimize shaders (avoid transparency/refraction)

## Best Practices

### Pre-Export Checklist

```
☐ Apply all modifiers
☐ Merge vertices (remove doubles)
☐ Triangulate faces (if required)
☐ Optimize polygon count (<50k triangles)
☐ UV unwrap all meshes
☐ Bake materials (if complex)
☐ Resize textures (max 2048x2048)
☐ Use Principled BSDF materials
☐ Remove unused data (orphan cleanup)
☐ Name objects descriptively
☐ Set origin points correctly
☐ Apply transformations (Ctrl+A)
```

### Export Settings

```python
# Recommended glTF export settings
bpy.ops.export_scene.gltf(
    filepath='/output.glb',
    export_format='GLB',                # Binary format
    export_apply=True,                  # Apply modifiers
    export_image_format='JPEG',         # Smaller file size
    export_jpeg_quality=85,             # Quality vs size
    export_draco_mesh_compression_enable=True,  # Enable compression
    export_draco_mesh_compression_level=6,      # Balance speed/size
    export_animations=True,             # Include animations
    export_lights=False,                # Skip lights (recreate in code)
    export_cameras=False                # Skip cameras
)
```

## Resources

This skill includes:

### scripts/
- `batch_export.py` - Batch export .blend files to glTF
- `optimize_model.py` - Optimize geometry and textures for web
- `generate_lods.py` - Generate LOD copies automatically

### references/
- `gltf_export_guide.md` - Complete glTF export reference
- `bpy_api_reference.md` - Blender Python API quick reference
- `optimization_strategies.md` - Detailed optimization techniques

### assets/
- `export_template.blend` - Pre-configured export template
- `shader_library/` - Web-optimized PBR shaders

## Related Skills

- **threejs-webgl** - Load and render exported glTF models in Three.js
- **react-three-fiber** - Use glTF models in React applications
- **babylonjs-engine** - Alternative 3D engine for web
- **playcanvas-engine** - Game engine that supports glTF import



===== FILE: plugins/individual/blender-web-pipeline/skills/blender-web-pipeline/references/bpy_api_reference.md =====

# Blender Python API Quick Reference

Essential bpy (Blender Python) API commands for automation.

## Accessing Data

```python
import bpy

# Scene and Objects
bpy.context.scene  # Active scene
bpy.data.objects  # All objects
bpy.data.objects['Name']  # Get object by name
bpy.context.selected_objects  # Selected objects
bpy.context.active_object  # Active object

# Collections
bpy.data.collections  # All collections
bpy.context.collection  # Active collection

# Materials and Textures
bpy.data.materials  # All materials
bpy.data.images  # All images/textures

# Meshes
bpy.data.meshes  # All mesh data
```

## Object Operations

```python
# Selection
bpy.ops.object.select_all(action='SELECT')  # Select all
bpy.ops.object.select_all(action='DESELECT')  # Deselect all
obj.select_set(True)  # Select specific object

# Transformation
obj.location = (x, y, z)
obj.rotation_euler = (rx, ry, rz)
obj.scale = (sx, sy, sz)

# Modifiers
modifier = obj.modifiers.new(name='Name', type='TYPE')
bpy.ops.object.modifier_apply(modifier='Name')

# Duplication
new_obj = obj.copy()
new_obj.data = obj.data.copy()
bpy.context.collection.objects.link(new_obj)
```

## Mesh Editing

```python
# Edit Mode
bpy.ops.object.mode_set(mode='EDIT')

# Common Operations
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0001)  # Merge vertices
bpy.ops.mesh.quads_convert_to_tris()  # Triangulate
bpy.ops.uv.smart_project()  # UV unwrap

# Return to Object Mode
bpy.ops.object.mode_set(mode='OBJECT')
```

## File Operations

```python
# Open File
bpy.ops.wm.open_mainfile(filepath='/path/to/file.blend')

# Save File
bpy.ops.wm.save_as_mainfile(filepath='/path/to/file.blend')

# Import/Export
bpy.ops.import_scene.obj(filepath='/path/to/model.obj')
bpy.ops.export_scene.gltf(filepath='/path/to/model.glb')
```



===== FILE: plugins/individual/blender-web-pipeline/skills/blender-web-pipeline/references/gltf_export_guide.md =====

# Blender glTF Export Complete Guide

Reference guide for glTF 2.0 export settings and options in Blender.

## Export Format Options

```python
export_format='GLB'  # or 'GLTF_SEPARATE' or 'GLTF_EMBEDDED'
```

- **GLB**: Single binary file (recommended for web)
- **GLTF_SEPARATE**: JSON + separate .bin + separate textures
- **GLTF_EMBEDDED**: JSON with embedded Base64 data (large file)

## All Export Parameters

```python
bpy.ops.export_scene.gltf(
    # File Settings
    filepath='/path/to/output.glb',
    export_format='GLB',  # 'GLB', 'GLTF_SEPARATE', 'GLTF_EMBEDDED'

    # Include Settings
    use_selection=False,  # Export selected objects only
    use_visible=False,  # Export visible objects only
    use_renderable=False,  # Export renderable objects only
    use_active_collection=False,  # Export active collection only
    use_active_scene=False,  # Export active scene only

    # Transform Settings
    export_yup=True,  # Y-axis up (default for glTF)
    export_apply=False,  # Apply modifiers (True recommended)

    # Data Settings
    export_texcoords=True,  # UV coordinates
    export_normals=True,  # Normals
    export_draco_mesh_compression_enable=False,  # Enable Draco compression
    export_draco_mesh_compression_level=6,  # 0-10 (higher = smaller + slower)
    export_draco_position_quantization=14,  # 8-14 bits
    export_draco_normal_quantization=10,  # 8-10 bits
    export_draco_texcoord_quantization=12,  # 8-12 bits
    export_draco_color_quantization=10,  # 8-10 bits
    export_draco_generic_quantization=12,  # 8-12 bits
    export_tangents=False,  # Tangents (auto-computed by engines)
    export_materials='EXPORT',  # 'EXPORT', 'PLACEHOLDER', 'NONE'
    export_colors=True,  # Vertex colors
    export_attributes=True,  # Custom attributes
    export_cameras=False,  # Export cameras
    export_lights=False,  # Export lights

    # Animation Settings
    export_animations=True,  # Export animations
    export_frame_range=True,  # Use scene frame range
    export_frame_step=1,  # Frame step
    export_force_sampling=True,  # Force sampling (all frames)
    export_nla_strips=True,  # Export NLA strips
    export_nla_strips_merged_animation_name='Animation',  # Merged animation name
    export_def_bones=False,  # Export deformation bones only
    export_current_frame=False,  # Export current frame
    export_skins=True,  # Export skinning data
    export_all_influences=False,  # Export all bone influences
    export_morph=True,  # Export shape keys
    export_morph_normal=True,  # Export shape key normals
    export_morph_tangent=False,  # Export shape key tangents

    # Image Settings
    export_image_format='AUTO',  # 'AUTO', 'JPEG', 'PNG'
    export_jpeg_quality=75,  # 0-100
    export_keep_originals=False,  # Keep original images

    # Extras
    export_extras=False,  # Export custom properties
    export_copyright='',  # Copyright notice
    export_custom_props=False,  # Export custom properties
)
```

## Recommended Presets

### Minimal (Smallest File)
```python
export_format='GLB',
export_apply=True,
export_image_format='JPEG',
export_jpeg_quality=75,
export_draco_mesh_compression_enable=True,
export_draco_mesh_compression_level=10,  # Max compression
export_animations=False,
export_cameras=False,
export_lights=False
```

### Standard (Balanced)
```python
export_format='GLB',
export_apply=True,
export_image_format='JPEG',
export_jpeg_quality=85,
export_draco_mesh_compression_enable=True,
export_draco_mesh_compression_level=6,
export_animations=True
```

### High Quality (Larger Files)
```python
export_format='GLB',
export_apply=True,
export_image_format='PNG',
export_draco_mesh_compression_enable=False,
export_animations=True,
export_morph=True
```



===== FILE: plugins/individual/blender-web-pipeline/skills/blender-web-pipeline/references/optimization_strategies.md =====

# 3D Model Optimization Strategies

Advanced optimization techniques for web-ready 3D models.

## Polygon Reduction

### 1. Decimate Modifier (Automatic)
Best for: Organic shapes, detailed models

```python
decimate = obj.modifiers.new(name='Decimate', type='DECIMATE')
decimate.ratio = 0.5  # 50% reduction
decimate.use_collapse_triangulate = True
```

### 2. Manual Retopology
Best for: Character models, hero assets
- Tools: Quad Draw, PolyBuild, Shrinkwrap modifier
- Target: Clean edge loops, optimized topology

### 3. Normal Map Baking
Best for: Static props, architecture

```python
# Bake high-poly detail to normal map
# Apply to low-poly model in web engine
```

## Texture Optimization

### 1. Texture Atlasing
Combine multiple textures into one large texture

Benefits:
- Fewer draw calls
- Better performance
- Smaller total file size

### 2. Texture Compression
- Use JPEG for diffuse maps (lossy, smaller)
- Use PNG for alpha/normal maps (lossless)
- Target resolution: 512-1024px

### 3. MIP Mapping
Auto-generated by web engines
- Smaller textures for distant objects
- Better performance, reduced aliasing

## File Size Reduction

Target sizes:
- Small props: <100 KB
- Character models: 500 KB - 1 MB
- Environment assets: 1-5 MB

Strategies:
1. Draco compression (60-90% reduction)
2. Lower texture resolution
3. JPEG instead of PNG
4. Reduce polygon count
5. Remove unused data

## Performance Targets

- Triangles: <50,000 per model
- Draw calls: Minimize (texture atlases, instancing)
- Texture memory: <50 MB total
- Load time: <2 seconds



===== FILE: plugins/individual/blender-web-pipeline/agents/blender-web-pipeline-pipeline.md =====

# Blender Web Pipeline Pipeline Specialist

## Role

Expert pipeline specialist for Blender Web Pipeline workflows, asset optimization, and web integration.

## Expertise

- Asset export and optimization
- Web-ready format conversion
- Texture and material optimization
- Automated pipeline workflows
- Quality assurance and validation
- Cross-platform compatibility

## When to use

Activate this agent when working on:
- Asset export pipelines
- Batch processing workflows
- Optimization for web delivery
- Integration with web frameworks
- Automated quality checks

## Approach

1. Analyze asset requirements and constraints
2. Design optimal export pipeline
3. Implement automation scripts
4. Optimize for web performance
5. Validate output quality

## Tools

This agent has access to:
- Blender Web Pipeline skill knowledge
- Pipeline automation scripts
- Optimization guidelines
- Quality validation checklists



===== FILE: plugins/individual/blender-web-pipeline/commands/batch_export.md =====

# /blender-web-pipeline-batch_export

Blender Web Pipeline - Batch Export

## Description

Executes the batch_export script for Blender Web Pipeline.

## Usage

```bash
/blender-web-pipeline-batch_export
```

## Implementation

This command runs the `batch_export.py` script from the Blender Web Pipeline skill, which provides automated assistance for batch export.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/blender-web-pipeline/commands/generate_lods.md =====

# /blender-web-pipeline-generate_lods

Blender Web Pipeline - Generate Lods

## Description

Executes the generate_lods script for Blender Web Pipeline.

## Usage

```bash
/blender-web-pipeline-generate_lods
```

## Implementation

This command runs the `generate_lods.py` script from the Blender Web Pipeline skill, which provides automated assistance for generate lods.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/blender-web-pipeline/commands/optimize_model.md =====

# /blender-web-pipeline-optimize_model

Blender Web Pipeline - Optimize Model

## Description

Executes the optimize_model script for Blender Web Pipeline.

## Usage

```bash
/blender-web-pipeline-optimize_model
```

## Implementation

This command runs the `optimize_model.py` script from the Blender Web Pipeline skill, which provides automated assistance for optimize model.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/blender-web-pipeline/skills/blender-web-pipeline/scripts/batch_export.py =====

```py
#!/usr/bin/env blender --background --python
"""
Batch Export Blender Files to glTF

Usage:
    blender --background --python batch_export.py -- /input/dir /output/dir
"""

import bpy
import os
import sys

argv = sys.argv[argv.index("--") + 1:] if "--" in sys.argv else []
input_dir = argv[0] if argv else "/models"
output_dir = argv[1] if len(argv) > 1 else input_dir + "_gltf"

os.makedirs(output_dir, exist_ok=True)

blend_files = [f for f in os.listdir(input_dir) if f.endswith('.blend')]

for blend_file in blend_files:
    input_path = os.path.join(input_dir, blend_file)
    output_path = os.path.join(output_dir, blend_file.replace('.blend', '.glb'))

    bpy.ops.wm.open_mainfile(filepath=input_path)
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6
    )
    print(f"Exported: {blend_file}")

```


===== FILE: plugins/individual/blender-web-pipeline/skills/blender-web-pipeline/scripts/generate_lods.py =====

```py
#!/usr/bin/env python3
"""
Generate LOD (Level of Detail) Copies

Usage:
    blender --background model.blend --python generate_lods.py
"""

import bpy

def generate_lods(obj, levels=[0.75, 0.5, 0.25]):
    """Create LOD copies with decreasing detail."""
    for i, ratio in enumerate(levels):
        lod_obj = obj.copy()
        lod_obj.data = obj.data.copy()
        lod_obj.name = f"{obj.name}_LOD{i}"

        bpy.context.collection.objects.link(lod_obj)

        decimate = lod_obj.modifiers.new(name='Decimate', type='DECIMATE')
        decimate.ratio = ratio

        bpy.context.view_layer.objects.active = lod_obj
        bpy.ops.object.modifier_apply(modifier='Decimate')

        print(f"Created {lod_obj.name}: {len(lod_obj.data.polygons)} polygons")

# Generate LODs for all meshes
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        generate_lods(obj)

print("LOD generation complete")

```


===== FILE: plugins/individual/blender-web-pipeline/skills/blender-web-pipeline/scripts/optimize_model.py =====

```py
#!/usr/bin/env python3
"""
Optimize Blender Model for Web

Usage:
    blender --background model.blend --python optimize_model.py
"""

import bpy

def optimize_mesh(obj, ratio=0.5):
    """Reduce polygon count."""
    if obj.type != 'MESH':
        return

    decimate = obj.modifiers.new(name='Decimate', type='DECIMATE')
    decimate.ratio = ratio
    decimate.use_collapse_triangulate = True

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier='Decimate')

    print(f"Optimized {obj.name}: {len(obj.data.polygons)} polygons")

# Optimize all meshes
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        optimize_mesh(obj, ratio=0.3)

print("Optimization complete")

```


===== FILE: plugins/individual/blender-web-pipeline/skills/blender-web-pipeline/assets/README.md =====

# Blender Web Pipeline Assets

Template files and resources for Blender to web workflows.

## Included Assets

### export_template.blend
Pre-configured Blender template with:
- Optimized export settings
- PBR material setup
- LOD examples
- Proper UV unwrapping

### shader_library/
Collection of web-optimized PBR shaders:
- Basic PBR material
- Emissive material
- Transparent material
- Metallic material

## Usage

1. Open `export_template.blend` in Blender
2. Replace placeholder geometry with your models
3. Use pre-configured materials from shader_library
4. Export using File → Export → glTF 2.0 (.glb)
5. Test in web viewer before deploying

## Quick Start

```bash
# Open template
blender export_template.blend

# Or use as base for new projects
blender --factory-startup export_template.blend --save-as mynewproject.blend
```



# Skill: spline-interactive


===== FILE: plugins/individual/spline-interactive/skills/spline-interactive/SKILL.md =====

---
name: spline-interactive
description: Browser-based 3D design tool with visual editor, animation, and web export. Use this skill when creating 3D scenes without code, designing interactive web experiences, prototyping 3D UI, exporting to React/web, or building designer-friendly 3D content. Triggers on tasks involving Spline, no-code 3D, visual 3D editor, 3D animation, state-based interactions, React Spline integration, or scene export. Alternative to Three.js for designers who prefer visual tools over code.
---

# Spline Interactive - Browser-Based 3D Design and Animation

## Overview

Spline is a browser-based 3D design and animation platform that enables creators to build interactive 3D experiences without requiring code or specialized software knowledge. It provides a collaborative visual editor for designing, animating, and exporting 3D scenes across multiple platforms.

**Key Features**:
- Visual 3D modeling with parametric shapes, extrusion, and boolean operations
- State-based animation system with timeline controls
- Interactive event system (mouse, keyboard, collision, scroll)
- Multiple export options (React components, web code, public URLs)
- Real-time collaboration with team libraries
- AI-powered generation (3D from text, textures, style transfer)
- Built-in physics and particle systems

**When to Use This Skill**:
- Creating 3D web experiences without writing Three.js code
- Designing interactive product showcases or configurators
- Prototyping 3D UI/UX concepts visually
- Building marketing pages with 3D elements
- Collaborating with designers on 3D content
- Exporting scenes for React or vanilla JS integration

**Alternatives**:
- **Three.js** (threejs-webgl): For developers who prefer code-first approach and need maximum control
- **Babylon.js** (babylonjs-engine): For game-focused projects with built-in physics
- **React Three Fiber** (react-three-fiber): For React developers who want to build 3D with JSX

## Core Concepts

### 1. Scene Structure

Spline organizes projects into scenes containing:
- **Objects**: 3D models, shapes, text, images
- **Lights**: Directional, point, spot lights
- **Cameras**: Orbital, perspective, orthographic
- **Events**: Interaction triggers
- **States**: Animation keyframes

### 2. Components System

Reusable elements that can be:
- Created from any object or group
- Instantiated multiple times
- Updated across all instances
- Overridden per instance

### 3. State-Based Animation

Animations are defined as transitions between states:
- **Default State**: Initial appearance
- **Additional States**: Target appearances
- **Events**: Triggers that cause state transitions
- **Transitions**: Duration, easing, properties

### 4. Interactivity Model

Event-driven system with:
- **Events**: User actions or scene triggers
- **Conditions**: Logic gates (if/else)
- **Actions**: State changes, audio, scene switches
- **Variables**: Dynamic data from APIs or user input

### 5. Export Options

Multiple deployment methods:
- **Public URL**: Direct shareable link
- **Code Export**: React component or vanilla JS
- **Spline Viewer**: Embedded iframe
- **Self-Hosted**: Download and host independently

## Common Patterns

### Pattern 1: Basic React Integration

**Use Case**: Embed a Spline scene in a React application

**Implementation**:

```bash
# Installation
npm install @splinetool/react-spline @splinetool/runtime
```

```jsx
import Spline from '@splinetool/react-spline';

export default function Hero() {
  return (
    <div style={{ width: '100%', height: '600px' }}>
      <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
    </div>
  );
}
```

**Key Points**:
- Scene URL comes from Spline export dialog
- Component fills parent container
- Automatically handles loading and rendering

### Pattern 2: Event Handling and Object Interaction

**Use Case**: Respond to user clicks on specific objects

**Implementation**:

```jsx
import Spline from '@splinetool/react-spline';

export default function InteractiveScene() {
  function onSplineMouseDown(e) {
    // Check if clicked object is the button
    if (e.target.name === 'Button') {
      console.log('Button clicked!');

      // Get object properties
      console.log('Position:', e.target.position);
      console.log('Rotation:', e.target.rotation);
      console.log('Scale:', e.target.scale);
    }
  }

  function onSplineMouseHover(e) {
    if (e.target.name === 'Button') {
      console.log('Hovering over button');
    }
  }

  return (
    <Spline
      scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
      onSplineMouseDown={onSplineMouseDown}
      onSplineMouseHover={onSplineMouseHover}
    />
  );
}
```

**Available Event Handlers**:
- `onSplineMouseDown` - Mouse press on object
- `onSplineMouseUp` - Mouse release
- `onSplineMouseHover` - Mouse over object
- `onSplineKeyDown` - Keyboard press
- `onSplineKeyUp` - Keyboard release
- `onSplineStart` - Scene loaded and started
- `onSplineLookAt` - Camera look-at event
- `onSplineFollow` - Camera follow event
- `onSplineScroll` - Scroll event

### Pattern 3: Programmatic Object Control

**Use Case**: Modify object properties from React code

**Implementation**:

```jsx
import { useRef } from 'react';
import Spline from '@splinetool/react-spline';

export default function ProductViewer() {
  const cube = useRef();
  const splineApp = useRef();

  function onLoad(spline) {
    // Save Spline instance
    splineApp.current = spline;

    // Find object by name
    const obj = spline.findObjectByName('Product');
    // Or by ID
    // const obj = spline.findObjectById('8E8C2DDD-18B6-4C54-861D-7ED2519DE20E');

    cube.current = obj;
  }

  function rotateProduct() {
    if (cube.current) {
      // Rotate 45 degrees around Y axis
      cube.current.rotation.y += Math.PI / 4;
    }
  }

  function changeColor() {
    if (cube.current) {
      // Change material color (hex color)
      cube.current.material.color.set(0xff6b6b);
    }
  }

  function moveProduct() {
    if (cube.current) {
      cube.current.position.x += 50;
      cube.current.position.y += 10;
    }
  }

  return (
    <div>
      <Spline
        scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
        onLoad={onLoad}
      />
      <div style={{ position: 'absolute', top: 20, left: 20 }}>
        <button onClick={rotateProduct}>Rotate</button>
        <button onClick={changeColor}>Change Color</button>
        <button onClick={moveProduct}>Move</button>
      </div>
    </div>
  );
}
```

**Object Properties You Can Modify**:
- `position` - { x, y, z }
- `rotation` - { x, y, z } (radians)
- `scale` - { x, y, z }
- `material.color` - Color hex value
- `visible` - Boolean

### Pattern 4: Triggering Spline Animations

**Use Case**: Trigger animations defined in Spline from React

**Implementation**:

```jsx
import { useRef } from 'react';
import Spline from '@splinetool/react-spline';

export default function AnimatedCard() {
  const splineApp = useRef();

  function onLoad(app) {
    splineApp.current = app;
  }

  function triggerHoverAnimation() {
    // Emit mouseHover event on 'Card' object
    splineApp.current.emitEvent('mouseHover', 'Card');
  }

  function triggerClickAnimation() {
    // Emit mouseDown event on 'Button' object
    splineApp.current.emitEvent('mouseDown', 'Button');
  }

  function reverseAnimation() {
    // Play animation in reverse
    splineApp.current.emitEventReverse('mouseHover', 'Card');
  }

  return (
    <div>
      <Spline
        scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
        onLoad={onLoad}
      />
      <button onClick={triggerHoverAnimation}>Hover Effect</button>
      <button onClick={triggerClickAnimation}>Click Effect</button>
      <button onClick={reverseAnimation}>Reverse</button>
    </div>
  );
}
```

**Available Event Types**:
- `mouseDown` - Mouse press
- `mouseHover` - Hover effect
- `mouseUp` - Mouse release
- `keyDown` - Key press
- `keyUp` - Key release
- `start` - Start event
- `lookAt` - Look at camera
- `follow` - Follow camera

### Pattern 5: Next.js Integration with SSR

**Use Case**: Use Spline in Next.js with server-side rendering benefits

**Implementation**:

```jsx
// app/page.js (Next.js 13+ App Router)
import Spline from '@splinetool/react-spline/next';

export default function Home() {
  return (
    <main>
      <div style={{ width: '100vw', height: '100vh' }}>
        <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
      </div>
    </main>
  );
}
```

**Benefits**:
- Placeholder image shown during SSR
- Faster perceived load times
- Better SEO with fallback content

### Pattern 6: Lazy Loading for Performance

**Use Case**: Defer Spline loading until needed

**Implementation**:

```jsx
import React, { Suspense } from 'react';

// Dynamically import Spline
const Spline = React.lazy(() => import('@splinetool/react-spline'));

export default function LazyScene() {
  return (
    <div>
      <h1>My Page Content</h1>

      <Suspense fallback={<div>Loading 3D scene...</div>}>
        <div style={{ width: '100%', height: '500px' }}>
          <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
        </div>
      </Suspense>

      <p>More content below</p>
    </div>
  );
}
```

**Benefits**:
- Reduces initial bundle size
- Improves page load performance
- Shows custom loading UI

### Pattern 7: Responsive Spline Scenes

**Use Case**: Make Spline scenes adapt to different screen sizes

**Implementation**:

```jsx
import Spline from '@splinetool/react-spline';
import { useState, useEffect } from 'react';

export default function ResponsiveScene() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div style={{
      width: '100%',
      height: isMobile ? '400px' : '600px'
    }}>
      <Spline
        scene={
          isMobile
            ? "https://prod.spline.design/YOUR-MOBILE-SCENE/scene.splinecode"
            : "https://prod.spline.design/YOUR-DESKTOP-SCENE/scene.splinecode"
        }
      />
    </div>
  );
}
```

**Alternative Approach** (Single Scene):

```jsx
import Spline from '@splinetool/react-spline';
import { useRef, useEffect } from 'react';

export default function ResponsiveScene() {
  const splineApp = useRef();

  function onLoad(app) {
    splineApp.current = app;
    adjustForScreenSize();
  }

  function adjustForScreenSize() {
    if (!splineApp.current) return;

    const camera = splineApp.current.findObjectByName('Camera');
    const isMobile = window.innerWidth < 768;

    if (isMobile) {
      // Zoom out on mobile
      splineApp.current.setZoom(0.7);
      // Adjust camera position
      camera.position.z = 1500;
    }
  }

  useEffect(() => {
    window.addEventListener('resize', adjustForScreenSize);
    return () => window.removeEventListener('resize', adjustForScreenSize);
  }, []);

  return (
    <Spline
      scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
      onLoad={onLoad}
    />
  );
}
```

## Integration Patterns

### With Three.js (threejs-webgl)

For advanced use cases, combine Spline-designed assets with Three.js code:

1. **Export from Spline**: Use GLTF/GLB export
2. **Import in Three.js**: Load using GLTFLoader
3. **Enhance with code**: Add custom shaders, physics, or effects

```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const loader = new GLTFLoader();
loader.load('spline-model.glb', (gltf) => {
  scene.add(gltf.scene);
  // Add custom behaviors
});
```

### With GSAP (gsap-scrolltrigger)

Trigger Spline animations on scroll:

```jsx
import { useEffect, useRef } from 'react';
import Spline from '@splinetool/react-spline';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default function ScrollAnimated() {
  const splineApp = useRef();

  function onLoad(app) {
    splineApp.current = app;

    ScrollTrigger.create({
      trigger: '.scene-container',
      start: 'top center',
      onEnter: () => {
        app.emitEvent('mouseHover', 'Product');
      }
    });
  }

  return (
    <div className="scene-container">
      <Spline
        scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
        onLoad={onLoad}
      />
    </div>
  );
}
```

### With Framer Motion (motion-framer)

Animate container while Spline handles 3D:

```jsx
import { motion } from 'framer-motion';
import Spline from '@splinetool/react-spline';

export default function AnimatedContainer() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      style={{ width: '100%', height: '600px' }}
    >
      <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
    </motion.div>
  );
}
```

## Performance Optimization

### 1. Enable On-Demand Rendering

Render only when scene changes, not every frame:

```jsx
<Spline
  scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
  renderOnDemand={true} // Default is true
/>
```

### 2. Optimize Scene in Spline Editor

**In Spline**:
- Reduce polygon count (use decimation)
- Compress textures (lower resolution, use JPG over PNG)
- Limit lights (2-3 lights maximum)
- Use simple materials when possible
- Enable LOD (Level of Detail) for distant objects

### 3. Lazy Load Heavy Scenes

Use React.lazy() as shown in Pattern 6

### 4. Preload Critical Scenes

```jsx
import { useEffect } from 'react';
import Spline from '@splinetool/react-spline';

export default function PreloadedScene() {
  useEffect(() => {
    // Preload scene assets
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = 'https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode';
    document.head.appendChild(link);
  }, []);

  return (
    <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
  );
}
```

### 5. Mobile Optimizations

- Create separate mobile scenes with lower detail
- Reduce canvas resolution on mobile
- Disable shadows and reflections
- Use simpler materials

```jsx
<Spline
  scene={isMobile ? mobileSceneUrl : desktopSceneUrl}
  style={{
    width: '100%',
    height: isMobile ? '300px' : '600px'
  }}
/>
```

## Common Pitfalls and Solutions

### Pitfall 1: Scene Not Loading

**Problem**: Spline component renders but scene doesn't appear

**Solutions**:
```jsx
// ❌ Wrong: Invalid scene URL
<Spline scene="my-scene.splinecode" />

// ✅ Correct: Full URL from Spline export
<Spline scene="https://prod.spline.design/KFonZGtsoUXP-qx7/scene.splinecode" />

// Check for errors
function onLoad(app) {
  console.log('Scene loaded successfully', app);
}

<Spline scene={sceneUrl} onLoad={onLoad} />
```

**Also Check**:
- Scene is published in Spline editor
- Network tab shows successful file downloads
- No CORS errors in console

### Pitfall 2: Object References Lost After Re-render

**Problem**: Object refs become undefined after component updates

**Solution**:
```jsx
// ❌ Wrong: Storing objects without proper refs
let myObject;

function onLoad(spline) {
  myObject = spline.findObjectByName('Cube'); // Lost on re-render
}

// ✅ Correct: Use React refs
const myObject = useRef();

function onLoad(spline) {
  myObject.current = spline.findObjectByName('Cube');
}
```

### Pitfall 3: Performance Issues on Mobile

**Problem**: Scene runs slowly on mobile devices

**Solutions**:
```jsx
// Create mobile-optimized version in Spline editor
// - Fewer polygons (< 50k triangles)
// - Smaller textures (512x512 or less)
// - No shadows or reflections
// - Simpler materials

// Load appropriate version
const isMobile = window.innerWidth < 768;
const sceneUrl = isMobile
  ? 'https://prod.spline.design/MOBILE-SCENE/scene.splinecode'
  : 'https://prod.spline.design/DESKTOP-SCENE/scene.splinecode';

<Spline scene={sceneUrl} renderOnDemand={true} />
```

### Pitfall 4: Events Not Firing

**Problem**: Click or hover events don't trigger

**Solutions**:
```jsx
// ❌ Wrong: Using wrong event name
<Spline onMouseDown={handler} /> // Not a Spline prop

// ✅ Correct: Use Spline event props
<Spline onSplineMouseDown={handler} />

// Also ensure object has events in Spline editor:
// 1. Select object in Spline
// 2. Add event in "Events" panel
// 3. Assign state transition or action
```

### Pitfall 5: Animation Not Triggering Programmatically

**Problem**: `emitEvent()` doesn't trigger animation

**Solutions**:
```jsx
// ❌ Wrong: Calling before scene loads
function triggerAnimation() {
  splineApp.current.emitEvent('mouseHover', 'Button'); // Error if not loaded
}

// ✅ Correct: Ensure scene is loaded
const [isLoaded, setIsLoaded] = useState(false);

function onLoad(app) {
  splineApp.current = app;
  setIsLoaded(true);
}

function triggerAnimation() {
  if (isLoaded && splineApp.current) {
    splineApp.current.emitEvent('mouseHover', 'Button');
  }
}

// Also verify in Spline editor:
// - Object has the correct name ('Button')
// - mouseHover event is configured
// - Event has action (state transition, etc.)
```

### Pitfall 6: Hydration Errors in Next.js

**Problem**: Mismatch between server and client render

**Solution**:
```jsx
// ❌ Wrong: Using standard import in Next.js
import Spline from '@splinetool/react-spline';

// ✅ Correct: Use Next.js-specific import
import Spline from '@splinetool/react-spline/next';

// Or use dynamic import with ssr: false
import dynamic from 'next/dynamic';

const Spline = dynamic(
  () => import('@splinetool/react-spline'),
  { ssr: false }
);
```

## Resources

### Official Documentation
- **Spline Docs**: https://docs.spline.design
- **React Spline GitHub**: https://github.com/splinetool/react-spline
- **Spline Community**: https://spline.community

### Spline Editor
- **Web App**: https://app.spline.design
- **Desktop App**: Available for macOS, Windows, Linux

### Learning Resources
- **Tutorials**: https://spline.design/tutorials
- **YouTube Channel**: Official Spline tutorials
- **Examples Gallery**: https://spline.design/community

### Export Formats
- React component (via `@splinetool/react-spline`)
- Vanilla JavaScript (Web Code API)
- GLTF/GLB (for Three.js, Babylon.js)
- USDZ (for Apple AR)
- STL (for 3D printing)
- Video/GIF (for marketing)

## Related Skills

- **threejs-webgl**: For code-first 3D development with more control
- **react-three-fiber**: For building 3D scenes with React and JSX
- **babylonjs-engine**: Alternative 3D engine with editor workflow
- **motion-framer**: For animating Spline containers and UI elements
- **gsap-scrolltrigger**: For scroll-driven Spline animations
- **figma-dev-mode**: For design-to-code workflow (similar visual approach)

## Scripts

This skill includes utility scripts:
- `project_generator.py` - Generate Spline + React starter projects
- `component_builder.py` - Build Spline component wrappers with events

Run scripts from the skill directory:
```bash
./scripts/project_generator.py
./scripts/component_builder.py
```

## Assets

Starter templates and examples:
- `starter_spline/` - Complete React + Spline template
- `examples/` - Real-world integration patterns



===== FILE: plugins/individual/spline-interactive/skills/spline-interactive/references/api_reference.md =====

# Spline React API Reference

Complete reference for `@splinetool/react-spline` and Spline Application API.

## Installation

```bash
npm install @splinetool/react-spline @splinetool/runtime
# or
yarn add @splinetool/react-spline @splinetool/runtime
```

## Spline Component

### Import

```jsx
// Standard React
import Spline from '@splinetool/react-spline';

// Next.js (with SSR support)
import Spline from '@splinetool/react-spline/next';
```

### Props

#### `scene` (required)
- **Type**: `string`
- **Description**: URL to the Spline scene file
- **Example**: `"https://prod.spline.design/6Wq1Q7YGyM-iab9i/scene.splinecode"`

#### `onLoad`
- **Type**: `(spline: Application) => void`
- **Description**: Called once the scene has loaded. Provides Spline Application instance
- **Example**:
  ```jsx
  function onLoad(spline) {
    console.log('Scene loaded', spline);
    const obj = spline.findObjectByName('Cube');
  }

  <Spline scene={sceneUrl} onLoad={onLoad} />
  ```

#### `renderOnDemand`
- **Type**: `boolean`
- **Default**: `true`
- **Description**: Enable on-demand rendering (only renders when scene changes)
- **Example**: `<Spline scene={sceneUrl} renderOnDemand={false} />`

#### `className`
- **Type**: `string`
- **Description**: CSS class name(s) for the canvas container
- **Example**: `<Spline scene={sceneUrl} className="my-scene" />`

#### `style`
- **Type**: `React.CSSProperties`
- **Description**: Inline CSS styles for the canvas container
- **Example**: `<Spline scene={sceneUrl} style={{ width: '100%', height: '600px' }} />`

#### `id`
- **Type**: `string`
- **Description**: HTML id attribute for the canvas element
- **Example**: `<Spline scene={sceneUrl} id="main-scene" />`

#### `ref`
- **Type**: `React.Ref<HTMLDivElement>`
- **Description**: React ref pointing to the container div element
- **Example**:
  ```jsx
  const containerRef = useRef();
  <Spline scene={sceneUrl} ref={containerRef} />
  ```

### Event Handler Props

#### `onSplineMouseDown`
- **Type**: `(e: SplineEvent) => void`
- **Description**: Fired when mouse button is pressed on an object
- **Event Object**:
  - `e.target` - The object that was clicked (contains name, id, position, rotation, scale)
  - `e.target.name` - Object name from Spline editor
  - `e.target.id` - Object UUID
- **Example**:
  ```jsx
  function onSplineMouseDown(e) {
    console.log('Clicked:', e.target.name);
    console.log('Position:', e.target.position);
  }
  ```

#### `onSplineMouseUp`
- **Type**: `(e: SplineEvent) => void`
- **Description**: Fired when mouse button is released
- **Example**:
  ```jsx
  function onSplineMouseUp(e) {
    console.log('Released:', e.target.name);
  }
  ```

#### `onSplineMouseHover`
- **Type**: `(e: SplineEvent) => void`
- **Description**: Fired when mouse hovers over an object
- **Example**:
  ```jsx
  function onSplineMouseHover(e) {
    console.log('Hovering:', e.target.name);
  }
  ```

#### `onSplineKeyDown`
- **Type**: `(e: SplineEvent) => void`
- **Description**: Fired when a keyboard key is pressed
- **Example**:
  ```jsx
  function onSplineKeyDown(e) {
    console.log('Key pressed:', e.key);
  }
  ```

#### `onSplineKeyUp`
- **Type**: `(e: SplineEvent) => void`
- **Description**: Fired when a keyboard key is released

#### `onSplineStart`
- **Type**: `(e: SplineEvent) => void`
- **Description**: Fired when the scene starts (after loading)

#### `onSplineLookAt`
- **Type**: `(e: SplineEvent) => void`
- **Description**: Fired when a camera look-at event occurs

#### `onSplineFollow`
- **Type**: `(e: SplineEvent) => void`
- **Description**: Fired when a camera follow event occurs

#### `onSplineScroll`
- **Type**: `(e: SplineEvent) => void`
- **Description**: Fired when a scroll event occurs in the scene

## Spline Application API

The `Application` object is provided via the `onLoad` callback.

### Methods

#### `emitEvent(eventName, nameOrUuid)`
- **Description**: Triggers a Spline event on an object
- **Parameters**:
  - `eventName` (SplineEventName) - The event to trigger
  - `nameOrUuid` (string) - Object name or UUID
- **Returns**: `void`
- **Example**:
  ```jsx
  spline.emitEvent('mouseHover', 'Button');
  spline.emitEvent('mouseDown', '8E8C2DDD-18B6-4C54-861D-7ED2519DE20E');
  ```

#### `emitEventReverse(eventName, nameOrUuid)`
- **Description**: Triggers a Spline event in reverse (from last state to first)
- **Parameters**:
  - `eventName` (SplineEventName) - The event to trigger
  - `nameOrUuid` (string) - Object name or UUID
- **Returns**: `void`
- **Example**:
  ```jsx
  spline.emitEventReverse('mouseHover', 'Card');
  ```

#### `findObjectById(uuid)`
- **Description**: Finds an object by its UUID
- **Parameters**:
  - `uuid` (string) - Object UUID from Spline editor
- **Returns**: `SPEObject` - The object if found, undefined otherwise
- **Example**:
  ```jsx
  const obj = spline.findObjectById('8E8C2DDD-18B6-4C54-861D-7ED2519DE20E');
  console.log(obj.name, obj.position);
  ```

#### `findObjectByName(name)`
- **Description**: Finds the first object matching the specified name
- **Parameters**:
  - `name` (string) - Object name from Spline editor
- **Returns**: `SPEObject` - The object if found, undefined otherwise
- **Example**:
  ```jsx
  const cube = spline.findObjectByName('Cube');
  cube.position.x += 10;
  ```

#### `setZoom(zoom)`
- **Description**: Sets the camera zoom level
- **Parameters**:
  - `zoom` (number) - Zoom value (1.0 is default, <1.0 zooms out, >1.0 zooms in)
- **Returns**: `void`
- **Example**:
  ```jsx
  spline.setZoom(1.5); // Zoom in
  spline.setZoom(0.7); // Zoom out
  ```

## SplineEventName Type

Available event types for `emitEvent()` and `emitEventReverse()`:

- `'mouseDown'` - Mouse button pressed
- `'mouseHover'` - Mouse hover
- `'mouseUp'` - Mouse button released
- `'keyDown'` - Keyboard key pressed
- `'keyUp'` - Keyboard key released
- `'start'` - Scene start event
- `'lookAt'` - Camera look-at event
- `'follow'` - Camera follow event

## SPEObject Interface

Objects returned by `findObjectById()` and `findObjectByName()` have the following properties:

### Properties

#### `name`
- **Type**: `string`
- **Description**: Object name from Spline editor
- **Example**: `'Cube'`, `'Button'`, `'Product'`

#### `id`
- **Type**: `string`
- **Description**: Object UUID
- **Example**: `'8E8C2DDD-18B6-4C54-861D-7ED2519DE20E'`

#### `position`
- **Type**: `{ x: number, y: number, z: number }`
- **Description**: Object position in 3D space
- **Mutable**: Yes
- **Example**:
  ```jsx
  console.log(obj.position); // { x: 0, y: 100, z: 50 }
  obj.position.x += 10;
  obj.position.y = 200;
  ```

#### `rotation`
- **Type**: `{ x: number, y: number, z: number }`
- **Description**: Object rotation in radians
- **Mutable**: Yes
- **Example**:
  ```jsx
  obj.rotation.y += Math.PI / 4; // Rotate 45 degrees
  obj.rotation.x = Math.PI / 2; // Rotate 90 degrees
  ```

#### `scale`
- **Type**: `{ x: number, y: number, z: number }`
- **Description**: Object scale multiplier
- **Mutable**: Yes
- **Example**:
  ```jsx
  obj.scale.x = 2; // Scale to 2x width
  obj.scale.y = 0.5; // Scale to half height
  obj.scale.z = 1.5;
  ```

#### `material`
- **Type**: `Material`
- **Description**: Object material properties
- **Properties**:
  - `color` - Material color (use `.set()` method)
- **Example**:
  ```jsx
  // Set color using hex value
  obj.material.color.set(0xff6b6b); // Red
  obj.material.color.set(0x4ecdc4); // Cyan
  obj.material.color.set(0xffe66d); // Yellow
  ```

#### `visible`
- **Type**: `boolean`
- **Description**: Object visibility
- **Mutable**: Yes
- **Example**:
  ```jsx
  obj.visible = false; // Hide object
  obj.visible = true;  // Show object
  ```

### Methods

#### `emitEvent(eventName)`
- **Description**: Triggers an event on this specific object
- **Parameters**:
  - `eventName` (SplineEventName) - The event to trigger
- **Returns**: `void`
- **Example**:
  ```jsx
  const button = spline.findObjectByName('Button');
  button.emitEvent('mouseHover'); // Trigger hover animation
  ```

## SplineEvent Interface

Event object passed to event handler callbacks:

### Properties

#### `target`
- **Type**: `SPEObject`
- **Description**: The object that triggered the event
- **Example**:
  ```jsx
  function onSplineMouseDown(e) {
    console.log('Clicked object:', e.target.name);
    console.log('Object ID:', e.target.id);
    console.log('Position:', e.target.position);
  }
  ```

#### `type`
- **Type**: `string`
- **Description**: Event type name
- **Values**: `'mouseDown'`, `'mouseUp'`, `'mouseHover'`, etc.

## Usage Examples

### Complete Component Example

```jsx
import { useRef, useState } from 'react';
import Spline from '@splinetool/react-spline';

export default function InteractiveScene() {
  const splineApp = useRef();
  const [isLoaded, setIsLoaded] = useState(false);

  function onLoad(spline) {
    splineApp.current = spline;
    setIsLoaded(true);
    console.log('Scene loaded');
  }

  function onSplineMouseDown(e) {
    console.log('Clicked:', e.target.name);

    if (e.target.name === 'Button') {
      // Trigger animation
      splineApp.current.emitEvent('mouseHover', 'Card');
    }
  }

  function rotateAllObjects() {
    if (!isLoaded) return;

    const cube = splineApp.current.findObjectByName('Cube');
    const sphere = splineApp.current.findObjectByName('Sphere');

    if (cube) cube.rotation.y += Math.PI / 4;
    if (sphere) sphere.rotation.x += Math.PI / 4;
  }

  return (
    <div>
      <Spline
        scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
        onLoad={onLoad}
        onSplineMouseDown={onSplineMouseDown}
        style={{ width: '100%', height: '600px' }}
      />

      {isLoaded && (
        <button onClick={rotateAllObjects}>
          Rotate Objects
        </button>
      )}
    </div>
  );
}
```

### Next.js Example

```jsx
// app/components/SplineScene.jsx
'use client';

import Spline from '@splinetool/react-spline/next';

export default function SplineScene() {
  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
    </div>
  );
}
```

### Lazy Loading Example

```jsx
import React, { Suspense } from 'react';

const Spline = React.lazy(() => import('@splinetool/react-spline'));

export default function LazyScene() {
  return (
    <Suspense fallback={<div>Loading 3D scene...</div>}>
      <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
    </Suspense>
  );
}
```

## Color Reference

Common hex color values for `material.color.set()`:

```javascript
// Red tones
0xff0000  // Pure red
0xff6b6b  // Coral red
0xe74c3c  // Soft red

// Blue tones
0x0000ff  // Pure blue
0x3498db  // Sky blue
0x2c3e50  // Dark blue

// Green tones
0x00ff00  // Pure green
0x2ecc71  // Emerald green
0x27ae60  // Dark green

// Yellow/Orange
0xffff00  // Pure yellow
0xffe66d  // Soft yellow
0xf39c12  // Orange

// Purple/Pink
0x9b59b6  // Purple
0xe91e63  // Pink
0xff69b4  // Hot pink

// Cyan/Teal
0x00ffff  // Pure cyan
0x4ecdc4  // Teal
0x1abc9c  // Turquoise

// Grayscale
0xffffff  // White
0xcccccc  // Light gray
0x95a5a6  // Gray
0x7f8c8d  // Dark gray
0x000000  // Black
```

## Math Helpers

Common rotation values (radians):

```javascript
Math.PI / 6   // 30 degrees
Math.PI / 4   // 45 degrees
Math.PI / 3   // 60 degrees
Math.PI / 2   // 90 degrees
Math.PI       // 180 degrees
Math.PI * 2   // 360 degrees

// Convert degrees to radians
const radians = (degrees * Math.PI) / 180;

// Convert radians to degrees
const degrees = (radians * 180) / Math.PI;
```

## Troubleshooting

### Scene Not Loading
- Verify scene URL is correct and complete
- Check that scene is published in Spline editor
- Look for CORS errors in console
- Ensure `@splinetool/runtime` is installed

### Events Not Firing
- Use `onSplineMouseDown` not `onMouseDown`
- Verify object has events configured in Spline editor
- Check object name matches exactly

### Object Not Found
- Verify object name in Spline editor matches exactly (case-sensitive)
- Check that `onLoad` has been called before finding objects
- Use `findObjectById` if name changes frequently

### Performance Issues
- Enable `renderOnDemand={true}`
- Reduce polygon count in Spline editor
- Compress textures
- Create mobile-specific scenes
- Use lazy loading for heavy scenes

## TypeScript Support

```typescript
import { Application, SPEObject, SplineEvent } from '@splinetool/runtime';
import Spline from '@splinetool/react-spline';

interface Props {
  sceneUrl: string;
}

export default function MyScene({ sceneUrl }: Props) {
  const splineApp = useRef<Application | null>(null);

  function onLoad(app: Application): void {
    splineApp.current = app;
  }

  function onSplineMouseDown(e: SplineEvent): void {
    const target: SPEObject = e.target;
    console.log(target.name);
  }

  return (
    <Spline
      scene={sceneUrl}
      onLoad={onLoad}
      onSplineMouseDown={onSplineMouseDown}
    />
  );
}
```



===== FILE: plugins/individual/spline-interactive/agents/spline-interactive-pipeline.md =====

# Spline Pipeline Specialist

## Role

Expert pipeline specialist for Spline workflows, asset optimization, and web integration.

## Expertise

- Asset export and optimization
- Web-ready format conversion
- Texture and material optimization
- Automated pipeline workflows
- Quality assurance and validation
- Cross-platform compatibility

## When to use

Activate this agent when working on:
- Asset export pipelines
- Batch processing workflows
- Optimization for web delivery
- Integration with web frameworks
- Automated quality checks

## Approach

1. Analyze asset requirements and constraints
2. Design optimal export pipeline
3. Implement automation scripts
4. Optimize for web performance
5. Validate output quality

## Tools

This agent has access to:
- Spline skill knowledge
- Pipeline automation scripts
- Optimization guidelines
- Quality validation checklists



===== FILE: plugins/individual/spline-interactive/commands/component_builder.md =====

# /spline-interactive-component_builder

Spline - Component Builder

## Description

Executes the component_builder script for Spline.

## Usage

```bash
/spline-interactive-component_builder
```

## Implementation

This command runs the `component_builder.py` script from the Spline skill, which provides automated assistance for component builder.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/spline-interactive/commands/project_generator.md =====

# /spline-interactive-project_generator

Spline - Project Generator

## Description

Executes the project_generator script for Spline.

## Usage

```bash
/spline-interactive-project_generator
```

## Implementation

This command runs the `project_generator.py` script from the Spline skill, which provides automated assistance for project generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/spline-interactive/skills/spline-interactive/scripts/component_builder.py =====

```py
#!/usr/bin/env python3
"""
Spline Component Wrapper Generator

Generates reusable Spline component wrappers with event handling.

Usage:
    ./component_builder.py                        # Interactive mode
    ./component_builder.py --name ProductViewer   # CLI mode
"""

import argparse
import sys
from pathlib import Path


COMPONENT_TEMPLATES = {
    'basic': '''import Spline from '@splinetool/react-spline';

export default function {name}({{ sceneUrl }}) {{
  return (
    <div style={{{{ width: '100%', height: '600px' }}}}>
      <Spline scene={{sceneUrl}} />
    </div>
  );
}}
''',

    'interactive': '''import {{ useRef, useState }} from 'react';
import Spline from '@splinetool/react-spline';

export default function {name}({{ sceneUrl, onObjectClick }}) {{
  const splineApp = useRef();
  const [isLoaded, setIsLoaded] = useState(false);

  function onLoad(spline) {{
    splineApp.current = spline;
    setIsLoaded(true);
  }}

  function onSplineMouseDown(e) {{
    console.log('Clicked:', e.target.name);
    if (onObjectClick) {{
      onObjectClick(e.target);
    }}
  }}

  return (
    <Spline
      scene={{sceneUrl}}
      onLoad={{onLoad}}
      onSplineMouseDown={{onSplineMouseDown}}
    />
  );
}}
''',

    'animated': '''import {{ useRef }} from 'react';
import Spline from '@splinetool/react-spline';

export default function {name}({{ sceneUrl, animationTrigger }}) {{
  const splineApp = useRef();

  function onLoad(spline) {{
    splineApp.current = spline;
  }}

  // Expose animation controls
  const triggerAnimation = (objectName, eventType = 'mouseHover') => {{
    if (splineApp.current) {{
      splineApp.current.emitEvent(eventType, objectName);
    }}
  }};

  const reverseAnimation = (objectName, eventType = 'mouseHover') => {{
    if (splineApp.current) {{
      splineApp.current.emitEventReverse(eventType, objectName);
    }}
  }};

  return (
    <Spline
      scene={{sceneUrl}}
      onLoad={{onLoad}}
    />
  );
}}
''',

    'controlled': '''import {{ useRef, useImperativeHandle, forwardRef }} from 'react';
import Spline from '@splinetool/react-spline';

const {name} = forwardRef(({{ sceneUrl }}, ref) => {{
  const splineApp = useRef();

  function onLoad(spline) {{
    splineApp.current = spline;
  }}

  // Expose methods to parent component
  useImperativeHandle(ref, () => ({{
    findObject: (name) => {{
      return splineApp.current?.findObjectByName(name);
    }},
    emitEvent: (eventName, objectName) => {{
      splineApp.current?.emitEvent(eventName, objectName);
    }},
    setZoom: (zoom) => {{
      splineApp.current?.setZoom(zoom);
    }},
    getApp: () => splineApp.current
  }}));

  return (
    <Spline
      scene={{sceneUrl}}
      onLoad={{onLoad}}
    />
  );
}});

export default {name};
''',

    'responsive': '''import {{ useRef, useEffect, useState }} from 'react';
import Spline from '@splinetool/react-spline';

export default function {name}({{ mobileSceneUrl, desktopSceneUrl }}) {{
  const splineApp = useRef();
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {{
    const checkMobile = () => {{
      setIsMobile(window.innerWidth < 768);
    }};

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }}, []);

  function onLoad(spline) {{
    splineApp.current = spline;

    // Adjust for mobile
    if (isMobile) {{
      spline.setZoom(0.7);
    }}
  }}

  const sceneUrl = isMobile ? mobileSceneUrl : desktopSceneUrl;

  return (
    <div style={{{{
      width: '100%',
      height: isMobile ? '400px' : '600px'
    }}}}>
      <Spline
        scene={{sceneUrl}}
        onLoad={{onLoad}}
      />
    </div>
  );
}}
''',

    'lazy': '''import React, {{ Suspense }} from 'react';

const Spline = React.lazy(() => import('@splinetool/react-spline'));

export default function {name}({{ sceneUrl, fallback }}) {{
  return (
    <Suspense fallback={{fallback || <div>Loading 3D scene...</div>}}>
      <div style={{{{ width: '100%', height: '600px' }}}}>
        <Spline scene={{sceneUrl}} />
      </div>
    </Suspense>
  );
}}
'''
}


def generate_component(name, component_type, output_path=None):
    """Generate component code"""

    if component_type not in COMPONENT_TEMPLATES:
        print(f"❌ Unknown component type: {component_type}")
        print(f"Available types: {', '.join(COMPONENT_TEMPLATES.keys())}")
        sys.exit(1)

    template = COMPONENT_TEMPLATES[component_type]
    code = template.format(name=name)

    # Output to file or stdout
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(code)
        print(f"✅ Component created: {output_file}")
    else:
        print("\n" + "=" * 60)
        print(f"// {name}.jsx")
        print("=" * 60)
        print(code)
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Generate Spline component wrappers'
    )
    parser.add_argument(
        '--name',
        type=str,
        help='Component name (e.g., ProductViewer)'
    )
    parser.add_argument(
        '--type',
        type=str,
        choices=list(COMPONENT_TEMPLATES.keys()),
        help='Component type'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: print to stdout)'
    )

    args = parser.parse_args()

    # Interactive mode
    if not args.name or not args.type:
        print("🎨 Spline Component Builder\n")

        if not args.name:
            name = input("Component name (e.g., ProductViewer): ").strip()
            if not name:
                print("❌ Component name is required")
                sys.exit(1)
        else:
            name = args.name

        if not args.type:
            print("\nComponent types:")
            for i, comp_type in enumerate(COMPONENT_TEMPLATES.keys(), 1):
                print(f"  {i}. {comp_type}")

            choice = input("\nSelect type (1-6): ").strip()
            try:
                comp_type = list(COMPONENT_TEMPLATES.keys())[int(choice) - 1]
            except (ValueError, IndexError):
                print("❌ Invalid choice")
                sys.exit(1)
        else:
            comp_type = args.type

        output_path = args.output
    else:
        name = args.name
        comp_type = args.type
        output_path = args.output

    # Generate component
    generate_component(name, comp_type, output_path)


if __name__ == '__main__':
    main()

```


===== FILE: plugins/individual/spline-interactive/skills/spline-interactive/scripts/project_generator.py =====

````py
#!/usr/bin/env python3
"""
Spline + React Project Generator

Generates boilerplate React projects with Spline integration.

Usage:
    ./project_generator.py                    # Interactive mode
    ./project_generator.py --name my-project  # CLI mode
"""

import argparse
import json
import os
import sys
from pathlib import Path


def create_project_structure(project_name, include_nextjs=False):
    """Create complete project structure with all necessary files"""

    base_path = Path(project_name)

    # Create directories
    directories = [
        base_path,
        base_path / 'src',
        base_path / 'public',
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    # package.json
    package_json = {
        "name": project_name,
        "version": "0.1.0",
        "private": True,
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "@splinetool/react-spline": "^2.2.6",
            "@splinetool/runtime": "^0.9.508"
        },
        "devDependencies": {
            "@vitejs/plugin-react": "^4.0.0",
            "vite": "^4.3.9"
        },
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        }
    }

    if include_nextjs:
        package_json["dependencies"]["next"] = "^14.0.0"
        package_json["scripts"] = {
            "dev": "next dev",
            "build": "next build",
            "start": "next start"
        }

    with open(base_path / 'package.json', 'w') as f:
        json.dump(package_json, f, indent=2)

    # vite.config.js (if not Next.js)
    if not include_nextjs:
        vite_config = """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000
  }
});
"""
        with open(base_path / 'vite.config.js', 'w') as f:
            f.write(vite_config)

    # index.html (if not Next.js)
    if not include_nextjs:
        index_html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Spline React App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""
        with open(base_path / 'index.html', 'w') as f:
            f.write(index_html)

    # src/main.jsx (if not Next.js)
    if not include_nextjs:
        main_jsx = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './App.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        with open(base_path / 'src' / 'main.jsx', 'w') as f:
            f.write(main_jsx)

    # src/App.jsx or app/page.jsx
    if include_nextjs:
        app_dir = base_path / 'app'
        app_dir.mkdir(exist_ok=True)

        page_jsx = """'use client';

import Spline from '@splinetool/react-spline/next';
import { useRef } from 'react';

export default function Home() {
  const splineApp = useRef();

  function onLoad(spline) {
    splineApp.current = spline;
    console.log('Spline scene loaded');
  }

  function onSplineMouseDown(e) {
    console.log('Clicked:', e.target.name);
  }

  return (
    <main style={{ width: '100vw', height: '100vh' }}>
      <Spline
        scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
        onLoad={onLoad}
        onSplineMouseDown={onSplineMouseDown}
      />
    </main>
  );
}
"""
        with open(app_dir / 'page.jsx', 'w') as f:
            f.write(page_jsx)
    else:
        app_jsx = """import { useRef, useState } from 'react';
import Spline from '@splinetool/react-spline';

export default function App() {
  const splineApp = useRef();
  const [isLoaded, setIsLoaded] = useState(false);

  function onLoad(spline) {
    splineApp.current = spline;
    setIsLoaded(true);
    console.log('Spline scene loaded');
  }

  function onSplineMouseDown(e) {
    console.log('Clicked:', e.target.name);

    if (e.target.name === 'Button') {
      splineApp.current.emitEvent('mouseHover', 'Card');
    }
  }

  return (
    <div className="app">
      <div className="scene-container">
        <Spline
          scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
          onLoad={onLoad}
          onSplineMouseDown={onSplineMouseDown}
        />
      </div>

      {isLoaded && (
        <div className="controls">
          <button onClick={() => splineApp.current.setZoom(1.5)}>
            Zoom In
          </button>
          <button onClick={() => splineApp.current.setZoom(0.7)}>
            Zoom Out
          </button>
        </div>
      )}
    </div>
  );
}
"""
        with open(base_path / 'src' / 'App.jsx', 'w') as f:
            f.write(app_jsx)

    # CSS
    if not include_nextjs:
        app_css = """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app {
  width: 100vw;
  height: 100vh;
  position: relative;
}

.scene-container {
  width: 100%;
  height: 100%;
}

.controls {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  gap: 10px;
  z-index: 10;
}

button {
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

button:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

button:active {
  transform: scale(0.98);
}
"""
        with open(base_path / 'src' / 'App.css', 'w') as f:
            f.write(app_css)

    # README.md
    readme = f"""# {project_name}

Spline + React project

## Setup

```bash
npm install
```

## Development

```bash
npm run dev
```

Visit http://localhost:3000

## Update Scene URL

Replace `YOUR-SCENE-ID` in the code with your actual Spline scene ID.

Get your scene URL from Spline:
1. Open your scene in Spline editor
2. Click "Export" button
3. Select "Code Export" > "React"
4. Copy the scene URL

## Build

```bash
npm run build
```

## Learn More

- [Spline Documentation](https://docs.spline.design)
- [React Spline GitHub](https://github.com/splinetool/react-spline)
"""
    with open(base_path / 'README.md', 'w') as f:
        f.write(readme)

    print(f"\n✅ Project '{project_name}' created successfully!")
    print(f"\nNext steps:")
    print(f"  cd {project_name}")
    print(f"  npm install")
    print(f"  npm run dev")
    print(f"\n📝 Don't forget to update the Spline scene URL!")


def main():
    parser = argparse.ArgumentParser(
        description='Generate Spline + React project boilerplate'
    )
    parser.add_argument(
        '--name',
        type=str,
        help='Project name'
    )
    parser.add_argument(
        '--nextjs',
        action='store_true',
        help='Use Next.js instead of Vite'
    )

    args = parser.parse_args()

    # Interactive mode
    if not args.name:
        print("🚀 Spline + React Project Generator\n")
        project_name = input("Project name: ").strip()

        if not project_name:
            print("❌ Project name is required")
            sys.exit(1)

        use_nextjs = input("Use Next.js? (y/N): ").strip().lower() == 'y'
    else:
        project_name = args.name
        use_nextjs = args.nextjs

    # Create project
    create_project_structure(project_name, use_nextjs)


if __name__ == '__main__':
    main()

````


===== FILE: plugins/individual/spline-interactive/skills/spline-interactive/assets/README.md =====

# Spline Interactive - Assets

This directory contains starter templates and examples for Spline + React integration.

## Using the Project Generator

The easiest way to get started is using the `project_generator.py` script:

```bash
# Interactive mode
./scripts/project_generator.py

# CLI mode
./scripts/project_generator.py --name my-spline-app

# Next.js project
./scripts/project_generator.py --name my-spline-app --nextjs
```

This automatically generates a complete project with:
- package.json with all dependencies
- Vite or Next.js configuration
- React components with Spline integration
- Example event handlers
- Starter CSS
- README with setup instructions

## Project Structure

Generated projects have this structure:

```
my-spline-app/
├── package.json
├── vite.config.js (or next.config.js)
├── index.html (Vite only)
├── README.md
├── src/
│   ├── main.jsx (Vite only)
│   ├── App.jsx
│   └── App.css
└── app/ (Next.js only)
    └── page.jsx
```

## Component Templates

Use `component_builder.py` to generate reusable Spline components:

```bash
# Interactive mode
./scripts/component_builder.py

# Generate specific component
./scripts/component_builder.py --name ProductViewer --type interactive

# Save to file
./scripts/component_builder.py --name ProductViewer --type interactive --output src/components/ProductViewer.jsx
```

### Available Component Types

1. **basic** - Simple Spline scene wrapper
2. **interactive** - With click/hover event handling
3. **animated** - With animation trigger methods
4. **controlled** - Exposes methods via ref for parent control
5. **responsive** - Adapts to mobile/desktop screen sizes
6. **lazy** - Lazy-loaded with React.lazy()

## Example Integrations

### With GSAP ScrollTrigger

```jsx
import { useRef, useEffect } from 'react';
import Spline from '@splinetool/react-spline';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default function ScrollSpline() {
  const splineApp = useRef();

  function onLoad(app) {
    splineApp.current = app;

    ScrollTrigger.create({
      trigger: '.scene',
      start: 'top center',
      onEnter: () => app.emitEvent('mouseHover', 'Product')
    });
  }

  return (
    <div className="scene">
      <Spline
        scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
        onLoad={onLoad}
      />
    </div>
  );
}
```

### With Framer Motion

```jsx
import { motion } from 'framer-motion';
import Spline from '@splinetool/react-spline';

export default function AnimatedSpline() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8 }}
      style={{ width: '100%', height: '600px' }}
    >
      <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
    </motion.div>
  );
}
```

### Product Configurator

```jsx
import { useRef, useState } from 'react';
import Spline from '@splinetool/react-spline';

export default function ProductConfigurator() {
  const product = useRef();
  const splineApp = useRef();
  const [color, setColor] = useState('#ff6b6b');

  function onLoad(spline) {
    splineApp.current = spline;
    product.current = spline.findObjectByName('Product');
  }

  function changeColor(newColor) {
    setColor(newColor);
    if (product.current) {
      product.current.material.color.set(parseInt(newColor.substring(1), 16));
    }
  }

  function rotate() {
    if (product.current) {
      product.current.rotation.y += Math.PI / 4;
    }
  }

  return (
    <div>
      <Spline
        scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
        onLoad={onLoad}
      />

      <div className="controls">
        <button onClick={() => changeColor('#ff6b6b')}>Red</button>
        <button onClick={() => changeColor('#4ecdc4')}>Cyan</button>
        <button onClick={() => changeColor('#ffe66d')}>Yellow</button>
        <button onClick={rotate}>Rotate</button>
      </div>
    </div>
  );
}
```

### Multi-Scene Viewer

```jsx
import { useState } from 'react';
import Spline from '@splinetool/react-spline';

const scenes = {
  scene1: 'https://prod.spline.design/SCENE-1/scene.splinecode',
  scene2: 'https://prod.spline.design/SCENE-2/scene.splinecode',
  scene3: 'https://prod.spline.design/SCENE-3/scene.splinecode'
};

export default function SceneSwitcher() {
  const [currentScene, setCurrentScene] = useState('scene1');

  return (
    <div>
      <Spline scene={scenes[currentScene]} />

      <div className="tabs">
        <button onClick={() => setCurrentScene('scene1')}>Scene 1</button>
        <button onClick={() => setCurrentScene('scene2')}>Scene 2</button>
        <button onClick={() => setCurrentScene('scene3')}>Scene 3</button>
      </div>
    </div>
  );
}
```

## Getting Your Spline Scene URL

1. Open your scene in Spline editor (https://app.spline.design)
2. Click the "Export" button (top right)
3. Select "Code Export" → "React"
4. Copy the scene URL (format: `https://prod.spline.design/[ID]/scene.splinecode`)
5. Replace `YOUR-SCENE-ID` in the templates with your actual scene URL

## Common Use Cases

### Marketing Hero Section

```jsx
import Spline from '@splinetool/react-spline';
import './Hero.css';

export default function Hero() {
  return (
    <section className="hero">
      <div className="hero-content">
        <h1>Welcome to Our Product</h1>
        <p>Experience 3D interaction</p>
        <button>Get Started</button>
      </div>

      <div className="hero-scene">
        <Spline scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode" />
      </div>
    </section>
  );
}
```

### Interactive Portfolio

```jsx
import { useRef } from 'react';
import Spline from '@splinetool/react-spline';

export default function Portfolio() {
  const splineApp = useRef();

  function showProject(projectName) {
    splineApp.current?.emitEvent('mouseHover', projectName);
  }

  return (
    <div className="portfolio">
      <nav>
        <button onClick={() => showProject('Project1')}>Project 1</button>
        <button onClick={() => showProject('Project2')}>Project 2</button>
        <button onClick={() => showProject('Project3')}>Project 3</button>
      </nav>

      <Spline
        scene="https://prod.spline.design/YOUR-SCENE-ID/scene.splinecode"
        onLoad={(app) => (splineApp.current = app)}
      />
    </div>
  );
}
```

## Performance Tips

1. **Use On-Demand Rendering** (enabled by default):
   ```jsx
   <Spline scene={sceneUrl} renderOnDemand={true} />
   ```

2. **Lazy Load Heavy Scenes**:
   ```jsx
   const Spline = React.lazy(() => import('@splinetool/react-spline'));
   ```

3. **Optimize in Spline Editor**:
   - Reduce polygon count
   - Compress textures
   - Limit lights to 2-3
   - Use simple materials

4. **Create Mobile Versions**:
   - Lower detail meshes
   - Smaller textures (512x512)
   - No shadows/reflections

## Troubleshooting

### Scene Not Loading
- Verify scene URL is complete and correct
- Check scene is published in Spline editor
- Look for CORS errors in browser console
- Ensure both `@splinetool/react-spline` and `@splinetool/runtime` are installed

### Events Not Working
- Use `onSplineMouseDown` not `onMouseDown`
- Verify objects have events configured in Spline editor
- Check object names match exactly (case-sensitive)

### Performance Issues
- Enable renderOnDemand
- Create mobile-specific scenes with lower detail
- Use lazy loading for heavy scenes
- Profile with Chrome DevTools

## Additional Resources

- [Spline Documentation](https://docs.spline.design)
- [React Spline GitHub](https://github.com/splinetool/react-spline)
- [Spline Community](https://spline.community)
- [Spline Tutorials](https://spline.design/tutorials)



# Skill: rive-interactive


===== FILE: plugins/individual/rive-interactive/skills/rive-interactive/SKILL.md =====

---
name: rive-interactive
description: State machine-based vector animation with runtime interactivity and web integration. Use this skill when creating interactive animations, state-driven UI, animated components with logic, or designer-created animations with runtime control. Triggers on tasks involving Rive, state machines, interactive vector animations, animation with input handling, ViewModel data binding, or React Rive integration. Alternative to Lottie for animations requiring state machines and two-way interactivity.
---

# Rive Interactive - State Machine-Based Vector Animation

## Overview

Rive is a state machine-based animation platform that enables designers to create interactive vector animations with complex logic and runtime interactivity. Unlike timeline-only animation tools (like Lottie), Rive supports state machines, input handling, and two-way data binding between application code and animations.

**Key Features**:
- State machine system for complex interactive logic
- ViewModel API for two-way data binding
- Input handling (boolean, number, trigger inputs)
- Custom events for animation-to-code communication
- Runtime property control (colors, strings, numbers, enums)
- Cross-platform support (Web, React, React Native, iOS, Android, Flutter)
- Small file sizes with vector graphics

**When to Use This Skill**:
- Creating UI animations with complex state transitions
- Building interactive animated components (buttons, toggles, loaders)
- Implementing game-like UI with state-driven animations
- Binding real-time data to animated visualizations
- Creating animations that respond to user input
- Working with designer-created animations requiring runtime control

**Alternatives**:
- **Lottie** (lottie-animations): For simpler timeline-based animations without state machines
- **Framer Motion** (motion-framer): For code-first React animations with spring physics
- **GSAP** (gsap-scrolltrigger): For timeline-based web animations with precise control

## Core Concepts

### 1. State Machines

State machines define animation behavior with states and transitions:
- **States**: Different animation states (e.g., idle, hover, pressed)
- **Inputs**: Variables that control transitions (boolean, number, trigger)
- **Transitions**: Rules for moving between states
- **Listeners**: React hooks to respond to state changes

### 2. Inputs

Three input types control state machine behavior:
- **Boolean**: On/off states (e.g., isHovered, isActive)
- **Number**: Numeric values (e.g., progress, volume)
- **Trigger**: One-time events (e.g., click, submit)

### 3. ViewModels

Data binding system for dynamic properties:
- **String Properties**: Text content (e.g., username, title)
- **Number Properties**: Numeric data (e.g., stock price, score)
- **Color Properties**: Dynamic colors (hex values)
- **Enum Properties**: Selection from predefined options
- **Trigger Properties**: Animation events

### 4. Events

Custom events emitted from animations:
- **General Events**: Custom named events
- **Event Properties**: Data attached to events
- **Event Listeners**: React hooks to handle events

## Common Patterns

### Pattern 1: Basic Rive Animation

**Use Case**: Display a simple Rive animation in React

**Implementation**:

```bash
# Installation
npm install rive-react
```

```jsx
import Rive from 'rive-react';

export default function SimpleAnimation() {
  return (
    <Rive
      src="animation.riv"
      artboard="Main"
      animations="idle"
      layout={{ fit: "contain", alignment: "center" }}
      style={{ width: '400px', height: '400px' }}
    />
  );
}
```

**Key Points**:
- `src`: Path to .riv file
- `artboard`: Which artboard to display
- `animations`: Which animation timeline to play
- `layout`: How animation fits in container

### Pattern 2: State Machine Control with Inputs

**Use Case**: Control animation states based on user interaction

**Implementation**:

```jsx
import { useRive, useStateMachineInput } from 'rive-react';

export default function InteractiveButton() {
  const { rive, RiveComponent } = useRive({
    src: 'button.riv',
    stateMachines: 'Button State Machine',
    autoplay: true,
  });

  // Get state machine inputs
  const hoverInput = useStateMachineInput(
    rive,
    'Button State Machine',
    'isHovered',
    false
  );

  const clickInput = useStateMachineInput(
    rive,
    'Button State Machine',
    'isClicked',
    false
  );

  return (
    <div
      onMouseEnter={() => hoverInput && (hoverInput.value = true)}
      onMouseLeave={() => hoverInput && (hoverInput.value = false)}
      onClick={() => clickInput && clickInput.fire()} // Trigger input
      style={{ cursor: 'pointer' }}
    >
      <RiveComponent style={{ width: '200px', height: '100px' }} />
    </div>
  );
}
```

**Input Types**:
- Boolean: `input.value = true/false`
- Number: `input.value = 50`
- Trigger: `input.fire()`

### Pattern 3: ViewModel Data Binding

**Use Case**: Bind application data to animation properties

**Implementation**:

```jsx
import { useRive, useViewModel, useViewModelInstance,
         useViewModelInstanceString, useViewModelInstanceNumber } from 'rive-react';
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [stockPrice, setStockPrice] = useState(150.0);

  const { rive, RiveComponent } = useRive({
    src: 'dashboard.riv',
    autoplay: true,
    autoBind: false, // Manual binding for ViewModels
  });

  // Get ViewModel and instance
  const viewModel = useViewModel(rive, { name: 'Dashboard' });
  const viewModelInstance = useViewModelInstance(viewModel, { rive });

  // Bind properties
  const { setValue: setTitle } = useViewModelInstanceString(
    'title',
    viewModelInstance
  );

  const { setValue: setPrice } = useViewModelInstanceNumber(
    'stockPrice',
    viewModelInstance
  );

  useEffect(() => {
    if (setTitle) setTitle('Stock Dashboard');
  }, [setTitle]);

  useEffect(() => {
    if (setPrice) setPrice(stockPrice);
  }, [setPrice, stockPrice]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setStockPrice((prev) => prev + (Math.random() - 0.5) * 10);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return <RiveComponent style={{ width: '800px', height: '600px' }} />;
}
```

**ViewModel Property Hooks**:
- `useViewModelInstanceString` - Text properties
- `useViewModelInstanceNumber` - Numeric properties
- `useViewModelInstanceColor` - Color properties (hex)
- `useViewModelInstanceEnum` - Enum selection
- `useViewModelInstanceTrigger` - Animation triggers

### Pattern 4: Handling Rive Events

**Use Case**: React to events emitted from Rive animation

**Implementation**:

```jsx
import { useRive, EventType, RiveEventType } from 'rive-react';
import { useEffect } from 'react';

export default function InteractiveRating() {
  const { rive, RiveComponent } = useRive({
    src: 'rating.riv',
    stateMachines: 'State Machine 1',
    autoplay: true,
    automaticallyHandleEvents: true,
  });

  useEffect(() => {
    if (!rive) return;

    const onRiveEvent = (event) => {
      const eventData = event.data;

      if (eventData.type === RiveEventType.General) {
        console.log('Event:', eventData.name);

        // Access event properties
        const rating = eventData.properties.rating;
        const message = eventData.properties.message;

        if (rating >= 4) {
          alert(`Thanks for ${rating} stars: ${message}`);
        }
      }
    };

    rive.on(EventType.RiveEvent, onRiveEvent);

    return () => {
      rive.off(EventType.RiveEvent, onRiveEvent);
    };
  }, [rive]);

  return <RiveComponent style={{ width: '400px', height: '300px' }} />;
}
```

### Pattern 5: Preloading Rive Files

**Use Case**: Optimize load times by preloading animations

**Implementation**:

```jsx
import { useRiveFile, useRive } from 'rive-react';

export default function PreloadedAnimation() {
  const { riveFile, status } = useRiveFile({
    src: 'large-animation.riv',
  });

  const { RiveComponent } = useRive({
    riveFile: riveFile,
    artboard: 'Main',
    autoplay: true,
  });

  if (status === 'loading') {
    return <div>Loading animation...</div>;
  }

  if (status === 'failed') {
    return <div>Failed to load animation</div>;
  }

  return <RiveComponent style={{ width: '600px', height: '400px' }} />;
}
```

### Pattern 6: Controlled Animation with Refs

**Use Case**: Control animation from parent component

**Implementation**:

```jsx
import { useRive, useViewModel, useViewModelInstance,
         useViewModelInstanceTrigger } from 'rive-react';
import { useImperativeHandle, forwardRef } from 'react';

const AnimatedComponent = forwardRef((props, ref) => {
  const { rive, RiveComponent } = useRive({
    src: 'logo.riv',
    autoplay: true,
    autoBind: false,
  });

  const viewModel = useViewModel(rive, { useDefault: true });
  const viewModelInstance = useViewModelInstance(viewModel, { rive });

  const { trigger: spinTrigger } = useViewModelInstanceTrigger(
    'triggerSpin',
    viewModelInstance
  );

  // Expose methods to parent
  useImperativeHandle(ref, () => ({
    spin: () => spinTrigger && spinTrigger(),
    pause: () => rive && rive.pause(),
    play: () => rive && rive.play(),
  }));

  return <RiveComponent style={{ width: '200px', height: '200px' }} />;
});

export default function App() {
  const animationRef = useRef();

  return (
    <div>
      <AnimatedComponent ref={animationRef} />
      <button onClick={() => animationRef.current?.spin()}>Spin</button>
      <button onClick={() => animationRef.current?.pause()}>Pause</button>
    </div>
  );
}
```

### Pattern 7: Multi-Property ViewModel Updates

**Use Case**: Update multiple animation properties from complex data

**Implementation**:

```jsx
import { useRive, useViewModel, useViewModelInstance,
         useViewModelInstanceString, useViewModelInstanceNumber,
         useViewModelInstanceColor } from 'rive-react';
import { useEffect } from 'react';

export default function UserProfile({ user }) {
  const { rive, RiveComponent } = useRive({
    src: 'profile.riv',
    autoplay: true,
    autoBind: false,
  });

  const viewModel = useViewModel(rive, { useDefault: true });
  const viewModelInstance = useViewModelInstance(viewModel, { rive });

  // Bind all properties
  const { setValue: setName } = useViewModelInstanceString('name', viewModelInstance);
  const { setValue: setScore } = useViewModelInstanceNumber('score', viewModelInstance);
  const { setValue: setColor } = useViewModelInstanceColor('avatarColor', viewModelInstance);

  useEffect(() => {
    if (user && setName && setScore && setColor) {
      setName(user.name);
      setScore(user.score);
      setColor(parseInt(user.color.substring(1), 16)); // Convert hex to number
    }
  }, [user, setName, setScore, setColor]);

  return <RiveComponent style={{ width: '300px', height: '300px' }} />;
}
```

## Integration Patterns

### With Framer Motion (motion-framer)

Animate container while Rive handles interactive content:

```jsx
import { motion } from 'framer-motion';
import Rive from 'rive-react';

export default function AnimatedCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.05 }}
    >
      <Rive
        src="card.riv"
        stateMachines="Card State Machine"
        style={{ width: '300px', height: '400px' }}
      />
    </motion.div>
  );
}
```

### With GSAP ScrollTrigger (gsap-scrolltrigger)

Trigger Rive animations on scroll:

```jsx
import { useRive, useStateMachineInput } from 'rive-react';
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default function ScrollRive() {
  const containerRef = useRef();
  const { rive, RiveComponent } = useRive({
    src: 'scroll-animation.riv',
    stateMachines: 'State Machine 1',
    autoplay: true,
  });

  const trigger = useStateMachineInput(rive, 'State Machine 1', 'trigger');

  useEffect(() => {
    if (!trigger) return;

    ScrollTrigger.create({
      trigger: containerRef.current,
      start: 'top center',
      onEnter: () => trigger.fire(),
    });
  }, [trigger]);

  return (
    <div ref={containerRef}>
      <RiveComponent style={{ width: '100%', height: '600px' }} />
    </div>
  );
}
```

## Performance Optimization

### 1. Use Off-Screen Renderer

```jsx
<Rive
  src="animation.riv"
  useOffscreenRenderer={true} // Better performance
/>
```

### 2. Optimize Rive Files

**In Rive Editor**:
- Keep artboards under 2MB
- Use vector graphics (avoid raster images when possible)
- Minimize number of bones in skeletal animations
- Reduce complexity of state machines

### 3. Preload Critical Animations

```jsx
const { riveFile } = useRiveFile({ src: 'critical.riv' });
// Preload during app initialization
```

### 4. Disable Automatic Event Handling

```jsx
<Rive
  src="animation.riv"
  automaticallyHandleEvents={false} // Manual control
/>
```

## Common Pitfalls and Solutions

### Pitfall 1: State Machine Input Not Found

**Problem**: `useStateMachineInput` returns null

**Solution**:
```jsx
// ❌ Wrong: Incorrect input name
const input = useStateMachineInput(rive, 'State Machine', 'wrongName');

// ✅ Correct: Match exact name from Rive editor
const input = useStateMachineInput(rive, 'State Machine', 'isHovered');

// Always check if input exists before using
if (input) {
  input.value = true;
}
```

### Pitfall 2: ViewModel Property Not Updating

**Problem**: ViewModel property doesn't update animation

**Solution**:
```jsx
// ❌ Wrong: autoBind enabled
const { rive } = useRive({
  src: 'dashboard.riv',
  autoplay: true,
  // autoBind: true (default)
});

// ✅ Correct: Disable autoBind for ViewModels
const { rive } = useRive({
  src: 'dashboard.riv',
  autoplay: true,
  autoBind: false, // Required for manual ViewModel control
});
```

### Pitfall 3: Event Listener Not Firing

**Problem**: Rive events not triggering callback

**Solution**:
```jsx
// ❌ Wrong: Missing automaticallyHandleEvents
const { rive } = useRive({
  src: 'rating.riv',
  stateMachines: 'State Machine 1',
  autoplay: true,
});

// ✅ Correct: Enable event handling
const { rive } = useRive({
  src: 'rating.riv',
  stateMachines: 'State Machine 1',
  autoplay: true,
  automaticallyHandleEvents: true, // Required for events
});
```

## Resources

### Official Documentation
- **Rive Docs**: https://rive.app/docs
- **React Rive GitHub**: https://github.com/rive-app/rive-react
- **Rive Community**: https://rive.app/community

### Rive Editor
- **Web Editor**: https://rive.app/community
- **Desktop App**: Available for macOS, Windows

### Learning Resources
- **Tutorials**: https://rive.app/learn
- **Examples**: https://rive.app/community/files
- **State Machine Guide**: https://rive.app/docs/state-machine

## Related Skills

- **lottie-animations**: For simpler timeline-based animations without state machines
- **motion-framer**: For code-first React animations with gestures
- **gsap-scrolltrigger**: For scroll-driven animations
- **spline-interactive**: For 3D interactive animations

## Scripts

This skill includes utility scripts:
- `component_generator.py` - Generate Rive React component boilerplate
- `viewmodel_builder.py` - Build ViewModel property bindings

Run scripts from the skill directory:
```bash
./scripts/component_generator.py
./scripts/viewmodel_builder.py
```

## Assets

Starter templates and examples:
- `starter_rive/` - Complete React + Rive template
- `examples/` - Real-world integration patterns



===== FILE: plugins/individual/rive-interactive/skills/rive-interactive/references/api_reference.md =====

# Rive React API Reference

Complete API reference for `rive-react` library.

## Installation

```bash
npm install rive-react
```

## Hooks

### useRive

Main hook for initializing Rive animations.

```typescript
const { rive, RiveComponent } = useRive(options);
```

**Options**:
- `src` (string): Path to .riv file
- `riveFile` (File): Preloaded Rive file
- `artboard` (string): Artboard name
- `animations` (string | string[]): Animations to play
- `stateMachines` (string | string[]): State machines to activate
- `layout` (Layout): Fit and alignment options
- `autoplay` (boolean): Auto-play animations (default: true)
- `autoBind` (boolean): Auto-bind ViewModels (default: true)
- `automaticallyHandleEvents` (boolean): Handle Rive events
- `useOffscreenRenderer` (boolean): Use off-screen renderer
- `shouldResizeCanvasToContainer` (boolean): Auto-resize canvas

### useStateMachineInput

Get state machine input reference.

```typescript
const input = useStateMachineInput(rive, stateMachineName, inputName, initialValue);
```

**Input Types**:
- Boolean: `input.value = true/false`
- Number: `input.value = 50`
- Trigger: `input.fire()`

### useViewModel

Get ViewModel reference.

```typescript
const viewModel = useViewModel(rive, { name: 'ViewModelName' });
// Or use default ViewModel
const viewModel = useViewModel(rive, { useDefault: true });
```

### useViewModelInstance

Get or create ViewModel instance.

```typescript
// Get default instance
const instance = useViewModelInstance(viewModel, { rive });

// Get named instance
const instance = useViewModelInstance(viewModel, { name: 'Instance1' });

// Create new instance
const instance = useViewModelInstance(viewModel, { useNew: true, rive });
```

### useViewModelInstanceString

Bind string property.

```typescript
const { value, setValue } = useViewModelInstanceString('propertyName', instance);
```

### useViewModelInstanceNumber

Bind number property.

```typescript
const { value, setValue } = useViewModelInstanceNumber('propertyName', instance);
```

### useViewModelInstanceColor

Bind color property (hex number).

```typescript
const { value, setValue } = useViewModelInstanceColor('propertyName', instance);

// Set color
setValue(0xff6b6b); // Hex number, no #
```

### useViewModelInstanceEnum

Bind enum property.

```typescript
const { value, setValue } = useViewModelInstanceEnum('propertyName', instance);
```

### useViewModelInstanceTrigger

Fire or listen to trigger events.

```typescript
// Fire trigger
const { trigger } = useViewModelInstanceTrigger('triggerName', instance);
trigger();

// Listen to trigger
useViewModelInstanceTrigger('triggerName', instance, {
  onTrigger: () => console.log('Triggered!')
});
```

### useRiveFile

Preload Rive file.

```typescript
const { riveFile, status } = useRiveFile({ src: 'animation.riv' });
// status: 'loading' | 'success' | 'failed'
```

## Components

### Rive Component

Declarative component for simple use cases.

```jsx
import Rive from 'rive-react';

<Rive
  src="animation.riv"
  artboard="Main"
  animations="idle"
  stateMachines="State Machine 1"
  layout={{ fit: "contain", alignment: "center" }}
  useOffscreenRenderer={true}
  shouldResizeCanvasToContainer={true}
  automaticallyHandleEvents={false}
  style={{ width: '400px', height: '400px' }}
/>
```

### RiveComponent (from useRive)

Component returned by useRive hook.

```jsx
const { RiveComponent } = useRive({ src: 'animation.riv' });

<RiveComponent style={{ width: '400px', height: '400px' }} />
```

## Events

### EventType

```typescript
import { EventType } from 'rive-react';

EventType.Load          // Rive file loaded
EventType.Play          // Animation started
EventType.Pause         // Animation paused
EventType.Stop          // Animation stopped
EventType.Loop          // Animation looped
EventType.Draw          // Frame drawn
EventType.RiveEvent     // Custom Rive event
```

### RiveEventType

```typescript
import { RiveEventType } from 'rive-react';

RiveEventType.General   // General custom event
RiveEventType.OpenUrl   // Open URL event
```

### Event Listening

```jsx
useEffect(() => {
  if (!rive) return;

  const onRiveEvent = (event) => {
    const eventData = event.data;

    if (eventData.type === RiveEventType.General) {
      console.log('Event:', eventData.name);
      console.log('Properties:', eventData.properties);
    }
  };

  rive.on(EventType.RiveEvent, onRiveEvent);

  return () => {
    rive.off(EventType.RiveEvent, onRiveEvent);
  };
}, [rive]);
```

## Layout Options

```typescript
interface Layout {
  fit?: 'contain' | 'cover' | 'fill' | 'fitWidth' | 'fitHeight' | 'none' | 'scaleDown';
  alignment?: 'center' | 'topLeft' | 'topCenter' | 'topRight' | 'centerLeft' |
              'centerRight' | 'bottomLeft' | 'bottomCenter' | 'bottomRight';
}
```

## Rive Instance Methods

From `useRive` hook:

```typescript
rive.play()                          // Play animation
rive.pause()                         // Pause animation
rive.stop()                          // Stop animation
rive.reset()                         // Reset animation
rive.cleanup()                       // Cleanup resources
rive.resizeDrawingSurfaceToCanvas()  // Resize canvas
```

## TypeScript Support

```typescript
import { useRive, useStateMachineInput, Layout } from 'rive-react';

interface Props {
  animationSrc: string;
}

const MyComponent: React.FC<Props> = ({ animationSrc }) => {
  const { rive, RiveComponent } = useRive({
    src: animationSrc,
    autoplay: true,
  });

  const hoverInput = useStateMachineInput(
    rive,
    'State Machine',
    'isHovered',
    false
  );

  return <RiveComponent />;
};
```

## Common Patterns

### Dynamic Animation Switching

```jsx
const [animation, setAnimation] = useState('idle');

const { RiveComponent } = useRive({
  src: 'character.riv',
  animations: animation,
  autoplay: true,
});

// Change animation
<button onClick={() => setAnimation('walk')}>Walk</button>
```

### Multiple State Machines

```jsx
const { rive, RiveComponent } = useRive({
  src: 'animation.riv',
  stateMachines: ['State Machine 1', 'State Machine 2'],
  autoplay: true,
});
```

### Responsive Layout

```jsx
const layout = {
  fit: window.innerWidth < 768 ? 'fitWidth' : 'contain',
  alignment: 'center'
};

<Rive src="animation.riv" layout={layout} />
```

## Error Handling

```jsx
const { rive, RiveComponent } = useRive({
  src: 'animation.riv',
  autoplay: true,
});

if (!rive) {
  return <div>Loading animation...</div>;
}

return <RiveComponent />;
```

## Performance Tips

1. **Use Off-Screen Renderer**:
   ```jsx
   <Rive useOffscreenRenderer={true} />
   ```

2. **Preload Files**:
   ```jsx
   const { riveFile } = useRiveFile({ src: 'animation.riv' });
   ```

3. **Disable Auto-Resize**:
   ```jsx
   <Rive shouldResizeCanvasToContainer={false} />
   ```

4. **Manual Event Handling**:
   ```jsx
   <Rive automaticallyHandleEvents={false} />
   ```



===== FILE: plugins/individual/rive-interactive/agents/rive-interactive-choreographer.md =====

# Rive Animation Choreographer

## Role

Expert animation choreographer specializing in Rive animation design, timing, and orchestration.

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
3. Implement using Rive best practices
4. Optimize for smooth 60fps performance
5. Test across devices and browsers

## Tools

This agent has access to:
- Rive skill knowledge
- Animation pattern libraries
- Performance optimization techniques
- Timeline management strategies



===== FILE: plugins/individual/rive-interactive/commands/component_generator.md =====

# /rive-interactive-component_generator

Rive - Component Generator

## Description

Executes the component_generator script for Rive.

## Usage

```bash
/rive-interactive-component_generator
```

## Implementation

This command runs the `component_generator.py` script from the Rive skill, which provides automated assistance for component generator.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/rive-interactive/commands/viewmodel_builder.md =====

# /rive-interactive-viewmodel_builder

Rive - Viewmodel Builder

## Description

Executes the viewmodel_builder script for Rive.

## Usage

```bash
/rive-interactive-viewmodel_builder
```

## Implementation

This command runs the `viewmodel_builder.py` script from the Rive skill, which provides automated assistance for viewmodel builder.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/rive-interactive/skills/rive-interactive/scripts/component_generator.py =====

````py
#!/usr/bin/env python3
"""
Rive Component Generator

Generate Rive React component boilerplate.

Usage:
    ./component_generator.py  # Interactive mode
"""

print("""
# Rive Component Template

```jsx
import { useRive, useStateMachineInput } from 'rive-react';

export default function RiveComponent() {
  const { rive, RiveComponent } = useRive({
    src: 'animation.riv',
    stateMachines: 'State Machine 1',
    autoplay: true,
  });

  const input = useStateMachineInput(
    rive,
    'State Machine 1',
    'inputName',
    false
  );

  return (
    <RiveComponent style={{ width: '400px', height: '400px' }} />
  );
}
```

Visit https://rive.app/docs for more information.
""")

````


===== FILE: plugins/individual/rive-interactive/skills/rive-interactive/scripts/viewmodel_builder.py =====

````py
#!/usr/bin/env python3
"""
Rive ViewModel Builder

Generate ViewModel property binding code.

Usage:
    ./viewmodel_builder.py  # Interactive mode
"""

print("""
# Rive ViewModel Template

```jsx
import { useRive, useViewModel, useViewModelInstance,
         useViewModelInstanceString, useViewModelInstanceNumber } from 'rive-react';
import { useEffect } from 'react';

export default function ViewModelComponent({ data }) {
  const { rive, RiveComponent } = useRive({
    src: 'animation.riv',
    autoplay: true,
    autoBind: false, // Required for ViewModels
  });

  const viewModel = useViewModel(rive, { useDefault: true });
  const instance = useViewModelInstance(viewModel, { rive });

  const { setValue: setTitle } = useViewModelInstanceString('title', instance);
  const { setValue: setValue } = useViewModelInstanceNumber('value', instance);

  useEffect(() => {
    if (setTitle && setValue) {
      setTitle(data.title);
      setValue(data.value);
    }
  }, [data, setTitle, setValue]);

  return <RiveComponent style={{ width: '600px', height: '400px' }} />;
}
```

Visit https://rive.app/docs/viewmodel for more information.
""")

````


===== FILE: plugins/individual/rive-interactive/skills/rive-interactive/assets/README.md =====

# Rive Interactive - Assets

Starter templates and examples for Rive + React integration.

## Quick Start

```bash
npm install rive-react
```

## Basic Usage

```jsx
import Rive from 'rive-react';

<Rive
  src="animation.riv"
  stateMachines="State Machine 1"
  style={{ width: '400px', height: '400px' }}
/>
```

## State Machine Example

```jsx
import { useRive, useStateMachineInput } from 'rive-react';

export default function InteractiveButton() {
  const { rive, RiveComponent } = useRive({
    src: 'button.riv',
    stateMachines: 'Button State Machine',
    autoplay: true,
  });

  const hoverInput = useStateMachineInput(rive, 'Button State Machine', 'isHovered', false);

  return (
    <div
      onMouseEnter={() => hoverInput && (hoverInput.value = true)}
      onMouseLeave={() => hoverInput && (hoverInput.value = false)}
    >
      <RiveComponent style={{ width: '200px', height: '100px' }} />
    </div>
  );
}
```

## ViewModel Example

```jsx
import { useRive, useViewModel, useViewModelInstance,
         useViewModelInstanceString } from 'rive-react';
import { useEffect } from 'react';

export default function Dashboard({ title }) {
  const { rive, RiveComponent } = useRive({
    src: 'dashboard.riv',
    autoplay: true,
    autoBind: false,
  });

  const viewModel = useViewModel(rive, { useDefault: true });
  const instance = useViewModelInstance(viewModel, { rive });
  const { setValue: setTitle } = useViewModelInstanceString('title', instance);

  useEffect(() => {
    if (setTitle) setTitle(title);
  }, [title, setTitle]);

  return <RiveComponent style={{ width: '800px', height: '600px' }} />;
}
```

## Resources

- [Rive Documentation](https://rive.app/docs)
- [React Rive GitHub](https://github.com/rive-app/rive-react)
- [Rive Community](https://rive.app/community)
- [State Machine Guide](https://rive.app/docs/state-machine)



# Skill: substance-3d-texturing


===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/SKILL.md =====

---
name: substance-3d-texturing
description: Comprehensive skill for Adobe Substance 3D Painter texturing and material creation workflow. Use this skill when creating PBR materials, exporting textures for web/game engines, optimizing 3D assets for real-time rendering, or automating texture workflows. Triggers on tasks involving Substance 3D Painter, PBR texturing, material creation, texture export for Three.js, Babylon.js, Unity, Unreal, glTF optimization, or Python API automation. Creates optimized textures for threejs-webgl, react-three-fiber, and babylonjs-engine materials.
---

# Substance 3D Texturing

## Overview

Master PBR (Physically Based Rendering) texture creation and export workflows for web and real-time engines. This skill covers Substance 3D Painter workflows from material creation through web-optimized texture export, with Python automation for batch processing and integration with WebGL/WebGPU engines.

**Key capabilities:**
- PBR material authoring (metallic/roughness workflow)
- Web-optimized texture export (glTF, Three.js, Babylon.js)
- Python API automation for batch export
- Texture compression and optimization for real-time rendering

## Core Concepts

### PBR Workflow

Substance 3D Painter uses the **metallic/roughness** PBR workflow with these core channels:

**Base Texture Maps:**
- `baseColor` (Albedo) - RGB diffuse color, no lighting information
- `normal` - RGB normal map (tangent space)
- `metallic` - Grayscale metalness (0 = dielectric, 1 = metal)
- `roughness` - Grayscale surface roughness (0 = smooth/glossy, 1 = rough/matte)

**Additional Maps:**
- `ambientOcclusion` (AO) - Grayscale cavity/occlusion
- `height` - Grayscale displacement/height
- `emissive` - RGB self-illumination
- `opacity` - Grayscale transparency

### Export Presets

Substance 3D Painter includes built-in export presets for common engines:
- **PBR Metallic Roughness** - Standard glTF/WebGL format
- **Unity HDRP/URP** - Unity pipelines
- **Unreal Engine** - UE4/UE5 format
- **Arnold (AiStandard)** - Renderer-specific

For web engines, **PBR Metallic Roughness** is the universal standard.

### Texture Resolution

Common resolutions for web (powers of 2):
- 512×512 - Low detail props, mobile
- 1024×1024 - Standard props, characters
- 2048×2048 - Hero assets, close-ups
- 4096×4096 - Showcase quality (use sparingly)

**Web optimization rule:** Start at 1024×1024, scale up only when texture detail is visible.

## Common Patterns

### 1. Basic Web Export (Three.js/Babylon.js)

Manual export workflow for single texture set:

**Steps:**
1. **File → Export Textures**
2. **Select preset:** "PBR Metallic Roughness"
3. **Configure export:**
   - Output directory: Choose target folder
   - File format: PNG (8-bit) for web
   - Padding: "Infinite" (prevents seams)
   - Resolution: 1024×1024 (adjust per asset)
4. **Export**

**Result files:**
```
MyAsset_baseColor.png
MyAsset_normal.png
MyAsset_metallicRoughness.png  // Packed: R=nothing, G=roughness, B=metallic
MyAsset_emissive.png           // Optional
```

**Three.js usage:**
```javascript
import * as THREE from 'three';

const textureLoader = new THREE.TextureLoader();

const material = new THREE.MeshStandardMaterial({
  map: textureLoader.load('MyAsset_baseColor.png'),
  normalMap: textureLoader.load('MyAsset_normal.png'),
  metalnessMap: textureLoader.load('MyAsset_metallicRoughness.png'),
  roughnessMap: textureLoader.load('MyAsset_metallicRoughness.png'),
  aoMap: textureLoader.load('MyAsset_ambientOcclusion.png'),
});
```

### 2. Batch Export with Python API

Automate export for multiple texture sets:

```python
import substance_painter.export
import substance_painter.resource
import substance_painter.textureset

# Define export preset
export_preset = substance_painter.resource.ResourceID(
    context="starter_assets",
    name="PBR Metallic Roughness"
)

# Configure export for all texture sets
config = {
    "exportShaderParams": False,
    "exportPath": "C:/export/web_textures",
    "defaultExportPreset": export_preset.url(),
    "exportList": [],
    "exportParameters": [{
        "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "dithering": True,
            "paddingAlgorithm": "infinite",
            "sizeLog2": 10  // 1024×1024
        }
    }]
}

# Add all texture sets to export list
for texture_set in substance_painter.textureset.all_texture_sets():
    config["exportList"].append({
        "rootPath": texture_set.name()
    })

# Execute export
result = substance_painter.export.export_project_textures(config)

if result.status == substance_painter.export.ExportStatus.Success:
    for stack, files in result.textures.items():
        print(f"Exported {stack}: {len(files)} textures")
else:
    print(f"Export failed: {result.message}")
```

### 3. Resolution Override per Asset

Export different resolutions for different assets (e.g., hero vs. background):

```python
config = {
    "exportPath": "C:/export",
    "defaultExportPreset": export_preset.url(),
    "exportList": [
        {"rootPath": "HeroCharacter"},   # Will use 2048 (override below)
        {"rootPath": "BackgroundProp"}   # Will use 512 (override below)
    ],
    "exportParameters": [
        {
            "filter": {"dataPaths": ["HeroCharacter"]},
            "parameters": {"sizeLog2": 11}  # 2048×2048
        },
        {
            "filter": {"dataPaths": ["BackgroundProp"]},
            "parameters": {"sizeLog2": 9}   # 512×512
        }
    ]
}
```

### 4. Custom Export Preset (Separate Channels)

Create custom preset to export metallic and roughness as separate files:

```python
custom_preset = {
    "exportPresets": [{
        "name": "WebGL_Separated",
        "maps": [
            {
                "fileName": "$textureSet_baseColor",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                ]
            },
            {
                "fileName": "$textureSet_normal",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"}
                ]
            },
            {
                "fileName": "$textureSet_metallic",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8"}
            },
            {
                "fileName": "$textureSet_roughness",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8"}
            }
        ]
    }]
}

config = {
    "exportPath": "C:/export",
    "exportPresets": custom_preset["exportPresets"],
    "exportList": [{"rootPath": "MyAsset", "exportPreset": "WebGL_Separated"}]
}
```

### 5. Mobile-Optimized Export

Aggressive compression for mobile WebGL:

```python
mobile_config = {
    "exportPath": "C:/export/mobile",
    "defaultExportPreset": export_preset.url(),
    "exportList": [{"rootPath": texture_set.name()}],
    "exportParameters": [{
        "parameters": {
            "fileFormat": "jpeg",        # JPEG for baseColor (lossy but smaller)
            "bitDepth": "8",
            "sizeLog2": 9,               # 512×512 maximum
            "paddingAlgorithm": "infinite"
        }
    }, {
        "filter": {"outputMaps": ["$textureSet_normal", "$textureSet_metallicRoughness"]},
        "parameters": {
            "fileFormat": "png"          # PNG for data maps (need lossless)
        }
    }]
}
```

**Post-export:** Use tools like `pngquant` or `tinypng` for further compression.

### 6. glTF/GLB Integration

Export textures for glTF 2.0 format:

```python
gltf_config = {
    "exportPath": "C:/export/gltf",
    "defaultExportPreset": substance_painter.resource.ResourceID(
        context="starter_assets",
        name="PBR Metallic Roughness"
    ).url(),
    "exportList": [{"rootPath": texture_set.name()}],
    "exportParameters": [{
        "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10,              # 1024×1024
            "paddingAlgorithm": "infinite"
        }
    }]
}

# After export, reference in glTF:
# {
#   "materials": [{
#     "name": "Material",
#     "pbrMetallicRoughness": {
#       "baseColorTexture": {"index": 0},
#       "metallicRoughnessTexture": {"index": 1}
#     },
#     "normalTexture": {"index": 2}
#   }]
# }
```

### 7. Event-Driven Export Plugin

Auto-export on save using Python plugin:

```python
import substance_painter.event
import substance_painter.export
import substance_painter.project

def auto_export(e):
    if not substance_painter.project.is_open():
        return

    config = {
        "exportPath": substance_painter.project.file_path().replace('.spp', '_textures'),
        "defaultExportPreset": substance_painter.resource.ResourceID(
            context="starter_assets", name="PBR Metallic Roughness"
        ).url(),
        "exportList": [{"rootPath": ts.name()} for ts in substance_painter.textureset.all_texture_sets()],
        "exportParameters": [{
            "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
        }]
    }

    substance_painter.export.export_project_textures(config)
    print("Auto-export completed")

# Register event
substance_painter.event.DISPATCHER.connect(
    substance_painter.event.ProjectSaved,
    auto_export
)
```

## Integration Patterns

### Three.js + React Three Fiber

Use exported textures in R3F:

```jsx
import { useTexture } from '@react-three/drei';

function TexturedMesh() {
  const [baseColor, normal, metallicRoughness, ao] = useTexture([
    '/textures/Asset_baseColor.png',
    '/textures/Asset_normal.png',
    '/textures/Asset_metallicRoughness.png',
    '/textures/Asset_ambientOcclusion.png',
  ]);

  return (
    <mesh>
      <boxGeometry />
      <meshStandardMaterial
        map={baseColor}
        normalMap={normal}
        metalnessMap={metallicRoughness}
        roughnessMap={metallicRoughness}
        aoMap={ao}
      />
    </mesh>
  );
}
```

See **react-three-fiber** skill for advanced R3F material workflows.

### Babylon.js PBR Materials

```javascript
import { PBRMaterial, Texture } from '@babylonjs/core';

const pbr = new PBRMaterial("pbr", scene);
pbr.albedoTexture = new Texture("/textures/Asset_baseColor.png", scene);
pbr.bumpTexture = new Texture("/textures/Asset_normal.png", scene);
pbr.metallicTexture = new Texture("/textures/Asset_metallicRoughness.png", scene);
pbr.useRoughnessFromMetallicTextureAlpha = false;
pbr.useRoughnessFromMetallicTextureGreen = true;
pbr.useMetallnessFromMetallicTextureBlue = true;
```

See **babylonjs-engine** skill for advanced PBR workflows.

### GLTF Export Pipeline

1. Export textures from Substance (as above)
2. Export model from Blender with glTF exporter
3. Reference Substance textures in `.gltf` JSON
4. Use `gltf-pipeline` for Draco compression:

```bash
gltf-pipeline -i model.gltf -o model.glb -d
```

See **blender-web-pipeline** skill for complete 3D asset pipeline.

## Performance Optimization

### Texture Size Budget

**Desktop WebGL:** ~100-150MB total texture memory
**Mobile WebGL:** ~30-50MB total texture memory

**Budget per asset:**
- Background/props: 512×512 (1MB per texture × 4 maps = 4MB)
- Standard assets: 1024×1024 (4MB per texture × 4 maps = 16MB)
- Hero assets: 2048×2048 (16MB per texture × 4 maps = 64MB)

### Compression Strategies

1. **JPEG for baseColor** (70-80% quality) - 10× smaller than PNG
2. **PNG-8 for data maps** (normal, metallic, roughness) - lossless required
3. **Basis Universal** (`.basis`) - GPU texture compression (90% smaller)
4. **Texture atlasing** - Combine multiple assets into single texture

### Channel Packing

Pack grayscale maps into RGB channels to reduce texture count:

**Packed ORM (Occlusion-Roughness-Metallic):**
- Red: Ambient Occlusion
- Green: Roughness
- Blue: Metallic

Export in Substance:
```python
orm_map = {
    "fileName": "$textureSet_ORM",
    "channels": [
        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "ambientOcclusion"},
        {"destChannel": "G", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"},
        {"destChannel": "B", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
    ]
}
```

### Mipmaps

Always enable mipmaps in engine for textures viewed at distance:

```javascript
// Three.js (automatic)
texture.generateMipmaps = true;

// Babylon.js
texture.updateSamplingMode(Texture.TRILINEAR_SAMPLINGMODE);
```

## Common Pitfalls

### 1. Wrong Color Space for BaseColor

**Problem:** BaseColor exported in linear space looks washed out.

**Solution:** Substance exports baseColor in sRGB by default (correct). Ensure engine uses sRGB:

```javascript
// Three.js
baseColorTexture.colorSpace = THREE.SRGBColorSpace;

// Babylon.js (automatic for albedoTexture)
```

### 2. Normal Map Baking Issues

**Problem:** Normal maps show inverted or incorrect shading.

**Solution:**
- Verify tangent space normal format (DirectX vs. OpenGL Y-flip)
- Substance uses OpenGL (Y+), same as glTF standard
- If using DirectX engine, flip green channel in export

### 3. Metallic/Roughness Channel Order

**Problem:** Metallic/roughness texture has swapped channels.

**Solution:** Default Substance export:
- Blue channel = Metallic
- Green channel = Roughness
- Matches glTF 2.0 specification

### 4. Padding Artifacts at UV Seams

**Problem:** Black or colored lines appear at UV seams.

**Solution:** Set padding algorithm to **"infinite"** in export settings:
```python
"paddingAlgorithm": "infinite"
```

### 5. Oversized Textures for Web

**Problem:** 4K textures cause long load times and memory issues on web.

**Solution:**
- Default to 1024×1024 for web
- Use 2048×2048 only for hero assets viewed close-up
- Implement LOD system with multiple resolution sets

### 6. Missing AO Map in Engine

**Problem:** AO map exported but not visible in engine.

**Solution:**
- Three.js: Requires second UV channel (`geometry.attributes.uv2`)
- Babylon.js: Set `material.useAmbientOcclusionFromMetallicTextureRed = true`
- Alternative: Bake AO into baseColor in Substance

## Resources

See bundled resources for complete workflows:

- **references/python_api_reference.md** - Complete Substance Painter Python API
- **references/export_presets.md** - Built-in and custom export preset catalog
- **references/pbr_channel_guide.md** - Deep dive into PBR texture channels
- **scripts/batch_export.py** - Batch export all texture sets
- **scripts/web_optimizer.py** - Post-process textures for web (resize, compress)
- **scripts/generate_export_preset.py** - Create custom export preset JSON
- **assets/export_templates/** - Pre-configured export presets for Three.js, Babylon.js, Unity

## Related Skills

- **blender-web-pipeline** - Complete 3D model → texture → web pipeline
- **threejs-webgl** - Loading and using PBR textures in Three.js
- **react-three-fiber** - R3F material workflows with Substance textures
- **babylonjs-engine** - Babylon.js PBR material system integration



===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/references/export_presets.md =====

# Substance 3D Painter Export Presets

Complete catalog of built-in and custom export presets for various game engines and web platforms.

## Table of Contents

- [Built-in Presets](#built-in-presets)
- [Web/glTF Presets](#webgltf-presets)
- [Custom Preset Examples](#custom-preset-examples)
- [Channel Packing Strategies](#channel-packing-strategies)

## Built-in Presets

Substance 3D Painter ships with presets for major engines and renderers.

### PBR Metallic Roughness

**Context:** `starter_assets`
**Name:** `PBR Metallic Roughness`
**Use for:** glTF, Three.js, Babylon.js, generic PBR engines

**Output textures:**
- `$textureSet_baseColor.png` - Base color (RGB)
- `$textureSet_normal.png` - Normal map (RGB, OpenGL format)
- `$textureSet_metallicRoughness.png` - Packed texture:
  - Red: Unused
  - Green: Roughness
  - Blue: Metallic
- `$textureSet_emissive.png` - Emissive (RGB) *if present*

**Usage:**
```python
preset = substance_painter.resource.ResourceID(
    context="starter_assets",
    name="PBR Metallic Roughness"
)
```

**Best for:**
- Web applications (Three.js, Babylon.js)
- glTF/GLB export
- Generic PBR workflows

---

### Unity HDRP (Lit)

**Context:** `starter_assets`
**Name:** `Unity HDRP (Lit)`
**Use for:** Unity High Definition Render Pipeline

**Output textures:**
- `$textureSet_BaseMap.png` - Base color + alpha
- `$textureSet_Normal.png` - Normal map (DirectX format)
- `$textureSet_MaskMap.png` - Packed texture:
  - Red: Metallic
  - Green: Ambient Occlusion
  - Blue: Detail Mask
  - Alpha: Smoothness (1 - roughness)

**Differences from standard PBR:**
- DirectX normal format (Y-flipped)
- Smoothness instead of roughness (inverted)
- Different channel packing

---

### Unity URP (Lit)

**Context:** `starter_assets`
**Name:** `Unity URP (Lit)`
**Use for:** Unity Universal Render Pipeline

**Output textures:**
- `$textureSet_BaseMap.png` - Base color + alpha
- `$textureSet_Normal.png` - Normal map
- `$textureSet_MetallicSmoothness.png` - Packed:
  - RGB: Metallic
  - Alpha: Smoothness

---

### Unreal Engine

**Context:** `starter_assets`
**Name:** `Unreal Engine 4/5 (Packed)`
**Use for:** Unreal Engine 4 and 5

**Output textures:**
- `$textureSet_BaseColor.png` - Base color
- `$textureSet_Normal.png` - Normal map (DirectX)
- `$textureSet_OcclusionRoughnessMetallic.png` - Packed:
  - Red: Ambient Occlusion
  - Green: Roughness
  - Blue: Metallic
- `$textureSet_Emissive.png` - Emissive

**Note:** Unreal's packed ORM format is widely used and efficient.

---

### Arnold (AiStandard)

**Context:** `starter_assets`
**Name:** `Arnold (AiStandard)`
**Use for:** Arnold renderer (Maya, Cinema 4D, Houdini)

**Output textures:**
- `$textureSet_baseColor.exr` - Base color (EXR 32-bit)
- `$textureSet_normal.exr` - Normal map
- `$textureSet_specularRoughness.exr` - Roughness
- `$textureSet_metalness.exr` - Metallic

**Note:** Uses EXR format for high dynamic range.

---

### V-Ray

**Context:** `starter_assets`
**Name:** `V-Ray`
**Use for:** V-Ray renderer

**Output textures:**
- Separate files for each channel
- High bit-depth support (16/32-bit)

## Web/glTF Presets

Optimized presets for web and real-time rendering.

### glTF 2.0 Standard

**Custom preset for glTF 2.0 compliance:**

```python
{
    "exportPresets": [{
        "name": "glTF_Standard",
        "maps": [
            {
                "fileName": "$textureSet_baseColor",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                ],
                "parameters": {
                    "fileFormat": "png",
                    "bitDepth": "8",
                    "sizeLog2": 10  # 1024×1024
                }
            },
            {
                "fileName": "$textureSet_normal",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
            },
            {
                "fileName": "$textureSet_metallicRoughness",
                "channels": [
                    {"destChannel": "G", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"},
                    {"destChannel": "B", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
            }
        ]
    }]
}
```

**Matches glTF 2.0 specification:**
- BaseColor in sRGB color space
- MetallicRoughness: Green = Roughness, Blue = Metallic
- Normal in OpenGL format (Y+)

---

### Three.js Optimized

**Preset optimized for Three.js MeshStandardMaterial:**

```python
{
    "exportPresets": [{
        "name": "ThreeJS_Standard",
        "maps": [
            {
                "fileName": "$textureSet_color",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                ],
                "parameters": {"fileFormat": "jpeg", "bitDepth": "8", "sizeLog2": 10}  # JPEG for smaller size
            },
            {
                "fileName": "$textureSet_normal",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
            },
            {
                "fileName": "$textureSet_ao",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "ambientOcclusion"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
            },
            {
                "fileName": "$textureSet_metalness",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
            },
            {
                "fileName": "$textureSet_roughness",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
            }
        ]
    }]
}
```

**Features:**
- JPEG for baseColor (70-80% quality, 10× smaller)
- PNG for data textures (lossless required)
- Separate metalness and roughness for flexibility
- Separate AO map

**Three.js usage:**
```javascript
const material = new THREE.MeshStandardMaterial({
  map: new THREE.TextureLoader().load('Asset_color.jpg'),
  normalMap: new THREE.TextureLoader().load('Asset_normal.png'),
  aoMap: new THREE.TextureLoader().load('Asset_ao.png'),
  metalnessMap: new THREE.TextureLoader().load('Asset_metalness.png'),
  roughnessMap: new THREE.TextureLoader().load('Asset_roughness.png'),
});
```

---

### Babylon.js PBR

**Preset for Babylon.js PBRMaterial:**

```python
{
    "exportPresets": [{
        "name": "BabylonJS_PBR",
        "maps": [
            {
                "fileName": "$textureSet_albedo",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
            },
            {
                "fileName": "$textureSet_normal",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
            },
            {
                "fileName": "$textureSet_metallicRoughness",
                "channels": [
                    {"destChannel": "G", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"},
                    {"destChannel": "B", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
            }
        ]
    }]
}
```

**Babylon.js usage:**
```javascript
const pbr = new BABYLON.PBRMaterial("pbr", scene);
pbr.albedoTexture = new BABYLON.Texture("Asset_albedo.png", scene);
pbr.bumpTexture = new BABYLON.Texture("Asset_normal.png", scene);
pbr.metallicTexture = new BABYLON.Texture("Asset_metallicRoughness.png", scene);
pbr.useRoughnessFromMetallicTextureGreen = true;
pbr.useMetallnessFromMetallicTextureBlue = true;
```

---

### Mobile WebGL (Low Spec)

**Aggressive compression for mobile:**

```python
{
    "exportPresets": [{
        "name": "Mobile_WebGL",
        "maps": [
            {
                "fileName": "$textureSet_color",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                ],
                "parameters": {"fileFormat": "jpeg", "bitDepth": "8", "sizeLog2": 9}  # 512×512
            },
            {
                "fileName": "$textureSet_normal",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 9}  # Skip blue channel
            },
            {
                "fileName": "$textureSet_packed",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "ambientOcclusion"},
                    {"destChannel": "G", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"},
                    {"destChannel": "B", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                ],
                "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 9}
            }
        ]
    }]
}
```

**Optimizations:**
- 512×512 maximum resolution
- JPEG for color (lossy but small)
- RG normal map only (reconstruct Z in shader)
- ORM packing (3 maps → 1 texture)

**Total texture budget:** ~3MB (vs. ~16MB standard)

## Custom Preset Examples

### ORM Packing (Occlusion-Roughness-Metallic)

**Most efficient packing for web:**

```python
orm_preset = {
    "exportPresets": [{
        "name": "Web_ORM",
        "maps": [
            {
                "fileName": "$textureSet_baseColor",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                ]
            },
            {
                "fileName": "$textureSet_normal",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"}
                ]
            },
            {
                "fileName": "$textureSet_ORM",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "ambientOcclusion"},
                    {"destChannel": "G", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"},
                    {"destChannel": "B", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                ]
            }
        ]
    }]
}
```

**Reduces texture count:** 6 textures → 3 textures
**Shader setup (Three.js):**
```javascript
material.aoMap = ormTexture;
material.roughnessMap = ormTexture;
material.metalnessMap = ormTexture;
// Three.js automatically reads from R/G/B channels
```

---

### Height + Normal Combined

**Pack height into normal alpha channel:**

```python
{
    "fileName": "$textureSet_normalHeight",
    "channels": [
        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
        {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"},
        {"destChannel": "A", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "height"}
    ]
}
```

**Use case:** Parallax occlusion mapping (height from alpha)

---

### Emissive + Alpha

**Pack emissive RGB + opacity:**

```python
{
    "fileName": "$textureSet_emissiveAlpha",
    "channels": [
        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "emissive"},
        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "emissive"},
        {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "emissive"},
        {"destChannel": "A", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "opacity"}
    ]
}
```

---

### Stylized/NPR Export

**Non-photorealistic rendering (toon shading):**

```python
{
    "exportPresets": [{
        "name": "Stylized_Toon",
        "maps": [
            {
                "fileName": "$textureSet_diffuse",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                ]
            },
            {
                "fileName": "$textureSet_shadowMask",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "ambientOcclusion"}
                ]
            },
            # No metallic/roughness for toon shaders
        ]
    }]
}
```

## Channel Packing Strategies

### Standard PBR Packing

**glTF 2.0 / Khronos Standard:**
- BaseColor: RGB (sRGB)
- Normal: RGB (OpenGL, linear)
- MetallicRoughness:
  - R: Unused
  - G: Roughness (linear)
  - B: Metallic (linear)

**Advantages:**
- Industry standard
- Maximum compatibility
- glTF compliance

---

### Unreal Engine Packing

**Unreal's ORM format:**
- BaseColor: RGB
- Normal: RGB (DirectX)
- ORM:
  - R: Ambient Occlusion
  - G: Roughness
  - B: Metallic

**Advantages:**
- Includes AO without extra texture
- Widely used format
- Efficient for complex materials

---

### Mobile Optimized Packing

**Aggressive compression:**
- BaseColor: JPEG (lossy)
- Normal: RG only (reconstruct Z)
- ORM: RGB (AO + Roughness + Metallic)

**Advantages:**
- Smallest file size
- Reduced texture memory
- Faster loading on mobile

**Disadvantages:**
- Lossy baseColor (visual artifacts)
- RG normal requires shader modification

---

### High Quality / Archival

**Separate channels, high bit depth:**
- BaseColor: PNG-16 or EXR-32
- Normal: PNG-16
- Metallic: PNG-16 (separate)
- Roughness: PNG-16 (separate)
- AO: PNG-16 (separate)
- Height: PNG-16 (separate)

**Advantages:**
- Maximum quality
- Per-channel editability
- HDR support (EXR)

**Disadvantages:**
- Large file sizes
- More texture slots
- Overkill for real-time

## Preset Selection Guide

### By Platform

| Platform | Recommended Preset | Resolution | Format |
|----------|-------------------|------------|---------|
| **Desktop Web** | glTF_Standard / Web_ORM | 1024-2048 | PNG |
| **Mobile Web** | Mobile_WebGL | 512-1024 | JPEG+PNG |
| **Unity HDRP** | Unity HDRP (Lit) | 2048-4096 | PNG |
| **Unreal Engine** | Unreal Engine (Packed) | 2048-4096 | PNG |
| **glTF Export** | PBR Metallic Roughness | 1024-2048 | PNG |
| **Three.js** | ThreeJS_Standard | 1024-2048 | JPEG+PNG |
| **Babylon.js** | BabylonJS_PBR | 1024-2048 | PNG |

### By Use Case

| Use Case | Preset | Notes |
|----------|--------|-------|
| **Quick web export** | PBR Metallic Roughness | Built-in, universal |
| **Smallest file size** | Mobile_WebGL | JPEG color, ORM packing |
| **Maximum compatibility** | glTF_Standard | Strict glTF 2.0 spec |
| **Maximum quality** | High Quality / Archival | 16/32-bit, separate channels |
| **Production pipeline** | Web_ORM | Efficient, industry standard |

### By Texture Count

| Texture Count | Packing Strategy | Maps |
|---------------|------------------|------|
| **3 textures** | ORM packed | BaseColor, Normal, ORM |
| **4 textures** | glTF standard | BaseColor, Normal, MetallicRoughness, Emissive |
| **5+ textures** | Separate channels | Color, Normal, Metallic, Roughness, AO |

## Best Practices

### For Web Platforms

1. **Use ORM packing** - 3 textures instead of 6
2. **JPEG for baseColor** - 70-80% quality, 10× smaller
3. **PNG for data maps** - Normal, ORM require lossless
4. **Start at 1024×1024** - Scale up only when needed
5. **Test file sizes** - Aim for <5MB total per asset

### For Game Engines

1. **Use engine-specific presets** - Proper channel order/format
2. **Match color space** - sRGB for color, linear for data
3. **Check normal format** - DirectX vs. OpenGL (Y-flip)
4. **Consider UDIM** - For large characters (multiple tiles)

### For glTF/GLB

1. **Use "PBR Metallic Roughness"** - Official standard
2. **OpenGL normal maps** - Y+ (green up)
3. **Keep within spec** - Avoid custom channels
4. **Compress with Draco** - gltf-pipeline for final export

## Troubleshooting

**Textures look washed out:**
- BaseColor in wrong color space (should be sRGB)
- Check engine texture settings

**Metallic looks rough / rough looks metallic:**
- Channels swapped (check Green/Blue order)
- Verify MetallicRoughness packing: G=Roughness, B=Metallic

**Normal map inverted:**
- DirectX vs. OpenGL format
- Flip green channel in export or engine

**Seams at UV borders:**
- Use `"paddingAlgorithm": "infinite"` in export parameters
- Increase dilation distance

**File sizes too large:**
- Use JPEG for baseColor
- Reduce resolution (sizeLog2)
- Pack channels (ORM)
- Compress with external tools (pngquant, tinypng)



===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/references/pbr_channel_guide.md =====

# PBR Texture Channel Guide

Deep dive into Physically Based Rendering (PBR) texture channels, their purpose, authoring best practices, and technical specifications.

## Table of Contents

- [PBR Fundamentals](#pbr-fundamentals)
- [Core Channels](#core-channels)
- [Additional Channels](#additional-channels)
- [Channel Best Practices](#channel-best-practices)
- [Common Material Types](#common-material-types)

## PBR Fundamentals

### What is PBR?

Physically Based Rendering (PBR) is a shading model that aims to accurately simulate how light interacts with surfaces in the real world. PBR workflows ensure materials look consistent under different lighting conditions.

**Key principles:**
1. **Energy conservation** - Reflected light never exceeds incoming light
2. **Fresnel reflectance** - Reflection intensity varies with viewing angle
3. **Microsurface detail** - Surface roughness affects light scattering

### Metallic/Roughness vs. Specular/Glossiness

Substance 3D Painter uses the **metallic/roughness** workflow (also called metal/rough or met/rough).

**Metallic/Roughness:**
- `baseColor` = Albedo color for dielectrics, reflectance tint for metals
- `metallic` = 0 for non-metals, 1 for metals
- `roughness` = Surface roughness (0 = glossy, 1 = rough)

**Advantages:**
- Simpler (fewer maps)
- More physically accurate
- Industry standard (glTF, PBR games)

**Alternative (Specular/Glossiness):**
- `diffuse` = Albedo color
- `specular` = RGB specular reflectance
- `glossiness` = Surface smoothness (1 - roughness)

Note: Substance supports both, but metallic/roughness is recommended for web.

## Core Channels

### Base Color (Albedo)

**What it is:**
The intrinsic color of the surface, without any lighting information.

**Technical specs:**
- **Format:** RGB, 8-bit per channel (24-bit total)
- **Color space:** sRGB (gamma ~2.2)
- **Value range:** 0-255 per channel
- **File format:** PNG or JPEG

**Authoring guidelines:**

**For non-metals (dielectrics):**
- Typical value range: sRGB 50-240 (linear 0.02-0.8)
- Dark materials: Charcoal ~50, Rubber ~60
- Mid-tone materials: Wood ~120, Leather ~100
- Light materials: Snow ~240, Paper ~200
- **Never pure black** (30 minimum for black materials)
- **Never pure white** (240 maximum for white materials)

**For metals:**
- Use actual metal reflectance values:
  - Iron: sRGB(196, 198, 200)
  - Gold: sRGB(255, 195, 86)
  - Copper: sRGB(250, 155, 110)
  - Aluminum: sRGB(245, 246, 246)
  - Silver: sRGB(252, 250, 245)
- Bright, saturated colors for colored metals (gold, copper)

**Common mistakes:**
- ❌ **Lighting baked in** - Shadows or highlights in albedo
- ❌ **Too dark** - Black baseColor = no light reflection
- ❌ **Too bright** - Unrealistic energy conservation
- ❌ **Specular details** - Reflections should come from roughness, not albedo

**Validation:**
Use the "no lighting" shader in Substance to check:
- Does the material look correct without lights?
- Are there any baked shadows or highlights?
- Are values within physically plausible ranges?

---

### Normal Map

**What it is:**
Encodes surface detail by perturbing surface normals, creating the illusion of depth without additional geometry.

**Technical specs:**
- **Format:** RGB, 8-bit per channel
- **Color space:** Linear (not sRGB!)
- **Value range:** 0-255 → maps to -1 to +1 normals
- **File format:** PNG (lossless required)
- **Coordinate system:** Tangent space

**Normal format standards:**

**OpenGL (Y+) - Used by:**
- glTF/GLB
- Three.js
- Babylon.js
- Substance 3D Painter (default export)
- WebGL/WebGPU

**DirectX (Y-) - Used by:**
- Unity
- Unreal Engine
- Direct3D engines

**Visual difference:**
- OpenGL: Green channel points "up" on the texture
- DirectX: Green channel points "down" (inverted Y)

**Converting between formats:**
- OpenGL → DirectX: Invert green channel (255 - G)
- DirectX → OpenGL: Invert green channel (255 - G)

**Authoring guidelines:**

**Do:**
- ✅ Bake high-poly details to normal map
- ✅ Use for micro-surface detail (scratches, dents, pores)
- ✅ Keep intensity realistic (don't over-exaggerate)
- ✅ Use 8-bit PNG (16-bit unnecessary for real-time)

**Don't:**
- ❌ Use JPEG (compression artifacts create shading errors)
- ❌ Apply to low-poly silhouettes (causes artifacts)
- ❌ Extreme details (creates aliasing/shimmering)

**Validation:**
- Flat surface = RGB(128, 128, 255) or #8080FF
- No black or white pixels (except extreme cases)
- Blue channel dominant (~255) for most pixels

---

### Metallic

**What it is:**
Defines whether a surface is metallic (conductor) or non-metallic (dielectric/insulator).

**Technical specs:**
- **Format:** Grayscale, 8-bit
- **Color space:** Linear
- **Value range:** 0-255 (0 = non-metal, 255 = metal)
- **File format:** PNG

**Physical meaning:**
- **0 (black)** - Dielectric materials:
  - Wood, plastic, fabric, skin, ceramic, stone
  - Specular reflection ~4% (Fresnel F0 ≈ 0.04)
  - BaseColor = diffuse color
- **255 (white)** - Metallic materials:
  - Iron, gold, copper, aluminum, silver, chrome
  - Specular reflection ~60-100% (Fresnel F0 ≈ 0.6-1.0)
  - BaseColor = specular tint (no diffuse)

**Authoring guidelines:**

**Binary choice:**
- Use **only 0 or 255** (fully non-metal or fully metal)
- **Avoid gray values** (0-254) - not physically accurate
- Exception: Corroded/oxidized metals can have transition zones

**Material examples:**
- **Metallic = 0:** Wood, leather, cloth, rubber, plastic, glass, skin, concrete
- **Metallic = 255:** Iron, steel, aluminum, gold, silver, copper, brass, chrome

**Common mistakes:**
- ❌ Gradient metallic (0-255) - Not realistic
- ❌ Metallic = 255 with dark baseColor - Metals are reflective
- ❌ Metallic = 0 with bright baseColor + low roughness - Creates plastic look

**Special cases:**

**Painted metal:**
- Metallic = 0 (paint is dielectric)
- Only exposed metal areas = 255

**Rusty metal:**
- Clean metal = 255
- Rust (iron oxide) = 0 (rust is dielectric)

**Validation:**
- Histogram should show two spikes: at 0 and 255
- Very few pixels in 1-254 range

---

### Roughness

**What it is:**
Defines the microsurface roughness, controlling how light scatters when reflected.

**Technical specs:**
- **Format:** Grayscale, 8-bit
- **Color space:** Linear
- **Value range:** 0-255 (0 = smooth/glossy, 255 = rough/matte)
- **File format:** PNG

**Physical meaning:**
- **0 (black)** - Mirror smooth:
  - Perfect specular reflections
  - Sharp, focused highlights
  - Examples: Polished chrome, water, glass
- **255 (white)** - Completely rough:
  - Diffuse specular reflections
  - Large, blurred highlights
  - Examples: Concrete, fabric, unfinished wood

**Authoring guidelines:**

**Typical value ranges:**
- Mirror/chrome: 0-20
- Polished metal: 20-50
- Glossy plastic: 30-70
- Painted surfaces: 50-100
- Unfinished wood: 150-200
- Concrete/fabric: 200-255

**Do:**
- ✅ Use full range (0-255) across different materials
- ✅ Add variation (dirt, fingerprints, wear in crevices)
- ✅ Consider surface finish (polished vs. brushed vs. rough)

**Don't:**
- ❌ Uniform roughness across entire surface (boring, unrealistic)
- ❌ Pure white (255) for hard surfaces (leaves no specular)
- ❌ Pure black (0) for organic materials (too perfect)

**Roughness variation examples:**

**Metal object:**
- Base roughness: 40 (semi-polished)
- Scratches: 80 (exposed rough metal)
- Fingerprints: 30 (oil reduces roughness)
- Edges: 60 (worn from handling)

**Wooden table:**
- Base roughness: 100 (sanded wood)
- Glossy finish: 40 (varnish/polish)
- Worn areas: 150 (exposed grain)

**Validation:**
- Histogram should show variation (not single spike)
- Check for breakup in specular highlights (not uniform)
- Test under different lighting (rotating HDRI)

---

## Additional Channels

### Ambient Occlusion (AO)

**What it is:**
Approximates how ambient light reaches each point on the surface. Darkens crevices and contact areas.

**Technical specs:**
- **Format:** Grayscale, 8-bit
- **Color space:** Linear
- **Value range:** 0-255 (0 = fully occluded, 255 = fully lit)
- **File format:** PNG

**Purpose:**
- Enhance depth perception
- Darken crevices, corners, contact points
- Fake indirect lighting occlusion

**Authoring guidelines:**

**Do:**
- ✅ Bake from high-poly mesh
- ✅ Subtle intensity (avoid pure black)
- ✅ Use for cavity detail (screws, seams, panel gaps)

**Don't:**
- ❌ Bake directional lighting (AO should be omnidirectional)
- ❌ Over-darken (reduces albedo contrast)

**Web implementation:**

**Three.js:**
```javascript
material.aoMap = aoTexture;
material.aoMapIntensity = 1.0; // Adjust strength
geometry.attributes.uv2 = geometry.attributes.uv; // AO requires second UV channel
```

**Note:** Many engines require a second UV channel for AO. Consider baking AO into baseColor as an alternative for simpler setups.

---

### Height (Displacement)

**What it is:**
Grayscale map encoding surface height, used for displacement mapping or parallax effects.

**Technical specs:**
- **Format:** Grayscale, 8-16 bit
- **Color space:** Linear
- **Value range:** 0-255 (0 = low, 255 = high)
- **File format:** PNG

**Use cases:**
1. **Displacement mapping** - Actual geometry modification (not common in real-time)
2. **Parallax occlusion mapping (POM)** - Shader-based fake depth
3. **Normal map generation** - Convert height → normal in Substance

**Authoring guidelines:**
- Smooth gradients (avoid sharp steps)
- Sufficient contrast for visible effect
- Usually lower resolution than other maps (512-1024)

**Web usage:**
Limited support in real-time engines. Height is usually converted to normal maps in Substance before export.

---

### Emissive (Self-Illumination)

**What it is:**
RGB map defining areas that emit light (glow).

**Technical specs:**
- **Format:** RGB, 8-bit or 16-bit
- **Color space:** Linear (for HDR) or sRGB (for LDR)
- **Value range:** 0-255 (8-bit) or 0-65535 (16-bit)
- **File format:** PNG or EXR

**Use cases:**
- Glowing screens, LEDs, neon signs
- Bioluminescence
- Hot metal/lava
- Energy effects

**Authoring guidelines:**

**LDR emissive (8-bit):**
- Black (0,0,0) = no emission
- White (255,255,255) = full brightness
- Use `emissiveIntensity` in engine to control brightness

**HDR emissive (16/32-bit EXR):**
- Values can exceed 1.0 for bloom effects
- Physically accurate for bright lights

**Web implementation:**

**Three.js:**
```javascript
material.emissive = new THREE.Color(0xffffff);
material.emissiveMap = emissiveTexture;
material.emissiveIntensity = 2.0; // Boost for bloom
```

**Common mistake:**
❌ Using emissive for ambient occlusion (emissive should glow, not darken)

---

### Opacity (Alpha)

**What it is:**
Grayscale map controlling surface transparency.

**Technical specs:**
- **Format:** Grayscale, 8-bit
- **Color space:** Linear
- **Value range:** 0-255 (0 = transparent, 255 = opaque)
- **File format:** PNG (with alpha channel support)

**Use cases:**
- Glass, water, smoke
- Vegetation (leaves, grass)
- Decals, stickers
- Fading effects

**Authoring guidelines:**

**Binary alpha (cutout):**
- Use only 0 or 255 (fully transparent or opaque)
- Efficient for vegetation (no alpha blending)
- Set `alphaTest` threshold in engine

**Gradient alpha (blended):**
- Full 0-255 range for smooth transparency
- More expensive (requires alpha blending, sorting)

**Web implementation:**

**Three.js:**
```javascript
material.transparent = true;
material.alphaMap = opacityTexture;
material.alphaTest = 0.5; // For binary alpha (cutout)
material.opacity = 1.0; // Overall opacity multiplier
```

**Performance notes:**
- Alpha blending is expensive (disable backface culling, requires sorting)
- Use `alphaTest` (cutout) instead of `transparent` when possible

## Channel Best Practices

### Color Space Management

**sRGB (Gamma ~2.2):**
- BaseColor
- Emissive (8-bit)

**Linear (No Gamma):**
- Normal
- Metallic
- Roughness
- AO
- Height
- Opacity

**Why it matters:**
Incorrect color space causes incorrect lighting calculations. Always ensure:
- BaseColor textures have sRGB flag in engine
- Data textures (normal, roughness, etc.) use linear

**Three.js example:**
```javascript
baseColorTexture.colorSpace = THREE.SRGBColorSpace; // ✅ Correct
normalTexture.colorSpace = THREE.NoColorSpace;     // ✅ Correct (linear)
```

---

### Resolution Guidelines

**By channel importance:**

**Highest detail (1024-2048):**
- BaseColor (most visible)
- Normal (defines micro-detail)

**Medium detail (512-1024):**
- Roughness (specular breakup)
- Metallic (usually binary, less detail)

**Lower detail (512-1024):**
- AO (subtle effect)
- Emissive (often solid colors)

**Lowest detail (256-512):**
- Height (usually converted to normal)

**Web optimization:**
All channels can share the same resolution (1024×1024) for simplicity, but consider per-channel resizing for advanced optimization.

---

### File Format Selection

| Channel | Recommended Format | Reason |
|---------|-------------------|--------|
| **BaseColor** | JPEG (70-80%) or PNG-8 | Large file, compression acceptable |
| **Normal** | PNG-8 | Lossless required, compression breaks lighting |
| **Metallic** | PNG-8 | Binary data, lossless required |
| **Roughness** | PNG-8 | Subtle details, lossless preferred |
| **AO** | PNG-8 or JPEG (80%) | Subtle, can tolerate some compression |
| **Height** | PNG-16 | Benefits from higher bit depth |
| **Emissive** | PNG-8 (LDR) or EXR-32 (HDR) | HDR for bloom effects |
| **Opacity** | PNG-8 (with alpha) | Requires alpha channel |

---

### Texture Streaming & LOD

**Mipmaps:**
Always generate mipmaps for all textures. Engines generate automatically, but you can bake custom mipmaps in Substance for specific filtering.

**LOD strategy:**
Export multiple resolution sets:
- **LOD0** (close-up): 2048×2048
- **LOD1** (medium): 1024×1024
- **LOD2** (distant): 512×512

**Implementation (Three.js):**
```javascript
const lod = new THREE.LOD();
lod.addLevel(mesh_high_res, 0);    // 0-10 units
lod.addLevel(mesh_med_res, 10);    // 10-30 units
lod.addLevel(mesh_low_res, 30);    // 30+ units
```

## Common Material Types

### Plastic

**BaseColor:**
- Saturated colors (RGB 180, 60, 40 for red plastic)
- Consistent across surface

**Metallic:** 0 (non-metal)

**Roughness:**
- Glossy plastic: 30-50
- Matte plastic: 150-200

**Example (Three.js):**
```javascript
material.color = new THREE.Color(0xb43c28); // Orange plastic
material.metalness = 0.0;
material.roughness = 0.3; // Glossy
```

---

### Brushed Metal

**BaseColor:**
- Metal reflectance value (e.g., Aluminum: #F5F6F6)

**Metallic:** 255 (full metal)

**Roughness:**
- Directional variation (brush lines)
- 40-80 depending on finish

**Special:** Add anisotropic roughness for realistic brushed look (advanced shaders)

---

### Wood

**BaseColor:**
- Natural wood colors (browns, tans)
- Wood grain texture
- RGB 90-150 range

**Metallic:** 0 (non-metal)

**Roughness:**
- Unfinished: 150-200
- Varnished: 40-80
- Add variation (grain roughness differs)

**AO:** Cavity detail in grain

---

### Glass

**BaseColor:**
- Slight tint (RGB 245, 245, 245 for clear)

**Metallic:** 0

**Roughness:**
- Clean glass: 0-10
- Frosted glass: 100-200

**Opacity:** 20-50 (mostly transparent)

**Special:** Use refraction in engine (`transmission` in Three.js)

---

### Fabric

**BaseColor:**
- Fabric color with weave detail
- Medium values (RGB 80-180)

**Metallic:** 0

**Roughness:** 180-220 (very rough)

**Normal:** Weave/fiber details

**Special:** Consider subsurface scattering for translucent fabrics

---

### Rusty Metal

**BaseColor:**
- Clean metal: Metal reflectance
- Rust: Orange-brown (RGB 150, 80, 40)
- Use mask to blend

**Metallic:**
- Clean metal: 255
- Rust (iron oxide): 0
- Use same mask as baseColor

**Roughness:**
- Clean metal: 30-50
- Rust: 180-220

**Example mask-based blend:**
```python
# In Substance, use rust mask to drive:
# - BaseColor: Metal color → Rust color
# - Metallic: 255 → 0
# - Roughness: 40 → 200
```

## Validation Checklist

Before exporting, verify:

**BaseColor:**
- [ ] No baked lighting/shadows
- [ ] Values within plausible range (30-240 for most materials)
- [ ] Metals use actual metal reflectance colors

**Normal:**
- [ ] Correct format (OpenGL vs. DirectX)
- [ ] No compression artifacts (PNG only)
- [ ] Blue channel dominant

**Metallic:**
- [ ] Binary values (0 or 255 only)
- [ ] Matches material type (0 for dielectrics)

**Roughness:**
- [ ] Has surface variation (not uniform)
- [ ] Within realistic range for material

**All Maps:**
- [ ] Correct color space (sRGB vs. linear)
- [ ] Appropriate resolution (not oversized)
- [ ] Proper file format (lossless for data, JPEG for color)
- [ ] Padding set to "infinite" (no seams)

## Resources

- **PBR Guide:** https://academy.substance3d.com/courses/the-pbr-guide-part-1
- **Material Values:** https://docs.unrealengine.com/en-US/Resources/ContentExamples/MaterialProperties/
- **Texture Naming:** glTF 2.0 specification



===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/references/python_api_reference.md =====

# Substance 3D Painter Python API Reference

Complete reference for automating Substance 3D Painter workflows with Python.

## API Overview

The Substance 3D Painter Python API provides programmatic access to:
- **Export System** - Texture export configuration and execution
- **Project Management** - Open, save, close projects
- **Texture Sets** - Access and modify texture sets
- **Resource Management** - Access materials, brushes, presets
- **Event System** - React to application events
- **UI System** - Add custom menu items and dialogs

## Core Modules

### substance_painter.export

Texture export functionality.

#### Functions

**export_project_textures(json_config: dict) → ExportResult**

Exports project textures according to JSON configuration.

**Parameters:**
- `json_config` (dict) - Export configuration object

**Returns:**
- `ExportResult` with status, message, and list of exported files

**Raises:**
- `ProjectError` - No project is open
- `ValueError` - Invalid configuration

**Example:**
```python
import substance_painter.export

config = {
    "exportPath": "C:/export",
    "defaultExportPreset": "starter_assets://PBR Metallic Roughness",
    "exportList": [{"rootPath": "TextureSetName"}],
    "exportParameters": [{
        "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
        }
    }]
}

result = substance_painter.export.export_project_textures(config)

if result.status == substance_painter.export.ExportStatus.Success:
    print(f"Exported {len(result.textures)} texture sets")
```

---

**list_project_textures(json_config: dict) → Dict[Tuple[str, str], List[str]]**

Lists textures that would be exported without actually exporting.

**Parameters:**
- `json_config` (dict) - Export configuration

**Returns:**
- Dictionary mapping (texture_set, stack) to list of file paths

**Example:**
```python
texture_list = substance_painter.export.list_project_textures(config)

for stack, files in texture_list.items():
    print(f"Stack {stack}:")
    for file in files:
        print(f"  - {file}")
```

#### Classes

**ExportStatus (Enum)**

Export operation status codes:
- `Success` - Export completed successfully
- `Error` - Export failed

**ExportResult**

Result object returned by `export_project_textures()`.

**Attributes:**
- `status` (ExportStatus) - Status code
- `message` (str) - Human-readable status message
- `textures` (Dict[Tuple[str, str], List[str]]) - Exported files grouped by stack

#### Events

**ExportTexturesAboutToStart**

Triggered before export begins.

**Attributes:**
- `textures` (Dict[Tuple[str, str], List[str]]) - Files to be exported

**Example:**
```python
import substance_painter.event

def on_export_start(event):
    print(f"Exporting {len(event.textures)} texture sets")

substance_painter.event.DISPATCHER.connect(
    substance_painter.event.ExportTexturesAboutToStart,
    on_export_start
)
```

**ExportTexturesEnded**

Triggered after export completes.

**Attributes:**
- `status` (ExportStatus) - Export status
- `message` (str) - Status message
- `textures` (Dict[Tuple[str, str], List[str]]) - Exported files

### substance_painter.project

Project management operations.

#### Functions

**is_open() → bool**

Check if a project is currently open.

**Example:**
```python
if substance_painter.project.is_open():
    print("Project is open")
```

---

**open(file_path: str) → None**

Open an existing Substance project (.spp).

**Parameters:**
- `file_path` (str) - Absolute path to .spp file

**Example:**
```python
substance_painter.project.open("C:/projects/MyProject.spp")
```

---

**save() → None**

Save the current project.

---

**save_as(file_path: str) → None**

Save project to a new file path.

---

**close() → None**

Close the current project.

---

**file_path() → str**

Get the current project's file path.

**Returns:**
- Absolute path to .spp file, or empty string if no project open

**Example:**
```python
project_path = substance_painter.project.file_path()
export_path = project_path.replace('.spp', '_textures')
```

---

**name() → str**

Get the current project's name (filename without extension).

#### Events

**ProjectOpened**

Triggered when a project is opened.

**ProjectAboutToClose**

Triggered before project closes.

**ProjectAboutToSave**

Triggered before project saves.

**ProjectSaved**

Triggered after project saves.

**Example: Auto-export on save**
```python
import substance_painter.event
import substance_painter.project
import substance_painter.export

def auto_export(event):
    if not substance_painter.project.is_open():
        return

    # Export textures when project saves
    config = {
        "exportPath": substance_painter.project.file_path().replace('.spp', '_export'),
        # ... rest of config
    }
    substance_painter.export.export_project_textures(config)

substance_painter.event.DISPATCHER.connect(
    substance_painter.event.ProjectSaved,
    auto_export
)
```

### substance_painter.textureset

Access texture sets and UV tiles.

#### Functions

**all_texture_sets() → List[TextureSet]**

Get all texture sets in the project.

**Returns:**
- List of TextureSet objects

**Example:**
```python
import substance_painter.textureset

for ts in substance_painter.textureset.all_texture_sets():
    print(f"Texture Set: {ts.name()}")
    print(f"  Layered: {ts.is_layered_material()}")
    print(f"  Resolution: {ts.get_resolution()}")
```

---

**all_uv_tiles() → List[UVTile]**

Get all UV tiles in the project (for UDIM workflows).

**Returns:**
- List of UVTile objects

**Example:**
```python
for tile in substance_painter.textureset.all_uv_tiles():
    print(f"Tile ({tile.u}, {tile.v}): {tile.get_resolution()}")
```

---

**set_uvtiles_resolution(resolutions: Dict[UVTile, Resolution]) → None**

Set resolution for multiple UV tiles.

**Parameters:**
- `resolutions` (dict) - Mapping of UVTile to Resolution

**Example:**
```python
from substance_painter.textureset import Resolution

# Set all tiles in first row to 2K
row0 = [tile for tile in all_uv_tiles() if tile.v == 0]
resolution_2k = Resolution(2048, 2048)
substance_painter.textureset.set_uvtiles_resolution({
    tile: resolution_2k for tile in row0
})
```

#### Classes

**TextureSet**

Represents a texture set (material slot).

**Methods:**
- `name() → str` - Get texture set name
- `is_layered_material() → bool` - Check if uses layer stacks
- `get_resolution() → Resolution` - Get texture resolution
- `get_stack() → Stack` - Get layer stack (if layered)

**Stack**

Represents a layer stack in a texture set.

**Methods:**
- `material() → TextureSet` - Get parent texture set
- `get_channel(channel_type: ChannelType) → Channel` - Get specific channel

**Channel**

Represents a texture channel (baseColor, normal, etc.).

**Methods:**
- `is_color() → bool` - Check if channel contains color data

**ChannelType (Enum)**

Available texture channels:
- `BaseColor`
- `Normal`
- `Metallic`
- `Roughness`
- `Height`
- `Opacity`
- `Emissive`
- `AmbientOcclusion`

**Resolution**

Texture resolution container.

**Attributes:**
- `width` (int) - Width in pixels
- `height` (int) - Height in pixels

**Constructor:**
```python
from substance_painter.textureset import Resolution

res = Resolution(2048, 2048)  # 2K
```

**UVTile**

Represents a UV tile in UDIM workflow.

**Attributes:**
- `u` (int) - U coordinate (0-based)
- `v` (int) - V coordinate (0-based)

**Methods:**
- `get_resolution() → Resolution` - Get tile resolution
- `set_resolution(resolution: Resolution) → None` - Set tile resolution

### substance_painter.resource

Access and manage resources (materials, brushes, presets).

#### Classes

**ResourceID**

Identifier for a resource.

**Constructor:**
```python
resource = substance_painter.resource.ResourceID(
    context="starter_assets",  # Library name
    name="PBR Metallic Roughness"  # Resource name
)
```

**Methods:**
- `url() → str` - Get resource URL (e.g., "starter_assets://PBR Metallic Roughness")

**Example: Use export preset**
```python
export_preset = substance_painter.resource.ResourceID(
    context="starter_assets",
    name="Unity HDRP (Lit)"
)

config = {
    "defaultExportPreset": export_preset.url(),
    # ...
}
```

### substance_painter.ui

UI customization and menu integration.

#### Enums

**ApplicationMenu**

Available application menus:
- `File`
- `Edit`
- `Mode`
- `View`
- `Viewport`
- `Shader`
- `Window`
- `Help`

#### Functions

**add_action(menu: ApplicationMenu, action: QtWidgets.QAction) → None**

Add menu item to application menu.

**Parameters:**
- `menu` (ApplicationMenu) - Target menu
- `action` (QAction) - Qt action to add

**Example:**
```python
from PySide2 import QtWidgets
import substance_painter.ui

def my_function():
    print("Menu item clicked!")

action = QtWidgets.QAction("My Custom Command", triggered=my_function)
substance_painter.ui.add_action(substance_painter.ui.ApplicationMenu.File, action)
```

---

**delete_ui_element(element) → None**

Remove UI element (cleanup when plugin closes).

---

**get_main_window() → QtWidgets.QMainWindow**

Get main application window (for parenting dialogs).

**Example: File dialog**
```python
from PySide2 import QtWidgets

export_path = QtWidgets.QFileDialog.getExistingDirectory(
    substance_painter.ui.get_main_window(),
    "Choose export directory"
)
```

### substance_painter.event

Event system for reacting to application events.

#### Event Dispatcher

**DISPATCHER**

Global event dispatcher object.

**Methods:**
- `connect(event_type, callback)` - Register event handler
- `disconnect(event_type, callback)` - Unregister event handler

**Example:**
```python
import substance_painter.event

def on_project_opened(event):
    print("Project opened!")

substance_painter.event.DISPATCHER.connect(
    substance_painter.event.ProjectOpened,
    on_project_opened
)
```

#### Available Events

**Project Events:**
- `ProjectOpened`
- `ProjectAboutToClose`
- `ProjectAboutToSave`
- `ProjectSaved`

**Export Events:**
- `ExportTexturesAboutToStart`
- `ExportTexturesEnded`

**Shader Events:**
- `ShaderAdded`
- `ShaderRemoved`

**Texture Set Events:**
- `TextureSetAdded`
- `TextureSetRemoved`

## Export Configuration Schema

Complete JSON schema for `export_project_textures()` config parameter.

### Root Configuration Object

```python
{
    "exportPath": str,              # Required: Output directory path
    "exportShaderParams": bool,     # Optional: Export shader params to JSON (default: false)
    "defaultExportPreset": str,     # Optional: Default preset URL
    "exportPresets": list,          # Optional: Custom export presets
    "exportList": list,             # Required: Texture sets to export
    "exportParameters": list        # Optional: Export parameter overrides
}
```

### Export List Item

```python
{
    "rootPath": str,                # Required: Texture set name (or "TextureSet/Stack" for layered)
    "exportPreset": str,            # Optional: Override preset for this item
    "filter": {                     # Optional: Filter which maps/tiles to export
        "outputMaps": list,         # List of map names (e.g., ["$textureSet_baseColor"])
        "uvTiles": list             # List of [u, v] tile coordinates (e.g., [[1,1], [1,2]])
    }
}
```

### Export Parameters Item

```python
{
    "filter": {                     # Optional: Match specific files
        "dataPaths": list,          # Texture set/stack names
        "outputMaps": list,         # Map name patterns
        "uvTiles": list             # UV tile coordinates
    },
    "parameters": {                 # Optional: Override export settings
        "fileFormat": str,          # "png", "jpeg", "tga", "exr", etc.
        "bitDepth": str,            # "8", "16", "32"
        "dithering": bool,          # Enable dithering
        "sizeLog2": int,            # Texture size: 9=512, 10=1024, 11=2048, 12=4096
        "paddingAlgorithm": str,    # "passthrough", "color", "transparent", "diffusion", "infinite"
        "dilationDistance": int     # Padding distance in pixels (required for some padding modes)
    }
}
```

### Custom Export Preset

```python
{
    "name": str,                    # Preset name
    "maps": [                       # List of texture maps to export
        {
            "fileName": str,        # Output filename pattern (e.g., "$textureSet_baseColor")
            "channels": [           # Channel mapping
                {
                    "destChannel": str,      # "R", "G", "B", "A"
                    "srcChannel": str,       # "R", "G", "B", "A"
                    "srcMapType": str,       # "documentMap"
                    "srcMapName": str        # "baseColor", "normal", "metallic", etc.
                }
            ],
            "parameters": {         # Optional: Per-map export parameters
                "fileFormat": str,
                "bitDepth": str,
                "sizeLog2": int
            }
        }
    ]
}
```

### Filename Patterns

Variables available in `fileName` patterns:
- `$textureSet` - Texture set name
- `$project` - Project name
- `$mesh` - Mesh name
- `$udim` - UDIM tile number (e.g., 1001)

**Examples:**
- `$textureSet_baseColor` → "MyAsset_baseColor.png"
- `$project_$textureSet_color` → "MyProject_MyAsset_color.png"

## Complete Examples

### Example 1: Basic Batch Export

Export all texture sets with standard settings:

```python
import substance_painter.export
import substance_painter.resource
import substance_painter.textureset

# Define preset
preset = substance_painter.resource.ResourceID(
    context="starter_assets",
    name="PBR Metallic Roughness"
)

# Build config
config = {
    "exportPath": "C:/export",
    "defaultExportPreset": preset.url(),
    "exportList": [
        {"rootPath": ts.name()}
        for ts in substance_painter.textureset.all_texture_sets()
    ],
    "exportParameters": [{
        "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10,
            "paddingAlgorithm": "infinite"
        }
    }]
}

# Export
result = substance_painter.export.export_project_textures(config)
print(f"Status: {result.status}")
```

### Example 2: Selective Export with Filters

Export only baseColor at high resolution, other maps at lower resolution:

```python
config = {
    "exportPath": "C:/export",
    "defaultExportPreset": preset.url(),
    "exportList": [{"rootPath": "CharacterBody"}],
    "exportParameters": [
        {
            "filter": {"outputMaps": ["$textureSet_baseColor"]},
            "parameters": {"sizeLog2": 12}  # 4096 for baseColor
        },
        {
            "filter": {"outputMaps": ["$textureSet_normal", "$textureSet_metallicRoughness"]},
            "parameters": {"sizeLog2": 11}  # 2048 for other maps
        }
    ]
}
```

### Example 3: Custom Preset with Channel Packing

Create ORM (Occlusion-Roughness-Metallic) packed texture:

```python
custom_preset = {
    "exportPresets": [{
        "name": "WebGL_ORM",
        "maps": [
            {
                "fileName": "$textureSet_baseColor",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                ]
            },
            {
                "fileName": "$textureSet_normal",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"}
                ]
            },
            {
                "fileName": "$textureSet_ORM",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "ambientOcclusion"},
                    {"destChannel": "G", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"},
                    {"destChannel": "B", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                ]
            }
        ]
    }]
}

config = {
    "exportPath": "C:/export",
    "exportPresets": custom_preset["exportPresets"],
    "exportList": [{"rootPath": "MyAsset", "exportPreset": "WebGL_ORM"}],
    "exportParameters": [{
        "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
    }]
}
```

### Example 4: UDIM Export

Export specific UV tiles with different resolutions:

```python
from substance_painter.textureset import Resolution

# Set tile 1001 to 4K, others to 2K
tile_1001 = next((t for t in all_uv_tiles() if t.u == 0 and t.v == 0), None)
if tile_1001:
    tile_1001.set_resolution(Resolution(4096, 4096))

config = {
    "exportPath": "C:/export",
    "defaultExportPreset": preset.url(),
    "exportList": [
        {
            "rootPath": "UDIMAsset",
            "filter": {"uvTiles": [[0, 0], [1, 0], [2, 0]]}  # Export first row
        }
    ]
}
```

## Plugin Development

### Creating a Plugin

**Directory structure:**
```
plugins/
└── my_plugin/
    ├── __init__.py
    └── plugin.py
```

**plugin.py:**
```python
import substance_painter.ui
from PySide2 import QtWidgets

plugin_widgets = []

def my_command():
    print("Plugin command executed!")

def start_plugin():
    """Called when plugin loads"""
    action = QtWidgets.QAction("My Command", triggered=my_command)
    substance_painter.ui.add_action(substance_painter.ui.ApplicationMenu.File, action)
    plugin_widgets.append(action)

def close_plugin():
    """Called when plugin unloads"""
    for widget in plugin_widgets:
        substance_painter.ui.delete_ui_element(widget)
    plugin_widgets.clear()

if __name__ == "__main__":
    start_plugin()
```

### Plugin Best Practices

1. **Store UI elements** in module-level list for cleanup
2. **Check project state** before operations:
   ```python
   if not substance_painter.project.is_open():
       return
   ```
3. **Handle errors gracefully**:
   ```python
   try:
       result = substance_painter.export.export_project_textures(config)
   except ValueError as e:
       print(f"Export failed: {e}")
   ```
4. **Use absolute paths** for file operations
5. **Clean up resources** in `close_plugin()`

## Troubleshooting

### Common Issues

**Import Error: No module named 'substance_painter'**
- API only available when running inside Substance 3D Painter
- Use File → Scripts → Run Script to execute Python code

**ProjectError: No project is open**
- Check `substance_painter.project.is_open()` before API calls

**ValueError: Invalid export configuration**
- Verify all required fields in export config
- Check `exportPath` exists and is writable
- Ensure `exportList` is not empty

**ResourceID not found**
- Verify `context` (library name) is correct
- Check resource `name` matches exactly (case-sensitive)
- Use Substance UI to find resource names

### Debugging Tips

**Print configuration:**
```python
import json
print(json.dumps(config, indent=2))
```

**List available texture sets:**
```python
for ts in substance_painter.textureset.all_texture_sets():
    print(f"Texture Set: {ts.name()}")
```

**Preview export list without exporting:**
```python
preview = substance_painter.export.list_project_textures(config)
for stack, files in preview.items():
    print(f"{stack}: {files}")
```

## Resources

- **Official Python API Docs:** https://helpx.adobe.com/substance-3d-painter-python/api/
- **Substance 3D Community:** https://community.adobe.com/t5/substance-3d-painter/ct-p/ct-substance-3d-painter
- **Python Plugin Examples:** Included in Substance installation under `python/examples/`



===== FILE: plugins/individual/substance-3d-texturing/agents/substance-3d-texturing-pipeline.md =====

# Substance 3D Pipeline Specialist

## Role

Expert pipeline specialist for Substance 3D workflows, asset optimization, and web integration.

## Expertise

- Asset export and optimization
- Web-ready format conversion
- Texture and material optimization
- Automated pipeline workflows
- Quality assurance and validation
- Cross-platform compatibility

## When to use

Activate this agent when working on:
- Asset export pipelines
- Batch processing workflows
- Optimization for web delivery
- Integration with web frameworks
- Automated quality checks

## Approach

1. Analyze asset requirements and constraints
2. Design optimal export pipeline
3. Implement automation scripts
4. Optimize for web performance
5. Validate output quality

## Tools

This agent has access to:
- Substance 3D skill knowledge
- Pipeline automation scripts
- Optimization guidelines
- Quality validation checklists



===== FILE: plugins/individual/substance-3d-texturing/commands/batch_export.md =====

# /substance-3d-texturing-batch_export

Substance 3D - Batch Export

## Description

Executes the batch_export script for Substance 3D.

## Usage

```bash
/substance-3d-texturing-batch_export
```

## Implementation

This command runs the `batch_export.py` script from the Substance 3D skill, which provides automated assistance for batch export.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/substance-3d-texturing/commands/generate_export_preset.md =====

# /substance-3d-texturing-generate_export_preset

Substance 3D - Generate Export Preset

## Description

Executes the generate_export_preset script for Substance 3D.

## Usage

```bash
/substance-3d-texturing-generate_export_preset
```

## Implementation

This command runs the `generate_export_preset.py` script from the Substance 3D skill, which provides automated assistance for generate export preset.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/substance-3d-texturing/commands/web_optimizer.md =====

# /substance-3d-texturing-web_optimizer

Substance 3D - Web Optimizer

## Description

Executes the web_optimizer script for Substance 3D.

## Usage

```bash
/substance-3d-texturing-web_optimizer
```

## Implementation

This command runs the `web_optimizer.py` script from the Substance 3D skill, which provides automated assistance for web optimizer.

## Notes

- This command leverages the skill's built-in automation scripts
- For interactive mode, the script will prompt for required information
- Check the skill documentation for detailed script usage



===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/scripts/batch_export.py =====

```py
#!/usr/bin/env python3
"""
Substance 3D Painter Batch Export Script

Exports all texture sets from the currently open Substance Painter project
using the PBR Metallic Roughness preset optimized for web.

Usage:
    # Run from Substance Painter: File → Python → Execute Script
    # Or load as plugin

Requirements:
    - Substance 3D Painter must be running
    - A project must be open
    - substance_painter module (available in Substance environment)

Example:
    import batch_export
    batch_export.export_all_web()

    # Or customize export path
    batch_export.export_all_web(export_path="C:/MyExports")
"""

try:
    import substance_painter.export
    import substance_painter.resource
    import substance_painter.textureset
    import substance_painter.project
except ImportError:
    print("ERROR: This script must be run inside Substance 3D Painter")
    print("Go to: File → Python → Execute Script")
    exit(1)


def export_all_web(export_path=None, resolution=1024):
    """
    Export all texture sets with web-optimized settings.

    Args:
        export_path (str): Output directory. If None, exports next to .spp file.
        resolution (int): Texture size (512, 1024, 2048, 4096).

    Returns:
        bool: True if export succeeded, False otherwise.
    """
    # Verify project is open
    if not substance_painter.project.is_open():
        print("ERROR: No project is open. Open a project first.")
        return False

    # Determine export path
    if export_path is None:
        project_path = substance_painter.project.file_path()
        if not project_path:
            print("ERROR: Project has no file path (save the project first)")
            return False
        export_path = project_path.replace('.spp', '_textures')

    print(f"Export directory: {export_path}")

    # Map resolution to sizeLog2
    size_map = {
        512: 9,
        1024: 10,
        2048: 11,
        4096: 12
    }

    if resolution not in size_map:
        print(f"ERROR: Invalid resolution {resolution}. Use 512, 1024, 2048, or 4096.")
        return False

    size_log2 = size_map[resolution]

    # Define export preset
    try:
        export_preset = substance_painter.resource.ResourceID(
            context="starter_assets",
            name="PBR Metallic Roughness"
        )
    except Exception as e:
        print(f"ERROR: Could not load export preset: {e}")
        return False

    # Build export configuration
    config = {
        "exportShaderParams": False,
        "exportPath": export_path,
        "defaultExportPreset": export_preset.url(),
        "exportList": [],
        "exportParameters": [{
            "parameters": {
                "fileFormat": "png",
                "bitDepth": "8",
                "dithering": True,
                "paddingAlgorithm": "infinite",
                "sizeLog2": size_log2
            }
        }]
    }

    # Add all texture sets to export list
    texture_sets = substance_painter.textureset.all_texture_sets()

    if not texture_sets:
        print("WARNING: No texture sets found in project")
        return False

    for texture_set in texture_sets:
        config["exportList"].append({
            "rootPath": texture_set.name()
        })
        print(f"Added to export queue: {texture_set.name()}")

    print(f"\nExporting {len(texture_sets)} texture set(s) at {resolution}×{resolution}...")

    # Execute export
    try:
        result = substance_painter.export.export_project_textures(config)

        if result.status == substance_painter.export.ExportStatus.Success:
            print("\n✓ Export completed successfully!")
            print(f"\nExported textures:")

            total_files = 0
            for stack, files in result.textures.items():
                print(f"\n  {stack}:")
                for file_path in files:
                    print(f"    - {file_path}")
                    total_files += 1

            print(f"\nTotal files exported: {total_files}")
            return True
        else:
            print(f"\n✗ Export failed: {result.message}")
            return False

    except ValueError as e:
        print(f"\n✗ Export configuration error: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error during export: {e}")
        return False


def export_mobile_optimized(export_path=None):
    """
    Export with aggressive mobile optimization.

    Features:
    - 512×512 resolution
    - JPEG for baseColor (smaller file size)
    - PNG for data maps (lossless required)

    Args:
        export_path (str): Output directory. If None, exports to project_mobile/.

    Returns:
        bool: True if export succeeded, False otherwise.
    """
    if not substance_painter.project.is_open():
        print("ERROR: No project is open.")
        return False

    # Determine export path
    if export_path is None:
        project_path = substance_painter.project.file_path()
        if not project_path:
            print("ERROR: Project has no file path (save the project first)")
            return False
        export_path = project_path.replace('.spp', '_mobile')

    print(f"Mobile export directory: {export_path}")

    # Define export preset
    export_preset = substance_painter.resource.ResourceID(
        context="starter_assets",
        name="PBR Metallic Roughness"
    )

    # Build export configuration with mobile optimizations
    config = {
        "exportShaderParams": False,
        "exportPath": export_path,
        "defaultExportPreset": export_preset.url(),
        "exportList": [],
        "exportParameters": [
            {
                # Default: JPEG for baseColor
                "filter": {"outputMaps": ["$textureSet_baseColor"]},
                "parameters": {
                    "fileFormat": "jpeg",
                    "bitDepth": "8",
                    "sizeLog2": 9,  # 512×512
                    "paddingAlgorithm": "infinite"
                }
            },
            {
                # PNG for normal and metallicRoughness (data maps need lossless)
                "filter": {"outputMaps": ["$textureSet_normal", "$textureSet_metallicRoughness"]},
                "parameters": {
                    "fileFormat": "png",
                    "bitDepth": "8",
                    "sizeLog2": 9,  # 512×512
                    "paddingAlgorithm": "infinite"
                }
            }
        ]
    }

    # Add all texture sets
    for texture_set in substance_painter.textureset.all_texture_sets():
        config["exportList"].append({"rootPath": texture_set.name()})

    print(f"Exporting {len(substance_painter.textureset.all_texture_sets())} texture set(s) for mobile...")

    # Execute export
    try:
        result = substance_painter.export.export_project_textures(config)

        if result.status == substance_painter.export.ExportStatus.Success:
            print("\n✓ Mobile export completed!")
            return True
        else:
            print(f"\n✗ Export failed: {result.message}")
            return False

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def print_texture_sets():
    """Print all texture sets in the current project."""
    if not substance_painter.project.is_open():
        print("No project is open.")
        return

    texture_sets = substance_painter.textureset.all_texture_sets()

    if not texture_sets:
        print("No texture sets found in project.")
        return

    print(f"\nFound {len(texture_sets)} texture set(s):\n")

    for i, ts in enumerate(texture_sets, 1):
        print(f"{i}. {ts.name()}")
        print(f"   Layered: {ts.is_layered_material()}")
        resolution = ts.get_resolution()
        print(f"   Resolution: {resolution.width}×{resolution.height}")
        print()


def main():
    """Main entry point when script is executed directly."""
    print("=" * 60)
    print("Substance 3D Painter - Batch Export Script")
    print("=" * 60)

    if not substance_painter.project.is_open():
        print("\nERROR: No project is open.")
        print("Please open a Substance Painter project first.")
        return

    # Show project info
    project_name = substance_painter.project.name()
    print(f"\nProject: {project_name}")

    # Show texture sets
    print_texture_sets()

    # Perform export
    print("Starting web export (1024×1024)...")
    success = export_all_web(resolution=1024)

    if success:
        print("\n" + "=" * 60)
        print("Export complete! Check the output directory.")
        print("=" * 60)
    else:
        print("\nExport failed. See errors above.")


if __name__ == "__main__":
    main()

```


===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/scripts/generate_export_preset.py =====

```py
#!/usr/bin/env python3
"""
Substance 3D Painter Export Preset Generator

Interactive tool for creating custom export preset JSON configurations.

Usage:
    # Interactive mode
    ./generate_export_preset.py

    # Quick presets
    ./generate_export_preset.py --preset gltf
    ./generate_export_preset.py --preset threejs
    ./generate_export_preset.py --preset orm

    # Output to file
    ./generate_export_preset.py --preset gltf --output my_preset.json

Presets:
    - gltf: glTF 2.0 standard (MetallicRoughness)
    - threejs: Three.js optimized (separate channels)
    - babylonjs: Babylon.js PBR format
    - orm: Occlusion-Roughness-Metallic packed
    - mobile: Mobile-optimized (512px, JPEG color)

Requirements:
    - Python 3.6+
    - Standard library only
"""

import json
import sys
import argparse


# Preset templates
PRESETS = {
    'gltf': {
        "exportPresets": [{
            "name": "glTF_Standard",
            "maps": [
                {
                    "fileName": "$textureSet_baseColor",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                        {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                    ],
                    "parameters": {
                        "fileFormat": "png",
                        "bitDepth": "8",
                        "sizeLog2": 10
                    }
                },
                {
                    "fileName": "$textureSet_normal",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
                        {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                },
                {
                    "fileName": "$textureSet_metallicRoughness",
                    "channels": [
                        {"destChannel": "G", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"},
                        {"destChannel": "B", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                }
            ]
        }]
    },

    'threejs': {
        "exportPresets": [{
            "name": "ThreeJS_Standard",
            "maps": [
                {
                    "fileName": "$textureSet_color",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                        {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                    ],
                    "parameters": {"fileFormat": "jpeg", "bitDepth": "8", "sizeLog2": 10}
                },
                {
                    "fileName": "$textureSet_normal",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
                        {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                },
                {
                    "fileName": "$textureSet_ao",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "ambientOcclusion"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                },
                {
                    "fileName": "$textureSet_metalness",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                },
                {
                    "fileName": "$textureSet_roughness",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                }
            ]
        }]
    },

    'babylonjs': {
        "exportPresets": [{
            "name": "BabylonJS_PBR",
            "maps": [
                {
                    "fileName": "$textureSet_albedo",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                        {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                },
                {
                    "fileName": "$textureSet_normal",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
                        {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                },
                {
                    "fileName": "$textureSet_metallicRoughness",
                    "channels": [
                        {"destChannel": "G", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"},
                        {"destChannel": "B", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                }
            ]
        }]
    },

    'orm': {
        "exportPresets": [{
            "name": "Web_ORM",
            "maps": [
                {
                    "fileName": "$textureSet_baseColor",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                        {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                },
                {
                    "fileName": "$textureSet_normal",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"},
                        {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "normal"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                },
                {
                    "fileName": "$textureSet_ORM",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "ambientOcclusion"},
                        {"destChannel": "G", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"},
                        {"destChannel": "B", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
                }
            ]
        }]
    },

    'mobile': {
        "exportPresets": [{
            "name": "Mobile_WebGL",
            "maps": [
                {
                    "fileName": "$textureSet_color",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "baseColor"},
                        {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "baseColor"}
                    ],
                    "parameters": {"fileFormat": "jpeg", "bitDepth": "8", "sizeLog2": 9}
                },
                {
                    "fileName": "$textureSet_normal",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "normal"},
                        {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "normal"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 9}
                },
                {
                    "fileName": "$textureSet_packed",
                    "channels": [
                        {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "ambientOcclusion"},
                        {"destChannel": "G", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "roughness"},
                        {"destChannel": "B", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "metallic"}
                    ],
                    "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 9}
                }
            ]
        }]
    }
}


def print_preset_info(preset_name):
    """Print information about a preset."""
    descriptions = {
        'gltf': "glTF 2.0 standard format with MetallicRoughness packing (OpenGL normals)",
        'threejs': "Three.js optimized with separate channels and JPEG color",
        'babylonjs': "Babylon.js PBR format with MetallicRoughness packing",
        'orm': "Occlusion-Roughness-Metallic packed format (most efficient)",
        'mobile': "Mobile-optimized with 512px resolution and aggressive compression"
    }

    if preset_name in descriptions:
        print(f"\n{preset_name.upper()} Preset:")
        print(f"  {descriptions[preset_name]}")


def generate_preset_json(preset_name):
    """Generate preset JSON configuration."""
    if preset_name not in PRESETS:
        print(f"ERROR: Unknown preset '{preset_name}'")
        print(f"Available presets: {', '.join(PRESETS.keys())}")
        return None

    return PRESETS[preset_name]


def print_usage_example(preset_name, output_file=None):
    """Print usage example for the generated preset."""
    print("\n" + "=" * 60)
    print("USAGE EXAMPLE (Python)")
    print("=" * 60)

    if output_file:
        print(f"""
import json
import substance_painter.export

# Load custom preset
with open('{output_file}', 'r') as f:
    custom_preset = json.load(f)

config = {{
    "exportPath": "C:/export",
    "exportPresets": custom_preset["exportPresets"],
    "exportList": [{{"rootPath": "MyAsset", "exportPreset": "{PRESETS[preset_name]['exportPresets'][0]['name']}"}}],
    "exportParameters": [{{
        "parameters": {{"paddingAlgorithm": "infinite"}}
    }}]
}}

result = substance_painter.export.export_project_textures(config)
""")
    else:
        print(f"""
import substance_painter.export

preset = {json.dumps(PRESETS[preset_name], indent=2)}

config = {{
    "exportPath": "C:/export",
    "exportPresets": preset["exportPresets"],
    "exportList": [{{"rootPath": "MyAsset", "exportPreset": "{PRESETS[preset_name]['exportPresets'][0]['name']}"}}]
}}

result = substance_painter.export.export_project_textures(config)
""")


def interactive_mode():
    """Interactive preset builder."""
    print("=" * 60)
    print("Substance 3D Painter - Export Preset Generator")
    print("=" * 60)

    print("\nAvailable presets:\n")

    for i, (name, _) in enumerate(PRESETS.items(), 1):
        print(f"{i}. {name}")
        print_preset_info(name)

    print()

    while True:
        try:
            choice = input("Select preset (1-5) or 'q' to quit: ").strip()

            if choice.lower() == 'q':
                sys.exit(0)

            preset_index = int(choice) - 1
            preset_names = list(PRESETS.keys())

            if 0 <= preset_index < len(preset_names):
                preset_name = preset_names[preset_index]
                break
            else:
                print("Invalid selection. Try again.")

        except ValueError:
            print("Invalid input. Enter a number 1-5.")
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(0)

    # Generate preset
    preset_json = generate_preset_json(preset_name)

    print("\n" + "=" * 60)
    print(f"Generated {preset_name.upper()} Preset")
    print("=" * 60)
    print(json.dumps(preset_json, indent=2))

    # Ask to save
    save = input("\nSave to file? (y/n): ").strip().lower()

    if save == 'y':
        filename = input("Enter filename (default: export_preset.json): ").strip()
        if not filename:
            filename = "export_preset.json"

        if not filename.endswith('.json'):
            filename += '.json'

        with open(filename, 'w') as f:
            json.dump(preset_json, f, indent=2)

        print(f"\n✓ Preset saved to: {filename}")
        print_usage_example(preset_name, filename)
    else:
        print_usage_example(preset_name)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate custom Substance 3D Painter export presets"
    )

    parser.add_argument(
        '--preset',
        choices=list(PRESETS.keys()),
        help="Preset type (gltf, threejs, babylonjs, orm, mobile)"
    )

    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help="Output JSON file path"
    )

    args = parser.parse_args()

    # Interactive mode if no preset specified
    if args.preset is None:
        interactive_mode()
        return

    # Generate preset
    preset_json = generate_preset_json(args.preset)

    if preset_json is None:
        sys.exit(1)

    # Output to file or stdout
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(preset_json, f, indent=2)

        print(f"✓ {args.preset.upper()} preset saved to: {args.output_file}")
        print_usage_example(args.preset, args.output_file)
    else:
        print(json.dumps(preset_json, indent=2))
        print_usage_example(args.preset)


if __name__ == "__main__":
    main()

```


===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/scripts/web_optimizer.py =====

```py
#!/usr/bin/env python3
"""
Web Texture Optimizer

Post-processes exported textures from Substance 3D Painter for optimal web delivery.
Performs resizing, format conversion, and reports file size savings.

Features:
- Resize textures to target resolution
- Convert baseColor to JPEG (lossy compression)
- Keep data maps as PNG (lossless)
- Generate multiple LOD levels
- Report file size savings

Usage:
    ./web_optimizer.py <input_directory> [options]

    ./web_optimizer.py C:/exports/MyAsset --resolution 1024
    ./web_optimizer.py C:/exports/MyAsset --lod 3
    ./web_optimizer.py C:/exports/MyAsset --jpeg-quality 80

Requirements:
    - Python 3.6+
    - Pillow library (optional, for image processing)
      Install: pip install Pillow
    - If Pillow not available, provides instructions for manual optimization

Note:
    This script uses only standard library when Pillow is not installed.
    With Pillow, it can perform automatic image processing.
"""

import os
import sys
import argparse
from pathlib import Path


def check_pillow():
    """Check if Pillow is installed."""
    try:
        from PIL import Image
        return True
    except ImportError:
        return False


def get_file_size_mb(file_path):
    """Get file size in MB."""
    return os.path.getsize(file_path) / (1024 * 1024)


def resize_texture(input_path, output_path, target_size, quality=85):
    """
    Resize texture and optionally convert format.

    Args:
        input_path (str): Input image path
        output_path (str): Output image path
        target_size (int): Target resolution (width = height)
        quality (int): JPEG quality (1-100)

    Returns:
        bool: Success
    """
    try:
        from PIL import Image

        img = Image.open(input_path)

        # Resize with high-quality resampling
        resized = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

        # Save with appropriate settings
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            resized.save(output_path, 'JPEG', quality=quality, optimize=True)
        elif output_path.lower().endswith('.png'):
            resized.save(output_path, 'PNG', optimize=True)
        else:
            resized.save(output_path)

        return True

    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


def analyze_directory(input_dir):
    """
    Analyze texture directory and categorize files.

    Args:
        input_dir (str): Input directory path

    Returns:
        dict: Categorized texture files
    """
    textures = {
        'baseColor': [],
        'normal': [],
        'metallicRoughness': [],
        'emissive': [],
        'other': []
    }

    for file_path in Path(input_dir).glob('*.png'):
        file_name = file_path.name.lower()

        if 'basecolor' in file_name or '_color' in file_name or '_diffuse' in file_name:
            textures['baseColor'].append(file_path)
        elif 'normal' in file_name:
            textures['normal'].append(file_path)
        elif 'metallic' in file_name or 'roughness' in file_name:
            textures['metallicRoughness'].append(file_path)
        elif 'emissive' in file_name:
            textures['emissive'].append(file_path)
        else:
            textures['other'].append(file_path)

    # Also check for existing JPEGs
    for file_path in Path(input_dir).glob('*.jpg'):
        textures['baseColor'].append(file_path)

    return textures


def optimize_directory(input_dir, output_dir, target_resolution=1024, jpeg_quality=80):
    """
    Optimize all textures in a directory.

    Args:
        input_dir (str): Input directory
        output_dir (str): Output directory
        target_resolution (int): Target texture size
        jpeg_quality (int): JPEG quality (1-100)

    Returns:
        dict: Optimization statistics
    """
    if not check_pillow():
        print("ERROR: Pillow library not installed.")
        print("Install with: pip install Pillow")
        print("\nAlternatively, use manual optimization tools:")
        print("  - ImageMagick: convert input.png -resize 1024x1024 output.png")
        print("  - pngquant: pngquant --quality 80-100 input.png")
        print("  - TinyPNG: https://tinypng.com/")
        return None

    from PIL import Image

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Analyze input directory
    textures = analyze_directory(input_dir)

    stats = {
        'files_processed': 0,
        'original_size_mb': 0,
        'optimized_size_mb': 0
    }

    print(f"\nOptimizing textures to {target_resolution}×{target_resolution}...")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}\n")

    # Process baseColor textures (convert to JPEG)
    for file_path in textures['baseColor']:
        original_size = get_file_size_mb(file_path)
        stats['original_size_mb'] += original_size

        output_name = file_path.stem + '.jpg'
        output_path = os.path.join(output_dir, output_name)

        print(f"Processing {file_path.name} → {output_name} (JPEG {jpeg_quality}%)")

        if resize_texture(str(file_path), output_path, target_resolution, jpeg_quality):
            optimized_size = get_file_size_mb(output_path)
            stats['optimized_size_mb'] += optimized_size
            stats['files_processed'] += 1

            savings = ((original_size - optimized_size) / original_size) * 100
            print(f"  {original_size:.2f} MB → {optimized_size:.2f} MB (-{savings:.1f}%)\n")

    # Process data maps (keep as PNG)
    for category in ['normal', 'metallicRoughness', 'emissive', 'other']:
        for file_path in textures[category]:
            original_size = get_file_size_mb(file_path)
            stats['original_size_mb'] += original_size

            output_name = file_path.name
            output_path = os.path.join(output_dir, output_name)

            print(f"Processing {file_path.name} (PNG)")

            if resize_texture(str(file_path), output_path, target_resolution):
                optimized_size = get_file_size_mb(output_path)
                stats['optimized_size_mb'] += optimized_size
                stats['files_processed'] += 1

                savings = ((original_size - optimized_size) / original_size) * 100
                print(f"  {original_size:.2f} MB → {optimized_size:.2f} MB (-{savings:.1f}%)\n")

    return stats


def generate_lod_levels(input_dir, output_base_dir, levels=3):
    """
    Generate multiple LOD levels from input textures.

    Args:
        input_dir (str): Input directory with original textures
        output_base_dir (str): Base output directory
        levels (int): Number of LOD levels (1-4)

    Returns:
        bool: Success
    """
    if not check_pillow():
        print("ERROR: Pillow library required for LOD generation.")
        return False

    # LOD resolution mapping
    lod_resolutions = {
        0: 2048,  # LOD0 - highest detail
        1: 1024,  # LOD1 - medium detail
        2: 512,   # LOD2 - low detail
        3: 256    # LOD3 - very low detail
    }

    print(f"\nGenerating {levels} LOD level(s)...\n")

    for lod in range(levels):
        resolution = lod_resolutions[lod]
        output_dir = os.path.join(output_base_dir, f'LOD{lod}')

        print(f"LOD{lod}: {resolution}×{resolution}")
        print(f"Output: {output_dir}\n")

        stats = optimize_directory(input_dir, output_dir, resolution)

        if stats:
            print(f"LOD{lod} complete: {stats['files_processed']} files")
            print(f"Total size: {stats['optimized_size_mb']:.2f} MB\n")
            print("-" * 60 + "\n")

    return True


def print_manual_instructions(input_dir):
    """Print manual optimization instructions when Pillow is not available."""
    print("\n" + "=" * 60)
    print("MANUAL OPTIMIZATION INSTRUCTIONS")
    print("=" * 60)
    print("\nSince Pillow is not installed, use these tools:\n")

    print("1. ImageMagick (batch processing):")
    print("   # Resize to 1024×1024")
    print(f"   for file in {input_dir}/*.png; do")
    print("     convert \"$file\" -resize 1024x1024 \"optimized_$(basename $file)\"")
    print("   done\n")

    print("2. pngquant (PNG compression):")
    print("   # Compress PNGs (lossy but smaller)")
    print(f"   pngquant --quality 80-100 {input_dir}/*.png\n")

    print("3. cwebp (WebP conversion - best for web):")
    print("   # Convert to WebP (90% smaller than PNG)")
    print(f"   for file in {input_dir}/*_baseColor.png; do")
    print("     cwebp -q 80 \"$file\" -o \"$(basename $file .png).webp\"")
    print("   done\n")

    print("4. Online tools:")
    print("   - TinyPNG: https://tinypng.com/")
    print("   - Squoosh: https://squoosh.app/")
    print("\n" + "=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Optimize Substance 3D Painter textures for web delivery"
    )

    parser.add_argument(
        'input_dir',
        help="Input directory containing exported textures"
    )

    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        help="Output directory (default: input_dir_optimized)"
    )

    parser.add_argument(
        '-r', '--resolution',
        type=int,
        default=1024,
        choices=[256, 512, 1024, 2048, 4096],
        help="Target resolution (default: 1024)"
    )

    parser.add_argument(
        '-q', '--jpeg-quality',
        type=int,
        default=80,
        choices=range(1, 101),
        metavar='1-100',
        help="JPEG quality for baseColor (default: 80)"
    )

    parser.add_argument(
        '--lod',
        type=int,
        choices=[1, 2, 3, 4],
        help="Generate LOD levels (1-4)"
    )

    args = parser.parse_args()

    # Validate input directory
    if not os.path.isdir(args.input_dir):
        print(f"ERROR: Input directory not found: {args.input_dir}")
        sys.exit(1)

    # Determine output directory
    if args.output_dir is None:
        args.output_dir = args.input_dir + '_optimized'

    print("=" * 60)
    print("Web Texture Optimizer")
    print("=" * 60)

    # Check if Pillow is available
    if not check_pillow():
        print("\nWARNING: Pillow library not installed.")
        print_manual_instructions(args.input_dir)
        sys.exit(1)

    # Generate LOD levels or single optimization
    if args.lod:
        success = generate_lod_levels(args.input_dir, args.output_dir, args.lod)
        if not success:
            sys.exit(1)
    else:
        stats = optimize_directory(
            args.input_dir,
            args.output_dir,
            args.resolution,
            args.jpeg_quality
        )

        if stats is None:
            sys.exit(1)

        # Print summary
        print("=" * 60)
        print("OPTIMIZATION SUMMARY")
        print("=" * 60)
        print(f"Files processed: {stats['files_processed']}")
        print(f"Original size: {stats['original_size_mb']:.2f} MB")
        print(f"Optimized size: {stats['optimized_size_mb']:.2f} MB")

        total_savings = stats['original_size_mb'] - stats['optimized_size_mb']
        savings_percent = (total_savings / stats['original_size_mb']) * 100

        print(f"Total savings: {total_savings:.2f} MB ({savings_percent:.1f}%)")
        print("=" * 60)

    print(f"\nOptimized textures saved to: {args.output_dir}")


if __name__ == "__main__":
    main()

```


===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/assets/README.md =====

# Substance 3D Texturing Assets

Pre-configured export preset templates for various web engines and platforms.

## Directory Structure

```
assets/
└── export_templates/
    ├── gltf_standard.json          # glTF 2.0 compliant preset
    ├── threejs_optimized.json      # Three.js with separate channels
    ├── babylonjs_pbr.json          # Babylon.js PBR format
    ├── web_orm_packed.json         # ORM channel packing
    └── mobile_webgl.json           # Mobile-optimized preset
```

## Usage

### Method 1: Copy Preset Configuration

Copy the JSON content from any template file and use directly in your Python script:

```python
import json
import substance_painter.export

# Load preset from file
with open('assets/export_templates/gltf_standard.json', 'r') as f:
    custom_preset = json.load(f)

config = {
    "exportPath": "C:/export",
    "exportPresets": custom_preset["exportPresets"],
    "exportList": [{"rootPath": "MyAsset", "exportPreset": "glTF_Standard"}],
    "exportParameters": [{
        "parameters": {"paddingAlgorithm": "infinite"}
    }]
}

result = substance_painter.export.export_project_textures(config)
```

### Method 2: Use Preset Generator Script

Generate presets programmatically:

```bash
# Generate glTF preset
.gemini/skills/substance-3d-texturing/scripts/generate_export_preset.py --preset gltf --output my_preset.json

# Interactive mode
.gemini/skills/substance-3d-texturing/scripts/generate_export_preset.py
```

## Preset Descriptions

### gltf_standard.json

**Format:** glTF 2.0 compliant
**Resolution:** 1024×1024
**Outputs:**
- `baseColor.png` - RGB base color (sRGB)
- `normal.png` - RGB normal map (OpenGL format)
- `metallicRoughness.png` - Packed: G=Roughness, B=Metallic

**Best for:**
- glTF/GLB export
- Generic WebGL applications
- Three.js, Babylon.js (standard workflow)

---

### threejs_optimized.json

**Format:** Three.js MeshStandardMaterial
**Resolution:** 1024×1024
**Outputs:**
- `color.jpg` - JPEG base color (smaller file size)
- `normal.png` - RGB normal map
- `ao.png` - Ambient occlusion
- `metalness.png` - Metallic channel
- `roughness.png` - Roughness channel

**Best for:**
- Three.js projects requiring separate channels
- Maximum flexibility (individual map control)
- When file size is less critical than editability

---

### babylonjs_pbr.json

**Format:** Babylon.js PBRMaterial
**Resolution:** 1024×1024
**Outputs:**
- `albedo.png` - Base color
- `normal.png` - Normal map
- `metallicRoughness.png` - Packed: G=Roughness, B=Metallic

**Best for:**
- Babylon.js PBR workflows
- Similar to glTF but with Babylon naming conventions

---

### web_orm_packed.json

**Format:** ORM (Occlusion-Roughness-Metallic) Packed
**Resolution:** 1024×1024
**Outputs:**
- `baseColor.png` - RGB base color
- `normal.png` - RGB normal map
- `ORM.png` - Packed: R=AO, G=Roughness, B=Metallic

**Best for:**
- Maximum efficiency (3 textures instead of 6)
- Production web applications
- When texture count matters more than editability

**Texture memory savings:** ~50% reduction

---

### mobile_webgl.json

**Format:** Mobile-optimized
**Resolution:** 512×512
**Outputs:**
- `color.jpg` - JPEG base color (aggressive compression)
- `normal.png` - RG normal map (reconstruct Z in shader)
- `packed.png` - R=AO, G=Roughness, B=Metallic

**Best for:**
- Mobile web applications
- Low-end devices
- When load time and memory are critical

**File size:** ~3MB total vs. ~16MB standard

## Customization

All presets can be customized by modifying the JSON files:

### Change Resolution

Modify the `sizeLog2` parameter:
- `9` = 512×512
- `10` = 1024×1024 (default)
- `11` = 2048×2048
- `12` = 4096×4096

```json
{
  "parameters": {
    "sizeLog2": 11  // Change to 2048×2048
  }
}
```

### Change File Format

Modify the `fileFormat` parameter:
- `"png"` - Lossless (recommended for data maps)
- `"jpeg"` - Lossy compression (good for baseColor)
- `"tga"` - Targa format
- `"exr"` - HDR format (32-bit)

```json
{
  "parameters": {
    "fileFormat": "jpeg"  // Change to JPEG
  }
}
```

### Add Custom Channels

Add new map entries to pack additional channels:

```json
{
  "fileName": "$textureSet_emissive",
  "channels": [
    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "emissive"},
    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "emissive"},
    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "emissive"}
  ],
  "parameters": {"fileFormat": "png", "bitDepth": "8", "sizeLog2": 10}
}
```

## Integration Examples

### Three.js with glTF Preset

```javascript
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

const loader = new GLTFLoader();

loader.load('model.glb', (gltf) => {
  // Textures automatically loaded from glTF
  scene.add(gltf.scene);
});
```

### Three.js with Separate Textures

```javascript
import * as THREE from 'three';

const textureLoader = new THREE.TextureLoader();

const material = new THREE.MeshStandardMaterial({
  map: textureLoader.load('Asset_color.jpg'),
  normalMap: textureLoader.load('Asset_normal.png'),
  aoMap: textureLoader.load('Asset_ao.png'),
  metalnessMap: textureLoader.load('Asset_metalness.png'),
  roughnessMap: textureLoader.load('Asset_roughness.png'),
});

// Set color space for baseColor
material.map.colorSpace = THREE.SRGBColorSpace;
```

### Babylon.js with PBR Preset

```javascript
import { PBRMaterial, Texture } from '@babylonjs/core';

const pbr = new PBRMaterial("pbr", scene);
pbr.albedoTexture = new Texture("Asset_albedo.png", scene);
pbr.bumpTexture = new Texture("Asset_normal.png", scene);
pbr.metallicTexture = new Texture("Asset_metallicRoughness.png", scene);

// Configure channel reading
pbr.useRoughnessFromMetallicTextureGreen = true;
pbr.useMetallnessFromMetallicTextureBlue = true;
```

### ORM Packed Workflow

```javascript
// Three.js with ORM texture
const ormTexture = textureLoader.load('Asset_ORM.png');

material.aoMap = ormTexture;        // Reads from Red channel
material.roughnessMap = ormTexture; // Reads from Green channel
material.metalnessMap = ormTexture; // Reads from Blue channel
```

## Troubleshooting

**Preset not found in Substance:**
- Presets are for custom export via Python API only
- Not visible in Substance UI preset dropdown
- Use via Python scripts or plugins

**Wrong channel order:**
- Verify glTF spec: G=Roughness, B=Metallic
- Unreal uses different packing: R=AO, G=Roughness, B=Metallic
- Check engine documentation for channel expectations

**Textures too large:**
- Reduce `sizeLog2` (e.g., 10 → 9 for 512px)
- Use mobile preset for aggressive optimization
- Convert baseColor to JPEG post-export

**Normal map inverted:**
- Substance uses OpenGL format (Y+)
- If using DirectX engine, flip green channel
- Or use engine setting to flip normal Y

## Additional Resources

- **Substance Python API:** https://helpx.adobe.com/substance-3d-painter-python/api/
- **glTF 2.0 Spec:** https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
- **Three.js Materials:** https://threejs.org/docs/#api/en/materials/MeshStandardMaterial
- **Babylon.js PBR:** https://doc.babylonjs.com/features/featuresDeepDive/materials/using/introToPBR

## License

These preset templates are provided as examples and can be freely modified for your projects.



===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/assets/export_templates/babylonjs_pbr.json =====

```json
{
  "exportPresets": [
    {
      "name": "BabylonJS_PBR",
      "maps": [
        {
          "fileName": "$textureSet_albedo",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            },
            {
              "destChannel": "G",
              "srcChannel": "G",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            },
            {
              "destChannel": "B",
              "srcChannel": "B",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        },
        {
          "fileName": "$textureSet_normal",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            },
            {
              "destChannel": "G",
              "srcChannel": "G",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            },
            {
              "destChannel": "B",
              "srcChannel": "B",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        },
        {
          "fileName": "$textureSet_metallicRoughness",
          "channels": [
            {
              "destChannel": "G",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "roughness"
            },
            {
              "destChannel": "B",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "metallic"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        }
      ]
    }
  ]
}
```


===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/assets/export_templates/gltf_standard.json =====

```json
{
  "exportPresets": [
    {
      "name": "glTF_Standard",
      "maps": [
        {
          "fileName": "$textureSet_baseColor",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            },
            {
              "destChannel": "G",
              "srcChannel": "G",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            },
            {
              "destChannel": "B",
              "srcChannel": "B",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        },
        {
          "fileName": "$textureSet_normal",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            },
            {
              "destChannel": "G",
              "srcChannel": "G",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            },
            {
              "destChannel": "B",
              "srcChannel": "B",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        },
        {
          "fileName": "$textureSet_metallicRoughness",
          "channels": [
            {
              "destChannel": "G",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "roughness"
            },
            {
              "destChannel": "B",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "metallic"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        }
      ]
    }
  ]
}
```


===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/assets/export_templates/mobile_webgl.json =====

```json
{
  "exportPresets": [
    {
      "name": "Mobile_WebGL",
      "maps": [
        {
          "fileName": "$textureSet_color",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            },
            {
              "destChannel": "G",
              "srcChannel": "G",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            },
            {
              "destChannel": "B",
              "srcChannel": "B",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            }
          ],
          "parameters": {
            "fileFormat": "jpeg",
            "bitDepth": "8",
            "sizeLog2": 9
          }
        },
        {
          "fileName": "$textureSet_normal",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            },
            {
              "destChannel": "G",
              "srcChannel": "G",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 9
          }
        },
        {
          "fileName": "$textureSet_packed",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "ambientOcclusion"
            },
            {
              "destChannel": "G",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "roughness"
            },
            {
              "destChannel": "B",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "metallic"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 9
          }
        }
      ]
    }
  ]
}
```


===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/assets/export_templates/threejs_optimized.json =====

```json
{
  "exportPresets": [
    {
      "name": "ThreeJS_Standard",
      "maps": [
        {
          "fileName": "$textureSet_color",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            },
            {
              "destChannel": "G",
              "srcChannel": "G",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            },
            {
              "destChannel": "B",
              "srcChannel": "B",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            }
          ],
          "parameters": {
            "fileFormat": "jpeg",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        },
        {
          "fileName": "$textureSet_normal",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            },
            {
              "destChannel": "G",
              "srcChannel": "G",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            },
            {
              "destChannel": "B",
              "srcChannel": "B",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        },
        {
          "fileName": "$textureSet_ao",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "ambientOcclusion"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        },
        {
          "fileName": "$textureSet_metalness",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "metallic"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        },
        {
          "fileName": "$textureSet_roughness",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "roughness"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        }
      ]
    }
  ]
}
```


===== FILE: plugins/individual/substance-3d-texturing/skills/substance-3d-texturing/assets/export_templates/web_orm_packed.json =====

```json
{
  "exportPresets": [
    {
      "name": "Web_ORM",
      "maps": [
        {
          "fileName": "$textureSet_baseColor",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            },
            {
              "destChannel": "G",
              "srcChannel": "G",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            },
            {
              "destChannel": "B",
              "srcChannel": "B",
              "srcMapType": "documentMap",
              "srcMapName": "baseColor"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        },
        {
          "fileName": "$textureSet_normal",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            },
            {
              "destChannel": "G",
              "srcChannel": "G",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            },
            {
              "destChannel": "B",
              "srcChannel": "B",
              "srcMapType": "documentMap",
              "srcMapName": "normal"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        },
        {
          "fileName": "$textureSet_ORM",
          "channels": [
            {
              "destChannel": "R",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "ambientOcclusion"
            },
            {
              "destChannel": "G",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "roughness"
            },
            {
              "destChannel": "B",
              "srcChannel": "R",
              "srcMapType": "documentMap",
              "srcMapName": "metallic"
            }
          ],
          "parameters": {
            "fileFormat": "png",
            "bitDepth": "8",
            "sizeLog2": 10
          }
        }
      ]
    }
  ]
}
```


# Skill: web3d-integration-patterns


===== FILE: plugins/individual/web3d-integration-patterns/skills/web3d-integration-patterns/SKILL.md =====

---
name: web3d-integration-patterns
description: Meta-skill for combining Three.js, GSAP ScrollTrigger, React Three Fiber, Motion, and React Spring for complex 3D web experiences. Use when building applications that integrate multiple 3D and animation libraries, requiring architecture patterns, state management, and performance optimization across the stack. Triggers on tasks involving library integration, multi-library architectures, scroll-driven 3D experiences, physics-based 3D animations, or complex interactive 3D applications.
---

# Web 3D Integration Patterns

## Overview

This meta-skill provides architectural patterns, best practices, and integration strategies for combining multiple 3D and animation libraries in web applications. It synthesizes knowledge from the threejs-webgl, gsap-scrolltrigger, react-three-fiber, motion-framer, and react-spring-physics skills into cohesive patterns for building complex, performant 3D web experiences.

**When to use this skill:**
- Building complex 3D applications that combine multiple libraries
- Creating scroll-driven 3D experiences with animation orchestration
- Implementing physics-based interactions with 3D scenes
- Managing state across 3D rendering and UI animations
- Optimizing performance in multi-library architectures
- Designing reusable component architectures for 3D applications
- Migrating between or combining animation approaches

**Core Integration Combinations:**
1. **Three.js + GSAP** - Scroll-driven 3D animations, timeline orchestration
2. **React Three Fiber + Motion** - State-based 3D with declarative animations
3. **React Three Fiber + GSAP** - Complex 3D sequences in React
4. **React Three Fiber + React Spring** - Physics-based 3D interactions
5. **Three.js + GSAP + React** - Hybrid imperative/declarative 3D

## Architecture Patterns

### Pattern 1: Layered Separation (Three.js + GSAP + React UI)

**Use case:** 3D scene with overlaid UI, scroll-driven animations

**Architecture:**
```
├── 3D Layer (Three.js)
│   ├── Scene management
│   ├── Camera controls
│   └── Render loop
├── Animation Layer (GSAP)
│   ├── ScrollTrigger for 3D properties
│   ├── Timelines for sequences
│   └── UI transitions
└── UI Layer (React + Motion)
    ├── HTML overlays
    ├── State management
    └── User interactions
```

**Implementation:**

```javascript
// App.jsx - React root
import { useEffect, useRef } from 'react'
import { initThreeScene } from './three/scene'
import { initScrollAnimations } from './animations/scroll'
import { motion } from 'framer-motion'

function App() {
  const canvasRef = useRef()
  const sceneRef = useRef()

  useEffect(() => {
    // Initialize Three.js scene
    sceneRef.current = initThreeScene(canvasRef.current)

    // Initialize GSAP ScrollTrigger animations
    initScrollAnimations(sceneRef.current)

    // Cleanup
    return () => {
      sceneRef.current.dispose()
    }
  }, [])

  return (
    <div className="app">
      <canvas ref={canvasRef} />

      <motion.div
        className="overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <section className="hero">
          <h1>3D Experience</h1>
        </section>
        <section className="content">
          {/* Scrollable content */}
        </section>
      </motion.div>
    </div>
  )
}
```

```javascript
// three/scene.js - Three.js setup
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

export function initThreeScene(canvas) {
  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true })

  renderer.setSize(window.innerWidth, window.innerHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

  const controls = new OrbitControls(camera, canvas)
  controls.enableDamping = true

  // Setup scene objects
  const geometry = new THREE.BoxGeometry(2, 2, 2)
  const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 })
  const cube = new THREE.Mesh(geometry, material)
  scene.add(cube)

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
  directionalLight.position.set(5, 10, 7.5)
  scene.add(directionalLight)

  camera.position.set(0, 2, 5)

  // Animation loop
  function animate() {
    requestAnimationFrame(animate)
    controls.update()
    renderer.render(scene, camera)
  }
  animate()

  // Resize handler
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize(window.innerWidth, window.innerHeight)
  })

  return { scene, camera, renderer, cube }
}
```

```javascript
// animations/scroll.js - GSAP ScrollTrigger integration
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export function initScrollAnimations(sceneRefs) {
  const { camera, cube } = sceneRefs

  // Animate camera on scroll
  gsap.to(camera.position, {
    x: 5,
    y: 3,
    z: 10,
    scrollTrigger: {
      trigger: '.content',
      start: 'top top',
      end: 'bottom center',
      scrub: 1,
      onUpdate: () => camera.lookAt(cube.position)
    }
  })

  // Animate mesh rotation
  gsap.to(cube.rotation, {
    y: Math.PI * 2,
    x: Math.PI,
    scrollTrigger: {
      trigger: '.content',
      start: 'top bottom',
      end: 'bottom top',
      scrub: true
    }
  })

  // Animate material properties
  gsap.to(cube.material, {
    opacity: 0.3,
    scrollTrigger: {
      trigger: '.content',
      start: 'top center',
      end: 'center center',
      scrub: 1
    }
  })
}
```

**Benefits:**
- Clear separation of concerns
- Easy to reason about data flow
- Performance optimization per layer
- Independent testing of layers

**Trade-offs:**
- More boilerplate
- Manual synchronization between layers
- State management complexity

---

### Pattern 2: Unified React Component (React Three Fiber + Motion)

**Use case:** React-first architecture with declarative 3D and animations

**Architecture:**
```
React Component Tree
├── <Canvas> (R3F)
│   ├── 3D Scene Components
│   ├── Lights
│   ├── Camera
│   └── Effects
└── <motion.div> (UI overlays)
    ├── HTML content
    └── Animations
```

**Implementation:**

```jsx
// App.jsx - Unified React approach
import { Canvas } from '@react-three/fiber'
import { Suspense } from 'react'
import { motion } from 'framer-motion'
import { Scene } from './components/Scene'
import { Loader } from './components/Loader'

function App() {
  return (
    <div className="app">
      <Canvas
        camera={{ position: [0, 2, 5], fov: 75 }}
        dpr={[1, 2]}
        shadows
      >
        <Suspense fallback={<Loader />}>
          <Scene />
        </Suspense>
      </Canvas>

      <motion.div
        className="ui-overlay"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      >
        <h1>React-First 3D Experience</h1>
      </motion.div>
    </div>
  )
}
```

```jsx
// components/Scene.jsx - R3F scene
import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { OrbitControls, Environment } from '@react-three/drei'
import { motion } from 'framer-motion-3d'

export function Scene() {
  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 10, 7.5]} castShadow />

      <AnimatedCube />
      <Floor />

      <OrbitControls enableDamping dampingFactor={0.05} />
      <Environment preset="sunset" />
    </>
  )
}

function AnimatedCube() {
  const [hovered, setHovered] = useState(false)
  const [active, setActive] = useState(false)

  return (
    <motion.mesh
      scale={active ? 1.5 : 1}
      onClick={() => setActive(!active)}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
      animate={{
        rotateY: hovered ? Math.PI * 2 : 0
      }}
      transition={{ type: 'spring', stiffness: 200, damping: 20 }}
    >
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
    </motion.mesh>
  )
}

function Floor() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]} receiveShadow>
      <planeGeometry args={[100, 100]} />
      <meshStandardMaterial color="#222" />
    </mesh>
  )
}
```

**Benefits:**
- Declarative, React-first approach
- Unified state management
- Component reusability
- Easy testing with React tools

**Trade-offs:**
- R3F learning curve
- Less control over render loop
- Potential React re-render issues

---

### Pattern 3: Hybrid Approach (R3F + GSAP Timelines)

**Use case:** Complex animation sequences with React state management

**Implementation:**

```jsx
// components/AnimatedScene.jsx
import { useRef, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import gsap from 'gsap'

export function AnimatedScene() {
  const groupRef = useRef()
  const timelineRef = useRef()

  useEffect(() => {
    // Create GSAP timeline for complex sequence
    const tl = gsap.timeline({ repeat: -1, yoyo: true })

    tl.to(groupRef.current.position, {
      y: 2,
      duration: 1,
      ease: 'power2.inOut'
    })
    .to(groupRef.current.rotation, {
      y: Math.PI * 2,
      duration: 2,
      ease: 'none'
    }, 0) // Start at same time

    timelineRef.current = tl

    return () => tl.kill()
  }, [])

  return (
    <group ref={groupRef}>
      <mesh>
        <boxGeometry />
        <meshStandardMaterial color="cyan" />
      </mesh>
    </group>
  )
}
```

---

### Pattern 4: Physics-Based 3D (R3F + React Spring)

**Use case:** Natural, physics-driven 3D interactions

**Implementation:**

```jsx
// components/PhysicsCube.jsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { useSpring, animated, config } from '@react-spring/three'

const AnimatedMesh = animated('mesh')

export function PhysicsCube() {
  const [springs, api] = useSpring(() => ({
    scale: 1,
    position: [0, 0, 0],
    config: config.wobbly
  }), [])

  const handleClick = () => {
    api.start({
      scale: 1.5,
      position: [0, 2, 0]
    })

    // Return to original after delay
    setTimeout(() => {
      api.start({
        scale: 1,
        position: [0, 0, 0]
      })
    }, 1000)
  }

  return (
    <AnimatedMesh
      scale={springs.scale}
      position={springs.position}
      onClick={handleClick}
    >
      <boxGeometry />
      <meshStandardMaterial color="orange" />
    </AnimatedMesh>
  )
}
```

---

## Common Integration Patterns

### 1. Scroll-Driven Camera Movement

**Three.js + GSAP:**

```javascript
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

// Smooth camera path through multiple points
const cameraPath = [
  { x: 0, y: 2, z: 5, lookAt: { x: 0, y: 0, z: 0 } },
  { x: 5, y: 3, z: 10, lookAt: { x: 0, y: 0, z: 0 } },
  { x: -3, y: 1, z: 8, lookAt: { x: 0, y: 0, z: 0 } }
]

const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '#container',
    start: 'top top',
    end: 'bottom bottom',
    scrub: 1,
    pin: true
  }
})

cameraPath.forEach((point, i) => {
  tl.to(camera.position, {
    x: point.x,
    y: point.y,
    z: point.z,
    duration: 1,
    onUpdate: () => camera.lookAt(point.lookAt.x, point.lookAt.y, point.lookAt.z)
  }, i)
})
```

**R3F + ScrollControls (Drei):**

```jsx
import { ScrollControls, Scroll, useScroll } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'

function CameraRig() {
  const scroll = useScroll()

  useFrame((state) => {
    const offset = scroll.offset

    state.camera.position.x = Math.sin(offset * Math.PI * 2) * 5
    state.camera.position.z = Math.cos(offset * Math.PI * 2) * 5
    state.camera.lookAt(0, 0, 0)
  })

  return null
}

export function App() {
  return (
    <Canvas>
      <ScrollControls pages={3} damping={0.5}>
        <CameraRig />
        <Scroll>
          <Scene />
        </Scroll>
      </ScrollControls>
    </Canvas>
  )
}
```

### 2. Gesture-Driven 3D Manipulation

**R3F + Motion (Framer Motion 3D):**

```jsx
import { motion } from 'framer-motion-3d'

function DraggableObject() {
  return (
    <motion.mesh
      drag
      dragElastic={0.1}
      dragConstraints={{ left: -5, right: 5, top: 5, bottom: -5 }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      animate={{
        rotateY: [0, Math.PI * 2],
        transition: { repeat: Infinity, duration: 4, ease: 'linear' }
      }}
    >
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="hotpink" />
    </motion.mesh>
  )
}
```

### 3. State-Synchronized Animations

**R3F + Zustand + GSAP:**

```jsx
// store.js
import create from 'zustand'

export const useStore = create((set) => ({
  selectedObject: null,
  cameraMode: 'orbit',
  setSelectedObject: (obj) => set({ selectedObject: obj }),
  setCameraMode: (mode) => set({ cameraMode: mode })
}))
```

```jsx
// components/InteractiveObject.jsx
import { useRef, useEffect } from 'react'
import { useStore } from '../store'
import gsap from 'gsap'

export function InteractiveObject({ id }) {
  const meshRef = useRef()
  const selectedObject = useStore((state) => state.selectedObject)
  const setSelectedObject = useStore((state) => state.setSelectedObject)

  const isSelected = selectedObject === id

  useEffect(() => {
    if (isSelected) {
      gsap.to(meshRef.current.scale, {
        x: 1.2,
        y: 1.2,
        z: 1.2,
        duration: 0.3,
        ease: 'back.out'
      })
      gsap.to(meshRef.current.material, {
        emissiveIntensity: 0.5,
        duration: 0.3
      })
    } else {
      gsap.to(meshRef.current.scale, {
        x: 1,
        y: 1,
        z: 1,
        duration: 0.3,
        ease: 'power2.inOut'
      })
      gsap.to(meshRef.current.material, {
        emissiveIntensity: 0,
        duration: 0.3
      })
    }
  }, [isSelected])

  return (
    <mesh
      ref={meshRef}
      onClick={() => setSelectedObject(isSelected ? null : id)}
    >
      <boxGeometry />
      <meshStandardMaterial color="cyan" emissive="cyan" />
    </mesh>
  )
}
```

---

## State Management Strategies

### 1. Zustand for Global 3D State

**Best for:** Shared state across 3D scene and UI

```javascript
// store/scene.js
import create from 'zustand'

export const useSceneStore = create((set, get) => ({
  // State
  camera: { position: [0, 2, 5], target: [0, 0, 0] },
  objects: {},
  selectedId: null,
  isAnimating: false,

  // Actions
  updateCamera: (updates) => set((state) => ({
    camera: { ...state.camera, ...updates }
  })),

  addObject: (id, object) => set((state) => ({
    objects: { ...state.objects, [id]: object }
  })),

  selectObject: (id) => set({ selectedId: id }),

  setAnimating: (isAnimating) => set({ isAnimating })
}))
```

**Usage in R3F:**

```jsx
import { useSceneStore } from '../store/scene'

function Object3D({ id }) {
  const selectedId = useSceneStore((state) => state.selectedId)
  const selectObject = useSceneStore((state) => state.selectObject)

  const isSelected = selectedId === id

  return (
    <mesh onClick={() => selectObject(id)}>
      <boxGeometry />
      <meshStandardMaterial color={isSelected ? 'hotpink' : 'orange'} />
    </mesh>
  )
}
```

---

## Performance Optimization

### Cross-Library Performance Patterns

#### 1. Render Loop Optimization

**Coordinate render loops between Three.js and animation libraries:**

```javascript
// Unified render loop with conditional rendering
import { Clock } from 'three'

const clock = new Clock()
let needsRender = true

function animate() {
  requestAnimationFrame(animate)

  const delta = clock.getDelta()
  const elapsed = clock.getElapsedTime()

  // Only render when needed
  if (needsRender || controls.enabled) {
    // Update GSAP animations (handled automatically)

    // Update Three.js
    controls.update()
    renderer.render(scene, camera)

    // Reset flag
    needsRender = false
  }
}

// Trigger re-render on interactions
ScrollTrigger.addEventListener('update', () => {
  needsRender = true
})
```

#### 2. On-Demand Rendering (R3F)

```jsx
import { Canvas } from '@react-three/fiber'

function App() {
  return (
    <Canvas
      frameloop="demand" // Only renders when needed
      dpr={[1, 2]} // Adaptive pixel ratio
    >
      <Scene />
    </Canvas>
  )
}

function Scene() {
  const invalidate = useThree((state) => state.invalidate)

  // Trigger render on state change
  const handleClick = () => {
    // Update state...
    invalidate() // Manually trigger render
  }

  return <mesh onClick={handleClick}>...</mesh>
}
```

---

## Common Pitfalls

### 1. Animation Conflicts

**Problem:** Multiple libraries trying to animate the same property

```jsx
// ❌ Wrong: GSAP and React Spring both animating position
gsap.to(meshRef.current.position, { x: 5 })
api.start({ position: [10, 0, 0] }) // Conflict!
```

**Solution:** Choose one library per property or coordinate timing

```jsx
// ✅ Correct: Separate properties
gsap.to(meshRef.current.position, { x: 5 }) // GSAP handles position
api.start({ scale: 1.5 }) // Spring handles scale
```

### 2. State Synchronization Issues

**Problem:** React state out of sync with Three.js scene

```jsx
// ❌ Wrong: Updating Three.js without updating React state
mesh.position.x = 5 // Three.js updated
// But React state still shows old value!
```

**Solution:** Use refs or state management

```jsx
// ✅ Correct: Update both
const updatePosition = (x) => {
  mesh.position.x = x
  setPosition(x) // Update React state
}
```

### 3. Memory Leaks from Abandoned Animations

**Problem:** Not cleaning up animations on unmount

```jsx
// ❌ Wrong: No cleanup
useEffect(() => {
  gsap.to(meshRef.current.rotation, { y: Math.PI * 2, repeat: -1 })
}, [])
```

**Solution:** Always cleanup in useEffect return

```jsx
// ✅ Correct: Cleanup on unmount
useEffect(() => {
  const tween = gsap.to(meshRef.current.rotation, { y: Math.PI * 2, repeat: -1 })

  return () => {
    tween.kill()
  }
}, [])
```

---

## Decision Matrix

### When to Use Which Combination

| Use Case | Recommended Stack | Rationale |
|----------|------------------|-----------|
| Marketing landing page with scroll-driven 3D | Three.js + GSAP + React UI | GSAP excels at scroll orchestration |
| React app with interactive 3D product viewer | R3F + Motion | Declarative, state-driven, component-based |
| Complex animation sequences (timeline-based) | R3F + GSAP | GSAP timeline control with R3F components |
| Physics-based interactions (drag, momentum) | R3F + React Spring | Spring physics feel natural for gestures |
| High-performance particle systems | Three.js + GSAP | Imperative control, instancing, minimal overhead |
| Rapid prototyping, quick iterations | R3F + Drei + Motion | High-level abstractions, fast development |
| Game-like experiences with physics | R3F + React Spring + Cannon (physics) | Physics engine + spring-based UI feedback |

---

## Resources

This skill includes bundled resources for multi-library integration:

### references/
- `architecture_patterns.md` - Detailed architectural patterns and trade-offs
- `performance_optimization.md` - Performance strategies across the stack
- `state_management.md` - State management patterns for 3D applications

### scripts/
- `integration_helper.py` - Generate integration boilerplate for library combinations
- `pattern_generator.py` - Scaffold common integration patterns

### assets/
- `starter_unified/` - Complete starter template combining R3F + GSAP + Motion
- `examples/` - Real-world integration examples

---

## Related Skills

**Foundation Skills** (use these for library-specific details):
- **threejs-webgl** - Three.js fundamentals, scene setup, rendering
- **gsap-scrolltrigger** - GSAP animations, ScrollTrigger, timelines
- **react-three-fiber** - R3F components, hooks, Drei helpers
- **motion-framer** - Motion components, gestures, layout animations
- **react-spring-physics** - Spring physics, React Spring hooks

**When to Reference Foundation Skills:**
- Three.js-specific API questions → `threejs-webgl`
- ScrollTrigger syntax → `gsap-scrolltrigger`
- R3F hooks and patterns → `react-three-fiber`
- Motion gesture handling → `motion-framer`
- Spring configuration → `react-spring-physics`

**This Meta-Skill Covers:**
- Architecture patterns for combining libraries
- State management across libraries
- Performance optimization strategies
- Common integration pitfalls
- Decision-making frameworks

---

**Use this skill when building complex 3D web applications that integrate multiple animation and rendering libraries. For library-specific implementation details, reference the individual foundation skills.**



===== FILE: plugins/individual/web3d-integration-patterns/agents/web3d-integration-patterns-specialist.md =====

# Web3D Integration Patterns Specialist

## Role

Expert specialist in Web3D Integration Patterns implementation, patterns, and best practices.

## Expertise

- Web3D Integration Patterns core concepts and patterns
- Integration with other libraries and frameworks
- Performance optimization
- Common pitfalls and solutions
- Best practices and conventions

## When to use

Activate this agent when working on:
- Web3D Integration Patterns implementation challenges
- Integration with other technologies
- Performance optimization
- Troubleshooting and debugging
- Architecture decisions

## Approach

1. Understand project requirements and context
2. Apply Web3D Integration Patterns best practices
3. Recommend optimal implementation patterns
4. Identify and solve common issues
5. Provide detailed guidance and examples

## Tools

This agent has access to:
- Web3D Integration Patterns skill knowledge
- Pattern libraries and examples
- Troubleshooting guides
- Integration patterns



===== FILE: plugins/individual/web3d-integration-patterns/commands/help.md =====

# /web3d-integration-patterns-help

Get help with Web3D Integration Patterns

## Description

Provides comprehensive help and documentation for Web3D Integration Patterns.

## Usage

```bash
/web3d-integration-patterns-help
```

## What it does

- Shows common patterns and examples
- Links to official documentation
- Provides troubleshooting guidance
- Explains key concepts



===== FILE: plugins/individual/web3d-integration-patterns/commands/setup.md =====

# /web3d-integration-patterns-setup

Initialize Web3D Integration Patterns project

## Description

Provides setup guidance and boilerplate code for starting a new Web3D Integration Patterns project.

## Usage

```bash
/web3d-integration-patterns-setup
```

## What it does

- Analyzes your project structure
- Provides installation instructions
- Generates boilerplate code
- Offers configuration guidance

