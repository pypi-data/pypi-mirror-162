from typing import IO, Any, Dict, Iterable, List, Optional, Set, Tuple, Union
from configparser import _UNSET, ConfigParser, NoOptionError, NoSectionError  # type: ignore
import re
import os
import datetime
import json
import logging
import warnings
from collections import OrderedDict
from typing_extensions import overload
import shlex
import subprocess
import sys
from json.decoder import JSONDecodeError

from example_demo.utils.exceptions import OnedatautilConfigException
from example_demo.utils.moudle_loading import import_string

log = logging.getLogger(__name__)

_SQLITE3_VERSION_PATTERN = re.compile(r"(?P<version>^\d+(?:\.\d+)*)\D?.*$")

ConfigType = Union[str, int, float, bool]
ConfigOptionsDictType = Dict[str, ConfigType]
ConfigSectionSourcesType = Dict[str, Union[str, Tuple[str, str]]]
ConfigSourcesType = Dict[str, ConfigSectionSourcesType]

CONFIG_FILE = 'project.cfg'


@overload
def expand_env_var(env_var: None) -> None:
    ...


@overload
def expand_env_var(env_var: str) -> str:
    ...


def expand_env_var(env_var: Union[str, None]) -> Optional[Union[str, None]]:
    """
    Expands (potentially nested) env vars by repeatedly applying
    `expandvars` and `expanduser` until interpolation stops having
    any effect.
    """
    if not env_var:
        return env_var
    while True:
        interpolated = os.path.expanduser(os.path.expandvars(str(env_var)))
        if interpolated == env_var:
            return interpolated
        else:
            env_var = interpolated


def run_command(command: str) -> str:
    """Runs command and returns stdout"""
    process = subprocess.Popen(
        shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True
    )
    output, stderr = (stream.decode(sys.getdefaultencoding(), 'ignore') for stream in process.communicate())

    if process.returncode != 0:
        raise OnedatautilConfigException(
            f"Cannot execute {command}. Error code is: {process.returncode}. "
            f"Output: {output}, Stderr: {stderr}"
        )

    return output


