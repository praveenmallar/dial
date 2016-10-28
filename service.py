from Tkinter import *
import connectdb as cdb
import tkMessageBox as tmb
import comp 
import shelve

class Inv(Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.pack()
		b=InvFrame(self)
		c=ServiceProducts(self)
		a=InvList(self,b,c)
		b.invlist=a
		c.pack(side=RIGHT,ipadx=25,ipady=25,padx=10,pady=5)
		a.pack(side=TOP,ipadx=25,ipady=25)
		b.pack(side=TOP,ipadx=25,ipady=25)



class InvList(Frame):
	
	def __init__(self,parent=None,invFrame=None,serviceProduct=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent)
		self.invFrame=invFrame
		self.serviceProduct=serviceProduct
		self.packitems()
	
	def packitems(self):
		try:
			self.f.pack_forget()
		except:
			pass		
		self.f=Frame(self)
		self.f.pack()
		self.list=comp.myComp2(self.f,listheight=5)
		self.list.pack(side=LEFT)
		f=Frame(self.f)
		f.pack(side=LEFT,ipadx=10,ipady=10)
		self.list.bind("<<listChanged>>",self.load)
		self.deleteButton=Button(f,text="Delete",command=self.delete)
		self.deleteButton.pack()
		self.add=Button(f,text="New",command=self.new)
		self.add.pack()
		self.reload()

	def reload(self):
		cur=cdb.Db().connection().cursor()
		sql="select * from service order by name;"
		cur.execute(sql)
		rows=cur.fetchall()
		temp=[]
		for r in rows:
			temp.append([r[1],r[0]])
		self.list.changelist(temp)		
		
	def load(self,e=None):
		id=self.list.get()[1]
		self.invFrame.load(id)
		self.serviceProduct.load(id)
	
	def new(self):
		self.invFrame.load()
	
	def delete(self):
		inv=self.list.get()
		if not tmb.askyesno("Confirm","Delete the investigation "+inv[0]+"?",parent=self.master):
			return
		sql="delete from service where id =%s"
		con=cdb.Db().connection()
		cur=con.cursor()
		cur.execute(sql,(inv[1]))
		con.commit()
		sh=shelve.open("data.db")
		try:
			data=sh['misc']
		except:
			data="\n"
		data+="deleted service "+ str(inv[0])+"\n"
		sh['misc']=data
		self.packitems()

class InvFrame(Frame):
	
	def __init__(self,parent=None,inv=None,*arg,**karg):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent,*arg,**karg)
		self.id=inv
		self.invlist=None
		Label(self,text="Service").grid(row=0,column=0)
		self.name=StringVar()
		Entry(self,textvariable=self.name).grid(row=0,column=1,sticky=E+W,padx=10,pady=10)
		Label(self,text="rate").grid(row=1,column=0)
		self.rate=DoubleVar()
		Entry(self,textvariable=self.rate).grid(row=1,column=1,sticky=E+W,padx=10,pady=10)
		self.save=Button(self,text="save",command=self.save)
		self.save.grid(row=3,column=1,padx=10,pady=10)
		self.save.bind("<Return>",self.save)
		if self.id:
			self.load(self.id)

	def load(self,id=None):
		if not id:
			self.clear()
			self.id=None
			return
		self.id=id
		sql="select * from service where id=%s"
		cur=cdb.Db().connection().cursor()
		cur.execute(sql,(id))
		row=cur.fetchone()
		self.name.set(row[1])
		self.rate.set(row[2])

	def save(self):
		sh=shelve.open("data.db")
		if self.id:
			id=self.id
			name=self.name.get()
			rate=self.rate.get()
			try:
				cn=cdb.Db().connection()
				cr=cn.cursor()
				sql="update service set name=%s , rate=%s where id=%s;"
				cr.execute(sql,(name,rate,id))
				cn.commit()
				tmb.showinfo("Done","updated service",parent=self.master)
				try:
					data=sh['misc']
				except:
					data="\n"
				data+="updated service "+ name+" rate="+str(rate)+"\n"
				sh['misc']=data
			except:
				tmb.showerror("Error","couldn't update database",parent=self.master)
		else:
			if tmb.askyesno("Confirm","Add New Service?",parent=self.master):			
				try:
					name=self.name.get()
					rate=self.rate.get()
					cn=cdb.Db().connection()
					cr=cn.cursor()
					sql="insert into service(name,rate) values(%s,%s);"
					cr.execute(sql,(name,rate))
					cn.commit()
					tmb.showinfo("Done","Added the Service",parent=self.master)
					self.clear()
					self.invlist.reload()
					try:
						data=sh['misc']
					except:
						data="\n"
					data+="added service "+ name+" rate= "+str(rate)+"\n"
					sh['misc']=data
				except Exception,e:
					tmb.showerror("Error -couldn't update database",e,parent=self.master)

	def clear(self):
		self.name.set("")
		self.rate.set("")

class ServiceProducts (Frame):
	def __init__(self,parent=None):
		if not parent:
			parent=Toplevel()
		Frame.__init__(self,parent,bd=2,relief=RAISED)
		Label(self,text="products for service",font="Helvetica 12").grid(row=0,column=0,columnspan=4)
		self.product=comp.myComp2(self,listheight=2,listitems=[])
		self.product.grid(row=1,column=0,pady=10,padx=5)
		Label(self,text="count").grid(row=1,column=1)
		self.count=IntVar()
		num=comp.NumEntry(self,width=3,textvariable=self.count)
		num.grid(row=1,column=2)
		b=Button(self,text="Add",command=self.add)
		b.grid(row=1,column=3)
		b.bind("<Return>",self.add)
		num.bind("<Return>",self.add)
		f=Frame(self,bd=1,relief=RIDGE,width=250,height=200)
		f.grid(row=2,column=0,columnspan=4)
		sb=Scrollbar(f)
		sb.pack(side=RIGHT,fill=Y)
		self.canvas=Canvas(f,yscrollcommand=sb.set)
		self.canvas.pack(fill=BOTH,expand=1)
		sb.config(command=self.canvas.yview)
		self.loadproducts()
		self.bin=PhotoImage(file="images/bin.png")
		
	def loadproducts(self):
		cur=cdb.Db().connection().cursor()
		sql="select * from products order by name;"
		cur.execute(sql)
		rows=cur.fetchall()
		items=[]
		for r in rows:
			items.append([r[1],r[0]])
		self.product.changelist(items)

	def add(self,event=None):
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="insert into productservice values(%s,%s,%s);"
		cur.execute(sql,(self.id,self.product.get()[1],self.count.get()))		
		con.commit()
		self.load(self.id)
		self.product.clear()
		self.count.set("")		

	def load(self,id):
		self.id=id
		cur=cdb.Db().connection().cursor()
		sql="select products.name, productservice.count,products.id from service join productservice on service.id=productservice.service "\
			" join products on productservice.product=products.id where service.id=%s"
		cur.execute(sql,(id))
		rows=cur.fetchall()
		self.items=[]
		for r in rows:
			f=Frame(self.canvas,height=30)
			Label(f,width=20,text=r[0]).pack(side=LEFT)
			Label(f,width=5,text=r[1]).pack(side=LEFT)
			f.product=r[2]
			Button(f,image=self.bin,command=lambda x=f:self.remove(x)).pack(side=LEFT,padx=5)
			self.items.append(f)
		self.refreshcanvas()

	def refreshcanvas(self):
		self.canvas.delete(ALL)
		i=0
		for f in self.items:
			self.canvas.create_window(1,1+i*30,window=f,anchor=NW)
			i+=1
		self.canvas.update_idletasks()
		self.canvas.config(scrollregion=self.canvas.bbox(ALL))

	def remove(self,f):
		con=cdb.Db().connection()
		cur=con.cursor()
		sql="delete from productservice where service=%s and product=%s;"
		cur.execute(sql,(self.id,f.product))
		con.commit()
		self.load(self.id)

if __name__=="__main__":
	i=Inv()
	i.mainloop()
