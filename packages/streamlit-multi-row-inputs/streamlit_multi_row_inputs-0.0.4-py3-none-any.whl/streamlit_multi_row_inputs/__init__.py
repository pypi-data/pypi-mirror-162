from dataclasses import dataclass, asdict
import os
from enum import IntEnum
from typing import Any, List, Dict

import streamlit.components.v1 as components

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_multi_row_inputs",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_multi_row_inputs", path=build_dir)


# --------------------------------------------
# Actual Code

class InputType(IntEnum):
    SHORT_TEXT = 0
    LONG_TEXT = 1
    DATE = 2
    TIME = 3
    DATETIME = 4


@dataclass
class InputInfo():
    type: InputType
    label: str
    weight: int
    line: int


def multi_row_inputs(label, input_info: List[InputInfo], line_num=1, default_list: List[List[Any]]=None, key=None):
    """Create a new instance of "multi_row_inputs".

    Parameters
    ----------
    label: str
        The name of the instantiated component.
    
    input_types: IntEnum
        List of types of each column.
        Currently, textarea, date, and time type are supported.

    default_list: List[List[Any]]
        List of default values.
        Values should be sorted as same order as `input_types`.

    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    List[List]
        List of inputs

    """
    component_value = _component_func(label=label, input_types=list(map(asdict, input_info)), line_num=line_num, key=key, default=default_list)

    return component_value

# --------------------------------------------


if not _RELEASE:
    import streamlit as st

    st.subheader("Multi String Component")
    num_clicks = multi_row_inputs("wow", [
            InputInfo(InputType.LONG_TEXT, "Event", 2, 0),
            InputInfo(InputType.SHORT_TEXT, "Location", 1, 0),
            InputInfo(InputType.DATETIME, "datetime", 1, 1)
        ], line_num=2, default_list=[["Free time", "Del pino resort"]], key="foo")
    
    for i in num_clicks:
        st.write(i)
