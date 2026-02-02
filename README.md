[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)]() [![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)]() [![Scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)]() [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=fff&style=for-the-badge)]() [![NeonDB](https://img.shields.io/badge/Neon_DB-333?style=for-the-badge&logo=postgresql&logoColor=white)]() [![Docker](https://img.shields.io/badge/docker-257bd6?style=for-the-badge&logo=docker&logoColor=white)]() [![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=flat&logo=Apache%20Airflow&logoColor=white)]()

*[English translation](#uk-data-pipelines-for-ai) follows below.*

# <p align="center">Certification AIA - bloc 3 Conception & mise en œuvre de pipelines :fr:</p>

### <p align="center">Jedha: projet détection automatique de fraude</p>
![](/logos/Logo_Jedha.jpg)

Bienvenue dans mon repo dédié au projet de détection automatique de fraude, pour la certification AIA Jedha!

Ce bref projet est consacré à la conception et mise en production d'une infrastructure automatisée incluant des pipelines pour la détection par IA de fraudes bancaires. Vous trouverez ici:

* Le notebook .ipynb incluant le travail sur le machine learning,
* Les dossiers `dags`, `data`, `logs` & `plugins` nécessaires au fonctionnement d'Airflow,
* Le dossier `understanding_infrastructure` expliquant la réflexion derrière ce système,
* Les fichiers `Dockerfile`, `docker-compose.yaml` & `requirements.txt` pour déployer Airflow avec Docker,
* Un guide d'instructions `.env_example.md` pour la création des variables confidentielles d'environnement,
* Un exemple de réponse d'API `test_api.json` explicitant la donnée reçue alimentant ce système,
* L'environnement .yml vous permettant d'exécuter le .ipynb correctement.

> [!NOTE]
> Ce projet s'attend à ce que vous soyez familier avec des outils tels Docker ou Airflow et leur installation/utilisation! Notez également que sans instruction sur la gestion d'exception, lorsque l'API est surchargée et retourne une erreur html 500, le process en cours s'interrompra et il faudra attendre la prochaine itération orchestrée.

> [!WARNING]
> Ce projet implique l'usage d'un outil en ligne sur le modèle économique du *freemium*, par conséquent il vous faudra créer votre propre compte sur le service impliqué et en gérer votre propre utilisation. Suivez attentivement les instructions du guide sur les variables confidentielles!

Bonne exploration! :feet:


---


# <p align="center">:uk: Data pipelines for AI</p>

### <p align="center">Jedha: Automatic fraud detection project</p>
![](/logos/Logo_Jedha.jpg)

Welcome to my repository dedicated to the automatic fraud detection project, for Jedha's certification!

This short project is dedicated to producing & deploying pipelines to automate fraud detection with AI on transactions. You may find here:

* The .ipynb notebook for the machine learning part,
* The `dags`, `data`, `logs` & `plugins` folders required to properly run Airflow,
* The `understanding_infrastructure` folder detailing the thinking behind this system,
* The `Dockerfile`, `docker-compose.yaml` & `requirements.txt` files to deploy Airflow with Docker,
* An instructions file `.env_example.md` to create your confidential environment variables,
* An example of API reply `test_api.json` showing the data format feeding this system,
* The .yml environment to properly run the .ipynb notebook.

> [!NOTE]
> This project expects you to be familiar with tools like Docker or Airflow and their installation/use! Please also note without instructions regarding exception management, should the API reach its limit and return a 500 html error, the current process will be interrupted and you will have to wait for the next orchestrated iteration.

> [!WARNING]
> This project involves an online tool on a *freemium* economical model, hence the need for the user to create their own account on the related service and monitor their own use of it. Make sure to follow the instructions given in the environment template file!

Have fun exploring! :feet: