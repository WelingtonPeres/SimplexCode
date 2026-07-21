import io
from datetime import datetime
import math

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether,
)

from reporting.grafico import (
    calcular_vertices,
    extrair_caminho,
    extrair_ponto_do_tableau,
    plotar_grafico,
)


HEADER_BG = "#BDBDBD"
CELL_BG = "#FFFFFF"
BASIC_BG = "#E8E8E8"
PIVOT_COL_BG = "#BBDEFB"
PIVOT_ROW_BG = "#BBDEFB"
PIVOT_ELEM_BG = "#1565C0"
NEGATIVE_BG = "#FFCDD2"
Z_ROW_BG = "#E8F5E9"
Z_PRIME_ROW_BG = "#E3F2FD"

PAGE_W, PAGE_H = A4


def _hex(c):
    return rl_colors.HexColor(c)


def gerar_relatorio(caminho_arquivo, ppl, simplex, dados_originais):
    doc = SimpleDocTemplate(
        caminho_arquivo,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "TituloRelatorio", parent=styles["Title"],
        fontSize=18, alignment=TA_CENTER, spaceAfter=6,
    )
    subtitulo_style = ParagraphStyle(
        "SubtituloRelatorio", parent=styles["Normal"],
        fontSize=10, alignment=TA_CENTER, textColor=rl_colors.HexColor("#757575"),
        spaceAfter=20,
    )
    secao_style = ParagraphStyle(
        "Secao", parent=styles["Heading2"],
        fontSize=14, spaceBefore=16, spaceAfter=8,
    )
    eq_style = ParagraphStyle(
        "Equacao", parent=styles["Normal"],
        fontSize=11, fontName="Courier",
        leftIndent=20, spaceAfter=4,
    )

    story = []
    tabela_comprimento = PAGE_W - 4 * cm

    vertices = None
    caminho = None
    if dados_originais["n_variaveis"] == 2:
        vertices = calcular_vertices(
            dados_originais["matriz_coeficientes"],
            dados_originais["vetor_b"],
            dados_originais["vetor_sinais"],
        )
        caminho = extrair_caminho(simplex.tableaus_list)

    # ── CAPA + MODELAGEM ──
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("Relatório de Resolução", titulo_style))
    story.append(Paragraph("Método Simplex", titulo_style))
    story.append(Spacer(1, 0.5 * cm))
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"Data: {agora}", subtitulo_style))
    tipo_str = "Minimização" if dados_originais["eh_minimizacao"] else "Maximização"
    fases_str = "Duas Fases" if ppl.eh_DuasEtapas else "Uma Fase"
    story.append(Paragraph(f"Tipo: {tipo_str} | Classificação: {fases_str}", subtitulo_style))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Modelagem do Problema", secao_style))

    fo = dados_originais["funcao_objetivo"]
    termos_fo = " + ".join(
        f"{fo[i]}x<sub>{i+1}</sub>" if fo[i] >= 0 else f"({fo[i]})x<sub>{i+1}</sub>"
        for i in range(len(fo))
    )
    prefixo = "Minimizar" if dados_originais["eh_minimizacao"] else "Maximizar"
    story.append(Paragraph(f"{prefixo} Z = {termos_fo}", eq_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Sujeito a:", eq_style))

    A = dados_originais["matriz_coeficientes"]
    b = dados_originais["vetor_b"]
    sinais = dados_originais["vetor_sinais"]
    for i in range(len(A)):
        termos = " + ".join(
            f"{A[i][j]}x<sub>{j+1}</sub>" if A[i][j] >= 0
            else f"({A[i][j]})x<sub>{j+1}</sub>"
            for j in range(len(A[i]))
        )
        story.append(Paragraph(f"{termos} {sinais[i]} {b[i]}", eq_style))

    n = dados_originais["n_variaveis"]
    nao_neg = ", ".join(f"x<sub>{j+1}</sub>" for j in range(n))
    story.append(Paragraph(f"{nao_neg} ≥ 0", eq_style))
    story.append(PageBreak())

    # ── ETAPAS ──
    for idx, tableau in enumerate(simplex.tableaus_list):
        story.append(Paragraph(
            f"Quadro {idx + 1} de {len(simplex.tableaus_list)}",
            secao_style,
        ))

        has_artificial = (
            hasattr(tableau, '_funcao_objetivo_artificial')
            and tableau._funcao_objetivo_artificial is not None
        )
        fase = "Fase I" if has_artificial else "Fase II"
        story.append(Paragraph(fase, ParagraphStyle(
            "FaseLabel", parent=styles["Normal"],
            fontSize=10, textColor=rl_colors.HexColor("#757575"),
            spaceAfter=8,
        )))

        desc = getattr(tableau, 'descricao', '')
        col_entrada = getattr(tableau, 'coluna_entrada', None)
        linha_pivo = getattr(tableau, 'linha_pivo', None)
        headers_t = getattr(tableau, 'headers', [])

        if desc:
            story.append(Paragraph(desc, eq_style))

        if col_entrada is not None and linha_pivo is not None:
            entra = headers_t[col_entrada] if col_entrada < len(headers_t) else "?"
            col_saida = getattr(tableau, 'coluna_saida', None)
            sai = headers_t[col_saida] if col_saida is not None and col_saida < len(headers_t) else "?"
            pivo_val = tableau.tableau[linha_pivo][col_entrada] if (
                linha_pivo < len(tableau.tableau)
                and col_entrada < len(tableau.tableau[linha_pivo])
            ) else "?"
            story.append(Paragraph(
                f"Entra: {entra}  |  Sai: {sai}  |  Pivô: {pivo_val}",
                eq_style,
            ))

        razoes = getattr(tableau, 'razoes_info', [])
        if razoes:
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph("Teste da Razão:", ParagraphStyle(
                "RazaoLabel", parent=styles["Normal"],
                fontSize=9, fontName="Helvetica-Bold",
                textColor=rl_colors.HexColor("#1565C0"),
                spaceBefore=4, spaceAfter=2,
            )))
            for r in razoes:
                story.append(Paragraph(r, ParagraphStyle(
                    "RazaoItem", parent=styles["Normal"],
                    fontSize=8, fontName="Courier",
                    leftIndent=10, spaceAfter=1,
                    textColor=rl_colors.HexColor("#424242"),
                )))

        operacoes = getattr(tableau, 'operacoes_linha', [])
        if operacoes:
            story.append(Spacer(1, 0.1 * cm))
            story.append(Paragraph("Operações de Linha:", ParagraphStyle(
                "OpLabel", parent=styles["Normal"],
                fontSize=9, fontName="Helvetica-Bold",
                textColor=rl_colors.HexColor("#2E7D32"),
                spaceBefore=4, spaceAfter=2,
            )))
            for op in operacoes:
                story.append(Paragraph(op, ParagraphStyle(
                    "OpItem", parent=styles["Normal"],
                    fontSize=8, fontName="Courier",
                    leftIndent=10, spaceAfter=1,
                    textColor=rl_colors.HexColor("#2E7D32"),
                )))

        story.append(Spacer(1, 0.3 * cm))
        tabela = _criar_tabela_tableau(tableau, tabela_comprimento)
        story.append(tabela)
        story.append(Spacer(1, 0.5 * cm))

        if vertices is not None and caminho is not None:
            img_data = _grafico_para_imagem(
                dados_originais, vertices, caminho, idx,
                solucao=simplex.solucao if idx == len(simplex.tableaus_list) - 1 else None,
            )
            img = Image(img_data, width=14 * cm, height=10 * cm)
            story.append(KeepTogether(img))

        story.append(PageBreak())

    # ── RESULTADO ──
    story.append(Paragraph("Resultado Final", secao_style))
    sol = simplex.solucao

    if sol is None:
        story.append(Paragraph("Solução não disponível.", eq_style))
    else:
        dados_tabela = [["Variável", "Valor"]]
        for i, val in enumerate(sol["variaveis"]):
            if isinstance(val, float) and abs(val) < 1e-9:
                continue
            if val == 0:
                continue
            dados_tabela.append([f"x{i+1}", f"{math.trunc(val * 10000) / 10000:.4f}"])
        dados_tabela.append(["Z*", f"{math.trunc(sol['valor_objetivo'] * 10000) / 10000:.4f}"])

        t = Table(dados_tabela, colWidths=[6 * cm, 6 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _hex(HEADER_BG)),
            ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.black),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, _hex("#BDBDBD")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_hex(CELL_BG), _hex("#F5F5F5")]),
            ("BACKGROUND", (0, -1), (-1, -1), _hex("#E8F5E9")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ]))
        story.append(Spacer(1, 1 * cm))
        story.append(t)
        story.append(Spacer(1, 1 * cm))

        status = "Solução ótima encontrada"
        if ppl.eh_DuasEtapas:
            status += " (Método das Duas Fases)"
        story.append(Paragraph(status, ParagraphStyle(
            "Status", parent=styles["Normal"],
            fontSize=12, textColor=rl_colors.HexColor("#2E7D32"),
            alignment=TA_LEFT,
        )))

    doc.build(story)


