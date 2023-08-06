from enum import Enum

from hsmodels.namespaces import DCTERMS, HSTERMS


class StringEnum(str, Enum):
    pass


class TermEnum(StringEnum):
    pass


class CoverageType(TermEnum):
    period = str(DCTERMS.period)
    box = str(DCTERMS.box)
    point = str(DCTERMS.point)


class SpatialReferenceType(TermEnum):
    point = str(HSTERMS.point)
    box = str(HSTERMS.box)


class MultidimensionalSpatialReferenceType(TermEnum):
    point = str(DCTERMS.point)
    box = str(DCTERMS.box)


class VariableType(StringEnum):
    Char = 'Char'  # 8-bit byte that contains uninterpreted character data
    Byte = 'Byte'  # integer(8bit)
    Short = 'Short'  # signed integer (16bit)
    Int = 'Int'  # signed integer (32bit)
    Float = 'Float'  # floating point (32bit)
    Double = 'Double'  # floating point(64bit)
    Int64 = 'Int64'  # integer(64bit)
    Unsigned_Byte = 'Unsigned Byte'
    Unsigned_Short = 'Unsigned Short'
    Unsigned_Int = 'Unsigned Int'
    Unsigned_Int64 = 'Unsigned Int64'
    String = 'String'  # variable length character string
    User_Defined_Type = 'User Defined Type'  # compound, vlen, opaque, enum
    Unknown = 'Unknown'


class UserIdentifierType(StringEnum):
    google_scholar_id = "GoogleScholarID"
    research_gate_id = "ResearchGateID"
    ORCID = "ORCID"


class RelationType(StringEnum):
    isPartOf = 'The content of this resource is part of'
    hasPart = 'This resource includes'
    isExecutedBy = 'The content of this resource can be executed by'
    isCreatedBy = 'The content of this resource was created by a related App or software program'
    isVersionOf = 'This resource updates and replaces a previous version'
    isReplacedBy = 'This resource has been replaced by a newer version'
    isDescribedBy = 'This resource is described by'
    conformsTo = 'This resource conforms to established standard described by'
    hasFormat = 'This resource has a related resource in another format'
    isFormatOf = 'This resource is a different format of'
    isRequiredBy = 'This resource is required by'
    requires = 'This resource requires'
    isReferencedBy = 'This resource is referenced by'
    references = 'The content of this resource references'
    replaces = 'This resource replaces'
    source = 'The content of this resource is derived from'


class AggregationType(StringEnum):
    SingleFileAggregation = "Generic"
    FileSetAggregation = "FileSet"
    GeographicRasterAggregation = "GeoRaster"
    MultidimensionalAggregation = "NetCDF"
    GeographicFeatureAggregation = "GeoFeature"
    ReferencedTimeSeriesAggregation = "RefTimeseries"
    TimeSeriesAggregation = "TimeSeries"
    ModelProgramAggregation = "ModelProgram"
    ModelInstanceAggregation = "ModelInstance"


class DateType(TermEnum):
    modified = str(DCTERMS.modified)
    created = str(DCTERMS.created)
    valid = str(DCTERMS.valid)
    available = str(DCTERMS.available)
    published = str(DCTERMS.published)


class ModelProgramFileType(TermEnum):
    release_notes = str(HSTERMS.modelReleaseNotes)
    documentation = str(HSTERMS.modelDocumentation)
    software = str(HSTERMS.modelSoftware)
    engine = str(HSTERMS.modelEngine)
