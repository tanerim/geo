from flask import Flask, jsonify, request, render_template
import mysql.connector
import json

app = Flask(__name__)

# create a connection to the MySql database
db = mysql.connector.connect(
    host="localhost",
    user="***",
    password="***",
    database="geo"
)

# define a function to execute the query based on input parameters
def execute_query(params):
    il = params.get('il')
    cursor = db.cursor()
    query = "SELECT * FROM geo_all WHERE 1=1"
    values = []
    if il:
        query += " AND il = %s"
        values.append(il)
    if 'ilce' in params:
        query += " AND ilce = %s"
        values.append(params['ilce'])
    if 'mah' in params:
        query += " AND mah = %s"
        values.append(params['mah'])
    cursor.execute(query, tuple(values))
    columns = [desc[0] for desc in cursor.description]
    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return result


# define a function to handle non-serializable objects
def handle_non_serializable(obj):
    if isinstance(obj, bytes):
        return obj.decode()
    raise TypeError(f"{type(obj)} is not JSON serializable")

# define a route for the API
@app.route('/query', methods=['GET'])
def query():
    params = request.args.to_dict()
    result = execute_query(params)
    result = json.loads(json.dumps(result, default=handle_non_serializable))
    return jsonify(result)

# define a route to serve the API
@app.route('/gui')
def gui_query():
    il = request.args.get('il')
    ilce = request.args.get('ilce')
    mah = request.args.get('mah')
    params = {'il': il, 'ilce': ilce, 'mah': mah}
    try:
        result = execute_query(params)
        # decode byte strings to regular strings
        for row in result:
            for key, value in row.items():
                if isinstance(value, bytes):
                    row[key] = value.decode()
        return render_template('result.html', result=result)
    except ValueError as e:
        return str(e)


# define a route to serve the graphical interface
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)