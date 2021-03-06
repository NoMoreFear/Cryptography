from Elliptic_Curve import gcdex
from Classic_Elgamal import isPrime
from functools import reduce
from itertools import repeat
import pathos.multiprocessing as pm
import numpy as np
import sympy as sp
from sympy import Matrix
from random import randint, getrandbits
import time

class Mtr_Elgamal:
    def __init__(self, order, len_of_key, amount_of_fond):
        self.executor = pm.ProcessingPool()
        self.primes = list()
        for i in range(amount_of_fond):
            num = getrandbits(len_of_key)
            while not isPrime(num):
                num = getrandbits(len_of_key)
            self.primes.append(num)

        self.Prime = reduce(lambda a, b: a * b, self.primes)
        func = lambda m: self.Prime // m * (gcdex(self.Prime // m, m)[1] % m)
        self.weights = tuple(map(func, self.primes))
        self.size = order
        self.A = list()
        for i in range(self.size):
            self.A.append(list())
            for j in range(self.size):
                self.A[i].append(randint(0, self.Prime))
        self.alpha = randint(2, self.Prime - 1)
        self.powA = self.Pow_matrix(self.A, self.alpha, self.Prime)
        pass

    def Mult_matrix(self, A, B, prime):
        ans = list()
        for i in range(self.size):
            ans.append(list())
            for j in range(self.size):
                ans[i].append(0)
                for k in range(self.size):
                    ans[i][j] += A[i][k] * B[k][j]
                ans[i][j] %= prime
        return ans

    def Pow_matrix(self, A, n, prime):
        steps = list()
        while True:
            if n == 1:
                break
            elif n % 2 == 1:
                n -= 1
                steps.append(1)
            else:
                n //= 2
                steps.append(n)
        steps.reverse()
        ans = A
        for i in steps:
            if i == 1:
                ans = self.Mult_matrix(ans, A, prime)
            else:
                ans = self.Mult_matrix(ans, ans, prime)
        return ans

    def Inv_matrix(self, A, prime):
        M = list()
        determinate = sp.det(Matrix(A)) # определитель матрицы
        determinate = gcdex(determinate, prime)[1] % prime # det(A)^(-1)
        for i in range(self.size):
            M.append(list())
            for j in range(self.size):
                m = np.delete(A, i, axis=0)
                m = sp.det(Matrix(np.delete(m, j, axis=1)))  # алгебраическое дополнение
                M[i].append(pow(-1, i+j) * m * determinate % prime)
        M = list(map(list, zip(*M)))
        return M

    def Encrypt(self, mes):
        session_key = randint(2, self.Prime - 1)
        china_C1 = self.executor.map(self.Pow_matrix, repeat(self.A), repeat(session_key), self.primes)
        china_C2 = self.executor.map(self.Pow_matrix, repeat(self.powA), repeat(session_key), self.primes)
        china_C2 = self.executor.map(self.Mult_matrix, repeat(mes), china_C2, self.primes)
        C1 = [[0] * self.size for i in range(self.size)]
        C2 = [[0] * self.size for i in range(self.size)]
        for line in range(self.size):  # собираем из n матриц одну
            for row in range(self.size):
                for matrix in range(len(self.primes)):
                    C1[line][row] += china_C1[matrix][line][row] * self.weights[matrix]
                    C2[line][row] += china_C2[matrix][line][row] * self.weights[matrix]
                C1[line][row] %= self.Prime
                C2[line][row] %= self.Prime
        return C1 + C2

    def Decrypt(self, C1, C2):  # mes = C2*(C1^alpha)^(-1)
        china_C = self.executor.map(self.Pow_matrix, repeat(C1), repeat(self.alpha), self.primes)
        china_C = self.executor.map(self.Inv_matrix, china_C, self.primes)
        china_C = self.executor.map(self.Mult_matrix, repeat(C2), china_C, self.primes)
        C = [[0] * self.size for i in range(self.size)]
        for line in range(self.size):  # собираем из n матриц одну
            for row in range(self.size):
                for matrix in range(len(self.primes)):
                    C[line][row] += china_C[matrix][line][row] * self.weights[matrix]
                C[line][row] %= self.Prime
        return C

if __name__ == '__main__':
    encode = 'utf-16'
    text = open('text.txt', 'rt', encoding=encode)
    crypt = open('Crypt.txt', 'wt', encoding=encode)
    decrypt = open('Decrypt.txt', 'wt', encoding=encode)
    order = 6
    length_of_key = 32
    amount_of_foundation = 2
    mashine = Mtr_Elgamal(order, length_of_key, amount_of_foundation)

    time_to_encrypt = 0
    symbols = text.read(pow(order, 2))
    while symbols:
        print(symbols)
        '''преобразование текста к списку размера order*order'''
        symbols = list(map(ord, symbols))
        while len(symbols) < pow(order, 2):
            symbols.append(ord(' '))
        symbols = np.array(symbols).reshape((order, order))
        symbols = symbols.tolist()

        '''шифрование и время'''
        start = time.time()
        enc_sym = mashine.Encrypt(symbols)
        time_to_encrypt += time.time() - start
        print(time_to_encrypt)

        '''вывод результата шифрования'''
        for i in range(len(enc_sym)):
            for j in range(len(enc_sym[i])):
                crypt.write(str(hex(enc_sym[i][j])))

        '''так до конца документа'''
        symbols = text.read(pow(order, 2))
    crypt.close()
    print("---Encrypt for %s seconds---" % time_to_encrypt)

    time_to_decrypt = 0
    crypt = open('Crypt.txt', 'rt', encoding=encode)
    cry_text = crypt.read().split('0x')
    cry_text.pop(0)
    while cry_text:
        '''преобразование текста к списку размера order*order'''
        enc_sym = np.array([int(cry_text.pop(0), 16) for i in range(2 * pow(order, 2))]).reshape(order*2, order)
        enc_sym = enc_sym.tolist()

        '''дешифрование и время'''
        start = time.time()
        enc_sym = mashine.Decrypt([enc_sym.pop(0) for i in range(order)], enc_sym)
        time_to_decrypt += time.time() - start

        '''Вывод результата дешифрования'''
        for i in range(len(enc_sym)):
            for j in range(len(enc_sym[i])):
                decrypt.write(chr(enc_sym[i][j]))
        '''так до конца документа'''
    print("---Decrypt for %s seconds---" % time_to_decrypt)
    decrypt.write('\n\n---Chinese Matrix Elgamal---')
    decrypt.write('\n---Length of key %s bits---' % length_of_key)
    decrypt.write('\n---The order of matrix %s---' % order)
    decrypt.write("\n---Encrypt for %s seconds---" % time_to_encrypt)
    decrypt.write("\n---Decrypt for %s seconds---" % time_to_decrypt)
    crypt.close()
    decrypt.close()