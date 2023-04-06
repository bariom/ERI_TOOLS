import csv

# Definisci le costanti per l'INSERT
tbid = '813'
tbdtou = '040423'
tboprn = '0050001'

# Apri il file CSV di input e crea un file di output per gli statement di INSERT
with open('c:/TEMP/739/ucomuni.csv', newline='') as infile, open('c:/TEMP/739/output813.sql', 'w') as outfile:
    reader = csv.DictReader(infile, delimiter=';')

    # Leggi il file di input riga per riga e genera gli statement di INSERT
    for row in reader:
        # Definisci le variabili per l'INSERT basate sui valori della riga corrente
        zcomune = row['zcomune'].strip()
        zp = row['zp'].strip()
        zcod = row['zcod'].strip()
        zcap = row['zcap'].strip()
        zcab = row['zcab'].strip()
        zst = row['zst'].strip()
        zdescri = row['zdescri'].strip()
        z = row['z'].strip()
        zcabcm = row['zcabcm'].strip()
        zistat = row['zistat'].strip()
        zdatamor = row['zdatamor'].strip()
        zdataacc = row['zdataacc'].strip()
        tbcode = zcap + zcab
        tbdes2 = '     ' + zp

        # Genera lo statement di INSERT per la riga corrente se zp è diverso da 'ES' e scrivilo nel file di output
        if z != 'L':
            if zdatamor == '':
                if zp != 'ES':
                    insert_statement = f"INSERT INTO FDBTAB (TBID, TBCODE, TBDTOU, TBOPRN, TBDES1, TBDES2) VALUES ('{tbid}', '{tbcode}', '{tbdtou}', '{tboprn}', '{zcomune}', '{tbdes2}');"
                    outfile.write(insert_statement + '\n')
