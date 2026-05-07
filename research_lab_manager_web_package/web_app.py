from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'research-lab-manager-demo-key'


def get_db_config():
    return {
        'host': session.get('db_host', 'localhost'),
        'user': session.get('db_user', 'root'),
        'password': session.get('db_password', ''),
        'database': session.get('db_name', 'research_lab_manager'),
    }


def get_conn():
    return mysql.connector.connect(**get_db_config())


def fetch_all(sql, params=None):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()


def execute(sql, params=None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
    finally:
        cur.close()
        conn.close()


def safe_int(value):
    return int(value) if value not in (None, '') else None


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['db_host'] = request.form.get('host') or 'localhost'
        session['db_user'] = request.form.get('user') or 'root'
        session['db_password'] = request.form.get('password') or ''
        session['db_name'] = request.form.get('database') or 'research_lab_manager'
        try:
            conn = get_conn()
            conn.close()
            flash('Database connection successful.', 'success')
            return redirect(url_for('dashboard'))
        except Error as e:
            flash(f'Connection failed: {e}', 'error')
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/members')
@app.route('/members')
def members():
    search = request.args.get('search', '').strip()
    if search:
        rows = fetch_all(
            'SELECT MID, Name, Join_Date, Type, Mentor, M_SDate, M_EDate FROM LAB_MEMBER WHERE MID LIKE %s OR Name LIKE %s ORDER BY MID',
            (f'%{search}%', f'%{search}%')
        )
    else:
        rows = fetch_all('SELECT MID, Name, Join_Date, Type, Mentor, M_SDate, M_EDate FROM LAB_MEMBER ORDER BY MID')
    return render_template('members.html', rows=rows, search=search)


@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        try:
            execute('INSERT INTO LAB_MEMBER (MID, Name, Join_Date, Type, Mentor, M_SDate, M_EDate) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                    (safe_int(request.form['mid']), request.form['name'], request.form['join_date'], request.form['type'], safe_int(request.form.get('mentor')), request.form.get('m_sdate') or None, request.form.get('m_edate') or None))
            member_type = request.form['type']
            mid = safe_int(request.form['mid'])
            if member_type == 'faculty':
                execute('INSERT INTO FACULTY (MID, Department) VALUES (%s,%s)', (mid, request.form.get('department') or 'Not specified'))
            elif member_type == 'student':
                execute('INSERT INTO STUDENT (MID, SID, Level, Major) VALUES (%s,%s,%s,%s)', (mid, request.form.get('sid'), request.form.get('level'), request.form.get('major')))
            elif member_type == 'collaborator':
                execute('INSERT INTO COLLABORATOR (MID, Affiliation, CV) VALUES (%s,%s,%s)', (mid, request.form.get('affiliation'), request.form.get('cv')))
            flash('Member added.', 'success')
            return redirect(url_for('members'))
        except Error as e:
            flash(f'Add member failed: {e}', 'error')
    return render_template('member_form.html', action='Add')


@app.route('/members/<int:mid>/edit', methods=['GET', 'POST'])
def edit_member(mid):
    if request.method == 'POST':
        try:
            execute('UPDATE LAB_MEMBER SET Name=%s, Join_Date=%s, Type=%s, Mentor=%s, M_SDate=%s, M_EDate=%s WHERE MID=%s',
                    (request.form['name'], request.form['join_date'], request.form['type'], safe_int(request.form.get('mentor')), request.form.get('m_sdate') or None, request.form.get('m_edate') or None, mid))
            flash('Member updated.', 'success')
            return redirect(url_for('members'))
        except Error as e:
            flash(f'Update failed: {e}', 'error')
    row = fetch_all('SELECT * FROM LAB_MEMBER WHERE MID=%s', (mid,))[0]
    return render_template('member_form.html', action='Edit', row=row)


@app.route('/members/<int:mid>/delete', methods=['POST'])
def delete_member(mid):
    try:
        execute('DELETE FROM LAB_MEMBER WHERE MID=%s', (mid,))
        flash('Member removed.', 'success')
    except Error as e:
        flash(f'Remove failed: {e}', 'error')
    return redirect(url_for('members'))


@app.route('/projects')
def projects():
    search = request.args.get('search', '').strip()
    if search:
        rows = fetch_all('''SELECT p.PID, p.Title, p.S_Date, p.E_Date, p.E_Duration, p.Leader, lm.Name AS Leader_Name
                            FROM PROJECT p JOIN FACULTY f ON p.Leader=f.MID JOIN LAB_MEMBER lm ON f.MID=lm.MID
                            WHERE p.PID LIKE %s OR p.Title LIKE %s
                            ORDER BY p.PID''', (f'%{search}%', f'%{search}%'))
    else:
        rows = fetch_all('''SELECT p.PID, p.Title, p.S_Date, p.E_Date, p.E_Duration, p.Leader, lm.Name AS Leader_Name
                            FROM PROJECT p JOIN FACULTY f ON p.Leader=f.MID JOIN LAB_MEMBER lm ON f.MID=lm.MID ORDER BY p.PID''')
    return render_template('projects.html', rows=rows, search=search)


@app.route('/projects/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        try:
            execute('INSERT INTO PROJECT (PID, Title, S_Date, E_Date, E_Duration, Leader) VALUES (%s,%s,%s,%s,%s,%s)',
                    (safe_int(request.form['pid']), request.form['title'], request.form['s_date'], request.form.get('e_date') or None, safe_int(request.form['duration']), safe_int(request.form['leader'])))
            flash('Project added.', 'success')
            return redirect(url_for('projects'))
        except Error as e:
            flash(f'Add project failed: {e}', 'error')
    faculty = fetch_all('SELECT f.MID, lm.Name FROM FACULTY f JOIN LAB_MEMBER lm ON f.MID=lm.MID ORDER BY lm.Name')
    return render_template('project_form.html', action='Add', faculty=faculty)


@app.route('/projects/<int:pid>/edit', methods=['GET', 'POST'])
def edit_project(pid):
    if request.method == 'POST':
        try:
            execute('UPDATE PROJECT SET Title=%s, S_Date=%s, E_Date=%s, E_Duration=%s, Leader=%s WHERE PID=%s',
                    (request.form['title'], request.form['s_date'], request.form.get('e_date') or None, safe_int(request.form['duration']), safe_int(request.form['leader']), pid))
            flash('Project updated.', 'success')
            return redirect(url_for('projects'))
        except Error as e:
            flash(f'Update project failed: {e}', 'error')
    row = fetch_all('SELECT * FROM PROJECT WHERE PID=%s', (pid,))[0]
    faculty = fetch_all('SELECT f.MID, lm.Name FROM FACULTY f JOIN LAB_MEMBER lm ON f.MID=lm.MID ORDER BY lm.Name')
    return render_template('project_form.html', action='Edit', row=row, faculty=faculty)


@app.route('/projects/<int:pid>/delete', methods=['POST'])
def delete_project(pid):
    try:
        execute('DELETE FROM PROJECT WHERE PID=%s', (pid,))
        flash('Project removed.', 'success')
    except Error as e:
        flash(f'Remove project failed: {e}', 'error')
    return redirect(url_for('projects'))


@app.route('/project-status', methods=['GET', 'POST'])
def project_status():
    rows = []
    if request.method == 'POST':
        pid = safe_int(request.form['pid'])
        rows = fetch_all('''SELECT p.PID, p.Title,
                 CASE WHEN p.E_Date IS NULL THEN 'active'
                      WHEN p.E_Date < CURDATE() THEN 'completed'
                      ELSE 'active'
                 END AS Status,
                 p.S_Date, p.E_Date, lm.Name AS Leader_Name
                 FROM PROJECT p JOIN LAB_MEMBER lm ON p.Leader = lm.MID WHERE p.PID=%s''', (pid,))
    return render_template('report.html', title='Project Status', rows=rows, form='project_status')


@app.route('/members-by-grant', methods=['GET', 'POST'])
def members_by_grant():
    rows = []
    if request.method == 'POST':
        gid = safe_int(request.form['gid'])
        rows = fetch_all('''SELECT DISTINCT g.GID, g.Agency, p.PID, p.Title AS Project_Title, lm.MID, lm.Name, w.Role, w.Hours
                            FROM GRANT_TBL g JOIN PROJECT p ON g.PID=p.PID JOIN WORKS w ON p.PID=w.PID JOIN LAB_MEMBER lm ON w.MID=lm.MID
                            WHERE g.GID=%s ORDER BY lm.Name''', (gid,))
    return render_template('report.html', title='Members Who Worked on Projects Funded by Grant', rows=rows, form='grant_members')


@app.route('/mentorship-same-project')
def mentorship_same_project():
    rows = fetch_all('''SELECT DISTINCT p.PID, p.Title AS Project_Title,
                               mentor.Name AS Mentor_Name, mentee.Name AS Mentee_Name,
                               mentee.M_SDate, mentee.M_EDate
                        FROM LAB_MEMBER mentee
                        JOIN LAB_MEMBER mentor ON mentee.Mentor = mentor.MID
                        JOIN WORKS wm ON mentor.MID = wm.MID
                        JOIN WORKS we ON mentee.MID = we.MID AND wm.PID = we.PID
                        JOIN PROJECT p ON wm.PID = p.PID
                        ORDER BY p.PID, Mentor_Name, Mentee_Name''')
    return render_template('report.html', title='Mentorship Relations Among Members on the Same Project', rows=rows)


@app.route('/equipment')
def equipment():
    search = request.args.get('search', '').strip()
    if search:
        rows = fetch_all(
            'SELECT EID, E_Type, E_Name, Manual_Text FROM EQUIPMENT WHERE EID LIKE %s OR E_Name LIKE %s OR E_Type LIKE %s ORDER BY EID',
            (f'%{search}%', f'%{search}%', f'%{search}%')
        )
    else:
        rows = fetch_all('SELECT EID, E_Type, E_Name, Manual_Text FROM EQUIPMENT ORDER BY EID')
    return render_template('equipment.html', rows=rows, search=search)


@app.route('/equipment/add', methods=['GET', 'POST'])
def add_equipment():
    if request.method == 'POST':
        try:
            execute('INSERT INTO EQUIPMENT (EID, E_Type, E_Name, Manual_Text) VALUES (%s,%s,%s,%s)',
                    (safe_int(request.form['eid']), request.form['etype'], request.form['ename'], request.form.get('manual')))
            flash('Equipment added.', 'success')
            return redirect(url_for('equipment'))
        except Error as e:
            flash(f'Add equipment failed: {e}', 'error')
    return render_template('equipment_form.html', action='Add')


@app.route('/equipment/<int:eid>/edit', methods=['GET', 'POST'])
def edit_equipment(eid):
    if request.method == 'POST':
        try:
            execute('UPDATE EQUIPMENT SET E_Type=%s, E_Name=%s, Manual_Text=%s WHERE EID=%s',
                    (request.form['etype'], request.form['ename'], request.form.get('manual'), eid))
            flash('Equipment updated.', 'success')
            return redirect(url_for('equipment'))
        except Error as e:
            flash(f'Update equipment failed: {e}', 'error')
    row = fetch_all('SELECT * FROM EQUIPMENT WHERE EID=%s', (eid,))[0]
    return render_template('equipment_form.html', action='Edit', row=row)


@app.route('/equipment/<int:eid>/delete', methods=['POST'])
def delete_equipment(eid):
    try:
        execute('DELETE FROM EQUIPMENT WHERE EID=%s', (eid,))
        flash('Equipment removed.', 'success')
    except Error as e:
        flash(f'Remove equipment failed: {e}', 'error')
    return redirect(url_for('equipment'))


@app.route('/usage')
def usage():
    search = request.args.get('search', '').strip()
    if search:
        rows = fetch_all('''SELECT u.MID, lm.Name, u.DID, u.EID, e.E_Name, u.S_Date, u.E_Date, u.Purpose
                            FROM USES u JOIN LAB_MEMBER lm ON u.MID=lm.MID JOIN EQUIPMENT e ON u.EID=e.EID
                            WHERE lm.Name LIKE %s OR e.E_Name LIKE %s OR u.MID LIKE %s
                            ORDER BY u.S_Date DESC''', (f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        rows = fetch_all('''SELECT u.MID, lm.Name, u.DID, u.EID, e.E_Name, u.S_Date, u.E_Date, u.Purpose
                            FROM USES u JOIN LAB_MEMBER lm ON u.MID=lm.MID JOIN EQUIPMENT e ON u.EID=e.EID
                            ORDER BY u.S_Date DESC''')
    return render_template('usage.html', rows=rows, search=search)


@app.route('/usage/add', methods=['GET', 'POST'])
def add_usage():
    if request.method == 'POST':
        try:
            execute('INSERT INTO USES (MID, DID, EID, S_Date, E_Date, Purpose) VALUES (%s,%s,%s,%s,%s,%s)',
                    (safe_int(request.form['mid']), safe_int(request.form['did']), safe_int(request.form['eid']), request.form['s_date'], request.form.get('e_date') or None, request.form['purpose']))
            flash('Usage added.', 'success')
            return redirect(url_for('usage'))
        except Error as e:
            flash(f'Add usage failed: {e}', 'error')
    return render_template('usage_form.html')


@app.route('/usage/delete', methods=['POST'])
def delete_usage():
    try:
        execute('DELETE FROM USES WHERE MID=%s AND DID=%s AND S_Date=%s', (safe_int(request.form['mid']), safe_int(request.form['did']), request.form['s_date']))
        flash('Usage removed.', 'success')
    except Error as e:
        flash(f'Remove usage failed: {e}', 'error')
    return redirect(url_for('usage'))


@app.route('/equipment-status', methods=['GET', 'POST'])
def equipment_status():
    rows = []
    if request.method == 'POST':
        eid = safe_int(request.form['eid'])
        rows = fetch_all('''SELECT e.EID, e.E_Name, d.DID, d.Status, d.P_Date
                            FROM EQUIPMENT e JOIN DEVICE d ON e.EID=d.EID
                            WHERE e.EID=%s ORDER BY d.DID''', (eid,))
    return render_template('report.html', title='Equipment Status', rows=rows, form='equipment_status')


@app.route('/current-users', methods=['GET', 'POST'])
def current_users():
    rows = []
    if request.method == 'POST':
        eid = safe_int(request.form['eid'])
        rows = fetch_all('''SELECT e.EID, e.E_Name, d.DID, lm.MID, lm.Name, p.PID, p.Title AS Project_Title, w.Role
                            FROM EQUIPMENT e
                            JOIN DEVICE d ON e.EID=d.EID
                            JOIN USES u ON d.DID=u.DID AND u.E_Date IS NULL
                            JOIN LAB_MEMBER lm ON u.MID=lm.MID
                            LEFT JOIN WORKS w ON lm.MID=w.MID
                            LEFT JOIN PROJECT p ON w.PID=p.PID
                            WHERE e.EID=%s
                            ORDER BY d.DID, lm.Name, p.PID''', (eid,))
    return render_template('report.html', title='Members Currently Using Equipment and Their Projects', rows=rows, form='current_users')


@app.route('/reports')
def reports():
    return render_template('reports.html')


@app.route('/reports/top-funded')
def top_funded():
    rows = fetch_all('''SELECT p.PID, p.Title, SUM(g.Budget) AS Total_Funding
                        FROM PROJECT p JOIN GRANT_TBL g ON p.PID=g.PID
                        GROUP BY p.PID, p.Title
                        ORDER BY Total_Funding DESC LIMIT 5''')
    return render_template('report.html', title='Top 5 Projects by Total Grant Funding', rows=rows)


@app.route('/reports/mentor-publications')
def mentor_publications():
    rows = fetch_all('''SELECT mentor.MID AS Mentor_MID, mentor.Name AS Mentor_Name, COUNT(DISTINCT pub.PubID) AS Mentee_Publication_Count
                        FROM LAB_MEMBER mentor
                        JOIN LAB_MEMBER mentee ON mentee.Mentor = mentor.MID
                        JOIN PUBLISHES pub ON mentee.MID = pub.MID
                        GROUP BY mentor.MID, mentor.Name
                        HAVING COUNT(DISTINCT pub.PubID) = (
                            SELECT MAX(pub_count) FROM (
                                SELECT COUNT(DISTINCT p2.PubID) AS pub_count
                                FROM LAB_MEMBER m2
                                JOIN LAB_MEMBER t2 ON t2.Mentor = m2.MID
                                JOIN PUBLISHES p2 ON t2.MID = p2.MID
                                GROUP BY m2.MID
                            ) x
                        )''')
    return render_template('report.html', title='Mentor(s) Whose Mentees Produced the Most Publications', rows=rows)


@app.route('/reports/student-publications')
def student_publications():
    rows = fetch_all('''SELECT s.Major, YEAR(pub.Date) AS Publication_Year, COUNT(DISTINCT pub.PubID) AS Student_Publications
                        FROM STUDENT s JOIN PUBLISHES p ON s.MID=p.MID JOIN PUBLICATION pub ON p.PubID=pub.PubID
                        GROUP BY s.Major, YEAR(pub.Date)
                        ORDER BY s.Major, Publication_Year''')
    return render_template('report.html', title='Student Publications per Major and Year', rows=rows)


@app.route('/reports/projects-ended', methods=['GET', 'POST'])
def projects_ended():
    rows = []
    if request.method == 'POST':
        date_x = request.form['date_x']
        rows = fetch_all('''SELECT p.PID, p.Title, p.E_Date, COUNT(g.GID) AS Grant_Count
                            FROM PROJECT p LEFT JOIN GRANT_TBL g ON p.PID=g.PID
                            WHERE p.E_Date IS NOT NULL AND p.E_Date < %s
                            GROUP BY p.PID, p.Title, p.E_Date
                            ORDER BY p.E_Date''', (date_x,))
    return render_template('report.html', title='Projects Ended Before Given Date', rows=rows, form='projects_ended')


@app.route('/reports/productive-years')
def productive_years():
    rows = fetch_all('''SELECT YEAR(pub.Date) AS Publication_Year, COUNT(DISTINCT pub.PubID) AS Student_Publications
                        FROM STUDENT s JOIN PUBLISHES p ON s.MID=p.MID JOIN PUBLICATION pub ON p.PubID=pub.PubID
                        GROUP BY YEAR(pub.Date)
                        ORDER BY Student_Publications DESC, Publication_Year ASC
                        LIMIT 3''')
    return render_template('report.html', title='Top 3 Most Productive Years for Student Publications', rows=rows)


if __name__ == '__main__':
    app.run(debug=True)
