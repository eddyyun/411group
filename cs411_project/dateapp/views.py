from django.shortcuts import render
from dateapp.models import Date
import requests
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import json
import cv2
import os
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
import io
import time
import datetime
from django.contrib.auth.models import User

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
from django.contrib.auth import logout


from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import shutil




def index(request):
    movie_genre_id = None
    image_available = True
    emotion=None
    json_data=[]
    movie_1=None
    movie_image_1=None
    movie_2=None
    movie_image_2=None
    movie_3=None
    movie_image_3=None
    backdrop_path_1=None
    backdrop_path_2=None
    backdrop_path_3=None
    emotion_notavailable=False
    path_1 = 'dateapp/static/images'
    file = os.path.join(path_1, 'happy_pic.png')
    current_username=request.user
    current_user_id=request.user.id
    if os.path.isfile(file)==False:
        image_available=False
    if 'take_photo' in request.POST:
        time.sleep(2)
        # Camera Capture
        camera_port = 0
        ramp_frames = 30
        camera = cv2.VideoCapture(camera_port)
        def get_image():
            retval, im = camera.read()
            return im

        for i in range(ramp_frames):
            temp = get_image()
        print("Taking image...")
        # Take the actual image we want to keep
        camera_capture = get_image()
        path_1='dateapp/static/images'
        file=os.path.join(path_1 , 'happy_pic.png')
        cv2.imwrite(file, camera_capture)
        del (camera)

    ## File upload case 
    elif request.method=='POST':
        try:
            file = os.path.join(path_1, 'happy_pic.png')
            if os.path.isfile(file):
                os.remove(file)
            uploaded_file = request.FILES['document']
            path = default_storage.save('happy_pic.png', ContentFile(uploaded_file.read()))
            shutil.move(path, path_1)
            return HttpResponseRedirect('/')
        except:
            return HttpResponseRedirect('/')

    ## if file is avaible send image to Google Vision API
    if os.path.isfile(file)==True:
        image_available=True
        client = vision.ImageAnnotatorClient()
        path_2='dateapp/static/images'
        path=os.path.join(path_2 , 'happy_pic.png')

        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.types.Image(content=content)

        response = client.face_detection(image=image)
        faces = response.face_annotations

        # Names of likelihood from google.cloud.vision.enums
        likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                           'LIKELY', 'VERY_LIKELY')
        print('Faces:' + path)
        emoDict = {}
        for face in faces:
            anger = ('anger: {}'.format(likelihood_name[face.anger_likelihood]))
            angerList = anger.split(':')
            emoDict[angerList[0]] = angerList[1]
            joy = ('joy: {}'.format(likelihood_name[face.joy_likelihood]))
            joyList = joy.split(':')
            emoDict[joyList[0]] = joyList[1]
            sur = ('surprise: {}'.format(likelihood_name[face.surprise_likelihood]))
            surList = sur.split(':')
            emoDict[surList[0]] = surList[1]
            sor = ('sorrow: {}'.format(likelihood_name[face.sorrow_likelihood]))
            sorList = sor.split(':')
            emoDict[sorList[0]] = sorList[1]
        
        newDict = dict()
        for x, y in emoDict.items():
            if (len(newDict) == 0 and y == ' VERY_LIKELY'):
                newDict[x] = y
        for x, y in emoDict.items():
            if (len(newDict) == 0 and y == ' LIKELY'):
                newDict[x] = y
        for x, y in emoDict.items():
            if (len(newDict) == 0 and y == ' POSSIBLE'):
                newDict[x] = y
        for x, y in emoDict.items():
            if (len(newDict) == 0):
                newDict['None'] = True

        if (len(emoDict)==0):
            emotion_notavailable = True
 
        genreID = 0
        if "anger" in newDict:
            if (newDict['anger'] == ' VERY_LIKELY'):
                genreID = 18 ##Drama
            if (newDict['anger'] == ' LIKELY' or ' POSSIBLE'):
                genreID = 10752 ##War
        if "joy" in newDict:
            if (newDict['joy'] == ' VERY_LIKELY'):
                genreID = 35 #comedy
            if (newDict['joy'] == ' LIKELY' or ' POSSIBLE'):
                genreID = 35 #Comedy
        if "surprise" in newDict:
            if (newDict['surprise'] == ' VERY_LIKELY'):
                genreID = 9648 ## mystery
            if (newDict['surprise'] == ' LIKELY' or ' POSSIBLE'):
                genreID = 53 ##Thriller
        if "sorrow" in newDict:
            if (newDict['sorrow'] == ' VERY_LIKELY'):
                genreID = 27 ##Horror
            if (newDict['sorrow'] == ' LIKELY' or ' POSSIBLE'):
                genreID = 10749  ##Romance
        if "None" in newDict:
            emotion_notavailable= True

        print("genreID is ", genreID)

  


        url = "https://api.themoviedb.org/3/discover/movie"

        querystring = {"api_key": settings.GOOGLE_API_KEY, "language": "en-US", "sort_by": "popularity.desc",
                       "include_adult": "false", "include_video": "false", "page": "1",
                       "primary_release_date.gte": "2016-01-01", "primary_release_date.lte": "2018-12-31",
                       "vote_average.gte": "6", "with_genres": genreID}

        payload = "undefined="
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache",
            'Postman-Token': "fc55909f-7faa-4e5d-ac20-ecccdcf60ab2"
        }

        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

        json_data = json.loads(response.text)

        if emotion_notavailable==False:
            emotion = (newDict.popitem()[0]).capitalize()
            todays_date = datetime.date.today()
            movie_1 = json_data['results'][0]['title']
            movie_2 = json_data['results'][1]['title']
            movie_3 = json_data['results'][2]['title']
            backdrop_path_1 = json_data['results'][0]['poster_path']
            backdrop_path_2 = json_data['results'][1]['poster_path']
            backdrop_path_3 = json_data['results'][2]['poster_path']
            movie_image_1 = 'https://image.tmdb.org/t/p/original' + backdrop_path_1
            movie_image_2 = 'https://image.tmdb.org/t/p/original' + backdrop_path_2
            movie_image_3 = 'https://image.tmdb.org/t/p/original' + backdrop_path_3
            date=Date.objects.create(user_id=current_user_id,date=todays_date,emotion=emotion,movie_suggestion_1=movie_1,movie_suggestion_2=movie_2,movie_suggestion_3=movie_3,movie_path_1= backdrop_path_1,movie_path_2= backdrop_path_2,movie_path_3= backdrop_path_3)
            date.save()


        else:
            movie_1 = None
            movie_image_1 = None
            movie_2 = None
            movie_image_2 = None
            movie_3 = None
            movie_image_3 = None
            backdrop_path_1 = None
            backdrop_path_2 = None
            backdrop_path_3 = None
            image_available=True

    return render(request,'index.html',{'res':json_data,'movie_genre_id':movie_genre_id,'movie_1':movie_1,'movie_2':movie_2,'movie_3':movie_3,'image_available':image_available,'emotion':emotion,'backdrop_1':movie_image_1,'backdrop_2':movie_image_2,'backdrop_3':movie_image_3,'current_username':current_username,'emotion_notavailable':emotion_notavailable})


