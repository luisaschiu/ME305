''' @file        main.py
    @brief       Main script for Lab 4.
    @details     Implements cooperative multitasking using tasks implemented by
                 finite state machines.
    @author      Faith Chau
    @author      Luisa Chiu
    @date        November 15, 2021    
    \image html  Lab4_TaskDiagram.png "Lab 4 Task Diagram"
    \image html  Lab2_TaskEncoder_FSM.png "Lab 2 Task Encoder FSM"
    \image html  Lab4_TaskMotor.png "Lab 4 Task Motor FSM"
    \image html  Lab4_TaskUser_FSM.png "Lab 4 Task User FSM"
    \image html  Lab4_PlotProgression.png "Lab 4 Plot Progression"
    \image html  Lab4_BlockDiagram.png "Lab 4 Block Diagram"
    
    @page        page1 Lab 4 Report
    @brief       Main script for Lab 4.
    @details     Implements cooperative multitasking using tasks implemented by
                 finite state machines.
    @author      Faith Chau
    @author      Luisa Chiu
    @date        November 15, 2021  
    
    Below is a screenshot of the progression of plots from tuning the controller gain values.
    To improve the closed-loop velocity output of the motor, we changed the controller gains (also known as Kp).
    We did this by increasing Kp values by increments of 0.1 to obtain the smoothest results for velocity. As seen
    in the screenshot below, as Kp increased, the velocity values did not vary or oscillate as much over time. Therefore, through
    tuning, we can conclude that that a controller gain of 1 yielded the best results for an input velocity of 150 rad/s.
    \image html  Lab4_PlotProgression.png "Lab 4 Progression of Plots"
    Below is a screenshot of the block diagram implemented for the closed loop control.
    \image html  Lab4_BlockDiagram.png "Lab 4 Block Diagram"
    Below is the task diagram for lab 4. Task encoder reads motor data such as delta and uses it to calculate the measured velocity of
    the motor. Task motor implements the closed loop speed controller; it runs the motor using the acuation level calculated from user 
    input values of gain and setpoint. Task user interacts with the user by prompting the user for input.
    \image html  Lab4_TaskDiagram.png "Lab 4 Task Diagram"
    Below are the finite state machines for task encoder, task motor, and task user.
    \image html  Lab2_TaskEncoder_FSM.png "Lab 2 Task Encoder FSM"
    \image html  Lab4_TaskMotor.png "Lab 4 Task Motor FSM"
    \image html  Lab4_TaskUser_FSM.png "Lab 4 Task User FSM"
'''


import shares
import Lab4_task_userinterface
import Lab4_task_encoder
import pyb
import encoder
import Lab4_task_motor
import DRV8847
        
