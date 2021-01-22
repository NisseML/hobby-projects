from Tkinter import *
from tavling import *
from datetime import *
import pickle

class CurlingApp(Frame):

	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack()
		self.createWidgets()
		
	def createWidgets(self):
		self.QUIT = Button(self)
		self.QUIT["text"] = "QUIT"
		self.QUIT["command"] = self.quit
		self.QUIT.grid(column = 0, row = 0)
		
		self.createtourney = Button(self)
		self.createtourney["text"] = "Create tournament"
		self.createtourney["command"] = self.createtourney_Callback
		self.createtourney.grid(column = 3, row = 0)
		
		self.loadbutton = Button(self)
		self.loadbutton["text"] = "Load"
		self.loadbutton["command"] = self.load
		self.loadbutton.grid(column = 2, row = 0)
		
		self.tourneyname = Entry(self)
		self.tourneyname.grid(column = 1, row = 0)
		
	def createTourneyWidgets(self):
		#Clean up
		self.createtourney["state"] = DISABLED
		
		clublbl = Label(self, text = 'Club')
		clublbl.grid(column = 0, row = 1)
		self.clubentry = Entry(self)
		self.clubentry.grid(column = 1, row = 1)
		namelbl = Label(self, text = 'Team name')
		namelbl.grid(column = 0, row = 2)
		self.nameentry = Entry(self)
		self.nameentry.grid(column = 1, row = 2)
		
		self.playerentry = []
		self.skipradiobutton = []
		self.skipvar = IntVar()
		self.skipvar.set(0)
		poslist = ['Fourth','Third','Second','Lead','Alternate']
		for i in xrange(5):
			crow = i+3
			playerlbl = Label(self)
			playerlbl["text"] = poslist[i]
			playerlbl.grid(column = 0, row = crow)
			self.playerentry.append(Entry(self))
			self.playerentry[i].grid(column = 1, row = crow)
			self.skipradiobutton.append(Radiobutton(self, variable = self.skipvar, value = i))
			self.skipradiobutton[i].grid(column = 2, row = crow)
			self.skipradiobutton[i]["command"] = self.skipradiobutton_Callback
		self.skipradiobutton[self.skipvar.get()]["text"] = "Skip"
		
		self.addteam = Button(self)
		self.addteam["text"] = "Add team"
		self.addteam["command"] = self.addteam_Callback
		self.addteam.grid(column = 2, row = 1)
		
		self.ends = IntVar()
		self.ends.set(8)		
		self.endscontrol = Menubutton(self, text = "Ends per match")
		endsmenu = Menu(self.endscontrol)
		for l in range(1,11):
			endsmenu.add_radiobutton(variable = self.ends, value = l, label = str(l), command = self.endsupdate)
		self.endscontrol["menu"] = endsmenu
		self.endscontrol.grid(column = 3, row = 1)
		
		self.headtoheads = IntVar()
		self.headtoheads.set(1)
		self.singleradiobutton = Radiobutton(self, text = "Single round", variable = self.headtoheads, value = 1)
		self.singleradiobutton.grid(column = 3, row = 2)
		self.doubleradiobutton = Radiobutton(self, text = "Double round", variable = self.headtoheads, value = 2)
		self.doubleradiobutton.grid(column = 3, row = 3)
		
		self.nbrgroups = IntVar()
		self.nbrgroups.set(1)
		self.nbrgroupscontrol = Menubutton(self, text = "Nbr of groups")
		self.nbrgroupsupdate()
		self.nbrgroupscontrol.grid(column = 3, row = 4)
		
		self.teammatchlimit = IntVar()
		self.teammatchlimit.set(2)
		self.limitcontrol = Menubutton(self, text = "Matches/day")
		self.limitupdate()
		self.limitcontrol.grid(column = 3, row = 5)
		
		self.buttonframe = Frame(self)
		self.buttonframe.grid(column = 0, row = 8, columnspan = 10)
		
		self.generatematches = Button(self.buttonframe)
		self.generatematches["text"] = "Make schedule"
		self.generatematches["command"] = self.generateschedule
		self.generatematches.grid(column = 1, row = 0)
		
		self.fillbutton = Button(self.buttonframe)
		self.fillbutton["text"] = "Fill schedule"
		self.fillbutton["command"] = self.fillschedule
		self.fillbutton.grid(column = 2, row = 0)
		
		self.addsessionbutton = Button(self.buttonframe)
		self.addsessionbutton["text"] = "Add session"
		self.addsessionbutton["command"] = self.addsession
		self.addsessionbutton.grid(column = 0, row = 0, sticky = W)
		
		self.savebutton = Button(self.buttonframe)
		self.savebutton["text"] = "Save tournament"
		self.savebutton["command"] = self.save
		self.savebutton.grid(column = 3, row = 0)
		
		self.htmlbutton = Button(self.buttonframe)
		self.htmlbutton["text"] = "Write to HTML"
		self.htmlbutton["command"] = self.writetohtml
		self.htmlbutton.grid(column = 4, row = 0)
		
		self.scheduleframe = Frame(self)
		self.scheduleframe.grid(column = 0, row = 9, columnspan = 10, sticky = W)
		
		self.lanes = IntVar()
		self.lanescontrol = Menubutton(self.scheduleframe, text = "Nbr of lanes")
		lanesmenu = Menu(self.lanescontrol)
		for l in range(1,13):
			lanesmenu.add_radiobutton(variable = self.lanes, value = l, label = str(l), command = self.dolanes)
		self.lanescontrol["menu"] = lanesmenu
		self.lanescontrol.grid(column = 0, row = 0, columnspan = 5, sticky = W)
		
		self.teamlabels = []
		self.editbuttons = []
		self.removebuttons = []
		self.scheduledates = []
		self.lanelabels = []
		self.schedulecontrol = []
		
	def nbrgroupsupdate(self):
		nbrgroupsmenu = Menu(self.nbrgroupscontrol)
		maxgroups = len(self.tourney.teams)/2
		for n in range(1,maxgroups+1):
			nbrgroupsmenu.add_radiobutton(variable = self.nbrgroups, value = n, label = str(n))
		self.nbrgroupscontrol["menu"] = nbrgroupsmenu
	
	def limitupdate(self):
		limitmenu = Menu(self.limitcontrol)
		for n in [2,3]:
			limitmenu.add_radiobutton(variable = self.teammatchlimit, value = n, label = str(n), command = self.updateteammatchlimit)
		self.limitcontrol["menu"] = limitmenu
	
	def updateteammatchlimit(self):
		self.tourney.teammatchlimit = self.teammatchlimit.get()
	
	def createtourney_Callback(self):
		self.tourney = League(self.tourneyname.get())
		self.createTourneyWidgets()
		
	def addteam_Callback(self):
		roster = []
		for i in xrange(5):
			player = self.playerentry[i].get()
			if player == "":
				break
			roster.append(player)
			self.playerentry[i].delete(0,END)
		teamname = self.nameentry.get()
		if len(teamname) == 0:
			teamname = None
		newteam = Team(self.clubentry.get(), roster, name = teamname, skip = self.skipvar.get())
		self.tourney.addteam(newteam)
		self.printteams()
		self.nbrgroupsupdate()
		
	def printteams(self):
		for label,button1,button2 in zip(self.teamlabels, self.editbuttons, self.removebuttons):
			label.destroy()
			button1.destroy()
			button2.destroy()
		self.teamlabels = []
		self.editbuttons = []
		self.removebuttons = []
		self.teevals = []
		self.teemenus = []
		self.halfvals = []
		for i, team in enumerate(self.tourney.teams):
			row = i % 7
			col = 4+4*(i/7)
			self.teamlabels.append(Label(self, text = str(team)))
			self.teamlabels[i].grid(column = col, row = row)
			self.editbuttons.append(Button(self, text = "Edit", command = self.editbutton_Callback(team)))
			self.editbuttons[i].grid(column = col+1, row = row)
			self.removebuttons.append(Button(self, text = "Remove", command = self.removebutton_Callback(team)))
			self.removebuttons[i].grid(column = col+2, row = row)
			self.teevals.append(IntVar())
			self.halfvals.append(IntVar())
			self.teevals[i].set(-1)
			self.halfvals[i].set(0)
			self.teemenus.append(Menubutton(self, text = "Tee"))
			teemenus = Menu(self.teemenus[i])
			for j in range(-1,21):
				teemenus.add_radiobutton(variable = self.teevals[i], value = j, label = str(j), command = self.tee_Callback(team,i))
			teemenus.add_checkbutton(variable = self.halfvals[i], label = "+0.5", command = self.tee_Callback(team,i))
			self.teemenus[i]["menu"] = teemenus
			self.teemenus[i].grid(column = col+3, row = row)
	
	def tee_Callback(self,team,i):
		def callback():
			n = self.teevals[i].get()
			half = self.halfvals[i].get()
			if n == -1:
				self.tourney.table[team].settee(None)
			elif half == 0:
				self.tourney.table[team].settee(n)
			else:
				self.tourney.table[team].settee(n+0.5)
		return callback
			
	def skipradiobutton_Callback(self):
		for button in self.skipradiobutton:
			button["text"] = ""
		self.skipradiobutton[self.skipvar.get()]["text"] = "Skip"
		
	def editbutton_Callback(self, team):
		def callback():
			self.clubentry.delete(0,END)
			self.clubentry.insert(0, team.club)
			self.nameentry.delete(0,END)
			self.nameentry.insert(0, team.name)
			for i, player in enumerate(team.roster):
				self.playerentry[i].delete(0,END)
				self.playerentry[i].insert(0, player)
			self.addteam["command"] = lambda : self.saveedited(team)
			self.addteam["text"] = "Save"
		return callback
		
	def saveedited(self, team):
		roster = []
		for i in xrange(5):
			player = self.playerentry[i].get()
			if player == "":
				break
			roster.append(player)
			self.playerentry[i].delete(0,END)
		clubname = self.clubentry.get()
		teamname = self.nameentry.get()
		if len(teamname) != 0:
			team.name = teamname
		if len(clubname) != 0:
			team.club = clubname
		team.roster = roster
		self.addteam["command"] = self.addteam_Callback
		self.addteam["text"] = "Add team"
		
	def removebutton_Callback(self, team):
		def callback():
			self.tourney.removeteam(team)
			self.printteams()
			self.nbrgroupsupdate()
		return callback
		
	def endsupdate(self):
		nbrends = self.ends.get()
		self.tourney.nbrends = nbrends
		if nbrends > 8:
			self.tourney.teammatchlimit = 2
		else:
			self.tourney.teammatchlimit = 3
	
	def addsession(self, preset = None):
		lend = len(self.scheduledates)
		if lend > 0 and preset == None:
			preset = self.scheduledates[-1].datetime
		self.scheduledates.append(Datecontrol(self.scheduleframe, lend+1, 0, preset))
	
	def dolanes(self):
		[label.destroy() for label in self.lanelabels]
		self.lanelabels = []
		for i in xrange(self.lanes.get()):
			label = Label(self.scheduleframe, text = 'Lane {0}'.format(i+1))
			label.grid(row = 0, column = i+5)
			self.lanelabels.append(label)
		
	def generateschedule(self):
		if isinstance(self, RoundRobinTourney):
			self.tourney.makegroups(self.nbrgroups.get())
		self.tourney.makematches(self.headtoheads.get())
		datetimes = [dates.datetime for dates in self.scheduledates]
		nbroflanes = self.lanes.get()
		self.tourney.makeschedule(nbroflanes, datetimes)
		try:
			self.schedulecontrol.destroy()
		except:
			pass
		self.schedulecontrol = Schedulecontrol(self.scheduleframe, self.tourney)
		self.tourney.teammatchlimit = self.teammatchlimit.get()
	
	def updateschedule(self):
		datetimes = [dates.datetime for dates in self.scheduledates]
		for i, dt in enumerate(datetimes):
			if i < len(self.tourney.schedule):
				self.tourney.schedule[i].dt = dt
				for loc in self.tourney.schedule[i]:
					loc.dt = dt
	
	def fillschedule(self):
		self.tourney.teammatchlimit = self.teammatchlimit.get()
		self.tourney.fillschedule()
		self.schedulecontrol.updatematchnbr()
		
	def save(self):
		self.tourney.name = self.tourneyname.get()
		self.updateschedule()
		f = open('{0}.tav'.format(self.tourney.name), 'w')
		pickle.dump(self.tourney, f)
		f.close()
		
	def load(self):
		f = open('{0}.tav'.format(self.tourneyname.get()), 'r')
		self.tourney = pickle.load(f)
		f.close()
		self.createTourneyWidgets()
		self.update()
		
	def writetohtml(self):
		self.tourney.name = self.tourneyname.get()
		self.updateschedule()
		root = Tk()
		mres = HtmlWriteGUI(self.tourney, master = root)
		mres.mainloop()
		
	def update(self):
		self.tourneyname.delete(0, END)
		self.tourneyname.insert(0, self.tourney.name)
		self.printteams()
		self.ends.set(self.tourney.nbrends)
		self.schedulecontrol = Schedulecontrol(self.scheduleframe, self.tourney)
		self.schedulecontrol.update()
		
		#Update schedule display
		if self.tourney.schedule != None:
			self.lanes.set(len(self.tourney.schedule[0]))
			self.dolanes()
			for session in self.tourney.schedule:
				self.addsession(session.dt)
		
