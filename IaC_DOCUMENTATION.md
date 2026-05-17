# 4. Házi – Infrastructure as Code (Terraform)

A Photo Album OpenShift infrastruktúráját a `terraform/` mappában lévő kód definiálja. Push után a GitHub Actions lefuttatja a `terraform plan` / `apply` lépéseket.

## Terraform a következő erőforrásokat telepíti OpenShift-be:

- **PostgreSQL**: secret, PVC, service, deployment
- **Photo-Album-App**: deployment, PVC, service, route
- **Build**: ImageStream, BuildConfig (GitHub + generic webhook)
- **Skálázás** (opcionális): HPA – `enable_hpa = true` esetén

A manifest sablonok: `terraform/manifests/*.yaml.tftpl`.
Namespace: `photo-album-pibk75`.

## GitHub Actions

A Terraform muodul telepítését GitHub Actions végzi.
Workflow: `.github/workflows/deploy-terraform.yml`

**Trigger** (push `main`-re), ha változik: `terraform/`, `Dockerfile`, `webapp/`, a workflow fájl.

**Kötelező repository secret-ek** (Settings → Secrets and variables → Actions):

| Secret | Leírás |
|--------|----------------|
| `KUBECONFIG_CONTENT` | base64 kubeconfig |
| `DB_PASSWORD` | PostgreSQL jelszó |
| `WEBHOOK_SECRET_GITHUB` | BuildConfig GitHub webhook |
| `WEBHOOK_SECRET_GENERIC` | BuildConfig generic webhook |

A Kubeconfig token időnként lejárhat, oylankor azt friisíeni szükséges a respository secretek között.

## App frissítése

Két workflow:

1. **OpenShift build** – push → BuildConfig webhook → új image → deployment rollout (ez a kezdetektől megvolt).
2. **Terraform** – infrastruktúra / manifest változás → GitHub Actions -> terraform apply.
