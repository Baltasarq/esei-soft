# (c) 2019 esei-soft Baltasar MIT License <baltasarq@gmail.com>


import time
import datetime

from flask import render_template, flash, redirect, request, Response
from flask_babel import _
import flask
from google.appengine.ext import ndb
from google.appengine.api import users

from main import app
from models.ndb_models import retrieve_obj, Request, Software, Subject, User, RequestSoftware, System
from models.request_complete import RequestComplete
from models.appinfo import AppInfo


def create_anonymous_user():
    """Creates an anonymous user, in case it is not found for a request."""
    return User(name="no usr", is_admin=False, user_id="0")


def create_anonynous_subject():
    """Creates an anonymous subject, in case it is not found for a request."""
    return Subject(name="undefined", abbreviation="n/a", year=1992, quarter=1)


def correct_capitalization(s):
    """Capitalizes a string with various words, except for prepositions and articles.

        :param s: The string to capitalize.
        :return: A new, capitalized, string.
    """

    toret = ""

    if s:
        always_upper = {"tic", "i", "ii", "iii", "iv", "v", "vs", "vs.", "2d", "3d",
                        "swi", "gnu", "c++", "c/c++", "c#"}
        articles = {"el", "la", "las", "lo", "los", "un", "unos", "una", "unas",
                    "a", "an", "the", "these", "those", "that"}
        preps = {"en", "de", "del", "para", "con", "y", "e", "o",
                 "in", "of", "for", "with", "and", "or"}

        words = s.strip().lower().split()
        capitalized_words = []

        for word in words:
            if word in always_upper:
                word = word.upper()
            elif (not word in articles
              and not word in preps):
                word = word.capitalize()

            capitalized_words.append(word)

        toret = ' '.join(capitalized_words)

    return toret


@app.route('/')
@app.route('/index')
def login():
    user = User.get_current_user()
    if user:
        try:
            return render_template("login.html",
                                   AppInfo=AppInfo,
                                   current_user=user,
                                   user_logout=users.create_logout_url("/"))
        except Exception as e:
            print(e.message)
            print(e.args)
    else:
        return render_template("login.html", AppInfo=AppInfo, user_login=users.create_login_url("/"))


@app.route('/subjects')
def showSubjects():
    user = User.get_current_user()
    if user:
        try:
            subjects = Subject.query().order(Subject.abbreviation)
            return render_template("subjects.html",
                                   AppInfo=AppInfo,
                                   current_user=user,
                                   user_logout=users.create_logout_url("/"),
                                   subjects=subjects)
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/addSubject', methods=['GET', 'POST'])
def addSubject():
    def chk_abbreviation(abbreviation):
        """Checks whether the abbreviation is composed only by letters."""

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
                name = correct_capitalization(flask.request.form.get("name"))
                abbreviation = flask.request.form.get("abbreviation").strip().upper()
                year = int(flask.request.form.get("year"))
                quarter = int(flask.request.form.get("quarter"))

                if not chk_abbreviation(abbreviation):
                    flash(_(_('Abbreviation invalid: only letters are allowed')), 'error')
                    return render_template("addSubject.html",
                                           AppInfo=AppInfo,
                                           current_user=user,
                                           user_logout=users.create_logout_url("/"),
                                           name=name, year=year, quarter=quarter)
                else:
                    subject = Subject.query(Subject.abbreviation == abbreviation)
                    if subject.count() == 0:
                            subject = Subject(name=name,
                                            abbreviation=abbreviation,
                                            year=year,
                                            quarter=quarter,
                                            user_key=user.key)
                            subject.put()
                            time.sleep(1)
                            flash(_('Subject added correctly'), 'success')
                            return redirect("/subjects")
                    else:
                        flash(_(_('Subject already exists ')) + ": " + abbreviation, 'error')
                        return render_template("addSubject.html",
                                               AppInfo=AppInfo,
                                               current_user=user,
                                               user_logout=users.create_logout_url("/"),
                                               name=name, year=year, quarter=quarter)
            except Exception as e:
                print(e.message)
        else:
            return render_template("addSubject.html",
                                   AppInfo=AppInfo,
                                   current_user=user,
                                   user_logout=users.create_logout_url("/"))
    else:
        return redirect("/")


