
from flask import Flask , render_template, session, request, redirect, url_for, jsonify
import psycopg2, hashlib, os
from flask_cors import CORS

app = Flask(__name__) 
app.secret_key = os.urandom(24)
CORS(app)

def fetchQueryResult(query, parameters):
    con = psycopg2.connect(
        database="bpoonpnh",
        user="bpoonpnh",
        password="Ghp8K45LAum643dO0wX8eFMtnjntZz5L",
        host="isabelle.db.elephantsql.com",
        port= '5432'
    )

    cur_object = con.cursor()

    cur_object.execute(query, parameters)

    result = cur_object.fetchall()

    return result

def executeQueryResult(query, parameters):
    con = psycopg2.connect(
        database="bpoonpnh",
        user="bpoonpnh",
        password="Ghp8K45LAum643dO0wX8eFMtnjntZz5L",
        host="isabelle.db.elephantsql.com",
        port= '5432'
    )

    cur_object = con.cursor()

    cur_object.execute(query, parameters)

    con.commit()

    return True

def getEncryptedPassword(password):
    hash_object = hashlib.sha256()
    hash_object.update(password.encode())
    hash_password = hash_object.hexdigest()
    return hash_password


@app.route('/')
def index():

    #print(fetchQueryResult("Select * from customer"))

    #print(getEncryptedPassword("deku"))

    print(session.get('loggedIn'))
    
    if session.get('loggedIn') == True:
        data = {
            'flag' : 1,
            'cname' : session['cname'],
            'email' : session['email']
        }
        print(data)
        return render_template('index.html' , data = data)
    else:
        data = {
            'flag' : 0
        }
        print(data)
        return render_template('index.html' , data = data)


@app.route('/signup' , methods = ['POST'])
def signup():
    email = request.form['email']
    cname = request.form['cname']
    password = request.form['password']

    enc_password = getEncryptedPassword(password)

    print(enc_password)

    query = "INSERT INTO customer (cName, st_address, city, state, zipcode, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s);"

    parameters = (cname, request.form['st_address'], request.form['city'], request.form['state'], request.form['zipcode'], email, enc_password)

    result = executeQueryResult(query, parameters)

    print(result)

    if result == True:
        print('Register Successful !')
        #Storing details in session variables.
        session['email'] = email
        session['cname'] = cname
        session['loggedIn'] = True

        print("#")
        print(session.get('loggedIn'))
        print("#")
        return redirect(url_for('index'))
    else:
        print("Registration Unsuccessful !")
        return jsonify({'flag' : 0})

@app.route('/login' , methods = ['POST'])
def login():
    email = request.form['email']

    password = request.form['password']   
    enc_password = getEncryptedPassword(password)
    query = "SELECT email, cName, customer_id FROM customer WHERE email = %s and password = %s;"
    parameters = (email, enc_password)

    result = fetchQueryResult(query, parameters)

    print(result)
    
    if not result == None:
        #Storing details in session variables.
        session['email'] = result[0][0]
        session['cname'] = result[0][1]
        session['customer_id'] = result[0][2]
        session['loggedIn'] = True
        print("User Logged In")
        return redirect(url_for('index'))
    else: 
        return jsonify({'flag' : 0})

@app.route('/logout', methods = ['POST'])
def logout():
    session['cname'] = ''
    session['email'] = ''
    session['password'] = ''
    session['loggedIn'] = False
    return jsonify({'flag' : 1})


@app.route('/servicelocations')
def servicelocations():

    email = session['email']

    query = "SELECT sl_id, p_st_address, p_city, p_state, p_zipcode, take_over_date, square_footage, bedroom_count, occupants_count FROM service_locations sl, customer c WHERE sl.customer_id = c.customer_id and c.email = %s;"
    parameters = (email,)

    result = fetchQueryResult(query, parameters)
    print(result)

    print(result[0][5])

    data = {
        'flag' : 1,
        'cname' : session['cname'],
        'email' : session['email'],
        'customer_id' : session['customer_id'],
        'servicelocations' : result,
    }

    print(data)
    return render_template('servicelocations.html' , data = data)

