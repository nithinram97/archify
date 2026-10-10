#!/usr/bin/env python3
"""
Original soundtrack for the ERM 2.0 trailer (storyboard v3, 94 s), synthesized from scratch with numpy:
no samples, no third-party recordings. Every cue is placed on the trailer's timeline.

  0-17   Globe and siglums   A minor pad (Am9, F, C, G), soft plucks, a chime on each country, whooshes on the
                             long spins, a shimmer as the dots fly, a heartbeat pulse, riser into the hub dive
  17-23  Your ERM            the same pad, quieter
  23-29  Until now           low drone and a ticking clock, fading to nothing
  29-33  The turn            silence, one deep hit on "From the ground up", a rising shimmer on the light line
  33-41  Gate                the beat comes in (C, G, Am, F); a zap as each screen crosses
  41-77  Inside the app      full groove at 120 bpm, a whoosh on every push between screens, sparkles on NEW
  77-84  Brought to you by   soft pad and bells, a tuned tick per typed letter, riser
  83-94  ERM 2.0             impact, big Cmaj9, bells on the tagline, fade out

Writes 48 kHz / 16-bit stereo WAVs next to this script:
  erm2_trailer_mix.wav (music + effects), erm2_trailer_music.wav, erm2_trailer_sfx.wav

Run: python3 make_trailer_audio.py  (needs numpy). If you retime the trailer, change the times below.
License of the output: CC0-1.0, like the Clairvoyant brand kit's audio.
"""

import os
import wave

import numpy as np

SR = 48000
DUR = 94.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
HERE = os.path.dirname(os.path.abspath(__file__))

music = np.zeros((N, 2))
sfx = np.zeros((N, 2))


# ---------------------------------------------------------------------------------------------- helpers
def tt(n):
    return np.arange(n) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(buf, sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    n = min(len(sig), N - i)
    th = (pan + 1) * np.pi / 4
    if sig.ndim == 1:
        buf[i:i + n, 0] += sig[:n] * gain * np.cos(th) * np.sqrt(2)
        buf[i:i + n, 1] += sig[:n] * gain * np.sin(th) * np.sqrt(2)
    else:
        buf[i:i + n] += sig[:n] * gain


def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    e = np.full(n, s)
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = min(na, n)
    e[:na] = np.linspace(0, 1, na, endpoint=False)
    nd = min(nd, n - na)
    e[na:na + nd] = np.linspace(1, s, nd, endpoint=False)
    nr = min(nr, n)
    e[n - nr:] *= np.linspace(1, 0, nr)
    return e


def additive(f, dur, harm=8, roll=1.2, decay=None):
    n = int(dur * SR)
    t = tt(n)
    out = np.zeros(n)
    for k in range(1, harm + 1):
        if f * k > 15000:
            break
        part = np.sin(2 * np.pi * f * k * t + rng.uniform(0, 6.28)) / k ** roll
        if decay is not None:
            part *= np.exp(-t * decay * (1 + 0.6 * (k - 1)))
        out += part
    return out


def lowpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


# ---------------------------------------------------------------------------------------------- instruments
def pad(notes, dur, a=0.8, r=1.0):
    n = int(dur * SR)
    out = np.zeros(n)
    for m in notes:
        for cents in (-7, 7):
            out += additive(midi(m) * 2 ** (cents / 1200), dur, harm=7, roll=1.6)
    t = tt(n)
    out *= 1 + 0.08 * np.sin(2 * np.pi * 0.25 * t)
    return out * adsr(n, a, 0.3, 0.85, r) / (len(notes) * 2.5)


def pluck(m, dur=0.7):
    n = int(dur * SR)
    return additive(midi(m), dur, harm=6, roll=1.0, decay=5.0) * adsr(n, 0.003, 0.05, 1.0, 0.1) * 0.6


def bell(m, dur=2.5):
    n = int(dur * SR)
    t = tt(n)
    f = midi(m)
    out = np.zeros(n)
    for ratio, amp, dec in ((1, 1, 1.4), (2.0, 0.45, 2.2), (2.76, 0.35, 3.0), (4.07, 0.2, 4.5), (5.4, 0.12, 6.0)):
        out += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dec)
    return out * adsr(n, 0.002, 0.05, 1.0, 0.3) * 0.4


