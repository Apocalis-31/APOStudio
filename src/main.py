from ui.app import ApoStudio
from services.config_service import ConfigService
from services.update_service import UpdateService


def main():

    config = ConfigService()

    info = UpdateService.check()

    print(info)

    config.set("ai.provider", "claude")

    app = ApoStudio()
    app.mainloop()


if __name__ == "__main__":
    main()
