import win32wnet
try:
    from Tkinter import *
except ImportError:
    from tkinter import *
try:
    from Tkinter import messagebox
except ImportError:
    from tkinter import messagebox
import ttk
#from Tkinter import ttk
import tkFileDialog
import os
import xml.etree.ElementTree as ET
import math
from datetime import datetime
import subprocess
import re

root = Tk()
root.title("Oracle Auto Backup")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

users_to_backup = StringVar()
oracle_path = StringVar()
your_path = StringVar()
backup_time_text = StringVar()
move_backup_time_text = StringVar()
toplevel_t=False

def browse(*args):
	if any(True for res in args if "oraclepath_browse"==res):
		directory = tkFileDialog.askdirectory()
		directory = re.sub("/",r"\\",directory)
		oracle_path.set(directory)
		oracle_path_entry.config(width=max(len(directory),20))
	if any(True for res in args if "yourpath_browse"==res):
		directory = tkFileDialog.askdirectory()
		directory = re.sub("/",r"\\",directory)
		your_path.set(directory)
		your_path_entry.config(width=max(len(directory),20))
	if any(True for res in args if "folderpath_browse"==res):
		directory = tkFileDialog.askdirectory()
		directory = str(re.sub("/",r"\\",directory))
		#print os.listdir(directory)
		folder_path_text.insert("1.0",directory+"\n")
		h=0
		max_width=40
		for i in folder_path_text.get("1.0",END).split("\n"):
			#print len(i)
			h+= math.ceil(len(i)/max_width)

		folder_path_text.config(width=min(max(len(i) for i in folder_path_text.get("1.0",END).split("\n")),max_width)+5,height=h+2)

def backup_time(*args):

	def destroy():
		if any(True for res in args if "move"==res):
			move_backup_time_text.set(backuptime.get()+" "+ampm.get())
			toplevel_t.destroy()
		else:
			backup_time_text.set(backuptime.get()+" "+ampm.get())
			toplevel_t.destroy()

	global toplevel_t # to destroy any toplevel previously raised
	if toplevel_t:
		toplevel_t.destroy()
	toplevel_t = Toplevel()
	#t.transient(root)
	toplevel_t.wm_title("Window")
	mainframe = ttk.Frame(toplevel_t, padding="1 1 1 1")
	mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
	mainframe.columnconfigure(0, weight=1)
	mainframe.rowconfigure(0, weight=1)
	if any(True for res in args if "move"==res):
		ttk.Label(mainframe, text="Move Backup Times").grid(column=1, row=1, sticky=W,padx=10, pady=1)
	else:
		ttk.Label(mainframe, text="Backup Times").grid(column=1, row=1, sticky=W,padx=10, pady=1)
	backuptime=StringVar()
	ampm=StringVar()
	ttk.OptionMenu(mainframe, backuptime, "1","2","3","4","5","6","7","8","9","10","11","12").grid(column=2, row=1, sticky=W,padx=0, pady=1)
	ttk.OptionMenu(mainframe, ampm, "PM","AM").grid(column=3, row=1, sticky=W,padx=0, pady=1)
	ttk.Button(mainframe, text="OK", command=destroy).grid(column=4, row=1, sticky=W,padx=10, pady=1)

