"""
buk_brand.py — Tokens y utilidades de marca Buk (Buk Brand Guide 2026).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

# ──────────────────────────────────────────────────────────────────────────────
# 1. PALETA OFICIAL (HEX de la guía)
# ──────────────────────────────────────────────────────────────────────────────
BUK_BLUE   = "#0059FF"   # PMS 285C          · fondos, elementos gráficos, logo
DARK_BLUE  = "#04047F"   # PMS Reflex Blue C · fondos y elementos gráficos
LIGHT_BLUE = "#71D6FF"   # PMS 2985C         · fondos y elementos gráficos
OFF_WHITE  = "#FDF2E7"   # PMS 7527C         · fondos, gráficos, textos y logo
BLACK      = "#000000"   # textos y logo
PURPLE     = "#BB51B7"   # PMS 218C          · solo gráficos / soporte digital
ORANGE     = "#F78C68"   # PMS 163C          · solo gráficos / soporte digital
BEIGE      = "#F3B7A3"   # PMS 6022C         · solo gráficos / soporte digital
WHITE      = "#FFFFFF"   # fondo base

CHART_COLORS = [BUK_BLUE, LIGHT_BLUE, DARK_BLUE, PURPLE, ORANGE, BEIGE]
GRADIENT_BLUR_PX = 200

# ──────────────────────────────────────────────────────────────────────────────
# 2. TIPOGRAFÍA
# ──────────────────────────────────────────────────────────────────────────────
FONT_FAMILY = "Urbanist"
FONT_FALLBACK = "system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif"
FONT_WEIGHT_DISPLAY = 600        # Urbanist SemiBold → títulos
FONT_WEIGHT_TEXT = 400           # Urbanist Regular  → texto de apoyo
LEADING_TITLE = 0.95             # títulos / formatos grandes
LEADING_TEXT = 1.20              # textos largos
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Urbanist:wght@400;600&display=swap"
)

# ──────────────────────────────────────────────────────────────────────────────
# 3. FORMA Y ESPACIADO
# ──────────────────────────────────────────────────────────────────────────────
RADIUS_CARD = 24     # px · esquinas suaves
RADIUS_CONTROL = 16  # px · botones / inputs
BORDER_WIDTH = 1     # px · tarjeta con contorno azul sobre fondo claro
GLASS = {
    "light_angle": -45, "light_intensity": 0.80, "refraction": 80,
    "depth": 60, "dispersion": 100, "frost": 35, "splay": 0,
}


# ──────────────────────────────────────────────────────────────────────────────
# 4. UTILIDADES DE COLOR
# ──────────────────────────────────────────────────────────────────────────────
def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def mix(fg: str, bg: str, alpha: float) -> str:
    """Mezcla `fg` sobre `bg` con opacidad `alpha` y devuelve HEX sólido."""
    f, b = _rgb(fg), _rgb(bg)
    return "#%02X%02X%02X" % tuple(round(f[i] * alpha + b[i] * (1 - alpha)) for i in range(3))


def contrast_ratio(c1: str, c2: str) -> float:
    """Ratio de contraste WCAG entre dos colores HEX."""
    def lum(h: str) -> float:
        out = []
        for v in _rgb(h):
            v /= 255
            out.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
        return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]
    a, b = sorted((lum(c1), lum(c2)), reverse=True)
    return (a + 0.05) / (b + 0.05)


# ──────────────────────────────────────────────────────────────────────────────
# 5. TEMAS (CLARO / OSCURO)
# ──────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Theme:
    name: str
    background: str
    surface: str
    text: str
    text_muted: str
    primary: str
    on_primary: str
    border: str
    accent: str
    logo: str


LIGHT = Theme(
    name="light",
    background=WHITE,
    surface=OFF_WHITE,
    text=BLACK,
    text_muted=mix(BLACK, WHITE, 0.65),
    primary=BUK_BLUE,
    on_primary=OFF_WHITE,
    border=BUK_BLUE,
    accent=DARK_BLUE,
    logo="blue",
)

DARK = Theme(
    name="dark",
    background=DARK_BLUE,
    surface=mix(OFF_WHITE, DARK_BLUE, 0.08),
    text=OFF_WHITE,
    text_muted=mix(OFF_WHITE, DARK_BLUE, 0.70),
    primary=LIGHT_BLUE,
    on_primary=BLACK,
    border=LIGHT_BLUE,
    accent=LIGHT_BLUE,
    logo="white",
)

THEMES = {"light": LIGHT, "dark": DARK}


def get_theme(mode: str = "light") -> Theme:
    """Devuelve el tema. Acepta 'light'/'dark' (y alias 'claro'/'oscuro')."""
    alias = {"claro": "light", "oscuro": "dark", "white": "light", "blanco": "light"}
    key = alias.get(str(mode).lower(), str(mode).lower())
    if key not in THEMES:
        raise ValueError(f"Modo desconocido: {mode!r}. Usa 'light' o 'dark'.")
    return THEMES[key]


def logo_variant(mode: str = "light", monochrome: bool = False) -> str:
    """Versión de logo según la guía: azul en blanco, blanco en azul, negro en B/N."""
    if monochrome:
        return "white" if get_theme(mode).name == "dark" else "black"
    return get_theme(mode).logo


def logo_clear_space(logo_height_px: float) -> float:
    """Zona de protección: mitad del alto del logo en todos los lados."""
    return logo_height_px / 2


# ──────────────────────────────────────────────────────────────────────────────
# 6. ADAPTADOR CSS
# ──────────────────────────────────────────────────────────────────────────────
def _vars(t: Theme) -> str:
    return (
        f"  --buk-bg: {t.background};\n  --buk-surface: {t.surface};\n"
        f"  --buk-text: {t.text};\n  --buk-text-muted: {t.text_muted};\n"
        f"  --buk-primary: {t.primary};\n  --buk-on-primary: {t.on_primary};\n"
        f"  --buk-border: {t.border};\n  --buk-accent: {t.accent};\n"
    )


def gradient_css() -> str:
    """Gradiente de marca para fondos de Buk AI / Buk Studio."""
    return (
        f"background-color: {BUK_BLUE};\n"
        f"background-image:\n"
        f"  radial-gradient(60% 70% at 15% 70%, {LIGHT_BLUE} 0%, transparent 70%),\n"
        f"  radial-gradient(50% 60% at 55% 85%, {PURPLE} 0%, transparent 70%),\n"
        f"  radial-gradient(45% 55% at 95% 95%, {ORANGE} 0%, transparent 70%),\n"
        f"  radial-gradient(40% 50% at 0% 0%, {DARK_BLUE} 0%, transparent 70%);"
    )


def css(default_mode: str = "light", include_font_import: bool = True) -> str:
    """Genera las reglas CSS completas de la marca Buk."""
    d = get_theme(default_mode)
    o = get_theme("dark" if default_mode == "light" else "light")
    imp = f'@import url("{GOOGLE_FONTS_URL}");\n' if include_font_import else ""
    media = (
        f"@media (prefers-color-scheme: {o.name}) {{\n"
        f"  :root:not([data-theme]) {{\n{_vars(o)}  }}\n}}\n"
        if default_mode == "light" else ""
    )
    return f"""{imp}:root {{
{_vars(d)}  --buk-radius-card: {RADIUS_CARD}px;
  --buk-radius-control: {RADIUS_CONTROL}px;
  --buk-font: '{FONT_FAMILY}', {FONT_FALLBACK};
}}
{media}[data-theme="light"] {{
{_vars(LIGHT)}}}
[data-theme="dark"] {{
{_vars(DARK)}}}

