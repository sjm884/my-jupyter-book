#!/usr/bin/env python
# coding: utf-8

# ## Exploratory Data Analysis of The Vancouver Street Trees Dataset
# 
# This report was prepared by Sarah McDonald on December 12, 2021, as the final project for a Data Visualization class at the University of British Columbia using a [subset](https://raw.githubusercontent.com/UBC-MDS/data_viz_wrangled/main/data/Trees_data_sets/small_unique_vancouver.csv) of the Vancouver Street Trees Data {cite}`vancouvertrees` provided.
# 
#  ```{figure} images/tree-vancouver.jpg
#  ---
#  name: street-trees
#  ---
#  Street trees in Vancouver
#  ```

# In[1]:


# Import libraries needed for this analysis
import pandas as pd
import altair as alt
import json


# pandas {cite}`The_pandas_development_team_pandas-dev_pandas_Pandas` is used to handle data, altair {cite}`altair` is a package used for graphing, and json {cite}`Lohmann_JSON_for_Modern_2022` is used to [create maps.](city-map)

# In[2]:


# Load in the data and view a subset
trees_url = 'https://raw.githubusercontent.com/UBC-MDS/data_viz_wrangled/main/data/Trees_data_sets/small_unique_vancouver.csv'
trees_df = pd.read_csv(trees_url, parse_dates=['date_planted'])
trees_df.head()


# In[3]:


# get more information about our datasset
trees_df.info()


# ## Questions of Interest
# For this analysis I am interested in how the number and type of trees planted has changed over time. From our initial look at the data, I can see that a lot of values are missing from the 'date_planted' column. This could be an error in data recording or it could be that we don't have records of when older trees were planted. To visualize the gaps in our data, let's first plot the dates we do have.

# In[4]:


# rug plot to visualize date_planted column data
trees_date = alt.Chart(trees_df).mark_tick().encode(
             alt.X("date_planted:T", scale=alt.Scale())
             )

trees_date


# It looks like we have continuous data from 1989-2019. If our theory is correct and data without values in the ‘date_planted’ column is from older trees, we could expect these trees to be larger than trees planted more recently. Let’s see if that holds true for our data. 
# 
# To make the data easier to filter I will use the pandas {cite}`The_pandas_development_team_pandas-dev_pandas_Pandas` package to add a new column to our data frame. A simple boolean will let us see if the date planted is availabe for that entry. 
# 
# ```python
# {
#     trees_nan = trees_df.assign(date_record = trees_df.isna().loc[:,'date_planted'])
# }
# ```

# In[5]:


# add a boolean column to our datafrom for data_planted data available
trees_nan = trees_df.assign(date_record = trees_df.isna().loc[:, 'date_planted'])
trees_nan.head()


# To account for differences in species we want to break the records down by species. First let's see how many species we are working with.

# In[6]:


species = trees_nan.groupby("species_name")
species.describe()


# (top-10)=
# ## Top 10
# 171 is a lot of species to visualize all at once. Let's find our top 10 using the pandas package {cite}`The_pandas_development_team_pandas-dev_pandas_Pandas` to group entries by their common name, count those entries, and sort from most to least common. Then we can filter so we see only the first 10 entries, the 10 most common trees planted!
# 
# ```python
# {
#     trees_common = (trees_nan.groupby("common_name").count().sort_values(by='tree_id', ascending=False
#                     ).reset_index().loc[0:9])
# 
# }
# ```

# In[7]:


#find the 10 most common trees in our dataset
trees_common = (trees_nan.groupby("common_name").count().sort_values(by='tree_id', ascending=False
                ).reset_index().loc[0:9])
trees_common = trees_common["common_name"].tolist()
trees_common


# In[8]:


# filter trees_nan to include only the most common trees
common_records = trees_nan.common_name.isin(trees_common)
trees_nan_small = trees_nan[common_records]


# In[9]:


# chart average tree diameter per species (most common)
tree_diam = alt.Chart(trees_nan_small).mark_boxplot().encode(
            alt.X('diameter:Q'),
            alt.Y('common_name:N'),
            ).properties(width=300).facet('date_record')
tree_diam


# (age-est) = 
# ## Age Estimation
# As we can see from the chart above, trees without a date record do have a higher median diameter than trees with a date record. Trees increase in circumference as they age, a general formula for estimating the age of a trees is the diameter of the tree multiplied by a growth factor specific to the species.{cite}`Lukaszkiewicz2008`  
# 
# $$
#   age \approx \frac{C}{\pi} \times G
# $$
# 
# Where $\pi$ is defined as the ratio between the circumferance of a circle to its diameter.
# 
# $$
#     \pi = \frac{C}{d}
# $$
# 
# Our theory that trees without date records are older seems be correct, we will exclude these values from future plots regarding date. To make analysis easier, I will add a column with just the year planted.

# In[10]:


# remove entries with no date_planted
trees_small = trees_df.dropna(subset=['date_planted'])
# create a new column with just year 
trees_small = trees_small.assign(year_planted = trees_small['date_planted'].dt.year)


