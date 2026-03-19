:fr: *Sommaire*

1. ![Le raisonnement](#comprendre-le-système)
2. ![Comment démarrer le système](#comment-démarrer-le-système)

![schema_fr](infrastructure_schema.png)

# Comprendre le système

Une question vous aura amené ici: **pourquoi** ce système a-t-il été ainsi conçu?

### Base de réflexion

Voyez notre source: une API que l'on peut appeler 5 fois maximum par minute, simulant une transaction. Nous ne disposons d'aucun contrôle sur cet élément, et devons donc travailler avec ce qu'elle nous fournit; parmi ses informations, la colonne 'is_fraud' est facilement remarquable puisqu'il s'agit de notre cible pour la prédiction. Or c'est un élément que nous n'aurions pas en situation réelle, que nous ne pouvons donc pas nous permettre d'utiliser en l'état bien qu'il s'agisse d'une information pratique pour contre-vérifier la réalité face à la prédiction fournie par notre modèle!

À l'opposé, nous avons l'élément au cœur de la prédiction: notre modèle. Si l'on lui fournissait une variable jamais vue avant, il ne saurait pas quoi en faire; une question essentielle surgit alors - les données fournies pour notre entraînement ont-elles le même format que les données fournies par l'API? La réponse est non.

C'est sur ce postulat que la réflexion autour du système débute; s'agissant d'un projet étudiant, nous disposons tout de même de quelques instructions sans oublier le sujet - les pipelines. Par conséquent nous ne toucherons pas aux données d'entraînement; nous ne ferons qu'en isoler la cible, faire un peu de feature engineering et puisque le machine learning n'est pas l'objet premier de ce thème, seuls deux modèles réduits au plus simple feront l'objet d'un entraînement - une régression logistique et une classification *random forest* (pour éviter tout barbarisme linguistique), où nous utiliserons cette dernière puisque plus performante.

À cet égard cependant, notons que leurs performances sont loin d'être impressionantes mais ne sont pas le sujet de ce projet. Intéressons-nous alors au travail d'adaptation autour des données fournies par l'API!

### La procédure d'ETL

De ce thème découle la logique du système: comment transformer la donnée l'alimentant, de sorte à ce qu'elle puisse être reconnue par notre modèle. Référons-nous au schéma en commençant par l'**ETL**: nous extrayons les données de l'API via des commandes bash, cependant les réponses ne sont pas immédiatement sous un format exploitable puisque nous obtenons une réponse html offrant une string contenant un json. S'en suivent un ensemble de transformations **exclusivement** pour permettre d'obtenir une donnée tabulaire, à charger ensuite sur notre PostgreSQL derrière ![Neon](https://neon.com/)!

Il nous faut anticiper les étapes en aval, en vue de la prédiction. Deux envois sont effectués vers Neon: la première table ne contient qu'un argument *append* où l'objectif est de produire un historique des transactions. Indépendemment des besoins en aval, ils deviennent une référence stockant la donnée **brute** qui nous a été fournie, bien qu'elle soit passée d'un format html au SQL! Cette table ne fera qu'accumuler des lignes dans le temps; une méthode plus réaliste aurait été de produire des *batches* plus larges pour un chargement moins fréquent plutôt que de réaliser l'opération à chaque itération, cependant faute d'instructions ce concept aura été ignoré.

Quant à la seconde table, celle-ci est prévue pour ne servir qu'aux besoins opérationnels en aval; celle-ci dispose d'un argument *replace*, où les nouvelles données fournies écrasent constamment les anciennes puisqu'il s'agit du "work in progress". L'objectif est de maintenir une vitesse d'exécution optimale au travers d'une ressource dédiée, non pas de stocker sur la durée!

### Consommation & prédiction

Le contenu de notre "work in progress" est donc ce que nous souhaitons extraire en vue d'une prédiction, dès lors qu'un nouveau *batch* est mis à disposition. C'est le début de l'étape de **consume**, ou consommation de notre donnée: dès acquisition, de nouvelles transformations cette fois sur le contenu sont opérées. Pour rappel, nos données d'entraînement diffèrent sensiblement de celles de l'API; c'est pourquoi nous transformons les données tirées de cette dernière!

L'objectif devient donc de rendre ces données d'API compréhensibles pour notre modèle, de sorte qu'il n'ignore pas les variables qu'il ne connaît pas. D'ailleurs, la plupart des variables produites lors du *feature engineering* se sont avérées avoir un poids important dans les *features* de notre modèle, telles que les périodes de la journée!

Une fois nos données donc transformées et prêtes pour ingestion, nous récupérons également l'objet de *preprocessing* utilisé dans notre modèle pour l'appliquer sur nos données; c'est le détail qui permet d'obtenir l'équivalent de toutes les informations qui ont pu être apprises lors de l'entraînement du modèle.

Venons-en pour finir au **predict**, la prédiction de fraude: si notre modèle estime la transaction comme légitime, son travail s'arrête là. Dans le cas opposé cependant, le résultat ne peut être ignoré; nos instructions n'attendent *que* la production d'une notification dans ce cas, rien de plus. Intervient alors le dernier élément du système où, à chaque label frauduleux produit, un email est envoyé à l'adresse fournie!



# Comment démarrer le système

### Pré-requis