from hestia_earth.schema import SchemaType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.tools import non_empty_value
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name

from ..log import debugValues
from . import _term_id, _include_methodModel
from .lookup import _ALLOW_ALL


def _new_emission(term, model=None):
    node = {'@type': SchemaType.EMISSION.value}
    node['term'] = linked_node(term if isinstance(term, dict) else download_hestia(_term_id(term)))
    return _include_methodModel(node, model)


def _model_lookup_values(model: str, term_id: str, restriction: str):
    lookup = download_lookup(f"emission-model-{restriction}.csv")
    values = get_table_value(lookup, 'termid', term_id, column_name(model))
    return (values or _ALLOW_ALL).split(';')


def _is_siteType_allowed(model: str, term_id: str, data: dict):
    site = data if data.get('@type', data.get('type')) == 'Site' else data.get('site', {})
    site_type = site.get('siteType')
    allowed_values = _model_lookup_values(model, term_id, 'siteTypesAllowed')
    return True if _ALLOW_ALL in allowed_values or not site_type else site_type in allowed_values


def _run_model_required(model: str, term_id: str, data: dict):
    siteType_allowed = _is_siteType_allowed(model, term_id, data)

    run_required = all([siteType_allowed])
    debugValues(data, model=model, term=term_id,
                run_required=run_required,
                siteType_allowed=siteType_allowed)
    return run_required


def _default_emission(model: str, term_id: str, data: dict, returns_data: dict):
    node_type = data.get('@type', data.get('type'))
    return_data = returns_data.get('Emission', [{"value": [0]}])[0]
    # need to keep only keys with a value
    return_data = {k: v for k, v in return_data.items() if non_empty_value(v)}
    return [{
        **_new_emission(term_id, model),
        **return_data,
        'value': [0]
    }] if node_type != SchemaType.TRANSFORMATION.value else []
