PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS Roles;
CREATE TABLE Roles (
   id INTEGER PRIMARY KEY,
   name TEXT NOT NULL
);

INSERT INTO Roles(name) VALUES(
   'student'
);
INSERT INTO Roles(name) VALUES(
   'instructor'
);
INSERT INTO Roles(name) VALUES(
   'registrar'
);


COMMIT;
