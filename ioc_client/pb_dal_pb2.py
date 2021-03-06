# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pb_dal.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='pb_dal.proto',
  package='com.cybertrap.protobuf.dal',
  syntax='proto3',
  serialized_options=_b('Z/git.vie.cybertrap.com/generated/protobuf-go/dal\270\001\001'),
  serialized_pb=_b('\n\x0cpb_dal.proto\x12\x1a\x63om.cybertrap.protobuf.dal\"\xa2\x01\n\x0c\x45ventMessage\x12<\n\x04type\x18\x01 \x01(\x0e\x32..com.cybertrap.protobuf.dal.EventMessage.Types\x12\r\n\x05\x65vent\x18\x02 \x01(\x0c\"E\n\x05Types\x12\x0b\n\x07PROCESS\x10\x00\x12\n\n\x06THREAD\x10\x01\x12\x0b\n\x07NETWORK\x10\x02\x12\x0c\n\x08REGISTRY\x10\x03\x12\x08\n\x04\x46ILE\x10\x04\"\xb9\x04\n\x0f\x45ventDTOMessage\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x1a\n\x12OBSOLETE_ipAddress\x18\x02 \x01(\t\x12\x0e\n\x06unitId\x18\x03 \x01(\x04\x12\x0b\n\x03pid\x18\x04 \x01(\x04\x12\x13\n\x0bprocessPath\x18\x05 \x01(\t\x12\x0c\n\x04time\x18\x06 \x01(\x04\x12\x15\n\risBlacklisted\x18\x07 \x01(\x08\x12\x10\n\x08parentId\x18\x08 \x01(\x04\x12\x17\n\x0fiocIdentifiedBy\x18\t \x01(\t\x12\x12\n\niocComment\x18\n \x01(\t\x12\x1d\n\x15iocAppliedRuleComment\x18\x0b \x01(\t\x12\x14\n\x0ciocIsCleared\x18\x0c \x01(\x08\x12\x14\n\x0ciocClearedAt\x18\r \x01(\x04\x12\x1c\n\x14iocClearedByUsername\x18\x0e \x01(\t\x12\x13\n\x0bisTruncated\x18\x0f \x01(\x08\x12\x12\n\nsequenceId\x18\x10 \x01(\x04\x12\x10\n\x08hostname\x18\x11 \x01(\t\x12\x1c\n\x14OBSOLETE_eventTypeId\x18\x12 \x01(\r\x12L\n\tiocStatus\x18\x13 \x01(\x0e\x32\x39.com.cybertrap.protobuf.dal.EventDTOMessage.IOCStatusEnum\x12\x1a\n\x12iocIsFalsePositive\x18\x14 \x01(\x08\"<\n\rIOCStatusEnum\x12\n\n\x06NO_IOC\x10\x00\x12\x0e\n\nACTIVE_IOC\x10\x01\x12\x0f\n\x0b\x43LEARED_IOC\x10\x02\"\xc6\x01\n\x16ProcessEventDTOMessage\x12\x44\n\x0f\x65ventDTOMessage\x18\x01 \x01(\x0b\x32+.com.cybertrap.protobuf.dal.EventDTOMessage\x12\x11\n\tparentPid\x18\x02 \x01(\x04\x12\x12\n\ndomainName\x18\x03 \x01(\t\x12\x10\n\x08userName\x18\x04 \x01(\t\x12\x13\n\x0b\x63ommandLine\x18\x05 \x01(\t\x12\x18\n\x10workingDirectory\x18\x06 \x01(\t\"\x9d\x01\n\x15ThreadEventDTOMessage\x12\x44\n\x0f\x65ventDTOMessage\x18\x01 \x01(\x0b\x32+.com.cybertrap.protobuf.dal.EventDTOMessage\x12\x11\n\ttargetPid\x18\x02 \x01(\x04\x12\x10\n\x08threadId\x18\x03 \x01(\x04\x12\x19\n\x11targetProcessName\x18\x04 \x01(\t\"\xc6\x02\n\x17RegistryEventDTOMessage\x12\x44\n\x0f\x65ventDTOMessage\x18\x01 \x01(\x0b\x32+.com.cybertrap.protobuf.dal.EventDTOMessage\x12\x11\n\toperation\x18\x02 \x01(\t\x12\x0c\n\x04path\x18\x03 \x01(\t\x12\x0b\n\x03key\x18\x04 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x05 \x01(\x0c\x12G\n\x04type\x18\x06 \x01(\x0e\x32\x39.com.cybertrap.protobuf.dal.RegistryEventDTOMessage.Types\"`\n\x05Types\x12\t\n\x05OTHER\x10\x00\x12\x0c\n\x08\x44WORD_LE\x10\x01\x12\x0c\n\x08\x44WORD_BE\x10\x02\x12\x12\n\x0eUNICODE_STRING\x10\x03\x12\x10\n\x0cMULTI_STRING\x10\x04\x12\n\n\x06\x42INARY\x10\x05\"\x8c\x02\n\x16NetworkEventDTOMessage\x12\x44\n\x0f\x65ventDTOMessage\x18\x01 \x01(\x0b\x32+.com.cybertrap.protobuf.dal.EventDTOMessage\x12\x16\n\x0elocalIpAddress\x18\x02 \x01(\t\x12\x11\n\tlocalPort\x18\x03 \x01(\r\x12\x17\n\x0fremoteIpAddress\x18\x04 \x01(\t\x12\x12\n\nremotePort\x18\x05 \x01(\r\x12\x1c\n\x14isConnectionOutgoing\x18\x06 \x01(\x08\x12\x10\n\x08\x65vilness\x18\x07 \x01(\r\x12\x12\n\nprotocolID\x18\x08 \x01(\x04\x12\x10\n\x08protocol\x18\t \x01(\t\"\xe9\x01\n\x13\x46ileEventDTOMessage\x12\x44\n\x0f\x65ventDTOMessage\x18\x01 \x01(\x0b\x32+.com.cybertrap.protobuf.dal.EventDTOMessage\x12\x0c\n\x04type\x18\x02 \x01(\t\x12\x16\n\x0esourceFileName\x18\x03 \x01(\t\x12\x1b\n\x13\x64\x65stinationFileName\x18\x04 \x01(\t\x12\x12\n\ndomainName\x18\x05 \x01(\t\x12\x10\n\x08userName\x18\x06 \x01(\t\x12\x11\n\tshareName\x18\x07 \x01(\t\x12\x10\n\x08\x63lientIP\x18\x08 \x01(\tB4Z/git.vie.cybertrap.com/generated/protobuf-go/dal\xb8\x01\x01\x62\x06proto3')
)



