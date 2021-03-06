import os
import ConfigParser
import simplejson
import itertools
import shutil
import datetime

import tps_utils

class TPS_settings:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.process_settings(settings_file)
    def get_force_recount(self, count_type):
        return self.settings['force_%s_recount' % count_type]
    def get_settings_file(self):
        return self.settings_file
    def get_property(self, property, default=None):
        try:
            if not property in self.settings and default != None:
                return default
            return self.settings[property]
        except:
            print self.settings
            raise  ValueError('cannot find %s' % property)
    def get_rdir(self):
        tps_utils.make_dir(self.rdir)
        return self.rdir
    def get_wdir(self):
        tps_utils.make_dir(self.wdir)
        return self.wdir
    def get_input_barcode(self):
        return self.settings['library_seq_barcode']

    def iter_lib_settings(self):
        for i in range(len(self.sample_names)):
            yield TPS_lib_settings(self,
              self.sample_names[i],
              self.fastq_gz_file_handles[i])

    def process_settings(self, settings_file):
        """
        - reads the settings file and converts str to float, list, etc.
        - stores result in self.settings as a dict()
        """
        int_keys = [ 'first_base_to_keep', 'last_base_to_keep', 'max_reads_to_split', 'minimum_reads_for_inclusion',
                     'pool_5trim', 'pool_3trim', 'min_post_adaptor_length']
        #float_keys = []
        str_keys = ['adaptor_sequence', 'rrna_index', 'genome_index', 'pool_append', 'pool_prepend', 'primer_sequence']
        boolean_keys = ['collapse_identical_reads', 'force_read_resplit', 'force_remapping', 'force_recollapse',
                        'force_recount', 'force_index_rebuild', 'force_retrim', 'trim_adaptor']
        list_str_keys = ['fastq_gz_files', 'sample_names']
        #list_float_keys = ['concentrations', 'input_rna']
        extant_files = ['pool_fasta',]
        config = ConfigParser.ConfigParser()
        config.read(settings_file)
        settings = {}
        for section in config.sections():
            for option in config.options(section):
                settings[option] = config.get(section, option)
                settings[section] = True
        for k in int_keys:
            settings[k] = int(settings[k])
        for k in str_keys:
            settings[k] = settings[k]
        #for k in float_keys:
        #    settings[k] = float(settings[k])
        for k in boolean_keys:
            if not settings[k].lower() in ['true', 'false']:
                raise ValueError(
                  'Boolean value %s must be "true" or "false"' % k)
            settings[k] = settings[k].lower() == 'true'
        #for k in list_float_keys:
        #    settings[k] = map(float, simplejson.loads(settings[k]))
        #for k in list_int_keys:
        #    settings[k] = map(int, simplejson.loads(settings[k]))
        for k in list_str_keys:
            settings[k] = simplejson.loads(settings[k])
        self.fqdir = settings['fastq_dir']
        self.sample_names = settings['sample_names']
        self.fastq_gz_file_handles = [os.path.join(self.fqdir, fastq_gz_file) for fastq_gz_file in
                                      settings['fastq_gz_files']]
        for file_handle in self.fastq_gz_file_handles:
            assert tps_utils.file_exists(file_handle)
        for k in extant_files:
            assert tps_utils.file_exists(settings[k])
        self.settings = settings
        self.wdir = settings['working_dir']
        self.rdir = settings['results_dir']
        shutil.copy(settings_file, self.rdir)

    def check_barcode_lens(self):
        """
        verifies that all the barcodes are the same length
        """
        barcode_lens = set(map(len, self.settings['barcodes']))
        if 1 != len(barcode_lens):
            raise ValueError('all barcodes must be the same length')
        self.barcode_len = barcode_lens.pop()
        self.settings['barcode_len'] = self.barcode_len

    def check_barcodes_are_separated(self):
        """
        makes sure the barcodes are all totally distinguishable
        """
        for b1, b2 in itertools.combinations(self.settings['barcodes'], 2):
            hamming_dist = tps_utils.hamming_distance(b1, b2)
            if hamming_dist < 2:
                raise ValueError('The barcodes supplied are not well '
                  'separated: %s-%s' % (b1, b2))

    def get_bowtie_index(self):
        index = os.path.join(
          self.get_rdir(),
          'bowtie_indices',
          'pool_index')
        return index

    def get_rRNA_bowtie_index(self):
        index = index = self.get_property('rrna_index')
        return index

    def get_genome_bowtie_index(self):
        index = self.get_property('genome_index')
        return index
    def bowtie_index_exists(self):
        return tps_utils.file_exists(self.get_bowtie_index()+'.1.bt2')

    def get_log(self):
        log = os.path.join(
          self.get_rdir(),
          'log.txt')
        return log
    def write_to_log(self, text, add_time = True):
        f = open(self.get_log(), 'a')
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M")
        if add_time:
            f.write('[%s] %s\n' % (time, text))
        else:
            f.write(text)
        f.close()
    def get_trimmed_pool_fasta(self):
        log = os.path.join(
          self.get_rdir(),
          'trimmed_pool_seqs.fasta')
        return log

