from typing import Any, DefaultDict, List, Tuple


def close_outer_cells(
    *,
    cells: DefaultDict[Any, List[Tuple]],
) -> DefaultDict[Any, List[Tuple]]:
    """
    Close the outer cells.
    """
    for polygon_index, line_indices in cells.items():
        lines_with_one_dangling_vertex = []
        lines_with_two_dangling_vertices = []
        for line_index_0, line_index_1 in line_indices:
            connections = _get_connections(
                line_indices=line_indices,
                line_index_0=line_index_0,
                line_index_1=line_index_1,
            )
            line = (line_index_0, line_index_1)
            print(line)
            if len(connections) == 0:
                lines_with_two_dangling_vertices.append(line)
            if len(connections) < 1:
                raise ValueError(
                    f'Too few connections ({len(connections)}): {connections}'
                )
            if len(connections) == 1:
                lines_with_one_dangling_vertex.append(line)
            # Lines with 2 connections are not dangling in any sense
            if len(connections) > 2:
                raise ValueError(
                    f'Too many connections ({len(connections)}): {connections}'
                )
        assert len(lines_with_one_dangling_vertex) in {0, 2}
        if len(lines_with_one_dangling_vertex) == 2:
            (i11, i12), (i21, i22) = lines_with_one_dangling_vertex

            # determine which line ends are unconnected
            i11_unconnected = not _get_connected(
                line_indices=line_indices,
                start_index=i11,
                end_index=i12,
            )

            i21_unconnected = not _get_connected(
                start_index=i21,
                end_index=i22,
                line_indices=line_indices,
            )

            start_index = i11 if i11_unconnected else i12
            end_index = i21 if i21_unconnected else i22

            line = (start_index, end_index)
            cells[polygon_index].append(line)

    return cells


def _get_connected(
    *,
    line_indices,
    start_index,
    end_index,
):
    connected = list(
        filter(
            lambda line:
            (line[0], line[1]) != (start_index, end_index) and
            (
                    line[0] == start_index or
                    line[1] == start_index
            ),
            line_indices
        )
    )

    return connected


def _get_connections(
    *,
    line_indices,
    line_index_0,
    line_index_1,
):
    connections = list(
        filter(
            lambda i12_:
            (line_index_0, line_index_1) != (i12_[0], i12_[1])
            and
            (
                    line_index_0 == i12_[0] or
                    line_index_0 == i12_[1] or
                    line_index_1 == i12_[0] or
                    line_index_1 == i12_[1]
            ),
            line_indices
        )
    )

    return connections
