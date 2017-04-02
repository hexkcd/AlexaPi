
import radio
from microbit import *

think = [Image("00000:"
             "00000:"
             "09090:"
             "90909:"
             "00000"), Image("00000:"
             "00000:"
             "90909:"
             "09090:"
             "00000")]

waiting = Image("09990:"
             "90009:"
             "00990:"
             "00000:"
             "00900")

listen = Image("09990:"
             "90009:"
             "00909:"
             "09009:"
             "00990")

talk = [Image.SQUARE, Image.SQUARE_SMALL, Image("00000:"
             "00000:"
             "00900:"
             "00000:"
             "00000"), Image.SQUARE_SMALL]

ticker = 0
buttonStat = "off"
alexaStat = "waiting"
remote = True

radio.on()

while True:
    ticker = ticker+1
    if (ticker%len(think)==0) and (ticker%len(talk)==0):
        ticker = 0
        
    stat = "on" if button_a.is_pressed() else "off"
    if stat != buttonStat:
        if remote:
            buttonStat = stat
            radio.send(buttonStat)
    
    if not pin1.is_touched() and not pin2.is_touched():
        stat = "thinking"
    elif not pin1.is_touched():
        stat = "talking"
    elif not pin2.is_touched():
        stat = "listening"
    else:
        stat = "waiting"
        remote = False
        
    if stat != alexaStat:
        if not remote:
            alexaStat = stat
            radio.send(alexaStat)
    
    msg = radio.receive()
    if msg in ["on", "off"]:
        buttonStat = msg
    elif msg in ["listening", "waiting", "thinking", "talking"]:
        alexaStat = msg

    if buttonStat == "on":
        pin0.write_digital(1)
    else:
        pin0.write_digital(0)
    
    if alexaStat == "thinking":
        display.show(think[ticker%len(think)])
        sleep(50)
    elif alexaStat == "talking":
        display.show(talk[ticker%len(talk)])
        sleep(50)
    elif alexaStat == "listening":
        display.show(listen)
    elif alexaStat == "waiting":
        display.show(waiting) 
        
        