_EVENTMESSAGE_TYPES = _descriptor.EnumDescriptor(
  name='Types',
  full_name='com.cybertrap.protobuf.dal.EventMessage.Types',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PROCESS', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='THREAD', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NETWORK', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='REGISTRY', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FILE', index=4, number=4,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=138,
  serialized_end=207,
)
_sym_db.RegisterEnumDescriptor(_EVENTMESSAGE_TYPES)

_EVENTDTOMESSAGE_IOCSTATUSENUM = _descriptor.EnumDescriptor(
  name='IOCStatusEnum',
  full_name='com.cybertrap.protobuf.dal.EventDTOMessage.IOCStatusEnum',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NO_IOC', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ACTIVE_IOC', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CLEARED_IOC', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=719,
  serialized_end=779,
)
_sym_db.RegisterEnumDescriptor(_EVENTDTOMESSAGE_IOCSTATUSENUM)

_REGISTRYEVENTDTOMESSAGE_TYPES = _descriptor.EnumDescriptor(
  name='Types',
  full_name='com.cybertrap.protobuf.dal.RegistryEventDTOMessage.Types',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='OTHER', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DWORD_LE', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DWORD_BE', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='UNICODE_STRING', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MULTI_STRING', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BINARY', index=5, number=5,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1373,
  serialized_end=1469,
)
_sym_db.RegisterEnumDescriptor(_REGISTRYEVENTDTOMESSAGE_TYPES)


