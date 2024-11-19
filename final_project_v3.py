"""
Name: Lucas Daignault
CS230: Section 05
Data: Nuclear Explosions 1945-1998
URL: https://nuclearexplosionsv3-ba2d3vexvwircmj7b3ymtv.streamlit.app/

Description: This program provides data visualization which helps the user learn about the nuclear testing and use
of several nuclear-armed countries. By filtering based on country, year, blast yield, etc., the user
can interactively learn about the nuclear-armed countries strategies, strengths, and the nature of their tests, which continue
to cause controversy today.

"""


import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import plotly.express as px

# graph colors (Tableau Palette from matplotlib)
colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:cyan"]

# read the data in the csv into a DataFrame
def read_data():
    df = pd.read_csv("nuclear_explosions.csv")
    df["Underground"] = df["Location.Cordinates.Depth"].apply(lambda x: True if x > 0 else False)       # [DA1], [DA7], [DA9]
    return df

# apply filtering to a specified DataFrame
def filter(df, countries, min_yield, max_yield, min_year, max_year, show_underground=False):
    df = df.loc[df["WEAPON SOURCE COUNTRY"].isin(countries)]        # [DA4]
    df = df.loc[df["Data.Yeild.Upper"] >= min_yield]        # [DA5]
    df = df.loc[df["Data.Yeild.Upper"] <= max_yield]
    df = df.loc[df["Date.Year"] >= min_year]
    df = df.loc[df["Date.Year"] <= max_year]
    if show_underground == True:
        df = df.loc[df["Underground"] == True]
    return df

# create a list of all countries
def all_countries(df):
    lst = []
    for ind, row in df.iterrows():      # [DA8]
        if row["WEAPON SOURCE COUNTRY"] not in lst:
            lst.append(row["WEAPON SOURCE COUNTRY"])
    return lst

# count the frequency of detonations by country
def country_frequency(df, countries):
    # first part of the list comp filters dataset to only take countries included in the multiselect (and determines length AKA count). Second part of the list comp adds the count to the list
    country_count_list = [df.loc[df["WEAPON SOURCE COUNTRY"].isin([country])].shape[0] for country in countries]  # PY4     >> Syntax inspiration is from the "CS 230 Final Project Example" video
    return country_count_list

# creates a pie chart which breaks down detonations by country
def generate_pie_chart(counts, countries):      # [VIZ1]
    plt.figure()
    plt.pie(counts, autopct="%1.1f%%", labeldistance=1.1, colors=colors)        # labeldistance from https://www.analyticsvidhya.com/blog/2024/02/pie-chart-matplotlib/#:~:text=To%20add%20labels%20and%20percentages,the%20percentages%20should%20be%20displayed.
    plt.title("Detonations by Country")
    plt.legend(countries, title="Countries", bbox_to_anchor=(1, 1))       # (horizontal, vertical)
    # plt.show()
    return plt

# creates a bar chart which breaks down detonations by country
def generate_bar_chart(counts, countries):      # [VIZ2]
    fig = plt.figure()
    bars = plt.bar(countries, counts, color=colors)

    # data labels (based on CS 230 course video)
    for i, bar in enumerate(bars):
        formatted_value = f"{counts[i]:,.0f}"
        plt.annotate(formatted_value, xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     xytext=(0, 3), textcoords='offset points', ha='center', va='bottom')

    plt.title("Detonations by Country")
    plt.ylabel("Number of Detonations")

    # plt.show()
    return fig

# creates a dictionary with keys = countries and values = yields
def country_yields(df):
    # creates a list of yields and a list of countries
    yields = [row["Data.Yeild.Upper"] for index, row in df.iterrows()]  # goes through each fow in the df, gathers all the yields into a list       >> Syntax inspiration is from the "CS 230 Final Project Example" video
    countries = [row["WEAPON SOURCE COUNTRY"] for index, row in df.iterrows()]  # creates a list of all countries

    # we need to combine the two above lists into a dict
    dict = {}       # [PY5]

    # initialize the dict by adding each country as a key
    for country in countries:
        dict[country] = []  # create  dictionary with countries as keys so that we can then append a the value

    # append each country's yields to its dict key
    for i in range(len(yields)):
        dict[countries[i]].append(yields[i])  # take each country key and append a yield to its value

    # return the dict where keys are countries and yields are keys
    return dict

# update the dictionary created above so that the keys = countries and the values = the highest yield from that country
def country_max_yield(dict_yields):
    dict = {}
    for key in dict_yields.keys():
        dict[key] = max(dict_yields[key])  # replaces values currently in dict (list of all yields) with the max yield
    return dict

