from enum import unique
from flask import Flask,render_template,redirect,flash,request
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required,login_user,logout_user,LoginManager,UserMixin,current_user
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, URL ,ValidationError
from werkzeug.exceptions import abort
import requests
import os


app=Flask(__name__)
os.environ.get
app.config["SECRET_KEY"]=os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///weather_app.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
my_api=os.environ.get("API")
base_url="https://api.openweathermap.org/data/2.5/weather?q="

db=SQLAlchemy(app)


#DATABASE Models
# class Users(UserMixin,db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     name=db.Column(db.String(10))
#     username=db.Column(db.String(10),unique=True)
#     password=db.Column(db.String(10))
#     lists = db.relationship('List', backref='users', lazy='dynamic')

class WeatherData(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),unique=True)
    weather=db.Column(db.String(20))
    discription=db.Column(db.String(100))
    icon=db.Column(db.String(20))
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


db.create_all()
#fORMS
# class Register(FlaskForm):
#     name=StringField('Name',validators=[DataRequired()])
#     username=StringField('Username',validators=[DataRequired()])
#     password=PasswordField('Password',validators=[DataRequired()])

#     def validate_username(self, username):
#         user = Users.query.filter_by(username=username.data).first()
#         if user:
#             raise ValidationError('That username already exits. Please choose another.')

# class Login(FlaskForm):
#     username=StringField('Username',validators=[DataRequired()])
#     password=PasswordField('Password',validators=[DataRequired()])

#     def validate_username(self, username):
#         user = Users.query.filter_by(username=username.data).first()
#         if not user:
#             raise ValidationError('Wrong Username or Password')


#api data fetching
def get_weather_data(city):
    respose=requests.get(f"{base_url}{city}&appid={my_api}")
    data=respose.json()
    return data




@app.route('/')
def index_get():
    all_cities=db.session.query(WeatherData).all()
    return render_template("index.html",weater_data=all_cities)




@app.route('/post',methods=["POST"])
def index_post():    
    city=request.form.get('cityname')
    print(city)
    city_data=get_weather_data(city)
    err_msg=''
    if city:
        old_city = WeatherData.query.filter_by(name=city).first()
        if not old_city:
            if city_data['cod']==200:
                city_obj=WeatherData(
                    name=city,
                    weather=city_data['weather'][0]['main'],
                    discription=city_data['weather'][0]['description'],
                    icon=city_data['weather'][0]['icon'],
                )
                db.session.add(city_obj)
                db.session.commit()
            else:
                err_msg = 'That city dont exist.'      
        else:
            err_msg = 'You tried entering a city that already exists.'
        if err_msg:
            flash(err_msg,'error')
        else:
            flash("Successfully Added",'success')
    return redirect(url_for('index_get'))



@app.route('/delete')
def delete():
    city_id=request.args.get("city_id")
    city_to_delete = WeatherData.query.get(city_id)
    db.session.delete(city_to_delete)
    db.session.commit()

    return redirect(url_for("index_get"))
if __name__=="__main__":
    app.run(debug=True)