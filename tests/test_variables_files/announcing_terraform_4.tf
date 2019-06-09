# https://www.hashicorp.com/blog/announcing-terraform-0-12#iteration-constructs

locals {
  public_instances_by_az = {
    for i in aws_instance.example : i.availability_zone => i...
    if i.associate_public_ip_address
  }
}

variable "source_image_region" {
  type = string
}

variable "target_image_regions" {
  type = list(string)
}

resource "azurerm_shared_image_version" "ubuntu" {
  name                = "1.0.1"
  gallery_name        = azurerm_shared_image_gallery.image_gallery.name
  image_name          = azurerm_shared_image.image_definition.name
  resource_group_name = azurerm_resource_group.image_gallery.name
  location            = var.source_image_location
  managed_image_id    = data.azurerm_image.ubuntu.id[count.index]

  dynamic "target_region" {
    for_each = var.target_image_regions
    content {
      name                   = target_region.value
      regional_replica_count = 1
    }
  }
}
