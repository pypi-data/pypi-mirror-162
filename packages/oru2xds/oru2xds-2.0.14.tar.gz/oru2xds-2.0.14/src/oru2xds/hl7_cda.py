 #!/usr/bin/python3
#
# Antonio Martins (digiplan.pt@gmail.com)
#

# Creates an HL7 CDA according to:
# Implementation Guide for CDA Release 2:
# Imaging Integration Levels 1, 2, and 3
# Basic Imaging Reports in CDA and DICOM
# Diagnostic Imaging Reports (DIR) – Universal Realm CDAR2_II_BIMGRPTS_R1_INF_2009MAR.pdf

import os
import logging
import hashlib
from lxml import etree
from lxml.builder import ElementMaker
from striprtf.striprtf import rtf_to_text
import hl7

import config
import hl7_v2x_receiver


###################################################################


# Logging facility
logger = logging.getLogger(config.APP_NAME + "." + __name__)

# Define namespaces
attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
nsmap = {
	None: 'urn:hl7-org:v3',
	'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}


###################################################################
## class CDABuilder
###################################################################

class HL7CdaBuilder:
	def __init__(self):
		# All the metadata fiels are defined here, so they can be accessed from all
		# functions in this module. They are mapped in function fill_cda_metadata()

		# ClinicalDocument/id
		self.m_id = {
			"extension": None,
			"id_root": None
		}

		# Exam code
		self.m_code = {
			"code": None,
			"codeSystem": None,
			"codeSystemName": None,
			"displayName": None
		}

		# ClinicalDocument/title
		self.m_title = None

		# ClinicalDocument/effectiveTime
		self.m_effectiveTime = None

		# ClinicalDocument/confidentialityCode
		self.m_confidentialityCode = {
			"code": None,
			"codeSystem": None
		}

		# ClinicalDocument/languageCode
		self.m_languageCode = None

		# ClinicalDocument/setId
		self.m_setId = {
			"extension": None,
			"root": None
		}

		# ClinicalDocument/versionNumber
		self.m_versionNumber_value = None

		#
		# Participants
		#

		# recordTarget (the patient)
		self.m_patient = {
			"id": None,
			"assigningAuthorityName": None,
			"assigningAuthorityOID": None,
			"name": None,
			"birthdate": None,
			"sex": None
		}

		# author
		self.m_author = {
			"time": None,
			"id_extension": None,
			"id_root": None,
			"assignedAuthorAssignedPersonName": None,
			"assignedAuthorRepresentedOrganizationIdRoot": None,
			"assignedAuthorRepresentedOrganizationName": None
		}

		# dataEnterer
		# informant

		# custodian
		self.m_custodian = {
			"assignedCustodianRepresentedCustodianOrganizationIdRoot": None,
			"assignedCustodianRepresentedCustodianOrganizationName": None
		}

		# informationRecipient

		# legalAuthenticator
		self.m_legalAuthenticator = {
			"time": None,
			"signatureCode": None,
			"assignedEntityIdExtension": None,
			"assignedEntityIdRoot": None,
			"assignedEntityAssignedPersonName": None
		}

		# authenticator
		self.m_authenticator = {
			"time": None,
			"signatureCode": None,
			"assignedEntityIdExtension": None,
			"assignedEntityIdRoot": None,
			"assignedEntityAssignedPersonName": None
		}

		# participant
		# <participant typeCode="REF">
		#	<associatedEntity classCode="PROV">
		#		<id nullFlavor="NI"/>
		#		<addr nullFlavor="NI"/>
		#		<telecom nullFlavor="NI"/>
		#		<associatedPerson>
		#			<name>
		#				<given>Amanda</given>
		#				<family>Assigned</family>
		#				<suffix>MD</suffix>
		#			</name>
		#		</associatedPerson>
		#	</associatedEntity>
		#</participant>

		#
		# END of Participants
		#

		# In fullfillment of
		self.m_inFullfillmentOf = {
			"id_root": None,
			"id_extension": None,
			"code": None,
			"codeSystem": None,
			"codeSystemName": None,
			"displayName": None,
		}

		# Documentation of
		self.m_documentationOf = {
			"classCode": None,
			"id_root": None,
			"code": None,
			"codeSystem": None,
			"codeSystemName": None,
			"displayName": None,
			"effectiveTime": None,
		}

		# authorization
		# relatedDocument
		# componentOf

		#
		# Body
		#

		# Structured body components
		self.m_cdaBody_Sections = None


###################################################################
## Main configuration
###################################################################


	# This function fills all CDA sections with fixed data order
	# otherwise information taken from the received HL7 message.
	#
	# Use the value hl7message['MSH.F10'] for instances
	# if you want to use the field MSH-10 into a variable that represents
	# some CDA metadata.
	#
	# format hl7message[SEGMENT.Fx.Ry.Cw.Sz] 	for single values
	#
	# If you want a string with multiple fiels, use:
	# hl7message.unescape(str(hl7message.segment('PID')[3][1])))
	# In both cases, the unescaped version of the string will be used.
	# Otherwise fill with fixed strings, or some python function.
	def fill_cda_metadata(self, hl7message):
		logger.info('Assigning HL7 message values into variables')

		# ClinicalDocument/id
		self.m_id = {
			"extension": hl7message['MSH.F10'],
			"id_root": "1.3.6.1.4.1.55196.1.1.2.5"
		}

		# ClinicalDocument/code
		# CONF-DIR-17: The value for ClinicalDocument/code SHOULD be selected from
		# Table 4: LOINC® Document Type Codes 2.16.840.1.113883.6.1 LOINC DYNAMIC
		# and SHOULD be 18748-4 "Diagnostic Imaging Report" 2.16.840.1.113883.6.1 LOINC STATIC .
		# CONF-DIR-18: Implementations MAY use local codes in translation elements to
		# further refine the document type.
		# Consider OBR-4.1 for the exam code
		self.m_code = {
			"code": "18748-4",
			"codeSystem": "2.16.840.1.113883.6.1",
			"codeSystemName": "LOINC",
			"displayName": "Diagnostic Imaging Report",
		}

		# ClinicalDocument/title
		self.m_title = "Imaging report"

		# ClinicalDocument/effectiveTime
		self.m_effectiveTime = hl7message['OBR.F22']

		# ClinicalDocument/confidentialityCode
		self.m_confidentialityCode = {
			"code": "N",
			"codeSystem": "2.16.840.1.113883.5.25"
		}

		# ClinicalDocument/languageCode
		self.m_languageCode = "en-US"

		# ClinicalDocument/setId
		self.m_setId = {
			"extension": None,
			"root": None
		}

		# ClinicalDocument/versionNumber
		self.m_versionNumber_value = None
		# self.m_versionNumber_value = "1"

		# This call finds the PID-3 repetition that has the patient ID in the 
		# XDS affinity domain
		# Use this variable instead of "repetition" in the HL7 message
		xad_pid_repetition = hl7_v2x_receiver.Hl7v2x.hl7_find_xad_pid_repetition(hl7message)
		logger.info("Domain assigning authority OID (XAD PID) is present as repetition %s of PID segment", xad_pid_repetition)

		# recordTarget (Patient)
		self.m_patient = {
			"id": hl7message.unescape(str(hl7message.segment('PID')(3)(xad_pid_repetition)(1))),
			"assigningAuthorityName": hl7message.unescape(str(hl7message.segment('PID')(3)(xad_pid_repetition)(4)(1))),
			"assigningAuthorityOID": hl7message.unescape(str(hl7message.segment('PID')(3)(xad_pid_repetition)(4)(2))),
			"name": hl7message.unescape(str(hl7message.segment('PID')(5)(0))),
			"birthdate": hl7message['PID.F7'],
			"sex": hl7message['PID.F8']
		}

		# author
		self.m_author = {
			"time": hl7message['OBR.F22'],
			"id_extension": hl7message['OBR.F32.R1.C1.S1'],
			"id_root": "1.3.6.1.4.1.55196.1.3.2.4",
			"assignedAuthorAssignedPersonName": hl7message['OBR.F32.R1.C1.S2'],
			"assignedAuthorRepresentedOrganizationIdRoot": "1.3.6.1.4.1.55196.1.3",
			"assignedAuthorRepresentedOrganizationName": "Example hospital - Radiology department"
		}

		# dataEnterer
		# TODO: To implement

		# informant
		# TODO: To implement

		# custodian
		# Consider representedOrganization_id to be PV1-39
		self.m_custodian = {
			"assignedCustodianRepresentedCustodianOrganizationIdRoot": "1.3.6.1.4.1.55196.1.3",
			"assignedCustodianRepresentedCustodianOrganizationName": "Example hospital - Radiology department"
		}

		# informationRecipient
		# TODO: To implement

		# legalAuthenticator
		self.m_legalAuthenticator = {
			"time": hl7message['OBR.F22'],
			"signatureCode": "S",
			"assignedEntityIdExtension": hl7message['OBR.F32.R1.C1.S1'],
			"assignedEntityIdRoot": "1.3.6.1.4.1.55196.1.3.2.4",
			"assignedEntityAssignedPersonName": hl7message['OBR.F32.R1.C1.S2']
		}

		# authenticator
		# TODO: To implement
		# self.m_authenticator = {
		# 	"time": "20060922",
		# 	"signatureCode": "S",
		# 	"assignedEntityIdExtension": "69",
		# 	"assignedEntityIdRoot": "2.16.840.1.113883.2.10.1.1.2",
		# 	"assignedEntityAssignedPersonName": "Ducrey^Gabriel"
		# }

		# participant
		# TODO: To implement

		# inFullfillmentOf
		# CONF-DIR-49: One or more inFullfillmentOf elements MAY be present. They
		# represent the Placer Order that was fulfilled by the imaging procedure(s) covered by
		# this report document.
		self.m_inFullfillmentOf = {
			"id_root": "1.3.6.1.4.1.55196.1.3.2.2",
			"id_extension": hl7message['OBR.F18'] + hl7message['ZEI.F1'],
			"code": hl7message['OBR.F4.R1.C1'],
			"codeSystem": "1.3.6.1.4.1.55196.2.1",
			"codeSystemName": "Tabela MDCT - Imagiologia",
			"displayName": hl7message['OBR.F4.R1.C2'],
		}

		# documentationOf
		# TODO: To implement
		# self.m_documentationOf = {
		# 	"classCode": "ACT",
		# 	"id_root": "1.2.826.0.1.5968184.2.2.1.1555065954200.9891",
		# 	"code": "11010",
		# 	"codeSystem": "SAUDACOR.PROCEDURES",
		# 	"codeSystemName": "Saudacor Procedures",
		# 	"displayName": "ABDÓMEN SIMPLES, UMA INCIDÊNCIA",
		# 	"effectiveTime": "20190902120127+0000",
		# }

		# authorization
		# TODO: To implement

		# relatedDocument
		# TODO: To implement

		# componentOf
		# TODO: To implement

		# CONF-DIR-102: The templateId for a Findings section SHALL be 2.16.840.1.113883.10.20.6.1.2.
		self.m_cdaBody_Sections = [
			{
				"templateId": "2.16.840.1.113883.10.20.6.1.2",
				"code": "18782-3",
				"codeSystem": "2.16.840.1.113883.6.1",
				"codeSystemName": "LOINC",
				"displayName": "RADIOLOGY STUDY OBSERVATION",
				"title": "Observação",
				"text": hl7message['OBX.F5']
			},
			{
				"templateId": "",
				"code": "11329-0",
				"codeSystem": "2.16.840.1.113883.6.1",
				"codeSystemName": "LOINC",
				"displayName": "HISTORY GENERAL",
				"title": "Clinical information",
				"text": hl7message['OBR.F13']
			}
		]


###################################################################
## End of Main configuration
###################################################################


	#
	## calculate_cda_size
	#
	# Calculates the size of the CDA document received as string
	def calculate_cda_size(self, cda_xml_str):
		# Now that the CDA document is created, we should calculate the hash and size
		#     in bytes
		cda_size = len(cda_xml_str.encode('utf-8'))
		logger.info("CDA document has %s bytes", cda_size)
		return cda_size


	#
	## calculate_cda_hash
	#
	# Calculates the SHA-1 hash of the CDA document received as string
	def calculate_cda_hash(self, cda_xml_str):
		hash_object = hashlib.sha1(cda_xml_str.encode('utf-8'))
		cda_hash = hash_object.hexdigest()
		logger.info("SHA1 of CDA document: %s", cda_hash)
		return cda_hash


	#
	## convert_cda_paragraphs
	#
	# Converts newlines into proper cda <paragraphs>
	def convert_cda_paragraphs(self, text_field):
		# Now insert <paragraph>...</paragraph> on each line
		text_field = text_field.split(os.linesep)
		for idx in range(0, len(text_field)):
			text_field[idx] = "<paragraph>" + text_field[idx] + "</paragraph>"
		text_field = "".join(text_field)
		return text_field


	###################################################################
	## CDA metadata
	###################################################################


	#
	## cda_typeId_section
	#
	# ClinicalDocument/typeId
	# The ClinicalDocument/typeId element identifies the constraints imposed by CDA R2
	# on the content, essentially acting as a version identifier. The @root and @extension
	# values of this element are specified as shown below.
	# CONF-DIR-11: The root attribute of the typeId element SHALL be
	# 2.16.840.1.113883.1.3 and extension attribute SHALL be POCD_HD000040.
	def cda_typeId_section(self, parentNode):
		E = ElementMaker(nsmap=nsmap)

		parentNode.append(
			E.typeId(
				root="2.16.840.1.113883.1.3",
				extension="POCD_HD000040"
			)
		)


	#
	## cda_templateId_section
	#
	# ClinicalDocument/templateId
	# The ClinicalDocument/templateId element identifies the template that defines
	# constraints on the content. The ClinicalDocument/templateId with the content
	# shown below indicates conformance to this specification.
	# CONF-DIR-12: A ClinicalDocument/templateId element SHALL be present with
	# the value 2.16.840.1.113883.10.20.6.
	def cda_templateId_section(self, parentNode):
		E = ElementMaker(nsmap=nsmap)

		parentNode.append(
			E.templateId(
				root="2.16.840.1.113883.10.20.6"
			)
		)


	#
	## cda_id_section
	#
	# ClinicalDocument/id
	# The ClinicalDocument/id element is an instance identifier data type (see HL7
	# Version 3 Abstract Data Types). For compatibility with DICOM-SR, this specification
	# constrains the root attribute to an OID, and UUIDs are prohibited. Since every UUID
	# has an OID representation (see ITU-T X.667), this constraint should not pose an
	# exceptional burden on implementers. If an extension is present, the root uniquely
	# identifies the scope of the extension. The root and extension attributes uniquely
	# identify the document.
	# OIDs are limited by this specification to no more than 64 characters in length for
	# compatibility with other standards and IGs.
	#  CONF-DIR-13: The ClinicalDocument/id element SHALL be present. The
	# ClinicalDocument/id/@root attribute SHALL be a syntactically correct OID, and
	# SHALL NOT be a UUID.
	# CONF-DIR-14: OIDs SHALL be represented in dotted decimal notation, where each
	# decimal number is either 0 or starts with a nonzero digit. More formally, an OID
	# SHALL be in the form ([0-2])(.([1-9][0-9]*|0))+
	# CONF-DIR-15: OIDs SHALL be no more than 64 characters in length.
	def cda_id_section(self, parentNode):
		if not self.m_id["extension"] or not self.m_id["id_root"]:
			raise RuntimeError("ClinicalDocument/id extension or root are required fields. Aborting CDA creation")

		E = ElementMaker(nsmap=nsmap)

		logger.debug("ClinicalDocument/id:")
		logger.debug("    extension: \"%s\"", self.m_id["extension"])
		logger.debug("    root: \"%s\"", self.m_id["id_root"])

		parentNode.append(
			E.id(
				extension = self.m_id["extension"],
				root = self.m_id["id_root"]
			)
		)
		# TODO: Not supported multiple IDs
		#	parentNode.append(
		#		E.id(
		#			root="2.16.840.1.113883.2.9.2.30"
		#			extension="030308.0000X0AQC9.57833-6.CDA"
		#			displayable="true"
		#			assigningAuthorityName="Direção Regional dos Açores"
		#		)
		#	)


	#
	## cda_code_section
	#
	# ClinicalDocument/code
	# CONF-DIR-16: The ClinicalDocument/code element SHALL be present and specifies
	# the type of the clinical document.
	# Given that reports generated according to this IG may be transformed from established
	# collections of imaging reports already stored with their own type codes, this IG does not
	# prescribe a closed, static set of Document Type codes. The set of LOINC codes listed
	# here may be extended by additions to LOINC and supplemented by local codes as
	# translations.
	# CONF-DIR-17: The value for ClinicalDocument/code SHOULD be selected from
	# Table 4: LOINC® Document Type Codes 2.16.840.1.113883.6.1 LOINC DYNAMIC
	# and SHOULD be 18748-4 "Diagnostic Imaging Report" 2.16.840.1.113883.6.1 LOINC STATIC .
	# CONF-DIR-18: Implementations MAY use local codes in translation elements to
	# further refine the document type.
	def cda_code_section(self, parentNode):
		if not self.m_code["code"] or not self.m_code["codeSystem"] or not self.m_code["codeSystemName"] or not self.m_code["displayName"]:
			raise RuntimeError("ClinicalDocument/code is a required field and is partly or fully missing. Aborting CDA creation")

		E = ElementMaker(nsmap=nsmap)

		logger.debug("ClinicalDocument/code:")
		logger.debug("    code: \"%s\"", self.m_code["code"])
		logger.debug("    codeSystem: \"%s\"", self.m_code["codeSystem"])
		logger.debug("    codeSystemName: \"%s\"", self.m_code["codeSystemName"])
		logger.debug("    displayName: \"%s\"", self.m_code["displayName"])

		parentNode.append(
			E.code(
				code = self.m_code["code"],
				codeSystem = self.m_code["codeSystem"],
				codeSystemName = self.m_code["codeSystemName"],
				displayName = self.m_code["displayName"]
			)
		)


	#
	## cda_title_section
	#
	# ClinicalDocument/title
	# CONF-DIR-21: The title element SHALL be present and specifies the local name
	# used for document
	def cda_title_section(self, parentNode):
		if not self.m_title:
			raise RuntimeError("ClinicalDocument/title is a required field and is missing. Aborting CDA creation")

		E = ElementMaker(nsmap=nsmap)

		logger.debug("ClinicalDocument/title: \"%s\"", self.m_title)

		parentNode.append(
			E.title(self.m_title)
		)


	#
	## cda_effectiveTime_section
	#
	# ClinicalDocument/effectiveTime
	# CONF-DIR-22: The ClinicalDocument/effectiveTime element SHALL be present
	# and specifies the creation time of the document. All Diagnostic Imaging Report
	# documents authored by direct input to a computer system SHOULD record an
	# effectiveTime that is precise to the second.
	# In case the CDA was transformed from a DICOM SR, the effectiveTime is the creation
	# time of the SR document.
	def cda_effectiveTime_section(self, parentNode):
		if not self.m_title:
			raise RuntimeError("ClinicalDocument/effectiveTime is a required field and is missing. Aborting CDA creation")

		E = ElementMaker(nsmap=nsmap)

		logger.debug("ClinicalDocument/effectiveTime: \"%s\"", self.m_effectiveTime)

		parentNode.append(
			E.effectiveTime(
				value = self.m_effectiveTime
			)
		)


	#
	## cda_confidentialityCode_section
	#
	# ClinicalDocument/confidentialityCode
	# CDA R2 requires that the ClinicalDocument/confidentialityCode be present. It
	# specifies the confidentiality assigned to the document. This specification provides no
	# further guidance on documents with respect to the vocabulary used for
	# confidentialityCode, nor treatment, nor implementation of confidentiality
	def cda_confidentialityCode_section(self, parentNode):
		if not self.m_confidentialityCode["code"] or not self.m_confidentialityCode["codeSystem"]:
			raise RuntimeError("ClinicalDocument/confidentialityCode is a required field and is fully or partly missing. Aborting CDA creation")

		E = ElementMaker(nsmap=nsmap)

		logger.debug("ClinicalDocument/confidentialityCode:")
		logger.debug("    code: \"%s\"", self.m_confidentialityCode["code"])
		logger.debug("    codeSystem: \"%s\"", self.m_confidentialityCode["codeSystem"])

		parentNode.append(
			E.confidentialityCode(
				code = self.m_confidentialityCode["code"],
				codeSystem = self.m_confidentialityCode["codeSystem"]
			)
		)


	#
	## cda_languageCode_section
	#
	# ClinicalDocument/languageCode
	# The ClinicalDocument/languageCode specifies the language of the report. Diagnostic
	# Imaging Reports must be readable by medical practitioners, caregivers, and patients.
	# CONF-DIR-23: ClinicalDocument/languageCode SHALL be present.
	# CONF-DIR-24: nn-CC. ClinicalDocument/languageCode SHALL be in the form nn, or
	# CONF-DIR-25: The nn portion of ClinicalDocument/languageCode SHALL be a legal
	# ISO-639-1 language code in lower case.
	# CONF-DIR-26: The CC portion ClinicalDocument/languageCode, if present, SHALL
	# be an ISO-3166 country code in upper case.
	def cda_languageCode_section(self, parentNode):
		if not self.m_languageCode:
			raise RuntimeError("ClinicalDocument/languageCode is a required field and is missing. Aborting CDA creation")

		E = ElementMaker(nsmap=nsmap)

		logger.debug("ClinicalDocument/languageCode: \"%s\"", self.m_languageCode)

		parentNode.append(
			E.languageCode(
				code = self.m_languageCode
			)
		)


	#
	## cda_setId_section
	#
	# ClinicalDocument/setId
	# The ClinicalDocument/setId element uses the instance identifier (II) data type. The
	# root attribute is a UUID or OID that uniquely identifies the scope of the identifier, and
	# the extension attribute is a value that is unique within the scope of the root for the set
	# of versions of the document. See Document Identification, Revisions, and Addenda in
	# Section 4.2.3.1 of the HL7 CDA Release 2.0 Specification for some examples showing
	# the use of the setId element.
	# CONF-DIR-27: Both ClinicalDocument/setId and
	# ClinicalDocument/versionNumber SHALL be present or both SHALL be absent.
	# CONF-DIR-28: The clinicalDocument/setId element SHALL be different from
	# ClinicalDocument/id when both are present (i.e., either the root or extension
	# must be different).
	# Note that setId and version number will not be present in transformed DICOM SR
	# documents.
	def cda_setId_section(self, parentNode):
		if not self.m_setId["extension"] or not self.m_setId["root"]:
			logger.warning("ClinicalDocument/setId is fully or partially missing. Skipping")
			return

		E = ElementMaker(nsmap=nsmap)

		logger.debug("ClinicalDocument/setId:")
		logger.debug("    extension: \"%s\"", self.m_setId["extension"])
		logger.debug("    root: \"%s\"", self.m_setId["root"])

		parentNode.append(
			E.setId(
				extension = self.m_setId["extension"],
				root = self.m_setId["root"]
			)
		)


	#
	## cda_versionNumber_section
	#
	# ClinicalDocument/versionNumber
	# See ClinicalDocument/setId
	def cda_versionNumber_section(self, parentNode):
		if not self.m_versionNumber_value:
			logger.warning("ClinicalDocument/versionNumber is missing. Skipping")
			return

		logger.debug("ClinicalDocument/versionNumber:")
		logger.debug("    value: \"%s\"", self.m_versionNumber_value)

		E = ElementMaker(nsmap=nsmap)

		parentNode.append(
			E.versionNumber(
				value = self.m_versionNumber_value
			)
		)


	# Participants
	# Only recordTarget, author, custodian, legalAuthenticator are supported.
	# Others are: dataEnterer, informant, informationRecipient
	# Not implemented


	#
	## cda_recordTarget_section
	#
	# recordTarget
	# The recordTarget element must be present. It records the patient or patients whose
	# health information is described by the clinical document.
	# CONF-DIR-30: At least one recordTarget/patientRole element SHALL be present.
	# CONF-DIR-31: A patient/birthTime element SHALL be present. The
	# patient/birthTime element SHALL be precise at least to the year, and SHOULD be
	# precise at least to the day, and MAY omit time zone. If unknown, it SHALL be
	# represented using a flavor of null.
	# CONF-DIR-32: A patient/administrativeGenderCode element SHALL be present.
	# If unknown, it SHALL be represented using a flavor of null. Values for
	# administrativeGenderCode SHOULD be drawn from the HL7 AdministrativeGender
	# vocabulary.
	# CONF-DIR-33: The maritalStatusCode, religiousAffiliationCode, raceCode,
	#  and ethnicGroupCode element MAY be present. If maritalStatusCode,
	# religiousAffiliationCode, raceCode, and ethnicGroupCode elements are
	# present, they SHOULD be encoded using the appropriate HL7 vocabularies.
	# CONF-DIR-34: minor child. The guardian element SHOULD be present when the patient is a
	# CONF-DIR-35: The providerOrganization element MAY be present.
	def cda_recordTarget_section(self, parentNode):
		if not self.m_patient["id"]:
			raise RuntimeError("recordTarget/PatientRole ID is a required field and is missing. Aborting CDA creation")
		# Optional
		if not self.m_patient["assigningAuthorityName"]:
			logger.warning("recordTarget/PatientRole assigningAuthorityName is missing. Continuing")
		if not self.m_patient["assigningAuthorityOID"]:
			raise RuntimeError("recordTarget/PatientRole assigningAuthorityOID is a required field and is missing. Aborting CDA creation")
		if not self.m_patient["name"]:
			raise RuntimeError("recordTarget/PatientRole name is a required field and is missing. Aborting CDA creation")
		if not self.m_patient["birthdate"]:
			raise RuntimeError("recordTarget/PatientRole birtTime is a required field and is missing. Aborting CDA creation")
		if not self.m_patient["sex"]:
			raise RuntimeError("recordTarget/PatientRole administrativeGenderCode is a required field and is missing. Aborting CDA creation")
		if config.AFFINITY_DOMAIN_ASSIGNING_AUTHORITY_OID != self.m_patient["assigningAuthorityOID"]:
			raise RuntimeError("Affinity Domain Assigning Authority OID does not match that of recordTarget/PatientRole assigningAuthorityOID")

		logger.debug("recordTarget/PatientRole:")
		logger.debug("    id: \"%s\"", self.m_patient["id"])
		logger.debug("    assigningAuthorityName: \"%s\"", self.m_patient["assigningAuthorityName"])
		logger.debug("    assigningAuthorityOID: \"%s\"", self.m_patient["assigningAuthorityOID"])
		logger.debug("    name: \"%s\"", self.m_patient["name"])
		logger.debug("    birthdate: \"%s\"", self.m_patient["birthdate"])
		logger.debug("    sex: \"%s\"", self.m_patient["sex"])

		E = ElementMaker(nsmap=nsmap)

		# TODO: Patient address and telecom is currently unsupported
		recordtarget = E.recordTarget (
			E.patientRole (
				E.id (
					extension = self.m_patient["id"],
					root = self.m_patient["assigningAuthorityOID"],
					assigningAuthorityName = self.m_patient["assigningAuthorityName"]
				),
				E.addr (
					nullFlavor = "NI"
				),
				E.telecom (
					nullFlavor = "NI"
				),
				E.patient (
					E.name (),
					E.administrativeGenderCode (
						code = self.m_patient["sex"],
						codeSystem ="2.16.840.1.113883.5.1"
					),
					E.birthTime (
						value = self.m_patient["birthdate"]
					)
				)
			)
		)
		# Now fills the name element
		patient_name = recordtarget.find(".//name")
		# Name should have at least one component
		# Splits based on ^ separator
		nameparts = self.m_patient["name"].split("^")
		if len(nameparts) >= 1:
			patient_name.append(E.family(nameparts[0]))
		if len(nameparts) >= 2:
			patient_name.append(E.given(nameparts[1]))
		if len(nameparts) >= 3:
			patient_name.append(E.given(nameparts[2]))
		if len(nameparts) >= 4:
			patient_name.append(E.prefix(nameparts[3]))
		parentNode.append(recordtarget)


	#
	## cda_author_section
	#
	# author
	# The author element represents the creator of the clinical document. If the role of the
	# actor is the entry of information from his or her own knowledge or application of skills,
	# that actor is the author. If one actor provides information to another actor who filters,
	# reasons, or algorithmically creates new information, then that second actor is also an
	# author, having created information from his or her own knowledge or skills. However,
	# that determination is independent from the determination of the first actor's
	# authorship. The DICOM author date (based on the DICOM attributes Content Date and
	# Content Time) is unchanged in a transformed SR document.
	# CONF-DIR-36: The author/time element represents the start time of the author’s
	# participation in the creation of the content of the clinical document. The
	#  author/time element SHALL be present.
	# CONF-DIR-37: The assignedAuthor/id element SHALL be present.
	#  CONF-DIR-38: An assignedAuthor element SHALL contain at least one
	# assignedPerson or assignedAuthoringDevice element.
	def cda_author_section(self, parentNode):
		if not self.m_author["time"]:
			raise RuntimeError("author/time is a required field and is missing. Aborting CDA creation")
		if not self.m_author["id_extension"]:
			raise RuntimeError("author/assignedAuthor id_extension is a required field and is missing. Aborting CDA creation")
		if not self.m_author["id_root"]:
			raise RuntimeError("author/assignedAuthor id_root is a required field and is missing. Aborting CDA creation")
		if not self.m_author["assignedAuthorAssignedPersonName"]:
			raise RuntimeError("author/assignedAuthor/assignedPersonName is a required field and is missing. Aborting CDA creation")
		if not self.m_author["assignedAuthorRepresentedOrganizationIdRoot"]:
			raise RuntimeError("author/assignedAuthor/RepresentedOrganizationIdRoot is a required field and is missing. Aborting CDA creation")
		if not self.m_author["assignedAuthorRepresentedOrganizationName"]:
			raise RuntimeError("author/assignedAuthor/RepresentedOrganizationName is a required field and is missing. Aborting CDA creation")

		logger.debug("author:")
		logger.debug("    time: \"%s\"", self.m_author["time"])
		logger.debug("    assignedAuthor id extension: \"%s\"", self.m_author["id_extension"])
		logger.debug("    assignedAuthor id root: \"%s\"", self.m_author["id_root"])
		logger.debug("    assignedAuthor assignedPerson name: \"%s\"", self.m_author["assignedAuthorAssignedPersonName"])
		logger.debug("    assignedAuthor representedOrganization id root: \"%s\"", self.m_author["assignedAuthorRepresentedOrganizationIdRoot"])
		logger.debug("    assignedAuthor representedOrganization name: \"%s\"", self.m_author["assignedAuthorRepresentedOrganizationName"])

		E = ElementMaker(nsmap=nsmap)

		author = E.author (
			E.time (
				value = self.m_author["time"]
			),
			E.assignedAuthor (
				E.id (
					extension = self.m_author["id_extension"],
					root = self.m_author["id_root"]
				),
				E.assignedPerson (
					E.name(
					)
				),
				E.representedOrganization (
					E.id (
						root = self.m_author["assignedAuthorRepresentedOrganizationIdRoot"]
					),
					E.name(self.m_author["assignedAuthorRepresentedOrganizationName"])
				)
			)
		)
		# Now fills the name element
		person_name = author.find(".//name")
		# Name should have at least one component
		# Splits based on ^ separator
		nameparts = self.m_author["assignedAuthorAssignedPersonName"].split("^")
		if len(nameparts) >= 1:
			person_name.append(E.family(nameparts[0]))
		if len(nameparts) >= 2:
			person_name.append(E.given(nameparts[1]))
		if len(nameparts) >= 3:
			person_name.append(E.given(nameparts[2]))
		if len(nameparts) >= 4:
			person_name.append(E.prefix(nameparts[3]))
		parentNode.append(author)


	#
	## cda_custodian_section
	#
	# Custodian
	# Based on the CDA R2 constraints (Section 4.2.2.3 of the CDA specification), the
	# custodian element is required and is the custodian of the clinical document.
	# The custodian is optional in DICOM SR documents. When transforming from SR to
	# CDA, if custodian is not present in the source document, it must be set according to
	# local organizational policies.
	def cda_custodian_section(self, parentNode):
		if not self.m_custodian["assignedCustodianRepresentedCustodianOrganizationIdRoot"]:
			raise RuntimeError("custodian/assignedCustodian/representedCustodianOrganization id root is a required field and is missing. Aborting CDA creation")
		if not self.m_custodian["assignedCustodianRepresentedCustodianOrganizationName"]:
			raise RuntimeError("custodian/assignedCustodian/representedCustodianOrganization name is a required field and is missing. Aborting CDA creation")

		logger.debug("custodian:")
		logger.debug("    assignedCustodian representedCustodianOrganization id root: \"%s\"", self.m_custodian["assignedCustodianRepresentedCustodianOrganizationIdRoot"])
		logger.debug("    assignedCustodian representedCustodianOrganization name: \"%s\"", self.m_custodian["assignedCustodianRepresentedCustodianOrganizationName"])

		E = ElementMaker(nsmap=nsmap)

		parentNode.append(
			E.custodian (
				E.assignedCustodian (
					E.representedCustodianOrganization (
						E.id (
							root = self.m_custodian["assignedCustodianRepresentedCustodianOrganizationIdRoot"]
						),
						E.name(self.m_custodian["assignedCustodianRepresentedCustodianOrganizationName"])
					)
				)
			)
		)


	#
	## cda_legalAuthenticator_section
	#
	# LegalAuthenticator
	# The legalAuthenticator element identifies the legal authenticator of the document
	# and must be present if the document has been legally authenticated. Based on local
	# practice, clinical documents may be released before legal authentication. This implies
	# that a clinical document that does not contain this element has not been legally
	# authenticated.
	# The act of legal authentication requires that a certain privilege be granted to the legal
	# authenticator depending upon local policy. All clinical documents have the potential for
	# legal authentication, given the appropriate credentials.
	# Local policies may choose to delegate the function of legal authentication to a device or
	# system that generates the clinical document. In these cases, the legal authenticator is
	# a person accepting responsibility for the document, not the generating device or system.
	# CONF-DIR-45: If the document has been signed, legalAuthenticator SHALL be present.
	# CONF-DIR-46: The assignedEntity/assignedPerson element SHALL be present in legalAuthenticator
	# legalAuthenticator.
	def cda_legalAuthenticator_section(self, parentNode):
		if not self.m_legalAuthenticator["time"]:
			logger.warning("legalAuthenticator/time is missing. Skipping")
			return
		if not self.m_legalAuthenticator["signatureCode"]:
			logger.warning("legalAuthenticator/signatureCode is missing. Skipping")
			return
		if not self.m_legalAuthenticator["assignedEntityIdExtension"] or not self.m_legalAuthenticator["assignedEntityIdRoot"] or not self.m_legalAuthenticator["assignedEntityAssignedPersonName"]:
			logger.warning("legalAuthenticator/assignedEntity is fully or partially missing. Skipping")
			return

		logger.debug("legalAuthenticator:")
		logger.debug("    time: \"%s\"", self.m_legalAuthenticator["time"])
		logger.debug("    signatureCode: \"%s\"", self.m_legalAuthenticator["signatureCode"])
		logger.debug("    assignedEntity id extension: \"%s\"", self.m_legalAuthenticator["assignedEntityIdExtension"])
		logger.debug("    assignedEntity id root: \"%s\"", self.m_legalAuthenticator["assignedEntityIdRoot"])
		logger.debug("    assignedEntity assignedPerson name: \"%s\"", self.m_legalAuthenticator["assignedEntityAssignedPersonName"])

		E = ElementMaker(nsmap=nsmap)

		legalauthenticator = E.legalAuthenticator (
			E.time (
				value = self.m_legalAuthenticator["time"]
			),
			E.signatureCode (
				code = self.m_legalAuthenticator["signatureCode"]
			),
			E.assignedEntity (
				E.id (
					extension = self.m_legalAuthenticator["assignedEntityIdExtension"],
					root = self.m_legalAuthenticator["assignedEntityIdRoot"]
				),
				E.assignedPerson (
					E.name (
					)
				)
			)
		)
		# Now fills the name element
		person_name = legalauthenticator.find(".//name")
		# Name should have at least one component
		# Splits based on ^ separator
		nameparts = self.m_legalAuthenticator["assignedEntityAssignedPersonName"].split("^")
		if len(nameparts) >= 1:
			person_name.append(E.family(nameparts[0]))
		if len(nameparts) >= 2:
			person_name.append(E.given(nameparts[1]))
		if len(nameparts) >= 3:
			person_name.append(E.given(nameparts[2]))
		if len(nameparts) >= 4:
			person_name.append(E.prefix(nameparts[3]))
		parentNode.append(legalauthenticator)


	#
	## cda_authenticator_section
	#
	# authenticator
	# The authenticator identifies the participant who attested to the accuracy of the
	# information in the document.
	# In radiology reporting environments, the authenticator would typically be a resident
	# who dictated the initial report and reviewed and approved the transcribed version, but
	# the report would still need to be legally authenticated by an attending radiologist.
	# CONF-DIR-47: An authenticator element MAY be present. The
	# assignedEntity/assignedPerson element SHALL be present in an authenticator element.
	def cda_authenticator_section(self, parentNode):
		if not self.m_authenticator["time"]:
			logger.warning("Not creating authenticator section as time is not present. Skipping")
			return
		if not self.m_authenticator["signatureCode"]:
			logger.warning("Not creating authenticator section as signatureCode is not present. Skipping")
			return
		if not self.m_authenticator["assignedEntityIdExtension"] or not self.m_authenticator["assignedEntityIdRoot"] or not self.m_authenticator["assignedEntityAssignedPersonName"]:
			logger.warning("Not creating authenticator section as assignedEntity is not present. Skipping")
			return

		E = ElementMaker(nsmap=nsmap)

		logger.debug("authenticator:")
		logger.debug("    time: \"%s\"", self.m_authenticator["time"])
		logger.debug("    signatureCode: \"%s\"", self.m_authenticator["signatureCode"])
		logger.debug("    assignedEntity id extension: \"%s\"", self.m_authenticator["assignedEntityIdExtension"])
		logger.debug("    assignedEntity id root: \"%s\"", self.m_authenticator["assignedEntityIdRoot"])
		logger.debug("    assignedEntity assignedPerson name: \"%s\"", self.m_authenticator["assignedEntityAssignedPersonName"])

		authenticator = E.authenticator (
			E.time (
				value = self.m_authenticator["time"]
			),
			E.signatureCode (
				code = self.m_authenticator["signatureCode"]
			),
			E.assignedEntity (
				E.id (
					extension = self.m_authenticator["assignedEntityIdExtension"],
					root = self.m_authenticator["assignedEntityIdRoot"]
				),
				E.assignedPerson (
					E.name (
					)
				)
			)
		)
		# Now fills the name element
		person_name = authenticator.find(".//name")
		# Name should have at least one component
		# Splits based on ^ separator
		nameparts = self.m_authenticator["assignedEntityAssignedPersonName"].split("^")
		if len(nameparts) >= 1:
			person_name.append(E.family(nameparts[0]))
		if len(nameparts) >= 2:
			person_name.append(E.given(nameparts[1]))
		if len(nameparts) >= 3:
			person_name.append(E.given(nameparts[2]))
		if len(nameparts) >= 4:
			person_name.append(E.prefix(nameparts[3]))
		parentNode.append(authenticator)


	#
	## cda_inFullfilmentOf_section
	#
	# inFullfillmentOf
	# CONF-DIR-49: One or more inFullfillmentOf elements MAY be present. They
	# represent the Placer Order that was fulfilled by the imaging procedure(s) covered by
	# this report document.
	# In both cases, inFullfillmentOf/order/id is mapped to the DICOM Accession
	# Number in the imaging data.
	def cda_inFullfilmentOf_section(self, parentNode):
		if not self.m_inFullfillmentOf["id_root"] or not self.m_inFullfillmentOf["id_extension"]:
			logger.warning("Not creating inFullfillmentOf section as ID root or extension is not present. Skipping")
			return
		if not self.m_inFullfillmentOf["code"]:
			logger.warning("Not creating inFullfillmentOf section as code is not present. Skipping")
			return
		if not self.m_inFullfillmentOf["codeSystem"]:
			logger.warning("Not creating inFullfillmentOf section as codeSystem is not present. Skipping")
			return
		if not self.m_inFullfillmentOf["codeSystemName"]:
			logger.warning("Not creating inFullfillmentOf section as codeSystemName is not present. Skipping")
			return
		if not self.m_inFullfillmentOf["displayName"]:
			logger.warning("Not creating inFullfillmentOf section as displayName is not present. Skipping")
			return

		logger.debug("inFullfillmentOf:")
		logger.debug("    order/id root: \"%s\"", self.m_inFullfillmentOf["id_root"])
		logger.debug("    order/id extension: \"%s\"", self.m_inFullfillmentOf["id_extension"])
		logger.debug("    order/code: \"%s\"", self.m_inFullfillmentOf["code"])
		logger.debug("    order/codeSystem: \"%s\"", self.m_inFullfillmentOf["codeSystem"])
		logger.debug("    order/codeSystemName: \"%s\"", self.m_inFullfillmentOf["codeSystemName"])
		logger.debug("    order/displayName: \"%s\"", self.m_inFullfillmentOf["displayName"])

		E = ElementMaker(nsmap=nsmap)

		parentNode.append(
			E.inFullfillmentOf (
				E.order (
					E.id (
						root = self.m_inFullfillmentOf["id_root"],
						extension = self.m_inFullfillmentOf["id_extension"]
					),
					# TODO: Unsupported more than one ID
					# Variables missing here!
					# E.id (
					# 	root = "1.2.752.24.29.20.5.1.20191022.7",
					# 	extension="2019019686"
					# ),
					E.code (
						code = self.m_inFullfillmentOf["code"],
						codeSystem = self.m_inFullfillmentOf["codeSystem"],
						codeSystemName = self.m_inFullfillmentOf["codeSystemName"],
						displayName = self.m_inFullfillmentOf["displayName"]
					)
				)
			)
		)


	#
	## cda_documentationOf_section
	#
	# documentationOf
	# Each documentationOf/ServiceEvent indicates an imaging procedure that the
	# provider describes and interprets in the content of the Diagnostic Imaging Report. The
	# main activity being described by this document is the interpretation of the imaging
	# procedure. This is shown by setting the value of the @classCode attribute of the
	# serviceEvent element to ACT, and indicating the duration over which care was
	# provided in the effectiveTime element. Within each documentationOf element, there
	# is one serviceEvent element. This event is the unit imaging procedure corresponding
	# to a billable item. The type of imaging procedure may be further described in the
	# serviceEvent/code element. This IG makes no specific recommendations about the
	# vocabulary to use for describing this event.
	def cda_documentationOf_section(self, parentNode):
		if not self.m_documentationOf["classCode"]:
			logger.warning("Not creating documentationOf section as classCode is not present. Skipping")
			return
		if not self.m_documentationOf["id_root"]:
			logger.warning("Not creating documentationOf section as id_root is not present. Skipping")
			return
		if not self.m_documentationOf["code"]:
			logger.warning("Not creating documentationOf section as code is not present. Skipping")
			return
		if not self.m_documentationOf["codeSystem"]:
			logger.warning("Not creating documentationOf section as codeSystem is not present. Skipping")
			return
		if not self.m_documentationOf["codeSystemName"]:
			logger.warning("Not creating documentationOf section as codeSystemName is not present. Skipping")
			return
		if not self.m_documentationOf["displayName"]:
			logger.warning("Not creating documentationOf section as displayName is not present. Skipping")
			return
		if not self.m_documentationOf["effectiveTime"]:
			logger.warning("Not creating documentationOf section as effectiveTime is not present. Skipping")
			return

		logger.debug("documentationOf:")
		logger.debug("    serviceEvent/classCode: \"%s\"", self.m_documentationOf["classCode"])
		logger.debug("    serviceEvent/id root: \"%s\"", self.m_documentationOf["id_root"])
		logger.debug("    serviceEvent/code: \"%s\"", self.m_documentationOf["code"])
		logger.debug("    serviceEvent/codeSystem: \"%s\"", self.m_documentationOf["codeSystem"])
		logger.debug("    serviceEvent/codeSystemName: \"%s\"", self.m_documentationOf["codeSystemName"])
		logger.debug("    serviceEvent/displayName: \"%s\"", self.m_documentationOf["displayName"])
		logger.debug("    serviceEvent effectiveTime value: \"%s\"", self.m_documentationOf["effectiveTime"])

		E = ElementMaker(nsmap=nsmap)

		parentNode.append(
			E.documentationOf (
				E.serviceEvent (
					E.id (
						root = self.m_documentationOf["id_root"]
					),
					# TODO: Unsupported more than one ID
					# Variables missing here!
					# E.id (
					# 	root = "1.2.752.24.29.20.7.1.20191022.9",
					# 	extension = "2019019686"
					# ),
					E.code (
						code = self.m_documentationOf["code"],
						codeSystem = self.m_documentationOf["codeSystem"],
						codeSystemName = self.m_documentationOf["codeSystemName"],
						displayName = self.m_documentationOf["displayName"]
					),
					classCode = self.m_documentationOf["classCode"]
				),
				E.effectiveTime (
					value = self.m_documentationOf["effectiveTime"]
				)
			)
		)


	#
	## cda_body
	#
	# CDA Body
	# CONF-DIR-74: A Diagnostic Imaging Report SHALL have a structuredBody element.
	# The content of this element makes up the human-readable text of the document.
	# The Section Type codes used in this IG are described below in Table 5
	# R - required, C - conditionally required, O - optional
	# DICOM Code	DICOM Code meaning 	LOINC Code 	LOINC Code Meaning 	Use
	# 121181		DICOM Object Catalog 	N/A 	N/A					C
	# 121060		History 				11329-0 HISTORY GENERAL		O
	# 121062		Request 				55115-0 REQUESTED IMAGING STUDIES INFORMATION O
	# 121064		Current Procedure Descriptions 55111-9 CURRENT IMAGING PROCEDURE DESCRIPTIONS O
	# 121066		Prior Procedure Descriptions 55114-3 PRIOR IMAGING PROCEDURE DESCRIPTIONS O
	# 121068		Previous Findings		18834-2 RADIOLOGY COMPARISON STUDY - OBSERVATION O
	# 121070		Findings				18782-3 RADIOLOGY STUDY OBSERVATION R
	# 121072		Impressions				19005-8 RADIOLOGY - IMPRESSION O
	# 121074		Recommendations			18783-1 RADIOLOGY STUDY - RECOMMENDATION O
	# 121076		Conclusions				55110-1 CONCLUSIONS			O
	# 121078		Addendum				55107-7 ADDENDUM			O
	# 121109		Indications for Procedure 18785-6 RADIOLOGY REASON FOR STUDY O
	# 121110		Patient Presentation	55108-5 CLINICAL PRESENTATION O
	# 121113		Complications			55109-3 COMPLICATIONS		O
	# 121111		Summary					55112-7 DOCUMENT SUMMARY	O
	# 121180		Key Images				55113-5 KEY IMAGES			O
	#
	# CONF-DIR-75: The DICOM Object Catalog section (see Section 3.2.1 DICOM Object
	# Catalog – DCM 121181), if present, SHALL be the first section in the document Body.
	# CONF-DIR-76: With the exception of the DICOM Object Catalog (templateId
	# 2.16.840.1.113883.10.20.6.1.1), all sections within the Diagnostic Imaging
	# Report content SHOULD contain a title element.
	# CONF-DIR-77: For sections not listed in Table 5, the section/code SHOULD be
	# selected from LOINC ® or DICOM.
	# The remainder of the examples in this section all show sample content that would
	# appear in the structuredBody element.
	# For Level 2 conformance, all section elements that are present in the Body of the
	# document must have a code and some nonblank text or one or more subsections, even
	# if the purpose of the text is only to indicate that information is unknown.
	# CONF-DIR-78: All sections defined in Table 5: Section Type Codes SHALL be top-level sections.
	# CONF-DIR-79: A section element SHALL have a code element which SHALL contain a
	# LOINC ® code if available, or DCM code for sections which have no LOINC ®
	# equivalent. This only applies to sections described in Table 5: Section Type Codes.
	# CONF-DIR-80: Apart from the DICOM Object Catalog, all other instances of section
	# SHALL contain at least one text element or one or more component elements.
	# CONF-DIR-81: All text or component elements SHALL contain content. text
	# elements SHALL contain PCDATA or child elements, and component elements SHALL
	# contain child elements.
	# CONF-DIR-82: The text elements (and their children) MAY contain Web Access to
	# DICOM Persistent Object (WADO) references to DICOM objects by including a
	# linkHtml element where @href is a valid WADO URL and the text content of
	# linkHtml is the visible text of the hyperlink.
	def cda_body(self, parentNode):
		if len(self.m_cdaBody_Sections) == 0:
			raise RuntimeError("No CDA body sections. At least one required.")

		component = etree.Element("component")
		structuredbody = etree.SubElement(component, "structuredBody")
		parentNode.append(component)

		E = ElementMaker(nsmap=nsmap)

		# Go through each body section of m_cdaBody_Sections
		for section in self.m_cdaBody_Sections:
			logger.debug("CDA body section beggining:")
			logger.debug("    templateId: \"%s\"", section["templateId"])
			logger.debug("    code: \"%s\"", section["code"])
			logger.debug("    codeSystem: \"%s\"", section["codeSystem"])
			logger.debug("    codeSystemName: \"%s\"", section["codeSystemName"])
			logger.debug("    displayName: \"%s\"", section["displayName"])
			logger.debug("    title: \"%s\"", section["title"])

			# Check if observation text is in RTF format, and strip it to plain text if so
			if (section["text"][0:6] == r'{\rtf1'):
				logger.info("text is in RTF format, converting to plain text")
				section_text = rtf_to_text(section["text"])
			else:
				section_text = section["text"]

			# Convert newlines into <paragraphs>
			section_text = self.convert_cda_paragraphs(section_text)
			# create xml element tree
			section_text_xml = etree.fromstring("<text>" + section_text + "</text>")

			logger.debug("    text: \"%s\"", section_text)

			new_section = E.section(
				E.code(
					code=section["code"],
					codeSystem=section["codeSystem"],
					codeSystemName=section["codeSystemName"],
					displayName=section["displayName"]
				),
				E.title(section["title"]),
			)
			new_section.append(section_text_xml)

			# Insert templateId if it exists
			if section["templateId"]:
				new_section.insert(0, etree.Element("templateId", root=section["templateId"]))

			component = etree.Element("component")
			component.append(new_section)
			structuredbody.append(component)


	#
	## build_cda
	#
	# Builds the whole CDA based on HL7 fields
	def build_cda(self, hl7message, content_id):
		self.fill_cda_metadata(hl7message)

		logger.info('Building HL7 CDA XML')

		CD = etree.Element('ClinicalDocument',
			{attr_qname: 'urn:hl7-org:v3 CDA.xsd'},
			nsmap=nsmap)

		self.cda_typeId_section(CD)
		self.cda_templateId_section(CD)
		self.cda_id_section(CD)
		self.cda_code_section(CD)
		self.cda_title_section(CD)
		self.cda_effectiveTime_section(CD)
		self.cda_confidentialityCode_section(CD)
		self.cda_languageCode_section(CD)
		# self.cda_setId_section(CD)
		# self.cda_versionNumber_section(CD)
		self.cda_recordTarget_section(CD)
		self.cda_author_section(CD)
		self.cda_custodian_section(CD)
		self.cda_legalAuthenticator_section(CD)
		self.cda_authenticator_section(CD)
		self.cda_inFullfilmentOf_section(CD)
		self.cda_documentationOf_section(CD)
		self.cda_body(CD)

		# Convert lxml CDA document into a string
		# Manually add a xml_declaration
		full_cda_str = "<?xml version='1.0' encoding='UTF-8'?>" + os.linesep

		# Add a stylesheet if defined above in cda_stylesheet
		if config.cda_stylesheet :
			full_cda_str += '<?xml-stylesheet type="text/xsl" href="{}"?>'.format(config.cda_stylesheet) + os.linesep

		# TODO: Consider returning a string with full xml_declaration ???
		#       Currently not working because for "utf-8" it is not possible
		#       full_cda_str = etree.tostring(CD, encoding="utf-8", xml_declaration=True, pretty_print=True)
		# For debugging purposes, one might want to replace each indent with four spaces
		# etree.indent(CD, space="    ")
		full_cda_str += etree.tostring(CD, pretty_print=True, xml_declaration=False, encoding='unicode')
		# Log the full CDA
		logger.debug('Full CDA here:%s%s', os.linesep, full_cda_str)
		
		# CDA file logging
		if config.LOG_CDA_TOFILE:
			if not os.path.exists(config.LOG_DIR_PATH + '/cda') :
				os.makedirs(config.LOG_DIR_PATH + '/cda')
			file_log = config.LOG_DIR_PATH + "/cda/CDA_{}.xml".format(content_id)
			logger.info("Writing CDA document to log file %s", file_log)
			text_file = open(file_log, "wb")
			text_file.write(etree.tostring(CD, pretty_print = True, xml_declaration = False, encoding = 'utf-8'))
			text_file.close()

		return full_cda_str
