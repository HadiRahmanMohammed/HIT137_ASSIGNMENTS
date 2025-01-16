# for the encryption
def encrypt(raw, n, m):
    encrypted = ''
    for c in raw:
        if c >= 'a' and c <= 'm': # for the small letter number
            encrypted += chr((ord(c) - ord('a') + (n * m)) % 13 + ord('a'))
        elif c >= 'n' and c <= 'z':
            encrypted += chr((ord(c) - ord('n') - (n + m)) % 13 + ord('n'))
        elif c >= 'A' and c <= 'M':  # for the big letter number
            encrypted += chr((ord(c) - ord('A') - (n)) % 13 + ord('A'))
        elif c >= 'N' and c <= 'Z':
            encrypted += chr((ord(c) - ord('N') + (m ** 2)) % 13 + ord('N'))
        else:  
            encrypted += c   # for the non alphabetical characters
    return encrypted 

# for the decryption
def decrypt(encrypted, n,m):
    decrypted = ''
    for c in encrypted:
        if c >= 'a' and c <= 'm': # for the small letter number
            decrypted += chr((ord(c) - ord('a') - (n * m)) % 13 + ord('a'))
        elif c >= 'n' and c <= 'z':
            decrypted += chr((ord(c) - ord('n') + (n * m)) % 13 + ord('n'))
        elif c >= 'A' and c <= 'M': # for the big letter number
            decrypted += chr((ord(c) - ord('A') + (n) % 13 + ord('A')))
        elif c >= 'N' and c <= 'Z':
            decrypted += chr((ord(c) - ord('N') - (m ** 2)) % 13 + ord ('N'))
        else :   
            decrypted += c  # for the non alphabetical characters
    return decrypted 

def verify(raw, decrypted):
    return raw == decrypted

# for the input of n and m for user
n = int(input("Enter the integer n: "))
m = int(input("Enter the integer m: "))


# for reading raw text inside the file
with open('raw_text.txt', encoding = 'utf-8') as f:
    raw_text = f.read()


# for encrypt the text 

encrypted_text = encrypt(raw_text, n, m)
with open('encrypted_text.txt', 'w', encodings = 'utf-8') as f:
    f.write(encrypted_text)

# for decrypt the text

decrypted_text = decrypt(encrypted_text, n, m)

# to verify the corectness
correct = verify(raw_text, decrypted_text)
print("Decryption Is Correct:", correct)

print("Decrypted Text:")
print(decrypted_text) 
