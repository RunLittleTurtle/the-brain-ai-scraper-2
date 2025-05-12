# [module] tool_registry

tool_registry/
  ├── __init__.py
  ├── models.py           # Modèles Pydantic pour les métadonnées des outils
  ├── core_tool.py        # Logique principale (gestion des outils, compatibilités, adaptateurs)
  ├── exceptions.py       # Exceptions personnalisées pour gérer les erreurs spécifiques
  ├── cli.py              # Interface CLI pour interagir avec le registre des outils
  └── tests/              # Tests unitaires pour valider le module
      ├── __init__.py
      ├── test_models.py  # Tests des modèles Pydantic
      └── test_core_tool.py  # Tests de la logique principale

## Description
Le module `tool_registry` est le catalogue centralisé des outils de scraping et d’automatisation web pour "The Brain". Il stocke les métadonnées des outils (nom, type, mode d’exécution, capacités, compatibilités) et permet leur gestion via une interface CLI et des fonctions API internes. Ce module est crucial pour que d’autres modules, comme `pipeline_builder`, puissent sélectionner et empiler des outils compatibles de manière dynamique, comme des "Lego", afin de construire des pipelines de scraping adaptés à chaque requête. Il est conçu pour être autonome, ne dépendant d’aucun autre module, et vise à minimiser les erreurs en fournissant des règles claires pour la compatibilité et l’adaptabilité des outils.

## Objectif Principal pour le LLM
Permettre la création d’**adaptateurs** simples et standardisés pour chaque outil, facilitant leur empilement dans des pipelines. Les adaptateurs doivent agir comme des interfaces uniformes, transformant les spécificités de chaque outil en un format commun compatible avec le système (par exemple, un adaptateur pour "Playwright" gère ses particularités tout en offrant une interface générique exploitable par "The Brain"). Cette logique "Lego" repose sur des métadonnées précises (notamment `compatibilities` et `capabilities`) et des fonctions de vérification des compatibilités.

## Dépendances

*   **Interne:** Aucune dépendance stricte sur d'autres modules *pour l'implémentation de base*. Utilisera `config_secrets` plus tard pour gérer le chemin de `tools.json`.



## Inputs / Outputs

*   **Inputs (CLI):**
    *   `brain tools add -f <tool_metadata.json>`: Ajoute un nouvel outil depuis un fichier JSON respectant le schéma `ToolMetadata`.
    *   `brain tools list [--type <type>] [--capability <cap>]`: Liste les outils enregistrés, avec filtres optionnels par type ou capacité.
    *   `brain tools remove <tool_name>`: Supprime un outil du registre en utilisant son nom unique.
    *   `brain tools check-compat <name1> <name2> [<name3>...]`: Vérifie si une liste d'outils (par nom) sont compatibles entre eux selon les règles du registre.
*   **Inputs (API Python - Fonctions/Méthodes Internes):**
    *   `registry.add_tool(metadata: ToolMetadata)`: Ajoute ou met à jour un outil dans le registre. Valide via Pydantic.
    *   `registry.get_tool(name: str) -> Optional[ToolMetadata]`: Récupère les métadonnées complètes d'un outil par son nom unique. Retourne `None` si non trouvé.
    *   `registry.list_tools(tool_type: Optional[str] = None, capability: Optional[str] = None) -> List[ToolMetadata]`: Retourne une liste filtrée d'outils.
    *   `registry.remove_tool(name: str) -> bool`: Supprime un outil par son nom. Retourne `True` si succès, `False` si non trouvé.
    *   `registry.check_compatibility(names: List[str]) -> bool`: Vérifie si tous les outils dans la liste de noms sont compatibles entre eux.
    *   `registry.find_compatible_tools(name: str, target_type: Optional[str] = None) -> List[ToolMetadata]`: Trouve tous les outils enregistrés qui sont compatibles avec l'outil spécifié (filtrable par type cible).
*   **Outputs (CLI):**
    *   Affichage JSON formaté pour les listes.
    *   Messages de statut clairs (succès, erreur de validation, outil non trouvé, etc.).
    *   Sortie booléenne (texte "Compatible" / "Non compatible") pour `check-compat`.
