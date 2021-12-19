from io import StringIO

from behave import *

import tabsave
from features.environment import *


@given(u'there was no game save named "{game_save:w}"')
def step_impl(context, game_save):
    remove_game_saves(game_save)
    assert not game_save_exists(game_save), f'Expected {game_save} not to exist, but it exists.'


use_step_matcher("re")


@when(r'Alex tries to run `tabsave (\w+) ?([^`]*)`')
def step_impl(context, game_save: str, options_str: str):
    options = get_argument_list(options_str)
    context.add_result(Runnable(tabsave.main, (game_save, *options)))


@when(u'Alex runs `tabsave (\w+) ([^`]+)`')
def step_impl(context, game_save: str, options_str: str):
    options = get_argument_list(options_str)
    result = context.add_result(Runnable(tabsave.main, (game_save, *options)))
    if result.exception is not None:
        raise result.exception


@when(u'Alex runs `tabsave (\w+)`')
def step_impl(context, game_save: str):
    result = context.add_result(Runnable(tabsave.main, (game_save,)))
    if result.exception is not None:
        raise result.exception


use_step_matcher("parse")


@then(u'Alex should get an error')
def step_impl(context):
    assert get_next_run_result(context).exception is not None, f'Expected an error that was not found.'


@given(u'there was a game save named "{game_save:w}"')
def step_impl(context, game_save: str):
    create_game_save(game_save)
    assert game_save_exists(game_save), f'{game_save} was missing expected files.'


@then(u'game save "{game_save:w}" will have 1 backup which is a copy of the current save')
def step_impl(context, game_save: str):
    backup_dir = TEST_GAME_SAVE_DIR / 'backups' / game_save

    count = 0
    for path_shallow in backup_dir.iterdir():
        count += 1
        for path in path_shallow.iterdir():
            with open(path, 'r') as f:
                contents_in_backup = f.readlines()
            with open(TEST_GAME_SAVE_DIR / path.name) as f:
                contents_in_active_save = f.readlines()
            assert contents_in_backup == contents_in_active_save, f'{path} does not match contents of ' \
                                                                  f'{TEST_GAME_SAVE_DIR / path.name}.'
    assert count == 1, f'Expected 1 backup but found {count}.'
