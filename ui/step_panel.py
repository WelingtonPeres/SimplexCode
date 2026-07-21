import tkinter as tk
from tkinter import ttk

FASE_I_COLOR = "#D4E6F1"
FASE_II_COLOR = "#D5F5E3"
HEADER_BG = "#BDBDBD"
CELL_BG = "#FFFFFF"
BASIC_BG = "#E8E8E8"
PIVOT_COL_BG = "#BBDEFB"
PIVOT_ROW_BG = "#BBDEFB"
PIVOT_ELEM_BG = "#1565C0"
PIVOT_ELEM_FG = "#FFFFFF"
NEGATIVE_BG = "#FFCDD2"
Z_ROW_BG = "#E8F5E9"
Z_PRIME_ROW_BG = "#E3F2FD"
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

        ops_frame = tk.Frame(self, bg="#F0F0F0")
        ops_frame.pack(fill=tk.X, padx=20, pady=(0, 3))

        self._ops_text = tk.Text(
            ops_frame, height=5,
            font=("Courier", 9), bg="#FAFAFA", fg="#212121",
            wrap=tk.WORD, borderwidth=1, relief="solid",
            state=tk.DISABLED,
        )
        self._ops_text.pack(fill=tk.X)

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

        self._btn_grafico = tk.Button(
            botoes_frame, text="Solução Gráfica",
            font=("Helvetica", 11), bg="#FF9800", fg="white",
            padx=20, pady=6, border=0, cursor="hand2",
            activebackground="#F57C00", state=tk.DISABLED,
            command=lambda: self.app.abrir_grafico(),
        )
        self._btn_grafico.pack(side=tk.LEFT, padx=5)

        tk.Button(
            botoes_frame, text="Exportar PDF",
            font=("Helvetica", 11), bg="#607D8B", fg="white",
            padx=20, pady=6, border=0, cursor="hand2",
            activebackground="#455A64",
            command=lambda: self.app.exportar_pdf(),
        ).pack(side=tk.LEFT, padx=5)

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

        self._ops_text.config(state=tk.NORMAL)
        self._ops_text.delete("1.0", tk.END)

        razoes = getattr(t, 'razoes_info', [])
        operacoes = getattr(t, 'operacoes_linha', [])

        if razoes:
            self._ops_text.insert(tk.END, "─── Teste da Razão ───\n", "header")
            for r in razoes:
                self._ops_text.insert(tk.END, f"  {r}\n", "razao")

        if operacoes:
            if razoes:
                self._ops_text.insert(tk.END, "\n")
            self._ops_text.insert(tk.END, "─── Operações de Linha ───\n", "header")
            for op in operacoes:
                self._ops_text.insert(tk.END, f"  {op}\n", "operacao")

        if not razoes and not operacoes:
            self._ops_text.insert(tk.END, "Quadro inicial — sem operações ainda.", "empty")

        self._ops_text.tag_configure("header", font=("Courier", 9, "bold"), foreground="#1565C0")
        self._ops_text.tag_configure("razao", font=("Courier", 9), foreground="#424242")
        self._ops_text.tag_configure("operacao", font=("Courier", 9), foreground="#2E7D32")
        self._ops_text.tag_configure("empty", font=("Courier", 9), foreground="#9E9E9E")
        self._ops_text.config(state=tk.DISABLED)

        self._renderizar_tableau(t)

        total = len(self._tableaus)
        if self._indice < total - 1:
            self._btn_resultado.config(state=tk.DISABLED)
        else:
            self._btn_resultado.config(state=tk.NORMAL)

        if self.app.simplex and self.app.simplex.ppl.n_variaveis == 2:
            self.app.sincronizar_grafico(self._indice)
            if self._btn_grafico:
                self._btn_grafico.config(state=tk.NORMAL)
        elif self._btn_grafico:
            self._btn_grafico.config(state=tk.DISABLED)

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

        cell_w = 72
        cell_h = 28
        vb_w = 52
        label_w = 34

        n_restricoes = len(t.tableau) - (
            2 if t._funcao_objetivo_artificial is not None else 1
        )

        vb_por_linha = {row: col for col, row in t.variaveis_basicas}

        basic_cols = {col for col, row in t.variaveis_basicas}
        pivot_col = t.coluna_entrada if t.coluna_entrada is not None else -1
        pivot_row = t.linha_pivo if t.linha_pivo is not None else -1

        total_w = vb_w + label_w + n_cols * cell_w + 20
        total_h = (n_rows + 1) * cell_h + 20

        self._canvas.update_idletasks()
        canvas_w = self._canvas.winfo_width()
        canvas_h = self._canvas.winfo_height()
        offset_x = max(0, (canvas_w - total_w) // 2)
        offset_y = max(0, (canvas_h - total_h) // 2)

        def _x_vb():
            return offset_x

        def _x_label():
            return offset_x + vb_w

        def _x_data(j):
            return offset_x + vb_w + label_w + j * cell_w

        # --- Headers ---
        header_y = offset_y
        self._canvas.create_rectangle(
            _x_vb(), header_y, _x_vb() + vb_w, header_y + cell_h,
            fill=HEADER_BG, outline="#9E9E9E",
        )
        self._canvas.create_text(
            _x_vb() + vb_w / 2, header_y + cell_h / 2,
            text="VB", font=("Courier", 9, "bold"), fill=TEXT_COLOR,
        )

        self._canvas.create_rectangle(
            _x_label(), header_y, _x_label() + label_w, header_y + cell_h,
            fill=HEADER_BG, outline="#9E9E9E",
        )
        self._canvas.create_text(
            _x_label() + label_w / 2, header_y + cell_h / 2,
            text="#", font=("Courier", 9, "bold"), fill=TEXT_COLOR,
        )

        for j, h in enumerate(headers_display):
            x = _x_data(j)
            self._canvas.create_rectangle(
                x, header_y, x + cell_w, header_y + cell_h,
                fill=HEADER_BG, outline="#9E9E9E",
            )
            self._canvas.create_text(
                x + cell_w / 2, header_y + cell_h / 2,
                text=str(h)[:8], font=("Courier", 9, "bold"), fill=TEXT_COLOR,
            )

        # --- Data rows ---
        for i, row in enumerate(t.tableau):
            y = offset_y + (i + 1) * cell_h

            if i < n_restricoes:
                vb_name = t.headers[vb_por_linha[i]] if i in vb_por_linha else ""
            else:
                vb_name = ""

            self._canvas.create_rectangle(
                _x_vb(), y, _x_vb() + vb_w, y + cell_h,
                fill=CELL_BG, outline="#BDBDBD",
            )
            self._canvas.create_text(
                _x_vb() + vb_w / 2, y + cell_h / 2,
                text=vb_name[:6], font=("Courier", 9), fill=TEXT_COLOR,
            )

            if i < n_restricoes:
                row_label = f"L{i}"
                label_fill = CELL_BG
                label_color = "#757575"
            elif i == n_restricoes:
                row_label = "Z"
                label_fill = Z_ROW_BG
                label_color = "#2E7D32"
            else:
                row_label = "Z'"
                label_fill = Z_PRIME_ROW_BG
                label_color = "#1565C0"

            self._canvas.create_rectangle(
                _x_label(), y, _x_label() + label_w, y + cell_h,
                fill=label_fill, outline="#BDBDBD",
            )
            self._canvas.create_text(
                _x_label() + label_w / 2, y + cell_h / 2,
                text=row_label, font=("Courier", 9, "bold"), fill=label_color,
            )

            for j, val in enumerate(row):
                x = _x_data(j)
                is_last_col = (j == len(row) - 1)

                if i < n_restricoes:
                    if i == pivot_row and j == pivot_col:
                        bg = PIVOT_ELEM_BG
                        fg = PIVOT_ELEM_FG
                    elif i == pivot_row:
                        bg = PIVOT_ROW_BG
                        fg = TEXT_COLOR
                    elif j == pivot_col:
                        bg = PIVOT_COL_BG
                        fg = TEXT_COLOR
                    elif j in basic_cols:
                        bg = BASIC_BG
                        fg = TEXT_COLOR
                    else:
                        bg = CELL_BG
                        fg = TEXT_COLOR
                elif i == n_restricoes:
                    if j == pivot_col:
                        bg = PIVOT_COL_BG
                        fg = TEXT_COLOR
                    elif val < 0 and not is_last_col:
                        bg = NEGATIVE_BG
                        fg = TEXT_COLOR
                    else:
                        bg = Z_ROW_BG
                        fg = TEXT_COLOR
                else:
                    if j == pivot_col:
                        bg = PIVOT_COL_BG
                        fg = TEXT_COLOR
                    elif val < 0 and not is_last_col:
                        bg = NEGATIVE_BG
                        fg = TEXT_COLOR
                    else:
                        bg = Z_PRIME_ROW_BG
                        fg = TEXT_COLOR

                self._canvas.create_rectangle(
                    x, y, x + cell_w, y + cell_h,
                    fill=bg, outline="#BDBDBD",
                )

                text = str(val)
                if isinstance(val, float):
                    text = f"{val:.2f}"
                self._canvas.create_text(
                    x + cell_w / 2, y + cell_h / 2,
                    text=text[:10], font=("Courier", 9), fill=fg,
                )

        self._canvas.configure(scrollregion=(
            -offset_x, -offset_y,
            total_w + max(0, canvas_w - total_w),
            total_h + max(0, canvas_h - total_h),
        ))
