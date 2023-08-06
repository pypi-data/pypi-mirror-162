from datetime import date, datetime
from typing import List

from pydantic import AnyUrl, Field, root_validator

from hsmodels.namespaces import DC, HSTERMS, RDF
from hsmodels.schemas.rdf.fields import (
    BandInformationInRDF,
    CellInformationInRDF,
    CoverageInRDF,
    DescriptionInRDF,
    ExtendedMetadataInRDF,
    FieldInformationInRDF,
    GeometryInformationInRDF,
    MultidimensionalSpatialReferenceInRDF,
    RDFBaseModel,
    RightsInRDF,
    SpatialReferenceInRDF,
    TimeSeriesResultInRDF,
    VariableInRDF,
)
from hsmodels.schemas.rdf.root_validators import (
    parse_coverages,
    parse_rdf_extended_metadata,
    parse_rdf_multidimensional_spatial_reference,
    parse_rdf_spatial_reference,
    rdf_parse_description,
    rdf_parse_file_types,
    rdf_parse_rdf_subject,
)


class BaseAggregationMetadataInRDF(RDFBaseModel):
    _parse_rdf_subject = root_validator(pre=True, allow_reuse=True)(rdf_parse_rdf_subject)

    title: str = Field(rdf_predicate=DC.title)
    subjects: List[str] = Field(rdf_predicate=DC.subject, default=[])
    language: str = Field(rdf_predicate=DC.language, default="eng")
    extended_metadata: List[ExtendedMetadataInRDF] = Field(rdf_predicate=HSTERMS.extendedMetadata, default=[])
    coverages: List[CoverageInRDF] = Field(rdf_predicate=DC.coverage, default=[])
    rights: RightsInRDF = Field(rdf_predicate=DC.rights, default=[])

    _parse_coverages = root_validator(pre=True, allow_reuse=True)(parse_coverages)

    _parse_extended_metadata = root_validator(pre=True, allow_reuse=True)(parse_rdf_extended_metadata)


class GeographicRasterMetadataInRDF(BaseAggregationMetadataInRDF):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.GeographicRasterAggregation)

    label: str = Field(
        const=True,
        default="Geographic Raster Content: A geographic grid represented by a virtual "
        "raster tile (.vrt) file and one or more geotiff (.tif) files",
    )
    dc_type: AnyUrl = Field(rdf_predicate=DC.type, default=HSTERMS.GeographicRasterAggregation, const=True)

    band_information: BandInformationInRDF = Field(rdf_predicate=HSTERMS.BandInformation)
    spatial_reference: SpatialReferenceInRDF = Field(rdf_predicate=HSTERMS.spatialReference, default=None)
    cell_information: CellInformationInRDF = Field(rdf_predicate=HSTERMS.CellInformation)

    _parse_spatial_reference = root_validator(pre=True, allow_reuse=True)(parse_rdf_spatial_reference)


class GeographicFeatureMetadataInRDF(BaseAggregationMetadataInRDF):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.GeographicFeatureAggregation)

    label: str = Field(
        const=True, default="Geographic Feature Content: The multiple files that are part of a " "geographic shapefile"
    )
    dc_type: AnyUrl = Field(rdf_predicate=DC.type, default=HSTERMS.GeographicFeatureAggregation, const=True)

    field_information: List[FieldInformationInRDF] = Field(rdf_predicate=HSTERMS.FieldInformation, default=[])
    geometry_information: GeometryInformationInRDF = Field(rdf_predicate=HSTERMS.GeometryInformation)
    spatial_reference: SpatialReferenceInRDF = Field(rdf_predicate=HSTERMS.spatialReference, default=None)

    _parse_spatial_reference = root_validator(pre=True, allow_reuse=True)(parse_rdf_spatial_reference)


class MultidimensionalMetadataInRDF(BaseAggregationMetadataInRDF):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.MultidimensionalAggregation)

    label: str = Field(
        const=True,
        default="Multidimensional Content: A multidimensional dataset represented by a "
        "NetCDF file (.nc) and text file giving its NetCDF header content",
    )
    dc_type: AnyUrl = Field(rdf_predicate=DC.type, default=HSTERMS.MultidimensionalAggregation, const=True)

    variables: List[VariableInRDF] = Field(rdf_predicate=HSTERMS.Variable, default=[])
    spatial_reference: MultidimensionalSpatialReferenceInRDF = Field(
        rdf_predicate=HSTERMS.spatialReference, default=None
    )

    _parse_spatial_reference = root_validator(pre=True, allow_reuse=True)(parse_rdf_multidimensional_spatial_reference)


