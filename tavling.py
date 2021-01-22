from datetime import datetime,date,time
from random import shuffle

class Team:
#Class to define a curling team
	def __init__(self, club, roster, name = None, skip = 0):
		self.club = club
		self.roster = roster
		if name == None:
			skipname = roster[skip]
			spaces = skipname.rfind(' ')
			name = skipname[spaces+1:]
		self.name = name
	
	def __str__(self):
	#Define output of the 'print' statement
		return self.name
		
	def fullname(self):
	#Get full name of team, including club	
		if len(self.club) > 0:
			return self.club + '/' + self.name
		else:
			return self.name
	
	def __eq__(self,oth):
	#Define equality between teams
		return self.name == oth.name
		
class Match:
#Class to define a curling match
	def __init__(self, team1, team2):
		if team1 == team2:
			return
		self.hometeam = team1
		self.awayteam = team2
		self.loc = None
		self.unfinish()
		
	def switchhometeam(self):
		temp = self.hometeam
		self.hometeam = self.awayteam
		self.awayteam = temp
	
	def finish(self,result):
	#Result is given as a list of end-by-end scores
	#Negative numbers indicate away team score
		self.result = result
		awaypts = 0
		homepts = 0
		for i in result:
			if i > 0:
				homepts += i
			else:
				awaypts += i
		self.homepts = homepts
		self.awaypts = -awaypts #negative values in list
		
	def unfinish(self):
		self.result = []
		self.homepts = ''
		self.awaypts = ''
		
	def isfinished(self):
		return len(self.result) > 0		
		
	def matchupstr(self):
		return self.hometeam.name + ' - ' + self.awayteam.name
		
	def resultstr(self, reverse = False):
		if reverse:
			return '{1}-{0}'.format(self.homepts,self.awaypts)
		return '{0}-{1}'.format(self.homepts,self.awaypts)
		
	def htmlmatch(self, nbrends, bgcolor = 'white', txtcolor = 'black'):
		toprow = '<tr bgcolor="{0}"><td width="200"></td>'.format(bgcolor)
		homerow = '<tr><td>{0}</td>'.format(self.hometeam)
		awayrow = '<tr><td>{0}</td>'.format(self.awayteam)
		zerow = '<td>0</td>'
		xrow = '<td>X</td>'
		emptyrow = '<td> </td>'
		for i in xrange(nbrends+1):
			if i < nbrends:
				endname = i+1
			else:
				endname = 'EE'
			toprow += '<td><font color="{0}">{1}</font></td>'.format(txtcolor,endname)
			if i < len(self.result):
				eres = self.result[i]
				if eres >= 0:
					homerow += '<td>{0}</td>'.format(eres)
					awayrow += zerow
				else:
					homerow += zerow
					awayrow += '<td>{0}</td>'.format(-eres)
			elif not self.isfinished():
				homerow += emptyrow
				awayrow += emptyrow
			else:
				homerow += xrow
				awayrow += xrow
		
		toprow += '<td><font color="{0}">Total</font></td></tr>'.format(txtcolor)
		homerow += '<td>{0}</td></tr>'.format(self.homepts)
		awayrow +='<td>{0}</td></tr>'.format(self.awaypts)
		return '<table border="1" width="400">' + toprow + homerow + awayrow + '</table>'
	
	def __str__(self):
	#Define output of the 'print' statement
		return self.matchupstr() + '   ' + self.resultstr()


class Matchloc:
#Class to define lane and time of a curling match
	def __init__(self,dt,lanenbr):
		self.dt = dt
		self.lane = lanenbr
		self.match = None
		
	def addmatch(self,match):
		self.empty()
		match.loc = self
		self.match = match
	
	def empty(self):
		if self.match == None:
			return
		match = self.match
		match.loc = None
		self.match = None
	
	def __eq__(self,oth):
		if not isinstance(oth, Matchloc):
			return False
		return self.dt==self.dt and self.lane==oth.lane
		
	def datestr(self):
		return self.dt.strftime('%y-%m-%d')
	
	def timestr(self):
		return self.dt.strftime('%H:%M')
		
	def __str__(self):
		return '{0} {1} Bana {2} {3}'.format(self.datestr(), self.timestr(), self.lane, str(self.match))
		