_EVENTMESSAGE = _descriptor.Descriptor(
  name='EventMessage',
  full_name='com.cybertrap.protobuf.dal.EventMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='com.cybertrap.protobuf.dal.EventMessage.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='event', full_name='com.cybertrap.protobuf.dal.EventMessage.event', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _EVENTMESSAGE_TYPES,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=45,
  serialized_end=207,
)


_EVENTDTOMESSAGE = _descriptor.Descriptor(
  name='EventDTOMessage',
  full_name='com.cybertrap.protobuf.dal.EventDTOMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.id', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='OBSOLETE_ipAddress', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.OBSOLETE_ipAddress', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='unitId', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.unitId', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pid', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.pid', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='processPath', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.processPath', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='time', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.time', index=5,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='isBlacklisted', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.isBlacklisted', index=6,
      number=7, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='parentId', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.parentId', index=7,
      number=8, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='iocIdentifiedBy', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.iocIdentifiedBy', index=8,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='iocComment', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.iocComment', index=9,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='iocAppliedRuleComment', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.iocAppliedRuleComment', index=10,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='iocIsCleared', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.iocIsCleared', index=11,
      number=12, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='iocClearedAt', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.iocClearedAt', index=12,
      number=13, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='iocClearedByUsername', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.iocClearedByUsername', index=13,
      number=14, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='isTruncated', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.isTruncated', index=14,
      number=15, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sequenceId', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.sequenceId', index=15,
      number=16, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='hostname', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.hostname', index=16,
      number=17, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='OBSOLETE_eventTypeId', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.OBSOLETE_eventTypeId', index=17,
      number=18, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='iocStatus', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.iocStatus', index=18,
      number=19, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='iocIsFalsePositive', full_name='com.cybertrap.protobuf.dal.EventDTOMessage.iocIsFalsePositive', index=19,
      number=20, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _EVENTDTOMESSAGE_IOCSTATUSENUM,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=210,
  serialized_end=779,
)


_PROCESSEVENTDTOMESSAGE = _descriptor.Descriptor(
  name='ProcessEventDTOMessage',
  full_name='com.cybertrap.protobuf.dal.ProcessEventDTOMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='eventDTOMessage', full_name='com.cybertrap.protobuf.dal.ProcessEventDTOMessage.eventDTOMessage', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='parentPid', full_name='com.cybertrap.protobuf.dal.ProcessEventDTOMessage.parentPid', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='domainName', full_name='com.cybertrap.protobuf.dal.ProcessEventDTOMessage.domainName', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='userName', full_name='com.cybertrap.protobuf.dal.ProcessEventDTOMessage.userName', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='commandLine', full_name='com.cybertrap.protobuf.dal.ProcessEventDTOMessage.commandLine', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='workingDirectory', full_name='com.cybertrap.protobuf.dal.ProcessEventDTOMessage.workingDirectory', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=782,
  serialized_end=980,
)


_THREADEVENTDTOMESSAGE = _descriptor.Descriptor(
  name='ThreadEventDTOMessage',
  full_name='com.cybertrap.protobuf.dal.ThreadEventDTOMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='eventDTOMessage', full_name='com.cybertrap.protobuf.dal.ThreadEventDTOMessage.eventDTOMessage', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='targetPid', full_name='com.cybertrap.protobuf.dal.ThreadEventDTOMessage.targetPid', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='threadId', full_name='com.cybertrap.protobuf.dal.ThreadEventDTOMessage.threadId', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='targetProcessName', full_name='com.cybertrap.protobuf.dal.ThreadEventDTOMessage.targetProcessName', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=983,
  serialized_end=1140,
)


_REGISTRYEVENTDTOMESSAGE = _descriptor.Descriptor(
  name='RegistryEventDTOMessage',
  full_name='com.cybertrap.protobuf.dal.RegistryEventDTOMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='eventDTOMessage', full_name='com.cybertrap.protobuf.dal.RegistryEventDTOMessage.eventDTOMessage', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='operation', full_name='com.cybertrap.protobuf.dal.RegistryEventDTOMessage.operation', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='path', full_name='com.cybertrap.protobuf.dal.RegistryEventDTOMessage.path', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='key', full_name='com.cybertrap.protobuf.dal.RegistryEventDTOMessage.key', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data', full_name='com.cybertrap.protobuf.dal.RegistryEventDTOMessage.data', index=4,
      number=5, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='type', full_name='com.cybertrap.protobuf.dal.RegistryEventDTOMessage.type', index=5,
      number=6, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _REGISTRYEVENTDTOMESSAGE_TYPES,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1143,
  serialized_end=1469,
)


