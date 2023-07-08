import io
import shutil
import os
from os import listdir
from os.path import isfile, join, dirname, splitext
from ctypes import *

def tohex(val, nbits):
  return hex((val + (1 << nbits)) % (1 << nbits))

string_hash_dictionary = {}
try:
    with io.open("string_hash_dictionary.txt", mode="r") as dictionary_file:
        for i, line in enumerate(dictionary_file):
            if i > 1:
                arr = line.split()
                h = int(arr[0], 16)
                string_hash_dictionary[h] = arr[1]
        
except IOError:
    input("Could not open file!")

assert(len(string_hash_dictionary) != 0)

fileList = [ 
    f for f in listdir(dirname(__file__)) if isfile(join(dirname(__file__), f))
]

class resource_versions(Structure):
    _fields_ = [("field_0", c_int),
                ("field_4", c_int),
                ("field_8", c_int),
                ("field_C", c_int),
                ("field_10", c_int)]
                
class resource_amalgapak_header(Structure):
    _fields_ = [("field_0", resource_versions),
                ("field_14", c_int),
                ("field_18", c_int),
                ("header_size", c_int),
                ("location_table_size", c_int),
                ("field_24", c_int),
                ("memory_map_table_size", c_int),
                ("field_2C", c_int),
                ("prerequisite_table_size", c_int),
                ("field_34", c_int)]

assert(sizeof(resource_versions) == 0x14)

assert(sizeof(resource_amalgapak_header) == 0x38)

class string_hash(Structure):
    _fields_ = [("field_0", c_int)]

class resource_key(Structure):
    _fields_ = [("m_hash", string_hash),
                ("m_type", c_int)
                ]

class resource_pack_header(Structure):
    _fields_ = [("field_0", resource_versions),
                ("field_14", c_int),
                ("directory_offset", c_int),
                ("res_dir_mash_size", c_int),
                ("field_20", c_int),
                ("field_24", c_int),
                ("field_28", c_int)
                ]
assert(sizeof(resource_pack_header) == 0x2C)

class resource_location(Structure):
    _fields_ = [("field_0", resource_key),
                ("m_offset", c_int),
                ("m_size", c_int)
                ]



DEV_MODE = 1

#Header_Section 0x38

def extract_pak(rPack):

    class resource_pack_location(Structure):
        _fields_ = [("loc", resource_location),
                    ("field_10", c_int),
                    ("field_14", c_int),
                    ("field_18", c_int),
                    ("field_1C", c_int),
                    ("prerequisite_offset", c_int),
                    ("prerequisite_count", c_int),
                    ("field_28", c_int),
                    ("field_2C", c_int),
                    ("m_name", c_char * 32)
                    ]
                    
    assert(sizeof(resource_pack_location) == 0x50)
    
    amalgapak_pack_location_table_t = resource_pack_location * int(location_table_size / sizeof(resource_pack_location))
    amalgapak_pack_location_table = amalgapak_pack_location_table_t()
    rPack.readinto(amalgapak_pack_location_table)
    
    amalgapak_pack_location_count = len(amalgapak_pack_location_table)
    print(amalgapak_pack_location_count, "Files detected")

    folder = name_pak
    try:
        os.mkdir(folder)
    except OSError:
        print ("Creation of the directory %s failed" % folder)
    else:
        print ("Successfully created the directory %s " % folder)
        
    for fileIndex in range(amalgapak_pack_location_count):
        pack_loc = amalgapak_pack_location_table[fileIndex]
        ndisplay = pack_loc.m_name.decode('utf-8')
        print(ndisplay)
        offset_loc = pack_loc.loc.m_offset
        filesize = pack_loc.loc.m_size
        
        filepath = os.path.join(folder, ndisplay + ".XBPACK")
        filepath = ''.join(x for x in filepath if x.isprintable())
        
        rPack.seek(base_offset + offset_loc, 0)
        
        filePos = rPack.tell()
        print(filepath, hex(filePos))
        
        nfldata = rPack.read(filesize)
        nflfile = open(filepath, mode="wb")
        nflfile.write(nfldata)
        nflfile.close()

