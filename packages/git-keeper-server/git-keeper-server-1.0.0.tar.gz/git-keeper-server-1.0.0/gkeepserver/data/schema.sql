DROP TABLE IF EXISTS user;
CREATE TABLE user(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT,
  username TEXT,
  role TEXT,
  first_name TEXT,
  last_name TEXT,
  CONSTRAINT unique_username UNIQUE(email),
  CONSTRAINT unique_username UNIQUE(username)
);

DROP TABLE IF EXISTS admin;
CREATE TABLE admin(
  email TEXT,
  FOREIGN KEY(email) REFERENCES user(email)
);

DROP TABLE IF EXISTS class;
CREATE TABLE class(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  faculty_id INTEGER,
  CONSTRAINT unique_for_faculty UNIQUE(name, faculty_id),
  FOREIGN KEY(faculty_id) REFERENCES user(id)
);

DROP TABLE IF EXISTS class_student;
CREATE TABLE class_student(
  class_id INTEGER,
  student_id INTEGER,
  FOREIGN KEY(class_id) REFERENCES class(id),
  FOREIGN KEY(student_id) REFERENCES user(id)
);