class Schedule:
#Class to define the schedule of a tournament
	def __init__(self, nbroflanes, datetimes):
		self.schedule = []
		datetimes.sort()
		for dt in datetimes:
			self.schedule.append(Session(dt,[Matchloc(dt,i+1) for i in xrange(nbroflanes)]))
			#for i in xrange(nbroflanes):
			#	self.schedule.append(Matchloc(dt,i+1)) #there is no lane 0

	def getmatchesat(self, dateandortime, upto = False):
	#Method to get matches at (or up until) a certain date or time defined by datetime object
		matchlist = []
		isdatetime = isinstance(dateandortime, datetime)
		for session in self.schedule:
			if session.dt == dateandortime or session.dt.date() == dateandortime:
				matchlist += [loc.match for loc in session]
				if isdatetime:
					break
			elif not isdatetime and session.dt.date() > dateandortime:
				break
			elif upto:
				matchlist += [loc.match for loc in session]
		return matchlist
				

	def getteamsat(self, dateandtime, upto = False):
	#Method to get a list of all teams playing at a certain date or time
		teamlist = []
		for match in self.getmatchesat(dateandtime,upto):
			if match != None:
				teamlist += [match.hometeam, match.awayteam]
		return teamlist

	def noclash(self, match, loc, teamlist, lim = 3):
	#Method to check if a schedule spot is available for a match 

		#Check if spot is taken
		if loc.match != None:
			return False
		
		team1 = match.hometeam
		team2 = match.awayteam
		
		#Check if either team is already scheduled at the same time
		teamsnow = self.getteamsat(loc.dt)
		#Try this to help the menu...
		#teamsnow = [t for t in teamsnow if loc.match == None or (t != loc.match.hometeam and t != loc.match.awayteam)]
		if team1 in teamsnow or team2 in teamsnow:
			return False
		
		#Check if either team has reached its match limit for the day
		teamstoday = self.getteamsat(loc.dt.date())
		if teamstoday.count(team1) >= lim or teamstoday.count(team2) >= lim:
			return False

		#Check if this match makes one team get too far ahead/behind in the schedule
		teamsuntilnow = self.getteamsat(loc.dt, upto = True)
		restteams = [t for t in teamlist if t != team1 and t != team2]
		counts = [teamsuntilnow.count(team) for team in restteams]
		if teamsuntilnow.count(team1) - min(counts) > 1 or teamsuntilnow.count(team2) - min(counts) > 1:
			return False
		return True
		
	def __str__(self):
	#Define output of the 'print' statement
		stri = ''
		for session in self.schedule:
			for loc in session:
				stri += str(loc) + '\n'
		return stri
	
	def __getitem__(self,key):
	#Define evaluation of the self[key] command
		if isinstance(key, datetime):
			for session in self.schedule:
				if session.dt == key:
					return session
			else:
				return []
		else:
			return self.schedule[key]
	
	def __iter__(self):
		return iter(self.schedule)
		
	def __len__(self):
		return len(self.schedule)
		
	def append(self, session):
		self.schedule.append(session)
		
	def getlanes(self):
		return [loc.lane for loc in self.schedule[0]]
		
class Session:
	def __init__(self, dateandtime, loclist):
		self.dt = dateandtime
		self.locs = loclist
	
	def __getitem__(self,key):
	#Define evaluation of the self[key] command
		return self.locs[key]
		
	def __iter__(self):
		return iter(self.locs)
	
	def __len__(self):
		return len(self.locs)
				
	def isfull(self):
		return None not in [loc.match for loc in self.locs]

