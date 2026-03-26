# Pi Pico MIDI Matrix Decode
#
# @diyelectromusic
# https://diyelectromusic.wordpress.com/2021/02/03/pi-pico-midi-matrix-decode/
#
#      MIT License
#      
#      Copyright (c) 2020 diyelectromusic (Kevin)
#      
#      Permission is hereby granted, free of charge, to any person obtaining a copy of
#      this software and associated documentation files (the "Software"), to deal in
#      the Software without restriction, including without limitation the rights to
#      use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
#      the Software, and to permit persons to whom the Software is furnished to do so,
#      subject to the following conditions:
#      
#      The above copyright notice and this permission notice shall be included in all
#      copies or substantial portions of the Software.
#      
#      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#      IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
#      FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#      COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHERIN
#      AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#      WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
from machine import ADC
from machine import Pin, I2C
import utime
import midi
from time import sleep
from ads1x15 import ADS1115

#configuration du ADS1115

i2c=I2C(1, sda=Pin(26), scl=Pin(27))
adc = ADS1115(i2c, address=72, gain=1)


#juste la led de la pico
led = Pin(25, Pin.OUT)

#boutons octaves
bout_bass1 = Pin(19, Pin.IN,Pin.PULL_UP) #basses 
bout_bass2 = Pin(18, Pin.IN,Pin.PULL_UP) #basses
bout_acc1 = Pin(16, Pin.IN,Pin.PULL_UP) #accords
bout_acc2 = Pin(17, Pin.IN,Pin.PULL_UP) #accords
bout_midi1 = Pin(20, Pin.IN,Pin.PULL_UP) #midi
bout_midi2 = Pin(21, Pin.IN,Pin.PULL_UP) #midi



#potards
adc_pin_bend = Pin(28, mode=Pin.IN)
bend = ADC(adc_pin_bend)

#uart = UART(0,31250)

#librairie midi

my_midi = midi.Midi(0,Pin(0),Pin(1))
velocity = 127
note=48
debounce_gate=5





# tentons de faire un tableau de commande

grille_basses_noms=[
    ["fa","do","sol","re","la","mi",
     "si","fad","dod","lab","mib","sib",
     "Afa","Ado","Asol","Are","Ala","Ami",
     "Asi","Afad","Adod","Alab","Amib","Asib"
     ]
]

grille_basses_notes=[
    [                       #### NOTES ###########
     -7,    # FA            #    41   # r=8  c= 13   
     0,     # DO            #    48   #      c= 15     
     -5,    # SOL           #    55   #      c= 11      
     2,     # RE            #    50   #      c= 14      
     -3,    # LA            #    45   #      c= 10     
     -8,    # MI            #    40   #      c= 12     
     -1,    # SI            #    47   # r=9  c= 13     
     -6,    # FA# / SOLb    #    42   #      c= 15     
     1,     # DO# / REb     #    49   #      c= 11     
     -4,    # SOL# / LAb    #    44   #      c= 14     
     3,     # RE# / MIb     #    51   #      c= 10     
     -2,    # LA# / SIb     #    46   #      c= 12
                            #### ACCORDS #########
     5+12,     # fa            #    53   # r=6  c= 13     
     12+12,    # do            #    60   #      c= 15     
     7+12,     # sol           #    67   #      c= 11     
     14+12,    # re            #    62   #      c= 14    
     9+12,     # la            #    57   #      c= 10     
     4+12+12,  # mi            #    52   #      c= 12     
     11+12,    # si            #    59   # r=7  c= 13     
     6+12,     # fa# / solb    #    54   #      c= 15     
     13+12,    # do# / reb     #    61   #      c= 11     
     8+12,     # sol# / lab    #    56   #      c= 14     
     15+12,    # re# / mib     #    63   #      c= 10     
     10+12     # la# / sib     #    58   #      c= 12     
     ]
]





# Details of how to make a keyboard matrix
# http://blog.komar.be/how-to-make-a-keyboard-the-matrix/

firstnote = 48 # C3
rows = []
cols = []
playnote = []
lastnote = []
# MIDI

canal_1 = 1
canal_2 = 1


def bouton1(x):
    if (bout_midi1.value() == 1): 
        x = 1
    if (bout_midi1.value() == 0):
        x = 2

    return (x)

def bouton2(y):
    if (bout_midi2.value() == 1): 
        y = 2
    if (bout_midi2.value() == 0):
        y = 1

    return (y)

    


#pitch sur dac du pico pin 28

def midiPitchBend(x):
    pot_bend = round(bend.read_u16()/4)   # conversion analogique-numérique 0-65535 vers 16384
    msb = pot_bend >> 7
    lsb = pot_bend & 127 
    my_midi.send_pitch_bend(223+x,lsb,msb)

def mod_wheel(x):
    vMW = round(adc.read(7, 3)/206)
    my_midi.send_control_change(midi.CHANNEL[x], 1, value=vMW)

    return vMW

def mod_13(x):
    v13 = round(adc.read(7, 2)/206)
    my_midi.send_control_change(midi.CHANNEL[x], 13, value=-v13+127)
    return(v13)

def mod_91(x):
    v91 = round(adc.read(7, 1)/206)
    my_midi.send_control_change(midi.CHANNEL[x], 91, value=v91)
    return(v91)

def mod_12(x):
    v12 = round(adc.read(7, 0)/206)
    my_midi.send_control_change(midi.CHANNEL[x], 12, value=v12)
    return(v12)








def ecrire():
    print("-> mod wheel = ", mod_wheel()," ### 13 = ", mod_13()," ### 91 = ", mod_91()," ### 12 = ", mod_12())





    #91 attaque? , 13 puissant, 12 subtile

