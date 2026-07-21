from dataclasses import dataclass

class PrintPPL:

    def __init__(self,
                 matriz_coeficientes: list[list],
                 vetor_b: list,
                 vetor_sinais: list,
                 funcao_objetivo: list,
                 eh_minimizacao: bool):

        self.matriz_coeficientes = matriz_coeficientes
        self.vetor_b = vetor_b
        self.vetor_sinais = vetor_sinais
        self.funcao_objetivo = funcao_objetivo
        self.tipo_problema = eh_minimizacao

    def mostrar_modelagem(self):
        pass


class PPL:
    def __init__(self,
                 n_variaveis: int,
                 matriz_coeficientes: list[list],
                 vetor_b: list,
                 vetor_sinais: list,
                 funcao_objetivo: list,
                 eh_minimizacao: bool):

        # Headers da matriz_coeficientes deve ser as varaiveis do problema (x1, x2, x3, ... , xn)
        # Vetor sinais deve ser uma lista de strings com os sinais das restrições (<=, >=, =)
        # Tipo de problema deve ser um booleano, False para maximização e True para minimização

        # Vireficação de consistência dos dados de entrada
        if len(matriz_coeficientes) != len(vetor_b):
            raise ValueError("O número de restrições (linhas da matriz de coeficientes) deve ser igual ao tamanho do vetor b.")

        if len(matriz_coeficientes) != len(vetor_sinais):
            raise ValueError("O número de restrições (linhas da matriz de coeficientes) deve ser igual ao tamanho do vetor de sinais.")

        if len(matriz_coeficientes[0]) != n_variaveis:
            raise ValueError("O número de variáveis (colunas da matriz de coeficientes) deve ser igual ao valor de n_variaveis.")

        if len(funcao_objetivo) != n_variaveis:
            raise ValueError("O tamanho do vetor da função objetivo deve ser igual ao valor de n_variaveis.")

        if not all(sinal in ["<=", ">=", "="] for sinal in vetor_sinais):
            raise ValueError("Todos os sinais das restrições devem ser '<=', '>=', ou '='.")

        self.n_variaveis = n_variaveis
        self.tipo_problema = eh_minimizacao # Se for false precisa ser trasformada para forma padrão como minimização 

        self.matriz_coeficientes = matriz_coeficientes
        self.vetor_sinais = vetor_sinais
        self.vetor_b = vetor_b

        self.funcao_objetivo = funcao_objetivo
        self.funcao_objetivo_artificial = None

        self.headers = [f"x{i+1}" for i in range(n_variaveis)]

        # Variaveis de Identificação do Problema
        self.eh_DuasEtapas = False
        self.EstaBase = False
        self._fo_invertida = False

        self.PPLno_forma_base = PrintPPL(
            self.matriz_coeficientes, self.vetor_b, self.vetor_sinais,
            self.funcao_objetivo, self.tipo_problema
        )

        self.__converter_para_forma_base()

        self.PPLforma_base = PrintPPL(
            self.matriz_coeficientes, self.vetor_b, self.vetor_sinais,
            self.funcao_objetivo, self.tipo_problema
        )

    def PrintarPoblema(self, base: bool = False):
        if base:
            return self.PPLforma_base
        else:
            return self.PPLno_forma_base

    def __converter_para_forma_base(self):
        if self.EstaBase:
            raise ValueError("O problema já está na forma base.")

        if not self.tipo_problema:
            self.funcao_objetivo = [-c for c in self.funcao_objetivo] # Inverter os coeficientes da função objetivo 
            self._fo_invertida = True

        n_restricoes = len(self.matriz_coeficientes)
        n_cols = len(self.matriz_coeficientes[0])

        for i in range(n_restricoes):
            
            # Se caso o b[i] for negativo, multiplica a linha inteira por -1 e inverte o sinal da restrição
            if self.vetor_b[i] < 0:
                self.matriz_coeficientes[i] = [-c for c in self.matriz_coeficientes[i]]
                self.vetor_b[i] = -self.vetor_b[i]

                sinal = self.vetor_sinais[i]
                if sinal == "<=":
                    self.vetor_sinais[i] = ">="
                elif sinal == ">=":
                    self.vetor_sinais[i] = "<="

        self.indices_folga = []
        self.indices_excesso = []
        self.indices_artificiais = []

        # Extração de variáveis de folga, excesso e artificiais, e atualização da matriz de coeficientes e função objetivo
        for i, sinal in enumerate(self.vetor_sinais):

            if sinal == "<=": # Vai adicionar s_i
                self.indices_folga.append(n_cols)
                for j in range(n_restricoes):
                    self.matriz_coeficientes[j].append(1 if j == i else 0)

                self.headers.append(f"s{len(self.indices_folga)}")
                n_cols += 1

            elif sinal == ">=": # Vai adicionar -s_i e a_i
                self.eh_DuasEtapas = True
                self.indices_excesso.append(n_cols)
                for j in range(n_restricoes):
                    self.matriz_coeficientes[j].append(-1 if j == i else 0)

                self.headers.append(f"e{len(self.indices_excesso)}")
                n_cols += 1

                self.indices_artificiais.append(n_cols)
                for j in range(n_restricoes):
                    self.matriz_coeficientes[j].append(1 if j == i else 0)
                self.headers.append(f"a{len(self.indices_artificiais)}")
                n_cols += 1

            elif sinal == "=": # Vai adicionar a_i
                self.eh_DuasEtapas = True
                self.indices_artificiais.append(n_cols)
                for j in range(n_restricoes):
                    self.matriz_coeficientes[j].append(1 if j == i else 0)

                self.headers.append(f"a{len(self.indices_artificiais)}")
                n_cols += 1

            self.vetor_sinais[i] = "="

        self.funcao_objetivo.extend([0] * (n_cols - len(self.funcao_objetivo)))

        # Quando o problema é de duas etapas, cria-se a função objetivo artificial
        if self.eh_DuasEtapas:
            self.funcao_objetivo_artificial = [0] * len(self.funcao_objetivo)
            for idx in self.indices_artificiais:
                self.funcao_objetivo_artificial[idx] = 1 # Cria z' = a1 + a2 + ... + am, onde ai são as variáveis artificiais

        self.EstaBase = True
