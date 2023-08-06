import subprocess
import typing
from typing import List


class Zenity:
    @staticmethod
    def _command_factory(window_type: str, loc: dict, excluded: set = None) -> List[str]:
        """
        Builds a zenity command (list of strings) to be passed to subprocess.
        :param window_type: type of zenity window ('question', 'warning', 'info', etc.)
        :param loc: a dictionary of parameters (set of k: v). They are parsed in a way that depends on their type
        and value. If type(v) is bool, '--{k}' is added if v is True, nothing is added otherwise. If type(v) is str or
        int, '--{k}={v}' is added if v is not None ; nothing added otherwise (v="" and v=None are treated differently).
        If type(v) is something else, the pair k: v is ignored.
        :param excluded: set of keys that must be ignored even though their type is in (bool, int, str).
        :return: list of strings to be passed to subprocess command (Popen(), call(), run(), ...)
        """
        command = ['zenity', '--' + window_type]
        excluded = excluded or {}
        try:
            loc.update(loc.pop('kwargs'))
        except KeyError:
            pass
        for k, v in loc.items():
            if k in excluded:
                continue
            k = k.replace('_', '-')
            if k in excluded:
                continue
            if v is None:
                continue
            if type(v) is bool and v:
                command.append('--' + k)
            elif type(v) in {str, int} and v is not None:
                command.append('--' + k + '=' + str(v))
            else:
                pass
        return command

    @staticmethod
    def question(title: str = None, text: str = None, width: int = None, height: int = None,
                 ellipsize: bool = True, timeout: int = 60, default_cancel: bool = False, **kwargs) -> bool:
        """
        Calls a subprocess.run(command) where 'command' is built from keyword arguments. The command starts by
        'zenity --question'. The most common options are already in the signature but some others can be added.
        Type 'zenity --help-question' in a terminal for a complete list of parameters.

        :return: True is user accepts
        """
        command = Zenity._command_factory('question', locals())
        process = subprocess.run(command)
        return not process.returncode

    @staticmethod
    def warning(title: str = None, text: str = None, width: int = None, height: int = None,
                ellipsize: bool = True, timeout: int = 60, **kwargs) -> subprocess.CompletedProcess:
        """
        Calls a subprocess.run(command) where 'command' is built from keyword arguments. The command starts by
        'zenity --warning'. The most common options are already in the signature but some others can be added.
        Type 'zenity --help-warning' in a terminal for a complete list of parameters.
        """
        command = Zenity._command_factory('warning', locals())
        return subprocess.run(command)

    @staticmethod
    def error(title: str = None, text: str = None, width: int = None, height: int = None,
              ellipsize: bool = True, timeout: int = 60, **kwargs) -> subprocess.CompletedProcess:
        """
        Calls a subprocess.run(command) where 'command' is built from keyword arguments. The command starts by
        'zenity --error'. The most common options are already in the signature but some others can be added.
        Type 'zenity --help-error' in a terminal for a complete list of parameters.
        """
        command = Zenity._command_factory('error', locals())
        return subprocess.run(command)

    @staticmethod
    def info(title: str = None, text: str = None, width: int = None, height: int = None,
             ellipsize: bool = True, timeout: int = 60, **kwargs) -> subprocess.CompletedProcess:
        """
        Calls a subprocess.run(command) where 'command' is built from keyword arguments. The command starts by
        'zenity --info'. The most common options are already in the signature but some others can be added.
        Type 'zenity --help-info' in a terminal for a complete list of parameters.
        """
        command = Zenity._command_factory('info', locals())
        return subprocess.run(command)

    @staticmethod
    def choice(choices, title: str = None, text: str = None, switch: bool = True, ellipsize: bool = True,
               width: int = None, height: int = None, timeout: int = 60, **kwargs) -> typing.Any:
        """
        Calls a subprocess.run(command) where 'command' is built from keyword arguments. The command starts by
        'zenity --question'. The most common options are already in the signature but some others can be added.
        Type 'zenity --help-question' in a terminal for a complete list of parameters.
        """
        command = Zenity._command_factory('question', locals())
        for c in choices:
            command.append(f"--extra-button={c}")
        try:
            output = subprocess.check_output(command)
        except subprocess.CalledProcessError as e:
            output = e.output
        return output.decode().strip('\n')

    @staticmethod
    def list(title: str = None, text: str = None, width: int = None, height: int = None,
             columns=None, table=None, timeout: int = 60, check_output: bool = False, **kwargs) -> typing.Any:
        """
        Calls a subprocess.run(command) where 'command' is built from keyword arguments. The command starts by
        'zenity --list'. The most common options are already in the signature but some others can be added.
        Type 'zenity --help-list' in a terminal for a complete list of parameters.
        """
        command = Zenity._command_factory('list', locals(), {'check_output'})
        table = table or []
        for col in columns:
            command.append(f"--column={col}")
        for row in table:
            for val in row:
                command.append(str(val))
        if check_output:
            try:
                output = subprocess.check_output(command)
            except subprocess.CalledProcessError as e:
                output = e.output
            return output.decode().strip('\n')
        else:
            return subprocess.run(command, timeout=timeout)
