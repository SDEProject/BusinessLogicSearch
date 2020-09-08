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
        status_code = 200

        response_query = requests.get(f"http://{settings.SERVICE_QUERY_SELECTION_HOST}:{settings.SERVICE_QUERY_SELECTION_PORT}/{settings.SERVICE_QUERY_SELECTION}/query_selection", parameters)
        if response_query.status_code == 200:
            query = json.loads(response_query.content)['query']

            json_parameters = dict(parameters)
            json_parameters['query'] = query

            response = requests.get(f"http://{settings.SERVICE_KNOWLEDGE_HOST}:{settings.SERVICE_KNOWLEDGE_PORT}/{settings.SERVICE_KNOWLEDGE}/queries", json_parameters)
            json_response = json.loads(response.content)
            if response.status_code == 200:
                messages, status_code = response_templates(query, json_response['results'], parameters)
            else:
                messages = json_response['text']
                status_code = response.status_code
            response = {
                "fulfillmentMessages": [{
                    "text": {
                        "text": [messages]
                    }
                }]
            }
        else:
            status_code = response_query.status_code
            response = {
                "fulfillmentMessages": [{
                    "text": {
                        "text": ['Sorry, I cannot resolve your request.']
                    }
                }]
            }
        return JsonResponse(response, status=status_code)


def response_templates(query, results, parameters):
    messages = ''
    print(results)
    status_code = 200

    if len(results) > 0:
        try:
            iterations = min(len(results), MAXIMUM_RESULTS_SHOWN)
            if query == '3':
                hot = 'hotels' if len(results) > 1 else 'hotel'
                template = f'I\' ve found {len(results)} {hot}.'
                if len(results) <= MAXIMUM_RESULTS_SHOWN:
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
                    details += f'• {res["street"]} {res["number"]};\n'
                    endhour = '00:00' if res['endhour'] == 'None' else res['endhour']
                    details += f'• checkin {res["starthour"]}-{endhour}.'
                    tmp.append(details)
                messages = template + '\n\n'.join(tmp)
            elif query == '6':
                hot = 'hotels' if len(results) > 1 else 'hotel'
                template = f'I\' ve found {len(results)} {hot}.'
                if len(results) <= MAXIMUM_RESULTS_SHOWN:
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
                    details += f'• {res["street"]} {res["number"]}, {res["city"]} ({normalize_from_ontology(res["province"])});\n'
                    endhour = '00:00' if res['endhour'] == 'None' else res['endhour']
                    details += f'• checkin {res["starthour"]}-{endhour}.'
                    tmp.append(details)
                messages = template + '\n\n'.join(tmp)
            elif query == '4':
                template = f'There are {len(results)} {normalize_enum(parameters.get("shop_enum", None))} in {parameters.get("region", None)}'
                if len(results) <= MAXIMUM_RESULTS_SHOWN:
                    template += ':\n\n'
                else:
                    template += f'. Here the first {MAXIMUM_RESULTS_SHOWN}:\n\n'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    tmp.append(f'• {res["name"]}\n    in {res["street"]} {res["number"]}, {res["city"]}')
                messages = template + ';\n\n'.join(tmp) + '.'
            elif query == '5':
                template = f'There {len(results)} {normalize_enum(parameters.get("shop_enum", None))}'
                if len(results) <= MAXIMUM_RESULTS_SHOWN:
                    template += ':\n\n'
                else:
                    template += f'. Here the first {MAXIMUM_RESULTS_SHOWN}:\n\n'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    tmp.append(f'• {res["name"]}\n    in {res["street"]} {res["number"]}, {res["city"]} ({normalize_from_ontology(res["province"])})')
                messages = template + ';\n\n'.join(tmp) + '.'
            elif query == '7':
                template = f'There are {len(results)} {normalize_enum(parameters.get("shop_enum", None))}'
                if len(results) <= MAXIMUM_RESULTS_SHOWN:
                    template += ':\n\n'
                else:
                    template += f'. Here the first {MAXIMUM_RESULTS_SHOWN}:\n\n'
                shop_template = '• {name}\n    in {address}, {city} ({region})'
                tmp = []
                for index in range(iterations):
                    res = results[index]
                    tmp.append(shop_template.format(name=res['name'], address=res['street'], city=res['city'], region=normalize_from_ontology(res['province'])))
                messages = template + ';\n\n'.join(tmp) + '.'
            elif query == '8':
                template = 'The {difficulty} difficulty activity paths with duration {time} minutes are: {paths}.'
            elif query == '9':
                template = f'There are {len(results)} {parameters.get("path_difficulty", None)} difficulty activity paths {parameters.get("info_equipment", None)}.'
                if len(results) <= MAXIMUM_RESULTS_SHOWN:
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
                if len(results) <= MAXIMUM_RESULTS_SHOWN:
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
                if len(results) <= MAXIMUM_RESULTS_SHOWN:
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
                if len(results) <= MAXIMUM_RESULTS_SHOWN:
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
            status_code = 500
    else:
        messages = 'No results found with these parameters.'
        status_code = 404

    return messages, status_code


