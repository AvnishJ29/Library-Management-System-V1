from flask import render_template, request, redirect, url_for, session,send_file
from Application.model import *
from flask import current_app as app
from datetime import datetime
from fpdf import FPDF


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/user/register",methods=["POST","GET"])
def user_register():
    if request.method=="POST":
        user_name=request.form.get("user")
        email=request.form.get("email")
        password=request.form.get("pass")
        if user_name is None:
            return "<h1>Username cannot be None</h1>"
        if email is None or "@" not in email:
            return "<h1>Invalid Email</h1>"
        if password is None or len(password)<5:
            return "<h1>Password cannot be None</h1>"
        user=Users(user_name=user_name,password=password,Email=email,Wallet=100,Role="general")
        try:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("user_login"))
        except:
            db.session.rollback()
            return "<h1>OOPS! Somethong went wrong</h1>"
    return render_template("user_register.html")

@app.route("/user/login",methods=["POST","GET"])
def user_login():
    if request.method=="POST":
        user_name=request.form.get("user")
        password=request.form.get("pass")   
        if user_name is None:
            return "<h1>Username cannot be None</h1>"     
        user=Users.query.filter_by(user_name=user_name,password=password,Role="general").first()
        if user:
            session["user_id"]=user.ID
            return redirect(url_for('user_dashboard'))
        else:
            return render_template("error_user_login.html")
    else:
        return render_template("user_login.html")
    
@app.route("/librarian/login",methods=["POST","GET"])
def librarian_login():
    if request.method=="POST":
        user_name=request.form.get("user")
        password=request.form.get("pass")
        if user_name is None:
            return "<h1>Username cannot be None</h1>"
        user=Users.query.filter_by(user_name=user_name,password=password,Role="librarian").first()
        if user:
            session["librarian_id"]=user.ID
            return redirect(url_for('librarian_dashboard'))
        else:
             return render_template("error_librarian_login.html")
    else:
        return render_template("librarian_login.html")

@app.route("/user/logout")
def user_logout():
    session.pop("user_id",None)
    return redirect("/")

@app.route("/librarian/logout")
def librarian_logout():
    session.pop("librarian_id",None)
    return redirect("/")





@app.route("/user/dashboard")
def user_dashboard():
     if 'user_id' in session:                
        user_details=Users.query.get(session['user_id'])
        sections=Section.query.all()
        books={}
        for section in sections:
            books[section]=Book.query.filter_by(Section_id=section.ID).all()    
        recently_added_books = Book.query.order_by(Book.ID.desc()).limit(5).all()
        return render_template("user_dashboard.html",user=user_details,books=books,section=sections,recent_books=recently_added_books)
     else:
        return redirect(url_for("user_login"))

@app.route("/user/profile/<int:user_id>",methods=["GET","POST"])
def profile(user_id):
    user=Users.query.get(user_id) 
    issue=BookIssueUser.query.filter_by(User_id=user_id).count()
    req=BookRequestUser.query.filter_by(User_id=user_id).count()
    if request.method=="POST":
        user_name=request.form.get("user")
        email=request.form.get("email")
        password=request.form.get("pass")       
        if password is None or len(password)<5:
            return "<h1>Password cannot be None</h1>"
        user.user_name=user_name
        user.Email=email
        user.password=password
        db.session.commit()
        return redirect(url_for("user_dashboard"))
    else:     
        return render_template("user_profile.html",user=user,issue=issue,req=req)        

@app.route("/book/issued/<int:user_id>")
def book_issued(user_id):
    if 'user_id' in session:
        user=Users.query.get(user_id)
        loans = BookIssueUser.query.filter_by(User_id=user_id).all()
        books = []
        for loan in loans: 
            return_date = datetime.strptime(loan.Return_date,'%Y-%m-%d')           
            if return_date >= datetime.now():
                book = Book.query.get(loan.Book_id)
                books.append((book,loan))
            else:
                db.session.delete(loan)                
                db.session.commit()
        return render_template("issued_books.html",books=books,user=user)
    else:
        return redirect(url_for("user_login"))

