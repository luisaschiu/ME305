'''@file        task_motor.py
   @brief       Motor task reponsible for motor control.
   @details     Implements a finite state machine that interacts with the motor and task user interface.
   @author      Faith Chau
   @author      Luisa Chiu
   @date        December 9, 2021
   \image html  LabFF_TaskMotor.png "Lab FF Task Motor FSM"
'''

#from ulab import numpy as np
#import closedloop

## @brief     State 1 of the motor task
#  @details   Creates an initial state condition for state 1. State 1 is the enable state.
S1_RUN = 2
## @brief     State 2 of the motor task
#  @details   Creates an initial state condition for state 2. State 2 is the disable state.
S2_BALANCE = 1
## @brief     State 3 of the motor task
#  @details   Creates an initial state condition for state 3. State 3 is the fault alert state.
S3_DISABLE = 3


class Task_Motor():
    ''' @brief      Motor task that creates variables for motor driver functions and parameters
        @details    Implements a finite state machine for the motor driver
    '''
    
    
    def __init__(self, period_motor, motor_obj, motor_drv, L, balance_flag, state_vect_x, state_vect_y, disable_flag, closedloop):
        ''' @brief                   Constructs a motor task
            @details                 The motor task is implemented as a finite state machine.
            @param period            The period, in microseconds, between runs of the task
            @param motor_obj         The motor object that calls motors 1 or 2
            @param motor_drv         The motor driver object that calls DRV8847
            @param enable_flag       A boolean flag used to enable a corresponding motor
            @param step_flag         A boolean flag used to start step response
            @param L                 Variable used to define actuation level
    '''
    
        ## @brief     The motor object that calls motors 1 or 2
        #  @details   Motors 1 or 2 were defined in the main.py file  
        self.motor_obj = motor_obj
        ## @brief     The motor driver object that calls DRV8847
        #  @details   This motor driver was defined in the main.py file
        self.motor_drv = motor_drv
        ## @brief     Variable used to define actuation level
        #  @details   This value is calculated using gain, measured angular velocity, and reference angular velocity
        self.L = L
        ## @brief     A boolean flag used to start balancing the platform and/or ball
        #  @details   Works with the motor task and user interface to implement closed-loop control that balances the platform and ball   
        self.balance_flag = balance_flag
        ## @brief     A boolean flag used to disable motors
        #  @details   Works with the motor task and user interface to halt motor movement
        self.disable_flag = disable_flag
        ## @brief     A shared list used to define state vector x
        #  @details   Contains variables for x position, theta y, x velocity, and angular velocity (theta y dot)
        self.state_vect_x = state_vect_x
        ## @brief     A shared list used to define state vector y
        #  @details   Contains variables for y position, theta x, y velocity, and angular velocity (theta x dot)
        self.state_vect_y = state_vect_y
        ## @brief     The frequency of the task
        #  @details   Defines variable that specifies timer frequency
        self.period_motor = period_motor
        ## @brief     Initializes starting state to be state 2
        #  @details   Motors begin in the stop state
        self.state = S1_RUN
        ## @brief     Sets the number of runs to 0
        #  @details   Defines a variable to keep track of runs
        self.runs = 0
        ## @brief     The controller object that refers to closedloop.py
        #  @details   Creates the controller object used to perform closed loop speed control of the motors
        self.closedloop = closedloop

        
    def run(self):
        ''' @brief Runs one iteration of the FSM
        '''
       
        if self.state == S1_RUN:                                         
                                                         
                if self.balance_flag.read() == 1:
                   self.transition_to(S2_BALANCE)     
                      
                   
                    
        if self.state == S2_BALANCE:
            
              self.closedloop.run()      
              if self.motor_drv == None:
                 self.motor_obj.set_duty(self.L.read())                   

                  
              else:
                  self.motor_obj.set_duty(self.L.read())
                  
                  if self.disable_flag.read() == 1:
                      self.transition_to(S3_DISABLE)
                  

                  
#               else:
#                   self.gains_x = np.array([-0.026, -0.026, -0.005, 0.006]) #X-GAINS
#                   self.state_vect_x_array = np.array([self.state_vect_x[0].read(), self.state_vect_x[1].read(), self.state_vect_x[2].read(), self.state_vect_x[3].read()])
#                   self.Torque_x = np.dot(-self.gains_x,self.state_vect_x_array)
#                   self.L.write((13.345)*self.Torque_x*100/4)
#                   if self.L.read() > 80:
#                      self.L.write(80)
#                   if self.L.read() < -80:
#                      self.L.write(-80)
#                   self.motor_obj.set_duty(self.L.read())
#                   
#                   if self.disable_flag.read() == 1:
#                      self.transition_to(S3_DISABLE)
                           
        if self.state == S3_DISABLE:
            if self.motor_drv == None:
                 self.motor_obj.set_duty(0)
                 self.disable_flag.write(0)
                 self.transition_to(S1_RUN)
            else:
                 self.motor_obj.set_duty(0)
                 self.disable_flag.write(0)
                 self.transition_to(S1_RUN)
                                            
                

    def transition_to(self, new_state):
        ''' @brief            Transitions the FSM to a new state
            @details          A function that transitions the FSM to a new state
            @param new_state  The state to transition to
        '''
        self.state = new_state