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

        response_query = requests.get(f"http://{settings.SERVICE_QUERY_SELECTION_HOST}:{settings.SERVICE_QUERY_SELECTION_PORT}/{settings.SERVICE_QUERY_SELECTION}/query_selection", parameters)
        query = json.loads(response_query.content)['query']
        returned_params = json.loads(response_query.content)['returned_params']

        json_parameters = dict(parameters)
        json_parameters['query'] = query

        # print(json_parameters)

        response = requests.get(f"http://{settings.SERVICE_KNOWLEDGE_HOST}:{settings.SERVICE_KNOWLEDGE_PORT}/{settings.SERVICE_KNOWLEDGE}/queries", json_parameters)
        # print(response.content)
        json_response = json.loads(response.content)

        response = {
                     "fulfillmentMessages": [
                         {
                           "text": {
                             "text": response_templates(query, json_response)
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


def response_templates(query, results):
    messages = []

    if query == '3':
        for res in results['results']:
            messages.append('The hotel ' + res['name'] + ' starts checkin at ' + res['starthour'] + ' and ends at ' + res['endhour'] + '.')

    return messages
