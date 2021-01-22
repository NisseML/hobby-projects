from Tkinter import *
from bokning import *
from datetime import *
from tkdate import Datecontrol
import pickle

class SeasonApp(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.pack()
		self.createWidgets()
		
	def createWidgets(self):
		self.QUIT = Button(self)
		self.QUIT["text"] = "QUIT"
		self.QUIT["command"] = self.quit
		self.QUIT.grid(column = 0, row = 0)
		
		self.scheduleframe = Frame(self)
		self.scheduleframe.grid(column = 0, row = 1, columnspan = 4, sticky = W)
		self.startlabel = Label(self.scheduleframe, text = "Start date")
		self.startlabel.grid(column = 0, row = 1)
		self.startdate = Datecontrol(self.scheduleframe, 1, 1)
		self.endlabel = Label(self.scheduleframe, text = "End date")
		self.endlabel.grid(column = 0, row = 2)
		self.enddate = Datecontrol(self.scheduleframe, 2, 1)
		
		self.generatebutton = Button(self)
		self.generatebutton["text"] = "Generate season"
		self.generatebutton["command"] = self.generateseason
		self.generatebutton.grid(column = 1, row = 0)
		
		self.loadbutton = Button(self)
		self.loadbutton["text"] = "Load schedule"
		self.loadbutton["command"] = self.load
		self.loadbutton.grid(column = 2, row = 0)
		
		self.makehtmlbutton = Button(self)
		self.makehtmlbutton["text"] = "Make HTML schedule"
		self.makehtmlbutton["command"] = self.makehtml
		self.makehtmlbutton.grid(column = 3, row = 0)
	
	def load(self):
		yearnow = date.today().year
		for i in xrange(5):
			try:
				fid = open('Schedule_{0}.pkl'.format(yearnow))
				break
			except:
				--yearnow
				pass
		else:
			print 'Could not find file to load'
			return
		
		self.season = pickle.load(fid)
		fid.close()
		self.newseasonupdate()
		
	
	def makehtml(self):
		startyear = self.startdate.datetime.year
		filename = "Schedule_{0}.htm".format(startyear)
		fid = open(filename,'w')
		fid.write('<table border="1">')
		fid.write('<tr><td colspan="6"><span style="font-size:x-large;"><b><center>Tider {0}-{1}</center></b></span></td></tr>'.format(startyear,startyear+1))
		fid.write('<tr><td></td>')
		for i in xrange(1,6):
			fid.write('<td>Bana {0}</td>'.format(i))
		fid.write('</tr>')
		for psw in self.pswidgets:
			fid.write('<tr><td>{0}</td>'.format(psw.datetimelabel["text"]))
			for lane in psw.lanebuttons:
				fid.write('<td bgcolor="{1}">{0}</td>'.format(lane["text"],lane["bg"]))
			fid.write('</tr>')
		fid.write('</table>')
		fid.close()
		
		#Save season
		f = open("Schedule_{0}.pkl".format(startyear), 'w')
		pickle.dump(self.season, f)
		f.close()
		
	def generateseason(self):
		self.season = CurlingSeason(self.startdate.date, self.enddate.date,[3])
		self.newseasonupdate()
		
	def newseasonupdate(self):
		self.startlabel.destroy()
		self.endlabel.destroy()
		self.startdate.destroy()
		self.enddate.destroy()
		self.pswidgets = []
		
		self.toplimit = 0
		self.btmlimit = 20

		self.updatescheduleframe()
		if len(self.pswidgets) > 20:
			self.scrollbar = Scrollbar(self.scheduleframe)
			self.scrollbar["orient"] = VERTICAL
			self.scrollbar.grid(row = 0, column = 1, sticky = N+S, rowspan = 20)
			self.scrollbar["command"] = self.scroll2
		
	def updatescheduleframe(self):
		oldwidgets = [wgt for wgt in self.pswidgets]
		self.pswidgets = []
		for i, pses in enumerate(self.season):
			neww = SimplePracticeWidget(self.scheduleframe, pses)
			if self.toplimit <= i < self.btmlimit:
				neww.grid(column = 0, row = i-self.toplimit)
			self.pswidgets.append(neww)
		for wgt in oldwidgets:
			wgt.destroy()
		
	def scroll(self, val):
		val = int(val)
		topmax = len(self.pswidgets)-20
		if val != 0:
			self.toplimit = min(max(self.toplimit+val,0),topmax)
			self.btmlimit = self.toplimit+20
			self.updatescheduleframe()
			
	def scroll2(self, action, val, modifier):
		val = int(val)
		topmax = len(self.pswidgets)-20
		if action == SCROLL:
			self.toplimit = min(max(self.toplimit+val,0),topmax)
		elif action == MOVETO:
			self.toplimit = val*topmax
		self.btmlimit = self.toplimit+20
		self.updatescheduleframe()
		
class SimplePracticeWidget(Frame):

	def __init__(self, master, session):
		Frame.__init__(self, master)
		self.session = session
		self.createWidgets()
		
	def createWidgets(self):
		self.datetimelabel = Label(self, text = self.session.dtstr())
		self.datetimelabel.grid(column = 0, row = 0)
		
		self.lanebuttons = []
		for i in xrange(5):
			lb = Button(self)
			lb["command"] = self.toggle(i)
			lb.grid(column = i+1, row = 0)
			self.lanebuttons.append(lb)
			self.updatelane(i)
		
		self.removebutton = Button(self, text = "Remove")
		self.removebutton["command"] = self.remove
		self.removebutton.grid(column = 6, row = 0)
		
	def toggle(self,lane):
		def callback():
			val = self.session.paynplays[lane]
			self.session.paynplays[lane] = (val+1) % 3
			self.updatelane(lane)
		return callback
		
	def updatelane(self,lane):
		val = self.session.paynplays[lane]
		lb = self.lanebuttons[lane]
		if val == 0:
			lb["text"] = "Intern"
			lb["bg"] = "gray"
		elif val == 1:
			lb["text"] = "Ledig"
			lb["bg"] = "green"
		elif val == 2:
			lb["text"] = "Bokad"
			lb["bg"] = "red"

	def remove(self):
		self.master.master.season.remove(self.session.date)
		self.update()

	def update(self):
		self.master.master.updatescheduleframe()

class PracticeSessionWidget(Frame):

	def __init__(self, master, session):
		Frame.__init__(self, master)
		self.session = session
		self.createWidgets()
		
	def createWidgets(self):
		self.datetimelabel = Label(self, text = self.session.dtstr())
		self.datetimelabel.grid(column = 0, row = 0)
		
		self.lanebuttons = []
		for lane in xrange(1,6):
			lb = Button(self)
			lb["text"] = "Lane {0}".format(lane)
			if lane > len(self.session.paynplays):
				lb["bg"] = "green"
			else:
				lb["bg"] = "red"
			lb["command"] = self.launch(lane)
			lb.grid(column = lane, row = 0)
			self.lanebuttons.append(lb)
			
		
		self.removebutton = Button(self, text = "Remove")
		self.removebutton["command"] = self.remove
		self.removebutton.grid(column = 6, row = 0)

	def launch(self, lane):
		def callback():
			gui = PaynPlayGUI(self.session, lane, master = self.master)
			gui.grid(column = 7, row = 0, rowspan = 4)
			gui.mainloop()
			self.update()
		return callback
	
	def remove(self):
		self.master.master.season.remove(self.session.date)
		self.update()
	
	def update(self):
		self.master.master.updatescheduleframe()

class PaynPlayGUI(Frame):

	def __init__(self, session, lane, master=None):
		Frame.__init__(self, master)
		
		self.session = session
		self.pack()
		if lane > len(session.paynplays):
			self.createPnpWidgets()
		else:
			self.createInstWidgets(lane)
			
	def createInstWidgets(self, lane):
		pnp = self.session.paynplays[lane-1]
		self.instructor = StringVar()
		self.instructor.set(pnp.instructor)
		self.paid = IntVar()
		self.paid.set(pnp.payreceived)
		
		clabel = Label(self, text = "Customer")
		clabel.grid(column = 0, row = 0)
		ctext = Entry(self, state = DISABLED)
		ctext.insert(0, pnp.customer)
		ctext.grid(column = 1, row = 0)
		
		ilabel = Label(self, text = "Instructor")
		ilabel.grid(column = 0, row = 1)
		itext = Entry(self, textvariable = self.instructor)
		itext.grid(column = 1, row = 1)
		
		pbox = Checkbutton(self, text = "Paid", variable = self.paid)
		pbox.grid(column = 0, row = 2, columnspan = 2)
		
		self.okbutton = Button(self, text = "OK", command = self.instok(pnp))
		self.okbutton.grid(column = 0, row = 3)
		self.rembutton = Button(self, text = "Remove", command = self.empty(pnp))
		self.rembutton.grid(column = 1, row = 3)
		self.ccbutton = Button(self, text = "Cancel", command = self.cancel)
		self.ccbutton.grid(column = 2, row = 3)
		
	def createPnpWidgets(self):
		self.customer = StringVar()
		self.nbroflanes = IntVar()
		self.nbroflanes.set(1)
			
		clabel = Label(self, text = "Customer")
		clabel.grid(column = 0, row = 0)
		ctext = Entry(self, textvariable = self.customer)
		ctext.grid(column = 1, row = 0)
		
		llabel = Label(self, text = "Nbr of lanes")
		llabel.grid(column = 0, row = 1)
		availablelanes = 5 - len(self.session.paynplays)
		self.lanebox = Spinbox(self, from_ = 1, to_ = availablelanes)
		self.lanebox.grid(column = 1, row = 1)
		"""
		self.laneframe = LabelFrame(self, text = "Nbr of lanes")
		self.laneframe.grid(column = 0, row = 1, columnspan = 2)
		self.lanebuttons = []
		for i in xrange(1,6):
			lb = Radiobutton(self.laneframe, text = str(i), value = i, variable = self.nbroflanes)
			lb.grid(column = i-1, row = 0)
		"""
		
		self.okbutton = Button(self, text = "OK", command = self.ok)
		self.okbutton.grid(column = 0, row = 2)
		self.ccbutton = Button(self, text = "Cancel", command = self.cancel)
		self.ccbutton.grid(column = 1, row = 2)
			
	def ok(self):
		self.session.addPaynplay(self.customer.get(), int(self.lanebox.get()))
		self.destroy()
		self.quit()
		
	def instok(self, pnp):
		def callback():
			pnp.setinstructor(self.instructor.get())
			pnp.payreceived = (self.paid.get() == 1)
			self.destroy()
			self.quit()
		return callback
	
	def empty(self, pnp):
		def callback():
			self.session.removePaynplay(pnp)
			self.destroy()
			self.quit()
		return callback
		
	def cancel(self):
		self.destroy()
		self.quit()

root = Tk()
app = SeasonApp(master=root)
app.mainloop()
root.destroy()
