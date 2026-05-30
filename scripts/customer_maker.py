import sqlite3


class Customer:
    def __init__(self):
        self.connection = sqlite3.connect("databases/test.db")
        self.cursor = self.connection.cursor()

        # make a table with commend
        # create table if not exist Customer
        # customer will have 
        # id, name,age_group,location,special infoamtion
        msg = """Create table if not exists Customer(
        id integer primary key autoincrement,
        name TEXT,
        age_group TEXT,
        location TEXT,
        special_info TEXT
        )"""
        self.cursor.execute(msg)
        self.connection.commit()

    def add_data(self,name,age_group,location,sp_in):
        msg = """insert into Customer (name,age_group,location,special_info)
        values (?,?,?,?)"""
        data = (name,age_group,location,sp_in)
        self.cursor.execute(msg,data)
        self.connection.commit()


c = Customer()
c.add_data("apple","50-60","town","no")
c.add_data("pinapple", "18-40", "klön", "cool")


    