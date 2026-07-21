import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PPL import PPL, PrintPPL


class TestPrintPPL(unittest.TestCase):

    def test_construtor_armazena_atributos_corretamente(self):
        matriz = [[1, 2], [3, 4]]
        b = [5, 6]
        sinais = ["<=", ">="]
        fo = [7, 8]
        eh_min = True

        p = PrintPPL(matriz, b, sinais, fo, eh_min)

        self.assertIs(p.matriz_coeficientes, matriz)
        self.assertIs(p.vetor_b, b)
        self.assertIs(p.vetor_sinais, sinais)
        self.assertIs(p.funcao_objetivo, fo)
        self.assertEqual(p.tipo_problema, eh_min)

    def test_construtor_problema_maximizacao(self):
        p = PrintPPL([[1]], [2], ["<="], [3], False)
        self.assertFalse(p.tipo_problema)

    def test_mostrar_modelagem_nao_levanta_excecao(self):
        p = PrintPPL([[1]], [2], ["<="], [3], True)
        try:
            p.mostrar_modelagem()
        except Exception as e:
            self.fail(f"mostrar_modelagem() levantou {e}")


class TestPPLValidacaoEntrada(unittest.TestCase):

    def test_matriz_b_tamanhos_incompativeis_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            PPL(
                n_variaveis=2,
                matriz_coeficientes=[[1, 2], [3, 4]],
                vetor_b=[5],
                vetor_sinais=["<=", "<="],
                funcao_objetivo=[1, 1],
                eh_minimizacao=True,
            )

    def test_matriz_sinais_tamanhos_incompativeis_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            PPL(
                n_variaveis=2,
                matriz_coeficientes=[[1, 2], [3, 4]],
                vetor_b=[5, 6],
                vetor_sinais=["<="],
                funcao_objetivo=[1, 1],
                eh_minimizacao=True,
            )

    def test_colunas_diferentes_de_n_variaveis_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            PPL(
                n_variaveis=2,
                matriz_coeficientes=[[1, 2, 3]],
                vetor_b=[5],
                vetor_sinais=["<="],
                funcao_objetivo=[1, 1],
                eh_minimizacao=True,
            )

    def test_funcao_objetivo_tamanho_incompativel_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            PPL(
                n_variaveis=2,
                matriz_coeficientes=[[1, 2]],
                vetor_b=[5],
                vetor_sinais=["<="],
                funcao_objetivo=[1],
                eh_minimizacao=True,
            )

    def test_sinal_invalido_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            PPL(
                n_variaveis=2,
                matriz_coeficientes=[[1, 2]],
                vetor_b=[5],
                vetor_sinais=["!="],
                funcao_objetivo=[1, 1],
                eh_minimizacao=True,
            )

    def test_entrada_valida_nao_levanta_excecao(self):
        try:
            PPL(
                n_variaveis=2,
                matriz_coeficientes=[[1, 2], [3, 4]],
                vetor_b=[5, 6],
                vetor_sinais=["<=", "<="],
                funcao_objetivo=[1, 1],
                eh_minimizacao=True,
            )
        except Exception as e:
            self.fail(f"PPL valido levantou {e}")


class TestPPLMinimizacao(unittest.TestCase):

    def setUp(self):
        self.ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[[1, 2], [3, 4]],
            vetor_b=[5, 6],
            vetor_sinais=["<=", "<="],
            funcao_objetivo=[7, 8],
            eh_minimizacao=True,
        )

    def test_tipo_problema_preservado(self):
        self.assertTrue(self.ppl.tipo_problema)

    def test_fo_nao_invertida(self):
        self.assertFalse(self.ppl._fo_invertida)

    def test_funcao_objetivo_inalterada_apos_conversao(self):
        self.assertEqual(self.ppl.funcao_objetivo[0], 7)
        self.assertEqual(self.ppl.funcao_objetivo[1], 8)

    def test_PPLno_forma_base_preserva_tipo(self):
        p = self.ppl.PPLno_forma_base
        self.assertTrue(p.tipo_problema)

    def test_PPLforma_base_preserva_tipo(self):
        p = self.ppl.PPLforma_base
        self.assertTrue(p.tipo_problema)


