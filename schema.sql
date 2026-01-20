-- schema.sql
-- Minimal database schema for Ticket System (MariaDB)

CREATE DATABASE IF NOT EXISTS ticketsystem
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ticketsystem;

-- Drop tables (safe reset for development)
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  brukernavn VARCHAR(50) NOT NULL UNIQUE,
  passord VARCHAR(255) NOT NULL,
  rolle ENUM('bruker', 'drift') NOT NULL
) ENGINE=InnoDB;

CREATE TABLE tickets (
  id INT AUTO_INCREMENT PRIMARY KEY,
  bruker_id INT NOT NULL,
  tittel VARCHAR(120) NOT NULL,
  beskrivelse TEXT NOT NULL,
  status ENUM('åpen', 'under_arbeid', 'lukket') NOT NULL DEFAULT 'åpen',
  behandler_id INT NULL,
  opprettet TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_tickets_user
    FOREIGN KEY (bruker_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_tickets_behandler
    FOREIGN KEY (behandler_id) REFERENCES users(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB;