html, body {{
  background: var(--buk-bg); color: var(--buk-text);
  font-family: var(--buk-font); font-weight: {FONT_WEIGHT_TEXT}; line-height: {LEADING_TEXT};
}}
h1, h2, h3, h4 {{
  font-family: var(--buk-font); font-weight: {FONT_WEIGHT_DISPLAY};
  line-height: {LEADING_TITLE}; color: var(--buk-text); text-wrap: balance;
}}
p {{ text-wrap: pretty; }}
a {{ color: var(--buk-primary); }}
.buk-card {{
  background: var(--buk-surface); color: var(--buk-text);
  border: {BORDER_WIDTH}px solid var(--buk-border); border-radius: var(--buk-radius-card);
  padding: 1.5rem;
}}
.buk-btn {{
  background: var(--buk-primary); color: var(--buk-on-primary); border: 0;
  border-radius: var(--buk-radius-control); padding: .7rem 1.4rem;
  font: {FONT_WEIGHT_DISPLAY} 1rem var(--buk-font); cursor: pointer;
}}
.buk-gradient {{ {gradient_css()} }}
"""


# ──────────────────────────────────────────────────────────────────────────────
# 7. ADAPTADORES PARA PYTHON (matplotlib, Plotly, Streamlit)
# ──────────────────────────────────────────────────────────────────────────────
def apply_matplotlib(mode: str = "light") -> None:
    """Aplica la marca a matplotlib."""
    import matplotlib as mpl
    from cycler import cycler
    t = get_theme(mode)
    mpl.rcParams.update({
        "figure.facecolor": t.background, "axes.facecolor": t.background,
        "savefig.facecolor": t.background,
        "text.color": t.text, "axes.labelcolor": t.text,
        "axes.edgecolor": t.text_muted, "xtick.color": t.text, "ytick.color": t.text,
        "grid.color": mix(t.text, t.background, 0.12),
        "axes.prop_cycle": cycler(color=CHART_COLORS),
        "font.family": [FONT_FAMILY, "DejaVu Sans"],
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titleweight": "semibold", "axes.titlelocation": "left",
    })


def plotly_template(mode: str = "light") -> dict:
    """Template de Plotly con los colores de Buk."""
    t = get_theme(mode)
    grid = mix(t.text, t.background, 0.12)
    return {"layout": {
        "paper_bgcolor": t.background, "plot_bgcolor": t.background,
        "font": {"family": f"{FONT_FAMILY}, {FONT_FALLBACK}", "color": t.text},
        "colorway": CHART_COLORS,
        "xaxis": {"gridcolor": grid, "linecolor": t.text_muted},
        "yaxis": {"gridcolor": grid, "linecolor": t.text_muted},
    }}


def streamlit_inject(mode: str = "light") -> None:
    """Inyecta la marca en Streamlit. Llamar una vez al inicio de la app."""
    import streamlit as st
    t = get_theme(mode)
    st.markdown(
        f"<style>{css(mode)}\n"
        f".stApp {{ background: {t.background}; color: {t.text}; }}\n"
        f".stButton>button {{ background: {t.primary}; color: {t.on_primary};"
        f" border-radius: {RADIUS_CONTROL}px; border: 0; font-weight: {FONT_WEIGHT_DISPLAY}; }}</style>",
        unsafe_allow_html=True,
    )


def to_dict(mode: str = "light") -> dict:
    """Tema como diccionario."""
    return asdict(get_theme(mode))


# ──────────────────────────────────────────────────────────────────────────────
# 8. AUDITORÍA  →  python buk_brand.py
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Autoría: Daniela Puig\n")
    for m in ("light", "dark"):
        t = get_theme(m)
        print(f"[{m}] bg={t.background} surface={t.surface} text={t.text} primary={t.primary}")
        for label, fg, bg in [
            ("texto / fondo", t.text, t.background),
            ("texto / tarjeta", t.text, t.surface),
            ("texto suave / fondo", t.text_muted, t.background),
            ("botón", t.on_primary, t.primary),
            ("enlace / fondo", t.primary, t.background),
        ]:
            r = contrast_ratio(fg, bg)
            print(f"   {label:<20} {r:5.1f}:1  {'OK' if r >= 4.5 else 'REVISAR'}")