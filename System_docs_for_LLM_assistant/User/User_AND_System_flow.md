# User - System Flow

**Flux Optimal : Scraper une Page Produit Amazon avec "The Brain" (V1 et Évolution V2)**

Voici un flux complet illustrant comment "The Brain" traite une demande de scraping de manière dynamique, dès une version initiale (V1) sans adaptateurs, et comment il évolue en V2 pour une exécution modulaire. Ce flux respecte la logique "Lego" en permettant l’empilement d’outils dynamiquement sélectionnés selon leurs compatibilités, tout en offrant une flexibilité maximale à l’utilisateur pour exprimer son intention et des mécanismes robustes pour gérer les erreurs ou résultats insatisfaisants.

1. **Intention de l’Utilisateur (Entrée) :**
   - L’utilisateur soumet une requête via le CLI, qui peut être soit une commande structurée, soit une requête textuelle libre reflétant un langage naturel. Exemples :
     - Commande structurée : `brain scrape --url "https://www.amazon.ca/dp/B08WRBGSL2" --extract "price,title" --jscan true`.
     - Requête libre : `brain scrape "Je veux récupérer le prix et le titre d’un produit sur Amazon à cette URL : https://www.amazon.ca/dp/B08WRBGSL2, et le site utilise JavaScript."`
   - Cette entrée est analysée par le module `intent_inference`, conçu pour être permissif et flexible. Grâce à un modèle LLM (Language Model), `intent_inference` traduit aussi bien les commandes structurées que les requêtes libres en un format standardisé `IntentSpec` (JSON structuré) compréhensible par `pipeline_builder`. Exemple de résultat `IntentSpec` :
     ```json
     {
       "target": {
         "type": "url",
         "value": "https://www.amazon.ca/dp/B08WRBGSL2"
       },
       "requirements": {
         "technical": ["javascript_rendering", "html_parsing", "data_extraction"],
         "domain_specific": ["e-commerce", "product_page"]
       },
       "data_to_extract": ["price", "title"],
       "additional_notes": "Site Amazon connu pour contenu dynamique via JavaScript."
     }
     ```
   - **Permissivité de `intent_inference` :** Le LLM intégré est entraîné ou prompté pour interpréter une large gamme de formulations (ex. "Récupère le prix sur Amazon", "Scrape cette page produit", "Je veux des infos sur ce lien"), extraire les éléments clés (URL, besoins techniques, données souhaitées) et combler les lacunes avec des hypothèses raisonnables (ex. si JavaScript n’est pas mentionné explicitement, supposer `javascript_rendering` pour Amazon). En cas d’ambiguïté, le module peut retourner un `IntentSpec` avec des options ou demander une clarification via le CLI (ex. "Confirmez-vous que JavaScript est nécessaire ?").

2. **Pipeline Builder (Construction Dynamique - Sélection et Configuration) :**
   - Le module `pipeline_builder` reçoit l’`IntentSpec` standardisé de `intent_inference` et interroge `tool_registry` (déjà peuplé d’outils comme Playwright, BeautifulSoup4, etc.) pour construire un pipeline adapté :
     - **Étape 1 - Recherche par capacités :** "J’ai besoin d’un outil pour rendre JavaScript. Quels outils ont la capacité `javascript_rendering` dans `tool_registry` ?"
       - Réponse : ["Playwright", "Selenium"] (tous deux de `tool_type: browser`).
     - **Étape 2 - Recherche complémentaire :** "J’ai besoin d’extraire des données ('price', 'title'). Quels outils ont `tool_type: parser` ou la capacité `html_parsing` ?"
       - Réponse : ["BeautifulSoup4", "lxml"].
     - **Étape 3 - Vérification de compatibilité :** "Est-ce que Playwright et BeautifulSoup4 sont compatibles ? Vérification via `check_compatibility(['Playwright', 'BeautifulSoup4'])` ou champ `compatibilities`."
       - Réponse : "Oui, Playwright est compatible avec `type:parser` et BeautifulSoup4 avec `type:browser`."
     - **Étape 4 - Configuration requise :** "Quels sont les `required_config` pour Playwright et BeautifulSoup4 ?"
       - Réponse : "Aucun pour les deux."
     - **Étape 5 - Sélection et configuration :** Le `Builder` choisit Playwright (via une logique simple comme le premier outil ou une heuristique future comme performance) et BeautifulSoup4. Il configure chaque outil pour la tâche spécifique, en s’appuyant sur l’`IntentSpec` et des heuristiques domain-spécifiques (ex. sélecteurs typiques pour Amazon) :
         - Playwright : charger l’URL spécifiée et attendre un sélecteur probable pour le prix.
         - BeautifulSoup4 : extraire le texte des sélecteurs pour "price" et "title".
     - **Étape 6 - Production de la spécification :** Le `Builder` génère une spécification JSON du pipeline, décrivant la séquence d’outils et leurs configurations :
       ```json
       [
         {
           "step": 1,
           "tool": "Playwright",
           "description": "Load page with JavaScript rendering",
           "config": {
             "url": "https://www.amazon.ca/dp/B08WRBGSL2",
             "wait_selector": "span.a-price-whole",
             "headless": true
           }
         },
         {
           "step": 2,
           "tool": "BeautifulSoup4",
           "description": "Extract price and title from HTML",
           "config": {
             "selectors": {
               "price": "span.a-price-whole",
               "title": "#productTitle"
             },
             "extract": "text"
           }
         }
       ]
       ```
   - Cette spécification est générée dynamiquement en temps réel selon les métadonnées de `tool_registry` et l’`IntentSpec`, sans reposer sur des templates statiques. Si un nouvel outil comme "SuperBrowser" est ajouté avec `javascript_rendering`, le `Builder` pourrait le choisir à l’avenir selon des critères supplémentaires (ex. vitesse, fiabilité).

