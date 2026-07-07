# generate_architecture_map.py
import graphviz
import os

def create_architecture_diagram():
    # Create the graph
    dot = graphviz.Digraph('OneHealth_Architecture', comment='System Architecture', format='png')
    dot.attr(rankdir='TB', size='12,12', bgcolor='#f4f6f9')
    
    # 1. DATA SOURCES
    with dot.subgraph(name='cluster_0') as c:
        c.attr(label='1. Data Sources', color='#3c8dbc', style='dashed', fontname='Arial Bold')
        c.node('S1', 'Satellite Remote Sensing\n(18 parameters: NDVI, LST, etc)', shape='box', style='filled', fillcolor='#ffffff')
        c.node('S2', 'Lab Clinical Records\n(19 Priority Pathogens)', shape='box', style='filled', fillcolor='#ffffff')

    # 2. AGENT FACTORY
    with dot.subgraph(name='cluster_1') as c:
        c.attr(label='2. Agent Factory Floor (ADK)', color='#00a65a', style='filled', fillcolor='#e8f5e9', fontname='Arial Bold')
        c.node('A1', 'Data Ingestion Agent\n(Validation & RBAC)', shape='component', style='filled', fillcolor='#ffffff')
        c.node('A2', 'Risk Analysis Agent\n(Probabilistic & SEIR)', shape='component', style='filled', fillcolor='#ffffff')
        c.node('A3', 'Communication Agent\n(Report Orchestrator)', shape='component', style='filled', fillcolor='#ffffff')
        c.edge('A1', 'A2', label='Sanitized Data')
        c.edge('A2', 'A3', label='Risk Outcomes')

    # 3. SECURITY & INTEROP
    dot.node('MCP', 'MCP Server\n(Surveillance Tools)', shape='hexagon', style='filled', fillcolor='#f39c12', fontcolor='white')
    dot.node('Harness', 'Security Harness\n(JIT, Vibe Diff, Policy)', shape='doubleoctagon', style='filled', fillcolor='#dd4b39', fontcolor='white')

    # 4. OUTCOMES
    with dot.subgraph(name='cluster_2') as c:
        c.attr(label='3. Visual Outcomes', color='#00c0ef', style='dashed', fontname='Arial Bold')
        c.node('O1', 'R Shiny Dashboard\n(Interactive GUI)', shape='note', style='filled', fillcolor='#ffffff')
        c.node('O2', 'GIS Asset\n(GeoJSON)', shape='note', style='filled', fillcolor='#ffffff')
        c.node('O3', 'Bulletins\n(Markdown Archive)', shape='note', style='filled', fillcolor='#ffffff')

    # Connections
    dot.edge('S1', 'A1')
    dot.edge('S2', 'A1')
    dot.edge('A3', 'O1')
    dot.edge('A3', 'O2')
    dot.edge('A3', 'O3')
    dot.edge('MCP', 'A3', style='dotted', dir='both')
    dot.edge('Harness', 'A3', color='red', label='Verification')

    # Render
    output_path = 'docs/architecture'
    os.makedirs('docs', exist_ok=True)
    dot.render(output_path, view=False)
    print(f"Architecture diagram generated at: {output_path}.png")

if __name__ == "__main__":
    create_architecture_diagram()
