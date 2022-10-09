variable "token" {
  description = "Optionally say something about this variable"
}
terraform {
    
  required_providers {
    linode = {
      source = "linode/linode"
      token  = $LINODE_TOKEN
    }
  }
}

# Configure the Linode Provider
provider "linode" {
}

provider "local" {}

locals {
  // Decode the Kubeconfig so we can access the individual fields.
  kubeconfig = base64decode(linode_lke_cluster.wp-cluster.kubeconfig)
}

resource "linode_lke_cluster" "wp-cluster" {
  label       = "wp-cluster"
  k8s_version = "1.21"
  region      = "us-west"
  tags        = ["dev"]

  pool {
    type  = "g6-standard-1"
    count = 3
  }
}

resource "local_file" "kubeconfig" {
  content  = local.kubeconfig
  filename = "kubeconfig.yaml"
}