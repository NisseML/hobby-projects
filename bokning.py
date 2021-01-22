from datetime import *
# from calendar import Calendar # maybe

class PracticeSession(object):

	def __init__(self,practicedate):
		self.date = practicedate
		if self.date.weekday() == 3:
			self.time = time(20,0)
		else:
			self.time = time(16,30)
		# 0 = not available, 1 = available, 2 = booked
		self.paynplays = [0,0,0,1,1]
	
	def dtstr(self):
		return str(self.date) + ' ' + self.time.strftime('%H.%M')
	
	def __str__(self):
	# define output of the 'print' statement
		stri = str(self.date) + '\t' + self.time.strftime('%H.%M')
		for pnp in self.paynplays:
			stri += '\t' + str(pnp)
		return stri
		
	def __eq__(self, cmpobj):
	# define equality between objects to make them easier to access from lists
		return type(self) == type(cmpobj) and self.date == cmpobj.date
		
	def addPaynplay(self, customer, nbroflanes):
		for i in xrange(nbroflanes):
			self.paynplays.append(Paynplay(customer))
			
	def removePaynplay(self, pnp):
		self.paynplays.remove(pnp)
		
class Paynplay(object):
	
	def __init__(self, customer, instructor = None):
		self.customer = customer
		self.instructor = ""
		self.payreceived = False
		
	def setinstructor(self, instructor):
		self.instructor = instructor
		
	def paid(self):
		self.payreceived = True
	
	def __str__(self):
		return "Bokat"
		

class CurlingSeason(object):
	
	def __init__(self, startdate, enddate, wd = [3,6]): 
	# wd = weekdays of practice sessions, 3 = Thursday, 6 = Sunday		
		self.Schedule = []
		day = startdate
		while day <= enddate:
			if day.weekday() in wd:
				self.Schedule.append(PracticeSession(day))
			day += timedelta(1)
				
	def __str__(self):
	# define output of the 'print' statement
		stri = ''
		for ses in self.Schedule:
			stri += (str(ses) + '\n')
		return stri
		
	def __getitem__(self, keydate):
	# define access by [] subscripting
		i = self.Schedule.index(PracticeSession(keydate))
		return self.Schedule[i]
		
	def __iter__(self):
		return iter(self.Schedule)
		
	def __len__(self):
		return len(self.Schedule)
		
	def remove(self, datetoremove):
		self.Schedule.remove(self[datetoremove])
		
#lastseason = CurlingSeason(date(2010,9,30),date(2011,4,28))
#nextseason = CurlingSeason(date(2011,9,29),date(2012,4,22))
#thisseason = CurlingSeason(date(2012,9,6),date(2013,3,17))

