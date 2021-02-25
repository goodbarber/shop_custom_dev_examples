import sys
import os
import time
import atexit
from signal import SIGTERM 

class Daemon:

	def __init__(self, pidfile, callback, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
		self.stdin = stdin
		self.stdout = "/tmp/textAlertout.log"
		self.stderr = "/tmp/textAlerterr.log"
		self.pidfile = pidfile
		self.callback = callback
	
	def daemonize(self):
		#do the UNIX double-fork magic
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit first parent
				sys.exit(0) 
		except (OSError) as e: 
			sys.stderr.write(f"fork #1 failed: {e.errno} ({e.strerror})")
			sys.exit(1)
	
		# decouple from parent environment
		os.chdir("/") 
		os.setsid() #Make fork #1 a session leader with no TTY
		os.umask(0) 
	
		# do second fork
		try: 
			pid = os.fork() 
			if pid > 0:
				# exit from second parent
				sys.exit(0) 
		except (OSError) as e: 
			sys.stderr.write(f"fork #2 failed: {e.errno} ({e.strerror})")
			sys.exit(1) 
	
		# redirect standard fd
		sys.stdout.flush()
		sys.stderr.flush()
		si = open(self.stdin, 'r')
		so = open(self.stdout, 'a+')
		se = open(self.stderr, 'a+')
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())

	
		# write pidfile
		atexit.register(self.delpid)
		pid = str(os.getpid())

		open(self.pidfile,'w+').write(f"{pid}\n")

	def getPidFromFile(self):
		try:
			with open(self.pidfile,'r') as pf:
				return int(pf.read().strip())
		except IOError:
			return None

	def delpid(self):
		os.remove(self.pidfile)

	def start(self):
		"""
		Start the daemon
		"""
		pid = self.getPidFromFile()
	
		if pid:
			sys.stderr.write(f"Pidfile {self.pidfile} already exists. Daemon already running?\n")
			sys.exit(1)
		
		# Start the daemon
		self.daemonize()
		self.run()

	def stop(self):
		"""
		Stop the daemon
		"""
		pid = self.getPidFromFile()
	
		if not pid:
			sys.stderr.write(f"Pidfile {self.pidfile} does not exist. Daemon not running?\n")
			return # not an error in a restart

		# Try killing the daemon process	
		try:
			while 1:
				os.kill(pid, SIGTERM)
				time.sleep(0.1)
				
		except (OSError) as e:
			e = str(e)
			if e.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
					print("Daemon closed & pidfile successfully cleared")
			else:
				print(e)
				sys.exit(1)

	def restart(self):
		"""
		Restart the daemon
		"""
		self.stop()
		self.start()

	def run(self):
		"""
		You should override this method when you subclass Daemon. It will be called after the process has been
		daemonized by start() or restart().
		"""
		print("Daemon will start executing callback")
		self.callback()
		


if __name__ == '__main__':
    daemon = Daemon('/tmp/textAlert.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print('Unknown command')
            sys.exit(2)
        sys.exit(0)
    else:
        print(f"usage: {sys.argv[0]} start|stop|restart")
        sys.exit(2)