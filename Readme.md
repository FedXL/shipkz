### Unregistered User Authorization Model Description

- Access tokens are issued for each interaction with the server by an unregistered user. For example, when adding an order or clicking the mini-messenger button. The token's lifespan is 2 weeks. Each token creates a new WebUsers user without a profile and access to the site.
- The app_auth section contains static JavaScript code that adds authorization to the base template.