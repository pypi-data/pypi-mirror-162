from matplotlib import rcParams
import matplotlib.pyplot as plt
from cycler import cycler
import seaborn as sns
import numpy as np
from matplotlib.ticker import FuncFormatter
import pandas as pd
import matplotlib.lines as lines


def fis_dark_theme():
    darked = '#303030'
    light_white = '#FFFEF1'
    sns.set(rc={
        'axes.facecolor':'#303030', 
        'figure.facecolor':'#303030',
        'text.color':light_white,
        'axes.labelcolor':light_white,
        'xtick.color':light_white,
        'ytick.color':light_white,
    })

    sns.set(rc={'axes.facecolor':darked, 'figure.facecolor':darked})

    dark_theme_colors = ["#e60049", "#0bb4ff", "#50e991", "#e6d800", "#9b19f5", "#ffa300", "#dc0ab4", "#b3d4ff", "#00bfa0"]
    dark_theme_colors + ["#2f6997","#936bb6","#c765ae","#f26195","#ff6a71","#ff8445","#ffa600"]
    dark_theme_colors + ["#b30000", "#7c1158", "#4421af", "#1a53ff", "#0d88e6", "#00b7c7", "#5ad45a", "#8be04e", "#ebdc78"]
    dark_theme_colors + ["#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a", "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"]
    dark_theme_colors + ["#ea5545", "#f46a9b", "#ef9b20", "#edbf33", "#ede15b", "#bdcf32", "#87bc45", "#27aeef", "#b33dc6"]
    rcParams['figure.figsize'] = 9,4
    rcParams['figure.facecolor'] = '#303030'
    rcParams['axes.facecolor'] = '#303030'
    rcParams['figure.facecolor'] = '#303030'
    rcParams['axes.edgecolor'] = light_white
    rcParams['text.color'] = light_white
    rcParams['axes.labelcolor'] = light_white
    rcParams['xtick.color'] = light_white
    rcParams['ytick.color'] = light_white
    rcParams['axes.grid'] = True
    rcParams['grid.color'] = light_white
    rcParams['grid.alpha'] = .1
    rcParams['axes.prop_cycle'] = cycler(color=dark_theme_colors)
    rcParams['image.cmap'] = 'inferno'

def fis_light_theme():
    dark_blue = "#152238"
    sns.set(rc={
        'text.color':dark_blue,
        'axes.labelcolor':dark_blue,
        'xtick.color':dark_blue,
        'ytick.color':dark_blue,
    })

    light_white = '#FFFEF1'
    dark_theme_colors = ["#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a", "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"]
    dark_theme_colors + ["#e60049", "#0bb4ff", "#50e991", "#e6d800", "#9b19f5", "#ffa300", "#dc0ab4", "#b3d4ff", "#00bfa0"]
    dark_theme_colors + ["#2f6997","#936bb6","#c765ae","#f26195","#ff6a71","#ff8445","#ffa600"]
    dark_theme_colors + ["#b30000", "#7c1158", "#4421af", "#1a53ff", "#0d88e6", "#00b7c7", "#5ad45a", "#8be04e", "#ebdc78"]
    dark_theme_colors + ["#ea5545", "#f46a9b", "#ef9b20", "#edbf33", "#ede15b", "#bdcf32", "#87bc45", "#27aeef", "#b33dc6"]
    rcParams['figure.figsize'] = 9,4
    rcParams['axes.edgecolor'] = dark_blue 
    rcParams['axes.grid'] = True
    rcParams['grid.alpha'] = .5
    rcParams['axes.prop_cycle'] = cycler(color=dark_theme_colors)
    rcParams['grid.color'] = light_white
    rcParams['image.cmap'] = 'inferno'

