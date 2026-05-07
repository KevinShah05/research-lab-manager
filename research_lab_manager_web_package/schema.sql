-- Research Lab Manager - Phase 3 Schema
-- MySQL implementation based on the professor-provided relational schema.
-- Note: GRANT is a reserved keyword in MySQL, so the table is named GRANT_TBL.

DROP DATABASE IF EXISTS research_lab_manager;
CREATE DATABASE research_lab_manager;
USE research_lab_manager;

CREATE TABLE LAB_MEMBER (
    MID         INT          NOT NULL,
    Name        VARCHAR(100) NOT NULL,
    Join_Date   DATE         NOT NULL,
    Type        VARCHAR(20)  NOT NULL,
    Mentor      INT,
    M_SDate     DATE,
    M_EDate     DATE,
    CONSTRAINT pk_lab_member PRIMARY KEY (MID),
    CONSTRAINT chk_lab_member_type CHECK (Type IN ('faculty', 'student', 'collaborator')),
    CONSTRAINT fk_lab_member_mentor FOREIGN KEY (Mentor)
        REFERENCES LAB_MEMBER(MID),
    CONSTRAINT chk_mentor_dates CHECK (M_EDate IS NULL OR M_SDate IS NULL OR M_EDate >= M_SDate),
    CONSTRAINT chk_no_self_mentor CHECK (Mentor IS NULL OR Mentor <> MID)
);

CREATE TABLE STUDENT (
    MID      INT          NOT NULL,
    SID      VARCHAR(20)  NOT NULL,
    Level    VARCHAR(30)  NOT NULL,
    Major    VARCHAR(100) NOT NULL,
    CONSTRAINT pk_student PRIMARY KEY (MID),
    CONSTRAINT uq_student_sid UNIQUE (SID),
    CONSTRAINT fk_student_mid FOREIGN KEY (MID)
        REFERENCES LAB_MEMBER(MID)
        ON DELETE CASCADE,
    CONSTRAINT chk_student_level CHECK (Level IN ('junior', 'senior', 'graduate student'))
);

CREATE TABLE COLLABORATOR (
    MID          INT          NOT NULL,
    Affiliation  VARCHAR(200) NOT NULL,
    CV           TEXT,
    CONSTRAINT pk_collaborator PRIMARY KEY (MID),
    CONSTRAINT fk_collaborator_mid FOREIGN KEY (MID)
        REFERENCES LAB_MEMBER(MID)
        ON DELETE CASCADE
);

CREATE TABLE FACULTY (
    MID         INT          NOT NULL,
    Department  VARCHAR(100) NOT NULL,
    CONSTRAINT pk_faculty PRIMARY KEY (MID),
    CONSTRAINT fk_faculty_mid FOREIGN KEY (MID)
        REFERENCES LAB_MEMBER(MID)
        ON DELETE CASCADE
);

CREATE TABLE PROJECT (
    PID         INT          NOT NULL,
    Title       VARCHAR(200) NOT NULL,
    S_Date      DATE         NOT NULL,
    E_Date      DATE,
    E_Duration  INT          NOT NULL,
    Leader      INT          NOT NULL,
    CONSTRAINT pk_project PRIMARY KEY (PID),
    CONSTRAINT fk_project_leader FOREIGN KEY (Leader)
        REFERENCES FACULTY(MID),
    CONSTRAINT chk_project_dates CHECK (E_Date IS NULL OR E_Date >= S_Date),
    CONSTRAINT chk_project_duration CHECK (E_Duration > 0)
);

CREATE TABLE GRANT_TBL (
    GID          INT           NOT NULL,
    P_Duration   INT           NOT NULL,
    Agency       VARCHAR(200)  NOT NULL,
    Budget       DECIMAL(15,2) NOT NULL,
    Start_Date   DATE          NOT NULL,
    PID          INT           NOT NULL,
    CONSTRAINT pk_grant PRIMARY KEY (GID),
    CONSTRAINT fk_grant_project FOREIGN KEY (PID)
        REFERENCES PROJECT(PID)
        ON DELETE CASCADE,
    CONSTRAINT chk_grant_budget CHECK (Budget > 0),
    CONSTRAINT chk_grant_duration CHECK (P_Duration > 0)
);

CREATE TABLE WORKS (
    PID     INT          NOT NULL,
    MID     INT          NOT NULL,
    Role    VARCHAR(100) NOT NULL,
    Hours   DECIMAL(8,2) NOT NULL,
    CONSTRAINT pk_works PRIMARY KEY (PID, MID),
    CONSTRAINT fk_works_project FOREIGN KEY (PID)
        REFERENCES PROJECT(PID)
        ON DELETE CASCADE,
    CONSTRAINT fk_works_member FOREIGN KEY (MID)
        REFERENCES LAB_MEMBER(MID)
        ON DELETE CASCADE,
    CONSTRAINT chk_works_hours CHECK (Hours > 0)
);

CREATE TABLE EQUIPMENT (
    EID      INT          NOT NULL,
    E_Type   VARCHAR(100) NOT NULL,
    E_Name   VARCHAR(100) NOT NULL,
    Manual_Text TEXT,
    CONSTRAINT pk_equipment PRIMARY KEY (EID)
);

CREATE TABLE DEVICE (
    DID      INT         NOT NULL,
    EID      INT         NOT NULL,
    Status   VARCHAR(20) NOT NULL,
    P_Date   DATE        NOT NULL,
    CONSTRAINT pk_device PRIMARY KEY (DID),
    CONSTRAINT fk_device_equipment FOREIGN KEY (EID)
        REFERENCES EQUIPMENT(EID)
        ON DELETE CASCADE,
    CONSTRAINT chk_device_status CHECK (Status IN ('available', 'in use', 'retired'))
);

CREATE TABLE USES (
    MID      INT          NOT NULL,
    DID      INT          NOT NULL,
    EID      INT          NOT NULL,
    S_Date   DATE         NOT NULL,
    E_Date   DATE,
    Purpose  VARCHAR(300) NOT NULL,
    CONSTRAINT pk_uses PRIMARY KEY (MID, DID, S_Date),
    CONSTRAINT fk_uses_member FOREIGN KEY (MID)
        REFERENCES LAB_MEMBER(MID)
        ON DELETE CASCADE,
    CONSTRAINT fk_uses_device FOREIGN KEY (DID)
        REFERENCES DEVICE(DID)
        ON DELETE CASCADE,
    CONSTRAINT fk_uses_equipment FOREIGN KEY (EID)
        REFERENCES EQUIPMENT(EID)
        ON DELETE CASCADE,
    CONSTRAINT chk_uses_dates CHECK (E_Date IS NULL OR E_Date >= S_Date)
);

CREATE TABLE PUBLICATION (
    PubID  INT          NOT NULL,
    Title  VARCHAR(300) NOT NULL,
    Venue  VARCHAR(200) NOT NULL,
    Date   DATE         NOT NULL,
    DOI    VARCHAR(100),
    CONSTRAINT pk_publication PRIMARY KEY (PubID),
    CONSTRAINT uq_publication_doi UNIQUE (DOI)
);

CREATE TABLE PUBLISHES (
    MID    INT NOT NULL,
    PubID  INT NOT NULL,
    CONSTRAINT pk_publishes PRIMARY KEY (MID, PubID),
    CONSTRAINT fk_publishes_member FOREIGN KEY (MID)
        REFERENCES LAB_MEMBER(MID)
        ON DELETE CASCADE,
    CONSTRAINT fk_publishes_publication FOREIGN KEY (PubID)
        REFERENCES PUBLICATION(PubID)
        ON DELETE CASCADE
);
