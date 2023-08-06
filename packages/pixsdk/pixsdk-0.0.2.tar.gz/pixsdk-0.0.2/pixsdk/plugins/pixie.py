from re import T
from pixsdk.context import PixContext
from pixsdk.runtime import PixRuntime
from pixsdk.steps import PixStep
from ..plugin import PixPluginContext
from ..engine import execute_scaffold
from ..rendering import render_options


def init(context: PixPluginContext):
    context.add_step('pixsdk', PixStep())

class PixStep(PixStep):
    def run(self, context: PixContext, step: dict, runtime: PixRuntime):
        options = render_options(step, context)
        orig_package = context['__package']

        has_private_context = True
        actual_context = PixContext(options.get('context', {}))
        actual_context['__package'] = orig_package
        actual_context['__target'] = context['__target']
        actual_context['env'] = context['env']

        execute_scaffold(actual_context, options, runtime)
        if has_private_context:
            context.todos.extend(actual_context.todos)
            context.notes.extend(actual_context.notes)
        context['__package'] = orig_package
