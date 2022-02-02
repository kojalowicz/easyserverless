provider "google" {
  project = "salesrecon"
  region  = "europe-west1"
}

resource "google_storage_bucket" "bucket" {
  name     = "dsrgbshdnjffhmik"
  location = "europe-west1"
  project = "SALESRECON"
}

resource "google_storage_bucket_object" "archive" {
  name   = "awerfawfaer"
  bucket = google_storage_bucket.bucket.name
  source = "../t_function-py/t_function-py.zip"
}

resource "google_cloudfunctions_function" "function" {
  project = "salesrecon"
  name        = "function-test"
  description = "My function"
  runtime     = "python39"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  entry_point           = "recognize_product"
}