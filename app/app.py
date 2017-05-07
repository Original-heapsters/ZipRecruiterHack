import os
import json
import time
import pprint
import clarif
import JobScorer
import operator
import ResumeAnalyzer as res
from flask import Flask, render_template, request, g, session, url_for, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
Resume_Analysis_FOLDER = 'static/ResumeJSON/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'docx'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['Resume_Analysis_FOLDER'] = Resume_Analysis_FOLDER

if os.path.isdir(UPLOAD_FOLDER) is False:
    os.makedirs(UPLOAD_FOLDER)

if os.path.isdir(Resume_Analysis_FOLDER) is False:
    os.makedirs(Resume_Analysis_FOLDER)

@app.route('/', methods=['GET','POST'])
def index():
    resScore = '0'
    jobScore = '0'
    interViewScore = '0'
    max_num = 0
    curr_num = 0
    matches = 'matches.txt'
    with open(matches, 'r') as matchFile:
        for line in matchFile.readlines():
            splits = line.split(':')
            curr_num = int(splits[1])
            if curr_num > max_num:
                max_num = curr_num
            splits = line.split(':')
    updateScores('job',max_num)

    lastKnownFile = os.path.join('static/lastKnown.txt')
    with open (lastKnownFile) as f:
        for line in f.readlines():
            splits = line.split(':')
            if 'resume' in splits[0]:
                resScore = splits[1]
            if 'job' in splits[0]:
                jobScore = splits[1]
            if 'interview' in splits[0]:
                interViewScore = splits[1]

    if request.method == 'POST':
        return render_template('index.html', resScore=resScore, jobScore=jobScore,interViewScore=interViewScore)
    else:
        return render_template('index.html', resScore=resScore, jobScore=jobScore,interViewScore=interViewScore)

