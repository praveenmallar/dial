import os
header = ("Lions Dialysis Center","Payyanur ph: 04985 205119,202939")
import shelve
import tkMessageBox as tmb
import Tkinter as tk

class printer:
	
	def __init__(self):
		self.esc = "\x1b"
		self.gs="\x1d"
		self.output=""
		self.default()
		self.printers={"bill_printer":0}
	
		sh=shelve.open("data.db")
		self.printer=[None]*len(self.printers)
		for k in self.printers.keys():
			try:
				self.printer[self.printers[k]]=sh[k]
			except:
				pass
		try:
			self.noprinter=sh['noprinter']
		except:
			self.noprinter=False

	def default(self):
		self.output+=self.esc+"@"

	def align_left(self):
		self.output+=self.esc+"a"+chr(0)
	def align_center(self):
		self.output+=self.esc+"a"+chr(1)
	def align_right(self):
		self.output+=self.esc+"a"+chr(2)

	def underline(self):
		self.output+=self.esc+chr(45)+chr(1)
	def no_underline(self):
		self.output+=self.esc+chr(45)+chr(1)

	def bold(self):
		self.output+=self.esc+chr(69)+chr(1)
	def no_bold(self):
		self.output+=self.esc+chr(69)+chr(0)

	def font1(self):
		self.output+=self.esc+chr(77)+chr(0)
	def font2(self):
		self.output+=self.esc+chr(77)+chr(1)
	
	def blank(self,num=1):
		self.output+=self.esc+chr(100)+chr(num)

	def cut(self):
		self.output+=self.gs+chr(86)+chr(65)

	def title(self):
		self.output+=self.esc+chr(33)+chr(57)
	def no_title(self):
		self.output+=self.esc+chr(33)+chr(0)

	def text(self,text):
		self.output+=text+"\n"
	
	def printout(self):
		print self.output

	def toprinter(self,printer=0):
		prntr=self.printer[printer]
		if not self.noprinter:
			dev=os.open(prntr,os.O_RDWR)
			os.write(dev,self.output)
			os.write(dev,"\0")
			os.close(dev)
		else:
			print self.output
		f=open("bills.txt","a")
		output=(self.output).replace("\n","@@")+"\n"
		f.write	(output)
		f.close()

def printbill(billno,patient,sponsor,date,total,items,ip=None,selfbill=0,credit=False):
	p=printer()
	if selfbill==1:
		p.text("selfbill")
		p.blank(1)
	else:
		p.align_center()
		p.title()
		p.text(header[0])
		p.no_title()
		p.text(header[1])
		p.align_left()
		p.blank(1)
		p.blank()
		p.text("Bill number: "+str(billno))
	p.text("Patient: "+patient)
	if credit:p.text("**CREDIT bill**")	
	if sponsor:p.text("Sponsor: "+sponsor)
	if ip:p.text("IP #"+str(ip))
	p.text("date: "+str(date))
	p.blank(1)
	for item in items:
		p.text('  {:30s}{:7.2f}'.format(item[0],item[1]))		
	p.blank(1)
	blanklines=5-len(items)
	if blanklines>0:
		p.blank(blanklines)
	p.bold()
	if credit:
		p.text('  {:30s}{:7.2f}'.format("TOTAL: (credit) ",total))
	else:
		p.text('  {:30s}{:7.2f}'.format("TOTAL: ",total))
	p.no_bold()
	p.blank(2)
	p.align_right()	
	p.text('{:15s}'.format("Signature"))
	p.blank(2)	
	p.cut()
	p.toprinter()
	
def printinfo(lines):

	p=printer()
	p.blank(1)	
	for line in lines:
		p.text(line)
	p.blank(2)
	blines=10-len(lines)
	if blines>0:	
		p.blank(blines)
	p.cut()
	p.toprinter()

class Checkprinters:
	
	def __init__(self):

		self.sysprinters=None
		try:
			self.sysprinters=sp.check_output("ls /dev/usb/lp*",shell=True).split("\n")
		except:
			pass	 
		if not self.sysprinters:
			tmb.showerror("Error","No printer detected")
			return
		printers=printer().printers
		sh=shelve.open("data.db")
		shprinter={}
		for k in printers.keys():
			try:
				shprinter[k]=sh[k]
			except:
				shprinter[k]=None
		self.top=tk.Toplevel(parent=None)
		f=tk.Frame(self.top)
		f.pack()
		self.fins=[]
		for p in printers.keys():
			fin=tk.Frame(f)
			fin.pack(side=tk.TOP,pady=10)
			tk.Label(fin,text=p,width=10).pack(side=tk.LEFT)
			fin.printvar=tk.StringVar()
			fin.key=p
			printnum=1
			for s in self.sysprinters:
				if len(s)==0:
					continue
				prin="printer "+str(printnum)
				tk.Radiobutton(fin,text=prin,variable=fin.printvar,value=s,command=lambda x=s:self.demoprint(x) , width=8).pack(side=tk.LEFT)
				if shprinter[p]==s:
					fin.printvar.set(s)
				printnum+=1
			self.fins.append(fin)
		tk.Button(f,text="OK",command=self.selectprinters).pack(side=tk.RIGHT,pady=10)
		tk.Button(f,text="Cancel",command=lambda:self.top.destroy()).pack(side=tk.RIGHT,padx=10,pady=10)
		self.top.grab_set()

	def selectprinters(self):
		sh=shelve.open("data.db")
		for fin in self.fins:
			sh[fin.key]=fin.printvar.get()
		tmb.showinfo("Done","Printers saved",parent=self.top)
		self.top.destroy()

	def demoprint (self,printer):
		dev=os.open(printer,os.O_RDWR)
		os.write(dev,"xxxx")
		os.write(dev,"\0")
		os.close(dev)