class TestPPLMaximizacao(unittest.TestCase):

    def setUp(self):
        self.ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[[1, 2], [3, 4]],
            vetor_b=[5, 6],
            vetor_sinais=["<=", "<="],
            funcao_objetivo=[7, 8],
            eh_minimizacao=False,
        )

    def test_fo_invertida_para_minimizacao(self):
        self.assertTrue(self.ppl._fo_invertida)

    def test_funcao_objetivo_negada(self):
        self.assertEqual(self.ppl.funcao_objetivo[0], -7)
        self.assertEqual(self.ppl.funcao_objetivo[1], -8)

    def test_PPLno_forma_base_preserva_tipo_original(self):
        p = self.ppl.PPLno_forma_base
        self.assertFalse(p.tipo_problema)

    def test_PPLforma_base_reflete_tipo_original(self):
        p = self.ppl.PPLforma_base
        self.assertFalse(p.tipo_problema)


class TestPPLRestricaoMenorIgual(unittest.TestCase):

    def setUp(self):
        self.ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[[2, 3]],
            vetor_b=[10],
            vetor_sinais=["<="],
            funcao_objetivo=[5, 4],
            eh_minimizacao=True,
        )

    def test_nao_exige_duas_etapas(self):
        self.assertFalse(self.ppl.eh_DuasEtapas)

    def test_adiciona_uma_variavel_folga(self):
        self.assertEqual(len(self.ppl.indices_folga), 1)

    def test_sem_variaveis_excesso(self):
        self.assertEqual(len(self.ppl.indices_excesso), 0)

    def test_sem_variaveis_artificiais(self):
        self.assertEqual(len(self.ppl.indices_artificiais), 0)

    def test_sinal_convertido_para_igual(self):
        self.assertEqual(self.ppl.vetor_sinais[0], "=")

    def test_coluna_folga_adicionada_corretamente(self):
        col_original = 2
        self.assertEqual(self.ppl.matriz_coeficientes[0][col_original], 1)

    def test_headers_inclui_folga(self):
        self.assertIn("s1", self.ppl.headers)

    def test_funcao_objetivo_estendida_com_zero(self):
        self.assertEqual(len(self.ppl.funcao_objetivo), 3)
        self.assertEqual(self.ppl.funcao_objetivo[2], 0)

    def test_numero_colunas_aumentou_em_um(self):
        self.assertEqual(len(self.ppl.matriz_coeficientes[0]), 3)

    def test_funcao_objetivo_artificial_nao_existe_para_uma_fase(self):
        self.assertIsNone(self.ppl.funcao_objetivo_artificial)


