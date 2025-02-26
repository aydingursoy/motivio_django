# Motivio - Car Maintenance Tracker

Motivio is a user-friendly web application designed to help car owners track their vehicle's maintenance history and manage upcoming service needs through manual data entry.

## Features

- **Vehicle Profile Management**: Add and manage multiple vehicles with their details (make, model, year, VIN, etc.)
- **Maintenance Logging**: Keep records of all maintenance activities with service dates, costs, and receipts
- **Service Reminders**: Set custom reminders based on mileage or time intervals
- **Maintenance History**: View a complete timeline of all past services
- **Mileage Tracking**: Log mileage periodically to track usage patterns
- **Cost Estimates**: Get price estimates for maintenance services and hold providers accountable
- **Mobile-Friendly Interface**: Accessible on any device

## Tech Stack

- **Backend**: Django 4.2
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Database**: PostgreSQL (for production), SQLite (for development)
- **Deployment**: AWS (EC2, RDS, S3)
- **Additional Tools**: Celery, Redis, Gunicorn, Nginx

## Local Development Setup

### Prerequisites

- Python 3.9+
- pip
- virtualenv (recommended)
- Redis (for Celery)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/motivio.git
cd motivio
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Initialize the database with default data:
```bash
python initialize_data.py
```

7. Create a superuser:
```bash
python manage.py createsuperuser
```

8. Start the development server:
```bash
python manage.py runserver
```

9. (Optional) Start Celery worker for background tasks:
```bash
celery -A motivio_project worker -l info
```

10. (Optional) Start Celery beat for scheduled tasks:
```bash
celery -A motivio_project beat -l info
```

Visit http://localhost:8000 to access the application.

## Deploying to AWS

### Prerequisites

- AWS Account
- AWS CLI installed and configured
- Domain name (optional)

### Setting up AWS Infrastructure

#### 1. RDS (PostgreSQL Database)

1. Go to AWS RDS and create a new PostgreSQL database:
   - Choose PostgreSQL as the engine
   - Select the appropriate tier (t2.micro is sufficient for starting)
   - Configure storage (20GB is a good start)
   - Set up a master username and password
   - Make sure to save these credentials securely
   - Set the database to be publicly accessible for now

2. Note the database endpoint, username, password, and database name.

#### 2. S3 Bucket (Static and Media Files)

1. Go to AWS S3 and create a new bucket:
   - Choose a globally unique name
   - Choose the region closest to your users
   - Configure Block Public Access settings (unblock public access for static hosting)
   - Enable versioning if needed

2. Set up bucket policy to allow public read access:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

3. Create folders for 'static' and 'media' in the bucket.

#### 3. EC2 Instance (Web Server)

1. Go to AWS EC2 and launch a new instance:
   - Choose Ubuntu Server LTS (20.04 or newer)
   - Choose t2.micro for starters
   - Configure storage (8GB is usually sufficient)
   - Create or select an existing key pair for SSH access
   - Create a security group with the following rules:
     - SSH (Port 22) - Your IP or trusted IPs
     - HTTP (Port 80) - Anywhere
     - HTTPS (Port 443) - Anywhere

2. Allocate an Elastic IP and associate it with your instance.

### Deploying the Application

1. SSH into your EC2 instance:
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

2. Install required packages:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx redis-server
```

3. Clone the repository:
```bash
git clone https://github.com/your-username/motivio.git
cd motivio
```

4. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

5. Install dependencies:
```bash
pip install -r requirements.txt
pip install gunicorn
```

6. Create a `.env` file with production settings:
```
DEBUG=False
SECRET_KEY=your-very-secure-secret-key
ALLOWED_HOSTS=your-domain.com,your-ip-address

DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-rds-endpoint
DB_PORT=5432

AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

SITE_URL=https://your-domain.com
```

7. Run migrations and initialize data:
```bash
python manage.py migrate
python initialize_data.py
python manage.py createsuperuser
```

8. Collect static files:
```bash
python manage.py collectstatic
```

9. Configure Gunicorn:
Create a systemd service file for Gunicorn:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Add the following content:
```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/motivio
ExecStart=/home/ubuntu/motivio/venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/ubuntu/motivio/motivio.sock \
          motivio_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

10. Configure Celery:
Create a systemd service file for Celery worker:
```bash
sudo nano /etc/systemd/system/celery.service
```

Add the following content:
```
[Unit]
Description=Celery Worker
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/motivio
ExecStart=/home/ubuntu/motivio/venv/bin/celery -A motivio_project worker -l info
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Create a systemd service file for Celery beat:
```bash
sudo nano /etc/systemd/system/celerybeat.service
```

Add the following content:
```
[Unit]
Description=Celery Beat
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/motivio
ExecStart=/home/ubuntu/motivio/venv/bin/celery -A motivio_project beat -l info
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

11. Configure Nginx:
```bash
sudo nano /etc/nginx/sites-available/motivio
```

Add the following content:
```
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        proxy_pass https://your-s3-bucket.s3.amazonaws.com/static/;
    }
    
    location /media/ {
        proxy_pass https://your-s3-bucket.s3.amazonaws.com/media/;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/motivio/motivio.sock;
    }
}
```

Create a symbolic link to enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/motivio /etc/nginx/sites-enabled
```

12. Start all services:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl start celery
sudo systemctl enable celery
sudo systemctl start celerybeat
sudo systemctl enable celerybeat
sudo systemctl restart nginx
```

13. (Optional) Set up SSL with Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Troubleshooting

- Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`
- Check Gunicorn logs: `sudo journalctl -u gunicorn`
- Check Celery logs: `sudo journalctl -u celery`

## Maintenance and Updates

### Backing Up the Database

1. Create a backup script:
```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
PGPASSWORD=your-db-password pg_dump -h your-rds-endpoint -U your-db-user your-db-name > backup-$DATE.sql
aws s3 cp backup-$DATE.sql s3://your-backup-bucket/database-backups/
rm backup-$DATE.sql
```

2. Make it executable and add to crontab:
```bash
chmod +x backup.sh
crontab -e
```

Add this line to run backups daily at 2 AM:
```
0 2 * * * /home/ubuntu/motivio/backup.sh
```

### Updating the Application

1. SSH into your EC2 instance
2. Pull the latest changes:
```bash
cd motivio
git pull
```

3. Activate virtual environment and update dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. Run migrations if needed:
```bash
python manage.py migrate
```

5. Collect static files:
```bash
python manage.py collectstatic --noinput
```

6. Restart services:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celerybeat
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

This project was created as part of the ISI490 course by Grace Costello, Aydin Gursoy, and Noman Afzal.