def fis_business_theme():
    dark_blue =  "#152238"
    cadet_blue = "#364D6E"
    white =      "#FFFFFF"
    light_blue = "#DAE3F3"
    silver =     "#D6D7D9"
    business_colors = ["#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9",
                       "#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9",
                       "#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9",
                      ]
    sns.set(rc={
        'text.color':dark_blue,
        'axes.labelcolor':dark_blue,
        'xtick.color':dark_blue,
        'ytick.color':dark_blue,
        'axes.spines.left':False,
        'ytick.left': False,
    })

    sns.set_palette(business_colors)

    rcParams['figure.figsize'] = 14,8
    rcParams['axes.edgecolor'] = dark_blue
    rcParams['axes.facecolor'] = white
    rcParams['axes.grid'] = False
    rcParams['axes.spines.top'] = False
    rcParams['axes.spines.right'] = False
    rcParams['axes.spines.left'] = False
    rcParams['ytick.labelleft'] = True
    rcParams['date.autoformatter.month'] = '%m/%Y'
    rcParams['grid.alpha'] = .5
    rcParams['axes.prop_cycle'] = cycler(color=business_colors)
    rcParams['grid.color'] = white
    rcParams['image.cmap'] = 'Greys'

def fis_bs_histogram(df,value,labelx=None,labely=None):
    sns.histplot(df,x=value,shrink=0.8)
    xlocs, xlabs = plt.xticks()
    j = 0
    for i,v in zip(df[value].value_counts(sort=False).index,df[value].value_counts(sort=False)):
        plt.text(xlocs[j], v+2, int(v), ha='center', fontsize=12)
        j+=1

    if labelx is not None:
        plt.xlabel(labelx, c="#364D6E", fontsize=14)
    if labely is not None:
        plt.ylabel(labely, c="#364D6E", fontsize=14)
    # remove y ticks
    plt.yticks([])
    plt.show()

def fis_bs_histmax(df,value,labelx=None,labely=None,
                   max_color="#364D6E",other_color="#D6D7D9"):

    series = df[value].value_counts(sort=False)
    max_val = df[value].value_counts(sort=False).max()
    pal = []

    for item in series:
        if item == max_val:
            pal.append(max_color)
        else:
            pal.append(other_color)

    plt.figure(figsize=(12,9))
    ax = sns.barplot(x = df[value].value_counts(sort=False).index,
                     y = df[value].value_counts(sort=False),
                palette=pal)

    xlocs, xlabs = plt.xticks()
    j = 0
    for i,v in zip(df[value].value_counts(sort=False).index,
                   df[value].value_counts(sort=False)):
        plt.text(xlocs[j], v+2, int(v), ha='center', fontsize=12)
        j+=1

    if labelx is not None:
        plt.xlabel(labelx, c="#364D6E", fontsize=14)
    if labely is not None:
        plt.ylabel(labely, c="#364D6E", fontsize=14)
    # remove y ticks
    plt.yticks([])
    plt.show()

