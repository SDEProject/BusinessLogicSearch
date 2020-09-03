import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from requests import Response
from rest_framework import viewsets, mixins
from travelando import settings
import json


# Create your views here.
class SearchBusinessView(View):
    def get(self, request):
        parameters = request.GET
        # print(parameters.get('shop_enum', None))
        print(parameters)
        print('call query')
        response_query = requests.get(f"http://{settings.SERVICE_QUERY_SELECTION_HOST}:{settings.SERVICE_QUERY_SELECTION_PORT}/{settings.SERVICE_QUERY_SELECTION}/query_selection", parameters)
        query = json.loads(response_query.content)['query']
        print('done')
        # returned_params = json.loads(response_query.content)['returned_params']

        json_parameters = dict(parameters)
        json_parameters['query'] = query

        # print(json_parameters)
        # print(f"http://{settings.SERVICE_KNOWLEDGE_HOST}:{settings.SERVICE_KNOWLEDGE_PORT}/{settings.SERVICE_KNOWLEDGE}/queries")
        response = requests.get(f"http://{settings.SERVICE_KNOWLEDGE_HOST}:{settings.SERVICE_KNOWLEDGE_PORT}/{settings.SERVICE_KNOWLEDGE}/queries", json_parameters)
        # print(response.content)
        json_response = json.loads(response.content)

        response = {
                     "fulfillmentMessages": [
                         {
                           "text": {
                             "text": response_templates(query, json_response['results'], parameters)
                           }
                         }
                       ]
                     }

        # for res in json_response['results']:
        #     response['fulfillmentMessages'][0]['text']['text'].append('The hotel ' + res['name'] + ' starts checkin at ' + res['starthour'] + ' and ends at ' + res['endhour'] + '.')

        # retrieve get parameter request.GET.get('intentName', None)
        # response['fulfillmentMessages'][0]['text']['text'].append('I\'ll execute query ' + query)
        # return JsonResponse(response.json(), safe=False)
        return JsonResponse(response)


def response_templates(query, results, parameters):
    messages = []
    print(results)

    if query == '3':
        template = 'The hotel {name} starts checkin at {starthour} and ends at {endhour}.'
        for res in results:
            messages.append(template.format(name=res['name'], starthour=res['starthour'], endhour=res['endhour']))
    elif query == '6':
        template = 'The hotel {name} in {city} starts checkin at {starthour} and ends at {endhour}.'
        for res in results:
            messages.append(template.format(name=res['name'], city=res['city'], starthour=res['starthour'], endhour=res['endhour']))
    elif query == '4':
        template = 'The {shop_enum} in {region} are: {shops}.'
        tmp = []
        for res in results:
            tmp.append(res['name'] + ' ('+res['city']+')')
        messages.append(template.format(shop_enum=normalize_enum(parameters.get('shop_enum', None)), region=parameters.get('region', None), shops=', '.join(tmp)))
    elif query == '5':
        template = 'The {shop_enum} in {city} ({region}) are: {shops}.'
        tmp = []
        for res in results:
            tmp.append(res['name'])
        messages.append(template.format(shop_enum=normalize_enum(parameters.get('shop_enum', None)), city=parameters.get('city', None), region=parameters.get('region', None), shops=', '.join(tmp)))
    elif query == '7':
        template = 'The {shop_enum} {name} is in {address}, {city} ({region}).'
        for res in results:
            messages.append(template.format(shop_enum=normalize_enum(parameters.get('shop_enum', None)), name=res['name'], address=res['street'], city=res['city'], region=normalize_from_ontology(res['province'])))
    elif query == '8':
        template = 'The {difficulty} difficulty activity paths with duration {time} are: {paths}.'
    elif query == '9':
        template = 'The {difficulty} difficulty activity paths {equipment} are: {paths}.'
        path_template = 'activity path {name} starts in {poi_from} and ends in {poi_to}'
        tmp = []
        for res in results:
            tmp.append(path_template.format(name=res['name'], poi_from=res['poi_from'], poi_to=res['poi_to']))
        messages.append(template.format(difficulty=parameters.get('path_difficulty', None), equipment=parameters.get('info_equipment', None), paths='; '.join(tmp)))

    return messages


def normalize_from_ontology(value):
    return value.replace('http://www.semanticweb.org/aleca/ontologies/2019/10/untitled-ontology-10#', '')


def normalize_enum(value):
    if value == 'S_Bikes':
        return 'bike shop'
    return value
