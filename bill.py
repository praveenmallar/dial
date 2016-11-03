from Tkinter import *
import comp
import connectdb as cdb
import datetime as dt
import tkMessageBox as tmb
from tkFont import Font
import printer
import dayreport

class Bill (Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.pack()
		titlefont=Font(family="Gothic", size=10, weight="bold")
		Label(self,text="Bill",font="Helvetica 16 bold").grid(row=0,column=0,columnspan=2)
		f1=Frame(self,border=1,relief=SUNKEN)
		f1.grid(row=1,column=0,padx=5)
		Label(f1,text="Patient",anchor=W,font=titlefont).pack(side=TOP,fill=X,expand=1,padx=15)
		self.patients=comp.myComp2(f1,listitems=[],listheight=3,pady=5)
		self.patients.pack(padx=10,side=LEFT)
		self.note=StringVar()
		Label(f1,height=2,anchor=W,width=20,textvariable=self.note).pack(pady=5,fill=X)
		self.total=StringVar()
		Label(f1,height=1,anchor=W,width=20,textvariable=self.total).pack(fill=X)
		self.free=StringVar()
		Label(f1,height=1,anchor=W,width=20,textvariable=self.free).pack(fill=X,pady=5)
		
		f2=Frame(self,bd=1,relief=SUNKEN)
		f2.grid(row=2,column=0,pady=10)		
		Label(f2,text="Sponsor",anchor=W,font=titlefont).pack(side=TOP,fill=X,expand=1,padx=15)
		self.sponsors=comp.myComp2(f2,listitems=[],listheight=2,pady=5)
		self.sponsors.pack(side=LEFT,padx=10)
		self.sponsordetails=StringVar()
		Label(f2,textvariable=self.sponsordetails,height=2,anchor=W,width=20).pack(fill=X,side=LEFT)

		f3=Frame(self,bd=1,relief=SUNKEN)
		f3.grid(row=3,column=0,pady=10)
		Label(f3,text="Items",anchor=W,font=titlefont).pack(side=TOP,fill=X,expand=1,padx=15)
		self.products=comp.myComp2(f3,listitems=[],listheight=4)
		self.products.pack(side=LEFT,padx=10)
		self.productdetails=StringVar()
		Label(f3,textvariable=self.productdetails,height=1,anchor=W,width=20).pack(fill=X)
		Label(f3,text="count").pack()
		self.count=IntVar()
		count=comp.NumEntry(f3,textvariable=self.count,width=5)
		count.pack()
		count.bind('<Return>',self.add)
		button=Button(f3,text="Add",command=self.add,pady=5)
		button.pack()
		button.bind("<Return>",self.add)

		f4=Frame(self,bd=1,relief=RAISED)
		f4.grid(row=1,column=1,rowspan=3,padx=10)
		f5=Frame(f4)
		f5.pack()
		sb=Scrollbar(f5)
		sb.pack(side=RIGHT,fill=Y)
		self.canvas=Canvas(f5,bd=1,relief=SUNKEN,yscrollcommand=sb.set,width=300,height=300)
		self.canvas.pack()
		sb.config(command=self.canvas.yview)
		self.credit=IntVar()
		Checkbutton(f4,text="credit",command=self.check_credit,variable=self.credit).pack(side=LEFT,pady=20,padx=20)
		Button(f4,text="Save\nBill",command=self.bill).pack(pady=20)

		self.fillpatients()
		self.fillsponsors()
		self.fillproducts()
		self.patients.bind("<<listChanged>>",self.patientChanged)
		self.sponsors.bind("<<listChanged>>",self.donorChanged)
		self.products.bind("<<listChanged>>",self.productChanged)

		self.items=[]
		self.bin=PhotoImage(file="images/bin.png")
		self.patients.focus()
		
		
	def fillpatients(self):
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="select patient.id, patient.name as patient,patient.note , count(bill.id) as total, count(sponsorship.bill)as free "\
			"from patient left join bill on bill.patient=patient.id left join sponsorship on sponsorship.bill=bill.id"\
			" group by patient.id order by name;"
		cur.execute(sql)
		rows=cur.fetchall()
		items=[]
		for row in rows:
			items.append([row[1],row])
		self.patients.changelist(items)

	def fillsponsors(self):
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="select * from donor order by name;"
		cur.execute(sql)
		rows=cur.fetchall()
		items=[]
		items.append(["",None])
		for row in rows:
			items.append([row[1],row])
		self.sponsors.changelist(items)

	def fillproducts(self):
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="select products.id, products.name,1, sum(stock.cur_count),0 from products join stock on products.id=stock.product "\
			"group by products.id union select service.id, service.name,2, \"\",service.rate from service;"
		cur.execute(sql)
		rows=cur.fetchall()
		items=[]
		for row in rows:
			items.append([row[1],row])
		items.sort(key=lambda x:x[0])
		self.products.changelist(items)

	def add(self,e=None):
		product=self.products.get()[1]
		count=self.count.get()
		if product[2]==2:		#service
			count=1
		f=Frame(self.canvas,width=300,height=30)
		f.product=product
		f.count=count		
		Label(f,text=product[1],width=20).pack(side=LEFT,padx=15)
		Label(f,text=count,width=5).pack(side=LEFT)
		Button(f,image=self.bin,command=lambda x=f:self.remove(x),relief=FLAT).pack(side=LEFT,padx=10)
		self.items.append(f)
		self.refreshcanvas()
		self.products.clear()
		self.count.set(0)
		self.products.focus()

	def refreshcanvas(self):
		self.canvas.delete(ALL)	
		i=0
		for f in self.items:
			self.canvas.create_window(1,1+i*30,window=f, anchor=NW)
			i=i+1
		self.canvas.update_idletasks()
		self.canvas.config(scrollregion=self.canvas.bbox(ALL))

	def remove(self,f):
		self.items.remove(f)
		self.refreshcanvas()

	def bill(self):
		patient=self.patients.get()[1]
		con=cdb.Db().connection()
		cur=con.cursor()
		date=dt.date.today()
		try:
			sql="insert into bill (date, patient) values (%s,%s);"
			cur.execute(sql,(date,patient[0]))
			billid=cur.lastrowid
			lines=[]
			billtotal=0
			goods=[]
			for item in self.items:
				product = item.product
				count=item.count
				if product[2]==2:		#service
					sql="insert into services (service,bill,rate) values(%s,%s,%s);"
					cur.execute(sql,(product[1],billid,product[4]))
					billtotal+=product[4]
					lines.append([product[1],product[4]])
					sql="select products.id,productservice.count,products.name "\
						"from productservice join products on productservice.product=products.id where service=%s;"
					cur.execute(sql,(product[0]))
					rows=cur.fetchall()
					for r in rows:		#service products
						goods.append([r[0],r[1],0,r[2]])

				else:				#product
					goods.append([product[0],count,1,product[1]])

			for item in goods:
				count=item[1]
				sql="select id,cur_count as count,batch,mrp,expiry from stock where product=%s and expiry>curdate() and cur_count>0 "\
					"order by expiry;"
				cur=con.cursor(cdb.dictcursor)
				cur.execute(sql,(item[0]))
				rows=cur.fetchall()
				for b in rows:
					if count>b['count']:
						count-=b['count']
						saleamount=b['count']*b['mrp']*item[2]	
						salecount=b['count']
						batchcount=0					
					elif count>0:
						saleamount=count*b['mrp']*item[2]
						salecount=count						
						batchcount=b['count']-count
						count=0
					else:
						break
					cur.execute("update stock set cur_count=%s where id=%s;",(batchcount,b['id']))
					cur.execute("insert into sale (stock,bill,count,amount) values(%s,%s,%s,%s);",(b['id'],billid,salecount,saleamount))
					billtotal+=saleamount
					lines.append([item[3],saleamount])
				if count > 0:
					raise cdb.mdb.Error(420, "not enough stock of " +item[3] )
			cur.execute("update bill set amount=%s where id=%s;",(billtotal,billid))
			credit=False
			if self.credit.get()==1:
				credit=True
			donor=None			
			donor=self.sponsors.get()
			dayreport.dayrep.receive("bill:"+patient[1],billtotal)
			if donor :
				donor=donor[1]
				if not donor[2]>billtotal and not credit:
					raise cdb.mdb.Error(420,"not enough donation with the sponsor "+donor[1])
				cur.execute("update donor set value=%s where id=%s;",(donor[2]-billtotal,donor[0]))
				cur.execute("insert into sponsorship (donor,bill) values(%s,%s);",(donor[0],billid))
				donor=donor[1]
				dayreport.dayrep.spend("spnsr:"+donor,billtotal)
				billtotal=0
			con.commit()	
			date=date.strftime("%e-%b-%y")
			printer.printbill(billid,patient[1],donor,date,billtotal,lines)

			self.items=[]
			self.refreshcanvas()
			self.fillpatients()
			self.fillsponsors()
			self.fillproducts()
			self.credit.set(0)

		except cdb.mdb.Error as e:
			tmb.showerror("Error","error %d: %s" %(e.args[0],e.args[1]),parent=self.master)
			if con:
				con.rollback()	
		

	def patientChanged(self,event=None):
		patient=self.patients.get()[1]
		self.note.set(patient[2])
		self.total.set("Total :"+str(patient[3]))
		self.free.set("Free :"+str(patient[4]))

	def donorChanged(self,event=None):
		donor=self.sponsors.get()
		if donor:
			donor=donor[1]
			self.sponsordetails.set("Value :"+str(donor[2]))
		else:
			self.sponsordetails.set("Value :")
			
	
	def productChanged(self,event=None):
		pr=self.products.get()[1]
		val=pr[3]
		if len(val)>0:
			txt="Count :"+str(val)
		else:
			txt=""
		self.productdetails.set(txt)

	def check_credit(self,event=None):
		if self.credit.get()==1:
			donor=self.sponsors.get()
			if not donor:
				tmb.showerror("No Donor Selected","Select Donor first",parent=self.master)
				self.credit.set(0)
				self.sponsors.focus()
				return			
			if not tmb.askyesno("Confirm","make this a credit bill?",parent=self.master):
				self.credit.set(0)

if __name__=="__main__":
	b=Bill()
	b.mainloop()
		
		
