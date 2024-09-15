from flask import render_template, request, redirect, url_for, session
from Application.model import *
from flask import current_app as app
from datetime import datetime,timedelta
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

@app.route("/librarian/dashboard")
def librarian_dashboard():
    if 'librarian_id' in session:
        sections=Section.query.all()
        books={}
        for section in sections:
            books[section]=Book.query.filter_by(Section_id=section.ID).all()   
            
        return render_template("librarian_dashboard.html",books=books,section=sections)    
    else:
        return redirect(url_for('librarian_login'))

@app.route("/book/create",methods=["GET","POST"])
def create_book():
    if 'librarian_id' in session:   
        section=Section.query.all()     
        if request.method == 'POST':            
            Name = request.form['name']
            Content = request.form.get('content') 
            Pages=request.form.get('pages')                              
            author_names = request.form.get('author_names').split(',') 
            section_id=request.form.get('section_id')          
            book=Book(Name=Name,Content=Content,Pages=Pages,Section_id=section_id)         
            for x in author_names:
                author=Authors(book=book,Name=x)
                db.session.add(author)  
            db.session.add(book)               
            db.session.commit()
            return redirect(url_for('librarian_dashboard'))                                    
        else:
            return render_template("book_create.html",section=section)
    else:
        return redirect(url_for('librarian_login'))

@app.route("/book/edit/<int:book_id>",methods=["GET","POST"])
def edit_book(book_id):
    if 'librarian_id' in session:
        sections=Section.query.all()        
        book=Book.query.get(book_id) 
        section=Section.query.get(book.Section_id)
        existing_authors=""
        auth=list(Authors.query.filter_by(Book_id=book_id))
        if len(auth)<=1:
            existing_authors+=auth[0].Name
        else:
            for i in range(len(auth)-1):
                existing_authors+=auth[i].Name+","
            existing_authors+=auth[-1].Name      
                 
        if request.method=="POST":
            Name = request.form.get('name')
            Content = request.form.get('content')
            Pages=request.form.get('pages')
            section_id=request.form.get('section_id')            
            author_names = request.form.get('author_names').split(',')             
            book.Name=Name
            book.Content=Content
            book.Pages=Pages
            book.Section_id=section_id
            Authors.query.filter_by(Book_id=book_id).delete()
            for x in author_names:
                author=Authors(Book_id=book_id,Name=x)
                db.session.add(author)                    
            db.session.commit()
            return redirect(url_for('librarian_dashboard'))             
        else:
            return render_template("book_edit.html",book=book,section=section,sections=sections,existing_authors=existing_authors)
    else:
        return redirect(url_for('librarian_login'))

@app.route("/section/edit/<int:section_id>",methods=["GET","POST"])
def edit_section(section_id):
    if 'librarian_id' in session:
        section=Section.query.get(section_id)
        if request.method=="POST":
            Name = request.form.get('name')
            Description = request.form.get('description')         
            section.Name=Name
            section.Description=Description  
            db.session.commit()
            return redirect(url_for('librarian_dashboard'))                     
        else:
            return render_template("section_edit.html",section=section)
    else:
        return redirect(url_for('librarian_login'))

@app.route("/section/create",methods=["GET","POST"])
def create_section():
    if 'librarian_id' in session:
        if request.method=="POST":
            Name = request.form.get('name')
            Description = request.form.get('description') 
            Date_Created= datetime.now().strftime("%Y-%m-%d")
            section=Section(Name=Name,Date_Created=Date_Created,Description=Description)
            db.session.add(section)
            db.session.commit()
            return redirect(url_for('librarian_dashboard')) 
        else:
            return render_template("section_create.html")
    else:
        return redirect(url_for('librarian_login'))

@app.route("/section/remove/<int:section_id>")
def remove_section(section_id):
    if 'librarian_id' in session:
        section=Section.query.get(section_id)
        books=Book.query.filter_by(Section_id=section_id).all()
        for book in books:
            BookIssueUser.query.filter_by(Book_id=book.ID).delete()
            BookRequestUser.query.filter_by(Book_id=book.ID).delete()
            Authors.query.filter_by(Book_id=book.ID).delete()            
            db.session.delete(book)
        db.session.delete(section)
        db.session.commit()
        return redirect(url_for('librarian_dashboard'))
    else:
        return redirect(url_for('librarian_login'))

@app.route("/book/remove/<int:book_id>")
def remove_book(book_id):
    if 'librarian_id' in session:
        book=Book.query.get(book_id)        
        Authors.query.filter_by(Book_id=book_id).delete()   
        BookIssueUser.query.filter_by(Book_id=book_id).delete()
        BookRequestUser.query.filter_by(Book_id=book_id).delete()                     
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('librarian_dashboard'))
    else:
        return redirect(url_for('librarian_login'))

