import sys
from typing import List, Dict, Set
import subprocess
import matplotlib.pyplot as plt
from copy import deepcopy
from animate import *

class Ponto:

    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y


class Poligono:

    pontos: List[Ponto]

    def __init__(self):
        self.pontos = []

    def add_ponto(self, i_ponto: Ponto) -> None:
        self.pontos.append(i_ponto)

    def remove_ponto(self, i_ponto: Ponto) -> None:
        self.pontos.remove(i_ponto)

    def remove_ponto_em(self, index: int):
        """
        Remove um ponto em um dado indice. 
        Se o indice é maior que o numero de pontos, ele retorna ao 0 e segue.
        """
        self.pontos.pop(index % len(self.pontos))


class No:
    ponto: Ponto
    vizinhos: List[int]

    def __init__(self, ponto: Ponto):
        self.ponto = ponto
        self.vizinhos = []


class Grafo:
    nos: List[No]

    def __init__(self):
        self.nos = []

    def add_no(self, i_no: No) -> None:
        self.nos.append(i_no)

    # Nao remove nos para que o indice dos nos siga o mesmo

    def add_aresta(self, start: int, end: int) -> None:
        self.nos[start].vizinhos.append(end)
        self.nos[end].vizinhos.append(start)

    def add_aresta_a_pontos(self, start: Ponto, end: Ponto) -> None:
        start_index: int = -1
        end_index: int = -1

        for i in range(len(self.nos)):
            if self.nos[i].ponto == start:
                start_index = i
            if self.nos[i].ponto == end:
                end_index = i

        if start_index == -1:
            self.add_no(No(start))
            start_index = len(self.nos) - 1

        if end_index == -1:
            self.add_no(No(end))
            end_index = len(self.nos) - 1

        self.add_aresta(start_index, end_index)

    def remove_aresta(self, start: int, end: int) -> None:
        self.nos[start].vizinhos.remove(end)
        self.nos[end].vizinhos.remove(start)

    def arestas(self) -> Set[Set[int]]:
        arestas = set()
        for i in range(len(self.nos)):
            for vizinho in self.nos[i].vizinhos:
                arestas.add(frozenset([i, vizinho]))
        return arestas

    def nos(self) -> List[int]:
        return [i for i in range(len(self.nos))]

    def to_string(self) -> str:
        string: str = ""
        string += f"{len(self.nos)} {len(self.arestas())}\n"

        for i in range(len(self.nos)):
            string += f"{int(self.nos[i].ponto.x)} {int(self.nos[i].ponto.y)} "
            string += f"{len(self.nos[i].vizinhos)} "
            for vizinho in self.nos[i].vizinhos:
                string += f"{vizinho + 1} "
            string += "\n"

        return string
    
poligono = Poligono()
grafo_primal = Grafo()
grafo_dual = Grafo()
dual_a_primal = {}
mapa_cor_primal = {}
cameras = []

color_dict = {-1: "red", 1: 'yellow', 2: "blue", 3: "green"}

class Estado:
    poligono: Poligono
    grafo_primal: Grafo
    grafo_dual: Grafo
    mapa_cor_primal: Dict[int, int]
    cameras: List[Ponto]

    def __init__(self):
        global poligono, grafo_primal, grafo_dual, dual_a_primal, mapa_cor_primal, cameras

        self.poligono = deepcopy(poligono)
        self.grafo_primal = deepcopy(grafo_primal)
        self.grafo_dual = deepcopy(grafo_dual)
        self.mapa_cor_primal = deepcopy(mapa_cor_primal)
        self.cameras = deepcopy(cameras)


class SequenciaEstados:
    estados: List[Estado]

    def __init__(self):
        self.estados = []

    def add_estado(self) -> None:
        self.estados.append(Estado())


sequencia = SequenciaEstados()