3. **Executor V1 (Exécution Statique Codée en Dur) :**
   - Le module `executor` reçoit la spécification JSON du `pipeline_builder` et exécute chaque étape de la séquence. En V1, sans adaptateurs, il utilise une logique codée en dur spécifique aux outils connus :
     - **Étape 1 - Analyse de la spécification :** Lecture de la première étape : `tool: Playwright` avec sa configuration.
     - **Étape 2 - Exécution spécifique :** Détection de Playwright, exécution d’un bloc de code dédié :
       ```python
       if step['tool'] == 'Playwright':
           config = step['config']
           # Logique codée en dur pour Playwright
           from playwright.async_api import async_playwright
           async def run_playwright():
               async with async_playwright() as p:
                   browser = await p.chromium.launch(headless=config['headless'])
                   page = await browser.new_page()
                   await page.goto(config['url'])
                   try:
                       await page.wait_for_selector(config['wait_selector'], timeout=10000)
                       html_content = await page.content()
                   except Exception as e:
                       html_content = None
                       error_msg = f"Erreur Playwright : {str(e)}"
                   finally:
                       await browser.close()
                   return html_content, error_msg if not html_content else None
           current_data, error = await run_playwright()  # Stocke HTML ou erreur
           if error:
               raise ExecutionError(error)
       ```
     - **Étape 3 - Passage des données :** Lecture de la deuxième étape : `tool: BeautifulSoup4`. Passage des données de l’étape précédente (`current_data` = HTML) à cette étape, si aucune erreur préalable.
     - **Étape 4 - Exécution spécifique :** Détection de BeautifulSoup4, exécution d’un bloc de code dédié :
       ```python
       elif step['tool'] == 'BeautifulSoup4':
           config = step['config']
           # Logique codée en dur pour BeautifulSoup4
           from bs4 import BeautifulSoup
           soup = BeautifulSoup(current_data, 'lxml')
           result = {}
           for key, selector in config['selectors'].items():
               element = soup.select_one(selector)
               result[key] = element.get_text(strip=True) if element else None
           current_data = result  # Stocke résultat (ex. {"price": "123", "title": "Mon Produit"})
       ```
     - **Étape 5 - Résultat final :** Après toutes les étapes, stockage ou retour du résultat final (ex. `{"price": "123", "title": "Mon Produit Incroyable"}`), sauf en cas d’erreur interceptée.
   - **Limitation V1 :** Cet `Executor` ne peut exécuter que les outils pour lesquels il a une logique codée en dur (via `if/elif`). Si un outil inconnu comme "SuperBrowser" est choisi par le `Builder`, l’exécution échoue faute de branche correspondante.

