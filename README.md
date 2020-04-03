# Dash 

Visualization of covid-19 in morocco

[![Website moroccodata.site](https://img.shields.io/website-up-down-green-red/http/moroccodata.site.svg)](https://moroccodata.site) 
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/) 
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/Med-ELOMARI/marocovid19-dashboard)

This Dashboard is an initiative to give better presentation to the data available on the internet .
 
Current Testing url is here : [![Website covidmaroc.herokuapp.com/](https://img.shields.io/website-up-down-green-red/http/covidmaroc.herokuapp.com/.svg)](https://covidmaroc.herokuapp.com/) 

![](assets/images/Screenshot.png)
 
# Structure

![](assets/images/structure.png)

the conf.json for cloud function not included (only read-only.json) 
## Getting Started

### Deploy this app to your account

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Or Run the app locally

First create a virtual environment with conda or venv inside a temp folder, then activate it.

```
virtualenv venv

# Windows
venv\Scripts\activate
# Or Linux
source venv/bin/activate

```

Clone the git repo, then install the requirements with pip

```

pip install -r requirements.txt

```

To run the app
Run the app

```

python index.py

```

## Built With

- [Dash](https://dash.plot.ly/) - Main server and interactive components
- [Plotly Python](https://plot.ly/python/) - Used to create the interactive plots
- Google Cloud Function
- Purely Python 