def history(request):
    path_1 = 'dateapp/static/images'
    current_username=request.user
    current_user_id=request.user.id
    user_history_list=list()
    user_dates=list()
    user_emotion_list=list()
    user_movie_1_list=list()
    user_movie_2_list=list()
    user_movie_3_list=list()
    history_available=False
    file = os.path.join(path_1, 'happy_pic.png')
    if os.path.isfile(file):
        os.remove(file)
    if Date.objects.filter(user_id=current_user_id).count()>0:
        history_available=True
        current_date_count = Date.objects.filter(user_id=current_user_id).count()
        for i in range(0, current_date_count):
            current_date= Date.objects.filter(user_id=current_user_id).order_by("-id")[i].date
            current_emotion=Date.objects.filter(user_id=current_user_id).order_by("-id")[i].emotion
            current_movie_1=Date.objects.filter(user_id=current_user_id).order_by("-id")[i].movie_suggestion_1
            current_movie_2=Date.objects.filter(user_id=current_user_id).order_by("-id")[i].movie_suggestion_2
            current_movie_3=Date.objects.filter(user_id=current_user_id).order_by("-id")[i].movie_suggestion_3
            user_dates.append(current_date)
            user_emotion_list.append(current_emotion)
            user_movie_1_list.append(current_movie_1)
            user_movie_2_list.append(current_movie_2)
            user_movie_3_list.append(current_movie_3)

        user_history_list=zip(user_dates,user_emotion_list,user_movie_1_list,user_movie_2_list,user_movie_3_list)


    return render(request,'history.html',{'current_username':current_username,'history_available':history_available,'user_history_list':user_history_list})


