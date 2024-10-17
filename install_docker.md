# Install Docker and Docker-Compose

To install Docker and Docker Compose on Ubuntu-based instance.

Step-by-Step Installation of Docker and Docker Compose

### 1. Update Your Package Manager

Before installing Docker, update your package list and upgrade your packages.

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Prerequisites

Install required packages for Docker and Docker Compose.

```bash
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
```

### 3. Add Docker’s Official GPG Key

Add Docker's official GPG key for verifying the installation packages.

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

### 4. Add Docker’s Repository

Add the Docker APT repository to your system.

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 5. Install Docker Engine

Now, update the package manager again and install Docker.

```bash
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io -y
```

### 6. Start and Enable Docker Service

After installation, start the Docker service and enable it to run on startup.

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

Verify that Docker is running:

```bash
sudo systemctl status docker
```

### 7. Add Your User to the Docker Group (Optional)

If you want to run Docker commands without using sudo, add your user to the Docker group.

```bash
sudo usermod -aG docker $USER
```

Log out and back in again for the group membership to take effect.

### 8.  Install Docker Compose

First, download the 2.29.6 version of Docker Compose. Check the actual link for downloading here: `https://docs.docker.com/compose/install/standalone/`

```bash
sudo curl -SL https://github.com/docker/compose/releases/download/v2.29.6/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
```

Apply executable permissions to the binary.

```bash
sudo chmod +x /usr/local/bin/docker-compose
```

### 9.  Verify Docker Compose Installation

Check the installed version of Docker Compose.

```bash
docker-compose --version
```

### 10.  Reboot the Ubuntu Instance (Optional)

To ensure that all changes, especially group membership changes, take effect, you can reboot your Ubuntu instance.

```bash
sudo reboot
```

After Reboot:

SSH back into the instance and verify that both Docker and Docker Compose are properly installed and working.
You are now ready to use Docker and Docker Compose on your Ubuntu instance!