# In[11]:


# number of trees planted over time
trees_time = alt.Chart(trees_small).mark_bar().encode(
             alt.X('year_planted:O'),
             alt.Y('count()'))
trees_time


# (click-filter)=
# ## Click to filter
# Let's make this chart clickable so we can filter our top 10 tree species by year. 

# In[12]:


click_year = alt.selection_multi(encodings=['x'], on='click')
click_trees_year = (trees_time.encode(
                   opacity=alt.condition(click_year, alt.value(1), alt.value(0.5)))
                  .properties(height=100, width=500)
                  .add_selection(click_year))


# In[13]:


# select 10 most common trees based on year
species_select = (alt.Chart(trees_small).transform_filter(click_year).mark_bar().encode(
                    alt.Y('species_name:N', sort='x'),
                    alt.X('species_count:Q'),
                    ).transform_aggregate(
                    species_count="count()",
                    groupby=["species_name"]
                    ).transform_window(
                    rank='rank(species_count)',
                    sort=[alt.SortField("species_count", order="descending")]
                    ).transform_filter((alt.datum.rank <= 10)).add_selection(click_year))
species_select & click_trees_year


# Interesting, there is less overlap in the top 10 species per year than I thought there would be. Now, I would like to look more at the size of trees. I wonder how the method of planting affects a tree's size. To visualize I will use our [top 10 data subset](Top-10).

# In[14]:


# Tree diameter vs height colored by species
tree_height = alt.Chart(trees_nan_small).mark_circle().encode(
              alt.X('diameter:Q'),
              alt.Y('height_range_id:Q'),
              color='species_name:N'
              )
tree_height


# In[15]:


# facet our size chart by root barrier
tree_height.facet('root_barrier:N')


# In[16]:


# facet tree size by side of street
tree_side = tree_height.properties(width=200).facet('street_side_name')
tree_side


# (root-barriers)=
# ## Barriers to barriers
# It looks like the side of the street trees are planted on makes no difference to size however, trees planted with a root barrier do seem to be smaller. Let's see if the trees with root barriers are younger than those without using our full dataset.
# 
#  ```{figure} images/root-barrier.jpg
#  ---
#  name: root-barrier
#  ---
#  An example of a root barrier. These are used to prevent tree roots from damaging the sidewalk.
#  ```

# In[17]:


root_barrier = trees_time.encode(color="root_barrier:N")
root_barrier


# It looks like most of the trees with root barriers were planted between 2004 and 2009. Let's filter our data to include just those years and see if the pattern still holds. 

# In[18]:


tree_height_filter = alt.Chart(trees_small).transform_filter(
                   alt.FieldRangePredicate(field='year_planted', range=[2004, 2009])
                   ).mark_circle().encode(
                   alt.X('diameter:Q'),
                   alt.Y('height_range_id:Q')
                   ).properties(width=300).facet('root_barrier:N')
tree_height_filter


# When we filter just for years that used root barriers the size difference is much less pronounced. Our initial observations about [root barriers](root-barriers) could have been because a smaller percentage of the data used root barriers.
# 
# Now, lets see how the trees are distributed over Vancouver. As part of this course code was provided to create a base [map of Vancouver.](city-map)

# In[19]:


# load data to make a map of vancouver (code provided)
url_geojson = 'https://raw.githubusercontent.com/UBC-MDS/exploratory-data-viz/main/data/local-area-boundary.geojson'
data_geojson_remote = alt.Data(url=url_geojson, format=alt.DataFormat(property='features',type='json'))
data_geojson_remote


# In[20]:


# base map of Vancouver (code provided)
vancouver_map = alt.Chart(data_geojson_remote).mark_geoshape(
    color = 'white', opacity= 0.5, stroke='black').encode(
).project(type='identity', reflectY=True)

vancouver_map


# In[21]:


#Map location of all trees in Vancouver
points = alt.Chart(trees_small).mark_circle(size=20).encode(
         longitude='longitude',
         latitude='latitude',
         ).project(type= 'identity', reflectY=True)

point_map = (vancouver_map + points)
point_map


# To see how the distribution changes over time I am going to use the [clickable year chart](click-filter) we made earlier.

# In[22]:


point_map = point_map.encode(
                opacity=alt.condition(click_year, alt.value(1), alt.value(0.1)),
                color="species_name:N"
                ).add_selection(click_year)
point_map & click_trees_year


# ## Conclusion
# Interesting, over the years the distribution seems to be spread out evenly. I would have guessed that the street tree program would have started in a few neighbourhoods and branched out from there. There also doesn't seem to be any clusters of particular species in neighbourhoods but it is hard to tell with so many species to consider. For the analysis report I think it will be interesting to explore the distribution of species planted over time and space using both time charts and a map. Linking our [top 10 species per year chart](top-10) will make the species distribution much easier to visualize. I am also very interested in our findings about the size of trees and [root barriers](root-barriers) so I will include those in our report as well.
# 
# ```{bibliography} references.bib
# ```

# In[ ]:




