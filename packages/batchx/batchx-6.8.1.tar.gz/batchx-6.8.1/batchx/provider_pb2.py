# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: provider.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import common_pb2 as common__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eprovider.proto\x12\x0f\x62\x61tchx.provider\x1a\x0c\x63ommon.proto\")\n\x12ListPayoutsRequest\x12\x13\n\x0b\x65nvironment\x18\x01 \x01(\t\"\x88\x01\n\x06Payout\x12\x16\n\x0ets_period_from\x18\x01 \x01(\x03\x12\x14\n\x0cts_period_to\x18\x02 \x01(\x03\x12\x12\n\nts_deposit\x18\x03 \x01(\x03\x12\x12\n\ntotal_fees\x18\x04 \x01(\x05\x12\x19\n\x11\x62\x61tchx_commission\x18\x05 \x01(\x05\x12\r\n\x05total\x18\x06 \x01(\x05\">\n\x13ListPayoutsResponse\x12\'\n\x06payout\x18\x01 \x03(\x0b\x32\x17.batchx.provider.Payout\"H\n\x11GetMetricsRequest\x12\x13\n\x0b\x65nvironment\x18\x01 \x01(\t\x12\x0f\n\x07ts_from\x18\x02 \x01(\x03\x12\r\n\x05ts_to\x18\x03 \x01(\x03\"\xc5\x03\n\x12GetMetricsResponse\x12\x18\n\x10\x61\x63tive_consumers\x18\x01 \x01(\x05\x12\x11\n\ttool_fees\x18\x02 \x01(\x03\x12\x45\n\x0ctool_metrics\x18\x03 \x01(\x0b\x32/.batchx.provider.GetMetricsResponse.ToolMetrics\x12\x43\n\x0bjob_metrics\x18\x04 \x01(\x0b\x32..batchx.provider.GetMetricsResponse.JobMetrics\x1aS\n\x0bToolMetrics\x12\x0e\n\x06\x61\x63tive\x18\x01 \x01(\x05\x12\x19\n\x11\x63umulative_cloned\x18\x02 \x01(\x05\x12\x19\n\x11\x63umulative_shared\x18\x03 \x01(\x05\x1a\xa0\x01\n\nJobMetrics\x12[\n\x0fstatus_counters\x18\x01 \x03(\x0b\x32\x42.batchx.provider.GetMetricsResponse.JobMetrics.StatusCountersEntry\x1a\x35\n\x13StatusCountersEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\x03:\x02\x38\x01\"\xca\x01\n\x19ListRevenueByToolsRequest\x12\x13\n\x0b\x65nvironment\x18\x01 \x01(\t\x12\x0f\n\x07ts_from\x18\x02 \x01(\x03\x12\r\n\x05ts_to\x18\x03 \x01(\x03\x12I\n\npagination\x18\x04 \x01(\x0b\x32\x35.batchx.provider.ListRevenueByToolsRequest.Pagination\x1a-\n\nPagination\x12\x11\n\tpage_size\x18\x01 \x01(\x05\x12\x0c\n\x04page\x18\x02 \x01(\x05\"\x83\x02\n\x1aListRevenueByToolsResponse\x12\x44\n\x05\x65ntry\x18\x01 \x03(\x0b\x32\x35.batchx.provider.ListRevenueByToolsResponse.ToolEntry\x12\x15\n\rtotal_entries\x18\x02 \x01(\x05\x1a\x87\x01\n\tToolEntry\x12\x11\n\ttool_name\x18\x01 \x01(\t\x12\r\n\x05users\x18\x02 \x01(\x05\x12\x11\n\tsucceeded\x18\x03 \x01(\x03\x12\x0e\n\x06\x66\x61iled\x18\x04 \x01(\x03\x12\r\n\x05total\x18\x05 \x01(\x03\x12\x0c\n\x04\x66\x65\x65s\x18\x06 \x01(\x05\x12\x18\n\x10\x63omputation_cost\x18\x07 \x01(\x05\"\xd0\x01\n\x1cListRevenueByCustomerRequest\x12\x13\n\x0b\x65nvironment\x18\x01 \x01(\t\x12\x0f\n\x07ts_from\x18\x02 \x01(\x03\x12\r\n\x05ts_to\x18\x03 \x01(\x03\x12L\n\npagination\x18\x04 \x01(\x0b\x32\x38.batchx.provider.ListRevenueByCustomerRequest.Pagination\x1a-\n\nPagination\x12\x11\n\tpage_size\x18\x01 \x01(\x05\x12\x0c\n\x04page\x18\x02 \x01(\x05\"\xbd\x04\n\x1dListRevenueByCustomerResponse\x12K\n\x05\x65ntry\x18\x01 \x03(\x0b\x32<.batchx.provider.ListRevenueByCustomerResponse.CustomerEntry\x12O\n\tuser_data\x18\x02 \x03(\x0b\x32<.batchx.provider.ListRevenueByCustomerResponse.UserDataEntry\x12M\n\x08org_data\x18\x03 \x03(\x0b\x32;.batchx.provider.ListRevenueByCustomerResponse.OrgDataEntry\x12\x15\n\rtotal_entries\x18\x04 \x01(\x05\x1a\x84\x01\n\rCustomerEntry\x12\n\n\x02id\x18\x01 \x01(\t\x12\r\n\x05tools\x18\x02 \x01(\x05\x12\x11\n\tsucceeded\x18\x03 \x01(\x03\x12\x0e\n\x06\x66\x61iled\x18\x04 \x01(\x03\x12\r\n\x05total\x18\x05 \x01(\x03\x12\x0c\n\x04\x66\x65\x65s\x18\x06 \x01(\x05\x12\x18\n\x10\x63omputation_cost\x18\x07 \x01(\x05\x1a\x44\n\rUserDataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\"\n\x05value\x18\x02 \x01(\x0b\x32\x13.batchx.common.User:\x02\x38\x01\x1aK\n\x0cOrgDataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12*\n\x05value\x18\x02 \x01(\x0b\x32\x1b.batchx.common.Organization:\x02\x38\x01\x32\xcb\x03\n\x0fProviderService\x12Z\n\nGetMetrics\x12\".batchx.provider.GetMetricsRequest\x1a#.batchx.provider.GetMetricsResponse\"\x03\x90\x02\x01\x12]\n\x0bListPayouts\x12#.batchx.provider.ListPayoutsRequest\x1a$.batchx.provider.ListPayoutsResponse\"\x03\x90\x02\x01\x12r\n\x12ListRevenueByTools\x12*.batchx.provider.ListRevenueByToolsRequest\x1a+.batchx.provider.ListRevenueByToolsResponse\"\x03\x90\x02\x01\x12{\n\x15ListRevenueByCustomer\x12-.batchx.provider.ListRevenueByCustomerRequest\x1a..batchx.provider.ListRevenueByCustomerResponse\"\x03\x90\x02\x01\x1a\x0c\x82\x97\"\x02\x08\n\x82\x97\"\x02\x10\x01\x42 \n\x0fio.batchx.protoB\rProviderProtob\x06proto3')



