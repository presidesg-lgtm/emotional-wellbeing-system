USE emotional_wellbeing;


CREATE TABLE IF NOT EXISTS payment_proofs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    appointment_id INT UNSIGNED NOT NULL,

    user_id INT UNSIGNED NOT NULL,

    original_filename VARCHAR(255) NOT NULL,

    stored_filename VARCHAR(255) NOT NULL,

    status ENUM(
        'pending',
        'verified',
        'rejected'
    ) NOT NULL DEFAULT 'pending',

    admin_note VARCHAR(500),

    submitted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    reviewed_at TIMESTAMP NULL DEFAULT NULL,

    CONSTRAINT uq_payment_proof_appointment
        UNIQUE (appointment_id),

    CONSTRAINT fk_payment_proof_appointment
        FOREIGN KEY (appointment_id)
        REFERENCES appointments(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_payment_proof_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);