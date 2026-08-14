"""
theme.py
=========
Todo el estilo visual de la app vive aquí: paleta de colores, fuentes y
las hojas de estilo (QSS) de cada tipo de widget.

Inspirado en un fondo degradado violeta/azul con acentos cian, tipografía
blanca bien gruesa y botones redondeados con "glow" — igual que la
referencia de diseño (logo "cpu" + tarjetas tipo noticia).

Si quieres cambiar los colores de toda la app, este es el único archivo
que necesitas tocar.
"""

# ---------------------------------------------------------------------------
# Paleta de colores
# ---------------------------------------------------------------------------
COLOR_BG_TOP = "#3a2a8c"       # morado oscuro (esquina superior)
COLOR_BG_MID = "#5b3fb8"       # violeta medio
COLOR_BG_BOTTOM = "#2f6fe0"    # azul (esquina inferior)

COLOR_ACCENT = "#37e0d8"       # cian brillante (acento / hover)
COLOR_ACCENT_DARK = "#1fb8b0"  # cian oscuro (pressed)

COLOR_CARD_BG = "rgba(255, 255, 255, 28)"      # tarjetas translúcidas
COLOR_CARD_BORDER = "rgba(255, 255, 255, 60)"

COLOR_TEXT_PRIMARY = "#ffffff"
COLOR_TEXT_SECONDARY = "rgba(255, 255, 255, 190)"

COLOR_PRIMARY_BTN_BG = "#ff5d8f"      # rosa/magenta llamativo (call to action)
COLOR_PRIMARY_BTN_HOVER = "#ff7ba3"
COLOR_PRIMARY_BTN_PRESSED = "#e14d7c"

COLOR_SPLIT_BG = "rgba(255, 255, 255, 18)"
COLOR_SPLIT_BG_HOVER = "rgba(255, 255, 255, 40)"
COLOR_SPLIT_ACTIVE = "#37e0d8"

# ---------------------------------------------------------------------------
# Fuente
# ---------------------------------------------------------------------------
FONT_FAMILY = "Segoe UI, Arial, sans-serif"

# ---------------------------------------------------------------------------
# Fondo general de ventana (degradado diagonal estilo la referencia)
# ---------------------------------------------------------------------------
WINDOW_BACKGROUND_QSS = f"""
QMainWindow, QDialog {{
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 {COLOR_BG_TOP},
        stop:0.5 {COLOR_BG_MID},
        stop:1 {COLOR_BG_BOTTOM}
    );
}}
"""

# ---------------------------------------------------------------------------
# Botón principal (Correr Benchmark) — grande, redondeado, con acento
# ---------------------------------------------------------------------------
PRIMARY_BUTTON_QSS = f"""
QPushButton#primaryButton {{
    background-color: {COLOR_PRIMARY_BTN_BG};
    color: {COLOR_TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: 18px;
    font-weight: 800;
    border: none;
    border-radius: 28px;
    padding: 16px 40px;
    min-height: 24px;
}}
QPushButton#primaryButton:hover {{
    background-color: {COLOR_PRIMARY_BTN_HOVER};
}}
QPushButton#primaryButton:pressed {{
    background-color: {COLOR_PRIMARY_BTN_PRESSED};
}}
QPushButton#primaryButton:disabled {{
    background-color: rgba(255, 93, 143, 120);
    color: rgba(255, 255, 255, 150);
}}
"""

# ---------------------------------------------------------------------------
# Botón split superior (CPU Bench | Opciones)
# ---------------------------------------------------------------------------
SPLIT_LEFT_QSS = f"""
QPushButton#splitLeft {{
    background-color: {COLOR_SPLIT_BG};
    color: {COLOR_TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: 13px;
    font-weight: 700;
    border: 1px solid {COLOR_CARD_BORDER};
    border-right: none;
    border-top-left-radius: 18px;
    border-bottom-left-radius: 18px;
    padding: 10px 18px;
}}
QPushButton#splitLeft:hover {{
    background-color: {COLOR_SPLIT_BG_HOVER};
}}
"""

SPLIT_RIGHT_QSS = f"""
QPushButton#splitRight {{
    background-color: {COLOR_SPLIT_BG};
    color: {COLOR_TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: 13px;
    font-weight: 700;
    border: 1px solid {COLOR_CARD_BORDER};
    border-top-right-radius: 18px;
    border-bottom-right-radius: 18px;
    padding: 10px 18px;
}}
QPushButton#splitRight:hover {{
    background-color: {COLOR_SPLIT_BG_HOVER};
}}
"""

# ---------------------------------------------------------------------------
# Etiquetas de texto
# ---------------------------------------------------------------------------
TITLE_LABEL_QSS = f"""
QLabel#titleLabel {{
    color: {COLOR_TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: 34px;
    font-weight: 800;
    letter-spacing: 1px;
}}
"""

SUBTITLE_LABEL_QSS = f"""
QLabel#subtitleLabel {{
    color: {COLOR_TEXT_SECONDARY};
    font-family: {FONT_FAMILY};
    font-size: 15px;
    font-weight: 500;
}}
"""

