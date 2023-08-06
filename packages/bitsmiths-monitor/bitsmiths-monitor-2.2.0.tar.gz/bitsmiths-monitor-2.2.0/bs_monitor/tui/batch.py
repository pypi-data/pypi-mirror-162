import datetime
import json

import asciimatics.event

from asciimatics import widgets
from asciimatics.screen import Screen

from asciimatics import exceptions

from bs_monitor.db.tables import tBatch
from bs_monitor.braze     import bBatchQuery
from bs_monitor.braze     import bLazyLoad

from bs_monitor.tui import tui_util
from bs_monitor.tui.pod_tui import PodTui


class BatchEnquiry(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(BatchEnquiry, self).__init__(
            screen, screen.height, screen.width, on_load=self._btn_refresh_click, has_shadow=True, hover_focus=True,
            can_scroll=True, reduce_cpu=True, title="Batch Enquiry"
        )

        self._pod = pod
        self._btn_reset_click()

        if not self.data:
            self.data = self._build_default_criteria()

        layout_crit = widgets.Layout([1, 1])
        layout_sep1 = widgets.Layout([100])
        layout_crit_btns = widgets.Layout([1, 1, 1, 1])
        layout_grid = widgets.Layout([100], fill_frame=True)
        layout_bi_btns = widgets.Layout([1, 1, 1])

        self.add_layout(layout_crit)
        self.add_layout(layout_sep1)
        self.add_layout(layout_crit_btns)
        self.add_layout(layout_grid)
        self.add_layout(layout_bi_btns)

        cd = self._load_crit_data()

        layout_crit.add_widget(widgets.DropdownList(cd['status'], "Status:", "crit_status"), 0)
        layout_crit.add_widget(widgets.Text("Limit:", "crit_limit", validator=tui_util.validator_numeric(), max_length=6), 0)
        layout_crit.add_widget(widgets.DropdownList(cd['batch_grps'], "Batch Group:", "crit_batch_grp"), 1)
        layout_crit.add_widget(widgets.Text("Offset:", "crit_offset", validator=tui_util.validator_numeric(), max_length=6), 1)

        layout_sep1.add_widget(widgets.Divider())

        layout_crit_btns.add_widget(widgets.Button(f"Refresh [{tui_util.KEY_HINT_REFRESH}]", self._btn_refresh_click), 0)
        layout_crit_btns.add_widget(widgets.Button(f"Reset [{tui_util.KEY_HINT_RESET}]", self._btn_reset_click), 1)
        layout_crit_btns.add_widget(widgets.Button(f"Back [{tui_util.KEY_HINT_BACK}]", self._btn_back_click), 2)
        layout_crit_btns.add_widget(widgets.Button(f"Quit [{tui_util.KEY_HINT_QUIT}]", self._btn_quit), 3)

        self._grid = widgets.MultiColumnListBox(
            widgets.Widget.FILL_FRAME,
            [">10", ">10", "<32", "<8", "<20", "<12", "<8", ">10", "100%" ],
            [],
            titles=[
                "ID", "PARENT", "NAME", "STATUS", "RUNDATE", "TIME", "CYCLE", "INTERVAL", "GROUP" ],
            name="batch_grid",
            add_scroll_bar=True,
            on_select=self._on_select_batch,
            on_change=self._on_change_batch,
        )

        layout_grid.add_widget(widgets.Divider())
        layout_grid.add_widget(self._grid)
        layout_grid.add_widget(widgets.Divider())

        self._btn_bi_edit = widgets.Button(f"Edit [{tui_util.KEY_HINT_EDIT}]", self._btn_bi_edit_click, disabled=True)
        self._btn_bi_edit_items = widgets.Button("Edit Job Items", self._btn_bi_edit_items_click, disabled=True)
        self._btn_bi_create = widgets.Button(f"Create [{tui_util.KEY_HINT_CREATE}]", self._btn_bi_create_click, disabled=True)

        layout_bi_btns.add_widget(self._btn_bi_edit, 0)
        layout_bi_btns.add_widget(self._btn_bi_edit_items, 1)
        layout_bi_btns.add_widget(self._btn_bi_create, 2)

        self.fix()

    def process_event(self, event):
        if isinstance(event, asciimatics.event.KeyboardEvent):
            if tui_util.handle_f_keys(self._screen, self._scene, event):
                return

            if event.key_code == tui_util.KEY_REFRESH:
                self._btn_refresh_click()
            elif event.key_code == tui_util.KEY_RESET:
                self._btn_reset_click()
            elif event.key_code == tui_util.KEY_BACK:
                self._btn_back_click()
            elif event.key_code == tui_util.KEY_EDIT:
                if not self._btn_bi_edit.disabled:
                    self._btn_bi_edit_click()
                return
            elif event.key_code == tui_util.KEY_CREATE:
                self._btn_bi_create_click()

        return super(BatchEnquiry, self).process_event(event)

    def _btn_refresh_click(self):
        self.set_theme(self._pod.theme)
        self.save()

        if not self.data:
            self.data = self._build_default_criteria()

        qry = bBatchQuery()
        ll = bLazyLoad(
            int(self.data['crit_offset'] if self.data['crit_offset'] else 0),
            int(self.data['crit_limit'] if self.data['crit_limit'] else 0)
        )

        if self.data['crit_status']:
            qry.status = [self.data['crit_status']]

        if self.data['crit_batch_grp']:
            qry.group = self.data['crit_batch_grp']

        res = self._pod.svr.batch_list(ll, qry)
        options = []

        for x in res:
            options.append(self._create_grid_item(x))

        self._grid.options = options
        self._grid.value = None

    def _btn_back_click(self) -> None:
        raise exceptions.NextScene('MainMenu')

    def _btn_quit(self) -> None:
        raise exceptions.StopApplication("User quit")

    def _btn_reset_click(self) -> None:
        self.data = self._build_default_criteria()

    def _on_select_batch(self) -> None:
        self.save()
        brec = self.data['batch_grid']

        self._reload_from_db(brec)
        info_txt = self._gen_dialog_info_text(brec)

        pop = widgets.PopUpDialog(
            self._screen,
            info_txt,
            ["OK", "BatchInst Enquiry"],
            has_shadow=True,
            on_close=self._batch_options
        )

        self._scene.add_effect(pop)

    def _on_change_batch(self) -> None:
        self.save()
        self._btn_bi_edit.disabled = True
        self._btn_bi_edit_items.disabled = True
        self._btn_bi_create.disabled = True

        brec = self._grid.value

        if not brec:
            return

        self._btn_bi_edit.disabled = False
        self._btn_bi_edit_items.disabled = False
        self._btn_bi_create.disabled = False

    def _build_default_criteria(self) -> dict:
        res = {
            'crit_status': None,
            'crit_limit': '1000',
            'crit_offset': '0',
            'crit_batch_grp': None,
        }

        if 'job_inst_qry' in self._pod.cfg:
            qry = self._pod.cfg.pop('job_inst_qry')

            if 'batchinst_id' in qry:
                res['crit_batchinst_id'] = str(qry['batchinst_id'])

        return res

    def _load_crit_data(self) -> dict:
        lookups = self._pod.load_lookups()

        res = {
            'status': tui_util.couplet_to_dropdown(tBatch.Status_Couplet()),
            'batch_grps': tui_util.couplet_to_dropdown(lookups['batch_grps']),
        }

        return res


    def _btn_bi_edit_click(self) -> None:
        self._pod.cfg['batch_item'] = self._grid.value
        raise exceptions.NextScene("BatchView")

    def _btn_bi_edit_items_click(self) -> None:
        self._pod.cfg['batch_item'] = self._grid.value
        raise exceptions.NextScene("BatchItemEnquiry")

    def _btn_bi_create_click(self) -> None:
        self._pod.cfg['batch_item'] = None
        raise exceptions.NextScene("BatchView")

    def _reload_from_db(self, brec: tBatch) -> None:
        dbrec = self._pod.svr.batch_read(brec.id, None)
        brec._copy_from(dbrec)

    def _gen_dialog_info_text(self, brec: tBatch) -> str:
        mask = '%s%-18.18s : %-20.20s    %-18.18s : %s'
        mask_single = '%s%-18.18s : %s'
        nl = '\n'

        res = f'Batch:{nl}'
        res += mask % (nl, "ID", str(brec.id), "Parent ID", str(brec.parent_id))
        res += mask_single % (nl, 'Name', brec.name)
        res += mask_single % (nl, 'Group', brec.group_id)
        res += mask_single % (nl, "Status", tBatch.Status_Couplet.get_value(brec.status))

        res += nl
        res += mask % (nl, "Run Date", str(brec.run_date), "Cycle", tBatch.Cycle_Couplet.get_value(brec.cycle))
        res += mask % (nl, "Run Time", self._interval_time(brec.run_time), "Interval", str(brec.run_interval))

        res += nl

        if brec.ext_data:
            res += mask_single % (nl, "Extra Data", brec.ext_data)

        res += mask_single % (nl, "Stamp By", brec.stamp_by)
        res += mask_single % (nl, "Stamp Tm", str(brec.stamp_tm))

        return res

    def _batch_options(self, selected: int) -> None:
        brec = self.data['batch_grid']

        if selected == 1:
            self._pod.cfg['batch_inst_qry'] = {'batch_id': brec.id}
            raise exceptions.NextScene("BatchInstEnquiry")

        self._refresh_gird_item(brec)

    def _create_grid_item(self, brec: tBatch) -> tuple:
        return (
            [
                str(brec.id),
                str(brec.parent_id) if brec.parent_id else '',
                brec.name,
                tBatch.Status_Couplet.get_value(brec.status),
                str(brec.run_date),
                self._interval_time(brec.run_time),
                tBatch.Cycle_Couplet.get_value(brec.cycle),
                str(brec.run_interval),
                brec.group_id,
            ],
            brec
        )

    def _refresh_gird_item(self, brec: tBatch) -> tuple:
        options = self._grid.options
        idx = 0

        while idx < len(options):
            if options[idx][1] == brec:
                options[idx] = self._create_grid_item(brec)
                return

            idx += 1

    @staticmethod
    def _interval_time(run_time: str) -> str:
        return f"{run_time[0:2]}:{run_time[2:4]}:{run_time[4:]}"


class BatchView(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(BatchView, self).__init__(
            screen, 18, 80, hover_focus=True, can_scroll=False,
            reduce_cpu=True, title="Batch Details"
        )

        self._pod = pod
        self._rec = None

        layout_form = widgets.Layout([100], fill_frame=True)
        layout_sep = widgets.Layout([100])
        layout_btns = widgets.Layout([1, 1])

        self.add_layout(layout_form)
        self.add_layout(layout_sep)
        self.add_layout(layout_btns)

        lookups = self._pod.load_lookups()

        self._rundate_widget = widgets.Text("Run Date:", "run_date", readonly=True)

        layout_form.add_widget(widgets.Text("ID:", "id", readonly=True))
        layout_form.add_widget(widgets.DropdownList( tui_util.couplet_to_dropdown(lookups['batches'], False, True), "Parent:", "parent_id"))  # noqa
        layout_form.add_widget(widgets.Text("Name:", "name", max_length=256))
        layout_form.add_widget(widgets.Text("Group:", "group_id", max_length=128))
        layout_form.add_widget(widgets.DropdownList(tui_util.couplet_to_dropdown(tBatch.Status_Couplet(), False), "Status:", "status"))  # noqa
        layout_form.add_widget(self._rundate_widget)
        layout_form.add_widget(widgets.TimePicker("Run Time", name="run_time", on_change=self._upd_rundate, seconds=True))
        layout_form.add_widget(widgets.DropdownList(tui_util.couplet_to_dropdown(tBatch.Cycle_Couplet(), False), "Run Cycle:", "cycle"))  # noqa
        layout_form.add_widget(widgets.Text("Run Interval:", "run_interval", validator=tui_util.validator_numeric(), max_length=2))  # noqa
        layout_form.add_widget(widgets.Text("External Data:", "ext_data", validator=tui_util.validator_json))
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

        return super(BatchView, self).process_event(event)

    def reset(self):
        super(BatchView, self).reset()
        self.set_theme(self._pod.theme)

        item = self._pod.cfg['batch_item']

        if item is None:
            today = datetime.date.today()
            self._rec = tBatch()
            self._rec.parent_id = None
            self._rec.status = tBatch.Status_Couplet.key_active
            self._rec.cycle = tBatch.Cycle_Couplet.key_day
            self._rec.run_date = datetime.datetime(today.year, today.month, today.day, 0, 0)
            self._rec.run_interval = 1
            self._rec.run_time = '000000'
        else:
            self._rec = self._pod.svr.batch_read(item.id, None)

        rt = self._str_to_time(self._rec.run_time)

        self.data = {
            'id': str(self._rec.id) if self._rec.id else '<NEW>',
            'parent_id': self._rec.parent_id or None,
            'name': self._rec.name,
            'group_id': self._rec.group_id,
            'status': self._rec.status,
            'run_date': self._gen_rundate(rt),
            'cycle': self._rec.cycle,
            'run_time': rt,
            'run_interval': str(self._rec.run_interval),
            'ext_data': json.dumps(self._rec.ext_data) if self._rec.ext_data else '',
            'stamp_by': self._rec.stamp_by or '',
            'stamp_tm': self._rec.stamp_tm.isoformat() if self._rec.stamp_tm else '',
        }


    def _ok(self):
        self.save()

        if not self._validate_record():
            return

        chg = False
        chg = tui_util.assign_diff(self._rec, self.data, 'parent_id', int) or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'name') or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'group_id') or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'status') or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'cycle') or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'run_interval', int) or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'ext_data', dict) or chg

        rts = self._time_to_str(self.data['run_time'])

        if rts != self._rec.run_time:
            rt = self.data['run_time']
            rd = self._rec.run_date
            self._rec.run_time = rts
            self._rec.run_date = datetime.datetime(rd.year, rd.month, rd.day, rt.hour, rt.minute, rt.second)
            chg = True

        try:
            if self._rec.id == 0:
                self._pod.svr.batch_create(self._rec)
            else:
                if chg:
                    self._pod.svr.batch_update(self._rec)
        except Exception as x:
            self._scene.add_effect(tui_util.pop_exception(self._screen, x))
            return

        raise exceptions.NextScene("BatchEnquiry")

    def _cancel(self):
        raise exceptions.NextScene("BatchEnquiry")

    def _validate_record(self) -> bool:
        pop = None

        if not self.data['name']:
            pop = widgets.PopUpDialog(self._screen, "Name is required.", ["OK"], has_shadow=True)
        elif not self.data['group_id']:
            pop = widgets.PopUpDialog(self._screen, "Group is required.", ["OK"], has_shadow=True)

        ri = int(self.data['run_interval'])

        if ri < 1 or ri > 60:
            pop = widgets.PopUpDialog(self._screen, "Run Interval must be between 1 and 60.", ["OK"], has_shadow=True)

        if pop:
            self._scene.add_effect(pop)
            return False

        return True

    def _gen_rundate(self, time: datetime.time) -> str:
        return f'{self._rec.run_date.date()}T{time}'

    def _upd_rundate(self) -> None:
        self.save()
        self._rundate_widget.value = self._gen_rundate(self.data['run_time'])

    @staticmethod
    def _str_to_time(rt: str) -> datetime.time:
        return datetime.datetime.strptime(rt, '%H%M%S').time()

    @staticmethod
    def _time_to_str(rt: datetime.time) -> str:
        return rt.strftime('%H%M%S')
