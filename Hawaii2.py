from flask import Flask  
from flask import jsonify

#dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
import pandas as pd
import numpy as np
import datetime as dt

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurements = Base.classes.measurement
Stations = Base.classes.station

#session = Session(engine)

@app.route("/")
def home():
	return "Welcome to Surfs Up"

@app.route("/welcome")
#List all available routes
def welcome ():
	return (
		f"Welcome to the Surf Up API<br>"
		f"Available Routes:<br>"
		f"/api/v1.0/precipitation<br>"
		f"/api/v1.0/stations<br>"
		f"/api/v1.0/tobs<br>"
		f"/api/v1.0/<start><br>"
		f"/api/v1.0<start>/<end><br>"
	)
	
@app.route("/api/v1.0/precipitation")
def precipitation():
	#Query for the dates and temperature observations from the last year.
	session = Session(engine)
	results = session.query(Measurements.date,Measurements.prcp).filter(Measurements.date >= "08-23-2017").all()
	#session.close()
	year_prcp = list(np.ravel(results))
	
	#Create a dictionary using 'date' as the key and 'prcp' as the value.
	"""year_prcp = []
	for result in results:
		row = {}
		row[Measurements.date] = row[Measurements.prcp]
		year_prcp.append(row)"""

	return jsonify(year_prcp)

@app.route("/api/v1.0/stations")
def stations():
	#return a json list of stations from the dataset.
	session = Session(engine)
	station = session.query(Stations.station, Stations.name).all()
	session.close()
	station_df = pd.DataFrame(station)
	station_df.set_index(['Station'], inplace=True)
	
	results = {}
	for index,row in station_df.iterrows():
		results[index] = dict(row)
		
	return jsonify(results)
	
	
@app.route("/api/v1.0/tobs")
def temperature():
	#Return a json list of Temperature Observations (tobs) for the previous year
	session = Session(engine)
	year_tobs = []
	results = session.query(Measurements.tobs).filter(Measurements.date >= "2016-08-23").all()
	session.close()
	year_tobs = list(np.ravel(results))

	return jsonify(year_tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def tripDuration(start, end='empty'):
    session = Session(engine)
    if(end == 'empty'):
        end = session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0]
        

    trip_index = f"{start} to {end}"
   
  
    duration= session.query(func.min(Measurements.tobs).label("MinTemp"), func.max(Measurements.tobs).label("MaxTemp"), func.avg(Measurements.tobs).label("AvgTemp")).filter(Measurements.date.between(start, end)).all()
    session.close()
   
    duration_df = pd.DataFrame(duration)
    duration_df["info"] = [trip_index]
    duration_df.set_index(['info'], inplace=True)

    results = {}
    for index,row in duration_df.iterrows():
        results[index] = dict(row)
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)