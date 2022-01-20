''' @file       Lab2_task_userinterface.py
    @brief      User interface task for cooperative multitasking example.
    @details    Implements a finite state machine that runs a data collection interface to interact with the encoder object.
    @author     Faith Chau
    @author     Luisa Chiu
    @date       October 19, 2021
    \image html  Lab2_TaskUser_FSM.png "Task User FSM"
'''
import utime
import pyb

## @brief     State 0 of the user interface task
#  @details   Creates an initial state condition for state 0.
S0_init = 0

## @brief     State 1 of the user interface task
#  @details   Creates an initial state condition for state 1. State 1 waits for user input.
S1_wait_for_char = 1

## @brief      State 2 of the user interface task
#  @details    Creates an initial state condition for state 2. State 2 collects and stores time and encoder position data.
S2_collect_data = 2

## @brief     State 3 of the user interface task
#  @details   Creates an initial state condition for state 3. State 3 prints time and encoder position data.
S3_print_data = 3


class Task_User():
    ''' @brief      User interface task for data collection and interaction with encoder object
        @details    Implements a finite state machine that runs a data collection interface to interact with the encoder object.
    '''    
    def __init__(self, period, enc_pos, z_flag, enc_delta, my_Q):
        ''' @brief              Constructs the user interface task
            @details            The user task is implemented as a finite state machine that takes in character input from the user and obtains information from the encoder task to present to user.
            @param period       The period, in microseconds, between runs of the task
            @param enc_pos      The encoder position that counts total movement
            @param z_flag       A boolean flag used to reset encoder position to 0
            @param enc_delta    The change in time increments in timer count
            @param my_Q         A shares object that represents the queue for holding list items
        '''
        ## @brief     The frequency of the task
        #  @details   Defines variable that specifies timer frequency
        self.period = 150000
        ## @brief     The encoder position that counts total movement
        #  @details   The total position moved is characterized by the total number of timer counts
        self.enc_pos = enc_pos
        ## @brief     The change in position
        #  @details   The difference between two recorded positions of the encoder
        self.enc_delta = enc_delta
        ## @brief     A boolean flag used to reset encoder position to 0
        #  @details   When character "z" is pressed on the keyboard, z-flag will be 'True' and reset encoder position
        self.z_flag = z_flag
        ## @brief     A shares object that represents the queue for holding list items
        #  @details   The queue holds the time and position list items.
        self.my_Q = my_Q
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
        #  @details   Create a new USB_VCP object
        self.ser = pyb.USB_VCP()
        
    def run(self):
        ''' @brief     Runs one iteration of the FSM
            @details   Implements a finite state machine
        '''
        ## @brief     Starts timer
        #  @details   An increasing microsecond counter with an arbitrary reference point
        current_time = utime.ticks_us()
        if (utime.ticks_diff(current_time, self.next_time) >= 0):
            if self.state == S0_init:
                print("Welcome, press:" ,
                      "\'z\' to zero the position of the encoder,",
                      "\'p\' to print out the position of the encoder,",
                      "\'d\' to print out the delta for the encoder,",
                      "\'g\' to collect encoder data for 30 seconds and print it to PuTTY as a comma separated list,",
                      "\'s\' to end data collected prematurely.", sep="\n")
                self.state = S1_wait_for_char
            elif self.state == S1_wait_for_char:
                 if self.ser.any():
                    char_in = self.ser.read(1).decode()
                    if(char_in == 'z' or char_in == 'Z'):        
                        self.z_flag.write(1)
                        ## @brief     Variable that defines encoder position shared item
                        #  @details   Allows encoder position data to be accessed                      
                        reset_pos= self.enc_pos.read()
                        self.enc_pos.write(reset_pos)
                        print('Encoder position successfully reset')
                    elif(char_in == 'p' or char_in == 'P'):
                        print(self.enc_pos.read())
                    elif(char_in == 'd' or char_in == 'D'):
                        print(self.enc_delta.read())
                    elif(char_in == 'g' or char_in == 'G'):
                        ## @brief     Assigns an arbitrary reference point that begins when 'g' is pressed
                        #  @details   Used to implement the timed data collection period
                        self.collect_time = current_time  
                        self.transition_to(S2_collect_data)
                    else:
                        print('Command \'{:}\' is invalid.'.format(char_in))
    
            elif self.state == S2_collect_data:
                 ## @brief     Creates a variable that calculates difference between time reference points
                 #  @details   Used to collect data for a maximum time of 30 seconds
#                 self.time_diff = (current_time - self.collect_time)/1000000
                 self.time_diff = utime.ticks_diff(current_time, self.collect_time)/1000000
                 if self.time_diff <= 30:    
                     ## @brief     Creates a tuple that holds time and position data
                     #  @details   Used to store all data collected into queue
                     self.my_tuple = (self.time_diff,self.enc_pos.read())
                     self.my_Q.put(self.my_tuple)
                 

                     if self.ser.any():
                         char_in = self.ser.read(1).decode()
                         if(char_in == 's' or char_in == 'S'):
                            self.transition_to(S3_print_data) 
                                 
                 else:
                     self.transition_to(S3_print_data) 
                         
            elif self.state == S3_print_data:
                 if (self.my_Q.num_in()>0):
                         print(self.my_Q.get())     
                 
                 else:                     
                     print('Finished collecting data.')
                     self.transition_to(S0_init) 
                 
            else:
                raise ValueError('Invalid State')
            
            self.next_time = utime.ticks_add(self.next_time, self.period)
            self.runs += 1
            
    def transition_to(self, new_state):
        ''' @brief            Transitions the FSM to a new state
            @details          A function that transitions the FSM to a new state
            @param new_state  The state to transition to
        '''
        self.state = new_state
            