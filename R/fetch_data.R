library(jsonlite)

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


extract_data <- function(file_path){
  lines <- readLines(file_path, warn = FALSE)

  if (length(lines) > 0) {
    writeLines(lines, file_path)
    message(sprintf("%s successfully saved!", file_path))
  } else {
    message(sprintf("No data found in %s!", file_path))
 }
}
