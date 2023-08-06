from asciimatics import widgets
from asciimatics.screen import Screen

import asciimatics.event

from asciimatics import exceptions

from bs_monitor.tui import tui_util
from bs_monitor.tui.pod_tui import PodTui


class MainMenu(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(MainMenu, self).__init__(
            screen, 10, 40, on_load=self._load_menu, has_shadow=True, hover_focus=True, can_scroll=False,
            reduce_cpu=True, title="Monitor Main Menu"
        )

        self._pod = pod
        self._key_ords = tui_util.get_ords('123456q')

        layout = widgets.Layout([100], fill_frame=True)

        self._options = [
            ("1. Job Instances", "JobInstEnquiry"),
            ("2. Batch Instances", "BatchInstEnquiry"),
            ("3. Batches", "BatchEnquiry"),
            ("4. Jobs", "JobEnquiry"),
            ("5. Dates", "MondateEnquiry"),
            ("6. Change Theme", "ChangeTheme"),
            (f"{tui_util.KEY_HINT_HELP}. Help", "Help"),
            (f"{tui_util.KEY_HINT_QUIT}. Quit", "Quit"),
        ]

        self.add_layout(layout)

        self._menu_list = widgets.ListBox(
            widgets.Widget.FILL_FRAME,
            self._options,
            name="main_menu",
            add_scroll_bar=True,
            on_select=self._select_option)

        layout.add_widget(self._menu_list)
        self.fix()

    def _load_menu(self, new_value=None):
        self.set_theme(self._pod.theme)
        self._menu_list.options = self._options
        self._menu_list.value = new_value

    def process_event(self, event):
        if isinstance(event, asciimatics.event.KeyboardEvent):
            if tui_util.handle_f_keys(self._screen, self._scene, event):
                return

            if event.key_code == tui_util.KEY_BACK:
                tui_util.handle_f_keys(self._screen, self._scene, asciimatics.event.KeyboardEvent(tui_util.KEY_QUIT))
                return

            if event.key_code in self._key_ords['6']:
                self._change_theme()
                return

            if event.key_code in self._key_ords['1']:
                raise exceptions.NextScene(self._options[0][1])

            if event.key_code in self._key_ords['2']:
                raise exceptions.NextScene(self._options[1][1])

            if event.key_code in self._key_ords['3']:
                raise exceptions.NextScene(self._options[2][1])

            if event.key_code in self._key_ords['4']:
                raise exceptions.NextScene(self._options[3][1])

            if event.key_code in self._key_ords['5']:
                raise exceptions.NextScene(self._options[4][1])

            if event.key_code in self._key_ords['6']:
                self._change_theme()
                return

        return super(MainMenu, self).process_event(event)

    def _select_option(self):
        self.save()

        if self.data['main_menu'] == 'Help':
            tui_util.handle_f_keys(self._screen, self._scene, asciimatics.event.KeyboardEvent(tui_util.KEY_HELP))
            return

        if self.data['main_menu'] == 'Quit':
            tui_util.handle_f_keys(self._screen, self._scene, asciimatics.event.KeyboardEvent(tui_util.KEY_QUIT))

        if self.data['main_menu'] == 'ChangeTheme':
            self._change_theme()
            return

        raise exceptions.NextScene(self.data['main_menu'])

    def _change_theme(self) -> None:
        options = [
            ("Default", self._set_theme_default),
            ("Green", self._set_theme_green),
            ("Monochrome", self._set_theme_mono),
            ("Bright", self._set_theme_bright),
        ]

        if self.screen.colours >= 256:
            options.append(("Red/white", self._set_theme_tlj))

        self._scene.add_effect(
            widgets.PopupMenu(self.screen, options, int(self.screen.width / 2) - 8, int(self.screen.height / 2) - 10)
        )

    def _set_theme_default(self) -> None:
        self._set_and_write_theme("default")

    def _set_theme_green(self) -> None:
        self._set_and_write_theme("green")

    def _set_theme_mono(self) -> None:
        self._set_and_write_theme("monochrome")

    def _set_theme_bright(self) -> None:
        self._set_and_write_theme("bright")

    def _set_theme_tlj(self) -> None:
        self._set_and_write_theme("tlj256")

    def _set_and_write_theme(self, theme: str) -> None:
        self.set_theme(theme)
        self._pod.write_theme(theme)
