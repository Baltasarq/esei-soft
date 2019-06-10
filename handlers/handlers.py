
from google.appengine.api import users

import time
from flask import render_template, flash, redirect, request, Response
from flask_babel import _
import flask
import datetime
from google.appengine.ext import ndb
from main import app
from models.ndbModels import Request, Software, Subject, User, RequestSoftware, System
from models.requestComplete import RequestComplete

@app.route('/')
@app.route('/index')
def login():
    user = User.get_current_user()
    if user:
        try:
            return render_template("login.html", current_user=user, user_logout=users.create_logout_url("/"))
        except Exception as e:
            print(e.message)
            print(e.args)
    else:
        return render_template("login.html", user_login=users.create_login_url("/"))


@app.route('/subjects')
def showSubjects():
    user = User.get_current_user()
    if user:
        try:
            subjects = Subject.query().order(Subject.name)
            return render_template("subjects.html", current_user=user, user_logout=users.create_logout_url("/"),
                                   subjects=subjects)
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/addSubject', methods=['GET', 'POST'])
def addSubject():
    def chk_abbreviation(abbreviation):
        toret = False
        
        for ch in abbreviation:
            if not ch.isalpha():
                break
        else:
            toret = True
            
        return toret
            
    user = User.get_current_user()
    if user:
        if flask.request.method == 'POST':
            try:
                name = flask.request.form.get("name").strip()
                abbreviation = flask.request.form.get("abbreviation").strip().upper()
                year = int(flask.request.form.get("year"))
                quarter = int(flask.request.form.get("quarter"))

                if not chk_abbreviation(abbreviation):
                    flash(_(_('Abbreviation invalid: only letters are allowed')), 'error')
                    return render_template("addSubject.html", current_user=user, user_logout=users.create_logout_url("/"),
                                        name=name, year=year, quarter=quarter)
                else:
                    subject = Subject.query(Subject.abbreviation == abbreviation)
                    if subject.count() == 0:
                            subject = Subject(name=name,
                                            abbreviation=abbreviation,
                                            year=year,
                                            quarter=quarter,
                                            user_key=ndb.Key(User, user.user_id))
                            subject.put()
                            time.sleep(1)
                            flash(_('Subject added correctly'), 'success')
                            return redirect("/subjects")
                    else:
                        flash(_(_('Subject already exists ')) + ": " + abbreviation, 'error')
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
        user = User.get_current_user()
        if user:
            if flask.request.method == 'POST':
                name = flask.request.form.get("name").strip()
                abbreviation = flask.request.form.get("abbreviation")
                year = int(flask.request.form.get("year"))
                quarter = int(flask.request.form.get("quarter"))

                if abbreviation:
                    abbreviation = abbreviation.strip().upper()

                if name != "":
                    subjects = Subject.query(Subject.abbreviation == abbreviation)
                    if subjects.count() == 0:
                        sKey = int(request.args.get("key"))
                        subject_key = ndb.Key(Subject, sKey)
                        subject = Subject.query(Subject.key == subject_key).get()
                        subject.name = name
                        subject.year = year
                        subject.quarter = quarter

                        subject.put()
                        time.sleep(1)
                        flash(_('Subject edited correctly'), 'success')
                        return redirect("/subjects")

                    else:
                        flash(_(_('Subject already exists ')) + ": " + abbreviation, 'error')
                else:
                    flash(_(_('Subject name cant be blank ')), 'error')
                sKey = int(request.args.get("key"))
                subject_key = ndb.Key(Subject, sKey)
                subject = Subject.query(Subject.key == subject_key).get()
                return render_template("editSubject.html", current_user=user, user_logout=users.create_logout_url("/"),
                                       subject=subject)
            else:
                try:
                    sKey = int(request.args.get("key"))
                    subject_key = ndb.Key(Subject, sKey)
                    subject = Subject.query(Subject.key == subject_key).get()
                    return render_template("editSubject.html", current_user=user, subject=subject, user_logout=users.create_logout_url("/"))
                except Exception as e:
                    print(e.message)
        else:
            return redirect("/")
    except Exception as e:
        print(e.message)


