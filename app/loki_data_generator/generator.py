import yaml
import os
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler
# from loki_logger_handler.formatters.logger_formatter import LoggerFormatter
from loguru import logger
import threading
import time
import random
import string
import datetime
import logging

class LokiDataGenerator:
    def __init__(self):
        self.config = self.get_config()
        self.threads = []
        self.running = False
        logger.info("Configuration loaded")
        
    def run(self):
        logger.info("Loki Data Generator started")
        self.running = True
        
        # Create threads for each target and stream combination
        for target in self.config.get('loki_targets', []):
            target_name = target.get('name', 'unknown')
            logger.info(f"Setting up target: {target_name}")
            
            # Create LokiLoggerHandler for this target
            loki_handler = self._create_loki_handler(target)
            
            # Create threads for each stream in this target
            for stream in target.get('streams', []):
                stream_name = stream.get('name', 'unknown')
                thread_name = f"{target_name}_{stream_name}"
                
                thread = threading.Thread(
                    target=self._stream_worker,
                    args=(target, stream, loki_handler),
                    name=thread_name,
                    daemon=True
                )
                thread.start()
                self.threads.append(thread)
                logger.info(f"Started thread: {thread_name}")

        # Report to DEBUG log the number of threads started
        logger.debug(f"Number of threads started: {len(self.threads)}")

        # Wait for all threads to complete
        for thread in self.threads:
            thread.join()
        
    def stop(self):
        logger.info("Loki Data Generator stopping...")
        self.running = False
        
        # Wait for all threads to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        logger.info("Loki Data Generator stopped")
        
    def __del__(self):
        logger.info("Loki Data Generator destroyed")
        
    def __str__(self):
        return "Loki Data Generator"
        
    def __repr__(self):
        return "LokiDataGenerator()"
        
    def __eq__(self, other):
        return self.config == other.config

    @staticmethod
    def get_config():
        if "LDG_CONFIG" in os.environ:
            path = os.environ["LDG_CONFIG"]
        else:
            path = "config.yaml"

        logger.debug(
            "Reading configuration from {}".format(path)
        )

        # Read configuration from file
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        return config

    def _create_loki_handler(self, target):
        """Create a LokiLoggerHandler for the given target configuration."""
        target_name = target.get('name', 'unknown')
        host = target.get('host', 'localhost')
        port = target.get('port', 3100)
        auth_enabled = target.get('auth_enabled', True)
        protocol = target.get('protocol', 'https')
        username = target.get('username')
        password = target.get('password')
        tenant = target.get('tenant')
        source = target.get('source', 'loki_data_generator')
        
        if auth_enabled:
            url = "{}://{}:{}@{}:{}/loki/api/v1/push".format(protocol, username, password, host, port)
        else:
            url = "{}://{}:{}/loki/api/v1/push".format(protocol, host, port)

        # Create formatter
        # formatter = LoggerFormatter()
        
        # Create handler
        handler = LokiLoggerHandler(
            url=url,
            labels={"tenant": tenant, "source": source},
            label_keys={},
            timeout=10,
            enable_self_errors=True
            # default_formatter=formatter
        )
        handler.setLevel(logging.DEBUG)
        
        logger.info(f"Created Loki handler for target: {target_name}")
        logger.debug(f"Target URL: {url}")
        logger.debug(f"Loki handler: {handler}")

        return handler

    def _stream_worker(self, target, stream, loki_handler):
        """Worker method for each stream thread."""
        target_name = target.get('name', 'unknown')
        stream_name = stream.get('name', 'unknown')
        thread_name = f"{target_name}_{stream_name}"
        
        # Combine target and stream labels
        labels = {}
        labels.update(target.get('labels', {}))
        labels.update(stream.get('labels', {}))
        
        logger.info(f"Stream worker {thread_name} started with labels: {labels}")
        
        try:
            while self.running:
                # Process each message template in the stream
                for message_config in stream.get('messages', []):
                    if not self.running:
                        break
                        
                    template = message_config.get('template', '')
                    level_name = message_config.get('level', 'INFO')
                    level = getattr(logging, level_name.upper(), logging.INFO)
                    probability = message_config.get('probability', 1.0)
                    
                    # Check probability
                    if random.random() > probability:
                        continue
                    
                    # Generate message
                    message = self._generate_message(template, labels)
                    
                    logger.debug(f"Loki handler: {loki_handler}")
                    logger.debug(f"Sent message to Loki: {message}")
                    logger.debug(f"Labels: {labels}")
                    logger.debug(f"Level: {level}")
                    logger.debug(f"Probability: {probability}")
                    logger.debug(f"Template: {template}")

                    # Send to Loki
                    self._send_to_loki(loki_handler, message, level, labels)
                    
                    # Small delay to prevent overwhelming
                    time.sleep(stream.get('pause_between_messages', 0.1))
                
                # Sleep between message cycles
                time.sleep(stream.get('sleep_between_cycles', 1))
                
        except Exception as e:
            logger.error(f"Error in stream worker {thread_name}: {e}")
        finally:
            logger.info(f"Stream worker {thread_name} finished")

    def _generate_message(self, template, labels):
        """Generate a message from template with dynamic content."""
        # Replace placeholders in template
        message = template
        
        # Add timestamp
        timestamp = datetime.datetime.now().isoformat()
        message = message.replace('{timestamp}', timestamp)
        
        # Add random content
        message = message.replace('{random_string}', ''.join(random.choices(string.ascii_letters, k=8)))
        message = message.replace('{random_number}', str(random.randint(1, 1000)))
        
        # Add label values
        for key, value in labels.items():
            message = message.replace(f'{{{key}}}', str(value))
        
        return message

    def _send_to_loki(self, loki_handler, message, level, labels):
        """Send message to Loki using the handler."""
        try:
            # Create log record
            record = logging.LogRecord(
                name='loki_data_generator',
                level=level,
                pathname='loki_data_generator',
                lineno=0,
                msg=message,
                args=(),
                exc_info=None,
                func=None,
                sinfo=None,
                labels=labels
            )
            # record = {
            #     'msg': message,
            #     'levelname': level,
            #     'labels': labels,
            #     'created': time.time()
            # }
            
            # Report details about loki_handler
            logger.debug(f"Loki handler: {loki_handler}")

            # Report details of the record
            logger.debug(f"Sending record to Loki: {record}")

            # Send to Loki
            loki_handler.emit(record)
            
        except Exception as e:
            logger.error(f"Failed to send message to Loki: {e}")
