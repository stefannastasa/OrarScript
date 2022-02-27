from __future__ import print_function
from math import floor

import time
import datetime
import os.path
from venv import create
from orare import get_orar_grupa
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def insert_calendar(to_add):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    calendar = {
        'summary': 'OrarFacultate'
    }
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    try:
        service = build("calendar",version='v3', credentials=creds)
        
        created_calendar = service.calendars().insert(body=calendar).execute()
        print("Calendar creat: {}".format(created_calendar['id']))
        
        
        for i,event in enumerate(to_add):
            service.events().insert(calendarId=created_calendar['id'], body=event).execute()
            print("{}% done.".format(floor(i/len(to_add)*100)))
    
    except HttpError as error:
        print("An error has occured: {}".format(error))
                
    
    

def createEvents(to_add, sgrupa, exceptii):
    
    weekdays = {"Luni":0, 'Marti':1, 'Miercuri':2, 'Joi':3, 'Vineri':4}
    answer = []
    for event in to_add:
        ok = True
        for ex in exceptii:
            if ex in event['Disciplina'].lower():
                ok = False     
                
        if (len(event['Formatia'].split('/')) == 1 or event['Formatia'].split('/')[1] == sgrupa) and ok:     
            pos = datetime.datetime(2022, 2,21)
            
            pos += datetime.timedelta(days = weekdays[event['Ziua']] )
            
            times = event['Orele']
            times = times.split('-')
            startT = datetime.datetime(pos.year,pos.month, pos.day,int(times[0].split('.')[0]),int(times[0].split('.')[1]),0,0,tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
            endT = datetime.datetime(pos.year,pos.month, pos.day,int(times[1].split('.')[0]),int(times[1].split('.')[1]),0,0 ,tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
            endT -= datetime.timedelta(minutes=20)
            
            freq = 'WEEKLY'
            count = 1
            color = 5 if event['Tipul']=='Laborator' else (10 if event['Tipul']=='Seminar' else 11)
            if event['Frecventa'].lower() == 'sapt. 1' or event['Frecventa'].lower() == 'sapt. 2':
                if event['Frecventa'] == 'sapt. 2':
                    startT += datetime.timedelta(days=7)
                    endT += datetime.timedelta(days=7)
                
                count = 2
            for i in range(12//count):
                activitate = {
                    'summary': event['Disciplina'],
                    'location': event['Sala'],
                    'start':{
                        'dateTime': startT.isoformat(sep='T'),
                        'timeZone': 'Europe/Bucharest'
                    },
                    'end':{
                        'dateTime': endT.isoformat(sep='T'),
                        'timeZone': 'Europe/Bucharest'
                    },
                    'colorId': color
                    
                }
                answer.append(activitate)
                startT += datetime.timedelta(days=count*7)
                endT += datetime.timedelta(days=count*7)
    
    return answer


def main():
    grupa = input("Introdu grupa/semigrupa: ")
    exceptii = input("Introdu materiile exceptie cu virgula intre: ")
    print("Se descarca orarul...")
    to_add = get_orar_grupa(grupa.split('/')[0])
    
    exceptii = exceptii.split(',')
    exceptii = list(a.lower() for a in exceptii)
    to_add = createEvents(to_add,grupa.split('/')[1], exceptii)
    
    insert_calendar(to_add)
    
    
    

if __name__ == '__main__':
    main()