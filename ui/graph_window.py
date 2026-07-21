import tkinter as tk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from reporting.grafico import (
    calcular_vertices,
    extrair_caminho,
    plotar_grafico,
)


class GraphWindow(tk.Toplevel):

    def __init__(self, parent, dados_originais, simplex):
        super().__init__(parent)
        self.title("Solução Gráfica")
        self.geometry("700x650")
        self.resizable(True, True)
        self.configure(bg="#F0F0F0")

        self._dados = dados_originais
        self._simplex = simplex
        self._tableaus = simplex.tableaus_list
        self._indice = 0

        self._vertices = []
        self._caminho_pontos = []

        self._fig = Figure(figsize=(6, 5.5), dpi=100)
        self._ax = self._fig.add_subplot(111)

        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._construir_navegacao()
        self._vertices = calcular_vertices(
            self._dados["matriz_coeficientes"],
            self._dados["vetor_b"],
            self._dados["vetor_sinais"],
        )
        self._caminho_pontos = extrair_caminho(self._tableaus)
        self._renderizar()
        self._atualizar_zoom()

        self.protocol("WM_DELETE_WINDOW", self._fechar)

    def _fechar(self):
        if hasattr(self.master, '_graph_window'):
            self.master._graph_window = None
        self.destroy()

    def _construir_navegacao(self):
        nav = tk.Frame(self, bg="#F0F0F0")
        nav.pack(pady=(0, 5))

        tk.Button(
            nav, text="<<", width=3, bg="#E0E0E0", border=0, cursor="hand2",
            command=self._primeiro,
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            nav, text="<", width=3, bg="#E0E0E0", border=0, cursor="hand2",
            command=self._anterior,
        ).pack(side=tk.LEFT, padx=2)

        self._quadro_label = tk.Label(
            nav, text="", width=20, font=("Helvetica", 10), bg="#F0F0F0",
        )
        self._quadro_label.pack(side=tk.LEFT, padx=10)

        tk.Button(
            nav, text=">", width=3, bg="#E0E0E0", border=0, cursor="hand2",
            command=self._proximo,
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            nav, text=">>", width=3, bg="#E0E0E0", border=0, cursor="hand2",
            command=self._ultimo,
        ).pack(side=tk.LEFT, padx=2)

    def _atualizar_nav_label(self):
        self._quadro_label.config(
            text=f"Quadro {self._indice + 1} de {len(self._tableaus)}"
        )

    def _primeiro(self):
        self._indice = 0
        self._atualizar()

    def _anterior(self):
        if self._indice > 0:
            self._indice -= 1
            self._atualizar()

    def _proximo(self):
        if self._indice < len(self._tableaus) - 1:
            self._indice += 1
            self._atualizar()

    def _ultimo(self):
        self._indice = len(self._tableaus) - 1
        self._atualizar()

    def _atualizar(self):
        self._atualizar_nav_label()
        self._renderizar()

    def sincronizar(self, indice):
        if 0 <= indice < len(self._tableaus):
            self._indice = indice
            self._atualizar_nav_label()
            self._renderizar()

    def _renderizar(self):
        self._ax.clear()
        plotar_grafico(
            self._ax, self._dados, self._vertices,
            self._caminho_pontos, self._indice,
            solucao=self._simplex.solucao if self._indice == len(self._tableaus) - 1 else None,
        )
        self._canvas.draw()

    def _atualizar_zoom(self):
        largura = self._fig.get_size_inches()[0] * self._fig.dpi
        altura = self._fig.get_size_inches()[1] * self._fig.dpi
        self._fig.tight_layout(pad=2.0)
