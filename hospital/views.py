from django.shortcuts import render, redirect
from django.http import HttpResponse
import psycopg2 as pg
from datetime import date
import yagmail
from datetime import datetime
import random

# Create your views here.


conn_params = {
    "host": "127.0.0.1",
    "database": "project",
    "user": "postgres",
    "password": "jaswanth12",
}

global doctor_id


def fdo_task(request):
    task = request.POST.get("task")
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    if task == "register":
        patient_id = request.POST.get("patient_id")
        curr.execute(
            "SELECT * FROM AppointmentRequests A WHERE A.SSN=%s;", (patient_id,))
        result = curr.fetchone()
        (name, SSN, email, appointmentdate, department, priority) = result
        curr.execute("select P.employee_id,P.name from Physician P where P.department=%s and P.employee_id not in (select P1.physician from OnLeave P1);", (department,))
        result = curr.fetchall()
        if result == []:
            # send mail to patient that no doctors available
            subject = "Regarding Appointment Details"
            body = """"Dear {patient_name},

I hope this email finds you in good health. I am writing to inform you that unfortunately, we were unable to schedule your appointment on the date requested. This is due to a shortage of doctors available at the time. Please accept our sincere apologies for any inconvenience this may have caused.

Thank you for your understanding and patience in this matter. If you have any questions or concerns, please do not hesitate to reach out to us.

Best regards,
frontDeskOperator.""".format(patien_name=name)
            SendMail(to=email, subject=subject, body=body)
        else:
            physician = random.choice(result)
            doctor_name = physician[1]
            physician = physician[0]
            curr.execute("INSERT INTO Patient(SSN,name,PCP,email) VALUES(%s,%s,%s,%s)",
                         (SSN, name, physician, email,))
            appointmentID = physician+str(SSN)+appointmentdate
            curr.execute("INSERT INTO Appointment(appointment_id,patient,physician,start) VALUES(%s,%s,%s,%s)",
                         (appointmentID, SSN, physician, appointmentdate))
            # send mail to patient
            subject = "Regarding Appointment Details"
            body = """Dear {patient_name},

I am writing to confirm that your appointment with Dr.{doctor_name} has been successfully scheduled for {APT_DATE}.

Please arrive 15 minutes prior to your scheduled appointment time and bring any relevant medical records or test results with you. During the appointment, Dr.{doctor_name} will assess your condition and discuss any necessary treatment or next steps.

If you need to reschedule or cancel the appointment, please let us know as soon as possible so that we can make alternative arrangements.

If you have any questions or concerns, please do not hesitate to contact us. We look forward to seeing you at your scheduled appointment.

Best regards,
frontDeskOperator. """.format(patient_name=name, doctor_name=doctor_name, APT_DATE=appointmentdate)
            SendMail(to=email, subject=subject, body=body)
            if priority == "emergency":
                # send mail to doctor
                curr.execute(
                    "SELECT P.email FROM physician P WHERE P.employee_id=%s", (physician,))
                email = curr.fetchone()[0]
                recipient = email
                subject = "Regarding Emergency Appointment"
                curr.execute(
                    "SELECT A.Appointment_ID,A.patient,A.physician,A.start FROM Appointment A WHERE A.patient=%s", (patient_id,))
                result = curr.fetchone()
                (apt_id, pat, phy, start) = result
                body = """Dear Dr. {doctor_name},

I am writing to request an emergency appointment for one of our patients, {patient_name}. The patient is experiencing severe health problem. We are concerned about their condition and believe that immediate medical attention is necessary.

The patient's details are as follows:

    Patient  Name   :{patient_name}
    Patient  ID     :{pat}
    Appointment ID  :{apt_id}
    Appointment Date:{start}

We would greatly appreciate it if you could fit the patient into your schedule as soon as possible. If you require any further information or have any questions, please do not hesitate to contact us.

Thank you for your prompt attention to this matter.

Yours truly,
frontDeskOperator""".format(apt_id=apt_id, pat=pat, patient_name=name, start=start, doctor_name=doctor_name)
                SendMail(to=recipient, subject=subject, body=body)
        curr.execute(
            "DELETE FROM AppointmentRequests A WHERE A.SSN=%s", (patient_id,))
        conn.commit()
        curr.close()
        conn.close()
        return redirect("http://127.0.0.1:8000/fdo/")
    elif task == "admit":
        patient_id = request.POST.get("patient_id")
        room_id = request.POST.get("room_id")
        date = request.POST.get("date")
        curr.execute(
            "UPDATE ROOM  SET availability='0' WHERE number=%s", (room_id,))
        curr.execute("INSERT INTO Admit(patient,room,date)  VALUES(%s,%s,%s)",
                     (patient_id, room_id, date))
        conn.commit()
        curr.close()
        conn.close()
        return redirect("http://127.0.0.1:8000/fdo/")
    elif task == "discharge":
        patient_id = request.POST.get("patient_id")
        room_id = request.POST.get("room_id")
        date = request.POST.get("date")
        curr.execute(
            "UPDATE ROOM  SET availability='1' WHERE number=%s", (room_id,))
        curr.execute(
            "UPDATE Undergoes SET end_date=%s WHERE patient=%s", (date, patient_id,))
        conn.commit()
        curr.close()
        conn.close()
        return redirect("http://127.0.0.1:8000/fdo/")


