from django.shortcuts import render

from elasticsearch import Elasticsearch
from django.http import HttpResponse
from django.template import RequestContext, loader

import re

import json


def parse_query(query = None):

    if query is None:
        return None

    q = re.sub(r'[^A-Za-z0-9_|&:\ ><@#]+', r'', query)
    q = re.sub(r'@', r'author:', q)
    q = re.sub(r'#', r'tags:', q)

    return q

def index(request):

    page = 1
    size = 10

    if not request.GET.get('q'):
        context = RequestContext(request, { } )
        return render(request, 'mirko/index.html', context)

    if request.GET.get('strona'):
        page = abs(int(request.GET.get('strona')))
        if page == 0:
            page = 1

    if request.GET.get('ile'):
        size = abs(int(request.GET.get('ile')))

    q = parse_query(request.GET.get('q'))
    query = {}
    query['size'] = size
    query['from'] = (page - 1) * size #from is reserved keyword in python
    query['query'] = {}
    query['query']['query_string'] = {}
    query['query']['query_string']['query'] = q
    query['query']['query_string']['default_operator'] = "and"
    query['query']['query_string']['fields'] = ["text^2", "author^4","comments.text^0.6", "comments.author^0.6"]
    query['query']['query_string']['default_field'] = "_all"
    query['sort'] = []
    query['sort'].append({'_score' : 'desc'})
    query['sort'].append({'plus' : 'desc'})
    query['sort'].append({'timestamp' : 'desc'})
    query['highlight'] = {}
    query['highlight']['fields'] = '_all'

    es = Elasticsearch()

    res = es.search(
            index="mirko2",
            body=json.dumps(query)
            )

    results = []
    for i in res['hits']['hits']:
        results.append(i['_source'])


    context = RequestContext(request, { 'res' : res['hits'], 'q' : q, 'r' : results, 'size' : size, 'page' : page } )
    return render(request, 'mirko/index.html', context)
