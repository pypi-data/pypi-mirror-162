from hsmodels.schemas import enums, fields
from hsmodels.utils import to_coverage_dict


def parse_spatial_reference(cls, value):
    if not value:
        return value
    # This is a workaround for form submissions that do not include type
    if isinstance(value, dict) and "type" not in value:
        if "north" in value or "east" in value:
            # it's a type point
            value["type"] = "point"
        else:
            value["type"] = "box"
    if value['type'] == enums.SpatialReferenceType.box:
        return fields.BoxSpatialReference(**to_coverage_dict(value['value']))
    if value['type'] == enums.SpatialReferenceType.point:
        return fields.PointSpatialReference(**to_coverage_dict(value['value']))
    return value


def parse_multidimensional_spatial_reference(cls, value):
    # This is a workaround for form submissions that do not include type
    if isinstance(value, dict) and "type" not in value:
        if "north" in value or "east" in value:
            # it's a type point
            value["type"] = "point"
        else:
            value["type"] = "box"
    if value['type'] == enums.MultidimensionalSpatialReferenceType.box:
        d = to_coverage_dict(value['value'])
        return fields.MultidimensionalBoxSpatialReference(**d)
    if value['type'] == enums.MultidimensionalSpatialReferenceType.point:
        d = to_coverage_dict(value['value'])
        return fields.MultidimensionalPointSpatialReference(**d)
    return value


def parse_identifier(cls, value):
    if isinstance(value, dict) and "hydroshare_identifier" in value:
        return value['hydroshare_identifier']
    return value


def parse_spatial_coverage(cls, value):
    # This is a workaround for form submissions that do not include type
    if isinstance(value, dict) and "type" not in value:
        if "north" in value or "east" in value:
            # it's a type point
            value["type"] = "point"
        else:
            value["type"] = "box"
    return value


def list_not_empty(cls, l):
    if len(l) == 0:
        raise ValueError("list must contain at least one entry")
    return l


def validate_user_id(value):
    """Validate that value is a valid id for a hydroshare user."""
    err_message = '%s is not a valid id for hydroshare user' % value
    if value:
        try:
            user_id = value
        except ValueError:
            raise ValueError(err_message)
    return value