_LISTPAYOUTSREQUEST = DESCRIPTOR.message_types_by_name['ListPayoutsRequest']
_PAYOUT = DESCRIPTOR.message_types_by_name['Payout']
_LISTPAYOUTSRESPONSE = DESCRIPTOR.message_types_by_name['ListPayoutsResponse']
_GETMETRICSREQUEST = DESCRIPTOR.message_types_by_name['GetMetricsRequest']
_GETMETRICSRESPONSE = DESCRIPTOR.message_types_by_name['GetMetricsResponse']
_GETMETRICSRESPONSE_TOOLMETRICS = _GETMETRICSRESPONSE.nested_types_by_name['ToolMetrics']
_GETMETRICSRESPONSE_JOBMETRICS = _GETMETRICSRESPONSE.nested_types_by_name['JobMetrics']
_GETMETRICSRESPONSE_JOBMETRICS_STATUSCOUNTERSENTRY = _GETMETRICSRESPONSE_JOBMETRICS.nested_types_by_name['StatusCountersEntry']
_LISTREVENUEBYTOOLSREQUEST = DESCRIPTOR.message_types_by_name['ListRevenueByToolsRequest']
_LISTREVENUEBYTOOLSREQUEST_PAGINATION = _LISTREVENUEBYTOOLSREQUEST.nested_types_by_name['Pagination']
_LISTREVENUEBYTOOLSRESPONSE = DESCRIPTOR.message_types_by_name['ListRevenueByToolsResponse']
_LISTREVENUEBYTOOLSRESPONSE_TOOLENTRY = _LISTREVENUEBYTOOLSRESPONSE.nested_types_by_name['ToolEntry']
_LISTREVENUEBYCUSTOMERREQUEST = DESCRIPTOR.message_types_by_name['ListRevenueByCustomerRequest']
_LISTREVENUEBYCUSTOMERREQUEST_PAGINATION = _LISTREVENUEBYCUSTOMERREQUEST.nested_types_by_name['Pagination']
_LISTREVENUEBYCUSTOMERRESPONSE = DESCRIPTOR.message_types_by_name['ListRevenueByCustomerResponse']
_LISTREVENUEBYCUSTOMERRESPONSE_CUSTOMERENTRY = _LISTREVENUEBYCUSTOMERRESPONSE.nested_types_by_name['CustomerEntry']
_LISTREVENUEBYCUSTOMERRESPONSE_USERDATAENTRY = _LISTREVENUEBYCUSTOMERRESPONSE.nested_types_by_name['UserDataEntry']
_LISTREVENUEBYCUSTOMERRESPONSE_ORGDATAENTRY = _LISTREVENUEBYCUSTOMERRESPONSE.nested_types_by_name['OrgDataEntry']
ListPayoutsRequest = _reflection.GeneratedProtocolMessageType('ListPayoutsRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTPAYOUTSREQUEST,
  '__module__' : 'provider_pb2'
  # @@protoc_insertion_point(class_scope:batchx.provider.ListPayoutsRequest)
  })
