TAB = '\t'
BACK = '\x08'
ENTER = '\r'
DELETE = '\x7f'
ESCAPE = '\x1b'
PASTE = '\x16'
COPY = '\x03'
SPACE = ' '

lowercase_alphabet = {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'}
'''The lowercase latin alphabet'''
uppercase_alphabet = {'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'}
'''The lowercase latin alphabet'''
alphabet = lowercase_alphabet.union(uppercase_alphabet)
numbers = {'1','2','3','4','5','6','7','8','9','0','.'}
'''Numbers 1-9 including "." '''
symbols = {',','`','~','!','@','#','$','%','^','&','*','(',')','_','+','-','=','{','}','[',']','|','\\',';',':','"','<','>','.','?','/','`',"'"}
filename_valid = alphabet.union(numbers, symbols, {" ",}).difference({'<','>','|','/','\\','*',':','?','"'}) 
'''File name accepted characters'''
