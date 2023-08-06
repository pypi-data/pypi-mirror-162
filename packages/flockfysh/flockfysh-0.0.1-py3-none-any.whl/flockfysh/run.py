import yaml
import os
import sys


try:
    from config import BASE_DIR
except:
    from flockfysh.config import BASE_DIR

if not os.path.abspath(BASE_DIR) in sys.path:
    sys.path.append(os.path.abspath(BASE_DIR))

for pth in [ f.name for f in os.scandir(os.path.join(BASE_DIR, 'scraper')) if f.is_dir() ]:
    if not os.path.abspath(os.path.join(BASE_DIR, 'scraper', pth)) in sys.path:
        sys.path.append(os.path.abspath(os.path.join(BASE_DIR, 'scraper', pth)))
for pth in [ f.name for f in os.scandir(os.path.join(BASE_DIR, 'utilities')) if f.is_dir() ]:
    if not os.path.abspath(os.path.join(BASE_DIR, 'utilities', pth)) in sys.path:
        sys.path.append(os.path.abspath(os.path.join(BASE_DIR, 'utilities', pth)))


from utilities.pipelines.training_webscrape_loop import run_training_object_detection_webscrape_loop
from utilities.parse_config.input_validator import get_jobs_from_yaml_params, get_input_yaml 
from utilities.parse_config.job_config import TRAIN_SCRAPE_JOB, ANNOTATE_JOB, DOWNLOAD_JOB, SUPPORTED_DOWNLOAD_APIS
from utilities.output_generation.misc_output import generate_json_file
from utilities.dataset_setup.download_dataset import download_dataset

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

def run():
    #Load the YAML params first

    yaml_params = get_input_yaml(sys.argv[1])
    jobs = get_jobs_from_yaml_params(yaml_params)
    output_dir, _ = os.path.split(os.path.abspath(sys.argv[1]))

    for job in jobs:
        if job['job_type'] == TRAIN_SCRAPE_JOB:
            print(f'Running train scrape job with name {job["job_name"]}')      
            job['output-working-dir'] = output_dir
            job['input-dir'] = os.path.abspath(os.path.join(output_dir, job['input-dir']))
            run_training_object_detection_webscrape_loop(**job)
            generate_json_file(job)
        
        elif job['job_type'] == ANNOTATE_JOB:
            job['input-dir'] = os.path.abspath(os.path.join(output_dir, job['input-dir']))
            print(f'Running annotate job with name {job["job_name"]}')

        elif job['job_type'] == DOWNLOAD_JOB:
            if job['api-name'] in SUPPORTED_DOWNLOAD_APIS:
                job['output-working-dir'] = output_dir
                download_dataset(job['api-name'], job)
        


if __name__ == '__main__':
    run()