@app.route('/InterviewPreparedness', methods=['GET','POST'])
def InterviewPreparedness():
    if request.method == 'POST':
        if 'image' in request.files:
            ClearUploadsDir()
            category = request.form['category']
            conceptDictList = []
            files = request.files.getlist('image')
            for fl in files:
                filename = secure_filename(fl.filename)
                fileFullName = filename
                fl.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                jsonTags = clarif.doStuffWithURL(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                conceptDict = clarif.getConceptsWithConfidence(jsonTags)
                conceptDictList.append(conceptDict)
            tags = 'tags.txt'
            open(tags, 'w').close()
            with open(tags, 'w') as tagFile:
                for dic in conceptDictList:
                    tagFile.writelines("\n".join(dic.keys()))

            names = os.listdir(os.path.join(app.static_folder, 'uploads'))
            imgs = []
            for name in names:
                if 'jpg' in name or 'png' in name:
                    img_url = url_for('static', filename=os.path.join('uploads/', name))
                    imgs.append(img_url)

            imageScore = scoreImages()

            updateScores('interview',imageScore)
            return render_template('InterviewPreparedness.html', conceptDictList=conceptDictList, imgs=imgs)
        else:
            return render_template('InterviewPreparedness.html')
    else:
        names = os.listdir(os.path.join(app.static_folder, 'uploads'))
        imgs = []
        for name in names:
            if 'jpg' in name or 'png' in name:
                img_url = url_for('static', filename=os.path.join('uploads/', name))
                imgs.append(img_url)
        return render_template('InterviewPreparedness.html', imgs=imgs)

@app.route('/ResumeRating', methods=['GET','POST'])
def ResumeRating():
    highSentimentThresh = .90
    lowSentimentThresh = .40
    resScore = '0'
    lastKnownFile = os.path.join('static/lastKnown.txt')
    with open (lastKnownFile) as f:
        for line in f.readlines():
            splits = line.split(':')
            if 'resume' in splits[0]:
                resScore = splits[1]
            if 'update' in splits[0]:
                updated = splits[1]
        f.close()

    highSents = {}
    topSkills = []
    basicInfo = []
    skills = []
    sent = {}
    edu = None
    workExp = None
    ResumeAnalysis = os.path.join('static/ResumeJSON/ResumeAnalysis.txt')

    with open(ResumeAnalysis, 'r') as res:
        for line in res.readlines():
            splits = line.split(':')
            if 'missing' in splits[0] and 'missing_points' not in splits[0]:
                basicInfo.append(splits[1])
            if 'sent' in splits[0] and '_Overall' not in splits[0]:
                if float(splits[3]) > highSentimentThresh:
                    highSents[splits[1]] = splits[3]
                elif float(splits[3]) < lowSentimentThresh:
                    sent[splits[1]] = splits[3]

            if 'skill' in splits[0]:
                if len(topSkills) < 5:
                    topSkills.append(splits[1])
            if 'work_experience' in splits[0]:
                message = ''
                count = int(splits[1])
                if count < 0:
                    message = 'You should remove or trim ' + str(abs(count)) + ' work experince entries.'
                else:
                    message = 'You might want to add ' + str(abs(count)) + ' work experience entries.'
                workExp = message
            if 'education_level' in splits[0]:
                if int(splits[1]) <= 0:
                    edu = 'could not parse education'


    #
    # highSents['sentiment'] = '99%'
    # topSkills=['cool', 'alright']
    # basicInfo=['address','firstname']
    # skills=['cool', 'alright']
    # edu='Could not parse'
    # sent['sentiment'] = '-50%'

    if request.method == 'POST':
        return render_template('ResumeRating.html')

    else:
        return render_template('ResumeRating.html',
        updated=updated,
        resScore=resScore,
        highSents=highSents,
        topSkills=topSkills,
        basicInfo=basicInfo,
        skills=skills,
        edu=edu,
        sent=sent,
        workExp=workExp)

@app.route('/UploadResume', methods=['GET','POST'])
def UploadResume():
    JobScorer.scoreResume()
    if request.method == 'POST':
        if 'resume' in request.files:
            file = request.files['resume']
            filename = secure_filename(file.filename)
            fileFullName = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            curdur = os.getcwd()
            print 'trying to use this ' + os.path.join(app.config['UPLOAD_FOLDER']) + fileFullName
            ResumeJson = res.getResumeJSON(os.path.join(app.config['UPLOAD_FOLDER']) + fileFullName)

            with open(ResumeJson) as data_file:
                data = json.load(data_file)

            score = JobScorer.pullComponents()

            return redirect(url_for('ResumeRating'))
        else:
            return render_template('UploadResume.html')

    else:
        return render_template('UploadResume.html')

@app.route('/JobListing', methods=['GET','POST'])
def JobListing():
    jobs = {}
    max_num = 0
    curr_num = 0
    matches = 'matches.txt'
    with open(matches, 'r') as matchFile:
        for line in matchFile.readlines():
            splits = line.split(':')
            curr_num = int(splits[1])
            if curr_num > max_num:
                max_num = curr_num
            splits = line.split(':')
            jobs[splits[0]] = splits[1]
    updateScores('job',max_num)
    #jobs = sorted(jobs, key=jobs.__getitem__, reverse=True)
    sorted_jobs = dict(sorted(jobs.items(), key=operator.itemgetter(1), reverse=True))
    return render_template('JobListing.html',jobs=sorted_jobs)

@app.route('/Settings', methods=['GET'])
def Settings():
    return render_template('Settings.html')

def ClearUploadsDir():
    folder = 'static/uploads'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def scoreImages():
    score = 0
    good = 'goodAttributes.txt'
    bad = 'badAttributes.txt'
    tags = 'tags.txt'
    goodAttr = []
    with open(good, 'r') as goodFile:
        for line in goodFile:
            goodAttr.append(line)

    badAttr = []
    with open(bad, 'r') as badFile:
        for line in badFile:
            badAttr.append(line)

    with open(tags, 'r') as tagFile:
        for line in tagFile.readlines():
            print 'comparing ' + line.lower() + ' with ' + good + ' and ' + bad
            if line.lower() in goodAttr:
                score += 1
            if line.lower() in badAttr:
                score -= 1
    return score

def updateScores(keyVar, value):
    newLines = []
    print (time.strftime("%I:%M:%S"))
    with open('static/lastKnown.txt', 'r') as f:
        for line in  f.readlines():
            if keyVar in line:
                spl = line.split(':')
                k = spl[0]
                newLines.append(k + ':' + str(value))
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(debug=True);
