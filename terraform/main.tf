locals {
  common_vars = {
    namespace              = var.namespace
    project_display_name   = var.project_display_name
    project_description    = var.project_description
    db_name                = var.db_name
    db_user                = var.db_user
    db_password            = var.db_password
    github_repo_url        = var.github_repo_url
    github_branch          = var.github_branch
    github_webhook_secret  = var.github_webhook_secret
    generic_webhook_secret = var.generic_webhook_secret
  }
}

resource "kubectl_manifest" "project" {
  count     = var.create_project ? 1 : 0
  yaml_body = templatefile("${path.module}/manifests/project.yaml.tftpl", local.common_vars)
}

resource "kubectl_manifest" "db_secret" {
  yaml_body = templatefile("${path.module}/manifests/postgres-secret.yaml.tftpl", local.common_vars)
}

resource "kubectl_manifest" "webhook_secrets" {
  for_each = {
    github  = templatefile("${path.module}/manifests/webhook-secret-github.yaml.tftpl", local.common_vars)
    generic = templatefile("${path.module}/manifests/webhook-secret-generic.yaml.tftpl", local.common_vars)
  }

  yaml_body = each.value
}

resource "kubectl_manifest" "db_pvc" {
  yaml_body = templatefile("${path.module}/manifests/postgres-pvc.yaml.tftpl", local.common_vars)
}

resource "kubectl_manifest" "media_pvc" {
  yaml_body = templatefile("${path.module}/manifests/media-pvc.yaml.tftpl", local.common_vars)
}

resource "kubectl_manifest" "db_service" {
  yaml_body = templatefile("${path.module}/manifests/postgres-service.yaml.tftpl", local.common_vars)
}

resource "kubectl_manifest" "db_deployment" {
  depends_on       = [kubectl_manifest.db_secret, kubectl_manifest.db_pvc, kubectl_manifest.db_service]
  wait_for_rollout = false
  yaml_body        = templatefile("${path.module}/manifests/postgres-deployment.yaml.tftpl", local.common_vars)
}

resource "kubectl_manifest" "imagestream" {
  yaml_body = templatefile("${path.module}/manifests/imagestream.yaml.tftpl", local.common_vars)
}

resource "kubectl_manifest" "buildconfig" {
  depends_on = [kubectl_manifest.imagestream, kubectl_manifest.webhook_secrets]
  yaml_body  = templatefile("${path.module}/manifests/buildconfig.yaml.tftpl", local.common_vars)
}

resource "kubectl_manifest" "web_service" {
  yaml_body = templatefile("${path.module}/manifests/web-service.yaml.tftpl", local.common_vars)
}

resource "kubectl_manifest" "web_route" {
  depends_on = [kubectl_manifest.web_service]
  yaml_body  = templatefile("${path.module}/manifests/web-route.yaml.tftpl", local.common_vars)
}

resource "kubectl_manifest" "web_deployment" {
  depends_on = [
    kubectl_manifest.db_deployment,
    kubectl_manifest.media_pvc,
    kubectl_manifest.web_service,
    kubectl_manifest.buildconfig
  ]

  wait_for_rollout = false
  yaml_body        = templatefile("${path.module}/manifests/web-deployment.yaml.tftpl", local.common_vars)
}

resource "kubectl_manifest" "hpa" {
  count = var.enable_hpa ? 1 : 0

  depends_on = [kubectl_manifest.web_deployment]
  yaml_body  = templatefile("${path.module}/manifests/hpa.yaml.tftpl", local.common_vars)
}
