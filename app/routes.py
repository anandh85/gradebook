from flask import render_template, redirect, request, url_for, flash, make_response
from . import app
from .models import db, Students, Roster, StudentClass, Assignments, Users
from sqlalchemy import func
from flask_login import login_user, current_user, login_required, logout_user

# Verify if user exists in the database
@app.login_manager.user_loader
def load_user(user_id):
    return Users.query.filter_by(username=user_id).first()

# Custom Error Handling
@app.errorhandler(401)
def error_handler(e):
    if (e.code == 401):
        return render_template('index.html', errmessage=e.name)
    else:
        return "Some other Error {}".format(e.code)

# Dummy Base URL for viewgrade
@app.route('/viewgrade/student_id/class_id')
def base_url():
    return "None"

# Dummy Base URL for editgrade
@app.route('/editgrade/student_id/class_id/assignment_id')
def base_edit_url():
    return "None"

# Dummy Base URL for viewstudentdetails
@app.route('/viewstudentdetails/stud_id')
def base_show_result_by_id():
    return "None"

# Dummy Base URL for studentdetailsbyroster
@app.route('/viewrostergrades/roster_id')
def base_show_result_by_roster_id():
    return "None"

# Home Page
@app.route('/')
def homepage():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))
    # return login page

# Login Page
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    user = load_user(request.form["username"])
    if user is None:
        return render_template("login_page.html", error=True)
    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for('homepage'))

# Logout
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Add New Assignment for a User in a Class
@app.route('/assignment/<int:studentid>/<int:classid>', methods=['GET'])
@login_required
def new_assignment(studentid, classid):
    if request.method == 'GET':
        return make_response(render_template('gradebook/addassignment.html', sid=studentid, cid=classid), 200)

# View Single Grade from a Single Class in Edit Mode
@app.route('/editgrade/<int:studentid>/<int:classid>/<int:id>', methods=['GET'])
@login_required
def edit_assignment_grade(studentid, classid, id):
    if request.method == 'GET':
        assignmentinfo = Assignments.query.filter(Assignments.id == id)
        for assignment in assignmentinfo:
            assignmentname = assignment.assignment_name
            assignmentgrade = assignment.grade
            return make_response(render_template('gradebook/editassignmentgrade.html', sid=studentid, cid=classid, assignmentid=id, name=assignmentname, grade=assignmentgrade), 200)

# Route to add a new Assignment
@app.route('/savegrade', methods=['POST'])
@login_required
def add_assignment():
    if request.method == 'POST':
        if request.form['submit'] == 'cancel':
            return redirect(url_for('view_gradebook', studentid=request.form['studentid'], classid=request.form['classid']))
        elif request.form['submit'] == 'save':
            newgrade = Assignments(student_id=request.form['studentid'], class_id=request.form['classid'],
                                   assignment_name=request.form['assignname'], grade=request.form['assigngrade'])
            db.session.add(newgrade)
            db.session.commit()
            return redirect(url_for('view_gradebook', studentid=request.form['studentid'], classid=request.form['classid']))

# Route to Update New assignment
@app.route('/updategrade', methods=['POST'])
@login_required
def update_assignment():
    if request.method == 'POST':
        if request.form['submit'] == 'cancel':
            return redirect(url_for('view_gradebook', studentid=request.form['studentid'], classid=request.form['classid']))
        elif request.form['submit'] == 'save':
            db.session.query(Assignments).filter(Assignments.id == request.form['assignmentid']).update(
                {'assignment_name': request.form['assignname'], 'grade': request.form['assigngrade']})
            db.session.commit()
            return redirect(url_for('view_gradebook', studentid=request.form['studentid'], classid=request.form['classid']))

# View Gradebook per Class for a Single User
@app.route('/viewgrade/<string:studentid>/<string:classid>', methods=['GET'])
@login_required
def view_gradebook(studentid, classid):
    studentinfo = Students.query.filter(Students.id == studentid)
    studentclassinfo = StudentClass.query.filter(
        StudentClass.id == classid)
    for classinfo in studentclassinfo:
        classname = classinfo.class_name
    for student in studentinfo:
        studentdetails = student
        rosterinfo = Roster.query.filter(
            Roster.id == student.roster_id)
    for roster in rosterinfo:
        rostername = roster.roster_name
    assignmentlist = Assignments.query.filter(
        Assignments.student_id == studentid, Assignments.class_id == classid)
    averagegrade = db.session.query(func.avg(Assignments.grade)).filter(
        Assignments.student_id == studentid, Assignments.class_id == classid)
    for avg in averagegrade:
        if avg[0] is not None:
            avggrade = avg[0]
        else:
            avggrade = 'N/A'
    return make_response(render_template('gradebook/studentgradebook.html', student=studentdetails, cid=classid, studentclass=classname, rosterdetails=rostername, assignmentinfo=assignmentlist, avggrade=avggrade), 200)

