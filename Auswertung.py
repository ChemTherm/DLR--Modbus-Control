import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pandas as pd
import pickle
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots


ordner = "./"
filename = ordner + "2024-10-25_2_Daten"
counter = 0

with open(filename + ".dat", 'r') as file: 
    for _ in range(5):
        skipped_line = file.readline()  # Überspringe die ersten fünf Zeilen
    headers = file.readline().strip().split('\t') # Lese die Überschriften aus der ersten Zeile
    for i in range(len(headers)):
         headers[i] =headers[i].replace(" ", "")
    data_Anlage = {}
    for header in headers:
        data_Anlage[header] = [] # Erstelle eine leere Liste für jede Überschrift

    for num, line in enumerate(file):
        values = line.strip().split('\t')
        #print(line)
        if "#" in line or headers[1] in values[1] :
            counter += 1
            continue
        for i in range(len(headers)):
            values[i].replace(" ", "")
            if ':' in values[i]:        
                time = datetime.strptime(values[i][:-4], '%Y-%m-%d %H:%M:%S.%f')
                data_Anlage[headers[i]].append(time) # Füge die Uhrzeit als time-Objekt hinzu
            else:    
                try:  
                    value = float(values[i].replace(',', '.'))
                except ValueError:
                    value = 0.0
                data_Anlage[headers[i]].append(value) # Füge den Wert zur entsprechenden Liste hinzu

""" data_Anlage['F_1'] = ((pd.Series(data_Anlage['F_1'])/ 1e6) - 4) / (20-4) * (20-0) +0
data_Anlage['Verdampfer'] = ((pd.Series(data_Anlage['Verdampfer'])/ 1e6) - 4) / (20-4) * (6000-0) +0
data_Anlage['p_1'] = ((pd.Series(data_Anlage['p_1'])/ 1e6) - 4) / (20-4) * (100-0) +1 """

data_Anlage['Zeitpunkt'] = pd.to_datetime(data_Anlage['Zeitpunkt'], format='%Y-%m-%d %H:%M:%S.%f')
first_time = data_Anlage['Zeitpunkt'][0]
last_time = data_Anlage['Zeitpunkt'][-1]
time_diffs = [(t - first_time).total_seconds() / 60 for t in data_Anlage['Zeitpunkt']]
data_Anlage['runTime'] = time_diffs


# Berechnung durchführen
# Erstelle ein Plotly-Subplot-Objekt mit zwei getrennten Plots, die auf der X-Achse synchronisiert sind
fig = make_subplots(rows=2, cols=2, shared_xaxes='all', 
                    vertical_spacing=0.1,  # Abstand zwischen den Diagrammen
                    subplot_titles=("Temperaturverlauf", "Heizleistung", "Flow", "Druck"))

# Füge das erste Plot (Temperaturen) in die erste Zeile ein
fig.add_trace(go.Scatter(x=data_Anlage['runTime'][::2], y=data_Anlage['T1'][::2],
                         mode='lines', name='Heizpatrone', line=dict(width=4)),
              row=1, col=1)

fig.add_trace(go.Scatter(x=data_Anlage['runTime'][::2], y=data_Anlage['T2'][::2],
                         mode='lines', name='Innen_1', line=dict(width=4)),
              row=1, col=1)

fig.add_trace(go.Scatter(x=data_Anlage['runTime'][::2], y=data_Anlage['T3'][::2],
                         mode='lines', name='Innen_2', line=dict(width=4, color='darkgreen')),
              row=1, col=1)
fig.add_trace(go.Scatter(x=data_Anlage['runTime'][::2], y=data_Anlage['T4'][::2],
                         mode='lines', name='Außen', line=dict(width=4)),
              row=1, col=1)
fig.add_trace(go.Scatter(x=data_Anlage['runTime'][::2], y=data_Anlage['T5'][::2],
                         mode='lines', name='Zulauf', line=dict(width=4)),
              row=1, col=1)
fig.add_trace(go.Scatter(x=data_Anlage['runTime'][::2], y=data_Anlage['T6'][::2],
                         mode='lines', name='Austritt', line=dict(width=4)),
              row=1, col=1)
# Füge das zweite Plot (Flow) in die zweite Zeile ein
fig.add_trace(go.Scatter(x=data_Anlage['runTime'][::2], y = data_Anlage['Leistung'][::2],
                         mode='lines', name='Heizleistung', line=dict(width=4)),
              row=1, col=2)
# Füge das zweite Plot (Flow) in die zweite Zeile ein
fig.add_trace(go.Scatter(x=data_Anlage['runTime'][::2], y = data_Anlage['Flow'][::2],
                         mode='lines', name='Flow', line=dict(width=4)),
              row=2, col=1)

# Füge das dritte Plot (Druck) in die zweite Zeile ein
fig.add_trace(go.Scatter(x=data_Anlage['runTime'][::2], y=data_Anlage['p_Verdampfer'][::2],
                         mode='lines', name='Druck', line=dict(width=4, color='blue')),
              row=2, col=2)
fig.add_trace(go.Scatter(x=data_Anlage['runTime'][::2], y=data_Anlage['p_Pumpe'][::2],
                         mode='lines', name='Druck', line=dict(width=4, color='blue')),
              row=2, col=2)


# Layout anpassen
fig.update_layout(
    xaxis=dict(title='Zeit / min'),  # Gemeinsame X-Achse
    yaxis=dict(title='Temperatur / °C', range=[20, 500]),
    yaxis2=dict(title='Heizleistung / Watt'),
    xaxis2=dict(title='Zeit / min'),  # Gemeinsame X-Achse
    yaxis3=dict(title='Flow / kg/h'),
    xaxis3=dict(title='Zeit / min'),  # Gemeinsame X-Achse
    yaxis4=dict(title='Pressure / bar'),
    xaxis4=dict(title='Zeit / min', range=[0, 90]),  # Gemeinsame X-Achse
    font=dict(size=18, family='Garamond'),
    legend=dict(
        orientation='h',  # Horizontale Ausrichtung der Legende
        yanchor="bottom", y=1.15,  # Position über den Diagrammen
        xanchor="center", x=0.5
    ),
    height=1200,  # Gesamthöhe der Grafik
    template="plotly_white"
)

# Speichere die gekoppelte Figur als HTML-Datei
pio.write_html(fig, file=filename + ".html", full_html=True)

# Zeige die Figur an
fig.show()
