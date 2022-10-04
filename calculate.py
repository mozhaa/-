import numpy as np
import random
import math
import pickle
import sys


def main(args):
    filename = args[1]
    with open(filename, "rb") as file:
        details = pickle.load(file)
    calculate(details)


def get_value(details, x):
    result = 0
    for det in details:
        if x >= det.pos and x < det.pos + det.length:
            result += det.mass / det.length
    return result


def get_center_of_gravity(details):
    result = 0
    total_mass = 0
    for det in details:
        total_mass += det.mass
        result += det.mass * (det.pos + det.length / 2)
    return result / total_mass


def random_color():
    return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])


def calculate(details):
    f = lambda x: get_value(details, x)
    left_edge = min([det.pos for det in details])
    right_edge = max([(det.pos + det.length) for det in details])
    precision = 10000
    segment_size = (right_edge - left_edge) / precision
    points = np.linspace(left_edge, right_edge, precision)
    center = get_center_of_gravity(details)
    prev = f(left_edge) * math.pow(left_edge - center, 2)
    total_area = 0
    for i, x in enumerate(points[1:]):
        curr = f(x) * math.pow(x - center, 2)
        total_area += segment_size * (prev + curr) / 2
        prev = curr
    print(total_area) # грамм / см^2



if __name__ == "__main__":
    main(sys.argv)
