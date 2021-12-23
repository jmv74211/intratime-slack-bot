"""
Clockzy tables schema definitions.
"""

USER_TABLE = """ \
    CREATE TABLE IF NOT EXISTS user (
        id VARCHAR(50) NOT NULL,
        user_name VARCHAR(100) NOT NULL,
        password VARCHAR(100) NOT NULL,
        mail VARCHAR(200) NOT NULL,
        entry_data DATETIME,
        last_registration_date DATETIME,
        PRIMARY KEY (id)
    )
"""

CLOCK_TABLE = """ \
    CREATE TABLE IF NOT EXISTS clock (
        id INT NOT NULL AUTO_INCREMENT,
        user_id VARCHAR(50),
        action VARCHAR(20) NOT NULL,
        date_time DATETIME NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES user(id)
    )
"""

COMMANDS_HISTORY_TABLE = """ \
    CREATE TABLE IF NOT EXISTS commands_history (
        id INT NOT NULL AUTO_INCREMENT,
        user_id VARCHAR(50),
        command VARCHAR(50) NOT NULL,
        parameters VARCHAR(150),
        date_time DATETIME NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES user(id)
    )
"""

CONFIG_TABLE = """ \
    CREATE TABLE IF NOT EXISTS config (
        user_id VARCHAR(50),
        intratime_integration BOOLEAN NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id)
    )
"""

ALIAS_TABLE = """ \
    CREATE TABLE IF NOT EXISTS alias (
        user_name VARCHAR(100) NOT NULL,
        alias VARCHAR(100) NOT NULL,
        PRIMARY KEY (user_name)
    )
"""
