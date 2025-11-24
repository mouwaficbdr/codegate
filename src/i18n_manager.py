class I18nManager:
    TRANSLATIONS = {
        "en": {
            # General / Common
            "app_name": "CodeGate",
            "settings": "Settings",
            "save": "Save",
            "cancel": "Cancel",
            "quit": "Quit CodeGate",
            "about": "About",
            "general": "General",
            "language": "Interface Language",
            "language_hint": "Language will be updated on next restart.",
            
            # Categories
            "cat_browsers": "Browsers",
            "cat_communication": "Communication",
            "cat_games": "Games & Entertainment",
            "cat_dev": "Development",
            "cat_social": "Social Networks",
            
            # Settings Dialog
            "settings_title": "General Settings",
            "blocked_apps": "Blocked Apps",
            "difficulty": "Challenge Difficulty",
            "diff_easy_desc": "• Easy: Basic concepts",
            "diff_medium_desc": "• Medium: Simple algorithms",
            "diff_hard_desc": "• Hard: Complex algorithms",
            "diff_mixed_desc": "• Mixed: Random mix (recommended)",
            "search_placeholder": "🔍 Search for an application...",
            "add_btn": "+ Add",
            "add_tooltip": "Add custom application by process name",
            "legend": "🟢 = Running  |  ✏️ = Custom",
            "custom_apps": "Custom Apps",
            "other_blocked": "Other Blocked",
            "add_custom_title": "Add Application",
            "add_custom_msg": "Process name (e.g., notepad.exe, vlc):",
            "about_subtitle": "Productivity through Code",
            "about_desc": "Version 1.0.0\n\nDeveloped with ❤️ to help you stay focused.\nEvery distraction is an opportunity to learn.",
            
            # Main Overlay
            "solution_label": "Solution:",
            "test_output_label": "Test Output:",
            "run_tests_btn": "Run Sample Tests",
            "attempt_btn": "Attempt",
            "running_tests": "Running tests...",
            "execution_error": "Execution Error:",
            "result_passed": "Result: {passed}/{total} Passed",
            "no_challenges": "No challenges loaded.",
            
            # Tray Icon
            "tray_tooltip": "CodeGate - Productivity & Focus",
            
            # Onboarding
            "welcome_title": "Welcome to CodeGate! 🛡️",
            "welcome_subtitle": "<h2>CodeGate - Productivity through Code</h2>",
            "welcome_intro": "<p>CodeGate is a unique productivity tool that helps you stay focused.</p>",
            "how_it_works": "<p><b>How it works?</b></p>",
            "step_1": "<li>You select the apps that distract you</li>",
            "step_2": "<li>When you try to open them, they are <b>blocked</b></li>",
            "step_3": "<li>You must <b>solve a coding challenge</b> to access them</li>",
            "step_4": "<li>Once solved, you have access until the next attempt</li>",
            "benefits_title": "<p>📚 <b>Benefits:</b></p>",
            "benefit_1": "<li>✅ Improve your coding skills</li>",
            "benefit_2": "<li>✅ Reduce distractions</li>",
            "benefit_3": "<li>✅ Strengthened self-discipline</li>",
            
            "app_selection_title": "App Selection",
            "app_selection_subtitle": "Choose the apps you want to block",
            "app_selection_instr": "Select the applications you find <b>distracting</b> and for which you will have to solve a challenge before accessing them.",
            "app_selection_tip": "💡 <i>Tip: Start with 2-3 apps to test the system.</i>",
            
            "diff_title": "Difficulty Level",
            "diff_subtitle": "Choose your challenge level",
            "diff_expl": "Challenges vary in difficulty. You can change this setting at any time.",
            "diff_easy": "✅ Easy - Simple problems (start)",
            "diff_medium": "🔸 Medium - Intermediate challenges",
            "diff_hard": "🔥 Hard - Advanced algorithms",
            "diff_mixed": "🎲 Mixed - All levels (recommended)",
            
            "final_title": "Configuration Complete! 🎉",
            "final_autostart": "<p><b>⚙️ Auto-start:</b><br>CodeGate will start automatically at every login to monitor your applications.</p>",
            "final_settings": "<p><b>🔧 Settings:</b><br>You can modify your preferences at any time via the ⚙ button in the main interface.</p>",
            "final_msg": "<hr><h3>Ready to boost your productivity? 🚀</h3><p>Click <b>Finish</b> to start!</p>",
            "final_summary_apps": "<b>📱 Blocked apps ({count}):</b>",
            "final_summary_diff": "<b>🎯 Difficulty:</b> {diff}",
            "no_apps": "<i>No application</i>",
            
            "wizard_next": "Next →",
            "wizard_back": "← Back",
            "wizard_finish": "Finish",
            "wizard_cancel": "Cancel",
            "wizard_title": "CodeGate - Initial Configuration",
            
            # Notifications
            "notif_blocked_title": "Application Blocked! 🔒",
            "notif_blocked_msg": "{app_name} has been blocked.\nSolve the challenge to continue.",
            "notif_solved_title": "Challenge Solved! ✅",
            "notif_solved_msg": "Great! {language} challenge solved{time_msg}.\nYou have access to your apps.",
            "notif_time_msg": " in {time_taken}s",
            "notif_failed_title": "Challenge Failed ❌",
            "notif_failed_msg": "Try again to unlock your apps.",
            "notif_startup_title": "CodeGate Active",
            "notif_startup_msg": "App monitoring is enabled.",
            "notif_stats_title": "CodeGate Statistics",
            "notif_stats_blocks_today": "📊 Blocks today: {count}",
            "notif_stats_total_blocks": "🔒 Total blocks: {count}",
            "notif_stats_solved": "✅ Challenges solved: {count}",
            "notif_stats_failed": "❌ Challenges failed: {count}",
            "notif_stats_rate": "📈 Success rate: {rate:.1f}%"
        },
        "fr": {
            # General / Common
            "app_name": "CodeGate",
            "settings": "Paramètres",
            "save": "Enregistrer",
            "cancel": "Annuler",
            "quit": "Quitter CodeGate",
            "about": "À propos",
            "general": "Général",
            "language": "Langue de l'interface",
            "language_hint": "La langue sera mise à jour au prochain démarrage de l'interface.",
            
            # Categories
            "cat_browsers": "Navigateurs",
            "cat_communication": "Communication",
            "cat_games": "Jeux & Divertissement",
            "cat_dev": "Développement",
            "cat_social": "Réseaux Sociaux",
            
            # Settings Dialog
            "settings_title": "Paramètres Généraux",
            "blocked_apps": "Applications Bloquées",
            "difficulty": "Difficulté des Challenges",
            "diff_easy_desc": "• Easy: Concepts de base",
            "diff_medium_desc": "• Medium: Algorithmes simples",
            "diff_hard_desc": "• Hard: Algorithmes complexes",
            "diff_mixed_desc": "• Mixed: Mélange aléatoire (recommandé)",
            "search_placeholder": "🔍 Rechercher une application...",
            "add_btn": "+ Ajouter",
            "add_tooltip": "Ajouter une application personnalisée par nom de processus",
            "legend": "🟢 = En cours d'exécution  |  ✏️ = Personnalisé",
            "custom_apps": "Applications Personnalisées",
            "other_blocked": "Autres Bloquées",
            "add_custom_title": "Ajouter une application",
            "add_custom_msg": "Nom du processus (ex: notepad.exe, vlc):",
            "about_subtitle": "Productivité par le Code",
            "about_desc": "Version 1.0.0\n\nDéveloppé avec ❤️ pour vous aider à rester concentré.\nChaque distraction est une opportunité d'apprendre.",
            
            # Main Overlay
            "solution_label": "Solution :",
            "test_output_label": "Sortie des tests :",
            "run_tests_btn": "Lancer les tests",
            "attempt_btn": "Soumettre",
            "running_tests": "Exécution des tests...",
            "execution_error": "Erreur d'exécution :",
            "result_passed": "Résultat : {passed}/{total} Réussis",
            "no_challenges": "Aucun challenge chargé.",
            
            # Tray Icon
            "tray_tooltip": "CodeGate - Productivité & Focus",
            
            # Onboarding
            "welcome_title": "Bienvenue dans CodeGate! 🛡️",
            "welcome_subtitle": "<h2>CodeGate - Productivité par le Code</h2>",
            "welcome_intro": "<p>CodeGate est un outil de productivité unique qui vous aide à rester concentré.</p>",
            "how_it_works": "<p><b>Comment ça marche?</b></p>",
            "step_1": "<li>Vous sélectionnez les applications qui vous distraient</li>",
            "step_2": "<li>Quand vous essayez de les ouvrir, elles sont <b>bloquées</b></li>",
            "step_3": "<li>Vous devez <b>résoudre un challenge de code</b> pour y accéder</li>",
            "step_4": "<li>Une fois résolu, vous avez accès jusqu'à la prochaine tentative</li>",
            "benefits_title": "<p>📚 <b>Bénéfices:</b></p>",
            "benefit_1": "<li>✅ Amélioration de vos compétences en programmation</li>",
            "benefit_2": "<li>✅ Réduction des distractions</li>",
            "benefit_3": "<li>✅ Discipline personnelle renforcée</li>",
            
            "app_selection_title": "Sélection des Applications",
            "app_selection_subtitle": "Choisissez les applications que vous voulez bloquer",
            "app_selection_instr": "Sélectionnez les applications que vous trouvez <b>distrayantes</b> et pour lesquelles vous devrez résoudre un challenge avant d'y accéder.",
            "app_selection_tip": "💡 <i>Conseil: Commencez avec 2-3 applications pour tester le système.</i>",
            
            "diff_title": "Niveau de Difficulté",
            "diff_subtitle": "Choisissez le niveau de vos challenges",
            "diff_expl": "Les challenges varient en difficulté. Vous pouvez changer ce paramètre à tout moment.",
            "diff_easy": "✅ Facile - Problèmes simples (début)",
            "diff_medium": "🔸 Moyen - Challenges intermédiaires",
            "diff_hard": "🔥 Difficile - Algorithmes avancés",
            "diff_mixed": "🎲 Mixte - Tous les niveaux (recommandé)",
            
            "final_title": "Configuration Terminée! 🎉",
            "final_autostart": "<p><b>⚙️ Démarrage automatique:</b><br>CodeGate démarrera automatiquement à chaque connexion pour surveiller vos applications.</p>",
            "final_settings": "<p><b>🔧 Paramètres:</b><br>Vous pouvez modifier vos préférences à tout moment via le bouton ⚙ dans l'interface principale.</p>",
            "final_msg": "<hr><h3>Prêt à booster votre productivité? 🚀</h3><p>Cliquez sur <b>Terminer</b> pour commencer!</p>",
            "final_summary_apps": "<b>📱 Applications bloquées ({count}):</b>",
            "final_summary_diff": "<b>🎯 Difficulté:</b> {diff}",
            "no_apps": "<i>Aucune application</i>",
            
            "wizard_next": "Suivant →",
            "wizard_back": "← Retour",
            "wizard_finish": "Terminer",
            "wizard_cancel": "Annuler",
            "wizard_title": "CodeGate - Configuration Initiale",
            
            # Notifications
            "notif_blocked_title": "Application bloquée! 🔒",
            "notif_blocked_msg": "{app_name} a été bloquée.\nRésolvez le challenge pour continuer.",
            "notif_solved_title": "Challenge résolu! ✅",
            "notif_solved_msg": "Bravo! Challenge {language} résolu{time_msg}.\nVous avez accès à vos applications.",
            "notif_time_msg": " en {time_taken}s",
            "notif_failed_title": "Challenge échoué ❌",
            "notif_failed_msg": "Réessayez pour débloquer vos applications.",
            "notif_startup_title": "CodeGate actif",
            "notif_startup_msg": "La surveillance des applications est activée.",
            "notif_stats_title": "Statistiques CodeGate",
            "notif_stats_blocks_today": "📊 Blocages aujourd'hui: {count}",
            "notif_stats_total_blocks": "🔒 Total blocages: {count}",
            "notif_stats_solved": "✅ Challenges résolus: {count}",
            "notif_stats_failed": "❌ Challenges échoués: {count}",
            "notif_stats_rate": "📈 Taux de réussite: {rate:.1f}%"
        }
    }

    def __init__(self, lang="en"):
        self.lang = lang

    def set_language(self, lang):
        if lang in self.TRANSLATIONS:
            self.lang = lang

    def get(self, key, **kwargs):
        text = self.TRANSLATIONS.get(self.lang, {}).get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text
