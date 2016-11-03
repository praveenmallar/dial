#!/usr/bin/env python
from Tkinter import *
import bill,donor,patient,purchase,service,password,printer,editstock,review,new,banks,creditpay,reporter,petty
import shelve
import tkMessageBox 
import connectdb as cdb
import datetime as dt
import dayreport

class Dialysis():
	def __init__(self):
		self.master=Tk()
		self.master.config(width=600,height=400)
		self.master.title("Lions Dialysis Center")
		self.addmenus()
		self.addshortcuts()
		f=Frame(self.master)
		bill.Bill(f).pack()
		f.pack()
		self.master.mainloop()

	def addshortcuts(self):
		f=Frame(self.master,bd=1,relief=SUNKEN)
		f.pack()
		photo=PhotoImage(file="./images/bill.png")
		b=Button(f,image=photo,text="bill",compound=BOTTOM,width=100,height=100,command=lambda:bill.Bill())
		b.pack(side=LEFT)
		b.image=photo
		photo=PhotoImage(file="./images/purchase.png")
		b=Button(f,image=photo,text="purchase",compound=BOTTOM,width=100,height=100,command=lambda:purchase.addStock())
		b.pack(side=LEFT)
		b.image=photo
		photo=PhotoImage(file="./images/patient.png")
		b=Button(f,image=photo,text="patient",compound=BOTTOM,width=100,height=100,command=lambda:patient.Patient())
		b.pack(side=LEFT)
		b.image=photo
		photo=PhotoImage(file="./images/donor.png")
		b=Button(f,image=photo,text="donor",compound=BOTTOM,width=100,height=100,command=lambda:donor.Donor())
		b.pack(side=LEFT)
		b.image=photo
		photo=PhotoImage(file="./images/new.png")
		b=Button(f,image=photo,text="Services",compound=BOTTOM,width=100,height=100,command=lambda:service.Inv())
		b.pack(side=LEFT)
		b.image=photo
		
	def addmenus(self):
		menu=Menu(self.master)

		self.debug=BooleanVar()
		self.debug.set(False)
		sh=shelve.open("data.db")
		try:
			noprinter=sh['noprinter']
		except:
			noprinter=False
		self.debug.set(noprinter)
		
		repmenu=Menu(menu,tearoff=0)
		monthsalemenu=Menu(repmenu,tearoff=0)
		monthsalemenu.add_command(label="previous month",command=lambda x=-1:self.lastmonthbal(x))
		monthsalemenu.add_command(label="current month",command=lambda x=0:self.lastmonthbal(x))
		repmenu.add_command(label="Day close",command=self.dayclose)
		repmenu.add_command(label="Last Month Report",command=self.monthreport)
		repmenu.add_cascade(label="Month Balance",menu=monthsalemenu)		
		menu.add_cascade(label="Report",menu=repmenu)

		viewmenu=Menu(menu,tearoff=0)
		viewmenu.add_command(label="print stockists list", command=self.liststockists)
		viewmenu.add_command(label="review bills",command=self.reviewbills)
		viewmenu.add_command(label="print report",command=lambda:reporter.reporter())
		menu.add_cascade(label="View",menu=viewmenu)

		taskmenu=Menu(menu,tearoff=0)
		taskmenu.add_command(label="New",command=lambda:new.adder())
		taskmenu.add_command(label="Banks",command=lambda:banks.banks())
		taskmenu.add_command(label="Credit",command=lambda:creditpay.creditpay())
		taskmenu.add_command(label="Payment",command=lambda:petty.petty())
		menu.add_cascade(label="Tasks",menu=taskmenu)

		adminmenu=Menu(menu,tearoff=0)
		adminmenu.add_command(label="Pay Stockists",command=self.purchasepay)
		adminmenu.add_command(label="Passwords",command=lambda:password.Password())
		adminmenu.add_command(label="Edit Stock",command=self.editstock)
		adminmenu.add_checkbutton(label="Debug",command=self.noprinter,variable=self.debug)
		adminmenu.add_command(label="Set Printers",command=self.setprinters)
		adminmenu.add_command(label="Set Db params",command=self.dbparams)
		menu.add_cascade(label="Admin",menu=adminmenu)

		self.master.config(menu=menu)

	def editstock(self):
		if not password.askpass():
			return
		editstock.EditStock()

	def dayclose(self):
		if not password.askpass():
			tkMessageBox.showerror("wrong password","try again")
			return
		dayreport.dayrep.day_close()

	def lastmonthbal(self,mon):
		if not password.askpass():
			return
		d=dt.date.today()
		if mon==-1:
			d = d.replace(day=1) - dt.timedelta(days=1)
		dayreport.dayrep.print_monthreport(d)		

	def monthreport(self):
		if not password.askpass("admin"):
			tkMessageBox.showerror("error","wrong password")
			return
		cur=cdb.Db().connection().cursor()
		cur.execute("select count(id),sum(amount) from bill where date >= date_format(current_date-interval 1 month, '%Y/%m/01') and "\
				"date <date_format(current_date,'%Y/%m/01')")
		r=cur.fetchone()
		lines=["Report of Month "+(dt.date.today().replace(day=1)-dt.timedelta(days=1)).strftime("%b")," "]
		lines.append("Number of bills: "+str(r[0]))
		lines.append("Total Value: "+str(r[1]))
		cur.execute("select count(bill.amount), sum(bill.amount) from bill join sponsorship on sponsorship.bill=bill.id "\
				"where bill.date >= date_format(current_date-interval 1 month, '%Y/%m/01') and bill.date <date_format(current_date,'%Y/%m/01')")
		r=cur.fetchone()		
		lines.append("Number of free bills: "+str(r[0]))
		lines.append("Total value of free: "+str(r[1]))
		printer.printinfo(lines)

	def reviewbills(self):
		if password.askpass("admin"):
			review.Review(status="admin")
		else:
			review.Review()
	def purchasepay(self):
		if not password.askpass("admin"):
			tkMessageBox.showerror("wrong password","try again")
			return 
		con=cdb.Db().connection()
		cur=con.cursor()
		sql = "select * from seller order by name;"
		cur.execute(sql)
		stockists=cur.fetchall()
		items =["   PURCHASE PAYMENT"," "]
		for stockist in stockists:
			sql="select count(amount), sum(amount) ,group_concat(amount) from purchase "\
				"where date < date_format(now(),'%Y-%m-01') and paid!=1 and seller="+str(stockist[0])+";"
			print sql
			cur.execute(sql)
			if cur.rowcount>0:
				res=cur.fetchone()			
				count=res[0]
				amount=res[1]
				bills=res[2]
				if count>0:
					item= " {:30s}{:10.2f} ::{}".format(stockist[1]+" ("+str(count)+")",amount,bills)
					items.append(item)
					sql="update purchase set paid=1 where seller="+str(stockist[0])+" and date<date_format(now(),'%Y-%m-01');"
					cur.execute(sql)
		con.commit()
		printer.printinfo(items)

	def setprinters(self):
		printer.Checkprinters()
	
	def dbparams(self):
		if password.askpass("admin"):
			win=cdb.DbVariables()

	def liststockists(self):
		if not password.askpass("admin"):
			tkMessageBox.showerror("error","wrong password",parent=self.master)
			return
		sql = "select name from seller order by name;"
		lines=["STOCKISTS"," "]
		con=cdb.Db().connection()
		cur=con.cursor()
		cur.execute(sql)
		result=cur.fetchall()
		for r in result:
			lines.append(r[0])
		printer.printinfo(lines)

	def noprinter(self):
		if not password.askpass("admin"):
			return
		sh=shelve.open("data.db")
		sh['noprinter']=self.debug.get()


if __name__=="__main__":
	Dialysis()


