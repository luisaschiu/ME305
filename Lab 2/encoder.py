# -*- coding: utf-8 -*-
''' @file       encoder.py
    @brief      An encoder driver for reading from Quadrature Encoders.
    @details    This file interacts with the Nucleo board by recording and updating position and delta of the encoder.
    @author     Faith Chau
    @author     Luisa Chiu
    @date       October 19, 2021
'''

import pyb

class Encoder:
    ''' @brief      Class that reads encoder.
        @details    Uses the operation of a timer to read from an encoder connected to arbitrary pins
    '''    
    def __init__(self, pinA, pinB, tim_num):
        ''' @brief              Constructs an encoder object.
            @details            The encoder object is created from three attributes: pinA, pinB, and timer number.
            @param pinA         First pin associated with the designated encoder object.
            @param pinB         Second pin associated with the designated encoder object.
            @param tim_num      Timer number associated with designated encoder object.
        '''
        ## @brief     "Auto Reload" value
        #  @details   Specifies the largest number that can be stored in the timer
        self.period = 65535
        ## @brief     Variable that specifies timer number
        #  @details   Uses attributes of prescaler and period to create timer object
        self.tim = pyb.Timer(tim_num, prescaler=0, period=self.period)
        self.tim.channel(1, pyb.Timer.ENC_AB, pin=pinA)
        self.tim.channel(2, pyb.Timer.ENC_AB, pin=pinB)
        ## @brief     Variable representing previous time stamp
        #  @details   Counter that corresponds to number of ticks
        self.start = self.tim.counter()
        ## @brief     The encoder position that counts total movement
        #  @details   The total position moved is characterized by the total number of timer counts
        self.enc_pos = 0                 #initialize encoder position
        
    def update(self):
        ''' @brief      Updates encoder position and delta
            @details    Detects delta overflow and corrects delta and calculates encoder position.
        '''
        ## @brief     Variable representing current time stamp
        #  @details   Counter that corresponds to number of ticks
        self.stop = self.tim.counter()       #time starts        
        ## @brief     Calculates delta
        #  @details   Delta is the difference between two most recently updated encoder positions
        self.delta = self.stop - self.start  #finds difference between initial and time value
        self.start = self.stop               #sets initial time to equal new time value 
        
        if self.delta > self.period/2:
           self.delta -= self.period
        elif self.delta < -self.period/2:
             self.delta += self.period
                
        self.enc_pos += self.delta
                 

    def get_position(self):
        ''' @brief      Returns encoder position
            @details    A function that returns encoder position
            @return     The position of the encoder shaft
        '''
        return self.enc_pos
    
    def set_position(self, position):
        ''' @brief      Sets encoder position
            @details    A function that sets encoder position to a specified value
            @return     The new position of the encoder shaft
        '''
        self.enc_pos = position
        self.start = self.stop
        
    def get_delta(self):
        ''' @brief      Returns encoder delta
            @details    A function that returns encoder delta
            @return     The change in position of the encoder shaft between the two most recent updates
        '''
        return self.delta

    






