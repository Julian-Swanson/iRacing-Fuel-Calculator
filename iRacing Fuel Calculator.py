import irsdk
import time
import tkinter as tk
from tkinter import ttk
import threading

#GLOBAL VARIABLES

ir = irsdk.IRSDK()

availability = ['', 0]
calculating_fuel_status = ['Calculating status', 'red']

fuel_capacity = 0
fuel_current = 0
fuel_avg_lap = 0
avg_lap_time = 0
time_hours = 0
time_minutes = 0
time_seconds = 0
pit_stop_time = 0

torf_iracing_color = 'red'

iracing_fuel_data_off = True

stop_lap_check = False

#UI STARTUP

master = tk.Tk()
master.geometry('500x650')
master.title('Fuel Calculator')
master.configure(background='whitesmoke')

#INPUTS

fuel1_var = tk.StringVar()
fuel2_var = tk.StringVar()
fuel3_var = tk.StringVar()
lapavg_var = tk.StringVar()
hour_var = tk.StringVar()
minute_var = tk.StringVar()
seconds_var = tk.StringVar()
pitstop_var = tk.StringVar()

toggle_iracing_var = tk.IntVar()

fuel1_value = 0
fuel2_value = 1
fuel3_value = 2
lapavg_value = 3
hour_value = 4
minute_value = 5
seconds_value = 6
pitstop_value = 7

label_entry_list_name = ['fuel1_label', 'fuel2_label', 'fuel3_label', 'lapavg_label', 'hour_label', 'minute_label', 'seconds_label', 'pitstop_label']
label_entry_list_text = ['Max fuel capacity in litres', 'Current fuel in litres', 'Average fuel usage per lap in litres', 'Average lap time in seconds', 'Hours', 'Minutes', 'Seconds', 'Pitstop time in seconds']

entry_list_name = ['fuel1_entry', 'fuel2_entry', 'fuel3_entry', 'lapavg_entry', 'hour_entry', 'minute_entry', 'seconds_entry', 'pitstop_entry']
entry_list_var = [fuel1_var, fuel2_var, fuel3_var, lapavg_var, hour_var, minute_var, seconds_var, pitstop_var]

label_dict = {}
entry_dict = {}

def label_entry_dict_maker():
    for a, b, x, y, z in zip(entry_list_name, entry_list_var, label_entry_list_name, label_entry_list_text, range(0, len(label_entry_list_name))):
        x = ttk.Label(master, text=y)
        label_dict[z] = x
        a = ttk.Entry(master, textvariable=b)
        entry_dict[z] = a

###-----------------FUNCTIONS-----------------###

def iracing_startup_notifications():
    
    ir.startup()

    if not ir.startup():
        print("iRacing not running")

    if ir.is_connected:
        print("Connected to session")
    else:
        print("Not connected")

def check_status():

    global availability
    global iracing_fuel_data_off

    if iracing_fuel_data_off:
        
        availability = ["Not asking for data from iRacing", 1]

    elif not ir.is_connected:

        availability = ['iRacing not running', 1]

    elif (ir['FuelCapacity'] == None) and not iracing_fuel_data_off:

        availability = ["Fuel capacity data from iRacing not being transmitted.", 2]

    elif (ir['FuelLevel'] == None):
       
        availability = ["Fuel level data from iRacing not being transmitted.", 3]

    elif (ir['FuelCapacity'] == None) and (ir['FuelLevel'] == None) and not iracing_fuel_data_off:
        
        availability = ["No data from iRacing transmitted.", 1]
    
    else:
        availability = ["All data being transmitted", 4]

def fuel_average_calculator():

    global fuel_avg_lap

    previous_lap = None
    fuel_start = None
    fuel_consumption_per_lap = []

    print("Called Fuel Average Calculator")

    try:
        while True:
            ir.freeze_var_buffer_latest()
            
            current_lap = ir['Lap']
            current_fuel = ir['FuelLevel']
            
            if previous_lap is not None and current_lap > previous_lap:
                if fuel_start is not None:

                    fuel_used = fuel_start - current_fuel

                    print("Fuel used", fuel_used)

                    if fuel_used > 0:
                        
                        fuel_consumption_per_lap.append(fuel_used)
                        print(f"Lap {current_lap} completed. Fuel Used: {fuel_used:.2f} L")
                    
                        fuel_avg_lap = sum(fuel_consumption_per_lap) / len(fuel_consumption_per_lap)
                        print(f"Average Fuel Per Lap: {fuel_avg_lap:.2f} L")                        
                        data_submit()
                        calculating_label.configure(text="Fuel calculated", background='green')
                        break

                fuel_start = current_fuel
            
            previous_lap = current_lap
            
            if fuel_start is None:
                fuel_start = current_fuel
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        print("Check fuel average off")

