CREATE TABLE IF NOT EXISTS users (
    id INTEGER,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    PRIMARY KEY(id)
);
CREATE UNIQUE INDEX IF NOT EXISTS username ON users (username);

CREATE TABLE IF NOT EXISTS sentmessages (
    id INTEGER,
    user_id INTEGER,
    timemessages DEFAULT CURRENT_TIMESTAMP NOT NULL,
    messages TEXT NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);