def bass(m, dur):
    n = int(dur * SR)
    t = tt(n)
    f = midi(m)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t)
    return np.tanh(1.6 * x) * adsr(n, 0.005, 0.08, 0.6, 0.06) * 0.5


def kick(heavy=False):
    dur = 0.9 if heavy else 0.45
    n = int(dur * SR)
    t = tt(n)
    f = 45 + 75 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * (4 if heavy else 9))
    x[:200] += rng.uniform(-0.4, 0.4, 200) * np.linspace(1, 0, 200)
    return np.tanh(1.5 * x)


def hat(open_=False):
    n = int((0.25 if open_ else 0.07) * SR)
    t = tt(n)
    x = highpass(rng.uniform(-1, 1, n), 7000)
    return x * np.exp(-t * (14 if open_ else 70)) * 0.6


def clap():
    n = int(0.3 * SR)
    t = tt(n)
    x = lowpass(highpass(rng.uniform(-1, 1, n), 900), 5000)
    env = np.exp(-t * 14)
    for off in (0.0, 0.011, 0.022):
        env += 0.6 * np.exp(-np.clip(t - off, 0, None) * 120) * (t >= off)
    return x * env * 0.5


def sweep(dur, up=True, peak=0.5):
    """Filtered-noise whoosh: crossfades between low and high passes; `peak` = where the envelope peaks."""
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    x = rng.uniform(-1, 1, n)
    bands = [lowpass(x, c) for c in (400, 1500, 5000, 14000)]
    pos = t if up else 1 - t
    pos = pos * (len(bands) - 1)
    out = np.zeros(n)
    for i, b in enumerate(bands):
        out += b * np.clip(1 - np.abs(pos - i), 0, 1)
    env = np.where(t < peak, (t / peak) ** 2, ((1 - t) / (1 - peak)) ** 1.5)
    return out * env


def whoosh(dur=0.6):
    return sweep(dur, True, 0.55) * 0.9


def riser(dur):
    n = int(dur * SR)
    t = tt(n)
    f = 180 * (8 ** (t / dur))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    return (sweep(dur, True, 0.97) + tone) * np.linspace(0.05, 1, n) ** 2


def boom(dur=3.0):
    n = int(dur * SR)
    t = tt(n)
    sub = np.sin(2 * np.pi * 38 * t) * np.exp(-t * 1.4)
    burst = lowpass(rng.uniform(-1, 1, n), 900) * np.exp(-t * 9)
    k = np.zeros(n)
    kk = kick(True)
    k[:len(kk)] = kk
    return np.tanh(1.2 * (sub + 0.6 * burst + 0.8 * k))


def tick(f=2600, dur=0.05):
    n = int(dur * SR)
    t = tt(n)
    click = highpass(rng.uniform(-1, 1, n), 3000) * np.exp(-t * 400)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 90) + click) * 0.5


def sparkle(dur=1.2, base=84, count=9):
    n = int(dur * SR)
    out = np.zeros(n)
    for _ in range(count):
        b = bell(base + int(rng.choice([0, 2, 4, 7, 9, 12])), 0.9) * 0.35
        i = int(rng.uniform(0, dur - 0.9) * SR)
        out[i:i + len(b)] += b[:n - i]
    return out


# ---------------------------------------------------------------------------------------------- score
CH = {  # pad voicings and bass roots
    'Am9': ([57, 60, 64, 67, 71], 45), 'F': ([53, 57, 60, 64], 41), 'C': ([55, 60, 64, 67], 48),
    'G': ([55, 59, 62, 67], 43), 'Cmaj9': ([48, 55, 60, 62, 64, 67, 71], 36),
}


def progression(t0, t1, names, bar=2.0, gain=0.16, a=0.6, r=1.0):
    t = t0
    i = 0
    while t < t1 - 1e-6:
        d = min(bar, t1 - t)
        notes, _ = CH[names[i % len(names)]]
        add(music, pad(notes, d + r * 0.6, a, r), t, gain)
        t += bar
        i += 1


