import copy

from src.PPL import PPL
from src.Tableau import Tableau


class Simplex:

    def __init__(self, ppl: PPL):
        self.ppl = ppl
        self.tableaus_list = []
        self.stage = 0
        self.solucao = None

    def InicarSimpex(self):
        
        tableau_inicial = Tableau(
            id_stage=1,
            headers=self.ppl.headers,
            matriz_coeficientes=self.ppl.matriz_coeficientes,
            vetor_b=self.ppl.vetor_b,
            funcao_objetivo=self.ppl.funcao_objetivo,
            funcao_objetivo_artificial=self.ppl.funcao_objetivo_artificial,
        )
        self.tableaus_list.append(copy.deepcopy(tableau_inicial))

        tableau_atual = tableau_inicial

        if self.ppl.eh_DuasEtapas: # Se for de duas etapas
            self.stage = 1
            
            while not self.__verificar_otimalidade(tableau_atual): # Enquanto a solução não for otima o codigo roda
                tableau_atual = tableau_atual.realizar_iteracao()
                self.tableaus_list.append(copy.deepcopy(tableau_atual))

            z_prime_rhs = tableau_atual.tableau[-1][-1]
            
            if z_prime_rhs != 0: 
                raise ValueError(
                    "Problema inviavel: valor otimo de Z' eh diferente de zero "
                    f"(Z'* = {z_prime_rhs})."
                )

            tableau_atual = tableau_atual.transitar_para_fase_ii(self.ppl.indices_artificiais)
            self.tableaus_list.append(copy.deepcopy(tableau_atual))
            

        self.stage = 2 # não tem mais variaveis artificiais
        while not self.__verificar_otimalidade(tableau_atual):
            tableau_atual = tableau_atual.realizar_iteracao()
            self.tableaus_list.append(copy.deepcopy(tableau_atual))

        self.solucao = self.__extrair_solucao(tableau_atual)
        return self.solucao

    def __verificar_otimalidade(self, tableau_atual: Tableau):
        funcao_objetivo = tableau_atual.tableau[-1][:-1]
        return all(c >= 0 for c in funcao_objetivo) # quando todos contantes forem maior ou igual a 0. (All True)

    def __extrair_solucao(self, tableau_atual: Tableau):
        n_variaveis = self.ppl.n_variaveis
        valores = [0.0] * n_variaveis

        for col, row in tableau_atual.variaveis_basicas:
            if col < n_variaveis:
                valores[col] = float(tableau_atual.tableau[row][-1])

        valor_objetivo = -tableau_atual.tableau[-1][-1]
        if not self.ppl.tipo_problema and self.ppl._fo_invertida:
            valor_objetivo = -valor_objetivo

        return {
            "variaveis": valores,
            "valor_objetivo": valor_objetivo,
            "headers": tableau_atual.headers,
        }
