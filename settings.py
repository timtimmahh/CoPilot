from os import system, environ
from time import strftime
from configparser import ConfigParser, NoSectionError, DuplicateSectionError, DuplicateOptionError, NoOptionError

try:
    import RPi.GPIO as GPIO

    # import serial
    test_environment = False
except (ImportError, RuntimeError):
    test_environment = True


class Brightness:
    pass


class AutoBrightness(Brightness):
    pass


class NightLight(AutoBrightness):
    def __init__(self):
        self.start_time, self.end_time, self.night_light_brightness, self.default_brightness = configs_for({
            'Brightness':
                [
                    {
                        'dtype': 'int',
                        'option': 'night_light_start_time',
                        'fallback': 21
                    },
                    {
                        'dtype': 'int',
                        'option': 'night_light_end_time',
                        'fallback': 7
                    },
                    {
                        'dtype': 'int',
                        'option': 'night_light_brightness_level',
                        'fallback': 15
                    },
                    {
                        'dtype': 'int',
                        'option': 'default_brightness_level',
                        'fallback': 175
                    }
                ]
        }).get('Brightness').values()

    def print(self):
        print('Start time: %d End time: %d NL Brightness: %d Default Brightness: %d'
              % (self.start_time, self.end_time, self.night_light_brightness, self.default_brightness))

    def start_night_light(self):
        if self.end_time > int(strftime("%-H")) > self.start_time:
            print("dim")
            system("sudo echo %d > /sys/class/backlight/rpi_backlight/brightness" % self.night_light_brightness)

    def end_night_light(self):
        if self.start_time > int(strftime("%-H")) > self.end_time:
            print("bright")
            system("sudo echo %d > /sys/class/backlight/rpi_backlight/brightness" % self.default_brightness)


def open_config(method, exceptions=(NoSectionError, DuplicateSectionError, DuplicateOptionError,
                                    NoOptionError)):
    def cfg(data: dict, mode: str = 'r'):
        try:
            with open("./config.ini", mode) as f:
                config = ConfigParser(allow_no_value=True)
                if mode == 'r':
                    config.read_file(f)
                return method(config, f, data)
        except exceptions:
            print(exceptions)

    return cfg


def write_config(config, f, data: dict):
    for section, options in data.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, value in options.items():
            config.set(section, key, value)
    config.write(f)


new_config_for = open_config(write_config)


def get_configs(config, f, data: dict):
    def switch(section, option: dict):
        return {
            'int': config.getint,
            'bool': config.getboolean,
            'float': config.getfloat
        }.get(option.get('dtype', None), config.get) \
            (section, option['option'], raw=option.get('raw', False),
             vars=option.get('vars', None), fallback=option['fallback'])

    return {section: {option['option']: switch(section, option) for option in options}
            for section, options in data.items() if config.has_section(section)}


configs_for = open_config(get_configs)


def get_configs(config, f, dtype: str, section, option, raw: bool = False, vars=None, fallback=''):
    return get_configs(config, f,
                       {section: [{'dtype': dtype, 'option': option, 'raw': raw, 'vars': vars, 'fallback': fallback}]})


def get_all_config_options():
    return configs_for({
        'Info':
            [
                {
                    'dtype': 'str',
                    'option': 'version',
                    'fallback': 'V2.3.0'
                },
                {
                    'dtype': 'str',
                    'option': 'name',
                    'fallback': 'AutoPi'
                }
            ],
        'Display':
            [
                {
                    'dtype': 'int',
                    'option': 'width',
                    'fallback': '800'
                },
                {
                    'dtype': 'int',
                    'option': 'height',
                    'fallback': '480'
                },
                {
                    'dtype': 'str',
                    'option': 'fullscreen',
                    'fallback': 'auto'
                },
                {
                    'dtype': 'str',
                    'option': 'window_state',
                    'fallback': 'maximized'
                }
            ],
        'Brightness':
            [
                {
                    'dtype': 'int',
                    'option': 'auto_brightness_enabled',
                    'fallback': '1'
                },
                {
                    'dtype': 'int',
                    'option': 'default_brightness_level',
                    'fallback': '175'
                },
                {
                    'dtype': 'int',
                    'option': 'night_light_enabled',
                    'fallback': '1'
                },
                {
                    'dtype': 'int',
                    'option': 'night_light_start_time',
                    'fallback': '21'
                },
                {
                    'dtype': 'int',
                    'option': 'night_light_end_time',
                    'fallback': '7'
                },
                {
                    'dtype': 'int',
                    'option': 'night_light_brightness_level',
                    'fallback': '15'
                }
            ]
    })


if __name__ == '__main__':
    environ["KIVY_IMAGE"] = "pil"  # Sets how images should be loaded: 'pil' for linux