def lap_check():

    print("lap check called")

    previous_lap = None

    while True:

        print("While-loop")

        ir.freeze_var_buffer_latest
        current_lap = ir['Lap']

        if previous_lap == None:
            previous_lap = current_lap
            print("called prev lap")
        
        elif previous_lap < current_lap:
            print("called step 3")
            calculating_label.configure(text='Calculating fuel average...', background='yellow')
            master.after(200, fuel_average_calculator)
            break

        else:
            time.sleep(0.1)
            print("called step 4")

def data_submit():

    global output1
    global output2
    global output3
    global output4
    global fuel_avg_lap
    global availability
    
    try:
        check_status()
        print(availability[0])

        output1.delete('1.0', 'end')
        output2.delete('1.0', 'end')
        output3.delete('1.0', 'end')
        output4.delete('1.0', 'end')

        if availability[1] == 1:

            fuel_capacity = float(fuel1_var.get())
            fuel_current = float(fuel2_var.get())
            fuel_avg_lap = float(fuel3_var.get())

        elif availability[1] == 2:

            fuel_capacity = float(fuel1_var.get())
            fuel_current = ir['FuelLevel']

            print(fuel_capacity, fuel_current)
            
            if fuel_avg_lap == None:
                print("Wait")
            
            else:
                print(fuel_avg_lap)

        elif availability[1] == 3:
        
            fuel_capacity = ir['FuelCapacity']
            fuel_current = float(fuel2_var.get())
            fuel_avg_lap = float(fuel3_var.get())

        else:

            fuel_capacity = ir['FuelCapacity']
            fuel_current = ir['FuelLevel']

            print(fuel_capacity, fuel_current)
            print(fuel_avg_lap)



        avg_lap_time = float(lapavg_var.get())
        time_hours = float(hour_var.get())
        time_minutes = float(minute_var.get())
        time_seconds = float(seconds_var.get())
        pit_stop_time = float(pitstop_var.get())
        
        fuel_counter = fuel_current
        lap_counter = 0
        pit_stop_counter = 0
        time_counter = (time_hours*3600)+(time_minutes*60)+time_seconds

        if fuel_avg_lap == None:
            print("wait")
        
        if fuel_counter == None:
            print("whiuf")

        while True:

            if time_counter > 0:
                if (fuel_counter > fuel_avg_lap*1.02):
                    fuel_counter -= fuel_avg_lap
                    lap_counter += 1
                    time_counter -= avg_lap_time
                else: #elif (fuel_counter <= fuel_avg_lap):
                    time_counter -= (pit_stop_time+avg_lap_time)
                    pit_stop_counter += 1
                    lap_counter += 1
                    fuel_counter = fuel_capacity - fuel_avg_lap
            else:            
                total_fuel = lap_counter*fuel_avg_lap
                laps_across_stint = fuel_capacity // fuel_avg_lap
                final_laps_stint = lap_counter % laps_across_stint
                final_fuel_stint = final_laps_stint * fuel_avg_lap

                if final_fuel_stint == 0:
                    final_fuel_stint = fuel_capacity

                info = ('laps: '+str(lap_counter)+' Pit stops: '+str(pit_stop_counter)+' Final fuel stint: '+str(final_fuel_stint)) 

                print(total_fuel)
                print(info)
                output1.insert(tk.END, lap_counter)
                output2.insert(tk.END, pit_stop_counter)
                output3.insert(tk.END, final_fuel_stint)
                output4.insert(tk.END, fuel_avg_lap)
                break
    except KeyboardInterrupt:
        print("Exiting...")
    else:
        print("Error")
    finally:
        print("Finished Calculation")
    

