import os
import json
import pprint
import clarif
import JobScorer
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
    lastKnownFile = os.path.join('static/lastKnown.txt')
    print lastKnownFile
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
            return render_template('InterviewPreparedness.html', conceptDictList=conceptDictList)
        else:
            return render_template('InterviewPreparedness.html')
    else:
        return render_template('InterviewPreparedness.html')

@app.route('/ResumeRating', methods=['GET','POST'])
def ResumeRating():
    if request.method == 'POST':
        return render_template('ResumeRating.html', args=args)

    else:
        return render_template('ResumeRating.html')

@app.route('/UploadResume', methods=['GET','POST'])
def UploadResume():
    if request.method == 'POST':
        if 'resume' in request.files:
            file = request.files['resume']
            filename = secure_filename(file.filename)
            fileFullName = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            curdur = os.getcwd()
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
    return render_template('JobListing.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(debug=True);
