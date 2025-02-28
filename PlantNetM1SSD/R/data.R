source('R/fetch_data.R')


subDir <- "data"
mainDir <- getwd()
dir_path <- file.path(mainDir, subDir)
if (!dir.exists(dir_path)) {
  dir.create(dir_path, recursive = TRUE, showWarnings = FALSE)
}


zip_url <- "https://zenodo.org/record/10782465/files/plantnet_swe.zip"
zip_path <- file.path(tempdir(), "plantnet_swe.zip")

download.file(zip_url, zip_path, mode = "wb")


target_files <- c("zenodo/aggregation/ai_answers.json",
                  "zenodo/aggregation/ai_classes.json",
                  "zenodo/aggregation/ai_scores.json",
                  "zenodo/converters/classes.json",
                  "zenodo/converters/tasks.json",
                  "zenodo/answers/ground_truth.txt")

output_files <- file.path(dir_path, basename(target_files))

unique_dirs <- unique(dirname(output_files))
for (dir in unique_dirs) {
  if (!dir.exists(dir)) {
    dir.create(dir, recursive = TRUE, showWarnings = FALSE)
  }
}

unzip(zip_path, files = target_files, exdir = dir_path, junkpaths = TRUE)


for (file in output_files) {
  extract_data(file)
}


#zip_url_300 <- "https://zenodo.org/records/4726653/files/plantnet_300K.zip"
#zip_path_300 <- file.path(tempdir(), "plantnet_300K.zip")

#download.file(zip_url_300, zip_path_300, mode = "wb")

#target_file_300 <- c("plantnet_300K/plantnet300K_metadata.json")

#output_file_300 <- file.path(dir_path, basename(target_file_300))

#extract_limited_lines(output_file_300)

library(httr)
new_zip_url <- "https://lab.plantnet.org/share/external/swe/samples/kswe_20250117_00.tgz"
tgz_file <- "kswe_20250117_00.tgz"
response <- GET(new_zip_url, authenticate("repro", "cessing"))


if (status_code(response) == 200) {
  writeBin(content(response, "raw"), tgz_file)
  untar(tgz_file, exdir = subDir)
  message(sprintf("%s successfully saved!", list.files("samples", recursive = TRUE)))
} else {
  print(paste("Failed to download. HTTP status:", status_code(response)))
}


file.remove(tgz_file)
