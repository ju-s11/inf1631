import unittest
from euler import (euleriano, circuito_euler, valida_circuito, conexo,
                   graus, gerar_grafo, arestas)
import random


def grafo_de(n, lista):
    G = {v: set() for v in range(1, n + 1)}
    for u, v in lista:
        G[u].add(v)
        G[v].add(u)
    return G


class TestesObrigatorios(unittest.TestCase):
    def test_ciclo_c4(self):
        G = grafo_de(4, [(1, 2), (2, 3), (3, 4), (4, 1)])
        self.assertTrue(euleriano(G))
        C = circuito_euler(G)
        self.assertTrue(valida_circuito(G, C))
        self.assertEqual(len(C), 5)

    def test_caminho_p4(self):
        G = grafo_de(4, [(1, 2), (2, 3), (3, 4)])
        self.assertTrue(conexo(G))
        self.assertFalse(euleriano(G))
        self.assertIsNone(circuito_euler(G))

    def test_desconexo_dois_ciclos(self):
        G = grafo_de(6, [(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4)])
        self.assertFalse(conexo(G))
        self.assertFalse(euleriano(G))

    def test_grafo_vazio(self):
        G = grafo_de(10, [])
        self.assertTrue(conexo(G))        # vacuamente verdadeiro
        self.assertFalse(euleriano(G))    # tratado explicitamente
        self.assertIsNone(circuito_euler(G))


class TestesExtras(unittest.TestCase):
    def test_validador_rejeita_circuitos_invalidos(self):
        G = grafo_de(4, [(1, 2), (2, 3), (3, 4), (4, 1)])
        self.assertFalse(valida_circuito(G, [1, 2, 3, 4]))        # nao fecha
        self.assertFalse(valida_circuito(G, [1, 2, 3, 1]))        # aresta inexistente
        self.assertFalse(valida_circuito(G, [1, 2, 1, 2, 1]))     # repete / incompleto
        self.assertFalse(valida_circuito(G, [1, 2, 3, 4, 1, 2, 1]))

    def test_dois_ciclos_compartilhando_vertice(self):
        # "gravata": vertice 1 com grau 4 -> Euleriano
        G = grafo_de(5, [(1, 2), (2, 3), (3, 1), (1, 4), (4, 5), (5, 1)])
        self.assertTrue(euleriano(G))
        self.assertTrue(valida_circuito(G, circuito_euler(G)))

    def test_reprodutibilidade(self):
        g1 = gerar_grafo(10, 0.3, random.Random(137))
        g2 = gerar_grafo(10, 0.3, random.Random(137))
        self.assertEqual(g1, g2)

    def test_aleatorios_sempre_validos(self):
        rng = random.Random(1)
        achados = 0
        for _ in range(3000):
            G = gerar_grafo(10, 0.5, rng)
            if euleriano(G):
                achados += 1
                self.assertTrue(valida_circuito(G, circuito_euler(G)))
        self.assertGreater(achados, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