class TimeSeriesMetadataInRDF(BaseAggregationMetadataInRDF):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.TimeSeriesAggregation)

    label: str = Field(
        const=True,
        default="Time Series Content: One or more time series held in an ODM2 format "
        "SQLite file and optional source comma separated (.csv) files",
    )
    dc_type: AnyUrl = Field(rdf_predicate=DC.type, default=HSTERMS.TimeSeriesAggregation, const=True)
    description: DescriptionInRDF = Field(rdf_predicate=DC.description, default_factory=DescriptionInRDF)

    time_series_results: List[TimeSeriesResultInRDF] = Field(rdf_predicate=HSTERMS.timeSeriesResult, default=[])

    _parse_description = root_validator(pre=True, allow_reuse=True)(rdf_parse_description)


class ReferencedTimeSeriesMetadataInRDF(BaseAggregationMetadataInRDF):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.ReferencedTimeSeriesAggregation)

    label: str = Field(
        const=True,
        default="Referenced Time Series Content: A reference to one or more time series "
        "served from HydroServers outside of HydroShare in WaterML format",
    )
    dc_type: AnyUrl = Field(rdf_predicate=DC.type, default=HSTERMS.ReferencedTimeSeriesAggregation, const=True)


class FileSetMetadataInRDF(BaseAggregationMetadataInRDF):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.FileSetAggregation)

    label: str = Field(const=True, default="File Set Content: One or more files with specific metadata")
    dc_type: AnyUrl = Field(rdf_predicate=DC.type, default=HSTERMS.FileSetAggregation, const=True)


class SingleFileMetadataInRDF(BaseAggregationMetadataInRDF):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.SingleFileAggregation)

    label: str = Field(const=True, default="Single File Content: A single file with file specific metadata")
    dc_type: AnyUrl = Field(rdf_predicate=DC.type, default=HSTERMS.SingleFileAggregation, const=True)


class ModelProgramMetadataInRDF(BaseAggregationMetadataInRDF):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.ModelProgramAggregation)

    label: str = Field(const=True, default="Model Program Content: One or more files with specific metadata")
    dc_type: AnyUrl = Field(rdf_predicate=DC.type, default=HSTERMS.ModelProgramAggregation, const=True)

    name: str = Field(rdf_predicate=HSTERMS.modelProgramName, default=None)
    version: str = Field(rdf_predicate=HSTERMS.modelVersion, default=None)
    programming_languages: List[str] = Field(rdf_predicate=HSTERMS.modelProgramLanguage, default=[])
    operating_systems: List[str] = Field(rdf_predicate=HSTERMS.modelOperatingSystem, default=[])
    release_date: date = Field(rdf_predicate=HSTERMS.modelReleaseDate, default=None)
    website: AnyUrl = Field(rdf_predicate=HSTERMS.modelWebsite, default=None)
    code_repository: AnyUrl = Field(rdf_predicate=HSTERMS.modelCodeRepository, default=None)
    program_schema_json: AnyUrl = Field(rdf_predicate=HSTERMS.modelProgramSchema, default=None)

    release_notes: List[str] = Field(rdf_predicate=HSTERMS.modelReleaseNotes, default=[])
    documentation: List[str] = Field(rdf_predicate=HSTERMS.modelDocumentation, default=[])
    software: List[str] = Field(rdf_predicate=HSTERMS.modelSoftware, default=[])
    engine: List[str] = Field(rdf_predicate=HSTERMS.modelEngine, default=[])

    _parse_file_types = root_validator(pre=True, allow_reuse=True)(rdf_parse_file_types)


class ModelInstanceMetadataInRDF(BaseAggregationMetadataInRDF):
    rdf_type: AnyUrl = Field(rdf_predicate=RDF.type, const=True, default=HSTERMS.ModelInstanceAggregation)

    label: str = Field(const=True, default="Model Instance Content: One or more files with specific metadata")
    dc_type: AnyUrl = Field(rdf_predicate=DC.type, default=HSTERMS.ModelInstanceAggregation, const=True)

    includes_model_output: bool = Field(rdf_predicate=HSTERMS.includesModelOutput)
    executed_by: AnyUrl = Field(rdf_predicate=HSTERMS.executedByModelProgram, default=None)
    program_schema_json: AnyUrl = Field(rdf_predicate=HSTERMS.modelProgramSchema, default=None)
    program_schema_json_values: AnyUrl = Field(rdf_predicate=HSTERMS.modelProgramSchemaValues, default=None)
