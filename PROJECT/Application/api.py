from flask import make_response, current_app as app
from flask_restful import Resource, Api, reqparse
from werkzeug.exceptions import HTTPException
import json
from Application.model import*

api = Api(app)

class ValidationError(HTTPException):
    def __init__(self, status_code,error_code,error_message):
        message={"error_code":error_code,"error_message":error_message}
        self.response=make_response(json.dumps(message),status_code)   

class BookApi(Resource):
    def get(self, book_id):           
        book = Book.query.get(book_id)        
        if book:
            result={}
            result["Name"]=book.Name
            result["Content"]=book.Content  
            result["Authors"]=[author.Name for author in book.author]
            result["Pages"]=book.Pages         
            section = Section.query.get(book.Section_id)
            result["Section"] = section.Name          
            return result,200
        elif book is None:
            return "Book not found", 404
        else:
            return "Internal Server Error",500
    
    def delete(self,book_id):
        book=Book.query.get(book_id)
        if book:                 
            Authors.query.filter_by(Book_id=book_id).delete()   
            BookIssueUser.query.filter_by(Book_id=book_id).delete()
            BookRequestUser.query.filter_by(Book_id=book_id).delete()          
            db.session.delete(book)
            db.session.commit()
            return "Book successfully Deleted",200
        elif book is None:
            return "Book not found",404
        else:
            return "Internal Server error",500
    
    def put(self, book_id):
        book = Book.query.get(book_id)
        parser = reqparse.RequestParser()
        parser.add_argument("Name", type=str)
        parser.add_argument("Content", type=str)
        parser.add_argument("Pages", type=str)
        parser.add_argument("Section",type=str)
        parser.add_argument("Authors", type=list,location="json")
        args = parser.parse_args()
        authors_data = args.get("Authors", []) 
        if book:
            if args["Name"]:
                book.Name = args["Name"]
            if args["Content"]:
                book.Content = args["Content"]
            if args["Pages"]:
                book.Pages = args["Pages"]
            if args["Section"]:
                section = Section.query.filter_by(Name=args["Section"]).first()
                if section:
                    book.Section_id = section.ID
                else:
                    raise ValidationError(status_code=400, error_code="BOOK003", error_message="Section does not exist")
            if authors_data:
                Authors.query.filter_by(Book_id=book_id).delete()
                for x in authors_data:
                    author = Authors(Book_id=book_id, Name=x)
                    db.session.add(author) 
            db.session.commit()
            return "Book updated successfully", 200
        elif book is None:
            return "Book not found", 404
        else:
            return "Internal Server error", 500
    
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("Name", type=str)
        parser.add_argument("Content", type=str)
        parser.add_argument("Pages", type=str)
        parser.add_argument("Section",type=str)
        parser.add_argument("Authors", type=list,location="json")
        args = parser.parse_args() 
        if args['Name'] is None:
            raise ValidationError(status_code=400, error_code="BOOK001", error_message="Book name is required")
        if args['Content'] is None:
            raise ValidationError(status_code=400, error_code="BOOK002", error_message="Book Content is required")
        authors_data = args.get("Authors", [])         
        section = Section.query.filter_by(Name=args["Section"]).first()
        if section is None:                  
                raise ValidationError(status_code=400, error_code="BOOK003", error_message="Section does not exist")              
        book = Book(Name=args['Name'], Content=args['Content'], Pages=args['Pages'], Section_id=section.ID)        
        
        try:  
            for x in authors_data:
                author = Authors(book=book, Name=x)
                db.session.add(author)
            db.session.add(book)               
            db.session.commit()    
            return "Book Added Successfully",200
        except:
            db.session.rollback()
            return "Internal Server error",500            
                
api.add_resource(BookApi, "/api/book/<int:book_id>", "/api/book")

class SectionApi(Resource):
    def get(self,section_id):
        section=Section.query.get(section_id)
        if section:
            result={}
            result["ID"]=section.ID
            result["Name"]=section.Name
            result["Date_Created"]=section.Date_Created
            result["Description"]=section.Description
            return result,200
        elif section is None:
            return "Section Not Found",404
        else:
            return "Internal Server Error",500
    
    def delete(self,section_id):
        section=Section.query.get(section_id)
        if section:
            books=Book.query.filter_by(Section_id=section_id).all()
            for book in books:
                BookIssueUser.query.filter_by(Book_id=book.ID).delete()
                BookRequestUser.query.filter_by(Book_id=book.ID).delete()
                Authors.query.filter_by(Book_id=book.ID).delete()            
                db.session.delete(book)
            db.session.delete(section)
            db.session.commit()
            return "Section Deleted Successfully",200
        elif section is None:
            return "Section Not Found",404
        else:
            return "Internal Server Error",500
    
    def put(self,section_id):
        section=Section.query.get(section_id)
        parser = reqparse.RequestParser()
        parser.add_argument("Name", type=str)
        parser.add_argument("Date_Created", type=str)
        parser.add_argument("Description", type=str)
        args = parser.parse_args() 
        if section:
            if args["Name"]:
                section.Name=args["Name"]
            if args["Date_Created"]:
                section.Date_Created=args["Date_Created"]
            if args["Description"]:
                section.Description=args["Description"]
            db.session.commit()
            return "Section Updated Successfully",200
        elif section is None:
            return "Section Not Found",404
        else:
            return "Internal Server Error",500

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("Name", type=str)
        parser.add_argument("Date_Created", type=str)
        parser.add_argument("Description", type=str)
        args = parser.parse_args()
        if args['Name'] is None:
            raise ValidationError(status_code=400, error_code="SECTION001", error_message="Section name is required")
        if args['Date_Created'] is None:
            raise ValidationError(status_code=400, error_code="SECTION002", error_message="Date created is required")
        section=Section(Name=args["Name"],Date_Created=args["Date_Created"],Description=args["Description"])
        try:
            db.session.add(section)
            db.session.commit()
            return "Section added Successfully",200
        except:
            "Internal server Error",500

api.add_resource(SectionApi, "/api/section/<int:section_id>", "/api/section")