import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime


class SimplexApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("SimplexCode")
        self.geometry("850x650")
        self.resizable(True, True)
        self.configure(bg="#F0F0F0")

        self.ppl = None
        self.simplex = None
        self._dados_originais = None
        self._graph_window = None

        self.frames = {}
        self._criar_frames()
        self._mostrar_frame("input")

    def _criar_frames(self):
        from ui.input_panel import InputPanel
        from ui.step_panel import StepPanel
        from ui.result_panel import ResultPanel

        container = tk.Frame(self, bg="#F0F0F0")
        container.pack(fill=tk.BOTH, expand=True)

        self.frames["input"] = InputPanel(container, self)
        self.frames["step"] = StepPanel(container, self)
        self.frames["result"] = ResultPanel(container, self)

        for f in self.frames.values():
            f.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _mostrar_frame(self, nome):
        self.frames[nome].tkraise()
        if nome == "step" and self.simplex is not None:
            self.frames["step"].carregar(self.simplex)
        elif nome == "result" and self.simplex is not None:
            self.frames["result"].carregar(self.simplex)

    def resolver(self, n_variaveis, matriz_coeficientes, vetor_b,
                 vetor_sinais, funcao_objetivo, eh_minimizacao):
        from src.PPL import PPL
        from src.Simplex import Simplex

        self._dados_originais = {
            "n_variaveis": n_variaveis,
            "matriz_coeficientes": [row[:] for row in matriz_coeficientes],
            "vetor_b": vetor_b[:],
            "vetor_sinais": vetor_sinais[:],
            "funcao_objetivo": funcao_objetivo[:],
            "eh_minimizacao": eh_minimizacao,
        }

        try:
            self.ppl = PPL(
                n_variaveis=n_variaveis,
                matriz_coeficientes=matriz_coeficientes,
                vetor_b=vetor_b,
                vetor_sinais=vetor_sinais,
                funcao_objetivo=funcao_objetivo,
                eh_minimizacao=eh_minimizacao,
            )
            self.simplex = Simplex(self.ppl)
            self.simplex.InicarSimpex()
        except ValueError as e:
            return str(e)

        if n_variaveis == 2:
            self.abrir_grafico()

        return None

    def abrir_grafico(self):
        if self._graph_window is not None and self._graph_window.winfo_exists():
            self._graph_window.lift()
            self._graph_window.focus_force()
            return
        if self.simplex is None or self._dados_originais is None:
            return
        from ui.graph_window import GraphWindow
        self._graph_window = GraphWindow(self, self._dados_originais, self.simplex)

    def sincronizar_grafico(self, indice):
        if self._graph_window is not None and self._graph_window.winfo_exists():
            self._graph_window.sincronizar(indice)

    def exportar_pdf(self):
        if self.simplex is None or self.ppl is None or self._dados_originais is None:
            messagebox.showwarning("Aviso", "Nenhum problema resolvido para exportar.")
            return

        nome_padrao = f"simplex_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        caminho = filedialog.asksaveasfilename(
            title="Salvar relatório PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile=nome_padrao,
        )
        if not caminho:
            return

        try:
            from reporting.pdf_generator import gerar_relatorio
            gerar_relatorio(caminho, self.ppl, self.simplex, self._dados_originais)
            messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar PDF:\n{e}")
