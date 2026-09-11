"""
Hostel Room Booking and Fees Management System

A menu-driven console application to replace a paper ledger for tracking
hostel room bookings and student fee payments.

Author: Noah KUSAASIRA

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
"""

import json
import os
from datetime import datetime

DATA_FILE = "hostel_data.json"


# a) Data setup
def default_blocks():
    """
    Docstring: The function predefined hostel blocks. Each block maps room numbers to a dict holding
    the room's fixed capacity and the list of registration numbers of
    students currently occupying it.
    """
    blocks = {
        "BLOCK-A": {
            "ROOM1": {"capacity": 2, "occupants": []},
            "ROOM2": {"capacity": 2, "occupants": []},
            "ROOM3": {"capacity": 3, "occupants": []},
        },
        "BLOCK-B": {
            "ROOM1": {"capacity": 2, "occupants": []},
            "ROOM2": {"capacity": 2, "occupants": []},
        },
        "BLOCK-C": {
            "ROOM1": {"capacity": 2, "occupants": []},
            "ROOM2": {"capacity": 2, "occupants": []},
            "ROOM3": {"capacity": 3, "occupants": []},
            "ROOM4": {"capacity": 4, "occupants": []}
        }
    }
    return blocks


class HostelSystem:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.blocks = {}
        self.students = {}
        self._load_data()
        if not self.blocks:
            # First run, or the file was missing/unreadable -> seed defaults.
            self.blocks = default_blocks()

    # e) FILE PERSISTENCE
    def _load_data(self):
        """
        Docstring: The class method loads blocks/students from the json file.
        Any problem (missing file, empty file, corrupted JSON, unexpected structure) is handled gracefully:
        the system falls back to a fresh/default state instead of crashing.
        """
        if not os.path.exists(self.data_file):
            print(f"[Info] No existing data file found ('{self.data_file}'). "
                  f"Starting with a fresh system.")
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                raw = json.load(f)

            if not isinstance(raw, dict):
                raise ValueError("Data file does not contain the expected structure.")

            blocks = raw.get("blocks", {})
            students = raw.get("students", {})

            if not isinstance(blocks, dict) or not isinstance(students, dict):
                raise ValueError("Data file structure is invalid.")

            self.blocks = blocks
            self.students = students
            print(f"[Info] Loaded existing data from '{self.data_file}'.")

        except (json.JSONDecodeError, ValueError, TypeError, KeyError, AttributeError) as e:
            print(f"[Warning] Data file '{self.data_file}' appears to be "
                  f"damaged or in an unexpected format ({e}). "
                  f"Starting with a fresh system instead of crashing.")
            self.blocks = {}
            self.students = {}
        except OSError as e:
            print(f"[Warning] Could not read '{self.data_file}' ({e}). "
                  f"Starting with a fresh system.")
            self.blocks = {}
            self.students = {}

    def save_data(self):
        """
        Docstring: The class method stores the current state to a JSON file.
        """
        payload = {"blocks": self.blocks, "students": self.students}
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            return True
        except OSError as e:
            print(f"[Error] Could not save data: {e}")
            return False

    # Occupancy overview (used at startup and from the menu)
    def occupancy_overview(self):
        """
        Docstring: The class method prints a brief overview of current hostel block occupancy upon startup.
        """
        lines = []
        lines.append("=" * 55)
        lines.append("HOSTEL OCCUPANCY OVERVIEW")
        lines.append("=" * 55)
        grand_capacity = 0
        grand_occupied = 0
        for block_name in sorted(self.blocks):
            rooms = self.blocks[block_name]
            block_capacity = sum(r["capacity"] for r in rooms.values())
            block_occupied = sum(len(r["occupants"]) for r in rooms.values())
            grand_capacity += block_capacity
            grand_occupied += block_occupied
            lines.append(
                f"Block {block_name}: {block_occupied}/{block_capacity} "
                f"beds occupied across {len(rooms)} room(s)"
            )
        lines.append("-" * 55)
        lines.append(f"TOTAL: {grand_occupied}/{grand_capacity} beds occupied")
        lines.append("=" * 55)
        return "\n".join(lines)

    # b) STUDENT REGISTRATION AND ROOM ALLOCATION
    def allocate_student(self, reg_no, name, block_name, room_no, total_fee):
        """
        Docstring: The class method registers a new student and allocate them to a room, if space allows.
        Returns (success: bool, message: str).
        """
        reg_no = reg_no.strip().upper()
        block_name = block_name.strip().upper()
        room_no = str(room_no).strip()

        if reg_no in self.students:
            return False, (
                f"Registration number '{reg_no}' is already in use by "
                f"{self.students[reg_no]['name']}."
            )

        if block_name not in self.blocks:
            available = ", ".join(sorted(self.blocks))
            return False, f"Block '{block_name}' does not exist. Available blocks: {available}."

        rooms = self.blocks[block_name]
        if room_no not in rooms:
            available = ", ".join(sorted(rooms))
            return False, (
                f"Room '{room_no}' does not exist in Block {block_name}. "
                f"Available rooms: {available}."
            )

        room = rooms[room_no]
        if len(room["occupants"]) >= room["capacity"]:
            return False, (
                f"Room {room_no} in Block {block_name} is already full "
                f"({len(room['occupants'])}/{room['capacity']}). "
                f"Allocation rejected."
            )

        # All checks passed: create the student record and update occupancy.
        room["occupants"].append(reg_no)
        self.students[reg_no] = {
            "name": name.strip(),
            "reg_no": reg_no,
            "block": block_name,
            "room": room_no,
            "total_fee": round(float(total_fee), 2),
            "paid": 0.0,
            "balance": round(float(total_fee), 2),
            "payments": [],
        }
        return True, (
            f"{name.strip()} ({reg_no}) allocated to Room {room_no}, "
            f"Block {block_name}. Room now {len(room['occupants'])}/{room['capacity']} full."
        )

    # c) FEE PAYMENT RECORDING
    def record_payment(self, reg_no, amount):
        """
        Docstring: The class method records a full or partial payment against a student's account.
        Returns (success: bool, message: str).
        """
        reg_no = reg_no.strip().upper()
        if reg_no not in self.students:
            return False, f"No student found with registration number '{reg_no}'."

        if amount <= 0:
            return False, "Payment amount must be greater than zero."

        student = self.students[reg_no]
        student["paid"] = round(student["paid"] + amount, 2)
        student["balance"] = round(student["total_fee"] - student["paid"], 2)
        student["payments"].append({
            "amount": round(float(amount), 2),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        if student["balance"] <= 0:
            status = "Fees fully paid."
            if student["balance"] < 0:
                status += f" Overpaid by {abs(student['balance']):.2f}."
        else:
            status = f"Outstanding balance: {student['balance']:.2f}."

        return True, (
            f"Payment of {amount:.2f} recorded for {student['name']} "
            f"({reg_no}). {status}"
        )

    # d) SEARCH AND REPORTING
    def search_student(self, query):
        """
        Docstring: The class method searches by exact registration number or partial/full name (case-insensitive).
        """
        query = query.strip().upper()
        if not query:
            return []

        # Exact reg_no match first.
        if query in self.students:
            return [self.students[query]]

        # Otherwise search by name substring.
        matches = [s for s in self.students.values() if query in s["name"].upper()]
        return matches

    def block_report(self, block_name):
        """
        Docstring: The class method generates full occupancy report for a hostel block, room by room.
        """
        block_name = block_name.strip().upper()
        if block_name not in self.blocks:
            return f"Block '{block_name}' does not exist."

        rooms = self.blocks[block_name]
        lines = [f"OCCUPANCY REPORT - BLOCK {block_name}", "-" * 45]
        for room_no in sorted(rooms):
            room = rooms[room_no]
            lines.append(f"Room {room_no} ({len(room['occupants'])}/{room['capacity']}):")
            if room["occupants"]:
                for reg_no in room["occupants"]:
                    name = self.students.get(reg_no, {}).get("name", "Unknown")
                    lines.append(f"    - {name} ({reg_no})")
            else:
                lines.append("    (empty)")
        return "\n".join(lines)

    def all_blocks_report(self):
        return "\n\n".join(self.block_report(b) for b in sorted(self.blocks))

    def fee_defaulters(self, threshold):
        """
        Docstring: The class method lists students whose outstanding balance is above the given threshold.
        """
        defaulters = [s for s in self.students.values() if s["balance"] > threshold]
        defaulters.sort(key=lambda s: s["balance"], reverse=True)
        return defaulters


# f) MENU-DRIVEN DRIVER PROGRAMME
def get_nonempty_str(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def get_positive_float(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number (e.g. 150000 or 150000.50).")


def get_nonnegative_float(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value < 0:
                print("Please enter a number that is zero or greater.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")


def pause():
    input("\nPress Enter to return to the menu...")


def menu_register_allocate(system):
    print("\n--- Register Student & Allocate Room ---")
    reg_no = get_nonempty_str("Registration number: ")
    name = get_nonempty_str("Full name: ")
    print("Available blocks:", ", ".join(sorted(system.blocks)))
    block = get_nonempty_str("Block (e.g. A): ")
    print("Available rooms in that block:",
          ", ".join(sorted(system.blocks.get(block.strip().upper(), {}))) or "N/A")
    room = get_nonempty_str("Room number: ")
    total_fee = get_positive_float("Total fee owed for the term/semester: ")

    success, message = system.allocate_student(reg_no, name, block, room, total_fee)
    print(("\n[SUCCESS] " if success else "\n[REJECTED] ") + message)
    if success:
        system.save_data()


def menu_record_payment(system):
    print("\n--- Record Fee Payment ---")
    reg_no = get_nonempty_str("Student registration number: ")
    if reg_no.strip().upper() not in system.students:
        print(f"[REJECTED] No student found with registration number '{reg_no}'.")
        return
    student = system.students[reg_no.strip().upper()]
    print(f"Student: {student['name']} | Balance so far: {student['balance']:.2f}")
    amount = get_positive_float("Amount being paid now: ")

    success, message = system.record_payment(reg_no, amount)
    print(("\n[SUCCESS] " if success else "\n[REJECTED] ") + message)
    if success:
        system.save_data()


def print_student_details(student):
    print(f"Name        : {student['name']}")
    print(f"Reg. No.    : {student['reg_no']}")
    print(f"Block/Room  : {student['block']} / {student['room']}")
    print(f"Total Fee   : {student['total_fee']:.2f}")
    print(f"Paid So Far : {student['paid']:.2f}")
    print(f"Balance     : {student['balance']:.2f}")
    if student["payments"]:
        print("Payment history:")
        for p in student["payments"]:
            print(f"    - {p['date']}: {p['amount']:.2f}")
    else:
        print("Payment history: (no payments recorded yet)")


def menu_search(system):
    print("\n--- Search Student ---")
    query = get_nonempty_str("Enter name or registration number: ")
    results = system.search_student(query)
    if not results:
        print(f"No student found matching '{query}'.")
        return
    print(f"\n{len(results)} match(es) found:\n")
    for i, student in enumerate(results, start=1):
        print(f"[{i}]")
        print_student_details(student)
        print()


def menu_block_report(system):
    print("\n--- Block Occupancy Report ---")
    print("Available blocks:", ", ".join(sorted(system.blocks)), "| or type ALL")
    choice = get_nonempty_str("Block to report on: ").strip().upper()
    if choice == "ALL":
        print("\n" + system.all_blocks_report())
    else:
        print("\n" + system.block_report(choice))


def menu_defaulters(system):
    print("\n--- Fee Defaulters Report ---")
    threshold = get_nonnegative_float("Show students with balance ABOVE: ")
    defaulters = system.fee_defaulters(threshold)
    if not defaulters:
        print(f"\nNo students have an outstanding balance above {threshold:.2f}.")
        return
    print(f"\n{len(defaulters)} defaulter(s) found (balance > {threshold:.2f}):\n")
    for s in defaulters:
        print(f"  {s['name']} ({s['reg_no']}) - Block {s['block']} Room {s['room']} "
              f"- Owes {s['balance']:.2f}")


def print_menu():
    print("\n" + "=" * 55)
    print("HOSTEL ROOM BOOKING & FEES MANAGEMENT SYSTEM")
    print("=" * 55)
    print("1. View occupancy overview")
    print("2. Register a student & allocate a room")
    print("3. Record a fee payment")
    print("4. Search for a student")
    print("5. Generate block occupancy report")
    print("6. Generate fee defaulters report")
    print("7. Save data now")
    print("8. Exit")
    print("=" * 55)


def main():
    system = HostelSystem()
    print(system.occupancy_overview())

    while True:
        print_menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            print("\n" + system.occupancy_overview())
            pause()
        elif choice == "2":
            menu_register_allocate(system)
            pause()
        elif choice == "3":
            menu_record_payment(system)
            pause()
        elif choice == "4":
            menu_search(system)
            pause()
        elif choice == "5":
            menu_block_report(system)
            pause()
        elif choice == "6":
            menu_defaulters(system)
            pause()
        elif choice == "7":
            if system.save_data():
                print("\n[SUCCESS] Data saved to disk.")
            pause()
        elif choice == "8":
            if system.save_data():
                print("\nData saved. Goodbye!")
            else:
                print("\n[Warning] Exiting without confirmed save.")
            break
        else:
            print("\nInvalid choice. Please enter a number from 1 to 8.")
            pause()


if __name__ == '__main__':
    main()

