# Docker Quickstart

This project provides a simple way to start a Docker container in headless (detached) mode using a quickstart script. The container will run in the background and can be monitored through the Docker dashboard.

## Project Structure

```
docker-quickstart
├── scripts
│   └── quickstart_script.sh
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Quickstart Script

The `scripts/quickstart_script.sh` script is designed to start the Docker container in detached mode. To run the script, execute the following command in your terminal:

```bash
bash scripts/quickstart_script.sh
```

## Docker Setup

### Dockerfile

The `Dockerfile` contains the necessary instructions to build the Docker image for this project. It specifies the base image, copies required files, installs dependencies, and sets up the environment.

### Docker Compose

The `docker-compose.yml` file defines the services, networks, and volumes for the Docker application. It allows you to easily manage multi-container Docker applications.

## Usage

1. Ensure you have Docker and Docker Compose installed on your machine.
2. Build the Docker image using the following command:

   ```bash
   docker-compose build
   ```

3. Start the Docker container in detached mode by running the quickstart script:

   ```bash
   bash scripts/quickstart_script.sh
   ```

4. Check the Docker dashboard to see the running container.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.