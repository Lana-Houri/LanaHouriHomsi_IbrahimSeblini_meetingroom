# Load Balancer Configuration

This directory contains load balancing configurations for HAProxy and Nginx.

## HAProxy Configuration

The `haproxy.cfg` file configures HAProxy for load balancing across microservices.

### Features:
- Round-robin load balancing
- Health checks for all services
- SSL/TLS support
- Statistics dashboard on port 8404
- Automatic failover to backup servers

### Usage:

1. Install HAProxy:
```bash
sudo apt-get update
sudo apt-get install haproxy
```

2. Copy configuration:
```bash
sudo cp haproxy.cfg /etc/haproxy/haproxy.cfg
```

3. Start HAProxy:
```bash
sudo systemctl start haproxy
sudo systemctl enable haproxy
```

4. Access statistics:
- URL: http://localhost:8404/stats
- Username: admin
- Password: admin

## Nginx Configuration

The `nginx.conf` file configures Nginx for load balancing across microservices.

### Features:
- Least connections load balancing
- Rate limiting
- Health checks
- SSL/TLS support
- Connection keep-alive

### Usage:

1. Install Nginx:
```bash
sudo apt-get update
sudo apt-get install nginx
```

2. Copy configuration:
```bash
sudo cp nginx.conf /etc/nginx/sites-available/meetingroom
sudo ln -s /etc/nginx/sites-available/meetingroom /etc/nginx/sites-enabled/
```

3. Test configuration:
```bash
sudo nginx -t
```

4. Start Nginx:
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Docker Compose Integration

To use with Docker Compose, add load balancer services:

```yaml
  haproxy:
    image: haproxy:latest
    ports:
      - "80:80"
      - "8404:8404"
    volumes:
      - ./load_balancer/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
    depends_on:
      - users-service
      - rooms-service
      - bookings-service
      - reviews-service
    networks:
      - meetingroom-network

  nginx:
    image: nginx:latest
    ports:
      - "8080:80"
    volumes:
      - ./load_balancer/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - users-service
      - rooms-service
      - bookings-service
      - reviews-service
    networks:
      - meetingroom-network
```

## Load Balancing Algorithms

### HAProxy:
- **roundrobin**: Distributes requests evenly (default)
- **leastconn**: Routes to server with fewest connections
- **source**: Routes based on client IP

### Nginx:
- **round-robin**: Default, distributes evenly
- **least_conn**: Routes to server with fewest connections
- **ip_hash**: Routes based on client IP

## Health Checks

Both configurations include health check endpoints:
- `/health` - Service health status
- Automatic removal of unhealthy servers
- Automatic re-addition when servers recover

## Notes

- Update server names and ports to match your Docker Compose service names
- Configure SSL certificates for production use
- Adjust rate limits based on your requirements
- Monitor statistics dashboards for performance metrics

