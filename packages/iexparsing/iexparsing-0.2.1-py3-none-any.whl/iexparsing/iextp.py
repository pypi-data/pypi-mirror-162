from functools import partial
import io
import math
import struct

"""
The supported IEX-TP versions
"""
SUPPORTED_VERSIONS = ['1.25']

_Session__HEADER_FORMAT = '<BxHIIHHqqq'
_Session__HEADER_LENGTH = struct.calcsize(_Session__HEADER_FORMAT)
_Session__MESSAGE_BLOCK_HEADER_FORMAT = '<H'
_Session__MESSAGE_BLOCK_HEADER_LENGTH = struct.calcsize(_Session__MESSAGE_BLOCK_HEADER_FORMAT)

class OutboundSegment:
	"""
    A group of higher-level messages

    Attributes
    ----------
    messages
        a list of messages, by order
    messages_protocol_id : int
    	a no. declaring the higher-level messages protocol (e.g. DEEP or TOPS)
    past : bool
    	was the packet received after later packets were already processed, i.e., out of order
    """

	def __init__(self, messages, messages_protocol_id: int, past: bool=False):
		self.messages = messages
		self.messages_protocol_id = messages_protocol_id
		self.past = past

	def __str__(self) -> str:
		return f'IEX-TP outbound segment: {self.messages}'

class Session:
	"""
	An IEX-TP packets parser

	A session tracks the validity and order of multiple packets.
	"""

	def __init__(self):
		self.session_id = None
		self.latest_timestamp = -math.inf

	def decode_packet(self, contents: bytes) -> OutboundSegment:
		"""
		Decodes an outbound segment

		Parameters
		----------
		contents : bytes
			the raw packet data, e.g., the body of a TCP or UDP packet
		"""

		# Seperate the buffer to fields.
		header = struct.unpack(__HEADER_FORMAT, contents[:__HEADER_LENGTH])
		payload = contents[__HEADER_LENGTH:]

		# Verify the IEXTP version.
		assert header[0] == 0x1

		# Derive the message protocol
		messages_protocol_id = header[1]

		# Verify that the session is constant.
		if self.session_id:
			assert self.session_id == header[3]
		else:
			self.session_id = header[3]

		# Check if the packet was received out of order.
		past = header[8] < self.latest_timestamp

		if not past:
			self.latest_timestamp = header[8]

		# Parse the message blocks.
		assert header[4] == len(payload)
		payload = io.BytesIO(payload)

		messages = []
		for message_block_header in iter(partial(payload.read, __MESSAGE_BLOCK_HEADER_LENGTH), b''):
			message_len = struct.unpack(__MESSAGE_BLOCK_HEADER_FORMAT, message_block_header)[0]
			messages.append(payload.read(message_len))

		assert len(messages) == header[5]

		return OutboundSegment(messages, messages_protocol_id, past)