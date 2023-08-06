import numpy as np


def get_long_line_endpoints_and_line_indices(
    *,
    circum_centers,
    delaunay,
    triangles,
):
    long_lines_endpoints = []
    triangle_index_and_an_integer = []
    for triangle_index, triangle in enumerate(triangles):
        circum_center = circum_centers[triangle_index]
        triangle_neighbors = delaunay.neighbors[triangle_index]
        triangle_index_and_an_integer += _get_triangle_index_and_an_integer(
            circum_center=circum_center,
            circum_centers=circum_centers,
            long_lines_endpoints=long_lines_endpoints,
            triangle=triangle,
            triangle_index=triangle_index,
            triangle_neighbors=triangle_neighbors,
        )

    return long_lines_endpoints, triangle_index_and_an_integer


def _get_triangle_index_and_an_integer(
    *,
    circum_center,
    circum_centers,
    long_lines_endpoints,
    triangle,
    triangle_index,
    triangle_neighbors,
):
    list_of_triangle_indices_and_integers = []
    for neighbor_index, neighbor in enumerate(triangle_neighbors):
        if neighbor != -1:
            list_of_triangle_indices_and_integers.append(
                (triangle_index, neighbor)
            )
            continue

        ps = \
            triangle[(neighbor_index + 1) % 3] - \
            triangle[(neighbor_index - 1) % 3]
        try:
            # 3D
            ps = np.array((ps[2], ps[1], -ps[0]))  # TODO Is this correct?
        except IndexError:
            # 2D
            ps = np.array((ps[1], -ps[0]))

        middle = (
            triangle[(neighbor_index + 1) % 3] +
            triangle[(neighbor_index - 1) % 3]
        ) * 0.5
        di = middle - triangle[neighbor_index]

        ps /= np.linalg.norm(ps)
        di /= np.linalg.norm(di)

        if np.dot(di, ps) < 0.0:
            ps *= -1000.0
        else:
            ps *= 1000.0

        long_lines_endpoints.append(circum_center + ps)
        triangle_index_and_an_integer = (
            triangle_index,
            len(circum_centers) + len(long_lines_endpoints) - 1
        )
        list_of_triangle_indices_and_integers.append(
            triangle_index_and_an_integer
        )

    return list_of_triangle_indices_and_integers
