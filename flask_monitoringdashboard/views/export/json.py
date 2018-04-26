import datetime

import jwt
from flask import json, jsonify

from flask_monitoringdashboard import blueprint, config
from flask_monitoringdashboard.database.function_calls import get_data_between
from flask_monitoringdashboard.database.monitor_rules import get_monitor_data
from flask_monitoringdashboard.core.utils import get_details


@blueprint.route('/get_json_data', defaults={'time_from': 0})
@blueprint.route('/get_json_data/<time_from>')
@blueprint.route('/get_json_data/<time_from>/<time_to>')
def get_json_data_from(time_from, time_to=None):
    """
    The returned data is the data that is encrypted using a security token. This security token is set in the
    configuration.
    :param time_from: (optional) if specified, only the data-values after this date are returned.
                      input must be an timestamp value (utc) (= integer)
                      :param time_to: (optional) if specified, only the data-values before this date are returned.
                      input must be an timestamp value (utc) (= integer)
    :return: all entries from the database. (endpoint-table)
    """
    data = []
    try:
        time1 = datetime.datetime.utcfromtimestamp(int(time_from))
        time2 = None
        if time_to:
            time2 = datetime.datetime.utcfromtimestamp(int(time_to))
        for entry in get_data_between(time1, time2):
            # nice conversion to json-object
            data.append({
                'endpoint': entry.endpoint,
                'execution_time': entry.execution_time,
                'time': str(entry.time),
                'version': entry.version,
                'group_by': entry.group_by,
                'ip': entry.ip
            })
        return jwt.encode({'data': json.dumps(data)}, config.security_token, algorithm='HS256')
    except ValueError as e:
        return 'ValueError: {}'.format(e)


@blueprint.route('/get_json_monitor_rules')
def get_json_monitor_rules():
    """
    The returned data is the data that is encrypted using a security token. This security token is set in the
    configuration.
    :return: all entries from the database (rules-table)
    """
    data = []
    try:
        for entry in get_monitor_data():
            # nice conversion to json-object
            data.append({
                'endpoint': entry.endpoint,
                'last_accessed': str(entry.last_accessed),
                'monitor': entry.monitor,
                'time_added': str(entry.time_added),
                'version_added': entry.version_added
            })
        return jwt.encode({'data': json.dumps(data)}, config.security_token, algorithm='HS256')
    except ValueError as e:
        return 'ValueError: {}'.format(e)


@blueprint.route('/get_json_details')
def get_json_details():
    """
    Some details about the deployment, such as the current version, etc...
    :return: a json-object with the details.
    """
    return jsonify(get_details())
