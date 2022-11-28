import matplotlib.pyplot as plt
import re
import os
import numpy as np

file_ending = ".xrdml"

# Decide where to put vertical lines

# interesting_peaks = {'NGO': 47.0043, '001': 6.4, '002':	12.83, '003':	19.3, '004': 25.82, '005': 32.44, '006':	39.17, '007':	46.04, '008': 53.09, '009':	60.37, '0010':	67.92, '0011': 75.83, '0012': 84.19, '0013' : 93.14}

# interesting_peaks = {'001': 8.84, '002':	17.73, '003':	26.73, '004': 35.9, '005': 45.32	, '006':	55.07,
#  '007':	65.27	, '008': 76.1, '009':	87.8, '0010':	100.79, '0011': 75.83, '0012': 84.19, '0013' : 93.14}

interesting_peaks = {'001': 8.84, '002':	17.73, '003':	26.73, '004': 35.9, '005': 45.32	, '006':	55.07,
 '007':	65.27	, '008': 76.1}

# interesting_peaks = {}
							
# Extract all xrdml files in children folders
xrdml_folder_file_dict = {}
folder_list = [dir for dir in os.listdir() if os.path.isdir(dir)]
for folder in folder_list:
  folder_xrdml_file_list = [f[:-len(file_ending)] for f in os.listdir(folder) if f.endswith(file_ending)]
  xrdml_folder_file_dict[folder] = folder_xrdml_file_list

# regex to extract relevant values from xrdml files
reg_start_angle = "<startPosition>(.*)</startPosition>"
reg_end_angle = "<endPosition>(.*?)</endPosition>"
reg_counts = "<counts unit=\"counts\">(.*?)</counts>"

# Map all files to their data
for folder in xrdml_folder_file_dict:
  file_data_dict = {}
  for file in xrdml_folder_file_dict[folder]:
    with open(folder + "/" + file + file_ending, 'r') as xrdml_file:
        # Read file data
        file_text = xrdml_file.read()
        # Extract relevant values
        counts = re.findall(reg_counts, file_text)
        start_angle_list = re.findall(reg_start_angle, file_text)
        end_angle_list = re.findall(reg_end_angle, file_text)
        count_list = [float(count) for count in counts[0].split(' ')]
        start_angle = float(start_angle_list[0])
        end_angle = float(end_angle_list[0])
        angle_list = np.linspace(start=start_angle, stop=end_angle, num=len(count_list))
        # Put data in dictionary
        file_data_dict[file] = (angle_list, count_list)
  xrdml_folder_file_dict[folder] = file_data_dict

# Sort folders in desired order
name_start = 'SD'
doping_start= 'Nd'
doping_reg = '{}[0-9]+'.format(doping_start)
name_reg = '{}[0-9]+'.format(name_start)
sorting_reg = name_reg

def folder_sort(sorting_reg):
    return lambda folder_name: re.findall(sorting_reg, folder_name)

sorted_folder_dict = sorted(xrdml_folder_file_dict, key=folder_sort(sorting_reg), reverse=False)

# Create comparison figures
total_fig, total_ax = plt.subplots(figsize=(12, 8))
total_fig_title = 'XRD Comparison'
total_ax.set_yscale('log')
total_ax.set_xscale('linear')
total_ax.set_xlabel('Angle (${}^\circ$)')
total_ax.set_ylabel('Intensity (counts/second)')
total_ax.set_title(total_fig_title)
total_ax.grid(alpha=0.25)
for peak in interesting_peaks:
  total_ax.axvline(interesting_peaks[peak], 0, 1, label=None, ls='--', lw='0.5')
total_offset = 0.1

# Plot the data from each file in sorted order
for folder in sorted_folder_dict:
  total_offset *= 100
  for file in xrdml_folder_file_dict[folder]:
    angle_values = np.asarray(xrdml_folder_file_dict[folder][file][0])
    intensity_values = np.asarray(xrdml_folder_file_dict[folder][file][1])
    # doping = int(re.findall(doping_reg, folder)[0][-2:])
    doping = re.findall(doping_reg, folder)
    plot_label = '{}: {}%'.format(folder[:5], int(doping[0][-2:])) if doping else folder[:5]

    fig, ax = plt.subplots()
    ax.plot(angle_values, intensity_values, label=plot_label)

    # Only plot vertical lines and comparison for xrd files
    if 'tth' in file:
      total_ax.plot(angle_values, intensity_values * total_offset, lw='0.7', label=plot_label)
      for peak in interesting_peaks:
        ax.axvline(interesting_peaks[peak], 0, 1, label=peak, ls='--', lw='0.5')

    # TODO: Create comparison for XRR files

    ax.set_title(file)
    ax.set_yscale("log")
    ax.set_xscale("linear")
    ax.set_xlabel('Angle (${}^\circ$)')
    ax.set_ylabel('Intensity (counts/second)')
    ax.legend(framealpha=1, shadow=True)
    ax.grid(alpha=0.25)
    # Save .png of plot to folder with file
    fig.savefig("{}/{}.png".format(folder, file))
    # fig.show()
    # plt.pause(0.001)

# Label both by sample ID and by doping
handles, labels = total_ax.get_legend_handles_labels()
total_ax.legend(handles[::-1], labels[::-1], title=None, loc='best')
total_fig.savefig('{}_{}.png'.format(total_fig_title, doping_start if sorting_reg == doping_reg else name_start))
total_fig.show()

input("hit[enter] to close all plots")
plt.close('all')