# creates bar chart which graphs the above-determined highest yield from each country
def generate_max_bar_chart(dict_yields):
    fig = plt.figure()

    x = dict_yields.keys()
    y = dict_yields.values()
    num = list(y)

    bars = plt.bar(x, y, color="tab:red")

    # data labels
    for i, bar in enumerate(bars):
        formatted_value = f"{num[i]:,.0f}"
        plt.annotate(formatted_value, xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     xytext=(0, 3), textcoords='offset points', ha='center', va='bottom')

    plt.title("Max Detonation Yield by Country")
    plt.ylabel("Detonation Yield (kilotons of TNT)")
    # plt.show()
    return fig

# sorts the df by yield size, in descending order. pulls and returns the top five rows, or the top five largest yields
def largest_yield_table(df):
  dfSorted = df.sort_values(by="Data.Yeild.Upper", ascending=False)     # [DA2]
  dfSorted = dfSorted[["WEAPON SOURCE COUNTRY", "WEAPON DEPLOYMENT LOCATION", "Date.Year", "Data.Yeild.Upper"]]
  dfSorted = dfSorted.iloc[:5]      # [DA3]
  return dfSorted

# creates map of all bomb detonation locations; includes tool tips
def generate_map(df):       # [MAP]
    map_df = df.filter(["Data.Name", "Location.Cordinates.Latitude", "Location.Cordinates.Longitude", "Data.Yeild.Upper", "Date.Year", "WEAPON SOURCE COUNTRY"])
    fig = px.scatter_mapbox(map_df,
                         lat=map_df["Location.Cordinates.Latitude"],
                         lon=map_df["Location.Cordinates.Longitude"],
                         hover_name="Data.Name",
                         hover_data=["WEAPON SOURCE COUNTRY", "Data.Yeild.Upper", "Date.Year"],
                         color="Date.Year",
                         color_continuous_scale="Rainbow",      # there are several other themes which can be used, but Rainbow was the most visible
                         mapbox_style="carto-positron")        # this code is from the plotly documentation (https://plotly.com/python/scatter-plots-on-maps/)
    fig.update_layout(height=700,
                      mapbox_zoom=1,
                      mapbox_center={"lat": map_df["Location.Cordinates.Latitude"].mean(), "lon": map_df["Location.Cordinates.Longitude"].mean()})
    return fig

# creates a line chart which shows the number of atomic bombs tested over time. includes tool tips and annotations
# code for generate_line_chart based on code from ChatGPT. See section 1 of accompanying document.
def generate_line_chart(df):
    # create a pivot table which shows the number of detonations per year
    pivot_table = df.pivot_table(index='Date.Year', aggfunc='size', columns=None, fill_value=0)     # [DA6]
    pivot_table = pivot_table.rename("Detonations Count")
    pivot_table_reset = pivot_table.reset_index()
    pivot_table_reset.head()
    # graph the pivot table using plotly
    fig = px.line(pivot_table_reset, x="Date.Year", y="Detonations Count", title="Number of Detonations over Time",
                  template="simple_white", labels={"Date.Year": "Year", "Detonations Count": "Number of Detonations"})
    fig.add_annotation(     # annotations from https://plotly.com/python/text-and-annotations/
        x=1958, y=116,
        text="Bilateral Testing Ban signed",
        showarrow=True,
        arrowhead=2,
        ax=0, ay=-40)
    fig.add_annotation(
        x=1963, y=50,
        text="Partial Nuclear Test Ban Treaty signed",
        showarrow=True,
        arrowhead=2,
        ax=0, ay=40)
    fig.add_annotation(
        x=1991, y=14,
        text="USSR collapses",
        showarrow=True,
        arrowhead=2,
        ax=0, ay=-40)
    return fig

# returns output statistics that helps the user get a feel for the amount of the data they are visualizing
def output_statistics(df, filtered_df):
    total_detonations = df.shape[0]
    selected_detonations = filtered_df.shape[0]
    return total_detonations, selected_detonations      # [PY2]

# function which can change the Streamlit font color
def font_color(text, color="blue"):        # PY1
    output = ":" + color + "[" + text + "]"     # https://discuss.streamlit.io/t/colored-text/34892/2
    return output

