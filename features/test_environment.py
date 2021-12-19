import dataclasses
from ctypes import Union
from typing import Type, Iterable, Collection
from unittest import TestCase
from environment import get_argument_list, Runnable, RunResult, before_all, get_next_run_result


class MockObject:
    pass


class Test(TestCase):
    def test_get_argument_list(self):

        # noinspection PyPep8Naming
        @dataclasses.dataclass
        class _data:
            expected: (tuple, Type[BaseException])
            given: str

        subtests = {'double quote': _data(expected=('user', '--name', 'Josh Z'),
                                          given='user --name "Josh Z"'),
                    'single quote': _data(expected=('user', '--name', 'Josh Z'),
                                          given="user --name 'Josh Z'"),
                    'double quote mid-arg': _data(expected=('user', '--name', 'Josh"Z'),
                                                  given='user --name Josh"Z'),
                    'single quote mid-arg': _data(expected=('user', '--name', "Josh'Z"),
                                                  given="user --name Josh'Z"),
                    'preserved whitespace in quotes': _data(expected=('user', '--name', ' Josh Z '),
                                                            given="user --name ' Josh Z '"),
                    'trimmed whitespace outside quotes': _data(expected=('user', '--name', 'Josh Z'),
                                                               given="  user    --name  'Josh Z'   "),
                    'Error - unbalanced (double) quotes': _data(expected=ValueError,
                                                                given='user --name "Josh Z'),
                    'Error - unbalanced (single) quotes': _data(expected=ValueError,
                                                                given="user --name 'Josh Z"),
                    'Escaped single quote': _data(expected=('user', '--name', "Josh'Z"),
                                                  given=r"user --name 'Josh\'Z'"),
                    'Escaped double quote': _data(expected=('user', '--name', 'Josh"Z'),
                                                  given=r'user --name "Josh\"Z"')
                    }

        for msg, data in subtests.items():
            with self.subTest(msg):
                if isinstance(data.expected, type) and issubclass(data.expected, BaseException):
                    with self.assertRaises(data.expected):
                        get_argument_list(data.given)
                else:
                    actual = get_argument_list(data.given)
                    self.assertEqual(data.expected, actual)

    def test_get_next_run_result(self):

        # set up the mock context object
        mock_context = MockObject
        before_all(mock_context)

        def f(x):
            return x + 1

        # noinspection PyPep8Naming
        @dataclasses.dataclass
        class _data:
            expected: (Collection[RunResult], Type[Exception])
            given: Collection[Runnable]

        expected = [RunResult(return_value=2),
                    RunResult(return_value=3),
                    TypeError]

        given = [Runnable(f, 1),
                 Runnable(f, 2),
                 Runnable(f, 'a')]
        for r, e in zip(given, expected):
            with self.subTest(f'add_result - {r!r}'):
                # noinspection PyUnresolvedReferences
                actual = mock_context.add_result(r)
                if isinstance(e, type):
                    self.assertIsInstance(actual.exception, e)
                else:
                    self.assertEqual(e, actual)

        with self.subTest('test length of context results'):
            # noinspection PyUnresolvedReferences
            self.assertEqual(len(expected), len(mock_context.results))

        for r, e in zip(given, expected):
            with self.subTest(f'get_next_run_result - {r}'):
                actual = get_next_run_result(mock_context)
                if isinstance(e, type):
                    self.assertIsInstance(actual.exception, e)
                else:
                    self.assertEqual(e, actual)
