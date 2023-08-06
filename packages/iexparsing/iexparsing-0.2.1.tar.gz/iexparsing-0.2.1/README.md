# iexparsing
A collection of parsers for [IEX](https://exchange.iex.io/).

Use the parsers to gather relevant quotes and trades information. 

Currently, only IEX-TP and TOPS parsing is supported.

## IEX-TP Parsing Example

```py
from iexparsing import iextp

session = iextp.Session()

outbound_segment = session.decode_packet(b'\x01\x00\xFF\xFF\x01\x00\x00\x00\x00\x00\x87\x42\x07\x00\x02\x00\x8c\xa6\x21\x00\x00\x00\x00\x00\xca\xc3\x00\x00\x00\x00\x00\x00\xec\x45\xc2\x20\x96\x86\x6d\x14\x01\x00\x69\x02\x00\xBE\xEF')
print(outbound_segment)
```

```
IEX-TP outbound segment: [b'i', b'\xbe\xef']
```

You can then pass `outbound_segment.messages` to a messages-protocol parser, e.g. TOPS.

## TOPS Parsing Example

```py
from iexparsing import tops

session = tops.Session()
    
print(session.decode_message(b'\x51\x00\xac\x63\xc0\x20\x96\x86\x6d\x14\x5a\x49\x45\x58\x54\x20\x20\x20\xe4\x25\x00\x00\x24\x1d\x0f\x00\x00\x00\x00\x00\xec\x1d\x0f\x00\x00\x00\x00\x00\xe8\x03\x00\x00'))
```

```
best bid: 9700 ZIEXT shares for 99.05 USD; best ask: 1000 ones for 99.07 USD @ 2016-08-23 19:30:32.572716
```

## TODO

- [x] Make a basic parser
- [x] Write documentation
- [ ] Report errors
- [ ] Add a DEEP parser
- [ ] Parse trading breaks
