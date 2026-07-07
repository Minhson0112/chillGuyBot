ALTER TABLE couple
    ADD COLUMN ring_item_id BIGINT DEFAULT NULL COMMENT 'server item ring used for marriage' AFTER divorcing_at,
    ADD KEY idx_couple_ring_item_id (ring_item_id),
    ADD CONSTRAINT fk_couple_ring_item_id
        FOREIGN KEY (ring_item_id) REFERENCES server_item_master(id)
        ON DELETE RESTRICT;
