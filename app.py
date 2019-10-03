from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc, asc
import pandas as pd
import datetime as dt
from datetime import datetime, date, timedelta

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
    """ List all routes that are possible """
    return (
        f"Welcome to Hawaii Weather Data!<br/>"
        f"Available Routes:<br/>"
        f"<a href = /api/v1.0/precipitation>Precipitation</a><br/>"
        f"<a href = /api/v1.0/stations>Stations</a><br/>"
        f"<a href = /api/v1.0/tobs>Temperature Observations</a><br/>"
        f"add your start date to the end of this route: /api/v1.0/<br/>"
        f"add your start and ending dates to the end of this route, separated by a forward slash: /api/v1.0/<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    """ Query results of date/prcp converted to dictionary and returned in JSON form"""
   
    one_year_earlier = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    df = pd.DataFrame(session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_earlier).\
    order_by(Measurement.date).all())
    precip_dictionary = df.to_dict()
    return jsonify(precip_dictionary)

@app.route("/api/v1.0/stations")
def stations():
    
    """ JSON list of stations"""
    
    station_names = session.query(Station.station).all()
    return jsonify(station_names)


@app.route("/api/v1.0/tobs")
def tobs():

    """ Query for the dates and temperature observations from last 12 months. Return JSON list of Temperature Observations"""

    temperatures = session.query(Measurement.station, 
                         func.min(Measurement.tobs), 
                         func.max(Measurement.tobs),
                         func.avg(Measurement.tobs))\
                .group_by(Measurement.station)\
                .order_by(func.count(Measurement.station).desc())\
                .all()
    return jsonify(temperatures)


@app.route("/api/v1.0/<start>")
def start():
    """ Return a JSON list of TMIN, TAVG, and TMAX temp for all dates greater than or equal to the start date """
    def calc_temps(start_date):
        temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter( Measurement.date <= '2017-08-23').all()
        tmin = temps[0][0]
        tavg = round(temps[0][1],2)
        tmax = temps[0][2]
        return tmin, tavg, tmax
    temp = calc_temps(start_date)
    return jsonify(temp)

    
@app.route("/api/v1.0/<start>/<end>")
def start_end():
    """ Return a JSON list of TMIN, TAVG, and TMAX temp for all dates between start and end dates, inclusive."""
    
    
    def calc_temps(start_date, end_date):
            temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
            tmin = temps[0][0]
            tavg = round(temps[0][1],2)
            tmax = temps[0][2]
            return tmin, tavg, tmax
    temp = calc_temps(start_date, end_date)
    return jsonify(temp)

    


if __name__ == "__main__":
    app.run(debug=True)