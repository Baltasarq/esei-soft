
from google.appengine.api import users

import time
from flask import render_template, flash, redirect, request
from flask_babel import _
import flask
from google.appengine.ext import ndb
from main import app
from models.ndbModels import Request, Software, Subject, User, Teacher, SubjectSoftware


@app.route('/')
@app.route('/index')
def login():
    user = users.get_current_user()
    if user:
        try:

            user_key = user.user_id()
            usersDb = User.query(User.user_key == user_key)
            if usersDb.count() == 0:
                # Store new User
                username = user.nickname()
                new_user = User(user_key=user_key, name=username, is_admin=0)
                new_user.put()
                time.sleep(1)
            return render_template("login.html", user=user.nickname().partition("@")[0],
                                  # is_admin=user.__getattribute__("is_admin"),
                                   user_logout=users.create_logout_url("/"))
        except Exception as e:
            print(e.message)
    else:
        return render_template("login.html", user_login=users.create_login_url("/"))


@app.route('/subjects')
def showSubjects():
    user = users.get_current_user()
    if user:
        try:
            subjects = Subject.query().order(Subject.name)
            return render_template("subjects.html", user_logout=users.create_logout_url("/"),
                                   subjects=subjects)
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/addSubject', methods=['GET', 'POST'])
def addSubject():
    user = users.get_current_user()
    if user:
        if flask.request.method == 'POST':
            name = flask.request.form.get("name")
            year = int(flask.request.form.get("year"))
            quarter = int(flask.request.form.get("quarter"))

            subject = Subject.query(Subject.name == name, Subject.year == year, Subject.quarter == quarter)
            if subject.count() == 0:
                try:
                    subject = Subject(name=name, year=year, quarter=quarter, user_key=ndb.Key(User, user.user_id()))
                    print(subject)
                    subject.put()
                    time.sleep(1)
                    flash(_('Subject added correctly'), 'success')
                    return redirect("/subjects")
                except Exception as e:
                    print(e.message)
            else:
                flash(_(_('Subject already exists ')), 'error')
                return render_template("addSubject.html", user_logout=users.create_logout_url("/"),
                                       name=name, year=year, quarter=quarter)
        else:
            return render_template("addSubject.html", user_logout=users.create_logout_url("/"))
    else:
        return redirect("/")


@app.route('/editSubject', methods=['GET', 'POST'])
def editSubject():
    try:
        user = users.get_current_user()
        if user:
            if flask.request.method == 'POST':
                name = flask.request.form.get("name")
                year = int(flask.request.form.get("year"))
                quarter = int(flask.request.form.get("quarter"))

                if name != "":
                    subjects = Subject.query(Subject.name == name, Subject.year == year, Subject.quarter == quarter)
                    if subjects.count() == 0:
                        sKey = int(request.args.get("key"))
                        subjectKey = ndb.Key(Subject, sKey)
                        subject = Subject.query(Subject.key == subjectKey).get()
                        subject.name=name
                        subject.year=year
                        subject.quarter=quarter

                        subject.put()
                        time.sleep(1)
                        flash(_('Subject edited correctly'), 'success')
                        return redirect("/subjects")

                    else:
                        flash(_(_('Subject already exists ')), 'error')
                else:
                    flash(_(_('Subject name cant be blank ')), 'error')
                sKey = int(request.args.get("key"))
                subjectKey = ndb.Key(Subject, sKey)
                subject = Subject.query(Subject.key == subjectKey).get()
                return render_template("editSubject.html", user_logout=users.create_logout_url("/"),
                                       subject=subject)
            else:
                try:
                    sKey = int(request.args.get("key"))
                    subjectKey = ndb.Key(Subject, sKey)
                    subject = Subject.query(Subject.key == subjectKey).get()
                    return render_template("editSubject.html", subject=subject, user_logout=users.create_logout_url("/"))
                except Exception as e:
                    print(e.message)
        else:
            return redirect("/")
    except Exception as e:
        print(e.message)


