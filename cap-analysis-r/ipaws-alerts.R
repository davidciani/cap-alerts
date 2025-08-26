library(tidyverse)
library(fs)
library(jsonlite)

library(arrow)


DATA_DIR = path("/Volumes/TheTank/datasets/ipaws-alerts")

file_name = path("~/Downloads/IpawsArchivedAlerts.jsonl")

data = jsonlite::read_json(file_name)
arrow_info()


data = read_parquet(path("~/Downloads/IpawsArchivedAlerts?=parquet"))
