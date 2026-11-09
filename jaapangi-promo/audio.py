"""자아판기 홍보영상 배경음악 + 효과음 합성 (저작권 걱정 없는 자체 생성 음원).

사용법: python3 audio.py  -> jaapangi_audio.wav
"""
import wave
import numpy as np

SR = 44100
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def place(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * (1 - pan) * 0.5 ** 0.5 * 1.2
    R[i:i + len(sig)] += sig * (1 + pan) * 0.5 ** 0.5 * 1.2


def tt(d):
    return np.arange(int(d * SR)) / SR


def epiano(f, d=1.6):
    x = tt(d)
    env = np.exp(-x * 2.2) * np.minimum(1, x / 0.005)
    s = np.sin(2 * np.pi * f * x) + 0.35 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 4) \
        + 0.08 * np.sin(2 * np.pi * 3 * f * x) * np.exp(-x * 6)
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * x)
    return s * env * trem


def bass(f, d=0.8):
    x = tt(d)
    env = np.exp(-x * 3) * np.minimum(1, x / 0.01)
    return (np.sin(2 * np.pi * f * x) + 0.2 * np.sin(2 * np.pi * 2 * f * x)) * env


def kick():
    x = tt(0.35)
    f = 50 + 70 * np.exp(-x * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 9)


def lowpass(sig, k):
    return np.convolve(sig, np.ones(k) / k, mode='same')


def hat():
    x = tt(0.06)
    n = rng.standard_normal(len(x))
    return (n - lowpass(n, 6)) * np.exp(-x * 70)


def snare_brush():
    x = tt(0.25)
    n = rng.standard_normal(len(x))
    return lowpass(n, 3) * np.exp(-x * 18)


# ---------------- 음악 (80 BPM, Fmaj7-Em7-Dm7-Cmaj7) ----------------
BPM = 80
beat = 60 / BPM
chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
roots = [41, 40, 38, 36]
music_start = 0.6
drums_start = 3.5
bar = 0
t = music_start
while t < DUR - 0.5:
    ch = chords[bar % 4]
    # 코드 (살짝 롤링)
    for k, n in enumerate(ch):
        place(epiano(midi(n + 12), 2.8), t + k * 0.018, 0.07, pan=(k - 1.5) * 0.15)
    # 아르페지오 (8분음)
    arp = [ch[0] + 24, ch[2] + 12, ch[3] + 12, ch[1] + 24, ch[2] + 24, ch[3] + 12, ch[1] + 24, ch[2] + 12]
    for k, n in enumerate(arp):
        if bar == 0 and k < 4:
            continue
        place(epiano(midi(n), 0.9), t + k * beat / 2 + 0.01 * (k % 2), 0.045, pan=0.3 if k % 2 else -0.3)
    # 베이스
    if t >= drums_start - 0.1:
        place(bass(midi(roots[bar % 4])), t, 0.28)
        place(bass(midi(roots[bar % 4] + 7)), t + 2.5 * beat, 0.18)
    # 드럼 (로파이)
    for b in range(4):
        bt = t + b * beat
        if bt < drums_start:
            continue
        if b in (0, 2):
            place(kick(), bt, 0.42)
        if b in (1, 3):
            place(snare_brush(), bt, 0.12)
        place(hat(), bt + beat / 2 + 0.02, 0.10, pan=0.25)
    t += 4 * beat
    bar += 1

# 바이닐 노이즈
crackle = np.zeros(N)
idx = rng.integers(0, N, 900)
crackle[idx] = rng.standard_normal(900) * 0.25
hiss = lowpass(rng.standard_normal(N), 30) * 0.012
L += crackle + hiss
R += np.roll(crackle, 37) + hiss

# 음악 엔벨로프 (끝부분 페이드아웃)
fade = np.ones(N)
fo = int(28.6 * SR)
fade[fo:] = np.linspace(1, 0, N - fo)
L *= fade
R *= fade

