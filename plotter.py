from config import num_samples_gradient
import datetime
import matplotlib.pyplot as plt
import base64
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.ticker as ticker
import io
from utils import logo_render
from PIL import Image


class Plotter:
    def __init__(self, x, y, title, background_color=None, growth_rate=0, plt_thickness=2.0, xlabel='', ylabel='', no_data_error='', client='', plot_gradient_intensity=0.5):
        self.x = x
        self.y = y
        self.title = title
        self.growth_rate = growth_rate
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.no_data_error = no_data_error
        self.client = client
        self.plot_gradient_intensity= plot_gradient_intensity
        self.plt_thickness = plt_thickness
        self.background_color = background_color
    
    
    def generate_plot(self):
        fig, ax = plt.subplots()  # Create a new Figure and Axes object

        if self.background_color:
            background_color = self.background_color
            fig.patch.set_facecolor(background_color)

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
        green = 47/255
        blue = 111/255
        self.plot_gradient_intensity

        ######################################## complex color plots################################
        import time

      
        for i in range(len(color_samples)):
            if i != (len(color_samples) - 1):

                if color_samples[dict_keys[i]] !=0:
                    c_gradient = (color_samples[dict_keys[i+1]] - color_samples[dict_keys[i]]) / (color_samples[dict_keys[i]])*2.5
                else:
                    c_gradient=0.3
                
                red -= c_gradient*self.plot_gradient_intensity
                blue += c_gradient*self.plot_gradient_intensity

                if red < 0:
                    red = 0
                elif red > 1.0:
                    red = 1.0

                if blue < 0:
                    blue = 0
                elif blue > 1.0:
                    blue = 1.0

                ax.plot(
                    self.x[dict_keys[i]: dict_keys[i + 1] + 1],
                    self.y[dict_keys[i]: dict_keys[i + 1] + 1],
                    color=[red, green, blue],
                    linewidth= self.plt_thickness 

                )

            else:
                ax.plot(self.x[dict_keys[i]:], self.y[dict_keys[i]:], color=[red, green, blue])



        ax.set_title(self.title, fontfamily='Roboto', fontsize=16, fontweight='bold',color='#002F6F',)
        ax.set_xlabel(self.xlabel, fontfamily='Roboto', fontsize=7, fontweight='bold')
        ax.set_ylabel(self.ylabel, fontfamily='Roboto', fontsize=10, fontweight='bold')

        num_xlabels = min(len(self.x), 3)  # Get the minimum between the number of x-labels and 5
        x_indices = np.linspace(0, len(self.x) - 1, num_xlabels, dtype=int)  # Generate evenly spaced indices
        x_labels = [self.format_date(self.x[i]) for i in x_indices]  # Get the corresponding formatted x-labels
     
        ax.set_xticks(x_indices)  # Set the x-axis tick locations
        ax.set_xticklabels(x_labels, fontsize=11)  # Set the x-axis tick labels
        
        # Format y-axis tick labels as integers
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:.0f}'.format(y)))
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y')


        if self.no_data_error:
            ax.text(0.5, 0.2, self.no_data_error, horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, color='red', fontsize=10, fontweight='bold',
                    bbox={'facecolor': 'white', 'edgecolor': 'black', 'linewidth': 1,'alpha': 0.5})

         
        
        growth_percentage = self.growth_rate
        if growth_percentage is not None:
            text = f"Change: {int(growth_percentage)}%"
            color = 'green' if growth_percentage > 0 else 'red'
            marker = '▲' if growth_percentage > 0 else '▼'
            ax.text(0.95, 0.05, marker+' '+text, horizontalalignment='right', verticalalignment='bottom',
                    transform=ax.transAxes, color=color, fontsize=10, fontweight='bold',
                    bbox={'facecolor': 'white', 'edgecolor': 'black', 'linewidth': 1,'alpha': 0.5})
        
        
        if self.client:
            logo = logo_render(self.client)
            if logo:
                self.attach_logo(fig, logo)  # Attach the logo to the plot

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
    
    def attach_logo(self, fig, logo):
        # Resize the logo to fit in the plot
        logo_width = fig.bbox.width * 0.15
        logo_height = logo_width * logo.size[1] / logo.size[0]
        logo = logo.resize((int(logo_width), int(logo_height)), Image.ANTIALIAS)
        
        # Calculate the position to place the logo
        logo_x = 10
        logo_y = fig.bbox.height - logo_height - 10
        
        # Overlay the lofgo on the plot
        fig.figimage(logo, xo=logo_x, yo=logo_y, alpha=0.85)
