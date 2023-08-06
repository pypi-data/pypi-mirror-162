terraform {
  required_version = ">= 0.13"
  backend "gcs" {
    bucket = "aaa-terraform-state"
    prefix = "APP_NAME"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.24.0"
    }
  }
}

data "terraform_remote_state" "root" {
  backend   = "gcs"
  workspace = "master"
  config = {
    bucket = "aaa-root-state-a7554315"
  }
}

locals {
  root = data.terraform_remote_state.root.outputs
  env  = local.root.environments.web_services[terraform.workspace]
}

provider "google" {
  project = var.env.project.project_id
}