class Schedulecontrol:

	def __init__(self, parent, tourney):
		self.matchcontrols = []
		for session in tourney.schedule:
			for loc in session:
				self.matchcontrols.append(Matchcontrol(self, parent, tourney, loc))
		
	def destroy(self):
		[mc.destroy() for mc in self.matchcontrols]
	
	def update(self):
		[mc.update() for mc in self.matchcontrols]
		
	def updatematchnbr(self):
		[mc.updatematchnbr() for mc in self.matchcontrols]
			
	
class Matchcontrol:

	def __init__(self, schedulecontrol, parent, tourney, loc):
		self.schedulecontrol = schedulecontrol
		self.parent = parent
		self.tourney = tourney
		self.loc = loc
		
		self.matchnbr = IntVar()
		self.menu = Menubutton(self.parent)
		
		self.updatematchnbr()
		
		datetimes = [session.dt for session in tourney.schedule]
		row = datetimes.index(loc.dt) + 1
		col = loc.lane + 4
		self.menu.grid(column = col, row = row)
		
	def updatematchnbr(self):
		if self.loc.match == None:
			self.matchnbr.set(-1)
		else:
			self.matchnbr.set(self.tourney.matches.index(self.loc.match))
		self.update()
	
	def update(self):
		matchmenu = Menu(self.menu)
		if self.matchnbr.get() < 0:
			txt = "Empty"
			self.loc.empty()
		else:
			selectmatch = self.tourney.matches[self.matchnbr.get()]
			self.loc.addmatch(selectmatch)
			txt = str(selectmatch)
			matchmenu.add_command(label = "Finish", command = self.finishmatch_Callback(selectmatch))
			matchmenu.add_command(label = "Unfinish", command = self.unfinishmatch_Callback(selectmatch))
			matchmenu.add_command(label = "Switch home/away", command = self.switchhometeam_Callback(selectmatch))
			lanemenu = Menu(matchmenu)
			for lnbr in self.tourney.schedule.getlanes():
				if lnbr != self.loc.lane:
					lanemenu.add_command(label = str(lnbr), command = self.switchlane_Callback(selectmatch, lnbr))
			matchmenu.add_cascade(label = "Move to lane", menu = lanemenu)
			matchmenu.add_separator()
		self.menu["text"] = txt
		
		matchmenu.add_radiobutton(variable = self.matchnbr, value = -1, label = "Empty", command = self.schedulecontrol.update)
		for i in range(len(self.tourney.matches)):
			match = self.tourney.matches[i]
			if match.loc == None and self.tourney.schedule.noclash(match, self.loc, self.tourney.teams):
				matchmenu.add_radiobutton(variable = self.matchnbr, value = i, label = str(match), command = self.schedulecontrol.update)
		self.menu["menu"] = matchmenu
	
	def finishmatch_Callback(self, match):
		def callback():
			root = Tk()
			mres = MatchResult(match, self.tourney.nbrends, master = root)
			mres.mainloop()
			root.destroy()
			self.update()
		return callback
		
	def unfinishmatch_Callback(self, match):
		def callback():
			match.unfinish()
			self.update()
		return callback
		
	def switchhometeam_Callback(self, match):
		def callback():
			match.switchhometeam()
			self.update()
		return callback
		
	def switchlane_Callback(self, match, lane):
		def callback():
			session = self.tourney.schedule[self.loc.dt]
			for loc in session:
				if loc.lane == lane:
					othmatch = loc.match
					loc.addmatch(match)
			if othmatch != None:
				self.loc.addmatch(othmatch)
			else:
				self.loc.empty()
			self.schedulecontrol.updatematchnbr()	
		return callback
	
	def destroy(self):
		self.menu.destroy()
	
