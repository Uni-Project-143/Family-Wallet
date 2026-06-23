"""
Генератор PDF-версії 05_Promotion_Marketing_Kit.

Конвертує Markdown → стилізований HTML → PDF (xhtml2pdf), додає:
  - логотип Family Wallet у шапці (вимога завдання Б — Hunter Kit);
  - галерею з 5 mobile-скріншотів у розділі «Б) Product Hunt Strategy».

Запуск:    python build_pdf.py
Залежності: pip install markdown xhtml2pdf
Вихід:     05_Promotion_Marketing_Kit.pdf
"""

import re
from pathlib import Path
import markdown
from xhtml2pdf import pisa
from xhtml2pdf.default import DEFAULT_FONT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

HERE = Path(__file__).parent
MD = HERE / "05_Promotion_Marketing_Kit.md"
PDF = HERE / "05_Promotion_Marketing_Kit.pdf"
LOGO = HERE / "branding" / "logo_primary.png"
SHOTS_DIR = HERE.parent.parent / "frontend" / "screenshots_mobile"

ARIAL = "C:/Windows/Fonts/arial.ttf"
ARIAL_BD = "C:/Windows/Fonts/arialbd.ttf"
ARIAL_IT = "C:/Windows/Fonts/ariali.ttf"
ARIAL_BI = "C:/Windows/Fonts/arialbi.ttf"

SCREENSHOTS = [
    ("1-dashboard.jpg", "Dashboard — жива стрічка + донат-діаграма"),
    ("2-secret-gift.jpg", "Secret Gift — прогрес збору на подарунок"),
    ("3-money-request.jpg", "Money Request — запит коштів"),
    ("4-transactions.jpg", "Транзакції — стрічка з реакціями"),
    ("5-connected-cards.jpg", "Connected Cards — картки з балансами"),
]


def strip_emoji(text: str) -> str:
    """Прибирає emoji (xhtml2pdf/Arial їх не рендерить — були б порожні квадрати)."""
    emoji = re.compile(
        "[" "\U0001F300-\U0001FAFF" "\U00002600-\U000027BF"
        "\U0001F1E6-\U0001F1FF" "\U00002190-\U000021FF"
        "\U00002B00-\U00002BFF" "\U0000FE0F" "\U0000200D" "]+",
        flags=re.UNICODE,
    )
    return emoji.sub("", text)


def screenshots_html() -> str:
    """Галерея 5 скріншотів: ряд із 3 + ряд із 2 (через таблицю для xhtml2pdf)."""
    def cell(fname, caption):
        p = (SHOTS_DIR / fname).resolve().as_posix()
        return (
            f'<td class="shot-cell">'
            f'<img src="{p}" class="shot"/>'
            f'<div class="shot-cap">{caption}</div></td>'
        )

    row1 = "".join(cell(f, c) for f, c in SCREENSHOTS[:3])
    row2 = "".join(cell(f, c) for f, c in SCREENSHOTS[3:]) + '<td class="shot-cell"></td>'
    return (
        '<div class="gallery">'
        '<div class="gallery-title">Скріншоти продукту (mobile · реальні дані)</div>'
        f'<table class="shot-table"><tr>{row1}</tr><tr>{row2}</tr></table>'
        "</div>"
    )


def header_html() -> str:
    logo = LOGO.resolve().as_posix()
    return (
        '<div class="cover">'
        f'<img src="{logo}" class="logo"/>'
        '<div class="cover-title">Family Wallet</div>'
        '<div class="cover-sub">Promotion &amp; Marketing Kit</div>'
        "</div>"
    )


def register_fonts():
    """Реєструє Arial напряму в reportlab і додає його в реєстр xhtml2pdf.

    Оминає баг xhtml2pdf на Windows, коли @font-face пише шрифт у temp-файл
    і не може його повторно відкрити (PermissionError). Назви варіантів
    App_<bold><italic> — той самий формат, що використовує xhtml2pdf.
    """
    variants = {
        "App_00": ARIAL, "App_10": ARIAL_BD,
        "App_01": ARIAL_IT, "App_11": ARIAL_BI,
    }
    for name, path in variants.items():
        pdfmetrics.registerFont(TTFont(name, path))
    addMapping("App", 0, 0, "App_00")
    addMapping("App", 1, 0, "App_10")
    addMapping("App", 0, 1, "App_01")
    addMapping("App", 1, 1, "App_11")
    DEFAULT_FONT["app"] = "App"          # css font-family: App → reportlab 'App'


