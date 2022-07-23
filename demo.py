#########################################################################
# LOGIN and DEFINE SECTION
#########################################################################
# Run _LOGIN.py and copy the token string here:

# Course name to course ID 
# 14 for EEI SU21, 15 for BMEI 12wk, 16 for BMEI T1, 17 for BMEI T2 (all SU21)
courses = {
    'Explore Engineering Innovation Online':"(14)",
    # 'Biomedical Engineering Innovation':"(15,16,17)"
    }

#%% HEADER AND FUNCTIONS ######################################################
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import os
from pathlib import Path
import re
from secret import token 
pd.options.mode.chained_assignment = None  # default='warn'

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
    # print(qstring)
    query= {"database": database, "type": "native", "native": {"query": qstring}}
    res = requests.post(endpoint+'/api/dataset',
              headers = {'Content-Type': 'application/json',
                        'X-Metabase-Session': token},json=query)

    # returns {'data': {'rows': [[COUNT]]}, ...} 
    c = res.json()['data']['rows'][0]
    c = c[0]

    return c

#%% QUESTIONS AND RESPONSES ==========================================================
Qs = {
        'i_intend_to_study_0et0_engineering_in_college' 
            : 'I intend to study engineering in college', 
        'i_feel_prepared_to_study_0et0_engineering_in_college':
            'I feel prepared to study engineering in college',
    }

respDict = {
            'Strongly agree':'Strongly agree',
            'Agree':'Agree',
            'Neither agree nor disagree':'Neutral',
            'Disagree':'Disagree',
            'Strongly disagree':'Strongly disagree',
            'Total': 'Total'
            }

respValue = {
    'Strongly agree': 5,
    'Agree': 4,
    'Neutral': 3,
    'Disagree': 2,
    'Strongly disagree': 1,
}

#%% DEMOGRAPHICS ==========================================================
dictSex = {'col':'sex',
            'data': {'M':'Male','F':'Female'}
            }
dictRace = {'col':'race',
            'data': {
                'American Indian or Alaska Native':'American Indian or Alaska Native',
                'Asian':'Asian',
                'Black or African American':'Black or African American',
                'Native Hawaiian or Other Pacific':'Native Hawaiian or Other Pacific',
                'White':'White'}
            }
dictEthn= {'col':'hispanic',
            'data': {'Y':'Hispanic','N':'Not Hispanic'}
            }
dictGrade = {'col':'current_grade',
            'data': {
                '9':'9th grade',
                '10':'10th grade',
                '11':'11th grade',
                '12':'12th grade'}
            }
demographics = [dictSex, dictRace, dictEthn, dictGrade]

# Query from raw data table 
table = 'v_student_survey'

for course in courses:
    # Build LaTeX report header
    latexFileName = "tex/"+course.replace(' ', '_')+".tex"
    f = open(latexFileName, "w")
    f.write("\documentclass{article}\n")
    f.write(r"\usepackage[hidelinks]{hyperref}" + "\n")
    f.write(r"\usepackage[top=1in, bottom=1in, left=1in, right=1in, "+
            "marginparsep=0.15in]{geometry}")
    f.write(r"\usepackage{booktabs}" + "\n")
    f.write(r"\usepackage{graphicx}" + "\n")
    f.write(r"\usepackage{caption}" + "\n")
    f.write(r"\title{" + course + r" Summer 2021}")
    f.write(r"\date{}")
    #f.write(r"\author{"+teachers[section]+"}")
    f.write(r"\begin{document} \maketitle"+"\n")
    f.write(r"\setcounter{tocdepth}{1} \tableofcontents"+"\n")
    f.write("\n" + r"\noindent ")
    f.write(r"\pagebreak"+"\n")

    # for each question 
    for q in Qs: 
        qText = Qs[q]
        f.write(r"\section{"+qText+"}"+"\n")
        print("Query for question: " + qText)
    
        for demo in demographics: 
            print("\tdemographic: " + demo['col'].replace('_', ' '))
            colList = list(respDict.values())
            rowList = []    
            for var in demo['data']:
                for survey in ['Pre-Course Student', 'Post-Course Student']: 
                    rowList.append(survey + " - " + demo['data'][var])
            # initialize raw values 
            dfDem = pd.DataFrame(None,index=rowList,columns=colList)
            dfDem.fillna(0, inplace=True)
            # initialize percentage values 
            dfPerc = pd.DataFrame(None,index=rowList,columns=colList)
            dfPerc.drop('Total', axis=1) # don't show total 
            dfPerc.fillna(0, inplace=True)

            for survey in ['Pre-Course Student', 'Post-Course Student']: 
                for var in demo['data']:
                    total = 0
                    for resp in respDict:
                        if resp == 'Total': 
                            continue 
                        
                        qstring = (
                            "SELECT COUNT(v_student_survey.response)"
                        + " FROM " + table
                        + " INNER JOIN v_student_demographics ON v_student_survey.email_id=v_student_demographics.email_id"
                        + " WHERE v_student_survey.course_id IN " + courses[course]
                        + " AND v_student_survey.details = '" + survey + "'"
                        + " AND v_student_survey.question = '" + q + "'"
                        + " AND v_student_survey.response = '" + resp + "'"
                        + " AND v_student_demographics." + demo['col'] + " = '" + var + "'"
                        )
                        nResp = queryForCount(qstring)
                        dfDem[respDict[resp]][survey + ' - ' + demo['data'][var]] = nResp
                        total += nResp
                    # update dfPerc based on dfDem
                    for resp in respDict:
                        count = dfDem[respDict[resp]][survey + ' - ' + demo['data'][var]]
                        dfPerc[respDict[resp]][survey + ' - ' + demo['data'][var]] = count / total 
            
            # Plot data
            #   Pre-formatting
            font = {'weight':'normal', 'size':10}
            plt.rc('font', **font)
            fwidth = 6.5
            fheight = 4.5
            #   Plot and modify
            ax = dfPerc.plot.barh(stacked=True, figsize=(fwidth, fheight))
            ax.legend(loc='upper center', bbox_to_anchor=(0.2, -0.08),
                        fancybox=False, shadow=False, ncol=5)
            ax.spines[:].set_visible(False)
            ax.yaxis.set_ticks_position('none')
            ax.set_ylabel("")
            
            #   Save
            fname = q+'___'+demo['col'].replace('_', ' ')
            plt.savefig('tex/fig/'+fname+'.png', bbox_inches='tight', dpi=300)
            f.write(r"\subsection{"+demo['col'].replace('_', ' ')+"}"+"\n")
            f.write(r"\includegraphics[width="+str(fwidth)+"in]{fig/"+fname+r".png}\\"+"\n")

            # Table of statistics 
            colList = ['Mean', 'Agrees']
            dfStats = pd.DataFrame(None,index=rowList,columns=colList)
            for row in rowList: 
                sum = 0
                total = 0
                # Calculate mean 
                for col in list(respDict.values()): 
                    if col == 'Total': 
                        continue; 
                    sum += dfDem[col][row] * respValue[col]
                    total += dfDem[col][row]
                dfStats['Mean'][row] = str(round((sum / total), 2))
                # Calculate agrees 
                agrees = dfDem['Strongly agree'][row] + dfDem['Agree'][row]
                dfStats['Agrees'][row] = agrees
            
            f.write(dfStats.style.to_latex(position='!h',column_format='|r|cc|'))

    #%% WRAP-UP REPORT ========================================================
    f.write("\end{document}")
    f.close()
    os.system("pdflatex -output-directory=tex -interaction=batchmode "+latexFileName)
    print(latexFileName + " has been created!")