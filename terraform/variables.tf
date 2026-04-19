variable "namespace" {
  description = "OpenShift project (namespace) name."
  type        = string
  default     = "photo-album-pibk75"
}

variable "project_display_name" {
  description = "Display name for the OpenShift Project."
  type        = string
  default     = "Photo Album"
}

variable "project_description" {
  description = "Description for the OpenShift Project."
  type        = string
  default     = "Photo Album Django application"
}

variable "create_project" {
  description = "Create/OpenShift Project via Terraform when true. Keep false if project already exists."
  type        = bool
  default     = false
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig used by Terraform."
  type        = string
  default     = "~/.kube/config"
}

variable "db_name" {
  description = "PostgreSQL database name."
  type        = string
  default     = "photo-album-pibk75"
}

variable "db_user" {
  description = "PostgreSQL username."
  type        = string
  default     = "photo-album-pibk75"
}

variable "db_password" {
  description = "PostgreSQL password."
  type        = string
  sensitive   = true
}

variable "github_repo_url" {
  description = "GitHub repository URL used by OpenShift BuildConfig."
  type        = string
  default     = "https://github.com/nGergo0/photo-album-django"
}

variable "github_branch" {
  description = "Git branch used by OpenShift BuildConfig."
  type        = string
  default     = "main"
}

variable "github_webhook_secret" {
  description = "Webhook secret used by the BuildConfig GitHub trigger."
  type        = string
  sensitive   = true
}

variable "generic_webhook_secret" {
  description = "Webhook secret used by the BuildConfig Generic trigger."
  type        = string
  sensitive   = true
}

variable "enable_hpa" {
  description = "Create HorizontalPodAutoscaler resource when true."
  type        = bool
  default     = true
}
