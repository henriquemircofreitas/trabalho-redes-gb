"""Gera a apresentação de 10 minutos a partir dos resultados versionados.

Uso: uv run python scripts/make_slides.py
"""

from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "apresentacao_redes_gb.pptx"

W, H = 13.333, 7.5
NAVY = "0B172A"
NAVY_2 = "13233D"
WHITE = "F7FAFC"
MUTED = "A9B8CC"
TEAL = "2DD4BF"
CYAN = "38BDF8"
ORANGE = "FB923C"
RED = "F87171"
GREEN = "4ADE80"
BLUE = "60A5FA"
DARK_TEXT = "172033"
LIGHT_PANEL = "EEF4F8"


def rgb(value: str) -> RGBColor:
    return RGBColor.from_string(value)


def set_fill(shape, color: str, transparency: int = 0) -> None:
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(color)
    shape.fill.transparency = transparency


def no_line(shape) -> None:
    shape.line.fill.background()


def text(
    slide,
    value: str,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    size: float = 20,
    color: str = WHITE,
    bold: bool = False,
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.MIDDLE,
    font: str = "Aptos",
    margin: float = 0.04,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.margin_left = frame.margin_right = Inches(margin)
    frame.margin_top = frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = value
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = rgb(color)
    return box


def panel(slide, x, y, w, h, color=NAVY_2, radius=True, line=None):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    set_fill(shape, color)
    if line:
        shape.line.color.rgb = rgb(line)
        shape.line.width = Pt(1.2)
    else:
        no_line(shape)
    return shape


def base(slide, number: int, speaker: str, duration: str, light: bool = False) -> None:
    background = WHITE if light else NAVY
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(background)
    footer_color = "5D6B7E" if light else MUTED
    text(slide, f"{number:02d}", 0.42, 7.08, 0.45, 0.22, size=9, color=footer_color)
    text(
        slide,
        "Redes de Computadores · GB",
        0.92,
        7.08,
        2.7,
        0.22,
        size=9,
        color=footer_color,
    )
    pill = panel(slide, 10.78, 7.0, 2.1, 0.31, color="DDE7EF" if light else NAVY_2)
    text(
        slide,
        f"{speaker}  ·  {duration}",
        10.83,
        7.04,
        2.0,
        0.18,
        size=8.5,
        color=DARK_TEXT if light else WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )


def title(slide, heading: str, kicker: str | None = None, light: bool = False) -> None:
    main_color = DARK_TEXT if light else WHITE
    sub_color = "567086" if light else TEAL
    if kicker:
        text(slide, kicker.upper(), 0.65, 0.33, 5.8, 0.3, size=10, color=sub_color, bold=True)
    text(slide, heading, 0.65, 0.68, 12.0, 0.62, size=28, color=main_color, bold=True, font="Aptos Display")


def notes(slide, value: str) -> None:
    slide.notes_slide.notes_text_frame.text = value.strip()


def add_picture_contain(slide, path: Path, x: float, y: float, w: float, h: float) -> None:
    with Image.open(path) as image:
        iw, ih = image.size
    ratio = min(w / iw, h / ih)
    pw, ph = iw * ratio, ih * ratio
    slide.shapes.add_picture(str(path), Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph))


def add_bullets(slide, items: list[str], x, y, w, h, *, size=18, color=WHITE, accent=TEAL):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.05)
    for index, item in enumerate(items):
        p = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        p.text = item
        p.font.name = "Aptos"
        p.font.size = Pt(size)
        p.font.color.rgb = rgb(color)
        p.space_after = Pt(11)
        p.level = 0
        p.bullet = True
    # Accent marker keeps the list visually tied to the theme.
    marker = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x - 0.14), Inches(y + 0.04), Inches(0.05), Inches(min(h - 0.08, 0.55)))
    set_fill(marker, accent)
    no_line(marker)
    return box


def add_stat(slide, value, label, x, y, w, accent=TEAL, light=False):
    box_color = "E8F1F7" if light else NAVY_2
    panel(slide, x, y, w, 1.28, color=box_color)
    text(slide, value, x + 0.12, y + 0.13, w - 0.24, 0.55, size=27, color=accent, bold=True, align=PP_ALIGN.CENTER)
    text(
        slide,
        label,
        x + 0.12,
        y + 0.72,
        w - 0.24,
        0.35,
        size=11.5,
        color="4F6477" if light else MUTED,
        align=PP_ALIGN.CENTER,
    )


