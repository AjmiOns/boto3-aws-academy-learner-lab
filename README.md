# Boto3 & AWS Academy Learner Lab

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Boto3](https://img.shields.io/badge/boto3-AWS%20SDK-orange)
![AWS](https://img.shields.io/badge/AWS-Learner%20Lab-232F3E)
![Status](https://img.shields.io/badge/status-in%20progress-yellow)

Progressive hands-on labs to automate AWS with **Python and Boto3**, run inside the **AWS Academy Learner Lab** (temporary credentials, restricted IAM, `us-east-1`).

## Objectif

Aller de zéro à des outils d'automatisation cloud fiables :

- configurer un environnement AWS reproductible avec des credentials temporaires ;
- maîtriser les deux interfaces de Boto3 (**client** vs **resource**) ;
- appliquer les patterns qu'on retrouve en production : **paginators**, **waiters**, **gestion d'erreurs par `Error.Code`**, **logging**, nettoyage systématique des ressources.

## Contenu

| Lab | Dossier | Services | Livrable | Pattern clé |
|-----|---------|----------|----------|-------------|
| 0 | [`lab0-aws-environment-setup`](./lab0-aws-environment-setup) | STS | Environnement fonctionnel + test de connexion | Credentials temporaires |
| 1 | [`lab1-aws-boto3-fundamentals`](./lab1-aws-boto3-fundamentals) | STS, S3, EC2 | `aws_resource_explorer.py` | Clients vs Resources |
| 2 | [`lab2-aws-boto3-s3-file-management`](./lab2-aws-boto3-s3-file-management) | S3 | `s3_manager.py` | Paginators |

### Lab 1 — AWS Resource Explorer
Script qui affiche l'identité (STS), la région résolue, les buckets S3 (via client **et** resource), les instances EC2 (réponse imbriquée `Reservations > Instances`) et les régions disponibles. Il échoue proprement sur `NoCredentialsError` et `ClientError`.

### Lab 2 — S3 File Manager
Outil CLI interactif : création/suppression de buckets, upload/download, listing paginé, URLs présignées, et sauvegarde récursive d'un dossier local en préservant l'arborescence sous forme de préfixes de clés.

## Prérequis

- Python **3.9+**
- Un accès à l'**AWS Academy Learner Lab**
- Git

## Installation

```bash
git clone https://github.com/<votre-utilisateur>/boto3-aws-academy-learner-lab.git
cd boto3-aws-academy-learner-lab

python -m venv venv
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

## Configuration des credentials (à refaire à chaque session)

Les credentials du Learner Lab **changent à chaque `Start Lab`** et expirent après **4 h**.

1. Learner Lab → **Start Lab**, attendre le voyant vert.
2. **AWS Details → Show** (AWS CLI) et copier les **3 lignes**.
3. Les coller dans `~/.aws/credentials` (Windows : `C:\Users\<vous>\.aws\credentials`, sans extension) :

```ini
[default]
aws_access_key_id     = ASIA...
aws_secret_access_key = ...
aws_session_token     = ...
```

4. `~/.aws/config` :

```ini
[default]
region = us-east-1
output = json
```

5. Vérifier :

```python
import boto3
print(boto3.client("sts").get_caller_identity())
```

> **Sécurité** : ne jamais committer de credentials. Ils restent dans `~/.aws/`, hors du dépôt, et `.gitignore` bloque les fichiers sensibles.

## Utilisation

```bash
# Lab 1
python lab1-aws-boto3-fundamentals/aws_resource_explorer.py

# Lab 2
python lab2-aws-boto3-s3-file-management/s3_manager.py
```

## Contraintes du Learner Lab

| Sujet | Limite |
|-------|--------|
| Régions | `us-east-1`, `us-west-2` uniquement |
| EC2 | `t3.micro` recommandé (nano à large autorisés) |
| IAM | Création d'utilisateurs/rôles interdite → utiliser `LabRole` |
| Session | 4 h, puis arrêt de tout |
| Buckets S3 | Noms globaux uniques → préfixer avec un identifiant personnel |

## Dépannage rapide

| Erreur | Cause | Solution |
|--------|-------|----------|
| `ExpiredToken` | Session expirée | Start Lab, recopier les 3 lignes |
| `NoCredentialsError` | Credentials introuvables | Vérifier le chemin de `~/.aws/credentials` |
| `NoRegionError` | Région absente | Ajouter `region = us-east-1` dans `~/.aws/config` |
| `BucketAlreadyExists` | Nom pris par un autre compte | Ajouter un préfixe personnel |
| `KeyError: 'Tags'` / `'Contents'` | Champ optionnel absent | Utiliser `.get(..., [])` |

## Bonnes pratiques appliquées

- Branchement sur `e.response["Error"]["Code"]`, jamais sur le message.
- Paginators pour ne jamais tronquer les résultats (limite de 1000 objets S3).
- Champs optionnels lus avec `.get()`.
- Validation locale avant tout appel AWS.
- Confirmation explicite pour les actions destructrices.
- **Nettoyage en fin de session** : instances EC2 *terminées* (pas seulement arrêtées), buckets vidés puis supprimés.

## Structure du dépôt

```
boto3-aws-academy-learner-lab/
├── lab0-aws-environment-setup/
├── lab1-aws-boto3-fundamentals/
├── lab2-aws-boto3-s3-file-management/
├── requirements.txt
├── .gitignore
└── README.md
```

## Feuille de route

- [x] Lab 0 — Environnement
- [x] Lab 1 — Fondamentaux Boto3
- [x] Lab 2 — Gestion S3
- [ ] Labs suivants (EC2, DynamoDB, Lambda)

## Auteur

**Ons** — étudiante ingénieur, TEK-UP University (Tunisie)
[GitHub](https://github.com/<votre-utilisateur>) · [LinkedIn](https://www.linkedin.com/in/<votre-profil>)

## Licence

Projet à but pédagogique — licence [MIT](./LICENSE).
