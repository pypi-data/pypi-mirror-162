import os.path
import logging

from mettle.db import IConnect

from bs_lib import Pod

from bs_monitor.monitor_server_impl import MonitorServerImpl

from bs_monitor.braze     import bBatchQuery


class PodTui(Pod):
    THEME_FILE = '.bs_monitor_tui_theme'

    def __init__(self, dbcon: IConnect) -> None:
        logger = logging.getLogger('bs_monitor_tui').addHandler(logging.NullHandler())
        Pod.__init__(self, {}, dbcon, logger, "[monitor-tui]")
        self.theme = self._read_theme()

        dao_name = None

        if dbcon.name().lower().find('postgres') >= 0:
            dao_name = 'postgresql'

        if not dao_name:
            raise Exception(f'No DAO module found for database connection: {dbcon.name()}')

        self.svr = MonitorServerImpl(self, dao_name, cli_mode=True)
        self.lookups = {}


    def load_lookups(self, force_refresh: bool = False) -> dict:
        if self.lookups and not force_refresh:
            return self.lookups

        job_list = self.svr.job_list(None, None, None)
        batch_list = self.svr.batch_list(None, bBatchQuery())
        jobs = {}
        job_grps = {}
        batches = {}
        batch_grps = {}

        for job in job_list:
            jobs[job.id] = job.name
            job_grps[job.group_id] = job.group_id

        for batch in batch_list:
            batches[batch.id] = batch.name
            batch_grps[batch.group_id] = batch.group_id

        self.lookups = {
            'jobs': jobs,
            'job_grps': job_grps,
            'batches': batches,
            'batch_grps': batch_grps,
        }

        return self.lookups


    def _read_theme(self) -> str:
        if os.path.exists(self.THEME_FILE):
            with open(self.THEME_FILE, 'rt') as fh:
                return fh.read() or 'default'

        return 'default'


    def write_theme(self, theme: str) -> None:
        with open(self.THEME_FILE, 'wt') as fh:
            fh.write(theme)

        self.theme = theme
