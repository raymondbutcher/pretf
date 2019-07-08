resource "helm_release" "external_dns" {
  name = "external-dns"

  set {
    name  = "domainFilters"
    value = format("\"[%s]\"", jsonencode(var.domain))
  }

  set {
    name  = "rbac.create"
    value = "true"
  }
}
