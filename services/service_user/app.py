# Modified for containerization: logging to stdout instead of file
import os
import sys
import time
import logging
import socket
import json
import pymysql  # Changed from MySQLdb to pymysql
from kafka import KafkaConsumer,KafkaProducer
from datetime import datetime, timedelta

# current path from which python is executed
CURRENT_PATH = os.path.dirname(__file__)

# set up logging
logger = logging.getLogger("UsersLog")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# Changed to stream handler for container logging
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

MYSQL_DATABASE_URL     = os.environ['MYSQL_DATABASE_URL']
MYSQL_DATABASE     = os.environ['MYSQL_DATABASE']
MYSQL_USER     = os.environ['MYSQL_USER']
MYSQL_PASSWORD     = os.environ['MYSQL_PASSWORD']
KAFKA_URL         = os.environ['KAFKA_BOOTSTRAP_SERVERS']
ALFR3D_ENV_NAME   = os.environ.get('ALFR3D_ENV_NAME', 'test')

producer = None
while producer is None:
    try:
        print("Connecting to Kafka at: "+KAFKA_URL)
        producer = KafkaProducer(bootstrap_servers=[KAFKA_URL])
        logger.info("Connected to Kafka")
    except Exception as e:
        logger.error("Failed to connect to Kafka, retrying in 5 seconds")
        time.sleep(5)

