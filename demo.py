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

Qs = {
        'would_recommend_course_to_friend_interested_in_0et0_eng' 
            : 'Would recommend course to friend interested in engineering', 
        # 'an_engineering_degree_will_guarantee_me_a_job_when_i_graduate' :
        #     'An engineering_degree will guarantee me a job when I graduate',
        # 'engineers_are_well_paid':
        #     'Engineers are well paid',
        # 'engineering_plays_an_important_role_in_solving_societys_problems':
        #     'Engineering plays an important role in solving societys problems',
        # 'i_like_to_solve_problems_and/or_figure_out_how_things_work':
        #     'I like to solve problems and/or figure out how things work'
    }

respDict = {
            'Strongly agree':'Strongly agree',
            'Agree':'Agree',
            'Neither agree nor disagree':'Neutral',
            'Disagree':'Disagree',
            'Strongly disagree':'Strongly disagree',
            'Total': 'Total'
            }

# Query for post-course response by sex 
for course in courses:
    dataframes = []
    for qText in Qs: 
        #%% DEMOGRAPHICS ==========================================================
        dictSex = {'col':'sex',
            'data': {'M':'Male','F':'Female'}
            }

        # Query data from the database for this section only
        table = 'v_student_survey'
        courseIDs = courses[course]
        survey = 'Post-Course Student'
        section = 'EN.500.109.01'

        colList = list(respDict.values())
        rowList = list(dictSex['data'].values())
        dfDem = pd.DataFrame(None,index=rowList,columns=colList)

        dfDem.fillna(0, inplace=True)

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
                dfDem[respDict[resp]][dictSex['data'][r]] = nResp
                dfDem['Total'][dictSex['data'][r]] += nResp
            
        dfPerc = pd.DataFrame(None,index=list(rowList),columns=colList)
        for resp in respDict:
            for r in dictSex['data']:
                if resp == 'Total': 
                    continue 
                count = dfDem[respDict[resp]][dictSex['data'][r]] 
                total = dfDem['Total'][dictSex['data'][r]] 
                dfDem[respDict[resp]][dictSex['data'][r]] = count / total 
        dfPerc = dfDem.drop('Total', axis=1) # don't show total 
        
        dataframes.append(dfPerc)
    
    print(dataframes)
    print(Qs[qText])

    df = dfPerc
    # Plot data
    #   Pre-formatting
    font = {'weight':'normal', 'size':10}
    plt.rc('font', **font)
    fwidth = 6.5
    fheight = 5
    #   Plot and modify
    df = df.sort_values('Strongly agree', ascending=True)
    ax = df.plot.barh(stacked=True, figsize=(fwidth, fheight))
    ax.legend(loc='upper center', bbox_to_anchor=(0.2, -0.08),
                fancybox=False, shadow=False, ncol=5)
    ax.spines[:].set_visible(False)
    ax.yaxis.set_ticks_position('none')
    ax.set_ylabel("")

    #   Save
    fname = course+'_general'
    plt.savefig('tex/fig/'+fname+'.png', bbox_inches='tight', dpi=300)
    plt.show()