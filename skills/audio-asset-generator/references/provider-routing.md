# Provider routing

Use this reference only to choose a generation path. Capabilities change; verify the provider surface available in the current runtime before acting.

## Routing table

First apply the global order in `SKILL.md`: reusable project assets outrank every generation route below.

| Need | Preferred generation route | Next route | Final fallback | Do not do |
| --- | --- | --- | --- | --- |
| Short synthetic UI/game SFX | Bundled procedural generator | Available documented first-party SFX capability | Already-configured SFX generator, then prompts | Spend credits for a sound that can be synthesized locally |
| Realistic Foley / environmental SFX | Available documented first-party SFX capability | Already-configured SFX generator | Asset map + prompts | Pretend a speech model is an SFX generator |
| Ambience | Available documented first-party ambience capability | Already-configured audio generator | Asset map + prompts | Force procedural synthesis when realism matters |
| Background music | Available documented first-party music capability | Already-configured music generator | Asset map + music prompts | Send music prompts to a speech-only model |
| Voice / narration | Available documented first-party speech capability | Already-configured speech generator | Asset map + voice prompts | Treat TTS as music or general SFX generation |

## OpenAI boundary

The current official OpenAI text-to-speech guide documents spoken-audio generation through the speech endpoint and speech models. That documentation establishes a voice route only; it does not establish music or sound-effect generation. Re-check the tools actually exposed by the current runtime and current official documentation before every provider-backed generation task.

If an OpenAI capability is unavailable in the current agent/runtime, do not attempt to install unofficial shims or silently switch to a paid third-party provider.

## External and local generators

A richer generator is eligible only when one of these is true:

- it is already installed locally;
- it is already exposed as a tool in the current runtime; or
- the user has explicitly authorized installation, credentials, and any cost.

Before generation, check:

1. requested media type is supported;
2. output may be used under the project's intended license/distribution model;
3. expected cost is allowed;
4. output format can be integrated into the target runtime;
5. the prompt does not depend on direct imitation of protected music or a living artist's distinctive style.

If capability, price or credit consumption, or distribution rights remain unknown, do not call the provider. Return the asset map and exact generation prompts with the unresolved field identified. Existing credentials or a connected tool prove access, not approval to incur cost.

## Provenance note

For non-procedural generated assets, record at minimum:

```text
asset: <path or logical name>
category: sfx | ambience | music | voice
provider: <provider/tool>
model_or_mode: <when known>
prompt: <generation prompt>
generated_at: <date>
license_note: <material restriction or source URL when applicable>
```

Use an existing asset manifest when the target project already has one. Otherwise keep the note task-local unless the user wants durable provenance committed to the project.

## Prompt-only fallback

For each unresolved asset, provide enough information for a later operator to generate it without redoing product analysis:

```text
asset: <logical name and intended output path>
status: not generated
category: sfx | ambience | music | voice
trigger_or_scene: <product event>
duration_and_loop: <target duration; one-shot or loop>
delivery: <codec, channels, sample rate, or project convention when known>
prompt: <exact audible production prompt>
negative_constraints: <for example no music, no voice, dry, no clipping>
provider_requirement: <capability needed; do not invent a provider>
license_requirement: <intended distribution and unresolved rights>
```

Keep `status: not generated` until a real output file has been produced and validated.