class Datecontrol:
		
	def __init__(self, parent, row, column, presetdate = None):
		if presetdate == None:
			self.datetime = datetime.now().replace(minute = 0, second = 0, microsecond = 0)
			self.datemin = datetime.min
		else:
			self.datemin = presetdate
			self.datetime = presetdate
		self.parent = parent
		self.row = row
		self.col = column
		self.inityear()
		self.initmonth()
		self.initday()
		self.inithour()
		self.initminute()
		self.update()
		
	def inityear(self):
		self.year = IntVar()
		self.year.set(self.datetime.year)
		self.yearcontrol = Menubutton(self.parent)
		
		yearmenu = Menu(self.yearcontrol)
		for y in range(2000,2100):
			yearmenu.add_radiobutton(variable = self.year, value = y, label = str(y), command = self.update)
		self.yearcontrol["menu"] = yearmenu
		
		self.yearcontrol.grid(column = self.col, row = self.row)
		
	def initmonth(self):
		self.month = IntVar()
		self.month.set(self.datetime.month)
		self.monthcontrol = Menubutton(self.parent)
		
		monthmenu = Menu(self.monthcontrol)
		for m in range(1,13):
			monthmenu.add_radiobutton(variable = self.month, value = m, label = str(m), command = self.update)
		self.monthcontrol["menu"] = monthmenu
		
		self.monthcontrol.grid(column = self.col+1, row = self.row)
	
	def initday(self):
		self.day = IntVar()
		self.day.set(self.datetime.day)
		self.daycontrol = Menubutton(self.parent)
		
		self.daycontrol.grid(column = self.col+2, row = self.row)
	
	def inithour(self):
		self.hour = IntVar()
		self.hour.set(self.datetime.hour)
		self.hourcontrol = Menubutton(self.parent)
		
		hourmenu = Menu(self.hourcontrol)
		for h in range(0,24):
			hourmenu.add_radiobutton(variable = self.hour, value = h, label = str(h), command = self.update)
		self.hourcontrol["menu"] = hourmenu
		
		self.hourcontrol.grid(column = self.col+3, row = self.row)
	
	def initminute(self):
		self.minute = IntVar()
		self.minute.set(self.datetime.minute)
		self.minutecontrol = Menubutton(self.parent)
		
		minutemenu = Menu(self.minutecontrol)
		for m in range(0,60,5):
			minutemenu.add_radiobutton(variable = self.minute, value = m, label = ('0'+str(m))[-2:], command = self.update)
		self.minutecontrol["menu"] = minutemenu
		
		self.minutecontrol.grid(column = self.col+4, row = self.row)
		
	def update(self):
		try:
			self.datetime = datetime(self.year.get(),self.month.get(),self.day.get(),self.hour.get(),self.minute.get())
		except ValueError:
			self.year.set(self.datetime.year)
			self.month.set(self.datetime.month)
		if False and self.datetime < self.datemin:
			self.datetime = self.datemin
			self.year.set(self.datetime.year)
			self.month.set(self.datetime.month)
			self.day.set(self.datetime.day)
			self.hour.set(self.datetime.hour)
			self.minute.set(self.datetime.minute)
		self.yearcontrol["text"] = str(self.datetime.year)
		self.monthcontrol["text"] = str(self.datetime.month)
		self.daycontrol["text"] = str(self.datetime.day)
		self.hourcontrol["text"] = str(self.datetime.hour)
		self.minutecontrol["text"] = ('0' + str(self.datetime.minute))[-2:]
				
		year = self.datetime.year
		nextmonth = self.datetime.month % 12 + 1
		if nextmonth == 1:
			year += 1
		maxday = (date(year,nextmonth,1) - date(self.datetime.year,self.datetime.month,1)).days
		
		daymenu = Menu(self.daycontrol)
		for d in range(1,maxday+1):
			daymenu.add_radiobutton(variable = self.day, value = d, label = str(d), command = self.update)
		self.daycontrol["menu"] = daymenu
		self.parent.update()
		
