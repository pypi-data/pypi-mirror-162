import importlib
import importlib
from importlib import util
import subprocess
import sys
import os

from pixsdk.context import PixContext
from pixsdk.runtime import PixRuntime
from ..steps import PixStep
from ..plugin import PixPluginContext
from ..rendering import render_options, render_text, render_value


def init(context: PixPluginContext):
    context.add_step("set_context", SetStep())
    context.add_step("add_note", AddNoteStep())
    context.add_step("add_todo", AddTodoStep())
    context.add_step("module", ModuleStep())
    context.add_step("file", FileStep())


class SetStep(PixStep):   
    def run(self, context: PixContext, step: dict, runtime: PixRuntime):
        context_names = step
        for context_name in context_names:
            context[context_name] = render_value(
                context_names[context_name], context)


class AddNoteStep(PixStep):
    def run(self, context: PixContext, step: str, runtime: PixRuntime):
        message = render_text(step, context)
        context.notes.append(message)


class AddTodoStep(PixStep):
    def run(self, context: PixContext, step: str, runtime: PixRuntime):
        message = render_text(step, context)
        context.todos.append(message)


class ModuleStep(PixStep):
    def run(self, context: PixContext, step: dict, runtime: PixRuntime):
        options = render_options(step, context)

        install_dependencies(options.get('dependencies', []))

        file = context.resolve_package_path(options['path'])
        spec = util.spec_from_file_location("module.name", file)
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        main_fn = getattr(foo, 'main')

        module_context = render_options(options.get('context', {}), context)

        return main_fn(module_context, options, runtime)


class FileStep(PixStep):
    def write(self, context: PixContext, step: dict, runtime: PixRuntime):
        options = render_options(step, context)

        path = context.resolve_target_path(options['path'])
        content = options.get('content')

        with open(path, 'w') as fhd:
            fhd.write(content)
    
    def read(self, context: PixContext, step: dict, runtime: PixRuntime):
        options = render_options(step, context)

        path = context.resolve_target_path(options['path'])

        with open(path, 'r') as fhd:
            return fhd.read()


def install_dependencies(dependencies):
    for dep in dependencies:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
