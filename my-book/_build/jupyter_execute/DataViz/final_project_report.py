#!/usr/bin/env python
# coding: utf-8

# # Variety of Vancouver Street Trees
# 
# This report was prepared by Sarah McDonald on December 15, 2021, as the final project for a Data Visualization class at the University of British Columbia using a [subset](https://raw.githubusercontent.com/UBC-MDS/data_viz_wrangled/main/data/Trees_data_sets/small_unique_vancouver.csv) of the Vancouver Street Trees dataset.{cite}`vancouvertrees`

# ## Introduction
# Vancouver is a beautiful city. A big part of the appeal is how the natural landscape has been incorporated into the cityscape. In this report I will examine how the variety, density, and number of street trees in Vancouver has changed over time.
# 
#  ```{figure} images/van.jpg
#  ---
#  name: ariel-van
#  ---
#  An ariel view of Vancouver
#  ```

# ## Analysis

# In[1]:


# Import libraries needed for this analysis
import pandas as pd
import altair as alt
import json
from myst_nb import glue
#alt.data_transformers.enable("data_server")

# Load in the data
trees_url = 'https://raw.githubusercontent.com/UBC-MDS/data_viz_wrangled/main/data/Trees_data_sets/small_unique_vancouver.csv'
trees_df = pd.read_csv(trees_url, parse_dates=['date_planted'])

#remove colunm that represented the index in the origional dataset
trees_df = trees_df.drop(columns=['Unnamed: 0'])


# ## Describe the dataset
# This dataset is available on the City of Vacouver's [open data portal](https://opendata.vancouver.ca/explore/dataset/street-trees/information/?disjunctive.species_name&disjunctive.common_name&disjunctive.height_range_id). The website describes it as follows: 
# 
# "The street tree dataset includes a listing of public trees on boulevards in the City of Vancouver and provides data on tree coordinates, species and other related characteristics. Park trees and private trees are not included in the inventory."
# 
# The dataset contains 1 table with 18 columns described as follows: 
# ### TREE_ID
# Numerical ID
# ### CIVIC_NUMBER
# Street address of the site at which the tree is associated with
# ### STD_STREET
# Street name of the site at which the tree is associated with
# ### GENUS_NAME
# Genus name
# ### SPECIES_NAME
# Species name
# ### CULTIVAR_NAME
# Cultivar name
# ### COMMON_NAME
# Common name
# ### ASSIGNED
# Indicates whether the address is made up to associate the tree with a nearby  lot (Y=Yes or N=No)
# ### ROOT_BARRIER
# Root barrier installed (Y = Yes, N = No)
# ### PLANT_AREA
# B = behind sidewalk, G = in tree grate, N = no sidewalk, C = cutout, a number  indicates boulevard width in feet
# ### ON_STREET_BLOCK
# The street block at which the tree is physically located on
# ### ON_STREET
# The name of the street at which the tree is physically located on
# ### NEIGHBOURHOOD_NAME
# City's defined local area in which the tree is located.  For more information, see theLocal Area Boundary Datapage.
# ### STREET_SIDE_NAME
# The street side which the tree is physically located on (Even, Odd or Median  (Med))
# ### HEIGHT_RANGE_ID
# 0-10 for every 10 feet (e.g., 0 = 0-10 ft, 1 = 10-20 ft, 2 = 20-30 ft, and10 = 100+ ft)
# ### DIAMETER
# DBH in inches (DBH stands for diameter of tree at breast height)
# ### CURB
# Curb presence (Y = Yes, N = No)
# ### DATE_PLANTED
# The date of planting in YYYYMMDD format.  Data for this field may not be available for all trees.
# ### GEOM
# Spatial representation of feature
# *Expressed as 'latitude and 'longitude' in the subset used for this assignment
# 
# ### Note
# 
# I am using a [subset](https://raw.githubusercontent.com/UBC-MDS/data_viz_wrangled/main/data/Trees_data_sets/small_unique_vancouver.csv) of this dataset. For this assignment, 5000 random rows were provided and, the GEOM column was broken into 'latitude and 'longitude'. The origional index of each row contained in the column "Unnamed: 0" was dropped for this analysis. 
# 
# ## Data Summary

# In[2]:


# Get more information about the dataset
trees_df.info()
print("\n")
trees_df.describe()


# For this analysis, I am interested in how the number and type of street trees planted in Vancouver has changed over time. From our initial look at the data, we can see that a lot of values are missing from the 'date_planted' column. This could be an error in data recording or it could be that we don't have records of when older trees were planted. In my [exploratory analysis](final_project_EDA.ipynb), I found that we have continuous data from 1989-2019. For this report, we will exclude data where the date planted is not available. To simplify the analysis I will only include the year when plotting the date planted. 

# In[3]:


# remove entries with no date planted
trees_small = trees_df.dropna(subset=['date_planted'])

# create a new date column with just year 
trees_small = trees_small.assign(year_planted = trees_small['date_planted'].dt.year)


# ### Question 1: How has the number and type of trees planted changed over time?

# In[4]:


# number of trees planted over time
trees_time = alt.Chart(trees_small).mark_bar(color='darkgray').encode(
             alt.X('year_planted:O', title="Year Planted"),
             alt.Y('count()', title="Number of Trees"))
glue("trees_time", trees_time, display=False)


# ```{glue:figure} trees_time
# :name: = trees_time
# "Number of Vancouver Street Trees Planted Over Time"
# ```

# From {numref}`trees_time`, we can see that the number of trees planted over the years has varied, with the largest spikes around 1996, 2002, and 2013. Now, let's see how the species planted has changed over time. Our dataset contains 171 different species so, we will break this down to the top 10 of each year.

# In[5]:


# Make selection chart based on year
click_year = alt.selection_multi(encodings=['x'], on='click')
click_trees_year = (trees_time.encode(
                   opacity=alt.condition(click_year, alt.value(1), alt.value(0.5)))
                  .properties(height=100, width=500)
                  .add_selection(click_year))

# select 10 most common trees per year
species_select = (alt.Chart(trees_small).transform_filter(click_year).mark_bar().encode(
                    alt.Y('species_name:N', sort='x', title="Species Name"),
                    alt.X('species_count:Q', title="Amount Planted"),
                    alt.Color('species_name:N', legend=None, scale=alt.Scale(scheme='category20'))
                    ).transform_aggregate(
                    species_count="count()",
                    groupby=["species_name"]
                    ).transform_window(
                    rank='rank(species_count)',
                    sort=[alt.SortField("species_count", order="descending")]
                    ).transform_filter((alt.datum.rank <= 10)
                    ).add_selection(click_year).properties(height=250))
(species_select & click_trees_year)
glue("species_select",species_select, display=False)


# ```{glue:figure} species_select
# :name: = species_select
# "Top 10 Vancouver Street Tree Species Planted Per Year"
# ```

# Interesting, while there has been a wide variety of species chosen over the years it looks like some species, such as Platanoides, have remained popular. This is a species of maple not native to BC. Now, I would like to examine tree growth. 
#  ```{figure} images/platanoides.jpg
#  ---
#  name: platanoides
#  ---
# Platanoides, a species of maple. 
#  ```
# 

# ### Question 2: Has the method of planting affected the growth of the trees?

# While we do have specific information about where each tree was planted, I am most interested in planting methods that cover or restrict the roots. A healthy root system is essential to tree growth, my hypothesis is that planting trees with a [root barrier](root-barriers) will stunt the growth of the tree. To measure growth, we have both diameter and height. Diameter can be used to estimate the [age of a tree](age-est)

# In[6]:


# Create a scatter plot to visualize tree growth
size_chart = (alt.Chart(trees_small).transform_filter(click_year).mark_circle().encode(
                    alt.Y('height_range_id:Q', title="Height"),
                    alt.X('diameter:Q', title=("Diameter")),
                    alt.Color('species_name:N', legend=None, scale=alt.Scale(scheme='category20')),
                    tooltip=[alt.Tooltip('species_name', title='Species'), 
                             alt.Tooltip('height_range_id', title='Height'),
                             alt.Tooltip('diameter', title='Diameter')],
                    facet=alt.Facet('root_barrier:N', title="Root Barrier Y/N")
                    ).add_selection(click_year) 
                    .properties(height=200, width=250))

# Make chart selectabe with year chart
size_click = (size_chart & click_trees_year)
glue("size_click", size_click, display=False)


# ```{glue:figure} size_click
# :name: = size_click
# "Tree Growth Stunted by Root Barriers, Click on a bar to filter by year"
# ```
# 

# {numref}`size_click` does seem to suggest size difference between trees that were planted with and without root barriers however, it is hard to tell given how little data we have on trees planted with root barriers. Perhaps it is a good thing they fell out of fashion. We can see from the chart that planting with a root barrier was most popular between 2004 and 2009. Now, I would like to see the distribution of trees planted throughout Vancouver. The code for creating the map of Vancouver was provided as part of this assignment
# 
# ### Question 3: How has the distribution of trees around Vancouver changed over time?

# In[7]:


# load data to make a map of vancouver (code provided)
url_geojson = 'https://raw.githubusercontent.com/UBC-MDS/exploratory-data-viz/main/data/local-area-boundary.geojson'
data_geojson_remote = alt.Data(url=url_geojson, format=alt.DataFormat(property='features',type='json'))