class Tourney:
#Class to define a curling tournament
	def __init__(self, name, teams = [], nbrends = 8):
		self.name = name
		self.teams = teams
		self.nbrends = nbrends
		if nbrends > 8:
			matchlimit = 2
		else:
			matchlimit = 3 
		self.teammatchlimit = matchlimit
		self.schedule = None
		self.matches = []
		
	def addteam(self,team):
		self.teams.append(team)
		
	def removeteam(self, team):
		for match in self.getteammatches(team):
			del match
		self.teams.remove(team)
	
	def getteammatches(self,team):
		matchlist = []
		for match in self.matches:
			if team == match.hometeam or team == match.awayteam:
				matchlist.append(match)
		return matchlist
		
	def makeschedule(self, nbroflanes, datetimes):
		self.schedule = Schedule(nbroflanes, datetimes)
		
	def updateschedule(self, nbroflanes, datetimes):
		if self.schedule == None:
			self.makeschedule(nbroflanes, datetimes)
			return
		for i, dt in enumerate(datetimes):
			if i < len(self.schedule):
				session = self.schedule[i]
				session.dt = dt
				oldlocs = session.locs
				newlocs = []
				for j in xrange(nbroflanes):
					if j < len(oldlocs):
						newlocs.append(oldlocs[j])
					else:
						newlocs.append(Matchloc(datetimes[i],j))
				session.locs = newlocs
			else:
				locs = [Matchloc(dt, l+1) for l in xrange(nbroflanes)]
				session = Session(dt, locs)
				self.schedule.append(session)
					
	def fillschedule(self):
	#Attempt to fill schedule with matches, making sure no clashes
		if self.schedule == None or len(self.matches) == 0:
			return
		matchlist = [match for match in self.matches if match.loc == None]
		played = [0 for team in self.teams]
		for session in self.schedule:
			self.fillsession(session, matchlist)
	
	def fillsession(self, session, matchlist):
	#Helper function for fillschedule
		i = 0
		tries = 0
		while not session.isfull():
			loc = session[i]
			for match in matchlist:
				if self.schedule.noclash(match, loc, self.teams, self.teammatchlimit):
					loc.addmatch(match)
					matchlist.remove(match)
					i += 1
					break #next loc
			else:
			#go back one loc and try a different match
				if i == 0 or len(matchlist) == 0 or tries > 10:
					return
				tries += 1
				i -= 1
				matchlist.append(session[i].match)
				session[i].empty()
					 						
		
	def printschedule(self):
		print self.schedule
		
	def htmlschedule(self, dtformat = '%y-%m-%d %H:%M', bgcolor = 'white', txtcolor = 'black'):
		stri = '<table border="1">'
		topstri = '<tr bgcolor="{0}"><td></td>'.format(bgcolor)
		for lane in self.schedule.getlanes():
			topstri += '<td><font color="{0}"><strong>Bana {1}</strong></font></td>'.format(txtcolor, lane)
		stri += topstri + '</tr>'
		for session in self.schedule:
			sesstri = '<tr><td bgcolor="{0}"><font color="{1}"><strong>{2}</strong></font></td>'.format(bgcolor, txtcolor, session.dt.strftime(dtformat))
			for loc in session:
				if loc.match != None:
					sesstri += '<td>{0}</td>'.format(loc.match.matchupstr())
				else:
					sesstri += '<td></td>'
			stri += sesstri
		return stri + '</table>'
	
	def htmlresults(self, dtformat = '%y-%m-%d %H:%M', bgcolor = 'white', txtcolor = 'black'):
		stri = ''
		for session in self.schedule:
			sesstri = ''
			for loc in session:
				if loc.match != None and loc.match.isfinished():
					sesstri += loc.match.htmlmatch(self.nbrends, bgcolor, txtcolor)
			if len(sesstri) > 0:
				stri += '<h4>{0}</h4>{1}'.format(session.dt.strftime(dtformat),sesstri)
		return stri
	
	def htmlrosters(self):
	#Return string of html code for displaying team rosters
		stri = '<table>'
		for team in self.teams:
			tstri = '<tr><td><strong>{0}</strong></td><td>'
			for n in range(len(team.roster)):
				if n > 0:
					tstri += ', '
				tstri += '{' + str(n+1) + '}'
			stri += (tstri +'</td></tr>').format(team.fullname(),*team.roster)
		return stri + '</table>'
		

