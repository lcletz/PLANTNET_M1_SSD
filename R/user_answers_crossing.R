library(jsonlite)
library(dplyr)
library(tidyr)
library(tibble)
library(purrr)

## Tasks x Answers
tasks <- fromJSON("data/tasks.json") %>% 
  enframe(name = "task_id", value = "obs_SWE") %>% 
  mutate(obs_SWE = as.character(obs_SWE))

answers <- fromJSON("data/majority_answers.json")

result_df <- answers %>%
  left_join(tasks, by = "obs_SWE")


## Samples_Classes x Tasks_User_Answers
predictions <- fromJSON('data/samples_classes.json', simplifyVector = FALSE)

process_observation <- function(observation, expected_value, obs_id) {
  cat("Traitement de l'observation:", obs_id, "\n")
  cat("Observation contient", length(observation), "éléments.\n")
  
  if (length(observation) == 0) {
    cat("Aucun élément à traiter pour l'observation:", obs_id, "\n")
    return(observation)
  }
  
  else {
    observation <- map(observation, function(item) {
      cat("Traitement de l'élément avec id_SWE:", item$id_SWE, "\n")
      if (!is.null(item$id_SWE) && !is.null(expected_value) && any(item$id_SWE == expected_value)) {
        item$correct <- 1
      } else {
        item$correct <- 0
      }
      return(item)
    })
  }
  return(observation)
}

# test <- sample(predictions,10)
# test2 <- purrr::map2(test, names(test), function(obs, obs_id) {
#   cat("Traitement de l'observation pour task_id:", obs_id, "\n")
#   if (obs_id %in% result_df$task_id) {
#    expected_value <- result_df %>%
#      filter(task_id == obs_id) %>%
#      pull(id_SWE)
#    cat("Valeur attendue pour", obs_id, ":", expected_value, "\n")
#   } else {
#     expected_value <- NULL
#     cat("Aucune valeur attendue trouvée pour", obs_id, "\n")
#   }
#   
#   if (!is.null(expected_value)) {
#     return(process_observation(obs, expected_value, obs_id))
#   } else {
#     return(obs) 
#   }
# })


predictions2 <- purrr::map2(predictions, names(predictions), function(obs, obs_id) {
  cat("Traitement de l'observation pour task_id:", obs_id, "\n")
  if (obs_id %in% result_df$task_id) {
    expected_value <- result_df %>%
      filter(task_id == obs_id) %>%
      pull(id_SWE)
    cat("Valeur attendue pour", obs_id, ":", expected_value, "\n")
  } else {
    expected_value <- NULL
    cat("Aucune valeur attendue trouvée pour", obs_id, "\n")
  }
  
  if (!is.null(expected_value)) {
    return(process_observation(obs, expected_value, obs_id))
  } else {
    return(obs) 
  }
})

write_json(predictions2, "data/samples_user_answers.json", pretty = TRUE, auto_unbox = TRUE)


## Scores
results <- fromJSON('data/samples_user_answers.json')
test <- sample(predictions2,5)

calculate_scores <- function(data) {
  scores <- list()
  
  for (i in names(data)) {
    predictions <- data[[i]]
    cumulative_prob <- 0
    found_correct <- FALSE
    
    for (j in 1:length(predictions)) {
      if (is.na(predictions[[j]]$correct)) {
        next
      }
      if (predictions[[j]]$correct == 1) {
        found_correct <- TRUE
        break
      } else {
        cumulative_prob <- cumulative_prob + predictions[[j]]$proba
      }
    }
    if (found_correct) {
      scores[[i]] <- 1 - cumulative_prob
    } else {
      scores[[i]] <- 0
    }
  }
  return(scores)
}

scores_test <- calculate_scores(test)
scores <- calculate_scores(predictions2)

write_json(scores, 'data/scores_user_answer.json', pretty = TRUE)
