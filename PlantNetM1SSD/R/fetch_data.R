library(jsonlite)

subDir <- "extracted_data"
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
                  "zenodo/converters/tasks.json")

output_files <- file.path(dir_path, basename(target_files))

unique_dirs <- unique(dirname(output_files))
for (dir in unique_dirs) {
  if (!dir.exists(dir)) {
    dir.create(dir, recursive = TRUE, showWarnings = FALSE)
  }
}

unzip(zip_path, files = target_files, exdir = dir_path, junkpaths = TRUE)

extract_limited_lines <- function(file_path, num_lines = 20000) {
  con <- file(file_path, "r")
  lines <- character(0)

  for (i in seq_len(num_lines)) {
    line <- tryCatch(readLines(con, n = 1, warn = FALSE),
                     error = function(e) return(NULL))

    if (is.null(line) || length(line) == 0) {
      break
    }

    lines <- c(lines, line)
  }

  close(con)

  if (length(lines) > 0) {
    last_line <- trimws(lines[length(lines)])

    last_line <- sub(",$", "", last_line)

    if (!grepl("}$", last_line)) {
      last_line <- paste0(last_line, "}")
    }

    lines[length(lines)] <- last_line

    writeLines(lines, file_path)
    message(sprintf("Successfully saved %d lines in %s!", length(lines), file_path))
  } else {
    message(sprintf("No data found in %s!", file_path))
  }
}

for (file in output_files) {
  extract_limited_lines(file)
}


#zip_url_300 <- "https://zenodo.org/records/4726653/files/plantnet_300K.zip"
#zip_path_300 <- file.path(tempdir(), "plantnet_300K.zip")

#download.file(zip_url_300, zip_path_300, mode = "wb")

#target_file_300 <- c("plantnet_300K/plantnet300K_metadata.json")

#output_file_300 <- file.path(dir_path, basename(target_file_300))

#extract_limited_lines(output_file_300)
