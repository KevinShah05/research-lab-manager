-- Research Lab Manager - Phase 3 Sample Data
USE research_lab_manager;

-- Supertype rows first. Mentor values are updated later because mentors are also LAB_MEMBER rows.
INSERT INTO LAB_MEMBER (MID, Name, Join_Date, Type, Mentor, M_SDate, M_EDate) VALUES
(1,  'Dr. Alice Kim',      '2021-08-15', 'faculty',      NULL, NULL, NULL),
(2,  'Dr. Robert Chen',    '2020-09-01', 'faculty',      NULL, NULL, NULL),
(3,  'Dr. Maria Patel',    '2019-01-20', 'faculty',      NULL, NULL, NULL),
(4,  'Nina Shah',          '2023-09-05', 'student',      NULL, NULL, NULL),
(5,  'Omar Diaz',          '2022-09-01', 'student',      NULL, NULL, NULL),
(6,  'Grace Lee',          '2024-01-10', 'student',      NULL, NULL, NULL),
(7,  'Ethan Miller',       '2023-01-15', 'student',      NULL, NULL, NULL),
(8,  'Priya Singh',        '2022-02-11', 'student',      NULL, NULL, NULL),
(9,  'Dr. Elena Garcia',   '2023-05-21', 'collaborator', NULL, NULL, NULL),
(10, 'Liam O''Connor',     '2024-02-01', 'collaborator', NULL, NULL, NULL),
(11, 'Maya Johnson',       '2023-06-12', 'student',      NULL, NULL, NULL),
(12, 'Dr. Samuel Brown',   '2021-04-18', 'collaborator', NULL, NULL, NULL),
(13, 'Hannah Nguyen',      '2024-08-25', 'student',      NULL, NULL, NULL),
(14, 'Daniel Park',        '2023-11-03', 'student',      NULL, NULL, NULL);

INSERT INTO FACULTY (MID, Department) VALUES
(1, 'Computer Science'),
(2, 'Biomedical Engineering'),
(3, 'Data Science');

INSERT INTO STUDENT (MID, SID, Level, Major) VALUES
(4,  'S1004', 'graduate student', 'Computer Science'),
(5,  'S1005', 'senior',           'Data Science'),
(6,  'S1006', 'junior',           'Biomedical Engineering'),
(7,  'S1007', 'graduate student', 'Computer Science'),
(8,  'S1008', 'senior',           'Information Technology'),
(11, 'S1011', 'graduate student', 'Data Science'),
(13, 'S1013', 'junior',           'Computer Science'),
(14, 'S1014', 'senior',           'Biomedical Engineering');

INSERT INTO COLLABORATOR (MID, Affiliation, CV) VALUES
(9,  'Rutgers University', 'External collaborator specializing in medical informatics.'),
(10, 'Princeton Research Center', 'External collaborator specializing in sensor calibration.'),
(12, 'City Hospital Research Unit', 'Clinical collaborator for biomedical research studies.');

-- Mentorships stored in LAB_MEMBER based on professor-provided schema.
UPDATE LAB_MEMBER SET Mentor = 1, M_SDate = '2023-09-10', M_EDate = NULL WHERE MID IN (4, 7, 13);
UPDATE LAB_MEMBER SET Mentor = 2, M_SDate = '2024-01-15', M_EDate = NULL WHERE MID IN (6, 14);
UPDATE LAB_MEMBER SET Mentor = 3, M_SDate = '2022-09-15', M_EDate = NULL WHERE MID IN (5, 8, 11);

INSERT INTO PROJECT (PID, Title, S_Date, E_Date, E_Duration, Leader) VALUES
(101, 'AI Assisted Lab Scheduling',        '2023-01-01', NULL,          24, 1),
(102, 'Biomedical Sensor Analysis',        '2022-06-01', '2024-06-30',  24, 2),
(103, 'Grant Impact Dashboard',            '2023-09-01', NULL,          18, 3),
(104, 'Robotics Equipment Automation',     '2021-05-01', '2023-12-31',  30, 1),
(105, 'Student Publication Analytics',     '2024-01-01', NULL,          12, 3),
(106, 'Microscope Usage Optimization',     '2022-01-10', '2023-07-15',  18, 2);

INSERT INTO GRANT_TBL (GID, P_Duration, Agency, Budget, Start_Date, PID) VALUES
(201, 24, 'National Science Foundation',       150000.00, '2023-01-01', 101),
(202, 12, 'NJ Health Innovation Fund',          75000.00, '2023-06-01', 102),
(203, 24, 'National Institutes of Health',     220000.00, '2022-06-01', 102),
(204, 18, 'University Research Office',         45000.00, '2023-09-01', 103),
(205, 30, 'Defense Research Program',          180000.00, '2021-05-01', 104),
(206, 12, 'Student Research Fund',              35000.00, '2024-01-01', 105),
(207, 18, 'Biomedical Equipment Grant',         90000.00, '2022-01-10', 106),
(208, 12, 'AI Innovation Fund',                 65000.00, '2024-02-01', 101);

