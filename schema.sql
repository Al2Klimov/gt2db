-- SPDX-License-Identifier: AGPL-3.0-or-later

CREATE TABLE keyword
(
    id        SERIAL,
    keyword   VARCHAR(255) NOT NULL,
    updated   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    past_done BOOLEAN      NOT NULL DEFAULT FALSE,

    CONSTRAINT keyword_pk PRIMARY KEY (id),
    CONSTRAINT keyword_uk_keyword UNIQUE (keyword)
);

CREATE INDEX keyword_ix_updated ON keyword (updated);

CREATE TABLE searches
(
    keyword  INT,
    time     TIMESTAMP,
    searches INT NOT NULL,

    CONSTRAINT searches_pk PRIMARY KEY (keyword, time),
    CONSTRAINT searches_fk_keyword FOREIGN KEY (keyword) REFERENCES keyword (id)
);
