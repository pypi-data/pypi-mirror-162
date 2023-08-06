def BIN_to_BEAN(_bin_: str, word, remainder=None, bit_length=8) -> str:
    bean_text = ''
    beans = word*(len(_bin_)//len(word)+((len(_bin_)%5)!=0)*1)

    if remainder != None:
        beans = word[-remainder:]

    
    for i, bit in enumerate(_bin_):
        if int(bit):
            bean_text += beans[i].upper()
        else:
            bean_text += beans[i]

    return bean_text
        

def beanory(plain_text: str, word, encrypt=True, bit_length=8) -> str:
    word_len = len(word)

    if encrypt:
        bean_text = ''
        bin_8bit = ''

        for letter in plain_text:
            if ord(letter)> 2**bit_length-1:
                raise Exception(f'Character <{letter}> cannot be represented using {bit_length} bits')
            
            bin_unk = str(bin(ord(letter)))[2:]
            bin_8bit += (bit_length-len(bin_unk))*'0'+bin_unk
        
        bean_text = BIN_to_BEAN(bin_8bit, word, bit_length=bit_length)
        
        if len(bean_text)%word_len != 0:
            _remainder_=word_len-(len(bean_text)%word_len)
            remainder_bin_unk = str(bin(_remainder_))[2:]
            remainder_bin_kwn_unk = (_remainder_-len(remainder_bin_unk))*'0'+remainder_bin_unk
            bean_rem = BIN_to_BEAN(remainder_bin_kwn_unk, word, remainder=_remainder_, bit_length=bit_length)
        else:
            bean_rem = ''
        
        return bean_text + bean_rem
    
    else:
        if len(plain_text)%bit_length != 0:
            filtered_plain_text = plain_text[:-(len(plain_text)%bit_length)]
        else:
            filtered_plain_text = plain_text

        plain_text_bin_8bit = ''

        decoded = ''
        for i in range(len(filtered_plain_text)):
            if filtered_plain_text[i] == filtered_plain_text[i].lower():
                plain_text_bin_8bit += '0'
            else:
                plain_text_bin_8bit += '1'


        for i in range(0, len(plain_text_bin_8bit), bit_length):
            ordinal = int(plain_text_bin_8bit[i:i+bit_length], 2)
            decoded += chr(ordinal)

        return decoded

t = beanory('He', 'beans', encrypt=True, bit_length=8)
print(len(t))


