# -*- coding: utf-8 -*-
import os
import json
from google.oauth2.service_account import Credentials
from google.cloud import asset_v1p5beta1
from googleapiclient import discovery
from matos_gcp_provider.lib.log import get_logger

logger = get_logger()


class Connection:
    """
    Collection base auth class
    """

    _credentials = None
    _project_id = None
    _account_info = None
    _cred_mode = 'file'

    def __init__(self,
                 **kwargs) -> None:
        """
        Constructor method
        """
        self.SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
        svc_account_filename = "google_service_account.json"
        gcp_svc_account_path = os.getenv("GCP_SVC_ACCOUNT_PATH", "credentials")
        self._gcp_svc_account_file = os.path.join(gcp_svc_account_path, svc_account_filename)
        try:
            with open(self._gcp_svc_account_file, encoding="utf-8") as file:
                self._account_info = json.load(file)
            self._project_id = self._account_info.get('project_id', '')
        except Exception as ex:
            GCP_ACCOUNT_FILE_EXCEPTION = "Not found account service json for GCP " \
                                         "- credentials/google_service_account.json"
            logger.error(ex)
            raise Exception(GCP_ACCOUNT_FILE_EXCEPTION) from ex

    @property
    def client(self):
        """
        Client property
        """
        return asset_v1p5beta1.AssetServiceClient(credentials=self.credentials)

    @property
    def credentials(self):
        """
        Get credentials property
        """

        if self._credentials is not None:
            return self._credentials

        try:
            self._credentials = Credentials.from_service_account_info(
                self._account_info, scopes=self.SCOPES
            )
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex) from ex

        return self._credentials

    @property
    def projectId(self):
        """
        Project id property
        """
        if not self._project_id:
            raise Exception("No project ID found.")
        return self._project_id

    def _get_projects(self):
        """
        Get project id method
        """

        service = discovery.build('cloudresourcemanager', 'v1',
                                  credentials=self.credentials)
        request = service.projects().list()  # pylint: disable=E1101
        response = request.execute()

        return [x['projectId'] for x in response['projects']]
