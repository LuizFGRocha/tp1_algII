import sys
from typing import List, Dict, Set, Tuple
import plotly.graph_objects as go
import subprocess


class Point:

    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y


class Polygon:

    points: List[Point]

    def __init__(self):
        self.points = []

    def add_point(self, i_point: Point) -> None:
        self.points.append(i_point)

    def remove_point(self, i_point: Point) -> None:
        self.points.remove(i_point)

    def remove_point_at(self, index: int):
        """
        Removes a point at a given index. 
        If the index is greater than the number of points, it will wrap around.
        """
        self.points.pop(index % len(self.points))


class Node:
    point: Point
    neighbors: List[int]

    def __init__(self, point: Point):
        self.point = point
        self.neighbors = []


class Graph:
    nodes: List[Node]

    def __init__(self):
        self.nodes = []

    def add_node(self, i_node: Node) -> None:
        self.nodes.append(i_node)

    # Doesn't remove nodes so that the index of the nodes remains the same

    def add_edge(self, start: int, end: int) -> None:
        self.nodes[start].neighbors.append(end)
        self.nodes[end].neighbors.append(start)

    def add_edge_to_points(self, start: Point, end: Point) -> None:
        start_index: int = -1
        end_index: int = -1

        for i in range(len(self.nodes)):
            if self.nodes[i].point == start:
                start_index = i
            if self.nodes[i].point == end:
                end_index = i

        if start_index == -1:
            self.add_node(Node(start))
            start_index = len(self.nodes) - 1

        if end_index == -1:
            self.add_node(Node(end))
            end_index = len(self.nodes) - 1

        self.add_edge(start_index, end_index)

    def remove_edge(self, start: int, end: int) -> None:
        self.nodes[start].neighbors.remove(end)
        self.nodes[end].neighbors.remove(start)

    def edges(self) -> Set[Set[int]]:
        edges = set()
        for i in range(len(self.nodes)):
            for neighbor in self.nodes[i].neighbors:
                edges.add(frozenset([i, neighbor]))
        return edges

    def nodes(self) -> List[int]:
        return [i for i in range(len(self.nodes))]

    def to_string(self) -> str:
        string: str = ""
        string += f"{len(self.nodes)} {len(self.edges())}\n"

        for i in range(len(self.nodes)):
            string += f"{int(self.nodes[i].point.x)} {int(self.nodes[i].point.y)} "
            string += f"{len(self.nodes[i].neighbors)} "
            for neighbor in self.nodes[i].neighbors:
                string += f"{neighbor + 1} "
            string += "\n"

        return string


def plot_polygon(polygon: Polygon):
    x_coords = [point.x for point in polygon.points]
    y_coords = [point.y for point in polygon.points]

    if len(polygon.points) > 0:
        x_coords.append(polygon.points[0].x)
        y_coords.append(polygon.points[0].y)

    fig = go.Figure(go.Scatter(x=x_coords, y=y_coords, fill="toself", mode='lines+markers'))

    fig.update_layout(title="Polígono", xaxis_title="X", yaxis_title="Y")

    fig.show()


def plot_graph(graph: Graph):
    x_coords = [node.point.x for node in graph.nodes]
    y_coords = [node.point.y for node in graph.nodes]

    fig = go.Figure(go.Scatter(x=x_coords, y=y_coords, mode='markers'))

    for node in graph.nodes:
        for neighbor in node.neighbors:
            fig.add_trace(go.Scatter(x=[node.point.x, graph.nodes[neighbor].point.x], y=[node.point.y, graph.nodes[neighbor].point.y], mode='lines'))

    fig.update_layout(title="Grafo", xaxis_title="X", yaxis_title="Y")

    fig.show()