# ---------------- 효과음 ----------------
def bell(freqs, d=1.2, decay=4.0):
    x = tt(d)
    return sum(np.sin(2 * np.pi * f * x) * np.exp(-x * decay * (1 + i * 0.4)) / (i + 1)
               for i, f in enumerate(freqs))


def click():
    x = tt(0.05)
    return (rng.standard_normal(len(x)) * 0.6 + np.sin(2 * np.pi * 1800 * x)) * np.exp(-x * 120)


def hum(d):
    x = tt(d)
    return (np.sin(2 * np.pi * 100 * x) + 0.5 * np.sin(2 * np.pi * 200 * x)) * 0.5


# 0.35~0.85s 조명 깜빡임
for ts in (0.35, 0.45, 0.6, 0.68, 0.85):
    place(click(), ts, 0.5)
h = hum(1.4) * np.minimum(1, tt(1.4) / 0.05) * np.exp(-tt(1.4) * 2.5)
place(h, 0.85, 0.12)
# 4.9s 동전 낙하 / 5.2s 투입
place(bell([2350, 3720, 5210], 0.6, 9), 4.62, 0.12, pan=0.2)
place(bell([1900, 3100], 0.5, 10), 5.2, 0.18, pan=0.2)
place(click(), 5.22, 0.4)
# 5.45~6.75 버튼 불빛 순회 (작은 틱)
for k in range(5):
    place(bell([2600], 0.08, 40), 5.45 + k * 0.3, 0.05)
# 6.75 버튼 눌림
place(click(), 6.75, 0.8)
place(bell([880, 1320], 0.4, 8), 6.78, 0.12)
# 8.35~ 컵 낙하 (통통)
for ts, g in [(8.62, .35), (8.80, .15), (8.9, .07)]:
    x = tt(0.25)
    place(np.sin(2 * np.pi * 220 * x) * np.exp(-x * 25), ts, g)
    place(bell([1250, 2900], 0.3, 14), ts, g * 0.4)
# 9.1~11.7 추출/우유 따르는 소리
pour = rng.standard_normal(int(2.6 * SR))
pour = lowpass(pour, 4) - lowpass(pour, 40)
x = tt(2.6)
pe = np.minimum(1, x / 0.15) * np.minimum(1, (2.6 - x) / 0.2)
pe *= 0.7 + 0.3 * np.sin(2 * np.pi * 7 * x) ** 2
gap = (x > 1.2) & (x < 1.3)
pe[gap] *= 0.1
place(pour * pe, 9.1, 0.10)
# 12.2 장면 전환 차임 / 13.6 하트 완성 반짝
place(bell([midi(84), midi(88)], 1.4, 3), 12.25, 0.07)
for k, n in enumerate([88, 91, 96]):
    place(bell([midi(n)], 1.0, 4), 13.55 + k * 0.08, 0.06)
# 14.2 / 19.0 와이프 휙
def whoosh(d=0.55):
    x = tt(d)
    n = rng.standard_normal(len(x))
    n = lowpass(n, 8)
    return n * np.sin(np.pi * x / d) ** 2
place(whoosh(), 14.0, 0.25)
place(whoosh(), 18.8, 0.25)
# 20.2~ 컵 등장 팝
for k in range(4):
    place(bell([midi(79 + [0, 4, 7, 12][k])], 0.4, 10), 20.3 + k * 0.28, 0.07)
# 26.0 이름 공개
place(bell([midi(72), midi(79), midi(84), midi(88)], 2.5, 1.6), 26.0, 0.08)
# 28.0 엔드카드 딩
place(bell([midi(84), midi(91)], 2.0, 2.2), 28.05, 0.08)

# ---------------- 마스터 ----------------
st = np.stack([L, R], axis=1)
st /= np.max(np.abs(st)) / 0.89
st = np.tanh(st * 1.1) / np.tanh(1.1)
pcm = (st * 32767).astype(np.int16)
with wave.open('jaapangi_audio.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('done: jaapangi_audio.wav')
