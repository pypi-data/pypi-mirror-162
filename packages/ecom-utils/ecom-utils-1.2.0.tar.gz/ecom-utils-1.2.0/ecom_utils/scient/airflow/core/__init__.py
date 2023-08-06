import importlib

from dw_chaco_etl.settings.manage import SETTINGS_MODULE


settings = importlib.import_module(SETTINGS_MODULE)

setattr(settings, "SETTINGS_MODULE", SETTINGS_MODULE)