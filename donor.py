from Tkinter import *
import comp
import connectdb as cdb
import tkMessageBox as tmb
import datetime as dt
import printer


class Donor (Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent,bd=1,relief=RIDGE)
		self.pack(padx=3,pady=3)
		Label (self,text="Donors",font="Halvetica 10 bold").pack(pady=15)
		f1=Frame(self,bd=1)
		f1.pack(side=LEFT,fill=Y)
		f=Frame(f1,relief=SUNKEN,bd=1)
		f.pack()
		self.donors=comp.myComp2(f,listitems=[],listheight=5)
		self.addnew=Entry(f)
		self.donors.pack(padx=20,pady=10)
		self.addnew.pack(pady=20,padx=10)
		Button(f,text="Add New",command=self.add).pack(padx=10)
		f2=Frame(self,bd=1,relief=RAISED)
		f2.pack()		
		self.donorvalue=StringVar()
		self.donorvalue.set("Value =")
		Label(f2,textvariable=self.donorvalue,width=15,height=2,bg="#bbbb00").pack(fill=X, expand=1)
		f3=Frame(f2,bd=1, relief=SUNKEN)
		f3.pack(fill=Y,expand=1,pady=10)		
		self.value=DoubleVar()
		Label(f3,text="Donation").grid(row=0,column=0,padx=10)
		Entry(f3,textvariable=self.value).grid(row=0,column=1,pady=4)
		Button(f3,text="Add",command=self.donate).grid(row=1,column=1)
		self.donors.bind("<<listChanged>>",self.listchanged)
		f4=Frame(self,bd=1,relief=RAISED)
		f4.pack(pady=5)
		Label(f4,text="Donations").pack()
		f=Frame(f4)
		f.pack()
		sb=Scrollbar(f)
		sb.pack(side=RIGHT,fill=Y)
		self.donationlist=Canvas(f,width=200,height=100,bd=1,yscrollcommand=sb.set)
		self.donationlist.pack()
		self.donationlist.items=None
		sb.config(command=self.donationlist.yview)
		f=Frame(f4)
		f.pack()
		Label(f,text="print").pack(side=LEFT)
		self.donationlistprint=IntVar()
		e=comp.NumEntry(f,textvariable=self.donationlistprint,width=4)
		e.pack(side=LEFT)
		e.bind("<Return>",self.printdonationlist)
		Label(f,text="lines").pack(side=LEFT)
		f=Frame(self,bd=1,relief=RAISED)
		f.pack()
		Label(f,text="Sponsors done so far").pack()
		ff=Frame(f)
		ff.pack()
		sb=Scrollbar(ff)
		sb.pack(side=RIGHT,fill=Y)
		self.sponsorlist=Canvas(ff,width=240,height=120,bd=1,yscrollcommand=sb.set)
		self.sponsorlist.pack()
		self.sponsorlist.items=None
		sb.config(command=self.sponsorlist.yview)
		ff=Frame(f)
		ff.pack()
		Label(ff,text="print").pack(side=LEFT)
		self.sponsorlistprint=IntVar()
		e=comp.NumEntry(ff,textvariable=self.sponsorlistprint,width=4)
		e.pack(side=LEFT)
		e.bind("<Return>",self.printsponsorlist)
		Label(ff,text="lines").pack(side=LEFT)


		self.changelist()
		

	def changelist(self,e=None):
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="select name, id , value from donor order by name;"
		cur.execute(sql)
		rows=cur.fetchall()
		arr=[]
		for row in rows:
			arr.append([row[0],row])
		self.donors.changelist(arr)

	def add(self):
		if not tmb.askyesno("Confirm","Add Donor?",parent=self.master):
			return
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="insert into donor (name,value) values(%s,0);"
		cur.execute(sql,(self.addnew.get()))
		con.commit()
		self.changelist()
		self.addnew.set("")

	def listchanged(self,e=None):
		self.donorvalue.set("Value ="+str(self.donors.get()[1][2]))
		self.showDonations()
		self.showSponsorings()

	def donate(self):
		if not tmb.askyesno("Confirm","Make Donation?",parent=self.master):
			return
		con=cdb.Db().connection()
		cur=con.cursor()
		donor=self.donors.get()[1]
		index=self.donors.index()
		try:
			value=self.value.get()			
			sql="update donor set value=value+%s where id=%s"
			cur.execute(sql,(self.value.get(),donor[1]))
			sql="insert into donation(donor, value) values(%s,%s);"
			cur.execute(sql,(donor[1],value))
			con.commit()
			self.value.set("")	
			lines=[]
			lines.extend(printer.header)
			lines.append(" ")
			lines.extend(["Received Rs "+"{:5.2f}".format(value), "with thanks from "+donor[0]])
			lines.extend(["towards sponsoship for dialysis for needy patients"," ", "Thank you"])
			printer.printinfo(lines)
		except Exception as e:
			tmb.showinfo("Error ",str(e))
			con.rollback()
		self.changelist()
		self.donors.see(index)

	def showDonations(self):
		donor=self.donors.get()[1][1]
		cur=cdb.Db().connection().cursor(cdb.dictcursor)
		cur.execute("select * from donation where donor=%s order by datestamp desc;",(donor))
		rows=cur.fetchall()
		self.donationlist.delete(ALL)
		i=0
		self.donationlist.items=[]
		for r in rows:
			f=Frame(self.donationlist,height=30)
			date=r['datestamp'].strftime('%d %b,%y')
			Label(f,width=3,text=str(i+1),bd=1,relief=SUNKEN).pack(side=LEFT)
			Label(f, width=10,text=date,bd=1,relief=SUNKEN).pack(side=LEFT)
			Label(f,width=10,text=r['value'],bd=1,relief=SUNKEN).pack(side=LEFT)			
			self.donationlist.create_window(1,1+i*18,window=f,anchor=NW)
			i+=1
			self.donationlist.items.append("{:%d%b%y} :{:9.2f}".format(r['datestamp'],r['value']))
		self.donationlist.update_idletasks()
		self.donationlist.config(scrollregion=self.donationlist.bbox(ALL))	

	def printdonationlist(self,e=None):
		num=self.donationlistprint.get()
		lines= ["Last "+str(num)+ " donations by "+self.donors.get()[1][0]]
		lines.extend( self.donationlist.items[:num])
		printer.printinfo(lines)

	def showSponsorings(self):
		donor=self.donors.get()[1][1]
		cur=cdb.Db().connection().cursor(cdb.dictcursor)
		cur.execute("select bill.date as date,patient.name as patient,bill.amount as value from donor join sponsorship on donor.id=sponsorship.donor join bill on sponsorship.bill=bill.id join patient on bill.patient=patient.id where donor.id=%s order by bill.date desc",(donor))
		rows=cur.fetchall()
		self.sponsorlist.delete(ALL)
		i=0
		self.sponsorlist.items=[]
		for r in rows:
			f=Frame(self.sponsorlist,height=30)
			date=r['date'].strftime('%d %b,%y')
			Label(f,width=3,text=str(i+1),bd=1,relief=SUNKEN).pack(side=LEFT)
			Label(f, width=8,text=date,bd=1,relief=SUNKEN).pack(side=LEFT)
			Label(f,width=10,text="{:.10s}".format(r['patient']),bd=1,relief=SUNKEN).pack(side=LEFT)
			Label(f,width=7,text=r['value'],bd=1,relief=SUNKEN).pack(side=LEFT)			
			self.sponsorlist.create_window(1,1+i*18,window=f,anchor=NW)
			i+=1
			self.sponsorlist.items.append("{:%d%b%y} {:10.10s} :{:9.2f}".format(r['date'],r['patient'],r['value']))
		self.sponsorlist.update_idletasks()
		self.sponsorlist.config(scrollregion=self.donationlist.bbox(ALL))	

	def printsponsorlist(self,e=None):
		num=self.sponsorlistprint.get()
		lines= ["Last "+str(num)+ " sponsorships by "+self.donors.get()[1][0]]
		lines.extend( self.sponsorlist.items[:num])
		printer.printinfo(lines)	


if __name__=="__main__":
	t=Tk()
	a=Donor(t)
	
	t.mainloop()
