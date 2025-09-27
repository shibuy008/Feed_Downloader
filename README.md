# Feed Downloader

A scalable, vendor-agnostic data downloader in Python that can flexibly fetch data from many sources (SFTP, REST APIs, WebSockets, HTTP downloads, JSON/XML feeds, etc.), with configs so it's generic rather than hard-coded per vendor.

## Features

- **Config-driven**: Each vendor's source is defined in a YAML configuration file
- **Pluggable architecture**: Base downloader class with extensions for different source types
- **Format agnostic**: Normalizes downloaded data into pandas DataFrames regardless of source/format
- **Error handling & retries**: Built-in resilience with retry logic and comprehensive error handling
- **Logging & monitoring**: Centralized logging with vendor-specific tags
- **Compression support**: Handles ZIP, GZIP, and TAR compressed files
- **Multiple data sources**: SFTP, REST APIs, WebSockets, HTTP file downloads
- **🆕 Intelligent Scheduling**: Time-based downloads with cron expressions and real-time polling
- **🆕 Timezone Support**: Full timezone awareness for global financial markets
- **🆕 Continuous Operation**: Runs continuously with automatic retry and error recovery

## Supported Data Sources

- **SFTP**: Secure file transfer protocol for file downloads
- **REST API**: HTTP REST endpoints for JSON/XML data
- **WebSocket**: Real-time data streams
- **HTTP**: Direct file downloads from URLs

## Supported Data Formats

- **CSV**: Comma-separated values with customizable delimiters
- **JSON**: JavaScript Object Notation with nested data support
- **XML**: Extensible Markup Language including RSS/Atom feeds
- **Excel**: XLS and XLSX files with multi-sheet support
- **Compressed**: ZIP, GZIP, and TAR archives

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Feed_Downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. **Configure your vendors** in `config.yaml`:
```yaml
vendors:
  - name: "my_vendor"
    type: "rest_api"
    endpoint: "https://api.example.com/data"
    headers:
      Authorization: "Bearer your_token"
    local_path: "./downloads/vendor_data.json"
    format: "json"
```

2. **Run the downloader**:
```bash
python main.py
```

3. **Check results** in the `./downloads/` directory

## Configuration

The `config.yaml` file defines all vendor sources and their connection details. Here's a comprehensive example:

```yaml
# Global settings
global:
  download_dir: "./downloads"
  timeout: 30
  max_retries: 3
  retry_delay: 5

# Vendor configurations
vendors:
  # SFTP vendor
  - name: "vendor_sftp"
    type: "sftp"
    host: "sftp.example.com"
    username: "user"
    password: "pass"
    remote_path: "/data/file.csv"
    local_path: "./downloads/sftp_data.csv"
    format: "csv"
    
  # REST API vendor
  - name: "vendor_api"
    type: "rest_api"
    endpoint: "https://api.example.com/data"
    headers:
      Authorization: "Bearer token"
    params:
      symbol: "AAPL"
    local_path: "./downloads/api_data.json"
    format: "json"
    
  # WebSocket vendor
  - name: "vendor_ws"
    type: "websocket"
    url: "wss://ws.example.com/stream"
    subscription_message: '{"subscribe": "prices"}'
    local_path: "./downloads/ws_data.json"
    format: "json"
    duration: 10
    
  # HTTP file download
  - name: "vendor_http"
    type: "http"
    url: "https://example.com/data.csv"
    local_path: "./downloads/http_data.csv"
    format: "csv"
    
  # Compressed file
  - name: "vendor_zip"
    type: "sftp"
    host: "sftp.example.com"
    username: "user"
    password: "pass"
    remote_path: "/data/archive.zip"
    local_path: "./downloads/archive.zip"
    format: "csv"
    compressed: true
    compression_type: "zip"
```

## Usage

### Basic Usage

```bash
# Run with default config.yaml (one-time execution)
python main.py

# Use custom configuration file
python main.py --config my_config.yaml

# Process specific vendor only
python main.py --vendor vendor_sftp

# Dry run (validate configuration without downloading)
python main.py --dry-run

# Set logging level
python main.py --log-level DEBUG

# Save logs to file
python main.py --log-file ./logs/downloader.log
```

### 🆕 Scheduler Mode (Continuous Operation)

```bash
# Run in continuous scheduler mode
python main.py --scheduler

# Check scheduler status
python main.py --status

# Run scheduler with custom config
python main.py --scheduler --config my_config.yaml

# Run scheduler with debug logging
python main.py --scheduler --log-level DEBUG
```

### Command Line Options

- `--config, -c`: Path to configuration file (default: config.yaml)
- `--vendor, -v`: Process specific vendor only
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `--log-file`: Log file path
- `--dry-run`: Validate configuration without downloading

## Project Structure

```
data_downloader/
│── main.py                    # Main application entry point
│── config.yaml               # Configuration file
│── downloader_factory.py     # Factory for creating downloaders
│── downloaders/              # Downloader implementations
│    ├── base.py             # Base downloader class
│    ├── sftp_downloader.py  # SFTP downloader
│    ├── rest_api_downloader.py  # REST API downloader
│    ├── websocket_downloader.py # WebSocket downloader
│    └── http_downloader.py  # HTTP file downloader
│── parsers/                  # Data parsers
│    ├── parser_factory.py   # Parser factory
│    ├── csv_parser.py       # CSV parser
│    ├── json_parser.py      # JSON parser
│    ├── xml_parser.py       # XML parser
│    └── excel_parser.py     # Excel parser
│── utils/                    # Utility modules
│    └── decompressor.py     # File decompression utility
│── downloads/                # Downloaded files directory
│── logs/                     # Log files directory
```

## 🆕 Scheduling System

The Feed Downloader now includes a powerful scheduling system that handles both time-based and real-time data feeds.

### Schedule Types

1. **Scheduled Feeds**: Download at specific times using cron expressions
2. **Real-time Feeds**: Download continuously with specified intervals
3. **On-demand Feeds**: Download only when manually triggered

### Configuration Examples

```yaml
vendors:
  # Scheduled feed - daily at 8 AM
  - name: "daily_data"
    type: "sftp"
    # ... connection details ...
    schedule:
      type: "scheduled"
      cron: "0 8 * * *"  # Daily at 8 AM
      timezone: "UTC"
      enabled: true
      max_retries: 3
      retry_delay: 300

  # Real-time feed - every 5 minutes
  - name: "realtime_prices"
    type: "rest_api"
    # ... connection details ...
    schedule:
      type: "real_time"
      interval_seconds: 300  # Every 5 minutes
      timezone: "UTC"
      enabled: true
      max_retries: 5
      retry_delay: 60

  # Market hours only - every hour during trading
  - name: "market_data"
    type: "rest_api"
    # ... connection details ...
    schedule:
      type: "scheduled"
      cron: "0 9-16 * * 1-5"  # 9 AM - 4 PM, weekdays only
      timezone: "America/New_York"
      enabled: true
      max_retries: 3
      retry_delay: 300
```

### Common Cron Expressions

```yaml
scheduling:
  common_schedules:
    market_open: "0 9 * * 1-5"        # 9 AM weekdays
    market_close: "0 16 * * 1-5"      # 4 PM weekdays
    daily_morning: "0 8 * * *"        # 8 AM daily
    daily_evening: "0 18 * * *"       # 6 PM daily
    hourly: "0 * * * *"               # Every hour
    every_15_minutes: "*/15 * * * *"  # Every 15 minutes
    every_5_minutes: "*/5 * * * *"    # Every 5 minutes
    weekly_monday: "0 9 * * 1"        # 9 AM Mondays
    monthly_first: "0 9 1 * *"        # 9 AM first day of month
    end_of_day: "0 23 * * *"          # 11 PM daily
    pre_market: "0 6 * * 1-5"         # 6 AM weekdays
    after_hours: "0 20 * * 1-5"       # 8 PM weekdays
```