def add_waveform(slide, chips: list[int], x: float, y: float, w: float, h: float, color: str) -> None:
    dx = w / len(chips)
    high, low = y, y + h
    previous_y = high if chips[0] else low
    for index, chip in enumerate(chips):
        current_y = high if chip else low
        x0, x1 = x + index * dx, x + (index + 1) * dx
        if index and current_y != previous_y:
            line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x0), Inches(previous_y), Inches(x0), Inches(current_y))
            line.line.color.rgb = rgb(color)
            line.line.width = Pt(2.2)
        line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x0), Inches(current_y), Inches(x1), Inches(current_y))
        line.line.color.rgb = rgb(color)
        line.line.width = Pt(2.2)
        previous_y = current_y
    axis = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x), Inches(y + h + 0.11), Inches(x + w), Inches(y + h + 0.11))
    axis.line.color.rgb = rgb("52667E")
    axis.line.width = Pt(0.7)


def slide_1(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = rgb(NAVY)
    text(slide, "TRANSMISSÃO DIGITAL NA PRÁTICA", 0.7, 0.55, 6.8, 0.34, size=11, color=TEAL, bold=True)
    text(slide, "Do texto ASCII\nà mensagem recuperada", 0.7, 1.18, 7.2, 1.65, size=36, color=WHITE, bold=True, font="Aptos Display")
    text(slide, "BER, eficiência espectral e ruído em rajadas", 0.72, 3.03, 6.1, 0.48, size=20, color=MUTED)
    panel(slide, 0.72, 4.12, 5.8, 1.15, color=NAVY_2)
    text(slide, "Bernardo Dauber  ·  Henrique Freitas", 0.98, 4.35, 5.3, 0.35, size=17, color=WHITE, bold=True)
    text(slide, "Redes de Computadores · GB · 19/11/2026", 0.98, 4.76, 5.3, 0.26, size=11, color=MUTED)
    # Decorative constellation on the right.
    panel(slide, 8.0, 0.65, 4.55, 5.75, color=NAVY_2)
    for i in range(4):
        for q in range(4):
            dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(8.62 + i * 0.93), Inches(1.28 + q * 1.18), Inches(0.16), Inches(0.16))
            set_fill(dot, TEAL if (i + q) % 2 == 0 else CYAN)
            no_line(dot)
    text(slide, "16-QAM", 8.5, 6.0, 3.55, 0.28, size=11, color=MUTED, align=PP_ALIGN.CENTER)
    text(slide, "10 min", 11.75, 6.92, 0.78, 0.25, size=10, color=TEAL, bold=True, align=PP_ALIGN.RIGHT)
    notes(slide, """
    Bernardo: Boa noite. Nós somos Bernardo e Henrique. Nosso trabalho acompanha uma mensagem ASCII
    por toda a cadeia de transmissão digital e mede como a codificação de linha, a modulação e o
    canal alteram a taxa de erro e a eficiência espectral. A ideia foi construir um experimento
    reproduzível, não apenas uma demonstração isolada.
    """)


