'''@file        task_panel.py
   @brief       Responsible for interfacing with the touch panel using the panel object
   @details     Implements a finite state machine that interacts with touch panel driver
   @author      Faith Chau
   @author      Luisa Chiu
   @date        December 9, 2021
   \image html  LabFF_TaskPanel.png "Lab FF Task Panel TSM"
'''
    
import utime

S0_INIT = 0

S1_POSITION = 1
 
S2_VELOCITY = 2

S3_CALIBRATE = 3

class Task_Panel():
    ''' @brief      Touch panel task responsible for interfacing with the touch panel using the panel object
        @details    Implements a finite state machine for touch panel
    '''
    

   
    def __init__(self, period_pan, panel_obj, state_vect_x, state_vect_y, calib_pan_flag):
        ''' @brief                   Constructs a touch panel task
            @details                 Touch panel task attributes include the period, panel object, state vectors, and panel flag for calibration
            @param period_pan        The period, in microseconds, between runs of the panel task
            @param panel_obj         The panel object of the touch panel driver class
            @param state_vect_x      List used to define state vector x
            @param state_vect_y      List used to define state vector y
            @param calib_pan_flag    A boolean flag used to enable touch panel calibration
        '''
        ## @brief     The frequency of the panel task
        #  @details   Variable that specifies timer frequency
        self.period_pan = period_pan
        ## @brief     The panel driver object
        #  @details   This panel driver was defined in the main.py file
        self.panel_obj = panel_obj
        ## @brief     A boolean flag used to start touch panel calibration
        #  @details   Works with the task panel and user interface to enable resistive touch panel calibration
        self.calib_pan_flag = calib_pan_flag
        ## @brief     A shared list used to define state vector x
        #  @details   Contains variables for x position, theta y, x velocity, and angular velocity (theta y dot)
        self.state_vect_x = state_vect_x
        ## @brief     A shared list used to define state vector y
        #  @details   Contains variables for y position, theta x, y velocity, and angular velocity (theta x dot)
        self.state_vect_y = state_vect_y
        ## @brief     Sets initial state to State 0
        #  @details   FSM starts at State 0, where user input is prompted for further action    
        self.state = 0        
        ## @brief     Sets the number of runs to 0
        #  @details   Defines a variable to keep track of runs
        self.runs = 0     
        ## @brief     The utime.ticks_us() value associated with the next run of the FSM
        #  @details   Defines a variable that adds the period to the ongoing timer
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period_pan)
        ## @brief     Initializes x position variable
        #  @details   Continuously updated to calculate positional velocity in x-direction
        self.first_pos_x = 0
        ## @brief     Initializes y position variable
        #  @details   Continuously updated to calculate positional velocity in y-direction
        self.first_pos_y = 0
        
    def run(self):
        ''' @brief Runs one iteration of the FSM
        '''
        current_time = utime.ticks_us()
        if (utime.ticks_diff(current_time, self.next_time) >= 0):
            
            if self.state == S0_INIT:
                
                if self.calib_pan_flag.read() == 1:
                    self.transition_to(S3_CALIBRATE)
                
                else:
                    if self.runs == 0:
                        #Initializes velocity calculations
                        self.positions = self.panel_obj.get_coords()
                        self.first_pos_x = self.positions[0]
                        self.first_pos_y = self.positions[1]
                        
                    else:
                        #Runs get.coords() to obtain touch panel readings
                        ## @brief     Object associated with position read by touch panel
                        #  @details   Uses panel object to update state vectors
                        self.positions = self.panel_obj.get_coords()        
                        
                        #Reads ball position on touch panel when contact is made
                        self.state_vect_x[0].write(self.positions[0])
                        self.state_vect_y[0].write(self.positions[1])
                        
                        #Continues velocity calculations
                        ## @brief     Defines x position variable read after position changes
                        #  @details   Continuously updated to calculate positional velocity in x-direction
                        self.second_pos_x = self.positions[0]         
                        ## @brief     Defines y position variable read after position changes
                        #  @details   Continuously updated to calculate positional velocity in y-direction                            
                        self.second_pos_y = self.positions[1]  
                        ## @brief     Calculates x velocity after position changes
                        #  @details   Change in x position over task period
                        self.x_velocity = (self.second_pos_x - self.first_pos_x)/self.period_pan
                        ## @brief     Calculates y velocity after position changes
                        #  @details   Change in y position over task period
                        self.y_velocity = (self.second_pos_y - self.first_pos_y)/self.period_pan

                        self.first_pos_x = self.second_pos_x
                        self.first_pos_y = self.second_pos_y
                        self.state_vect_x[2].write(self.x_velocity)
                        self.state_vect_y[2].write(self.y_velocity)
     
        
            if self.state == S3_CALIBRATE:
                #Runs calibrate() function
                self.panel_obj.calibrate()
                self.calib_pan_flag.write(0)
                self.runs = 0
                self.transition_to(S0_INIT)
           
        self.runs += 1 
        self.next_time = utime.ticks_add(self.next_time, self.period_pan)      
            

    def transition_to(self, new_state):
        ''' @brief            Transitions the FSM to a new state
            @details          A function that transitions the FSM to a new state
            @param new_state  The state to transition to
        '''
        self.state = new_state                        
