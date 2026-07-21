import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Tableau import Tableau


class TestIdentificarVariaveisBasicas(unittest.TestCase):

    @classmethod
    def _invoke(cls, matriz_coeficientes):
        return Tableau._Tableau__identificar_variaveis_basicas(None, matriz_coeficientes)

    def test_caso_canonico_padrao(self):
        resultado = self._invoke([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ])
        self.assertEqual(resultado, [(0, 0), (1, 1), (2, 2)])

    def test_caso_canonico_ordem_embaralhada(self):
        resultado = self._invoke([
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, 1],
        ])
        self.assertEqual(resultado, [(0, 1), (1, 0), (2, 2)])

    def test_coluna_toda_zero_nao_eh_basica(self):
        resultado = self._invoke([
            [1, 0, 0],
            [0, 0, 1],
        ])
        self.assertEqual(resultado, [(0, 0), (2, 1)])

    def test_coluna_com_menos_um_nao_eh_basica(self):
        resultado = self._invoke([
            [-1, 1, 0],
            [0, 0, 1],
        ])
        self.assertEqual(resultado, [(1, 0), (2, 1)])

    def test_coluna_com_valor_dois_nao_eh_basica(self):
        resultado = self._invoke([
            [2, 0, 1],
            [1, 1, 0],
        ])
        self.assertEqual(resultado, [(1, 1), (2, 0)])

    def test_problema_vms_sla_do_pdf(self):
        resultado = self._invoke([
            [1, 1, -1, 1, 0],
            [2, 1, 0, 0, 1],
        ])
        self.assertEqual(len(resultado), 2)
        self.assertIn((3, 0), resultado)
        self.assertIn((4, 1), resultado)

    def test_nenhuma_variavel_basica_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            self._invoke([
                [1, 2],
                [3, 4],
            ])

    def test_poucas_variaveis_basicas_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            self._invoke([
                [1, 0, 0],
                [0, 0, 0],
                [0, 0, 1],
            ])

    def test_conflito_mesma_linha_resolvido_pela_coluna_direita(self):
        resultado = self._invoke([
            [1, 0, 1],
            [0, 1, 0],
        ])
        self.assertEqual(resultado, [(2, 0), (1, 1)])

    def test_unica_linha_uma_basica(self):
        resultado = self._invoke([
            [1, 0],
        ])
        self.assertEqual(resultado, [(0, 0)])

    def test_unica_linha_nenhuma_basica_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            self._invoke([
                [2, 3],
            ])


class TestTableauConstrutor(unittest.TestCase):

    def test_construtor_com_matriz_valida(self):
        try:
            Tableau(
                id_stage=1,
                headers=["x1", "x2", "s1", "s2"],
                matriz_coeficientes=[
                    [1, 2, 1, 0],
                    [3, 4, 0, 1],
                ],
                vetor_b=[5, 6],
                funcao_objetivo=[7, 8, 0, 0],
                funcao_objetivo_artificial=None,
            )
        except Exception as e:
            self.fail(f"Tableau valido levantou {e}")

    def test_construtor_sem_basicas_suficientes_levanta_valueerror(self):
        with self.assertRaises(ValueError):
            Tableau(
                id_stage=1,
                headers=["x1", "x2", "s1", "s2"],
                matriz_coeficientes=[
                    [1, 2, 0, 0],
                    [3, 4, 0, 0],
                ],
                vetor_b=[5, 6],
                funcao_objetivo=[7, 8, 0, 0],
                funcao_objetivo_artificial=None,
            )

    def test_construtor_com_colunas_conflitantes_resolve_pela_direita(self):
        try:
            Tableau(
                id_stage=1,
                headers=["x1", "x2", "s1", "s2"],
                matriz_coeficientes=[
                    [1, 0, 1, 0],
                    [0, 1, 0, 1],
                ],
                vetor_b=[5, 6],
                funcao_objetivo=[7, 8, 0, 0],
                funcao_objetivo_artificial=None,
            )
        except Exception as e:
            self.fail(f"Conflito deveria ser resolvido, mas levantou {e}")

    def test_construtor_problema_vms_sla_pdf(self):
        try:
            Tableau(
                id_stage=1,
                headers=["x1", "x2", "e1", "a1", "s1"],
                matriz_coeficientes=[
                    [1, 1, -1, 1, 0],
                    [2, 1, 0, 0, 1],
                ],
                vetor_b=[4, 6],
                funcao_objetivo=[3, 2, 0, 0, 0],
                funcao_objetivo_artificial=[0, 0, 0, 1, 0],
            )
        except Exception as e:
            self.fail(f"Tableau do problema VMs/SLA levantou {e}")