4. **Retour à l’Utilisateur et Nettoyage des Sorties (Sortie Initiale) :**
   - Une fois l’exécution terminée, l’`Executor` transmet le résultat brut à un sous-module ou une fonction de nettoyage (intégrée ou dans un module futur comme `evaluator`) pour garantir que le JSON de sortie est propre et conforme à l’`IntentSpec`. Ce nettoyage inclut :
     - Suppression des balises HTML résiduelles ou des caractères indésirables (ex. `<br>`, `\n` multiples) dans les champs extraits comme "price" ou "title".
     - Validation que les champs demandés dans `IntentSpec` sont présents et non vides.
     - Formatage standardisé (ex. "price" converti en valeur numérique si possible, ou marqué comme "invalide" si non pertinent).
   - Résultat final après nettoyage, retourné à l’utilisateur via le CLI ou l’interface appelante :
     ```json
     {
       "price": "123.00",
       "title": "Mon Produit Incroyable"
     }
     ```
   - En cas d’erreur technique (ex. sélecteur non trouvé, page inaccessible, timeout), un message ou statut d’échec est retourné avec des détails pour guider l’utilisateur vers un ajustement (ex. "Erreur : Sélecteur 'span.a-price-whole' non trouvé, page peut avoir changé").

5. **Validation et Ajustements (Boucle de Feedback Approfondie) :**
   - **Étape 1 - Évaluation du Résultat par l’Utilisateur ou un Système automatique :**
     - Post-exécution, l’utilisateur (ou un module automatisé comme `evaluator` dans une phase future) examine la qualité du résultat renvoyé par l’`Executor` après nettoyage. L’évaluation répond à des questions comme :
       - Les champs demandés ("price", "title") sont-ils présents et corrects ?
       - Les valeurs semblent-elles pertinentes (ex. "price" est-il un nombre valide et non une chaîne comme "Prix non disponible") ?
       - Y a-t-il eu une erreur technique signalée (ex. timeout, page non accessible, sélecteur non trouvé) ?
     - **Cas d’insatisfaction ou d’erreur :**
       - **Résultat insatisfaisant (données vides ou incorrectes) :** Ex. le champ "price" est vide ou contient "N/A", ou le "title" inclut du texte hors sujet comme "Acheter maintenant".
       - **Erreur technique :** Ex. "Sélecteur non trouvé", "Timeout lors du chargement de la page", ou "Erreur réseau 403 (Accès refusé)", ce qui peut indiquer un besoin d’anti-bot ou de proxy non pris en compte initialement.
   - **Étape 2 - Décision sur l’Ajustement Nécessaire et Retour au Module Approprié :**
     - **Retour à `intent_inference` (Cas 1 - Intention mal interprétée ou incomplète) :** Si l’erreur ou le mauvais résultat semble provenir d’une mauvaise compréhension de l’intention utilisateur (ex. l’utilisateur voulait scraper une liste de produits, pas un produit unique, mais l’`IntentSpec` a mal interprété cela), le processus retourne à `intent_inference`. L’utilisateur peut reformuler sa requête initiale ou répondre à une clarification demandée par le système :
       - Exemple : L’utilisateur reformule via CLI : `brain scrape "Je veux les prix de tous les produits listés sur cette page Amazon, pas d’un seul produit."`
       - Le LLM de `intent_inference` met à jour l’`IntentSpec` pour refléter cela (ex. `"data_to_extract": ["list_of_prices"]`, `"requirements": ["pagination_support"]`).
     - **Retour à `pipeline_builder` (Cas 2 - Intention correcte, mais pipeline inadapté) :** Si l’intention était correctement interprétée (l’`IntentSpec` est bon), mais le pipeline généré a échoué ou produit un mauvais résultat (ex. sélecteur incorrect, outil inadapté face à un anti-bot), le processus retourne directement à `pipeline_builder` pour reconstruire ou ajuster le pipeline. Cela peut être déclenché par :
       - Une suggestion automatique du système basée sur l’erreur (ex. "Erreur 403 : Accès refusé, ajout de `cloudscraper` comme anti-bot recommandé").
       - Une intervention utilisateur via CLI (ex. `brain retry --adjust-selector "price:span.a-price-new"` pour changer un sélecteur).
       - `pipeline_builder` reçoit l’`IntentSpec` original (inchangé) et les informations de feedback (ex. type d’erreur, ajustements demandés) pour générer une nouvelle spécification JSON. Exemple d’ajustement :
         - Ajouter un outil comme `cloudscraper` si erreur anti-bot détectée.
         - Modifier les configurations (ex. nouveau sélecteur pour "price").
         - Changer un outil (ex. remplacer Playwright par Selenium si échec persistant dû à détection).
     - **Retour combiné (Cas 3 - Double ajustement) :** Dans certains cas complexes, un retour à `intent_inference` (pour reformuler l’intention) peut précéder un ajustement par `pipeline_builder` (pour reconstruire le pipeline). Exemple : L’utilisateur précise son intention plus clairement, puis ajuste manuellement un sélecteur.
   - **Étape 3 - Reconstruction ou Réutilisation par `pipeline_builder` :**
     - Une fois le feedback traité (via `intent_inference` ou directement), `pipeline_builder` reconstruit une nouvelle spécification JSON si nécessaire, ou réutilise l’existante avec des ajustements mineurs (ex. mise à jour des sélecteurs ou ajout d’un outil). Le processus d’exécution via `executor` redémarre avec cette mise à jour.
   - **Étape 4 - Apprentissage à long terme (Optionnel) :**
     - Si le feedback révèle des problèmes systématiques (ex. incompatibilité non détectée, sélecteurs souvent erronés pour Amazon), cela peut influencer `tool_registry` (ex. mise à jour des métadonnées comme `compatibilities` ou ajout de nouveaux outils). Ce feedback peut également être stocké dans un module futur comme `knowledge_base` pour éviter des erreurs similaires à l’avenir.
   - **Résumé du Feedback :** Le retour à `intent_inference` est nécessaire uniquement si l’intention était mal comprise ; sinon, le retour directe à `pipeline_builder` est privilégié pour ajuster le pipeline. Cela garantit une boucle réactive tout en minimisant les interventions utilisateur inutiles.