_sym_db.RegisterMessage(ListPayoutsRequest)

Payout = _reflection.GeneratedProtocolMessageType('Payout', (_message.Message,), {
  'DESCRIPTOR' : _PAYOUT,
  '__module__' : 'provider_pb2'
  # @@protoc_insertion_point(class_scope:batchx.provider.Payout)
  })
_sym_db.RegisterMessage(Payout)

ListPayoutsResponse = _reflection.GeneratedProtocolMessageType('ListPayoutsResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTPAYOUTSRESPONSE,
  '__module__' : 'provider_pb2'
  # @@protoc_insertion_point(class_scope:batchx.provider.ListPayoutsResponse)
  })
_sym_db.RegisterMessage(ListPayoutsResponse)

GetMetricsRequest = _reflection.GeneratedProtocolMessageType('GetMetricsRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETMETRICSREQUEST,
  '__module__' : 'provider_pb2'
  # @@protoc_insertion_point(class_scope:batchx.provider.GetMetricsRequest)
  })
_sym_db.RegisterMessage(GetMetricsRequest)

GetMetricsResponse = _reflection.GeneratedProtocolMessageType('GetMetricsResponse', (_message.Message,), {

  'ToolMetrics' : _reflection.GeneratedProtocolMessageType('ToolMetrics', (_message.Message,), {
    'DESCRIPTOR' : _GETMETRICSRESPONSE_TOOLMETRICS,
    '__module__' : 'provider_pb2'
    # @@protoc_insertion_point(class_scope:batchx.provider.GetMetricsResponse.ToolMetrics)
    })
  ,

  'JobMetrics' : _reflection.GeneratedProtocolMessageType('JobMetrics', (_message.Message,), {

    'StatusCountersEntry' : _reflection.GeneratedProtocolMessageType('StatusCountersEntry', (_message.Message,), {
      'DESCRIPTOR' : _GETMETRICSRESPONSE_JOBMETRICS_STATUSCOUNTERSENTRY,
      '__module__' : 'provider_pb2'
      # @@protoc_insertion_point(class_scope:batchx.provider.GetMetricsResponse.JobMetrics.StatusCountersEntry)
      })
    ,
    'DESCRIPTOR' : _GETMETRICSRESPONSE_JOBMETRICS,
    '__module__' : 'provider_pb2'
    # @@protoc_insertion_point(class_scope:batchx.provider.GetMetricsResponse.JobMetrics)
    })
  ,
  'DESCRIPTOR' : _GETMETRICSRESPONSE,
  '__module__' : 'provider_pb2'
  # @@protoc_insertion_point(class_scope:batchx.provider.GetMetricsResponse)
  })
