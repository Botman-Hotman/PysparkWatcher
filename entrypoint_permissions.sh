#!/bin/bash

# Ensure the /app/imports directory exists and has correct permissions
chown -R appuser:appgroup /app/imports
chmod -R 775 /app/imports

# Set umask to allow group write permissions
umask 0002

# Execute the CMD
exec "$@"
