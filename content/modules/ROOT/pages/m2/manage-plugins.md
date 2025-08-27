
= Manage Plugins

== Plugin Architecture

# Reference: https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html/dynamic_plugins_reference/con-preinstalled-dynamic-plugins
# Explain Pre-installed Dynamic Plugins
# Explain that some must be enabled and configured manually
# Explain that third party plugins can be used, but require packaging. Reference: https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html/installing_and_viewing_plugins_in_red_hat_developer_hub/assembly-third-party-plugins#proc-export-third-party-plugins-rhdh_assembly-third-party-plugins

== Create a Dynamic Plugins Configuration

# Explain how to enable dynamic plugins with the operator-based deployment of Developer Hub. Reference: https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html/installing_and_viewing_plugins_in_red_hat_developer_hub/rhdh-installing-rhdh-plugins_title-plugins-rhdh-about#proc-config-dynamic-plugins-rhdh-operator_rhdh-installing-rhdh-plugins
# Instruct lab reader to visit $BACKSTAGE_HOST/api/dynamic-plugins-info/loaded-plugins to see loaded plugins, and also how to view them using the Developer Hub Administrator > Extensions UI

== Enable and Configure the Keycloak Plugin

# Update the dynamic plugins config map to enable Keycloak plugin(s)
# Explain that this will import User and Group Entities into the Catalog
# Create a secret to hold the Keycloak realm, client id, and client secret values
# Update catalog providers and necesary integrations to enable keycloak Sync
# Instruct lab reader to login and see new User and Group entities in catalog
# Instruct lab reader to check Backstage pod logs syncing keycloak users


== Enable and Configure the GitLab Plugin

# Update the dynamic plugins config map to enable integration with GitLab
# Create a secret to store GitLab credentials client id and secret
# Add GitLab catalog provider and integrations in app-config.yaml
# Sync catalog-info.yaml files from a repo in a given GitLab organisation