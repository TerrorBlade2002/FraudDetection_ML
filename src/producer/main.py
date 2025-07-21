import json
import os
import random
import signal
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from random import randint

from confluent_kafka import Producer
from dotenv import load_dotenv
import logging
from faker import Faker
from jsonschema import FormatChecker, validate, ValidationError

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    level = logging.INFO
)

logger = logging.getLogger(__name__)

load_dotenv(dotenv_path='/app/.env')

fake = Faker()

# JSON Schema for transaction validation
TRANSACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "transaction_id": {"type": "string"},
        "user_id": {"type": "number", "minimum": 1000, "maximum": 9999},
        "amount": {"type": "number", "minimum": 0.01, "maximum": 100000},
        "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
        "merchant": {"type": "string"},
        "timestamp": {
            "type": "string",
            "format": "date-time"
        },
        "location": {"type": "string", "pattern": "^[A-Z]{2}$"},
        "is_fraud": {"type": "integer", "minimum": 0, "maximum": 1}
    },
    "required": ["transaction_id", "user_id", "amount", "currency", "timestamp", 'is_fraud']
}

class TransactionProducer():

    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.kafka_username = os.getenv('KAFKA_USERNAME')
        self.kafka_password = os.getenv('KAFKA_PASSWORD')
        self.topic = os.getenv('KAFKA_TOPIC', 'transactions')
        self.running = False

        #confluent kafka config
        self.producer_config = {
            'bootstrap.servers': self.bootstrap_servers,
            'client.id': 'transaction-producer',
            'compression.type': 'gzip',
            'linger.ms': '5',
            'batch.size': 16384,
        }

        if self.kafka_username and self.kafka_password:
            self.producer_config.update({
                'security.protocol': 'SASL_SSL',
                'sasl.mechanism': 'PLAIN',
                'sasl.username': self.kafka_username,
                'sasl.password': self.kafka_password,
            })

        else:
            self.producer_config['security.protocol'] = 'PLAINTEXT'

        try:
            self.producer = Producer(self.producer_config)
            logger.info('Confluent Kafka Producer initialized successfully')

        except  Exception as e:

            logger.error(f"Failed to initialize Confluent Kafka Producer: {str(e)}")
            raise e

        #Handle suspicious users!
        self.compromised_users = set(random.sample(range(1000, 9999), 50))  #0.5% of users
        self.high_risk_merchants = ['QuickCash', 'GlobalDigital', 'FastMoneyX']  #sample
        self.fraud_pattern_weights ={
            'account_takeover' : 0.4,  #40% of fraud cases
            'card_testing' : 0.3,   #weights assigned to each according to what's typically seen
            'merchant_collusion' : 0.2,
            'geo_anomaly' : 0.1
        }

        #Configure graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Validate transaction against JSON schema with date-time checking"""
        try:
            validate(
                instance=transaction,
                schema=TRANSACTION_SCHEMA,
                format_checker=FormatChecker()
            )
            return True
        except ValidationError as e:
            logger.error(f"Invalid transaction: {e.message}")
            return False

    def generate_transaction(self) -> Optional[Dict[str, Any]]:

        transaction={
            'transaction_id': fake.uuid4(),
            'user_id': random.randint(1000, 9999),
            'amount': round(fake.pyfloat(min_value = 0.01, max_value = 10000), 2),
            'currency': 'USD',
            'merchant': fake.company(),
            'timestamp': (datetime.now(timezone.utc) +
                          timedelta(seconds = random.randint(-300, 3000))).isoformat(),
            'location': fake.country_code(),
            'is_fraud': 0
        }

        is_fraud = 0
        amount = transaction['amount']
        user_id = transaction['user_id']
        merchant = transaction['merchant']

        #Pattern 1: Account takeover (0.6% of total transactions)
        if user_id in self.compromised_users and amount > 500:
            if random.random() < 0.3:      #30% chance of fraud in compromised accounts
                is_fraud = 1
                transaction['amount'] = random.uniform(500, 5000)   #Typical takeover amounts
                transaction['merchant'] = random.choice(self.high_risk_merchants)

        #Pattern 2: Card testing (0.45% of total)
        if not is_fraud and amount < 2.0:
            #Simulate rapid small transactions (every 10th user in testing mode)
            if user_id % 1000 == 0 and random.random() < 0.25:
                is_fraud = 1
                transaction['amount'] = round(random.uniform(0.01, 2), 2)
                transaction['location'] = 'US'  #consistent location

        #Pattern 3: Merchant collusion (0.3% of total)
        if not is_fraud and merchant in self.high_risk_merchants:
            if amount > 300 and random.random() < 0.15:
                is_fraud = 1
                transaction['amount'] = random.uniform(300, 1500)

        # Pattern 4: Geographic anomalies (0.15% of total)
        if not is_fraud:
            # Simulate location change without actual state tracking
            if user_id % 500 == 0 and random.random() < 0.1:
                is_fraud = 1
                transaction['location'] = random.choice(['CN', 'RU', 'NG'])  # High-risk countries

        # Baseline random fraud (0.1-0.3%)
        if not is_fraud and random.random() < 0.002:
            is_fraud = 1
            transaction['amount'] = random.uniform(100, 2000)

        # Ensure final fraud rate stays between 1-2%
        transaction['is_fraud'] = is_fraud if random.random() < 0.985 else 0

        # Validate modified transaction
        if self.validate_transaction(transaction):
            return transaction
        return None

    def delivery_report(self, err, msg):

        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')
            
    def send_transaction(self) -> bool:

        try:
            transaction = self.generate_transaction()
            if not transaction:
                return False

            self.producer.produce(
                self.topic,
                key = transaction['transaction_id'],
                value = json.dumps(transaction),
                callback = self.delivery_report
            )

            self.producer.poll(0)     #trigger callbacks
            return True

        except Exception as e:
            logger.error(f'Error producing message {str(e)}')
            return False



    def run_continuous_production(self, interval: float=0.0):
        """Run continuous message production with graceful shutdown"""
        self.running = True
        logger.info('Starting producer for topic %s...', self.topic)

        try:
            while self.running:
                if self.send_transaction():
                    time.sleep(interval)

        finally:
            self.shutdown()



    def shutdown(self, signum=None, frame=None):
        #Graceful shutdown
        if self.running:
            logger.info('Initiating shutdown...')
            self.running = False

            if self.producer:
                self.producer.flush(timeout=30) # <-- Ensure flush() is called
                self.producer.close()
            logger.info('Producer Stopped')


if __name__ == "__main__":

    producer = TransactionProducer()
    producer.run_continuous_production()
