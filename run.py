import logging

from router import config
from router.app import create_app


logging.getLogger().setLevel(logging.INFO)
create_app(config.ProductionConfig).run(host='0.0.0.0', port=8080)