def slide_2(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6]); base(slide, 2, "Bernardo", "45 s"); title(slide, "Do texto ao bit recuperado", "Arquitetura")
    stages = [
        ("ASCII", "12.533 caracteres"), ("BITS", "100.264"), ("LINHA", "3 códigos"),
        ("SÍMBOLOS", "3 modulações"), ("CANAL", "2 cenários"), ("RECEPTOR", "decisão dura"),
        ("MÉTRICAS", "BER + η"),
    ]
    colors = [TEAL, CYAN, BLUE, ORANGE, RED, BLUE, GREEN]
    x0, gap, width = 0.55, 0.16, 1.63
    for i, ((name, sub), color) in enumerate(zip(stages, colors, strict=True)):
        x = x0 + i * (width + gap)
        panel(slide, x, 2.15, width, 1.48, color=NAVY_2, line=color)
        text(slide, name, x + 0.08, 2.37, width - 0.16, 0.32, size=13, color=color, bold=True, align=PP_ALIGN.CENTER)
        text(slide, sub, x + 0.08, 2.84, width - 0.16, 0.37, size=11, color=WHITE, align=PP_ALIGN.CENTER)
        if i < len(stages) - 1:
            text(slide, "→", x + width + 0.01, 2.62, gap, 0.38, size=16, color=MUTED, bold=True, align=PP_ALIGN.CENTER)
    panel(slide, 1.02, 4.28, 11.25, 1.32, color="102B3B", line=TEAL)
    text(slide, "A BER é medida depois da decodificação de linha", 1.28, 4.5, 10.73, 0.4, size=22, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    text(slide, "Comparação sempre nos bits originais da mensagem", 1.28, 5.0, 10.73, 0.28, size=13, color=MUTED, align=PP_ALIGN.CENTER)
    notes(slide, """
    Bernardo: A cadeia começa no texto e termina na comparação bit a bit. Primeiro convertemos o
    texto em bits, aplicamos o código de linha e agrupamos chips em símbolos. O canal adiciona ruído;
    depois fazemos decisão de símbolo, decodificação de linha e reconstrução do texto. Um detalhe
    importante é que a BER é calculada nos bits originais, depois de todo o receptor.
    """)


def slide_3(prs):
    from sim import line_codes
    import numpy as np
    slide = prs.slides.add_slide(prs.slide_layouts[6]); base(slide, 3, "Bernardo", "55 s"); title(slide, "Código de linha não corrige erros", "Conceito-chave")
    bits = np.array([0, 1, 0, 1], dtype=np.uint8)
    rows = [("NRZ", "1 chip/bit", "nrz", CYAN), ("Manchester", "2 chips/bit · 0→01, 1→10", "manchester", TEAL), ("Manchester diferencial", "2 chips/bit · transição central", "diff_manchester", ORANGE)]
    for idx, (label, sub, code, color) in enumerate(rows):
        y = 1.72 + idx * 1.27
        panel(slide, 0.65, y, 8.1, 1.02, color=NAVY_2)
        text(slide, label, 0.86, y + 0.12, 2.05, 0.3, size=15, color=color, bold=True)
        text(slide, sub, 0.86, y + 0.52, 2.25, 0.23, size=10, color=MUTED)
        chips = line_codes.encode(bits, code).tolist()
        add_waveform(slide, chips, 3.25, y + 0.22, 5.0, 0.46, color)
    panel(slide, 9.1, 1.72, 3.55, 3.57, color="172B3F", line=RED)
    text(slide, "DETECÇÃO ≠ CORREÇÃO", 9.35, 2.02, 3.05, 0.35, size=14, color=RED, bold=True, align=PP_ALIGN.CENTER)
    text(slide, "00 ou 11", 9.35, 2.6, 3.05, 0.52, size=28, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    text(slide, "são violações em Manchester", 9.45, 3.2, 2.85, 0.5, size=13, color=MUTED, align=PP_ALIGN.CENTER)
    text(slide, "Detectamos que algo deu errado,\nmas não há redundância suficiente\npara corrigir com certeza.", 9.42, 4.02, 2.91, 0.82, size=12, color=WHITE, align=PP_ALIGN.CENTER)
    text(slide, "Bits:   0      1      0      1", 3.26, 5.63, 5.0, 0.26, size=11, color=MUTED, align=PP_ALIGN.CENTER)
    notes(slide, """
    Bernardo: Código de linha define a forma de representar os bits no sinal. Ele ajuda em
    sincronismo e transições, mas não é um código de correção de erros. No Manchester, cada bit vira
    dois chips e sempre existe uma transição no meio. Se recebermos 00 ou 11, sabemos que houve uma
    violação, mas não sabemos qual era o bit original. Por isso contamos violações separadamente.
    """)


def constellation_card(slide, x, title_text, points, eta, color):
    panel(slide, x, 1.78, 3.82, 3.8, color=NAVY_2)
    text(slide, title_text, x + 0.2, 2.02, 3.42, 0.35, size=18, color=color, bold=True, align=PP_ALIGN.CENTER)
    cx, cy = x + 1.91, 3.42
    # axes
    for coords in [(x + 0.62, cy, x + 3.2, cy), (cx, 2.55, cx, 4.4)]:
        line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, *(Inches(v) for v in coords))
        line.line.color.rgb = rgb("60738A"); line.line.width = Pt(0.8)
    for px, py in points:
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx + px - 0.06), Inches(cy - py - 0.06), Inches(0.12), Inches(0.12))
        set_fill(dot, color); no_line(dot)
    text(slide, eta, x + 0.35, 4.78, 3.12, 0.34, size=15, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    text(slide, "Mapeamento Gray", x + 0.35, 5.17, 3.12, 0.24, size=10, color=MUTED, align=PP_ALIGN.CENTER)


def slide_4(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6]); base(slide, 4, "Bernardo", "55 s"); title(slide, "Três modulações, três compromissos", "Modulação")
    constellation_card(slide, 0.55, "BPSK", [(-0.72, 0), (0.72, 0)], "1 bit/símbolo", BLUE)
    constellation_card(slide, 4.76, "QPSK", [(-0.62, -0.62), (-0.62, 0.62), (0.62, -0.62), (0.62, 0.62)], "2 bits/símbolo", TEAL)
    pts = [(i * 0.42, q * 0.42) for i in (-1.5, -0.5, 0.5, 1.5) for q in (-1.5, -0.5, 0.5, 1.5)]
    constellation_card(slide, 8.97, "16-QAM", pts, "4 bits/símbolo", ORANGE)
    text(slide, "Mais pontos por símbolo → mais eficiência, mas menor distância entre decisões", 1.4, 6.08, 10.55, 0.42, size=18, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    notes(slide, """
    Bernardo: Nas três modulações usamos constelações normalizadas e rótulos Gray, para que pontos
    vizinhos diferenciem em apenas um bit. BPSK carrega um bit por símbolo, QPSK carrega dois e
    16-QAM carrega quatro. A eficiência cresce, mas os pontos ficam mais próximos e o receptor
    precisa de mais Eb/N0 para manter a mesma BER.
    """)


def slide_5(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6]); base(slide, 5, "Henrique", "50 s"); title(slide, "Dois canais, a mesma referência de energia", "Canal")
    panel(slide, 0.72, 1.6, 5.75, 3.35, color=NAVY_2, line=CYAN)
    text(slide, "AWGN", 1.05, 1.9, 5.1, 0.42, size=25, color=CYAN, bold=True, align=PP_ALIGN.CENTER)
    text(slide, "Ruído gaussiano independente\nem todos os símbolos", 1.15, 2.55, 4.9, 0.82, size=20, color=WHITE, align=PP_ALIGN.CENTER)
    text(slide, "N₀ diminui quando Eb/N₀ aumenta", 1.15, 3.72, 4.9, 0.35, size=13, color=MUTED, align=PP_ALIGN.CENTER)
    panel(slide, 6.86, 1.6, 5.75, 3.35, color=NAVY_2, line=RED)
    text(slide, "AWGN + RAJADAS", 7.2, 1.9, 5.08, 0.42, size=25, color=RED, bold=True, align=PP_ALIGN.CENTER)
    text(slide, "Estado ruim em 1% dos símbolos\nrajada média de 20 símbolos", 7.25, 2.52, 4.98, 0.82, size=20, color=WHITE, align=PP_ALIGN.CENTER)
    text(slide, "Ruído adicional fixo: 0 dB", 7.25, 3.72, 4.98, 0.35, size=13, color=MUTED, align=PP_ALIGN.CENTER)
    panel(slide, 2.0, 5.38, 9.3, 0.9, color="102B3B", line=TEAL)
    text(slide, "Eb/N₀ sempre por bit da mensagem · energia medida no fluxo real", 2.22, 5.6, 8.86, 0.35, size=17, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    notes(slide, """
    Henrique: O primeiro cenário é AWGN puro. O segundo mantém o AWGN e acrescenta um processo de
    dois estados. Em média, 1% dos símbolos ficam no estado ruim, com rajadas de 20 símbolos. O
    ruído da rajada tem nível absoluto, então não desaparece quando aumentamos a SNR do fundo. Em
    todas as comparações usamos Eb/N0 por bit da mensagem e medimos a energia realmente transmitida.
    """)


def slide_6(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6]); base(slide, 6, "Henrique", "40 s", light=True); title(slide, "Experimento controlado e reproduzível", "Metodologia", light=True)
    add_stat(slide, "100.264", "bits por transmissão", 0.72, 1.72, 2.78, TEAL, True)
    add_stat(slide, "11", "valores de Eb/N0", 3.76, 1.72, 2.78, CYAN, True)
    add_stat(slide, "5", "sementes por ponto", 6.8, 1.72, 2.78, ORANGE, True)
    add_stat(slide, "990", "execuções completas", 9.84, 1.72, 2.78, RED, True)
    panel(slide, 0.72, 3.48, 11.9, 2.2, color=LIGHT_PANEL, line="C8D5DF")
    items = [
        "Eb/N0 = 0, 2, 4, …, 20 dB para todas as combinações",
        "3 códigos × 3 modulações × 2 canais × 11 pontos × 5 sementes",
        "CSV bruto, configuração, hash da implementação e scripts versionados",
        "Média + IC de 95%; regra de três quando nenhum erro é observado",
    ]
    add_bullets(slide, items, 1.15, 3.83, 10.95, 1.55, size=15, color=DARK_TEXT, accent=TEAL)
    text(slide, "99.261.360 bits de mensagem transmitidos no total", 2.55, 6.05, 8.2, 0.36, size=17, color=DARK_TEXT, bold=True, align=PP_ALIGN.CENTER)
    notes(slide, """
    Henrique: Para cada combinação usamos a mesma grade de onze valores, de zero a vinte dB, e
    cinco sementes. Cada execução transmite 100.264 bits, acima do mínimo do enunciado. Isso gera
    990 execuções e mais de 99 milhões de bits. Salvamos cada repetição no CSV e mostramos média e
    intervalo de confiança de 95%.
    """)


