from distutils.core import setup
import py2exe 

mydata_files = [('Backup_Users', ['D:\Documents(D)\python_prog\oracle_backup\Backup_Users\users_to_backup.txt'])]

setup(windows=[{'script':'oracle_backup_gui.py','uac_info': "requireAdministrator"}],console=[{'script':'uninstall_run.py','uac_info': "requireAdministrator"},{'script':'python_oracle_auto_backup.py'}],data_files=mydata_files,options = {'py2exe': {'bundle_files': 3,'optimize':2,'skip_archive':False}},)


