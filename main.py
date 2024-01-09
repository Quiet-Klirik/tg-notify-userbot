from core.handlers import prepare_handlers
from core.utils import ProjectManager


def main():
    project = ProjectManager()
    prepare_handlers(project)
    project.run()


if __name__ == '__main__':
    main()
