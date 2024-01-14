DROP TABLE IF EXISTS Interprete;
DROP TABLE IF EXISTS Compositeur;
DROP TABLE IF EXISTS Acteur;
DROP TABLE IF EXISTS Realisateur;
DROP TABLE IF EXISTS Auteur;
DROP TABLE IF EXISTS Contributeur CASCADE;
DROP TABLE IF EXISTS Musique;
DROP TABLE IF EXISTS Film;
DROP TABLE IF EXISTS Livre;
DROP TABLE IF EXISTS Exemplaire CASCADE;
DROP TABLE IF EXISTS Ressource CASCADE;
DROP TABLE IF EXISTS EtatExemplaire;
DROP TABLE IF EXISTS Sanction;
DROP TABLE IF EXISTS Adhesion;
DROP TABLE IF EXISTS Empreinte;
DROP TABLE IF EXISTS Adherent;
DROP TABLE IF EXISTS Personnel;
DROP TABLE IF EXISTS Historique;
DROP TABLE IF EXISTS Membre;
DROP TABLE IF EXISTS CompteUtilisateur;
DROP TABLE IF EXISTS POPULARITE;

CREATE TABLE EtatExemplaire (
    nom VARCHAR(30) PRIMARY KEY

);

CREATE TABLE Ressource (
    code VARCHAR(20) PRIMARY KEY,
    titre VARCHAR(30),
    dateApparition DATE,
    editeur VARCHAR(30),
    genre VARCHAR(30),
    codeClassification VARCHAR(30) UNIQUE
);
CREATE TABLE Exemplaire (
    idExemplaire SERIAL PRIMARY KEY,
    etat VARCHAR(30) NOT NULL REFERENCES EtatExemplaire(nom),
    disponible BOOLEAN,
    ressource VARCHAR(30) NOT NULL REFERENCES Ressource(code) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Livre (
    code VARCHAR(20) PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    resume VARCHAR(255),
    langue VARCHAR(30),
    FOREIGN KEY (code) REFERENCES Ressource(code) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE Film (
    code  VARCHAR(20) PRIMARY KEY,
    langue VARCHAR(30),
    longueur INTEGER NOT NULL,
    synopsis VARCHAR(255),
    FOREIGN KEY (code) REFERENCES Ressource(code) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE Musique (
    code  VARCHAR(20) PRIMARY KEY,
    longueur INTEGER,
    FOREIGN KEY (code) REFERENCES Ressource(code) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE Contributeur (
    idContributeur VARCHAR(10) PRIMARY KEY,
    nom VARCHAR(30) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    dateNaissance DATE,
    nationalite VARCHAR(30)
);
CREATE TABLE Auteur (
    contributeur VARCHAR(10) REFERENCES Contributeur(idContributeur) ON DELETE CASCADE ON UPDATE CASCADE,
    code VARCHAR(10) REFERENCES Ressource(code) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (contributeur, code)
);
CREATE TABLE Acteur (
    contributeur VARCHAR(10) REFERENCES Contributeur(idContributeur) ON DELETE CASCADE ON UPDATE CASCADE,
    code VARCHAR(10) REFERENCES Ressource(code) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (contributeur, code)
);
CREATE TABLE Realisateur (
    contributeur VARCHAR(10) REFERENCES Contributeur(idContributeur) ON DELETE CASCADE ON UPDATE CASCADE,
    code VARCHAR(10) REFERENCES Ressource(code) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (contributeur, code)
);
CREATE TABLE Compositeur (
    contributeur VARCHAR(10) REFERENCES Contributeur(idContributeur) ON DELETE CASCADE ON UPDATE CASCADE,
    code VARCHAR(10) REFERENCES Ressource(code) ON DELETE CASCADE ON UPDATE CASCADE, 
    PRIMARY KEY (contributeur, code)
);
CREATE TABLE Interprete (
    contributeur VARCHAR(10) REFERENCES Contributeur(idContributeur) ON DELETE CASCADE ON UPDATE CASCADE,
    code VARCHAR(10) REFERENCES Ressource(code) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (contributeur, code)
);
CREATE TABLE CompteUtilisateur (
    Login VARCHAR(7) PRIMARY KEY,
    Mdp VARCHAR(255) NOT NULL
);
CREATE TABLE Membre (
 
    nom VARCHAR(50),
    prenom VARCHAR(50),
    adresse VARCHAR(100),
      dateDeNaissance DATE,
    Mail VARCHAR(30) PRIMARY KEY
);
CREATE TABLE Historique (
    Login VARCHAR(7) REFERENCES CompteUtilisateur(Login) ON DELETE CASCADE ON UPDATE CASCADE,
    Mail VARCHAR(255) REFERENCES Membre(Mail) ON DELETE CASCADE ON UPDATE CASCADE,
    Debut DATE NOT NULL,
    Fin DATE NOT NULL,
    PRIMARY KEY (Login, Mail),
    CHECK (Debut < Fin)
);
CREATE TABLE Personnel (
    Mail VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (Mail) REFERENCES Membre(Mail) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Adherent (
  Mail VARCHAR(255) PRIMARY KEY,
  telephone integer,
FOREIGN KEY (Mail) REFERENCES Membre(Mail) ON DELETE CASCADE ON UPDATE CASCADE

);
CREATE TABLE Empreinte (
    DateEmpreinte DATE,
    Duree TIME,
    codeRessource SERIAL REFERENCES EXEMPLAIRE(idexemplaire) ON DELETE CASCADE ON UPDATE CASCADE,
    Mailadherent VARCHAR(255) REFERENCES Adherent(Mail) ON DELETE CASCADE ON UPDATE CASCADE,
		PRIMARY KEY(DATEEmpreinte, codeRessource)
);
CREATE TABLE Adhesion (
    DateDebut DATE,
    DateFin DATE,
    MailAdherent VARCHAR(255) REFERENCES Adherent(Mail) ON DELETE CASCADE ON UPDATE CASCADE primary key,
    CHECK (DateDebut < DateFin)
);
CREATE TABLE Sanction (
    Type VARCHAR(20),
    DateDebut DATE,
    DateFin DATE,
    Mailadherent  VARCHAR(255) REFERENCES Adherent(Mail) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (Mailadherent,Type),
    CHECK (Type IN ('RETARD', 'PERTE', 'BLACKLIST'))
);
CREATE TABLE POPULARITE(
    CODE VARCHAR(20) REFERENCES RESSOURCE(code) ON DELETE CASCADE ON UPDATE CASCADE, dateEmprunts DATE NOT NULL);

CREATE OR REPLACE FUNCTION insert_into_popularite()
RETURNS TRIGGER AS $$
DECLARE
    resource_code VARCHAR(20);
BEGIN
    SELECT RESSOURCE.code INTO resource_code
    FROM RESSOURCE 
    JOIN EXEMPLAIRE ON RESSOURCE.code = EXEMPLAIRE.ressource 
    WHERE idexemplaire = NEW.codeRessource;

    INSERT INTO POPULARITE (CODE, dateEmprunts)
    VALUES (resource_code, NEW.DateEmpreinte);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_insert_into_popularite
AFTER INSERT ON Empreinte
FOR EACH ROW
EXECUTE FUNCTION insert_into_popularite();

INSERT INTO EtatExemplaire VALUES ('neuf');
INSERT INTO EtatExemplaire VALUES ('bon');
INSERT INTO EtatExemplaire VALUES ('abime');
INSERT INTO EtatExemplaire VALUES ('perdu');
INSERT INTO Ressource VALUES ('B1234', 'Le Petit Prince', '1990-05-15', 'Gallimard', 'Littérature', 'LIV1');
INSERT INTO Ressource VALUES ('F5678', 'Inception', '2010-07-16', 'Warner Bros', 'Science-fiction', 'FILM1');


INSERT INTO Membre (nom, prenom, adresse, dateDeNaissance, Mail) VALUES
('Doe', 'John', '123 Rue des Lilas, Paris', '1990-05-15', 'john.doe@email.com');

INSERT INTO Membre (nom, prenom, adresse, dateDeNaissance, Mail) VALUES
('Smith', 'Jane', '456 Avenue des Roses, Lyon', '1988-03-20', 'jane.smith@email.com');

INSERT INTO Membre (nom, prenom, adresse, dateDeNaissance, Mail) VALUES
('Martin', 'Luc', '789 Boulevard des Oiseaux, Marseille', '1995-07-10', 'luc.martin@email.com');

INSERT INTO Exemplaire (etat, disponible, ressource) VALUES ('neuf', TRUE, 'B1234');
INSERT INTO Exemplaire (etat, disponible, ressource) VALUES ('bon', FALSE, 'F5678');

INSERT INTO Livre VALUES ('B1234', '9782070612758', 'Histoire d un jeune garçon sur une autre planète', 'Français');

INSERT INTO Film VALUES ('F5678', 'Anglais', 148, 'Un rêve dans un rêve');

INSERT INTO Contributeur VALUES ('CTR1', 'Saint-Exupéry', 'Antoine', '1900-06-29', 'Française');
INSERT INTO Contributeur VALUES ('CTR2', 'Nolan', 'Christopher', '1970-07-30', 'Américaine');

INSERT INTO Auteur VALUES ('CTR1', 'B1234');
INSERT INTO Auteur VALUES ('CTR2', 'F5678');

INSERT INTO CompteUtilisateur VALUES ('alice', 'motdepassealice');
INSERT INTO CompteUtilisateur VALUES ('bob', 'motdepassebob');
INSERT INTO CompteUtilisateur VALUES ('luc', 'motdepasseluc');

INSERT INTO Historique VALUES ('alice', 'john.doe@email.com', '2022-01-10', '2022-12-10');
INSERT INTO Historique VALUES ('bob', 'jane.smith@email.com', '2022-02-15', '2023-08-15');
INSERT INTO Historique VALUES ('luc', 'luc.martin@email.com', '2021-02-15', '2023-02-15');

INSERT INTO Adherent VALUES('jane.smith@email.com', 0783339092);



INSERT INTO Sanction
VALUES ('RETARD', '2022-04-15', '2022-05-15', 'jane.smith@email.com');

INSERT INTO Adhesion VALUES ('2022-02-15', '2023-02-15', 'jane.smith@email.com');
INSERT INTO Empreinte VALUES ('2022-03-05', '15:45:00', '1', 'jane.smith@email.com');
INSERT INTO Ressource VALUES ('R8901', 'La Flûte enchantée', '1791-09-30', 'Mozart Productions', 'Classique', 'MUS1');


INSERT INTO Musique VALUES ('R8901', 180);
INSERT INTO Contributeur VALUES ('CTR3', 'Mozart', 'Wolfgang Amadeus', '1756-01-27', 'Autrichienne');
INSERT INTO Compositeur (contributeur, code) VALUES ('CTR3', 'R8901');
INSERT INTO Contributeur VALUES ('CTR4', 'Doe', 'John', '1980-05-10', 'Américaine');
INSERT INTO Interprete (contributeur, code) VALUES ('CTR4', 'R8901');

INSERT INTO Personnel (Mail)
VALUES ('luc.martin@email.com');

