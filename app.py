#import dependencies
import numpy as np
import sqlalchemy
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#create engine & base
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

#save variables to a table
Measurement = Base.classes.measurement
Station = Base.classes.station

#create session link from python
session = Session(engine)

#flask setup
app = Flask(__name__)

#create Flask routes
@app.route("/")
def welcome():
    """List of Available API Routes"""
    return (
        "Hawaiian Weather API:<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "Dates (start and end) must be  called in %Y-%m-%d format<br/>"
        "/api/v1.0/start<br/>"
        "/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    "Precipitation Query."

    # Define time one year ago
    year_ago = dt.datetime.strptime('2016-08-23', '%Y-%m-%d')
    
    # Query for year ago facts
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    # Create dictonary of prcp results
    prcp_dict = {}
    for prcp in results:
        prcp_dict[prcp.date] = prcp.prcp
    
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def station():
    "Station Query."

    # Query all stations from Station
    results = session.query(Station.name).all()
    
    # Create list of station names
    station_list = []
    
    #Add stations to list
    
    for x in results:
        station_list.append(x.name)

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    "Temperature Observations Over Last Year"    
    year_ago = dt.datetime.strptime('2016-08-23', '%Y-%m-%d')
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date>year_ago).\
                order_by(Measurement.date).all()
    tobs_list = []
    for x in tobs_results:
        tobs_list.append(x)
    return jsonify(tobs_list)

@app.route("/api/v1.0/start")
def start():
    def calc_temps_start(start_date):
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    start_date = dt.date('%Y-%m-%d')
    temperature_data = calc_temps_start(start_date)
    return jsonify(temperature_data)


@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):
    "JSON list of minimum temp, avg temp and max temp and the max temperature for start and end dates. If dates out of range return 404 Error."

    # Define year ago
    try: 
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return jsonify({"Error": " %Y-%m-%d date format required"}), 404
    
    if start_date > end_date:
        return jsonify({"Error": "input start date is greater than end date"}), 404
    
    #Query for temperature observations from start date 
    results = session.query(Measurement.tobs).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    tobs_list = []
    for x in results:
        tobs_list.append(x.tobs)
    
    if tobs_list != []:
        result_dict = {
            'TMIN': min(tobs_list),
            'TMAX': max(tobs_list),
            'TAVG': np.mean(tobs_list)
        }

        return jsonify(result_dict)
    
    #If date exceeds max date in data set
    return jsonify({"Error": "input start date exceeds dataset"}), 404

if __name__ == "__main__":
    app.run(debug=True)
