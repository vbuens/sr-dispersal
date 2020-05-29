from django.shortcuts import render
from django.http import HttpResponse
from .forms import InputForm, PredictForm
# from .GPModel.GPM_django import runmodel
from .GPModel.GPM_django_PF import runmodel, stabilityclass_latlon
# from django_countries import countries
# from .GPModel.atmospheric_functions import stabilityclass_input, stabilityclass_API
from .GPModel.releaseprediction import RH_APIcall
# Create your views here.

def index(request):
    return render(request, 'dispersal/index.html') #"Hello, world. You're at the model index. Go to run model")

def about(request):
    return render(request, 'dispersal/about.html') #"Hello, world. You're at the model index. Go to run model")

def run(request):
    template_name = 'dispersal/run.html'
    form = InputForm()
    return render(request, template_name, {'form': form})


def release(request):
    template_name = 'dispersal/prediction.html'
    form = PredictForm()
    return render(request, template_name, {'form': form})


def predictions(request):
    if request.method == 'POST':
        # return render(request, 'dispersal/prediction_results.html')
    # else:
        form = PredictForm(request.POST)
        if form.is_valid():
            lat = form.cleaned_data['lat']
            NS = form.cleaned_data['NS']
            lon = form.cleaned_data['lon']
            WE = form.cleaned_data['WE']
            print(lat,NS,lon, WE)
            lat=float(NS+lat)
            lon=float(WE+lon)
            print(lat,lon)
            prediction,city,country=RH_APIcall(lat,lon)
            print(prediction)
            # context={
            #     'headers': [u'Date',u'Relative Hummidity',u'Precipitation (mm)'],
            #     'rows':
            # }
            # context.update({'context':prediction})
            return render(request, 'dispersal/prediction_results.html', {'context':prediction,'city':city,'country':country})
    # else:
    #     return render(request, 'dispersal/prediction.html')

    # return render(request,'dispersal/prediction.html', {'form': form,'context':context})

def results(request):
    if request.method == 'POST':
        return render(request, 'dispersal/run.html')
    else:
        form = InputForm(request.GET)
        if form.is_valid():
            # form.save()
            # Q=form.cleaned_data['source'] #source strength
            graph='2D'
            lat = form.cleaned_data['lat']
            NS = form.cleaned_data['NS']
            lon = form.cleaned_data['lon']
            WE = form.cleaned_data['WE']
            lat=float(NS+lat)
            lon=float(WE+lon)

            # if request.GET.get('weathercheck') == "on":
            #     UV = form.cleaned_data['UV']
            #     wind = form.cleaned_data['wind']
            #     cloudiness =  int(form.cleaned_data['cloudperc'])/100
            #     #cloudiness =  int(request.GET.get('cloudperc'))/100
            #     stabilityclasses=stabilityclass_input(wind,cloudiness,UV)
            #
            # else:
            stabilityclasses,wind,RH,I,R,clouds,UV,city, country =stabilityclass_latlon(lat,lon)

            H = float(form.cleaned_data['height'])
            bushperc = int(form.cleaned_data['bushperc'])/100
            leafperc = int(form.cleaned_data['leafperc'])/100
            # Calculating the source strength based on percentage of infection
            # Q = round(34661.61598*bushperc*leafperc,2)
            # Q = round(224607.272*bushperc*leafperc,2)
            Q = round(623909.0877*0.6*bushperc*leafperc,2)

            maxdistances=runmodel(graph,H,Q, float(wind),I,R,clouds,stabilityclasses)
            context={'source':Q,'country':country,'city':city,
                    'rain': R,'RH': RH,'clouds':clouds*100,'Irradiance': I,
                    'wind': wind, 'bushperc': round(bushperc*100,0), 'leafperc': round(leafperc*100),
                    'X99d': maxdistances['Day'][3],'X99n': maxdistances['Night'][3],
                    'XminD': maxdistances['Day'][4],'XminN': maxdistances['Night'][4],
                    'X95d': maxdistances['Day'][0],'X75d': maxdistances['Day'][1],
                    'X50d': maxdistances['Day'][2],'X95n': maxdistances['Night'][0],
                    'X75n': maxdistances['Night'][1],'X50n': maxdistances['Night'][2]}
            return render(request, 'dispersal/results.html', context)
        else:
            return render(request,'dispersal/run.html', {'form': form})



def results_old(request):
    if request.method == 'POST':
        return render(request, 'dispersal/run.html')
    else:
        form = InputForm(request.GET)
        if form.is_valid():
            form.save()
            # Q=form.cleaned_data['source'] #source strength
            graph='2D'
            country = form.cleaned_data['country']
            country=dict(countries)[country].strip(' ')
            city = form.cleaned_data['city']

            if request.GET.get('weathercheck') == "on":
                UV = form.cleaned_data['UV']
                wind = form.cleaned_data['wind']
                cloudiness =  int(form.cleaned_data['cloudperc'])/100
                #cloudiness =  int(request.GET.get('cloudperc'))/100
                stabilityclasses=stabilityclass_input(wind,cloudiness,UV)

            else:
                stabilityclasses,wind = stabilityclass_API(city,country)

            H = float(form.cleaned_data['height'])
            bushperc = int(form.cleaned_data['bushperc'])/100
            leafperc = int(form.cleaned_data['leafperc'])/100
            # bushperc = int(request.GET.get('bushperc'))/100
            # leafperc = int(request.GET.get('leafperc'))/100
            # print(stabilityclasses, wind)
            # Calculating the source strength based on percentage of infection
            Q = round(34661.61598*bushperc*leafperc,2)
            # print(Q)
            # maxdistances=runmodel(graph,H,Q, float(wind),stabilityclasses)
            maxdistances=runmodel(graph,H,Q, float(wind),I,R,clouds,stabilityclasses)
            context={'source':Q,'country':country,'city':city,
                    'wind': wind, 'bushperc': round(bushperc*100,0), 'leafperc': round(leafperc*100),
                    'X95d': maxdistances['Day'][0],'X75d': maxdistances['Day'][1],
                    'X50d': maxdistances['Day'][2],'X95n': maxdistances['Night'][0],
                    'X75n': maxdistances['Night'][1],'X50n': maxdistances['Night'][2]}
            return render(request, 'dispersal/results.html', context)
        else:
            return render(request,'dispersal/run.html', {'form': form})
