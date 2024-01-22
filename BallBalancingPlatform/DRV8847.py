'''@file        DRV8847.py
   @brief       A motor driver for the DRV8847 from Texas Instruments.
   @details     Creates a motor driver object.
   @author      Faith Chau
   @author      Luisa Chiu
   @date        December 9, 2021
'''
import pyb
import utime


class DRV8847:
    ''' @brief    A motor driver class for the DRV8847 from Texas Instruments.
        @details  Objects of this class can be used to configure the DRV8847
                  motor driver and to create one or more objects of the 
                  Motor class which can be used to perform motor control.
    '''


    def __init__ (self, nSLEEP, nFAULT, tim):
        ''' @brief              Constructs a motor driver object
            @details            The motor driver object is created from three attributes: nSLEEP, nFAULT, and timer number.
            @param nSLEEP       This is an active-high enable pin that corresponds to pin A15
            @param nFAULT       This is a pin that detects faults and corresponds to pin B2
            @param tim          Variable that specifies timer number
        '''
        ## @brief     This is an active-high enable pin that corresponds to pin A15
        #  @details   When set on high, it enables the motors. When set on low, it disables the motors.
        self.nSLEEP = pyb.Pin(nSLEEP, pyb.Pin.OUT_PP)
        ## @brief     This is a pin that detects faults and corresponds to pin B2
        #  @details   Detects fault conditions that may damage the motors
        self.nFAULT = pyb.Pin(nFAULT, pyb.Pin.IN)
        ## @brief     Variable that specifies timer number
        #  @details   Uses an attribute of frequency to create a timer object
        self.tim = pyb.Timer(tim, freq = 20000)
        ## @brief     A boolean flag that signals the motor of a fault detection
        #  @details   This variable initializes the fault callback flag
        self.fault_cb_flag = 0
        ## @brief     Registers the callback function and causes an interrupt when fault is triggered
        #  @details   Defines a variable for the interrupt request for fault detection
        self.fault = pyb.ExtInt(self.nFAULT, mode=pyb.ExtInt.IRQ_FALLING, pull=pyb.Pin.PULL_NONE, callback=self.fault_cb)       

        pass
    
    def enable (self):
        ''' @brief Brings the DRV8847 out of sleep mode.
        '''
        self.fault.disable()
        self.nSLEEP.high()
        utime.sleep_us(25)
        self.fault.enable()
        pass
    
    def disable (self):
        ''' @brief Puts the DRV8847 in sleep mode.
        '''
        self.nSLEEP.low()
        pass
    
    def fault_cb (self, IRQ_irc):
        ''' @brief Callback function to run on fault condition.
            @param IRQ_src The source of the interrupt request.
        '''
        self.fault_cb_flag = 1
        self.disable()
        print('Error: Fault detected')
        pass
    
    def motor (self, pinA, pinB, channel_A, channel_B): 
        ''' @brief Initializes and return a motor object associated with DRV8847.
            @return An object of class Motor
        '''
        return Motor(pinA, pinB, channel_A, channel_B, self.tim)
    
class Motor:
    ''' @brief A motor class for one channel of the DRV8847.
        @details Objects of this class can be used to apply PWM to a given DC motor.
    '''

    def __init__ (self, pinA, pinB, channel_A, channel_B, tim):
        ''' @brief Initializes and returns a motor object associated wtih the DRV8847.
            @details Objects of this class should not be instantiated directly. Instead
                     create a DRV8847 object and use that to create Motor objects using
                     the method DRV8847.motor().
        '''
        ## @brief     Variable that specifies timer number
        #  @details   This variable was created to generalize timer number and allow for specification in task files
        self.tim = tim
        ## @brief     Variable that specifies channel number corresponding to motor 1
        #  @details   This variable was created to generalize channel number and allow for specification in task files
        self.channel_A = self.tim.channel(channel_A, pyb.Timer.PWM, pin=pinA)
        ## @brief     Variable that specifies channel number corresponding to motor 2
        #  @details   This variable was created to generalize channel number and allow for specification in task files
        self.channel_B = self.tim.channel(channel_B, pyb.Timer.PWM, pin=pinB)
        pass
    
    def set_duty (self, duty):
        ''' @brief Set the PWM duty cycle for the motor channel.
            @details This method sets the duty cycle to be sent to the motor to the 
                     given level. Positive values cause effort in one direction, 
                     negative values in the opposite direction.
            @param duty A signed number holding the duty cycle of the PWM signal sent to the motor.
        '''
        # forward motion
        ## @brief     Variable that defines duty cycle for PWM input
        #  @details   Duty cycle values control motor speed
        self.duty = duty
        if self.duty > 0:
            self.channel_A.pulse_width_percent(self.duty)
            self.channel_B.pulse_width_percent(0)
            
        # backward motion
        if self.duty < 0:
            self.channel_A.pulse_width_percent(0)
            self.channel_B.pulse_width_percent(-self.duty)
        
        # no motion
        if self.duty == 0:
            self.channel_A.pulse_width_percent(0)
            self.channel_A.pulse_width_percent(0)
        pass
    
