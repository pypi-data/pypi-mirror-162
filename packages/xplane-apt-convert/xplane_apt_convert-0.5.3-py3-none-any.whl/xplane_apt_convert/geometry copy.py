from bezier.curve import Curve
from xplane_airports.AptDat import RowCode
import numpy as np


BEZIER_RESOLUTION = 15


def _calculate_quadratic_bezier(p0, p1, p2, resolution=BEZIER_RESOLUTION):
    if p0 == p2:
        return [p0]

    curve = Curve.from_nodes(np.asarray([p0, p1, p2]).T)
    curve_points = curve.evaluate_multi(np.linspace(0.0, 1.0, resolution))

    return curve_points.T.tolist()


def _calculate_cubic_bezier(p0, p1, p2, p3, resolution=BEZIER_RESOLUTION):
    if p0 == p3:
        return [p0]

    curve = Curve.from_nodes(np.asarray([p0, p1, p2, p3]).T)
    curve_points = curve.evaluate_multi(np.linspace(0.0, 1.0, resolution))

    return curve_points.T.tolist()


def _calculate_bezier(p0, p1, p2, p3=None, resolution=BEZIER_RESOLUTION):
    if p3 is None:
        return _calculate_quadratic_bezier(p0, p1, p2)
    else:
        return _calculate_cubic_bezier(p0, p1, p2, p3)


def get_path(row_iterator):
    def _process_row(is_bezier, tokens):
        nonlocal in_bezier, temp_bezier_nodes, coordinates, properties

        lat, lon = float(tokens[1]), float(tokens[2])

        if not is_bezier:
            if len(tokens) > 3:
                properties["painted_line_type"] = int(tokens[3])
            if len(tokens) > 4:
                properties["lighting_line_type"] = int(tokens[4])

            if in_bezier:
                temp_bezier_nodes.append((lon, lat))
                coordinates.extend(_calculate_bezier(*temp_bezier_nodes))
                temp_bezier_nodes = []
            else:
                coordinates.append((lon, lat))

            in_bezier = False

        else:
            bzp_lat, bzp_lon = float(tokens[3]), float(tokens[4])

            if len(tokens) > 5:
                properties["painted_line_type"] = int(tokens[5])
            if len(tokens) > 6:
                properties["lighting_line_type"] = int(tokens[6])

            if in_bezier:
                diff_lat = bzp_lat - lat
                diff_lon = bzp_lon - lon
                mirr_lat = lat - diff_lat
                mirr_lon = lon - diff_lon

                temp_bezier_nodes.append((mirr_lon, mirr_lat))
                temp_bezier_nodes.append((lon, lat))
                coordinates.extend(_calculate_bezier(*temp_bezier_nodes))
                temp_bezier_nodes = []
            else:
                if len(coordinates):
                    diff_lat = bzp_lat - lat
                    diff_lon = bzp_lon - lon
                    mirr_lat = lat - diff_lat
                    mirr_lon = lon - diff_lon

                    temp_bezier_nodes.append(coordinates[-1])
                    temp_bezier_nodes.append((mirr_lon, mirr_lat))
                    temp_bezier_nodes.append((lon, lat))
                    coordinates.extend(_calculate_bezier(*temp_bezier_nodes))
                    temp_bezier_nodes = []

            temp_bezier_nodes.append((lon, lat))
            temp_bezier_nodes.append((bzp_lon, bzp_lat))

            # else:
            in_bezier = True

    coordinates_list = []
    properties_list = []
    more_segments = True

    while more_segments:
        coordinates = []
        properties = {}
        temp_bezier_nodes = []
        in_bezier = False
        first_row = None
        first_row_is_bezier = None

        for row in row_iterator:
            if first_row is None:
                first_row = row
                first_row_is_bezier = row.row_code == RowCode.LINE_CURVE

            row_code = row.row_code
            tokens = row.tokens

            if row_code == RowCode.LINE_SEGMENT:
                _process_row(False, tokens)
            elif row_code == RowCode.LINE_CURVE:
                _process_row(True, tokens)
            elif row_code == RowCode.RING_SEGMENT:
                _process_row(False, tokens)
                _process_row(first_row_is_bezier, first_row.tokens)
                break
            elif row_code == RowCode.RING_CURVE:
                _process_row(True, tokens)
                _process_row(first_row_is_bezier, first_row.tokens)
                break
            elif row_code == RowCode.END_SEGMENT:
                _process_row(False, tokens)
                break
            elif row_code == RowCode.END_CURVE:
                _process_row(True, tokens)
                break
            else:
                # raise ValueError(f"Unexpected row code {row.row_code}")
                row_iterator.unnext()
                more_segments = False
                break
        else:
            # there is no more rows
            more_segments = False

        if len(coordinates) > 0:
            coordinates_list.append(coordinates)
            properties_list.append(properties)

    return coordinates_list, properties_list


def get_path_features(row_iterator):
    # https://forums.x-plane.org/index.php?/forums/topic/66713-understanding-the-logic-of-bezier-control-points-in-aptdat/

    # TODO: One same line can have different line styles (different properties), should be split into different features.
    # features = []

    coordinates, properties = get_path(row_iterator)

    assert len(coordinates) == len(properties)

    # props.update(
    #     {
    #         "type": "line",
    #     }
    # )

    # linear_feature = geojson.Feature(geometry=line, properties=props)
    # feature = {
    #     "geometry": {
    #         "type": "LineString",
    #         "coordinates": node_paths[0],
    #     },
    #     "properties": {},
    # }

    # features.append(feature)

    return coordinates, properties
