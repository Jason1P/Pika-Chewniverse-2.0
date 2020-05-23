"""
System for automatically broadcasting object creation, destruction and data updates to connected players.
See RakNet's ReplicaManager.
"""

import logging
from typing import Dict, Iterable, Set

from bitstream import c_bit, c_ubyte, c_ushort, WriteStream

from .messages import Message
from .server import Server
from .transports.abc import *
from uuid import uuid3, NAMESPACE_DNS
from event_dispatcher import EventDispatcher
import Logger
from GameMessages.Outgoing import *

log = logging.getLogger(__name__)


class Replica:
	def __init__(self):
		self.important = False
	"""Abstract base class for replicas (objects serialized using the replica manager system)."""

	def write_construction(self, stream: WriteStream) -> None:
		"""
		This is where the object should write data to be sent on construction.
		"""
		raise NotImplementedError

	def serialize(self, stream: WriteStream) -> None:
		"""
		This is where the object should write data to be sent on serialization.
		"""
		raise NotImplementedError

	def on_destruction(self) -> None:
		"""
		This will be called by the ReplicaManager before the destruction message is sent.
		"""

class ReplicaManager:
	"""
	Handles broadcasting updates of objects to connected players.
	"""

	def __init__(self, dispatcher: EventDispatcher):
		self._dispatcher = dispatcher
		self._dispatcher.add_listener(ConnectionEvent.Close, self._on_conn_close)
		self._participants: Set[Connection] = set()
		self._network_ids: Dict[Replica, int] = {}
		self._current_network_id = 0

	def add_participant(self, server, conn: Connection) -> None:
		string = " added connection: " + str(conn.get_address()[0])
		Logger.log(Logger.LOGGINGLEVEL.REPLICADEBUG, string)
		"""
		Add a participant to which object updates will be broadcast to.
		Updates won't automatically be sent to all connected players, just the ones added via this method.
		Disconnected players will automatically be removed from the list when they disconnect.
		Newly added players will receive construction messages for all objects are currently registered with the manager (construct has been called and destruct hasn't been called yet).
		"""
		self._participants.add(conn)

		important_not_sent = True

		for obj in self._network_ids:
			if obj.important:
				self._construct(obj, new=False, recipients=[conn])
				print("Sent player")

		address = (str(conn.get_address()[0]), int(conn.get_address()[1]))
		uid = str(uuid3(NAMESPACE_DNS, str(address)))
		session = server.get_session(uid)
		obj_load = ServerDoneLoadingAllObjects.ServerDoneLoadingAllObjects(objid=int(session.current_character.object_id), message_id=0x66a)
		conn.send(obj_load, reliability=Reliability.ReliableOrdered)
		player_ready = PlayerReady.PlayerReady(objid=int(session.current_character.object_id), message_id=0x1fd)
		conn.send(player_ready, reliability=Reliability.ReliableOrdered)

		for obj in self._network_ids:
			if obj.important is not True:
				self._construct(obj, new=False, recipients=[conn])
				print("sent object")

	def construct(self, obj: Replica, new: bool=True, important: bool=False) -> None:
		"""
		Send a construction message to participants.

		The object is registered and participants joining later will also receive a construction message when they join (if the object hasn't been destructed in the meantime).
		The actual content of the construction message is determined by the object's write_construction method.
		"""
		self._construct(obj, new, important)

	def _construct(self, obj: Replica, new: bool=True, important: bool=False, recipients: Iterable[Connection]=None) -> None:
		# recipients is needed to send replicas to new participants
		if recipients is None:
			recipients = self._participants

		if new:
			self._network_ids[obj] = self._current_network_id
			self._current_network_id += 1

		out = WriteStream()
		out.write(c_ubyte(Message.ReplicaManagerConstruction.value))
		out.write(c_bit(True))
		out.write(c_ushort(self._network_ids[obj]))
		obj.write_construction(out)

		out = bytes(out)
		for conn in recipients:
			conn.send(out)

	def serialize(self, obj: Replica, reliability = None) -> None:
		"""
		Send a serialization message to participants.

		The actual content of the serialization message is determined by the object's serialize method.
		Note that the manager does not automatically send a serialization message when some part of your object changes - you have to call this function explicitly.
		"""
		out = WriteStream()
		out.write(c_ubyte(Message.ReplicaManagerSerialize.value))
		out.write(c_ushort(self._network_ids[obj]))
		obj.serialize(out)

		out = bytes(out)
		for conn in self._participants:
			if reliability is not None:
				conn.send(out, reliability=reliability)
			else:
				conn.send(out)

	def destruct(self, obj: Replica, reliability = None) -> None:
		"""
		Send a destruction message to participants.

		Before the message is actually sent, the object's on_destruction method is called.
		This message also deregisters the object from the manager so that it won't be broadcast afterwards.
		"""
		log.debug("destructing %s", obj)
		obj.on_destruction()
		out = WriteStream()
		out.write(c_ubyte(Message.ReplicaManagerDestruction.value))
		out.write(c_ushort(self._network_ids[obj]))

		out = bytes(out)
		for conn in self._participants:
			if reliability is not None:
				conn.send(out, reliability=reliability)
			else:
				conn.send(out)

		del self._network_ids[obj]

	def _on_conn_close(self, conn: Connection) -> None:
		self._participants.discard(conn)
