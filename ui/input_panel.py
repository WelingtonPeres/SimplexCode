import tkinter as tk
from tkinter import ttk, messagebox


class InputPanel(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg="#F0F0F0")
        self.app = app

        self._n_var = tk.IntVar(value=2)
        self._n_restr = tk.IntVar(value=2)
        self._tipo = tk.BooleanVar(value=False)

        self._entradas_coef = []
        self._entradas_b = []
        self._entradas_sinais = []
        self._entradas_fo = []

        self._construir()

    def _construir(self):
        titulo = tk.Label(
            self, text="SimplexCode",
            font=("Helvetica", 18, "bold"), bg="#F0F0F0", fg="#333333",
        )
        titulo.pack(pady=(20, 5))

        subtitulo = tk.Label(
            self, text="Defina o problema de Programacao Linear",
            font=("Helvetica", 11), bg="#F0F0F0", fg="#666666",
        )
        subtitulo.pack(pady=(0, 15))

        config_frame = tk.Frame(self, bg="#F0F0F0")
        config_frame.pack(pady=(0, 10))

        tk.Label(config_frame, text="Numero de variaveis:", bg="#F0F0F0").grid(
            row=0, column=0, sticky="e", padx=(0, 5)
        )
        tk.Spinbox(
            config_frame, from_=2, to=10, width=5,
            textvariable=self._n_var, command=self._atualizar_grid,
        ).grid(row=0, column=1, sticky="w")

        tk.Label(config_frame, text="Numero de restricoes:", bg="#F0F0F0").grid(
            row=1, column=0, sticky="e", padx=(0, 5), pady=(5, 0)
        )
        tk.Spinbox(
            config_frame, from_=1, to=10, width=5,
            textvariable=self._n_restr, command=self._atualizar_grid,
        ).grid(row=1, column=1, sticky="w", pady=(5, 0))

        tk.Radiobutton(
            config_frame, text="Maximizacao", variable=self._tipo,
            value=False, bg="#F0F0F0",
        ).grid(row=0, column=2, padx=(30, 5))
        tk.Radiobutton(
            config_frame, text="Minimizacao", variable=self._tipo,
            value=True, bg="#F0F0F0",
        ).grid(row=0, column=3)

        self._grid_frame = tk.Frame(self, bg="#F0F0F0")
        self._grid_frame.pack(pady=(5, 10))

        btn_frame = tk.Frame(self, bg="#F0F0F0")
        btn_frame.pack(pady=(0, 15))

        tk.Button(
            btn_frame, text="Resolver",
            font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white",
            padx=30, pady=8, border=0, cursor="hand2",
            activebackground="#45a049", command=self._resolver,
        ).pack()

        self._atualizar_grid()

    def _atualizar_grid(self):
        for w in self._grid_frame.winfo_children():
            w.destroy()

        self._entradas_coef = []
        self._entradas_b = []
        self._entradas_sinais = []
        self._entradas_fo = []

        n = self._n_var.get()
        m = self._n_restr.get()

        tk.Label(
            self._grid_frame, text="Restricoes",
            font=("Helvetica", 10, "bold"), bg="#F0F0F0",
        ).grid(row=0, column=0, columnspan=n + 2, pady=(0, 3))

        for j in range(n):
            tk.Label(
                self._grid_frame, text=f"x{j+1}", bg="#DDDDDD",
                relief="groove", width=6,
            ).grid(row=1, column=j, sticky="nsew")

        tk.Label(
            self._grid_frame, text="Sinal", bg="#DDDDDD",
            relief="groove", width=6,
        ).grid(row=1, column=n, sticky="nsew")

        tk.Label(
            self._grid_frame, text="b", bg="#DDDDDD",
            relief="groove", width=6,
        ).grid(row=1, column=n + 1, sticky="nsew")

        for i in range(m):
            linha_coef = []
            for j in range(n):
                e = tk.Entry(self._grid_frame, width=6, justify="center")
                e.grid(row=i + 2, column=j, sticky="nsew", padx=1, pady=1)
                e.insert(0, "0")
                linha_coef.append(e)
            self._entradas_coef.append(linha_coef)

            sinal_var = tk.StringVar(value="<=")
            cb = ttk.Combobox(
                self._grid_frame, textvariable=sinal_var,
                values=["<=", ">=", "="], width=5, state="readonly",
            )
            cb.grid(row=i + 2, column=n, sticky="nsew", padx=1, pady=1)
            self._entradas_sinais.append(sinal_var)

            e_b = tk.Entry(self._grid_frame, width=6, justify="center")
            e_b.grid(row=i + 2, column=n + 1, sticky="nsew", padx=1, pady=1)
            e_b.insert(0, "0")
            self._entradas_b.append(e_b)

        sep_row = m + 2
        tk.Label(
            self._grid_frame, text="Funcao Objetivo",
            font=("Helvetica", 10, "bold"), bg="#F0F0F0",
        ).grid(row=sep_row, column=0, columnspan=n + 2, pady=(8, 3))

        for j in range(n):
            tk.Label(
                self._grid_frame, text=f"x{j+1}", bg="#DDDDDD",
                relief="groove", width=6,
            ).grid(row=sep_row + 1, column=j, sticky="nsew")

            e = tk.Entry(self._grid_frame, width=6, justify="center")
            e.grid(row=sep_row + 2, column=j, sticky="nsew", padx=1, pady=1)
            e.insert(0, "0")
            self._entradas_fo.append(e)

    def _resolver(self):
        try:
            n = self._n_var.get()
            m = self._n_restr.get()

            matriz_coef = []
            for linha in self._entradas_coef:
                linha_vals = []
                for e in linha:
                    val = e.get().strip()
                    if val == "":
                        raise ValueError("Preencha todos os coeficientes.")
                    linha_vals.append(float(val))
                matriz_coef.append(linha_vals)

            vetor_b = []
            for e in self._entradas_b:
                val = e.get().strip()
                if val == "":
                    raise ValueError("Preencha todos os valores de b.")
                vetor_b.append(float(val))

            vetor_sinais = [s.get() for s in self._entradas_sinais]
            if not all(s in ["<=", ">=", "="] for s in vetor_sinais):
                raise ValueError("Sinais invalidos.")

            funcao_objetivo = []
            for e in self._entradas_fo:
                val = e.get().strip()
                if val == "":
                    raise ValueError("Preencha todos os coeficientes da funcao objetivo.")
                funcao_objetivo.append(float(val))

            erro = self.app.resolver(
                n, matriz_coef, vetor_b, vetor_sinais,
                funcao_objetivo, self._tipo.get(),
            )

            if erro:
                messagebox.showerror("Erro", erro)
            else:
                self.app._mostrar_frame("step")

        except ValueError as e:
            messagebox.showerror("Erro de entrada", str(e))
