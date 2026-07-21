

class Tableau:
    """
    Amarzenamento das informações de um tableau no stage determinado do Simplex.
    """
    def __init__(self, 
                 id_stage: int,
                 headers: list[str],
                 matriz_coeficientes: list[list],
                 vetor_b: list,
                 funcao_objetivo: list,
                 funcao_objetivo_artificial: list | None):
        
        # Entradas
        self.id_stage = id_stage
        self.headers = headers # Ordem (x1, x2, ..., xn) + (s1, s2, ..., sm) + (a1, a2, ..., am) + (b)
        
        self.__matriz_coeficientes = matriz_coeficientes
        self.__vetor_b = vetor_b
        
        self.__funcao_objetivo = funcao_objetivo
        self._funcao_objetivo_artificial = funcao_objetivo_artificial
        
        self.variaveis_basicas = self.__identificar_variaveis_basicas(self.__matriz_coeficientes)
        self.tableau = self.__montar_tableau()

        self.coluna_entrada = None
        self.linha_pivo = None
        self.coluna_saida = None
        self.descricao = "Tableau inicial"
        self.operacoes_linha = []
        self.razoes_info = []
        

    def __identificar_coluna_pivo(self):
        """
        Identifica a coluna pivo do tableau.
        Regra de Bland: primeira coluna com coeficiente negativo na linha objetivo.
        Em Fase I, tableau[-1] eh a linha Z'. Em Fase II, tableau[-1] eh a linha Z.
        """
        funcao_objetivo = self.tableau[-1][:-1]
        for j, coef in enumerate(funcao_objetivo):
            if coef < 0:
                return j
        return -1

    def __identificar_linha_pivo(self, coluna_pivo: int):
        """
        Identifica a linha pivo do tableau via teste da razao.
        Bland: em caso de empate, escolhe a linha cuja variavel basica tem o menor indice.
        Se nenhuma linha tem coeficiente > 0 na coluna pivo, o problema eh ilimitado.
        """
        n_restricoes = len(self.__matriz_coeficientes)
        melhor_linha = -1
        melhor_razao = None
        melhor_col_basica = None

        razoes = []
        candidatos = []

        for i in range(n_restricoes):
            coef = self.tableau[i][coluna_pivo]
            if coef > 0:
                razao = self.tableau[i][-1] / coef
                col_basica = next(col for col, row in self.variaveis_basicas if row == i)
                candidatos.append((i, razao, col_basica, coef))
                if (
                    melhor_razao is None
                    or razao < melhor_razao
                    or (razao == melhor_razao and col_basica < melhor_col_basica)
                ):
                    melhor_razao = razao
                    melhor_linha = i
                    melhor_col_basica = col_basica
            elif coef == 0:
                razoes.append(f"L{i}: coef = 0 (ignorada)")
            else:
                razoes.append(f"L{i}: coef < 0 (ignorada)")

        for i, razao, col_basica, coef in candidatos:
            is_melhor = (i == melhor_linha)
            razoes.append(
                f"L{i}: {self.tableau[i][-1]} / {coef} = {razao:.4f}"
                + ("  ← menor" if is_melhor else "")
            )

        if melhor_linha == -1:
            raise ValueError(
                "Problema ilimitado: todos os coeficientes da coluna pivo "
                "sao nao-positivos nas linhas de restricao."
            )

        self.razoes_info = razoes
        return melhor_linha

    def __montar_tableau(self):
        """
        Montar a Matriz Tableau a partir das informacoes da matriz de coeficientes,
        vetor b e funcoes objetivo.
        """
        tableau = []
        
        for i in range(len(self.__matriz_coeficientes)):
            linha_tableau = self.__matriz_coeficientes[i] + [self.__vetor_b[i]] # Concatena a coluna b ao final da linha
            tableau.append(linha_tableau)

        funcao_objetivo_tableau = self.__funcao_objetivo + [0] 
        tableau.append(funcao_objetivo_tableau)

        if self._funcao_objetivo_artificial is not None:
            funcao_objetivo_artificial_tableau = self._funcao_objetivo_artificial + [0]
            tableau.append(funcao_objetivo_artificial_tableau)
            
        if self.id_stage == 1:
            self.__canonicalizar(tableau)
            
        return tableau

    def __canonicalizar(self, tableau: list[list]):
        """
        Coloca o tableau na forma canonica:
        zera os coeficientes das variaveis basicas nas linhas da funcao objetivo (Z e Z').
        """
        
        n_restricoes = len(self.__matriz_coeficientes)
        linha_z = n_restricoes

        for col_j, linha_i in self.variaveis_basicas:
            
            pivot_z = tableau[linha_z][col_j]
            
            if pivot_z != 0:
                for k in range(len(tableau[linha_z])):
                    tableau[linha_z][k] -= pivot_z * tableau[linha_i][k] # Subtrai a linha da funcao objetivo pela linha da variavel basica multiplicada pelo coeficiente da variavel basica na funcao objetivo

            if self._funcao_objetivo_artificial is not None:
                linha_z_prime = n_restricoes + 1
                pivot_z_prime = tableau[linha_z_prime][col_j]
                
                if pivot_z_prime != 0:
                    for k in range(len(tableau[linha_z_prime])):
                        tableau[linha_z_prime][k] -= pivot_z_prime * tableau[linha_i][k] # Mesma logica
                        
    
    def __identificar_variaveis_basicas(self, matriz_coeficientes: list[list]):
        """
        Identificar as variaveis basicas do tableau.
        Quando ha conflito (duas colunas identidade na mesma linha),
        a coluna mais a direita (variavel auxiliar) tem prioridade.
        Retorna lista de tuplas (indice_coluna, indice_linha).
        """
        variaveis_basicas = []

        numero_linhas = len(matriz_coeficientes)
        numero_colunas = len(matriz_coeficientes[0])

        for j in range(numero_colunas):
            coluna_atual = [matriz_coeficientes[i][j] for i in range(numero_linhas)]

            if coluna_atual.count(1) == 1 and coluna_atual.count(0) == numero_linhas - 1:
                linha_pivot = coluna_atual.index(1)
                for idx, (cj, rj) in enumerate(variaveis_basicas):
                    if rj == linha_pivot:
                        variaveis_basicas[idx] = (j, linha_pivot)
                        break
                else:
                    variaveis_basicas.append((j, linha_pivot))

        if len(variaveis_basicas) != numero_linhas:
            raise ValueError(
                f"Numero incorreto de variaveis basicas: "
                f"esperado {numero_linhas}, encontrado {len(variaveis_basicas)}."
            )

        return variaveis_basicas

    def _realizar_pivo(self, coluna_pivo: int, linha_pivo: int):
        elemento_pivo = self.tableau[linha_pivo][coluna_pivo]

        if elemento_pivo == 0:
            raise ValueError("Elemento pivo eh zero, nao eh possivel realizar a iteracao.")
        if elemento_pivo < 0:
            raise ValueError("Elemento pivo eh negativo, nao eh possivel realizar a iteracao.")

        operacoes = []

        if elemento_pivo != 1:
            self.tableau[linha_pivo] = [c / elemento_pivo for c in self.tableau[linha_pivo]]
            operacoes.append(f"L{linha_pivo} ← L{linha_pivo} / {elemento_pivo}")

        for i in range(len(self.tableau)):
            if i != linha_pivo:
                coef = self.tableau[i][coluna_pivo]
                if coef != 0:
                    self.tableau[i] = [
                        c - coef * c_pivo
                        for c, c_pivo in zip(self.tableau[i], self.tableau[linha_pivo])
                    ]
                    sinal = "-" if coef > 0 else "+"
                    op_str = f"L{i} ← L{i} {sinal} {abs(coef)} × L{linha_pivo}"
                    if elemento_pivo != 1:
                        op_str += f"  (L{linha_pivo} já normalizada por / {elemento_pivo})"
                    operacoes.append(op_str)

        coluna_saida = None
        for col, row in self.variaveis_basicas:
            if row == linha_pivo:
                coluna_saida = col
                break

        for i, (col, row) in enumerate(self.variaveis_basicas):
            if row == linha_pivo:
                self.variaveis_basicas[i] = (coluna_pivo, linha_pivo)
                break

        self.coluna_entrada = coluna_pivo
        self.linha_pivo = linha_pivo
        self.coluna_saida = coluna_saida
        self.operacoes_linha = operacoes

    def realizar_iteracao(self):
        coluna_pivo = self.__identificar_coluna_pivo()
        linha_pivo = self.__identificar_linha_pivo(coluna_pivo)
        self._realizar_pivo(coluna_pivo, linha_pivo)
        self.descricao = "Iteracao do Simplex"
        return self

    def transitar_para_fase_ii(self, indices_artificiais: list[int]):
        self.tableau.pop()

        # Expulsa variáveis artificiais residuais da base
        colunas_artificiais = sorted(indices_artificiais, reverse=True)
        for col in colunas_artificiais:
            for c, r in self.variaveis_basicas:
                if c == col:
                    for j in range(len(self.tableau[r]) - 1):
                        if j not in indices_artificiais and self.tableau[r][j] != 0:
                            self._realizar_pivo(coluna_pivo=j, linha_pivo=r)
                            break
                    break

        for col in colunas_artificiais:
            for row in self.tableau:
                row.pop(col)
            self.headers.pop(col)
            self.variaveis_basicas = [
                (c if c < col else c - 1, r)
                for (c, r) in self.variaveis_basicas
            ]

        self._funcao_objetivo_artificial = None
        self.id_stage = 2
        self.coluna_entrada = None
        self.linha_pivo = None
        self.coluna_saida = None
        self.descricao = "Transicao Fase I -> Fase II"

        n_restricoes = len(self.__matriz_coeficientes)

        for col_j, row_i in self.variaveis_basicas:
            pivot_z = self.tableau[n_restricoes][col_j]
            if pivot_z != 0:
                for k in range(len(self.tableau[n_restricoes])):
                    self.tableau[n_restricoes][k] -= pivot_z * self.tableau[row_i][k]

        return self

    def mostrar_tableau(self):
        pass