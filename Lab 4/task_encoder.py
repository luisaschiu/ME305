''' @file        task_userinterface.py
    @brief       User interface task for cooperative multitasking example.
    @details     Implements a finite state machine that runs a data collection interface to interact with the encoder, motor, motor driver, and controller.
    @author      Faith Chau
    @author      Luisa Chiu
    @date        October 19, 2021
    \image html  Lab4_TaskUser_FSM.png "Lab 4 Task User FSM"
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
#  @details   Creates an initial state condition for state 13. State 13 prompts user input for the proportional gain for motor 1.
S13_input_gain_1 = 13

## @brief     State 14 of the user interface task
#  @details   Creates an initial state condition for state 14. State 14 prompts user input for the proportional gain for motor 2.
S14_input_gain_2 = 14

## @brief     State 15 of the user interface task
#  @details   Creates an initial state condition for state 15. State 15 prompts user input for the angular velocity setpoint for motor 1.
S15_input_vel_1 = 15

## @brief     State 16 of the user interface task
#  @details   Creates an initial state condition for state 16. State 16 prompts user input for the angular velocity setpoint for motor 2.
S16_input_vel_2 = 16

## @brief     State 17 of the user interface task
#  @details   Creates an initial state condition for state 17. State 17 alerts user of a fault condition.
S17_fault_occurs = 17

## @brief     State 18 of the user interface task
#  @details   Creates an initial state condition for state 18. State 18 tells user that the fault condition is cleared.
S18_fault_cleared = 18

## @brief     State 19 of the user interface task
#  @details   Creates an initial state condition for state 19. State 19 runs the step_response for 10 seconds; it collects and stores time, measured velocity, and PWM level for motor 1.
S19_step_response_1 = 19

## @brief     State 20 of the user interface task
#  @details   Creates an initial state condition for state 20. State 20 runs the step_response for 10 seconds; it collects and stores time, measured velocity, and PWM level for motor 2.
S20_step_response_2 = 20

## @brief     State 21 of the user interface task
#  @details   Creates an initial state condition for state 21. State 21 prints motor data for the step response.
S21_step_print = 21

class Task_User():
    ''' @brief      User interface task for data collection and interaction with task encoder, task motor, and task motor driver
        @details    Implements a finite state machine that runs a data collection interface.
    '''    
    def __init__(self, period, enc_pos_1, enc_pos_2, z_flag_1, z_flag_2, fault_user_flag, enable_flag, enc_delta_1, enc_delta_2, gain_1, gain_2, inp_vel_1, inp_vel_2, step_flag, meas_vel_1, meas_vel_2, L_1, L_2):
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
            @param gain_1           Variable that defines gain value for motor 1
            @param gain_2           Variable that defines gain value for motor 2
            @param inp_vel_1        Variable that defines input velocity for motor 1
            @param inp_vel_2        Variable that defines input velocity for motor 2
            @param step_flag        A boolean flag used to start step response
            @param meas_vel_1       Variable that defines measured velocity for motor 1
            @param meas_vel_2       Variable that defines measured velocity for motor 2
            @param L_1              Variable used to define actuation level for motor 1
            @param L_2              Variable used to define actuation level for motor 2
        '''
        ## @brief     The frequency of the task
        #  @details   Defines variable that specifies timer frequency
        self.period = 20000
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
        ## @brief     Variable that defines gain value for motor 1
        #  @details   Also known as Kp, or proportional gain 
        self.gain_1 = gain_1
        ## @brief     Variable that defines gain value for motor 2
        #  @details   Also known as Kp, or proportional gain 
        self.gain_2 = gain_2
        ## @brief     Variable that defines input velocity for motor 1
        #  @details   This is the reference velocity inputted by the user
        self.inp_vel_1 = inp_vel_1
        ## @brief     Variable that defines input velocity for motor 2
        #  @details   This is the reference velocity inputted by the user
        self.inp_vel_2 = inp_vel_2
        ## @brief     Variable that defines measured velocity for motor 1
        #  @details   Takes the measured delta values from the encoder and divides by the period to obtain measured velocity
        self.meas_vel_1 = meas_vel_1
        ## @brief     Variable that defines measured velocity for motor 2
        #  @details   Takes the measured delta values from the encoder and divides by the period to obtain measured velocity
        self.meas_vel_2 = meas_vel_2
        ## @brief     Variable used to define actuation level for motor 1
        #  @details   This value is calculated using gain, measured angular velocity, and reference angular velocity
        self.L_1 = L_1
        ## @brief     Variable used to define actuation level for motor 2
        #  @details   This value is calculated using gain, measured angular velocity, and reference angular velocity
        self.L_2 = L_2
        ## @brief     A variable used to initialize the user input
        #  @details   This string is what the user sees for motor 1 input
        self.num_str_1 = ''  
        ## @brief     A variable used to initialize the user input
        #  @details   This string is what the user sees for motor 2 input
        self.num_str_2 = ''  
        ## @brief     A variable used for indexing
        #  @details   This value helps index data points for time, position, and delta
        self.i = 0
        ## @brief     An array that is created to store time elapsed
        #  @details   This variable creates an empty array of 1000 data points, which will be populated later with time data
        self.time_array = array.array('f', 1000*[0])
        ## @brief     An array that is created to store measured positions of the motors
        #  @details   This variable creates an empty array of 1000 data points, which will be populated later with position data
        self.position_array = array.array('f', 1000*[0])
        ## @brief     An array that is created to store measured velocites of the motors
        #  @details   This variable creates an empty array of 1000 data points, which will be populated later with velocity data
        self.velocity_array = array.array('f', 1000*[0])        
        ## @brief     An array that is created to store actuation level of the motors
        #  @details   This variable creates an empty array of 1000 data points, which will be populated later with actuation level data        
        self.L_array = array.array('f', 1000*[0])
        ## @brief     An array that is created to store measured velocites of the motors
        #  @details   This variable creates an empty array of 1000 data points, which will be populated later with velocity data
        self.meas_vel_array = array.array('f', 1000*[0])
        ## @brief     A boolean flag used to start step response
        #  @details   Works with the motor task and user interface to communicate step function performance
        self.step_flag = step_flag     
        

        
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
                      "\'m\' to perform a step response for motor 1,",
                      "\'M\' to perform a step response for motor 2,",
                      "\'c\' to clear a fault condition triggered by DR,",                    
                      "\'s\' to end encoder 1 data collection prematurely,",
                      "\'S\' to end encoder 2 data collection prematurely.", sep="\n")
                self.state = S1_wait_for_char
                
            elif self.state == S1_wait_for_char:
                
                if self.fault_user_flag.read() == 1:
                    self.transition_to(S17_fault_occurs)
                        
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
                        
                    elif (char_in == 'm'):
                        print('Input gain, Kp, for Motor 1: ')
                        self.transition_to(S13_input_gain_1) 
                        
                    elif (char_in == 'M'):
                        print('Input gain, Kp, for Motor 2: ')
                        self.transition_to(S14_input_gain_2)
                    
                    else:
                        print('Command \'{:}\' is invalid.'.format(char_in))                                 
                        
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
                   
                    
            elif self.state == S13_input_gain_1:
                # Enable/Disable motors
                if self.enable_flag.read() == 0:
                    self.gain_2.write(0)
                    self.inp_vel_2.write(0)
                    self.L_2.write(0)
                    self.enable_flag.write(1)
 
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
                                if char_in == '\r':
                                    self.ser.write('\n')
                                    self.ser.write('\r')
                                    ## @brief     Variable that turns string input into float for duty cycle 1
                                    #  @details   This float value corresponds to motor 1
                                    number_1 = float(self.num_str_1)                                 
                                    self.gain_1.write(number_1)
                                    print('Gain set to: ' + str(number_1))
                                    print('Input velocity in rad/s for Motor 1: ')
                                    self.num_str_1 = ''                                    
                                    self.transition_to(S15_input_vel_1)
                                                                
                 
            elif self.state == S14_input_gain_2:
               # Enable/Disable motors
                if self.enable_flag.read() == 0:
                   self.gain_1.write(0)
                   self.inp_vel_1.write(0)
                   self.L_1.write(0)
                   self.enable_flag.write(1)
                   
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
                                if char_in == '\r':
                                    self.ser.write('\n')
                                    self.ser.write('\r')
                                    ## @brief     Variable that turns string input into float for duty cycle 2
                                    #  @details   This float value corresponds to motor 2
                                    number_2 = float(self.num_str_2)                                 
                                    self.gain_2.write(number_2)
                                    print('Gain set to: ' + str(number_2))
                                    print('Input velocity in rad/s for Motor 2: ')
                                    self.num_str_2 = ''
                                    self.transition_to(S16_input_vel_2)
                                    
            elif self.state == S15_input_vel_1:
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
                                if char_in == '\r':
                                    self.ser.write('\n')
                                    self.ser.write('\r')
                                    ## @brief     Variable that turns string input into float for duty cycle 1
                                    #  @details   This float value corresponds to motor 1
                                    number_1 = float(self.num_str_1)                                 
                                    self.inp_vel_1.write(number_1)
                                    print('Velocity set to: ' + str(number_1))                                    
                                    self.num_str_1 = ''
                                    ## @brief     Assigns an arbitrary reference point that begins after user inputs are defined
                                    #  @details   Used to implement the timed data collection period
                                    self.collect_time = current_time
                                    print('Performing step response...')
                                    self.transition_to(S19_step_response_1)
                                    
            elif self.state == S16_input_vel_2:                  
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
                       else:                                         #if len doesn't equal 0, go back and wait for char input  
                           if char_in == '\x7F':
                               if len(self.num_str_2) == 0:          #if string is empty, if there is no first char
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
                                if char_in == '\r':
                                    self.ser.write('\n')
                                    self.ser.write('\r')
                                    ## @brief     Variable that turns string input into float for duty cycle 1
                                    #  @details   This float value corresponds to motor 1
                                    number_2 = float(self.num_str_2)                                 
                                    self.inp_vel_2.write(number_2)
                                    print('Velocity set to: ' + str(number_2))
                                    self.num_str_2 = ''
                                    self.collect_time = current_time
                                    print('Performing step response...')
                                    self.transition_to(S20_step_response_2)                                   
                                    
            elif self.state == S17_fault_occurs:
                 print('Press c to clear fault.')
                 self.transition_to(S18_fault_cleared) 

            elif self.state == S18_fault_cleared:  
                if self.ser.any():
                    char_in = self.ser.read(1).decode()
                    if (char_in == 'c'):
                         self.fault_user_flag.write(0)
                         self.transition_to(S1_wait_for_char)
                         
            elif self.state == S19_step_response_1:
                 self.meas_vel_1.write((self.enc_delta_1.read()*2*math.pi/4000)/self.period*1000000)
                 self.step_flag.write(1)
                 ## @brief     Creates a variable that calculates difference between time reference points
                 #  @details   Used to collect data for a maximum time of 10 seconds
                 self.time_diff = utime.ticks_diff(current_time, self.collect_time)/1000000    
                 if self.time_diff <= 10:
                    if self.fault_user_flag.read() == 1:
                        self.transition_to(S17_fault_occurs)
                        
                    self.time_array[self.i] = self.time_diff
                    self.meas_vel_array[self.i] = self.meas_vel_1.read()
                    self.L_array[self.i] = self.L_1.read()
                    self.i += 1
                    ## @brief     A variable that creates a list of the time, angular velocity, and actuation level arrays
                    #  @details   This list combines three individual arrays
                    self.list_3 = [self.time_array, self.meas_vel_array, self.L_array]
                    if self.ser.any():
                       char_in = self.ser.read(1).decode()
                       if(char_in == 's' or 'S'):
                         self.transition_to(S21_step_print)
                         
                 else: self.transition_to(S21_step_print)
            
            elif self.state == S20_step_response_2:
                 self.meas_vel_2.write((self.enc_delta_2.read()*2*math.pi/4000)/self.period*1000000)
                 self.step_flag.write(1)
                 self.time_diff = utime.ticks_diff(current_time, self.collect_time)/1000000                 
                 if self.time_diff <= 10:   
                    if self.fault_user_flag.read() == 1:
                        self.transition_to(S17_fault_occurs)
                        
                    self.time_array[self.i] = self.time_diff
                    self.meas_vel_array[self.i] = self.meas_vel_2.read()
                    self.L_array[self.i] = self.L_1.read()
                    self.i += 1
                    self.list_3 = [self.time_array, self.meas_vel_array, self.L_array]
                    if self.ser.any():
                       char_in = self.ser.read(1).decode()
                       if(char_in == 's' or 'S'):
                         self.transition_to(S21_step_print)
                         
                 else: self.transition_to(S21_step_print)
            
            elif self.state == S21_step_print:
                for number in range(self.i):
                    print(str(round(self.time_array[number], 2)) + ' s, ' + str(round(self.meas_vel_array[number], 2)) + ' rad/s,' + str(round(self.L_array[number], 2)) + ' % ')
                else:     
                    print('Step response completed.') 
                    self.enable_flag.write(0)
                    self.step_flag.write(0)
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
        

            