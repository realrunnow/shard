#!/usr/bin/env python3
"""
Test runner for the Shard parser.
Run this script to execute all the tests.
"""

import unittest
import sys
import os
import logging
import logging.handlers
from datetime import datetime
import inspect

# Add the tests directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all the test modules
from tests.test_lexer import LexerTestCase
from tests.test_expression_parser import ExpressionParserTestCase
from tests.test_statement_parser import StatementParserTestCase
from tests.test_parser_full import FullParserTestCase
from tests.test_encoders import EncodersTestCase

def setup_logging(log_to_file=False, log_level=logging.DEBUG):
    """Setup logging for tests"""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Always add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # Add file handler if requested
    if log_to_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(logs_dir, f"test_{timestamp}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)
        logging.info(f"Logging to file: {log_file}")
        return log_file
    
    return None

class LogTestResult(unittest.TextTestResult):
    """Test result class that logs detailed information"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_test = None
        self.log_buffer = []
        
    def startTest(self, test):
        super().startTest(test)
        self.current_test = test
        self.log_buffer = []
        
        # Create a test-specific buffer handler to capture logs during the test
        self.buffer_handler = logging.handlers.MemoryHandler(capacity=1024*10, 
                                                           target=None)
        root_logger = logging.getLogger()
        root_logger.addHandler(self.buffer_handler)
        
        # Log basic test information
        test_name = test.id().split('.')[-1]
        test_class = test.id().split('.')[-2]
        logging.info(f"Starting {test_class}.{test_name}")
        
        # Try to get the test docstring for more context
        test_method = getattr(test, test_name)
        if test_method.__doc__:
            logging.info(f"Test description: {test_method.__doc__.strip()}")
    
    def addSuccess(self, test):
        super().addSuccess(test)
        
        # Log the captured output
        self._flush_logs()
        logging.info(f"Success: {test.id()}")
    
    def addError(self, test, err):
        super().addError(test, err)
        
        # Log the captured output and error
        self._flush_logs()
        logging.error(f"Error in {test.id()}: {err[1]}")
        
        # Log the traceback
        import traceback
        logging.error(f"Traceback: {traceback.format_exception(*err)}")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        
        # Log the captured output and failure
        self._flush_logs()
        logging.error(f"Failure in {test.id()}: {err[1]}")
        
        # Log the traceback
        import traceback
        logging.error(f"Traceback: {traceback.format_exception(*err)}")
    
    def _flush_logs(self):
        """Flush the buffer of logs captured during the test"""
        if hasattr(self, 'buffer_handler'):
            # Remove the handler to prevent further logging to this buffer
            root_logger = logging.getLogger()
            root_logger.removeHandler(self.buffer_handler)
            
            # Flush all buffered records
            for record in self.buffer_handler.buffer:
                # Only log records at DEBUG level or higher
                if record.levelno >= logging.DEBUG:
                    logging.info(f"Test log: {record.getMessage()}")
            
            self.buffer_handler.buffer = []

    def tearDown(self):
        """Ensure the buffer handler is removed after the test"""
        root_logger = logging.getLogger()
        if hasattr(self, 'buffer_handler') and self.buffer_handler in root_logger.handlers:
            root_logger.removeHandler(self.buffer_handler)
        self.current_test = None
        self.log_buffer = []

class LogTestRunner(unittest.TextTestRunner):
    """Test runner that uses LogTestResult"""
    
    def _makeResult(self):
        return LogTestResult(self.stream, self.descriptions, self.verbosity)

def run_tests(verbosity=2, log_to_file=False):
    """Run all the tests"""
    log_file = setup_logging(log_to_file=log_to_file)
    
    # Log start of test run
    logging.info("Starting test run")
    
    # Create test loader and suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all the test cases
    suite.addTests(loader.loadTestsFromTestCase(LexerTestCase))
    suite.addTests(loader.loadTestsFromTestCase(ExpressionParserTestCase))
    suite.addTests(loader.loadTestsFromTestCase(StatementParserTestCase))
    suite.addTests(loader.loadTestsFromTestCase(FullParserTestCase))
    suite.addTests(loader.loadTestsFromTestCase(EncodersTestCase))
    
    # Run the tests
    runner = LogTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Log test run completion
    logging.info(f"Test run completed: {result.testsRun} tests run")
    logging.info(f"Failures: {len(result.failures)}, Errors: {len(result.errors)}")
    
    if log_file:
        print(f"\nDetailed test logs written to: {log_file}")
    
    return result

if __name__ == "__main__":
    verbosity = 2
    log_to_file = False
    
    # Parse command line arguments
    for arg in sys.argv[1:]:
        if arg in ('-v', '--verbose'):
            verbosity = 3
        elif arg in ('-l', '--log'):
            log_to_file = True
    
    result = run_tests(verbosity=verbosity, log_to_file=log_to_file)
    
    # Exit with non-zero code if tests failed
    if not result.wasSuccessful():
        sys.exit(1) 