### Timezone Support

The scheduler supports all standard timezones:

- `UTC` - Coordinated Universal Time
- `America/New_York` - Eastern Time (US)
- `America/Chicago` - Central Time (US)
- `America/Denver` - Mountain Time (US)
- `America/Los_Angeles` - Pacific Time (US)
- `Europe/London` - Greenwich Mean Time
- `Asia/Tokyo` - Japan Standard Time
- And many more...

### Running the Scheduler

```bash
# Start continuous scheduler
python main.py --scheduler

# Check status
python main.py --status

# View next scheduled runs
python main.py --status
```

## Advanced Features

### Custom Parsing Options

You can specify custom parsing options in the configuration:

```yaml
parsing:
  csv:
    delimiter: ";"
    encoding: "utf-8"
    parse_dates: true
  json:
    encoding: "utf-8"
    normalize_nested: true
  excel:
    engine: "openpyxl"
    na_values: ["", "N/A", "NULL"]
```

### Compression Support

The downloader automatically handles compressed files:

```yaml
vendors:
  - name: "compressed_vendor"
    type: "sftp"
    # ... connection details ...
    compressed: true
    compression_type: "zip"  # or "gzip", "tar"
```

### Error Handling and Retries

Built-in retry logic with configurable settings:

```yaml
global:
  max_retries: 3
  retry_delay: 5
  timeout: 30
```

### Logging

Comprehensive logging with different levels:

```bash
# Debug level for detailed information
python main.py --log-level DEBUG

# Save logs to file
python main.py --log-file ./logs/downloader.log
```

## Extending the Downloader

### Adding New Downloader Types

1. Create a new downloader class inheriting from `BaseDownloader`
2. Implement the `download()` method
3. Add the new type to `downloader_factory.py`

### Adding New Parser Types

1. Create a new parser function in the `parsers/` directory
2. Add the format to `parser_factory.py`
3. Update the supported formats list

## Examples

### Financial Data Sources

```yaml
vendors:
  # Stock prices from REST API
  - name: "stock_prices"
    type: "rest_api"
    endpoint: "https://api.alphavantage.co/query"
    params:
      function: "TIME_SERIES_DAILY"
      symbol: "AAPL"
      apikey: "your_api_key"
    local_path: "./downloads/stock_prices.json"
    format: "json"
    
  # Real-time crypto prices via WebSocket
  - name: "crypto_prices"
    type: "websocket"
    url: "wss://stream.binance.com:9443/ws/btcusdt@ticker"
    local_path: "./downloads/crypto_prices.json"
    format: "json"
    duration: 60
    
  # Economic data from SFTP
  - name: "economic_data"
    type: "sftp"
    host: "data.federalreserve.gov"
    username: "anonymous"
    password: ""
    remote_path: "/data/economic/indicators.csv"
    local_path: "./downloads/economic_data.csv"
    format: "csv"
```

### News and RSS Feeds

```yaml
vendors:
  # Financial news RSS feed
  - name: "financial_news"
    type: "http"
    url: "https://feeds.finance.yahoo.com/rss/2.0/headline"
    local_path: "./downloads/financial_news.xml"
    format: "xml"
    
  # Market data in Excel format
  - name: "market_report"
    type: "rest_api"
    endpoint: "https://api.marketdata.com/report"
    headers:
      Authorization: "Bearer your_token"
    local_path: "./downloads/market_report.xlsx"
    format: "excel"
```

## Troubleshooting

### Common Issues

1. **Connection timeouts**: Increase the `timeout` value in configuration
2. **Authentication failures**: Verify credentials in the configuration
3. **Parsing errors**: Check file format and encoding settings
4. **Permission errors**: Ensure write permissions for download directory

### Debug Mode

Run with debug logging to get detailed information:

```bash
python main.py --log-level DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration examples
3. Enable debug logging for detailed error information
4. Create an issue in the repository