#!/usr/bin/env python3
"""FalkorDB CSV Exporter for WikiGraphs - Working Version"""

import csv
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '/home/mpere/ragops/deepmind-research/wikigraphs')

def main():
    print("🚀 WikiGraphs → FalkorDB CSV Exporter")
    
    try:
        from wikigraphs.data import paired_dataset
        print("✅ Imported WikiGraphs successfully")
        
        # Create output directory
        output_dir = Path('./falkordb_csv_export')
        output_dir.mkdir(exist_ok=True)
        print(f"📁 Created output directory: {output_dir.absolute()}")
        
        # Load dataset
        print("📊 Loading dataset...")
        dataset = paired_dataset.ParsedDataset(subset='train', version='max256')
        print("✅ Dataset loaded")
        
        # Open output files
        triplets_file = output_dir / 'wikigraphs_train_max256_full_triplets.csv'
        nodes_file = output_dir / 'wikigraphs_train_max256_full_nodes.csv'
        
        print(f"📝 Writing to:")
        print(f"   - {triplets_file}")
        print(f"   - {nodes_file}")
        
        with open(triplets_file, 'w', newline='', encoding='utf-8') as tf, \
             open(nodes_file, 'w', newline='', encoding='utf-8') as nf:
            
            triplet_writer = csv.writer(tf)
            node_writer = csv.writer(nf)
            
            # Write headers
            triplet_writer.writerow(['subject', 'predicate', 'object', 'context'])
            node_writer.writerow(['node_id', 'node_type', 'display_name'])
            
            unique_triplets = set()
            unique_nodes = set()
            graphs_processed = 0
            
            # Process all graphs in the dataset
            for i, pair in enumerate(dataset):
                graphs_processed += 1
                
                if i % 100 == 0:
                    print(f"📊 Processed {i} graphs...")
                
                try:
                    edges = pair.graph.to_edges()
                    context = getattr(pair, 'title', f'Graph_{i}')
                    
                    for edge_str in edges:
                        if edge_str in unique_triplets:
                            continue
                            
                        unique_triplets.add(edge_str)
                        
                        parts = edge_str.split('\t')
                        if len(parts) == 3:
                            subject, predicate, obj = parts
                            
                            # Clean predicate
                            clean_pred = predicate.replace('ns/', '').replace('key/', '').replace('.', '_').replace('/', '_')
                            
                            # Write triplet
                            triplet_writer.writerow([subject, clean_pred, obj, context])
                            
                            # Track nodes
                            for node in [subject, obj]:
                                if node not in unique_nodes:
                                    unique_nodes.add(node)
                                    
                                    # Determine node type
                                    if node.startswith('ns/m.'):
                                        node_type = 'Entity'
                                    elif node.startswith('ns/'):
                                        node_type = 'Concept'
                                    elif node.startswith('"'):
                                        node_type = 'Literal'
                                    else:
                                        node_type = 'Other'
                                    
                                    # Display name
                                    display = node[1:-1] if node.startswith('"') and node.endswith('"') else node
                                    
                                    node_writer.writerow([node, node_type, display])
                
                except Exception as e:
                    print(f"⚠️  Error in graph {i}: {e}")
                    continue
        
        # Write import script
        script_file = output_dir / 'falkordb_import.cypher'
        with open(script_file, 'w') as f:
            f.write("""-- FalkorDB Import Script for WikiGraphs
-- Copy this file and the CSV files to your FalkorDB import directory

-- Create indexes
CREATE INDEX FOR (n) ON (n.node_id);
CREATE INDEX FOR (n) ON (n.node_type);

-- Load nodes
LOAD CSV WITH HEADERS FROM 'file://wikigraphs_nodes.csv' AS row
MERGE (n {node_id: row.node_id, node_type: row.node_type, display_name: row.display_name});

-- Load relationships  
LOAD CSV WITH HEADERS FROM 'file://wikigraphs_triplets.csv' AS row
MATCH (s {node_id: row.subject})
MATCH (o {node_id: row.object})
CREATE (s)-[r:RELATION {type: row.predicate, context: row.context}]->(o);

-- Verify import
MATCH (n) RETURN n.node_type, count(n) as node_count;
MATCH ()-[r]-() RETURN r.type, count(r) as rel_count LIMIT 10;
""")
        
        print(f"\n✅ Export completed successfully!")
        print(f"📈 Statistics:")
        print(f"   📊 Graphs processed: {graphs_processed}")
        print(f"   🔗 Unique triplets: {len(unique_triplets)}")
        print(f"   🔵 Unique nodes: {len(unique_nodes)}")
        print(f"\n📋 Generated files:")
        print(f"   📄 {triplets_file}")
        print(f"   📄 {nodes_file}")
        print(f"   📄 {script_file}")
        print(f"\n🔧 To import into FalkorDB:")
        print(f"   1. Copy CSV files to FalkorDB import directory")
        print(f"   2. Execute the commands in {script_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
