library(jsonlite)
library(dplyr)
library(tidyr)
library(stringr)
library(tibble)
library(purrr)
library(data.table)


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


# ADD ID_SWE (~1J / ~13Go)
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


# PROCESS EXPERT ANSWERS
expert <- fread("data/ground_truth.txt", header = FALSE)
expert <- expert[V1 != -1]

tasks <- fromJSON("data/tasks.json", simplifyVector = TRUE)
tasks_dt <- data.table(
  id = names(tasks),
  numero = as.integer(unname(tasks))
)

expert <- expert[tasks_dt, on = .(ligne = numero), nomatch = NULL]

expert_processed <- list()
for (i in 1:nrow(expert)) {
  identifiant <- as.character(expert[i, id])
  valeur_obs <- as.character(expert[i, ligne])
  valeur_id <- as.integer(expert[i, V1])
  expert_processed[[identifiant]] <- list(
    obs_SWE = valeur_obs,
    id_SWE = valeur_id
  )
}

write_json(expert_processed, 'data/true_classes.json', pretty = TRUE, auto_unbox = TRUE)


# PROCESS EXPERT PROBABILITIES
json_files <- list.files("data/chunks", pattern = "^kswe_.*\\.json$", full.names = TRUE)
expert <- fromJSON("data/true_classes.json", simplifyVector = FALSE)
expert_final <- list()

for(json_path in json_files){
  cat("Processing:", basename(json_path), "\n")
  json_data <- fromJSON(json_path, simplifyVector = FALSE)
  expert_processed <- list()
  
  for (id in names(json_data)) {
    if (id %in% names(expert)) {
      expected_value <- expert[[id]]$id_SWE
      obs_SWE_value <- expert[[id]]$obs_SWE
      items <- list()
      
      for (item in json_data[[id]]) {
        item$obs_SWE <- obs_SWE_value
        item$correct <- if (isTRUE(!is.null(expected_value) && 
                                   !is.null(item$id_SWE) && 
                                   item$id_SWE == expected_value)) 1 else 0
        items[[length(items) + 1]] <- item
      }
      expert_processed[[id]] <- items
    }
  }
  expert_final <- c(expert_final, expert_processed)
}
write_json(expert_final, 'data/expert_processed.json', pretty = TRUE, auto_unbox = TRUE)


# PROCESS USER ANSWERS
tasks <- fromJSON("data/tasks.json") %>% 
  enframe(name = "task_id", value = "obs_SWE") %>% 
  mutate(obs_SWE = as.character(obs_SWE))

answers <- fromJSON("data/majority_answers.json")

answers <- answers %>%
  left_join(tasks, by = "obs_SWE")

answers2 <- setNames(
  lapply(split(answers, answers$task_id), function(x) {
    x$task_id <- NULL
    as.list(x)
  }),
  answers$task_id
)

write_json(answers2, 'data/majority_answers_processed.json', pretty = TRUE, auto_unbox = TRUE)


# PROCESS VALID NON-EXPERT ANSWERS
json_files <- list.files("data/chunks", pattern = "^kswe_.*\\.json$", full.names = TRUE)
dir.create("data/processed", showWarnings = FALSE)
answers2 <- fromJSON('data/majority_answers_processed.json', simplifyVector = FALSE)
answers2 <- setNames(answers2, sapply(answers2, function(x) x$task_id))

process_obs <- function(obs, expected_value, task_id) {
  cat("Traitement de l'observation:", task_id, "\n")
  cat("Observation contient", length(obs), "éléments.\n")
  
  obs <- purrr::map(obs, function(item) {
    id_SWE <- item$id_SWE
    
    if (!is.null(id_SWE) && !is.list(id_SWE) && length(id_SWE) == 1) {
      id_SWE_str <- as.character(id_SWE)
      expected_str <- as.character(expected_value)
      
      cat("  Traitement de l'élément avec id_SWE:", id_SWE_str, "\n")
      
      item$correct <- if (!is.na(id_SWE_str) && nzchar(id_SWE_str) && id_SWE_str == expected_str) 1 else 0
    } else {
      item$correct <- 0
    }
    
    return(item)
  })
  
  return(obs)
}

for (json_path in json_files) {
  cat("Processing:", basename(json_path), "\n")
  json_data <- fromJSON(json_path, simplifyVector = FALSE)
  
  json_data <- purrr::imap(json_data, function(obs, task_id) {
    if (task_id %in% names(answers2)) {
      expected_value <- answers2[[task_id]]$id_SWE
      cat("  Valeur attendue pour", task_id, ":", expected_value, "\n")
      return(process_obs(obs, expected_value, task_id))
    } else {
      cat("  Aucune valeur attendue trouvée pour", task_id, "\n")
      return(obs)
    }
  })
  
  output_path <- file.path("data/processed", basename(json_path))
  write_json(json_data, output_path, pretty = TRUE, auto_unbox = TRUE)
}

