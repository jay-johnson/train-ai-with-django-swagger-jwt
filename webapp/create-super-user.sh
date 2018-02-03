#!/bin/bash

email="root@email.com"
username="root"
password="123321"

echo "Creating Super User"
echo "from django.contrib.auth import get_user_model; from django.contrib.auth.models import User; User = get_user_model(); User.objects.filter(email='${email}').delete(); User.objects.create_superuser('${username}', '${email}', '${password}')" | python manage.py shell
echo "Done Creating Super User: ${username}"

exit 0
