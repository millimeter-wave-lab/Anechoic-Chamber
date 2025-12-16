import pickle as pkl
import numpy as np
import argparse
import matplotlib.pyplot as plt
import csv

def save_to_csv(angles, s21_powers, filename):
    with open('measurements/' + filename + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Angle [°]", "S21 [dBm]"])

        # write the header
        for i in range(len(angles)):
            writer.writerow([angles[i], s21_powers[i]])

def get_point_values_from_curves(curves, point_number):
    point_values = []
    for i in range(len(curves)):
        point_values.append(curves[i][1][round(point_number)])

    return point_values

def plot_measurement(angle_list, s21_max_power_list, normalize, min_r, max_r, target_freq_ghz):
    # setting the axes projection as polar
    #plt.axes(projection = 'polar')
    
    # plotting the circle
    #for i in range(len(angle_list)):
    #    angle_in_rad = angle_list[i]*np.pi/180
    #    plt.polar(angle_in_rad, s21_max_power_list[i], 'b.')
    
    # display the Polar plot
    #plt.show()

    angle_in_rad = np.zeros(len(angle_list))
    for i in range(len(angle_list)):
        angle_in_rad[i] = angle_list[i]*np.pi/180

    plt.figure()
    ax = plt.subplot(111, polar = True)
    
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    if (normalize):
        target_r = s21_max_power_list-max(s21_max_power_list)
        ax.set_rlim(min_r,1)
        ax.set_title("Normalized radiation pattern at " +str(target_freq_ghz) + " GHz", va='bottom')
    else:
        target_r = s21_max_power_list
        ax.set_rlim(min_r,max_r)
        ax.set_title("Radiation pattern at " +str(target_freq_ghz) + " GHz", va='bottom')


    

    ax.plot(angle_in_rad, target_r, lw = 3)
    plt.show()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='plots a antenna anechoic chamber measurement'+
                                                 ' from a pkl file')
    parser.add_argument('filename', help='name of the file')
    parser.add_argument('-p','--point', type = int, help ='point of spectrum to observe, corresponds to a target frequency', default = 360)
    parser.add_argument('-minr','--minimum_radius', type = float, help ='minimum radius of the plot', default = -60)
    parser.add_argument('-maxr','--maximum_radius', type = float, help ='maximum radius of the plot', default = -10)
    parser.add_argument('--normalize', action='store_true',help="write this if you want to normalize the graph", default=True) 
    parser.add_argument('--dont_normalize', dest='normalize', action='store_false', help="write this if you don't want to normalize the graph")

    args = parser.parse_args()

    name = 'measurements/'
    if args.filename[-4:] == '.pkl':
        name = name + args.filename
    else:
        name = name + args.filename + '.pkl'
    
    try:
        file = open(name,'rb')
    except:
        print("File does not exist")

    # reading file and saving distances
    measure_list = []
    file_len_counter = 0
    while True:
        try:
            if file_len_counter == 0:
                parameters_dict = pkl.load(file)
            else:
                measure_list.append(pkl.load(file))
            file_len_counter += 1
        except:
            break
    file.close()

    # reading measurement parameters
    n_points = parameters_dict['CURVE_POINTS']
    min_freq = parameters_dict['MIN_FREQ']
    max_freq = parameters_dict['MAX_FREQ']

    angle_list = []
    curves_list = []
    for i in range(len(measure_list)):
        angle_list.append(measure_list[i][1])
        curves_list.append(measure_list[i][2])

    point_to_measure = args.point
    normalize = args.normalize
    target_freq_ghz = round(curves_list[0][0][point_to_measure]/1e9*100)/100
    max_radius = args.maximum_radius
    min_radius = args.minimum_radius

    #point_to_measure = n_points/2
    s21_max_power_list = get_point_values_from_curves(curves_list, point_to_measure)
    save_to_csv(angle_list, s21_max_power_list, args.filename + str())
    plot_measurement(angle_list, s21_max_power_list, normalize, min_radius, max_radius, target_freq_ghz)


    #plot_curve(distances[0][0])

