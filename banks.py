from Tkinter import *
import connectdb as cdb
import comp


class banks(Frame):
	
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.pack(padx=3,pady=3)
		f1=Frame(self)
		f1.pack(side=LEFT,fill=Y,expand=1)
		self.banks=comp.myComp2(f1,listheight=5)
		self.banks.pack()
		self.bank_name=StringVar()
		self.bank_addr=StringVar()
		self.bank_phone=StringVar()
		Entry(f1,textvariable=self.bank_name).pack(fill=X,padx=5,pady=5)
		Entry(f1,textvariable=self.bank_addr).pack(fill=X,padx=5,pady=5)
		Entry(f1,textvariable=self.bank_phone).pack(fill=X,padx=5,pady=5)
		Button(f1,text="update",command=self.update_bank).pack(side=LEFT,padx=10,pady=5)
		Button(f1,text="new",command=self.bank_new).pack(side=LEFT,padx=10,pady=5)
		self.fillbanks()
		self.banks.bind("<<listChanged>>",self.bank_details)


	def fillbanks(self):
		cur=cdb.Db().connection().cursor()
		cur.execute("select * from banks order by name")
		rows=cur.fetchall()
		items=[]
		for r in rows:
			items.append([r[1],r])
		self.banks.changelist(listitems=items)

	def bank_details(self,e=None):
		b=self.banks.get()[1]
		self.bank_name.set(b[1])
		self.bank_addr.set(b[2])
		self.bank_phone.set(b[3])

	def update_bank(self):
		pass

	def bank_new(self):
		pass


if __name__=="__main__":
	b=banks()
	b.mainloop()