class TPS_lib_settings:
    def __init__(self, experiment_settings, sample_name, fastq_gz_filehandle):
        self.experiment_settings = experiment_settings
        self.sample_name = sample_name
        self.fastq_gz_filehandle = fastq_gz_filehandle

    def get_property(self, property):
        return self.experiment_settings.get_property(property)

    def get_log(self):
        tps_utils.make_dir(os.path.join(self.experiment_settings.get_rdir(), 'logs'))
        log = os.path.join(
          self.experiment_settings.get_rdir(),
          'logs',
          '%(sample_name)s.log' %
           {'sample_name': self.sample_name})
        return log
    def write_to_log(self, text, add_time = True):
        f = open(self.get_log(), 'a')
        now = datetime.datetime.now()
        time = now.strftime("%Y-%m-%d %H:%M")
        if add_time:
            f.write('[%s] %s\n' % (time, text))
        else:
            f.write(text)
        f.close()

    def get_fastq_file(self):
        return self.fastq_gz_filehandle

    def get_collapsed_reads(self):
        collapsed_reads = os.path.join(
          self.experiment_settings.get_rdir(),
          'collapsed_reads',
          '%(sample_name)s.fasta.gz' %
           {'sample_name': self.sample_name})
        return collapsed_reads

    def get_adaptor_trimmed_reads(self):
        collapsed_reads = os.path.join(
          self.experiment_settings.get_rdir(),
          'adaptor_removed',
          '%(sample_name)s.fasta.gz' %
           {'sample_name': self.sample_name})
        return collapsed_reads

    def get_primer_trimmed_reads(self):
        collapsed_reads = os.path.join(
          self.experiment_settings.get_rdir(),
          'primer_removed',
          '%(sample_name)s.fasta.gz' %
           {'sample_name': self.sample_name})
        return collapsed_reads

    def get_pool_mapping_stats(self):
        pool_mapping_stats = os.path.join(self.experiment_settings.get_rdir(), 'mapping_stats', '%(sample_name)s.pool.txt' % {'sample_name': self.sample_name})
        return pool_mapping_stats

    def get_rRNA_mapping_stats(self):
        rRNA_mapping_stats = os.path.join(self.experiment_settings.get_rdir(), 'mapping_stats', '%(sample_name)s.rRNA.txt' %{'sample_name': self.sample_name})
        return rRNA_mapping_stats

    def get_genome_mapping_stats(self):
        rRNA_mapping_stats = os.path.join(
          self.experiment_settings.get_rdir(),
          'mapping_stats',
          '%(sample_name)s.genome.txt' %
           {'sample_name': self.sample_name})
        return rRNA_mapping_stats

    def get_mapped_reads(self):
        mapped_reads = os.path.join(self.experiment_settings.get_rdir(), 'mapped_reads', '%(sample_name)s.bam' % {'sample_name': self.sample_name})
        return mapped_reads

    def get_mapped_reads_sam(self):
        mapped_reads = os.path.join(self.experiment_settings.get_rdir(), 'mapped_reads', '%(sample_name)s.sam' % {'sample_name': self.sample_name})
        return mapped_reads

    def get_unmappable_reads(self):
        unmapped_reads = os.path.join(
          self.experiment_settings.get_rdir(),
          'unmapped_reads',
          '%(sample_name)s.unmappable.fasta.gz' %
           {'sample_name': self.sample_name})
        return unmapped_reads

    def get_rRNA_mapped_reads(self):
        mapped_reads = os.path.join(self.experiment_settings.get_rdir(), 'mapped_reads', '%(sample_name)s_rRNA.bam' % {'sample_name': self.sample_name})
        return mapped_reads

    def get_rRNA_unmapped_reads(self):
        mapped_reads = os.path.join(self.experiment_settings.get_rdir(), 'unmapped_reads', '%(sample_name)s_rRNA.unmapped.fasta.gz' % {'sample_name': self.sample_name})
        return mapped_reads

    def get_genome_mapped_reads(self):
        mapped_reads = os.path.join(self.experiment_settings.get_rdir(), 'mapped_reads', '%(sample_name)s_genome.bam' % {'sample_name': self.sample_name})
        return mapped_reads

    def get_genome_unmapped_reads(self):
        mapped_reads = os.path.join(self.experiment_settings.get_rdir(), 'unmapped_reads', '%(sample_name)s_genome.unmapped.fasta.gz' % {'sample_name': self.sample_name})
        return mapped_reads


    def get_trimmed_reads(self):
        trimmed_reads = os.path.join(
          self.experiment_settings.get_rdir(),
          'trimmed_reads',
          '%(sample_name)s.trimmed.fasta.gz' %
           {'sample_name': self.sample_name})
        return trimmed_reads

    def get_sequence_counts(self):
        sequence_counts = os.path.join(
          self.experiment_settings.get_rdir(),
          'sequence_counts',
          '%(sample_name)s.counts.pkl' %
           {'sample_name': self.sample_name})
        return sequence_counts

    def get_overall_contamination_summary(self):
        summary_file = os.path.join(
          self.experiment_settings.get_rdir(),
          'QC',
          '%(sample_name)s.contamination_summary.txt' %
           {'sample_name': self.sample_name})
        return summary_file

    def split_reads_exist(self):
        split_reads = self.get_split_reads()
        return tps_utils.file_exists(split_reads)

    def collapsed_reads_exist(self):
        collapsed_reads = self.get_collapsed_reads()
        return tps_utils.file_exists(collapsed_reads)

    def adaptorless_reads_exist(self):
        adaptorless_reads = self.get_adaptor_trimmed_reads()
        return tps_utils.file_exists(adaptorless_reads)

    def primerless_reads_exist(self):
        primerless_reads = self.get_primer_trimmed_reads()
        return tps_utils.file_exists(primerless_reads)

    def trimmed_reads_exist(self):
        trimmed_reads = self.get_trimmed_reads()
        return tps_utils.file_exists(trimmed_reads)

    def mapped_reads_exist(self):
        mapped_reads = self.get_mapped_reads()
        return tps_utils.file_exists(mapped_reads)

    def sequence_counts_exist(self):
        sequence_counts = self.get_sequence_counts()
        return tps_utils.file_exists(sequence_counts)