*   **Outputs (API Python):**
    *   Instances de `ToolMetadata` ou `List[ToolMetadata]`.
    *   `bool` pour les vérifications de compatibilité ou succès de suppression.
    *   `None` si un outil n'est pas trouvé par `get_tool`.
    *   Lève des exceptions spécifiques (ex: `ToolValidationError`, `ToolNotFoundError`) pour les erreurs.
*   **Stockage:**
    *   La liste complète des `ToolMetadata` est persistée dans un fichier `tools.json`.
    *   L'emplacement idéal de ce fichier est un répertoire de configuration utilisateur (ex: `~/.thebrain/config/tools.json`) plutôt que dans le code source. La localisation exacte sera gérée via le module `config_secrets` à terme, mais pour l'implémentation initiale, un chemin par défaut peut être utilisé.

## Fonctionnalités Encapsulées

*   **Gestion du Catalogue:** Maintient une liste à jour des outils disponibles.
*   **Persistance:** Chargement au démarrage et sauvegarde des modifications dans `tools.json`.
*   **Validation Stricte:** Utilisation de Pydantic (`ToolMetadata`) pour garantir la structure et le type correct des données de chaque outil.
*   **CRUD Complet:** Ajout (`add`), Lecture (`get`, `list`), Suppression (`remove`) des outils.
*   **Logique de Compatibilité:** Implémente les règles pour vérifier si des outils peuvent fonctionner ensemble (`check_compatibility`) et pour trouver des partenaires potentiels (`find_compatible_tools`).
*   **Interface d'Accès Claire:** Fournit à la fois une API Python pour les autres modules et une interface CLI pour l'utilisateur/admin.
*   **Gestion d'Erreurs:** Utilise des exceptions personnalisées pour signaler les problèmes (validation, outil non trouvé).

## Schéma Pydantic & Format JSON (ToolMetadata)

Chaque outil dans `tools.json` (qui est une liste `[...]` de ces objets) **doit** respecter ce schéma. Représentation JSON du modèle Pydantic attendu (`models.py`):

