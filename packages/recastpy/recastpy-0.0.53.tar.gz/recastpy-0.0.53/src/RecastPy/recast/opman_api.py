"""
This is a Python wrapper for interacting with the OpMan HTTP REST API. This module should do nothing other than
facilitate making calls to, and receiving responses from, that API. The OpMan API should be exclusively responsible
for all OpMan related logic.
"""
import urllib3
import json
from RecastPy.aws import secrets_manager

OPMAN_API_BASE_URL = "https://ly231vyas0.execute-api.us-east-1.amazonaws.com/{stage}"


def _get_api_key():
    return secrets_manager.get_secret_value("prod/opman/api_key", "key")


def request(method, endpoint, fields=None, body=None, stage='production'):
    """
    This method will allow the caller to use any method on any endpoint.

    :param method: GET, POST, etc.
    :param endpoint: API Gateway resource to be called, such as /v2/service/event
    :param fields: HTTP header fields
    :param body: HTTP body
    :param stage: API Gateway stage to call, defaults to production
    :return: HTTP response
    """

    http = urllib3.PoolManager()

    url = f"{OPMAN_API_BASE_URL.replace('{stage}', stage)}/{endpoint}"

    api_key = _get_api_key()

    response = http.request(
        method=method,
        url=url,
        headers={
            'x-api-key': api_key,
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        fields=fields,
        body=json.dumps(body)
    )

    try:
        return json.loads(response.data.decode('utf-8'))
    except:
        return response.data.decode('utf-8')


def post_event(
        event_source: str,
        event_type: str,
        event_details: json,
        event_bus: str = 'recast',
        api_version: str = 'v2'
):
    """
    This method will POST to the /{version}/service/event endpoint, which sends an event to the {event_bus} bus.

    :param event_source: The source of the event, for example "recast.workflow".
    :param event_type: The event type, for example "DataIngestStarted".
    :param event_details: The details associated with the specific event type.
    :param event_bus: The bust to post the event to, defaults to "recast".
    :param api_version: The version of the API to call, defaults to "v2".
    :return: HTTP response
    """

    body = {
        'event_bus': event_bus,
        'event_source': event_source,
        'event_type': event_type,
        'event_details': event_details
    }
    response = request('POST', f'{api_version}/service/event', body=body)

    return response


if __name__ == '__main__':
    # test getting a list of fleet runs
    # response = request('GET', 'v2/service/fleet_runs')

    # test posting an event to the recast event bus.
    response = post_event(
        event_source='recast.workflow',
        event_type='DataIngestStarted',
        event_details={
            'ingest_id': 'b8844406-f084-4281-b7c0-e0340090e145',
            'ingest_task_ids': [
                {'ingest_and_validate': '32976509-54cf-475b-a755-0aee890386c8'}
            ]
        }
    )

    print(response)