def slide_7(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6]); base(slide, 7, "Henrique", "65 s", light=True); title(slide, "Em AWGN, o resultado acompanha a teoria", "Resultado 1", light=True)
    panel(slide, 0.55, 1.35, 8.82, 5.45, color="FFFFFF", line="D7E1E8")
    add_picture_contain(slide, ROOT / "results/plots/ber_nrz.png", 0.7, 1.5, 8.52, 5.12)
    panel(slide, 9.65, 1.58, 3.05, 1.25, color="E6F8F5")
    text(slide, "6,69 dB", 9.84, 1.76, 2.67, 0.43, size=25, color="087F70", bold=True, align=PP_ALIGN.CENTER)
    text(slide, "NRZ-BPSK para BER 10⁻³", 9.84, 2.23, 2.67, 0.25, size=10.5, color=DARK_TEXT, align=PP_ALIGN.CENTER)
    panel(slide, 9.65, 3.05, 3.05, 1.25, color="FFF0E5")
    text(slide, "10,43 dB", 9.84, 3.23, 2.67, 0.43, size=25, color="B64E0A", bold=True, align=PP_ALIGN.CENTER)
    text(slide, "NRZ-16-QAM para BER 10⁻³", 9.84, 3.7, 2.67, 0.25, size=10.5, color=DARK_TEXT, align=PP_ALIGN.CENTER)
    text(slide, "BPSK e QPSK quase coincidem\nquando comparadas por Eb/N0", 9.74, 4.74, 2.87, 0.78, size=16, color=DARK_TEXT, bold=True, align=PP_ALIGN.CENTER)
    text(slide, "As linhas tracejadas são as curvas teóricas.", 9.8, 5.82, 2.72, 0.45, size=11, color="5D6B7E", align=PP_ALIGN.CENTER)
    notes(slide, """
    Henrique: No painel esquerdo vemos o AWGN. BPSK e QPSK ficam praticamente sobrepostas e
    acompanham a curva teórica, o que valida o simulador. Para chegar a BER de 10⁻³, BPSK precisou
    de cerca de 6,69 dB. A 16-QAM entrega quatro bits por símbolo, mas precisou de 10,43 dB. Os
    marcadores têm intervalos de 95%; triângulos vazios representam limite superior sem erros.
    """)