6. **Évolution Vers V2 (Executor Dynamique avec Adaptateurs) :**
   - En V2, après validation des fondations (`tool_registry`, `pipeline_builder`, `executor` V1), les adaptateurs remplacent la logique codée en dur dans l’`Executor`. Chaque outil dans `tool_registry` est lié à un adaptateur (via un mécanisme comme une convention de nommage ou un champ dédié), encapsulant sa logique spécifique derrière une interface commune (ex. méthodes `initialize()`, `execute_step(data, config)`).
   - L’`Executor` devient générique :
     - **Étape 1 - Chargement des adaptateurs :** Pour chaque outil de la spécification, chargement dynamique de l’adaptateur correspondant (ex. `playwright_adapter` pour Playwright).
     - **Étape 2 - Exécution standardisée :** Invocation des méthodes communes de l’adaptateur sans connaître les détails internes :
       ```python
       # Executor V2 générique
       current_data = None
       for step in pipeline_spec:
           tool_name = step['tool']
           config = step['config']
           adapter = load_adapter(tool_name)  # Chargement dynamique
           if not adapter:
               raise ExecutorError(f"Adaptateur pour {tool_name} non trouvé")
           current_data = adapter.execute_step(current_data, config)  # Exécution standardisée
       ```
     - **Étape 3 - Résultat final :** Retour du résultat ou gestion des erreurs, sans limitation sur les outils pris en charge (tant qu’un adaptateur existe).
   - Cette évolution rend l’`Executor` capable d’exécuter dynamiquement tout outil sélectionné par le `Builder`, éliminant les blocs `if/elif` codés en dur.

   

7. **Résultat Final (Après Feedback ou Succès Initial) :**

   - Si l'exécution réussit (initialement ou après une boucle de feedback) et que le nettoyage basique a été effectué, le résultat final nettoyé est présenté à l'utilisateur :

     json

     

     ```json
     {
       "price": "123",
       "title": "Mon Produit Incroyable"
     }
     ```

**Résumé du Flux Optimal :**
- **V1 (Simplifiée) :** Intention utilisateur (structurée ou libre) → Analyse permissive via `intent_inference` → Construction dynamique d’une spécification par `pipeline_builder` avec `tool_registry` → Exécution statique par `executor` (logique codée en dur) → Nettoyage et retour du résultat → Feedback pour ajustements (retour à `intent_inference` ou `pipeline_builder` selon le problème).
- **V2 (Dynamique Complète) :** Même flux, mais l’`executor` utilise des adaptateurs pour une exécution générique de tout outil, respectant pleinement la logique "Lego" à chaque étape.
- Ce flux maintient une construction dynamique dès la V1 tout en préparant une exécution modulaire en V2, équilibrant pragmatisme, flexibilité utilisateur, et gestion robuste des erreurs.