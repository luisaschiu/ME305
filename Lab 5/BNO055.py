'''@file        BNO055.py
   @brief       An orientation sensor driver for the BNO055 from Bosch Sensortec.
   @details     Creates an orientation sensor driver object.
   @author      Faith Chau
   @author      Luisa Chiu
   @date        December 9, 2021
'''
import struct
import os
import array

class BNO055:
    ''' @brief    An orientation sensor driver class for the BNO055 from Bosch Sensortec.
        @details  Objects of this class can be used to configure the BNO055
                  orientation sensor driver and to create an object of the 
                  BNO055 class which can be used to perform orientation sensor control.
    '''
    
    
    def __init__ (self, i2c, calib_IMU_flag):
        ''' @brief                      Constructs an orientation sensor driver object
            @details                    The orientation sensor driver object is created from the i2c class. It is
                                        used to calibrate the IMU and find angle and angular velocity.
            @param i2c                  A two-wire protocol for communicating between devices.
            @param calib_IMU_flag       A boolean flag used to enable IMU calibration
        '''
        ## @brief     A two-wire protocol for communicating between devices
        #  @details   Defines a variable that specifies the i2c class
        self.i2c = i2c
        ## @brief     An array filled with calibration coefficients read by the i2c
        #  @details   Defines a variable that specifies the calibration coefficients array.
        self.calib_coefs = array.array('b', 22*[0])
        ## @brief     A boolean flag used to start IMU calibration
        #  @details   Works with the task IMU and user interface to do IMU calibration
        self.calib_IMU_flag = calib_IMU_flag
        
    def set_operating (self):
        ''' @brief Sets operating mode
        '''
        self.i2c.mem_write(0x0C, 0x28, 0x3D)
    
    def get_calib_status (self):
        ''' @brief Gets calibration status of the i2c
        '''
        cal_bytes = self.i2c.mem_read(1, 0x28, 0x35)
        print('Calibration Status')
        self._cal_status = (cal_bytes[0] & 0b11,
                     (cal_bytes[0] & 0b11 <<2) >> 2,
                     (cal_bytes[0] & 0b11 <<4) >> 4,
                     (cal_bytes[0] & 0b11 <<6) >> 6)
        print("Values:", self._cal_status)
        print('\n')        
    
    def get_calib_coef (self):
        ''' @brief Gets calibration coefficients of the i2c
        '''
        #create byte array of 22 spots, read all 
        self.calib_coefs = array.array('b', 22*[0])
        self._calib_coef.decode('utf-8')
        print(self.calib_coef)
        
    def set_calib_coef (self):
        ''' @brief Sets calibration status of the i2c
        '''
        filename = "IMU_cal_coeffs.txt"
        if filename in os.listdir():
            with open(filename, 'r') as f:
                cal_data_string = f.readline()
                cal_values = bytes(int(cal_value) for cal_value in cal_data_string.strip().split(','))              
                self._calib_coef = self.i2c.mem_write(cal_values,0x28,0x55)
                print('IMU Calibrated.')
                self.calib_IMU_flag.write(0)
        else:
            with open(filename, 'w') as f:
                if self._cal_status == bytearray('3,3,3,3'):
                    
                    #array.array('b', 22*[0]) = cal_values
                    
                    #IMU_coefs = (R55, R56, R57, R58, R59, R5A, R5B, R5C, R5D, R5E, R5F, R60, R61, R62, R63, R64, R65, R66, R67, R68, R69, RA) 
                    #f.write(f"{R55}, {R56}, {R57}, {R58}, {R59}, {R5A}, {R5B}, {R5C}, {R5D}, {R5E}, {R5F}, {R60}, {R61}, {R62}, {R63}, {R64}, {R65}, {R66}, {R67}, {R68}, {R69}, {RA}\r\n")
                    pass
        
    def euler_angle (self):
        ''' @brief Obtains and returns euler angles measured by the i2c
        '''
        self.set_operating()
        eul_bytes = bytearray(6)
        eul_bytes = self.i2c.mem_read(eul_bytes, 0x28, 0x1A)    
        eul_signed_ints = struct.unpack('<hhh', eul_bytes)       
        eul_vals = tuple(eul_int/16 for eul_int in eul_signed_ints)
        return(eul_vals)
                 
    
    def angular_vel (self):
        ''' @brief Obtains and returns angular velocity measured by the i2c
        '''
        self.set_operating()
        ang_bytes = bytearray(6)
        ang_bytes = self.i2c.mem_read(ang_bytes, 0x28, 0x14)
        ang_signed_ints = struct.unpack('<hhh', ang_bytes)        
        ang_vals = tuple(ang_int/900 for ang_int in ang_signed_ints)
        return(ang_vals)
  