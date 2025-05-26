deactivate
rm -rf .venv/
rm pyproject.toml 
rm uv.lock 
uv venv --python=3.10
uv python pin 3.10
source .venv/bin/activate
which pip
which python
python --version
#pip list
#pip install -r requirements.txt
#pip install -e .
#python --version
#python scripts/build_vocab.py   --vocab_file_path=../data/wikitext-vocab.csv   --data_dir=../data/wikitext-103
uv pip install -U pip
uv pip install -r requirements.txt 
uv pip install -e .
uv add -r requirements.txt
uv pip list
uv run python --version
uv run --active python scripts/build_vocab.py   --vocab_file_path=../data/wikitext-vocab.csv   --data_dir=../data/wikitext-103