# Delete Assignment
@app.route('/deleteassignment', methods=['POST'])
@login_required
def delete_assignment():
    Assignments.query.filter(
        Assignments.id == request.form['assignmentid']).delete()
    db.session.commit()
    return redirect(url_for('view_gradebook', studentid=request.form['studentid'], classid=request.form['classid']))

# Route to Add a Student
@app.route('/addstudent', methods=['GET', 'POST'])
@login_required
def create_student_record():
    if request.method == 'POST':
        if request.form['submit'] == 'cancel':
            return redirect(url_for('homepage'))
        elif request.form['submit'] == 'submit':
            student = Students(first_name=request.form['fname'], last_name=request.form['lname'], student_id=request.form[
                'id'], email=request.form['email'], roster_id=request.form['rosteroptions'], class_id=request.form['classoptions'])
            db.session.add(student)
            db.session.commit()
            flash('Student record successfully created')
            return redirect(url_for('view_students_record'))
        else:
            flash("Error in Request Redirecting to Home Page")
            return redirect(url_for('homepage'))
    roster_list = Roster.query.all()
    class_list = StudentClass.query.all()
    return make_response(render_template('student/addstudent.html', rosterlist=roster_list, classlist=class_list), 200)

# Route to delete student record
@app.route('/deletestudent', methods=['POST'])
@login_required
def delete_student_record():
    Assignments.query.filter(
        Assignments.student_id == request.form['studentid'], Assignments.class_id == request.form['classid']).delete()
    Students.query.filter(
        Students.id == request.form['studentid'], Students.class_id == request.form['classid']).delete()
    db.session.commit()
    return redirect(url_for('view_students_record'))

# Route to View Student Record
@app.route('/viewstudents', methods=['GET'])
@login_required
def view_students_record():
    if request.method == 'GET':
        students = Students.query.order_by(Students.first_name).all()
        rosternames = []
        classnames = []
        for student in students:
            rosternames.append(Roster.query.filter(
                Roster.id == student.roster_id).all())
            classnames.append(StudentClass.query.filter(
                StudentClass.id == student.class_id).all())
        table_data = [[students[i], rosternames[i], classnames[i]]
                      for i in range(0, len(students))]
        return make_response(render_template('student/viewstudents.html', studentlist=table_data), 200)

# Display All the Student Scores by Student id
@app.route('/viewstudentdetails/<string:stud_id>', methods=['GET'])
@login_required
def show_student_details(stud_id):
    rosterdetails = []
    grades = []
    if request.method == 'GET':
        query1 = db.session.query(Students).filter(
            Students.student_id == stud_id)
        for student in query1:
            fullname = student.first_name + ' ' + student.last_name
            email = student.email
            studentid = student.student_id
            for assignments in student.students:
                grades.append(assignments.grade)
            rosterdetails.append({'studentclassname': student.studentclass.class_name,
                                  'studentroster': student.roster.roster_name,
                                  'assignments': student.students
                                  })
        rosterdetails = sorted(rosterdetails, key=lambda k: k['studentroster'])
        return make_response(render_template('student/studentdetails.html', fullname=fullname, email=email, studentid=studentid, studentlist=rosterdetails, averagegrade=sum(grades)/len(grades) if len(grades) != 0 else 'N/A'), 200)

# Display All the Student Scores by Roster
@app.route('/viewrostergrades/<string:r_id>', methods=['GET'])
@login_required
def show_student_grades_by_roster(r_id):
    rosterdetails = []
    grades = []
    if request.method == 'GET':
        query1 = db.session.query(Students).filter(
            Students.roster_id == r_id)
        for student in query1:
            grades.clear()
            for assignments in student.students:
                grades.append(assignments.grade)
            rostername = student.roster.roster_name
            rosterdetails.append({'studentname': student.first_name + ' ' + student.last_name,
                                  'studentclassname': student.studentclass.class_name,
                                  'grade': sum(grades)/len(grades) if len(grades) != 0 else 'N/A'
                                  })
        rosterdetails = sorted(rosterdetails, key=lambda k: k['studentname'])
        return make_response(render_template('student/studentdetailsbyroster.html',  studentlist=rosterdetails, roster_name=rostername), 200)