_sym_db.RegisterMessage(GetMetricsResponse)
_sym_db.RegisterMessage(GetMetricsResponse.ToolMetrics)
_sym_db.RegisterMessage(GetMetricsResponse.JobMetrics)
_sym_db.RegisterMessage(GetMetricsResponse.JobMetrics.StatusCountersEntry)

ListRevenueByToolsRequest = _reflection.GeneratedProtocolMessageType('ListRevenueByToolsRequest', (_message.Message,), {

  'Pagination' : _reflection.GeneratedProtocolMessageType('Pagination', (_message.Message,), {
    'DESCRIPTOR' : _LISTREVENUEBYTOOLSREQUEST_PAGINATION,
    '__module__' : 'provider_pb2'
    # @@protoc_insertion_point(class_scope:batchx.provider.ListRevenueByToolsRequest.Pagination)
    })
  ,
  'DESCRIPTOR' : _LISTREVENUEBYTOOLSREQUEST,
  '__module__' : 'provider_pb2'
  # @@protoc_insertion_point(class_scope:batchx.provider.ListRevenueByToolsRequest)
  })
_sym_db.RegisterMessage(ListRevenueByToolsRequest)
_sym_db.RegisterMessage(ListRevenueByToolsRequest.Pagination)

ListRevenueByToolsResponse = _reflection.GeneratedProtocolMessageType('ListRevenueByToolsResponse', (_message.Message,), {

  'ToolEntry' : _reflection.GeneratedProtocolMessageType('ToolEntry', (_message.Message,), {
    'DESCRIPTOR' : _LISTREVENUEBYTOOLSRESPONSE_TOOLENTRY,
    '__module__' : 'provider_pb2'
    # @@protoc_insertion_point(class_scope:batchx.provider.ListRevenueByToolsResponse.ToolEntry)
    })
  ,
  'DESCRIPTOR' : _LISTREVENUEBYTOOLSRESPONSE,
  '__module__' : 'provider_pb2'
  # @@protoc_insertion_point(class_scope:batchx.provider.ListRevenueByToolsResponse)
  })
_sym_db.RegisterMessage(ListRevenueByToolsResponse)
_sym_db.RegisterMessage(ListRevenueByToolsResponse.ToolEntry)

ListRevenueByCustomerRequest = _reflection.GeneratedProtocolMessageType('ListRevenueByCustomerRequest', (_message.Message,), {

  'Pagination' : _reflection.GeneratedProtocolMessageType('Pagination', (_message.Message,), {
    'DESCRIPTOR' : _LISTREVENUEBYCUSTOMERREQUEST_PAGINATION,
    '__module__' : 'provider_pb2'
    # @@protoc_insertion_point(class_scope:batchx.provider.ListRevenueByCustomerRequest.Pagination)
    })
  ,
  'DESCRIPTOR' : _LISTREVENUEBYCUSTOMERREQUEST,
  '__module__' : 'provider_pb2'
  # @@protoc_insertion_point(class_scope:batchx.provider.ListRevenueByCustomerRequest)
  })