class User:
    """
        User Class for Alfr3d Users
    """
    name = 'unknown'
    state = 'offline'
    last_online = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    userType = 'guest'

    def create(self):
        logger.info("Creating a new user")
        db = pymysql.connect(host=MYSQL_DATABASE_URL, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
        cursor = db.cursor()
        cursor.execute("SELECT * from user WHERE username = %s", (self.name,))
        data = cursor.fetchone()

        try:
            exists = self.get(self.name)
        except:
            exists = False
        if exists:
            logger.error("User with that name already exists")
            db.close()
            return False

        logger.info("Creating a new DB entry for user: "+self.name)
        try:
            cursor.execute("SELECT * from states WHERE state = %s", ("offline",))
            usrstate = cursor.fetchone()[0]
            cursor.execute("SELECT * from user_types WHERE type = %s", ("guest",))
            usrtype = cursor.fetchone()[0]
            cursor.execute("SELECT * from environment WHERE name = %s", (ALFR3D_ENV_NAME,))
            envid = cursor.fetchone()[0]            
            cursor.execute("INSERT INTO user(username, last_online, state, type, environment_id) VALUES (%s, %s, %s, %s, %s)", (self.name, self.last_online, usrstate, usrtype, envid))
            db.commit()
        except Exception as  e:
            logger.error("Failed to create a new entry in the database")
            logger.error("Traceback: "+str(e))
            db.rollback()
            db.close()
            return False

        db.close()
        producer = KafkaProducer(bootstrap_servers=[KAFKA_URL])
        producer.send("speak", b"A new user has been added to the database")
        return True

    def get(self):
        """
            Description:
                Find a user from DB by name
        """
        logger.info("Looking for user: " + self.name)
        db = pymysql.connect(host=MYSQL_DATABASE_URL, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
        cursor = db.cursor()
        cursor.execute("SELECT * from user WHERE username = %s", (self.name,))
        data = cursor.fetchone()

        if not data:
            logger.warning("Failed to find user with username: " +self.name+ " in the database")
            db.close()
            return False

        #print data
        self.name = data[1]
        self.state = data[5]
        self.last_online = data[6]
        self.userType = data[8]

        db.close()
        return True

    def update(self):
        """
            Description:
                Update a User in DB
        """
        logger.info("Updating user: " + self.name)
        db = pymysql.connect(host=MYSQL_DATABASE_URL, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
        cursor = db.cursor()
        cursor.execute("SELECT * from user WHERE username = %s", (self.name,))
        data = cursor.fetchone()

        if not data:
            logger.warn("Failed to find user with username: " +self.name+ " in the database")
            db.close()
            return False

        logger.info("User found")
        logger.info(data)

        try:
            cursor.execute("UPDATE user SET username = %s WHERE username = %s", (self.name, self.name))
            cursor.execute("UPDATE user SET last_online = %s WHERE username = %s", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.name))
            cursor.execute("SELECT * from states WHERE state = %s", ("online",))
            data = cursor.fetchone()
            stateid = data[0]
            cursor.execute("UPDATE user SET state = %s WHERE username = %s", (stateid, self.name))
            cursor.execute("SELECT * from environment WHERE name = %s", (ALFR3D_ENV_NAME,))
            data = cursor.fetchone()
            envid = data[0]
            cursor.execute("UPDATE user SET environment_id = %s WHERE username = %s", (envid, self.name))

            db.commit()
        except Exception as  e:
            logger.error("Failed to update the database")
            logger.error("Traceback: "+str(e))
            db.rollback()
            db.close()
            return False

        db.close()
        logger.info("Updated user: " + self.name)
        return True
    
    def delete(self):
        """
            Description:
                Delete a User from DB
        """
        logger.info("Deleting a User")
        db = pymysql.connect(host=MYSQL_DATABASE_URL, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
        cursor = db.cursor()
        cursor.execute("SELECT * from user WHERE username = \""+self.name+"\";")
        data = cursor.fetchone()

        if not data:
            logger.warning("Failed to find user with username: " +self.name+ " in the database")
            db.close()
            return False

        logger.info("User found")

        try:
            cursor.execute("DELETE from user WHERE username = \""+self.name+"\";")
            db.commit()
        except Exception as e:
            logger.error("Failed to update the database")
            logger.error("Traceback: "+str(e))
            db.rollback()
            db.close()
            return False

        db.close()
        logger.info("Deleted user with username: " +self.name)
        return True            

# refreshes state and last_online for all users
def refreshAll():
    logger.info("Refreshing users")

    db = pymysql.connect(host=MYSQL_DATABASE_URL, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DATABASE)
    cursor = db.cursor()
    cursor.execute("SELECT * from user;")
    user_data = cursor.fetchall()

    # figure out device types
    dev_types = {}
    cursor.execute("SELECT * FROM device_types;")
    types = cursor.fetchall()
    for type in types:
        dev_types[type[1]]=type[0]

    # figure out states
    stat = {}
    cursor.execute("SELECT * FROM states;")
    states = cursor.fetchall()
    for state in states:
        stat[state[1]]=state[0]

    # figure out environments
    
    cursor.execute("SELECT * FROM environment WHERE name = %s", (ALFR3D_ENV_NAME,))
    env_data = cursor.fetchone()
    if env_data:
        env = env_data[1]
        env_id = env_data[0]

    # get all devices for that user
    for user in user_data:
        logger.info("Refreshing user "+user[1])
        logger.info(user)
        last_online=user[6]

        # get all devices for that user
        try:
            logger.info("Fetching user devices")
            cursor.execute("SELECT d.last_online FROM device d \
                              inner join device_types dt on d.device_type = dt.id \
                            WHERE user_id = "+str(user[0])+" \
                            AND (type = \"guest\" or type = \"resident\");")
            devices = cursor.fetchall()
            for device in devices:
                # update last_online time for that user
                if device[0] and user[6] and device[0] > user[6]:
                    logger.info("Updating user "+user[1])
                    cursor.execute("UPDATE user SET last_online = \""+str(device[0])+"\" WHERE username = \""+user[1]+"\";")
                    cursor.execute("UPDATE user SET environment_id = \""+str(env_id)+"\" WHERE username = \""+user[1]+"\";")
                    db.commit()
                    last_online = device[0]     # most recent online time (user[6] is when user went offline last time)
        except Exception as  e:
            logger.error("Failed to update the database")
            logger.error("Traceback: "+str(e))
            db.rollback()
            continue

        # this time only needs to account for one cycle of alfr3d's standard loop
        # or a few... in case one of them misses it :)
        try:
            time_now = datetime.now()
            if last_online:
                delta = time_now - last_online
            else:
                delta = timedelta(minutes=60)
        except Exception as  e:
            logger.error("Failed to figure out the timedelta")
            delta = timedelta(minutes=60)

        if delta < timedelta(minutes=30):    # 30 minutes
            logger.info("User is online")    #DEBUG
            if user[5] == stat["offline"]:
                logger.info(user[1]+" just came online")
                producer = KafkaProducer(bootstrap_servers=[KAFKA_URL])
                producer.send("speak", bytes(user[1]+" just came online",'utf-8')) ## temp until greeting                
                cursor.execute("UPDATE user SET state = "+str(stat['online'])+" WHERE username = \""+user[1]+"\";")                
                # welcome the user
                cursor.execute("SELECT * FROM user_types where id = %s", (user[8],))
                usr_type = cursor.fetchone()
                #print(usr_type) # DEBUG
                data = {
                    'user':user[1],
                    'type':usr_type[1],
                    'last_online':str(user[6])
                    }
                producer.send("speak",value=json.dumps(data).encode('utf-8'),key=b'welcome')
                #nighttime_auto()    # turn on the lights
                # speak welcome
        else:
            logger.info("User is offline")    #DEBUG
            if user[5] == stat["online"]:
                logger.info(user[1]+" went offline")
                cursor.execute("UPDATE user SET state = "+str(stat['offline'])+" WHERE username = \""+user[1]+"\";")
                cursor.execute("UPDATE device SET state = "+str(stat['offline'])+" WHERE user_id = \""+str(user[0])+"\";")
                #nighttime_auto()            # this is only useful when alfr3d is left all alone

        try:
            db.commit()
        except Exception as  e:
            logger.error("Failed to update the database")
            logger.error("Traceback: "+str(e))
            db.rollback()
            db.close()
            continue

    db.close()
    logger.info("Refreshed all users")
    return True
    
if __name__ == '__main__':
    # get all instructions from Kafka
    # topic: user
    logger.info("Starting Alfr3d's user service")
    consumer = None
    while consumer is None:
        try:
            consumer = KafkaConsumer('user', bootstrap_servers=KAFKA_URL, auto_offset_reset='earliest')
            logger.info("Connected to Kafka user topic")
        except Exception as e:
            logger.error("Failed to connect to Kafka user topic, retrying in 5 seconds")
            time.sleep(5)

    while True:
        for message in consumer:
            if message.value.decode('ascii') == "alfr3d-user.exit":
                logger.info("Received exit request. Stopping service.")
                sys.exit(1)
            if message.value.decode('ascii') == "refresh-all":
                refreshAll()
            if message.key:
                if message.key.decode('ascii') == "create":
                    usr = User()
                    usr.name = message.value.decode('ascii')
                    usr.create()
                if message.key.decode('ascii') == "delete":
                    usr = User()
                    usr.name = message.value.decode('ascii')
                    usr.delete()    

            time.sleep(10)