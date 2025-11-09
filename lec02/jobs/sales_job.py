import os
import shutil
from pathlib import Path

import requests
from flask import Flask, request
from requests.exceptions import HTTPError
from requests.models import Response

FAKE_API_URL: str = 'https://fake-api-vycpfa6oca-uc.a.run.app'
ULTRA_SECRET_TOKEN: str = os.getenv('AUTH_TOKEN')
JOBS_ROOT_PATH: Path = Path('../storage')


app = Flask(__name__)

def run_sales_job(root_path: Path, raw_path: Path, date: str) -> dict[str, str]:
    result: dict[str, str] = {}

    job_dir: Path = root_path / raw_path / 'sales' / date

    # cleanup job directory
    if job_dir.exists():
        shutil.rmtree(job_dir)
    job_dir.mkdir(parents=True, exist_ok=True)

    partition_counter: int = 1
    while True:
        try:
            response: Response = requests.get(
                url = f'{FAKE_API_URL}/sales',
                params = {
                    'date': date,
                    'page': partition_counter
                },
                headers = {
                    'Authorization': ULTRA_SECRET_TOKEN
                }
            )
            response.raise_for_status()

            payload: str = response.text

            with open(job_dir / f'sales_{date}_{partition_counter}.json', 'x') as f:
                f.write(payload)

            partition_counter += 1
        except HTTPError:
            break

    return result

@app.route('/http_to_json', methods=['POST'])
def http_to_jsons() -> dict[str, str]:
    result: dict[str, str] = {}

    path: str | None = request.args.get('raw_dir')
    date: str | None = request.args.get('date')

    if path is None:
        result['PathError'] = 'You must provide path'
    # TODO check date format
    if date is None:
        result['DateError'] = 'You must provide date'

    result = run_sales_job(
        JOBS_ROOT_PATH,
        Path(path),
        date
    )

    return result

if __name__ == '__main__':
    app.run(port=8081, debug=True)