def extract_pak_preview(rPack):

    class resource_pack_location(Structure):
        _fields_ = [("loc", resource_location),
                    ("field_10", c_int),
                    ("field_14", c_int),
                    ("field_18", c_int),
                    ("field_1C", c_int),
                    ("prerequisite_offset", c_int),
                    ("prerequisite_count", c_int),
                    ]
                    
    assert(sizeof(resource_pack_location) == 0x28)
    
    amalgapak_pack_location_table_t = resource_pack_location * int(location_table_size / sizeof(resource_pack_location))
    amalgapak_pack_location_table = amalgapak_pack_location_table_t()
    rPack.readinto(amalgapak_pack_location_table)
    
    amalgapak_pack_location_count = len(amalgapak_pack_location_table)
    print(amalgapak_pack_location_count, "Files detected")

    folder = name_pak
    try:
        os.mkdir(folder)
    except OSError:
        print ("Creation of the directory %s failed" % folder)
    else:
        print ("Successfully created the directory %s " % folder)
        
    for fileIndex in range(amalgapak_pack_location_count):
        pack_loc = amalgapak_pack_location_table[fileIndex]
        
        key = pack_loc.loc.field_0
        h = int(tohex(key.m_hash.field_0, 32), 16)
        name = string_hash_dictionary.get(h, tohex(key.m_hash.field_0, 32))
        
        ndisplay = name
        print(ndisplay)
        offset_loc = pack_loc.loc.m_offset
        filesize = pack_loc.loc.m_size
        
        filepath = os.path.join(folder, ndisplay + ".XBPACK")
        filepath = ''.join(x for x in filepath if x.isprintable())
        
        rPack.seek(base_offset + offset_loc, 0)
        
        filePos = rPack.tell()
        print(filepath, hex(filePos))
        
        nfldata = rPack.read(filesize)
        nflfile = open(filepath, mode="wb")
        nflfile.write(nfldata)
        nflfile.close()


for file in fileList:
    name_pak, ext = splitext(file)
    if ext == ".PAK":
        print("Resource pack:", file)
        with io.open(file, mode="rb") as rPack:

            rPack.seek(0, 2)
            numOfBytes = rPack.tell()
            print("Total Size:", numOfBytes, "bytes")
            
            rPack.seek(0, 0)
            pack_file_header = resource_amalgapak_header()
            rPack.readinto(pack_file_header)
            
            rpVersion = pack_file_header.field_0.field_0
            
            #Header Section Size
            headerSize = pack_file_header.header_size
            
            #LBA_SECTION
            location_table_size = pack_file_header.location_table_size

            base_offset = pack_file_header.field_18

            if DEV_MODE == 1:
                print("\nDeveloper info:\n")
                
                versions = pack_file_header.field_0
                print("RESOURCE_PACK_VERSION 0x%08x" % versions.field_0)
                print("RESOURCE_ENTITY_MASH_VERSION 0x%08x" % versions.field_4)
                print("RESOURCE_NOENTITY_MASH_VERSION 0x%08x" % versions.field_8)
                print("RESOURCE_AUTO_MASH_VERSION 0x%08x" % versions.field_C)
                print("RESOURCE_RAW_MASH_VERSION 0x%08x" % versions.field_10)
                
                print("base_offset:", hex(base_offset))
                
                print("Header Section Size:", hex(headerSize), "bytes")
                print("LBA Section Size:", hex(location_table_size), "bytes")

            if rpVersion == 14:
                print("Game: Ultimate Spider-Man NTSC 1.0")
                extract_pak(rPack)
            elif rpVersion == 10:
                print("Game: Ultimate Spider-Man NTSC 06/20/2005 Prototype")
                extract_pak_preview(rPack)
                

print("\nDone.")
