from Tkinter import *
import comp
import connectdb as cdb
import tkMessageBox as tmb

class creditpay (Frame):
	
	def __init__(self,parent=None):
		if not parent:
			parent=Tk()
		Frame.__init__(self,parent)
		self.pack()
		Label(self,text="Credit Pay",font="Halvetica 16 bold").pack()
		f1=Frame(self,bd=1,relief=RAISED)
		f1.pack(side=LEFT,padx=1,pady=1)
		self.patients=comp.myComp2(f1,listitems=[],listheight=4)
		Label(f1,text="patient").pack(side=LEFT,padx=5)
		self.patients.pack()
		self.patients.bind("<<listChanged>>",self.patientchanged)

		f=Frame(self,bd=1,relief=RAISED)
		f.pack(padx=1,pady=1)
		sb=Scrollbar(f)
		sb.pack(side=RIGHT,fill=Y)
		self.credits=Canvas(f,yscrollcommand=sb.set,bd=1,relief=SUNKEN,height=250,width=400)
		self.credits.pack()
		sb.config(command=self.credits.yview)
		
		
		self.init()

	def init(self):
		cur=cdb.Db().connection().cursor()
		cur.execute("select * from patient order by name;")
		rows=cur.fetchall()
		items=[]		
		for row in rows:
			items.append([row[1],row[0]])
		self.patients.changelist(items)	

	def patientchanged(self,e=None):
		self.creditbills=set()
		self.credits.delete(ALL)
		patient=self.patients.get()[1]
		cur=cdb.Db().connection().cursor()
		cur.execute("select bill.id,bill.date,bill.amount from bill join credit  on credit.bill=bill.id where bill.patient=%s and credit.paid is null;",(patient))
		rows=cur.fetchall()
		i=0
		for r in rows:
			f=Frame(self.credits,height=30,width=250,bd=1,relief=RIDGE)
			Label(f,width=8,text=r[0]).pack(side=LEFT)
			Label(f,width=15,text=r[1],bd=1,relief=RIDGE).pack(side=LEFT)
			Label(f,width=15,text=r[2]).pack(side=LEFT)
			selvar=IntVar()
			c=Checkbutton(f,command=lambda x=r[0],y=selvar:self.creditselected(x,y),variable=selvar)
			c.pack(side=LEFT)
			self.credits.create_window(1,1+i*30,window=f,anchor=NW)
			i+=1
		self.credits.update_idletasks()
		self.credits.config(scrollregion=self.credits.bbox(ALL))
			

	def creditselected(self,bill,selected):
		if selected.get()==1:
			if len(self.creditbills)<6:
				self.creditbills.add(bill)
			else:
				tmb.showerror("Limit exeeded","Can add only 5 bills at a time",parent=self.master)
		else:
			self.creditbills.discard(bill)
		print self.creditbills			


if __name__=="__main__":
	c=creditpay()
	c.mainloop()