def arps(t0, t1, names, step=0.25, gain=0.07, octave=12, bar=2.0):
    t = t0
    k = 0
    while t < t1 - 1e-6:
        notes, _ = CH[names[int((t - t0) // bar) % len(names)]]
        m = notes[k % len(notes)] + octave
        add(music, pluck(m), t, gain, pan=0.35 if k % 2 else -0.35)
        t += step
        k += 1


def groove(t0, t1, names, clap_on=True, hats=True, bass_on=True, stabs=True, bar=2.0, kick_gain=0.45):
    t = t0
    while t < t1 - 1e-6:
        beat = round((t - t0) / 0.5)
        add(music, kick(), t, kick_gain)
        if clap_on and beat % 2 == 1:
            add(music, clap(), t, 0.32, 0.1)
        if hats:
            add(music, hat(), t + 0.25, 0.16, 0.25)
            add(music, hat(beat % 4 == 3), t, 0.08, -0.25)
        notes, root = CH[names[int((t - t0) // bar) % len(names)]]
        if bass_on:
            add(music, bass(root, 0.22), t, 0.42)
            add(music, bass(root + 12 if beat % 2 else root, 0.2), t + 0.25, 0.3)
        if stabs and beat % 2 == 1:
            for m in notes[1:]:
                add(music, pluck(m + 12, 0.25), t + 0.25, 0.035)
        t += 0.5


# 0-17 · globe and siglums
progression(0.0, 16.0, ['Am9', 'F', 'C', 'G'], gain=0.24, a=1.2)
add(music, pad(CH['G'][0], 1.6, 0.2, 0.6), 16.0, 0.24)
arps(1.0, 16.0, ['Am9', 'F', 'C', 'G'], step=0.25, gain=0.085)
for i, t in enumerate([1.4, 3.0, 4.4, 5.6, 7.0, 8.4]):  # a chime on each country
    add(sfx, bell([76, 79, 81, 84, 86, 88][i], 2.5), t - 0.05, 0.3, pan=-0.2 + i * 0.08)
for t, d in ((6.3, 0.9), (7.65, 1.0)):  # the long spins
    add(sfx, whoosh(d), t, 0.35)
add(sfx, sparkle(1.4, 81, 7), 9.0, 0.5)  # the totals appear
add(sfx, sweep(1.8, True, 0.4), 10.0, 0.3)  # the dots lift off
add(sfx, sparkle(1.8, 84, 12), 10.1, 0.5)
for t in np.arange(10.0, 16.0, 0.5):  # heartbeat pulse
    add(music, kick(), t, 0.22 + 0.1 * (t - 10) / 6)
for i in range(7):  # siglum nodes pop
    add(sfx, pluck([72, 74, 76, 79, 81, 84, 86][i], 0.6), 11.3 + i * 0.22, 0.12, pan=-0.5 + i / 6)
add(sfx, riser(1.35), 15.65, 0.42)
add(sfx, boom(2.0), 17.0, 0.35)
add(music, bell(84, 3.0), 17.0, 0.18)

# 17-23 · your ERM
progression(17.0, 23.0, ['F', 'C', 'G'], gain=0.2, a=0.4)
arps(17.0, 22.5, ['F', 'C', 'G'], step=0.5, gain=0.065)

# 23-29 · until now: drone and a ticking clock
drone = pad([33, 40, 45], 6.0, 1.0, 1.6) + 0.3 * pad([46], 6.0, 2.0, 1.6)  # a slightly sour B-flat
add(music, drone, 23.0, 0.26)
for k, t in enumerate(np.arange(23.3, 28.6, 0.5)):
    add(sfx, tick(2300 if k % 2 else 1700, 0.06), t, 0.28, pan=0.15 if k % 2 else -0.15)

# 29-33 · the turn
add(sfx, boom(3.5), 30.3, 0.55)
add(music, pad([24, 36, 43, 48], 2.5, 0.02, 1.4), 30.3, 0.22)
add(sfx, riser(1.0), 32.0, 0.3)
add(sfx, sparkle(1.0, 88, 6), 32.2, 0.35)

# 33-41 · gate: the beat comes in
progression(33.0, 41.0, ['C', 'G', 'Am9', 'F'], gain=0.15, a=0.3)
groove(33.0, 35.0, ['C'], clap_on=False, hats=False, stabs=False)
groove(35.0, 41.0, ['G', 'Am9', 'F'], clap_on=False, stabs=False)
for k in range(6):  # each screen crosses the gate
    tc = 33 + 0.9 + k * 0.75 + 9.5 / 4.2
    add(sfx, sweep(0.5, True, 0.7), tc - 0.35, 0.28)
    add(sfx, bell(91 + (k % 3) * 2, 1.2), tc, 0.14, pan=0.3)

# 41-77 · inside the app
progression(41.0, 77.0, ['C', 'G', 'Am9', 'F'], gain=0.12, a=0.2, r=0.6)
groove(41.0, 76.5, ['C', 'G', 'Am9', 'F'])
arps(65.0, 76.0, ['F', 'G', 'Am9'], step=0.125, gain=0.04, octave=24, bar=2.0)
for t1 in (45, 49, 53, 57, 61, 65, 71):  # push between screens
    add(sfx, whoosh(0.6), t1 - 0.5, 0.42)
for t in (65.5, 71.5):  # NEW
    add(sfx, sparkle(1.0, 86, 8), t, 0.45)
add(sfx, riser(1.2), 72.3, 0.3)  # slideshow goes full screen
add(sfx, bell(79, 2.0), 73.5, 0.2)

# 77-84 · brought to you by
add(music, pad(CH['F'][0], 3.6, 0.8, 1.0), 77.0, 0.16)
add(music, pad(CH['G'][0], 3.4, 0.6, 0.8), 80.2, 0.16)
add(sfx, bell(79, 2.0), 77.9, 0.22, -0.3)   # Skywise
add(sfx, bell(84, 2.0), 78.6, 0.22, 0.3)    # Clairvoyant mark
step = 1.2 / 11
for i in range(11):  # one tuned tick per typed letter
    add(sfx, tick([2100, 2350, 2640, 2800, 3140][i % 5], 0.05), 79.2 + i * step, 0.3, pan=0.25)
add(sfx, riser(1.5), 81.8, 0.45)

# 83.3-94 · ERM 2.0
add(sfx, boom(4.0), 83.3, 0.6)
add(music, pad(CH['Cmaj9'][0], 10.7, 0.05, 3.5), 83.3, 0.3)
add(music, bass(36, 6.0) * np.exp(-tt(int(6.0 * SR)) * 0.4), 83.3, 0.4)
for i, m in enumerate([72, 76, 79, 84, 88]):
    add(music, bell(m, 4.0), 83.35 + i * 0.12, 0.16, pan=-0.4 + i * 0.2)
add(sfx, sparkle(1.4, 88, 9), 84.6, 0.4)   # tagline
add(sfx, sparkle(1.2, 91, 6), 85.4, 0.3)   # Coming soon


# ---------------------------------------------------------------------------------------------- mix
def reverb(buf, wet, seconds=2.2):
    n = int(seconds * SR)
    t = tt(n)
    out = buf.copy() * (1 - wet * 0.3)
    size = 1 << int(np.ceil(np.log2(len(buf) + n)))
    for ch in range(2):
        ir = rng.uniform(-1, 1, n) * np.exp(-t / 0.42)
        ir = lowpass(ir, 6000)
        ir /= np.sqrt(np.sum(ir ** 2))
        y = np.fft.irfft(np.fft.rfft(buf[:, ch], size) * np.fft.rfft(ir, size), size)[:len(buf)]
        out[:, ch] += wet * y
    return out


music_w = reverb(music, 0.35)
sfx_w = reverb(sfx, 0.18)
fade = np.ones(N)
fi, fo = int(0.6 * SR), int(91.5 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[fo:] = np.linspace(1, 0, N - fo)
music_w *= fade[:, None]
sfx_w *= fade[:, None]
mix = music_w + sfx_w
peak = np.max(np.abs(np.tanh(mix * 1.1)))
scale = 10 ** (-1 / 20) / peak


def write(name, x):
    y = np.clip(np.tanh(x * 1.1) * scale, -1, 1)
    data = (y * 32767).astype('<i2').tobytes()
    with wave.open(os.path.join(HERE, name), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)
    print('wrote', name)


write('erm2_trailer_mix.wav', mix)
write('erm2_trailer_music.wav', music_w)
write('erm2_trailer_sfx.wav', sfx_w)
