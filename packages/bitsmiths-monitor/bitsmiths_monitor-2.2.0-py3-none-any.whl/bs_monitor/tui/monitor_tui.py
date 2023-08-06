import sys

from asciimatics.effects import Background
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics import exceptions

from mettle.db import IConnect

from bs_monitor.tui.pod_tui import PodTui
from bs_monitor.tui.batch import BatchEnquiry
from bs_monitor.tui.batch import BatchView
from bs_monitor.tui.batchinst import BatchInstEnquiry
from bs_monitor.tui.batchitem import BatchItemEnquiry
from bs_monitor.tui.batchitem import BatchItemView
from bs_monitor.tui.job import JobEnquiry
from bs_monitor.tui.job import JobView
from bs_monitor.tui.job import JobSpawnView
from bs_monitor.tui.jobinst import JobInstEnquiry
from bs_monitor.tui.mondate import MondateEnquiry
from bs_monitor.tui.mondate import MondateView
from bs_monitor.tui.main_menu import MainMenu


__last_scene = None
__pod = None



def __entry_point(screen: Scene, scene: Scene):
    global __pod

    bg = Background(screen)


    scenes = [
        Scene([bg, MainMenu(screen, __pod)], -1, name="MainMenu"),
        Scene([bg, BatchInstEnquiry(screen, __pod)], -1, name="BatchInstEnquiry"),
        Scene([bg, BatchEnquiry(screen, __pod)], -1, name="BatchEnquiry"),
        Scene([bg, BatchView(screen, __pod)], -1, name="BatchView"),
        Scene([bg, BatchItemEnquiry(screen, __pod)], -1, name="BatchItemEnquiry"),
        Scene([bg, BatchItemView(screen, __pod)], -1, name="BatchItemView"),
        Scene([bg, JobInstEnquiry(screen, __pod)], -1, name="JobInstEnquiry"),
        Scene([bg, JobEnquiry(screen, __pod)], -1, name="JobEnquiry"),
        Scene([bg, JobView(screen, __pod)], -1, name="JobView"),
        Scene([bg, JobSpawnView(screen, __pod)], -1, name="JobSpawnView"),
        Scene([bg, MondateEnquiry(screen, __pod)], -1, name="MondateEnquiry"),
        Scene([bg, MondateView(screen, __pod)], -1, name="MondateView"),
    ]

    screen.play(
        scenes,
        stop_on_resize=True,
        start_scene=scene,
        allow_int=True
    )


def main(dbcon: IConnect) -> int:
    global __pod
    global __last_scene

    __pod = PodTui(dbcon)

    while True:
        try:
            Screen.wrapper(__entry_point, catch_interrupt=True, arguments=[__last_scene])
            return 0
        except exceptions.ResizeScreenError as e:
            __last_scene = e.scene

    return 0


if __name__ == '__main__':

    def _init_dbcon() -> IConnect:
        from mettle.db.psycopg2.connect import Connect as Psycopg2Connect
        conn = Psycopg2Connect()
        conn.connect('postgresql://bs:dev@127.0.0.1/bs')

        return conn


    sys.exit(main(_init_dbcon()))
