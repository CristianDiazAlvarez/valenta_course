
# Connect to MySQL
conn = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# Create a cursor object
cur = conn.cursor()

# Create table if not exists
create_table_query = """
CREATE TABLE IF NOT EXISTS penguins (
    species VARCHAR(20),
    island VARCHAR(20),
    bill_length_mm FLOAT,
    bill_depth_mm FLOAT,
    flipper_length_mm FLOAT,
    body_mass_g FLOAT,
    sex VARCHAR(10),
    year INT
)
"""
cur.execute(create_table_query)

# Insert data row by row
insert_query = """
INSERT INTO penguins (species, island, bill_length_mm, bill_depth_mm, flipper_length_mm, body_mass_g, sex, year)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

for _, row in penguins.iterrows():
    cur.execute(insert_query, tuple(row))
    #print(tuple(row))
    
conn.commit()
cur.close()
conn.close()

print("Penguins dataset loaded into MySQL using pymysql!")