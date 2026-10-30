#!/usr/bin/env python3
"""
Projeto de Estruturas Discretas - Grafos (INF1631 - 3WB, 2026)
O robo consegue inspecionar toda a rede?

Gera grafos aleatorios ate encontrar um com circuito de Euler, usando os
criterios matematicos (conectividade dos vertices de grau nao nulo + graus
pares) e o algoritmo de Hierholzer. Depois roda um experimento com 1000 grafos.

Uso:
    python euler.py --p 0.30 --seed 137
"""

import argparse
import random
import time

N_PADRAO = 10
NUM_EXPERIMENTO = 1000


# ----------------------------------------------------------------------
# Representacao: grafo = dict {vertice: set(vizinhos)}, vertices 1..n
# ----------------------------------------------------------------------
def gerar_grafo(n, p, rng):
    """Grafo simples nao direcionado com n vertices; cada uma das
    n(n-1)/2 arestas possiveis e incluida com probabilidade p."""
    G = {v: set() for v in range(1, n + 1)}
    for u in range(1, n + 1):
        for v in range(u + 1, n + 1):
            if rng.random() < p:
                G[u].add(v)
                G[v].add(u)
    return G


def arestas(G):
    """Lista ordenada de arestas (u, v) com u < v."""
    return sorted((u, v) for u in G for v in G[u] if u < v)


def graus(G):
    """Grau de cada vertice."""
    return {v: len(G[v]) for v in G}


def conexo(G):
    """True se todos os vertices de grau > 0 estao na mesma componente
    conexa (busca em profundidade). Sem vertices de grau > 0 -> True
    (condicao vacuamente verdadeira)."""
    nao_nulos = [v for v in G if len(G[v]) > 0]
    if not nao_nulos:
        return True
    visitados = {nao_nulos[0]}
    pilha = [nao_nulos[0]]
    while pilha:
        u = pilha.pop()
        for w in G[u]:
            if w not in visitados:
                visitados.add(w)
                pilha.append(w)
    return all(v in visitados for v in nao_nulos)


def todos_graus_pares(G):
    """True se todos os vertices (de grau nao nulo) tem grau par."""
    return all(len(G[v]) % 2 == 0 for v in G)


def euleriano(G):
    """Criterio de Euler: (1) vertices de grau nao nulo na mesma componente
    conexa e (2) todos com grau par.
    Tratamento explicito do grafo vazio: sem arestas nao ha ruas a inspecionar,
    entao o consideramos NAO adequado (retorna False)."""
    if len(arestas(G)) == 0:
        return False
    return conexo(G) and todos_graus_pares(G)


def circuito_euler(G):
    """Algoritmo de Hierholzer (iterativo). Retorna lista de vertices
    [v0, v1, ..., v0] ou None se o grafo nao for Euleriano."""
    if not euleriano(G):
        return None
    restantes = {v: set(G[v]) for v in G}  # copia: arestas ainda nao usadas
    inicio = next(v for v in sorted(G) if G[v])
    pilha = [inicio]
    circuito = []
    while pilha:
        u = pilha[-1]
        if restantes[u]:
            w = min(restantes[u])      # escolha deterministica
            restantes[u].remove(w)     # consome a aresta {u, w}
            restantes[w].remove(u)
            pilha.append(w)
        else:
            circuito.append(pilha.pop())
    circuito.reverse()
    return circuito


def valida_circuito(G, C):
    """Verifica: comeca e termina no mesmo vertice; cada passo e uma aresta
    de G; nenhuma aresta repetida; todas as arestas de G usadas."""
    if not C or len(C) < 2:
        return False
    if C[0] != C[-1]:
        return False
    usadas = []
    for a, b in zip(C, C[1:]):
        if a not in G or b not in G[a]:
            return False
        usadas.append((min(a, b), max(a, b)))
    if len(usadas) != len(set(usadas)):          # aresta repetida
        return False
    return set(usadas) == set(arestas(G))        # todas as arestas usadas


# ----------------------------------------------------------------------
# Experimentos
# ----------------------------------------------------------------------
def buscar_primeiro_euleriano(n, p, seed, limite=10_000_000):
    rng = random.Random(seed)
    for contador in range(1, limite + 1):
        G = gerar_grafo(n, p, rng)
        if euleriano(G):
            return G, contador
    return None, limite


def experimento(n, p, seed, k=NUM_EXPERIMENTO):
    rng = random.Random(seed)  # mesma seed -> reproduzivel
    t0 = time.perf_counter()
    grafos = [gerar_grafo(n, p, rng) for _ in range(k)]
    tempo = time.perf_counter() - t0
    qtd = sum(1 for G in grafos if euleriano(G))
    return tempo, qtd, qtd / k


def sim_nao(b):
    return "sim" if b else "nao"


def main():
    ap = argparse.ArgumentParser(description="Circuito de Euler em grafos aleatorios")
    ap.add_argument("--p", type=float, default=0.30, help="probabilidade de cada aresta")
    ap.add_argument("--seed", type=int, default=137, help="semente do gerador")
    ap.add_argument("--n", type=int, default=N_PADRAO, help="numero de vertices")
    a = ap.parse_args()

    print(f"Numero de vertices: {a.n}")
    print(f"Probabilidade p: {a.p:.2f}")
    print(f"Seed: {a.seed}")

    G, ger = buscar_primeiro_euleriano(a.n, a.p, a.seed)
    if G is None:
        print("Nenhum grafo Euleriano encontrado dentro do limite.")
        return

    print("Grafo Euleriano encontrado!")
    print(f"Numero de grafos gerados: {ger}")
    print("Arestas:")
    print(" ".join(f"({u},{v})" for u, v in arestas(G)))
    print("Graus:")
    for v, d in graus(G).items():
        print(f"v{v}: {d}")
    print(f"Conexo: {sim_nao(conexo(G))}")
    print(f"Todos os graus sao pares: {sim_nao(todos_graus_pares(G))}")
    print(f"Euleriano: {sim_nao(euleriano(G))}")
    C = circuito_euler(G)
    print("Circuito de Euler:")
    print(" -> ".join(map(str, C)))
    print(f"Validacao do circuito: {'OK' if valida_circuito(G, C) else 'FALHOU'}")

    print("--------------------------------")
    tempo, qtd, prop = experimento(a.n, a.p, a.seed)
    print(f"Experimento com {NUM_EXPERIMENTO} grafos:")
    print(f"Tempo total de geracao: {tempo:.4f} s")
    print(f"Grafos Eulerianos: {qtd}")
    print(f"Proporcao: {prop:.3f}")


if __name__ == "__main__":
    main()