class League(Tourney):
#Subclass of Tourney to define a league format tournament

	def __init__(self,*args):
		Tourney.__init__(self,*args)
		self.table = Table(self.teams)
	
	def addteam(self,team):
		self.teams.append(team)
		self.table = Table(self.teams)
	
	def makematches(self, headtoheads = 1):
		fulllist = []
		halflist = []
		teamlist = [team for team in self.teams]
		shuffle(teamlist)
		for i,hometeam in enumerate(teamlist):
			for j,awayteam in enumerate(teamlist):
				if hometeam != awayteam:
					fulllist.append(Match(hometeam,awayteam))
					if (j-i)%99%2 == 1:
						halflist.append(Match(hometeam,awayteam))
		self.matches = fulllist*(headtoheads/2) + halflist*(headtoheads%2)		
		
	def calctable(self):
	#Calculate table of standings
		for entry in self.table:
			entry.wins = 0
			entry.ties = 0
			entry.loss = 0
		table = self.table
		for match in self.matches:
			if len(match.result)>0:
				if match.homepts > match.awaypts:
					table[match.hometeam].wins += 1
					table[match.awayteam].loss += 1
				elif match.awaypts > match.homepts:
					table[match.awayteam].wins += 1
					table[match.hometeam].loss += 1
				else:
					table[match.awayteam].ties += 1
					table[match.hometeam].ties += 1
		table.sort()
		
		curpts = -1
		curteams = []
		for [i,entry] in enumerate(table):
			if entry.getpoints() == curpts:
				curteams.append(entry.team)
			else:
				if len(curteams) > 1:
					teamsout = self.makesubleague(curteams)
					entries = [table[team] for team in teamsout]
					for [j,ent] in enumerate(entries):
						table.table[i-j-1] = ent
				curpts = entry.getpoints()
				curteams = [entry.team]
		
		self.table = table
		
	def makesubleague(self, teamlist):
		subleague = League("subleague", teamlist, self.nbrends)
		for team in teamlist:
			subleague.table[team].settee(self.table[team].tee)
		for match in self.matches:
			if match.hometeam in teamlist and match.awayteam in teamlist:
				subleague.matches.append(match)
		subleague.calctable()
		teamlistout = []
		for entry in subleague.table:
			teamlistout.append(entry.team)
		teamlistout.reverse() #reverse to get last first
		return teamlistout
		
	def htmlmatrix(self, repeat = True, bgcolor = 'white', txtcolor = 'black'):
	#Return html string of result matrix, which can be written to file
		nbrofteams = len(self.teams)
		resmat = [['-']*nbrofteams for i in xrange(nbrofteams)]
		for i in xrange(nbrofteams):
			resmat[i][i] = 'X'
		for match in self.matches:
			homeix = self.teams.index(match.hometeam)
			awayix = self.teams.index(match.awayteam)
			resmat[homeix][awayix] = match.resultstr()
			if repeat:
				resmat[awayix][homeix] = match.resultstr(reverse = True)
		stri = '<table border="1">'
		rowstri = '<tr><td bgcolor="{0}"><font color="{1}"><strong>'.format(bgcolor,txtcolor) + '{0}</strong></font></td>'
		toprowstri = '<tr bgcolor="{0}"><td></td>'.format(bgcolor)
		for i,team in enumerate(self.teams):
			rowstri += '<td align="center">{' + str(i+1) + '}</td>'
			toprowstri += '<td><font color="{0}"><strong>{1}</strong></font></td>'.format(txtcolor, str(team))
		stri += toprowstri + '</tr>'
		rowstri += '</tr>'
		for i,team in enumerate(self.teams):
			stri += rowstri.format(str(team),*resmat[i])
		return stri + '</table>'
			
	def printtable(self):
		print self.table
		
	def htmltable(self, headlist, bgcolor = 'white', txtcolor = 'black'):
	#Return html string of table, which can be written to file. headlist is a list containing
	#the headlines of each stat column, in order [matches, wins, ties, losses, tee, points]
		stri = '<table border="1">'
		rowstri = '<tr bgcolor = "{0}"><td>{1}</td>'
		for i,head in enumerate(headlist):
			if head != None:
				rowstri += '<td>{' + str(i+2) + '}</td>'
		rowstri += '</tr>'
		fheads = ['<font color="{0}"><strong>{1}</strong></font>'.format(txtcolor,hword) for hword in headlist]
		stri += rowstri.format(bgcolor,'',*fheads)
		for e in self.table:
			stri += rowstri.format('white',e.team.fullname(),e.wins+e.ties+e.loss,e.wins,e.ties,e.loss,e.gettee(),2*e.wins+e.ties)
		return stri + '</table>'

