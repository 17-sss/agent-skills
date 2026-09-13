# Web audio delivery

Use these defaults only when the target is a browser-based product and the repository has no stronger convention.

## Playback behavior

- Assume browsers may block audible autoplay until a user gesture. Start or resume background audio from an allowed interaction rather than fighting the policy.
- Separate music and SFX volume controls when the product already exposes that distinction.
- Avoid creating a new `Audio` object on every frame or render. Reuse a small playback layer or the repository's existing audio abstraction.
- Limit simultaneous duplicates for loud or frequently triggered effects when stacking becomes unpleasant.
- Pause or reduce long-running audio when the application's existing lifecycle policy requires it.

## Loading

- Preload small latency-sensitive UI/game SFX when bundle and memory cost are acceptable.
- Lazy-load long music and ambience unless immediate playback is a product requirement.
- Keep source assets out of the client bundle when the framework serves them more efficiently as static/public files.

## Formats

Follow existing project format support first. When choosing from scratch, verify the project's browser support matrix before encoding. A broadly supported fallback may be preferable to a smaller codec when compatibility matters more than bytes.

Keep masters lossless when the project has an asset-source workflow. Avoid repeatedly transcoding lossy files.

## Looping

For loopable music or ambience:

- trim unintended leading/trailing silence;
- avoid fades that create an obvious volume dip at the seam unless the composition expects it;
- audition the seam in the real playback layer when possible;
- do not claim a seamless loop from waveform metadata alone.

## Verification

For a browser integration, verify as much of this as the runtime permits:

1. first allowed interaction unlocks audio;
2. expected trigger plays the correct logical asset;
3. repeated triggers do not create runaway overlap;
4. music lifecycle behaves correctly across route/state changes;
5. mute and volume controls affect the intended buses/categories;
6. production build still resolves static asset URLs.