```json
{
  "title": "ToolMetadata",
  "description": "Représente les métadonnées essentielles d'un outil intégrable dans les pipelines The Brain.",
  "type": "object",
  "properties": {
    "name": {
      "title": "Name",
      "description": "Nom unique et identifiant de l'outil (ex: 'playwright', 'requests', 'beautifulsoup4'). Utilisé comme ID.",
      "type": "string"
    },
    "description": {
      "title": "Description",
      "description": "Courte description textuelle expliquant le rôle principal de l'outil.",
      "type": "string"
    },
    "tool_type": {
      "title": "Tool Type",
      "description": "Catégorie fonctionnelle principale de l'outil (ex: 'browser', 'http_client', 'parser', 'anti_bot_service', 'captcha_solver', 'proxy_manager', 'data_storage').",
      "type": "string"
    },
    "package_name": {
      "title": "Package Name",
      "description": "Nom du package Python à installer via pip (ex: 'playwright', 'requests', 'beautifulsoup4').",
      "type": "string"
    },
    "pip_install_command": {
      "title": "Pip Install Command",
      "description": "Commande pip exacte pour installer l'outil et ses dépendances spécifiques si nécessaire (ex: 'pip install playwright', 'pip install beautifulsoup4[lxml]').",
      "type": "string",
      "default": "pip install {package_name}"
    },
    "execution_mode": {
      "title": "Execution Mode",
      "description": "Mode d'exécution principal ('sync' ou 'async'). Crucial pour l'orchestration par le module 'executor'.",
      "enum": ["sync", "async"],
      "type": "string"
    },
    "capabilities": {
      "title": "Capabilities",
      "description": "Liste des capacités ou fonctionnalités clés offertes par l'outil (tags utiles pour la sélection, ex: 'javascript_rendering', 'anti_cloudflare', 'proxy_rotation', 'html_parsing', 'xml_parsing', 'json_parsing', 'captcha_solving', 'session_management', 'form_submission', 'headless_mode', 'http2_support').",
      "type": "array",
      "items": { "type": "string" }
    },
    "compatibilities": {
      "title": "Compatibilities",
      "description": "Liste des **noms** ou **types ('type:*')** d'autres outils avec lesquels cet outil est conçu pour interagir directement ou est généralement utilisé en conjonction (ex: un parser est compatible avec 'type:browser' et 'type:http_client').",
      "type": "array",
      "items": { "type": "string" },
      "default": []
    },
    "incompatible_with": {
    "type": "array",
    "description": "Liste des noms d’outils ou types d’outils (préfixés par 'type:', ex. 'type:browser') avec lesquels cet outil est explicitement incompatible et ne peut pas fonctionner dans un même pipeline, en raison de conflits techniques ou de comportements divergents. Prend le pas sur une compatibilité implicite.",
    "items": {"type": "string"},
    "default": [],
    "required": false
  },
    "required_config": {
      "title": "Required Config",
      "description": "Liste des noms des clés de configuration ou secrets qui DOIVENT être fournis (via le module 'config_secrets') pour que cet outil fonctionne (ex: ['SCRAPERAPI_KEY', 'ANTICAPTCHA_KEY']).",
      "type": "array",
      "items": { "type": "string" },
      "default": []
    }
  },
  "required": [
    "name",
    "description",
    "tool_type",
    "package_name",
    "execution_mode",
    "capabilities"
  ]
}
```
## Exemples concrets
```json
### Exemple 1: Outil de type "browser" (playwright.json)
{
  "name": "playwright",
  "description": "Un framework d'automatisation de navigateur moderne et puissant développé par Microsoft. Permet de contrôler Chromium, Firefox et WebKit via une API Python unifiée (synchrone et asynchrone). Idéal pour les sites web complexes nécessitant une exécution JavaScript complète (Single Page Applications), la simulation d'interactions utilisateur avancées (clics, formulaires, navigation) et la gestion de contextes de navigateur isolés. Offre des capacités d'interception réseau et de prise de captures d'écran/PDF.",
  "tool_type": "browser",
  "package_name": "playwright",
  "pip_install_command": "pip install playwright==1.40.0 && playwright install --with-deps",
  "execution_mode": "async",
  "capabilities": [
    "javascript_rendering",
    "spa_support",
    "headless_mode",
    "headed_mode",
    "screenshot",
    "pdf_generation",
    "network_interception",
    "network_mocking",
    "multi_browser_support",
    "user_input_simulation",
    "form_submission",
    "iframe_handling",
    "shadow_dom_support",
    "geolocation_mocking",
    "permissions_handling",
    "downloads_handling",
    "video_recording"
  ],
  "compatibilities": [
    "type:parser",
    "type:captcha_solver",
    "type:proxy_manager",
    "type:anti_bot_service"
  ],
  "required_config": []
}

### Exemple 2: Outil de type "parser" (beautifulsoup4.json)
{
  "name": "beautifulsoup4",
  "description": "Une bibliothèque Python extrêmement populaire pour extraire des données de fichiers HTML et XML. Elle crée un arbre d'analyse pour le contenu parsé, facilitant la navigation, la recherche et la modification des données. Fonctionne avec différents parseurs sous-jacents (comme lxml, html5lib, html.parser) pour offrir flexibilité et robustesse, même face à du balisage mal formé. Permet de rechercher des éléments via des sélecteurs CSS, des noms de balises, des attributs, et du texte. Principalement synchrone.",
  "tool_type": "parser",
  "package_name": "beautifulsoup4",
  "pip_install_command": "pip install beautifulsoup4[lxml]==4.12.2",
  "execution_mode": "sync",
  "capabilities": [
    "html_parsing",
    "xml_parsing",
    "malformed_markup_handling",
    "css_selectors",
    "xpath_support",
    "tag_navigation",
    "attribute_extraction",
    "text_extraction",
    "encoding_detection"
  ],
  "compatibilities": [
    "type:http_client",
    "type:browser"
  ],
  "required_config": []
}

```
## API Utiles pour la Construction de Pipelines

