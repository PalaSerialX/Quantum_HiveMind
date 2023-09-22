-- Create search_results table
CREATE TABLE IF NOT EXISTS search_results (
    id SERIAL PRIMARY KEY,
    uniquetaskid VARCHAR(255),
    Title TEXT,
    URL TEXT,
    IsCherry BOOLEAN,
    Keywords TEXT,
    Timestamp TIMESTAMP,
    Priority INT,
    Status TEXT,
    scraped_text TEXT
);

-- Create chat_history table
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    role TEXT,
    content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);