import os
import json
import pprint
import clarif
import JobScorer
import ResumeAnalyzer as res
from flask import Flask, render_template, request, g, session, url_for, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        args = []
        args.append(request.form['firstname'])
        args.append(request.form['lastname'])
        return render_template('index.html', args=args)
    else:
        return render_template('index.html')

@app.route('/InterviewPreparedness', methods=['GET','POST'])
def InterviewPreparedness():
    if request.method == 'POST':
        args = []
        args.append(request.form['firstname'])
        args.append(request.form['lastname'])

        if 'image' in request.files:
            file = request.files['image']
            filename = secure_filename(file.filename)
            fileFullName = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            curdur = os.getcwd()
            jsonTags = clarif.doStuffWithURL(curdur + '/static/uploads/' + fileFullName)
            conceptDict = clarif.getConceptsWithConfidence(jsonTags)
            return render_template('InterviewPreparedness.html', conceptDict=conceptDict, args=args)
        else:
            return render_template('InterviewPreparedness.html', args=args)
    else:
        return render_template('InterviewPreparedness.html')

@app.route('/ResumeRating', methods=['GET','POST'])
def ResumeRating():
    if request.method == 'POST':
        args = []
        args.append(request.form['firstname'])
        args.append(request.form['lastname'])
        if 'resume' in request.files:
            file = request.files['resume']
            filename = secure_filename(file.filename)
            fileFullName = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            curdur = os.getcwd()
            ResumeJson = res.getResumeJSON(curdur + '/static/uploads/' + fileFullName)

            with open(ResumeJson) as data_file:
                data = json.load(data_file)

            #print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            #pprint(data)

            score = JobScorer.pullComponents()

            return render_template('ResumeRating.html', ResumeJson=ResumeJson, args=args)
        else:
            return render_template('ResumeRating.html', args=args)

    else:
        return render_template('ResumeRating.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(debug=True);
