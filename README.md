Hostel Room Booking and Fees Management System

A menu-driven console application to replace a paper ledger for tracking
hostel room bookings and student fee payments.

Author: Moses Kyegombe

Option 1: Hostel Room Booking and Fees Management System
Your university’s hostel warden currently tracks room bookings and fee payments using a paper ledger, which is slow
and error-prone. Your group has been asked to build a Python system to replace it.
a) Data setup
Predefine at least three hostel blocks, each with a fixed number of rooms and a maximum capacity per room, using a
suitable data structure. When the programme starts, print a brief occupancy overview.
b) Student registration and room allocation
Allow a new student to be allocated to a specified room only if space remains in it. Reject the allocation with a
clear explanation if the room is already full and correctly update the room’s current occupancy when an
allocation succeeds.
c) Fee payment recording
Allow full or partial fee payments to be recorded against a student’s account. Track and correctly update the
outstanding balance across multiple payments made over time for the same student.
d) Search and reporting
Allow a student to be searched for by name or registration number. Generate a full occupancy report for each
hostel block and generate a list of “fee defaulters”, meaning students whose outstanding balance is above a
given threshold.
e) File persistence
Save student, room and payment records to file so that data survives between runs and reload this data
automatically when the programme starts. Handle a missing or damaged file gracefully rather than crashing.
f) Menu-driven driver programme
Bring every module above together behind one well-organised, looping menu that a hostel warden with no programming
background could realistically operate, with input validated throughout.
