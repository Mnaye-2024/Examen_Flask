# Gestionnaire de Budget Personnel (Flask)

## Objectif du Projet

Cette application web, développée avec le framework Flask, permet à un utilisateur de gérer son budget personnel. L'objectif est de pouvoir enregistrer ses revenus et dépenses, de les classer par catégories, de visualiser un résumé financier via un tableau de bord graphique, et d'exporter ses données.

## Fonctionnalités Clés

*   **Suivi des Transactions :** Enregistrement des revenus et dépenses (montant en XOF, date, catégorie, description).
*   **Catégories Personnalisées :** Création de catégories propres à l'utilisateur (ex: Nourriture, Loyer, Salaire).
*   **Tableau de Bord :** Visualisation rapide du solde (en XOF), des dépenses par catégorie (graphique circulaire) et de l'évolution mensuelle revenus/dépenses (graphique linéaire).
*   **Export :** Exportation des transactions en format PDF ou Excel (.xlsx), avec possibilité de filtrer par date (montants en XOF).
*   **Authentification :** Système d'inscription et de connexion pour que chaque utilisateur accède uniquement à ses données.

## Technologies Principales

*   **Backend :** Python, Flask
*   **Base de Données :** SQLite (via Flask-SQLAlchemy)
*   **Formulaires :** Flask-WTF
*   **Formatage Devise :** Babel
*   **Graphiques :** Chart.js (côté client)
*   **Export :** ReportLab (PDF), openpyxl (Excel)

## Comment Lancer le Projet

**Prérequis :** Python 3 et pip installés.

1.  **Environnement Virtuel :**
    *   Ouvrez un terminal dans le dossier du projet (`budget_app/`).
    *   Créez un environnement virtuel : `python -m venv venv`
    *   Activez-le :
        *   Windows : `.\venv\Scripts\activate`

2.  **Installer les Dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration Minimale :**
    *   Créez un fichier nommé `.env` à la racine du projet.
    *   Ajoutez au minimum une clé secrète :
        ```dotenv
        SECRET_KEY='PAPA-MBAYE'
        # DATABASE_URL est déjà configuré par défaut pour SQLite dans instance/budget.db
        ```
    *   **Important :** Remplacez la valeur par une vraie clé secrète.

4.  **Initialiser la Base de Données :**
    *   (Optionnel, si `flask` n'est pas reconnu directement) : (Windows CMD) ou `$env:FLASK_APP = "run.py"` (PowerShell)
    *   Exécutez :
        ```bash
        flask db migrate -m "Initialisation DB"
        flask db upgrade
        ```
        *(Si `flask db init` n'a jamais été lancé, faites-le avant `migrate`)*



## Utilisation Rapide

1.  Cliquez sur "Inscription" pour créer un compte.
2.  Connectez-vous.
3.  **Important :** Allez dans "Catégories" et ajoutez au moins une catégorie (ex: "Salaire", "Courses").
4.  Allez dans "Ajouter Transaction" pour enregistrer vos premiers revenus/dépenses (les montants sont en Francs CFA).
5.  Explorez le "Tableau de Bord" et la fonction "Exporter".