- `check_compatibility(tool_ids: List[str]) -> bool` : Vérifie si une liste d’outils est compatible pour un pipeline.
- `find_compatible_tools(tool_id: str) -> List[ToolSpec]` : Retourne la liste des outils compatibles avec un outil donné.
- `get_tools_by_capability(capability: str) -> List[ToolSpec]` : Liste les outils ayant une capacité spécifique.
- `add_tool(tool_spec: dict) -> ToolSpec` : Ajoute un outil et retourne ses métadonnées validées.
- `get_tool(tool_id: str) -> ToolSpec` : Récupère un outil par son ID unique.


## Tests de Régression CLI

- `brain tools add -f playwright.json` : Ajoute un outil depuis un fichier JSON (doit retourner un message de succès si valide).
- `brain tools list --type browser` : Liste les outils de type "browser" (doit afficher au moins un outil si présent, comme Playwright).
- `brain tools list --capability html_parsing` : Liste les outils avec la capacité "html_parsing" (doit afficher des outils comme BeautifulSoup4 si présents).
- `brain tools check-compat playwright scraperapi` : Vérifie la compatibilité entre Playwright et ScraperAPI (doit retourner un statut basé sur `compatibilities`).
- `brain tools remove requests` : Supprime l’outil "requests" (doit retourner un message de succès ou échec si non trouvé).





## Notes pour le LLM

- Focus sur la logique "Lego" : Utilise le champ `compatibilities` pour garantir que seuls des outils compatibles soient combinés dans un pipeline. Chaque adaptateur doit simplifier l’intégration d’un outil en masquant ses spécificités derrière une interface commune.
- Évite les suppositions : Suis strictement le schéma Pydantic et les exemples fournis pour minimiser les erreurs dans la gestion des métadonnées.
- Priorise les tâches marquées `[To_Do_Next]` avant de passer aux tâches `[Backlog]`, pour établir une base fonctionnelle avant d’ajouter des fonctionnalités avancées comme les adaptateurs complets.

## Fonctionnalités à Développer pour le Module tool_registry
> **Statuts** : `[Backlog]`, `[To_Do_Next]`, `[LLM_In_Progress]`, `[LLM_Test]`, `[LLM_Testing]`, `[Human_Review]`, `[Human_Done]`

Ce module constitue la base pour gérer les outils de scraping et d’automatisation web dans "The Brain". Les tâches suivantes sont organisées par domaine de fonctionnalité pour fournir un guide clair au LLM tout en lui laissant une certaine liberté d’implémentation. L’objectif est de construire un système robuste permettant d’empiler les outils comme des "Lego" grâce à des règles de compatibilité bien définies.

### 1. Modèles de Données et Validation
- **1.1 Définition des Modèles Pydantic dans `models.py`** `[Human_Review]`  
  Développer le modèle Pydantic `ToolMetadata` selon le schéma JSON fourni (incluant `name`, `tool_type`, `capabilities`, `compatibilities`, etc.), pour valider les métadonnées des outils. Inclure des validateurs si nécessaire pour garantir l’unicité des noms ou la validité des catégories.
- **1.2 Exceptions Personnalisées dans `exceptions.py`** `[Human_Review]`  
  Créer des classes d’exceptions spécifiques comme `ToolNotFoundError`, `ToolValidationError`, ou `ToolExistsError` pour gérer les erreurs courantes liées aux outils.

### 2. Logique Principale du Registre
- **2.1 Création de la Classe `ToolRegistry` dans `core_tool.py`** `[Human_Review]`  
  Implémenter une classe de base `ToolRegistry` pour gérer le registre des outils, incluant l’initialisation et les stubs pour le chargement/sauvegarde des données dans `tools.json`.
- **2.2 Gestion du Stockage dans `core_tool.py`** `[Human_Review]`  
  Développer les fonctions de chargement et de sauvegarde des outils depuis/vers un fichier `tools.json`, en gérant les cas d’erreur (fichier inexistant, format JSON invalide) et en validant les données avec le modèle Pydantic.
