# Expert Detection
This repository contains the source code for the paper **Expert Detection on Crowdsourcing Forums via Sheaf Laplacian**.

## Network
The edge and hypergraph edgelist for all four datasets we used are avaliable in the network_info folder, along with the official reputation score by Stack Exchange for the users. 

## Scripts
Inside the `src` directory, you'll find the Python scripts used to generate the rankings referenced in the paper. To run these scripts, you'll need to adjust the paths to the Stack Exchange datasets you want to analyze, specify the desired output file names, and set the target tags for ranking generation. Note that the sheaf graph and hypergraph scripts can be memory-intensive due to the eigenvalue computations, which may limit their feasibility on larger Stack Exchange datasets. You can download the datasets from [Stack Exchange on Archive.org](https://archive.org/download/stackexchange).

### Hypergraph vs Graph
The hypergraph scripts require manual adjustments for each tag, whereas the graph scripts are tailored to individual Stack Exchange communities and their respective tags.

## Results
The experimental results referenced in the paper are located in the `results/Results` folder, with each experiment’s output stored in logically named folders and files for easy navigation.