def fdo(request):
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute("SELECT R.number FROM Room R WHERE R.availability='1';")
    rooms_list = curr.fetchall()
    curr.execute(
        "SELECT A.name,A.SSN,A.department,A.appointmentdate FROM AppointmentRequests A WHERE A.priority='emergency'")
    emergency_list = curr.fetchall()
    curr.execute(
        "SELECT A.name,A.SSN,A.department ,A.appointmentdate FROM AppointmentRequests A WHERE A.priority='general'")
    general_list = curr.fetchall()
    appointmentrequests = True
    if emergency_list == [] and general_list == []:
        appointmentrequests = False
    curr.close()
    conn.close()
    return render(request, "FDO.html", {"rooms_list": rooms_list, "emergency_list": emergency_list, "general_list": general_list, "appointmentrequests": appointmentrequests})


def del_user(request):
    user_type = request.POST.get("user_type")
    employee_id = request.POST.get("employee_id")
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    user_list = None
    if user_type == "Data Base Adminstrator":
        curr.execute(
            "DELETE FROM databaseadminstrator D WHERE D.employee_id=%s", (employee_id,))
        conn.commit()
        print(curr.rowcount)
        curr.execute(
            "SELECT D.name,D.employee_id FROM databaseadminstrator D ")
        user_list = curr.fetchall()
    elif user_type == "Doctor":
        curr.execute(
            "DELETE FROM physician D WHERE D.employee_id=%s", (employee_id,))
        conn.commit()
        curr.execute("SELECT D.name,D.employee_id FROM physician D ")
        user_list = curr.fetchall()
    elif user_type == "Data Entry Operator":
        curr.execute(
            "DELETE FROM dataentryoperator D WHERE D.employee_id=%s", (employee_id,))
        conn.commit()
        curr.execute("SELECT D.name ,D.employee_id FROM dataentryoperator D ")
        user_list = curr.fetchall()
    elif user_type == "Front Desk Operator":
        curr.execute(
            "DELETE FROM frontdeskoperator D WHERE D.employee_id=%s", (employee_id,))
        conn.commit()
        curr.execute("SELECT D.name,D.employee_id FROM frontdeskoperator D ")
        user_list = curr.fetchall()
    curr.close()
    conn.close()
    return render(request, 'delete_data.html', {"user_type": user_type, "user_list": user_list})


def del_admin(request):
    user_type = "Data Base Adminstrator"
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute("SELECT D.name,D.employee_id FROM databaseadminstrator D ")
    user_list = curr.fetchall()
    curr.close()
    conn.close()
    return render(request, 'delete_data.html', {"user_type": user_type, "user_list": user_list})


def del_doctor(request):
    user_type = "Doctor"
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute("SELECT D.name,D.employee_id FROM physician D ")
    user_list = curr.fetchall()
    curr.close()
    conn.close()
    return render(request, 'delete_data.html', {"user_type": user_type, "user_list": user_list})


def del_fdo(request):
    user_type = "Front Desk Operator"
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute("SELECT D.name,D.employee_id FROM frontdeskoperator D ")
    user_list = curr.fetchall()
    curr.close()
    conn.close()
    return render(request, 'delete_data.html', {"user_type": user_type, "user_list": user_list})


