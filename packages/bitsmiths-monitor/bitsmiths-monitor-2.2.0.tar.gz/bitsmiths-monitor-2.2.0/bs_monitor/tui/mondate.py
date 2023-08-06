import asciimatics.event

from asciimatics import widgets
from asciimatics.screen import Screen

from asciimatics import exceptions

from bs_monitor.tui import tui_util
from bs_monitor.tui.pod_tui import PodTui


class MondateEnquiry(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(MondateEnquiry, self).__init__(
            screen, 12, 80, on_load=self._btn_refresh_click, has_shadow=True, hover_focus=True, can_scroll=False,
            reduce_cpu=True, title="Monitor Date Enquiry"
        )

        self._pod = pod

        layout_btns = widgets.Layout([1, 1, 1])
        layout_grid = widgets.Layout([100], fill_frame=True)

        self.add_layout(layout_btns)
        self.add_layout(layout_grid)

        layout_btns.add_widget(widgets.Button(f"Refresh [{tui_util.KEY_HINT_REFRESH}]", self._btn_refresh_click), 0)
        layout_btns.add_widget(widgets.Button(f"Back [{tui_util.KEY_HINT_BACK}]", self._btn_back_click), 1)
        layout_btns.add_widget(widgets.Button(f"Quit [{tui_util.KEY_HINT_QUIT}]", self._btn_quit_click), 2)

        self._grid = widgets.MultiColumnListBox(
            widgets.Widget.FILL_FRAME,
            ["<16", "<12", "<64" ],
            [],
            titles=["ID", "VALUE", "DESCR"],
            name="mondate_gridlist",
            on_select=self._select_option,
        )

        layout_grid.add_widget(widgets.Divider())
        layout_grid.add_widget(self._grid)

        self.fix()

    def process_event(self, event):
        if isinstance(event, asciimatics.event.KeyboardEvent):
            if tui_util.handle_f_keys(self._screen, self._scene, event):
                return

            if event.key_code == tui_util.KEY_REFRESH:
                self._btn_refresh_click()
            elif event.key_code == tui_util.KEY_BACK:
                self._btn_back_click()
            elif event.key_code == tui_util.KEY_EDIT:
                self._select_option()

        return super(MondateEnquiry, self).process_event(event)

    def _btn_refresh_click(self, new_value=None):
        self.set_theme(self._pod.theme)
        mlist = self._pod.svr.mondate_list(None, None)
        options = []

        for x in mlist:
            options.append(([x.id, str(x.value), x.descr], x.id))

        self._grid.options = options
        self._grid.value = new_value

    def _btn_back_click(self) -> None:
        raise exceptions.NextScene('MainMenu')

    def _btn_quit_click(self) -> None:
        raise exceptions.StopApplication("User quit")

    def _select_option(self):
        self.save()

        if not self.data.get('mondate_gridlist'):
            return

        self._pod.cfg['mondate_item'] = self.data['mondate_gridlist']
        raise exceptions.NextScene("MondateView")


class MondateView(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(MondateView, self).__init__(
            screen, 12, 80, hover_focus=True, can_scroll=False,
            reduce_cpu=True, title="Mondate Details"
        )

        self._pod = pod
        self._rec = None

        layout_form = widgets.Layout([100], fill_frame=True)
        layout_sep = widgets.Layout([100])
        layout_btns = widgets.Layout([1, 1])

        self.add_layout(layout_form)
        self.add_layout(layout_sep)
        self.add_layout(layout_btns)

        layout_form.add_widget(widgets.Text("ID:", "id", readonly=True))
        layout_form.add_widget(widgets.Text("Description:", "descr", max_length=256))
        layout_form.add_widget(widgets.DatePicker("Value:", "value"))
        layout_form.add_widget(widgets.Text("Stamp By:", "stamp_by", readonly=True))
        layout_form.add_widget(widgets.Text("Stamp Tm:", "stamp_tm", readonly=True))

        layout_sep.add_widget(widgets.Divider())

        layout_btns.add_widget(widgets.Button(f"OK [{tui_util.KEY_HINT_SAVE}]", self._ok), 0)
        layout_btns.add_widget(widgets.Button(f"Cancel [{tui_util.KEY_HINT_BACK}]", self._cancel), 1)
        self.fix()

    def process_event(self, event):
        if isinstance(event, asciimatics.event.KeyboardEvent):
            if tui_util.handle_f_keys(self._screen, self._scene, event):
                return

            if event.key_code == tui_util.KEY_SAVE:
                self._ok()
            elif event.key_code == tui_util.KEY_BACK:
                self._cancel()

        return super(MondateView, self).process_event(event)

    def reset(self):
        super(MondateView, self).reset()
        self.set_theme(self._pod.theme)

        self._rec = self._pod.svr.mondate_read(self._pod.cfg['mondate_item'])

        self.data = {
            'id': self._rec.id,
            'descr': self._rec.descr,
            'value': self._rec.value,
            'stamp_by': self._rec.stamp_by,
            'stamp_tm': self._rec.stamp_tm.isoformat(),
        }

    def _ok(self):
        self.save()

        chg = False
        chg = tui_util.assign_diff(self._rec, self.data, 'descr') or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'value') or chg

        if chg:
            try:
                self._pod.svr.mondate_update(self._rec)
            except Exception as x:
                self._scene.add_effect(tui_util.pop_exception(self._screen, x))
                return


        raise exceptions.NextScene("MondateEnquiry")

    def _cancel(self):
        raise exceptions.NextScene("MondateEnquiry")
