class BaseConfig:
    pass


class DevelopmentConfig(BaseConfig):
    ENV = 'dev'
    DEBUG = True


class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = True


class ProductionConfig(BaseConfig):
    ENV = 'prod'
    DEBUG = False
