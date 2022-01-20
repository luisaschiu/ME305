'''@file        Lab0x01.py
   @brief       Changes LED light patterns on the Nucleo L476 development board
   \image html  Lab1_FSM.png "State Transition Diagram"
   Link to Demonstration Video: https://youtu.be/anM4EopmLjM
   @date        October 7, 2021

'''
import pyb
import utime
import math

## @brief        Creates a new pin object associated with pin A5 on the Nucleo
#  @details      Defines a variable for pinA5 corresponding to LED light
pinA5 = pyb.Pin (pyb.Pin.cpu.A5)

## @brief        Creates a new pin object associated with pinC13 on the Nucleo
#  @details      Defines a variable for pinC13 corresponding to button press
pinC13 = pyb.Pin (pyb.Pin.cpu.C13)

## @brief        Creates a timer object using timer 2
#  @details      Defines a variable for a timer with a frequency of 20000 Hz
tim2 = pyb.Timer(2,freq = 20000)

## @brief        Creates a timer channel object
#  @details      Defines a variable for timer 2 channel 1 in relation to pinA5
t2ch1 = tim2.channel (1, pyb.Timer.PWM, pin=pinA5)

def onButtonPressFCN(IRQ_src): 
    '''
        @brief    This is a callback function that runs when the button is pressed. 
        @details  Using a variable that we assign with on (1) and off(0) values, we allow for the button to effectively switch on and off and move through the FSM.
        @param    IRC_src This is the interrupt callback input that is called when the button is pressed.
        @return   'Press' variable is assigned the value 1. 
    '''
    global press
    press = 1
    
def reset_timer():
    '''
       @brief    This is a function that resets the Current_Time, which is a measure of the duration for the wave
       @details  The startTime variable is reset when this function is called.
    '''
    global startTime
    startTime = utime.ticks_ms()
    
def update_timer():
    '''
       @brief   This is a function that updates the Current_Time, which is a measure of the duration for the wave
       @details The stopTime and Current_Time variables are updated when this function is called.
    '''
    global stopTime
    global Current_Time
    stopTime = utime.ticks_ms()
    Current_Time = utime.ticks_diff(stopTime,startTime)/1000

def Update_SQW(Current_Time):
    '''
       @brief    This is a function that updates the LED brightness for the square wave pattern.
       @details  Using input Current_Time, this function creates a true/false argument that is satisfied by the listed expression and inequality.
       @param    Current_Time represents the elapsed time between startTime and stopTime.
       @return   This function returns either value 0 or 100, and is used with pulse_width_percent to reflect LED brightness.
    '''
    return 100*(Current_Time % 1.0 < 0.5)


def Update_STW(Current_Time):
    '''
       @brief    This is a function that updates the LED brightness for the sawtooth wave pattern.
       @details  Using input Current_Time, this function returns values that increase with time until reaching the value 1.
       @param    Current_Time represents the elapsed time between startTime and stopTime.
       @return   This function returns increasing values until threshold is reached and is used with pulse_width_percent to reflect LED brightness.
    '''
    return 100*(Current_Time % 1.0)


def Update_SW(Current_Time):
    '''
       @brief    This is a function that updates the LED brightness for the sine wave pattern.
       @details  This function returns sine values as a function of Current_Time and has a period of 10 seconds.
       @param    Current_Time represents the elapsed time between startTime and stopTime.
       @return   This function returns sine values for the given period and is used with pulse_width_percent to reflect LED brightness.
    '''
    return 100*math.sin(Current_Time*2*math.pi/10)


if __name__ == '__main__':
  ## @brief        Creates an initial state condition
  #  @details      Defines the starting state condition to be at state 0
  state = 0
  
  ## @brief        Sets the number of runs to 0
  #  @details      Defines a variable to keep track of runs
  runs = 0 
  
  ## @brief        Sets initial condition for button press callback to be False
  #  @details      Defines a variable for the button press callback
  press = 0
  
  ## @brief        Registers the callback function and causes an interrupt when pressing the button
  #  @details      Defines a variable for the interrupt request for pinC13 when the trigger is on a falling edge
  ButtonInt = pyb.ExtInt(pinC13, mode=pyb.ExtInt.IRQ_FALLING,
                                     pull=pyb.Pin.PULL_NONE, callback=onButtonPressFCN)
  
  ## @brief        An increasing millisecond counter with an arbitrary reference point
  #  @details      Records the first time stamp in milliseconds
  
  startTime = utime.ticks_ms()
  
  ## @brief        An increasing millisecond counter with an arbitrary reference point
  #  @details      Records the second time stamp in milliseconds
  stopTime = utime.ticks_ms()
  
  ## @brief        Duration between button presses in units of milliseconds
  #  @details      Calculates elapsed time between startTime and stopTime
  Current_Time = utime.ticks_diff(stopTime,startTime)/1000
  
  while (True):
     try:
          if (state == 0):
              print('Please press the B1 Button (Blue) to cycle through LED patterns')
              state = 1
          elif (state==1):
              if press == 1:
                  state = 2
                  reset_timer()
                  press = 0
                  print('Square Wave pattern selected')
          elif (state==2):
             update_timer()
             t2ch1.pulse_width_percent(Update_SQW(Current_Time))
             if press == 1:
                 state = 3
                 reset_timer()
                 press = 0
                 print('Sawtooth Wave pattern selected')
          elif (state==3):
             update_timer()
             t2ch1.pulse_width_percent(Update_STW(Current_Time))
             if press == 1:
                 state = 4
                 reset_timer()
                 press = 0
                 print('Sine Wave pattern selected')
          elif (state==4):
             update_timer()
             t2ch1.pulse_width_percent(Update_SW(Current_Time))    
             if press == 1:
                 state = 2
                 reset_timer()
                 press = 0
                 print('Square Wave pattern selected')
          
          runs += 1
          
     except KeyboardInterrupt:
        break
    
print('Program Terminated')

