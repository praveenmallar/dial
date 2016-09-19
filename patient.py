import comp
from Tkinter import *
import connectdb as cdb
import tkMessageBox as tmb


class Patient (Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.pack()
		Label(self,text="Patient",font="Halvetica 12 bold").pack(pady=10)
		f1=Frame(self)
		self.patients=comp.myComp2(f1,listitems=[],listheight=5)
		f1.pack(padx=10,pady=20)
		self.patients.pack()
		f2=Frame(self,bd=1,relief=RAISED)
		f2.pack(padx=20,pady=10)
		self.name=StringVar()
		self.address=StringVar()
		self.phone=StringVar()
		self.note=StringVar()
		Label(f2,text="Name").grid(row=0,column=0,padx=5,pady=5)
		Label(f2,text="Address").grid(row=1,column=0,padx=5,pady=5)
		Label(f2,text="Phone").grid(row=2,column=0,padx=5,pady=5)
		Label(f2,text="Note").grid(row=3,column=0,padx=5,pady=5)
		Entry(f2,textvariable=self.name).grid(row=0,column=1,padx=5,pady=5)
		Entry(f2,textvariable=self.address).grid(row=1,column=1,padx=5,pady=5)
		Entry(f2,textvariable=self.phone).grid(row=2,column=1,padx=5,pady=5)
		Entry(f2,textvariable=self.note).grid(row=3,column=1,padx=5,pady=5)
		f3=Frame(self)
		f3.pack(pady=15)
		Button(f3,text="Update",command=self.update).pack(side=LEFT,padx=15)
		Button(f3,text="Add New",command=self.addnew).pack(side=LEFT,padx=15)
		self.patients.bind("<<listChanged>>",self.patientChanged)
		self.fillPatients()

	def fillPatients(self):
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="select name,id,address,phone,note from patient;"
		cur.execute(sql)
		rows=cur.fetchall()
		items=[]
		for r in rows:
			items.append([r[0],r])
		self.patients.changelist(items)
	
	def patientChanged(self,e=None):
		patient=self.patients.get()[1]
		self.name.set(patient[0])
		self.address.set(patient[2])
		self.phone.set(patient[3])
		self.note.set(patient[4])

	def update(self):
		id=self.patients.get()[1][1]
		index=self.patients.index()
		address=self.address.get()
		phone=self.phone.get()
		note=self.note.get()
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="update patient set address=%s, phone=%s,note=%s where id=%s;"
		cur.execute(sql,(address,phone,note,id))
		con.commit()
		self.fillPatients()
		self.patients.see(index)
		tmb.showinfo("Done","Details updated")

	def addnew(self):
		name=self.name.get()
		if not tmb.askyesno("Confirm","Add new Patient?"):
			return
		address=self.address.get()
		phone=self.phone.get()
		note=self.note.get()
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="insert into patient(name,address,phone,note) values(%s,%s,%s,%s);"
		cur.execute(sql,(name,address,phone,note))
		con.commit()

if __name__=="__main__":
	a=Patient(	)
	a.mainloop()