_NETWORKEVENTDTOMESSAGE = _descriptor.Descriptor(
  name='NetworkEventDTOMessage',
  full_name='com.cybertrap.protobuf.dal.NetworkEventDTOMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='eventDTOMessage', full_name='com.cybertrap.protobuf.dal.NetworkEventDTOMessage.eventDTOMessage', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='localIpAddress', full_name='com.cybertrap.protobuf.dal.NetworkEventDTOMessage.localIpAddress', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='localPort', full_name='com.cybertrap.protobuf.dal.NetworkEventDTOMessage.localPort', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='remoteIpAddress', full_name='com.cybertrap.protobuf.dal.NetworkEventDTOMessage.remoteIpAddress', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='remotePort', full_name='com.cybertrap.protobuf.dal.NetworkEventDTOMessage.remotePort', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='isConnectionOutgoing', full_name='com.cybertrap.protobuf.dal.NetworkEventDTOMessage.isConnectionOutgoing', index=5,
      number=6, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='evilness', full_name='com.cybertrap.protobuf.dal.NetworkEventDTOMessage.evilness', index=6,
      number=7, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='protocolID', full_name='com.cybertrap.protobuf.dal.NetworkEventDTOMessage.protocolID', index=7,
      number=8, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='protocol', full_name='com.cybertrap.protobuf.dal.NetworkEventDTOMessage.protocol', index=8,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1472,
  serialized_end=1740,
)


_FILEEVENTDTOMESSAGE = _descriptor.Descriptor(
  name='FileEventDTOMessage',
  full_name='com.cybertrap.protobuf.dal.FileEventDTOMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='eventDTOMessage', full_name='com.cybertrap.protobuf.dal.FileEventDTOMessage.eventDTOMessage', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='type', full_name='com.cybertrap.protobuf.dal.FileEventDTOMessage.type', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sourceFileName', full_name='com.cybertrap.protobuf.dal.FileEventDTOMessage.sourceFileName', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='destinationFileName', full_name='com.cybertrap.protobuf.dal.FileEventDTOMessage.destinationFileName', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='domainName', full_name='com.cybertrap.protobuf.dal.FileEventDTOMessage.domainName', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='userName', full_name='com.cybertrap.protobuf.dal.FileEventDTOMessage.userName', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='shareName', full_name='com.cybertrap.protobuf.dal.FileEventDTOMessage.shareName', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='clientIP', full_name='com.cybertrap.protobuf.dal.FileEventDTOMessage.clientIP', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1743,
  serialized_end=1976,
)

_EVENTMESSAGE.fields_by_name['type'].enum_type = _EVENTMESSAGE_TYPES
_EVENTMESSAGE_TYPES.containing_type = _EVENTMESSAGE
_EVENTDTOMESSAGE.fields_by_name['iocStatus'].enum_type = _EVENTDTOMESSAGE_IOCSTATUSENUM
_EVENTDTOMESSAGE_IOCSTATUSENUM.containing_type = _EVENTDTOMESSAGE
_PROCESSEVENTDTOMESSAGE.fields_by_name['eventDTOMessage'].message_type = _EVENTDTOMESSAGE
_THREADEVENTDTOMESSAGE.fields_by_name['eventDTOMessage'].message_type = _EVENTDTOMESSAGE
_REGISTRYEVENTDTOMESSAGE.fields_by_name['eventDTOMessage'].message_type = _EVENTDTOMESSAGE
_REGISTRYEVENTDTOMESSAGE.fields_by_name['type'].enum_type = _REGISTRYEVENTDTOMESSAGE_TYPES
_REGISTRYEVENTDTOMESSAGE_TYPES.containing_type = _REGISTRYEVENTDTOMESSAGE
_NETWORKEVENTDTOMESSAGE.fields_by_name['eventDTOMessage'].message_type = _EVENTDTOMESSAGE
_FILEEVENTDTOMESSAGE.fields_by_name['eventDTOMessage'].message_type = _EVENTDTOMESSAGE
DESCRIPTOR.message_types_by_name['EventMessage'] = _EVENTMESSAGE
DESCRIPTOR.message_types_by_name['EventDTOMessage'] = _EVENTDTOMESSAGE
DESCRIPTOR.message_types_by_name['ProcessEventDTOMessage'] = _PROCESSEVENTDTOMESSAGE
DESCRIPTOR.message_types_by_name['ThreadEventDTOMessage'] = _THREADEVENTDTOMESSAGE
DESCRIPTOR.message_types_by_name['RegistryEventDTOMessage'] = _REGISTRYEVENTDTOMESSAGE
DESCRIPTOR.message_types_by_name['NetworkEventDTOMessage'] = _NETWORKEVENTDTOMESSAGE
DESCRIPTOR.message_types_by_name['FileEventDTOMessage'] = _FILEEVENTDTOMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