@app.route('/viewSubject')
def viewSubject():
    user = User.get_current_user()
    if user:
        try:
            sKey = int(request.args.get("key"))
            subjectKey = ndb.Key(Subject, sKey)
            subject = Subject.query(Subject.key == subjectKey).get()
            u = User.query(User.user_id == subject.user_key.id()).get()
            sofwares = list()

            requests = Request.query(Request.subject_key == subjectKey)

            for r in requests:
                softwareRequests = RequestSoftware.query(RequestSoftware.request_key == r.key)
                for softwareRequest in softwareRequests:
                    softToAdd = Software.query(Software.key == softwareRequest.software_key).get()
                    if softToAdd not in sofwares:
                        sofwares.append(softToAdd)

            return render_template("viewSubject.html",
                                   current_user=user,
                                   user=u,
                                   softwares=sofwares,
                                   subject=subject,
                                   user_logout=users.create_logout_url("/"))
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/deleteSubject')
def deleteSubject():
    user = User.get_current_user()
    if user:
        try:
            sKey = int(request.args.get("key"))
            subjectKey = ndb.Key(Subject, sKey)
            subject = Subject.query(Subject.key == subjectKey).get()
            requests = Request.query(Request.subject_key == subjectKey)
            for r in requests:
                sofsRequests = RequestSoftware.query(RequestSoftware.request_key == r.key)
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
        user = User.get_current_user()
        if user:
            if flask.request.method == 'POST':
                name = flask.request.form.get("name").strip()
                url = flask.request.form.get("url").strip()
                root = str(flask.request.form.get("root")).strip().lower() == "true"
                notes = flask.request.form.get("notes").encode("utf-8")

                if not url.lower().startswith("http"):
                    url = "http://" + url

                try:
                    softwares = Software.query(Software.name == name)

                    if softwares.count() == 0:
                        software = Software(name=name,
                                            url=url,
                                            instalation_notes=notes,
                                            needs_root=root)
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
    user = User.get_current_user()
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
        user = User.get_current_user()
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
    user = User.get_current_user()
    if user:
        try:
            sKey = int(request.args.get("key"))
            softwareKey = ndb.Key(Software, sKey)
            software = Software.query(Software.key == softwareKey).get()

            requestsDeleted = list()
            requestsInDB = list()

            requestSoftware = RequestSoftware.query(RequestSoftware.software_key == softwareKey)
            for rs in requestSoftware:
                requestsDeleted.append(rs)
                rs.key.delete()
                time.sleep(1)

            aux = RequestSoftware.query()

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
    user = User.get_current_user()
    if user:
        try:
            date_and_time = datetime.datetime.today()
            date = str(date_and_time).split(' ')[0]
            file_name = date.split('-')[2] + date.split('-')[1] + date.split('-')[0]

            requests_to_generate = []
            requests = Request.query().order(Request.subject_key)
            for found_request in requests:
                request_owner = User.query(User.user_id == found_request.user_key.id()).get()

                subject = Subject.query(Subject.key == found_request.subject_key).get()
                requested_software = RequestSoftware.query(RequestSoftware.request_key == found_request.key)
                apps = list()

                for app in requested_software:
                    apps.append(Software.query(Software.key == app.software_key).get())

                requests_to_generate.append(
                    RequestComplete(found_request.key, request_owner, subject, apps, found_request.system, found_request.date))

            # All requests accounted for, generate CSV
            csv_content = "Request date, Operating System, " \
                          "User name, " \
                          "Abbrev, Subject name, Subject course, Subject quarter, " \
                          "Software name, needs root, notes\n"

            for complete_request in requests_to_generate:
                request_owner = complete_request.getUser()
                subject = complete_request.getSubject()
                softs = complete_request.getSoftware()

                if complete_request.getSystem() == System.LINUX:
                    system = 'Linux'
                elif complete_request.getSystem() == System.WINDOWS:
                    system = 'Windows'
                else:
                    system = 'Linux & Windows'

                content_to_append = ""
                for software in softs:
                    content_to_append += str.split(str(complete_request.getDate()), ".")[0] + "," + system + "," \
                        + request_owner.name.encode("utf-8") + ","\
                        + subject.abbreviation.encode("utf-8") + ","\
                        + subject.name.encode("utf-8") + "," + str(subject.year) + "," + str(subject.quarter) + ","\
                        + software.name.encode("utf-8") + "," + str(software.needs_root) + "," + software.instalation_notes.encode("utf-8")\
                        + "\n"
                csv_content += content_to_append

            generator = (cell for row in csv_content
                         for cell in row)

            return Response(generator,
                            mimetype="text/csv",
                            headers={"Content-Disposition": "attachment;filename=" + file_name + ".csv"})

        except Exception as e:
            print(e)
    else:
        return redirect("/")

