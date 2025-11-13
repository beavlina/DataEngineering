import json
import shutil
from pathlib import Path
from typing import Any

from fastavro import writer, parse_schema
from flask import Flask, request

JOBS_ROOT_PATH: Path = Path('../storage')

app = Flask(__name__)


def run_sales_job(root_path: Path, stg_path: Path, raw_path: Path, date: str) -> dict[str, str]:
    result: dict[str, str] = {}

    stg_dir: Path = root_path / stg_path / 'sales' / date
    raw_dir: Path = root_path / raw_path/ 'sales' / date


    # cleanup job directory
    if stg_dir.exists():
        shutil.rmtree(stg_dir)
    stg_dir.mkdir(parents=True, exist_ok=True)

    avro_schema: dict[str, Any] = {
        'name': 'Entry',
        'type': 'record',
        'fields': [
            {'name': 'client', 'type': 'string'},
            {'name': 'purchase_date', 'type': 'string'},
            {'name': 'product', 'type': 'string'},
            {'name': 'price', 'type': 'int'},
        ]
    }

    parsed_schema = parse_schema(avro_schema)

    for file in raw_dir.iterdir():
        text: str | None = None

        if file.is_file():
            with open(file, 'r') as f:
                text = f.read()

        if text is None:
            raise ValueError(f'Couldn\'t read data from {file}. Is that a file?')

        json_data: Any = json.loads(text)

        with open(stg_dir / f'sales_{date}.avro', 'wb') as out:
            writer(
                out,
                parsed_schema,
                json_data
            )






    return result

# http://127.0.0.1:8082/jsons_to_avro?stg_path=stg&raw_path=raw&date=2022-08-09
@app.route('/jsons_to_avro', methods=['POST'])
def jsons_to_avro() -> dict[str, str]:
    result: dict[str, str] = {}

    stg_path: str | None = request.args.get('stg_path')
    raw_path: str | None = request.args.get('raw_path')
    date: str | None = request.args.get('date')

    if stg_path is None:
        result['PathError'] = 'You must provide stg_path'
    if raw_path is None:
        result['PathError'] = 'You must provide raw_path'
    # TODO check date format
    if date is None:
        result['DateError'] = 'You must provide date'

    result = run_sales_job(
        JOBS_ROOT_PATH,
        Path(stg_path),
        Path(raw_path),
        date
    )

    return result

if __name__ == '__main__':
    app.run(port=8082, debug=True)