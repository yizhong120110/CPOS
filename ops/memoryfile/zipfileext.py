# -*- coding: utf-8 -*-
#from zipfile import *
from zipfile import ZipFile ,ZIP_DEFLATED
from zipfile import ZIP_FILECOUNT_LIMIT ,ZIP64_LIMIT \
            ,structEndArchive ,stringEndArchive ,structCentralDir ,stringCentralDir \
            ,ZIP_BZIP2 ,ZIP_LZMA ,ZIP64_VERSION ,BZIP2_VERSION ,LZMA_VERSION \
            ,structEndArchive64, stringEndArchive64
from zipfile import struct


class Memory_ZipFile(ZipFile):
    def sj_close(self):
        """Close the file, and for mode "w" and "a" write the ending
        records."""
        if self.fp is None:
            return

        try:
            if self.mode in ("w", "a") and self._didModify: # write ending records
                count = 0
                pos1 = self.fp.tell()
                for zinfo in self.filelist:         # write central directory
                    count = count + 1
                    dt = zinfo.date_time
                    dosdate = (dt[0] - 1980) << 9 | dt[1] << 5 | dt[2]
                    dostime = dt[3] << 11 | dt[4] << 5 | (dt[5] // 2)
                    extra = []
                    if zinfo.file_size > ZIP64_LIMIT \
                       or zinfo.compress_size > ZIP64_LIMIT:
                        extra.append(zinfo.file_size)
                        extra.append(zinfo.compress_size)
                        file_size = 0xffffffff
                        compress_size = 0xffffffff
                    else:
                        file_size = zinfo.file_size
                        compress_size = zinfo.compress_size

                    if zinfo.header_offset > ZIP64_LIMIT:
                        extra.append(zinfo.header_offset)
                        header_offset = 0xffffffff
                    else:
                        header_offset = zinfo.header_offset

                    extra_data = zinfo.extra
                    min_version = 0
                    if extra:
                        # Append a ZIP64 field to the extra's
                        extra_data = struct.pack(
                            '<HH' + 'Q'*len(extra),
                            1, 8*len(extra), *extra) + extra_data

                        min_version = ZIP64_VERSION

                    if zinfo.compress_type == ZIP_BZIP2:
                        min_version = max(BZIP2_VERSION, min_version)
                    elif zinfo.compress_type == ZIP_LZMA:
                        min_version = max(LZMA_VERSION, min_version)

                    extract_version = max(min_version, zinfo.extract_version)
                    create_version = max(min_version, zinfo.create_version)
                    try:
                        filename, flag_bits = zinfo._encodeFilenameFlags()
                        centdir = struct.pack(structCentralDir,
                                              stringCentralDir, create_version,
                                              zinfo.create_system, extract_version, zinfo.reserved,
                                              flag_bits, zinfo.compress_type, dostime, dosdate,
                                              zinfo.CRC, compress_size, file_size,
                                              len(filename), len(extra_data), len(zinfo.comment),
                                              0, zinfo.internal_attr, zinfo.external_attr,
                                              header_offset)
                    except DeprecationWarning:
                        print((structCentralDir, stringCentralDir, create_version,
                               zinfo.create_system, extract_version, zinfo.reserved,
                               zinfo.flag_bits, zinfo.compress_type, dostime, dosdate,
                               zinfo.CRC, compress_size, file_size,
                               len(zinfo.filename), len(extra_data), len(zinfo.comment),
                               0, zinfo.internal_attr, zinfo.external_attr,
                               header_offset), file=sys.stderr)
                        raise
                    self.fp.write(centdir)
                    self.fp.write(filename)
                    self.fp.write(extra_data)
                    self.fp.write(zinfo.comment)

                pos2 = self.fp.tell()
                # Write end-of-zip-archive record
                centDirCount = count
                centDirSize = pos2 - pos1
                centDirOffset = pos1
                if (centDirCount >= ZIP_FILECOUNT_LIMIT or
                    centDirOffset > ZIP64_LIMIT or
                    centDirSize > ZIP64_LIMIT):
                    # Need to write the ZIP64 end-of-archive records
                    zip64endrec = struct.pack(
                        structEndArchive64, stringEndArchive64,
                        44, 45, 45, 0, 0, centDirCount, centDirCount,
                        centDirSize, centDirOffset)
                    self.fp.write(zip64endrec)

                    zip64locrec = struct.pack(
                        structEndArchive64Locator,
                        stringEndArchive64Locator, 0, pos2, 1)
                    self.fp.write(zip64locrec)
                    centDirCount = min(centDirCount, 0xFFFF)
                    centDirSize = min(centDirSize, 0xFFFFFFFF)
                    centDirOffset = min(centDirOffset, 0xFFFFFFFF)

                endrec = struct.pack(structEndArchive, stringEndArchive,
                                     0, 0, centDirCount, centDirCount,
                                     centDirSize, centDirOffset, len(self._comment))
                self.fp.write(endrec)
                self.fp.write(self._comment)
                self.fp.flush()
        finally:
            pass
#            fp = self.fp
#            self.fp = None
#            if not self._filePassed:
#                fp.close()


