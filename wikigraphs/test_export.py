#!/usr/bin/env python3
"""Minimal test script for WikiGraphs export."""

print("🚀 Starting WikiGraphs export test...")

try:
    # Test import
    print("📦 Importing modules...")
    from wikigraphs.data import paired_dataset
    print("✅ Import successful")
    
    # Test dataset loading
    print("📊 Loading dataset...")
    dataset = paired_dataset.ParsedDataset(subset='train', version='max256')
    print("✅ Dataset loaded")
    
    # Test iteration
    print("🔄 Testing iteration...")
    count = 0
    triplet_count = 0
    
    for i, pair in enumerate(dataset):
        count += 1
        edges = pair.graph.to_edges()
        triplet_count += len(edges)
        
        if i == 0:
            print(f"📋 First graph sample:")
            print(f"   Title: {getattr(pair, 'title', 'N/A')}")
            print(f"   Edges: {len(edges)}")
            if edges:
                print(f"   Sample edge: {edges[0]}")
        
        if i >= 10:  # Test first 10 graphs
            break
    
    print(f"✅ Successfully processed {count} graphs with {triplet_count} total triplets")
    
    # Now try a simple export
    print("💾 Creating simple CSV export...")
    
    import csv
    from pathlib import Path
    
    output_dir = Path('./test_export')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'sample_triplets.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['subject', 'predicate', 'object'])
        
        # Export from first few graphs
        for i, pair in enumerate(dataset):
            if i >= 5:  # Just first 5 graphs
                break
                
            for edge in pair.graph.to_edges():
                parts = edge.split('\t')
                if len(parts) == 3:
                    writer.writerow(parts)
    
    print(f"✅ Sample export complete! Check {output_dir / 'sample_triplets.csv'}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("🏁 Test complete!")
