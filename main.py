import sys
from typing import List


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
    self.points.pop(index)


def parse_input(filename: str) -> Polygon:
  polygon = Polygon()

  with open(filename, 'r') as file:
    inputs = file.readline().split('   ')

    vertex_count = int(inputs[0])
    for i in range(1, 2 * vertex_count, 2):
      first_str = inputs[i].split('/')
      first_value = float(first_str[0]) / float(first_str[1])

      second_str = inputs[i+1].split('/')
      second_value = float(second_str[0]) / float(second_str[1])

      polygon.add_point(Point(first_value, second_value))

  return polygon


def triangulate(polygon: Polygon) -> Polygon:
  pass


def main():
  filename = sys.argv[1]
  polygon = parse_input(filename)

  for point in polygon.points:
    print(f'({point.x}, {point.y})')
    

if __name__ == '__main__':
  main()