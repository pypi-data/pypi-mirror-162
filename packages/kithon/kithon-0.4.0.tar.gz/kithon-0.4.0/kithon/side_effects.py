from .types import type_eval


def side_effect(effects, parts):
    ...

def set_el_type(obj, _type='None'):
    obj.type.el_type = _type

def set_type(obj, _type='None'):
    if 'own' in obj.parts:
        obj.env.variables[obj.parts['own']] = _type
    obj.type = _type

def set_as_mut(obj):
    obj.env.variables[obj.own]['immut'] = False

def type_conversion(obj, _type):
    """
    converse obj.type to _type
    """
    if isinstance(_type, str):
        obj.type = _type
        obj.env.variables[obj.own]['type'] = _type
    else:
        type = type_eval(_type)
        if obj.type.name:
            pass

side_effects = {
    'set_el_type': set_el_type,
    'set_as_mut': set_as_mut,
    'set_type': set_type
}
