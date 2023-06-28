import datetime
import os
import matplotlib.pyplot as plt
import io
import base64

import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.cm as cm
from matplotlib.collections import LineCollection

class Plotter:
    def __init__(self, x, y, title, xlabel='', ylabel='', no_data_error=''):
        self.x = x
        self.y = y
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.no_data_error = no_data_error
    
    def generate_plot(self):
        fig, ax = plt.subplots()  # Create a new Figure and Axes object
        ax.plot(self.x, self.y, color='green')
        
        ax.set_title(self.title, fontfamily='serif', fontsize=12, fontweight='bold')  # Make the title bold
        ax.set_xlabel(self.xlabel, fontfamily='serif', fontsize=8, fontweight='bold')  # Make the xlabel bold
        ax.set_ylabel(self.ylabel, fontfamily='serif', fontsize=10, fontweight='bold')  # Make the ylabel bold

        ax.set_xticklabels(ax.get_xticks(), fontweight='bold', fontsize=7)  # Make xticklabels bold
        ax.set_yticklabels(ax.get_yticks(), fontweight='bold', fontsize=7)  # Make yticklabels bold

        if self.no_data_error:
            ax.text(0.5, 0.2, self.no_data_error, horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, color='red', fontsize=12, fontweight='bold')

        return fig
    
    def format_date(self, date_str):
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date.strftime("%y-%m-%d")  # Format the date as yy-mm-dd
    
    def save_plot(self, filename):
        filepath = os.path.join('static', 'image', filename+'.png')  # Use forward slashes in the file path
        print('filepath:', filepath) 
        
        fig = self.generate_plot()  # Generate the plot

        # Format the x-axis labels as dates without time if no_date is False
        x_labels = [self.format_date(date) for date in self.x]
        fig.axes[0].set_xticklabels(x_labels, rotation='vertical', fontsize=7)  # Adjust rotation and fontsize
        
        fig.savefig(filepath, format='png')
        plt.close(fig)

        with open(filepath, 'rb') as image_file:
            # Read the saved image file
            image_data = image_file.read()

        # Convert the image to a base64-encoded string
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Create the JSON response
        return image_base64
