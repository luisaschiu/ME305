''' @file        task_userinterface.py
    @brief       User interface task for the term project.
    @details     Implements a finite state machine that runs a data collection interface to interact with the IMU, touch panel, and motors.
    @author      Faith Chau
    @author      Luisa Chiu
    @date        December 9, 2021
    \image html  LabFF_TaskUser.png "Lab FF Task User FSM"
'''
import utime
import pyb
import array

## @brief     State 0 of the user interface task
#  @details   Creates an initial state condition for state 0.
S0_init = 0

## @brief     State 1 of the user interface task
#  @details   Creates an initial state condition for state 1. This state waits for user input.
S1_wait_for_char = 1

## @brief      State 2 of the user interface task
#  @details    Creates an initial state condition for state 2. State 2 raises the balance_flag that communicates to the motor task to start ball and platform balancing.
S2_ball = 2

## @brief      State 3 of the user interface task
#  @details    Creates an initial state condition for state 3. State 3 raises the calib_pan_flag that communicates to the panel task to run panel calibration.
S3_calibrate_panel = 3

## @brief     State 4 of the user interface task
#  @details   Creates an initial state condition for state 4. State 4 raises the calib_IMU_flag that communicates to the IMU task to run IMU calibration.
S4_calibrate_IMU = 4

## @brief     State 5 of the user interface task
#  @details   Creates an initial state condition for state 5. State 5 collects state vector data for both x and y directions for 5 seconds.
S5_collect_data = 5

## @brief     State 6 of the user interface task
#  @details   Creates an initial state condition for state 6. State 6 prints the collected state vector data.
S6_print_data = 6

## @brief     State 7 of the user interface task
#  @details   Creates an initial state condition for state 7. State 7 disables motors 1 and 2 by setting the PWM levels to 0.
S7_disable = 7



