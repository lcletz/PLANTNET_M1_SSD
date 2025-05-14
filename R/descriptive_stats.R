library(jsonlite)
library(dplyr)
library(ggplot2)
library(tibble)
library(knitr)
library(grid)
library(purrr)
library(plotly)
library(htmlwidgets)
set.seed(9204)

#We have set a seed, so that when the datas are chosen randomly, the same ones are always chosen.

## Data processing

#Let's read the JSON files as DataFrames and rename the columns for easier splitting and merging.

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

## Univariate analysis

#17 247 species that appear in *ai_classes.json* don't appear in *ai_answers.json*. After merging these two, we can observe the distribution of observed species.

plant_counts <- ai_answers_df %>%
  count(ai_answers_df[,2])
colnames(plant_counts) <- c("plant_id","count")

merged_df <- ai_classes_df %>%
  left_join(plant_counts, by = "plant_id")
merged_df$count[is.na(merged_df$count)] <- 0
# which(merged_df["count"]==0) (test)

sup100_count_plants <- merged_df %>%
  filter(count >= 100)

p0 <- ggplot(sup100_count_plants, aes(x = reorder(plant_class, count), y = count,  fill = plant_class)) +
  geom_bar(stat = 'identity', fill = '#b4a7d5ff') +
  scale_y_log10() +
  labs(title = "Count (>=100) of Observations Distribution on Logarithmic Scale", x = 'Species', y = 'Number of observations') +
  theme_minimal() +
  theme(axis.text.x = element_blank())

p0_interactive <- ggplotly(p0)
p0_interactive
saveWidget(p0_interactive, "R_plot/interactive_species_plot.html", selfcontained = TRUE)


#Let's zoom on the most observed species:

top_plants <- merged_df %>% top_n(10, count)

p1 <- ggplot(top_plants, aes(x = reorder(plant_class, count), y = count, fill = plant_class)) +
  geom_bar(stat = "identity", fill = '#b4a7d5ff') +
coord_flip() +
  labs(title = "", x = "Espèces", y = "Nombre d'observations") +
  theme_minimal() +
  theme(axis.text = element_text(size = 12),
        axis.title = element_text(size = 16))
plot(p1)

#*Prunus spinosa L.* is the most observed plant, it is a blackthorne shrub/sloe bush. Its ID in the CrowdSWE database is 251.
#Within the 17 247 observed species, 3 617 have only been observed once.

bottom_plants <- merged_df %>%
  filter(count == 1) %>%
  select(plant_id, plant_class, count)
# observed at least once (3617 species)

not_observed_plants <- merged_df %>% top_n(-1, count)

#Barplot:
count_df <- merged_df %>%
  mutate(count_by = cut(
    count,
    breaks = c(-1, 0, 1, 100, 500, 1000, 5000, 10000, Inf),
    labels = c("0", "1", "2–100", "101–500", "501–1000", "1001–5000", "5001–10000", "10000+"),
    right = TRUE
  ))
count_df <- count_df %>%
  count(count_by)

p1bis <- ggplot(count_df, aes(x = count_by, y = n)) +
  geom_bar(stat = "identity", fill = '#b4a') +
  geom_text(
    data = filter(count_df, count_by %in% c("1", "10000+")),
    aes(label = n),
    vjust = -0.5,
    size = 4
  ) +
  labs(title = "", x = "Nombre d'observations", y = "Nombre d'espèces") +
  theme_minimal() +
  theme(axis.text = element_text(size = 12),
        axis.title = element_text(size = 16))
plot(p1bis)

## Bivariate Analysis

### Prunus Spinosa L.

#This plant has been observed 22 309 times but the scores given by the AI are scattered.

top1_scores <- ai_answers_df %>%
  left_join(ai_scores_df, by = "obs_id")

top1_scores <- top1_scores %>% filter(plant_id == 251) %>% select(-2)
plot(top1_scores[,1], top1_scores[,2], xlab="obs_ID", ylab="score",
     main="Score for each observation of Prunus spinosa L.")

### Observed-only-once species

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

#The scores for these species go from 0.001 to 0.997, it's still really scattered. But the mean is at 0.392 and the median at 0.344, we can see these species are more likely to get low scores.

#Clean table for report
special_plant <- bottom_plants %>%
  filter(plant_id == 13150)

other_plants <- bottom_plants %>%
  filter(plant_id != 13150) %>%
  slice_sample(n = 9)

bind_rows(special_plant, other_plants) %>%
  select(plant_id, plant_class) %>%
  gt() %>%
  tab_style(
    style = list(cell_fill(color = "#b4a7d5ff")),
    locations = cells_body()
  ) %>%
  tab_style(
    style = cell_text(weight = "bold"),
    locations = cells_body(columns = c(plant_class))
  )

