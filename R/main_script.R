library(jsonlite)
library(dplyr)
library(tidyr)
library(tibble)
library(purrr)

# SKIP IF ALREADY DOWNLOADED
subDir <- "./data"
new_zip_url <- "https://lab.plantnet.org/share/external/swe/"
tar_file <- "kswe_20250117.tar"
response <- GET(new_zip_url, authenticate("repro", "cessing"))

if (status_code(response) == 200) {
  writeBin(content(response, "raw"), tar_file)
  untar(tar_file, exdir = subDir)
  message(sprintf("%s successfully saved!", list.files("kswe_20250117", recursive = TRUE)))
} else {
  print(paste("Failed to download. HTTP status:", status_code(response)))
}

file.remove(paste0('data/', tar_file))
file.remove('data/kswe_20250117/Errors.tgz')

# PROCESS JSON FILES (~4H / ~11Go)
tgz_files <- list.files("data/kswe_20250117", pattern = "\\.tgz$", full.names = TRUE)
tgz_chunks <- split(tgz_files, ceiling(seq_along(tgz_files) / 3))        # Small chunks to save easily as JSON
dir.create("data/chunks", showWarnings = FALSE)

for (i in seq_along(tgz_chunks)) {
  cat("Processing chunk", i, "...\n")
  
  processed_data <- list()
  
  for (tgz_file in tgz_chunks[[i]]) {
    temp_dir <- tempfile()
    dir.create(temp_dir)
    
    untar(tgz_file, exdir = temp_dir)
    
    json_files <- list.files(temp_dir, pattern = "\\.json$", recursive = TRUE, full.names = TRUE)
    
    for (file in json_files) {
      data <- fromJSON(file)
      data$status <- NULL
      ## Tasks x Answers
      tasks <- fromJSON("data/tasks.json") %>% 
        enframe(name = "task_id", value = "obs_SWE") %>% 
        mutate(obs_SWE = as.character(obs_SWE))
      
      answers <- fromJSON("data/majority_answers.json")
      
      result_df <- answers %>%
        left_join(tasks, by = "obs_SWE")
      file_id <- tools::file_path_sans_ext(basename(file))
      
      predictions <- map2(
        data$results$name,
        data$results$id,
        function(name, obs_id) {
          list(
            name = name,
            obs = obs_id,
            proba = data$results$score[which(data$results$id == obs_id)]
          )
        }
      )
      
      processed_data[[file_id]] <- predictions
    }
    
    unlink(temp_dir, recursive = TRUE)
  }
  
  output_file <- sprintf("data/chunks/kswe_%02d.json", i)
  write_json(processed_data, output_file, pretty = TRUE, auto_unbox = TRUE)       # Faster if auto_unbox = FALSE but less fancy
}

unlink("data/kswe_20250117", recursive = TRUE)

## Tasks x Answers
tasks <- fromJSON("data/tasks.json") %>% 
  enframe(name = "task_id", value = "obs_SWE") %>% 
  mutate(obs_SWE = as.character(obs_SWE))

answers <- fromJSON("data/majority_answers.json")

result_df <- answers %>%
  left_join(tasks, by = "obs_SWE")

# ADD ID_SWE
ai_classes <- fromJSON("data/ai_classes.json")
json_files <- list.files("data/chunks", pattern = "^kswe_.*\\.json$", full.names = TRUE)

add_id <- function(file) {
  cat("Processing:", basename(file), "\n")
  
  data <- fromJSON(file)
  data <- map(data, function(x) {
    if (is.data.frame(x)) {
      mutate(x, id_SWE = ai_classes[name])
    } else {
      x
    }
  })
  
  write_json(data, file, pretty = TRUE, auto_unbox = TRUE)
}

walk(json_files, add_id)
