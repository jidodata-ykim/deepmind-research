#!/usr/bin/env python3
"""Full WikiGraphs Dataset Exporter for FalkorDB"""

import csv
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, '/home/mpere/ragops/deepmind-research/wikigraphs')

def export_subset(subset='train', version='max256', limit=None, output_base_dir='./falkordb_full_export'):
    """Export a specific subset/version of WikiGraphs to FalkorDB format"""
    
    print(f"🚀 Exporting WikiGraphs {subset}/{version} → FalkorDB CSV")
    
    try:
        from wikigraphs.data import paired_dataset
        print("✅ Imported WikiGraphs successfully")
        
        # Create output directory
        output_dir = Path(output_base_dir) / f"{subset}_{version}"
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory: {output_dir.absolute()}")
        
        # Load dataset
        print(f"📊 Loading dataset {subset}/{version}...")
        dataset = paired_dataset.ParsedDataset(subset=subset, version=version)
        print("✅ Dataset loaded")
        
        # Open output files
        triplets_file = output_dir / f'wikigraphs_{subset}_{version}_triplets.csv'
        nodes_file = output_dir / f'wikigraphs_{subset}_{version}_nodes.csv'
        
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
            total_edges = 0
            
            start_time = datetime.now()
            
            # Process all graphs (or limit if specified)
            for i, pair in enumerate(dataset):
                if limit and i >= limit:
                    print(f"🛑 Reached limit of {limit} graphs")
                    break
                
                graphs_processed += 1
                
                # Progress reporting
                if i % 100 == 0 and i > 0:
                    elapsed = datetime.now() - start_time
                    rate = i / elapsed.total_seconds()
                    print(f"📊 Processed {i:,} graphs... ({rate:.1f} graphs/sec)")
                
                try:
                    edges = pair.graph.to_edges()
                    context = getattr(pair, 'title', f'Graph_{i}')
                    
                    graph_edges = 0
                    for edge_str in edges:
                        if edge_str in unique_triplets:
                            continue
                            
                        unique_triplets.add(edge_str)
                        total_edges += 1
                        graph_edges += 1
                        
                        parts = edge_str.split('\t')
                        if len(parts) == 3:
                            subject, predicate, obj = parts
                            
                            # Clean predicate - more comprehensive cleaning
                            clean_pred = (predicate
                                        .replace('ns/', '')
                                        .replace('key/', '')
                                        .replace('type/', '')
                                        .replace('.', '_')
                                        .replace('/', '_')
                                        .replace('-', '_')
                                        .replace(' ', '_'))
                            
                            # Write triplet
                            triplet_writer.writerow([subject, clean_pred, obj, context])
                            
                            # Track nodes
                            for node in [subject, obj]:
                                if node not in unique_nodes:
                                    unique_nodes.add(node)
                                    
                                    # More sophisticated node type determination
                                    if node.startswith('ns/m.'):
                                        node_type = 'Entity'
                                    elif node.startswith('ns/g.'):
                                        node_type = 'Entity'  # Guid entities
                                    elif node.startswith('ns/'):
                                        node_type = 'Concept'
                                    elif node.startswith('key/'):
                                        node_type = 'Key'
                                    elif node.startswith('"') and node.endswith('"'):
                                        node_type = 'Literal'
                                    elif node.startswith('type/'):
                                        node_type = 'Type'
                                    else:
                                        node_type = 'Other'
                                    
                                    # Clean display name
                                    if node.startswith('"') and node.endswith('"'):
                                        display = node[1:-1]  # Remove quotes
                                    elif node.startswith('ns/'):
                                        display = node[3:]    # Remove ns/ prefix
                                    elif node.startswith('key/'):
                                        display = node[4:]    # Remove key/ prefix
                                    elif node.startswith('type/'):
                                        display = node[5:]    # Remove type/ prefix
                                    else:
                                        display = node
                                    
                                    # Replace underscores with spaces for readability
                                    display = display.replace('_', ' ')
                                    
                                    node_writer.writerow([node, node_type, display])
                
                except Exception as e:
                    print(f"⚠️  Error in graph {i}: {e}")
                    continue
        
        # Write import script
        script_file = output_dir / f'import_{subset}_{version}.cypher'
        with open(script_file, 'w') as f:
            f.write(f"""-- FalkorDB Import Script for WikiGraphs {subset}/{version}
-- Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Copy this file and the CSV files to your FalkorDB import directory

-- Create indexes for performance
CREATE INDEX FOR (n) ON (n.node_id);
CREATE INDEX FOR (n) ON (n.node_type);
CREATE INDEX FOR (n) ON (n.display_name);

-- Load nodes first
LOAD CSV WITH HEADERS FROM 'file://wikigraphs_{subset}_{version}_nodes.csv' AS row
MERGE (n {{node_id: row.node_id, node_type: row.node_type, display_name: row.display_name}});

-- Load relationships  
LOAD CSV WITH HEADERS FROM 'file://wikigraphs_{subset}_{version}_triplets.csv' AS row
MATCH (s {{node_id: row.subject}})
MATCH (o {{node_id: row.object}})
CREATE (s)-[r:RELATION {{type: row.predicate, context: row.context}}]->(o);

-- Create additional indexes on relationship types
CALL db.index.fulltext.createRelationshipIndex('rel_type_index', ['RELATION'], ['type']);

-- Verify import
MATCH (n) RETURN n.node_type, count(n) as node_count ORDER BY node_count DESC;
MATCH ()-[r]-() RETURN r.type, count(r) as rel_count ORDER BY rel_count DESC LIMIT 20;

-- Sample queries
-- Find all entities
-- MATCH (n {{node_type: 'Entity'}}) RETURN n LIMIT 10;

-- Find relationships of a specific type
-- MATCH ()-[r {{type: 'wikipedia_en'}}]-() RETURN r LIMIT 10;

-- Find nodes with specific display names
-- MATCH (n) WHERE n.display_name CONTAINS 'Obama' RETURN n;
""")
        
        # Generate stats file
        stats_file = output_dir / f'stats_{subset}_{version}.txt'
        elapsed = datetime.now() - start_time
        
        with open(stats_file, 'w') as f:
            f.write(f"WikiGraphs {subset}/{version} Export Statistics\n")
            f.write(f"=" * 50 + "\n\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Processing Time: {elapsed}\n")
            f.write(f"Graphs Processed: {graphs_processed:,}\n")
            f.write(f"Unique Triplets: {len(unique_triplets):,}\n")
            f.write(f"Unique Nodes: {len(unique_nodes):,}\n")
            f.write(f"Processing Rate: {graphs_processed / elapsed.total_seconds():.1f} graphs/sec\n")
            f.write(f"Triplets per Graph: {len(unique_triplets) / graphs_processed:.1f}\n")
            f.write(f"Nodes per Graph: {len(unique_nodes) / graphs_processed:.1f}\n")
        
        print(f"\n✅ Export completed successfully!")
        print(f"📈 Final Statistics:")
        print(f"   ⏱️  Processing time: {elapsed}")
        print(f"   📊 Graphs processed: {graphs_processed:,}")
        print(f"   🔗 Unique triplets: {len(unique_triplets):,}")
        print(f"   🔵 Unique nodes: {len(unique_nodes):,}")
        print(f"   ⚡ Rate: {graphs_processed / elapsed.total_seconds():.1f} graphs/sec")
        
        print(f"\n📋 Generated files:")
        print(f"   📄 {triplets_file}")
        print(f"   📄 {nodes_file}")
        print(f"   📄 {script_file}")
        print(f"   📄 {stats_file}")
        
        return {
            'success': True,
            'graphs_processed': graphs_processed,
            'unique_triplets': len(unique_triplets),
            'unique_nodes': len(unique_nodes),
            'processing_time': elapsed,
            'output_dir': output_dir
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def main():
    parser = argparse.ArgumentParser(description='Export WikiGraphs dataset to FalkorDB format')
    parser.add_argument('--subset', choices=['train', 'valid', 'test'], default='train',
                       help='Dataset subset to export (default: train)')
    parser.add_argument('--version', choices=['max256', 'max512', 'max1024'], default='max256',
                       help='Dataset version to export (default: max256)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of graphs to process (default: no limit)')
    parser.add_argument('--output-dir', default='./falkordb_full_export',
                       help='Base output directory (default: ./falkordb_full_export)')
    parser.add_argument('--all', action='store_true',
                       help='Export all subsets and versions')
    
    args = parser.parse_args()
    
    if args.all:
        print("🚀 Exporting ALL WikiGraphs subsets and versions...")
        
        combinations = [
            ('train', 'max256'),
            ('train', 'max512'),
            ('train', 'max1024'),
            ('valid', 'max256'),
            ('valid', 'max512'),
            ('valid', 'max1024'),
            ('test', 'max256'),
            ('test', 'max512'),
            ('test', 'max1024')
        ]
        
        results = []
        total_start = datetime.now()
        
        for subset, version in combinations:
            print(f"\n{'='*60}")
            print(f"Starting export: {subset}/{version}")
            print(f"{'='*60}")
            
            result = export_subset(subset, version, args.limit, args.output_dir)
            results.append((subset, version, result))
            
            if not result['success']:
                print(f"❌ Failed to export {subset}/{version}: {result.get('error', 'Unknown error')}")
            else:
                print(f"✅ Completed {subset}/{version}")
        
        # Summary
        total_time = datetime.now() - total_start
        print(f"\n{'='*60}")
        print(f"EXPORT SUMMARY")
        print(f"{'='*60}")
        print(f"Total time: {total_time}")
        
        for subset, version, result in results:
            status = "✅" if result['success'] else "❌"
            if result['success']:
                print(f"{status} {subset}/{version}: {result['graphs_processed']:,} graphs, {result['unique_triplets']:,} triplets")
            else:
                print(f"{status} {subset}/{version}: FAILED")
        
    else:
        # Export single subset/version
        result = export_subset(args.subset, args.version, args.limit, args.output_dir)
        return 0 if result['success'] else 1

if __name__ == '__main__':
    sys.exit(main())
