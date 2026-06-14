-- Create extra databases needed by services
CREATE DATABASE keycloak;
CREATE DATABASE langfuse;
GRANT ALL PRIVILEGES ON DATABASE keycloak TO wealthmesh;
GRANT ALL PRIVILEGES ON DATABASE langfuse TO wealthmesh;
