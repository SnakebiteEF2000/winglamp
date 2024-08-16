_hexdig = '0123456789ABCDEFabcdef'
_hextobyte = None

def unquote(string):
    """unquote('abc%20def') -> 'abc def'."""
    global _hextobyte

    if not string:
        return ''

    if isinstance(string, str):
        string = string.encode('utf-8')

    bits = string.split(b'%')
    if len(bits) == 1:
        return string.decode('utf-8')  # Decode the byte string here

    res = [bits[0].decode('utf-8')]  # Decode each part of the split string
    append = res.append

    if _hextobyte is None:
        _hextobyte = {a+b: bytes([int(a+b, 16)]) for a in _hexdig for b in _hexdig}

    for item in bits[1:]:
        try:
            append(_hextobyte[item[:2]].decode('utf-8'))  # Decode after appending
            append(item[2:].decode('utf-8'))  # Decode the rest of the item
        except KeyError:
            append(b'%')
            append(item)

    return ''.join(res)  # Join the list of strings without needing to decode again
