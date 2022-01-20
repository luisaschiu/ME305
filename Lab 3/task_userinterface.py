''' @file        task_userinterface.py
    @brief       User interface task for cooperative multitasking example.
    @details     Implements a finite state machine that runs a data collection interface to interact with the encoder object.
    @author      Faith Chau
    @author      Luisa Chiu
    @date        October 19, 2021
    \image html  Lab3_TaskUser_FSM.png "Lab 3 Task User FSM"
'''
import utime
import pyb
import math
import array

## @brief     State 0 of the user interface task
#  @details   Creates an initial state condition for state 0.
S0_init = 0

## @brief     State 1 of the user interface task
#  @details   Creates an initial state condition for state 1. This state waits for user input.
S1_wait_for_char = 1

## @brief      State 2 of the user interface task
#  @details    Creates an initial state condition for state 2. State 2 collects and stores time and encoder 1 position data.
S2_collect_data_1 = 2

## @brief      State 3 of the user interface task
#  @details    Creates an initial state condition for state 3. State 3 collects and stores time and encoder 2 position data.
S3_collect_data_2 = 3

## @brief     State 4 of the user interface task
#  @details   Creates an initial state condition for state 4. State 4 prints time, position, and delta for encoder 1.
S4_print_data_1 = 4

## @brief     State 5 of the user interface task
#  @details   Creates an initial state condition for state 5. State 5 prints time, position, and delta for encoder 2.
S5_print_data_2 = 5

## @brief     State 6 of the user interface task
#  @details   Creates an initial state condition for state 6. State 6 sets encoder 1 position to zero.
S6_zero_enc_1 = 6

## @brief     State 7 of the user interface task
#  @details   Creates an initial state condition for state 7. State 7 sets encoder 2 position to zero.
S7_zero_enc_2 = 7

## @brief     State 8 of the user interface task
#  @details   Creates an initial state condition for state 8. State 8 prints encoder 1 position data.
S8_print_enc_pos_1 = 8

## @brief     State 9 of the user interface task
#  @details   Creates an initial state condition for state 9. State 9 prints encoder 2 position data.
S9_print_enc_pos_2 = 9

## @brief     State 10 of the user interface task
#  @details   Creates an initial state condition for state 10. State 10 prints encoder 1 delta.
S10_print_enc_delta_1 = 10

## @brief     State 11 of the user interface task
#  @details   Creates an initial state condition for state 11. State 11 prints encoder 2 delta.
S11_print_enc_delta_2 = 11

## @brief     State 12 of the user interface task
#  @details   Creates an initial state condition for state 12. State 12 enables motors 1 and 2.
S12_enable = 12

## @brief     State 13 of the user interface task
#  @details   Creates an initial state condition for state 13. State 13 prompts user input for duty cycle 1.
S13_prompt_duty_cycle_1 = 13

## @brief     State 14 of the user interface task
#  @details   Creates an initial state condition for state 14. State 14 prompts user input for duty cycle 2.
S14_prompt_duty_cycle_2 = 14

## @brief     State 15 of the user interface task
#  @details   Creates an initial state condition for state 15. State 15 alerts user of a fault condition.
S15_fault_occurs = 15

## @brief     State 16 of the user interface task
#  @details   Creates an initial state condition for state 16. State 16 tells user that the fault condition is cleared.
S16_fault_cleared = 16

