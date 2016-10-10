from Tkinter import *
import connectdb as cdb
import comp
import tkMessageBox as tmb


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

		f2=Frame(self,bd=1,relief=RAISED)
		f2.pack(side=TOP,expand=1)
		self.bank_label=StringVar()
		Label(f2,height=2,padx=10,pady=2,textvariable=self.bank_label).pack(side=TOP)
		Label(f2,text="new transaction").pack()
		f=Frame(f2)
		f.pack()
		Label(f,text="amount").grid(row=0,column=0)
		self.trans_amount=DoubleVar()
		comp.NumEntry(f,textvariable=self.trans_amount).grid(row=0,column=1)


	def fillbanks(self):
		i=self.banks.index()
		cur=cdb.Db().connection().cursor()
		cur.execute("select * from banks order by name")
		rows=cur.fetchall()
		items=[]
		for r in rows:
			items.append([r[1],r])
		self.banks.changelist(listitems=items)
		self.banks.see(i)

	def bank_details(self,e=None):
		b=self.banks.get()[1]
		self.bank_name.set(b[1])
		self.bank_addr.set(b[2])
		self.bank_phone.set(b[3])
		self.bank_label.set(b[1])

	def update_bank(self):
		b=self.banks.get()[1][0]
		ph=self.bank_phone.get()
		ad=self.bank_addr.get()
		con=cdb.Db().connection()
		cur=con.cursor()
		try:
			cur.execute("update banks set address=%s, phone=%s where id=%s;",(ad,ph,b))
			con.commit()
		except Exception as e:
			tmb.showerror("Error!",e.args,parent=self.master)
		self.fillbanks()

	def bank_new(self):
		b=self.bank_name.get()
		ph=self.bank_phone.get()
		ad=self.bank_addr.get()
		if not tmb.askyesno("Confirm","Add new bank {}".format(b),parent=self.master):
			return
		con=cdb.Db().connection()
		cur=con.cursor()
		try:
			cur.execute("insert into banks(name,phone,address) values(%s,%s,%s);",(b,ph,ad))
			con.commit()
		except Exception as e:
			tmb.showerror("Error!",e.args,parent=self.master)
		self.fillbanks()

if __name__=="__main__":
	t=Tk()
	b=banks(t)
	b.mainloop()
