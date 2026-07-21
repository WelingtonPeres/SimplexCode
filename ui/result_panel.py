import tkinter as tk
from tkinter import ttk


class ResultPanel(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg="#F0F0F0")
        self.app = app
        self._construir()

    def _construir(self):
        self._titulo = tk.Label(
            self, text="Resultado",
            font=("Helvetica", 16, "bold"), bg="#F0F0F0", fg="#333333",
        )
        self._titulo.pack(pady=(20, 15))

        self._tabela_frame = tk.Frame(self, bg="#F0F0F0")
        self._tabela_frame.pack(pady=(0, 10))

        self._status = tk.Label(
            self, text="", font=("Helvetica", 11), bg="#F0F0F0",
        )
        self._status.pack(pady=(5, 5))

        self._z_label = tk.Label(
            self, text="", font=("Helvetica", 12, "bold"),
            bg="#F0F0F0", fg="#2E7D32",
        )
        self._z_label.pack(pady=(5, 15))

        btn_frame = tk.Frame(self, bg="#F0F0F0")
        btn_frame.pack()

        self._btn_grafico = tk.Button(
            btn_frame, text="Solução Gráfica",
            font=("Helvetica", 11, "bold"), bg="#FF9800", fg="white",
            padx=20, pady=6, border=0, cursor="hand2",
            activebackground="#F57C00",
            command=lambda: self.app.abrir_grafico(),
        )
        self._btn_grafico.pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame, text="Exportar PDF",
            font=("Helvetica", 11, "bold"), bg="#607D8B", fg="white",
            padx=20, pady=6, border=0, cursor="hand2",
            activebackground="#455A64",
            command=lambda: self.app.exportar_pdf(),
        ).pack(side=tk.LEFT, padx=5)

        self._btn_novo = tk.Button(
            btn_frame, text="Novo Problema",
            font=("Helvetica", 11, "bold"), bg="#4CAF50", fg="white",
            padx=25, pady=8, border=0, cursor="hand2",
            activebackground="#45a049",
            command=lambda: self.app._mostrar_frame("input"),
        )
        self._btn_novo.pack(side=tk.LEFT, padx=5)

    def carregar(self, simplex):
        for w in self._tabela_frame.winfo_children():
            w.destroy()

        solucao = simplex.solucao
        if solucao is None:
            self._status.config(text="Solucao nao disponivel.", fg="red")
            return

        n = len(solucao["variaveis"])
        tipo = "Minimizacao" if simplex.ppl.tipo_problema else "Maximizacao"

        self._status.config(
            text=f"Solucao otima encontrada ({tipo}).",
            fg="#2E7D32",
        )

        tk.Label(
            self._tabela_frame, text="Variavel", bg="#BDBDBD",
            font=("Helvetica", 10, "bold"), width=10, relief="ridge",
        ).grid(row=0, column=0, sticky="nsew")

        tk.Label(
            self._tabela_frame, text="Valor", bg="#BDBDBD",
            font=("Helvetica", 10, "bold"), width=12, relief="ridge",
        ).grid(row=0, column=1, sticky="nsew")

        for i in range(n):
            tk.Label(
                self._tabela_frame, text=f"x{i+1}",
                bg="#ECECEC", width=10, relief="ridge",
            ).grid(row=i + 1, column=0, sticky="nsew")

            val = solucao["variaveis"][i]
            texto = f"{val:.4f}" if isinstance(val, float) else str(val)
            tk.Label(
                self._tabela_frame, text=texto,
                bg="white", width=12, relief="ridge",
            ).grid(row=i + 1, column=1, sticky="nsew")

        self._z_label.config(
            text=f"Z = {solucao['valor_objetivo']:.4f}" if isinstance(
                solucao["valor_objetivo"], float
            ) else f"Z = {solucao['valor_objetivo']}",
        )

        if simplex.ppl.n_variaveis == 2:
            self._btn_grafico.config(state=tk.NORMAL)
        else:
            self._btn_grafico.config(state=tk.DISABLED)
