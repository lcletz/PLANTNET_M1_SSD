library(jsonlite)
library(dplyr)
library(purrr)
library(tidyr)

tasks <- fromJSON("data/tasks.json")
tasks_df <- data.frame(
  plant_swe_id = sapply(tasks, function(x) x[[1]]),
  stringsAsFactors = FALSE
)
tasks_df <- rownames_to_column(tasks_df, var = "plantnet_id")

samples <- fromJSON("data/samples.json")
samples$file <- sub("\\.json$", "", samples$file)

samples <- samples %>%
  mutate(
  name = purrr::map(name, function(.x){if (!is.list(.x)) list(.x) else .x}),
  id = purrr::map(id, function(.x){if (!is.list(.x)) list(.x) else .x}),
  score = purrr::map(score, function(.x){if (!is.list(.x)) list(.x) else .x})
  ) %>%
  rowwise() %>%
  mutate(
    min_len = min(length(name), length(id), length(score)),
    name = list(name[1:min_len]),
    id = list(id[1:min_len]),
    score = list(score[1:min_len])
  ) %>%
  ungroup() %>%
  select(-min_len) %>%
  unnest(cols = c(name, id, score))

merged_df <- merge(tasks_df, samples, by.x = 'plantnet_id', by.y = 'file')

merged_df <- merged_df %>%
  nest(.by = c("plantnet_id", "plant_swe_id")) %>%
  mutate(
    name  = map(data, "name"),
    id    = map(data, "id"),
    score = map(data, "score")
  ) %>%
  select(-data)

write_json(merged_df, 'data/merged_samples.json', pretty=TRUE)

test <- anti_join(samples, tasks_df, join_by(file==plantnet_id))
test2 <- anti_join(tasks_df, samples, join_by(plantnet_id==file))

gt <- fromJSON("data/ground_truth.json")
merged_truth <- merge(merged_df, gt, by.x = 'plant_swe_id', by.y = 'plantswe_id')
merged_truth <- merged_truth[!duplicated(merged_truth$plant_swe_id), ]

write_json(merged_truth, 'data/merged_truth.json', pretty=TRUE)
