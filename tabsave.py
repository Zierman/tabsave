#!/usr/bin/env python3
from __future__ import annotations
import argparse
import shutil
import sys
from functools import total_ordering
from pathlib import Path
from shutil import copy2
from typing import Optional, Union, Callable, overload
import yaml

MAX_FILENAME_LENGTH = 30


def _can_expand_to_match(abr: str, target: str) -> bool:
    """Returns True if abr is an abbreviation of the target or is equal to the target"""
    can_expand_to_match = False
    if len(abr) <= len(target):
        can_expand_to_match = True
        for a, t in zip(abr, target):
            if a != t:
                can_expand_to_match = False
    return can_expand_to_match


def _yn_input(prompt: str, repeat_prompt=None, allow_none=False) -> Optional[str]:
    """ Asks a yes or no question and returns 'y' if the user answered yes, or 'n' if the user entered no."""
    answer = input(prompt).strip().lower()
    if _can_expand_to_match(answer, 'yes'):
        return 'y'

    if _can_expand_to_match(answer, 'no'):
        return 'n'

    if allow_none:
        return None
    else:
        if repeat_prompt is None:
            repeat_prompt = prompt
        return _yn_input(repeat_prompt, repeat_prompt, allow_none)


def _mkdir_if_needed(path: Path) -> None:
    """ Makes a directory if needed

    Args:
        path: the path to the directory

    Returns: None

    Raises: NotADirectoryError if the path is not for a directory.

    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    elif not path.is_dir():
        raise NotADirectoryError(f'{path} is not a directory.')


def _can_parse_to_int(s: str):
    """Checks if the string can be parsed to an int."""
    try:
        int(s)
        return True
    except (ValueError, TypeError):
        return False


class SingletonError(RuntimeError):
    """An Error to be thrown if trying to create a second instance of a singleton class."""
    def __init__(self, cls, instance, *args):
        """ Initializes the error.

        Args:
            cls: The class of the singleton.
            instance: The instance of the singleton that may be accessed in an except block.
            *args: any other arguments that will be passed to the super's __init__ method.
        """
        self.singleton_class = cls
        self.singleton_instance = instance
        if args:
            super().__init__(args)
        else:
            super().__init__(f"{cls} already has an instance.")


class Config:
    """A singleton class that allows configuration information to be saved to and loaded from file."""
    _instance = None

    @classmethod
    def instance(cls) -> Config:
        """Gets the instance of the class or creates one if needed."""
        if Config._instance is None:
            Config._instance = Config()
        return Config._instance

    def __init__(self):

        # enforce singleton behaviour
        if Config._instance:
            raise SingletonError(Config, Config._instance)

        # make the config directory if needed
        config_dir = Path.home() / '.tabsave'
        _mkdir_if_needed(config_dir)

        # create the config file if needed
        config_path = config_dir / 'tabsave_config.yml'
        if not config_path.exists():
            with open(config_path, 'w') as cfg_file:
                path = None
                while path is None:
                    path = input('We need to know the absolute path to hey Are Billions save directory.\nPath: ')
                    if not Path(path).is_dir():
                        print('That was not a directory... try again.')
                        path = None
                cfg_file.write(f'save_dir: {path}\n')

        # read the config file and store the information.
        with open(config_path, 'r') as cfg_file:
            cfg = yaml.safe_load(cfg_file)
        self.save_dir = Path(cfg['save_dir'])


def get_save_dir() -> Path:
    """Gets the path to the save directory."""
    d = Config.instance().save_dir
    if not d.is_dir():
        raise NotADirectoryError(f'{d} is not a directory.')
    return d


def get_backup_root_dir() -> Path:
    """Gets the path to the shallowest backup directory."""
    d = Config.instance().save_dir / 'backups'
    if not d.is_dir():
        raise NotADirectoryError(f'{d} is not a directory.')
    return d


class InvalidBackupDirectoryNameError(ValueError):
    """An error to be raised if the backup directory name is invalid."""
    ...


@total_ordering
class Backup:
    """A class that represents an individual backup object."""
    _yaml_extractables = ['message']
    metadata_filename = 'metadata.yml'

    def _set_backup_number_from_dir(self):
        """Extracts the backup number from the directory name."""

        # find index of first non-decimal character in directory name (to be used in extracting backup number)
        i = 0
        for ch in self.dir.name:
            if ch.isdecimal():
                i += 1

        # Sets the number to the integer extracted from the start of the name
        self.number = int(self.dir.name[:i])

    @property
    def yaml_path(self) -> Path:
        """The path to the backup's yaml metadata file."""
        return self.dir / Backup.metadata_filename

    def _set_attributes_from_yaml(self) -> None:
        """Extracts the attributes from file if the file exists, else leaves default values as is."""
        if self.yaml_path.is_file():
            with open(self.yaml_path, 'r') as file:
                results = yaml.safe_load(file)

            for yaml_extractable in Backup._yaml_extractables:
                try:
                    setattr(self, yaml_extractable, results[yaml_extractable])
                except KeyError:
                    ...  # the item is not in the yaml file... just leave it as None

    def __init__(self, backup_dir: Path, message: str = None):
        self.dir = backup_dir
        self.message = message
        try:
            self._set_backup_number_from_dir()
        except ValueError as e:
            msg = f'Backup directories must start with a number. Could not extract backup number from "{backup_dir}".'
            raise InvalidBackupDirectoryNameError(msg) from e

        # create the backup directory if needed
        if not self.dir.exists():
            self.dir.mkdir(parents=True)

        # create or update yaml file within backup directory
        to_save = {yaml_extractable: getattr(self, yaml_extractable)
                   for yaml_extractable in Backup._yaml_extractables
                   if getattr(self, yaml_extractable) is not None}
        if to_save:
            with open(self.yaml_path, 'w') as file:
                yaml.safe_dump(to_save, file)

    @classmethod
    def load(cls, backup_dir: Path) -> Backup:
        """Loads the backup object from filesystem."""
        backup = Backup(backup_dir)
        backup._set_attributes_from_yaml()
        return backup

    def __eq__(self, other):
        if isinstance(other, Backup):
            return self.number.__eq__(other.number)
        else:
            raise TypeError(f'{type(self)} cannot be compared to {type(other)}')

    def __lt__(self, other):
        if isinstance(other, Backup):
            return self.number.__lt__(other.number)
        else:
            raise TypeError(f'{type(self)} cannot be compared to {type(other)}')