@app.route('/editSubject', methods=['GET', 'POST'])
def editSubject():
    try:
        user = User.get_current_user()
        
        if user:
            str_key = request.args.get("key")
            subject = retrieve_obj(Subject, str_key)
            
            if not subject:
                flash("Subject.id == " + str(str_key) + "??", 'error')
                return redirect("/subjects")
            
            if flask.request.method == 'POST':
                name = correct_capitalization(flask.request.form.get("name").strip())
                abbreviation = flask.request.form.get("abbreviation")
                year = int(flask.request.form.get("year"))
                quarter = int(flask.request.form.get("quarter"))

                if abbreviation:
                    abbreviation = abbreviation.strip().upper()

                if not name or not abbreviation:
                    subjects = Subject.query(Subject.abbreviation == abbreviation)
                    if subjects.count() == 0:
                        subject.name = name
                        subject.year = year
                        subject.quarter = quarter
                        subject.user_key = user.key

                        subject.put()
                        time.sleep(1)
                        flash(_('Subject edited correctly'), 'success')                            
                        return redirect("/subjects")

                    else:
                        flash(_(_('Subject already exists ')) + ": " + abbreviation, 'error')
                else:
                    flash(_(_('Subject name cant be blank ')), 'error')

            return render_template("editSubject.html",
                                   AppInfo=AppInfo,
                                   current_user=user,
                                   user_logout=users.create_logout_url("/"),
                                   subject=subject)
        else:
            return redirect("/")
    except Exception as e:
        print(e.message)


