# Full Stack Application Structure with Docker

## Overview
This document outlines the structure and best practices for creating a full stack application using Docker with separate containers for frontend, backend, and database components.

## Project Structure
```
full-stack-app/
├── client/                 # Frontend application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── server/                 # Backend application
│   ├── src/
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── routes/
│   │   └── middleware/
│   ├── package.json
│   ├── .env.example
│   └── Dockerfile
├── database/               # Database configuration (MongoDB)
│   └── init.js
├── docker-compose.yml
└── README.md
```

## Components

### Client (Frontend)
- Built with React, Vue, or Angular
- Communicates with backend API through HTTP requests
- Uses environment variables for API endpoints

### Server (Backend)
- Node.js application using Express framework
- MongoDB database integration with Mongoose
- API routes and controllers for handling requests
- Environment configuration handling

### Database
- MongoDB container with persistent data storage
- Initialization scripts for setup
- Connection management through environment variables

## Docker Architecture

### docker-compose.yml
```yaml
version: '3.8'
services:
  frontend:
    build: ./client
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - app-network
  
  backend:
    build: ./server
    ports:
      - "3001:3001"
    environment:
      - MONGO_URI=mongodb://database:27017/myapp
    depends_on:
      - database
    networks:
      - app-network
  
  database:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  mongodb_data:
```

### Environment Configuration (.env)
For backend:
```
MONGO_URI=mongodb://database:27017/myapp
PORT=3001
NODE_ENV=development
```

## Best Practices

1. **Separation of Concerns:**
   - Each component runs in its own container
   - Clear boundaries between frontend, backend, and database

2. **Environment Variables:**
   - Use .env files for configuration
   - Sensitive data should be passed via environment variables

3. **Network Configuration:**
   - Use custom Docker networks for isolation
   - Containers communicate through defined ports

4. **Volume Management:**
   - Persistent volumes for database data
   - Proper backup strategies

5. **Dockerfile Optimization:**
   - Multi-stage builds where appropriate
   - Minimal base images
   - Efficient layer caching

6. **Health Checks:**
   - Implement health checks for each service
   - Monitoring and logging capabilities

## Deployment Process

1. Build frontend container with production-ready files
2. Build backend container with optimized dependencies
3. Start database container with persistent volume
4. Use docker-compose to orchestrate all containers
5. Configure reverse proxy (if needed) with Nginx

## Troubleshooting

1. **Container Communication Issues:**
   - Check network configuration in docker-compose.yml
   - Verify service names are correctly referenced

2. **Database Connection Failures:**
   - Ensure MongoDB container is up and running
   - Validate connection string format

3. **Port Conflicts:**
   - Check if ports are already in use
   - Modify port mappings in docker-compose.yml