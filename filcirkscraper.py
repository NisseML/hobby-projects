from datetime import date
from html.parser import HTMLParser
import re
import json
import pandas as pd
import urllib.request as ur

class fcHTMLParser(HTMLParser):

    def __init__(self, year):
        HTMLParser.__init__(self)
        self.lecturers = []
        self.lectures = []
        self.year = year

        self.datecoming = True
        self.titlecoming = False
        self.curlecture = None

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            pass
            #self.datecoming = True
        elif tag == 'a':
            #self.titlecoming = True
            pass

    def handle_endtag(self, tag):
        if tag == 'p':
            pass
            #self.datecoming = False
            #self.curlecture = None
        elif tag == 'a':
            pass
            #self.titlecoming = False
    
    def handle_comment(self, data):
        pass

    def handle_data(self, data):
        data = strtrim(data) #.decode('unicode-escape')
        m = re.search('\w', data)
        if m == None:
            return
        elif data[0] == '<':
            #style description
            return
        if self.datecoming:
            m1 = re.search('\d', data)
            m2 = re.search('jan|feb|mar|apr|maj|aug|sep|okt|nov|dec', data)
            if m2 == None:
                m2 = re.search('/\d+', data)
            words = re.split(' ', data)
            if m1 != None and m2 != None:
                m11 = re.search('\d\d', data)
                if m11 != None:
                    d = self.get_date(m11.group(), m2.group())
                else:
                    d = self.get_date(m1.group(), m2.group())
                self.curlecture = Lecture(d)
                self.datecoming = False
                self.titlecoming = True
        elif self.curlecture != None:
            if self.titlecoming:
                self.curlecture.title = data
                self.titlecoming = False
            else:
                self.curlecture.lecturer = data
            if self.curlecture.complete():
                #print self.curlecture.date + '\t' + self.curlecture.title + '\t' + self.curlecture.lecturer + '\n'
                self.lectures.append(self.curlecture)
                self.lecturers.append(self.curlecture.lecturer)
                self.curlecture = None
                self.datecoming = True
                
    def get_date(self, day, month):
        monthdict = {'jan':1, 'feb':2, 'mar':3, 'apr':4,
                     'maj':5, 'jun':6, 'jul':7, 'aug':8,
                     'sep':9, 'okt':10, 'nov':11, 'dec':12}
        if month in monthdict.keys():
            monthval = monthdict[month]
        else:
            monthval = int(month[1:])
        return date(year=self.year, month=monthval, day=int(day))

class Lecturer:
    def __init__(self, name, description = ''):
        self.name = name
        self.description = description

    def __eq__(self,other):
        return self.name == other.name

    def todict(self):
        return {'name':self.name, 'title':self.description}

class Lecture:
    def __init__(self, date):
        self.date = date
        self.title = None
        self.lecturer = None

    def __str__(self):
        return '%s\n%s\n%s'%(self.date,self.lecturer,self.title)
        #return u'{0}\n{1}\n{2}'.format(self.date,self.lecturer,self.title)

    def todict(self):
        return {'date':self.date, 'lecturer':self.lecturer, 'title':self.title}
        
    def complete(self):
        if self.title != None and self.lecturer != None:
            m1 = re.findall('\s',self.title)
            m2 = re.findall('\s',self.lecturer)
            if len(m1) < len(m2):
                tmp = self.title
                self.title = self.lecturer
                self.lecturer = tmp
            return True
        else:
            return False

def strtrim(stri):
    strstart = 0
    strend = len(stri)
    m = re.finditer('\s',stri)
    wsl = [s.start() for s in m]
    for i in reversed(wsl):
        if i == strend-1:
            strend = i
    for i in wsl:
        if i == strstart:
            strstart += 1
    return stri[strstart:strend]

alllecturers = set([])
alllectures = []
for year in range(1995, 2017):
    for term in [1,2]:
        filename = 'https://xje.se/video/fc{0}h{1}.htm'.format(str(year % 100).rjust(2,'0'),term)
        
        #filename = 'filcirkdata\\fc{0}h{1}.htm'.format(str(year % 100).rjust(2,'0'),term)
        try:
            fcfile = ur.urlopen(filename)
            print('Reading file {0}'.format(filename))
            filestri = str(fcfile.read(), 'iso-8859-1')
            fcfile.close()
        except:
            filestri = ''
        parser = fcHTMLParser(year)
        parser.feed(filestri)
        alllecturers = alllecturers | set(parser.lecturers)
        alllectures += parser.lectures

wfile = open('alllectures.json','w')
lecturersobj = [Lecturer(lcr).todict() for lcr in alllecturers]
#for lcr in alllectures:
#    print lcr
#json.dump(wfile,lecturersobj)

df_fc = pd.DataFrame(index=[lc.date for lc in alllectures])
df_fc['lecturer'] = [lc.lecturer for lc in alllectures]
df_fc['title'] = [lc.title for lc in alllectures]
df_fc['title'] = df_fc['title'].str.replace('\s+', ' ')