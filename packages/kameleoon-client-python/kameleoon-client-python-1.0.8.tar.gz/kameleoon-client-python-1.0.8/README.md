# Kameleoon Python SDK

## Getting Started

Our SDK gives you the possibility of running experiments and activating feature flags on your Python platform. Integrating our SDK into your applications is easy, and its footprint (in terms of memory and network usage) is low.

## Learn more

You can refer to the [SDK reference](https://developers.kameleoon.com/python-sdk.html#reference) to check out all possible features of the SDK. Also make sure you check out our [Getting started tutorial](https://developers.kameleoon.com/python-sdk.html#getting-started) which we have prepared to walk you through the installation and implementation.


#### Additional configuration

You should provide credentials for the Kameleoon SDK via a configuration file, 
which can also be used to customize the SDK behavior. A sample configuration 
file can be obtained here. We suggest to install this file to the default path of 
`/etc/kameleoon/client-python.yaml`, but you can also put it in another location and 
passing the path as an argument to the KameleoonClient class. 
With the current version of the Python SDK, those are the available keys:

* `client_id: String`:  a client_id is required for authentication to the Kameleoon service.
* `client_secret: String`: a client_secret is required for authentication to the Kameleoon service.
* `actions_configuration_refresh_interval: int`: this specifies the refresh interval, in minutes, 
  of the configuration for experiments and feature flags (the active experiments and feature
  flags are fetched from the Kameleoon servers). It means that once you launch an experiment,
  pause it, or stop it the changes can take (at most) the duration of this interval to be 
  propagated in production to your servers. If not specified, the default interval 
  is 60 minutes.
* `visitor_data_maximum_size: int`: this specifies the maximum amount of memory that the hash 
  holding all the visitor data (in particular custom data) can take (in MB). 
  If not specified, the default size is 500MB.


### Initializing the Kameleoon client

After installing the SDK into your application, 
configuring the correct credentials (in /etc/kameleoon/client.yaml) and setting 
up a server-side experiment on Kameleoon's back-office, 
the next step is to create the Kameleoon client in your application code.

The code below gives a clear example. 
A KameleoonClient is a singleton object that acts as a bridge 
between your application and the Kameleoon platform. 
It includes all the methods and properties you will need to run an experiment.

```python 
from kameleoon import KameleoonClient

SITE_CODE = 'a8st4f59bj'

kameleoon_client = KameleoonClient(SITE_CODE)

kameleoon_client = KameleoonClient(SITE_CODE, blocking=False, configuration_path='/etc/kameleoon/client.yaml')

kameleoon_client = KameleoonClient(SITE_CODE, blocking=True)

kameleoon_client = KameleoonClient(SITE_CODE, blocking=True, logger=MyLogger)
```

### Triggering an experiment

Running an A/B experiment on your Python application means bucketing your visitors 
into several groups (one per variation). The SDK takes care of this bucketing (and the associated reporting) 
automatically.

Triggering an experiment by calling the trigger_experiment() method will register a 
random variation for a given visitor_code. If this visitor_code is already associated with a 
variation (most likely a returning visitor that has already been exposed to the experiment previously), 
then it will return the previous variation assigned for the given experiment.

```python
visitor_code = kameleoon_client.obtain_visitor_code(request.COOKIES)
variation_id = 0
try:
    variation_id = kameleoon_client.trigger_experiment(visitor_code, 135471)
except NotActivated as ex:
    # The user triggered the experiment, but did not activate it. 
    # Usually, this happens because the user has been associated 
    # with excluded traffic
    variation_id = 0
    client.logger.error(ex)
except NotTargeted as ex:
    # The user did not trigger the experiment, as the associated 
    # targeting segment conditions were not fulfilled. 
    # He should see the reference variation
    variation_id = 0
    client.logger.error(ex)
except ExperimentConfigurationNotFound as ex:
    # The user will not be counted into the experiment, 
    # but should see the reference variation
    variation_id = 0
    client.logger.error(ex)

recommended_products_number = 5
# This is the default / reference number of products to display

if variation_id == 148382:
    # We are changing number of recommended products for this variation to 10
    recommended_products_number = 10
elif variation_id == 187791:
    # We are changing number of recommended products for this variation to 8
    recommended_products_number = 8

# Here you should have code to generate the HTML page back to the client, 
# where recommendedProductsNumber will be used
response = JsonResponse({...})
```

### How to use Kameleoon SDK with Django
#### You can view an example project in the folder:
`tests/integration/proj`

The SDK uses a separate thread to exchange data with the Kameleoon servers.   
If you use Django, we recommend you to initialize the Kameleoon client at server start-up, 
in the file apps.py your django app.

When you use `python manage.py runserver` Django start two processes, 
one for the actual development server and other to reload your application 
when the code change.

You can also start the server without the reload option, and you will 
see only one process running will only be executed once :

`python manage.py runserver --noreload`

You can also just check the RUN_MAIN env var in the ready() method itself.

```python 
def ready(self):
    if os.environ.get('RUN_MAIN', None) == 'true':
        configuration_path = os.path.join(ROOT_DIR, 'path_to_config', 'config.yml')
        self.kameleoon_client = KameleoonClient(SITE_CODE, configuration_path=configuration_path)
```

This only applies to local development when you use `python manage.py runserver`.
In a production environment, the code in the `ready()` function will be executed only one time when 
the application is initialized

#### Wrap the wsgi application in middleware class.

KameleoonWSGIMiddleware extracts and sets the Kameleoon visitor code cookie.
KameleoonWSGIMiddleware is a WSGI middleware which operates by wrapping the wsgi application instance. 
The following example shows a sample django application wrapped by the KameleoonWSGIMiddleware middleware class:
```python
import uuid

from django.core.wsgi import get_wsgi_application

from kameleoon import KameleoonWSGIMiddleware
application = KameleoonWSGIMiddleware(get_wsgi_application(), 'example.com', uuid.uuid4().hex)
```

You can then access the Kameleoon client in your views:

```python 
from django.apps import apps

kameleoon_app = apps.get_app_config('your_app')
client = kameleoon_app.kameleoon_client
```

 Obtaining a Kameleoon visitor_code for the current HTTP request is an important 
 step of the process. 
 You should use the provided `obtain_visitor_code()`

```python
from django.apps import apps
from django.http import JsonResponse

from kameleoon.exceptions import NotActivated, NotTargeted, ExperimentConfigurationNotFound

kameleoon_app = apps.get_app_config('your_app')
client = kameleoon_app.kameleoon_client

def view(request):
    visitor_code = client.obtain_visitor_code(request.COOKIES)
    variation_id = 0
    try:
        variation_id = client.trigger_experiment(visitor_code, 135471)
    except NotActivated as ex:
        # The user triggered the experiment, but did not activate it. 
        # Usually, this happens because the user has been associated 
        # with excluded traffic
        variation_id = 0
        client.logger.error(ex)
    except NotTargeted as ex:
        # The user did not trigger the experiment, as the associated 
        # targeting segment conditions were not fulfilled. 
        # He should see the reference variation
        variation_id = 0
        client.logger.error(ex)
    except ExperimentConfigurationNotFound as ex:
        # The user will not be counted into the experiment, 
        # but should see the reference variation
        variation_id = 0
        client.logger.error(ex)
    
    recommended_products_number = 5
    # This is the default / reference number of products to display

    if variation_id == 148382:
        # We are changing number of recommended products for this variation to 10
        recommended_products_number = 10
    elif variation_id == 187791:
        # We are changing number of recommended products for this variation to 8
        recommended_products_number = 8
        
    # Here you should have code to generate the HTML page back to the client, 
    # where recommendedProductsNumber will be used
    response = JsonResponse({...})
    # set a cookie
    response.set_cookie(**kameleoon_cookie)

    return response
```

#### Tracking conversion

After you are done triggering an experiment, the next step is usually to start tracking 
conversions. This is done to measure performance characteristics according 
to the goals that make sense for your business.

For this purpose, use the `track_conversion()` method of the SDK as shown in the example. 
You need to pass the visitor_code and goal_id parameters so we can correctly
track conversions for this particular visitor.

```python
visitor_code = client.obtain_visitor_code(request.COOKIES)
goal_id = 83023
client.track_conversion(visitor_code, goal_id )
```


