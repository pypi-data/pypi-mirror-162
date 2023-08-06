def BIN_to_BEAN(_bin_: str, encryption_key, remainder=None, bit_length=8) -> str:
    bean_text = ''
    beans = encryption_key*(len(_bin_)//len(encryption_key)+((len(_bin_)%5)!=0)*1)

    if remainder != None:
        beans = encryption_key[-remainder:]

    
    for i, bit in enumerate(_bin_):
        if int(bit):
            bean_text += beans[i].upper()
        else:
            bean_text += beans[i]

    return bean_text