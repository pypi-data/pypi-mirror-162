class ConfigBase:
    pass


class Production(ConfigBase):
    FLASK_CONFIG = "production"
    pass


class Development(ConfigBase):
    FLASK_CONFIG = "development"
    DEBUG = True


class Testing(ConfigBase):
    FLASK_CONFIG = "testing"
    TESTING = True
    WTF_CSRF_ENABLED = False


config = {
    "production": Production,
    "development": Development,
    "testing": Testing,
}