class Task_User():
    ''' @brief      User interface task for data collection and interaction with encoder object
        @details    Implements a finite state machine that runs a data collection interface to interact with the encoder object.
    '''    
    def __init__(self, period, enc_pos_1, enc_pos_2, z_flag_1, z_flag_2, fault_user_flag, enable_flag, enc_delta_1, enc_delta_2, dutycycle_1, dutycycle_2):
        ''' @brief                  Constructs the user interface task
            @details                The user task is implemented as a finite state machine that takes in character input from the user and obtains information from the encoder task to present to user.
            @param period           The period, in microseconds, between runs of the task
            @param enc_pos_1        The encoder position that counts total movement for encoder 1
            @param enc_pos_2        The encoder position that counts total movement for encoder 2
            @param z_flag_1         A boolean flag used to reset encoder 1 position to 0 
            @param z_flag_2         A boolean flag used to reset encoder 2 position to 0 
            @param fault_user_flag  A boolean flag used to alert user of fault for a corresponding motor
            @param enable_flag      A boolean flag used to enable a corresponding motor
            @param enc_delta_1      The change in time increments in timer count for encoder 1
            @param enc_delta_2      The change in time increments in timer count for encoder 2
            @param dutycycle_1      A variable that defines duty cycle for motor 1
            @param dutycycle_2      A variable that defines duty cycle for motor 2
        '''
        ## @brief     The frequency of the task
        #  @details   Defines variable that specifies timer frequency
        self.period = 30000
        ## @brief     The encoder 1 position that counts total movement
        #  @details   The total position moved is characterized by the total number of timer counts
        self.enc_pos_1 = enc_pos_1
        ## @brief     The encoder 2 position that counts total movement
        #  @details   The total position moved is characterized by the total number of timer counts        
        self.enc_pos_2 = enc_pos_2
        ## @brief     The change in encoder 1 position
        #  @details   The difference between two recorded positions of the encoder
        self.enc_delta_1 = enc_delta_1
        ## @brief     The change in encoder 2 position
        #  @details   The difference between two recorded positions of the encoder        
        self.enc_delta_2 = enc_delta_2
        ## @brief     A boolean flag used to reset encoder 1 position to 0
        #  @details   When character "z" is pressed on the keyboard, z-flag will be 'True' and reset encoder 1 position
        self.z_flag_1 = z_flag_1
        ## @brief     A boolean flag used to reset encoder 2 position to 0
        #  @details   When character "z" is pressed on the keyboard, z-flag will be 'True' and reset encoder 2 position
        self.z_flag_2 = z_flag_2
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
        ## @brief     A boolean flag used to alert user of fault for motors
        #  @details   Used to indicate fault in user interface
        self.fault_user_flag = fault_user_flag
        ## @brief     A boolean flag used to enable motor 1
        #  @details   Used to communicate enable function between driver, motor task, and user task
        self.enable_flag = enable_flag
        ## @brief     A variable that defines duty cycle for motor 1
        #  @details   Duty cycle values control motor speed
        self.dutycycle_1 = dutycycle_1
        ## @brief     A variable that defines duty cycle for motor 2
        #  @details   Duty cycle values control motor speed
        self.dutycycle_2 = dutycycle_2
        ## @brief     A variable used to initialize the user input
        #  @details   This string is what the user sees for motor 1 input
        self.num_str_1 = ''  
        ## @brief     A variable used to initialize the user input
        #  @details   This string is what the user sees for motor 2 input
        self.num_str_2 = ''  
        ## @brief     A variable used for indexing
        #  @details   This value helps index data points for time, position, and delta
        self.i = 0
        ## @brief     A variable that is created in preparation for the time array for motor 1
        #  @details   This variable creates an empty array of 1000 data points, which will be populated later with time data
        self.time_array_1 = array.array('f', 1000*[0])
        ## @brief     A variable that is created in preparation for the time array for motor 2
        #  @details   This variable creates an empty array of 1000 data points, which will be populated later with time data 
        self.time_array_2 = array.array('f', 1000*[0])
        ## @brief     A variable that is created in preparation for the position array for motor 1
        #  @details   This variable creates an empty array of 1000 data points, which will be populated later with position data
        self.position_array_1 = array.array('f', 1000*[0])
        ## @brief     A variable that is created in preparation for the position array for motor 2
        #  @details   This variable creates an empty array of 1000 data points, which will be populated later with position data
        self.position_array_2 = array.array('f', 1000*[0])
        ## @brief     A variable that is created in preparation for the velocity array for motor 1
        #  @details   This variable creates an empty array of 1000 data points, which will be populated later with velocity data
        self.velocity_array_1 = array.array('f', 1000*[0])
        ## @brief     A variable that is created in preparation for the velocity array for motor 2
        #  @details   This variable creates an empty array of 1000 data points, which will be populated later with velocity data        
        self.velocity_array_2 = array.array('f', 1000*[0])
        

        
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
                      "\'z\' to zero the position of encoder 1,",
                      "\'Z\' to zero the position of encoder 2,",
                      "\'p\' to print out the position of encoder 1,",
                      "\'P\' to print out the position of encoder 2,",
                      "\'d\' to print out the delta for encoder 1,",
                      "\'D\' to print out the delta for encoder 2,",
                      "\'e\' or \'E\' to enable DRV8847,",
                      "\'m\' to enter a duty cycle for motor 1,",
                      "\'M\' to enter a duty cycle for motor 2,",
                      "\'c\' to clear a fault condition triggered by DR,",
                      "\'g\' to collect encoder 1 data for 30 seconds and print it to PuTTY,",
                      "\'G\' to collect encoder 2 data for 30 seconds and print it to PuTTY,",                      
                      "\'s\' to end encoder 1 data collection prematurely,",
                      "\'S\' to end encoder 2 data collection prematurely.", sep="\n")
                self.state = S1_wait_for_char
                
            elif self.state == S1_wait_for_char:
                
                if self.fault_user_flag.read() == 1:
                    self.transition_to(S15_fault_occurs)
                        
                if self.ser.any():
                    char_in = self.ser.read(1).decode()
                    
                    if(char_in == 'z'): 
                        self.transition_to(S6_zero_enc_1) 
                        
                    elif(char_in == 'Z'):  
                        self.transition_to(S7_zero_enc_2) 
                    
                    elif(char_in == 'p'):
                        self.transition_to(S8_print_enc_pos_1)                     
                        
                    elif(char_in == 'P'):
                        self.transition_to(S9_print_enc_pos_2)
                   
                    elif(char_in == 'd'):
                        self.transition_to(S10_print_enc_delta_1)
                        
                    elif(char_in == 'D'):
                        self.transition_to(S11_print_enc_delta_2)
                    
                    elif (char_in == 'e' or char_in == 'E'):
                        self.transition_to(S12_enable)
                        
                    elif(char_in == 'g'):
                        ## @brief     Assigns an arbitrary reference point that begins when 'g' is pressed
                        #  @details   Used to implement the timed data collection period
                        self.collect_time = current_time
                        print('Collecting encoder 1 data...')
                        self.transition_to(S2_collect_data_1)  
                        
                    elif(char_in == 'G'):                    
                        self.collect_time = current_time
                        print('Collecting encoder 2 data...')
                        self.transition_to(S3_collect_data_2) 
                        
                    elif (char_in == 'm'):
                        print('Input duty cycle for Motor 1: ')
                        self.transition_to(S13_prompt_duty_cycle_1) 
                        
                    elif (char_in == 'M'):
                        print('Input duty cycle for Motor 2: ')
                        self.transition_to(S14_prompt_duty_cycle_2)
                    
                    else:
                        print('Command \'{:}\' is invalid.'.format(char_in))
                                 
                        
            elif self.state == S2_collect_data_1:
                 ## @brief     Creates a variable that calculates velocity for motor 1
                 #  @details   Calculates velocity using delta values, period, and unit conversions
                 self.measured_vel_1 = (self.enc_delta_1.read()*2*math.pi/4000)/self.period*1000000
                 ## @brief     Creates a variable that calculates difference between time reference points
                 #  @details   Used to collect data for a maximum time of 30 seconds
                 self.time_diff = utime.ticks_diff(current_time, self.collect_time)/1000000
                 if self.time_diff <= 30:
                     self.time_array_1[self.i] = self.time_diff
                     self.position_array_1[self.i] = self.enc_pos_1.read()*2*math.pi/4000
                     self.velocity_array_1[self.i] = self.measured_vel_1
                     self.i += 1
                     ## @brief     A variable that creates a list of the time, position, and velocity arrays for motor 1
                     #  @details   This list combines three individual arrays
                     self.list_1 = [self.time_array_1, self.position_array_1, self.velocity_array_1]                    
                     
                     if self.ser.any():
                         char_in = self.ser.read(1).decode()
                         if(char_in == 's' or 'S'):
                            self.transition_to(S4_print_data_1)  
                 else:
                     self.transition_to(S4_print_data_1)
                     
            elif self.state == S3_collect_data_2:
                 ## @brief     Creates a variable that calculates velocity for motor 2
                 #  @details   Calculates velocity using delta values, period, and unit conversions
                 self.measured_vel_2 = (self.enc_delta_2.read()*2*math.pi/4000)/self.period*1000000
                 ## @brief     Creates a variable that calculates difference between time reference points
                 #  @details   Used to collect data for a maximum time of 30 seconds
                 self.time_diff = utime.ticks_diff(current_time, self.collect_time)/1000000
                 if self.time_diff <= 30:
                     self.time_array_2[self.i] = self.time_diff
                     self.position_array_2[self.i] = self.enc_pos_2.read()*2*math.pi/4000
                     self.velocity_array_2[self.i] = self.measured_vel_2
                     self.i += 1
                     ## @brief     A variable that creates a list of the time, position, and velocity arrays for motor 2
                     #  @details   This list combines three individual arrays
                     self.list_2 = [self.time_array_2, self.position_array_2, self.velocity_array_2]                    
                     
                     if self.ser.any():
                         char_in = self.ser.read(1).decode()
                         if(char_in == 's' or 'S'):
                            self.transition_to(S5_print_data_2)  
                 else:
                     self.transition_to(S5_print_data_2)                          

            elif self.state == S4_print_data_1:        
                for number in range(self.i):
                    print(str(round(self.time_array_1[number], 2)) + ' s, ' + str(round(self.position_array_1[number], 2)) + ' rad, ' + str(round(self.velocity_array_1[number], 2)) + ' rad/s')                         
                else:     
                    print('Finished collecting encoder 1 data.') 
                    self.transition_to(S1_wait_for_char)
                      
            elif self.state == S5_print_data_2:
                 for number in range(self.i):
                     print(str(round(self.time_array_2[number], 2)) + ' s, ' + str(round(self.position_array_2[number], 2)) + ' rad, ' + str(round(self.velocity_array_2[number], 2)) + ' rad/s')
                 else:                     
                     print('Finished collecting encoder 2 data.')
                     self.transition_to(S1_wait_for_char)
                        
            elif self.state == S6_zero_enc_1:
                 self.z_flag_1.write(1)
                 ## @brief     Variable that defines encoder 1 position shared item
                 #  @details   Allows encoder 1 position data to be accessed                      
                 reset_pos_1 = self.enc_pos_1.read()
                 self.enc_pos_1.write(reset_pos_1)
                 print('Encoder 1 position successfully reset.')
                 self.transition_to(S1_wait_for_char)
           
            elif self.state == S7_zero_enc_2:
                 self.z_flag_2.write(1)
                 ## @brief     Variable that defines encoder 2 position shared item
                 #  @details   Allows encoder 2 position data to be accessed                      
                 reset_pos_2 = self.enc_pos_2.read()
                 self.enc_pos_2.write(reset_pos_2)
                 print('Encoder 2 position successfully reset.') 
                 self.transition_to(S1_wait_for_char)
            
            elif self.state == S8_print_enc_pos_1:
                 print('Encoder 1 position: ' + str(self.enc_pos_1.read()*2*math.pi/4000) + 'rad')
                 self.transition_to(S1_wait_for_char)
               
            elif self.state == S9_print_enc_pos_2: 
                 print('Encoder 2 position: ' + str(self.enc_pos_2.read()*2*math.pi/4000) + 'rad')
                 self.transition_to(S1_wait_for_char)
                
            elif self.state == S10_print_enc_delta_1:
                 print('Encoder 1 delta: ' + str(self.enc_delta_1.read()*2*math.pi/4000) + 'rad')
                 self.transition_to(S1_wait_for_char)
                
            elif self.state == S11_print_enc_delta_2: 
                 print('Encoder 2 delta: ' + str(self.enc_delta_2.read()*2*math.pi/4000) + 'rad')
                 self.transition_to(S1_wait_for_char)
                
            elif self.state == S12_enable:
                
                if self.enable_flag.read() == 0:
                   self.enable_flag.write(1)
                   print('Motors enabled.')
                   self.transition_to(S1_wait_for_char)
                                
                elif self.enable_flag.read() == 1:
                   self.enable_flag.write(0)
                   print('Motors disabled.')
                   self.transition_to(S1_wait_for_char)
                   
                    
            elif self.state == S13_prompt_duty_cycle_1:                  
                if self.ser.any():
                   char_in = self.ser.read(1).decode()                                           
                   if char_in.isdigit() == True:
                           self.num_str_1 += char_in
                           self.ser.write(char_in)
                   else:
                       if(char_in == '-'):
                           if len(self.num_str_1) == 0:       
                              self.num_str_1 = '-' + self.num_str_1  #if there is first char, add char to string
                              self.ser.write(char_in) 
                       else:                                         #if len doesn't equal 0, go back and wait for char input  
                           if char_in == '\x7F':
                               if len(self.num_str_1) == 0:          #if string is empty, if there is no first char
                                   pass   
                               else:
                                   self.num_str_1 = self.num_str_1[: -1]
                                   self.ser.write(char_in)
                           else:
                                if '.' in self.num_str_1:       
                                   pass  
                                else:
                                    if (char_in == '.'):
                                       self.num_str_1 += char_in
                                       self.ser.write(char_in)
                                if float(self.num_str_1) > 100:
                                    self.num_str_1 = 100
                                if float(self.num_str_1) < -100:
                                    self.num_str_1 = -100   
                                if char_in == '\r':
                                    self.ser.write('\n')
                                    self.ser.write('\r')
                                    ## @brief     Variable that turns string input into float for duty cycle 1
                                    #  @details   This float value corresponds to motor 1
                                    number_1 = float(self.num_str_1)                                 
                                    self.dutycycle_1.write(number_1)
                                    print('Duty cycle set to: ' + str(number_1))
                                    self.num_str_1 = ''
                                    self.transition_to(S1_wait_for_char)
                                                                
                 
            elif self.state == S14_prompt_duty_cycle_2:
                if self.ser.any():
                   char_in = self.ser.read(1).decode()                                           
                   if char_in.isdigit() == True:
                           self.num_str_2 += char_in
                           self.ser.write(char_in)
                   else:
                       if(char_in == '-'):
                           if len(self.num_str_2) == 0:       
                              self.num_str_2 = '-' + self.num_str_2  #if there is first char, add char to string
                              self.ser.write(char_in) 
                       else:                                 #if len doesn't equal 0, go back and wait for char input  
                           if char_in == '\x7F':
                               if len(self.num_str_2) == 0:  #if string is empty, if there is no first char
                                   pass   
                               else:
                                   self.num_str_2 = self.num_str_2[: -1]
                                   self.ser.write(char_in)
                           else:
                                if '.' in self.num_str_2:       
                                   pass  
                                else:
                                    if (char_in == '.'):
                                       self.num_str_2 += char_in
                                       self.ser.write(char_in)
                                if float(self.num_str_2) > 100:
                                    self.num_str_2 = 100
                                if float(self.num_str_2) < -100:
                                    self.num_str_2 = -100   
                                if char_in == '\r':
                                    self.ser.write('\n')
                                    self.ser.write('\r')
                                    ## @brief     Variable that turns string input into float for duty cycle 2
                                    #  @details   This float value corresponds to motor 2
                                    number_2 = float(self.num_str_2)                                 
                                    self.dutycycle_2.write(number_2)
                                    print('Duty cycle set to: ' + str(number_2))
                                    self.num_str_2 = ''
                                    self.transition_to(S1_wait_for_char)
                 
            elif self.state == S15_fault_occurs:
                 print('Press c to clear fault.')
                 self.transition_to(S16_fault_cleared) 

            elif self.state == S16_fault_cleared:  
                if self.ser.any():
                    char_in = self.ser.read(1).decode()
                    if (char_in == 'c'):
                         self.fault_user_flag.write(0)
                         self.transition_to(S1_wait_for_char)
     
      
            else:
                raise ValueError('Invalid State.')
            
            self.next_time = utime.ticks_add(self.next_time, self.period)
            self.runs += 1
            
    def transition_to(self, new_state):
        ''' @brief            Transitions the FSM to a new state
            @details          A function that transitions the FSM to a new state
            @param new_state  The state to transition to
        '''
        self.state = new_state
        

            