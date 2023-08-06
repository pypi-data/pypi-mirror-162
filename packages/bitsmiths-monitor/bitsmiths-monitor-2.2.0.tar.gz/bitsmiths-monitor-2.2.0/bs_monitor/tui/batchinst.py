import datetime
import asciimatics.event

from asciimatics import widgets
from asciimatics.screen import Screen

from asciimatics import exceptions

from bs_monitor.db.tables import tBatchInst
from bs_monitor.db.tables import tJobInst
from bs_monitor.braze     import bBatchInstQuery
from bs_monitor.braze     import bJobInstQuery
from bs_monitor.braze     import bLazyLoad

from bs_monitor.tui import tui_util
from bs_monitor.tui.pod_tui import PodTui


class BatchInstEnquiry(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(BatchInstEnquiry, self).__init__(
            screen, screen.height, screen.width, on_load=self._btn_refresh_click, has_shadow=True, hover_focus=True,
            can_scroll=True, reduce_cpu=True, title="Batch Instance Enquiry"
        )

        self._pod = pod
        self._btn_reset_click()

        if not self.data:
            self.data = self._build_default_criteria()

        layout_crit = widgets.Layout([1, 1, 1])
        layout_sep1 = widgets.Layout([100])
        layout_crit_btns = widgets.Layout([1, 1, 1, 1])
        layout_grid = widgets.Layout([100], fill_frame=True)

        self.add_layout(layout_crit)
        self.add_layout(layout_sep1)
        self.add_layout(layout_crit_btns)
        self.add_layout(layout_grid)

        cd = self._load_crit_data()

        layout_crit.add_widget(widgets.DropdownList(cd['status'], "Status:", "crit_status"), 0)
        layout_crit.add_widget(widgets.DropdownList(cd['batches'], "Batch:", "crit_batch"), 0)
        layout_crit.add_widget(widgets.Text("Limit:", "crit_limit", validator=tui_util.validator_numeric(), max_length=6), 0)
        layout_crit.add_widget(widgets.DatePicker("From Date:", name="crit_from_date"), 1)
        layout_crit.add_widget(widgets.DatePicker("To Date:", "crit_to_date"), 1)
        layout_crit.add_widget(widgets.Text("Offset:", "crit_offset", validator=tui_util.validator_numeric(), max_length=6), 1)

        layout_sep1.add_widget(widgets.Divider())

        layout_crit_btns.add_widget(widgets.Button(f"Refresh [{tui_util.KEY_HINT_REFRESH}]", self._btn_refresh_click), 0)
        layout_crit_btns.add_widget(widgets.Button(f"Reset [{tui_util.KEY_HINT_RESET}]", self._btn_reset_click), 1)
        layout_crit_btns.add_widget(widgets.Button(f"Back [{tui_util.KEY_HINT_BACK}]", self._btn_back_click), 2)
        layout_crit_btns.add_widget(widgets.Button(f"Quit [{tui_util.KEY_HINT_QUIT}]", self._btn_quit_click), 3)

        self._grid = widgets.MultiColumnListBox(
            widgets.Widget.FILL_FRAME,
            [">10", ">10", "<12", "<20", "<20", "<20", "100%" ],
            [],
            titles=[
                "ID", "PARENT", "STATUS", "RUN DATE", "START DATE", "END DATE", "BATCH"
            ],
            name="batchinst_grid",
            add_scroll_bar=True,
            on_select=self._on_select_job_inst,
            on_change=self._on_change_job_inst,
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
            elif event.key_code == tui_util.KEY_RESET:
                self._btn_reset_click()
            elif event.key_code == tui_util.KEY_BACK:
                self._btn_back_click()

        return super(BatchInstEnquiry, self).process_event(event)

    def _btn_refresh_click(self):
        self.set_theme(self._pod.theme)
        self.save()

        if not self.data or self._pod.cfg.get('batch_inst_qry'):
            self.data = self._build_default_criteria()

        qry = bBatchInstQuery()
        ll = bLazyLoad(
            int(self.data['crit_offset'] if self.data['crit_offset'] else 0),
            int(self.data['crit_limit'] if self.data['crit_limit'] else 0)
        )

        qry.date_from = self.data['crit_from_date']
        qry.date_to = self.data['crit_to_date']

        if self.data['crit_status']:
            qry.status = [self.data['crit_status']]

        if self.data['crit_batch']:
            qry.batch_id = int(self.data['crit_batch'])

        res = self._pod.svr.batchinst_list(ll, qry)
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
        brec = self.data['batchinst_grid']

        self._reload_from_db(brec)
        info_txt = self._gen_dialog_info_text(brec)

        opts = ["OK", "Show Items"]

        if brec.status == tBatchInst.Status_Couplet.key_busy:
            opts.append("Rerun Failed")

        pop = widgets.PopUpDialog(
            self._screen,
            info_txt,
            opts,
            has_shadow=True,
            on_close=self._batch_inst_opt
        )

        self._scene.add_effect(pop)

    def _on_change_job_inst(self) -> None:
        self.save()

    def _build_default_criteria(self) -> dict:
        res = {
            'crit_status': None,
            'crit_limit': '1000',
            'crit_offset': '0',
            'crit_from_date': datetime.date.today() - datetime.timedelta(days=90),
            'crit_to_date': datetime.date.today() + datetime.timedelta(days=3),
            'crit_batch': None,
        }

        if 'batch_inst_qry' in self._pod.cfg:
            qry = self._pod.cfg.pop('batch_inst_qry')

            if 'batch_id' in qry:
                res['crit_batch'] = qry['batch_id']

        return res

    def _load_crit_data(self) -> dict:
        lookups = self._pod.load_lookups()

        res = {
            'status': tui_util.couplet_to_dropdown(tBatchInst.Status_Couplet()),
            'batches': tui_util.couplet_to_dropdown(lookups['batches']),
        }

        return res

    def _reload_from_db(self, brec: tBatchInst) -> None:
        dbrec = self._pod.svr.batchinst_read(brec.id)
        brec._copy_from(dbrec)

    def _gen_dialog_info_text(self, brec: tBatchInst) -> str:
        mask = '%s%-18.18s : %s'
        nl = '\n'

        res = f'Batch Instance:                                             {nl}'
        res += mask % (nl, "ID", str(brec.id))
        res += mask % (nl, "Parent ID", str(brec.parent_id))

        res += mask % (nl, "Status", tBatchInst.Status_Couplet.get_value(brec.status))
        res += mask % (nl, "Run Date", str(brec.run_date))

        res += mask % (nl, "Start Date", brec.start_date)
        res += mask % (nl, "End Date", brec.end_date)

        return res

    def _batch_inst_opt(self, selected: int) -> None:
        brec = self.data['batchinst_grid']

        if selected == 1:
            self._pod.cfg['job_inst_qry'] = {'batchinst_id': brec.id}
            raise exceptions.NextScene("JobInstEnquiry")

        if selected == 2:
            qry = bJobInstQuery()

            qry.date_from = brec.run_date - datetime.timedelta(days=2)
            qry.date_to = datetime.date.today() + datetime.timedelta(days=2)
            qry.batchinst_id = brec.id
            qry.jobinst_status = [ tJobInst.Status_Couplet.key_failed ]

            ji_list = self._pod.svr.jobinst_list(bLazyLoad(0, 0), qry)

            if ji_list:
                job_res = self._pod.svr.jobinst_rerun(ji_list[-1].inst_rec.id, True)
                pop = widgets.PopUpDialog(
                    self._screen,
                    self._gen_rerun_jobinst_text(job_res),
                    ["OK", "JobInst Enquiry"],
                    has_shadow=True,
                    on_close=self._open_jobinst_enquiry
                )
            else:
                pop = widgets.PopUpDialog(self._screen, "No failed jobs found.", ["OK"], has_shadow=True)

            self._scene.add_effect(pop)

        self._refresh_gird_item(brec)
        return

    def _create_grid_item(self, brec: tBatchInst) -> tuple:
        lookups = self._pod.load_lookups()
        batch = lookups['batches'].get(brec.batch_id)

        return (
            [
                str(brec.id),
                str(brec.parent_id) if brec.parent_id else '',
                tBatchInst.Status_Couplet.get_value(brec.status),
                str(brec.run_date),
                str(brec.start_date) if brec.start_date else '',
                str(brec.end_date) if brec.end_date else '',
                batch or '',
            ],
            brec
        )

    def _refresh_gird_item(self, brec: tBatchInst) -> tuple:
        options = self._grid.options
        idx = 0

        while idx < len(options):
            if options[idx][1] == brec:
                options[idx] = self._create_grid_item(brec)
                return

            idx += 1

    def _gen_rerun_jobinst_text(self, inst: tJobInst) -> str:
        lookups = self._pod.load_lookups()
        mask = '%s%-18.18s : %s'
        nl = '\n'

        job = lookups['jobs'].get(inst.job_id)

        res = f'Reruning Job Instance:{nl}'
        res += mask % (nl, "ID", str(inst.id))
        res += mask % (nl, "Parent ID", str(inst.parent_id) if inst.parent_id else None)
        res += mask % (nl, "Job", job or '<???>')
        res += mask % (nl, "Status", tJobInst.Status_Couplet.get_value(inst.status))
        res += mask % (nl, "Priority", str(inst.priority))
        res += mask % (nl, "Process Date", str(inst.process_date))
        res += mask % (nl, 'Extra Args', inst.extra_args)

        return res

    def _open_jobinst_enquiry(self, selected: int) -> None:
        if selected == 1:
            brec = self.data['batchinst_grid']
            self._pod.cfg['job_inst_qry'] = {'batchinst_id': brec.id}
            raise exceptions.NextScene("JobInstEnquiry")
