import logging
import re
from typing import Optional, Tuple, Dict, Any

class PipelineLogger:
    def __init__(self,
                 name: Optional[str] = None,
                 default_formatter: Optional[logging.Formatter] = None,
                 verbosity: int = 0,
                 *handlers: logging.Handler,
                 **handler_kwargs: Dict[str, Optional[Any]]) -> None:
        """
        Initialize a PipelineLogger instance.

        Args:
            name (Optional[str]): The name of the logger. If None, uses the base logger.
            default_formatter (Optional[logging.Formatter]): The default formatter for handlers. 
                If None, a default formatter is created.
            verbosity (int): The verbosity level of the logger. Defaults to 0, only ERROR and CRITICAL are logged.
            *handlers: Variable length argument list of optional logging.Handler objects.
            **handler_kwargs: Arbitrary keyword arguments for additional handlers.
                Values can be None.

        Raises:
            ValueError: If an invalid handler is provided.
        """
        base_logger = logging.getLogger(__name__)
        self.logger = base_logger.getChild(self.safe_logger_name(name)) if name else base_logger
        self.set_logging_config(verbosity, default_formatter, *handlers, **handler_kwargs)

    def get_logger(self) -> logging.Logger:
        """
        Retrieve the logger instance associated with this PipelineLogger.

        Returns:
            logging.Logger: The configured logger instance.
        """
        return self.logger
    
    def safe_logger_name(self, name: str) -> str:
        """
        Sanitize the logger name by replacing invalid characters with underscores.

        This method checks if the logger name contains invalid characters and replaces them with
        underscores. It also checks if the resulting name already exists in the logger dictionary.
        If the name does exist a reference to the existing logger will be returned.

        Args:
            name (str): The proposed logger name.

        Returns:
            str: The sanitized logger name.

        Note:
            This method prints warnings to the console if the name is modified or already exists.
        """
        safe_name = re.sub(r'[^0-9a-zA-Z_]', '_', name)
        if safe_name != name:
            print(f"Logger name {name} was coerced into {safe_name} because it contained invalid characters.")
        if safe_name in logging.getLogger().manager.loggerDict:
            print(f"Logger name {name} already exists. Returning existing logger.")
        return safe_name
    
    def set_logging_config(self,
                           verbosity: int,
                           default_formatter: logging.Formatter,
                           *handlers: logging.Handler,
                           **handler_kwargs: Dict[str, Optional[Any]]) -> None:
        """
        Configure the logger with the specified verbosity, formatter, and handlers.

        This method sets up the logger with the given configuration. It removes any existing
        handlers, sets the log level based on the verbosity, and adds new handlers as specified.

        Args:
            verbosity (int): An integer representing the desired verbosity level.
                Use 0 for ERROR, 1 for WARNING, 2 for INFO, 3 or higher for DEBUG.
            default_formatter (Optional[logging.Formatter]): The default formatter to use for
                handlers that don't have a specific formatter configured. If None, a default
                formatter with the format '%(asctime)s - %(levelname)s - %(message)s' is used.
            *handlers (logging.Handler): Variable length argument list of pre-configured
                logging.Handler objects to be added to the logger.
            **handler_kwargs (Dict[str, Any]): Keyword arguments representing additional
                handlers to be created and added. The key should be the handler class name
                (e.g., 'FileHandler'), and the value should be a dictionary of arguments
                for that handler's constructor.

        Raises:
            ValueError: If an invalid handler object is provided in *handlers,
                        if an unknown handler type is specified in **handler_kwargs,
                        or if an invalid formatter configuration is provided.

        Note:
            - If no handlers are provided (either through *handlers or **handler_kwargs),
            a default StreamHandler will be added.
            - Handlers can have their own formatter specified in the handler_kwargs by
            including a 'formatter' key. This can be a logging.Formatter object,
            a format string, or a dictionary of formatter parameters.
            - Existing handlers on the logger will be removed before adding new ones.

        Example:
            set_logging_config(
                2,
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
                logging.StreamHandler(),
                FileHandler={'filename': 'app.log', 'mode': 'a'},
                RotatingFileHandler={'filename': 'rotating.log', 'maxBytes': 1024, 'backupCount': 3}
            )
        """
        level = self.get_level(verbosity)
        self.logger.setLevel(level)

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        if default_formatter is None:
            default_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Add custom handlers if provided

        for handler in handlers:
            if isinstance(handler, logging.Handler):
                if not handler.formatter:
                    handler.setFormatter(default_formatter)
                self.logger.addHandler(handler)
            else:
                raise ValueError(f"Positional argument {handler} is not a valid logging.Handler object.")

        for handler_name, handler_config in handler_kwargs.items():
            if hasattr(logging, handler_name):
                formatter_config = handler_config.pop('formatter', None)
                handler_class = getattr(logging, handler_name)
                handler = handler_class(**handler_config)

                if formatter_config:
                    if isinstance(formatter_config, logging.Formatter):
                        handler.setFormatter(formatter_config)
                    elif isinstance(formatter_config, str):
                        handler.setFormatter(logging.Formatter(formatter_config))
                    elif isinstance(formatter_config, dict):
                        handler.setFormatter(logging.Formatter(**formatter_config))
                    else:
                        raise ValueError(f"Invalid formatter configuration for {handler_name}")
                else:
                    handler.setFormatter(default_formatter)

                self.logger.addHandler(handler)

            else:
                raise ValueError(f"Unknown handler type {handler_name}")
        
        # If no handlers were added, add a default StreamHandler
        if not self.logger.handlers:  
            handler = logging.StreamHandler()
            handler.setFormatter(default_formatter)
            self.logger.addHandler(handler)

    def set_verbosity(self, verbosity: int) -> None:
        """
        Set the verbosity level of the PipelineLogger instance.

        This method adjusts the logging level of the logger based on the provided verbosity.

        Args:
            verbosity (int): The desired verbosity level.
                0 or less: ERROR and CRITICAL
                1: WARNING
                2: INFO
                3 or more: DEBUG

        Note:
            This method modifies the logger in-place and does not return a new logger.
        """
        self.logger.setLevel(self.get_level(verbosity))

    @staticmethod
    def get_level(verbosity: int) -> int:
        """
        Convert verbosity level to corresponding logging level.

        Args:
            verbosity (int): The verbosity level.
                0 or less: ERROR
                1: WARNING
                2: INFO
                3 or more: DEBUG

        Returns:
            int: The corresponding logging level constant from the logging module.
                These are integers with special properties, typically:
                logging.ERROR (40)
                logging.WARNING (30)
                logging.INFO (20)
                logging.DEBUG (10)

        Example:
            >>> PipelineLogger.get_level(2)
            20  # This is logging.INFO
        """
        if verbosity == 1:
            return logging.WARNING
        elif verbosity == 2:
            return logging.INFO
        elif verbosity >= 3:
            return logging.DEBUG
        else:
            return logging.ERROR
