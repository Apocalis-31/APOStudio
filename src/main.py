from ui.app import ApoStudio
from services.config_service import ConfigService


def main():

    config = ConfigService()



    config.set("ai.provider", "claude")

    app = ApoStudio()
    app.mainloop()


if __name__ == "__main__":
    main()