def del_deo(request):
    user_type = "Data Entry Operator"
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute("SELECT D.name,D.employee_id FROM dataentryoperator D ")
    user_list = curr.fetchall()
    curr.close()
    conn.close()
    return render(request, 'delete_data.html', {"user_type": user_type, "user_list": user_list})


def homepage(request):
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d-%m-%Y")
    print(formatted_date)
    return render(request, 'homepage.html')


def login(request):
    return render(request, 'login.html')


def about(request):
    return render(request, 'about.html')


def bookappointment(request):
    return render(request, 'bookappointment.html')


def response(request):
    name = request.POST.get("name")
    SSN = request.POST.get("SSN")
    email = request.POST.get("email")
    appointmentdate = request.POST.get("appointmentdate")
    department = request.POST.get("department")
    priority = request.POST.get("priority")
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute("INSERT INTO AppointmentRequests(name,SSN,email,appointmentdate,department,priority) VALUES (%s,%s,%s,%s,%s,%s)",
                 (name, SSN, email, appointmentdate, department, priority))
    conn.commit()
    curr.close()
    conn.close()
    return render(request, 'response.html')


def test(request):
    return render(request, 'tests.html')


def test_submit(request):
    name = request.POST.get("pname")
    SSN = request.POST.get("pid")
    physician_id = request.POST.get("phid")
    test_id = request.POST.get("test_id")
    date = request.POST.get("date")
    result = request.POST.get("result")
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute("INSERT INTO test_undergoes(patient,test_id,date,physician,result) VALUES (%s,%s,%s,%s,%s)",
                 (SSN, test_id, date, physician_id, result))
    conn.commit()
    curr.close()
    conn.close()
    return redirect("http://127.0.0.1:8000/deo/")


def treatment(request):
    return render(request, 'treatment.html')


def treatment_submit(request):
    patient_id = request.POST.get("patient_id")
    procedure_id = request.POST.get("procedure_id")
    physician_id = request.POST.get("physician_id")
    room = request.POST.get("room")
    date = request.POST.get("date")
    result = request.POST.get("result")
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute("INSERT INTO Undergoes(patient,procedure,room,date,physician,result) VALUES (%s,%s,%s,%s,%s,%s)",
                 (patient_id, procedure_id, room, date, physician_id, result,))
    conn.commit()
    curr.close()
    conn.close()
    return redirect("http://127.0.0.1:8000/deo/")


def deo(request):
    return render(request, 'P_data.html')


def dataadminstrator(request):
    return render(request, 'index.html')


def doctor(request):
    current_date = datetime.now()
    today = current_date.strftime("%d-%m-%Y")
    # print(today)
    global doctor_id
    print(doctor_id)
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute("SELECT P.name,P.SSN,P.email,A.start FROM patient P,Appointment A WHERE P.SSN=A.patient AND A.physician=%s AND A.start!=%s", (doctor_id, today,))
    patient_list = curr.fetchall()
    curr.execute(
        "SELECT p.name,a.start from patient p,appointment a  where p.SSN=a.patient AND a.start=%s", (today,))
    appointments = curr.fetchall()
    curr.close()
    conn.close()
    return render(request, 'doctor.html', {"doctor_id": doctor_id, "patient_list": patient_list, "appointments": appointments})


def search(request):
    patient_id = request.POST.get("patient_id")
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute(
        "select P.SSN,P.name,P.email from patient P where P.SSN= %s", (patient_id,))
    patient = curr.fetchone()
    curr.execute("select P2.name,M.name,M.brand,P1.dose,P1.date from Prescribes P1,medication M,Physician P2 where P1.patient=%s and M.code=P1.medication and P2.employee_id=P1.physician; ", (patient_id,))
    medication = curr.fetchone()
    curr.execute("select P.name,U.date,P.cost,P2.name from undergoes U,procedure P,Physician P2 where U.patient=%s and P.code=U.procedure and P2.employee_id=U.physician;", (patient_id,))
    procedure = curr.fetchone()
    conn.commit()
    curr.close()
    conn.close()
    return render(request, 'search.html', {"patient": patient, "medication": medication, "procedure": procedure})


