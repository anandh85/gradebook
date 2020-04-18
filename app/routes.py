from flask import render_template, redirect, request, url_for, flash
from . import app
from .models import db, Students, Roster, StudentClass, Assignments
from sqlalchemy import func

# Dummy Base URL
@app.route('/viewgrade/student_id/class_id')
def baseURL():
    return "None"


@app.route('/editgrade/student_id/class_id/assignment_id')
def baseEditURL():
    return "None"


@app.route('/viewstudentdetails/stud_id')
def baseShowResultbyId():
    return "None"

# Home Page
@app.route('/')
def homepage():
    return render_template('index.html')

# Add New Assignment for a User in a Class
@app.route('/assignment/<int:studentid>/<int:classid>', methods=['GET'])
def newassignment(studentid, classid):
    if request.method == 'GET':
        return render_template('gradebook/addassignment.html', sid=studentid, cid=classid)


# View Single Grade from a Single Class in Edit Mode
@app.route('/editgrade/<int:studentid>/<int:classid>/<int:id>', methods=['GET'])
def editassignmentgrade(studentid, classid, id):
    if request.method == 'GET':
        assignmentinfo = Assignments.query.filter(Assignments.id == id)
        for assignment in assignmentinfo:
            assignmentname = assignment.assignment_name
            assignmentgrade = assignment.grade
            return render_template('gradebook/editassignmentgrade.html', sid=studentid, cid=classid, assignmentid=id, name=assignmentname, grade=assignmentgrade)

# Route to add a new Assignment
@app.route('/savegrade', methods=['POST'])
def addassignment():
    if request.method == 'POST':
        if request.form['submit'] == 'cancel':
            return redirect(url_for('viewgradebook', studentid=request.form['studentid'], classid=request.form['classid']))
        elif request.form['submit'] == 'save':
            newgrade = Assignments(student_id=request.form['studentid'], class_id=request.form['classid'],
                                   assignment_name=request.form['assignname'], grade=request.form['assigngrade'])
            db.session.add(newgrade)
            db.session.commit()
            return redirect(url_for('viewgradebook', studentid=request.form['studentid'], classid=request.form['classid']))

# Route to Update New assignment
@app.route('/updategrade', methods=['POST'])
def updateassignment():
    if request.method == 'POST':
        if request.form['submit'] == 'cancel':
            return redirect(url_for('viewgradebook', studentid=request.form['studentid'], classid=request.form['classid']))
        elif request.form['submit'] == 'save':
            db.session.query(Assignments).filter(Assignments.id == request.form['assignmentid']).update(
                {'assignment_name': request.form['assignname'], 'grade': request.form['assigngrade']})
            db.session.commit()
            return redirect(url_for('viewgradebook', studentid=request.form['studentid'], classid=request.form['classid']))

# View Gradebook per Class for a Single User
@app.route('/viewgrade/<string:studentid>/<string:classid>', methods=['GET'])
def viewgradebook(studentid, classid):
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
    return render_template('gradebook/studentgradebook.html', student=studentdetails, cid=classid, studentclass=classname, rosterdetails=rostername, assignmentinfo=assignmentlist, avggrade=avggrade)

# Delete Assignment
@app.route('/deleteassignment', methods=['POST'])
def deleteassignment():
    Assignments.query.filter(
        Assignments.id == request.form['assignmentid']).delete()
    db.session.commit()
    return redirect(url_for('viewgradebook', studentid=request.form['studentid'], classid=request.form['classid']))


# Route to Add a Student
@app.route('/addstudent', methods=['GET', 'POST'])
def createstudentrecord():
    if request.method == 'POST':
        if request.form['submit'] == 'cancel':
            return redirect(url_for('homepage'))
        elif request.form['submit'] == 'submit':
            student = Students(first_name=request.form['fname'], last_name=request.form['lname'], student_id=request.form[
                'id'], email=request.form['email'], roster_id=request.form['rosteroptions'], class_id=request.form['classoptions'])
            db.session.add(student)
            db.session.commit()
            flash('Student record successfully created')
            return redirect(url_for('viewstudentsrecord'))
        else:
            flash("Error in Request Redirecting to Home Page")
            return redirect(url_for('homepage'))
    roster_list = Roster.query.all()
    class_list = StudentClass.query.all()
    return render_template('student/addstudent.html', rosterlist=roster_list, classlist=class_list)


# Route to delete student record
@app.route('/deletestudent', methods=['POST'])
def deletestudentrecord():
    Assignments.query.filter(
        Assignments.student_id == request.form['studentid'], Assignments.class_id == request.form['classid']).delete()
    Students.query.filter(
        Students.id == request.form['studentid'], Students.class_id == request.form['classid']).delete()
    db.session.commit()
    return redirect(url_for('viewstudentsrecord'))

# Route to View Student Record
@app.route('/viewstudents', methods=['GET'])
def viewstudentsrecord():
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
        return render_template('student/viewstudents.html', studentlist=table_data)

# Display All the Student Scores by Student id
@app.route('/viewstudentdetails/<string:stud_id>', methods=['GET'])
def showstudentdetails(stud_id):
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
        sorted(rosterdetails, key=lambda k: k['studentroster'])
        return render_template('student/studentdetails.html', fullname=fullname, email=email, studentid=studentid, studentlist=rosterdetails, averagegrade=sum(grades)/len(grades) if len(grades) != 0 else 'N/A')