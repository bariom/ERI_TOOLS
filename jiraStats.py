import psycopg2
import matplotlib.pyplot as plt
import pandas as pd

# Provide your database credentials
hostname = "gvalug04.eri.local"
port = "5432"
database = "postgres"
username = "postgres"
password = "next"

# Connect to the database
try:
    conn = psycopg2.connect(
        host=hostname,
        port=port,
        database=database,
        user=username,
        password=password
    )
    print("Connected to the database successfully!")

    # Retrieve the delivery date and status
    query = "SELECT liv_date, cli_sts FROM bpslivs WHERE cli_sts IS NOT NULL and liv_date > '2023-02-01' ORDER BY liv_date"
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    # Create a pandas DataFrame from the results
    df = pd.DataFrame(results, columns=["liv_date", "cli_sts"])

    # Create a scatter plot of delivery date and status
    plt.scatter(df["liv_date"], df["cli_sts"])
    plt.xlabel("Delivery date")
    plt.ylabel("Delivery status")
    plt.title("Delivery status over time")
    plt.show()

except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")