class TestPPLRestricaoMaiorIgual(unittest.TestCase):

    def setUp(self):
        self.ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[[2, 3]],
            vetor_b=[10],
            vetor_sinais=[">="],
            funcao_objetivo=[5, 4],
            eh_minimizacao=True,
        )

    def test_exige_duas_etapas(self):
        self.assertTrue(self.ppl.eh_DuasEtapas)

    def test_sem_variaveis_folga(self):
        self.assertEqual(len(self.ppl.indices_folga), 0)

    def test_adiciona_uma_variavel_excesso(self):
        self.assertEqual(len(self.ppl.indices_excesso), 1)

    def test_adiciona_uma_variavel_artificial(self):
        self.assertEqual(len(self.ppl.indices_artificiais), 1)

    def test_sinal_convertido_para_igual(self):
        self.assertEqual(self.ppl.vetor_sinais[0], "=")

    def test_coluna_excesso_tem_coeficiente_negativo(self):
        col_excesso = self.ppl.indices_excesso[0]
        self.assertEqual(self.ppl.matriz_coeficientes[0][col_excesso], -1)

    def test_coluna_artificial_tem_coeficiente_positivo(self):
        col_artificial = self.ppl.indices_artificiais[0]
        self.assertEqual(self.ppl.matriz_coeficientes[0][col_artificial], 1)

    def test_headers_inclui_excesso_e_artificial(self):
        self.assertIn("e1", self.ppl.headers)
        self.assertIn("a1", self.ppl.headers)

    def test_funcao_objetivo_estendida_com_zeros(self):
        self.assertEqual(len(self.ppl.funcao_objetivo), 4)
        self.assertEqual(self.ppl.funcao_objetivo[2], 0)
        self.assertEqual(self.ppl.funcao_objetivo[3], 0)

    def test_numero_colunas_aumentou_em_dois(self):
        self.assertEqual(len(self.ppl.matriz_coeficientes[0]), 4)

    def test_funcao_objetivo_artificial_tem_1_na_posicao_artificial(self):
        self.assertEqual(len(self.ppl.funcao_objetivo_artificial), 4)
        self.assertEqual(self.ppl.funcao_objetivo_artificial[0], 0)
        self.assertEqual(self.ppl.funcao_objetivo_artificial[1], 0)
        col_excesso = self.ppl.indices_excesso[0]
        col_artificial = self.ppl.indices_artificiais[0]
        self.assertEqual(self.ppl.funcao_objetivo_artificial[col_excesso], 0)
        self.assertEqual(self.ppl.funcao_objetivo_artificial[col_artificial], 1)


class TestPPLRestricaoIgual(unittest.TestCase):

    def setUp(self):
        self.ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[[2, 3]],
            vetor_b=[10],
            vetor_sinais=["="],
            funcao_objetivo=[5, 4],
            eh_minimizacao=True,
        )

    def test_exige_duas_etapas(self):
        self.assertTrue(self.ppl.eh_DuasEtapas)

    def test_sem_variaveis_folga(self):
        self.assertEqual(len(self.ppl.indices_folga), 0)

    def test_sem_variaveis_excesso(self):
        self.assertEqual(len(self.ppl.indices_excesso), 0)

    def test_adiciona_uma_variavel_artificial(self):
        self.assertEqual(len(self.ppl.indices_artificiais), 1)

    def test_sinal_permanece_igual(self):
        self.assertEqual(self.ppl.vetor_sinais[0], "=")

    def test_coluna_artificial_tem_coeficiente_positivo(self):
        col_artificial = self.ppl.indices_artificiais[0]
        self.assertEqual(self.ppl.matriz_coeficientes[0][col_artificial], 1)

    def test_headers_inclui_apenas_artificial(self):
        self.assertIn("a1", self.ppl.headers)
        self.assertNotIn("e1", self.ppl.headers)
        self.assertNotIn("s1", self.ppl.headers)

    def test_numero_colunas_aumentou_em_um(self):
        self.assertEqual(len(self.ppl.matriz_coeficientes[0]), 3)

    def test_funcao_objetivo_artificial_tem_1_na_posicao_artificial(self):
        self.assertEqual(len(self.ppl.funcao_objetivo_artificial), 3)
        self.assertEqual(self.ppl.funcao_objetivo_artificial[0], 0)
        self.assertEqual(self.ppl.funcao_objetivo_artificial[1], 0)
        col_artificial = self.ppl.indices_artificiais[0]
        self.assertEqual(self.ppl.funcao_objetivo_artificial[col_artificial], 1)


class TestPPLRestricaoLadoDireitoNegativo(unittest.TestCase):

    def setUp(self):
        self.ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[[2, 3]],
            vetor_b=[-10],
            vetor_sinais=["<="],
            funcao_objetivo=[5, 4],
            eh_minimizacao=True,
        )

    def test_vetor_b_nao_negativo_apos_normalizacao(self):
        self.assertGreaterEqual(self.ppl.vetor_b[0], 0)

    def test_coeficientes_negados_apos_normalizacao(self):
        self.assertEqual(self.ppl.matriz_coeficientes[0][0], -2)
        self.assertEqual(self.ppl.matriz_coeficientes[0][1], -3)


