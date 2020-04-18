from app import app
from app import db
from flask_migrate import Migrate
from sqlalchemy.orm import relationship
migrate = Migrate(app, db)


class StudentClass(db.Model):
    __tablename__ = "student_class"
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), nullable=False)


class Roster(db.Model):
    __tablename__ = "roster"
    id = db.Column(db.Integer, primary_key=True)
    roster_name = db.Column(db.String(100), nullable=False)


class Students(db.Model):

    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    roster_id = db.Column(db.Integer, db.ForeignKey('roster.id'))
    roster = relationship("Roster", backref="roster")
    class_id = db.Column(db.Integer, db.ForeignKey('student_class.id'))
    studentclass = relationship(
        "StudentClass", backref="student_class")


class Assignments(db.Model):
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    student = relationship(
        "Students", backref="students")
    class_id = db.Column(db.Integer, db.ForeignKey('student_class.id'))
    assignment_name = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.Float(precision='32,2'), nullable=True)
