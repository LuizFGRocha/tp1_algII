import sys
from typing import List, Dict, Set, Tuple
import subprocess
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from copy import deepcopy


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
    
polygon = Polygon()
primal_graph = Graph()
dual_graph = Graph()
dual_to_primal = {}
primal_color_map = {}
cameras = []

color_dict = {-1: "red", 1: 'yellow', 2: "blue", 3: "green"}

class State:
    polygon: Polygon
    primal_graph: Graph
    dual_graph: Graph
    primal_color_map: Dict[int, int]
    cameras: List[Point]

    def __init__(self):
        global polygon, primal_graph, dual_graph, dual_to_primal, primal_color_map, cameras

        self.polygon = deepcopy(polygon)
        self.primal_graph = deepcopy(primal_graph)
        self.dual_graph = deepcopy(dual_graph)
        self.primal_color_map = deepcopy(primal_color_map)
        self.cameras = deepcopy(cameras)


class StateSequence:
    states: List[State]

    def __init__(self):
        self.states = []

    def add_state(self) -> None:
        self.states.append(State())


sequence = StateSequence()

def create_animation(sequence: StateSequence):
    fig, ax = plt.subplots()
    
    def update(frame):
        ax.clear()
        state = sequence.states[frame]
        polygon = state.polygon
        primal_graph = state.primal_graph
        dual_graph = state.dual_graph
        primal_color_map = state.primal_color_map
        
        # Draw polygon points with increased size and edge thickness
        if len(polygon.points) > 0:
            polygon_x = [point.x for point in polygon.points] + [polygon.points[0].x]  # closing the polygon loop
            polygon_y = [point.y for point in polygon.points] + [polygon.points[0].y]
            ax.plot(polygon_x, polygon_y, 'b-', marker='o', markersize=10, linewidth=3)
        
        # Draw primal graph nodes and edges
        for node in primal_graph.nodes:
            x, y = node.point.x, node.point.y
            ax.plot(x, y, 'ro', markersize=5)  # Smaller size for primal graph nodes
            for neighbor_index in node.neighbors:
                neighbor = primal_graph.nodes[neighbor_index].point
                ax.plot([x, neighbor.x], [y, neighbor.y], 'r-', linewidth=1)
        
        # Apply colors from primal_color_map
        for node_index, color in primal_color_map.items():
            node = primal_graph.nodes[node_index]
            ax.plot(node.point.x, node.point.y, 'o', c=color_dict[color], markersize=5)

        # Draws cameras
        for camera in state.cameras:
            ax.plot(camera.x, camera.y, 'kx', markersize=10, color='black')
        
        # Draw dual graph nodes and edges on top of primal graph
        for node in dual_graph.nodes:
            x, y = node.point.x, node.point.y
            ax.plot(x, y, 'o', markersize=5, color='gray')  # Dual graph nodes in gray
            for neighbor_index in node.neighbors:
                neighbor = dual_graph.nodes[neighbor_index].point
                ax.plot([x, neighbor.x], [y, neighbor.y], color='gray', linewidth=1)
        
        ax.set_title(f'State {frame + 1}')
    
    ani = animation.FuncAnimation(fig, update, frames=len(sequence.states), repeat=False, interval=25)
    
    plt.show()


def parse_input(filename: str) -> None:
    # todo fazer funcionar com separação com espaço ou breakline
    with open(filename, 'r') as file:
        size: int = int(file.readline())

        for i in range(size):
            inputs = file.readline().split()

            first_str = inputs[0].split('/')
            first_value = float(first_str[0]) / float(first_str[1])

            second_str = inputs[1].split('/')
            second_value = float(second_str[0]) / float(second_str[1])

            polygon.add_point(Point(first_value, second_value))

    sequence.add_state()


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


def no_point_inside(p1: Point, p2: Point, p3: Point) -> bool:
    for p in polygon.points:
        if p != p1 and p != p2 and p != p3:
            if point_in_triangle(p1, p2, p3, p):
                return False
    return True


def is_ear(position: int) -> bool:
    p1 = polygon.points[position]
    p2 = polygon.points[(position + 1) % len(polygon.points)]
    p3 = polygon.points[(position + 2) % len(polygon.points)]

    if orientation(p1, p2, p3) == -1 and no_point_inside(p1, p2, p3):
        return True

    return False


def triangulate() -> Graph:
    global polygon

    for point in polygon.points:
        primal_graph.add_node(Node(point))

    for node in range(len(primal_graph.nodes)):
        primal_graph.add_edge(node, (node + 1) % len(primal_graph.nodes))

    sequence.add_state()

    while len(polygon.points) > 3:

        # For each position, checks it and the next two
        # Dá pra otimizar essa parte, eu acho
        for pos in range(len(polygon.points)):
            if is_ear(pos):
                # todo melhorar a eficiência da próxima linha talvez
                primal_graph.add_edge_to_points(polygon.points[pos], polygon.points[(pos + 2) % len(polygon.points)])
                polygon.remove_point_at((pos + 1) % len(polygon.points))
                sequence.add_state()
                break

    # Apaga o polígono
    polygon = Polygon()

    return primal_graph


def get_faces() -> List[Set[int]]:
    # todo verificar se está funcionando
    input: str = primal_graph.to_string()

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


def get_dual() -> None:
    faces = get_faces()

    # Cria um nó para cada face no grafo original
    for i, face in enumerate(faces):
        face_center = Point(sum(primal_graph.nodes[v].point.x for v in face) / len(face),
                            sum(primal_graph.nodes[v].point.y for v in face) / len(face))
        dual_graph.add_node(Node(face_center))
        dual_to_primal[i] = face

    # Conecta nós no grafo dual se as faces originais compartilharem uma aresta
    for edge in primal_graph.edges():
        incident_faces = [i for i, face in enumerate(faces) if edge.issubset(face)]
        if len(incident_faces) == 2:
            dual_graph.add_edge(incident_faces[0], incident_faces[1])

    sequence.add_state()

    return dual_graph, dual_to_primal


def color() -> Dict[int, int]:
    global primal_color_map, dual_graph
    primal_color_map = {i: -1 for i in range(len(primal_graph.nodes))}
    visited: Dict[int, bool] = {i: False for i in range(len(dual_graph.nodes))}

    def dfs(node: int):
        available_colors: Set[int] = {1, 2, 3}
        for vertex in dual_to_primal[node]:
            if primal_color_map[vertex] != -1:
                available_colors.remove(primal_color_map[vertex])
        for vertex in dual_to_primal[node]:
            if primal_color_map[vertex] == -1:
                primal_color_map[vertex] = available_colors.pop()
                sequence.add_state()

        visited[node] = True

        for neighbor in dual_graph.nodes[node].neighbors:
            if not visited[neighbor]:
                dfs(neighbor)

    dfs(0)

    # Apaga o grafo dual
    dual_graph = Graph()

    # Escolhe do map a cor com menos ocorrências
    color_count = {1: 0, 2: 0, 3: 0}
    for color in primal_color_map.values():
        color_count[color] += 1

    min_color = min(color_count, key=color_count.get)

    for vertex in primal_color_map:
        if primal_color_map[vertex] == min_color:
            cameras.append(primal_graph.nodes[vertex].point)

    sequence.add_state()

    return primal_color_map


def run(filename: str) -> None:
    parse_input(filename)

    triangulate()
    get_dual()
    color()

    sequence.add_state()

    create_animation(sequence)


def main():
    filename: str = sys.argv[1]

    parse_input(filename)

    triangulate()
    get_dual()
    color()

    sequence.add_state()

    create_animation(sequence)


if __name__ == '__main__':
    main()
