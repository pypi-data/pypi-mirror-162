import asciimatics.event
import datetime

from asciimatics import widgets
from asciimatics.screen import Screen

from asciimatics import exceptions

from bs_monitor.db.tables import tJob
from bs_monitor.db.tables import tJobInst

from bs_monitor.tui import tui_util
from bs_monitor.tui.pod_tui import PodTui


class JobEnquiry(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(JobEnquiry, self).__init__(
            screen, screen.height, screen.width, on_load=self._btn_refresh_click, has_shadow=True, hover_focus=True,
            can_scroll=True, reduce_cpu=True, title="Job Enquiry"
        )

        self.data = {}
        self._pod = pod

        layout_btns = widgets.Layout([1, 1, 1])
        layout_grid = widgets.Layout([100], fill_frame=True)
        layout_grid_btns = widgets.Layout([1, 1, 1])

        self.add_layout(layout_btns)
        self.add_layout(layout_grid)
        self.add_layout(layout_grid_btns)

        layout_btns.add_widget(widgets.Button(f"Refresh [{tui_util.KEY_HINT_REFRESH}]", self._btn_refresh_click), 0)
        layout_btns.add_widget(widgets.Button(f"Back [{tui_util.KEY_HINT_BACK}]", self._btn_back_click), 1)
        layout_btns.add_widget(widgets.Button(f"Quit [{tui_util.KEY_HINT_QUIT}]", self._btn_quit_click), 2)

        self._grid = widgets.MultiColumnListBox(
            widgets.Widget.FILL_FRAME,
            [">10", "<32", "<32", ">10", "100%" ],
            [],
            titles=["ID", "NAME", "GROUP", "PRIORITY", "PATH & ARGS"],
            name="job_grid",
            add_scroll_bar=True,
            on_select=self._on_select_job_inst,
            on_change=self._on_change_job_inst,
        )

        layout_grid.add_widget(widgets.Divider())
        layout_grid.add_widget(self._grid)
        layout_grid.add_widget(widgets.Divider())

        self._btn_spawn = widgets.Button("Spawn", self._btn_spawn_click, disabled=True)
        self._btn_edit = widgets.Button(f"Edit [{tui_util.KEY_HINT_EDIT}]", self._btn_edit_click, disabled=True)
        self._btn_create = widgets.Button(f"Create [{tui_util.KEY_HINT_CREATE}]", self._btn_create_click)

        layout_grid_btns.add_widget(self._btn_spawn, 0)
        layout_grid_btns.add_widget(self._btn_edit, 1)
        layout_grid_btns.add_widget(self._btn_create, 2)

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
                if not self._btn_edit.disabled:
                    self._btn_edit_click()
                return
            elif event.key_code == tui_util.KEY_CREATE:
                self._btn_create_click()

        return super(JobEnquiry, self).process_event(event)

    def _btn_refresh_click(self):
        self.set_theme(self._pod.theme)
        self.save()

        res = self._pod.svr.job_list(None, None, None)
        options = []

        for x in res:
            options.append(self._create_grid_item(x))

        self._grid.options = options
        self._grid.value = None


    def _btn_back_click(self) -> None:
        raise exceptions.NextScene('MainMenu')

    def _btn_quit_click(self) -> None:
        raise exceptions.StopApplication("User quit")

    def _on_select_job_inst(self) -> None:
        self.save()
        jrec = self.data['job_grid']

        self._reload_from_db(jrec)
        info_txt = self._gen_dialog_info_text(jrec)
        pop = widgets.PopUpDialog(self._screen, info_txt, ["OK", "Spawn", "Edit"], has_shadow=True, on_close=self._job_opts)
        self._scene.add_effect(pop)

    def _on_change_job_inst(self) -> None:
        self.save()
        self._btn_spawn.disabled = True
        self._btn_edit.disabled = True

        jrec = self._grid.value

        if not jrec:
            return

        self._btn_spawn.disabled = False
        self._btn_edit.disabled = False

    def _job_opts(self, selected: int) -> None:
        job = self.data['job_grid']

        if selected == 0:
            self._refresh_gird_item(job)
            return

        if selected == 1:
            self._btn_spawn_click()
            return

        if selected == 2:
            self._btn_edit_click()
            return

    def _btn_spawn_click(self) -> None:
        self._pod.cfg['spawn_job'] = self._grid.value
        raise exceptions.NextScene("JobSpawnView")

    def _btn_edit_click(self) -> None:
        self._pod.cfg['job_item'] = self._grid.value
        raise exceptions.NextScene("JobView")

    def _btn_create_click(self) -> None:
        self._pod.cfg['job_item'] = None
        raise exceptions.NextScene("JobView")

    def _reload_from_db(self, jrec: tJob) -> None:
        dbrec = self._pod.svr.job_read(jrec.id, None)
        jrec._copy_from(dbrec)

    def _create_grid_item(self, jrec: tJob) -> tuple:
        return (
            [
                str(jrec.id),
                jrec.name,
                jrec.group_id,
                str(jrec.priority),
                f'{jrec.program_path} {jrec.program_args or ""}',
            ],
            jrec
        )

    def _refresh_gird_item(self, jrec: tJob) -> tuple:
        options = self._grid.options
        idx = 0

        while idx < len(options):
            if options[idx][1] == jrec:
                options[idx] = self._create_grid_item(jrec)
                return

            idx += 1

    def _gen_dialog_info_text(self, jrec: tJob) -> str:
        mask = '%s%-18.18s : %s'
        nl = '\n'

        res = mask % ('', "ID", str(jrec.id))
        res += mask % (nl, 'Name', jrec.name)
        res += mask % (nl, 'Group', jrec.group_id)
        res += mask % (nl, 'Priority', str(jrec.priority))
        res += mask % (nl, 'Path', jrec.program_path)
        res += mask % (nl, 'Args', jrec.program_args)

        res += nl
        res += mask % (nl, 'Stamp By', jrec.stamp_by)
        res += mask % (nl, 'Stamp Tm', str(jrec.stamp_tm))

        return res


class JobView(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(JobView, self).__init__(
            screen, 12, 80, hover_focus=True, can_scroll=False,
            reduce_cpu=True, title="Job Details"
        )

        self._pod = pod
        self._rec = None

        layout_form = widgets.Layout([100], fill_frame=True)
        layout_btns = widgets.Layout([1, 1])

        self.add_layout(layout_form)
        self.add_layout(layout_btns)

        layout_form.add_widget(widgets.Text("ID:", "id", readonly=True))
        layout_form.add_widget(widgets.Text("Name:", "name", max_length=256))
        layout_form.add_widget(widgets.Text("Group:", "group_id", max_length=128))
        layout_form.add_widget(widgets.Text("Priority:", "priority", validator=tui_util.validator_numeric(), max_length=2))
        layout_form.add_widget(widgets.Text("Program Path:", "program_path", max_length=256))
        layout_form.add_widget(widgets.Text("Program Args:", "program_args", max_length=256))
        layout_form.add_widget(widgets.Text("Stamp By:", "stamp_by", readonly=True))
        layout_form.add_widget(widgets.Text("Stamp Tm:", "stamp_tm", readonly=True))

        layout_form.add_widget(widgets.Divider())

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

        return super(JobView, self).process_event(event)

    def reset(self):
        super(JobView, self).reset()
        self.set_theme(self._pod.theme)

        item = self._pod.cfg['job_item']

        if item is None:
            self._rec = tJob()
            self._rec.priority = 10
        else:
            self._rec = self._pod.svr.job_read(item.id, None)

        self.data = {
            'id': str(self._rec.id) if self._rec.id else '<NEW>',
            'name': self._rec.name,
            'group_id': self._rec.group_id,
            'priority': str(self._rec.priority),
            'program_path': self._rec.program_path,
            'program_args': self._rec.program_args,
            'stamp_by': self._rec.stamp_by,
            'stamp_tm': self._rec.stamp_tm.isoformat() if self._rec.stamp_tm else '',
        }

    def _ok(self):
        self.save()

        if not self._validate_record():
            return

        chg = False
        chg = tui_util.assign_diff(self._rec, self.data, 'name') or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'group_id') or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'program_path') or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'program_args') or chg
        chg = tui_util.assign_diff(self._rec, self.data, 'priority', int) or chg

        try:
            if self._rec.id == 0:
                self._pod.svr.job_create(self._rec)
            else:
                if chg:
                    self._pod.svr.job_update(self._rec)
        except Exception as x:
            self._scene.add_effect(tui_util.pop_exception(self._screen, x))
            return

        raise exceptions.NextScene("JobEnquiry")

    def _cancel(self):
        raise exceptions.NextScene("JobEnquiry")

    def _validate_record(self) -> bool:
        pop = None

        if not self.data['name']:
            pop = widgets.PopUpDialog(self._screen, "Name is required.", ["OK"], has_shadow=True)
        elif not self.data['group_id']:
            pop = widgets.PopUpDialog(self._screen, "Group is required.", ["OK"], has_shadow=True)
        elif not self.data['program_path']:
            pop = widgets.PopUpDialog(self._screen, "Program Path is required.", ["OK"], has_shadow=True)
        elif not self.data['priority']:
            pop = widgets.PopUpDialog(self._screen, "Priority is required.", ["OK"], has_shadow=True)

        if pop:
            self._scene.add_effect(pop)
            return False

        return True


