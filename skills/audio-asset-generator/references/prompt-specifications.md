# Audio Prompt Specifications

Read the relevant category only when writing a generator prompt or prompt-only handoff.

## Write prompts as production specifications

For generated audio, prompts should describe audible properties rather than implementation details.

For SFX, specify:

- source/action;
- material or texture;
- intensity;
- environment or dryness;
- duration;
- perspective when relevant;
- no-music or no-voice constraints when needed.

For music, specify:

- emotional role in the product;
- genre and instrumentation;
- approximate tempo or energy;
- loop behavior;
- desired duration;
- vocals or no vocals;
- scene transitions or intensity variants when needed.

For ambience, specify:

- environment and time or weather context;
- persistent bed, foreground events, and any intermittent layers;
- density, motion, and variation over time;
- acoustic space, listener perspective, and spatial treatment when relevant;
- target loop duration and an unobtrusive seam; and
- exclusions such as no music, no voice, or no identifiable recordings.

For voice, specify:

- the exact approved script without silently rewriting it;
- language, locale, and pronunciations or phonetic guidance;
- character or narrator role, emotional intent, pace, and energy;
- pauses, emphasis, and delivery variants when relevant;
- dry or environmental recording treatment and file segmentation; and
- stock or custom voice status, speaker authorization when applicable, and required AI-generated-voice disclosure.

Do not request an imitation of a recognizable real person's voice without documented authorization. If authorization, consent evidence, or disclosure ownership is unresolved, stop at a voice asset map and prompt rather than generating or integrating the voice.

Do not name copyrighted songs or ask for direct imitation of a living artist's distinctive style when a neutral sonic description will achieve the goal.
