"""
Research Lab Manager - Menu Driven Application
Python + MySQL implementation for CS 631 Project Deliverable 3.

Before running:
1. pip install mysql-connector-python
2. Run schema.sql and populate.sql in MySQL
3. Run: python app.py
"""

import mysql.connector
from mysql.connector import Error


def get_connection():
    print("Research Lab Manager - MySQL Login")
    host = input("Host [localhost]: ").strip() or "localhost"
    user = input("User [root]: ").strip() or "root"
    password = input("Password: ")
    database = input("Database [research_lab_manager]: ").strip() or "research_lab_manager"

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )


def print_rows(cursor, rows):
    if not rows:
        print("No records found.")
        return
    columns = [desc[0] for desc in cursor.description]
    widths = [len(col) for col in columns]
    for row in rows:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(str(value)) if value is not None else 4)

    line = " | ".join(col.ljust(widths[i]) for i, col in enumerate(columns))
    print(line)
    print("-" * len(line))
    for row in rows:
        print(" | ".join((str(value) if value is not None else "NULL").ljust(widths[i]) for i, value in enumerate(row)))


def run_select(conn, query, params=None):
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    rows = cursor.fetchall()
    print_rows(cursor, rows)
    cursor.close()


def run_change(conn, query, params=None):
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    print(f"Operation completed. Rows affected: {cursor.rowcount}")
    cursor.close()


