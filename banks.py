from Tkinter import *
import connectdb as cdb
import comp
import tkMessageBox as tmb
import printer
import dayreport


class banks(Frame):
	
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent,bd=1,relief=SUNKEN)
		self.pack(padx=3,pady=3)
		f1=Frame(self,bd=1,relief=RAISED)
		f1.pack(side=LEFT,fill=Y,expand=1)
		self.banks=comp.myComp2(f1,listheight=5)
		self.banks.pack()
		self.bank_name=StringVar()
		self.bank_addr=StringVar()
		self.bank_phone=StringVar()
		Entry(f1,textvariable=self.bank_name).pack(fill=X,padx=5,pady=5)
		Label(f1,text="address").pack(padx=5)
		Entry(f1,textvariable=self.bank_addr).pack(fill=X,padx=5,pady=5)
		Label(f1,text="phone").pack(padx=5)
		Entry(f1,textvariable=self.bank_phone).pack(fill=X,padx=5,pady=5)
		Button(f1,text="update",command=self.update_bank).pack(side=LEFT,padx=10,pady=5)
		Button(f1,text="new",command=self.bank_new).pack(side=LEFT,padx=10,pady=5)
		self.fillbanks()
		self.banks.bind("<<listChanged>>",self.bank_details)

		f2=Frame(self,bd=1,relief=RAISED)
		f2.pack(side=TOP,expand=1,fill=BOTH)
		self.bank_label=StringVar()
		Label(f2,height=2,padx=10,pady=2,textvariable=self.bank_label).pack(side=TOP)
		Label(f2,text="new transaction").pack()
		f=Frame(f2)
		f.pack()
		Label(f,text="amount").grid(row=0,column=0)
		self.trans_amount=DoubleVar()
		comp.NumEntry(f,textvariable=self.trans_amount).grid(row=0,column=1)
		Label(f,text="note").grid(row=1,column=0)
		self.trans_note=StringVar()
		Entry(f,textvariable=self.trans_note).grid(row=1,column=1)
		ftemp=Frame(f)
		self.trans_type=IntVar()
		Radiobutton(ftemp,text="withdrawal",variable=self.trans_type,value=1).pack(side=LEFT)
		Radiobutton(ftemp,text="deopsit",variable=self.trans_type,value=2).pack(side=LEFT)
		ftemp.grid(row=2,column=1)
		self.trans_type.set(2)
		Button(f,text="Save",command=self.bank_trans).grid(row=3,column=1)

		f4=Frame(self,bd=1,relief=RAISED)
		f4.pack(side=TOP,expand=1)
		Label(f4,text="Transactions",height=2,padx=10,pady=2).pack()
		f=Frame(f4)
		f.pack()
		sb=Scrollbar(f)
		sb.pack(side=RIGHT,fill=Y)
		self.transactionlist=Canvas(f,width=300,height=100,bd=1,yscrollcommand=sb.set)
		self.transactionlist.pack()
		self.transactionlist.items=None
		sb.config(command=self.transactionlist.yview)
		f=Frame(f4)
		f.pack()
		Label(f,text="print").pack(side=LEFT)
		self.transactionlistprint=IntVar()
		e=comp.NumEntry(f,textvariable=self.transactionlistprint,width=4)
		e.pack(side=LEFT)
		e.bind("<Return>",self.print_trans_list)
		Label(f,text="lines").pack(side=LEFT)

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

		bank=b[0]
		cur=cdb.Db().connection().cursor(cdb.dictcursor)
		cur.execute("select * from banktrans where bank=%s order by time desc;",(bank))
		rows=cur.fetchall()
		self.transactionlist.delete(ALL)
		i=0
		self.transactionlist.items=[]
		for r in rows:
			f=Frame(self.transactionlist,height=30)
			date=r['time'].strftime('%d %b,%y')
			Label(f,width=3,text=str(i+1),bd=1,relief=SUNKEN).pack(side=LEFT)
			Label(f, width=10,text=date,bd=1,relief=SUNKEN).pack(side=LEFT)
			Label(f,width=10,text=r['amount'],bd=1,relief=SUNKEN).pack(side=LEFT)
			Label(f,width=15,text=r['note'],bd=1,relief=SUNKEN).pack(side=LEFT)			
			self.transactionlist.create_window(1,1+i*18,window=f,anchor=NW)
			i+=1
			self.transactionlist.items.append("{:%d%b%y}-{:15.15s} :{:9.2f}".format(r['time'],r['note'],r['amount']))
		self.transactionlist.update_idletasks()
		self.transactionlist.config(scrollregion=self.transactionlist.bbox(ALL))

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

	def bank_trans(self):
		if not tmb.askyesno("Confirm","Add new bank transaction?",parent=self.master):
			return
		bank=self.banks.get()[1][0]
		bank_name=self.banks.get()[1][1]
		note=self.trans_note.get()
		amount=self.trans_amount.get()
		if self.trans_type.get()==1:
			amount=-amount
		con=cdb.Db().connection()
		cur=con.cursor()
		cur.execute("insert into banktrans(bank,note,time,amount) values(%s,%s,now(),%s);",(bank,note,amount))
		con.commit()
		dayreport.dayrep.spend("to bank "+bank_name,amount)
		self.trans_note.set("")
		self.trans_amount.set("")
		self.trans_type.set(2)
		self.fillbanks()

	def print_trans_list(self,e=None):
		num=self.transactionlistprint.get()
		lines= ["Last "+str(num)+ " transactions by "+self.banks.get()[1][1]]
		lines.extend( self.transactionlist.items[:num])
		printer.printinfo(lines)

if __name__=="__main__":
	t=Tk()
	b=banks(t)
	b.mainloop()