class TestPPLRestricaoMaiorIgualComLadoDireitoNegativo(unittest.TestCase):

    def setUp(self):
        self.ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[[2, 3]],
            vetor_b=[-10],
            vetor_sinais=[">="],
            funcao_objetivo=[5, 4],
            eh_minimizacao=True,
        )

    def test_sinal_invertido_para_menor_igual_e_depois_convertido(self):
        self.assertEqual(self.ppl.vetor_sinais[0], "=")

    def test_adiciona_folga_nao_excesso_nem_artificial(self):
        self.assertEqual(len(self.ppl.indices_folga), 1)
        self.assertEqual(len(self.ppl.indices_excesso), 0)
        self.assertEqual(len(self.ppl.indices_artificiais), 0)


class TestPPLMultiplasRestricoes(unittest.TestCase):

    def setUp(self):
        self.ppl = PPL(
            n_variaveis=3,
            matriz_coeficientes=[
                [1, 2, 1],
                [2, 0, 1],
                [1, 2, 3],
            ],
            vetor_b=[4, 3, 8],
            vetor_sinais=["<=", ">=", "="],
            funcao_objetivo=[2, 3, 1],
            eh_minimizacao=False,
        )

    def test_exige_duas_etapas(self):
        self.assertTrue(self.ppl.eh_DuasEtapas)

    def test_folgas_apenas_na_primeira_restricao(self):
        self.assertEqual(len(self.ppl.indices_folga), 1)

    def test_excesso_apenas_na_segunda_restricao(self):
        self.assertEqual(len(self.ppl.indices_excesso), 1)

    def test_artificiais_na_segunda_e_terceira_restricao(self):
        self.assertEqual(len(self.ppl.indices_artificiais), 2)

    def test_todos_sinais_convertidos_para_igual(self):
        self.assertEqual(self.ppl.vetor_sinais, ["=", "=", "="])

    def test_funcao_objetivo_invertida_para_minimizacao(self):
        self.assertEqual(self.ppl.funcao_objetivo[0], -2)
        self.assertEqual(self.ppl.funcao_objetivo[1], -3)
        self.assertEqual(self.ppl.funcao_objetivo[2], -1)

    def test_funcao_objetivo_estendida_com_zeros_para_auxiliares(self):
        expected_len = 3 + 1 + 1 + 2
        self.assertEqual(len(self.ppl.funcao_objetivo), expected_len)
        for i in range(3, expected_len):
            self.assertEqual(self.ppl.funcao_objetivo[i], 0)

    def test_headers_inclui_auxiliares_nomeados_corretamente(self):
        self.assertIn("s1", self.ppl.headers)
        self.assertIn("e1", self.ppl.headers)
        self.assertIn("a1", self.ppl.headers)
        self.assertIn("a2", self.ppl.headers)

    def test_matriz_coeficientes_coluna_folga(self):
        col_s1 = self.ppl.indices_folga[0]
        self.assertEqual(self.ppl.matriz_coeficientes[0][col_s1], 1)
        self.assertEqual(self.ppl.matriz_coeficientes[1][col_s1], 0)
        self.assertEqual(self.ppl.matriz_coeficientes[2][col_s1], 0)

    def test_matriz_coeficientes_coluna_excesso(self):
        col_e1 = self.ppl.indices_excesso[0]
        self.assertEqual(self.ppl.matriz_coeficientes[0][col_e1], 0)
        self.assertEqual(self.ppl.matriz_coeficientes[1][col_e1], -1)
        self.assertEqual(self.ppl.matriz_coeficientes[2][col_e1], 0)

    def test_matriz_coeficientes_coluna_artificial_1(self):
        col_a1 = self.ppl.indices_artificiais[0]
        self.assertEqual(self.ppl.matriz_coeficientes[0][col_a1], 0)
        self.assertEqual(self.ppl.matriz_coeficientes[1][col_a1], 1)
        self.assertEqual(self.ppl.matriz_coeficientes[2][col_a1], 0)

    def test_matriz_coeficientes_coluna_artificial_2(self):
        col_a2 = self.ppl.indices_artificiais[1]
        self.assertEqual(self.ppl.matriz_coeficientes[0][col_a2], 0)
        self.assertEqual(self.ppl.matriz_coeficientes[1][col_a2], 0)
        self.assertEqual(self.ppl.matriz_coeficientes[2][col_a2], 1)

    def test_funcao_objetivo_artificial_nas_posicoes_corretas(self):
        n_cols = len(self.ppl.funcao_objetivo_artificial)
        self.assertEqual(n_cols, 7)
        for i in range(n_cols):
            if i in self.ppl.indices_artificiais:
                self.assertEqual(self.ppl.funcao_objetivo_artificial[i], 1,
                                 f"Posição {i} (artificial) deveria ser 1")
            else:
                self.assertEqual(self.ppl.funcao_objetivo_artificial[i], 0,
                                 f"Posição {i} deveria ser 0")


