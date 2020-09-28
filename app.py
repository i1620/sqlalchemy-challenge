import datetime as dt
from dateutil.parser import parse
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Took some code from Jupyter Notebook
measurement_df = pd.read_sql("select date, prcp from Measurement \
    where date between '2016-08-23' and '2017-08-23'",conn)
measurement_df = measurement_df.dropna()
station_df = pd.read_sql("select * from Station",conn)
station_list = station_df['station'].to_json(orient='records')
high_station = pd.read_sql("select date,tobs from Measurement \
where station = 'USC00519281' and date between '2016-08-23' \
    and '2017-08-23'", conn)
station_9281 = high_station.to_json(orient='records')
measure_df = pd.read_sql("select * from Measurement",conn)
last_year = measure_df.iloc[-1]['date']

# Flask Routes
@app.route('/')
def hello():
    return (
        f"Hello, this is the Hawaii Climate App!<br/>"
        f"How can I help you today?<br/>"
        f"These are the Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return a list of stations."""
    return jsonify(measurement_df.to_dict(orient='records'))

@app.route('/api/v1.0/stations')
def stations():
    """Return a list of stations."""
    return station_list

@app.route('/api/v1.0/tobs')
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    return station_9281

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    if not end:
        end = last_year
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), 
    func.max(Measurement.tobs)).filter(Measurement.date >= start).filter\
            (Measurement.date <= end).all()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
