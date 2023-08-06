import json

import asciimatics
from asciimatics.event import KeyboardEvent
from asciimatics.scene import Scene
from asciimatics.screen import Screen

ALL_CAPTION = "<ALL>"
NONE_CAPTION = "<NONE>"
WTF_CAPTION = "<???>"
NO_YES_OPTIONS = ["No", "Yes"]

KEY_HELP = Screen.KEY_F1
KEY_EDIT = Screen.KEY_F2
KEY_SAVE = Screen.KEY_F4
KEY_REFRESH = Screen.KEY_F5
KEY_RESET = Screen.KEY_F6
KEY_BACK = Screen.KEY_F3
KEY_QUIT = Screen.KEY_F10
KEY_CREATE = Screen.KEY_INSERT
KEY_DELETE = Screen.KEY_DELETE

KEY_HINT_HELP = 'F1'
KEY_HINT_EDIT = 'F2'
KEY_HINT_SAVE = 'F4'
KEY_HINT_REFRESH = 'F5'
KEY_HINT_RESET = 'F6'
KEY_HINT_BACK = 'F3'
KEY_HINT_QUIT = 'F10'
KEY_HINT_CREATE = 'INS'
KEY_HINT_DELETE = 'DEL'


def get_ords(chs: str) -> dict:
    res = {}

    for x in chs:
        if x.isalpha():
            res[x] = { ord(x), ord(x.upper()) }

        else:
            res[x] = { ord(x) }

    return res


def assign_diff(obj1, obj2, attr: str, type_conv = None) -> bool:
    if isinstance(obj1, dict):
        v1 = obj1[attr]
    else:
        v1 = getattr(obj1, attr)

    if isinstance(obj2, dict):
        v2 = obj2[attr]
    else:
        v2 = getattr(obj2, attr)

    if type_conv:
        if type_conv == dict:
            if v1 and not isinstance(v1, dict):
                v1 = json.loads(v1)

            if v2 and not isinstance(v2, dict):
                v2 = json.loads(v2)
        else:
            if v1 is not None:
                v1 = type_conv(v1)

            if v2 is not None:
                v2 = type_conv(v2)

    if v1 == v2:
        return False

    if isinstance(obj1, dict):
        obj1[attr] = v2
    else:
        setattr(obj1, attr, v2)

    return True


def validator_alpha() -> str:
    return "^[a-zA-Z]*$"


def validator_numeric() -> str:
    return "^[0-9]*$"


def validator_json(value: str) -> bool:
    if not value:
        return True

    try:
        json.loads(value)
    except Exception:
        return False

    return True


def couplet_to_dropdown(cplt: dict, add_all: bool = True, add_none: bool = False) -> list:
    res = []

    if add_all:
        res.append((ALL_CAPTION, None))
    elif add_none:
        res.append((NONE_CAPTION, None))

    keys = list(cplt.keys())
    keys.sort()

    for key in keys:
        res.append((cplt[key], key))

    return res


def pop_exception(screen, ex: Exception) -> str:
    from asciimatics import widgets

    text = f'!! ERROR !!\n\n{ex}'
    return widgets.PopUpDialog(screen, text, ["OK"], has_shadow=True)


def handle_f_keys(screen: Screen, scene: Scene, event: KeyboardEvent) -> bool:
    if event.key_code == Screen.KEY_F1:
        text = f"""HELP / SHORTCUTS

{KEY_HINT_HELP}     : This help
{KEY_HINT_EDIT}     : Edit Record
{KEY_HINT_BACK}     : Back to previous screen / Cancel
{KEY_HINT_SAVE}     : Save Record
{KEY_HINT_REFRESH}     : Refresh current grid (if applicable)
{KEY_HINT_RESET}     : Reset search criteria (if applicable)

{KEY_HINT_CREATE}    : Insert/Create a new record (if applicable)
{KEY_HINT_DELETE}    : Delete the current record (if applicable)

ENTER/ :
SPACE  : Pressing enter or space on any grid item will refresh just that row

{KEY_HINT_QUIT}    : Quit

"""

        pop = asciimatics.widgets.PopUpDialog(screen, text, ["OK"], has_shadow=True)
        scene.add_effect(pop)
        return True

    if event.key_code == Screen.KEY_F10:
        raise asciimatics.exceptions.StopApplication("User quit")
