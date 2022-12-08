# from here: https://github.com/bokeh/bokeh/tree/branch-3.0/examples/app/movies

import os
from os.path import dirname, join
import numpy as np
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, CustomJS, Toggle
from bokeh.plotting import figure

path = os.getcwd()
print(path)
#path = path.rsplit('/')[0]
movies = pd.read_csv(f"{path}/data/performers_with_coefficient.csv")
print(movies)

snl_cast_crew = pd.read_csv(f"{path}/data/snl_cast_crew.csv")
seasons_list = ["All","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","43","44","45","46","47","48","49","50","51","52"]
snl_alums_list = snl_cast_crew['person'].to_list()
snl_alums_list.sort()
snl_alums_list.append("All")
snl_alums_list.sort()
#snl_media = open(join(dirname(__file__), f"{path}/data/snl_associated_media.txt")).read().split()
movies["color"] = "grey"
#movies.loc[movies.imdb_link.isin(snl_media), "color"] = "purple"
movies["alpha"] = 1

axis_map = {
    "Person Coefficient": "coefficient",
    "Year (Start)": "year_start",
}

desc = Div(text=open(join(dirname(__file__), "description.html")).read(), sizing_mode="stretch_width")

# Create Input controls
min_coefficient = Slider(title="Minimum coefficient", value=0, start=0, end=1, step=.001)
season = Select(title="Season", value="All", options=seasons_list)
snl_alumni = Select(title="SNL Alum", value="All", options=snl_alums_list)
x_axis = Select(title="X Axis", options=["Year (Start)"], value="Year (Start)")
y_axis = Select(title="Y Axis", options=["Person Coefficient"], value="Person Coefficient")
roles = Select(title='Roles', value="All", options=["All","Writers","Performers"])
specifics = Select(title="Curated Lists", value="None",options=['None','Five-Timers Club','Head Writers','Weekend Update', 'Best Of Compilations', 'Alumni Hosts'])
lorne =  Select(title="Include Lorne?", options=["Yes","No"], value="No")
title_input = TextInput(value="", title="Search for a Person:")

source = ColumnDataSource(data=dict(x=[], y=[], color=[], title=[], year=[], alpha=[]))

TOOLTIPS=[
    ("Alum", "@person"),
    ("Year (Start)", "@year_start"),
    ("Year (End)", "@year_end"),
    ("Number of Seasons", "@num_seasons_total"),
    ("Coefficient", "@coefficient")
]

p = figure(height=600, width=700, title="", toolbar_location=None, tooltips=TOOLTIPS, sizing_mode="scale_both")
p.circle(x="x", y="y", source=source, size=7, color="color", line_color=None, fill_alpha="alpha")


def select_movies():
    snl_alumni_val = snl_alumni.value
    specifics_val = specifics.value
    title_input_val = title_input.value
    roles_val = roles.value
    season_val = season.value
    lorne_val = lorne.value
    selected = movies[(movies.coefficient >= min_coefficient.value)]
    if (lorne_val=="No"):
        selected = selected[selected.person.str.contains("Lorne Michaels")==False]
    if (snl_alumni_val != "All"):
        selected = selected[selected.person.str.contains(snl_alumni_val)==True]
    if (roles_val != "All"):
        if roles_val =="Writers":
            selected = selected[selected.num_seasons_writer>=1]
        else:
            selected = selected[selected.num_seasons_actor>=1]
    if (season_val != "All"):
        seasons_dict = {"1":1975,"2":1976,"3":1977,"4":1978,"5":1979,"6":1980,"7":1981,"8":1982,"9":1983,"10":1984,"11":1985,"12":1986,"13":1987,"14":1988,"15":1989,"16":1990,"17":1991,"18":1992,"19":1993,"20":1994,"21":1995,"22":1996,"23":1997,"24":1998,"25":1999,"26":2000,"27":2001,"28":2002,"29":2003,"30":2004,"31":2005,"32":2006,"33":2007,"34":2008,"35":2009,"36":2010,"37":2011,"38":2012,"39":2013,"40":2014,"41":2015,"42":2016,"43":2017,"44":2018,"45":2019,"46":2020,"47":2021,"48":2022,"49":2023,"50":2024,"51":2025,"52":2026}
        season_start = seasons_dict[season_val]
        season_end = seasons_dict[season_val] + 1
        selected = selected[selected['year_start']<=season_start]
        selected = selected[selected['year_end']>=season_end]
    if (specifics_val != "None"):
       if specifics_val == "Five-Timers Club":
           selected = selected[selected['num_episodes_hosted']>=5]
       elif specifics_val == 'Head Writers':
            selected = selected[selected['num_seasons_headwriter']>=1]
       elif specifics_val == 'Weekend Update':
            selected = selected[selected['num_seasons_weekend_update']>=1]
       elif specifics_val == 'Best of Compilations':
            selected = selected[selected['best_of']!=0]
       else:
           selected = selected[selected['num_episodes_hosted']>=1]
    if (title_input_val != ""):
        selected = selected[selected.title.str.contains(title_input_val)==True]
    return selected

def update():
    df = select_movies()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]
    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d alumnni selected" % len(df)
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
        person=df['person'],
        year_start=df["year_start"],
        year_end=df["year_end"],
        alpha=df["alpha"],
        coefficient=df["coefficient"],
        num_seasons_total=df['num_seasons_total'],
    )

controls = [season, roles, lorne, snl_alumni, min_coefficient, x_axis, y_axis, specifics, title_input]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

inputs = column(*controls, width=320)

l = column(desc, row(inputs, p), sizing_mode="scale_both")

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "SNL Alumni"
