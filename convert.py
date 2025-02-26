from scipy.interpolate import interp1d

def convert(voltage):
    global spline_model
   
    # Moved voltages and weights arrays here for clarity
                #1000        #900           #800        #700            #*600
    voltages = [968.9, 967.3, 965.0, 959.7, 953.5, 950.6, 937.6, 933.5, 923.5, 889.3, 868.6, 755.4, 559.3, 133.8, 118.6, 30.6, 23.4, 16.9, 0]
    weights = [1000, 950, 900, 850, 800, 750, 700, 650, 600, 550, 500, 450, 400, 350, 300, 250, 200, 150, 0]
    
    spline_model = interp1d(voltages, weights, kind='linear', fill_value="extrapolate")

    return float(spline_model(voltage))


voltages = []

with open("etc/test1", "r") as f:
    for i in f:
        voltages.append(i)
        
for n in voltages: 
    with open("etc/test1_weight", "a") as f:
        data = f"{convert(n)}\n"
        f.write(data)