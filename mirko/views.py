from django.shortcuts import render

from elasticsearch import Elasticsearch
from django.http import HttpResponse
from django.template import RequestContext, loader

import re

import json

# Create your views here.

def index(request):

    if not request.GET.get('q'):
        context = RequestContext(request, { } )
        return render(request, 'mirko/index.html', context)

    q = re.sub(r'[^A-Za-z0-9_|&:\ ><]+', r'', request.GET.get('q'))
    query = {}
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
            size=100,
            body=json.dumps(query)
            )

    print("Got %d Hits:" % res['hits']['total'])

    results = []
    for i in res['hits']['hits']:
        results.append(i['_source'])


    context = RequestContext(request, { 'res' : res['hits'], 'q' : q, 'r' : results } )
    return render(request, 'mirko/index.html', context)
