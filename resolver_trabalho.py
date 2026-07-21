import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.PPL import PPL
from src.Simplex import Simplex
from reporting.pdf_generator import gerar_relatorio

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "relatorios")
os.makedirs(OUTPUT_DIR, exist_ok=True)

problemas = []

# Questao 01 — ChemLabs: Max Z = 8A + 10B
problemas.append({
    "nome": "Questao_01_ChemLabs",
    "dados": {
        "n_variaveis": 2,
        "matriz_coeficientes": [
            [0.5, 0.5], [0.6, 0.4],
            [1, 0], [1, 0], [0, 1], [0, 1],
        ],
        "vetor_b": [150, 145, 30, 150, 40, 200],
        "vetor_sinais": ["<=", "<=", ">=", "<=", ">=", "<="],
        "funcao_objetivo": [8, 10],
        "eh_minimizacao": False,
    },
})

# Questao 02 — Top Toys: Max Z = 2000R + 3000T (+4500)
problemas.append({
    "nome": "Questao_02_TopToys",
    "dados": {
        "n_variaveis": 2,
        "matriz_coeficientes": [
            [300, 2000], [300, 0], [0, 2000],
            [1, 0], [0, 1],
        ],
        "vetor_b": [20000, 16000, 16000, 1, 1],
        "vetor_sinais": ["<=", "<=", "<=", ">=", ">="],
        "funcao_objetivo": [2000, 3000],
        "eh_minimizacao": False,
    },
})

# Questao 03 — Burroughs Garment: Max Z = 8S + 12Bl
problemas.append({
    "nome": "Questao_03_BurroughsGarment",
    "dados": {
        "n_variaveis": 2,
        "matriz_coeficientes": [
            [20, 60], [70, 60], [12, 4],
        ],
        "vetor_b": [60000, 84000, 12000],
        "vetor_sinais": ["<=", "<=", "<="],
        "funcao_objetivo": [8, 12],
        "eh_minimizacao": False,
    },
})

# Questao 04 — Wild West: Max Z = 8x1 + 5x2
problemas.append({
    "nome": "Questao_04_WildWest",
    "dados": {
        "n_variaveis": 2,
        "matriz_coeficientes": [
            [2, 1], [1, 0], [0, 1],
        ],
        "vetor_b": [400, 150, 200],
        "vetor_sinais": ["<=", "<=", "<="],
        "funcao_objetivo": [8, 5],
        "eh_minimizacao": False,
    },
})

# Questao 05 — Logistica Fria: Min Z = 800x1+1200x2+700x3+900y1+1100y2+600y3 (+5000)
problemas.append({
    "nome": "Questao_05_LogisticaFria",
    "dados": {
        "n_variaveis": 6,
        "matriz_coeficientes": [
            [1,1,1,0,0,0], [0,0,0,1,1,1],
            [1,0,0,1,0,0], [0,1,0,0,1,0], [0,0,1,0,0,1],
            [1,0,0,0,0,0], [1,0,0,0,0,0],
            [0,1,0,0,0,0], [0,1,0,0,0,0],
            [0,0,1,0,0,0], [0,0,1,0,0,0],
            [0,0,0,1,0,0], [0,0,0,1,0,0],
            [0,0,0,0,1,0], [0,0,0,0,1,0],
            [0,0,0,0,0,1], [0,0,0,0,0,1], [0,0,0,0,0,1],
        ],
        "vetor_b": [120,90,50,70,40, 24,50, 24,50, 24,50, 18,40, 18,40, 18,40,15],
        "vetor_sinais": [
            "=","=",">=",">=",">=",
            ">=","<=",">=","<=",">=","<=",
            ">=","<=",">=","<=",">=","<=",">=",
        ],
        "funcao_objetivo": [800, 1200, 700, 900, 1100, 600],
        "eh_minimizacao": True,
    },
})


print("=" * 60)
print("RESOLUCAO DOS PROBLEMAS DE PROGRAMACAO LINEAR")
print("=" * 60)

for p in problemas:
    nome = p["nome"]
    d = p["dados"]

    print(f"\n{'=' * 50}")
    print(f"  {nome}")
    print(f"{'=' * 50}")

    try:
        ppl = PPL(
            n_variaveis=d["n_variaveis"],
            matriz_coeficientes=d["matriz_coeficientes"],
            vetor_b=d["vetor_b"],
            vetor_sinais=d["vetor_sinais"],
            funcao_objetivo=d["funcao_objetivo"],
            eh_minimizacao=d["eh_minimizacao"],
        )
        simplex = Simplex(ppl)
        solucao = simplex.InicarSimpex()

        print(f"  Status: Solucao otima encontrada")
        print(f"  Z* = {solucao['valor_objetivo']:.4f}")
        print(f"  Quadros: {len(simplex.tableaus_list)}")
        print(f"  Variaveis: ", end="")
        for i, val in enumerate(solucao["variaveis"]):
            print(f"x{i+1}={val:.4f}  ", end="")
        print()

        pdf_path = os.path.join(OUTPUT_DIR, f"{nome}.pdf")
        gerar_relatorio(pdf_path, ppl, simplex, d)
        print(f"  PDF: {pdf_path}  ({os.path.getsize(pdf_path)} bytes)")

    except Exception as e:
        print(f"  ERRO: {e}")

print(f"\n{'=' * 60}")
print(f"Relatorios salvos em: {OUTPUT_DIR}")
print(f"{'=' * 60}")
