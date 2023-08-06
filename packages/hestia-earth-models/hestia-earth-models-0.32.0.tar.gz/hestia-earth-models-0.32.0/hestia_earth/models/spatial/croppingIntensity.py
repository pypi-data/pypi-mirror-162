from hestia_earth.schema import MeasurementStatsDefinition

from hestia_earth.models.log import logRequirements, logShouldRun
from hestia_earth.models.utils.measurement import _new_measurement
from .utils import download, find_existing_measurement, get_region_factor, has_geospatial_data
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "or": [
            {"latitude": "", "longitude": ""},
            {"boundary": {}},
            {"region": {"@type": "Term", "termType": "region"}}
        ]
    }
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "statsDefinition": "spatial"
    }]
}
LOOKUPS = {
    "region-measurment": "croppingIntensity"
}
TERM_ID = 'croppingIntensity'
EE_PARAMS = {
    'ee_type': 'raster',
    'reducer': 'sum',
    'fields': 'sum'
}


def _measurement(value: float):
    measurement = _new_measurement(TERM_ID, MODEL)
    measurement['value'] = [round(value, 7)]
    measurement['statsDefinition'] = MeasurementStatsDefinition.SPATIAL.value
    return measurement


def _download(site: dict):
    # 1) extract maximum monthly growing area (MMGA)
    MMGA_value = download(
        TERM_ID,
        site,
        {
            **EE_PARAMS,
            'collection': 'MMGA'
        }
    )
    MMGA_value = MMGA_value.get(EE_PARAMS['reducer'], 0)

    # 2) extract area harvested (AH)
    AH_value = download(
        TERM_ID,
        site,
        {
            **EE_PARAMS,
            'collection': 'AH'
        }
    )
    AH_value = AH_value.get(EE_PARAMS['reducer'])

    # 3) estimate croppingIntensity from MMGA and AH.
    return None if MMGA_value is None or AH_value is None or AH_value == 0 else (MMGA_value / AH_value)


def _run(site: dict):
    value = find_existing_measurement(TERM_ID, site) or _download(site) or get_region_factor(TERM_ID, site)
    return [_measurement(value)] if value is not None else []


def _should_run(site: dict):
    geospatial_data = has_geospatial_data(site)

    logRequirements(site, model=MODEL, term=TERM_ID,
                    geospatial_data=geospatial_data)

    should_run = all([geospatial_data])
    logShouldRun(site, MODEL, TERM_ID, should_run)
    return should_run


def run(site: dict): return _run(site) if _should_run(site) else []
