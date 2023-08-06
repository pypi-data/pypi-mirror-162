# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class CheckboxTree(Component):
    """A CheckboxTree component.


Keyword arguments:

- id (string; optional):
    The ID of this component, used to identify dash components  in
    callbacks. The ID needs to be unique across all of the  components
    in an app.

- checked (list of string | numbers; optional):
    An array of checked node values.

- className (string; optional):
    Often used with CSS to style elements with common properties.

- disabled (boolean; default False):
    If True, the component will be disabled and nodes cannot be
    checked.

- expandDisabled (boolean; default False):
    If True, the ability to expand nodes will be disabled.

- expandOnClick (boolean; default False):
    If True, nodes will be expanded by clicking on labels. Requires  a
    non-empty onClick function.

- expanded (list of string | numbers; optional):
    An array of expanded node values.

- loading_state (dict; optional):
    Object that holds the loading state object coming from
    dash-renderer.

    `loading_state` is a dict with keys:

    - component_name (string; optional):
        Holds the name of the component that is loading.

    - is_loading (boolean; optional):
        Determines if the component is loading or not.

    - prop_name (string; optional):
        Holds which property is loading.

- name (string; default ''):
    Optional name for the hidden <input> element.

- nameAsArray (boolean; default False):
    If True, the hidden <input> will encode its values as an array
    rather than a joined string.

- nativeCheckboxes (boolean; default False):
    If True, native browser checkboxes will be used insted of
    pseudo-checkbox icons.

- noCascade (boolean; default False):
    If True, toggling a parent node will not cascade its check state
    to its children.

- nodes (list of dicts; optional):
    The children of this component.

    `nodes` is a list of dicts with keys:

    - className (string; optional):
        A classname to add to the node.

    - disabled (boolean; optional):
        Whether the node should be disabled.

    - icon (string; optional):
        An icon tag. Default: star.

    - label (string | number; required):
        The node label.

    - showCheckbox (boolean; optional):
        Whether the node should show a checkbox.

    - value (string | number; required):
        The node value.

- onlyLeafCheckboxes (boolean; default False):
    If True, checkboxes will only be shown for leaf nodes.

- optimisticToggle (boolean; default True):
    If True, toggling a partially-checked node will select all
    children.  If False, it will deselect.

- showNodeIcon (boolean; default True):
    If True, each node will show a parent or leaf icon.

- style (dict; optional):
    Defines CSS styles which will override styles previously set."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'checkbox_tree'
    _type = 'CheckboxTree'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, nodes=Component.UNDEFINED, checked=Component.UNDEFINED, expanded=Component.UNDEFINED, disabled=Component.UNDEFINED, expandDisabled=Component.UNDEFINED, expandOnClick=Component.UNDEFINED, name=Component.UNDEFINED, nameAsArray=Component.UNDEFINED, nativeCheckboxes=Component.UNDEFINED, noCascade=Component.UNDEFINED, onlyLeafCheckboxes=Component.UNDEFINED, optimisticToggle=Component.UNDEFINED, showNodeIcon=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'checked', 'className', 'disabled', 'expandDisabled', 'expandOnClick', 'expanded', 'loading_state', 'name', 'nameAsArray', 'nativeCheckboxes', 'noCascade', 'nodes', 'onlyLeafCheckboxes', 'optimisticToggle', 'showNodeIcon', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'checked', 'className', 'disabled', 'expandDisabled', 'expandOnClick', 'expanded', 'loading_state', 'name', 'nameAsArray', 'nativeCheckboxes', 'noCascade', 'nodes', 'onlyLeafCheckboxes', 'optimisticToggle', 'showNodeIcon', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(CheckboxTree, self).__init__(**args)
