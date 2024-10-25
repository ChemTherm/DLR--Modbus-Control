import tkinter as tk
import time
import customtkinter as ctk
from PIL import Image,ImageTk
from datetime import datetime, timedelta
import json
from threading import Thread, Lock
from pyModbusTCP.client import ModbusClient
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_industrial_dual_0_20ma_v2 import BrickletIndustrialDual020mAV2
from tinkerforge.bricklet_industrial_dual_analog_in_v2 import BrickletIndustrialDualAnalogInV2

class TF_IndustrialDualAnalogIn:
    Voltage = [0,0]
 
    def __init__(self,ID_in,ipcon) -> None:
        self.obj = BrickletIndustrialDualAnalogInV2(ID_in, ipcon)   
        self.ID = ID_in
        #self.start()
       
    def get_voltages(self,TF_obj):
        self.Voltage = TF_obj.obj.get_all_voltages()

class TF_IndustrialDualAnalogIn_mA:
    current = [0,0]
    
    def __init__(self,ID_in,ipcon) -> None:
        self.obj = BrickletIndustrialDual020mAV2(ID_in, ipcon)    
        self.ID = ID_in
    
    def get_current(self,TF_obj):
        self.current[0] = TF_obj.obj.get_current(0)
        self.current[1] = TF_obj.obj.get_current(1)



modbus_controller = ModbusClient(host='192.168.1.3', port=502, auto_open=True, timeout=0.2)
ipcon = IPConnection() # Create IP connection
ipcon.connect("localhost", 4223) # Connect to brickd
dual_AI = TF_IndustrialDualAnalogIn("24xB", ipcon) 
dual_AI_mA = TF_IndustrialDualAnalogIn_mA("ZYk", ipcon) 


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
    global  t0, t_save
    T = modbus_controller.read_holding_registers( 2400, 6)
    label_T_ist[0].configure(text = str(T[0]/10)+" °C")
    label_T_ist[1].configure(text = str(T[1]/10)+" °C")
    label_T_ist[2].configure(text = str(T[2]/10)+" °C")
    label_T_ist[3].configure(text = str(T[3]/10)+" °C")
    label_T_ist[4].configure(text = str(T[4]/10)+" °C")
    label_T_ist[5].configure(text = str(T[5]/10)+" °C")
    DruckVerdampfer = dual_AI.get_voltages(dual_AI)
    DruckPumpe = dual_AI_mA.get_current(dual_AI_mA)
    DruckVerdampfer = dual_AI.Voltage[0]/(10000)*160 + 1  # umrechnen von mV in bar - Keller Druckmesser 0-160 0-10000 mV
    if DruckVerdampfer < 1:
        DruckVerdampfer = 1
    DruckPumpe = ((dual_AI_mA.current[1]-4e6) / 16e6 *100 )+1 # umrechnen von 4.20 mA in 0-100 bar
    if DruckPumpe < 1: 
        DruckPumpe = 1
    label_DruckVerdampfer.configure(text =  f"{DruckVerdampfer:.2f} bar")
    label_DruckPumpe.configure(text =  f"{DruckPumpe:.2f} bar")
    Statuswort= (int_to_bit_array(modbus_controller.read_holding_registers( 2000, 1)[0])) 
    Durchfluss= modbus_controller.read_holding_registers( 2100, 1)
    Leistung= modbus_controller.read_holding_registers( 2500, 1)
    label_Durchfluss.configure(text = str(Durchfluss[0])+" g/h")
    label_Leistung.configure(text = str(Leistung[0])+" W")
    An_Aus = Schalter_1.get() 
    modbus_controller.write_multiple_registers( 1000, [An_Aus])
    #print(Statuswort)
    for i in range(8):
        if Statuswort[-i-1]:
        # Setzt die Farbe auf Grün, wenn das Bit gesetzt ist
            led[i].configure(bg_color="green")
        else:
        # Setzt die Farbe auf Rot, wenn das Bit nicht gesetzt ist
            led[i].configure(bg_color="red")


    # Daten speichern:
    if save_trigger == 1 and time.time()- t_save > 0.5:
        with open(save_file, 'a') as file:            
            data_line = f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}\t"
            data_line += f"{T[0]/10}\t"
            data_line += f"{T[1]/10}\t"
            data_line += f"{T[2]/10}\t"
            data_line += f"{T[3]/10}\t"
            data_line += f"{T[4]/10}\t"
            data_line += f"{T[5]/10}\t"
            data_line += f"{Durchfluss[0]}\t"
            data_line += f"{Leistung[0]}\t"
            data_line += f"{DruckVerdampfer}\t"
            data_line += f"{DruckPumpe}"
            data_line += '\n'
            file.write(data_line)
            t_save = time.time()        

    window.after(50, tk_loop)

