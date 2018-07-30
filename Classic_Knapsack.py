from random import randint, getrandbits
import time

'''Расширенный алгоритм Евклида'''
def gcdex(a, b):
    if b == 0:
        return a, 1, 0
    else:
        d, x, y = gcdex(b, a % b)
        return d, y, x - y * (a // b)

def Sym_to_bin(sym, length):
    symbol = list(map(int, bin(ord(sym)[2:].zfill(length))))
    return symbol

def Bin_to_sym(bin):
    bin.reverse()
    sym = '0b' + ''.join(list(map(str, bin)))
    return chr(int(sym, 2))

'''
Класс рюкзачной криптосистемы
'''
class Knapsack:
    def __init__(self, n):
        #n = length_of_symbol
        self.b = list()
        self.b.append(getrandbits(n))
        for i in range(1, n):
            self.b.append(sum(self.b) + getrandbits(n))

        self.m = randint(sum(self.b) + 1, sum(self.b) + getrandbits(n))

        self.w = randint(1, self.m - 1)
        while gcdex(self.w, self.m)[0] != 1:
            self.w = randint(1, self.m - 1)

        self.alpha = list()
        for i in range(n):
            self.alpha.append((self.w * self.b[i]) % self.m)

    def Encrypt(self, m):
        return sum([(self.alpha[i] * m[i]) for i in range(len(self.alpha))])

    def Decrypt(self, C):
        H = gcdex(self.w, self.m)[1] * C % self.m
        Z = list()
        for i in range(len(self.b) - 1, -1, -1): #Решается проблема рюкзака
            if H >= self.b[i] and H != 0:
                H -= self.b[i]
                Z.append(1)
            else:
                Z.append(0)
        return Z

if __name__ == '__main__':
    encode = 'utf-16'
    text = open('text.txt', 'rt', encoding=encode)
    crypt = open('Crypt.txt', 'wt', encoding=encode)
    decrypt = open('Decrypt.txt', 'wt', encoding=encode)
    length_of_symbol = 16
    mashine = Knapsack(length_of_symbol)

    time_to_encrypt = 0
    time_to_decrypt = 0

    for line in text.readlines():
        for symbol in line:
            symbol = Sym_to_bin(symbol, length_of_symbol)
            start = time.time()
            enc_symbol = mashine.Encrypt(symbol)
            time_to_encrypt += time.time() - start
            crypt.write(str(hex(enc_symbol)))
    crypt.close()

    crypt = open('Crypt.txt', 'rt', encoding=encode)
    cry = crypt.read().split('0x')
    cry.pop(0)
    for i in cry:
        i = int(i, 16)
        start = time.time()
        dec_symbol = mashine.Decrypt(i)
        time_to_decrypt += time.time() - start
        decrypt.write(Bin_to_sym(dec_symbol))

    print("---Encrypt for %s seconds---" % time_to_encrypt)
    print("---Decrypt for %s seconds---" % time_to_decrypt)
    decrypt.write('\n\n---Classic Knapsack---')
    #decrypt.write('\n---Length of key %s bits---' % length_of_key)
    decrypt.write("\n---Encrypt for %s seconds---" % time_to_encrypt)
    decrypt.write("\n---Decrypt for %s seconds---" % time_to_decrypt)
    crypt.close()
    decrypt.close()