@app.route('/exportXML')
def exportXML():
    user = User.get_current_user()
    if user:
        try:
            dateTime = datetime.datetime.today()
            date = str(dateTime).split(' ')[0]
            fileName = date.split('-')[2] + date.split('-')[1] + date.split('-')[0]

            requestToShow = []
            requests = Request.query()
            for request in requests:
                u = User.query(User.user_id == request.user_key.id()).get()

                s = Subject.query(Subject.key == request.subject_key).get()
                requestSofts = RequestSoftware.query(RequestSoftware.request_key == request.key)
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
                    "<user><key>" + str(u.user_id) + "</key><name>" + u.name.encode("utf-8") + "</name></user>"\
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
    user = User.get_current_user()
    if user:
        try:
            requestToShow = []
            requests = Request.query()

            for request in requests:
                u = User.query(User.user_id == request.user_key.id()).get()

                s = Subject.query(Subject.key == request.subject_key).get()
                requestSofts = RequestSoftware.query(RequestSoftware.request_key == request.key)
                softwares = list()

                for soft in requestSofts:
                    softwares.append(Software.query(Software.key == soft.software_key).get())

                requestToShow.append(RequestComplete(request.key, u, s, softwares, request.system, request.date, ))

            return render_template("requests.html", current_user=user,
                                   requests=requestToShow,
                                   user_logout=users.create_logout_url("/"), is_admin=users.is_current_user_admin())
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/addRequest', methods=['GET', 'POST'])
def addRequest():
    user = User.get_current_user()
    if user:
        if flask.request.method == 'POST':
            subject_key = ndb.Key(Subject, int(flask.request.form.get("subject")))

            try:
                request = Request()
                user_key = ndb.Key(User, user.user_id)
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
                    requestSoftwares = RequestSoftware()
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
                subjects = Subject.query().order(Subject.name)
                softwares = Software.query().order(Software.name)
                return render_template("addRequest.html", current_user=user, softwares=softwares,
                                       subjects=subjects, user_logout=users.create_logout_url("/"))

            except Exception as e:
                print(e.message)
    else:
        return redirect("/")


@app.route('/viewRequest', methods=["POST", "GET"])
def viewRequest():
    user = User.get_current_user()
    if user:
        try:
            rKey = int(request.args.get("key"))
            req = Request.query(Request.key == ndb.Key(Request, rKey)).get()

            u = User.query(User.user_id == req.user_key.id()).get()
            s = Subject.query(Subject.key == req.subject_key).get()

            requestSofts = RequestSoftware.query(RequestSoftware.request_key == req.key)
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
    user = User.get_current_user()
    if user:
        try:
            rKey = int(request.args.get("key"))
            req = Request.query(Request.key == ndb.Key(Request, rKey)).get()
            req.key.delete()
            time.sleep(1)
            sofsRequests = RequestSoftware.query(RequestSoftware.request_key == ndb.Key(Request, rKey))
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
