import os
import time

totalResumeScore = 0
sentimentThreshold = .50
minSkills = 2
maxSkills = 10

def pullComponents():
    global totalResumeScore
    home = os.getcwd()
    inFile = home + '/static/ResumeJSON/ResumeAnalysis.txt'

    missingComponents = []
    missingScore = 0
    sentiments = {}
    overallSentiment = {}
    skills = []
    workExpCount = 0
    eduLevel=0

    with open (inFile, 'r') as inFile:
        for line in inFile.readlines():
            splitLine = line.split(':')
            if 'missing' == splitLine[0]:
                missingComponents.append(splitLine[1])
            elif 'missing_points' == splitLine[0]:
                missingScore = splitLine[1]
                totalResumeScore -= int(missingScore)
            elif 'sent_Original_Text' == splitLine[0]:
                text = splitLine[1]
                score = splitLine[3]
                if float(score) < sentimentThreshold:
                    totalResumeScore -= 1
                else:
                    totalResumeScore += 1
                sentiments[text] = score
            elif 'sent_Overall_Score' == splitLine[0]:
                sent = splitLine[3]
                score = splitLine[1]
                if float(score) < sentimentThreshold:
                    totalResumeScore -= 1
                else:
                    totalResumeScore += 1
                overallSentiment[sent] = score
            elif 'skill' == splitLine[0]:
                skills.append(splitLine[1])
                totalResumeScore += 1
            elif 'work_experience' == splitLine[0]:
                workExpCount = splitLine[1]
                totalResumeScore -= abs(int(workExpCount))
            elif 'education_level' == splitLine[0]:
                eduLevel = splitLine[1]
                totalResumeScore += int(eduLevel)

    rec_edits = 50

    if missingScore > 0:
        rec_edits -= 1.6 * float(missingScore)
    print rec_edits

    totalSubtraction = 10
    trackedSubtraction = 0
    for sent in sentiments:
        if float(sentiments[sent]) < sentimentThreshold:
            print "ding for sentiment of " + sent + " that scored " + sentiments[sent]
            trackedSubtraction += 1
        if trackedSubtraction == totalSubtraction:
            break
    rec_edits -= trackedSubtraction
    print rec_edits

    if minSkills > len(skills):
        print 'ding for min skills'
        rec_edits -= 5


    if len(skills) > maxSkills:
        print "ding for max skills"

        rec_edits -= 5
    print rec_edits

    if int(workExpCount) != 0:
        print "ding for work experince count of " + workExpCount
        rec_edits -= 10
    print rec_edits

    if eduLevel == 0:
        print "ding for education"
        rec_edits -= 10

    print rec_edits

    rec_pct = (float(rec_edits)/50.0) * 100


    print "You scored " + str(totalResumeScore) + " Which is " + str(rec_pct) + "%"
    updateScores('resume',str(rec_pct))
    return totalResumeScore


def updateScores(keyVar, value):
    newLines = []
    print (time.strftime("%I:%M:%S"))
    with open('static/lastKnown.txt', 'r') as f:
        for line in  f.readlines():
            if keyVar in line:
                spl = line.split(':')
                k = spl[0]
                newLines.append(k + ':' + value)
            elif 'update' in line:
                print '.'
            else:
                newLines.append(line)
        f.close()
    open('static/lastKnown.txt', 'w').close()
    with open('static/lastKnown.txt', 'w') as f:
        f.write('update:' + time.strftime("%d/%m/%Y_") + time.strftime("%I-%M-%S") + '\n')
        for line in newLines:
            f.write(line.strip() + '\n')
        f.close()
    return

def scoreResume():
    return