@app.route('/viewSubject')
def viewSubject():
    user = users.get_current_user()
    if user:
        try:
            sKey = int(request.args.get("key"))
            subjectKey = ndb.Key(Subject, sKey)
            subject = Subject.query(Subject.key == subjectKey).get()
            u = User.query(User.user_key == subject.user_key.id()).get()
            sofwares = list()
            softwaresDb = SubjectSoftware.query()
            for soft in softwaresDb:
                if soft.subject_key == subjectKey:
                    sofwares.append(Software.query(Software.key == soft.software_key).get())

            return render_template("viewSubject.html", user=u, softwares=sofwares, subject=subject, user_logout=users.create_logout_url("/"))
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/deleteSubject')
def deleteSubject():
    user = users.get_current_user()
    if user:
        try:
            sKey = int(request.args.get("key"))
            subjectKey = ndb.Key(Subject, sKey)
            subject = Subject.query(Subject.key == subjectKey).get()
            subject.key.delete()
            time.sleep(1)
            flash(_('Subject deleted correctly'), 'success')
            return redirect('/subjects')
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/softwares')
def showSoftwares():
    user = users.get_current_user()
    if user:
        try:
            softwares = Software.query().order(Software.name)
            return render_template("softwares.html", user_logout=users.create_logout_url("/"),
                                   softwares=softwares)
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/viewSoftware')
def viewSoftware():
    try:
        user = users.get_current_user()
        if user:
            sKey = int(request.args.get("key"))
            softwareKey = ndb.Key(Software, sKey)
            software = Software.query(Software.key == softwareKey).get()
            print(software.instalation_notes)
            return render_template("viewSoftware.html", software=software, user_logout=users.create_logout_url("/"))
        else:
            return redirect("/")
    except Exception as e:
        print(e.message)


@app.route('/exportSubjectCSV')
def exportCSV():
    user = users.get_current_user()
    if user:
        try:
            sKey = int(request.args.get("key"))
            subjectKey = ndb.Key(Subject, sKey)
            subject = Subject.query(Subject.key == subjectKey).get()

            import csv
            filename = subject.name + ".csv"
            print({'Name: ' + subject.name + ', Year: ' + str(subject.year) + ', Quarter: ' + str(subject.quarter)})

            with open(filename, 'wb') as csvfile:
                fieldnames = ['Name', 'Year', 'Quarter']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({'Name': subject.name, 'Year': subject.year, 'Quarter': subject.quarter})

            flash(_('Subject deleted correctly'), 'success')
            return redirect('/subjects')
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/addSoftware', methods=['GET', 'POST'])
def addSoftware():
    try:
        user = users.get_current_user()
        if user:
            if flask.request.method == 'POST':
                name = flask.request.form.get("name")
                url = flask.request.form.get("url")
                root = int(flask.request.form.get("root"))
                notes = flask.request.form.get("notes")

                try:
                    softwares = Software.query(Software.name == name)
                    if softwares.count() == 0:
                        software = Software(name=name, url=url, instalation_notes=notes, needs_root=root)
                        software.put()
                        time.sleep(1)
                        flash(_('Software add correctly'), 'success')
                    else:
                        flash(_('Software already exists'), 'error')

                    if "addRequest" in request.referrer:
                        return redirect('/addRequest')
                    else:
                        return redirect('/softwares')
                except Exception as e:
                    print(e.message)
            else:
                return render_template("addSoftware.html", user_logout=users.create_logout_url("/"))
        else:
            return redirect("/")
    except Exception as e:
        print(e.message)





@app.route('/requests', methods=["POST", "GET"])
def showRequests():
    user = users.get_current_user()
    if user:
        if(flask.request.method == 'POST'):
            print("POST")
        else:
            try:
                currentUser = User.query(User.user_key == user.user_id()).get()
                if currentUser.is_admin == 1:
                    requests = Request.query().get()
                else:
                    requests = Request.query(Request.user == ndb.Key(User, user.user_id()))

                return render_template("requests.html", requests=requests,
                                       user_logout=users.create_logout_url("/"))
            except Exception as e:
                print(e.message)
    else:
        return redirect("/")


@app.route('/addRequest', methods=['GET', 'POST'])
def addRequest():
    user = users.get_current_user()
    if user:
        if flask.request.method == 'POST':
            subject_key = ndb.Key(Subject, int(flask.request.form.get("subject")))

            subject = Subject.query(Subject.name == name, Subject.year == year, Subject.quarter == quarter)
            if subject.count() == 0:
                try:
                    subject = Subject(name=name, year=year, quarter=quarter, user_key=ndb.Key(User, user.user_id()))
                    print(subject)
                    subject.put()
                    time.sleep(1)
                    flash(_('Subject added correctly'), 'success')
                    return redirect("/subjects")
                except Exception as e:
                    print(e.message)
            else:
                flash(_(_('Subject already exists ')), 'error')
                return render_template("addSubject.html", user_logout=users.create_logout_url("/"),
                                       name=name, year=year, quarter=quarter)
        else:
            try:
                subjects = Subject.query(Subject.user_key == ndb.Key(User, user.user_id())).order(Subject.name)
                softwares = Software.query().order(Software.name)
                return render_template("addRequest.html", softwares=softwares, subjects=subjects, user_logout=users.create_logout_url("/"))
            except Exception as e:
                print(e.message)
    else:
        return redirect("/")
