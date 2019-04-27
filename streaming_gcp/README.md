# Pick up and post for Pocket Streaming

## requirements
terraform (v0.11.11)

## deploy

### Slack
create new app: `https://api.slack.com/apps`

### Pocket
get consumer_key & `access_token: https://getpocket.com/developer/docs/authentication`

### Terraform Deploy (Cloud Scheduler & Pubsub topic)
Terraform use gcloud default credentials.
You need to configure gcloud cli. (`https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login`)

If you have not used Cloud Scheduler before, please specify CloudScheduler region as `asia-northeast1` in GCP console.


Fill `streaming_gcp/tf-files/vars.tf.example` & execute below command. 
```
$ terraform apply
```

### Cloud Functions
deploy command
```
$ gcloud functions deploy pocket_endpoint --runtime python37 --trigger-topic pocket_cron_topic --env-vars-file env.yaml --region asia-northeast1
```

## Trouble Shoot

### PROJECT does not contain an App Engine application

error contents
```error
* google_cloud_scheduler_job.cron_job: Error creating Job: googleapi: Error 404: The project <YOUR_PROJECT_NAME> does not contain an App Engine application. Please visit https://console.developers.google.com/appengine?project=kaito2 to to add an App Engine application.
```
please specify CloudScheduler region as `asia-northeast1` in GCP console.