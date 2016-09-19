from Tkinter import *
import comp1

def myfunc(e):
	print "event triggered"
tk=Tk()
a=comp1.myComp(tk)
a.bind("<<listChanged>>",myfunc)
a.pack()
tk.mainloop()


