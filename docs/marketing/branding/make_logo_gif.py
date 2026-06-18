"""
Генератор анімації логотипа Family Wallet.

Анімація: fade-in + zoom-pop + золотий відблиск (shimmer), зациклена.
Вхід:  logo_white_round.png (512x512, RGBA, білий бейдж із золотим написом)
Вихід:
  - logo_animated.gif      темний фон #0D0C0A (Product Hunt / соцмережі)
  - logo_animated.webp     ПРОЗОРИЙ фон, плавна альфа (README, веб)
  - logo_animated.png      ПРОЗОРИЙ фон, APNG (універсальний fallback)

GIF підтримує лише 1-бітну прозорість (рвані краї + без плавного fade),
тому для прозорого фону використовуємо WebP та APNG зі справжнім альфа-каналом.

Запуск:   python make_logo_gif.py
Залежності: pip install Pillow numpy
"""

from pathlib import Path
import numpy as np
from PIL import Image

# ── Налаштування ───────────────────────────────────────────────────────────
HERE = Path(__file__).parent
SRC = HERE / "logo_white_round.png"
OUT_GIF = HERE / "logo_animated.gif"
OUT_WEBP = HERE / "logo_animated.webp"
OUT_APNG = HERE / "logo_animated.png"

CANVAS = 400               # розмір кадру (квадрат), px
LOGO_MAX = 340             # макс. розмір логотипа на полотні, px
BG = (13, 12, 10)          # фон #0D0C0A (Ink/Primary) — золото на ньому "грає"
FRAME_MS = 40              # тривалість кадру (40ms ≈ 25 fps)

# Фази (в кадрах)
F_IN = 16                  # fade-in + zoom-pop
F_HOLD1 = 6                # коротка пауза перед відблиском
F_SHINE = 22               # прохід золотого відблиску
F_HOLD2 = 18               # фінальна пауза (логотип стоїть)
SHINE_COLOR = (245, 235, 190)   # колір відблиску (світле золото #F5EBBE)
SHINE_STRENGTH = 0.85           # інтенсивність відблиску 0..1
SHINE_BAND = 0.16               # ширина смуги відблиску (частка діагоналі)


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def load_logo() -> np.ndarray:
    """Завантажує логотип, тримить прозорі поля, вписує в LOGO_MAX, центрує на CANVAS."""
    im = Image.open(SRC).convert("RGBA")
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    scale = LOGO_MAX / max(w, h)
    im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.paste(im, ((CANVAS - im.width) // 2, (CANVAS - im.height) // 2), im)
    return np.asarray(canvas, dtype=np.float32)  # (H, W, 4)


def composite(logo_rgba: np.ndarray, alpha_mul: float, shine_pos, transparent=False):
    """Збирає один кадр: логотип (з множником прозорості + відблиском).

    transparent=False → на фоні BG (RGB, для GIF).
    transparent=True  → на прозорому фоні (RGBA, для WebP/APNG).
    """
    rgb = logo_rgba[..., :3].copy()
    a = logo_rgba[..., 3:4] / 255.0 * alpha_mul

    if shine_pos is not None:
        h, w = rgb.shape[:2]
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
        diag = (xs + ys) / (w + h)                 # 0..1 діагональна координата
        band = np.exp(-((diag - shine_pos) / SHINE_BAND) ** 2)[..., None]
        shine = np.array(SHINE_COLOR, dtype=np.float32)
        rgb = rgb + (shine - rgb) * band * SHINE_STRENGTH
        rgb = np.clip(rgb, 0, 255)

    if transparent:
        out = np.concatenate([rgb, a * 255.0], axis=-1)
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")

    bg = np.array(BG, dtype=np.float32)
    out = bg * (1 - a) + rgb * a
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


def scale_logo(logo_rgba: np.ndarray, factor: float) -> np.ndarray:
    """Масштабує логотип навколо центру (для zoom-pop), повертає полотно CANVAS."""
    if abs(factor - 1.0) < 1e-3:
        return logo_rgba
    im = Image.fromarray(logo_rgba.astype(np.uint8), "RGBA")
    nw, nh = max(1, round(CANVAS * factor)), max(1, round(CANVAS * factor))
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.paste(im, ((CANVAS - nw) // 2, (CANVAS - nh) // 2), im)
    return np.asarray(canvas, dtype=np.float32)


def build_frames(transparent=False) -> list[Image.Image]:
    logo = load_logo()
    frames = []

    # Фаза 1: fade-in + zoom-pop (0.92 → 1.0)
    for i in range(F_IN):
        t = ease_out_cubic((i + 1) / F_IN)
        frames.append(composite(scale_logo(logo, 0.92 + 0.08 * t), t, None, transparent))

    # Фаза 2: пауза
    for _ in range(F_HOLD1):
        frames.append(composite(logo, 1.0, None, transparent))

    # Фаза 3: золотий відблиск проходить по діагоналі
    for i in range(F_SHINE):
        pos = -0.3 + 1.6 * ((i + 1) / F_SHINE)     # від -0.3 до 1.3
        frames.append(composite(logo, 1.0, pos, transparent))

    # Фаза 4: фінальна пауза
    for _ in range(F_HOLD2):
        frames.append(composite(logo, 1.0, None, transparent))

    return frames


def save_gif():
    frames = build_frames(transparent=False)
    paletted = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
    paletted[0].save(
        OUT_GIF, save_all=True, append_images=paletted[1:],
        duration=FRAME_MS, loop=0, optimize=True, disposal=2,
    )
    _report(OUT_GIF, len(frames), "темний фон")


def save_webp():
    frames = build_frames(transparent=True)
    frames[0].save(
        OUT_WEBP, save_all=True, append_images=frames[1:],
        duration=FRAME_MS, loop=0, lossless=True, method=6,
        disposal=2, background=(0, 0, 0, 0),
    )
    _report(OUT_WEBP, len(frames), "ПРОЗОРИЙ фон")


def save_apng():
    frames = build_frames(transparent=True)
    frames[0].save(
        OUT_APNG, save_all=True, append_images=frames[1:],
        duration=FRAME_MS, loop=0, disposal=1,
    )
    _report(OUT_APNG, len(frames), "ПРОЗОРИЙ фон (APNG)")


def _report(path: Path, n: int, note: str):
    size_kb = path.stat().st_size / 1024
    print(f"OK: {path.name:22s} | {n} кадрів | {CANVAS}x{CANVAS}px | {size_kb:6.0f} KB | {note}")


def main():
    save_gif()
    save_webp()
    save_apng()


if __name__ == "__main__":
    main()
