import pandas as pd

# read the table from file or create it as a pandas DataFrame
table = pd.read_csv("c:/tmp/pianoconti.csv", delimiter=";")

# iterate over each row in the table
for i, row in table.iterrows():
    tipo = row["TIPO"]
    codice_conto = str(row["CODICE CONTO"])

    # check if the conditions are met
    if tipo == "A" and len(codice_conto) == 7:
        codice_conto = "010" + codice_conto
    elif tipo == "A" and len(codice_conto) == 8:
        codice_conto = "01" + codice_conto
    elif tipo =="P":
        codice_conto = "02" + codice_conto
    elif tipo == "O":
        codice_conto = "21" + codice_conto
    elif tipo =="I":
        codice_conto = "22" + codice_conto
    elif tipo =="R":
        codice_conto = "13" + codice_conto
    elif tipo =="C":
        codice_conto = "14" + codice_conto


    # update the value of the CODICE CONTO column
    table.at[i, "CODICE CONTO"] = codice_conto.zfill(10)

# save the modified table to a new file
table.to_csv("c:/tmp/modified_piano.csv", index=False, sep=";")

# read the modified table from file
table2 = pd.read_csv("c:/tmp/modified_piano.csv", delimiter=";")

# open the output file for writing
with open("c:/tmp/insert_statements.txt", "w") as f:
    # iterate over each row in the table
    for _, row in table2.iterrows():
        # extract the values from the row
        tbcode = str(row["CODICE CONTO"]).zfill(10)
        tbdes1 = str(row["DESCRIZIONE"])[:35]  # truncate to 35 characters if longer
        tbdes2 = str(row["DESCRIZIONE"])[:35]  # truncate to 35 characters if longer
        tbdes3 = str(row["DESCRIZIONE"])[:35]  # truncate to 35 characters if longer
        tbdes4 = str(row["DESCRIZIONE"])[:35]  # truncate to 35 characters if longer


        # generate the INSERT statement for the row
        insert_statement = f"INSERT INTO FDBTAB (TBID, TBCODE, TBETAT, TBDTOU, TBDTMU, TBOPRN, TBDES1, TBDES2, TBDES3, TBDES4, TBCOMP, TBNBRM, TBCOMP2) VALUES ('034', '{tbcode}', ' ', '280323', ' ', '0050091', '{tbdes1}', '{tbdes2}', '{tbdes3}', '{tbdes4}', ' ', 1, ' ');"

        # write the INSERT statement to the output file
        f.write(insert_statement + "\n")