EventMessage = _reflection.GeneratedProtocolMessageType('EventMessage', (_message.Message,), dict(
  DESCRIPTOR = _EVENTMESSAGE,
  __module__ = 'pb_dal_pb2'
  # @@protoc_insertion_point(class_scope:com.cybertrap.protobuf.dal.EventMessage)
  ))
_sym_db.RegisterMessage(EventMessage)

EventDTOMessage = _reflection.GeneratedProtocolMessageType('EventDTOMessage', (_message.Message,), dict(
  DESCRIPTOR = _EVENTDTOMESSAGE,
  __module__ = 'pb_dal_pb2'
  # @@protoc_insertion_point(class_scope:com.cybertrap.protobuf.dal.EventDTOMessage)
  ))
_sym_db.RegisterMessage(EventDTOMessage)

ProcessEventDTOMessage = _reflection.GeneratedProtocolMessageType('ProcessEventDTOMessage', (_message.Message,), dict(
  DESCRIPTOR = _PROCESSEVENTDTOMESSAGE,
  __module__ = 'pb_dal_pb2'
  # @@protoc_insertion_point(class_scope:com.cybertrap.protobuf.dal.ProcessEventDTOMessage)
  ))
_sym_db.RegisterMessage(ProcessEventDTOMessage)

ThreadEventDTOMessage = _reflection.GeneratedProtocolMessageType('ThreadEventDTOMessage', (_message.Message,), dict(
  DESCRIPTOR = _THREADEVENTDTOMESSAGE,
  __module__ = 'pb_dal_pb2'
  # @@protoc_insertion_point(class_scope:com.cybertrap.protobuf.dal.ThreadEventDTOMessage)
  ))
_sym_db.RegisterMessage(ThreadEventDTOMessage)

RegistryEventDTOMessage = _reflection.GeneratedProtocolMessageType('RegistryEventDTOMessage', (_message.Message,), dict(
  DESCRIPTOR = _REGISTRYEVENTDTOMESSAGE,
  __module__ = 'pb_dal_pb2'
  # @@protoc_insertion_point(class_scope:com.cybertrap.protobuf.dal.RegistryEventDTOMessage)
  ))
_sym_db.RegisterMessage(RegistryEventDTOMessage)

NetworkEventDTOMessage = _reflection.GeneratedProtocolMessageType('NetworkEventDTOMessage', (_message.Message,), dict(
  DESCRIPTOR = _NETWORKEVENTDTOMESSAGE,
  __module__ = 'pb_dal_pb2'
  # @@protoc_insertion_point(class_scope:com.cybertrap.protobuf.dal.NetworkEventDTOMessage)
  ))
_sym_db.RegisterMessage(NetworkEventDTOMessage)

FileEventDTOMessage = _reflection.GeneratedProtocolMessageType('FileEventDTOMessage', (_message.Message,), dict(
  DESCRIPTOR = _FILEEVENTDTOMESSAGE,
  __module__ = 'pb_dal_pb2'
  # @@protoc_insertion_point(class_scope:com.cybertrap.protobuf.dal.FileEventDTOMessage)
  ))
_sym_db.RegisterMessage(FileEventDTOMessage)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
