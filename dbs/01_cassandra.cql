// =====================================================================
// Cassandra - Personas (clientes y empleados)
// Ejecutar con:  cqlsh -f dbs/01_cassandra.cql
// =====================================================================

CREATE KEYSPACE IF NOT EXISTS billing
WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': 1 };

USE billing;

DROP TABLE IF EXISTS person;
DROP TABLE IF EXISTS person_by_role;

CREATE TABLE person (
    document        text PRIMARY KEY,
    id              uuid,
    first_name      text,
    last_name       text,
    role            text,
    email           text,
    phone           text,
    birth_date      date,
    gender          text,
    stratum         int,
    neighborhood    text,
    municipality    text,
    department      text,
    salary          double
);

CREATE TABLE person_by_role (
    role         text,
    document     text,
    first_name   text,
    last_name    text,
    email        text,
    PRIMARY KEY (role, document)
);

// --------- Datos semilla ---------
// Empleados
INSERT INTO person (document,id,first_name,last_name,role,email,phone,birth_date,gender,stratum,neighborhood,municipality,department,salary)
VALUES ('E001', uuid(), 'María',   'Gómez',    'EMPLOYEE','maria.gomez@pb.co','3001112233','1990-04-15','F',4,'La Pola','Ibagué','Tolima',2500000);
INSERT INTO person_by_role (role,document,first_name,last_name,email)
VALUES ('EMPLOYEE','E001','María','Gómez','maria.gomez@pb.co');

INSERT INTO person (document,id,first_name,last_name,role,email,phone,birth_date,gender,stratum,neighborhood,municipality,department,salary)
VALUES ('E002', uuid(), 'Carlos', 'Rodríguez','EMPLOYEE','carlos.r@pb.co','3014445566','1988-08-22','M',3,'Cádiz','Ibagué','Tolima',2200000);
INSERT INTO person_by_role (role,document,first_name,last_name,email)
VALUES ('EMPLOYEE','E002','Carlos','Rodríguez','carlos.r@pb.co');

// Clientes
INSERT INTO person (document,id,first_name,last_name,role,email,phone,birth_date,gender,stratum,neighborhood,municipality,department,salary)
VALUES ('C100', uuid(), 'Ana',    'López',    'CLIENT','ana@mail.co','3201112233','1995-02-10','F',3,'Cádiz','Ibagué','Tolima',null);
INSERT INTO person_by_role (role,document,first_name,last_name,email)
VALUES ('CLIENT','C100','Ana','López','ana@mail.co');

INSERT INTO person (document,id,first_name,last_name,role,email,phone,birth_date,gender,stratum,neighborhood,municipality,department,salary)
VALUES ('C101', uuid(), 'Luis',   'Martínez', 'CLIENT','luis@mail.co','3204445566','1992-06-25','M',3,'Cádiz','Ibagué','Tolima',null);
INSERT INTO person_by_role (role,document,first_name,last_name,email)
VALUES ('CLIENT','C101','Luis','Martínez','luis@mail.co');

INSERT INTO person (document,id,first_name,last_name,role,email,phone,birth_date,gender,stratum,neighborhood,municipality,department,salary)
VALUES ('C102', uuid(), 'Sofía',  'Ramírez',  'CLIENT','sofia@mail.co','3207778899','1998-11-05','F',4,'La Pola','Ibagué','Tolima',null);
INSERT INTO person_by_role (role,document,first_name,last_name,email)
VALUES ('CLIENT','C102','Sofía','Ramírez','sofia@mail.co');

INSERT INTO person (document,id,first_name,last_name,role,email,phone,birth_date,gender,stratum,neighborhood,municipality,department,salary)
VALUES ('C103', uuid(), 'Andrés', 'Torres',   'CLIENT','andres@mail.co','3208889900','1985-09-12','M',2,'Jordán','Ibagué','Tolima',null);
INSERT INTO person_by_role (role,document,first_name,last_name,email)
VALUES ('CLIENT','C103','Andrés','Torres','andres@mail.co');

INSERT INTO person (document,id,first_name,last_name,role,email,phone,birth_date,gender,stratum,neighborhood,municipality,department,salary)
VALUES ('C104', uuid(), 'Valentina','Pérez',  'CLIENT','vale@mail.co','3201234567','2000-01-30','F',5,'Piedra Pintada','Ibagué','Tolima',null);
INSERT INTO person_by_role (role,document,first_name,last_name,email)
VALUES ('CLIENT','C104','Valentina','Pérez','vale@mail.co');
