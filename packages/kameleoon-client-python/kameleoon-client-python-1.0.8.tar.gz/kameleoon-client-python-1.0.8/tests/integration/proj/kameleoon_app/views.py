import json

from django.http import JsonResponse
from django.apps import apps

from kameleoon.data import CustomData
from kameleoon.exceptions import NotActivated, NotTargeted, KameleoonException, ExperimentConfigurationNotFound

kameleoon_app = apps.get_app_config('kameleoon_app')
client = kameleoon_app.kameleoon_client
local_ip = '127.0.0.1'

def variation_view(request):
    visitor_code = client.obtain_visitor_code(request.COOKIES, local_ip)
    experiment_id = 135471
    experiment = list(filter(lambda x: x['id'] == experiment_id, client.experiments))
    variation_id = None
    if request.GET.get('blocking'):
        client.blocking = True
    try:
        variation_id = client.trigger_experiment(visitor_code, experiment_id)
    except NotActivated:
        variation_id = None
    except NotTargeted:
        variation_id = None
    except ExperimentConfigurationNotFound:
        variation_id = None
    except KameleoonException as ex:
        print(ex)
    client.blocking = False
    response = JsonResponse({'visitor_code': visitor_code, 'variation': variation_id})
    return response


def simple_test_view(request):
    experiment_id = 777
    deviations = {
        "1": 0.5,
        "2": 0.25,
        "3": 0.25
    }
    experiment = {
        "id": experiment_id,
        "deviations": deviations,
        "respoolTime": {}
    }
    client.experiments.append(experiment)
    visitor_code = client.obtain_visitor_code(request.COOKIES, local_ip)

    variation_id = None
    try:
        variation_id = client.trigger_experiment(visitor_code, experiment_id)
    except NotActivated:
        variation_id = 0
    except NotTargeted:
        variation_id = 0
    except ExperimentConfigurationNotFound:
        variation_id = 0
    except KameleoonException as ex:
        print(ex)

    return JsonResponse({'experiment': experiment_id, 'variation': variation_id})


def activate_view(request):
    visitor_code = client.obtain_visitor_code(request.COOKIES, local_ip)
    feature_key = "test_key"
    is_activated = client.activate_feature(visitor_code, feature_key)
    response = JsonResponse({"visitor_code": visitor_code, "activate": is_activated})
    return response


def add_data_view(request):
    visitor_code = client.obtain_visitor_code(request.COOKIES, local_ip)
    data = {}
    if 'data' in request.GET:
        data = json.loads(request.GET.get('data'))
        for x in data:
            client.add_data(visitor_code, CustomData(**x))
        data = {}
        for k, v in client.data.items():
            data[k] = [x.to_dict() for x in v]
    response = JsonResponse({"data": data})
    return response

def flush_view(request):
    kameleoon_cookie = client.obtain_visitor_code(request.COOKIES, local_ip)
    client.flush()
    data = {}
    for k, v in client.data.items():
        data[k] = [x.to_dict() for x in v]
    response = JsonResponse({"data": data})
    return response