@app.route('/servicelocationdata', methods = ['POST', 'GET'])
def servicelocationdata():

    email = session['email']

    query = "SELECT sl_id, p_st_address, p_city, p_state, p_zipcode, take_over_date, square_footage, bedroom_count, occupants_count FROM service_locations sl, customer c WHERE sl.customer_id = c.customer_id and c.email = %s;"
    parameters = (email,)

    result = fetchQueryResult(query, parameters)
    print(result)

    print(result[0][5])

    data = {
        'flag' : 1,
        'cname' : session['cname'],
        'email' : session['email'],
        'servicelocations' : result,
    }

    print(data)
    return data

@app.route('/servicelocationinsert', methods = ['POST'])
def servicelocationdatainsert():

    query = "INSERT INTO service_locations (customer_id, p_st_address, p_city, p_state, p_zipcode, take_over_date, square_footage, bedroom_count, occupants_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
    print(request.form['takeoverDate'])

    parameters = (session['customer_id'],
                  request.form['stAddress'],
                  request.form['city'],
                  request.form['state'],
                  request.form['zipcode'],
                  request.form['takeoverDate'],
                  request.form['sqFootage'],
                  request.form['bedroomCount'],
                  request.form['occupantCount'])

    result = executeQueryResult(query, parameters)
    print(result)

    if(result == True):
        data = {
            'flag' : 1,
            'cname' : session['cname'],
            'email' : session['email'],
            'servicelocations' : result,
        }
    else:
        data = {
            'flag' : 0,
        }

    return data

@app.route('/servicelocationdelete', methods = ['POST'])
def servicelocationdatadelete():


    query = "DELETE FROM service_locations WHERE sl_id= %s;"
    parameters = (request.form['sl_id'],)

    result = executeQueryResult(query, parameters)
    print(result)

    if(result == True):
        data = {
            'flag' : 1,
        }
    else:
        data = {
            'flag' : 0,
        }

    return data

@app.route('/devices/<int:sl_id>')
def devicesinstalled(sl_id):

    query = "select id.installed_device_id , dm.device_type , dm.model_num  from installed_devices id , device_models dm , service_locations sl where id.device_id = dm.device_id and id.sl_id = sl.sl_id and sl.sl_id = %s"
    parameters = (sl_id,)

    result = fetchQueryResult(query, parameters)
    print(result)

    data = {
        'flag' : 1,
        'cname' : session['cname'],
        'email' : session['email'],
        'sl_id' : sl_id,
        'installedDevices' : result,
    }

    print(data)
    return render_template('installeddevices.html' , data = data)

@app.route('/devicesdata/<int:sl_id>')
def devicesinstalleddata(sl_id):

    query = "select id.installed_device_id , dm.device_type , dm.model_num  from installed_devices id , device_models dm , service_locations sl where id.device_id = dm.device_id and id.sl_id = sl.sl_id and sl.sl_id = %s"
    parameters = (sl_id,)

    result = fetchQueryResult(query, parameters)
    print(result)

    data = {
        'flag' : 1,
        'cname' : session['cname'],
        'email' : session['email'],
        'sl_id' : sl_id,
        'installedDevices' : result,
    }

    print(data)
    return data

@app.route('/installeddevicedelete', methods = ['POST'])
def installeddevicedelete():


    query = "DELETE FROM installed_devices WHERE installed_device_id= %s;"
    parameters = (request.form['installed_device_id'],)

    result = executeQueryResult(query, parameters)
    print(result)

    if(result == True):
        data = {
            'flag' : 1,
        }
    else:
        data = {
            'flag' : 0,
        }

    return data

@app.route('/installeddeviceinsert', methods = ['POST'])
def installeddevicedatainsert():


    request.form['device_id']
    request.form['sl_id']


    query = "INSERT INTO installed_devices (device_id, sl_id) VALUES (%s, %s);"
    

    parameters = (request.form['device_id'],
                  request.form['sl_id'])

    result = executeQueryResult(query, parameters)
    print(result)

    if(result == True):
        data = {
            'flag' : 1,
        }
    else:
        data = {
            'flag' : 0,
        }

    return data

