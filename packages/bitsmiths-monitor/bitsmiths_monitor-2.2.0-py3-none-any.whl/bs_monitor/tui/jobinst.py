import datetime
import asciimatics.event

from asciimatics import widgets
from asciimatics.screen import Screen

from asciimatics import exceptions

from bs_monitor.db.tables import tBatchInst
from bs_monitor.db.tables import tJobInst
from bs_monitor.db.tables import tJobInstMetric
from bs_monitor.db.tables import oJobInstSearch
from bs_monitor.braze     import bJobInstQuery
from bs_monitor.braze     import bLazyLoad

from bs_monitor.tui import tui_util
from bs_monitor.tui.pod_tui import PodTui


class JobInstEnquiry(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(JobInstEnquiry, self).__init__(
            screen, screen.height, screen.width, on_load=self._btn_refresh_click, has_shadow=True, hover_focus=True,
            can_scroll=True, reduce_cpu=True, title="Job Instance Enquiry"
        )

        self._pod = pod
        self._btn_reset_click()

        if not self.data:
            self.data = self._build_default_criteria()

        layout_crit = widgets.Layout([1, 1, 1, 1])
        layout_sep1 = widgets.Layout([100])
        layout_crit_btns = widgets.Layout([1, 1, 1, 1])
        layout_grid = widgets.Layout([100], fill_frame=True)
        layout_ji_btns = widgets.Layout([1, 1, 1, 1])

        self.add_layout(layout_crit)
        self.add_layout(layout_sep1)
        self.add_layout(layout_crit_btns)
        self.add_layout(layout_grid)
        self.add_layout(layout_ji_btns)

        cd = self._load_crit_data()

        layout_crit.add_widget(widgets.DropdownList(cd['status'], "Status:", "crit_status"), 0)
        layout_crit.add_widget(
            widgets.Text("Job Inst ID:", "crit_jobinst_id", validator=tui_util.validator_numeric(), max_length=16), 0
        )
        layout_crit.add_widget(widgets.Text("Limit:", "crit_limit", validator=tui_util.validator_numeric(), max_length=6), 0)
        layout_crit.add_widget(widgets.DatePicker("From Date:", name="crit_from_date"), 1)
        layout_crit.add_widget(widgets.DatePicker("To Date:", "crit_to_date"), 1)
        layout_crit.add_widget(widgets.Text("Offset:", "crit_offset", validator=tui_util.validator_numeric(), max_length=6), 1)
        layout_crit.add_widget(widgets.DropdownList(cd['jobs'], "Job:", "crit_job"), 2)
        layout_crit.add_widget(widgets.DropdownList(cd['job_grps'], "Job Group:", "crit_job_grp"), 2)
        layout_crit.add_widget(widgets.DropdownList(cd['batches'], "Batch:", "crit_batch"), 3)
        layout_crit.add_widget(widgets.DropdownList(cd['batch_grps'], "Batch Group:", "crit_batch_grp"), 3)
        layout_crit.add_widget(
            widgets.Text("Batch Inst ID:", "crit_batchinst_id", validator=tui_util.validator_numeric(), max_length=16), 3
        )

        layout_sep1.add_widget(widgets.Divider())

        layout_crit_btns.add_widget(widgets.Button(f"Refresh [{tui_util.KEY_HINT_REFRESH}]", self._btn_refresh_click), 0)
        layout_crit_btns.add_widget(widgets.Button(f"Reset [{tui_util.KEY_HINT_RESET}]", self._btn_reset_click), 1)
        layout_crit_btns.add_widget(widgets.Button(f"Back [{tui_util.KEY_HINT_BACK}]", self._btn_back_click), 2)
        layout_crit_btns.add_widget(widgets.Button(f"Quit [{tui_util.KEY_HINT_QUIT}]", self._btn_quit_click), 3)

        self._grid = widgets.MultiColumnListBox(
            widgets.Widget.FILL_FRAME,
            [">10", ">10", "<36", ">10", "<20", "<11", ">9", "<20", "<20", "100%" ],
            [],
            titles=[
                "ID", "PARENT", "JOB", "BATCH INST", "PROCESS DATE", "STATUS", "PRIORITY", "JOB GROUP",
                "BATCH GROUP", "EXTRA ARGS"
            ],
            name="jobinst_grid",
            add_scroll_bar=True,
            on_select=self._on_select_job_inst,
            on_change=self._on_change_job_inst,
        )

        layout_grid.add_widget(widgets.Divider())
        layout_grid.add_widget(self._grid)
        layout_grid.add_widget(widgets.Divider())

        self._btn_ji_rerun = widgets.Button("Rerun", self._btn_ji_rerun_click, disabled=True)
        self._btn_ji_forceok = widgets.Button("Force OK", self._btn_ji_forceok_click, disabled=True)
        self._btn_ji_cancel = widgets.Button("Stop/Cancel", self._btn_ji_cancel_click, disabled=True)
        self._btn_ji_hist = widgets.Button("History", self._btn_ji_hist_click, disabled=True)

        layout_ji_btns.add_widget(self._btn_ji_rerun, 0)
        layout_ji_btns.add_widget(self._btn_ji_forceok, 1)
        layout_ji_btns.add_widget(self._btn_ji_cancel, 2)
        layout_ji_btns.add_widget(self._btn_ji_hist, 3)

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

        return super(JobInstEnquiry, self).process_event(event)

    def _btn_refresh_click(self):
        self.set_theme(self._pod.theme)
        self.save()

        if not self.data or self._pod.cfg.get('job_inst_qry'):
            self.data = self._build_default_criteria()

        qry = bJobInstQuery()
        ll = bLazyLoad(
            int(self.data['crit_offset'] if self.data['crit_offset'] else 0),
            int(self.data['crit_limit'] if self.data['crit_limit'] else 0)
        )

        qry.date_from = self.data['crit_from_date']
        qry.date_to = self.data['crit_to_date']

        if self.data['crit_status']:
            qry.jobinst_status = [self.data['crit_status']]

        if self.data['crit_job']:
            qry.job_id = self.data['crit_job']

        if self.data['crit_jobinst_id']:
            qry.jobinst_id = int(self.data['crit_jobinst_id'])

        if self.data['crit_job_grp']:
            qry.group_job = self.data['crit_job_grp']

        if self.data['crit_batch']:
            qry.batch_id = int(self.data['crit_batch'])

        if self.data['crit_batch_grp']:
            qry.group_batch = self.data['crit_batch_grp']

        if self.data['crit_batchinst_id']:
            qry.batchinst_id = int(self.data['crit_batchinst_id'])

        res = self._pod.svr.jobinst_list(ll, qry)
        options = []

        for x in res:
            options.append(self._create_grid_item(x))

        self._grid.options = options
        self._grid.value = None

    def _btn_back_click(self) -> None:
        raise exceptions.NextScene('MainMenu')

    def _btn_quit_click(self) -> None:
        raise exceptions.StopApplication("User quit")

    def _btn_reset_click(self) -> None:
        self.data = self._build_default_criteria()

    def _on_select_job_inst(self) -> None:
        self.save()
        ji_rec = self.data['jobinst_grid']

        self._reload_from_db(ji_rec)
        info_txt = self._gen_dialog_info_text(ji_rec)

        pop = widgets.PopUpDialog(
            self._screen,
            info_txt,
            ["OK", "Rerun"],
            has_shadow=True,
            on_close=self._confirm_rerun
        )

        self._scene.add_effect(pop)

    def _on_change_job_inst(self) -> None:
        self.save()
        self._btn_ji_rerun.disabled = True
        self._btn_ji_forceok.disabled = True
        self._btn_ji_cancel.disabled = True
        self._btn_ji_hist.disabled = True

        ji = self._grid.value

        if not ji:
            return

        self._btn_ji_hist.disabled = False
        self._btn_ji_rerun.disabled = False

        if ji.inst_rec.status == tJobInst.Status_Couplet.key_failed:
            self._btn_ji_forceok.disabled = False
        elif ji.inst_rec.status == tJobInst.Status_Couplet.key_running:
            self._btn_ji_cancel.disabled = False

    def _build_default_criteria(self) -> dict:
        res = {
            'crit_status': None,
            'crit_jobinst_id': '',
            'crit_limit': '1000',
            'crit_offset': '0',
            'crit_from_date': datetime.date.today() - datetime.timedelta(days=90),
            'crit_to_date': datetime.date.today() + datetime.timedelta(days=3),
            'crit_job': None,
            'crit_batch': None,
            'crit_job_grp': None,
            'crit_batch_grp': None,
            'crit_batchinst_id': '',
        }

        if 'job_inst_qry' in self._pod.cfg:
            qry = self._pod.cfg.pop('job_inst_qry')

            if 'batchinst_id' in qry:
                res['crit_batchinst_id'] = str(qry['batchinst_id'])

        return res

    def _load_crit_data(self) -> dict:
        lookups = self._pod.load_lookups()

        res = {
            'status': tui_util.couplet_to_dropdown(tJobInst.Status_Couplet()),
            'jobs': tui_util.couplet_to_dropdown(lookups['jobs']),
            'job_grps': tui_util.couplet_to_dropdown(lookups['job_grps']),
            'batches': tui_util.couplet_to_dropdown(lookups['batches']),
            'batch_grps': tui_util.couplet_to_dropdown(lookups['batch_grps']),
        }

        return res

    def _btn_ji_rerun_click(self) -> None:
        self._scene.add_effect(widgets.PopUpDialog(self._screen, "Are you sure you want Rerun?", tui_util.NO_YES_OPTIONS, has_shadow=True, on_close=self._confirm_rerun))  # noqa

    def _btn_ji_forceok_click(self) -> None:
        self._scene.add_effect(widgets.PopUpDialog(self._screen, "Are you sure you want Force OK?", tui_util.NO_YES_OPTIONS, has_shadow=True, on_close=self._confirm_force_ok))  # noqa

    def _btn_ji_cancel_click(self) -> None:
        self._scene.add_effect(widgets.PopUpDialog(self._screen, "Are you sure you want Stop/Cancel this job?", tui_util.NO_YES_OPTIONS, has_shadow=True, on_close=self._confirm_cancel))  # noqa

    def _btn_ji_hist_click(self) -> None:
        ji_rec = self.data['jobinst_grid']
        metrics = self._pod.svr.jobinst_metrics(None, ji_rec.inst_rec.id)

        if not metrics:
            self._scene.add_effect(widgets.PopUpDialog(self._screen, "No history found.", ["OK"], has_shadow=True))
            return

        sep = '|'
        mask = '%s%-19.19s %s %-14.14s %s %-64s'
        nl = '\n'

        res = mask % ('', "Time Stamp", sep, "Type", sep, "Message")
        res += nl
        sep = ' '

        for rec in metrics:
            res += mask % (nl, str(rec.stamp_tm), sep, tJobInstMetric.Mtype_Couplet.get_value(rec.mtype), sep, rec.msg or '')

        self._scene.add_effect(widgets.PopUpDialog(self._screen, res, ["OK"], has_shadow=True))

    def _reload_from_db(self, jrec: oJobInstSearch) -> None:
        dbrec = self._pod.svr.jobinst_read(jrec.inst_rec.id)
        jrec.inst_rec._copy_from(dbrec)

    def _gen_dialog_info_text(self, jrec: oJobInstSearch) -> str:
        mask = '%s%-18.18s : %-20.20s    %-18.18s : %s'
        mask_single = '%s%-18.18s : %s'
        nl = '\n'

        res = f'Job Instance:{nl}'
        res += mask % (nl, "ID", str(jrec.inst_rec.id), "Parent ID", str(jrec.inst_rec.parent_id))

        res += mask % (nl, "Status", tJobInst.Status_Couplet.get_value(jrec.inst_rec.status), "Priority", str(jrec.inst_rec.priority))  # noqa
        res += mask % (nl, "Process Date", str(jrec.inst_rec.process_date), "Batch Run Date", str(jrec.batch_run_date))

        if jrec.inst_rec.extra_args:
            res += mask_single % (nl, 'Extra Args', jrec.inst_rec.extra_args)

        if jrec.inst_rec.batchinst_id:
            res += nl
            res += mask % (nl, "BatchInst ID", str(jrec.inst_rec.batchinst_id) or '', "Batch ID", str(jrec.batch_id) or '')
            res += mask % (nl, "BatchInst Status", tBatchInst.Status_Couplet.get_value(jrec.batchinst_status), "Batch Name", jrec.batch_name)  # noqa
            res += mask % (nl, "BatchInst Rundate", str(jrec.batchinst_run_date), "Batch Rundate", str(jrec.batch_run_date))

        res += nl
        res += mask % (nl, "Group Job", jrec.inst_rec.group_job or '', "Stamp By", jrec.inst_rec.stamp_by)
        res += mask % (nl, "Group Batch", jrec.inst_rec.group_batch or '', "Stamp Tm", str(jrec.inst_rec.stamp_tm))

        return res

    def _confirm_rerun(self, selected: int) -> None:
        ji_rec = self.data['jobinst_grid']

        if selected == 0:
            self._refresh_gird_item(ji_rec)
            return

        try:
            res = self._pod.svr.jobinst_rerun(ji_rec.inst_rec.id, True)
            ji_rec.inst_rec._copy_from(res)
            self._refresh_gird_item(ji_rec)
        except Exception as x:
            self._scene.add_effect(tui_util.pop_exception(self._screen, x))
            return

    def _confirm_force_ok(self, selected: int) -> None:
        if selected == 0:
            return

        try:
            ji_rec = self.data['jobinst_grid']
            res = self._pod.svr.jobinst_force_ok(ji_rec.inst_rec.id, None)
            ji_rec.inst_rec._copy_from(res)
            self._refresh_gird_item(ji_rec)
        except Exception as x:
            self._scene.add_effect(tui_util.pop_exception(self._screen, x))
            return

    def _confirm_cancel(self, selected: int) -> None:
        if selected == 0:
            return

        try:
            ji_rec = self.data['jobinst_grid']
            res = self._pod.svr.jobinst_stop(ji_rec.inst_rec.id, None)
            ji_rec.inst_rec._copy_from(res)
            self._refresh_gird_item(ji_rec)
        except Exception as x:
            self._scene.add_effect(tui_util.pop_exception(self._screen, x))
            return

    def _create_grid_item(self, ji_rec: oJobInstSearch) -> tuple:
        return (
            [
                str(ji_rec.inst_rec.id),
                str(ji_rec.inst_rec.parent_id) if ji_rec.inst_rec.parent_id else '',
                ji_rec.job_name,
                str(ji_rec.batchinst_id) if ji_rec.batchinst_id else '',
                str(ji_rec.inst_rec.process_date),
                tJobInst.Status_Couplet.get_value(ji_rec.inst_rec.status),
                str(ji_rec.inst_rec.priority),
                ji_rec.inst_rec.group_job,
                ji_rec.inst_rec.group_batch,
                ji_rec.inst_rec.extra_args,
            ],
            ji_rec
        )

    def _refresh_gird_item(self, ji_rec: oJobInstSearch) -> tuple:
        options = self._grid.options
        idx = 0

        while idx < len(options):
            if options[idx][1] == ji_rec:
                options[idx] = self._create_grid_item(ji_rec)
                return

            idx += 1
