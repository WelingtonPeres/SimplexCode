import tkinter as tk
from tkinter import ttk


class SimplexApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("SimplexCode")
        self.geometry("850x650")
        self.resizable(True, True)
        self.configure(bg="#F0F0F0")

        self.ppl = None
        self.simplex = None

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
        from PPL import PPL
        from Simplex import Simplex

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

        return None
