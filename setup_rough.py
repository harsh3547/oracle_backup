from distutils.core import setup
import py2exe 


setup(console=[{'script':'rough1.py','uac_info': "requireAdministrator"}],options = {'py2exe': {'bundle_files': 3,'optimize':2,'skip_archive':False}},)


