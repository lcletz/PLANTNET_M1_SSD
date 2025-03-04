library(jsonlite)
library(dplyr)
library(ggplot2)
library(tibble)
library(knitr)
set.seed(9204)

## Data processing:

# (observation ID + predicted class ID)
ai_answers <- fromJSON("data/ai_answers.json")
ai_answers_df <- data.frame(matrix(unlist(ai_answers), byrow = TRUE), stringsAsFactors = FALSE) |>
  rownames_to_column(var = "obs_id")
colnames(ai_answers_df) <- c("obs_id", "plant_id")

# (name of predicted class + predicted class ID)
ai_classes <- fromJSON("data/ai_classes.json")
ai_classes_df <- do.call(rbind, lapply(ai_classes, as.data.frame)) |>
  rownames_to_column(var = "plant_class")
colnames(ai_classes_df) <- c("plant_class", "plant_id")

# (observation ID + score for #1 predicted class)
ai_scores <- fromJSON("data/ai_scores.json")
ai_scores_df <- data.frame(matrix(unlist(ai_scores), byrow = TRUE), stringsAsFactors = FALSE) |>
  rownames_to_column(var = "obs_id")
colnames(ai_scores_df) <- c("obs_id", "score")

### Univariate analysis

## Counts

plant_counts <- ai_answers_df %>%
  count(ai_answers_df[,2])
colnames(plant_counts) <- c("plant_id","count")
# Note: 17247 species in 'ai_classes' aren't in 'ai_answers'

merged_df <- ai_classes_df %>%
  left_join(plant_counts, by = "plant_id")
merged_df$count[is.na(merged_df$count)] <- 0
# which(merged_df["count"]==0) (test)

sup100_count_plants <- merged_df %>%
  filter(count >= 100)

p0 <- ggplot(sup100_count_plants, aes(x = reorder(plant_class, count), y = count,  fill = plant_class)) +
  geom_bar(stat = 'identity', fill = '#b4a7d5ff') +
  labs(title = "Count (>=100) of Observations Distribution", x = 'Species', y = 'Number of observations') +
  theme_minimal()
plot(p0)

top_plants <- merged_df %>% top_n(10, count)

p1 <- ggplot(top_plants, aes(x = reorder(plant_class, count), y = count, fill = plant_class)) +
  geom_bar(stat = "identity", fill = '#b4a7d5ff') +
  coord_flip() +
  labs(title = "10 Most Observed Species", x = "Species", y = "Number of observations") +
  theme_minimal()
plot(p1)
# top1 : plant_id = 251 - Prunus spinosa L.


bottom_plants <- merged_df %>%
  filter(count == 1) %>%
  select(plant_id, plant_class, count)
# observed at least once (3617 species)

not_observed_plants <- merged_df %>% top_n(-1, count)


### Bivariate Analysis

## #1 Scores
top1_scores <- ai_answers_df %>%
  left_join(ai_scores_df, by = "obs_id")

top1_scores <- top1_scores %>% filter(plant_id == 251) %>% select(-2)
plot(top1_scores[,1], top1_scores[,2], xlab="obs_ID", ylab="score",
     main="Score for each observation of Prunus spinosa L.")
# 251 has been observed 22309 times but the scores obtained are scattered


## Observed-only-once scores

bottom_plants <- ai_answers_df %>%
  inner_join(bottom_plants, by = "plant_id")
bottom_plants <- bottom_plants %>%
  left_join(ai_scores_df, by = "obs_id")

bp_summarise <- bottom_plants %>% summarise(
  mean_score = mean(score, na.rm = TRUE),
  median_score = median(score, na.rm = TRUE),
  min_score = min(score, na.rm = TRUE),
  max_score = max(score, na.rm = TRUE),
  sd_score = sd(score, na.rm = TRUE),
  q25 = quantile(score, 0.25, na.rm = TRUE),
  q75 = quantile(score, 0.75, na.rm = TRUE)
)
kable(bp_summarise, caption='Observed-only-once Species Scores Summary')
# Scores from 0.001 to 0.997 (scattered once again)
# Mean at 0.392, Median at 0.344 (low scores)


## Top 200

top_200_plants <- merged_df %>%
  arrange(desc(count)) %>%
  slice_head(n = 200) %>%
  select(plant_id, plant_class, count)

top_200_plants <- ai_answers_df %>%
  inner_join(top_200_plants, by = "plant_id")