class Task_User():
    ''' @brief      User interface task for data collection and interaction with all the tasks
        @details    Implements a finite state machine that communicates with the user to interface with all the tasks
    '''    
    def __init__(self, period, balance_flag, calib_pan_flag, calib_IMU_flag, disable_flag, state_vect_x, state_vect_y, L_1, L_2):
        ''' @brief                  Constructs the user interface task
            @details                The user task is implemented as a finite state machine that interacts between the user and the program.
            @param period           The period, in microseconds, between runs of the task
            @param balance_flag     A boolean flag used to enable ball balancing
            @param calib_pan_flag   A boolean flag used to enable touch panel calibration
            @param calib_IMU_flag   A boolean flag used to enable IMU calibration
            @param disable_flag     A boolean flag used to disable the motors
            @param L_1              Variable used to define actuation level for motor 1
            @param L_2              Variable used to define actuation level for motor 2
            @param state_vect_x     List used to define state vector x
            @param state_vect_y     List used to define state vector y
        '''
        ## @brief     The frequency of the task
        #  @details   Defines variable that specifies timer frequency
        self.period = period
        ## @brief     Sets initial state to State 0
        #  @details   FSM starts at State 0, where user input is prompted for further action
        self.state = S0_init
        ## @brief     Sets the number of runs to 0
        #  @details   Defines a variable to keep track of runs
        self.runs = 0
        ## @brief     The utime.ticks_us() value associated with the next run of the FSM
        #  @details   Defines a variable that adds the period to the ongoing timer
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period)
        ## @brief     A serial port to use for user I/O
        #  @details   Creates a new USB_VCP object
        self.ser = pyb.USB_VCP()
        ## @brief     A boolean flag used to start balancing the platform and/or ball
        #  @details   Works with the motor task and user interface to implement closed-loop control that balances the platform and ball
        self.balance_flag = balance_flag        
        ## @brief     A variable used for indexing
        #  @details   This value helps index state vector points for data collection
        self.i = 0
        ## @brief     A boolean flag used to start touch panel calibration
        #  @details   Works with the task panel and user interface to do resistive touch panel calibration
        self.calib_pan_flag = calib_pan_flag
        ## @brief     A boolean flag used to start IMU calibration
        #  @details   Works with the task IMU and user interface to do IMU calibration
        self.calib_IMU_flag = calib_IMU_flag
        ## @brief     A boolean flag used to disable motors
        #  @details   Works with the motor task and user interface to halt motor movement
        self.disable_flag = disable_flag
        ## @brief     A shared list used to define state vector x
        #  @details   Contains variables for x position, theta y, x velocity, and angular velocity (theta y dot)
        self.state_vect_x = state_vect_x
        ## @brief     A shared list used to define state vector y
        #  @details   Contains variables for y position, theta x, y velocity, and angular velocity (theta x dot)
        self.state_vect_y = state_vect_y     
        ## @brief     Variable used to define actuation level for motor 1
        #  @details   This value is calculated using input gain and torque
        self.L_1 = L_1
        ## @brief     Variable used to define actuation level for motor 2
        #  @details   This value is calculated using input gain and torque
        self.L_2 = L_2
        ## @brief     The utime.ticks_us() value associated with the next run of the FSM
        #  @details   Defines a variable that adds the period to the ongoing timer
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period) 
        ## @brief    An array for time
        #  @details  This variable creates an empty array of 1000 data points, which will be populated with time data
        self.time_array = array.array('f',1000*[0])
        ## @brief    An array for x position
        #  @details  This variable creates an empty array of 1000 data points, which will be populated with x-position data gathered from the touch panel
        self.x_array = array.array('f',1000*[0])
        ## @brief    An array for theta y angle
        #  @details  This variable creates an empty array of 1000 data points, which will be populated with angular position data in the y axis gathered from the IMU
        self.thy_array = array.array('f',1000*[0])
        ## @brief    An array for x velocity
        #  @details  This variable creates an empty array of 1000 data points, which will be populated with x-velocity data gathered from the touch panel
        self.xd_array = array.array('f',1000*[0])
        ## @brief    An array for angular velocity (y direction)
        #  @details  This variable creates an empty array of 1000 data points, which will be populated with angular velocity data in the y axis gathered from the IMU
        self.thyd_array = array.array('f',1000*[0])
        ## @brief    An array for y position
        #  @details  This variable creates an empty array of 1000 data points, which will be populated with y-position data gathered from the touch panel
        self.y_array = array.array('f',1000*[0])
        ## @brief    An array for theta x angle
        #  @details  This variable creates an empty array of 1000 data points, which will be populated with angular position data in the x axis gathered from the IMU
        self.thx_array = array.array('f',1000*[0])
        ## @brief    An array for y velocity
        #  @details  This variable creates an empty array of 1000 data points, which will be populated with y-velocity data gathered from the touch panel
        self.yd_array = array.array('f',1000*[0])
        ## @brief    An array for angular velocity (x direction)
        #  @details  This variable creates an empty array of 1000 data points, which will be populated with angular velocity data in the x axis gathered from the IMU
        self.thxd_array = array.array('f',1000*[0])
        
        
    def run(self):
            ''' @brief     Runs one iteration of the FSM
                @details   Implements a finite state machine
            '''
        ## @brief     Starts timer
        #  @details   An increasing microsecond counter with an arbitrary reference point
            current_time = utime.ticks_us()
    
             
            if self.state == S0_init:
                print("Welcome. Please calibrate the touch panel and IMU before balancing the ball. Press:" ,
                      "\'c\' to calibrate the touch panel,",
                      "\'C\' to calibrate the IMU,",
                      "\'b\' to balance the ball and/or platform,",
                      "\'d\' to collect state vector data.",sep="\n")
                self.state = S1_wait_for_char
                
            elif self.state == S1_wait_for_char:
                        
                if self.ser.any():
                    char_in = self.ser.read(1).decode()
                    
                    if (char_in == 'e' or char_in == 'E'):
                        self.transition_to(S7_disable)
                    
                    elif (char_in == 'c'):
                        self.transition_to(S3_calibrate_panel)
                        
                    elif (char_in == 'C'):
                        self.transition_to(S4_calibrate_IMU)
                        
                    elif (char_in == 'b'):
                        print('Ball balance commencing... ')
                        self.transition_to(S2_ball) 
                    
                    elif (char_in == 'd'):
                        ## @brief     Starts timer for data collection
                        #  @details   An increasing microsecond counter equal to current_time
                        self.collect_time = current_time
                        print('Printing state vector data... ')
                        self.transition_to(S5_collect_data) 
                    
                    else:
                        print('Command \'{:}\' is invalid.'.format(char_in))
                        pass                                                        
            
            elif self.state == S2_ball:
                 self.balance_flag.write(1)
                 self.transition_to(S1_wait_for_char)
                 
            elif self.state == S3_calibrate_panel:  
                 self.calib_pan_flag.write(1)
                 self.transition_to(S1_wait_for_char)
                 
            elif self.state == S4_calibrate_IMU:
                 self.calib_IMU_flag.write(1)
                 self.transition_to(S1_wait_for_char)                                                      
                
            elif self.state == S5_collect_data:
             ## @brief     Creates a variable that calculates difference between time reference points
             #  @details   Used to collect data for a maximum time of 30 seconds
             self.time_diff = utime.ticks_diff(current_time, self.collect_time)/1000000
             if self.time_diff <= 5:
                 
                 self.time_array[self.i] = self.time_diff
                 self.x_array[self.i] = self.state_vect_x[0].read()
                 self.thy_array[self.i] = self.state_vect_x[1].read()
                 self.xd_array[self.i] = self.state_vect_x[2].read()
                 self.thyd_array[self.i] = self.state_vect_x[3].read()
                 
                 self.y_array[self.i] = self.state_vect_y[0].read()
                 self.thx_array[self.i] = self.state_vect_y[1].read()
                 self.yd_array[self.i] = self.state_vect_y[2].read()
                 self.thxd_array[self.i] = self.state_vect_y[3].read()
                 
                 self.i += 1                   
                 
                 if self.ser.any():
                     char_in = self.ser.read(1).decode()
                     if(char_in == 's' or 'S'):
                        self.transition_to(S6_print_data)
             else:
                     self.transition_to(S6_print_data)
                     
                     
            elif self.state == S6_print_data:
                for number in range(self.i):
                     print(str(round(self.time_array[number], 2)) + '[s], ' +str(round(self.x_array[number], 2)) + ' x pos [mm], ' + str(round(self.thy_array[number], 2)) + ' theta_y [deg], ' + str(round(self.xd_array[number], 2)) + ' x-vel [mm/s],' + str(round(self.thyd_array[number], 2)) + ' ang vel(y) [deg/s],' + 
                          str(round(self.y_array[number], 2)) + ' y pos [mm], ' + str(round(self.thx_array[number], 2)) + ' theta_x [deg], ' + str(round(self.yd_array[number], 2)) + ' y-vel [mm/s],' + str(round(self.thxd_array[number], 2)) + ' ang vel(x) [deg/s]')

#                    Use the code below to print data values without units (for ease of plotting)
#                    print(str(round(self.time_array[number], 2)) + ', ' + str(round(self.x_array[number], 2)) + ', ' + str(round(self.thy_array[number], 2)) + ', ' + str(round(self.xd_array[number], 2)) + ', ' + str(round(self.thyd_array[number], 2)) + ', ' +
#                          str(round(self.y_array[number], 2)) + ', ' + str(round(self.thx_array[number], 2)) + ', ' + str(round(self.yd_array[number], 2)) + ', ' + str(round(self.thxd_array[number], 2)))  
            
                else:
                    print('Finished collecting data.')
                    self.transition_to(S0_init)
                    
            elif self.state == S7_disable:
                self.disable_flag.write(1)
                print('Motors disabled. Press b to recommence balancing.')
                self.transition_to(S1_wait_for_char)    
                                 
            else:
                    raise ValueError('Invalid State.')         

            
    def transition_to(self, new_state):
        ''' @brief            Transitions the FSM to a new state
            @details          A function that transitions the FSM to a new state
            @param new_state  The state to transition to
        '''
        self.state = new_state
        

            