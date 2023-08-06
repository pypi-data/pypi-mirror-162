from cloudmesh.common.util import banner
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.debug import VERBOSE


class ProgressCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_progress(self, args, arguments):
        """
        ::

          Usage:
                progress PROGRESS [--status=STATUS] [--pid=PID] [--now] [KEY=VALUE...] [--sep=SEP] [--banner]

          Prints a progress line of the form


           "# cloudmesh status=ready progress=0 pid=$$ time='2022-08-05 16:29:40.228901' key1=value1 key2=value2"

          Arguments:
              PROGRESS   the progess in value from 0 to 100
              KEY=VALUE   the key value pars to be added

          Options:
              --status=STATUS      the status [default: running]
              --pid=PID            the PID
              --now                add a time of now
              --sep=SEP            separator when adding key=values
              --banner             creates also a banner when specified [default: None]

          Description:

            The example
                progress 50 --status=running --pid=101 --now user=gregor
            produces
                # cloudmesh status=running progress=0 pid=123 time='2022-08-05 16:29:40.228901' user=gregor
        """


        # arguments.FILE = arguments['--file'] or None

        # switch debug on

        values = arguments["KEY=VALUE"]

        map_parameters(arguments, "sep", "status", "pid", "now", "banner")

        if arguments.sep is None:
            arguments.sep = " "

        if len(values) > 0:
            values = (arguments.sep).join(values)
        else:
            values = None

        # VERBOSE(arguments)

        from cloudmesh.common.StopWatch import progress
        progress(status=arguments.status, progress=arguments.PROGRESS, pid=arguments.pid, time=arguments["--now"], stdout=True, append=values, with_banner=arguments.banner)



        return ""
