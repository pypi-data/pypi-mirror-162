from charset_normalizer import logging
from pixsdk.context import PixContext
from ..runtime import PixRuntime
from ..steps import PixStep
from ..plugin import PixPluginContext
from ..rendering import render_text


_log = logging.getLogger(__name__)


def init(context: PixPluginContext):
    context.add_step('log', LogStep())
    context.add_step('debug', DebugStep())
    context.add_step('print', PrintStep())


class LogStep(PixStep):
    # def resolve_fn(self, obj_name, fn_name, context):
    #     return getattr(_log, fn_name), False

    def run(self, context: PixContext, step: dict, runtime: PixRuntime):
        message = render_text(step['message'], context)
        _log.info(message)


class DebugStep(PixStep):
    def run(self, context: PixContext, step: dict, runtime: PixRuntime):
        message = render_text(step['message'], context)
        _log.debug(message)


class PrintStep(PixStep):
    def run(self, context: PixContext, step: dict, runtime: PixRuntime):
        message = render_text(step['message'], context)
        print(message)
