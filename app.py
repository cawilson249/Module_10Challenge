from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base= automap_base()
# reflect the tables
Base.prepare(engine, reflect = True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# home routes
@app.route("/")
def home():
    return(
        f"<center><h2>Welcome to the Hawaii Climate Analysis Local API!<h2></center"
        f"<center><h3>Select from one of the available routes:<h2></center"
        f"<center>/api/v1.0/precipitation</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start/end</center>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= previousYear).all()
    
    session.close()

    #Dictionary with the date as the key and the precipitation (prcp) as the value
    precipitation = {date: prcp for date, prcp in results}
    # convert to a json 
    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    # Perform a query to retrieve the name of the stations
    results = session.query(Station.station).all()
    session.close()

    stationList = list(np.ravel(results))

    # convert to a json 
    return jsonify(stationList)


@app.route("/api/v1.0/tobs")
def temperatures():
    # return the previous years temps
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # previous year

    #perform query to retrieve temperatures
    results = session.query(Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= previousYear).all()
    
    session.close()

    tempList = list(np.ravel(results))

    # return temperature list
    return jsonify(tempList)
    
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start = None, end=None):

    #selection statement
    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:
        startDate = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*selection).filter(Measurement.date >= startDate).all()

        session.close()

        tempList = list(np.ravel(results))

        # return temperature list
        return jsonify(tempList)
    
    else: 
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*selection).filter(Measurement.date >= startDate).\
            filter(Measurement.date<= endDate).all()

        session.close()

        tempList = list(np.ravel(results))

        # return temperature list
        return jsonify(tempList)

## app launcher 
if __name__ == '__main__':
    app.run(debug=True)
