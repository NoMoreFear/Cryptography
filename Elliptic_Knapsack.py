from Elliptic_Curve import *
from random import randint, choice, getrandbits
import time

'''ответит почти наверняка простое ли число'''
def isPrime(N):
    if N == 2:
        return True
    for i in range(100):
        n = randint(2, N-2)
        if gcdex(N, n)[0] != 1:
            return False
        if pow(n, N-1, N) != 1: #тест Ферма
            return False
    return True

def Sym_to_bin(sym, length):
    symbol = list(bin(ord(sym)))
    symbol = [int(symbol[i]) for i in range(2, len(symbol))]
    while True:
        if len(symbol) < length:
            symbol.insert(0, 0)
        else:
            return symbol

def Bin_to_sym(bin):
    bin.reverse()
    sym = '0b'
    for i in range(len(bin)):
        sym += str(bin[i])
    return chr(int(sym, 2))

class Ell_Knapsack:
    def __init__(self, length):
        self.length = length  # бит. длинна представления символа
        self.crv = Curve(-3, # a
                    2455155546008943817740293915197451784769108058161191238065, #b
                    6277101735386680763835789423207666416083908700390324961279) # mod prime

        n = 6277101735386680763835789423176059013767194773182842284081 # |E(G)|

        self.P = randint(1, n - 1) * Point(self.crv, #curve
                                                602046282375688656758213480587526111916698976636884684818,    # Gx
                                                174050332293622031404857552280219410364023488927386650641)    # Gy

        #self.k = randint(1, (n - 1) // sum([2**i for i in range(1, self.length)])) # close_key
        self.k = (n - 1) // sum([2**i for i in range(1, self.length)]) + 10
        self.AP = tuple([self.k*pow(2, (i-1))*self.P for i in range(1, self.length + 1)])    # close_key
        #self.AP = tuple([self.P*i for i in self.a]) # open_key
        #self.R = self.P*choice(self.a)  # open_key
        #self.d = randint(2, self.n - 1)     # close_key
        #self.S = self.d * self.R    # open_key

    def Encrypt(self, M):   # M - двоичный вектор
        summa = Point(self.crv, inf, inf)
        for i in range(len(self.AP)):
            if M[i] != 0:
                summa += self.AP[i]
        return summa.x, summa.y
        #t = randint(2, self.crv.p - 1)
        #C1 = t*self.R
        #C2 = summa + t*self.S
        #return C1, C2

    def Decrypt(self, X, Y): #C1, C2):
        C = Point(self.crv, X, Y)
        M = list()
        #C = C2 - self.d*C1
        for i in range(self.length-1, -1, -1):
            #XE = C - self.a[i]*self.P
            XE = C - self.AP[i]
            flag = True
            for j in range(pow(2, self.length-1)):
                flag &= XE - self.k*j*self.P != Point(self.crv, inf, inf)
                if not flag:
                    M.append(1)
                    C = XE
                    break
            if flag:
                M.append(0)
        return M

if __name__ == '__main__':
    encode = 'utf-16'
    text = open('text1.txt', 'rt', encoding=encode)
    crypt = open('Crypt.txt', 'wt', encoding=encode)
    decrypt = open('Decrypt.txt', 'wt', encoding=encode)
    length_of_symbol = 8
    mashine = Ell_Knapsack(length_of_symbol)

    time_to_encrypt = 0
    time_to_decrypt = 0

    for line in text.readlines():
        for symbol in line:
            symbol = Sym_to_bin(symbol, length_of_symbol)
            start = time.time()
            enc_symbol = mashine.Encrypt(symbol)
            time_to_encrypt += time.time() - start
            print(time_to_encrypt)
            for i in enc_symbol:
                crypt.write(str(hex(i)))
    crypt.close()

    crypt = open('Crypt.txt', 'rt', encoding=encode)
    cry = crypt.read().split('0x')
    for i in range(1, len(cry), 2):
        X, Y = int(cry[i], 16), int(cry[i + 1], 16)
        start = time.time()
        dec_symbol = mashine.Decrypt(X, Y)
        print(dec_symbol)
        time_to_decrypt += time.time() - start
        decrypt.write(Bin_to_sym(dec_symbol))

    print("---Encrypt for %s seconds---" % time_to_encrypt)
    print("---Decrypt for %s seconds---" % time_to_decrypt)
    decrypt.write('\n\n---Elliptic Knapsack---')
    #decrypt.write('\n---Length of key %s bits---' % length_of_key)
    decrypt.write("\n---Encrypt for %s seconds---" % time_to_encrypt)
    decrypt.write("\n---Decrypt for %s seconds---" % time_to_decrypt)
    crypt.close()
    decrypt.close()

# mashine = Ell_Knapsack()
# M = chr(getrandbits(8))
# print(M)
# M = Sym_to_bin(M)
# print(M)
# start_time = time.time()
# #C1, C2 = mashine.Encrypt(M)
# C = mashine.Encrypt(M)
# print(C)
# #M = mashine.Decrypt(C1, C2)
# M = mashine.Decrypt(C)
# print("--- %s seconds ---" % (time.time() - start_time))
# print(M)
# print(Bin_to_sym(M))


