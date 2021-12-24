"""
Clockzy tables schema definitions.
"""

USER_TABLE = 'user'
CLOCK_TABLE = 'clock'
COMMANDS_HISTORY_TABLE = 'command_history'
CONFIG_TABLE = 'config'
ALIAS_TABLE = 'alias'

USER_TABLE_SCHEMA = """ \
    CREATE TABLE IF NOT EXISTS user (
        id VARCHAR(50) NOT NULL,
        user_name VARCHAR(100) NOT NULL,
        password VARCHAR(100),
        email VARCHAR(200),
        entry_data DATETIME,
        last_registration_date DATETIME,
        PRIMARY KEY (id)
    )
"""

CLOCK_TABLE_SCHEMA = """ \
    CREATE TABLE IF NOT EXISTS clock (
        id INT NOT NULL AUTO_INCREMENT,
        user_id VARCHAR(50),
        action VARCHAR(20) NOT NULL,
        date_time DATETIME NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES user(id)
    )
"""

COMMANDS_HISTORY_TABLE_SCHEMA = """ \
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

CONFIG_TABLE_SCHEMA = """ \
    CREATE TABLE IF NOT EXISTS config (
        user_id VARCHAR(50),
        intratime_integration BOOLEAN NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id)
    )
"""

ALIAS_TABLE_SCHEMA = """ \
    CREATE TABLE IF NOT EXISTS alias (
        user_name VARCHAR(100) NOT NULL,
        alias VARCHAR(100) NOT NULL,
        PRIMARY KEY (alias),
        FOREIGN KEY (user_name) REFERENCES user(user_name)
    )
"""
