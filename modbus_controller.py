import tkinter as tk
import time
import customtkinter as ctk
from PIL import Image,ImageTk
from datetime import datetime, timedelta
import json
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient

modbus_controller = ModbusClient(host='192.168.1.3', port=502, auto_open=True, timeout=0.2)
def int_to_bit_array(value, signed=False):
    # Überprüfen, ob es sich um eine signed oder unsigned Zahl handelt
    if signed:
        if value < -32768 or value > 32767:
            raise ValueError("Value out of range for signed 16-bit integer")
        # 2er-Komplement für signed
        value = (1 << 16) + value if value < 0 else value
    else:
        if value < 0 or value > 65535:
            raise ValueError("Value out of range for unsigned 16-bit integer")
    
    # Umwandeln in Binär, mit 16 Bit
    binary_str = format(value, '016b')
    
    # Array erstellen, wo jedes Bit in einen Index (0 bis 15) kommt
    bit_array = [int(bit) for bit in binary_str]

    return bit_array

def tk_loop():
    global  t0
    T = modbus_controller.read_holding_registers( 2400, 4)
    lable_T_ist[0].configure(text = str(T[0]/10)+" °C")
    lable_T_ist[1].configure(text = str(T[1]/10)+" °C")
    lable_T_ist[2].configure(text = str(T[2]/10)+" °C")
    lable_T_ist[3].configure(text = str(T[3]/10)+" °C")
    #lable_T_ist[4].configure(text = str(T[4]/10)+" °C")
    Statuswort= (int_to_bit_array(modbus_controller.read_holding_registers( 2000, 1)[0])) 
    #print(Statuswort)
    for i in range(8):
        if Statuswort[-i-1]:
        # Setzt die Farbe auf Grün, wenn das Bit gesetzt ist
            led[i].configure(bg_color="green")
        else:
        # Setzt die Farbe auf Rot, wenn das Bit nicht gesetzt ist
            led[i].configure(bg_color="red")


    window.after(50, tk_loop)

def getdata():    
    if F_Flow_value.get() != '':
        out = int(F_Flow_value.get())
        print(out)
        modbus_controller.write_multiple_registers( 0x044C, [out])


'''' 
====================================
SETUP 
====================================
'''
t0 = time.time()
section_time = time.time()

""" 
filename = "test2.dat"
with open("D:/Daten/" + filename, 'a') as f:
    headline = "time \t T1 \t T2 \t T3 \t T4 \t p1 \t p2 \t P1 \t Flow1 \n"
    f.writelines(headline)

with open('img/setting.json', 'r') as img_file:
    img = json.load(img_file) """


window = ctk.CTk()
ctk.set_appearance_mode("light")
scrW = window.winfo_screenwidth() #2560
scrH = window.winfo_screenheight() #1440
window.geometry(str(scrW) + "x" + str(scrH))
window.title("DLR-Modbus Control")
window.configure(bg= "#F2F2F2")
window.attributes('-fullscreen',True)
print(scrW)
print(scrH)
#----------- Images ----------- 
#close_img = ctk.CTkImage(Image.open(config['PATH']['images'] + 'close.png'),size=(80, 80))
bg_image = ctk.CTkImage(Image.open("HauptBild.png"),size=(1553, 798))

#----------- Labels -----------
label_background = ctk.CTkLabel(window,image=bg_image,text="")
x_offset = 50
y_offset = 50
label_background.place(x = x_offset,y = y_offset)
label_background.lower()


lable_T_ist ={}
led ={}
led_label ={}
lable_T_ist[0] = ctk.CTkLabel(window, font = ('Arial',20), text='0 °C',bg_color="white")
lable_T_ist[0].place(x = 630 , y = 490)
lable_T_ist[1] = ctk.CTkLabel(window, font = ('Arial',20), text='0 °C',bg_color="white")
lable_T_ist[1].place(x = 410 , y = 160)
lable_T_ist[2] = ctk.CTkLabel(window, font = ('Arial',20), text='0 °C',bg_color="white")
lable_T_ist[2].place(x = 610 , y = 160)
lable_T_ist[3] = ctk.CTkLabel(window, font = ('Arial',20), text='0 °C',bg_color="white")
lable_T_ist[3].place(x = 990 , y = 160)
lable_T_ist[4] = ctk.CTkLabel(window, font = ('Arial',20), text='0 °C',bg_color="white")
lable_T_ist[4].place(x = 1350 , y = 160)
lable_T_ist[5] = ctk.CTkLabel(window, font = ('Arial',20), text='0 °C',bg_color="white")
lable_T_ist[5].place(x = 750 , y = 760)

Schalter_1 =  ctk.CTkSwitch(window, text="Schalter 1")
Schalter_1.place(x = 1250 , y = 760)
x_LED = 1250
y_LED = 520
led[0] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[0].place(x = x_LED , y = y_LED)
led_label[0] = ctk.CTkLabel(window, font = ('Arial',20), text='Power')
led_label[0].place(x = x_LED+50 , y = y_LED+10)
led[4] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[4].place(x = x_LED+200 , y = y_LED)
led_label[4] = ctk.CTkLabel(window, font = ('Arial',20), text='T Sicherheit')
led_label[4].place(x = x_LED+250 , y = y_LED+10)

y_LED = 620

led[1] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[1].place(x = x_LED , y = y_LED)
led_label[1] = ctk.CTkLabel(window, font = ('Arial',20), text='Rückdruck')
led_label[1].place(x = x_LED+50 , y = y_LED+10)
led[5] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[5].place(x = x_LED+200 , y = y_LED)
led_label[5] = ctk.CTkLabel(window, font = ('Arial',20), text='P + V')
led_label[5].place(x = x_LED+250 , y = y_LED+10)

y_LED = 720

led[2] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[2].place(x = x_LED , y = y_LED)
led_label[2] = ctk.CTkLabel(window, font = ('Arial',20), text='Ventil')
led_label[2].place(x = x_LED+50 , y = y_LED+10)
led[6] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[6].place(x = x_LED+200 , y = y_LED)
led_label[6] = ctk.CTkLabel(window, font = ('Arial',20), text='Auto/Hand')
led_label[6].place(x = x_LED+250 , y = y_LED+10)

y_LED = 820

led[3] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[3].place(x = x_LED , y = y_LED)
led_label[3] = ctk.CTkLabel(window, font = ('Arial',20), text='Temp')
led_label[3].place(x = x_LED+50 , y = y_LED+10)
led[7] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[7].place(x = x_LED+200 , y = y_LED)
led_label[7] = ctk.CTkLabel(window, font = ('Arial',20), text='COM')
led_label[7].place(x = x_LED+250 , y = y_LED+10)

y_Flow = 420
F_Flow_text= ctk.CTkLabel(window, font = ('Arial',20), text="Massenstrom")
F_Flow_text.place(x = x_LED , y = y_Flow)
F_Flow_value= tk.Entry(window, font = ('Arial',20), width = 8 )
F_Flow_value.insert(0, '0')     
F_Flow_value.place(x = 2055 , y = 630)
F_Flow_unit= ctk.CTkLabel(window, font = ('Arial',20), text=' g/h')
F_Flow_unit.place(x = x_LED+200 , y = y_Flow)

button1 = tk.Button(window, text='Set Values', command=getdata, bg='brown', fg='white', width=12, height=2, font=('Arial', 20))
button1.place(x = 1645 , y = 630)

window.after(1000, tk_loop())
window.mainloop()


print("shutting down...")