class GameSave:
    save_dir = get_save_dir()

    def __init__(self, name: str):

        if not name or not isinstance(name, str):
            raise ValueError(f'name must be a non-empty string')
        if not GameSave.save_dir.is_dir():
            raise NotADirectoryError(f'{self.save_dir} is not a directory.')

        self.backup_base_dir: Path = get_backup_root_dir() / name
        _mkdir_if_needed(self.backup_base_dir)
        self.name: str = name

        endings = ['.zxcheck', '.zxsav', '_Backup.zxcheck', '_Backup.zxsav']
        self.base_filenames = [f'{name}{e}' for e in endings]
        self.backups = list(Backup.load(d) for d in self.backup_base_dir.iterdir())

    def _copy_all(self, source: Union[Path, Backup], destination: Union[Path, Backup]):

        source_dir = source if isinstance(source, Path) else source.dir
        destination_dir = destination if isinstance(destination, Path) else destination.dir

        _mkdir_if_needed(destination_dir)

        transfer_params_list = []
        for filename in self.base_filenames:
            source_path = source_dir / filename
            destination = destination_dir / filename
            if not source_path.is_file():
                if '_Backup.zx' in source_path.name:
                    continue  # without adding to params list
                raise FileNotFoundError(f'Could not copy {source_path} to {destination} '
                                        f'because the source is not a file.')
            transfer_params_list.append((source_path, destination))
        for source, destination in transfer_params_list:
            copy2(source, destination, follow_symlinks=True)

    def _get_max_backup_dir_int(self, *, default=None):
        if self.backups:
            return max((b.number for b in self.backups))
        else:  # there are no backups
            return default

    def backup(self, n: Optional[int] = None, message: Optional[str] = None):
        if n is None:  # check for next integer starting with 1 if none found
            n = self._get_max_backup_dir_int(default=0) + 1
        if message:
            processed_msg = str(ch if ch.isalnum or ch == ' ' else '_' for ch in message)
            processed_msg = processed_msg.strip()
            dir_name = f'{n}' if MAX_FILENAME_LENGTH < len(f'{n} - {processed_msg}') else f'{n} - {processed_msg}'
            backup = Backup(self.backup_base_dir / f'{dir_name}', message)
        else:
            backup = Backup(self.backup_base_dir / f'{n}')
        self._copy_all(self.save_dir, backup)

    def restore(self, n: Optional[int] = None):
        if n is None:  # check for next integer starting with 1 if none found
            n = self._get_max_backup_dir_int(default=None)
            if n is None:
                raise NotADirectoryError(f'No backup directories found.')
        if n != 0:
            # create a temporary backup of the active save files in case this is used on accident. The temp index is 0.
            self._copy_all(self.save_dir, self.backup_base_dir / '0')

        # restore the backup.
        self._copy_all(self.backup_base_dir / f'{n}', self.save_dir)

    def get_list(self,
                 verbose: Optional[bool] = None,
                 *,
                 include_path: bool = False,
                 include_message: bool = False) -> str:
        backups = [Backup.load(backup_dir)
                   for backup_dir
                   in self.backup_base_dir.iterdir()
                   if backup_dir.is_dir() and _can_parse_to_int(backup_dir.name)]

        lines = []

        if not backups:
            if verbose:
                lines.append(f'{self.name} has no backups.')
            return '\n'.join(lines)

        class _Field:
            def __init__(self, name: str, label: str, get_value_callable: Callable[[Backup], str], included):
                self.name = name
                self._label = label
                self._get_value_callable = get_value_callable
                self.max_column_width = max((len(label), *(len(get_value_callable(b)) for b
                                                           in backups if get_value_callable(b) is not None)))

                self.included = included

            def get_label(self, *, centered=False):
                if centered:
                    return self._label.center(self.max_column_width)
                else:
                    return f'{self._label:{self.max_column_width}}'

            def _get_value(self, b: Backup):
                val_str = self._get_value_callable(b)
                if val_str is not None:
                    return f'{val_str:{self.max_column_width}}'
                else:
                    return None

            def get_value(self, b: Backup):
                s = self._get_value(b)
                return s if s is not None else '-------'.center(self.max_column_width)

        fields = (_Field('number', 'Number', lambda b: f'{b.number}', True),
                  _Field('path', 'Path_to_Directory', lambda b: f'"{b.dir}"', include_path),
                  _Field('message', 'Message', lambda b: f'{b.message}' if b.message is not None else None,
                         include_message))
        fields = tuple(field for field in fields if field.included)

        # print the column labels.
        lines.append('    '.join(f.get_label(centered=True) for f in fields))

        # print divider
        lines.append('-' * len(lines[0]))

        # print each row
        for b in sorted(backups):
            lines.append('    '.join(f.get_value(b) for f in fields))
        return '\n'.join(lines)

    @overload
    def list(self,
             verbose: Optional[bool] = None,
             *,
             include_path: bool = False,
             include_message: bool = False) -> None:
        ...

    def list(self, *args, **kwargs) -> None:
        print(self.get_list(*args, **kwargs))

    def delete(self, require_confirmation=True):
        if require_confirmation:
            a = _yn_input(f'Are you certain that you want to delete all backups for the '
                          f'They are Billions save {self.name!r}? (yes/no):')
        else:
            a = 'y'

        if a == 'y':
            shutil.rmtree(self.backup_base_dir)