def plot_two_graphs(graph1, graph2, color_map1=None, color_map2=None):
    fig = go.Figure()

    # Adiciona os nós e arestas do primeiro grafo
    for idx, node in enumerate(graph1.nodes):
        color = color_map1[idx] if color_map1 and idx in color_map1 else 'blue'
        fig.add_trace(go.Scatter(x=[node.point.x], y=[node.point.y], mode='markers',
                                 marker=dict(color=color)))
        for neighbor in node.neighbors:
            fig.add_trace(go.Scatter(x=[node.point.x, graph1.nodes[neighbor].point.x],
                                     y=[node.point.y, graph1.nodes[neighbor].point.y], mode='lines',
                                     line=dict(color=color)))

    # Adiciona os nós e arestas do segundo grafo
    for idx, node in enumerate(graph2.nodes):
        color = color_map2[idx] if color_map2 and idx in color_map2 else 'red'
        fig.add_trace(go.Scatter(x=[node.point.x], y=[node.point.y], mode='markers',
                                 marker=dict(color=color)))
        for neighbor in node.neighbors:
            fig.add_trace(go.Scatter(x=[node.point.x, graph2.nodes[neighbor].point.x],
                                     y=[node.point.y, graph2.nodes[neighbor].point.y], mode='lines',
                                     line=dict(color=color)))

    # Atualiza o layout da figura
    fig.update_layout(title="Dois Grafos", xaxis_title="X", yaxis_title="Y")

    # Mostra a figura
    fig.show()


def plot_graph_colored(graph: Graph, color_map: dict):
    fig = go.Figure()

    for idx, node in enumerate(graph.nodes):
        if idx not in color_map:
            print(f"Warning: Node {idx} not in color_map")
            continue

        fig.add_trace(go.Scatter(x=[node.point.x], y=[node.point.y], mode='markers',
                                 marker=dict(color=color_map[idx])))

    for node in graph.nodes:
        for neighbor in node.neighbors:
            fig.add_trace(go.Scatter(x=[node.point.x, graph.nodes[neighbor].point.x],
                                     y=[node.point.y, graph.nodes[neighbor].point.y],
                                     mode='lines', line=dict(color='grey')))

    fig.update_layout(title="Grafo Colorido", xaxis_title="X", yaxis_title="Y")
    fig.show()




def parse_input(filename: str) -> Polygon:
    polygon = Polygon()

    with open(filename, 'r') as file:
        size: int = int(file.readline())

        for i in range(size):
            inputs = file.readline().split()

            first_str = inputs[0].split('/')
            first_value = float(first_str[0]) / float(first_str[1])

            second_str = inputs[1].split('/')
            second_value = float(second_str[0]) / float(second_str[1])

            polygon.add_point(Point(first_value, second_value))

    return polygon


def orientation(p1: Point, p2: Point, p3: Point) -> int:
    """
    Returns the orientation of the 3 points.
    1: Clockwise
    0: Collinear
    -1: Counter clockwise
    """
    val = (p2.y - p1.y) * (p3.x - p2.x) - (p2.x - p1.x) * (p3.y - p2.y)

    if val == 0:
        return 0
    return 1 if val > 0 else -1


def point_in_triangle(p1: Point, p2: Point, p3: Point, p: Point) -> bool:
    # Precisa tratar caso de divisão por 0
    points: List[Point] = [p1, p2, p3]

    crossings: int = 0
    for i in range(3):

        # todo verificar se esse problema tá resolvido
        slope: float
        if points[i].x == points[(i + 1) % 3].x:
            slope = float('inf')
        else:
            slope = (points[(i + 1) % 3].y - points[i].y) / (points[(i + 1) % 3].x - points[i].x)

        cond1: bool = points[i].x <= p.x < points[(i + 1) % 3].x
        cond2: bool = points[(i + 1) % 3].x <= p.x < points[i].x
        above: bool = p.y <= slope * (p.x - points[i].x) + points[i].y # Mudei para <= espero que não dê problema kk
        if (cond1 or cond2) and above:
            crossings += 1

    return crossings % 2 != 0


def no_point_inside(p1: Point, p2: Point, p3: Point, polygon: Polygon) -> bool:
    for p in polygon.points:
        if p != p1 and p != p2 and p != p3:
            if point_in_triangle(p1, p2, p3, p):
                return False
    return True


