import serial
import time as t
import re
import sys
import glob
import serial

def serial_ports():
    """ Grabbed from: https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
        Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

# model of VXM stage bi-slide E04, conversion factor btwn steps and distance
E04 = .0254 #mm/step

# command repo, all commands that don't require specific inputs, all in utf-8 encoding
# you can also put b infront of the string and it will put it as utf-8 i guess
com_ctrl = 'E' # remote control of vxm, with returns from machine
com_ctrl = com_ctrl.encode()
com_rtn = 'Q' # returns vxm to manual mode
com_rtn = com_rtn.encode()
com_clr = 'C' # clears mem of commands
com_clr = com_clr.encode()
com_kill = 'K' # kills current process
com_kill = com_kill.encode()
com_pos = 'X' # position of 1st motor w.r.t stored 0
com_pos = com_pos.encode()
com_zero = 'IA1M0' # moves stage to absolute zero stored in vxm
com_zero = com_zero.encode()
com_set_zero = 'IA1M-0' # sets absolute zero of stage
com_set_zero = com_set_zero.encode()
com_max_pos = 'I1M0' # moves to furthest positive position possible
com_max_pos = com_max_pos.encode()
com_min_pos = 'I1M-0' # moves to furthest neg position possible
com_min_pos = com_min_pos.encode()

# other useful commands, but they require some specific input
# currently just for motor 1

# 'I1Mx' - moves pos (cw) direction, x steps
# 'I1M-x' - moves neg (ccw) direction, x steps
# ^ aboves commands for range of x = [1,16777215]
# 'IA1Mx' - moves x steps from absolute zero, x = [-8388608,8388607]
# 'Px' - pauses x tenths of a second, x = [0,65535]
# 'P-x' - pauses x tenths of a millisecond, x = [1,65535]

# goal of program: travel 5mm in 100 steps all while photodiode continously collects data

# programs as a part of this module:
# move stage to 0, move stage once relative to initial position, move + pause in loop, position check
# all programs use 'with' context manager, and relenquishes remote control and closes port at end of program
# assumes you are only working with motor 1 (and as of now 3/18/22, it is)

def zero_stage(port):
    '''
    moves the stage to its stored zero position
    if you dislike the stored zero you are able to shift it with the commands above
    input:
    port - str - the COM port name that the VXM is attached to
    '''
    # check inputs
    assert(type(port)==str), 'port must be string'
    # open port
    with serial.Serial() as s:
        s.port = port
        s.timeout = 0
        s.open()
        s.flushOutput()
        s.write(com_ctrl)
        s.write(com_clr)
        s.write(b'IA1M0,R') # zeros position
        t.sleep(2.)
        s.write(com_clr)
        s.flushOutput()
        s.write(com_rtn)
        s.close()

def pos_check(port):
    '''
    sends query to VXM to return the position (in steps) of the stage w.r.t the set zero
    inputs:
    port - str - the COM port name that the VXM is attached to
    outputs:
    loc - int, [steps] - the number of steps the stage is from VXM's set zero
    '''
    with serial.Serial() as s:
        s.port = port
        s.timeout = 0
        s.open()
        s.flushOutput()
        s.write(b'E,C')
        s.flushOutput()
        s.write(b'X')
        t.sleep(.1) # need the slight pause so VXM can return query
        pos = s.readline()
        # print(pos.decode()) # raw output if you feels so inclined to see it
        s.flushOutput()
        s.write(b'C,Q')
        s.close()
    pos = pos.decode(encoding='ascii')
    
    print(pos)
    #return int(pos)


def rel_move(port,dist,pause,CW=True):
    '''
    moves stage a given distance relative to its position before this program was ran
    NOTE: if the distance input is greater than the stage can travel, it will just go to the edge and stop
    currently (3/18/22) this program doest check for this
    inputs:
    port - str - the COM port name that the VXM is attached to
    dist - float,[mm] - distance you would like stage to move, realtive to intial stage position
    pause - float,[sec] - the amount of time you would like to wait before and after the move
    ^ minimum amount of time able to wait: 1e-5 sec (10 microseconds)
    CW - bool - direction stage will move, default CW positive direction (away from motor)
    '''
    # check inputs
    assert(type(port)==str),'port input must be string'
    assert(type(CW)==bool),'direction input must be boolean'
    # calculate steps and time for VXM inputs, along with time for sleep
    if (pause < .03):
        p = round(pause/1.e-5)
        time_com = 'P-'+str(p)
    else:
        p = round(pause/.1)
        time_com = 'P'+str(p)
    z = pause*2. + 1. 
    steps = round(dist/E04)
    if CW:
        mv_com = 'I1M'+str(steps)
    else:
        mv_com = 'I1M-'+str(steps)
    cmd = time_com+','+mv_com+','+time_com+',R'
    # open port
    with serial.Serial() as s:
        s.port = port
        s.timeout = 0
        s.open()
        s.flushOutput()
        s.write(b'F,C')
        s.flushOutput()
        s.write(cmd.encode())
        t.sleep(z)
        s.write(b'C,Q')
        s.close()

# Currently (2022-03-18) no distance/step check after either move program
def loop_move(port: str, tot_dist: float, increments: int, pause: float, direction: str='+'):
    '''
    loops the action of 'rel_move' the number of times given in increments, moving a total distance give by tot_dist input
    inputs:
    port - str - the COM port name that will allow you to interface with the VXM
    tot_dist - float,[mm] - total distance you would like stage to move, realtive to intial stage position
    increments - int - number of stops you would like the stage to take on its journey
    ^ E04 stage can move 0.0254mm/step so you should keep in mind
    pause - float,[sec] - the amount of time you would like to wait before and after each incremental move
    ^ NOTE: now in a loop, VXM is given a 2 pause commands in between each move, so VXM will wait pause*2 seconds in between each move
    ^ minimum amount of time able to wait: 1e-5 sec (10 microseconds),
    direction - direction stage will move, default '+' direction (away from motor)
    '''
    # check inputs
    assert(type(port)==str),'port input must be string'
    assert(type(increments)==int),'increments input must be integer'
    assert(direction == '+' or direction == '-'),'direction input must be + or -'
    
    # calculate time for VXM inputs, along with time for sleep
    if (pause < .03):
        p = round(pause/1.e-5) # [*10 microsec]
        time_com = 'P-'+str(p)
    else:
        p = round(pause/.1) # [*.1 sec]
        time_com = 'P'+str(p)
    z = increments*pause*2. + 1. # sec
    
    # determine steps nessecary for each incremental move
    dps = tot_dist/increments # dist per increment [mm]
    spi = round(dps/E04) # steps per increment [steps]
    if direction == '+':
        mv_com = 'I1M'+str(spi)
    elif direction == '-':
        mv_com = 'I1M-'+str(spi)
    
    # comand string
    cmd = time_com+','+mv_com+','+time_com+',L'+str(increments)+',R'
    print(cmd)

    # open port
    with serial.Serial() as s:
        s.port = port
        s.timeout = 0
        s.open()
        s.flushOutput()
        s.write('F,C'.encode(encoding='ascii'))
        s.flushOutput()
        s.write(cmd.encode(encoding='ascii'))
        t.sleep(z)
        s.write('C,Q'.encode(encoding='ascii'))
        s.close()

def home(port):
    with serial.Serial() as s:
        s.port = port
        s.timeout = 0
        s.open()
        s.flushOutput()
        s.write('F,C'.encode(encoding='ascii'))
        s.flushOutput()
        s.write('S1M1000,I1M-0,R'.encode(encoding='ascii'))
        t.sleep(5)
        s.write('IA1M-0,R'.encode(encoding='ascii'))
        s.write('C,Q'.encode(encoding='ascii'))
        s.close()

def goto(port: str, index: int):
    with serial.Serial() as s:
        s.port = port
        s.timeout = 0
        s.open()
        s.flushOutput()
        s.write('F,C'.encode(encoding='ascii'))
        s.flushOutput()
        # MUST HAVE A PAUSE BEFORE INDEX COMMAND!!!!
        s.write(('P1,IA1M4000,R').encode(encoding='ascii'))
        t.sleep(5)
        s.write('C,Q'.encode(encoding='ascii'))
        s.close()

vxm_controller = serial_ports()[0]
print(vxm_controller)
#home(vxm_controller)
goto(vxm_controller, 4000)
goto(vxm_controller, 0)
#loop_move(vxm_controller, 30., 5, 1., '+')
print(pos_check(vxm_controller))