def return_pressed(event):
    
    if master.focus_get() == entry_dict[pitstop_value]:
        print("worked")
        calculate_choose()
    else:
        event.widget.tk_focusNext().focus()
    
def up_key_pressed(event):

    event.widget.tk_focusPrev().focus()

def down_key_pressed(event):

    event.widget.tk_focusNext().focus()

def toggle_iracing():
   
    global iracing_fuel_data_off

    if toggle_iracing_var.get() == 1:
        iracing_fuel_data_off = False
        print("on")
        delete_ui()
        create_ui()

    else:
        iracing_fuel_data_off = True
        print("off")
        delete_ui()
        create_ui()

def calculate_choose():

    global availability

    if availability[1] == 2 or availability[1] == 4:
        
        calculating_label.configure(text='Calculating laps...', background='orange')    
        master.after(200, lap_check)
    
    elif availability[1] == 1:
        data_submit()
    else:
        data_submit()

def delete_ui():

    for widget in master.winfo_children():
        widget.destroy()

def create_ui():
    
    global output1
    global output2
    global output3
    global output4
    global iracing_connected_label
    global torf_iracing_color
    global availability
    global calculating_label

    label_entry_dict_maker()

    top_label = ttk.Label(master, text = 'Please add some margin so that there are not any huge mistakes.'
                     , background='gainsboro', foreground='dodgerblue', font=('Helvetica', 11))
    
    iracing_connected_label = ttk.Label(master, text= availability[0], background=torf_iracing_color, font=('Arial', 10, 'bold'))

    submit_button = ttk.Button(master, text = "Calculate", command = calculate_choose)

    calculating_label = ttk.Label(master, text = 'Calculating status', background='red')

    toggle_iracing_button = ttk.Checkbutton(master, text="Toggle iRacing Fuel Data", variable=toggle_iracing_var, onvalue=1, offvalue=0
                                        , command=toggle_iracing)

    space_label = ttk.Label(master, text = '')

    output1 = tk.Text(master, height = 2, width = 52)
    output1_label = ttk.Label(master, text='Total laps')
    output2 = tk.Text(master, height = 2, width = 52)
    output2_label = ttk.Label(master, text='Total pit stops')
    output3 = tk.Text(master, height = 2, width = 52)
    output3_label = ttk.Label(master, text='Litres for final stint')
    output4 = tk.Text(master, height = 2, width = 52)
    output4_label = ttk.Label(master, text='Fuel average')

    master.bind("<Return>", return_pressed)
    master.bind("<Up>", up_key_pressed)
    master.bind("<Down>", down_key_pressed)

    ###.pack items###
    
    top_label.pack()

    check_status()

    if availability[1] == 1:
        label_dict[fuel1_value].pack()
        entry_dict[fuel1_value].pack()
        label_dict[fuel2_value].pack()
        entry_dict[fuel2_value].pack()
        label_dict[fuel3_value].pack()
        entry_dict[fuel3_value].pack()
        master.geometry('500x650')

    if availability[1] == 2:
        label_dict[fuel1_value].pack()
        entry_dict[fuel1_value].pack()
        master.geometry('500x600')

    if availability[1] == 3:
        label_dict[fuel2_value].pack()
        entry_dict[fuel2_value].pack()
        label_dict[fuel3_value].pack()
        entry_dict[fuel3_value].pack()
        master.geometry('500x600') 

    for n in range(3, 8):
        label_dict[n].pack()
        entry_dict[n].pack()

    submit_button.pack()
    
    if (availability[1]) == (2 or 4):
        calculating_label.pack()

    toggle_iracing_button.pack()

    space_label.pack()

    output1_label.pack()
    output1.pack()
    output2_label.pack()
    output2.pack()
    output3_label.pack()
    output3.pack()
    if availability[1] == 2 or availability[1] == 4:
        output4_label.pack()
        output4.pack()
    iracing_connected_label.pack()

def connected_status():

    global iracing_connected_label
    global torf_iracing_color

    if ir.is_connected:
        torf_iracing_color = "Green"
    else:
        torf_iracing_color = "Red"

    check_status()

    iracing_connected_label.configure(text=availability[0], background=torf_iracing_color)
    master.after(1, connected_status)

create_ui()
iracing_startup_notifications()
connected_status()
master.mainloop()
