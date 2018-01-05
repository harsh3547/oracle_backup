from distutils.core import setup
import py2exe 
try:
    # py2exe 0.6.4 introduced a replacement modulefinder.
    # This means we have to add package paths there, not to the built-in
    # one.  If this new modulefinder gets integrated into Python, then
    # we might be able to revert this some day.
    # if this doesn't work, try import modulefinder
    try:
        import py2exe.mf as modulefinder
    except ImportError:
        import modulefinder
    import win32com, sys
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]: #,"win32com.mapi"
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass


mydata_files = [('Backup_Users', ['C:\Documents and Settings\Lahanga\My Documents\python_odoo\Dropbox\python_prog\oracle_backup\Backup_Users\users_to_backup.txt'])]

setup(windows=[{'script':'oracle_backup_gui.py','uac_info': "requireAdministrator"}],console=[{'script':'uninstall_run.py','uac_info': "requireAdministrator"},{'script':'python_oracle_auto_backup.py'}],data_files=mydata_files,options = {'py2exe': {'bundle_files': 3,'optimize':2,'skip_archive':False,'packages':['win32com']}},)


