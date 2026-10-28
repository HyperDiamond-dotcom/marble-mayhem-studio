# Marble Mayhem Studio

Original 3D spiral race scene designed for TikTok vertical videos. The renderer and procedural geometry are original; no code from the earlier unlicensed fork is imported.

**The test is cinematic animation, not a validated real-world physics simulation.** Five coloured marbles follow independently animated tracks through a large multi-level helical course, with rotating obstacles and a travelling camera. A proper collision engine and race logic are future work.

## Render a free technical preview
Select **Actions → Original 3D Gauntlet preview → Run workflow**. The workflow uses a standard Ubuntu GitHub Actions runner; no Runway credits or Railway costs. After success, download the ZIP artifact with the four-second video and still frame.

## Render locally with Blender 4.x
Run: blender -b -P gauntlet_original.py -- --preview

For a complete 70-second, vertical 1080×1920 scene, omit --preview. **Do not start a full-resolution CPU render on GitHub**; use a suitable GPU machine after checking the preview. Blender currently defaults to CPU for portability; GPU settings and visual quality must be validated before production.

No automatic TikTok posting, purchases, external downloads or API keys are used.
