#!/usr/bin/env python3
#

import sys
import struct
import math
import time
import argparse
import os
import subprocess
import zlib
import gzip

class MKFS:

	def __init__(self, src, dest):
		self._src = src
		self._dest = dest		
		self._fileCount = 0	
		self.data=bytearray()
		self.offset=0

	def output_writeln(self,line):
		self.file_dest.write(line+'\r\n')

	def writeFile(self,path,filename,compress):
		with open(path, "rb") as f:
			
			
			fileBytes = f.read()
			

			if compress:
				gzip_compress = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
				gzip_data = gzip_compress.compress(fileBytes) + gzip_compress.flush()
				fileBytes = gzip_data

			
			fileLen = len(fileBytes)			
			fileBytes = bytearray(fileBytes)
					

			self.output_writeln('\t\t{')
			self.output_writeln('\t\t.size='+str(fileLen)+',')
			self.output_writeln('\t\t.name = "'+filename+'",')
			if compress:
				self.output_writeln('\t\t.gzip=1,')	
			else:
				self.output_writeln('\t\t.gzip=0,')			
			self.output_writeln('\t\t.offset='+str(self.offset))			
			
			#append data
			for b in fileBytes:
				self.data.append(b)
			

			if self._innerCount == self._fileCount-1:
				self.output_writeln('\t\t}')	
			else:
				self.output_writeln('\t\t},')	

			self._innerCount+=1
			self.offset+=fileLen;

					
	def count(self):
		for dirname, dirnames, filenames in os.walk(self._src):
			
			# print path to all filenames.
			for filename in filenames:
				self._fileCount+=1

			if '.bak' in dirnames:
				dirnames.remove('.bak')

			if '.git' in dirnames:
				# don't go into any .git directories.
				dirnames.remove('.git')

	def run(self):
		self.file_dest = open(self._dest,'w')

		self.count()

		self.output_writeln('//Generated by MKFS tool')
		self.output_writeln('//')
		self.output_writeln('#include "rofs.h"')
		self.output_writeln('#include "c_types.h"')

		self.output_writeln('#define ROFS_FILE_COUNT '+str(self._fileCount))
		self.output_writeln('const RO_FS ro_file_system = {')
		self.output_writeln('\t.count='+str(self._fileCount)+',')
		self.output_writeln('\t.files={')		

		self._innerCount=0;
		#make full path
		for dirname, dirnames, filenames in os.walk(self._src):		


			# print path to all filenames.
			for filename in filenames:
				self.writeFile(os.path.join(dirname,filename),filename,1)

			# Advanced usage:
			# editing the 'dirnames' list will stop os.walk() from recursing into there.
			if '.git' in dirnames:
				# don't go into any .git directories.
				dirnames.remove('.git')

			if '.bak' in dirnames:
				dirnames.remove('.bak')

		self.output_writeln('\t}')
		self.output_writeln('};')

		fileHex = ', '.join(hex(x) for x in self.data)	

		self.output_writeln('const ICACHE_STORE_ATTR ICACHE_RODATA_ATTR uint8_t rofs_data[]={'+fileHex+'};')
		#self.output_writeln('static ROFS_FILE_ENTRY ro_file_system_entries[]={'+','.join('file'+str(x) for x in range(0,self._fileCount-1))+'};')
		

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'ROM FS make from dir', prog = 'mkfs')

	parser.add_argument(
	        '--src', '-s',	        
	        help = 'Source directory')

	parser.add_argument(
	       '--dest', '-d',	       
	       help = 'Destination file')

	parser.add_argument(
	       '--gzip', '-z',	       
	       help = 'Destination file',
	       default=1)

	args = parser.parse_args()
	
	mkfs = MKFS(args.src,args.dest)
	mkfs.run()

