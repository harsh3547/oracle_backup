# create zulia/zulia user in oracle with dba privileges
import shutil, errno
import subprocess
import os
import datetime
import re
import time
import sys
import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

print "system argumenst ----",sys.argv

vars=['LOCALAPPDATA','APPDATA','HOMEPATH']
file_path=""
for i in vars:
    if os.environ.get(i,False):
        file_path=os.environ[i]
        break
#file_path=os.getcwd()
dba_users_to_backup = "None"
oracle_path=""
your_path=""
folder_path_text=[]
data_dir=os.path.join(file_path,"oracle_backup")
if "oracle_backup.txt" in os.listdir(data_dir):
    with open(os.path.join(data_dir,'oracle_backup.txt'),'r') as file:
        for line in file.readlines():
            if "oracle_path" in line:
                oracle_path=line.split("==")[1].strip("\n")
                print oracle_path
            if "your_path" in line:
                your_path=line.split("==")[1].strip("\n")
                print your_path
            if "folder_path_text" in line:
                for li in line.split("'"):
                    if os.path.exists(li):
                        folder_path_text.append(li)
                print folder_path_text
            if "users_to_backup_text" in line:
                dba_users_to_backup=line.split("==")[1].strip("\n")



two_days_in_sec=2*24*60*60
ts_epoch = time.time()

file_name = "RR_"+datetime.datetime.now().strftime("%d_%m_%y_%H_%M")+".dmp"
print file_name


# checking if user zulia for dba_backup exists
def run_query(query=""):
    session = subprocess.Popen(['sqlplus','/ as sysdba'],stderr=subprocess.PIPE,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    session.stdin.write(query)
    stdout, stderr = session.communicate()
    return stdout , stderr

def check_user():
    try:
        stdout = run_query("SELECT username FROM dba_users WHERE username='ZULIA';")[0]
        if 'ZULIA' not in stdout:

            run_query("create user zulia identified by zulia;")[0]
            run_query("grant all privileges to zulia;")[0]
            run_query("grant dba to zulia;")[0]
        return True
    except:
        return False

def _print_verbose(dir_1,files=[]):
    print dir_1,files
    return []

def copyanything(src, dst):
    try:
        if os.path.exists(dst) and os.path.isdir(dst):
            subprocess.call(['rmdir','/s','/q',dst],shell=True)
        shutil.copytree(src, dst,ignore=_print_verbose)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

def zipfile_method(src,dst,arc_name=""):
    print src,dst,arc_name
    print "---zipping file--",src
    zf = zipfile.ZipFile(dst, mode='w',compression=compression)
    try:
        print 'adding ',src
        zf.write(src,arcname=arc_name)
    finally:
        print 'closing'
        zf.close()
    print dst
    return dst
    

def create_backup():

    if check_user():
        backup_path_dir = your_path if os.path.exists(your_path) else oracle_path
        backup_path_dir_temp = data_dir
        backup_path = False
        if backup_path_dir_temp:
            backup_path = os.path.join(backup_path_dir_temp,file_name)
            print "-----create_backup in --------",backup_path
            p = subprocess.call(['exp','userid=zulia/zulia','owner='+dba_users_to_backup,"file="+backup_path],stdout=subprocess.PIPE)
            ts_epoch = time.time()
            os.utime(backup_path,(ts_epoch,ts_epoch)) # TO SET CREATE AND MODIFIED TIME OF A FILE
        if backup_path_dir and backup_path:
            src=backup_path
            dst=backup_path.lower().replace(".dmp",".zip")
            arc_name=file_name
            backup_path_zip = zipfile_method(src,dst,arc_name)
            print "-----moving file--",backup_path_zip,backup_path_dir
            subprocess.call(['move','/y',backup_path_zip,backup_path_dir],stdout=subprocess.PIPE,shell=True)
            print "-----deleting src dmp file--",src
            subprocess.call(['del',src],stdout=subprocess.PIPE,shell=True)

    # copy folders to backup locations
    if os.path.exists(your_path):
        for folder in folder_path_text:
            print "----******************************************************copying files ..........................."
            # extracting the folder name of folder var and join to your_path 
            # so if the dir exists it is deleted and created again else dir is created
            your_path_m=os.path.join(your_path,os.path.basename(os.path.normpath(folder)))
            print "----copying ---------",folder,"--to---",your_path_m
            copyanything(folder,your_path_m)


def move_bckup_from_oracle_path():
    # transferring backup files of last two days to A:\TBS
    frmPATH=oracle_path
    toPATH=your_path
    for file in os.listdir(frmPATH):
        try:
            if ('rr' in file.lower()) and ('_' in file.lower()) and ('.dmp' in file.lower()):
                if ts_epoch - os.path.getmtime(os.path.join(frmPATH,file)) < two_days_in_sec:
                    src=os.path.join(frmPATH,file)
                    dst=os.path.join(frmPATH,file.lower().replace(".dmp",".zip"))
                    arc_name=file
                    backup_path_zip = zipfile_method(src,dst,arc_name)
                    
                    print "---moving file--",backup_path_zip,toPATH
                    subprocess.call(['move','/y',backup_path_zip,toPATH],stdout=subprocess.PIPE,shell=True)
                    print "-----deleting src dmp file--",src
                    subprocess.call(['del',src],stdout=subprocess.PIPE,shell=True)
                    
        except OSError:
            pass


def delete_old_files():
    # deleting backup files older than 2 days
    PATHS_TO_CHECK=[oracle_path,your_path]
    for path in PATHS_TO_CHECK:
        try:
            for file in os.listdir(path):
                try:
                    if ('rr' in file.lower()) and ('_' in file.lower()) and (('.dmp' in file.lower()) or ('.zip' in file.lower())):
                        if ts_epoch - os.path.getmtime(os.path.join(path,file)) > two_days_in_sec:
                            print "--deleting files--",os.path.join(path,file)
                            subprocess.call(['del',os.path.join(path,file)],stdout=subprocess.PIPE,shell=True)
                except OSError:
                    pass

        except OSError:
            pass


try:
    if "backup" in sys.argv:
        print "--creating backup"
        create_backup()
        pass
    
    if "move" in sys.argv:
        move_bckup_from_oracle_path()
        delete_old_files()
        pass
    

except OSError as e:
    print e
    pass

#run_query("SELECT username FROM dba_users WHERE username='ZULIA';")[0]