# builds the Streamlit and runs the program
def main():
    # read in the data & modify with lambda
    df = read_data()

    # Streamlit web app outputs:

    # title & header section
    st.title(font_color("Nuclear Bomb Detonations Data Analysis"))
    st.write(font_color("By Lucas Daignault, F24 CS 230", "red"))
    st.write("Detonation yield is measured in kilotons of TNT. One kiloton = 1,000 tons of TNT. 1 megaton = 1,000 kilotons, or 1,000,000 tons of TNT. For reference, the Allies dropped approximately 2.7 million tons of TNT on Europe during WWII. ")
    st.write("")

    # sidebar
    st.sidebar.write("Please choose your options to display data")      # [ST4]
    countries = st.sidebar.multiselect("Select a country:", all_countries(df),default=["USA", "USSR", "CHINA"])     # [ST1]
    yield_range = st.sidebar.slider("Select a blast yield range:", min_value=0, max_value=50000, value=(0,50000))       # [ST2]
    year_range = st.sidebar.slider("Select a year range:", min_value=1945, max_value=2000, value=(1945, 2000))
    show_underground = st.sidebar.checkbox("Check the box to only show underground tests", value=False)     #[ST3]
    st.sidebar.write("Note that the underground data is imprecise due to classification.")

    # filtered data
    df_filtered = filter(df, countries, yield_range[0], yield_range[1], year_range[0], year_range[1], show_underground)

    # if statement is to prevent the streamlit app from crashing in the event that no data is selected
    if len(df_filtered) > 0:

        # query 1: how many nuclear bombs did selected countries detonate during the selected time period?
        st.subheader("How many nuclear bombs within selected parameters did countries detonate?")
        st.write("")
        st.pyplot(generate_pie_chart(country_frequency(df_filtered, countries),countries))
        st.pyplot(generate_bar_chart(country_frequency(df_filtered, countries),countries))
        st.write("")

        # query 2: what were the largest bombs dropped? what were the largest bombs dropped by country?
        st.subheader("What was the detonation yield of the largest bomb each country had?")
        st.write("")
        st.pyplot(generate_max_bar_chart(country_max_yield(country_yields(df))))
        st.write("")
        st.write("The largest five detonations were:")
        st.dataframe(largest_yield_table(df).style.format({"Date.Year": "{:.0f}", "Data.Yeild.Upper": "{:,.0f}"}))
        st.write("")
        st.write("In 2020, Russia released previously classified footage of the 'Tsar bomba,' the largest nuclear detonation in history:")
        st.video("https://www.youtube.com/watch?v=YtCTzbh4mNQ")
        st.markdown("""
        **Some facts about the Tsar Bomba:**
        * The Tsar Bomba was considered a 'political event,' hence the footage
        * The blast wave created was so strong that it circled the earth three times
        * The Tsar Bomba had the same blast yield as all explosives used in WWII... times 10
        * The Tsar Bomba was originally designed to yield 100 megatons, or 100,000 kilotons. Out of fear, the designers scaled down the yield to 'only' 50 megatons, or 50,000 kilotons. 
        * The Americans invested heavily in creating accurate missiles; the Soviets instead opted to make a bomb large enough that the delivery could be imprecise
        """)
        st.write("")

        # query 3: where were bombs dropped (map)?
        st.subheader("Where were bombs within selected parameters detonated?")
        st.plotly_chart(generate_map(df_filtered), use_container_width=True)       # filtered to show only the bombs detonated within the user-selected parameters
        st.write("")

        # query 4: show bombs over time to identify especially intense testing periods
        st.subheader("When were bombs detonated?")
        st.write("")
        st.plotly_chart(generate_line_chart(df))
        st.write("")
        st.markdown("""
        **Notes on the above chart:**
        * The U.S. was the first country to develop an atomic bomb; the USSR detonated their first bomb in 1949
        * In 1958, the Soviet Union unilaterally stopped testing bombs, provided the west also would. The USA agreed and lasts until 1961 when the Soviets repeal the ban. 
        * In 1963, the Partial Nuclear Test Ban Treaty was signed. In anticipation for the moratorium on all but underground testing, both the U.S. and USSR conducted as many non-underground tests as possible
        * There were several treaties banning the testing of nuclear weapons in interesting places. For instance, the Antarctic Treaty System, Outer Space Treaty, Seabed Arms Control Treaty, and the Moon Treaty 
        * The U.S., Soviet Union, UK, China, and France all discontinued nuclear testing by the end of 1996. India and Pakistan most recently tested nuclear weapons in 1998. North Korea most recently tested a nuclear weapon in 2017.  
        """)

        # output stats at the bottom of the page
        st.subheader("Output statistics:")
        st.write("")
        total_detonations, selected_detonations = output_statistics(df, df_filtered)
        st.write(f"Total number of detonations: {total_detonations:,.0f}")        # << insert total number of detonations
        st.write(f"Detonations from selected countries: {selected_detonations:,.0f}")  # << insert total number of detonations

    else:
        st.subheader("No detonations match your search. Please update the search parameters.")

# run code
main()
