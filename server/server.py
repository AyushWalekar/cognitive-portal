from flask import Flask, request
from flask_cors import CORS

# from .people_counting_opencv import queries
from people_counting_opencv import queries

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app)


# sanity check route
@app.route('/test', methods=['GET'])
def test():
    return queries.get_logs_from_date_str("2019-01-01T01:01:01Z")


@app.route('/fromto', methods=['GET'])
def get_logs():
    return queries.get_logs_str(request.args.get('from_time'), request.args.get('to_time'))


@app.route('/today', methods=['GET'])
def get_todays_logs():
    return queries.get_todays_logs()


@app.route('/that_day', methods=['GET'])
def get_that_days_logs():
    date_str = request.args.get('date_str')
    return queries.get_that_days_logs(date_str=date_str)


@app.route('/past_logs', methods=['GET'])
def get_past_logs():
    return queries.get_past_logs(days=request.args.get('days'), hours=request.args.get('hours'),
                                 minutes=request.args.get('minutes'), weeks=request.args.get('weeks'),
                                 months=request.args.get('months'), years=request.args.get('years'))


if __name__ == '__main__':
    app.run(port=2222)
