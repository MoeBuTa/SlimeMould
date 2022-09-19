## Setup this project

1. Installing [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
2. Creating conda environment
    - `conda env create -f environment.yml`
3. Activating the environment
    - `conda activate slime`
4. Updating the environment
    - `conda env update --name mtdsimtime --file environment.yml --prune`
6. Still developing.....


## Objective
Centred around a model that you will design, implement, explore and analyse. 

## Assessment
 
The Project Report (30%) must be submitted on LMS by COB on 28.10.22. It consists of 
 - A (maximum) 5-page report (not including figures), which should 
 - Outline the model details and place it in context of existing approaches, 
 - Give a qualitative discussion (including link to any simulations) and quantitative summary of the results. 
 
The Jupyter Notebook (10%) is also to be submitted on LMS by COB on 28.10.22. It should 
 - contain all code used to do the Project.
 
The Project Report and the Jupyter Notebook should be well-integrated and complement each other where appropriate.

## Background

you’ll need to start small and build up your understanding of the system and your model by increasing the complexity. 

Slime mould, Physarum polycephalum, works like this: Single-celled organisms grow when fed, creating a network of nutrient-channeling tubes. Nature and evolution have spent millennia perfecting this living complex system, which, if given enough time, will optimise its network structure to transfer nutrients efficiently throughout the entire organism. This is done in two stages: first forage for food sources by growing outward, then adaptively refine the network and respond to the environment by killing off inefficient branches. 

When slime mould is put to work it can do amazing things like solve mazes, change its structure to account for changes in resources and display something akin to memory. 

Slime mould grows at approximately 1-4cm an hour (if conditions are good and depending on, which source you trust), and will successfully map most problems in a few days. 
 
In 2010 a team of researchers arranged pieces of oatmeal on a petri dish to represent railway stations of Tokyo. 
 - The slime evolved to produce a network that looked a lot like Tokyo’s actual railway network! (Slime mould loves oatmeal and hates salt). 
 - The slime mould doesn’t have any awareness of the overall problem it is trying to solve. 
 - An emergent phenomenon, 
 - micro behaviour creating macro patterns, 
 - feedback loops, 
 - local interaction 
 - as the driver and creator of a superorganisms’ communication network, 
 - and many of the other themes
 
## Tasks:

Your task is to 
 - create a bio-inspired model of the slime in-silico and 
 - simulate its evolution over a ‘city’ of nutrient loaded ‘towns’ 
 - Optimising the resulting network. 
 - The ‘city’ and ‘towns’ in the underlying network you set your slime mould loose on is up to you. 
 

