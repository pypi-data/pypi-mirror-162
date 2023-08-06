#!/bin/bash
{% set log_dir = jobs_dir + "/log" %}
#SBATCH --nodes={{ request_cpus }}
#SBATCH --mem={{ required_mem }}
#SBATCH --array=1-{{ n_jobs }}
#SBATCH --time={{ request_time }}
#SBATCH --output={{ log_dir }}/out_%a.log

{{ executable }} {{ arguments }}