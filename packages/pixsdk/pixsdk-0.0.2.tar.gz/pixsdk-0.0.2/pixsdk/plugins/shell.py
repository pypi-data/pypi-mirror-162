from asyncio import subprocess
import subprocess
import os

from ..context import PixContext
from ..steps import PixStep
from ..runtime import PixRuntime
from ..plugin import PixPluginContext
from ..rendering import render_text

color = {
    'PURPLE': '\033[35m',
    'CYAN':  '\033[36m',
    'BLUE':  '\033[34m',
    'GREEN':  '\033[32m',
    'YELLOW':  '\033[33m',
    'RED':  '\033[31m',
    'BOLD':  '\033[1m',
    'UNDERLINE':  '\033[4m',
    'ITALIC':  '\033[3m',
    'END':  '\033[0m',
}


def init(context: PixPluginContext):
    context.add_step('shell', ShellStep())


class ShellStep(PixStep):
    def run(self, context: PixContext, step: dict, runtime: PixRuntime):
        commands = render_text(step['command'], context)
        term_colors = dict_to_str(color, 'TERM_%s="%s"\n')
        cmd = """
set +x -ae
%s
%s
""" % (term_colors, commands)
        subprocess.run(cmd, cwd=context.get('__target', '.'), check=True, shell=True)


def dict_to_str(d, fmt='%s=%s\n'):
    s = ''
    for x in d:
        s += fmt % (x, d[x])
    return s
