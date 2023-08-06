
# SCF_FSM_PACKAGE

A resuable django application that can handle transition and workflow's in your project .


## Authors

- [@anandrajB](https://github.com/anandrajB)
- [@Mohamed-Sheik-Ali](https://github.com/Mohamed-Sheik-Ali)


## Installation

Install scf_fsm_package with pip

```bash
pip install finflo
```

1. In your django application , browse to installed_apps section in settings.py and add finflo 
2. make sure you have installed [DjangoRestFramework](https://www.django-rest-framework.org/#installation)

```bash
INSTALLED_APPS = [
    'finflo',
    'rest_framework'
]
```
if you want party you can customize by adding this finflo section in your settings.py 

1. from_party and to_party is required to mention the flow is needed to sent from one party to another party
2. The MODEL is optional field the user can specify their transition_model in their application

**NOTE** : The FINFLO section is required 
```bash
FINFLO = {
    'FROM_PARTY' : 'django_app.model_name', # example

    'FROM_PARTY' : 'accounts.party',
    'TO_PARTY' : 'accounts.party'

    'WORK_MODEL' : ['django_app.model_name' , 'django_app.model_name'] # example
    'WORK_MODEL' : ['MyApp.Programs' , 'MyApp.Invoices']
}
```

or else simple mention None , 

```bash
FINFLO = {
    'FROM_PARTY' : None,
    'TO_PARTY' : None,
    'WORK_MODEL' : None
}
```

now navigate to the middleware section and add the finflo middleware


```
MIDDLEWARE = [
    'finflo.middleware.TransitionUserMiddleware',
]
```

## Api urls 

In your application's urls.py , you can include finflo's api urls for browsable api's 

** make sure that you have installed [DjangoRestFramework](https://www.django-rest-framework.org/#installation)


Now add this peice of code in your urls.py

```
urlpatterns = [
    path('', include('finflo.urls'))
]
```

## Usage


1. import your transition function 

    ```bash
    from finflo.transitions import FinFlotransition
    ```

2. The transition function requires 4 positional arguments :

3.  |  Arguments   | Data_Type  |
    | ------------- | ------------- |
    | type   | str  |
    | action  | str  |
    | stage  | int  |
    | t_id (optional) | int  | 




## Example 1 : generic

```python
from finflo.transition import FinFlotransition

myhandler = FinFlotransition()

# example function

def index():
    myhandler.transition(type = "PROGRAM",action = "submit" ,stage = 0)
    return HttpResponse({"data"})

```
## Example 2 : customizable

1. Browse to /api/transition/ 
2. send your type , action , stage , t_id(optional) in body \
![Screenshot](image1.JPG)

## Tech Stack

    1. Python
    2. Django==3.2.5
    3. Django-rest-framework


## Additional API's 

#### Api urls 


| Api URL's  | METHOD | QUERY_PARAMS |
| ------------- | ------------- | ------------- |
| *localhost/model/* | GET  | ?type=PROGRAM |
| *localhost/*action*/* | GET | NONE |
| *localhost/*action*/* | POST | NONE |
| *localhost/*workflowitems*/* | GET | NONE |
| *localhost/workevents/* | GET | NONE |




## Support

For support, email support@venzo.com .


## Future
    
1. postgres support
2. next_Avail_transitions
3. customizable workflowitems and workflowevents