class MatchResult(Frame):

	def __init__(self, match, nbrends, master=None):
		Frame.__init__(self, master)
		self.match = match
		self.nbrends = nbrends
		self.pack()
		self.createWidgets()
		
	def createWidgets(self):
		homelabel = Label(self, text = str(self.match.hometeam))
		homelabel.grid(column = 0, row = 0)
		endlabel = Label(self, text = "End")
		endlabel.grid(column = 0, row = 1)
		awaylabel = Label(self, text = str(self.match.awayteam))
		awaylabel.grid(column = 0, row = 2)
		
		self.homescores = []
		self.awayscores = []
		
		for end in xrange(1, self.nbrends+2):
			if end <= self.nbrends:
				endstri = str(end)
			else:
				endstri = 'EE'
			self.homescores.append(Entry(self, width = 1))
			self.homescores[-1]["validate"] = "focusout"
			self.homescores[-1]["validatecommand"] = self.valfun("home",end)
			self.homescores[-1].grid(column = end, row = 0)
			endnbr = Label(self, text = endstri)
			endnbr.grid(column = end, row = 1)
			self.awayscores.append(Entry(self, width = 1))
			self.awayscores[-1]["validate"] = "focusout"
			self.awayscores[-1]["validatecommand"] = self.valfun("away",end)
			self.awayscores[-1].grid(column = end, row = 2)
			if end <= len(self.match.result):
				self.homescores[-1].insert(0,'0')
				self.awayscores[-1].insert(0,'0')
				endres = self.match.result[end-1]
				if endres > 0:
					self.homescores[-1].delete(0,END)
					self.homescores[-1].insert(0, str(endres))
				else:
					self.awayscores[-1].delete(0,END)
					self.awayscores[-1].insert(0, str(-endres))
		
		self.hometotal = Label(self, text = "0")
		self.hometotal.grid(column = self.nbrends+2, row = 0)
		totlabel = Label(self, text = "Total")
		totlabel.grid(column = self.nbrends+2, row = 1)
		self.awaytotal = Label(self, text = "0")
		self.awaytotal.grid(column = self.nbrends+2, row = 2)
		self.updatetotalscores()
		
		self.savebutton = Button(self, text = "Save", command = self.save)
		self.savebutton.grid(column = 12, row = 1)
		
	def valfun(self, homeaway, index):
		end = index-1
		def command():
			try:		
				if homeaway == "home":
					homescore = int(self.homescores[end].get())
					if homescore == 0:
						val = True
					elif 0 < homescore < 9:
						self.awayscores[end].delete(0,END)
						self.awayscores[end].insert(0,'0')
						val = True
					else:
						val = False
				else:
					awayscore = int(self.awayscores[end].get())
					if awayscore == 0:
						val = True
					elif 0 < awayscore < 9:
						self.homescores[end].delete(0,END)
						self.homescores[end].insert(0,'0')
						val = True
					else:
						val = False
			except ValueError:
				val = False
			if val:
				self.updatetotalscores()
			else:
				self.homescores[end].delete(0,END)
				self.homescores[end].insert(0,'')
				self.awayscores[end].delete(0,END)
				self.awayscores[end].insert(0,'')
			return val
		return command
		
	def updatetotalscores(self):
		hometot = 0
		awaytot = 0
		for end in xrange(self.nbrends+1):
			homestr = self.homescores[end].get()
			awaystr = self.awayscores[end].get()
			if homestr == '' or awaystr == '':
				break
			hometot += int(homestr)
			awaytot += int(awaystr)
		self.hometotal["text"] = str(hometot)
		self.awaytotal["text"] = str(awaytot)
		
	def save(self):
		res = []
		for end in xrange(self.nbrends+1):
			homestr = self.homescores[end].get()
			awaystr = self.awayscores[end].get()
			if homestr == '' or awaystr == '':
				break
			res.append(int(homestr) - int(awaystr))
		self.match.finish(res)
		self.quit()

