''' @file       Lab2_task_encoder.py
    @brief      Encoder task for updating the encoder object.
    @details    Implements a finite state machine that interacts with the encoder driver and task user interface
    @author     Faith Chau
    @author     Luisa Chiu
    @date       October 19, 2021
    \image html  Lab2_TaskEncoder_FSM.png "Task Encoder FSM"
'''

import utime

## @brief     State 1 of the user interface task
#  @details   Creates an initial state condition for state 1
S1_UPDATE = 0

class Task_Encoder():
    ''' @brief      Encoder task for cooperative multitasking example.
        @details    Implements a finite state machine that interacts with the encoder driver and task user interface

    '''
    def __init__(self, period, enc_pos, z_flag, enc_delta, enc_obj, my_Q):
        ''' @brief              Constructs an encoder task
            @details            The encoder task is implemented as a finite state machine
            @param period       The period, in microseconds, between runs of the task
            @param enc_pos      The encoder position that counts total movement
            @param z_flag       A boolean flag used to reset encoder position to 0
            @param enc_delta    The change in time increments in timer count
            @param enc_obj      The encoder object that calls encoders 1 or 2
            @param my_Q         A shares object that represents the queue for holding list items
        '''
        ## @brief     The frequency of the task
        #  @details   Defines variable that specifies timer frequency
        self.period = 150000
        ## @brief     The encoder position that counts total movement
        #  @details   The total position moved is characterized by the total number of timer counts
        self.enc_pos = enc_pos
        ## @brief     A boolean flag used to reset encoder position to 0
        #  @details   When character "z" is pressed on the keyboard, z-flag will be 'True' and reset encoder position
        self.z_flag = z_flag
        ## @brief     A shares object that represents the queue for holding list items
        #  @details   The queue holds the time and position list items.
        self.my_Q = my_Q
        ## @brief    The encoder object that calls encoders 1 or 2
        #  @details  Encoders 1 or 2 was defined in the main.py file
        self.enc_obj = enc_obj
        ## @brief     The change in position
        #  @details   The difference between two recorded positions of the encoder
        self.enc_delta = enc_delta
        ## @brief     Sets initial state to State 1
        #  @details   FSM starts at State 1, where the update function is called for encoder object
        self.state = S1_UPDATE
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
            if self.state == S1_UPDATE:
               self.enc_obj.update()
               self.enc_pos.write(self.enc_obj.get_position())
               self.enc_delta.write(self.enc_obj.get_delta())
               
            if self.z_flag.read() == 1:
                self.enc_obj.set_position(0)
                self.enc_obj.update()
                self.enc_pos.write(self.enc_obj.get_position())
                self.enc_delta.write(self.enc_obj.get_delta())
                self.z_flag.write(0)
            
            self.next_time = utime.ticks_add(self.next_time, self.period)
            self.runs += 1
            
                
                
                
                
                
                
            
            