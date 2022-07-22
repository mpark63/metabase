#########################################################################
# LOGIN and DEFINE SECTION
#########################################################################
# Run _LOGIN.py and copy the token string here:
token = 'df5be32f-7822-4204-b6a2-443084c33502'    

# Course name to course ID 
# 14 for EEI SU21, 15 for BMEI 12wk, 16 for BMEI T1, 17 for BMEI T2 (all SU21)
courses = {
    'Explore Engineering Innovation Online':"(14)",
    # 'Biomedical Engineering Innovation':"(15,16,17)"
    }

#%% HEADER AND FUNCTIONS ######################################################
import pandas as pd
import matplotlib.pyplot as plt
import requests
import os
from pathlib import Path
import re

endpoint = 'https://metabase.di.inciter.io'  
database = 14   # Database JHU-WSE

# Set numerical values for Likert answers
vSA = 5     # value for "strongly agree" (SA)
vA  = 4
vN  = 3     # value for neutral (N)
vD  = 2
vSD = 1     # value for "strongly disagree" (SD)

#%% Function queryForCount =======================================================
def queryForCount(qstring):
    print(qstring)
    query= {"database": database, "type": "native", "native": {"query": qstring}}
    res = requests.post(endpoint+'/api/dataset',
              headers = {'Content-Type': 'application/json',
                        'X-Metabase-Session': token},json=query)

    # returns {'data': {'rows': [[COUNT]]}, ...} 
    c = res.json()['data']['rows'][0]
    c = c[0]

    return c

# Query for post-course response by sex 
for course in courses:
    #%% DEMOGRAPHICS ==========================================================
    dictSex = {'col':'sex',
               'data': {'M':'Male','F':'Female'}
            }

    # Query data from the database for this section only
    table = 'v_student_survey'
    courseIDs = courses[course]
    survey = 'Post-Course Student'
    section = 'EN.500.109.01'

    respDict = {
        'Strongly agree':'Strongly agree',
        'Agree':'Agree',
        'Neither agree nor disagree':'Neutral',
        'Disagree':'Disagree',
        'Strongly disagree':'Strongly disagree',
        'Total': 'Total'
        }
    colList = list(respDict.values())
    dfDem = pd.DataFrame(None,index=list(dictSex['data'].values()),columns=colList)

    qText = 'would_recommend_course_to_friend_interested_in_0et0_eng'
    for r in dictSex['data']: 
        dfDem['Total'][dictSex['data'][r]] = 0
    for resp in respDict:
        for r in dictSex['data']:
            if resp == 'Total': 
                continue 
            qstring = (
                "SELECT COUNT(v_student_survey.response)"
            + " FROM " + table
            + " INNER JOIN v_student_demographics ON v_student_survey.email_id=v_student_demographics.email_id"
            + " WHERE v_student_survey.course_id IN " + courses[course]
            + " AND v_student_survey.details = '" + survey + "'"
            + " AND v_student_survey.question = '" + qText + "'"
            + " AND v_student_survey.response = '" + resp + "'"
            + " AND v_student_demographics." + dictSex['col'] + " = '" + r + "'"
            )

            nResp = queryForCount(qstring)
            #dfDem['Neutral']['Male']
            dfDem[respDict[resp]][dictSex['data'][r]] = nResp
            dfDem['Total'][dictSex['data'][r]] += nResp

    print(qText)
    print(dfDem)