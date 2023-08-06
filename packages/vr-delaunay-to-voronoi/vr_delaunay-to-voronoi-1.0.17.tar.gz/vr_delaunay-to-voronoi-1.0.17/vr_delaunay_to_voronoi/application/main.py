from matplotlib import pyplot as plt

from vr_delaunay_to_voronoi.application.plot_preparation import prepare_plot
from vr_delaunay_to_voronoi.application.plotting import plot


def main():
    delaunay_simplices, voronoi_polygons, x, y = prepare_plot()

    plot(
        delaunay_simplices=delaunay_simplices,
        voronoi_polygons=voronoi_polygons,
        x=x,
        y=y,
    )

    plt.show()


if __name__ == '__main__':
    main()