def slide_8(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6]); base(slide, 8, "Henrique", "65 s", light=True); title(slide, "Rajadas criam um piso de BER", "Resultado 2", light=True)
    panel(slide, 0.55, 1.42, 9.05, 5.28, color="FFFFFF", line="D7E1E8")
    add_picture_contain(slide, ROOT / "results/plots/comparacao_canais_nrz.png", 0.7, 1.58, 8.75, 4.96)
    text(slide, "A 20 dB", 10.05, 1.63, 2.4, 0.34, size=14, color="5D6B7E", bold=True, align=PP_ALIGN.CENTER)
    for i, (name, value, color) in enumerate([("BPSK", "7,72×10⁻⁴", BLUE), ("QPSK", "9,24×10⁻⁴", TEAL), ("16-QAM", "1,37×10⁻³", ORANGE)]):
        y = 2.1 + i * 1.08
        panel(slide, 9.9, y, 2.7, 0.86, color="EDF3F7")
        text(slide, name, 10.06, y + 0.08, 0.82, 0.25, size=11, color=color, bold=True)
        text(slide, value, 10.82, y + 0.08, 1.58, 0.28, size=16, color=DARK_TEXT, bold=True, align=PP_ALIGN.RIGHT)
        text(slide, "BER média em rajadas", 10.06, y + 0.46, 2.34, 0.19, size=8.5, color="69798A")
    panel(slide, 9.9, 5.55, 2.7, 0.9, color="FDECEC", line="F3B4B4")
    text(slide, "Mais potência reduz o fundo,\nmas não elimina a rajada.", 10.05, 5.73, 2.4, 0.48, size=12.5, color="8E2525", bold=True, align=PP_ALIGN.CENTER)
    notes(slide, """
    Henrique: Aqui comparamos diretamente os dois canais. As linhas contínuas de AWGN continuam
    caindo. As tracejadas de rajadas param em um piso porque o ruído extra não depende da SNR de
    fundo. A vinte dB, a BER ainda fica entre aproximadamente 7,7 vezes 10⁻⁴ e 1,37 vezes 10⁻³ no
    NRZ. Portanto, simplesmente aumentar potência não resolve esse tipo de degradação.
    """)


