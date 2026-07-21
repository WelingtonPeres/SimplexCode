import numpy as np


def calcular_vertices(matriz_coeficientes, vetor_b, vetor_sinais):
    linhas = []
    for i in range(len(matriz_coeficientes)):
        linhas.append(
            (matriz_coeficientes[i][0], matriz_coeficientes[i][1],
             vetor_b[i], vetor_sinais[i])
        )
    linhas.append((1, 0, 0, ">="))
    linhas.append((0, 1, 0, ">="))

    vertices = []
    n = len(linhas)

    for i in range(n):
        for j in range(i + 1, n):
            p = _intersecao(linhas[i], linhas[j])
            if p is not None and _eh_viavel(p, linhas):
                p_novo = (round(p[0], 10), round(p[1], 10))
                if not any(
                    abs(p_novo[0] - v[0]) < 1e-8 and abs(p_novo[1] - v[1]) < 1e-8
                    for v in vertices
                ):
                    vertices.append(p_novo)

    if vertices:
        cx = sum(v[0] for v in vertices) / len(vertices)
        cy = sum(v[1] for v in vertices) / len(vertices)
        vertices.sort(key=lambda v: np.arctan2(v[1] - cy, v[0] - cx))

    return vertices


def _intersecao(l1, l2):
    a1, b1, c1, _ = l1
    a2, b2, c2, _ = l2
    det = a1 * b2 - a2 * b1
    if abs(det) < 1e-12:
        return None
    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    return (x, y)


def _eh_viavel(p, linhas):
    x, y = p
    if x < -1e-9 or y < -1e-9:
        return False
    for a, b_coef, c, sinal in linhas:
        valor = a * x + b_coef * y
        if sinal == "<=" and valor > c + 1e-9:
            return False
        elif sinal == ">=" and valor < c - 1e-9:
            return False
        elif sinal == "=" and abs(valor - c) > 1e-9:
            return False
    return True


def extrair_ponto_do_tableau(tableau):
    x = 0.0
    y = 0.0
    vbs = getattr(tableau, 'variaveis_basicas', [])
    mat = getattr(tableau, 'tableau', [])
    if not vbs or not mat:
        return None, None
    for col, row in vbs:
        if col == 0:
            x = float(mat[row][-1])
        elif col == 1:
            y = float(mat[row][-1])
    return x, y


def extrair_caminho(tableaus_list):
    caminho = []
    for tableau in tableaus_list:
        x, y = extrair_ponto_do_tableau(tableau)
        if x is not None and y is not None:
            caminho.append((x, y))
        else:
            caminho.append(None)
    return caminho


def plotar_grafico(ax, dados, vertices, caminho, indice, solucao=None):
    A = dados["matriz_coeficientes"]
    b = dados["vetor_b"]
    sinais = dados["vetor_sinais"]
    fo = dados["funcao_objetivo"]

    max_x = 1.0
    max_y = 1.0
    for i in range(len(A)):
        a1, a2 = A[i][0], A[i][1]
        bi = b[i]
        if abs(a1) > 1e-9:
            max_x = max(max_x, abs(bi / a1))
        if abs(a2) > 1e-9:
            max_y = max(max_y, abs(bi / a2))
    for v in vertices:
        max_x = max(max_x, v[0] + 1)
        max_y = max(max_y, v[1] + 1)
    max_x = max(max_x * 1.25, 2)
    max_y = max(max_y * 1.25, 2)

    x_vals = np.linspace(0, max_x, 400)

    cores = ["#1565C0", "#2E7D32", "#E65100", "#6A1B9A",
             "#00838F", "#C62828", "#283593", "#4E342E"]

    for i in range(len(A)):
        a1, a2 = A[i][0], A[i][1]
        bi = b[i]
        color = cores[i % len(cores)]
        label = f"{a1}x₁ + {a2}x₂ {sinais[i]} {bi}"
        if abs(a2) > 1e-9:
            y_linha = (bi - a1 * x_vals) / a2
            ax.plot(x_vals, y_linha, color=color, linewidth=1.5, label=label)
        elif abs(a1) > 1e-9:
            x_const = bi / a1
            ax.axvline(x=x_const, color=color, linewidth=1.5, label=label)

    x_vals_fill = np.linspace(0, max_x, 200)
    y_vals_fill = np.linspace(0, max_y, 200)
    X, Y = np.meshgrid(x_vals_fill, y_vals_fill)
    mask = np.ones_like(X, dtype=bool)
    for i in range(len(A)):
        a1, a2 = A[i][0], A[i][1]
        bi = b[i]
        sinal = sinais[i]
        valores = a1 * X + a2 * Y
        if sinal == "<=":
            mask &= (valores <= bi + 1e-9)
        elif sinal == ">=":
            mask &= (valores >= bi - 1e-9)
        elif sinal == "=":
            mask &= (np.abs(valores - bi) <= 1e-9)
    ax.contourf(X, Y, mask.astype(float), levels=[0.5, 1.5],
                colors=["#BBDEFB"], alpha=0.15)

    if vertices:
        vx = [v[0] for v in vertices] + [vertices[0][0]]
        vy = [v[1] for v in vertices] + [vertices[0][1]]
        ax.fill(vx, vy, alpha=0.08, color="#1976D2")

        for vx_v, vy_v in vertices:
            z_val = fo[0] * vx_v + fo[1] * vy_v
            ax.plot(vx_v, vy_v, "o", color="#757575", markersize=6)
            ax.annotate(
                f"({vx_v:.2f}, {vy_v:.2f})\nZ={z_val:.2f}",
                (vx_v, vy_v),
                textcoords="offset points",
                xytext=(8, 8),
                fontsize=7,
                color="#424242",
                bbox=dict(boxstyle="round,pad=0.2", fc="white",
                          ec="#BDBDBD", alpha=0.9),
            )

    pontos_validos = [p for p in caminho[:indice + 1] if p is not None]
    if len(pontos_validos) >= 2:
        px = [p[0] for p in pontos_validos]
        py = [p[1] for p in pontos_validos]
        ax.plot(px, py, "r--", linewidth=2, alpha=0.7, marker="o",
                markersize=5, markerfacecolor="red")

    if caminho and indice < len(caminho):
        p_atual = caminho[indice]
        if p_atual is not None:
            ax.plot(p_atual[0], p_atual[1], "o",
                    color="#C62828", markersize=14, zorder=5,
                    markeredgecolor="white", markeredgewidth=2)

    n_tableaus = len(caminho)
    if indice == n_tableaus - 1 and solucao and vertices:
        if solucao and len(solucao.get("variaveis", [])) >= 2:
            x_otimo = solucao["variaveis"][0]
            y_otimo = solucao["variaveis"][1]
            ax.plot(x_otimo, y_otimo, "*",
                    color="#FFD600", markersize=18, zorder=6,
                    markeredgecolor="#F57F17", markeredgewidth=1)

    ax.set_xlabel("x₁", fontsize=11)
    ax.set_ylabel("x₂", fontsize=11)
    ax.set_title("Solução Gráfica — Método Simplex", fontsize=13, fontweight="bold")
    ax.set_xlim(0, max_x)
    ax.set_ylim(0, max_y)
    ax.axhline(y=0, color="black", linewidth=0.5)
    ax.axvline(x=0, color="black", linewidth=0.5)
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="upper right", fontsize=7, framealpha=0.9)
    ax.set_aspect("equal")