class HtmlWriteGUI(Frame):

	def __init__(self, tourney, master=None):
		Frame.__init__(self, master)
		self.tourney = tourney
		self.bgcolor = StringVar()
		self.bgcolor.set("White")
		self.txtcolor = StringVar()
		self.txtcolor.set("Black")
		
		self.pack()
		self.createWidgets()
		
	def createWidgets(self):
		self.bgcontrol = Menubutton(self, text = "Background color")
		bgmenu = Menu(self.bgcontrol)
		self.bgcontrolmenu = bgmenu
		colorlist = ["White", "Black", "Blue", "Red", "Green", "Yellow", "Magenta", "Cyan", "Orange", "ForestGreen"]
		for col in colorlist:
			bgmenu.add_radiobutton(variable = self.bgcolor, value = col, label = col, command = self.setbgcolor(col))
		self.bgcontrol["menu"] = bgmenu
		self.bgcontrol.grid(column = 0, row = 0)
	
		self.txtcontrol = Menubutton(self, text = "Text color")
		txtmenu = Menu(self.txtcontrol)
		for col in colorlist:
			txtmenu.add_radiobutton(variable = self.txtcolor, value = col, label = col, command = self.settxtcolor(col))
		self.txtcontrol["menu"] = txtmenu
		self.txtcontrol.grid(column = 0, row = 1)
		
		self.includeties = IntVar()
		self.includeties.set(0)
		self.tiescheckbox = Checkbutton(self, text = 'Include ties', variable = self.includeties, command = self.setties)
		self.tiescheckbox.grid(column = 0, row = 2)
	
		self.writebutton = Button(self, text = "Write", command = self.write)
		self.writebutton.grid(column = 0, row = 3)
	
	def setbgcolor(self, col):
		def callback():
			self.bgcolor.set(col)
		return callback
				
	def settxtcolor(self, col):
		def callback():
			self.txtcolor.set(col)
		return callback
	
	def setties(self):
		self.includeties.set(1-self.includeties.get())
	
	def write(self):
		self.tourney.calctable()
		col1 = self.bgcolor.get()
		col2 = self.txtcolor.get()
		hlist = ['Matcher','Vinster',None,'F&ouml;rluster','Tee','Po&auml;ng']
		if self.includeties.get() == 1:
			hlist[2] = 'Oavgjorda'
		
		#For debugging
		#print "{0} on {1}".format(col2,col1)
		fid = open('{0}.htm'.format(self.tourney.name),'w')
		fid.write('<h2>{0}</h2>'.format(self.tourney.name))
		fid.write('<p><h3>Laguppst&auml;llningar</h3></p><p>')
		fid.write(self.tourney.htmlrosters())
		fid.write('</p><p><h3>Spelschema</h3></p><p>')
		fid.write(self.tourney.htmlschedule(bgcolor = col1, txtcolor = col2))
		fid.write('</p><p><h3>Resultat</h3></p><p>')
		fid.write(self.tourney.htmlmatrix(bgcolor = col1, txtcolor = col2))
		fid.write('</p><p>')
		fid.write(self.tourney.htmlresults(bgcolor = col1, txtcolor = col2))
		fid.write('</p><p><h3>Tabell</h3></p><p>')
		fid.write(self.tourney.htmltable(headlist = hlist,bgcolor = col1,txtcolor = col2))
		fid.write('</p>')
		fid.close()
		
root = Tk()
app = CurlingApp(master=root)
app.mainloop()
root.destroy()