# Switch OFF will be HIGH (operating in PULL_UP mode)
#notes = do re mi fa sol la >> row = 13,14,12,15,11,10 / col = 8
#notes = fa# sol# la# si do# re# >> row = 13,14,12,15,11,10 / col = 9
row_pins = [15,13,11,14,10,12]
numrows = len(row_pins)
for rp in range(0, numrows):
    rows.append(Pin(row_pins[rp], Pin.IN, Pin.PULL_UP))

# OPEN DRAIN mode means that when HIGH the pin is effectively disabled.
# According to the RP2 MicroPython code this is simulated on the RP2 chip.
# See https://github.com/micropython/micropython/blob/master/ports/rp2/machine_pin.c
# WARNING: At time of writing, this isn't in the MP release!
#          For now, just use standard Pin.OUT.
#




 #accord = 6,7 notes=8,9
col_pins = [8,9,6,7]
numcols = len(col_pins)
for cp in range(0, numcols):
    cols.append(Pin(col_pins[cp], Pin.OUT))


# Initialise Columns to HIGH (i.e. disconnected)
for c in range(0, numcols):
    cols[c].value(True)
    for r in range(0, numrows):
        # initialise the note list
        playnote.append(0)
        lastnote.append(0)

while True:

    # Activate each column in turn by setting it to low
    for c in range(0, numcols):
        cols[c].value(False)

        # Then scan for buttons pressed on the rows
        # Any pressed buttons will be LOW
        for r in range(0, numrows):
            if (rows[r].value() == False):
                playnote[c*numrows+r] = 1
                
            else:
                playnote[c*numrows+r] = 0

        # Disable it again once done
        cols[c].value(True)


    # Now see if there are any off->on transitions to trigger MIDI on
    # or on->off to trigger MIDI off
    for n in range(0, len(playnote)):
        if (playnote[n] > 0):

            midiPitchBend(canal_1)
            midiPitchBend(canal_2)
            
            mod_wheel(canal_1)
            mod_13(canal_1)
            mod_12(canal_1)
            mod_91(canal_1)

            mod_wheel(canal_2)
            mod_13(canal_2)
            mod_12(canal_2)
            mod_91(canal_2)

            print( "ouaich midi ",  canal_1,canal_2)

            canal_1 = bouton1(canal_1)
            canal_2 = bouton2(canal_2)
           # ecrire()

        if (playnote[n] == 1 and lastnote[n] == 0):


            for o in grille_basses_notes:
                #print("######################################################################")
                #print("note : ",firstnote+o[n])

                if (n < 12):

                    if (bout_bass1.value()==0):
                        my_midi.send_note_on(midi.CHANNEL[canal_1], firstnote+o[n]-12, velocity)
                        my_midi.send_note_on(midi.CHANNEL[canal_1], firstnote+o[n], velocity)
                    if (bout_bass1.value()==1 & bout_bass2.value()==1):
                        my_midi.send_note_on(midi.CHANNEL[canal_1], firstnote+o[n], velocity)
                        my_midi.send_note_on(midi.CHANNEL[canal_1], firstnote+o[n]+24, velocity)
                        my_midi.send_note_on(midi.CHANNEL[canal_1], firstnote+o[n]+12, velocity)
                    if (bout_bass2.value()==0):
                        my_midi.send_note_on(midi.CHANNEL[canal_1], firstnote+o[n]+12, velocity)
                        my_midi.send_note_on(midi.CHANNEL[canal_1], firstnote+o[n]+24, velocity)


                if (n > 11):
                    if (bout_acc1.value()==0):
                        #utime.sleep_us(debounce_gate)
                        my_midi.send_note_on(midi.CHANNEL[canal_2], firstnote+o[n], velocity)
                        my_midi.send_note_on(midi.CHANNEL[canal_2], firstnote+o[n]+12, velocity)
                    if (bout_acc1.value()==1 & bout_acc2.value()==1):
                        #utime.sleep_us(debounce_gate)
                        my_midi.send_note_on(midi.CHANNEL[canal_2], firstnote+o[n]-12, velocity)
                        my_midi.send_note_on(midi.CHANNEL[canal_2], firstnote+o[n], velocity)
                        my_midi.send_note_on(midi.CHANNEL[canal_2], firstnote+o[n]+12, velocity)
                    if (bout_acc2.value()==0):
                        #utime.sleep_us(debounce_gate)
                        my_midi.send_note_on(midi.CHANNEL[canal_2], firstnote+o[n], velocity)
                        my_midi.send_note_on(midi.CHANNEL[canal_2], firstnote+o[n]-12, velocity)






        if (playnote[n] == 0 and lastnote[n] == 1):
            #print("####»»»»####»»»»####»»»»#####»»»»####»»»»####")
            utime.sleep_ms(debounce_gate)
            my_midi.send_note_off(midi.CHANNEL[1], firstnote+o[n])            
            my_midi.send_note_off(midi.CHANNEL[1], firstnote+o[n]+12)            
            my_midi.send_note_off(midi.CHANNEL[1], firstnote+o[n]+24)            
            my_midi.send_note_off(midi.CHANNEL[1], firstnote+o[n]-12)             
            my_midi.send_note_off(midi.CHANNEL[2], firstnote+o[n])            
            my_midi.send_note_off(midi.CHANNEL[2], firstnote+o[n]+12)            
            my_midi.send_note_off(midi.CHANNEL[2], firstnote+o[n]+24)            
            my_midi.send_note_off(midi.CHANNEL[2], firstnote+o[n]-12)            
         




 

        lastnote[n] = playnote[n]




