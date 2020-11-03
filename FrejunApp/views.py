from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
import pandas as pd
from pathlib import Path
import os
import re
import requests
import xml.etree.ElementTree as ET
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent
# Create your views here.
path = os.path.join(BASE_DIR, 'FrejunApp/static/FrejunApp/csvfiles/')


def home(request):
    return render(request, 'FrejunApp/index.html')


def load(request):
    if request.method == "POST":
        csvfile = request.FILES['upload']
        fs = FileSystemStorage()
        filename = csvfile.name
        fullpath = os.path.join(settings.MEDIA_ROOT, filename)
        if os.path.exists(fullpath):
            os.remove(fullpath)

        fs.save(csvfile.name, csvfile)
        return render(request, 'FrejunApp/loading.html', {'file': filename})


def csvHandler(request):
    filename = request.GET['file']
    print("got the file"+filename)
    df = pd.read_csv(path+filename)
    patt = re.compile(
        r'\b(mobile\sn.*|contact\sn.*|telephone\sn.*|phone\sn.*)\b', flags=re.I)
    mob = []

    for i in df.columns:  # for every column device-widthi am checking for column name with matching pattern
        if re.search(patt, i):  # pattern matching happening here
            # if column name matched the pattern then i converting that column to list
            mob = df[i].to_list()
    # final_data = df[['Full name', 'Mobile Number']]
    # print(final_data['Mobile Number'].tolist())
    # res = final_data['Mobile Number'].tolist()
    status = []
    #resDict = {}
    strmob = []
    for m in mob:
        status.append(checkStatus(m))
        strmob.append(str(m))
    # status.append(checkStatus(m))
    context = {'mob': strmob, 'status': status}
    # print(mob, status)
    return JsonResponse(context)


def checkStatus(mobile):
    if re.search(r'(^(((\+){1}91)|(91)){1}[1-9]{1}[0-9]{9}$)|(^[1-9]{1}[0-9]{9}$)', str(mobile)):
        res = requests.get(
            'https://kookoo.in/outbound/checkdnd.php?phone_no='+str(mobile)+'')

        xmltext = res.content
        xmltext = xmltext.decode('utf-8')
        root = ET.fromstring(xmltext)
        status = root[1].text
    else:
        status = "Invalid"
    return status
