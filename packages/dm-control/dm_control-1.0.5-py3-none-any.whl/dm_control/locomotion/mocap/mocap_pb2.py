# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mocap.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bmocap.proto\x12\x1b\x64m_control.locomotion.mocap\"T\n\x06Marker\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06parent\x18\x02 \x01(\t\x12\x14\n\x08position\x18\x03 \x03(\x01\x42\x02\x10\x01\x12\x16\n\nquaternion\x18\x04 \x03(\x01\x42\x02\x10\x01\">\n\x07Markers\x12\x33\n\x06marker\x18\x01 \x03(\x0b\x32#.dm_control.locomotion.mocap.Marker\"O\n\x0eSubtreeScaling\x12\x11\n\tbody_name\x18\x01 \x01(\t\x12\x15\n\rparent_length\x18\x02 \x01(\x01\x12\x13\n\x0bsize_factor\x18\x03 \x01(\x01\"M\n\rWalkerScaling\x12<\n\x07subtree\x18\x01 \x03(\x0b\x32+.dm_control.locomotion.mocap.SubtreeScaling\"\xa2\x03\n\x06Walker\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x38\n\x05model\x18\x02 \x01(\x0e\x32).dm_control.locomotion.mocap.Walker.Model\x12;\n\x07scaling\x18\x03 \x01(\x0b\x32*.dm_control.locomotion.mocap.WalkerScaling\x12\x35\n\x07markers\x18\x04 \x01(\x0b\x32$.dm_control.locomotion.mocap.Markers\x12\x0c\n\x04mass\x18\x05 \x01(\x01\x12\x1a\n\x12\x65nd_effector_names\x18\x06 \x03(\t\x12\x17\n\x0f\x61ppendage_names\x18\x07 \x03(\t\"\x98\x01\n\x05Model\x12\x0f\n\x0bUNSPECIFIED\x10\x00\x12\x0c\n\x08\x43MU_2019\x10\x01\x12\x17\n\x13RESERVED_MODEL_ID_2\x10\x02\x12\x17\n\x13RESERVED_MODEL_ID_3\x10\x03\x12\x0c\n\x08\x43MU_2020\x10\x04\x12\x17\n\x13RESERVED_MODEL_ID_5\x10\x05\x12\x17\n\x13RESERVED_MODEL_ID_6\x10\x06\"\x9b\x01\n\x04Prop\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x36\n\x05shape\x18\x02 \x01(\x0e\x32\'.dm_control.locomotion.mocap.Prop.Shape\x12\x10\n\x04size\x18\x03 \x03(\x01\x42\x02\x10\x01\x12\x0c\n\x04mass\x18\x04 \x01(\x01\"-\n\x05Shape\x12\x0f\n\x0bUNSPECIFIED\x10\x00\x12\n\n\x06SPHERE\x10\x01\x12\x07\n\x03\x42OX\x10\x02\"\xa8\x02\n\nWalkerPose\x12\x14\n\x08position\x18\x01 \x03(\x01\x42\x02\x10\x01\x12\x16\n\nquaternion\x18\x02 \x03(\x01\x42\x02\x10\x01\x12\x12\n\x06joints\x18\x03 \x03(\x01\x42\x02\x10\x01\x12\x1a\n\x0e\x63\x65nter_of_mass\x18\x04 \x03(\x01\x42\x02\x10\x01\x12\x19\n\rend_effectors\x18\x05 \x03(\x01\x42\x02\x10\x01\x12\x14\n\x08velocity\x18\x06 \x03(\x01\x42\x02\x10\x01\x12\x1c\n\x10\x61ngular_velocity\x18\x07 \x03(\x01\x42\x02\x10\x01\x12\x1b\n\x0fjoints_velocity\x18\x08 \x03(\x01\x42\x02\x10\x01\x12\x16\n\nappendages\x18\t \x03(\x01\x42\x02\x10\x01\x12\x1a\n\x0e\x62ody_positions\x18\n \x03(\x01\x42\x02\x10\x01\x12\x1c\n\x10\x62ody_quaternions\x18\x0b \x03(\x01\x42\x02\x10\x01\"l\n\x08PropPose\x12\x14\n\x08position\x18\x01 \x03(\x01\x42\x02\x10\x01\x12\x16\n\nquaternion\x18\x02 \x03(\x01\x42\x02\x10\x01\x12\x14\n\x08velocity\x18\x03 \x03(\x01\x42\x02\x10\x01\x12\x1c\n\x10\x61ngular_velocity\x18\x04 \x03(\x01\x42\x02\x10\x01\"~\n\x0cTimestepData\x12\x38\n\x07walkers\x18\x01 \x03(\x0b\x32\'.dm_control.locomotion.mocap.WalkerPose\x12\x34\n\x05props\x18\x02 \x03(\x0b\x32%.dm_control.locomotion.mocap.PropPose\"\x82\x02\n\x10\x46ittedTrajectory\x12\x12\n\nidentifier\x18\x01 \x01(\t\x12\x0c\n\x04year\x18\x02 \x01(\x05\x12\r\n\x05month\x18\x03 \x01(\x05\x12\x0b\n\x03\x64\x61y\x18\x04 \x01(\x05\x12\n\n\x02\x64t\x18\x05 \x01(\x01\x12\x34\n\x07walkers\x18\x06 \x03(\x0b\x32#.dm_control.locomotion.mocap.Walker\x12\x30\n\x05props\x18\x07 \x03(\x0b\x32!.dm_control.locomotion.mocap.Prop\x12<\n\ttimesteps\x18\x08 \x03(\x0b\x32).dm_control.locomotion.mocap.TimestepDatab\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'mocap_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _MARKER.fields_by_name['position']._options = None
  _MARKER.fields_by_name['position']._serialized_options = b'\020\001'
  _MARKER.fields_by_name['quaternion']._options = None
  _MARKER.fields_by_name['quaternion']._serialized_options = b'\020\001'
  _PROP.fields_by_name['size']._options = None
  _PROP.fields_by_name['size']._serialized_options = b'\020\001'
  _WALKERPOSE.fields_by_name['position']._options = None
  _WALKERPOSE.fields_by_name['position']._serialized_options = b'\020\001'
  _WALKERPOSE.fields_by_name['quaternion']._options = None
  _WALKERPOSE.fields_by_name['quaternion']._serialized_options = b'\020\001'
  _WALKERPOSE.fields_by_name['joints']._options = None
  _WALKERPOSE.fields_by_name['joints']._serialized_options = b'\020\001'
  _WALKERPOSE.fields_by_name['center_of_mass']._options = None
  _WALKERPOSE.fields_by_name['center_of_mass']._serialized_options = b'\020\001'
  _WALKERPOSE.fields_by_name['end_effectors']._options = None
  _WALKERPOSE.fields_by_name['end_effectors']._serialized_options = b'\020\001'
  _WALKERPOSE.fields_by_name['velocity']._options = None
  _WALKERPOSE.fields_by_name['velocity']._serialized_options = b'\020\001'
  _WALKERPOSE.fields_by_name['angular_velocity']._options = None
  _WALKERPOSE.fields_by_name['angular_velocity']._serialized_options = b'\020\001'
  _WALKERPOSE.fields_by_name['joints_velocity']._options = None
  _WALKERPOSE.fields_by_name['joints_velocity']._serialized_options = b'\020\001'
  _WALKERPOSE.fields_by_name['appendages']._options = None
  _WALKERPOSE.fields_by_name['appendages']._serialized_options = b'\020\001'
  _WALKERPOSE.fields_by_name['body_positions']._options = None
  _WALKERPOSE.fields_by_name['body_positions']._serialized_options = b'\020\001'
  _WALKERPOSE.fields_by_name['body_quaternions']._options = None
  _WALKERPOSE.fields_by_name['body_quaternions']._serialized_options = b'\020\001'
  _PROPPOSE.fields_by_name['position']._options = None
  _PROPPOSE.fields_by_name['position']._serialized_options = b'\020\001'
  _PROPPOSE.fields_by_name['quaternion']._options = None
  _PROPPOSE.fields_by_name['quaternion']._serialized_options = b'\020\001'
  _PROPPOSE.fields_by_name['velocity']._options = None
  _PROPPOSE.fields_by_name['velocity']._serialized_options = b'\020\001'
  _PROPPOSE.fields_by_name['angular_velocity']._options = None
  _PROPPOSE.fields_by_name['angular_velocity']._serialized_options = b'\020\001'
  _MARKER._serialized_start=44
  _MARKER._serialized_end=128
  _MARKERS._serialized_start=130
  _MARKERS._serialized_end=192
  _SUBTREESCALING._serialized_start=194
  _SUBTREESCALING._serialized_end=273
  _WALKERSCALING._serialized_start=275
  _WALKERSCALING._serialized_end=352
  _WALKER._serialized_start=355
  _WALKER._serialized_end=773
  _WALKER_MODEL._serialized_start=621
  _WALKER_MODEL._serialized_end=773
  _PROP._serialized_start=776
  _PROP._serialized_end=931
  _PROP_SHAPE._serialized_start=886
  _PROP_SHAPE._serialized_end=931
  _WALKERPOSE._serialized_start=934
  _WALKERPOSE._serialized_end=1230
  _PROPPOSE._serialized_start=1232
  _PROPPOSE._serialized_end=1340
  _TIMESTEPDATA._serialized_start=1342
  _TIMESTEPDATA._serialized_end=1468
  _FITTEDTRAJECTORY._serialized_start=1471
  _FITTEDTRAJECTORY._serialized_end=1729
# @@protoc_insertion_point(module_scope)
