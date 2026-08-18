USE emotional_wellbeing;

CREATE TABLE IF NOT EXISTS mood_entries (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    submitted_text TEXT NOT NULL,
    predicted_emotion ENUM(
        'Sadness',
        'Joy',
        'Love',
        'Anger',
        'Fear',
        'Surprise'
    ) NOT NULL,
    confidence DECIMAL(6, 5) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_mood_entries_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);