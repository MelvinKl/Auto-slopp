# Architecture Overview

This document provides a comprehensive overview of Auto-slopp's architecture, design principles, and component interactions.

## Table of Contents

1. [Design Principles](#design-principles)
2. [High-Level Architecture](#high-level-architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Component Interactions](#component-interactions)
6. [Extension Points](#extension-points)
7. [Security Considerations](#security-considerations)
8. [Scalability](#scalability)

## Design Principles

### 1. Pluggability

The system is designed around a pluggable worker architecture:

- **Abstract Base Classes**: All workers inherit from a common `Worker` interface
- **Dynamic Discovery**: Workers are discovered at runtime using Python's import system
- **Loose Coupling**: Components interact through well-defined interfaces
- **Extensibility**: New functionality can be added without modifying core code

### 2. Configuration-Driven

- **Environment Variables**: All configuration is externalized through environment variables
- **Pydantic Settings**: Type-safe configuration with validation
- **Default Values**: Sensible defaults for all settings
- **Runtime Overrides**: Command-line arguments can override configuration

### 3. Observability

- **Structured Logging**: Comprehensive logging with configurable levels
- **Telegram Integration**: Real-time notifications for critical events
- **Debug Mode**: Detailed logging for troubleshooting
- **Error Reporting**: Graceful error handling with detailed error messages

### 4. Modern Python

- **Python 3.14+**: Latest Python features and type hints
- **Async Support**: First-class support for async operations
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Package Management**: Modern dependency management with uv

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Auto-slopp                           │
├─────────────────────────────────────────────────────────────┤
│  CLI Interface (main.py)                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Argument    │  │ Logging     │  │ Settings    │         │
│  │ Parsing     │  │ Setup       │  │ Management  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  Execution Layer (executor.py)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Worker      │  │ Worker      │  │ Result      │         │
│  │ Discovery   │  │ Execution   │  │ Aggregation │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  Worker System (worker.py, workers/)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Base Worker │  │ Built-in    │  │ Custom      │         │
│  │ Interface   │  │ Workers     │  │ Workers     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  Integration Layer                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Telegram    │  │ Settings    │  │ Discovery    │         │
│  │ Handler     │  │ Manager     │  │ Utilities    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Main Entry Point (main.py)

The main module serves as the application's entry point and orchestrates initialization:

```python
def main() -> None:
    """Main entry point for Auto-slopp."""
    # 1. Parse command-line arguments
    args = parse_arguments()
    
    # 2. Load configuration
    settings = load_settings(args)
    
    # 3. Set up logging
    setup_logging(settings)
    
    # 4. Execute workers
    run_executor(settings)
```

**Responsibilities:**
- Command-line argument parsing
- Configuration loading and validation
- Logging system initialization
- Error handling and graceful shutdown

### 2. Executor (executor.py)

The executor manages worker discovery and execution:

```python
class Executor:
    """Discovers and executes worker implementations."""
    
    def __init__(self, search_path: Path):
        self.search_path = search_path
        self.workers: List[Type[Worker]] = []
    
    def discover_workers(self) -> List[Type[Worker]]:
        """Discover worker implementations dynamically."""
        
    def execute_workers(self, repo_path: Path) -> Dict[str, Any]:
        """Execute all discovered workers."""
```

**Responsibilities:**
- Dynamic worker discovery
- Worker instantiation and lifecycle management
- Execution coordination
- Result collection and aggregation

### 3. Worker Interface (worker.py)

The worker interface defines the contract for all automation tasks:

```python
class Worker(ABC):
    """Abstract base class for all worker implementations."""
    
    @abstractmethod
    def run(self, repo_path: Path) -> Any:
        """Execute the worker's automation task."""
        pass
```

**Design Considerations:**
- Simple, focused interface
- Path-based input for consistency
- Flexible return types for different use cases
- Abstract base class enforcement

### 4. Settings Management (settings/main.py)

Configuration management using Pydantic:

```python
class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Path configuration
    base_repo_path: Path = Field(default_factory=lambda: Path.cwd())
    
    # Execution configuration
    debug: bool = Field(default=False)
    executor_sleep_interval: float = Field(default=1.0)
    
    # Telegram configuration
    telegram_enabled: bool = Field(default=False)
    telegram_bot_token: Optional[str] = Field(default=None)
    telegram_chat_id: Optional[str] = Field(default=None)
```

**Features:**
- Type-safe configuration
- Environment variable mapping
- Validation and defaults
- Runtime overrides

### 5. Telegram Integration (telegram_handler.py)

Async logging handler for Telegram notifications:

```python
class TelegramHandler(logging.Handler):
    """Async logging handler for Telegram bot integration."""
    
    def __init__(self, **kwargs):
        # Initialize HTTP client and configuration
        
    def emit(self, record: logging.LogRecord) -> None:
        """Send log record to Telegram asynchronously."""
        
    def _send_message_async(self, record: logging.LogRecord) -> None:
        """Handle async message sending with retries."""
```

**Capabilities:**
- Async message sending
- Retry logic with exponential backoff
- HTML/Markdown formatting
- Rate limiting handling

## Data Flow

### 1. Initialization Flow

```
Start → Parse CLI Args → Load Settings → Setup Logging → Discover Workers → Ready
```

**Detailed Flow:**
1. **CLI Parsing**: Command-line arguments are parsed and validated
2. **Settings Loading**: Environment variables and settings files are loaded
3. **Logging Setup**: Logging handlers are configured (console + Telegram)
4. **Worker Discovery**: Python modules are scanned for Worker subclasses
5. **Ready State**: System is ready to execute tasks

### 2. Execution Flow

```
Execute → For Each Worker → Instantiate → Run → Collect Results → Aggregate → Return
```

**Detailed Flow:**
1. **Worker Iteration**: Each discovered worker is processed
2. **Instantiation**: Worker instances are created (with configuration if needed)
3. **Execution**: Worker.run() is called with repo_path
4. **Result Collection**: Individual worker results are collected
5. **Aggregation**: Results are aggregated into a unified response
6. **Error Handling**: Failed workers are logged but don't stop execution

### 3. Error Handling Flow

```
Error → Log Error → Send to Telegram → Continue Execution → Report Results
```

**Error Handling Strategy:**
- **Graceful Degradation**: Individual worker failures don't stop the system
- **Comprehensive Logging**: All errors are logged with context
- **Telegram Notifications**: Critical errors are sent to Telegram
- **Result Reporting**: Failed workers are marked in results

## Component Interactions

### 1. Main → Executor Interaction

```python
# main.py
def main():
    # Load settings
    settings = load_settings()
    
    # Create executor
    executor = Executor(search_path=settings.worker_search_path)
    
    # Execute workers
    results = executor.execute_workers(
        repo_path=settings.base_repo_path
    )
```

### 2. Executor → Worker Interaction

```python
# executor.py
def execute_workers(self, repo_path: Path):
    results = {}
    
    for worker_class in self.workers:
        try:
            # Instantiate worker
            worker = worker_class()
            
            # Execute worker
            result = worker.run(repo_path)
            results[worker_class.__name__] = result
            
        except Exception as e:
            # Handle worker failure
            results[worker_class.__name__] = {"error": str(e)}
    
    return results
```

### 3. Settings → Component Interaction

```python
# Settings are injected into components
class TelegramHandler:
    def __init__(self, settings: Settings):
        self.enabled = settings.telegram_enabled
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id

# Components access settings globally
from settings.main import settings

def setup_logging():
    if settings.telegram_enabled:
        # Setup Telegram handler
```

## Extension Points

### 1. Custom Workers

Create new workers by inheriting from the base class:

```python
class CustomWorker(Worker):
    """Custom worker for specific automation task."""
    
    def __init__(self, custom_config: str = "default"):
        self.custom_config = custom_config
    
    def run(self, repo_path: Path) -> Dict[str, Any]:
        # Custom automation logic
        return {
            "custom_result": "success",
            "config_used": self.custom_config
        }
```

### 2. Custom Settings

Extend settings for worker-specific configuration:

```python
class CustomSettings(Settings):
    """Extended settings for custom workers."""
    
    custom_worker_enabled: bool = Field(default=False)
    custom_worker_config: str = Field(default="default")
    custom_worker_timeout: float = Field(default=30.0)
```

### 3. Custom Logging Handlers

Add custom logging handlers:

```python
class CustomLogHandler(logging.Handler):
    """Custom logging handler for specific needs."""
    
    def emit(self, record: logging.LogRecord):
        # Custom logging logic
        pass

# Integration in main.py
def setup_logging():
    # Add custom handler
    custom_handler = CustomLogHandler()
    logging.getLogger().addHandler(custom_handler)
```

### 4. Plugin System

Implement a plugin registry for dynamic loading:

```python
class PluginRegistry:
    """Registry for worker plugins."""
    
    def __init__(self):
        self._plugins = {}
    
    def register(self, name: str, worker_class: Type[Worker]):
        self._plugins[name] = worker_class
    
    def load_plugins(self, plugin_dir: Path):
        # Load plugins from directory
        pass

# Usage
registry = PluginRegistry()
registry.load_plugins(Path("plugins/"))
```

## Security Considerations

### 1. Configuration Security

- **Environment Variables**: Sensitive data stored in environment variables
- **No Hardcoded Secrets**: Bot tokens and API keys never hardcoded
- **File Permissions**: Configuration files have appropriate permissions
- **Validation**: All configuration inputs are validated

### 2. Worker Security

- **Sandboxing**: Workers run in controlled environments
- **Path Validation**: All paths are validated and sanitized
- **Resource Limits**: Workers have resource constraints
- **Error Information**: Sensitive information not exposed in errors

### 3. Telegram Security

- **Token Protection**: Bot tokens are treated as secrets
- **Privacy Settings**: Bot privacy mode enabled by default
- **Message Sanitization**: Sensitive data removed from messages
- **Rate Limiting**: Respect Telegram API rate limits

### 4. Network Security

- **HTTPS Only**: All network communication uses HTTPS
- **Timeout Configuration**: Appropriate timeouts for network requests
- **Certificate Validation**: SSL certificates are validated
- **Retry Logic**: Safe retry logic for network failures

## Scalability

### 1. Worker Scalability

- **Parallel Execution**: Workers can be executed in parallel
- **Resource Management**: Efficient resource usage for many workers
- **Lazy Loading**: Workers loaded only when needed
- **Memory Management**: Proper cleanup of worker instances

### 2. Configuration Scalability

- **Environment-based**: Configuration scales with environment complexity
- **Hierarchical Settings**: Support for nested configuration
- **Dynamic Updates**: Configuration can be updated at runtime
- **Validation**: Comprehensive validation prevents configuration errors

### 3. Logging Scalability

- **Async Logging**: Non-blocking log message processing
- **Buffer Management**: Efficient buffering for high-volume logging
- **Filtering**: Log level filtering reduces overhead
- **Aggregation**: Log aggregation for distributed systems

### 4. Performance Considerations

- **Caching**: Worker discovery results cached
- **Connection Pooling**: HTTP connections reused for Telegram
- **Batch Processing**: Multiple operations batched when possible
- **Memory Efficiency**: Minimal memory footprint for core components

## Future Architecture Considerations

### 1. Microservices Architecture

- **Service Separation**: Components could be separated into services
- **API Gateway**: Central API gateway for external access
- **Service Discovery**: Dynamic service discovery and registration
- **Load Balancing**: Load balancing for worker execution

### 2. Event-Driven Architecture

- **Event Bus**: Event-driven communication between components
- **Message Queues**: Asynchronous message processing
- **Event Sourcing**: Event sourcing for state management
- **CQRS**: Command Query Responsibility Segregation

### 3. Cloud-Native Features

- **Containerization**: Docker containerization for deployment
- **Kubernetes**: Kubernetes orchestration for scaling
- **Auto-scaling**: Automatic scaling based on load
- **Health Checks**: Comprehensive health check endpoints

### 4. Advanced Features

- **Machine Learning**: ML-based worker optimization
- **Workflow Engine**: Complex workflow orchestration
- **Monitoring**: Advanced monitoring and alerting
- **Analytics**: Usage analytics and reporting

---

This architecture provides a solid foundation for automation tasks while maintaining flexibility for future enhancements and scaling requirements.