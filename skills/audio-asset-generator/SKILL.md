---
name: audio-asset-generator
description: Experimental cross-agent workflow for creating production-ready audio assets for games, interactive web apps, and native apps. Use to inventory required sound effects, ambience, background music, or voice, generate zero-cost procedural SFX locally when suitable, route richer audio to explicitly available generators, normalize and encode assets for the target runtime, and wire them into the project without inventing unsupported provider capabilities or silently spending money.
---

# Audio Asset Generator

> **Experimental:** This workflow is still being validated, and its behavior and interfaces may change.

Create audio that is usable by the target product, not just a loose collection of generated files.

Use this evidence chain:

`inspect product -> define audio map -> choose cheapest valid source -> generate -> post-process -> integrate -> verify playback -> report provenance`

## Keep the package standalone

- Do not require, install, invoke, or delegate the workflow to another skill.
- Work with the tools already available in the current runtime and repository.
- Do not install audio models, system packages, codecs, Python packages, browser binaries, or provider SDKs unless the user separately authorizes that environment change.
- Do not register for a service, create paid resources, consume paid credits, or send billable API requests without explicit user authorization when cost could be incurred.
- Do not claim a provider can generate music, sound effects, or voice unless that capability is actually available in the current runtime or documented provider surface.
- Do not commit, push, publish, or modify external systems unless separately authorized.

## Inspect the product before generating anything

Establish these facts from the repository and task:

1. Target runtime: browser, native app, engine, or other runtime.
2. Existing audio stack and conventions: file locations, naming, playback libraries, manifests, preload strategy, background-music lifecycle, mute/music/SFX volume controls, and supported codecs.
3. Required categories: UI SFX, gameplay SFX, ambience, background music, voice, or a subset.
4. Product direction: mood, genre, intensity, texture, pacing, and whether the audio should loop.
5. Delivery constraints: bundle size, duration, latency, mobile support, licensing, and whether generated assets may be commercially distributed.

Reuse existing product or design documents instead of asking again. Ask only when a missing decision materially changes generation or acceptance.

Create a concise task-local audio map before generation. It should identify each asset, trigger or scene, category, target duration, looping requirement, intended source, and output path.

For every candidate source, record whether reuse and commercial distribution are allowed. Treat unknown rights as a blocker for committed product integration, not as permission to proceed.

## Choose the cheapest valid source first

Read [provider-routing.md](references/provider-routing.md) when selecting a generation route.

Use this preference order:

1. **Existing project asset** when a suitable asset already exists and reuse is allowed.
2. **Local procedural synthesis** for synthetic UI/game SFX that can be described with oscillators, noise, envelopes, pitch sweeps, and simple layering.
3. **Already-available first-party capability** when the current runtime exposes a documented audio capability appropriate for the requested category.
4. **Already-configured local or external generator** for richer SFX, ambience, or music when procedural synthesis is not credible.
5. **Asset plan only** when no suitable generator is available or use would require unapproved installation, signup, credentials, or spend.

Never route background music to a speech-only model. Never route realistic environmental SFX to a procedural generator merely to avoid reporting a capability gap.

## Generate local procedural SFX when appropriate

The bundled generator is dependency-free Python and is intended for short synthetic effects, not realistic Foley or full music.

From the installed skill directory, run:

```bash
python3 scripts/generate_procedural_sfx.py \
  --preset ui-click \
  --output /path/to/project/public/audio/sfx/ui-click.wav
```

Supported presets are documented by `--list-presets`.

The helper refuses to overwrite an existing file unless `--force` is supplied. Use `--force` only when replacement of that exact asset is already authorized.

Generate small variations for repeatedly triggered sounds when repetition would be obvious:

```bash
python3 scripts/generate_procedural_sfx.py \
  --preset impact \
  --seed 1 \
  --output /path/to/project/public/audio/sfx/impact-01.wav

python3 scripts/generate_procedural_sfx.py \
  --preset impact \
  --seed 2 \
  --output /path/to/project/public/audio/sfx/impact-02.wav
```

Preserve generated WAV sources when the project already keeps masters. Otherwise follow the repository's existing asset convention.

## Use richer generators conservatively

When the task needs realistic Foley, environmental ambience, long-form background music, or other content that local procedural synthesis cannot credibly produce:

- Inspect the current runtime's available tools and configured providers.
- Prefer tools the user already has access to.
- Verify the provider supports the requested media type before using it.
- Preserve the user's stated budget preference. A free local option outranks a paid API when both are adequate. Treat unknown pricing or credit use as potentially billable and ask before making the request.
- Record the provider, model or mode when known, prompt, generation date, and any material license constraint in a task-local note or existing project asset manifest.
- Do not fabricate provider output when the generator is unavailable. Return the exact prompts and asset map needed for a later generation pass instead.

For voice, use a documented speech-generation surface only when voice is actually requested. Treat voice, music, and sound effects as separate capabilities. Before using a custom or recognizable voice identity, confirm the speaker authorization, consent evidence, and disclosure obligations required by the provider and product. A connected voice tool is not evidence that those rights are satisfied.

When generation is unavailable, mark each audio-map item `not generated` and provide a ready-to-run prompt with its category, audible target, duration, loop requirement, output format, and negative constraints. Do not use a prompt-only deliverable as evidence that an audio file exists.

## Write prompts as production specifications

For richer generation or a prompt-only handoff, read the relevant category in [prompt-specifications.md](references/prompt-specifications.md). Keep the prompt tied to the approved audio map. For voice, confirm speaker authorization and disclosure ownership before generation; never imitate a recognizable person without documented authorization.

## Post-process only with available tools

Read [web-audio-delivery.md](references/web-audio-delivery.md) only for browser-oriented delivery.

Use the repository's existing audio tooling first. If `ffmpeg` or an equivalent tool is already available, it may be used for:

- trimming silence;
- fades;
- peak or loudness normalization;
- mono/stereo conversion when justified;
- sample-rate conversion when required;
- encoding into the project's delivery format;
- validating duration and stream metadata.

Do not install a codec tool merely because it would be convenient.

Keep lossy re-encoding to a minimum. Preserve loop boundaries when the asset is intended to repeat continuously.

## Integrate into the actual product

Generation is incomplete until the target project can use the asset.

Follow the existing architecture. Typical work may include:

- placing files under the established public/static/assets directory;
- updating an audio manifest;
- wiring named sound events to interaction handlers;
- adding background-music lifecycle behavior;
- respecting global mute, music, and SFX volume settings;
- preloading only latency-sensitive small assets;
- lazy-loading larger music or ambience;
- preventing duplicate overlapping playback when the product contract requires it.

For browser products, respect autoplay restrictions. Do not force background audio to start before an allowed user gesture when the browser would block it.

## Verify the result

Run the smallest available verification that proves the integration:

1. Confirm every generated file is readable and non-empty.
2. Check duration and codec when tooling is available.
3. Run relevant build, typecheck, lint, or tests for changed integration code.
4. Exercise the trigger or scene in the real target runtime when browser, app, or engine playback is available.
5. Check loops for audible clicks, unintended gaps, or large level jumps when looping is required.
6. Confirm mute and volume behavior when those controls exist.

Do not claim an asset sounds good if the runtime provides no way to listen to it. Distinguish file-level validation from actual listening or playback verification.

## Finish honestly

Report:

- assets created, reused, or still missing;
- generation route for each category;
- files and integration points changed;
- provider and licensing notes where relevant;
- verification performed, including whether audio was actually heard;
- any generation route blocked by missing tools, credentials, approval, or budget; and
- exact next prompts or asset-map entries for anything that could not be generated.
