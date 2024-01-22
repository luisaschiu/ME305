'''@file        task_IMU.py
   @brief       IMU driver
   @details     Implements a finite state machine that interacts with IMU driver
   @author      Faith Chau
   @author      Luisa Chiu
   @date        December 9, 2021
   \image html 
'''


S0_INIT = 0


S1_CALIBRATE = 1

class Task_IMU():
    ''' @brief      IMU task
        @details    Implements a finite state machine for the IMU task using the IMU driver to calibrate and collect IMU readings
    '''
    

   
    def __init__(self, period_IMU, IMU_obj, state_vect_x, calib_IMU_flag, state_vect_y):
        ''' @brief                  Constructs an IMU task
            @details                Interfaces with IMU attached to top of platform
            @param period_IMU       The period, in microseconds, between runs of the IMU task
            @param IMU_obj          IMU object created to interface with IMU task
            @param calib_IMU_flag   A boolean flag used to enable IMU calibration
            @param state_vect_x     List used to define state vector x
            @param state_vect_y     List used to define state vector y
        '''
        ## @brief     The frequency of the IMU task
        #  @details   Defines variable that specifies timer frequency
        self.period_IMU = period_IMU
        ## @brief     The IMU object
        #  @details   This IMU driver was defined in the main.py file
        self.IMU_obj = IMU_obj
        ## @brief     A boolean flag used to start IMU calibration
        #  @details   Works with the task IMU and user interface to enable IMU calibration
        self.calib_IMU_flag = calib_IMU_flag
        ## @brief     A shared list used to define state vector x
        #  @details   Contains variables for x position, theta y, x velocity, and angular velocity (theta y dot)
        self.state_vect_x = state_vect_x
        ## @brief     A shared list used to define state vector y
        #  @details   Contains variables for y position, theta x, y velocity, and angular velocity (theta x dot)
        self.state_vect_y = state_vect_y
        ## @brief     Sets the number of runs to 0
        #  @details   Defines a variable to keep track of runs
        self.runs = 0
        ## @brief     Sets initial state to State 0
        #  @details   FSM starts at State 0, where IMU data is inputted into state vectors
        self.state = S0_INIT
        
    def run(self):
        ''' @brief Runs one iteration of the FSM
        '''
        if self.state == S0_INIT:
            #Constantly updating euler angle and angular velocity readings to state vector arrays
            angle = self.IMU_obj.euler_angle()
            
            self.state_vect_x[1].write(angle[2])
            self.state_vect_y[1].write(angle[1])

            
            angular_velocity = self.IMU_obj.angular_vel()
            self.state_vect_x[3].write(angular_velocity[2])
            self.state_vect_y[3].write(angular_velocity[1])
            
            if self.calib_IMU_flag.read() == 1:
                self.state = S1_CALIBRATE
           
        if self.state == S1_CALIBRATE:
            #Call calibration function when prompted by user
            self.IMU_obj.set_calib_coef()
            self.state = S0_INIT

                
            
                