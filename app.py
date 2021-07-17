#!/usr/bin/env python
# coding: utf-8

# In[17]:


from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import pandas as pd
import pickle
import os

reg=pickle.load(open('static/regressor.pkl', 'rb'))
membrane=pickle.load(open('static/membrane.pkl','rb'))
o2=pickle.load(open('static/O2.pkl','rb'))
h2=pickle.load(open('static/H2.pkl','rb'))

app=Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')

def upload():
    return render_template("Pred.html")

@app.route('/uploader', methods=['GET','POST'])
def uploader():
    if request.method=='POST':
        k=request.form['options']
        if k=='1':
            return render_template("open.html")
        else:
            return render_template('index.html')

@app.route('/uploadfile', methods=['GET','POST'])
def uploadfile():
    if request.method=='POST':
        f=request.files['file']
        

        fsplit=f.filename.split(".")[-1]
        if fsplit=='xlsx':
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename("test_data.xlsx")))
            df=pd.read_excel("static/test_data.xlsx")
        else:
            return "Kindly upload Excel Format File"
        
#         df=df.fillna(0)
        df.fillna(0,inplace=True)
        print(df.head())
        df['Membrane']=membrane.transform(df['Membrane'])
        df['O2 Condition']=o2.transform(df['O2 Condition'])
        df['H2 Condition']=h2.transform(df['H2 Condition'])
        names=['Thickness (micron)', 'Temperature (C Deg)', 'Current (A cm-2)','Content of composite (wt%)',
       'Relative Humidity (%)', 'Flow Rate (H2) (cm3/min)',
       'Flow Rate (O2) (cm3/min)', 'O2 Condition', 'H2 Condition', 'Membrane']
        df=df[names]
        print(df.head())
        pred=reg.predict(df)
        df['OCV (V)']=pred
        df['Power W/cm2']=df['OCV (V)']*df['Current (A cm-2)']
        
        return render_template("simple.html", tables=[df.to_html(classes='data')], titles=df.columns.values)
        
@app.route('/fildetails', methods=['GET','POST'])
def fildetails():
    if request.method=='POST':
        final=[]
        c=request.form['name']
        
        d=request.form['thickness']
        e=request.form['current']
        f=request.form['temp']
        g=request.form['content']
        h=request.form['humidity']
        i=request.form['flow-rate1']
        h=request.form['flow-rate2']
        j=request.form['o2 condition']
        k=request.form['h2 condition']
        
        names=['Thickness (micron)', 'Temperature (C Deg)', 'Current (A cm-2)','Content of composite (wt%)',
       'Relative Humidity (%)', 'Flow Rate (H2) (cm3/min)',
       'Flow Rate (O2) (cm3/min)', 'O2 Condition', 'H2 Condition', 'Membrane']
        
        df=pd.DataFrame(columns=names, index=range(0,1))
        
        df['Thickness (micron)'][0]=float(d)
        df['Temperature (C Deg)'][0]=float(f)
        df['Current (A cm-2)'][0]=float(e)
        df['Content of composite (wt%)'][0]=float(g)
        df['Relative Humidity (%)'][0]=float(h)
        df['Flow Rate (H2) (cm3/min)'][0]=float(i)
        df['Flow Rate (O2) (cm3/min)'][0]=float(h)
        df['O2 Condition'][0]=o2.transform([j])
        df['H2 Condition'][0]=h2.transform([k])
        df['Membrane'][0]=membrane.transform([c])
        pred=reg.predict(df)
        power=pred*float(e)
        
        return render_template("result.html", msg=float(pred),msg2=float(power), a10=c,
                        a1=d,a2=f,a3=e,a4=g,a5=h,a6=i,a7=h,a8=j,a9=k)
        
if __name__ == '__main__':
    app.run()       

