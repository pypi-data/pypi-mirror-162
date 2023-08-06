This packages takes an input of plain text and converts into n-bit binary, representing 
a digital logic high as the capitalised charater of the word of choice. For example, the text
<'A'> is represented as 01000001 in 8 bit binary, given the encryption word is <'beans'> the final
encrypted text would look as follows: bEansbeA. 

The function is named 'Beanory' and takes a miniumum of 2 arguments:

plain_text <str>: the string that will be encrypted 
word <str>: the word that will replaces the 0s and 1s

There are two other non-postional arguments:

encrypt <bool> default - <True>: True toggles encrytpion, False toggles decryption
bit_length <int> default - <8> : bit length of each byte