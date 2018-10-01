def one_or_more(
    schema: dict, unique_items: bool =  True, min: int = 1, max: int = None
    ) -> dict:
    """Helper function to construct a schema that validates items matching 
    `schema` or an array containing items
    
    Arguments:
        schema {dict} -- The schema to use
    
    Keyword Arguments:
        unique_items {bool} -- Flag if array items should be unique (default: {True})
        min {int} -- Correlates to ``minLength`` attribute of JSON Schema array (default: {1})
        max {int} -- Correlates to ``maxLength`` attribute of JSON Schema array (default: {None})
    
    Returns:
        dict -- [description]
    """

    multi_schema = {
        "type": "array",
        "items": schema,
        "minItems": min,
        "uniqueItems": unique_items,
    }

    if max:
        multi_schema["maxItems"] = max

    return {"oneOf": [multi_schema, schema]}

def list_to_commas(list_of_args) -> str:
    """Convert a list of items to a comma separated list. If ``lis_of_args`` 
    is not a list, just return it back 
    
    Arguments:
        list_of_args {[type]} -- List of items
    
    Returns:
        str -- A string representing a comma separated list
    """

    if isinstance(list_of_args, list):
        return ",".join(list_of_args)

    return list_of_args
