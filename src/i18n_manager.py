class I18nManager:
    TRANSLATIONS = {
        "en": {
            "title_locked": "CodeGate: Locked",
            "desc_locked": "Solve this challenge to unlock your apps.",
            "submit": "Submit Solution",
            "success": "Success",
            "success_msg": "Correct! Unlocking apps...",
            "failed": "Failed",
            "failed_msg": "Incorrect solution. Try again.",
            "settings": "Settings",
            "language": "Language",
            "difficulty": "Difficulty Distribution",
            "save": "Save",
            "cancel": "Cancel"
        },
        "fr": {
            "title_locked": "CodeGate : Verrouillé",
            "desc_locked": "Résolvez ce défi pour débloquer vos applications.",
            "submit": "Soumettre la solution",
            "success": "Succès",
            "success_msg": "Correct ! Déblocage des applications...",
            "failed": "Échec",
            "failed_msg": "Solution incorrecte. Réessayez.",
            "settings": "Paramètres",
            "language": "Langue",
            "difficulty": "Distribution de Difficulté",
            "save": "Enregistrer",
            "cancel": "Annuler"
        }
    }

    def __init__(self, lang="en"):
        self.lang = lang

    def set_language(self, lang):
        if lang in self.TRANSLATIONS:
            self.lang = lang

    def get(self, key):
        return self.TRANSLATIONS.get(self.lang, {}).get(key, key)
