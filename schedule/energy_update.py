import mysql.connector
from datetime import datetime, timedelta

db_config = {
    'user': 'user',
    'password': 'password',
    'host': 'localhost',
    'database': 'database_name',
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    update_query = """
        UPDATE currencies
        SET energy = CASE
            WHEN energy + 1 <= 20 THEN energy + 1
            ELSE energy
        END
    """
    cursor.execute(update_query)

    conn.commit()

except Exception as err:
    conn.rollback()

    print("Error on /schedule/energy_update:\n", err)
    
finally:
    cursor.close()
    conn.close()