from Tkinter import *
import connectdb as cdb


class reporter (Frame):

	def __init__(self, parent, bill=None):
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
		f.pack()
		sb=Scrollbar(f)
		sb.pack(side=RIGHT,fill=Y)
		self.reports=Canvas(f,width=350,height=300,yscrollcommand=sb.set)
		sb.config(command=self.reports.yview)
		self.reports.pack()

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

if __name__=="__main__":
	t= Tk()
	b=reporter(t)
	b.mainloop()
