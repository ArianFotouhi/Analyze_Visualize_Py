import datetime
import os
import matplotlib.pyplot as plt
import io
import base64

import matplotlib
matplotlib.use('Agg')

class Plotter:
    def __init__(self, x, y, title, xlabel='', ylabel=''):
        self.x = x
        self.y = y
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
    
    def generate_plot(self):
        fig, ax = plt.subplots()  # Create a new Figure and Axes object
        ax.plot(self.x, self.y)
        ax.set_title(self.title, fontfamily='serif', fontsize=12)
        ax.set_xlabel(self.xlabel, fontfamily='serif', fontsize=8)
        ax.set_ylabel(self.ylabel, fontfamily='serif', fontsize=10)
        return fig
    
    def format_date(self, date_str):
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date.strftime("%y-%m-%d")  # Format the date as yy-mm-dd
    
    def save_plot(self, filename):
        filepath = os.path.join('static', 'image', filename+'.png')  # Use forward slashes in the file path
        print('filepath:', filepath) 
        
        fig = self.generate_plot()  # Generate the plot
        
        # Format the x-axis labels as dates without time
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
