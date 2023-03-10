# Import Dependencies 
import numpy as np
import pandas as pd
import datetime as dt
import json
import os


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#create engine

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#Set Up flask 

from flask import Flask, jsonify

app = Flask(__name__)

# Flask Routes 


@app.route('/')

def Home():
   return (
        f"List of Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"To find avg temp, max temp, and min temp from a given start date:<br/>"
        f"/api/v1.0/<start><br/>"
        f"<br/>"
        f"To find avg temp, max temp, and min temp from a given start date to end date range:<br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )



#Convert the query results to a dictionary using date as the key and prcp as the value. Return the JSON representation of your dictionary.
@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    prcp_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > one_year_ago).\
    order_by(Measurement.date).all()
  
    session.close()
    return jsonify(prcp_data)




#Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    locations = session.query(Measurement).group_by(Measurement.station).count()
    active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
            group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()
    stations = dict(active_stations)

    session.close()
    return jsonify(stations)



#Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_temp = session.query(Measurement.tobs).\
        filter(Measurement.date >= one_year_ago, Measurement.station == 'USC00519281').\
         order_by(Measurement.tobs).all()

    yr_temp = []
    for y_t in year_temp:
        yrtemp = {}
        yrtemp["tobs"] = y_t.tobs
        yr_temp.append(yrtemp)

    session.close()
    return jsonify(yr_temp)



#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
def calc_start_temps(start_date):
    session = Session(engine)
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                         filter(Measurement.date >= start_date).all()
    session.close()


@app.route("/api/v1.0/<start>")
def startday(start):
    session = Session(engine)
    calc_s_temp = calc_start_temps(start)
    s_temp= list(np.ravel(calc_s_temp))

    t_min = s_temp[0]
    t_max = s_temp[2]
    t_avg = s_temp[1]
    t_dict = {'Minimum temperature': t_min, 'Maximum temperature': t_max, 'Avg temperature': t_avg}

    session.close()
    return jsonify(t_dict)



def calc_temps(start_date, end_date):
    session = Session(engine)
    return session.query(func.min(Measurement.tobs), \
                        func.avg(Measurement.tobs), \
                        func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start_date).\
                        filter(Measurement.date <= end_date).all()
    session.close()


@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    session = Session(engine)
    calc_se_temp = calc_temps(start, end)
    se_temp= list(np.ravel(calc_se_temp))

    temp_min = se_temp[0]
    temp_max = se_temp[2]
    temp_avg = se_temp[1]
    temp_dict = { 'Minimum temperature': temp_min, 'Maximum temperature': temp_max, 'Avg temperature': temp_avg}

    session.close()

    return jsonify(temp_dict)


if __name__ == '__main__':
    app.run(debug=True)