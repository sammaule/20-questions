resource google_cloud_run_service  "twenty-questions"{
 name     = "twenty-questions"
 location = "europe-west1"

 template {
   spec {
     containers {
       image = "europe-docker.pkg.dev/venema-cloud-run/twenty-questions/app"
       env {
          name = "API_KEY"
          value_from {
            secret_key_ref {
              name = "candidate-llm-api-key"
              key = "1"
            }
          }
        }
     }
   }
 }
}

data google_iam_policy "run_invoke_all_users" {
 binding {
   role = "roles/run.invoker"
   members = [
     "allUsers",
   ]
 }
}

resource google_cloud_run_service_iam_policy "twenty_questions_all_users" {
 service     = google_cloud_run_service.twenty-questions.name
 location    = google_cloud_run_service.twenty-questions.location
 policy_data = data.google_iam_policy.run_invoke_all_users.policy_data
}