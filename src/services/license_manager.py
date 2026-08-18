from datetime import datetime
import hashlib


class LicenseManager:
    """
    Gestionnaire des licences APO Studio.

    V1 :
    - Community par défaut
    - codes Beta locaux
    - persistance via ConfigService
    - architecture prévue pour Premium
    """

    COMMUNITY = "community"
    BETA = "beta"
    PREMIUM = "premium"

    FEATURES = {
        "assisted_editing",
        "thumbnail_generation",
        "assisted_planning",
    }

    # ==================================================
    # Codes Beta
    # ==================================================

    # Pour la V1, les codes sont locaux.
    #
    # IMPORTANT :
    # Ce système est volontairement adapté à la bêta.
    # Pour le futur système payant, la validation devra
    # être faite côté serveur.

    BETA_CODES = {
        "APOSTUDIO-BETA-7F42-A91C",
        "APOSTUDIO-BETA-C83D-21F7",
        "APOSTUDIO-BETA-94AE-6D31",
    }

    # ==================================================

    def __init__(self, config):
        self.config = config

        self.level = self.COMMUNITY
        self.code = None
        self.activated_at = None

        self._load()

    # ==================================================
    # Chargement
    # ==================================================

    def _load(self):

        if self.config is None:
            return

        try:

            license_data = (
                self.config.get(
                    "license",
                    {},
                )
                or {}
            )

            self.level = license_data.get(
                "level",
                self.COMMUNITY,
            )

            self.code = license_data.get(
                "code",
            )

            self.activated_at = license_data.get(
                "activated_at",
            )

            if self.level not in (
                self.COMMUNITY,
                self.BETA,
                self.PREMIUM,
            ):
                self.level = self.COMMUNITY

        except Exception:

            self.level = self.COMMUNITY
            self.code = None
            self.activated_at = None

    # ==================================================
    # Sauvegarde
    # ==================================================

    def _save(self):

        if self.config is None:
            return

        self.config.set(
            "license.level",
            self.level,
        )

        self.config.set(
            "license.code",
            self.code or "",
        )

        self.config.set(
            "license.activated_at",
            self.activated_at or "",
        )

        self.config.save()

    # ==================================================
    # Activation
    # ==================================================

    def activate_code(self, code: str) -> bool:

        if not code:
            return False

        normalized = (
            code
            .strip()
            .upper()
        )

        if normalized not in self.BETA_CODES:
            return False

        self.level = self.BETA
        self.code = normalized
        self.activated_at = (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )

        self._save()

        return True

    # ==================================================
    # Désactivation
    # ==================================================

    def deactivate(self):

        self.level = self.COMMUNITY
        self.code = None
        self.activated_at = None

        self._save()

    # ==================================================
    # Accès
    # ==================================================

    def has_access(
        self,
        feature: str,
    ) -> bool:

        # Fonctionnalités non protégées
        if feature not in self.FEATURES:
            return True

        return self.level in (
            self.BETA,
            self.PREMIUM,
        )

    # ==================================================
    # Informations
    # ==================================================

    def is_beta(self) -> bool:

        return self.level == self.BETA

    def is_premium(self) -> bool:

        return self.level == self.PREMIUM

    def is_community(self) -> bool:

        return self.level == self.COMMUNITY

    def license_name(self) -> str:

        if self.level == self.BETA:
            return "Beta Tester"

        if self.level == self.PREMIUM:
            return "APO Studio Premium"

        return "Community"