def list_all(verbose: Optional[bool] = None,
             *,
             include_path: bool = False,
             include_message: bool = False,
             padding: Optional[int] = None):
    if padding is None:
        padding = 2
    elif padding < 0:
        raise ValueError('padding must be non-negative')
    else:
        padding = int(padding)
    pad = ' ' * padding

    saves = (GameSave(directory.name) for directory in get_backup_root_dir().iterdir())
    sections = []
    max_width = 0

    # get lines for each section
    for save in saves:
        sections.append([f'{save.name} has {len(save.backups)} backups'])
        if verbose:
            lines = sections[-1]
            listing = save.get_list(verbose=verbose, include_path=include_path, include_message=include_message)
            if isinstance(listing, str):
                lines.extend(listing.split('\n'))
            else:
                lines.extend(listing)

    # get max width
    for section in sections:
        for line in section:
            if len(line) > max_width:
                max_width = len(line)
    max_width += padding * 2

    # print
    if verbose:
        print(f'*{"*" * max_width}*')
        for section in sections:
            print(f"*{' ' * max_width}*")
            top_line = section[0]
            other_lines = section[1:]
            print(f"*{top_line:^{max_width}}*")
            print(f"*{'.' * max_width}*")
            print(f"*{' ' * max_width}*")
            for line in other_lines:
                line = f'{pad}{line}'
                print(f"*{line:<{max_width}}*")

            print(f"*{' ' * max_width}*")
            print(f"*{'*' * max_width}*")
    else:
        for section in sections:
            print(section[0])


