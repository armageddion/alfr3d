# Adapted for containerization: logging to stdout, MySQLdb to pymysql
import os
import sys
import time
import logging
import socket
import pymysql  # Changed from MySQLdb
from kafka import KafkaConsumer,KafkaProducer
from datetime import datetime, timedelta

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging
logger = logging.getLogger("DevicesLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# Changed to stream handler for container logging
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

DATABASE_URL 	= os.environ['DATABASE_URL']
DATABASE_NAME 	= os.environ['DATABASE_NAME']
DATABASE_USER 	= os.environ['DATABASE_USER']
DATABASE_PSWD 	= os.environ['DATABASE_PSWD']
KAFKA_URL 		= os.environ['KAFKA_BOOTSTRAP_SERVERS']

producer = None
while producer is None:
    try:
        producer = KafkaProducer(bootstrap_servers=[KAFKA_URL])
        logger.info("Connected to Kafka")
    except Exception as e:
        logger.error("Failed to connect to Kafka, retrying in 5 seconds")
        time.sleep(5)

class Device:
	"""
		Device Class for Alfr3d Users' devices
	"""
	name = 'unknown'
	IP = '0.0.0.0'
	MAC = '00:00:00:00:00:00'
	state = 'offline'
	last_online = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	environment = socket.gethostname()
	user = 'unknown'
	deviceType = 'guest'

	# mandatory to pass MAC for robustness
	def create(self, mac):
		"""
			Description:
				Add new device to the database with default parameters
		"""		
		logger.info("Creating a new device")
		db = pymysql.connect(host=DATABASE_URL, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from device WHERE MAC = %s", (mac,))
		data = cursor.fetchone()

		if data:
			logger.warn("device already exists.... aborting")
			db.close()
			return False

		logger.info("Creating a new DB entry for device with MAC: "+mac)
		try:
			cursor.execute("SELECT * from states WHERE state = %s", (self.state,))
			devstate = cursor.fetchone()[0]
			cursor.execute("SELECT * from device_types WHERE type = %s", (self.deviceType,))
			devtype = cursor.fetchone()[0]
			cursor.execute("SELECT * from user WHERE username = %s", (self.user,))
			usrid = cursor.fetchone()[0]
			cursor.execute("SELECT * from environment WHERE name = %s", (self.environment,))
			envid = cursor.fetchone()[0]
			cursor.execute("INSERT INTO device(name, IP, MAC, last_online, state, device_type, user_id, environment_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (self.name, self.IP, self.MAC, self.last_online, devstate, devtype, usrid, envid))
			db.commit()
		except Exception as e:
			logger.error("Failed to create a new entry in the database")
			logger.error("Traceback: "+str(e))
			db.rollback()
			db.close()
			return False

		db.close()
		producer.send("speak", b"A new device was added to the database")
		return True

	def get(self,mac):
		"""
			Description:
				Find device from DB by MAC
		"""				
		logger.info("Looking for device with MAC: " + mac)
		db = pymysql.connect(host=DATABASE_URL, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from device WHERE MAC = %s", (mac,))
		data = cursor.fetchone()

		if not data:
			logger.warning("Failed to find a device with MAC: " +mac+ " in the database")
			db.close()
			return False

		logger.info("Device found")
		logger.info(data)
		print(data)		#DEBUG

		self.name = data[1]
		self.IP = data[2]
		self.MAC = data[3]
		self.state = data[4]
		self.last_online = data[5]
		self.deviceType = data[6]
		self.user = data[7]
		self.environment = data[8]

		db.close()
		return True

	# update entire object in DB with latest values
	def update(self):
		"""
			Description:
				Update a Device in DB
		"""				
		logger.info("Updating device")
		db = pymysql.connect(host=DATABASE_URL, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from device WHERE MAC = %s", (self.MAC,))
		data = cursor.fetchone()

		if not data:
			logger.warn("Failed to find a device with MAC: " +self.MAC+ " in the database")
			db.close()
			return False

		logger.info("Device found")
		logger.info(data)

		try:
			cursor.execute("SELECT * from states WHERE state = %s", ("online",))
			data = cursor.fetchone()
			stateid = data[0]
			cursor.execute("SELECT * from environment WHERE name = %s", (socket.gethostname(),))
			data = cursor.fetchone()
			envid = data[0]
			cursor.execute("UPDATE device SET name = %s, IP = %s, last_online = %s, state = %s, environment_id = %s WHERE MAC = %s", (self.name, self.IP, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), stateid, envid, self.MAC))

			db.commit()
		except Exception as e:
			logger.error("Failed to update the database")
			logger.error("Traceback: "+str(e))
			db.rollback()
			db.close()
			return False

		db.close()
		logger.info("Updated device with MAC: " + self.MAC)
		return True

	# update entire object in DB with latest values
	def delete(self):
		"""
			Description:
				Delete a Device from DB
		"""				
		logger.info("Deleting device")
		db = pymysql.connect(host=DATABASE_URL, user=DATABASE_USER, password=DATABASE_PSWD, database=DATABASE_NAME)
		cursor = db.cursor()
		cursor.execute("SELECT * from device WHERE MAC = %s", (self.MAC,))
		data = cursor.fetchone()

		if not data:
			logger.warn("Failed to find a device with MAC: " +self.MAC+ " in the database")
			db.close()
			return False

		logger.info("Device found")
		#logger.info(data)

		try:
			cursor.execute("DELETE from device WHERE MAC = %s", (self.MAC,))
			db.commit()
		except Exception as e:
			logger.error("Failed to update the database")
			logger.error("Traceback: "+str(e))
			db.rollback()
			db.close()
			return False

		db.close()
		logger.info("Deleted device with MAC: " + self.MAC)
		return True		

def checkLAN():
	"""
		Description:
			This function checks who is on LAN
	"""
	logger.info("Checking localnet for online devices")

	# temporary file for storing results of network scan
	netclientsfile = os.path.join(os.path.join(os.getcwd(),os.path.dirname(__file__)),'netclients.tmp')	

	# find out which devices are online
	os.system("arp-scan --localnet > "+ netclientsfile)  # Removed sudo, assuming container runs as root or privileged

	netClients = open(netclientsfile, 'r')
	netClientsMACs = []
	netClientsIPs = []

	# parse MAC and IP addresses
	for line in netClients:
		print(line)
		if line.startswith("192.")==False and \
			line.startswith("10.")==False:
			continue
		ret = line.split('\t')
		# parse MAC addresses from arp-scan run
		netClientsMACs.append(ret[1])
		# parse IP addresses from arp-scan run
		netClientsIPs.append(ret[0])	

	# clean up and parse MAC&IP info
	netClients2 = {}
	for i in range(len(netClientsMACs)):
		netClients2[netClientsMACs[i]] = netClientsIPs[i]	

	# find who is online and
	# update DB status and last_online time
	for member in netClientsMACs:
		print(member)
		device = Device()
		exists = device.get(member)

		# try to find out device name
		try:
			name = socket.gethostbyaddr(netClients2[member])[0]
			if name == "_gateway":
				name = None
		except socket.herror:
			logger.error("Couldn't resolve hostname for device with MAC: "+member)
			name = None
		except Exception as e:
			logger.error("Failed to find out hostname")
			logger.error("Traceback: "+str(e))	

		# if device exists in the DB update it
		if exists:
			logger.info("Updating device with MAC: "+member)
			device.IP = netClients2[member]
			device.update()

		# otherwise, create and add it.
		else:
			logger.info("Creating a new DB entry for device with MAC: "+member)
			device.IP = netClients2[member]
			device.MAC = member
			if name:
				device.name = name
			device.create(member)

	logger.info("Cleaning up temporary files")
	os.system('rm -rf '+netclientsfile)

	producer.send("user", b"refresh-all")

if __name__ == '__main__':
	# get all instructions from Kafka
	# topic: device
	logger.info("Starting Alfr3d's device service")
	consumer = None
	while consumer is None:
		try:
			consumer = KafkaConsumer('device', bootstrap_servers=KAFKA_URL)
			logger.info("Connected to Kafka device topic")
		except Exception as e:
			logger.error("Failed to connect to Kafka device topic, retrying in 5 seconds")
			time.sleep(5)

	while True:
		for message in consumer:
			if message.value.decode('ascii') == "alfr3d-device.exit":
				logger.info("Received exit request. Stopping service.")
				sys.exit(1)
			if message.value.decode('ascii') == "scan net":
				checkLAN()

			time.sleep(10)