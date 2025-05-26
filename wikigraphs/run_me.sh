uv run python --version
#uv run --active python scripts/build_vocab.py   --vocab_file_path=../data/wikitext-vocab.csv   --data_dir=../data/wikitext-103
#uv run --active python scripts/freebase_preprocess.py --freebase_dir=../data/freebase/max256 --output_dir=../data/wikigraphs/max256
#uv run --active python scripts/freebase_preprocess.py --freebase_dir=../data/freebase/max512 --output_dir=../data/wikigraphs/max512
#uv run --active python scripts/freebase_preprocess.py --freebase_dir=../data/freebase/max1024 --output_dir=../data/wikigraphs/max1024
#uv run --active python export_full_dataset.py --subset train --version max256
#uv run --active python export_full_dataset.py --subset test --version max256
#uv run --active python export_full_dataset.py --subset valid --version max256
#uv run --active python export_full_dataset.py --subset train --version max512
#uv run --active python export_full_dataset.py --subset test --version max512
#uv run --active python export_full_dataset.py --subset valid --version max512
#uv run --active python export_full_dataset.py --subset train --version max1024
#uv run --active python export_full_dataset.py --subset test --version max1024
#uv run --active python export_full_dataset.py --subset valid --version max1024



#uv run --active python -c "
#from wikigraphs.data import paired_dataset
#import sys
#
## Load a small sample of the dataset
#dataset = paired_dataset.ParsedDataset(subset='train', version='max256')
#pair = next(iter(dataset))
#
#print('=== Sample Graph-Text Pair ===')
#print(f'Center node: {pair.center_node}')
#print(f'Title: {pair.title}')
#print(f'Text (first 100 chars): {pair.text[:100]}...')
#print(f'Graph nodes: {pair.graph.nodes()[:5]}...')  # First 5 nodes
#print(f'Graph edges (first 5): {pair.graph.edges()[:5]}...')  # First 5 edges
#print(f'Graph edge format as strings: {pair.graph.to_edges()[:3]}...')  # First 3 edge strings
#"
