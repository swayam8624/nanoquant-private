#!/bin/bash
# Push both NanoQuant repositories to their remotes

echo "Setting up remote repositories..."
echo "Please make sure you've created empty repositories on GitHub/GitLab first"

# Public repository
echo "=== Public Repository (nanoquant-core) ==="
cd /Users/swayamsingal/Desktop/Programming/NanoQuant/public-repo/nanoquant-core

# Add remote (replace with your actual repository URL)
# git remote add origin https://github.com/yourusername/nanoquant-core.git

# Push to remote
# git push -u origin main

echo "Public repository ready for push (configure remote and uncomment lines above)"

# Private repository
echo "=== Private Repository (nanoquant-business) ==="
cd /Users/swayamsingal/Desktop/Programming/NanoQuant/private-repo

# Add remote (replace with your actual repository URL)
# git remote add origin https://github.com/yourusername/nanoquant-business.git

# Push to remote
# git push -u origin main

echo "Private repository ready for push (configure remote and uncomment lines above)"

echo "Setup complete!"