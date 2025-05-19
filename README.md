# Epic Events CRM – Interface en ligne de commande

Ce projet est une interface CLI (Command Line Interface) complète pour la gestion du CRM d’Epic Events. Il permet la gestion des utilisateurs, clients, contrats et événements via des commandes sécurisées.

---

## Sommaire

- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration de la base de données](#configuration-de-la-base-de-données)
- [Variables d’environnement](#variables-denvironnement)
- [Initialisation](#initialisation)
- [Utilisation de la CLI](#utilisation-de-la-cli)
- [Structure des commandes](#structure-des-commandes)
- [Tests](#tests)
- [Architecture du projet](#architecture-du-projet)
- [Licence](#licence)
- [Auteurs](#auteurs)

---

## Prérequis

Avant de commencer, assurez-vous d’avoir installé :

- Python 3.10 ou version supérieure  
- MySQL 8 ou version supérieure  
- pip  
- git  

---

## Installation

### 1. Cloner le dépôt

```bash
git clone <https://github.com/ThibaultGERARDIN/pythonProjet12.git>
cd epic-events-crm
```
Renommer le dossier "pythonProjet12" en "epic-events-crm" (ou autre suivant votre préférence)

```bash
cd epic-events-crm
```
### 2. Créer un environnement virtuel

```bash
python -m venv env
```

### 3. Activer l’environnement

#### Sous macOS / Linux :

```bash
source env/bin/activate
```

#### Sous Windows :

```bash
env\Scripts\activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## Configuration de la base de données

Lancer MySQL et créer la base de données et l'utilisateur associé :


```sql
CREATE DATABASE epic_crm;
CREATE USER 'epic_admin'@'localhost' IDENTIFIED BY 'epic_admin_password';
GRANT ALL PRIVILEGES ON epic_crm.* TO 'epic_admin'@'localhost';
FLUSH PRIVILEGES;
```

---

## Variables d’environnement

Créer un fichier `.env` à la racine du projet :

```env
DATABASE_USER=epic_admin
DATABASE_PWD=epic_admin_password
SECRET_KEY=cle_super_secrete
SENTRY_KEY="your_sentry_DSN_key"
MASTER_PASSWORD=mot_de_passe_admin
```

> ⚠️ Ce fichier `.env` ne doit jamais être versionné.

---

## Initialisation

### Créer les tables de la base

```bash
python main.py init-db
```

### Créer un administrateur

```bash
python main.py create-admin
```

Vous devrez entrer le mot de passe maître (défini dans `.env`), puis renseigner les informations de l’administrateur.

---

## Utilisation de la CLI

### Connexion / Déconnexion

```bash
python main.py login
python main.py logout
```

### Afficher l’utilisateur connecté

```bash
python main.py current-user
```

### Créer un utilisateur

```bash
python main.py create-user
```

### Liste des utilisateurs

```bash
python main.py list-users
```

---

## Structure des commandes

### Clients

```bash
python main.py client create
python main.py client list
python main.py client update
python main.py client delete
```

### Contrats

```bash
python main.py contract create
python main.py contract list
python main.py contract update
python main.py contract delete
```

### Événements

```bash
python main.py event create
python main.py event list
python main.py event list-my
python main.py event list-unassigned
python main.py event update
python main.py event delete
```

### Administration

```bash
python main.py reset-db
python main.py delete-users
```

---

## Tests

### Prérequis : création de la base de donnée tests

Lancer MySQL et créer la base de données, accorder les droits à l'utilisateur epic_admin créé précédemment:


```sql
CREATE DATABASE epic_crm_test;
GRANT ALL PRIVILEGES ON epic_crm_test.* TO 'epic_admin'@'localhost';
FLUSH PRIVILEGES;
```

Lancer tous les tests (unitaires et d’intégration) avec :

```bash
pytest
```

Si vous souhaitez générer le rapport de couverture html :

```bash
pytest --cov=. --cov-report html
```
---

## Architecture du projet

- `main.py` – Entrée principale de la CLI  
- `views/` – Commandes CLI (Click)  
- `controllers/` – Logique métier (gestionnaires de modèles)  
- `models/` – ORM SQLAlchemy (clients, contrats, événements, utilisateurs)  
- `tests/` – Dossier de tests  
- `.env` – Variables d’environnement  
- `requirements.txt` – Dépendances Python  

---

## Auteurs

Développé dans le cadre du parcours Développeur Python chez OpenClassrooms.
