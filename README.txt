This is a sample of code I wrote for the backend of the Playfull application. As it is only a sample, this code does not run as a standalone project, and requires integration with the rest of the Playfull backend project in order to function.

This particular Django app supports the Clan features of the project--it allows users to join and exit groups, to post messages to a shared space within the group, and to participate in competitions against other clans within the same league.

This is a Django app which makes use of the Django Rest Framework (DRF). As such, the model information can be found in models.py and the business logic can be found in views.py and serializers.py. The application also includes regression tests, for ensuring that new changes will not break existing end points.