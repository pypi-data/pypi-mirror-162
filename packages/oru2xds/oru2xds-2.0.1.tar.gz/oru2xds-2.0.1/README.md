# ORU2XDS

oru2xds allows you to receive an HL7 v2.x message in ER7 format, with MLLP transport, into an IHE XDS.b Provide and Register Document Set-b \[ITI-41\] transaction, as actor Document Source, which is sent to an XDS repository as a properly formatted SOAP message over HTTP. The result of the operation is then used to build an HL7 v2.x ACK^R01 acknowledge message back to the source.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You should have some modules available to python3, in order to run oru2xds.
Required Python modules are hl7, striprtf, lxml, uuid, requests and requests-toolbelt.

## Installing

```
$ pip install oru2xds
```

If you plan to use it right now, without first testing it using xdstoolkit, proceed to the #Configurations section

### Install XDS toolkit for testing purposes (optional)

If you do not have a tested IHE XDS repository, or if you want to try oru2xds first against a reference implementation like xdstoolkit, here is how to do it. We will run xdstoolkit as a docker container (from https://hub.docker.com/r/antocm/xdstools774)

```
$ docker pull antocm/xdstools774
$ docker image ls
```

Now you have XDS toolkit installed as a docker image running in http://localhost>:8080/xdstools4/

XDS Toolkit config password: easy
Tomcat UI username/password: admin/admin

You can now run the XDS toolkit with:

`$ docker run -it -p 8080:8080 -p 8888:8888 -p 8443:8443 -v $PWD/cache:/tmp/xdstoolkit-cache antocm/xdstools774`

And stop it with:

`$ docker stop $(docker ps -q --filter ancestor=antocm/xdstools774)`

If you want to restart it, you can just
docker start  `docker ps -q -l` # restart it in the background
docker attach `docker ps -q -l` # reattach the terminal & stdin

To list images use $ docker image ls
To list running containers use $docker ps

## Preparations for a test conversion

* a XDS toolkit should be available. Open a browser in http://localhost:8080/xdstools4/
* Go to "Toolkit configuration" on the left toolbar.
* Type the admin password "easy".
* Check the "External cache" to be /tmp/xdstoolkit-cache which should be now mapped to the directory "cache" of your current directory.
* Check the Toolkit Port to be 8080, as defined above.
* Close the "ToolkitConf" tab.
* Go to "Simulators" on the left toolbar.
* Select actor type and select "Document Repository/Registry", Simulator ID "1" and press "Create Actor Simulator".
* Select the row with ID "Default__1" and press the "Edit" button below.
* Confirm that PnR endpoint is http://localhost:8080/xdstools4/sim/default__1/rep/prb
* Close the "SimConfig default__1" tab.
* Close the "SimCntl" tab.
* Go to "Manage Patient IDs" on the left toolbar.
* In the "Favorite Patient IDs" list, select the patient "IHEBLUE-2709^^^&1.3.6.1.4.1.21367.13.20.3000&ISO"
* From the "Generate V2 Patient Identity Feed", make sure that "Patient ID to send" is "Selection in Favorites"
* From the SAML dropdown list, select "SAML OFF"
* From the "Send to"Document Registry:", select "default__1"
* Press "Run" to issue a patient identity feed
* You are ready to perform an initial test.

### Running a test conversion

From the working directory where you have downloaded the oru2xds converter:

`$ ./oru2xds.py`

Open another terminal window, and send an HL7 test message to the configured HL7 listening port

`$ ~/.local/bin/mllp_send -p 2575 -f tests/sample1-ORU-R01.hl7 --loose localhost`

Look at the HL7 ACK response message,

### Examine the resulting logs

Log files are placed in the log directory.
    `oru2xds-<DATE>.log` - general logs
    `cda/` - folder with the generated HL7 CDA document
    `xds_requests/` - folder with the generated XDS Provide and Register Document Set-b requests
    `soap/` - folder with the generated SOAP requests and responses

Depending on the configuration set on config.py, for the variables
```
    LOG_XDS_REQUEST_TOFILE = True/False
    LOG_SOAP_ENVELOPE_TOFILE = True/False
    LOG_SOAP_RESPONSE_TOFILE = True/False
```
you may define if those files are generated or not.

## Configurations

### oru2xds general configurations

General configuration for the oru2xds is located in the file config.py. You may edit the file to suit your needs.
Mapping between HL7 v2.x ORU message
* CDA metadata is placed in the file hl7_cda.py
* XDS metadata is placed in the file ihe_xds.py.

All metadata configuration must be done in the section below the marker.

### HL7 CDA Metadata configurations

Metadata should be according to the Implementation Guide for CDA Release 2:
  Implementation Guide for CDA Release 2:
  Imaging Integration Levels 1, 2, and 3
  Basic Imaging Reports in CDA and DICOM
 Diagnostic Imaging Reports (DIR) – Universal Realm CDAR2_II_BIMGRPTS_R1_INF_2009MAR.pdf

Configuring the mapping of the fields is tricky. It should be done inside the Python scripts, setting the values of the properties of the class .

Open the hl7_cda.py and look for the placeholder
###################################################################
## Main configuration
###################################################################

All the configuration should be done before the placeholder shows up:

###################################################################
## End of Main configuration
###################################################################

they must be inserted programatically under each metadata field structure, as sampled there.

```
self.m_author = {
			"time": hl7message['OBR.F22'],
			"id_extension": hl7message['OBR.F32.R1.C1.S1'],
			"id_root": "1.3.6.1.4.1.55196.1.3.2.4",
			"assignedAuthorAssignedPersonName": hl7message['OBR.F32.R1.C1.S2'],
			"assignedAuthorRepresentedOrganizationIdRoot": "1.3.6.1.4.1.55196.1.3",
			"assignedAuthorRepresentedOrganizationName": "Example hospital - Radiology department"
		}
```

### XDS Metadata configurations

Configuring the mapping of the fields is tricky. It should be done inside the Python scripts, setting the values of the properties of the class .

Open the ihe_xds.py and look for the placeholder
###################################################################
## Main configuration
###################################################################

All the configuration should be done before the placeholder shows up:

###################################################################
## End of Main configuration
###################################################################

they must be inserted programatically under each metadata field structure, as sampled there.

For example, the m_DocumentEntry_author is built as:

```
	m_DocumentEntry_author = [[
		{
			"authorvalue": [hl7message['OBR.F32.R1.C1.S2']],
			"authorrole": "authorPerson",
		},
		{
			"authorvalue": ["Example hospital - Radiology department"],
			"authorrole": "authorInstitution"
		}
	]]
```

The authorPerson is taken from the HL7 message as hl7message\['OBR.F32.R1.C1.S2'\] meaning OBR segment, field 32, component 1, sub-component 2.
The authorRole is hard coded with a fixed value.

Here are the fields that are required or optional in an XDS DocumentEntry and SubmissionSet. Folder is not supported.

These are the following fields that should go into an XDS document submission request
* Metadata Element 	Metadata Attribute 	XDS DS
* DocumentEntry		author					R2
* DocumentEntry		availabilityStatus		O
* DocumentEntry		classCode				R
* DocumentEntry		comments				O
* DocumentEntry		confidentialityCode		R
* DocumentEntry		creationTime			R
* DocumentEntry		entryUUID				R
* DocumentEntry		eventCodeList			O
* DocumentEntry		formatCode				R
* DocumentEntry		hash					O
* DocumentEntry		healthcareFacilityTypeCode		R
* DocumentEntry		homeCommunityId			O
* DocumentEntry		languageCode			R
* DocumentEntry		legalAuthenticator		O
* DocumentEntry		limitedMetadata			X
* DocumentEntry		mimeType				R
* DocumentEntry		objectType				R
* DocumentEntry		patientId				R
* DocumentEntry		practiceSettingCode		R
* DocumentEntry		referenceIdList			O
* DocumentEntry		repositoryUniqueId		O
* DocumentEntry		serviceStartTime		R2
* DocumentEntry		serviceStopTime			R2
* DocumentEntry		size					O
* DocumentEntry		sourcePatientId			R
* DocumentEntry		sourcePatientInfo		O
* DocumentEntry		title					O
* DocumentEntry		typeCode				R
* DocumentEntry		uniqueId				R
* DocumentEntry		URI						O

* SubmissionSet		author					R2
* SubmissionSet		availabilityStatus		O
* SubmissionSet		comments				O
* SubmissionSet		contentTypeCode			R
* SubmissionSet		entryUUID				R
* SubmissionSet		homeCommunityId			O
* SubmissionSet		intendedRecipient		O
* SubmissionSet		limitedMetadata			X
* SubmissionSet		patientId				R
* SubmissionSet		sourceId				R
* SubmissionSet		submissionTime			R
* SubmissionSet		title					O
* SubmissionSet		uniqueId				R

Note: Folder is not implemented
* Folder			availabilityStatus		O
* Folder			codeList				R
* Folder			comments				O
* Folder			entryUUID				R
* Folder			homeCommunityId			O
* Folder			lastUpdateTime			O
* Folder			limitedMetadata			X
* Folder			patientId				R
* Folder			title					R
* Folder			uniqueId				R

## Built With

* [lxml](https://lxml.de/) - All XML processing
* [aiorun](https://github.com/cjrh/aiorun) - creates the HL7 server service
* [python-hl7](https://python-hl7.readthedocs.io/en/latest/) - MLLP server and HL7 message parser
* [striprtf](https://github.com/joshy/striprtf) - Convert RTF file to strings
* [requests](https://requests.readthedocs.io/en/latest/) - HTTP send and receive
* [requests-toolbelt](https://github.com/requests/toolbelt) - Multipart encoding and decoding

## Author

* **Antonio Martins** - *Initial work* - (https://github.com/antocm)

## License

This project is licensed under the GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* IHE XDS.b profile and all the available documentation
* HL7 CDA Implementation Guide for CDA Release 2: Imaging Integration Levels 1, 2, and 3 Basic Imaging Reports in  CDA and DICOM Diagnostic Imaging Reports (DIR) – Universal Realm CDAR2_II_BIMGRPTS_R1_INF_2009MAR.pdf
