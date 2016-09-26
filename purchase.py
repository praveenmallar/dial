from Tkinter import *
import connectdb as cdb
import comp
import calpicker
import tkMessageBox
import printer as printbill
import shelve
import dayreport

class addStock(Frame):

	def __init__(self, parent=None,*args, **kwargs):
		if not parent:
			t=Toplevel()
			parent=t
		Frame.__init__(self,parent,*args,**kwargs)
		self.items=[]
		db=cdb.Db().connection()
		cursor = db.cursor()
		cursor.execute("select * from seller")
		result=cursor.fetchall()
		stockists=[]
		for row in result:
			stockists.append(row[1])
		drugs=[]
		cursor.execute("select * from products")
		result=cursor.fetchall()
		for row in result:
			drugs.append(row[1])
		
		ftop=Frame(self,bd=1,relief=RAISED,background="cyan")
		ftop.pack(side=TOP,fill=X,expand=1)
		myfont=("Times",10,"bold")

		#frame1 - to select bill details
		f1=Frame(ftop,bd=1,relief=GROOVE)
		Label(f1,text="Seller",font=myfont).grid(row=0,column=0,sticky=E,padx=4,pady=2)
		self.stockists=comp.myComp(f1,listitems=stockists,listheight=2,width=14)
		self.stockists.grid(row=0,column=1,sticky=E+W+N+S,padx=4,pady=2)
		Label(f1,text="Bill Number",font=myfont).grid(row=1,column=0,sticky=E,padx=4,pady=2)
		self.billno=Entry(f1,width=14)
		self.billno.grid(row=1,column=1,sticky=E+W+N+S,padx=4,pady=2)
		Label(f1,text="Date",font=myfont).grid(row=2,column=0,sticky=E,padx=4,pady=2)
		self.date=calpicker.Calbutton(f1,width=14)
		self.date.grid(row=2,column=1,sticky=E+W+N+S,padx=4,pady=2)
		Label(f1,text="Total",font=myfont).grid(row=3,column=0,sticky=E,padx=4,pady=2)
		self.total=comp.NumEntry(f1,width=14)
		self.total.grid(row=3,column=1,sticky=E+W+N+S,padx=4,pady=4)
		f1.pack(side=TOP)	

		#frame2 - to add stocks
		f2=Frame(ftop)
		Label(f2,text="Product",font=myfont).pack(side=LEFT)
		self.drug=comp.myComp(f2,listitems=drugs,listheight=3,width=14)
		self.drug.pack(side=LEFT)
		Label(f2,text="Batch",font=myfont).pack(side=LEFT)
		self.batch=Entry(f2,width=10)
		self.batch.pack(side=LEFT)
		Label(f2,text="Count",font=myfont).pack(side=LEFT)
		self.count=comp.NumEntry(f2,width=5)
		self.count.pack(side=LEFT)
		Label(f2,text="Rate",font=myfont).pack(side=LEFT)
		self.rate=comp.NumEntry(f2,width=10)
		self.rate.pack(side=LEFT)
		Label(f2,text="MRP",font=myfont).pack(side=LEFT)
		self.mrp=comp.NumEntry(f2,width=10)
		self.mrp.pack(side=LEFT)
		Label(f2,text="Expiry",font=myfont).pack(side=LEFT)
		self.expiry=calpicker.Calbutton(f2,width=14)
		self.expiry.pack(side=LEFT)
		self.add=Button(f2,text="Add",command=self.addstock,font=myfont)
		self.add.bind("<Return>",self.addstock)
		self.add.pack(side=LEFT)
		f2.pack(side=TOP)

		#frame3 - bill list
		f=Frame(self,width=800,height=300)		
		f.pack(side=LEFT,fill=X,expand=1)
		sb=Scrollbar(f)
		sb.pack(side=RIGHT,fill=Y)
		f3=self.f3=Canvas(f,bd=1,relief=SUNKEN,yscrollcommand=sb.set,width=700,height=300)
		f3.pack(fill=BOTH,expand=1)
		sb.config(command=f3.yview)
		submitButton=Button(self,text="Submit\nBill", font=("Times",14,"bold"),padx=10,pady=10,command=self.addbill)
		submitButton.bind("<Return>",self.addbill)		
		submitButton.pack(side=RIGHT)

		self.pack()
		self.stockists.focus()

	def addstock(self,event=None):
		f=Frame(self.f3,bd=1,relief=RIDGE)
		f.drug=StringVar()
		f.drug.set(self.drug.get())
		Label(f,width=20,height=1,textvariable=f.drug).pack(side=LEFT)
		f.batch=StringVar()
		f.batch.set(self.batch.get())		
		Label(f,width=10,height=1,textvariable=f.batch).pack(side=LEFT)
		f.count=IntVar()
		f.count.set(int(self.count.get()))
		Label(f,width=5,height=1,textvariable=f.count).pack(side=LEFT)
		f.rate=DoubleVar()
		f.rate.set(float(self.rate.get()))
		Label(f,width=8,height=1,textvariable=f.rate).pack(side=LEFT)
		f.mrp=DoubleVar()
		f.mrp.set(float(self.mrp.get()))
		Label(f,width=8,height=1,textvariable=f.mrp).pack(side=LEFT)
		f.expiry=StringVar()
		f.expiry.set(self.expiry.get())
		Label(f,width=8,height=1,textvariable=f.expiry).pack(side=LEFT)
		b=Button(f,text="remove")
		b.config(command=lambda: self.removeframe(b))		
		b.pack(side=LEFT)	
		self.items.append(f)
		self.refreshcanvas()
		self.drug.clear()
		self.batch.delete(0,END)
		self.count.delete(0,END)
		self.rate.delete(0,END)
		self.mrp.delete(0,END)
		self.drug.focus()

	def refreshcanvas(self):
		self.f3.delete(ALL)
		i=0
		for f in self.items:
			self.f3.create_window(1,1+i*32,window=f, anchor=NW)
			i=i+1
		self.f3.update_idletasks()
		self.f3.config(scrollregion=self.f3.bbox(ALL))

	def removeframe(self,button):
		self.items.remove(button.master)
		self.refreshcanvas()

	def addbill(self,event=None):
		db=cdb.Db().connection()
		cur = db.cursor()

		stockist=self.stockists.get()
		billno=self.billno.get()
		date=self.date.get()
		total=str(self.total.get())
		
		try:
			sql="select id from seller where name='"+stockist+"';"
			cur.execute(sql)
			row=cur.fetchone()
			stockistid=row[0]
			sql="insert into purchase (bill,seller,date,amount) values ('"+str(billno)+"','"+str(stockistid)+"',str_to_date('"+date+"','%d-%b-%y'),"+total+");"
			cur.execute(sql)
			billid=cur.lastrowid
			billtotal=0
			printout=["","","PURCHASE","",stockist,"bill: "+billno,""]
			for f in self.items:
				drug=f.drug.get()
				batch=f.batch.get()
				count=f.count.get()
				rate=f.rate.get()
				mrp=f.mrp.get()
				expiry=f.expiry.get()
				dsql="select id from products where name='"+drug+"';"
				cur.execute(dsql)
				row=cur.fetchone()
				drugid=row[0]
				sql="select sum(stock.cur_count) from stock where stock.product=%s and stock.expiry> curdate();"
				cur.execute(sql,(drugid))
				r=cur.fetchone()
				existing_stock=str(r[0])
				sql="select sum(sale.count) from sale join bill on sale.bill=bill.id join stock on sale.stock=stock.id where bill.date> date_add(curdate(), interval -1 month) and stock.product=%s;"
				cur.execute(sql,(drugid))
				r=cur.fetchone()
				lastmonth_sale=str(r[0])
				sql="insert into stock (batch,expiry,ini_count,cur_count,product,mrp, purchase,rate) values('"+batch+ "',str_to_date('"+expiry+"','%d-%b-%y'),"+str(count)+","+str(count)+","+str(drugid) +","+str(mrp) +","+ str(billid) +","+ str(rate) +")"
				cur.execute(sql)
				billtotal=billtotal+count*rate
				printout.append(drug+ " b:"+batch+" ("+str(count)+")@"+str(rate)+" mrp:"+str(mrp)+" x:"+expiry+ " o/c:"+existing_stock+" o/s:"+lastmonth_sale)
			db.commit()
			printout.append(" ")
			printout.extend(["net total: "+str(billtotal),"bill total: "+total,"",""])
			printbill.printinfo(printout)
			dayreport.dayrep.spend("purchase:"+stockist,total,nocash=True)
			sh=shelve.open("data.db")
			try:
				curpurchase=sh['purchase']
			except:
				curpurchase=0
			sh['purchase']=curpurchase+float(total)
			self.items=[]
			self.refreshcanvas()
			self.drug.focus()

		except cdb.mdb.Error,e:
			tkMessageBox.showerror("Error in database:", "error %d: %s" %(e.args[0],e.args[1]),parent=self.master)
			if db:
				db.rollback()
		finally :
			db.close()


if __name__=="__main__":
	root=addStock()
	root.mainloop()
	
		
