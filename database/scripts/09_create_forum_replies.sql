CREATE TABLE forum_replies (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    post_id INT UNSIGNED NOT NULL,
    user_id INT UNSIGNED NOT NULL,
    content VARCHAR(1000) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_forum_replies_post_id (post_id),
    KEY idx_forum_replies_user_id (user_id),
    CONSTRAINT fk_forum_replies_post
        FOREIGN KEY (post_id)
        REFERENCES forum_posts(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_forum_replies_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
