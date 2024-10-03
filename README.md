# Expert_Detection


## Scripts
Within the src file of the repo is the various python scripts used in order to produce the rankings utilized in the paper. All the python files need to be edited to include paths to the Stack Exchange datasets you wish to use, what output names you want for each file, along with altering which Tag you wish to get rankings for. The sheaf graph and hypergraph python files take up a lot of memory due to how the eigenvalues are computed, meaning that doing it on larger stack-exchange datasets may not be feasible. The Stack Exchange Datasets are avaliable for download here https://archive.org/download/stackexchange.

## Results
The results for the experiments mentioned in the paper are included in the results/Results folder, with each experiments results being in a logical folder and filename.