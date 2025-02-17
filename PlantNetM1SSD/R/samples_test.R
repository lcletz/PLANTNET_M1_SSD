library(jsonlite)
library(purrr)
library(dplyr)

tasks <- fromJSON("extracted_data/tasks.json")
tasks_df <- data.frame(
  plant_swe_id = sapply(tasks, function(x) x[[1]]),
  stringsAsFactors = FALSE
)
tasks_df <- rownames_to_column(tasks_df, var = "plantnet_id")


samples_test <- list.files("samples/00", pattern="*.json", full.names=TRUE, recursive = TRUE)
samples_test <- purrr::map(samples_test, function(file) {
  data <- jsonlite::fromJSON(file)
  data$status <- NULL
  return(list(data = data, file = basename(file)))
})

processed_data <- purrr::map(samples_test, function(sample) {
  list(
    file = sample$file,
    id = sample$data$results$id,
    score = sample$data$results$score
  )
})

write_json(processed_data, "samples/samples.json", pretty = TRUE)

unlink("samples/00", recursive = TRUE)