def cria_animacao(sequencia: SequenciaEstados):
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))

    ax.set_aspect('equal', adjustable='datalim')
    
    def update(frame):
        ax.clear()
        estado = sequencia.estados[frame]
        poligono = estado.poligono
        grafo_primal = estado.grafo_primal
        grafo_dual = estado.grafo_dual
        mapa_cor_primal = estado.mapa_cor_primal
        
        # Desenha os pontos do poligono com area maior e arestas mais grossas
        if len(poligono.pontos) > 0:
            poligono_x = [ponto.x for ponto in poligono.pontos] + [poligono.pontos[0].x]  # fechando o loop do poligono
            poligono_y = [ponto.y for ponto in poligono.pontos] + [poligono.pontos[0].y]
            ax.plot(poligono_x, poligono_y, 'b-', marker='o', markersize=10, linewidth=3)
        
        # Desenha os nos e arestas do grafo primal
        for no in grafo_primal.nos:
            x, y = no.ponto.x, no.ponto.y
            ax.plot(x, y, 'ro', markersize=5)  # Tamanho reduzido para nos do grafo primal
            for vizinho_index in no.vizinhos:
                vizinho = grafo_primal.nos[vizinho_index].ponto
                ax.plot([x, vizinho.x], [y, vizinho.y], 'r-', linewidth=1)
        
        # Aplica cores do mapa_cor_primal
        for no_index, color in mapa_cor_primal.items():
            no = grafo_primal.nos[no_index]
            ax.plot(no.ponto.x, no.ponto.y, 'o', c=color_dict[color], markersize=5)

        # Desenha cameras
        for camera in estado.cameras:
            ax.plot(camera.x, camera.y, 'kx', markersize=10, color='black')

        if len(estado.cameras) > 0:
            ax.set_title(f'Estado final - {len(estado.cameras)} câmeras')
        
        # Desenha nos e arestas do grafo dual em cima do primal
        for no in grafo_dual.nos:
            x, y = no.ponto.x, no.ponto.y
            ax.plot(x, y, 'o', markersize=5, color='gray')  # Dual graph nos in gray
            for vizinho_index in no.vizinhos:
                vizinho = grafo_dual.nos[vizinho_index].ponto
                ax.plot([x, vizinho.x], [y, vizinho.y], color='gray', linewidth=1)
        
        ax.set_title(f'Estado {frame + 1}')
    
    # Instanciando Player
    ani = Player(fig, update, maxi=len(sequencia.estados)-1)
    
    plt.show()


def parse_entrada(arquivo: str) -> None:
    # fazer funcionar com separação com espaço ou breakline
    with open(arquivo, 'r') as file:
        tam: int = int(file.readline())

        for i in range(tam):
            inputs = file.readline().split()

            pri_str = inputs[0].split('/')
            pri_value = float(pri_str[0]) / float(pri_str[1])

            seg_str = inputs[1].split('/')
            seg_value = float(seg_str[0]) / float(seg_str[1])

            poligono.add_ponto(Ponto(pri_value, seg_value))

    sequencia.add_estado()


def orientacao(p1: Ponto, p2: Ponto, p3: Ponto) -> int:
    """
    Retorna a orientacao dos 3 pontos.
    1: Horario
    0: Colinear
    -1: Anti-Horario
    """
    val = (p2.y - p1.y) * (p3.x - p2.x) - (p2.x - p1.x) * (p3.y - p2.y)

    if val == 0:
        return 0
    return 1 if val > 0 else -1


def ponto_no_triangulo(p1: Ponto, p2: Ponto, p3: Ponto, p: Ponto) -> bool:
    # Precisa tratar caso de divisão por 0
    pontos: List[Ponto] = [p1, p2, p3]

    cruzamentos: int = 0
    for i in range(3):

        # todo verificar se esse problema tá resolvido
        inclinacao: float
        if pontos[i].x == pontos[(i + 1) % 3].x:
            inclinacao = float('inf')
        else:
            inclinacao = (pontos[(i + 1) % 3].y - pontos[i].y) / (pontos[(i + 1) % 3].x - pontos[i].x)

        cond1: bool = pontos[i].x <= p.x < pontos[(i + 1) % 3].x
        cond2: bool = pontos[(i + 1) % 3].x <= p.x < pontos[i].x
        acima: bool = p.y <= inclinacao * (p.x - pontos[i].x) + pontos[i].y # Mudei para <= espero que não dê problema kk
        if (cond1 or cond2) and acima:
            cruzamentos += 1

    return cruzamentos % 2 != 0


def nenhum_ponto_dentro(p1: Ponto, p2: Ponto, p3: Ponto) -> bool:
    for p in poligono.pontos:
        if p != p1 and p != p2 and p != p3:
            if ponto_no_triangulo(p1, p2, p3, p):
                return False
    return True


def eh_orelha(posicao: int) -> bool:
    p1 = poligono.pontos[posicao]
    p2 = poligono.pontos[(posicao + 1) % len(poligono.pontos)]
    p3 = poligono.pontos[(posicao + 2) % len(poligono.pontos)]

    if orientacao(p1, p2, p3) == -1 and nenhum_ponto_dentro(p1, p2, p3):
        return True

    return False


