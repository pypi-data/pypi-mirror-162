from hsmodels.schemas.enums import CoverageType, DateType, ModelProgramFileType, RelationType, UserIdentifierType
from hsmodels.utils import to_coverage_dict


def split_dates(cls, values):
    if "dates" in values:
        for date in values['dates']:
            if date['type'] == DateType.created:
                values["created"] = date['value']
            elif date['type'] == DateType.modified:
                values["modified"] = date['value']
            elif date['type'] == DateType.published:
                values["published"] = date['value']
        del values["dates"]
    return values


def split_coverages(cls, values):
    from hsmodels.schemas.fields import BoxCoverage, PeriodCoverage, PointCoverage

    if "coverages" in values:
        for coverage in values['coverages']:
            if coverage['type'] == CoverageType.period:
                values["period_coverage"] = PeriodCoverage(**to_coverage_dict(coverage['value']))
            elif coverage['type'] == CoverageType.box:
                values["spatial_coverage"] = BoxCoverage(**to_coverage_dict(coverage['value']))
            elif coverage['type'] == CoverageType.point:
                values["spatial_coverage"] = PointCoverage(**to_coverage_dict(coverage['value']))
        del values["coverages"]
    return values


def parse_additional_metadata(cls, values):
    if "extended_metadata" in values:
        value = values["extended_metadata"]
        if isinstance(value, list):
            parsed = {}
            for em in value:
                parsed[em['key']] = em['value']
            values["additional_metadata"] = parsed
            del values["extended_metadata"]
    return values


def parse_abstract(cls, values):
    if "description" in values:
        value = values["description"]
        if isinstance(value, dict) and "abstract" in value:
            values['abstract'] = value['abstract']
            del values['description']
    return values


def parse_utc_offset_value(cls, values):
    if "utc_offset" in values:
        value = values["utc_offset"]
        if isinstance(value, dict) and "value" in value:
            values["value"] = value["value"]
            del values["utc_offset"]
    return values


def parse_url(cls, values):
    if "rdf_subject" in values:
        value = values["rdf_subject"]
        if value:
            values["url"] = values["rdf_subject"]
            del values["rdf_subject"]
    return values


def parse_relation(cls, values):
    if "type" in values or "value" in values:
        return values
    for relation_type in RelationType:
        if relation_type.name in values and values[relation_type.name]:
            values["type"] = relation_type
            values["value"] = values[relation_type.name]
            return values


def group_user_identifiers(cls, values):
    if "identifiers" not in values:
        identifiers = {}
        for identifier in UserIdentifierType:
            if identifier.name in values and values[identifier.name]:
                identifiers[identifier] = values[identifier.name]
        values["identifiers"] = identifiers
    return values


def parse_file_types(cls, values):
    if "file_types" not in values:
        file_types_list = []
        for file_type in ModelProgramFileType:
            if file_type.name in values:
                ftypes = values[file_type.name]
                if isinstance(ftypes, list):
                    for ftype in ftypes:
                        file_types_list.append({"type": file_type, "url": ftype})
                    del values[file_type.name]
        values['file_types'] = file_types_list
    return values


def normalize_additional_metadata(cls, values):
    if "additional_metadata" in values:
        value = values["additional_metadata"]
        if isinstance(value, list):
            as_dict = {}
            for val in value:
                if not isinstance(val, dict):
                    raise ValueError(f"List entry {val} must be a dict")
                if "key" not in val:
                    raise ValueError(f"Missing the 'key' key in {val}")
                if "value" not in val:
                    raise ValueError(f"Missing the 'value' key in {val}")
                if val["key"] in as_dict:
                    raise ValueError(f"Found a duplicate key {val['key']}")
                as_dict[val["key"]] = val["value"]
            values["additional_metadata"] = as_dict
    return values
