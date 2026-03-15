'''   
1. Install streamlit, plotly.express and (panda)
2. Make sure they are installed in the same directory as this file
3. Use the following command in terminal
   python -m streamlit run B25CS003.py
'''


import streamlit as stream
import plotly.express as plotly


stream.title("Health v/s Wealth: A Global Perspective")

#Loading the builtin gapminder dataset from plotly 
dataset = plotly.data.gapminder()


#Part 1 Interactive Bubble Chart

stream.header("Wealth v/s Health (1952-2007)")
stream.write("See how life expectancy and GDP changed for all of the countries over time")


#Slider to select the year
year = stream.slider("Select a Year:", 
                 min_value=int(dataset['year'].min()), 
                 max_value=int(dataset['year'].max()), 
                 step=5)
#Using step 5 because the data was released every 5 years
#Filtering the main data based on year selected in slider
dataforbubble = dataset[dataset['year'] == year]



scatter_figure = plotly.scatter(
    dataforbubble,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    hover_name="country",
    log_x=True,             # Using log scale for x-axis
    size_max=60,
    title=f"Global Health vs. Wealth in {year}"
)


stream.plotly_chart(scatter_figure)


#Part 2 Comparing specific Countries

stream.header("Compare countries over time")
stream.write("Select one or more countries to get started")

#Dropdown List
all_countries = dataset['country'].unique()


selected_countries = stream.multiselect(
    "Select Countries:",
    options=all_countries,
    default=["India", "China", "United States"]
)


#Filtering the data
dataforline = dataset[dataset['country'].isin(selected_countries)]


stream.subheader("Life Expectancy Over Time")
line_life = plotly.line(
    dataforline,
    x="year",
    y="lifeExp",
    color="country",
    title="Life Expectancy"
)
stream.plotly_chart(line_life)


stream.subheader("GDP per Capita Over Time")
line_gdp = plotly.line(
    dataforline,
    x="year",
    y="gdpPercap",
    color="country",
    title="GDP per Capita"
)
stream.plotly_chart(line_gdp)
