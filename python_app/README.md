# Python app

## Usage

This folder contains a relatively small, easy to use graphical interface that plots the data received from the IN100.

The web app is based on the "Manufacturing SPC Dashboard" sample app from [Plotly](https//plot.ly/).

## Modifying the code 

A few functions can be modified easily to adapt the code for various types of data. 

The `IN100_ble.py` file contains all the code handling reading the data sent by the device, and writing it to a file. 

The `IN100_writePayloadToCSV` function can be modified, as it is responsible for the formatting of the data. The lines 
where it can be modified are shown by comments. 

Important : if the number of columns is modified, the `build_top_panel(stop_interval)` function in `app.py` (again, follow the instructions in the comments) 

## License 

The sample app is under MIT license, see the [LICENSE](./template_info/LICENSE) file. This modified version is under the same license, which you can read [here](../LICENSE)

## Requirements
We suggest you to create a separate virtual environment running Python 3 for this app, and install all of the required dependencies there. Run in Terminal/Command Prompt:

```
python3 -m virtualenv venv
```
In UNIX system: 

```
source venv/bin/activate
```
In Windows: 

```
venv\Scripts\activate
```

To install all of the required packages to this environment, simply run :

```
pip install -r requirements.txt
```

and all of the required `pip` packages will be installed, and the app will be able to run.


## How to use this app

Run this app locally by:
```
python app.py
```
Open http://0.0.0.0:8050/ in your browser, you will see a live-updating dashboard.

## Resources and references

* [Dash User Guide](https://dash.plot.ly/)

## Known bugs (as of 2025-03-07)

- The sparkline graphs do not update automatically
