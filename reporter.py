from Tkinter import *
import connectdb as cdb
import tkMessageBox as tmb
import printer

class reporter (Frame):

	def __init__(self, parent=None, bill=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self, parent)
		self.pack()
		f=Frame(self)
		f.pack()
		Button(f,text="<",command=lambda:self.move(-1)).pack(side=LEFT,padx=20,pady=10)
		self.bill=IntVar()
		if bill:
			self.bill.set(bill)
		e=Entry(f,width=6,textvariable=self.bill)
		e.pack(side=LEFT,padx=5,pady=10)
		e.bind("<Return>",self.showreport)
		Button(f,text=">",command=lambda:self.move(1)).pack(side=LEFT,padx=20,pady=10)

		f=Frame(self,bd=1,relief=SUNKEN)
		f.pack(padx=10)
		sb=Scrollbar(f)
		sb.pack(side=RIGHT,fill=Y)
		self.reports=Canvas(f,width=350,height=300,yscrollcommand=sb.set)
		sb.config(command=self.reports.yview)
		self.reports.pack()
		
		f=Frame(self)
		f.pack()
		Button(f,text="save",command=self.save).pack(side=LEFT,padx=20,pady=10)
		Button(f,text="print",command=self.prnt).pack(side=LEFT,padx=20,pady=10)
		

	def move(self,direction=1):
		self.bill.set(self.bill.get()+direction)
		self.showreport()

	def showreport(self,e=None):
		bill=self.bill.get()
		if bill==0:
			return
		cur=cdb.Db().connection().cursor()
		cur.execute("select id, service, report from services where bill=%s",(bill))
		rows=cur.fetchall()
		self.reports.delete(ALL)
		i=0
		self.reports.items=[]
		for row in rows:
			self.reports.create_text(5,i+30,anchor=NW,text=row[1])
			t=Text(self.reports,width=30,height=5)
			t.id=row[0]
			t.insert(END,row[2])
			self.reports.create_window(100,i,anchor=NW,window=t)
			i+=100
			self.reports.items.append(t)
		self.reports.update_idletasks()
		self.reports.config(scrollregion=self.reports.bbox(ALL))

	def checkbill(self):
		cur=cdb.Db().connection().cursor()
		cur.execute("select id from services where bill=%s;",(self.bill.get()))
		rows=cur.fetchall()
		ids=[]
		for row in rows:
			ids.append(row[0])
		for t in self.reports.items:
			if t.id not in ids:
				tmb.showinfo("check bill number","bill number in search box and reports dont match",parent=self.master)
				return False
		return True

	def save (self):
		if not self.checkbill():
			return False
		db=cdb.Db().connection()
		cur=db.cursor()
		try:
			for t in self.reports.items:
				r=t.get("1.0","end-1c")
				if len(r.strip())==0:
					continue
				id=t.id
				sql="update services set report=%s where id=%s;"
				cur.execute(sql,(r,id))
			db.commit()			 
			tmb.showinfo("Saved","Report Saved", parent=self.master)
			return True
		except cdb.mdb.Error as e:
			tmb.showerror("error: "+e.args[0], e.args[1])
			return False

	def prnt (self):
		if not self.save():
			return False
		reportno=self.bill.get()
		db=cdb.Db().connection()
		cur=db.cursor()
		sql="select patient.name as patient, bill.date from bill join patient on bill.patient=patient.id where bill.id=%s;"
		cur.execute(sql,(reportno))
		r=cur.fetchone()
		patient=r[0]
		date=r[1]
		sql="select services.report as report from services where services.bill=%s;"
		cur.execute(sql,(reportno))
		rows=cur.fetchall()
		items=[]
		for r in rows:
			if len(r[0])==0:
				continue
			else:
				items.append(r[0])
		printer.printreport(reportno,patient,date,items)

if __name__=="__main__":
	t= Tk()
	b=reporter(t)
	b.mainloop()
