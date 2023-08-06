from dynaconf import Dynaconf

PUBLIC_CONFIG_FILE = 'settings.yaml'

dynaconf_settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[PUBLIC_CONFIG_FILE, '.secrets.yaml'],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
