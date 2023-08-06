from typing import List, Any

from matplotlib.patches import Polygon
from scipy.spatial import Delaunay

from vr_delaunay_to_voronoi.shims.matplotlib_patches import get_polygons
from vr_delaunay_to_voronoi.voronoi.delaunay_tesselation_getting import \
    get_delaunay_tesselation
from vr_delaunay_to_voronoi.voronoi.voronoi_getting import get_voronoi_polygons


def get_delaunay_simplices_and_voronoi_polygons(points):
    delaunay: Delaunay = get_delaunay_tesselation(points=points)
    voronoi_polygon_list: List[Any] = get_voronoi_polygons(delaunay=delaunay)
    voronoi_polygons: List[Polygon] = \
        get_polygons(voronoi_polygon_list=voronoi_polygon_list)

    delaunay_simplices = delaunay.simplices

    return delaunay_simplices, voronoi_polygons
