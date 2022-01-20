'''@file        task_motor.py
   @brief       Motor task reponsible for motor control.
   @details     Implements a finite state machine that interacts with the motor and task user interface.
   @author      Faith Chau
   @author      Luisa Chiu
   @date        November 2, 2021
   \image html  Lab3_TaskMotor.png "Lab 3 Task Motor FSM"
   \image html  Lab3_Motor1_Plot.png "Lab 3 Motor 1 Plot"
   \image html  Lab3_Motor2_Plot.png "Lab 3 Motor 2 Plot"
'''

import utime
import shares

dutycycle_1 = shares.Share(0)
dutycycle_2 = shares.Share(0)

## @brief     State 1 of the motor task
#  @details   Creates an initial state condition for state 1. State 1 is the enable state.
S1_RUN = 2
## @brief     State 2 of the motor task
#  @details   Creates an initial state condition for state 2. State 2 is the disabled state.
S2_STOP = 1
## @brief     State 3 of the motor task
#  @details   Creates an initial state condition for state 3. State 3 is the fault alert state.
S3_FAULT = 3
## @brief     State 4 of the motor task
#  @details   Creates an initial state condition for state 4. State 4 is the clear fault state.
S4_CLEAR_FAULT = 4


class Task_Motor():
    ''' @brief      Motor task that creates variables for motor driver functions and parameters
        @details    Implements a finite state machine for lab 3
    '''
    def __init__(self, period, motor_obj, motor_drv, fault_user_flag, enable_flag, dutycycle):
        ''' @brief                   Constructs a motor task
            @details                 The motor task is implemented as a finite state machine.
            @param period            The period, in microseconds, between runs of the task
            @param motor_obj         The motor object that calls motors 1 or 2
            @param motor_drv         The motor driver object that calls DRV8847
            @param fault_user_flag   A boolean flag used to alert user of fault for a corresponding motor
            @param enable_flag       A boolean flag used to enable a corresponding motor
            @param dutycycle         A variable that defines duty cycle for a corresponding motor
    '''
        
        ## @brief     A boolean flag used to alert user of fault for a corresponding motor
        #  @details   Used to indicate fault in user interface
        self.fault_user_flag = fault_user_flag
        ## @brief     A boolean flag used to enable a corresponding motor
        #  @details   Used to communicate enable function between driver, motor task, and user task        
        self.enable_flag = enable_flag
        ## @brief     A variable that defines duty cycle for a corresponding motor
        #  @details   Duty cycle values control motor speed
        self.dutycycle = dutycycle
        ## @brief     The motor object that calls motors 1 or 2
        #  @details   Motors 1 or 2 were defined in the main.py file  
        self.motor_obj = motor_obj
        ## @brief     The motor driver object that calls DRV8847
        #  @details   This motor driver was defined in the main.py file
        self.motor_drv = motor_drv
        ## @brief     The frequency of the task
        #  @details   Defines variable that specifies timer frequency
        self.period = 30000
        ## @brief     Initializes starting state to be state 2
        #  @details   Motors begin in the stop state
        self.state = S2_STOP
        ## @brief     Sets the number of runs to 0
        #  @details   Defines a variable to keep track of runs
        self.runs = 0
        ## @brief     The utime.ticks_us() value associated with the next run of the FSM
        #  @details   Defines a variable that adds the period to the ongoing timer        
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period)
        
        
    def run(self):
        ''' @brief Runs one iteration of the FSM
        '''
        current_time = utime.ticks_us() 
        if (utime.ticks_diff(current_time, self.next_time) >= 0):
            
            if self.state == S1_RUN:
                
                if self.motor_drv == None:
                   self.motor_obj.set_duty(self.dutycycle.read())
                   pass
                  
                else:
                   self.motor_drv.enable()
                   
                   self.motor_obj.set_duty(self.dutycycle.read())
                   
                   if self.enable_flag.read() == 0:
                      self.transition_to(S2_STOP)
                      
                     
                   # When fault occurs
                   if self.motor_drv.fault_cb_flag == 1:
                      self.transition_to(S3_FAULT)                                           
                                            
                    
            # This is the state our motors start in
            if self.state == S2_STOP:
                   
                   if self.motor_drv == None:
                      self.transition_to(S1_RUN)
                      pass                   
                   else:
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

            self.next_time = utime.ticks_add(self.next_time, self.period)
            self.runs += 1                
                
                

    def transition_to(self, new_state):
        ''' @brief            Transitions the FSM to a new state
            @details          A function that transitions the FSM to a new state
            @param new_state  The state to transition to
        '''
        self.state = new_state