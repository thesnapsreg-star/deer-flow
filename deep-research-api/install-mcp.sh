#!/bin/bash
# Install Deep Research MCP Server for Claude Code

set -e

echo "Installing Deep Research MCP Server..."

# Get the absolute path to this directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Claude Code MCP config file location
MCP_CONFIG="$HOME/.config/claude-code/mcp.json"

# Create config directory if it doesn't exist
mkdir -p "$(dirname "$MCP_CONFIG")"

# Check if config file exists
if [ ! -f "$MCP_CONFIG" ]; then
    echo "Creating new MCP configuration file..."
    echo '{"mcpServers":{}}' > "$MCP_CONFIG"
fi

# Update the mcp-config.json with actual paths
sed "s|/home/user/deer-flow/deep-research-api|$DIR|g" "$DIR/mcp-config.json" > "$DIR/mcp-config.resolved.json"

# Merge with existing config using Python
python3 << EOF
import json
import sys

# Read existing config
with open('$MCP_CONFIG', 'r') as f:
    existing_config = json.load(f)

# Read new server config
with open('$DIR/mcp-config.resolved.json', 'r') as f:
    new_config = json.load(f)

# Merge configs
if 'mcpServers' not in existing_config:
    existing_config['mcpServers'] = {}

existing_config['mcpServers']['deep-research'] = new_config['mcpServers']['deep-research']

# Write updated config
with open('$MCP_CONFIG', 'w') as f:
    json.dump(existing_config, f, indent=2)

print("MCP server configuration updated successfully!")
EOF

# Clean up temporary file
rm "$DIR/mcp-config.resolved.json"

echo ""
echo "✓ Deep Research MCP Server installed!"
echo ""
echo "Configuration added to: $MCP_CONFIG"
echo ""
echo "Next steps:"
echo "1. Install dependencies: cd $DIR && pip install -e ."
echo "2. Configure environment: cp .env.example .env && edit .env"
echo "3. Start the API server: python -m api.main"
echo "4. Restart Claude Code to load the MCP server"
echo ""
echo "Available tools in Claude Code:"
echo "  - deep_research: Comprehensive multi-agent research"
echo "  - quick_research: Fast research with fewer steps"
