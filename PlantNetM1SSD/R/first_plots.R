library(jsonlite)
library(dplyr)
library(ggplot2)
library(tibble)


# Traitement des 18847 lignees de données :
ai_answers <- fromJSON("extracted_data/ai_answers.json")
ai_answers_df <- data.frame(matrix(unlist(ai_answers), byrow=TRUE), stringsAsFactors=FALSE)
ai_answers_df <- rownames_to_column(ai_answers_df, var = "obs_id")
colnames(ai_answers_df) <- c("obs_id","plant_id")
# obs ID + predicted class ID
ai_classes <- fromJSON("extracted_data/ai_classes.json")
ai_classes_df <- do.call(rbind, lapply(ai_classes, as.data.frame))
ai_classes_df <- rownames_to_column(ai_classes_df, var = "plant_class")
colnames(ai_classes_df) <- c('plant_class','plant_id')
# name of predicted class + predicted class ID
ai_scores <- fromJSON("extracted_data/ai_scores.json")
ai_scores_df <- data.frame(matrix(unlist(ai_scores), byrow=TRUE), stringsAsFactors=FALSE)
ai_scores_df <- rownames_to_column(ai_scores_df, var = "obs_id")
colnames(ai_scores_df) <- c('obs_id','score')
# obs ID + score for #1 predicted class


# Compteurs et barplots :

plant_counts <- ai_answers_df %>%
  count(ai_answers_df[,2])
colnames(plant_counts) <- c("plant_id","count")
# Remarque : 14534 classes présentes dans ai_classes ne le sont pas dans ai_answers

merged_df <- ai_classes_df %>%
  left_join(plant_counts, by = "plant_id")
merged_df$count[is.na(merged_df$count)] <- 0
# which(merged_df["count"]==0) (test)


top_plants <- merged_df %>% top_n(10, count)

ggplot(top_plants, aes(x = reorder(plant_class, count), y = count, fill = plant_class)) +
  geom_bar(stat = "identity", fill = '#b4a7d5ff') +
  coord_flip() +
  labs(title = "Top 10 des espèces les plus fréquentes", x = "Espèce", y = "Nombre d'observations") +
  theme_minimal()
# top1 : plant_id = 267

bottom_plants <- merged_df %>%
  filter(count > 0) %>%
  arrange(count) %>%
  slice_head(n = 20) # les 20 plantes les moins observées (observées qu'1 fois dans notre cas)

not_observed_plants <- merged_df %>% top_n(-1, count)


# Scores du Top 1 :
merged_answers_scores <- ai_answers_df %>%
  left_join(ai_scores_df, by = "obs_id")

top1_scores <- merged_answers_scores %>% filter(plant_id == 267) %>% select(-2)
plot(top1_scores[,1], top1_scores[,2], xlab="obs_ID", ylab="score")
# 267 a beau être une plante très souvent observée, les scores sont dispersées
# est-ce dû à la qualité des photos ? des différences au sein d'une même classe ?


# Scores des bottom_plants :

bottom_obs <- ai_answers_df %>%
  inner_join(bottom_plants, by = "plant_id")

bottom_scores <- bottom_obs %>%
  left_join(ai_scores_df, by = "obs_id")

bottom_scores %>% summarise(
  mean_score = mean(score, na.rm = TRUE),
  median_score = median(score, na.rm = TRUE),
  min_score = min(score, na.rm = TRUE),
  max_score = max(score, na.rm = TRUE),
  sd_score = sd(score, na.rm = TRUE),
  q25 = quantile(score, 0.25, na.rm = TRUE),
  q75 = quantile(score, 0.75, na.rm = TRUE)
)
# les scores vont de 0.035 à 0.960, ce qui est à nouveau assez dispersé avec une moyenne à 0.448
# et une médiane à 0.385, alors que ces plantes n'ont été observées qu'1 fois


# Les 200 premières classes :

top_200_plants <- merged_df %>%
  arrange(plant_id) %>%
  slice_head(n = 200) %>%
  select(plant_id, plant_class, count)

top_200_obs <- ai_answers_df %>%
  inner_join(top_200_plants, by = "plant_id")

top_200_scores <- top_200_obs %>%
  left_join(ai_scores_df, by = "obs_id")

top_200_df <- top_200_scores %>%
  group_by(plant_class) %>%
  summarise(
    count = first(count),
    mean_score = mean(score, na.rm = TRUE)
  ) %>%
  arrange(desc(count))


ggplot(top_200_df, aes(x = count, y = mean_score)) +
  geom_point(aes(color = plant_class), size = 3) + # une couleur, une plante
  #geom_smooth(method = "lm", se = FALSE, color = "blue") + # régression linéaire
  labs(
    title = "Mean Score by Count for Top 200 Plants",
    x = "Count of Observations",
    y = "Mean Score"
  ) +
  theme_minimal() +
  theme(legend.position = "none")

# Les 2000 premières classes :

top_2000_plants <- merged_df %>%
  arrange(plant_id) %>%
  slice_head(n = 2000) %>%
  select(plant_id, plant_class, count)

top_2000_obs <- ai_answers_df %>%
  inner_join(top_2000_plants, by = "plant_id")

top_2000_scores <- top_2000_obs %>%
  left_join(ai_scores_df, by = "obs_id")

top_2000_df <- top_2000_scores %>%
  group_by(plant_class) %>%
  summarise(
    count = first(count),
    mean_score = mean(score, na.rm = TRUE)
  ) %>%
  arrange(desc(count))


ggplot(top_2000_df, aes(y = count, x = mean_score)) +
  geom_point(aes(color = plant_class), size = 3) + # une couleur, une plante
  geom_smooth(method = "loess", se = FALSE, color = "blue") +
  labs(
    title = "",
    y = "Nombre d'observations",
    x = "Score moyen"
  ) +
  theme_minimal() +
  theme(legend.position = "none")

