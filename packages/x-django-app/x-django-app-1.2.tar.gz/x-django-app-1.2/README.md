# x-django-app

Django application for all my custom stuff

## Features:

**Models:**

- *XActivity* to store all user activities in the project\
  CREATE\
  EDIT\
  DELETE\
  RESET\
  DOWNLOAD\
  BACKUP\
  RESTORE\
  EXPORT\
  IMPORT\
  PUBLISH\
  ACCEPT\
  REJECT\
  ENABLE\
  DISABLE\
  ACTIVATE\
  DEACTIVATE


**Views:**

- *XListView* for searching in selected fields

- *XCreateView* to record create activity in *XActivity* model, also add *created_by* for the requested user

- *XUpdateView* to record edit activity in *XActivity* model, also add *edited_by* for the requested user

- *x_record_delete_object* function to record delete activity in *XActivity* model\
**NOTE:** *x_record_delete_object* is a function not a view used as\
*x_record_delete_object(request, object, message)*

**Tags:**

- *class_name* return the class name for the object

- *detect_language* return language code to the text

- *get_data* change '' to "" for Jason use

- *to_string* change number to string

- *trunc* trnucate text for any selected length

- *make_clear* replace all ' _ ' to ' '

- *permission_check* check if user has specific permission regardless if user is superuser or not

- *x_sort* sort model data with selected field



## Install:

* Install python > 3.7.3\
recommended python==3.8.2

* Install using pip\
pip install x-django-app

* Add "x_django_app" to your INSTALLED_APPS settings:\
\
  INSTALLED_APPS = [\
      ...\
      'x_django_app',\
  ]


## Use:

* For views\
    from x_django_app.views import XListView, XCreateView, XUpdateView, x_record_delete_object

* For tags\
  {% load x_tags %}

* For paginations\
  {% include 'x_django_app/_pagination.html' %}
