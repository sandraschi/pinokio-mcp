# Available Local AI Apps - What's Actually on This Pinokio Install

**Last surveyed:** 2026-07-14 (via `pinokio-mcp`'s own `app_management(action="list")`, cross-checked with a direct filesystem size scan)
**Why this exists:** `pinokio-mcp` can list, start, and stop Pinokio apps, but it has no concept of *what's actually inside them* - whether an app has real downloaded model weights or is just an empty environment. This doc is the missing piece: a real inventory of what's here, what it's good for, and what's worth trying first. It's a snapshot, not a live view - re-survey when apps are added or removed (see "Keeping this current" at the bottom).

**Total footprint:** ~550GB across 20 installed apps.

---

## Start here if you're not sure what to try

| If you want... | Try |
|---|---|
| A quick 3D model from one photo | `ml-sharp-pinokio.git` - smallest footprint (7.7GB), fastest to test |
| An AI-generated song with lyrics | `SongGeneration-Studio.git` |
| A local text-to-speech voice | `zonos.git` - 200k+ hours of training data, tiny (5.9GB) |
| A video from a photo | `wan.git` (Wan 2.1, already proven working) or `lingbot-world-pinokio.git` (a purpose-built world model, untested but promising) |
| To swap a face in a photo/video | `facefusion-pinokio.git` |
| To upscale an old low-res image | `clarity-refiners-ui.git` |

---

## Full list, grouped by what it does

### 3D / spatial
- **`ml-sharp-pinokio.git`** (7.7GB) - one-click single-image-to-3D-Gaussian-splat. Small, fast to try.
- **`Hunyuan3D-2-lowvram.git`** (75GB) - image-to-3D-mesh, runs on as little as 6GB VRAM.
- **`cube.git`** (14.6GB) - Roblox's 3D foundation model.

### Video generation
- **`wan.git`** (30.2GB) - Wan 2.1, video generation optimized for GPU-poor machines. **Proven working** - real weights, native support confirmed in a fresh ComfyUI install.
- **`lingbot-world-pinokio.git`** (183.4GB) - a "world model" for image-to-video, 4-bit quantized (~20GB VRAM). The biggest single app here; untested but its whole design point is spatial/physical consistency, which general video models don't specifically target.
- **`Hunyuan3D-2-lowvram.git`**'s sibling, **`hunyuanvideo.git`** (41.2GB) - Tencent's HunyuanVideo, optimized for lower-end GPUs.
- **`Frame-Pack.git`** (45.2GB) - progressive, next-frame-section video generation.

### Song / music generation
- **`SongGeneration-Studio.git`** (40.1GB) - full songs: lyrics, vocals, instrumental, style control.
- **`yue.git`** (22.8GB) - YuE, an open full-song generation foundation model.
- **`diffrhythm.git`** (18.4GB) - songs up to 4m45s, lyrics or instrumental.

### Text-to-speech
- **`zonos.git`** (5.9GB) - Zonos-v0.1, open-weight, multilingual, 200k+ hours of training data.
- **`Orpheus-TTS-FastAPI.git`** (0GB) - registered but never actually downloaded, nothing to use here.

### Image generation / editing
- **`flux-2-klein-pinokio.git`** (6.1GB) - **environment only, no model weights** despite the name; would need a real download to actually generate anything.
- **`MagicQuill.git`** (18.7GB) - interactive image editing, erase/add objects.
- **`StyleAligned.pinokio.git`** (12.0GB) - style-aligned image generation via shared attention.
- **`clarity-refiners-ui.git`** (8.2GB) - image upscaling/enhancement.
- **`facefusion-pinokio.git`** (6.8GB) - face manipulation.
- **`comfy.git`** (5.5GB) - Pinokio's own ComfyUI wrapper. A separate, direct ComfyUI install exists elsewhere on this machine (`D:\ComfyUI`) that's already in active use - this one isn't currently needed.

### Audio (non-speech)
- **`MMAudio.git`** (10.3GB) - generates audio synced to video or text input.

### Other
- **`deeperhermes.git`** (0.04GB) - essentially empty, failed/abandoned install.

---

## The two biggest red flags found

1. **App size isn't proof of real content.** `flux-2-klein-pinokio.git` is 6.1GB and looks like a serious install - checked directly, every file over 100MB is a torch/CUDA library file. Zero actual model checkpoints. The app environment got set up; the model download step never happened. Always check for real `.safetensors`/`.gguf`/`.ckpt` files before assuming an app is ready to use.
2. **"Installed" doesn't mean "has weights."** `Orpheus-TTS-FastAPI.git` is a 0GB folder - registered with Pinokio, environment presumably never even set up. Worth cleaning up or re-attempting if Orpheus is ever actually wanted.

---

## Keeping this current

This is a point-in-time snapshot from 2026-07-14. To re-check what's here:

```powershell
Get-ChildItem "D:\pinokio\api" -Directory | ForEach-Object {
    $sz = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1GB
    [PSCustomObject]@{App=$_.Name; SizeGB=[math]::Round($sz,2)}
} | Sort-Object SizeGB -Descending
```

For real weight files specifically (not just folder size), add `-Include "*.safetensors","*.gguf","*.ckpt","*.pt"` to a recursive `Get-ChildItem` inside any app folder you're checking.

**Known gap in `pinokio-mcp` itself:** there's no tool that does this automatically - `app_management(action="list")` tells you an app exists and whether it's running, not what's inside it. A `pinokio_models` (or similar) tool op that walks each app's likely weight-storage location and reports real file sizes/formats would close this gap. Not built yet - this doc is the manual substitute.

## Fleet-wide relevance

If you're working across the broader MCP fleet, not just this one Pinokio install: several apps here directly fill gaps other fleet servers have - `SongGeneration-Studio`/`YuE`/`DiffRhythm` for `songgeneration-mcp` (which currently has no real backend), `Zonos` for `ittybitty`'s stubbed TTS provider, `ml-sharp` and `lingbot-world` for `splatmaker-mcp`'s prompt-to-splat design. Full cross-referenced writeup: `mcp-central-docs/architecture/PINOKIO_INVENTORY.md`.
