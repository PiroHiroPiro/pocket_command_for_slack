resource "google_pubsub_topic" "pocket_cron_topic" {
  name = "pocket_cron_topic"
  project = "${var.gcp_project}"
}

resource "google_cloud_scheduler_job" "cron_job" {
  name     = "1min_cron_job"
  description = "publish every 1 min"
  schedule = "*/1 * * * *"
  project = "${var.gcp_project}"
  depends_on = ["google_pubsub_topic.pocket_cron_topic"]

  pubsub_target {
    topic_name = "${google_pubsub_topic.pocket_cron_topic.id}"
    data = "${base64encode("test")}"
  }
}