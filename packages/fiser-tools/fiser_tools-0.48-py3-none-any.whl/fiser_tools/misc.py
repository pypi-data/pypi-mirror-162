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
    business_colors = ["#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9",
                    "#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9","#D6D7D9"]
    sns.set(rc={
        'text.color':dark_blue,
        'axes.labelcolor':dark_blue,
        'xtick.color':dark_blue,
        'ytick.color':dark_blue,
        'axes.spines.left':False,
        'ytick.left': False,
        'image.cmap': 'Greys',
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

def fis_get_colors(theme):
    if theme == 'light':
        dark_theme_colors = ["#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a", "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"]
        dark_theme_colors + ["#e60049", "#0bb4ff", "#50e991", "#e6d800", "#9b19f5", "#ffa300", "#dc0ab4", "#b3d4ff", "#00bfa0"]
        dark_theme_colors + ["#2f6997","#936bb6","#c765ae","#f26195","#ff6a71","#ff8445","#ffa600"]
        dark_theme_colors + ["#b30000", "#7c1158", "#4421af", "#1a53ff", "#0d88e6", "#00b7c7", "#5ad45a", "#8be04e", "#ebdc78"]
        dark_theme_colors + ["#ea5545", "#f46a9b", "#ef9b20", "#edbf33", "#ede15b", "#bdcf32", "#87bc45", "#27aeef", "#b33dc6"]
        return dark_theme_colors     
    elif theme == 'dark':
        dark_theme_colors = ["#e60049", "#0bb4ff", "#50e991", "#e6d800", "#9b19f5", "#ffa300", "#dc0ab4", "#b3d4ff", "#00bfa0"]
        dark_theme_colors + ["#2f6997","#936bb6","#c765ae","#f26195","#ff6a71","#ff8445","#ffa600"]
        dark_theme_colors + ["#b30000", "#7c1158", "#4421af", "#1a53ff", "#0d88e6", "#00b7c7", "#5ad45a", "#8be04e", "#ebdc78"]
        dark_theme_colors + ["#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a", "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"]
        dark_theme_colors + ["#ea5545", "#f46a9b", "#ef9b20", "#edbf33", "#ede15b", "#bdcf32", "#87bc45", "#27aeef", "#b33dc6"]
        return dark_theme_colors
    elif theme == 'business':
        business_colors = ["#D6D7D9","#97ACCF","#A7A8AA","#B6E1F6","#DAE3F3","#2f6997","#7A7B7D","#00b7c7","#505153","#8bd3c7","#3E4756","#0d88e6"]        
        return business_colors
    else:
        return None
