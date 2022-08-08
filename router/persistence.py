from __future__ import print_function

import json
import os
import psycopg2

def persist(result, identifier, request):

    try:
        # hostname = os.environ['DB_HOSTNAME']
        # port = os.environ['DB_PORT']
        # db = os.environ['DB_DB']
        # user = os.environ['DB_USER']
        # pwd = os.environ['DB_PWD']

        hostname = 'localhost'
        port = '5432'
        db = 'postgres'
        user = 'postgres'
        pwd = 'postgres'

        connect = psycopg2.connect(host=hostname, port=port, database=db,user=user, password=pwd, connect_timeout=1)

        itemTable = {
            'id': identifier,
            'request': request,
            'result': result
        }

        jsonString = json.dumps(itemTable)

        insert_query = "insert into ortools (id, result) values (%s, %s)"

        cursor = connect.cursor()
        cursor.execute(insert_query, (identifier, jsonString))
        cursor.close()

        connect.commit()

    finally:
        if connect:
            connect.close()
