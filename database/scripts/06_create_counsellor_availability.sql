CREATE TABLE counsellor_availability_slots (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    counsellor_profile_id INT UNSIGNED NOT NULL,

    slot_date DATE NOT NULL,

    start_time TIME NOT NULL,

    is_booked BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_availability_counsellor_profile
        FOREIGN KEY (counsellor_profile_id)
        REFERENCES counsellor_profiles(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_counsellor_availability_slot
        UNIQUE (
            counsellor_profile_id,
            slot_date,
            start_time
        )
);


ALTER TABLE appointments
    ADD COLUMN availability_slot_id INT UNSIGNED NULL
    AFTER counsellor_profile_id;


ALTER TABLE appointments
    ADD CONSTRAINT fk_appointment_availability_slot
        FOREIGN KEY (availability_slot_id)
        REFERENCES counsellor_availability_slots(id)
        ON DELETE SET NULL;