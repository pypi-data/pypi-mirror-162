import posixpath
from io import BytesIO
import logging


log = logging.getLogger(__name__)


class Sharepoint:
    def __init__(self, conf, site_name):
        self.tenant_name = conf.tenant_name
        self.tenant_id = conf.tenant_id
        self.client_id = conf.client_id
        self.key = conf.key
        self.thumbprint = conf.thumbprint
        self.site_name = site_name
        self.session = None

    def connect(self):
        import adal
        from office365.runtime.auth.token_response import TokenResponse
        from office365.sharepoint.client_context import ClientContext
        if self.session:
            return self.session
        sharepoint_base_url = f'https://{self.tenant_name}.sharepoint.com'
        site_url = f'{sharepoint_base_url}/sites/{self.site_name}'
        authority = f'https://login.microsoftonline.com/{self.tenant_id}'
        app = adal.AuthenticationContext(authority)
        token_json = app.acquire_token_with_client_certificate(
            sharepoint_base_url,
            self.client_id,
            self.key,
            self.thumbprint,
        )
        self.session = ClientContext(site_url).with_access_token(
            lambda: TokenResponse.from_json(token_json)
        )
        return self.session

    def ensure(self, d):
        """
        ensures that d exists
        """
        from office365.sharepoint.folders.folder import Folder
        session = self.connect()
        pieces = d.split(posixpath.sep)[3:]
        s: Folder = session.web.root_folder
        s = s.expand(['Folders'])
        for x in pieces:
            found = False
            s = s.get().execute_query()
            for y in s.folders:
                if y.name == x:
                    found = True
                    s = y
                    break
            if not found:
                log.info('creating folder %s in %s', x, s.serverRelativeUrl)
                s = s.folders.ensure_folder_path(x).execute_query()
        return s

    def upload(self, buff, destination):
        """
        uploads a BytesIO to the destination path
        """
        from office365.sharepoint.folders.folder import Folder
        destination = destination.replace('Documents', 'Shared Documents')
        d = posixpath.dirname(destination)
        base = posixpath.basename(destination)
        destination = posixpath.join('/sites', self.site_name, d)
        folder: Folder = self.ensure(destination)
        buff.seek(0)
        log.info(f'uploading %s => %s', base, destination)
        folder.upload_file(base, buff.getvalue()).execute_query()

    def download(self, filename):
        """
        Downloads the specified path into a BytesIO buffer
        """
        source = filename.replace('Documents', 'Shared Documents')
        source = posixpath.join('/sites', self.site_name, source)
        session = self.connect()
        f = session.web.get_file_by_server_relative_path(source)
        log.info('downloading %s from %s', filename, self.site_name)
        buff = BytesIO()
        f.download(buff).execute_query()
        buff.seek(0)
        return buff

    def upload_dataframes(self, filename, *args):
        """
        provide arguments as filename, df1, sheet_name1, df2, sheet_name2, ...
        """
        import pandas as pd
        n = len(args)
        buff = BytesIO()
        with pd.ExcelWriter(buff) as f:
            for x in range(0, n, 2):
                df = args[x]
                sheet_name = args[x + 1]
                df.to_excel(f, sheet_name=sheet_name)
        self.upload(buff, filename)

    def download_dataframe(self, filename, engine='openpyxl', **kwargs):
        """
        downloads the file from sharepoint and provides it to the caller
        as a dataframe
        """
        import pandas as pd
        buff = self.download(filename)
        df = pd.read_excel(io=buff)
        return df
