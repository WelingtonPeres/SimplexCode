import tkinter as tk
from tkinter import ttk

FASE_I_COLOR = "#D4E6F1"
FASE_II_COLOR = "#D5F5E3"
HEADER_BG = "#BDBDBD"
CELL_BG = "#FFFFFF"
BASIC_BG = "#E0E0E0"
PIVOT_COL_BG = "#A5D6A7"
PIVOT_ROW_BG = "#90CAF9"
PIVOT_ELEM_BG = "#FFF176"
TEXT_COLOR = "#212121"


class StepPanel(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg="#F0F0F0")
        self.app = app
        self._indice = 0
        self._tableaus = []
        self._canvas = None
        self._construir()

    def _construir(self):
        self._titulo = tk.Label(
            self, text="Execucao Passo a Passo",
            font=("Helvetica", 16, "bold"), bg="#F0F0F0", fg="#333333",
        )
        self._titulo.pack(pady=(15, 2))

        self._info = tk.Label(
            self, text="",
            font=("Helvetica", 10), bg="#F0F0F0", fg="#555555",
        )
        self._info.pack(pady=(0, 8))

        canvas_frame = tk.Frame(self, bg="#F0F0F0")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 5))

        self._canvas = tk.Canvas(
            canvas_frame, bg="#FAFAFA",
            highlightthickness=0, bd=0,
        )
        scroll_y = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL,
                                command=self._canvas.yview)
        scroll_x = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL,
                                command=self._canvas.xview)
        self._canvas.configure(
            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
        )

        self._canvas.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=0, column=2, sticky="ew")
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        nav_frame = tk.Frame(self, bg="#F0F0F0")
        nav_frame.pack(pady=(5, 2))

        tk.Button(
            nav_frame, text="<<", width=3,
            command=self._primeiro, bg="#E0E0E0", border=0, cursor="hand2",
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            nav_frame, text="<", width=3,
            command=self._anterior, bg="#E0E0E0", border=0, cursor="hand2",
        ).pack(side=tk.LEFT, padx=2)

        self._iter_label = tk.Label(
            nav_frame, text="", width=20,
            font=("Helvetica", 10), bg="#F0F0F0",
        )
        self._iter_label.pack(side=tk.LEFT, padx=10)

        tk.Button(
            nav_frame, text=">", width=3,
            command=self._proximo, bg="#E0E0E0", border=0, cursor="hand2",
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            nav_frame, text=">>", width=3,
            command=self._ultimo, bg="#E0E0E0", border=0, cursor="hand2",
        ).pack(side=tk.LEFT, padx=2)

        botoes_frame = tk.Frame(self, bg="#F0F0F0")
        botoes_frame.pack(pady=(0, 10))

        self._btn_resultado = tk.Button(
            botoes_frame, text="Ver Resultado",
            font=("Helvetica", 11, "bold"), bg="#2196F3", fg="white",
            padx=20, pady=6, border=0, cursor="hand2",
            activebackground="#1976D2",
            command=lambda: self.app._mostrar_frame("result"),
        )
        self._btn_resultado.pack(side=tk.LEFT, padx=5)

        tk.Button(
            botoes_frame, text="Novo Problema",
            font=("Helvetica", 11), bg="#E0E0E0",
            padx=20, pady=6, border=0, cursor="hand2",
            command=lambda: self.app._mostrar_frame("input"),
        ).pack(side=tk.LEFT, padx=5)

    def carregar(self, simplex):
        self._tableaus = simplex.tableaus_list
        self._indice = 0
        self._atualizar()

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
        if not self._tableaus:
            return

        t = self._tableaus[self._indice]
        self._iter_label.config(
            text=f"Quadro {self._indice + 1} de {len(self._tableaus)}"
        )

        fase = "Fase I" if t._funcao_objetivo_artificial is not None else "Fase II"
        desc = t.descricao if hasattr(t, "descricao") else ""

        info_text = f"{desc}  |  {fase}"
        if t.coluna_entrada is not None and t.linha_pivo is not None:
            entra = t.headers[t.coluna_entrada] if t.coluna_entrada < len(t.headers) else "?"
            sai = "?"
            for col, row in t.variaveis_basicas:
                if row == t.linha_pivo and hasattr(t, 'coluna_saida'):
                    if t.coluna_saida is not None and t.coluna_saida < len(t.headers):
                        sai = t.headers[t.coluna_saida]
                    break

            pivo = t.tableau[t.linha_pivo][t.coluna_entrada] if (
                t.linha_pivo < len(t.tableau)
                and t.coluna_entrada < len(t.tableau[t.linha_pivo])
            ) else "?"
            info_text += f"  |  Entra: {entra}  |  Sai: {sai}  |  Pivo: {pivo}"

        self._info.config(text=info_text)

        self._renderizar_tableau(t)

        total = len(self._tableaus)
        if self._indice < total - 1:
            self._btn_resultado.config(state=tk.DISABLED)
        else:
            self._btn_resultado.config(state=tk.NORMAL)

    def _renderizar_tableau(self, t):
        self._canvas.delete("all")

        if not t.tableau:
            return

        n_rows = len(t.tableau)
        n_cols = max(len(row) for row in t.tableau)
        headers_display = t.headers[:]
        if len(headers_display) < n_cols - 1:
            headers_display.extend([""] * (n_cols - 1 - len(headers_display)))
        headers_display.append("b")

        cell_w = 75
        cell_h = 28
        margin_x = 10
        margin_y = 10

        basic_cols = {col for col, row in t.variaveis_basicas}
        pivot_col = t.coluna_entrada if t.coluna_entrada is not None else -1
        pivot_row = t.linha_pivo if t.linha_pivo is not None else -1

        for j, h in enumerate(headers_display):
            x = margin_x + j * cell_w
            y = margin_y
            self._canvas.create_rectangle(
                x, y, x + cell_w, y + cell_h,
                fill=HEADER_BG, outline="#9E9E9E",
            )
            self._canvas.create_text(
                x + cell_w / 2, y + cell_h / 2,
                text=str(h)[:8], font=("Courier", 9, "bold"),
                fill=TEXT_COLOR,
            )

        n_restricoes = len(t.tableau) - (
            2 if t._funcao_objetivo_artificial is not None else 1
        )

        for i, row in enumerate(t.tableau):
            for j, val in enumerate(row):
                x = margin_x + j * cell_w
                y = margin_y + (i + 1) * cell_h

                if i < n_restricoes:
                    bg = CELL_BG
                    if i == pivot_row:
                        bg = PIVOT_ROW_BG
                    if j == pivot_col:
                        bg = PIVOT_COL_BG
                    if i == pivot_row and j == pivot_col:
                        bg = PIVOT_ELEM_BG
                    if j in basic_cols and j != pivot_col:
                        bg = BASIC_BG
                elif i == n_restricoes:
                    bg = "#E8F5E9" if t._funcao_objetivo_artificial is not None else "#E8F5E9"
                else:
                    bg = "#E3F2FD"

                self._canvas.create_rectangle(
                    x, y, x + cell_w, y + cell_h,
                    fill=bg, outline="#BDBDBD",
                )

                text = str(val)
                if isinstance(val, float):
                    text = f"{val:.2f}"
                self._canvas.create_text(
                    x + cell_w / 2, y + cell_h / 2,
                    text=text[:10], font=("Courier", 9),
                    fill=TEXT_COLOR,
                )

        for i in range(n_restricoes):
            y = margin_y + (i + 1) * cell_h
            self._canvas.create_text(
                margin_x - 5, y + cell_h / 2,
                text=f"R{i}", font=("Courier", 8, "bold"),
                fill="#757575", anchor="e",
            )

        z_y = margin_y + (n_restricoes + 1) * cell_h
        self._canvas.create_text(
            margin_x - 5, z_y + cell_h / 2,
            text="Z", font=("Courier", 8, "bold"),
            fill="#757575", anchor="e",
        )

        if t._funcao_objetivo_artificial is not None:
            z_prime_y = margin_y + (n_restricoes + 2) * cell_h
            self._canvas.create_text(
                margin_x - 5, z_prime_y + cell_h / 2,
                text="Z'", font=("Courier", 8, "bold"),
                fill="#757575", anchor="e",
            )

        total_w = margin_x + n_cols * cell_w + 20
        total_h = margin_y + (n_rows + 1) * cell_h + 20
        self._canvas.configure(scrollregion=(0, 0, total_w, total_h))
