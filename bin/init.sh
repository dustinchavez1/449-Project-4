#!/bin/sh
sqlite3 ./var/db/users/primary/fuse/database.db < ./share/users/users.sql
sqlite3 ./var/db/users/primary/fuse/database.db < ./share/users/roles.sql
sqlite3 ./var/db/users/primary/fuse/database.db < ./share/users/userRoles.sql

python ./share/enrollment/classes.py
python ./share/enrollment/enrollments.py
python ./share/enrollment/instructors.py
python ./share/enrollment/registrar.py
python ./share/enrollment/sections.py
python ./share/enrollment/students.py
python ./share/enrollment/enrollment_count.py
