drop table appointment cascade;
drop table medication cascade;
drop table test cascade;
drop table test_undergoes cascade;
drop table patient cascade;
drop table physician cascade;
drop table prescribes cascade;
drop table procedure cascade;
drop table room cascade;
drop table undergoes cascade;
drop table FrontDeskOperator cascade;
drop table DataEntryOperator cascade;
drop table DatabaseAdminstrator cascade;
drop table AppointmentRequests cascade;
drop table Admit cascade;
drop table onleave cascade;

create table FrontDeskOperator(
    name text not null,
    employee_id text not null,
    password text not null,
    SSN int not null,
    primary key(employee_id));

create table DataEntryOperator(
   name text not null,
    employee_id text not null,
    password text not null,
    SSN int not null,
    primary key(employee_id)); 

create table DatabaseAdminstrator(
    name text not null,
    employee_id text not null,
    password text not null,
    SSN int not null,
    primary key(employee_id)); 

create table Physician(
    employee_id text not null,
    name        text not null,
    SSN         int not null,
	password    text not null,
    department text not null,
    email  text not null,
    primary key(employee_id));

create table Medication(
    code    int not null,
    name    text not null,
    brand   text not null,
    description text not null,
    primary key(code));

create table Procedure(
    code int not null,
    name text not null,
    cost int not null,
    primary key(code));

create table Test(
    test_name text not null,
    test_id int not null,
    test_cost int not null,
    primary key(test_id));

create table Room(
    number text not null,
    type text not null,
    availability boolean not null,
    primary key(number));

create table Patient(
    SSN int not null,
    name text not null,
    pcp text not null,
    email text not null,
    primary key(SSN),
    foreign key(pcp) references Physician(employee_id));



create table Undergoes(
    patient int not null,
    procedure int not null,
    room text not null,
    "date" text not null,
    physician text not null,
    result text not null,
    end_date text,
    primary key(patient,procedure,room,date),
    foreign key(patient) references Patient(SSN),
    foreign key(procedure) references Procedure(code),
    foreign key(room) references room(number),
    foreign key(physician) references Physician(employee_id));

create table Test_Undergoes(
    patient int not null,
    test_id int not null,
    "date" text not null,
    physician text not null,
    result text not null,
    primary key(patient,test_id,date,physician),
    foreign key(patient) references Patient(SSN),
    foreign key(test_id) references Test(test_id),
    foreign key(physician) references Physician(employee_id));

create table Appointment(
    appointment_id text not null,
    patient int not null,
    physician text not null,
    "start" text not null,
    "end" text ,
    primary key(appointment_id),
    foreign key(patient) references Patient(SSN),
    foreign key(physician) references Physician(employee_id));

create table Prescribes(
    physician text not null,
    patient int not null,
    medication int not null,
    "date" text not null,
    appointment text not null,
    dose text not null,
    primary key(physician,patient,medication,"date"),
    foreign key(physician) references Physician(employee_id),
    foreign key(patient) references Patient(SSN),
    foreign key(medication) references Medication(code),
    foreign key(appointment) references Appointment(appointment_id));

create table AppointmentRequests(
    name text not null,
    SSN int not null,
    email text not null,
    appointmentdate text not null,
    department text not null,
    priority text not null,
    primary key(SSN,appointmentdate));
    
create table Admit(
    patient int not null,
    room text not null,
    "date" text not null,
    primary key(patient,room,"date"));

create table OnLeave(
    physician text not null,
    "date" text not null,
    primary key(physician,"date"));

INSERT into DatabaseAdminstrator VALUES('itachi','da1','1',1807);
INSERT into DataEntryOperator VALUES('kakashi','deo1','1',420);
INSERT into FrontDeskOperator VALUES('tsunade','fdo1','1',106);