def validate(request):
    employee_id = request.POST.get("username")
    password = request.POST.get("password")
    user_type = request.POST.get("user_type")
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    if user_type == "Data Base Adminstrator":
        curr.execute(
            "SELECT * FROM databaseadminstrator D where D.employee_Id=%s AND D.password=%s", (employee_id, password,))
        results = curr.fetchall()
        curr.close()
        conn.close()
        if results == []:
            return redirect("http://127.0.0.1:8000/login/")
        else:
            return redirect("http://127.0.0.1:8000/dataadminstrator/")
    elif user_type == "Doctor":
        curr.execute(
            "SELECT * FROM physician D WHERE D.employee_id=%s AND D.password=%s", (employee_id, password,))
        results = curr.fetchall()
        # curr.close()
        # conn.close()
        if results == []:
            curr.close()
            conn.close()
            return redirect("http://127.0.0.1:8000/login/")
        else:
            global doctor_id
            doctor_id = employee_id
            print(doctor_id)
            conn = pg.connect(**conn_params)
            curr = conn.cursor()
            current_date = datetime.now()
            today = current_date.strftime("%d-%m-%Y")
            curr.execute(
                "SELECT P.name,P.SSN,P.email,A.start FROM patient P,Appointment A WHERE P.SSN=A.patient AND A.physician=%s AND A.start!=%s", (doctor_id, today,))
            patient_list = curr.fetchall()
            curr.execute(
                "SELECT p.name,a.start from patient p,appointment a  where p.SSN=a.patient AND a.start=%s", (today,))
            appointments = curr.fetchall()
            curr.close()
            conn.close()
            return render(request, 'doctor.html', {"doctor_id": doctor_id, "patient_list": patient_list, "appointments": appointments})

    elif user_type == "Data Entry Operator":
        curr.execute(
            "SELECT * FROM dataentryoperator D WHERE D.employee_id=%s AND D.password=%s", (employee_id, password,))
        results = curr.fetchall()
        curr.close()
        conn.close()
        if results == []:
            return redirect("http://127.0.0.1:8000/login/")
        else:
            return redirect("http://127.0.0.1:8000/deo/")
    elif user_type == "Front Desk Operator":
        curr.execute(
            "SELECT * FROM frontdeskoperator D WHERE D.employee_id=%s AND D.password=%s", (employee_id, password,))
        results = curr.fetchall()
        curr.close()
        conn.close()
        if results == []:
            return redirect("http://127.0.0.1:8000/login/")
        else:
            return redirect("http://127.0.0.1:8000/fdo/")


def delete_data(request):
    return render(request, 'delete_data.html')


def add_fdo(request):
    user_type = "frontdeskoperator"
    return render(request, 'add_data.html', {"user_type": user_type})


def add_deo(request):
    user_type = "dataentryoperator"
    return render(request, 'add_data.html', {"user_type": user_type})


def add_admin(request):
    user_type = "dataadminstrator"
    return render(request, 'add_data.html', {"user_type": user_type})


def add_doctor(request):
    return render(request, 'add_doctor.html')


def add_user(request):
    user_type = request.POST.get("user_type")
    name = request.POST.get("name")
    employee_id = request.POST.get("employee_id")
    password = request.POST.get("password")
    SSN = request.POST.get("SSN")
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute("INSERT INTO {}(name,employee_id,password,SSN) VALUES (%s,%s,%s,%s)".format(
        user_type), (name, employee_id, password, SSN))
    conn.commit()
    curr.close()
    conn.close()
    return redirect("http://127.0.0.1:8000/dataadminstrator/")


def doc_add(request):
    employee_id = request.POST.get("employee_id")
    name = request.POST.get("name")
    SSN = request.POST.get("SSN")
    password = request.POST.get("password")
    department = request.POST.get("department")
    email = request.POST.get("email")
    conn = pg.connect(**conn_params)
    curr = conn.cursor()
    curr.execute("INSERT INTO physician (employee_id,name,SSN,password,department,email) VALUES (%s,%s,%s,%s,%s,%s)",
                 (employee_id, name, SSN, password, department, email,))
    conn.commit()
    curr.close()
    conn.close()
    return redirect("http://127.0.0.1:8000/dataadminstrator/")


def SendMail(to, subject, body):
    yag = yagmail.SMTP('hospitalfrontdesk420@gmail.com', 'prjcwyudioqhhxbi')
    yag.send(to=to, subject=subject, contents=body)

    return