def run_query(query=""):
    session = subprocess.Popen(['sqlplus','/ as sysdba'],stderr=subprocess.PIPE,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    session.stdin.write(query)
    stdout, stderr = session.communicate()
    return stdout , stderr

def check_user(users=""):
    try:
        stdout = run_query("SELECT username FROM dba_users WHERE username IN (%s);"%(users))
        invalid_users=[]
        for res in users.split(","):
        	if res.strip("'") not in stdout[0]:
        		invalid_users.append(res.strip("'"))
        		
        if invalid_users:
        	messagebox.showerror("Error", "Invalid Users = %s"%(",".join(invalid_users)))
        	raise ValueError('stuff is not in content')
        return True
    except Exception as e:
    	print "---error check user--",e
        return False

def task_on_close(*args):

	vars=['LOCALAPPDATA','APPDATA','HOMEPATH']
	file_path=""
	for i in vars:
		if os.environ.get(i,False):
			file_path=os.environ[i]
			break

	data_dir=os.path.join(file_path,"oracle_backup")
	if not os.path.exists(data_dir):
		os.makedirs(data_dir)

	user=True
	user_list=[user.strip(" ") for user in users_to_backup.get().split(',')]
	user_list_quote=["'"+user.upper()+"'" for user in user_list]
	user_list_string=",".join(user_list_quote)


	no_field_empty=True
	if not oracle_path.get() and no_field_empty:
		messagebox.showerror("Error", "'Default Oracle Backup Path' cannot be empty")
		no_field_empty=False
	if not your_path.get() and no_field_empty:
		messagebox.showerror("Error", "'Your Backup Path' cannot be empty")
		no_field_empty=False
	if not backup_time_text.get() and no_field_empty:
		messagebox.showerror("Error", "'Backup Time' cannot be empty")
		no_field_empty=False
	if not users_to_backup.get() and no_field_empty:
		messagebox.showerror("Error", "'DBA Users To Backup' cannot be empty")
		no_field_empty=False
	

	
	# CHECKING IF THE USERS TO BACKUP ARE VALID THEN ONLY CRAETE DATA FILE
	if no_field_empty and check_user(user_list_string):
		#messagebox.showerror("Error", "Invalid User = "%(user.strip(" ")))
		print "-------"
		write_values_to_file(data_dir)
		create_schedule_tasks(data_dir)
		root.destroy()


def write_values_to_file(data_dir):
	
	new_file=os.path.join(data_dir,"oracle_backup.txt")
	print new_file
	with open(new_file,"w") as f:
		if oracle_path.get():
			try:
				oracle_path_unc=(win32wnet.WNetGetUniversalName(oracle_path.get(), 1))
			except Exception as e:
				oracle_path_unc=oracle_path.get()
			f.write("oracle_path==%s\n"%(oracle_path_unc))

		if your_path.get():
			try:
				your_path_unc=(win32wnet.WNetGetUniversalName(your_path.get(), 1))
			except Exception as e:
				your_path_unc=your_path.get()
			f.write("your_path==%s\n"%(your_path_unc))
			
		folders=[]
		for res in folder_path_text.get("1.0",END).split("\n"):
			if res:
				try:
					folders.append((win32wnet.WNetGetUniversalName(folder_path.get(), 1)))
				except Exception as e:
					folders.append(res)
		if folders:
			f.write("folder_path_text==%s\n"%str(folders))

		if backup_time_text.get():
			f.write("backup_time_text==%s\n"%(backup_time_text.get()))
		if move_backup_time_text.get():
			f.write("move_backup_time_text==%s\n"%(move_backup_time_text.get()))
		if users_to_backup.get():
			f.write("users_to_backup_text==%s"%(users_to_backup.get().upper()))


def _create_task(name,raw_time,argument_to_xml,data_dir):

	time=datetime.strptime(raw_time,"%I %p").strftime("%H:%M")
	if "python_oracle_auto_backup.exe" in os.listdir(os.getcwd()) or "python_oracle_auto_backup.py" in os.listdir(os.getcwd()):
		exe_path='"'+os.path.join(os.getcwd(),"python_oracle_auto_backup.exe")+'"'
		print "exe_path--------------",exe_path
		
		## if the task already exists then delete and create a new one
		session = subprocess.Popen(['schtasks' ,'/Query', '/XML','/TN',name],stderr=subprocess.PIPE,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
		stdout, stderr = session.communicate()
		if stdout:subprocess.call(['SchTasks','/Delete','/TN' ,name,'/f'])
		
		# create a dummy one with name and time and ############# system user to run background ***************
		#if argument_to_xml=='move':
		#subprocess.call(['SchTasks','/Create','/RU','SYSTEM','/SC','DAILY', '/TN' ,name, '/TR', exe_path,'/ST' ,time])
		#else:
		subprocess.call(['SchTasks','/Create','/SC','DAILY', '/TN' ,name, '/TR', exe_path,'/ST' ,time])
		# query the task , output xml then edit xml to add custom lines
		session = subprocess.Popen(['schtasks' ,'/Query', '/XML','/TN',name],stderr=subprocess.PIPE,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
		stdout, stderr = session.communicate()
		stdout = stdout.replace("UTF-16","UTF-8")
		###removing namespcae from xml (xmlns)
		file_name=os.path.join(data_dir,"task_xml_file1.xml")
		with open(file_name,"w") as file:
			file.write(stdout)
		print stdout
		namespace=False
		if stdout.find("xmlns="):
			namespace=stdout[stdout.find("xmlns=")+6:stdout.find(">",stdout.find("xmlns="))]
			stdout = stdout.replace(namespace,'""')
			#print stdout
		root = ET.fromstring(stdout)
		#print root.tag,root.attrib
		#### adding arguments to task scheduler
		for child in root.iterfind('Actions/Exec'):
			a1=ET.SubElement(child,"Arguments")
			a1.text=argument_to_xml

		###### adding runlevel privelege , works only if py2exe has uac_admin
		for child in root.iterfind('Principals/Principal/RunLevel'):
			#print child.tag,child.text
			child.text="HighestAvailable"

		# putting back namespace
		if namespace:root.attrib["xmlns"]=namespace.strip('"')
		stdout = ET.tostring(root)
		print stdout 
		file_name=os.path.join(data_dir,"task_xml_file2.xml")
		with open(file_name,"w") as file:
			file.write(stdout)
		### creating new task with edited xml and deleting old one
		subprocess.call(['SchTasks','/Delete','/TN' ,name,'/f'])
		print "-----final xml file ============================="
		with open(file_name,"r") as file:
			for l in file.readlines():
				print l,
		subprocess.call(['SchTasks','/Create','/XML',file_name,'/TN' ,name])

	else:
		raise OSError("no file python_oracle_auto_backup.exe in %s"%(os.getcwd()))

def create_schedule_tasks(data_dir):
	#creating backup task
	if backup_time_text.get():_create_task("oracle_backup",backup_time_text.get(),"backup",data_dir)

	# create moving files task
	if move_backup_time_text.get():_create_task("oracle_move_backup",move_backup_time_text.get(),"move",data_dir)
	pass
	
	
def delete_text(event):
	event.widget.delete(0, END)



ttk.Label(mainframe, text="Default Oracle Backup Path").grid(column=1, row=1, sticky=W,padx=5, pady=5)
oracle_path_entry = ttk.Entry(mainframe, width=20, textvariable=oracle_path,state='readonly')
oracle_path_entry.grid(column=2, row=1, sticky=(W, E),padx=5, pady=5)
ttk.Button(mainframe, text="Browse", command=lambda: browse('oraclepath_browse')).grid(column=3, row=1, sticky=W,padx=5, pady=5)

ttk.Label(mainframe, text="Your Backup Path").grid(column=1, row=2, sticky=W,padx=5, pady=5)
your_path_entry = ttk.Entry(mainframe, width=20, textvariable=your_path,state='readonly')
your_path_entry.grid(column=2, row=2, sticky=(W, E),padx=5, pady=5)
ttk.Button(mainframe, text="Browse", command=lambda: browse('yourpath_browse')).grid(column=3, row=2, sticky=W,padx=5, pady=5)


ttk.Label(mainframe, text="Folders to Backup").grid(column=1, row=3, sticky=W,padx=5, pady=5)
folder_path_text = Text(mainframe,width=20,height=2,wrap=WORD)
folder_path_text.grid(column=2, row=3, sticky=W,padx=5, pady=5)
ttk.Button(mainframe, text="Browse", command=lambda: browse('folderpath_browse')).grid(column=3, row=3, sticky=W,padx=5, pady=5)


ttk.Label(mainframe, text="Backup Time").grid(column=1, row=4, sticky=W,padx=5, pady=5)
backup_time_entry = ttk.Entry(mainframe, width=20, textvariable=backup_time_text)
backup_time_entry.grid(column=2, row=4, sticky=(W, E),padx=5, pady=5)
ttk.Button(mainframe, text="Add Backup Time", command=lambda: backup_time()).grid(column=3, row=4, sticky=W,padx=5, pady=5)

ttk.Label(mainframe, text="Move Backup Time").grid(column=1, row=5, sticky=W,padx=5, pady=5)
move_time_entry = ttk.Entry(mainframe, width=20, textvariable=move_backup_time_text)
move_time_entry.grid(column=2, row=5, sticky=(W, E),padx=5, pady=5)
ttk.Button(mainframe, text="Move Backup Time", command=lambda: backup_time("move")).grid(column=3, row=5, sticky=W,padx=5, pady=5)

ttk.Label(mainframe, text="DBA Users To Backup").grid(column=1, row=6, sticky=W,padx=5, pady=5)
users_to_backup_entry = ttk.Entry(mainframe, width=20, textvariable=users_to_backup)
users_to_backup_entry.grid(column=2, row=6, sticky=(W, E),padx=5, pady=5)
default_user_text="ORDCON,RICHIERTAIL,RICHIERETAIL_PK,RICHIEGAR,RICHIEGAR_PK,RICHIESAREE,RICHIESAREE_PK"
with open(os.path.join(os.getcwd(),"Backup_Users\users_to_backup.txt"),"r") as file:
	for l in file.readlines():
		if '#' in l:
			continue
		else:
			default_user_text=l.strip("\n").strip(" ")

users_to_backup_entry.insert(0,default_user_text)
#users_to_backup_entry.bind('<FocusIn>',delete_text)

ok_btn = ttk.Button(mainframe, text="Ok", command=lambda: task_on_close()).grid(column=2, row=7, sticky=(W,E),padx=5, pady=5)

root.mainloop()

