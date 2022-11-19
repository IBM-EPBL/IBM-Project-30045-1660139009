import re 
import numpy as np
import os
from flask import Flask, app,request,render_template
from tensorflow.keras import models
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.python.ops.gen_array_ops import concat
from tensorflow.keras.applications.inception_v3 import preprocess_input
import requests
from flask import Flask,request,render_template,redirect,url_for
from cloudant.client import Cloudant

UPLOAD_FOLDER=os.path.join('static','uploads')
client = Cloudant.iam("48b309ee-528e-4ac3-bb4d-adcf2b863882-bluemix","_i0fpz1gN-ngDO9UG-02mhz6d3MJCuZ-VS4kgkjMziB9",connect=True)
my_database=client.create_database("my_database")
model1=load_model("model/level.h5")
if model1:
    print('model exists')
model2=load_model("model/body.h5")
app=Flask(__name__) 
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.secret_key='sharavana'

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/index')
def home():
    return render_template('index.html')
@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/afterreg',methods=['POST'])
def afterreg():
    x=[x for x in request.form.values()]
    print(x)
    data={
        '_id': x[1],
        'name':x[0],
        'psw':x[2],
    }
    print(data)
    
    query = {'_id':{'$eq': data['_id']}}
    docs = my_database.get_query_result(query)
    print(docs)
    
    print(len(docs.all()))
    if (len(docs.all())==0):
        url = my_database.create_document(data)
        return redirect(url_for('login'))
    else:
        return render_template('login.html',pred="You are already a member, please login using your details")
        


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/afterLogin',methods=['POST'])
def afterlogin():
    user = request.form['_id']
    passw=request.form['psw']
    print(user,passw)
    
    query = {'_id':{'$eq': user}}
    docs = my_database.get_query_result(query)
    print(docs)
    
    #print(len(docs.all()))
    if (len(docs.all())==0):
        return render_template('login.html',pred="The username is not found.")
    else:
         if((user==docs[0][0]['_id'] and passw==docs[0][0]['psw'])):
            return redirect(url_for('prediction'))
         else:
            print('Invalid User') 
   
            
        



@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

@app.route("/postprediction",methods=["POST","GET"])
def prediction_post(): 
    if request.method=="POST":
        print('function started')
        f=request.files["image"]
        basepath=os.path.dirname(__file__) 
        #file_name=secure_filename(f.filename)
        #basepath="uploaded_files"
        print('the file is saved at',basepath)
        #filepath=os.path.join(basepath,'uploads',f.filename)
        filepath=UPLOAD_FOLDER+'/'+ f.filename
        print('the file is saved at',filepath)
        f.save(filepath)
        img=image.load_img(filepath, target_size=(224,224))
        x=image.img_to_array(img)
        x=np.expand_dims(x,axis=0)
        img_data=preprocess_input(x)
        prediction1=np.argmax(model1.predict(img_data)) 
        prediction2=np.argmax(model2.predict(img_data))
        index1=["front","rear","side"]
        index2=["minor","moderate","severe"]

        result1=index1[prediction1]
        result2=index2[prediction2]
        if (result1 == "front" and result2 == "minor"):
            value = "3000 - 5000 INR"
        elif (result1 == "front" and result2 == "moderate"):
            value = "6000 8000 INR"
        elif (result1 == "front" and result2 == "severe"):
            value = "9000 11000 INR"

        elif (result1 == "rear" and result2 == "minor"):
            value = "4000 - 6000 INR"

        elif (result1 == "rear" and result2 == "moderate"):
            value = "7000 9000 INR"

        elif (result1 == "rear" and result2 == "severe"):
            value = "11000 - 13000 INR"

        elif (result1 == "side" and result2 == "minor"):
            value = "6000 - 8000 INR"

        elif (result1 == "side" and result2 == "moderate"):
            value = "9000 - 11000 INR"

        elif (result1 == "side" and result2 == "severe"):
            value = "12000 - 15000 INR"

        else:
            value = "16000 - 50000 INR"
        print(value)
        return render_template('result.html', prediction=value)    
    

'''@app.route("/result")
def result():  
    return render_template('result.html',prediction='3000-4000')'''


if __name__ == '__main__':
    app.run(debug=True,port=8080)   