def project_member_menu(conn):
    while True:
        print("\nPROJECT AND MEMBER MANAGEMENT")
        print("1. List all members")
        print("2. Add a lab member")
        print("3. Update a lab member name")
        print("4. Remove a lab member")
        print("5. List all projects")
        print("6. Add a project")
        print("7. Update project status/end date")
        print("8. Remove a project")
        print("9. Display the status of a project")
        print("10. Show members who worked on projects funded by a given grant")
        print("11. Show mentorship relations among members who worked on the same project")
        print("0. Back")

        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                run_select(conn, "SELECT MID, Name, Join_Date, Type, Mentor, M_SDate, M_EDate FROM LAB_MEMBER ORDER BY MID")

            elif choice == "2":
                mid = int(input("MID: "))
                name = input("Name: ")
                join_date = input("Join date (YYYY-MM-DD): ")
                mtype = input("Type (faculty/student/collaborator): ").lower()
                run_change(conn,
                    "INSERT INTO LAB_MEMBER (MID, Name, Join_Date, Type) VALUES (%s, %s, %s, %s)",
                    (mid, name, join_date, mtype)
                )

            elif choice == "3":
                mid = int(input("MID to update: "))
                name = input("New name: ")
                run_change(conn, "UPDATE LAB_MEMBER SET Name = %s WHERE MID = %s", (name, mid))

            elif choice == "4":
                mid = int(input("MID to remove: "))
                run_change(conn, "DELETE FROM LAB_MEMBER WHERE MID = %s", (mid,))

            elif choice == "5":
                run_select(conn, """
                    SELECT P.PID, P.Title, P.S_Date, P.E_Date, P.E_Duration, L.Name AS Leader
                    FROM PROJECT P JOIN LAB_MEMBER L ON P.Leader = L.MID
                    ORDER BY P.PID
                """)

            elif choice == "6":
                pid = int(input("PID: "))
                title = input("Title: ")
                sdate = input("Start date (YYYY-MM-DD): ")
                edate = input("End date (YYYY-MM-DD or blank): ").strip() or None
                duration = int(input("Expected duration/months: "))
                leader = int(input("Faculty leader MID: "))
                run_change(conn, """
                    INSERT INTO PROJECT (PID, Title, S_Date, E_Date, E_Duration, Leader)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (pid, title, sdate, edate, duration, leader))

            elif choice == "7":
                pid = int(input("PID to update: "))
                edate = input("New end date (YYYY-MM-DD or blank for active): ").strip() or None
                run_change(conn, "UPDATE PROJECT SET E_Date = %s WHERE PID = %s", (edate, pid))

            elif choice == "8":
                pid = int(input("PID to remove: "))
                run_change(conn, "DELETE FROM PROJECT WHERE PID = %s", (pid,))

            elif choice == "9":
                pid = int(input("PID: "))
                run_select(conn, """
                    SELECT PID, Title,
                           CASE WHEN E_Date IS NULL THEN 'active' ELSE 'completed' END AS Project_Status,
                           S_Date, E_Date, E_Duration
                    FROM PROJECT
                    WHERE PID = %s
                """, (pid,))

            elif choice == "10":
                gid = int(input("Grant ID: "))
                run_select(conn, """
                    SELECT DISTINCT LM.MID, LM.Name, LM.Type, P.PID, P.Title, G.GID, G.Agency
                    FROM GRANT_TBL G
                    JOIN PROJECT P ON G.PID = P.PID
                    JOIN WORKS W ON P.PID = W.PID
                    JOIN LAB_MEMBER LM ON W.MID = LM.MID
                    WHERE G.GID = %s
                    ORDER BY LM.Name
                """, (gid,))

            elif choice == "11":
                pid = int(input("Project ID: "))
                run_select(conn, """
                    SELECT P.PID, P.Title,
                           Mentor.Name AS Mentor_Name,
                           Mentee.Name AS Mentee_Name,
                           Mentee.M_SDate,
                           Mentee.M_EDate
                    FROM PROJECT P
                    JOIN WORKS W1 ON P.PID = W1.PID
                    JOIN LAB_MEMBER Mentee ON W1.MID = Mentee.MID
                    JOIN LAB_MEMBER Mentor ON Mentee.Mentor = Mentor.MID
                    JOIN WORKS W2 ON W2.PID = P.PID AND W2.MID = Mentor.MID
                    WHERE P.PID = %s
                    ORDER BY Mentor.Name, Mentee.Name
                """, (pid,))

            elif choice == "0":
                return
            else:
                print("Invalid option.")
        except Error as e:
            print("Database error:", e)
        except ValueError:
            print("Invalid input type.")


def equipment_menu(conn):
    while True:
        print("\nEQUIPMENT USAGE TRACKING")
        print("1. List equipment")
        print("2. Add equipment")
        print("3. Update equipment name/manual")
        print("4. Remove equipment")
        print("5. List equipment usage")
        print("6. Add equipment usage")
        print("7. Update equipment usage end date")
        print("8. Remove equipment usage")
        print("9. Show status of a piece of equipment")
        print("10. Show members currently using a given piece of equipment and their projects")
        print("0. Back")

        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                run_select(conn, "SELECT EID, E_Type, E_Name, Manual FROM EQUIPMENT ORDER BY EID")

            elif choice == "2":
                eid = int(input("EID: "))
                etype = input("Equipment type: ")
                ename = input("Equipment name: ")
                manual = input("Manual/reference: ")
                run_change(conn,
                    "INSERT INTO EQUIPMENT (EID, E_Type, E_Name, Manual) VALUES (%s, %s, %s, %s)",
                    (eid, etype, ename, manual)
                )

            elif choice == "3":
                eid = int(input("EID to update: "))
                ename = input("New equipment name: ")
                manual = input("New manual/reference: ")
                run_change(conn, "UPDATE EQUIPMENT SET E_Name = %s, Manual = %s WHERE EID = %s",
                           (ename, manual, eid))

            elif choice == "4":
                eid = int(input("EID to remove: "))
                run_change(conn, "DELETE FROM EQUIPMENT WHERE EID = %s", (eid,))

            elif choice == "5":
                run_select(conn, """
                    SELECT U.MID, LM.Name, U.DID, E.E_Name, U.S_Date, U.E_Date, U.Purpose
                    FROM USES U
                    JOIN LAB_MEMBER LM ON U.MID = LM.MID
                    JOIN EQUIPMENT E ON U.EID = E.EID
                    ORDER BY U.S_Date DESC
                """)

            elif choice == "6":
                mid = int(input("MID: "))
                did = int(input("DID: "))
                eid = int(input("EID: "))
                sdate = input("Start date (YYYY-MM-DD): ")
                edate = input("End date (YYYY-MM-DD or blank): ").strip() or None
                purpose = input("Purpose: ")

                # Application-level check for max 3 simultaneous current users.
                if edate is None:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT COUNT(*) FROM USES
                        WHERE DID = %s AND E_Date IS NULL
                    """, (did,))
                    active_count = cursor.fetchone()[0]
                    cursor.close()
                    if active_count >= 3:
                        print("Cannot add usage: this device already has 3 active users.")
                        continue

                run_change(conn, """
                    INSERT INTO USES (MID, DID, EID, S_Date, E_Date, Purpose)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (mid, did, eid, sdate, edate, purpose))

            elif choice == "7":
                mid = int(input("MID: "))
                did = int(input("DID: "))
                sdate = input("Usage start date (YYYY-MM-DD): ")
                edate = input("New end date (YYYY-MM-DD): ")
                run_change(conn, """
                    UPDATE USES SET E_Date = %s
                    WHERE MID = %s AND DID = %s AND S_Date = %s
                """, (edate, mid, did, sdate))

            elif choice == "8":
                mid = int(input("MID: "))
                did = int(input("DID: "))
                sdate = input("Usage start date (YYYY-MM-DD): ")
                run_change(conn, "DELETE FROM USES WHERE MID = %s AND DID = %s AND S_Date = %s",
                           (mid, did, sdate))

            elif choice == "9":
                eid = int(input("EID: "))
                run_select(conn, """
                    SELECT E.EID, E.E_Name, E.E_Type, D.DID, D.Status
                    FROM EQUIPMENT E
                    JOIN DEVICE D ON E.EID = D.EID
                    WHERE E.EID = %s
                    ORDER BY D.DID
                """, (eid,))

            elif choice == "10":
                eid = int(input("EID: "))
                run_select(conn, """
                    SELECT DISTINCT LM.MID, LM.Name, D.DID, E.E_Name, P.PID, P.Title AS Project_Title
                    FROM USES U
                    JOIN LAB_MEMBER LM ON U.MID = LM.MID
                    JOIN DEVICE D ON U.DID = D.DID
                    JOIN EQUIPMENT E ON U.EID = E.EID
                    LEFT JOIN WORKS W ON LM.MID = W.MID
                    LEFT JOIN PROJECT P ON W.PID = P.PID
                    WHERE U.EID = %s AND U.E_Date IS NULL
                    ORDER BY LM.Name, P.PID
                """, (eid,))

            elif choice == "0":
                return
            else:
                print("Invalid option.")
        except Error as e:
            print("Database error:", e)
        except ValueError:
            print("Invalid input type.")


def reporting_menu(conn):
    while True:
        print("\nGRANT AND PUBLICATION REPORTING")
        print("1. Top 5 projects by total grant funding")
        print("2. Mentor(s) whose mentees produced the largest number of publications")
        print("3. Total student publications per major and publication year")
        print("4. Given date X, projects ended before X and number of grants")
        print("5. Three most productive years for student publications")
        print("0. Back")

        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                run_select(conn, """
                    SELECT P.PID, P.Title, SUM(G.Budget) AS Total_Funding
                    FROM PROJECT P
                    JOIN GRANT_TBL G ON P.PID = G.PID
                    GROUP BY P.PID, P.Title
                    ORDER BY Total_Funding DESC
                    LIMIT 5
                """)

            elif choice == "2":
                run_select(conn, """
                    WITH MentorPubCounts AS (
                        SELECT Mentor.MID AS Mentor_ID,
                               Mentor.Name AS Mentor_Name,
                               COUNT(DISTINCT Pub.PubID) AS Publication_Count
                        FROM LAB_MEMBER Mentee
                        JOIN LAB_MEMBER Mentor ON Mentee.Mentor = Mentor.MID
                        JOIN PUBLISHES Pub ON Mentee.MID = Pub.MID
                        GROUP BY Mentor.MID, Mentor.Name
                    ),
                    MaxCount AS (
                        SELECT MAX(Publication_Count) AS Max_Publications
                        FROM MentorPubCounts
                    )
                    SELECT Mentor_ID, Mentor_Name, Publication_Count
                    FROM MentorPubCounts
                    WHERE Publication_Count = (SELECT Max_Publications FROM MaxCount)
                """)

            elif choice == "3":
                run_select(conn, """
                    SELECT S.Major,
                           YEAR(P.Date) AS Publication_Year,
                           COUNT(DISTINCT P.PubID) AS Total_Student_Publications
                    FROM STUDENT S
                    JOIN PUBLISHES PB ON S.MID = PB.MID
                    JOIN PUBLICATION P ON PB.PubID = P.PubID
                    GROUP BY S.Major, YEAR(P.Date)
                    ORDER BY S.Major, Publication_Year
                """)

            elif choice == "4":
                date_x = input("Enter date X (YYYY-MM-DD): ")
                run_select(conn, """
                    SELECT P.PID, P.Title, P.E_Date, COUNT(G.GID) AS Number_Of_Grants
                    FROM PROJECT P
                    LEFT JOIN GRANT_TBL G ON P.PID = G.PID
                    WHERE P.E_Date IS NOT NULL AND P.E_Date < %s
                    GROUP BY P.PID, P.Title, P.E_Date
                    ORDER BY P.E_Date
                """, (date_x,))

            elif choice == "5":
                run_select(conn, """
                    SELECT YEAR(P.Date) AS Publication_Year,
                           COUNT(DISTINCT P.PubID) AS Student_Publication_Count
                    FROM STUDENT S
                    JOIN PUBLISHES PB ON S.MID = PB.MID
                    JOIN PUBLICATION P ON PB.PubID = P.PubID
                    GROUP BY YEAR(P.Date)
                    ORDER BY Student_Publication_Count DESC, Publication_Year DESC
                    LIMIT 3
                """)

            elif choice == "0":
                return
            else:
                print("Invalid option.")
        except Error as e:
            print("Database error:", e)


def main():
    try:
        conn = get_connection()
        print("Connected successfully.")

        while True:
            print("\nMAIN MENU")
            print("1. Project and Member Management")
            print("2. Equipment Usage Tracking")
            print("3. Grant and Publication Reporting")
            print("0. Exit")

            choice = input("Choose: ").strip()
            if choice == "1":
                project_member_menu(conn)
            elif choice == "2":
                equipment_menu(conn)
            elif choice == "3":
                reporting_menu(conn)
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print("Invalid option.")

        conn.close()

    except Error as e:
        print("Could not connect to database:", e)


if __name__ == "__main__":
    main()
