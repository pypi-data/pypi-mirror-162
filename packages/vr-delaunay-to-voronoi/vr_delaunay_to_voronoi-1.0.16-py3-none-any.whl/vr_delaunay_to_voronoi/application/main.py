from typing import Any, List, Union

from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
from scipy.spatial import Delaunay

from vr_delaunay_to_voronoi.application.plotting import plot
from vr_delaunay_to_voronoi.application.points_getting import get_points
from vr_delaunay_to_voronoi.shims.library_seeding import \
    seed_standard_library_and_numpy
from vr_delaunay_to_voronoi.shims.matplotlib_patches import get_polygons
from vr_delaunay_to_voronoi.voronoi.delaunay_tesselation_getting import \
    get_delaunay_tesselation
from vr_delaunay_to_voronoi.voronoi.voronoi_getting import get_voronoi_polygons


def main():
    delaunay_simplices, voronoi_polygons, x, y = prepare_plot()

    plot(
        delaunay_simplices=delaunay_simplices,
        voronoi_polygons=voronoi_polygons,
        x=x,
        y=y,
    )

    plt.show()


def prepare_plot():
    seed_standard_library_and_numpy()

    points: Union = get_points()
    delaunay_simplices, voronoi_polygons = \
        get_delaunay_simplices_and_voronoi_polygons(points)
    x, y = points[:, 0], points[:, 1]

    return delaunay_simplices, voronoi_polygons, x, y


def get_delaunay_simplices_and_voronoi_polygons(points):
    delaunay: Delaunay = get_delaunay_tesselation(points=points)
    voronoi_polygon_list: List[Any] = get_voronoi_polygons(delaunay=delaunay)
    voronoi_polygons: List[Polygon] = \
        get_polygons(voronoi_polygon_list=voronoi_polygon_list)

    delaunay_simplices = delaunay.simplices

    return delaunay_simplices, voronoi_polygons


if __name__ == '__main__':
    main()
