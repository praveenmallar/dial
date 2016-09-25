import comp
from Tkinter import *
import connectdb as cdb
import tkMessageBox as tmb


class Patient (Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.id=None
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
		Button(f3,text="Delete",command=self.delete).pack(side=LEFT,padx=15)
		Button(f3,text="Update",command=self.update).pack(side=LEFT,padx=15)
		Button(f3,text="Add New",command=self.addnew).pack(side=LEFT,padx=15)
		self.patients.bind("<<listChanged>>",self.patientChanged)
		self.fillPatients()

	def fillPatients(self):
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="select name,id,address,phone,note from patient order by name;"
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
		self.id=patient[1]
	
	def addnew(self):
		self.id=None
		self.name.set("")
		self.address.set("")
		self.phone.set("")
		self.note.set("")

	def delete(self):
		if self.id:
			id=self.id
			name=self.name.get()
			if not tmb.askyesno("Confirm","Delete Patient {}?".format(name),parent=self.master):
				return
			con=cdb.Db().connection()
			cur=con.cursor()
			cur.execute("delete from patient where id=%s;",(id))
			con.commit()
			tmb.showinfo("Deleted","Patient deleted", parent=self.master)
			self.fillPatients()

	def update(self):
		index=self.patients.index()
		id=self.id
		name=self.name.get()
		address=self.address.get()
		phone=self.phone.get()
		note=self.note.get()
		con=cdb.Db().connection()
		cur=con.cursor()
		try:
			if not id:
				if not tmb.askyesno("Confirm","Add new Patient?",parent=self.master):
					return
				cur.execute("insert into patient(name,address,phone,note) values(%s,%s,%s,%s);",(name,address,phone,note))
			else:
				cur.execute("update patient set address=%s, phone=%s,note=%s where id=%s;",(address,phone,note,id))
			con.commit()		
		except cdb.IntegrityError as e:
			tmb.showerror("Error "+str(e.args[0]),e.args[1],parent=self.master)
			return
		self.fillPatients()
		self.patients.see(index)
		tmb.showinfo("Done","Details updated",parent=self.master)

if __name__=="__main__":
	a=Patient(	)
	a.mainloop()
