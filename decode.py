import base64
from algosdk import encoding
str="TVniUXEnzIkLjC8q/Uq2YJZw3ncEonY9HLA8qcACEwY="
decoded_string = base64.b64decode(str)
d=encoding.encode_address(decoded_string)
print(d)
print(base64.b64encode(encoding.decode_address("JVM6EULRE7GISC4MF4VP2SVWMCLHBXTXASRHMPI4WA6KTQACCMDKDWAM5U")))