# base map of Vancouver (code provided)
vancouver_map = alt.Chart(data_geojson_remote).mark_geoshape(
    color = 'white', opacity= 0.5, stroke='black').encode(
).project(type='identity', reflectY=True)

#Map location of all trees in Vancouver
points = alt.Chart(trees_small).mark_circle(size=10).encode(
         longitude='longitude',
         latitude='latitude'
         ).project(type= 'identity', reflectY=True)
# Layer points and Vancouver map. Add filter for year planted
point_map = (vancouver_map + points).add_selection(click_year).encode(
            opacity=alt.condition(click_year, alt.value(1), alt.value(0.05)))
#add year chart to filter data
click_trees_year = click_trees_year.encode(color=alt.value('darkgray'))
point_click_year = (point_map & click_trees_year)
glue("point_click_year",point_click_year, display=False)


# ```{glue:figure} point_click_year
# :name: = point_click_year
# "Location of Vancouver Street Trees. Click on a bar to filter by year."
# ```

# It is interesting to see that the Vancouver Street Trees were planted evenly throughout the city over the years rather than starting in one neigbourhood and expanding from there.
# 
# ## Discussion
# 
# Vancouver street trees have been beautifying the city for decades. We have data about when trees were planted, location, size, and planting methods from 1989 to 2019. As we saw in {numref}`trees_time`, the distribution of trees planted has been fairly consistent over the years with spikes around 1998, 2002, and 2013. Between 1989 and 2019, 171 different species of trees were planted in Vancouver. We saw in {numref}`species_select` that the top 10 species planted each year has varied greatly over the years with Rubrum, Plantanoids, and Zumi making frequent appearances in the top 10. I think it would be interesting to explore more about the species chosen, I wonder how many of these are native species. In the beginning of this analysis, I was interested in how the planting method might affect growth of the trees. {numref}`size_click` showed that there is a much smaller difference between the size of trees planted with and without a root barrier than I theorized. However, we also saw that [root barrier](root-barriers) planting methods were only popular between 2004 and 2009 so, we don’t have enough data to draw any hard conclusions about the effects of root barrier planting on tree size. Finally, in {numref}`point_click_year` we saw that the distribution of trees across Vancouver has been consistent over the years, rather than growing out from a few neighbourhoods. I think we can all appreciate the biodiversity that makes our city unique. 
# 
# ## Dashboard

# In[8]:


# Create selection widgets
root_barrier = sorted(trees_small['root_barrier'].unique())
radiobuttons_root = alt.binding_radio(name='Root Barrier ', options=root_barrier)
year_max = trees_small['year_planted'].max()
year_min = trees_small['year_planted'].min()
year_slider = alt.binding_range(
              name='Year Planted ', min=year_min, max=year_max, step=1)
select_dashboard = alt.selection_single(
                   fields=['year_planted', 'root_barrier'],
                   bind={'year_planted': year_slider, 'root_barrier': radiobuttons_root},
                   init={'root_barrier': 'N', 'year_planted': year_min})
# add selection filter to point map
point_map = point_map.add_selection(select_dashboard).encode(
            opacity=alt.condition(select_dashboard, alt.value(1), alt.value(0.05)))
# add selection filter to top 100 species chart
species_select = (alt.Chart(trees_small).transform_filter(select_dashboard).mark_bar().encode(
                    alt.Y('species_name:N', sort='x', title="Species Name"),
                    alt.X('species_count:Q', title="Amount Planted"),
                    alt.Color('species_name:N', legend=None, scale=alt.Scale(scheme='category20'))
                    ).transform_aggregate(
                    species_count="count()",
                    groupby=["species_name"]
                    ).transform_window(
                    rank='rank(species_count)',
                    sort=[alt.SortField("species_count", order="descending")]
                    ).transform_filter((alt.datum.rank <= 10))
                    ).properties(height=200, width=250, title="Click to Select Species")
# make top 10 species chart clickable
click_species = alt.selection_multi(encodings=['y'], on='click', nearest=True)
species_select = species_select.add_selection(click_species).encode(
                 opacity=alt.condition(click_species, alt.value(1), alt.value(0.05)))
# filter point map by species. Encode diameter to size
point_map = point_map.encode(
            size=alt.Size('diameter:Q', legend=None, title="Diameter"),
            color=alt.condition(click_species, 'species_name:N', alt.value('white'))
            ).add_selection(click_species)
#Layer charts and add title
((point_map | species_select)
 .properties(title={'text': ["Size and Distribution of Vancouver Street Trees"],
            'subtitle': ["Filter by top 10 species per year. Point size is proportional to tree diameter."]}
            ).configure_title(anchor='middle'))


# ## References
# 
# ```{bibliography}
# :style: unsrt
# ```
