output "namespace" {
  description = "OpenShift namespace where resources are created."
  value       = var.namespace
}

output "buildconfig_name" {
  description = "Name of the BuildConfig used by webhook builds."
  value       = "photo-album-django"
}
