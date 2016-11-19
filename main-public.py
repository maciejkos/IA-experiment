# -*- coding: utf-8 -*-

## TREATMENT CONDITIONS
# Flu = 49% / Cancer = 90% loss of earnings
# Effectiveness of prevention = 20 or 60 pp
# price of prevention: Flu = 13% / Cancer = 26%
# high risk group: magic number <6,10> / low risk group: magic number <1,5>
########

### Harmonia 1 was the 1st test in November 2014
# no change log (but there were changes)
### Harmonia 2 was the 2nd test in November 2014; this version
# change log: various patches including adding the number of correctly memorized numbers to a separate table and variable
# check trello for more info
# 8 March 2015 - change log. Added randomization and changed questions in RteDemo from race to spirituality. Also
# changed Ania's questions in AddABG2 from reputation to genetic tests. Finally, tons of technical updates.
# 1/27/2016 - big changes to the experiment - structure and parameters


import os
import logging
import webapp2
import jinja2
import json
import re
from time import sleep
from google.appengine.ext import db
from django.utils import simplejson
from random import randint
import random
from datetime import datetime
from datetime import timedelta

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

## Tracking

# Google Analytics - we pass ga as a parameter to individual pages

global ga
ga = '''<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-60468837-1', 'auto');
  ga('send', 'pageview');

</script>'''

##########

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Content(db.Model):
    # content is a table name - Google calls it entity
    # subject, content, created, linkid are columns in that table
    subject = db.StringProperty(required = True, indexed=False)
    content = db.TextProperty(required = True, indexed=False)
    created = db.DateTimeProperty(auto_now_add = True, indexed=False)

