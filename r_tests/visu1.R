library(jsonlite)
library(tidyverse)
ai_answers <- fromJSON("/data/aggregation/ai_answers.json")
# obs ID + predicted class ID
ai_classes <- fromJSON("/data/aggregation/ai_classes.json")
# name of predicted class + predicted class ID
ai_scores <- fromJSON("data/aggregation/ai_scores.json")
# obs ID + score for #1 predicted class

names(ai_classes)[which(ai_classes==11425)] # "Sedum moranense Kunth"