_sym_db.RegisterMessage(ListRevenueByCustomerRequest)
_sym_db.RegisterMessage(ListRevenueByCustomerRequest.Pagination)

ListRevenueByCustomerResponse = _reflection.GeneratedProtocolMessageType('ListRevenueByCustomerResponse', (_message.Message,), {

  'CustomerEntry' : _reflection.GeneratedProtocolMessageType('CustomerEntry', (_message.Message,), {
    'DESCRIPTOR' : _LISTREVENUEBYCUSTOMERRESPONSE_CUSTOMERENTRY,
    '__module__' : 'provider_pb2'
    # @@protoc_insertion_point(class_scope:batchx.provider.ListRevenueByCustomerResponse.CustomerEntry)
    })
  ,

  'UserDataEntry' : _reflection.GeneratedProtocolMessageType('UserDataEntry', (_message.Message,), {
    'DESCRIPTOR' : _LISTREVENUEBYCUSTOMERRESPONSE_USERDATAENTRY,
    '__module__' : 'provider_pb2'
    # @@protoc_insertion_point(class_scope:batchx.provider.ListRevenueByCustomerResponse.UserDataEntry)
    })
  ,

  'OrgDataEntry' : _reflection.GeneratedProtocolMessageType('OrgDataEntry', (_message.Message,), {
    'DESCRIPTOR' : _LISTREVENUEBYCUSTOMERRESPONSE_ORGDATAENTRY,
    '__module__' : 'provider_pb2'
    # @@protoc_insertion_point(class_scope:batchx.provider.ListRevenueByCustomerResponse.OrgDataEntry)
    })
  ,
  'DESCRIPTOR' : _LISTREVENUEBYCUSTOMERRESPONSE,
  '__module__' : 'provider_pb2'
  # @@protoc_insertion_point(class_scope:batchx.provider.ListRevenueByCustomerResponse)
  })
_sym_db.RegisterMessage(ListRevenueByCustomerResponse)
_sym_db.RegisterMessage(ListRevenueByCustomerResponse.CustomerEntry)
_sym_db.RegisterMessage(ListRevenueByCustomerResponse.UserDataEntry)
_sym_db.RegisterMessage(ListRevenueByCustomerResponse.OrgDataEntry)

