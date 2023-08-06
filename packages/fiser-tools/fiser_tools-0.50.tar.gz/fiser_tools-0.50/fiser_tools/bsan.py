#!/usr/bin/env python
from matplotlib import rcParams
import matplotlib.pyplot as plt
from cycler import cycler
import seaborn as sns
import numpy as np
from matplotlib.ticker import FuncFormatter
import pandas as pd
import matplotlib.lines as lines

def pareto_graph(variable, salida='tabla'):
    #Ordenar en descendente y pasar a dataframe
    pareto = variable.sort_values(ascending=False).to_frame()
    #Cambiar el nombre a la variable
    pareto.columns = ['Valor']
    #Crear la posición
    pareto['Posicion'] = np.arange(start=1, stop=len(pareto) + 1)
    pareto['Posicion_Porc'] = pareto.Posicion.transform(
        lambda x: x / pareto.shape[0] * 100)
    #Crear el acumulado
    pareto['Acum'] = pareto['Valor'].cumsum()
    max_pareto_acum = max(pareto.Acum)
    pareto['Acum_Porc'] = pareto.Acum.transform(
        lambda x: x / max_pareto_acum * 100)
    #Simplificar
    pareto = pareto[['Posicion_Porc', 'Acum_Porc']]

    value = 80
    idx = (pareto["Acum_Porc"] - value).abs().idxmin()
    idx2 = pareto["Acum_Porc"].idxmin()
    nearest = pareto["Posicion_Porc"].loc[idx]
    ini = pareto["Posicion_Porc"].loc[idx2]

    #Devolver la salida
    if salida == 'grafico':
        f, ax = plt.subplots(figsize=(10, 5))
        ax.plot(pareto.Posicion_Porc, pareto.Acum_Porc)
        ax.plot(pareto.Posicion_Porc, pareto.Posicion_Porc)
        ax.tick_params(axis='x', labelsize=12, labelrotation=90)
        ax.set_xticks(pareto.Posicion_Porc, pareto.index, rotation='vertical')
        ax.axvline(nearest, color='green', alpha=0.3)
        ax.text(nearest + 2, 0, "%.1f %%" % (nearest))
        ax.axhline(80, color='green', alpha=0.3, linestyle='dotted')
        ax.set_title("Pareto graph for '%s' by '%s'" %
                     (variable.name, variable.index.name))
        ax.fill_between([ini, nearest, nearest, ini], [0, 0, 100, 100],
                        alpha=0.3,
                        color='green')
        return (ax)
    else:
        return (pareto)

def fis_bs_pareto_graph(variable, salida='tabla'):
    #Ordenar en descendente y pasar a dataframe
    pareto = variable.sort_values(ascending=False).to_frame()
    #Cambiar el nombre a la variable
    pareto.columns = ['Valor']
    #Crear la posición
    pareto['Posicion'] = np.arange(start=1, stop=len(pareto) + 1)
    pareto['Posicion_Porc'] = pareto.Posicion.transform(
        lambda x: x / pareto.shape[0] * 100)
    #Crear el acumulado
    pareto['Acum'] = pareto['Valor'].cumsum()
    max_pareto_acum = max(pareto.Acum)
    pareto['Acum_Porc'] = pareto.Acum.transform(
        lambda x: x / max_pareto_acum * 100)
    #Simplificar
    pareto = pareto[['Posicion_Porc', 'Acum_Porc']]

    value = 80
    idx = (pareto["Acum_Porc"] - value).abs().idxmin()
    idx2 = pareto["Acum_Porc"].idxmin()
    nearest = pareto["Posicion_Porc"].loc[idx]
    ini = pareto["Posicion_Porc"].loc[idx2]

    #Devolver la salida
    if salida == 'grafico':
        f, ax = plt.subplots(figsize=(10, 5))
        ax.plot(pareto.Posicion_Porc, pareto.Acum_Porc)
        ax.plot(pareto.Posicion_Porc, pareto.Posicion_Porc)
        ax.tick_params(axis='x', labelsize=12, labelrotation=90)
        ax.set_xticks(pareto.Posicion_Porc, pareto.index, rotation='vertical')
        ax.axvline(nearest, color='green', alpha=0.3)
        ax.text(nearest + 2, 0, "%.1f %%" % (nearest))
        ax.axhline(80, color='green', alpha=0.3, linestyle='dotted')
        ax.set_title("Pareto graph for '%s' by '%s'" %
                     (variable.name, variable.index.name))
        ax.fill_between([ini, nearest, nearest, ini], [0, 0, 100, 100],
                        alpha=0.3,
                        color='green')
        return (ax)
    else:
        return (pareto)