class JobSpawnView(widgets.Frame):
    def __init__(self, screen: Screen, pod: PodTui):
        super(JobSpawnView, self).__init__(
            screen, 12, 80, hover_focus=True, can_scroll=False,
            reduce_cpu=True, title="Spawn New Job"
        )

        self._pod = pod
        self._job = None

        layout_form = widgets.Layout([100], fill_frame=True)
        layout_sep = widgets.Layout([100])
        layout_btns = widgets.Layout([1, 1])

        self.add_layout(layout_form)
        self.add_layout(layout_sep)
        self.add_layout(layout_btns)

        layout_form.add_widget(widgets.Text("Job ID:", "job_id", readonly=True))
        layout_form.add_widget(widgets.Text("Job Name:", "job_name", readonly=True))
        layout_form.add_widget(widgets.Text("Program Path:", "program_path", readonly=True))
        layout_form.add_widget(widgets.Text("Program Args:", "program_args", readonly=True))
        layout_form.add_widget(widgets.Text("Priority:", "priority", validator=tui_util.validator_numeric(), max_length=2))
        layout_form.add_widget(widgets.Text("Extra Args:", "extra_args"))

        layout_form.add_widget(widgets.Divider())

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

        return super(JobSpawnView, self).process_event(event)

    def reset(self):
        super(JobSpawnView, self).reset()
        self.set_theme(self._pod.theme)

        self._job = self._pod.cfg['spawn_job']

        self.data = {
            'job_id': str(self._job.id),
            'job_name': self._job.name,
            'program_path': self._job.program_path,
            'program_args': self._job.program_args,
            'priority': str(self._job.priority),
            'extra_args': '',
        }

    def _ok(self):
        self.save()

        if not self._validate_record():
            return

        value = {'priority': self._job.priority}
        tui_util.assign_diff(value, self.data, 'priority', int)

        srec = self._pod.svr.job_schedule(
            self._job.id, None, datetime.datetime.now(), self.data['extra_args'], value['priority'], None
        )

        pop = widgets.PopUpDialog(
            self._screen,
            self._gen_spawn_info_text(srec),
            ["OK", "JobInst Enquiry"],
            has_shadow=True,
            on_close=self._spawn_done
        )

        self._scene.add_effect(pop)

    def _cancel(self):
        raise exceptions.NextScene("JobEnquiry")


    def _validate_record(self) -> bool:
        pop = None

        if not self.data['priority']:
            pop = widgets.PopUpDialog(self._screen, "Priority is required.", ["OK"], has_shadow=True)

        if pop:
            self._scene.add_effect(pop)
            return False

        return True

    def _gen_spawn_info_text(self, inst: tJobInst) -> str:
        mask = '%s%-18.18s : %s'
        nl = '\n'

        res = f'Job Instance Spawn OK:{nl}'
        res += mask % (nl, "ID", str(inst.id))
        res += mask % (nl, "Status", tJobInst.Status_Couplet.get_value(inst.status))
        res += mask % (nl, "Priority", str(inst.priority))
        res += mask % (nl, "Process Date", str(inst.process_date))
        res += mask % (nl, 'Extra Args', inst.extra_args)

        return res

    def _spawn_done(self, selected: int) -> None:
        if selected == 1:
            raise exceptions.NextScene("JobInstEnquiry")

        raise exceptions.NextScene("JobEnquiry")
