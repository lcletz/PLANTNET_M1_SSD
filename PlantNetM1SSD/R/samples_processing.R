library(jsonlite)
library(purrr)
library(dplyr)

samples_test <- list.files("data/00", pattern="*.json", full.names=TRUE, recursive = TRUE)
samples_test <- purrr::map(samples_test, function(file) {
  data <- jsonlite::fromJSON(file)
  data$status <- NULL
  return(list(data = data, file = basename(file)))
})

processed_data <- purrr::map(samples_test, function(sample) {
  list(
    file = sample$file,
    name = sample$data$results$name,
    id = sample$data$results$id,
    score = sample$data$results$score
  )
})

write_json(processed_data, "data/samples.json", pretty = TRUE)

unlink("data/00", recursive = TRUE)
