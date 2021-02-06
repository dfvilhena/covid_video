import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import matplotlib.dates as mdates
import datetime as dt
from data_handling import data_handling
from copy import deepcopy
import os
#from cv2 import cv2
#import ffmpeg
from shutil import copyfile
from PIL import Image


png_folder = "./frames/"

final_gif = "covid_variation.gif"

background_color = "#0c0c19"
line_color = "xkcd:bright turquoise" # #0ffef9
text_color = "xkcd:off white"

### Graphic settings

dpi = 100
side_inches = 11

fig = plt.figure(dpi=dpi)
fig.set_size_inches(11, 11, True)

fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=None, hspace=None)

ax = plt.gca()
ax.set_facecolor(background_color)
ax.tick_params(direction="in")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%y"))

ax.yaxis.get_major_ticks()[1].label1.set_visible(False)

ax.tick_params(axis="x",direction="out", pad=-55, labelsize=15, length=20, color=text_color, 
    labelcolor=text_color, labelrotation=90, bottom=False, top=False, 
    labelbottom=False, labeltop=False)

ax.tick_params(axis="y",direction="in", pad=-65, labelsize=15, length=20, color=text_color, 
    left=False, labelcolor=text_color)    

plt.rc('font', size=20)

text = ax.text(dt.date(2020, 3, 2), 1, "", ha='left', va='top')

fps = 8
seconds_pause = 1.5

### Preparing visualization

number_of_markers = 0
frame_counter = 0
marker_id = []

wvar_df = data_handling()

### Function that builds the plot

def buildmebarchart(i=int):
    global frame_counter
    if i > 1:   
        p = plt.plot(wvar_df[:i].Data, wvar_df[:i].Var_I_New, alpha=0.1, linewidth=7.0)

        marker_df = wvar_df[:i][wvar_df["Marker"]==1]
        q = plt.scatter(marker_df.Data, marker_df.Var_I_New, s=1024, marker=2, color=line_color, alpha=1)

        max_y = wvar_df[:i].Var_I_New.max()
        latest_date = wvar_df[:i].Data.max()
        total_cases = wvar_df[:i].confirmados.max()

        text.set_x(dt.date(2020, 3, 2))    
        text.set_y(max_y)
        text.set_text("          Data: %s\n          Casos totais: %.0f" % (latest_date.strftime("%d-%m-%Y"), total_cases))
        text.set_c(text_color)
        p[0].set_color(line_color)

        global number_of_markers

        if len(marker_df["Data"]) > number_of_markers:
            meas_text = marker_df["Medida"].iloc[-1]
            text.set_text("          Data: %s\n          Casos totais: %.0f\n          %s" % (latest_date.strftime("%d-%m-%Y"), total_cases, meas_text))
            number_of_markers = deepcopy(len(marker_df["Data"]))
            marker_id.append(frame_counter)

        png_filename = png_folder+"frame_"+str(frame_counter).zfill(3)+".png"
        plt.savefig(png_filename)
        frame_counter += 1

number_of_frames = 200
animator = ani.FuncAnimation(fig, buildmebarchart, interval=(1/fps)*1000,blit=False, save_count=number_of_frames)
plt.show()

### Saving frames

frame_array = []

file_list = [f for f in os.listdir(png_folder) if f.endswith(".png")]

for f in file_list:
    f_id = int(f.split("_")[-1].split(".")[0])
    if f_id in marker_id:
        for i in range(0, int(fps*seconds_pause)-1):
            source_file = png_folder+f
            copy_name = png_folder+f.split(".")[0]+"_"+str(i).zfill(3)+".png"
            copyfile(source_file, copy_name)
  
file_list = [png_folder+f for f in os.listdir(png_folder)]

image_list = []
for f in file_list:
    image_list.append(Image.open(f))

gif = []

for image in image_list:
    gif.append(image.convert("P", palette=Image.ADAPTIVE))

gif[0].save(final_gif, save_all=True, optimize=False, append_images=gif[1:], loop=0, duration=(1/fps)*1000)

### Cleaning up

for f in os.listdir(png_folder):
    os.remove(png_folder+f)