def normalize_from_ontology(value):
    return value.replace('http://www.semanticweb.org/aleca/ontologies/2019/10/untitled-ontology-10#', '')


def normalize_enum(value):
    if value == 'S_Bikes':
        return 'bike shop'
    elif value == 'S_Local_traditional_products':
        return 'local traditional shop'
    elif value == 'S_Optician_photography':
        return 'optician and photography shop'
    elif value == 'S_Agricoltural_products':
        return 'agricoltural shop'
    elif value == 'S_Antiques':
        return 'antiques shop'
    elif value == 'S_Artists':
        return 'artists shop'
    elif value == 'S_Artist_gilder':
        return 'artist gilder shop'
    elif value == 'S_Beverages':
        return 'beverages shop'
    elif value == 'S_Bread_baked_goods':
        return 'bread and baked goods shop'
    elif value == 'S_Cleanings':
        return 'cleaning shop'
    elif value == 'S_Computer_accessories_technology':
        return 'technology shop'
    elif value == 'S_Drugstore':
        return 'drugstore'
    elif value == 'S_Fashion_clothing':
        return 'fashion shop'
    elif value == 'S_Flowers':
        return 'flower shop'
    elif value == 'S_Fruits_vegetables':
        return 'fruits and vegetables market'
    elif value == 'S_Groceries':
        return 'groceries'
    elif value == 'S_Handicrafts':
        return 'handicrafts'
    elif value == 'S_Home_furnishings':
        return 'home furniture shop'
    elif value == 'S_Housewares':
        return 'houseware shop'
    elif value == 'S_Jeweller_Goldsmiths':
        return 'jeweller'
    elif value == 'S_Kids_fashion':
        return 'kids fashion shop'
    elif value == 'S_Leather_ware_shoes':
        return 'shoes shop'
    elif value == 'S_Meat_sausages':
        return 'butcher'
    elif value == 'S_More_craft':
        return 'craft'
    elif value == 'S_Newspapers_books_stationary':
        return 'bookstore'
    elif value == 'S_Paints_Wallpapers':
        return 'paints shop'
    elif value == 'S_Pet_supplies':
        return 'pet supplies shop'
    elif value == 'S_Production_facilities_farm_shops':
        return 'farm shop'
    elif value == 'S_Quill_embroidery':
        return 'quill embroidery'
    elif value == 'S_Sculptor':
        return 'sculptor shop'
    elif value == 'S_Souvenirs':
        return 'souvenir shop'
    elif value == 'S_Sport_equipment':
        return 'sport equipment shop'
    elif value == 'S_Toys':
        return 'toys shop'
    elif value == 'S_Weaving_mill_arts':
        return 'weaving mill arts'
    return value
