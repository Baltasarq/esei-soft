
from google.appengine.api import users

import time
from flask import render_template, flash, redirect, request, Response
from flask_babel import _
import flask
import datetime
from google.appengine.ext import ndb
from main import app
from models.ndbModels import Request, Software, Subject, User, Request_Software, System
from models.requestComplete import RequestComplete

@app.route('/')
@app.route('/index')
def login():
    user = users.get_current_user()
    if user:
        try:
            usersDb = User.query(User.user_key == user.user_id())
            if usersDb.count() == 0:
                # Store new User
                username = user.nickname()
                new_user = User(user_key=user.user_id(), name=user.nickname())
                if users.is_current_user_admin():
                    new_user.is_admin = 1
                else:
                    new_user.is_admin = 0

                new_user.put()
                time.sleep(1)
            return render_template("login.html", current_user=user, user_logout=users.create_logout_url("/"),
                                   is_admin=users.is_current_user_admin())
        except Exception as e:
            print(e.message)
    else:
        return render_template("login.html", user_login=users.create_login_url("/"))


@app.route('/subjects')
def showSubjects():
    user = users.get_current_user()
    if user:
        try:
            u = User.query(User.user_key == user.user_id()).get()
            subjects = Subject.query().order(Subject.name)
            return render_template("subjects.html", current_user=user, user=u, user_logout=users.create_logout_url("/"),
                                   subjects=subjects, is_admin=users.is_current_user_admin())
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/addSubject', methods=['GET', 'POST'])
def addSubject():
    user = users.get_current_user()
    if user:
        if flask.request.method == 'POST':
            try:
                name = flask.request.form.get("name").strip()
                year = int(flask.request.form.get("year"))
                quarter = int(flask.request.form.get("quarter"))

                subject = Subject.query(Subject.name == name, Subject.year == year, Subject.quarter == quarter)
                if subject.count() == 0:

                        subject = Subject(name=name, year=year, quarter=quarter, user_key=ndb.Key(User, user.user_id()))
                        subject.put()
                        time.sleep(1)
                        flash(_('Subject added correctly'), 'success')
                        return redirect("/subjects")
                else:
                    flash(_(_('Subject already exists ')), 'error')
                    return render_template("addSubject.html", current_user=user, user_logout=users.create_logout_url("/"),
                                           name=name, year=year, quarter=quarter)
            except Exception as e:
                print(e.message)
        else:
            return render_template("addSubject.html", current_user=user, user_logout=users.create_logout_url("/"))
    else:
        return redirect("/")


@app.route('/editSubject', methods=['GET', 'POST'])
def editSubject():
    try:
        user = users.get_current_user()
        if user:
            if flask.request.method == 'POST':
                name = flask.request.form.get("name").strip()
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
                return render_template("editSubject.html", current_user=user, user_logout=users.create_logout_url("/"),
                                       subject=subject)
            else:
                try:
                    sKey = int(request.args.get("key"))
                    subjectKey = ndb.Key(Subject, sKey)
                    subject = Subject.query(Subject.key == subjectKey).get()
                    return render_template("editSubject.html", current_user=user, subject=subject, user_logout=users.create_logout_url("/"))
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

            requests = Request.query(Request.subject_key == subjectKey)

            for r in requests:
                softwareRequests = Request_Software.query(Request_Software.request_key == r.key)
                for softwareRequest in softwareRequests:
                    softToAdd = Software.query(Software.key == softwareRequest.software_key).get()
                    if softToAdd not in sofwares:
                        sofwares.append(softToAdd)

            return render_template("viewSubject.html", current_user=user, user=u, softwares=sofwares, subject=subject,
                                   user_logout=users.create_logout_url("/"))
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
            requests = Request.query(Request.subject_key == subjectKey)
            for r in requests:
                sofsRequests = Request_Software.query(Request_Software.request_key == r.key)
                for s in sofsRequests:
                    s.key.delete()
                r.key.delete()
                time.sleep(0.5)
            subject.key.delete()
            time.sleep(1)
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
                name = flask.request.form.get("name").strip()
                url = flask.request.form.get("url").strip()
                root = int(flask.request.form.get("root"))
                notes = flask.request.form.get("notes").encode("utf-8")

                try:
                    softwares = Software.query(Software.name == name)
                    if softwares.count() == 0:
                        software = Software(name=name, url=url, instalation_notes=notes, needs_root=root)
                        software.put()
                        time.sleep(1)
                        flash(_('Software added correctly'), 'success')
                    else:
                        flash(_('Software already exists'), 'error')

                    if "addRequest" in request.referrer:
                        return redirect('/addRequest')
                    else:
                        return redirect('/softwares')
                except Exception as e:
                    print(e.message)
            else:
                return render_template("addSoftware.html", current_user=user, user_logout=users.create_logout_url("/"))
        else:
            return redirect("/")
    except Exception as e:
        print(e.message)


