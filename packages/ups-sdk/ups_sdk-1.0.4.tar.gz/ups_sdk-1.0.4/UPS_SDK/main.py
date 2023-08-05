from dataclasses import dataclass
import xml.etree.ElementTree as ET
import requests, urllib3, xmltodict, json
from UPS_SDK.models.TrackError import TrackError
from UPS_SDK.models.TrackResponse import TrackResponse
urllib3.disable_warnings()

@dataclass
class TrackType:
    ByReferenceNumber = "ReferenceNumber"
    ByTrackingNumber = "TrackingNumber"
    
class UPSApi:
    def __init__(self, access_license_number: str, user_id: str, password: str):
        """
        Create A Ups SDK

        Args:
            access_license_number (str): API Access License Number
            user_id (str): API User ID
            password (str): API Password
        """
        
        self.access_license_number = access_license_number
        self.user_id = user_id
        self.password = password
        self.host = 'https://onlinetools.ups.com/ups.app/xml/Track'

    def create_xml_request(self, value: str, type: TrackType):
        """
        Find Package With ReferenceNumber or TrackingNumber And Returned TrackResponse Object Or Raise TrackError Object

        Args:
            value (str): Reference Number Or Tracking Number
            type (TrackType): Track Type for find, TrackType.ByReferenceNumber or TrackType.ByTrackingNumber

        Raises:
            TrackError: If Tracking Information Not Found Raise Track Error

        Returns:
            TrackResponse: TrackResponse Object
        """

        AccessRequest = ET.Element('AccessRequest')
        ET.SubElement(AccessRequest,'AccessLicenseNumber').text = self.access_license_number
        ET.SubElement(AccessRequest,'UserId').text = self.user_id
        ET.SubElement(AccessRequest,'Password').text = self.password


        TrackToolsRequest = ET.Element('TrackRequest')
        Request = ET.SubElement(TrackToolsRequest,'Request')
        TransactionReference = ET.SubElement(Request,'TransactionReference')
        TrackEL = ET.SubElement(TrackToolsRequest, type)
        
        ET.SubElement(TransactionReference,'CustomerContext').text = 'Customer context'
        ET.SubElement(TransactionReference,'XpciVersion').text = '1.0'
        ET.SubElement(Request,'RequestAction').text = 'Track'
        ET.SubElement(Request,'RequestOption').text = 'activity'
        ET.SubElement(TrackEL, "Value").text = value
        
        _reqString = ET.tostring(AccessRequest)

        tree = ET.ElementTree(ET.fromstring(_reqString))
        root = tree.getroot()

        _QuantunmRequest = ET.tostring(TrackToolsRequest)
        quantunmTree = ET.ElementTree(ET.fromstring(_QuantunmRequest))
        quantRoot = quantunmTree.getroot()
        _XmlRequest: bytes = ET.tostring(root,encoding='utf8', method='xml') + ET.tostring(quantRoot,encoding='utf8', method='xml')
        _XmlRequest = _XmlRequest.decode().replace('\n','')
        
        response = requests.post(self.host, _XmlRequest, verify=False)
        xpars = xmltodict.parse(response.text, dict_constructor=dict)
        json_response = json.loads(json.dumps(xpars))
        track_response: dict = json_response["TrackResponse"]
        
        if "Error" in track_response["Response"].keys():
            raise TrackError(**track_response["Response"]["Error"])
        
        if isinstance(track_response["Shipment"]["Package"]["Activity"], dict):
            track_response['Shipment']["Package"]["Activity"] = [track_response["Shipment"]["Package"]["Activity"]]
        
        
        response = TrackResponse(**track_response)
        
        return response
    
    
    
    def get_package(self, reference_number_or_tracking_number: str, track_type: TrackType):
        """
        Get Tracking Information By ReferenceNumber Or TrackingNumber

        Args:
            reference_number_or_tracking_number (str): ReferenceNumber Or TrackingNumber
            track_type (TrackType): TrackType For Find

        Returns:
            TrackResponse: TrackResponse Object Or Raise TrackError
        """
        response = self.create_xml_request(reference_number_or_tracking_number, track_type)
        return response
    
    