def slide_9(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6]); base(slide, 9, "Ambos", "60 s", light=True); title(slide, "Eficiência espectral não vem de graça", "Compromisso", light=True)
    rows = [
        ("NRZ", "BPSK", "1,0", "6,69 dB", "Robustez"),
        ("NRZ", "QPSK", "2,0", "6,73 dB", "Melhor equilíbrio"),
        ("NRZ", "16-QAM", "4,0", "10,43 dB", "Largura de banda"),
        ("Manchester", "BPSK", "0,5", "9,69 dB", "Sincronismo"),
        ("Manchester dif.", "16-QAM", "2,0", "14,09 dB", "Caso mais exigente"),
    ]
    x, y, widths = 0.72, 1.65, [2.25, 1.85, 1.55, 2.45, 3.6]
    headers = ["Código", "Modulação", "η bit/s/Hz", "Eb/N0 p/ BER 10⁻³", "Quando faz sentido"]
    cursor = x
    for head, width in zip(headers, widths, strict=True):
        panel(slide, cursor, y, width, 0.58, color=NAVY_2, radius=False)
        text(slide, head, cursor + 0.06, y + 0.09, width - 0.12, 0.28, size=10.5, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
        cursor += width
    for row_idx, row in enumerate(rows):
        cursor = x; ry = y + 0.58 + row_idx * 0.72
        bg = "FFFFFF" if row_idx % 2 == 0 else "EDF3F7"
        for col_idx, (cell, width) in enumerate(zip(row, widths, strict=True)):
            panel(slide, cursor, ry, width, 0.72, color=bg, radius=False)
            cell_color = "087F70" if row_idx == 1 else DARK_TEXT
            text(slide, cell, cursor + 0.07, ry + 0.12, width - 0.14, 0.34, size=11.5 if col_idx != 4 else 10.5, color=cell_color, bold=row_idx == 1, align=PP_ALIGN.CENTER)
            cursor += width
    panel(slide, 1.15, 6.05, 11.0, 0.55, color="E6F8F5", line="A6DED5")
    text(slide, "QPSK/NRZ dobra a eficiência da BPSK praticamente sem penalidade em AWGN ideal", 1.35, 6.16, 10.6, 0.28, size=15, color="087F70", bold=True, align=PP_ALIGN.CENTER)
    notes(slide, """
    Bernardo: A eficiência nominal mostra quantos bits da mensagem cabem por segundo por hertz.
    Henrique: Em AWGN ideal, QPSK com NRZ é o melhor equilíbrio: dobra a eficiência da BPSK e exige
    praticamente o mesmo Eb/N0. A 16-QAM chega a quatro bits por segundo por hertz, mas pede mais
    potência. Manchester reduz a eficiência pela metade e, neste receptor, também custa cerca de
    três dB.
    """)


def slide_10(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6]); base(slide, 10, "Bernardo", "55 s", light=True); title(slide, "Consistência: o enlace funciona sem ruído", "Validação", light=True)
    panel(slide, 0.55, 1.38, 8.65, 5.34, color="FFFFFF", line="D7E1E8")
    add_picture_contain(slide, ROOT / "results/plots/constelacoes_16qam.png", 0.7, 1.55, 8.35, 5.0)
    panel(slide, 9.52, 1.58, 3.1, 1.38, color="E8FAEE", line="B9E6C7")
    text(slide, "9 / 9", 9.74, 1.76, 2.66, 0.5, size=29, color="137A3D", bold=True, align=PP_ALIGN.CENTER)
    text(slide, "combinações exatas no canal ideal", 9.75, 2.35, 2.64, 0.32, size=10.5, color=DARK_TEXT, align=PP_ALIGN.CENTER)
    panel(slide, 9.52, 3.23, 3.1, 1.38, color="EAF4FD", line="BAD7EF")
    text(slide, "0 erros", 9.74, 3.42, 2.66, 0.5, size=27, color="1B66A3", bold=True, align=PP_ALIGN.CENTER)
    text(slide, "AWGN a 20 dB nas cinco sementes", 9.75, 4.0, 2.64, 0.32, size=10.5, color=DARK_TEXT, align=PP_ALIGN.CENTER)
    text(slide, "26 testes automatizados\n+ CI no GitHub", 9.75, 5.28, 2.64, 0.72, size=18, color=DARK_TEXT, bold=True, align=PP_ALIGN.CENTER)
    notes(slide, """
    Bernardo: Antes de interpretar as curvas, validamos o enlace. Sem ruído, todas as nove
    combinações recuperam exatamente a mensagem. Em AWGN a vinte dB, as cinco sementes também
    tiveram zero erros. Os diagramas mostram a 16-QAM: em zero dB as nuvens se misturam, em dez dB
    os grupos aparecem e em vinte dB ficam compactos. Nas rajadas ainda restam amostras afastadas.
    """)


