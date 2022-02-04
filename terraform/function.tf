resource "google_storage_bucket" "bucket" {
  name     = "salesrecon"
  location = "europe-west1"
  project = "SALESRECON"
}

resource "google_storage_bucket_object" "archive" {
  name   = "coca-cola"
  bucket = google_storage_bucket.bucket.name
  source = "../function/function.zip"
}

resource "google_cloudfunctions_function" "function" {
  project = "salesrecon"
  name        = "coca-cola-function"
  runtime     = "python39"

  available_memory_mb   = 128
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.archive.name
  trigger_http          = true
  entry_point           = "recognize_product"
}
