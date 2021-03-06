#!/usr/bin/env python2

'''
Convert BED format to gff3
reference for gff3: https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md
'''
import os
import tempfile
from collections import OrderedDict

from util import subtools 
from DataConversion import DataConversion

class BedConversion(DataConversion):
    def __init__(self, inputBedFile, outputFile, chromSizesFile, bedType, trackType, options=None):
       super(BedConversion, self).__init__(inputBedFile, outputFile, chromSizesFile, bedType, options)
        
    
    def convertFormats(self):
        self.dataToJson()

    
    def dataToJson(self):
        if self.dataType != 'bed':
            self.convertToGff3()
            self.inputFile = self.gff3_file
            self.dataType == 'gff'
        subtools.flatfile_to_json(self.inputFile, self.dataType, self.trackType, self.trackLabel, self.outputFile, self.options)
        
    def convertToGff3(self):
        self.gff3_file = tempfile.NamedTemporaryFile(suffix=".gff3")
        if self.dataType == "trfbig":
            self.trfbig_to_gff3()
        elif self.dataType == "regtools":
            self.splicejunctions_to_gff3()
        elif self.dataType == "blat":
            self.bigpsl_to_gff3()
        else:
            raise ValueError("dataType %s is not support for converting to GFF3", self.dataType)

    def trfbig_to_gff3(self):
        gff3 = open(self.gff3_file.name, 'w')
        gff3.write("##gff-version 3\n")
        sizes_dict = subtools.sequence_region(self.chromSizesFile)
        seq_regions = dict()
        with open(self.inputFile, 'r') as bed:
            for line in bed:
                field = OrderedDict()
                attribute = OrderedDict()
                li = line.rstrip().split("\t")
                field['seqid'] = li[0]
                if field['seqid'] not in seq_regions:
                    end_region = sizes_dict[field['seqid']]
                    gff3.write("##sequence-region " + field['seqid'] + ' 1 ' + str(end_region) + '\n')
                    seq_regions[field['seqid']] = end_region
                field['source'] = li[3]
                field['type'] = 'tandem_repeat'
                # The first base in a chromosome is numbered 0 in BED format
                field['start'] = str(int(li[1]) + 1)
                field['end'] = li[2]
                field['score'] = li[9]
                field['strand'] = '+'
                field['phase'] = '.'
                attribute['length of repeat unit'] = li[4]
                attribute['mean number of copies of repeat'] = li[5]
                attribute['length of consensus sequence'] = li[6]
                attribute['percentage match'] = li[7]
                attribute['percentage indel'] = li[8]
                attribute['percent of a\'s in repeat unit'] = li[10]
                attribute['percent of c\'s in repeat unit'] = li[11]
                attribute['percent of g\'s in repeat unit'] = li[12]
                attribute['percent of t\'s in repeat unit'] = li[13]
                attribute['entropy'] = li[14]
                attribute['sequence of repeat unit element'] = li[15]
                subtools.write_features(field, attribute, gff3)
        gff3.close()


    def splicejunctions_to_gff3(self):
        gff3 = open(self.gff3_file.name, 'w')
        gff3.write("##gff-version 3\n")
        sizes_dict = subtools.sequence_region(self.chromSizesFile)
        seq_regions = dict()
        with open(self.inputFile, 'r') as bed:
            for line in bed:
                field = OrderedDict()
                attribute = OrderedDict()
                li = line.rstrip().split("\t")
                field['seqid'] = li[0]
                if field['seqid'] not in seq_regions:
                    end_region = sizes_dict[field['seqid']]
                    gff3.write("##sequence-region " + field['seqid'] + ' 1 ' + str(end_region) + '\n')
                    seq_regions[field['seqid']] = end_region
                field['source'] = li[3]
                field['type'] = 'junction'
                # The first base in a chromosome is numbered 0 in BED format
                field['start'] = int(li[1]) + 1
                field['end'] = li[2]
                field['score'] = li[12]
                field['strand'] = li[5]
                field['phase'] = '.'
                attribute['ID'] = li[0] + '_' + li[3]
                attribute['Name'] = li[3]
                attribute['blockcount'] = li[9]
                attribute['blocksizes'] = li[10]
                attribute['chromstarts'] = li[11]
                subtools.write_features(field, attribute, gff3)
                subtools.child_blocks(field, attribute, gff3, 'exon_junction')
        gff3.close()

    def bigpsl_to_gff3(self):
        gff3 = open(self.gff3_file.name, 'w')
        gff3.write("##gff-version 3\n")
        sizes_dict = subtools.sequence_region(self.chromSizesFile)
        seq_regions = dict()
        with open(self.inputFile, 'r') as bed:
            for line in bed:
                field = OrderedDict()
                attribute = OrderedDict()
                li = line.rstrip().split("\t")
                field['seqid'] = li[0]
                if field['seqid'] not in seq_regions:
                    end_region = sizes_dict[field['seqid']]
                    gff3.write("##sequence-region " + field['seqid'] + ' 1 ' + str(end_region) + '\n')
                    seq_regions[field['seqid']] = end_region
                field['source'] = 'UCSC BLAT alignment tool'
                field['type'] = 'match'
                # The first base in a chromosome is numbered 0 in BED format
                field['start'] = str(int(li[1]) + 1)
                field['end'] = li[2]
                field['score'] = li[4]
                field['strand'] = li[5]
                field['phase'] = '.'
                attribute['ID'] = li[0] + '_' + li[3]
                attribute['Name'] = li[3]
                attribute['blockcount'] = li[9]
                attribute['blocksizes'] = li[10]
                attribute['chromstarts'] = li[11]
                attribute['ochrom_start'] = li[12]
                attribute['ochrom_end'] = li[13]
                attribute['ochrom_strand'] = li[14]
                attribute['ochrom_size'] = li[15]
                attribute['ochrom_starts'] = li[16]
                attribute['sequence on other chromosome'] = li[17]
                attribute['cds in ncbi format'] = li[18]
                attribute['size of target chromosome'] = li[19]
                attribute['number of bases matched'] = li[20]
                attribute['number of bases that don\'t match'] = li[21]
                attribute['number of bases that match but are part of repeats'] = li[22]
                attribute['number of \'N\' bases'] = li[23]
                subtools.write_features(field, attribute, gff3)
                subtools.child_blocks(field, attribute, gff3, 'match_part')
        gff3.close()