INSERT INTO WORKS (PID, MID, Role, Hours) VALUES
(101, 1,  'Project Leader',       8.0),
(101, 4,  'Graduate Researcher',  12.0),
(101, 7,  'Data Engineer',        10.0),
(101, 13, 'Research Assistant',    6.0),
(102, 2,  'Project Leader',       7.5),
(102, 6,  'Lab Assistant',         8.0),
(102, 9,  'External Advisor',      4.0),
(102, 14, 'Research Assistant',    6.5),
(103, 3,  'Project Leader',       6.0),
(103, 5,  'Data Analyst',          9.0),
(103, 8,  'Dashboard Developer',   8.0),
(103, 11, 'Publication Analyst',   7.0),
(104, 1,  'Project Leader',       5.0),
(104, 10, 'Sensor Consultant',     3.0),
(104, 7,  'Robotics Programmer',   8.0),
(105, 3,  'Project Leader',       6.0),
(105, 4,  'Publication Analyst',   6.0),
(105, 5,  'Data Analyst',          5.5),
(105, 11, 'Research Assistant',    7.5),
(106, 2,  'Project Leader',       5.0),
(106, 6,  'Equipment Tester',      7.0),
(106, 12, 'Clinical Advisor',      2.0);

INSERT INTO EQUIPMENT (EID, E_Type, E_Name, Manual_Text) VALUES
(301, 'Microscope', 'Olympus CX43 Microscope', 'Manual stored in lab drive /manuals/olympus_cx43.pdf'),
(302, 'Server',     'Dell PowerEdge R550',     'Manual stored in lab drive /manuals/dell_r550.pdf'),
(303, 'Sensor',     'BioSensor Kit A',         'Manual stored in lab drive /manuals/biosensor_a.pdf'),
(304, 'Robot',      'TurtleBot Research Unit', 'Manual stored in lab drive /manuals/turtlebot.pdf'),
(305, 'Workstation','GPU Workstation',         'Manual stored in lab drive /manuals/gpu_workstation.pdf');

INSERT INTO DEVICE (DID, EID, Status, P_Date) VALUES
(401, 301, 'in use',    '2021-03-10'),
(402, 301, 'available', '2021-03-10'),
(403, 302, 'in use',    '2022-07-01'),
(404, 303, 'in use',    '2022-08-18'),
(405, 303, 'available', '2023-02-20'),
(406, 304, 'retired',   '2020-05-12'),
(407, 304, 'in use',    '2022-11-04'),
(408, 305, 'available', '2024-01-14'),
(409, 305, 'in use',    '2024-01-14');

INSERT INTO USES (MID, DID, EID, S_Date, E_Date, Purpose) VALUES
(4,  403, 302, '2024-03-01', NULL,         'Model training for AI scheduling project'),
(7,  403, 302, '2024-03-05', NULL,         'Database pipeline testing'),
(13, 409, 305, '2024-09-01', NULL,         'Data preprocessing for scheduling project'),
(6,  401, 301, '2024-02-01', NULL,         'Biomedical sample analysis'),
(14, 401, 301, '2024-02-10', NULL,         'Microscope image collection'),
(9,  404, 303, '2024-04-01', NULL,         'Sensor validation'),
(10, 407, 304, '2023-06-01', '2023-12-10', 'Robotics navigation testing'),
(7,  407, 304, '2023-06-15', '2023-12-15', 'Robot automation scripts'),
(11, 408, 305, '2024-04-20', '2024-05-30', 'Publication analytics experiments'),
(5,  405, 303, '2023-10-01', '2023-12-01', 'Dashboard sensor data testing');

INSERT INTO PUBLICATION (PubID, Title, Venue, Date, DOI) VALUES
(501, 'Optimizing Laboratory Scheduling with AI', 'Journal of Lab Informatics', '2024-05-10', '10.1000/rlm.501'),
(502, 'Biomedical Sensor Data Quality Evaluation', 'Sensors Today', '2023-11-18', '10.1000/rlm.502'),
(503, 'Grant Funding Patterns in University Labs', 'Data Management Review', '2024-02-14', '10.1000/rlm.503'),
(504, 'Robotics Automation in Shared Research Spaces', 'Robotics Research Letters', '2022-09-22', '10.1000/rlm.504'),
(505, 'Publication Analytics for Student Researchers', 'Education Data Journal', '2024-08-05', '10.1000/rlm.505'),
(506, 'Microscope Usage Modeling in Biomedical Labs', 'Biomedical Systems Journal', '2023-04-12', '10.1000/rlm.506'),
(507, 'Student Research Productivity Trends', 'Academic Analytics Conference', '2025-01-15', '10.1000/rlm.507'),
(508, 'Sensor Calibration Workflows for Research Labs', 'Engineering Systems Workshop', '2023-07-19', '10.1000/rlm.508');

INSERT INTO PUBLISHES (MID, PubID) VALUES
(1, 501), (4, 501), (7, 501),
(2, 502), (6, 502), (9, 502),
(3, 503), (5, 503), (8, 503),
(1, 504), (7, 504), (10, 504),
(3, 505), (4, 505), (11, 505),
(2, 506), (6, 506), (12, 506),
(3, 507), (5, 507), (11, 507), (8, 507),
(2, 508), (6, 508), (14, 508);