class TestCanonicalizar(unittest.TestCase):

    def test_problema_vms_sla_tableau_canonico(self):
        t = Tableau(
            id_stage=1,
            headers=["x1", "x2", "e1", "a1", "s1"],
            matriz_coeficientes=[
                [1, 1, -1, 1, 0],
                [2, 1, 0, 0, 1],
            ],
            vetor_b=[4, 6],
            funcao_objetivo=[3, 2, 0, 0, 0],
            funcao_objetivo_artificial=[0, 0, 0, 1, 0],
        )

        self.assertEqual(len(t.tableau), 4)

        self.assertEqual(t.tableau[0], [1, 1, -1, 1, 0, 4])
        self.assertEqual(t.tableau[1], [2, 1, 0, 0, 1, 6])

        self.assertEqual(t.tableau[2], [3, 2, 0, 0, 0, 0])

        self.assertEqual(t.tableau[3], [-1, -1, 1, 0, 0, -4])

    def test_variaveis_basicas_tem_coeficiente_zero_na_linha_z(self):
        t = Tableau(
            id_stage=1,
            headers=["x1", "x2", "e1", "a1", "s1"],
            matriz_coeficientes=[
                [1, 1, -1, 1, 0],
                [2, 1, 0, 0, 1],
            ],
            vetor_b=[4, 6],
            funcao_objetivo=[3, 2, 0, 0, 0],
            funcao_objetivo_artificial=[0, 0, 0, 1, 0],
        )

        linha_z = len(t.tableau) - 2
        linha_z_prime = len(t.tableau) - 1

        for col, _ in t.variaveis_basicas:
            self.assertEqual(t.tableau[linha_z][col], 0,
                             f"Coeficiente na linha Z, col {col} deveria ser 0")
            self.assertEqual(t.tableau[linha_z_prime][col], 0,
                             f"Coeficiente na linha Z', col {col} deveria ser 0")

    def test_sem_z_prime_z_row_ainda_canonica(self):
        t = Tableau(
            id_stage=1,
            headers=["x1", "x2", "s1", "s2"],
            matriz_coeficientes=[
                [1, 2, 1, 0],
                [3, 4, 0, 1],
            ],
            vetor_b=[5, 6],
            funcao_objetivo=[7, 8, 2, 0],
            funcao_objetivo_artificial=None,
        )

        linha_z = len(t.tableau) - 1

        self.assertEqual(t.tableau[0], [1, 2, 1, 0, 5])
        self.assertEqual(t.tableau[1], [3, 4, 0, 1, 6])

        for col, _ in t.variaveis_basicas:
            self.assertEqual(t.tableau[linha_z][col], 0,
                             f"Coeficiente na linha Z, col {col} deveria ser 0")

    def test_varias_iteracoes_nao_altera_tableau_canonico(self):
        t = Tableau(
            id_stage=1,
            headers=["x1", "x2", "e1", "a1", "s1"],
            matriz_coeficientes=[
                [1, 1, -1, 1, 0],
                [2, 1, 0, 0, 1],
            ],
            vetor_b=[4, 6],
            funcao_objetivo=[3, 2, 0, 0, 0],
            funcao_objetivo_artificial=[0, 0, 0, 1, 0],
        )

        primeira_chamada = [row[:] for row in t.tableau]
        t._Tableau__canonicalizar(t.tableau)
        segunda_chamada = [row[:] for row in t.tableau]

        self.assertEqual(primeira_chamada, segunda_chamada)

    def test_varias_basicas_com_coeficiente_nao_zero_em_z(self):
        t = Tableau(
            id_stage=1,
            headers=["x1", "x2", "x3", "s1", "s2"],
            matriz_coeficientes=[
                [1, 2, 0, 1, 0],
                [3, 1, 0, 0, 1],
            ],
            vetor_b=[10, 20],
            funcao_objetivo=[5, 3, 7, 2, 3],
            funcao_objetivo_artificial=None,
        )

        self.assertEqual(t.tableau[0], [1, 2, 0, 1, 0, 10])
        self.assertEqual(t.tableau[1], [3, 1, 0, 0, 1, 20])

        linha_z = len(t.tableau) - 1

        self.assertEqual(t.tableau[linha_z][0], -6)
        self.assertEqual(t.tableau[linha_z][1], -4)
        self.assertEqual(t.tableau[linha_z][2], 7)
        self.assertEqual(t.tableau[linha_z][3], 0)
        self.assertEqual(t.tableau[linha_z][4], 0)
        self.assertEqual(t.tableau[linha_z][5], -80)


if __name__ == "__main__":
    unittest.main(verbosity=2)
