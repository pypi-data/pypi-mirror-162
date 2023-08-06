# -*- python -*-
#
# Copyright 2021, 2022 Xingeng Chen
# Copyright 2018, 2019, 2020, 2021 Liang Chen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# dmprj.engineering.hpcluster.scheduler


class Scheduler(object):
    '''
    High Performance Cluster Job Scheduler
    '''


class SLURM(Scheduler):
    '''
    SLURM scheduler
    '''

    CHAR_SBATCH_FIELD_SEP = ';'  # semicolon
    CHAR_SQUEUE_FIELD_SEP = '|'

    CHECKPOINT_INTERVAL = 300

    FULL_CONTINGENT = 'afterok'
    WEAK_CONTINGENT = 'afterany'
    NO_CONTINGENT   = 'after'

    def get_sbatch_template(self):
        FMT = [
            'sbatch',
            '--parsable',
            #'--parsable --quiet',
            '{dependency}',
            '-p {queue_name}',
            '-J {job_name}',
            '-D {job_dir}',
            '{walltime} {concurrency} {checkpoint}',
            '-e {job_dir}/log.err',
            '-o {job_dir}/log.out',
            '{script}',
        ]
        return FMT

    def _slurm_run(self, command, **kwargs):
        '''
        process command line for SLURM sbatch

        :param command: (obj)

        :return: final command (string)
        '''
        d = {
            'job_name': command.job_name,
            'job_dir': command.job_dir,
            'script': command.job_script,
            'dependency': '--dependency=afterok:{j}'.format(j=command.depend_on_job) if command.depend_on_job else '',
            'queue_name': command.queue_name,
            'concurrency': '-S {n}'.format(n=command.n_thread) if command.n_thread else '',
            'walltime': '-t {wt}'.format(wt=command.wall_time) if command.wall_time else '',
            'checkpoint': '--checkpoint={cp_interval} --checkpoint-dir={cpdir}'.format(cp_interval=self.CHECKPOINT_INTERVAL, cpdir=command.checkpoint_dir) if command.checkpoint_dir else '',
            'priority': '' if command.priority else '',
        }
        return (' '.join(self.get_sbatch_template())).format(**d)

    def slurm_submission_step(self, job_def, **kwargs):
        '''
        SLURM job submission steps

        :param job_def: (obj)

        :return: HPC job id (string or none)
        '''
        output = None
        try:
            self.execute_command(
                self._slurm_run(job_def.preexec_command)
            )
            output = self.execute_command(
                self._slurm_run(job_def.main_command)
            )
            self.execute_command(
                self._slurm_run(job_def.postexec_command)
            )
        except Exception as e:
            self.get_logger().error(self.get_backtrace(e))
            raise e
        return self.sbatch_output_process(output)

    def sbatch_output_process(self, value):
        '''
        :param value: `sbatch` command output (string)

        :return: HPC job id (string or none)
        '''
        ret = None
        if value is not None:
            ret = value.split(self.CHAR_SBATCH_FIELD_SEP)[0]
        return ret

    def get_squeue_output_field(self):
        fields = [
            '%A', # JOBID
            '%j', # NAME
            '%a', # ACCOUNT
            '%u', # USER
            '%P', # PARTITION
            '%T', # STATE
            '%V', # SUBMIT_TIME
            '%t', # ST (stats compact code)
            '%C', # CPUS
        ]
        return fields

    def get_squeue_template(self):
        FMT = [
            'squeue',
            '-h',
            '-a',
            #'-p {queue_name}',
            '-S "P,i"',
            #'-u {user}',
            '-t all',
            #'-O jobid,name,account,username,paritition,state,submittime,exit_code,numcups',
            # '-o "%all"',
            '-o "'+self.CHAR_SQUEUE_FIELD_SEP.join(self.get_squeue_output_field())+'"',
        ]
        return FMT

    def squeue_output_process(self, value):
        '''
        :param value: `squeue` command output (string)

        :return: HPC job record (list of string or none)
        '''
        ret = None
        if value is not None:
            ret = value.split(self.CHAR_SQUEUE_FIELD_SEP)
        return ret


class HTCondor(Scheduler):
    '''
    Condor/HTCondor scheduler
    '''

    def get_condor_submit_template(self):
        '''
        seealso `https://research.cs.wisc.edu/htcondor/manual/v8.6/condor_submit.html`
        seealso `https://research.cs.wisc.edu/htcondor/manual/v8.6/2_5Submitting_Job.html`
        seealso `https://research.iac.es/sieinvens/siepedia/pmwiki.php?n=HOWTOs.CondorSubmitFile`
        '''
        FMT = [
            'condor_submit',
            '{dependency}',
            '-batch-name {job_name}',
            '{submit_description_file}',
            '-queue {queue_name}',
        ]
        return FMT

    def get_decription_file_template(self):
        DESCR = [
            '####################',
            '# submit description file',
            '####################',
            'executable = {script}',
            'log = {job_log}',
            'input = {input}',
            'output = {output}',
            'error = {errlog}',
            'should_transfer_files = Yes',
            'when_to_transfer_output = ON_EXIT',
            'initialdir = {job_dir}',
            'queue',
        ]
        return DESCR
