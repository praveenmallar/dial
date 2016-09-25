import shelve
db="dayreport.db"
import datetime

class dayreport:
	def __init__(self):
		self.db=shelve.open(db)
		self.refresh()

	def refresh(self):
		self.bal=self.get("balance")
		if self.bal=="":
			self.bal=0
		else:
			self.bal=float(self.bal)
		self.rep=self.get("dayreport")	
		if self.rep=="":
			self.rep=[]
		if len(self.rep)==0:
			b=self.get("closing balance")
			self.bal=0
			self.receive("opening balance",b)	

	def __del__(self):
		print self.bal, self.rep
		self.put("balance",self.bal)
		self.put("dayreport",self.rep)
		self.db.close()

	def day_close(self):
		d=datetime.date.today().strftime("%Y%m%d")
		self.receive("closing balance",0)		
		self.put(d,self.rep)
		self.put("closing balance",self.bal)
		self.rep=[]
		self.put("dayreport",self.rep)

	def get(self,var):
		try:
			ret=self.db[var]
		except:
			ret=""
		return ret

	def put(self,var,val):
		self.db[var]=val

	def receive(self,head,amount):
		self.bal+=float(amount)
		self.rep.append([head,amount,0,self.bal])

	def spend(self,head,amount):
		self.bal-=float(amount)
		self.rep.append([head,0,amount,self.bal])

d=dayreport()
d.receive("from me",1000)
d.spend("to lachu",500)
d.day_close()
