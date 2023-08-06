from datetime import datetime
from deprecation import deprecated
import struct
import typing

"""
The supported TOPS versions
"""
SUPPORTED_VERSIONS = ['1.5', '1.6']

"""
The message protocol id. for IEX-TP
"""
MESSAGE_PROTOCOL_ID = 0x8003

class QuoteUpdate:
    """
    A top-quotes update message

    Attributes
    ----------
    symbol : str
        the stock ticker (e.g. 'AAPL')
    time : datetime.datetime
        the time of the update with nanoseconds precision
    bid_price : float
        best quoted bid price in USD
    bid_size : int
        aggregate quoted best bid size
    ask_price : float
        best quoted ask price in USD
    ask_size : int
        aggregate quoted best ask size
    """

    def __init__(
        self,
        symbol: str,
        time: datetime,
        bid_price: float,
        bid_size: int,
        ask_price: float,
        ask_size: int
    ):
        self.symbol = symbol
        self.time = time
        self.bid_price = bid_price
        self.bid_size = bid_size
        self.ask_price = ask_price
        self.ask_size = ask_size

    def __str__(self) -> str:
        return f'best bid: {self.bid_size} {self.symbol} shares for {self.bid_price} USD; best ask: {self.ask_size} ones for {self.ask_price} USD @ {self.time}'

class TradeReport:
    """
    A trade report

    Attributes
    ----------
    symbol : str
        the stock ticker (e.g. 'AAPL')
    time : datetime.datetime
        the time of the trade with nanoseconds precision
    price : float
        the trade execution price in USD
    size : int
        the no. of shares
    """

    def __init__(
        self,
        symbol: str,
        time: datetime,
        price: float,
        size: int
    ):
        self.symbol = symbol
        self.time = time
        self.price = price
        self.size = size
    
    def __str__(self) -> str:
        return f'trade: {self.size} {self.symbol} shares for {self.price} USD @ {self.time}'

class Session:
    """
    An TOPS messages parser

    A session tracks the validity and order of multiple messages.
    """

    def decode_message(self, contents: bytes) -> typing.Union[QuoteUpdate,TradeReport]:
        """
        Decodes a TOPS message

        Parameters
        ----------
        contents : bytes
            the raw message, e.g., an IEX-TP message
        """
        match contents[0]:
            case 0x51:
                # Seperate the buffer to fields.
                data = struct.unpack('<bBq8sIQQI', contents)

                symbol = data[3].rstrip().decode()
                time = datetime.utcfromtimestamp(data[2] / 1E9)
                # The price is stored as a fixed-point no.
                bid_price, ask_price = data[5] / 1E4, data[6] / 1E4
                bid_size, ask_size = data[4], data[7]

                return QuoteUpdate(symbol, time, bid_price, bid_size, ask_price, ask_size)
            
            case 0x54:
                # Seperate the buffer to fields.
                data = struct.unpack('<bBq8sIQq', contents)
                
                symbol = data[3].rstrip().decode()
                time = datetime.utcfromtimestamp(data[2] / 1E9)
                # The price is stored as a fixed-point no.
                price = data[5] / 1E4
                size = data[4]

                return TradeReport(symbol, time, price, size)
            
            case 0x53 | 0x44 | 0x48 | 0x49 | 0x4F | 0x50 | 0x58 | 0x42 | 0x41:
                pass
            
            case message_type:
                raise ValueError(f'Unknown message type: {hex(message_type)}, is the TOPS versions supported?')

@deprecated(deprecated_in='0.2.0', removed_in='0.3.0', details='Use Session.decode_message instead.')
def decode_message(contents: bytes) -> typing.Union[QuoteUpdate,TradeReport]:
    sess = Session()
    return sess.decode_message(contents)