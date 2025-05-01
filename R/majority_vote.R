library(jsonlite)
library(dplyr)


gt <- fromJSON('data/ground_truth.json')

answers <- fromJSON("data/answers.json") %>% 
  enframe(name = "obs_SWE", value = "id_SWE") %>% 
  unnest(cols='id_SWE') %>% 
  mutate(obs_SWE = as.character(obs_SWE), 
         id_SWE = as.numeric(id_SWE))


cl_answers <- answers %>%
  anti_join(gt, by=join_by("obs_SWE"=="obs_id"))


counts <- cl_answers %>%
  count(obs_SWE) %>%
  filter(n > 1)

first_rows <- cl_answers %>%
  filter(obs_SWE %in% counts$obs_SWE) %>%
  group_by(obs_SWE) %>%
  slice(1) %>%
  ungroup()

first_rows <- first_rows[rep(1:nrow(first_rows), each = 2), ]

long_answers <- bind_rows(cl_answers, first_rows)


majority_vote <- long_answers %>%
  group_by(obs_SWE, id_SWE) %>%
  tally(name = "count") %>%
  arrange(obs_SWE, desc(count)) %>%
  slice_head(n = 1) %>% 
  ungroup() %>%
  select(-count)


write_json(majority_vote, 'data/majority_answers.json', pretty = TRUE)
