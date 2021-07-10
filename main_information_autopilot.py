import tkinter as tk
from tkinter import ttk
import mysql.connector
from mysql.connector import Error

global_create_values = {}
global_change_values = {}
global_pk = {}

keys_persons = ["vorname", "nachname", "handynummer", "status", "geburtstag"]


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


def unfilled_input_fields(unpacked_values):
    for key in unpacked_values:
        if unpacked_values[key] == '':
            return False
    return True


def retrieve_values(packed_values):
    unpacked_values = {}
    for val in packed_values:
        if val == "geburtstag":
            dates_list_unpacked = []
            for time_object in packed_values[val]:
                dates_list_unpacked.append(time_object.get())
            unpacked_values[val] = dates_list_unpacked
        else:
            unpacked_values[val] = packed_values[val].get()
    return unpacked_values


def notification_window(current_notifications, window_size):
    notification_win = tk.Toplevel(window_1)
    notification_win.title("Achtung!")
    notification_win.geometry(window_size)
    tk.Label(notification_win, text="").grid(row=0, column=0)
    for i, notification in enumerate(current_notifications, start=1):
        tk.Label(notification_win, text=notification, font="bold", padx=15).grid(row=i, column=0)


def check_syntax_values(unpacked_values):
    error_list = []
    for key in unpacked_values:
        if key == "status" or key == "geburtstag":
            pass
        else:
            if key == "vorname" or key == "nachname":
                rv_result_str = unpacked_values[key].isalpha()
                if rv_result_str:
                    pass
                else:
                    error_message = "{} nicht korrekt".format(key)
                    error_list.append(error_message)
            else:
                rv_result_int = unpacked_values[key].isdigit()
                if rv_result_int:
                    pass
                else:
                    error_message_1 = "{} nicht korrekt".format(key)
                    error_list.append(error_message_1)
    return error_list


def convert_into_date_syntax(date_data):
    date_american = ""
    for time_unit in date_data:
        date_american += time_unit + "-"
    date_american = date_american[:-1]
    return date_american


def convert_values_to_sql_statement(unpacked_values):
    sql_statement_columns = "INSERT INTO geburtstagspersonen ("
    sql_statement_values = "VALUES ("
    for key in unpacked_values:
        if key == "geburtstag":
            correct_date = convert_into_date_syntax(unpacked_values[key])
            sql_statement_columns += key + ", "
            sql_statement_values += "'" + correct_date + "', "
        else:
            sql_statement_columns += key + ", "
            sql_statement_values += "'" + unpacked_values[key] + "', "
    sql_statement_columns = sql_statement_columns[:-2]
    sql_statement_columns += ")"
    sql_statement_values = sql_statement_values[:-2]
    sql_statement_values += ");"
    return sql_statement_columns + " " + sql_statement_values


def convert_values_to_sql_statement_update(unpacked_values, pk):
    sql_statement_update = "UPDATE geburtstagspersonen SET "
    for key in unpacked_values:
        if key == "geburtstag":
            correct_date = convert_into_date_syntax(unpacked_values[key])
            sql_statement_update += key + "='" + correct_date + "' " + "WHERE id='" + str(pk[0]) + "';"
        else:
            sql_statement_update += key + "='" + unpacked_values[key] + "' " + "WHERE id='" + str(pk[0]) + "';"
    return sql_statement_update


def save_values(packed_values):
    rv_unpacked_values = retrieve_values(packed_values)
    rv_all_filled_out = unfilled_input_fields(rv_unpacked_values)
    if rv_all_filled_out:
        rv_checked_result = check_syntax_values(rv_unpacked_values)
        if rv_checked_result:
            notification_window(rv_checked_result, "260x110")
        else:
            if len(rv_unpacked_values) > 1:
                sql_statement = convert_values_to_sql_statement(rv_unpacked_values)
                rv_db = write_read_in_database("push", sql_statement)
                for message in rv_db:
                    if message == "success":
                        rv_db[0] = "Datensatz ist gespeichert!"
                    else:
                        rv_db[0] = "Ein Error beim speichern!"
                notification_window(rv_db, "240x60")
            else:
                sql_statement_update = convert_values_to_sql_statement_update(rv_unpacked_values,
                                                                              global_pk["pk"].get().split(";"))
                rv_db = write_read_in_database("push", sql_statement_update)
                for message in rv_db:
                    if message == "success":
                        rv_db[0] = "Datensatz wurde aktualisiert!"
                    else:
                        rv_db[0] = "Ein Error beim speichern!"
                notification_window(rv_db, "240x60")
    else:
        notification_window(["Alle Felder ausfüllen!"], "200x60")


