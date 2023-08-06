import numpy as np


def get_points(
    *,
    dimensionality=2,
):
    points = np.random.normal(
        loc=(0.5, ) * dimensionality,
        scale=(0.2, ) * dimensionality,
        size=(10, dimensionality),
    )

    return points
