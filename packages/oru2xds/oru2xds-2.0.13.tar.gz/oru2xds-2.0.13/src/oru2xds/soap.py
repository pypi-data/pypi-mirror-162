#!/usr/bin/python3
#
# Antonio Martins (digiplan.pt@gmail.com)
#

import os
import logging
import uuid
from lxml import etree
from lxml.builder import ElementMaker
import requests
from urllib3.filepost import encode_multipart_formdata, choose_boundary
from urllib3.fields import RequestField
from requests_toolbelt.multipart import decoder
from io import StringIO, BytesIO

import config


###################################################################


# Logging facility
logger = logging.getLogger(config.APP_NAME + "." + __name__)

# Define namespaces
nsmap = {
	'soapenv': 'http://www.w3.org/2003/05/soap-envelope',
	'wsa': 'http://www.w3.org/2005/08/addressing'}
soapenv_prefix = "{" + nsmap['soapenv'] + "}"
wsa_prefix = "{" + nsmap['wsa'] + "}"


###################################################################
## Class SOAP
###################################################################


class SOAP:
	def __init__(self, soap_message):
		message = None
		uuid = None
		response_message = None

		logger.info("Building SOAP envelope")
		self.generate_UUID()
		if self.uuid is None:
			raise RuntimeError("SOAP message cannot obtain a valid uuid.")
		# Envelope
		self.create_envelope()
		# Header
		self.create_header()
		# Body
		self.create_body(soap_message)
		logger.debug('Full SOAP here:%s%s', os.linesep, repr(self))


	#
	## Generate a UUID for the SOAP
	#
	def generate_UUID(self):
		# Generate a unique message ID
		self.uuid = "urn:uuid:" + str(uuid.uuid1())


	#
	## Builds SOAP envelope
	#
	def create_envelope(self):
		# Envelope
		self.message = etree.Element(soapenv_prefix + "Envelope", nsmap = nsmap)


	#
	## SOAP envelope header
	#
	def create_header(self):
		# Creates the envelope header
		soap_header = etree.Element(soapenv_prefix + "Header", nsmap = nsmap)
		element = etree.SubElement(soap_header, wsa_prefix + "To", nsmap = nsmap)
		element.text = config.SERVICE_URL
		element = etree.SubElement(soap_header, wsa_prefix + "MessageID", nsmap = nsmap)
		element.set(soapenv_prefix + "mustUnderstand", "true")
		element.text = self.uuid
		element = etree.SubElement(soap_header, wsa_prefix + "Action", nsmap = nsmap)
		element.text = "urn:ihe:iti:2007:ProvideAndRegisterDocumentSet-b"
		self.message.append(soap_header)


	#
	## SOAP envelope body
	#
	def create_body(self, soap_message):
		soap_body = etree.Element(soapenv_prefix + "Body")
		soap_body.append(soap_message)
		self.message.append(soap_body)


	#
	## Builds a full SOAP
	#
	def __repr__(self):
		# full_soap_str = "<?xml version='1.0' encoding='UTF-8'?>" + os.linesep
		# full_soap_str = ""
		# etree.indent(self.message, space = "    ")
		# full_soap_str += etree.tostring(self.message, pretty_print = config.PRETTY_PRINT, xml_declaration = False, encoding = 'unicode')
		return etree.tostring(self.message, pretty_print = config.PRETTY_PRINT, xml_declaration = False, encoding = 'unicode')


	# Assembles the HTTP multipart request based on the parts
	#
	## encode_multipart_related
	#
	def encode_multipart_related(self, fields, boundary = None):
		if boundary is None:
			boundary = choose_boundary()
		body, _ = encode_multipart_formdata(fields, boundary)
		content_type = str('multipart/related; boundary="%s"' % boundary)
		return body, content_type


	# Creates the two parts of an HTTP multipart request
	# In our case, part one is the XDS request, part two is the CDA document
	# TODO: Improvice with requestes-toolbelt ?
	# TODO: https://pypi.org/project/requests-toolbelt/
	#
	## encode_media_related
	#
	def encode_media_related(self, part1_id, part1, part2_id, part2):
		rf1 = RequestField(
			name = 'xds_request',
			data = part1,
			headers = {'Content-Type': 'application/xop+xml; charset=UTF-8; type="application/soap+xml"',
					'Content-Transfer-Encoding': 'binary',
					'Content-ID': '<' + part1_id + '>'
			},
		)
		# TODO: Replace Content-type to that of the mimeType of the document being submitted
		rf2 = RequestField(
			name = 'attachment1',
			data = part2,
			headers = {'Content-Type': 'text/xml',
				'Content-Transfer-Encoding': 'binary',
				'Content-ID': '<' + part2_id + '>'
			},
		)
		return self.encode_multipart_related([rf1, rf2])


	#
	## Send SOAP message using MTOM/XOP
	#
	def send_http_multipart(self, attachment_id, attachment_body):
		logger.info("Sending full request to SOAP server")

		# SOAP messages are ALWAYS CRLF
		messageStr = repr(self)
		messageStr = messageStr.replace('\n', '\r\n')
		attachment_body = attachment_body.replace('\n', '\r\n')

		session = requests.Session()
		body, content_type = self.encode_media_related(
			self.uuid,
			messageStr,
			attachment_id,
			attachment_body
		)

		# Insert the HTTP headers
		# MTOM/XOP is based on MIME Multipart encoding 
		headers = {
			'user-agent': config.HTTP_USER_AGENT,
			'Content-Type': content_type + '; type="application/xop+xml"; start="<{}>"; start-info="application/soap+xml"'.format(self.uuid)
			# 'Content-Type': content_type + '; type="application/xop+xml"; start="<{}>"; start-info="application/soap+xml"; action="{}"'.format(self.uuid, soap_action)
		}

		logger.debug("SOAP service URL is: %s", config.SERVICE_URL)
		# Prepare the POST request
		req = requests.Request('POST', config.SERVICE_URL, data=body, headers=headers)
		prepped = req.prepare()

		# SOAP file logging
		if config.LOG_SOAP_ENVELOPE_TOFILE:
			if not os.path.exists(config.LOG_DIR_PATH + '/soap') :
				os.makedirs(config.LOG_DIR_PATH + '/soap')
			file_log = config.LOG_DIR_PATH + "/soap/SOAP_{}.xml".format(self.uuid)
			logger.info("Writing SOAP request to log file %s", file_log)
			text_file = open(file_log, "w")
			log_text = '{}\n{}\r\n{}\r\n\r\n{}'.format(
				'-----------START-----------',
				prepped.method + ' ' + prepped.url,
				'\r\n'.join('{}: {}'.format(k, v) for k, v in prepped.headers.items()),
				prepped.body.decode('utf-8')
			)
			text_file.write(log_text)
			text_file.close()

		try:
			server_response = session.send(prepped)
			# server_response = session.post(config.SERVICE_URL, data = body, headers = headers)
			server_response.raise_for_status()
		except requests.exceptions.HTTPError as errh:
			logger.exception("HTTP Error: {}".format(errh))
			raise RuntimeError("HTTP Error: {}".format(errh))
		except requests.exceptions.ConnectionError as errc:
			logger.exception("Error Connecting: {}".format(errc))
			raise RuntimeError("Error Connecting: {}".format(errc))
		except requests.exceptions.Timeout as errt:
			logger.exception("Timeout Error: {}".format(errt))
			raise RuntimeError("Timeout Error: {}".format(errt))
		except requests.exceptions.RequestException as err:
			logger.exception("Error: {}".format(err))
			raise RuntimeError("Error: {}".format(err))

		if server_response.status_code == requests.codes.ok:
			logger.info("SOAP service called successfully")
		else:
			logger.error("SOAP service FAILED. Return code was: {}{}{}".format(server_response.status_code, os.linesep, server_response.raise_for_status()))
			raise RuntimeError("SOAP service FAILED. Return code was: {}{}{}".format(server_response.status_code, os.linesep, server_response.raise_for_status()))

		# After stripping the content of the HTTP server response, we are left
		# with a SOAP envelope, that we should process as an XML

		if server_response is None:
			raise RuntimeError("Failed to complete the SOAP transaction. No server response.")

		# SOAP response file logging
		if config.LOG_SOAP_RESPONSE_TOFILE:
			if not os.path.exists(config.LOG_DIR_PATH + '/soap') :
				os.makedirs(config.LOG_DIR_PATH + '/soap')
			file_log = config.LOG_DIR_PATH + "/soap/SOAP_RSP_{}.xml".format(self.uuid)
			logger.info("Writing SOAP response to log file %s", file_log)
			text_file = open(file_log, "wb")
			# text_file.write(etree.tostring(self.response_message, pretty_print = True, xml_declaration = False, encoding = 'utf-8'))
			text_file.write(server_response.content)
			text_file.close()

		logger.info("Processing HTTP server response")

		# The server responded with an HTTP server response, which is a MULTIPART one
		multipart_data = decoder.MultipartDecoder.from_response(server_response)
		logger.debug("Downloaded %s bytes in %s parts", len(server_response.text), len(multipart_data.parts))
		if not multipart_data.parts:
			raise RuntimeError("Failed to get parts from the HTTP multipart response")

		if len(multipart_data.parts) > 1:
			raise RuntimeError("Only one HTTPS multipart response is supported")

		# Only 1 PART is allowed
		part = multipart_data.parts[0]
		logger.debug("Part 1 headers --> %s", part.headers)
		# logger.debug(part.content)  # Alternatively, part.text if you want unicode

		if "application/xop+xml" not in part.headers[b'Content-Type'].decode('utf-8'):
			raise RuntimeError("HTTP multipart response type must be application/xop+xml")

		# Convert PART1 to XML tree
		self.response_message = etree.parse(BytesIO(part.content))

		logger.debug('SOAP response here: {}{}'.format(os.linesep,
			etree.tostring(self.response_message, pretty_print = True, xml_declaration = False, encoding = 'unicode'))
		)
		return self.response_message


if __name__ == "__main__":
	# For debugging purposes only.
	# print(etree.tostring(build_soap_envelop(), pretty_print = True, xml_declaration = True, encoding = 'utf-8'))
	pass