@app.route('/softwares')
def showSoftwares():
    user = users.get_current_user()
    if user:
        try:
            softwares = Software.query().order(Software.name)
            return render_template("softwares.html", current_user=user, user_logout=users.create_logout_url("/"),
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
            return render_template("viewSoftware.html", current_user=user, software=software, user_logout=users.create_logout_url("/"))
        else:
            return redirect("/")
    except Exception as e:
        print(e.message)


@app.route('/deleteSoftware')
def deleteSoftware():
    user = users.get_current_user()
    if user:
        try:
            sKey = int(request.args.get("key"))
            softwareKey = ndb.Key(Software, sKey)
            software = Software.query(Software.key == softwareKey).get()

            requestsDeleted = list()
            requestsInDB = list()

            requestSoftware = Request_Software.query(Request_Software.software_key == softwareKey)
            for rs in requestSoftware:
                requestsDeleted.append(rs)
                rs.key.delete()
                time.sleep(1)

            aux = Request_Software.query()

            for r in aux:
                requestsInDB.append(r.request_key)

            for req in requestsDeleted:
                if req.request_key not in requestsInDB:
                    requestToDelete = Request.query(Request.key == req.request_key).get()
                    requestToDelete.key.delete()
                    time.sleep(0.5)

            software.key.delete()
            time.sleep(1)
            flash(_('Software deleted correctly'), 'success')
            return redirect('/softwares')
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/exportCSV')
def exportCSV():
    user = users.get_current_user()
    if user:
        try:
            dateTime = datetime.datetime.today()
            date = str(dateTime).split(' ')[0]
            fileName = date.split('-')[2] + date.split('-')[1] + date.split('-')[0]

            requestToShow = []
            requests = Request.query()
            for request in requests:
                u = User.query(User.user_key == request.user_key.id()).get()

                s = Subject.query(Subject.key == request.subject_key).get()
                requestSofts = Request_Software.query(Request_Software.request_key == request.key)
                softwares = list()

                for soft in requestSofts:
                    softwares.append(Software.query(Software.key == soft.software_key).get())

                requestToShow.append(RequestComplete(request.key, u, s, softwares, request.system, request.date))

            csv_content = "Request_date, Operative System, " \
                          "User_name, " \
                          "Subject_name, Subject_course, Subject_quarter, " \
                          "Software_name\n"

            for rc in requestToShow:
                u = rc.getUser()
                sub = rc.getSubject()
                softs = rc.getSoftware()
                if rc.getSystem() == System.LINUX:
                    system = 'Linux'
                elif rc.getSystem() == System.WINDOWS:
                    system = 'Windows'
                else:
                    system = 'Linux and Windows'

                for s in softs:
                    contentToAppend = str.split(str(rc.getDate()), ".")[0] + "," + system + "," \
                        + u.name.encode("utf-8") + ","\
                        + sub.name.encode("utf-8") + "," + str(sub.year) + "," + str(sub.quarter) + ","\
                        + s.name.encode("utf-8") + "\n"
                csv_content += contentToAppend

            generator = (cell for row in csv_content
                         for cell in row)

            return Response(generator,
                            mimetype="text/csv",
                            headers={"Content-Disposition": "attachment;filename=" + fileName + ".csv"})

        except Exception as e:
            print(e)
    else:
        return redirect("/")

@app.route('/exportXML')
def exportXML():
    user = users.get_current_user()
    if user:
        try:
            dateTime = datetime.datetime.today()
            date = str(dateTime).split(' ')[0]
            fileName = date.split('-')[2] + date.split('-')[1] + date.split('-')[0]

            requestToShow = []
            requests = Request.query()
            for request in requests:
                u = User.query(User.user_key == request.user_key.id()).get()

                s = Subject.query(Subject.key == request.subject_key).get()
                requestSofts = Request_Software.query(Request_Software.request_key == request.key)
                softwares = list()

                for soft in requestSofts:
                    softwares.append(Software.query(Software.key == soft.software_key).get())

                requestToShow.append(RequestComplete(request.key, u, s, softwares, request.system, request.date))

            xml_content = "<requests>"

            for rc in requestToShow:
                u = rc.getUser()
                sub = rc.getSubject()
                softs = rc.getSoftware()
                if rc.getSystem() == System.LINUX:
                    system = 'Linux'
                elif rc.getSystem() == System.WINDOWS:
                    system = 'Windows'
                else:
                    system = 'Linux and Windows'

                contentToAppend = \
                    "<request>" \
                    "<date>" + str.split(str(rc.getDate()), ".")[0] + "</date>"\
                    "<system>" + system + "</system>"\
                    "<user><key>" + str(u.user_key) + "</key><name>" + u.name.encode("utf-8") + "</name></user>"\
                    "<subject>" \
                        "<key>" + str(sub.key.id()) + "</key>" \
                        "<name>" + sub.name.encode("utf-8") + "</name>" \
                        "<course>" + str(sub.year) + "</course>" \
                        "<quarter>" + str(sub.quarter) + "</quarter></subject>"\
                        "<softwares>"
                for s in softs:
                    contentToAppend += "<software>" \
                                       "<key>" + str(s.key.id()) + "</key>" \
                                       "<name>" + s.name.encode("utf-8") + "</name>" \
                                       "<needs_root>"
                    if s.needs_root == 0:
                        contentToAppend += "No"
                    else:
                        contentToAppend += "Yes"
                    contentToAppend += "</needs_root></software>"

                contentToAppend += "</softwares></request>"

                xml_content += contentToAppend

            xml_content += "</requests>"
            generator = (cell for row in xml_content
                         for cell in row)

            return Response(generator,
                            mimetype="text/xml",
                            headers={"Content-Disposition": "attachment;filename=" + fileName + ".xml"})

        except Exception as e:
            print(e)
    else:
        return redirect("/")


@app.route('/requests', methods=["POST", "GET"])
def showRequests():
    user = users.get_current_user()
    if user:
        try:
            requestToShow = []
            requests = Request.query()

            for request in requests:
                u = User.query(User.user_key == request.user_key.id()).get()

                s = Subject.query(Subject.key == request.subject_key).get()
                requestSofts = Request_Software.query(Request_Software.request_key == request.key)
                softwares = list()

                for soft in requestSofts:
                    softwares.append(Software.query(Software.key == soft.software_key).get())

                requestToShow.append(RequestComplete(request.key, u, s, softwares, request.system, request.date, ))

            u = User.query(User.user_key == user.user_id()).get()
            return render_template("requests.html", current_user=user, user=u, requests=requestToShow,
                                   user_logout=users.create_logout_url("/"), is_admin=users.is_current_user_admin())
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/addRequest', methods=['GET', 'POST'])
def addRequest():
    user = users.get_current_user()
    if user:
         if users.is_current_user_admin():
            if flask.request.method == 'POST':
                subject_key = ndb.Key(Subject, int(flask.request.form.get("subject")))

                try:
                    request = Request()
                    user_key = ndb.Key(User, user.user_id())
                    request.user_key = user_key
                    request.subject_key = subject_key
                    date = datetime.datetime.today()
                    request.date = date

                    systems = flask.request.form.getlist("systems")

                    print(systems[0])
                    if len(systems) > 1:
                        request.system = System.BOTH
                    elif int(systems[0]) == 1:
                        request.system = System.LINUX
                        print(System.LINUX)
                    else:
                        print(System.WINDOWS)
                        request.system = System.WINDOWS

                    request.put()
                    time.sleep(1)

                    currentRequest = Request.query(Request.user_key == user_key, Request.date == date,
                                                   Request.subject_key == subject_key).get()

                    softwares = flask.request.form.getlist("softwares")
                    #Add all software to the Request
                    for software in softwares:
                        requestSoftwares = Request_Software()
                        requestSoftwares.request_key = currentRequest.key
                        requestSoftwares.software_key = ndb.Key(Software, int(software))
                        requestSoftwares.put()
                        time.sleep(1)

                    flash(_('Request added correctly'), 'success')
                    return redirect("/requests")
                except Exception as e:
                    print(e.message)
            else:
                try:
                    u = User.query(User.user_key == user.user_id()).get()
                    subjects = Subject.query().order(Subject.name)
                    softwares = Software.query().order(Software.name)
                    return render_template("addRequest.html", user=u, current_user=user, softwares=softwares,
                                           subjects=subjects, user_logout=users.create_logout_url("/"))

                except Exception as e:
                    print(e.message)
         else:
            flash(_('You dont have permission for this action'), 'error')
            return redirect("/")
    else:
        return redirect("/")


@app.route('/viewRequest', methods=["POST", "GET"])
def viewRequest():
    user = users.get_current_user()
    if user:
        try:
            rKey = int(request.args.get("key"))
            req = Request.query(Request.key == ndb.Key(Request, rKey)).get()

            u = User.query(User.user_key == req.user_key.id()).get()
            s = Subject.query(Subject.key == req.subject_key).get()

            requestSofts = Request_Software.query(Request_Software.request_key == req.key)
            softwares = list()

            for soft in requestSofts:
                softwares.append(Software.query(Software.key == soft.software_key).get())

            requestToShow = RequestComplete(req.key, u, s, softwares, req.system, req.date, )

            return render_template("viewRequest.html", current_user=user, request=requestToShow,
                                   user_logout=users.create_logout_url("/"))
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")

@app.route('/deleteRequest')
def deleteRequest():
    user = users.get_current_user()
    if user:
        try:
            rKey = int(request.args.get("key"))
            req = Request.query(Request.key == ndb.Key(Request, rKey)).get()
            req.key.delete()
            time.sleep(1)
            sofsRequests = Request_Software.query(Request_Software.request_key == ndb.Key(Request,rKey))
            for s in sofsRequests:
                print(s.key)
                s.key.delete()
                time.sleep(0.5)
            flash(_('Software deleted correctly'), 'success')
            return redirect('/requests')
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")
