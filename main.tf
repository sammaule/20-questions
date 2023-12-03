provider google { 
 project = var.project_id 
}

variable "project_id" {
 type        = string
 description = "The Google Cloud Project ID to use"
}