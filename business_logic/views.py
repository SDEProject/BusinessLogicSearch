import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from requests import Response
from rest_framework import viewsets, mixins
from travelando import settings
import json


MAXIMUM_RESULTS_SHOWN = 5


# Create your views here.
class SearchBusinessView(View):
    def get(self, request):
        parameters = request.GET

        response_query = requests.get(f"http://{settings.SERVICE_QUERY_SELECTION_HOST}:{settings.SERVICE_QUERY_SELECTION_PORT}/{settings.SERVICE_QUERY_SELECTION}/query_selection", parameters)
        query = json.loads(response_query.content)['query']
        # returned_params = json.loads(response_query.content)['returned_params']

        json_parameters = dict(parameters)
        json_parameters['query'] = query

        response = requests.get(f"http://{settings.SERVICE_KNOWLEDGE_HOST}:{settings.SERVICE_KNOWLEDGE_PORT}/{settings.SERVICE_KNOWLEDGE}/queries", json_parameters)
        json_response = json.loads(response.content)

        response = {
            "fulfillmentMessages": [{
                "text": {
                    "text": [response_templates(query, json_response['results'], parameters)]
                }
            }]
        }
        return JsonResponse(response)


def response_templates(query, results, parameters):
    messages = ''
    print(results)

    if len(results) > 0:
        try:
            iterations = min(len(results), MAXIMUM_RESULTS_SHOWN)
            if query == '3':
                hot = 'hotels' if len(results) > 1 else 'hotel'
                template = f'I\' ve found {len(results)} {hot}. Here the first {MAXIMUM_RESULTS_SHOWN}:\n'
                hotel_template = '• {name} starts checkin at {starthour} and ends at {endhour}'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    endhour = '00:00' if res['endhour'] == 'None' else res['endhour']
                    tmp.append(hotel_template.format(name=res['name'], starthour=res['starthour'], endhour=endhour))
                messages = template + ';\n'.join(tmp) + '.'
            elif query == '6':
                hot = 'hotels' if len(results) > 1 else 'hotel'
                template = f'I\' ve found {len(results)} {hot}.'
                if iterations <= MAXIMUM_RESULTS_SHOWN:
                    template += '\n\n'
                else:
                    template += f' The first {MAXIMUM_RESULTS_SHOWN} are:\n\n'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    details = f'The accommodation {res["name"]} has the following details:\n'
                    details += f'• type {normalize_from_ontology(res["accommodationenum"])};\n'
                    if res.get('stars') is not None:
                        details += f'• stars {res["stars"]};\n'
                    details += f'• {res["street"]} {res["number"]}, {res["city"]} ({normalize_from_ontology(res["province"])}).'
                    endhour = '00:00' if res['endhour'] == 'None' else res['endhour']
                    details += f'• checkin {res["starthour"]}-{endhour}.'
                    tmp.append(details)
                messages = template + ';\n'.join(tmp) + '.'
            elif query == '4':
                template = f'There are {len(results)} {normalize_enum(parameters.get("shop_enum", None))} in {parameters.get("region", None)}. Here the first {MAXIMUM_RESULTS_SHOWN}:\n.'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    tmp.append('• ' + res['name'] + ' ('+res['city']+')')
                messages = template + ';\n'.join(tmp) + '.'
            elif query == '5':
                template = f'There {len(results)} {normalize_enum(parameters.get("shop_enum", None))} in {parameters.get("city", None)} ({parameters.get("region", None)}). Here the first {MAXIMUM_RESULTS_SHOWN}:'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    tmp.append('• ' + res['name'])
                messages = template + ';\n'.join(tmp) + '.'
            elif query == '7':
                template = f'There are {len(results)} {normalize_enum(parameters.get("shop_enum", None))}'
                if iterations <= MAXIMUM_RESULTS_SHOWN:
                    template += ':\n'
                else:
                    template += f'. Here the first {MAXIMUM_RESULTS_SHOWN}:\n'
                shop_template = '• {name}\n    in {address}, {city} ({region})'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    tmp.append(shop_template.format(name=res['name'], address=res['street'], city=res['city'], region=normalize_from_ontology(res['province'])))
                messages = template + ';\n'.join(tmp) + '.'
            elif query == '8':
                template = 'The {difficulty} difficulty activity paths with duration {time} minutes are: {paths}.'
            elif query == '9':
                template = f'There are {len(results)} {parameters.get("path_difficulty", None)} difficulty activity paths {parameters.get("info_equipment", None)}.'
                if iterations <= MAXIMUM_RESULTS_SHOWN:
                    template += '\n\n'
                else:
                    template += f' Here the first {MAXIMUM_RESULTS_SHOWN}:\n\n'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    details = f'The activity path {res["name"]} has the following details:\n'
                    details += f'• from {res["poi_from"]};\n'
                    details += f'• to {res["poi_to"]};\n'
                    details += f'• length {res["length"]["#text"]} meters;\n'
                    details += f'• duration {res["time"]["#text"]} minutes.'
                    tmp.append(details)
                messages = template + '\n\n'.join(tmp)
            elif query == '12':
                template = f'There are {len(results)} smooth activity paths. Here the first {MAXIMUM_RESULTS_SHOWN}:\n'
                path_template = '• activity path {name} from {poi_from} to {poi_to}'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    tmp.append(path_template.format(name=res['name'], poi_from=res['poi_from'], poi_to=res['poi_to']))
                messages = template + ';\n'.join(tmp) + '.'
            elif query == '13':
                template = f'There are {len(results)} activity paths from {parameters.get("poi_activity_from", None)} to {parameters.get("poi_activity_to", None)}. Here the first {MAXIMUM_RESULTS_SHOWN}:\n'
                path_template = '• activity path {name}'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    tmp.append(path_template.format(name=res['name']))
                messages = template + ';\n'.join(tmp) + '.'
            elif query == '14':
                template = f'There are {len(results)} activity paths with {parameters.get("difficulty", None)} difficulty.'
                if iterations <= MAXIMUM_RESULTS_SHOWN:
                    template += '\n\n'
                else:
                    template += f' Here the first {MAXIMUM_RESULTS_SHOWN}:\n\n'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    details = f'The activity path {res["name"]} has the following details:\n'
                    details += f'• from {res["poi_from"]};\n'
                    details += f'• to {res["poi_to"]};\n'
                    details += f'• length {res["length"]["#text"]} meters;\n'
                    details += f'• duration {res["time"]["#text"]} minutes.'
                    tmp.append(details)
                messages = template + '\n\n'.join(tmp)
            elif query == '17':
                template = f'There are {len(results)} activity paths from {parameters.get("poi_activity_from", None)}.'
                if iterations <= MAXIMUM_RESULTS_SHOWN:
                    template += '\n\n'
                else:
                    template += f' Here the first {MAXIMUM_RESULTS_SHOWN}:\n\n'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    details = f'The activity path {res["name"]} has the following details:\n'
                    details += f'• from {res["poi_from"]};\n'
                    details += f'• to {res["poi_to"]};\n'
                    details += f'• difficulty {normalize_from_ontology(res["difficulty"])};\n'
                    details += f'• length {res["length"]["#text"]} meters;\n'
                    details += f'• duration {res["time"]["#text"]} minutes.'
                    tmp.append(details)
                messages = template + '\n\n'.join(tmp)
            elif query == '18':
                template = f'There are {len(results)} activity paths from {parameters.get("poi_activity_from", None)} to {parameters.get("poi_activity_to", None)}.'
                if iterations <= MAXIMUM_RESULTS_SHOWN:
                    template += '\n\n'
                else:
                    template += f' Here the first {MAXIMUM_RESULTS_SHOWN}:\n\n'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    details = f'The activity path {res["name"]} has the following details:\n'
                    details += f'• difficulty {normalize_from_ontology(res["difficulty"])};\n'
                    details += f'• length {res["length"]["#text"]} meters;\n'
                    details += f'• duration {res["time"]["#text"]} minutes.'
                    tmp.append(details)
                messages = template + '\n\n'.join(tmp)
            elif query == '19':
                template = f'There are {len(results)} activity paths with number {parameters.get("path_number", None)}.\n\n'
                tmp = []
                for res in results:
                    details = f'The activity path {res["name"]} has the following details:\n'
                    details += f'• from {res["poi_from"]};\n'
                    details += f'• to {res["poi_to"]};\n'
                    details += f'• difficulty {normalize_from_ontology(res["difficulty"])};\n'
                    details += f'• length {res["length"]["#text"]} meters;\n'
                    details += f'• duration {res["time"]["#text"]} minutes.'
                    tmp.append(details)
                messages = template + '\n\n'.join(tmp)
        except:
            print('Error in generating response.')
            messages = 'Sorry, I had a problem in generating the response for you.'
    else:
        messages = 'No results found with these parameters.'

    return messages


def normalize_from_ontology(value):
    return value.replace('http://www.semanticweb.org/aleca/ontologies/2019/10/untitled-ontology-10#', '')


def normalize_enum(value):
    if value == 'S_Bikes':
        return 'bike shop'
    return value
