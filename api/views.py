from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from json import loads
from api.models import *
from api.serializers import *
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone

@csrf_exempt
def resources(request):
  if request.method == 'GET':
    resources = Resource.objects.all()
    serializer = ResourceWithProviderSerializer(resources, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def resource(request, pk=None):
  if request.method == 'GET':
    resource = Resource.objects.get(pk=pk)
    serializer = ResourceWithProviderSerializer(resource)

  elif request.method == 'POST':
    body_unicode = request.body.decode('utf-8')
    params = loads(body_unicode)

    resource = Resource.objects.create(provider_id=params['provider_id'], type=params['type'], 
      details=params['details'])
    serializer = ResourceSerializer(resource)

  return JsonResponse(serializer.data, safe=False)
    

@csrf_exempt
def providers(request):
  if request.method == 'GET':
    params = loads(request.GET.get('params', '{}'))

    if params:
      q_objects = Q()
      for param_name, value in params['details'].items():
        q_objects.add(Q(**{'{0}__{1}__{2}'.format('resources', 'details', param_name): value}), Q.AND)

      providers = Provider.objects.filter(resources__type=params['resource_type']).filter(q_objects).distinct()
      serializer = ProviderWithResourcesSerializer(providers, many=True)

    else: 
      providers = Provider.objects.all()
      serializer = ProviderSerializer(providers, many=True)

    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def provider(request, pk=None):
  if request.method == 'GET':
    provider = Provider.objects.get(pk=pk)
    serializer = ProviderSerializer(provider)
    return JsonResponse(serializer.data, safe=False)

  elif request.method == 'POST':
    body_unicode = request.body.decode('utf-8')
    params = loads(body_unicode)

    provider = Provider.objects.create(first_name=params['first_name'], last_name=params['last_name'], email=params['email'])
    serializer = ProviderSerializer(provider)
    return JsonResponse(serializer.data, safe=False)

  elif request.method == 'PUT': 
    body_unicode = request.body.decode('utf-8')
    params = loads(body_unicode)
      
    provider = Provider.objects.filter(pk=pk)
    provider.update(**params)
    serializer = ProviderSerializer(provider.first())
    return JsonResponse(serializer.data, safe=False)

  elif request.method == 'DELETE':
    provider = Provider.objects.filter(pk=pk).first()
    provider.delete()
    return JsonResponse({}, status=200)

@csrf_exempt
def clients(request):
  if request.method == 'GET':
    clients = Client.objects.all()
    serializer = ClientSerializer(clients, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def dashboard_clients(request):
  if request.method == 'GET':
    two_weeks_ago = timezone.now() - timedelta(weeks=2)
    clients = Client.objects.filter(needs__needresourcematch__updated_at__gt = two_weeks_ago).distinct()
    serializer = DashboardClientSerializer(clients, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def client(request, pk=None):
  if request.method == 'GET':
    client = Client.objects.get(pk=pk)
    serializer = ClientSerializer(client)
    return JsonResponse(serializer.data, safe=False)

  elif request.method == 'POST':
    body_unicode = request.body.decode('utf-8')
    params = loads(body_unicode)

    client = Client.objects.create(first_name=params['first_name'], last_name=params['last_name'], email=params['email'])
    serializer = ClientSerializer(client)
    return JsonResponse(serializer.data, safe=False)

  elif request.method == 'PUT': 
    body_unicode = request.body.decode('utf-8')
    params = loads(body_unicode)
      
    client = Client.objects.filter(pk=pk)
    client.update(**params)
    serializer = ClientSerializer(client.first())
    return JsonResponse(serializer.data, safe=False)

  elif request.method == 'DELETE':
    client = Client.objects.filter(pk=pk).first()
    client.delete()
    return JsonResponse({}, status=200)

@csrf_exempt
def client_needs(request, client_id):
  # GET returns all needs for the specified Client
  if request.method == 'POST': # POST creates a new need for the specified Client   
    need = Need.objects.create(client_id=client_id)
    serializer = NeedResourceMatchStatusSerializer(need)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def client_need(request, client_id, pk):
  # GET returns the specific client need
  if request.method == 'PUT': 
    body_unicode = request.body.decode('utf-8')
    params = loads(body_unicode)
      
    need = Need.objects.filter(client_id = client_id, pk=pk).first()
    need.type=params['need_type']
    need.requirements=params['requirements']
    need.save()
    serializer = NeedResourceMatchStatusSerializer(need)
    return JsonResponse(serializer.data, safe=False)

  elif request.method == 'DELETE':
    need = Need.objects.filter(client_id = client_id, pk=pk).first()
    need.delete()
    return JsonResponse({}, status=200)

@csrf_exempt
def need_resource(request, need_id, pk):
  if request.method == 'POST': # create NeedResourceMatch or update if one already exists for need / resource combination
    body_unicode = request.body.decode('utf-8')
    params = loads(body_unicode)

    NeedResourceMatch.objects.update_or_create(need_id = need_id, resource_id = pk,
      defaults={'pending': params['pending'], 'fulfilled': params['fulfilled']})

  elif request.method == 'DELETE':
    NeedResourceMatch.objects.filter(need_id = need_id, resource_id=pk).delete()

  need = Need.objects.get(pk=need_id)
  serializer = NeedResourceMatchStatusSerializer(need)
  return JsonResponse(serializer.data, safe=False)

# need = Need.objects.filter(client_id = client_id, pk=pk)
# if need:
#   return HttpResponse("<h5>if</h5>")

# data = JSONParser().parse(request
# serializer = NeedSerializer(data=data)

# if serializer.is_valid():
#     serializer.save()
#     return JsonResponse(serializer.data, status=201)
# return JsonResponse(serializer.errors, status=400)

# @csrf_exempt
# def resources(request):
#     if request.method == 'GET':
#       params = loads(request.GET.get('params', '{}'))
      
#       q_objects = Q()
#       for param_name, value in params['details'].items():
#         q_objects.add(Q(**{'{0}__{1}'.format('details', param_name): value}), Q.AND)

#       resources = Resource.objects.filter(type=params['type']).filter(q_objects)
#       serializer = ResourceSerializer(resources, many=True)
#       return JsonResponse(serializer.data, safe=False)

# elif request.method == 'POST':
#     data = JSONParser().parse(request)
#     serializer = ResourceSerializer(data=data)
#     if serializer.is_valid():
#         serializer.save()
#         return JsonResponse(serializer.data, status=201)
#     return JsonResponse(serializer.errors, status=400)
