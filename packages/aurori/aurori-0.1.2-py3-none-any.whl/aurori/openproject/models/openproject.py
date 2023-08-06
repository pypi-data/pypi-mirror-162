from aurori import db


class OpenProject(db.Model):
    __tablename__ = 'openproject'
    id = db.Column(db.Integer,
                   primary_key=True,
                   index=True,
                   autoincrement=True,
                   unique=True)