CSS = f"""
@page {{ size: A4; margin: 1.6cm 1.4cm; }}
body {{ font-family: App; font-size: 9.5pt; color: #0D0C0A; line-height: 1.45; }}

h1 {{ font-size: 18pt; color: #9B7A25; border-bottom: 2pt solid #B8973A;
      padding-bottom: 4pt; margin: 14pt 0 8pt; }}
h2 {{ font-size: 13pt; color: #0D0C0A; background: #F2E9C8;
      padding: 4pt 6pt; margin: 14pt 0 6pt; }}
h3 {{ font-size: 11.5pt; color: #9B7A25; margin: 12pt 0 4pt; }}
h4 {{ font-size: 10.5pt; color: #0D0C0A; margin: 10pt 0 3pt; }}
p {{ margin: 4pt 0; }}
a {{ color: #B8973A; text-decoration: none; }}
strong {{ color: #0D0C0A; }}
ul {{ margin: 4pt 0 4pt 10pt; }}
li {{ margin: 2pt 0; }}
hr {{ border: none; border-top: 0.6pt solid #D6D3CE; margin: 10pt 0; }}

code {{ font-family: App; background: #F4F1E9; color: #7A5E1A;
        padding: 1pt 2pt; font-size: 9pt; }}
pre {{ background: #FBF7EC; border: 0.6pt solid #F2E9C8; padding: 6pt;
       font-size: 8.5pt; }}

blockquote {{ border-left: 3pt solid #B8973A; background: #FBF7EC;
              margin: 6pt 0; padding: 5pt 5pt 5pt 9pt; color: #2D2B27; }}

table {{ width: 100%; border-collapse: collapse; margin: 6pt 0; font-size: 8.3pt; }}
th {{ background: #0D0C0A; color: #EAD9A0; padding: 4pt; text-align: left;
      border: 0.5pt solid #9B7A25; }}
td {{ padding: 4pt; border: 0.5pt solid #EAE8E4; vertical-align: top; }}

.cover {{ text-align: center; margin-bottom: 10pt; }}
.logo {{ width: 130px; }}
.cover-title {{ font-size: 22pt; font-weight: bold; color: #9B7A25; }}
.cover-sub {{ font-size: 12pt; color: #6B6860; letter-spacing: 1pt; }}

.gallery {{ margin: 8pt 0; }}
.gallery-title {{ font-size: 10pt; font-weight: bold; color: #9B7A25; margin-bottom: 5pt; }}
.shot-table {{ width: 100%; border-collapse: collapse; }}
.shot-table td {{ border: none; }}
.shot-cell {{ width: 33%; text-align: center; padding: 4pt; }}
.shot {{ width: 145px; border: 0.8pt solid #D6D3CE; }}
.shot-cap {{ font-size: 7.5pt; color: #6B6860; margin-top: 3pt; }}
"""


def main():
    register_fonts()
    raw = strip_emoji(MD.read_text(encoding="utf-8"))

    html_body = markdown.markdown(
        raw, extensions=["tables", "fenced_code", "sane_lists", "nl2br"]
    )

    # Галерея скріншотів — перед розділом «Перший коментар (Makers)»
    marker = "<h4>Перший коментар (Makers)</h4>"
    if marker in html_body:
        html_body = html_body.replace(marker, screenshots_html() + marker, 1)
    else:
        html_body += screenshots_html()  # fallback: у кінець

    doc = (
        f"<html><head><meta charset='utf-8'><style>{CSS}</style></head>"
        f"<body>{header_html()}{html_body}</body></html>"
    )

    with open(PDF, "wb") as f:
        result = pisa.CreatePDF(doc, dest=f, encoding="utf-8")

    if result.err:
        raise SystemExit(f"PDF generation failed with {result.err} error(s)")
    size_kb = PDF.stat().st_size / 1024
    print(f"OK: {PDF.name} | {size_kb:.0f} KB | logo + {len(SCREENSHOTS)} screenshots")


if __name__ == "__main__":
    main()