def fis_bs_waterfall(df,valor, Title="", x_lab="", y_lab="",
                     formatting = "{:,.1f}", 
                     green_color="#D6D7D9", 
                     red_color="#D6D7D9", 
                     blue_color="#364D6E",
                     sorted_value = False, 
                     threshold=None, 
                     other_label='other', 
                     net_label='net', 
                     rotation_value = 30, 
                     blank_color=(0,0,0,0), 
                     figsize = (10,10)):
    index = df.index
    data = df[valor].values
    '''
    Given two sequences ordered appropriately, generate a standard waterfall chart.
    Optionally modify the title, axis labels, number formatting, bar colors, 
    increment sorting, and thresholding. Thresholding groups lower magnitude changes
    into a combined group to display as a single entity on the chart.
    '''
    
    #convert data and index to np.array
    index=np.array(index)
    data=np.array(data)
    
    # wip
    #sorted by absolute value 
    if sorted_value: 
        abs_data = abs(data)
        data_order = np.argsort(abs_data)[::-1]
        data = data[data_order]
        index = index[data_order]
    
    #group contributors less than the threshold into 'other' 
    if threshold:
        
        abs_data = abs(data)
        threshold_v = abs_data.max()*threshold
        
        if threshold_v > abs_data.min():
            index = np.append(index[abs_data>=threshold_v],other_label)
            data = np.append(data[abs_data>=threshold_v],sum(data[abs_data<threshold_v]))
    
    changes = {'amount' : data}
    
    #define format formatter
    def money(x, pos):
        'The two args are the value and tick position'
        return formatting.format(x)
    formatter = FuncFormatter(money)
    
    fig, ax = plt.subplots(figsize=figsize)
    ax.yaxis.set_major_formatter(formatter)

    #Store data and create a blank series to use for the waterfall
    trans = pd.DataFrame(data=changes,index=index)
    blank = trans.amount.cumsum().shift(1).fillna(0)
    
    trans['positive'] = trans['amount'] > 0

    #Get the net total number for the final element in the waterfall
    total = trans.sum().amount
    trans.loc[net_label]= total
    blank.loc[net_label] = total

    #The steps graphically show the levels as well as used for label placement
    step = blank.reset_index(drop=True).repeat(3).shift(-1)
    step[1::3] = np.nan

    #When plotting the last element, we want to show the full bar,
    #Set the blank to 0
    blank.loc[net_label] = 0
    
    #define bar colors for net bar
    trans.loc[trans['positive'] > 1, 'positive'] = 99
    trans.loc[trans['positive'] < 0, 'positive'] = 99
    trans.loc[(trans['positive'] > 0) & (trans['positive'] < 1), 'positive'] = 99
    
    trans['color'] = trans['positive']
    
    trans.loc[trans['positive'] == 1, 'color'] = green_color
    trans.loc[trans['positive'] == 0, 'color'] = red_color
    trans.loc[trans['positive'] == 99, 'color'] = blue_color
    
    my_colors = list(trans.color)
    
    #Plot and label
    my_plot = plt.bar(range(0,len(trans.index)), blank, width=0.5, color=blank_color)
    plt.bar(range(0,len(trans.index)), trans.amount, width=0.6,
             bottom=blank, color=my_colors)       
                                   
    
    plt.plot(step.index, step.values,alpha=0.4,ls=':')
    
    #axis labels
    plt.xlabel("\n" + x_lab)
    plt.ylabel(y_lab + "\n")

    #Get the y-axis position for the labels
    y_height = trans.amount.cumsum().shift(1).fillna(0)
    
    temp = list(trans.amount)
    
    # create dynamic chart range
    for i in range(len(temp)):
        if (i > 0) & (i < (len(temp) - 1)):
            temp[i] = temp[i] + temp[i-1]
    
    trans['temp'] = temp
            
    plot_max = trans['temp'].max()
    plot_min = trans['temp'].min()
    
    #Make sure the plot doesn't accidentally focus only on the changes in the data
    if all(i >= 0 for i in temp):
        plot_min = 0
    if all(i < 0 for i in temp):
        plot_max = 0
    
    if abs(plot_max) >= abs(plot_min):
        maxmax = abs(plot_max)   
    else:
        maxmax = abs(plot_min)
        
    pos_offset = maxmax / 150
    
    plot_offset = maxmax / 30 ## needs to me cumulative sum dynamic

    #Start label loop
    loop = 0
    for index, row in trans.iterrows():
        # For the last item in the list, we don't want to double count
        if row['amount'] == total:
            y = y_height[loop]
        else:
            y = y_height[loop] + row['amount']
        # Determine if we want a neg or pos offset
        if row['amount'] > 0:
            y += (pos_offset*2)
            plt.annotate(formatting.format(row['amount']),(loop,y),ha="center", fontsize=9)
        else:
            y -= (pos_offset*4)
            plt.annotate(formatting.format(row['amount']),(loop,y),ha="center", fontsize=9)
        loop+=1

    #Scale up the y axis so there is room for the labels
    plt.ylim(plot_min-round(3.6*plot_offset, 7),plot_max+round(3.6*plot_offset, 7))
    
    #Rotate the labels
    plt.xticks(range(0,len(trans)), trans.index, rotation=rotation_value)
    
    #add zero line and title
    plt.axhline(0, color='black', linewidth = 0.6, linestyle="dashed")
    # remove y ticks
    plt.yticks([])
    plt.title(Title)
    plt.tight_layout()

    return fig, ax
