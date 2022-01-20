'''@file        closedloop.py
   @brief       Closed loop control used with a motor and encoder to modify and control motor speed
   @details     Takes input values (gain and reference value) to compute actuation levels based on measured values. Can also be used to modify gain value.
   @author      Faith Chau
   @author      Luisa Chiu
   @date        November 15, 2021
'''

from ulab import numpy as np

class ClosedLoop:
    ''' @brief   A closed loop speed control used in conjuction with the motor and encoder drivers
        @details Objects of this class can be used to control and monitor motor speed
        
    '''

    def __init__ (self, sat_max, sat_min, L, state_vect, gain):
        ''' @brief            Constructs a controller object that computes an actuation value based on reference and measured values
            @details          This class uses gains and position and angle data to compute an actuation value.
            @param sat_max    Variable used to define maximum saturation limit for the PWM level used for motor speed
            @param sat_min    Variable used to define minimum saturation limit for the PWM level used for motor speed
            @param L          Variable used to define actuation level
            @state_vect       Variable used to define state vectors
            @param gain       Variable used to define proportional gain value
        '''
        ## @brief    Variable used to define maximum saturation limit for the PWM level
        #  @details  This value is set to ensure the motor does not fall below a maximum PWM level
        self.sat_max = sat_max
        ## @brief    Variable used to define minimum saturation limit for the PWM level
        #  @details  This value is set to ensure the motor does not fall below a minimum PWM level
        self.sat_min = sat_min
        ## @brief    Variable used to define actuation level for motor 1
        #  @details  This value is calculated using gain, position data, and angle data
        self.L = L
        ## @brief    Variable used to define proportional gain value
        #  @details  This value is the proportional gain inputted by the user.
        self.gain = gain
        ## @brief    Variable used to define state vectors
        #  @details  This array is filled with data in the following order: [position, velocity, angle, angular velocity]
        self.state_vect = state_vect
        
    def run (self):
        ''' @brief Uses state vector values and gain values to compute torque to compute actuation value L.
        '''
        ## @brief    Variable used to define the array for state vectors
        #  @details  This array will be filled with state vector data read from the touch panel and IMU
        self.state_vect_array = np.array([self.state_vect[0].read(), self.state_vect[1].read(), self.state_vect[2].read(), self.state_vect[3].read()])                  
        ## @brief    Variable used to define the torque calculated
        #  @details  This value is calculated using gain values and the state vector values
        self.Torque = np.dot(-self.gain,self.state_vect_array)
        self.L.write((13.345)*self.Torque*100/4)
        if self.L.read() > self.sat_max:
           self.L.write(self.sat_max)
        if self.L.read() < self.sat_min:
           self.L.write(self.sat_min)
        pass                  
                           
    
    def get__Kp (self):
        ''' @brief Returns gain value for modification
        '''
        return self.Kp
        

    def set__Kp (self, Kp):
        ''' @brief Sets modified gain value
        '''
        ## @brief    Kp represents the proportional gain value
        #  @details  This value is used for modification
        self.Kp = Kp