def _criar_tabela_tableau(tableau, largura_total):
    n_rows = len(tableau.tableau)
    n_cols = max(len(row) for row in tableau.tableau)

    vbs = getattr(tableau, 'variaveis_basicas', [])
    headers_t = getattr(tableau, 'headers', [])
    has_artificial = (
        hasattr(tableau, '_funcao_objetivo_artificial')
        and tableau._funcao_objetivo_artificial is not None
    )

    n_restricoes = n_rows - (2 if has_artificial else 1)
    vb_por_linha = {row: col for col, row in vbs}

    col_entrada = getattr(tableau, 'coluna_entrada', None)
    linha_pivo = getattr(tableau, 'linha_pivo', None)
    basic_cols = {col for col, _ in vbs}

    header_row = ["VB", "#"]
    for j in range(n_cols - 1):
        if j < len(headers_t):
            header_row.append(headers_t[j])
        else:
            header_row.append("")
    header_row.append("b")

    data = [header_row]
    cell_colors = [[_hex(HEADER_BG)] * (n_cols + 2)]
    cell_text_colors = [[rl_colors.black] * (n_cols + 2)]

    for i, row in enumerate(tableau.tableau):
        if i < n_restricoes:
            vb_name = headers_t[vb_por_linha[i]] if i in vb_por_linha else ""
            row_label = f"L{i}"
        elif i == n_restricoes:
            vb_name = ""
            row_label = "Z"
        else:
            vb_name = ""
            row_label = "Z'"

        display_row = [vb_name, row_label]
        colors_row = [_hex(CELL_BG), _hex(CELL_BG)]
        text_colors_row = [rl_colors.black, rl_colors.black]

        for j, val in enumerate(row):
            if isinstance(val, float):
                display_row.append(f"{math.trunc(val * 10000) / 10000:.4f}")
            else:
                display_row.append(str(val))
            is_last = (j == len(row) - 1)

            if i < n_restricoes:
                if i == linha_pivo and j == col_entrada and col_entrada is not None:
                    colors_row.append(_hex(PIVOT_ELEM_BG))
                    text_colors_row.append(rl_colors.white)
                elif i == linha_pivo:
                    colors_row.append(_hex(PIVOT_ROW_BG))
                    text_colors_row.append(rl_colors.black)
                elif j == col_entrada and col_entrada is not None:
                    colors_row.append(_hex(PIVOT_COL_BG))
                    text_colors_row.append(rl_colors.black)
                elif j in basic_cols:
                    colors_row.append(_hex(BASIC_BG))
                    text_colors_row.append(rl_colors.black)
                else:
                    colors_row.append(_hex(CELL_BG))
                    text_colors_row.append(rl_colors.black)
            elif i == n_restricoes:
                if j == col_entrada and col_entrada is not None:
                    colors_row.append(_hex(PIVOT_COL_BG))
                    text_colors_row.append(rl_colors.black)
                elif val < 0 and not is_last:
                    colors_row.append(_hex(NEGATIVE_BG))
                    text_colors_row.append(rl_colors.black)
                else:
                    colors_row.append(_hex(Z_ROW_BG))
                    text_colors_row.append(rl_colors.black)
            else:
                if j == col_entrada and col_entrada is not None:
                    colors_row.append(_hex(PIVOT_COL_BG))
                    text_colors_row.append(rl_colors.black)
                elif val < 0 and not is_last:
                    colors_row.append(_hex(NEGATIVE_BG))
                    text_colors_row.append(rl_colors.black)
                else:
                    colors_row.append(_hex(Z_PRIME_ROW_BG))
                    text_colors_row.append(rl_colors.black)

        data.append(display_row)
        cell_colors.append(colors_row)
        cell_text_colors.append(text_colors_row)

    col_width = largura_total / (n_cols + 2)
    col_widths = [1.2 * col_width, 0.7 * col_width] + [col_width] * n_cols

    font_size = 8
    if n_cols > 8:
        font_size = 7
    if n_cols > 12:
        font_size = 6
    if n_cols > 18:
        font_size = 5

    t = Table(data, colWidths=col_widths)
    style_commands = [
        ("GRID", (0, 0), (-1, -1), 0.5, _hex("#BDBDBD")),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Courier"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]

    for i in range(len(data)):
        for j in range(len(data[i])):
            style_commands.append(("BACKGROUND", (j, i), (j, i), cell_colors[i][j]))
            style_commands.append(("TEXTCOLOR", (j, i), (j, i), cell_text_colors[i][j]))

    t.setStyle(TableStyle(style_commands))
    return t


def _grafico_para_imagem(dados, vertices, caminho, indice, solucao=None):
    fig = Figure(figsize=(7, 5), dpi=120)
    ax = fig.add_subplot(111)
    plotar_grafico(ax, dados, vertices, caminho, indice, solucao=solucao)
    fig.tight_layout(pad=2.0)

    buf = io.BytesIO()
    FigureCanvasAgg(fig).print_png(buf)
    buf.seek(0)
    return buf
