library(tibble)
library(jsonlite)

ground_truth <- read.table("data/ground_truth.txt")
ground_truth <- rownames_to_column(ground_truth)
ground_truth <- ground_truth[which(ground_truth[,2] != -1),]
colnames(ground_truth) <- c('obs_id', 'plantswe_id')
write_json(ground_truth, "data/ground_truth.json", pretty = TRUE)
file.remove('data/ground_truth.txt')
