import os
import json
import xmlrpclib
import SentimentAnalyzer as sentiment
from xml.dom.minidom import parseString

allComponents = []
allComponents.append('name')
allComponents.append('firstname')
allComponents.append('surname')
allComponents.append('email')
allComponents.append('address')
allComponents.append('phone')

reccomended_WorkExp = 4

eduLevels = {}

eduLevels['hs'] = 1
eduLevels['college'] = 2
eduLevels['masters'] = 3
eduLevels['doctorate'] = 4

def getResumeJSON(inputPath):

    home = os.getcwd()
    outfile = home + '/static/ResumeJSON/out.json'
    command = 'sh ~/git/ResumeParser/ResumeTransducer/CreateJSON.sh ' + inputPath + ' ' + outfile
    os.system(command)

    with open(outfile) as data_file:
        data = json.load(data_file)

    missing, contribution = getMissingComponents(data)
    countToModify = getWorkExpCount(data)
    allSentiments = getSentiments(data)
    allSkills = getKeySkills(data)
    eduLevel = getEducationLevel(data)

    writeAnalysis(missingComps=missing,contribution=contribution,workExp=countToModify, sentiments=allSentiments, skills=allSkills,education=eduLevel)

    return outfile

def getMissingComponents(jsonInput):
    print jsonInput
    missingComponents = []
    contribution = 0
    rawJson = str(jsonInput).lower()
    for component in allComponents:
        if component in rawJson:
            print 'Found ' + component
        else:
            print 'Could not find ' + component
            missingComponents.append(component)
            contribution -= 1

    return (missingComponents, contribution)



def getKeySkills(jsonInput):
    allSkills = []

    if 'skills' in jsonInput:
        for item in jsonInput['skills']:
            for k,v in item.iteritems():
                skillList = v.strip()
                for skill in skillList.split(','):
                    allSkills.append(skill)
                    print 'SKILL: ' + skill

    return allSkills

def getSentiments(jsonInput):
    allSentences = []
    alltext = ''
    for item in jsonInput['work_experience']:
        for entry in item:
            if 'text' in entry:
                allSentences.append(item[entry].encode('utf-8').split('.'))
                alltext += item[entry].encode('utf-8')
    sentiment.getSentiments(alltext)
    sent = sentiment.sentiments
    return sent

def getWorkExpCount(jsonInput):
    workExperienceCount = len(jsonInput['work_experience'])
    difference = reccomended_WorkExp - workExperienceCount
    print difference

    if difference < 0:
        print 'too many entries'
    else:
        print 'too few entries'
    return difference

def typoCheck(jsonInput):
    return

def getEducationLevel(jsonInput):
    level = 0
    for item in jsonInput['education_and_training']:
        for k,v in item.iteritems():
            if (' hs ' in v.lower() or 'highscool' in v.lower()) and level <= 0:
                level = eduLevels['hs']
            if (' bs ' in v.lower() or 'bachelor' in v.lower()) and level <= 1:
                level = eduLevels['college']
            if (' ms ' in v.lower() or 'master' in v.lower()) and level <= 2:
                level = eduLevels['masters']
            if (' phd ' in v.lower() or 'doctorate' in v.lower()) and level <= 3:
                level = eduLevels['doctorate']

    return level

def getLicenses():
    return

def writeAnalysis(missingComps, contribution, workExp, sentiments, skills,education):
    home = os.getcwd()
    home += '/static/ResumeJSON/'
    outFile = home + 'ResumeAnalysis.txt'

    with open (outFile, 'w') as write:
        for missing in missingComps:
            write.write('missing:' + missing + '\n')
        write.write('missing_points:' + str(contribution) + '\n')

        write.write(sentiments + '\n')
        # for sentiment in sentiments:
        #     write.write('sentiment:' + sentiment + '\n')

        for skill in skills:
            write.write('skill:' + skill.strip() + '\n')


        write.write('work_experience:' + str(workExp) + '\n')
        write.write('education_level:'+ str(education) + '\n')

    return
