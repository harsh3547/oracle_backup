import subprocess

for name in ['oracle_backup','oracle_move_backup']:
	session = subprocess.Popen(['schtasks' ,'/Query', '/XML','/TN',name],stderr=subprocess.PIPE,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
	stdout, stderr = session.communicate()
	if stdout:subprocess.call(['SchTasks','/Delete','/TN' ,name,'/f'])