_PROVIDERSERVICE = DESCRIPTOR.services_by_name['ProviderService']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\017io.batchx.protoB\rProviderProto'
  _GETMETRICSRESPONSE_JOBMETRICS_STATUSCOUNTERSENTRY._options = None
  _GETMETRICSRESPONSE_JOBMETRICS_STATUSCOUNTERSENTRY._serialized_options = b'8\001'
  _LISTREVENUEBYCUSTOMERRESPONSE_USERDATAENTRY._options = None
  _LISTREVENUEBYCUSTOMERRESPONSE_USERDATAENTRY._serialized_options = b'8\001'
  _LISTREVENUEBYCUSTOMERRESPONSE_ORGDATAENTRY._options = None
  _LISTREVENUEBYCUSTOMERRESPONSE_ORGDATAENTRY._serialized_options = b'8\001'
  _PROVIDERSERVICE._options = None
  _PROVIDERSERVICE._serialized_options = b'\202\227\"\002\010\n\202\227\"\002\020\001'
  _PROVIDERSERVICE.methods_by_name['GetMetrics']._options = None
  _PROVIDERSERVICE.methods_by_name['GetMetrics']._serialized_options = b'\220\002\001'
  _PROVIDERSERVICE.methods_by_name['ListPayouts']._options = None
  _PROVIDERSERVICE.methods_by_name['ListPayouts']._serialized_options = b'\220\002\001'
  _PROVIDERSERVICE.methods_by_name['ListRevenueByTools']._options = None
  _PROVIDERSERVICE.methods_by_name['ListRevenueByTools']._serialized_options = b'\220\002\001'
  _PROVIDERSERVICE.methods_by_name['ListRevenueByCustomer']._options = None
  _PROVIDERSERVICE.methods_by_name['ListRevenueByCustomer']._serialized_options = b'\220\002\001'
  _LISTPAYOUTSREQUEST._serialized_start=49
  _LISTPAYOUTSREQUEST._serialized_end=90
  _PAYOUT._serialized_start=93
  _PAYOUT._serialized_end=229
  _LISTPAYOUTSRESPONSE._serialized_start=231
  _LISTPAYOUTSRESPONSE._serialized_end=293
  _GETMETRICSREQUEST._serialized_start=295
  _GETMETRICSREQUEST._serialized_end=367
  _GETMETRICSRESPONSE._serialized_start=370
  _GETMETRICSRESPONSE._serialized_end=823
  _GETMETRICSRESPONSE_TOOLMETRICS._serialized_start=577
  _GETMETRICSRESPONSE_TOOLMETRICS._serialized_end=660
  _GETMETRICSRESPONSE_JOBMETRICS._serialized_start=663
  _GETMETRICSRESPONSE_JOBMETRICS._serialized_end=823
  _GETMETRICSRESPONSE_JOBMETRICS_STATUSCOUNTERSENTRY._serialized_start=770
  _GETMETRICSRESPONSE_JOBMETRICS_STATUSCOUNTERSENTRY._serialized_end=823
  _LISTREVENUEBYTOOLSREQUEST._serialized_start=826
  _LISTREVENUEBYTOOLSREQUEST._serialized_end=1028
  _LISTREVENUEBYTOOLSREQUEST_PAGINATION._serialized_start=983
  _LISTREVENUEBYTOOLSREQUEST_PAGINATION._serialized_end=1028
  _LISTREVENUEBYTOOLSRESPONSE._serialized_start=1031
  _LISTREVENUEBYTOOLSRESPONSE._serialized_end=1290
  _LISTREVENUEBYTOOLSRESPONSE_TOOLENTRY._serialized_start=1155
  _LISTREVENUEBYTOOLSRESPONSE_TOOLENTRY._serialized_end=1290
  _LISTREVENUEBYCUSTOMERREQUEST._serialized_start=1293
  _LISTREVENUEBYCUSTOMERREQUEST._serialized_end=1501
  _LISTREVENUEBYCUSTOMERREQUEST_PAGINATION._serialized_start=983
  _LISTREVENUEBYCUSTOMERREQUEST_PAGINATION._serialized_end=1028
  _LISTREVENUEBYCUSTOMERRESPONSE._serialized_start=1504
  _LISTREVENUEBYCUSTOMERRESPONSE._serialized_end=2077
  _LISTREVENUEBYCUSTOMERRESPONSE_CUSTOMERENTRY._serialized_start=1798
  _LISTREVENUEBYCUSTOMERRESPONSE_CUSTOMERENTRY._serialized_end=1930
  _LISTREVENUEBYCUSTOMERRESPONSE_USERDATAENTRY._serialized_start=1932
  _LISTREVENUEBYCUSTOMERRESPONSE_USERDATAENTRY._serialized_end=2000
  _LISTREVENUEBYCUSTOMERRESPONSE_ORGDATAENTRY._serialized_start=2002
  _LISTREVENUEBYCUSTOMERRESPONSE_ORGDATAENTRY._serialized_end=2077
  _PROVIDERSERVICE._serialized_start=2080
  _PROVIDERSERVICE._serialized_end=2539
# @@protoc_insertion_point(module_scope)
