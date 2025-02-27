from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from utils.logger import logger
import utils.config as config
import threading
import logging
import os

# Suppress pyftpdlib logs
null_handler = logging.NullHandler()
logging.getLogger('pyftpdlib').addHandler(null_handler)

class CustomFTPHandler(FTPHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.host_ip = None
		self.host_port = None

	def ftp_SYST(self, line):
		self.respond(f"215 {config.get_service_by_name("ftp")["system_type"]}")

	def send_welcome(self):
		logger.info(f'"type":["connection","start","allowed"],"kind":"alert","category":["network","intrusion_detection"],"dataset":"faitour.honeypot","action":"send_welcome","reason":"FTP banner sent","outcome":"success"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}')
		self.respond(config.get_service_by_name("ftp")["banner"])

	def on_connect(self):
		logger.info(f'"type":["connection","start","allowed"],"kind":"alert","category":["network","intrusion_detection"],"dataset":"faitour.honeypot","action":"on_connect","reason":"FTP Connection established","outcome":"success"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}')

	def on_disconnect(self):
		logger.info(f'"type":["connection","end"],"kind":"alert","category":["network","intrusion_detection"],"dataset":"faitour.honeypot","action":"on_disconnect","reason":"FTP Connection closed","outcome":"success"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}')

	def on_login(self, username, ):
		logger.info(f'"type":["connection","start","allowed"],"kind":"alert","category":["network","authentication","intrusion_detection"],"dataset":"faitour.honeypot","action":"on_login","reason":"FTP User logged in","outcome":"success"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"user":{{"name":"{username}"')

	def on_login_failed(self, username, password):
		logger.info(f'"type":["connection","start","denied"],"kind":"alert","category":["network","authentication","intrusion_detection"],"dataset":"faitour.honeypot","action":"on_login_failed","reason":"FTP failed login","outcome":"failure"}},"source":{{"ip":"{self.remote_ip}","port":"{self.remote_port}"}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"user":{{"name":"{username}","password":"{password}"')

	def on_logout(self, username):
		logger.info(f'"type":["connection","end"],"kind":"alert","category":["network","intrusion_detection"],"dataset":"faitour.honeypot","action":"on_logout","reason":"FTP User logged out","outcome":"success"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"user":{{"name":"{username}"')

	def ftp_LIST(self, path):
		logger.info(f'"type":["access"],"kind":"alert","category":["file","network","intrusion_detection"],"dataset":"faitour.honeypot","action":"ftp_LIST","reason":"Directory listing for {path}","outcome":"success"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"file":{{"directory":"{path}"')
		super().ftp_LIST(path)

	def ftp_DELE(self, path):
		if path == "README.txt":
			logger.info(f'"type":["deletion"],"kind":"alert","category":["file","network","intrusion_detection"],"dataset":"faitour.honeypot","action":"ftp_DELE","reason":"File delete requested: {path}","outcome":"failure"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"file":{{"name":"{path}"')
			self.respond("550 Permission denied.")
		else:
			logger.info(f'"type":["deletion"],"kind":"alert","category":["file","network","intrusion_detection"],"dataset":"faitour.honeypot","action":"ftp_DELE","reason":"File delete requested: {path}","outcome":"success"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"file":{{"name":"{path}"')
			super().ftp_DELE(path)

	def ftp_MKD(self, path):
		logger.info(f'"type":["creation"],"kind":"alert","category":["file","network","intrusion_detection"],"dataset":"faitour.honeypot","action":"ftp_MKD","reason":"Directory creation requested: {path}","outcome":"success"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"file":{{"directory":"{path}"')
		super().ftp_MKD(path)

	def ftp_RMD(self, path):
		logger.info(f'"type":["deletion"],"kind":"alert","category":["file","network","intrusion_detection"],"dataset":"faitour.honeypot","action":"ftp_RMD","reason":"Directory deletion requested: {path}","outcome":"success"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"file":{{"directory":"{path}"')
		super().ftp_RMD(path)

	def on_file_sent(self, file):
		logger.info(f'"type":["access"],"kind":"alert","category":["file","network","intrusion_detection"],"dataset":"faitour.honeypot","action":"on_file_sent","reason":"FTP File sent","outcome":"success"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"file":{{"name":"{file}"')

	def on_file_received(self, file):
		logger.info(f'"type":["creation"],"kind":"alert","category":["file","network","intrusion_detection"],"dataset":"faitour.honeypot","action":"on_file_received","reason":"FTP File received","outcome":"success"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"file":{{"name":"{file}"')

	def on_incomplete_file_sent(self, file):
		logger.info(f'"type":["access"],"kind":"alert","category":["file","network","intrusion_detection"],"dataset":"faitour.honeypot","action":"on_incomplete_file_sent","reason":"FTP Incomplete file sent","outcome":"failure"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"file":{{"name":"{file}"')

	def on_incomplete_file_received(self, file):
		logger.info(f'"type":["creation"],"kind":"alert","category":["file","network","intrusion_detection"],"dataset":"faitour.honeypot","action":"on_incomplete_file_received","reason":"FTP Incomplete file received","outcome":"failure"}},"source":{{"ip":"{self.remote_ip}","port":{self.remote_port}}},"destination":{{"ip":"{self.host_ip}","port":{self.host_port}}},"file":{{"name":"{file}"')

class FTPServerEmulator(threading.Thread):
	def __init__(self):
		super().__init__()
		self.running = False
		self.host_ip = config.get_value("network.adapter.ip")
		self.host_port = config.get_service_by_name("ftp")["port"]
		self.root_dir = "./emulators/ftp_root"

		# Ensure the root directory exists
		if not os.path.exists(self.root_dir):
			os.makedirs(self.root_dir)

		self.authorizer = DummyAuthorizer()
		
		# Define a custom handler subclass with host and port
		host_ip = self.host_ip
		host_port = self.host_port
		class CustomHandlerWithHostPort(CustomFTPHandler):
			def __init__(self, *args, **kwargs):
				super().__init__(*args, **kwargs)
				self.host_ip = host_ip
				self.host_port = host_port

		self.handler = CustomHandlerWithHostPort
		self.server = None

	# Add a user with full read/write permissions
	def setup_server(self):
		username = config.get_service_by_name("ftp")["username"]
		password = config.get_service_by_name("ftp")["password"]
		self.authorizer.add_user(username, password, self.root_dir, perm='elradfmw')
		self.authorizer.add_anonymous(self.root_dir, perm='elr')

		self.handler.authorizer = self.authorizer

		# Create the FTP server instance
		self.server = FTPServer((self.host_ip, self.host_port), self.handler)
		self.handler.banner = config.get_service_by_name("ftp")["banner"].strip()

	# Start the FTP server
	def start(self):
		self.setup_server()
		logger.info(f'"type":["info"],"kind":"event","category":["process"],"dataset":"faitour.application","action":"stop","reason":"FTP server emulator is starting","outcome":"unknown"}},"server":{{"ip":"{self.host_ip}","port":{self.host_port}')
		self.running = True
		self.server.serve_forever()
		logger.info(f'"type":["start"],"kind":"event","category":["process"],"dataset":"faitour.application","action":"stop","reason":"FTP server emulator has started","outcome":"success"}},"server":{{"ip":"{self.host_ip}","port":{self.host_port}')

	# Stop the FTP server
	def stop(self):
		if self.server:
			logger.info(f'"type":["info"],"kind":"event","category":["process"],"dataset":"faitour.application","action":"stop","reason":"FTP server emulator is stopping","outcome":"unknown"}},"server":{{"ip":"{self.host_ip}","port":{self.host_port}')
			self.running = False
			self.server.close_all()
			logger.info(f'"type":["end"],"kind":"event","category":["process"],"dataset":"faitour.application","action":"stop","reason":"FTP server emulator has stopped","outcome":"success"}},"server":{{"ip":"{self.host_ip}","port":{self.host_port}')