class Users(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty(required=False)

class ExpData(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username = db.StringProperty(required=True)
    task1n = db.StringProperty(required=False, indexed=False)
    task1a = db.StringProperty(required=False, indexed=False)
    task1c = db.StringProperty(required=False, indexed=False)

    task2n = db.StringProperty(required=False, indexed=False)
    task2a = db.StringProperty(required=False, indexed=False)
    task2c = db.StringProperty(required=False, indexed=False)

    task3n = db.StringProperty(required=False, indexed=False)
    task3a = db.StringProperty(required=False, indexed=False)
    task3c = db.StringProperty(required=False, indexed=False)

    task4n = db.StringProperty(required=False, indexed=False)
    task4a = db.StringProperty(required=False, indexed=False)
    task4c = db.StringProperty(required=False, indexed=False)

    q1 = db.StringProperty(required=False)
    q2 = db.StringProperty(required=False)

    ecus = db.StringProperty(required=False)

class ExpFinal(db.Model):
    username = db.StringProperty(required=False)
    prevention = db.StringProperty(required=False)
    preventionCost = db.StringProperty(required=False)
    error = db.StringProperty(required=False)
    ecu = db.StringProperty(required=False)
    created = db.DateTimeProperty(auto_now_add = True)

class probabilitySick(db.Model):
    username = db.StringProperty(required=False)
    probabilitySickOriginal = db.FloatProperty(required=False) # prob(sick) generated in /prev
    probabilitySickNew = db.FloatProperty(required=False) # prob(sick) - preventionEffect.. in /prev
    created = db.DateTimeProperty(auto_now_add = True)


class ExpQuestionnaires(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    # nmi1 = db.StringProperty(required=False)
    # nmi2 = db.StringProperty(required=False)
    # nmi3 = db.StringProperty(required=False)
    nmi_happy = db.StringProperty(required=False, indexed=False)
    nmi_pleasant = db.StringProperty(required=False, indexed=False)
    nmi_good = db.StringProperty(required=False, indexed=False)
    nmi_interested = db.StringProperty(required=False, indexed=False)
    ai_content = db.TextProperty(required=False)
    aic = db.TextProperty(required=False, indexed=False)
    pQuizAttempts = db.IntegerProperty(required=False)
    eQuizAttempts = db.IntegerProperty(required=False)

class ForecastDB(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    probabilityForecast = db.StringProperty(required=False, indexed=False)
    affectForecast = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesDMa(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    dm1 = db.StringProperty(required=False, indexed=False)
    dm2 = db.StringProperty(required=False, indexed=False)
    dm3 = db.StringProperty(required=False, indexed=False)
    dm4 = db.StringProperty(required=False, indexed=False)
    dm5 = db.StringProperty(required=False, indexed=False)
    dm6 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesDMb(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    dm7 = db.StringProperty(required=False, indexed=False)
    dm8 = db.StringProperty(required=False, indexed=False)
    dm9 = db.StringProperty(required=False, indexed=False)
    dm10 = db.StringProperty(required=False, indexed=False)
    dm11 = db.StringProperty(required=False, indexed=False)
    dm12 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesDMc(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    dm13 = db.StringProperty(required=False, indexed=False)
    dm14 = db.StringProperty(required=False, indexed=False)
    dm15 = db.StringProperty(required=False, indexed=False)
    dm16 = db.StringProperty(required=False, indexed=False)
    dm17 = db.StringProperty(required=False, indexed=False)
    dm18 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesDMd(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    dm19 = db.StringProperty(required=False, indexed=False)
    dm20 = db.StringProperty(required=False, indexed=False)
    dm21 = db.StringProperty(required=False, indexed=False)
    dm22 = db.StringProperty(required=False, indexed=False)
    dm23 = db.StringProperty(required=False, indexed=False)
    dm24 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesDMe(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    dm25 = db.StringProperty(required=False, indexed=False)
    dm26 = db.StringProperty(required=False, indexed=False)
    dm27 = db.StringProperty(required=False, indexed=False)
    dm28 = db.StringProperty(required=False, indexed=False)
    dm29 = db.StringProperty(required=False, indexed=False)
    dm30 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesDMf(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    dm31 = db.StringProperty(required=False, indexed=False)
    dm32 = db.StringProperty(required=False, indexed=False)
    dm33 = db.StringProperty(required=False, indexed=False)
    dm34 = db.StringProperty(required=False, indexed=False)
    dm35 = db.StringProperty(required=False, indexed=False)
    dm36 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesSOEP(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    soep1 = db.StringProperty(required=False, indexed=False)
    soep2 = db.StringProperty(required=False, indexed=False)
    soep3 = db.StringProperty(required=False, indexed=False)
    soep4 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesIMP(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)

    imp1 = db.StringProperty(required=False, indexed=False)
    imp2 = db.StringProperty(required=False, indexed=False)
    imp3 = db.StringProperty(required=False, indexed=False)
    imp4 = db.StringProperty(required=False, indexed=False)
    imp5 = db.StringProperty(required=False, indexed=False)
    imp6 = db.StringProperty(required=False, indexed=False)
    imp7 = db.StringProperty(required=False, indexed=False)
    imp8 = db.StringProperty(required=False, indexed=False)
    imp9 = db.StringProperty(required=False, indexed=False)
    imp10 = db.StringProperty(required=False, indexed=False)
    imp11 = db.StringProperty(required=False, indexed=False)
    imp12 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesLOC(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)

    loc1 = db.StringProperty(required=False, indexed=False)
    loc2 = db.StringProperty(required=False, indexed=False)
    loc3 = db.StringProperty(required=False, indexed=False)
    loc4 = db.StringProperty(required=False, indexed=False)
    loc5 = db.StringProperty(required=False, indexed=False)
    loc6 = db.StringProperty(required=False, indexed=False)
    loc7 = db.StringProperty(required=False, indexed=False)
    loc8 = db.StringProperty(required=False, indexed=False)
    loc9 = db.StringProperty(required=False, indexed=False)
    loc10 = db.StringProperty(required=False, indexed=False)
    loc11 = db.StringProperty(required=False, indexed=False)
    loc12 = db.StringProperty(required=False, indexed=False)
    loc13 = db.StringProperty(required=False, indexed=False)
    loc14 = db.StringProperty(required=False, indexed=False)
    loc15 = db.StringProperty(required=False, indexed=False)
    loc16 = db.StringProperty(required=False, indexed=False)
    loc17 = db.StringProperty(required=False, indexed=False)
    loc18 = db.StringProperty(required=False, indexed=False)
    loc19 = db.StringProperty(required=False, indexed=False)
    loc20 = db.StringProperty(required=False, indexed=False)
    loc21 = db.StringProperty(required=False, indexed=False)
    loc22 = db.StringProperty(required=False, indexed=False)
    loc23 = db.StringProperty(required=False, indexed=False)
    loc24 = db.StringProperty(required=False, indexed=False)
    loc25 = db.StringProperty(required=False, indexed=False)
    loc26 = db.StringProperty(required=False, indexed=False)
    loc27 = db.StringProperty(required=False, indexed=False)
    loc28 = db.StringProperty(required=False, indexed=False)
    loc29 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesDEMO(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)

    demo = db.StringProperty(required=False, indexed=False)
    demo1 = db.StringProperty(required=False, indexed=False)
    demo2 = db.StringProperty(required=False, indexed=False)
    demo21 = db.StringProperty(required=False, indexed=False)
    demo4 = db.StringProperty(required=False, indexed=False)
    demo5 = db.StringProperty(required=False, indexed=False)
    demo6 = db.StringProperty(required=False, indexed=False)
    demo7 = db.StringProperty(required=False, indexed=False)
    demo8 = db.StringProperty(required=False, indexed=False)
    demo9 = db.StringProperty(required=False, indexed=False)
    # demo10 = db.StringProperty(required=False, indexed=False) # not used anymore

class ExpQuestionnairesREI(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)

    rei1 = db.StringProperty(required=False, indexed=False)
    rei2 = db.StringProperty(required=False, indexed=False)
    rei3 = db.StringProperty(required=False, indexed=False)
    rei4 = db.StringProperty(required=False, indexed=False)
    rei5 = db.StringProperty(required=False, indexed=False)
    rei6 = db.StringProperty(required=False, indexed=False)
    rei7 = db.StringProperty(required=False, indexed=False)
    rei8 = db.StringProperty(required=False, indexed=False)
    rei9 = db.StringProperty(required=False, indexed=False)
    rei10 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesM(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    RteM1 = db.StringProperty(required=False, indexed=False)
    RteM2 = db.StringProperty(required=False, indexed=False)
    RteM3 = db.StringProperty(required=False, indexed=False)
    RteM4 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesPIL(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    pil1 = db.StringProperty(required=False, indexed=False)
    pil2 = db.StringProperty(required=False, indexed=False)
    pil3 = db.StringProperty(required=False, indexed=False)
    pil4 = db.StringProperty(required=False, indexed=False)
    pil5 = db.StringProperty(required=False, indexed=False)
    pil6 = db.StringProperty(required=False, indexed=False)
    pil7 = db.StringProperty(required=False, indexed=False)
    pil8 = db.StringProperty(required=False, indexed=False)
    pil9 = db.StringProperty(required=False, indexed=False)
    pil10 = db.StringProperty(required=False, indexed=False)
    pil11 = db.StringProperty(required=False, indexed=False)
    pil12 = db.StringProperty(required=False, indexed=False)
    pil13 = db.StringProperty(required=False, indexed=False)
    pil14 = db.StringProperty(required=False, indexed=False)
    pil15 = db.StringProperty(required=False, indexed=False)
    pil16 = db.StringProperty(required=False, indexed=False)
    pil17 = db.StringProperty(required=False, indexed=False)
    pil18 = db.StringProperty(required=False, indexed=False)
    pil19 = db.StringProperty(required=False, indexed=False)
    pil20 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesSELFE(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    selfe1 = db.StringProperty(required=False, indexed=False)
    selfe2 = db.StringProperty(required=False, indexed=False)
    selfe3 = db.StringProperty(required=False, indexed=False)
    selfe4 = db.StringProperty(required=False, indexed=False)
    selfe5 = db.StringProperty(required=False, indexed=False)
    selfe6 = db.StringProperty(required=False, indexed=False)
    selfe7 = db.StringProperty(required=False, indexed=False)
    selfe8 = db.StringProperty(required=False, indexed=False)
    selfe9 = db.StringProperty(required=False, indexed=False)
    selfe10 = db.StringProperty(required=False, indexed=False)

class ExpQuestionnairesBAS(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    bas1 = db.StringProperty(required=False, indexed=False)
    bas2 = db.StringProperty(required=False, indexed=False)
    bas3 = db.StringProperty(required=False, indexed=False)
    bas4 = db.StringProperty(required=False, indexed=False)
    bas5 = db.StringProperty(required=False, indexed=False)
    bas6 = db.StringProperty(required=False, indexed=False)
    bas7 = db.StringProperty(required=False, indexed=False)
    bas8 = db.StringProperty(required=False, indexed=False)
    bas9 = db.StringProperty(required=False, indexed=False)
    bas10 = db.StringProperty(required=False, indexed=False)
    bas11 = db.StringProperty(required=False, indexed=False)
    bas12 = db.StringProperty(required=False, indexed=False)
    bas13 = db.StringProperty(required=False, indexed=False)
    bas14 = db.StringProperty(required=False, indexed=False)
    bas15 = db.StringProperty(required=False, indexed=False)
    bas16 = db.StringProperty(required=False, indexed=False)
    bas17 = db.StringProperty(required=False, indexed=False)
    bas18 = db.StringProperty(required=False, indexed=False)
    bas19 = db.StringProperty(required=False, indexed=False)
    bas20 = db.StringProperty(required=False, indexed=False)
    bas21 = db.StringProperty(required=False, indexed=False)
    bas22 = db.StringProperty(required=False, indexed=False)
    bas23 = db.StringProperty(required=False, indexed=False)
    bas24 = db.StringProperty(required=False, indexed=False)
class ExpTime(db.Model):
    username = db.StringProperty(required=False)
    q1 = db.StringProperty(required=False)
    q2 = db.StringProperty(required=False)
    q3 = db.StringProperty(required=False)
    q4 = db.StringProperty(required=False)
    q5 = db.StringProperty(required=False)
    q6 = db.StringProperty(required=False)
    q7 = db.StringProperty(required=False)
    q8 = db.StringProperty(required=False)
    q9 = db.StringProperty(required=False)
    q10 = db.StringProperty(required=False)
    selectedQ = db.StringProperty(required=False)
    created = db.DateTimeProperty(auto_now_add = True)
    TEpayoff = db.FloatProperty(required=False)
    error = db.StringProperty(required=False)
    timing = db.StringProperty(required=False)

class Attempts(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    # n_attempts = db.StringProperty(required=False, indexed=False)
    # number_attempts_instructions= db.StringProperty(required=False, indexed=False)
    expQuizErrors= db.IntegerProperty(required=False, default=0, indexed=False) #experimental quiz attempts by user
    ppointQuizErrors= db.IntegerProperty(required=False, default=0, indexed=False) #percentange points attempts by user

class WrongAnswers(db.Model):
    # wrong answers from equiz are logged here
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    wrong_answers= db.StringProperty(required=False, indexed=False)

class ErrorLogs(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    errorQ2 = db.StringProperty(required=False, indexed=False)

class RevLock(db.Model):
    ''' Entries in this model are PESEL code. Users with this PESEL cannot access rev again.
    I created this to block users from changing scores of other users even if they know their PESEL.
    PESEL numbers are anonymized by another script.
    '''
    created = db.DateTimeProperty(auto_now_add = True)
    pesel = db.StringProperty(required=False)

class ExpViewer(db.Model):
    ecus = db.StringProperty(required=False)
    preventionCost = db.StringProperty(required=False)
    payoffLucky = db.FloatProperty(required=False)
    payoffUnlucky = db.FloatProperty(required=False)
    outcome = db.StringProperty(required=False)
    payoff = db.FloatProperty(required=False)
    magicNumber = db.IntegerProperty(required=False)
    HLpayoffFinal = db.StringProperty(required=False)
    username = db.StringProperty(required=False)
    timing = db.StringProperty(required=False)

class ExpHL(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username = db.StringProperty(required=False)
    q1 = db.StringProperty(required=False)
    q2 = db.StringProperty(required=False)
    q3 = db.StringProperty(required=False)
    q4 = db.StringProperty(required=False)
    q5 = db.StringProperty(required=False)
    q6 = db.StringProperty(required=False)
    q7 = db.StringProperty(required=False)
    q8 = db.StringProperty(required=False)
    q9 = db.StringProperty(required=False)
    q10 = db.StringProperty(required=False)
    q11 = db.StringProperty(required=False)
    q12 = db.StringProperty(required=False)
    q13 = db.StringProperty(required=False)
    q14 = db.StringProperty(required=False)
    q15 = db.StringProperty(required=False)
    HLpayoff = db.FloatProperty(required=False)


class AniaP1(db.Model):
    # Ania's questions page 1
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    AddABG1 = db.StringProperty(required=False, indexed=False)
    AddABG2 = db.StringProperty(required=False, indexed=False)
    AddABG3 = db.StringProperty(required=False, indexed=False)
    AddABG4 = db.StringProperty(required=False, indexed=False)
    AddABG5 = db.StringProperty(required=False, indexed=False)
    AddABG6 = db.StringProperty(required=False, indexed=False)
    AddABG7 = db.StringProperty(required=False, indexed=False)
    AddABG8 = db.StringProperty(required=False, indexed=False)
    AddABG9 = db.StringProperty(required=False, indexed=False)
    AddABG10 = db.StringProperty(required=False, indexed=False)
    AddABG11 = db.StringProperty(required=False, indexed=False)
    AddABG12 = db.StringProperty(required=False, indexed=False)
    AddABG13 = db.StringProperty(required=False, indexed=False)
    AddABG14 = db.StringProperty(required=False, indexed=False)
    AddABG15 = db.StringProperty(required=False, indexed=False)

class AniaP2(db.Model):
    ''' Final questions about interest in genetic tests, etc.'''
    created = db.DateTimeProperty(auto_now_add = True)
    username= db.StringProperty(required=False)
    AddABG16 = db.StringProperty(required=False, indexed=False)
    AddABG17 = db.StringProperty(required=False, indexed=False)
    AddABG18 = db.StringProperty(required=False, indexed=False)
    AddABG19 = db.StringProperty(required=False, indexed=False)
    AddABG20 = db.StringProperty(required=False, indexed=False)
    AddABG21 = db.StringProperty(required=False, indexed=False)
    AddABG22 = db.StringProperty(required=False, indexed=False)


class UserTreatment(db.Model):
    # stores info about each users' treatment assignment
    created = db.DateTimeProperty(auto_now_add = True)
    username = db.StringProperty(required=False)
    severity = db.StringProperty(required=False)
    prevention = db.StringProperty(required=False)
    risk = db.StringProperty(required=False)
    evaluation = db.StringProperty(required=False)

class SubjectsInTreatments(db.Model):
    ''' counts of how many subjects there are in each treatment
    '''

    treatment = db.StringProperty(required=False)
    subjectCounter = db.IntegerProperty(required=False)

class SubjectContactData(db.Model):
    # stores subjects' sensitive information
    created = db.DateTimeProperty(auto_now_add = True)
    username = db.StringProperty(required=False)
    firstName = db.StringProperty(required=False)
    middleName = db.StringProperty(required=False)
    lastName = db.StringProperty(required=False)
    city = db.StringProperty(required=False)
    zipCode = db.StringProperty(required=False)
    isStudent = db.StringProperty(required=False)

class SubjectAgreement(db.Model):
    # stores info about each users' treatment assignment
    created = db.DateTimeProperty(auto_now_add = True)
    username = db.StringProperty(required=False)
    experimentAgree = db.StringProperty(required=False)
    paypalAgree = db.StringProperty(required=False)

class RteBEDdb(db.Model):
    # stores info about binge eating disorder and BMI
    created = db.DateTimeProperty(auto_now_add = True)
    username = db.StringProperty(required=False)
    q1 = db.StringProperty(required=False)
    q2 = db.StringProperty(required=False)
    q3 = db.StringProperty(required=False)
    q4 = db.StringProperty(required=False)
    weight = db.StringProperty(required=False)
    height = db.StringProperty(required=False)


class Visited(db.Model):
    '''
    Stores if user visited /tasks, /prev and /rev. True = visited
    Used to prevent users from returning to these pages after visiting them
    '''
    username = db.StringProperty(required=False)
    prev = db.BooleanProperty(required=False, default=False)
    tasks = db.BooleanProperty(required=False, default=False)
    rev = db.BooleanProperty(required=False, default=False)
    te = db.BooleanProperty(required=False, default=False)
    rtehl = db.BooleanProperty(required=False, default=False)
class StudentsInformation(db.Model):
    # stores informatiion about *students* taking the exam - it will be used by teachers to give extra points
    created = db.DateTimeProperty(auto_now_add = True)
    username = db.StringProperty(required=False)
    firstName = db.StringProperty(required=False)
    lastName = db.StringProperty(required=False)
    teacher = db.StringProperty(required=False)
    className = db.StringProperty(required=False)
class MainPage(Handler):

    def get(self):
        # self.render_front()
        self.render("main-paypal.html", ga = ga) # or main-bank.html
        # self.render("main-bank.html", ga = ga) # or main-paypal.html

    def post(self):
        next = self.request.get("Dalej")
        if next == "yes":
            self.redirect('/phones')

class NewPost(Handler):
    def render_front(self, subject="", content="", error=""):
        contents = db.GqlQuery("SELECT * FROM Content ORDER BY created DESC")
        self.render("front.html", subject = subject, content = content, error = error, contents = contents)
    def get(self):
        self.render_front()
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        # linkid =
        if subject and content:
            a = Content(subject = subject, content = content) # creates object
            a_key = a.put() # adds it to a database // Key('Blog', id)


            self.redirect("/%d" % a_key.id())
        else:
            error = "we need both a subject and some content!"
            self.render_front(subject, content, error)

class Permalink(Handler):
    def get(self, blog_id):
        s = Content.get_by_id(int(blog_id))
        self.render("permalink.html", blogs = [s]) # this sends a list (blog entry) to permalink.html using blogs variables

def user_check(username):
    return True if username else False

def password_check(password):
    return True if password else False

def password_verify(password, verify_password):
    return True if password == verify_password else False

def unique_user(username):

    usernames = Users.all().filter('username =', username)
    return not usernames.get() # returns false if a user already exists that matches

class Pulse(Handler):
    def get(self):
        self.render("pulse.html")

    def post(self):
        # jsonstring = self.request.body
        # jsonobject = simplejson.loads(jsonstring)
        # user = self.request.get('user')
        # logging.info(user)

        username = self.request.get("user")
        # stage = self.request.get("stage")
        # logging.info("username in pulse!")
        # logging.info(username)
        task1n = self.request.get("task1n")
        # logging.info(task1n)
        task1a = self.request.get("task1a")
        task1c = self.request.get("task1c")

        task2n = self.request.get("task2n")
        task2a = self.request.get("task2a")
        task2c = self.request.get("task2c")

        task3n = self.request.get("task3n")
        task3a = self.request.get("task3a")
        task3c = self.request.get("task3c")
        # logging.info(task3c)
        task4n = self.request.get("task4n")
        task4a = self.request.get("task4a")
        task4c = self.request.get("task4c")

        q1 = self.request.get("q1")
        q2 = self.request.get("q2")

        # time = self.request.get("time")
        # localtime = self.request.get("localtime")
        ecus = self.request.get("ecus")

        # b = ExpData(username = username, stage = stage, task1n=task1n, task1a=task1a, task1c=task1c, task2n=task2n, task2a=task2a, task2c=task2c, task3n=task3n, task3a=task3a, task3c=task3c, task4n=task4n, task4a=task4a, task4c=task4c, q1 = q1, q2=q2, time = time, localtime = localtime, ecus = ecus ) # creates object
        # b = ExpData(username = username) # shorter version for tests
        b = ExpData(username = username, task1n=task1n, task1a=task1a, task1c=task1c, task2n=task2n, task2a=task2a, task2c=task2c, task3n=task3n, task3a=task3a, task3c=task3c, task4n=task4n, task4a=task4a, task4c=task4c, q1 = q1, q2 = q2, ecus = ecus ) # creates object
 # shorter version for tests
        b_key = b.put() # adds it to a database //

class Logout(Handler):
    def get(self):

        self.response.headers.add_header('Set-Cookie', 'name=; Path=/')
        self.redirect('/signup')


class Welcome(Handler):
    def get(self):

        self.render("welcome.html", ga = ga )

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/inputnumber')

class Phones(Handler):
    def get(self):

        self.render("phones.html", ga = ga )

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/inputnumber')

class Timer(Handler):
    def get(self):
            self.render("timer.html")

class Test(Handler):
    def get(self):
            self.render("test.html")

class Test1(Handler):
    def get(self):
        self.render("test1.html")

class Inputnumber(Handler):
    def get(self):
        self.render("inputnumber.html", ga = ga )
        self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % "-1")

    def post(self): # user number will be dropped in a cookie
        username = self.request.get("username")
        username=str(username)
        self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % username)
        firstName = self.request.get("firstName")
        lastName = self.request.get("lastName")
        teacher = self.request.get("teacher")
        className = self.request.get("className")

        next = self.request.get("next")

        a = Visited(username = username)
        b = StudentsInformation(username = username, firstName = firstName, lastName = lastName, teacher = teacher, className = className)

        if username.isdigit() == True:  # check if this works! make sure that username exits and is a digit before redirection! // WORKS!
            if checkPesel(username) == True:
                if HasUserFinished(username) == False: #this check that the user hasn't already finished exp
                    makeUser(username)
                    a.put()
                    b.put()
                    self.redirect('/agreement')
                else:
                    print "error in input number"
                    error = u'Osoba o tym numerze PESEL uczestniczyła już w eksperymencie.'
                    self.render("inputnumber.html", error = error)
            else:
                print "error in input number"
                error = u'Podano nieprawidłowy numer PESEL.'
                self.render("inputnumber.html", error = error)
        else:
            print "error in input number"
            error = u'Podano nieprawidłowy numer PESEL.'
            self.render("inputnumber.html", error = error)




        # print "self.__class__.__name__ === ", self.__class__.__name__

class Exp_structure(Handler):
    def get(self):
        self.render("exp_structure.html", ga = ga )

    def post(self): # user number will be dropped in a cookie
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/pinstructions')


class Pinstructions(Handler):
    def get(self):
        self.render("pinstructions.html", ga = ga )

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/pquiz1')

global error
error =""

global attempt
attempt = 0

# def attemptCount():
#     logging.info("attemptCount")
#     logging.info(error)
#     global attempt
#     global error
#     attempt = attempt + 1
error = u'Niestety, jedna lub dwie z poprzednich odpowiedzi była niepoprawna. Oto nowe zadania do rozwiązania.'


class Pquiz1(Handler):
    def get(self):
        self.render("pquiz1.html", ga = ga )

    def post(self):

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/presults')

class Pquiz2(Handler):
    def get(self):
        self.render("pquiz2.html", ga = ga, error = error)

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/presults')

class Pquiz3(Handler):
    def get(self):
        self.render("pquiz3.html", ga = ga, error = error)

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/presults')

class Pquiz4(Handler):
    def get(self):
        self.render("pquiz4.html", ga = ga, error = error)

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/presults')


global quiz


class Presults(Handler): # checks if answers to percentage points quiz were correct

    answers = {}
    def post(self):
        username = self.request.cookies.get('username', 0)
        q1 = self.request.get("q1")
        q2 = self.request.get("q2")
        quiz = self.request.get("quiz")
        q1 = str(q1)
        q2 = str(q2)
        quiz = str(quiz)
        # logging.info(type(quiz))

        pQuizAttempts = 0

        if quiz == "1":
            logging.info("in 1st if")
            answers = {"q1": "a", "q2": "a"}
        elif quiz == "2":
            logging.info("in 2 if")
            answers = {"q1": "b", "q2": "a"}
        elif quiz == "3":
            logging.info("in 3 if")
            answers = {"q1": "a", "q2": "a"}
        elif quiz == "4":
            logging.info("in 4 if")
            answers = {"q1": "b", "q2": "b"}
        else:
            answers = {}
            logging.info("ERROR!")

        logging.info(type(q1))
        logging.info(q2)
        logging.info(quiz)

        userErrors = Attempts(username = username, ppointQuizErrors = 0, expQuizErrors = 0) # here I only initialize this class.


        v = Attempts.all().filter('username = ', username) # let's check if user exists in attempts
        if not v.get(): # if doesn't exist
            userErrors.put() # add it
            sleep(0.1) # datastore needs a "second" to store data


        if q1 == answers["q1"] and q2 == answers["q2"]:
            logging.info("success!")
            n_attempts = str(attempts.giveErrorN())
            zz = Attempts(username = username, n_attempts = n_attempts)
            # zz.put()
            self.redirect('/einstructions_wait')
        else:
            logging.info("fail!")
            logging.info(attempt)
            pQuizAttempts = pQuizAttempts + 1 # legacy code
            z = ExpQuestionnaires(username = username, pQuizAttempts = pQuizAttempts) # legacy code
            # z.put()
            attempts.incrementErrorN()

            # new code below
            _id = Attempts.all().filter('username = ', username).get()
            _id = _id.key()

            currentexpQuizAttempts = Attempts.all().filter('username = ', username).get() # we get value of ppointQuizErrors
            currentexpQuizAttempts = currentexpQuizAttempts.ppointQuizErrors

            oldexpQuizAttempts = db.get(str(_id)) # db.get needs a normal key to be cast as string. if you want to print number key use entity.key().id()
            oldexpQuizAttempts.ppointQuizErrors = currentexpQuizAttempts + 1 # we update expQuizErrors by one to reflect user making an error
            updatedexpQuizAttempts = oldexpQuizAttempts
            updatedexpQuizAttempts.put()

            # end of new code

            quiz = int(quiz) +1
            if quiz > 4:
                quiz = 2 # because quiz 1 does not have an error message
            self.redirect("/pquiz%s" %quiz)

        # if next == "yes":
        #     self.redirect('/einstructions_wait')

class PresultsP(Handler):
    def get(self):
        self.render("presultsp.html")

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/einstructions_wait')

class PresultsF(Handler):
    def get(self):
        self.render("presultsf.html")

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/einstructions_wait')

class Einstructions_wait(Handler):
    def get(self):
        self.render("einstructions_wait.html", ga = ga )

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/einstructions_intro')

class Einstructions_intro(Handler):
    def get(self):
        self.render("einstructions_intro.html", ga = ga )

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/einstructions_rules1')

class Einstructions_rules1(Handler):
    def get(self):
        self.render("einstructions_rules1.html", ga = ga )

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/einstructions_rules2')

class Einstructions_rules11(Handler):
    def get(self):
        error = u'Niestety nie na wszystkie pytania odpowiedziałeś/aś poprawnie. Przeczytaj jeszcze raz instrukcje i spróbuj ponownie.'
        self.render("einstructions_rules1.html", ga = ga, error = error)

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/einstructions_rules2')

class Einstructions_rules2(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)
        forSeverity = UserTreatment.all().filter('username = ', username).get()
        forSeverity = forSeverity.severity
        print forSeverity
        severity =''
        if forSeverity.lower() == 'flu':
            severity = u'49%'
        if forSeverity.lower() == 'cancer':
            severity = u'90%'
        self.render("einstructions_rules2.html", ga = ga, severity = severity)

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            # self.redirect('/einstructions_rules3')
            self.redirect('/einstructions_rules3')
class Einstructions_rules3(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)
        forAll = UserTreatment.all().filter('username = ', username).get()
        forRisk = forAll.risk
        forSeverity = forAll.severity
        risk =''
        if forRisk.lower() == 'low_risk':
            risk = u'niższe'
        if forRisk.lower() == 'high_risk':
            risk = u'wyższe'

        severity =''
        if forSeverity.lower() == 'flu':
            severity = u'49%'
        if forSeverity.lower() == 'cancer':
            severity = u'90%'
        self.render("einstructions_rules3.html", ga = ga, risk = risk, severity = severity)

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/einstructions_rules4')

class Einstructions_rules4(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)
        forAll = UserTreatment.all().filter('username = ', username).get()
        forPreventionEffectiveness = forAll.prevention
        forPreventionPrice = forAll.severity # because price also depends on severity
        forSeverity = forAll.severity

        preventionPrice =''
        preventionEffectiveness =''

        if forPreventionEffectiveness.lower() == 'ineffective':
            preventionEffectiveness = u'20 punktów procentowych'
            if forPreventionPrice.lower() == 'cancer':
                preventionPrice = u'26%'
            elif forPreventionPrice.lower() == 'flu':
                preventionPrice = u'13%'
            else:
                print "ERROR  1 in if forPreventionEffectiveness.lower() == 'ineffective'"
                print "Assumed preventionPrice = u'26%'"
                print "username = ", username
                print "forPreventionPrice.lower() = ", forPreventionPrice.lower()
                preventionPrice = u'26%'

        elif forPreventionEffectiveness.lower() == 'effective':
            preventionEffectiveness = u'60 punktów procentowych'
            if forPreventionPrice.lower() == 'cancer':
                preventionPrice = u'26%'
            elif forPreventionPrice.lower() == 'flu':
                preventionPrice = u'13%'
            else:
                print "ERROR  2 in if forPreventionEffectiveness.lower() == 'ineffective'"
                print "Assumed preventionPrice = u'26%'"
                print "username = ", username
                print "forPreventionPrice.lower() = ", forPreventionPrice.lower()
                preventionPrice = u'26%'

        else:
            print "ERROR  3 in if forPreventionEffectiveness.lower() == 'ineffective'"
            print "Assumed preventionPrice = u'26%'"
            print "Assumed preventionEffectiveness = u'20 punktów procentowych'"
            print "username = ", username
            print "forPreventionPrice.lower() = ", forPreventionEffectiveness.lower()
            preventionEffectiveness = u'20 punktów procentowych'
            preventionPrice = u'26%'
            # TODO add all of errors in this class to database somewhere. Maybe create a function that will accept error
            # as a parameter and add all errors with usernames and time to database?
        severity =''
        if forSeverity.lower() == 'flu':
            severity = u'49%'
        if forSeverity.lower() == 'cancer':
            severity = u'90%'

        self.render("einstructions_rules4.html", ga = ga, preventionEffectiveness = preventionEffectiveness, preventionPrice = preventionPrice, severity = severity)

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/einstructions_rules5')

class Einstructions_rules5(Handler):
    def get(self):
        self.render("einstructions_rules5.html", ga = ga )

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/equiz')

class Equiz(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)
        forAll = UserTreatment.all().filter('username = ', username).get()

        forSeverity = forAll.severity
        severity =''
        if forSeverity.lower() == 'flu':
            severity = u'49%'
        if forSeverity.lower() == 'cancer':
            severity = u'90%'

        forRisk = forAll.risk
        risk =''
        if forRisk.lower() == 'low_risk':
            risk = u'niższe'
            prefix = u'nie stracę'
        if forRisk.lower() == 'high_risk':
            risk = u'wyższe'
            prefix = u'stracę'

        self.render("equiz.html", ga = ga, severity = severity, risk = risk, prefix = prefix)

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/eresults')

class Eresults(Handler):
    def get(self):
        self.render("eresults.html")
    def post(self):
        q1 = self.request.get("q1")
        q2 = self.request.get("q2")
        q3 = self.request.get("q3")
        q4 = self.request.get("q4")
        q5 = self.request.get("q5")
        quiz = self.request.get("quiz")
        q1 = str(q1)
        q2 = str(q2)
        q3 = str(q3)
        q4 = str(q4)
        q5 = str(q5)
        quiz = str(quiz)
        username = self.request.cookies.get('username', 0)
        # logging.info(type(quiz))
        answers = {"q1": "b", "q2": "c", "q3":"a", "q4":"a", "q5":"b"}

        if quiz == "equiz":
            logging.info("equiz")

        else:
            answers = {}
            logging.info("equiz ERROR!")

        logging.info(type(q1))
        logging.info(q2)
        logging.info(quiz)
        eQuizAttempts = 0

        if q1 == answers["q1"] and q2 == answers["q2"] and q3 == answers["q3"] and q4 == answers["q4"] and q5 == answers["q5"]:
            logging.info("equiz success!")
            number_attempts_instructions = str(attempts_instructions.giveErrorN())
            n_attempts = str(attempts.giveErrorN())
            zzz = Attempts(username = username, attempts = n_attempts, number_attempts_instructions = number_attempts_instructions)
            # zzz.put()
            self.redirect('/nmi_instructions')
        else:
            logging.info("equiz fail!")
            error = u'Niestety nie na wszystkie pytania odpowiedziałeś/aś poprawnie. Przeczytaj jeszcze raz instrukcje i spróbuj ponownie.'
            eQuizAttempts = eQuizAttempts + 1 #TODO this line can probably get removed
            attempts_instructions.incrementErrorN()

            # here I log wrong answers
            wrong_answers = {}
            if q1 != answers["q1"]: wrong_answers['q1'] = q1;
            if q2 != answers["q2"]: wrong_answers['q2'] = q2;
            if q3 != answers["q3"]: wrong_answers['q3'] = q3;
            if q4 != answers["q4"]: wrong_answers['q4'] = q4;
            if q5 != answers["q5"]: wrong_answers['q5'] = q5;
            wrong_answers_json = json.dumps(wrong_answers, sort_keys=True)
            wrongs = WrongAnswers(username = username, wrong_answers = wrong_answers_json)
            wrongs.put()

            # legacy code
            z = ExpQuestionnaires(username = username, eQuizAttempts = eQuizAttempts)
            # z.put()
            # legacy code end
            # self.render("/einstructions_rules1.html", error = error)

            # new code below

            _id = Attempts.all().filter('username = ', username).get()
            _id = _id.key()

            currentexpQuizAttempts = Attempts.all().filter('username = ', username).get() # we get value of ppointQuizErrors
            currentexpQuizAttempts = currentexpQuizAttempts.expQuizErrors
            print "currentexpQuizAttempts", currentexpQuizAttempts

            oldexpQuizAttempts = db.get(str(_id)) # db.get needs a normal key to be cast as string. if you want to print number key use entity.key().id()
            oldexpQuizAttempts.expQuizErrors = currentexpQuizAttempts + 1 # we update expQuizErrors by one to reflect user making an error
            updatedexpQuizAttempts = oldexpQuizAttempts
            updatedexpQuizAttempts.put()

            # end of new code

            self.redirect('/einstructions_rules11')

        # if next == "yes":
        #     self.redirect('/einstructions_wait')
    # def post(self):
    #     next = self.request.get("next")
    #     if next == "yes":
    #         self.redirect('/nmi')

class Nmi_instructions(Handler):
    def get(self):
        self.render("nmi_instructions.html", ga = ga )

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            # self.redirect('/nmi_read')
            self.redirect('/ai')

class Nmi_read(Handler):
    def get(self):
        self.render("nmi_read.html", ga = ga )

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/nmi_questions')

class Nmi_questions(Handler):
    def get(self):
        self.render("nmi_questions.html", ga = ga )

    def post(self):
        # nmi1 = self.request.get("ch11")
        # nmi2 = self.request.get("ch12")
        # nmi3 = self.request.get("ch13")
        nmi_happy = self.request.get("Happy")
        nmi_pleasant = self.request.get("Pleasant")
        nmi_good = self.request.get("Good")
        nmi_interested = self.request.get("Interested")
        username = self.request.cookies.get('username', 0)
        # logging.info("Happy")
        # logging.info(Happy)
        # logging.info("Pleasant")
        # logging.info(Pleasant)
        # logging.info("Good")
        # logging.info(Good)
        # logging.info("Interested")
        # logging.info(Interested)
        # nmi = ExpQuestionnaires(username = username, nmi1 = nmi1, nmi2 = nmi2, nmi3 = nmi3, nmi_happy = nmi_happy, nmi_pleasant = nmi_pleasant, nmi_good = nmi_good, nmi_interested = nmi_interested)
        nmi = ExpQuestionnaires(username = username, nmi_happy = nmi_happy, nmi_pleasant = nmi_pleasant, nmi_good = nmi_good, nmi_interested = nmi_interested)
        nmi.put()


        next = self.request.get("next")
        if next == "yes":
            # self.redirect('/ai')
            self.redirect('/exp_structure')

class Nmic(Handler):
    def get(self):
        self.render("nmic.html", ga = ga )

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/ai')

class Ai(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)
        forAll = UserTreatment.all().filter('username = ', username).get()
        forEvaluation = forAll.evaluation
        question =''
        if forEvaluation.lower() == 'analytical':
            question = u'Jeżeli planujesz przyszły zakup, co powinieneś brać pod uwagę, żeby mieć pewność, że będzie to odpowiedni wybór?'
        if forEvaluation.lower() == 'emotional':
            question = u'Gdy w przeszłości dokonywałeś zakupu, jakie czynniki upewniły Cię, że Twój wybór był trafny?'

        self.render("ai.html", ga = ga, question = question)

    def post(self):
        ai_content = self.request.get("content")
        username = self.request.cookies.get('username', 0)

        ai = ExpQuestionnaires(username = username, ai_content = ai_content)
        ai.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/aic')

class Aic(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)
        forAll = UserTreatment.all().filter('username = ', username).get()
        forEvaluation = forAll.evaluation
        question =''
        if forEvaluation.lower() == 'analytical':
            question = u'Od czego będzie zależeć Twoja decyzja?'
        if forEvaluation.lower() == 'emotional':
            question = u'Od czego zależała Twoja decyzja?'

        self.render("aic.html", ga = ga, question = question)

    def post(self):
        aic = self.request.get("aic")
        username = self.request.cookies.get('username', 0)

        aic = ExpQuestionnaires(username = username, aic = aic)
        aic.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/forecast')

class Forecast(Handler):
    def get(self):
        self.render("forecast.html", ga = ga)

    def post(self):
        probabilityForecast = self.request.get("probabilityForecast")
        affectForecast = self.request.get("affectForecast")
        username = self.request.cookies.get('username', 0)

        forecasts = ForecastDB(username = username, probabilityForecast = probabilityForecast, affectForecast = affectForecast)
        forecasts.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/tasks_instructions')


class Tasks_instructions(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)
        forAll = UserTreatment.all().filter('username = ', username).get()
        forRisk = forAll.risk
        risk =''
        if forRisk.lower() == 'low_risk':
            risk = u'niższe'
        if forRisk.lower() == 'high_risk':
            risk = u'wyższe'

        forSeverity = forAll.severity
        print forSeverity
        severity =''
        if forSeverity.lower() == 'flu':
            severity = u'49%'
        if forSeverity.lower() == 'cancer':
            severity = u'90%'
        self.render("tasks_instructions.html", ga = ga, risk = risk, severity = severity)

    def post(self):
        Terror=""
        checkbox = self.request.get("checkbox")
        next = self.request.get("next")

        if next == "yes" and checkbox == "Yes":
            self.redirect('/tasks')
        else:
            Terror = u'Bez potwierdzenia, że żadne informacje nie będą notowane podczas eksperymentu, kontynuacja badania jest niemożliwa.'
            self.render("tasks_instructions.html", ga = ga, Terror = Terror)
class Tasks(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)
        redirects = {"tasks": "/prev", "prev":"/te", "te":"/RteHL","RteHL":"/RteDM1", "rev":"/thankyou"}
        handlerName = self.__class__.__name__
        whereToRedirect = redirects[handlerName.lower()]

        # I disabled the below because if user refreshes the page than he is redirected to prev without
        # seeing q1 and q2 and with max ecus.
        # I should rethink this in the future because now it is possible to retry /tasks
        #
        # OK, so I thought about that and decided to check if /tasks  was visited BUT I will flip tasks to visited, on
        # /prev page. So check that handler.

        # If tasks was visited,, it will forward to /prev
        # if visited(username, handlerName) == True: # checks if it was visited earlier by the user
        #     print "VISITED!!!!!"
        #     self.redirect(whereToRedirect)
        # elif visited(username, self.__class__.__name__) == False:
        #     print "NOT VISITED!!!!!"
        #     pass

        # experiment2c - 2 digits, cancer
        # experiment2f - 2 digits, flu
        # experiment7c - 7 digits, cancer
        # experiment7f - 7 digits, flu

        forAll = UserTreatment.all().filter('username = ', username).get()
        forEvaluation = forAll.evaluation
        forSeverity = forAll.severity

        # here I construct variable that will change html to redirect to different javascripts depending on
        # what treatment condition the subject is in
        experiment = u''
        if forEvaluation.lower() == 'analytical':
            experiment = u'2'
        if forEvaluation.lower() == 'emotional':
            experiment = u'7'
        if forSeverity.lower() == 'flu':
            experiment = experiment + u'f'
        if forSeverity.lower() == 'cancer':
            experiment = experiment + u'c'
        # print "experiment = ", experiment
        # experiment = u'2f-test'
        print "experiment", experiment
        print "forSeverity.lower()", forSeverity.lower()

        self.render("tasks.html", ga = ga, exp = experiment)

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/prev')

def getQ2(username):
    # get_q2 = db.GqlQuery("SELECT q2 FROM ExpData WHERE q2 != '-1' AND username =:1", 'Ania')
    # logging.info("get_q2 = ")
    # logging.debug(get_q2)

    # for item in get_q2:
    #     logging.info("item in get_q2 = ")
    #     logging.debug(item)

    # logging.info("get_q2.get() = ")
    # logging.debug(get_q2)


    # fetched_q2 = get_q2.q2
    # get_q2 = ExpData.all().filter('username =', username)

    # here we check what was the answer to question 2, i.e., if the user wants to know his probability

    get_q2 = ExpData.all()
    get_q2.filter('username =', username)
    # print "username ==", username
    get_q2.filter('q2 !=', "-1")
    get_q2.filter('q2 !=', None)
    q2_result = get_q2.get()
    # print "q2_result = ", q2_result


    counter = 0
    for item in get_q2:
        # logging.info("item in get_q2 = ")
        # logging.debug(item.q2)
        counter +=1
        # logging.debug(counter)


    # logging.info("q2_result = ")
    # logging.debug(q2_result.q2)

    # # fetched_q2 = get_q2.q2
    # logging.info("I am in getQ2")
    # logging.debug(fetched_q2)
    # # logging.debug(password)
    # # logging.debug(username)
    # if fetched_q2 == 1: # if they want to see info
    #     return True
    # elif fetched_q2 == 0: # they DON'T want info
    #     return False
    # else:
    #     logging.info("ERROR in getQ2")
    #     return None

    # TODO remove try/except
    # this is *very* sloppy but I sometimes get an error saying "AttributeError: 'NoneType' object has no attribute 'q2'"
    # I suspect this happens when they don't answer q2 in /tasks but I cannot replicate it
    # so the except clause defaults to None

    # if hasattr(q2_result, "q2"):
    #     print "q2 SUCCESS"
    # else:
    #     print "q2 NOT SUCCESS"
    try:

        if q2_result.q2 == "tak": # if they want to see info
            logging.info("TRUE")
            return True
        elif q2_result.q2 == "nie": # they DON'T want info
            logging.info("FALSE")
            return False

    except AttributeError: # this means that subject didn't answer q2, so attribute q2 doesn't exist
            logging.info("ERROR in getQ2")
            errorQ2 = 'Yes'
            a = ErrorLogs(username = username, errorQ2 = errorQ2)
            a.put()
            return None
    except:
        errorQ2 = 'Yes but error not attribute error'
        a = ErrorLogs(username = username, errorQ2 = errorQ2)
        a.put()
        return None

def getECU(username):
    logging.info("username in getECU")
    logging.info(username)
    ecuData = ExpData.all()
    ecuData.filter('username =', username)
    ecuData.filter('ecus !=', None)
    ecuData.order('ecus')
    ecuCurrent = ecuData.get()
    logging.info("ecuCurrent.ecus")
    logging.info(ecuCurrent.ecus)
    return ecuCurrent.ecus

class Prev(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)
        redirects = {"tasks": "/prev", "prev":"/te", "te":"/RteHL","RteHL":"/RteDM1", "rev":"/thankyou"}
        handlerName = self.__class__.__name__
        whereToRedirect = redirects[handlerName.lower()]
        if visited(username, handlerName) == True: # checks if it was visited earlier by the user
            print "VISITED!!!!!"
            self.redirect(whereToRedirect)
        elif visited(username, self.__class__.__name__) == False:
            print "NOT VISITED!!!!!"
            pass

        # to understand why the below is here - check comment in /tasks handler

        if visited(username, "Tasks") == True: # I basically flip Tasks to vistied and nothing else
            # print "VISITED!!!!!"
            # self.redirect("/tasks")
            pass
        # elif visited(username, "Tasks") == False:
            # print "NOT VISITED!!!!!"
            # pass


        forAll = UserTreatment.all().filter('username = ', username).get()
        forSeverity = forAll.severity
        forRisk = forAll.risk
        forPreventionEffectiveness = forAll.prevention
        forPreventionPrice = forAll.severity # because price also depends on severity

        self.response.headers.add_header('Set-Cookie', 'experimentdata=%s; Path=/' % "030301090801") #hardcoded number to find those who want to take the experiment again

        logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        logging.info(">>>>>>> name = ")
        logging.info(username)
        # print "self.__class__.__name__ === ", self.__class__.__name__

        # pp, pp_price depend on treatment condition
        # pp_price_user depends of pp, pp_price and how many ECUS users has

        if forPreventionEffectiveness.lower() == 'ineffective':
            preventionEffectiveness = u'20'
            if forPreventionPrice.lower() == 'cancer':
                preventionPrice = u'26'
            elif forPreventionPrice.lower() == 'flu':
                preventionPrice = u'13'
            else:
                print "ERROR  1 in if forPreventionEffectiveness.lower() == 'ineffective'"
                print "Assumed preventionPrice = u'26%'"
                print "username = ", username
                print "forPreventionPrice.lower() = ", forPreventionPrice.lower()
                preventionPrice = u'26'

        elif forPreventionEffectiveness.lower() == 'effective':
            preventionEffectiveness = u'60'
            if forPreventionPrice.lower() == 'cancer':
                preventionPrice = u'26'
            elif forPreventionPrice.lower() == 'flu':
                preventionPrice = u'13'
            else:
                print "ERROR  2 in if forPreventionEffectiveness.lower() == 'ineffective'"
                print "Assumed preventionPrice = u'26%'"
                print "username = ", username
                print "forPreventionPrice.lower() = ", forPreventionPrice.lower()
                preventionPrice = u'26'

        else:
            print "ERROR  3 in if forPreventionEffectiveness.lower() == 'ineffective'"
            print "Assumed preventionPrice = u'26%'"
            print "Assumed preventionEffectiveness = u'20 punktów procentowych'"
            print "username = ", username
            print "forPreventionPrice.lower() = ", forPreventionEffectiveness.lower()
            preventionEffectiveness = u'20'
            preventionPrice = u'26'

        # pp = u'20' # or "60"
        pp = preventionEffectiveness
        pp_price = preventionPrice
        preventionPriceAsFraction = float(preventionPrice)/100
        pp_price_user = float(getECU(username))/10 * (preventionPriceAsFraction)
        current_ecus = float(getECU(username))/10
        print "current_ecus", current_ecus
        print "pp", pp
        print "pp_price", pp_price
        print "preventionPrice", preventionPrice
        print "int(preventionPrice)/100", int(preventionPrice)/100
        print "preventionPriceAsFraction", preventionPriceAsFraction
        print "pp_price_user", pp_price_user

        # probability of sick (or unlucky, or magic number) is generated below
        prevention = int(pp)

        if forRisk.lower() == 'low_risk':
                probabilitySi = float(random.randrange(240,255))/10 # I save it to db a few lines below as probabilitySickOriginal

        if forRisk.lower() == 'high_risk':
                probabilitySi = float(random.randrange(745,760))/10 # I save it to db a few lines below as probabilitySickOriginal
        probabilityNew = probabilitySi - prevention
        if probabilityNew < 0: probabilityNew = 0 # otherwise we would have negative probability

        pSick = probabilitySick(username = username, probabilitySickOriginal = float(probabilitySi), probabilitySickNew = float(probabilityNew))
        pSick.put()

        message = ""
        if getQ2(username) == True: # they want to know the answer
            if forRisk.lower() == 'low_risk':
                # probabilityS = float(random.randrange(220,250))/10 # I save it to db a few lines below
                probabilityNew = probabilitySi - prevention
                if probabilityNew < 0: probabilityNew = 0
                probabilityS = unicode(str(probabilitySi))

                # message =  u'probabilitySick' # jinja2 requires unicode strings to have u' in front
                message = u'Twoje prawdopodobieństwo utraty pieniędzy to'
                message2 = u'%' # jinja2 requires unicode strings to have u' in front
                message3 = u'Po zakupie, nowa wartość Twojego prawdopodobieństwa utraty pieniędzy wynosić będzie'
                message4 = u'%'
            if forRisk.lower() == 'high_risk':
                # probabilityS = float(random.randrange(730,760))/10 # I save it to db a few lines below
                probabilityNew = probabilitySi - prevention
                if probabilityNew < 0: probabilityNew = 0
                probabilityS = unicode(str(probabilitySi))
                # message =  u'probabilitySick'
                message = u'Twoje prawdopodobieństwo utraty pieniędzy to' # jinja2 requires unicode strings to have u' in front
                message2 = u'%'
                message3 = u'Po zakupie, nowa wartość Twojego prawdopodobieństwa utraty pieniędzy wynosić będzie'
                message4 = u'%'
            # message = u'Wartość Twojego prawdopodobieństwa bycia pechowcem znajduje się w przedziale od 50% do 100%.' # jinja2 requires unicode strings to have u' in front

            # TD = show message1 or message2 depending on a situation
            # message1 = u'Wartość Twojego prawdopodobieństwa bycia pechowcem znajduje się w przedziale od 0% do 50%.' # jinja2 requires unicode strings to have u' in front
            # message2 = u'Wartość Twojego prawdopodobieństwa bycia pechowcem znajduje się w przedziale od 50% do 100%.' # jinja2 requires unicode strings to have u' in front

        elif getQ2(username) == False: # they do not want to know the answer
            message = ""
            message2 = ""
            probabilityS = ""
            message3 = ""
            probabilityNew =""
            message4 = ""
        elif getQ2(username) == None: # they did not answer
            message = ""
            message2 = ""
            probabilityS = ""
            message3 = ""
            probabilityNew =""
            message4 = ""
            print "getQ2(username) == None"
        else:
            logging.info("ERROR getQ2 returned something unexpected")

        self.render("prev.html", message = message, probabilityS = probabilityS, message2 = message2, message3 = message3, message4 = message4, probabilityNew = probabilityNew, pp = pp, pp_price = pp_price, pp_price_user = pp_price_user, current_ecus = current_ecus, ga = ga)
        # self.render("prev.html")

    def post(self):
        username = self.request.cookies.get('username', 0)
        next = self.request.get("next")
        prev = self.request.get("prev")
        prev = str(prev)
        # username = str(username)
        prevCostToDatastore = "0"
        # print "ECU TYPE ==== "
        # print(type(getECU()))
        obj = ExpFinal()

        # logging.info(getECU())
        # logging.info(float(getECU()))
        # logging.info(round(float(getECU())))
        # logging.info(str(round(float(getECU()))))
        forAll = UserTreatment.all().filter('username = ', username).get()
        forSeverity = forAll.severity
        preventionPrice = 0
        if forSeverity.lower() == 'cancer':
            preventionPrice = 0.26
        elif forSeverity.lower() == 'flu':
            preventionPrice = 0.13

        if prev == "yes":
           prevCostToDatastore = float(getECU(username)) * (preventionPrice)
           prevCostToDatastore = str(round(prevCostToDatastore))
           obj.username = username
           obj.prevention = '1'
           obj.preventionCost = prevCostToDatastore
           obj.ecu = str(round(float(getECU(username))))
           obj.put()
           logging.info("PREV = YES!")
        elif prev == "no":
            obj.username = username
            obj.prevention = '0'
            obj.preventionCost = '0'
            obj.ecu = str(getECU(username))
            obj.put()
        else:
            prevCostToDatastore = float(getECU(username)) * (preventionPrice)
            prevCostToDatastore = str(round(prevCostToDatastore))
            obj.username = username
            obj.prevention = '1'
            obj.preventionCost = prevCostToDatastore
            obj.ecu = str(round(float(getECU(username))))
            obj.error = "no answer was selected, defaulted to YES"
            obj.put()
            logging.info("PREV - no answer selected!")
        if next == "yes":
            self.redirect('/te')

class Te(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)

        redirects = {"tasks": "/prev", "prev":"/te", "te":"/RteHL","RteHL":"/RteDM1", "rev":"/thankyou"}
        handlerName = self.__class__.__name__
        whereToRedirect = redirects[handlerName.lower()]
        if visited(username, handlerName) == True: # checks if it was visited earlier by the user
            print "VISITED!!!!!"
            self.redirect(whereToRedirect)
        elif visited(username, self.__class__.__name__) == False:
            print "NOT VISITED!!!!!"
            pass

        self.render("te.html", ga = ga )

    def post(self):
        username = self.request.cookies.get('username', 0)
        q1 = self.request.get("i51")
        q2 = self.request.get("i52")
        q3 = self.request.get("i53")
        q4 = self.request.get("i54")
        q5 = self.request.get("i55")
        q6 = self.request.get("i56")
        q7 = self.request.get("i57")
        q8 = self.request.get("i58")
        q9 = self.request.get("i59")
        q10 = self.request.get("i510")
        next = self.request.get("next")

        teAnswers = {"q1" : q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5, "q6": q6, "q7": q7, "q8": q8, "q9": q9, "q10": q10}
        randomTeAnswer = random.choice(teAnswers.keys())
        selectedQ = str(randomTeAnswer)

        logging.info("randomTeAnswer")
        logging.info(randomTeAnswer)
        logging.info(teAnswers[randomTeAnswer])
        error = ""

        if (q1 and q2 and q3 and q4 and q5 and q6 and q7 and q8 and q9 and q10):
            error =""

            if teAnswers[randomTeAnswer] == "2": # they want to wait
                teGuaranteedPayoffMultipliers = {"q1": 1.0,"q2": 1.1,"q3": 1.2,"q4": 1.3,"q5": 1.4,"q6": 1.5,"q7": 1.6,"q8": 1.7,"q9": 1.8,"q10": 1.9}
                TEpayoff = float(teGuaranteedPayoffMultipliers[randomTeAnswer])
                timing = "later"
                logging.info("TEpayoff")
                logging.info(TEpayoff)
            elif teAnswers[randomTeAnswer] == "1": # they want to be paid now
                TEpayoff = float(1.0)
                timing = "now"
                logging.info("TEpayoff")
                logging.info(TEpayoff)

            else:
                TEpayoff = float(1.0)
                error = "ERROR in if in TEpayoff"
                timing = "error"
                logging.info("ERROR TEpayoff")
        else:
            TEpayoff = float(1.0)
            # _error = -1
            timing = "error - one answer not selected"
            logging.info("TE - one answer not selected")
            error = u'Nie zaznaczono jednej lub więcej odpowiedzi. Proszę spróbować ponownie.'

        teDone = ExpTime(username = username, q1 = q1, q2 = q2, q3 = q3, q4 = q4, q5 = q5, q6 = q6, q7 = q7, q8 = q8, q9 = q9, q10 = q10, selectedQ = selectedQ, TEpayoff = TEpayoff, error = error, timing = timing)
        teDone.put()


        if next == "yes" and error == "":
            self.redirect('/RteHL')
        else:
            self.render("te.html", ga = ga, error = error)


class RteHL(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)
        redirects = {"tasks": "/prev", "prev":"/te", "te":"/RteHL","rtehl":"/RteDM1", "rev":"/thankyou"}
        handlerName = self.__class__.__name__
        whereToRedirect = redirects[handlerName.lower()]
        if visited(username, handlerName) == True: # checks if it was visited earlier by the user
            print "VISITED!!!!!"
            self.redirect(whereToRedirect)
        elif visited(username, self.__class__.__name__) == False:
            print "NOT VISITED!!!!!"
            pass

        self.render("RteHL.html", ga = ga )

    def post(self):
        username = self.request.cookies.get('username', 0)
        q1 = self.request.get("RteHL1")
        q2 = self.request.get("RteHL2")
        q3 = self.request.get("RteHL3")
        q4 = self.request.get("RteHL4")
        q5 = self.request.get("RteHL5")
        q6 = self.request.get("RteHL6")
        q7 = self.request.get("RteHL7")
        q8 = self.request.get("RteHL8")
        q9 = self.request.get("RteHL9")
        q10 = self.request.get("RteHL10")
        q11 = self.request.get("RteHL11")
        q12 = self.request.get("RteHL12")
        q13 = self.request.get("RteHL13")
        q14 = self.request.get("RteHL14")
        q15 = self.request.get("RteHL15")
        next = self.request.get("next")

        HLerror = ""

        foo = {"q1" : q1, "q2": q2, "q3": q3, "q4": q4, "q5": q5, "q6": q6, "q7": q7, "q8": q8, "q9": q9, "q10": q10, "q11": q11,"q12": q12,"q13": q13,"q14": q14,"q15": q15}
        randomHL = random.choice(foo.keys())
        logging.info("randomHL")
        logging.info(randomHL)
        logging.info(foo[randomHL])
        HLpayoff = 0.01
        if (q1 and q2 and q3 and q4 and q5 and q6 and q7 and q8 and q9 and q10):
            HLerror = ""

            if foo[randomHL] == "2": # what value to add? create another dict or list with values from HL html file
                HLfixedpayoffs = {"q1": 0.25,"q2": 0.5,"q3":  0.75,"q4":  1,"q5":  1.25,"q6":  1.5,"q7":  1.75,"q8":  2.00,"q9":  2.25,"q10":  2.5,"q11":  2.75,"q12":  3,"q13":  3.25,"q14":  3.5,"q15":  3.75}
                HLpayoff = float(HLfixedpayoffs[randomHL])
                logging.info("HLpayoff")
                logging.info(HLpayoff)

            elif foo[randomHL] == "1": # get a random flip coin and give either 4 or 0 dukatów
                HLpayoff = float(random.choice([4,0]))
                logging.info("RANDOM!")
                logging.info(HLpayoff)
            else:
                logging.info("ERROR in RANDOMHL")
                HLpayoff = -1.000

                # get a random flip coin and give either 4 or 0 dukatów
        else:
            HLpayoff = -1.000
            # _error = -1

            logging.info("HL - one answer not selected")
            HLerror = u'Nie zaznaczono jednej lub więcej odpowiedzi. Proszę spróbować ponownie.'




        d = ExpHL(username = username, q1 = q1, q2 = q2, q3 = q3, q4 = q4, q5 = q5, q6 = q6, q7 = q7, q8 = q8, q9 = q9, q10 = q10, q11 = q11, q12 = q12, q13 = q13, q14 = q14, q15 = q15, HLpayoff = HLpayoff)
        d.put()


        if next == "yes" and HLerror == "":
            self.redirect('/RteDM1')
        else:
            self.render("RteHL.html", ga = ga , HLerror = HLerror)

class RteDM1(Handler):
    def get(self):
        self.render("RteDM1.html", ga = ga )

    def post(self):
        dm1 = self.request.get("DM1")
        dm2 = self.request.get("DM2")
        dm3 = self.request.get("DM3")
        dm4 = self.request.get("DM4")
        dm5 = self.request.get("DM5")
        dm6 = self.request.get("DM6")
        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesDMa(username = username, dm1 = dm1, dm2 = dm2, dm3 = dm3, dm4 = dm4, dm5 = dm5, dm6 = dm6)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteDM2')

class RteDM2(Handler):
    def get(self):
        self.render("RteDM2.html", ga = ga )

    def post(self):
        dm7 = self.request.get("DM7")
        dm8 = self.request.get("DM8")
        dm9 = self.request.get("DM9")
        dm10 = self.request.get("DM10")
        dm11 = self.request.get("DM11")
        dm12 = self.request.get("DM12")
        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesDMb(username = username, dm7 = dm7, dm8 = dm8, dm9 = dm9, dm10 = dm10, dm11 = dm11, dm12 = dm12)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteDM3')

class RteDM3(Handler):
    def get(self):
        self.render("RteDM3.html", ga = ga )

    def post(self):
        dm13 = self.request.get("DM13")
        dm14 = self.request.get("DM14")
        dm15 = self.request.get("DM15")
        dm16 = self.request.get("DM16")
        dm17 = self.request.get("DM17")
        dm18 = self.request.get("DM18")

        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesDMc(username = username, dm13 = dm13, dm14 = dm14, dm15 = dm15, dm16 = dm16, dm17 = dm17, dm18 = dm18)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteDM4')

class RteDM4(Handler):
    def get(self):
        self.render("RteDM4.html", ga = ga )

    def post(self):
        dm19 = self.request.get("DM19")
        dm20 = self.request.get("DM20")
        dm21 = self.request.get("DM21")
        dm22 = self.request.get("DM22")
        dm23 = self.request.get("DM23")
        dm24 = self.request.get("DM24")

        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesDMd(username = username, dm19 = dm19, dm20 = dm20, dm21 = dm21, dm22 = dm22, dm23 = dm23, dm24 = dm24)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteDM5')

class RteDM5(Handler):
    def get(self):
        self.render("RteDM5.html", ga = ga )

    def post(self):
        dm25 = self.request.get("DM25")
        dm26 = self.request.get("DM26")
        dm27 = self.request.get("DM27")
        dm28 = self.request.get("DM28")
        dm29 = self.request.get("DM29")
        dm30 = self.request.get("DM30")

        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesDMe(username = username, dm25 = dm25, dm26 = dm26, dm27 = dm27, dm28 = dm28, dm29 = dm29, dm30 = dm30)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteDM6')

class RteDM6(Handler):
    def get(self):
        self.render("RteDM6.html", ga = ga )

    def post(self):
        dm31 = self.request.get("DM31")
        dm32 = self.request.get("DM32")
        dm33 = self.request.get("DM33")
        dm34 = self.request.get("DM34")
        dm35 = self.request.get("DM35")
        dm36 = self.request.get("DM36")

        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesDMf(username = username, dm31 = dm31, dm32 = dm32, dm33 = dm33, dm34 = dm34, dm35 = dm35, dm36 = dm36)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteSOEP')

class RteSOEP(Handler):
    def get(self):
        self.render("RteSOEP.html", ga = ga )

    def post(self):
        soep1 = self.request.get("RteSOEP1")
        soep2 = self.request.get("RteSOEP2")
        soep3 = self.request.get("RteSOEP3")
        soep4 = self.request.get("RteSOEP4")

        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesSOEP(username = username, soep1 = soep1, soep2 = soep2, soep3 = soep3, soep4 = soep4)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteM')

class RteM(Handler):
    def get(self):
        self.render("RteM.html", ga = ga )

    def post(self):
        RteM1 = str(self.request.get("RteM1", allow_multiple=True))
        RteM2 = str(self.request.get("RteM2", allow_multiple=True))
        RteM3 = str(self.request.get("RteM3", allow_multiple=True))
        RteM4 = str(self.request.get("RteM4", allow_multiple=True))


        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesM(username = username, RteM1 = RteM1, RteM2 = RteM2, RteM3 = RteM3, RteM4 = RteM4)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteLOC')

class RteLOC(Handler):
    def get(self):
        self.render("RteLOC.html", ga = ga )

    def post(self):
        loc1 = self.request.get("q61")
        loc2 = self.request.get("q62")
        loc3 = self.request.get("q63")
        loc4 = self.request.get("q64")
        loc5 = self.request.get("q65")
        loc6 = self.request.get("q66")
        loc7 = self.request.get("q67")
        loc8 = self.request.get("q68")
        loc9 = self.request.get("q69")
        loc10 = self.request.get("q610")
        loc11 = self.request.get("q611")
        loc12 = self.request.get("q612")
        loc13 = self.request.get("q613")
        loc14 = self.request.get("q614")
        loc15 = self.request.get("q615")
        loc16 = self.request.get("q616")
        loc17 = self.request.get("q617")
        loc18 = self.request.get("q618")
        loc19 = self.request.get("q619")
        loc20 = self.request.get("q620")
        loc21 = self.request.get("q621")
        loc22 = self.request.get("q622")
        loc23 = self.request.get("q623")
        loc24 = self.request.get("q624")
        loc25 = self.request.get("q625")
        loc26 = self.request.get("q626")
        loc27 = self.request.get("q627")
        loc28 = self.request.get("q628")
        loc29 = self.request.get("q629")

        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesLOC(username = username, loc1 = loc1, loc2 = loc2, loc3 = loc3, loc4 = loc4, loc5 = loc5, loc6 = loc6, loc7 = loc7, loc8 = loc8, loc9 = loc9, loc10 = loc10, loc11 = loc11, loc12 = loc12, loc13 = loc13, loc14 = loc14, loc15 = loc15, loc16 = loc16, loc17 = loc17, loc18 = loc18, loc19 = loc19, loc20 = loc20, loc21 = loc21, loc22 = loc22, loc23 = loc23, loc24 = loc24, loc25 = loc25, loc26 = loc26, loc27 = loc27, loc28 = loc28, loc29 = loc29)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteBIS')

class RteBIS(Handler):
    # not used

    def get(self):
        self.render("RteBIS.html", ga = ga )

    def post(self):

        bis1 = self.request.get("q11")
        bis2 = self.request.get("q12")
        bis3 = self.request.get("q13")
        bis4 = self.request.get("q14")
        bis5 = self.request.get("q15")
        bis6 = self.request.get("q16")
        bis7 = self.request.get("q17")


        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnaires(username = username, bis1 = bis1,  bis2 = bis2, bis3 = bis3, bis4 = bis4, bis5 = bis5, bis6 = bis6, bis7 = bis7)
        dmdata.put()
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteREI')

class RteBAS(Handler):
    def get(self):
        self.render("RteBAS.html", ga = ga )

    def post(self):
        bas1 = self.request.get("BAS1")
        bas2 = self.request.get("BAS2")
        bas3 = self.request.get("BAS3")
        bas4 = self.request.get("BAS4")
        bas5 = self.request.get("BAS5")
        bas6 = self.request.get("BAS6")
        bas7 = self.request.get("BAS7")
        bas8 = self.request.get("BAS8")
        bas9 = self.request.get("BAS9")
        bas10 = self.request.get("BAS10")
        bas11 = self.request.get("BAS11")
        bas12 = self.request.get("BAS12")
        bas13 = self.request.get("BAS13")
        bas14 = self.request.get("BAS14")
        bas15 = self.request.get("BAS15")
        bas16 = self.request.get("BAS16")
        bas17 = self.request.get("BAS17")
        bas18 = self.request.get("BAS18")
        bas19 = self.request.get("BAS19")
        bas20 = self.request.get("BAS20")
        bas21 = self.request.get("BAS21")
        bas22 = self.request.get("BAS22")
        bas23 = self.request.get("BAS23")
        bas24 = self.request.get("BAS24")
        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesBAS(username = username, bas1 = bas1, bas2 = bas2, bas3 = bas3, bas4 = bas4, bas5 = bas5, bas6 = bas6, bas7 = bas7, bas8 = bas8, bas9 = bas9, bas10 = bas10, bas11 = bas11, bas12 = bas12, bas13 = bas13, bas14 = bas14, bas15 = bas15, bas16 = bas16, bas17 = bas17, bas18 = bas18, bas19 = bas19, bas20 = bas20, bas21 = bas21, bas22 = bas22, bas23 = bas23, bas24 = bas24)
        dmdata.put()
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteREI')

class RteREI(Handler):
    def get(self):
        self.render("RteREI.html", ga = ga )

    def post(self):
        rei1 = self.request.get("q31")
        rei2 = self.request.get("q32")
        rei3 = self.request.get("q33")
        rei4 = self.request.get("q34")
        rei5 = self.request.get("q35")
        rei6 = self.request.get("q36")
        rei7 = self.request.get("q37")
        rei8 = self.request.get("q38")
        rei9 = self.request.get("q39")
        rei10 = self.request.get("q310")


        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesREI(username = username, rei1 = rei1, rei2 = rei2, rei3 = rei3, rei4 = rei4, rei5 = rei5, rei6 = rei6, rei7 = rei7, rei8 = rei8, rei9 = rei9, rei10 = rei10)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteBED')

class RteIMP(Handler):
    def get(self):
        self.render("RteIMP.html", ga = ga )

    def post(self):
        imp1 = self.request.get("q41")
        imp2 = self.request.get("q42")
        imp3 = self.request.get("q43")
        imp4 = self.request.get("q44")
        imp5 = self.request.get("q45")
        imp6 = self.request.get("q46")
        imp7 = self.request.get("q47")
        imp8 = self.request.get("q48")
        imp9 = self.request.get("q49")
        imp10 = self.request.get("q410")
        imp11 = self.request.get("q411")
        imp12 = self.request.get("q412")

        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesIMP(username = username, imp1 = imp1, imp2 = imp2, imp3 = imp3, imp4 = imp4, imp5 = imp5, imp6 = imp6, imp7 = imp7, imp8 = imp8, imp9 = imp9, imp10 = imp10, imp11 = imp11, imp12 = imp12)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RtePIL')

class RtePIL(Handler):
    def get(self):
        self.render("RtePIL.html", ga = ga )

    def post(self):
        pil1 = self.request.get("PIL1")
        pil2 = self.request.get("PIL2")
        pil3 = self.request.get("PIL3")
        pil4 = self.request.get("PIL4")
        pil5 = self.request.get("PIL5")
        pil6 = self.request.get("PIL6")
        pil7 = self.request.get("PIL7")
        pil8 = self.request.get("PIL8")
        pil9 = self.request.get("PIL9")
        pil10 = self.request.get("PIL10")
        pil11 = self.request.get("PIL11")
        pil12 = self.request.get("PIL12")
        pil13 = self.request.get("PIL13")
        pil14 = self.request.get("PIL14")
        pil15 = self.request.get("PIL15")
        pil16 = self.request.get("PIL16")
        pil17 = self.request.get("PIL17")
        pil18 = self.request.get("PIL18")
        pil19 = self.request.get("PIL19")
        pil20 = self.request.get("PIL20")

        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesPIL(username = username, pil1 = pil1, pil2 = pil2, pil3 = pil3, pil4 = pil4, pil5 = pil5, pil6 = pil6, pil7 = pil7, pil8 = pil8, pil9 = pil9, pil10 = pil10, pil11 = pil11, pil12 = pil12, pil13 = pil13, pil14 = pil14, pil15 = pil15, pil16 = pil16, pil17 = pil17, pil18 = pil18, pil19 = pil19, pil20 = pil20)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteSELFE')

class RteSELFE(Handler):
    def get(self):
        self.render("RteSELFE.html", ga = ga )

    def post(self):
        selfe1 = self.request.get("selfe1")
        selfe2 = self.request.get("selfe2")
        selfe3 = self.request.get("selfe3")
        selfe4 = self.request.get("selfe4")
        selfe5 = self.request.get("selfe5")
        selfe6 = self.request.get("selfe6")
        selfe7 = self.request.get("selfe7")
        selfe8 = self.request.get("selfe8")
        selfe9 = self.request.get("selfe9")
        selfe10 = self.request.get("selfe10")

        username = self.request.cookies.get('username', 0)

        dmdata = ExpQuestionnairesSELFE(username = username, selfe1 = selfe1, selfe2 = selfe2, selfe3 = selfe3, selfe4 = selfe4, selfe5 = selfe5, selfe6 = selfe6, selfe7 = selfe7, selfe8 = selfe8, selfe9 = selfe9, selfe10 = selfe10)
        dmdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteDEMO')

class RteDEMO(Handler):
    def get(self):
        self.render("RteDEMO.html", ga = ga )

    def post(self):
        demo = str(self.request.get("demo"))
        demo1 = self.request.get("demo1")
        demo2 = self.request.get("demo2")
        demo21 = self.request.get("demo21")
        demo4 = self.request.get("demo4")
        demo5 = self.request.get("demo5")
        demo6 = self.request.get("demo6")
        demo7 = self.request.get("demo7")
        demo8 = self.request.get("demo8")
        demo9 = self.request.get("demo9")
        # demo10 = self.request.get("demo10")

        username = str(self.request.cookies.get('username', 0))  # some strange new error if I have username as int....

        # dmdata = ExpQuestionnaires(username = username, demo = demo, demo1 = demo1, demo2 = demo2, demo3 = demo3, demo4 = demo4, demo5 = demo5, demo6 = demo6, demo7 = demo7, demo8 = demo8, demo9 = demo9, demo10 = demo10)
## REMOVE THIS TEST
        dmdata = ExpQuestionnairesDEMO(username = username, demo = demo, demo1 = demo1, demo2 = demo2, demo21 = demo21, demo4 = demo4, demo5 = demo5, demo6 = demo6, demo7 = demo7, demo8 = demo8, demo9 = demo9) # no demo10 b/c not used
        dmdata.put()
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/rev')

class ThankYou(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % "030301090801") #hardcoded number to find those who want to take the experiment again
        self.render("thankyou.html", ga = ga )

    def post(self):
        next = self.request.get("next")
        if next == "yes":
             self.redirect('/subjectdata')

class Other(Handler):
    def get(self):
        self.render("other.html")

    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/rev')

class Rev(Handler):
    def get(self):
        username = self.request.cookies.get('username', 0)
        # redirects = {"tasks": "/prev", "prev":"/te", "te":"/RteHL","rtehl":"/RteDM1", "rev":"/thankyou"}
        # handlerName = self.__class__.__name__
        # whereToRedirect = redirects[handlerName.lower()]
        # if visited(username, handlerName) == True: # checks if it was visited earlier by the user
        #     print "VISITED!!!!!"
        #     self.redirect(whereToRedirect)
        # elif visited(username, self.__class__.__name__) == False:
        #     print "NOT VISITED!!!!!"
        #     pass


        rLockValues = RevLock.all()

        for value in rLockValues:
            ''' This checks if username (pesel) is in the database. If it is there, this means that such a person
            already finished the experiment and maybe somebody else i trying to see her score.
            Hence, it redirects this person to the last screen.
            '''
            if value.pesel == username:
                self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % "030301090801") #hardcoded number to find those who want to take the experiment again
                self.redirect('/thankyou')
                return None

        if username == "030301090801":
            self.redirect('/thankyou')
            return None
        else:
            rLock = RevLock(pesel = username)
            rLock.put()





        # here I check if the user moved back to Rev. If yes (and cookie was changed above), I redirect him to /thankyou
        # username1 = self.request.cookies.get('username', 0)



        get_preventionCost = ExpFinal.all()
        get_preventionCost.filter('username =', username)
        preventionCost_result = get_preventionCost.get()
        preventionCost = preventionCost_result.preventionCost

        get_ecus = ExpFinal.all()
        get_ecus.filter('username =', username)
        ecus_result = get_ecus.get()
        ecus = ecus_result.ecu

        get_HLdata = ExpHL.all()
        get_HLdata.filter('username =', username)
        get_HLdata.order('-created')
        HLdata = get_HLdata.get()
        HLpayoffFinal = HLdata.HLpayoff # it's a float

        get_TEdata = ExpTime.all()
        get_TEdata.filter('username =', username)
        get_TEdata.order('-created')
        TEdata = get_TEdata.get()
        TEpayoffFinal = TEdata.TEpayoff # it's a float
        timing = TEdata.timing
        # logging.info("HLpayoffFinal")
        # logging.info(type(HLpayoffFinal))

        # get_AICdata = ExpQuestionnaires.all()
        # get_AICdata.filter('username =', username)
        # get_AICdata.filter('ai_content !=', None)
        # get_AICdata.order('-created')
        # AICdata = get_AICdata.get()
        # AICdataFinal = AICdata.ai_content

        forAll = UserTreatment.all().filter('username = ', username).get()
        forSeverity = forAll.severity
        forRisk = forAll.risk
        forPreventionEffectiveness = forAll.prevention
        forPreventionPrice = forAll.severity # because price also depends on severity

        logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        logging.info(">>>>>>> name = ")
        logging.info(username)


        # pp, pp_price depend on treatment condition
        # pp_price_user depends of pp, pp_price and how many ECUS users has

        if forPreventionEffectiveness.lower() == 'ineffective':
            preventionEffectiveness = u'20'
            if forPreventionPrice.lower() == 'cancer':
                preventionPrice = u'26'
            elif forPreventionPrice.lower() == 'flu':
                preventionPrice = u'13'
            else:
                print "ERROR  1 in if forPreventionEffectiveness.lower() == 'ineffective'"
                print "Assumed preventionPrice = u'26%'"
                print "username = ", username
                print "forPreventionPrice.lower() = ", forPreventionPrice.lower()
                preventionPrice = u'26'

        elif forPreventionEffectiveness.lower() == 'effective':
            preventionEffectiveness = u'60'
            if forPreventionPrice.lower() == 'cancer':
                preventionPrice = u'26'
            elif forPreventionPrice.lower() == 'flu':
                preventionPrice = u'13'
            else:
                print "ERROR  2 in if forPreventionEffectiveness.lower() == 'ineffective'"
                print "Assumed preventionPrice = u'26%'"
                print "username = ", username
                print "forPreventionPrice.lower() = ", forPreventionPrice.lower()
                preventionPrice = u'26'

        else:
            print "ERROR  3 in if forPreventionEffectiveness.lower() == 'ineffective'"
            print "Assumed preventionPrice = u'26%'"
            print "Assumed preventionEffectiveness = u'20 punktów procentowych'"
            print "username = ", username
            print "forPreventionPrice.lower() = ", forPreventionEffectiveness.lower()
            preventionEffectiveness = u'20'
            preventionPrice = u'26'



        payoffLucky = (float(ecus) - float(preventionCost) + float(HLpayoffFinal))*float(TEpayoffFinal)
        payoffLucky = round(payoffLucky)

        if forSeverity.lower() == 'cancer':
            payoffUnlucky = ((float(ecus) - float(preventionCost) + float(HLpayoffFinal))*float(TEpayoffFinal))*0.1
            payoffUnlucky = round(payoffUnlucky)
        elif forSeverity.lower() == 'flu':
            payoffUnlucky = ((float(ecus) - float(preventionCost) + float(HLpayoffFinal))*float(TEpayoffFinal))*0.51
            payoffUnlucky = round(payoffUnlucky)

        print "payoffLucky =", payoffLucky
        print "payoffUnlucky =", payoffUnlucky
        print "ecus =", ecus
        print "preventionCost =", preventionCost
        print "HLpayoffFinal =", HLpayoffFinal
        print "TEpayoffFinal =", TEpayoffFinal

        # get_randomQ = ExpHL.all()
        # get_randomQ.filter('username =', username)
        # randomQ_result = get_randomQ.get()
        # randomQ_final = randomQ_result.randomQ

        forProbabilitySick = probabilitySick.all().filter('username = ', username).get()
        forProbabilityOriginal = forProbabilitySick.probabilitySickOriginal
        forProbabilityNew = forProbabilitySick.probabilitySickNew
        probabilityOriginal = float(forProbabilityOriginal)
        probabilityNew = float(forProbabilityNew)


        # if forRisk.lower() == 'low_risk':
        #     magicNumber = randint(0,5) #Inclusive
        # if forRisk.lower() == 'high_risk':
        #     magicNumber = randint(6,10) #Inclusive

        # # for low risk group
        # magicNumber = randint(1,5) #Inclusive

        # logging.info type(preventionCost)

        if timing == "now":
            payoffTiming = u'Wypłatę otrzymasz w ciągu 24 godzin.'
        elif timing == "later":
            payoffTiming = u'Zgodnie z Twoją decyzją, powiększoną wypłatę otrzymasz za 4 tygodnie.'
        else:
            payoffTiming = u'Wystąpił błąd. Nic się nie martw - wyślij email ze swoim numerem PESEL na student@dwach.edu.pl .'

        #
        # # efectiveness of prevention = 20 pp
        # if preventionCost != "0": # means they bought prevention
        #     magicNumber = magicNumber - 2 # here efectivenes of prev = 0.2 so we substract 2 b/e ,e.g., 0.6-0.2 is the same as 6 - 2 in our case
        #
        # # # efectiveness of prevention = 60 pp
        # # if preventionCost != "0": # means they bought prevention
        # #     magicNumber = magicNumber - 3 # here efectivenes of prev = 0.8 so we substract 3 b/e ,e.g., 0.6-0.8 is the same as 6 - 3 in our case
        #
        import numpy as np
        magicNumber = (int(np.random.binomial(1, (1-probabilityOriginal/100))))*10 # 0 means unlucky, 10 means lucky
        # magicNumber = np.random.choice([0, 10], p=[probabilityOriginal/10, (1-probabilityOriginal/10)]) # 0 means unlucky, 10 means lucky // doesn't work because GAE does not support the newest numpy

        if preventionCost != "0": # means they bought prevention
            magicNumber = (int(np.random.binomial(1, (1-probabilityNew/100))))*10 # 0 means unlucky, 10 means lucky // doesn't work because GAE does not support the newest numpy
            # magicNumber = np.random.choice([0, 10], p=[probabilityNew/10, (1-probabilityNew/10)]) # 0 means unlucky, 10 means lucky // doesn't work because GAE does not support the newest numpy


        # if preventionCost != "0": # means they bought prevention
        #             if forPreventionEffectiveness.lower() == 'ineffective':
        #                 magicNumber = magicNumber - 2 # here efectiveness of prev = 0.2 so we substract 2 b/e ,e.g., 0.6-0.2 is the same as 6 - 2 in our case
        #             if forPreventionEffectiveness.lower() == 'effective':
        #                 magicNumber = magicNumber - 8 # here efectiveness of prev = 0.8 so we substract 3 b/e ,e.g., 0.6-0.8 is the same as 6 - 3 in our case

        print "magicNumber", magicNumber

        percentageLoss = u''
        if forSeverity.lower() == 'cancer':
            percentageLoss = u'90'
        elif forSeverity.lower() == 'flu':
            percentageLoss = u'49'

        if magicNumber < 5: # if unlucky
            outcome = u'Niestety, komputer uznał, że utracisz ' + percentageLoss + u' procent pieniędzy.'
            payoff = payoffUnlucky
            payoff = payoff/10

        if magicNumber >= 5: # if lucky
            outcome = u'Na szczęście, komputer uznał, że nie utracisz ' + percentageLoss + u' procent pieniędzy.'
            payoff = payoffLucky
            payoff = payoff/10

        while payoff < 5: # makes sure payoff is > 5 because of showup fee
            payoff = payoff + 1

        HLpayoffFinal = str(HLpayoffFinal)
        e = ExpViewer(ecus = ecus, preventionCost = preventionCost, payoffLucky = payoffLucky, payoffUnlucky = payoffUnlucky, outcome = outcome, payoff = payoff, magicNumber = magicNumber, HLpayoffFinal = HLpayoffFinal, username = username, timing = timing)
        e.put()
        self.render("rev.html", ga = ga, ecus = ecus, preventionCost = preventionCost, payoffLucky = payoffLucky, payoffUnlucky = payoffUnlucky, outcome = outcome, payoff = payoff, magicNumber = magicNumber, HLpayoffFinal = HLpayoffFinal, username = username, payoffTiming = payoffTiming)
        self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % "030301090801") #hardcoded number to find those who want to take the experiment again


    def post(self):
        next = self.request.get("next")
        if next == "yes":
            self.redirect('/thankyou')

class Experiment(Handler):
    def get(self):
        self.render("experiment.html", ga = ga )

class Viewer(Handler):
    def get(self):

        get_ViewerData = ExpViewer.all()

        dataDictToPrint = {}
        for value in get_ViewerData:
            dataDictToPrint[value.username] = {}
            dataDictToPrint[value.username]["payoff"] = value.payoff
            dataDictToPrint[value.username]["timing"] = value.timing
             # dataDictToPrint[int(value.username)]["timing"] = value.timing

        print dataDictToPrint

        # for value in get_ViewerData:
        #      print value.payoff, value.timing

        # # this prints names of all properties of a db
        #
        # for key, value in ExpViewer.properties().items():
        #     print key
        #
        # print ExpViewer.properties()


        self.render("viewer.html", contents = get_ViewerData)

    # def post(self):
    #     next = self.request.get("next")
    #     if next == "yes":
    #         self.redirect('/Logout')

class SecretViewer(Handler):

    #TODO rewrite this to make is actually secure, instead of hardcoding u and p.

    def get(self):
        print "Welcome to Secret Viewer 4000"
        username = self.request.cookies.get('username', 0)
        password = self.request.cookies.get('password', 0)

        if username == "__REWRITE_ME__" and password == "__REWRITE_ME__":
            print "passwords correct"
            self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % "3d213h")
            self.response.headers.add_header('Set-Cookie', 'password=%s; Path=/' % "4329c4d32")
        else:
            print "incorrect passwords, sire!", username, password
            self.redirect("/login")
            return None

        get_ViewerData = ExpViewer.all()

        dataDictToPrint1 = {}
        for value in get_ViewerData:
            dataDictToPrint1[value.username] = {}
            dataDictToPrint1[value.username]["payoff"] = value.payoff
            dataDictToPrint1[value.username]["timing"] = value.timing
             # dataDictToPrint[int(value.username)]["timing"] = value.timing

        # print dataDictToPrint

        get_SubjectContactData = SubjectContactData.all()

        # props = ["stateID", "motherName"]
        dataDictToPrint2 = {}
        for value in get_SubjectContactData:

            dataDictToPrint2[value.stateID] = {}
            for keyz in SubjectContactData.properties():

                dataDictToPrint2[value.stateID][keyz] = getattr(value, keyz) # this dynamically calls atributes of value. I need this to create a dictionary

        print dataDictToPrint1
        print dataDictToPrint2

        dict1 = dataDictToPrint1
        dict2 = dataDictToPrint2


        for key1, value1 in dict1.items():
            for key2, value2 in dict2.items():
                # _ = [dict1][key1]
                if key1 == key2:
                    dict2[key1]['payoff'] = dict1[key1]['payoff']
                    dict2[key1]['timing'] = dict1[key1]['timing']

        print dict2
        for key, value in dict2.items():
            # temp = value['created'].lstrip('datetime.datetime(').rstrip(')')
            # date = datetime.strptime(temp, '%Y, %m, %d, %H, %M, %S, %f')
            date = value['created']


            try: # I use try/except because not all values have a 'timing' key
                if value['timing'] == 'now': value['timing'] = date.year, date.month, date.day, 'TERAZ'
                if value['timing'] == 'later':
                    date += timedelta(days=30)
                    value['timing'] = date.year, date.month, date.day, 'POTEM'

            except:
                pass


        # # this prints names of all properties of a db
        #
        # for key, value in ExpViewer.properties().items():
        #     print key
        #
        # print ExpViewer.properties() // dictionary


        self.render("viewer.html", contents = dict2)


class GetData(Handler):
# So far only gets results from ExpQuestionnaires

    def get(self):

        get_data = ExpQuestionnaires.all()
        get_data.order('username')
        get_data.order('-created')

        # get_data.order('username')

        # self.render("getdata.html", contents = get_ViewerData
        self.render("getdata.html", contents = get_data)

def evaluateList(ints):

    score = -9 # intialization
    error = "" # intialization

    for i in xrange(1,15):
        if ints[i-1] < ints[i]:

            score = i # where was the last value before switching to bigger, eg. from 1 to 2
            error = "no error"

        if ints[i-1] > ints[i]:
            score = -1
            error = "switched back at " + str(i) # where was the last value before switching back

    if score == -9: # either all numbers are the same or some reason earlier ifs didn't go through the list
        if all(ints[0] == item for item in ints[0:-1]): # checking if all values are the same
            score = ints[0] # all values are the same, so this returns what that non-changing number is
            error = "never switched"
    username = ints[-1]
    return username, score, error

outcomes = {}
def dataToDict(ints):
    nameFinal = evaluateList(ints)[0]
    scoreFinal = evaluateList(ints)[1]
    errorFinal = evaluateList(ints)[2]

    # print scoreFinal, errorFinal, nameFinal



    preOutcome = {}

    preOutcome["score"]=scoreFinal
    preOutcome["error"]=errorFinal
    outcomes[nameFinal]=preOutcome

    return outcomes

class GetDataHL(Handler):
# So far only gets results from ExpQuestionnaires

    def get(self):

        get_data = ExpHL.all()
        get_data.order('username')
        logging.info("--------------------- EXPHL ----------------------")

        for item in get_data:
            # print item.username
            if int(item.HLpayoff) > -1:           # makes sure answer did not have an error
                logging.debug(item.username)
                ints = []
                ints.append(item.q1)
                ints.append(item.q2)
                ints.append(item.q3)
                ints.append(item.q4)
                ints.append(item.q5)
                ints.append(item.q6)
                ints.append(item.q7)
                ints.append(item.q8)
                ints.append(item.q9)
                ints.append(item.q10)
                ints.append(item.q11)
                ints.append(item.q12)
                ints.append(item.q13)
                ints.append(item.q14)
                ints.append(item.q15)
                ints.append(item.username)

                evaluateList(ints)
                dataToDict(ints)


        # get_data.order('username')

        other = {32323: {"score": 22, "error": "all ok!"}}
        # self.render("getdata.html", contents = get_ViewerData
        self.render("getdataHL.html", contents = get_data, other = outcomes)


class errorCounter:
    # used to count the number of quiz attempts in pquiz

    errorN = 1

    def __int__(self):
        self.errorN = errorN

    def giveErrorN(self):
    	return self.errorN

    def incrementErrorN(self):
        self.errorN = self.errorN + 1

attempts = errorCounter() # logs the number of retakes of pquiz (quiz about percentage points)
attempts_instructions = errorCounter() # logs the number of retakes of equiz (quiz of experimental instructions)


class AddABG(Handler):
    # Ania's questions handler 1

    def get(self):
        self.render("AddABG.html", ga = ga )

    def post(self):
        AddABG1 = self.request.get("ADDABG1")
        AddABG2 = self.request.get("ADDABG2")
        AddABG3 = self.request.get("ADDABG3")
        AddABG4 = self.request.get("ADDABG4")
        AddABG5 = self.request.get("ADDABG5")
        AddABG6 = self.request.get("ADDABG6")
        AddABG7 = self.request.get("ADDABG7")
        AddABG8 = self.request.get("ADDABG8")
        AddABG9 = self.request.get("ADDABG9")
        AddABG10 = self.request.get("ADDABG10")
        AddABG11 = self.request.get("ADDABG11")
        AddABG12 = self.request.get("ADDABG12")
        AddABG13 = self.request.get("ADDABG13")
        AddABG14 = self.request.get("ADDABG14")
        AddABG15 = self.request.get("ADDABG15")


        username = self.request.cookies.get('username', 0)

        ABGdata = AniaP1(username = username, AddABG1 = AddABG1, AddABG2 = AddABG2, AddABG3 = AddABG3, AddABG4 = AddABG4, AddABG5 = AddABG5, AddABG6 = AddABG6, AddABG7 = AddABG7, AddABG8 = AddABG8, AddABG9 = AddABG9, AddABG10 = AddABG10, AddABG11 = AddABG11, AddABG12 = AddABG12, AddABG13 = AddABG13, AddABG14 = AddABG14, AddABG15 = AddABG15)
        ABGdata.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/AddABG2')


class AddABG2(Handler):
    # Ania's questions handler 2

    def get(self):
        self.render("AddABG2.html", ga = ga )

    def post(self):
        AddABG16 = self.request.get("ADDABG16")
        AddABG17 = self.request.get("ADDABG17")
        AddABG18 = self.request.get("ADDABG18")
        AddABG19 = self.request.get("ADDABG19")
        AddABG20 = self.request.get("ADDABG20")
        AddABG21 = self.request.get("ADDABG21")
        AddABG22 = self.request.get("ADDABG22")

        username = self.request.cookies.get('username', 0)

        ABG2data = AniaP2(username = username, AddABG16 = AddABG16, AddABG17 = AddABG17, AddABG18 = AddABG18, AddABG19 = AddABG19, AddABG20 = AddABG20, AddABG21 = AddABG21, AddABG22 = AddABG22)
        ABG2data.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/rev')



class SubjectData(Handler):
    # Viewer for DW

    def get(self):
        # self.render("subjectdata-v2-bank.html", ga = ga ) # or change to paypal
        self.render("subjectdata-v2-paypal.html", ga = ga ) # or change to bank

    def post(self):
        username = self.request.cookies.get('username', 0)
        firstName = self.request.get("firstName")
        middleName = self.request.get("middleName")
        lastName = self.request.get("lastName")
        city = self.request.get("city")
        zipCode = self.request.get("zipCode")
        country = self.request.get("country")
        isStudent = self.request.get("isStudent")


        form = SubjectContactData(username = username, firstName = firstName, middleName = middleName,
                                  lastName = lastName, city = city,
                                  zipCode = zipCode, country = country, isStudent = isStudent)
        form.put()

        next = self.request.get("next")
        if next == "yes":
            self.redirect('/end')


class Agreement(Handler):
    # DW's agreement form

    def get(self):
        self.render("agreement.html", ga = ga )

    def post(self):
        username = self.request.cookies.get('username', 0)
        experimentAgree = self.request.get("experimentAgree")
        paypalAgree = self.request.get("paypalAgree")


        # username = self.request.cookies.get('username', 0)

        agree = SubjectAgreement(username = username, experimentAgree = experimentAgree, paypalAgree = paypalAgree)
        agree.put()

        Aerror = ""
        Berror = ""

        next = self.request.get("next")

        if next == "yes" and experimentAgree and paypalAgree:

            if next == "yes" and experimentAgree == "yes" and paypalAgree == "yes":
                self.redirect('/nmi_questions')

            elif next == "yes" and experimentAgree == "no" and paypalAgree == "yes":
                print "1"
                Aerror = u'Bez wyrażenia zgody kontynuacja badania jest niemożliwa.'
                print "2"
                self.render("agreement.html", Aerror = Aerror, Berror = Berror)
                print "3"
            elif next == "yes" and experimentAgree == "yes" and paypalAgree == "no":
                Berror = u'Bez wyrażenia zgody kontynuacja badania jest niemożliwa.'
                self.render("agreement.html", Aerror = Aerror, Berror = Berror)

            elif next == "yes" and experimentAgree == "no" and paypalAgree == "no":
                Aerror = u'Bez wyrażenia zgody kontynuacja badania jest niemożliwa.'
                Berror = u'Bez wyrażenia zgody kontynuacja badania jest niemożliwa.'
                self.render("agreement.html", Aerror = Aerror, Berror = Berror)

        elif next == "yes":
            Aerror = u'Bez wyrażenia zgody kontynuacja badania jest niemożliwa.'
            Berror = u'Bez wyrażenia zgody kontynuacja badania jest niemożliwa.'
            self.render("agreement.html", Aerror = Aerror, Berror = Berror)

        # elif next == "yes" and ((experimentAgree and not paypalAgree) or (experimentAgree and not paypalAgree)):
        #     Aerror = u'Bez wyrażenia zgody kontynuacja badania jest niemożliwa.'
        #     Berror = u'Bez wyrażenia zgody kontynuacja badania jest niemożliwa.'
        #     self.render("agreement.html", Aerror = Aerror, Berror = Berror)

class RteBED(Handler):
    # Binge eating disorder and bmi

    def get(self):
        self.render("RteBED.html", ga = ga )

    def post(self):
        q1 = self.request.get("q1")
        q2 = self.request.get("q2")
        q3 = self.request.get("q3")
        q4 = self.request.get("q4")
        weight = self.request.get("weight")
        height = self.request.get("height")
        username = self.request.cookies.get('username', 0)

        beddata = RteBEDdb(username = username, q1 = q1, q2 = q2, q3 = q3, q4 = q4, weight = weight, height = height)
        beddata.put()

        # q1 = self.request.get("q1")
        # q2 = self.request.get("q2")
        # q3 = self.request.get("q3")
        # q4 = self.request.get("q4")
        # weight = self.request.get("weight")
        # height = self.request.get("height")


        next = self.request.get("next")
        if next == "yes":
            self.redirect('/RteSELFE')

class End(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % "030301090801") #hardcoded number to find those who want to take the experiment again (cheating)
        self.render("end.html", ga = ga )

    def post(self):
        pass

class SeeYouSoon(Handler):
    def get(self):
        self.render("seeYouSoon.html")

    def post(self):
        pass


class UserData:
    '''
    stores info about users' treatments and updates the number of subjects in a given treatment in the datastore
    '''

    def __init__(self, username, severity, prevention, risk, evaluation, treatmentName):
        self.username = username.lower() # username
        self.severity = severity.lower() # illness severity: Flu = 49% / Cancer = 90% loss of earnings
        self.prevention = prevention.lower() # Effectiveness of prevention = low (20pp) or high (60 pp) (price of prevention is 13% for Flu and 26% for Cancer)
        self.risk = risk.lower() # high risk group: magic number <6,10> / low risk group: magic number <1,5>
        self.evaluation = evaluation.lower() # info evaluation: analytical (2 digit numbers) or emotional (7 digit numbers)
        self.treatmentName = treatmentName.lower() # content = domain of message content: financial or ethical

        saveUser = UserTreatment(username = self.username, severity = self.severity, prevention = self.prevention, risk = self.risk, evaluation = self.evaluation)
        saveUser.put()

        _id = SubjectsInTreatments.all().filter('treatment = ', treatmentName).get()
        _id = _id.key()

        currentSubjectCounter = SubjectsInTreatments.all().filter('treatment = ', treatmentName).get()
        currentSubjectCounter = currentSubjectCounter.subjectCounter

        oldSubjectCounter = db.get(str(_id)) # db.get needs a normal key to be cast as string. if you want to print number key use entity.key().id()
        oldSubjectCounter.subjectCounter = currentSubjectCounter + 1
        updatedSubjectCounter = oldSubjectCounter
        updatedSubjectCounter.put()

def makeUser(username):
    treatmentName, treatmentCondition = assignTreatments()
    thisUser = UserData(username, treatmentCondition["severity"], treatmentCondition["prevention"], treatmentCondition["risk"], treatmentCondition["evaluation"], treatmentName = treatmentName)


def getTreatmentsCounts():

        ''' Here I create treatments and add them to datastore with count = 0, if they don't yet exist. Basically, this
        will only happen once (for the first subject taking the experiment). It is a little complicated but I need to
         check errors in datastore, etc. I cannot simply create it because each new subject would overwrite values in
         SubjectsInTreatments and these values have to persist.

        This function RETURNS a dictionary of treatments with the number of subjects per treatment
        '''


        treatmentsList = ["treatment1", "treatment2", "treatment3", "treatment4", "treatment5", "treatment6",
                        "treatment7", "treatment8", "treatment9", "treatment10", "treatment11", "treatment12",
                          "treatment13", "treatment14", "treatment15", "treatment16"]
        treatments = {}

        for t in treatmentsList:
            treatments[t] = -1
        print "**********  1 treatments, should be all -1", treatments



        for i in SubjectsInTreatments.all():
            treatments[i.treatment] = i.subjectCounter

        print "**********  2 treatments                   ", treatments

        treatmentsToCreate = []
        for k, v in treatments.items():
            if v < 0: treatmentsToCreate.append(k) # treatments with no subjects get created with subjectCounter = 0 below

        print "**********  3 treatmentsTOCREATE, should be t1-t16  ", treatmentsToCreate
        # print "treatments", treatments
        # print "treatmentsToCreate", treatmentsToCreate
        global treatmentsKeys
        treatmentsKeys = {}

        for item in treatmentsToCreate:
            toPut = SubjectsInTreatments(treatment = item, subjectCounter = 0)
            toPut.put()

        global recursion_level
        recursion_level = 0

        def waitForDatastore():
            ''' This checks if all data was written to datastore. If not it waits and retries.
            I need this because sometimes datastore is too slow, which cause issue in other parts of the application

            :return: -1 if failed after 500 tries
            '''
            global recursion_level
            i = 0
            for treat in treatmentsToCreate:
                for entity in SubjectsInTreatments.all().filter('treatment = ', treat):
                    i = i + 1

            if i < len(treatmentsToCreate) and recursion_level < 500:
                # print "Time to sleeeeeeeeeeeeeeeeeeeeeeeeeeep", i
                sleep(0.01)
                recursion_level = recursion_level + 1
                waitForDatastore()

            if recursion_level >= 500:
                print "ERROR in waitForDatastore!"
                print "i=", i
                return -1

        waitForDatastore()
        print "recursion_level", recursion_level

        treatmentsFinal = {}

        for i in SubjectsInTreatments.all():
            treatmentsFinal[i.treatment] = i.subjectCounter
        # print "treatmentsFinal", treatmentsFinal
        return treatmentsFinal # dict with counts of subjects per treatment


def getTreatmentsSmallest():
    ''' returns treatment condition (TC) with the least subjects
    if more than 1 such TC, it returns a random one of such TC

    coding of treatment conditions:
    1 ('cancer', 'high_risk', 'analytical', 'effective')
    2 ('cancer', 'high_risk', 'analytical', 'ineffective')
    3 ('cancer', 'high_risk', 'emotional', 'effective')
    4 ('cancer', 'high_risk', 'emotional', 'ineffective')
    5 ('cancer', 'low_risk', 'analytical', 'effective')
    6 ('cancer', 'low_risk', 'analytical', 'ineffective')
    7 ('cancer', 'low_risk', 'emotional', 'effective')
    8 ('cancer', 'low_risk', 'emotional', 'ineffective')
    9 ('flu', 'high_risk', 'analytical', 'effective')
    10 ('flu', 'high_risk', 'analytical', 'ineffective')
    11 ('flu', 'high_risk', 'emotional', 'effective')
    12 ('flu', 'high_risk', 'emotional', 'ineffective')
    13 ('flu', 'low_risk', 'analytical', 'effective')
    14 ('flu', 'low_risk', 'analytical', 'ineffective')
    15 ('flu', 'low_risk', 'emotional', 'effective')
    16 ('flu', 'low_risk', 'emotional', 'ineffective')

    '''
    # #########################
    # Treatments for half-fractional
    # 2 ('cancer', 'high_risk', 'analytical', 'ineffective') X
    # 5 ('cancer', 'low_risk', 'analytical', 'effective') X
    # 9 ('flu', 'high_risk', 'analytical', 'effective') X
    # 14 ('flu', 'low_risk', 'analytical', 'ineffective') X
    # #########################

    myDict = getTreatmentsCounts()
    print "myDict", myDict

    # ##############################################
    # # THIS IS FOR HALF-FRACTIONAL DESIGN ONLY !!!
    # # REMOVE FOR FULL FACTORIAL
    #
    # for k, v in myDict.items():
    #     if k == "treatment2" or k == "treatment5" or k == "treatment9" or k == "treatment14":
    #         pass
    #     else:
    #         del myDict[k]
    # print "myDict", myDict
    # ##############################################

    # ################################################
    # # THIS IS FOR SELECTING TREATMENTS ONE BY ONE
    #
    # # listOfTreatments = [2, 10, 6, 14, 1, 9, 5, 13, 4, 12, 8, 16, 3, 11, 7, 15] #this order was set by experimenters on purpose
    # listOfTreatments = [15, 3, 11, 16, 7, 12, 2, 10, 6, 14, 1, 9, 5, 13, 4, 8] #this order was set by experimenters on purpose
    #
    #
    # try:
    #     for i in listOfTreatments:
    #         # print "i===", i
    #         treatment = "treatment"+str(i)
    #         if myDict[treatment] < 70:
    #             print i, myDict[treatment]
    #             _count = myDict[treatment]
    #             break
    #
    #     myDict.clear()
    #     myDict[treatment] = _count
    #     print myDict
    #
    # except: # if the above fails, than subject is assigned to a random treatment
    #         # the above will fail, when all treatments have more then 50 subjects
    #     print "exception"
    #     myDict = getTreatmentsCounts()
    #     pass
    # ################################################

    myDict = getTreatmentsCounts() # IMPORTANT, comment out this line (and the above section) to assign treatments one by one, i.e., not purely randomly

    treatments = []

    # print "myDict after exception", myDict

    min_val = min(myDict.itervalues())
    [treatments.append(k) for k, v in myDict.iteritems() if v == min_val]
    # print "smallest value in list", treatments
    return random.choice(treatments) # random treatment selected if 2 or more treatments have the same # of subjects

def assignTreatments():
    '''used to assigns subject to random treatment // currently used in makeUser()
    :returns: a random treatment as a tuple of a string and a dict
    '''

    import itertools
    assigned = getTreatmentsSmallest()
    print "assigned >>>", assigned

    treatmentCondition = {}

    import itertools
    severity = ["cancer", "flu"]
    risk = ["high_risk", "low_risk"]
    evaluation = ["analytical", "emotional"]
    prevention = ["effective", "ineffective"]

    n = 1
    treatmentConditions = {}
    for i in itertools.product(severity, risk, evaluation, prevention):
        treatmentConditions[n] = {}
        treatmentConditions[n]["severity"] = i[0]
        treatmentConditions[n]["risk"] = i[1]
        treatmentConditions[n]["evaluation"] = i[2]
        treatmentConditions[n]["prevention"] = i[3]
        n += 1
    treatmentNumber = int(assigned[9:]) #number of treatment appears after the 8th character in this string. Can't use -1 because this number is 1 or 2 digits
    treatmentCondition = treatmentConditions[treatmentNumber]
    print "treatmentNumber", treatmentNumber
    print "treatmentConditions", treatmentConditions
    print "treatmentCondition", treatmentCondition

    return (assigned, treatmentCondition)

def visited(username, page):
    '''
    checks if user visited this page. If not, updates entry in database to True (aka visited). If user was on that page,
     it redirects user to his previous page.

    :param username: username
    :param page: page asking the question
    :return: True if everything OK. False if not
    '''
    sleep(0.1)
    username = str(username)
    page = str(page).lower()

    pageVisited = Visited.all().filter('username = ', username).get()
    # print "pageVisited", pageVisited.properties()
    pageVisited = getattr(pageVisited,page)
    print pageVisited
    # pageVisited.page

    if pageVisited == False: #if page wasn't vistied by user

        _id = Visited.all().filter('username = ', username).get()
        _id = _id.key()

        oldVisited = db.get(str(_id)) # db.get needs a normal key to be cast as string. if you want to print number key use entity.key().id()
        # oldVisited.page = True
        setattr(oldVisited, page, True)
        # newVisited = oldVisited
        # newVisited.put()
        oldVisited.put()
        return False

    if pageVisited == True:
        return True

def checkPesel(pesel):
    if len(str(pesel)) != 11:
        return False
    else:
        sum, ct = 0, [1, 3, 7, 9, 1, 3, 7, 9, 1, 3, 1]
        for i in range(11):
            sum += (int(pesel[i]) * ct[i])
        return (sum%10 == 0)

def HasUserFinished(username):
    '''
    :return: True if user finished experiment , ie., finished /rev and his username is in revlock
    '''
    finished = RevLock.all().filter('pesel = ', username).get()
    peselFromOldExperiment = [59070709546, 62042411552, 69082002159, 69111100052, 70120403573, 73032106046, 76020719145, 76082806300, 77112205362, 78061203872, 78101909331, 80041115147, 80102705977, 81092514060, 84030204933, 84080100562, 84112717094, 85011805848, 86031202637, 88020511733, 88030914278, 88092300365, 89033007989, 89070214348, 89071207965, 89082003301, 89120300247, 90011410002, 90022106936, 90033112294, 90040416767, 90050208459, 90051205875, 90051603741, 90051703014, 90052214814, 90052414139, 90061403649, 90062709478, 90070804060, 90072003627, 90073100019, 90091811887, 90100103363, 90103004579, 90110805648, 90113004716, 91012904783, 91030613764, 91032100204, 91032515583, 91040102544, 91041201587, 91041601486, 91042315191, 91060607843, 91061206812, 91062017774, 91071507327, 91071807175, 91072401255, 91082004572, 91082504508, 91090207329, 91090505410, 91091302801, 91091507862, 91091604880, 91092404045, 91102706783, 91102801266, 91102903784, 91112202310, 91112501570, 91112701536, 91120904550, 91121401384, 91122300262, 91122407174, 91122806584, 92010302351, 92010600794, 92010905066, 92010913258, 92012211446, 92012914707, 92020711888, 92021214090, 92021407063, 92021609403, 92021703480, 92021706674, 92021714682, 92022300037, 92022605590, 92022806694, 92030105543, 92030311553, 92032101035, 92032305156, 92032808789, 92040614855, 92042902774, 92050803542, 92050910358, 92051707371, 92052109035, 92053009266, 92060604182, 92060813751, 92060904824, 92061608871, 92061810825, 92062303232, 92070115298, 92070815877, 92071412097, 92072100854, 92072210335, 92072800891, 92082107104, 92082407655, 92083101367, 92090300999, 92090302472, 92090307620, 92090909808, 92091111820, 92091802278, 92092101833, 92092304861, 92092307963, 92092906100, 92100613921, 92100900889, 92101404313, 92101700877, 92101906716, 92102408460, 92110104147, 92110204397, 92110802663, 92111302940, 92111409388, 92111505305, 92111706911, 92112201583, 92120112064, 92120508577, 92121111437, 92121508842, 92122907565, 93012310395, 93012410996, 93012508035, 93020405687, 93020802743, 93020901848, 93020905088, 93021700866, 93021800177, 93022102643, 93022311069, 93022403737, 93030214518, 93030413603, 93030708927, 93031007650, 93031702012, 93032111363, 93032411111, 93040103242, 93041011115, 93041101522, 93042106724, 93050402489, 93051107536, 93051404077, 93051900627, 93052104983, 93052507410, 93052600830, 93052801996, 93060100692, 93060111467, 93061712728, 93062710329, 93062907938, 93063003459, 93070108820, 93070609222, 93070701528, 93071400181, 93071511229, 93071513207, 93072410671, 93073106290, 93080206499, 93080212788, 93081201868, 93081701108, 93082300122, 93082409517, 93082808286, 93090600225, 93092001840, 93092609444, 93092907450, 93092910104, 93100115499, 93100309319, 93101000059, 93101701028, 93101908807, 93102112708, 93102503896, 93110414155, 93111203279, 93111508084, 93111606706, 93112201641, 93120201309, 93120307401, 93120313738, 93121105503, 93121805830, 94010404507, 94010505789, 94010510671, 94010709428, 94010901851, 94011200812, 94011201080, 94011308282, 94011701900, 94011707531, 94012007982, 94012203708, 94012203746, 94012904036, 94020502732, 94020502930, 94020611694, 94020700284, 94021102283, 94021614870, 94021711713, 94021908742, 94022114348, 94022302170, 94022406898, 94022510892, 94022702017, 94030302999, 94030400819, 94030503710, 94030712402, 94030801269, 94031001842, 94031203046, 94031804131, 94032109389, 94032502687, 94032508980, 94032600552, 94032706234, 94032800587, 94033006012, 94040210864, 94040805943, 94041409801, 94041505262, 94041509143, 94041700865, 94041904580, 94042103865, 94042108198, 94042507140, 94042608988, 94042905931, 94043006433, 94050202741, 94050210575, 94050308522, 94050610573, 94050706009, 94051214653, 94051413199, 94051601921, 94051714993, 94052006367, 94052010104, 94052704357, 94060304741, 94060603796, 94061105723, 94061510620, 94061612100, 94061712336, 94062100635, 94062306956, 94062307346, 94062500091, 94062607330, 94062800665, 94062912742, 94062915219, 94070405283, 94070500049, 94070503561, 94071103234, 94071502101, 94071510102, 94072004916, 94072305819, 94072406688, 94072503521, 94072708056, 94072800741, 94073103645, 94080102396, 94080806276, 94081209054, 94081501217, 94090202448, 94090205038, 94090506450, 94091510197, 94091703160, 94092406307, 94092411343, 94092607005, 94092901208, 94100402132, 94100404394, 94100404431, 94100601791, 94100606772, 94100708030, 94100807906, 94101103537, 94101605145, 94101901227, 94102005210, 94102404217, 94102409595, 94102707174, 94110200885, 94110503179, 94110509779, 94111300188, 94111300829, 94111302388, 94111613031, 94111702904, 94111902540, 94112206292, 94112802856, 94120304924, 94120308638, 94120503002, 94121307469, 94121408757, 94121600135, 94121702004, 94121809718, 94122004259, 94122303280, 94122303822, 94122503048, 95010400388, 95010709920, 95010810075, 95011001595, 95011007782, 95011401081, 95011502683, 95011502843, 95011603834, 95011609083, 95011705987, 95011901116, 95012310603, 95012509214, 95012700172, 95012700820, 95012700844, 95012702273, 95012713079, 95012800445, 95013000240, 95020105468, 95020204198, 95020500645, 95020503396, 95020604868, 95020611783, 95020611981, 95020709044, 95020802860, 95020803366, 95020910967, 95021204388, 95021206502, 95021303360, 95021400043, 95021400944, 95021502400, 95021607365, 95021707805, 95021804359, 95022000259, 95022102364, 95022104625, 95022303895, 95022400240, 95022402228, 95022603797, 95022605522, 95022610445, 95022706162, 95030109722, 95030111673, 95030311004, 95030409747, 95030701160, 95030704347, 95030812840, 95030900224, 95030904815, 95030911129, 95031005768, 95031100432, 95031108720, 95031403474, 95031502845, 95031602750, 95031805023, 95031809652, 95032005248, 95032101098, 95032200421, 95032400807, 95032408904, 95032503333, 95032605004, 95032801066, 95032906006, 95032906143, 95032912227, 95033009982, 95033100645, 95033109354, 95040108968, 95040201302, 95040307527, 95040705134, 95040804307, 95040805360, 95040808271, 95040900249, 95041003545, 95041006029, 95041108776, 95041205862, 95041302286, 95041401855, 95041507056, 95041602478, 95041602638, 95041703322, 95041703407, 95041802373, 95041811108, 95041909391, 95042105741, 95042210906, 95042306401, 95042401564, 95042401878, 95042504090, 95042606648, 95042608244, 95042806550, 95050302707, 95050403293, 95050403668, 95050702668, 95050901029, 95051005906, 95051202723, 95051212245, 95051504139, 95051512895, 95051603029, 95051701086, 95051804840, 95051812049, 95051900102, 95052208810, 95052304349, 95052609949, 95052701702, 95053013110, 95053105604, 95060200945, 95060208608, 95060301929, 95060404325, 95060508463, 95060511209, 95060700865, 95060802307, 95060807166, 95061100589, 95061105522, 95061400498, 95061401802, 95061503924, 95061601394, 95061702866, 95061707441, 95061911152, 95062101862, 95062107776, 95062210977, 95062211466, 95062701109, 95062809678, 95062900928, 95062904465, 95062906948, 95063001260, 95063002612, 95070100321, 95070200410, 95070306352, 95070306642, 95070401927, 95070403462, 95070409550, 95070605468, 95070800528, 95070800986, 95071108625, 95071204475, 95071206606, 95071210283, 95071505040, 95071505842, 95071604398, 95071700650, 95071707862, 95071803704, 95072301386, 95072304662, 95072600263, 95072606702, 95072609026, 95072701865, 95072702002, 95072801107, 95072912177, 95073005616, 95080111203, 95080205508, 95080206967, 95080404884, 95080505769, 95080506289, 95080601380, 95080601984, 95080611215, 95080808817, 95080904254, 95081102446, 95081302044, 95081302488, 95081600739, 95081601242, 95081700071, 95081704242, 95081704648, 95081807006, 95081900518, 95082000941, 95082008093, 95082100931, 95082108885, 95082405760, 95082500502, 95082708658, 95082913834, 95083001422, 95083002065, 95090111587, 95090406047, 95090501100, 95090502507, 95090606621, 95090610444, 95090704732, 95090709034, 95090801545, 95091105334, 95091209632, 95091302533, 95091401843, 95091503668, 95091505110, 95091703907, 95091802989, 95091902191, 95091902238, 95092101322, 95092104547, 95092107526, 95092109245, 95092206447, 95092208982, 95092300721, 95092506356, 95092702332, 95092800948, 95092813081, 95092901458, 95093006855, 95093009759, 95100103061, 95100103207, 95100311462, 95100401077, 95100409143, 95100505245, 95100609505, 95100905007, 95100906398, 95101005591, 95101209766, 95101309145, 95101501820, 95101601742, 95102104343, 95102108514, 95102109133, 95102200445, 95102502196, 95102703764, 95102709739, 95102901582, 95103112183, 95110203007, 95110205849, 95110305594, 95110308825, 95110400558, 95110404620, 95111011287, 95111109920, 95111407837, 95112006875, 95112202721, 95112302223, 95112404925, 95112502265, 95112903516, 95120104279, 95120104941, 95120104996, 95120404546, 95120508899, 95120800366, 95120800625, 95120801954, 95120904695, 95121007625, 95121110369, 95121202044, 95121301071, 95121304142, 95121404040, 95121503978, 95121602257, 95121809968, 95122105438, 95122200638, 95122304882, 95122600308, 95122600384, 95122702994, 95122708846, 95123001429, 96011107755, 96022103621, 96042503003, 96050503549, 96051209482, 96051902262, 96061104108, 97012110467 ]
    if int(username) in peselFromOldExperiment:
        return True # user exists and finished the old version of the experiment
    elif finished == None: #no such entity in RevLock, so new user
        return False
    else:
        return True # user exists and finished experiment


    # if finished == None: #no such entity in RevLock, so new user
    #     return False
    # else:
    #     return True # user exists and finished experiment

# to revert to full app - comment this and uncomment the below
# app = webapp2.WSGIApplication([('/', SeeYouSoon)] # wait for instructions
#
#                                                        , debug=True)

# uncomment me to make the full app work

app = webapp2.WSGIApplication([('/', MainPage), # wait for instructions
                               ('/phones', Phones), # shut down mobile phones
                               ('/pickuser', PickUser), # for tests
                               ('/welcome', Welcome), # welcome screen
                               ('/inputnumber', Inputnumber), #student id number input
                               ('/exp_structure', Exp_structure), #structure of the experiment
                               ('/pinstructions', Pinstructions), # % point instructions
                               ('/pquiz1', Pquiz1), # % ppoint quiz
                               ('/pquiz2', Pquiz2), # % ppoint quiz
                               ('/pquiz3', Pquiz3), # % ppoint quiz
                               ('/pquiz4', Pquiz4), # % ppoint quiz
                               ('/presultsp', PresultsP), # % point results if passes
                               ('/presultsf', PresultsF), # % point results if failes
                               ('/presults', Presults), # % point quiz
                               ('/einstructions_wait', Einstructions_wait), # wait for experimental instructions
                               ('/einstructions_intro', Einstructions_intro), # experimental instructions intro
                               ('/einstructions_rules1', Einstructions_rules1), # experimental instructions1
                               ('/einstructions_rules11', Einstructions_rules11), # experimental instructions11 - displayed when pquiz is failed
                               ('/einstructions_rules2', Einstructions_rules2), # experimental instructions2
                               ('/einstructions_rules3', Einstructions_rules3), # experimental instructions3
                               ('/einstructions_rules4', Einstructions_rules4), # experimental instructions4
                               ('/einstructions_rules5', Einstructions_rules5), # experimental instructions5
                               ('/equiz', Equiz), # experimental instructions quiz
                               ('/eresults', Eresults), # experimental instructions quiz
                               ('/nmi_instructions', Nmi_instructions), # neutral mood induction - chicago
                               ('/nmi_read', Nmi_read), # neutral mood induction
                               ('/nmi_questions', Nmi_questions), # neutral mood induction questions
                               ('/nmic', Nmic), # neutral mood induction check
                               ('/ai', Ai), # analytical induction
                               ('/aic', Aic), # analytical induction check
                               ('/forecast', Forecast), # analytical induction check
                               ('/tasks_instructions', Tasks_instructions), # instructions for tasks
                               ('/tasks', Tasks), # tasks 1-4
                               ('/prev', Prev), # prevention
                               ('/te', Te), # time preference elicitation
                               ('/RteHL', RteHL), # risk and trust elicitation, H&L lottery
                               ('/RteDM1', RteDM1), # risk and trust elicitation, DOSPERT-M
                               ('/RteDM2', RteDM2), # risk and trust elicitation, DOSPERT-M
                               ('/RteDM3', RteDM3), # risk and trust elicitation, DOSPERT-M
                               ('/RteDM4', RteDM4), # risk and trust elicitation, DOSPERT-M
                               ('/RteDM5', RteDM5), # risk and trust elicitation, DOSPERT-M
                               ('/RteDM6', RteDM6), # risk and trust elicitation, DOSPERT-M
                               ('/RteSOEP', RteSOEP), # risk and trust elicitation, SOEP
                               ('/RteM', RteM), # risk and trust elicitation, Miller - coping
                               ('/RteLOC', RteLOC), # risk and trust elicitation, Locus of control
                               ('/RteBIS', RteBIS), # risk and trust elicitation, BIS-scale
                               ('/RteBAS', RteBAS), # risk and trust elicitation, BAS-fun
                               ('/RteREI', RteREI), # risk and trust elicitation, REI
                               ('/RteIMP', RteIMP), # risk and trust elicitation, impulsiveness
                               ('/RteBED', RteBED), # binge eating and BMI questions
                               ('/RtePIL', RtePIL), # risk and trust elicitation, purpose in life
                               ('/RteSELFE', RteSELFE), # demographics
                               ('/RteDEMO', RteDEMO), # demographics
                               ('/other', Other), # other data elicitation
                               ('/AddABG', AddABG), # Ania's questions 1
                               ('/AddABG2', AddABG2), # Ania's questions 2
                               ('/rev', Rev), # reveal phase
                               ('/pulse', Pulse), # API accepting POST requests from /tasks
                               ('/logout', Logout), # clears cookie
                               ('/experiment', Experiment),
                               ('/thankyou', ThankYou),
                               # ('/viewer', Viewer),
                               ('/login', Login), # login to access sensitive data - password in code
                               ('/secretviewer', SecretViewer),
                               ('/test', Test),
                               ('/getdata', GetData),
                               ('/getdataHL', GetDataHL),
                               ('/subjectdata', SubjectData), # DW sensitive data form
                               ('/agreement', Agreement), # DW oswiadczenie woli
                               ('/end', End), # last screen
                               ('/test1', Test1)]
                               , debug=True)

