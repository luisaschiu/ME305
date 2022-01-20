'''@file        task_motor.py
   @brief       Motor task reponsible for motor control.
   @details     Implements a finite state machine that interacts with the motor and task user interface.
   @author      Faith Chau
   @author      Luisa Chiu
   @date        November 2, 2021
   \image html  Lab4_TaskMotor.png "Lab 4 Task Motor FSM"
'''

import utime
import closedloop

## @brief     State 1 of the motor task
#  @details   Creates an initial state condition for state 1. State 1 is the enable state.
S1_RUN = 2
## @brief     State 2 of the motor task
#  @details   Creates an initial state condition for state 2. State 2 is the disable state.
S2_STOP = 1
## @brief     State 3 of the motor task
#  @details   Creates an initial state condition for state 3. State 3 is the fault alert state.
S3_FAULT = 3
## @brief     State 4 of the motor task
#  @details   Creates an initial state condition for state 4. State 4 is the clear fault state.
S4_CLEAR_FAULT = 4
## @brief     State 5 of the motor task
#  @details   Creates an initial state condition for state 5. State 5 is the step response state.
S5_STEP_RESPONSE = 5

class Task_Motor():
    ''' @brief      Motor task that creates variables for motor driver functions and parameters
        @details    Implements a finite state machine for the motor driver
    '''
    
    
    def __init__(self, period, motor_obj, motor_drv, fault_user_flag, enable_flag, step_flag, gain, L, inp_vel, meas_vel):
        ''' @brief                   Constructs a motor task
            @details                 The motor task is implemented as a finite state machine.
            @param period            The period, in microseconds, between runs of the task
            @param motor_obj         The motor object that calls motors 1 or 2
            @param motor_drv         The motor driver object that calls DRV8847
            @param fault_user_flag   A boolean flag used to alert user of fault for a corresponding motor
            @param enable_flag       A boolean flag used to enable a corresponding motor
            @param step_flag         A boolean flag used to start step response
            @param gain              Variable that defines gain value
            @param L                 Variable used to define actuation level
            @param inp_vel           Variable that defines input velocity
            @param meas_vel          Variable that defines measured velocity
    '''
        
        ## @brief     A boolean flag used to alert user of fault for a corresponding motor
        #  @details   Used to indicate fault in user interface
        self.fault_user_flag = fault_user_flag
        ## @brief     A boolean flag used to enable a corresponding motor
        #  @details   Used to communicate enable function between driver, motor task, and user task        
        self.enable_flag = enable_flag
        ## @brief     The motor object that calls motors 1 or 2
        #  @details   Motors 1 or 2 were defined in the main.py file  
        self.motor_obj = motor_obj
        ## @brief     The motor driver object that calls DRV8847
        #  @details   This motor driver was defined in the main.py file
        self.motor_drv = motor_drv
        ## @brief     Variable that defines gain value
        #  @details   Also known as Kp, or proportional gain 
        self.gain = gain
        ## @brief     Variable used to define actuation level
        #  @details   This value is calculated using gain, measured angular velocity, and reference angular velocity
        self.L = L
        ## @brief     Variable that defines input velocity
        #  @details   This is the reference velocity inputted by the user
        self.inp_vel = inp_vel
        ## @brief     Variable that defines measured velocity
        #  @details   Takes the measured delta values from the encoder and divides by the period to obtain measured velocity
        self.meas_vel = meas_vel
        ## @brief     A boolean flag used to start step response
        #  @details   Works with the motor task and user interface to communicate step function performance
        self.step_flag = step_flag     
        ## @brief     The frequency of the task
        #  @details   Defines variable that specifies timer frequency
        self.period = 20000
        ## @brief     Initializes starting state to be state 2
        #  @details   Motors begin in the stop state
        self.state = S2_STOP
        ## @brief     Sets the number of runs to 0
        #  @details   Defines a variable to keep track of runs
        self.runs = 0
        ## @brief     The utime.ticks_us() value associated with the next run of the FSM
        #  @details   Defines a variable that adds the period to the ongoing timer        
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period)
        ## @brief     The controller object that refers to closedloop.py
        #  @details   Creates the controller object used to perform closed loop speed control of the motors
        self.controller = closedloop.ClosedLoop(inp_vel, meas_vel, 100, -100, L, gain)
        
    def run(self):
        ''' @brief Runs one iteration of the FSM
        '''
        ## @brief     Starts timer
        #  @details   An increasing microsecond counter with an arbitrary reference point
        current_time = utime.ticks_us() 
        if (utime.ticks_diff(current_time, self.next_time) >= 0):
            
            if self.state == S1_RUN:
                
                if self.motor_drv == None:
                   self.motor_obj.set_duty(self.L.read())
                   
                   if self.step_flag.read() == 1:
                      self.transition_to(S5_STEP_RESPONSE) 
                      pass
                  
                else:
                   self.motor_drv.enable()
                   self.motor_obj.set_duty(self.L.read())                  
                   
                   if self.enable_flag.read() == 0:
                      self.transition_to(S2_STOP)            
                     
                   # When fault occurs
                   if self.motor_drv.fault_cb_flag == 1:
                      self.transition_to(S3_FAULT)

                   if self.step_flag.read() == 1:
                      self.transition_to(S5_STEP_RESPONSE)                          
                                            
                    
            # This is the state our motors start in
            if self.state == S2_STOP:
                   
                   if self.motor_drv == None:
                      self.transition_to(S1_RUN)
                      pass                   
                  
                   else:
                       if self.enable_flag.read() == 0:
                          self.motor_drv.disable()   
                                                                               
                       if self.enable_flag.read() == 1:
                          self.fault_user_flag.write(0)
                          self.transition_to(S1_RUN)                                                 
                          
            if self.state == S3_FAULT:
                  if self.motor_drv == None:
                      self.transition_to(S1_RUN)
                      pass
                   
                  else:
                       self.motor_drv.disable() 
                       self.enable_flag.write(0)
                       self.fault_user_flag.write(1)
                       self.transition_to(S4_CLEAR_FAULT)
          
            if self.state == S4_CLEAR_FAULT:            
               
               if self.fault_user_flag.read() == 0: #if fault_user is cleared by user, set fault_cb = 0
                          self.motor_drv.fault_cb_flag = 0
                          print('Fault cleared!') 
                          self.transition_to(S2_STOP)
                          
            if self.state == S5_STEP_RESPONSE:
               self.controller.run()
               if self.motor_drv == None:
                   self.motor_obj.set_duty(self.L.read())                   
                   pass
                  
               else:
                   self.motor_obj.set_duty(self.L.read())
                   
                   if self.step_flag.read() == 0:
                      self.transition_to(S2_STOP)    
            
            self.next_time = utime.ticks_add(self.next_time, self.period)
            self.runs += 1                
                
                

    def transition_to(self, new_state):
        ''' @brief            Transitions the FSM to a new state
            @details          A function that transitions the FSM to a new state
            @param new_state  The state to transition to
        '''
        self.state = new_state