class OnedatautilConfigParser(ConfigParser):
    # These configuration elements can be fetched as the stdout of commands
    # following the "{section}__{name}_cmd" pattern, the idea behind this
    # is to not store password on boxes in text files.
    # These configs can also be fetched from Secrets backend
    # following the "{section}__{name}__secret" pattern
    sensitive_config_values: Set[Tuple[str, str]] = {
        ('project', 'name'),
        ('source_get', 'request_type'),
    }

    # A mapping of (new section, new option) -> (old section, old option, since_version).
    # When reading new option, the old option will be checked to see if it exists. If it does a
    # DeprecationWarning will be issued and the old option will be used instead

    # A mapping of old default values that we want to change and warn the user
    # about. Mapping of section -> setting -> { old, replace, by_version }

    _available_logging_levels = ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG']
    enums_options = {
        ("logging", "logging_level"): _available_logging_levels,
        ("logging", "fab_logging_level"): _available_logging_levels,
        ("logging", "celery_logging_level"): _available_logging_levels + [''],
    }

    upgraded_values: Dict[Tuple[str, str], str]
    """Mapping of (section,option) to the old value that was upgraded"""

    # This method transforms option names on every read, get, or set operation.
    # This changes from the default behaviour of ConfigParser from lower-casing
    # to instead be case-preserving
    def optionxform(self, optionstr: str) -> str:
        return optionstr

    def __init__(self, default_config: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.upgraded_values = {}

        self.onedatautil_defaults = ConfigParser(*args, **kwargs)
        if default_config is not None:
            self.onedatautil_defaults.read_string(default_config)
            # Set the upgrade value based on the current loaded default

        # else:
        #     with suppress(KeyError):
        #         del self.deprecated_values['logging']['log_filename_template']

        self.is_validated = False

    def _validate_enums(self):
        """Validate that enum type config has an accepted value"""
        for (section_key, option_key), enum_options in self.enums_options.items():
            if self.has_option(section_key, option_key):
                value = self.get(section_key, option_key)
                if value not in enum_options:
                    raise OnedatautilConfigException(
                        f"`[{section_key}] {option_key}` should not be "
                        f"{value!r}. Possible values: {', '.join(enum_options)}."
                    )

    # must arg value
    def get_mandatory_value(self, section: str, key: str, **kwargs) -> str:
        value = self.get(section, key, **kwargs)
        if value is None:
            raise ValueError(f"The value {section}/{key} should be set!")
        return value

    def get(self, section: str, key: str, **kwargs) -> Optional[str]:  # type: ignore[override]
        section = str(section).lower()
        key = str(key).lower()

        option = self._get_option_from_config_file(key, kwargs, section)
        if option:
            return option

        return self._get_option_from_default_config(section, key, **kwargs)

    def _get_option_from_default_config(self, section: str, key: str, **kwargs) -> Optional[str]:
        # ...then the default config
        if self.onedatautil_defaults.has_option(section, key) or 'fallback' in kwargs:
            return expand_env_var(self.onedatautil_defaults.get(section, key, **kwargs))

        else:
            log.warning("section/key [%s/%s] not found in config", section, key)

            raise OnedatautilConfigException(f"section/key [{section}/{key}] not found in config")

    def _get_option_from_config_file(
            self,
            key: str,
            kwargs: Dict[str, Any],
            section: str,
    ) -> Optional[str]:
        # ...then the config file
        if super().has_option(section, key):
            # Use the parent's methods to get the actual config here to be able to
            # separate the config from default config.
            return expand_env_var(super().get(section, key, **kwargs))

        return None

    def getboolean(self, section: str, key: str, default_val=False, **kwargs) -> bool:  # type: ignore[override]
        val = str(self.get(section, key, **kwargs)).lower().strip()
        if '#' in val:
            val = val.split('#')[0].strip()
        if val in ('t', 'true', '1'):
            return True
        elif val in ('f', 'false', '0'):
            return False
        else:
            return default_val
            # raise OnedatautilConfigException(
            #     f'Failed to convert value to bool. Please check "{key}" key in "{section}" section. '
            #     f'Current value: "{val}".'
            # )

    def getint(self, section: str, key: str, default_int=0, **kwargs) -> int:  # type: ignore[override]
        val = self.get(section, key, **kwargs)
        if not val:
            return default_int
            # raise OnedatautilConfigException(
            #     f'Failed to convert value None to int and no default arg'
            #     f'Please check "{key}" key in "{section}" section is set.'
            # )
        try:
            return int(val)
        except ValueError:
            raise OnedatautilConfigException(
                f'Failed to convert value to int. Please check "{key}" key in "{section}" section. '
                f'Current value: "{val}".'
            )

    def getfloat(self, section: str, key: str, **kwargs) -> float:  # type: ignore[override]
        val = self.get(section, key, **kwargs)
        if val is None:
            raise OnedatautilConfigException(
                f'Failed to convert value None to float. '
                f'Please check "{key}" key in "{section}" section is set.'
            )
        try:
            return float(val)
        except ValueError:
            raise OnedatautilConfigException(
                f'Failed to convert value to float. Please check "{key}" key in "{section}" section. '
                f'Current value: "{val}".'
            )

    def getimport(self, section: str, key: str, **kwargs) -> Any:
        """
        Reads options, imports the full qualified name, and returns the object.

        In case of failure, it throws an exception with the key and section names

        :return: The object or None, if the option is empty
        """
        full_qualified_path = conf.get(section=section, key=key, **kwargs)
        if not full_qualified_path:
            return None

        try:
            return import_string(full_qualified_path)
        except ImportError as e:
            log.error(e)
            raise OnedatautilConfigException(
                f'The object could not be loaded. Please check "{key}" key in "{section}" section. '
                f'Current value: "{full_qualified_path}".'
            )

    def getjson(
            self, section: str, key: str, fallback=_UNSET, **kwargs
    ) -> Union[dict, list, str, int, float, None]:
        """
        Return a config value parsed from a JSON string.

        ``fallback`` is *not* JSON parsed but used verbatim when no config value is given.
        """
        # get always returns the fallback value as a string, so for this if
        # someone gives us an object we want to keep that
        default = _UNSET
        if fallback is not _UNSET:
            default = fallback
            fallback = _UNSET

        try:
            data = self.get(section=section, key=key, fallback=fallback, **kwargs)
        except (NoSectionError, NoOptionError):
            return default

        if not data:
            return default if default is not _UNSET else None

        try:
            return json.loads(data)
        except JSONDecodeError as e:
            raise OnedatautilConfigException(f'Unable to parse [{section}] {key!r} as valid json') from e

    def gettimedelta(
            self, section: str, key: str, fallback: Any = None, **kwargs
    ) -> Optional[datetime.timedelta]:
        """
        Gets the config value for the given section and key, and converts it into datetime.timedelta object.
        If the key is missing, then it is considered as `None`.

        :param section: the section from the config
        :param key: the key defined in the given section
        :param fallback: fallback value when no config value is given, defaults to None
        :raises OnedatautilConfigException: raised because ValueError or OverflowError
        :return: datetime.timedelta(seconds=<config_value>) or None
        """
        val = self.get(section, key, fallback=fallback, **kwargs)

        if val:
            # the given value must be convertible to integer
            try:
                int_val = int(val)
            except ValueError:
                raise OnedatautilConfigException(
                    f'Failed to convert value to int. Please check "{key}" key in "{section}" section. '
                    f'Current value: "{val}".'
                )

            try:
                return datetime.timedelta(seconds=int_val)
            except OverflowError as err:
                raise OnedatautilConfigException(
                    f'Failed to convert value to timedelta in `seconds`. '
                    f'{err}. '
                    f'Please check "{key}" key in "{section}" section. Current value: "{val}".'
                )

        return fallback

    def read(
            self,
            filenames: Union[
                str,
                bytes,
                os.PathLike,
                Iterable[Union[str, bytes, os.PathLike]],
            ],
            encoding=None,
    ):
        super().read(filenames=filenames, encoding=encoding)

    # The RawConfigParser defines "Mapping" from abc.collections is not subscriptable - so we have
    # to use Dict here.
    def read_dict(  # type: ignore[override]
            self, dictionary: Dict[str, Dict[str, Any]], source: str = '<dict>'
    ):
        super().read_dict(dictionary=dictionary, source=source)

    def has_option(self, section: str, option: str) -> bool:
        try:
            # Using self.get() to avoid reimplementing the priority order
            # of config variables (env, config, cmd, defaults)
            # UNSET to avoid logging a warning about missing values
            self.get(section, option, fallback=_UNSET)
            return True
        except (NoOptionError, NoSectionError):
            return False

    def remove_option(self, section: str, option: str, remove_default: bool = True):
        """
        Remove an option if it exists in config from a file or
        default config. If both of config have the same option, this removes
        the option in both configs unless remove_default=False.
        """
        if super().has_option(section, option):
            super().remove_option(section, option)

        if self.onedatautil_defaults.has_option(section, option) and remove_default:
            self.onedatautil_defaults.remove_option(section, option)

    def getsection(self, section: str) -> Optional[ConfigOptionsDictType]:
        """
        Returns the section as a dict. Values are converted to int, float, bool
        as required.

        :param section: section from the config
        :rtype: dict
        """
        if not self.has_section(section) and not self.onedatautil_defaults.has_section(section):
            return None
        if self.onedatautil_defaults.has_section(section):
            _section: ConfigOptionsDictType = OrderedDict(self.onedatautil_defaults.items(section))
        else:
            _section = OrderedDict()

        if self.has_section(section):
            _section.update(OrderedDict(self.items(section)))
        #
        # section_prefix = self._env_var_name(section, '')
        # for env_var in sorted(os.environ.keys()):
        #     if env_var.startswith(section_prefix):
        #         key = env_var.replace(section_prefix, '')
        #         if key.endswith("_CMD"):
        #             key = key[:-4]
        #         key = key.lower()
        #         _section[key] = self._get_env_var_option(section, key)

        for key, val in _section.items():
            if val is None:
                raise OnedatautilConfigException(
                    f'Failed to convert value automatically. '
                    f'Please check "{key}" key in "{section}" section is set.'
                )
            try:
                _section[key] = int(val)
            except ValueError:
                try:
                    _section[key] = float(val)
                except ValueError:
                    if isinstance(val, str) and val.lower() in ('t', 'true'):
                        _section[key] = True
                    elif isinstance(val, str) and val.lower() in ('f', 'false'):
                        _section[key] = False
        return _section

    def write(self, fp: IO, space_around_delimiters: bool = True):  # type: ignore[override]
        # This is based on the configparser.RawConfigParser.write method code to add support for
        # reading options from environment variables.
        # Various type ignores below deal with less-than-perfect RawConfigParser superclass typing
        if space_around_delimiters:
            delimiter = f" {self._delimiters[0]} "  # type: ignore[attr-defined]
        else:
            delimiter = self._delimiters[0]  # type: ignore[attr-defined]
        if self._defaults:  # type: ignore
            self._write_section(  # type: ignore[attr-defined]
                fp, self.default_section, self._defaults.items(), delimiter  # type: ignore[attr-defined]
            )
        for section in self._sections:  # type: ignore[attr-defined]
            item_section: ConfigOptionsDictType = self.getsection(section)  # type: ignore[assignment]
            self._write_section(fp, section, item_section.items(), delimiter)  # type: ignore[attr-defined]

    def as_dict(
            self,
            display_source: bool = False,
            display_sensitive: bool = False,
            raw: bool = False,
    ) -> ConfigSourcesType:
        """
        Returns the current configuration as an OrderedDict of OrderedDicts.

        W
        :param display_source: If False, the option value is returned. If True,
            a tuple of (option_value, source) is returned. Source is either
            'project.cfg', 'default', 'env var', or 'cmd'.
        :param display_sensitive: If True, the values of options set by env
            vars and bash commands will be displayed. If False, those options
            are shown as '< hidden >'
        :param raw: Should the values be output as interpolated values, or the
            "raw" form that can be fed back in to ConfigParser

        :param include_cmds: Should the result of calling any *_cmd config be
            set (True, default), or should the _cmd options be left as the
            command to run (False)

        :return: Dictionary, where the key is the name of the section and the content is
            the dictionary with the name of the parameter and its value.
        """
        config_sources: ConfigSourcesType = {}
        configs = [
            ('default', self.onedatautil_defaults),
            ('project.cfg', self),
        ]

        self._replace_config_with_display_sources(
            config_sources,
            configs,
            display_source,
            raw,
        )

        return config_sources

    def _filter_by_source(
            self,
            config_sources: ConfigSourcesType,
            display_source: bool,
            getter_func,
    ):
        """
        Deletes default configs from current configuration (an OrderedDict of
        OrderedDicts) if it would conflict with special sensitive_config_values.


        :param config_sources: The current configuration to operate on
        :param display_source: If False, configuration options contain raw
            values. If True, options are a tuple of (option_value, source).
            Source is either 'project.cfg', 'default', 'env var', or 'cmd'.
        :param getter_func: A callback function that gets the user configured
            override value for a particular sensitive_config_values config.
        :rtype: None
        :return: None, the given config_sources is filtered if necessary,
            otherwise untouched.
        """
        for (section, key) in self.sensitive_config_values:
            # Don't bother if we don't have section / key
            if section not in config_sources or key not in config_sources[section]:
                continue
            # Check that there is something to override defaults
            try:
                getter_opt = getter_func(section, key)
            except ValueError:
                continue
            if not getter_opt:
                continue
            # Check to see that there is a default value
            if not self.onedatautil_defaults.has_option(section, key):
                continue
            # Check to see if bare setting is the same as defaults
            if display_source:
                # when display_source = true, we know that the config_sources contains tuple
                opt, source = config_sources[section][key]  # type: ignore
            else:
                opt = config_sources[section][key]
            if opt == self.onedatautil_defaults.get(section, key):
                del config_sources[section][key]

    @staticmethod
    def _replace_config_with_display_sources(
            config_sources: ConfigSourcesType,
            configs: Iterable[Tuple[str, ConfigParser]],
            display_source: bool,
            raw: bool,
    ):
        for (source_name, config) in configs:
            for section in config.sections():
                OnedatautilConfigParser._replace_section_config_with_display_sources(
                    config,
                    config_sources,
                    display_source,
                    raw,
                    section,
                    source_name,
                )

    @staticmethod
    def _deprecated_value_is_set_in_config(
            deprecated_section: str,
            deprecated_key: str,
            configs: Iterable[Tuple[str, ConfigParser]],
    ) -> bool:
        for config_type, config in configs:
            if config_type == 'default':
                continue
            try:
                deprecated_section_array = config.items(section=deprecated_section, raw=True)
                for (key_candidate, _) in deprecated_section_array:
                    if key_candidate == deprecated_key:
                        return True
            except NoSectionError:
                pass
        return False

    @staticmethod
    def _replace_section_config_with_display_sources(
            config: ConfigParser,
            config_sources: ConfigSourcesType,
            display_source: bool,
            raw: bool,
            section: str,
            source_name: str,
    ):
        sect = config_sources.setdefault(section, OrderedDict())
        for (k, val) in config.items(section=section, raw=raw):
            if display_source:
                sect[k] = (val, source_name)
            else:
                sect[k] = val

    @staticmethod
    def _warn_deprecate(section: str, key: str, deprecated_section: str, deprecated_name: str):
        if section == deprecated_section:
            warnings.warn(
                f'The {deprecated_name} option in [{section}] has been renamed to {key} - '
                f'the old setting has been used, but please update your config.',
                DeprecationWarning,
                stacklevel=3,
            )
        else:
            warnings.warn(
                f'The {deprecated_name} option in [{deprecated_section}] has been moved to the {key} option '
                f'in [{section}] - the old setting has been used, but please update your config.',
                DeprecationWarning,
                stacklevel=3,
            )

    def __getstate__(self):
        return {
            name: getattr(self, name)
            for name in [
                '_sections',
                'is_validated',
                'onedatautil_defaults',
            ]
        }

    def __setstate__(self, state):
        self.__init__()
        config = state.pop('_sections')
        self.read_dict(config)
        self.__dict__.update(state)


def _default_config_file_path(file_name: str) -> str:
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    return os.path.join(templates_dir, file_name)


def _parameterized_config_from_template(filename) -> str:
    path = _default_config_file_path(filename)
    try:
        with open(path, encoding='utf-8') as fh:

            return fh.read().strip()
    except Exception as e:
        # 默认 encoding=gbk
        with open(path) as fh:
            return fh.read().strip()

def get_cfg_file():
    program_cfg_path = os.path.join(os.getcwd(), CONFIG_FILE)
    if not os.path.exists(program_cfg_path):
        sys_path_first = sys.path[0] if sys.path[0] != os.getcwd() else sys.path[1]
        program_cfg_path = os.path.join(sys_path_first, CONFIG_FILE)

    return program_cfg_path
def initialize_config(work_path=''):
    """
    Load the  project.cfg file.

    """
    default_config = _parameterized_config_from_template('default_project.cfg')

    local_conf = OnedatautilConfigParser(default_config=default_config)
    if not work_path:
        program_cfg_path = os.path.join(os.getcwd(), CONFIG_FILE)
        if not os.path.exists(program_cfg_path):
            sys_path_first = sys.path[0] if sys.path[0] != os.getcwd() else sys.path[1]
            program_cfg_path = os.path.join(sys_path_first, CONFIG_FILE)
    else:
        program_cfg_path = os.path.join(work_path, CONFIG_FILE)

    if os.path.isfile(program_cfg_path):
        try:
            local_conf.read(program_cfg_path)
        except Exception as e:
            local_conf.read(program_cfg_path, encoding='utf-8')
    return local_conf


conf = initialize_config()
