from Tkinter import *
import datetime
from calendar import monthrange

class Calpicker():

	'''Chose a date
		Calpicker(parent,inidate)
		parent.wait_window(Calpicker().root)
	'''

	months=["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
	returndate=datetime.date.today()

	def __init__(self, parent=None, inidate=datetime.date.today()):
		self.parent=parent
		root=self.root=Toplevel(parent)
		#root.overrideredirect(1)
		root.transient(parent)
		f=Frame(root)
		f.pack()
		self.date=inidate		
		frame_top=Frame(f);frame_top.pack()
		frame_buttons=Frame(f,relief=RAISED,borderwidth=1)
		frame_bottom=Frame(f)
		self.monthlabel=StringVar()
		self.yearlabel=StringVar()
		self.datelabel=StringVar()
		Button(frame_top,text="<",command=lambda:self.changemonth("back")).pack(side=LEFT)
		Label(frame_top,textvariable=self.monthlabel,width=4).pack(side=LEFT)
		Button(frame_top,text=">",command=lambda:self.changemonth("forward")).pack(side=LEFT)
		Label(frame_top,textvariable=self.datelabel,relief=GROOVE,width=10).pack(side=LEFT,padx=10)
		Button(frame_top,text=">",command=lambda:self.changeyear("forward")).pack(side=RIGHT)
		Label(frame_top,textvariable=self.yearlabel).pack(side=RIGHT)
		Button(frame_top,text="<",command=lambda:self.changeyear("back")).pack(side=RIGHT)

		self.daybuttons={};self.curdaybutton=None
		for i in range(1,32):
			b=Button(frame_buttons,text=str(i),command=lambda n=i:self.daypressed(n),height=2,width=2)
			self.daybuttons[i]=b
		self.defaultbg=self.daybuttons[1].cget('bg')		
		self.setdate()
		frame_buttons.pack()

		Button(frame_bottom,text="reset date",command=self.resetdate).pack()
		frame_bottom.pack()
		
		root.grab_set()
		root.focus_set()
		root.bind('<Return>',self.ok)
		root.bind('<Escape>',self.cancel)
		root.protocol('WM_DELETE_WINDOW',self.cancel)
		
	def changemonth(self,direction):
		d = self.date.day
		m=self.date.month
		y=self.date.year
		valid=0
		if direction=="back":		
			m=m-1
		elif direction=="forward":
			m=m+1
		if m==0:
			m=12
			y=y-1
		if m==13:
			m=1
			y=y+1
		while valid==0:
			try:
				date=datetime.date(y,m,d)
				self.date=date
				valid=1
			except:
				d=d-1
		self.setdate()

	def changeyear(self,direction):
		yr=int(self.yearlabel.get())
		if direction=="back":
			yr=yr-1
		elif direction=="forward":
			yr=yr+1
		self.date= datetime.date(yr,self.date.month,self.date.day)
		self.setdate()

	def setdate(self):
		self.datelabel.set(self.date.strftime("%d %b %Y") )
		self.yearlabel.set(self.date.year)
		self.monthlabel.set(self.months[self.date.month-1])
		if self.curdaybutton !=None:
			self.curdaybutton.config(bg=self.defaultbg)		
		self.curdaybutton=self.daybuttons[self.date.day]
		self.curdaybutton.config(bg='cyan')		
		self.displaydaybuttons()
		
	def daypressed (self,d):
		self.date=datetime.date(self.date.year,self.date.month,d)	
		self.setdate()
		self.ok()
	
	def displaydaybuttons(self):
		mr=monthrange(self.date.year,self.date.month)
		weekday=mr[0]
		daysinmonth=mr[1]
		row=0
		for i in range(1,32):
			self.daybuttons[i].grid_forget()
			self.daybuttons[i].config(fg='black')
		for d in range (1,daysinmonth+1):
			b=self.daybuttons[d]
			b.grid(row=row,column=weekday)
			weekday=weekday+1
			if weekday==7:
				b.config(fg='red')
				weekday=0
				row=row+1

	def ok (self, event=None):
		self.returndate=self.date
		self.cancel()
			
	def cancel(self,event=None):
		self.root.destroy()
		if self.parent: self.parent.focus_set()

	def resetdate(self):
		self.date=datetime.date.today()
		self.setdate()

def getdate(window=None,inidate=datetime.date.today()):
	'''getdate(parent)
	'''
	if window==None:
		root=Tk()
	else:
		root=window
	c = Calpicker(root,inidate=inidate)
	root.wait_window(c.root)
	returndate=c.returndate
	return returndate

class Calbutton(Button):
	def __init__(self,parent,inidate=datetime.date.today(),**kwarg):
		Button.__init__(self,parent,kwarg)
		self.config(text=inidate.strftime("%d-%b-%y"))
		self.config(command=self.getdate)
		self.bind("<Return>",self.getdate)
	
	def getdate(self,event=None):
		t=getdate(self,inidate=datetime.datetime.strptime(self.cget('text'),"%d-%b-%y"))		
		self.config(text=t.strftime("%d-%b-%y"))

	def get(self):
		return self.cget('text')
			
if __name__=="__main__":
	print getdate()
