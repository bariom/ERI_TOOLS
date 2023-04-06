import tkinter as tk
import tkinter.ttk as ttk
import psycopg2
from datetime import datetime
import getpass

# Connect to the PostgresSQL database
conn = psycopg2.connect(
    host="gvalug04.eri.local",
    database="eritools",
    user="postgres",
    password="next"
)

# Create the table to store the stopwatch data
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS stopwatch_data (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255),
        activity VARCHAR(255),
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        elapsed_time INTERVAL
    )
""")
conn.commit()

# Define a function to start the stopwatch
def start_stopwatch():
    global start_time, running
    start_time = datetime.now()
    running = True
    update_stopwatch()

# Define a function to stop the stopwatch
def stop_stopwatch():
    global running
    end_time = datetime.now()
    elapsed_time = end_time - start_time
    elapsed_time_str = str(elapsed_time)
    username = getpass.getuser()
    activity = activity_input.get()

    # Insert the stopwatch data into the database
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO stopwatch_data (username, activity, start_time, end_time, elapsed_time)
        VALUES (%s, %s, %s, %s, %s)
    """, (username, activity, start_time, end_time, elapsed_time))
    conn.commit()

    # Update the GUI to display the elapsed time
    elapsed_time_label.config(text=elapsed_time_str)
    running = False

# Define a function to update the stopwatch
def update_stopwatch():
    if running:
        elapsed_time = datetime.now() - start_time
        elapsed_time_str = str(elapsed_time).split(".")[0]
        stopwatch_label.config(text=elapsed_time_str)
        root.after(1000, update_stopwatch)

# Define a function to show the month's activities
def show_month_activities():
    username = getpass.getuser()
    cur = conn.cursor()
    cur.execute("""
        SELECT activity, start_time, end_time, elapsed_time
        FROM stopwatch_data
        WHERE username = %s AND start_time >= date_trunc('month', CURRENT_DATE)
    """, (username,))
    rows = cur.fetchall()

    # Calculate the total elapsed time for the month
    total_elapsed_time = sum(row[3].total_seconds() for row in rows)
    total_elapsed_time_str = str(datetime.utcfromtimestamp(total_elapsed_time).time())

    # Create a new window to display the data
    activity_window = tk.Toplevel(root)
    activity_window.title("Month's Activities")

    # Create a table to display the data
    table = ttk.Treeview(activity_window, columns=("activity", "start_time", "end_time", "elapsed_time"))
#    table.heading("#0", text="Activity")
    table.column("#0", width=0)
    table.configure(selectmode='none')
    table.heading("activity", text="Activity")
    table.column("activity", anchor="w", width=150)
    table.heading("start_time", text="Start Time")
    table.column("start_time", anchor="w", width=150)
    table.heading("end_time", text="End Time")
    table.column("end_time", anchor="w", width=150)
    table.heading("elapsed_time", text="Elapsed Time")
    table.column("elapsed_time", anchor="w", width=150)
    table.pack()

    # Loop through the rows and add them to the table
    for row in rows:
        activity, start_time, end_time, elapsed_time = row
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
        elapsed_time_str = str(elapsed_time)
        table.insert("", tk.END, text=activity, values=(activity, start_time_str, end_time_str, elapsed_time_str))

    # Add a row for the total elapsed time
    table.insert("", tk.END, text="Total Elapsed Time", values=("", "", "", total_elapsed_time_str))

# Create the GUI
root = tk.Tk()
root.title("Stopwatch")

username_label = tk.Label(root, text="Username:", font=("Arial", 14))
username_label.grid(row=0, column=0)

username_value = getpass.getuser()
username_entry = tk.Label(root, text=username_value, font=("Arial", 12))
username_entry.grid(row=0, column=1)

activity_label = tk.Label(root, text="Activity:")
activity_label.grid(row=1, column=0)

activity_input = tk.Entry(root, width=50)
activity_input.grid(row=1, column=1)

start_button = tk.Button(root, text="Start", command=start_stopwatch)
start_button.grid(row=2, column=0)

stop_button = tk.Button(root, text="Stop", command=stop_stopwatch)
stop_button.grid(row=2, column=1)

show_activities_button = tk.Button(root, text="Show Month's Activities", command=show_month_activities)
show_activities_button.grid(row=3, column=0, columnspan=2)

stopwatch_label = tk.Label(root, text="")
stopwatch_label.grid(row=4, column=0, columnspan=2)

elapsed_time_label = tk.Label(root, text="")
elapsed_time_label.grid(row=5, column=0, columnspan=2)

root.mainloop()