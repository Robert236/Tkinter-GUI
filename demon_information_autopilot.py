import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
import datetime


def write_read_in_database(methode, sql_statement):
    conn = mysql.connector.connect(host='127.0.0.1',
                                   database='Birthday_Information_Autopilot',
                                   user='root',
                                   password='1234',
                                   auth_plugin='mysql_native_password')
    try:
        if conn.is_connected():
            if methode == "push":
                cursor = conn.cursor()
                cursor.execute(sql_statement)
                conn.commit()
                return ["success"]
            else:
                cursor = conn.cursor()
                cursor.execute(sql_statement)
                rv = cursor.fetchall()
                return rv
        else:
            print("database is not connected.")
    except Error:
        return ["error"]
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


def calculate_age(dataset):
    year_of_birth = str(dataset["geburtstag"])[:4]
    current_year = now_american[:4]
    return int(current_year) - int(year_of_birth)


def send_via_mail(entry_dict):
    try:
        sender = 'whatsapp.autopilot1@googlemail.com'
        receiver = 'robertvater1@googlemail.com'
        s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
        s.login(user=sender, password='wXHf7hwYhrTreuOW5j99')
        rv_age = calculate_age(entry_dict)
        body_of_the_email = "Wird heute {} Jahre alt. Handnummer: {}, Status: {}".format(rv_age,
                                                                                            entry_dict["handynummer"],
                                                                                            entry_dict["status"])
        birthday_child = "Geburtstag von {}, {} am {}!".format(entry_dict["nachname"],
                                                               entry_dict["vorname"], now.strftime("%d %B, %Y"))
        msg = MIMEText(body_of_the_email, 'html')
        msg['Subject'] = birthday_child
        msg['From'] = sender
        msg['To'] = receiver
        s.sendmail(sender, receiver, msg.as_string())
        # print("Die Nachricht wurde per E-Mail verschickt.")
        s.quit()
    except smtplib.SMTPAuthenticationError as error:
        print(error)


sql_statement_fetch_all = "SELECT vorname, nachname, handynummer, status, geburtstag FROM geburtstagspersonen;"
rv_db = write_read_in_database("pull", sql_statement_fetch_all)
now = datetime.datetime.now()
now_american = now.strftime('%Y-%m-%d')
for entry in rv_db:
    if str(entry[4])[5:] == now_american[5:]:
        keys = ("vorname", "nachname", "handynummer", "status", "geburtstag")
        entry_as_dict = dict(zip(keys, entry))
        send_via_mail(entry_as_dict)
