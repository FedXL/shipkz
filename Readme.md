### Unregistered User Authorization Model Description

The `app_middlewares` implements this mechanism by checking each request for the presence of a token in the header. If the token is not present, the user is registered.

Looks we can have some problems with spammers and indexing bots. We need to implement a mechanism that will allow us to distinguish between registered and unregistered users.