@app.route("/book/<int:book_id>/request/<int:user_id>")
def request_book(book_id,user_id): 
    if 'user_id' in session:
        user=Users.query.get(user_id)
        n=BookRequestUser.query.filter_by(User_id=user_id).count()
        if n<5:
            book_request=BookRequestUser(User_id=user_id,Book_id=book_id)
            try:
                db.session.add(book_request)
                db.session.commit()
            except:
                db.session.rollback()
                return render_template("error.html",error="book_already_request",user=user)
        else:                   
            return render_template("error.html",error="book_request",user=user)
        return redirect(url_for("user_dashboard"))  
    else:
        return redirect(url_for("user_login"))
    
@app.route("/book/<int:book_id>/return/<int:user_id>")
def return_book(book_id,user_id):
     if 'user_id' in session:        
        BookIssueUser.query.filter_by(User_id=user_id,Book_id=book_id).delete()
        db.session.commit()        
        return redirect(url_for("user_dashboard"))
     else:
         return redirect(url_for("user_login"))         

@app.route("/book/<int:book_id>/feedback/<int:user_id>",methods=["POST","GET"])
def book_feedback(book_id,user_id):
    if 'user_id' in session:
        book = Book.query.get(book_id)
        user = Users.query.get(user_id)
        if request.method=="POST":            
            content_rating =int(request.form.get('content_rating'))
            writing_style_rating = int(request.form.get('writing_style_rating'))
            recomm_rating=int(request.form.get('recomm_rating'))
            overall_rating=int(request.form.get('overall_rating')) 
            comment=request.form.get("comment")                  
            rating=UserFeedback(User_id=user_id,Book_id=book_id,Content_quality=content_rating,Writing_style=writing_style_rating,Recommendation=recomm_rating,Overall_rating=overall_rating,Comment=comment)
            try:
                db.session.add(rating)
                db.session.commit()
                return redirect("/user/dashboard")
            except:
                db.session.rollback()
                return render_template("error.html",error="book_feedback",user=user)     
        else:
            return render_template('book_feedback.html',book=book,user=user)
    else:
        return redirect(url_for("user_login"))

@app.route('/book/download/<int:book_id>/<int:user_id>')
def download_pdf(book_id,user_id):     
    if 'user_id' in session:
        issued = BookIssueUser.query.filter_by(Book_id=book_id,User_id=user_id).first() 
        if issued:  
            user=Users.query.get(user_id)
            user.Wallet-=10
            db.session.commit()
            book = Book.query.get(book_id)
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            text=book.Content
            filename=f"{book.Name}.pdf"
            pdf.multi_cell(0, 10, text)
            pdf.output(filename)               
            return send_file(filename, as_attachment=True)
        else:
            return "<h1>You are not Authorised for this Action</h1>"            
    else:
        return redirect(url_for("user_login"))  
    
@app.route('/book/content/<int:book_id>/<int:user_id>')
def content(book_id,user_id):
    book=Book.query.get(book_id)
    user=Users.query.get(user_id)
    return render_template("book_content.html",book=book,user=user)
        

@app.route("/user/search/<int:user_id>",methods=["GET","POST"])
def search(user_id):
    user=Users.query.get(user_id)
    section=Section.query.all()
    if request.method=="POST":
        query=request.form.get("value").lower()    
        books = Book.query.filter((Book.Name.ilike(f'%{query}%')) | (Book.Pages.ilike(f'%{query}%'))| (Authors.Name.ilike(f'%{query}%'))).all()    
    return render_template("search.html",books=books,user=user,section=section)  

@app.route("/search/section/<int:section_id>/<int:user_id>")
def search_section(section_id,user_id):
    user=Users.query.get(user_id)
    books=Book.query.filter_by(Section_id=section_id).all()
    section=Section.query.get(section_id)
    sections=Section.query.all()
    return render_template("search_section.html",user=user,books=books,section=section,sections=sections)