@app.route('/fetchdevicetypes')
def fetchdevicetypes():

    query = "select distinct (dm.device_type) from device_models dm;"
    parameters = ()

    result = fetchQueryResult(query, parameters)
    print(result)

    data = {
        'flag' : 1,
        'devicestypes' : result,
    }

    print(data)
    return data

@app.route('/fetchmodels/<device_type>')
def fetchmodels(device_type):

    print(device_type)

    query = "select dm.device_id, dm.model_num from device_models dm where dm.device_type = %s;"
    parameters = (device_type,)

    result = fetchQueryResult(query, parameters)
    print(result)

    data = {
        'flag' : 1,
        'modeltypes' : result,
    }

    print(data)
    return data

@app.route('/fetchdevicepiedata', methods = ['POST'])
def fetchdevicepiedata():

    sl_id = request.form['sl_id']

    query = "select dm.device_type , count(*) from installed_devices id , device_models dm , service_locations sl where id.device_id = dm.device_id and id.sl_id = sl.sl_id and sl.sl_id = %s group by dm.device_type;"
    parameters = (sl_id,)

    result = fetchQueryResult(query, parameters)

    device_model = []
    count = []

    for device in result:
        device_model.append(device[0])
        count.append(device[1])
    
    data = {
        'flag' : 1,
        'device_model' : device_model,
        'count' : count
    }

    print(data)

    return data

@app.route('/fetchdevicebardata', methods = ['POST'])
def fetchdevicebardata():

    sl_id = request.form['sl_id']
    month = request.form['month']
    year = request.form['year']

    query = "select dm.device_type , sum(e.val) from events e , installed_devices id, device_models dm where e.installed_device_id = id.installed_device_id and id.device_id = dm.device_id and id.sl_id = %s and DATE_PART('month', e.event_timestamp) = %s and DATE_PART('year', e.event_timestamp) = %s and e.event_desc = 'energy use' group by dm.device_type;"
    parameters = (sl_id,month,year)

    result = fetchQueryResult(query, parameters)

    device_model = []
    count = []

    for device in result:
        device_model.append(device[0])
        count.append(device[1])
    
    data = {
        'flag' : 1,
        'device_model' : device_model,
        'count' : count
    }

    print(data)

    return data

@app.route('/fetchservicelocationbardata', methods = ['POST'])
def fetchservicelocationbardata():

    c_id = request.form['c_id']
    month = request.form['month']
    year = request.form['year']

    query = "select sl2.p_st_address || '-' || sl2.p_city as House , sum(val) from events e , installed_devices id, service_locations sl2 where e.installed_device_id = id.installed_device_id and id.sl_id = sl2.sl_id and id.sl_id in (select sl_id from service_locations sl where sl.customer_id = %s) and DATE_PART('month', e.event_timestamp) = %s and DATE_PART('year', e.event_timestamp) = %s and e.event_desc = 'energy use' group by sl2.p_st_address , sl2.p_city;"
    parameters = (c_id,month,year)

    result = fetchQueryResult(query, parameters)

    location = []
    count = []

    for loc in result:
        location.append(loc[0])
        count.append(loc[1])
    
    data = {
        'flag' : 1,
        'location' : location,
        'count' : count
    }

    print(data)

    return data

@app.route('/fetchservicelocationpiedata', methods = ['POST'])
def fetchservicelocationpiedata():

    c_id = request.form['c_id']

    query = "select p_city , count(*) from service_locations sl where sl.customer_id = %s group by p_city;"
    parameters = (c_id,)

    result = fetchQueryResult(query, parameters)

    device_model = []
    count = []

    for device in result:
        device_model.append(device[0])
        count.append(device[1])
    
    data = {
        'flag' : 1,
        'device_model' : device_model,
        'count' : count
    }

    print(data)

    return data

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=8989)