def main():
    ''' @brief The main program
    '''
    ## @brief        Creates a new pin object associated with pinB6 on the Nucleo
    #  @details      Defines a variable for pinB6 corresponding to encoder
    pinB6 = pyb.Pin(pyb.Pin.cpu.B6)
    ## @brief        Creates a new pin object associated with pinB7 on the Nucleo
    #  @details      Defines a variable for pinB7 corresponding to encoder
    pinB7 = pyb.Pin(pyb.Pin.cpu.B7)
    ## @brief        Creates an encoder object for encoder 1
    #  @details      Specifies the encoder object for corresponding motor
    encoder1 = encoder.Encoder(pinB6, pinB7, 4)
    ## @brief        Creates a new pin object associated with pinC6 on the Nucleo
    #  @details      Defines a variable for pinC6 corresponding to encoder
    pinC6 = pyb.Pin(pyb.Pin.cpu.C6)
    ## @brief        Creates a new pin object associated with pinC7 on the Nucleo
    #  @details      Defines a variable for pinC7 corresponding to encoder
    pinC7 = pyb.Pin(pyb.Pin.cpu.C7)
    ## @brief        Creates an encoder object for encoder 2
    #  @details      Specifies the encoder object for corresponding motor
    encoder2 = encoder.Encoder(pinC6, pinC7, 8) 
    ## @brief     The motor driver object that calls the DRV8847 Dual H-Bridge Motor Driver 
    #  @details   This motor driver object was created in the DRV8847.py file
    motor_drv = DRV8847.DRV8847(pyb.Pin.cpu.A15, pyb.Pin.cpu.B2, 3)
    ## @brief     The motor object that calls motor 1
    #  @details   This motor object was defined in main.py    
    motor_1 = motor_drv.motor(pyb.Pin.cpu.B4, pyb.Pin.cpu.B5, 1, 2)
    ## @brief     The motor object that calls motor 2
    #  @details   This motor object was defined in main.py
    motor_2 = motor_drv.motor(pyb.Pin.cpu.B0, pyb.Pin.cpu.B1, 3, 4) 
    ## @brief      This is a placeholder for the motor driver object for task 5
    #  @details    This is used so we call the motor driver once in all of our tasks
    motor_none = None   
    ## @brief     The period (in us) of the task
    #  @details   Specifies the largest number that can be stored in the timer, also known as the "Auto Reload" value
    period = 20000  # Number of microseconds between each desired interval
    z_flag_1 = shares.Share(0)
    z_flag_2 = shares.Share(0)
    fault_user_flag = shares.Share(0)
    enable_flag = shares.Share(0)
    enc_pos_1 = shares.Share(0)
    enc_pos_2 = shares.Share(0)
    enc_delta_1 = shares.Share(0)
    enc_delta_2 = shares.Share(0)
    gain_1 = shares.Share(0)
    gain_2 = shares.Share(0)
    inp_vel_1 = shares.Share(0)
    inp_vel_2 = shares.Share(0)
    meas_vel_1 = shares.Share(0)
    meas_vel_2 = shares.Share(0)
    step_flag = shares.Share(0)
    L_1 = shares.Share(0)
    L_2 = shares.Share(0)
    
    ## @brief        Creates a parameterized task constructor for task_userinterface.py
    #  @details      The constructor takes input arguments and objects and passes them into user task
    task1 = Lab4_task_userinterface.Task_User(period, enc_pos_1, enc_pos_2, z_flag_1, z_flag_2, fault_user_flag, enable_flag, enc_delta_1,
                                         enc_delta_2, gain_1, gain_2, inp_vel_1, inp_vel_2, step_flag, meas_vel_1, meas_vel_2, L_1, L_2)
    ## @brief        Creates a parameterized task constructor for task_encoder.py corresponding to encoder 1
    #  @details      The constructor takes input arguments and objects and interacts with both the encoder driver and user task
    task2 = Lab4_task_encoder.Task_Encoder(period, enc_pos_1, z_flag_1, enc_delta_1, encoder1)
    ## @brief        Creates a parameterized task constructor for task_encoder.py corresponding to encoder 2
    #  @details      The constructor takes input arguments and objects and interacts with both the encoder driver and user task   
    task3 = Lab4_task_encoder.Task_Encoder(period, enc_pos_2, z_flag_2, enc_delta_2, encoder2)
    ## @brief        Creates a parameterized task constructor for task_motor.py corresponding to motor 1
    #  @details      The constructor takes input arguments and objects and passes them into user task
    task4 = Lab4_task_motor.Task_Motor(period, motor_1, motor_drv, fault_user_flag, enable_flag, step_flag, gain_1, L_1, inp_vel_1, meas_vel_1)
    ## @brief        Creates a parameterized task constructor for task_motor.py corresponding to motor 2
    #  @details      The constructor takes input arguments and objects and passes them into user task
    task5 = Lab4_task_motor.Task_Motor(period, motor_2, motor_none, fault_user_flag, enable_flag, step_flag, gain_2, L_2, inp_vel_2, meas_vel_2)
                                  
    task_list = [task1, task2, task3, task4, task5]
    

    
    
    while(True):
        try:
            for task in task_list:
                task.run()
                
        except KeyboardInterrupt:
            break
        
    print('Program Terminating')
    
    
if __name__ == '__main__':
    main()