top_200_plants <- top_200_plants %>%
  left_join(ai_scores_df, by = "obs_id")

top_200_df <- top_200_plants %>%
  group_by(plant_class) %>%
  summarise(
    count = first(count),
    max_score = max(score, na.rm = TRUE)
  ) %>%
  arrange(desc(count))


p2 <- ggplot(top_200_df, aes(x = count, y = max_score)) +
  geom_point(size = 3) +
  labs(
    title = "Max Score for 200 Most Observed Plants",
    x = "Count of Observations",
    y = "Max Score"
  ) +
  theme_minimal() +
  theme(legend.position = "none")
plot(p2)


## Top 2000

top_2000_plants <- merged_df %>%
  arrange(desc(count)) %>%
  slice_head(n = 2000) %>%
  select(plant_id, plant_class, count)

top_2000_plants <- ai_answers_df %>%
  inner_join(top_2000_plants, by = "plant_id")

top_2000_plants <- top_2000_plants %>%
  left_join(ai_scores_df, by = "obs_id")

top_2000_df <- top_2000_plants %>%
  group_by(plant_class) %>%
  summarise(
    count = first(count),
    max_score = max(score, na.rm = TRUE)
  ) %>%
  arrange(desc(count))

top_2000_most_observed <- top_2000_df %>%
  filter(count == max(count, na.rm = TRUE))
top_2000_least_observed <- top_2000_df %>%
  filter(count == min(count, na.rm = TRUE))
top_2000_min_score <- top_2000_df %>%
  filter(max_score == min(max_score, na.rm = TRUE))


p3 <- ggplot(top_2000_df, aes(x = count, y = max_score)) +
  geom_point(size = 2) +
  geom_segment(data = top_2000_most_observed,
               aes(x = count, y = max_score - 0.2,
                   xend = count, yend = max_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "red") +
  geom_text(data = top_2000_most_observed,
            aes(x = count - 2000, y = max_score - 0.2, label = plant_class),
            color = "red"
  ) +
  geom_segment(data = top_2000_least_observed,
               aes(x = count + 6000, y = max_score,
                   xend = count, yend = max_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "red") +
  geom_text(data = top_2000_least_observed,
            aes(x = count + 8000, y = max_score + 0.01, label = plant_class),
            color = "red", fontface = "bold"
  ) +
  geom_segment(data = top_2000_min_score,
               aes(x = count + 6000, y = max_score,
                   xend = count, yend = max_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "red") +
  geom_text(data = top_2000_min_score,
            aes(x = count + 9000, y = max_score, label = plant_class),
            color = "red"
  ) +
  labs(
    title = "Max Score for Top 2000 Most Observed Plants",
    x = "Count of Observations",
    y = "Max Score"
  ) +
  theme_minimal() +
  theme(legend.position = "none")
plot(p3)


## random 2000

valid_plants <- ai_answers_df %>%
  semi_join(merged_df, by = "plant_id") %>%
  slice_sample(n = 2000)

rd_2000_plants <- valid_plants %>%
  inner_join(merged_df, by = "plant_id") %>%
  left_join(ai_scores_df, by = "obs_id")

rd_2000_df <- rd_2000_plants %>%
  group_by(plant_class) %>%
  summarise(
    count = first(count),
    max_score = max(score, na.rm = TRUE)
  ) %>%
  arrange(desc(count))

rd_2000_most_observed <- rd_2000_df %>%
  filter(count == max(count, na.rm = TRUE))
rd_2000_least_observed <- rd_2000_df %>%
  filter(count == min(count, na.rm = TRUE))


p4 <- ggplot(rd_2000_df, aes(x = count, y = max_score)) +
  geom_point(size = 2) +
  geom_segment(data = rd_2000_most_observed,
               aes(x = count, y = max_score - 0.2,
                   xend = count, yend = max_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "red") +
  geom_text(data = rd_2000_most_observed,
            aes(x = count - 2000, y = max_score - 0.2, label = plant_class),
            color = "red"
  ) +
  geom_segment(data = rd_2000_least_observed,
               aes(x = count + 6000, y = max_score,
                   xend = count, yend = max_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "red") +
  geom_text(data = rd_2000_least_observed,
            aes(x = count + 9000, y = max_score, label = plant_class),
            color = "red"
  ) +
  labs(
    title = "Max Score for 2000 Random Plants",
    x = "Count of Observations",
    y = "Max Score"
  ) +
  theme_minimal() +
  theme(legend.position = "none")
plot(p4)
