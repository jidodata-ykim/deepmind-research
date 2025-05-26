#!/usr/bin/env python3
"""
Simple FalkorDB CSV exporter for WikiGraphs dataset.
Creates CSV files compatible with FalkorDB's LOAD CSV functionality.
"""

import csv
import sys
from pathlib import Path
from wikigraphs.data import paired_dataset

def export_to_falkordb_csv(subset='train', version='max256', max_graphs=100, output_dir='./falkordb_export'):
    """Export WikiGraphs to FalkorDB-compatible CSV format."""
    
    print(f"🚀 Exporting WikiGraphs {subset}/{version} to FalkorDB CSV format")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Load dataset
    try:
        dataset = paired_dataset.ParsedDataset(subset=subset, version=version)
        print("✅ Dataset loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        return
    
    # Output files
    triplets_file = output_path / f"wikigraphs_{subset}_{version}_triplets.csv"
    nodes_file = output_path / f"wikigraphs_{subset}_{version}_nodes.csv"
    
    # Track unique items
    unique_triplets = set()
    unique_nodes = set()
    
    # Statistics
    stats = {
        'graphs_processed': 0,
        'total_triplets': 0,
        'unique_triplets': 0,
        'unique_nodes': 0
    }
    
    print(f"📁 Writing to: {output_path}")
    
    with open(triplets_file, 'w', newline='', encoding='utf-8') as tf, \
         open(nodes_file, 'w', newline='', encoding='utf-8') as nf:
        
        # CSV writers
        triplet_writer = csv.writer(tf, quoting=csv.QUOTE_MINIMAL)
        node_writer = csv.writer(nf, quoting=csv.QUOTE_MINIMAL)
        
        # Write headers
        triplet_writer.writerow(['subject', 'predicate', 'object', 'context'])
        node_writer.writerow(['node_id', 'node_type', 'display_name'])
        
        # Process graphs
        for i, pair in enumerate(dataset):
            if max_graphs and i >= max_graphs:
                break
                
            if i % 10 == 0:
                print(f"📊 Processed {i} graphs, {len(unique_triplets)} unique triplets")
            
            stats['graphs_processed'] += 1
            
            try:
                # Get triplets from graph
                triplets = pair.graph.to_edges()
                
                for triplet_str in triplets:
                    stats['total_triplets'] += 1
                    
                    # Skip if already seen
                    if triplet_str in unique_triplets:
                        continue
                    
                    unique_triplets.add(triplet_str)
                    stats['unique_triplets'] += 1
                    
                    # Parse triplet
                    parts = triplet_str.split('\t')
                    if len(parts) != 3:
                        continue
                    
                    subject, predicate, obj = parts
                    
                    # Clean predicate name (remove namespaces, replace special chars)
                    clean_predicate = predicate
                    if clean_predicate.startswith('ns/'):
                        clean_predicate = clean_predicate[3:]
                    elif clean_predicate.startswith('key/'):
                        clean_predicate = clean_predicate[4:]
                    clean_predicate = clean_predicate.replace('.', '_').replace('/', '_')
                    
                    # Write triplet
                    context = getattr(pair, 'title', '')
                    triplet_writer.writerow([subject, clean_predicate, obj, context])
                    
                    # Track nodes
                    for node in [subject, obj]:
                        if node not in unique_nodes:
                            unique_nodes.add(node)
                            
                            # Determine node type
                            if node.startswith('ns/m.'):
                                node_type = 'Entity'
                            elif node.startswith('ns/'):
                                node_type = 'Concept'
                            elif node.startswith('key/'):
                                node_type = 'Key'
                            elif node.startswith('"') and node.endswith('"'):
                                node_type = 'Literal'
                            else:
                                node_type = 'Unknown'
                            
                            # Display name
                            display_name = node
                            if node.startswith('"') and node.endswith('"'):
                                display_name = node[1:-1]  # Remove quotes
                            
                            node_writer.writerow([node, node_type, display_name])
                            
            except Exception as e:
                print(f"⚠️  Error processing graph {i}: {e}")
                continue
    
    # Update final stats
    stats['unique_nodes'] = len(unique_nodes)
    
    # Print results
    print(f"\n✅ Export completed successfully!")
    print(f"📈 Statistics:")
    print(f"  📊 Graphs processed: {stats['graphs_processed']:,}")
    print(f"  🔗 Total triplets found: {stats['total_triplets']:,}")
    print(f"  🔗 Unique triplets exported: {stats['unique_triplets']:,}")
    print(f"  🔵 Unique nodes exported: {stats['unique_nodes']:,}")
    
    print(f"\n📋 Generated files:")
    print(f"  📄 {triplets_file}")
    print(f"  📄 {nodes_file}")
    
    # Generate import script
    script_file = output_path / f"import_{subset}_{version}.cypher"
    with open(script_file, 'w') as f:
        f.write("// FalkorDB Import Script for WikiGraphs\n\n")
        f.write("// 1. Create indexes for better performance\n")
        f.write("CREATE INDEX FOR (n) ON (n.node_id);\n")
        f.write("CREATE INDEX FOR (n) ON (n.node_type);\n\n")
        
        f.write("// 2. Load nodes\n")
        f.write(f"LOAD CSV WITH HEADERS FROM 'file://{nodes_file.name}' AS row\n")
        f.write("MERGE (n {node_id: row.node_id, node_type: row.node_type, display_name: row.display_name});\n\n")
        
        f.write("// 3. Load relationships\n")
        f.write(f"LOAD CSV WITH HEADERS FROM 'file://{triplets_file.name}' AS row\n")
        f.write("MATCH (s {node_id: row.subject})\n")
        f.write("MATCH (o {node_id: row.object})\n")
        f.write("CREATE (s)-[r:RELATION {type: row.predicate, context: row.context}]->(o);\n\n")
        
        f.write("// 4. Verify import\n")
        f.write("MATCH (n) RETURN n.node_type, count(n) as count;\n")
        f.write("MATCH ()-[r]-() RETURN r.type, count(r) as count LIMIT 10;\n")
    
    print(f"  📄 {script_file}")
    
    print(f"\n🔧 To import into FalkorDB:")
    print(f"  1. Copy CSV files to FalkorDB import directory")
    print(f"  2. Run: falkordb-cli --eval \"$(cat {script_file})\"")
    print(f"  3. Or execute commands from {script_file} one by one")

if __name__ == '__main__':
    # Simple command line interface
    subset = sys.argv[1] if len(sys.argv) > 1 else 'train'
    version = sys.argv[2] if len(sys.argv) > 2 else 'max256'
    max_graphs = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    
    export_to_falkordb_csv(subset, version, max_graphs)