INSERT into Medication VALUES('11000','Amlodipine','Norvasc','Amlodipine is a calcium channel blocker, prescribed for high blood pressure and chest pain.');
INSERT into Medication VALUES('11111','Ibuprofen','Advil','Ibuprofen provides good analgesia after the removal of impacted third molars.');
INSERT into Medication VALUES('11222','Multivitamin','Folgard','It is to fill in nutritional gaps, and provides only a hint of the vast array of healthful nutrients found in food.');
INSERT into Medication VALUES('11333','Citalopram','Celexa','A medication used to treat depression and anxiety.');
INSERT into Medication VALUES('11444','Sertaline','Zoloft','It is used to treat depression, obsessive-compulsive disorder , panic attacks , posttraumatic stress disorder.');
INSERT into Medication VALUES('11555','Amoxicillin','Amoxicil','It is used to treat bacterial infections, such as chest infections (including pneumonia) and dental abscesses.');

INSERT into Room VALUES('101','General Ward','0');
INSERT into Room VALUES('104','Emergency ward','1');
INSERT into Room VALUES('105','ICU','0');

INSERT into Test VALUES('Blood test','112','450');
INSERT into Test VALUES('Oral Examination','113','1200');
INSERT into Test VALUES('Nutrition monitoring','114','500');
INSERT into Test VALUES('Psychological testing','115','2200');
INSERT into Test VALUES('Psychological Assessment','116','1100');
INSERT into Test VALUES('Screening test','117','750');


INSERT into Procedure VALUES('333','Bypass Surgery','300000');
INSERT into Procedure VALUES('444','Dental Implant','25000');
INSERT into Procedure VALUES('555','Nutrition evaluation','800');
INSERT into Procedure VALUES('666','Psychotherapy','9000');
INSERT into Procedure VALUES('777','Physiatry','8000');
INSERT into Procedure VALUES('888','Pediatric surgery','150000');

INSERT into Physician VALUES('sushanth','sushanth','1','sushanth','Orthopaedics','maradasushanth@gmail.com');
INSERT into Physician VALUES('peter','peter','2','peter','Paediatrics','bhanutejasiripuram264@gmail.com');
INSERT into Physician VALUES('sahan','sahan','3','sahan','Cardiology','saisahantalabattula@gmail.com');
INSERT into Physician VALUES('donkey','donkey','3','donkey','Cardiology','test@gmail.com');

INSERT into Patient VALUES('1','Thor','sushanth','myselfavenger5@gmail.com');
INSERT into Patient VALUES('2','HulK','sushanth','myselfavenger5@gmail.com');
INSERT into Patient VALUES('3','Ironman','sahan','myselfavenger5@gmail.com');
INSERT into Patient VALUES('4','Loki','peter','myselfavenger5@gmail.com');
INSERT into Patient VALUES('5','Captain','peter','myselfavenger5@gmail.com');

INSERT into Appointment VALUES('1','2','sushanth','12-05-2023','12-05-2023');
INSERT into Appointment VALUES('2','3','sahan','01-02-2023','04-02-2023');
INSERT into Appointment VALUES('3','4','peter','02-11-2022','03-11-2022');
INSERT into Appointment VALUES('4','5','peter','20-01-2023','25-02-2023');

INSERT into Prescribes VALUES('peter','4','11444','02-11-2022','3','20mg');
INSERT into Prescribes VALUES('sahan','3','11222','01-02-2023','2','100mg');
INSERT into Prescribes VALUES('peter','5','11000','20-01-2023','4','2mg');
INSERT into Prescribes VALUES('sushanth','2','11333','12-05-2023','1','0.1mg');

INSERT into Undergoes VALUES('2','666','101','12-05-2003','sushanth','positive','12-05-2023');
INSERT into Undergoes VALUES('3','555','101','01-02-2023','sahan','negative','04-02-2023');
INSERT into Undergoes VALUES('5','777','101','20-01-2023','peter','positive','25-02-2023');

INSERT into Test_Undergoes VALUES('2','115','12-05-2003','sushanth','positive');
INSERT into Test_Undergoes VALUES('3','114','01-02-2023','sahan','negative');
INSERT into Test_Undergoes VALUES('5','116','20-01-2023','peter','positive');

INSERT into OnLeave VALUES('donkey','05-03-2023');