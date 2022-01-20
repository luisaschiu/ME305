# -*- coding: utf-8 -*-
'''
@author  Luisa Chiu
@file    Lab0x00.py
@brief   This function calculates a Fibonacci number at a specific index.
@param idx An integer specifying the index of the desired Fibonacci number

'''

def fib(idx):
    if int(idx) == 0:
        return 0
    elif int(idx) == 1:
        return 1      
    else:
        f0 = 0
        f1 = 1
        for i in range(int(idx)-1):
            fn = f0 + f1
            f0 = f1
            f1 = fn
        return fn

if __name__ == '__main__':
    my_string = 'yes'
    while my_string == 'yes':
        idx = input ('Choose an index: ')
        if not idx.isdigit():
            print ('The index must be a positive integer!')
        elif int(idx) < 0:
            print ('The index must be a positive integer!')
        else:
            print ('Fibonacci number at index {:} is {:}.'.format(idx,fib(idx)))
        my_string = input ('Enter no to quit or yes to continue:')
