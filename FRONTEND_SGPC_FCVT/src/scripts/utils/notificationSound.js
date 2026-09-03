let audioContext =
  null;

let unlocked =
  false;

let unlockInstalled =
  false;


const clamp = (
  value,
  min,
  max
) =>
  Math.min(
    max,
    Math.max(
      min,
      value
    )
  );


const getAudioContext = () => {
  if (
    typeof window ===
    "undefined"
  ) {
    return null;
  }

  const AudioContextClass =
    window.AudioContext ||
    window.webkitAudioContext;

  if (
    !AudioContextClass
  ) {
    return null;
  }

  if (
    !audioContext
  ) {
    audioContext =
      new AudioContextClass();
  }

  return audioContext;
};


const tryUnlock =
  async () => {
    const context =
      getAudioContext();

    if (
      !context
    ) {
      return false;
    }

    try {
      if (
        context.state ===
        "suspended"
      ) {
        await context.resume();
      }

      unlocked =
        context.state ===
        "running";

      return unlocked;
    } catch {
      return false;
    }
  };


export const installNotificationSoundUnlock =
  () => {
    if (
      typeof window ===
        "undefined" ||
      unlockInstalled
    ) {
      return;
    }

    unlockInstalled =
      true;

    const unlock =
      async () => {
        const success =
          await tryUnlock();

        if (
          !success
        ) {
          return;
        }

        window.removeEventListener(
          "pointerdown",
          unlock
        );

        window.removeEventListener(
          "keydown",
          unlock
        );
      };

    window.addEventListener(
      "pointerdown",
      unlock,
      {
        passive: true,
      }
    );

    window.addEventListener(
      "keydown",
      unlock
    );
  };


const scheduleVoice = ({
  context,
  destination,
  type,
  frequency,
  start,
  duration,
  peak,
  detune = 0,
}) => {
  const oscillator =
    context.createOscillator();

  const gain =
    context.createGain();

  oscillator.type =
    type;

  oscillator.frequency
    .setValueAtTime(
      frequency,
      start
    );

  oscillator.detune
    .setValueAtTime(
      detune,
      start
    );

  gain.gain
    .setValueAtTime(
      0.0001,
      start
    );

  gain.gain
    .exponentialRampToValueAtTime(
      Math.max(
        0.0001,
        peak
      ),
      start + 0.018
    );

  gain.gain
    .exponentialRampToValueAtTime(
      0.0001,
      start + duration
    );

  oscillator.connect(
    gain
  );

  gain.connect(
    destination
  );

  oscillator.start(
    start
  );

  oscillator.stop(
    start +
    duration +
    0.03
  );
};


const scheduleChimeNote = ({
  context,
  destination,
  frequency,
  start,
  duration,
  intensity = 1,
}) => {
  scheduleVoice({
    context,
    destination,
    type: "triangle",
    frequency,
    start,
    duration,
    peak:
      0.17 *
      intensity,
  });

  scheduleVoice({
    context,
    destination,
    type: "sine",

    frequency:
      frequency * 2,

    start:
      start + 0.008,

    duration:
      duration * 0.82,

    peak:
      0.055 *
      intensity,

    detune:
      -4,
  });
};


export const playNotificationSound =
  async ({
    force = false,
    volume = 0.82,
  } = {}) => {
    const context =
      getAudioContext();

    if (
      !context
    ) {
      return false;
    }

    if (
      !unlocked ||
      context.state !==
        "running"
    ) {
      const resumed =
        await tryUnlock();

      if (
        !resumed &&
        !force
      ) {
        return false;
      }
    }

    if (
      context.state !==
      "running"
    ) {
      return false;
    }

    const normalizedVolume =
      clamp(
        Number(volume),
        0,
        1
      );

    if (
      normalizedVolume <=
      0
    ) {
      return true;
    }

    const master =
      context.createGain();

    const compressor =
      context
        .createDynamicsCompressor();

    compressor.threshold
      .setValueAtTime(
        -18,
        context.currentTime
      );

    compressor.knee
      .setValueAtTime(
        12,
        context.currentTime
      );

    compressor.ratio
      .setValueAtTime(
        4,
        context.currentTime
      );

    compressor.attack
      .setValueAtTime(
        0.003,
        context.currentTime
      );

    compressor.release
      .setValueAtTime(
        0.18,
        context.currentTime
      );

    master.gain
      .setValueAtTime(
        normalizedVolume *
          0.92,
        context.currentTime
      );

    master.connect(
      compressor
    );

    compressor.connect(
      context.destination
    );

    const now =
      context.currentTime +
      0.015;

    scheduleChimeNote({
      context,
      destination:
        master,

      frequency:
        659.25,

      start:
        now,

      duration:
        0.17,

      intensity:
        0.92,
    });

    scheduleChimeNote({
      context,
      destination:
        master,

      frequency:
        880,

      start:
        now + 0.095,

      duration:
        0.2,

      intensity:
        1,
    });

    scheduleChimeNote({
      context,
      destination:
        master,

      frequency:
        1046.5,

      start:
        now + 0.205,

      duration:
        0.31,

      intensity:
        0.9,
    });

    window.setTimeout(
      () => {
        try {
          master.disconnect();
          compressor.disconnect();
        } catch {
          // Los nodos ya pueden estar cerrados.
        }
      },
      900
    );

    return true;
  };