import shelve
db="dayreport.db"
import datetime, calendar
import tkMessageBox as tmb
import Tkinter
import printer

class dayreport:

	'''usage:
		import dayreport
		dayreport.dayrep.spend(head,amount)
		dayreport.dayrep.receive(head,amount)
		dayreport.dayrep.day_close()
		dayreport.dayrep.print_dayreport(datetime.date)
		dayreport.dayrep.print_monthreport(datetime.date)
	'''

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
			if b=="":
				b=0
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
		self.rep.append([head,float(amount),self.bal])
		self.put("balance",self.bal)
		self.put("dayreport",self.rep)

	def spend(self,head,amount,nocash=False):
		if not nocash:
			self.bal-=float(amount)
		self.rep.append([head,0-float(amount),self.bal])
		self.put("balance",self.bal)
		self.put("dayreport",self.rep)

	def print_dayreport(self,day):
		d=day.strftime("%Y%m%d")
		rep=self.get(d)
		lines=["Day closing report "+d]
		for r in rep:
			lines.append( "{:20.20s}{:10.2f}{:10.2f}".format(*r))
		printer.printinfo(lines)

	def print_monthreport(self,day):
		numdays=calendar.monthrange(day.year,day.month)[1]
		days=[datetime.date(day.year,day.month,d) for d in range(1,numdays+1)]
		lines=[]
		lines.append( "{:10.10s}{:10.10s}{:10.10s}".format("date","op_balance","cl_balance"))
		for d in days:
			dd=d.strftime("%Y%m%d")
			rep=self.get(dd)
			op=""
			cl=""
			for line in rep:
				if line[0]=="opening balance" and op=="": 
					op=line[2]
				if line[0]=="closing balance": 
					cl=line[2]
			lines.append( "{:10.10s}{:>10.10s}{:>10.10s}".format(d.strftime("%d %b,%y"),str(op),str(cl)))
		printer.printinfo(lines)


dayrep=dayreport()

if __name__=="__main__":
	d=dayreport()
	print d.rep
