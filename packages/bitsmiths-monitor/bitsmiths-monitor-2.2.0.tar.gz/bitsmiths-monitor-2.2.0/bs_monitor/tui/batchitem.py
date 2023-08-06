import asciimatics.event
from asciimatics import widgets
from asciimatics.screen import Screen

from asciimatics import exceptions

from bs_monitor.db.tables import tBatchItem

from bs_monitor.tui import tui_util
from bs_monitor.tui.pod_tui import PodTui


class BatchItemEnquiry(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(BatchItemEnquiry, self).__init__(
            screen, int(screen.height * 2 // 3), int(screen.width * 2 // 3), on_load=self._btn_refresh_click, has_shadow=True,
            hover_focus=True, can_scroll=True, reduce_cpu=True, title="Batch Item Enquiry"
        )

        self._pod = pod
        self._lookups = self._pod.load_lookups()
        self._parent_batch = self._pod.cfg.get('batch_item')
        self._header_lbl = widgets.Label("BATCH ITEM", align="^")
        self._is_new = False

        layout_head = widgets.Layout([100])
        layout_btns = widgets.Layout([1, 1, 1])
        layout_sep1 = widgets.Layout([100])
        layout_grid = widgets.Layout([100], fill_frame=True)
        layout_bi_btns = widgets.Layout([1, 1])

        self.add_layout(layout_head)
        self.add_layout(layout_sep1)
        self.add_layout(layout_btns)
        self.add_layout(layout_grid)
        self.add_layout(layout_bi_btns)

        layout_head.add_widget(self._header_lbl)
        layout_head.add_widget(widgets.Divider())

        layout_btns.add_widget(widgets.Button(f"Refresh {tui_util.KEY_HINT_REFRESH}", self._btn_refresh_click), 0)
        layout_btns.add_widget(widgets.Button(f"Back {tui_util.KEY_HINT_BACK}", self._btn_back_click), 1)
        layout_btns.add_widget(widgets.Button(f"Quit {tui_util.KEY_HINT_QUIT}", self._btn_quit_click), 2)

        self._grid = widgets.MultiColumnListBox(
            widgets.Widget.FILL_FRAME,
            [">10", "<40", "100%" ],
            [],
            titles=[
                "INDEX", "JOB", "EXTRA ARGS" ],
            name="batchitem_grid",
            add_scroll_bar=True,
            on_select=self._on_select_batch,
            on_change=self._on_change_batch,
        )

        layout_grid.add_widget(widgets.Divider())
        layout_grid.add_widget(self._grid)
        layout_grid.add_widget(widgets.Divider())

        self._btn_bi_create = widgets.Button(f"Create [{tui_util.KEY_HINT_CREATE}]", self._btn_bi_create_click, disabled=False)
        self._btn_bi_delete = widgets.Button(f"Delete [{tui_util.KEY_HINT_DELETE}]", self._btn_bi_delete_click, disabled=False)

        layout_bi_btns.add_widget(self._btn_bi_create, 0)
        layout_bi_btns.add_widget(self._btn_bi_delete, 1)

        self.fix()

    def process_event(self, event):
        if isinstance(event, asciimatics.event.KeyboardEvent):
            if tui_util.handle_f_keys(self._screen, self._scene, event):
                return

            if event.key_code == tui_util.KEY_REFRESH:
                self._btn_refresh_click()
            elif event.key_code == tui_util.KEY_BACK:
                self._btn_back_click()
            elif event.key_code == tui_util.KEY_DELETE:
                if not self._btn_bi_delete.disabled:
                    self._btn_bi_delete_click()
                return
            elif event.key_code == tui_util.KEY_CREATE:
                self._btn_bi_create_click()

        return super(BatchItemEnquiry, self).process_event(event)

    def _btn_refresh_click(self):
        self.set_theme(self._pod.theme)
        self.save()

        self._parent_batch = self._pod.cfg.get('batch_item')
        self._header_lbl.text = f"[{self._parent_batch.id}] - {self._parent_batch.name}"
        res = self._pod.svr.batchitem_list(self._parent_batch.id)
        options = []

        for x in res:
            options.append(self._create_grid_item(x))

        self._grid.options = options
        self._grid.value = None

    def _btn_back_click(self) -> None:
        raise exceptions.NextScene('BatchEnquiry')

    def _btn_quit_click(self) -> None:
        raise exceptions.StopApplication("User quit")

    def _on_select_batch(self) -> None:
        self.save()
        irec = self.data['batchitem_grid']

        self._reload_from_db(irec)
        info_txt = self._gen_dialog_info_text(irec)

        pop = widgets.PopUpDialog(
            self._screen,
            info_txt,
            ["OK", "EDIT"],
            has_shadow=True,
            on_close=self._batchitem_options
        )

        self._scene.add_effect(pop)

    def _on_change_batch(self) -> None:
        self.save()
        irec = self._grid.value
        self._btn_bi_delete.disabled = False if irec else True

    def _btn_bi_create_click(self) -> None:
        self._pod.cfg['batchitem_item'] = None
        raise exceptions.NextScene("BatchItemView")

    def _btn_bi_delete_click(self) -> None:
        self._scene.add_effect(
            widgets.PopUpDialog(
                self._screen,
                "Are you sure you want Delete?",
                tui_util.NO_YES_OPTIONS, has_shadow=True,
                on_close=self._confirm_delete
            )
        )

    def _reload_from_db(self, irec: tBatchItem) -> None:
        try:
            dbrec = self._pod.svr.batchitem_read(irec.id, irec.batch_id)
            irec._copy_from(dbrec)
        except Exception as ex:
            self._scene.add_effect(tui_util.pop_exception(self._screen, ex))
            return

    def _gen_dialog_info_text(self, irec: tBatchItem) -> str:
        mask = '%s%-18.18s : %s'
        nl = '\n'
        jname = self._lookups['jobs'].get(irec.job_id, tui_util.WTF_CAPTION)

        res = f'Batch Item:{nl}'
        res += mask % (nl, "ID", str(irec.id))
        res += mask % (nl, 'Job', f'{jname} [{irec.job_id}]')
        res += mask % (nl, 'Extra Args', irec.extra_args or '')
        res += nl
        res += mask % (nl, "Stamp By", irec.stamp_by)
        res += mask % (nl, "Stamp Tm", str(irec.stamp_tm))

        return res

    def _batchitem_options(self, selected: int) -> None:
        irec = self.data['batchitem_grid']

        if selected == 1:
            self._pod.cfg['batchitem_item'] = irec
            raise exceptions.NextScene("BatchItemView")

        self._refresh_gird_item(irec)

    def _create_grid_item(self, irec: tBatchItem) -> tuple:
        return (
            [
                str(irec.id),
                self._lookups['jobs'].get(irec.job_id) or tui_util.WTF_CAPTION,
                irec.extra_args or ''
            ],
            irec
        )

    def _refresh_gird_item(self, irec: tBatchItem) -> tuple:
        options = self._grid.options
        idx = 0

        while idx < len(options):
            if options[idx][1] == irec:
                options[idx] = self._create_grid_item(irec)
                return

            idx += 1

    def _confirm_delete(self, selected: int) -> None:
        irec = self.data['batchitem_grid']

        if selected == 0:
            self._refresh_gird_item(irec)
            return

        try:
            self._pod.svr.batchitem_delete(irec.id, irec.batch_id)
            self._btn_refresh_click()
        except Exception as x:
            self._scene.add_effect(tui_util.pop_exception(self._screen, x))
            return


class BatchItemView(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(BatchItemView, self).__init__(
            screen, 18, 80, hover_focus=True, can_scroll=False,
            reduce_cpu=True, title="Batch Item Details"
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

        layout_form.add_widget(widgets.Text("Index:", "id", validator=tui_util.validator_numeric(), max_length=3))
        layout_form.add_widget(widgets.DropdownList( tui_util.couplet_to_dropdown(lookups['jobs'], False), "Job:", "job_id"))
        layout_form.add_widget(widgets.Text("Extra Args:", "extra_args", max_length=256))
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

        return super(BatchItemView, self).process_event(event)

    def reset(self):
        super(BatchItemView, self).reset()
        self.set_theme(self._pod.theme)

        item = self._pod.cfg['batchitem_item']

        if item is None:
            pb = self._pod.cfg.get('batch_item')
            self._is_new = True
            self._rec = tBatchItem(999, pb.id)
        else:
            self._is_new = False
            self._rec = self._pod.svr.batchitem_read(item.id, item.batch_id)

        self.data = {
            'id': str(self._rec.id),
            'job_id': self._rec.job_id or None,
            'extra_args': self._rec.extra_args or '',
            'stamp_by': self._rec.stamp_by or '',
            'stamp_tm': self._rec.stamp_tm.isoformat() if self._rec.stamp_tm else '',
        }

    def _ok(self):
        self.save()

        if not self._validate_record():
            return

        old_id = self._rec.id
        tui_util.assign_diff(self._rec, self.data, 'id', int)
        new_id = self._rec.id
        self._rec.id = old_id

        chg = False
        chg = tui_util.assign_diff(self._rec, self.data, 'job_id', int) or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'extra_args') or chg

        try:
            if self._is_new:
                self._pod.svr.batchitem_create(self._rec)
                self._is_new = False
                return

            if chg:
                tmp = self._pod.svr.batchitem_update(self._rec)
                self._rec._copy_from(tmp)
        except Exception as x:
            self._scene.add_effect(tui_util.pop_exception(self._screen, x))
            return

        if old_id != new_id:
            try:
                self._pod.svr.batchitem_shift(old_id, self._rec.batch_id, new_id - old_id)
            except Exception as x:
                self._rec.id = old_id
                self._scene.add_effect(tui_util.pop_exception(self._screen, x))
                return


        raise exceptions.NextScene("BatchItemEnquiry")

    def _cancel(self):
        raise exceptions.NextScene("BatchItemEnquiry")

    def _validate_record(self) -> bool:
        pop = None
        idx = int(self.data['id'])

        if idx < 1:
            pop = widgets.PopUpDialog(self._screen, "Index cannot be less than 1.", ["OK"], has_shadow=True)

        if pop:
            self._scene.add_effect(pop)
            return False

        return True
