# Use an official Node runtime as a parent image
FROM node:18-slim

# Set the working directory in the container
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (Vite default)
EXPOSE 5173

# Start the application in dev mode
CMD ["npm", "run", "dev", "--", "--host"]