# Variante de título más pequeña, usada en diálogos secundarios
# (Opciones, ventana de progreso) donde el título grande de 34px
# ocuparía demasiado espacio.
def dialog_title_qss(font_size_px: int = 18) -> str:
    return f"""
    QLabel#dialogTitleLabel {{
        color: {COLOR_TEXT_PRIMARY};
        font-family: {FONT_FAMILY};
        font-size: {font_size_px}px;
        font-weight: 800;
    }}
    """

# ---------------------------------------------------------------------------
# Tarjeta translúcida genérica (glassmorphism), usada en Opciones, etc.
# ---------------------------------------------------------------------------
CARD_QSS = f"""
QFrame#card {{
    background-color: {COLOR_CARD_BG};
    border: 1px solid {COLOR_CARD_BORDER};
    border-radius: 20px;
}}
"""

# ---------------------------------------------------------------------------
# Checkbox estilizado (usado en la ventana de Opciones)
# ---------------------------------------------------------------------------
CHECKBOX_QSS = f"""
QCheckBox {{
    color: {COLOR_TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: 14px;
    font-weight: 600;
    spacing: 10px;
    padding: 6px 0;
}}
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 2px solid {COLOR_CARD_BORDER};
    background-color: rgba(255, 255, 255, 20);
}}
QCheckBox::indicator:hover {{
    border: 2px solid {COLOR_ACCENT};
}}
QCheckBox::indicator:checked {{
    background-color: {COLOR_ACCENT};
    border: 2px solid {COLOR_ACCENT};
}}
"""

# ---------------------------------------------------------------------------
# Botón secundario (usado dentro de diálogos, p.ej. "Correr tests")
# ---------------------------------------------------------------------------
SECONDARY_BUTTON_QSS = f"""
QPushButton#secondaryButton {{
    background-color: {COLOR_ACCENT};
    color: #0b2b2a;
    font-family: {FONT_FAMILY};
    font-size: 14px;
    font-weight: 800;
    border: none;
    border-radius: 18px;
    padding: 10px 24px;
}}
QPushButton#secondaryButton:hover {{
    background-color: #4ff0e8;
}}
QPushButton#secondaryButton:pressed {{
    background-color: {COLOR_ACCENT_DARK};
}}
"""

# ---------------------------------------------------------------------------
# Barra de progreso (ventana "ejecutando benchmark")
# ---------------------------------------------------------------------------
PROGRESS_BAR_QSS = f"""
QProgressBar {{
    background-color: rgba(255, 255, 255, 30);
    border: none;
    border-radius: 8px;
    height: 14px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {COLOR_ACCENT};
    border-radius: 8px;
}}
"""

# ---------------------------------------------------------------------------
# Texto genérico dentro de diálogos
# ---------------------------------------------------------------------------
DIALOG_TEXT_QSS = f"""
QLabel {{
    color: {COLOR_TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
}}
"""

# ---------------------------------------------------------------------------
# Ventana de Resultados
# ---------------------------------------------------------------------------
SCORE_TOTAL_LABEL_QSS = f"""
QLabel#scoreTotalLabel {{
    color: {COLOR_TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: 56px;
    font-weight: 800;
}}
"""

SCORE_TOTAL_CAPTION_QSS = f"""
QLabel#scoreTotalCaption {{
    color: {COLOR_ACCENT};
    font-family: {FONT_FAMILY};
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
}}
"""

RESULT_CARD_QSS = f"""
QFrame#resultCard {{
    background-color: {COLOR_CARD_BG};
    border: 1px solid {COLOR_CARD_BORDER};
    border-radius: 16px;
}}
"""

RESULT_ICON_QSS = """
QLabel#resultIcon {
    font-size: 22px;
}
"""

RESULT_NAME_QSS = f"""
QLabel#resultName {{
    color: {COLOR_TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: 14px;
    font-weight: 700;
}}
"""

RESULT_SUBNAME_QSS = f"""
QLabel#resultSubname {{
    color: {COLOR_TEXT_SECONDARY};
    font-family: {FONT_FAMILY};
    font-size: 12px;
    font-weight: 400;
}}
"""

RESULT_SCORE_QSS = f"""
QLabel#resultScore {{
    color: {COLOR_ACCENT};
    font-family: {FONT_FAMILY};
    font-size: 20px;
    font-weight: 800;
}}
"""

# ---------------------------------------------------------------------------
# Indicador de estado de Phoronix Test Suite (main_window.py)
# ---------------------------------------------------------------------------
PTS_STATUS_OK_QSS = """
QLabel#ptsStatusLabel {
    color: #8bffc7;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 12px;
    font-weight: 600;
}
"""

PTS_STATUS_WARN_QSS = """
QLabel#ptsStatusLabel {
    color: #ffd27a;
    font-family: Segoe UI, Arial, sans-serif;
    font-size: 12px;
    font-weight: 600;
}
"""

# ---------------------------------------------------------------------------
# Ensambla todo el QSS de una ventana a partir de los fragmentos anteriores
# ---------------------------------------------------------------------------
def full_stylesheet(*fragments: str) -> str:
    """Concatena fragmentos QSS. Uso: widget.setStyleSheet(theme.full_stylesheet(...))"""
    return "\n".join(fragments)
