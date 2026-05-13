-- OM 2021.02.17
-- FICHIER MYSQL POUR FAIRE FONCTIONNER LES EXEMPLES
-- DE REQUETES MYSQL
-- Database: FAVRE_YAEL_DEVA1A_STOCK_164_2026

-- Destruction de la BD si elle existe.
-- Pour être certain d'avoir la dernière version des données

DROP DATABASE IF EXISTS FAVRE_YAEL_DEVA1A_STOCK_164_2026;
CREATE DATABASE IF NOT EXISTS FAVRE_YAEL_DEVA1A_STOCK_164_2026;
USE FAVRE_YAEL_DEVA1A_STOCK_164_2026;

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

-- ============================
-- TABLES
-- ============================

DROP TABLE IF EXISTS `t_session`;
CREATE TABLE `t_session` (
  `id_session` int(11) NOT NULL,
  `fk_personne` int(11) DEFAULT NULL,
  `nom` varchar(50) NOT NULL,
  `prenom` varchar(50) NOT NULL,
  `mot_de_passe` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_connexion`;
CREATE TABLE `t_connexion` (
  `id_connexion` int(11) NOT NULL,
  `fk_session` int(11) NOT NULL,
  `date_debut` datetime NOT NULL,
  `date_fin` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_marque`;
CREATE TABLE `t_marque` (
  `id_marque` int(11) NOT NULL,
  `nom` varchar(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_modele`;
CREATE TABLE `t_modele` (
  `id_modele` int(11) NOT NULL,
  `fk_marque` int(11) DEFAULT NULL,
  `nom` varchar(150) NOT NULL,
  `annee` year(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_produit`;
CREATE TABLE `t_produit` (
  `id_produit` int(11) NOT NULL,
  `fk_modele` int(11) DEFAULT NULL,
  `type` varchar(50) NOT NULL,
  `prix` decimal(10,2) NOT NULL,
  `quantite_stock` smallint(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_taille`;
CREATE TABLE `t_taille` (
  `id_taille` int(11) NOT NULL,
  `taille` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_link_produit_taille`;
CREATE TABLE `t_link_produit_taille` (
  `fk_produit` int(11) NOT NULL,
  `fk_taille` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `t_mouvement`;
CREATE TABLE `t_mouvement` (
  `id_action` int(11) NOT NULL,
  `fk_session` int(11) NOT NULL,
  `fk_produit` int(11) NOT NULL,
  `type_action` enum('DEPOT','RETRAIT') NOT NULL,
  `quantite` smallint(11) NOT NULL,
  `date` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ============================
-- INDEXES
-- ============================

ALTER TABLE `t_session`
  ADD PRIMARY KEY (`id_session`);

ALTER TABLE `t_connexion`
  ADD PRIMARY KEY (`id_connexion`),
  ADD KEY `fk_session` (`fk_session`);

ALTER TABLE `t_marque`
  ADD PRIMARY KEY (`id_marque`);

ALTER TABLE `t_modele`
  ADD PRIMARY KEY (`id_modele`),
  ADD KEY `fk_marque` (`fk_marque`);

ALTER TABLE `t_produit`
  ADD PRIMARY KEY (`id_produit`),
  ADD KEY `fk_modele` (`fk_modele`);

ALTER TABLE `t_taille`
  ADD PRIMARY KEY (`id_taille`);

ALTER TABLE `t_link_produit_taille`
  ADD PRIMARY KEY (`fk_produit`,`fk_taille`),
  ADD KEY `fk_taille` (`fk_taille`);

ALTER TABLE `t_mouvement`
  ADD PRIMARY KEY (`id_action`),
  ADD KEY `fk_session` (`fk_session`),
  ADD KEY `fk_produit` (`fk_produit`);

-- ============================
-- AUTO INCREMENT
-- ============================

ALTER TABLE `t_session`
  MODIFY `id_session` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `t_connexion`
  MODIFY `id_connexion` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `t_marque`
  MODIFY `id_marque` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `t_modele`
  MODIFY `id_modele` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `t_produit`
  MODIFY `id_produit` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `t_taille`
  MODIFY `id_taille` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `t_mouvement`
  MODIFY `id_action` int(11) NOT NULL AUTO_INCREMENT;

-- ============================
-- FOREIGN KEYS
-- ============================

ALTER TABLE `t_connexion`
  ADD CONSTRAINT `t_connexion_ibfk_1` FOREIGN KEY (`fk_session`) REFERENCES `t_session` (`id_session`);

ALTER TABLE `t_modele`
  ADD CONSTRAINT `t_modele_ibfk_1` FOREIGN KEY (`fk_marque`) REFERENCES `t_marque` (`id_marque`);

ALTER TABLE `t_produit`
  ADD CONSTRAINT `t_produit_ibfk_1` FOREIGN KEY (`fk_modele`) REFERENCES `t_modele` (`id_modele`);

ALTER TABLE `t_link_produit_taille`
  ADD CONSTRAINT `t_link_produit_taille_ibfk_1` FOREIGN KEY (`fk_produit`) REFERENCES `t_produit` (`id_produit`),
  ADD CONSTRAINT `t_link_produit_taille_ibfk_2` FOREIGN KEY (`fk_taille`) REFERENCES `t_taille` (`id_taille`);

ALTER TABLE `t_mouvement`
  ADD CONSTRAINT `t_mouvement_ibfk_1` FOREIGN KEY (`fk_session`) REFERENCES `t_session` (`id_session`),
  ADD CONSTRAINT `t_mouvement_ibfk_2` FOREIGN KEY (`fk_produit`) REFERENCES `t_produit` (`id_produit`);

COMMIT;

