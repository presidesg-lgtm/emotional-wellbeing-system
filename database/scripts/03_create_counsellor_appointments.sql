USE emotional_wellbeing;


CREATE TABLE IF NOT EXISTS counsellor_profiles (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    user_id INT UNSIGNED NOT NULL,

    specialization VARCHAR(150) NOT NULL,

    qualifications VARCHAR(255),

    bio TEXT,

    years_experience INT UNSIGNED DEFAULT 0,

    is_available BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT uq_counsellor_profile_user
        UNIQUE (user_id),

    CONSTRAINT fk_counsellor_profile_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS appointments (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    user_id INT UNSIGNED NOT NULL,

    counsellor_profile_id INT UNSIGNED NOT NULL,

    appointment_date DATE NOT NULL,

    start_time TIME NOT NULL,

    status ENUM(
        'pending',
        'confirmed',
        'completed',
        'cancelled',
        'rejected'
    ) NOT NULL DEFAULT 'pending',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_appointment_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_appointment_counsellor
        FOREIGN KEY (counsellor_profile_id)
        REFERENCES counsellor_profiles(id)
        ON DELETE CASCADE
);