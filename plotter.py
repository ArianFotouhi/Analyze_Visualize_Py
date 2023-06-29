from config import plot_gradient_intensity, num_samples_gradient
import datetime
import os
import matplotlib.pyplot as plt
import base64
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.ticker as ticker
import io

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

        y_length = len(self.y)
        color_samples = {}
        num_samples = num_samples_gradient

        if y_length <= num_samples:
            for i, rate in enumerate(self.y):
                color_samples[i] = rate
        else:
            stride = y_length // num_samples
            index = 0
            for i in range(num_samples):
                selected_index = stride * i + index
                color_samples[selected_index] = self.y[selected_index]

        dict_keys = sorted(color_samples.keys())

        red = 0.0
        green = 187/255
        blue = 0.0
        #blue = 120/255
        for i in range(len(color_samples)):
            if i != (len(color_samples) - 1):
                c_gradient = (color_samples[dict_keys[i+1]] - color_samples[dict_keys[i]]) / (color_samples[dict_keys[i]])
                red -= c_gradient*plot_gradient_intensity
                green += c_gradient*plot_gradient_intensity

                if red <0:
                    red = 0
                elif red > 1.0:
                    red = 1.0

                if green < 0:
                    green = 0
                elif green > 1.0:
                    green = 1.0

                ax.plot(
                    self.x[dict_keys[i]: dict_keys[i + 1] + 1],
                    self.y[dict_keys[i]: dict_keys[i + 1] + 1],
                    color=[red, green, blue]
                )

            else:
                ax.plot(self.x[dict_keys[i]:], self.y[dict_keys[i]:], color=[red, green, blue])
        
        ax.set_title(self.title, fontfamily='Roboto', fontsize=16, fontweight='bold')
        ax.set_xlabel(self.xlabel, fontfamily='Roboto', fontsize=7, fontweight='bold')
        ax.set_ylabel(self.ylabel, fontfamily='Roboto', fontsize=10, fontweight='bold')

        num_xlabels = min(len(self.x), 3)  # Get the minimum between the number of x-labels and 5
        x_indices = np.linspace(0, len(self.x) - 1, num_xlabels, dtype=int)  # Generate evenly spaced indices
        x_labels = [self.format_date(self.x[i]) for i in x_indices]  # Get the corresponding formatted x-labels
     
        ax.set_xticks(x_indices)  # Set the x-axis tick locations
        ax.set_xticklabels(x_labels, fontsize=11)  # Set the x-axis tick labels
        
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
    
    def save_plot(self):
        fig = self.generate_plot()  # Generate the plot

        # Save the plot to a BytesIO object
        image_stream = io.BytesIO()
        fig.savefig(image_stream, format='png')
        plt.close(fig)

        # Retrieve the image data from the BytesIO object
        image_stream.seek(0)
        image_data = image_stream.getvalue()

        # Convert the image to a base64-encoded string
        image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Create the JSON response
        return image_base64
