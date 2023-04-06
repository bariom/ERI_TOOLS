######################################################
# Script per popolare i nuovi punti jira nel db livs #
# Cliente BPS                                        #
######################################################

import jaydebeapi
import psycopg2

# Connect to the AS400 using jaydebeapi
conn_as400 = jaydebeapi.connect("com.ibm.as400.access.AS400JDBCDriver",
                                "jdbc:as400://ASGVA01",
                                {"user": "nextlux", "password": "next"},
                                "C:/TEMP/jt400.jar",
)

# Construct the SQL query
sql = "SELECT REF, SUMMARY FROM ERISVN.OVERVIEW_JIRA_73 WHERE PROJECT = 'BPSON-LUG' ORDER BY ID_ISSUE DESC FETCH FIRST 50 ROWS ONLY"

# Execute the query and fetch the results
cur_as400 = conn_as400.cursor()
cur_as400.execute(sql)
results = cur_as400.fetchall()

# Insert the results into the jira table in the PostgreSQL database
conn_pgsql = psycopg2.connect(database="postgres", user="postgres", password="next", host="gvalug04", port="5432")
cur_pgsql = conn_pgsql.cursor()
for ref, summary in results:
    check_sql = "SELECT EXISTS(SELECT 1 FROM jira WHERE jnum = %s)"
    cur_pgsql.execute(check_sql, (ref,))
    if not cur_pgsql.fetchone()[0]:
        insert_sql = "INSERT INTO jira (jnum, jdesc) VALUES (%s, %s)"
        cur_pgsql.execute(insert_sql, (ref, summary))

# Commit the changes and close the cursors and connections
conn_pgsql.commit()
cur_as400.close()
cur_pgsql.close()
conn_as400.close()
conn_pgsql.close()
