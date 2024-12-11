import os
import shutil
from django.conf import settings

ROOT_HOME_FOLDER = settings.HOME_FOLDER_ROOT #'./home'
DEFAULT_HOME_FOLDER_NAME = 'default'

INITIAL_ROOT_HOME_FOLDER = os.path.join(settings.BASE_DIR, 'home_init') #'./home_init'
INITIAL_HOME_FOLDER_NAME = 'default'


class HomeFolder:
    root_folder = ROOT_HOME_FOLDER
    home_folder = DEFAULT_HOME_FOLDER_NAME

    public_offer_file_name = "Public_offer.pdf"
    privacy_policy_file_name = "Privacy_policy.pdf"

    def __init__(self, home_folder=DEFAULT_HOME_FOLDER_NAME, root_folder=ROOT_HOME_FOLDER):
        self.home_folder = home_folder
        self.root_folder = root_folder

    # Папка в которой хранится начальная конфигурация домашней директории
    @classmethod
    def initial_folder(cls):
        return HomeFolder(root_folder=INITIAL_ROOT_HOME_FOLDER, home_folder=INITIAL_HOME_FOLDER_NAME)

    # Папка в которой хранится конфигурация по умолчанию директории
    # !LazyInitialization если папки не существует она создаётся
    @classmethod
    def default_folder(cls):
        hf = HomeFolder(root_folder=ROOT_HOME_FOLDER, home_folder=DEFAULT_HOME_FOLDER_NAME)
        if not hf.exists:
            hf.make_from_folder(HomeFolder.initial_folder())

        return hf

    @classmethod
    def for_agency(cls, agency, default_folder=None):
        if not default_folder:
            default_folder = HomeFolder.default_folder()
        if not agency:
            return default_folder

        from main.models.agency.agency import Agency
        hf = HomeFolder(home_folder=Agency.get_valid_filename(agency, True), root_folder=default_folder.root_folder)
        hf.make_from_folder(HomeFolder.initial_folder())
        return hf

    @property
    def path(self):
        return os.path.join(self.root_folder, self.home_folder)

    @property
    def exists(self):
        return os.path.exists(self.path)

    @property
    def path_media(self):
        return os.path.join(self.path, 'media')

    @property
    def path_templates(self):
        return os.path.join(self.path, 'templates')

    @property
    def path_reports(self):
        return os.path.join(self.path, 'templates/reports')

    @property
    def path_mails(self):
        return os.path.join(self.path, 'templates/mails')

    @property
    def path_contracts(self):
        return os.path.join(self.path, 'templates/contracts')

    @property
    def file_path_logo(self):
        return os.path.join(self.path_media, 'logo.png')

    @property
    def file_path_favicon(self):
        return os.path.join(self.path_media, 'favicon.png')

    @property
    def file_path_report_logo(self):
        return os.path.join(self.path_media, 'report-logo.png')

    @property
    def file_path_supplier_cabinet_logo(self):
        return os.path.join(self.path_media, 'supplier-cabinet-logo.png')

    @property
    def file_path_supplier_cabinet_navbar_theme_light(self):
        return os.path.join(self.path_media, 'supplier-cabinet-navbar-theme-light')

    def make_new_folder(self):
        os.makedirs(self.path_media)
        os.makedirs(self.path_contracts)
        os.makedirs(self.path_reports)

    def make_from_folder(self, source_home_folder):
        if not os.path.exists(self.path):
            shutil.copytree(source_home_folder.path, self.path)

    def make_from_default(self):
        self.make_from_folder(HomeFolder())