class TestPPLPrintarPoblema(unittest.TestCase):

    def setUp(self):
        self.ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[[1, 2], [3, 4]],
            vetor_b=[5, 6],
            vetor_sinais=["<=", ">="],
            funcao_objetivo=[7, 8],
            eh_minimizacao=False,
        )

    def test_printar_forma_original_retorna_PPLno_forma_base(self):
        resultado = self.ppl.PrintarPoblema(base=False)
        self.assertIs(resultado, self.ppl.PPLno_forma_base)

    def test_printar_forma_base_retorna_PPLforma_base(self):
        resultado = self.ppl.PrintarPoblema(base=True)
        self.assertIs(resultado, self.ppl.PPLforma_base)

    def test_forma_original_compartilha_referencias_com_ppl(self):
        original = self.ppl.PrintarPoblema(base=False)
        self.assertEqual(len(original.matriz_coeficientes[0]), 5)
        self.assertEqual(len(self.ppl.matriz_coeficientes[0]), 5)

    def test_forma_base_reflete_conversao(self):
        base = self.ppl.PrintarPoblema(base=True)
        self.assertEqual(base.vetor_sinais, ["=", "="])
        self.assertFalse(base.tipo_problema)


class TestPPLExemploCompletoSalaDeAula(unittest.TestCase):

    def test_problema_minimizacao_com_todas_restricoes(self):
        ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[
                [1, 1],
                [2, 1],
                [0, 1],
            ],
            vetor_b=[4, 6, 2],
            vetor_sinais=["<=", ">=", "="],
            funcao_objetivo=[3, 2],
            eh_minimizacao=True,
        )

        self.assertTrue(ppl.eh_DuasEtapas)
        self.assertEqual(len(ppl.indices_folga), 1)
        self.assertEqual(len(ppl.indices_excesso), 1)
        self.assertEqual(len(ppl.indices_artificiais), 2)
        self.assertEqual(len(ppl.headers), 2 + 1 + 1 + 2)
        self.assertEqual(ppl. headers[0], "x1")
        self.assertEqual(ppl.headers[1], "x2")
        self.assertEqual(ppl.vetor_sinais, ["=", "=", "="])
        self.assertFalse(ppl._fo_invertida)
        self.assertEqual(ppl.funcao_objetivo[:2], [3, 2])

    def test_problema_maximizacao_simples_uma_fase(self):
        ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[
                [1, 0],
                [0, 2],
                [3, 2],
            ],
            vetor_b=[4, 12, 18],
            vetor_sinais=["<=", "<=", "<="],
            funcao_objetivo=[3, 5],
            eh_minimizacao=False,
        )

        self.assertFalse(ppl.eh_DuasEtapas)
        self.assertEqual(len(ppl.indices_folga), 3)
        self.assertEqual(len(ppl.indices_excesso), 0)
        self.assertEqual(len(ppl.indices_artificiais), 0)
        self.assertEqual(ppl.funcao_objetivo[:2], [-3, -5])

    def test_problema_vms_sla_do_pdf(self):
        """Problema do PDF: Min Z=3x+2y s.a. x+y>=4, 2x+y<=6"""
        ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[
                [1, 1],
                [2, 1],
            ],
            vetor_b=[4, 6],
            vetor_sinais=[">=", "<="],
            funcao_objetivo=[3, 2],
            eh_minimizacao=True,
        )

        self.assertTrue(ppl.eh_DuasEtapas)
        self.assertFalse(ppl._fo_invertida)
        self.assertEqual(ppl.n_variaveis, 2)

        self.assertEqual(len(ppl.indices_folga), 1)
        self.assertEqual(len(ppl.indices_excesso), 1)
        self.assertEqual(len(ppl.indices_artificiais), 1)

        self.assertEqual(ppl.vetor_sinais, ["=", "="])

        self.assertEqual(ppl.funcao_objetivo[0], 3)
        self.assertEqual(ppl.funcao_objetivo[1], 2)
        self.assertEqual(len(ppl.funcao_objetivo), 5)
        self.assertEqual(ppl.funcao_objetivo, [3, 2, 0, 0, 0])

        col_a1 = ppl.indices_artificiais[0]
        col_s1 = ppl.indices_folga[0]
        col_e1 = ppl.indices_excesso[0]

        self.assertEqual(ppl.funcao_objetivo_artificial[col_a1], 1)
        self.assertEqual(ppl.funcao_objetivo_artificial[col_s1], 0)
        self.assertEqual(ppl.funcao_objetivo_artificial[col_e1], 0)
        self.assertEqual(sum(ppl.funcao_objetivo_artificial), 1)

        self.assertEqual(len(ppl.matriz_coeficientes), 2)
        self.assertEqual(len(ppl.matriz_coeficientes[0]), 5)
        self.assertEqual(len(ppl.matriz_coeficientes[1]), 5)

        self.assertEqual(ppl.matriz_coeficientes[0][col_e1], -1)
        self.assertEqual(ppl.matriz_coeficientes[0][col_a1], 1)
        self.assertEqual(ppl.matriz_coeficientes[0][col_s1], 0)

        self.assertEqual(ppl.matriz_coeficientes[1][col_e1], 0)
        self.assertEqual(ppl.matriz_coeficientes[1][col_a1], 0)
        self.assertEqual(ppl.matriz_coeficientes[1][col_s1], 1)

        self.assertEqual(ppl.headers[0], "x1")
        self.assertEqual(ppl.headers[1], "x2")
        self.assertIn("e1", ppl.headers)
        self.assertIn("a1", ppl.headers)
        self.assertIn("s1", ppl.headers)

    def test_problema_vms_sla_mostrar_modelagem(self):
        """PrintPPL deve expor a modelagem sem excecao"""
        ppl = PPL(
            n_variaveis=2,
            matriz_coeficientes=[[1, 1], [2, 1]],
            vetor_b=[4, 6],
            vetor_sinais=[">=", "<="],
            funcao_objetivo=[3, 2],
            eh_minimizacao=True,
        )

        original = ppl.PrintarPoblema(base=False)
        self.assertEqual(original.vetor_b, [4, 6])
        self.assertEqual(original.vetor_sinais, ["=", "="])

        base = ppl.PrintarPoblema(base=True)
        self.assertEqual(base.vetor_sinais, ["=", "="])
        self.assertEqual(base.funcao_objetivo, [3, 2, 0, 0, 0])

        try:
            original.mostrar_modelagem()
            base.mostrar_modelagem()
        except Exception as e:
            self.fail(f"mostrar_modelagem() levantou {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
