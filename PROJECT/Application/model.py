from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):   
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String, nullable=False)
    Content = db.Column(db.String, nullable=False)   
    Pages = db.Column(db.String) 
    Section_id = db.Column(db.Integer, db.ForeignKey("section.ID"))    
    author=db.relationship('Authors',backref='book')    

class Section(db.Model):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String, nullable=False)
    Date_Created = db.Column(db.String, nullable=False)
    Description = db.Column(db.String)     

class Authors(db.Model):
    Book_id = db.Column(db.Integer, db.ForeignKey("book.ID"), nullable=False, primary_key=True)
    Name = db.Column(db.String, nullable=False, primary_key=True)

class Users(db.Model):    
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    Role = db.Column(db.String, nullable=False)
    Email = db.Column(db.String,nullable=False)
    Wallet=db.Column(db.Integer,nullable=False)

class BookIssueUser(db.Model):
    User_id = db.Column(db.Integer, db.ForeignKey("users.ID"), primary_key=True)
    Book_id = db.Column(db.Integer, db.ForeignKey("book.ID"),  primary_key=True)
    Issue_date = db.Column(db.String)
    Return_date = db.Column(db.String)

class BookRequestUser(db.Model):
    User_id = db.Column(db.Integer, db.ForeignKey("users.ID"), nullable=False, primary_key=True)
    Book_id = db.Column(db.Integer, db.ForeignKey("book.ID"), nullable=False, primary_key=True)

class UserFeedback(db.Model):
    User_id = db.Column(db.Integer, db.ForeignKey("users.ID"), primary_key=True)
    Book_id = db.Column(db.Integer, db.ForeignKey("book.ID"), primary_key=True)
    Content_quality = db.Column(db.Integer, nullable=False)
    Writing_style = db.Column(db.Integer, nullable=False)
    Recommendation = db.Column(db.Integer, nullable=False)
    Overall_rating = db.Column(db.Integer, nullable=False)
    Comment=db.Column(db.String)
    