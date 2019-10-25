provider "google" {
  //project     = "kaito2"
  project     = "${var.gcp_project}"
  region      = "asia-northeast1"
}