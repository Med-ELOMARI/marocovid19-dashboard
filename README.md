# Dash
Current Demo is here : [url](https://polar-refuge-68443.herokuapp.com/)

![](https://api.apiflash.com/v1/urltoimage?access_key=72d704b7cedd4ee6b2b3bdd377bdfe30&format=png&response_type=image&scale_factor=1&url=https%3A%2F%2Fpolar-refuge-68443.herokuapp.com%2F)
 
# Structure

![](images/structure.png)

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

## About the App

## Built With

- [Dash](https://dash.plot.ly/) - Main server and interactive components
- [Plotly Python](https://plot.ly/python/) - Used to create the interactive plots
- Google Cloud Function
- Purely Python 