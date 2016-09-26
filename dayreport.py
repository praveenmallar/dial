import shelve
db="dayreport.db"
import datetime, calendar
import tkMessageBox as tmb
import Tkinter

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

	def day_close(self):
		d=datetime.date.today().strftime("%Y%m%d")
		self.receive("closing balance",0)		
		cur=self.get(d)
		if len(cur)>0:
			tmb.showinfo("Already closed before","appending to old report")
			cur.extend(self.rep)
			self.rep=cur
		self.put(d,self.rep)
		self.put("closing balance",self.bal)
		self.rep=[]
		self.put("dayreport",self.rep)
		self.print_dayreport(datetime.date.today())
		
	def get(self,var):
		try:
			ret=self.db[var]
		except:
			ret=""
		return ret

	def put(self,var,val):
		self.db[var]=val

	def receive(self,head,amount,nocash=False):
		if not nocash:
			self.bal+=float(amount)
		self.rep.append([head,float(amount),0,self.bal])
		self.put("balance",self.bal)
		self.put("dayreport",self.rep)

	def spend(self,head,amount,nocash=False):
		if not nocash:
			self.bal-=float(amount)
		self.rep.append([head,0,float(amount),self.bal])
		self.put("balance",self.bal)
		self.put("dayreport",self.rep)

	def print_dayreport(self,day):
		d=day.strftime("%Y%m%d")
		rep=self.get(d)
		for r in rep:
			print "{:20.20s}{:8.2f}{:8.2f}{:10.2f}".format(*r)

	def print_monthreport(self,day):
		numdays=calendar.monthrange(day.year,day.month)[1]
		days=[datetime.date(day.year,day.month,d) for d in range(1,numdays+1)]
		print "{:10.10s}{:10.10s}{:10.10s}".format("date","op_balance","cl_balance")
		for d in days:
			dd=d.strftime("%Y%m%d")
			rep=self.get(dd)
			op=""
			cl=""
			for line in rep:
				if line[0]=="opening balance": 
					op=line[3]
				if line[0]=="closing balance": 
					cl=line[3]
			print "{:10.10s}{:>10.10s}{:>10.10s}".format(d.strftime("%d %b,%y"),str(op),str(cl))



dayrep=dayreport()

if __name__=="__main__":
	d=dayreport()
	print d.rep
