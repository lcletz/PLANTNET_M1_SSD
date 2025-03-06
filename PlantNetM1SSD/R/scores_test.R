library(jsonlite)

mt <- fromJSON('data/merged_truth.json')
# on veut oublier les scores et les labels donnés à ces données
# afin de nous-mêmes les prédire par des fonctions scores

## likelihood scores