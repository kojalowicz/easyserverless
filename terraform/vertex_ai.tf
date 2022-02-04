resource "google_vertex_ai_dataset" "dataset" {
  display_name          = "${var.DATA}"
  metadata_schema_uri   = "gs://google-cloud-aiplatform/schema/dataset/metadata/image_1.0.0.yaml"
  region                = "us-central1"
}