def delete_all():
    raise NotImplementedError  # FIXME


def main(args=None) -> int:
    # if no args where provided, show help message
    if not args:
        return main(['-h'])

    # set up and parse arguments
    p = argparse.ArgumentParser(description='This tool allows a user to backup or restore a save from the game '
                                            'They Are Billions.')
    p.save_choice_group = p.add_mutually_exclusive_group()
    p.normal_group = p.save_choice_group.add_argument_group()

    if not any(no_name_arg in args for no_name_arg in ('-L', '--list-all', '--delete-all')):
        p.normal_group.add_argument('name', help='The name of the save')

    p.mode_group = p.normal_group.add_mutually_exclusive_group()
    p.output_group = p.add_mutually_exclusive_group()

    p.mode_group.add_argument('-b', '--backup',
                              action='store_true',
                              help='Backup active file. [DEFAULT_MODE]')

    p.mode_group.add_argument('-r', '--restore',
                              action='store_true',
                              help='Restore backup fail.')

    p.mode_group.add_argument('-l', '--list',
                              action='store_true',
                              help='Lists all backups for particular save.')

    p.save_choice_group.add_argument('-L', '--list-all',
                                     action='store_true',
                                     help='Lists all backups for all saves.')

    p.mode_group.add_argument('--delete',
                              action='store_true',
                              help='Deletes all backups for the save.')

    p.save_choice_group.add_argument('--delete-all',
                                     action='store_true',
                                     help='Deletes all backups for all saves.')

    p.add_argument('-n',
                   type=int,
                   help='The index to use. Will save to new index or restore greatest index if not specified.')

    p.add_argument('-p', '--path',
                   action='store_true',
                   help='Used to include path in listings.')

    p.add_argument('-y', '--auto-confirm',
                   action='store_true',
                   help='When used all confirmation dialogs will be auto completed.')

    if any(help_arg in args for help_arg in ('-h', '--help')):
        p.add_argument('-m', '--message',
                       help='Includes message in list or declair a message when creating a backup.')
    elif any(list_arg in args for list_arg in ('-L', '--list-all', '-l', '--list')):
        p.add_argument('-m', '--message',
                       action='store_true',
                       help='Includes message in list.')
    else:
        p.add_argument('-m', '--message',
                       help='Used to provide a message.')

    p.output_group.add_argument('-v', '--verbose',
                                action='store_true',
                                help='Outputs more information.')

    args = p.parse_args(args)

    # extract args
    n = args.n
    auto_confirm = args.auto_confirm

    if args.delete_all:
        delete_all()
    elif args.list_all:
        list_all(verbose=args.verbose,
                 include_path=args.path,
                 include_message=args.message)
    else:
        game_save = GameSave(args.name)

        # run the program according to the specified mode.
        if args.list:
            game_save.list(verbose=args.verbose,
                           include_path=args.path,
                           include_message=args.message)
        elif args.restore:
            game_save.restore(n)
        elif args.delete:
            game_save.delete(require_confirmation=not auto_confirm)
        else:
            game_save.backup(n, args.message)
    return 0


if __name__ == '__main__':
    main(sys.argv[1:])
