from Tkinter import *
import printer 
import comp
import connectdb as cdb
import tkMessageBox as tmb
import calpicker as cp
import dayreport as dr
import datetime

class Review (Frame):
	def __init__(self,parent=None,status=0):
		self.status=status
		if not parent:
			parent=Toplevel()
		Frame.__init__(self, parent)
		parent.minsize(width=800,height=600)
		f1=Frame(self,height=100,width=800,bd=2,relief=SUNKEN)
		f1.pack(side=TOP,fill=X)
		self.f1=f1
		f1.pack_propagate(0)
		
		f2=Frame(self, width=250,height=500,bd=2,relief=SUNKEN)
		f2.pack(side=LEFT,fill=Y)
		f2.fr=None
		self.f2=f2
		f2.pack_propagate(0)

		f3=Frame(self,bd=1,relief=RIDGE,width=550)
		f3.pack(fill=BOTH,expand=1)
		sb=Scrollbar(f3)
		sb.pack(side=RIGHT,fill=Y)
		self.canvas=Canvas(f3,yscrollcommand=sb.set)
		self.canvas.pack(fill=BOTH,expand=1)
		sb.config(command=self.canvas.yview)
		self.f3=f3

		self.pack()
		self.packoptions()
		self.lines=[]

	def packoptions(self):
		Button(self.f1,text="Sale",command=lambda:self.showOptions("sale")).pack(side=LEFT)
		Button(self.f1,text="day reports",command=lambda:self.showOptions("dayrep")).pack(side=LEFT)

		if self.status=="admin":
			Button(self.f1,text="Print",command=self.printlines).pack(side=RIGHT)



	def showOptions(self,selection):
		f=self.f2
		if f.fr:
			f.fr.pack_forget()

		if selection =="dayrep":
			f.fr=fr=Frame(f,bd=1)
			fr.pack(padx=5,pady=5)
			Label(fr,text="select date").pack(pady=20)
			dt=cp.Calbutton(fr)
			dt.pack()
			Button(fr,text="Load",command=lambda d=dt:self.showdayrep(dt)).pack(pady=10)

	def showdayrep(self,dt):
		d=dt.get()
		day= datetime.datetime.strptime(d,"%d-%b-%y").strftime("%Y%m%d")
		lines=dr.dayrep.get(day)
		self.canvas.delete(ALL)
		i=0
		self.lines=[]
		for row in lines:
			line=" {:30.30s}:  {:10.2f} : {:12.2f}".format(*row)
			self.lines.append(line)
			self.canvas.create_text(2,5+i*20,text=line,anchor=NW,font=("FreeMono",10))
			i+=1
		self.canvas.config(scrollregion=self.canvas.bbox(ALL))
		
	
	def showSale(self,mode,*args):
		if mode=="bills":
			v1=args[0].get()
			v2=args[1].get()
			sql="select bill.id, patient.name as patient, bill.date, bill.amount from bill join patient on bill.patient=patient.id "\
				" where bill.id>="+str(v1)+" and bill.id<="+str(v2)+" order by bill.id;"
			self.fillCanvas(sql)
		
			

	def fillCanvas(self,sql):
		self.canvas.delete(ALL)
		con=cdb.Db().connection()
		cur=con.cursor()
		try:
			cur.execute(sql)
			rows=cur.fetchall()
		except:
			tmb.showerror("Error","check for values",parent=self.master)
			return
		i=0
		self.lines=[]
		for row in rows:
			line=", ".join([str(s) for s in row])
			self.lines.append(line)
			self.canvas.create_text(2,5+i*20,text=line,anchor=NW)
			i+=1
		self.canvas.config(scrollregion=self.canvas.bbox(ALL))

	def printlines(self):
		printer.printinfo(self.lines)
			
	
if __name__=="__main__":
	t=Tk()	
	a=Review(t)
	a.mainloop()
