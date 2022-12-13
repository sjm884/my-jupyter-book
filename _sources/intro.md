# Welcome to Sarah's Jupyter Book!
This book was prepared for Assignment 8 of the *Data science tool box* course at the University of British Columbia. 

```{figure} images/UBC_logo.png
The UBC Logo
 ---
 ```
## Content
To create this book, I will be using my final project from the *Data Visualization* course taken in 2021 as part of the *Key fundamentals in data science* certificate from UBC. This project explored the Vancouver Street Trees data {cite}`vancouvertrees` available from the City of Vancouver.
```{margin} Did you know?
The Vancouver Street Trees Dataset has been downloaded over 5000 times!
```
```{figure} images/vancouver.jpg
 ---
 The City of Vancouver
 ```
```{note}
You can find the Vancouver Street Trees dataset in the City of Vancouver's Open Data Portal.
```
 
(city-map)= ## City Map
As part of this project, the folowing code was provided to allow us to visualize the distribution of these street trees on a map of Vancouver.
```{note}
You can find 4 different world projections from vega_datasets
```
First, loading a *.geojson* using JSON libraries {cite}'Lohmann_JSON_for_Modern_2022' with the coordinates of vancouver.
```python
{
    url_geojson = 'https://raw.githubusercontent.com/UBC-MDS/exploratory-data-viz/main/data/local-area-boundary.geojson'
    data_geojson_remote = alt.Data(url=url_geojson, format=alt.DataFormat(property='features',type='json'))
    data_geojson_remote
}
```
Then, using the python package altair {cite}'altair' to creae a base map of Vancouver using the coordinates we loaded in. 
```python
{
    vancouver_map = alt.Chart(data_geojson_remote).mark_geoshape(
    color = 'white', opacity= 0.5, stroke='black').encode(
    ).project(type='identity', reflectY=True)

    vancouver_map
}