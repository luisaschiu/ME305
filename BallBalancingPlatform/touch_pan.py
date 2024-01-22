'''@file        touch_pan.py       
   @brief       Touch panel driver
   @details     Implements finite state machine that interacts with touch panel task
   @author      Faith Chau
   @author      Luisa Chiu
   @date        December 9, 2021
'''

from pyb import Pin
import pyb
import utime
import micropython
from ulab import numpy as np
import array
import os

## @brief     Constant created for Pin.OUT_PP
#  @details   Used to increase task speed
OUT_PP = micropython.const(Pin.OUT_PP)
## @brief     Constant created for Pin.IN
#  @details   Used to increase task speed
IN = micropython.const(Pin.IN)

class Touch_Pan:
    ''' @brief   Hardware driver to interface resistive touch panels with the STM32 microcontroller
        @details Scans X, Y, and Z components of contact point on touch panel by configuring 4 pin objects
    '''

    def __init__ (self, x_p, x_m, y_p, y_m):
        ''' @brief              Constructs a touch panel object
            @details            The touch panel object is created from four touch panel pins configured to read the touch panel.
            @param x_p          Used to scan x component from touch panel, configured as a push-pull output 
            @param x_m          Used to scan x component from touch panel, configured as a push-pull output   
            @param y_p          Used to scan y component from touch panel, configured as a push-pull output
            @param y_m          Used to scan y component from touch panel, configured as a push-pull output 
        '''
        ## @brief     Variable for pin reading x-component of contact point 
        #  @details   Used to locate touch in x-direction
        self.x_p = x_p
        ## @brief     Variable for pin reading x-component of contact point 
        #  @details   Used to locate touch in x-direction
        self.x_m = x_m
        ## @brief     Variable for pin reading y-component of contact point 
        #  @details   Used to locate touch in y-direction
        self.y_p = y_p
        ## @brief     Variable for pin reading y-component of contact point 
        #  @details   Used to locate touch in y-direction
        self.y_m = y_m
        ## @brief     Variable for width of touch panel
        #  @details   Defines width of panel in the x-direction
        self.x_width = 176 #mm
        ## @brief     Variable for length of touch panel
        #  @details   Defines length of panel in the y-direction
        self.y_length = 100 #mm
        ## @brief     A boolean flag used to detect contact with touch panel
        #  @details   Signals to the panel to read values when contact is made
        self.z_ADC_flag = 0
        ## @brief     A flag used to signal whether the panel has been calibrated or not
        #  @details   Determines which coordinate values (calibrated or not-calibrated) to return
        self.calibrate_flag = 0
        ## @brief     Array to define beta values
        #  @details   Used to calibrate the touch panel and account for center offset
        self.beta = array.array('f', 6*[0]) 

    def get_x(self): 
        ''' @brief Reads x position. Returns uncalibrated values.
        '''
        self._x_x_p = Pin(self.x_p, OUT_PP)
        self._x_x_m = Pin(self.x_m, OUT_PP)
        self._x_y_p = Pin(self.y_p, IN)
        self._x_y_m = pyb.ADC(self.y_m)        
        self._x_x_p.high()
        self._x_x_m.low()
        
        return self.x_ADC
        
    
    def get_y(self):  
        ''' @brief Reads y position. Returns uncalibrated values.
        '''
        self._y_x_p = pyb.ADC(self.x_p)
        self._y_x_m = Pin(self.x_m, IN)
        self._y_y_p = Pin(self.y_p, OUT_PP)
        self._y_y_m = Pin(self.y_m, OUT_PP)
        
        self._y_y_p.high()
        self._y_y_m.low()

        return self.y_ADC
        
    def get_z(self):  
        ''' @brief Reads z "position" and creates a boolean flag for when contact is detected.
        '''
        self._z_x_p = pyb.ADC(self.x_p)
        self._z_x_m = Pin(self.x_m, OUT_PP)
        self._z_y_p = Pin(self.y_p, OUT_PP)
        self._z_y_m = Pin(self.y_m, IN)
        
        self._z_y_p.high()
        self._z_x_m.low()
        self.z_ADC = self.z_x_p.read()/4095
        if self.z_ADC > 0.1:
            self.z_ADC_flag = 1
        else:
            self.z_ADC_flag = 0
            
        return self.z_ADC
    
    def get_coords(self):
        ''' @brief Gets x, y, and z positions. Returns uncalibrated and calibrated values.
        '''
        self._x_x_p = Pin(self.x_p, OUT_PP)
        self._x_x_m = Pin(self.x_m, OUT_PP)
        self._x_y_p = Pin(self.y_p, IN)
        self._x_y_m = pyb.ADC(self.y_m)
        self._x_x_p.high()
        self._x_x_m.low()
        ## @brief Uncalibrated x-position values read by touch panel
        #  @details Measures x-position
        self.x_ADC = self.x_y_m.read()
        
        self._y_x_p = pyb.ADC(self.x_p)
        self._y_x_m = Pin(self.x_m, IN)
        self._y_y_p = Pin(self.y_p, OUT_PP)
        self._y_y_m = Pin(self.y_m, OUT_PP) 
        self._y_y_p.high()
        self._y_y_m.low()
        ## @brief Uncalibrated y-position values read by touch panel
        #  @details Measures y-position
        self.y_ADC = self.y_x_p.read()      
        
        self._z_x_p = pyb.ADC(self.x_p)
        self._z_x_m = Pin(self.x_m, OUT_PP)
        self._z_y_p = Pin(self.y_p, OUT_PP)
        self._z_y_m = Pin(self.y_m, IN)
        
        self._z_y_p.high()
        self._z_x_m.low()
        
        ## @brief Uncalibrated z-position values read by touch panel
        #  @details Measures z-position (contact with panel)
        self.z_ADC = self.z_x_p.read()/4095
        
        if self.z_ADC > 0.1:
            self.z_ADC_flag = 1
        else:
            self.z_ADC_flag = 0
            
        
        if self.calibrate_flag == 1:
            ## @brief Calibrated x-position values read by touch panel
            #  @details Measures x-position accurately based on manual or automatic calibration constants
            self.x_ADC_cal = self.x_ADC*self.beta[0] + self.y_ADC*self.beta[1] + self.beta[4]
            ## @brief Calibrated y-position values read by touch panel
            #  @details Measures y-position accurately based on manual or automatic calibration constants
            self.y_ADC_cal = self.x_ADC*self.beta[2] + self.y_ADC*self.beta[3] + self.beta[5]

            if self.z_ADC > 0.1:
                self.z_ADC_flag = 1
            else:
                self.z_ADC_flag = 0 
                self.x_ADC_cal = 0
                self.y_ADC_cal = 0
            ## @brief Calibrated x and y positions read by panel
            #  @details Creates list of positions to be used for state vectors      
            self.calibrated_pos = (self.x_ADC_cal, self.y_ADC_cal)
            return(self.calibrated_pos)
        else:
            ## @brief Uncalibrated x and y positions read by panel
            #  @details Creates list of uncalibrated positions. Should not be used for ball balancing.
            self.uncalibrated_pos = (self.x_ADC, self.y_ADC)
            return self.uncalibrated_pos
        
     
    def calibrate(self):
        ''' @brief Calibrates touch panel
        '''
        filename = "RT_cal_coeffs.txt"
        if filename in os.listdir():
            with open(filename, 'r') as f:
                cal_data_string = f.readline()
                cal_values = [float(cal_value) for cal_value in cal_data_string.strip().split(',')]
                (Kxx, Kxy, Kyx, Kyy, Xc, Yc) = cal_values
                self.beta[0] = (cal_values[0]) 
                self.beta[1] = (cal_values[1]) 
                self.beta[2] = (cal_values[2]) 
                self.beta[3] = (cal_values[3]) 
                self.beta[4] = (cal_values[4]) 
                self.beta[5] = (cal_values[5]) 
                print('Panel has been calibrated, no need to touch panel')
                self.calibrate_flag = 1
        else:
            
            ## @brief Array of panel coordinates
            #  @details Coordinates to be used in panel calibration calculations 
            self.panel_coords = np.array([[-80 ,  40],   #top far left
                                          [80  ,  40],   #top far right
                                          [0   ,  0],    #center of plate
                                          [-80 ,  -40],  #bottom far left
                                          [80  ,  -40]]) #bottom far right
            ## @brief Instructions for user during panel calibration
            #  @details User touches the listed coordinates for panel calibration
            self.panel_coords_instr = ['top left', 
                                       'top right',
                                       'center',
                                       'bottom left',
                                       'bottom right']
            ## @brief Empty array for panel measurements
            #  @details Measured positional coordinates to be used in panel calibration calculations
            self.panel_meas = np.zeros((5,3))
            ## @brief     A variable used for indexing
            #  @details   This value helps index state vector points for calibration
            self.i = 0
            print('Place a finger on the ' + str(self.panel_coords_instr[self.i]))
            while self.i <= (len(self.panel_meas)-1): 
                utime.sleep(.4)
                self.get_coords()

                if self.z_ADC_flag == 1:
                    self.panel_meas[self.i,0] = self.x_ADC
                    self.panel_meas[self.i,1] = self.y_ADC
                    self.panel_meas[self.i,2] = 1
                    print('Contact detected')

                    self.i += 1
                    if self.i < len(self.panel_meas):
                        print('Place a finger on the ' + str(self.panel_coords_instr[self.i]))

     
    
            mult1 = np.dot(self.panel_meas.transpose(),self.panel_meas)
            mult2 = np.dot(self.panel_meas.transpose(),self.panel_coords)
            inv = np.linalg.inv(mult1)
            ## @brief     Array of calculated panel coefficients
            #  @details   Beta values that will be applied to ADC position readings to calibrate touch panel coordinates
            self.touch_coeffs = np.dot(inv,mult2)
            print('K matrix' + str(self.touch_coeffs))
            self.beta = array.array('f', 6*[0])
            self.beta[0] = (self.touch_coeffs[0,0]) 
            self.beta[1] = (self.touch_coeffs[0,1]) 
            self.beta[2] = (self.touch_coeffs[1,0]) 
            self.beta[3] = (self.touch_coeffs[1,1]) 
            self.beta[4] = (self.touch_coeffs[2,0]) 
            self.beta[5] = (self.touch_coeffs[2,1])
            with open(filename, 'w') as f:
                (Kxx, Kxy, Kyx, Kyy, Xc, Yc) = (self.beta[0], self.beta[1], self.beta[2], self.beta[3], self.beta[4], self.beta[5])
                f.write(f"{Kxx}, {Kxy}, {Kyx}, {Kyy}, {Xc}, {Yc}\r\n")
                self.calibrate_flag = 1
                
        