@app.route("/book/issue/management")
def issue_management():
    if 'librarian_id' in session:
        issued_books, nonissued_books, pending_books = [], [], []  
        books = Book.query.all()        
        users = Users.query.all()
        for book in books:
            temp1 = None
            temp2 = None
            for user in users:
                temp1 = BookIssueUser.query.filter_by(Book_id=book.ID, User_id=user.ID).first()
                temp2 = BookRequestUser.query.filter_by(Book_id=book.ID, User_id=user.ID).first()
                if temp1:
                    issued_books.append((book, user))
                if temp2:
                    pending_books.append((book, user))            
        for book in books:
            if book not in [u[0] for u in issued_books] and book not in [u[0] for u in pending_books]:
                nonissued_books.append(book)
                    
        return render_template("issue_management.html", issued_books=issued_books, nonissued_books=nonissued_books, pending_books=pending_books, books=books)
    else:
        return redirect(url_for('librarian_login'))

@app.route("/book/<int:user_id>/access/revoke/<int:book_id>")
def access_revoke(user_id,book_id):
    if 'librarian_id' in session:
        BookIssueUser.query.filter_by(User_id=user_id,Book_id=book_id).delete()
        db.session.commit()
        return redirect(url_for("issue_management"))
    else:
        return redirect(url_for('librarian_login'))

@app.route("/book/<int:user_id>/access/grant/<int:book_id>")
def access_grant(user_id,book_id):
    if 'librarian_id' in session:
        BookRequestUser.query.filter_by(User_id=user_id,Book_id=book_id).delete()
        Issue_date = datetime.now()
        Return_date = Issue_date + timedelta(days=14)
        book_issue = BookIssueUser(User_id=user_id,Book_id=book_id,Issue_date=Issue_date.strftime("%Y-%m-%d"), Return_date =Return_date.strftime("%Y-%m-%d"))
        db.session.add(book_issue)
        db.session.commit()
        return redirect(url_for("issue_management"))
    else:
        return redirect(url_for('librarian_login')) 

@app.route("/book/<int:user_id>/access/deny/<int:book_id>")
def access_deny(user_id,book_id):
    if 'librarian_id' in session:
        BookRequestUser.query.filter_by(User_id=user_id,Book_id=book_id).delete()
        db.session.commit()
        return redirect(url_for("issue_management"))
    else:
        return redirect(url_for('librarian_login'))

@app.route("/librarian/search",methods=["GET","POST"])
def search_librarian():    
    section=Section.query.all()
    if request.method=="POST":
        query=request.form.get("value").lower()    
        books = Book.query.filter((Book.Name.ilike(f'%{query}%')) | (Book.Pages.ilike(f'%{query}%'))| (Authors.Name.ilike(f'%{query}%'))).all()    
    return render_template("search_lib.html",books=books,section=section)  

@app.route("/librarian/search/section/<int:section_id>")
def search_section_librarian(section_id):    
    books=Book.query.filter_by(Section_id=section_id).all()
    section=Section.query.get(section_id)
    sections=Section.query.all()
    return render_template("search_lib_section.html",books=books,section=section,sections=sections)

@app.route("/statistics")
def statistics():
    if "librarian_id" in session:
        users = Users.query.filter_by(Role="general").count()   
        books_issued=BookIssueUser.query.count()
        books_requested=BookRequestUser.query.count()        
        total_books=Book.query.count()
        total_sections=Section.query.count()
        wallet=Users.query.filter(Users.Wallet<40).count()
        sections = Section.query.all()
        book_counts = []
        for x in sections:
            book = Book.query.filter_by(Section_id=x.ID).count()
            book_counts.append((x.Name, book))
        section = [row[0] for row in book_counts]
        counts = [row[1] for row in book_counts]
        plt.figure(figsize=(8, 6))
        plt.bar(section, counts, color='steelblue') 
        plt.xlabel('Section')
        plt.ylabel('Book Count')
        plt.title('Number of Books in Each Section')
        plt.savefig('static/section_vs_book.png')
        plt.close()
        
        book_feedback = []
        books = Book.query.all()
        for x in books:
            ratings = UserFeedback.query.filter_by(Book_id=x.ID).all()
            r = 0.0
            c = 0
            for y in ratings:
                r += y.Overall_rating
                c += 1
            if c != 0:
                book_feedback.append((x.Name, r/c))
        books = [row[0] for row in book_feedback]
        rating = [row[1] for row in book_feedback]
        plt.figure(figsize=(8, 6))
        plt.bar(books, rating, color='skyblue') 
        plt.xlabel('Book')
        plt.ylabel('Average Overall Rating')
        plt.title('Average Overall rating of each Book')
        plt.savefig('static/book_vs_feedback.png')
        plt.close()

        return render_template("statistics.html", users=users,books_issued=books_issued,books_requested=books_requested,total_books=total_books,total_sections=total_sections,wallet=wallet,image1='static/section_vs_book.png', image2='static/book_vs_feedback.png')
    else:
        return redirect(url_for('librarian_login'))