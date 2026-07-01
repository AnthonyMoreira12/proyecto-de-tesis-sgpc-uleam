terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-sgpc-fcvt-prod"
  location = "East US" # Puedes cambiarlo a la región más cercana
}

# 1. Base de Datos Administrada (PostgreSQL Flexible Server)
resource "azurerm_postgresql_flexible_server" "db" {
  name                   = "psql-sgpc-prod"
  resource_group_name    = azurerm_resource_group.rg.name
  location               = azurerm_resource_group.rg.location
  version                = "14"
  administrator_login    = "sgpcadmin"
  administrator_password = "PasswordSeguro123!" # En prod real, esto se inyecta por CI/CD
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
}

# 2. Almacenamiento Blob para archivos PDF
resource "azurerm_storage_account" "storage" {
  name                     = "stsgpcfcvtprod"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "pdfs" {
  name                  = "publicaciones-pdf"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}

# 3. Servicio de Aplicación (App Service Linux)
resource "azurerm_service_plan" "app_plan" {
  name                = "plan-sgpc-prod"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "app" {
  name                = "app-sgpc-backend-prod"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.app_plan.id

  site_config {
    always_on = false
    application_stack {
      python_version = "3.12"
    }
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    "DJANGO_SETTINGS_MODULE"              = "BACKEND_SGPC_FCVT.settings"
    "ENABLE_TELEMETRY"                    = "True"
  }
}