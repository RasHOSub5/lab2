from enum import Enum

class Level(Enum):
    DEBUG = (1, '\033[94m')    # Azul
    INFO = (2, '\033[92m')     # Verde
    WARNING = (3, '\033[93m')  # Amarillo
    ERROR = (4, '\033[91m')    # Rojo
    CRITICAL = (5, '\033[95m') # Magenta

    def __init__(self, level, color):
        self.level = level
        self.color = color

class Logger:

    _global_level = Level.DEBUG
    _enabled_categories = set()
    _disabled_categories = set()
    _enabled = True

    def __init__(self, category=None):
        self.reset = '\033[0m'
        self.level = Level
        self.category = category

    def _log(self, message, level):

        if not Logger._enabled:
            return
        
        if level.level < Logger._global_level.level:
            return
        
        if Logger._enabled_categories and self.category not in Logger._enabled_categories:
            return

        if self.category in Logger._disabled_categories:
            return
        
        if self.category:
            print(f"{level.color}[{self.category}] {message}{self.reset}")
        else:
            print(f"{level.color}{message}{self.reset}")

    def debug(self, message):
        self._log(message, self.level.DEBUG)

    def info(self, message):
        self._log(message, self.level.INFO)

    def warning(self, message):
        self._log(message, self.level.WARNING)

    def error(self, message):
        self._log(message, self.level.ERROR)

    def critical(self, message):
        self._log(message, self.level.CRITICAL)

    @classmethod
    def set_global_level(cls, level):
        cls._global_level = level

    @classmethod
    def enable_category(cls, category):
        cls._enabled_categories.add(category)

    @classmethod
    def enable_categories(cls, categories):
        cls._enabled_categories.update(categories)

    @classmethod
    def disable_category(cls, category):
        cls._disabled_categories.add(category)

    @classmethod
    def disable_categories(cls, categories):
        cls._disabled_categories.update(categories)

    @classmethod
    def enable_all_categories(cls):
        cls._enabled_categories.clear()

    @classmethod
    def disable_all_categories(cls):
        cls._disabled_categories.clear()

    @classmethod
    def enable_all(cls):
        cls._enabled = True
        cls._enabled_categories.clear()
        cls._disabled_categories.clear()

    @classmethod
    def disable_all(cls):
        cls._enabled = False

    @classmethod
    def get_status(cls):
        return {
            "enabled": cls._enabled,
            "global_level": cls._global_level.name,
            "enabled_categories": list(cls._enabled_categories),
            "disabled_categories": list(cls._disabled_categories)
        }