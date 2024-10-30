### START
Just run docker-compose up --build. However, the project requires a pre-configured database and can’t initialize it on its own. You can start it, but not everything will work as expected.
- u can see how it works here https://supportstation/shipkz


### Unregistered User Authorization Model Description

- Access tokens are issued for each interaction with the server by an unregistered user. For example, when adding an order or clicking the mini-messenger button. The token's lifespan is 2 weeks. Each token creates a new WebUsers user without a profile and access to the site.
- The app_auth section contains static JavaScript code that adds authorization to the base template.


### Parsers
The parsers run constantly, consuming approximately 1 GB of RAM.
Thought of the Day: They need to be refactored to use Celery and should only activate when truly necessary, for example, when an order is added or a user visits a product page. Additionally, there’s no need for 4 Selenium instances to run simultaneously.
### Thoughts
https://drive.google.com/file/d/1yezIh0CK7UqjQRVVkNU_svJv486CTKAE/view?usp=sharing