@app.route('/viewSubject')
def viewSubject():
    user = User.get_current_user()
    if user:
        try:
            str_key = request.args.get("key")
            subject = retrieve_obj(Subject, str_key)
            
            if subject:
                subject_owner = subject.user_key.get()
                apps = []

                if not subject_owner:
                    subject_owner = create_anonymous_user()

                requests = Request.query(Request.subject_key == subject.key)

                for req in requests:
                    for software_in_request in RequestSoftware.query(RequestSoftware.request_key == req.key):
                        apps.append(software_in_request.software_key.get())

                return render_template("viewSubject.html",
                                        AppInfo=AppInfo,
                                        current_user=user,
                                        subject_owner=subject_owner,
                                        softwares=list(apps),
                                        subject=subject,
                                        user_logout=users.create_logout_url("/"))
            else:
                flash("Subject.key == " + str(str_key) + "??", 'error')
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/deleteSubject')
def deleteSubject():
    user = User.get_current_user()
    if user:
        try:
            str_key = request.args.get("key")
            subject = retrieve_obj(Subject, str_key)
            
            if subject:
                requests = Request.query(Request.subject_key == subject.key)
                
                for req in requests:
                    pairs = RequestSoftware.query(RequestSoftware.request_key == req.key)

                    for pair_req_soft in pairs:
                        pair_req_soft.key.delete()

                    req.key.delete()

                subject.key.delete()
                time.sleep(1)
                flash(_('Subject deleted correctly'), 'success')
            else:
                flash("Subject.key == " + str(str_key) + "??", 'error')

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
                name = correct_capitalization(flask.request.form.get("name"))
                url = flask.request.form.get("url").strip()
                root = str(flask.request.form.get("root")).strip().lower() == "true"
                notes = flask.request.form.get("notes").encode("utf-8")

                if url and not url.lower().startswith("http"):
                    url = "http://" + url

                try:
                    softwares = Software.query(Software.name == name)

                    if softwares.count() == 0:
                        software = Software(name=name,
                                            url=url,
                                            installation_notes=notes,
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
                return render_template("addSoftware.html",
                                       AppInfo=AppInfo,
                                       current_user=user,
                                       user_logout=users.create_logout_url("/"))
        else:
            return redirect("/")
    except Exception as e:
        print(e.message)


@app.route('/editSoftware', methods=['GET', 'POST'])
def editSoftware():
    try:
        user = User.get_current_user()
        if user:
            str_key = request.args.get("key")
            software = retrieve_obj(Software, str_key)
            
            if not software:
                flash("Software.key == " + str(str_key) + "??", 'error')
                return redirect('/softwares')

            if flask.request.method == 'POST':
                name = correct_capitalization(flask.request.form.get("name"))
                url = flask.request.form.get("url").strip().lower()
                needs_root = str(flask.request.form.get("root")).strip().lower() == "true"
                notes = flask.request.form.get("notes").encode("utf-8")

                if url and not url.lower().startswith("http"):
                    url = "http://" + url

                try:
                    software.name = name
                    software.url = url
                    software.needs_root = needs_root
                    software.installation_notes = notes
                    software.put()

                    time.sleep(1)
                    flash(_('Software added correctly'), 'success')

                    return redirect('/softwares')
                except Exception as e:
                    print(e.message)
            else:
                return render_template("editSoftware.html",
                                       AppInfo=AppInfo,
                                       current_user=user,
                                       app=software,
                                       user_logout=users.create_logout_url("/"))
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
            return render_template("softwares.html",
                                   AppInfo=AppInfo,
                                   current_user=user,
                                   user_logout=users.create_logout_url("/"),
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
            str_key = request.args.get("key")
            software = retrieve_obj(Software, str_key)
            
            if not software:
                flash("Software.key == " + str(str_key) + "??", 'error')
                return redirect("/softwares")
                
            return render_template("viewSoftware.html",
                                   AppInfo=AppInfo,
                                   current_user=user,
                                   software=software,
                                   user_logout=users.create_logout_url("/"))
        else:
            return redirect("/")
    except Exception as e:
        print(e.message)


@app.route('/deleteSoftware')
def deleteSoftware():
    user = User.get_current_user()
    if user:
        try:
            str_key = request.args.get("key")
            software = retrieve_obj(Software, str_key)
            
            if not software:
                flash("Software.key == " + str(str_key) + "??", 'error')
                return redirect("/softwares")

            # Delete the request/software pairs for that software
            req_soft_pairs = RequestSoftware.query(RequestSoftware.software_key == software.key)
            
            affected_requests = []
            for pair in req_soft_pairs:
                affected_requests.append(pair.request_key)
                pair.key.delete()
            
            # Delete those affected requests without corresponding pairs
            for affected_request in affected_requests:
                affected_pairs = RequestSoftware.query(RequestSoftware.request_key == affected_request.key)
                
                if affected_pairs.count() == 0:
                    affected_request.delete()

            # Delete the software itself
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
                softs = complete_request.getSoftwares()

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
                        + software.name.encode("utf-8") + "," + str(software.needs_root) + "," + software.installation_notes.encode("utf-8")\
                        + "\n"
                    
                if content_to_append:
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
                softs = rc.getSoftwares()
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
            requests_to_show = []
            requests = Request.query()
            is_current_user_the_owner = False

            for request in requests:
                req_owner = request.user_key.get()

                if not req_owner:
                    req_owner = create_anonymous_user()
                else:
                    is_current_user_the_owner = (user.key.id() == req_owner.key.id())

                req_subject = request.subject_key.get()
                req_softs = RequestSoftware.query(RequestSoftware.request_key == request.key)
                softwares = list()

                for soft in req_softs:
                    softwares.append(Software.query(Software.key == soft.software_key).get())

                requests_to_show.append(
                    RequestComplete(
                        request.key,
                        req_owner,
                        req_subject,
                        softwares,
                        [],
                        request.system,
                        request.date))

            return render_template("requests.html",
                                   AppInfo=AppInfo,
                                   current_user=user,
                                   requests=requests_to_show,
                                   user_logout=users.create_logout_url("/"),
                                   is_admin=user.is_admin,
                                   is_current_user_the_owner=is_current_user_the_owner)
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/addRequest', methods=['GET', 'POST'])
def addRequest():
    user = User.get_current_user()

    if user:
        if flask.request.method == 'POST':
            str_key = flask.request.form.get("subject")
            subject = retrieve_obj(Subject, str_key)

            if not subject:
                flash("Subject.key == " + str(str_key) + "??", 'error')
                return redirect("/requests")

            try:
                request = Request()
                request.user_key = user.key
                request.subject_key = subject.key

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

                all_software = flask.request.form.getlist("softwares")

                # Add all softwares to the request
                for software in all_software:
                    request_software = RequestSoftware()
                    request_software.request_key = request.key
                    request_software.software_key = ndb.Key(Software, int(software))
                    request_software.put()
                    time.sleep(1)

                flash(_('Request added correctly'), 'success')
                return redirect("/requests")
            except Exception as e:
                print(e.message)
        else:
            try:
                subjects = Subject.query().order(Subject.name)
                softwares = Software.query().order(Software.name)
                return render_template("addRequest.html",
                                       AppInfo=AppInfo,
                                       current_user=user,
                                       softwares=softwares,
                                       subjects=subjects,
                                       user_logout=users.create_logout_url("/"))

            except Exception as e:
                print(e.message)
    else:
        return redirect("/")


@app.route('/viewRequest', methods=["POST", "GET"])
def viewRequest():
    user = User.get_current_user()
    if user:
        try:
            str_key = request.args.get("key")
            req = retrieve_obj(Request, str_key)

            if not req:
                flash("Request.key == " + str(str_key) + "??", 'error')
                return redirect("/requests")

            req_owner = req.user_key.get()
            req_subject = req.subject_key.get()

            if not req_owner:
                req_owner = create_anonymous_user()

            if not req_subject:
                req_subject = create_anonynous_subject()

            pairs_req_soft = RequestSoftware.query(RequestSoftware.request_key == req.key)
            softwares = []
            pairs_keys = []

            for pair_req_soft in pairs_req_soft:
                softwares.append(pair_req_soft.software_key.get())
                pairs_keys.append(pair_req_soft.key)

            request_to_show = RequestComplete(req.key,
                                              req_owner,
                                              req_subject,
                                              softwares,
                                              pairs_keys,
                                              req.system,
                                              req.date)

            return render_template("viewRequest.html",
                                   AppInfo=AppInfo,
                                   current_user=user,
                                   request=request_to_show,
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
            str_key = request.args.get("key")
            req = retrieve_obj(Request, str_key)

            if req:
                # Delete all related request - software pairs
                soft_reqs = RequestSoftware.query(RequestSoftware.request_key == req.key)

                for pair in soft_reqs:
                    pair.key.delete()

                flash(_('request deleted correctly'), 'success')

                # Delete the request itself
                req.key.delete()
                time.sleep(1)
            else:
                flash("Request.key == " + str(str_key) + "??")

            return redirect('/requests')
        except Exception as e:
            print(e.message)
    else:
        return redirect("/")


@app.route('/deleteRequestPair')
def deleteRequestPair():
    user = User.get_current_user()

    if user:
        try:
            str_key = request.args.get("key")
            req_pair = retrieve_obj(RequestSoftware, str_key)

            if not req_pair:
                flash("RequestSoftware.id == " + str(str_key) + "??", 'error')
                return redirect("/requests")

            # Find the request
            req = req_pair.request_key.get()
            req_owner = req.user_key.get()
            is_current_user_the_owner = False

            if req_owner:
                is_current_user_the_owner = (req_owner.key.id() == user.key.id())

            if user.is_admin or is_current_user_the_owner:
                req_pair.key.delete()
                time.sleep(1)
                flash(_('request deleted correctly'), 'success')
            else:
                flash("You're not allowed!!", 'error')
        except Exception as e:
            print("/deleteRequestPair: unable to delete pair: " + e.message)

        return redirect("/viewRequest?key=" + str(req.key.id()))
    else:
        return redirect("/")
