from Tkinter import *
from comp import NumEntry
import dayreport
import tkMessageBox as tmb


class petty(Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.pack()
		self.master.title("payment")
		padx=20
		pady=10
		self.head=StringVar()
		self.amount=DoubleVar()
		Label(self,text="head").grid(row=0,column=0,padx=padx,pady=pady)
		Label(self,text="amount").grid(row=1,column=0,padx=padx,pady=pady)
		Entry(self,width=15,textvariable=self.head).grid(row=0,column=1,padx=padx,pady=pady)
		NumEntry(self,width=15,textvariable=self.amount).grid(row=1,column=1,padx=padx,pady=pady)
		Button(self,text="save",command=self.save).grid(row=3,column=1,padx=padx,pady=pady)

	def save(self):
		head=self.head.get()
		amount=self.amount.get()
		if float(amount)==0:
			return
		dayreport.dayrep.spend(head,amount)
		self.head.set("")
		self.amount.set(0)		
		tmb.showinfo("Done","Saved transaction",parent=self.master)

if __name__=="__main__":
	t=Tk()
	p=petty(t)
	p.mainloop()
