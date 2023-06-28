import datetime
import os
import matplotlib.pyplot as plt
import base64
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.ticker as ticker

class Plotter:
    def __init__(self, x, y, title, xlabel='', ylabel='', no_data_error=''):
        self.x = x
        self.y = y
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.no_data_error = no_data_error
    
    def calculate_growth_percentage(self):
        # Calculate the growth percentage of the last two points of y
        if len(self.y) >= 2:
            growth_percentage = ((self.y[-1] - self.y[-2]) / self.y[-2]) * 100
            return growth_percentage
        else:
            return None

    def generate_plot(self):
        fig, ax = plt.subplots()  # Create a new Figure and Axes object
        ax.plot(self.x, self.y, c='green')
        
        ax.set_title(self.title, fontfamily='serif', fontsize=12, fontweight='bold')
        ax.set_xlabel(self.xlabel, fontfamily='serif', fontsize=7, fontweight='bold')
        ax.set_ylabel(self.ylabel, fontfamily='serif', fontsize=10, fontweight='bold')

        num_xlabels = min(len(self.x), 5)  # Get the minimum between the number of x-labels and 5
        x_indices = np.linspace(0, len(self.x) - 1, num_xlabels, dtype=int)  # Generate evenly spaced indices
        x_labels = [self.format_date(self.x[i]) for i in x_indices]  # Get the corresponding formatted x-labels
     
        ax.set_xticks(x_indices)  # Set the x-axis tick locations
        ax.set_xticklabels(x_labels, rotation='vertical', fontsize=6)  # Set the x-axis tick labels
        
        # Format y-axis tick labels as integers
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:.0f}'.format(y)))

        if self.no_data_error:
            ax.text(0.5, 0.2, self.no_data_error, horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, color='red', fontsize=12, fontweight='bold')
        
        growth_percentage = self.calculate_growth_percentage()
        if growth_percentage is not None:
            text = f"Growth: {growth_percentage:.2f}%"
            color = 'green' if growth_percentage > 0 else 'red'
            marker = '▲' if growth_percentage > 0 else '▼'
            ax.text(0.95, 0.05, marker+' '+text, horizontalalignment='right', verticalalignment='bottom',
                    transform=ax.transAxes, color=color, fontsize=10, fontweight='bold')

        return fig
    
    def format_date(self, date_str):
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date.strftime("%y-%m-%d")  # Format the date as yy-mm-dd
    
    def save_plot(self, filename):
        filepath = os.path.join('static', 'image', filename+'.png')  # Use forward slashes in the file path
        
        fig = self.generate_plot()  # Generate the plot

        fig.savefig(filepath, format='png')
        plt.close(fig)

        with open(filepath, 'rb') as image_file:
            # Read the saved image file
            image_data = image_file.read()

        # Convert the image to a base64-encoded string
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Create the JSON response
        return image_base64
