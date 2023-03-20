# Climadash
***Exploring Climate Change in Canada: A Dashboard to Raise Awareness and Encourage Reflection***
===

## Introduction
This app aims to raise awareness and promote reflection on the issue of climate change in Canada. Through interactive data visualizations and educational resources, I hope to inspire people to think more deeply about the impact of climate change on our planet and the urgent need to take action to address this global challenge. 

This individual project is based on the group work in collaboration with Vikram Grewal, Xinru Lu, and Mehdi Naji. We are a group students from UBC Master of Data Science program, and our group created another version of the Canadian Climate dashboard. Welcome to check it out [here](https://jlittlefull.shinyapps.io/climadash/).


## Quick Start
📊 [Dashboard Link](https://climadash-ca.onrender.com)

## Project proposal
📊 [Proposal Link](https://github.com/UBC-MDS/climadash/blob/main/report/proposal.md)


## Description

![pic](/data/screenshot.png)

This dashboard aim to show the Canadian climate change over eighty years, using the data collected from 13 Canadian major cities. 

To show the general trend over years, an animated plot is presented. The plot is a scatter map with the location of each city represented by a dot. The colors of the dots correspond to the annual average temperature (in degree Celsius) or percipiation (in mm). The higher the value, the lighter the color. By clicking on the play button, plot will shows the gradual change in temperature (or percipitation, depending on the selection in the radio button), reflected through the change of color. 

To closely examine the trend for the city of interest, two plots are presented.
- Line plot with mean, minimum and maximum of the metric of interest.
- Scatter plot of the annual averages with an estimated regression line showing the general trend of climate change.

For both of the plots described above, the user could select the city of interest, and the range of years that they want to closely examine.

Tooltip will show the detailed data when hovering over the plots. 


## License

`climadash_py` was created by Kelly Wu.
It is licensed under the terms of the MIT license.

## Contribute

If you are interested in contibuting to the project, check out the [contributing guidelines](https://github.com/kellywujy/climadash_py/blob/main/CONTRIBUTING.md). 

Please note that this project is released with a [Code of Conduct](https://github.com/kellywujy/climadash_py/blob/main/CONDUCT.md). By contributing to this project, you agree to abide by its terms.

