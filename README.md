# Kodi Zapp Télé

Extension personnelle Kodi 21 / LibreELEC 12.2.1, version 1.3.0.

- Connexion par hôte, nom d’utilisateur et mot de passe.
- Chaînes M3U et guide XMLTV intégrés à IPTV Simple Client.
- Cache persistant ; synchronisation en arrière-plan (chaînes 6 h, guide 24 h).
- Sélection des groupes avec **Cocher tout**, **Décocher tout**, **Valider** et **Annuler**.
- Groupes prioritaires : **Locale**, **Sports #tata**, **Québec — Chaînes spécialisées**.
- Présélections locales par ville, dont Granby.

Aucun abonnement, identifiant personnel, flux ou guide télé n’est inclus. Un compte auprès du fournisseur et **IPTV Simple Client** sont nécessaires. Le serveur par défaut utilise HTTP ; HTTPS peut être configuré si le fournisseur le prend en charge.

## Installation

Avec Python 3, depuis le dossier du dépôt :

```sh
python3 scripts/build.py
```

Dans Kodi, installer le ZIP produit dans `dist/` via **Extensions → Installer depuis un fichier ZIP**, puis ouvrir **Zapp Télé** pour configurer le compte.

Voir le [guide d’utilisation](docs/UTILISATION.md) pour les groupes, la configuration TV et la restauration.

## Développement

Le code de l’extension se trouve dans `plugin.video.zapptele/`. Il utilise la bibliothèque standard Python et les API Python fournies par Kodi, sans dépendance Python externe.

Tests hors Kodi, sans compte et sans connexion réseau :

```sh
python3 tests/test_core.py
python3 tests/test_cache.py
```

La lecture et les fenêtres de l’extension nécessitent Kodi. La version initiale a été vérifiée sur un Raspberry Pi 5 avec LibreELEC 12.2.1 et IPTV Simple Client 21.11.

Licence : [MIT](LICENSE).
