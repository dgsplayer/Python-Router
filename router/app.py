from multiprocessing import Process
from pprint import pformat

import asyncio
import threading
import logging
import os
import psycopg2
from flask import Flask, request, jsonify
from router.exceptions import AppException
from webargs.flaskparser import FlaskParser
from router.service import handle

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Setup flask error handler (handled inside the views and nested methods)
    app.errorhandler(AppException)(lambda err: err.to_response())
    parser = create_parser()
    setup_views(app, parser)
    return app


def create_parser():
    parser = FlaskParser()

    # Setup validation error handler (handled by view methods decorator)
    @parser.error_handler
    def handle_validation_error(error, req, schema):
        raise AppException.validation_error(error)

    return parser


def setup_views(app, parser):
    @app.route('/router', methods=('post',))
    def router():
        json = request.json
        print(json)
        route_process = threading.Thread(target=handle, args=(json,))
        route_process.start()
        return jsonify(status="OK")

    @app.route('/router/<id>', methods=('get',))
    def get_route(id):
        hostname = 'localhost'
        port = '5432'
        db = 'postgres'
        user = 'postgres'
        pwd = 'postgres'

        connection = psycopg2.connect(host=hostname, port=port, database=db, user=user, password=pwd, connect_timeout=1)

        cursor = connection.cursor()
        query = 'select result from ortools where id = %s'

        cursor.execute(query, (id,))

        results = cursor.fetchall()
        if results:
            result = results[0]
            return jsonify(result,)

        if not results:
            return '', 204

    @app.route('/health')
    def health_check():
        return jsonify(status="OK")