def slide_11(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6]); base(slide, 11, "Ambos", "45 s"); title(slide, "O canal define a melhor escolha", "Conclusões")
    cards = [
        ("01", "AWGN", "BPSK e QPSK seguem a teoria; potência reduz a BER.", CYAN),
        ("02", "Rajadas", "Aparece um piso: mais potência não elimina erros concentrados.", RED),
        ("03", "Compromisso", "QPSK/NRZ equilibra robustez e eficiência; 16-QAM prioriza banda.", TEAL),
    ]
    for i, (num, head, body, color) in enumerate(cards):
        x = 0.72 + i * 4.15
        panel(slide, x, 1.62, 3.75, 2.72, color=NAVY_2, line=color)
        text(slide, num, x + 0.22, 1.83, 0.65, 0.36, size=14, color=color, bold=True)
        text(slide, head, x + 0.22, 2.3, 3.25, 0.44, size=22, color=WHITE, bold=True)
        text(slide, body, x + 0.22, 2.94, 3.28, 0.92, size=15, color=MUTED)
    panel(slide, 1.35, 4.92, 10.65, 1.15, color="102B3B", line=TEAL)
    box = text(slide, "github.com/henriquemircofreitas/trabalho-redes-gb", 1.7, 5.18, 9.95, 0.37, size=17, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    box.text_frame.paragraphs[0].runs[0].hyperlink.address = "https://github.com/henriquemircofreitas/trabalho-redes-gb"
    text(slide, "Código · dados brutos · gráficos · testes · reprodução", 1.7, 5.63, 9.95, 0.25, size=11, color=MUTED, align=PP_ALIGN.CENTER)
    text(slide, "Perguntas?", 4.6, 6.35, 4.1, 0.45, size=25, color=TEAL, bold=True, align=PP_ALIGN.CENTER)
    notes(slide, """
    Henrique: Concluímos que a modulação não pode ser escolhida isoladamente. Em AWGN, aumentar
    potência reduz a BER; em rajadas, surge um piso. Bernardo: QPSK com NRZ foi o melhor equilíbrio
    no nosso modelo, enquanto 16-QAM é interessante quando largura de banda é mais importante e há
    SNR disponível. Todo o código, dados brutos e reprodução estão no GitHub. Obrigado.
    """)


def main() -> None:
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    prs.core_properties.title = "Transmissão digital na prática"
    prs.core_properties.subject = "Redes de Computadores — GB"
    prs.core_properties.author = "Bernardo Dauber e Henrique Freitas"
    prs.core_properties.comments = "Apresentação gerada a partir dos resultados versionados no repositório."
    for builder in (slide_1, slide_2, slide_3, slide_4, slide_5, slide_6, slide_7, slide_8, slide_9, slide_10, slide_11):
        builder(prs)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"Gerado: {OUT} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