- **2.3 Opérations CRUD dans `core_tool.py`** `[Human_Review]`  
  Implémenter les méthodes pour ajouter (`add_tool`), récupérer (`get_tool`), lister (`list_tools` avec filtres par type ou capacité), et supprimer (`remove_tool`) des outils dans le registre.
- **2.4 Gestion des Compatibilités dans `core_tool.py`** `[Human_Review]`  
  Développer les fonctions `check_compatibility()` et `find_compatible_tools()` pour vérifier et suggérer des combinaisons d’outils basées sur le champ `compatibilities`, essentiel pour la logique "Lego" d’empilement des outils.
- **2.5 Développement d’Adaptateurs dans `core_tool.py`** `[Backlog]`  
  Créer une interface générique ou un squelette pour les adaptateurs d’outils, permettant d’intégrer chaque outil dans un pipeline via une interface standardisée qui masque leurs spécificités.
  **Note:** Cette fonctionnalité sera probablement implémentée à un stade ultérieur du développement, lorsque le module `pipeline_builder` sera prêt à exploiter les adaptateurs.

### 3. Interface Utilisateur
- **3.1 Interface CLI dans `cli.py`** `[Human_Review]`  
  Implémenter les commandes CLI pour gérer les outils (ex. `brain tools add`, `list`, `remove`, `check-compat`), avec un formatage clair des sorties (JSON ou texte) et une gestion des erreurs utilisateur-friendly.

### 4. Validation et Tests
- **4.1 Tests Unitaires dans `tests/`** `[Human_Review]`  
  Écrire des tests pour valider les modèles Pydantic, les opérations CRUD, et la logique de compatibilité, en utilisant des mocks pour éviter des dépendances externes (ex. lecture/écriture de fichier).

### 5. Documentation et Intégration
- **5.1 Documentation des Classes et Méthodes** `[Human_Review]`  
  Ajouter des docstrings détaillés pour chaque classe, méthode ou fonction, pour faciliter la maintenance et l’utilisation par d’autres modules.
- **5.2 Intégration avec le Système Global** `[Human_Review]`  
  Exporter les fonctions principales dans `__init__.py` pour permettre une intégration facile avec le reste de "The Brain", en préparant des hooks si nécessaire pour des modules comme `pipeline_builder`.

## Règles de Compatibilité pour la Logique "Lego"
La logique d’empilement des outils repose sur des principes clairs à implémenter dans les fonctions comme `check_compatibility()` pour éviter des combinaisons invalides dans les pipelines :
- **Compatibilité Explicite :** Un outil peut déclarer explicitement avec quels autres outils ou types d’outils il est compatible via le champ `compatibilities` (ou similaire).
- **Incompatibilité Explicite :** Un outil peut déclarer explicitement des incompatibilités si un champ dédié est utilisé (ex. `incompatible_with`), interdisant certaines combinaisons.
- **Compatibilité Implicite :** Si aucune règle explicite n’est définie, les outils sont considérés compatibles sauf indication contraire.
- **Principe de Réciprocité :** Si un outil A déclare une incompatibilité avec B, B ne peut pas fonctionner avec A, même si B n’indique pas d’incompatibilité.
- **Types et Rôles :** Les outils du même type (ex. deux "browser") sont généralement incompatibles sauf déclaration explicite de compatibilité.

## Development Flow
1. **Finish Module Top-Down :** Compléter chaque fonctionnalité dans l’ordre des statuts, en s’assurant que les tests locaux et CLI passent pour chaque tâche avant de passer à la suivante.
2. **Move Status → [LLM_Test_Complete] :** Une fois qu’une tâche ou un ensemble de tâches est terminé et testé localement, changer son statut à `[LLM_Test_Complete]` et notifier un réviseur humain pour validation.
3. **Keep ≤5 Tasks in [LLM_In_Progress] or [LLM_Testing] :** Limiter à 5 le nombre de tâches simultanément en cours ou en test pour maintenir un flux de travail clair et éviter la surcharge.