class RoundRobinTourney(Tourney):
	
	def __init__(self,*args):
		Tourney.__init__(self,*args)
		
	def makegroups(self, nbrofgroups = 2):
		self.groups = []
		grouplist = [[] for i in xrange(nbrofgroups)]
		teamlist = [team for team in self.teams]
		shuffle(teamlist)
		for i,team in enumerate(teamlist):
			grouplist[i % nbrofgroups].append(team)
		for i in xrange(nbrofgroups):
			group = League("Group {0}".format(i+1), grouplist[i], self.nbrends)
			self.groups.append(group)
			
	def makematches(self, headtoheads = 1):
		for group in self.groups:
			group.makematches(headtoheads)
			self.matches += group.matches
		
	def calctable(self):
		for group in self.groups:
			group.calctable()
			
	def htmlmatrix(self, **args):
		htmlstri = ''
		for group in self.groups:
			htmlstri += '<h4>{0}</h4>'.format(group.name)
			htmlstri += group.htmlmatrix(**args)
		return htmlstri
	
	def htmltable(self, **args):
		htmlstri = ''
		for group in self.groups:
			htmlstri += '<h4>{0}</h4>'.format(group.name)
			htmlstri += group.htmltable(**args)
		return htmlstri
		
class Table:
#Class to define the table of standings for a league
	def __init__(self,teamlist):
		if len(teamlist) == 0:
			return
		self.table = [TableEntry(team) for team in teamlist]
		self.maxlength = max([len(team.name) for team in teamlist])	
		
	def __getitem__(self,key):
	#Define evaluation of the self[key] command
		for entry in self:
			if entry.team == key:
				return entry
		else:
			return []
	
	def sort(self):
	#Sort table to get standings
		self.table.sort()				
	
	def __str__(self):
		stri = ''
		for entry in self:
			stri += entry.tostring(self.maxlength) + '\n'
		return stri	
	
	def __iter__(self):
		return iter(self.table)
	
class TableEntry:
#Class to define an entry of a league table
	def __init__(self,team):
		self.team = team
		self.wins = 0
		self.ties = 0
		self.loss = 0
		self.tee = None
		
	def settee(self, val):
		self.tee = val
		
	def gettee(self):
		if self.tee == None:
			return '-'
		return self.tee
		
	def getpoints(self):
		return 2*self.wins+1*self.ties

	def __cmp__(self, other):
	#Define evaluation of comparisons, for sorting of the league table
		ptcmp =  other.getpoints() - self.getpoints()
		if ptcmp != 0:
			return ptcmp
		elif self.tee == None or other.tee == None:
			if str(self.team) < str(other.team):
				return -1
			else:
				return 1
		else:
			return other.tee - self.tee
		
		
	def tostring(self, maxlength):
		namespace = self.team.name + ' '*(maxlength-len(self.team.name)) #fill up with spaces
		return namespace + ' {0} {1}'.format(self.wins,self.loss)
	