## 2000 random species

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
  geom_point(size = 2, color='#b4a7d5ff') +
  geom_segment(data = rd_2000_most_observed,
               aes(x = count, y = max_score - 0.2,
                   xend = count, yend = max_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "black") +
  geom_text(data = rd_2000_most_observed,
            aes(x = count - 2000, y = max_score - 0.2, label = plant_class),
            color = "black"
  ) +
  geom_segment(data = rd_2000_least_observed,
               aes(x = count + 6000, y = max_score,
                   xend = count, yend = max_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "black") +
  geom_text(data = rd_2000_least_observed,
            aes(x = count + 9000, y = max_score, label = plant_class),
            color = "black"
  ) +
  labs(
    title = "",
    x = "Nombre d'observations",
    y = "Score Max"
  ) +
  theme_bw() +
  theme(legend.position = "none") +
  theme(axis.text = element_text(size = 10),
        axis.title = element_text(size = 14))
plot(p4)


#Mean?
rd_2000_df <- rd_2000_plants %>%
  group_by(plant_class) %>%
  summarise(
    count = first(count),
    mean_score = mean(score, na.rm = TRUE)
  ) %>%
  arrange(desc(count))

rd_2000_most_observed <- rd_2000_df %>%
  filter(count == max(count, na.rm = TRUE))
rd_2000_least_observed <- rd_2000_df %>%
  filter(count == min(count, na.rm = TRUE))


p4 <- ggplot(rd_2000_df, aes(x = count, y = mean_score)) +
  geom_point(aes(color = "Une espèce"), size = 2, show.legend = TRUE) +
  scale_color_manual(values = c("Une espèce" = "#b4a7d5ff")) +
  geom_segment(data = rd_2000_most_observed,
               aes(x = count, y = mean_score - 0.2,
                   xend = count, yend = mean_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "black") +
  geom_text(data = rd_2000_most_observed,
            aes(x = count - 2000, y = mean_score - 0.2, label = plant_class),
            color = "black") +
  geom_segment(data = rd_2000_least_observed,
               aes(x = count + 6000, y = mean_score,
                   xend = count, yend = mean_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "black") +
  geom_text(data = rd_2000_least_observed,
            aes(x = count + 9000, y = mean_score, label = plant_class),
            color = "black") +
  labs(
    title = "",
    x = "Nombre d'observations",
    y = "Score Moyen",
    color = NULL
  ) +
  theme_bw() +
  theme(
    axis.text = element_text(size = 10),
    axis.title = element_text(size = 14),
    legend.position = "left",
    legend.text = element_text(size = 12)
  )

plot(p4)

## Same previous things but instead of using Top 1 predicted AI answers, we go through a sample of users answers

ai_classes <- fromJSON("data/ai_classes.json")
ai_classes_df <- do.call(rbind, lapply(ai_classes, as.data.frame)) |>
  rownames_to_column(var = "name")
colnames(ai_classes_df) <- c("name", "id_SWE")

answers <- fromJSON("data/samples_user_answers.json")
correct_answers <- imap_dfr(answers, ~ {
  if (is.data.frame(.x) && "correct" %in% names(.x)) {
    df <- .x
  } else {
    df <- tryCatch(as.data.frame(.x), error = function(e) NULL)
  }
  
  if (!is.null(df) && "correct" %in% names(df)) {
    df$task_id <- .y
    df_correct <- filter(df, correct == 1)
    if (nrow(df_correct) > 0) return(df_correct)
  }
  
  NULL
})

plant_counts <- correct_answers %>%
  count(correct_answers[,4])
colnames(plant_counts) <- c("id_SWE","count")

merged_df <- ai_classes_df %>%
  left_join(plant_counts, by = "id_SWE")
merged_df$count[is.na(merged_df$count)] <- 0

#Barplot:
count_df <- merged_df %>%
  mutate(count_by = cut(
    count,
    breaks = c(-1, 0, 1, 20, 50, 100, 150, 200, Inf),
    labels = c("0", "1", "2-20", "21–50", "51–100", "101–150", "151–200", "200+"),
    right = TRUE
  ))
count_df <- count_df %>%
  count(count_by) %>%
  slice(-1)

p1bis <- ggplot(count_df, aes(x = count_by, y = n)) +
  geom_bar(stat = "identity", fill = '#b4a') +
  geom_text(
    data = filter(count_df, count_by %in% c("1", "200+")),
    aes(label = n),
    vjust = -0.5,
    size = 4
  ) +
  labs(title = "", x = "Nombre d'observations", y = "Nombre d'espèces") +
  theme_minimal() +
  theme(axis.text = element_text(size = 12),
        axis.title = element_text(size = 16))
plot(p1bis)


top_plants <- merged_df %>% top_n(10, count)

p1 <- ggplot(top_plants, aes(x = reorder(name, count), y = count, fill = name)) +
  geom_bar(stat = "identity", fill = '#b4a7d5ff') +
  coord_flip() +
  labs(title = "", x = "Espèces", y = "Nombre d'observations") +
  theme_minimal() +
  theme(axis.text = element_text(size = 12),
        axis.title = element_text(size = 16))
plot(p1)

valid_plants <- correct_answers %>%
  semi_join(merged_df, by = "id_SWE")

special_plant <- valid_plants %>%
  filter(name == "Daphne striata Tratt.")

other_plants <- valid_plants %>%
  filter(name != "Daphne striata Tratt.") %>%
  slice_sample(n = 3000)

valid_plants <- bind_rows(special_plant, other_plants)
  
rd_3000_plants <- valid_plants %>%
  inner_join(merged_df, by = "id_SWE") %>% 
  select(-name.y)

rd_3000_df <- rd_3000_plants %>%
  group_by(name.x) %>%
  summarise(
    count = first(count),
    max_score = max(proba, na.rm = TRUE)
  ) %>%
  arrange(desc(count))

rd_3000_most_observed <- rd_3000_df %>%
  filter(count == max(count, na.rm = TRUE))
rd_3000_least_observed <- rd_3000_df %>%
  filter(count == min(count, na.rm = TRUE)) %>%
  filter(name.x == 'Daphne striata Tratt.')


p6 <- ggplot(rd_3000_df, aes(x = count, y = max_score)) +
  geom_point(size = 2, color='#b4a7d5ff') +
  geom_segment(data = rd_3000_most_observed,
               aes(x = count, y = max_score - 0.2,
                   xend = count, yend = max_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "black") +
  geom_text(data = rd_3000_most_observed,
            aes(x = count - 10, y = max_score - 0.23, label = name.x),
            color = "black"
  ) +
  geom_segment(data = rd_3000_least_observed,
               aes(x = count + 35, y = max_score,
                   xend = count, yend = max_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "black") +
  geom_text(data = rd_3000_least_observed,
            aes(x = count + 60, y = max_score, label = name.x),
            color = "black"
  ) +
  labs(
    title = "",
    x = "Nombre d'observations",
    y = "Score Max"
  ) +
  theme_bw() +
  theme(legend.position = "none") +
  theme(axis.text = element_text(size = 10),
        axis.title = element_text(size = 14))
plot(p6)

rd_3000_df <- rd_3000_plants %>%
  group_by(name.x) %>%
  summarise(
    count = first(count),
    mean_score = mean(proba, na.rm = TRUE)
  ) %>%
  arrange(desc(count))

rd_3000_most_observed <- rd_3000_df %>%
  filter(count == max(count, na.rm = TRUE))
rd_3000_least_observed <- rd_3000_df %>%
  filter(count == min(count, na.rm = TRUE)) %>%
  filter(name.x == 'Daphne striata Tratt.')


p4 <- ggplot(rd_3000_df, aes(x = count, y = mean_score)) +
  geom_point(aes(color = "Une espèce"), size = 2, show.legend = TRUE) +
  scale_color_manual(values = c("Une espèce" = "#b4a7d5ff")) +
  geom_segment(data = rd_3000_most_observed,
               aes(x = count, y = mean_score - 0.2,
                   xend = count, yend = mean_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "black") +
  geom_text(data = rd_3000_most_observed,
            aes(x = count - 10, y = mean_score - 0.23, label = name.x),
            color = "black"
  ) +
  geom_segment(data = rd_3000_least_observed,
               aes(x = count + 35, y = mean_score,
                   xend = count, yend = mean_score),
               arrow = arrow(length = unit(0.3, "cm")),
               color = "black") +
  geom_text(data = rd_3000_least_observed,
            aes(x = count + 60, y = mean_score, label = name.x),
            color = "black"
  ) +
  labs(
    title = "",
    x = "Nombre d'observations",
    y = "Score Moyen",
    color = NULL
  ) +
  theme_bw() +
  theme(legend.position = "none") +
  theme(
    axis.text = element_text(size = 10),
    axis.title = element_text(size = 14),
    legend.position = "left",
    legend.text = element_text(size = 12)
  )
plot(p4)

#Clean table for least chosen by users
other_plants <- sample(unique(unlist(valid_plants$name)), size = 9)

other_plants_df <- ai_classes_df %>%
  filter(name %in% other_plants)
colnames(other_plants_df) <- c("plant_class", "plant_id")

special_plant <- special_plant %>% select(name, id_SWE)
colnames(special_plant) <- c("plant_class", "plant_id")

other_plants_df <- other_plants_df[, c("plant_id", "plant_class")]
special_plant <- special_plant[, c("plant_id", "plant_class")]

bind_rows(special_plant, other_plants_df) %>%
  gt() %>%
  tab_style(
    style = list(cell_fill(color = "#b4a7d5ff")),
    locations = cells_body()
  ) %>%
  tab_style(
    style = cell_text(weight = "bold"),
    locations = cells_body(columns = c(plant_class))
  )
