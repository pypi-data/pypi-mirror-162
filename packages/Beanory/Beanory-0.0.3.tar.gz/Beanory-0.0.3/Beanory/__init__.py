from BIN_to_BEAN import BIN_to_BEAN
        
def beanory(plain_text: str, encryption_key: str, encrypt=True, bit_length=8) -> str:
    if ' ' == encryption_key:
        ex = f'<{encryption_key}> is an invalid encrytion key.'
        raise Exception(ex)
    elif ' ' in encryption_key:
        ex = f'Encrytion key cannot contain any spaces.'
        raise Exception(ex)
    else:
        for char in encryption_key:
            if char == char.upper():
                print('Encryption keyword cannot contain any capital letters')
                while True:
                    ans = input(f'Would you like to use <{encryption_key.lower()}> instead? - <y/n> ')
                    if ans in ('Y', 'y'):
                        encryption_key = encryption_key.lower()
                        break
                    elif ans in ('N', 'n'):
                        return
                break



    encryption_key_len = len(encryption_key)

    if encrypt:
        bean_text = ''
        bin_nbit = ''

        for letter in plain_text:
            if ord(letter)> 2**bit_length-1:
                ex = f'Character <{letter}> cannot be represented using {bit_length} bits'
                raise Exception(ex)
            
            bin_unk = str(bin(ord(letter)))[2:]
            bin_nbit += (bit_length-len(bin_unk))*'0'+bin_unk
        
        bean_text = BIN_to_BEAN(bin_nbit, encryption_key, bit_length=bit_length)
        
        if len(bean_text)%encryption_key_len != 0:
            _remainder_=encryption_key_len-(len(bean_text)%encryption_key_len)
            remainder_bin_unk = str(bin(_remainder_))[2:]
            remainder_bin_kwn_unk = (_remainder_-len(remainder_bin_unk))*'0'+remainder_bin_unk
            bean_rem = BIN_to_BEAN(remainder_bin_kwn_unk, encryption_key, remainder=_remainder_, bit_length=bit_length)
        else:
            bean_rem = ''
        
        return bean_text + bean_rem
    
    else:
        encrypted_text = plain_text 

        if len(encrypted_text)%bit_length != 0:
            filtered_encrypted_text = encrypted_text[:-(len(encrypted_text)%bit_length)]
        else:
            filtered_encrypted_text = encrypted_text

        encrypted_text_bin_nbit = ''

        plain_text = ''
        for i in range(len(filtered_encrypted_text)):
            if filtered_encrypted_text[i] == filtered_encrypted_text[i].lower():
                encrypted_text_bin_nbit += '0'
            else:
                encrypted_text_bin_nbit += '1'


        for i in range(0, len(encrypted_text_bin_nbit), bit_length):
            ordinal = int(encrypted_text_bin_nbit[i:i+bit_length], 2)
            plain_text += chr(ordinal)

        return plain_text