def is_ear(polygon: Polygon, position: int) -> bool:
    p1 = polygon.points[position]
    p2 = polygon.points[(position + 1) % len(polygon.points)]
    p3 = polygon.points[(position + 2) % len(polygon.points)]

    if orientation(p1, p2, p3) == -1 and no_point_inside(p1, p2, p3, polygon):
        return True

    return False


def triangulate(polygon: Polygon) -> Graph:
    # todo verificar se está funcionando
    graph = Graph()

    for point in polygon.points:
        graph.add_node(Node(point))

    for node in range(len(graph.nodes)):
        graph.add_edge(node, (node + 1) % len(graph.nodes))

    while len(polygon.points) > 3:

        # For each position, checks it and the next two
        # Dá pra otimizar essa parte, eu acho
        for pos in range(len(polygon.points)):
            if is_ear(polygon, pos):
                # todo melhorar a eficiência da próxima linha talvez
                graph.add_edge_to_points(polygon.points[pos], polygon.points[(pos + 2) % len(polygon.points)])
                polygon.remove_point_at((pos + 1) % len(polygon.points))
                break

    return graph


def get_faces(graph: Graph) -> List[Set[int]]:
    # todo verificar se está funcionando
    input: str = graph.to_string()

    result = subprocess.run(["ls", "./main"], capture_output=True)
    if result.returncode != 0:
        result = subprocess.run(["g++", "main.cpp", "-o", "main", "-Ofast"])
        if result.returncode != 0:
            raise ValueError("Erro ao compilar o programa. Verifique se o arquivo main.cpp existe e se você"
                             "tem o compilador g++ instalado.")

    result = subprocess.run(["./main"], input=input, text=True, capture_output=True)
    output: str = result.stdout

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


def get_dual(graph: Graph) -> Tuple[Graph, Dict[int, set]]:
    faces = get_faces(graph)
    dual_graph = Graph()
    dual_to_primal: Dict[int, set] = {}

    # Cria um nó para cada face no grafo original
    for i, face in enumerate(faces):
        face_center = Point(sum(graph.nodes[v].point.x for v in face) / len(face),
                            sum(graph.nodes[v].point.y for v in face) / len(face))
        dual_graph.add_node(Node(face_center))
        dual_to_primal[i] = face

    # Conecta nós no grafo dual se as faces originais compartilharem uma aresta
    for edge in graph.edges():
        incident_faces = [i for i, face in enumerate(faces) if edge.issubset(face)]
        if len(incident_faces) == 2:
            dual_graph.add_edge(incident_faces[0], incident_faces[1])

    plot_two_graphs(graph, dual_graph)

    return dual_graph, dual_to_primal


def color(graph: Graph, dual: Graph, dual_to_primal: Dict[int, set]) -> Dict[int, int]:
    primal_color_map: Dict[int, int] = {i: -1 for i in range(len(graph.nodes))}
    visited: Dict[int, bool] = {i: False for i in range(len(dual.nodes))}

    def dfs(node: int):
        available_colors: Set[int] = {1, 2, 3}
        for vertex in dual_to_primal[node]:
            if primal_color_map[vertex] != -1:
                available_colors.remove(primal_color_map[vertex])
        for vertex in dual_to_primal[node]:
            if primal_color_map[vertex] == -1:
                primal_color_map[vertex] = available_colors.pop()

        visited[node] = True

        for neighbor in dual.nodes[node].neighbors:
            if not visited[neighbor]:
                dfs(neighbor)

    dfs(0)

    return primal_color_map


def main():
    filename: str = sys.argv[1]
    polygon: Polygon = parse_input(filename)
    graph: Graph = triangulate(polygon)
    dual, dual_to_primal = get_dual(graph)
    color_map: Dict[int, int] = color(graph, dual, dual_to_primal)

    print("Color Map:", color_map)

    plot_graph_colored(graph, color_map)

if __name__ == '__main__':
    main()