def triangular() -> Grafo:
    global poligono

    for ponto in poligono.pontos:
        grafo_primal.add_no(No(ponto))

    for no in range(len(grafo_primal.nos)):
        grafo_primal.add_aresta(no, (no + 1) % len(grafo_primal.nos))

    sequencia.add_estado()

    while len(poligono.pontos) > 3:

        # Para cada posição, checamos ela e as duas seguintes
        # Dá pra otimizar essa parte, eu acho
        for pos in range(len(poligono.pontos)):
            if eh_orelha(pos):
                # melhorar a eficiência da próxima linha talvez
                grafo_primal.add_aresta_a_pontos(poligono.pontos[pos], poligono.pontos[(pos + 2) % len(poligono.pontos)])
                poligono.remove_ponto_em((pos + 1) % len(poligono.pontos))
                sequencia.add_estado()
                break

    # Apaga o polígono
    poligono = Poligono()

    return grafo_primal


def get_faces() -> List[Set[int]]:
    # verificar se está funcionando
    input: str = grafo_primal.to_string()

    resultado = subprocess.run(["ls", "./main"], capture_output=True)
    if resultado.returncode != 0:
        resultado = subprocess.run(["g++", "main.cpp", "-o", "main", "-Ofast"])
        if resultado.returncode != 0:
            raise ValueError("Erro ao compilar o programa. Verifique se o arquivo main.cpp existe e se você"
                             "tem o compilador g++ instalado.")

    resultado = subprocess.run(["./main"], input=input, text=True, capture_output=True)
    output: str = resultado.stdout

    output = output.split('\n')
    qtd: int = int(output.pop(0))  # Remove a quantidade de vértices

    faces: List[Set[int]] = []

    for face in output:
        vertices = face.split(' ')

        if vertices[0] != '4':
            continue

        faces.append(set([int(vertex) - 1 for vertex in vertices[1:]]))

    if len(faces) != qtd - 1:
        raise ValueError("Número de faces incorreto")

    return faces


def get_dual() -> None:
    faces = get_faces()

    # Cria um nó para cada face no grafo original
    for i, face in enumerate(faces):
        face_centro = Ponto(sum(grafo_primal.nos[v].ponto.x for v in face) / len(face),
                            sum(grafo_primal.nos[v].ponto.y for v in face) / len(face))
        grafo_dual.add_no(No(face_centro))
        dual_a_primal[i] = face

    # Conecta nós no grafo dual se as faces originais compartilharem uma aresta
    for aresta in grafo_primal.arestas():
        faces_incidentes = [i for i, face in enumerate(faces) if aresta.issubset(face)]
        if len(faces_incidentes) == 2:
            grafo_dual.add_aresta(faces_incidentes[0], faces_incidentes[1])

    sequencia.add_estado()

    return grafo_dual, dual_a_primal


def cor() -> Dict[int, int]:
    global mapa_cor_primal, grafo_dual
    mapa_cor_primal = {i: -1 for i in range(len(grafo_primal.nos))}
    visitados: Dict[int, bool] = {i: False for i in range(len(grafo_dual.nos))}

    def dfs(no: int):
        dispo_cores: Set[int] = {1, 2, 3}
        for vertex in dual_a_primal[no]:
            if mapa_cor_primal[vertex] != -1:
                dispo_cores.remove(mapa_cor_primal[vertex])
        for vertex in dual_a_primal[no]:
            if mapa_cor_primal[vertex] == -1:
                mapa_cor_primal[vertex] = dispo_cores.pop()
                sequencia.add_estado()

        visitados[no] = True

        for vizinho in grafo_dual.nos[no].vizinhos:
            if not visitados[vizinho]:
                dfs(vizinho)

    dfs(0)

    # Apaga o grafo dual
    grafo_dual = Grafo()

    # Escolhe do map a cor com menos ocorrências
    cor_contador = {1: 0, 2: 0, 3: 0}
    for cor in mapa_cor_primal.values():
        cor_contador[cor] += 1

    min_cor = min(cor_contador, key=cor_contador.get)

    for vertex in mapa_cor_primal:
        if mapa_cor_primal[vertex] == min_cor:
            cameras.append(grafo_primal.nos[vertex].ponto)

    sequencia.add_estado()

    return mapa_cor_primal


def run(arquivo: str) -> None:
    parse_entrada(arquivo)

    triangular()
    get_dual()
    cor()

    sequencia.add_estado()

    cria_animacao(sequencia)


def main():
    arquivo: str = sys.argv[1]

    parse_entrada(arquivo)

    triangular()
    get_dual()
    cor()

    sequencia.add_estado()

    cria_animacao(sequencia)


if __name__ == '__main__':
    main()
