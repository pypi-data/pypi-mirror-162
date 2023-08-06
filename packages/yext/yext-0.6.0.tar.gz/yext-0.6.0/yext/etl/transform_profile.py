from jsonpath_ng import jsonpath, parse
from typing import List, Optional
from .mapping import Mapping

def transform_profile(source_profile: dict, mappings: List[dict], 
                      base_profile: Optional[dict] = None) -> dict:
    '''
    Transform a raw JSON profile into Knowledge Graph JSON via mappings.
    
    Args:
    ----
        source_profile: dict
            The profile from the source system. This is completely arbitrary
            JSON; there is no schema. 
        mappings: List[dict]
            A list of mappings. These can either be provided as dictionaries 
            of Mapping objects. See mapping.py for schema.
        base_profile: Optional[dict]
            A starting point for the profile that contains fields that aren't 
            necessarily from the source system. For example, you might put a 
            label on all entities. That belongs in the base profile.
    '''
    transformed_profile = base_profile if base_profile else {}
    mappings = [Mapping(**mapping) for mapping in mappings]
    for mapping in mappings:
        source_field = mapping.source_field
        kg_field = mapping.kg_field
        transformer = mapping.transform
        required = mapping.required
        jsonpath_expr = parse(source_field)
        raw_field = [match.value for match in jsonpath_expr.find(source_profile)]
        if not raw_field:
            if required:
                raise ValueError(f'Could not find matches for this path: {source_field}')
            else:
                continue
        else:
            raw_field = raw_field[0]
        transformed_value = transformer(raw_field)
        transformed_profile[kg_field] = transformed_value
    return transformed_profile