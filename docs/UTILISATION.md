# Zapp Télé — LibreELEC / Kodi

Extension personnelle version 1.3.0, Python 3, testée sur LibreELEC 12.2.1 (Raspberry Pi 5), Kodi 21 et IPTV Simple Client 21.11.

## Utilisation

Dans Kodi : **Extensions → Extensions vidéo → Zapp Télé**.

1. **Paramètres de connexion** : hôte (par défaut `http://zap444.com:8080`), nom d’utilisateur et mot de passe. Sur votre appareil, le compte déjà configuré dans IPTV Simple Client a été repris.
2. **Télécharger les chaînes et le guide** : à utiliser après toute modification du compte ou du serveur.
3. **Afficher ou masquer les groupes** : les groupes cochés sont visibles. Utilisez **Cocher tout** ou **Décocher tout**, ajustez les groupes individuellement, puis **Valider**. Un compteur indique le nombre de groupes cochés. Annuler conserve le choix précédent. Les nouveaux groupes sont visibles par défaut.
4. **Configurer la Télévision Kodi et le guide** : relie la liste filtrée et le guide XMLTV à IPTV Simple Client. Déjà effectué sur votre appareil.
5. Retrouvez les chaînes dans **Télévision → Chaînes / Guide** ou dans **Parcourir les chaînes** de l’extension.

Le cache persiste après redémarrage. L’ouverture de l’extension et la sélection des groupes utilisent les fichiers locaux. Les chaînes sont synchronisées toutes les 6 heures et le guide XMLTV toutes les 24 heures, en arrière-plan lorsque Kodi fonctionne. La commande de téléchargement permet de forcer la synchronisation en arrière-plan. Un guide identique ne sera ni réanalysé ni réécrit. Les données modifiées sont chargées par le client TV lorsque la lecture est arrêtée. Une panne conserve les fichiers valides et déclenche un nouvel essai ultérieur. Le serveur reste configuré avec les URL get.php et xmltv.php demandées.

Le mot de passe est masqué à l’écran. Comme les paramètres Kodi et les liens IPTV habituels, les fichiers locaux peuvent contenir les identifiants en clair. L’hôte HTTP par défaut transmet aussi les identifiants sans chiffrement ; HTTPS peut être renseigné si votre fournisseur le prend en charge. L’archive livrée ne contient aucun identifiant.

## Installation sur un autre appareil

Installer **IPTV Simple Client** depuis le dépôt LibreELEC. Copier le ZIP sur l’appareil, puis **Extensions → Installer depuis un fichier ZIP** (autoriser les sources inconnues si Kodi le demande). Configurer le compte et suivre les étapes ci-dessus.

## Fichiers et restauration

- Extension : `/storage/.kodi/addons/plugin.video.zapptele/`.
- Données : `/storage/.kodi/userdata/addon_data/plugin.video.zapptele/`.
- `source.m3u` : liste complète ; `channels.m3u` : liste filtrée ; `guide.xml` : guide ; `hidden.json` : groupes masqués.
- Avant modification, l’instance IPTV Simple Client existante est sauvegardée dans `pvr-original.xml` dans le dossier de données. Pour restaurer cette configuration, arrêter Kodi puis recopier cette sauvegarde vers l’instance indiquée par `instance.json`, dans `/storage/.kodi/userdata/addon_data/pvr.iptvsimple/`, et relancer Kodi.

Chaque ressource est validée indépendamment avant remplacement : une erreur du guide ne bloque pas la mise à jour des chaînes, et inversement. Les erreurs réseau ne sont pas journalisées avec leurs URL pour éviter d’exposer les identifiants.

## Vérifications effectuées

Tests du filtrage M3U, conservation des directives de lecture, caractères accentués et encodage des identifiants. Compilation Python sur LibreELEC. Téléchargement réel de la liste et du guide XMLTV et configuration du client PVR. La lecture audiovisuelle de chaque chaîne n’a pas été vérifiée.

## Présélection Locale

Le menu « Présélection Locale — choisir la ville » regroupe les stations correspondantes dans un groupe **Locale**, visible dans l’extension et dans la section Télévision. Il déplace ces stations depuis leurs groupes d’origine, sans changer les flux ni les identifiants du guide. Les autres groupes conservent leur visibilité. La désactivation restaure les groupes du fournisseur.

Granby : 12 entrées identifiées dans la liste fournie (réseaux généralistes, Estrie, Sherbrooke et Montréal). La liste ne comporte pas de station explicitement nommée Granby ; cette présélection est fondée sur les libellés du fournisseur, sans garantie de couverture géographique. Les nouveaux téléchargements conservent cette présélection.

## Présélection Sports #tata

Groupe de 17 chaînes dans la liste vérifiée : RDS, RDS 2, TVA Sports, TVA Sports 2, TSN 1 à 5, NHL Montréal Canadiens, Sportsnet 360, East, Pacific, One, Ontario, West et World. Les chaînes sont regroupées depuis leurs catégories d’origine et restent associées aux mêmes flux et identifiants du guide. Le groupe peut être masqué dans la sélection des groupes. La présélection est reconstruite à chaque téléchargement ; le groupe Locale reste disponible.

## Ordre prioritaire et chaînes spécialisées

Les groupes apparaissent dans cet ordre : **Locale**, **Sports #tata**, **Québec — Chaînes spécialisées**, puis les autres groupes par ordre alphabétique. Cet ordre s’applique à la sélection, à la navigation et au fichier M3U filtré. Kodi doit conserver l’option d’ordre des groupes fourni par le serveur activée ; elle a été activée sur votre appareil.

Le groupe Québec regroupe 41 chaînes spécialisées de la liste vérifiée, notamment Canal D, ARTV, Historia, Séries Plus, Z, Zeste, CASA, Évasion, ICI Explora, RDI, LCN, MétéoMédia, Cinépop et Super Écran 1 à 4. Les films, séries à la demande et boucles 24/7 ne sont pas inclus. Comme les autres présélections, les chaînes sont déplacées depuis leurs catégories d’origine, avec les mêmes flux et identifiants de guide.