def create_dropdown(win, values, row, column):
    var = tk.StringVar(win)
    comb = ttk.Combobox(win, width=10, textvariable=var, values=values, state="readonly")
    comb.grid(row=row, column=column, sticky="nsew")
    comb.current(0)
    return var


def create_fields(keys, global_values, win_size, title):
    global_values.clear()
    window_2 = tk.Toplevel(window_1)
    window_2.title(title)
    window_2.geometry(win_size)
    tk.Label(window_2, text="").grid(row=0, column=0)
    for i, key in enumerate(keys, start=1):
        if key == "geburtstag":
            tk.Label(window_2, text=key.title()+": ", pady=3, padx=5).grid(row=i, column=0, sticky="W")
            days_first = ["{:02d}".format(day_one_digit) for day_one_digit in range(1, 10)]
            days_last = [str(day_two_digits) for day_two_digits in range(10, 32)]
            days = tuple(days_first + days_last)
            months = ('01', '02', '03', '04', '05', '06', '07', '08',
                      '09', '10', '11', '12')
            years = list(range(1920, 2022))
            years = [str(year) for year in years]
            years = tuple(years)
            object_day = create_dropdown(window_2, days, i+1, 0)
            object_month = create_dropdown(window_2, months, i+1, 1)
            object_year = create_dropdown(window_2, years, i+1, 2)
            global_values[key] = [object_year, object_month, object_day]
        elif key == "status":
            tk.Label(window_2, text=key.title() + ": ", pady=3, padx=5).grid(row=i, column=0, sticky="W")
            status_options = ('Familie', 'Freunde', 'Bekannte', 'Arbeit')
            object_status = create_dropdown(window_2, status_options, i, 1)
            global_values[key] = object_status
        else:
            tk.Label(window_2, text=key.title()+": ", pady=3, padx=5).grid(row=i, column=0, sticky="W")
            entry_object = ttk.Entry(window_2, width=13)
            entry_object.grid(row=i, column=1)
            global_values[key] = entry_object
    tk.Button(window_2, text="Speichern", command=lambda: save_values(global_values)).grid(row=7, column=2)


def delete_entry(value_to_delete):
    unpacked_chosen = value_to_delete["pk"].get().split(";")
    sql_statement = "DELETE FROM geburtstagspersonen WHERE id='{}';".format(unpacked_chosen[0])
    rv_db = write_read_in_database("push", sql_statement)
    for message in rv_db:
        if message == "success":
            rv_db[0] = "Datensatz ist gelöscht!"
        else:
            rv_db[0] = "Ein Error beim löschen!"
    notification_window(rv_db, "240x60")


def show_all_persons(header):
    global_pk.clear()
    window_3 = tk.Toplevel(window_1)
    window_3.title("Personenübersicht")
    window_3.geometry("630x250")
    sql_statement = "SELECT * FROM geburtstagspersonen;"
    rv_db = write_read_in_database("pull", sql_statement)
    if rv_db:
        header_copy = header.copy()
        header_copy.insert(0, "id")
        for column, head in enumerate(header_copy):
            tk.Label(window_3, text=head.title(), font="bold", pady=3, padx=12).grid(row=0, column=column, sticky="W")
        count = 0
        for row, entry in enumerate(rv_db, start=1):
            count += 1
            for column, value in enumerate(entry):
                tk.Label(window_3, text=value, pady=3, padx=12).grid(row=row, column=column, sticky="W")
        values_insert = [str(tup[0]) + "; " + str(tup[1]) for tup in rv_db]
        values_insert = tuple(values_insert)
        object_chosen = create_dropdown(window_3, values_insert, count+1, 1)
        global_pk["pk"] = object_chosen
        tk.Button(window_3, text="Löschen",
                  command=lambda: delete_entry(global_pk), width=8).grid(row=count+1, column=2, sticky="E")
        object_chosen_value = create_dropdown(window_3, [head.title() for head in header.copy()], count+2, 1)
        tk.Button(window_3, text="Verändern",
                  command=lambda: create_fields([str(object_chosen_value.get().lower())], global_change_values,
                                                "330x120", "Eintrag ändern"), width=8).\
            grid(row=count+2, column=2, sticky="E")
    else:
        tk.Label(window_3, text="Keine Datensätze sind vorhanden!", pady=20, padx=20, font="bold").grid(row=0, column=0)


main_functions = {"Person anlegen": lambda: create_fields(keys_persons, global_create_values,
                                                          "330x210", "Person anlegen"),
                  "Personen anzeigen": lambda: show_all_persons(keys_persons)}


window_1 = tk.Tk()
window_1.title("Birthday App")
window_1.geometry("250x180")
tk.Label(window_1, text="Hauptmenü", font=("Arial", 18), pady=20).pack()
for func in main_functions:
    tk.Button(window_1, text=func, width=15, command=main_functions[func]).pack()
window_1.mainloop()
