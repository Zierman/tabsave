import pathlib
import random
import shutil
import subprocess
import sys
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, Tuple, Callable

import tabsave

TEST_ROOT_DIR = pathlib.Path.home() / '.tabsave_test'
TEST_GAME_SAVE_DIR = TEST_ROOT_DIR / 'They Are Billions' / 'Saves'
CONFIG_FILE_PATH = TEST_ROOT_DIR / tabsave.CONFIG_FILE_NAME


class RunResult:
    def __init__(self, return_value=None, exception=None):
        self.return_value = return_value
        self.exception = exception

    def __str__(self):
        return {'return_value': self.return_value, 'exception': self.exception}.__str__()

    def __repr__(self):
        return {'return_value': self.return_value, 'exception': self.exception}.__repr__()

    def __eq__(self, other):
        if not isinstance(other, RunResult):
            return False
        else:
            return all(getattr(self, attr) == getattr(other, attr) for attr in ['return_value', 'exception'])


class Runnable:
    """A class that creates a callable that has pre-defined arguments"""

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{{callable: {self._dict['callable'].__name__}, args: {self._dict['args']}, " \
               f"kwargs: {self._dict['kwargs']}}}"

    def __init__(self, callable_to_run: Callable, *args, **kwargs):
        self._dict = {'callable': callable_to_run,
                      'args': args,
                      'kwargs': kwargs}

    def __call__(self, *args, **kwargs):

        return_value = None
        exception = None

        args = (*self._dict['args'], *args)
        tmp = kwargs
        kwargs = self._dict['kwargs'].copy()
        kwargs.update(tmp)
        del tmp

        try:
            return_value = self._dict['callable'](*args, **kwargs)
        except Exception as e:
            exception = e

        return RunResult(return_value, exception)


def before_all(context):
    # setup context
    context.my_results = []

    def _add_result(r: Runnable):
        result = r()
        context.my_results.append(result)
        return result

    context.add_result = _add_result


def before_scenario(context, scenario):
    # change the config path to a test location
    tabsave.Config._test_setup(CONFIG_FILE_PATH)

    # setup context
    context.my_results = []

    # create the test game save directory
    TEST_GAME_SAVE_DIR.mkdir(parents=True, exist_ok=True)

    # create config file if we are not testing its creation
    if 'config_setup_test' not in scenario.tags:
        config_dir_path_str = TEST_GAME_SAVE_DIR.resolve()

        # create the config file
        with open(CONFIG_FILE_PATH, 'w') as file:
            file.write(f'save_dir: {config_dir_path_str}\n')


def after_scenario(context, feature):
    # delete the test directory and all of its files
    shutil.rmtree(TEST_ROOT_DIR)


def game_save_exists(save_name: str) -> bool:
    return all((TEST_GAME_SAVE_DIR / f'{save_name}{ending}').is_file() for ending in ('.zxcheck', '.zxsav'))


def game_save_backup_exists(save_name) -> bool:
    return all((TEST_GAME_SAVE_DIR / f'{save_name}{ending}').is_file() for ending
               in ('_Backup.zxcheck', '_Backup.zxsav'))


def create_game_save(save_name: str, create_backupzx_files=False) -> Dict[pathlib.Path, int]:
    endings = ('.zxcheck', '.zxsav', '_Backup.zxcheck', '_Backup.zxsav') if create_backupzx_files \
        else ('.zxcheck', '.zxsav')

    d = {}
    for ending in endings:
        random_int = random.randint(0, 1000000)
        path = TEST_GAME_SAVE_DIR / f'{save_name}{ending}'
        d[path] = random_int
        with open(path, 'w') as file:
            file.write(f"{save_name} - {random_int}\n")
    return d


def remove_game_saves(save_name: str):
    endings = ('.zxcheck', '.zxsav', '_Backup.zxcheck', '_Backup.zxsav')
    for ending in endings:
        path = TEST_GAME_SAVE_DIR / f'{save_name}{ending}'
        if path.is_file():
            path.unlink()


def get_argument_list(raw_str: str) -> Tuple[str]:
    args = []
    arg = []
    escaped = False
    current_quote = ''
    for ch in raw_str:
        if escaped:
            arg.append(ch)
            escaped = False
        else:
            if ch == '\\':
                escaped = True
            elif current_quote:
                if ch != current_quote:
                    arg.append(ch)
                else:
                    args.append(''.join(arg))
                    arg = []
                    current_quote = ''
            elif ch == ' ':
                if arg:
                    args.append(''.join(arg))
                    arg = []
                else:
                    ...  # it's leading whitespace, just ignore it.
            elif ch in ['"', "'"] and not arg:  # leading quote
                current_quote = ch
            else:
                arg.append(ch)
    if arg:
        args.append(''.join(arg))
        arg = []
    if current_quote:
        raise ValueError(f'<{raw_str}> could not be parsed because of an unclosed {current_quote} quotation mark.')
    return tuple((arg for arg in args if isinstance(arg, str)))


def get_next_run_result(context) -> RunResult:
    return context.my_results.pop(0)
