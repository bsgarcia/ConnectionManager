def main():
    from utils.config_management import ConfigFilesManager

    ConfigFilesManager.run()

    from connection_manager import model

    m = model.Model()
    m.run()


if __name__ == "__main__":
    main()