def getdata():    
    if F_Flow_value.get() != '':
        out = int(F_Flow_value.get())
        #print(out)
        modbus_controller.write_multiple_registers( 0x044C, [out])

def save_data(): 
    global t_save, save_trigger 
    if save_trigger == 1:
        save_trigger = 0
        button2.config(text="Save Data")
    else:    
        save_trigger = 1
        button2.config(text="Stop Save")
        t_save = time.time()        
        with open(save_file, 'a') as file:
            header_line = '### New Data \n Zeitpunkt \t T1 \t T2 \t T3 \t T4 \t T5 \t T6 \t Flow \t Leistung \t p_Verdampfer\t p_Pumpe'
            header_line += '\n'
            file.write(header_line)


save_file = "Daten.dat"

t0 = time.time()
t_save = time.time()
save_trigger = 0
window = ctk.CTk()
# Setze den Erscheinungsmodus auf "dark"
ctk.set_appearance_mode("dark")

# Bildschirmgröße abrufen
scrW = window.winfo_screenwidth()  # 2560
scrH = window.winfo_screenheight()  # 1440
window.geometry(f"{scrW}x{scrH}")
window.title("DLR-Modbus Control")
window.attributes('-fullscreen',True)

#----------- Images ----------- 
#close_img = ctk.CTkImage(Image.open(config['PATH']['images'] + 'close.png'),size=(80, 80))
bg_image = ctk.CTkImage(Image.open("HauptBild.png"),size=(1553, 798))

#----------- Labels -----------
label_background = ctk.CTkLabel(window,image=bg_image,text="")
x_offset = 50
y_offset = 50
label_background.place(x = x_offset,y = y_offset)
label_background.lower()


label_T_ist ={}
led ={}
led_label ={}
label_T_ist[0] = ctk.CTkLabel(window, font = ('Arial',24), text='0 °C',bg_color="white", text_color="#000000")
label_T_ist[0].place(x = 420 , y = 160)
label_T_ist[1] = ctk.CTkLabel(window, font = ('Arial',24), text='0 °C',bg_color="white", text_color="#000000")
label_T_ist[1].place(x = 630 , y = 490)
label_T_ist[2] = ctk.CTkLabel(window, font = ('Arial',24), text='0 °C',bg_color="white", text_color="#000000")
label_T_ist[2].place(x = 610 , y = 160)
label_T_ist[3] = ctk.CTkLabel(window, font = ('Arial',24), text='0 °C',bg_color="white", text_color="#000000")
label_T_ist[3].place(x = 1050 , y = 160)
label_T_ist[5] = ctk.CTkLabel(window, font = ('Arial',24), text='0 °C',bg_color="white", text_color="#000000")
label_T_ist[5].place(x = 1350 , y = 160)
label_T_ist[4] = ctk.CTkLabel(window, font = ('Arial',24), text='0 °C',bg_color="white", text_color="#000000")
label_T_ist[4].place(x = 750 , y = 760)

label_Durchfluss = ctk.CTkLabel(window, font = ('Arial',24), text='0 kg/h',bg_color="white", text_color="#000000")
label_Durchfluss.place(x = 240 , y = 490)

