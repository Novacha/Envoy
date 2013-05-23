import logging, json, oursql, os

from component import Component

def get_relative_path(path):
	my_path = os.path.dirname(os.path.abspath(__file__))
	return os.path.normpath(os.path.join(my_path, path))

class EnvoyComponent(Component):
	def __init__(self, jid, host, port, password):
		Component.__init__(self, jid, host, port, password)
		
		# Hook events
		self.register_event("login", self.on_login)
		self.register_event("logout", self.on_logout)
		self.register_event("ping", self.on_ping)
		self.register_event("status", self.on_status)
		self.register_event("join", self.on_join)
		self.register_event("leave", self.on_leave)
		self.register_event("group_message", self.on_group_message)
		self.register_event("private_message", self.on_private_message)
		self.register_event("topic_change", self.on_topic_change)
		
		# Hook XEP-0045 presence tracking to use the Envoy database
		self['xep_0045'].api.register(self._envoy_is_joined_room, 'is_joined_room')
		self['xep_0045'].api.register(self._envoy_get_joined_rooms, 'get_joined_rooms')
		self['xep_0045'].api.register(self._envoy_add_joined_room, 'add_joined_room')
		self['xep_0045'].api.register(self._envoy_del_joined_room, 'del_joined_room')
		
	def on_login(self, user):
		print "%s just logged in." % user

	def on_logout(self, user, reason):
		print "%s just disconnected with reason '%s'." % (user, reason)

	def on_ping(self, user):
		print "%s just pinged." % user

	def on_status(self, user, status, message):
		print "%s just changed their status to %s (%s)." % (user, status, message)

	def on_join(self, user, room):
		print "%s joined %s." % (user, room)

	def on_leave(self, user, room):
		print "%s left %s." % (user, room)
		
	def on_group_message(self, user, room, body):
		print "%s sent channel message to %s: '%s'" % (user, room, body)
		
	def on_private_message(self, sender, recipient, body):
		print "%s sent private message to %s: '%s'" % (sender, recipient, body)
		
	def on_topic_change(self, user, room, topic):
		print "%s changed topic for %s to '%s'" % (user, room, topic)
	
	# Envoy uses override methods for the user presence tracking feature in
	# the XEP-0045 plugin. Instead of storing the presences in memory, they
	# are stored in the Envoy database. This way, user presences are preserved 
	# across component restarts, thereby preventing inaccurate log entries.
	# Override methods are registered using SleekXMPPs API registry.
	
	def _envoy_is_joined_room(self, jid, node, ifrom, data):
		# Override for the _is_joined_room method.
		# Checks whether a JID was already present in a room.
		query = "SELECT COUNT(*) FROM presences WHERE `UserJid` = ? AND `RoomJid` = ?"
		cursor = db.cursor()
		cursor.execute(query, (str(jid), str(node)))
		return (cursor.fetchone()[0] > 0)
	
	def _envoy_get_joined_rooms(self, jid, node, ifrom, data):
		# Override for the _get_joined_rooms method.
		# Retrieves a list of all rooms a JID is present in.
		query = "SELECT * FROM presences WHERE `UserJid` = ?"
		cursor = db.cursor()
		cursor.execute(query, (str(jid)))
		return set([row[2] for row in cursor])
		
	def _envoy_add_joined_room(self, jid, node, ifrom, data):
		# Override for the _add_joined_room method.
		# Registers a JID presence in a room.
		query = "INSERT INTO presences (`UserJid`, `RoomJid`) VALUES (?, ?)"
		cursor = db.cursor()
		cursor.execute(query, (str(jid), str(node)))
		
	def _envoy_del_joined_room(self, jid, node, ifrom, data):
		# Override for the _del_joined_room method.
		# Removes a JID presence in a room.
		query = "DELETE FROM presences WHERE `UserJid` = ? AND `RoomJid` = ?"
		cursor = db.cursor()
		cursor.execute(query, (str(jid), str(node)))


logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')

configuration = json.load(open(get_relative_path("../config.json"), "r"))

db = oursql.connect(host=configuration['database']['hostname'], user=configuration['database']['username'], 
                    passwd=configuration['database']['password'], db=configuration['database']['database'],
                    autoreconnect=True)

xmpp = EnvoyComponent("component.envoy.local", "envoy.local", 5347, "password")
xmpp.connect()
xmpp.process(block=True)
