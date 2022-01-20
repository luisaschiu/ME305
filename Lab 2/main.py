''' @file       Lab2_main.py
    @brief      Main script for cooperative multitasking example.
    @details    Implements cooperative multitasking using tasks implemented by
                finite state machines.
    @author     Faith Chau
    @author     Luisa Chiu
    @date       October 19, 2021     
    \image html  Lab2_TaskDiagram.png "Task Diagram"
    \image html  Lab2_TaskEncoder_FSM.png "Task Encoder FSM"
    \image html  Lab2_TaskUser_FSM.png "Task User FSM"
'''


import shares
import task_userinterface
import task_encoder
import pyb
import encoder

## @brief        Creates a new pin object associated with pin B6 on the Nucleo
#  @details      Defines a variable for pinB6 corresponding to encoder
pinB6 = pyb.Pin(pyb.Pin.cpu.B6)
## @brief        Creates a new pin object associated with pin B7 on the Nucleo
#  @details      Defines a variable for pinB7 corresponding to encoder
pinB7 = pyb.Pin(pyb.Pin.cpu.B7)
## @brief        Creates an encoder object 
#  @details      Specifies the encoder object for corresponding motor
encoder1 = encoder.Encoder(pinB6, pinB7, 4)

#Input for encoder2 object
#pinC6 = pyb.Pin(pyb.Pin.cpu.C6)
#pinC7 = pyb.Pin(pyb.Pin.cpu.C7)
#encoder2 = encoder.Encoder(pinC6, pinC7, 3) 
        
def main():
    ''' @brief The main program
    '''
    ## @brief     The period (in us) of the task
    #  @details   Specifies the largest number that can be stored in the timer, also known as the "Auto Reload" value
    period = 20000  # Number of microseconds between each desired interval
    z_flag = shares.Share(0)
    enc_pos = shares.Share(0)
    enc_delta = shares.Share(0)
    my_Q = shares.Queue()
    enc_obj = encoder1
    ## @brief        Creates a parameterized task constructor
    #  @details      The constructor takes input arguments and objects and passes them into encoder task
    task1 = task_userinterface.Task_User(period, enc_pos, z_flag, enc_delta, my_Q)
    ## @brief        Creates a parameterized task constructor
    #  @details      The constructor takes input arguments and objects and interacts with both the encoder driver and user task
    task2 = task_encoder.Task_Encoder(period, enc_pos, z_flag, enc_delta, enc_obj, my_Q)
    ## @brief        Creates a variable that contains tasks
    #  @details      List that contains tasks to run
    task_list = [task1, task2]
    

    
    
    while(True):
        try:
            for task in task_list:
                task.run()
                
        except KeyboardInterrupt:
            break
        
    print('Program Terminating')
    
    
if __name__ == '__main__':
    main()