label_Leistung = ctk.CTkLabel(window, font = ('Arial',24), text='0 W',bg_color="white", text_color="#000000")
label_Leistung.place(x = 440 , y = 490)


label_DruckPumpe = ctk.CTkLabel(window, font = ('Arial',24), text='0 bar',bg_color="white", text_color="#000000")
label_DruckPumpe.place(x = 470 , y = 785)


label_DruckVerdampfer = ctk.CTkLabel(window, font = ('Arial',24), text='0 bar',bg_color="white", text_color="#000000")
label_DruckVerdampfer.place(x = 940 , y = 540)

Schalter_1 =  ctk.CTkSwitch(window, text="An/Aus", width=150, height=70, font = ('Arial',24))
Schalter_1.place(x = 1260 , y = 450)
x_LED = 1250
y_LED = 520
led[0] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[0].place(x = x_LED , y = y_LED)
led_label[0] = ctk.CTkLabel(window, font = ('Arial',24), text='Power')
led_label[0].place(x = x_LED+50 , y = y_LED+10)
led[4] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[4].place(x = x_LED+200 , y = y_LED)
led_label[4] = ctk.CTkLabel(window, font = ('Arial',24), text='T Sicherheit')
led_label[4].place(x = x_LED+250 , y = y_LED+10)

y_LED = 620

led[1] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[1].place(x = x_LED , y = y_LED)
led_label[1] = ctk.CTkLabel(window, font = ('Arial',24), text='Rückdruck')
led_label[1].place(x = x_LED+50 , y = y_LED+10)
led[5] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[5].place(x = x_LED+200 , y = y_LED)
led_label[5] = ctk.CTkLabel(window, font = ('Arial',24), text='P + V')
led_label[5].place(x = x_LED+250 , y = y_LED+10)

y_LED = 720

led[2] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[2].place(x = x_LED , y = y_LED)
led_label[2] = ctk.CTkLabel(window, font = ('Arial',24), text='Ventil')
led_label[2].place(x = x_LED+50 , y = y_LED+10)
led[6] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[6].place(x = x_LED+200 , y = y_LED)
led_label[6] = ctk.CTkLabel(window, font = ('Arial',24), text='Auto/Hand')
led_label[6].place(x = x_LED+250 , y = y_LED+10)

y_LED = 820

led[3] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[3].place(x = x_LED , y = y_LED)
led_label[3] = ctk.CTkLabel(window, font = ('Arial',24), text='Temp')
led_label[3].place(x = x_LED+50 , y = y_LED+10)
led[7] = ctk.CTkLabel(window, text="", width=40, height=40, bg_color="red")
led[7].place(x = x_LED+200 , y = y_LED)
led_label[7] = ctk.CTkLabel(window, font = ('Arial',24), text='COM')
led_label[7].place(x = x_LED+250 , y = y_LED+10)

y_Flow = 420
F_Flow_text= ctk.CTkLabel(window, font = ('Arial',24), text="Massenstrom")
F_Flow_text.place(x = x_LED , y = y_Flow)
F_Flow_value= tk.Entry(window, font = ('Arial',24), width = 4 )
F_Flow_value.insert(0, '0')     
F_Flow_value.place(x = x_LED+150 , y = y_Flow-5)
F_Flow_unit= ctk.CTkLabel(window, font = ('Arial',24), text=' g/h')
F_Flow_unit.place(x = x_LED+230 , y = y_Flow)

button1 = tk.Button(window, text='Set Values', command=getdata, bg='brown', fg='white', width=10, height=1, font=('Arial', 20))
button1.place(x = 1670 , y =390)


button2 = tk.Button(window, text='Save Values', command=save_data, bg='brown', fg='white', width=10, height=1, font=('Arial', 20))
button2.place(x = 1670 , y = 450)

window.after(1000, tk_loop())
window.mainloop()
modbus_controller.close()

print("shutting down...")