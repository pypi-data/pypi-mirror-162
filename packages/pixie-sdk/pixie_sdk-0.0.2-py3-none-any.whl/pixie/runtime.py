from getpass import getpass

import inquirer
import sys

from pixie.context import PixieContext
from pixie.rendering import render_text

CLI_COLORS = {
    'PURPLE': '\033[35m',
    'CYAN':  '\033[36m',
    'BLUE':  '\033[34m',
    'GREY':  '\33[90m',
    'GREEN':  '\033[32m',
    'YELLOW':  '\033[33m',
    'RED':  '\033[31m',
    'BOLD':  '\033[1m',
    'UNDERLINE':  '\033[4m',
    'ITALIC':  '\033[3m',
    'END':  '\033[0m',
}

class PixieRuntime:
    def write(self, message: str, format=False):
        pass

    def ask(self, prompt):
        pass

    def print_todos(self, context: PixieContext):
        pass

    def print_notes(self, context: PixieContext):
        pass


class PixieConsoleRuntime(PixieRuntime):
    def log(self, message):
        self.write(message + '\n')

    def ask(self, prompt):
        name = prompt.get('name')
        default = prompt.get('default')
        description = prompt.get('description', name)
        if 'choices' in prompt:
            choices = prompt['choices']
            answers = inquirer.prompt([
                inquirer.List("p", message=description, choices=choices, default=default)
            ])
            if answers is None:
                raise KeyboardInterrupt()
            return answers["p"]

        if prompt.get('secure', False):
            answers = inquirer.prompt([
                inquirer.Password("p", message=description, default=default)
            ])
            if answers is None:
                raise KeyboardInterrupt()
            return answers["p"]
        else:
            answers = inquirer.prompt([
                inquirer.Text("p", message=description, default=default)
            ])
            if answers is None:
                raise KeyboardInterrupt()
            return answers["p"]
    
    def write(self, message: str, format=False):
        if format:
            sys.stdout.write(message.format(**CLI_COLORS))
        else:
            sys.stdout.write(message)
        sys.stdout.flush()

    def print_todos(self, context: PixieContext):
        if context.todos:
            self.write('\n{GREEN}{BOLD}TODO:{END}\n'.format(**CLI_COLORS))
            for todo in context.todos:
                todo_str = render_text(todo, context)
                self.write(f' [ ] {todo_str}\n')

    def print_notes(self, context: PixieContext):
        if context.notes:
            self.write('\n{BLUE}{BOLD}NOTES:{END}\n'.format(**CLI_COLORS))
            for note in context.notes:
                note_str = render_text(note, context)
                self.write(f'{note_str}\n')

