from typing import Union

from vr_delaunay_to_voronoi.application\
    .delaunay_simplices_and_voronoi_polygons_getting import \
    get_delaunay_simplices_and_voronoi_polygons
from vr_delaunay_to_voronoi.application.points_getting import get_points
from vr_delaunay_to_voronoi.shims.library_seeding import \
    seed_standard_library_and_numpy


def prepare_plot():
    seed_standard_library_and_numpy()

    points: Union = get_points()
    delaunay_simplices, voronoi_polygons = \
        get_delaunay_simplices_and_voronoi_polygons(points)
    x, y = points[:, 0], points[:, 1]

    return delaunay_simplices, voronoi_polygons, x, y