def fis_tool_clean_df_columns(df):
    for col in df.columns:
        new_col = col.lower()
        new_col = new_col.replace(" ", "_")
        new_col = new_col.replace("ó", "o")
        new_col = new_col.replace("í", "i").replace("á", "a").replace("é", "e")
        new_col = new_col.replace("ü", "u")
        new_col = new_col.replace("(", "")
        new_col = new_col.replace(")", "")
        new_col = new_col.replace("-", "")
        new_col = new_col.replace('º', "").replace("__", "_")
        new_col = new_col.replace("ñ", "n").replace("ú", "u").replace("í", "i")
        df.rename({col: new_col}, axis=1, inplace=True)
    return df

def fis_bs_histogram(df,value,labelx=None,labely=None,figsize=(12,4),dpi=400):
    f = plt.figure(figsize=figsize,dpi=dpi)
    ax = sns.histplot(df,x=value,shrink=0.8)
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
    return f, ax

def fis_bs_histmax(df,value,labelx=None,labely=None,
                   max_color="#364D6E",other_color="#D6D7D9",
                   figsize=(12,4),dpi=400):

    series = df[value].value_counts(sort=False)
    max_val = df[value].value_counts(sort=False).max()
    pal = []

    for item in series:
        if item == max_val:
            pal.append(max_color)
        else:
            pal.append(other_color)

    f = plt.figure(figsize=figsize,dpi=dpi)
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
    return f, ax

def fis_bs_waterfall(df,valor,group=False,group_value="",
                     Title="", x_lab="", y_lab="",
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
                     figsize = (10,10),
                     dpi = 400):
    if group == True:
        df = df.groupby(group_value)[valor].sum().reset_index().set_index(group_value)
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
    
    fig, ax = plt.subplots(figsize=figsize,dpi=dpi)
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

def fis_bs_lollipop(df,valor1,valor2,figsize=(12,4),dpi=100,linewidth=5,size=10,textsize=12,offset=9,color='grey'):
    f, ax = plt.subplots(figsize=figsize,dpi=dpi)
    markers,stems,base = plt.stem(df[valor1],df[valor2])
    plt.setp(stems, 'linewidth', linewidth)
    markers.set_markersize(size)
    markers.set_color(color)
    xlocs, xlabs = plt.xticks()
    j = 0
    for v in df[valor2]:
        plt.text(xlocs[j], v+offset, int(v), ha='center', fontsize=textsize)
        j+=1
    plt.ylabel("")
    plt.yticks([])                                    
    return f, ax

def fis_bs_mekko(ynp_values,xnp_values,x_labels,figsize=(12,5),color1='light blue',color2='grey',xticks_size=14,legend1='val1',legend2='val2',title_size=20,legend_size=20,label_y="",label_x=""):
    # calculate x coordinates based on the width of the previous bars
    # same as: [0, width[0], width[0] + width[1], width[0] + width[1] + width[2]]
    width = [i/sum(x) for i in x]
    fig, ax = plt.subplots(figsize=figsize)
    mpl.rcParams['axes.titley'] = 1.25
    adjusted_x, temp = [0], 0
    for i in width[:-1]:
        temp += i
        adjusted_x.append(temp)
    # Marimekko chart
    plt.bar(adjusted_x, y, width=width, align='edge', edgecolor='black',color=color1)
    plt.bar(adjusted_x, np.ones(len(y))-y, bottom=y, width=width, align='edge', edgecolor='black',color=color2)
    # x and y ticks (%)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
    plt.ylim(0,1)
    plt.xlim(0,1)
    # twin y-axis to draw x-ticks at the top
    axy = ax.twiny()
    axy.set_xticks([(width[i]/2)+ v for i, v in enumerate(adjusted_x)])
    axy.set_xticklabels(x_label, fontsize=xticks_size)
    ax.set_ylabel(label_y)
    ax.set_xlabel(labex_x)
    plt.title(title,
              loc='left', fontsize=title_size)
    ax.legend([legend1,legend2], 
               ncol=2, loc='upper left', fontsize=legend_size,
                   frameon=False, bbox_to_anchor=(0,1.25))
    return f, ax
